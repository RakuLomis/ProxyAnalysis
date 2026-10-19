"""P6 six-class OOF metrics, registered content bootstrap and all contrasts."""
from common import *
from weight_schedule import registry,PRIMARY,REFERENCES

PC=[f'p{i}' for i in range(6)]
LPC=[f'logp{i}' for i in range(6)]

def per_visit(d):
    y=truths(d);p=d[PC].to_numpy();lp=d[LPC].to_numpy()
    return y,-lp[np.arange(len(y)),y],((p-np.eye(6)[y])**2).sum(1)

def cm_f1(y,z,weights=None):
    cm=np.bincount(y*6+z,weights=weights,minlength=36).reshape(6,6)
    den=cm.sum(0)+cm.sum(1);f=np.divide(2*np.diag(cm),den,out=np.zeros(6),where=den>0)
    return cm,f

def metrics(d,missing):
    y,ce,br=per_visit(d);cm,f=cm_f1(y,d.prediction.to_numpy(int));u=np.isin(y,missing)
    out=dict(F1_all=float(f.mean()),F1_U=float(f[missing].mean()),F1_C=float(np.delete(f,missing).mean()),accuracy=float((d.prediction.to_numpy()==y).mean()))
    for scope,take in [('all',np.ones(len(y),bool)),('C',~u),('U',u)]:
        out['CE_'+scope]=float(ce[take].mean());out['Brier_'+scope]=float(br[take].mean())
    return out,cm,f

def bootstrap(d):
    arms=[p['id'] for p in registry()];contents=sorted(d.content_id.unique());ci={u:j for j,u in enumerate(contents)}
    ai={u:j for j,u in enumerate(arms)};cm=np.zeros((39,4,3,30,6,6),dtype=np.int32)
    for (a,p,g,u),part in d.groupby(['policy_id','target','group','content_id'],sort=False):
        yy=truths(part);zz=part.prediction.to_numpy(int)
        cm[ai[a],PROTOCOLS.index(p),list(MASKS).index(g),ci[u]]=np.bincount(yy*6+zz,minlength=36).reshape(6,6)
    cl=d[['content_id','label_id']].drop_duplicates().set_index('content_id').loc[contents].label_id.map(dict(zip(LABELS,range(6)))).to_numpy()
    require(len(cl)==30,'30 unique labeled contents');rng=np.random.default_rng(20261017);w=np.zeros((10000,30),np.int32)
    for y in range(6):
        ix=np.where(cl==y)[0];require(len(ix)==5,'Five contents per class');picks=rng.choice(ix,size=(10000,5),replace=True)
        for j in range(10000):w[j]+=np.bincount(picks[j],minlength=30)
    uu=np.empty((10000,39));cc=np.empty_like(uu)
    for start in range(0,10000,100):
        budget_check();mat=np.einsum('bc,apgcyz->bapgyz',w[start:start+100],cm,optimize=True);den=mat.sum(-1)+mat.sum(-2)
        f=np.divide(2*np.diagonal(mat,axis1=-2,axis2=-1),den,out=np.zeros_like(den,dtype=float),where=den>0)
        u=[];c=[]
        for gi,g in enumerate(MASKS):
            u.append(np.take(f[:,:,:,gi,:],MASKS[g],axis=-1).mean(-1));c.append(np.delete(f[:,:,:,gi,:],MASKS[g],axis=-1).mean(-1))
        uu[start:start+100]=np.stack(u,-1).mean((2,3));cc[start:start+100]=np.stack(c,-1).mean((2,3))
    return arms,contents,w,uu,cc,cm

def run():
    with stage('P6'):
        c=contract();d=pd.read_parquet(OUT/'predictions/visits.parquet');labs=[]
        for r in c['roles']:
            lab=package(rolepath(r)/'labels.parquet','score')[['visit_id','content_id','label_id']].copy();lab['role_id']=r['id'];labs.append(lab)
        labels=pd.concat(labs,ignore_index=True);require(not labels.duplicated(['role_id','visit_id']).any(),'Unique label keys')
        d=d.merge(labels,on=['role_id','visit_id'],validate='many_to_one');require(len(d)==56160 and d.content_id.nunique()==30,'Labeled coverage')
        save(d,OUT/'scores/labeled-predictions.parquet')
        scenes=[];classes=[];cms=[];folds=[];content=[]
        for (a,p,g),part in d.groupby(['policy_id','target','group']):
            require(len(part)==120 and part.visit_id.is_unique,'Merge all folds, not average fold F1')
            m,cm,f=metrics(part,MASKS[g]);scenes.append(dict(policy_id=a,target=p,group=g,**m));cms.append(dict(policy_id=a,target=p,group=g,matrix=cm.astype(int).tolist()))
            for y in range(6):
                tp=cm[y,y];classes.append(dict(policy_id=a,target=p,group=g,label=LABELS[y],label_index=y,scope='U' if y in MASKS[g] else 'C',
                    F1=float(f[y]),recall=float(tp/cm[y].sum()),precision=float(tp/cm[:,y].sum()) if cm[:,y].sum() else 0.,support=int(cm[y].sum()),predicted_count=int(cm[:,y].sum()),TP=int(tp),FP=int(cm[:,y].sum()-tp),FN=int(cm[y].sum()-tp)))
        for (a,p,g,o),part in d.groupby(['policy_id','target','group','outer']):
            m,_,_=metrics(part,MASKS[g]);folds.append(dict(policy_id=a,target=p,group=g,outer=o,**m))
        for (a,p,g,u),part in d.groupby(['policy_id','target','group','content_id']):
            y,ce,br=per_visit(part);content.append(dict(policy_id=a,target=p,group=g,content_id=u,label_id=part.label_id.iloc[0],scope='U' if y[0] in MASKS[g] else 'C',visits=len(part),accuracy=float((part.prediction.to_numpy()==y).mean()),CE=float(ce.mean()),Brier=float(br.mean())))
        scene=pd.DataFrame(scenes);cols=[k for k in scene if k not in ['policy_id','target','group']]
        pooled=scene.groupby('policy_id')[cols].mean().reset_index();targets=scene.groupby(['policy_id','target'])[cols].mean().reset_index()
        pooled=pooled.merge(targets.groupby('policy_id').F1_U.min().rename('worst_target_F1_U'),on='policy_id')
        for name,df in [('scenarios',scene),('targets',targets),('pooled',pooled),('classes',pd.DataFrame(classes)),('outer-folds',pd.DataFrame(folds)),('contents',pd.DataFrame(content))]:save(df,OUT/'scores'/(name+'.parquet'))
        write(OUT/'scores/confusion-matrices.json',cms)
        arms,contents,w,u,aux,cm=bootstrap(d)
        path=writable(OUT/'comparisons/bootstrap.npz');np.savez_compressed(path,arms=np.array(arms),contents=np.array(contents),weights=w,F1_U=u,F1_C=aux,content_confusions=cm)
        point=pooled.set_index('policy_id');primary=[]
        for ref in REFERENCES:
            delta=u[:,arms.index(PRIMARY)]-u[:,arms.index(ref)];lo,hi=np.quantile(delta,[.05/12,1-.05/12],method='linear')
            primary.append(dict(candidate=PRIMARY,reference=ref,delta_F1_U=float(point.loc[PRIMARY,'F1_U']-point.loc[ref,'F1_U']),
                CI_family=[float(lo),float(hi)],CI95=np.quantile(delta,[.025,.975],method='linear').tolist(),positive=bool(lo>0),negative=bool(hi<0),
                delta_CE_U=float(point.loc[PRIMARY,'CE_U']-point.loc[ref,'CE_U']),delta_Brier_U=float(point.loc[PRIMARY,'Brier_U']-point.loc[ref,'Brier_U'])))
        write(OUT/'comparisons/primary.json',dict(family=6,coverage=1-.05/6,samples=10000,seed=20261017,quantile_method='linear',comparisons=primary,post_H_selection=False))
        pairs=[]
        for source in ['P','G','RawPre','RawPost']:
            for m in [.1,.25,.5]:
                tag=f'{source}__m{int(m*100):03d}__'
                pairs.extend([(tag+'UPR',tag+'SYM','same_mass'),(tag+'UPR',tag+'CPR','same_mass')])
        pairs.extend([('P__m050__UPR','P-full','C_mapping_removed_same_U'),('P__m025__UPR','P__m010__UPR','dose'),('P__m050__UPR','P__m025__UPR','dose')])
        extra=[]
        for a,b,kind in pairs:
            dd=u[:,arms.index(a)]-u[:,arms.index(b)];extra.append(dict(candidate=a,reference=b,kind=kind,delta_F1_U=float(point.loc[a,'F1_U']-point.loc[b,'F1_U']),CI95=np.quantile(dd,[.025,.975],method='linear').tolist(),confirmatory=False))
        write(OUT/'comparisons/descriptive.json',extra)
        # Paired error/probability contributions preserve full-six-class prediction.
        flips=[];contrib=[];candidate=d[d.policy_id.eq(PRIMARY)].set_index(['role_id','visit_id']).sort_index()
        for ref in REFERENCES:
            other=d[d.policy_id.eq(ref)].set_index(['role_id','visit_id']).loc[candidate.index]
            y,ce,br=per_visit(candidate);yr,cer,brr=per_visit(other);require(np.array_equal(y,yr),'Matched labels')
            ac=candidate.prediction.to_numpy()==y;bc=other.prediction.to_numpy()==y
            states=np.where(ac,np.where(bc,'both_correct','repaired'),np.where(bc,'new_error','both_wrong'))
            dc=ce-cer;db=br-brr
            f=candidate[['target','group','outer','content_id','label_id','prediction']].reset_index();f['reference']=ref;f['reference_prediction']=other.prediction.to_numpy();f['state']=states;f['delta_CE']=dc;f['delta_Brier']=db
            f['scope']=['U' if yy in MASKS[g] else 'C' for yy,g in zip(y,f.group)]
            f['candidate_pred_role']=['U' if yy in MASKS[g] else 'C' for yy,g in zip(f.prediction,f.group)]
            f['reference_pred_role']=['U' if yy in MASKS[g] else 'C' for yy,g in zip(f.reference_prediction,f.group)]
            flips.append(f)
            for (p,g),ix in f.groupby(['target','group']).groups.items():
                ix=np.asarray(list(ix));require(len(ix)==120,'Contribution context')
                for scope in ['all','C','U']:
                    take=ix if scope=='all' else ix[f.loc[ix,'scope'].eq(scope).to_numpy()]
                    acc=[];abb=[]
                    for state in ['both_correct','repaired','new_error','both_wrong']:
                        ii=take[states[take]==state];cv=float(dc[ii].sum()/len(take));bv=float(db[ii].sum()/len(take));acc.append(cv);abb.append(bv)
                        contrib.append(dict(reference=ref,target=p,group=g,scope=scope,state=state,count=len(ii),total=len(take),mass=len(ii)/len(take),CE_contribution=cv,Brier_contribution=bv,
                            conditional_delta_CE=float(dc[ii].mean()) if len(ii) else None,conditional_delta_Brier=float(db[ii].mean()) if len(ii) else None))
                    require(abs(sum(acc)-dc[take].mean())<1e-12 and abs(sum(abb)-db[take].mean())<1e-12,'Probability contributions do not sum')
        save(pd.concat(flips,ignore_index=True),OUT/'scores/error-transitions.parquet');save(pd.DataFrame(contrib),OUT/'scores/probability-contributions.parquet')
        base='P__m010__SYM';deltaC=float(point.loc[PRIMARY,'F1_C']-point.loc[base,'F1_C']);t=targets.set_index(['policy_id','target'])
        deploymentC={p:float(t.loc[(PRIMARY,p),'F1_C']-t.loc[(base,p),'F1_C']) for p in PROTOCOLS}
        write(OUT/'scores/C-practical-cost.json',dict(delta_F1_C=deltaC,overall_pass=bool(deltaC>=-.01),per_deployment=deploymentC,each_deployment_pass=all(v>=-.02 for v in deploymentC.values()),not_statistical_noninferiority=True,not_used_for_fallback=True))

