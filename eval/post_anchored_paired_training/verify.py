"""Validate all fitted states, capabilities, exposure, and sealed OOF coverage."""
from common import *


def main():
    authorize(); tasks = 0; timings = []
    for fold in range(5):
        role = read(OUT/'roles'/f'f{fold}.json')
        assert not set(role['train']) & set(role['test']) and not set(role['train_contents']) & set(role['test_contents'])
        folder = OUT/'fit'/f'f{fold}'; assert completed(folder)
        ck = torch.load(folder/'models.pt', map_location=device(), weights_only=False)
        assert len(ck['jobs']) == 24; tasks += 24
        timings.append(read(folder/'complete.json')['seconds'])
        for seed in SEEDS:
            jobs = [j for j in ck['jobs'] if j['seed'] == seed]
            assert len(jobs) == 8
            for k in ['initial_encoder_hash', 'initial_head_hash', 'post_500_exposures_hash', 'aux_500_exposures_hash']:
                assert len({j[k] for j in jobs}) == 1
        for i, job in enumerate(ck['jobs']):
            assert job['steps'] == 2000 and job['Adam_reset_at'] == 1000 and job['CUDA']
            assert job['test_reads'] == job['score_reads'] == 0
            assert state_hash(ck['E'][i]) == job['encoder_final_hash']
            assert state_hash(ck['H'][i]) == job['head_final_hash']
            assert state_hash({'weight': ck['A'][i]}) == job['A_final_hash']
            assert sum(v.numel() for v in ck['E'][i].values()) == 2528
            assert sum(v.numel() for v in ck['H'][i].values()) == 1254
            if job['arm'] in ['J0', 'J7']: assert job['reads'] == ['post']
            if job['arm'] not in CONDITIONS: assert torch.count_nonzero(ck['A'][i]).item() == 0
    pred = pd.read_parquet(OUT/'oof.parquet'); co = pd.read_parquet(OUT/'cohort.parquet')
    assert tasks == 120 and len(pred) == 14400
    assert not pred.duplicated(['arm', 'seed', 'session_id']).any()
    for _, g in pred.groupby(['arm', 'seed']): assert len(g) == 600 and set(g.session_id) == set(co.session_id)
    merged = pred.merge(co[['session_id', 'fold']], on='session_id', suffixes=('', '_role'))
    assert merged.fold.eq(merged.fold_role).all()
    assert read(OUT/'baseline-reproduction.json')['passed']
    assert read(OUT/'cuda-replay.json')['passed'] and read(OUT/'independent-score-check.json')['passed']
    assert read(OUT/'score-complete.json')['passed']
    assert sha(OLD/'oof.parquet') == read(OUT/'source-seal.json')['E1_prediction']
    write(OUT/'independent-verification.json', {'passed': True, 'fit_tasks': tasks, 'OOF_rows': len(pred),
          'summed_fit_seconds': sum(timings), 'all_CUDA': True, 'same_initializations': True,
          'per_slot_per_visit_exposures': 500, 'test_pre': False, 'inference_protocol_identity': False,
          'group_exact_identity': False, 'E1_unchanged': True, 'E2_started': False,
          'physical_identity_scope': 'existing P3/P2 registration, not new universal proof',
          'historical_unobserved_SYN_cases': 5, 'P2_preflight_limit_retained': True})
    print('All 120 fits, role/exposure/OOF scopes, CUDA and old-source checks passed', flush=True)


if __name__ == '__main__': main()
