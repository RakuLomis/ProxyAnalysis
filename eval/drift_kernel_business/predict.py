"""Frozen inference: receives only post histograms, model weights and deployment route."""
from common import *

def predict_frames(query,bundle,lr,mlps):
    require(set(query)==set(HIST+['visit_id']), 'Forbidden post query columns')
    h=tensor(query[HIST])
    results={}
    for arm in ['G0','G3','G4','G5']:
        results[(arm,-1)]=composite(h,bundle[arm])
    results[('G1',-1)]=standardized(query,lr['mu'],lr['scale'])@lr['weight'].T+lr['bias']
    for seed,m in mlps.items():
        results[('G2',seed)]=mlp_forward(standardized(query,m['mu'],m['scale'],torch.float32),m).double()
    return results

def run():
    c=start('predict')
    path=OUT/'predictions/complete.json'
    if path.exists():
        for p,h in read(path)['sha256'].items():
            require(sha(ROOT/p)==h,'Frozen prediction changed')
        print('Predictions already frozen; no overwrite',flush=True)
        return
    outputs=[]
    timing=[]
    for role in c['roles']:
        fold,p=role['fold'],role['protocol']
        query=load_package(rolefolder(fold,p)/'query-post-hist.parquet','predict')
        folder=modelfolder(fold,p)
        bundle=model_load(folder/'distributions.pt','predict')
        lr=model_load(folder/'G1.pt','predict')
        mlps={s:model_load(folder/f'G2-{s}.pt','predict') for s in SEEDS}
        torch.cuda.synchronize()
        started=time.perf_counter()
        with torch.inference_mode():
            result=predict_frames(query,bundle,lr,mlps)
        torch.cuda.synchronize()
        timing.append({'fold':fold,'protocol':p,'seconds':time.perf_counter()-started,'device':'cuda:0'})
        for (arm,seed),logit in result.items():
            prob=logit.softmax(1)
            require(bool(torch.isfinite(prob).all()) and torch.allclose(prob.sum(1),torch.ones(len(query),device=cuda(),dtype=prob.dtype),atol=1e-12),'Invalid inference probabilities')
            data=pd.DataFrame(prob.cpu().numpy(),columns=[f'p{i}' for i in range(6)])
            for i in range(6):
                data[f's{i}']=logit[:,i].cpu().numpy()
            data['prediction']=prob.argmax(1).cpu().numpy()
            data['visit_id']=query.visit_id.to_numpy()
            data['arm'],data['seed'],data['fold'],data['protocol']=arm,seed,fold,p
            outputs.append(data)
        print('post-only predictions',p,fold,flush=True)
    data=pd.concat(outputs,ignore_index=True)
    require(len(data)==3840,'Expected 480 visits times five deterministic arms plus three MLP seeds')
    out=OUT/'predictions/visits.parquet'
    saveparquet(data,out)
    write(path,{'sha256':{rel(out):sha(out)},'rows':len(data),'unique_visits':data.visit_id.nunique(),
          'test_labels_opened':False,'test_pre_opened':False,'frozen_before_scoring':True})
    finish('predict',timing=timing,rows=len(data),test_pre_read=False,test_label_read=False)

if __name__=='__main__':
    run()
