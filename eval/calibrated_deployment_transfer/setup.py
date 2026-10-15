"""Trusted cache packer; only this process may inspect the complete cohort."""
import platform
from common import *

def run():
    configure(); require(not (OUT/'manifests/experiment-contract.json').exists(), 'Cannot overwrite registered run')
    require(not (OUT/'manifests/preparation-complete.json').exists(), 'Preparation already finished')
    old = read(OLD/'manifests/experiment-contract.json'); baseline = {}
    require(read(OLD/'verification.json')['passed'], 'Historical KSR verification required')
    for key in ['source_sha256', 'packages_sha256', 'outer_kernels_sha256']:
        for p, h in old[key].items():
            require(sha(ROOT/p) == h, 'Historical input changed: '+p); baseline[p] = h
    for p in [Q/'features/paired-flow-features.parquet', Q/'cohorts/folds.parquet',
              OLD/'selection/choices.json', OLD/'selection/complete.json', OLD/'predictions/visits.parquet',
              OLD/'verification.json', ROOT/'outputs/cross-fitted-drift-reweighting-20261006/run-01/verification.json']:
        baseline[rel(p)] = sha(p)
    choicepath = OLD/'selection/choices.json'
    require(read(choicepath.parent/'complete.json')['choices_sha256'] == sha(choicepath), 'Old choice seal')
    choices = {(v['outer'], v['protocol']): v['t'] for v in read(choicepath) if v['arm'] == 'KSR1'}
    reused = []
    for outer in range(5):
      for proto in PROTOCOLS:
        t = choices[(outer, proto)]; mf = OLD/'models/outer'/f'f{outer}'/proto
        p = mf/('zero.pt' if t == 0 else f'KSR1-t{t:g}.pt')
        require(read(mf/'complete.json')['sha256'][p.name] == sha(p), 'Old model seal')
        for a in [p, mf/'complete.json']: baseline[rel(a)] = sha(a)
        reused.append({'outer': outer, 'protocol': proto, 't': t, 'path': rel(p)})
    df = pd.read_parquet(Q/'features/paired-flow-features.parquet')
    folds = pd.read_parquet(Q/'cohorts/folds.parquet')
    require(len(df) == 23566 and df.pair_id.is_unique and df.session_id.nunique() == 480, 'Pair/visit counts')
    require(set(df.protocol) == set(PROTOCOLS) and set(df.repetition) == {1, 2, 3, 4}, 'Protocols/repetitions')
    require(df.groupby('protocol').size().to_dict() == dict(zip(PROTOCOLS, [5608, 5957, 5919, 6082])), 'Pair counts')
    require(len(folds) == 30 and folds.content_id.is_unique and folds.groupby('fold').size().eq(6).all(), 'Global folds')
    require(folds.groupby(['fold', 'label_id']).size().eq(1).all(), 'Per-class global fold')
    foldmap = dict(zip(folds.content_id, folds.fold))
    require(df.content_id.map(foldmap).eq(df.fold).all(), 'Frozen fold mismatch')
    for field in ['pair_id', 'session_id', 'logical_id', 'carrier_id', 'registered_epoch_proxy', 'content_id']:
        require(df[field].notna().all() and df.groupby(field).fold.nunique().max() == 1, 'Entity crosses fold: '+field)
    require(df.groupby(['protocol', 'content_id']).content_visit_flow_mass.sum().sub(1).abs().max() < 1e-12, 'Content mass')
    df['visit_id'] = df.session_id.map(visitid)
    native = [s+'_'+f for s in ['pre', 'post'] for f in FEATURES]
    require(not df[native].isna().any().any(), 'No feature imputation')
    pool = {}; replay = 0.
    for proto in PROTOCOLS:
      for side in ['pre', 'post']:
        rows = []
        for sid, raw in df[df.protocol.eq(proto)].groupby('session_id', sort=True):
            r = raw.iloc[0]; row = {k: r[k] for k in ['visit_id', 'content_id', 'label_id', 'protocol', 'fold']}
            for j, f in enumerate(FEATURES):
                h = F.one_hot(bins(raw[side+'_'+f], j), size(j)).to(torch.float64).mean(0)
                row.update({f'h{j:02d}_{b:02d}': float(h[b]) for b in range(size(j))})
            rows.append(row)
        d = pd.DataFrame(rows).sort_values('visit_id').reset_index(drop=True)
        require(len(d) == 120 and d.groupby('label_id').size().eq(20).all(), 'Visit support')
        pool[(proto, side)] = d
        if side == 'post':
            train = pd.read_parquet(OLD/'packages/outer/f0'/proto/'fit-post-hist.parquet')
            query = pd.read_parquet(OLD/'packages/outer/f0'/proto/'query-post-hist.parquet')
            train['visit_id'] = train.session_id.map(visitid)
            prior = pd.concat([train[['visit_id', *HIST]], query]).set_index('visit_id').loc[d.visit_id]
            replay = max(replay, float(np.max(np.abs(prior[HIST].to_numpy()-d[HIST].to_numpy()))))
    require(replay < 1e-14, 'Post histogram replay')
    packages = {}; mainroles = []; diagroles = []; kernelroles = {}; roleaudits = []
    def store(frame, path, kind, scope):
        save(frame, path); packages[rel(path)] = {'sha256': sha(path), 'kind': kind,
            'columns': list(frame), 'rows': len(frame), 'scope': scope}
    def contents(excluded): return sorted(folds[~folds.fold.isin(excluded)].content_id)
    def hist(protocols, side, allowed):
        d = pd.concat([pool[(p, side)] for p in protocols], ignore_index=True)
        return d[d.content_id.isin(allowed)].sort_values(['protocol', 'visit_id']).reset_index(drop=True)
    # Diagnostic training packages are source-only and physically separated from labels/test pairs.
    for outer in range(5):
      for p in PROTOCOLS:
        for kind in ['pre', 'postmix']:
          sources = [p] if kind == 'pre' else [s for s in PROTOCOLS if s != p]
          for inner in [None]+[i for i in range(5) if i != outer]:
            rid = f"diagnostics/{kind}/f{outer}/{p}/"+('outer' if inner is None else f'i{inner}')
            tr = contents([outer]+([] if inner is None else [inner])); held = outer if inner is None else inner
            va = sorted(folds[folds.fold.eq(held)].content_id)
            r = {'id': rid, 'kind': kind, 'outer': outer, 'inner': inner, 'protocol': p,
                 'sources': sources, 'train_contents': tr, 'validation_contents': va}
            root = rolepath(r); train = hist(sources, 'pre' if kind == 'pre' else 'post', tr)
            store(train, root/'train.parquet', 'diag-train', r)
            qp = PROTOCOLS if kind == 'pre' and inner is None else ([p] if inner is None else sources)
            for target in qp:
                v = hist([target], 'pre' if kind == 'pre' else 'post', va)
                store(v[['visit_id', *HIST]], root/f'query-{target}.parquet', 'diag-query', r)
                store(v[['visit_id', 'content_id', 'label_id', 'protocol']], root/f'labels-{target}.parquet',
                      'diag-outer-labels' if inner is None else 'diag-inner-labels', r)
            diagroles.append(r)
        # Frozen post matrix queries; read only during diagnostic inference/scoring.
        for target in PROTOCOLS:
            v = hist([target], 'post', sorted(folds[folds.fold.eq(outer)].content_id))
            base = OUT/'packages/diagnostics/post'/f'f{outer}'/target
            store(v[['visit_id', *HIST]], base/'query.parquet', 'diag-query', {'outer': outer, 'target': target})
            store(v[['visit_id', 'content_id', 'label_id', 'protocol']], base/'labels.parquet',
                  'diag-outer-labels', {'outer': outer, 'target': target})
            # Create once per target/outer, rather than copy for each matrix source.
            raw = df[df.protocol.eq(target)&df.fold.eq(outer)]
            store(raw[['visit_id', 'content_id', 'label_id', *native]], base/'test-paired.parquet',
                  'diag-test-paired', {'outer': outer, 'target': target})
    for outer in range(5):
      for target in PROTOCOLS:
       for group, missing in MASKS.items():
        actualsources = [s for s in PROTOCOLS if s != target]
        configurations = [(None, target, actualsources)]
        configurations += [(i, pseudo, [s for s in actualsources if s != pseudo])
                           for i in range(5) if i != outer for pseudo in actualsources]
        for inner, calibration, sources in configurations:
            rid = f"main/f{outer}/{target}/{group}/"+('outer' if inner is None else f'i{inner}/{calibration}')
            tr = contents([outer]+([] if inner is None else [inner])); held = outer if inner is None else inner
            va = sorted(folds[folds.fold.eq(held)].content_id)
            C = sorted(folds[folds.content_id.isin(tr)&~folds.label_id.isin([LABELS[y] for y in missing])].content_id)
            U = sorted(set(tr)-set(C))
            require(not set(tr)&set(va) and not any(foldmap[u] == outer for u in tr), 'Global content isolation')
            r = {'id': rid, 'outer': outer, 'inner': inner, 'target': target, 'calibration': calibration,
                 'sources': sources, 'group': group, 'missing': missing, 'train_contents': tr,
                 'C_contents': C, 'U_contents': U, 'validation_contents': va}
            root = rolepath(r)
            for side in ['post', 'pre']:
                d = hist(sources, side, tr)
                if side == 'pre':
                    # No shared visit identity; class/domain weighted loss does not require correspondence.
                    d = d.drop(columns='visit_id').sort_values(['protocol', 'label_id', *HIST]).reset_index(drop=True)
                store(d, root/f'source-{side}.parquet', 'source-'+side, r)
            cp = hist([calibration], 'post', C)
            store(cp, root/'C-post.parquet', 'C-post', r)
            v = hist([calibration], 'post', va)
            store(v[['visit_id', *HIST]], root/'query.parquet', 'main-query', r)
            store(v[['visit_id', 'content_id', 'label_id', 'protocol']], root/'labels.parquet',
                  'main-outer-labels' if inner is None else 'main-inner-labels', r)
            if inner is None:
                raw = df[df.protocol.eq(target)&df.content_id.isin(va)]
                store(raw[['visit_id', 'content_id', 'label_id', *native]], root/'test-paired.parquet', 'main-test-paired', r)
            kid = kernelid(r); r['kernel_id'] = kid
            if kid not in kernelroles:
                kr = {k: r[k] for k in ['outer', 'inner', 'calibration', 'group', 'missing', 'C_contents']}
                kr['id'] = kid; kernelroles[kid] = kr; path = OUT/'packages/C-kernels'/kid
                raw = df[df.protocol.eq(calibration)&df.content_id.isin(C)].sort_values('pair_id')
                paired = raw[['pair_id', 'content_id', *native]].copy()
                paired['fit_mass'] = raw.content_visit_flow_mass.to_numpy()
                require(abs(paired.fit_mass.sum()-len(C)) < 1e-10, 'C-only mass')
                store(paired, path/'paired.parquet', 'C-paired', kr)
                for side, seed in [('pre', 103), ('post', 209)]:
                    d = paired[['content_id', 'fit_mass', *[side+'_'+f for f in FEATURES]]]
                    d = d.sample(frac=1, random_state=seed).reset_index(drop=True)
                    store(d, path/f'group-{side}.parquet', 'C-group-'+side, kr)
            elif kernelroles[kid]['C_contents'] != C: raise RuntimeError('Kernel cache member collision')
            require(len(cp) == (64 if inner is None else 48), 'Calibration visit count')
            require(set(cp.content_id) == set(C) and not set(cp.content_id)&set(U), 'Target U package leak')
            if inner is not None: require(target not in sources+[calibration], 'Actual target in inner selection')
            mainroles.append(r)
            roleaudits.append({'id': rid, 'sources': sources, 'calibration': calibration,
                              'C_visits': len(cp), 'forbidden_U_visits': len(U)*4, 'content_overlap': 0})
    require(len(diagroles) == 200 and len(mainroles) == 780 and len(kernelroles) == 300, 'Role counts')
    save(folds, OUT/'manifests/content-folds.parquet')
    write(OUT/'manifests/input-inventory.json', {'sha256': baseline, 'raw_capture_reads': 0})
    write(OUT/'manifests/reused-post-models.json', reused)
    write(OUT/'manifests/role-registry.json', {'diagnostics': diagroles, 'main': mainroles,
                                            'kernels': list(kernelroles.values())})
    write(OUT/'manifests/package-manifest.json', packages)
    write(OUT/'manifests/cohort-audit.json', {'pairs': 23566, 'visits': 480, 'contents': 30,
        'repetitions': [1, 2, 3, 4], 'registered_entity_crossfold_overlap': 0,
        'universal_TCP_epoch_proof': False, 'post_histogram_max_error': replay})
    write(OUT/'manifests/role-audit.json', roleaudits)
    write(OUT/'manifests/isolation-audit.json', {'registered_entity_crossfold_overlap': 0,
        'universal_TCP_epoch_proof': False, 'main_inner_actual_target_used': False,
        'target_U_package_numeric_rows': 0, 'role_audit_sha256': sha(OUT/'manifests/role-audit.json')})
    write(OUT/'manifests/environment.json', {'python': platform.python_version(), 'torch': torch.__version__,
        'cuda': torch.version.cuda, 'gpu': torch.cuda.get_device_name(0), 'dtype': 'float64',
        'device': 'cuda:0', 'CPU_fallback': False, 'Arrow_before_torch': True, 'TF32': False})
    complete(OUT/'manifests/preparation-complete.json', packages=len(packages), main_roles=len(mainroles),
             diagnostic_roles=len(diagroles), kernel_roles=len(kernelroles), post_histogram_max_error=replay)
    progress('CT00_CT05_prepared', packages=len(packages), main_roles=len(mainroles))

def register():
    require(not (OUT/'manifests/experiment-contract.json').exists(), 'Contract already sealed')
    require(read(OUT/'manifests/unit-tests.json')['passed'], 'Tests required before registration')
    rr = read(OUT/'manifests/role-registry.json'); pm = read(OUT/'manifests/package-manifest.json')
    audit = read(OUT/'manifests/cohort-audit.json')
    require(audit['registered_entity_crossfold_overlap'] == 0, 'Isolation gate')
    write(OUT/'manifests/isolation-audit.json', {'registered_entity_crossfold_overlap': 0,
        'universal_TCP_epoch_proof': False, 'main_inner_actual_target_used': False,
        'target_U_package_numeric_rows': 0, 'role_audit_sha256': sha(OUT/'manifests/role-audit.json')})
    require(len(rr['main']) == 780 and len(rr['kernels']) == 300 and len(rr['diagnostics']) == 200, 'Registry size')
    for p, info in pm.items(): require(sha(ROOT/p) == info['sha256'], 'Pre-register package changed')
    visits = pd.read_parquet(Q/'features/paired-flow-features.parquet', columns=['session_id', 'protocol', 'content_id', 'fold'])
    visits = visits.drop_duplicates().sort_values(['protocol', 'session_id']).reset_index(drop=True)
    require(len(visits) == 480 and visits.session_id.is_unique, 'Observation inventory cohort')
    save(visits, OUT/'manifests/cohort-visits.parquet')
    files = list(Path(__file__).parent.glob('*.py'))+[Path(__file__).parent/'README.md']
    write(OUT/'manifests/experiment-contract.json', {'version': 'CT-v1', 'registered_unix': time.time(),
        'plan_sha256': sha(PLAN), 'source_sha256': {rel(p): sha(p) for p in files}, 'packages': pm,
        'cohort_visits_sha256': sha(OUT/'manifests/cohort-visits.parquet'),
        'baseline_sha256': read(OUT/'manifests/input-inventory.json')['sha256'], **rr,
        'protocols': PROTOCOLS, 'labels': LABELS, 'features': FEATURES, 'histogram_columns': HIST,
        'masks': MASKS, 'arms': ARMS, 't_grid': TS, 'rho': '.001*(1+t)',
        'expected_new_fits': 15380, 'main_inner_fits': 14400, 'main_outer_fits': 300,
        'source_main_aux_C_mass': [1/3, 1/3, 1/3], 'class_mass': 1/6,
        'kernel': {'content_mass': 1, 'visit_mass': .25, 'alpha': 1, 'beta': 1},
        'coral_diagonal_regularization': 1, 'scaler': 'unweighted unique source-post plus C-post; population std',
        'primary_comparators': ['StrongPost', 'CT1', 'CT3'],
        'bootstrap': {'samples': 10000, 'seed': 20261005, 'unit': '30 business-stratified contents', 'family': 3},
        'safety_screen': {'pooled_aux_margin': -.02, 'worst_target_aux_margin': -.05,
                          'statistical_noninferiority_claimed': False},
        'user_authorization': '2026-10-06 user approved execution of the saved plan',
        'permission_whitelist_not_OS_sandbox': True, 'test_pre_after_prediction_seal_only': True,
        'optimizer': {'max_iter': 500, 'tolerance_grad': 1e-9, 'tolerance_change': 1e-12,
                      'line_search': 'strong_wolfe', 'gradient_gate': 1e-5},
        'stage3_external_window_and_full_physical_cache_not_yet_verified': True})
    progress('CT07_registered', new_fits=15380, source_files=len(files))

if __name__ == '__main__':
    import sys
    {'prepare': run, 'register': register}[sys.argv[1]]()
