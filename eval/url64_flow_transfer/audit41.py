"""Bounded raw identity and clock checks for the registered 260 visits.

Audit-only access to both sides; output is not a training package. No features
or classifier are fitted and no flow is retained based on the other side.
"""
from collections import defaultdict, Counter
from concurrent.futures import ProcessPoolExecutor
from decimal import Decimal
import argparse
import hashlib
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
import pandas as pd
from proxy_analysis.extend_calibration.audit import read, write, fs_path, file_hash, path_identity
from proxy_analysis.extend_calibration.forensic import endpoint, flow_tuple
from proxy_analysis.extend_calibration.extraction_v3 import reverse
from proxy_analysis.parsing import PcapNgReader, decode_packet
from proxy_analysis.parsing.packet_decoder import _strip_link_header

BASE = ROOT / 'outputs/url64-flow-transfer-extend/run-01/approved41-01'
OUT = BASE / 'raw-audit-01'


def anchors_from_netlog(doc):
    names = {v:k for k,v in doc['constants']['logEventTypes'].items()}
    offset = Decimal(str(doc['constants']['timeTickOffset']))
    begins, intervals = {}, []
    for e in doc['events']:
        if names.get(e['type']) != 'TCP_CONNECT': continue
        source = e['source']['id']; params = e.get('params') or {}
        utc = int((Decimal(str(e['time'])) + offset) * 1_000_000)
        if e['phase'] == 1: begins[source] = utc
        elif (e['phase'] == 2 and source in begins and not params.get('net_error')
              and params.get('local_address') and params.get('remote_address')):
            a, b = endpoint(params['local_address']), endpoint(params['remote_address'])
            intervals.append((('tcp', *a, *b), begins[source], utc))
    return intervals


def one(sid):
    scope = read(BASE / 'private-audit' / f'{sid}.json')
    base = (fs_path(ROOT / 'Datasets/extend') / scope['manifest_relative']).parent
    dest = OUT / 'sessions' / f'{sid}.json'
    if dest.exists():
        saved = read(dest)
        assert saved['scope_sha256'] == file_hash(BASE / 'private-audit' / f'{sid}.json')
        for name, h in saved['raw_hashes'].items(): assert file_hash(base / name) == h
        return saved
    for name, h in scope['input_hashes'].items(): assert file_hash(base / name) == h
    a, b = scope['window']['start_ns'], scope['window']['end_ns']
    intervals = anchors_from_netlog(read(base / 'raw/netlog.json'))
    anchor_keys = {k for k, _, _ in intervals}
    anchor_seen = defaultdict(lambda: {'syn': [], 'synack': []})
    counts, evidence, raw_hashes = [], [], {}
    positive_hashes = set()
    for side, filename in [('pre','tun.pcap'), ('post','phys.pcap')]:
        mapping = defaultdict(set)
        for ident, paths in scope[side + '_index'].items():
            for path in paths:
                k = flow_tuple(path); h = path_identity(path)
                mapping[k].add((ident, h, 1)); mapping[reverse(k)].add((ident, h, -1))
        per_path = defaultdict(lambda: {'positive_packets': 0, 'syn': set(), 'ids': set(), 'bad_packets': 0})
        stats = Counter(); first = last = None
        for rec in PcapNgReader(base / 'raw' / filename):
            stats['raw_packets'] += 1
            first = rec.timestamp_ns if first is None else min(first, rec.timestamp_ns)
            last = rec.timestamp_ns if last is None else max(last, rec.timestamp_ns)
            p = decode_packet(rec.link_type, rec.packet_data)
            k = (p.transport_protocol, p.ip_src, p.src_port, p.ip_dst, p.dst_port)
            flags = p.tcp_flags_raw or 0
            if side == 'pre' and p.transport_protocol == 'tcp' and flags & 2:
                canonical = reverse(k) if flags & 16 else k
                if canonical in anchor_keys:
                    anchor_seen[canonical]['synack' if flags & 16 else 'syn'].append(rec.timestamp_ns)
            matches = mapping.get(k)
            if not matches: continue
            for ident, h, direction in matches:
                v = per_path[h]; v['ids'].add(ident)
                if direction == 1 and flags & 2 and not flags & 16: v['syn'].add(p.tcp_seq)
            if not a <= rec.timestamp_ns < b: continue
            stats['selected_packets_in_window'] += 1
            if len(matches) > 1: stats['multi_owner_packets'] += 1
            if (p.transport_payload_len or 0) <= 0: continue
            stats['positive_packets'] += 1
            fragment = bool(p.ip_fragment_offset or p.ip_more_fragments)
            valid = p.decode_status == 'ok' and not fragment and rec.captured_len >= rec.original_len
            ip = _strip_link_header(rec.link_type, rec.packet_data) if valid else b''
            valid = valid and p.ip_total_len is not None and len(ip) >= p.ip_total_len
            if valid: positive_hashes.add(hashlib.sha256(ip[:p.ip_total_len]).digest())
            else: stats['positive_packet_requires_reassembly_or_review'] += 1
            for _, h, _ in matches:
                per_path[h]['positive_packets'] += 1
                per_path[h]['bad_packets'] += int(not valid)
        for h, value in per_path.items():
            syns = value.pop('syn'); ids = value.pop('ids')
            evidence.append({'side': side, 'path_hash': h, 'entity_ids': sorted(ids), **value,
                             'syn_count': len(syns),
                             'syn_signatures': [hashlib.sha256(f'{h}:{seq}'.encode()).hexdigest() for seq in sorted(syns)]})
        counts.append({'side': side, **dict(stats), 'first_ns': first, 'last_ns': last,
                       'positive_entities': len({i for v in evidence if v['side'] == side
                                                 and v['positive_packets'] for i in v['entity_ids']})})
        raw_hashes['raw/' + filename] = file_hash(base / 'raw' / filename)
    anchors = []
    for k, start, end in intervals:
        obs = anchor_seen[k]; tol = 2_000_000
        anchors.append({'observable': bool(obs['synack']),
                        'passed': any(start-tol <= t <= end+tol for t in obs['syn'])
                                  and any(start-tol <= t <= end+tol for t in obs['synack'])})
    result = {'session_id': sid, 'protocol': scope['protocol'], 'scope_sha256': file_hash(BASE/'private-audit'/f'{sid}.json'),
              'counts': counts, 'paths': evidence, 'raw_hashes': raw_hashes,
              'observable_anchors': sum(x['observable'] for x in anchors),
              'failed_observable_anchors': sum(x['observable'] and not x['passed'] for x in anchors),
              'training_allowed': False}
    pd.DataFrame({'sha256': sorted(positive_hashes)}).to_parquet(OUT / 'packet-hashes' / f'{sid}.parquet', index=False)
    write(dest, result)
    return result


def main(workers):
    assert (BASE / 'preparation.json').exists()
    assert not (OUT / 'summary.json').exists()
    (OUT / 'packet-hashes').mkdir(parents=True, exist_ok=True)
    ids = pd.read_parquet(BASE / 'candidate-visits.parquet').session_id.to_list()
    results = []
    with ProcessPoolExecutor(max_workers=workers) as ex:
        for i, r in enumerate(ex.map(one, ids), 1):
            results.append(r)
            print(f"Identity {i}/{len(ids)} {r['protocol']}", flush=True)
            write(OUT / 'progress.json', {'completed': i, 'total': len(ids), 'training_allowed': False})
    raw_owners, syn_owners, packet_owners = defaultdict(set), defaultdict(set), {}
    packet_collisions = set(); path_rows = []
    for r in results:
        sid = r['session_id']
        for h in r['raw_hashes'].values(): raw_owners[h].add(sid)
        for path in r['paths']:
            path_rows.append(dict(path, session_id=sid, protocol=r['protocol']))
            for h in path['syn_signatures']: syn_owners[h].add(sid)
        for h in pd.read_parquet(OUT / 'packet-hashes' / f'{sid}.parquet').sha256:
            if h in packet_owners and packet_owners[h] != sid:
                packet_collisions.add(tuple(sorted([sid, packet_owners[h]])))
            else: packet_owners[h] = sid
    paths = pd.DataFrame(path_rows); paths.to_parquet(OUT / 'path-evidence.parquet', index=False)
    conflicts = {'raw_files': {h:sorted(s) for h,s in raw_owners.items() if len(s)>1},
                 'syn': {h:sorted(s) for h,s in syn_owners.items() if len(s)>1},
                 'positive_packet_session_pairs': sorted(packet_collisions)}
    write(OUT / 'cross-visit-conflicts.json', conflicts)
    summary = {'visits': len(results), 'repeated_raw_hashes': len(conflicts['raw_files']),
               'repeated_syn_signatures': len(conflicts['syn']), 'positive_packet_collision_session_pairs': len(packet_collisions),
               'observable_anchors': sum(r['observable_anchors'] for r in results),
               'failed_observable_anchors': sum(r['failed_observable_anchors'] for r in results),
               'visits_without_observable_anchor': sum(not r['observable_anchors'] for r in results),
               'positive_paths_without_syn': int((paths.positive_packets.gt(0)&paths.syn_count.eq(0)).sum()),
               'positive_paths_with_multiple_syn_sequences': int((paths.positive_packets.gt(0)&paths.syn_count.gt(1)).sum()),
               'multi_owner_packets': sum(c.get('multi_owner_packets',0) for r in results for c in r['counts']),
               'positive_packets_requiring_reassembly_or_review': sum(c.get('positive_packet_requires_reassembly_or_review',0) for r in results for c in r['counts']),
               'training_allowed': False, 'full_TCP_epoch_proof_claimed': False,
               'scope': 'all registered TCP paths; no hashes of empty ACKs, no fragment-reassembled hashes',
               'code_sha256': file_hash(Path(__file__))}
    write(OUT / 'summary.json', summary); print(summary, flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--workers', type=int, default=4)
    main(p.parse_args().workers)
