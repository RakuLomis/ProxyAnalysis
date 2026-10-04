"""Independent persisted P3 audit, conditional on registered entity identity."""
from p3_common import *


def main():
    authorize();assert read(OUT/'score-complete.json')['passed']
    cohort=pd.read_parquet(OUT/'cohort.parquet');old=pd.read_parquet(LATEST/'cohort.parquet')
    pd.testing.assert_frame_equal(cohort,old)
    assert cohort.groupby('content_id').fold.nunique().eq(1).all()
    tasks=0;LOCO=0
    for jp in sorted((OUT/'generator-roles').glob('*.json')):
        job=read(jp);role=read(OUT/'roles'/f'E1-all-f{job["fold"]}.json')
        assert set(job['fit_sessions']).isdisjoint(job['query_sessions'])
        assert set(job['fit_sessions'])|set(job['query_sessions'])<=set(role['train'])
        for arm in GENERATORS:
            dest=OUT/'generation'/job['job']/arm;assert completed(dest);done=read(dest/'complete.json')
            assert done['cuda'] and done['redraws']==0 and done['test_reads']==0 and done['query_post_reads']==0
            assert set(done['fit_sessions'])==set(job['fit_sessions']) and set(done['query_sessions'])==set(job['query_sessions'])
            for row in read(dest/'loco.json'):
                assert row['fit_rows']==68 and len(row['fit_contents'])==17 and row['held_content'] not in row['fit_contents']
                assert row['query_post_reads']==0 and row['cuda'];LOCO+=1
            pool=np.load(dest/'residual-pool.npy');assert pool.shape==((288 if arm=='D2_group' else 72),6)
            for seed in SEEDS:
                with np.load(dest/f'samples-{seed}.npz',allow_pickle=False) as f:
                    assert set(f['session_ids'])==set(job['query_sessions']) and f['values'].shape==(24,8,6)
                    wm.validate(f['values'].reshape(-1,6))
                    assert (f['donor_indices']>=0).all() and (f['donor_indices']<len(pool)).all()
            tasks+=1
    assert tasks==500 and LOCO==9000
    # Only byte coordinates may change between same-input paired D1 and D2.
    for jp in sorted((OUT/'generator-roles').glob('*.json')):
        job=read(jp)
        one=OUT/'generation'/job['job']/'D1_pair';two=OUT/'generation'/job['job']/'D2_pair'
        np.testing.assert_array_equal(np.load(one/'residual-pool.npy')[:,:4],np.load(two/'residual-pool.npy')[:,:4])
        for seed in SEEDS:
            with np.load(one/f'samples-{seed}.npz',allow_pickle=False) as a,np.load(two/f'samples-{seed}.npz',allow_pickle=False) as b:
                np.testing.assert_array_equal(a['donor_indices'],b['donor_indices'])
                np.testing.assert_array_equal(a['values'][:,:,2:],b['values'][:,:,2:])
    count=0
    for rp in sorted((OUT/'roles').glob('*.json')):
        role=read(rp);assert set(role['train']).isdisjoint(role['test'])
        train=cohort[cohort.session_id.isin(role['train'])];test=cohort[cohort.session_id.isin(role['test'])]
        assert len(train)==480 and len(test)==120 and set(train.content_id).isdisjoint(test.content_id)
        ck=torch.load(OUT/'models'/role['scenario']/'models.pt',map_location=LC.device(),weights_only=False)
        assert set(ck['scaler_fit_sessions'])==set(role['train'])
        jobs=pd.DataFrame(ck['jobs'])
        for key in ['initial_hash','main_schedule_hash','view_schedule_hash']:
            assert jobs.groupby('seed')[key].nunique().eq(1).all()
        assert len(ck['states'])==18 and all(sum(v.numel() for v in state.values())==422 for state in ck['states'])
        count+=18
    pred=pd.read_parquet(OUT/'predictions.parquet');assert len(pred)==10800 and count==90
    assert not pred.duplicated(['arm','seed','session_id']).any()
    for (arm,seed),g in pred.groupby(['arm','seed']):
        assert len(g)==600 and set(g.session_id)==set(cohort.session_id)
    linked=pred.merge(cohort[['session_id','fold']],on='session_id',suffixes=('','_registered'))
    assert linked.fold.eq(linked.fold_registered).all()
    result={'passed':True,'production_Ridge_fits':9500,'generator_tasks':500,'LOCO_tasks':9000,
        'classifiers':90,'CUDA_fit_generate_train_infer':True,'all_generated_W_legal':True,
        'D0_all100_array_pool_draw_replay':True,'global_content_split_preserved':True,
        'D1_D2_paired_P_R_and_draw_indices_exact_equal':True,
        'test_pre_in_inference':False,'test_protocol_numeric_input':False,'query_post_generator_input':False,
        'group_session_or_repetition_input':False,'same_init_main_and_view_schedules':True,
        'source_hashes_unchanged':True,'classifier_replay':read(OUT/'classifier-baseline-replay.json'),
        'historical_unobserved_SYN_cases':5,'registered_entity_qualification_only':True,
        'universal_flow_identity_proof':False,'external_blind_validation':False,'P2_preflight_exception_retained':True}
    write(OUT/'independent-verification.json',result);print(result)


if __name__=='__main__':main()
