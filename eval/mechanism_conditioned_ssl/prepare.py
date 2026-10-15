"""Build independent, label-free SSL packages from sealed P3 cross-fit centers."""
import platform
import subprocess
from common import *


def canonical(frame):
    return frame.sort_values(['protocol', 'content_id', *W, 'session_id']).reset_index(drop=True)


def anon(frame, side, conditions=None):
    f = pd.DataFrame({'row_token': [digest([side, s]) for s in frame.session_id],
                      'deployment': frame.protocol.tolist(),
                      'group_id': [digest(['content', c]) for c in frame.content_id]})
    f[W] = frame[W].to_numpy()
    if conditions is not None: f[M] = conditions
    return f


def main():
    cli(__doc__).parse_args(); device()
    if (OUT/'seal.json').exists(): authorize(False); print('prepared and sealed; no overwrite'); return
    assert not OUT.exists(), 'partial preparation exists; preserve it for diagnosis'
    oldseal = read(OLD/'seal.json')
    assert read(OLD/'independent-verification.json')['passed']
    assert read(OLD/'qualification.json')['passed']
    for n, h in oldseal['hashes'].items(): assert sha(ROOT/n) == h
    assert sha(OLD/'model-contract.json') == oldseal['contract_sha256']
    cohort = pd.read_parquet(OLD/'cohort.parquet')
    assert len(cohort) == 600 and cohort.session_id.is_unique
    assert cohort.groupby('content_id').fold.nunique().eq(1).all()
    assert cohort.groupby(['protocol', 'content_id']).size().eq(4).all()
    assert cohort.groupby('content_id').label_id.nunique().eq(1).all()
    jobs = [read(p) for p in sorted((OLD/'generator-roles').glob('*.json'))]
    assert len(jobs) == 100
    OUT.mkdir(parents=True)
    hashes = {str(p.relative_to(ROOT)): sha(p) for p in CODE.glob('*.py')}
    for p in [PLAN, ROOT/'docs/mechanism-conditioned-ssl-extend/experiment-contract.md',
              OLD/'seal.json', OLD/'model-contract.json', OLD/'cohort.parquet',
              OLD/'independent-verification.json', OLD/'qualification.json',
              ROOT/'eval/hy2_carrier_calibration/window_model.py']:
        hashes[str(p.relative_to(ROOT))] = sha(p)
    cohort.to_parquet(OUT/'cohort.parquet', index=False)
    classes = sorted(cohort.label_id.unique().tolist()); assert len(classes) == 6
    provenance, allconditions = [], []; sourcechecks = 0; pre_registry = {}
    for fold in range(5):
        role = read(OLD/'roles'/f'E1-all-f{fold}.json')
        train, test = set(role['train']), set(role['test'])
        assert not train & test and len(train) == 480 and len(test) == 120
        tr = cohort[cohort.session_id.isin(train)]; te = cohort[cohort.session_id.isin(test)]
        assert set(tr.content_id).isdisjoint(te.content_id)
        premap, centers = {}, {a: {} for a in CENTERS}
        for job in jobs:
            if job['fold'] != fold: continue
            fitids, queryids = set(job['fit_sessions']), set(job['query_sessions'])
            assert not fitids & queryids and fitids | queryids <= train
            fitcontents = set(cohort.loc[cohort.session_id.isin(fitids), 'content_id'])
            querycontents = set(cohort.loc[cohort.session_id.isin(queryids), 'content_id'])
            assert not fitcontents & querycontents and len(fitcontents) == 18 and len(querycontents) == 6
            folder = OLD/'packages/generator-paired'/job['job']
            q = source_frame(folder, 'query_pre')
            assert set(q.session_id) == queryids
            for row in q.to_dict('records'):
                sid = row['session_id']; assert sid not in premap; premap[sid] = row
                if sid in pre_registry: assert pre_registry[sid] == row
                pre_registry[sid] = row
            for arm, oldarm in CENTERS.items():
                d = OLD/'generation'/job['job']/oldarm; done = read(d/'complete.json')
                assert done['seal_sha256'] == sha(OLD/'seal.json')
                assert set(done['fit_sessions']) == fitids and set(done['query_sessions']) == queryids
                assert done['query_post_reads'] == 0 and done['test_reads'] == 0
                for fname in ['distribution.npz', 'model.pt']:
                    assert sha(d/fname) == done['files'][fname]
                    hashes[str((d/fname).relative_to(ROOT))] = sha(d/fname)
                with np.load(d/'distribution.npz', allow_pickle=False) as x:
                    assert set(x['session_ids']) == queryids and x['raw_center'].shape == (24, 6)
                    validate(x['raw_center'])
                    for sid, v in zip(x['session_ids'].tolist(), x['raw_center']):
                        assert sid not in centers[arm]; centers[arm][sid] = v.copy()
                        provenance.append({'fold': fold, 'arm': arm, 'job': job['job'], 'session_id': sid,
                                           'query_content': cohort.set_index('session_id').loc[sid, 'content_id'],
                                           'fit_content_count': 18, 'fit_sessions_hash': digest(sorted(fitids)),
                                           'center_sha256': sha(d/'distribution.npz'), 'query_post_read': False})
                sourcechecks += 1
            for p in [folder/'manifest.json', folder/'query_pre.parquet',
                      OLD/'generator-roles'/(job['job']+'.json')]:
                hashes[str(p.relative_to(ROOT))] = sha(p)
        assert set(premap) == train and all(set(v) == train for v in centers.values())
        post = canonical(source_frame(OLD/'packages/training'/role['scenario'], 'post'))
        pre = pd.DataFrame([premap[s] for s in post.session_id])
        pre['protocol'] = post.protocol.tolist()
        assert (pre.content_id.to_numpy() == post.content_id.to_numpy()).all()
        a = pre[W].to_numpy(float); validate(a); validate(post[W].to_numpy(float))
        c1 = np.stack([centers['B4'][s] for s in post.session_id])
        c2 = np.stack([centers['B5'][s] for s in post.session_id])
        np.testing.assert_array_equal(c1[:, 2:], c2[:, 2:])
        np.testing.assert_array_equal(phi(c1)[:, :4].cpu(), phi(c2)[:, :4].cpu())
        scalers = {'post': fit_scale(post[W].to_numpy(float), True),
                   'pre': fit_scale(a, True), 'conditions': {}}
        rawdiffs, standardized = {}, {}
        for arm in CENTERS:
            cc = np.stack([centers[arm][s] for s in post.session_id])
            diff = (phi(cc)-phi(a)).cpu().numpy(); rawdiffs[arm] = diff
            scalers['conditions'][arm] = fit_scale(diff)
            standardized[arm] = scaled(diff, scalers['conditions'][arm]).cpu().numpy()
            for sid, raw, m in zip(post.session_id, diff, standardized[arm]):
                allconditions.append({'fold': fold, 'arm': arm, 'session_id': sid,
                                      **{f'delta{i}': v for i, v in enumerate(raw)},
                                      **dict(zip(M, m))})
        write(OUT/'scalers'/f'f{fold}.json', scalers)
        sup = pd.DataFrame({'session_id': post.session_id, 'deployment': post.protocol,
                            'group_id': [digest(['content', c]) for c in post.content_id],
                            'label_id': post.label_id})
        sup[W] = post[W].to_numpy()
        export(OUT/'packages'/f'f{fold}'/'supervised', {'post': sup})
        p_anon = anon(post, 'post')
        # Pre rows for no-correspondence arms independently ordered by pre values.
        order = canonical(pre).session_id.tolist(); idx = post.set_index('session_id')
        preind = pre.set_index('session_id').loc[order].reset_index()
        positions = {s: i for i, s in enumerate(post.session_id)}
        independent_idx = np.array([positions[s] for s in order])
        for arm in SSL:
            frames = {'post': p_anon}
            if arm in ['B2', 'B6']:
                cond = standardized[arm][independent_idx] if arm == 'B6' else None
                frames['pre'] = anon(preind, 'pre', cond)
            elif arm != 'B1':
                cond = standardized[arm] if arm in CENTERS else None
                frames['pre'] = anon(pre, 'pre', cond)
                # Paired token is authorized only in B3/B4/B5.
                frames['pre']['row_token'] = p_anon.row_token.tolist()
            export(OUT/'packages'/f'f{fold}'/arm, frames)
        inf = source_frame(OLD/'packages/inference'/role['scenario'], 'test_post')
        lab = source_frame(OLD/'packages/scoring'/role['scenario'], 'test_labels')
        assert set(inf.session_id) == test == set(lab.session_id)
        export(OUT/'packages'/f'f{fold}'/'inference', {'test_post': inf[['session_id', *W]]})
        export(OUT/'packages'/f'f{fold}'/'scoring', {'labels': lab[['session_id', 'label_id']]})
        write(OUT/'roles'/f'f{fold}.json', {'fold': fold, 'train': sorted(train), 'test': sorted(test),
                                         'train_contents': sorted(tr.content_id.unique()),
                                         'test_contents': sorted(te.content_id.unique())})
    assert sourcechecks == 300 and len(provenance) == len(allconditions) == 7200
    assert len(pre_registry) == 600
    for fold in range(5):
        role = read(OUT/'roles'/f'f{fold}.json'); diagnostic = {}
        for split in ['train', 'test']:
            ids = role[split]; pre = pd.DataFrame([pre_registry[s] for s in ids])
            meta = cohort.set_index('session_id').loc[ids]
            pre['protocol'] = meta.protocol.to_numpy()
            pp = pd.DataFrame({'session_id': pre.session_id, 'deployment': pre.protocol,
                               'group_id': [digest(['content', c]) for c in pre.content_id]})
            pp[W+AUX] = pre[W+AUX].to_numpy()
            post = source_frame(OLD/'packages'/('training' if split == 'train' else 'inference')/f'E1-all-f{fold}',
                                'post' if split == 'train' else 'test_post').set_index('session_id').loc[ids]
            bp = pp[['session_id', 'deployment', 'group_id']].copy(); bp[W] = post[W].to_numpy()
            diagnostic[split+'_pre'], diagnostic[split+'_post'] = pp, bp
        export(OUT/'packages'/f'f{fold}'/'diagnostic', diagnostic)
    pd.DataFrame(provenance).to_parquet(OUT/'center-provenance.parquet', index=False)
    pd.DataFrame(allconditions).to_parquet(OUT/'conditions-audit.parquet', index=False)
    write(OUT/'environment.json', {'python': platform.python_version(), 'torch': torch.__version__,
          'cuda': torch.version.cuda, 'gpu': torch.cuda.get_device_name(), 'numpy': np.__version__,
          'pandas': pd.__version__, 'conda_env': 'Pytorch312', 'cuda_memory': torch.cuda.mem_get_info()})
    commit = subprocess.check_output(['git', '-c', 'safe.directory='+ROOT.as_posix(),
                                      'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    write(OUT/'contract.json', {'version': 'mechanism-conditioned-ssl-E1-v1', 'date': '2026-10-04',
          'human_approval': '好的，请你先同步当前仓库，然后开始根据计划实施', 'git_commit': commit,
          'suite': 'E1', 'protocols': sorted(cohort.protocol.unique()), 'classes': classes,
          'features': W, 'seeds': SEEDS, 'arms': ARMS, 'SSL_sources': SSL, 'steps': 1000,
          'temperature': .2, 'lambda': 1., 'lr': .001, 'L2_weight': 5e-5,
          'encoder_parameters': 2528, 'inference_parameters': 3782,
          'center_coordinate': 'phi(decoded raw_center)-phi(query_pre), crossfit18/query6',
          'center_kind': CENTERS, 'batch': 120, 'masks_per_view': 1,
          'primary_references': PRIMARY, 'bootstrap_draws': 10000, 'bootstrap_seed': 20260928,
          'primary_quantiles': [.005, .995], 'E2_enabled': False,
          'classification_test_pre': False, 'test_selection': False, 'TF32': False,
          'registered_identity_limits_retained': True, 'universal_identity_proof': False,
          'fit_counts': {'SSL': 90, 'probe': 210, 'final': 120, 'diagnostic_centers': 75}})
    write(OUT/'qualification.json', {'passed': True, 'members': 600, 'global_contents': 30,
          'center_files': 300, 'condition_rows': 7200, 'query_content_excluded': True,
          'test_pre_exported_to_classification': False, 'group_shared_identity_exported': False,
          'D1_D2_nonbyte_exact': True, 'P3_identity_qualification_reused': True,
          'historical_unobserved_SYN_cases': 5, 'P2_preflight_exception_retained': True})
    for p in OUT.rglob('*'):
        if p.is_file(): hashes[str(p.relative_to(ROOT))] = sha(p)
    write(OUT/'seal.json', {'contract_sha256': sha(OUT/'contract.json'), 'hashes': hashes,
                            'production_requires_engineering': True, 'test_scores_read': False})
    print('Prepared: 600 visits, 300 sealed centers, 7200 conditions, five folds; no fit/test selection', flush=True)


if __name__ == '__main__': main()
