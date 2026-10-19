"""Post-only inference barrier, full-six-class scoring and fixed content bootstrap."""
from common import *

METRIC_NAMES=['F1_U','F1_C','F1_all','CE_U','CE_C','CE_all','Brier_U','Brier_C','Brier_all']

def predict_post(model,values):
    require(values.ndim==2 and values.shape[1]==96,'Prediction input shape')
    x=(values-model['mu'])/model['scale']
    logits=x@model['weight'].T+model['bias'];p=logits.softmax(1)
    require(torch.isfinite(logits).all() and torch.isfinite(p).all() and (p>0).all(),'Nonfinite/zero query probability')
    return logits,p

def predict():
    with stage('P3'):
        verify_seal(OUT/'models-complete.json');rows=[]
        for r in contract()['roles']:
            q=package(PREP/'packages'/r['id']/'query.parquet',r,'query')
            require(len(q)==24,'Query rows')
            raw=tensor(q[HIST])
            for arm in ARMS:
                m=own(OUT/'models'/r['id']/(arm+'.pt'))
                with compute('post-only-'+r['id']+'/'+arm):z,p=predict_post(m,raw)
                d=pd.DataFrame(cpu(p),columns=[f'p{i}' for i in range(6)])
                for i in range(6):d[f'logit{i}']=cpu(z[:,i])
                d['visit_id']=q.visit_id.to_numpy();d['prediction']=cpu(p.argmax(1))
                d['role_id']=r['id'];d['role_target']=r['target'];d['query_deployment']=r['calibration'];d['group']=r['group'];d['inner']=r['inner'];d['arm']=arm
                rows.append(d)
        df=pd.concat(rows,ignore_index=True)
        require(len(df)==4608 and not df.duplicated(['role_id','arm','visit_id']).any(),'Prediction completeness')
        save(df,'predictions');seal(OUT/'predictions-complete.json',[OUT/'predictions.parquet'],rows=4608,models=192,label_reads=0,actual_H_U_reads=0)

def scored_predictions():
    verify_seal(OUT/'predictions-complete.json')
    predictions=pd.read_parquet(OUT/'predictions.parquet');labels=[]
    for r in contract()['roles']:
        d=package(PREP/'packages'/r['id']/'labels.parquet',r,'labels')
        require(list(d)==['visit_id','content_id','label_id','protocol'] and d.visit_id.is_unique,'Label schema')
        require(set(d.protocol)=={r['calibration']} and set(d.content_id)==set(r['validation_contents']),'Scoring scope')
        require(d.groupby('content_id').size().eq(4).all(),'Query content repeats')
        d=d.copy();d['role_id']=r['id'];d['y']=truths(d);labels.append(d)
    meta=pd.concat(labels,ignore_index=True)
    require(len(meta)==1152 and meta.visit_id.nunique()==384 and meta.content_id.nunique()==24,'Scoring independence counts')
    require(meta.groupby(['protocol','visit_id']).content_id.nunique().eq(1).all(),'Visit metadata identity conflict')
    unique=meta[['content_id','y']].drop_duplicates()
    require(len(unique)==24 and unique.groupby('y').size().eq(4).all(),'Six business strata')
    d=predictions.merge(meta,on=['role_id','visit_id'],validate='many_to_one')
    require(len(d)==4608 and (d.query_deployment==d.protocol).all(),'Prediction label routing')
    prob=d[[f'p{i}' for i in range(6)]].to_numpy(); y=d.y.to_numpy()
    d['CE']=-np.log(prob[np.arange(len(d)),y]);d['Brier']=((prob-np.eye(6)[y])**2).sum(1)
    d['confidence']=prob.max(1);d['true_probability']=prob[np.arange(len(d)),y]
    d['correct']=d.prediction==d.y
    return d

def cell_metrics(d,missing):
    y=d.y.to_numpy(int);pred=d.prediction.to_numpy(int)
    cm=np.bincount(y*6+pred,minlength=36).reshape(6,6)
    den=cm.sum(0)+cm.sum(1);f=np.divide(2*np.diag(cm),den,out=np.zeros(6),where=den>0)
    is_u=np.isin(y,missing)
    require(is_u.any() and (~is_u).any(),'Empty probability subgroup')
    m=dict(F1_U=f[missing].mean(),F1_C=np.delete(f,missing).mean(),F1_all=f.mean(),accuracy=d.correct.mean(),rows=len(d))
    for mask,name in [(is_u,'U'),(~is_u,'C'),(np.ones(len(d),bool),'all')]:
        m['CE_'+name]=d.loc[mask,'CE'].mean();m['Brier_'+name]=d.loc[mask,'Brier'].mean()
    return m,cm,f

def tables(d):
    rows=[];cms=[];business=[]
    for key,g in d.groupby(['role_target','query_deployment','group','arm'],sort=True):
        target,dep,group,arm=key;require(len(g)==96 and g.inner.nunique()==4,'Pool four inner folds first')
        meta=dict(role_target=target,query_deployment=dep,group=group,arm=arm)
        m,cm,f=cell_metrics(g,MASKS[group]);rows.append(dict(**meta,**m))
        for y in range(6):
            business.append(dict(**meta,label=y,business=LABELS[y],F1=f[y],status='U' if y in MASKS[group] else 'C'))
            for p in range(6):cms.append(dict(**meta,truth=y,prediction=p,count=int(cm[y,p])))
    role=pd.DataFrame(rows);require(len(role)==48,'12 cells x 4 arms')
    numeric=METRIC_NAMES+['accuracy']
    dep=role.groupby(['role_target','query_deployment','arm'],as_index=False)[numeric].mean()
    overall=role.groupby('arm',as_index=False)[numeric].mean()
    worst=dep.loc[dep.groupby('arm').F1_U.idxmin(),['arm','query_deployment','F1_U']].copy()
    content=d.groupby(['role_target','query_deployment','group','arm','content_id','y'],as_index=False).agg(
        visits=('visit_id','size'),accuracy=('correct','mean'),CE=('CE','mean'),Brier=('Brier','mean'))
    return {'metrics-by-role-group':role,'metrics-by-query-deployment':dep,'metrics-overall':overall,
            'metrics-worst-deployment':worst,'metrics-by-business':pd.DataFrame(business),
            'confusion-matrices':pd.DataFrame(cms),'metrics-by-content':content}

def aggregate_content(d):
    contents=sorted(d.content_id.unique());index={u:i for i,u in enumerate(contents)}
    labels=d[['content_id','y']].drop_duplicates().set_index('content_id').loc[contents].y.to_numpy(int)
    cells=[(p,gr) for p in PROTOCOLS for gr in MASKS]
    cm=np.zeros((4,12,24,6,6));risks=np.zeros((4,12,24,2));counts=np.zeros((12,24))
    for ai,arm in enumerate(ARMS):
        for ci,(target,group) in enumerate(cells):
            sub=d[(d.arm==arm)&(d.role_target==target)&(d.group==group)]
            for u,g in sub.groupby('content_id'):
                k=index[u];require(len(g)==4,'Content cell repeats')
                cm[ai,ci,k]=np.bincount((g.y*6+g.prediction).to_numpy(),minlength=36).reshape(6,6)
                risks[ai,ci,k]=g[['CE','Brier']].sum().to_numpy();counts[ci,k]=len(g)
    require((counts==4).all(),'All query contents present in each pooled cell')
    masks=np.array([[y in MASKS[group] for y in labels] for _,group in cells],float)
    return contents,labels,cm,risks,counts,masks

def bootstrap_counts(labels):
    rng=np.random.default_rng(20261016);w=np.zeros((10000,24),dtype=np.float64)
    for y in range(6):
        ix=np.flatnonzero(labels==y);require(len(ix)==4,'Bootstrap stratum count')
        draw=rng.integers(0,4,size=(10000,4))
        for k in range(4):w[:,ix[k]]=(draw==k).sum(1)
    require((w.sum(1)==24).all(),'Bootstrap mass')
    return w

def bootstrap_gpu(cm,risks,counts,masks,weights):
    """Rebuild full confusion matrices under shared content counts, on CUDA FP64."""
    c,r,n,um=tensor(cm),tensor(risks),tensor(counts),tensor(masks)
    umclass=tensor(np.array([[y in MASKS[g] for y in range(6)] for _ in PROTOCOLS for g in MASKS],float))
    out=[];dep=[]
    for start in range(0,len(weights),250):
        w=tensor(weights[start:start+250]);b=len(w)
        # axes bootstrap, arm, pooled role/mask, true class, predicted class
        cc=(w@c.permute(2,0,1,3,4).reshape(24,-1)).reshape(b,4,12,6,6)
        denominator=cc.sum(-1)+cc.sum(-2)
        f=2*cc.diagonal(dim1=-2,dim2=-1)/denominator.clamp_min(1)
        fu=(f*umclass).sum(-1)/2;fc=(f*(1-umclass)).sum(-1)/4;fa=f.mean(-1)
        risk=(w@r.permute(2,0,1,3).reshape(24,-1)).reshape(b,4,12,2)
        ru=(w@(r*um[None,:,:,None]).permute(2,0,1,3).reshape(24,-1)).reshape(b,4,12,2)
        nu=w@(n*um).T;nc=w@(n*(1-um)).T;na=w@n.T
        rc=risk-ru
        vals=torch.stack([fu,fc,fa,ru[...,0]/nu[:,None,:],rc[...,0]/nc[:,None,:],risk[...,0]/na[:,None,:],
              ru[...,1]/nu[:,None,:],rc[...,1]/nc[:,None,:],risk[...,1]/na[:,None,:]],-1)
        require(torch.isfinite(vals).all(),'Nonfinite bootstrap metric')
        out.append(cpu(vals.mean(2)));dep.append(cpu(vals.reshape(b,4,4,3,9).mean(3)))
    return np.concatenate(out),np.concatenate(dep)

def bootstrap_independent(cm,risks,counts,masks,weights):
    """Independent NumPy reconstruction for all 10000 draws, no GPU code reuse."""
    cls=np.array([[int(y in MASKS[g]) for y in range(6)] for _ in PROTOCOLS for g in MASKS])
    pieces=[]
    for begin in range(0,len(weights),200):
        w=weights[begin:begin+200]
        cc=np.einsum('bk,ackij->bacij',w,cm,optimize=True)
        den=cc.sum(-1)+cc.sum(-2);f=2*np.diagonal(cc,axis1=-2,axis2=-1)/np.maximum(den,1)
        allrisk=np.einsum('bk,ackj->bacj',w,risks,optimize=True)
        urisk=np.einsum('bk,ackj,ck->bacj',w,risks,masks,optimize=True)
        nu=w@(counts*masks).T;nc=w@(counts*(1-masks)).T;na=w@counts.T
        crisk=allrisk-urisk
        values=np.stack([(f*cls).sum(-1)/2,(f*(1-cls)).sum(-1)/4,f.mean(-1),
              urisk[...,0]/nu[:,None,:],crisk[...,0]/nc[:,None,:],allrisk[...,0]/na[:,None,:],
              urisk[...,1]/nu[:,None,:],crisk[...,1]/nc[:,None,:],allrisk[...,1]/na[:,None,:]],-1)
        pieces.append(values.mean(2))
    return np.concatenate(pieces)

def errors(d):
    rows=[]
    keys=['role_id','visit_id']
    columns=keys+['role_target','query_deployment','group','inner','content_id','y','prediction','correct','confidence','true_probability','CE','Brier']+[f'p{i}' for i in range(6)]
    for cand,ref in COMPARISONS:
        a=d[d.arm==cand][columns];b=d[d.arm==ref][columns]
        m=a.merge(b,on=keys,suffixes=('_candidate','_reference'),validate='one_to_one')
        require(len(m)==1152,'Error comparison completeness')
        for key in ['role_target','query_deployment','group','inner','content_id','y']:
            require((m[key+'_candidate']==m[key+'_reference']).all(),'Comparison metadata conflict')
            m[key]=m[key+'_candidate'];m=m.drop(columns=[key+'_candidate',key+'_reference'])
        ac=m.correct_candidate.to_numpy();bc=m.correct_reference.to_numpy()
        m['case']=np.where(ac & ~bc,'repair',np.where(~ac & bc,'new_error',np.where(ac,'both_correct','both_wrong')))
        m['class_changed']=m.prediction_candidate!=m.prediction_reference
        m['CE_delta']=m.CE_candidate-m.CE_reference;m['Brier_delta']=m.Brier_candidate-m.Brier_reference
        m['probability_L1']=np.abs(m[[f'p{i}_candidate' for i in range(6)]].to_numpy()-m[[f'p{i}_reference' for i in range(6)]].to_numpy()).sum(1)
        m['comparison']=cand+'-'+ref;m['is_U']=[y in MASKS[g] for y,g in zip(m.y,m.group)]
        rows.append(m)
    flips=pd.concat(rows,ignore_index=True)
    summary=flips.groupby(['comparison','query_deployment','is_U','case'],as_index=False).agg(
        exposures=('visit_id','size'),CE_delta_sum=('CE_delta','sum'),Brier_delta_sum=('Brier_delta','sum'),
        confidence_candidate=('confidence_candidate','mean'),confidence_reference=('confidence_reference','mean'))
    common=flips[flips.case=='both_wrong'].groupby(['comparison','query_deployment','is_U'],as_index=False).agg(
        exposures=('visit_id','size'),CE_delta_sum=('CE_delta','sum'),Brier_delta_sum=('Brier_delta','sum'),
        confidence_candidate=('confidence_candidate','mean'),confidence_reference=('confidence_reference','mean'),
        true_probability_candidate=('true_probability_candidate','mean'),true_probability_reference=('true_probability_reference','mean'))
    return flips,summary,common

def score():
    with stage('P4'):
        d=scored_predictions();save(d,'scored-predictions')
        ts=tables(d)
        for name,t in ts.items():save(t,name)
        contents,labels,cm,risks,counts,masks=aggregate_content(d);weights=bootstrap_counts(labels)
        with compute('content-bootstrap-10000'):
            draws,depdraws=bootstrap_gpu(cm,risks,counts,masks,weights)
            point,_=bootstrap_gpu(cm,risks,counts,masks,np.ones((1,24)))
        ordinary=ts['metrics-overall'].set_index('arm').loc[ARMS,METRIC_NAMES].to_numpy()
        require(np.max(np.abs(point[0]-ordinary))<1e-12,'Bootstrap point vs independent table')
        primary={}
        for cand,ref in COMPARISONS:
            a,b=ARMS.index(cand),ARMS.index(ref);delta=draws[:,a]-draws[:,b];pt=ordinary[a]-ordinary[b]
            key=cand+'-'+ref;primary[key]=dict(candidate=cand,reference=ref,point=dict(zip(METRIC_NAMES,pt)),
                F1_U_CI95=np.quantile(delta[:,0],[.025,.975]).tolist(),
                F1_U_family_CI=np.quantile(delta[:,0],[.025/3,1-.025/3]).tolist(),
                metric_CI95={name:np.quantile(delta[:,k],[.025,.975]).tolist() for k,name in enumerate(METRIC_NAMES)},
                family_size=3,family_interval_level=1-.05/3)
        interaction=draws[:,0,0]-draws[:,1,0]-draws[:,2,0]+draws[:,3,0]
        ip=ordinary[0,0]-ordinary[1,0]-ordinary[2,0]+ordinary[3,0]
        write(OUT/'primary-comparisons.json',primary)
        write(OUT/'interaction.json',dict(F1_U_point=ip,CI95=np.quantile(interaction,[.025,.975]).tolist(),interpretation='descriptive nonadditivity, not physical causation or mutual information'))
        np.savez_compressed(writable(OUT/'bootstrap.npz'),counts=weights,draws=draws,deployment_draws=depdraws,
              contents=np.array(contents),labels=labels,metric_names=np.array(METRIC_NAMES),arms=np.array(ARMS))
        flips,summary,common=errors(d);save(flips,'error-flips');save(summary,'error-flip-summary');save(common,'shared-error-probability-cost')
        dep=ts['metrics-by-query-deployment'];diff={}
        for p in PROTOCOLS:
            g=dep[dep.query_deployment==p].set_index('arm');diff[p]=g.loc['GP','F1_C']-g.loc['PP','F1_C']
        overall=ordinary[2,1]-ordinary[0,1]
        write(OUT/'C-practical-screen.json',dict(GP_minus_PP_overall=overall,by_query_deployment=diff,
             overall_floor=-.01,deployment_floor=-.02,passed=overall>=-.01 and min(diff.values())>=-.02,
             screen_not_statistical_noninferiority=True))
        write(OUT/'coverage.json',dict(tasks=48,logical_endpoints=192,prediction_rows=len(d),task_query_exposures=1152,
             unique_query_visits=d.visit_id.nunique(),query_contents=d.content_id.nunique(),contents_per_business=4,
             pooled_cells=12,folds_per_cell=4,seeds=0))
        seal(OUT/'scores-complete.json',list(OUT.glob('metrics-*.parquet'))+[OUT/'primary-comparisons.json',OUT/'interaction.json',OUT/'bootstrap.npz',OUT/'C-practical-screen.json',OUT/'scored-predictions.parquet'])
