"""Registered KSR resources, CUDA numerical operations and checked IO."""
from pathlib import Path
import hashlib
import json
import os
import time
os.environ.setdefault('CUBLAS_WORKSPACE_CONFIG', ':4096:8')
# Arrow must initialize before torch on this Windows environment.
import numpy as np
import pandas as pd
import pyarrow.dataset
import pyarrow.parquet
import torch
import torch.nn.functional as F

ROOT = Path(__file__).resolve().parents[2]
G = ROOT/'outputs/drift-kernel-business-20261005/run-01'
Q = ROOT/'outputs/protocol-probability-drift-20261004/run-01'
OUT = ROOT/'outputs/kernel-sensitivity-regularization-20261005/run-01'
DOC = ROOT/'docs/kernel-sensitivity-regularization'
PLAN = ROOT/'plan/kernel-conditioned-sensitivity-regularization-plan-20261005.md'
PROTOCOLS = ['shadowsocks','vless','trojan','vmess']
FEATURES = ['W_up','W_down','U_up','U_down','P_up','P_down','E_up','E_down',
            'FR_packet_runs','R_unique_zero_runs']
WEIGHTS = [1/12]*8+[1/6]*2
BYTE_EDGES = [1,256,1024,4096,16384,65536,262144,1048576]
COUNT_EDGES = [1,2,3,4,8,16,32,64,128]
LABELS = ['bing.com::search_results_view','developer.mozilla.org::document_view',
          'github.com::repository_view','wikipedia.org::article_view',
          'youtube.com::search_results_view','youtube.com::video_playback']
HIST = [f'h{j:02d}_{b:02d}' for j in range(10) for b in range(9 if j<4 else 10)]
ARMS = ['KSR0','KSR1','KSR2','KSR3','KSR4']
TS = [0,.25,1,4]
ACCESS = []

def require(ok, message):
    if not ok:
        raise RuntimeError(message)

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def write(path, value):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2,
                               allow_nan=False)+'\n',encoding='utf-8')

def sha(path):
    path=Path(path)
    require(path.suffix.lower() not in ['.pcap','.pcapng','.cap'],'PCAP access forbidden')
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''): h.update(block)
    return h.hexdigest()

def rel(path): return Path(path).resolve().relative_to(ROOT).as_posix()

def cuda():
    require(torch.cuda.is_available(),'CUDA required; no CPU fallback')
    return torch.device('cuda:0')

def configure():
    cuda(); torch.set_num_threads(1)
    torch.backends.cuda.matmul.allow_tf32=False
    torch.backends.cudnn.allow_tf32=False
    torch.use_deterministic_algorithms(True)

def tensor(value,dtype=torch.float64):
    return torch.as_tensor(np.asarray(value),device=cuda(),dtype=dtype)

def size(feature): return 9 if feature.startswith(('W_','U_')) else 10

def encode(value,feature):
    x=np.asarray(value)
    require(np.isfinite(x).all() and (x>=0).all() and (x==np.floor(x)).all(),
            'Invalid nonnegative integer feature')
    return np.searchsorted(BYTE_EDGES if size(feature)==9 else COUNT_EDGES,x,side='right')

def saveparquet(frame,path):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    frame.to_parquet(path,index=False)

def folder(kind,outer,protocol,inner=None):
    base=OUT/kind/('outer' if inner is None else 'inner')/f'f{outer}'/protocol
    return base if inner is None else base/f'i{inner}'

def contract(): return read(OUT/'manifests/experiment-contract.json')

def start(role):
    configure(); ACCESS.clear(); c=contract()
    for p,h in c['source_sha256'].items():
        require(sha(ROOT/p)==h,'Sealed source changed: '+p)
    return c

def package(path,role):
    allowed={'matrix':{'fit-pre.parquet','fit-post.parquet','fit-post-hist.parquet','group-pre.parquet','group-post.parquet'},
             'fit':{'fit-post-hist.parquet'},'predict':{'query-post-hist.parquet'},
             'select':{'score-labels.parquet'},'score':{'score-labels.parquet'},
             'explain':{'fit-post-hist.parquet'},
             'verify':{'fit-pre.parquet','fit-post.parquet','fit-post-hist.parquet',
                       'group-pre.parquet','group-post.parquet','query-post-hist.parquet','score-labels.parquet'}}
    path=Path(path); require(path.name in allowed[role],'Forbidden package for '+role)
    if role=='select': require('/inner/' in path.as_posix(),'Selection cannot read outer labels')
    c=contract(); h=sha(path)
    require(c['packages_sha256'].get(rel(path))==h,'Package not sealed or changed')
    df=pd.read_parquet(path)
    if role=='predict':
        require(set(df)=={'visit_id',*HIST},'Query contains forbidden metadata/pre/labels')
    ACCESS.append({'role':role,'path':rel(path),'sha256':h})
    return df

def artifact(path,role):
    path=Path(path); h=sha(path)
    require(read(path.parent/'complete.json')['sha256'].get(path.name)==h,'Artifact changed')
    if role=='predict': require('/models/' in path.as_posix(),'Prediction may load only models')
    ACCESS.append({'role':role,'path':rel(path),'sha256':h})
    return torch.load(path,map_location=cuda(),weights_only=True)

def outer_kernel(r,feature,c):
    require(r['inner'] is None,'Inner matrix cannot load an old outer kernel')
    require((OUT/'selection/complete.json').exists(),'Outer kernels allowed only after sealed selection')
    path=Q/'kernels/primary'/f"f{r['outer']}"/r['protocol']/(feature+'.pt')
    require(c['outer_kernels_sha256'].get(rel(path))==sha(path),'Frozen outer kernel changed')
    ACCESS.append({'role':'outer_matrix','path':rel(path),'sha256':sha(path)})
    return torch.load(path,map_location=cuda(),weights_only=True)

def complete(path,**details):
    write(Path(path)/'complete.json',{'sha256':{p.name:sha(p) for p in Path(path).glob('*.pt')},**details})

def resume(path):
    done=Path(path)/'complete.json'
    if not done.exists(): return False
    for name,h in read(done)['sha256'].items(): require(sha(Path(path)/name)==h,'Resume artifact changed')
    return True

def finish(role,**details):
    write(OUT/'manifests'/f'{role}-ledger.json',{'reads':ACCESS,**details})
    write(OUT/'progress.json',{'stage':role,'time_unix':time.time(),**details})

def standardize(frame):
    raw=tensor(frame[HIST]); mu=raw.mean(0); scale=raw.std(0,unbiased=False)
    scale=torch.where(scale>0,scale,torch.ones_like(scale))
    return (raw-mu)/scale,mu,scale

def sensitivity(w,factor):
    centered=w-w.mean(0,keepdim=True)
    return (centered@factor).square().sum()/5

def loss(w,b,x,y,arm,t,factor=None):
    base=F.cross_entropy(x@w.T+b,y)+.0005*w.square().sum()
    if t==0: return base
    if arm=='KSR1': return base+.0005*t*w.square().sum()
    require(factor is not None,'Missing structural factor')
    return base+.0025*t*sensitivity(w,factor)

def lr_fit(x,y,arm='KSR0',t=0,factor=None):
    w=torch.nn.Parameter(torch.zeros((6,96),device=cuda(),dtype=torch.float64))
    b=torch.nn.Parameter(torch.zeros(6,device=cuda(),dtype=torch.float64))
    opt=torch.optim.LBFGS([w,b],max_iter=500,tolerance_grad=1e-9,
                          tolerance_change=1e-12,line_search_fn='strong_wolfe')
    evaluations=0; started=time.perf_counter()
    def closure():
        nonlocal evaluations
        evaluations+=1; opt.zero_grad()
        value=loss(w,b,x,y,arm,t,factor); value.backward(); return value
    opt.step(closure); final=float(closure().detach()); torch.cuda.synchronize()
    it=int(opt.state[w].get('n_iter',0))
    return {'weight':w.detach(),'bias':b.detach()}, {'iterations':it,'closure_evaluations':evaluations,
         'objective':final,'max_gradient':max(float(w.grad.abs().max()),float(b.grad.abs().max())),
         'hit_iteration_budget':it>=500,'seconds':time.perf_counter()-started,
         'device':'cuda:0','dtype':'float64','arm':arm,'t':t}

def probabilities(model,query):
    require(set(query)=={'visit_id',*HIST},'post-only query rejected')
    with torch.no_grad():
        x=(tensor(query[HIST])-model['mu'])/model['scale']
        s=x@model['weight'].T+model['bias']; p=torch.softmax(s,1)
    df=pd.DataFrame(p.cpu().numpy(),columns=[f'p{i}' for i in range(6)])
    df['visit_id']=query.visit_id.to_numpy(); df['prediction']=p.argmax(1).cpu().numpy()
    return df

def metrics(y,p):
    y=np.asarray(y,dtype=int); pred=p.argmax(1)
    cm=np.bincount(y*6+pred,minlength=36).reshape(6,6)
    tp=np.diag(cm); den=cm.sum(0)+cm.sum(1)
    f1=np.divide(2*tp,den,out=np.zeros(6),where=den>0)
    return {'F1':float(f1.mean()),'accuracy':float((y==pred).mean()),
            'CE':float(-np.log(p[np.arange(len(y)),y]).mean()),
            'Brier':float(((p-np.eye(6)[y])**2).sum(1).mean())},cm

def truths(frame): return frame.label_id.map({v:i for i,v in enumerate(LABELS)}).to_numpy(int)
