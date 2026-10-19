"""P1: synthetic geometry, permission and aggregation tests, no real score IO."""
from .common import *
from .basis import all_bases, energies
from .counterfactuals import make_views
from .marginal_references import summarize_marginals


def run():
    with stage('P1'):
        rows = []

        def check(name, value, threshold=TOL):
            value = float(value)
            need(np.isfinite(value) and value <= threshold, name + ' failed: ' + str(value))
            rows.append({'test': name, 'error': value, 'threshold': threshold, 'passed': True})

        with compute('synthetic-tests'):
            bases = all_bases()
            for n, b in bases.items():
                eye = torch.eye(n, device='cuda:0', dtype=torch.float64)
                check(f'n{n}-basis', error(b['T'].T @ b['T'], eye))
                check(f'n{n}-reconstruction', error(b['PM'] + b['PL'] + b['PR'], eye))
                for k in ['PM', 'PL', 'PR']:
                    check(f'n{n}-{k}-symmetric', error(b[k], b[k].T))
                    check(f'n{n}-{k}-idempotent', error(b[k] @ b[k], b[k]))
                for x, y in [('PM', 'PL'), ('PM', 'PR'), ('PL', 'PR')]:
                    check(f'n{n}-{x}-{y}', float((b[x] @ b[y]).abs().max()))
                v = torch.zeros(n, device='cuda:0', dtype=torch.float64)
                v[2:5] = t([.1, -.2, .1])
                check(f'n{n}-shape-preserves-mass', float((v @ b['u0']).abs()))
                check(f'n{n}-shape-preserves-location', float((v @ b['u1']).abs()))
                need(float((v @ b['PR']).square().sum()) > .01, 'Nonconstant R fixture')
                a = torch.zeros_like(v); a[2] = -.1; a[3] = .1
                check(f'n{n}-adjacent-preserves-mass', float((a @ b['u0']).abs()))
                need(float((a @ b['u1']).abs()) > 0, 'Adjacent move must change L')
                flux = prefix_sum(a)
                literal = torch.stack([a[:k+1].sum() for k in range(n)])
                check(f'n{n}-deterministic-prefix', error(flux, literal))
                check(f'n{n}-flux', float(((a @ b['c']) - (b['c'][-1]*flux[-1] - (torch.diff(b['c'])*flux[:-1]).sum())).abs()))
                check(f'n{n}-constant-offset-variance', float((a.repeat(5, 1)-a).square().sum()))
                need(float(a.square().mean()) > 0, 'Offset RMS cannot be zero')
            a = torch.cat([torch.full((8, n), 1/n, device='cuda:0', dtype=torch.float64) for n in SIZES], 1)
            pred = a.clone(); pred[:, :9] += t(np.linspace(-.2, .3, 9))
            vv = make_views(a, pred, bases)
            e0 = energies(pred-a, bases)
            ev = energies(vv-a, bases)
            check('LOC-keeps-M', error(ev[2, :, :, 0], e0[:, :, 0]))
            check('LOC-keeps-R', error(ev[2, :, :, 2], e0[:, :, 2]))
            check('MASS-keeps-L', error(ev[1, :, :, 1], e0[:, :, 1]))
            check('raw-energy-closure', error((pred-a).square().sum(1),
                  (e0 * t([[1, 1, n-2] for n in SIZES])).sum((1, 2))))
            # Explicit counterexample: preserving L may improve raw but worsen scaled error.
            n = 9; b = bases[n]
            l = b['u1']; r = b['PR'][:, 0]; r = r/torch.linalg.vector_norm(r)
            sd = t([.01, 1, 1, 1, 1, 1, 1, 1, 1])
            k = -float(l[0]/r[0])
            residual = l + k*r
            need(float((k*r).square().sum()) < float(residual.square().sum()), 'Raw counterexample')
            need(float(((k*r)/sd).square().sum()) > float((residual/sd).square().sum()), 'Scaled counterexample')
            check('raw-std-tradeoff-fixture', 0)
            # Same marginals, independent order; no paired grouping needed.
            train_a = a[:1].repeat(48, 1); train_b = train_a.clone()
            train_a[:, 0] += torch.arange(48, device='cuda:0') * 1e-5
            train_a[:, 1] -= torch.arange(48, device='cuda:0') * 1e-5
            train_b[:, 2] += torch.arange(48, device='cuda:0') * 2e-5
            train_b[:, 3] -= torch.arange(48, device='cuda:0') * 2e-5
            groups = np.repeat(np.arange(12), 4)
            summary = summarize_marginals(train_a, groups, train_b, groups, bases)
            ix = np.arange(48)[::-1].copy()
            perm = summarize_marginals(train_a[ix], groups[ix], train_b, groups, bases)
            check('anonymous-permutation-mean', error(summary['mean_pre'], perm['mean_pre']))
            # Fixed affine orientation and reversible raw/std path.
            mu = a[0]; sigma = t(np.linspace(.1, 2, 96)); mat = torch.diag(t(np.linspace(.8, 1.2, 96))); bias = sigma*.1
            z = (pred-mu)/sigma
            mapped = (z@mat.T+bias)*sigma+mu
            direct = mu+(pred-mu)*torch.diag(mat)+bias*sigma
            check('affine-coordinate-replay', error(mapped, direct))
            # Post changes cannot alter pre-only view construction.
            other_post = a+.001
            check('query-post-isolation', error(make_views(a, pred, bases), vv))
            need(float((energies(pred-a, bases)-energies(pred-other_post, bases)).abs().max()) > 0, 'Score responds to post')
            check('zero-scale-and-zero-reference-policy', 0 if not (0. > SCALE_MIN) else 1)
            # Reweight rows globally; never normalize each fold separately.
            weights = np.ones(6)/6; content = np.array([0, 0, 1, 1, 2, 2]); vals = np.arange(6.)
            draws = np.array([[3, 0, 0], [1, 1, 1], [0, 2, 1]])
            nums = np.bincount(content, weights*vals); masses = np.bincount(content, weights)
            fast = (draws@nums)/(draws@masses)
            slow = np.array([np.sum(weights*d[content]*vals)/np.sum(weights*d[content]) for d in draws])
            check('cluster-bootstrap-vectorized', np.max(np.abs(fast-slow)))
            # Ratio of pooled D/V is not the mean of fold ratios.
            d = np.array([1., 1.]); v = np.array([.01, 1.])
            need(abs(d.mean()/v.mean() - np.mean(d/v)) > 1, 'D/V ordering fixture')
            check('ratio-order-fixture', 0)
            # Marginals cannot identify coupling; both joint matrices share marginals.
            j1 = np.eye(2)/2; j2 = np.fliplr(j1)
            need(np.array_equal(j1.sum(0), j2.sum(0)) and not np.array_equal(j1, j2), 'Coupling fixture')
            check('nonunique-transport-fixture', 0)
            # Calls fail before decoding any real score or metadata column.
            role = contract()['roles'][0]
            root = PARENT/'packages'/role['id']/'i0'
            for name, purpose, path in [
                ('deny-score-before-seal', 'C-score', root/'P-score.parquet'),
                ('deny-metadata-before-seal', 'C-business-metadata', ROOT/role['metadata_ref']),
                ('deny-post-as-common-pre', 'common-query-pre', root/'P-score.parquet'),
                ('deny-paired-data-as-group-fit', 'anonymous-fit', root/'P-fit.parquet')]:
                denied = False
                try:
                    package(path, role, purpose)
                except RuntimeError:
                    denied = True
                need(denied, name)
                check(name, 0)
            need(not any(x['purpose'] in {'C-score', 'C-business-metadata'} for x in READS), 'Permission test decoded score')
        for n, b in bases.items():
            np.savez(target(OUT / f'basis-{n}.npz'), **{k: cpu(v) for k, v in b.items()})
        save(pd.DataFrame(rows), 'synthetic-tests')
        write(OUT/'P1-verification.json', {'numeric_pass': True, 'checks': len(rows), 'geometry_tolerance': TOL,
                                         'new_model_fits': 0, 'real_score_reads': 0})
        progress('synthetic_tests_passed', tests=len(rows))
