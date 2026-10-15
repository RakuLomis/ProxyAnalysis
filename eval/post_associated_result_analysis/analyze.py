"""Read-only Stage A closeout; source-only labels, no H/U access or fitting."""
from pathlib import Path
import collections
import hashlib
import json
from datetime import datetime, timezone, timedelta

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / 'outputs/post-input-associated-representation-20261014/run-02'
OUT = ROOT / 'outputs/post-associated-result-analysis-20261014/run-01'
LABELS = ['bing.com::search_results_view', 'developer.mozilla.org::document_view',
          'github.com::repository_view', 'wikipedia.org::article_view',
          'youtube.com::search_results_view', 'youtube.com::video_playback']
AUDIT = []


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    AUDIT.append({'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path)})
    return json.loads(path.read_text(encoding='utf-8'))


def sealed(path):
    record = read(path)
    assert record['passed']
    for name, digest in record['files'].items():
        target = ROOT / name
        assert sha(target) == digest, name
        AUDIT.append({'path': name, 'sha256': digest})
    return record


def dist(values):
    a = np.asarray(values, dtype=float)
    return dict(n=len(a), minimum=float(a.min()), q25=float(np.quantile(a, .25)),
                median=float(np.median(a)), mean=float(a.mean()),
                q75=float(np.quantile(a, .75)), maximum=float(a.max()))


def summarize(rows):
    return dict(n=len(rows), qualified=sum(r['qualified'] for r in rows),
                negative_CE=sum(r['delta_CE_U'] < 0 for r in rows),
                zero_F1_U=sum(r['delta_F1_U'] == 0 for r in rows),
                positive_F1_U=sum(r['delta_F1_U'] > 0 for r in rows),
                negative_F1_U=sum(r['delta_F1_U'] < 0 for r in rows),
                failure_counts=dict(collections.Counter(k for r in rows for k, v in r['gates'].items() if not v)),
                delta_CE_U=dist([r['delta_CE_U'] for r in rows]),
                CE_gate_gap=dist([r['delta_CE_U'] + .002 for r in rows]),
                delta_F1_U=dist([r['delta_F1_U'] for r in rows]),
                delta_F1_C=dist([r['delta_F1_C'] for r in rows]),
                worst_delta_F1_C=dist([r['worst_delta_F1_C'] for r in rows]))


def metric(y, p, missing):
    pred = p.argmax(1)
    cm = np.bincount(y * 6 + pred, minlength=36).reshape(6, 6)
    den = cm.sum(0) + cm.sum(1)
    f1 = np.divide(2 * np.diag(cm), den, out=np.zeros(6), where=den > 0)
    ce = -np.log(p[np.arange(len(y)), y][np.isin(y, missing)]).mean()
    return float(ce), float(f1[missing].mean()), float(np.delete(f1, missing).mean())


def main():
    assert not OUT.exists(), 'Use a fresh analysis output, never overwrite'
    contract = read(RUN / 'manifests/experiment-contract.json')
    assert sha(RUN / 'manifests/experiment-contract.json') == read(RUN / 'manifests/seal.json')['sha256']
    sealed(RUN / 'selections/complete.json')
    sealed(RUN / 'inner-predictions/complete.json')
    candidates = read(RUN / 'selections/candidate-metrics.json')
    decisions = read(RUN / 'selections/decisions.json')
    assert len(candidates) == 420 and len(decisions) == 180
    assert all(not r['enabled'] and r['fallback'] for r in decisions)
    roles = {r['id']: r for r in contract['roles']}
    truth = {}
    for r in contract['inner_roles']:
        assert r['inner'] is not None
        key = f"outputs/calibrated-deployment-business-transfer-20261006/run-01/packages/{r['id']}/labels.parquet"
        info = contract['packages'][key]
        assert info['kind'] == 'main-inner-labels' and info['role_id'] == r['id']
        path = ROOT / key
        assert sha(path) == info['sha256']
        AUDIT.append({'path': key, 'sha256': info['sha256'], 'purpose': 'source-only-score'})
        lab = pd.read_parquet(path, columns=['visit_id', 'label_id'])
        assert len(lab) == 24 and lab.visit_id.is_unique
        for vid, label in lab.itertuples(index=False, name=None):
            truth[(r['id'], vid)] = LABELS.index(label)
    d = pd.read_parquet(RUN / 'inner-predictions/post-only.parquet')
    assert len(d) == 259200
    d['truth'] = [truth[(r, v)] for r, v in zip(d.role_id, d.visit_id)]
    pcols = [f'p{i}' for i in range(6)]
    bcols = [f'bp{i}' for i in range(6)]
    # Independent closed-form source gate replay, including zero-lambda aliases.
    replay = {}
    flips = []
    for keys, sub in d.groupby(['outer', 'actual_target', 'group', 'arm', 'lambda'], sort=True):
        outer, target, group, arm, lv = keys
        rid = f'main/f{outer}/{target}/{group}/outer'
        missing = roles[rid]['missing']
        parts = []
        for (pseudo, seed), z in sub.groupby(['calibration', 'seed']):
            assert len(z) == 96
            y = z.truth.to_numpy(int)
            p = z[pcols].to_numpy()
            bp = z[bcols].to_numpy()
            a = metric(y, p, missing)
            b = metric(y, bp, missing)
            parts.append(dict(pseudo=pseudo, seed=seed, CE_U=a[0],
                              delta_CE_U=a[0]-b[0], delta_F1_U=a[1]-b[1], delta_F1_C=a[2]-b[2]))
        t = pd.DataFrame(parts)
        dc, du, cc = [float(t[k].mean()) for k in ['delta_CE_U', 'delta_F1_U', 'delta_F1_C']]
        worst = float(t.groupby('pseudo').delta_F1_C.mean().min())
        gates = dict(CE_U=dc <= -.002, F1_U=du >= 0, C_overall=cc >= -.01, C_deployment=worst >= -.02)
        replay[(rid, arm, lv)] = dict(CE_U=float(t.CE_U.mean()), delta_CE_U=dc,
            delta_F1_U=du, delta_F1_C=cc, worst_delta_F1_C=worst, gates=gates, qualified=all(gates.values()))
    max_error = 0.
    for row in candidates:
        key = (row['role_id'], 'A1' if row['lambda_value'] == 0 else row['arm'], row['lambda_value'])
        reference = replay[key]
        for k in ['CE_U', 'delta_CE_U', 'delta_F1_U', 'delta_F1_C', 'worst_delta_F1_C']:
            max_error = max(max_error, abs(row[k]-reference[k]))
        assert row['gates'] == reference['gates'] and row['qualified'] == reference['qualified']
    assert max_error < 1e-12
    for (arm, lv, seed), z in d.groupby(['arm', 'lambda', 'seed']):
        y = z.truth.to_numpy(int); p = z[pcols].to_numpy(); bp = z[bcols].to_numpy()
        pred = p.argmax(1); baseline = bp.argmax(1)
        tv = np.abs(p-bp).sum(1)/2
        flips.append(dict(arm=arm, lambda_value=float(lv), seed=int(seed), predictions=len(z),
             class_changes=int((pred != baseline).sum()), repaired=int(((pred == y)&(baseline != y)).sum()),
             added_errors=int(((pred != y)&(baseline == y)).sum()),
             both_wrong_class_changes=int(((pred != y)&(baseline != y)&(pred != baseline)).sum()),
             probability_TV=dist(tv), max_probability_difference=float(np.abs(p-bp).max())))
    summary = {}
    for arm, lv in [('A1', 0.), ('A2', .1), ('A2', 1.), ('A3', .1), ('A3', 1.)]:
        key = f'{arm}-lambda{lv:g}'
        selected = [r for r in candidates if r['arm'] == arm and r['lambda_value'] == lv]
        summary[key] = summarize(selected)
        summary[key]['by_actual_target'] = {target: summarize([r for r in selected if roles[r['role_id']]['target'] == target])
            for target in sorted({r['target'] for r in roles.values()})}
    training = collections.defaultdict(list)
    for path in (RUN/'inner-models').rglob('training.json'):
        record = json.loads(path.read_text(encoding='utf-8'))
        assert record['steps'] == 1000 and len(record['trace']) == 10
        first, last = record['trace'][0], record['trace'][-1]
        training[f"{record['arm']}-lambda{record['lambda_value']:g}"].append(dict(
            CE=last['CE'], MSE=last['MSE'], regularizer=last['regularizer'], objective=last['objective'],
            change_CE_100_to_1000=last['CE']-first['CE'],
            change_MSE_100_to_1000=last['MSE']-first['MSE'],
            change_objective_100_to_1000=last['objective']-first['objective']))
    assert sum(map(len, training.values())) == 10800
    train_summary = {key: {name: dist([r[name] for r in rows]) for name in rows[0]}
                     for key, rows in training.items()}
    teacher = [json.loads(p.read_text(encoding='utf-8')) for p in (RUN/'teachers').rglob('diagnostics.json')]
    assert len(teacher) == 720
    endpoint = read(RUN/'manifests/endpoints.json')
    assert len(endpoint) == 720 and all(e['fallback'] and e['residual_path'] is None for e in endpoint)
    for rid in roles:
        branch = [e for e in endpoint if e['role_id'] == rid]
        assert len(branch) == 12 and len({e['base_path'] for e in branch}) == 1
        model = ROOT / branch[0]['base_path']
        meta = read(model.with_suffix('.json'))
        assert sha(model) == meta['sha256']
        AUDIT.append({'path': model.relative_to(ROOT).as_posix(), 'sha256': meta['sha256'], 'purpose': 'fallback-alias'})
    stages = {}
    for path in (RUN/'stages').glob('*.json'):
        record = read(path)
        reads = record.get('reads', [])
        stages[path.stem] = dict(passed=record.get('passed'), seconds=record.get('seconds'),
            reads=len(reads), purpose_counts=dict(collections.Counter(r['purpose'] for r in reads)))
        assert not any(r['purpose'].startswith('H-') for r in reads)
    ledger = read(RUN/'ledger.json')
    completion = read(RUN/'completion.json')
    supervisor = read(RUN/'supervisor.json'); progress = read(RUN/'progress.json')
    tz = timezone(timedelta(hours=8))
    result = dict(status=completion, analysis_scope='source_only_no_new_training_no_H_U_reads',
        counts=dict(outer_roles=60, inner_roles=720, source_predictions=len(d), independent_configs=5,
                    source_residual_fits=10800, teachers=720, candidate_records=420,
                    unique_candidate_records=300, enabled=0, fallback=180,
                    unsealed_endpoint_records=720, actual_H_scored=False),
        timings=dict(start_beijing=datetime.fromtimestamp(supervisor['start_unix'], tz).isoformat(),
                     stop_beijing=datetime.fromtimestamp(progress['time_unix'], tz).isoformat(),
                     elapsed_supervisor_seconds=progress['time_unix']-supervisor['start_unix']),
        ledger=ledger, source_candidates=summary, source_prediction_differences=flips,
        source_gate_replay_max_error=max_error, source_training=train_summary,
        teacher_diagnostics=dict(training_accuracy=dist([r['training_accuracy'] for r in teacher]),
            effective_rank=dist([r['effective_rank'] for r in teacher]),
            raw_coordinate_sd=dist([s for r in teacher for s in r['sd']])),
        endpoint_aliases_verified=True, models_complete_present=(RUN/'manifests/models-complete.json').exists(),
        H_predictions_complete_present=(RUN/'predictions/complete.json').exists(),
        stages=stages, reads=AUDIT,
        note='Overlapping source pseudo-task predictions are not independent observations; no significance tests.')
    OUT.mkdir(parents=True)
    (OUT/'analysis.json').write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    print(json.dumps({k: result[k] for k in ['status','counts','timings','source_gate_replay_max_error', 'teacher_diagnostics']}, indent=2))
    for key, value in summary.items():
        print(key, json.dumps({k: v for k, v in value.items() if k != 'by_actual_target'}))
    print('Output:', OUT/'analysis.json')


if __name__ == '__main__':
    main()
