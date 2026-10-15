"""V4 IO boundary; frozen scientific definitions are read-only dependencies."""
from pathlib import Path
import importlib.util
import inspect
import json
import os
import time
os.environ.setdefault('CUBLAS_WORKSPACE_CONFIG', ':4096:8')
import numpy as np
import pandas as pd
import pyarrow.parquet
import torch
import torch.nn.functional as F

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('frozen_ct_common', ROOT/'eval/calibrated_deployment_transfer/common.py')
base = importlib.util.module_from_spec(spec); spec.loader.exec_module(base)
for name in ['PROTOCOLS', 'LABELS', 'FEATURES', 'FEATURE_WEIGHTS', 'HIST', 'MASKS', 'ARMS', 'TS',
             'Q', 'OLD', 'PLAN', 'require', 'read', 'sha', 'rel', 'device', 'configure', 'tensor',
             'truths', 'size', 'block', 'bins', 'weighted', 'validate_query', 'scaler', 'predict', 'metrics', 'objective']:
    globals()[name] = getattr(base, name)
PREP = base.OUT
OUT = ROOT/'outputs/calibrated-deployment-business-transfer-20261006/run-04'
DOC = ROOT/'docs/calibrated-deployment-business-transfer/v4'
REPAIR_PLAN = ROOT/'plan/calibrated-deployment-unified-budget-repair-plan-20261006.md'
PREVIOUS = ROOT/'outputs/calibrated-deployment-business-transfer-20261006/run-03'
from numeric_policy import POLICY, SOLVER, acceptance_gates
ACCESS = []
_V4 = None
_ADOPT = None

def writable(p):
    p = Path(p).resolve()
    require(p.is_relative_to(OUT.resolve()) or p.is_relative_to(DOC.resolve()), 'V4 write outside new roots')
    return p

def write(p, value):
    p = writable(p); p.parent.mkdir(parents=True, exist_ok=True)
    temp = p.with_name(p.name+'.tmp')
    temp.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2,
                              allow_nan=False, default=base.json_scalar)+'\n', encoding='utf-8')
    os.replace(temp, p)

def save(df, p):
    p = writable(p); p.parent.mkdir(parents=True, exist_ok=True)
    temp = p.with_name(p.name+'.tmp'); df.to_parquet(temp, index=False); os.replace(temp, p)

def save_artifact(model, p, **details):
    p = writable(p); p.parent.mkdir(parents=True, exist_ok=True)
    require(not p.with_suffix('.json').exists(), 'Do not overwrite accepted artifact')
    validate_new_log(details['optimizer'])
    temp = p.with_name(p.name+'.tmp'); torch.save(model, temp); os.replace(temp, p)
    write(p.with_suffix('.json'), {'sha256': sha(p), **details})

def v4contract():
    global _V4
    if _V4 is None:
        p = OUT/'manifests/experiment-contract-v4.json'
        require(sha(p) == read(p.with_name('contract-seal.json'))['sha256'], 'V4 contract seal')
        _V4 = read(p)
    return _V4

def contract():
    v4contract()
    return base.contract()

def start(stage):
    configure(); ACCESS.clear(); c = contract(); v = v4contract()
    require(sha(PLAN) == c['plan_sha256'], 'Original plan changed')
    require(sha(REPAIR_PLAN) == v['repair_plan_sha256'], 'Approved repair plan changed')
    require(sha(PREP/'manifests/experiment-contract-amended-io-v1.json') == v['original_contract_sha256'], 'Original contract changed')
    for p,h in v['previous_contracts'].items(): require(sha(ROOT/p)==h,'Prior contract changed')
    for p, h in {**c['source_sha256'], **v['previous_source_sha256'], **v['source_sha256']}.items(): require(sha(ROOT/p) == h, 'Sealed source changed: '+p)
    require(sha(Path(inspect.getfile(torch.optim.LBFGS)))==v['installed_LBFGS_sha256'],'Installed optimizer changed')
    policy_path = OUT/'manifests/numeric-policy.json'
    require(sha(policy_path) == v['numeric_policy_sha256'] and read(policy_path) == POLICY, 'Numeric policy changed')
    return c

def checked(p, hashes, role):
    p = Path(p); h = sha(p); require(hashes.get(rel(p)) == h, 'Unsealed input: '+rel(p))
    ACCESS.append({'role': role, 'path': rel(p), 'sha256': h})

def rolepath(r): return PREP/'packages'/r['id']

def package(p, role):
    p = Path(p); c = contract(); info = c['packages'][rel(p)]
    allowed = {'diag-fit': {'diag-train'}, 'main-predict': {'main-query'},
               'main-select': {'main-inner-labels'}, 'main-score': {'main-outer-labels'},
               'main-explain': {'main-test-paired'}, 'verify': {info['kind']}}
    require(role in allowed and info['kind'] in allowed[role], 'Role cannot read '+info['kind'])
    if role in ['main-score', 'main-explain']:
        seal = OUT/'predictions/complete.json'
        require(seal.exists() and sha(OUT/'predictions/visits.parquet') == read(seal)['sha256'], 'Seal ALL main predictions first')
    checked(p, {rel(p): info['sha256']}, role); d = pd.read_parquet(p)
    require(list(d) == info['columns'], 'Package schema changed')
    if role == 'main-predict': validate_query(d)
    return d

def artifact(p):
    global _ADOPT
    p = Path(p)
    # Redirect only frozen input artifacts, never a model or a prediction.
    if p.is_relative_to(OUT) and p.relative_to(OUT).parts[0] in ['slots', 'kernels']:
        p = PREP/p.relative_to(OUT)
    if p.is_relative_to(PREP):
        if _ADOPT is None:
            inventory = OUT/'manifests/adopted-artifacts.json'
            require(sha(inventory) == v4contract()['adopted_artifacts_sha256'], 'Adoption inventory changed')
            _ADOPT = read(inventory)['files']
        hashes = _ADOPT
        require(hashes.get(rel(p)) == sha(p), 'Unadopted or changed frozen artifact')
    info = read(p.with_suffix('.json'))
    require(info['sha256'] == sha(p), 'Artifact seal changed')
    if p.is_relative_to(OUT) and p.relative_to(OUT).parts[0] in ['models', 'pilot']:
        validate_new_log(info['optimizer'])
    ACCESS.append({'role': 'artifact', 'path': rel(p), 'sha256': sha(p)})
    return torch.load(p, map_location=device(), weights_only=True)

def validate_new_log(log):
    require(log['solver'] == SOLVER and log['accepted'], 'Wrong solver or unaccepted model')
    require(log['numeric_policy_sha256'] == sha(OUT/'manifests/numeric-policy.json'), 'Wrong model policy')
    require(log['settings']['max_iter'] == POLICY['max_iter'] and
            log['settings']['max_eval'] == POLICY['max_eval'], 'Wrong model budgets')
    expected = acceptance_gates(log['objective'], log['initial_objective'], log['max_gradient'],
        log['iterations'], log['objective_replay_error'], log['gradient_replay_error'])
    require(log['gates'] == expected and all(expected.values()), 'Model numerical gates changed')

def complete(p, **details): write(p, {'time_unix': time.time(), **details})
def progress(stage, **details):
    write(OUT/'progress.json', {'stage': stage, 'time_unix': time.time(), **details})
    print(stage, details, flush=True)
def finish(stage, **details):
    write(OUT/'manifests'/f'{stage}-ledger.json', {'reads': ACCESS,
          'cuda_peak_MiB': torch.cuda.max_memory_allocated()/1048576, **details})
    progress(stage, **details)

def fit(x, y, mass, t):
    from optimizer_preconditioning import fit_preconditioned
    caller = inspect.currentframe().f_back.f_locals
    r = caller['r']; arm = caller['arm']
    return fit_preconditioned(x, y, mass, t, {'role_id': r['id'], 'arm': arm, 't': t,
        'input_sha256': read((PREP/'slots'/r['id']/(arm+'.pt')).with_suffix('.json'))['sha256']})

def load_frozen(name):
    path = ROOT/'eval/calibrated_deployment_transfer'/(name+'.py')
    require(sha(path) == contract()['source_sha256'][rel(path)], 'Downstream source changed')
    spec = importlib.util.spec_from_file_location('frozen_v4_'+name, path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module
