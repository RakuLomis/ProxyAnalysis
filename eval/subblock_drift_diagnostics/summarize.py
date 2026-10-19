"""P4: original query masses, frozen-scale ratios and shared content bootstrap."""
from .common import *


def derive(frame):
    d = frame.copy()
    for s in ['L', 'R']:
        d['rho_'+s] = np.divide(d['D_'+s], d['V_'+s],
                                 out=np.full(len(d), np.nan), where=d['V_'+s].to_numpy() > SCALE_MIN)
        d['noninformative_'+s] = d['V_'+s] <= SCALE_MIN
    d['stable_margin'] = 1-d.rho_L
    d['rho_gap'] = d.rho_R-d.rho_L
    for ref in ['ID', 'MEAN', 'SHIFT', 'G']:
        d[ref+'_R_gain'] = d[ref+'_E_R']-d.P_E_R
        d[ref+'_R_skill'] = 1-np.divide(d.P_E_R, d[ref+'_E_R'],
                              out=np.full(len(d), np.nan), where=d[ref+'_E_R'].to_numpy() > SCALE_MIN)
    d['P_loc_raw_gain'] = d.P_BASE_raw_sum-d.P_LOC_raw_sum
    d['P_loc_std_gain'] = d.P_BASE_std_mse-d.P_LOC_std_mse
    d['G_loc_raw_gain'] = d.G_BASE_raw_sum-d.G_LOC_raw_sum
    d['G_loc_std_gain'] = d.G_BASE_std_mse-d.G_LOC_std_mse
    d['G_L_P'] = d.P_E_L-d.ID_E_L
    d['S'] = (~d.noninformative_L & ~d.noninformative_R
              & (d.stable_margin > TOL*np.maximum(1, np.abs(d.rho_L)))
              & (d.rho_gap > TOL*np.maximum.reduce([np.ones(len(d)), abs(d.rho_L), abs(d.rho_R)])))
    d['N'] = ((d.P_loc_raw_gain > TOL*np.maximum.reduce([np.ones(len(d)), abs(d.P_BASE_raw_sum), abs(d.P_LOC_raw_sum)]))
              & (d.P_loc_std_gain >= -TOL*np.maximum.reduce([np.ones(len(d)), abs(d.P_BASE_std_mse), abs(d.P_LOC_std_mse)])))
    d['D'] = True
    for ref in ['ID', 'MEAN', 'SHIFT', 'G']:
        d['D'] &= d[ref+'_R_gain'] > TOL*np.maximum.reduce([np.ones(len(d)), abs(d[ref+'_E_R']), abs(d.P_E_R)])
    d['SND'] = d.S & d.N & d.D
    return d


def build_core():
    stable = pd.read_parquet(OUT/'stability-ledger.parquet')
    errors = pd.read_parquet(OUT/'prediction-error-ledger.parquet')
    protect = pd.read_parquet(OUT/'protection-effect-ledger.parquet')
    key = [*META, 'block']
    ep = errors.pivot(index=key, columns='predictor', values=['E_M', 'E_L', 'E_R', 'raw_sum', 'std_mse'])
    ep.columns = [p+'_'+m for m, p in ep.columns]
    vp = protect.pivot(index=key, columns=['arm', 'view'], values=['raw_sum', 'std_mse'])
    vp.columns = [a+'_'+v+'_'+m for m, a, v in vp.columns]
    d = stable.merge(ep.reset_index(), on=key, validate='one_to_one').merge(vp.reset_index(), on=key, validate='one_to_one')
    need(len(d) == 38400, 'Core score membership')
    # Elementary identity verifies both independent predictor/view paths.
    need(float(abs((d.P_BASE_raw_sum-d.P_LOC_raw_sum)-(d.P_E_L-d.ID_E_L)).max()) <= TOL, 'Core LOC identity')
    columns = [c for c in d if c.startswith(('D_', 'V_', 'repeat_')) and c not in {'delta_R'}]
    columns += list(ep.columns)+list(vp.columns)
    columns = list(dict.fromkeys(columns))
    d['original_weight'] = 1/960
    return d, columns


def grouped(d, keys, columns, include_drift=True):
    out = d.groupby(keys, sort=True)[columns].mean().reset_index()
    count = d.groupby(keys, sort=True).size().rename('query_exposures').reset_index()
    out = out.merge(count, on=keys, validate='one_to_one')
    if include_drift:
        rows = []
        for name, g in d.groupby(keys, sort=True):
            name = name if isinstance(name, tuple) else (name,)
            row = dict(zip(keys, name)); n = int(g.bins.iloc[0])
            row['feature'] = g.feature.iloc[0]; row['bins'] = n
            row['centroid_signed_mean'] = g.delta_midx.mean()
            row['centroid_rms'] = np.sqrt(np.mean(g.delta_midx.to_numpy()**2))
            for q in [.1, .5, .9]:
                row['centroid_q'+str(int(q*100))] = np.quantile(g.delta_midx, q, method='linear')
            row['centroid_abs_q90'] = np.quantile(abs(g.delta_midx), .9, method='linear')
            for s in ['M', 'L', 'R']:
                bias = (float(g['delta_'+s].mean())**2 if s != 'R'
                        else float(np.square(np.stack(g.delta_R).mean(0)).sum())/(n-2))
                row['bias_energy_'+s] = bias
                row['fluctuation_energy_'+s] = float(g['D_'+s].mean())-bias
                row['small_scale_query_fraction_'+s] = float((g['V_'+s] <= SCALE_MIN).mean())
            rows.append(row)
        out = out.merge(pd.DataFrame(rows), on=keys, validate='one_to_one')
    return derive(out)


def bootstrap(d, columns, labels):
    tokens = labels.content_token.tolist()
    lookup = {u: i for i, u in enumerate(tokens)}
    rng = np.random.default_rng(20261015)
    draws = np.zeros((10000, 30), dtype=np.int16)
    for _, g in labels.groupby('label_id', sort=True):
        ix = np.array([lookup[u] for u in g.content_token])
        draws[:, ix] = rng.multinomial(5, np.full(5, .2), size=10000)
    need(np.all(draws.sum(1) == 30), 'Bootstrap total cluster mass')
    np.savez_compressed(target(OUT/'bootstrap-draws.npz'), multiplicities=draws, content_tokens=np.asarray(tokens))
    results = []
    for (deployment, block), g in d.groupby(['deployment', 'block'], sort=True):
        # All original row weights survive; no within-fold rebalancing.
        masses = g.groupby('content_token').original_weight.sum().reindex(tokens, fill_value=0).to_numpy()
        sums = g[columns].mul(g.original_weight, axis=0).groupby(g.content_token).sum().reindex(tokens, fill_value=0).to_numpy()
        denominator = draws@masses
        need(np.all(denominator > 0), 'Bootstrap empty deployment')
        values = (draws@sums)/denominator[:, None]
        reps = derive(pd.DataFrame(values, columns=columns))
        point = derive(pd.DataFrame([g[columns].mean().to_dict()])).iloc[0]
        metrics = [c for c in reps if pd.api.types.is_numeric_dtype(reps[c]) and not pd.api.types.is_bool_dtype(reps[c])]
        for metric in metrics:
            v = reps[metric].to_numpy(dtype=float)
            finite = np.isfinite(v)
            q = np.quantile(v[finite], [.025, .975]) if finite.any() else [np.nan, np.nan]
            results.append({'deployment': deployment, 'block': int(block), 'metric': metric,
                            'estimate': float(point[metric]), 'lower': q[0], 'upper': q[1],
                            'valid_replicates': int(finite.sum()), 'NA_fraction': float(1-finite.mean()),
                            'confidence_level': .95, 'family_corrected': False})
    return pd.DataFrame(results)


def screen(deployment_table, outer, by_content, intervals):
    rows = []
    required = ['stable_margin', 'rho_gap', 'P_loc_raw_gain', 'P_loc_std_gain',
                'ID_R_gain', 'MEAN_R_gain', 'SHIFT_R_gain', 'G_R_gain']
    for item in deployment_table.itertuples():
        dep, block = item.deployment, int(item.block)
        folds = outer[(outer.deployment == dep) & (outer.block == block)]
        cont = by_content[(by_content.deployment == dep) & (by_content.block == block)]
        ci = intervals[(intervals.deployment == dep) & (intervals.block == block)].set_index('metric')
        counts = {}; fractions = {}
        for metric in ['P_loc_raw_gain', 'G_R_gain']:
            vals = cont[metric].to_numpy()*cont.query_exposures.to_numpy()/960
            positive = cont[metric].to_numpy() > TOL
            counts[metric] = int(positive.sum())
            fractions[metric] = float(vals[positive].max()/vals[positive].sum()) if positive.any() else None
        unresolved = any(ci.loc[m, 'NA_fraction'] > 0 or not np.isfinite(ci.loc[m, 'lower'])
                         or ci.loc[m, 'lower'] <= 0 <= ci.loc[m, 'upper'] for m in required)
        fold_count = int(folds.SND.sum())
        candidate = bool(item.SND and fold_count >= 4 and all(v >= 2 for v in counts.values()))
        reasons = []
        if not item.S: reasons.append('no_nontrivial_position_stability')
        if not item.N: reasons.append('no_position_protection_need_or_std_tradeoff')
        if not item.D: reasons.append('shape_prediction_not_better_than_all_fixed_references')
        if fold_count < 4: reasons.append('outer_fold_consistency_below_4_of_5')
        if any(v < 2 for v in counts.values()): reasons.append('fewer_than_two_positive_content_contributions')
        rows.append({'deployment': dep, 'block': block, 'feature': FEATURES[block],
                     'S': bool(item.S), 'N': bool(item.N), 'D': bool(item.D),
                     'SND_outer_folds': fold_count, 'positive_contents': counts,
                     'max_positive_content_fraction': fractions,
                     'discussion_candidate': candidate, 'uncertainty_unresolved': bool(unresolved),
                     'reasons': reasons, 'deployable_protection': False})
    return rows


def run():
    with stage('P4'):
        need(read(OUT/'stages/P3.json')['complete'], 'Scoring not complete')
        with compute('all-aggregates-and-10000-content-bootstrap'):
            core, columns = build_core()
            role_fold = grouped(core, ['deployment', 'role_id', 'outer', 'group', 'inner', 'block'], columns)
            role = grouped(core, ['deployment', 'role_id', 'outer', 'group', 'block'], columns)
            outer = grouped(core, ['deployment', 'outer', 'block'], columns)
            dep = grouped(core, ['deployment', 'block'], columns)
            content = grouped(core, ['deployment', 'content_token', 'block'], columns)
            need(len(role_fold) == 2400 and len(role) == 600 and len(outer) == 200 and len(dep) == 40, 'Aggregation grid')
            lab = pd.read_parquet(OUT/'content-strata.parquet')
            need(sha(OUT/'stratification-seal.json') == read(OUT/'score-complete.json')['stratification_sha256'], 'Strata seal changed')
            need(lab.to_dict('records') == read(OUT/'stratification-seal.json')['content_strata'], 'Stratum rows changed')
            cis = bootstrap(core, columns, lab)
            flags = screen(dep, outer, content, cis)
            # Full-vector errors use dimension weights, not a ten-block mean.
            keys = [*META, 'arm', 'view']
            protection = pd.read_parquet(OUT/'protection-effect-ledger.parquet')
            protection['std_weighted'] = protection.std_mse*protection.bins/96
            whole = protection.groupby(keys, sort=True).agg(raw_sum=('raw_sum', 'sum'),
                                  std_mse=('std_weighted', 'sum')).reset_index()
            whole['raw_mse'] = whole.raw_sum/96
            whole_dep = whole.groupby(['deployment', 'arm', 'view'])[['raw_mse', 'std_mse']].mean().reset_index()
            quality = protection.groupby(['deployment', 'arm', 'view', 'block'], sort=True).agg(
                negative_bin_count=('negative_bins', 'sum'),
                negative_prediction_fraction=('negative_bins', lambda x: float((x > 0).mean())),
                minimum_predicted_bin=('min_bin', 'min'),
                mean_mass_residual=('mass_residual', 'mean'),
                mean_absolute_mass_residual=('mass_residual', lambda x: float(abs(x).mean())),
                max_absolute_mass_residual=('mass_residual', lambda x: float(abs(x).max()))).reset_index()
        for name, d in [('evaluation-core', core), ('by-role-fold-block', role_fold), ('by-role-block', role),
                        ('by-outer-fold-block', outer), ('by-deployment-block', dep), ('by-content', content),
                        ('bootstrap-descriptive', cis), ('full-vector-errors', whole),
                        ('full-vector-by-deployment', whole_dep), ('prediction-quality', quality)]:
            save(d, name)
        write(OUT/'screening-flags.json', {'units': flags, 'candidate_count': sum(x['discussion_candidate'] for x in flags),
                                         'uncertainty_unresolved': any(x['uncertainty_unresolved'] for x in flags),
                                         'authorize_new_G_training': False, 'authorize_business_training': False,
                                         'authorize_actual_H_U_read': False, 'old_guard_status_changed': False})
        write(OUT/'summary-complete.json', {'units': 40, 'bootstrap_replicates': 10000,
                                           'summary_estimates': 240, 'family_corrected': False,
                                           'fixed_query_weight_per_deployment': 1/960,
                                           'source_sha256': sha(OUT/'evaluation-core.parquet'),
                                           'files': {rel(OUT/(name+'.parquet')): sha(OUT/(name+'.parquet'))
                                                     for name in ['by-role-fold-block', 'by-role-block', 'by-outer-fold-block',
                                                                  'by-deployment-block', 'by-content', 'bootstrap-descriptive',
                                                                  'full-vector-errors', 'full-vector-by-deployment', 'prediction-quality']}})
        progress('P4_summary_complete', units=40, discussion_candidates=sum(x['discussion_candidate'] for x in flags))
