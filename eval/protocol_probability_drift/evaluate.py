"""Scoring process joins test post only after complete distributions are frozen."""
import numpy as np
import pandas as pd
import torch
from common import OUT, read, write, hash_file, relative, require, checkpoint, FAMILIES
from bins import encode
from kernels import tensor
from weights import mass


def run():
    contract = read(OUT / 'manifests/experiment-contract.json')
    read(OUT / 'manifests/prediction-ledger.json')
    all_content, all_native = [], []
    for role in contract['roles']:
        v, f, p = role['variant'], role['fold'], role['protocol']
        path = OUT / 'packages' / v / f'f{f}' / p / 'score-post.parquet'
        require(hash_file(path) == contract['packages_sha256'][relative(path)], 'Score package changed')
        score = pd.read_parquet(path)
        score['score_mass'] = mass(score, 'flow_equal' if v == 'flow_equal' else 'hierarchical')
        pred = pd.read_parquet(OUT / 'oof' / v / f'f{f}-{p}.parquet')
        scored = []
        for feature in role['features']:
            z = pred[pred.feature.eq(feature)].merge(score[['pair_id','content_id','label_id','score_mass','post_'+feature]],
                                                    on='pair_id', validate='many_to_one')
            b = encode(z['post_' + feature], feature, merged=v == 'merged')
            probs = tensor(z[[c for c in z if c.startswith('q') and c[1:].isdigit()]].to_numpy())
            row = torch.arange(len(z), device=probs.device)
            probability = probs[row, tensor(b, True)]
            require(bool((probability > 0).all()), 'Nonpositive predicted probability')
            z['B'], z['CE_bits'] = b, (-torch.log2(probability)).cpu().numpy()
            z['native_target'] = z['post_' + feature]
            z['fallback_row'] = z.row_mass.eq(0)
            scored.append(z.drop(columns=[c for c in z if c.startswith('q') and c[1:].isdigit()]))
        z = pd.concat(scored, ignore_index=True)
        dest = OUT / 'scores' / v / f'f{f}-{p}.parquet'
        dest.parent.mkdir(parents=True, exist_ok=True)
        z.to_parquet(dest, index=False)
        keys = ['variant','protocol','content_id','label_id','feature','arm']
        z['weighted_CE'] = z.CE_bits * z.score_mass
        z['weighted_fallback'] = z.fallback_row * z.score_mass
        grouped = z.groupby(keys, observed=True).agg(total=('score_mass','sum'), loss=('weighted_CE','sum'),
                                                    fallback=('weighted_fallback','sum'))
        grouped['CE_bits'], grouped['fallback_rate'] = grouped.loss/grouped.total, grouped.fallback/grouped.total
        grouped['evaluation_mass'] = grouped.total
        all_content.append(grouped.reset_index())
        if 'median' in z:
            target = z.native_target.to_numpy()
            delta = z['median'].to_numpy() - target
            z['MAE'], z['MSE'], z['bias'] = abs(delta), delta*delta, delta
            z['coverage80'] = (target>=z.p10)&(target<=z.p90)
            z['coverage90'] = (target>=z.p05)&(target<=z.p95)
            z['width80'], z['width90'] = z.p90-z.p10, z.p95-z.p05
            for metric in ['MAE','MSE','bias','coverage80','coverage90','width80','width90']:
                z[metric] = z[metric] * z.score_mass
            t = z.groupby(keys, observed=True)[['MAE','MSE','bias','coverage80','coverage90','width80','width90']].sum()
            totals = z.groupby(keys, observed=True).score_mass.sum()
            t = t.div(totals, axis=0)
            t['evaluation_mass'] = totals
            t = t.reset_index()
            all_native.append(t)
    content = pd.concat(all_content, ignore_index=True)
    family_map = {feature: family for family, fs in FAMILIES.items() for feature in fs}
    family_map.update({'R_window_up':'interaction','R_window_down':'interaction'})
    content['family'] = content.feature.map(family_map)
    content.to_parquet(OUT / 'scores/content-feature-scores.parquet', index=False)
    family = content.groupby(['variant','protocol','content_id','label_id','arm','family'], observed=True).agg(
        CE_bits=('CE_bits','mean'),evaluation_mass=('evaluation_mass','first')).reset_index()
    family.to_parquet(OUT / 'scores/content-family-scores.parquet', index=False)
    composite = family.groupby(['variant','protocol','content_id','label_id','arm'], observed=True).agg(
        CE_bits=('CE_bits','mean'),evaluation_mass=('evaluation_mass','first')).reset_index()
    composite.to_parquet(OUT / 'scores/content-composite-scores.parquet', index=False)
    if all_native:
        pd.concat(all_native, ignore_index=True).to_parquet(OUT / 'scores/content-native-scores.parquet', index=False)
    write(OUT / 'scores/score-complete.json', {'content_feature_rows': len(content),
          'test_post_only_in_scoring': True, 'composite_not_joint_likelihood': True})
    checkpoint('Q16_scored', {'content_feature_rows': len(content)})


if __name__ == '__main__':
    run()
