"""Confirmed fixed scalar14 sensitivity: 240 schemes 1/2 and 299 scheme 0."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path

import numpy as np
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import f1_score, balanced_accuracy_score, confusion_matrix

from .mechanism_contract import verify, read
from .business_conservative import match_training
from .business_splits import teacher_assignment, donors, disjoint
from .business_representations import matrix
from .privileged_learning import LinearStudent
from .teacher_diagnostics import probabilities_from_state
from .joint_teacher import array_digest, verify_complete
from .mechanism_report import clustered
from ..paired_information.prepare import table, digest
from ..reproducibility.preflight import write_json, write_table

ARMS=('M0','M1','M2','M3','J-True','J-Wrong')


def members(rows, assignment, context):
    c=context
    selected=[r for r in rows if c['task']=='six_business' or r['label_id'].startswith('youtube.com::')]
    available=[r for r in selected if r['protocol']==c['protocol'] and assignment[r['content_id']]!=c['outer_fold']]
    part=teacher_assignment(available,c['scheme'])
    train=match_training(available,part)
    test=[r for r in selected if r['protocol']==c['protocol'] and assignment[r['content_id']]==c['outer_fold']]
    target=[r for r in selected if r['protocol']!=c['protocol'] and assignment[r['content_id']]==c['outer_fold']]
    guard(train,test,target,c['protocol'])
    return available,train,test,target,part


def guard(train,test,target,source):
    disjoint(train,test); disjoint(train,target)
    if any(r['protocol']!=source for r in train+test) or any(r['protocol']==source for r in target):
        raise ValueError('Target deployment in training/source test')
    if {r['content_id'] for r in test}!={r['content_id'] for r in target}:
        raise ValueError('Cross-deployment test contents changed')


def row_ids(rows): return [r['session_id'] for r in rows]


def context_name(c):
    return f"{c['cohort']}-{c['task']}-{c['protocol']}-{c['outer_fold']}-scheme{c['scheme']}"


def run_one(dest,c,rows,assignment,cfg,business,root,old):
    available,train,test,target,part=members(rows,assignment,c)
    labels=sorted({r['label_id'] for r in train}); hard=np.eye(len(labels))[[labels.index(r['label_id']) for r in train]]
    pre=matrix(train,'pre','scalar14'); post=matrix(train,'post','scalar14')
    mapping=donors(train,part); fits=[]; teacher_oof=[]; predictions=[]; pair_maps=[]; splits=[]

    def fit(x,q,arm,member_rows,view,held=-1,donor_ids=None):
        model=LinearStudent(business).fit(x,q)
        record={'fit_id':f'{dest.name}:{len(fits)}', 'arm':arm,'held':held,'view':view,
            'train_ids':row_ids(member_rows),'donor_ids':donor_ids or [],'labels':labels,
            'x_sha256':array_digest(x),'targets':q.tolist(),'weight_sum':float(q.sum()),
            'state':model.state(),'fresh_fit':True}
        fits.append(record); return record

    def predict(record,selected,arm,stage):
        x=matrix(selected,'post','scalar14')
        p=probabilities_from_state(x,record['state'])
        for r,prob in zip(selected,p):
            truth=labels.index(r['label_id'])
            if stage=='student' and arm in ('M0','M1','M2','M3'):
                key=(c['task'],c['protocol'],c['outer_fold'],
                     (-1 if arm=='M0' else c['scheme']) if c['cohort']=='240' else c['scheme'],arm,r['session_id'])
                if np.max(np.abs(prob-np.asarray(old[key]['probabilities'])))>cfg['probability_tolerance']:
                    raise ValueError('Historical scalar sensitivity not reproduced')
            predictions.append({**c,'arm':arm,'stage':stage,'fit_id':record['fit_id'],
                'session_id':r['session_id'],'content_id':r['content_id'],'label_id':r['label_id'],
                'evaluation_protocol':r['protocol'],'truth':truth,'probabilities':prob.tolist(),
                'loss_bits':float(-np.log2(max(prob[truth],1e-12)))})

    if c['cohort']=='240':
        path=root/'jobs'/f"{c['task']}-{c['protocol']}-{c['outer_fold']}-scalar14"
        verify_complete(path)
        original=next(f for f in read(path/'fit-ledger.json') if f['arm']=='post')
        if original['train_ids']!=row_ids(train) or original['x_sha256']!=array_digest(post):
            raise ValueError('M0 reuse requires identical ordered training members/features')
        base={'fit_id':f'{dest.name}:M0-reused','arm':'M0','held':-1,'view':'post',
              'train_ids':row_ids(train),'donor_ids':[],'labels':labels,'x_sha256':array_digest(post),
              'targets':hard.tolist(),'weight_sum':float(hard.sum()),'state':original['state'],
              'fresh_fit':False,'source_fit_id':original['fit_id'],'source_ledger':str(path/'fit-ledger.json'),
              'source_ledger_sha256':digest(path/'fit-ledger.json')}
        fits.append(base)
    else: base=fit(post,hard,'M0',train,'post')
    predict(base,test,'M0','student'); predict(base,target,'M0','cross')
    q={name:np.zeros_like(hard) for name in ('pre','post','J-True','J-Wrong')}
    for held in (0,1):
        tr=[i for i,r in enumerate(train) if part[r['content_id']]!=held]
        va=[i for i,r in enumerate(train) if part[r['content_id']]==held]
        a,b=[train[i] for i in tr],[train[i] for i in va]
        disjoint(a,b,test); disjoint(a,b,target)
        for teacher in q:
            perm=np.arange(len(train)) if teacher=='J-True' else mapping
            if teacher in ('pre','post'):
                values=pre if teacher=='pre' else post
                x,xt=values[tr],values[va]; donor_ids=None
            else:
                x=np.concatenate([pre[perm[tr]],post[tr]],axis=1)
                xt=np.concatenate([pre[perm[va]],post[va]],axis=1)
                donor_ids=[train[perm[i]]['session_id'] for i in tr]
            f=fit(x,hard[tr],teacher+'_teacher',a,teacher,held,donor_ids)
            q[teacher][va]=probabilities_from_state(xt,f['state'])
            splits.append({'fit_id':f['fit_id'],'teacher':teacher,'held':held,
                'train_ids':row_ids(a),'holdout_ids':row_ids(b)})
            for i in va:
                teacher_oof.append({'fit_id':f['fit_id'],'teacher':teacher,'session_id':train[i]['session_id'],
                                    'probabilities':q[teacher][i].tolist()})
            if teacher in ('J-True','J-Wrong'):
                for role,indices in (('train',tr),('holdout',va)):
                    pair_maps.extend({'fit_id':f['fit_id'],'arm':teacher,'held':held,'role':role,
                        'receiver':train[i]['session_id'],'donor':train[perm[i]]['session_id']} for i in indices)
    pair_maps.extend({'fit_id':'pre_oof','arm':'M3','held':part[r['content_id']],'role':'student',
        'receiver':r['session_id'],'donor':train[mapping[i]]['session_id']} for i,r in enumerate(train))
    for arm,prob in [('M1',q['post']),('M2',q['pre']),('M3',q['pre'][mapping]),
                     ('J-True',q['J-True']),('J-Wrong',q['J-Wrong'])]:
        f=fit(post,.5*hard+.5*prob,arm,train,'post')
        predict(f,test,arm,'student'); predict(f,target,arm,'cross')
    write_json(dest/'membership.json',{'context':c,'available_ids':row_ids(available),'train_ids':row_ids(train),
        'test_ids':row_ids(test),'target_ids':row_ids(target),
        'excluded_train_ids':sorted(set(row_ids(available))-set(row_ids(train)))})
    write_json(dest/'fit-ledger.json',fits); write_json(dest/'teacher-splits.json',splits)
    write_table(dest/'teacher-oof.parquet',teacher_oof); write_table(dest/'pair-maps.parquet',pair_maps)
    write_table(dest/'predictions.parquet',predictions)
    write_json(dest/'complete.json',{'fresh_fits':sum(f['fresh_fit'] for f in fits),'reused_fits':sum(not f['fresh_fit'] for f in fits),
        'artifacts':{p.name:digest(p) for p in dest.iterdir() if p.is_file()}})


def load_inputs():
    cfg,business,source,root=verify()
    review=read(root/'delivery/next-sensitivity-review.json')
    allowed={r['session_id'] for r in table(source/'conservative-299/cohort.parquet')}
    all_rows=[r for r in table(source/'side-summaries.parquet') if r['selection']=='observed']
    cohorts={'240':[r for r in all_rows if r['primary_candidate']],
             '299':[r for r in all_rows if r['session_id'] in allowed]}
    if len(cohorts['240'])!=240 or len(cohorts['299'])!=299: raise ValueError('Wrong cohort counts')
    return cfg,business,source,root,review,cohorts,read(source/'learning/outer-splits.json')


def run():
    cfg,business,source,root,review,cohorts,assignment=load_inputs()
    out=root/'sensitivity'; out.mkdir(exist_ok=False)
    paths=[Path(__file__),root/'delivery/next-sensitivity-review.json',root/'training-complete.json',
           root/'report/validation.json',source/'conservative-299/cohort.parquet']
    write_json(out/'contract.json',{'approved':'user confirmed continuation; fixed 60 jobs/800 new fits',
        'sources':{str(p):digest(p) for p in paths},'jobs':review['jobs'],'alpha':.5,
        'representation':'scalar14','cohort_policy':'240_schemes_1_2; 299_scheme_0; no_MDN_recovered'})
    historical={}
    for cohort_id,directory in [('240',source/'learning'),('299',source/'conservative-299')]:
        verify_complete(directory)
        historical[cohort_id]={(r['task'],r['protocol'],r['outer_fold'],r['teacher_scheme'],r['arm'],r['session_id']):r
            for r in table(directory/'oof.parquet') if r['arm'] in ('M0','M1','M2','M3')}
    jobs=out/'jobs'; jobs.mkdir(); count=0; fresh=0; reused=0
    for planned in review['jobs']:
        c={k:planned[k] for k in ('cohort','task','protocol','outer_fold','scheme')}
        dest=jobs/context_name(c); dest.mkdir()
        try: run_one(dest,c,cohorts[c['cohort']],assignment,cfg,business,root,historical[c['cohort']])
        except Exception as exc:
            write_json(dest/'failed.json',{'context':c,'error':repr(exc),'action':'stop_no_retuning'})
            raise
        complete=verify_complete(dest); fresh+=complete['fresh_fits']; reused+=complete['reused_fits']; count+=1
        write_json(out/'progress.json',{'completed':count,'expected':60,'fresh_fits':fresh,'reused_M0':reused})
        print(json.dumps({'completed':count,'total':60,'fresh_fits':fresh}),flush=True)
    if fresh!=800 or reused!=40: raise ValueError('Confirmed fit budget mismatch')
    write_json(out/'complete.json',{'fresh_fits':fresh,'reused_M0':reused,'jobs':count,
        'job_hashes':{p.parent.name:digest(p) for p in jobs.glob('*/complete.json')}})


def audit_one(dest,rows,assignment,cfg):
    verify_complete(dest); lookup={r['session_id']:r for r in rows}
    membership=read(dest/'membership.json'); c=membership['context']
    available,train,test,target,part=members(rows,assignment,c)
    for key,expected in [('available_ids',available),('train_ids',train),('test_ids',test),('target_ids',target)]:
        if membership[key]!=row_ids(expected): raise ValueError('Frozen membership order changed')
    expected_train=set(row_ids(train)); labels=sorted({r['label_id'] for r in train})
    fits=read(dest/'fit-ledger.json'); by_id={f['fit_id']:f for f in fits}
    splits={r['fit_id']:r for r in read(dest/'teacher-splits.json')}
    if len(fits)!=14 or len(by_id)!=14 or len(splits)!=8: raise ValueError('Incomplete fit inventory')
    map_groups=defaultdict(list)
    maps=table(dest/'pair-maps.parquet')
    for m in maps:
        a,b=lookup[m['receiver']],lookup[m['donor']]
        if not {m['receiver'],m['donor']}<=expected_train: raise ValueError('Map outside source pool')
        if (a['label_id'],a['protocol'],a['repetition'],part[a['content_id']])!=(b['label_id'],b['protocol'],b['repetition'],part[b['content_id']]):
            raise ValueError('Mapping strata changed')
        if (m['arm']=='J-True' and m['receiver']!=m['donor']) or (m['arm']!='J-True' and a['content_id']==b['content_id']):
            raise ValueError('True/wrong mapping rule violated')
        map_groups[(m['fit_id'],m['role'])].append(m)
    for (fit_id,role),group in map_groups.items():
        ids=expected_train if role=='student' else set(splits[fit_id]['train_ids' if role=='train' else 'holdout_ids'])
        if len(group)!=len(ids) or {r['receiver'] for r in group}!=ids or {r['donor'] for r in group}!=ids:
            raise ValueError('Incomplete mapping bijection')
    q={}
    for r in table(dest/'teacher-oof.parquet'):
        f=by_id[r['fit_id']]; split=splits[f['fit_id']]; sid=r['session_id']; teacher=r['teacher']
        seen={x['session_id'] for x in train if part[x['content_id']]!=split['held']}
        hold=expected_train-seen
        if set(split['train_ids'])!=seen or set(split['holdout_ids'])!=hold or sid not in hold:
            raise ValueError('Teacher content exclusion failed')
        row=lookup[sid]
        if teacher in ('pre','post'): x=matrix([row],teacher,'scalar14')
        else:
            mp={m['receiver']:m['donor'] for m in map_groups[(f['fit_id'],'holdout')]}
            x=np.concatenate([matrix([lookup[mp[sid]]],'pre','scalar14'),matrix([row],'post','scalar14')],axis=1)
        p=probabilities_from_state(x,f['state'])[0]
        if (teacher,sid) in q or not np.allclose(p,r['probabilities'],atol=1e-10,rtol=0): raise ValueError('Invalid teacher OOF')
        q[(teacher,sid)]=p
    if len(q)!=4*len(train): raise ValueError('Teacher OOF coverage failed')
    cross={m['receiver']:m['donor'] for m in maps if m['arm']=='M3'}
    for f in fits:
        ids=f['train_ids']; fr=[lookup[s] for s in ids]
        if f['labels']!=labels or len(ids)!=len(set(ids)): raise ValueError('Fit classes/members')
        if f['fit_id'] in splits:
            if ids!=splits[f['fit_id']]['train_ids']: raise ValueError('Teacher fit pool')
        elif ids!=row_ids(train): raise ValueError('Student training pool changed')
        hard=np.eye(len(labels))[[labels.index(r['label_id']) for r in fr]]
        if f['view'] in ('J-True','J-Wrong'):
            mp={m['receiver']:m['donor'] for m in map_groups[(f['fit_id'],'train')]}
            if f['donor_ids']!=[mp[s] for s in ids]: raise ValueError('Donor order')
            x=np.concatenate([matrix([lookup[mp[s]] for s in ids],'pre','scalar14'),matrix(fr,'post','scalar14')],axis=1)
        else: x=matrix(fr,f['view'],'scalar14')
        if array_digest(x)!=f['x_sha256']: raise ValueError('Fit feature hash')
        target_q=hard
        if f['arm'] in ARMS[1:]:
            teacher={'M1':'post','M2':'pre','M3':'pre'}.get(f['arm'],f['arm'])
            probs=np.asarray([q[(teacher,cross[s] if f['arm']=='M3' else s)] for s in ids])
            target_q=.5*hard+.5*probs
        if not np.allclose(target_q,f['targets'],atol=1e-10,rtol=0) or not np.isclose(target_q.sum(),len(ids)):
            raise ValueError('Fit target/weight mismatch')
        imp=SimpleImputer(strategy='median',keep_empty_features=True).fit(x); scaler=StandardScaler().fit(imp.transform(x))
        for actual,saved in [(imp.statistics_,f['state']['imputer_statistics']),
                             (scaler.mean_,f['state']['scaler_mean']),(scaler.scale_,f['state']['scaler_scale'])]:
            if not np.allclose(actual,saved,atol=1e-12,rtol=0): raise ValueError('Non-source preprocessing')
        if not f['fresh_fit']:
            if digest(f['source_ledger'])!=f['source_ledger_sha256']: raise ValueError('Reused source changed')
            original=next(r for r in read(f['source_ledger']) if r['fit_id']==f['source_fit_id'])
            if original['state']!=f['state'] or original['train_ids']!=ids: raise ValueError('Incorrect M0 reuse')
    predictions=table(dest/'predictions.parquet'); groups=defaultdict(list)
    for r in predictions:
        if any(r[k]!=v for k,v in c.items()): raise ValueError('Prediction context mismatch')
        row=lookup[r['session_id']]; f=by_id[r['fit_id']]
        if f['arm']!=r['arm'] or r['session_id'] not in membership['target_ids' if r['stage']=='cross' else 'test_ids']:
            raise ValueError('Prediction model/membership mismatch')
        if r['truth']!=labels.index(row['label_id']) or r['evaluation_protocol']!=row['protocol']:
            raise ValueError('Prediction labels/deployment mismatch')
        p=probabilities_from_state(matrix([row],'post','scalar14'),f['state'])[0]
        if not np.allclose(p,r['probabilities'],atol=1e-10,rtol=0) or not np.isclose(r['loss_bits'],-np.log2(max(p[r['truth']],1e-12)),atol=1e-9):
            raise ValueError('Prediction reconstruction failed')
        groups[(r['stage'],r['arm'])].append(r)
    if set(groups)!={(s,a) for s in ('student','cross') for a in ARMS}: raise ValueError('Missing experimental arm')
    for (stage,arm),group in groups.items():
        ids=set(membership['target_ids' if stage=='cross' else 'test_ids'])
        if len(group)!=len(ids) or {r['session_id'] for r in group}!=ids: raise ValueError('Test coverage failed')
        if stage=='cross' and {r['fit_id'] for r in group}!={r['fit_id'] for r in groups[('student',arm)]}:
            raise ValueError('Cross-deployment model not reused')
    return predictions,len(maps)


def content_scores(rows):
    counts=Counter(r['content_id'] for r in rows); weights=np.asarray([1/counts[r['content_id']] for r in rows])
    p=np.asarray([r['probabilities'] for r in rows]); y=np.asarray([r['truth'] for r in rows]); pred=p.argmax(axis=1)
    return {'n':len(rows),'contents':len(counts),'log_loss_bits':float(np.average([r['loss_bits'] for r in rows],weights=weights)),
        'macro_f1':float(f1_score(y,pred,average='macro',sample_weight=weights)),
        'balanced_accuracy':float(balanced_accuracy_score(y,pred,sample_weight=weights)),
        'brier_multiclass':float(np.average(np.sum((p-np.eye(p.shape[1])[y])**2,axis=1),weights=weights)),
        'content_equal_confusion_matrix':confusion_matrix(y,pred,labels=np.arange(p.shape[1]),sample_weight=weights).tolist()}


def report():
    cfg,business,source,root,review,cohorts,assignment=load_inputs(); out=root/'sensitivity'
    contract=read(out/'contract.json')
    for name,expected in contract['sources'].items():
        if digest(name)!=expected: raise ValueError('Sensitivity frozen source changed')
    complete=read(out/'complete.json'); all_predictions=[]; maps=0
    if set(complete['job_hashes'])!={context_name(j) for j in contract['jobs']}: raise ValueError('Job inventory changed')
    for name,expected in complete['job_hashes'].items():
        dest=out/'jobs'/name
        if digest(dest/'complete.json')!=expected: raise ValueError('Job completion changed')
        c=read(dest/'membership.json')['context']
        p,n=audit_one(dest,cohorts[c['cohort']],assignment,cfg); all_predictions.extend(p); maps+=n
    groups=defaultdict(list); keys=('cohort','task','protocol','scheme','stage','arm')
    for r in all_predictions: groups[tuple(r[k] for k in keys)].append(r)
    metrics=[]; gains=[]; contents=[]; gaps=[]
    for key,rows in groups.items():
        if len(rows)!=len({r['session_id'] for r in rows}): raise ValueError('Duplicate OOF prediction')
        metrics.append(dict(zip(keys,key))|content_scores(rows))
        if key[-1] in ('M2','J-True'):
            for comparison,other_arm in [('G_task','M0'),('G_pair','M3' if key[-1]=='M2' else 'J-Wrong'),('G_soft','M1')]:
                other={r['session_id']:r for r in groups[(*key[:-1],other_arm)]}
                result,detail=clustered([(r['label_id'],r['content_id'],other[r['session_id']]['loss_bits']-r['loss_bits']) for r in rows],cfg)
                context=dict(zip(keys,key))|{'comparison':comparison}
                gains.append(context|result); contents.extend(context|d for d in detail)
        if key[-2]=='cross':
            source_rows=groups[(*key[:-2],'student',key[-1])]
            means={}
            for stage,items in [('source',source_rows),('target',rows)]:
                grouped=defaultdict(list)
                for r in items: grouped[(r['label_id'],r['content_id'])].append(r['loss_bits'])
                means[stage]={k:float(np.mean(v)) for k,v in grouped.items()}
            result,_=clustered([(label,cid,means['target'][(label,cid)]-value)
                for (label,cid),value in means['source'].items()],cfg)
            gaps.append(dict(zip(keys,key))|{'transfer_gap_bits':result['advantage_bits'],
                'round_policy':'each_content_valid_round_mean; 299 source/target round sets can differ'})
    dest=out/'report'; dest.mkdir(exist_ok=False)
    write_json(dest/'metrics.json',metrics); write_table(dest/'paired-gains.parquet',gains)
    write_table(dest/'content-effects.parquet',contents); write_json(dest/'transfer-gaps.json',gaps)
    write_table(dest/'predictions.parquet',all_predictions)
    write_json(dest/'validation.json',{'passed':True,'jobs':len(complete['job_hashes']),'fresh_fits':complete['fresh_fits'],
        'reused_M0':complete['reused_M0'],'prediction_rows':len(all_predictions),'pair_maps':maps,
        'target_fits':0,'source_preprocessing_and_soft_targets_reconstructed':True,
        'historical_M0_M1_M2_M3_reproduced':True,'weighting':'content_equal'})
    write_json(dest/'complete.json',{'artifacts':{p.name:digest(p) for p in dest.iterdir() if p.is_file()}})
    print(json.dumps(read(dest/'validation.json')),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--report',action='store_true'); args=p.parse_args()
    report() if args.report else run()
