"""Metadata gate for moved TrafficTracer bundles; never mutates captures."""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
from pathlib import Path
import shutil
import subprocess
import sys

import yaml

from ..information_validation.data import classify_activity, digest
from ..inventory import InventoryScanner, inventory_summary
from ..reproducibility.registry import discover_runs, read_json
from ..reproducibility.preflight import write_json, write_table
from ..reproducibility.metadata_report import document_route


def target_contract(pipeline):
    targets = []
    for t in pipeline['targets']:
        content = {'domain': t['domain'], 'url': t['url']}
        workload = {k: v for k, v in t.items() if k != 'index'}
        h = lambda x: hashlib.sha256(json.dumps(x, sort_keys=True).encode()).hexdigest()
        targets.append({**t, 'target_key': f"{pipeline['pipeline_id']}:{t['index']}",
                        'content_key': h(content), 'workload_contract_sha256': h(workload),
                        'configured_activity': 'video_playback' if t.get('playback') else 'page_load'})
    if len({t['target_key'] for t in targets}) != len(targets):
        raise ValueError('duplicate target identity')
    return {'schema_version': 1, 'pipeline_id': pipeline['pipeline_id'], 'sites': targets}


def audit_batch(raw, out, specification):
    out.mkdir(parents=True, exist_ok=True)
    registry = discover_runs(raw)
    selected = [r for r in registry if r['is_selected']]
    if len(registry) != specification['expected_attempts'] or len(selected) != specification['expected_selected']:
        raise ValueError('unexpected registry counts')
    write_table(out/'run_registry.parquet', registry)
    write_json(out/'selected-session-ids.json', [r['session_id'] for r in selected])
    pipeline = read_json(raw/'pipeline-manifest.json')
    contract = target_contract(pipeline)
    write_json(out/'target-contract.json', contract)
    inventory = InventoryScanner(raw).scan()
    if {s.session_id for s in inventory} != {r['session_id'] for r in selected}:
        raise ValueError('inventory and selected registry disagree')
    write_json(out/'inventory-summary.json', inventory_summary(inventory))
    evidence, quality, files = [], [], []
    targets = {t['index']: t for t in contract['sites']}
    for row in selected:
        sid = row['session_id']; path = Path(row['session_path'])
        summary = read_json(path/'analysis/summary.json')
        if summary['session_id'] != sid:
            raise ValueError('summary identity mismatch')
        state = json.loads(row['quality_json'])
        reasons = [k + ':' + state.get(k, {}).get('state', 'unavailable')
                   for k in ['local_runtime','capture_integrity','correlation','application']
                   if state.get(k, {}).get('state') not in {'passed', 'not_applicable'}]
        connections = read_json(path/'analysis/connection-index-v2.json')['items']
        requests = read_json(path/'analysis/request-index-v2.json')['items']
        route = document_route(requests, connections, summary.get('navigation_outcome', {}))
        status = classify_activity(summary)
        t = targets[row['target_index']]
        route_count = Counter(c.get('egress', {}).get('outcome') for c in connections)
        evidence.append({'session_id': sid, 'target_key': row['target_key'],
            'content_key': t['content_key'], 'target_domain': row['target_domain'],
            'target_url': row['target_url'], 'protocol': row['protocol'], 'repetition': row['repetition'],
            'configured_activity': t['configured_activity'], 'page_type': t.get('page_type'),
            'duration_seconds': t.get('duration_seconds'), **status, **route,
            'proxy_connections': route_count['proxy'], 'direct_connections': route_count['direct'],
            'metadata_quality_passed': not reasons,
            'source_sha256': digest(path/'analysis/summary.json'),
            'source_path': str(path/'analysis/summary.json'),
            'interpretation': 'metadata_only_not_independent_packet_audit'})
        quality.append({'session_id': sid, 'target_key': row['target_key'], 'protocol': row['protocol'],
            'repetition': row['repetition'], 'target_domain': row['target_domain'], 'reasons': reasons,
            'application_reason': summary.get('activity_outcome', {}).get('reason'),
            'quality_json': row['quality_json'], 'analysis_integrity_json': json.dumps(summary.get('analysis_integrity')),
            'warnings_json': json.dumps(summary.get('warnings')), 'consistency_json': json.dumps(summary.get('consistency'))})
        for name in ['raw/tun.pcap', 'raw/phys.pcap']:
            f = path/name
            files.append({'session_id': sid, 'path': str(f), 'bytes': f.stat().st_size, 'mtime_ns': f.stat().st_mtime_ns})
    write_table(out/'label-route-evidence.parquet', evidence)
    write_table(out/'quality-reasons.parquet', quality)
    write_table(out/'raw-file-inventory.parquet', files)
    result = {'registered': len(registry), 'selected': len(selected),
        'raw_capture_bytes': sum(r['bytes'] for r in files),
        'metadata_quality_passed': sum(not r['reasons'] for r in quality),
        'playback_verified': sum(r['playback_verified'] for r in evidence),
        'capture_version': dict(Counter(r['traffictracer_version'] for r in selected)),
        'selected_first_after_retry': [r['session_id'] for r in selected
            if r['is_first_attempt'] and sum(a['run_id']==r['run_id'] for a in registry)>1]}
    write_json(out/'metadata-summary.json', result)
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config', type=Path, default=Path('configs/replication-20260914.yaml'))
    p.add_argument('--output-root', type=Path, required=True)
    args = p.parse_args()
    cfg = yaml.safe_load(args.config.read_text(encoding='utf-8'))
    args.output_root.mkdir(parents=True, exist_ok=False)
    state = subprocess.run(['git','-c',f'safe.directory={Path.cwd().as_posix()}','status','--short'],
                           check=True,capture_output=True,text=True).stdout
    tracked = [args.config, *Path('src/proxy_analysis').rglob('*.py'), *Path('tests').rglob('*.py')]
    tracked += [Path(cfg['bundle_root'])/b['directory']/'pipeline-manifest.json' for b in cfg['batches'].values()]
    write_json(args.output_root/'provenance.json', {'time': datetime.now(timezone.utc).isoformat(),
        'python': sys.executable, 'version': sys.version, 'config': cfg, 'git_status': state,
        'hashes': {str(f): digest(f) for f in tracked},
        'packages': {k: importlib.metadata.version(k) for k in ['numpy','scipy','scikit-learn','pyarrow','PyYAML','pytest']},
        'disk_free_bytes': shutil.disk_usage(args.output_root).free})
    results = {}
    for batch, spec in cfg['batches'].items():
        print('metadata audit', batch, flush=True)
        results[batch] = audit_batch(Path(cfg['bundle_root'])/spec['directory'], args.output_root/batch/'audit', spec)
        print(results[batch], flush=True)
    write_json(args.output_root/'metadata-summary.json', results)


if __name__ == '__main__': main()
