"""RA1 isolated IO, train/query/score capabilities and unchanged v4 policy."""
from pathlib import Path
import ast
import contextlib
import hashlib
import importlib.util
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
from numeric_policy import POLICY, SOLVER, acceptance_gates

ROOT = Path(__file__).resolve().parents[2]
OLD = ROOT/'outputs/role-asymmetric-transfer-v1-20261017/run-01'
NR = ROOT/'outputs/role-asymmetric-transfer-v1-20261017/numeric-pilot-nr1'
OLD_CODE = ROOT/'eval/role_asymmetric_transfer_v1'
OUT = ROOT/'outputs/role-asymmetric-transfer-v1-20261017/full-nr2-01'
DOC = ROOT/'docs/role-asymmetric-transfer-v1-20261017/full-nr2'
PLAN = ROOT/'plan/RA1-NR2-full-resume-contract-20261018.md'
TI = ROOT/'outputs/strongpost-training-intervention-20261009/run-01'
SA = ROOT/'outputs/small-view-attribution-20261010/run-02'
JA = ROOT/'outputs/joint-affine-transfer-20261007/run-01'
PREP = ROOT/'outputs/calibrated-deployment-business-transfer-20261006/run-01'
V4 = ROOT/'outputs/calibrated-deployment-business-transfer-20261006/run-04'
PROTOCOLS = ['shadowsocks','vless','trojan','vmess']
LABELS = ['bing.com::search_results_view','developer.mozilla.org::document_view',
          'github.com::repository_view','wikipedia.org::article_view',
          'youtube.com::search_results_view','youtube.com::video_playback']
MASKS = {'G0':[2,4],'G1':[0,3],'G2':[1,5]}
HIST = [f'h{j:02d}_{b:02d}' for j in range(10) for b in range(9 if j<4 else 10)]
READS=[]
_CONTRACT=None
_CACHE={}
_ACTIVE=None
START=None
PRIOR=None

FULL1 = ROOT/'outputs/role-asymmetric-transfer-v1-20261017/full-nr1-01'
NR2 = ROOT/'outputs/role-asymmetric-transfer-v1-20261017/numeric-pilot-nr2-02'
NR2_CODE = ROOT/'eval/role_asymmetric_transfer_nr2_pilot'
LEGACY = OLD_CODE
BASE = ROOT/'outputs/role-asymmetric-transfer-v1-20261017'
class ActivityBudget(RuntimeError):pass

def require(ok, message):
    if not bool(ok): raise RuntimeError(message)

def read(path): return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def scalar(v):
    if isinstance(v,np.generic): return v.item()
    if isinstance(v,Path): return str(v)
    raise TypeError(type(v).__name__)
def writable(path):
    p=Path(path).resolve()
    require(p.is_relative_to(OUT) or p.is_relative_to(DOC),'Write outside RA1 roots')
    p.parent.mkdir(parents=True,exist_ok=True);return p
def write(path,value):
    p=writable(path);tmp=p.with_name(p.name+'.tmp')
    tmp.write_text(json.dumps(value,ensure_ascii=False,indent=2,sort_keys=True,allow_nan=False,default=scalar)+'\n',encoding='utf-8');os.replace(tmp,p)
def textfile(path,value): writable(path).write_text(value,encoding='utf-8')
def save(frame,path):
    p=writable(path);tmp=p.with_name(p.name+'.tmp');frame.to_parquet(tmp,index=False);os.replace(tmp,p)
def sha(path):
    p=Path(path);require(p.suffix.lower() not in {'.pcap','.pcapng','.cap'},'Raw capture forbidden')
    h=hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()
def rel(path): return Path(path).resolve().relative_to(ROOT).as_posix()
def checked(path,expected,purpose):
    p=Path(path);sig=(p.stat().st_size,p.stat().st_mtime_ns)
    if _CACHE.get(str(p))!=(sig,expected):
        require(sha(p)==expected,'Sealed input changed: '+str(p));_CACHE[str(p)]=(sig,expected)
    READS.append(dict(path=rel(p),purpose=purpose,sha256=expected,time_unix=time.time()))
def put(path,value,**meta):
    p=writable(path);require(not p.exists() and not p.with_suffix('.json').exists(),'Do not overwrite artifact')
    tmp=p.with_name(p.name+'.tmp');torch.save(value,tmp);os.replace(tmp,p)
    write(p.with_suffix('.json'),dict(sha256=sha(p),**meta))
def device():
    require(torch.cuda.is_available(),'CUDA required; no CPU numerical fallback');return torch.device('cuda:0')
def configure():
    device();torch.set_num_threads(1);torch.use_deterministic_algorithms(True)
    torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
    torch.cuda.reset_peak_memory_stats()
def tensor(v,dtype=torch.float64): return torch.as_tensor(np.asarray(v),device=device(),dtype=dtype)
def weighted(y,m,n): return F.one_hot(y,n).double().T@m
def truths(d):
    y=d.label_id.map(dict(zip(LABELS,range(6))));require(y.notna().all(),'Unknown label');return y.to_numpy(int)
def contract():
    global _CONTRACT
    if _CONTRACT is None:
        p=OUT/'manifests/contract.json';require(sha(p)==read(p.with_name('seal.json'))['sha256'],'RA1 contract changed');_CONTRACT=read(p)
    return _CONTRACT
def artifact(path,purpose='train-artifact'):
    p=Path(path)
    if not p.resolve().is_relative_to(OUT):
        c=contract();require(rel(p) in c['artifacts'],'Unregistered artifact')
        checked(p,c['artifacts'][rel(p)],purpose)
        checked(p.with_suffix('.json'),c['fixed'][rel(p.with_suffix('.json'))],'metadata')
    info=read(p.with_suffix('.json'));checked(p,info['sha256'],purpose)
    return torch.load(p,map_location=device(),weights_only=True)
def package(path,purpose):
    p=Path(path);c=contract();require(rel(p) in c['packages'],'Unregistered package');i=c['packages'][rel(p)]
    allowed={'train':{'source-pre','source-post','C-post'},'query':{'main-query'},'score':{'main-outer-labels'}}
    require(i['kind'] in allowed.get(purpose,set()),'Illegal package capability')
    if purpose=='query':
        require((OUT/'manifests/endpoint-seal.json').exists(),'Seal all models before H query')
        checked(OUT/'manifests/endpoints.parquet',read(OUT/'manifests/endpoint-seal.json')['sha256'],'endpoint-seal')
    if purpose=='score':
        require((OUT/'predictions/complete.json').exists(),'Seal all predictions before labels')
        checked(OUT/'predictions/visits.parquet',read(OUT/'predictions/complete.json')['sha256'],'prediction-seal')
    checked(p,i['sha256'],purpose);d=pd.read_parquet(p)
    require(list(d)==i['columns'],'Schema changed')
    s=i['scope']
    if i['kind'].startswith('source-'):
        require(set(d.content_id)<=set(s['train_contents']) and set(d.protocol)<=set(s['sources']),'Source scope')
        if i['kind']=='source-pre':require('visit_id' not in d and 'session_id' not in d,'Anonymous pre identity')
    if i['kind']=='C-post':require(set(d.content_id)<=set(s['C_contents']) and set(d.protocol)=={s['calibration']},'C scope')
    if purpose=='query':require(set(d)=={'visit_id',*HIST} and d.visit_id.is_unique and len(d)==24,'Query schema')
    if purpose=='score':require(set(d.content_id)==set(s['validation_contents']) and len(d)==24,'H label scope')
    return d
def progress(name,**details):
    write(OUT/'progress.json',dict(stage=name,time_unix=time.time(),pid=os.getpid(),cumulative_active_seconds=spent(),**details));print(name,details,flush=True)
def spent():
    return (PRIOR or 0.)+(time.perf_counter()-START if START is not None else 0.)
def budget_check():
    if spent()>=28680:raise ActivityBudget('Cumulative 8h safety limit: reserve 120 seconds for closeout; no fallback')
@contextlib.contextmanager
def stage(name):
    global _ACTIVE
    require(_ACTIVE is None,'Nested active stages');p=OUT/'stages'/f'{name}.json';require(not p.exists(),'Completed stage')
    READS.clear();_ACTIVE=time.perf_counter();start=time.time();ok=False
    try:
        budget_check()
        if (OUT/'manifests/seal.json').exists():
            for f,h in contract()['code'].items():require(sha(ROOT/f)==h,'Sealed code changed')
            require(sha(PLAN)==contract()['plan_sha256'],'Plan changed')
        progress(name+'_running');yield;ok=True
        write(p,dict(passed=True,started_unix=start,ended_unix=time.time(),seconds=time.perf_counter()-_ACTIVE,reads=READS.copy()))
    finally:
        duration=time.perf_counter()-_ACTIVE;_ACTIVE=None
        cost=read(OUT/'cost-ledger.json') if (OUT/'cost-ledger.json').exists() else dict(active_seconds=0.,activity_limit_seconds=28800,prior_cumulative_seconds=PRIOR,intervals=[])
        cost['active_seconds']+=duration;cost['intervals'].append(dict(stage=name,start=start,end=time.time(),seconds=duration,passed=ok));write(OUT/'cost-ledger.json',cost)
        cost['cumulative_active_seconds']=spent();write(OUT/'cost-ledger.json',cost)
        if not ok:write(OUT/'audits'/f'{name}-reads-on-stop.json',dict(reads=READS.copy(),traceback=traceback.format_exc()))
def trainpath(r): return OLD/'packages'/r['id']/'training.pt'
def rolepath(r): return PREP/'packages'/r['id']
def modelpath(r,p): return OUT/'models'/r['id']/(p['id']+'.pt')

# Narrow runtime aliases for sealed NR2 numerical modules.
def dev(): return device()
def guard(): return budget_check()
def pathout(path): return writable(path)
def cuda(*args):
    for a in args:
        require(a.is_cuda, 'CPU numerical input prohibited')
        if a.is_floating_point(): require(a.dtype==torch.float64, 'float64 required')
def finite(*args):
    for a in args: require(torch.isfinite(a).all(), 'Nonfinite numerical input')

