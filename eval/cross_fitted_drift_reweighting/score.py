"""Independent classification, shared content bootstrap and fixed-state appendix."""
import sys
from common import *

def evaluate():
    c=start('outer-score'); path=OUT/'predictions/visits.parquet'; dst=OUT/'scores'
    require(read(path.parent/'complete.json')['sha256'][path.name]==sha(path),'Outer prediction seal'); labels=[]
    for r in c['roles']:
        if r['inner'] is None: labels.append(package(r,'score-labels','outer-score'))
    d=pd.read_parquet(path).merge(pd.concat(labels,ignore_index=True).drop(columns='protocol'),on='visit_id',validate='many_to_one')
    require(len(d)==2400 and d.groupby(['protocol','arm']).size().eq(120).all(),'All six classes and visits retained')
    save(d,dst/'scored-visits.parquet'); rows=[]; classes=[]; cms=[]
    for (p,a),sub in d.groupby(['protocol','arm']):
        values,cm=metrics(truths(sub),sub[[f'p{i}' for i in range(6)]].to_numpy()); rows.append({'protocol':p,'arm':a,**values})
        for j,label in enumerate(LABELS):
            den=cm[j].sum()+cm[:,j].sum(); classes.append({'protocol':p,'arm':a,'business':label,'support':int(cm[j].sum()),
              'F1':float(2*cm[j,j]/den) if den else 0.,'recall':float(cm[j,j]/cm[j].sum()),
              'precision':float(cm[j,j]/cm[:,j].sum()) if cm[:,j].sum() else 0.})
            for k in range(6): cms.append({'protocol':p,'arm':a,'truth':label,'predicted':LABELS[k],'count':int(cm[j,k])})
    summary=pd.DataFrame(rows); save(summary,dst/'protocol-summary.parquet'); save(pd.DataFrame(classes),dst/'class-summary.parquet'); save(pd.DataFrame(cms),dst/'confusion.parquet')
    overall=summary.groupby('arm').agg(equal_protocol_F1=('F1','mean'),worst_protocol_F1=('F1','min'),mean_CE=('CE','mean'),mean_Brier=('Brier','mean')).reset_index()
    pooled=[]
    for a,sub in d.groupby('arm'):
        m,_=metrics(truths(sub),sub[[f'p{i}' for i in range(6)]].to_numpy()); pooled.append({'arm':a,**{'pooled_'+k:v for k,v in m.items()}})
    save(overall.merge(pd.DataFrame(pooled),on='arm'),dst/'overall-summary.parquet')
    flips=[]
    for proto in PROTOCOLS:
        b=d[(d.protocol==proto)&(d.arm=='RW4')].set_index('visit_id')
        for ref in ARMS[:-1]:
            a=d[(d.protocol==proto)&(d.arm==ref)].set_index('visit_id').loc[b.index]; y=truths(b)
            for k,visit in enumerate(b.index):
                flips.append({'protocol':proto,'reference':ref,'visit_id':visit,'content_id':b.iloc[k].content_id,'business':b.iloc[k].label_id,
                  'repaired':bool(b.iloc[k].prediction==y[k] and a.iloc[k].prediction!=y[k]),
                  'added':bool(b.iloc[k].prediction!=y[k] and a.iloc[k].prediction==y[k]),
                  'changed':bool(b.iloc[k].prediction!=a.iloc[k].prediction),
                  'true_probability_change':float(b.iloc[k][f'p{y[k]}']-a.iloc[k][f'p{y[k]}'])})
    f=pd.DataFrame(flips); save(f,dst/'error-flip-visits.parquet')
    for keys,name in [(['protocol','reference'],'error-flip-summary'),(['protocol','reference','business'],'business-flips'),
      (['protocol','reference','business','content_id'],'content-flips')]:
        save(f.groupby(keys,as_index=False)[['repaired','added','changed']].sum(),dst/(name+'.parquet'))
    complete(dst,rows=2400,post_prediction_labels_only=True)
    finish('RW21-RW23-partial',scored_visits=len(d)); print(summary.pivot(index='protocol',columns='arm',values='F1').to_string(),flush=True)

def bootstrap_f1(y,z,mult):
    cm=(mult@np.eye(36)[y*6+z]).reshape(-1,6,6); tp=np.diagonal(cm,axis1=1,axis2=2); den=cm.sum(1)+cm.sum(2)
    return np.divide(2*tp,den,out=np.zeros_like(tp),where=den>0).mean(1)
def bootstrap():
    c=start('bootstrap'); d=pd.read_parquet(OUT/'scores/scored-visits.parquet')
    p=DSR/'comparisons/bootstrap-indices.npy'; checked(p,c['baseline_sha256'],'fixed-bootstrap-indices'); ix=np.load(p)
    p=DSR/'comparisons/content-order.parquet'; checked(p,c['baseline_sha256'],'fixed-content-order'); order=pd.read_parquet(p)
    current=d[['content_id','label_id']].drop_duplicates().sort_values(['label_id','content_id']).reset_index(drop=True)
    require(order.equals(current),'Bootstrap order exact'); counts=np.stack([np.bincount(row,minlength=30) for row in ix]); lookup=dict(zip(order.content_id,range(30)))
    dst=OUT/'comparisons'; dst.mkdir(parents=True,exist_ok=True); np.save(dst/'bootstrap-indices.npy',ix); save(order,dst/'content-order.parquet')
    summary=pd.read_parquet(OUT/'scores/protocol-summary.parquet').set_index(['protocol','arm']); arrays={}; exploratory=[]
    for proto in PROTOCOLS:
        for arm in ARMS:
            sub=d[(d.protocol==proto)&(d.arm==arm)].sort_values('visit_id')
            arrays[proto,arm]=bootstrap_f1(truths(sub),sub.prediction.to_numpy(int),counts[:,sub.content_id.map(lookup)])
        for ref in ARMS[1:4]:
            diff=arrays[proto,'RW4']-arrays[proto,ref]; lo,hi=np.quantile(diff,[.025,.975])
            exploratory.append({'protocol':proto,'reference':ref,'point':float(summary.loc[(proto,'RW4'),'F1']-summary.loc[(proto,ref),'F1']),
              'lo95':float(lo),'hi95':float(hi),'descriptive_not_main_family':True})
    mean={a:sum(arrays[p,a] for p in PROTOCOLS)/4 for a in ARMS}; records=[]
    for ref in ARMS[1:4]:
        diff=mean['RW4']-mean[ref]; lo,hi,flo,fhi=np.quantile(diff,[.025,.975,.05/6,1-.05/6])
        point=float(sum(summary.loc[(p,'RW4'),'F1']-summary.loc[(p,ref),'F1'] for p in PROTOCOLS)/4)
        records.append({'comparison':'RW4-'+ref,'point':point,'lo95':float(lo),'hi95':float(hi),
          'family_lower':float(flo),'family_upper':float(fhi),'family_positive':bool(flo>0),'family':3,
          'fixed_selected_models':True,'practical_vs_RW1':bool(point>=.01) if ref=='RW1' else False})
    save(pd.DataFrame(records),dst/'main-contrasts.parquet'); save(pd.DataFrame(exploratory),dst/'protocol-descriptive.parquet')
    complete(dst,samples=10000,family=3,conditional_no_refit=True)
    finish('RW22',main_comparisons=3,samples=10000); print(pd.DataFrame(records).to_string(index=False),flush=True)

def mechanism():
    c=start('mechanism'); dst=OUT/'diagnostics'; rows=[]
    for r in c['roles']:
        settings=RATIOS if r['inner'] is not None else sorted({v['setting'] for v in read(OUT/'selection/choices.json') if v['outer']==r['outer'] and v['protocol']==r['protocol'] and v['arm'] in ARMS[2:]})
        for ratio in settings:
            packs={}
            for arm in ARMS[2:]:
                path=folder('weights',r)/f'{arm}-r{ratio:g}.pt'
                if path.exists(): packs[arm]=artifact(path,'diagnostic-fixed-weights')
            for ref in ['RW2','RW3']:
                if 'RW4' not in packs or ref not in packs: continue
                a=packs['RW4']; b=packs[ref]; ga=a['gamma'][:,a['hard']] if a['hard'] is not None else torch.full_like(a['w'],.5)
                gb=b['gamma'][:,b['hard']] if b['hard'] is not None else torch.full_like(b['w'],.5)
                va=a['w']-a['w'].mean(); vb=b['w']-b['w'].mean(); den=float(va.norm()*vb.norm())
                rows.append({**{k:r[k] for k in ['outer','inner','protocol']},'reference':ref,'setting':ratio,
                  'gamma_hard_absolute_difference':float((ga-gb).abs().mean()),'soft_overlap':float(torch.minimum(ga,gb).mean()),
                  'weight_absolute_difference':float((a['w']-b['w']).abs().mean()),
                  'weight_correlation':float(torch.dot(va,vb))/den if den>0 else None})
    save(pd.DataFrame(rows),dst/'state-weight-overlap.parquet')
    # Match every candidate to RW0 on exactly the same held-out role; diagnostics never select r.
    pred=pd.read_parquet(OUT/'selection/inner-predictions.parquet'); base=pred[pred.arm=='RW0'].set_index(['outer','inner','protocol','visit_id'])
    cand=[]
    for (o,i,p,a,s),d in pred.groupby(['outer','inner','protocol','arm','setting']):
        other=base.loc[pd.MultiIndex.from_frame(d[['outer','inner','protocol','visit_id']])]
        cand.append({'outer':int(o),'inner':int(i),'protocol':p,'arm':a,'setting':float(s),
          'validation_prediction_changes':int((d.prediction.to_numpy()!=other.prediction.to_numpy()).sum()),
          'validation_probability_max_change':float(np.max(abs(d[[f'p{k}' for k in range(6)]].to_numpy()-other[[f'p{k}' for k in range(6)]].to_numpy())))})
    save(pd.DataFrame(cand),dst/'inner-candidate-changes.parquet'); finish('RW23-RW24',overlap_rows=len(rows),candidate_diagnostics=len(cand))

def offline():
    c=start('offline-fixed-states'); require((OUT/'predictions/complete.json').exists(),'All new predictions sealed first')
    p=DSR/'diagnostics/offline-test-states.parquet'; checked(p,c['baseline_sha256'],'offline-test-states-only-after-predictions')
    states=pd.read_parquet(p); d=pd.read_parquet(OUT/'scores/scored-visits.parquet').merge(states[['visit_id','low_mass','high_mass','d_true']],on='visit_id',validate='many_to_one')
    rows=[]
    for (proto,arm),sub in d.groupby(['protocol','arm']):
        y=truths(sub); probs=sub[[f'p{i}' for i in range(6)]].to_numpy(); z=probs.argmax(1)
        for name in ['low','high']:
            w=sub[name+'_mass'].to_numpy(); mass=float(w.sum()); cm=np.bincount(y*6+z,weights=w,minlength=36).reshape(6,6)
            den=cm.sum(0)+cm.sum(1); f=np.divide(2*np.diag(cm),den,out=np.zeros(6),where=den>0)
            rows.append({'protocol':proto,'arm':arm,'state':name,'mass':mass,'class_support':int((cm.sum(1)>0).sum()),
              'F1_descriptive':float(f.mean()) if (cm.sum(1)>0).all() else None,
              'CE':float((-np.log(probs[np.arange(len(y)),y])*w).sum()/mass) if mass>0 else None})
    save(states,OUT/'diagnostics/offline-test-states.parquet'); save(pd.DataFrame(rows),OUT/'diagnostics/fixed-test-state-summary.parquet')
    complete(OUT/'diagnostics',test_state_no_training_feedback=True); finish('RW25',states_reused_without_new_thresholds=True)
if __name__=='__main__': {'evaluate':evaluate,'bootstrap':bootstrap,'mechanism':mechanism,'offline':offline}[sys.argv[1]]()
