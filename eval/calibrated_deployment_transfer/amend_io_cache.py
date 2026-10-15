"""Pre-fit, formula-preserving contract IO cache amendment; original seal retained."""
import ast
from common import *

def run():
    require(not (OUT/'models').exists(), 'IO amendment must precede all formal fitting')
    original = OUT/'manifests/experiment-contract.json'
    amended = OUT/'manifests/experiment-contract-amended-io-v1.json'
    require(not amended.exists(), 'Do not overwrite amendment')
    archive = OUT/'manifests/engineering-io-cache-v1/common-original-v1.py'
    old = read(original); common = Path(__file__).parent/'common.py'
    require(sha(archive) == old['source_sha256'][rel(common)], 'Original common snapshot mismatch')
    def funcs(path):
        return {x.name: ast.dump(x, include_attributes=False) for x in ast.parse(path.read_text(encoding='utf-8')).body
                if isinstance(x, (ast.FunctionDef, ast.AsyncFunctionDef))}
    before = funcs(archive); after = funcs(common)
    changed = sorted(k for k in set(before)|set(after) if before.get(k) != after.get(k))
    require(changed == ['contract', 'start'], 'Unexpected non-IO function change')
    for p, h in old['source_sha256'].items():
        if p != rel(common): require(sha(ROOT/p) == h, 'Unexpected sealed source change')
    new = dict(old)
    new['source_sha256'] = {rel(p): sha(p) for p in Path(__file__).parent.glob('*.py')}
    new['source_sha256'][rel(Path(__file__).parent/'README.md')] = sha(Path(__file__).parent/'README.md')
    new['engineering_revision'] = {'kind': 'IO-only contract cache', 'original_contract_sha256': sha(original),
        'original_common_sha256': sha(archive), 'changed_functions': changed,
        'scientific_contract_unchanged': True, 'fits_completed_at_amendment': 0,
        'all_unchanged_function_AST_equal': True, 'no_optimizer_kernel_or_prediction_change': True}
    write(amended, new)
    write(OUT/'manifests/engineering-io-cache-v1/amendment-seal.json', {
        'original_contract_sha256': sha(original), 'amended_contract_sha256': sha(amended),
        'original_common_sha256': sha(archive), 'repaired_common_sha256': sha(common),
        'scientific_contract_unchanged': True, 'method_or_budget_changed': False})
    print('Pre-fit IO amendment sealed; original contract retained; numerical functions AST unchanged', flush=True)

if __name__ == '__main__': run()
