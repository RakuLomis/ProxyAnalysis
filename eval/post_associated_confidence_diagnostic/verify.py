"""Independent arithmetic replay; no models or temperatures are fitted."""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'outputs/post-associated-confidence-diagnostic-20261015/run-01'
RUN = ROOT/'outputs/post-associated-frozen-readout-20261014/run-01'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def main():
    a = read(OUT/'analysis.json')
    d = pd.read_parquet(OUT/'frozen-row-diagnostics.parquet')
    s = read(RUN/'scores/summary.json')
    assert len(d) == 6912
    max_error = 0.
    for c in s['cells']:
        x = d[d.arm.eq(c['arm']) & d.eta.eq(c['eta'])]
        for name, value in [('CE_all', x.CE.mean()), ('Brier', x.Brier.mean()),
                            ('CE_U', x[x.split.eq('U')].CE.mean()),
                            ('CE_C', x[x.split.eq('C')].CE.mean()),
                            ('Brier_U', x[x.split.eq('U')].Brier.mean()),
                            ('Brier_C', x[x.split.eq('C')].Brier.mean())]:
            max_error = max(max_error, abs(float(value)-c[name]))
        for split in ['U', 'C']:
            part = x[x.split.eq(split)]
            states = [v for v in a['transitions'] if v['arm'] == c['arm']
                      and v['eta'] == c['eta'] and v['split'] == split]
            assert sum(v['n'] for v in states) == len(part)
            assert abs(sum(v['CE_contribution'] for v in states)-part.delta_CE.mean()) < 1e-14
            assert abs(sum(v['Brier_contribution'] for v in states)-part.delta_Brier.mean()) < 1e-14
        audit = read(RUN/'audits/independent-analysis.json')
        prior = next(v for v in audit['cells'] if v['arm'] == c['arm'] and v['eta'] == c['eta'])
        assert int(x.state.eq('wrong->correct').sum()) == prior['repaired_U'] + prior['repaired_C']
        assert int(x.state.eq('correct->wrong').sum()) == c['added_errors_all']
    assert max_error < 1e-14
    for path, expected in a['input_bindings'].items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest() == expected, path
    c = read(RUN/'manifests/experiment-contract.json')
    query = set().union(*(set(r['validation_contents']) for r in c['roles']))
    assert len(query) == 6
    assert all(not query & set(r['train_contents']) for r in c['roles'])
    assert all(set(r['validation_contents']) == query for r in c['roles'])
    assert np.isfinite(d.select_dtypes('number')).all().all()
    result = dict(passed=True, metric_replay_max_error=max_error,
                  input_hashes_verified=len(a['input_bindings']),
                  all_six_query_contents_excluded_from_all_role_training=True,
                  new_fits=0, new_temperature_predictions=0, H_reads=0, actual_U_reads=0)
    with (OUT/'verification.json').open('x', encoding='utf-8') as f:
        json.dump(result, f, indent=2, sort_keys=True)
        f.write('\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
