"""Content-cross-fitted CUDA scalar calibration of frozen source predictions.

Stages use distinct, sealed packages. No checkpoint, raw PCAP, actual H or actual
target U is loaded. Each role/fit sees only its own five calibration contents.
"""
from pathlib import Path
import argparse
import hashlib
import json
import time
import numpy as np
import pandas as pd
import torch

ROOT = Path(__file__).resolve().parents[2]
OLD = ROOT/'outputs/post-associated-frozen-readout-20261014/run-01'
DIAG = ROOT/'outputs/post-associated-confidence-diagnostic-20261015/run-01'
OUT = ROOT/'outputs/post-associated-temperature-calibration-20261015/run-02'
PLAN = ROOT/'plan/post-associated-rank-preserving-calibration-plan-20261015.md'
LABELS = ['bing.com::search_results_view', 'developer.mozilla.org::document_view',
          'github.com::repository_view', 'wikipedia.org::article_view',
          'youtube.com::search_results_view', 'youtube.com::video_playback']
PC, LC = [f'p{k}' for k in range(6)], [f'l{k}' for k in range(6)]
PIPES = ['base'] + [f'{a}_eta{e}' for a in ['X', 'R', 'G', 'P'] for e in ['1', '0p01']]
READS = []


def rel(p):
    return p.relative_to(ROOT).as_posix()


def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda: f.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def read(p):
    return json.loads(p.read_text(encoding='utf-8'))


def write(p, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('x', encoding='utf-8') as f:
        json.dump(obj, f, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False)
        f.write('\n')


def frame(p, purpose, expected=None, role=None):
    if expected is not None:
        assert sha(p) == expected, str(p)
    READS.append(dict(path=rel(p), purpose=purpose, role_id=role))
    return pd.read_parquet(p)


def save_frame(p, d):
    assert not p.exists()
    p.parent.mkdir(parents=True, exist_ok=True)
    d.to_parquet(p, index=False)


def seal(name, paths, **extra):
    write(OUT/name, dict(passed=True, files={rel(p): sha(p) for p in paths}, **extra))


def check_seal(name):
    x = read(OUT/name)
    assert x['passed']
    for p, h in x['files'].items():
        assert sha(ROOT/p) == h, p
    return x


def contract():
    check_seal('manifests/registration-seal.json')
    c = read(OUT/'manifests/contract.json')
    for p, h in c['code_files'].items():
        assert sha(ROOT/p) == h, p
    assert sha(PLAN) == c['plan_sha256']
    return c


def cuda():
    assert torch.cuda.is_available(), 'CUDA is mandatory; no CPU fitting fallback.'
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False


def objective(logits, y, w, inverse_temperature):
    z = logits * inverse_temperature[:, None, None]
    lp = torch.log_softmax(z, -1)
    p = lp.exp()
    ly = logits.gather(2, y[:, :, None]).squeeze(2)
    ce = (-lp.gather(2, y[:, :, None]).squeeze(2)*w).sum(1)
    mean = (p*logits).sum(2)
    gradient = ((mean-ly)*w).sum(1)
    hessian = (((p*logits.square()).sum(2)-mean.square())*w).sum(1)
    return ce, gradient, hessian


def solve(logits, y, w):
    """Batched independent convex solves, <=64 objective evaluations per fit."""
    n = len(logits)
    lo = torch.full((n,), .2, device='cuda', dtype=torch.float64)
    hi = torch.ones_like(lo)
    flo, glo, _ = objective(logits, y, w, lo)
    fhi, ghi, _ = objective(logits, y, w, hi)
    upper = ghi <= 0
    lower = (glo >= 0) & ~upper
    active = ~(upper | lower)
    beta = torch.where(upper, hi, torch.where(lower, lo, (lo+hi)/2))
    count = torch.full((n,), 2, device='cuda', dtype=torch.int64)
    for _ in range(61):  # Leave one of 64 evaluations for final independent replay.
        if not active.any().item():
            break
        ix = torch.nonzero(active).flatten()
        mid = (lo[ix]+hi[ix])/2
        _, g, _ = objective(logits[ix], y[ix], w[ix], mid)
        count[ix] += 1
        beta[ix] = mid
        negative = g < 0
        lo[ix] = torch.where(negative, mid, lo[ix])
        hi[ix] = torch.where(negative, hi[ix], mid)
        glo[ix] = torch.where(negative, g, glo[ix])
        ghi[ix] = torch.where(negative, ghi[ix], g)
        done = (g.abs() <= 1e-8) | ((hi[ix]-lo[ix]) <= 1e-10)
        active[ix[done]] = False
    assert not active.any().item(), 'Fixed calibration budget exhausted.'
    value, gradient, hess = objective(logits, y, w, beta)
    count += 1
    assert (count <= 64).all().item()
    assert (value <= fhi+1e-10).all().item()
    assert (hess >= -1e-10).all().item()
    interior = ~(upper | lower)
    qualified = ((upper & (gradient <= 1e-8)) | (lower & (gradient >= -1e-8)) |
                 (interior & ((gradient.abs() <= 1e-8) |
                  (((hi-lo) <= 1e-10) & (glo <= 0) & (ghi >= 0)))))
    assert qualified.all().item()
    return dict(inverse_temperature=beta.cpu().numpy(), temperature=(1/beta).cpu().numpy(),
                objective=value.cpu().numpy(), initial_objective=fhi.cpu().numpy(),
                gradient=gradient.cpu().numpy(), hessian=hess.cpu().numpy(),
                bracket_lower=lo.cpu().numpy(), bracket_upper=hi.cpu().numpy(),
                bracket_gradient_lower=glo.cpu().numpy(), bracket_gradient_upper=ghi.cpu().numpy(),
                function_evaluations=count.cpu().numpy(),
                status=np.where(upper.cpu().numpy(), 'T1', np.where(lower.cpu().numpy(), 'T5', 'interior')))


def register():
    assert not OUT.exists(), 'Preserve all existing runs; do not overwrite.'
    old = read(OLD/'manifests/experiment-contract.json')
    assert read(OLD/'completion.json')['passed']
    assert sha(OLD/'manifests/experiment-contract.json') == read(OLD/'manifests/contract-seal.json')['sha256']
    diag = read(DIAG/'analysis.json')
    assert read(DIAG/'verification.json')['passed']
    inputs = dict(diag['input_bindings'])
    for path, expected in inputs.items():
        assert sha(ROOT/path) == expected, path
    for p in [DIAG/'analysis.json', DIAG/'verification.json', DIAG/'frozen-row-diagnostics.parquet']:
        inputs[rel(p)] = sha(p)
    d = frame(OLD/'predictions/visits.parquet', 'register-frozen-predictions')
    b = frame(OLD/'predictions/base.parquet', 'register-frozen-baseline')
    assert len(d) == 6912 and len(b) == 288
    d['pipeline'] = [f'{a}_eta'+('1' if e == 1 else '0p01') for a, e in zip(d.arm, d.eta)]
    assert set(d.eta) == {1., .01} and set(d.arm) == {'X', 'R', 'G', 'P'}
    b = b.assign(pipeline='base', seed=-1)
    contents = sorted(set().union(*(set(r['validation_contents']) for r in old['roles'])))
    assert len(contents) == 6
    assert all(not set(contents)&set(r['train_contents']) for r in old['roles'])
    paths, jobs, rmeta = [], [], []
    for ri, r in enumerate(old['roles']):
        rid = r['id']
        labelpath = ROOT/r['labels']
        src = old['sources'][r['labels']]
        assert src['kind'] == 'query-label'
        lab = frame(labelpath, 'register-legal-source-query-label', src['sha256'], rid)
        assert len(lab) == 24 and lab.visit_id.is_unique
        assert set(lab.content_id) == set(contents) == set(r['validation_contents'])
        assert lab.groupby('content_id').size().eq(4).all()
        assert (lab.protocol == r['calibration']).all()
        lab['y'] = lab.label_id.map({v: k for k, v in enumerate(LABELS)})
        assert not lab.y.isna().any() and lab.groupby('content_id').y.nunique().eq(1).all()
        assert lab.y.value_counts().to_dict() == {k: 4 for k in range(6)}
        core = pd.concat([b[b.role_id.eq(rid)], d[d.role_id.eq(rid)]], ignore_index=True)
        keep = ['role_id', 'pipeline', 'seed', 'visit_id', *PC, *LC]
        core = core[keep].merge(lab[['visit_id', 'content_id', 'protocol']], on='visit_id', validate='many_to_one')
        assert len(core) == 600 and set(core.pipeline) == set(PIPES)
        assert not core.duplicated(['pipeline', 'seed', 'visit_id']).any()
        core['calibration_fold'] = core.content_id.map({v: k for k, v in enumerate(contents)})
        evaluation = OUT/f'packages/r{ri:02d}/evaluation.parquet'
        scoring = OUT/f'packages/r{ri:02d}/scoring-labels.parquet'
        save_frame(evaluation, core)
        save_frame(scoring, lab[['visit_id', 'content_id', 'protocol', 'y']])
        paths += [evaluation, scoring]
        calibration = []
        for fold, held in enumerate(contents):
            cal = core[core.content_id.ne(held)].merge(lab[['visit_id', 'y']], on='visit_id', validate='many_to_one')
            assert len(cal) == 500 and cal.visit_id.nunique() == 20 and cal.content_id.nunique() == 5
            path = OUT/f'packages/r{ri:02d}/calibration/h{fold}.parquet'
            save_frame(path, cal)
            paths.append(path)
            calibration.append(rel(path))
            for pipe in PIPES:
                sub = cal[cal.pipeline.eq(pipe)]
                seeds = sorted(int(v) for v in sub.seed.unique())
                assert len(sub) == (20 if pipe == 'base' else 60)
                assert seeds == ([-1] if pipe == 'base' else old['seeds'])
                jobs.append(dict(id=f'r{ri:02d}/{pipe}/h{fold}', role_id=rid, pipeline=pipe, fold=fold,
                                 held_content=held, calibration_file=rel(path), calibration_sha256=sha(path),
                                 calibration_contents=sorted(set(sub.content_id)),
                                 calibration_visit_ids=sorted(set(sub.visit_id)), seeds=seeds))
        rmeta.append(dict(id=rid, query_protocol=r['calibration'], actual_target=r['target'],
                          missing=r['missing'], train_contents=r['train_contents'],
                          evaluation=rel(evaluation), scoring_labels=rel(scoring),
                          calibration_files=calibration))
    assert len(jobs) == 648 and len({j['id'] for j in jobs}) == 648
    code = [Path(__file__), Path(__file__).with_name('audit.py')]
    c = dict(version='source-temperature-v1', authorized='User authorized execution on 2026-10-15',
             plan_sha256=sha(PLAN), code_files={rel(p): sha(p) for p in code}, old_inputs=inputs,
             roles=rmeta, contents=contents, pipelines=PIPES, jobs=jobs, temperature_range=[1., 5.],
             inverse_temperature_range=[.2, 1.], max_function_evaluations=64,
             derivative_tolerance=1e-8, bracket_tolerance=1e-10, replay_tolerance=1e-10,
             objective='calibration-only equal content/visit/seed six-class CE',
             source_unique_contents=6, source_unique_visits=96, CUDA_required=True,
             H_forbidden=True, actual_U_forbidden=True,
             gates=dict(CE_control_margin=.002, C_F1_cost=.01, C_deployment_F1_cost=.02),
             training_fits=dict(classifiers=0, G=0, teachers=0))
    write(OUT/'manifests/contract.json', c)
    seal('manifests/registration-seal.json', [OUT/'manifests/contract.json', *paths])
    write(OUT/'stages/P0-register.json', dict(passed=True, reads=READS, jobs=648, packages=len(paths)))
    print('P0 registered 648 role-isolated calibration jobs.', flush=True)


def unit_tests():
    contract()
    cuda()
    # Exact analytic interior optimum, monotonic boundary optima and flat case.
    logits = np.zeros((4, 10, 6), float)
    logits[:, :, 0] = 2.
    yy = np.array([[0]*10, [1]*10, [0]*4+[1]*6, [0]*10])
    logits[3] = 0
    l = torch.tensor(logits, device='cuda', dtype=torch.float64)
    y = torch.tensor(yy, device='cuda', dtype=torch.int64)
    w = torch.full((4, 10), .1, device='cuda', dtype=torch.float64)
    got = solve(l, y, w)
    exact = np.log((.4/.6)*5)/2
    assert abs(got['inverse_temperature'][2]-exact) < 1e-7
    assert list(got['status']) == ['T1', 'T5', 'interior', 'T1']
    beta = torch.full((4,), .7, device='cuda', dtype=torch.float64, requires_grad=True)
    val, deriv, hess = objective(l, y, w, beta)
    ag = torch.autograd.grad(val.sum(), beta, create_graph=True)[0]
    ah = torch.autograd.grad(ag.sum(), beta)[0]
    assert torch.max(torch.abs(ag-deriv)).item() < 1e-12
    assert torch.max(torch.abs(ah-hess)).item() < 1e-12
    h = 1e-5
    fd = (objective(l, y, w, beta.detach()+h)[0]-objective(l, y, w, beta.detach()-h)[0])/(2*h)
    assert torch.max(torch.abs(fd-deriv)).item() < 1e-8
    repeated = solve(l.repeat_interleave(3, 1), y.repeat_interleave(3, 1), w.repeat_interleave(3, 1)/3)
    assert np.max(abs(repeated['temperature']-got['temperature'])) < 1e-7
    shifted = solve(l+torch.arange(10, device='cuda', dtype=torch.float64)[None, :, None], y, w)
    # A flat objective has no identifiable temperature. Check probabilities,
    # rather than demanding the same arbitrary minimizer, for that case.
    assert np.max(abs(shifted['temperature'][:3]-got['temperature'][:3])) < 1e-7
    before = torch.softmax(l[3]/float(got['temperature'][3]), 1)
    after = torch.softmax(l[3]/float(shifted['temperature'][3]), 1)
    assert (before-after).abs().max().item() < 1e-12
    for t in [1., 1.5, 5.]:
        assert torch.equal(l.argmax(2), torch.log_softmax(l/t, 2).argmax(2))
    write(OUT/'audits/unit-tests.json', dict(passed=True, tests=['interior closed form', 'T1 KKT', 'T5 KKT',
          'flat objective', 'autograd gradient and curvature', 'central difference',
          'seed replication weights', 'common logit shift', 'argmax invariance'],
          device=torch.cuda.get_device_name(), precision='float64', fd_max_error=float((fd-deriv).abs().max())))
    print('P1 CUDA numerical interface tests passed.', flush=True)


def fits():
    c = contract()
    assert read(OUT/'audits/unit-tests.json')['passed']
    cuda()
    packed, targets, weights, metadata = [], [], [], []
    for r in c['roles']:
        # Read each role-only five-content package once, not the held-label file.
        for fold, path in enumerate(r['calibration_files']):
            z = frame(ROOT/path, 'fit-five-contents-only', role=r['id'])
            assert set(z.role_id) == {r['id']} and c['contents'][fold] not in set(z.content_id)
            for pipe in PIPES:
                sub = z[z.pipeline.eq(pipe)].sort_values(['visit_id', 'seed']).reset_index(drop=True)
                job = next(j for j in c['jobs'] if j['role_id'] == r['id'] and j['fold'] == fold and j['pipeline'] == pipe)
                assert rel(ROOT/path) == job['calibration_file'] and sha(ROOT/path) == job['calibration_sha256']
                assert set(sub.content_id) == set(job['calibration_contents'])
                assert set(sub.visit_id) == set(job['calibration_visit_ids'])
                assert sub.visit_id.nunique() == 20 and sub.groupby('visit_id').size().eq(len(job['seeds'])).all()
                assert sub.groupby('content_id').visit_id.nunique().eq(4).all()
                n = len(sub)
                l, y, w = np.zeros((60, 6)), np.zeros(60, dtype=int), np.zeros(60)
                l[:n], y[:n], w[:n] = sub[LC].to_numpy(), sub.y.to_numpy(), 1/n
                assert abs(w.sum()-1) < 1e-14
                packed.append(l)
                targets.append(y)
                weights.append(w)
                metadata.append(job)
    l = torch.tensor(np.stack(packed), device='cuda', dtype=torch.float64)
    y = torch.tensor(np.stack(targets), device='cuda', dtype=torch.int64)
    w = torch.tensor(np.stack(weights), device='cuda', dtype=torch.float64)
    start = time.perf_counter()
    got = solve(l, y, w)
    torch.cuda.synchronize()
    elapsed = time.perf_counter()-start
    records = []
    # Independent CPU arithmetic of each accepted scalar, not a second optimizer.
    for i, job in enumerate(metadata):
        result = {k: (v[i].item() if hasattr(v[i], 'item') else str(v[i])) for k, v in got.items()}
        beta = result['inverse_temperature']
        z = packed[i]*beta
        z -= z.max(1, keepdims=True)
        lp = z-np.log(np.exp(z).sum(1, keepdims=True))
        objective_replay = float((-lp[np.arange(60), targets[i]]*weights[i]).sum())
        derivative_replay = float((((np.exp(lp)*packed[i]).sum(1)-packed[i][np.arange(60), targets[i]])*weights[i]).sum())
        assert abs(objective_replay-result['objective']) <= 1e-10
        assert abs(derivative_replay-result['gradient']) <= 1e-10
        records.append(dict(**job, **result, qualified=True,
                            objective_replay_error=abs(objective_replay-result['objective']),
                            gradient_replay_error=abs(derivative_replay-result['gradient'])))
    assert len(records) == 648
    write(OUT/'fits/temperatures.json', records)
    write(OUT/'stages/P2-fit.json', dict(passed=True, reads=READS, temperature_fits=648,
          classifier_fits=0, G_fits=0, teacher_fits=0, cuda_solve_seconds=elapsed,
          device=torch.cuda.get_device_name(), precision='float64', TF32=False))
    seal('manifests/temperatures-complete.json', [OUT/'fits/temperatures.json', OUT/'stages/P2-fit.json',
         OUT/'audits/unit-tests.json'], fits=648, classification_fits=0)
    print(f'P2 sealed 648 temperatures, CUDA solve {elapsed:.3f} s.', flush=True)


def predict():
    c = contract()
    check_seal('manifests/temperatures-complete.json')
    ts = read(OUT/'fits/temperatures.json')
    idx = {(t['role_id'], t['pipeline'], t['fold']): t for t in ts}
    cuda()
    parts, exact_ties = [], 0
    for r in c['roles']:
        z = frame(ROOT/r['evaluation'], 'predict-label-free-frozen-logits', role=r['id'])
        assert 'y' not in z.columns and 'label_id' not in z.columns
        assert set(z.role_id) == {r['id']}
        temperatures = np.array([idx[(r['id'], p, int(f))]['temperature'] for p, f in zip(z.pipeline, z.calibration_fold)])
        original = torch.tensor(z[LC].to_numpy(), device='cuda', dtype=torch.float64)
        t = torch.tensor(temperatures, device='cuda', dtype=torch.float64)
        with torch.no_grad():
            lp = torch.log_softmax(original/t[:, None], 1)
        assert torch.equal(original.argmax(1), lp.argmax(1)), 'Class changed: stop.'
        assert np.array_equal(z[PC].to_numpy().argmax(1), original.argmax(1).cpu().numpy())
        exact_ties += int((original == original.max(1, keepdim=True).values).sum(1).gt(1).sum())
        z = z.rename(columns={k: 'raw_'+k for k in [*PC, *LC]})
        z['temperature'] = temperatures
        for k in range(6):
            z[f'l{k}'] = lp[:, k].cpu().numpy()
            z[f'p{k}'] = lp[:, k].exp().cpu().numpy()
        parts.append(z)
    out = pd.concat(parts, ignore_index=True)
    assert len(out) == 7200 and out.visit_id.nunique() == 96
    save_frame(OUT/'predictions/visits.parquet', out)
    write(OUT/'stages/P3-predict.json', dict(passed=True, reads=READS, rows=7200,
          label_reads=0, changed_classes=0, exact_ties=exact_ties,
          T_min=float(out.temperature.min()), T_max=float(out.temperature.max())))
    seal('manifests/predictions-complete.json', [OUT/'predictions/visits.parquet', OUT/'stages/P3-predict.json'], rows=7200)
    print('P3 sealed 7200 calibrated probabilities; all classes unchanged.', flush=True)


def metric(y, p, lp, missing):
    cm = np.bincount(y*6+p.argmax(1), minlength=36).reshape(6, 6)
    den = cm.sum(0)+cm.sum(1)
    f1 = np.divide(2*np.diag(cm), den, out=np.zeros(6), where=den > 0)
    u = np.isin(y, missing)
    ce = -lp[np.arange(len(y)), y]
    br = ((p-np.eye(6)[y])**2).sum(1)
    return dict(F1_all=float(f1.mean()), F1_U=float(f1[missing].mean()),
                F1_C=float(np.delete(f1, missing).mean()), CE_all=float(ce.mean()),
                CE_U=float(ce[u].mean()), CE_C=float(ce[~u].mean()),
                Brier=float(br.mean()), Brier_U=float(br[u].mean()), Brier_C=float(br[~u].mean()),
                accuracy=float((p.argmax(1) == y).mean()), confusion_matrix=cm.tolist())


def score():
    c = contract()
    check_seal('manifests/temperatures-complete.json')
    check_seal('manifests/predictions-complete.json')
    d = frame(OUT/'predictions/visits.parquet', 'score-sealed-predictions')
    rows, endpoints = [], []
    for r in c['roles']:
        lab = frame(ROOT/r['scoring_labels'], 'score-held-content-labels-after-prediction-seal', role=r['id'])
        z = d[d.role_id.eq(r['id'])].merge(lab[['visit_id', 'y']], on='visit_id', validate='many_to_one')
        base = z[z.pipeline.eq('base')].set_index('visit_id')
        for (pipe, seed), part in z.groupby(['pipeline', 'seed']):
            y = part.y.to_numpy(dtype=int)
            p, lp = part[PC].to_numpy(), part[LC].to_numpy()
            rawp = part[['raw_'+k for k in PC]].to_numpy()
            rawlp = part[['raw_'+k for k in LC]].to_numpy()
            now, old = metric(y, p, lp, r['missing']), metric(y, rawp, rawlp, r['missing'])
            for key in ['F1_all', 'F1_U', 'F1_C', 'accuracy', 'confusion_matrix']:
                assert now[key] == old[key], (pipe, key)
            endpoints.append(dict(role_id=r['id'], pipeline=pipe, seed=int(seed), query_protocol=r['query_protocol'],
                                  raw=old, calibrated=now))
            for i, (_, row) in enumerate(part.iterrows()):
                bp = base.loc[row.visit_id, ['raw_'+k for k in PC]].to_numpy(dtype=float)
                oc = int(bp.argmax()) == y[i]
                nc = int(p[i].argmax()) == y[i]
                state = ('correct' if oc else 'wrong')+'->'+('correct' if nc else 'wrong')
                u = y[i] in r['missing']
                rows.append(dict(role_id=r['id'], pipeline=pipe, seed=int(seed), visit_id=row.visit_id,
                                 content_id=row.content_id, protocol=r['query_protocol'],
                                 split='U' if u else 'C', y=int(y[i]), state=state,
                                 prediction=int(p[i].argmax()), raw_prediction=int(rawp[i].argmax()),
                                 confidence=float(p[i].max()), raw_confidence=float(rawp[i].max()),
                                 true_p=float(p[i, y[i]]), raw_true_p=float(rawp[i, y[i]]),
                                 CE=float(-lp[i, y[i]]), raw_CE=float(-rawlp[i, y[i]]),
                                 Brier=float(((p[i]-np.eye(6)[y[i]])**2).sum()),
                                 raw_Brier=float(((rawp[i]-np.eye(6)[y[i]])**2).sum())))
    assert len(endpoints) == 300 and len(rows) == 7200
    scored = pd.DataFrame(rows)
    metrics = ['F1_all', 'F1_U', 'F1_C', 'CE_all', 'CE_U', 'CE_C', 'Brier', 'Brier_U', 'Brier_C', 'accuracy']
    summary = []
    for pipe in PIPES:
        ep = [e for e in endpoints if e['pipeline'] == pipe]
        item = dict(pipeline=pipe)
        for phase in ['raw', 'calibrated']:
            item[phase] = {k: float(np.mean([e[phase][k] for e in ep])) for k in metrics}
        item['by_protocol'] = []
        for protocol in sorted(set(e['query_protocol'] for e in ep)):
            q = [e for e in ep if e['query_protocol'] == protocol]
            item['by_protocol'].append(dict(protocol=protocol, **{phase: {k: float(np.mean([e[phase][k] for e in q]))
                   for k in metrics} for phase in ['raw', 'calibrated']}))
        summary.append(item)
    idx = {v['pipeline']: v for v in summary}
    main, base = idx['P_eta0p01'], idx['base']
    p, pr, b = main['calibrated'], main['raw'], base['calibrated']
    probability = dict(classification_exactly_preserved=True,
          CE_U_improved_self=p['CE_U'] < pr['CE_U'], Brier_U_improved_self=p['Brier_U'] < pr['Brier_U'],
          CE_all_not_worse_self=p['CE_all'] <= pr['CE_all']+1e-12,
          Brier_all_not_worse_self=p['Brier'] <= pr['Brier']+1e-12,
          not_worse_calibrated_base={k: p[k] <= b[k]+1e-12 for k in ['CE_U', 'Brier_U', 'CE_all', 'Brier']})
    probability_pass = (all(v for k, v in probability.items() if not isinstance(v, dict))
                        and all(probability['not_worse_calibrated_base'].values()))
    controls = ['base', 'X_eta0p01', 'R_eta0p01', 'G_eta0p01']
    increment = dict(CE_margin={key: p['CE_U']-idx[key]['calibrated']['CE_U'] <= -.002+1e-12 for key in controls},
                     F1_U_not_worse={key: p['F1_U'] >= idx[key]['calibrated']['F1_U']-1e-12 for key in controls},
                     C_overall=p['F1_C']-b['F1_C'] >= -.01-1e-12,
                     C_by_protocol=all(e['calibrated']['F1_C']-next(v for v in base['by_protocol'] if v['protocol'] == e['protocol'])['calibrated']['F1_C'] >= -.02-1e-12
                                       for e in main['by_protocol']))
    increment_pass = all(increment['CE_margin'].values()) and all(increment['F1_U_not_worse'].values()) and increment['C_overall'] and increment['C_by_protocol']
    transitions = []
    for (pipe, split, state), z in scored.groupby(['pipeline', 'split', 'state']):
        n = len(scored[scored.pipeline.eq(pipe) & scored.split.eq(split)])
        transitions.append(dict(pipeline=pipe, split=split, state=state, n=len(z),
             unique_visits=z.visit_id.nunique(), unique_contents=z.content_id.nunique(),
             **{k: float(z[k].mean()) for k in ['CE', 'raw_CE', 'Brier', 'raw_Brier', 'confidence', 'raw_confidence', 'true_p', 'raw_true_p']},
             CE_contribution=float((z.CE-z.raw_CE).sum()/n), Brier_contribution=float((z.Brier-z.raw_Brier).sum()/n),
             raw_wrong_conf90=int(((z.prediction != z.y) & z.raw_confidence.ge(.9)).sum()),
             wrong_conf90=int(((z.prediction != z.y) & z.confidence.ge(.9)).sum()),
             raw_wrong_conf99=int(((z.prediction != z.y) & z.raw_confidence.ge(.99)).sum()),
             wrong_conf99=int(((z.prediction != z.y) & z.confidence.ge(.99)).sum())))
    breakdown = []
    for field in ['content_id', 'protocol', 'seed']:
        for (pipe, split, value), z in scored.groupby(['pipeline', 'split', field]):
            breakdown.append(dict(pipeline=pipe, split=split, field=field, value=str(value), n=len(z),
                **{k: float(z[k].mean()) for k in ['CE', 'raw_CE', 'Brier', 'raw_Brier', 'confidence', 'raw_confidence']}))
    ts = read(OUT/'fits/temperatures.json')
    temp = []
    for pipe in PIPES:
        fits = [v for v in ts if v['pipeline'] == pipe]
        t = np.array([v['temperature'] for v in fits])
        temp.append(dict(pipeline=pipe, fits=len(fits), T_min=float(t.min()), T_median=float(np.median(t)),
                         T_max=float(t.max()), T1=sum(v['status'] == 'T1' for v in fits),
                         T5=sum(v['status'] == 'T5' for v in fits),
                         interior=sum(v['status'] == 'interior' for v in fits)))
    write(OUT/'scores/endpoints.json', endpoints)
    save_frame(OUT/'scores/row-analysis.parquet', scored)
    write(OUT/'scores/summary.json', dict(passed=True, pipelines=summary, temperature_summary=temp,
         probability_gates=probability, probability_pass=bool(probability_pass),
         increment_gates=increment, increment_pass=bool(increment_pass),
         advance_full_roles=False, H_scored=False, source_only=True,
         transitions=transitions, breakdowns=breakdown))
    write(OUT/'stages/P4-score.json', dict(passed=True, reads=READS, rows=7200, endpoints=300,
          temperature_parameters_not_updated=True, old_results_unchanged=True))
    seal('manifests/scores-complete.json', [OUT/'scores/endpoints.json', OUT/'scores/row-analysis.parquet',
         OUT/'scores/summary.json', OUT/'stages/P4-score.json'])
    print(json.dumps(dict(probability_pass=bool(probability_pass), increment_pass=bool(increment_pass),
                         paired=main, temperature_summary=temp), indent=2), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('stage', choices=['register', 'test', 'fit', 'predict', 'score'])
    stage = parser.parse_args().stage
    start = time.perf_counter()
    try:
        dict(register=register, test=unit_tests, fit=fits, predict=predict, score=score)[stage]()
    except Exception as error:
        if OUT.exists():
            p = OUT/f'stops/{stage}-{time.time_ns()}.json'
            write(p, dict(passed=False, stage=stage, exception=type(error).__name__, message=str(error), reads=READS))
        raise
    print(f'{stage}: {time.perf_counter()-start:.3f} seconds', flush=True)


if __name__ == '__main__':
    main()
