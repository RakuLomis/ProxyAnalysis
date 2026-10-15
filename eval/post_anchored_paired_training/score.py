"""Fixed six-contrast family and content-cluster bootstrap, after sealing."""
from common import *


def f1(cm):
    tp = np.diagonal(cm, axis1=-2, axis2=-1); den = cm.sum(-2)+cm.sum(-1)
    return np.divide(2*tp, den, out=np.zeros_like(tp, dtype=float), where=den > 0).mean(-1)


def baseline_replay(pred):
    # Old predictions are read only after new predictions are sealed, without their labels.
    pp = [f'p{k}' for k in range(6)]
    old = pd.read_parquet(OLD/'oof.parquet', columns=['stage', 'arm', 'seed', 'session_id', *pp])
    old = old[old.stage.eq('finetune') & old.arm.eq('B0L')]
    joined = pred[pred.arm.eq('J0')].merge(old[['seed', 'session_id', *pp]],
             on=['seed', 'session_id'], suffixes=('', '_old'), validate='one_to_one')
    assert len(joined) == 1800
    a = joined[pp].to_numpy(float); b = joined[[p+'_old' for p in pp]].to_numpy(float)
    delta = float(np.max(np.abs(a-b))); changed = int(np.sum(a.argmax(1) != b.argmax(1)))
    write(OUT/'baseline-reproduction.json', {'passed': delta <= 1e-5 and changed == 0,
          'rows': 1800, 'maximum_probability_difference': delta, 'changed_decisions': changed,
          'reference': 'sealed E1 B0L', 'test_labels_read': False, 'tolerance': 1e-5})
    assert delta <= 1e-5 and changed == 0, 'baseline numerical replay gate failed; no score selection'


def main():
    authorize(); assert sha(OUT/'oof.parquet') == read(OUT/'prediction-seal.json')['oof_sha256']
    write(OUT/'scoring-source-seal.json', {'source_sha256': sha(Path(__file__)),
          'prediction_sha256': sha(OUT/'oof.parquet'), 'draws_fixed': 10000, 'family': 6})
    raw = pd.read_parquet(OUT/'oof.parquet'); baseline_replay(raw)
    co = pd.read_parquet(OUT/'cohort.parquet'); contract = read(OUT/'contract.json')
    classes, protocols = contract['classes'], contract['protocols']
    labels = pd.concat([Bundle(f, 'scoring').get('labels') for f in range(5)], ignore_index=True)
    assert labels.session_id.is_unique and labels.set_index('session_id').label_id.to_dict() == co.set_index('session_id').label_id.to_dict()
    pred = raw.merge(co, on=['session_id', 'fold'], validate='many_to_one')
    pp = pred[[f'p{k}' for k in range(6)]].to_numpy(float)
    assert np.isfinite(pp).all() and np.allclose(pp.sum(1), 1, atol=1e-5)
    pred['truth'] = pred.label_id.map({v: i for i, v in enumerate(classes)})
    pred['guess'] = pp.argmax(1); pred['correct'] = pred.truth.eq(pred.guess)
    pred['CE_bits'] = -np.log2(np.maximum(pp[np.arange(len(pp)), pred.truth.to_numpy()], 1e-15))
    pred['Brier'] = ((pp-np.eye(6)[pred.truth])**2).sum(1)
    pred.to_parquet(OUT/'scored-oof.parquet', index=False)
    contents = sorted(co.content_id.unique()); blocks = []
    for y in classes:
        cc = sorted(co.loc[co.label_id.eq(y), 'content_id'].unique()); assert len(cc) == 5
        blocks.append([contents.index(v) for v in cc])
    rng = np.random.default_rng(20260928)
    indices = np.concatenate([rng.choice(g, size=(10000, 5), replace=True) for g in blocks], axis=1)
    weights = np.eye(30, dtype=np.int16)[indices].sum(1)
    metrics, aggregate, perclass, confusion, boots, points = [], [], [], [], {}, {}
    for arm, g in pred.groupby('arm'):
        cm = np.zeros((3, 5, 30, 6, 6), dtype=np.int64)
        for row in g[['seed', 'protocol', 'content_id', 'truth', 'guess']].itertuples(index=False):
            cm[SEEDS.index(row.seed), protocols.index(row.protocol), contents.index(row.content_id), row.truth, row.guess] += 1
        pooled = cm.sum(2); ff = f1(pooled); pe = ff.mean(1)
        boots[arm] = f1(np.einsum('dc,spcij->dspij', weights, cm)).mean((1, 2)); points[arm] = pe.mean()
        for si, seed in enumerate(SEEDS):
            for pi, protocol in enumerate(protocols):
                sg = g[g.seed.eq(seed) & g.protocol.eq(protocol)]; conf = pooled[si, pi]
                metrics.append({'arm': arm, 'seed': seed, 'protocol': protocol, 'F1': ff[si, pi],
                                'accuracy': sg.correct.mean(), 'CE_bits': sg.CE_bits.mean(), 'Brier': sg.Brier.mean()})
                tp, rn, cn = conf.diagonal(), conf.sum(1), conf.sum(0)
                for k, y in enumerate(classes):
                    perclass.append({'arm': arm, 'seed': seed, 'protocol': protocol, 'class': y,
                                     'precision': tp[k]/cn[k] if cn[k] else 0., 'recall': tp[k]/rn[k],
                                     'F1': 2*tp[k]/(rn[k]+cn[k]), 'support': rn[k]})
                    for j, yg in enumerate(classes):
                        confusion.append({'arm': arm, 'seed': seed, 'protocol': protocol,
                                          'truth': y, 'guess': yg, 'count': conf[k, j]})
        aggregate.append({'arm': arm, 'F1': pe.mean(), 'min_seed': pe.min(), 'max_seed': pe.max(),
                          'worst_F1': ff.min(1).mean(), 'CE_bits': g.CE_bits.mean(), 'Brier': g.Brier.mean()})
    pairs = [('J4', r, True) for r in PRIMARY]+[('J4', 'J1', False), ('J2', 'J1', False), ('J6', 'J1', False), ('J7', 'J0', False)]
    contrasts, transitions = [], []
    for a, b, primary in pairs:
        delta = boots[a]-boots[b]; lo, hi = np.quantile(delta, [.025, .975])
        adj = np.quantile(delta, [.05/12, 1-.05/12]) if primary else [None, None]
        contrasts.append({'contrast': a+'-'+b, 'primary': primary, 'delta': points[a]-points[b],
                          'low95': lo, 'high95': hi, 'adjusted_low': adj[0], 'adjusted_high': adj[1]})
        joined = pred[pred.arm.eq(a)].merge(pred[pred.arm.eq(b)][['seed', 'session_id', 'correct']],
                 on=['seed', 'session_id'], suffixes=('', '_reference'), validate='one_to_one')
        joined['comparison'] = a+'-'+b; joined['repaired'] = joined.correct & ~joined.correct_reference
        joined['new_error'] = ~joined.correct & joined.correct_reference
        transitions.append(joined[['comparison', 'seed', 'session_id', 'protocol', 'content_id', 'label_id', 'repaired', 'new_error']])
    pd.DataFrame(metrics).to_parquet(OUT/'per-protocol-seed-metrics.parquet', index=False)
    pd.DataFrame(aggregate).to_parquet(OUT/'aggregate-metrics.parquet', index=False)
    pd.DataFrame(perclass).to_parquet(OUT/'per-class-metrics.parquet', index=False)
    pd.DataFrame(confusion).to_parquet(OUT/'confusion-matrices.parquet', index=False)
    pd.DataFrame(contrasts).to_parquet(OUT/'contrasts.parquet', index=False)
    errors = pd.concat(transitions); errors.to_parquet(OUT/'error-transitions.parquet', index=False)
    errors.groupby(['comparison', 'protocol', 'content_id', 'label_id'])[['repaired', 'new_error']].sum().reset_index().to_parquet(OUT/'content-error-transitions.parquet', index=False)
    np.savez_compressed(OUT/'bootstrap.npz', content_indices=indices, **boots)
    from sklearn.metrics import f1_score
    point_errors, draw_errors = [], []
    for row in metrics:
        g = pred[pred.arm.eq(row['arm']) & pred.seed.eq(row['seed']) & pred.protocol.eq(row['protocol'])]
        point_errors.append(abs(f1_score(g.truth, g.guess, labels=range(6), average='macro', zero_division=0)-row['F1']))
    for d in [0, 1, 9999]:
        for arm in ARMS:
            values = []
            for _, g in pred[pred.arm.eq(arm)].groupby(['seed', 'protocol']):
                sw = [weights[d, contents.index(c)] for c in g.content_id]
                values.append(f1_score(g.truth, g.guess, labels=range(6), average='macro', zero_division=0, sample_weight=sw))
            draw_errors.append(abs(np.mean(values)-boots[arm][d]))
    assert max(point_errors) < 1e-12 and max(draw_errors) < 1e-12
    write(OUT/'independent-score-check.json', {'passed': True, 'point_checks': len(point_errors),
          'draw_checks': len(draw_errors), 'maximum_point_error': max(point_errors),
          'maximum_draw_error': max(draw_errors), 'library': 'sklearn.metrics.f1_score'})
    write(OUT/'score-complete.json', {'passed': True, 'draws': 10000, 'primary_family': 6,
          'conditional_on_fixed_models': True, 'visits': 600, 'contents': 30,
          'prediction_sha256': sha(OUT/'oof.parquet'), 'test_selection': False})
    print(pd.DataFrame(aggregate).to_string(index=False), flush=True)
    print(pd.DataFrame(contrasts).to_string(index=False), flush=True)


if __name__ == '__main__': main()
