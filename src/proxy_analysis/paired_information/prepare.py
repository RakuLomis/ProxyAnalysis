"""Fail-closed sources, audited cohorts, and replayable two-sided summaries."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import time

import numpy as np
import pyarrow.parquet as pq
import yaml
from sklearn.metrics import balanced_accuracy_score, f1_score

from ..config import FeatureConfig
from ..information_validation.data import digest
from ..indexing.identities import build_entity_descriptors
from ..reproducibility.extract import extract_one
from ..reproducibility.preflight import write_json, write_table


def canonical(path):
    # Existing registries store long-path Windows names; compare resolved paths.
    value = str(path)
    if value.startswith('\\\\?\\'):
        value = value[4:]
    return Path(value).resolve()


def guarded(path, root):
    original = Path(path)
    path, root = canonical(path), canonical(root)
    if not path.is_relative_to(root) or 'comparison' in path.relative_to(root).parts:
        raise ValueError(f'non-0914 or mixed source: {path}')
    if not original.is_file():
        raise ValueError(f'missing source: {path}')
    return original


def load_config(path):
    cfg = yaml.safe_load(Path(path).read_text(encoding='utf-8'))
    if canonical(cfg['raw_root']) != canonical('Datasets/TrafficTracer-Datasets-20260914'):
        raise ValueError('raw root must be 0914')
    if canonical(cfg['input_root']) != canonical('outputs/replication-20260914/run-01'):
        raise ValueError('input root must be audited 0914 run')
    if cfg['protocols'] != ['SHADOWSOCKS', 'VLESS'] or cfg['scope'] != 'exclusive_page':
        raise ValueError('unsupported primary scope')
    return cfg


def table(path):
    return pq.read_table(path).to_pylist()


def metrics(rows):
    y = np.asarray([r['truth'] for r in rows])
    p = np.clip([r['prob_vless'] for r in rows], 1e-12, 1-1e-12)
    return {'n': len(rows), 'macro_f1': float(f1_score(y, p >= .5, average='macro')),
            'balanced_accuracy': float(balanced_accuracy_score(y, p >= .5)),
            'log_loss_bits': float(np.mean(-(y*np.log2(p)+(1-y)*np.log2(1-p)))),
            'brier': float(np.mean((p-y)**2))}


def prepare(cfg):
    raw, root, out = map(Path, (cfg['raw_root'], cfg['input_root'], cfg['output_root']))
    sources = {}

    def read(relative):
        source = guarded(root / relative, root)
        sources[str(source)] = digest(source)
        return table(source)

    registry = []
    for batch, relative in [('repeat', 'repeat/audit/run_registry.parquet'),
                            ('broad', 'broad/audit/run_registry.parquet')]:
        rows = read(relative)
        for row in rows:
            summary = guarded(Path(row['session_path']) / 'analysis/summary.json', raw)
            payload = json.loads(summary.read_text(encoding='utf-8'))
            if payload['session_id'] != row['session_id']:
                raise ValueError('raw session identity mismatch')
            sources[str(summary)] = digest(summary)
            registry.append({**row, 'batch': batch})
    by_id = {r['session_id']: r for r in registry}
    if len(by_id) != len(registry):
        raise ValueError('duplicate registry session')
    labels = read('activity-confirmation-v3/activity-labels.parquet')
    for label in labels:
        original = by_id[label['session_id']]
        for field in ('batch', 'target_url', 'target_domain', 'protocol', 'repetition'):
            if original[field] != label[field]:
                raise ValueError(f'label identity mismatch: {field}')
        source = guarded(label['evidence_path'], raw)
        if digest(source) != label['evidence_sha256']:
            raise ValueError('label evidence changed')
    if {r['session_id'] for r in labels} != {r['session_id'] for r in registry if r['is_final']}:
        raise ValueError('label/selected coverage mismatch')
    long = read('repeat/audit/repeat_feature_long.parquet')
    routes = {r['session_id']: r for r in read('repeat/audit/routing_eligibility.parquet')}
    spec = yaml.safe_load(Path(cfg['spec']).read_text(encoding='utf-8'))
    wanted = {m['id'] for m in spec['metrics']}
    indexed = defaultdict(dict)
    for row in long:
        original = by_id[row['session_id']]
        if original['batch'] != 'repeat':
            raise ValueError('non-repeat feature')
        for key in ('protocol', 'repetition', 'activity_id', 'target_domain', 'is_final'):
            if row[key] != original[key]:
                raise ValueError(f'feature identity mismatch: {key}')
        if row['scope'] == cfg['scope'] and row['selection'] == cfg['selection']:
            target = indexed[row['session_id']]
            if row['metric'] in target:
                raise ValueError('duplicate feature')
            target[row['metric']] = row
    repeat = [r for r in registry if r['batch'] == 'repeat']
    reasons, cells = {}, defaultdict(list)
    for row in repeat:
        sid = row['session_id']; why = []
        if not row['is_final']: why.append('historical_attempt')
        if row['protocol'] not in cfg['protocols']: why.append('carrier_context_not_primary')
        if not routes.get(sid, {}).get('page_context_candidate'): why.append('route_or_quality')
        feature = indexed[sid]
        if set(feature) != wanted: why.append('missing_feature_records')
        elif feature['entity_count']['pre'] is None or feature['entity_count']['post'] is None:
            why.append('no_usable_exclusive_side')
        reasons[sid] = why
        if not why: cells[row['target_url']].append((row['protocol'], row['repetition']))
    required = {(p, r) for p in cfg['protocols'] for r in range(1, 6)}
    for values in cells.values():
        if len(values) != len(set(values)): raise ValueError('duplicate target cell')
    complete = {u for u, values in cells.items() if set(values) == required}
    cohort, exclusions = [], []
    for row in repeat:
        why = reasons[row['session_id']].copy()
        if not why and row['target_url'] not in complete: why.append('incomplete_grid')
        exclusions.append({'session_id': row['session_id'], 'included': not why, 'reasons': why})
        if not why: cohort.append(row)
    old_membership = read('repeat/information-validation/cohort-membership.parquet')
    expected = {r['session_id'] for r in old_membership if r['setting']=='primary' and r['included']}
    if expected != {r['session_id'] for r in cohort}:
        raise ValueError('reconstructed cohort differs from audited primary')
    predictions = read('repeat/information-validation/classification-oof.parquet')
    groups = defaultdict(list)
    for row in predictions:
        if row['session_id'] not in by_id: raise ValueError('orphan prediction')
        if row['setting'] == 'primary':
            if row['session_id'] not in expected: raise ValueError('unexpected primary prediction')
            if row['truth'] != int(by_id[row['session_id']]['protocol'] == 'VLESS'):
                raise ValueError('prediction truth mismatch')
            groups[(row['scheme'], row['view'], row['model'])].append(row)
    baseline = []
    for key, rows in groups.items():
        if len({r['session_id'] for r in rows}) != len(rows) or len(rows) != len(cohort):
            raise ValueError('OOF coverage mismatch')
        baseline.append(dict(zip(('scheme', 'view', 'model'), key)) | metrics(rows))
    coverage = defaultdict(list)
    for row in labels:
        coverage[(row['batch'], row['effective_label_id'], row['protocol'])].append(row)
    cover = [{'batch': k[0], 'label': k[1], 'protocol': k[2], 'sessions': len(v),
              'distinct_urls_not_semantically_validated': len({r['target_url'] for r in v}),
              'urls': sorted({r['target_url'] for r in v}),
              'manual_confirmations': sum(r['manual_confirmation_applied'] for r in v)}
             for k, v in coverage.items()]
    out.mkdir(parents=True, exist_ok=False)
    for name, rows in [('registry', registry), ('labels', labels), ('cohort', cohort),
                       ('exclusions', exclusions), ('baseline-recheck', baseline),
                       ('activity-content-coverage', cover)]:
        write_table(out / f'{name}.parquet', rows)
    write_json(out/'source-manifest.json', {'sources': sources, 'config': cfg,
               'primary_sessions': len(cohort), 'primary_urls': len(complete),
               'raw_root': str(canonical(raw)), 'old_data_used': False})
    write_json(out/'config.json', cfg)
    print(json.dumps({'primary_sessions': len(cohort), 'primary_urls': len(complete),
                      'registry': len(registry), 'labels': len(labels)}, indent=2), flush=True)


def assert_replay(actual, expected):
    if len(actual) != len(expected): raise ValueError('replay length mismatch')
    for a, e in zip(actual, expected):
        for key in ('metric', 'reason', 'scope', 'selection'):
            if a[key] != e[key]: raise ValueError(f'replay identity: {key}')
        for key in ('pre', 'post', 'delta', 'delta_smoothed'):
            if (a[key] is None) != (e[key] is None): raise ValueError(f'replay null: {key}')
            if a[key] is not None and not np.isclose(a[key], e[key], rtol=1e-10, atol=1e-12):
                raise ValueError(f'replay numeric: {key} {a["metric"]}')


def summaries(cfg, limit=None):
    out = Path(cfg['output_root']); root = Path(cfg['input_root']); raw = Path(cfg['raw_root'])
    if json.loads((out/'config.json').read_text()) != cfg: raise ValueError('configuration changed')
    fc = FeatureConfig.load(cfg['feature_config'])
    spec = yaml.safe_load(Path(cfg['spec']).read_text(encoding='utf-8'))
    rows = sorted(table(out/'cohort.parquet'), key=lambda r: r['session_id'])
    if limit: rows = rows[:limit]
    destination = out/'sessions'; destination.mkdir(exist_ok=True)
    all_sides, audit = [], []
    for index, row in enumerate(rows, 1):
        started = time.perf_counter(); path = Path(row['session_path'])
        guarded(path/'manifest.json', raw)
        sources = [path/'manifest.json', path/'analysis/connection-index-v2.json',
                   path/'analysis/pcap-index-v1.json']
        for desc in build_entity_descriptors(path, row['protocol']):
            sources.append(guarded(desc.capture_path, raw))
        hashes = {str(guarded(p, raw)): digest(p) for p in set(sources)}
        hashes['extract_code'] = digest(Path(__file__).parents[1]/'reproducibility/extract.py')
        hashes['driver_code'] = digest(Path(__file__))
        hashes['feature_config'] = fc.sha256
        hashes['spec'] = digest(Path(cfg['spec']))
        fingerprint = hashlib.sha256(json.dumps(hashes, sort_keys=True).encode()).hexdigest()
        cache_path = destination/(row['session_id']+'.json')
        cache = json.loads(cache_path.read_text()) if cache_path.exists() else {}
        if cache.get('fingerprint') != fingerprint:
            side = []
            value = extract_one(row, fc, spec['metrics'], side_summary_sink=side)
            prior = guarded(root/'repeat/audit/repeat-feature-sessions'/(row['session_id']+'.json'), root)
            expected = json.loads(prior.read_text())['comparisons']
            assert_replay(value['comparisons'], expected)
            cache = {'fingerprint': fingerprint, 'sources': hashes, 'side_summaries': side,
                     'replay_comparisons': len(expected), 'reference_sha256': digest(prior)}
            write_json(cache_path, cache)
        for side in cache['side_summaries']:
            all_sides.append({'session_id': row['session_id'], 'target_url': row['target_url'],
                              'protocol': row['protocol'], 'repetition': row['repetition'], **side})
        audit.append({'session_id': row['session_id'], 'fingerprint': fingerprint,
                      'comparisons': cache['replay_comparisons'], 'passed': True})
        print(f'[{index}/{len(rows)}] {row["target_domain"]} {row["protocol"]} '
              f'r{row["repetition"]} {time.perf_counter()-started:.2f}s', flush=True)
    suffix = '-smoke' if limit else ''
    write_table(out/f'side-summaries{suffix}.parquet', all_sides)
    write_json(out/f'true-pair-replay-audit{suffix}.json', audit)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', default='configs/paired-information-0914.yaml')
    parser.add_argument('--stage', choices=['prepare', 'summaries'], required=True)
    parser.add_argument('--limit', type=int)
    args = parser.parse_args(); cfg = load_config(args.config)
    if args.stage == 'prepare': prepare(cfg)
    else: summaries(cfg, args.limit)


if __name__ == '__main__': main()
