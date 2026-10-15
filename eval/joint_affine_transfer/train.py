"""New auxiliary slots, fixed pilot and exhaustive nested CUDA fits."""
from common import *
import affine

def build(r,arm,eta):
    sp=slotpath(r,arm,eta)
    if sp.with_suffix('.json').exists():get(mappath(r,arm,eta));return get(sp)
    root=rolepath(r); source=package(root/'source-post.parquet','source-fit')
    cp=package(root/'C-post.parquet','source-fit'); pre=package(root/'source-pre.parquet','source-fit')
    require('visit_id' not in pre and 'session_id' not in pre,'Source auxiliary exact identity leak')
    mu,scale=scaler(torch.cat([tensor(source[HIST]),tensor(cp[HIST])]))
    # Independently compare against old frozen slot coordinates and row budget.
    oldpath=PREP/'slots'/r['id']/'CT1.pt'
    info=read(oldpath.with_suffix('.json')); require(sha(oldpath)==info['sha256'],'Old coordinate artifact changed')
    prior=torch.load(oldpath,map_location=device(),weights_only=True)
    require(torch.equal(prior['mu'],mu) and torch.equal(prior['scale'],scale),'Scaler differs from v4')
    if arm=='JA2':
        gp=package(ROOT/r['C_group_pre'],'group-map'); gb=package(ROOT/r['C_group_post'],'group-map')
        gp=gp.copy();gb=gb.copy()
        gp[HIST]=((tensor(gp[HIST])-mu)/scale).cpu().numpy()
        gb[HIST]=((tensor(gb[HIST])-mu)/scale).cpu().numpy()
        x=tensor(gp[HIST]);y,constant=affine.group_targets(gp,gb);mass=tensor(gp.fit_mass)
        fitpaths=[r['C_group_pre'],r['C_group_post']]
    else:
        d=package(ROOT/r['C_paired'],'paired-map')
        x=(tensor(d[['pre_'+h for h in HIST]])-mu)/scale
        y=(tensor(d[['post_'+h for h in HIST]])-mu)/scale
        mass=tensor(d.fit_mass);constant=0.;fitpaths=[r['C_paired']]
    model,log=affine.fit(x,y,mass,eta,arm,constant)
    model.update(mu=mu,scale=scale,fit_min=x.min(0).values,fit_max=x.max(0).values)
    put(model,mappath(r,arm,eta),mapping=log,role_id=r['id'],arm=arm,eta=eta,
        fit_packages=fitpaths,exact_visit_identity_used=arm!='JA2',target_U_read=False)
    raw=tensor(pre[HIST]); px=(raw-mu)/scale; aux=affine.apply(model,px)
    # Frozen weight function only; it cannot read files or identities.
    weights=module('ja_ct_weight_definition',ROOT/'eval/calibrated_deployment_transfer/representation.py')
    mass0,_=weights.loss_weights(source,cp,r['missing']); pmass,_=weights.loss_weights(pre,cp,r['missing'])
    weight=torch.cat([mass0[:len(source)],pmass[len(pre):2*len(pre)],mass0[2*len(source):]])
    labels=tensor(np.concatenate([truths(source),truths(pre),truths(cp)]),torch.long)
    xx=torch.cat([(tensor(source[HIST])-mu)/scale,aux,(tensor(cp[HIST])-mu)/scale])
    require(len(xx)==(640 if r['inner'] is None else 336),'Slot budget')
    require(torch.equal(labels,prior['y']) and torch.equal(weight,prior['mass']),'Frozen slot masses/labels differ')
    require(float((weighted(labels,weight,6)-1/6).abs().max())<1e-12,'Class mass')
    rawaux=aux*scale+mu
    shape={'negative_fraction':float((rawaux<0).to(torch.float64).mean()),
           'maximum_negative':float(torch.clamp(-rawaux,min=0).max()),
           'max_block_sum_error':max(float((rawaux[:,block(j)].sum(1)-1).abs().max()) for j in range(10)),
           'input_outside_C_coordinate_fraction':float(((px<model['fit_min'])|(px>model['fit_max'])).to(torch.float64).mean())}
    slot={'x':xx,'y':labels,'mass':weight,'mu':mu,'scale':scale}
    put(slot,sp,role_id=r['id'],arm=arm,eta=eta,rows=len(xx),real_scaler_rows=len(source)+len(cp),
        source_main_aux_C_mass=[1/3,1/3,1/3],target_U_read=False,shape=shape,
        mapping_sha256=sha(mappath(r,arm,eta)))
    return slot

def fit_one(r,arm,eta,t,solver):
    path=modelpath(r,arm,eta,t)
    if path.with_suffix('.json').exists():get(path);return read(path.with_suffix('.json'))['optimizer']
    slot=build(r,arm,eta)
    context={'role_id':r['id'],'arm':tag(arm,eta),'eta':eta,'t':t,'input_sha256':sha(slotpath(r,arm,eta))}
    model,log=solver.fit_preconditioned(slot['x'],slot['y'],slot['mass'],t,context)
    put({'mu':slot['mu'],'scale':slot['scale'],**model},path,optimizer=log,role_id=r['id'],
        arm=arm,eta=eta,t=t,target_U_read=False,pilot=r['id'] in contract()['pilot_roles'])
    return log

def pilot():
    c=start('pilot');solver=lr_solver();registry={r['id']:r for r in c['roles']};logs=[]
    for rid in c['pilot_roles']:
        r=registry[rid]
        for arm in ARMS:
            for eta in ETAS:
                for t in TS:
                    log=fit_one(r,arm,eta,t,solver)
                    logs.append({'role_id':rid,'arm':arm,'eta':eta,'t':t,
                                 **{k:log[k] for k in ['seconds','iterations','function_evaluations','max_gradient','accepted']}})
                    progress('JA_numeric_pilot',accepted=len(logs),total=720,role=rid,arm=arm,eta=eta,t=t)
    require(len(logs)==720 and all(v['accepted'] for v in logs),'Pilot incomplete')
    save(pd.DataFrame(logs),OUT/'pilot/quality.parquet')
    complete(OUT/'pilot/complete.json',candidates=720,mappings=180,quality_sha256=sha(OUT/'pilot/quality.parquet'),
             selection_labels_read=False,formal_budget_included=True)
    finish('pilot',accepted=720)

def repeat():
    c=start('repeat');require((OUT/'pilot/complete.json').exists(),'Pilot required')
    r=next(r for r in c['roles'] if r['id']==c['replay_role']);slot=build(r,'JA1',1.)
    ref=get(modelpath(r,'JA1',1.,0.));logs=[];solver=lr_solver()
    for index in range(2):
        context={'role_id':f'deterministic-replay/{index}/'+r['id'],'arm':'JA1-eta1','eta':1.,'t':0.,
                 'input_sha256':sha(slotpath(r,'JA1',1.))}
        m,log=solver.fit_preconditioned(slot['x'],slot['y'],slot['mass'],0.,context,diagnostic=True)
        err=max(float((m[k]-ref[k]).abs().max()) for k in ['weight','bias'])
        require(err==0.,'Deterministic replay changed')
        logs.append({'parameter_max_error':err,'optimizer':log})
    write(OUT/'pilot/deterministic-replay.json',{'passed':True,'diagnostic_fits':2,'rows':logs})
    q=pd.read_parquet(OUT/'pilot/quality.parquet'); timing=[]
    for arm,d in q.groupby('arm'):
        timing.append({'arm':arm,'models':len(d),'mean_seconds':float(d.seconds.mean()),
                      'p50_seconds':float(d.seconds.quantile(.5)),'p90_seconds':float(d.seconds.quantile(.9)),
                      'p95_seconds':float(d.seconds.quantile(.95))})
    estimate=sum(a['mean_seconds'] for a in timing)*(34560-720+180)/3
    write(OUT/'manifests/runtime-estimate.json',{'arms':timing,'remaining_models':34020,
        'remaining_fit_seconds_estimate':estimate,'IO_and_verification_not_included':True,
        'representative_pilot_not_guaranteed':True,'estimate_not_completion_promise':True})
    finish('repeat',diagnostic_fits=2,remaining_estimated_hours=estimate/3600)

def fit_roles(inner):
    c=start('inner_fit' if inner else 'outer_fit');solver=lr_solver()
    require(read(OUT/'manifests/pilot-promotion.json')['passed'],'Formal promotion gate')
    selected={} if inner else choices();total=34560 if inner else 180;count=0
    for r in c['roles']:
        if (r['inner'] is not None)!=inner:continue
        for arm in ARMS:
            params=[(e,t) for e in ETAS for t in TS] if inner else [(chosen(r,arm,selected)['eta'],chosen(r,arm,selected)['t'])]
            for eta,t in params:
                fit_one(r,arm,eta,t,solver);count+=1
                if count%10==0:progress('JA_inner_fit' if inner else 'JA_outer_fit',models=count,total=total,role=r['id'],arm=arm,eta=eta,t=t)
    require(count==total,'Fit count')
    finish('inner_fit' if inner else 'outer_fit',models=count)

def promote():
    c=start('promote');require(read(OUT/'pilot/deterministic-replay.json')['passed'],'Repeat gate')
    quality=pd.read_parquet(OUT/'pilot/quality.parquet')
    require(len(quality)==720 and quality.accepted.all(),'Pilot quality gate')
    write(OUT/'manifests/pilot-promotion.json',{'passed':True,'contract_sha256':sha(OUT/'manifests/experiment-contract.json'),
        'formal_model_count_included':720,'additional_copied_models':0,'selection_labels_read':False,
        'remaining_inner_models':33840,'remaining_outer_models':180})
    finish('promote',models=720,mappings=180)

if __name__=='__main__':
    {'pilot':pilot,'repeat':repeat,'promote':promote,'inner-fit':lambda:fit_roles(True),'outer-fit':lambda:fit_roles(False)}[sys.argv[1]]()
