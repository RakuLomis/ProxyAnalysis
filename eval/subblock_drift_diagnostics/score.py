"""P3: scorer-only exact matching; all five predictors share actual C targets."""
from .common import *
from .basis import all_bases, energies, validate_hist
from .prepare import score_post
from .replay import chunk_path


def error_frames(values, truth, scale, route, bases, names, kind):
    diff = values-truth
    en = energies(diff, bases)
    results = []
    for j, n in enumerate(SIZES):
        pred = values[..., sl(j)]
        rawsum = diff[..., sl(j)].square().sum(-1)
        closure = en[..., j, 0]+en[..., j, 1]+(n-2)*en[..., j, 2]
        need(error(rawsum, closure) <= TOL, 'Raw error decomposition failure')
        std = (diff[..., sl(j)]/scale[sl(j)]).square().mean(-1)
        stats = [cpu(en[..., j, :]), cpu(rawsum), cpu(std), cpu(pred.sum(-1)-1),
                 cpu((pred < 0).sum(-1)), cpu(pred.min(-1).values)]
        for k, name in enumerate(names):
            d = route.copy()
            d['block'] = j; d['feature'] = FEATURES[j]; d['bins'] = n
            if kind == 'predictor':
                d['predictor'] = name
            else:
                d['arm'], d['view'] = name
            for pos, s in enumerate(['M', 'L', 'R']):
                d['E_'+s] = stats[0][k, :, pos]
            d['raw_sum'] = stats[1][k]; d['raw_mse'] = stats[1][k]/n
            d['std_mse'] = stats[2][k]; d['mass_residual'] = stats[3][k]
            d['negative_bins'] = stats[4][k]; d['min_bin'] = stats[5][k]
            results.append(d)
    return results


def run():
    with stage('P3'):
        need(read(OUT/'stages/P2.json')['complete'], 'P2 not finished')
        seal = verify_prediction_seal()
        for p, h in seal['files'].items():
            need(sha(ROOT/p) == h, 'Frozen predictions changed before scoring')
        bindings = pd.read_parquet(OUT/'source-bindings.parquet')
        basis = all_bases()
        stable, err, protect, fluxes = [], [], [], []
        labels = {}; checks = []; routing_all = []
        for ri, role in enumerate(contract()['roles']):
            meta = package(ROOT/role['metadata_ref'], role, 'C-business-metadata')
            for row in meta.drop_duplicates(['content_id', 'label_id']).itertuples():
                ct = token(row.content_id); label = str(row.label_id)
                need(ct not in labels or labels[ct]['label_id'] == label, 'Inconsistent content business label')
                labels[ct] = {'content_token': ct, 'content_id': row.content_id, 'label_id': label}
            for inner in range(4):
                binding = bindings[(bindings.role_id == role['id']) & (bindings.inner == inner) & bindings.arm.eq('P')].iloc[0]
                path = chunk_path(role, inner)
                payload = own_obj(path)
                route = pd.read_parquet(path.parent/'routing.parquet')
                need(set(route.content_token) <= {token(u) for u in role['C_diagnostic_contents'][inner]}, 'Routing scope')
                post = score_post(role, ROOT/binding.P_score_ref, route)
                a = payload['a']; scale = payload['scale']; routing_all.append(route)
                with compute(role['id']+f'/i{inner}-score'):
                    validate_hist(post)
                    delta = post-a
                    drift_en = energies(delta, basis)
                    for j, n in enumerate(SIZES):
                        b = basis[n]; dx = delta[:, sl(j)]
                        d = route.copy(); d['block'] = j; d['feature'] = FEATURES[j]; d['bins'] = n
                        e = cpu(drift_en[:, j]); d['D_M'] = e[:, 0]; d['D_L'] = e[:, 1]; d['D_R'] = e[:, 2]
                        for s, pos in [('M', 0), ('L', 1), ('R', 2)]:
                            for source, prefix in [('V_pre', 'V_pre'), ('V_post', 'V_post'), ('V_min', 'V'),
                                                   ('repeat_pre', 'repeat_pre'), ('repeat_post', 'repeat_post')]:
                                d[prefix+'_'+s] = float(payload[source][j, pos])
                        d['delta_M'] = cpu(dx@b['u0']); d['delta_L'] = cpu(dx@b['u1'])
                        d['delta_R'] = list(cpu(dx@b['PR']))
                        d['delta_midx'] = cpu(dx@b['c'])
                        d['pre_midx'] = cpu(a[:, sl(j)]@b['c']); d['post_midx'] = cpu(post[:, sl(j)]@b['c'])
                        stable.append(d)
                        f = prefix_sum(dx)
                        rhs = b['c'][-1]*f[:, -1]-(torch.diff(b['c'])*f[:, :-1]).sum(-1)
                        ferr = error(dx@b['c'], rhs)
                        need(ferr <= TOL, 'General flux identity')
                        zerr = float(((dx@b['c'])+(torch.diff(b['c'])*f[:, :-1]).sum(-1)).abs().max())
                        need(zerr <= TOL, 'Closed-mass flux identity')
                        fd = route.copy(); fd['block'] = j
                        fd['net_flux'] = list(cpu(f[:, :-1])); fd['end_mass_residual'] = cpu(f[:, -1])
                        fd['delta_midx'] = cpu(dx@b['c']); fluxes.append(fd)
                    err.extend(error_frames(payload['predictions'], post, scale, route, basis, PREDICTORS, 'predictor'))
                    vv = payload['views'].reshape(8, 16, 96)
                    names = [(arm, name) for arm in ['P', 'G'] for name in VIEWS]
                    protect.extend(error_frames(vv, post, scale, route, basis, names, 'view'))
                    # Exact raw LOC improvement identity; no analogous standardized assertion.
                    ve = energies(payload['views']-post, basis)
                    for k, arm in enumerate(['P', 'G']):
                        base = payload['views'][k, 0]; loc = payload['views'][k, 2]
                        for j, n in enumerate(SIZES):
                            gain = (base[:, sl(j)]-post[:, sl(j)]).square().sum(-1)-(loc[:, sl(j)]-post[:, sl(j)]).square().sum(-1)
                            expected = ve[k, 0, :, j, 1]-ve[k, 2, :, j, 1]
                            need(error(gain, expected) <= TOL, 'LOC raw improvement identity')
                            need(error(ve[k, 0, :, j, 0], ve[k, 2, :, j, 0]) <= TOL, 'LOC changed M')
                            need(error(ve[k, 0, :, j, 2], ve[k, 2, :, j, 2]) <= TOL, 'LOC changed R')
                    checks.append({'role_id': role['id'], 'inner': inner, 'passed': True,
                                   'flux_normalized_error': ferr, 'flux_zero_boundary_error': zerr})
            if (ri+1) % 10 == 0:
                progress('P3_scored', roles=ri+1, total=60)
        lab = pd.DataFrame(labels.values()).sort_values(['label_id', 'content_token']).reset_index(drop=True)
        need(len(lab) == 30 and lab.groupby('label_id').size().eq(5).all() and len(lab.label_id.unique()) == 6, 'Bootstrap content strata mismatch')
        write(OUT/'stratification-seal.json', {'contract_sha256': sha(OUT/'contract.json'),
                                             'content_strata': lab.to_dict('records'), 'labels_prediction_worker_visible': False})
        save(lab, 'content-strata')
        tables = [('stability-ledger', stable, 38400), ('prediction-error-ledger', err, 192000),
                  ('protection-effect-ledger', protect, 307200), ('net-bin-flux', fluxes, 38400)]
        for name, frames, count in tables:
            d = pd.concat(frames, ignore_index=True)
            need(len(d) == count, 'Unexpected ledger size: '+name)
            num = d.select_dtypes(include=[np.number])
            need(np.isfinite(num.to_numpy()).all(), 'Nonfinite elementary score')
            save(d, name)
        routes = pd.concat(routing_all, ignore_index=True)
        save(routes.groupby(['deployment', 'query_key', 'content_token']).size().rename('role_exposures').reset_index(), 'physical-query-exposures')
        unique = routes[['deployment', 'query_key', 'content_token']].drop_duplicates()
        need(len(unique) == 480 and unique.content_token.nunique() == 30, 'Unique cohort coverage')
        save(pd.DataFrame(checks), 'score-numeric-checks')
        write(OUT/'score-complete.json', {'pairs': 3840, 'distinct_visits': 480, 'contents': 30,
                                         'score_matching': 'same real pair for ID/MEAN/SHIFT/P/G',
                                         'stratification_sha256': sha(OUT/'stratification-seal.json'),
                                         'files': {rel(OUT/(name+'.parquet')): sha(OUT/(name+'.parquet')) for name, _, _ in tables}})
