"""Training-only, content-crossfitted same-coordinate anchor reliability."""
from collections import defaultdict
import numpy as np
from sklearn.linear_model import Ridge

from .business_representations import dictionary
from .natural_pair_ssl_data import cyclic_donors


def feature_groups():
    names = dictionary()['distribution157']
    blocks = [
        ('G1', ['transport_bytes', 'ip_bytes', 'up_transport_bytes', 'down_transport_bytes']),
        ('G2', ['up_byte_fraction', 'direction_entropy']),
        ('G3', ['fr_runs', 'fr_switches', 'fr_runs_per_packet', 'transition_p_pm']),
        ('G4', ['packet_count', 'burst_count', 'length_median'] + [f'length_p_{i}' for i in range(19)]),
        ('G5', ['iat_median_us'] + [f'iat_p_{i}' for i in range(23)]),
        ('G6', [f'curve_{i}' for i in range(101)]),
    ]
    groups = [{'group': g, 'names': nn, 'indices': [names.index(n) for n in nn]} for g, nn in blocks]
    if sorted(j for g in groups for j in g['indices']) != list(range(157)):
        raise ValueError('Groups must partition 157 dimensions exactly once')
    return groups


def normalize_fit(raw, eps=1e-12):
    raw = np.asarray(raw, float)
    if np.isinf(raw).any():
        raise ValueError('Infinite input')
    median = []; mean = []; scale = []; valid = []
    for x in raw.T:
        v = x[np.isfinite(x)]
        med = float(np.median(v)) if len(v) else 0.
        mu = float(v.mean()) if len(v) else 0.
        var = float(v.var()) if len(v) else 0.
        median.append(med); mean.append(mu); scale.append(np.sqrt(var) if var >= eps else 1.)
        valid.append(bool(len(v) >= 2 and var >= eps))
    return {'median': median, 'mean': mean, 'scale': scale, 'valid': valid}


def normalized(raw, state):
    x = np.asarray(raw, float)
    return (np.where(np.isfinite(x), x, state['median']) - state['mean']) / state['scale']


def inner_splits(rows):
    # Labels organize the inherited balanced split only, never a scoring target.
    by_label = defaultdict(set)
    for r in rows:
        by_label[r['label_id']].add(r['content_id'])
    if any(len(v) != 4 for v in by_label.values()):
        raise ValueError('Expected four outer-training contents per business')
    assignments = {c: i for values in by_label.values() for i, c in enumerate(sorted(values))}
    return [([i for i, r in enumerate(rows) if assignments[r['content_id']] != fold],
             [i for i, r in enumerate(rows) if assignments[r['content_id']] == fold]) for fold in range(4)]


def aggregate(rows, squared, null_squared, groups, eps=1e-12):
    """Equal dimensions within visit, equal repetitions within content, then contents."""
    scores = []; reliability = []
    for g in groups:
        skills = []
        for protocol in sorted({r['protocol'] for r in rows}):
            per_content = defaultdict(list)
            for i, r in enumerate(rows):
                if r['protocol'] != protocol:
                    continue
                jj = g['indices']
                good = np.isfinite(squared[i, jj]) & np.isfinite(null_squared[i, jj])
                if good.any():
                    per_content[r['content_id']].append((float(squared[i, jj][good].mean()),
                                                         float(null_squared[i, jj][good].mean())))
            values = [np.mean(v, axis=0) for v in per_content.values()]
            pred, null = np.mean(values, axis=0) if values else (None, None)
            skill = float(1-pred/null) if null is not None and null > eps else None
            skills.append(skill)
            scores.append({'group': g['group'], 'protocol': protocol,
                           'prediction_mse': None if pred is None else float(pred),
                           'null_mse': None if null is None else float(null), 'skill': skill,
                           'contents': len(values), 'reason': None if skill is not None else 'undefined_null',
                           'content_errors': [{'content_id': c, 'prediction_mse': float(np.mean(v, axis=0)[0]),
                                               'null_mse': float(np.mean(v, axis=0)[1])}
                                              for c, v in sorted(per_content.items())]})
        reliability.append(max(0., min(skills)) if all(s is not None for s in skills) else 0.)
    total = sum(reliability)
    return {'scores': scores, 'reliability': reliability,
            'weights': [v/total for v in reliability] if total else [0.]*len(groups),
            'passed': total > 0}


def crossfit(rows, post, pre, relation, groups=None, alpha=1., eps=1e-12):
    """Receives ONLY outer-training arrays; no evaluation arrays or protocol inputs."""
    if relation not in ('true', 'mismatched'):
        raise ValueError('Unknown relation')
    groups = feature_groups() if groups is None else groups
    post = np.asarray(post, float); pre = np.asarray(pre, float)
    if post.shape != pre.shape or post.shape != (len(rows), 157):
        raise ValueError('Invalid training shape')
    sq = np.full_like(pre, np.nan); nullsq = sq.copy(); observations = []; fits = []; splits = []
    for fold, (train, val) in enumerate(inner_splits(rows)):
        tr = [rows[i] for i in train]; va = [rows[i] for i in val]
        dt = cyclic_donors(tr) if relation == 'mismatched' else list(range(len(tr)))
        dv = cyclic_donors(va) if relation == 'mismatched' else list(range(len(va)))
        target_train = pre[np.asarray(train)[dt]]; target_val = pre[np.asarray(val)[dv]]
        xs = normalize_fit(post[train], eps); ys = normalize_fit(target_train, eps)
        xt = normalized(post[train], xs); xv = normalized(post[val], xs)
        yt = normalized(target_train, ys); yv = normalized(target_val, ys)
        splits.append({'inner_fold': fold, 'train_ids': [r['session_id'] for r in tr],
                       'validation_ids': [r['session_id'] for r in va],
                       'train_donor_ids': [tr[i]['session_id'] for i in dt],
                       'validation_donor_ids': [va[i]['session_id'] for i in dv],
                       'post_scaler': xs, 'pre_scaler': ys})
        for j in range(157):
            if not ys['valid'][j]:
                continue
            mask = np.isfinite(target_train[:, j]); valid = np.isfinite(target_val[:, j])
            model = Ridge(alpha=alpha).fit(xt[mask, j:j+1], yt[mask, j])
            predicted = model.predict(xv[:, j:j+1])
            # Independent closed-form replay, not another estimator invocation.
            a = xt[mask, j]; b = yt[mask, j]
            coef = np.dot(a-a.mean(), b-b.mean()) / (np.dot(a-a.mean(), a-a.mean())+alpha)
            intercept = b.mean()-coef*a.mean()
            if not np.allclose(predicted, xv[:, j]*coef+intercept, rtol=1e-10, atol=1e-10):
                raise ValueError('Independent Ridge replay failed')
            fits.append({'inner_fold': fold, 'feature_index': j, 'coef': float(model.coef_[0]),
                         'intercept': float(model.intercept_), 'training_targets': int(mask.sum())})
            for k, i in enumerate(val):
                if not valid[k]:
                    continue
                sq[i, j] = (predicted[k]-yv[k, j])**2; nullsq[i, j] = yv[k, j]**2
                observations.append({'session_id': rows[i]['session_id'], 'content_id': rows[i]['content_id'],
                                     'protocol': rows[i]['protocol'], 'repetition': rows[i]['repetition'],
                                     'donor_id': va[dv[k]]['session_id'], 'inner_fold': fold,
                                     'feature_index': j, 'target_z': float(yv[k, j]),
                                     'prediction_z': float(predicted[k]), 'squared_error': float(sq[i, j]),
                                     'null_squared_error': float(nullsq[i, j])})
    result = aggregate(rows, sq, nullsq, groups, eps)
    permuted = [{**g, 'indices': g['indices'][::-1]} for g in groups]
    if not np.allclose(result['weights'], aggregate(rows, sq, nullsq, permuted, eps)['weights'], atol=1e-12):
        raise ValueError('Group order invariance failed')
    return {**result, 'relation': relation, 'fits': fits, 'splits': splits,
            'fit_count': len(fits), 'skipped_dimensions': 4*157-len(fits)}, observations


def delta_diagnostics(rows, pre, post):
    """Training-only raw paired differences and within-content repeat dispersion."""
    result = []
    for protocol in sorted({r['protocol'] for r in rows}):
        for j, name in enumerate(dictionary()['distribution157']):
            parts = defaultdict(list)
            for i, r in enumerate(rows):
                if r['protocol'] == protocol and np.isfinite(pre[i, j]) and np.isfinite(post[i, j]):
                    parts[r['content_id']].append(float(post[i, j]-pre[i, j]))
            all_values = [x for v in parts.values() for x in v]
            if all_values:
                result.append({'protocol': protocol, 'feature': name, 'median_post_minus_pre': float(np.median(all_values)),
                               'median_repeat_mad': float(np.median([np.median(abs(np.array(v)-np.median(v))) for v in parts.values()])),
                               'median_repeat_iqr': float(np.median([np.subtract(*np.quantile(v, [.75, .25])) for v in parts.values()]))})
    return result
