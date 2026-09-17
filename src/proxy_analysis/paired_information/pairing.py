"""Partition-local pairing and matched-information representations."""
from collections import defaultdict
import hashlib

import numpy as np

from ..reproducibility.extract import compare


def pairing(rows, seed, wrong=False):
    if len({r['session_id'] for r in rows}) != len(rows):
        raise ValueError('duplicate partition session')
    groups = defaultdict(list)
    for i, row in enumerate(rows):
        groups[(row['target_url'], row['protocol'])].append(i)
    donors = list(range(len(rows)))
    for key, indices in sorted(groups.items()):
        if not wrong: continue
        if len(indices) < 2: raise ValueError('not_estimable: singleton pairing stratum')
        if len({rows[i]['repetition'] for i in indices}) != len(indices):
            raise ValueError('duplicate repetition in pairing stratum')
        indices.sort(key=lambda i: rows[i]['session_id'])
        local_seed = int.from_bytes(hashlib.sha256(repr((seed, key)).encode()).digest()[:8])
        rng = np.random.default_rng(local_seed)
        while True:
            proposed = rng.permutation(indices).tolist()
            if all(a != b for a, b in zip(indices, proposed)): break
        for receiver, donor in zip(indices, proposed): donors[receiver] = donor
    mappings = []
    for receiver, donor in enumerate(donors):
        a, b = rows[receiver], rows[donor]
        mappings.append({'receiver_session_id': a['session_id'], 'donor_session_id': b['session_id'],
                         'target_url': a['target_url'], 'protocol': a['protocol'],
                         'receiver_repetition': a['repetition'], 'donor_repetition': b['repetition'],
                         'wrong': wrong, 'seed': seed})
    return donors, mappings


def matrix(rows, spec, view, *, seed=0, wrong=False):
    donors, mapping = pairing(rows, seed, wrong)
    scalar = [m for m in spec if m['transform'] != 'distance' and m['id'] != 'entity_count']
    delta = [m for m in spec if m['id'] != 'entity_count']
    def values(summary): return [summary.get(m['id']) for m in scalar]
    def distribution(summary):
        result = []
        for name in ('length_hist', 'iat_hist'):
            counts = np.asarray(summary[name], dtype=float)
            result.extend((counts / counts.sum()).tolist() if counts.sum() else [None]*len(counts))
        result.extend(summary['curve'] if summary['curve'] is not None else [None]*101)
        return result
    vectors = []
    for i, row in enumerate(rows):
        pre, post = rows[donors[i]]['pre'], row['post']
        if view == 'pre': vector = values(pre)
        elif view == 'post': vector = values(post)
        elif view == 'joint_scalar': vector = values(pre) + values(post)
        elif view == 'joint_distribution':
            vector = values(pre) + values(post) + distribution(pre) + distribution(post)
        elif view in {'delta_scalar', 'delta_distribution'}:
            vector = [r['delta'] for r in compare(pre, post,
                scalar if view == 'delta_scalar' else delta, True)]
        elif view.startswith('pre_family:'):
            vector = [pre.get(m['id']) for m in scalar if m['family'] == view.split(':')[1]]
        elif view.startswith('pre_without:'):
            vector = [pre.get(m['id']) for m in scalar if m['family'] != view.split(':')[1]]
        else: raise ValueError(f'unknown view: {view}')
        vectors.append(vector)
    return np.asarray(vectors, dtype=float), mapping
