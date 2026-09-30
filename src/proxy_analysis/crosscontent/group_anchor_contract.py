"""Separate, immutable preparation and training contract for grouped anchors."""
import argparse
from pathlib import Path
import platform
import numpy as np
import pyarrow
import torch
import sklearn
import yaml

from .mechanism_contract import read, cohort
from .natural_pair_ssl import verify as verify_historical
from .natural_pair_ssl_data import prepare_train, apply_preprocessing, audit_partition, fingerprint
from .business_representations import matrix
from .group_anchor_reliability import feature_groups, crossfit, normalize_fit, normalized, delta_diagnostics
from .paired_structure_contract import seal, validate_complete
from ..paired_information.prepare import digest, table
from ..reproducibility.preflight import write_json, write_table

CONFIG = Path('configs/group-anchor-0916.yaml')


def settings(config=CONFIG):
    cfg = yaml.safe_load(Path(config).read_text(encoding='utf-8'))
    return cfg, Path(cfg['business_root']), Path(cfg['output_root'])


def identity_check(source):
    gate = read(source/'identity-gate.json')
    if not gate['passed']:
        raise ValueError('Historical flow identity gate failed')
    for name, value in gate['source_hashes'].items():
        if digest(source/name) != value:
            raise ValueError('Changed identity evidence')
    return gate


def prepare(config=CONFIG):
    cfg, source, root = settings(config)
    verify_historical()
    identity = identity_check(source)
    if root.exists():
        raise FileExistsError('Refusing to overwrite group-anchor output')
    rows = cohort(source); assignment = read(source/'learning/outer-splits.json')
    if len(rows) != 240 or len({r['session_id'] for r in rows}) != 240:
        raise ValueError('Unexpected cohort')
    captures = {}
    for r in table(source/'capture-audit.parquet'):
        captures.setdefault(r['session_id'], []).append(r)
    groups = feature_groups(); statuses = []; fit_count = 0
    write_json(root/'prepared/groups.json', groups)
    for fold in range(5):
        name = f'six_business-{fold}'
        train = sorted([r for r in rows if assignment[r['content_id']] != fold], key=lambda r: r['session_id'])
        test = sorted([r for r in rows if assignment[r['content_id']] == fold], key=lambda r: r['session_id'])
        partition = audit_partition(train, test, captures)
        ssl, state, diag = prepare_train(train)
        post = matrix(train, 'post', 'distribution157'); pre = matrix(train, 'pre', 'distribution157')
        target_state = normalize_fit(pre, cfg['numerical_eps'])
        target = normalized(pre, target_state)
        mask = np.isfinite(pre) & np.array(target_state['valid'])[None, :]
        meta = lambda rr: [{k: r[k] for k in ('session_id','content_id','label_id','protocol','repetition')} for r in rr]
        true = None; wrong = None
        for relation in ('true', 'mismatched'):
            result, observations = crossfit(meta(train), post, pre, relation, groups, cfg['ridge_alpha'], cfg['numerical_eps'])
            # Validate raw-capture isolation and donor closure for every inner partition.
            lookup = {r['session_id']: r for r in train}
            for split in result['splits']:
                audit_partition([lookup[i] for i in split['train_ids']], [lookup[i] for i in split['validation_ids']], captures)
                for side in ('train', 'validation'):
                    if set(split[f'{side}_ids']) != set(split[f'{side}_donor_ids']):
                        raise ValueError('Donors escape their inner partition')
            fit_count += result['fit_count']
            write_json(root/'reliability'/name/f'{relation}.json', result)
            write_table(root/'reliability'/name/f'{relation}-oof.parquet', observations)
            if relation == 'true': true = result
            else: wrong = result
            statuses.append({'context': name, 'relation': relation, 'passed': result['passed'],
                             'weights': result['weights'], 'fit_count': result['fit_count']})
            print(f'{name} {relation}: weights={result["weights"]} passed={result["passed"]}', flush=True)
        available = [bool(mask[:, g['indices']].any()) for g in groups]
        anchor = {'session_ids': ssl['session_ids'], 'target': target.tolist(), 'target_mask': mask.tolist(),
                  'target_scaler': target_state, 'weights': {'R3': [int(v)/sum(available) for v in available],
                  'R4': true['weights'], 'R5': true['weights'], 'R6': wrong['weights']}}
        data = {'task': 'six_business', 'fold': fold, 'train': meta(train), 'test': meta(test),
                'labels': sorted({r['label_id'] for r in train}), 'audit': partition,
                'preprocessing': state, 'scale_diagnostics': diag,
                'test_post': apply_preprocessing(matrix(test, 'post', 'distribution157'), state).tolist()}
        write_json(root/'prepared'/f'{name}.json', data)
        write_json(root/'prepared'/f'{name}.ssl.json', ssl)
        write_json(root/'prepared'/f'{name}.anchor.json', anchor)
        write_table(root/'reliability'/name/'raw-delta-diagnostics.parquet', delta_diagnostics(train, pre, post))
    passed = all(s['passed'] for s in statuses)
    write_json(root/'reliability/gate.json', {'passed': passed, 'contexts': statuses, 'ridge_fits': fit_count,
               'fit_limit': 6280, 'independent_ridge_closed_form_replay': True,
               'group_order_invariance': True, 'historical_identity_gate': identity,
               'test_features_used_in_reliability': False, 'fresh_raw_packet_reaudit': False})
    seal(root/'prepared', passed=True); seal(root/'reliability', passed=passed)
    # Preparation provenance is frozen now; the full executable contract is frozen after tests.
    paths = [Path(config), source/'side-summaries.parquet', source/'capture-audit.parquet',
             source/'primary-cohort.parquet', source/'learning/outer-splits.json', source/'identity-gate.json']
    paths += list(Path('src/proxy_analysis').rglob('*.py'))
    write_json(root/'preparation-provenance.json', {'sources': {str(p): digest(p) for p in sorted(paths)}})
    if not passed:
        print('STOP: at least one context/relation has no supported anchor. No formal training authorized.', flush=True)


def freeze(config=CONFIG):
    cfg, source, root = settings(config)
    if (root/'contract').exists():
        raise FileExistsError('Contract already frozen')
    validate_complete(root/'prepared'); validate_complete(root/'reliability')
    if not read(root/'reliability/gate.json')['passed']:
        raise ValueError('Reliability gate failed; stop and request a revised design')
    for p, h in read(root/'preparation-provenance.json')['sources'].items():
        if digest(Path(p)) != h:
            raise ValueError(f'Preparation input changed: {p}')
    paths = list(Path('src/proxy_analysis').rglob('*.py')) + [Path(config), root/'preparation-provenance.json']
    write_json(root/'contract/manifest.json', {'config': cfg, 'sources': {str(p): digest(p) for p in sorted(paths)},
               'prepared_sha256': digest(root/'prepared/complete.json'),
               'reliability_sha256': digest(root/'reliability/complete.json')})
    write_json(root/'contract/environment.json', {'python': platform.python_version(), 'numpy': np.__version__,
               'torch': torch.__version__, 'sklearn': sklearn.__version__, 'device': 'cpu', 'dtype': 'float64'})
    seal(root/'contract', passed=True)


def verify(config=CONFIG):
    cfg, source, root = settings(config)
    validate_complete(root/'contract')
    manifest = read(root/'contract/manifest.json')
    if cfg != manifest['config']:
        raise ValueError('Config changed')
    for collection in (manifest['sources'], read(root/'preparation-provenance.json')['sources']):
        for p, h in collection.items():
            if digest(Path(p)) != h:
                raise ValueError(f'Frozen source changed: {p}')
    for directory in ('prepared', 'reliability'):
        if digest(root/directory/'complete.json') != manifest[f'{directory}_sha256']:
            raise ValueError('Prepared/reliability seal changed')
        validate_complete(root/directory)
    if not read(root/'reliability/gate.json')['passed']:
        raise ValueError('No reliable anchors')
    torch.set_num_threads(1); torch.use_deterministic_algorithms(True)
    return cfg, source, root


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('command', choices=['prepare', 'freeze', 'verify'])
    parser.add_argument('--config', default=str(CONFIG)); args = parser.parse_args()
    globals()[args.command](args.config)
