"""Fixed source-only content selection; no target-U/H observations or labels."""
from common import *
from mappings import coral
from objectives import fit
from representation import predict

_weights=None
def weights():
    global _weights
    if _weights is None:_weights=module('cj_original_loss_weights',ROOT/'eval/calibrated_deployment_transfer/representation.py')
    return _weights

def baseline(r,rep,inner=None):
    rootdir=rolepath(r)/rep; cols=INPUTS[rep]
    source=package(rootdir/'source-post.parquet','train'); cp=package(rootdir/'C-post.parquet','train')
    if inner is not None:
        val=set(r['inner_validation_contents'][inner])
        source=source[~source.content_id.isin(val)].reset_index(drop=True)
        cp=cp[~cp.content_id.isin(val)].reset_index(drop=True)
        require(len(source)==216 and len(cp)==48,'Inner fitting membership')
    mu96,scale96=scaler(torch.cat([tensor(source[HIST]),tensor(cp[HIST])]))
    if inner is None:
        old=artifact(ROOT/r['reuse_views'])
        require(float((mu96-old['mu']).abs().max())<=1e-14 and float((scale96-old['scale']).abs().max())<=1e-14,
                'Old first96 coordinate replay failed')
        mu96,scale96=old['mu'],old['scale']
    if rep=='M':mu,scale=mu96,scale96
    else:
        mn,sn=scaler(torch.cat([tensor(source[JOINT]),tensor(cp[JOINT])]))
        mu,scale=torch.cat([mu96,mn]),torch.cat([scale96,sn])
    x=(tensor(source[cols])-mu)/scale; cx=(tensor(cp[cols])-mu)/scale
    aux,parameters=coral(x,source,cx,cp,r['missing'])
    if inner is None:
        old=artifact(ROOT/r['reuse_views']); error=float((aux[:,:96]-old['S_x']).abs().max())
        require(error<1e-12,'Old CORAL first96 replay'); aux[:,:96]=old['S_x']
    mass,y=weights().loss_weights(source,cp,r['missing'])
    return {'x':torch.cat([x,aux,cx]),'y':y,'mass':mass,'mu':mu,'scale':scale,
            'main_x':x,'C_x':cx,'S_x':aux,'source':source,'cp':cp,'parameters':parameters}

def fit_role(r):
    summaries=[]
    for rep in ['M','I','J']:
        scores={t:[] for t in TS}
        for inner in range(2):
            b=baseline(r,rep,inner); q=package(rolepath(r)/rep/f'inner-query-{inner}.parquet','select')
            for t in TS:
                p=OUT/'models/selection'/r['id']/f'{rep}-i{inner}-t{t:g}.pt'
                if p.with_suffix('.json').exists():model=artifact(p)
                else:
                    m,log=fit(b['x'],b['y'],b['mass'],t,{'role_id':r['id'],'arm':f'{rep}-inner{inner}'})
                    model={'mu':b['mu'],'scale':b['scale'],**m}; put(model,p,optimizer=log,role_id=r['id'],representation=rep,inner=inner,t=t)
                prediction=predict(model,q[['visit_id',*INPUTS[rep]]],rep)
                pq=OUT/'selection/predictions'/r['id']/f'{rep}-i{inner}-t{t:g}.parquet'; save(prediction,pq)
                # Source validation labels only, never target heldout labels.
                y=truths(q); prob=prediction[[f'p{i}' for i in range(6)]].to_numpy()
                ce=-np.log(prob[np.arange(len(q)),y]); score=float(ce.mean())
                require(len(q)==72 and q.groupby(['protocol','label_id']).size().eq(4).all(),'Equal source scoring support')
                scores[t].append(score)
        means={t:float(np.mean(v)) for t,v in scores.items()}; best=min(means.values())
        chosen=min(t for t,value in means.items() if value<=best+1e-12)
        summaries.append({'representation':rep,'t':chosen,'source_CE':means[chosen],
                          'candidates':[{ 't':t,'CE_nats':means[t]} for t in TS]})
    write(OUT/'selection'/r['id']/'choices.json',{'role_id':r['id'],'choices':summaries,
         'H_label_reads':0,'target_U_reads':0,'inner_models':24})
    return summaries
