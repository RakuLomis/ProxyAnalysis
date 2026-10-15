"""Synthetic unit tests and actual allowed-training CT0 objective replay."""
from common import *
from representation import true_kernel, group_kernel, mapped, loss_weights, invroot

def run():
    configure(); tests = []
    def check(name, ok):
        require(ok, name); tests.append({'name': name, 'passed': True})
    def rejects(name, f):
        failed = False
        try: f()
        except (RuntimeError, KeyError): failed = True
        check(name, failed)
    check('CUDA float64 arithmetic', float(tensor([1, 2, 3]).square().sum()) == 14)
    check('right bin edges', torch.equal(bins([0, 1, 256, 4096], 0), tensor([0, 1, 2, 4], torch.long)))
    check('deterministic weighted counts', torch.equal(weighted(tensor([0, 1, 1], torch.long), tensor([.3, .2, .5]), 2), tensor([.3, .7])))
    q = pd.DataFrame({'visit_id': ['x'], **{h: [0.] for h in HIST}})
    validate_query(q); check('post-only schema', True)
    for key in ['pre_W_up', 'label_id', 'content_id', 'protocol', 'SNI', 'port', 'fold', 'quality_flag']:
        rejects('query rejects '+key, lambda key=key: validate_query(q.assign(**{key: ['bad']})))
    rejects('duplicate opaque query identity', lambda: validate_query(pd.concat([q, q])))
    # Nontrivial coupling with identical anonymous marginals.
    d = pd.DataFrame({'pair_id': [str(i) for i in range(8)], 'content_id': ['a']*4+['b']*4,
                      'fit_mass': [.25]*8})
    for f in FEATURES:
        d['pre_'+f] = [0, 1, 1, 0, 2, 2, 3, 3]; d['post_'+f] = [0, 1, 1, 0, 3, 3, 2, 2]
    pre = d[['content_id', 'fit_mass', *['pre_'+f for f in FEATURES]]]
    post = d[['content_id', 'fit_mass', *['post_'+f for f in FEATURES]]]
    for j in range(10):
        t = true_kernel(d, j); g = group_kernel(pre, post, j)
        check('kernel normalized '+str(j), float((t['matrix'].sum(1)-1).abs().max()) < 1e-12)
        check('anonymous same marginals '+str(j), max(float((t['counts'].sum(a)-g['counts'].sum(a)).abs().max()) for a in [0, 1]) < 1e-12)
        check('unseen row prior '+str(j), torch.equal(t['matrix'][t['row_mass'] == 0], t['q'].expand(int((t['row_mass'] == 0).sum()), -1)))
    rejects('anonymous pre identity', lambda: group_kernel(pre.assign(pair_id='x'), post, 0))
    rejects('anonymous shared visit identity', lambda: group_kernel(pre, post.assign(visit_id='x'), 0))
    original_group = group_kernel(pre, post, 4)
    shuffled_group = group_kernel(pre.sample(frac=1, random_state=71), post.sample(frac=1, random_state=93), 4)
    check('anonymous independent permutation invariant', float((original_group['matrix']-shuffled_group['matrix']).abs().max()) < 1e-12)
    changed = d.copy()
    changed['post_P_up'] = [1, 0, 0, 1, 2, 2, 3, 3]
    changed_true = true_kernel(changed, 4)
    check('true kernel responds to coupling not only marginals', float((changed_true['matrix']-true_kernel(d, 4)['matrix']).abs().max()) > .01)
    bundle = {f: true_kernel(d, j) for j, f in enumerate(FEATURES)}
    h = torch.cat([torch.ones((3, size(j)), device=device(), dtype=torch.float64)/size(j) for j in range(10)], 1)
    v, _ = mapped(h, bundle); check('all mapped blocks normalized', all(float((v[:, block(j)].sum(1)-1).abs().max()) < 1e-12 for j in range(10)))
    check('CORAL identity SPD', float((invroot(torch.eye(96, device=device(), dtype=torch.float64), -.5)-torch.eye(96, device=device(), dtype=torch.float64)).abs().max()) == 0)
    torch.manual_seed(20261006); x = torch.randn((24, 96), device=device(), dtype=torch.float64)/10
    y = tensor(np.repeat(np.arange(6), 4), torch.long); mass = torch.full((24,), 1/24, device=device(), dtype=torch.float64)
    w = torch.randn((6, 96), device=device(), dtype=torch.float64)/20; b = torch.zeros(6, device=device(), dtype=torch.float64)
    check('old unweighted L2 objective reproduced', abs(float(objective(w, b, x, y, mass, 0)-(F.cross_entropy(x@w.T+b, y)+.0005*w.square().sum()))) < 1e-12)
    doubled = objective(w, b, torch.cat([x, x]), torch.cat([y, y]), torch.cat([mass/2, mass/2]), 1)
    check('duplicate slot objective', abs(float(doubled-objective(w, b, x, y, mass, 1))) < 1e-12)
    state, log = fit(x, y, mass, 0); check('independent objective gradient replay', log['gradient_replay_error'] < 1e-10)
    # A legal inner role; no query, validation labels or target U data are read for this replay.
    r = next(r for r in read(OUT/'manifests/role-registry.json')['main'] if r['inner'] is not None)
    src = pd.read_parquet(rolepath(r)/'source-post.parquet'); cp = pd.read_parquet(rolepath(r)/'C-post.parquet')
    ms, labels = loss_weights(src, cp, r['missing'])
    raw = torch.cat([tensor(src[HIST]), tensor(cp[HIST])]); mu, scale = scaler(raw)
    zs = (tensor(src[HIST])-mu)/scale; zc = (tensor(cp[HIST])-mu)/scale
    xx = torch.cat([zs, zs, zc]); yy = labels
    original = objective(w, b, xx, yy, ms, .25)
    collapsed = objective(w, b, torch.cat([zs, zc]), tensor(np.concatenate([truths(src), truths(cp)]), torch.long),
                          torch.cat([2*ms[:len(src)], ms[2*len(src):]]), .25)
    check('actual CT0 collapsed weighted objective', abs(float(original-collapsed)) < 1e-12)
    check('actual six class mass', float((weighted(yy, ms, 6)-1/6).abs().max()) < 1e-12)
    check('actual real scaler count', len(raw) == 192)
    write(OUT/'manifests/unit-tests.json', {'passed': True, 'tests': tests, 'count': len(tests),
          'synthetic_optimizer_fits': 1, 'outer_labels_read': False, 'target_U_read': False})
    progress('CT06_tests_passed', tests=len(tests))

if __name__ == '__main__': run()
