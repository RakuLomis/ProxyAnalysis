"""Audited pre-positive-fit repair: deterministic CUDA weighted count reduction."""
from common import *
from matrices import tests

def run():
    archive=OUT/'manifests/engineering-repair-01'; old=read(archive/'contract-original.json')
    current=contract()
    require(current==old,'Repair must apply only once to the original contract')
    require(not any((OUT/'kernels').rglob('*.pt')) and not any((OUT/'regularizers').rglob('*.pt')),
            'No real kernel or regularizer may precede this repair')
    require(not any((OUT/'models/inner').rglob('*.pt')),'No positive fits may precede repair')
    require(sha(archive/'matrices-original.py')==old['source_sha256'][rel(Path(__file__).parent/'matrices.py')],
            'Original source archive mismatch')
    for p,h in old['source_sha256'].items():
        if p!=rel(Path(__file__).parent/'matrices.py'): require(sha(ROOT/p)==h,'Unrelated source changed')
    tests()
    record={'reason':'CUDA weighted bincount rejected strict deterministic_algorithms at first inner role',
        'fix':'same weighted counts via CUDA float64 one-hot GEMV; deterministic mode retained',
        'old_contract_sha256':sha(archive/'contract-original.json'),
        'original_matrix_source_sha256':sha(archive/'matrices-original.py'),
        'new_matrix_source_sha256':sha(Path(__file__).parent/'matrices.py'),
        'positive_models_before_repair':0,'real_kernel_outputs_before_repair':0,
        'candidate_hyperparameters_memberships_tolerances_changed':False,'repair_unix':time.time()}
    write(archive/'repair.json',record)
    current['source_sha256'][rel(Path(__file__).parent/'matrices.py')]=record['new_matrix_source_sha256']
    current['source_sha256'][rel(Path(__file__))]=sha(Path(__file__))
    current['engineering_amendment']=record
    write(OUT/'manifests/experiment-contract.json',current)
    print('Deterministic reduction repair sealed before any real inner kernel/model',flush=True)

if __name__=='__main__': run()
