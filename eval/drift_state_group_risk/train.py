"""Same-capacity risk fitting with saved baseline protection; no test reads."""
import sys
from common import *

def activity(m,x,y,gamma,reference=None):
    reference=m if reference is None else reference
    w=m['weight'].clone().requires_grad_(); b=m['bias'].clone().requires_grad_()
    value,parts=objective(w,b,x,y,gamma,reference['weight'],reference['bias'],.5)
    gradients={}
    for name,target in [('CE',parts['CE']),('L2',parts['L2']),('drift',parts['drift_gap']),('protection',ETA*parts['stay'])]:
        if name=='L2':
            gw=torch.autograd.grad(target,w,retain_graph=True)[0]
            gb=torch.zeros_like(b)
            gradients['L2_bias_gradient_norm']=0.
        else:
            gw,gb=torch.autograd.grad(target,[w,b],retain_graph=True)
        gradients[name+'_gradient_norm']=float(torch.sqrt(gw.square().sum()+gb.square().sum()))
    return {name:float(z.detach()) for name,z in parts.items()},gradients

def main(inner):
    c=start('risk-fit'); logs=[]; baseline_activity=[]
    choices=None
    if not inner:
        require((OUT/'selection/complete.json').exists(),'Selection first')
        choices={(x['outer'],x['protocol'],x['arm']):x['alpha'] for x in read(OUT/'selection/choices.json')}
        require(read(OUT/'selection/complete.json')['choices_sha256']==sha(OUT/'selection/choices.json'),'Selection changed')
    for r in c['roles']:
        if (r['inner'] is not None)!=inner: continue
        h=package(mainfolder('packages',r)/'train-post.parquet','risk-fit'); base=oldartifact('models',r,'zero')
        _,mu,scale=standardize(h); require(float((mu-base['mu']).abs().max())<1e-12 and float((scale-base['scale']).abs().max())<1e-12,'Base coordinates')
        x=(tensor(h[HIST])-base['mu'])/base['scale']; y=tensor(truths(h),torch.long)
        dst=mainfolder('models',r); dst.mkdir(parents=True,exist_ok=True); local=[]
        torch.save(base,dst/'zero.pt')
        for arm in ARMS[2:]:
            g=artifact(mainfolder('states',r)/(arm+'.pt'),'frozen-training-states')
            require(g['visit_id']==h.visit_id.tolist(),'State order'); gamma=g['gamma']
            a0,grads=activity(base,x,y,gamma); baseline_activity.append({'outer':r['outer'],'inner':r['inner'],'protocol':r['protocol'],'arm':arm,**a0,**grads})
            candidates=ALPHAS[1:] if inner else [choices[(r['outer'],r['protocol'],arm)]]
            for alpha in candidates:
                if alpha==0: continue
                if torch.equal(gamma,torch.full_like(gamma,.5)):
                    state={'weight':base['weight'],'bias':base['bias']}; log={'alpha':alpha,'structural_zero_alias':True,'device':'cuda:0','dtype':'float64','iterations':0,'max_gradient':0.,'seconds':0.}
                else:
                    state,log=optimize(x,y,base,gamma,alpha)
                model={'mu':base['mu'],'scale':base['scale'],**state}
                _,parts=objective(model['weight'],model['bias'],x,y,gamma,base['weight'],base['bias'],alpha)
                log.update({name:float(v.detach()) for name,v in parts.items()}); log.update({'outer':r['outer'],'inner':r['inner'],'protocol':r['protocol'],'arm':arm})
                _,final_gradients=activity(model,x,y,gamma,base); log.update(final_gradients)
                torch.save(model,dst/f'{arm}-a{alpha:g}.pt'); local.append(log); logs.append(log)
            require(torch.equal(base['weight'],oldartifact('models',r,'zero')['weight']),'Frozen base mutated')
        complete(dst,optimizer=local,train_contents=r['train_contents'],zero_alias=True)
        print('CUDA risk fitted',rolekey(r),'positive candidates',len(local),flush=True)
    part='inner' if inner else 'outer'; save(pd.DataFrame(logs),OUT/f'manifests/{part}-optimizer.parquet')
    save(pd.DataFrame(baseline_activity),OUT/f'diagnostics/{part}-base-activity.parquet')
    finish('D14-D15' if inner else 'D19',positive_fits=len(logs),all_cuda_float64=True)

if __name__=='__main__': main(sys.argv[1]=='inner')
