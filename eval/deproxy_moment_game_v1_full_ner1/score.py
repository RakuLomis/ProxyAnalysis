"""All 13 pipelines, complete six-class metrics and five shared-content contrasts."""
from common import *
from formal import historical,truth,metrics
PIPELINES=['B0']+[a+'-'+p for a in METHODS for p in ['PURE','FUSE']]
PRIMARY='F-P-FUSE';REFERENCES=['B0','E-post-FUSE','N-P-FUSE','F-G-FUSE','R-P-FUSE']

def bootstrap(data):
    contents=sorted(data.content_id.unique());require(len(contents)==30,'Thirty global contents')
    lookup={u:i for i,u in enumerate(contents)};groups=list(MASKS)
    cm=np.zeros((13,4,3,3,30,6,6),np.int32)
    for (a,p,g,seed,u),d in data.groupby(['pipeline','target','group','seed','content_id']):
        y=truth(d);z=d.prediction.to_numpy(int)
        cm[PIPELINES.index(a),PROTOCOLS.index(p),groups.index(g),SEEDS.index(seed),lookup[u]]=np.bincount(y*6+z,minlength=36).reshape(6,6)
    la=data[['content_id','label_id']].drop_duplicates();require(len(la)==30,'Consistent content labels')
    labels=truth(la.set_index('content_id').loc[contents].reset_index());rng=np.random.default_rng(20261016)
    w=np.zeros((10000,30),np.int32)
    for k in range(6):
        ids=np.flatnonzero(labels==k);require(len(ids)==5,'Five contents per business')
        picks=rng.choice(ids,size=(10000,5),replace=True)
        for i in range(10000):w[i]+=np.bincount(picks[i],minlength=30)
    values=np.empty((10000,13))
    for start in range(0,10000,100):
        c=np.einsum('bc,apgscyz->bapgsyz',w[start:start+100],cm,optimize=True)
        den=c.sum(-1)+c.sum(-2);f=np.divide(2*np.diagonal(c,axis1=-2,axis2=-1),den,out=np.zeros_like(den,dtype=float),where=den>0)
        pergroup=[np.take(f[:,:,:,j,:,:],MASKS[g],axis=-1).mean(-1) for j,g in enumerate(groups)]
        values[start:start+100]=np.stack(pergroup,-1).mean((2,3,4))
    np.savez_compressed(writable(OUT/'comparisons/bootstrap.npz'),contents=np.array(contents),pipelines=np.array(PIPELINES),weights=w,F1_U=values)
    return values

def run():
    configure('inference');barrier('P5-predictions-complete.json');hashes=code_seal('P5-score');labels=[]
    for r in contract()['roles']:
        d=historical(r,'labels');d['role_id']=r['id'];labels.append(d.drop(columns=['protocol'],errors='ignore'))
    pred=pd.read_parquet(OUT/'predictions/post-only.parquet')
    data=pred.merge(pd.concat(labels),on=['role_id','visit_id'],validate='many_to_one');require(len(data)==56160,'Full label join')
    scenes=[];classes=[];lc=[f'l{k}' for k in range(6)]
    for (a,p,g,seed),part in data.groupby(['pipeline','target','group','seed']):
        require(len(part)==120 and part.content_id.nunique()==30,'Complete pooled OOF content coverage')
        m,cm,f=metrics(truth(part),part[lc].to_numpy(),MASKS[g]);scenes.append(dict(pipeline=a,target=p,group=g,seed=seed,**m))
        for k in range(6):classes.append(dict(pipeline=a,target=p,group=g,seed=seed,label=LABELS[k],F1=float(f[k]),confusion_row=cm[k].tolist()))
    scenes=pd.DataFrame(scenes);cols=[k for k in scenes if k not in ['pipeline','target','group','seed']]
    pooled=scenes.groupby('pipeline')[cols].mean().reset_index();targets=scenes.groupby(['pipeline','target'])[cols].mean().reset_index()
    pooled=pooled.merge(targets.groupby('pipeline').F1_U.min().rename('worst_deployment_F1_U'),on='pipeline')
    for name,d in [('labeled-predictions',data),('scenarios',scenes),('targets',targets),('pooled',pooled),('classes',pd.DataFrame(classes))]:save(OUT/'scores'/(name+'.parquet'),d)
    values=bootstrap(data);point=pooled.set_index('pipeline');comparisons=[]
    for ref in REFERENCES:
        v=values[:,PIPELINES.index(PRIMARY)]-values[:,PIPELINES.index(ref)]
        comparisons.append(dict(candidate=PRIMARY,reference=ref,delta_F1_U=float(point.loc[PRIMARY,'F1_U']-point.loc[ref,'F1_U']),
            CI95=np.quantile(v,[.025,.975]).tolist(),CI99=np.quantile(v,[.005,.995]).tolist(),positive_family_increment=bool(np.quantile(v,.005)>0)))
    immutable(OUT/'comparisons/primary.json',dict(family=5,bootstrap=10000,seed=20261016,conditioned_on_fixed_fitted_models=True,comparisons=comparisons))
    guards=[]
    for proto,d in targets.groupby('target'):
        p=d.set_index('pipeline');delta=float(p.loc[PRIMARY,'F1_C']-p.loc['B0','F1_C']);guards.append(dict(deployment=proto,delta_F1_C=delta,passed=delta>=-.02))
    dc=float(point.loc[PRIMARY,'F1_C']-point.loc['B0','F1_C']);ce=float(point.loc[PRIMARY,'CE_U']-point.loc['B0','CE_U'])
    immutable(OUT/'comparisons/practical-screen.json',dict(overall_delta_F1_C=dc,overall_passed=dc>=-.01,deployments=guards,
        passed=dc>=-.01 and all(x['passed'] for x in guards),delta_CE_U=ce,CE_magnitude_flag=ce<=-.002,H_conditioned_fallback=False))
    flips=[]
    for ref in REFERENCES:
        main=data[data.pipeline==PRIMARY];other=data[data.pipeline==ref][['role_id','visit_id','seed','prediction']].rename(columns={'prediction':'reference_prediction'})
        z=main.merge(other,on=['role_id','visit_id','seed'],validate='one_to_one');y=truth(z)
        z['repaired']=(z.prediction.to_numpy()==y)&(z.reference_prediction.to_numpy()!=y)
        z['introduced']=(z.prediction.to_numpy()!=y)&(z.reference_prediction.to_numpy()==y)
        z['changed']=z.prediction.ne(z.reference_prediction);z['reference']=ref;z['scope']=['U' if k in MASKS[g] else 'C' for k,g in zip(y,z.group)];flips.append(z)
    save(OUT/'scores/error-flips.parquet',pd.concat(flips,ignore_index=True))
    flush_reads('P5-score');codecheck(hashes);seal(OUT/'manifests/P5-scores-complete.json',list((OUT/'scores').glob('*.parquet'))+list((OUT/'comparisons').glob('*')),complete_H_evaluation=True)
    progress('P5_scored',comparisons=comparisons)
