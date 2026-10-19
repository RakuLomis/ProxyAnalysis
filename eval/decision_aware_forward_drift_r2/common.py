"""Isolated, capability-checked DA-FGAN1 source-only pilot runtime."""
from pathlib import Path
import os, sys, json, time, hashlib, contextlib, traceback, threading
os.environ.setdefault('CUBLAS_WORKSPACE_CONFIG', ':4096:8')
import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F

ROOT=Path(__file__).resolve().parents[2]; CODE=Path(__file__).resolve().parent
OUT=ROOT/'outputs/decision-aware-forward-drift-20261017/pilot-02'
DOC=ROOT/'docs/decision-aware-forward-drift-20261017'
PLAN=ROOT/'plan/DA-FGAN1-forward-decision-space-pilot-plan-20261017.md'
ST=ROOT/'outputs/shape-source-task-attribution-20261016/run-01'
ASSOC=ROOT/'outputs/post-input-associated-representation-20261014/run-01'
PREP=ROOT/'outputs/calibrated-deployment-business-transfer-20261006/run-01'
RAW=ROOT/'outputs/deproxy-moment-game-v1-20261016/run-01'
NATIVE=ROOT/'outputs/protocol-probability-drift-20261004/run-01/features/paired-flow-features.parquet'
LABELS=['bing.com::search_results_view','developer.mozilla.org::document_view','github.com::repository_view','wikipedia.org::article_view','youtube.com::search_results_view','youtube.com::video_playback']
FEATURES=['W_up','W_down','U_up','U_down','P_up','P_down','E_up','E_down','FR_packet_runs','R_unique_zero_runs']
SIZES=[9]*4+[10]*6; HIST=[f'h{j:02}_{b:02}' for j,n in enumerate(SIZES) for b in range(n)]
MASKS={'G0':[2,4],'G1':[0,3],'G2':[1,5]}
ARMS=['DA-P','DA-G','Full-P']; PIPES=['B0','B0-R']+ARMS
CAP='none'; READS=[]; _C=None; _LOCK=threading.Lock(); _CHECKED={}

def require(x,msg):
    if not bool(x): raise RuntimeError(msg)
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def rel(p): return Path(p).resolve().relative_to(ROOT).as_posix()
def sha(p):
    p=Path(p); require(p.suffix.lower() not in {'.pcap','.pcapng','.cap'},'Capture forbidden')
    return hashlib.sha256(p.read_bytes()).hexdigest()
def writable(p):
    p=Path(p).resolve(); require(p.is_relative_to(OUT) or p.is_relative_to(DOC),'New roots only')
    p.parent.mkdir(parents=True,exist_ok=True); return p
def write(p,v):
    p=writable(p); t=p.with_name(p.name+'.tmp')
    t.write_text(json.dumps(v,ensure_ascii=False,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf-8'); os.replace(t,p)
def immutable(p,v): require(not Path(p).exists(),'Immutable record '+str(p)); write(p,v)
def put(p,v,**m):
    p=writable(p); require(not p.exists(),'Immutable tensor'); t=p.with_name(p.name+'.tmp'); torch.save(v,t); os.replace(t,p)
    immutable(p.with_suffix('.json'),dict(sha256=sha(p),**m))
def save(p,d):
    p=writable(p); require(not p.exists(),'Immutable table'); pd.DataFrame(d).to_parquet(p,index=False)
def seal(p,files,**m):
    fs=list(dict.fromkeys(Path(x) for x in files)); fs += [x.with_suffix('.json') for x in fs if x.suffix=='.pt']
    immutable(p,dict(files={rel(x):sha(x) for x in dict.fromkeys(fs)},**m))
def verifyseal(p):
    p=Path(p); sig=(p.stat().st_size,p.stat().st_mtime_ns)
    if _CHECKED.get(str(p))!=sig:
        for x,h in read(p)['files'].items(): require(sha(ROOT/x)==h,'Seal mismatch '+x)
        _CHECKED[str(p)]=sig
    return read(p)
def barrier(name):
    p=OUT/'manifests'/name; require(p.exists(),'Missing barrier '+name); return verifyseal(p)
def contract():
    global _C
    if _C is None:
        p=OUT/'manifests/experiment-contract.json'; require(sha(p)==read(p.with_suffix('.seal.json'))['sha256'],'Contract mismatch'); _C=read(p)
    return _C
def roles(): return contract()['roles']
def lookup(rid): return next(r for r in roles() if r['id']==rid)
def configure(cap):
    global CAP
    CAP=cap; require(torch.cuda.is_available(),'CUDA mandatory'); torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True); torch.backends.cuda.matmul.allow_tf32=False; torch.backends.cudnn.allow_tf32=False
def tensor(x,dtype=torch.float64): return torch.as_tensor(np.asarray(x),device='cuda',dtype=dtype)
def cpu(x): return x.detach().cpu().numpy()
def note(p,kind,rid):
    with _LOCK: READS.append(dict(path=rel(p),kind=kind,role_id=rid,capability=CAP,sha256=sha(p)))
def flush(tag):
    with _LOCK:
        if READS: immutable(OUT/'permissions'/f'{tag}-{os.getpid()}-{time.time_ns()}.json',dict(reads=list(READS))); READS.clear()
def external(p,rid,kind):
    p=Path(p); i=contract()['files'].get(rel(p)); require(i is not None and i['kind']==kind and i['role_id'] in [rid,None],'External binding')
    if kind in ['query','labels']:
        require(CAP in ['inference','score'],'Deferred read capability')
        barrier('models-complete.json' if kind=='query' else 'predictions-complete.json')
        if kind=='labels': require(CAP=='score','Label capability')
    else: require(CAP in ['trusted','tests'],'Historical producer only')
    require(sha(p)==i['sha256'],'Historical hash mismatch'); note(p,kind,rid)
    return torch.load(p,map_location='cuda',weights_only=True) if p.suffix=='.pt' else pd.read_parquet(p)
def own(p,rid=None):
    p=Path(p); require(p.resolve().is_relative_to(OUT),'Own root'); m=read(p.with_suffix('.json'))
    require(rid is None or m.get('role_id')==rid,'Own role mismatch')
    allowed={'trusted':{'shared','P','G','classification','model','base','diag'},'tests':{'shared','P','G','classification','model','base'},
             'P':{'shared','P'},'G':{'shared','G'},'fit':{'classification','model','base','shared'},
             'inference':{'model','base'},'diagnostic':{'model','base','shared','diag'},'score':{'model','base','diag','shared'}}
    require(m['capability'] in allowed.get(CAP,set()),'Capability denied '+m['capability']+' for '+CAP)
    if m['capability']=='diag': barrier('predictions-complete.json')
    require(sha(p)==m['sha256'],'Own tensor changed'); note(p,m['capability'],rid)
    return torch.load(p,map_location='cuda',weights_only=True)
def modelroot(r,arm): return OUT/'generators'/r['id']/arm
def progress(stage,**kw): write(OUT/'progress.json',dict(stage=stage,unix=time.time(),**kw)); print(stage,kw,flush=True)
def deadline():
    b=read(OUT/'budget.json'); require(time.time()-b['start_unix']<10800,'3h cumulative activity cap exhausted')
def codecheck():
    for p,h in contract()['code'].items(): require(sha(ROOT/p)==h,'Frozen code changed '+p)
def failure(stage,e):
    p=OUT/'failures'/f'{stage}-{time.time_ns()}.json'; immutable(p,dict(reason=str(e),traceback=traceback.format_exc(),stage=stage))
    progress('stopped',reason=str(e),failed_stage=stage)
def yvalues(d):
    y=d.label_id.map(dict(zip(LABELS,range(6)))); require(y.notna().all(),'Unknown label'); return y.to_numpy(int)
def block(j): return slice(sum(SIZES[:j]),sum(SIZES[:j+1]))
def persist(path,result,**meta):
    immutable(Path(path).with_suffix('.quality.json'),result['quality'])
    put(path,result['head'],capability='model',**meta)
    put(Path(path).with_name(Path(path).stem+'-solver.pt'),result['numeric_state'],capability='model',**meta)
