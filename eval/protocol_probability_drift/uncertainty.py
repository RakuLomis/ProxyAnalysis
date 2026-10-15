"""Shared business-stratified content-cluster draws; fixed-model intervals."""
import numpy as np
import pandas as pd
from common import OUT, read, write, PROTOCOLS, SEED, checkpoint


def draws():
    p = OUT / 'comparisons/bootstrap-indices.npy'
    folds = pd.read_parquet(OUT / 'cohorts/folds.parquet').sort_values('content_id').reset_index(drop=True)
    if p.exists():
        return folds, np.load(p)
    rng = np.random.default_rng(SEED)
    index = np.empty((10000, len(folds)), dtype=np.int16)
    offset = 0
    for _, block in folds.groupby('label_id', sort=True):
        ids = block.index.to_numpy()
        index[:,offset:offset+len(ids)] = rng.choice(ids, size=(10000,len(ids)), replace=True)
        offset += len(ids)
    p.parent.mkdir(parents=True, exist_ok=True)
    np.save(p, index)
    write(OUT / 'comparisons/bootstrap-manifest.json', {'seed':SEED,'samples':10000,
          'contents':folds.content_id.tolist(),'strata':folds.label_id.tolist(),
          'same_draws_all_protocols_and_arms':True,'fixed_model_only':True,
          'includes_refitting_uncertainty':False,'primary_family_size':8})
    return folds, index


def run():
    folds, index = draws()
    composite = pd.read_parquet(OUT / 'scores/content-composite-scores.parquet')
    rows = []
    for variant, frame in composite.groupby('variant'):
        for protocol, group in frame.groupby('protocol'):
            pivot = group.pivot(index='content_id', columns='arm', values='CE_bits').reindex(folds.content_id)
            if pivot.isna().any().any():
                raise RuntimeError('Incomplete content support; do not silently remove bootstrap clusters')
            comparisons = [('M0','M1'),('M2','M1')] if 'M0' in pivot else [('M2','M1')]
            for left, right in comparisons:
                delta = (pivot[left]-pivot[right]).to_numpy()
                weights = group.groupby('content_id').evaluation_mass.first().reindex(folds.content_id).to_numpy()
                boot = (delta[index]*weights[index]).sum(1)/weights[index].sum(1)
                q = np.quantile(boot, [.025,.975,.05/16,1-.05/16])
                rows.append({'variant':variant,'protocol':protocol,'contrast':left+'-'+right,
                             'gain_bits':float(np.average(delta,weights=weights)),'low95':q[0],'high95':q[1],
                             'family_low':q[2] if variant=='primary' else np.nan,
                             'family_high':q[3] if variant=='primary' else np.nan,
                             'family_positive':bool(q[2]>0) if variant=='primary' else False,
                             'exploratory':variant!='primary','contents':len(delta)})
    pd.DataFrame(rows).to_parquet(OUT / 'comparisons/composite-contrasts.parquet', index=False)
    feature = pd.read_parquet(OUT / 'scores/content-feature-scores.parquet')
    rows=[]
    for (variant,protocol,f), group in feature.groupby(['variant','protocol','feature']):
        pivot=group.pivot(index='content_id',columns='arm',values='CE_bits').reindex(folds.content_id)
        for left,right in ([('M0','M1'),('M2','M1')] if 'M0' in pivot else [('M2','M1')]):
            delta=(pivot[left]-pivot[right]).to_numpy()
            weights=group.groupby('content_id').evaluation_mass.first().reindex(folds.content_id).to_numpy()
            boot=(delta[index]*weights[index]).sum(1)/weights[index].sum(1)
            q=np.quantile(boot,[.025,.975])
            rows.append({'variant':variant,'protocol':protocol,'feature':f,'contrast':left+'-'+right,
                         'gain_bits':float(np.average(delta,weights=weights)),'low95':q[0],'high95':q[1],
                         'exploratory':True})
    pd.DataFrame(rows).to_parquet(OUT / 'comparisons/feature-contrasts.parquet', index=False)
    checkpoint('Q18_prediction_uncertainty_complete', {'primary_comparisons':8})


if __name__=='__main__':
    run()
