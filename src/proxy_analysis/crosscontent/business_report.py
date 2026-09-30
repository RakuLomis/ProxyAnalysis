"""Independent membership checks and content-clustered task/pair gains."""
from collections import defaultdict
import json
from pathlib import Path

import numpy as np

from ..paired_information.prepare import table, digest
from ..reproducibility.preflight import write_json, write_table
from .business_features import load_config
from .business_splits import outer_assignment
from .privileged_learning import scores


def main():
    cfg=load_config(); root=Path(cfg['output_root']); model_root=root/'learning'
    complete=json.loads((model_root/'complete.json').read_text(encoding='utf-8'))
    for name,expected in complete['artifacts'].items():
        if digest(model_root/name)!=expected: raise ValueError('Model artifact changed')
    out=root/'report'; out.mkdir(exist_ok=False)
    cohort=table(root/'primary-cohort.parquet'); lookup={r['session_id']:r for r in cohort}
    assignment=outer_assignment(cohort,cfg['seed'])
    splits=json.loads((model_root/'teacher-splits.json').read_text(encoding='utf-8'))
    split_lookup={(r['task'],r['protocol'],r['outer_fold'],r['scheme'],r['teacher_holdout']):r for r in splits}
    checked_maps=0
    map_groups=defaultdict(list)
    for m in table(model_root/'pair-maps.parquet'):
        key=(m['task'],m['protocol'],m['outer_fold'],m['scheme'],m['teacher_holdout'])
        s=split_lookup[key]; a,b=lookup[m['receiver']],lookup[m['donor']]
        train={lookup[sid]['content_id'] for sid in s['train_ids']}
        if a['content_id'] in train or b['content_id'] in train: raise ValueError('Teacher saw paired content')
        if m['receiver'] not in s['holdout_ids'] or m['donor'] not in s['holdout_ids']: raise ValueError('Donor crossed teacher partition')
        if any(assignment[r['content_id']]==m['outer_fold'] for r in (a,b)): raise ValueError('Outer test used for pairing')
        if (a['label_id'],a['protocol'])!=(b['label_id'],b['protocol']): raise ValueError('Wrong pair stratum')
        if m['arm']=='M2' and m['receiver']!=m['donor']: raise ValueError('True pair not identity')
        if m['arm']=='M3' and (a['content_id']==b['content_id'] or a['repetition']!=b['repetition']): raise ValueError('Invalid cross-content control')
        if m['arm']=='M3_within_content' and (a['content_id']!=b['content_id'] or m['receiver']==m['donor']): raise ValueError('Invalid within-content control')
        map_groups[(m['task'],m['protocol'],m['outer_fold'],m['scheme'],m['arm'],m['seed'])].append(m)
        checked_maps+=1
    for group in map_groups.values():
        receivers=[r['receiver'] for r in group]; donors=[r['donor'] for r in group]
        if len(set(receivers))!=len(receivers) or sorted(receivers)!=sorted(donors): raise ValueError('Mapping not bijective')
    prediction_rows=table(model_root/'oof.parquet'); groups=defaultdict(list)
    for r in prediction_rows:
        original=lookup[r['session_id']]
        if assignment[original['content_id']]!=r['outer_fold']: raise ValueError('Prediction in wrong outer fold')
        if r['protocol']!=original['protocol']: raise ValueError('Prediction protocol changed')
        labels=sorted({c['label_id'] for c in cohort if r['task']=='six_business' or c['label_id'].startswith('youtube.com::')})
        if r['truth']!=labels.index(original['label_id']): raise ValueError('Prediction label changed')
        if not np.isclose(sum(r['probabilities']),1): raise ValueError('Probabilities not normalized')
        groups[(r['task'],r['protocol'],r['teacher_scheme'],r['arm'],r['mismatch_seed'])].append(r)
    summary=[]
    for (task,protocol,scheme,arm,seed),rows in groups.items():
        expected={r['session_id'] for r in cohort if r['protocol']==protocol and (task=='six_business' or r['label_id'].startswith('youtube.com::'))}
        if {r['session_id'] for r in rows}!=expected or len(rows)!=len(expected): raise ValueError('OOF coverage/duplicate failure')
        summary.append({'task':task,'protocol':protocol,'teacher_scheme':scheme,'arm':arm,'mismatch_seed':seed,
                        **scores([r['truth'] for r in rows],[r['probabilities'] for r in rows])})
    write_json(out/'metrics.json',summary)
    gains=[]; content_rows=[]
    for task in ('six_business','youtube_activity'):
        for protocol in cfg['protocols']:
            for scheme in cfg['teacher_schemes']:
                true={r['session_id']:r for r in groups[(task,protocol,scheme,'M2',-1)]}
                controls=[('G_task','M0',-1,-1),('G_pair','M3',scheme,-1),('G_soft','M1',scheme,-1)]
                controls += [('G_within','M3_within_content',scheme,seed) for seed in cfg['within_content_seeds']]
                for kind,arm,control_scheme,seed in controls:
                    other={r['session_id']:r for r in groups[(task,protocol,control_scheme,arm,seed)]}
                    by_content=defaultdict(list)
                    for sid,r in true.items():
                        by_content[(r['label_id'],r['content_id'])].append(other[sid]['loss_bits']-r['loss_bits'])
                    label_values=defaultdict(list)
                    for (label,content),values in sorted(by_content.items()):
                        value=float(np.mean(values)); label_values[label].append(value)
                        content_rows.append({'task':task,'protocol':protocol,'scheme':scheme,'comparison':kind,
                            'mismatch_seed':seed,'label_id':label,'content_id':content,'advantage_bits':value})
                    if any(len(v)!=5 for v in label_values.values()): raise ValueError('Five test contents per label required')
                    array=np.asarray(list(label_values.values())); rng=np.random.default_rng(cfg['seed'])
                    indices=rng.integers(0,5,size=(cfg['bootstrap_repetitions'],len(array),5))
                    bootstrap=array[np.arange(len(array))[None,:,None],indices].mean(axis=(1,2))
                    gains.append({'task':task,'protocol':protocol,'teacher_scheme':scheme,'comparison':kind,
                        'mismatch_seed':seed,'advantage_bits':float(array.mean()),
                        'conditional_ci_low':float(np.quantile(bootstrap,.025)),
                        'conditional_ci_high':float(np.quantile(bootstrap,.975)),
                        'positive_contents':int(np.sum(array>0)),'contents':int(array.size),
                        'interval_scope':'class_stratified_content_bootstrap_conditional_on_fitted_models_not_external_validation'})
    write_table(out/'paired-gains.parquet',gains)
    write_table(out/'content-gains.parquet',content_rows)
    write_json(out/'validation.json',{'passed':True,'checked_pair_map_rows':checked_maps,
        'prediction_rows':len(prediction_rows),'fresh_fit_count':complete['fresh_fits'],
        'model_source_sha256':digest(model_root/'complete.json')})
    primary=[r for r in gains if r['teacher_scheme']==0 and r['comparison']!='G_within']
    write_json(out/'primary-gains.json',primary)
    # Review-only plan for 299: enforce common rounds between both donor contents
    # under each already-fixed teacher split. Do not train the sensitivity here.
    candidates=table(root/'candidates.parquet'); eligibility={r['session_id']:r for r in candidates if r['effective_label_valid']}
    all_rows=[r for r in table(root/'side-summaries.parquet') if r['selection']=='observed' and r['session_id'] in eligibility]
    from .business_splits import teacher_assignment
    sensitivity=[]
    for task in ('six_business','youtube_activity'):
        for protocol in cfg['protocols']:
            rows=[r for r in all_rows if r['protocol']==protocol and (task=='six_business' or r['label_id'].startswith('youtube.com::'))]
            for fold in range(5):
                train=[r for r in rows if assignment[r['content_id']]!=fold]
                for scheme in cfg['teacher_schemes']:
                    partition=teacher_assignment(train,scheme); strata=defaultdict(lambda:defaultdict(set))
                    for r in train: strata[(r['label_id'],partition[r['content_id']])][r['content_id']].add(r['repetition'])
                    keep=set()
                    for (label,held),contents in strata.items():
                        common=set.intersection(*contents.values())
                        keep.update(r['session_id'] for r in train if r['label_id']==label and partition[r['content_id']]==held and r['repetition'] in common)
                    sensitivity.append({'task':task,'protocol':protocol,'outer_fold':fold,'scheme':scheme,
                        'available_train':len(train),'matched_train':len(keep),
                        'excluded_ids':[r['session_id'] for r in train if r['session_id'] not in keep],
                        'available_test':sum(assignment[r['content_id']]==fold for r in rows),
                        'status':'review_only_not_trained'})
    write_json(out/'299-sensitivity-proposal.json',sensitivity)
    print(json.dumps({'validation':'passed','primary_gains':primary},ensure_ascii=False),flush=True)


if __name__=='__main__': main()
