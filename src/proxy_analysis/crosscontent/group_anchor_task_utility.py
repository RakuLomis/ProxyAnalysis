"""Fixed raw-post logistic regression on full, single and leave-group-out inputs."""
import argparse
import numpy as np
from sklearn.linear_model import LogisticRegression

from .group_anchor_diagnostics_contract import CONFIG, verify, validate_input
from .group_anchor_reliability import feature_groups
from .natural_pair_ssl_report import softmax
from .mechanism_contract import read
from .paired_structure_contract import seal, validate_complete
from ..reproducibility.preflight import write_json, write_table


def subsets():
    result = {'Full': list(range(157))}
    for g in feature_groups():
        result['Only-'+g['group']] = g['indices']
        result['Minus-'+g['group']] = [j for j in range(157) if j not in g['indices']]
    return result


def predict(fit, inputs):
    x = validate_input(inputs)[:, fit['indices']]
    return softmax(x@np.asarray(fit['coef']).T+fit['intercept'])


def run(config=CONFIG):
    cfg, _, root = verify(config); out = root/'utility'
    if (out/'complete.json').exists(): validate_complete(out); return
    predictions = []; count = 0; worst = 0.
    for fold in range(cfg['folds']):
        train = read(root/'packages'/f'fold-{fold}.train.json'); inputs = read(root/'packages'/f'fold-{fold}.input.json')
        x = np.asarray(train['post']); xt = validate_input(inputs)
        y = [train['labels'].index(r['label_id']) for r in train['rows']]
        for name, indices in subsets().items():
            path = out/'fits'/f'fold-{fold}-{name}.json'
            if path.exists(): raise FileExistsError('Partial fit output exists; review rather than refit silently')
            model = LogisticRegression(C=cfg['classifier_C'], solver='lbfgs', max_iter=cfg['classifier_max_iter'],
                tol=cfg['classifier_tol'], random_state=20260919).fit(x[:, indices], y)
            if model.n_iter_.max() >= cfg['classifier_max_iter']: raise ValueError('LR did not converge')
            fit = {'indices': indices, 'coef': model.coef_.tolist(), 'intercept': model.intercept_.tolist(),
                'classes': model.classes_.tolist(), 'labels': train['labels'], 'n_iter': model.n_iter_.tolist(),
                'train_ids': [r['session_id'] for r in train['rows']], 'fold': fold, 'subset': name}
            p = predict(fit, inputs)
            worst = max(worst, float(abs(p-model.predict_proba(xt[:, indices])).max()))
            write_json(path, fit); count += 1
            predictions.extend({'session_id': sid, 'fold': fold, 'subset': name, 'probabilities': v.tolist(),
                                'labels': train['labels']} for sid, v in zip(inputs['session_ids'], p))
        prior = np.bincount(y, minlength=len(train['labels']))/len(y)
        predictions.extend({'session_id': sid, 'fold': fold, 'subset': 'Prior', 'probabilities': prior.tolist(),
                            'labels': train['labels']} for sid in inputs['session_ids'])
        print(f'utility fold {fold}: 13 fits, no evaluation targets loaded', flush=True)
    if count != 65 or worst > 1e-10: raise ValueError('LR budget/replay failed')
    write_table(out/'predictions.parquet', predictions)
    write_json(out/'validation.json', {'passed': True, 'fits': count, 'predictions': len(predictions),
        'max_numpy_replay_error': worst, 'test_pre_or_labels_used_for_fitting': False})
    seal(out, passed=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--config', default=str(CONFIG)); args = parser.parse_args(); run(args.config)
