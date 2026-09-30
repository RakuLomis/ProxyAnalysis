"""Bounded metadata review of raw-extraction holds; no eligibility overrides."""
from collections import Counter, defaultdict
from pathlib import Path
import sys
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from proxy_analysis.extend_calibration.audit import read, write, fs_path, path_identity, bounded_trace
from proxy_analysis.parsing import PcapNgReader, decode_packet


def main():
    prior = ROOT / 'outputs/extend-calibration-20260930/run-01'
    base = prior / 'extraction-01'
    out = base / 'hold-review-02'
    out.mkdir(exist_ok=True)
    assert not (out / 'review.json').exists(), 'completed review is immutable'
    pool = pd.read_parquet(base / 'metadata-qualified-pool.parquet').set_index('session_id')
    cov = pd.read_parquet(base / 'full-coverage.parquet')
    missing, ambiguous, fragments = [], [], []
    for row in cov[~cov.W_gate_passed].to_dict('records'):
        sid = row['session_id']
        folder = base / 'sessions' / sid
        result, scope = read(folder/'complete.json'), read(folder/'scope.json')
        raw_base = (fs_path(ROOT/'Datasets/extend') / pool.loc[sid, 'manifest_relative']).parent
        flowdoc = read(raw_base/'analysis/flow-index.json')
        flows = {f['conn_id']: f for f in flowdoc['items'] if f['conn_id'] in scope['selected_logical_ids']}
        # The original lifecycle table only covered shared protocols. Read each
        # held session's verified snapshot here; absence from that table is NOT
        # evidence of missing lifecycle records for the exclusive protocols.
        evidence_rows, trace_audit = bounded_trace(raw_base/'raw/mihomo-trace.jsonl',
            read(raw_base/'analysis/summary.json'), set(scope['carriers']))
        assert trace_audit['status'] == 'bounded'
        assert trace_audit['sha256'] == result['input_hashes']['raw/mihomo-trace.jsonl']
        life = pd.DataFrame(evidence_rows, columns=['carrier_id','event_type','event_seq','ts'])
        for side, identifiers in [('pre', scope['missing_pre']), ('post', scope['missing_post'])]:
            for ident in identifiers:
                items = [flows[ident]] if side == 'pre' else [flows[v] for v in scope['carriers'][ident]]
                cids = {f['carrier_binding']['carrier_id'] for f in items}
                evidence = life[life.carrier_id.isin(cids)].copy()
                times = pd.to_datetime(evidence.ts, utc=True, errors='coerce')
                seconds = (times.astype('int64') - result['start_ns'])/1e9
                missing.append({'session_id': sid, 'protocol': row['protocol'], 'side': side, 'identifier': ident,
                    'networks': sorted({f.get(side+'_flow', {}).get('network', 'unknown') for f in items}),
                    'carrier_count': len(cids), 'related_logical_count': len(items),
                    'lifecycle_event_counts': dict(Counter(evidence.event_type)),
                    'first_lifecycle_relative_s': float(seconds.min()) if len(seconds) else None,
                    'last_lifecycle_relative_s': float(seconds.max()) if len(seconds) else None,
                    'window_seconds': (result['end_ns']-result['start_ns'])/1e9,
                    'decision': 'hold; lifecycle membership does not prove captured payload'})
        groups = defaultdict(set)
        for f in flows.values():
            for path in f['carrier_binding'].get('physical_paths') or [f.get('post_flow') or {}]:
                groups[path_identity(path)].add(f['carrier_binding']['carrier_id'])
        for path, cids in groups.items():
            if path and len(cids) > 1:
                evidence = life[life.carrier_id.isin(cids)]
                ambiguous.append({'session_id': sid, 'protocol': row['protocol'], 'post_path_hash': path,
                    'carrier_ids': sorted(cids), 'carrier_count': len(cids),
                    'lifecycle': evidence[['carrier_id','event_type','event_seq','ts']].to_dict('records'),
                    'decision': 'needs epoch-aware ownership; union counting and pair ownership are separate questions'})
        if 'selected_fragment' in row['review_reasons']:
            # One observed example per held session, not an estimate of full fragment composition.
            for packet in PcapNgReader(raw_base/'raw/phys.pcap'):
                p = decode_packet(packet.link_type, packet.packet_data)
                if p.ip_more_fragments and p.ip_fragment_offset == 0:
                    fragments.append({'session_id':sid, 'protocol':row['protocol'],
                        'raw_packet_ordinal':packet.packet_ordinal, 'transport':p.transport_protocol,
                        'ip_total_length':p.ip_total_len, 'first_fragment_payload_length':p.transport_payload_len,
                        'scope':'first first-fragment example only; no reassembly performed'})
                    break
    write(out/'missing-members.json', missing)
    write(out/'ambiguous-paths.json', ambiguous)
    write(out/'fragment-examples.json', fragments)
    reuse = read(base/'verification-01/identity-reuse.json')
    logical = [r for r in reuse if r['kind'] == 'logical_id']
    # Bare source endpoint conn_id strings are local aliases, not immutable global flows.
    endpoint_alias = [r for r in logical if ':' in r['identity_hash_or_id']]
    alias_note = {'repeated_logical_id_strings':len(logical), 'endpoint_style_aliases':len(endpoint_alias),
        'cross_fold_endpoint_aliases':sum(r['fold_count']>1 for r in endpoint_alias),
        'other_repeated_logical_ids':len(logical)-len(endpoint_alias),
        'repeated_carrier_ids':sum(r['kind']=='carrier_id' for r in reuse),
        'repeated_raw_file_hashes':sum(r['kind']=='raw_hash' for r in reuse),
        'interpretation':'raw string/path reuse is a flag, NOT established same-flow leakage; epoch-qualified identity audit remains open'}
    write(out/'identity-interpretation.json', alias_note)
    summary = {'held_visits':int((~cov.W_gate_passed).sum()), 'missing_member_rows':len(missing),
        'missing_member_visits':len({r['session_id'] for r in missing}),
        'ambiguous_path_groups':len(ambiguous), 'ambiguous_path_visits':len({r['session_id'] for r in ambiguous}),
        'fragment_example_sessions':len(fragments), 'fragment_example_transports':dict(Counter(r['transport'] for r in fragments)),
        'eligibility_changed':False, 'raw_data_modified':False, 'training_performed':False,
        'lifecycle_scope':'fresh verified bounded raw trace for every held session',
        'supersedes':'hold-review-01 used prior shared-only lifecycle table; empty exclusive-protocol evidence there was not conclusive'}
    write(out/'review.json', summary)
    print(summary)
    print(alias_note)


if __name__ == '__main__':
    main()
