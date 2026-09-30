"""P0: contextual OOF diagnostics and real-input soft-target equivalence."""
from collections import defaultdict
import json

import numpy as np
from scipy.special import expit, softmax
from sklearn.linear_model import LogisticRegression

from .mechanism_contract import verify, cohort, read
from .privileged_learning import LinearStudent, matrix, scores
from ..paired_information.prepare import table, digest
from ..reproducibility.preflight import write_json, write_table


def probabilities_from_state(x, state):
    z = np.asarray(x,dtype=float).copy()
    z = np.where(np.isnan(z),np.asarray(state['imputer_statistics']),z)
    z = (z-np.asarray(state['scaler_mean']))/np.asarray(state['scaler_scale'])
    logits = z@np.asarray(state['coef']).T+np.asarray(state['intercept'])
    if logits.shape[1]==1:
        p=expit(logits[:,0]); return np.column_stack([1-p,p])
    return softmax(logits,axis=1)


def main():
    cfg,business,source,out = verify()
    dest=out/'p0-diagnostics'; dest.mkdir(exist_ok=False)
    rows=cohort(source); lookup={r['session_id']:r for r in rows}
    assignment=read(source/'learning/outer-splits.json')
    teacher_rows=table(source/'learning/teacher-oof.parquet')
    splits={(s['task'],s['protocol'],s['outer_fold'],s['scheme'],s['teacher_holdout']):s
            for s in read(source/'learning/teacher-splits.json')}
    detail=[]; grouped=defaultdict(list); content_groups=defaultdict(list)
    for t in teacher_rows:
        r=lookup[t['session_id']]
        labels=sorted({v['label_id'] for v in rows if t['task']=='six_business' or v['label_id'].startswith('youtube.com::')})
        y=labels.index(r['label_id'])
        split=splits[(t['task'],t['protocol'],t['outer_fold'],t['scheme'],t['teacher_holdout'])]
        training_contents=sorted({lookup[s]['content_id'] for s in split['train_ids']})
        if r['content_id'] in training_contents or r['session_id'] not in split['holdout_ids']:
            raise ValueError('Teacher OOF exclusion failed')
        for side in ('pre','post'):
            p=np.asarray(t[side+'_probabilities']); positive=p[p>0]
            record={k:t[k] for k in ('task','protocol','outer_fold','scheme','teacher_holdout','session_id')}
            record.update(content_id=r['content_id'],label_id=r['label_id'],side=side,truth=y,
                probabilities=p.tolist(),loss_bits=float(-np.log2(max(p[y],1e-12))),
                true_probability=float(p[y]),entropy_bits=float(-np.sum(positive*np.log2(positive))),
                brier=float(np.sum((p-np.eye(len(p))[y])**2)),
                true_margin=float(p[y]-np.max(np.delete(p,y))),teacher_training_contents=training_contents)
            detail.append(record)
            key=(t['task'],t['protocol'],t['outer_fold'],t['scheme'],side)
            grouped[key].append(record); content_groups[(*key,r['content_id'])].append(record)
    summary=[]; content=[]
    for key, group in grouped.items():
        summary.append(dict(zip(('task','protocol','outer_fold','scheme','side'),key))|
            scores([r['truth'] for r in group],[r['probabilities'] for r in group])|
            {'mean_true_probability':float(np.mean([r['true_probability'] for r in group])),
             'mean_entropy_bits':float(np.mean([r['entropy_bits'] for r in group]))})
    for key,group in content_groups.items():
        content.append(dict(zip(('task','protocol','outer_fold','scheme','side','content_id'),key))|
            {'label_id':group[0]['label_id'],'n':len(group),
             **{name:float(np.mean([r[name] for r in group])) for name in
                ('loss_bits','true_probability','entropy_bits','brier','true_margin')}})
    predictions=table(source/'learning/oof.parquet'); pg=defaultdict(dict)
    for p in predictions:
        if p['arm'] in ('M0','M1','M2','M3'):
            pg[(p['task'],p['protocol'],p['outer_fold'],p['teacher_scheme'],p['arm'])][p['session_id']]=p
    effects=[]; contexts=[]
    for key, base in pg.items():
        task,protocol,fold,scheme,arm=key
        if arm!='M0': continue
        for s in business['teacher_schemes']:
            for comparison,other_arm in [('M2_minus_M0','M2'),('M1_minus_M0','M1'),('M3_minus_M2','M3')]:
                target=pg[(task,protocol,fold,s,other_arm)]
                ref=base if other_arm!='M3' else pg[(task,protocol,fold,s,'M2')]
                by_content=defaultdict(list)
                for sid,p in target.items():
                    by_content[p['content_id']].append(p['loss_bits']-ref[sid]['loss_bits'])
                for cid,values in by_content.items():
                    effects.append({'task':task,'protocol':protocol,'outer_fold':fold,'scheme':s,
                        'comparison':comparison,'content_id':cid,'difference_bits':float(np.mean(values))})
                contexts.append({'task':task,'protocol':protocol,'outer_fold':fold,'scheme':s,
                    'comparison':comparison,'heldout_difference_bits':float(np.mean([np.mean(v) for v in by_content.values()])),
                    **{side+'_training_oof_ce':float(np.mean([r['loss_bits'] for r in grouped[(task,protocol,fold,s,side)]]))
                       for side in ('pre','post')},'interpretation':'different_train_and_test_members; descriptive_five_fold_contexts_only'})
    sanity=[]; fits=0; tolerance=cfg['probability_tolerance']
    for task in ('six_business','youtube_activity'):
        for protocol in business['protocols']:
            selected=[r for r in rows if r['protocol']==protocol and (task=='six_business' or r['label_id'].startswith('youtube.com::'))]
            labels=sorted({r['label_id'] for r in selected})
            train=[r for r in selected if assignment[r['content_id']]!=0]
            test=[r for r in selected if assignment[r['content_id']]==0]
            y=np.asarray([labels.index(r['label_id']) for r in train]); hard=np.eye(len(labels))[y]
            x,xt=matrix(train,'post'),matrix(test,'post')
            base=LinearStudent(business).fit(x,hard); fits+=1
            ref=LogisticRegression(C=business['model_C'],max_iter=business['max_iter'],random_state=business['seed']).fit(base.preprocess.transform(x),y); fits+=1
            tests={'direct_hard':ref.predict_proba(base.preprocess.transform(xt))}
            q=np.full_like(hard,1/len(labels))
            for name,target in [('alpha_zero',(1-0)*hard+0*q),('teacher_onehot',.5*hard+.5*hard)]:
                tests[name]=LinearStudent(business).fit(x,target).predict(xt); fits+=1
            p=base.predict(xt)
            old=pg[(task,protocol,0,-1,'M0')]
            tests['historical_M0']=np.asarray([old[r['session_id']]['probabilities'] for r in test])
            tests['state_reconstruction']=probabilities_from_state(xt,base.state())
            differences={name:float(np.max(np.abs(p-v))) for name,v in tests.items()}
            if max(differences.values())>tolerance: raise ValueError(f'Soft target equivalence failed: {differences}')
            soft=.5*hard+.5*q
            if not np.allclose(soft.sum(axis=1),1) or not np.isclose(soft.sum(),len(train)):
                raise ValueError('Soft target weight conservation failed')
            sanity.append({'task':task,'protocol':protocol,'n':len(train),'weight_sum':float(soft.sum()),
                           'maximum_probability_differences':differences})
    write_table(dest/'teacher-oof-diagnostics.parquet',detail)
    write_table(dest/'teacher-content-summary.parquet',content)
    write_json(dest/'teacher-summary.json',summary)
    write_table(dest/'student-content-effects.parquet',effects)
    write_table(dest/'teacher-student-contexts.parquet',contexts)
    write_json(dest/'soft-target-sanity.json',{'passed':True,'tolerance':tolerance,'fresh_fits':fits,'checks':sanity})
    write_json(dest/'complete.json',{'passed':True,'fresh_fits':fits,'teacher_records':len(detail),
        'artifacts':{p.name:digest(p) for p in dest.iterdir() if p.is_file()}})
    print(json.dumps({'P0':'passed','fresh_fits':fits,'teacher_records':len(detail)}),flush=True)


if __name__=='__main__': main()
