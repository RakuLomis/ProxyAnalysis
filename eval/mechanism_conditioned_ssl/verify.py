"""Persisted isolation, exposure, parameter and OOF coverage audit."""
from common import *


def main():
    cli(__doc__).parse_args(); authorize(); counts = {'ssl': 0, 'probe': 0, 'finetune': 0}
    for fold in range(5):
        role = read(OUT/'roles'/f'f{fold}.json')
        assert not set(role['train']) & set(role['test'])
        assert not set(role['train_contents']) & set(role['test_contents'])
        for stage in counts:
            folder = OUT/stage/f'f{fold}'; assert completed(folder)
            counts[stage] += read(folder/'complete.json')['tasks']
        ck = torch.load(OUT/'ssl'/f'f{fold}'/'checkpoint.pt', map_location=device(), weights_only=False)
        for seed in SEEDS:
            jobs = [v for v in ck['jobs'] if v['seed'] == seed]
            assert len(jobs) == 6
            for key in ['post_schedule_hash', 'common_mask_hash', 'initial_encoder_hash', 'initial_projector_hash']:
                assert len({v[key] for v in jobs}) == 1
        for stage in ['probe', 'finetune']:
            for block in torch.load(OUT/stage/f'f{fold}'/'models.pt', map_location=device(), weights_only=False):
                for i, j in enumerate(block['jobs']):
                    assert state_hash(block['E'][i]) == j['encoder_final_hash']
                    assert sum(v.numel() for v in block['E'][i].values()) == 2528
                    if stage == 'probe': assert j['encoder_final_hash'] == j['initial_encoder_hash']
    assert counts == {'ssl': 90, 'probe': 210, 'finetune': 120}
    pred = pd.read_parquet(OUT/'oof.parquet'); assert len(pred) == 39600
    assert not pred.duplicated(['stage', 'arm', 'head', 'seed', 'session_id']).any()
    co = pd.read_parquet(OUT/'cohort.parquet')
    for _, g in pred.groupby(['stage', 'arm', 'head', 'seed']):
        assert len(g) == 600 and set(g.session_id) == set(co.session_id)
    merged = pred.merge(co[['session_id', 'fold']], on='session_id', suffixes=('', '_registered'))
    assert merged.fold.eq(merged.fold_registered).all()
    assert read(OUT/'cuda-replay.json')['passed'] and read(OUT/'score-complete.json')['passed']
    write(OUT/'independent-verification.json', {'passed': True, 'fit_counts': counts, 'OOF_rows': len(pred),
          'global_content_and_parent_access_membership': True, 'same_common_initialization_and_schedule': True,
          'all_frozen_probes_unchanged': True, 'CUDA_training_inference': True,
          'physical_identity_basis': 'reused sealed P3/P2 registration; no stronger universal proof',
          'historical_unobserved_SYN_cases': 5, 'P2_preflight_exception_retained': True,
          'test_pre_in_classification': False, 'numeric_protocol_input': False,
          'group_true_pair_identity': False, 'external_blind_validation': False})
    print('Independent verification passed:', counts, flush=True)


if __name__ == '__main__': main()
