"""P2: all frozen-map forecasts and deterministic views precede score unlock."""
from .common import *
from .basis import all_bases, validate_hist
from .prepare import common_query, anonymous_fit
from .marginal_references import summarize_marginals
from .counterfactuals import make_views


def predict(query_pre_values, frozen_map, frozen_scale):
    need(set(frozen_map) == {'matrix', 'bias'}, 'Frozen map schema')
    mu, sd = frozen_scale['mu'], frozen_scale['scale']
    need(mu.shape == sd.shape == (96,) and torch.isfinite(sd).all() and (sd > 0).all(), 'Frozen scaler')
    z = (query_pre_values-mu)/sd
    output = (z@frozen_map['matrix'].T+frozen_map['bias'])*sd+mu
    need(torch.isfinite(output).all(), 'Nonfinite frozen forward')
    return output


def chunk_path(role, inner):
    return OUT/'chunks'/role['id']/f'i{inner}'/'forecast.pt'


def frame(values, route, predictor=None, arm=None, view=None):
    d = route.copy()
    if predictor is not None: d['predictor'] = predictor
    if arm is not None: d['arm'] = arm
    if view is not None: d['view'] = view
    return pd.concat([d.reset_index(drop=True), pd.DataFrame(cpu(values), columns=HIST)], axis=1)


def run():
    with stage('P2'):
        need(read(OUT/'stages/P1.json')['complete'], 'Synthetic checks required')
        bindings = pd.read_parquet(OUT/'source-bindings.parquet')
        need(sha(OUT/'source-bindings.parquet') == read(OUT/'stages/P0.json')['binding_sha256'], 'Bindings changed')
        bases = all_bases()
        summary_rows, replay_rows, predictions, views, files = [], [], [], [], {}
        for ri, role in enumerate(contract()['roles']):
            for inner in range(4):
                bs = bindings[(bindings.role_id == role['id']) & (bindings.inner == inner)]
                need(len(bs) == 2 and set(bs.arm) == {'P', 'G'}, 'Map binding pair')
                p = bs[bs.arm.eq('P')].iloc[0]
                g = bs[bs.arm.eq('G')].iloc[0]
                a, route = common_query(role, ROOT/p.P_query_ref)
                route['role_id'] = role['id']; route['deployment'] = role['target']
                route['outer'] = role['outer']; route['group'] = role['group']; route['inner'] = inner
                route = route[META]
                path = chunk_path(role, inner)
                if path.exists():
                    payload = own_obj(path)
                    need(error(payload['a'], a) < 1e-12, 'Resumed query differs')
                    logs = read(path.parent/'replay-checks.json')
                else:
                    coord = obj(ROOT/p.scale_ref, role, 'scale')
                    need(p.scale_ref == g.scale_ref, 'P/G coordinate mismatch')
                    ap, ga = anonymous_fit(role, ROOT/p.G_pre_fit_ref)
                    bp, gb = anonymous_fit(role, ROOT/p.G_post_fit_ref)
                    # Trusted numeric multiset audit only; never expose matched visit IDs to G.
                    paired = package(ROOT/p.P_fit_ref, role, 'paired-fit-verification')
                    gq = package(ROOT/g.G_pre_validation_ref, role, 'old-G-query-fixture')
                    maps, fixtures = {}, {}
                    for arm, binding in [('P', p), ('G', g)]:
                        maps[arm] = obj(ROOT/binding.map_ref, role, 'map')
                        fixtures[arm] = obj(ROOT/binding.old_forecast_ref, role, 'old-forecast')
                    with compute(role['id']+f'/i{inner}-replay'):
                        validate_hist(a)
                        validate_hist(ap); validate_hist(bp)
                        for side, gd in [('pre', (ap, ga)), ('post', (bp, gb))]:
                            pv = paired[['%s_%s' % (side, h) for h in HIST]].to_numpy()
                            values, groups = gd
                            for u in sorted(set(groups)):
                                # Sort each side only, for multiset equality, never infer cross-side pairs.
                                x = pv[paired.content_token.to_numpy() == u]
                                y = cpu(values[np.flatnonzero(groups == u)])
                                x = x[np.lexsort(x.T[::-1])]; y = y[np.lexsort(y.T[::-1])]
                                need(float(np.max(np.abs(x-y))) <= 1e-14, 'P/G marginal multiset mismatch')
                        summary = summarize_marginals(ap, ga, bp, gb, bases)
                        ma = summary['mean_pre']; mb = summary['mean_post']
                        outputs = [a.clone(), mb.expand_as(a).clone(), a+mb-ma]
                        logs = []
                        for arm, binding in [('P', p), ('G', g)]:
                            q = a if arm == 'P' else t(gq[HIST].to_numpy())
                            fixture = fixtures[arm]
                            keys = route.query_key.tolist() if arm == 'P' else gq.query_key.tolist()
                            need(fixture['query_keys'] == keys, 'Original forecast input order changed')
                            need(error(q, fixture['a']) < 1e-12, 'Original query replay failed')
                            need(torch.equal(fixture['scale'], coord['scale']), 'Legacy forecast scale mismatch')
                            old_forward = predict(q, maps[arm], coord)
                            abs_err = float((old_forward-fixture['b0']).abs().max())
                            need(abs_err < 1e-12, 'Original raw forward replay failed')
                            outputs.append(predict(a, maps[arm], coord))
                            logs.append({'role_id': role['id'], 'inner': inner, 'arm': arm,
                                         'raw_max_abs_replay_error': abs_err, 'accepted': True,
                                         'old_policy_raw_replay_tolerance': 1e-12,
                                         'common_query_rows': 16, 'extra_fixture_forward_rows': 16,
                                         'map_sha256': contract()['files'][binding.map_ref]['sha256'],
                                         'scale_sha256': contract()['files'][binding.scale_ref]['sha256']})
                        outputs = torch.stack(outputs)
                        view_values = torch.stack([make_views(a, outputs[k], bases) for k in [3, 4]])
                        payload = {'a': a, 'scale': coord['scale'], 'predictions': outputs,
                                   'views': view_values, **summary}
                    put(path, payload)
                    write(path.parent/'replay-checks.json', logs)
                    save(route, str(path.parent.relative_to(OUT)/'routing'))
                replay_rows.extend(logs)
                for j, n in enumerate(SIZES):
                    for s, pos in [('M', 0), ('L', 1), ('R', 2)]:
                        summary_rows.append({'role_id': role['id'], 'deployment': role['target'],
                                             'outer': role['outer'], 'group': role['group'], 'inner': inner,
                                             'block': j, 'feature': FEATURES[j], 'subspace': s,
                                             **{k: float(payload[k][j, pos]) for k in ['V_pre', 'V_post', 'V_min', 'repeat_pre', 'repeat_post']},
                                             'mean_pre': cpu(payload['mean_pre'][sl(j)]).tolist(),
                                             'mean_post': cpu(payload['mean_post'][sl(j)]).tolist()})
                for k, name in enumerate(PREDICTORS):
                    predictions.append(frame(payload['predictions'][k], route, predictor=name))
                for k, arm in enumerate(['P', 'G']):
                    for vi, name in enumerate(VIEWS):
                        views.append(frame(payload['views'][k, vi], route, arm=arm, view=name))
                for fp in [path, path.with_suffix('.json'), path.parent/'replay-checks.json', path.parent/'routing.parquet']:
                    files[rel(fp)] = sha(fp)
            if (ri+1) % 10 == 0:
                progress('P2_forecasts', roles=ri+1, total=60, mappings=2*(ri+1)*4)
        save(pd.DataFrame(summary_rows), 'marginal-summaries')
        save(pd.DataFrame(replay_rows), 'map-replay-checks')
        forecast = pd.concat(predictions, ignore_index=True)
        counter = pd.concat(views, ignore_index=True)
        need(len(forecast) == 19200 and len(counter) == 30720 and len(replay_rows) == 480, 'Prediction matrix')
        save(forecast, 'frozen-predictions'); save(counter, 'counterfactual-views')
        for name in ['frozen-predictions', 'counterfactual-views', 'map-replay-checks', 'marginal-summaries']:
            files[rel(OUT/(name+'.parquet'))] = sha(OUT/(name+'.parquet'))
        score_reads = sum(r['purpose'] in {'C-score', 'C-business-metadata'} for r in READS)
        need(score_reads == 0, 'Premature score read')
        write(OUT/'predictions-complete.json', {'contract_sha256': sha(OUT/'contract.json'),
                                               'maps': 480, 'summary_estimates': 240, 'files': files,
                                               'query_map_predictions': 7680, 'predictor_rows': len(forecast),
                                               'counterfactual_rows': len(counter), 'score_reads_before_seal': 0,
                                               'new_model_fits': 0})
