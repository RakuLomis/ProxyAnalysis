"""DP-GAN1-M v1 isolated roots, role/capability readers and cumulative budget."""
from pathlib import Path
import os,json,time,hashlib,contextlib,traceback,sys
os.environ.setdefault('CUBLAS_WORKSPACE_CONFIG',':4096:8')
import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F

ROOT=Path(__file__).resolve().parents[2];CODE=Path(__file__).resolve().parent
OUT=ROOT/'outputs/deproxy-moment-game-v1-20261016/run-01'
DOC=ROOT/'docs/deproxy-moment-game-v1-20261016'
PLAN=ROOT/'plan/DP-GAN1-M-v1-local-implementation-plan-20261016.md'
PROPOSAL=Path('C:/Users/Windows/Desktop/DP_GAN1_M_v1_implementation_plan_20261016.md')
ASSOC=ROOT/'outputs/post-input-associated-representation-20261014/run-01'
PREP=ROOT/'outputs/calibrated-deployment-business-transfer-20261006/run-01'
NATIVE=ROOT/'outputs/protocol-probability-drift-20261004/run-01/features/paired-flow-features.parquet'
PROTOCOLS=['shadowsocks','vless','trojan','vmess']
LABELS=['bing.com::search_results_view','developer.mozilla.org::document_view','github.com::repository_view',
        'wikipedia.org::article_view','youtube.com::search_results_view','youtube.com::video_playback']
FEATURES=['W_up','W_down','U_up','U_down','P_up','P_down','E_up','E_down','FR_packet_runs','R_unique_zero_runs']
SIZES=[9]*4+[10]*6;HIST=[f'h{j:02}_{k:02}' for j,n in enumerate(SIZES) for k in range(n)]
MASKS={'G0':[2,4],'G1':[0,3],'G2':[1,5]};SEEDS=[20261014,20261015,20261016]
RECIPES=[dict(id=f'H{i+1:02}',lr=lr,gamma=g) for i,(lr,g) in enumerate((lr,g) for lr in [.0003,.001] for g in [.0001,.001,.01])]
GAMMAS=[.0001,.001,.01];DYNAMIC=['N-P','F-P','F-G','E-post'];METHODS=['R-P','R-G']+DYNAMIC
BETAS=[0.,.25,.5,.75,1.];READS=[];CAP='none';_C=None;_CACHE={};_SEALS={}

def require(ok,msg):
    if not bool(ok):raise RuntimeError(msg)
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def rel(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def sha(p):
    p=Path(p);require(p.suffix.lower() not in {'.pcap','.pcapng','.cap'},'PCAP forbidden')
    h=hashlib.sha256()
    with p.open('rb') as f:
        for x in iter(lambda:f.read(1048576),b''):h.update(x)
    return h.hexdigest()
def writable(p):
    p=Path(p).resolve();require(p.is_relative_to(OUT) or p.is_relative_to(DOC),'Write outside new experiment roots')
    p.parent.mkdir(parents=True,exist_ok=True);return p
def scalar(x):
    if isinstance(x,np.generic):return x.item()
    if isinstance(x,Path):return str(x)
    raise TypeError(type(x).__name__)
def write(p,v):
    p=writable(p);t=p.with_name(p.name+'.tmp');t.write_text(json.dumps(v,ensure_ascii=False,indent=2,sort_keys=True,allow_nan=False,default=scalar)+'\n',encoding='utf-8');os.replace(t,p)
def immutable(p,v):require(not Path(p).exists(),'Refuse record overwrite: '+str(p));write(p,v)
def put(p,v,**meta):
    p=writable(p);require(not p.exists(),'Refuse tensor overwrite')
    tmp=p.with_name(p.name+'.tmp');torch.save(v,tmp);os.replace(tmp,p)
    immutable(p.with_suffix('.json'),dict(sha256=sha(p),**meta))
def save(p,d):
    p=writable(p);require(not p.exists(),'Refuse table overwrite');d.to_parquet(p,index=False)
def seal(p,files,**meta):
    files=[Path(f) for f in files];files+= [f.with_suffix('.json') for f in files if f.suffix=='.pt']
    immutable(p,dict(files={rel(f):sha(f) for f in dict.fromkeys(files)},**meta))
def verifyseal(p):
    p=Path(p);sig=(p.stat().st_size,p.stat().st_mtime_ns)
    if str(p) in _SEALS and _SEALS[str(p)][0]==sig:return _SEALS[str(p)][1]
    v=read(p)
    for f,h in v['files'].items():require(sha(ROOT/f)==h,'Sealed asset changed: '+f)
    _SEALS[str(p)]=(sig,v);return v
def barrier(name):
    p=OUT/'manifests'/name;require(p.exists(),'Missing phase barrier: '+name);return verifyseal(p)
def configure(cap='none'):
    global CAP
    CAP=cap;require(torch.cuda.is_available(),'CUDA mandatory')
    torch.set_num_threads(1);torch.use_deterministic_algorithms(True)
    torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
def tensor(x,dtype=torch.float64):return torch.as_tensor(np.asarray(x),device='cuda',dtype=dtype)
def cpu(x):return x.detach().cpu().numpy()
def contract():
    global _C
    if _C is None:
        p=OUT/'manifests/contract.json';require(sha(p)==read(p.with_suffix('.seal.json'))['sha256'],'Contract changed');_C=read(p)
    return _C
def roles():return contract()['inner_roles']+contract()['roles']
def lookup(rid):return next(r for r in roles() if r['id']==rid)
def pilot_roles():
    nxt={p:PROTOCOLS[(i+1)%4] for i,p in enumerate(PROTOCOLS)}
    return [r for r in contract()['inner_roles'] if r['outer']==0 and r['inner']==1 and r['calibration']==nxt[r['target']]]
def own(p,rid=None):
    p=Path(p);require(p.resolve().is_relative_to(OUT),'Own reader root');m=read(p.with_suffix('.json'))
    if rid is not None:require(m.get('role_id')==rid,'Cross-role own asset')
    kind=m.get('capability','shared')
    allowed={'P':{'P','shared','pre','post'},'G':{'G','shared','pre','post'},'E':{'E','shared','post'},
             'trusted':{'P','G','E','shared','pre','post','trusted'},'inference':{'export','base'},'tests':{'P','G','E','shared','pre','post'}}
    require(kind in allowed.get(CAP,set()),'Capability denied '+kind+' for '+CAP)
    sig=(p.stat().st_size,p.stat().st_mtime_ns)
    if _CACHE.get(rel(p))!=(sig,m['sha256']):require(sha(p)==m['sha256'],'Own hash changed');_CACHE[rel(p)]=(sig,m['sha256'])
    READS.append(dict(path=rel(p),role_id=rid,capability=CAP,kind=kind,sha256=m['sha256']))
    return torch.load(p,map_location='cuda',weights_only=True)
def external(p,rid,kind):
    p=Path(p);info=contract()['files'].get(rel(p));require(info is not None and info['kind']==kind and info['role_id'] in [rid,None],'External role/schema')
    require(kind in {'source-post','source-pre','C-post','base','metadata'},'External numeric reader forbids query/native')
    require(CAP in {'trusted','tests','P','G','E','inference'},'No reader capability')
    if CAP=='E':require(kind in {'source-post','C-post','base','metadata'},'E cannot read pre')
    sig=(p.stat().st_size,p.stat().st_mtime_ns)
    if _CACHE.get(rel(p))!=(sig,info['sha256']):require(sha(p)==info['sha256'],'Historical asset changed');_CACHE[rel(p)]=(sig,info['sha256'])
    READS.append(dict(path=rel(p),role_id=rid,kind=kind,capability=CAP,sha256=info['sha256']))
    return torch.load(p,map_location='cuda',weights_only=True) if p.suffix=='.pt' else pd.read_parquet(p)
def flush_reads(tag):
    p=OUT/'permissions'/(tag+'-'+str(os.getpid())+'.json');write(p,dict(reads=READS,capability=CAP,H_pre_reads=0,target_U_training_reads=0,PCAP_reads=0))
def progress(stage,**kw):write(OUT/'progress.json',dict(stage=stage,unix=time.time(),**kw));print(stage,kw,flush=True)
def remaining():
    b=read(OUT/'budget.json');require(b['used_seconds']<86400,'Global activity budget exhausted; pending is not beta0');return 86400-b['used_seconds']
def debit(kind,seconds,**extra):
    b=read(OUT/'budget.json');b['used_seconds']+=seconds;b['items'].append(dict(kind=kind,seconds=seconds,**extra));write(OUT/'budget.json',b)
    require(b['used_seconds']<=86400,'Global activity budget exhausted; pending is not beta0')
@contextlib.contextmanager
def compute(kind,**extra):
    remaining();s=time.perf_counter()
    try:yield
    finally:
        torch.cuda.synchronize();debit(kind,time.perf_counter()-s,**extra)
def failure(stage,e):
    p=OUT/'failures'/(stage+'-'+str(time.time_ns())+'.json');immutable(p,dict(error=repr(e),traceback=traceback.format_exc(),no_automatic_retry=True))
    progress('stopped',stage_failed=stage,error=str(e))
def code_seal(tag):
    fs={}
    for p in sorted(CODE.glob('*.py')):
        q=writable(OUT/'code'/tag/p.name);require(not q.exists(),'Code tag exists');q.write_bytes(p.read_bytes());fs[rel(p)]=sha(p)
    immutable(OUT/'code'/tag/'seal.json',dict(files=fs,plan_sha256=sha(PLAN)));return fs
def codecheck(hashes):
    for p,h in hashes.items():require(sha(ROOT/p)==h,'Code changed during stage')
def block(j):a=sum(SIZES[:j]);return slice(a,a+SIZES[j])
def capfor(arm):return 'E' if arm=='E-post' else ('G' if arm in ['F-G','R-G'] else 'P')
def gamma_tag(g):return f'g{g:g}'
