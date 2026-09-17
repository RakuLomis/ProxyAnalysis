"""Independent distribution/mismatching reference, sharing only scalar reference.

The permutation algorithm is independently reproduced from its frozen contract;
the main pairing/matrix/compare/evaluate functions are not called.
"""
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

from ..reproducibility.preflight import write_json, write_table
from .next_stage import data, load, verify
from .prepare import digest, metrics, table
from .reference_retrain import build_matrix, inner_indices, fit_model, loss_bits, assert_partition


def construct(rows, spec, view, seed, wrong):
    donors = list(range(len(rows)))
    if wrong:
        groups = defaultdict(list)
        for i, row in enumerate(rows):
            groups[(row['target_url'], row['protocol'])].append(i)
        for key, ids in sorted(groups.items()):
            if len(ids) < 2:
                raise ValueError('Singleton stratum')
            ordered = sorted(ids, key=lambda i: rows[i]['session_id'])
            rng = np.random.default_rng(int.from_bytes(hashlib.sha256(repr((seed, key)).encode()).digest()[:8]))
            while True:
                shuffled = rng.permutation(ordered)
                if all(a != b for a, b in zip(ordered, shuffled)):
                    break
            for a, b in zip(ordered, shuffled):
                donors[a] = int(b)
    paired = [{**row, 'pre': rows[donors[i]]['pre']} for i, row in enumerate(rows)]
    scalar_view = 'joint_scalar' if view == 'joint_distribution' else 'delta_scalar'
    result = build_matrix(paired, spec, scalar_view).tolist()
    if view == 'delta_scalar':
        return np.asarray(result), donors
    for i, row in enumerate(paired):
        a, b = row['pre'], row['post']
        if view == 'joint_distribution':
            for side in (a, b):
                for key in ('length_hist', 'iat_hist'):
                    values = np.asarray(side[key], dtype=float)
                    result[i].extend(values/values.sum() if values.sum() else [np.nan]*len(values))
                result[i].extend(side['curve'] if side['curve'] is not None else [np.nan]*101)
        else:
            for key in ('length_hist', 'iat_hist'):
                p, q = np.asarray(a[key], dtype=float), np.asarray(b[key], dtype=float)
                if not p.sum() or not q.sum():
                    result[i].append(np.nan)
                    continue
                p, q = p/p.sum(), q/q.sum()
                middle = (p+q)/2
                terms = []
                for value in (p, q):
                    valid = value > 0
                    terms.append(float(np.sum(value[valid]*np.log2(value[valid]/middle[valid]))))
                result[i].append(sum(terms)/2)
            result[i].append(float(np.mean(np.abs(np.asarray(a['curve'])-np.asarray(b['curve']))))
                             if a['curve'] is not None and b['curve'] is not None else np.nan)
    return np.asarray(result, dtype=float), donors


def main():
    cfg = load('configs/paired-value-next-stage-0914.yaml')
    verify(cfg)
    rows, spec = data(cfg)
    out = Path(cfg['output_root'])/'reference-distribution'
    out.mkdir(exist_ok=False)
    results = []
    for view, wrong in [('joint_distribution', False), ('delta_distribution', False),
                        ('delta_scalar', True), ('delta_distribution', True)]:
        predictions, maps = [], []
        for url in sorted({r['target_url'] for r in rows}):
            train, test = [r for r in rows if r['target_url'] != url], [r for r in rows if r['target_url'] == url]
            losses = defaultdict(list)

            def x(part, offset, role, inner):
                result, donors = construct(part, spec, view, cfg['seed']+offset, wrong)
                maps.extend({'outer_url': url, 'inner_fold': inner, 'role': role,
                             'receiver': row['session_id'], 'donor': part[donors[i]]['session_id']}
                            for i, row in enumerate(part))
                return result

            for inner, (tr, va) in enumerate(inner_indices(train)):
                a, b = [train[i] for i in tr], [train[i] for i in va]
                assert_partition(a, b, test)
                xa, xb = x(a, inner*2, 'inner_train', inner), x(b, inner*2+1, 'inner_validation', inner)
                ya, yb = [int(r['protocol']=='VLESS') for r in a], [int(r['protocol']=='VLESS') for r in b]
                for c in cfg['classification_C']:
                    model = fit_model(xa, ya, c, cfg['seed'])
                    losses[c].extend(loss_bits(yb, model.predict_proba(xb)[:, 1]))
            chosen = min(cfg['classification_C'], key=lambda c: (np.mean(losses[c]), c))
            model = fit_model(x(train, 100, 'outer_train', -1), [int(r['protocol']=='VLESS') for r in train], chosen, cfg['seed'])
            probabilities = model.predict_proba(x(test, 101, 'outer_test', -1))[:, 1]
            predictions.extend({'session_id': row['session_id'], 'target_url': url,
                'truth': int(row['protocol']=='VLESS'), 'prob_vless': float(p), 'selected_C': chosen}
                for row, p in zip(test, probabilities))
        baseline_path = Path(cfg['source_root'])/('wrong-000' if wrong else 'views')/f'{view}-oof.parquet'
        old = {r['session_id']: r for r in table(baseline_path)}
        passed = all(r['selected_C'] == old[r['session_id']]['selected_C'] and
                     np.isclose(r['prob_vless'], old[r['session_id']]['prob_vless'],
                                rtol=cfg['probability_rtol'], atol=cfg['probability_atol']) for r in predictions)
        stem = f'{view}-wrong-{wrong}'
        write_table(out/f'{stem}-oof.parquet', predictions)
        write_table(out/f'{stem}-map.parquet', maps)
        result = {'view': view, 'wrong': wrong, **metrics(predictions), 'passed': passed,
                  'fresh_fit_count': 140, 'baseline_sha256': digest(baseline_path),
                  'max_probability_difference': max(abs(r['prob_vless']-old[r['session_id']]['prob_vless']) for r in predictions)}
        results.append(result)
        print(json.dumps(result), flush=True)
    write_json(out/'validation.json', {'all_passed': all(r['passed'] for r in results),
                                     'results': results, 'code_sha256': digest(Path(__file__))})
    if not all(r['passed'] for r in results):
        raise ValueError('Distribution/wrong reference mismatch')


if __name__ == '__main__':
    main()
