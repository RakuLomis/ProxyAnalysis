"""Freeze the complete executable before migration acceptance and full launch."""
from common import *
import ast

def run():
    require(not (OUT/'manifests/code-seal.json').exists(),'Code already frozen')
    files={rel(p):sha(p) for p in sorted(CODE.glob('*.py'))}
    for name,b in contract()['numerical_bindings'].items():
        require(sha(ROOT/b['source'])==b['source_sha256'] and sha(CODE/name)==b['copy_sha256'],'Numerical source copy changed after registration')
        require(ast.dump(ast.parse((CODE/name).read_text(encoding='utf-8')))==ast.dump(ast.parse((ROOT/b['source']).read_text(encoding='utf-8'))),'Numerical AST')
    require(sha(PILOT/'budget.json')==contract()['pilot_budget_sha256'],'Pilot frozen ledger')
    require(sha(inspect.getfile(torch.optim.LBFGS))==read(PILOT/'registration.json')['torch_lbfgs_sha256'],'Installed optimizer unchanged')
    immutable(OUT/'manifests/code-seal.json',dict(files=files,numerical_version='NER1',contract_sha256=sha(OUT/'manifests/contract.json')))
    progress('full_NER1_code_sealed',files=len(files))

if __name__=='__main__':run()
