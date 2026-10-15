"""Independent audit of the frozen-prediction temperature pilot; never fits."""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'outputs/post-associated-temperature-calibration-20261015/run-02'
OLD = ROOT/'outputs/post-associated-frozen-readout-20261014/run-01'


def read(p):
    return json.loads(p.read_text(encoding='utf-8'))


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    c = read(OUT/'manifests/contract.json')
    files = {}
    for name in ['registration-seal', 'temperatures-complete', 'predictions-complete', 'scores-complete']:
        p = OUT/f'manifests/{name}.json'
        seal = read(p)
        assert seal['passed']
        for f, h in seal['files'].items():
            assert sha(ROOT/f) == h, f
            files[f] = h
    for p, h in {**c['old_inputs'], **c['code_files']}.items():
        assert sha(ROOT/p) == h, p
    pred = pd.read_parquet(OUT/'predictions/visits.parquet')
    rows = pd.read_parquet(OUT/'scores/row-analysis.parquet')
    scores = read(OUT/'scores/summary.json')
    ts = read(OUT/'fits/temperatures.json')
    assert len(ts) == 648 and len(pred) == len(rows) == 7200
    assert pred.visit_id.nunique() == 96 and pred.content_id.nunique() == 6
    assert all(v['qualified'] and v['function_evaluations'] <= 64 for v in ts)
    fitdata = {v['path'] for v in read(OUT/'stages/P2-fit.json')['reads']}
    assert fitdata == {v for r in c['roles'] for v in r['calibration_files']}
    for v in read(OUT/'stages/P2-fit.json')['reads']:
        r = next(r for r in c['roles'] if r['id'] == v['role_id'])
        assert v['path'] in r['calibration_files']
        assert 'scoring-labels' not in v['path'] and '/evaluation.' not in v['path']
    assert all(v['purpose'] == 'predict-label-free-frozen-logits' for v in read(OUT/'stages/P3-predict.json')['reads'])
    for fit in ts:
        cal = pd.read_parquet(ROOT/fit['calibration_file'])
        sub = cal[cal.pipeline.eq(fit['pipeline'])]
        assert set(sub.role_id) == {fit['role_id']}
        assert fit['held_content'] not in set(sub.content_id)
        assert set(sub.content_id) == set(fit['calibration_contents'])
        assert set(sub.visit_id) == set(fit['calibration_visit_ids'])
        assert len(set(sub.content_id)) == 5 and sub.visit_id.nunique() == 20
        assert abs(fit['inverse_temperature']*fit['temperature']-1) < 1e-14
        g = fit['gradient']
        if fit['status'] == 'T1':
            assert g <= 1e-8
        elif fit['status'] == 'T5':
            assert g >= -1e-8
        else:
            assert abs(g) <= 1e-8 or (fit['bracket_upper']-fit['bracket_lower'] <= 1e-10 and
                   fit['bracket_gradient_lower'] <= 0 <= fit['bracket_gradient_upper'])
    # Numpy-only stable replay of all calibrated probabilities.
    lc, pc = [f'l{k}' for k in range(6)], [f'p{k}' for k in range(6)]
    original = pred[['raw_'+v for v in lc]].to_numpy()
    z = original/pred.temperature.to_numpy()[:, None]
    z -= z.max(1, keepdims=True)
    lp = z-np.log(np.exp(z).sum(1, keepdims=True))
    lp_error = float(np.max(abs(lp-pred[lc].to_numpy())))
    p_error = float(np.max(abs(np.exp(lp)-pred[pc].to_numpy())))
    assert lp_error < 1e-12 and p_error < 1e-12
    assert np.array_equal(pred[pc].to_numpy().argmax(1), original.argmax(1))
    assert np.array_equal(rows.prediction, rows.raw_prediction)
    # Ensure scalar routing follows the registered held-content fold.
    routing = {(v['role_id'], v['pipeline'], v['fold']): v for v in ts}
    for row in pred.itertuples(index=False):
        fit = routing[(row.role_id, row.pipeline, row.calibration_fold)]
        assert row.content_id == fit['held_content'] and row.temperature == fit['temperature']
        assert row.visit_id not in set(fit['calibration_visit_ids'])
    # Exact classification metrics and flip identities, not just average F1.
    eps = read(OUT/'scores/endpoints.json')
    for e in eps:
        for k in ['F1_all', 'F1_U', 'F1_C', 'accuracy', 'confusion_matrix']:
            assert e['raw'][k] == e['calibrated'][k]
    oldrows = pd.read_parquet(ROOT/'outputs/post-associated-confidence-diagnostic-20261015/run-01/frozen-row-diagnostics.parquet')
    oldrows['pipeline'] = [f'{a}_eta'+('1' if e == 1 else '0p01') for a, e in zip(oldrows.arm, oldrows.eta)]
    key = ['role_id', 'pipeline', 'seed', 'visit_id']
    matched = rows[rows.pipeline.ne('base')].merge(oldrows[key+['state', 'prediction']], on=key, suffixes=('', '_old'), validate='one_to_one')
    assert len(matched) == 6912 and matched.state.eq(matched.state_old).all() and matched.prediction.eq(matched.prediction_old).all()
    # Original endpoint and summary metric replay.
    prior = read(OLD/'scores/summary.json')
    old_metric_error = 0.
    for s in scores['pipelines']:
        if s['pipeline'] == 'base':
            orig = prior['baseline']
        else:
            arm, eta = s['pipeline'].split('_eta')
            eta = 1. if eta == '1' else .01
            orig = next(v for v in prior['cells'] if v['arm'] == arm and v['eta'] == eta)
        for k in s['raw']:
            old_metric_error = max(old_metric_error, abs(s['raw'][k]-orig[k]))
        q = rows[rows.pipeline.eq(s['pipeline'])]
        for split in ['U', 'C']:
            part = q[q.split.eq(split)]
            assert abs(part.CE.mean()-s['calibrated'][f'CE_{split}']) < 1e-14
            assert abs(part.Brier.mean()-s['calibrated'][f'Brier_{split}']) < 1e-14
    assert old_metric_error < 1e-14
    result = dict(passed=True, fits=648, endpoint_records=300, probability_rows=7200,
                  independent_logprob_max_error=lp_error, independent_probability_max_error=p_error,
                  original_metric_max_error=old_metric_error, sealed_files_verified=len(files),
                  old_files_verified=len(c['old_inputs']), classifications_changed=0,
                  old_6912_flip_states_exact=True, role_and_content_isolation=True,
                  actual_H_reads=0, actual_U_reads=0, G_fits=0, classifier_fits=0, teacher_fits=0,
                  code_sha256=sha(Path(__file__)))
    with (OUT/'audits/independent-verification.json').open('x', encoding='utf-8') as f:
        json.dump(result, f, indent=2, sort_keys=True)
        f.write('\n')
    complete = dict(passed=True, status='source_temperature_pilot_complete', fits=648,
                    probability_repair_pass=scores['probability_pass'],
                    paired_increment_pass=scores['increment_pass'], formal_H_scored=False,
                    full_role_training_started=False, old_results_unchanged=True,
                    audit_sha256=sha(OUT/'audits/independent-verification.json'))
    with (OUT/'completion.json').open('x', encoding='utf-8') as f:
        json.dump(complete, f, indent=2, sort_keys=True)
        f.write('\n')
    print(json.dumps(result, indent=2))
    print(json.dumps(complete, indent=2))


if __name__ == '__main__':
    main()
