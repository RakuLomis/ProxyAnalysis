"""NR1 pilot-only capabilities. No query, label or full-matrix entry point."""
from pathlib import Path
import ast
import contextlib
import hashlib
import inspect
import json
import os
import sys
import time
import traceback
import types
os.environ.setdefault('CUBLAS_WORKSPACE_CONFIG', ':4096:8')
import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F

ROOT=Path(__file__).resolve().parents[2]
OLD=ROOT/'outputs/role-asymmetric-transfer-v1-20261017/run-01'
OUT=ROOT/'outputs/role-asymmetric-transfer-v1-20261017/numeric-pilot-nr1'
DOC=ROOT/'docs/role-asymmetric-transfer-v1-20261017'
PLAN=ROOT/'plan/RA1-same-objective-numeric-revision-pilot-plan-20261018.md'
CASES=ROOT/'plan/RA1-NR1-fixed-pilot-cases-20261018.json'
OLD_CODE=ROOT/'eval/role_asymmetric_transfer_v1'
FAIL_ROLE='main/f0/vless/G0/outer'
FAIL_POLICY='RawPre__m050__UPR'
READS=[]
START=None
_C=None
_CHECKED={}
_PARENT_ACTIVE=None

class ActivityBudget(RuntimeError):pass

def require(ok,message):
    if not bool(ok):raise RuntimeError(message)
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def scalar(v):
    if isinstance(v,np.generic):return v.item()
    if isinstance(v,Path):return str(v)
    raise TypeError(type(v).__name__)
def writable(p):
    p=Path(p).resolve();require(p.is_relative_to(OUT) or p.is_relative_to(DOC),'NR1 write outside new roots')
    p.parent.mkdir(parents=True,exist_ok=True);return p
def write(p,value):
    p=writable(p);tmp=p.with_name(p.name+'.tmp');tmp.write_text(json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False,default=scalar)+'\n',encoding='utf-8');os.replace(tmp,p)
def save(d,p):
    p=writable(p);tmp=p.with_name(p.name+'.tmp');d.to_parquet(tmp,index=False);os.replace(tmp,p)
def textfile(p,s):writable(p).write_text(s,encoding='utf-8')
def put(p,value,**meta):
    p=writable(p);require(not p.exists() and not p.with_suffix('.json').exists(),'NR1 artifact overwrite')
    tmp=p.with_name(p.name+'.tmp');torch.save(value,tmp);os.replace(tmp,p);write(p.with_suffix('.json'),dict(sha256=sha(p),**meta))
def sha(p):
    p=Path(p);require(p.suffix.lower() not in ['.pcap','.pcapng','.cap'],'Raw capture forbidden')
    h=hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()
def rel(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def checked(p,h,purpose):
    p=Path(p);sig=(p.stat().st_size,p.stat().st_mtime_ns)
    if _CHECKED.get(str(p))!=(sig,h):require(sha(p)==h,'Changed sealed input '+str(p));_CHECKED[str(p)]=(sig,h)
    READS.append(dict(path=rel(p),sha256=h,purpose=purpose,time_unix=time.time()))
def contract():
    global _C
    if _C is None:
        p=OUT/'manifests/contract.json';require(sha(p)==read(p.with_name('seal.json'))['sha256'],'NR1 contract seal');_C=read(p)
    return _C
def old_artifact(p):
    p=Path(p);require(rel(p) in contract()['allowed_inputs'],'Non-whitelisted old input')
    checked(p,contract()['allowed_inputs'][rel(p)],'train-or-numeric-artifact')
    return torch.load(p,map_location=device(),weights_only=True)
def local_artifact(p):
    p=Path(p);require(p.resolve().is_relative_to(OUT),'Not an NR1 artifact')
    checked(p,read(p.with_suffix('.json'))['sha256'],'pilot-artifact');return torch.load(p,map_location=device(),weights_only=True)
def device():require(torch.cuda.is_available(),'CUDA required');return torch.device('cuda:0')
def configure():
    device();torch.set_num_threads(1);torch.use_deterministic_algorithms(True)
    torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False;torch.cuda.reset_peak_memory_stats()
def tensor(v,dtype=torch.float64):return torch.as_tensor(np.asarray(v),device=device(),dtype=dtype)
def weighted(y,m,n):return F.one_hot(y,n).double().T@m
def elapsed():return time.perf_counter()-START if START is not None else 0.
def budget_check(compute=True):
    global _PARENT_ACTIVE
    if _PARENT_ACTIVE is None:_PARENT_ACTIVE=read(OLD/'cost-ledger.json')['active_seconds']
    limit=1740 if compute else 1800
    if elapsed()>=limit or _PARENT_ACTIVE+elapsed()>=28800:
        raise ActivityBudget('NR1 active budget boundary; reserve final 60 seconds for closeout')
def progress(stage,**kw):
    write(OUT/'progress.json',dict(stage=stage,pid=os.getpid(),time_unix=time.time(),active_seconds=elapsed(),**kw));print(stage,kw,flush=True)
@contextlib.contextmanager
def phase(name):
    budget_check();started=time.time();left=len(READS);progress(name+'_running')
    try:
        yield
        write(OUT/'stages'/(name+'.json'),dict(passed=True,started_unix=started,ended_unix=time.time(),reads=READS[left:]))
    except BaseException:
        write(OUT/'stages'/(name+'-stopped.json'),dict(passed=False,started_unix=started,ended_unix=time.time(),reads=READS[left:],traceback=traceback.format_exc()));raise
def signature(s):
    h=hashlib.sha256();details={}
    for k in ['x','y','mass','mu','scale']:
        t=s[k].detach().cpu().contiguous();head=json.dumps(dict(key=k,dtype=str(t.dtype),shape=list(t.shape)),sort_keys=True).encode()
        raw=t.numpy().tobytes();h.update(head);h.update(raw);details[k]=dict(dtype=str(t.dtype),shape=list(t.shape),sha256=hashlib.sha256(raw).hexdigest())
    return dict(sha256=h.hexdigest(),fields=details)
def independent(s,theta,t):
    z=s['x']@theta[:,:96].T+theta[:,96];p=z.softmax(1);coef=.0005*(1+t)
    val=(s['mass']*(z.logsumexp(1)-z.gather(1,s['y'][:,None]).squeeze(1))).sum()+coef*theta[:,:96].square().sum()
    e=(p-F.one_hot(s['y'],6))*s['mass'][:,None]
    grad=torch.cat([e.T@s['x']+2*coef*theta[:,:96],e.sum(0)[:,None]],1)
    return float(val),grad
