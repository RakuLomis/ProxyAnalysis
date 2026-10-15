"""Fine-validation v2 IO; previous mathematics and artifacts remain read-only."""
from pathlib import Path
import contextlib
import inspect
import os
import sys
import time
os.environ.setdefault('CUBLAS_WORKSPACE_CONFIG', ':4096:8')
import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F
import importlib.util

ROOT=Path(__file__).resolve().parents[2]
OLD_CODE=ROOT/'eval/dynamic_soft_drift_implicit_pilot'
PARENT=ROOT/'outputs/dynamic-soft-drift-implicit-pilot-20261012/run-01'
CLOSE=ROOT/'outputs/dynamic-soft-drift-implicit-closeout-20261012/run-01'
SOURCE=ROOT/'outputs/dynamic-soft-drift-calibration-20261012/run-01'
REF=ROOT/'outputs/dynamic-soft-drift-calibration-repair-20261012/run-01'
COORD=ROOT/'outputs/dynamic-soft-drift-inner-v2-20261012/run-01'
OUT=ROOT/'outputs/dynamic-soft-drift-implicit-v2-20261012/run-01'
DOC=ROOT/'docs/dynamic-soft-drift-calibration/implicit-v2-20261012'
PLAN=ROOT/'plan/dynamic-soft-drift-implicit-fine-validation-v2-plan-20261012.md'

def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(spec)
    sys.modules[name]=m; spec.loader.exec_module(m); return m

PR=module('fine_validation_previous_io',OLD_CODE/'common.py')
PR.IO.OUT=OUT; PR.IO.DOC=DOC
for n in ['require','read','sha','rel','device','configure','tensor','block','size','weighted','POLICY','SOLVER',
          'acceptance_gates','writable','write','save','put','textfile','progress','checked','cuda','production','solver']:
    globals()[n]=getattr(PR,n)
ACCESS=PR.ACCESS; _C=None

def contract():
    global _C
    if _C is None:
        p=OUT/'manifests/contract.json'
        require(sha(p)==read(p.with_name('seal.json'))['contract_sha256'],'Contract changed')
        _C=read(p)
    return _C

def integrity():
    for p,h in contract()['parent_files'].items():require(sha(ROOT/p)==h,'Parent changed '+p)

@contextlib.contextmanager
def stage(name):
    configure(); ACCESS.clear(); c=contract(); checked(PLAN,c['plan_sha256'],'approved-plan')
    for p,h in c['code'].items():checked(ROOT/p,h,'sealed-v2-code')
    integrity(); checked(Path(c['environment']['installed_LBFGS_path']),c['environment']['installed_LBFGS_sha256'],'installed-solver')
    marker=OUT/'stages'/f'{name}.json'; require(not marker.exists(),'No completed stage overwrite')
    lock=OUT/'stage.lock'; lock.parent.mkdir(parents=True,exist_ok=True)
    fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY); os.write(fd,str(os.getpid()).encode()); os.close(fd)
    began=time.time()
    try:
        progress(name+'_running',pid=os.getpid());yield
        write(marker,dict(execution_complete=True,seconds=time.time()-began,reads=list(ACCESS)))
        progress(name+'_complete',seconds=time.time()-began)
    except BaseException as exc:
        write(OUT/'failures'/f'{name}-{time.time_ns()}.json',dict(stage=name,type=type(exc).__name__,exception=str(exc),
              reads=list(ACCESS),automatic_retry=False))
        progress(name+'_failed',reason=str(exc));raise
    finally:lock.unlink(missing_ok=True)

def asset(p,arm,purpose):
    p=Path(p); a=contract()['assets'].get(rel(p))
    require(a is not None and a['arm']==arm and arm in ['D-P','D-G'],'Asset identity permission')
    checked(p,a['sha256'],purpose,arm)
    require(read(p.with_suffix('.json'))['sha256']==a['sha256'],'Metadata changed')
    return torch.load(p,map_location=device(),weights_only=True)

def task(r,arm):return asset(SOURCE/'pilot/tasks'/r['id']/f'{arm}.pt',arm,'source-task')
def reference(r,arm):return asset(REF/'models'/r['id']/f'{arm}.pt',arm,'old-source-reference')
def coordinate(r,arm):return asset(COORD/'coordinates'/r['id']/f'{arm}.pt',arm,'frozen-training-coordinate')
def own(p):
    p=writable(p); info=read(p.with_suffix('.json'));checked(p,info['sha256'],'own-numeric')
    return torch.load(p,map_location=device(),weights_only=True)

def math_modules():
    g=module('gauge',OLD_CODE/'gauge.py')
    im=module('implicit',OLD_CODE/'implicit.py')
    ob=module('fv_frozen_oracle_bridge',OLD_CODE/'oracle_bridge.py')
    return g,im,ob

def register():
    configure(); require(not (OUT/'manifests/seal.json').exists(),'Already registered')
    pc=read(PARENT/'manifests/contract.json'); pe=read(PARENT/'completion.json'); pv=read(PARENT/'verification.json')
    ce=read(CLOSE/'completion.json'); cv=read(CLOSE/'verification.json')
    require(pe['status']=='stop_implicit_gradient_not_verified' and not pe['numeric_qualified'],'Preserve old stop')
    require(sha(PARENT/'verification.json')==pe['verification_sha256'] and sha(CLOSE/'verification.json')==ce['verification_sha256'],'Parent verification')
    require(cv['parent_files_unchanged'],'Closeout integrity')
    parent={**pc['parent_files'],**pc['code'],**pc['math_code'],**pv['files']}
    for directory in [PARENT,CLOSE]:
        for p in directory.rglob('*'):
            if p.is_file():parent[rel(p)]=sha(p)
    for p in (ROOT/'docs/dynamic-soft-drift-calibration/implicit-20261012').glob('*.md'):parent[rel(p)]=sha(p)
    for p in (ROOT/'eval/dynamic_soft_drift_implicit_closeout').glob('*.py'):parent[rel(p)]=sha(p)
    assets=dict(pc['assets']); first=pc['selected'][0]['id']; reused={}
    for key in ['one-center','one-all-h0-plus','one-all-h0-minus']:
        reused[key]={}
        for level in [0,1]:
            p=PARENT/'endpoints'/first/'D-P'/f'{key}-level{level}.pt'; info=read(p.with_suffix('.json'))
            require(sha(p)==info['sha256'],'Reuse SHA')
            assets[rel(p)]=dict(sha256=info['sha256'],arm='D-P',role_id=first)
            reused[key][str(level)]=rel(p)
    for r in pc['selected']:
        require(not set(r['train_contents'])&set(r['validation_contents']),'Content leakage')
        require(r['target'] not in r['sources']+[r['calibration']],'Target leakage')
    for p,h in parent.items():require(sha(ROOT/p)==h,'Parent changed '+p)
    env=dict(pc['environment']);require(env['torch']==torch.__version__ and env['gpu']==torch.cuda.get_device_name(0),'Environment changed')
    c=dict(version='fine-validation-implicit-v2',roles=pc['roles'],selected=pc['selected'],assets=assets,parent_files=parent,
        reused=reused,first_role=first,q_one=pc['q_one'],q_alt=pc['q_alt'],h=pc['h'],directions=pc['directions'],
        code={rel(p):sha(p) for p in Path(__file__).parent.glob('*.py')},plan_sha256=sha(PLAN),environment=env,
        gates=pc['gates'],fine_gradient=1e-9,coarse_diagnostic=1e-8,Newton_max=30,Armijo_c1=1e-4,backtrack=.5,backtrack_max=25,
        validation=dict(steps=1,step_size=1.,system_backward_error=1e-12,independent_step_relative=1e-8,
              objective_rounding=1e-12,platform_gradient=1e-12,platform_relative_step=1e-10),
        caps=dict(new_LR=202,old_reference_refinements=11,validation_steps=216,refinement_steps=6390,implicit_evaluations=48),
        old_CF_metric='diagnostic_only',new_metric='fine_vs_actual_single_Newton_validation',
        formal_matrix_authorized=False,target_C_U_H_numeric_reads=0,PCAP_reads=0)
    write(OUT/'manifests/contract.json',c);write(OUT/'manifests/seal.json',dict(contract_sha256=sha(OUT/'manifests/contract.json')))
    write(OUT/'manifests/numeric-policy.json',POLICY);write(OUT/'environment.json',env)
    write(OUT/'ledger.json',dict(new_LR_attempted=0,new_LR_accepted=0,old_reference_refinements=0,
         fine_states_reused=0,fine_states_created=0,refinement_steps=0,validation_steps=0,implicit_evaluations=0,
         formal_classifier_fits=0,new_mapping_fits=0))
    progress('fine_validation_registered',roles=6,old_fine_reuse=3)

def ledger(**delta):
    p=OUT/'ledger.json';v=read(p)
    for k,n in delta.items():v[k]+=n
    cap=contract()['caps']
    require(v['new_LR_attempted']<=cap['new_LR'] and v['validation_steps']<=cap['validation_steps'] and
            v['refinement_steps']<=cap['refinement_steps'] and v['implicit_evaluations']<=48,'Budget exceeded')
    write(p,v)
