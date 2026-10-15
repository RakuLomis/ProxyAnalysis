"""Isolated, deterministic CUDA diagnostics; no business classifier fitting."""
from pathlib import Path
import hashlib
import json
import os
import time
os.environ.setdefault('CUBLAS_WORKSPACE_CONFIG', ':4096:8')
import numpy as np
import pandas as pd
import pyarrow.dataset
import pyarrow.parquet
import torch
import torch.nn.functional as F

ROOT = Path(__file__).resolve().parents[2]
KSR = ROOT/'outputs/kernel-sensitivity-regularization-20261005/run-01'
Q = ROOT/'outputs/protocol-probability-drift-20261004/run-01'
OUT = ROOT/'outputs/business-conditioned-kernel-20261005/run-01'
DOC = ROOT/'docs/business-conditioned-kernel'
PLAN = ROOT/'plan/business-conditioned-kernel-qualification-plan-20261005.md'
PROTOCOLS = ['shadowsocks','vless','trojan','vmess']
FEATURES = ['W_up','W_down','U_up','U_down','P_up','P_down','E_up','E_down',
            'FR_packet_runs','R_unique_zero_runs']
WEIGHTS = [1/12]*8+[1/6]*2
LABELS = ['bing.com::search_results_view','developer.mozilla.org::document_view',
          'github.com::repository_view','wikipedia.org::article_view',
          'youtube.com::search_results_view','youtube.com::video_playback']
SHORT = ['Bing search','MDN documents','GitHub repository','Wikipedia article',
         'YouTube search','YouTube playback']
BYTE_EDGES = [1,256,1024,4096,16384,65536,262144,1048576]
COUNT_EDGES = [1,2,3,4,8,16,32,64,128]
HIST = [f'h{j:02d}_{b:02d}' for j in range(10) for b in range(9 if j<4 else 10)]
KAPPAS = ['0.25','1','4','16','inf']
TARGETS = ['T0','T1','G0','G1','P0','P1']
PI = 1/6
ACCESS = []

def require(ok, message):
    if not ok: raise RuntimeError(message)

def read(path): return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def write(path, value):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2,sort_keys=True,
                               allow_nan=False)+'\n',encoding='utf-8')
def sha(path):
    require(Path(path).suffix.lower() not in ['.pcap','.pcapng','.cap'],'No PCAP access')
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''): h.update(block)
    return h.hexdigest()
def rel(path): return Path(path).resolve().relative_to(ROOT).as_posix()
def device():
    require(torch.cuda.is_available(),'CUDA required; no CPU numerical fallback')
    return torch.device('cuda:0')
def configure():
    device(); torch.set_num_threads(1)
    torch.backends.cuda.matmul.allow_tf32=False; torch.backends.cudnn.allow_tf32=False
    torch.use_deterministic_algorithms(True)
def tensor(x,dtype=torch.float64): return torch.as_tensor(np.asarray(x),device=device(),dtype=dtype)
def size(j): return 9 if j<4 else 10
def bins(x,j):
    x=np.asarray(x); require(np.isfinite(x).all() and (x>=0).all() and (x==np.floor(x)).all(),'Invalid features')
    return tensor(np.searchsorted(BYTE_EDGES if j<4 else COUNT_EDGES,x,side='right'),torch.long)
def weighted(index, mass, n): return F.one_hot(index,num_classes=n).to(torch.float64).T@mass
def save(df,path):
    Path(path).parent.mkdir(parents=True,exist_ok=True); df.to_parquet(path,index=False)
def folder(kind,r,base=OUT):
    p=base/kind/('outer' if r['inner'] is None else 'inner')/f"f{r['outer']}"/r['protocol']
    return p if r['inner'] is None else p/f"i{r['inner']}"
def key(r): return f"f{r['outer']}/{r['protocol']}/"+('outer' if r['inner'] is None else f"i{r['inner']}")
def contract(): return read(OUT/'manifests/experiment-contract.json')
def checked(path, mapping, role):
    h=sha(path); require(mapping.get(rel(path))==h,'Unsealed or changed: '+rel(path))
    ACCESS.append({'role':role,'path':rel(path),'sha256':h})
def start(stage):
    configure(); ACCESS.clear(); c=contract()
    for p,h in c['source_sha256'].items(): require(sha(ROOT/p)==h,'Source changed after registration')
    return c
def package(r,name,role):
    allowed={'fit':{'train-paired','group-pre','group-post','train-label-map','train-post-hist'},
             'activity':{'train-post-hist'},'oracle':{'oracle-pre-Y'},
             'inner_score':{'moment-score'},'outer_score':{'moment-score','score-post'},
             'verify':{'train-paired','group-pre','group-post','train-label-map','train-post-hist',
                       'oracle-pre-Y','moment-score','score-post'}}
    require(name in allowed[role],'Forbidden role read')
    if role=='inner_score': require(r['inner'] is not None,'Inner scoring cannot read outer')
    if role in ['oracle','outer_score']:
        require(r['inner'] is None and (OUT/'qualification/complete.json').exists(),'Outer gate not sealed')
    p=folder('packages',r)/(name+'.parquet'); checked(p,contract()['packages_sha256'],role)
    return pd.read_parquet(p)
def load_old(kind,r,name):
    p=folder(kind,r,KSR)/(name+'.pt')
    checked(p,contract()['baseline_sha256'],'frozen_'+kind)
    require(read(p.parent/'complete.json')['sha256'][p.name]==sha(p),'Old complete mismatch')
    return torch.load(p,map_location=device(),weights_only=True)
def complete(path,**extra):
    path=Path(path)
    write(path/'complete.json',{'time_unix':time.time(),
        'sha256':{p.name:sha(p) for p in path.iterdir() if p.suffix in ['.pt','.parquet']},**extra})
def load_bundle(r,j,kind='kernels'):
    p=folder(kind,r)/(FEATURES[j]+'.pt')
    require(read(p.parent/'complete.json')['sha256'][p.name]==sha(p),'New artifact changed')
    ACCESS.append({'role':'load_'+kind,'path':rel(p),'sha256':sha(p)})
    return torch.load(p,map_location=device(),weights_only=True)
def finish(stage,**extra):
    write(OUT/'manifests'/f'{stage}-ledger.json',{'reads':ACCESS,'completed_unix':time.time(),**extra})
    write(OUT/'progress.json',{'stage':stage,'time_unix':time.time(),**extra})
    print(stage,extra,flush=True)
def smooth(counts):
    k=counts.shape[-1]; q=(counts.sum(0)+1/k)/(counts.sum()+1)
    return (counts+q)/(counts.sum(1,keepdim=True)+1),q
def conditional(counts,common,kappa):
    if kappa=='inf': return common.expand(6,*common.shape).clone()
    v=float(kappa); return (counts+v*common)/(counts.sum(2,keepdim=True)+v)
def post_conditional(counts,q,kappa):
    b=counts.sum(1)
    if kappa=='inf': return q.expand(6,-1).clone()
    v=float(kappa); return (b+v*q)/(b.sum(1,keepdim=True)+v)
def covariance(counts,rows):
    """rows[y,a,b] normalized; zero-supported y/a never acquires weight."""
    ya=counts.sum(2); a=ya.sum(0); total=a.sum()
    p=ya/a.clamp_min(1e-300); nu=a/total
    mean=(p[:,:,None]*rows).sum(0)
    inner=torch.diag_embed(rows)-rows[:,:,:,None]*rows[:,:,None,:]
    within=(nu[None,:,None,None]*p[:,:,None,None]*inner).sum((0,1))
    offset=rows-mean[None]
    between=(nu[None,:,None,None]*p[:,:,None,None]*offset[:,:,:,None]*offset[:,:,None,:]).sum((0,1))
    allcov=(nu[:,None,None]*(torch.diag_embed(mean)-mean[:,:,None]*mean[:,None,:])).sum(0)
    return within,between,allcov,mean,nu
def empirical_rows(counts):
    n=counts.sum(2,keepdim=True)
    return torch.where(n>0,counts/n.clamp_min(1e-300),torch.full_like(counts,1/counts.shape[-1]))
def moment_targets(bundle):
    n=bundle['true_by_y']; S=n.sum(2)/n.sum((1,2))[:,None]
    g=bundle['group_by_y']; SG=g.sum(2)/g.sum((1,2))[:,None]
    require(float((S-SG).abs().max())<1e-10,'Class pre margins inconsistent')
    kt,kg=bundle['common_true'],bundle['common_group']
    return {'T0':PI*(S*kt[:,4:].sum(1)).sum(1),
            'T1':PI*(S*bundle['true_1'][:,:,4:].sum(2)).sum(1),
            'G0':PI*(S*kg[:,4:].sum(1)).sum(1),
            'G1':PI*(S*bundle['group_1'][:,:,4:].sum(2)).sum(1),
            'P0':PI*n.sum(1)[:,4:].sum(1)/n.sum((1,2)),
            'P1':PI*bundle['post_1'][:,4:].sum(1)}
def interval(target,resids):
    rawlo=target+min(resids); rawhi=target+max(resids)
    lo=max(0.,rawlo); hi=min(PI,rawhi)
    return rawlo,rawhi,lo,hi,lo<=hi
def family(j): return 'bytes' if j<4 else ('events' if j<8 else 'interaction')
