"""CT08-CT19 source-only fits, post/pre matrices and sealed offline kernel scores."""
from common import *

def modelpath(r, t): return OUT/'models'/r['id']/f't{t:g}.pt'
def fit_roles(inner):
    c = start('diag_inner_fit' if inner else 'diag_outer_fit')
    choices = {} if inner else {(r['kind'], r['outer'], r['protocol']): r['t'] for r in read(OUT/'diagnostics/choices.json')}
    if not inner: require(sha(OUT/'diagnostics/choices.json') == read(OUT/'diagnostics/selection-complete.json')['sha256'], 'Diagnostic choice seal')
    count = 0
    for r in c['diagnostics']:
        if (r['inner'] is not None) != inner: continue
        d = package(rolepath(r)/'train.parquet', 'diag-fit')
        require(set(d.content_id) == set(r['train_contents']), 'Diagnostic train scope')
        raw = tensor(d[HIST]); mu, scale = scaler(raw); x = (raw-mu)/scale
        y = tensor(truths(d), torch.long); mass = torch.full((len(d),), 1/len(d), device=device(), dtype=torch.float64)
        for t in TS if inner else [choices[(r['kind'], r['outer'], r['protocol'])]]:
            p = modelpath(r, t)
            if p.with_suffix('.json').exists(): artifact(p)
            else:
                m, log = fit(x, y, mass, t)
                save_artifact({'mu': mu, 'scale': scale, **m}, p, optimizer=log, role_id=r['id'],
                              train_contents=r['train_contents'], target_data_used=False)
            count += 1
            progress('CT10_CT14_diag_inner' if inner else 'CT12_CT15_diag_outer', models=count,
                     total=640 if inner else 40, role=r['id'], t=t)
    require(count == (640 if inner else 40), 'Diagnostic fit count')
    finish('diag_inner_fit' if inner else 'diag_outer_fit', new_fit_budget=count)

def select():
    c = start('diag_select'); allrows = []
    for r in c['diagnostics']:
        if r['inner'] is None: continue
        for p in r['sources']:
            query = package(rolepath(r)/f'query-{p}.parquet', 'diag-predict')
            for t in TS:
                d = predict(artifact(modelpath(r, t)), query)
                d['kind'] = r['kind']; d['outer'] = r['outer']; d['protocol'] = r['protocol']
                d['inner'] = r['inner']; d['target'] = p; d['t'] = t; allrows.append(d)
    pred = pd.concat(allrows, ignore_index=True)
    pp = OUT/'diagnostics/inner-predictions.parquet'; save(pred, pp)
    complete(OUT/'diagnostics/inner-predictions-complete.json', sha256=sha(pp), rows=len(pred), outer_labels_read=False)
    labels = []
    for r in c['diagnostics']:
        if r['inner'] is None: continue
        for p in r['sources']:
            d = package(rolepath(r)/f'labels-{p}.parquet', 'diag-select').copy()
            d['kind'] = r['kind']; d['outer'] = r['outer']; d['source_protocol'] = r['protocol']
            d['inner'] = r['inner']; d['target'] = p; d = d.drop(columns='protocol')
            labels.append(d)
    score = pd.concat(labels, ignore_index=True).rename(columns={'source_protocol': 'protocol'})
    scored = pred.merge(score, on=['kind', 'outer', 'protocol', 'inner', 'target', 'visit_id'], validate='many_to_one')
    summaries = []
    for key, d in scored.groupby(['kind', 'outer', 'protocol', 't']):
        values = []
        for p, dd in d.groupby('target'):
            require(len(dd) == 96 and dd.content_id.nunique() == 24, 'Diagnostic source validation coverage')
            values.append(metrics(truths(dd), dd[[f'p{i}' for i in range(6)]].to_numpy())[0]['F1_all'])
        summaries.append(dict(zip(['kind', 'outer', 'protocol', 't'], key), F1=float(np.mean(values))))
    table = pd.DataFrame(summaries); chosen = []
    for key, d in table.groupby(['kind', 'outer', 'protocol']):
        winner = d[d.F1 >= d.F1.max()-1e-12].sort_values('t').iloc[0]
        chosen.append(dict(zip(['kind', 'outer', 'protocol'], key), t=float(winner.t), inner_F1=float(winner.F1)))
    require(len(chosen) == 40, 'Diagnostic choices')
    save(table, OUT/'diagnostics/candidates.parquet'); write(OUT/'diagnostics/choices.json', chosen)
    complete(OUT/'diagnostics/selection-complete.json', sha256=sha(OUT/'diagnostics/choices.json'), actual_target_reads=0)
    finish('diag_select', choices=40)

def predict_all():
    c = start('diag_predict'); rows = []; error = 0
    oldpred = None
    for r in read(OUT/'manifests/reused-post-models.json'):
        p = ROOT/r['path']; checked(p, c['baseline_sha256'], 'reused_source_post')
        m = torch.load(p, map_location=device(), weights_only=True)
        for target in PROTOCOLS:
            base = OUT/'packages/diagnostics/post'/f"f{r['outer']}"/target
            d = predict(m, package(base/'query.parquet', 'diag-predict'))
            d['kind'] = 'post'; d['outer'] = r['outer']; d['source'] = r['protocol']; d['target'] = target
            rows.append(d)
    choices = {(r['kind'], r['outer'], r['protocol']): r['t'] for r in read(OUT/'diagnostics/choices.json')}
    for r in c['diagnostics']:
        if r['inner'] is not None: continue
        m = artifact(modelpath(r, choices[(r['kind'], r['outer'], r['protocol'])]))
        for target in PROTOCOLS if r['kind'] == 'pre' else [r['protocol']]:
            d = predict(m, package(rolepath(r)/f'query-{target}.parquet', 'diag-predict'))
            d['kind'] = r['kind']; d['outer'] = r['outer']
            d['source'] = r['protocol'] if r['kind'] == 'pre' else '+'.join(r['sources'])
            d['target'] = target; rows.append(d)
    pred = pd.concat(rows, ignore_index=True); require(len(pred) == 4320, 'Diagnostic prediction count')
    # Reused old probabilities contain no labels; validate diagonal without opening score packages.
    checked(OLD/'predictions/visits.parquet', c['baseline_sha256'], 'old_probability_replay')
    oldpred = pd.read_parquet(OLD/'predictions/visits.parquet')
    oldpred = oldpred[oldpred.arm.eq('KSR1')]
    for (outer, p), d in pred[pred.kind.eq('post')&pred.source.eq(pred.target)].groupby(['outer', 'source']):
        previous = oldpred[oldpred.outer.eq(outer)&oldpred.protocol.eq(p)].set_index('visit_id').loc[d.visit_id]
        error = max(error, float(np.abs(previous[[f'p{i}' for i in range(6)]].to_numpy()-d[[f'p{i}' for i in range(6)]].to_numpy()).max()))
    require(error < 1e-8, 'Post diagonal probability replay')
    path = OUT/'diagnostics/predictions/visits.parquet'; save(pred, path)
    complete(path.parent/'complete.json', sha256=sha(path), rows=len(pred), diagonal_max_error=error,
             labels_read=False, test_paired_read=False)
    finish('diag_predict', rows=len(pred), diagonal_max_error=error)

def kernel_scores():
    c = start('diag_kernel_score'); rows = []
    require((OUT/'diagnostics/predictions/complete.json').exists(), 'Predictions not sealed')
    for outer in range(5):
      for source in PROTOCOLS:
        bundles = {}
        for f in FEATURES:
            p = Q/'kernels/primary'/f'f{outer}'/source/(f+'.pt')
            checked(p, c['baseline_sha256'], 'frozen_source24_kernel')
            bundles[f] = torch.load(p, map_location=device(), weights_only=True)
        for target in PROTOCOLS:
            d = package(OUT/'packages/diagnostics/post'/f'f{outer}'/target/'test-paired.parquet', 'diag-kernel-score')
            for j, f in enumerate(FEATURES):
                b = bundles[f]; aidx = bins(d['pre_'+f], j); bidx = bins(d['post_'+f], j)
                loss = -torch.log2(b['M1'][aidx, bidx]); zero = -torch.log2(b['M0'][bidx])
                zero_support = (b['true_counts'].sum(1)[aidx] == 0).to(torch.float64)
                z = d[['visit_id', 'content_id', 'label_id']].copy()
                z['loss_bits'] = loss.cpu().numpy(); z['marginal_bits'] = zero.cpu().numpy()
                z['zero_support_fraction'] = zero_support.cpu().numpy()
                z = z.groupby(['visit_id', 'content_id', 'label_id'], as_index=False).mean(numeric_only=True)
                z['source'] = source; z['target'] = target; z['outer'] = outer; z['feature'] = f
                rows.append(z)
    save(pd.concat(rows, ignore_index=True), OUT/'diagnostics/kernel-visit-scores.parquet')
    finish('diag_kernel_score', source_kernels=20, feature_visit_rows=sum(len(x) for x in rows))

def score():
    c = start('diag_score'); path = OUT/'diagnostics/predictions/visits.parquet'
    require(sha(path) == read(path.parent/'complete.json')['sha256'], 'Diagnostic predictions changed')
    pred = pd.read_parquet(path); labels = []
    for outer in range(5):
      for target in PROTOCOLS:
        d = package(OUT/'packages/diagnostics/post'/f'f{outer}'/target/'labels.parquet', 'diag-score')
        d = d.drop(columns='protocol'); d['outer'] = outer; d['target'] = target; labels.append(d)
    scored = pred.merge(pd.concat(labels, ignore_index=True), on=['outer', 'target', 'visit_id'], validate='many_to_one')
    rows = []
    for (kind, source, target), d in scored.groupby(['kind', 'source', 'target']):
        require(len(d) == 120 and d.content_id.nunique() == 30, 'Diagnostic total coverage')
        m, cm, _ = metrics(truths(d), d[[f'p{i}' for i in range(6)]].to_numpy())
        rows.append({'kind': kind, 'source': source, 'target': target, **m})
    save(pd.DataFrame(rows), OUT/'diagnostics/classification-summary.parquet')
    k = pd.read_parquet(OUT/'diagnostics/kernel-visit-scores.parquet')
    # Each content has four visits. First content means, then deployment-cell means.
    means = k.groupby(['source', 'target', 'feature', 'content_id'], as_index=False)[['loss_bits', 'marginal_bits', 'zero_support_fraction']].mean()
    table = means.groupby(['source', 'target', 'feature'], as_index=False)[['loss_bits', 'marginal_bits', 'zero_support_fraction']].mean()
    save(table, OUT/'diagnostics/kernel-feature-summary.parquet')
    finish('diag_score', classification_cells=len(rows), kernel_feature_cells=len(table), models_changed=False)

if __name__ == '__main__':
    import sys
    {'inner-fit': lambda: fit_roles(True), 'select': select, 'outer-fit': lambda: fit_roles(False),
     'predict': predict_all, 'kernels': kernel_scores, 'score': score}[sys.argv[1]]()
