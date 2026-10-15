"""Persist partial completion without bypassing the failed numerical gate."""
from common import *


def main():
    authorize(); counts = 0; seconds = 0.
    co = pd.read_parquet(OUT/'cohort.parquet'); pred = pd.read_parquet(OUT/'oof.parquet')
    assert len(pred) == 14400 and not pred.duplicated(['arm', 'seed', 'session_id']).any()
    for fold in range(5):
        role = read(OUT/'roles'/f'f{fold}.json')
        assert not set(role['train']) & set(role['test'])
        assert not set(role['train_contents']) & set(role['test_contents'])
        folder = OUT/'fit'/f'f{fold}'; assert completed(folder)
        ck = torch.load(folder/'models.pt', map_location=device(), weights_only=False)
        assert len(ck['jobs']) == 24; counts += 24
        seconds += read(folder/'complete.json')['seconds']
        for i, j in enumerate(ck['jobs']):
            assert j['steps'] == 2000 and j['CUDA'] and j['test_reads'] == j['score_reads'] == 0
            assert state_hash(ck['E'][i]) == j['encoder_final_hash']
            assert state_hash(ck['H'][i]) == j['head_final_hash']
            if j['arm'] in ['J0', 'J7']: assert j['reads'] == ['post']
    for _, g in pred.groupby(['arm', 'seed']): assert len(g) == 600 and set(g.session_id) == set(co.session_id)
    assert sha(OUT/'oof.parquet') == read(OUT/'prediction-seal.json')['oof_sha256']
    assert sha(OLD/'oof.parquet') == read(OUT/'source-seal.json')['E1_prediction']
    assert read(OUT/'cuda-replay.json')['passed']
    assert not read(OUT/'baseline-reproduction.json')['passed']
    assert not (OUT/'scored-oof.parquet').exists() and not (OUT/'score-complete.json').exists()
    write(OUT/'implementation-status.json', {'implementation_complete': True, 'formal_fits_completed': counts,
          'summed_fit_seconds': seconds, 'smoke_tasks': 8, 'additional_fits': 0,
          'OOF_predictions_sealed': 14400, 'CUDA_replays_passed': 120,
          'training_checks_passed': True, 'global_registered_content_membership': True,
          'old_E1_sources_unchanged': True, 'scoring_complete': False,
          'scorer_test_label_reads': 0, 'packaging_has_known_label_metadata': True,
          'paused_at': 'J0 versus frozen B0L numerical reproduction gate',
          'user_confirmation_required': 'additional fifteen J0 repair fits preserving failed attempt',
          'objective_budget_threshold_not_changed': True, 'E2_started': False})
    print('Partial status verified: 120 trained/120 CUDA replayed; scorer stopped before label consumption')


if __name__ == '__main__': main()
