"""Fit only post/Y plus frozen weights; export final 582-parameter models."""
import sys
from common import *

def main(inner):
    c=start('risk-fit'); logs=[]; activities=[]; aliases=[]; fitted=0
    choices={}
    if not inner:
        require(read(OUT/'selection/complete.json')['choices_sha256']==sha(OUT/'selection/choices.json'),'Selection frozen')
        choices={(x['outer'],x['protocol'],x['arm']):x['setting'] for x in read(OUT/'selection/choices.json')}
    part='inner' if inner else 'outer'; seal=read(OUT/f'weights/{part}-seal.json')
    for p,hsh in seal['role_seals'].items(): require(sha(ROOT/p)==hsh,'Weight seal changed')
    for r in c['roles']:
        if (r['inner'] is not None)!=inner: continue
        h=package(r,'train-post','risk-fit'); base=baseline(r); x=(tensor(h[HIST])-base['mu'])/base['scale']; y=tensor(truths(h),torch.long)
        raw=tensor(h[HIST]); scale=raw.std(0,unbiased=False); scale=torch.where(scale>0,scale,torch.ones_like(scale))
        require(float((raw.mean(0)-base['mu']).abs().max())<1e-12 and float((scale-base['scale']).abs().max())<1e-12,'Unweighted source coordinates')
        dst=folder('models',r); dst.mkdir(parents=True,exist_ok=True); local=[]
        if not inner:
            torch.save(base,dst/'RW0.pt'); torch.save(baseline(r,choices[(r['outer'],r['protocol'],'RW1')]),dst/'RW1.pt')
        for arm in ARMS[2:]:
            settings=RATIOS if inner else [choices[(r['outer'],r['protocol'],arm)]]
            for ratio in settings:
                wp=artifact(folder('weights',r)/f'{arm}-r{ratio:g}.pt','frozen-training-weights')
                require(wp['visit_id']==h.visit_id.tolist(),'Frozen weight order'); w=wp['w']; g=wp['gamma']
                val,parts=objective(base['weight'],base['bias'],x,y,w,g,base)
                activity={**{k:r[k] for k in ['outer','inner','protocol']},'arm':arm,'setting':ratio,
                  **{k:float(v) for k,v in parts.items()},**gradients(base['weight'],base['bias'],x,y,w,g,base)}
                activities.append(activity)
                alias=torch.equal(w,torch.ones_like(w))
                if alias:
                    model=base; aliases.append({**{k:r[k] for k in ['outer','inner','protocol']},'arm':arm,'setting':ratio,'reason':'uniform exact baseline'})
                else:
                    try: model,log=optimize(x,y,base,w,g)
                    except Exception as e:
                        write(OUT/'engineering-stop.json',{'role':r,'arm':arm,'setting':ratio,'error':str(e),
                          'status':'awaiting_user_revision','old_artifacts_preserved':True}); raise
                    log.update({**{k:r[k] for k in ['outer','inner','protocol']},'arm':arm,'setting':ratio}); logs.append(log); local.append(log); fitted+=1
                path=dst/(f'{arm}-r{ratio:g}.pt' if inner else arm+'.pt'); torch.save(model,path)
                # Actual model loss mixture replay, independent of optimizer logs.
                _,p=objective(model['weight'],model['bias'],x,y,w,g,base)
                expected=p['CE'] if wp['hard'] is None else (p[f"R{1-wp['hard']}"]+ratio*p[f"R{wp['hard']}"])/(1+ratio)
                require(abs(float(p['weighted_CE']-expected))<1e-12,'Actual weighted group-risk identity')
        complete(dst,optimizer=local,train_contents=r['train_contents'],merged_parameter_count=582,final_export=not inner)
        print('CUDA RW fitted',rolekey(r),'new fits',len(local),flush=True)
    save(pd.DataFrame(logs,columns=OPT_COLUMNS),OUT/f'manifests/{part}-optimizer.parquet')
    save(pd.DataFrame(activities),OUT/f'diagnostics/{part}-base-activity.parquet')
    save(pd.DataFrame(aliases,columns=['outer','inner','protocol','arm','setting','reason']),OUT/f'manifests/{part}-aliases.parquet')
    finish('RW11-RW13' if inner else 'RW19',new_fits=fitted,aliases=len(aliases),all_cuda_float64=True)
if __name__=='__main__': main(sys.argv[1]=='inner')
