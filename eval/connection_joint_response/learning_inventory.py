"""Append-only implementation extension before numerical pilot, no science change."""
from common import *

def run():
    c=contract(); require(not (OUT/'manifests/learning-code-seal.json').exists(),'Learning code already sealed')
    for p,h in c['source_sha256'].items():require(sha(ROOT/p)==h,'Registered preparation code changed')
    sources={rel(p):sha(p) for p in Path(__file__).parent.glob('*.py')}
    write(OUT/'manifests/learning-code.json',{'version':'CJ-learning-extension-v1','parent_contract_sha256':sha(OUT/'manifests/experiment-contract.json'),
        'sha256':sources,'scientific_contract_changed':False,'new_classifier_cap':1920,
        'numeric_policy':POLICY,'derived_local_LBFGS_reference':'eval/calibrated_deployment_transfer_v4/optimizer_preconditioning.py'})
    write(OUT/'manifests/learning-code-seal.json',{'sha256':sha(OUT/'manifests/learning-code.json')})
    progress('learning_code_registered',source_files=len(sources),scientific_contract_changed=False)

if __name__=='__main__':run()
