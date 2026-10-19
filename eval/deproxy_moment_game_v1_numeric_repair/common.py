"""NER1 train-only capability reader and coordinator-owned activity ledger."""
from pathlib import Path
import os, sys, json, time, hashlib, traceback, inspect
os.environ.setdefault('CUBLAS_WORKSPACE_CONFIG', ':4096:8')
import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F

ROOT=Path(__file__).resolve().parents[2]
CODE=Path(__file__).resolve().parent
OLD=ROOT/'outputs/deproxy-moment-game-v1-20261016/run-01'
OUT=OLD.parent/'numeric-repair-01'
PLAN=ROOT/'plan/DP-GAN1-M-v1-numeric-execution-repair-pilot-plan-20261016.md'
SIZES=[9]*4+[10]*6
GAMMAS=[.0001,.001,.01]
SEEDS=[20261014,20261015,20261016]
DYNAMIC=['N-P','F-P','F-G','E-post']
RECIPES=[dict(id=f'H{i+1:02}',lr=lr,gamma=g) for i,(lr,g) in enumerate((lr,g) for lr in [.0003,.001] for g in GAMMAS)]
CAP='none'
READS=[]
_REG=None
_STAGE_START=None
_DEADLINE=None
_VERIFIED={}

def require(ok,msg):
    if not bool(ok): raise RuntimeError(msg)

def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def rel(p): return Path(p).resolve().relative_to(ROOT).as_posix()
def sha(p):
    p=Path(p); require(p.suffix.lower() not in {'.pcap','.pcapng','.cap'},'PCAP forbidden')
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''): h.update(b)
    return h.hexdigest()

def write(p,v,immutable=False):
    p=Path(p).resolve();require(p.is_relative_to(OUT),'NER1 output root only')
    require(not immutable or not p.exists(),'Refuse overwrite '+str(p));p.parent.mkdir(parents=True,exist_ok=True)
    t=p.with_name(p.name+'.tmp')
    t.write_text(json.dumps(v,ensure_ascii=False,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf-8');os.replace(t,p)

def put(p,v,**meta):
    p=Path(p).resolve();require(p.is_relative_to(OUT) and not p.exists(),'Immutable NER1 tensor root')
    p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_name(p.name+'.tmp');torch.save(v,tmp);os.replace(tmp,p)
    write(p.with_suffix('.json'),dict(sha256=sha(p),numeric_version='NER1',**meta),True)

def save(p,rows):
    p=Path(p);require(p.resolve().is_relative_to(OUT) and not p.exists(),'Immutable NER1 table root')
    p.parent.mkdir(parents=True,exist_ok=True);pd.DataFrame(rows).to_parquet(p,index=False)

def registration():
    global _REG
    if _REG is None:
        p=OUT/'registration.json';require(sha(p)==read(OUT/'registration.seal.json')['sha256'],'Registration seal')
        _REG=read(p)
    return _REG

def configure(cap):
    global CAP
    require(cap in {'P','G','E','synthetic','coordinator'},'Unknown capability')
    CAP=cap;require(torch.cuda.is_available(),'CUDA required')
    torch.set_num_threads(1);torch.use_deterministic_algorithms(True)
    torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False

def roles(): return registration()['roles']
def lookup(rid):
    require(rid in {r['id'] for r in roles()},'Role outside fixed twelve')
    return next(r for r in roles() if r['id']==rid)
def block(j): return slice(sum(SIZES[:j]),sum(SIZES[:j+1]))
def capfor(arm): return 'E' if arm=='E-post' else ('G' if arm in ['F-G','R-G'] else 'P')
def tensor(v,dtype=torch.float64): return torch.as_tensor(np.asarray(v),device='cuda',dtype=dtype)
def cpu(v): return v.detach().cpu().numpy()

def own(p,rid):
    p=Path(p).resolve();reg=registration();lookup(rid)
    key=rel(p);binding=reg['assets'].get(key)
    require(binding is not None and binding['role_id']==rid,'Unregistered or cross-role input')
    allowed={'P':{'P','pre','post','shared'},'G':{'G','pre','post','shared'},'E':{'E','post','shared'}}
    require(binding['capability'] in allowed.get(CAP,set()),'Capability denied before decode')
    # Registration binds both sidecar and payload to the frozen parent seal.
    sig=(p.stat().st_size,p.stat().st_mtime_ns)
    if _VERIFIED.get(key)!=sig:
        require(sha(p)==binding['sha256'],'Payload hash mismatch')
        require(sha(p.with_suffix('.json'))==binding['sidecar_sha256'],'Sidecar hash mismatch')
        m=read(p.with_suffix('.json'))
        require(m['role_id']==rid and m['sha256']==binding['sha256'] and m['capability']==binding['capability'],'Bound metadata mismatch')
        _VERIFIED[key]=sig
    READS.append(dict(path=key,role_id=rid,capability=CAP,sha256=binding['sha256']))
    return torch.load(p,map_location='cuda',weights_only=True)

def newown(p,rid):
    p=Path(p).resolve();require(p.is_relative_to(OUT),'New asset root')
    m=read(p.with_suffix('.json'));require(m['role_id']==rid and m['numeric_version']=='NER1','New asset version/role')
    require(m['capability'] in {'P':{'P','pre','post'},'G':{'G','pre','post'},'E':{'E','post'}}.get(CAP,set()),'New asset capability')
    require(sha(p)==m['sha256'],'New tensor hash')
    return torch.load(p,map_location='cuda',weights_only=True)

def begin(stage):
    global _STAGE_START,_DEADLINE
    require(_STAGE_START is None,'Nested activity writer')
    b=read(OUT/'budget.json');require(sha(OLD/'budget.json')==registration()['parent_budget_sha256'],'Parent ledger changed')
    allowance=min(14400-b['repair_seconds'],86400-b['parent_seconds']-b['repair_seconds'])
    require(allowance>0,'Activity budget exhausted')
    _STAGE_START=time.perf_counter();_DEADLINE=_STAGE_START+allowance
    progress(stage,capability=CAP)

def deadline():
    require(_DEADLINE is not None and time.perf_counter()<_DEADLINE,'Activity budget exhausted')

def end(stage):
    global _STAGE_START
    torch.cuda.synchronize();s=time.perf_counter()-_STAGE_START
    b=read(OUT/'budget.json');b['repair_seconds']+=s;b['used_seconds']=b['parent_seconds']+b['repair_seconds']
    b['items'].append(dict(stage=stage,capability=CAP,seconds=s));write(OUT/'budget.json',b)
    write(OUT/'permissions'/f'{stage}-{CAP}-{time.time_ns()}.json',dict(reads=READS,query_reads=0,H_U_reads=0))
    _STAGE_START=None

def progress(stage,**kw):
    write(OUT/'progress.json',dict(stage=stage,unix=time.time(),**kw));print(stage,kw,flush=True)

def failure(stage,e):
    write(OUT/'failures'/f'{stage}-{time.time_ns()}.json',dict(error=repr(e),traceback=traceback.format_exc()),True)
    progress('stopped',stage_failed=stage,error=str(e))

def codecheck():
    for p,h in read(OUT/'code-seal.json')['files'].items():require(sha(ROOT/p)==h,'Code changed while executing '+p)
