"""Create a sealed repaired view; never overwrite attempt1 artifacts or code."""
import shutil
import common
from common import *
import predict

REPAIR = OUT/'repair-v1'


def assemble():
    authorize()
    if (REPAIR/'seal.json').exists(): return
    parent = read(OUT/'seal.json'); repaired = 0; unchanged = 0
    for fold in range(5):
        src = OUT/'fit'/f'f{fold}'; assert completed(src)
        refit = REPAIR/'refits'/f'f{fold}'; done = read(refit/'complete.json')
        assert done['tasks'] == 3 and done['repair_seal_sha256'] == sha(REPAIR/'repair-seal.json')
        for n, h in done['files'].items(): assert sha(refit/n) == h
        orig = torch.load(src/'models.pt', map_location=device(), weights_only=False)
        new = torch.load(refit/'models.pt', map_location=device(), weights_only=False)
        reproduction = read(refit/'training-reproduction.json')
        assert reproduction['first1000_max_loss_difference'] == 0
        assert all(v['same_encoder_hash'] and v['same_head_hash'] for v in reproduction['final_weight_comparisons'])
        mapping = {j['seed']: i for i, j in enumerate(new['jobs'])}
        combined = {'jobs': [], 'E': [], 'H': [], 'A': []}
        provenance = []
        for i, j in enumerate(orig['jobs']):
            if j['arm'] == 'J0':
                k = mapping[j['seed']]; source = new; entry = k; repaired += 1
                provenance.append({'arm': j['arm'], 'seed': j['seed'], 'source': 'approved J0 refit'})
            else:
                source = orig; entry = i; unchanged += 1
                assert source['jobs'][entry]['encoder_final_hash'] == j['encoder_final_hash']
                assert source['jobs'][entry]['head_final_hash'] == j['head_final_hash']
                provenance.append({'arm': j['arm'], 'seed': j['seed'], 'source': 'unchanged attempt1 model'})
            for key in combined: combined[key].append(source[key][entry])
        folder = REPAIR/'fit'/f'f{fold}'; folder.mkdir(parents=True, exist_ok=True)
        torch.save(combined, folder/'models.pt')
        write(folder/'fit-ledger.json', combined['jobs'])
        write(folder/'selection-provenance.json', {'original_models_sha256': sha(src/'models.pt'),
              'refit_models_sha256': sha(refit/'models.pt'), 'selection': provenance,
              'not_selected_by_test_results': True, 'loss_records': [str(src/'losses.npz'), str(refit/'losses.npz')]})
        # Completion markers are finalized after the new view seal exists.
        write(folder/'assembly-metadata.json', {'tasks': 24, 'steps': 2000, 'CUDA': True,
              'seconds': read(src/'complete.json')['seconds']+done['seconds'],
              'new_fits_here': 3, 'unchanged_models': 21})
    assert repaired == 15 and unchanged == 105
    for name in ['packages', 'scalers', 'roles']:
        assert not (REPAIR/name).exists(); shutil.copytree(OUT/name, REPAIR/name)
    for name in ['cohort.parquet', 'qualification.json', 'engineering.json', 'source-seal.json', 'environment.json']:
        shutil.copy2(OUT/name, REPAIR/name)
    contract = read(OUT/'contract.json')
    contract.update({'repair_version': 'v1', 'original_failed_baseline_models': 15,
                     'actual_full_length_fits': 135, 'selected_comparison_models': 120,
                     'repair_approval': '同意，请你继续', 'actual_J0_post_encoding_exposures': 500})
    write(REPAIR/'contract.json', contract)
    hashes = dict(parent['hashes'])
    for name in ['repair_train.py', 'repair_view.py', 'repair_score.py', 'repair_verify.py', 'report.py']:
        hashes[str((CODE/name).relative_to(ROOT))] = sha(CODE/name)
    for p in REPAIR.rglob('*'):
        if p.is_file(): hashes[str(p.relative_to(ROOT))] = sha(p)
    write(REPAIR/'seal.json', {'contract_sha256': sha(REPAIR/'contract.json'), 'hashes': hashes,
          'parent_attempt1_seal': sha(OUT/'seal.json'), 'replacement_models': 15,
          'unmodified_models': 105, 'score_selection': False})
    for fold in range(5):
        folder = REPAIR/'fit'/f'f{fold}'; meta = read(folder/'assembly-metadata.json')
        write(folder/'complete.json', {**meta, 'seal_sha256': sha(REPAIR/'seal.json'),
              'files': {p.name: sha(p) for p in folder.iterdir() if p.is_file() and p.name != 'complete.json'}})


def main():
    assemble()
    common.OUT = REPAIR; predict.OUT = REPAIR
    predict.main()


if __name__ == '__main__': main()
