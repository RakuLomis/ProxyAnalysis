"""Restricted source-only IO for the independently registered outer pilot."""
from pathlib import Path
import contextlib
import hashlib
import importlib.util
import inspect
import json
import os
import shutil
import sys
import time
import traceback
os.environ.setdefault('CUBLAS_WORKSPACE_CONFIG', ':4096:8')
import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
OUT=ROOT/'outputs/dynamic-soft-drift-outer-pilot-20261013/run-02'
DOC=ROOT/'docs/dynamic-soft-drift-calibration/outer-pilot-20261013/run-02'
PARENT=ROOT/'outputs/dynamic-soft-drift-business-formal-20261012/run-02'
PLAN=ROOT/'plan/dynamic-soft-drift-outer-optimization-pilot-plan-20261013.md'
ARM_KIND={'O-DP':'P','O-TP':'P','O-DG':'G'}
ARMS=list(ARM_KIND)
ACCESS=[]
_C=None
_HASH={}
_TASKS={}
_MATH=None
_CLOCK=None

def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m

base=module('outer_frozen_definitions',ROOT/'eval/calibrated_deployment_transfer/common.py')
for n in ['PROTOCOLS','LABELS','HIST','FEATURES','MASKS','require','read','sha','rel',
          'device','configure','tensor','block','size','truths','weighted','scaler']:
    globals()[n]=getattr(base,n)
policy=module('outer_frozen_policy',ROOT/'eval/calibrated_deployment_transfer_v4/numeric_policy.py')
POLICY,SOLVER,acceptance_gates=policy.POLICY,policy.SOLVER,policy.acceptance_gates
payload=module('payload',ROOT/'eval/dynamic_soft_drift_formal_v2/payload.py')

class BudgetStop(RuntimeError):pass

def writable(p):
    p=Path(p).resolve();require(p.is_relative_to(OUT) or p.is_relative_to(DOC),'Write outside pilot roots')
    p.parent.mkdir(parents=True,exist_ok=True);return p

def write(p,v):
    p=writable(p);tmp=p.with_name(p.name+'.tmp')
    tmp.write_text(json.dumps(v,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False,default=base.json_scalar)+'\n',encoding='utf-8');os.replace(tmp,p)

def save(d,p):
    p=writable(p);tmp=p.with_name(p.name+'.tmp');d.to_parquet(tmp,index=False);os.replace(tmp,p)

def textfile(p,s):writable(p).write_text(s,encoding='utf-8')

def put(v,p,**meta):
    p=writable(p);require(not p.exists() and not p.with_suffix('.json').exists(),'Refuse checkpoint overwrite')
    safe=payload.normalize(v);tmp=p.with_name(p.name+'.tmp');torch.save(safe,tmp)
    replay=torch.load(tmp,map_location=device(),weights_only=True);payload.assert_identical(safe,replay)
    os.replace(tmp,p);write(p.with_suffix('.json'),dict(sha256=sha(p),safe_roundtrip_passed=True,payload_schema='builtin-and-tensor-v2',**meta))

def checked(p,h,purpose,kind=None):
    p=Path(p).resolve();sig=(p.stat().st_size,p.stat().st_mtime_ns)
    if _HASH.get(str(p))!=(sig,h):require(sha(p)==h,'Changed input '+str(p));_HASH[str(p)]=(sig,h)
    ACCESS.append(dict(path=rel(p) if p.is_relative_to(ROOT) else str(p),sha256=h,purpose=purpose,kind=kind))

def contract():
    global _C
    if _C is None:
        p=OUT/'manifests/experiment-contract.json';require(sha(p)==read(p.with_name('seal.json'))['contract_sha256'],'Pilot contract changed');_C=read(p)
    return _C

def kind_for(arm):
    require(arm in ARM_KIND,'Unknown display arm');return ARM_KIND[arm]

def role_permission(r,inner):
    require(r['outer']==0 and not set(r['train_contents'])&set(r['validation_contents']),'Pilot fold/content scope')
    require(not set(r['C_contents'])&set(r['U_contents']),'C/U overlap')
    require(set(r['C_contents'])|set(r['U_contents'])==set(r['train_contents']),'C/U partition')
    if inner:require(r['inner'] is not None and r['target'] not in r['sources']+[r['calibration']],'Actual target in source feedback')

def parent_asset(p,category,kind,role_id,actor):
    p=Path(p).resolve();info=contract()['inputs'].get(rel(p))
    require(info is not None,'Unregistered/forbidden parent read: '+rel(p))
    require(info['category']==category and info['kind']==kind and info['role_id']==role_id,'Parent scope mismatch')
    if actor in ARMS:
        require(kind_for(actor)==kind,'Cross-kind read')
        require(not (actor=='O-TP' and category=='coefficients'),'T cannot read recovery targets')
    else:require(actor in ['trusted-packer','initial-audit','report'],'Unknown reader')
    checked(p,info['sha256'],category,kind)
    if p.suffix=='.pt':
        mp=p.with_suffix('.json');mi=contract()['inputs'][rel(mp)];checked(mp,mi['sha256'],'asset-metadata',kind)
        meta=read(mp);require(meta['sha256']==info['sha256'] and meta.get('safe_roundtrip_passed'),'Unsafe parent asset')
        return torch.load(p,map_location=device(),weights_only=True)
    return pd.read_parquet(p)

def own(p):
    p=Path(p).resolve();require(p.is_relative_to(OUT),'Own read outside pilot')
    m=read(p.with_suffix('.json'));checked(p,m['sha256'],'own-artifact',m.get('kind'))
    require(m['safe_roundtrip_passed'],'Unpublished safe asset');return torch.load(p,map_location=device(),weights_only=True)

def cuda(*xs):
    for x in xs:require(isinstance(x,torch.Tensor) and x.is_cuda and x.dtype==torch.float64,'CUDA float64 required')

def production():
    global _MATH
    if _MATH is None:
        a=module('amplitude',ROOT/'eval/dynamic_soft_drift_calibration/amplitude.py')
        u=module('unroll',ROOT/'eval/dynamic_soft_drift_calibration/unroll.py')
        rec=module('outer_recovery',ROOT/'eval/dynamic_soft_drift_calibration/recovery.py')
        _MATH=(a,u,None,rec)
    return _MATH

def task(r,legacy_arm):
    # Only the sealed mathematical adapter receives legacy names.
    require(legacy_arm in ['D-P','D-G'],'Unknown mathematical arm')
    kind={'D-P':'P','D-G':'G'}[legacy_arm]
    require((r['id'],kind) in _TASKS,'Task not installed in typed scope');return _TASKS[(r['id'],kind)]

def install_tasks(v):_TASKS.clear();_TASKS.update(v)
def solver():return module('outer_accepted_solver',ROOT/'eval/calibrated_deployment_transfer_v4/optimizer_preconditioning.py')
def group_schema(d):require(set(d)=={'content_token','fit_mass',*HIST},'Anonymous group schema')

def progress(stage,**v):
    write(OUT/'progress.json',dict(stage=stage,time_unix=time.time(),**v));print(stage,v,flush=True)

def start_clock():
    global _CLOCK
    require(_CLOCK is None,'Active clock already running');_CLOCK=(time.perf_counter(),read(OUT/'ledger.json')['active_seconds'])

def ledger(**delta):
    p=OUT/'ledger.json';v=read(p)
    for k,n in delta.items():require(k in v,'Unknown budget counter');v[k]+=n
    if _CLOCK is not None:v['active_seconds']=_CLOCK[1]+time.perf_counter()-_CLOCK[0]
    for k,limit in contract()['caps'].items():require(v[k]<=limit,'Budget exceeded '+k)
    write(p,v);return v

def resource_gate():
    v=ledger()
    if v['active_seconds']>=14400:raise BudgetStop('Four-hour cumulative active compute limit')
    remaining=max(0,17712-v['new_source_LR'])*200*1024+1024**3
    required=max(10*1024**3,2*remaining+5*1024**3)
    free=shutil.disk_usage(OUT).free
    if free<required:raise BudgetStop('Disk reserve limit')
    return dict(free=free,required=required,estimated_remaining=remaining)

def validate_environment():
    configure();e=contract()['environment']
    require(sys.executable.lower()==e['python'].lower() and torch.__version__==e['torch'],'Runtime mismatch')
    checked(Path(e['installed_LBFGS_path']),e['installed_LBFGS_sha256'],'installed-solver')

@contextlib.contextmanager
def stage(name):
    validate_environment();ACCESS.clear();c=contract()
    checked(PLAN,c['plan_sha256'],'approved-plan')
    for p,h in {**c['code'],**c['fixed_code'],**c['parent_metadata']}.items():checked(ROOT/p,h,'frozen-lineage')
    marker=OUT/'stages'/f'{name}.json';require(not marker.exists(),'Completed stage overwrite')
    lock=OUT/'stage.lock';fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY);os.write(fd,str(os.getpid()).encode());os.close(fd)
    began=time.perf_counter()
    try:
        progress(name+'_running',pid=os.getpid());yield
        write(marker,dict(passed=True,seconds=time.perf_counter()-began,reads=ACCESS))
    except BaseException as exc:
        write(OUT/'failures'/f'{name}-{time.time_ns()}.json',dict(type=type(exc).__name__,exception=str(exc),traceback=traceback.format_exc(),reads=ACCESS,automatic_retry=False))
        raise
    finally:lock.unlink(missing_ok=True)
