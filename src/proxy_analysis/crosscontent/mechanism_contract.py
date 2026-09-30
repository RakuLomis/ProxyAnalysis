"""Immutable inputs for the approved retrospective 0916 mechanism experiments."""
from __future__ import annotations

import json
from pathlib import Path
import platform

import numpy as np
import sklearn
import yaml

from .business_features import load_config, verify as verify_business
from .business_splits import outer_assignment
from ..paired_information.prepare import digest, table
from ..reproducibility.preflight import write_json

CONFIG = Path('configs/content-generalization-20260916-mechanism.yaml')


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def settings():
    cfg = yaml.safe_load(CONFIG.read_text(encoding='utf-8'))
    business = load_config(cfg['business_config'])
    return cfg, business, Path(business['output_root']), Path(cfg['output_root'])


def freeze():
    cfg, business, source, out = settings()
    verify_business(business)
    for directory in (source/'learning', source/'conservative-299'):
        for name, expected in read(directory/'complete.json')['artifacts'].items():
            if digest(directory/name) != expected:
                raise ValueError(f'Historical artifact changed: {directory/name}')
    gate = read(source/'identity-gate.json')
    if not gate['passed']:
        raise ValueError('Historical identity gate failed')
    for name, expected in gate['source_hashes'].items():
        if digest(source/name) != expected:
            raise ValueError('Audited input changed')
    for path in (source/'report/validation.json', source/'conservative-299/validation.json'):
        if not read(path)['passed']:
            raise ValueError('Historical model validation failed')
    rows = cohort(source)
    assignment = read(source/'learning/outer-splits.json')
    if len(rows) != cfg['cohort_size'] or assignment != outer_assignment(rows, business['seed']):
        raise ValueError('Historical cohort/splits mismatch')
    expected = {r['session_id'] for r in table(source/'primary-cohort.parquet')}
    if {r['session_id'] for r in rows} != expected:
        raise ValueError('Primary members changed')
    conservative = table(source/'conservative-299/cohort.parquet')
    candidates = table(source/'candidates.parquet')
    if len(conservative) != 299 or {r['session_id'] for r in conservative} != {
            r['session_id'] for r in candidates if r['effective_label_valid']}:
        raise ValueError('299 membership mismatch')
    paths = [CONFIG, Path(cfg['business_config']), Path(business['feature_config'])]
    paths += list(Path('src/proxy_analysis').rglob('*.py'))
    paths += [p for p in source.rglob('*') if p.is_file() and 'sessions' not in p.parts
              and 'smoke' not in p.parts]
    out.mkdir(parents=True, exist_ok=False)
    contract = out/'contract'; contract.mkdir()
    write_json(contract/'source-manifest.json', {'config':cfg, 'business_config':business,
        'sources':{str(p):digest(p) for p in sorted(set(paths))},
        'scope':'retrospective_0916_240_observed_only', 'target_fit_allowed':False})
    write_json(contract/'cohort-and-splits.json', {'members':sorted(expected), 'outer_assignment':assignment})
    write_json(contract/'environment.json', {'python':platform.python_version(), 'numpy':np.__version__,
        'sklearn':sklearn.__version__, 'platform':platform.platform()})
    print(json.dumps({'frozen':True, 'sources':len(set(paths)), 'cohort':len(rows)}), flush=True)


def verify():
    cfg, business, source, out = settings()
    contract = read(out/'contract/source-manifest.json')
    if cfg != contract['config'] or business != contract['business_config']:
        raise ValueError('Mechanism configuration changed')
    for path, expected in contract['sources'].items():
        if digest(Path(path)) != expected:
            raise ValueError(f'Frozen mechanism source changed: {path}')
    return cfg, business, source, out


def cohort(source):
    return [r for r in table(source/'side-summaries.parquet')
            if r['selection']=='observed' and r['primary_candidate']]


if __name__ == '__main__':
    freeze()
