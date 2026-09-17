"""Training-only nested calibration and URL-held-out recovery diagnostics."""
import argparse
from collections import defaultdict
import json
from pathlib import Path

import numpy as np
from scipy.optimize import minimize_scalar
from scipy.special import expit, logit
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import GroupKFold
import yaml

from ..information_validation.experiments import pipeline, bit_loss
from ..reproducibility.preflight import write_json, write_table
from .experiments import evaluate
from .pairing import matrix
from .prepare import load_config, table, metrics, digest


def temperature(y, probability):
    logits = logit(np.clip(probability, 1e-12, 1-1e-12))
    result = minimize_scalar(lambda log_t: float(np.mean(bit_loss(y, expit(logits/np.exp(log_t))))),
                             bounds=(-4., 4.), method='bounded')
    if not result.success: raise ValueError('temperature optimization failed')
    return float(np.exp(result.x))


def calibrate(root, rows, spec, cfg):
    out = root/'calibration'; out.mkdir(exist_ok=False)
    summaries = []
    for source in sorted((root/'views').glob('*-oof.parquet')):
        original = table(source); view = original[0]['view']
        predictions, fitted, calibration_oof = [], [], []
        for url in sorted({r['target_url'] for r in rows}):
            train = [r for r in rows if r['target_url'] != url]
            inner_predictions, _, _ = evaluate(train, spec, view, cfg, cfg['seed'], False)
            t = temperature([r['truth'] for r in inner_predictions],
                            [r['prob_vless'] for r in inner_predictions])
            calibration_oof.extend({**r, 'outer_test_url': url} for r in inner_predictions)
            fitted.append({'outer_test_url': url, 'temperature': t,
                           'training_session_ids': [r['session_id'] for r in train]})
            for r in original:
                if r['target_url'] == url:
                    probability = float(expit(logit(np.clip(r['prob_vless'], 1e-12, 1-1e-12))/t))
                    predictions.append({**r, 'prob_vless': probability, 'calibration': 'nested_group_oof_temperature'})
        write_table(out/f'{view}-oof.parquet', predictions)
        write_table(out/f'{view}-training-oof.parquet', calibration_oof)
        write_json(out/f'{view}-temperatures.json', fitted)
        result = {'view': view, **metrics(predictions)}
        summaries.append(result); print(json.dumps(result), flush=True)
    write_table(out/'summary.parquet', summaries)


def recover(root, rows, spec, cfg):
    out = root/'recovery'; out.mkdir(exist_ok=False)
    scalar = [m for m in spec if m['transform'] != 'distance' and m['id'] != 'entity_count']
    delta = [m for m in spec if m['id'] != 'entity_count']
    x, _ = matrix(rows, spec, 'post'); d, _ = matrix(rows, spec, 'delta_distribution')
    groups = np.asarray([r['target_url'] for r in rows])
    predictions = []
    targets = ['packet_count', 'transport_bytes', 'burst_count', 'fr_runs', 'length_js', 'iat_js']
    for target in targets:
        metric = next(m for m in spec if m['id']==target)
        y = d[:, [m['id'] for m in delta].index(target)]
        if not np.isfinite(y).all(): raise ValueError(f'missing target must define cohort: {target}')
        for url in sorted(set(groups)):
            train, test = np.flatnonzero(groups != url), np.flatnonzero(groups == url)
            scale = float(np.std(y[train]))
            for model_name in ['train_mean', 'known_deployment_mean_oracle', 'ridge_fixed',
                               'ridge_tuned', 'ridge_drop_family']:
                columns = [i for i, m in enumerate(scalar)
                           if model_name != 'ridge_drop_family' or m['family'] != metric['family']]
                selected = 1.
                if model_name == 'train_mean': prediction = np.repeat(y[train].mean(), len(test))
                elif model_name == 'known_deployment_mean_oracle':
                    prediction = [np.mean([y[j] for j in train if rows[j]['protocol']==rows[i]['protocol']]) for i in test]
                else:
                    if model_name == 'ridge_tuned':
                        scores = defaultdict(list)
                        for tr, va in GroupKFold(n_splits=3).split(train, groups=groups[train]):
                            for alpha in [.1, 1., 10., 100.]:
                                model = pipeline(Ridge(alpha=alpha))
                                model.fit(x[train[tr]][:, columns], y[train[tr]])
                                scores[alpha].extend(np.abs(model.predict(x[train[va]][:, columns])-y[train[va]]))
                        selected = min(scores, key=lambda a: (np.mean(scores[a]), a))
                    model = pipeline(Ridge(alpha=selected))
                    model.fit(x[train][:, columns], y[train])
                    prediction = model.predict(x[test][:, columns])
                predictions.extend({'target': target, 'model': model_name, 'session_id': rows[i]['session_id'],
                    'target_url': url, 'truth': float(y[i]), 'prediction': float(p), 'training_target_std': scale,
                    'selected_alpha': selected, 'n_features': len(columns)} for i, p in zip(test, prediction))
    write_table(out/'oof.parquet', predictions)
    groups_result = defaultdict(list)
    for r in predictions: groups_result[(r['target'], r['model'])].append(r)
    result = []
    for (target, model), group in groups_result.items():
        y, p = [r['truth'] for r in group], [r['prediction'] for r in group]
        result.append({'target': target, 'model': model, 'n': len(group), 'mae': float(mean_absolute_error(y,p)),
            'r2': float(r2_score(y,p)) if np.var(y)>0 else None,
            'target_variance': float(np.var(y)),
            'normalized_mae': float(np.mean([abs(r['truth']-r['prediction'])/r['training_target_std']
                                 for r in group])) if all(r['training_target_std']>0 for r in group) else None})
    write_table(out/'summary.parquet', result)
    print(json.dumps(result), flush=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config', default='configs/paired-information-0914.yaml')
    p.add_argument('--stage', choices=['calibration', 'recovery'], required=True)
    args = p.parse_args(); cfg = load_config(args.config); root = Path(cfg['output_root'])
    manifest = json.loads((root/'source-manifest.json').read_text())
    for path, value in manifest['sources'].items():
        if digest(Path(path)) != value: raise ValueError('source changed')
    rows = [r for r in table(root/'side-summaries.parquet')
            if r['scope']==cfg['scope'] and r['selection']==cfg['selection']]
    spec = yaml.safe_load(Path(cfg['spec']).read_text())['metrics']
    if args.stage == 'calibration': calibrate(root, rows, spec, cfg)
    else: recover(root, rows, spec, cfg)
    write_json(root/args.stage/'run.json', {'config': cfg, 'code_sha256': digest(Path(__file__)),
               'input_sha256': digest(root/'side-summaries.parquet')})


if __name__ == '__main__': main()
