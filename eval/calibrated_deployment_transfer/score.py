"""CT35-CT39 full six-class scoring and fixed-model common-content inference."""
from common import *

def run():
    c = start('main_score'); path = OUT/'predictions/visits.parquet'
    require(sha(path) == read(path.parent/'complete.json')['sha256'], 'Prediction seal')
    predictions = pd.read_parquet(path); labels = []
    for r in c['main']:
        if r['inner'] is not None: continue
        d = package(rolepath(r)/'labels.parquet', 'main-score').drop(columns='protocol')
        for key in ['outer', 'target', 'group']: d[key] = r[key]
        labels.append(d)
    scored = predictions.merge(pd.concat(labels, ignore_index=True), on=['outer', 'target', 'group', 'visit_id'], validate='many_to_one')
    require(len(scored) == 10080 and scored.visit_id.nunique() == 480, 'Scoring population')
    save(scored, OUT/'scores/scored-visits.parquet')
    folds = pd.read_parquet(OUT/'manifests/content-folds.parquet').sort_values(['label_id', 'content_id'])
    order = folds.content_id.tolist(); code = dict(zip(order, range(30)))
    require([LABELS.index(x) for x in folds.label_id] == list(np.repeat(range(6), 5)), 'Bootstrap label order')
    rng = np.random.default_rng(20261005)
    indices = np.concatenate([rng.choice(np.arange(y*5, y*5+5), (10000, 5), replace=True) for y in range(6)], 1)
    weights = np.zeros((10000, 30), dtype=np.float64)
    for b in range(30): weights[:, b] = (indices == b).sum(1)
    dst = OUT/'comparisons'; dst.mkdir(parents=True, exist_ok=True)
    np.save(dst/'bootstrap-indices.npy', indices); save(folds, dst/'content-order.parquet')
    summary = []; classes = []; bootstrap = {}; domain = {}; cms = {}
    for (target, group, arm), d in scored.groupby(['target', 'group', 'arm']):
        require(len(d) == 120 and d.visit_id.is_unique and d.content_id.nunique() == 30, 'Full outer-fold population')
        p = d[[f'p{i}' for i in range(6)]].to_numpy(); y = truths(d); z = p.argmax(1)
        m, cm, f1 = metrics(y, p, MASKS[group]); summary.append({'target': target, 'group': group, 'arm': arm, **m})
        cms[(target, group, arm)] = cm
        for label in range(6):
            tp = cm[label, label]; predicted = cm[:, label].sum(); actual = cm[label, :].sum()
            classes.append({'target': target, 'group': group, 'arm': arm, 'label_id': LABELS[label],
                            'F1': float(f1[label]), 'precision': float(tp/predicted) if predicted else 0.,
                            'recall': float(tp/actual), 'support': int(actual)})
        w = weights[:, d.content_id.map(code).to_numpy(int)]
        cm_boot = (w@np.eye(36)[y*6+z]).reshape(-1, 6, 6)
        diag = np.diagonal(cm_boot, axis1=1, axis2=2); den = cm_boot.sum(1)+cm_boot.sum(2)
        b_f1 = np.divide(2*diag, den, out=np.zeros_like(diag), where=den > 0)
        vals = {'F1_uncovered': b_f1[:, MASKS[group]].mean(1),
                'F1_aux': np.delete(b_f1, MASKS[group], axis=1).mean(1), 'F1_all': b_f1.mean(1)}
        for metric, value in vals.items():
            bootstrap[(arm, metric)] = bootstrap.get((arm, metric), np.zeros(10000))+value/12
            domain[(target, arm, metric)] = domain.get((target, arm, metric), np.zeros(10000))+value/3
    table = pd.DataFrame(summary); save(table, OUT/'scores/target-group-summary.parquet')
    save(pd.DataFrame(classes), OUT/'scores/class-results.parquet')
    pooled = table.groupby('arm', as_index=False).mean(numeric_only=True)
    targets = table.groupby(['target', 'arm'], as_index=False).mean(numeric_only=True)
    worst = targets.groupby('arm').F1_uncovered.min(); pooled['worst_target_F1_uncovered'] = pooled.arm.map(worst)
    save(pooled, OUT/'scores/equal-weight-summary.parquet'); save(targets, OUT/'scores/target-summary.parquet')
    contrasts = []
    for comparator in ['StrongPost', 'CT1', 'CT3']:
        point = float(pooled.set_index('arm').loc['CT4', 'F1_uncovered']-pooled.set_index('arm').loc[comparator, 'F1_uncovered'])
        delta = bootstrap[('CT4', 'F1_uncovered')]-bootstrap[(comparator, 'F1_uncovered')]
        ordinary = np.quantile(delta, [.025, .975]); adjusted = np.quantile(delta, [.05/6, 1-.05/6])
        aux = float(pooled.set_index('arm').loc['CT4', 'F1_aux']-pooled.set_index('arm').loc[comparator, 'F1_aux'])
        auxdelta = bootstrap[('CT4', 'F1_aux')]-bootstrap[(comparator, 'F1_aux')]
        contrasts.append({'comparison': 'CT4-'+comparator, 'delta_F1_uncovered': point,
                         'CI95_low': float(ordinary[0]), 'CI95_high': float(ordinary[1]),
                         'CI98_333_low': float(adjusted[0]), 'CI98_333_high': float(adjusted[1]),
                         'primary_pass': bool(adjusted[0] > 0), 'delta_F1_aux': aux,
                         'aux_CI95_low': float(np.quantile(auxdelta, .025)), 'aux_CI95_high': float(np.quantile(auxdelta, .975)),
                         'aux_practical_screen_pass': bool(aux >= -.02)})
    worst_gap = min(float(targets.set_index(['target', 'arm']).loc[(p, 'CT4'), 'F1_aux']-
                          targets.set_index(['target', 'arm']).loc[(p, 'StrongPost'), 'F1_aux']) for p in PROTOCOLS)
    save(pd.DataFrame(contrasts), dst/'primary-contrasts.parquet')
    np.savez_compressed(dst/'bootstrap-metrics.npz', **{a+'_'+m: v for (a, m), v in bootstrap.items()})
    np.savez_compressed(OUT/'scores/confusion-matrices.npz', **{'_'.join(k): v for k, v in cms.items()})
    flips = []
    for comparator in ['StrongPost', 'CT0', 'CT1', 'CT2', 'CT3', 'CT5']:
        a = scored[scored.arm.eq('CT4')]; b = scored[scored.arm.eq(comparator)]
        d = a.merge(b[['target', 'group', 'visit_id', 'prediction']], on=['target', 'group', 'visit_id'], suffixes=('', '_reference'), validate='one_to_one')
        y = truths(d); ref = d.prediction_reference.to_numpy(); new = d.prediction.to_numpy()
        d['repair'] = (ref != y)&(new == y); d['added_error'] = (ref == y)&(new != y)
        d['wrong_to_wrong'] = (ref != y)&(new != y)&(ref != new); d['changed'] = ref != new
        g = d.groupby(['target', 'group', 'content_id', 'label_id'], as_index=False)[['repair', 'added_error', 'wrong_to_wrong', 'changed']].sum()
        g['comparator'] = comparator; flips.append(g)
    save(pd.concat(flips, ignore_index=True), OUT/'scores/error-flips.parquet')
    decision = {'all_three_primary_pass': all(v['primary_pass'] for v in contrasts),
                'aux_pooled_screen_pass': all(v['aux_practical_screen_pass'] for v in contrasts),
                'worst_target_aux_gap': worst_gap, 'worst_target_aux_screen_pass': worst_gap >= -.05,
                'statistical_noninferiority_claimed': False, 'conditional_on_fixed_selected_models': True,
                'external_validation': False, 'independent_contents': 30}
    decision['registered_attack_increment_and_practical_screen_pass'] = bool(
        decision['all_three_primary_pass'] and decision['aux_pooled_screen_pass'] and decision['worst_target_aux_screen_pass'])
    write(dst/'decision.json', decision); finish('main_score', comparisons=contrasts, decision=decision)

def explain():
    c = start('main_explain'); rows = []; support = []
    for r in c['main']:
        if r['inner'] is not None: continue
        # Test pre is allowed ONLY after all main class probabilities have been sealed.
        d = package(rolepath(r)/'test-paired.parquet', 'main-explain')
        for arm, kind in [('CT4', 'true'), ('CT3', 'group')]:
            bundle = artifact(OUT/'kernels'/r['kernel_id']/(kind+'.pt'))
            for j, f in enumerate(FEATURES):
                b = bundle[f]; a = bins(d['pre_'+f], j); z = bins(d['post_'+f], j)
                v = d[['visit_id', 'content_id', 'label_id']].copy()
                v['loss_bits'] = (-torch.log2(b['matrix'][a, z])).cpu().numpy()
                v['marginal_bits'] = (-torch.log2(b['q'][z])).cpu().numpy()
                v = v.groupby(['visit_id', 'content_id', 'label_id'], as_index=False).mean(numeric_only=True)
                v['target'] = r['target']; v['group'] = r['group']; v['arm'] = arm; v['feature'] = f
                v['uncovered'] = np.isin(truths(v), r['missing']); rows.append(v)
            p = OUT/'slots'/r['id']/(arm+'-support.pt'); state = artifact(p)['zero_support_mass']
            for j, f in enumerate(FEATURES):
                support.append({'outer': r['outer'], 'target': r['target'], 'group': r['group'], 'arm': arm,
                                'feature': f, 'mean_zero_support_mass': float(state[:, j].mean()),
                                'max_zero_support_mass': float(state[:, j].max()), 'visits_retained': len(state)})
    save(pd.concat(rows, ignore_index=True), OUT/'scores/uncovered-kernel-visit-scores.parquet')
    save(pd.DataFrame(support), OUT/'scores/source-pre-support.parquet')
    finish('main_explain', forbidden_U_train_read=False, offline_test_pre_feedback=False)

if __name__ == '__main__':
    import sys
    {'score': run, 'explain': explain}[sys.argv[1]]()
