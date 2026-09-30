"""Training-only nested descriptive sums of squares and cross-side covariance."""
import argparse
from collections import defaultdict
import numpy as np

from .group_anchor_diagnostics_contract import CONFIG, verify
from .group_anchor_reliability import feature_groups
from .natural_pair_ssl_data import cyclic_donors
from .mechanism_contract import read
from .paired_structure_contract import seal, validate_complete
from ..reproducibility.preflight import write_json, write_table

LEVELS = ('business', 'content', 'visit')


def components(x, rows):
    x = np.asarray(x, float); centered = x-x.mean(); business = np.zeros_like(x); content = np.zeros_like(x)
    for label in sorted({r['label_id'] for r in rows}):
        indices = [i for i, r in enumerate(rows) if r['label_id'] == label]
        business[indices] = x[indices].mean()-x.mean()
    for item in sorted({r['content_id'] for r in rows}):
        indices = [i for i, r in enumerate(rows) if r['content_id'] == item]
        if len({rows[i]['label_id'] for i in indices}) != 1: raise ValueError('Content crosses business')
        content[indices] = x[indices].mean()-x.mean()-business[indices]
    visit = centered-business-content
    return np.stack([business, content, visit])


def decompose(pre, post, rows, eps=1e-12):
    pre = np.asarray(pre, float); post = np.asarray(post, float)
    if not np.isfinite(pre).all() or not np.isfinite(post).all(): raise ValueError('Only complete pairs allowed')
    if len(rows) < 8 or len({r['label_id'] for r in rows}) < 2:
        return {'valid': False, 'reason': 'insufficient_groups'}
    scales = [float(pre.std()), float(post.std())]
    if min(v*v for v in scales) < eps:
        return {'valid': False, 'reason': 'constant_side'}
    a = (pre-pre.mean())/scales[0]; b = (post-post.mean())/scales[1]
    ac = components(a, rows); bc = components(b, rows)
    ae = (ac*ac).sum(1); be = (bc*bc).sum(1); cov = (ac*bc).sum(1)
    at = float(a@a); bt = float(b@b); total = float(a@b); cross = ac@bc.T
    errors = [abs(ae.sum()-at), abs(be.sum()-bt), abs(cov.sum()-total),
              abs(ac.sum(0)-a).max(), abs(bc.sum(0)-b).max(),
              abs(cross-np.diag(np.diag(cross))).max(),
              abs(ac@ac.T-np.diag(ae)).max(), abs(bc@bc.T-np.diag(be)).max()]
    error = float(max(errors))/max(len(rows), 1)
    if error > 1e-10: raise ValueError('Hierarchical identity failed')
    levels = []
    for i, level in enumerate(LEVELS):
        denominator = float(np.sqrt(ae[i]*be[i]))
        levels.append({'level': level, 'pre_energy': float(ae[i]/at), 'post_energy': float(be[i]/bt),
            'covariance_standardized': float(cov[i]/len(rows)),
            'covariance_raw': float(cov[i]/len(rows)*scales[0]*scales[1]),
            'correlation': float(cov[i]/denominator) if denominator > eps*len(rows) else None,
            'signed_total_contribution': float(cov[i]/np.sqrt(at*bt))})
    return {'valid': True, 'pre_mean': float(pre.mean()), 'post_mean': float(post.mean()),
        'pre_scale': scales[0], 'post_scale': scales[1], 'total_correlation': total/np.sqrt(at*bt),
        'identity_error': error, 'levels': levels}


def run(config=CONFIG):
    cfg, _, root = verify(config); out = root/'hierarchy'
    if (out/'complete.json').exists(): validate_complete(out); return
    records = []; groups = feature_groups(); feature_group = {j:g['group'] for g in groups for j in g['indices']}
    names = {j:n for g in groups for j,n in zip(g['indices'], g['names'])}; worst = 0.; valid_count = 0
    for fold in range(cfg['folds']):
        train = read(root/'packages'/f'fold-{fold}.train.json')
        pre = np.asarray(train['raw_pre'], float); post = np.asarray(train['raw_post'], float)
        for protocol in sorted({r['protocol'] for r in train['rows']}):
            all_indices = [i for i, r in enumerate(train['rows']) if r['protocol'] == protocol]
            blocks = defaultdict(list)
            for i in all_indices: blocks[train['rows'][i]['content_id']].append(i)
            for j in range(157):
                indices = [i for block in blocks.values() if len(block) == 4 and
                           np.isfinite(pre[block, j]).all() and np.isfinite(post[block, j]).all() for i in block]
                rows = [train['rows'][i] for i in indices]
                base = {'fold': fold, 'protocol': protocol, 'feature_index': j, 'feature': names[j], 'group': feature_group[j],
                    'included_contents': len(indices)//4, 'excluded_contents': len(blocks)-len(indices)//4,
                    'visits': len(indices)}
                true = decompose(pre[indices, j], post[indices, j], rows, cfg['numerical_eps'])
                if not true['valid']:
                    records.append({**base, **true, 'relation': 'true'}); continue
                donors = cyclic_donors(rows)
                wrong = decompose(pre[np.asarray(indices)[donors], j], post[indices, j], rows, cfg['numerical_eps'])
                if not wrong['valid']: raise ValueError('Permutation changed valid variance')
                for k in range(3):
                    for field in ('pre_energy','post_energy'):
                        if not np.isclose(true['levels'][k][field], wrong['levels'][k][field], atol=1e-10):
                            raise ValueError('Permutation changed energy')
                    if k < 2 and not np.isclose(true['levels'][k]['signed_total_contribution'],
                                                wrong['levels'][k]['signed_total_contribution'], atol=1e-10):
                        raise ValueError('Permutation changed business/content covariance')
                valid_count += 1
                for relation, result in (('true', true), ('mismatched', wrong)):
                    worst = max(worst, result['identity_error'])
                    records.append({**base, **result, 'relation': relation})
        print(f'hierarchy fold {fold}: training rows only; identities verified', flush=True)
    write_json(out/'per-feature.json', records)
    aggregated = defaultdict(list)
    for r in records:
        if r['valid']:
            for level in r['levels']:
                aggregated[r['fold'],r['protocol'],r['group'],r['relation'],level['level']].append(level)
    summaries = []
    for key, values in sorted(aggregated.items()):
        fold, protocol, group, relation, level = key
        result = {'fold': fold, 'protocol': protocol, 'group': group, 'relation': relation, 'level': level,
                  'valid_dimensions': len(values)}
        for field in ('pre_energy','post_energy','correlation','signed_total_contribution'):
            available = [v[field] for v in values if v[field] is not None]
            result[field] = float(np.mean(available)) if available else None
            result[field+'_dimensions'] = len(available)
        summaries.append(result)
    write_json(out/'group-levels.json', summaries)
    write_json(out/'validation.json', {'passed': True, 'feature_contexts': 5*2*157,
        'valid_feature_contexts': valid_count, 'max_identity_error_per_visit': worst,
        'test_rows_used': 0, 'overlapping_outer_training_folds_treated_as_independent': False,
        'cyclic_mean_energy_invariance': True})
    seal(out, passed=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--config', default=str(CONFIG)); args = parser.parse_args(); run(args.config)
