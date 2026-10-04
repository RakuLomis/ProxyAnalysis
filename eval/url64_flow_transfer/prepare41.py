"""Freeze the approved 41-class/four-deployment metadata scope, no learning."""
from concurrent.futures import ProcessPoolExecutor
from collections import defaultdict
from pathlib import Path
import argparse
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
import pandas as pd
from proxy_analysis.extend_calibration.audit import read, write, fs_path, file_hash, digest, path_identity
from proxy_analysis.extend_calibration.common_window import define_window

PROTOCOLS = ['shadowsocks', 'vless', 'trojan', 'vmess']
OLD = ROOT / 'outputs/extend-calibration-20260930/run-01'
BASE = ROOT / 'outputs/url64-flow-transfer-extend/run-01'
OUT = BASE / 'approved41-01'


def public_post_index(flows, protocol):
    """Strip pre, requests, match quality and labels BEFORE side selection.

    Declared offline carrier index is required. This is not blind online inference.
    No logical lifecycle or positive pre-packet test enters post selection.
    """
    result = []
    for f in flows:
        b = f.get('carrier_binding') or {}
        sem = f.get('proxy_semantics') or {}
        p = sem.get('protocol')
        if p == 'ss': p = 'shadowsocks'
        if p != protocol or f.get('egress_outcome') != 'proxy': continue
        result.append({'carrier': b.get('carrier_id'), 'mode': b.get('mode'),
                       'paths': b.get('physical_paths') or [f.get('post_flow') or {}],
                       'adapter': sem.get('adapter_instance_id')})
    return result


def select_post(index):
    by_carrier = defaultdict(dict)
    for r in index:
        if r['mode'] != 'exclusive' or not r['carrier']: continue
        for p in r['paths']:
            if p.get('network') != 'tcp' or p.get('shared') or not p.get('complete'): continue
            h = path_identity(p)
            if h:
                by_carrier[r['carrier']][h] = p
    return {c: list(paths.values()) for c, paths in sorted(by_carrier.items())}


def prepare_one(row):
    base = (fs_path(ROOT / 'Datasets/extend') / row['manifest_relative']).parent
    manifest = read(base / 'manifest.json')
    context = read(base / 'raw/capture-context.json')
    netlog = read(base / 'raw/netlog.json')
    window = define_window(manifest, context, netlog)
    flows = read(base / 'analysis/flow-index.json')['items']
    post_index = public_post_index(flows, row['protocol'])
    post = select_post(post_index)
    pre = {}
    for f in flows:
        sem = f.get('proxy_semantics') or {}
        p = sem.get('protocol'); p = 'shadowsocks' if p == 'ss' else p
        path = f.get('pre_flow') or {}
        if (p == row['protocol'] and f.get('egress_outcome') == 'proxy'
                and path.get('network') == 'tcp' and path.get('complete') and path_identity(path)):
            pre[f['conn_id']] = [path]
    # Request lineage is descriptive only; capture-associated background remains
    # in the registered observation, not forced into resource-semantic labels.
    hashes = {name: file_hash(base / name) for name in ['manifest.json', 'raw/capture-context.json',
              'raw/netlog.json', 'analysis/flow-index.json']}
    saved = dict(row, window=window, pre_index=pre, post_index=post,
                 input_hashes=hashes, builds=manifest['component_versions'])
    write(OUT / 'private-audit' / f"{row['session_id']}.json", saved)
    # These permitted observation manifests deliberately do not include the other side.
    write(OUT / 'side-index' / 'post' / f"{row['session_id']}.json",
          {'session_id': row['session_id'], 'window': window, 'connections': post})
    write(OUT / 'side-index' / 'pre' / f"{row['session_id']}.json",
          {'session_id': row['session_id'], 'window': window, 'connections': pre})
    return {'session_id': row['session_id'], 'protocol': row['protocol'], 'role_pool': row['role_pool'],
            'start_ns': window['start_ns'], 'end_ns': window['end_ns'],
            'pre_tcp_index_size': len(pre), 'post_tcp_index_size': len(post),
            'post_carriers': sorted(post), 'netlog_sha256': hashes['raw/netlog.json']}


def main(workers):
    assert not (OUT / 'preparation.json').exists(), 'Frozen output exists'
    sessions = pd.read_parquet(OLD / 'sessions.parquet')
    broad = pd.read_parquet(BASE / 'broad-visits.parquet')
    broad = broad[broad.protocol.isin(PROTOCOLS) & broad.route.eq('proxy_success')]
    assert len(broad) == 164
    labels = sorted(broad.url_key.unique()); assert len(labels) == 41
    for p in PROTOCOLS:
        assert set(broad[broad.protocol.eq(p)].url_key) == set(labels)
    cal = pd.read_parquet(BASE / 'calibration-candidates.parquet')
    cal = cal[cal.protocol.isin(PROTOCOLS) & ~cal.overlaps_broad_observed_alias
              & cal.prior_route.eq('proxy_success') & cal.prior_generation_ok
              & cal.summary_generation_ok & cal.repetition.isin([1, 2, 4, 5])]
    common = set.intersection(*[set(g.index[g.eq(4)]) for p in PROTOCOLS
                  for g in [cal[cal.protocol.eq(p)].groupby('content_id').repetition.nunique()]])
    assert len(common) >= 6
    # Fixed deterministic sampling independent of class labels, raw features, or accuracy.
    ordered = sorted(common, key=lambda c: digest(['url41-calibration-v1', c]))
    selected = ordered[:6]
    cs = cal[cal.content_id.isin(selected)]
    assert len(cs) == 96 and not cs.session_id.duplicated().any()
    pool = sessions[sessions.session_id.isin(set(broad.session_id) | set(cs.session_id))].copy()
    pool['role_pool'] = pool.session_id.map(lambda s: 'C' if s in set(cs.session_id) else 'Broad')
    assert len(pool) == 260
    OUT.mkdir(parents=True, exist_ok=True)
    pool.to_parquet(OUT / 'candidate-visits.parquet', index=False)
    write(OUT / 'registration.json', {
        'user_approved': '41 common classes and four exclusive TCP deployments',
        'protocols': PROTOCOLS, 'labels': [{'label_id': i, 'url_key': u} for i, u in enumerate(labels)],
        'calibration_candidate_order': ordered, 'calibration_contents': selected,
        'calibration_rule': 'first six SHA256-ranked content IDs using url41-calibration-v1; no task labels or features',
        'repetitions': [1, 2, 4, 5], 'per_target': {'C': 24, 'U': 123, 'H': 41},
        'A_all_source_pool': 'same four deployments as B and A_matched; three sources per target',
        'post_selection': 'proxy exclusive TCP carrier paths from offline post index; observed positive post data in fixed window required later',
        'pre_selection': 'proxy TCP logical paths independently; no positive post or match-status requirement',
        'background_scope': 'capture-associated proxy connections, not exclusively page-request-attributed flows',
        'side_indexes_contain_endpoint_metadata': 'observation routing only; never classifier/generator numerical inputs; keep outputs local',
        'paired_C_rule_pending': 'independent side eligibility intersection may qualify pairs only within C',
        'training_allowed': False, 'code_sha256': file_hash(Path(__file__)),
        'source_hashes': {n: file_hash(BASE / n) for n in ['broad-visits.parquet', 'calibration-candidates.parquet']}})
    fields = ['session_id', 'protocol', 'manifest_relative', 'role_pool', 'content_id']
    rows = pool[fields].to_dict('records')
    results = []
    with ProcessPoolExecutor(max_workers=workers) as ex:
        for i, r in enumerate(ex.map(prepare_one, rows), 1):
            results.append(r)
            if i % 20 == 0: print(f'Prepared {i}/{len(rows)}', flush=True)
    pd.DataFrame(results).to_parquet(OUT / 'windows-and-counts.parquet', index=False)
    roles = []
    for target in PROTOCOLS:
        for r in rows:
            if r['role_pool'] == 'C' and r['protocol'] != target: continue
            role = 'C' if r['role_pool'] == 'C' else 'H' if r['protocol'] == target else 'U'
            roles.append({'target': target, 'session_id': r['session_id'], 'role': role,
                          'protocol': r['protocol'], 'content_id': r['content_id']})
    pd.DataFrame(roles).to_parquet(OUT / 'provisional-roles.parquet', index=False)
    ordered_windows = sorted(results, key=lambda r: r['start_ns'])
    overlaps = []
    for i, a in enumerate(ordered_windows):
        for b in ordered_windows[i+1:]:
            if b['start_ns'] >= a['end_ns']: break
            overlaps.append([a['session_id'], b['session_id']])
    carriers = defaultdict(set)
    for r in results:
        for c in r['post_carriers']: carriers[c].add(r['session_id'])
    reused = {c: sorted(s) for c,s in carriers.items() if len(s) > 1}
    status = {'visits': len(results), 'windows_valid': len(results), 'overlapping_windows': overlaps,
              'cross_visit_registered_carriers': reused,
              'empty_pre_indexes': sum(not r['pre_tcp_index_size'] for r in results),
              'empty_post_indexes': sum(not r['post_tcp_index_size'] for r in results),
              'raw_packet_identity_audit_pending': True, 'training_allowed': False}
    write(OUT / 'preparation.json', status)
    print(status, flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--workers', type=int, default=4)
    main(p.parse_args().workers)
