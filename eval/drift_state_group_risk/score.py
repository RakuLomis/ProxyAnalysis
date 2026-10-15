"""Independent scoring, three-family content bootstrap and offline states."""
import sys
from common import *
from grouping import sourcekernel,true_scores

def evaluate():
    c=start('outer-score'); dst=OUT/'scores'; labels=[]
    path=OUT/'predictions/visits.parquet'
    require(read(path.parent/'complete.json')['sha256'][path.name]==sha(path),'Prediction seal')
    for r in c['roles']:
        if r['inner'] is not None: continue
        labels.append(package(mainfolder('packages',r)/'score-labels.parquet','outer-score'))
    pred=pd.read_parquet(path); d=pred.merge(pd.concat(labels,ignore_index=True).drop(columns='protocol'),on='visit_id',validate='many_to_one')
    require(len(d)==2400 and d.groupby(['protocol','arm']).size().eq(120).all(),'Outcome support')
    save(d,dst/'scored-visits.parquet'); rows=[]; classes=[]; cms=[]
    for (proto,arm),sub in d.groupby(['protocol','arm']):
        values,cm=metrics(truths(sub),sub[[f'p{i}' for i in range(6)]].to_numpy()); rows.append({'protocol':proto,'arm':arm,**values})
        for y,label in enumerate(LABELS):
            den=cm[y].sum()+cm[:,y].sum(); classes.append({'protocol':proto,'arm':arm,'business':label,'support':int(cm[y].sum()),
              'F1':float(2*cm[y,y]/den) if den else 0.,'recall':float(cm[y,y]/cm[y].sum()),
              'precision':float(cm[y,y]/cm[:,y].sum()) if cm[:,y].sum() else 0.})
            for z in range(6): cms.append({'protocol':proto,'arm':arm,'truth':label,'predicted':LABELS[z],'count':int(cm[y,z])})
    summary=pd.DataFrame(rows); save(summary,dst/'protocol-summary.parquet'); save(pd.DataFrame(classes),dst/'class-summary.parquet'); save(pd.DataFrame(cms),dst/'confusion.parquet')
    overall=summary.groupby('arm').agg(equal_protocol_F1=('F1','mean'),worst_protocol_F1=('F1','min'),mean_CE=('CE','mean'),mean_Brier=('Brier','mean')).reset_index()
    pooled=[]
    for arm,sub in d.groupby('arm'):
        m,_=metrics(truths(sub),sub[[f'p{i}' for i in range(6)]].to_numpy()); pooled.append({'arm':arm,**{'pooled_'+k:v for k,v in m.items()}})
    overall=overall.merge(pd.DataFrame(pooled),on='arm'); save(overall,dst/'overall-summary.parquet')
    flip=[]
    for proto in PROTOCOLS:
        b=d[(d.protocol==proto)&(d.arm=='DSR4')].set_index('visit_id')
        for ref in ARMS[:-1]:
            other=d[(d.protocol==proto)&(d.arm==ref)].set_index('visit_id').loc[b.index]
            y=truths(b); repaired=(b.prediction.to_numpy()==y)&(other.prediction.to_numpy()!=y)
            added=(b.prediction.to_numpy()!=y)&(other.prediction.to_numpy()==y)
            for k,visit in enumerate(b.index):
                flip.append({'protocol':proto,'reference':ref,'visit_id':visit,'content_id':b.iloc[k].content_id,'business':b.iloc[k].label_id,
                  'repaired':bool(repaired[k]),'added':bool(added[k]),'changed':bool(b.iloc[k].prediction!=other.iloc[k].prediction),
                  'true_probability_change':float(b.iloc[k][f'p{y[k]}']-other.iloc[k][f'p{y[k]}'])})
    f=pd.DataFrame(flip); save(f,dst/'error-flip-visits.parquet')
    save(f.groupby(['protocol','reference'],as_index=False)[['repaired','added','changed']].sum(),dst/'error-flip-summary.parquet')
    save(f.groupby(['protocol','reference','business','content_id'],as_index=False)[['repaired','added','changed']].sum(),dst/'content-flips.parquet')
    finish('D21',scored_visits=len(d)); print(summary.pivot(index='protocol',columns='arm',values='F1').to_string(),flush=True)

def bootstrap_f1(y,pred,mult):
    cm=(mult@np.eye(36)[y*6+pred]).reshape(-1,6,6); tp=np.diagonal(cm,axis1=1,axis2=2); den=cm.sum(1)+cm.sum(2)
    return np.divide(2*tp,den,out=np.zeros_like(tp),where=den>0).mean(1)

def bootstrap():
    c=start('bootstrap'); d=pd.read_parquet(OUT/'scores/scored-visits.parquet')
    contents=d[['content_id','label_id']].drop_duplicates().sort_values(['label_id','content_id']).reset_index(drop=True)
    require(len(contents)==30 and contents.groupby('label_id').size().eq(5).all(),'Content bootstrap scope')
    rng=np.random.default_rng(20261005); ix=np.concatenate([rng.choice(np.arange(5*y,5*y+5),(10000,5),replace=True) for y in range(6)],1)
    counts=np.stack([np.bincount(row,minlength=30) for row in ix]); lookup=dict(zip(contents.content_id,range(30)))
    destination=OUT/'comparisons'; destination.mkdir(parents=True,exist_ok=True); np.save(destination/'bootstrap-indices.npy',ix); save(contents,destination/'content-order.parquet')
    protocol=pd.read_parquet(OUT/'scores/protocol-summary.parquet').set_index(['protocol','arm']); arrays={}; exploratory=[]
    for p in PROTOCOLS:
        for arm in ARMS:
            sub=d[(d.protocol==p)&(d.arm==arm)].sort_values('visit_id')
            arrays[p,arm]=bootstrap_f1(truths(sub),sub.prediction.to_numpy(int),counts[:,sub.content_id.map(lookup)])
        for ref in ARMS[1:4]:
            value=arrays[p,'DSR4']-arrays[p,ref]; lo,hi=np.quantile(value,[.025,.975])
            exploratory.append({'protocol':p,'reference':ref,'point':float(protocol.loc[(p,'DSR4'),'F1']-protocol.loc[(p,ref),'F1']),
                'lo95':float(lo),'hi95':float(hi),'descriptive_not_main_family':True})
    mean={a:sum(arrays[p,a] for p in PROTOCOLS)/4 for a in ARMS}; records=[]
    for ref in ARMS[1:4]:
        value=mean['DSR4']-mean[ref]; q=np.quantile(value,[.025,.975,.05/6,1-.05/6])
        point=float(sum(protocol.loc[(p,'DSR4'),'F1']-protocol.loc[(p,ref),'F1'] for p in PROTOCOLS)/4)
        records.append({'comparison':'DSR4-'+ref,'point':point,'lo95':float(q[0]),'hi95':float(q[1]),
           'family_lower':float(q[2]),'family_upper':float(q[3]),'family_positive':bool(q[2]>0),'family':3,
           'fixed_selected_models':True,'practical_vs_DSR1':bool(point>=.01) if ref=='DSR1' else False})
    save(pd.DataFrame(records),destination/'main-contrasts.parquet'); save(pd.DataFrame(exploratory),destination/'protocol-descriptive.parquet')
    complete(destination,samples=10000,family=3,conditional_no_refit=True)
    finish('D22',main_comparisons=3,samples=10000); print(pd.DataFrame(records).to_string(index=False),flush=True)

def test_states():
    c=start('test-state'); sources={s['id']:s for s in c['sources']}; bounds=pd.read_parquet(OUT/'states/outer-boundaries.parquet'); states=[]
    for r in c['roles']:
        if r['inner'] is not None: continue
        raw=package(mainfolder('packages',r)/'test-paired.parquet','test-state'); labels=raw[['visit_id','label_id','content_id']].drop_duplicates()
        raw=raw.drop(columns='label_id'); estimates=[]
        for q in c['queries']:
            if rolekey(q['parent'])!=rolekey(r): continue
            source=sources[q['source']]; estimates.append(true_scores(raw,[sourcekernel(source,j) for j in range(10)]))
        require(len(estimates)==4,'Four CF18 sources for offline test score')
        base=estimates[0].copy()
        for col in ['d_true','zero_support','low_support']:
            base[col]=np.mean([d.set_index('visit_id').loc[base.visit_id,col].to_numpy() for d in estimates],0)
        base=base[['visit_id','d_true','zero_support','low_support','connections']].merge(labels,on='visit_id',validate='one_to_one')
        bd=bounds[(bounds.outer==r['outer'])&(bounds.protocol==r['protocol'])&(bounds.arm=='DSR4')].set_index('y')
        low=[]
        for row in base.itertuples():
            threshold=bd.loc[LABELS.index(row.label_id)]; score=row.d_true
            low.append(1. if score<threshold.threshold else 0. if score>threshold.threshold else float(threshold.boundary_low_fraction))
        base['low_mass']=low; base['high_mass']=1-base.low_mass; base['outer']=r['outer']; base['protocol']=r['protocol']; states.append(base)
    s=pd.concat(states,ignore_index=True); save(s,OUT/'diagnostics/offline-test-states.parquet')
    pred=pd.read_parquet(OUT/'scores/scored-visits.parquet'); pred=pred.merge(s[['visit_id','low_mass','high_mass','d_true']],on='visit_id',validate='many_to_one')
    rows=[]
    for (p,a),d in pred.groupby(['protocol','arm']):
        y=truths(d); probs=d[[f'p{i}' for i in range(6)]].to_numpy(); z=probs.argmax(1)
        for name in ['low','high']:
            w=d[name+'_mass'].to_numpy(); cm=np.bincount(y*6+z,weights=w,minlength=36).reshape(6,6); den=cm.sum(0)+cm.sum(1)
            f1=np.divide(2*np.diag(cm),den,out=np.zeros(6),where=den>0)
            rows.append({'protocol':p,'arm':a,'state':name,'mass':float(w.sum()),'class_support':int((cm.sum(1)>0).sum()),
              'F1_descriptive':float(f1.mean()) if (cm.sum(1)>0).all() else None,
              'accuracy':float((w*(z==y)).sum()/w.sum()) if w.sum() else None,
              'CE':float((-w*np.log(probs[np.arange(len(y)),y])).sum()/w.sum()) if w.sum() else None,
              'post_only_inference':False})
    save(pd.DataFrame(rows),OUT/'diagnostics/offline-state-scores.parquet')
    finish('D23',offline_only=True,test_medians_reestimated=False,test_scores_used_for_fit=False)

if __name__=='__main__': {'evaluate':evaluate,'bootstrap':bootstrap,'test-states':test_states}[sys.argv[1]]()
