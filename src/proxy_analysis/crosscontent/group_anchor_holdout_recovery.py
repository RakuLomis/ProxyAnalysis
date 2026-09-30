"""Frozen SSL-head inference and outer-training-only univariate Ridge references."""
import argparse
import numpy as np
import pyarrow
import torch
from sklearn.linear_model import Ridge

from .group_anchor_diagnostics_contract import CONFIG, verify, validate_input
from .group_anchor_reliability import feature_groups
from .natural_pair_ssl import networks, restore
from .natural_pair_ssl_report import mlp
from .mechanism_contract import read
from .paired_structure_contract import seal, validate_complete
from ..paired_information.prepare import digest
from ..reproducibility.preflight import write_json, write_table


def ridge_fit(train, mismatched, alpha):
    x = np.asarray(train['post']); y = np.asarray(train['pre_target']); mask = np.asarray(train['target_mask'])
    donors = train['donors'] if mismatched else np.arange(len(x))
    y = y[donors]; mask = mask[donors]
    coefficients = np.zeros(157); intercepts = np.zeros(157); fits = 0; worst = 0.
    for j in range(157):
        valid = mask[:, j]
        if not valid.any(): continue
        a = x[valid, j]; b = y[valid, j]
        model = Ridge(alpha=alpha).fit(a[:, None], b)
        coef = np.dot(a-a.mean(), b-b.mean())/(np.dot(a-a.mean(), a-a.mean())+alpha)
        intercept = b.mean()-coef*a.mean()
        worst = max(worst, float(abs(model.predict(x[:, j:j+1])-(x[:, j]*coef+intercept)).max()))
        coefficients[j] = model.coef_[0]; intercepts[j] = model.intercept_; fits += 1
    if worst > 1e-9: raise ValueError('Closed-form Ridge replay differs')
    return {'coef': coefficients.tolist(), 'intercept': intercepts.tolist(), 'fits': fits,
        'max_closed_form_error': worst, 'train_ids': [r['session_id'] for r in train['rows']],
        'donor_ids': [train['rows'][i]['session_id'] for i in donors], 'alpha': alpha}


def ridge_predict(fit, inputs):
    x = validate_input(inputs)
    return x*np.asarray(fit['coef'])+np.asarray(fit['intercept'])


def neural_predict(fit, inputs):
    x = validate_input(inputs); h = mlp(x, fit['encoder']); result = np.zeros_like(x)
    for i, g in enumerate(feature_groups()):
        result[:, g['indices']] = h@np.asarray(fit['heads'][f'{i}.weight']).T+fit['heads'][f'{i}.bias']
    return result


def torch_replay(fit, inputs):
    encoder, _ = networks(0); restore(encoder, fit['encoder'])
    x = torch.tensor(validate_input(inputs), dtype=torch.float64); result = np.zeros(x.shape)
    with torch.no_grad():
        h = encoder(x)
        for i, g in enumerate(feature_groups()):
            w = torch.tensor(fit['heads'][f'{i}.weight'], dtype=torch.float64)
            b = torch.tensor(fit['heads'][f'{i}.bias'], dtype=torch.float64)
            result[:, g['indices']] = (h@w.T+b).numpy()
    return result


def run(config=CONFIG):
    cfg, anchor, root = verify(config); out = root/'recovery'
    if (out/'complete.json').exists(): validate_complete(out); return
    if out.exists(): raise FileExistsError('Partial recovery exists; explicit recovery review required')
    predictions = []; ridge_count = 0; checkpoints = []; worst = 0.
    for fold in range(cfg['folds']):
        train = read(root/'packages'/f'fold-{fold}.train.json'); inputs = read(root/'packages'/f'fold-{fold}.input.json')
        train_inputs = {'fold': fold, 'session_ids': [r['session_id'] for r in train['rows']], 'post': train['post']}
        def save(model, seed, split, bundle, values):
            if not np.isfinite(values).all(): raise ValueError('Nonfinite auxiliary predictions')
            predictions.extend({'fold': fold, 'session_id': sid, 'model': model, 'seed': seed,
                                'split': split, 'prediction': value.tolist()}
                               for sid, value in zip(bundle['session_ids'], values))
        for split, bundle in (('train', train_inputs), ('test', inputs)):
            save('Mean', None, split, bundle, np.zeros_like(validate_input(bundle)))
        for mismatched in (False, True):
            name = 'Ridge-wrong' if mismatched else 'Ridge-true'
            fit = ridge_fit(train, mismatched, cfg['ridge_alpha']); ridge_count += fit['fits']
            write_json(out/'fits'/f'fold-{fold}-{name}.json', fit)
            for split, bundle in (('train', train_inputs), ('test', inputs)):
                save(name, None, split, bundle, ridge_predict(fit, bundle))
        for arm in cfg['arms']:
            for seed in cfg['seeds']:
                path = anchor/'jobs'/f'six_business-{fold}-{seed}-{arm}'/'ssl-fit.json'; fit = read(path)
                if fit['arm'] != arm or fit['seed'] != seed or fit['train_ids'] != train_inputs['session_ids']:
                    raise ValueError('Checkpoint identity differs')
                for split, bundle in (('train', train_inputs), ('test', inputs)):
                    values = neural_predict(fit, bundle)
                    worst = max(worst, float(abs(values-torch_replay(fit, bundle)).max()))
                    save(arm, seed, split, bundle, values)
                checkpoints.append({'fold': fold, 'arm': arm, 'seed': seed, 'path': str(path), 'sha256': digest(path)})
        print(f'recovery fold {fold}: frozen heads plus two Ridge references; no test pre loaded', flush=True)
    if ridge_count > cfg['ridge_fit_limit'] or len(checkpoints) != 60 or worst > 1e-9:
        raise ValueError('Recovery budget or forward replay failed')
    write_table(out/'predictions.parquet', predictions); write_json(out/'checkpoints.json', checkpoints)
    write_json(out/'validation.json', {'passed': True, 'ridge_fits': ridge_count, 'neural_fits': 0,
        'checkpoints': 60, 'prediction_vectors': len(predictions), 'max_forward_replay_error': worst,
        'test_targets_or_business_labels_used_by_predictors': False})
    seal(out, passed=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--config', default=str(CONFIG)); args = parser.parse_args(); run(args.config)
