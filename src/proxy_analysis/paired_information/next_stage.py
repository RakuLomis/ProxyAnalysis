"""Frozen next-stage entry points. Every mode creates a new output directory."""
from __future__ import annotations

import argparse
import copy
import json
import platform
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
import sklearn
import yaml

from ..reproducibility.preflight import write_json, write_table
from .prepare import digest, metrics, table
from .reference_retrain import (build_matrix, inner_indices, reference_evaluate,
                                scalar_spec, assert_partition)


def load(path):
    cfg = yaml.safe_load(Path(path).read_text(encoding='utf-8'))
    if Path(cfg['raw_root']).resolve() != Path('Datasets/TrafficTracer-Datasets-20260914').resolve():
        raise ValueError('Only 0914 is authorized')
    if cfg['business_teacher_training_enabled']:
        raise ValueError('Business training requires a separate approved eligibility gate')
    return cfg


def data(cfg):
    root = Path(cfg['source_root'])
    rows = [r for r in table(root/'side-summaries.parquet')
            if r['selection'] == cfg['primary_selection'] and r['scope'] == cfg['scope']]
    expected = {r['session_id'] for r in table(root/'cohort.parquet')}
    if len(rows) != 140 or len(expected) != 140 or {r['session_id'] for r in rows} != expected:
        raise ValueError('Primary cohort changed')
    if {r['protocol'] for r in rows} != {'SHADOWSOCKS', 'VLESS'}:
        raise ValueError('Unexpected primary deployment')
    spec = yaml.safe_load(Path(cfg['spec']).read_text(encoding='utf-8'))['metrics']
    scalar_spec(spec)
    return rows, spec


def freeze(cfg, config_path):
    source = Path(cfg['source_root'])
    out = Path(cfg['output_root'])
    rows, spec = data(cfg)
    paths = [Path(config_path), Path(cfg['spec'])]
    paths += list(Path('src/proxy_analysis').rglob('*.py'))
    paths += [source/name for name in ('side-summaries.parquet', 'cohort.parquet',
              'labels.parquet', 'registry.parquet', 'source-manifest.json',
              'execution-diagnostics/session-execution.parquet')]
    for batch in ('broad', 'repeat'):
        paths += [Path(cfg['audit_root'])/batch/'audit'/name for name in
                  ('routing_eligibility.parquet', 'cohort_eligibility.parquet')]
    original = json.loads((source/'source-manifest.json').read_text(encoding='utf-8'))
    for path, expected in original['sources'].items():
        if digest(Path(path)) != expected:
            raise ValueError(f'Original source changed: {path}')
    hashes = {str(path): digest(path) for path in sorted(set(paths))}
    out.mkdir(parents=True, exist_ok=False)
    write_json(out/'contract.json', {
        'config': cfg, 'sources': hashes, 'config_path': str(config_path),
        'original_source_manifest_verified': True,
        'environment': {'python': platform.python_version(), 'sklearn': sklearn.__version__},
        'interpretation': 'retrospective_0914_internal_refitting_not_external_validation',
        'raw_connection_identity_audit': 'pending_persisted_reexecution',
        'budget': {'inner_partition_seeds': 10, 'wrong_seeds': 10,
                   'bootstrap_training_groups': 20, 'wrong_seeds_per_bootstrap': 5},
    })
    columns = [m['id'] for m in scalar_spec(spec)]
    write_json(out/'feature-allowlist.json', {
        'pre': ['pre.'+x for x in columns], 'post': ['post.'+x for x in columns],
        'joint_scalar': ['pre.'+x for x in columns]+['post.'+x for x in columns],
        'delta_scalar': [m['transform']+'(post,pre).'+m['id'] for m in scalar_spec(spec)],
        'note': 'ip_bytes is total IP byte volume, not an address; captured_bytes excluded',
    })
    invariants = []
    altered = copy.deepcopy(rows)
    for r in altered:
        r.update(session_id='metadata_mutation', protocol='metadata_mutation', target_url='metadata_mutation')
        for side in ('pre', 'post'):
            r[side].update(ip_src='secret', ip_dst='secret', src_port=1, dst_port=2,
                           sni='secret', mac_address='secret', captured_bytes=123456789)
    for view in ('pre', 'post', 'joint_scalar', 'delta_scalar'):
        np.testing.assert_equal(build_matrix(rows, spec, view), build_matrix(altered, spec, view))
        invariants.append({'view': view, 'metadata_mutation_invariant': True,
                           'n_features': build_matrix(rows, spec, view).shape[1]})
    write_json(out/'input-audit.json', invariants)
    splits = []
    for seed in cfg['inner_partition_seeds']:
        for url in sorted({r['target_url'] for r in rows}):
            train = [r for r in rows if r['target_url'] != url]
            test = [r for r in rows if r['target_url'] == url]
            for fold, (tr, va) in enumerate(inner_indices(train, seed)):
                a, b = [train[i] for i in tr], [train[i] for i in va]
                assert_partition(a, b, test)
                splits.append({'partition_seed': seed, 'outer_url': url, 'inner_fold': fold,
                               'train_ids': [r['session_id'] for r in a],
                               'validation_ids': [r['session_id'] for r in b],
                               'test_ids': [r['session_id'] for r in test]})
    write_json(out/'split-manifest.json', splits)
    print(json.dumps({'phase': 'freeze', 'sessions': len(rows), 'split_records': len(splits)}), flush=True)


def verify(cfg):
    contract = json.loads((Path(cfg['output_root'])/'contract.json').read_text(encoding='utf-8'))
    if contract['config'] != cfg:
        raise ValueError('Frozen configuration changed')
    for path, expected in contract['sources'].items():
        if digest(Path(path)) != expected:
            raise ValueError(f'Frozen source changed: {path}; use a new run')


def reference(cfg):
    verify(cfg)
    rows, spec = data(cfg)
    out = Path(cfg['output_root'])/'reference-retrain'
    out.mkdir(exist_ok=False)
    results = []
    for view in ('pre', 'post', 'joint_scalar', 'delta_scalar'):
        start = time.perf_counter()
        predictions, tuning, splits = reference_evaluate(rows, spec, view, cfg)
        # Old OOF is read only AFTER the fresh fits have finished.
        old = {r['session_id']: r for r in table(Path(cfg['source_root'])/'views'/f'{view}-oof.parquet')}
        if set(old) != {r['session_id'] for r in predictions}:
            raise ValueError('Reference OOF membership mismatch')
        max_diff = max(abs(r['prob_vless'] - old[r['session_id']]['prob_vless']) for r in predictions)
        c_equal = all(r['selected_C'] == old[r['session_id']]['selected_C'] for r in predictions)
        probability_equal = all(np.isclose(r['prob_vless'], old[r['session_id']]['prob_vless'],
                                rtol=cfg['probability_rtol'], atol=cfg['probability_atol']) for r in predictions)
        write_table(out/f'{view}-oof.parquet', predictions)
        write_json(out/f'{view}-tuning.json', tuning)
        write_json(out/f'{view}-splits.json', splits)
        result = {'view': view, **metrics(predictions), 'max_probability_difference': max_diff,
                  'selected_C_equal': c_equal, 'probability_equal': probability_equal,
                  'fresh_fit_count': 14*(3*len(cfg['classification_C'])+1),
                  'elapsed_seconds': time.perf_counter()-start}
        results.append(result)
        print(json.dumps(result), flush=True)
    write_json(out/'validation.json', {'all_passed': all(r['selected_C_equal'] and r['probability_equal'] for r in results),
                                     'results': results, 'not_external_validation': True})
    if not all(r['selected_C_equal'] and r['probability_equal'] for r in results):
        raise ValueError('Independent retraining differences require investigation')


def business(cfg):
    verify(cfg)
    source = Path(cfg['source_root'])
    out = Path(cfg['output_root'])/'business-audit'
    out.mkdir(exist_ok=False)
    labels = table(source/'labels.parquet')
    execution = {r['session_id']: r for r in table(source/'execution-diagnostics/session-execution.parquet')}
    routes, cohorts = {}, {}
    for batch in ('broad', 'repeat'):
        base = Path(cfg['audit_root'])/batch/'audit'
        routes.update({r['session_id']: r for r in table(base/'routing_eligibility.parquet')})
        cohorts.update({r['session_id']: r for r in table(base/'cohort_eligibility.parquet')})
    records, groups = [], defaultdict(list)
    for label in labels:
        sid = label['session_id']
        ex, route, cohort = execution[sid], routes.get(sid, {}), cohorts.get(sid, {})
        # Exact URL is an upper-bound content key, not verified semantic identity.
        video = label['effective_activity'] == 'video_playback'
        row = {
            'session_id': sid, 'batch': label['batch'], 'domain': label['target_domain'],
            'target_url': label['target_url'], 'content_upper_bound_id': label['target_url'],
            'protocol': label['protocol'], 'repetition': label['repetition'],
            'current_label_id': label['effective_label_id'], 'page_type': ex['page_type'],
            'activity_semantic_review': 'confirmed_video' if video else 'required_nonvideo_activity_review',
            'video_capture_valid': label['effective_video_capture_valid'],
            'evidence_source': label['effective_evidence_source'],
            'evidence_granularity': label['evidence_granularity'],
            'manual_confirmation_applied': label['manual_confirmation_applied'],
            'page_context_candidate': route.get('page_context_candidate'),
            'page_proxy_connections': cohort.get('page_proxy_connections'),
            'route_reasons_json': cohort.get('reasons_json'),
            'deployment_primary_member': ex['included_primary'],
            'strict_pair_status': 'existing_primary_verified' if ex['included_primary'] else 'requires_entity_level_audit',
            'pre_feature_status': 'existing_primary_available' if ex['included_primary'] else 'not_audited_here',
            'post_feature_status': 'existing_primary_available' if ex['included_primary'] else 'not_audited_here',
        }
        records.append(row)
        groups[row['current_label_id']].append(row)
    coverage = []
    for label_id, members in sorted(groups.items()):
        n = len({r['target_url'] for r in members})
        coverage.append({'label_id': label_id, 'sessions': len(members),
                        'exact_url_content_upper_bound': n,
                        'semantic_content_count': None,
                        'minimum_for_planned_design': cfg['business_min_contents_per_class'],
                        'upper_bound_passes_minimum': n >= cfg['business_min_contents_per_class'],
                        'existing_primary_sessions': sum(r['deployment_primary_member'] for r in members)})
    write_table(out/'session-eligibility-inventory.parquet', records)
    write_table(out/'content-coverage-upper-bound.parquet', coverage)
    summary = {'selected_sessions': len(records), 'label_groups': len(coverage),
               'groups_passing_content_upper_bound': sum(r['upper_bound_passes_minimum'] for r in coverage),
               'business_training_started': False,
               'gate': 'insufficient_content_upper_bound' if not any(r['upper_bound_passes_minimum'] for r in coverage) else 'needs_semantic_and_pair_audit',
               'strict_pair_reaudit_complete': False,
               'warning': 'Broad primary exclusion is not pairing failure; URL counts are not verified independent contents.'}
    write_json(out/'gate.json', summary)
    print(json.dumps(summary), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', default='configs/paired-value-next-stage-0914.yaml')
    parser.add_argument('--mode', choices=['freeze', 'reference', 'business'], required=True)
    args = parser.parse_args()
    cfg = load(args.config)
    if args.mode == 'freeze':
        freeze(cfg, args.config)
    elif args.mode == 'reference':
        reference(cfg)
    else:
        business(cfg)


if __name__ == '__main__':
    main()
