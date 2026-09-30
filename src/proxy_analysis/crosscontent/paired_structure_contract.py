"""Frozen inputs and independently sealed stages for P5-P7 (no legacy mutation)."""
import argparse
import os
import platform
from pathlib import Path

import numpy as np
import scipy
import sklearn
import yaml
from threadpoolctl import threadpool_info

from .mechanism_contract import verify as verify_legacy, read
from .business_representations import dictionary
from ..paired_information.prepare import digest, table
from ..reproducibility.preflight import write_json

CONFIG = Path('configs/content-generalization-20260916-paired-constraint.yaml')


def settings(config=CONFIG):
    cfg = yaml.safe_load(Path(config).read_text(encoding='utf-8'))
    return cfg, Path(cfg['business_root']), Path(cfg['mechanism_root']), Path(cfg['output_root'])


def validate_complete(directory):
    record = read(directory/'complete.json')
    for name, expected in record['artifacts'].items():
        if digest(directory/name) != expected:
            raise ValueError(f'Changed artifact: {directory/name}')
    return record


def seal(directory, **status):
    paths = [p for p in directory.rglob('*') if p.is_file() and p.name != 'complete.json']
    write_json(directory/'complete.json', {**status, 'artifacts':{
        str(p.relative_to(directory)):digest(p) for p in sorted(paths)}})


def freeze(config=CONFIG):
    verify_legacy()
    cfg, source, legacy, root = settings(config)
    paths = [Path(config), source/'side-summaries.parquet', source/'capture-audit.parquet',
             source/'primary-cohort.parquet', source/'conservative-299/cohort.parquet',
             source/'learning/outer-splits.json', legacy/'contract/source-manifest.json']
    for job in sorted((legacy/'jobs').iterdir()):
        validate_complete(job)
        paths.extend(p for p in job.iterdir() if p.is_file())
    for p in [legacy/'report/validation.json', legacy/'sensitivity/report/validation.json',
              legacy/'p4-transformation/validation.json', legacy/'p4-transformation/independent-validation.json']:
        if not read(p)['passed']: raise ValueError(f'Failed prior gate: {p}')
        paths.append(p)
    rows = table(source/'primary-cohort.parquet')
    if len(rows)!=240 or len({r['session_id'] for r in rows})!=240:
        raise ValueError('Primary membership changed')
    conservative = table(source/'conservative-299/cohort.parquet')
    if len(conservative)!=299: raise ValueError('Conservative membership changed')
    paths.extend(source/'sessions'/f"{r['session_id']}.json" for r in conservative)
    # Freeze legacy dependency code; new stage implementations receive their own receipts.
    paths.extend(Path('src/proxy_analysis').rglob('*.py'))
    root.mkdir(parents=True, exist_ok=False)
    write_json(root/'contract/manifest.json', {'config':cfg, 'sources':{
        str(p):digest(p) for p in sorted(set(paths))}, 'feature_dictionary':dictionary(),
        'primary_ids':sorted(r['session_id'] for r in rows),
        'conservative_ids':sorted(r['session_id'] for r in conservative),
        'outer_splits':read(source/'learning/outer-splits.json')})
    write_json(root/'contract/environment.json', {'python':platform.python_version(),
        'numpy':np.__version__, 'scipy':scipy.__version__, 'sklearn':sklearn.__version__,
        'platform':platform.platform(), 'threadpools':threadpool_info(),
        'thread_environment':{k:os.environ.get(k) for k in
          ['OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS']}})
    seal(root/'contract', passed=True)


def verify(config=CONFIG):
    cfg, source, legacy, root = settings(config)
    validate_complete(root/'contract')
    manifest = read(root/'contract/manifest.json')
    if manifest['config'] != cfg: raise ValueError('Frozen configuration changed')
    for p, expected in manifest['sources'].items():
        if digest(Path(p)) != expected: raise ValueError(f'Frozen source changed: {p}')
    return cfg, source, legacy, root


if __name__ == '__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--config',default=str(CONFIG))
    parser.add_argument('--mode',choices=['freeze','verify'],required=True)
    args=parser.parse_args()
    (freeze if args.mode=='freeze' else verify)(args.config)
    print(args.mode+' passed', flush=True)
