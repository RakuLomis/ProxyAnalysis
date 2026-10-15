"""Six-class decisions and stable CE, content-shared seven-comparison family."""
from common import *
PC=[f'p{i}' for i in range(6)]
LC=[f'l{i}' for i in range(6)]
COLS=['F1_all','F1_U','F1_C','accuracy','CE','CE_U','CE_C','Brier','Brier_U','Brier_C']

def metrics(d,g,weights=None):
    y=truths(d);z=d.prediction.to_numpy(int);w=np.ones(len(d)) if weights is None else weights
    cm=np.bincount(y*6+z,weights=w,minlength=36).reshape(6,6);den=cm.sum(0)+cm.sum(1)
    f=np.divide(2*cm.diagonal(),den,out=np.zeros(6),where=den>0)
    u=np.isin(y,MASKS[g]);p=d[PC].to_numpy();lp=d[LC].to_numpy()
    ce=-lp[np.arange(len(d)),y];br=((p-np.eye(6)[y])**2).sum(1)
    mean=lambda value,select:float(np.average(value[select],weights=w[select]))
    all_=np.ones(len(y),dtype=bool)
    return dict(F1_all=float(f.mean()),F1_U=float(f[MASKS[g]].mean()),F1_C=float(np.delete(f,MASKS[g]).mean()),
                accuracy=mean((y==z).astype(float),all_),CE=mean(ce,all_),CE_U=mean(ce,u),CE_C=mean(ce,~u),
                Brier=mean(br,all_),Brier_U=mean(br,u),Brier_C=mean(br,~u)),cm,f

def bootstrap(d):
    contents=sorted(d.content_id.unique());ix={u:i for i,u in enumerate(contents)};groups=list(MASKS)
    cm=np.zeros((10,4,3,30,6,6),dtype=np.int32)
    for (a,p,g,u),part in d.groupby(['arm','target','group','content_id']):
        yy=truths(part);zz=part.prediction.to_numpy();cm[ALL_ARMS.index(a),PROTOCOLS.index(p),groups.index(g),ix[u]]=np.bincount(yy*6+zz,minlength=36).reshape(6,6)
    labels=d[['content_id','label_id']].drop_duplicates().set_index('content_id');require(len(labels)==30,'Unique content labels')
    labels=labels.loc[contents].label_id.to_numpy();rng=np.random.default_rng(20261012);weights=np.zeros((10000,30),np.int32)
    for label in LABELS:
        ids=np.where(labels==label)[0];require(len(ids)==5,'Five contents/business')
        picks=rng.choice(ids,size=(10000,5),replace=True)
        for i in range(10000):weights[i]+=np.bincount(picks[i],minlength=30)
    results=np.empty((10000,10))
    for left in range(0,10000,250):
        cc=np.einsum('bc,apgcyz->bapgyz',weights[left:left+250],cm,optimize=True);den=cc.sum(-1)+cc.sum(-2)
        f=np.divide(2*np.diagonal(cc,axis1=-2,axis2=-1),den,out=np.zeros_like(den,dtype=float),where=den>0)
        selected=[np.take(f[:,:,:,gi,:],MASKS[g],axis=-1).mean(-1) for gi,g in enumerate(groups)]
        results[left:left+250]=np.stack(selected,-1).mean((2,3))
    return contents,weights,results

def run():
    with stage('score'):
        c=contract();verify_seal(OUT/'predictions/complete.json');labels=[]
        for r in c['roles']:
            d=package(PREP/'packages'/r['id']/'labels.parquet','H-score','scorer',r).drop(columns='protocol');d['role_id']=r['id'];labels.append(d)
        data=pd.read_parquet(OUT/'predictions/visits.parquet').merge(pd.concat(labels),on=['role_id','visit_id'],validate='many_to_one');require(len(data)==14400,'Label coverage')
        scenes=[];classes=[];cms=[]
        for (a,p,g),part in data.groupby(['arm','target','group']):
            require(len(part)==120 and part.content_id.nunique()==30 and part.visit_id.is_unique,'Global content OOF coverage')
            m,cm,f=metrics(part,g);scenes.append(dict(arm=a,target=p,group=g,**m));cms.append(dict(arm=a,target=p,group=g,matrix=cm.tolist()))
            for y in range(6):classes.append(dict(arm=a,target=p,group=g,label=LABELS[y],label_index=y,F1=float(f[y]),support=int(cm[y].sum()),TP=int(cm[y,y]),FP=int(cm[:,y].sum()-cm[y,y]),FN=int(cm[y].sum()-cm[y,y]),uncovered=y in MASKS[g]))
        scenes=pd.DataFrame(scenes);targets=scenes.groupby(['arm','target'])[COLS].mean().reset_index();pooled=scenes.groupby('arm')[COLS].mean().reset_index()
        pooled=pooled.merge(targets.groupby('arm').F1_U.min().rename('worst_protocol_F1_U'),on='arm')
        for name,d in [('labeled-predictions',data),('scenarios',scenes),('targets',targets),('pooled',pooled),('classes',pd.DataFrame(classes))]:save(d,OUT/'scores'/(name+'.parquet'))
        write(OUT/'scores/confusions.json',cms)
        flips=[]
        dp=data[data.arm.eq('D-P')]
        for arm in PRIMARY+['RawPost-small','Marginal-small']:
            ref=data[data.arm.eq(arm)][['role_id','visit_id','prediction']].rename(columns={'prediction':'reference_prediction'})
            paired=dp.merge(ref,on=['role_id','visit_id'],validate='one_to_one');y=truths(paired)
            paired['repaired']=(paired.prediction.to_numpy()==y)&(paired.reference_prediction.to_numpy()!=y)
            paired['introduced']=(paired.prediction.to_numpy()!=y)&(paired.reference_prediction.to_numpy()==y)
            paired['prediction_changed']=paired.prediction.ne(paired.reference_prediction);paired['reference']=arm
            flips.append(paired)
        flip=pd.concat(flips);save(flip,OUT/'scores/error-flips.parquet')
        save(flip.groupby(['reference','target','group','content_id','label_id'])[['repaired','introduced','prediction_changed']].sum().reset_index(),OUT/'scores/error-flips-by-content.parquet')
        contents,w,boot=bootstrap(data);point=pooled.set_index('arm');contrasts=[]
        for arm in PRIMARY:
            delta=boot[:,ALL_ARMS.index('D-P')]-boot[:,ALL_ARMS.index(arm)];lo,hi=np.quantile(delta,[.05/14,1-.05/14])
            contrasts.append(dict(candidate='D-P',reference=arm,delta_F1_U=float(point.loc['D-P','F1_U']-point.loc[arm,'F1_U']),CI_99_285714=[float(lo),float(hi)],CI_95=np.quantile(delta,[.025,.975]).tolist(),positive_increment=bool(lo>0)))
        write(OUT/'comparisons/primary.json',dict(family=7,seed=20261012,samples=10000,comparisons=contrasts,model_conditional_not_external_validation=True,winner_selected=False))
        np.savez_compressed(writable(OUT/'comparisons/bootstrap.npz'),contents=np.array(contents),arms=np.array(ALL_ARMS),weights=w,F1_U=boot)
        progress('formal_scored',comparisons=contrasts)

if __name__=='__main__':run()

