"""Immutable inputs and role-limited IO for the registered business experiment."""
from pathlib import Path
import hashlib
import json
import time
import os
os.environ.setdefault('CUBLAS_WORKSPACE_CONFIG', ':4096:8')
import numpy as np
import pandas as pd
import torch

ROOT = Path(__file__).resolve().parents[2]
OLD = ROOT / 'outputs/protocol-probability-drift-20261004/run-01'
OUT = ROOT / 'outputs/drift-kernel-business-20261005/run-01'
DOC = ROOT / 'docs/drift-kernel-business'
PLAN = ROOT / 'plan/drift-kernel-generative-business-classification-plan-20261005.md'
PROTOCOLS = ['shadowsocks', 'vless', 'trojan', 'vmess']
FEATURES = ['W_up','W_down','U_up','U_down','P_up','P_down','E_up','E_down',
            'FR_packet_runs','R_unique_zero_runs']
WEIGHTS = [1/12]*8 + [1/6]*2
BYTE_EDGES = [1,256,1024,4096,16384,65536,262144,1048576]
COUNT_EDGES = [1,2,3,4,8,16,32,64,128]
LABELS = ['bing.com::search_results_view','developer.mozilla.org::document_view',
          'github.com::repository_view','wikipedia.org::article_view',
          'youtube.com::search_results_view','youtube.com::video_playback']
ARMS = ['G0','G1','G2','G3','G4','G5']
SEEDS = [20261005,20261006,20261007]
EXPECTED = {'shadowsocks':5608,'vless':5957,'trojan':5919,'vmess':6082}
HIST = [f'h{j:02d}_{b:02d}' for j,f in enumerate(FEATURES) for b in range(9 if j<4 else 10)]
ACCESS = []

def require(value, message):
    if not value:
        raise RuntimeError(message)

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2,
                               allow_nan=False)+'\n', encoding='utf-8')

def sha(path):
    p = Path(path)
    require(p.suffix.lower() not in ['.pcap','.pcapng','.cap'], 'No raw PCAP access permitted')
    h = hashlib.sha256()
    with p.open('rb') as stream:
        for block in iter(lambda: stream.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()

def rel(path):
    return Path(path).resolve().relative_to(ROOT).as_posix()

def cuda():
    require(torch.cuda.is_available(), 'CUDA required; CPU fallback forbidden')
    return torch.device('cuda:0')

def tensor(x, dtype=torch.float64):
    return torch.as_tensor(np.asarray(x), dtype=dtype, device=cuda())

def rolefolder(fold, protocol):
    return OUT / 'packages' / f'f{fold}' / protocol

def modelfolder(fold, protocol):
    return OUT / 'models' / f'f{fold}' / protocol

def start(role):
    ACCESS.clear()
    c = read(OUT / 'manifests/experiment-contract.json')
    for p,h in c['source_sha256'].items():
        require(sha(ROOT/p)==h, 'Sealed source changed: '+p)
    cuda()
    return c

def load_package(path, role):
    allowed = {'distribution_fit': {'fit-pre.parquet','fit-post.parquet'},
               'baseline_fit': {'fit-post-hist.parquet'},
               'predict': {'query-post-hist.parquet'},
               'score': {'score-labels.parquet'},
               'explain': {'fit-pre.parquet','fit-post.parquet','fit-post-hist.parquet',
                           'query-post-hist.parquet','score-labels.parquet'},
               'verify': {'fit-pre.parquet','fit-post.parquet','fit-post-hist.parquet',
                          'query-post-flow.parquet','query-post-hist.parquet','score-labels.parquet'}}
    path = Path(path)
    require(path.name in allowed[role], 'Role attempted forbidden package: '+str(path))
    c = read(OUT / 'manifests/experiment-contract.json')
    require(sha(path)==c['packages_sha256'][rel(path)], 'Sealed package changed')
    ACCESS.append({'role':role,'path':rel(path),'sha256':sha(path)})
    return pd.read_parquet(path)

def model_load(path, role):
    path = Path(path)
    require(path.is_relative_to(OUT/'models'), 'Model outside registered output')
    require(sha(path)==read(path.parent/'complete.json')['sha256'][path.name], 'Model changed')
    ACCESS.append({'role':role,'path':rel(path),'sha256':sha(path)})
    return torch.load(path, map_location=cuda(), weights_only=True)

def kernel_load(fold, protocol, feature, role):
    path = OLD/'kernels/primary'/f'f{fold}'/protocol/(feature+'.pt')
    c = read(OUT/'manifests/experiment-contract.json')
    require(sha(path)==c['kernels_sha256'][rel(path)], 'Frozen kernel changed')
    ACCESS.append({'role':role,'path':rel(path),'sha256':sha(path)})
    return torch.load(path,map_location=cuda(),weights_only=True)

def finish(role, **details):
    write(OUT/'manifests'/f'{role}-ledger.json', {'reads':ACCESS,**details})
    write(OUT/'progress.json', {'stage':role,'time_unix':time.time(),**details})

def size(feature):
    return 9 if feature.startswith(('W_','U_')) else 10

def encode(values, feature):
    x = np.asarray(values)
    require(np.isfinite(x).all() and (x>=0).all() and np.equal(x,np.floor(x)).all(),
            'Noninteger, missing or negative observation')
    return np.searchsorted(BYTE_EDGES if size(feature)==9 else COUNT_EDGES,x,side='right')

def mass(frame):
    reps=frame[['content_id','session_id']].drop_duplicates().groupby('content_id').size()
    n=frame.groupby('session_id').size()
    return 1/(frame.content_id.map(reps).to_numpy(float)*frame.session_id.map(n).to_numpy(float))

def saveparquet(frame, path):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    frame.to_parquet(path,index=False)

def visits_histogram(frame, side, idcol='session_id'):
    """Fixed preprocessing on CUDA; consumes only the declared side's statistics."""
    names=sorted(frame[idcol].unique())
    ids={v:i for i,v in enumerate(names)}
    vi=tensor(frame[idcol].map(ids),torch.int64)
    n=torch.bincount(vi,minlength=len(names)).to(torch.float64)
    result=[]
    for f in FEATURES:
        b=tensor(encode(frame[side+'_'+f],f),torch.int64)
        h=torch.bincount(vi*size(f)+b,minlength=len(names)*size(f)).reshape(len(names),size(f))/n[:,None]
        require(torch.allclose(h.sum(1),torch.ones_like(n),atol=1e-12), 'Histogram not normalized')
        result.append(h)
    return names,torch.cat(result,1)

def composite(h, tables):
    scores=torch.full((len(h),6), -np.log(6),dtype=torch.float64,device=cuda())
    at=0
    for j,f in enumerate(FEATURES):
        q=tables[f]
        require(torch.all(q>0).item() and torch.allclose(q.sum(1),torch.ones(6,device=cuda(),dtype=q.dtype),atol=1e-12), 'Invalid business table')
        scores+=WEIGHTS[j]*(h[:,at:at+size(f)]@q.log().T)
        at+=size(f)
    return scores

def mlp_forward(x, state):
    return torch.relu(x@state['w1'].T+state['b1'])@state['w2'].T+state['b2']

def standardized(frame, mu, scale, dtype=torch.float64):
    # Match fit: normalize in float64, then cast the MLP input to float32.
    return ((tensor(frame[HIST])-mu.double())/scale.double()).to(dtype)

def js(p,q):
    m=(p+q)/2
    return float(.5*(np.sum(p*np.log(p/m))+np.sum(q*np.log(q/m))))
