"""Index-level business pairing plus primary raw-capture identity audit."""
import hashlib
import json
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

from ..indexing.pairs import build_exclusive_pairs
from ..parsing import PcapNgReader, decode_packet
from ..reproducibility.preflight import write_json, write_table
from .next_stage import load, verify
from .prepare import canonical, digest, guarded, table


def main():
    cfg = load('configs/paired-value-next-stage-0914.yaml')
    verify(cfg)
    source = Path(cfg['source_root'])
    out = Path(cfg['output_root'])/'raw-and-pair-audit'
    out.mkdir(exist_ok=False)
    primary = {r['session_id'] for r in table(source/'cohort.parquet')}
    rows = [r for r in table(source/'registry.parquet') if r['is_final']]
    session_results, captures, sources = [], [], {}
    for row in rows:
        sid = row['session_id']
        if row['protocol'] == 'HYSTERIA2':
            session_results.append({'session_id': sid, 'protocol': row['protocol'],
                'accepted_tcp_pairs': 0, 'status': 'shared_udp_outside_strict_tcp_pair_design',
                'primary': False, 'error': None})
            continue
        path = Path(row['session_path'])
        for name in ('connection-index-v2.json', 'pcap-index-v1.json'):
            item = guarded(path/'analysis'/name, cfg['raw_root'])
            sources[str(item)] = digest(item)
        try:
            candidates = build_exclusive_pairs(path, row['protocol'])
            counts = Counter((p.post.entity_id, str(p.post.capture_path)) for p in candidates)
            accepted = [p for p in candidates if counts[(p.post.entity_id, str(p.post.capture_path))] == 1
                        and p.pre.transport_protocol == p.post.transport_protocol == 'tcp']
            for pair in accepted:
                for desc in (pair.pre, pair.post):
                    cap = guarded(desc.capture_path, cfg['raw_root'])
                    if sid in primary:
                        # Addresses are audit-only, never fed into a model.
                        endpoints = sorted([(desc.initiator.ip, desc.initiator.port),
                                            (desc.responder.ip, desc.responder.port)])
                        captures.append({'session_id': sid, 'target_url': row['target_url'],
                            'connection_id': pair.connection_id, 'side': desc.capture_side,
                            'path': str(cap), 'canonical_path': str(canonical(cap)),
                            'sha256': digest(cap), 'tuple_key': json.dumps(endpoints)})
            session_results.append({'session_id': sid, 'protocol': row['protocol'],
                'accepted_tcp_pairs': len(accepted),
                'status': 'indexed_pairs_files_present' if accepted else 'no_eligible_exclusive_tcp_pair',
                'primary': sid in primary, 'error': None})
        except Exception as exc:
            session_results.append({'session_id': sid, 'protocol': row['protocol'],
                'accepted_tcp_pairs': None, 'status': 'audit_error', 'primary': sid in primary,
                'error': str(exc)})
    write_table(out/'business-index-pair-eligibility.parquet', session_results)
    write_table(out/'primary-capture-identities.parquet', captures)
    duplicates = []
    for key in ('canonical_path', 'sha256'):
        grouped = defaultdict(list)
        for row in captures:
            grouped[row[key]].append(row)
        for value, group in grouped.items():
            if len({r['session_id'] for r in group}) > 1:
                duplicates.append({'kind': key, 'value': value,
                                   'sessions': sorted({r['session_id'] for r in group})})
    tuples = defaultdict(list)
    for row in captures:
        tuples[row['tuple_key']].append(row)
    parsed = {}

    def packets(row):
        if row['path'] in parsed:
            return parsed[row['path']]
        ids, syns, times = set(), set(), []
        first_initial_syn = None
        for record in PcapNgReader(Path(row['path'])):
            times.append(record.timestamp_ns)
            ids.add((record.timestamp_ns, hashlib.sha256(record.packet_data).hexdigest()))
            packet = decode_packet(record.link_type, record.packet_data)
            initial = packet.tcp_flags_raw is not None and bool(packet.tcp_flags_raw & 2) and not bool(packet.tcp_flags_raw & 16)
            if first_initial_syn is None:
                first_initial_syn = initial
            if initial:
                syns.add((packet.ip_src, packet.src_port, packet.tcp_seq))
        result = (ids, syns, min(times) if times else None,
                  max(times) if times else None, first_initial_syn)
        parsed[row['path']] = result
        return result

    comparisons = []
    for key, group in tuples.items():
        for a, b in combinations(group, 2):
            if a['session_id'] == b['session_id']:
                continue
            aa, bb = packets(a), packets(b)
            overlap = None if aa[2] is None or bb[2] is None else max(aa[2], bb[2]) <= min(aa[3], bb[3])
            comparisons.append({'session_a': a['session_id'], 'session_b': b['session_id'],
                'path_a': a['path'], 'path_b': b['path'], 'different_url': a['target_url'] != b['target_url'],
                'time_overlap': overlap, 'identical_packet_count': len(aa[0] & bb[0]),
                'shared_initial_syn_identity_count': len(aa[1] & bb[1]),
                'both_start_initial_syn': bool(aa[4] and bb[4])})
    write_json(out/'cross-session-file-duplicates.json', duplicates)
    write_json(out/'tuple-reuse-comparisons.json', comparisons)
    write_json(out/'source-hashes.json', sources)
    result = {'selected_sessions': len(rows), 'primary_capture_records': len(captures),
        'primary_accepted_pairs': len(captures)//2, 'cross_session_duplicate_file_groups': len(duplicates),
        'tuple_reuse_comparisons': len(comparisons),
        'tuple_reuse_time_overlaps': sum(r['time_overlap'] is True for r in comparisons),
        'tuple_reuse_identical_packets': sum(r['identical_packet_count'] for r in comparisons),
        'audit_errors': sum(r['status'] == 'audit_error' for r in session_results),
        'business_status_counts': dict(Counter(r['status'] for r in session_results)),
        'scope': 'Raw identity: primary 140 only. Pair-file eligibility: all selected SS/VLESS.',
        'limitation': 'Index eligibility and file presence do not establish semantic activity validity or full extraction quality.'}
    write_json(out/'result.json', result)
    print(json.dumps(result), flush=True)
    if result['audit_errors'] or duplicates or result['tuple_reuse_identical_packets']:
        raise ValueError('Raw/pair audit requires review; see persisted outputs')


if __name__ == '__main__':
    main()
