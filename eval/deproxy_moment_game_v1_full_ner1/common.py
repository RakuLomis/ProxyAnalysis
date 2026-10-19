"""Full NER1 runtime: 40h cumulative, train capabilities, sealed phase readers."""
from pathlib import Path
import os,sys,json,time,hashlib,contextlib,traceback,inspect,shutil,threading
os.environ.setdefault('CUBLAS_WORKSPACE_CONFIG',':4096:8')
import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F

ROOT=Path(__file__).resolve().parents[2];CODE=Path(__file__).resolve().parent
OLD=ROOT/'outputs/deproxy-moment-game-v1-20261016/run-01'
PILOT=OLD.parent/'numeric-repair-01';OUT=OLD.parent/'full-ner1-01'
DOC=ROOT/'docs/deproxy-moment-game-v1-20261016'
PLAN=ROOT/'plan/DP-GAN1-M-v1-local-implementation-plan-20261016.md'
ASSOC=ROOT/'outputs/post-input-associated-representation-20261014/run-01'
PREP=ROOT/'outputs/calibrated-deployment-business-transfer-20261006/run-01'
PROTOCOLS=['shadowsocks','vless','trojan','vmess']
LABELS=['bing.com::search_results_view','developer.mozilla.org::document_view','github.com::repository_view','wikipedia.org::article_view','youtube.com::search_results_view','youtube.com::video_playback']
SIZES=[9]*4+[10]*6;HIST=[f'h{j:02}_{k:02}' for j,n in enumerate(SIZES) for k in range(n)]
MASKS={'G0':[2,4],'G1':[0,3],'G2':[1,5]};SEEDS=[20261014,20261015,20261016]
GAMMAS=[.0001,.001,.01]
RECIPES=[dict(id=f'H{i+1:02}',lr=lr,gamma=g) for i,(lr,g) in enumerate((lr,g) for lr in [.0003,.001] for g in GAMMAS)]
DYNAMIC=['N-P','F-P','F-G','E-post'];METHODS=['R-P','R-G']+DYNAMIC;BETAS=[0.,.25,.5,.75,1.]
CAP='none';READS=[];_REG=None;_STAGE_START=None;_DEADLINE=None;_VERIFIED={};_SEALS={}
ACTIVITY_CAP=144000.;FORECAST_GATE=115200.
_READ_LOCK=threading.Lock()

def require(ok,msg):
    if not bool(ok):raise RuntimeError(msg)
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def rel(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def sha(p):
    p=Path(p);require(p.suffix.lower() not in {'.pcap','.pcapng','.cap'},'PCAP forbidden')
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def writable(p):
    p=Path(p).resolve();require(p.is_relative_to(OUT),'Full NER1 output root only');p.parent.mkdir(parents=True,exist_ok=True);return p
def write(p,v,immutable=False):
    p=writable(p);require(not immutable or not p.exists(),'Refuse record overwrite '+str(p));t=p.with_name(p.name+'.tmp');t.write_text(json.dumps(v,ensure_ascii=False,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf-8');os.replace(t,p)
def immutable(p,v):require(not Path(p).exists(),'Refuse record overwrite '+str(p));write(p,v)
def put(p,v,**meta):
    p=writable(p);require(not p.exists(),'Immutable tensor');t=p.with_name(p.name+'.tmp');torch.save(v,t);os.replace(t,p)
    immutable(p.with_suffix('.json'),dict(sha256=sha(p),numeric_version='NER1',**meta))
def save(p,d):
    p=writable(p);require(not p.exists(),'Immutable table');pd.DataFrame(d).to_parquet(p,index=False)
def seal(p,files,**meta):
    fs=list(dict.fromkeys(Path(f) for f in files));fs+= [f.with_suffix('.json') for f in fs if f.suffix=='.pt']
    immutable(p,dict(files={rel(f):sha(f) for f in dict.fromkeys(fs)},**meta))
def verifyseal(p):
    p=Path(p);sig=(p.stat().st_size,p.stat().st_mtime_ns)
    if str(p) not in _SEALS or _SEALS[str(p)][0]!=sig:
        v=read(p)
        for k,h in v['files'].items():require(sha(ROOT/k)==h,'Sealed asset changed '+k)
        _SEALS[str(p)]=(sig,v)
    return _SEALS[str(p)][1]
def barrier(name):
    p=OUT/'manifests'/name;require(p.exists(),'Missing phase barrier '+name);return verifyseal(p)
def registration():
    global _REG
    if _REG is None:
        p=OUT/'manifests/contract.json';require(sha(p)==read(p.with_suffix('.seal.json'))['sha256'],'Full contract seal');_REG=read(p)
    return _REG
def contract():return registration()
def roles():return contract()['inner_roles']+contract()['roles']
def lookup(rid):
    matches=[r for r in roles() if r['id']==rid];require(len(matches)==1,'Unregistered role');return matches[0]
def block(j):return slice(sum(SIZES[:j]),sum(SIZES[:j+1]))
def capfor(arm):return 'E' if arm=='E-post' else ('G' if arm in ['F-G','R-G'] else 'P')
def gamma_tag(g):return f'g{g:g}'
def configure(cap):
    global CAP
    require(cap in {'P','G','E','inference','tests','coordinator'},'Capability');CAP=cap
    require(torch.cuda.is_available(),'CUDA mandatory');torch.set_num_threads(1);torch.use_deterministic_algorithms(True)
    torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
def tensor(v,dtype=torch.float64):return torch.as_tensor(np.asarray(v),device='cuda',dtype=dtype)
def cpu(v):return v.detach().cpu().numpy()
def audit_read(p,rid,kind,h):
    with _READ_LOCK:READS.append(dict(path=rel(p),role_id=rid,kind=kind,capability=CAP,sha256=h))
def flush_reads(tag):
    with _READ_LOCK:
        if READS:
            immutable(OUT/'permissions'/f'{tag}-{os.getpid()}-{time.time_ns()}.json',dict(reads=list(READS)));READS.clear()

def own(p,rid=None):
    p=Path(p).resolve();lookup(rid)
    allowed={'P':{'P','pre','post','shared'},'G':{'G','pre','post','shared'},'E':{'E','post','shared'},
        'inference':{'export','base','post'},'tests':{'P','G','E','pre','post','shared','export','base'}}
    if p.is_relative_to(OLD):
        binding=contract()['assets'].get(rel(p));require(binding is not None and binding['role_id']==rid,'Unregistered historical tensor')
        require(binding['capability'] in allowed.get(CAP,set()),'Historical capability denied before decode')
        mpath=p.with_suffix('.json');sig=(p.stat().st_size,p.stat().st_mtime_ns,mpath.stat().st_mtime_ns)
        if _VERIFIED.get(rel(p))!=sig:
            require(sha(p)==binding['sha256'] and sha(mpath)==binding['sidecar_sha256'],'Historical payload/sidecar changed')
            m=read(mpath);require(m['role_id']==rid and m['sha256']==binding['sha256'] and m['capability']==binding['capability'],'Historical role/capability')
            _VERIFIED[rel(p)]=sig
        kind=binding['capability'];h=binding['sha256']
    else:
        require(p.is_relative_to(OUT),'Full runtime rejects unbound external or pilot tensor')
        m=read(p.with_suffix('.json'));kind=m['capability'];h=m['sha256']
        require(m.get('numeric_version')=='NER1' and m['role_id']==rid and kind in allowed.get(CAP,set()),'Generated tensor version/role/capability')
        if 'accepted' in m:
            q=read(p.with_suffix('.quality.json'))
            require(m['accepted'] and q['accepted'] and q['iterations']<2000 and q['evaluations']<10000,'Rejected head cannot be reused')
        require(sha(p)==h,'Generated tensor hash')
    audit_read(p,rid,kind,h);return torch.load(p,map_location='cuda',weights_only=True)
def newown(p,rid):return own(p,rid)
def external(p,rid,kind):
    p=Path(p);info=contract()['files'].get(rel(p))
    require(CAP=='inference' and kind=='base' and info is not None and info['kind']==kind and info['role_id']==rid,'Closed B0 reader')
    require(sha(p)==info['sha256'],'B0 changed');audit_read(p,rid,kind,info['sha256'])
    return torch.load(p,map_location='cuda',weights_only=True)

def remaining():
    b=read(OUT/'budget.json');require(b['used_seconds']<ACTIVITY_CAP,'Cumulative 40h activity guard; pending is not fallback');return ACTIVITY_CAP-b['used_seconds']
def begin(stage):
    global _STAGE_START,_DEADLINE
    require(_STAGE_START is None,'Nested activity writer');b=read(OUT/'budget.json')
    require(sha(PILOT/'budget.json')==contract()['pilot_budget_sha256'],'Sealed pilot ledger changed')
    allowance=remaining();_STAGE_START=time.perf_counter();_DEADLINE=_STAGE_START+allowance
    write(OUT/'active-stage.json',dict(stage=stage,pid=os.getpid(),unix=time.time(),used_before=b['used_seconds']))
    progress(stage,capability=CAP)
def deadline():require(_DEADLINE is not None and time.perf_counter()<_DEADLINE,'Cumulative activity deadline exhausted')
def end(stage):
    global _STAGE_START
    torch.cuda.synchronize();seconds=time.perf_counter()-_STAGE_START
    b=read(OUT/'budget.json');b['new_seconds']+=seconds;b['used_seconds']=b['inherited_seconds']+b['new_seconds']
    b['items'].append(dict(stage=stage,capability=CAP,seconds=seconds));write(OUT/'budget.json',b);flush_reads(stage);_STAGE_START=None
def debit(kind,seconds,**extra):
    # Legacy inference compute() is nested in one process-owned stage. It records
    # work but does not double charge overlapping head/stream wall intervals.
    immutable(OUT/'timings'/f'{time.time_ns()}.json',dict(kind=kind,seconds=seconds,**extra))
@contextlib.contextmanager
def compute(kind,**extra):
    deadline();t=time.perf_counter()
    try:yield
    finally:torch.cuda.current_stream().synchronize();debit(kind,time.perf_counter()-t,**extra)
def progress(stage,**kw):write(OUT/'progress.json',dict(stage=stage,unix=time.time(),**kw));print(stage,kw,flush=True)
def failure(stage,e):
    immutable(OUT/'failures'/f'{stage}-{time.time_ns()}.json',dict(error=repr(e),traceback=traceback.format_exc(),no_automatic_retry=True))
    progress('stopped',stage_failed=stage,error=str(e))
def code_seal(tag):
    v=read(OUT/'manifests/code-seal.json');codecheck(v['files']);return v['files']
def codecheck(hashes=None):
    for p,h in (hashes or read(OUT/'manifests/code-seal.json')['files']).items():require(sha(ROOT/p)==h,'Executable source changed '+p)
