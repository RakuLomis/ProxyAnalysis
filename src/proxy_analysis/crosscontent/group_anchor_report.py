"""Post-only NumPy prediction replay and descriptive content-clustered contrasts."""
import argparse
from collections import defaultdict
import numpy as np
from sklearn.metrics import confusion_matrix, precision_recall_fscore_support

from .group_anchor_contract import CONFIG, verify
from .natural_pair_ssl_report import mlp, softmax, metrics, compare
from .mechanism_contract import read
from .paired_structure_contract import seal, validate_complete
from ..paired_information.prepare import table
from ..reproducibility.preflight import write_json, write_table


def report(config=CONFIG):
    cfg, _, root = verify(config)
    validate_complete(root/'training-audit'); validate_complete(root/'pretraining-audit')
    predictions = []; diagnostics = []; worst = 0.; stages = 0
    for job in sorted((root/'jobs').iterdir()):
        validate_complete(job); mem = read(job/'membership.json')
        data = read(root/'prepared'/f'{mem["context"]}.json'); x = np.asarray(data['test_post'])
        fit = read(job/'finetune-fit.json')['final']; h = mlp(x, fit, '0.')
        replay = {'finetune': softmax(h@np.asarray(fit['1.weight']).T+fit['1.bias'])}
        if mem['arm'] != 'R0':
            fit = read(job/'probe-fit.json'); h = (mlp(x, fit['encoder'])-fit['mean'])/fit['scale']
            replay['probe'] = softmax(h@np.asarray(fit['coef']).T+fit['intercept'])
            info = read(job/'ssl-fit.json')
            diagnostics.append({'context': mem['context'], 'arm': mem['arm'], 'seed': mem['seed'],
                **info['encoder_diagnostics'], 'weights': info.get('weights'),
                'train_group_huber': info.get('train_group_huber'), 'train_null_huber': info.get('train_null_huber')})
        rows = table(job/'predictions.parquet')
        for stage, p in replay.items():
            rr = [r for r in rows if r['stage'] == stage]
            if [r['session_id'] for r in rr] != mem['test_ids']: raise ValueError('Prediction membership differs')
            worst = max(worst, float(abs(p-np.asarray([r['probabilities'] for r in rr])).max()))
        stages += mem['stages']; predictions.extend(rows)
    if stages != 285 or len(predictions) != 9360 or worst > 1e-10:
        raise ValueError('Prediction replay/budget failed')
    groups = defaultdict(list); fold_groups = defaultdict(list)
    for r in predictions:
        for protocol in (r['protocol'], 'pooled'):
            groups[r['stage'], protocol, r['arm'], r['seed']].append(r)
            fold_groups[r['stage'], protocol, r['arm'], r['seed'], r['fold']].append(r)
    result = []; summaries = defaultdict(list); classes = []; confusions = []
    for (stage, protocol, arm, seed), rr in sorted(groups.items()):
        if len({r['session_id'] for r in rr}) != len(rr): raise ValueError('Repeated OOF visits')
        meta = {'stage': stage, 'protocol': protocol, 'arm': arm, 'seed': seed}
        value = {**meta, **metrics(rr)}; result.append(value); summaries[stage, protocol, arm].append(value)
        labels = rr[0]['labels']; y = [labels.index(r['label_id']) for r in rr]
        pred = [int(np.argmax(r['probabilities'])) for r in rr]
        precision, recall, f1, support = precision_recall_fscore_support(y, pred, labels=list(range(6)), zero_division=0)
        for j, label in enumerate(labels):
            classes.append({**meta, 'label': label, 'precision': float(precision[j]), 'recall': float(recall[j]),
                            'f1': float(f1[j]), 'support': int(support[j])})
        confusions.append({**meta, 'labels': labels, 'matrix': confusion_matrix(y, pred, labels=list(range(6))).tolist()})
    summary = []
    for (stage, protocol, arm), rr in sorted(summaries.items()):
        value = {'stage': stage, 'protocol': protocol, 'arm': arm}
        for metric in ('ce_bits', 'macro_f1', 'balanced_accuracy', 'brier'):
            values = [r[metric] for r in rr]; value[metric] = float(np.mean(values)); value[metric+'_range'] = [min(values), max(values)]
        summary.append(value)
    gains = []; content_effects = []
    for stage in ('probe', 'finetune'):
        for protocol in ('SHADOWSOCKS', 'VLESS', 'pooled'):
            def pick(arm): return [r for seed in cfg['seeds'] for r in groups[stage, protocol, arm, seed]]
            a = pick('R4')
            for control in (['R0'] if stage == 'finetune' else []) + ['R1','R2','R3','R5','R6']:
                b = pick(control)
                gains.append({'stage': stage, 'protocol': protocol, 'control': control,
                              **compare(a, b, cfg['bootstrap_repetitions'], cfg['seeds'])})
                lookup = {(r['session_id'], r['seed']): r for r in b}
                effects = defaultdict(list)
                for r in a:
                    other = lookup[r['session_id'], r['seed']]; j = r['labels'].index(r['label_id'])
                    ce = np.log2(max(r['probabilities'][j], 1e-15))-np.log2(max(other['probabilities'][j], 1e-15))
                    accuracy = int(np.argmax(r['probabilities']) == j)-int(np.argmax(other['probabilities']) == j)
                    effects[r['content_id']].append((float(ce), accuracy))
                for content, values in effects.items():
                    content_effects.append({'stage': stage, 'protocol': protocol, 'control': control,
                        'content_id': content, 'ce_gain_bits': float(np.mean(values, axis=0)[0]),
                        'accuracy_gain': float(np.mean(values, axis=0)[1])})
    fold_metrics = [{'stage': key[0], 'protocol': key[1], 'arm': key[2], 'seed': key[3], 'fold': key[4],
                     **metrics(rr)} for key, rr in sorted(fold_groups.items())]
    out = root/'report'
    write_table(out/'predictions.parquet', predictions); write_json(out/'metrics-summary.json', summary)
    write_json(out/'metrics-per-seed.json', result); write_json(out/'fold-metrics.json', fold_metrics)
    write_json(out/'per-class.json', classes); write_json(out/'confusion-matrices.json', confusions)
    write_json(out/'paired-gains.json', gains); write_json(out/'content-effects.json', content_effects)
    write_json(out/'representation-diagnostics.json', diagnostics)
    write_json(out/'validation.json', {'passed': True, 'training_stages': stages, 'predictions': len(predictions),
        'max_independent_probability_error': worst, 'external_validation': False,
        'scope': cfg['observation_scope'], 'intervals': 'unadjusted, conditional on fitted models, stratified by business content'})
    seal(out, passed=True)
    print(f'Report passed: {len(predictions)} predictions; max replay error {worst}', flush=True)
    for r in summary:
        if r['protocol'] == 'pooled': print(r, flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--config', default=str(CONFIG)); args = parser.parse_args()
    report(args.config)
