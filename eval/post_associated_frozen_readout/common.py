"""Frozen readout v2: sealed source-only IO and immutable historical assets."""
from pathlib import Path
import contextlib
import hashlib
import json
import os
import sys
import time
import traceback
os.environ.setdefault('CUBLAS_WORKSPACE_CONFIG', ':4096:8')
sys.dont_write_bytecode = True
import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'outputs/post-associated-frozen-readout-20261014/run-01'
DOC=ROOT/'docs/post-associated-frozen-readout-20261014'
SOURCE=ROOT/'outputs/post-input-associated-representation-20261014/run-02'
PARENT=SOURCE.parent/'run-01'
PLAN=ROOT/'plan/post-input-representation-output-scale-plan-v2-20261014.md'
CODE=Path(__file__).resolve().parent
SEEDS=[20261014,20261015,20261016]
ARMS=['X','R','G','P'];ETAS=[1.,.01]
LABELS=['bing.com::search_results_view','developer.mozilla.org::document_view','github.com::repository_view',
        'wikipedia.org::article_view','youtube.com::search_results_view','youtube.com::video_playback']
HIST=[f'h{j:02}_{i:02}' for j in range(10) for i in range(9 if j<4 else 10)]
ACCESS=[];_CONTRACT=None;_FIT_START=None

def require(ok,message):
    if not bool(ok):raise RuntimeError(message)
def rel(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def sha(p):
    require(Path(p).suffix.lower() not in ['.pcap','.pcapng','.cap'],'No raw capture access')
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def write(p,v):
    p=Path(p).resolve();require(p.is_relative_to(OUT) or p.is_relative_to(DOC),'Write outside new run/doc')
    p.parent.mkdir(parents=True,exist_ok=True)
    require(not p.exists(),'Refuse overwrite '+rel(p))
    p.write_text(json.dumps(v,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False,
        default=lambda x:x.item() if isinstance(x,np.generic) else str(x))+'\n',encoding='utf-8')
def mutable(p,v):
    p=Path(p).resolve();require(p.is_relative_to(OUT) and p.name in ['ledger.json','progress.json'],'Only mutable engineering counters')
    p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_suffix('.tmp')
    tmp.write_text(json.dumps(v,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf-8');os.replace(tmp,p)
def ledger(**delta):
    p=OUT/'ledger.json';v=read(p)
    for k,x in delta.items():v[k]=v.get(k,0)+x
    mutable(p,v)
def progress(s,**k):
    mutable(OUT/'progress.json',dict(stage=s,time_unix=time.time(),**k));print(s,k,flush=True)
def seal(p,files,**k):write(p,dict(files={rel(x):sha(x) for x in sorted(set(files))},**k))
def verifyseal(p):
    v=read(p);require(v.get('passed',False),'Failed seal')
    for name,h in v['files'].items():require(sha(ROOT/name)==h,'Sealed asset changed '+name)
def contract():
    global _CONTRACT
    p=OUT/'manifests/experiment-contract.json'
    if _CONTRACT is None:
        require(sha(p)==read(OUT/'manifests/contract-seal.json')['sha256'],'Contract changed');_CONTRACT=read(p)
    return _CONTRACT
def configure():
    require(torch.cuda.is_available(),'CUDA required, CPU fallback forbidden')
    torch.set_num_threads(1);torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
    torch.use_deterministic_algorithms(True);torch.cuda.reset_peak_memory_stats()
def device():return torch.device('cuda:0')
def check_source(p,purpose,rid=None,arm=None):
    info=contract()['sources'].get(rel(p));require(info is not None,'Unregistered source')
    if rid is not None:require(info.get('role_id')==rid,'Wrong source role')
    allowed={'train':{'classification','base','g-random','g-group','g-paired'},
        'conversion':{'g-group','g-paired'},'predict':{'query-post'},'score':{'query-label'},
        'integrity':{'historical','metadata','base'}}
    require(info['kind'] in allowed[purpose],'Forbidden source purpose')
    if info['kind'].startswith('g-') and purpose=='train':
        require(arm in {'R','G','P'} and info['kind']=={'R':'g-random','G':'g-group','P':'g-paired'}[arm],'Cross-arm G read')
    if purpose=='predict':require((OUT/'manifests/models-complete.json').exists(),'All models must seal before query')
    if purpose=='score':require((OUT/'predictions/complete.json').exists(),'All predictions must seal before labels')
    require(sha(p)==info['sha256'],'Source changed')
    ACCESS.append(dict(path=rel(p),sha256=info['sha256'],purpose=purpose,role_id=rid,arm=arm))
    return info
def source_tensor(p,rid,arm=None,purpose='train'):
    check_source(p,purpose,rid,arm);return torch.load(p,map_location=device(),weights_only=True)
def package(r,kind):
    key=r['query'] if kind=='predict' else r['labels'];p=ROOT/key
    info=check_source(p,kind,r['id']);d=pd.read_parquet(p)
    require(list(d)==info['columns'] and len(d)==info['rows'],'Source schema/count')
    if kind=='predict':require(set(d)=={'visit_id',*HIST} and d.visit_id.is_unique,'Post-only query')
    return d
def put(p,v,**meta):
    p=Path(p).resolve();require(p.is_relative_to(OUT) and not p.exists(),'Immutable new tensor output')
    p.parent.mkdir(parents=True,exist_ok=True);torch.save(v,p)
    write(p.with_suffix('.json'),dict(sha256=sha(p),**meta))
def own(p):
    require(sha(p)==read(p.with_suffix('.json'))['sha256'],'Own tensor changed')
    return torch.load(p,map_location=device(),weights_only=True)
def save(p,d):
    p=Path(p).resolve();require(p.is_relative_to(OUT) and not p.exists(),'Immutable new table')
    p.parent.mkdir(parents=True,exist_ok=True);d.to_parquet(p,index=False)
def budget():
    used=read(OUT/'ledger.json')['fit_seconds']
    if _FIT_START is not None:used+=time.perf_counter()-_FIT_START
    require(used<3600,'Cumulative source readout fit budget exhausted; unresolved is not fallback')
@contextlib.contextmanager
def stage(name):
    configure();ACCESS.clear();c=contract();require(sha(PLAN)==c['plan_sha256'],'Plan changed')
    verifyseal(OUT/'manifests/code.json');p=OUT/'stages'/f'{name}.json';require(not p.exists(),'Completed stage cannot repeat')
    start=time.perf_counter();progress(name+'_running',pid=os.getpid())
    try:
        yield
        write(p,dict(passed=True,seconds=time.perf_counter()-start,reads=ACCESS,
            peak_cuda_MiB=torch.cuda.max_memory_allocated()/1048576));progress(name+'_complete')
    except BaseException as e:
        write(OUT/'failures'/f'{name}.json',dict(reason=str(e),traceback=traceback.format_exc(),reads=ACCESS))
        write(OUT/'completion.json',dict(passed=False,status='stop_stage_gate',stage=name,reason=str(e),
            formal_H_scored=False,automatic_retry=False));progress(name+'_failed',reason=str(e));raise
def tag(arm,eta,seed):return f'{arm}-eta{eta:g}-seed{seed if arm!="X" else 0}'
def modelpath(r,arm,eta,seed):return OUT/'models'/r['id']/tag(arm,eta,seed)/'head.pt'
def gpath(r,arm,seed):return OUT/'frozen-G'/r['id']/f'{arm}-seed{seed}.pt'
