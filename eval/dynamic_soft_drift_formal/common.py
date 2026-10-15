"""Solution-level formal experiment: role-scoped IO and immutable lineage."""
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

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'outputs/dynamic-soft-drift-business-formal-20261012/run-01'
DOC = ROOT/'docs/dynamic-soft-drift-calibration/formal-20261012'
PLAN = ROOT/'plan/dynamic-soft-drift-solution-business-formal-plan-20261012.md'
DS = ROOT/'outputs/dynamic-soft-drift-calibration-20261012/run-01'
V2 = ROOT/'outputs/dynamic-soft-drift-implicit-v2-20261012/run-01'
JA = ROOT/'outputs/joint-affine-transfer-20261007/run-01'
TI = ROOT/'outputs/strongpost-training-intervention-20261009/run-01'
AG = ROOT/'outputs/invariant-anchor-guarded-drift-20261012/run-01'
SA = ROOT/'outputs/small-view-attribution-20261010/run-02'
CJ = ROOT/'outputs/connection-joint-response-20261010/run-01'

def module(name, path):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m

base=module('formal_frozen_definitions',ROOT/'eval/calibrated_deployment_transfer/common.py')
for n in ['PROTOCOLS','LABELS','HIST','FEATURES','MASKS','require','read','sha','rel',
          'device','configure','tensor','block','size','truths','weighted','scaler']:
    globals()[n]=getattr(base,n)
PREP=base.OUT
policy=module('formal_v4_policy',ROOT/'eval/calibrated_deployment_transfer_v4/numeric_policy.py')
POLICY,SOLVER,acceptance_gates=policy.POLICY,policy.SOLVER,policy.acceptance_gates
ARMS=['D-P','T-P','D-G']
REFERENCES=['S','P-small','G-small','RawPre-small','RawPost-small','Marginal-small','M-S']
ALL_ARMS=ARMS+REFERENCES
PRIMARY=['P-small','T-P','D-G','G-small','RawPre-small','S','M-S']
ACCESS=[]
_C=None
_HASH={}
_PRODUCTION=None
_TASKS={}

def writable(p):
    p=Path(p).resolve();require(p.is_relative_to(OUT) or p.is_relative_to(DOC),'Write outside formal roots');p.parent.mkdir(parents=True,exist_ok=True);return p

def write(p,v):
    p=writable(p);tmp=p.with_name(p.name+'.tmp')
    tmp.write_text(json.dumps(v,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False,default=base.json_scalar)+'\n',encoding='utf-8');os.replace(tmp,p)

def save(d,p):
    p=writable(p);tmp=p.with_name(p.name+'.tmp');d.to_parquet(tmp,index=False);os.replace(tmp,p)

def textfile(p,s):writable(p).write_text(s,encoding='utf-8')

def put(v,p,**meta):
    p=writable(p);require(not p.exists() and not p.with_suffix('.json').exists(),'Refuse accepted artifact overwrite: '+rel(p))
    tmp=p.with_name(p.name+'.tmp');torch.save(v,tmp);os.replace(tmp,p);write(p.with_suffix('.json'),dict(sha256=sha(p),**meta))

def checked(p,h,purpose,arm=None):
    p=Path(p);sig=(p.stat().st_size,p.stat().st_mtime_ns)
    if _HASH.get(str(p))!=(sig,h):require(sha(p)==h,'Changed input '+str(p));_HASH[str(p)]=(sig,h)
    ACCESS.append(dict(path=rel(p) if p.is_relative_to(ROOT) else str(p),sha256=h,purpose=purpose,arm=arm))

def contract():
    global _C
    if _C is None:
        p=OUT/'manifests/experiment-contract.json';require(sha(p)==read(p.with_name('seal.json'))['contract_sha256'],'Contract changed');_C=read(p)
    return _C

def role_permission(r,inner=None):
    require(not set(r['train_contents'])&set(r['validation_contents']),'Content overlap')
    require(not set(r['C_contents'])&set(r['U_contents']),'C/U overlap')
    require(set(r['C_contents'])|set(r['U_contents'])==set(r['train_contents']),'C/U partition')
    if inner is True:require(r['inner'] is not None and r['target'] not in r['sources']+[r['calibration']],'Actual target in source feedback')

def kind_permission(kind,purpose,arm):
    allowed={'source-train':{'source-pre','source-post','C-post'},
             'source-feedback':{'main-query','main-inner-labels'},
             'final-train':{'source-pre','source-post','C-post'},
             'C-P-fit':{'P-train'},'C-P-query':{'P-query'},'C-P-score':{'P-score'},
             'C-G-fit':{'G-pre-train','G-post-train'},'C-G-query':{'G-query'},
             'C-G-score':{'G-score'},'C-anonymous-post':{'G-post-full'},
             'H-query':{'main-query'},'H-score':{'main-outer-labels'}}
    require(kind in allowed.get(purpose,set()),'Forbidden package kind/purpose '+str((kind,purpose)))
    require(not (arm=='D-G' and purpose.startswith('C-P')),'G cannot read P correspondence')
    require(not (arm in ['D-P','T-P'] and purpose.startswith('C-G')),'P cannot read G-specific targets')

def package(p,purpose,arm,r):
    p=Path(p);info=contract()['packages'].get(rel(p));require(info is not None,'Unregistered package')
    require(info['role_id']==r['id'],'Wrong role package')
    role_permission(r,purpose.startswith('source-'))
    kind_permission(info['kind'],purpose,arm)
    if purpose.startswith('source-'):require(r['inner'] is not None,'Outer H cannot masquerade as source feedback')
    if purpose=='final-train':require(r['inner'] is None,'Final train outer roles only')
    if purpose=='H-query':
        require(r['inner'] is None and (OUT/'manifests/models-complete.json').exists(),'Seal all models before H query')
        verify_seal(OUT/'manifests/models-complete.json')
    if purpose=='H-score':
        require(r['inner'] is None and (OUT/'predictions/complete.json').exists(),'Seal all predictions before H labels')
        verify_seal(OUT/'predictions/complete.json')
    checked(p,info['sha256'],purpose,arm);d=pd.read_parquet(p)
    require(list(d)==info['columns'] and len(d)==info['rows'],'Schema/count changed')
    if 'content_id' in d:
        allowed=r['validation_contents'] if purpose in ['source-feedback','H-query','H-score'] else r['train_contents']
        require(set(d.content_id)<=set(allowed),'Package content scope')
    if info['kind'] in ['source-pre','source-post']:
        n=144 if r['inner'] is not None else 288
        require(len(d)==n and set(d.protocol)==set(r['sources']) and d.groupby(['protocol','content_id']).size().eq(4).all(),'Source repetitions/deployments')
        if info['kind']=='source-pre':require(not {'visit_id','session_id'}&set(d),'Exact source identity forbidden')
    if info['kind']=='C-post':
        require(len(d)==(48 if r['inner'] is not None else 64) and set(d.content_id)==set(r['C_contents']) and set(d.protocol)=={r['calibration']},'C scope')
    if purpose.startswith('C-'):
        tokens={hashlib.sha256(('ja-content:'+u).encode()).hexdigest() for u in r['C_contents']}
        require(set(d.content_token)<=tokens and not {'label_id','protocol','content_id','visit_id','repetition','pair_id'}&set(d),'C-only identity/label schema')
        if purpose.startswith('C-G') or purpose=='C-anonymous-post':
            require(set(d)<={'content_token','query_key','fit_mass',*HIST},'Anonymous group schema')
    if purpose in ['H-query','source-feedback'] and info['kind']=='main-query':base.validate_query(d)
    return d

def artifact(p,kind,arm,r=None):
    p=Path(p);require(kind in ['shared','P','G'],'Unknown artifact kind')
    require(not (arm=='D-G' and kind=='P') and not (arm in ['D-P','T-P'] and kind=='G'),'Cross-arm artifact read')
    info=contract()['artifacts'].get(rel(p));require(info is not None,'Unregistered artifact')
    require(info['kind']==kind,'Artifact namespace mismatch')
    if r is not None:require(info['role_id']==r['id'],'Wrong artifact role')
    checked(p,info['sha256'],'artifact',arm);require(read(p.with_suffix('.json'))['sha256']==info['sha256'],'Artifact metadata mismatch')
    return torch.load(p,map_location=device(),weights_only=True)

def own(p):
    p=Path(p);info=read(p.with_suffix('.json'));checked(p,info['sha256'],'own-artifact');return torch.load(p,map_location=device(),weights_only=True)

def verify_seal(p):
    for path,h in read(p)['files'].items():checked(ROOT/path,h,'stage-seal')

def progress(stage,**v):
    write(OUT/'progress.json',dict(stage=stage,time_unix=time.time(),**v));print(stage,v,flush=True)

def disk_gate():
    # Conservative pre-registered thin-state estimate: <=200 KiB/point plus 1 GiB ancillary.
    remaining=45360*200*1024+1024**3
    required=max(10*1024**3,2*remaining+5*1024**3)
    free=shutil.disk_usage(OUT if OUT.exists() else ROOT).free
    require(free>=required,'Resource pause: disk reserve');return dict(free=free,required=required,estimated_remaining=remaining)

@contextlib.contextmanager
def stage(name):
    configure();c=contract();ACCESS.clear()
    checked(PLAN,c['plan_sha256'],'approved-plan')
    for p,h in {**c['code'],**c['fixed_files']}.items():checked(ROOT/p,h,'code-or-lineage')
    checked(Path(c['environment']['installed_LBFGS_path']),c['environment']['installed_LBFGS_sha256'],'installed-solver')
    marker=OUT/'stages'/f'{name}.json';require(not marker.exists(),'Completed stage overwrite')
    lock=OUT/'stage.lock';fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY);os.write(fd,str(os.getpid()).encode());os.close(fd)
    began=time.perf_counter()
    try:
        progress(name+'_running',pid=os.getpid());yield
        write(marker,dict(passed=True,seconds=time.perf_counter()-began,reads=ACCESS))
        progress(name+'_complete',seconds=time.perf_counter()-began)
    except BaseException as exc:
        write(OUT/'failures'/f'{name}-{time.time_ns()}.json',dict(stage=name,type=type(exc).__name__,exception=str(exc),traceback=traceback.format_exc(),automatic_retry=False,reads=ACCESS))
        write(OUT/'completion.json',dict(status='stop_formal_gate_failure',passed=False,formal_complete=False,H_scored=False,reason=str(exc),stage=name))
        progress(name+'_failed',reason=str(exc));raise
    finally:lock.unlink(missing_ok=True)

def cuda(*xs):
    for x in xs:require(isinstance(x,torch.Tensor) and x.is_cuda and x.dtype==torch.float64,'CUDA float64 required')

def solver():return module('formal_accepted_solver',ROOT/'eval/calibrated_deployment_transfer_v4/optimizer_preconditioning.py')

def production():
    global _PRODUCTION
    if _PRODUCTION is not None:return _PRODUCTION
    a=module('amplitude',ROOT/'eval/dynamic_soft_drift_calibration/amplitude.py')
    u=module('unroll',ROOT/'eval/dynamic_soft_drift_calibration/unroll.py')
    rec=module('formal_recovery',ROOT/'eval/dynamic_soft_drift_calibration/recovery.py')
    _PRODUCTION=(a,u,None,rec);return _PRODUCTION

def task(r,arm):
    kind='G' if arm=='D-G' else 'P'
    require((r['id'],kind) in _TASKS,'Unregistered current source task')
    return _TASKS[(r['id'],kind)]

def install_tasks(values):
    _TASKS.clear();_TASKS.update(values)

def ledger(**delta):
    p=OUT/'ledger.json';v=read(p)
    for k,n in delta.items():v[k]+=n
    for k,limit in contract()['caps'].items():require(v[k]<=limit,'Budget exceeded '+k)
    write(p,v)

def group_schema(d):require(set(d)=={'content_token','fit_mass',*HIST},'Anonymous group schema')
