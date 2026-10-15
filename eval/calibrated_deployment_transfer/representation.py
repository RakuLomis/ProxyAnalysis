"""Separately fitted C-only kernels and per-arm source views; no test inputs."""
from common import *

def smooth(n):
    k = n.shape[1]; q = (n.sum(0)+1/k)/(n.sum()+1)
    m = (n+q)/(n.sum(1)[:, None]+1)
    require(torch.isfinite(m).all() and (m > 0).all() and float((m.sum(1)-1).abs().max()) < 1e-12, 'Kernel normalization')
    return q, m

def true_kernel(d, j):
    require(set(d) == {'pair_id', 'content_id', 'fit_mass', *[s+'_'+f for s in ['pre', 'post'] for f in FEATURES]}, 'True schema')
    k = size(j); a = bins(d['pre_'+FEATURES[j]], j); b = bins(d['post_'+FEATURES[j]], j)
    n = weighted(a*k+b, tensor(d.fit_mass), k*k).reshape(k, k)
    q, m = smooth(n); return {'counts': n, 'q': q, 'matrix': m, 'row_mass': n.sum(1)}

def group_kernel(pre, post, j):
    for side, d in [('pre', pre), ('post', post)]:
        require(set(d) == {'content_id', 'fit_mass', *[side+'_'+f for f in FEATURES]}, 'Anonymous identity leak')
    contents = sorted(pre.content_id.unique()); require(set(contents) == set(post.content_id), 'Group contents mismatch')
    codes = dict(zip(contents, range(len(contents)))); k = size(j); margins = []
    for side, d in [('pre', pre), ('post', post)]:
        u = tensor(d.content_id.map(codes), torch.long); b = bins(d[side+'_'+FEATURES[j]], j)
        margins.append(weighted(u*k+b, tensor(d.fit_mass), len(contents)*k).reshape(-1, k))
    a, b = margins
    require(float((a.sum(1)-b.sum(1)).abs().max()) < 1e-10 and (a.sum(1) > 0).all(), 'Group mass mismatch')
    n = a.T@(b/a.sum(1)[:, None]); q, m = smooth(n)
    return {'counts': n, 'q': q, 'matrix': m, 'row_mass': n.sum(1)}

def fit_kernels():
    c = start('C_kernels'); errors = []
    for r in c['kernels']:
        dst = OUT/'kernels'/r['id']; src = OUT/'packages/C-kernels'/r['id']
        if (dst/'complete.json').exists():
            for side in ['true', 'group']: artifact(dst/(side+'.pt'))
            errors.append(read(dst/'complete.json')); continue
        # Two independent producers: anonymous producer receives no paired frame or true artifact.
        paired = package(src/'paired.parquet', 'kernel-true')
        true = {f: true_kernel(paired, j) for j, f in enumerate(FEATURES)}
        require(abs(paired.fit_mass.sum()-len(r['C_contents'])) < 1e-10, 'C mass scope')
        save_artifact(true, dst/'true.pt', source_packages=[rel(src/'paired.parquet')], C_contents=r['C_contents'])
        del paired
        gp = package(src/'group-pre.parquet', 'kernel-group'); gb = package(src/'group-post.parquet', 'kernel-group')
        group = {f: group_kernel(gp, gb, j) for j, f in enumerate(FEATURES)}
        save_artifact(group, dst/'group.pt', source_packages=[rel(src/'group-pre.parquet'), rel(src/'group-post.parquet')],
                      exact_identity_read=False, C_contents=r['C_contents'])
        err = max(float((true[f]['counts'].sum(axis)-group[f]['counts'].sum(axis)).abs().max())
                  for f in FEATURES for axis in [0, 1])
        require(err < 1e-10, 'True/group marginals differ')
        d = {'id': r['id'], 'mass': len(r['C_contents']), 'marginal_max_error': err,
             'group_exact_identity_input': False, 'cuda': True}
        complete(dst/'complete.json', **d); errors.append(d)
        if len(errors) % 20 == 0: progress('CT21_C_kernels', roles=len(errors), total=len(c['kernels']))
    finish('C_kernels', roles=len(errors), marginal_max_error=max(x['marginal_max_error'] for x in errors))

def mapped(h, bundle):
    z = h.clone(); support = []
    for j, f in enumerate(FEATURES):
        z[:, block(j)] = h[:, block(j)]@bundle[f]['matrix']
        support.append((h[:, block(j)]*(bundle[f]['row_mass'] == 0)).sum(1))
        require(float((z[:, block(j)].sum(1)-1).abs().max()) < 1e-12 and (z[:, block(j)] >= 0).all(), 'Mapped histogram')
    return z, torch.stack(support, 1)

def invroot(cov, power):
    value, vec = torch.linalg.eigh((cov+cov.T)/2)
    require((value > 0).all(), 'CORAL covariance not positive definite')
    return (vec*value.pow(power))@vec.T

def coral(z, source, cp, missing):
    transformed = z.clone(); parameters = {}; identity = torch.eye(96, device=device(), dtype=torch.float64)
    cy = tensor(truths(cp), torch.long)
    require(not any(y in missing for y in cy.cpu().tolist()), 'CORAL target contains U')
    # cp numeric standardized coordinate passed separately from metadata by caller.
    cz = tensor(cp[HIST]); cm = cz.mean(0); cd = cz-cm; ct = cd.T@cd/(len(cz)-1)
    right = invroot(ct+identity, .5)
    for p in sorted(source.protocol.unique()):
        ix = np.where(source.protocol.to_numpy() == p)[0]; yi = truths(source.iloc[ix])
        matched = tensor(~np.isin(yi, missing), torch.bool)
        zs = z[ix][matched]; sm = zs.mean(0); sd = zs-sm; cs = sd.T@sd/(len(zs)-1)
        mat = invroot(cs+identity, -.5)@right
        transformed[ix] = (z[ix]-sm)@mat+cm
        parameters[p] = {'source_mean': sm, 'target_mean': cm, 'matrix': mat,
                         'source_matched_visits': len(zs), 'target_C_visits': len(cz)}
    require(torch.isfinite(transformed).all(), 'Invalid CORAL output')
    return transformed, parameters

def loss_weights(source, cp, missing):
    ys = truths(source); yc = truths(cp); wm = np.zeros(len(source)); wc = np.zeros(len(cp))
    for y in range(6):
        s = np.where(ys == y)[0]; require(len(s) > 0, 'Source class unavailable')
        share = 1 if y in missing else .5
        for proto in source.protocol.unique():
            ix = s[source.iloc[s].protocol.to_numpy() == proto]
            require(len(ix) > 0, 'Source deployment class unavailable')
            wm[ix] = share/(6*source.protocol.nunique()*len(ix)*2)
        if y not in missing:
            t = np.where(yc == y)[0]; require(len(t) > 0, 'C class unavailable'); wc[t] = .5/(6*len(t))
    mass = tensor(np.concatenate([wm, wm, wc])); yall = tensor(np.concatenate([ys, ys, yc]), torch.long)
    require(abs(float(mass.sum())-1) < 1e-12, 'Total weight')
    require(float((weighted(yall, mass, 6)-1/6).abs().max()) < 1e-12, 'Class weights')
    require(max(abs(float(tensor(wm).sum())-1/3), abs(float(tensor(wc).sum())-1/3)) < 1e-12, 'Slot weights')
    return mass, yall

def build_slots(r):
    root = rolepath(r); dst = OUT/'slots'/r['id']
    if (dst/'complete.json').exists():
        for arm in ARMS: artifact(dst/(arm+'.pt'))
        return read(dst/'complete.json')
    source = package(root/'source-post.parquet', 'view-fit'); cp = package(root/'C-post.parquet', 'view-fit')
    raw = tensor(source[HIST]); cr = tensor(cp[HIST]); mu, scale = scaler(torch.cat([raw, cr]))
    zs, zc = (raw-mu)/scale, (cr-mu)/scale
    mass, ys = loss_weights(source, cp, r['missing'])
    ys_main = truths(source); logs = []
    for arm in ARMS:
        support = None; params = None
        if arm == 'CT0': aux = zs.clone()
        elif arm == 'CT2':
            metadata = cp.copy(); metadata[HIST] = zc.cpu().numpy()
            aux, params = coral(zs, source, metadata, r['missing'])
        else:
            pre = package(root/'source-pre.parquet', 'view-fit')
            require('visit_id' not in pre and 'session_id' not in pre, 'Pre control exact identity')
            pr = tensor(pre[HIST]); py = truths(pre)
            # Pre rows have independent ordering. Their labels and mass must follow that ordering.
            pmass, _ = loss_weights(pre, cp, r['missing'])
            y = tensor(np.concatenate([ys_main, py, truths(cp)]), torch.long)
            # Independent pre sorting keeps per-class/domain weight equal; use its own auxiliary masses.
            mass_arm = torch.cat([mass[:len(source)], pmass[len(pre):2*len(pre)], mass[2*len(source):]])
            if arm == 'CT1': aux = (pr-mu)/scale
            else:
                which = 'true' if arm == 'CT4' else 'group'
                bundle = artifact(OUT/'kernels'/r['kernel_id']/(which+'.pt'))
                view, support = mapped(pr, bundle); aux = (view-mu)/scale
        if arm in ['CT0', 'CT2']: y, mass_arm = ys, mass
        x = torch.cat([zs, aux, zc])
        require(len(x) == (640 if r['inner'] is None else 336), 'View count')
        model = {'x': x, 'y': y, 'mass': mass_arm, 'mu': mu, 'scale': scale}
        save_artifact(model, dst/(arm+'.pt'), role_id=r['id'], arm=arm,
                      source_contents=r['train_contents'], C_contents=r['C_contents'],
                      raw_target_U_read=False, reference_model_read=False)
        if params is not None: save_artifact(params, dst/'coral.pt', role_id=r['id'])
        if support is not None: save_artifact({'zero_support_mass': support}, dst/(arm+'-support.pt'), role_id=r['id'])
        logs.append({'arm': arm, 'rows': len(x), 'real_scaler_rows': len(source)+len(cp),
                     'source_visits': len(source), 'C_visits': len(cp), 'class_mass_error':
                     float((weighted(y, mass_arm, 6)-1/6).abs().max()), 'device': 'cuda:0'})
    complete(dst/'complete.json', id=r['id'], slots=logs, target_U_reads=0)
    return read(dst/'complete.json')

def slots():
    c = start('slots'); logs = []
    for r in c['main']:
        logs.append(build_slots(r))
        if len(logs) % 25 == 0: progress('CT22_CT24_slots', roles=len(logs), total=len(c['main']))
    write(OUT/'manifests/slot-ledger.json', logs)
    finish('slots', roles=len(logs), main_test_data_reads=0)

def profile():
    c = start('runtime_profile')
    from main_experiment import modelpath
    r = next(r for r in c['main'] if r['inner'] is not None)
    slot = artifact(OUT/'slots'/r['id']/'CT0.pt'); p = modelpath(r, 'CT0', 0.)
    if not p.with_suffix('.json').exists():
        m, log = fit(slot['x'], slot['y'], slot['mass'], 0.)
        save_artifact({'mu': slot['mu'], 'scale': slot['scale'], **m}, p,
                      optimizer=log, role_id=r['id'], arm='CT0', t=0., target_U_read=False)
    else: artifact(p); log = read(p.with_suffix('.json'))['optimizer']
    write(OUT/'manifests/runtime-profile.json', {'role': r['id'], 'arm': 'CT0', 'optimizer': log,
        'formal_fit_counted_within_14400': True, 'additional_formal_fits': 0,
        'rough_main_seconds_if_representative': 14700*log['seconds'],
        'estimate_not_completion_promise': True, 'validation_or_outer_labels_read': False})
    finish('runtime_profile', seconds=log['seconds'], formal_fit_in_existing_budget=True)

if __name__ == '__main__':
    import sys
    {'kernels': fit_kernels, 'slots': slots, 'profile': profile}[sys.argv[1]]()
