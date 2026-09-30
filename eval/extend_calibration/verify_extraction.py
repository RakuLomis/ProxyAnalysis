"""Independent saved-event recomputation and CUDA round trip; never fits a model."""
from pathlib import Path
from collections import defaultdict
import json
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from proxy_analysis.extend_calibration.audit import read, write, file_hash

BASE = ROOT / 'outputs/extend-calibration-20260930/run-01/extraction-01'
OUT = BASE / 'verification-01'
WCOLS = ['W_up', 'W_down', 'P_up', 'P_down', 'R_up', 'R_down']
TCOLS = ['U_up', 'U_down', 'E_up', 'E_down', 'R_up', 'R_down']


def recount(frame, byte_column, per_connection=False):
    """Vectorized implementation independent of extraction.summarize."""
    if frame.empty:
        return np.zeros(6, dtype=np.int64)
    sort = (['logical_id'] if per_connection else []) + ['timestamp_ns', 'raw_packet_ordinal']
    f = frame.sort_values(sort)
    assert f.direction.isin([1, -1]).all() and f[byte_column].gt(0).all()
    assert not f.raw_packet_ordinal.duplicated().any()
    starts = f.direction.ne(f.direction.shift())
    if per_connection:
        starts |= f.logical_id.ne(f.logical_id.shift())
    return np.array([int(f.loc[f.direction.eq(d), byte_column].sum()) for d in [1, -1]] +
                    [int(f.direction.eq(d).sum()) for d in [1, -1]] +
                    [int((starts & f.direction.eq(d)).sum()) for d in [1, -1]], dtype=np.int64)


def reuse_table(registry, kind):
    return [{'kind': kind, 'identity_hash_or_id': k, 'sessions': sorted(v), 'session_count': len(v)}
            for k, v in registry.items() if len(v) > 1]


def main():
    OUT.mkdir(exist_ok=True)
    assert not (OUT / 'verification.json').exists(), 'completed verification is immutable'
    pool = pd.read_parquet(BASE / 'metadata-qualified-pool.parquet')
    coverage = pd.read_parquet(BASE / 'full-coverage.parquet')
    w = pd.read_parquet(BASE / 'full-W-features.parquet').set_index(['session_id', 'side'])
    t = pd.read_parquet(BASE / 'full-T-features.parquet').set_index(['session_id', 'side'])
    assert len(pool) == 600 and len(w) == len(t) == 1200
    registries = {k: defaultdict(set) for k in ['raw_hash', 'logical_id', 'carrier_id', 'pre_path', 'post_path']}
    validations, windows, ledger_reasons = [], [], []
    for n, row in enumerate(pool.to_dict('records'), 1):
        sid = row['session_id']
        folder = BASE / 'sessions' / sid
        complete, scope, pairs = [read(folder / name) for name in ['complete.json', 'scope.json', 'T-pairs.json']]
        common = {p['logical_id'] for p in pairs if p['common_valid_nonempty']}
        events = pd.read_parquet(folder / 'T-newbyte-events.parquet')
        ledger = pd.read_parquet(folder / 'T-direction-ledger.parquet')
        if not ledger.empty:
            for reason, count in ledger.loc[~ledger.valid, 'reasons'].value_counts().items():
                ledger_reasons.append({'protocol': row['protocol'], 'reasons': reason, 'directions': int(count)})
        for side in ['pre', 'post']:
            we = pd.read_parquet(folder / f'{side}-W-events.parquet')
            assert we.timestamp_ns.ge(complete['start_ns']).all() and we.timestamp_ns.lt(complete['end_ns']).all()
            rw = recount(we, 'payload_bytes')
            assert np.array_equal(rw, w.loc[(sid, side), WCOLS].to_numpy(dtype=np.int64))
            te = events if events.empty else events[events.side.eq(side) & events.logical_id.isin(common)]
            rt = recount(te, 'new_bytes', True)
            assert np.array_equal(rt, t.loc[(sid, side), TCOLS].to_numpy(dtype=np.int64))
            assert int(t.loc[(sid, side), 'F']) == len(common)
            if not te.empty:
                assert te.timestamp_ns.ge(complete['start_ns']).all() and te.timestamp_ns.lt(complete['end_ns']).all()
                le = ledger[ledger.side.eq(side) & ledger.logical_id.isin(common)]
                assert le.valid.all()
                for d, value in zip([1, -1], rt[:2]):
                    assert int(le.loc[le.direction.eq(d), 'unique_bytes'].sum()) == value
            validations.append({'session_id': sid, 'side': side, 'W_events': len(we), 'T_events': len(te),
                                'F': len(common), 'independent_counts_equal': True})
            registries['raw_hash'][complete['input_hashes'][f'raw/{"tun" if side == "pre" else "phys"}.pcap']].add(sid)
        for key, vals in [('logical_id', scope['selected_logical_ids']), ('carrier_id', scope['carriers']),
                          ('pre_path', scope['pre_path_hashes']), ('post_path', scope['post_path_hashes'])]:
            for v in vals:
                registries[key][v].add(sid)
        windows.append({'session_id': sid, 'start_ns': complete['start_ns'], 'end_ns': complete['end_ns']})
        if n % 100 == 0:
            print(f'Independent events {n}/600', flush=True)
    pd.DataFrame(validations).to_parquet(OUT / 'event-recomputation.parquet', index=False)
    if ledger_reasons:
        pd.DataFrame(ledger_reasons).groupby(['protocol', 'reasons'], as_index=False).directions.sum().to_parquet(OUT / 'T-invalid-direction-reasons.parquet', index=False)

    # No fitting or old experiment dataset reads: only existing algebraic CUDA functions.
    sys.path.insert(0, str(ROOT / 'eval/hy2_carrier_calibration'))
    import window_model as wm
    from proxy_analysis.feasible_summary_calibration import model as tm
    import torch
    assert torch.cuda.is_available()
    wa = w[WCOLS].to_numpy(dtype=np.int64)
    wd, _ = wm.decode(wm.encode(wa))
    assert wd.is_cuda and np.array_equal(wd.cpu().numpy(), wa)
    active = t[t.F.gt(0)]
    ta = active[TCOLS].to_numpy(dtype=np.int64)
    td, _ = tm.decode(tm.encode(ta), active.F.to_numpy(dtype=np.int64))
    assert td.is_cuda and np.array_equal(td.cpu().numpy(), ta)
    torch.cuda.synchronize()
    cuda = {'device': torch.cuda.get_device_name(0), 'torch': torch.__version__, 'W_rows': len(wa),
            'T_rows': len(ta), 'exact_integer_round_trip': True, 'model_fits': 0,
            'scope': 'algebra only, including held coverage rows; does not waive eligibility'}
    write(OUT / 'cuda-roundtrip.json', cuda)

    old_roles = ROOT / 'outputs/cross-business-calibration-0916/run-01/roles.parquet'
    roles = pd.read_parquet(old_roles)
    folds = roles.loc[roles.role.eq('H'), ['content_id', 'fold']].drop_duplicates()
    assert len(folds) == 30 and folds.content_id.is_unique
    members = pool[['session_id', 'protocol', 'content_id', 'label', 'repetition']].merge(folds, on='content_id', how='left', validate='many_to_one')
    assert members.fold.notna().all() and members.groupby(['protocol', 'fold']).size().eq(24).all()
    assert members.groupby('content_id').fold.nunique().eq(1).all()
    members.to_parquet(OUT / 'candidate-fold-members.parquet', index=False)
    member_index = members.set_index('session_id')
    reuse = [r for kind, reg in registries.items() for r in reuse_table(reg, kind)]
    for r in reuse:
        r['fold_count'] = int(member_index.loc[r['sessions'], 'fold'].nunique())
        r['content_count'] = int(member_index.loc[r['sessions'], 'content_id'].nunique())
    write(OUT / 'identity-reuse.json', reuse)
    wf = pd.DataFrame(windows).set_index('session_id')
    overlaps = []
    order = wf.sort_values('start_ns')
    for i, (sid, r) in enumerate(order.iterrows()):
        for sid2, r2 in order.iloc[i+1:].iterrows():
            if r2.start_ns >= r.end_ns:
                break
            overlaps.append({'session_a': sid, 'session_b': sid2})
    write(OUT / 'window-overlap.json', overlaps)
    # Tuple reuse is not connection identity. Do not silently equate the two.
    hard_reuse = [r for r in reuse if r['kind'] in ['raw_hash', 'logical_id', 'carrier_id'] and r['fold_count'] > 1]
    isolation = {'content_fold_consistency': True, 'cross_fold_registered_entity_or_raw_hash_reuse': len(hard_reuse),
                 'overlapping_manifest_windows': len(overlaps), 'reused_path_hashes': sum(r['kind'].endswith('_path') for r in reuse),
                 'packet_fingerprint_cross_file_audit_complete': False,
                 'full_split_isolation_passed': False,
                 'note': 'candidate content folds only; physical epochs and cross-file packet identity not fully audited'}
    write(OUT / 'candidate-isolation.json', isolation)
    stats = coverage.groupby('protocol', as_index=False).agg(visits=('session_id', 'size'), W_passed=('W_gate_passed', 'sum'),
        T_candidate_pairs=('T_candidate_pairs', 'sum'), T_common_pairs=('T_common_pairs', 'sum'))
    stats.to_parquet(OUT / 'protocol-coverage.parquet', index=False)
    holds = pool.merge(coverage[['session_id', 'W_gate_passed', 'review_reasons']], on='session_id', validate='one_to_one')
    holds = holds[~holds.W_gate_passed][['session_id', 'protocol', 'content_id', 'label', 'repetition', 'review_reasons']]
    holds.to_parquet(OUT / 'held-visits.parquet', index=False)
    verdict = {'visits': len(pool), 'independent_event_recomputation_passed': True, 'cuda_round_trip_passed': True,
        'W_coverage_passed': int(coverage.W_gate_passed.sum()), 'W_held': len(holds),
        'T_nonempty_visits': int(coverage.T_common_pairs.gt(0).sum()), 'training_allowed': False,
        'training_performed': False, 'permission_packages_exported': False,
        'source_hashes': {str(p.relative_to(ROOT)): file_hash(p) for p in [Path(__file__), BASE/'contract.json', old_roles,
                         BASE/'full-W-features.parquet', BASE/'full-T-features.parquet', BASE/'full-coverage.parquet']}}
    write(OUT / 'verification.json', verdict)
    print(json.dumps(verdict, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
