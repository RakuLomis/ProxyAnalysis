"""Reuse sealed E1 training conditions without reading diagnostic test-pre."""
import platform
from common import *


def main():
    device()
    if (OUT/'seal.json').exists(): authorize(False); print('already prepared; preserved'); return
    assert not OUT.exists(), 'preserve partial preparation for audit'
    oldseal = read(OLD/'seal.json')
    for n, h in oldseal['hashes'].items(): assert sha(ROOT/n) == h, n
    assert read(OLD/'independent-verification.json')['passed']
    assert read(OLD/'independent-score-check.json')['passed']
    assert read(OLD/'stopping-decision.json')['frozen']
    co = pd.read_parquet(OLD/'cohort.parquet')
    assert len(co) == 600 and co.session_id.is_unique and co.content_id.nunique() == 30
    assert co.groupby('content_id').fold.nunique().eq(1).all()
    assert co.groupby(['protocol', 'content_id']).size().eq(4).all()
    assert co.groupby('content_id').label_id.nunique().eq(1).all()
    q = read(OLD/'qualification.json'); assert q['center_files'] == 300 and q['condition_rows'] == 7200
    assert q['query_content_excluded'] and not q['test_pre_exported_to_classification']
    prov = pd.read_parquet(OLD/'center-provenance.parquet')
    assert len(prov) == 7200 and prov.fit_content_count.eq(18).all() and not prov.query_post_read.any()
    classes = sorted(co.label_id.unique().tolist()); OUT.mkdir(parents=True)
    co.to_parquet(OUT/'cohort.parquet', index=False)
    hashes = dict(oldseal['hashes'])
    for p in [OLD/'seal.json', OLD/'qualification.json', OLD/'independent-verification.json',
              OLD/'independent-score-check.json', OLD/'stopping-decision.json', OLD/'center-provenance.parquet',
              OLD/'conditions-audit.parquet', PLAN, DOC/'experiment-contract.md']:
        hashes[str(p.relative_to(ROOT))] = sha(p)
    for name in FIT_FILES: hashes[str((CODE/name).relative_to(ROOT))] = sha(CODE/name)
    audits = []
    for fold in range(5):
        role = read(OLD/'roles'/f'f{fold}.json'); tr, te = set(role['train']), set(role['test'])
        assert len(tr) == 480 and len(te) == 120 and not tr & te
        assert set(role['train_contents']).isdisjoint(role['test_contents'])
        sup = source_frame(OLD/'packages'/f'f{fold}'/'supervised', 'post')
        assert set(sup.session_id) == tr
        post = sup.rename(columns={'session_id': 'row_token'}).copy()
        post.row_token = [digest(['post', sid]) for sid in sup.session_id]
        assert list(post) == ['row_token', 'deployment', 'group_id', 'label_id', *W]
        expected_y = {(p, digest(['content', c])): y for p, c, y in
                      co.loc[co.session_id.isin(tr), ['protocol', 'content_id', 'label_id']].itertuples(index=False, name=None)}
        for arm in ARMS:
            frames = {'post': post.copy()}
            if arm not in ['J0', 'J7']:
                oldarm = CONDITIONS.get(arm, 'B3')
                bp = source_frame(OLD/'packages'/f'f{fold}'/oldarm, 'post')
                pre = source_frame(OLD/'packages'/f'f{fold}'/oldarm, 'pre')
                assert np.array_equal(bp[W], post[W]) and list(bp.row_token) == list(post.row_token)
                pre['label_id'] = [expected_y[k] for k in zip(pre.deployment, pre.group_id)]
                cols = ['row_token', 'deployment', 'group_id', 'label_id', *W]+(M if arm in CONDITIONS else [])
                pre = pre[cols].copy()
                if arm == 'J5':
                    assert set(pre.row_token).isdisjoint(post.row_token)
                    # No common visit identity survives. Independently shuffle both sides.
                    pre = pre.drop(columns='row_token').sample(frac=1, random_state=20261004+fold).reset_index(drop=True)
                    frames['post'] = post.drop(columns='row_token').sample(frac=1, random_state=20261014+fold).reset_index(drop=True)
                    assert set(pre.groupby(['deployment', 'group_id']).size()) == {4}
                    assert set(frames['post'].groupby(['deployment', 'group_id']).size()) == {4}
                else:
                    assert list(pre.row_token) == list(post.row_token)
                    assert list(pre.label_id) == list(post.label_id)
                frames['pre'] = pre
            export(OUT/'packages'/f'f{fold}'/arm, frames)
            audits.append({'fold': fold, 'arm': arm, 'files': sorted(frames), 'has_common_identity': arm in ['J1', 'J2', 'J3', 'J4', 'J6'],
                           'pre_rows': len(frames.get('pre', [])), 'post_rows': len(frames['post'])})
        spec = read(OLD/'scalers'/f'f{fold}.json')
        fresh = fit_scale(sup[W].to_numpy(float), True)
        assert digest(fresh) == digest(spec['post'])
        paired_pre = source_frame(OLD/'packages'/f'f{fold}'/'B3', 'pre')
        assert digest(fit_scale(paired_pre[W].to_numpy(float), True)) == digest(spec['pre'])
        write(OUT/'scalers'/f'f{fold}.json', spec)
        for capability, key in [('inference', 'test_post'), ('scoring', 'labels')]:
            frame = source_frame(OLD/'packages'/f'f{fold}'/capability, key)
            assert set(frame.session_id) == te
            export(OUT/'packages'/f'f{fold}'/capability, {key: frame})
        write(OUT/'roles'/f'f{fold}.json', role)
    prov.to_parquet(OUT/'condition-provenance.parquet', index=False)
    write(OUT/'package-audit.json', audits)
    write(OUT/'environment.json', {'python': platform.python_version(), 'torch': torch.__version__,
          'cuda': torch.version.cuda, 'GPU': torch.cuda.get_device_name(), 'conda': 'Pytorch312',
          'free_total_cuda_bytes': torch.cuda.mem_get_info()})
    write(OUT/'source-seal.json', {'E1_seal': sha(OLD/'seal.json'), 'E1_frozen': True,
          'E1_prediction': sha(OLD/'oof.parquet'), 'E2_started': False,
          'source_hashes': dict(oldseal['hashes'])})
    write(OUT/'contract.json', {'version': 'post-anchored-paired-J-v1', 'date': '2026-10-04',
          'approval': '好的，请你根据计划开始实现', 'arms': ARMS, 'main': 'J4', 'protocols': sorted(co.protocol.unique()),
          'classes': classes, 'features': W, 'seeds': SEEDS, 'steps': 2000, 'Adam_reset_at': 1000,
          'temperature': 2., 'transfer_coefficient': .5, 'L2_sum_coefficient': 5e-5,
          'lr': .001, 'batch': 120, 'inference_parameters': 3782, 'condition_parameters': 192,
          'conditional_training_parameters': 3974, 'primary_references': PRIMARY,
          'bootstrap_draws': 10000, 'bootstrap_seed': 20260928,
          'primary_quantiles': [.05/12, 1-.05/12], 'post_root_exposures': 500,
          'aux_exposures': 500, 'fit_tasks': 120, 'smoke_tasks': 8,
          'test_pre': False, 'E2': False, 'test_selection': False, 'unlabeled_SSL': False,
          'online_shared_teacher': True, 'fixed_independent_teacher': False,
          'CUDA_required': True, 'TF32': False, 'AMP': False})
    write(OUT/'qualification.json', {'passed': True, 'visits': 600, 'contents': 30,
          'center_files_reused': 300, 'condition_rows_reused': 7200, 'query_content_excluded': True,
          'train_test_content_disjoint': True, 'group_common_identity': False,
          'diagnostic_test_pre_read': False, 'physical_identity_registration_reused': True,
          'historical_unobserved_SYN_cases': 5, 'P2_preflight_limit_retained': True})
    for p in OUT.rglob('*'):
        if p.is_file(): hashes[str(p.relative_to(ROOT))] = sha(p)
    write(OUT/'seal.json', {'contract_sha256': sha(OUT/'contract.json'), 'hashes': hashes,
          'scores_read': False, 'new_fit_files': FIT_FILES})
    print('Prepared 600 visits, 5 folds, 8 separated capabilities; 300 centers/7200 conditions reused', flush=True)


if __name__ == '__main__': main()
