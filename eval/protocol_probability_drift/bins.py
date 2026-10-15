"""Fixed physical bins; zero is distinct and the upper bin is open."""
import numpy as np

BYTE_EDGES = [1, 256, 1024, 4096, 16384, 65536, 262144, 1048576]
COUNT_EDGES = [1, 2, 3, 4, 8, 16, 32, 64, 128]


def edges(feature):
    return BYTE_EDGES if feature.startswith(('W_', 'U_')) else COUNT_EDGES


def encode(values, feature, merged=False):
    x = np.asarray(values)
    if not np.isfinite(x).all() or (x < 0).any() or not np.equal(x, np.floor(x)).all():
        raise ValueError('Missing, negative, or noninteger native observation')
    b = np.searchsorted(edges(feature), x, side='right').astype(np.int64)
    return np.where(b == 0, 0, (b + 1) // 2) if merged else b


def size(feature, merged=False):
    k = len(edges(feature)) + 1
    return 1 + (k // 2) if merged else k


def load(values):
    return np.searchsorted([4096, 65536], np.asarray(values), side='right').astype(np.int64)


def labels(feature, merged=False):
    e = [0, *edges(feature)]
    labels = [str(e[i]) if e[i + 1] == e[i] + 1 else f'{e[i]}..{e[i+1]-1}'
              for i in range(len(e) - 1)] + [f'>={e[-1]}']
    if not merged:
        return labels
    return [labels[0]] + [' / '.join(labels[i:i+2]) for i in range(1, len(labels), 2)]


def schema():
    return {'byte_edges': BYTE_EDGES, 'count_edges': COUNT_EDGES,
            'rule': 'integer half-open; searchsorted right; zero separate; upper unbounded',
            'merged_rule': 'zero unchanged; merge consecutive nonzero pairs from lowest bin',
            'load_edges': [4096, 65536], 'alpha': 1, 'beta': 1,
            'test_derived_edges': False}

