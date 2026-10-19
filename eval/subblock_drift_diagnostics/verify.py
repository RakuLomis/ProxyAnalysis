"""P5 independent algebraic replay and provenance closeout, without any fitting."""
from .common import *
from .prepare import score_post
from .replay import chunk_path


def run():
    with stage('P5'):
        for name in ['P0', 'P1', 'P2', 'P3', 'P4']:
            need(read(OUT/'stages'/f'{name}.json')['complete'], 'Missing stage '+name)
        for p, info in contract()['files'].items():
            checked(ROOT/p, 'final-hash-only', info.get('role_id'))
        seals = [verify_prediction_seal(), read(OUT/'score-complete.json'), read(OUT/'summary-complete.json')]
        for s in seals:
            for p, h in s['files'].items():
                need(sha(ROOT/p) == h, 'Changed sealed derived asset: '+p)
        bindings = pd.read_parquet(OUT/'source-bindings.parquet')
        need(sha(OUT/'source-bindings.parquet') == read(OUT/'stages/P0.json')['binding_sha256'], 'Bindings hash changed')
        need(sha(OUT/'role-membership.parquet') == read(OUT/'stages/P0.json')['membership_sha256'], 'Membership hash changed')
        errors = pd.read_parquet(OUT/'prediction-error-ledger.parquet')
        protected = pd.read_parquet(OUT/'protection-effect-ledger.parquet')
        maxerr = 0.; checks = 0
        # Explicit scalar M/L and Pythagorean R, independent of production PR multiply.
        for role in contract()['roles']:
            for inner in range(4):
                binding = bindings[(bindings.role_id == role['id']) & (bindings.inner == inner) & bindings.arm.eq('P')].iloc[0]
                path = chunk_path(role, inner)
                v = own_obj(path); route = pd.read_parquet(path.parent/'routing.parquet')
                post = score_post(role, ROOT/binding.P_score_ref, route)
                es = errors[errors.role_id.eq(role['id']) & errors.inner.eq(inner)]
                ps = protected[protected.role_id.eq(role['id']) & protected.inner.eq(inner)]
                with compute(role['id']+f'/i{inner}-independent-replay'):
                    diff = v['predictions']-post
                    for j, n in enumerate(SIZES):
                        c = torch.arange(n, device='cuda:0', dtype=torch.float64)/(n-1)
                        uc = c-c.mean(); uc = uc/torch.linalg.vector_norm(uc)
                        x = diff[..., sl(j)]
                        em = x.sum(-1).square()/n
                        el = (x@uc).square()
                        er = (x.square().sum(-1)-em-el)/(n-2)
                        std = (x/v['scale'][sl(j)]).square().mean(-1)
                        for k, pred in enumerate(PREDICTORS):
                            old = es[es.block.eq(j) & es.predictor.eq(pred)].sort_values('row')
                            need(len(old) == 16, 'Independent score membership')
                            for name, val in [('E_M', em[k]), ('E_L', el[k]), ('E_R', er[k]), ('std_mse', std[k])]:
                                e = error(val, t(old[name].to_numpy()))
                                maxerr = max(maxerr, e); need(e <= TOL, 'Independent error mismatch')
                            checks += 1
                        for k, arm in enumerate(['P', 'G']):
                            base = v['predictions'][k+3, :, sl(j)]
                            d = v['a'][:, sl(j)]-base
                            mass = d.mean(-1, keepdim=True).expand_as(d)
                            loc = (d@uc)[:, None]*uc
                            expected = [base, base+mass, base+loc, base+mass+loc]
                            for vi in range(4):
                                e = error(expected[vi], v['views'][k, vi, :, sl(j)])
                                maxerr = max(maxerr, e); need(e <= TOL, 'Independent view mismatch')
                                old = ps[ps.block.eq(j) & ps.arm.eq(arm) & ps.view.eq(VIEWS[vi])].sort_values('row')
                                rs = (expected[vi]-post[:, sl(j)]).square().sum(-1)
                                ss = ((expected[vi]-post[:, sl(j)])/v['scale'][sl(j)]).square().mean(-1)
                                for name, val in [('raw_sum', rs), ('std_mse', ss)]:
                                    e = error(val, t(old[name].to_numpy()))
                                    maxerr = max(maxerr, e); need(e <= TOL, 'Independent protection score mismatch')
                    need(torch.isfinite(diff).all(), 'Nonfinite independent input')
        core = pd.read_parquet(OUT/'evaluation-core.parquet')
        dep = pd.read_parquet(OUT/'by-deployment-block.parquet')
        ci = pd.read_parquet(OUT/'bootstrap-descriptive.parquet')
        lab = pd.read_parquet(OUT/'content-strata.parquet')
        drawfile = np.load(OUT/'bootstrap-draws.npz')
        draws = drawfile['multiplicities'].astype(float)
        tokens = drawfile['content_tokens'].tolist()
        need(tokens == lab.content_token.tolist(), 'Bootstrap token order mismatch')
        lookup = {u: i for i, u in enumerate(tokens)}
        with compute('independent-aggregate-and-bootstrap-verification'):
            for (protocol, block), g in core.groupby(['deployment', 'block'], sort=True):
                result = dep[dep.deployment.eq(protocol) & dep.block.eq(block)].iloc[0]
                w = g.original_weight.to_numpy()
                need(abs(w.sum()-1) <= 1e-12, 'Original deployment mass')
                for s in ['L', 'R']:
                    numerator = float(w@g['D_'+s]); denominator = float(w@g['V_'+s])
                    need(abs(numerator-result['D_'+s]) <= TOL and abs(denominator-result['V_'+s]) <= TOL, 'Aggregate numerator/denominator')
                    if denominator > SCALE_MIN:
                        need(abs(numerator/denominator-result['rho_'+s])/max(1, abs(result['rho_'+s])) <= TOL, 'Ratio order mismatch')
                # Evaluate a fixed subset of bootstrap replicates with literal row weights.
                ix = np.array([lookup[u] for u in g.content_token])
                for rep in [0, 1, 2, 9999]:
                    wr = w*draws[rep, ix]; wr /= wr.sum()
                    fast = np.bincount(ix, weights=w*g.G_E_R)-np.bincount(ix, weights=w*g.P_E_R)
                    mass = np.bincount(ix, weights=w)
                    ref = float(draws[rep]@fast/(draws[rep]@mass))
                    raw = float(wr@(g.G_E_R-g.P_E_R))
                    need(abs(ref-raw) <= TOL, 'Independent bootstrap weights')
                # Full 10000-replicate check of the P-vs-G shape interval.
                numer = np.zeros(30); mass = np.zeros(30)
                np.add.at(numer, ix, w*(g.G_E_R-g.P_E_R).to_numpy())
                np.add.at(mass, ix, w)
                gain = (draws@numer)/(draws@mass)
                quant = np.quantile(gain, [.025, .975])
                old = ci[ci.deployment.eq(protocol) & ci.block.eq(block) & ci.metric.eq('G_R_gain')].iloc[0]
                need(np.max(np.abs(quant-[old.lower, old.upper])) <= TOL, 'Independent gain interval')
        manifests = []
        for p in (OUT/'ledgers').glob('*.json'):
            manifests.extend(read(p)['reads'])
        manifests += READS
        score_reads = [r for r in manifests if r.get('purpose') == 'C-score']
        metadata_reads = [r for r in manifests if r.get('purpose') == 'C-business-metadata']
        need(all(r.get('stage') in {'P3', 'P5'} for r in score_reads+metadata_reads), 'Score barrier violated')
        for r in manifests:
            if r.get('numeric_decode'):
                info = contract()['files'][r['path']]
                need(info['kind'] in {'P-query', 'P-train', 'P-score', 'G-pre-train', 'G-post-train', 'G-query', 'map', 'scale', 'old-forecast'}, 'Forbidden numeric input kind')
                need(r['role_id'] == info['role_id'], 'Cross-role numeric read')
        need(len(score_reads) == 480 and len(metadata_reads) == 60, 'Scoring read audit unexpected')
        flags = read(OUT/'screening-flags.json')
        budget = read(OUT/'budget.json')
        result = {'numeric_pass': True, 'source_integrity_pass': True,
                  'independent_predictor_fold_block_batches': checks, 'rows_per_batch': 16,
                  'independent_pair_block_checks': checks*16,
                  'max_independent_normalized_error': maxerr, 'all_registered_inputs_unchanged': True,
                  'old_guard_status': read(PARENT/'completion.json')['status'],
                  'score_reads': len(score_reads), 'C_metadata_reads': len(metadata_reads),
                  'actual_H_read': False, 'actual_U_read': False, 'PCAP_read': False,
                  'new_model_fits': 0, 'summary_estimates': 240, 'code_sha256': contract()['source_sha256'],
                  'prediction_seal_sha256': sha(OUT/'predictions-complete.json'),
                  'active_compute_seconds': budget['active_compute_seconds']}
        write(OUT/'verification.json', result)
        from .report import run as report
        report()
        files = {rel(p): sha(p) for p in [*OUT.glob('*.parquet'), *OUT.glob('*.npz'),
                                         OUT/'screening-flags.json', OUT/'verification.json', DOC/'complete-report.md']}
        write(OUT/'ledger.json', {'activity': read(OUT/'budget.json'),
                                 'stages': {p.stem: read(p) for p in (OUT/'stages').glob('*.json')},
                                 'new_model_fits': 0, 'summary_estimates': 240,
                                 'common_query_map_forward_rows': 7680, 'old_fixture_forward_rows': 7680,
                                 'independent_score_replay_pairs': 3840, 'output_files': files,
                                 'includes_earlier_unscored_historical_exposure': True})
        write(OUT/'completion.json', {'program_complete': True, 'numeric_pass': True, 'source_integrity_pass': True,
                                      'status': 'complete_with_discussion_candidates' if flags['candidate_count'] else 'complete_no_discussion_candidate',
                                      'has_discussion_candidate': bool(flags['candidate_count']),
                                      'discussion_candidate_count': flags['candidate_count'],
                                      'uncertainty_unresolved': flags['uncertainty_unresolved'],
                                      'new_model_fits': 0, 'summary_estimates': 240,
                                      'actual_H_read': False, 'actual_U_read': False,
                                      'new_G_training_authorized': False, 'business_training_authorized': False,
                                      'old_artifacts_changed': False, 'pending_stages': [],
                                      'active_compute_seconds': read(OUT/'budget.json')['active_compute_seconds'],
                                      'verification_sha256': sha(OUT/'verification.json'),
                                      'report_sha256': sha(DOC/'complete-report.md')})
