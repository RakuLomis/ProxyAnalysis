"""Train-only preprocessing and label-free natural-pair input contract."""
from collections import defaultdict
import hashlib
import json

import numpy as np
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler

from .business_representations import matrix, dictionary


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, allow_nan=False).encode()).hexdigest()


def cyclic_donors(rows):
    groups = defaultdict(list)
    for i, row in enumerate(rows):
        groups[row['protocol'], row['content_id']].append(i)
    donors = list(range(len(rows)))
    for indices in groups.values():
        indices.sort(key=lambda i: rows[i]['repetition'])
        if [rows[i]['repetition'] for i in indices] != [1, 2, 4, 5]:
            raise ValueError('Expected exactly four frozen repetitions')
        for i, j in zip(indices, indices[1:] + indices[:1]):
            donors[i] = j
    if sorted(donors) != list(range(len(rows))) or any(i == j for i, j in enumerate(donors)):
        raise ValueError('Donor mapping is not a fixed-point-free permutation')
    return donors


def apply_preprocessing(raw, state):
    raw = np.asarray(raw, dtype=float)
    return (np.where(np.isnan(raw), state['median'], raw) - state['mean']) / state['scale']


def prepare_train(rows):
    """Only allowed training rows; label values are never read by this function."""
    rows = sorted(rows, key=lambda r: r['session_id'])
    post = matrix(rows, 'post', 'distribution157')
    imp = SimpleImputer(strategy='median', keep_empty_features=True).fit(post)
    scaler = StandardScaler().fit(imp.transform(post))
    state = {'median': imp.statistics_.tolist(), 'mean': scaler.mean_.tolist(),
             'scale': scaler.scale_.tolist(), 'variance': scaler.var_.tolist()}
    pre = apply_preprocessing(matrix(rows, 'pre', 'distribution157'), state)
    post = apply_preprocessing(post, state)
    if not np.isfinite(pre).all() or not np.isfinite(post).all():
        raise ValueError('Nonfinite train-only preprocessing')
    names = dictionary()['distribution157']
    diagnostics = [{'feature': name, 'post_variance': state['variance'][i],
                    'pre_max_abs_z': float(abs(pre[:, i]).max()),
                    'post_max_abs_z': float(abs(post[:, i]).max())} for i, name in enumerate(names)]
    ssl = {'session_ids': [r['session_id'] for r in rows], 'pre': pre.tolist(),
           'post': post.tolist(), 'donor_indices': cyclic_donors(rows)}
    return ssl, state, diagnostics


def audit_partition(train, test, captures):
    for key in ('session_id', 'content_id'):
        if {r[key] for r in train} & {r[key] for r in test}:
            raise ValueError(f'Train/test overlap: {key}')
    # Normalize serialized Windows paths, including doubled separators.
    def paths(rows):
        result = set()
        for row in rows:
            entries = captures.get(row['session_id'], [])
            if not entries:
                raise ValueError('Missing capture audit')
            for entry in entries:
                p = entry['path'].replace('\\', '/').lower()
                while '//' in p:
                    p = p.replace('//', '/')
                result.add(p)
        return result
    a, b = paths(train), paths(test)
    if a & b:
        raise ValueError('Raw capture path crosses split')
    return {'train_visits': len(train), 'test_visits': len(test),
            'train_contents': len({r['content_id'] for r in train}),
            'test_contents': len({r['content_id'] for r in test}),
            'train_captures': len(a), 'test_captures': len(b), 'overlaps': 0}
