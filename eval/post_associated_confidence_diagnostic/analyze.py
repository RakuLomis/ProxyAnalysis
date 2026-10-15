"""Read-only probability and class-flip diagnosis of sealed source predictions.

No classifier, representation or calibration parameter is fitted. Temperature
derivatives are evaluated analytically at T=1 only, never used to rescore rows.
"""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd
import torch

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / 'outputs/post-associated-frozen-readout-20261014/run-01'
OUT = ROOT / 'outputs/post-associated-confidence-diagnostic-20261015/run-01'
LABELS = ['bing.com::search_results_view', 'developer.mozilla.org::document_view',
          'github.com::repository_view', 'wikipedia.org::article_view',
          'youtube.com::search_results_view', 'youtube.com::video_playback']
PC = [f'p{k}' for k in range(6)]
LC = [f'l{k}' for k in range(6)]


def read(p):
    return json.loads(p.read_text(encoding='utf-8'))


def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def stats(x):
    x = np.asarray(x, float)
    return {k: float(v) for k, v in zip(
        ['min', 'q10', 'median', 'q90', 'max', 'mean'],
        [x.min(), *np.quantile(x, [.1, .5, .9]), x.max(), x.mean()])}


def temperature_derivatives(p, lp, y):
    # Independent differentiable evaluation at the unchanged T=1 point.
    logits = torch.as_tensor(lp, dtype=torch.float64, device='cuda')
    target = torch.as_tensor(y, dtype=torch.int64, device='cuda')
    t = torch.tensor(1., dtype=torch.float64, device='cuda', requires_grad=True)
    lt = torch.log_softmax(logits / t, 1)
    pt = lt.exp()
    one = torch.nn.functional.one_hot(target, 6).double()
    ce = -lt[torch.arange(len(y), device='cuda'), target].mean()
    br = ((pt - one) ** 2).sum(1).mean()
    ag_ce = torch.autograd.grad(ce, t, retain_graph=True)[0].item()
    ag_br = torch.autograd.grad(br, t)[0].item()
    expected_logit = (p * lp).sum(1)
    dc = lp[np.arange(len(y)), y] - expected_logit
    dp = -p * (lp - expected_logit[:, None])
    db = 2 * ((p - np.eye(6)[y]) * dp).sum(1)
    assert abs(dc.mean() - ag_ce) < 1e-12
    assert abs(db.mean() - ag_br) < 1e-12
    return dc, db


def main():
    assert not OUT.exists(), 'New outputs only; choose a new run for replay.'
    assert torch.cuda.is_available(), 'CUDA required for probability derivative checks.'
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    c = read(RUN / 'manifests/experiment-contract.json')
    assert read(RUN / 'completion.json')['passed']
    assert sha(RUN / 'manifests/experiment-contract.json') == read(RUN / 'manifests/contract-seal.json')['sha256']
    inputs = {}

    def check(p, expected=None):
        got = sha(p)
        if expected is not None:
            assert got == expected, str(p)
        inputs[str(p.relative_to(ROOT)).replace('\\', '/')] = got

    for name in ['completion.json', 'manifests/experiment-contract.json',
                 'manifests/contract-seal.json', 'scores/summary.json',
                 'audits/independent-analysis.json', 'audits/final-verification.json']:
        check(RUN / name)
    for name in ['manifests/code.json', 'manifests/models-complete.json',
                 'predictions/complete.json', 'scores/complete.json']:
        manifest = read(RUN / name)
        assert manifest['passed']
        check(RUN / name)
        for path, expected in manifest['files'].items():
            check(ROOT / path, expected)
    roles = {r['id']: r for r in c['roles']}
    labelparts = []
    for rid, r in roles.items():
        path = ROOT / r['labels']
        info = c['sources'][r['labels']]
        assert info['kind'] == 'query-label'
        check(path, info['sha256'])
        z = pd.read_parquet(path)
        assert len(z) == 24 and z.visit_id.is_unique
        assert set(z.content_id) == set(r['validation_contents'])
        assert not set(z.content_id) & set(r['train_contents'])
        assert (z.protocol == r['calibration']).all()
        assert z.groupby('content_id').size().eq(4).all()
        z = z.assign(role_id=rid, y=z.label_id.map({v: i for i, v in enumerate(LABELS)}))
        z['split'] = np.where(z.y.isin(r['missing']), 'U', 'C')
        labelparts.append(z[['role_id', 'visit_id', 'content_id', 'y', 'protocol', 'split']])
    labels = pd.concat(labelparts, ignore_index=True)
    d = pd.read_parquet(RUN / 'predictions/visits.parquet')
    b = pd.read_parquet(RUN / 'predictions/base.parquet')
    d = d.merge(labels, on=['role_id', 'visit_id'], validate='many_to_one')
    d = d.merge(b[['role_id', 'visit_id', *PC, *LC]], on=['role_id', 'visit_id'],
                suffixes=('', '_base'), validate='many_to_one')
    assert len(d) == 6912 and d.visit_id.nunique() == 96 and d.content_id.nunique() == 6
    records, cells, flips = [], [], []
    base_summary = read(RUN / 'scores/summary.json')['baseline']
    for (arm, eta), z in d.groupby(['arm', 'eta']):
        z = z.reset_index(drop=True)
        p, lp = z[PC].to_numpy(), z[LC].to_numpy()
        bp, blp = z[[k + '_base' for k in PC]].to_numpy(), z[[k + '_base' for k in LC]].to_numpy()
        assert np.max(abs(p - np.exp(lp))) < 1e-12
        y = z.y.to_numpy(dtype=int)
        one = np.eye(6)[y]
        pred, oldpred = p.argmax(1), bp.argmax(1)
        ce, bc = -lp[np.arange(len(y)), y], -blp[np.arange(len(y)), y]
        br, bb = ((p - one)**2).sum(1), ((bp - one)**2).sum(1)
        dc, db = temperature_derivatives(p, lp, y)
        # Orthogonal decomposition is descriptive, not a new prediction rule.
        s, t = blp - blp.mean(1, keepdims=True), lp - lp.mean(1, keepdims=True)
        delta = t - s
        a = (delta * s).sum(1) / (s*s).sum(1)
        radial = a[:, None] * s
        other = delta - radial
        assert np.max(abs((radial * other).sum(1))) < 1e-10
        sortedp = np.sort(p, axis=1)
        sortedbp = np.sort(bp, axis=1)
        for i, row in z.iterrows():
            oc, nc = oldpred[i] == y[i], pred[i] == y[i]
            state = ('correct' if oc else 'wrong') + '->' + ('correct' if nc else 'wrong')
            rec = dict(arm=arm, eta=float(eta), role_id=row.role_id, seed=int(row.seed),
                       visit_id=row.visit_id, content_id=row.content_id, y=int(y[i]),
                       protocol=row.protocol, split=row.split, state=state,
                       old_prediction=int(oldpred[i]), prediction=int(pred[i]),
                       base_CE=float(bc[i]), CE=float(ce[i]), delta_CE=float(ce[i]-bc[i]),
                       base_Brier=float(bb[i]), Brier=float(br[i]), delta_Brier=float(br[i]-bb[i]),
                       base_confidence=float(bp[i].max()), confidence=float(p[i].max()),
                       base_true_p=float(bp[i, y[i]]), true_p=float(p[i, y[i]]),
                       delta_p_squared=float((p[i]**2).sum()-(bp[i]**2).sum()),
                       minus_2_delta_true_p=float(-2*(p[i, y[i]]-bp[i, y[i]])),
                       base_margin=float(sortedbp[i, -1]-sortedbp[i, -2]),
                       margin=float(sortedp[i, -1]-sortedp[i, -2]),
                       dCE_dT_at_1=float(dc[i]), dBrier_dT_at_1=float(db[i]),
                       radial_scale=float(1+a[i]), radial_energy=float((radial[i]**2).sum()),
                       angular_energy=float((other[i]**2).sum()),
                       delta_energy=float((delta[i]**2).sum()))
            assert abs(rec['delta_Brier']-rec['delta_p_squared']-rec['minus_2_delta_true_p']) < 2e-15
            records.append(rec)
            if pred[i] != oldpred[i]:
                flips.append(rec)
        cells.append(dict(arm=arm, eta=float(eta), n=len(z),
                          radial_energy_fraction=float((radial**2).sum()/(delta**2).sum()),
                          radial_scale=stats(1+a), CE=float(ce.mean()), Brier=float(br.mean()),
                          dCE_dT_at_1=float(dc.mean()), dBrier_dT_at_1=float(db.mean())))
    rows = pd.DataFrame(records)
    transitions = []
    cols = ['base_CE', 'CE', 'delta_CE', 'base_Brier', 'Brier', 'delta_Brier',
            'base_confidence', 'confidence', 'base_true_p', 'true_p', 'delta_p_squared',
            'minus_2_delta_true_p', 'base_margin', 'margin', 'dCE_dT_at_1', 'dBrier_dT_at_1']
    for (arm, eta, split, state), z in rows.groupby(['arm', 'eta', 'split', 'state']):
        denom = len(rows[rows.arm.eq(arm) & rows.eta.eq(eta) & rows.split.eq(split)])
        transitions.append(dict(arm=arm, eta=float(eta), split=split, state=state, n=len(z),
                                unique_visits=z.visit_id.nunique(), unique_contents=z.content_id.nunique(),
                                **{k: float(z[k].mean()) for k in cols},
                                CE_contribution=float(z.delta_CE.sum()/denom),
                                Brier_contribution=float(z.delta_Brier.sum()/denom),
                                base_wrong_conf90=int(((z.old_prediction != z.y)&z.base_confidence.ge(.9)).sum()),
                                wrong_conf90=int(((z.prediction != z.y)&z.confidence.ge(.9)).sum()),
                                base_wrong_conf99=int(((z.old_prediction != z.y)&z.base_confidence.ge(.99)).sum()),
                                wrong_conf99=int(((z.prediction != z.y)&z.confidence.ge(.99)).sum())))
    breakdowns = {}
    for field in ['content_id', 'protocol', 'seed']:
        parts = []
        for (arm, eta, split, value), z in rows.groupby(['arm', 'eta', 'split', field]):
            parts.append(dict(arm=arm, eta=float(eta), split=split, value=str(value), n=len(z),
                              **{k: float(z[k].mean()) for k in cols},
                              repairs=int(z.state.eq('wrong->correct').sum()),
                              added_errors=int(z.state.eq('correct->wrong').sum())))
        breakdowns[field] = parts
    baseline = b.merge(labels, on=['role_id', 'visit_id'], validate='one_to_one')
    bp, blp, y = baseline[PC].to_numpy(), baseline[LC].to_numpy(), baseline.y.to_numpy(dtype=int)
    dc, db = temperature_derivatives(bp, blp, y)
    base_directions = []
    for split in ['all', 'C', 'U']:
        ix = np.ones(len(y), bool) if split == 'all' else baseline.split.eq(split).to_numpy()
        base_directions.append(dict(split=split, n=int(ix.sum()),
                                    dCE_dT_at_1=float(dc[ix].mean()), dBrier_dT_at_1=float(db[ix].mean())))
    # Keep source identities/hashes stable and guard against accidental writes.
    for name, expected in inputs.items():
        assert sha(ROOT / name) == expected
    result = dict(passed=True, source=str(RUN.relative_to(ROOT)).replace('\\', '/'),
                  input_bindings=inputs, code_sha256=sha(Path(__file__)),
                  device=torch.cuda.get_device_name(), precision='float64',
                  new_fits=0, temperature_fits=0, new_temperature_predictions=0,
                  H_reads=0, actual_U_reads=0, source_unique_visits=96, source_unique_contents=6,
                  prediction_exposures=6912, baseline=base_summary, cells=cells,
                  baseline_temperature_derivatives=base_directions, transitions=transitions,
                  breakdowns=breakdowns, class_changes=flips,
                  limitations=['Source-internal retrospective diagnostics only',
                               'Repeated role/seed exposures are not independent visits',
                               'Local derivative is not calibrated held-content performance'])
    OUT.mkdir(parents=True)
    with (OUT/'analysis.json').open('x', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write('\n')
    # Detailed row evidence is new diagnostic output, not new predictions.
    rows.to_parquet(OUT/'frozen-row-diagnostics.parquet', index=False)
    print(json.dumps(dict(passed=True, outputs=str(OUT), cells=cells), indent=2))
    for row in transitions:
        if row['arm'] == 'P' and row['eta'] == .01:
            print(json.dumps(row))
    print('BASE_DERIVATIVES', json.dumps(base_directions))


if __name__ == '__main__':
    main()
