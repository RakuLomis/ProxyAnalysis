"""JA read boundaries and CUDA arithmetic; historical CT files stay read-only."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import sys
import time
os.environ.setdefault('CUBLAS_WORKSPACE_CONFIG', ':4096:8')
import numpy as np
import pandas as pd
import pyarrow.parquet
import torch
import torch.nn.functional as F

ROOT = Path(__file__).resolve().parents[2]
def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
base = module('ja_ct_definitions', ROOT/'eval/calibrated_deployment_transfer/common.py')
for name in ['PROTOCOLS','LABELS','FEATURES','HIST','MASKS','TS','require','read','sha','rel',
             'device','configure','tensor','truths','size','block','bins','weighted','scaler',
             'predict','metrics','objective']:
    globals()[name] = getattr(base, name)
policy = module('ja_v4_policy', ROOT/'eval/calibrated_deployment_transfer_v4/numeric_policy.py')
POLICY, SOLVER, acceptance_gates = policy.POLICY, policy.SOLVER, policy.acceptance_gates
PREP = base.OUT
V4 = ROOT/'outputs/calibrated-deployment-business-transfer-20261006/run-04'
Q = base.Q
PLAN = ROOT/'plan/mechanism-observability-joint-affine-transfer-plan-20261007.md'
run_arg = sys.argv[sys.argv.index('--run')+1] if '--run' in sys.argv else os.environ.get('JA_RUN_PATH')
OUT = Path(run_arg).resolve() if run_arg else ROOT/'outputs/joint-affine-transfer-20261007/run-01'
require(OUT.is_relative_to(ROOT/'outputs/joint-affine-transfer-20261007'), 'Unsafe run path')
os.environ['JA_RUN_PATH'] = str(OUT)
DOC = ROOT/'docs/joint-affine-transfer'
ARMS = ['JA0','JA1','JA2']
ETAS = [.1,1.,10.,100.]
ACCESS = []
_C = None

def writable(path):
    p = Path(path).resolve()
    require(p.is_relative_to(OUT) or p.is_relative_to(DOC), 'JA write outside new roots')
    return p
def write(path, value):
    p = writable(path); p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_name(p.name+'.tmp')
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True,
                             allow_nan=False, default=base.json_scalar)+'\n', encoding='utf-8')
    os.replace(tmp,p)
def textfile(path, value):
    p = writable(path); p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(value, encoding='utf-8')
def save(df, path):
    p = writable(path); p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_name(p.name+'.tmp'); df.to_parquet(tmp, index=False); os.replace(tmp,p)
def put(obj, path, **meta):
    p = writable(path); p.parent.mkdir(parents=True, exist_ok=True)
    require(not p.with_suffix('.json').exists(), 'Accepted artifact already exists')
    tmp = p.with_name(p.name+'.tmp'); torch.save(obj,tmp); os.replace(tmp,p)
    write(p.with_suffix('.json'), {'sha256':sha(p), **meta})
def get(path):
    p = Path(path); info = read(p.with_suffix('.json'))
    require(sha(p)==info['sha256'], 'Artifact hash changed: '+rel(p))
    if info.get('optimizer'):
        log=info['optimizer']; gates=acceptance_gates(log['objective'],log['initial_objective'],
            log['max_gradient'],log['iterations'],log['objective_replay_error'],log['gradient_replay_error'])
        require(log['solver']==SOLVER and log['accepted'] and all(gates.values()), 'Unaccepted classifier')
        require(log['numeric_policy_sha256']==sha(OUT/'manifests/numeric-policy.json'), 'Wrong policy')
    ACCESS.append({'purpose':'artifact','path':rel(p),'sha256':info['sha256']})
    return torch.load(p,map_location=device(),weights_only=True)
def progress(stage, **details):
    write(OUT/'progress.json', {'stage':stage,'time_unix':time.time(), **details})
    print(stage, details, flush=True)
def complete(path, **details): write(path, {'time_unix':time.time(), **details})
def contract():
    global _C
    if _C is None:
        p=OUT/'manifests/experiment-contract.json'
        require(sha(p)==read(OUT/'manifests/seal.json')['contract_sha256'], 'Contract changed')
        _C=read(p)
    return _C
def start(stage):
    configure(); ACCESS.clear(); c=contract()
    require(sha(PLAN)==c['plan_sha256'], 'Plan changed')
    for p,h in c['source_sha256'].items(): require(sha(ROOT/p)==h, 'Sealed source changed: '+p)
    require(sha(Path(c['installed_LBFGS_path']))==c['installed_LBFGS_sha256'],'Installed optimizer changed')
    require(read(OUT/'manifests/numeric-policy.json')==POLICY, 'Numerical policy changed')
    return c
def finish(stage, **details):
    write(OUT/'manifests'/f'{stage}-ledger.json', {'reads':ACCESS, **details})
    progress(stage, **details)
def paired_schema(d):
    expected={'visit_id','content_token','fit_mass', *['pre_'+h for h in HIST], *['post_'+h for h in HIST]}
    require(set(d)==expected and d.visit_id.is_unique, 'Unsafe paired schema')
def group_schema(d):
    require(set(d)=={'content_token','fit_mass',*HIST}, 'Anonymous identity/schema leak')
def sealed_predictions():
    p=OUT/'predictions/visits.parquet'
    require(p.exists() and sha(p)==read(p.with_name('complete.json'))['sha256'], 'Seal ALL predictions first')
def validate_scope(d,info):
    k=info['kind'];s=info['scope']
    if k in ['source-post','source-pre']:
        require(set(d.content_id).issubset(s['train_contents']),'Source crosses training contents')
        require(set(d.protocol).issubset(s['sources']),'Forbidden source deployment')
    elif k=='C-post':
        require(set(d.content_id).issubset(s['C_contents']),'Target U/C membership violation')
        require(set(d.protocol)=={s['calibration']},'Wrong calibration deployment')
    elif k in ['main-inner-labels','main-outer-labels','main-test-paired','JA-heldout-visits']:
        require(set(d.content_id).issubset(s['validation_contents']),'Held-out content scope changed')
    elif k in ['JA-C-paired','JA-C-group']:
        tokens={hashlib.sha256(('ja-content:'+str(u)).encode()).hexdigest() for u in s['C_contents']}
        require(set(d.content_token)==tokens,'Anonymous C content membership violation')
        require(abs(float(d.fit_mass.sum())-1)<1e-12 and (d.fit_mass>0).all(),'C weights changed')
def check_permission(kind,purpose):
    allowed={'source-fit':{'source-post','source-pre','C-post'}, 'paired-map':{'JA-C-paired'},
        'group-map':{'JA-C-group'},'query':{'main-query'},'select':{'main-inner-labels'},
        'score':{'main-outer-labels'},'explain':{'main-test-paired'},'explain-visits':{'JA-heldout-visits'}}
    require(purpose in allowed and kind in allowed[purpose],'Illegal package read')
def package(path, purpose):
    p=Path(path); c=contract(); info=c['packages'][rel(p)]
    check_permission(info['kind'],purpose)
    if purpose in ['score','explain','explain-visits']: sealed_predictions()
    require(sha(p)==info['sha256'], 'Changed package: '+rel(p))
    d=pd.read_parquet(p); require(list(d)==info['columns'], 'Package schema changed')
    validate_scope(d,info)
    if purpose=='paired-map': paired_schema(d)
    if purpose=='group-map': group_schema(d)
    if purpose=='query': base.validate_query(d)
    ACCESS.append({'purpose':purpose,'path':rel(p),'sha256':info['sha256']})
    return d
def rolepath(r): return PREP/'packages'/r['id']
def tag(arm, eta): return f'{arm}-eta{eta:g}'
def mappath(r, arm, eta): return OUT/'maps'/r['id']/(tag(arm,eta)+'.pt')
def slotpath(r, arm, eta): return OUT/'slots'/r['id']/(tag(arm,eta)+'.pt')
def modelpath(r, arm, eta, t): return OUT/'models'/r['id']/f'{tag(arm,eta)}-t{t:g}.pt'
def lr_solver():
    return module('ja_frozen_optimizer',ROOT/'eval/calibrated_deployment_transfer_v4/optimizer_preconditioning.py')
def choices():
    p=OUT/'selection/choices.json'
    require(sha(p)==read(p.with_name('complete.json'))['sha256'],'Selection changed')
    return {(v['outer'],v['target'],v['group'],v['arm']):v for v in read(p)}
def chosen(r, arm, selected): return selected[(r['outer'],r['target'],r['group'],arm)]
