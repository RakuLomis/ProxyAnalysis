"""Independent CUDA-only pilot IO. Historical runs are never writable."""
from pathlib import Path
import contextlib
import hashlib
import importlib.util
import inspect
import json
import os
import sys
import time
os.environ.setdefault('CUBLAS_WORKSPACE_CONFIG', ':4096:8')
import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'outputs/dynamic-soft-drift-calibration-20261012/run-01'
DOC = ROOT/'docs/dynamic-soft-drift-calibration'
PLAN = ROOT/'plan/dynamic-soft-constrained-drift-calibration-plan-20261012.md'
JA = ROOT/'outputs/joint-affine-transfer-20261007/run-01'
TI = ROOT/'outputs/strongpost-training-intervention-20261009/run-01'
AG = ROOT/'outputs/invariant-anchor-guarded-drift-20261012/run-01'
AC = ROOT/'outputs/invariant-anchor-diagnostic-closeout-20261012/run-01'

def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m

base = module('ds_original_definitions', ROOT/'eval/calibrated_deployment_transfer/common.py')
for name in ['PROTOCOLS','LABELS','HIST','FEATURES','MASKS','require','read','sha','rel',
             'device','configure','tensor','block','size','truths','weighted','scaler']:
    globals()[name] = getattr(base, name)
PREP = base.OUT
policy = module('ds_v4_policy', ROOT/'eval/calibrated_deployment_transfer_v4/numeric_policy.py')
POLICY, SOLVER, acceptance_gates = policy.POLICY, policy.SOLVER, policy.acceptance_gates
ACCESS = []
_C = None
ARMS = ['D-P','T-P','D-G']

def writable(path):
    p = Path(path).resolve()
    require(p.is_relative_to(OUT) or p.is_relative_to(DOC), 'Write outside new experiment roots')
    return p

def write(path, value):
    p = writable(path); p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_name(p.name+'.tmp')
    tmp.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2,
                             allow_nan=False, default=base.json_scalar)+'\n', encoding='utf-8')
    os.replace(tmp, p)

def save(df, path):
    p = writable(path); p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_name(p.name+'.tmp'); df.to_parquet(tmp, index=False); os.replace(tmp,p)

def textfile(path, value):
    p = writable(path); p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(value, encoding='utf-8')

def put(value, path, **info):
    p = writable(path); require(not p.exists(), 'Refuse to overwrite accepted artifact')
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_name(p.name+'.tmp'); torch.save(value, tmp); os.replace(tmp,p)
    write(p.with_suffix('.json'), dict(sha256=sha(p), **info))

def progress(stage, **info):
    write(OUT/'progress.json', dict(stage=stage, time_unix=time.time(), **info))
    print(stage, info, flush=True)

def contract():
    global _C
    if _C is None:
        p = OUT/'manifests/experiment-contract.json'
        require(sha(p)==read(p.with_name('seal.json'))['contract_sha256'], 'Contract seal changed')
        _C = read(p)
    return _C

def checked(path, expected, purpose, arm=None):
    p = Path(path)
    label=rel(p) if p.resolve().is_relative_to(ROOT) else p.as_posix()
    require(sha(p)==expected, 'Changed input '+label)
    ACCESS.append(dict(path=label, sha256=expected, purpose=purpose, arm=arm))

def package_permission(kind, purpose, arm=None):
    allowed = {'train': {'source-pre','source-post','C-post'},
               'meta-query': {'main-query'}, 'meta-labels': {'main-inner-labels'},
               'paired-recovery': {'JA-C-paired'}, 'group-recovery': {'JA-C-group'}}
    require(purpose in allowed and kind in allowed[purpose], 'Forbidden package purpose')
    require(not (arm=='D-G' and kind=='JA-C-paired'), 'Group cannot read exact identities')

def role_permission(r, pilot=False):
    require(not set(r['train_contents'])&set(r['validation_contents']), 'Training/test content overlap')
    require(not set(r['C_contents'])&set(r['U_contents']), 'C/U overlap')
    require(set(r['C_contents'])|set(r['U_contents'])==set(r['train_contents']), 'C/U partition')
    if pilot:
        require(r['inner'] is not None and r['target'] not in r['sources']+[r['calibration']],
                'Actual target data forbidden in source pilot')

def artifact_permission(kind, arm):
    require(kind in ['shared','P','G'], 'Unknown artifact permission')
    require(not (arm=='D-G' and kind=='P'), 'Group cannot read P artifacts')
    require(not (arm in ['D-P','T-P'] and kind=='G'), 'Paired arm does not read group map')

def package(path, purpose, arm, r):
    role_permission(r, pilot=True)
    c = contract(); p = Path(path); info = c['packages'][rel(p)]
    package_permission(info['kind'], purpose, arm)
    require(rel(p) in c['pilot_packages_by_role'][r['id']], 'Unregistered pilot package')
    checked(p, info['sha256'], purpose, arm)
    d = pd.read_parquet(p); require(list(d)==info['columns'], 'Schema changed')
    k = info['kind']
    if k in ['source-pre','source-post']:
        require(set(d.content_id)<=set(r['train_contents']) and set(d.protocol)==set(r['sources']), 'Source scope')
        require(len(d)==144 and d.groupby(['protocol','content_id']).size().eq(4).all(), 'Source repetitions')
        if k=='source-pre': require('visit_id' not in d and 'session_id' not in d, 'Source pre identity')
    elif k=='C-post':
        require(set(d.content_id)==set(r['C_contents']) and set(d.protocol)=={r['calibration']}, 'C scope')
        require(len(d)==48, 'C visits')
    elif k in ['main-query','main-inner-labels']:
        require(len(d)==24 and d.visit_id.is_unique, 'Meta validation visits')
        if k=='main-query': base.validate_query(d)
        else: require(set(d.content_id)==set(r['validation_contents']), 'Meta labels scope')
    else:
        tokens={hashlib.sha256(('ja-content:'+u).encode()).hexdigest() for u in r['C_contents']}
        require(set(d.content_token)==tokens and len(d)==48, 'Calibration content scope')
        require(d.groupby('content_token').size().eq(4).all(), 'Calibration repeats')
        require(abs(float(d.fit_mass.sum())-1)<1e-12, 'Calibration mass')
        if k=='JA-C-group': group_schema(d)
    return d

def group_schema(d):
    require(set(d)=={'content_token','fit_mass',*HIST}, 'Anonymous group schema violation')

def artifact(path, kind='shared', arm='D-P'):
    artifact_permission(kind, arm)
    p = Path(path); c = contract(); expected=c['artifacts'][rel(p)]
    checked(p, expected, 'artifact', arm)
    info = read(p.with_suffix('.json')); require(info['sha256']==expected, 'Artifact metadata seal')
    return torch.load(p, map_location=device(), weights_only=True)

def start(stage):
    configure(); ACCESS.clear(); c = contract()
    checked(PLAN,c['plan_sha256'],'approved-plan')
    for p,h in c['source_sha256'].items(): checked(ROOT/p,h,'source')
    for p,h in c['fixed_files'].items(): checked(ROOT/p,h,'metadata-lineage')
    require(read(OUT/'manifests/numeric-policy.json')==POLICY, 'Numeric policy changed')
    checked(Path(c['environment']['installed_LBFGS_path']),
            c['environment']['installed_LBFGS_sha256'],'installed-solver')
    return c

@contextlib.contextmanager
def stage(name):
    start(name); marker=OUT/'stages'/f'{name}.json'
    require(not marker.exists(), 'Stage already completed')
    lock=OUT/'stage.lock'; lock.parent.mkdir(parents=True, exist_ok=True)
    fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY); os.write(fd,str(os.getpid()).encode()); os.close(fd)
    began=time.time()
    try:
        progress(name+'_running',pid=os.getpid()); yield
        write(marker,dict(passed=True,seconds=time.time()-began,reads=ACCESS,time_unix=time.time()))
        progress(name+'_complete',seconds=time.time()-began)
    except BaseException as exc:
        write(OUT/'failures'/f'{name}-{time.time_ns()}.json',dict(stage=name,type=type(exc).__name__,
              exception=str(exc),reads=ACCESS,time_unix=time.time(),automatic_retry=False))
        progress(name+'_failed',reason=str(exc)); raise
    finally:
        lock.unlink(missing_ok=True)

def oldmap(r, kind): return JA/'maps'/r['id']/f'JA{1 if kind=="P" else 2}-eta{r["eta"]:g}.pt'
def oldslot(r, kind): return JA/'slots'/r['id']/f'JA{1 if kind=="P" else 2}-eta{r["eta"]:g}.pt'
def solver(): return module('ds_frozen_v4_solver',ROOT/'eval/calibrated_deployment_transfer_v4/optimizer_preconditioning.py')

def pilot_task(r, arm):
    kind='D-G' if arm=='D-G' else 'D-P'
    p=OUT/'pilot/tasks'/r['id']/f'{kind}.pt'
    artifact_permission('G' if kind=='D-G' else 'P',arm)
    info=read(p.with_suffix('.json'));require(info['role_id']==r['id'] and info['arm']==kind,'Task identity')
    checked(p,info['sha256'],'own-source-pilot-task',arm)
    return torch.load(p,map_location=device(),weights_only=True)
