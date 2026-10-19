"""P0: manifest-driven bindings, no query-post or label decoding."""
from .common import *


def run():
    configure()
    need(not (OUT / 'seal.json').exists(), 'SD1 inventory already sealed')
    started = time.perf_counter()
    completion = read(PARENT / 'completion.json')
    need(completion['status'] == 'stop_no_supported_protection_target', 'Historical stop changed')
    need(sha(PARENT / 'stage-1-verification.json') == completion['verification_sha256'], 'Old verification hash')
    pv = read(PARENT / 'stage-1-verification.json')
    pcpath = PARENT / 'manifests/experiment-contract.json'
    need(sha(pcpath) == read(pcpath.with_name('seal.json'))['contract_sha256'], 'Old contract changed')
    pc = read(pcpath)
    ix = read(PARENT / 'packages/index.json')
    need(sha(PARENT / 'packages/index.json') == read(PARENT / 'packages/complete.json')['index_sha256'], 'Old package seal')
    forecasts = read(PARENT / 'diagnostics/predictions-complete.json')['files']
    tcpath = TI / 'manifests/experiment-contract.json'
    need(sha(tcpath) == pc['fixed_files'][rel(tcpath)], 'Source metadata manifest not authenticated')
    tc = read(tcpath)
    close = read(CLOSE / 'completion.json')
    need(close['parent_stop_preserved'] and sha(CLOSE / 'verification.json') == close['verification_sha256'], 'Closeout integrity')
    files = {}

    def add(path, expected=None, **info):
        path = Path(path)
        key = rel(path)
        h = sha(path)
        expected = expected or pv['files'].get(key)
        need(expected is not None and expected == h, 'Unsealed/changed historical input: ' + key)
        files[key] = {'sha256': h, **info}
        return key

    for path in [PARENT / 'completion.json', PARENT / 'stage-1-verification.json',
                 CLOSE / 'completion.json', CLOSE / 'verification.json']:
        add(path, sha(path), kind='historical-terminal')
    for path in [pcpath, pcpath.with_name('seal.json'), PARENT / 'packages/index.json',
                 PARENT / 'packages/complete.json', PARENT / 'diagnostics/predictions-complete.json',
                 PARENT / 'audits/C-splits.parquet', PARENT / 'diagnostics/accepted-maps.parquet']:
        add(path, kind='historical-manifest')
    add(tcpath, pc['fixed_files'][rel(tcpath)], kind='historical-manifest')
    for p, h in pc['source_sha256'].items():
        add(ROOT / p, h, kind='historical-code')
    engineering_history = []
    previous_runs = ['run-01', 'run-02'][:int(RUN_ID[-2:])-1]
    prior_budget = {'active_compute_seconds': 0., 'limit_seconds': 1800., 'segments': []}
    for previous_run in previous_runs:
        previous = OUT.parent/previous_run
        old_stop = read(previous/'completion.json')
        stop_stage = 'P1' if previous_run == 'run-01' else 'P3'
        need(not old_stop['program_complete'] and old_stop['pending_stages'][0] == stop_stage, 'Unexpected prior SD1 state')
        for path in [previous/'contract.json', previous/'seal.json', previous/'completion.json']:
            add(path, sha(path), kind='historical-SD1-engineering-stop')
        for path in (previous/'source-snapshot').glob('*.py'):
            oldc = read(previous/'contract.json')
            expected = oldc['source_sha256']['eval/subblock_drift_diagnostics/'+path.name]
            add(path, expected, kind='historical-SD1-code-snapshot')
        prior = read(previous/'budget.json')
        # run-02 did not inherit run-01's tiny failed-test segment; charge both once.
        prior_budget['active_compute_seconds'] += prior['active_compute_seconds']
        prior_budget['segments'].extend([{**s, 'historical_run': previous_run} for s in prior['segments']])
        engineering_history.append({'run': previous_run, 'status': old_stop['status'],
                                    'stopped_stage': stop_stage, 'query_post_decoded': False,
                                    'cause': ('CUDA cumsum not deterministic in installed PyTorch' if previous_run == 'run-01'
                                              else 'label_id contains nominal strings, not integer IDs'),
                                    'revision': ('same prefix sum via fixed triangular CUDA float64 matrix' if previous_run == 'run-01'
                                                 else 'preserve nominal label string; clarify independent verification batch/row counts'),
                                    'scientific_model_loss_threshold_permissions_changed': False})
    roles, bindings, members, registration_reads = [], [], [], []
    for original in pc['roles']:
        r = {k: original[k] for k in ['id', 'target', 'outer', 'group', 'eta', 'C_contents', 'C_diagnostic_contents']}
        need(not set(original['C_contents']) & set(original['U_contents']), 'C/U overlap')
        need(not set(original['train_contents']) & set(original['validation_contents']), 'Train/H content overlap')
        need(sorted(sum(r['C_diagnostic_contents'], [])) == sorted(r['C_contents']), 'Internal fold coverage')
        metadata_path = next((p for p, v in tc['packages'].items()
                              if v['kind'] == 'C-post' and v['scope'].get('id') == r['id']), None)
        need(metadata_path is not None, 'No authenticated role C metadata package')
        mi = tc['packages'][metadata_path]
        need(mi['rows'] == 64 and set(mi['scope']['C_contents']) == set(r['C_contents']), 'C metadata scope')
        r['metadata_ref'] = add(ROOT / metadata_path, mi['sha256'], kind='C-metadata', role_id=r['id'],
                                columns=mi['columns'], rows=mi['rows'])
        seen_queries = set()
        for i, held in enumerate(r['C_diagnostic_contents']):
            train_tokens = sorted({token(u) for u in r['C_contents']} - {token(u) for u in held})
            query_tokens = sorted(token(u) for u in held)
            root = PARENT / 'packages' / r['id'] / f'i{i}'
            dest = PARENT / 'diagnostics' / r['id'] / f'i{i}'
            refs = {}
            for fn in ['P-fit.parquet', 'P-query.parquet', 'P-score.parquet',
                       'G-pre-fit.parquet', 'G-post-fit.parquet', 'G-pre-validation.parquet']:
                p = root / fn
                info = ix[rel(p)]
                add(p, info['sha256'], **{k: v for k, v in info.items() if k != 'sha256'}, role_id=r['id'])
                refs[fn] = rel(p)
            # P0 only decodes membership columns. Query-post remains sealed.
            for fn in ['P-fit.parquet', 'G-pre-fit.parquet', 'G-post-fit.parquet', 'P-query.parquet']:
                p = root / fn
                cols = ['content_token', 'query_key'] if fn == 'P-query.parquet' else ['content_token', 'fit_mass']
                d = pd.read_parquet(p, columns=cols)
                fit = fn != 'P-query.parquet'
                expected_tokens = train_tokens if fit else query_tokens
                need(len(d) == (48 if fit else 16) and set(d.content_token) == set(expected_tokens), 'Fold membership mismatch')
                need(d.groupby('content_token').size().eq(4).all(), 'Repeat count mismatch')
                if fit:
                    need(np.allclose(d.fit_mass, 1/48, rtol=0, atol=1e-15), 'Original fit mass')
                else:
                    need(not seen_queries & set(d.query_key), 'Query repeated across internal folds')
                    seen_queries.update(d.query_key)
                    for row, q in d.iterrows():
                        members.append({'role_id': r['id'], 'deployment': r['target'], 'outer': r['outer'],
                                        'group': r['group'], 'inner': i, 'row': row, 'query_key': q.query_key,
                                        'content_token': q.content_token, 'weight_deployment': 1/960})
                registration_reads.append({'path': rel(p), 'purpose': 'P0-membership', 'role_id': r['id'],
                                           'columns_decoded': cols, 'numeric_decode': False})
            need(set(ix[refs['P-score.parquet']]['content_tokens']) == set(query_tokens), 'Score member manifest mismatch')
            scaler = add(root / 'scaler.pt', kind='scale', role_id=r['id'])
            sm = read(root / 'scaler.json')
            add(root / 'scaler.json', kind='tensor-metadata', role_id=r['id'])
            need(sm['source_post_rows'] == 240 and sm['C_post_rows'] == 48 and not sm['validation_post_used'], 'Scaler scope')
            for arm in ['P', 'G']:
                mp = dest / f'{arm}-map.pt'
                meta = read(mp.with_suffix('.json'))
                log = meta['mapping']
                need(log['accepted'] and log['eta'] == r['eta'] and log['device'] == 'cuda:0' and log['dtype'] == 'float64', 'Old map not comparable')
                need(log['gradient_max'] <= 1e-8 and log['objective_replay_error'] < 1e-10
                     and log['gradient_replay_error'] < 1e-10 and log['normalized_equation_residual'] <= 1e-10,
                     'Old numerical acceptance changed')
                map_ref = add(mp, meta['sha256'], kind='map', role_id=r['id'])
                add(mp.with_suffix('.json'), kind='tensor-metadata', role_id=r['id'])
                fp = dest / f'{arm}-predictions.pt'
                forecast_ref = add(fp, forecasts[rel(fp)], kind='old-forecast', role_id=r['id'])
                add(fp.with_suffix('.json'), kind='tensor-metadata', role_id=r['id'])
                bindings.append({'role_id': r['id'], 'deployment': r['target'], 'outer': r['outer'],
                                 'group': r['group'], 'inner': i, 'arm': arm, 'eta': r['eta'],
                                 'map_ref': map_ref, 'scale_ref': scaler, 'old_forecast_ref': forecast_ref,
                                 'train_content_tokens': train_tokens, 'query_content_tokens': query_tokens,
                                 **{k.replace('.parquet', '').replace('-', '_') + '_ref': v for k, v in refs.items()}})
        need(len(seen_queries) == 64, 'C coverage incomplete')
        roles.append(r)
    need(len(roles) == 60 and len(bindings) == 480 and len(members) == 3840, 'SD1 matrix dimensions')
    source = {rel(p): sha(p) for p in Path(__file__).parent.glob('*.py')}
    c = {'version': 'SD1-v1.2-nominal-label-metadata', 'engineering_history': engineering_history,
         'roles': roles, 'files': files, 'source_sha256': source,
         'plan_sha256': sha(PLAN), 'hist': HIST, 'sizes': SIZES, 'features': FEATURES,
         'projector_tolerance': TOL, 'scale_min': SCALE_MIN, 'activity_limit_seconds': 1800,
         'bootstrap': {'replicates': 10000, 'seed': 20261015, 'strata': 6, 'contents_per_stratum': 5,
                       'fixed_models_and_summaries': True, 'corrected_family': False},
         'new_model_fits': 0, 'max_summary_estimates': 240, 'actual_H_allowed': False, 'actual_U_allowed': False,
         'historical_eta_selection_not_fully_independent_of_C_content': True,
         'common_query_policy': 'P-query pre numerics to both frozen maps; evaluator alone matches P-score',
         'counterfactuals': VIEWS, 'predictors': PREDICTORS,
         'screen': {'outer_folds_min': 4, 'positive_contents_min_each_gain': 2,
                    'block_complete_error_for_N': True, 'authorize_training': False},
         'environment': {'python': sys.executable, 'torch': torch.__version__, 'cuda': torch.version.cuda,
                         'gpu': torch.cuda.get_device_name(0), 'numeric_dtype': 'float64', 'CPU_fallback': False},
         'parent_completion': completion}
    write(OUT / 'contract.json', c)
    write(OUT / 'seal.json', {'contract_sha256': sha(OUT / 'contract.json')})
    if RUN_ID == 'run-03':
        write(OUT/'budget.json', prior_budget)
    save(pd.DataFrame(bindings), 'source-bindings')
    save(pd.DataFrame(members), 'role-membership')
    write(OUT / 'ledgers/P0.json', {'reads': registration_reads, 'hash_only_files': len(files),
                                   'seconds': time.perf_counter() - started, 'score_numeric_reads': 0})
    write(OUT / 'stages/P0.json', {'complete': True, 'seconds': time.perf_counter() - started,
                                 'binding_sha256': sha(OUT / 'source-bindings.parquet'),
                                 'membership_sha256': sha(OUT / 'role-membership.parquet')})
    progress('P0_complete', roles=60, maps=480, dependencies=len(files), gpu=c['environment']['gpu'])
