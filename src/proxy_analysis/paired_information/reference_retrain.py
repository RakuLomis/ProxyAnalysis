"""Independent scalar construction and fitting; never calls the original evaluate.

Shares sklearn estimators and saved source summaries, not the original matrix,
transformation, preprocessing factory, loss function, or training executor.
"""
from __future__ import annotations

import math
from collections import defaultdict

import numpy as np
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


SCALAR_NAMES = (
    'packet_count', 'transport_bytes', 'ip_bytes', 'up_transport_bytes',
    'down_transport_bytes', 'burst_count', 'fr_runs', 'fr_switches',
    'fr_runs_per_packet', 'up_byte_fraction', 'transition_p_pm',
    'direction_entropy', 'length_median', 'iat_median_us',
)


def scalar_spec(spec):
    result = [m for m in spec if m['transform'] != 'distance' and m['id'] != 'entity_count']
    if tuple(m['id'] for m in result) != SCALAR_NAMES:
        raise ValueError('Scalar contract changed; review required')
    return result


def build_matrix(rows, spec, view):
    selected = scalar_spec(spec)
    values = []
    for row in rows:
        pre = [row['pre'].get(m['id']) for m in selected]
        post = [row['post'].get(m['id']) for m in selected]
        if view == 'pre':
            vector = pre
        elif view == 'post':
            vector = post
        elif view == 'joint_scalar':
            vector = pre + post
        elif view == 'delta_scalar':
            vector = []
            for a, b, m in zip(pre, post, selected):
                if a is None or b is None:
                    vector.append(None)
                elif m['transform'] == 'log_ratio':
                    vector.append(math.log(b / a) if a > 0 and b > 0 else None)
                elif m['transform'] == 'difference':
                    vector.append(b - a)
                else:
                    raise ValueError(m['transform'])
        else:
            raise ValueError('Independent reference currently supports scalar views only')
        values.append(vector)
    return np.asarray(values, dtype=float)


def loss_bits(y, probabilities):
    p = np.clip(np.asarray(probabilities), 1e-12, 1 - 1e-12)
    return -np.log2(np.where(np.asarray(y) == 1, p, 1 - p))


def fit_model(x, y, c, seed):
    model = Pipeline([
        ('imputer', SimpleImputer(strategy='median', keep_empty_features=True)),
        ('scaler', StandardScaler()),
        ('classifier', LogisticRegression(C=c, max_iter=3000, random_state=seed)),
    ])
    return model.fit(x, y)


def assert_partition(train, validation, test):
    for key in ('session_id', 'target_url'):
        groups = [{r[key] for r in part} for part in (train, validation, test)]
        if any(groups[a] & groups[b] for a, b in ((0, 1), (0, 2), (1, 2))):
            raise ValueError(f'Cross-partition overlap: {key}')
    for part in (train, validation, test):
        if len({r['session_id'] for r in part}) != len(part):
            raise ValueError('Duplicate session in partition')


def inner_indices(rows, partition_seed=None):
    groups = np.asarray([r['target_url'] for r in rows])
    if partition_seed is None:
        yield from GroupKFold(3).split(np.zeros(len(rows)), groups=groups)
        return
    urls = np.asarray(sorted(set(groups)))
    if len(urls) < 3:
        raise ValueError('Too few URL groups')
    shuffled = np.random.default_rng(partition_seed).permutation(urls)
    for held in np.array_split(shuffled, 3):
        mask = np.isin(groups, held)
        yield np.flatnonzero(~mask), np.flatnonzero(mask)


def reference_evaluate(rows, spec, view, cfg, partition_seed=None):
    """Real-pair scalar reference with fresh fits in every inner/outer fold."""
    predictions, tuning, splits = [], [], []
    for url in sorted({r['target_url'] for r in rows}):
        train = [r for r in rows if r['target_url'] != url]
        test = [r for r in rows if r['target_url'] == url]
        x = build_matrix(train, spec, view)
        y = np.asarray([int(r['protocol'] == 'VLESS') for r in train])
        losses = defaultdict(list)
        for fold, (tr, va) in enumerate(inner_indices(train, partition_seed)):
            a, b = [train[i] for i in tr], [train[i] for i in va]
            assert_partition(a, b, test)
            splits.append({'outer_url': url, 'inner_fold': fold,
                           'train_ids': [r['session_id'] for r in a],
                           'validation_ids': [r['session_id'] for r in b],
                           'test_ids': [r['session_id'] for r in test]})
            for c in cfg['classification_C']:
                model = fit_model(x[tr], y[tr], c, cfg['seed'])
                losses[c].extend(loss_bits(y[va], model.predict_proba(x[va])[:, 1]))
        chosen = min(cfg['classification_C'], key=lambda c: (np.mean(losses[c]), c))
        model = fit_model(x, y, chosen, cfg['seed'])
        probabilities = model.predict_proba(build_matrix(test, spec, view))[:, 1]
        for row, probability in zip(test, probabilities):
            predictions.append({
                'session_id': row['session_id'], 'target_url': url,
                'protocol': row['protocol'], 'truth': int(row['protocol'] == 'VLESS'),
                'view': view, 'prob_vless': float(probability), 'selected_C': chosen,
                'fold': url, 'observation_level': cfg['observation_level'],
            })
        tuning.append({'fold': url, 'selected_C': chosen,
                       'inner_losses': {str(c): float(np.mean(v)) for c, v in losses.items()}})
    return predictions, tuning, splits
