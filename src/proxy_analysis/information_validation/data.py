"""Audited session views, conservative activity evidence and grouped splits."""
from __future__ import annotations

from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq

DISTANCES = {'length_js', 'iat_js', 'cumulative_l1'}
OBSERVATION = 'offline_index_assisted_post'


def write_json(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')


def write_table(path, rows):
    pq.write_table(pa.Table.from_pylist(rows), path)


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as source:
        for block in iter(lambda: source.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def validate_feature_identity(feature, registry_row):
    for key in ['session_id', 'protocol', 'repetition', 'activity_id', 'target_domain', 'is_final']:
        if feature[key] != registry_row[key]:
            raise ValueError(f'feature/registry identity mismatch: {key}')


def classify_activity(summary):
    """Only explicit playback observations verify playback; never infer from host."""
    activity = summary.get('activity_outcome') or {}
    playback = summary.get('playback') or {}
    navigation = summary.get('navigation_outcome') or {}
    verified = None
    playback_present = bool(playback) or 'playback' in activity.get('kind', '')
    seconds = playback.get('primary_content_seconds')
    desired = playback.get('desired_primary_seconds')
    passed = (activity.get('state') == 'passed'
              and playback.get('primary_goal_met') is True
              and playback.get('primary_content_observed') is True
              and isinstance(seconds, (int, float)) and isinstance(desired, (int, float))
              and desired > 0 and seconds >= desired)
    # Capture validity is distinct from achieving the configured duration goal.
    # Accept explicit main-content evidence, never merely a player/ad/page load.
    observed = playback.get('primary_content_observed', activity.get('primary_content_observed'))
    evidence_seconds = playback.get('primary_content_seconds', activity.get('primary_content_seconds'))
    positive_seconds = (isinstance(evidence_seconds, (int, float)) and not isinstance(evidence_seconds, bool)
                        and np.isfinite(evidence_seconds) and evidence_seconds > 0)
    valid_capture = observed is True or positive_seconds
    if valid_capture:
        verified = 'video_playback'
    elif navigation.get('state') == 'passed':
        verified = 'page_load'
    return {
        'verified_activity': verified,
        'activity_kind': activity.get('kind'),
        'activity_state': activity.get('state'),
        'navigation_state': navigation.get('state'),
        'playback_status': ('passed' if valid_capture else
                            'not_met' if playback_present and playback.get('primary_goal_met') is False
                            else 'unverified'),
        'primary_content_seconds': seconds,
        'desired_primary_seconds': desired,
        'playback_verified': valid_capture,
        'video_capture_valid': valid_capture,
        'playback_goal_met': passed,
        'playback_evidence_primary_seconds': evidence_seconds,
        'playback_evidence_primary_observed': observed,
        'playback_validity_policy': 'primary_content_presence_v2',
        'activity_reason': activity.get('reason'),
    }


def build_labels(registry, routes, sites):
    targets = {(s['domain'], s['url']): s for s in sites['sites']}
    if len(targets) != len(sites['sites']):
        raise ValueError('ambiguous duplicate target URL/activity; explicit activity key required')
    labels = []
    for row in registry:
        if not row['is_final']:
            continue
        source = Path(row['session_path']) / 'analysis/summary.json'
        summary = json.loads(source.read_text(encoding='utf-8'))
        if summary['session_id'] != row['session_id']:
            raise ValueError('summary/session identity mismatch')
        status = classify_activity(summary)
        target = targets[(row['target_domain'], row['target_url'])]
        intended = 'video_playback' if target.get('playback') else 'page_load'
        proposed = target.get('requested_activity', intended)
        # page_load is a verified captured behavior, NOT a substituted user activity class.
        labels.append({
            'session_id': row['session_id'], 'site_domain': row['target_domain'],
            'protocol': row['protocol'], 'repetition': row['repetition'],
            'content_id': row['activity_id'], 'target_url': row['target_url'],
            'intended_activity': intended, 'proposed_activity': proposed,
            'requested_label_id': row['target_domain'] + '::' + proposed,
            'observed_label_id': (row['target_domain'] + '::' + status['verified_activity']
                                  if status['verified_activity'] else None),
            'playback_label_eligible': status['playback_verified'],
            'page_proxy_candidate': routes[row['session_id']]['page_context_candidate'],
            'main_document_proxy_candidate': routes[row['session_id']]['main_document_proxy_candidate'],
            'evidence_source': str(source), 'evidence_sha256': digest(source),
            'label_mapping_status': 'playback_evidence_audit_not_full_activity_mapping',
            **status,
        })
    return labels


def split_indices(rows, scheme):
    key = 'repetition' if scheme == 'LORO' else ('activity_id' if all('activity_id' in r for r in rows) else 'target_domain')
    groups = sorted({r[key] for r in rows})
    if len(groups) < 3:
        raise ValueError('at least three outer groups required')
    for held in groups:
        train = np.array([i for i, r in enumerate(rows) if r[key] != held], dtype=int)
        test = np.array([i for i, r in enumerate(rows) if r[key] == held], dtype=int)
        assert not set(train) & set(test)
        assert {rows[i][key] for i in train}.isdisjoint({rows[i][key] for i in test})
        yield str(held), train, test


def build_data(input_root, output_root, config, metrics, sites):
    root, out = Path(input_root), Path(output_root)
    registry = pq.read_table(root / 'run_registry.parquet').to_pylist()
    route_rows = pq.read_table(root / 'routing_eligibility.parquet').to_pylist()
    routes = {r['session_id']: r for r in route_rows}
    if len(routes) != len(route_rows):
        raise ValueError('duplicate route session')
    if len({r['session_id'] for r in registry}) != len(registry):
        raise ValueError('duplicate registry session')
    by_session = {r['session_id']: r for r in registry}
    long = pq.read_table(root / 'repeat_feature_long.parquet').to_pylist()
    indexed = defaultdict(dict)
    missing = Counter()
    contract_ids = {r['contract_sha256'] for r in long}
    if len(contract_ids) != 1:
        raise ValueError('mixed extraction contracts')
    for r in long:
        if r['session_id'] not in by_session:
            raise ValueError('orphan feature session')
        validate_feature_identity(r, by_session[r['session_id']])
        if r['scope'] != 'exclusive_page':
            continue
        key = (r['session_id'], r['selection'])
        if r['metric'] in indexed[key]:
            raise ValueError('duplicate metric')
        indexed[key][r['metric']] = r
        if r['delta'] is None:
            missing[(r['metric'], r['reason'])] += 1
    scalar = [m['id'] for m in metrics if m['id'] not in DISTANCES | {'entity_count'}]
    delta = [m['id'] for m in metrics if m['id'] != 'entity_count']
    membership, data, splits = [], {}, []
    all_metrics = {m['id'] for m in metrics}
    for setting in config['settings']:
        eligible = []
        reasons = {}
        required = {(c, r) for c in config['protocols'] for r in range(setting['min_round'], 6)}
        for row in registry:
            sid = row['session_id']
            why = []
            if not row['is_final']: why.append('historical_attempt')
            if row['protocol'] not in config['protocols']: why.append('carrier_context_not_primary')
            if row['repetition'] < setting['min_round']: why.append('outside_round_stratum')
            if setting['no_retry'] and not row['is_first_attempt']: why.append('retried_final')
            route = routes.get(sid, {})
            field = 'main_document_proxy_candidate' if setting['route'] == 'main_document' else 'page_context_candidate'
            if not route.get(field): why.append('route_or_quality_ineligible')
            feature = indexed.get((sid, setting['selection']), {})
            if set(feature) != all_metrics: why.append('missing_feature_records')
            elif feature['entity_count']['pre'] is None or feature['entity_count']['post'] is None:
                why.append('no_usable_exclusive_side')
            reasons[sid] = why
            if not why:
                eligible.append(row)
        cells = defaultdict(list)
        for row in eligible:
            cells[row['activity_id']].append((row['protocol'], row['repetition']))
        for domain, values in cells.items():
            if len(values) != len(set(values)):
                raise ValueError('duplicate final target/protocol/round')
        complete = {u for u, values in cells.items() if set(values) == required}
        rows = []
        for row in registry:
            sid = row['session_id']
            why = list(reasons[sid])
            if not why and row['activity_id'] not in complete:
                why.append('incomplete_url_protocol_round_grid')
            membership.append({'setting': setting['id'], 'session_id': sid,
                               'target_domain': row['target_domain'], 'protocol': row['protocol'],
                               'repetition': row['repetition'], 'included': not why,
                               'reasons': why, 'is_final': row['is_final']})
            if why:
                continue
            features = indexed[(sid, setting['selection'])]
            item = {k: row[k] for k in ['session_id', 'target_domain', 'protocol', 'repetition',
                                        'activity_id', 'candidate_position', 'run_ordinal', 'traffictracer_commit']}
            item['setting'] = setting['id']
            item['observation_level'] = OBSERVATION
            for view, columns in [('pre', scalar), ('post', scalar), ('delta', delta)]:
                for metric in columns:
                    item[view + '__' + metric] = features[metric][view]
            rows.append(item)
        rows.sort(key=lambda r: (r['target_domain'], r['protocol'], r['repetition']))
        if len(complete) < 3:
            raise ValueError(f'insufficient complete URL groups: {setting}')
        data[setting['id']] = rows
        if len(rows) != len(complete) * len(required):
            raise ValueError('unexpected cohort size')
        for scheme in ['LORO', 'LOUO']:
            for held, train, test in split_indices(rows, scheme):
                for role, indices in [('train', train), ('test', test)]:
                    splits.extend({'setting': setting['id'], 'scheme': scheme, 'fold': held,
                                   'role': role, 'session_id': rows[i]['session_id']} for i in indices)
    write_table(out / 'cohort-membership.parquet', membership)
    write_table(out / 'split-manifest.parquet', splits)
    for view, columns in [('pre', scalar), ('post', scalar), ('delta', delta)]:
        write_table(out / (view + '-wide.parquet'), [
            {**{k: r[k] for k in ['setting', 'session_id', 'target_domain', 'protocol', 'repetition', 'observation_level']},
             **{c: r[view + '__' + c] for c in columns}}
            for rows in data.values() for r in rows])
    labels = build_labels(registry, routes, sites)
    write_table(out / 'label-evidence.parquet', labels)
    write_json(out / 'feature-allowlist.json', {'pre': scalar, 'post': scalar, 'delta': delta,
               'excluded': ['entity_count', 'metadata', 'opposite_side', 'distance_as_single_side'],
               'extraction_contract_sha256': next(iter(contract_ids))})
    write_json(out / 'missingness.json', [{'metric': a, 'reason': b, 'count_all_exclusive_attempts_variants': n}
                                         for (a, b), n in missing.items()])
    return data, scalar, delta, labels
