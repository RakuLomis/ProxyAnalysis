"""URL-held-out experiments; re-pair separately inside every training/validation partition."""
from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
import time

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupKFold
import yaml

from ..information_validation.experiments import pipeline, bit_loss
from ..reproducibility.preflight import write_json, write_table
from .pairing import matrix
from .prepare import load_config, table, metrics, digest


def evaluate(rows, spec, view, cfg, seed, wrong, *, limit=None, test_wrong=None):
    test_wrong = wrong if test_wrong is None else test_wrong
    predictions, maps, tuning = [], [], []
    held_urls = sorted({r['target_url'] for r in rows})
    if limit: held_urls = held_urls[:limit]
    for fold, url in enumerate(held_urls):
        train = [r for r in rows if r['target_url'] != url]
        test = [r for r in rows if r['target_url'] == url]
        if len({r['target_url'] for r in train}) < 3: raise ValueError('too few training URL groups')
        y = np.asarray([r['protocol'] == 'VLESS' for r in train], dtype=int)
        groups = [r['target_url'] for r in train]
        losses = defaultdict(list)
        for inner, (tr, va) in enumerate(GroupKFold(n_splits=3).split(train, y, groups)):
            a, b = [train[i] for i in tr], [train[i] for i in va]
            xa, ma = matrix(a, spec, view, seed=seed+inner*2, wrong=wrong)
            xb, mb = matrix(b, spec, view, seed=seed+inner*2+1, wrong=wrong)
            for role, mapping in [('inner_train', ma), ('inner_validation', mb)]:
                maps.extend({**m, 'outer_fold': url, 'inner_fold': inner, 'role': role} for m in mapping)
            for c in cfg['classification_C']:
                model = pipeline(LogisticRegression(C=c, max_iter=3000, random_state=cfg['seed']))
                model.fit(xa, y[tr])
                losses[c].extend(bit_loss(y[va], model.predict_proba(xb)[:, 1]))
        selected = min(cfg['classification_C'], key=lambda c: (float(np.mean(losses[c])), c))
        xa, ma = matrix(train, spec, view, seed=seed+100, wrong=wrong)
        xb, mb = matrix(test, spec, view, seed=seed+101, wrong=test_wrong)
        for role, mapping in [('outer_train', ma), ('outer_test', mb)]:
            maps.extend({**m, 'outer_fold': url, 'inner_fold': -1, 'role': role} for m in mapping)
        model = pipeline(LogisticRegression(C=selected, max_iter=3000, random_state=cfg['seed']))
        model.fit(xa, y)
        probability = model.predict_proba(xb)[:, 1]
        predictions.extend({'session_id': r['session_id'], 'target_url': r['target_url'],
            'protocol': r['protocol'], 'repetition': r['repetition'], 'truth': int(r['protocol']=='VLESS'),
            'prob_vless': float(p), 'view': view, 'wrong': wrong, 'test_wrong': test_wrong, 'seed': seed,
            'selected_C': selected, 'n_features': xa.shape[1], 'fold': url,
            'observation_level': 'offline_index_assisted_post', 'calibration': 'none'}
            for r, p in zip(test, probability))
        tuning.append({'fold': url, 'selected_C': selected,
                       'inner_losses': {str(c): float(np.mean(v)) for c, v in losses.items()}})
    return predictions, maps, tuning


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config', default='configs/paired-information-0914.yaml')
    p.add_argument('--mode', choices=['smoke', 'views', 'families', 'wrong'], required=True)
    p.add_argument('--seed-index', type=int, default=0)
    args = p.parse_args(); cfg = load_config(args.config); root = Path(cfg['output_root'])
    manifest = json.loads((root/'source-manifest.json').read_text())
    for path, expected in manifest['sources'].items():
        if digest(Path(path)) != expected: raise ValueError(f'source changed: {path}')
    spec = yaml.safe_load(Path(cfg['spec']).read_text())['metrics']
    rows = [r for r in table(root/'side-summaries.parquet')
            if r['selection'] == cfg['selection'] and r['scope'] == cfg['scope']]
    expected_ids = {r['session_id'] for r in table(root/'cohort.parquet')}
    if {r['session_id'] for r in rows} != expected_ids or len(rows) != len(expected_ids):
        raise ValueError('summary/cohort mismatch')
    views = ['pre', 'post', 'joint_scalar', 'delta_scalar', 'joint_distribution', 'delta_distribution']
    if args.mode == 'families':
        families = sorted({m['family'] for m in spec if m['transform'] != 'distance' and m['id'] != 'entity_count'})
        views = [prefix + family for prefix in ('pre_family:', 'pre_without:') for family in families]
    if args.mode in {'smoke', 'wrong'}: views = ['delta_scalar', 'delta_distribution']
    out = root / (args.mode + (f'-{args.seed_index:03d}' if args.mode == 'wrong' else ''))
    out.mkdir(exist_ok=False)
    summary = []
    for view in views:
        start = time.perf_counter()
        predictions, maps, tuning = evaluate(rows, spec, view, cfg, cfg['seed']+args.seed_index*1000,
                                             args.mode in {'smoke', 'wrong'},
                                             limit=1 if args.mode == 'smoke' else None)
        stem = view.replace(':', '-')
        write_table(out/f'{stem}-oof.parquet', predictions)
        write_table(out/f'{stem}-pair-map.parquet', maps)
        write_json(out/f'{stem}-tuning.json', tuning)
        result = {'view': view, 'mode': args.mode, **metrics(predictions),
                  'elapsed_seconds': time.perf_counter()-start}
        summary.append(result); print(json.dumps(result), flush=True)
    write_table(out/'summary.parquet', summary)
    write_json(out/'run.json', {'config': cfg, 'mode': args.mode, 'seed_index': args.seed_index,
        'calibration': 'not_implemented_in_this_stage', 'smoke_not_research_result': args.mode=='smoke',
        'input_sha256': digest(root/'side-summaries.parquet'),
        'code_sha256': digest(Path(__file__)), 'pairing_code_sha256': digest(Path(__file__).with_name('pairing.py'))})


if __name__ == '__main__': main()
