"""Independent objective gradients, role scopes, row counts and baseline hashes."""
from common import *
import affine

def run():
    c=start('verify');sealed_predictions();selected=choices();models=0;maps=0;maxg=0.;maxe=0.;maxmap=0.
    for index,r in enumerate(c['roles']):
        for arm in ARMS:
            grid=ETAS if r['inner'] is not None else [chosen(r,arm,selected)['eta']]
            for eta in grid:
                mapper=get(mappath(r,arm,eta));mapinfo=read(mappath(r,arm,eta).with_suffix('.json'))
                require(mapinfo['mapping']['accepted'],'Mapping gate')
                mu=mapper['mu'];scale=mapper['scale']
                if arm=='JA2':
                    gp=package(ROOT/r['C_group_pre'],'group-map').copy();gb=package(ROOT/r['C_group_post'],'group-map').copy()
                    gp[HIST]=((tensor(gp[HIST])-mu)/scale).cpu().numpy();gb[HIST]=((tensor(gb[HIST])-mu)/scale).cpu().numpy()
                    x=tensor(gp[HIST]);y,constant=affine.group_targets(gp,gb);mass=tensor(gp.fit_mass)
                    require(not mapinfo['exact_visit_identity_used'],'Group identity read')
                else:
                    d=package(ROOT/r['C_paired'],'paired-map')
                    x=(tensor(d[['pre_'+h for h in HIST]])-mu)/scale;y=(tensor(d[['post_'+h for h in HIST]])-mu)/scale
                    mass=tensor(d.fit_mass);constant=0.
                mm=mapper['matrix'].clone().requires_grad_();bb=mapper['bias'].clone().requires_grad_()
                loss=((x@mm.T+bb-y).square()*mass[:,None]).sum()/96+constant/96
                loss+=float(mapper['alpha'])*(mm-torch.eye(96,device=device(),dtype=torch.float64)).square().sum()/96
                gm,gb=torch.autograd.grad(loss,(mm,bb));mask=torch.ones_like(mm,dtype=torch.bool)
                if arm=='JA0':
                    mask.zero_()
                    for j in range(10):mask[block(j),block(j)]=True
                    require((mm.detach()[~mask]==0).all(),'Forbidden off-block coefficients')
                mg=max(float(gm[mask].abs().max()),float(gb.abs().max()))
                require(mg<=1e-8 and abs(float(loss.detach())-mapinfo['mapping']['objective'])<1e-10,'Independent mapping gate')
                maxmap=max(maxmap,mg);maps+=1
                slot=get(slotpath(r,arm,eta));require(len(slot['x'])==(336 if r['inner'] is not None else 640),'Slot rows')
                ts=TS if r['inner'] is not None else [chosen(r,arm,selected)['t']]
                for t in ts:
                    path=modelpath(r,arm,eta,t);m=get(path);log=read(path.with_suffix('.json'))['optimizer']
                    require(torch.equal(m['mu'],slot['mu']) and torch.equal(m['scale'],slot['scale']),'Classifier coordinate')
                    w=m['weight'].clone().requires_grad_();b=m['bias'].clone().requires_grad_()
                    logits=slot['x']@w.T+b
                    objective=(slot['mass']*(torch.logsumexp(logits,1)-logits.gather(1,slot['y'][:,None]).squeeze(1))).sum()
                    objective+=.0005*(1+t)*w.square().sum()
                    gw,gb=torch.autograd.grad(objective,(w,b));g=max(float(gw.abs().max()),float(gb.abs().max()))
                    e=abs(float(objective.detach())-log['objective'])
                    require(g<=1e-5 and e<1e-10 and log['iterations']<2000,'Independent LR gate')
                    require(log['settings']['max_iter']==2000 and log['settings']['max_eval']==10000,'Uniform budgets')
                    models+=1;maxg=max(maxg,g);maxe=max(maxe,e)
        if index%10==0:progress('JA_independent_verify',roles=index,models=models,mappings=maps)
    require(models==34740 and maps==8820,'Final numerical counts')
    for p,h in c['baseline_sha256'].items():require(sha(ROOT/p)==h,'Historical baseline changed: '+p)
    for p,info in c['packages'].items():require(sha(ROOT/p)==info['sha256'],'Package changed: '+p)
    score=pd.read_parquet(OUT/'scores/labeled-predictions.parquet');pooled=pd.read_parquet(OUT/'scores/pooled.parquet').set_index('arm')
    check=[]
    for arm,parts in score.groupby('arm'):
        results=[]
        for (target,group),d in parts.groupby(['target','group']):
            results.append(metrics(truths(d),d[[f'p{i}' for i in range(6)]].to_numpy(),MASKS[group])[0]['F1_uncovered'])
        check.append(abs(float(np.mean(results))-float(pooled.loc[arm,'F1_uncovered'])))
    require(max(check)<1e-12,'Metric replay')
    audit=read(OUT/'observability/audit.json')
    require(audit['unique_capture_files_read']<=16 and audit['scan_bytes']<=8*1024**3,'Parse budget')
    require(len(read(OUT/'selection/choices.json'))==180 and len(score)==14400,'Selected/prediction counts')
    write(OUT/'verification.json',{'passed':True,'new_main_classifiers':models,'mapping_tasks':maps,
        'original_classifier_gradient_max':maxg,'classifier_objective_replay_max_error':maxe,
        'mapping_gradient_max':maxmap,'metric_replay_max_error':max(check),'old_baseline_hashes_unchanged':True,
        'target_U_numeric_read':False,'all_training_and_inference_CUDA_float64':True,
        'universal_TCP_epoch_proof':False,'physical_only_external_input_verified':False})
    finish('verify',models=models,mappings=maps,passed=True)

if __name__=='__main__':run()
