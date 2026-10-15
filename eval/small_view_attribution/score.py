"""Six-class CM first, deployment/mask equal-weight F1 and content bootstrap."""
from common import *

PC=[f'p{i}' for i in range(6)]
COLS=['F1_all','F1_uncovered','F1_aux','accuracy','CE_nats','CE_bits','Brier']

def labeled():
    c=contract();p=OUT/'predictions/visits.parquet';checked(p,read(p.with_name('complete.json'))['sha256'],'prediction-seal')
    labels=[]
    for r in c['roles']:
        d=package(rolepath(r)/'labels.parquet','score').drop(columns='protocol')
        for k in ['outer','target','group']:d[k]=r[k]
        labels.append(d)
    return pd.read_parquet(p).merge(pd.concat(labels),on=['outer','target','group','visit_id'],validate='many_to_one')

def tables(d):
    scenes=[];classes=[];cms=[];folds=[];coverage=[]
    for (a,p,g),part in d.groupby(['arm','target','group']):
        require(len(part)==120 and part.visit_id.is_unique and part.content_id.nunique()==30,'OOF membership')
        m,cm,f=metrics(truths(part),part[PC].to_numpy(),MASKS[g]);scenes.append({'arm':a,'target':p,'group':g,**m})
        cms.append({'arm':a,'target':p,'group':g,'matrix':cm.tolist()})
        yy=truths(part)
        for y in range(6):classes.append({'arm':a,'target':p,'group':g,'label':LABELS[y],'label_index':y,
            'F1':float(f[y]),'uncovered':y in MASKS[g],'support':int(cm[y].sum()),
            'TP':int(cm[y,y]),'FP':int(cm[:,y].sum()-cm[y,y]),'FN':int(cm[y].sum()-cm[y,y])})
        for scope in ['C','U']:
            select=np.isin(yy,MASKS[g]);select=select if scope=='U' else ~select
            pp=part[PC].to_numpy()[select];yt=yy[select]
            coverage.append({'arm':a,'target':p,'group':g,'scope':scope,'exposures':len(yt),
                 'CE_nats':float(-np.log(pp[np.arange(len(yt)),yt]).mean()),
                 'Brier':float(((pp-np.eye(6)[yt])**2).sum(1).mean()),
                 'accuracy':float((pp.argmax(1)==yt).mean()),
                 'F1_full_six_class_CM':m['F1_uncovered' if scope=='U' else 'F1_aux']})
    for (a,p,g,o),part in d.groupby(['arm','target','group','outer']):
        m,_,_=metrics(truths(part),part[PC].to_numpy(),MASKS[g]);folds.append({'arm':a,'target':p,'group':g,'outer':int(o),**m})
    scene=pd.DataFrame(scenes);target=scene.groupby(['arm','target'])[COLS].mean().reset_index()
    pooled=scene.groupby('arm')[COLS].mean().reset_index()
    pooled=pooled.merge(target.groupby('arm').F1_uncovered.min().rename('worst_target_uncovered'),on='arm')
    return {'scenarios':scene,'targets':target,'pooled':pooled,'classes':pd.DataFrame(classes),
            'outer-folds':pd.DataFrame(folds),'coverage':pd.DataFrame(coverage),'labeled-predictions':d},cms

def bootstrap(d):
    contents=sorted(d.content_id.unique());uix={u:i for i,u in enumerate(contents)};groups=list(MASKS)
    cm=np.zeros((6,4,3,30,6,6),dtype=np.int32)
    for (a,p,g,u),part in d.groupby(['arm','target','group','content_id']):
        yy=truths(part);zz=part.prediction.to_numpy()
        cm[ARMS.index(a),PROTOCOLS.index(p),groups.index(g),uix[u]]=np.bincount(yy*6+zz,minlength=36).reshape(6,6)
    labels=d[['content_id','label_id']].drop_duplicates().set_index('content_id').loc[contents].label_id
    require(len(labels)==30,'Content label conflict');rng=np.random.default_rng(20261010)
    weights_=np.zeros((10000,30),dtype=np.int32)
    for label in LABELS:
        ids=np.where(labels.to_numpy()==label)[0];require(len(ids)==5,'Five contents per class')
        picks=rng.choice(ids,size=(10000,5),replace=True)
        for i in range(10000):weights_[i]+=np.bincount(picks[i],minlength=30)
    uncovered=np.empty((10000,6));aux=np.empty_like(uncovered)
    for left in range(0,10000,250):
        cc=np.einsum('bc,apgcyz->bapgyz',weights_[left:left+250],cm,optimize=True);den=cc.sum(-1)+cc.sum(-2)
        f1=np.divide(2*np.diagonal(cc,axis1=-2,axis2=-1),den,out=np.zeros_like(den,dtype=float),where=den>0)
        uu=[];aa=[]
        for gi,g in enumerate(groups):
            uu.append(np.take(f1[:,:,:,gi,:],MASKS[g],axis=-1).mean(-1))
            aa.append(np.delete(f1[:,:,:,gi,:],MASKS[g],axis=-1).mean(-1))
        uncovered[left:left+250]=np.stack(uu,-1).mean((2,3));aux[left:left+250]=np.stack(aa,-1).mean((2,3))
    return contents,weights_,uncovered,aux

def run():
    with stage('score'):
        d=labeled();dfs,cms=tables(d);prior=pd.read_parquet(PARENT/'scores/pooled.parquet').set_index('arm')
        point=dfs['pooled'].set_index('arm')
        for a in ARMS[:3]:require(np.max(np.abs(point.loc[a,COLS].to_numpy(float)-prior.loc[a,COLS].to_numpy(float)))<1e-12,'Frozen metric changed')
        for name,df in dfs.items():save(df,OUT/'scores'/(name+'.parquet'))
        write(OUT/'scores/confusion-matrices.json',cms)
        contents,w,u,aux=bootstrap(d);contrasts=[]
        for a,b in COMPARISONS:
            delta=u[:,ARMS.index(a)]-u[:,ARMS.index(b)];lo,hi=np.quantile(delta,[.05/6,1-.05/6])
            contrasts.append({'candidate':a,'reference':b,'delta_F1_uncovered':float(point.loc[a,'F1_uncovered']-point.loc[b,'F1_uncovered']),
                'CI_98_333333':[float(lo),float(hi)],'CI_95':np.quantile(delta,[.025,.975]).tolist(),'positive_increment':bool(lo>0)})
        write(OUT/'comparisons/primary.json',{'family':3,'bootstrap_seed':20261010,'bootstrap_samples':10000,
              'comparisons':contrasts,'all_three_passed':all(v['positive_increment'] for v in contrasts),
              'model_conditional_not_external_validation':True,'old_family_unchanged':True,'selected_winner':None})
        np.savez_compressed(writable(OUT/'comparisons/bootstrap.npz'),arms=np.array(ARMS),contents=np.array(contents),weights=w,uncovered=u,auxiliary=aux)
        progress('primary_results',comparisons=contrasts)

if __name__=='__main__':run()
