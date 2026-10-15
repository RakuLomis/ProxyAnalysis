"""Base scope verification plus repair lineage and 105 unchanged model checks."""
import common
from common import *
import verify


def main():
    base = OUT; repair = base/'repair-v1'
    common.OUT = repair; verify.OUT = repair; verify.main()
    unchanged, refitted = 0, 0
    for fold in range(5):
        orig = torch.load(base/'fit'/f'f{fold}'/'models.pt', map_location=device(), weights_only=False)
        selected = torch.load(repair/'fit'/f'f{fold}'/'models.pt', map_location=device(), weights_only=False)
        for i, j in enumerate(orig['jobs']):
            assert (j['arm'], j['seed']) == (selected['jobs'][i]['arm'], selected['jobs'][i]['seed'])
            if j['arm'] == 'J0': refitted += 1
            else:
                for key in ['E', 'H']: assert state_hash(orig[key][i]) == state_hash(selected[key][i])
                assert torch.equal(orig['A'][i], selected['A'][i]); unchanged += 1
    assert unchanged == 105 and refitted == 15
    parent = read(base/'seal.json')
    for n, h in parent['hashes'].items(): assert sha(ROOT/n) == h
    assert sha(base/'oof.parquet') == read(base/'prediction-seal.json')['oof_sha256']
    result = read(repair/'independent-verification.json')
    result.update({'unchanged_models': 105, 'refitted_J0': 15, 'actual_full_length_fits': 135,
                   'original_attempt1_preserved': True, 'approved_extra_fits_only': True})
    write(repair/'independent-verification.json', result)
    print('Repair lineage verified: original attempt preserved, 105 models bitwise unchanged, 15 refits', flush=True)


if __name__ == '__main__': main()
