"""Bounded pilot, deterministic replay, old diagnostic checks and model promotion."""
import shutil
from common import *
from optimizer_preconditioning import fit_preconditioned

def context(r, arm, t):
    path=PREP/'slots'/r['id']/(arm+'.pt')
    return {'role_id':r['id'],'arm':arm,'t':t,'input_sha256':read(path.with_suffix('.json'))['sha256']}
def pilotpath(r, arm, t):return OUT/'pilot/models'/r['id']/f'{arm}-t{t:g}.pt'

def pilot():
    c=start('pilot');ids=v2contract()['pilot_roles'];rows=[];started=time.perf_counter()
    for rid in ids:
        r=next(x for x in c['main'] if x['id']==rid)
        require(r['inner'] is not None and r['target'] not in r['sources']+[r['calibration']], 'Illegal pilot role')
        for arm in ARMS:
            slot=artifact(PREP/'slots'/rid/(arm+'.pt'))
            for t in TS:
                p=pilotpath(r,arm,t)
                if p.with_suffix('.json').exists():artifact(p);log=read(p.with_suffix('.json'))['optimizer']
                else:
                    m,log=fit_preconditioned(slot['x'],slot['y'],slot['mass'],t,context(r,arm,t))
                    save_artifact({'mu':slot['mu'],'scale':slot['scale'],**m},p,
                                  optimizer=log,role_id=rid,arm=arm,t=t,target_U_read=False,pilot=True)
                rows.append({'role_id':rid,'arm':arm,'t':t,**{k:log[k] for k in
                              ['iterations','function_evaluations','max_gradient','seconds','objective','accepted']}})
                progress('OR08_engineering_pilot',accepted=len(rows),total=60,role=rid,arm=arm,t=t,
                         iterations=log['iterations'],max_gradient=log['max_gradient'])
    require(len(rows)==60 and all(x['accepted'] for x in rows),'Pilot incomplete')
    save(pd.DataFrame(rows),OUT/'pilot/quality.parquet')
    complete(OUT/'pilot/complete.json',candidates=60,quality_sha256=sha(OUT/'pilot/quality.parquet'),
             source_selection_labels_read=False,seconds=time.perf_counter()-started)
    finish('pilot',accepted=60,unmodified_original_gates=True)

def repeat():
    c=start('repeat'); require((OUT/'pilot/complete.json').exists(),'Pilot not complete')
    r=next(x for x in c['main'] if x['id']==v2contract()['pilot_roles'][0]);slot=artifact(PREP/'slots'/r['id']/'CT1.pt')
    ctx=context(r,'CT1',0);ctx['role_id']='deterministic-replay/'+r['id']
    m,log=fit_preconditioned(slot['x'],slot['y'],slot['mass'],0,ctx,diagnostic=True)
    previous=artifact(pilotpath(r,'CT1',0));error=max(float((m[k]-previous[k]).abs().max()) for k in ['weight','bias'])
    require(error==0,'Deterministic numerical replay changed')
    write(OUT/'pilot/deterministic-replay.json',{'passed':True,'parameter_max_error':error,
          'diagnostic_fits':1,'formal_model_written':False,'optimizer':log})
    finish('repeat',parameter_max_error=error)

def reuse_diagnostics():
    c=start('reuse_diagnostics');choices={(v['kind'],v['outer'],v['protocol']):v['t']
                       for v in read(PREP/'diagnostics/choices.json')}
    count=0;err=0.;grad=0.
    for r in c['diagnostics']:
        d=package(rolepath(r)/'train.parquet','diag-fit');raw=tensor(d[HIST]);mu,scale=scaler(raw)
        x=(raw-mu)/scale;y=tensor(truths(d),torch.long)
        mass=torch.full((len(d),),1/len(d),device=device(),dtype=torch.float64)
        for t in TS if r['inner'] is not None else [choices[(r['kind'],r['outer'],r['protocol'])]]:
            p=PREP/'models'/r['id']/f't{t:g}.pt';m=artifact(p);log=read(p.with_suffix('.json'))['optimizer']
            require(torch.equal(m['mu'],mu) and torch.equal(m['scale'],scale),'Diagnostic coordinates changed')
            w=m['weight'].clone().requires_grad_();b=m['bias'].clone().requires_grad_()
            val=objective(w,b,x,y,mass,t);gw,gb=torch.autograd.grad(val,(w,b))
            e=abs(float(val.detach())-log['objective']);g=max(float(gw.abs().max()),float(gb.abs().max()))
            require(e<1e-10 and g<=1e-5 and log['iterations']<500,'Old diagnostic model invalid')
            count+=1;err=max(err,e);grad=max(grad,g)
        if count%100==0:progress('OR10_reuse_quality',models=count,total=680)
    old=read(OUT/'manifests/reused-post-models.json')
    for v in old:
        p=ROOT/v['path'];checked(p,c['baseline_sha256'],'old_source_post_reference')
    require(count==680 and len(old)==20,'Diagnostic reuse count')
    write(OUT/'manifests/diagnostic-reuse-check.json',{'passed':True,'models':count,'old_post_models':20,
          'objective_max_error':err,'gradient_max':grad,'new_fits':0})
    finish('reuse_diagnostics',models=count,new_fits=0)

def promote():
    c=start('promote');require((OUT/'pilot/deterministic-replay.json').exists(),'Repeat not passed')
    require(read(OUT/'manifests/diagnostic-reuse-check.json')['passed'],'Reuse not accepted')
    records=[]
    for rid in v2contract()['pilot_roles']:
      r=next(x for x in c['main'] if x['id']==rid)
      for arm in ARMS:
       for t in TS:
        src=pilotpath(r,arm,t);artifact(src);dst=writable(OUT/'models'/rid/src.name)
        dst.parent.mkdir(parents=True,exist_ok=True)
        require(not dst.with_suffix('.json').exists(),'Pilot already promoted')
        shutil.copyfile(src,dst);shutil.copyfile(src.with_suffix('.json'),dst.with_suffix('.json'))
        require(sha(dst)==sha(src),'Promotion bytes changed')
        records.append({'source':rel(src),'destination':rel(dst),'sha256':sha(dst)})
    require(len(records)==60,'Pilot promotion count')
    write(OUT/'manifests/promoted-pilot-models.json',{'models':records,'formal_budget_included':True})
    finish('promote',models=60,remaining_inner_fits=14340)

if __name__=='__main__':
    import sys
    {'pilot':pilot,'repeat':repeat,'reuse':reuse_diagnostics,'promote':promote}[sys.argv[1]]()
