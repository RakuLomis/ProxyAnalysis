"""All-selected-visit descriptive extraction; no classifier or Wireshark features.

Run from the repository root with Pytorch312. Raw datasets and old outputs are read-only.
"""
from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
import hashlib
import json
from pathlib import Path
import sys
import time
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

import numpy as np
import pyarrow.parquet as pq
from scipy.stats import ks_2samp, wasserstein_distance

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from proxy_analysis.config import FeatureConfig
from proxy_analysis.indexing.identities import build_entity_descriptors
from proxy_analysis.indexing.pairs import build_exclusive_pairs
from proxy_analysis.pipeline.analyze_entity import analyze_entity_capture
from proxy_analysis.reproducibility.extract import describe, context_descriptors, analyze_carrier
from proxy_analysis.reproducibility.preflight import write_json, write_table
from proxy_analysis.features.burst import direction_run_bursts
from proxy_analysis.features.pairwise import js_divergence
from proxy_analysis.features.transition import transition_features

OUT = ROOT / 'outputs/itemwise-statistics-0914-0916/run-01'
DOC = ROOT / 'docs/statistics/0914-0916-itemwise'
VERSION = 2


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def resource(url):
    s = urlsplit(url)
    query = parse_qsl(s.query, keep_blank_values=True)
    if s.hostname and s.hostname.endswith('bing.com') and s.path == '/search':
        query = [(k, v) for k, v in query if k.lower() not in {'rdr', 'rdrig'}]
    return urlunsplit((s.scheme.lower(), s.netloc.lower(), s.path or '/', urlencode(sorted(query)), s.fragment))


def registry():
    provenance, rows = {}, []
    def table(p):
        p = ROOT / p
        provenance[str(p)] = sha(p)
        return pq.read_table(p).to_pylist()
    labels14 = {r['session_id']: r for r in table('outputs/replication-20260914/run-01/activity-confirmation-v3/activity-labels.parquet')}
    labels16 = {r['session_id']: r for r in table('outputs/content-generalization-20260916/audit-01/activity-confirmation-20260917/effective-session-eligibility.parquet')}
    for batch, reg, route, labels in [
        ('0914-broad', 'outputs/replication-20260914/run-01/broad/audit/run_registry.parquet', 'outputs/replication-20260914/run-01/broad/audit/routing_eligibility.parquet', labels14),
        ('0914-repeat', 'outputs/replication-20260914/run-01/repeat/audit/run_registry.parquet', 'outputs/replication-20260914/run-01/repeat/audit/routing_eligibility.parquet', labels14),
        ('0916', 'outputs/content-generalization-20260916/audit-01/run-registry.parquet', 'outputs/content-generalization-20260916/audit-01/routing/session-routing.parquet', labels16),
    ]:
        routes = {r['session_id']: r for r in table(route)}
        for r in table(reg):
            label, routing = labels.get(r['session_id'], {}), routes.get(r['session_id'], {})
            activity = label.get('effective_label_id') or label.get('label_id') or f"{r['target_domain']}::unverified"
            # Item identity must not vary with a failed repetition's observed outcome.
            nominal = label.get('activity_kind') or activity.split('::')[-1]
            item_key = f"{batch}|{int(r['target_index'])}|{resource(r['target_url'])}"
            if batch == '0916':
                main_route = ('mixed' if routing.get('exact_target_proxy') and routing.get('exact_target_direct') else
                              'proxy' if routing.get('exact_target_proxy') else
                              'direct' if routing.get('exact_target_direct') else 'unresolved')
                proxy_n, direct_n, unknown_n = [routing.get(k) for k in ('proxy_requests', 'direct_requests', 'unresolved_requests')]
            else:
                main_route = routing.get('main_document_route', 'unresolved')
                proxy_n, direct_n, unknown_n = [routing.get(k) for k in ('proxy_request_count', 'direct_request_count', 'unavailable_request_count')]
            rows.append({**r, 'batch': batch, 'item_id': hashlib.sha256(item_key.encode()).hexdigest()[:16],
                         'resource': resource(r['target_url']), 'label_id': activity, 'activity_kind': nominal,
                         'main_route': main_route, 'proxy_requests': proxy_n, 'direct_requests': direct_n,
                         'unresolved_requests': unknown_n, 'activity_state': label.get('activity_state'),
                         'manual_confirmation': label.get('manual_confirmation_applied', False),
                         'evidence_granularity': label.get('effective_evidence_granularity', label.get('evidence_granularity')),
                         'run_state': label.get('run_state'), 'configured_duration_seconds': label.get('configured_duration_seconds'),
                         'playback_seconds': label.get('primary_content_seconds'),
                         'effective_label_valid': label.get('effective_label_valid', label.get('effective_video_capture_valid'))})
    assert len({r['session_id'] for r in rows}) == len(rows)
    counts = Counter(r['batch'] for r in rows if r['is_final'])
    assert counts == {'0914-broad': 192, '0914-repeat': 270, '0916': 525}, counts
    assert len(rows) == 1002
    write_table(OUT / 'item-registry.parquet', rows)
    write_json(OUT / 'registry-provenance.json', provenance)
    return rows


def stats(values):
    x = np.asarray(values, dtype=float)
    if not len(x):
        return {k: None for k in ('mean', 'std', 'min', 'q25', 'median', 'q75', 'p95', 'max', 'iqr', 'mad')}
    q = np.quantile(x, [.25, .5, .75, .95])
    return dict(mean=float(x.mean()), std=float(x.std()), min=float(x.min()), q25=float(q[0]),
                median=float(q[1]), q75=float(q[2]), p95=float(q[3]), max=float(x.max()),
                iqr=float(q[2]-q[0]), mad=float(np.median(abs(x-q[1]))))


def arrays(groups):
    groups = [sorted(g, key=lambda p: (p.timestamp_ns, p.packet_ordinal)) for g in groups]
    return ([p.transport_payload_len for g in groups for p in g if p.transport_payload_len > 0],
            [(b.timestamp_ns-a.timestamp_ns)/1000 for g in groups for a, b in zip(g, g[1:])])


def extended(groups, cfg, analyses=()):
    groups = [sorted(g, key=lambda p: (p.timestamp_ns, p.packet_ordinal)) for g in groups if g]
    d = describe(groups, cfg)
    if not d:
        return d
    packets = [p for g in groups for p in g]
    lengths, iats = arrays(groups)
    d['duration_s'] = (d['last_ns']-d['first_ns'])/1e9
    d['up_packets'] = sum(p.direction == 1 for p in packets)
    d['down_packets'] = len(packets)-d['up_packets']
    d['up_ip_bytes'] = sum(p.ip_total_len for p in packets if p.direction == 1)
    d['down_ip_bytes'] = d['ip_bytes']-d['up_ip_bytes']
    d['offload_suspect_fraction'] = sum(p.ip_total_len > 1500 for p in packets)/len(packets)
    d['zero_iat_fraction'] = d['zero_iat_count']/len(iats) if iats else None
    d['nonempty_entity_count'] = sum(any(p.transport_payload_len > 0 for p in g) for g in groups)
    denom = d['nonempty_packets']-d['nonempty_entity_count']
    d['fr_switches_per_possible_transition'] = d['fr_switches']/denom if denom else None
    transitions = [transition_features(p.direction for p in g if p.transport_payload_len) for g in groups]
    ns = [sum(getattr(t, 'n_'+k) for t in transitions) for k in ('pp', 'pm', 'mp', 'mm')]
    d.update({'transition_n_'+k: n for k, n in zip(('pp', 'pm', 'mp', 'mm'), ns)})
    probs = []
    for i, k in enumerate(('pp', 'pm', 'mp', 'mm')):
        den = sum(ns[:2]) if i < 2 else sum(ns[2:])
        val = ns[i]/den if den else None
        d['transition_p_'+k] = val
        if val:
            probs.append(-ns[i]/sum(ns)*np.log2(val))
    d['transition_entropy'] = float(sum(probs)) if sum(ns) else None
    bursts = [b for g in groups for b in direction_run_bursts(g)]
    for direction, prefix in [(1, 'up'), (-1, 'down')]:
        d[prefix+'_burst_count'] = sum(b.direction == direction for b in bursts)
    for name, values in [('length', lengths), ('iat_us', iats),
                         ('burst_packets', [b.packet_count for b in bursts]),
                         ('burst_bytes', [b.transport_payload_bytes for b in bursts]),
                         ('burst_duration_ms', [b.duration_ns/1e6 for b in bursts])]:
        d.update({name+'_'+k: v for k, v in stats(values).items()})
    # Occupancy of observed connection spans, not HTTP-request concurrency.
    events = sorted([(g[0].timestamp_ns, 1) for g in groups]+[(g[-1].timestamp_ns, -1) for g in groups], key=lambda a: (a[0], -a[1]))
    current = maximum = 0
    for _, sign in events:
        current += sign
        maximum = max(maximum, current)
    d['connection_span_concurrency_max'] = maximum
    for ms in (100, 500, 1000):
        threshold = ms*1000
        d[f'idle_gap_count_{ms}ms'] = sum(t > threshold for t in iats)
        d[f'idle_gap_sum_s_{ms}ms'] = sum(t for t in iats if t > threshold)/1e6
        d[f'active_span_sum_s_{ms}ms'] = sum(t for t in iats if t <= threshold)/1e6
    ids = {p.packet_event_id for p in packets}
    tcp = [p for a in analyses for p in a.tcp_packets if p.packet_event_id in ids]
    samples = [s.rtt_ns/1e6 for a in analyses if a.tcp for s in a.tcp.rtt_samples
               if s.ack_packet_event_id in ids and s.acknowledged_packet_event_id in ids]
    d['tcp_packet_count'] = len(tcp)
    d['rtt_sample_count'] = len(samples)
    d['rtt_median_ms'] = float(np.median(samples)) if samples else None
    d['tcp_window_raw_median'] = float(np.median([p.window_raw for p in tcp])) if tcp else None
    for flag, mask in [('syn', 2), ('fin', 1), ('rst', 4), ('ack', 16)]:
        d['tcp_'+flag+'_count'] = sum(bool(p.flags & mask) for p in tcp) if tcp else None
    d['full_retransmission_packets'] = sum(p.tcp_classification == 'full_retransmission' for p in packets) if tcp else None
    d['full_retransmission_fraction'] = d['full_retransmission_packets']/len(tcp) if tcp else None
    return d


def distances(pre, post, before, after):
    if not before or not after:
        return {}
    a, ai = arrays(pre)
    b, bi = arrays(post)
    out = {}
    for prefix, x, y, key in [('length', a, b, 'length_hist'), ('iat', ai, bi, 'iat_hist')]:
        if x and y:
            out[prefix+'_js'] = js_divergence(before[key], after[key])
            out[prefix+'_ks'] = float(ks_2samp(x, y, method='asymp').statistic)
            out[prefix+'_wasserstein'+('_log1p_us' if prefix == 'iat' else '_bytes')] = float(
                wasserstein_distance(np.log1p(x) if prefix == 'iat' else x,
                                     np.log1p(y) if prefix == 'iat' else y))
    if before.get('curve') is not None and after.get('curve') is not None:
        delta = np.abs(np.array(before['curve'])-np.array(after['curve']))
        out.update(cumulative_l1=float(delta.mean()), cumulative_max=float(delta.max()))
    return out


def extract_visit(row):
    sid, path = row['session_id'], Path(row['session_path'])
    dest = OUT / 'sessions' / (sid+'.json')
    if dest.exists():
        old = read(dest)
        if old.get('version') == VERSION:
            # A checkpoint is usable only for exactly the same captured inputs.
            changed = [p for p, digest in old.get('sources', {}).items()
                       if not Path(p).is_file() or sha(p) != digest]
            if changed:
                raise ValueError(f'Frozen source changed; use a new output run: {changed[:3]}')
            return sid, 'cached', len(old.get('errors', []))
    cfg = FeatureConfig.load(ROOT / 'configs/feature-defaults.yaml')
    result = {'version': VERSION, 'session_id': sid, 'scopes': [], 'errors': [], 'sources': {}, 'captures': [], 'sequences': []}
    cache = {}
    def load(desc):
        key = (desc.capture_side, desc.entity_id, str(desc.capture_path))
        if key not in cache:
            analysis = analyze_carrier(desc, path) if desc.entity_level == 'carrier' else analyze_entity_capture(desc)
            if analysis.unknown_direction_count or analysis.packet_count != len(analysis.packet_measures):
                raise ValueError(f'incomplete decoding/direction: {desc.entity_id}')
            cache[key] = analysis
            result['sources'][str(desc.capture_path)] = sha(desc.capture_path)
            result['captures'].append({'side': desc.capture_side, 'entity_id': desc.entity_id,
                'transport': desc.transport_protocol, 'route': desc.egress_outcome,
                'timestamp_regressions': sum(b.timestamp_ns < a.timestamp_ns for a, b in zip(analysis.packet_measures, analysis.packet_measures[1:])),
                'packet_count': analysis.packet_count, 'path': str(desc.capture_path)})
            ps = sorted(analysis.packet_measures, key=lambda p: (p.timestamp_ns, p.packet_ordinal))[:32]
            result['sequences'].append({'side': desc.capture_side, 'entity_id': desc.entity_id,
                'direction': [p.direction for p in ps], 'signed_length': [p.direction*p.transport_payload_len for p in ps],
                'iat_us': [None]+[(b.timestamp_ns-a.timestamp_ns)/1000 for a, b in zip(ps, ps[1:])] if ps else []})
        return cache[key]
    try:
        for filename in ('manifest.json', 'analysis/summary.json', 'analysis/connection-index-v2.json', 'analysis/pcap-index-v1.json', 'analysis/flow-index.json', 'raw/mihomo-trace.jsonl'):
            if (path/filename).exists():
                result['sources'][str(path/filename)] = sha(path/filename)
        descriptors = build_entity_descriptors(path, row['protocol'])
        result['indexed_entity_count'] = len(descriptors)
        result['indexed_pre_count'] = sum(d.capture_side == 'pre' for d in descriptors)
        result['indexed_route_counts'] = dict(Counter(d.egress_outcome for d in descriptors if d.capture_side == 'pre'))
        if row['protocol'] == 'HYSTERIA2':
            ctx = context_descriptors(path)
            post = [d for d in ctx if d.capture_side == 'post']
            members = {x for d in post for x in d.logical_connection_ids}
            pre = [d for d in ctx if d.capture_side == 'pre' and d.entity_id in members]
            scope = 'carrier_context_full'
        else:
            pairs = build_exclusive_pairs(path, row['protocol'])
            cnt = Counter((p.post.entity_id, str(p.post.capture_path)) for p in pairs)
            accepted = [p for p in pairs if cnt[(p.post.entity_id, str(p.post.capture_path))] == 1
                        and p.pre.transport_protocol == p.post.transport_protocol == 'tcp']
            result['excluded_pair_count'] = len(pairs)-len(accepted)
            pre, post = [p.pre for p in accepted], [p.post for p in accepted]
            scope = 'exclusive_page'
        scopes = [(scope, pre, post)]
        direct = [d for d in descriptors if d.capture_side == 'pre' and d.egress_outcome == 'direct']
        if direct:
            scopes.append(('direct_pre_only', direct, []))
        for scope, pre_desc, post_desc in scopes:
            try:
                pre_a, post_a = [load(d) for d in pre_desc], [load(d) for d in post_desc]
                pg, qg = [list(a.packet_measures) for a in pre_a], [list(a.packet_measures) for a in post_a]
                for selection in ('observed', 'nonempty', 'exclude_full_retransmission'):
                    def select(gs):
                        return [[p for p in g if (selection != 'nonempty' or p.transport_payload_len > 0)
                                 and (selection != 'exclude_full_retransmission' or p.tcp_classification != 'full_retransmission')]
                                for g in gs]
                    pgs, qgs = select(pg), select(qg)
                    before = extended(pgs, cfg, pre_a)
                    windows = [(scope, qgs)]
                    if scope == 'carrier_context_full':
                        windows.append(('carrier_context_envelope', [[p for p in g if before and before['first_ns'] <= p.timestamp_ns <= before['last_ns']] for g in qgs]))
                    for name, window in windows:
                        after = extended(window, cfg, post_a)
                        if name.startswith('carrier'):
                            # Do not call UDP direction runs the original TCP FR.
                            for d in (before, after):
                                for k in list(d):
                                    if k.startswith('fr_'):
                                        d['direction_run_analog_'+k[3:]] = d.pop(k)
                        result['scopes'].append({'scope': name, 'selection': selection, 'pre': dict(before), 'post': after,
                            'distances': distances(pgs, window, before, after),
                            'mapped_logical_connections_per_carrier': len(pre_desc)/len(post_desc) if scope.startswith('carrier') and post_desc else None})
            except Exception as exc:
                result['errors'].append({'scope': scope, 'error': repr(exc)})
    except Exception as exc:
        result['errors'].append({'scope': 'visit', 'error': repr(exc)})
    write_json(dest, result)
    return sid, 'extracted', len(result['errors'])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--limit', type=int)
    args = parser.parse_args()
    rows = registry()
    selected = [r for r in rows if r['is_final']]
    if args.limit:
        selected = selected[:args.limit]
    start = time.time()
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(extract_visit, r) for r in selected]
        errors = 0
        for i, f in enumerate(as_completed(futures), 1):
            sid, state, n = f.result()
            errors += n
            if i % 10 == 0 or n or i == len(selected):
                print(f'{i}/{len(selected)} {state} errors={errors} elapsed={time.time()-start:.1f}s {sid}', flush=True)
    write_json(OUT/'extraction-status.json', {'selected': len(selected), 'errors': errors, 'seconds': time.time()-start})


if __name__ == '__main__':
    main()
