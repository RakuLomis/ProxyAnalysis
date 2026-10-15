"""Separate scorer: shared content-cluster bootstrap conditional on fixed models."""
from common import *


def f1(cm):
    d = np.diagonal(cm, axis1=-2, axis2=-1)
    denominator = cm.sum(-2)+cm.sum(-1)
    return np.divide(2*d, denominator, out=np.zeros_like(d, dtype=float), where=denominator > 0).mean(-1)


def draws(cohort, classes):
    contents = sorted(cohort.content_id.unique()); groups = []
    for y in classes:
        cc = sorted(cohort.loc[cohort.label_id.eq(y), 'content_id'].unique()); assert len(cc) == 5
        groups.append([contents.index(v) for v in cc])
    rng = np.random.default_rng(20260928)
    indices = np.concatenate([rng.choice(g, size=(10000, 5), replace=True) for g in groups], axis=1)
    weights = np.eye(30, dtype=np.int16)[indices].sum(1)
    return contents, indices, weights


def main():
    cli(__doc__).parse_args(); authorize()
    assert read(OUT/'prediction-seal.json')['oof_sha256'] == sha(OUT/'oof.parquet')
    cohort = pd.read_parquet(OUT/'cohort.parquet'); contract = read(OUT/'contract.json'); classes = contract['classes']
    labels = pd.concat([Bundle(f, 'scoring').get('labels') for f in range(5)], ignore_index=True)
    assert labels.session_id.is_unique and set(labels.session_id) == set(cohort.session_id)
    assert labels.set_index('session_id').label_id.to_dict() == cohort.set_index('session_id').label_id.to_dict()
    pred = pd.read_parquet(OUT/'oof.parquet').merge(cohort, on=['session_id', 'fold'], validate='many_to_one')
    prob = pred[[f'p{k}' for k in range(6)]].to_numpy(float)
    assert np.isfinite(prob).all() and np.allclose(prob.sum(1), 1, atol=1e-5)
    pred['truth'] = pred.label_id.map({v: i for i, v in enumerate(classes)})
    pred['guess'] = prob.argmax(1); pred['correct'] = pred.truth.eq(pred.guess)
    pred['CE_bits'] = -np.log2(np.maximum(prob[np.arange(len(prob)), pred.truth.to_numpy()], 1e-15))
    pred['Brier'] = ((prob-np.eye(6)[pred.truth])**2).sum(1)
    pred.to_parquet(OUT/'scored-oof.parquet', index=False)
    contents, ix, weights = draws(cohort, classes); protocols = sorted(cohort.protocol.unique())
    metrics, perclass, aggregate, boot, point = [], [], [], {}, {}
    for (stage, arm, hk), g in pred.groupby(['stage', 'arm', 'head']):
        cm = np.zeros((3, 5, 30, 6, 6), dtype=np.int64)
        for row in g[['seed', 'protocol', 'content_id', 'truth', 'guess']].itertuples(index=False):
            cm[SEEDS.index(row.seed), protocols.index(row.protocol), contents.index(row.content_id), row.truth, row.guess] += 1
        pooled = cm.sum(2)
        f = f1(pooled); protocol_equal = f.mean(1)
        key = stage+'|'+arm+'|'+hk
        boot[key] = f1(np.einsum('dc,spcij->dspij', weights, cm)).mean((1, 2))
        point[key] = protocol_equal.mean()
        for si, seed in enumerate(SEEDS):
            for pi, protocol in enumerate(protocols):
                sg = g[g.seed.eq(seed) & g.protocol.eq(protocol)]; conf = pooled[si, pi]
                metrics.append({'stage': stage, 'arm': arm, 'head': hk, 'seed': seed, 'protocol': protocol,
                                'F1': f[si, pi], 'accuracy': sg.correct.mean(),
                                'CE_bits': sg.CE_bits.mean(), 'Brier': sg.Brier.mean()})
                tp = conf.diagonal(); rown, coln = conf.sum(1), conf.sum(0)
                for k, label in enumerate(classes):
                    perclass.append({'stage': stage, 'arm': arm, 'head': hk, 'seed': seed, 'protocol': protocol,
                                     'class': label, 'precision': tp[k]/coln[k] if coln[k] else 0.,
                                     'recall': tp[k]/rown[k], 'F1': 2*tp[k]/(rown[k]+coln[k])})
        aggregate.append({'stage': stage, 'arm': arm, 'head': hk, 'F1': protocol_equal.mean(),
                          'min_seed': protocol_equal.min(), 'max_seed': protocol_equal.max(),
                          'worst_F1': f.min(1).mean(), 'CE_bits': g.CE_bits.mean(), 'Brier': g.Brier.mean()})
    contrasts, transitions = [], []
    final = pred[pred.stage.eq('finetune')]
    base = final[final.arm.eq('B5')]
    for ref in ['B0', 'B0L', 'B1', 'B2', 'B3', 'B4', 'B6']:
        diff = boot['finetune|B5|mlp']-boot[f'finetune|{ref}|mlp']
        adj = np.quantile(diff, [.005, .995]) if ref in PRIMARY else [None, None]
        lo, hi = np.quantile(diff, [.025, .975])
        contrasts.append({'contrast': 'B5-'+ref, 'primary': ref in PRIMARY,
                          'delta': point['finetune|B5|mlp']-point[f'finetune|{ref}|mlp'],
                          'low95': lo, 'high95': hi, 'adjusted_low': adj[0], 'adjusted_high': adj[1]})
        joined = base.merge(final[final.arm.eq(ref)][['seed', 'session_id', 'correct']],
                            on=['seed', 'session_id'], suffixes=('', '_reference'), validate='one_to_one')
        joined['reference'] = ref
        joined['repaired'] = joined.correct & ~joined.correct_reference
        joined['new_error'] = ~joined.correct & joined.correct_reference
        transitions.append(joined[['reference', 'seed', 'session_id', 'protocol', 'content_id', 'label_id', 'repaired', 'new_error']])
    pd.DataFrame(metrics).to_parquet(OUT/'per-protocol-seed-metrics.parquet', index=False)
    pd.DataFrame(perclass).to_parquet(OUT/'per-class-metrics.parquet', index=False)
    pd.DataFrame(aggregate).to_parquet(OUT/'aggregate-metrics.parquet', index=False)
    pd.DataFrame(contrasts).to_parquet(OUT/'primary-contrasts.parquet', index=False)
    pd.concat(transitions).to_parquet(OUT/'error-transitions.parquet', index=False)
    np.savez_compressed(OUT/'bootstrap.npz', content_indices=ix, **boot)
    write(OUT/'score-complete.json', {'passed': True, 'primary_family': 5, 'draws': 10000,
          'conditional_on_fixed_models': True, 'prediction_sha256': sha(OUT/'oof.parquet'),
          'selected_checkpoints': False, 'independent_visits': 600, 'independent_contents': 30})
    print(pd.DataFrame(aggregate).query("stage=='finetune'").to_string(index=False), flush=True)


if __name__ == '__main__': main()
