"""Two preregistered eight-comparison families, content-cluster bootstrap."""
from common import *

def fast_f1(y,pred,multiplicity):
    one=np.eye(36)[y*6+pred]
    cm=(multiplicity@one).reshape(-1,6,6)
    tp=np.diagonal(cm,axis1=1,axis2=2)
    den=cm.sum(1)+cm.sum(2)
    return np.divide(2*tp,den,out=np.zeros_like(tp),where=den>0).mean(1)

def run():
    c=read(OUT/'manifests/experiment-contract.json')
    data=pd.read_parquet(OUT/'scores/scored-visits.parquet')
    contents=data[['content_id','label_id']].drop_duplicates().sort_values(['label_id','content_id']).reset_index(drop=True)
    require(len(contents)==30 and contents.groupby('label_id').size().eq(5).all(),'Bootstrap content support changed')
    rng=np.random.default_rng(c['bootstrap']['seed'])
    indices=np.concatenate([rng.choice(np.arange(5*i,5*i+5),size=(10000,5),replace=True) for i in range(6)],axis=1)
    (OUT/'comparisons').mkdir(exist_ok=True)
    np.save(OUT/'comparisons/bootstrap-indices.npy',indices)
    counts=np.stack([np.bincount(a,minlength=30) for a in indices])
    lookup={v:i for i,v in enumerate(contents.content_id)}
    summary=pd.read_parquet(OUT/'scores/protocol-summary.parquet').set_index(['protocol','arm'])
    rows=[]
    for p in PROTOCOLS:
        boot={}
        for arm in ARMS:
            values=[]
            for seed,g in data[data.protocol.eq(p)&data.arm.eq(arm)].groupby('seed'):
                m=counts[:,g.content_id.map(lookup).to_numpy()]
                values.append(fast_f1(g.truth.to_numpy(),g.prediction.to_numpy(),m))
            boot[arm]=np.mean(values,axis=0)
        for comp in ['G3','G5','G0','G2','G1']:
            delta=boot['G4']-boot[comp]
            ordinary=np.quantile(delta,[.025,.975])
            family='primary' if comp in ['G3','G5'] else 'baseline' if comp in ['G0','G2'] else 'supplement'
            adjusted=np.quantile(delta,[.003125,.996875]) if family!='supplement' else ordinary
            rows.append({'protocol':p,'family':family,'comparison':'G4-'+comp,
                 'point':float(summary.loc[(p,'G4'),'F1']-summary.loc[(p,comp),'F1']),
                 'lo95':float(ordinary[0]),'hi95':float(ordinary[1]),'family_lo':float(adjusted[0]),
                 'family_hi':float(adjusted[1]),'family_size':8 if family!='supplement' else 0,
                 'family_positive':bool(adjusted[0]>0),'bootstrap_samples':10000})
        print('content bootstrap',p,flush=True)
    saveparquet(pd.DataFrame(rows),OUT/'comparisons/F1-contrasts.parquet')
    saveparquet(contents,OUT/'comparisons/bootstrap-content-order.parquet')
    write(OUT/'comparisons/bootstrap-manifest.json',{'index_sha256':sha(OUT/'comparisons/bootstrap-indices.npy'),
          'order_sha256':sha(OUT/'comparisons/bootstrap-content-order.parquet'),'family_sizes':[8,8],
          'model_conditional':True,'MLP_statistic':'mean seed-wise F1, not probability ensemble or replicated visits',
          'retraining_bootstrap':False})

if __name__=='__main__':
    run()
