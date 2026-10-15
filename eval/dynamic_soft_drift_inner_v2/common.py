"""New writes, sealed source-only reads. Rebind IO in memory, never old files."""
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
ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'outputs/dynamic-soft-drift-calibration-20261012/run-01'
REF=ROOT/'outputs/dynamic-soft-drift-calibration-repair-20261012/run-01'
OUT=ROOT/'outputs/dynamic-soft-drift-inner-v2-20261012/run-01'
DOC=ROOT/'docs/dynamic-soft-drift-calibration/inner-v2-20261012'
PLAN=ROOT/'plan/dynamic-soft-drift-preconditioned-inner-v2-plan-20261012.md'
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec)
    sys.modules[name]=m;spec.loader.exec_module(m);return m
IO=module('iv2_readonly_io_helpers',ROOT/'eval/dynamic_soft_drift_calibration_repair/common.py')
IO.OUT=OUT;IO.DOC=DOC
for name in ['require','read','sha','rel','device','configure','tensor','block','size','weighted','HIST','FEATURES',
             'POLICY','SOLVER','acceptance_gates','writable','write','save','put','textfile','progress','checked']:
    globals()[name]=getattr(IO,name)
ACCESS=IO.ACCESS;_C=None
def contract():
    global _C
    if _C is None:
        p=OUT/'manifests/contract.json';require(sha(p)==read(p.with_name('seal.json'))['contract_sha256'],'Contract changed');_C=read(p)
    return _C
def integrity():
    for p,h in contract()['parent_files'].items():require(sha(ROOT/p)==h,'Parent changed '+p)
    require(read(SOURCE/'completion.json')['status']=='stop_numeric_FD_activation_boundary','Old failure changed')
    require(read(REF/'completion.json')['status']=='awaiting_inner_quality_decision','Reference state changed')
def start(name):
    configure();ACCESS.clear();c=contract();checked(PLAN,c['plan_sha256'],'plan')
    for p,h in {**c['source_sha256'],**c['math_source_sha256']}.items():checked(ROOT/p,h,'code')
    integrity();return c
@contextlib.contextmanager
def stage(name):
    start(name);marker=OUT/'stages'/f'{name}.json';require(not marker.exists(),'Stage complete')
    lock=OUT/'stage.lock';lock.parent.mkdir(parents=True,exist_ok=True)
    fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY);os.write(fd,str(os.getpid()).encode());os.close(fd);began=time.time()
    try:
        progress(name+'_running',pid=os.getpid());yield
        write(marker,dict(passed=True,seconds=time.time()-began,reads=ACCESS));progress(name+'_complete',seconds=time.time()-began)
    except BaseException as exc:
        write(OUT/'failures'/f'{name}-{time.time_ns()}.json',dict(stage=name,exception=str(exc),reads=ACCESS,automatic_retry=False))
        progress(name+'_failed',reason=str(exc));raise
    finally:lock.unlink(missing_ok=True)
def asset(path,arm,purpose):
    p=Path(path);entry=contract()['assets'].get(rel(p));require(entry is not None,'Unregistered numeric asset')
    require(arm in ['D-P','D-G'] and entry['arm']==arm,'Wrong side identity permission')
    checked(p,entry['sha256'],purpose,arm)
    require(read(p.with_suffix('.json'))['sha256']==entry['sha256'],'Artifact metadata changed')
    return torch.load(p,map_location=device(),weights_only=True)
def task(r,arm):return asset(SOURCE/'pilot/tasks'/r['id']/f'{arm}.pt',arm,'source-task')
def reference(r,arm):return asset(REF/'models'/r['id']/f'{arm}.pt',arm,'q-one-reference')
def load_own(path):
    p=Path(path);info=read(p.with_suffix('.json'));require(sha(p)==info['sha256'],'Own artifact changed')
    return torch.load(p,map_location=device(),weights_only=True)
def production():
    A=module('amplitude',ROOT/'eval/dynamic_soft_drift_calibration/amplitude.py')
    R=module('iv2_frozen_recovery',ROOT/'eval/dynamic_soft_drift_calibration/recovery.py')
    U=module('iv2_old_math',ROOT/'eval/dynamic_soft_drift_calibration/unroll.py')
    O=module('iv2_frozen_oracle',ROOT/'eval/dynamic_soft_drift_calibration_repair/oracle.py')
    return A,R,U,O
def solver():return module('iv2_frozen_solver',ROOT/'eval/calibrated_deployment_transfer_v4/optimizer_preconditioning.py')
def register():
    configure();require(not (OUT/'manifests/seal.json').exists(),'Already registered')
    rc=read(REF/'manifests/repair-contract.json');rv=read(REF/'verification.json');end=read(REF/'completion.json')
    require(end['passed'] and end['new_classifier_fits']==24 and sha(REF/'verification.json')==end['verification_sha256'],'Reference completion')
    parent=dict(rc['parent_files']);parent.update(rv['files']);parent.update(rc['source_sha256'])
    for p in [REF/'completion.json',REF/'verification.json',REF/'awaiting-decision.json',REF/'stages/report.json']:
        parent[rel(p)]=sha(p)
    for p,h in parent.items():require(sha(ROOT/p)==h,'Parent hash changed')
    assets={};audit=[]
    for r in rc['roles']:
        require(r['inner'] is not None and r['target'] not in r['sources']+[r['calibration']],'Target deployment source leak')
        require(not set(r['train_contents'])&set(r['validation_contents']),'Content overlap')
        for arm in ['D-P','D-G']:
            for p in [SOURCE/'pilot/tasks'/r['id']/f'{arm}.pt',REF/'models'/r['id']/f'{arm}.pt']:
                info=read(p.with_suffix('.json'));require(sha(p)==info['sha256'],'Asset hash')
                assets[rel(p)]=dict(sha256=info['sha256'],arm=arm,role_id=r['id'])
                if 'optimizer' in info:
                    log=info['optimizer'];require(log['accepted'] and all(acceptance_gates(log['objective'],log['initial_objective'],
                           log['max_gradient'],log['iterations'],log['objective_replay_error'],log['gradient_replay_error']).values()),'Reference precision')
                    audit.append(dict(role_id=r['id'],arm=arm,path=rel(p),reused=True,refit=False))
    own={rel(p):sha(p) for p in Path(__file__).parent.glob('*.py')}
    math=dict(rc['math_source_sha256']);math[rel(ROOT/'eval/dynamic_soft_drift_calibration_repair/oracle.py')]=sha(ROOT/'eval/dynamic_soft_drift_calibration_repair/oracle.py')
    env=dict(python=sys.executable,torch=torch.__version__,cuda=torch.version.cuda,gpu=torch.cuda.get_device_name(0),dtype='float64',CPU_fallback=False)
    c=dict(version='inner-v2-full-slot-spectral-GD',roles=rc['roles'],assets=assets,parent_files=parent,
           source_sha256=own,math_source_sha256=math,environment=env,plan_sha256=sha(PLAN),K_ladder=[64,128,256],
           gates=dict(objective=.01,remaining=.01,gradient=.001,CE_mean=.02,CE_row=.05,TV_mean=.02,TV_row=.05,
                      logit_RMSE=.10,margin=.02,weak_changes=1),q_alt=[.9,1.1]*5,q_one_refits=0,q_alt_fit_cap=24,
           formal_matrix_authorized=False,original_classifier_objective_changed=False,finite_surrogate_changed=True)
    write(OUT/'manifests/contract.json',c);write(OUT/'manifests/seal.json',dict(contract_sha256=sha(OUT/'manifests/contract.json')))
    write(OUT/'manifests/numeric-policy.json',POLICY);write(OUT/'environment.json',env)
    save(pd.DataFrame(audit),OUT/'audits/reference-reuse.parquet');progress('inner_v2_registered',references_reused=24,reference_refits=0)
