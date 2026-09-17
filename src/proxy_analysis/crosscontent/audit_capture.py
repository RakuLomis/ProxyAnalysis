"""Read-only capture eligibility audit; no model training or 0914 mixing."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import numpy as np

from ..indexing.pairs import build_exclusive_pairs
from ..pathutils import filesystem_path
from ..reproducibility.registry import discover_runs, read_json
from ..reproducibility.preflight import write_json, write_table


def file_hash(path):
    return hashlib.sha256(Path(filesystem_path(path)).read_bytes()).hexdigest()


def content_key(target):
    url = urlsplit(target['url'])
    query = parse_qs(url.query)
    if target['domain'] == 'youtube.com' and target.get('run_label') == 'video_playback':
        return 'youtube_video:' + query['v'][0]
    if target['domain'] == 'bilibili.com' and target.get('run_label') == 'video_playback':
        return 'bilibili_video:' + url.path.strip('/') + ':p=' + query.get('p', ['1'])[0]
    return target['url']


def analyze(root, out):
    manifest = read_json(root/'pipeline-manifest.json')
    rows = discover_runs(root)
    chosen = [r for r in rows if r['is_final']]
    targets = {t['index']: t for t in manifest['targets']}
    runs = {r['run_id']: r for r in manifest['runs']}
    hashes = {str(root/'pipeline-manifest.json'): file_hash(root/'pipeline-manifest.json')}
    records, pair_records = [], []
    for index, r in enumerate(chosen):
        target, run = targets[r['target_index']], runs[r['run_id']]
        path = Path(filesystem_path(r['session_path']))
        summary_path = path/'analysis/summary.json'
        summary = read_json(summary_path)
        hashes[str(summary_path)] = file_hash(summary_path)
        if summary['session_id'] != r['session_id']:
            raise ValueError('Summary session mismatch')
        activity = summary.get('activity_outcome') or {}
        nav = summary.get('navigation_outcome') or {}
        video = target.get('run_label') == 'video_playback'
        seconds = activity.get('primary_content_seconds')
        primary = activity.get('primary_content_observed') is True or (isinstance(seconds, (int, float)) and seconds > 0)
        valid = primary if video else nav.get('state') == 'passed' and activity.get('state') == 'passed'
        accepted, excluded, errors = [], [], []
        if r['protocol'] != 'HYSTERIA2':
            try:
                for name in ('connection-index-v2.json', 'pcap-index-v1.json'):
                    item = path/'analysis'/name
                    hashes[str(item)] = file_hash(item)
                pairs = build_exclusive_pairs(path, r['protocol'])
                counts = Counter((p.post.entity_id, str(p.post.capture_path)) for p in pairs)
                for pair in pairs:
                    if counts[(pair.post.entity_id, str(pair.post.capture_path))] != 1:
                        excluded.append('outer_reused')
                    elif pair.pre.transport_protocol != 'tcp' or pair.post.transport_protocol != 'tcp':
                        excluded.append('not_tcp')
                    elif not pair.pre.capture_path.is_file() or not pair.post.capture_path.is_file():
                        excluded.append('missing_capture')
                    elif min(pair.pre.capture_path.stat().st_size, pair.post.capture_path.stat().st_size) == 0:
                        excluded.append('zero_byte_capture')
                    else:
                        accepted.append(pair)
                        pair_records.append({'session_id': r['session_id'], 'connection_id': pair.connection_id,
                            'pre_path': str(pair.pre.capture_path), 'post_path': str(pair.post.capture_path),
                            'pre_file_bytes': pair.pre.capture_path.stat().st_size,
                            'post_file_bytes': pair.post.capture_path.stat().st_size})
            except Exception as exc:
                errors.append(str(exc))
        quality = run.get('quality') or {}
        capture_pass = (quality.get('capture_integrity') or {}).get('state') == 'passed'
        record = {k:r[k] for k in ('session_id','target_url','target_domain','protocol','repetition',
                  'target_index','started_at','cache_mode','traffictracer_version','traffictracer_commit',
                  'chronological_attempt','selected_attempt','run_ordinal')}
        record.update(label_id=target['domain']+'::'+target['run_label'],
            content_id=content_key(target), run_label=target['run_label'], page_type=target.get('page_type'),
            run_state=run['state'], activity_state=activity.get('state'), activity_kind=activity.get('kind'),
            activity_reason=activity.get('reason'), navigation_state=nav.get('state'),
            final_url=nav.get('final_url'), final_status=nav.get('final_status'),
            primary_content_observed=activity.get('primary_content_observed'), primary_content_seconds=seconds,
            primary_goal_met=activity.get('primary_goal_met'), automated_label_valid=valid,
            validity_evidence='session_primary_presence' if video else 'navigation_and_activity_pass_not_human_reading',
            capture_integrity_state=(quality.get('capture_integrity') or {}).get('state'),
            correlation_state=(quality.get('correlation') or {}).get('state'),
            application_state=(quality.get('application') or {}).get('state'),
            coverage_state=[x.get('status') for x in summary.get('packet_coverage', [])],
            drops_observation=[str(x.get('drops')) for x in summary.get('packet_coverage', [])],
            accepted_tcp_pairs=len(accepted), excluded_pair_reasons=excluded, audit_errors=errors,
            indexed_pair_candidate=bool(accepted) and not errors,
            joint_candidate=bool(valid and capture_pass and accepted and not errors),
            configured_duration_seconds=target.get('duration_seconds'),
            desired_primary_seconds=(target.get('playback') or {}).get('desired_primary_seconds'),
            resolved_leaf=run.get('resolved_leaf'), observed_protocol=run.get('observed_protocol'),
            profile_fingerprint=run.get('profile_fingerprint'),
            profile_snapshot_changed=run.get('profile_snapshot_changed'))
        records.append(record)
        if (index+1) % 100 == 0:
            print(json.dumps({'audited':index+1,'total':len(chosen)}), flush=True)
    out.mkdir(parents=True, exist_ok=False)
    write_table(out/'run-registry.parquet', rows)
    write_table(out/'session-eligibility.parquet', records)
    write_table(out/'indexed-pair-files.parquet', pair_records)
    write_json(out/'source-hashes.json', hashes)
    grouped = defaultdict(list)
    for r in records:
        grouped[(r['label_id'],r['protocol'])].append(r)
    coverage = []
    for (label, protocol), group in sorted(grouped.items()):
        by_content = defaultdict(list)
        for r in group:
            by_content[r['content_id']].append(r)
        valid_counts = {c:sum(r['joint_candidate'] for r in members) for c,members in by_content.items()}
        seconds = [r['primary_content_seconds'] for r in group if isinstance(r['primary_content_seconds'],(int,float))]
        coverage.append({'label_id':label,'protocol':protocol,'sessions':len(group),'registered_contents':len(by_content),
            'automated_label_valid':sum(r['automated_label_valid'] for r in group),
            'indexed_pair_sessions':sum(r['indexed_pair_candidate'] for r in group),
            'joint_candidate_sessions':sum(r['joint_candidate'] for r in group),
            'joint_candidate_contents':sum(v>0 for v in valid_counts.values()),
            'complete_five_repeat_contents':sum(v==5 for v in valid_counts.values()),
            'valid_repetitions_per_content_json':json.dumps(valid_counts),
            'strict_tcp_design_applicable':protocol!='HYSTERIA2',
            'median_primary_seconds':float(np.median(seconds)) if seconds else None,
            'minimum_primary_seconds':min(seconds) if seconds else None,
            'goal_met':sum(r['primary_goal_met'] is True for r in group),
            'run_states_json':json.dumps(dict(Counter(r['run_state'] for r in group)))})
    write_table(out/'label-protocol-coverage.parquet', coverage)
    degraded = [r for r in records if r['run_state']!='completed' or not r['automated_label_valid'] or r['audit_errors']]
    write_json(out/'exceptions.json', degraded)
    gates = []
    for label in sorted({r['label_id'] for r in records}):
        members = [r for r in records if r['label_id']==label]
        per_protocol = {p:{r['content_id'] for r in members if r['protocol']==p and r['joint_candidate']}
                        for p in ('SHADOWSOCKS','VLESS')}
        common = sorted(per_protocol['SHADOWSOCKS'] & per_protocol['VLESS'])
        gates.append({'label_id':label,'common_ss_vless_contents':common,
                      'five_content_index_gate':len(common)>=5,
                      'full_feature_quality_gate':'pending_packet_extraction',
                      'semantic_independence':'registered_resource_identity_only_needs_review'})
    write_json(out/'business-gates.json', gates)
    result = {'raw_root':str(root),'pipeline_state':manifest['state'],'planned_targets':len(targets),
        'stored_attempts':len(rows),'selected_sessions':len(records),'prior_attempts':len(rows)-len(records),
        'labels':len(gates),'run_states':dict(Counter(r['run_state'] for r in records)),
        'versions':dict(Counter(r['traffictracer_version'] for r in records)),
        'cache_modes':dict(Counter(r['cache_mode'] for r in records)),
        'configured_durations':dict(Counter(r['configured_duration_seconds'] for r in records)),
        'capture_integrity':dict(Counter(r['capture_integrity_state'] for r in records)),
        'correlation':dict(Counter(r['correlation_state'] for r in records)),
        'automated_label_valid':sum(r['automated_label_valid'] for r in records),
        'indexed_pairs':len(pair_records),'joint_candidate_sessions':sum(r['joint_candidate'] for r in records),
        'audit_errors':sum(bool(r['audit_errors']) for r in records),
        'five_content_ss_vless_labels':[g['label_id'] for g in gates if g['five_content_index_gate']],
        'coverage':coverage,'full_packet_feature_extraction':False,'models_trained':False}
    write_json(out/'summary.json', result)
    print(json.dumps({k:v for k,v in result.items() if k!='coverage'},ensure_ascii=False), flush=True)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--raw-root',type=Path,default=Path('Datasets/TrafficTracer-content-generalization-20260916'))
    parser.add_argument('--output-root',type=Path,default=Path('outputs/content-generalization-20260916/audit-01'))
    args=parser.parse_args()
    analyze(args.raw_root,args.output_root)


if __name__=='__main__': main()
