"""Read-only parent, independent repair writes, CUDA-only source model arithmetic."""
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
PARENT=ROOT/'outputs/dynamic-soft-drift-calibration-20261012/run-01'
OUT=ROOT/'outputs/dynamic-soft-drift-calibration-repair-20261012/run-01'
DOC=ROOT/'docs/dynamic-soft-drift-calibration/repair-20261012'
PLAN=ROOT/'plan/dynamic-soft-drift-gradient-inner-repair-plan-20261012.md'
OLD_CODE=ROOT/'eval/dynamic_soft_drift_calibration'

def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m

base=module('dsr_original_definitions',ROOT/'eval/calibrated_deployment_transfer/common.py')
for name in ['PROTOCOLS','LABELS','HIST','FEATURES','require','read','sha','rel','device','configure',
             'tensor','block','size','weighted']:
    globals()[name]=getattr(base,name)
policy=module('dsr_original_policy',ROOT/'eval/calibrated_deployment_transfer_v4/numeric_policy.py')
POLICY,SOLVER,acceptance_gates=policy.POLICY,policy.SOLVER,policy.acceptance_gates
ACCESS=[]
_C=None
ARMS=['D-P','T-P','D-G']

def writable(path):
    p=Path(path).resolve();require(p.is_relative_to(OUT) or p.is_relative_to(DOC),'Write outside repair roots');return p
def write(path,value):
    p=writable(path);p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_name(p.name+'.tmp')
    tmp.write_text(json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False,
                             default=base.json_scalar)+'\n',encoding='utf-8');os.replace(tmp,p)
def save(df,path):
    p=writable(path);p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_name(p.name+'.tmp')
    df.to_parquet(tmp,index=False);os.replace(tmp,p)
def put(obj,path,**meta):
    p=writable(path);require(not p.exists(),'Refuse accepted artifact overwrite');p.parent.mkdir(parents=True,exist_ok=True)
    tmp=p.with_name(p.name+'.tmp');torch.save(obj,tmp);os.replace(tmp,p);write(p.with_suffix('.json'),dict(sha256=sha(p),**meta))
def textfile(path,text):
    p=writable(path);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf-8')
def progress(stage,**info):
    write(OUT/'progress.json',dict(stage=stage,time_unix=time.time(),**info));print(stage,info,flush=True)
def checked(path,expected,purpose,arm=None):
    p=Path(path);label=rel(p) if p.resolve().is_relative_to(ROOT) else p.as_posix()
    require(sha(p)==expected,'Changed sealed input '+label);ACCESS.append(dict(path=label,sha256=expected,purpose=purpose,arm=arm))
def contract():
    global _C
    if _C is None:
        p=OUT/'manifests/repair-contract.json';require(sha(p)==read(p.with_name('seal.json'))['contract_sha256'],'Repair contract changed');_C=read(p)
    return _C
def parent_integrity():
    c=contract()
    for path,h in c['parent_files'].items():require(sha(ROOT/path)==h,'Parent changed '+path)
    require(read(PARENT/'completion.json')['status']=='stop_numeric_FD_activation_boundary','Parent failure not preserved')
def start(stage):
    configure();ACCESS.clear();c=contract();checked(PLAN,c['plan_sha256'],'approved-plan')
    for p,h in c['source_sha256'].items():checked(ROOT/p,h,'repair-code')
    for p,h in c['math_source_sha256'].items():checked(ROOT/p,h,'unchanged-math')
    require(read(OUT/'manifests/numeric-policy.json')==POLICY,'Numeric policy changed')
    checked(Path(c['environment']['installed_LBFGS_path']),c['environment']['installed_LBFGS_sha256'],'installed-solver')
    parent_integrity();return c
@contextlib.contextmanager
def stage(name):
    start(name);marker=OUT/'stages'/f'{name}.json';require(not marker.exists(),'Stage already complete')
    lock=OUT/'stage.lock';lock.parent.mkdir(parents=True,exist_ok=True)
    fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY);os.write(fd,str(os.getpid()).encode());os.close(fd);began=time.time()
    try:
        progress(name+'_running',pid=os.getpid());yield
        write(marker,dict(passed=True,seconds=time.time()-began,reads=ACCESS));progress(name+'_complete',seconds=time.time()-began)
    except BaseException as exc:
        write(OUT/'failures'/f'{name}-{time.time_ns()}.json',dict(stage=name,type=type(exc).__name__,exception=str(exc),reads=ACCESS,automatic_retry=False))
        progress(name+'_failed',reason=str(exc));raise
    finally:lock.unlink(missing_ok=True)
def asset(path,purpose,arm=None):
    p=Path(path);c=contract();require(rel(p) in c['source_assets'],'Unregistered source asset')
    if arm=='D-G':require('/D-P.' not in rel(p) and '/D-P-' not in rel(p),'Group cannot load paired asset')
    info=read(p.with_suffix('.json'));checked(p,c['source_assets'][rel(p)],purpose,arm)
    require(info['sha256']==c['source_assets'][rel(p)],'Artifact metadata mismatch')
    return torch.load(p,map_location=device(),weights_only=True)
def task(r,arm):
    kind='D-G' if arm=='D-G' else 'D-P'
    require(r['target'] not in r['sources']+[r['calibration']] and r['inner'] is not None,'Actual target source leak')
    return asset(PARENT/'pilot/tasks'/r['id']/f'{kind}.pt','source-task',arm)
def old_gradients(arm,point):return asset(PARENT/'pilot/gradients'/f'{arm}-{point}.pt','saved-source-unroll',arm)
def production():
    A=module('amplitude',OLD_CODE/'amplitude.py')
    R=module('dsr_frozen_recovery',OLD_CODE/'recovery.py')
    U=module('dsr_frozen_unroll',OLD_CODE/'unroll.py')
    return A,R,U
def solver():return module('dsr_frozen_v4_solver',ROOT/'eval/calibrated_deployment_transfer_v4/optimizer_preconditioning.py')

def register():
    configure();require(not (OUT/'manifests/seal.json').exists(),'Repair already registered')
    pc=read(PARENT/'manifests/experiment-contract.json');pv=read(PARENT/'verification.json');end=read(PARENT/'completion.json')
    require(end['status']=='stop_numeric_FD_activation_boundary' and not end['passed'],'Preserve rejected parent')
    require(sha(PARENT/'verification.json')==end['verification_sha256'] and pv['diagnostic_integrity_passed'],'Parent integrity')
    parent_files=dict(pv['files'])
    for p in [PARENT/'verification.json',PARENT/'completion.json',PARENT/'awaiting-decision.json',
              PARENT/'stages/failure_diagnosis.json']:
        parent_files[rel(p)]=sha(p)
    parent_files.update(pc['source_sha256'])
    for p,h in parent_files.items():require(sha(ROOT/p)==h,'Parent sealed file changed')
    source_assets={}
    for r in pc['pilot_roles']:
        require(not set(r['train_contents'])&set(r['validation_contents']),'Content fold leakage')
        require(r['target'] not in r['sources']+[r['calibration']],'Source role has actual target')
        for arm in ['D-P','D-G']:
            p=PARENT/'pilot/tasks'/r['id']/f'{arm}.pt'
            info=read(p.with_suffix('.json'));require(sha(p)==info['sha256'],'Source task hash');source_assets[rel(p)]=info['sha256']
    for arm in ARMS:
        for point in ['one','interior']:
            p=PARENT/'pilot/gradients'/f'{arm}-{point}.pt'
            info=read(p.with_suffix('.json'));require(sha(p)==info['sha256'],'Saved source gradient hash');source_assets[rel(p)]=info['sha256']
    math_sources=dict(pc['source_sha256'])
    for p in [ROOT/'eval/calibrated_deployment_transfer_v4/optimizer_preconditioning.py',
              ROOT/'eval/calibrated_deployment_transfer_v4/numeric_policy.py']:
        math_sources[rel(p)]=sha(p)
    environment=dict(python=sys.executable,torch=torch.__version__,cuda=torch.version.cuda,
                     gpu=torch.cuda.get_device_name(0),device='cuda:0',dtype='float64',CPU_fallback=False,
                     installed_LBFGS_path=inspect.getfile(torch.optim.LBFGS),installed_LBFGS_sha256=sha(Path(inspect.getfile(torch.optim.LBFGS))))
    c=dict(version='activation-aware-repair-v1',registered_unix=time.time(),plan_sha256=sha(PLAN),
           roles=pc['pilot_roles'],source_assets=source_assets,parent_files=parent_files,
           source_sha256={rel(p):sha(p) for p in Path(__file__).parent.glob('*.py')},
           math_source_sha256=math_sources,environment=environment,reference_cap=24,
           trajectory_cap=2952,formal_matrix_authorized=False,scientific_objective_changed=False,
           unroll_trajectory_changed=False,target_C_U_H_numeric_reads=0)
    write(OUT/'manifests/repair-contract.json',c);write(OUT/'manifests/seal.json',dict(contract_sha256=sha(OUT/'manifests/repair-contract.json')))
    write(OUT/'manifests/numeric-policy.json',POLICY);write(OUT/'environment.json',environment)
    progress('repair_registered',roles=12,reference_cap=24,parent_failure_preserved=True)
