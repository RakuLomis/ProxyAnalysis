"""Stage A scoped IO; historical assets are immutable."""
from pathlib import Path
import contextlib
import hashlib
import importlib.util
import json
import os
import sys
import time
import traceback
os.environ.setdefault('CUBLAS_WORKSPACE_CONFIG', ':4096:8')
import numpy as np
import pandas as pd
import pyarrow.dataset as ds
import pyarrow.parquet as pq
import torch
import torch.nn.functional as F

ROOT=Path(__file__).resolve().parents[2]
PARENT=ROOT/'outputs/post-input-associated-representation-20261014/run-01'
OUT=ROOT/'outputs/post-input-associated-representation-20261014/run-02'
DOC=ROOT/'docs/post-input-associated-representation/run-02'
PLAN=ROOT/'plan/post-input-associated-representation-residual-plan-20261014.md'
FORMAL=ROOT/'outputs/dynamic-soft-drift-business-formal-20261012/run-02'
PREP=ROOT/'outputs/calibrated-deployment-business-transfer-20261006/run-01'
NATIVE=ROOT/'outputs/protocol-probability-drift-20261004/run-01/features/paired-flow-features.parquet'
SEEDS=[20261014,20261015,20261016]
CONFIGS=[('A1',0.),('A2',.1),('A2',1.),('A3',.1),('A3',1.)]
ACCESS=[]
_TRAIN_START=None
_CONTRACT_CACHE=None
_CONTRACT_SIGNATURE=None
def module(name,p):
    spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec)
    sys.modules[name]=m;spec.loader.exec_module(m);return m
base=module('post_branch_frozen_definitions',ROOT/'eval/calibrated_deployment_transfer/common.py')
for n in ['require','read','sha','rel','device','configure','tensor','HIST','FEATURES','LABELS','PROTOCOLS','truths','weighted','size','bins']:
    globals()[n]=getattr(base,n)

def writable(p):
    p=Path(p).resolve();require(p.is_relative_to(OUT) or p.is_relative_to(DOC),'Write outside new roots')
    p.parent.mkdir(parents=True,exist_ok=True);return p
def write(p,v):
    p=writable(p);tmp=p.with_name(p.name+'.tmp')
    tmp.write_text(json.dumps(v,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False,
                             default=lambda x:x.item() if isinstance(x,np.generic) else str(x))+'\n',encoding='utf-8')
    os.replace(tmp,p)
def textfile(p,s):writable(p).write_text(s,encoding='utf-8')
def save(d,p):
    p=writable(p);tmp=p.with_name(p.name+'.tmp');d.to_parquet(tmp,index=False);os.replace(tmp,p)
def put(v,p,**meta):
    p=writable(p);require(not p.exists(),'Refuse overwrite accepted tensor '+str(p))
    tmp=p.with_name(p.name+'.tmp');torch.save(v,tmp)
    torch.load(tmp,map_location=device(),weights_only=True);os.replace(tmp,p)
    write(p.with_suffix('.json'),dict(sha256=sha(p),safe_payload=True,**meta))
def own(p,purpose,arm=None):
    p=Path(p)
    if purpose=='branch':
        require('/teacher/' not in p.as_posix() and '/trusted/' not in p.as_posix(),'Branch forbidden teacher/trusted file')
        if arm=='A1':require('/targets/' not in p.as_posix(),'A1/zero lambda forbidden targets')
        if '/targets/' in p.as_posix():require(p.name==arm+'.pt','Cross-arm target read')
    h=read(p.with_suffix('.json'))['sha256'];require(sha(p)==h,'Own artifact changed')
    ACCESS.append(dict(path=rel(p),sha256=h,purpose=purpose,arm=arm))
    return torch.load(p,map_location=device(),weights_only=True)
def contract():
    global _CONTRACT_CACHE,_CONTRACT_SIGNATURE
    p=OUT/'manifests/experiment-contract.json'
    s=p.stat();sig=(s.st_size,s.st_mtime_ns)
    if _CONTRACT_CACHE is None or sig!=_CONTRACT_SIGNATURE:
        require(sha(p)==read(p.with_name('seal.json'))['sha256'],'Contract changed')
        _CONTRACT_CACHE=read(p);_CONTRACT_SIGNATURE=sig
    return _CONTRACT_CACHE
def old(p,purpose):
    p=Path(p);c=contract();h=c['bindings'].get(rel(p));require(h is not None,'Unregistered historical asset')
    require(sha(p)==h,'Historical asset changed');ACCESS.append(dict(path=rel(p),sha256=h,purpose=purpose))
    return torch.load(p,map_location=device(),weights_only=True)
def oldpackage(p,r,purpose):
    p=Path(p);info=contract()['packages'].get(rel(p));require(info is not None and info['role_id']==r['id'],'Wrong historical role package')
    allowed={'prepare':{'source-pre','source-post','C-post'},'inner-predict':{'main-query'},'inner-score':{'main-inner-labels'},
             'H-predict':{'main-query'},'H-score':{'main-outer-labels'}}
    require(info['kind'] in allowed.get(purpose,set()),'Forbidden historical package purpose')
    if purpose.startswith('inner-'):require(r['inner'] is not None,'Actual H as source feedback')
    if purpose=='H-predict':require((OUT/'manifests/models-complete.json').exists(),'Models must seal before H')
    if purpose=='H-score':require((OUT/'predictions/complete.json').exists(),'Predictions must seal before H labels')
    require(sha(p)==info['sha256'],'Historical package changed')
    ACCESS.append(dict(path=rel(p),sha256=info['sha256'],purpose=purpose,role_id=r['id']))
    d=pd.read_parquet(p);require(len(d)==info['rows'] and list(d)==info['columns'],'Schema/count changed')
    return d
def progress(stage,**v):
    write(OUT/'progress.json',dict(stage=stage,time_unix=time.time(),**v));print(stage,v,flush=True)
def ledger(**delta):
    p=OUT/'ledger.json';v=read(p)
    for k,n in delta.items():v[k]=v.get(k,0)+n
    write(p,v)
def seal(p,files,**extra):write(p,dict(files={rel(x):sha(x) for x in files},**extra))
def verifyseal(p):
    for path,h in read(p)['files'].items():require(sha(ROOT/path)==h,'Stage seal changed')
@contextlib.contextmanager
def stage(name,training=False):
    global _TRAIN_START
    configure();c=contract();ACCESS.clear();require(sha(PLAN)==c['plan_sha256'],'Plan changed')
    require(sha(OUT/'manifests/experiment-contract.json')==read(OUT/'manifests/seal.json')['sha256'],'Contract stage seal changed')
    p=OUT/'stages'/f'{name}.json';require(not p.exists(),'Completed stage cannot repeat')
    lock=writable(OUT/'stage.lock');fd=os.open(lock,os.O_EXCL|os.O_CREAT|os.O_WRONLY);os.write(fd,str(os.getpid()).encode());os.close(fd)
    start=time.perf_counter()
    if training:_TRAIN_START=start
    try:
        progress(name+'_running',pid=os.getpid());yield
        write(p,dict(passed=True,seconds=time.perf_counter()-start,reads=ACCESS))
        progress(name+'_complete',seconds=time.perf_counter()-start)
    except BaseException as exc:
        write(OUT/'failures'/f'{name}-{time.time_ns()}.json',dict(reason=str(exc),traceback=traceback.format_exc(),reads=ACCESS,automatic_retry=False))
        write(OUT/'completion.json',dict(status='stop_stage_gate',passed=False,formal_complete=False,H_scored=False,stage=name,reason=str(exc)))
        progress(name+'_failed',reason=str(exc));raise
    finally:
        if training:
            ledger(training_wall_seconds=time.perf_counter()-start)
            _TRAIN_START=None
        lock.unlink(missing_ok=True)
def budget():
    used=read(OUT/'ledger.json')['training_wall_seconds']
    if _TRAIN_START is not None:used+=time.perf_counter()-_TRAIN_START
    require(used<43200,'Global training budget; incomplete roles cannot fallback')
def taskpath(r):return PARENT/'packages'/r['id']
def tag(arm,lam,seed):return f'{arm}-lambda{lam:g}-seed{seed}'
def cfg_arm(arm,lam):return 'A1' if lam==0 else arm
def parent_key(r):return (r['outer'],r['target'],r['group'])
def base_logits(m,x):return x@m['weight'].T+m['bias']
def loss_audit(m,s,t):
    w=m['weight'].detach().clone().requires_grad_();b=m['bias'].detach().clone().requires_grad_()
    z=s['x']@w.T+b
    j=(s['mass']*(torch.logsumexp(z,1)-z.gather(1,s['y'][:,None]).squeeze(1))).sum()+.0005*(1+t)*w.square().sum()
    grad=torch.autograd.grad(j,(w,b));mx=max(float(g.abs().max()) for g in grad)
    require(mx<=1e-5 and torch.isfinite(j),'Base original-coordinate gate')
    return dict(J=float(j.detach()),gradient_max=mx)
