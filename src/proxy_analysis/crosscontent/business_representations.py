"""Single-side, fixed-bin representations; no global learned preprocessing."""
import numpy as np

from ..paired_information.reference_retrain import SCALAR_NAMES

BOUNDED = {'fr_runs_per_packet', 'up_byte_fraction', 'transition_p_pm', 'direction_entropy'}


def probability_histogram(values, width):
    x = np.asarray(values, dtype=float)
    if x.shape != (width,) or not np.all(np.isfinite(x)) or np.any(x < 0):
        raise ValueError('Invalid frozen histogram')
    return x/x.sum() if x.sum() else np.full(width, np.nan)


def vector(summary, representation):
    scalar = np.asarray([summary.get(k) for k in SCALAR_NAMES], dtype=float)
    if representation == 'scalar14':
        return scalar
    if representation != 'distribution157':
        raise ValueError('Unknown representation')
    curve = np.asarray(summary['curve'] if summary['curve'] is not None else [np.nan]*101, dtype=float)
    if curve.shape != (101,):
        raise ValueError('Unexpected cumulative curve width')
    if np.any(np.isfinite(curve)) and (not np.all(np.isfinite(curve)) or np.any(curve < -1e-12)
            or np.any(curve > 1+1e-12) or np.any(np.diff(curve) < -1e-12)):
        raise ValueError('Invalid cumulative shape')
    return np.concatenate([scalar, probability_histogram(summary['length_hist'],19),
                           probability_histogram(summary['iat_hist'],23), curve])


def matrix(rows, side, representation):
    return np.asarray([vector(r[side],representation) for r in rows])


def transform(a, b):
    if a.shape != b.shape or a.shape[1] not in (14,157):
        raise ValueError('Invalid transformation shape')
    result = b-a
    for index, name in enumerate(SCALAR_NAMES):
        if name not in BOUNDED:
            if np.any(a[:,index]<0) or np.any(b[:,index]<0):
                raise ValueError('Negative scale feature')
            result[:,index] = np.log1p(b[:,index])-np.log1p(a[:,index])
    return result


def views(rows, representation):
    a,b = matrix(rows,'pre',representation), matrix(rows,'post',representation)
    return {'pre':a, 'post':b, 'joint':np.concatenate([a,b],axis=1), 'transformation':transform(a,b)}


def dictionary():
    names = list(SCALAR_NAMES)+[f'length_p_{i}' for i in range(19)]+[f'iat_p_{i}' for i in range(23)]+[
        f'curve_{i}' for i in range(101)]
    return {'scalar14':list(SCALAR_NAMES), 'distribution157':names,
        'histograms':'normalize_each_side_and_each_histogram_including_tails; empty_block_nan',
        'curve':'single_side_normalized_time_and_bytes_101_points',
        'transform':'log1p(post)-log1p(pre) for 10 scales; post-pre for other dimensions',
        'bounded_scalar_differences':sorted(BOUNDED), 'preprocessing':'training_only_median_then_standard_scaler',
        'metadata_in_X':False}
