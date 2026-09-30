"""299-session conservative sensitivity with matched training rounds in all arms."""
from collections import Counter, defaultdict
import json
from pathlib import Path

import numpy as np
from sklearn.metrics import balanced_accuracy_score, f1_score

from ..paired_information.prepare import table, digest
from ..reproducibility.preflight import write_json, write_table
from .business_features import load_config, verify
from .business_splits import outer_assignment, teacher_assignment, disjoint, donors
from .privileged_learning import LinearStudent, matrix, scores


def match_training(rows, partition):
    groups=defaultdict(lambda: defaultdict(set))
    for r in rows:
        groups[(r['label_id'],r['protocol'],partition[r['content_id']])][r['content_id']].add(r['repetition'])
    keep=set()
    for (label,protocol,held),contents in groups.items():
        if len(contents)!=2: raise ValueError('Two teacher holdout contents per class required')
        common=set.intersection(*contents.values())
        if len(common)<4: raise ValueError('Matching lost too many repetitions; needs review')
        keep.update(r['session_id'] for r in rows if r['label_id']==label and r['protocol']==protocol
                    and partition[r['content_id']]==held and r['repetition'] in common)
    matched=[r for r in rows if r['session_id'] in keep]
    if len(keep)!=len(matched): raise ValueError('Duplicate training session')
    donors(matched,partition)  # Must actually admit the unchanged cross-content bijection.
    return matched


def run():
    cfg=load_config(); verify(cfg); root=Path(cfg['output_root'])
    gate=json.loads((root/'identity-gate.json').read_text(encoding='utf-8'))
    if not gate['passed']: raise ValueError('Identity gate failed')
    for name,expected in gate['source_hashes'].items():
        if digest(root/name)!=expected: raise ValueError('Audited source changed')
    candidates=table(root/'candidates.parquet')
    allowed={r['session_id'] for r in candidates if r['effective_label_valid']}
    rows=[r for r in table(root/'side-summaries.parquet') if r['selection']=='observed' and r['session_id'] in allowed]
    if len(rows)!=299 or len(allowed)!=299: raise ValueError('Conservative membership changed')
    assignment=outer_assignment(rows,cfg['seed'])
    if assignment!=json.loads((root/'learning/outer-splits.json').read_text(encoding='utf-8')):
        raise ValueError('Original outer content assignment changed')
    proposal=json.loads((root/'report/299-sensitivity-proposal.json').read_text(encoding='utf-8'))
    proposed={(r['task'],r['protocol'],r['outer_fold'],r['scheme']):r for r in proposal}
    out=root/'conservative-299'; out.mkdir(exist_ok=False)
    write_json(out/'contract.json',{'config':cfg,'candidate_count':299,'primary_240_unchanged':True,
        'degraded_policy':'preserve_existing_activity_policy; omit_one_MDN_recovered_session_only',
        'matching':'same_class_protocol_round_and_teacher_holdout; train_all_arms_on_same_matched_pool',
        'within_content_control':'not_repeated_in_this_sensitivity',
        'metric_weighting':'content_equal_primary; sample_pooled_secondary',
        'sources':{str(root/name):digest(root/name) for name in ['candidates.parquet','side-summaries.parquet','identity-gate.json','report/299-sensitivity-proposal.json']},
        'code_hashes':{str(p):digest(p) for p in Path(__file__).parent.glob('*.py')}})
    write_table(out/'cohort.parquet',[{k:r[k] for k in ('session_id','content_id','label_id','protocol','repetition')} for r in rows])
    write_json(out/'excluded-candidates.json',[r for r in candidates if r['session_id'] not in allowed])
    predictions=[]; teacher_outputs=[]; mappings=[]; splits=[]; fits=[]; membership=[]; hard_cache={}
    def fit(x,q,metadata):
        model=LinearStudent(cfg).fit(x,q)
        fits.append({**metadata,'state':model.state()}); return model
    for task in ('six_business','youtube_activity'):
        for protocol in cfg['protocols']:
            selected=[r for r in rows if r['protocol']==protocol and (task=='six_business' or r['label_id'].startswith('youtube.com::'))]
            labels=sorted({r['label_id'] for r in selected}); k=len(labels)
            for fold in range(5):
                available=[r for r in selected if assignment[r['content_id']]!=fold]
                test=[r for r in selected if assignment[r['content_id']]==fold]
                for scheme in cfg['teacher_schemes']:
                    partition=teacher_assignment(available,scheme); train=match_training(available,partition)
                    disjoint(train,test)
                    excluded=sorted({r['session_id'] for r in available}-{r['session_id'] for r in train})
                    planned=proposed[(task,protocol,fold,scheme)]
                    if len(train)!=planned['matched_train'] or excluded!=sorted(planned['excluded_ids']) or len(test)!=planned['available_test']:
                        raise ValueError('Frozen sensitivity proposal mismatch')
                    context={'task':task,'protocol':protocol,'outer_fold':fold,'teacher_scheme':scheme}
                    ids=tuple(r['session_id'] for r in train)
                    membership.append({**context,'train_ids':list(ids),'test_ids':[r['session_id'] for r in test],
                                       'excluded_train_ids':excluded})
                    hard=np.eye(k)[[labels.index(r['label_id']) for r in train]]
                    q={side:np.zeros((len(train),k)) for side in ('pre','post')}
                    for held in (0,1):
                        tr=[i for i,r in enumerate(train) if partition[r['content_id']]!=held]
                        va=[i for i,r in enumerate(train) if partition[r['content_id']]==held]
                        a,b=[train[i] for i in tr],[train[i] for i in va]; disjoint(a,b,test)
                        splits.append({**context,'held':held,'train_ids':[r['session_id'] for r in a],
                                       'holdout_ids':[r['session_id'] for r in b]})
                        for side in ('pre','post'):
                            teacher=fit(matrix(a,side),hard[tr],{**context,'arm':side+'_teacher_oof','held':held})
                            q[side][va]=teacher.predict(matrix(b,side))
                    teacher_outputs.extend({**context,'session_id':r['session_id'],
                        'pre_probabilities':q['pre'][i].tolist(),'post_probabilities':q['post'][i].tolist()}
                        for i,r in enumerate(train))
                    cross=donors(train,partition)
                    arms=[('M0',hard,None,'post'),('M1',(1-cfg['alpha'])*hard+cfg['alpha']*q['post'],None,'post'),
                          ('M2',(1-cfg['alpha'])*hard+cfg['alpha']*q['pre'],np.arange(len(train)),'post'),
                          ('M3',(1-cfg['alpha'])*hard+cfg['alpha']*q['pre'][cross],cross,'post'),
                          ('pre_teacher_diagnostic',hard,None,'pre')]
                    for arm,target,mapping,side in arms:
                        cache_key=(task,protocol,fold,arm,ids)
                        if arm in ('M0','pre_teacher_diagnostic') and cache_key in hard_cache:
                            model=hard_cache[cache_key]
                        else:
                            model=fit(matrix(train,side),target,{**context,'arm':arm})
                            if arm in ('M0','pre_teacher_diagnostic'): hard_cache[cache_key]=model
                        probabilities=model.predict(matrix(test,side))
                        for r,p in zip(test,probabilities):
                            truth=labels.index(r['label_id'])
                            predictions.append({**context,'arm':arm,'session_id':r['session_id'],
                                'content_id':r['content_id'],'label_id':r['label_id'],'truth':truth,
                                'probabilities':p.tolist(),'loss_bits':float(-np.log2(max(p[truth],1e-12)))})
                        if mapping is not None:
                            mappings.extend({**context,'arm':arm,'receiver':r['session_id'],
                                'donor':train[mapping[i]]['session_id'],'held':partition[r['content_id']]}
                                for i,r in enumerate(train))
                print(json.dumps({'task':task,'protocol':protocol,'fold':fold,'fresh_fits':len(fits)}),flush=True)
    write_table(out/'oof.parquet',predictions); write_table(out/'teacher-oof.parquet',teacher_outputs)
    write_table(out/'pair-maps.parquet',mappings); write_json(out/'teacher-splits.json',splits)
    write_json(out/'student-membership.json',membership); write_json(out/'fit-ledger.json',fits)
    write_json(out/'complete.json',{'fresh_fits':len(fits),'prediction_rows':len(predictions),
        'artifacts':{name:digest(out/name) for name in ['oof.parquet','teacher-oof.parquet','pair-maps.parquet','teacher-splits.json','student-membership.json','fit-ledger.json']}})


def report():
    cfg=load_config(); root=Path(cfg['output_root']); out=root/'conservative-299'
    complete=json.loads((out/'complete.json').read_text(encoding='utf-8'))
    for name,expected in complete['artifacts'].items():
        if digest(out/name)!=expected: raise ValueError('Result changed')
    lookup={r['session_id']:r for r in table(out/'cohort.parquet')}; assignment=outer_assignment(list(lookup.values()),cfg['seed'])
    memberships=json.loads((out/'student-membership.json').read_text(encoding='utf-8'))
    key=lambda r:(r['task'],r['protocol'],r['outer_fold'],r['teacher_scheme'])
    membership={key(r):r for r in memberships}
    splits={(*key(r),r['held']):r for r in json.loads((out/'teacher-splits.json').read_text(encoding='utf-8'))}
    grouped_maps=defaultdict(list)
    maps=table(out/'pair-maps.parquet')
    for m in maps:
        a,b=lookup[m['receiver']],lookup[m['donor']]; split=splits[(*key(m),m['held'])]
        if m['receiver'] not in split['holdout_ids'] or m['donor'] not in split['holdout_ids']: raise ValueError('Donor crossed teacher fold')
        seen={lookup[s]['content_id'] for s in split['train_ids']}
        if a['content_id'] in seen or b['content_id'] in seen: raise ValueError('Teacher saw paired content')
        if m['receiver'] not in membership[key(m)]['train_ids'] or m['donor'] not in membership[key(m)]['train_ids']: raise ValueError('Wrong student pool')
        if (a['label_id'],a['protocol'],a['repetition'])!=(b['label_id'],b['protocol'],b['repetition']): raise ValueError('Pair stratum')
        if m['arm']=='M3' and a['content_id']==b['content_id']: raise ValueError('Cross-content fixed point')
        if m['arm']=='M2' and m['receiver']!=m['donor']: raise ValueError('Incorrect true pair')
        grouped_maps[(*key(m),m['arm'])].append(m)
    for k,group in grouped_maps.items():
        expected=sorted(membership[k[:4]]['train_ids'])
        if sorted(r['receiver'] for r in group)!=expected or sorted(r['donor'] for r in group)!=expected: raise ValueError('Bijection failure')
    groups=defaultdict(list)
    for r in table(out/'oof.parquet'):
        if r['session_id'] not in membership[key(r)]['test_ids'] or assignment[r['content_id']]!=r['outer_fold']: raise ValueError('Test membership')
        if not np.isclose(sum(r['probabilities']),1): raise ValueError('Probability normalization')
        groups[(r['task'],r['protocol'],r['teacher_scheme'],r['arm'])].append(r)
    metrics=[]; gains=[]; content_gains=[]
    for (task,protocol,scheme,arm),rows in groups.items():
        expected={sid for sid,r in lookup.items() if r['protocol']==protocol and (task=='six_business' or r['label_id'].startswith('youtube.com::'))}
        if len(rows)!=len(expected) or {r['session_id'] for r in rows}!=expected: raise ValueError('OOF coverage')
        counts=Counter(r['content_id'] for r in rows); weights=np.asarray([1/counts[r['content_id']] for r in rows])
        p=np.asarray([r['probabilities'] for r in rows]); y=np.asarray([r['truth'] for r in rows])
        metrics.append({'task':task,'protocol':protocol,'teacher_scheme':scheme,'arm':arm,
            'sample_pooled':scores(y,p),'content_equal_log_loss_bits':float(np.average([r['loss_bits'] for r in rows],weights=weights)),
            'content_equal_macro_f1':float(f1_score(y,p.argmax(axis=1),average='macro',sample_weight=weights)),
            'content_equal_balanced_accuracy':float(balanced_accuracy_score(y,p.argmax(axis=1),sample_weight=weights)),
            'content_equal_brier':float(np.average(np.sum((p-np.eye(p.shape[1])[y])**2,axis=1),weights=weights))})
    for task in ('six_business','youtube_activity'):
        for protocol in cfg['protocols']:
            for scheme in cfg['teacher_schemes']:
                true={r['session_id']:r for r in groups[(task,protocol,scheme,'M2')]}
                for name,arm in [('G_task','M0'),('G_pair','M3'),('G_soft','M1')]:
                    other={r['session_id']:r for r in groups[(task,protocol,scheme,arm)]}; grouped=defaultdict(list)
                    for sid,r in true.items(): grouped[(r['label_id'],r['content_id'])].append(other[sid]['loss_bits']-r['loss_bits'])
                    labels=defaultdict(list)
                    for (label,content),values in sorted(grouped.items()):
                        mean=float(np.mean(values)); labels[label].append(mean)
                        content_gains.append({'task':task,'protocol':protocol,'scheme':scheme,'comparison':name,
                            'label_id':label,'content_id':content,'repetitions':len(values),'advantage_bits':mean})
                    if any(len(v)!=5 for v in labels.values()): raise ValueError('Content coverage changed')
                    array=np.asarray(list(labels.values())); rng=np.random.default_rng(cfg['seed'])
                    indices=rng.integers(0,5,size=(cfg['bootstrap_repetitions'],len(array),5))
                    bootstrap=array[np.arange(len(array))[None,:,None],indices].mean(axis=(1,2))
                    gains.append({'task':task,'protocol':protocol,'teacher_scheme':scheme,'comparison':name,
                        'advantage_bits':float(array.mean()),'conditional_ci_low':float(np.quantile(bootstrap,.025)),
                        'conditional_ci_high':float(np.quantile(bootstrap,.975)),
                        'interval_scope':'content_equal_class_stratified_conditional_on_fitted_models'})
    write_json(out/'metrics.json',metrics); write_table(out/'paired-gains.parquet',gains)
    write_table(out/'content-gains.parquet',content_gains)
    write_json(out/'validation.json',{'passed':True,'checked_pair_maps':len(maps),**complete})
    print(json.dumps({'validation':'passed','primary_gains':[r for r in gains if r['teacher_scheme']==0]}),flush=True)


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(); p.add_argument('--report',action='store_true'); args=p.parse_args()
    if args.report: report()
    else: run()
