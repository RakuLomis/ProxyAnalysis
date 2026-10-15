"""Seal existing all-fallback endpoints without executing final_train or trainers."""
from common import *


def run():
    verifyseal(SOURCE/'manifests/engineering-code.json')
    verifyseal(SOURCE/'selections/complete.json')
    verifyseal(SOURCE/'inner-predictions/complete.json')
    contract = read(SOURCE/'manifests/experiment-contract.json')
    require(sha(SOURCE/'manifests/experiment-contract.json') == read(SOURCE/'manifests/seal.json')['sha256'], 'Contract changed')
    require(sha(ROOT/'plan/post-input-associated-representation-residual-plan-20261014.md') == contract['plan_sha256'], 'Plan changed')
    decisions = read(SOURCE/'selections/decisions.json')
    lookup = {(d['role_id'], d['arm']): d for d in decisions}
    roles = contract['roles']
    expected = {(r['id'], arm) for r in roles for arm in ['A1', 'A2', 'A3']}
    require(len(roles) == 60 and len({r['id'] for r in roles}) == 60, 'Role count/uniqueness')
    require(len(decisions) == 180 and set(lookup) == expected, 'Decision completeness')
    require(contract['seeds'] == SEEDS, 'Seed policy changed')
    require(all(not d['enabled'] and d['fallback'] and d['lambda_value'] is None
                and d['reason'] == 'no_source_qualified_candidate' for d in decisions),
            'Repair only authorized for existing all-fallback decisions; never invoke training')
    endpoints = []
    base_files = []
    source_models = []
    for r in roles:
        path = PARENT/'base-models'/r['id']/'P-small.pt'
        meta = read(path.with_suffix('.json'), 'base-lineage')
        require(meta['role_id'] == r['id'] and sha(path) == meta['sha256'], 'Base model identity/hash')
        original = ROOT/meta['source']
        require(meta['source'] in contract['bindings'] and sha(original) == contract['bindings'][meta['source']], 'Original P-small binding')
        base_files.extend([path, path.with_suffix('.json')])
        source_models.append(original)
        for arm in ['A0', 'A1', 'A2', 'A3']:
            for seed in SEEDS:
                endpoints.append(dict(role_id=r['id'], arm=arm, seed=seed,
                    base_path=rel(path), residual_path=None, fallback=True, lambda_value=None))
    old = read(SOURCE/'manifests/endpoints.json')
    require(old == endpoints and len(endpoints) == 720, 'Existing endpoints not exact registered Cartesian product')
    paths = collect_model_files(ROOT, endpoints)
    require(paths == set(base_files[::2]) and len(paths) == 60, 'Fixed model file collection')
    tests = self_tests()
    write(OUT/'manifests/endpoints.json', endpoints)
    write(OUT/'audits/path-interface.json', dict(passed=True, tests=tests,
        implementation='root / relative_path', source_line='ROOT[e[\'base_path\']]',
        endpoint_list_equal_to_stopped_P3=True, enabled=0, fallback_decisions=180,
        new_teacher_fits=0, new_residual_fits=0, new_LR_fits=0, H_reads=0, actual_U_reads=0))
    seal(OUT/'manifests/models-complete.json', base_files+source_models+[
        OUT/'manifests/endpoints.json', OUT/'manifests/repair-contract.json',
        OUT/'manifests/repair-code.json', SOURCE/'selections/complete.json',
        SOURCE/'selections/decisions.json', SOURCE/'manifests/experiment-contract.json'],
        passed=True, endpoints=720, unique_base_models=60, exact_fallback_decisions=180,
        scope='P3_seal_only_no_H_prediction', training_fits=0)
    print('P3_seal_complete endpoints=720 unique_base_models=60 training_fits=0', flush=True)
    return contract
