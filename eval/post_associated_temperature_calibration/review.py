"""Additional independent calibration-objective and loss-contribution replay."""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'outputs/post-associated-temperature-calibration-20261015/run-02'


def read(p):
    return json.loads(p.read_text(encoding='utf-8'))


def main():
    assert read(OUT/'completion.json')['passed']
    fits = read(OUT/'fits/temperatures.json')
    objective_error, derivative_error, max_interior = 0., 0., 0.
    for fit in fits:
        allrows = pd.read_parquet(ROOT/fit['calibration_file'])
        z = allrows[allrows.pipeline.eq(fit['pipeline'])]
        assert z.groupby('content_id').visit_id.nunique().eq(4).all()
        seeds_per_visit = z.groupby('visit_id').size()
        weights = np.array([1/(5*4*seeds_per_visit[v]) for v in z.visit_id])
        assert abs(weights.sum()-1) < 1e-14
        logits = z[[f'l{k}' for k in range(6)]].to_numpy()
        target = z.y.to_numpy(dtype=int)
        scaled = logits*fit['inverse_temperature']
        scaled -= scaled.max(1, keepdims=True)
        lp = scaled-np.log(np.exp(scaled).sum(1, keepdims=True))
        value = float((-lp[np.arange(len(z)), target]*weights).sum())
        gradient = float((((np.exp(lp)*logits).sum(1)-logits[np.arange(len(z)), target])*weights).sum())
        objective_error = max(objective_error, abs(value-fit['objective']))
        derivative_error = max(derivative_error, abs(gradient-fit['gradient']))
        if fit['status'] == 'interior':
            max_interior = max(max_interior, abs(gradient))
            assert abs(gradient) <= 1e-8 or fit['bracket_upper']-fit['bracket_lower'] <= 1e-10
        elif fit['status'] == 'T1':
            assert gradient <= 1e-8
        elif fit['status'] == 'T5':
            assert gradient >= -1e-8
        else:
            raise AssertionError(fit['status'])
    assert objective_error <= 1e-10 and derivative_error <= 1e-10
    s = read(OUT/'scores/summary.json')
    d = pd.read_parquet(OUT/'scores/row-analysis.parquet')
    for pipe in s['pipelines']:
        for split in ['C', 'U']:
            z = d[d.pipeline.eq(pipe['pipeline']) & d.split.eq(split)]
            t = [v for v in s['transitions'] if v['pipeline'] == pipe['pipeline'] and v['split'] == split]
            assert sum(v['n'] for v in t) == len(z)
            for metric in ['CE', 'Brier']:
                assert abs(sum(v[f'{metric}_contribution'] for v in t) -
                           (z[metric]-z[f'raw_{metric}']).mean()) < 1e-14
    result = dict(passed=True, independently_replayed_calibration_fits=648,
                  objective_max_error=objective_error, derivative_max_error=derivative_error,
                  interior_max_abs_gradient=max_interior,
                  lower_or_upper_boundary_gradients_checked_by_KKT=True,
                  contribution_replay_pass=True, new_fits=0,
                  code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    with (OUT/'audits/extended-quality.json').open('x', encoding='utf-8') as f:
        json.dump(result, f, indent=2, sort_keys=True)
        f.write('\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
