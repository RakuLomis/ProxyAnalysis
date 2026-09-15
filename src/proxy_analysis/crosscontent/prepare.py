"""Deterministic draft manifests and fail-closed readiness checks."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
from itertools import permutations
import json
from pathlib import Path
import random
from urllib.parse import urlsplit

import pyarrow as pa
import pyarrow.parquet as pq
import yaml


def validate_design(config):
    if config.get('schema_version') != 1:
        raise ValueError('unsupported schema_version')
    labels, protocols = config['labels'], config['protocols']
    if len(labels) != 4 or len(set(labels)) != 4:
        raise ValueError('design requires four unique labels')
    for label in labels:
        domain, activity = label.split('::')
        if domain not in {'bilibili.com', 'youtube.com'} or activity not in {
            'video_playback', 'search'}:
            raise ValueError('unsupported label')
    if set(protocols) != {'SHADOWSOCKS', 'VLESS', 'HYSTERIA2'} or len(protocols) != 3:
        raise ValueError('three unique deployments required')
    for section, keys in [('pilot', ['contents_per_label', 'blocks']),
                          ('formal', ['development_contents_per_label',
                                      'locked_contents_per_label', 'blocks'])]:
        for key in keys:
            value = config[section][key]
            if type(value) is not int or value < 1:
                raise ValueError(f'invalid {section}.{key}')
    if config['formal']['blocks'] < 2:
        raise ValueError('formal design needs a held-out block')
    obs = config['observation']
    if obs['primary_seconds'] <= 0 or obs['stop_at_playback_goal'] is not False:
        raise ValueError('fixed positive observation window required')


def content_slots(config):
    """Placeholders are deliberately not URLs or valid observations."""
    validate_design(config)
    rows = []
    for label_index, label in enumerate(config['labels']):
        for role, count in [
            ('pilot', config['pilot']['contents_per_label']),
            ('development', config['formal']['development_contents_per_label']),
            ('locked', config['formal']['locked_contents_per_label']),
        ]:
            for index in range(count):
                slot = f'{role}-label{label_index + 1}-{index + 1:03d}'
                domain, activity = label.split('::')
                rows.append(dict(slot_id=slot, label_id=label, domain=domain,
                                 activity=activity, split_role=role, target_url=None,
                                 content_group_id=None, accessible_verified=False,
                                 independent_of_0914_verified=False,
                                 semantic_group_reviewed=False))
    return rows


def validate_contents(config, rows):
    expected = {r['slot_id']: r for r in content_slots(config)}
    if len(rows) != len(expected) or {r['slot_id'] for r in rows} != set(expected):
        raise ValueError('missing or duplicate content slots')
    groups, urls = set(), set()
    for row in rows:
        for field in ('label_id', 'domain', 'activity', 'split_role'):
            if row[field] != expected[row['slot_id']][field]:
                raise ValueError(f'changed slot assignment: {field}')
        group, url = row.get('content_group_id'), row.get('target_url')
        if group is not None:
            if not isinstance(group, str) or not group.strip() or group in groups:
                raise ValueError('empty/duplicate content group; merge before splitting')
            groups.add(group)
        if url is not None:
            parsed = urlsplit(url)
            host = parsed.hostname or ''
            if (parsed.scheme != 'https' or parsed.username or parsed.password
                    or parsed.fragment or not (host == row['domain']
                    or host.endswith('.' + row['domain']))):
                raise ValueError('target must be an HTTPS URL on the declared domain')
            if url in urls:
                raise ValueError('duplicate target URL')
            urls.add(url)


def partition(role, block, total_blocks):
    if role == 'pilot':
        return 'pilot'
    if block == total_blocks:
        return 'joint_locked_test' if role == 'locked' else 'unseen_date_diagnostic'
    return 'unseen_content_test' if role == 'locked' else 'development'


def schedule(config, contents, stage):
    validate_design(config)
    validate_contents(config, contents)
    if stage not in {'pilot', 'formal'}:
        raise ValueError('unknown stage')
    selected = [r for r in contents if (r['split_role'] == 'pilot') == (stage == 'pilot')]
    selected.sort(key=lambda r: r['slot_id'])
    rng = random.Random(config['seed'] + (stage == 'formal'))
    blocks = config[stage]['blocks']
    orders = list(permutations(config['protocols']))
    rows = []
    for block in range(1, blocks + 1):
        shuffled = selected.copy()
        rng.shuffle(shuffled)
        balanced = [orders[i % len(orders)] for i in range(len(shuffled))]
        rng.shuffle(balanced)
        for content, order in zip(shuffled, balanced):
            for protocol in order:
                unit = f"{config['experiment_id']}:{content['slot_id']}:b{block}:{protocol}"
                rows.append({**content, 'experiment_id': config['experiment_id'],
                             'planned_unit_id': unit, 'stage': stage, 'block_id': block,
                             'protocol': protocol, 'planned_order': len(rows) + 1,
                             'partition': partition(content['split_role'], block, blocks),
                             'requires_model_lock': stage == 'formal' and block == blocks,
                             'date': None, 'capture_status': 'not_started',
                             'schedule_status': 'draft_not_capture_authorization'})
    return rows


def readiness(config, rows):
    validate_contents(config, rows)
    pilot = [r for r in rows if r['split_role'] == 'pilot']
    unresolved = [r['slot_id'] for r in pilot if not (
        r.get('target_url') and r.get('content_group_id')
        and all(r.get(k) is True for k in ('accessible_verified',
                'independent_of_0914_verified', 'semantic_group_reviewed')))]
    missing = [key for key in ('collector_path', 'deployment_manifest',
                               'isolated_proxy_confirmed', 'clean_browser_confirmed')
               if not config['deployment'].get(key)]
    return {'status': 'blocked' if unresolved or missing else 'configuration_complete',
            'unresolved_pilot_slots': unresolved, 'missing_deployment_fields': missing,
            'capture_ready': False,
            'remaining_operational_gates': ['collector integration', 'scope audit',
                                             'evidence integration', 'dated schedule'],
            'note': 'Configuration completeness never certifies runtime capture readiness.'}


def prepare(config_path, output, contents_path=None):
    config = yaml.safe_load(config_path.read_text(encoding='utf-8'))
    validate_design(config)
    contents = (json.loads(contents_path.read_text(encoding='utf-8'))
                if contents_path else content_slots(config))
    pilot = schedule(config, contents, 'pilot')
    formal = schedule(config, contents, 'formal')
    result = readiness(config, contents)
    result.update(planned_pilot_sessions=len(pilot), planned_formal_sessions=len(formal),
                  formal_partitions=dict(Counter(r['partition'] for r in formal)),
                  actual_captures=0,
                  config_sha256=hashlib.sha256(config_path.read_bytes()).hexdigest(),
                  contents_sha256=hashlib.sha256(json.dumps(contents, sort_keys=True,
                      ensure_ascii=False).encode('utf-8')).hexdigest())
    # Fail before overwriting any prior schedule or evidence.
    output.mkdir(parents=True, exist_ok=False)
    for name, rows in [('content-slots', contents), ('pilot-schedule', pilot),
                       ('formal-schedule-draft', formal)]:
        pq.write_table(pa.Table.from_pylist(rows), output / f'{name}.parquet')
    (output / 'content-slots.json').write_text(
        json.dumps(contents, ensure_ascii=False, indent=2), encoding='utf-8')
    (output / 'readiness.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    (output / 'design-snapshot.yaml').write_text(
        yaml.safe_dump(config, allow_unicode=True, sort_keys=False), encoding='utf-8')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--contents', type=Path)
    args = parser.parse_args()
    print(json.dumps(prepare(args.config, args.output, args.contents),
                     ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
