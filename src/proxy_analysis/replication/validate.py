"""Independent identity, grouped OOF and repeated-feature acceptance checks."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path

import pyarrow.parquet as pq

from ..information_validation.data import write_json


def unique(rows, keys):
    counts = Counter(tuple(r[k] for k in keys) for r in rows)
    if any(n != 1 for n in counts.values()):
        raise ValueError(f'duplicate identity: {keys}')


def repeat(root):
    rows = pq.read_table(root/'repeat_feature_long.parquet').to_pylist()
    registry = pq.read_table(root/'run_registry.parquet').to_pylist()
    selected = {r['session_id']: r for r in registry if r['is_final']}
    unique(rows, ['session_id','scope','selection','metric'])
    if {r['session_id'] for r in rows} != set(selected):
        raise ValueError('repeated feature selected coverage mismatch')
    for r in rows:
        if any(r[k] != selected[r['session_id']][k] for k in ['activity_id','protocol','repetition','is_final']):
            raise ValueError('repeated feature registry mismatch')
        if r['delta'] is None and not r.get('reason'):
            raise ValueError('missing repeated delta without reason')
    if len({r['contract_sha256'] for r in rows}) != 1:
        raise ValueError('mixed repeat contracts')
    return {'rows':len(rows),'sessions':len(selected),'checks':['unique_metric','selected_coverage','registry_identity','missing_reason','one_contract']}


def information(root):
    splits=pq.read_table(root/'split-manifest.parquet').to_pylist()
    unique(splits,['setting','scheme','fold','role','session_id'])
    memberships=defaultdict(lambda: defaultdict(set))
    for r in splits: memberships[(r['setting'],r['scheme'],r['fold'])][r['role']].add(r['session_id'])
    labels={r['session_id']:r for r in pq.read_table(root/'label-evidence.parquet').to_pylist()}
    for (_,scheme,_), roles in memberships.items():
        if roles['train'] & roles['test']: raise ValueError('train/test session leakage')
        group='repetition' if scheme=='LORO' else 'content_id'
        if {labels[s][group] for s in roles['train']} & {labels[s][group] for s in roles['test']}:
            raise ValueError('outer group leakage')
    counts={}
    for file,fields in [('classification-oof.parquet',['view','model']),
                        ('recoverability-oof.parquet',['target_view','metric','model'])]:
        rows=pq.read_table(root/file).to_pylist()
        unique(rows,['setting','scheme',*fields,'session_id'])
        for r in rows:
            roles=memberships[(r['setting'],r['scheme'],r['fold'])]
            if r['session_id'] not in roles['test'] or r['session_id'] in roles['train']:
                raise ValueError('OOF sample not held out')
        counts[file]=len(rows)
    allowed=json.loads((root/'feature-allowlist.json').read_text())
    if [len(allowed[v]) for v in ['pre','post','delta']] != [14,14,17]:
        raise ValueError('three-view contract changed')
    return {**counts,'outer_folds':len(memberships),'checks':['outer_session_isolation','outer_group_isolation','OOF_unique','OOF_test_membership','three_view_allowlist']}


def repeat_statistics(root):
    def table(name): return pq.read_table(root/(name+'.parquet')).to_pylist()
    a=table('within_protocol_repeatability')
    keys=['stratum','selection','cohort','scope','protocol','metric']
    groups=defaultdict(list)
    unique(a,[*keys,'target_domain'])
    for r in a:
        if r['n']!=len(r['values']) or r['n']!=len(set(r['repetitions'])):
            raise ValueError('A repetition denominator mismatch')
        expected=set(range(1 if r['stratum']=='all5' else 2,6))
        if r['complete'] != (set(r['repetitions'])==expected):
            raise ValueError('A completeness mismatch')
        groups[tuple(r[k] for k in keys)].append(r)
    iccs=table('repeatability_icc')
    for r in iccs:
        g=groups[tuple(r[k] for k in keys)]
        if r['n_urls']!=sum(x['complete'] for x in g): raise ValueError('ICC complete-URL denominator mismatch')
    b=table('between_protocol_separation')
    for r in b:
        if r['scope']!='exclusive_page': raise ValueError('Hy2 entered strict B inference')
        if r['row_type']!='summary': continue
        sets=[]
        for protocol in ['SHADOWSOCKS','VLESS']:
            key=tuple(protocol if k=='protocol' else r[k] for k in keys)
            sets.append({x['target_domain'] for x in groups[key] if x['complete']})
        if r['n_urls']!=len(sets[0]&sets[1]): raise ValueError('B common-URL denominator mismatch')
    c=table('cross_url_consistency')
    for r in c:
        g=groups[tuple(r[k] for k in keys)]
        if r['n_urls_observed']!=len(g) or r['n_urls_n_ge_3']!=sum(x['n']>=3 for x in g):
            raise ValueError('C observed/eligible denominator mismatch')
        if sum(r[k] for k in ['increase','decrease','practically_stable','uncertain','distance_above_threshold','distance_within_threshold'])!=len(g):
            raise ValueError('C classification count mismatch')
    return {'A_rows':len(a),'ICC_rows':len(iccs),'B_rows':len(b),'C_rows':len(c),
            'checks':['A_repetitions','ICC_complete_grid','B_SS_VLESS_only_common_grid','C_observed_eligible_denominators']}


def reproduction(root):
    a=root/'information-validation'; b=root/'information-validation-reproduction'
    paths=sorted(a.glob('*.parquet'))
    if not paths or {p.name for p in paths}!={p.name for p in b.glob('*.parquet')}:
        raise ValueError('reproduction table set mismatch')
    result={}
    for p in paths:
        left=pq.read_table(p); right=pq.read_table(b/p.name)
        if not left.equals(right,check_metadata=False): raise ValueError(f'reproduction differs: {p.name}')
        result[p.name]={'rows':left.num_rows,'exact_table_equal':True}
    return {'tables':result,'comparison':'all table values and row order, ignoring Arrow metadata'}


def formal(root):
    paths=sorted(root.glob('nested-*.json'))
    if len(paths)!=16: raise ValueError('formal job count mismatch')
    n=0
    entity_rows=pq.read_table(root.parent/'ml/entity-wide.parquet',
        columns=['session_id','record_id','record_level','capture_side']).to_pylist()
    entities=defaultdict(set)
    carrier_sessions=defaultdict(set)
    for r in entity_rows:
        entities[r['session_id']].add((r['record_id'],r['record_level'],r['capture_side']))
        if r['record_level']=='carrier':carrier_sessions[r['record_id']].add(r['session_id'])
    for p in paths:
        report=json.loads(p.read_text(encoding='utf-8'))
        rows=report['oof']; unique(rows,['repeat','session_id'])
        if len(rows)!=report['session_count']*report['outer_repeats']:
            raise ValueError('formal OOF coverage mismatch')
        folds={(f['repeat'],f['fold']):f for f in report['folds']}
        for f in folds.values():
            if set(f['train_sites']) & set(f['test_sites']) or set(f['train_session_ids']) & set(f['test_session_ids']):
                raise ValueError('formal group leakage')
            train_entities=set().union(*(entities[s] for s in f['train_session_ids']))
            test_entities=set().union(*(entities[s] for s in f['test_session_ids']))
            if train_entities & test_entities: raise ValueError('formal indexed entity leakage')
        for r in rows:
            f=folds[(r['repeat'],r['fold'])]
            if r['session_id'] not in f['test_session_ids'] or r['group_site'] not in f['test_sites']:
                raise ValueError('formal OOF not held out')
        n+=len(rows)
    return {'jobs':len(paths),'oof_rows':n,'carrier_ids':len(carrier_sessions),
            'cross_session_carrier_ids':sum(len(v)>1 for v in carrier_sessions.values()),
            'checks':['site_isolation','session_isolation','indexed_entity_isolation','OOF_unique_per_repeat','OOF_test_membership','complete_coverage']}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('kind',choices=['repeat','repeat_statistics','information','reproduction','formal'])
    parser.add_argument('root',type=Path)
    args=parser.parse_args()
    result=globals()[args.kind](args.root)
    result['state']='passed'
    filename = 'independent-validation.json' if args.kind in ['repeat','information','formal'] else args.kind+'-validation.json'
    write_json(args.root/filename,result)
    print(json.dumps(result))


if __name__=='__main__': main()
