"""Honest grouped OOF prediction; all model preprocessing is fit inside training."""
from __future__ import annotations

from collections import defaultdict
import math
from itertools import islice

import numpy as np
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import balanced_accuracy_score, f1_score, mean_absolute_error, r2_score
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from .data import DISTANCES, OBSERVATION, split_indices, write_table


def outer_splits(rows, scheme, config):
    splits = split_indices(rows, scheme)
    return islice(splits, 1) if config.get('smoke') else splits


def matrix(rows, view, columns):
    return np.array([[r.get(view + '__' + c) if r.get(view + '__' + c) is not None else np.nan
                      for c in columns] for r in rows], dtype=float)


def pipeline(model):
    return make_pipeline(SimpleImputer(strategy='median', keep_empty_features=True),
                         StandardScaler(), model)


def bit_loss(y, p):
    p = np.clip(np.asarray(p), 1e-12, 1 - 1e-12)
    y = np.asarray(y)
    return -(y * np.log2(p) + (1-y) * np.log2(1-p))


def entropy_binary(p):
    return float(-p*math.log2(p)-(1-p)*math.log2(1-p)) if 0 < p < 1 else 0.0


def tune_logistic(x, y, groups, config):
    folds = GroupKFold(n_splits=min(3, len(set(groups))))
    choices = []
    for c in config['classification_C']:
        losses = []
        for tr, va in folds.split(x, y, groups):
            model = pipeline(LogisticRegression(C=c, max_iter=3000, random_state=config['seed']))
            model.fit(x[tr], y[tr])
            losses.extend(bit_loss(y[va], model.predict_proba(x[va])[:, 1]))
        choices.append((float(np.mean(losses)), c))
    best = min(choices)[1]
    fitted = pipeline(LogisticRegression(C=best, max_iter=3000, random_state=config['seed']))
    fitted.fit(x, y)
    return fitted, best


def classification(data, scalar, delta, config, out):
    predictions = []
    for setting, rows in data.items():
        print('classification', setting, len(rows), flush=True)
        y = np.array([int(r['protocol'] == 'VLESS') for r in rows])
        views = {'pre': matrix(rows, 'pre', scalar), 'post': matrix(rows, 'post', scalar),
                 'delta': matrix(rows, 'delta', delta)}
        if setting == 'primary':
            views['missingness_only'] = np.isnan(views['delta']).astype(float)
            commits = sorted({r['traffictracer_commit'] for r in rows})
            views['metadata_diagnostic'] = np.array([
                [r['candidate_position'], r['run_ordinal'], r['repetition']]
                + [int(r['traffictracer_commit'] == c) for c in commits] for r in rows])
            # U is conditional information in this diagnostic, never a main input feature.
            urls = sorted({r['activity_id'] for r in rows})
            views['delta_condition_U'] = np.column_stack([
                views['delta'], [[int(r['activity_id'] == u) for u in urls] for r in rows]])
        for scheme in ['LORO', 'LOUO']:
            for held, tr, te in outer_splits(rows, scheme, config):
                group_key = 'repetition' if scheme == 'LORO' else 'activity_id'
                groups = np.array([rows[i][group_key] for i in tr])
                for view, x in views.items():
                    if view == 'delta_condition_U' and scheme != 'LORO':
                        continue
                    fitted, best = tune_logistic(x[tr], y[tr], groups, config)
                    models = [('logistic', fitted.predict_proba(x[te])[:, 1], best)]
                    if view in {'pre', 'post', 'delta'}:
                        tree = pipeline(ExtraTreesClassifier(n_estimators=100, max_depth=3,
                                           min_samples_leaf=3, random_state=config['seed'], n_jobs=1))
                        tree.fit(x[tr], y[tr])
                        models += [('extra_trees', tree.predict_proba(x[te])[:, 1], None),
                                   ('prior', np.full(len(te), y[tr].mean()), None)]
                    for name, probs, c in models:
                        if not np.isfinite(probs).all() or np.any((probs < 0) | (probs > 1)):
                            raise ValueError('invalid classifier probabilities')
                        for i, prob in zip(te, probs):
                            predictions.append({'setting': setting, 'scheme': scheme, 'fold': held,
                                'view': view, 'model': name, 'session_id': rows[i]['session_id'],
                                'target_domain': rows[i]['target_domain'], 'repetition': rows[i]['repetition'],
                                'truth': int(y[i]), 'prob_vless': float(prob), 'selected_C': c,
                                'train_n': len(tr), 'test_n': len(te), 'observation_level': OBSERVATION})
    if not config.get('smoke'):
        counts = defaultdict(int)
        for r in predictions:
            counts[(r['setting'], r['scheme'], r['view'], r['model'])] += 1
        if any(n != len(data[key[0]]) for key, n in counts.items()):
            raise ValueError('incomplete classification OOF coverage')
    write_table(out / 'classification-oof.parquet', predictions)
    return predictions


def conditional_mean(rows, train_indices, values, index, keys, median=False):
    """Training-only oracle means, explicitly falling back when a held URL is unseen."""
    selected = [k for k in train_indices if all(rows[k][f] == rows[index][f] for f in keys)]
    fallback = not selected
    selected = selected or list(train_indices)
    fn = np.median if median else np.mean
    return float(fn([values[k] for k in selected])), fallback


def dropped_columns(target, scalar, families):
    family = families[target]
    remove = {m for m in scalar if families[m] == family}
    # Explicit derived/strongly related fields beyond the nominal taxonomy.
    if target in {'packet_count', 'transport_bytes', 'burst_count', 'fr_runs'}:
        remove |= {'packet_count', 'transport_bytes', 'ip_bytes', 'up_transport_bytes',
                   'down_transport_bytes', 'burst_count', 'fr_runs', 'fr_switches',
                   'fr_runs_per_packet', 'length_median'}
    return [m for m in scalar if m not in remove]


def recoverability(data, scalar, config, metrics, out):
    result = []
    families = {m['id']: m['family'] for m in metrics}
    for setting, rows in data.items():
        print('recoverability', setting, flush=True)
        for scheme in ['LORO', 'LOUO']:
            for held, tr0, te0 in outer_splits(rows, scheme, config):
                targets = [('delta', t) for t in config['primary_targets']]
                if setting == 'primary':
                    targets += [('pre', t) for t in config['primary_targets'] if t not in DISTANCES]
                for target_view, target in targets:
                    values = np.array([r.get(target_view + '__' + target, np.nan) for r in rows], dtype=float)
                    if target_view == 'pre':
                        values = np.where(values > 0, np.log(np.maximum(values, 1e-300)), np.nan)
                    tr = np.array([i for i in tr0 if np.isfinite(values[i])])
                    te = np.array([i for i in te0 if np.isfinite(values[i])])
                    if len(tr) < 4 or not len(te):
                        continue
                    scale = float(np.std(values[tr], ddof=1))
                    models = {}
                    fallbacks = {}
                    for name, keys in [('global_mean', []), ('oracle_C_mean', ['protocol']),
                                       ('oracle_U_mean', ['activity_id']),
                                       ('oracle_UC_mean', ['activity_id', 'protocol'])]:
                        estimates = [conditional_mean(rows, tr, values, i, keys) for i in te]
                        models[name] = np.array([a for a, _ in estimates])
                        fallbacks[name] = [b for _, b in estimates]
                    models['global_median'] = np.full(len(te), np.median(values[tr]))
                    for name, cols in [('ridge_post', scalar),
                                       ('ridge_post_drop_family', dropped_columns(target, scalar, families))]:
                        x = matrix(rows, 'post', cols)
                        model = pipeline(Ridge(alpha=config['ridge_alpha']))
                        model.fit(x[tr], values[tr])
                        models[name] = model.predict(x[te])
                    if target_view == 'delta' and target not in DISTANCES:
                        pre = np.array([r['pre__' + target] for r in rows], dtype=float)
                        post = np.array([r['post__' + target] for r in rows], dtype=float)
                        logpre = np.log(np.maximum(pre, 1e-300))
                        logpost = np.log(np.maximum(post, 1e-300))
                        for name, keys in [('algebra_global', []), ('algebra_C', ['protocol']),
                                           ('algebra_UC', ['activity_id', 'protocol'])]:
                            estimates = [conditional_mean(rows, tr, logpre, i, keys) for i in te]
                            models[name] = np.array([logpost[i] - a for i, (a, _) in zip(te, estimates)])
                            fallbacks[name] = [b for _, b in estimates]
                    for name, preds in models.items():
                        if not np.isfinite(preds).all():
                            raise ValueError('nonfinite regression predictions')
                        for k, (i, pred) in enumerate(zip(te, preds)):
                            result.append({'setting': setting, 'scheme': scheme, 'fold': held,
                                'target_view': target_view, 'metric': target, 'model': name,
                                'session_id': rows[i]['session_id'], 'target_domain': rows[i]['target_domain'],
                                'protocol': rows[i]['protocol'], 'repetition': rows[i]['repetition'],
                                'truth': float(values[i]), 'prediction': float(pred),
                                'training_target_sd': scale, 'train_n': len(tr),
                                'target_missing_train': len(tr0)-len(tr), 'target_missing_test': len(te0)-len(te),
                                'oracle_group_fallback': fallbacks.get(name, [False]*len(te))[k],
                                'observation_level': OBSERVATION})
    write_table(out / 'recoverability-oof.parquet', result)
    return result


def summarize(class_rows, reg_rows, config, out):
    grouped = defaultdict(list)
    for r in class_rows:
        grouped[tuple(r[k] for k in ['setting', 'scheme', 'view', 'model'])].append(r)
    summaries, info, fold_summaries = [], [], []
    rng = np.random.default_rng(config['seed'])
    for key, rows in grouped.items():
        if len({r['session_id'] for r in rows}) != len(rows):
            raise ValueError('duplicate classification OOF prediction')
        base = dict(zip(['setting', 'scheme', 'view', 'model'], key))
        y = np.array([r['truth'] for r in rows])
        p = np.array([r['prob_vless'] for r in rows])
        pred = (p >= .5).astype(int)
        loss = bit_loss(y, p)
        err = float(np.mean(y != pred))
        h = entropy_binary(float(y.mean()))
        urls = sorted({r['target_domain'] for r in rows})
        url_losses = [float(np.mean([loss[i] for i, r in enumerate(rows) if r['target_domain'] == u])) for u in urls]
        boots = np.mean(rng.choice(url_losses, size=(config['bootstrap_repetitions'], len(urls))), axis=1)
        summary = {**base, 'n': len(rows), 'urls': len(urls), 'error': err,
                   'macro_f1': float(f1_score(y, pred, average='macro', zero_division=0)),
                   'balanced_accuracy': float(balanced_accuracy_score(y, pred)),
                   'log_loss_bits': float(loss.mean()), 'brier': float(np.mean((p-y)**2)),
                   'log_loss_url_bootstrap_low': float(np.quantile(boots, .025)),
                   'log_loss_url_bootstrap_high': float(np.quantile(boots, .975)),
                   'ss_pred_ss': int(np.sum((y==0)&(pred==0))), 'ss_pred_vless': int(np.sum((y==0)&(pred==1))),
                   'vless_pred_ss': int(np.sum((y==1)&(pred==0))), 'vless_pred_vless': int(np.sum((y==1)&(pred==1))),
                   'uncertainty': 'descriptive_URL_bootstrap_of_fixed_OOF_not_training_or_round_uncertainty',
                   'observation_level': OBSERVATION}
        summaries.append(summary)
        info.append({**base, 'entropy_C_bits': h, 'cross_entropy_bits': float(loss.mean()),
                     'entropy_minus_ce_plugin_bits': h-float(loss.mean()),
                     'fano_plugin_bits': h-entropy_binary(err),
                     'object': 'I(delta;C|U)' if key[2]=='delta_condition_U' else f'I({key[2]};C)',
                     'interpretation': 'empirical_plugin_not_certified_population_MI_bound'})
        for round_id in sorted({r['repetition'] for r in rows}):
            mask = np.array([r['repetition']==round_id for r in rows])
            fold_summaries.append({**base, 'repetition': round_id,
                'round_log_loss_bits': float(loss[mask].mean()),
                'leave_round_out_of_summary_loss': float(loss[~mask].mean()) if (~mask).any() else None,
                'round_accuracy': float(np.mean(pred[mask]==y[mask]))})
    reg_group = defaultdict(list)
    for r in reg_rows:
        reg_group[tuple(r[k] for k in ['setting', 'scheme', 'target_view', 'metric', 'model'])].append(r)
    reg_summary = []
    for key, rows in reg_group.items():
        if len({r['session_id'] for r in rows}) != len(rows):
            raise ValueError('duplicate regression OOF prediction')
        y = np.array([r['truth'] for r in rows])
        pred = np.array([r['prediction'] for r in rows])
        sd = np.array([r['training_target_sd'] for r in rows])
        norm = np.abs(y-pred)[sd > 1e-12] / sd[sd > 1e-12]
        score = float(r2_score(y, pred)) if np.var(y) > 1e-15 else None
        reg_summary.append({**dict(zip(['setting', 'scheme', 'target_view', 'metric', 'model'], key)),
            'n': len(rows), 'mae': float(mean_absolute_error(y, pred)), 'r2': score,
            'normalized_mae_training_sd': float(norm.mean()) if len(norm) else None,
            'normalized_n': len(norm), 'oracle_fallback_n': sum(r['oracle_group_fallback'] for r in rows)})
    write_table(out / 'classification-summary.parquet', summaries)
    write_table(out / 'information-proxy.parquet', info)
    write_table(out / 'round-sensitivity.parquet', fold_summaries)
    write_table(out / 'recoverability-summary.parquet', reg_summary)
    return summaries, reg_summary, info
