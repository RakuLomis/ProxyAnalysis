"""Frozen train/input/evaluation packages for controlled anchor diagnostics."""
import argparse
from pathlib import Path
import platform
import numpy as np
import pyarrow
import sklearn
import torch
import yaml

from .group_anchor_contract import verify as verify_anchor, identity_check
from .group_anchor_reliability import feature_groups
from .natural_pair_ssl_data import prepare_train, apply_preprocessing, audit_partition, fingerprint, cyclic_donors
from .business_representations import matrix
from .mechanism_contract import read, cohort
from .paired_structure_contract import seal, validate_complete
from ..paired_information.prepare import digest, table
from ..reproducibility.preflight import write_json

CONFIG = Path('configs/group-anchor-diagnostics-0916.yaml')


def settings(config=CONFIG):
    cfg = yaml.safe_load(Path(config).read_text(encoding='utf-8'))
    return cfg, Path(cfg['anchor_root']), Path(cfg['output_root'])


def nullable(x):
    x = np.asarray(x, dtype=object)
    x[~np.isfinite(np.asarray(x, float))] = None
    return x.tolist()


def freeze(config=CONFIG):
    cfg, anchor, root = settings(config)
    verify_anchor(cfg['anchor_config']); source = Path(cfg['business_root']); gate = identity_check(source)
    for part in ('report', 'training-audit', 'mechanism-audit'):
        validate_complete(anchor/part)
    if root.exists(): raise FileExistsError(root)
    lookup = {r['session_id']: r for r in cohort(source)}
    captures = {}
    for r in table(source/'capture-audit.parquet'):
        captures.setdefault(r['session_id'], []).append(r)
    audit = []
    for fold in range(cfg['folds']):
        old = read(anchor/'prepared'/f'six_business-{fold}.json')
        ssl = read(anchor/'prepared'/f'six_business-{fold}.ssl.json')
        target = read(anchor/'prepared'/f'six_business-{fold}.anchor.json')
        train = [lookup[r['session_id']] for r in old['train']]
        test = [lookup[r['session_id']] for r in old['test']]
        isolation = audit_partition(train, test, captures)
        rebuilt, scaler, _ = prepare_train(train)
        if fingerprint(rebuilt) != fingerprint(ssl) or fingerprint(scaler) != fingerprint(old['preprocessing']):
            raise ValueError('Training-only source reconstruction differs')
        test_post = apply_preprocessing(matrix(test, 'post', 'distribution157'), scaler)
        if not np.allclose(test_post, old['test_post'], rtol=0, atol=1e-12):
            raise ValueError('Test post source replay differs')
        write_json(root/'packages'/f'fold-{fold}.train.json', {
            'fold': fold, 'rows': old['train'], 'labels': old['labels'], 'post': ssl['post'],
            'raw_post': nullable(matrix(train, 'post', 'distribution157')),
            'raw_pre': nullable(matrix(train, 'pre', 'distribution157')),
            'pre_target': target['target'], 'target_mask': target['target_mask'],
            'post_scaler': scaler, 'pre_scaler': target['target_scaler'], 'donors': ssl['donor_indices']})
        write_json(root/'packages'/f'fold-{fold}.input.json', {
            'fold': fold, 'session_ids': [r['session_id'] for r in old['test']], 'post': test_post.tolist()})
        write_json(root/'evaluation'/f'fold-{fold}.json', {
            'fold': fold, 'rows': old['test'], 'raw_pre': nullable(matrix(test, 'pre', 'distribution157')),
            'donors': cyclic_donors(old['test'])})
        audit.append({'fold': fold, **isolation, 'train_donor_closure': sorted(ssl['donor_indices']) == list(range(192))})
    write_json(root/'packages/groups.json', feature_groups())
    write_json(root/'packages/isolation.json', audit)
    seal(root/'packages', passed=True); seal(root/'evaluation', passed=True)
    sources = list(Path('src/proxy_analysis').rglob('*.py')) + [Path(config), Path(cfg['anchor_config']),
        source/'side-summaries.parquet', source/'capture-audit.parquet', source/'identity-gate.json']
    sources += [p for directory in ('prepared', 'reliability', 'report', 'contract', 'mechanism-audit')
                for p in (anchor/directory).rglob('*') if p.is_file()]
    for fold in range(cfg['folds']):
        for seed in cfg['seeds']:
            for arm in cfg['arms']:
                job = anchor/'jobs'/f'six_business-{fold}-{seed}-{arm}'
                validate_complete(job)
                sources += [job/'ssl-fit.json', job/'membership.json', job/'complete.json']
    write_json(root/'contract/manifest.json', {'config': cfg, 'sources': {str(p): digest(p) for p in sorted(set(sources))},
        'packages_seal': digest(root/'packages/complete.json'), 'evaluation_seal': digest(root/'evaluation/complete.json'),
        'historical_identity_gate': gate, 'neural_training_authorized': False,
        'test_pre_authorized_only_for_offline_evaluation': True})
    write_json(root/'contract/environment.json', {'python': platform.python_version(), 'numpy': np.__version__,
        'sklearn': sklearn.__version__, 'torch': torch.__version__, 'dtype': 'float64', 'device': 'cpu'})
    seal(root/'contract', passed=True)
    print('Frozen five train/input/evaluation packages; no test labels/pre in inference input', flush=True)


def verify(config=CONFIG):
    cfg, anchor, root = settings(config); validate_complete(root/'contract')
    manifest = read(root/'contract/manifest.json')
    if cfg != manifest['config']: raise ValueError('Config changed')
    for p, expected in manifest['sources'].items():
        if digest(Path(p)) != expected: raise ValueError(f'Frozen source changed: {p}')
    for part, key in (('packages','packages_seal'), ('evaluation','evaluation_seal')):
        if digest(root/part/'complete.json') != manifest[key]: raise ValueError('Package manifest changed')
        validate_complete(root/part)
    torch.set_num_threads(1); torch.use_deterministic_algorithms(True)
    return cfg, anchor, root


def validate_input(value):
    if set(value) != {'fold', 'session_ids', 'post'}:
        raise ValueError('Inference input must not contain labels or pre targets')
    x = np.asarray(value['post'], float)
    if x.shape != (len(value['session_ids']), 157) or not np.isfinite(x).all():
        raise ValueError('Invalid inference matrix')
    return x


def evaluation_package(root, fold):
    # Parameters and both kinds of predictions must be sealed before targets are read.
    validate_complete(root/'utility'); validate_complete(root/'recovery')
    return read(root/'evaluation'/f'fold-{fold}.json')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('command', choices=['freeze','verify'])
    parser.add_argument('--config', default=str(CONFIG)); args = parser.parse_args(); globals()[args.command](args.config)
