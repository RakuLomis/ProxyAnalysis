"""Independent source-membership, soft-target, prediction audit and grouped reports."""
from collections import Counter, defaultdict
import json

import numpy as np

from .mechanism_contract import verify, cohort, read
from .business_representations import matrix, views
from .business_splits import teacher_assignment
from .joint_teacher import array_digest, verify_complete, source_guard
from .teacher_diagnostics import probabilities_from_state
from .privileged_learning import scores
from ..paired_information.prepare import table, digest
from ..reproducibility.preflight import write_json, write_table


def clustered(values, cfg):
    groups=defaultdict(list)
    for label,content,value in values: groups[(label,content)].append(value)
    by_label=defaultdict(list); content_rows=[]
    for (label,content),v in sorted(groups.items()):
        mean=float(np.mean(v)); by_label[label].append(mean)
        content_rows.append({'label_id':label,'content_id':content,'advantage_bits':mean})
    if any(len(v)!=5 for v in by_label.values()): raise ValueError('Incomplete content coverage')
    a=np.asarray(list(by_label.values())); rng=np.random.default_rng(cfg['seed'])
    indices=rng.integers(0,5,size=(cfg['bootstrap_repetitions'],len(a),5))
    bs=a[np.arange(len(a))[None,:,None],indices].mean(axis=(1,2))
    return {'advantage_bits':float(a.mean()),'conditional_ci_low':float(np.quantile(bs,.025)),
            'conditional_ci_high':float(np.quantile(bs,.975)),'positive_contents':int((a>0).sum()),
            'contents':int(a.size),'interval_scope':'class_stratified_content_bootstrap_conditional_on_fitted_models'},content_rows


def audit_job(dest, lookup, assignment, cfg):
    verify_complete(dest)
    member=read(dest/'membership.json'); c=member['context']; task=c['task']; protocol=c['protocol']; fold=c['outer_fold']
    rep=c['representation']; labels=sorted({r['label_id'] for r in lookup.values()
        if task=='six_business' or r['label_id'].startswith('youtube.com::')})
    eligible=[r for r in lookup.values() if r['label_id'] in labels]
    expected={
        'train_ids':{r['session_id'] for r in eligible if r['protocol']==protocol and assignment[r['content_id']]!=fold},
        'test_ids':{r['session_id'] for r in eligible if r['protocol']==protocol and assignment[r['content_id']]==fold},
        'target_ids':{r['session_id'] for r in eligible if r['protocol']!=protocol and assignment[r['content_id']]==fold}}
    for key, ids in expected.items():
        if len(member[key])!=len(ids) or set(member[key])!=ids: raise ValueError('Job membership changed')
    train=[lookup[s] for s in member['train_ids']]
    source_guard(train,[lookup[s] for s in member['test_ids']],[lookup[s] for s in member['target_ids']],protocol)
    partition=teacher_assignment(train,0)
    fits=read(dest/'fit-ledger.json'); fit_lookup={f['fit_id']:f for f in fits}
    if len(fits)!=28 or len(fit_lookup)!=28: raise ValueError('Expected four views/eight teachers/sixteen students')
    splits={s['fit_id']:s for s in read(dest/'teacher-splits.json')}
    maps=table(dest/'pair-maps.parquet'); map_groups=defaultdict(list)
    for m in maps:
        a,b=lookup[m['receiver']],lookup[m['donor']]
        if m['receiver'] not in expected['train_ids'] or m['donor'] not in expected['train_ids']:
            raise ValueError('Mapping contains outside member')
        if (a['label_id'],a['protocol'],a['repetition'],partition[a['content_id']])!=(b['label_id'],b['protocol'],b['repetition'],partition[b['content_id']]):
            raise ValueError('Wrong mapping strata')
        if m['arm']=='J-True':
            if m['receiver']!=m['donor']: raise ValueError('True map changed')
        elif a['content_id']==b['content_id']: raise ValueError('Wrong map not cross-content')
        map_groups[(m['teacher_fit_id'],m['role'])].append(m)
    for (fit_id,role), group in map_groups.items():
        ids=expected['train_ids'] if role=='student' else set(splits[fit_id][role+'_ids' if role=='train' else 'holdout_ids'])
        if len(group)!=len(ids) or {m['receiver'] for m in group}!=ids or {m['donor'] for m in group}!=ids:
            raise ValueError('Mapping not a complete bijection')
    teacher_outputs=table(dest/'teacher-oof.parquet'); q={}; oof_seen=Counter()
    for record in teacher_outputs:
        f=fit_lookup[record['fit_id']]; split=splits[f['fit_id']]; sid=record['session_id']
        expected_train={r['session_id'] for r in train if partition[r['content_id']]!=split['held']}
        expected_hold=expected['train_ids']-expected_train
        if set(split['train_ids'])!=expected_train or set(split['holdout_ids'])!=expected_hold:
            raise ValueError('Teacher split mismatch')
        if sid not in expected_hold: raise ValueError('Teacher OOF membership')
        row=lookup[sid]; teacher=record['teacher']
        if teacher in ('pre','post'): x=matrix([row],teacher,rep)
        else:
            mapping={m['receiver']:m['donor'] for m in map_groups[(f['fit_id'],'holdout')]}
            x=np.concatenate([matrix([lookup[mapping[sid]]],'pre',rep),matrix([row],'post',rep)],axis=1)
        p=probabilities_from_state(x,f['state'])[0]
        if np.max(np.abs(p-np.asarray(record['probabilities'])))>cfg['probability_tolerance']:
            raise ValueError('Teacher OOF reconstruction failed')
        q[(teacher,sid)]=p; oof_seen[(teacher,sid)]+=1
    if len(q)!=4*len(train) or set(oof_seen.values())!={1}: raise ValueError('Teacher OOF coverage')
    cross_map={m['receiver']:m['donor'] for m in maps if m['arm']=='M3'}
    for f in fits:
        ids=f['train_ids']; fr=[lookup[s] for s in ids]
        if len(ids)!=len(set(ids)) or not set(ids)<=expected['train_ids'] or f['labels']!=labels:
            raise ValueError('Fit training pool or class mapping changed')
        if f['fit_id'] in splits:
            if ids!=splits[f['fit_id']]['train_ids']: raise ValueError('Teacher fit members changed')
        elif ids!=member['train_ids']: raise ValueError('Student/view pool changed')
        hard=np.eye(len(labels))[[labels.index(r['label_id']) for r in fr]]
        if f['input_view'] in ('J-True','J-Wrong'):
            m={r['receiver']:r['donor'] for r in map_groups[(f['fit_id'],'train')]}
            if [m[s] for s in ids]!=f['donor_ids']: raise ValueError('Fit donor ordering mismatch')
            x=np.concatenate([matrix([lookup[m[s]] for s in ids],'pre',rep),matrix(fr,'post',rep)],axis=1)
        else: x=views(fr,rep)[f['input_view']]
        if array_digest(x)!=f['x_sha256'] or x.shape[1]!=f['n_features']: raise ValueError('Fit input mismatch')
        target=hard
        arm=f['arm']; alpha=f['alpha']
        if arm in ('M1','M2','M3','J-True','J-Wrong'):
            teacher={'M1':'post','M2':'pre','M3':'pre'}.get(arm,arm)
            prob=np.asarray([q[(teacher,cross_map[s] if arm=='M3' else s)] for s in ids])
            target=(1-alpha)*hard+alpha*prob
        elif arm=='LS10': target=.9*hard+.1/len(labels)
        if not np.allclose(target,f['targets'],atol=cfg['probability_tolerance'],rtol=0):
            raise ValueError('Student soft targets differ from audited OOF')
        if not np.isclose(np.sum(f['targets']),len(ids)): raise ValueError('Fit weight mismatch')
        # Refit only preprocessing independently, not a classifier, to exclude target-contaminated statistics.
        from sklearn.impute import SimpleImputer
        from sklearn.preprocessing import StandardScaler
        imp=SimpleImputer(strategy='median',keep_empty_features=True).fit(x)
        scaler=StandardScaler().fit(imp.transform(x))
        for a,b in [(imp.statistics_,f['state']['imputer_statistics']),
                    (scaler.mean_,f['state']['scaler_mean']),(scaler.scale_,f['state']['scaler_scale'])]:
            if not np.allclose(a,b,atol=1e-12,rtol=0): raise ValueError('Non-source preprocessing detected')
    predictions=table(dest/'predictions.parquet'); prediction_groups=defaultdict(list)
    for r in predictions:
        if any(r[k]!=v for k,v in c.items()): raise ValueError('Prediction context changed')
        row=lookup[r['session_id']]; f=fit_lookup[r['fit_id']]
        ids=expected['target_ids'] if r['stage']=='cross' else expected['test_ids']
        if r['session_id'] not in ids or r['truth']!=labels.index(row['label_id']) or r['evaluation_protocol']!=row['protocol']:
            raise ValueError('Prediction test membership/label')
        x=matrix([row],'post',rep) if r['stage']!='view' else views([row],rep)[r['arm']]
        p=probabilities_from_state(x,f['state'])[0]
        if not np.allclose(p,r['probabilities'],atol=cfg['probability_tolerance'],rtol=0):
            raise ValueError('Prediction reconstruction failed')
        if not np.isclose(r['loss_bits'],-np.log2(max(p[r['truth']],1e-12)),atol=1e-9): raise ValueError('Loss changed')
        prediction_groups[(r['stage'],r['arm'],r['alpha'])].append(r)
    student_arms=[('M0',0.),('LS10',.1)]+[(arm,alpha) for arm in ('M1','M2','M3','J-True','J-Wrong') for alpha in cfg['alphas']]
    expected_keys={('view',a,-1.) for a in ('pre','post','joint','transformation')}|{
        (stage,a,alpha) for stage in ('student','cross') for a,alpha in student_arms}
    if set(prediction_groups)!=expected_keys: raise ValueError('Missing planned arm')
    for (stage,arm,alpha),group in prediction_groups.items():
        ids=expected['target_ids'] if stage=='cross' else expected['test_ids']
        if len(group)!=len(ids) or {r['session_id'] for r in group}!=ids: raise ValueError('Prediction coverage')
        if stage=='cross':
            original=prediction_groups[('student',arm,alpha)]
            if {r['fit_id'] for r in group}!={r['fit_id'] for r in original}: raise ValueError('Target model not reused')
    return predictions, len(fits), len(maps)


def main():
    cfg,business,source,out=verify()
    complete=read(out/'training-complete.json')
    rows=cohort(source); lookup={r['session_id']:r for r in rows}
    assignment=read(source/'learning/outer-splits.json')
    all_predictions=[]; total_fits=0; total_maps=0
    for name,expected in complete['job_complete_hashes'].items():
        dest=out/'jobs'/name
        if digest(dest/'complete.json')!=expected: raise ValueError('Job completion changed')
        preds,fits,maps=audit_job(dest,lookup,assignment,cfg)
        all_predictions.extend(preds); total_fits+=fits; total_maps+=maps
    if len(complete['job_complete_hashes'])!=40 or total_fits!=1120: raise ValueError('Planned job count mismatch')
    dest=out/'report'; dest.mkdir(exist_ok=False)
    groups=defaultdict(list)
    for r in all_predictions:
        groups[(r['task'],r['protocol'],r['representation'],r['stage'],r['arm'],r['alpha'])].append(r)
    metrics=[]; gains=[]; content_rows=[]
    names=('task','protocol','representation','stage','arm','alpha')
    for key,group in groups.items():
        counts=Counter(r['content_id'] for r in group)
        if set(counts.values())!={4} or len(group)!=len({r['session_id'] for r in group}): raise ValueError('Unbalanced OOF or duplicates')
        metrics.append(dict(zip(names,key))|scores([r['truth'] for r in group],[r['probabilities'] for r in group]))
    def contrast(key,other_key,comparison):
        a=groups[key]; b={r['session_id']:r for r in groups[other_key]}
        values=[(r['label_id'],r['content_id'],b[r['session_id']]['loss_bits']-r['loss_bits']) for r in a]
        summary,detail=clustered(values,cfg)
        context=dict(zip(names,key))|{'comparison':comparison,'reference_arm':other_key[4]}
        gains.append(context|summary); content_rows.extend(context|r for r in detail)
    for key in groups:
        task,protocol,rep,stage,arm,alpha=key
        prefix=(task,protocol,rep,stage)
        if stage=='view' and arm!='post': contrast(key,(*prefix,'post',-1.),'view_vs_post')
        if stage in ('student','cross') and arm in ('M2','J-True'):
            for name,other,weight in [('G_task','M0',0.),('G_pair','M3' if arm=='M2' else 'J-Wrong',alpha),
                                      ('G_soft','M1',alpha),('vs_LS10','LS10',.1)]:
                contrast(key,(*prefix,other,weight),name)
            if arm=='J-True': contrast(key,(*prefix,'M2',alpha),'vs_pre_teacher')
    gaps=[]
    for key,group in groups.items():
        if key[3]!='cross': continue
        source_key=(*key[:3],'student',*key[4:])
        src={(r['content_id'],lookup[r['session_id']]['repetition']):r for r in groups[source_key]}
        values=[(r['label_id'],r['content_id'],r['loss_bits']-src[(r['content_id'],lookup[r['session_id']]['repetition'])]['loss_bits']) for r in group]
        summary,_=clustered(values,cfg)
        gaps.append(dict(zip(names,key))|{'target_protocol':group[0]['evaluation_protocol'],
            'transfer_gap_bits':summary.pop('advantage_bits'),**summary})
    gap_lookup={(r['task'],r['protocol'],r['representation'],r['arm'],r['alpha']):r for r in gaps}
    for r in gaps:
        baseline=gap_lookup[(r['task'],r['protocol'],r['representation'],'M0',0.)]
        r['gap_reduction_vs_M0_descriptive']=baseline['transfer_gap_bits']-r['transfer_gap_bits']
    write_json(dest/'metrics.json',metrics); write_table(dest/'paired-gains.parquet',gains)
    write_table(dest/'content-effects.parquet',content_rows); write_json(dest/'transfer-gaps.json',gaps)
    write_table(dest/'all-predictions.parquet',all_predictions)
    for stage,dirname in [('view','p1-view-comparison'),('student','p2-joint-teacher'),('cross','p3-cross-deployment')]:
        folder=out/dirname; folder.mkdir(exist_ok=False)
        write_json(folder/'metrics.json',[r for r in metrics if r['stage']==stage])
        write_table(folder/'predictions.parquet',[r for r in all_predictions if r['stage']==stage])
        write_table(folder/'gains.parquet',[r for r in gains if r['stage']==stage])
    write_json(dest/'validation.json',{'passed':True,'audited_fits':total_fits,'audited_pair_maps':total_maps,
        'prediction_rows':len(all_predictions),'target_fits':0,'source_only_preprocessing_verified':True,
        'soft_targets_reconstructed':True,'historical_scalar_baselines_reproduced':True})
    write_json(dest/'complete.json',{'artifacts':{p.name:digest(p) for p in dest.iterdir() if p.is_file()}})
    print(json.dumps({'audit':'passed','fits':total_fits,'predictions':len(all_predictions),
        'main_gains':[r for r in gains if r['representation']=='scalar14' and r['alpha']==.5 and r['comparison'] in ('G_task','G_pair')]}),flush=True)


if __name__=='__main__': main()
