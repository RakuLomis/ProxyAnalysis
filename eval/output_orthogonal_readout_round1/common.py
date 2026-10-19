"""OR1 isolated IO and immutable role/arm source bindings."""
from pathlib import Path
import contextlib
import hashlib
import importlib.util
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
CODE=Path(__file__).resolve().parent
OLD=ROOT/'outputs/post-associated-frozen-readout-20261014/run-01'
TEMP=ROOT/'outputs/post-associated-temperature-calibration-20261015/run-02'
OUT=ROOT/'outputs/output-orthogonal-readout-round1-20261015/run-01'
DOC=ROOT/'docs/output-orthogonal-readout-round1-20261015'
PLAN=ROOT/'plan/output-orthogonal-readout-round1-plan-20261015.md'
PREP=ROOT/'outputs/calibrated-deployment-business-transfer-20261006/run-01'
JA=ROOT/'outputs/joint-affine-transfer-20261007/run-01'
ARMS=['OR-X','OR-R','OR-G','OR-P','OR-BIAS']
SEEDS=[20261014,20261015,20261016]
HIST=[f'h{j:02}_{i:02}' for j in range(10) for i in range(9 if j<4 else 10)]
LABELS=['bing.com::search_results_view','developer.mozilla.org::document_view','github.com::repository_view',
        'wikipedia.org::article_view','youtube.com::search_results_view','youtube.com::video_playback']
PC=[f'p{i}' for i in range(6)];LC=[f'l{i}' for i in range(6)]
READS=[]; ACTIVE=None; FIT_START=None

def require(ok,msg):
    if not bool(ok):raise RuntimeError(msg)
def rel(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def write(p,obj):
    p=Path(p).resolve();require(p.is_relative_to(OUT) or p.is_relative_to(DOC),'Write outside OR1')
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf-8') as f:
        json.dump(obj,f,indent=2,sort_keys=True,ensure_ascii=False,allow_nan=False,
                  default=lambda v:v.item() if isinstance(v,np.generic) else str(v));f.write('\n')
def mutable(p,obj):
    require(p.parent==OUT and p.name in ['ledger.json','progress.json'],'Only engineering counters mutable')
    p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_suffix('.tmp')
    tmp.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n',encoding='utf-8');os.replace(tmp,p)
def ledger(**add):
    p=OUT/'ledger.json';x=read(p)
    for k,v in add.items():x[k]=x.get(k,0)+v
    mutable(p,x)
def progress(stage,**kw):
    mutable(OUT/'progress.json',dict(stage=stage,time_unix=time.time(),pid=os.getpid(),**kw))
    print(stage,kw,flush=True)
def seal(p,paths,**kw):write(p,dict(passed=True,files={rel(v):sha(v) for v in sorted(set(paths))},**kw))
def verify(p):
    m=read(p);require(m.get('passed',False),'Incomplete seal')
    for name,h in m['files'].items():require(sha(ROOT/name)==h,'Changed sealed file '+name)
def contract():
    p=OUT/'manifests/contract.json';require(sha(p)==read(OUT/'manifests/contract-seal.json')['sha256'],'Changed contract')
    return read(p)
def configure():
    require(torch.cuda.is_available(),'CUDA required; CPU fallback forbidden')
    torch.set_num_threads(1);torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
    torch.use_deterministic_algorithms(True)
def device():return torch.device('cuda:0')
def tensor(v,dtype=torch.float64):return torch.as_tensor(np.asarray(v),device=device(),dtype=dtype)
def check_source(p,purpose,rid=None,arm=None):
    info=contract()['sources'].get(rel(p));require(info is not None,'Unregistered source')
    if rid is not None:require(info.get('role_id')==rid,'Cross-role source')
    allowed={'train':{'classification','base','g-R','g-G','g-P'},
             'predict':{'query-post'},'labels':{'query-label'},'control':{'old-prediction','old-temperature','old-calibrated','old-score'},
             'provenance':{'source-post','source-pre','C-post','CT1','CT2','JA1'}}
    require(info['kind'] in allowed[purpose],'Forbidden source purpose')
    if info['kind'].startswith('g-'):
        require(arm in ['OR-R','OR-G','OR-P'] and info['kind']=='g-'+arm[-1],'Wrong G arm or G forbidden')
    if purpose=='predict':require((OUT/'manifests/models-complete.json').exists(),'All heads must seal before query')
    if purpose=='labels':require(ACTIVE in ['calibrate','score','audit'] and (OUT/'predictions/raw-complete.json').exists(),'Labels before raw prediction seal')
    require(sha(p)==info['sha256'],'Changed historical input')
    READS.append(dict(path=rel(p),kind=info['kind'],purpose=purpose,role_id=rid,arm=arm))
    return info
def source_tensor(p,rid,arm=None):
    check_source(p,'train',rid,arm);return torch.load(p,map_location=device(),weights_only=True)
def source_frame(p,purpose,rid=None):
    info=check_source(p,purpose,rid);x=pd.read_parquet(p)
    if 'columns' in info:require(list(x)==info['columns'] and len(x)==info['rows'],'Changed schema/count')
    return x
def own(p):
    require(sha(p)==read(p.with_suffix('.json'))['sha256'],'Changed own tensor')
    return torch.load(p,map_location=device(),weights_only=True)
def put(p,x,**kw):
    require(p.is_relative_to(OUT) and not p.exists(),'No overwrite tensor');p.parent.mkdir(parents=True,exist_ok=True)
    torch.save(x,p);write(p.with_suffix('.json'),dict(sha256=sha(p),**kw))
def save(p,x):
    require(p.is_relative_to(OUT) and not p.exists(),'No overwrite table');p.parent.mkdir(parents=True,exist_ok=True);x.to_parquet(p,index=False)
def seed_for(arm,seed):return 0 if arm in ['OR-X','OR-BIAS'] else seed
def modelpath(r,arm,seed):return OUT/'models'/r['id']/f'{arm}-seed{seed_for(arm,seed)}.pt'
def train(r,arm,seed):
    s=source_tensor(ROOT/r['classification'],r['id']);m=source_tensor(ROOT/r['base'],r['id'])
    require(s['x'].shape==(480,96) and s['real_x'].shape==(192,96),'Frozen rows')
    require(torch.equal(s['mu'],m['mu']) and torch.equal(s['scale'],m['scale']),'Frozen scale')
    require(abs(float(s['mass'].sum())-1)<1e-12 and float((F.one_hot(s['y'],6).double().T@s['mass']-1/6).abs().max())<1e-12,'Frozen sample mass')
    g=None if arm in ['OR-X','OR-BIAS'] else source_tensor(ROOT/r['frozen_G'][f'{arm}-{seed}'],r['id'],arm)
    return s,m,g
def features(x,g,arm):
    if arm=='OR-BIAS':return torch.empty((len(x),0),device=device(),dtype=torch.float64)
    xx=x.float()
    if g is None:return xx.double()
    require(all(v.is_cuda and v.dtype==torch.float32 and not v.requires_grad for v in g.values()),'G precision/freeze')
    with torch.no_grad():z=F.linear(F.relu(F.linear(xx,g['w0'],g['b0'])),g['w1'],g['b1'])
    return torch.cat([xx,z],1).double()
def offset(x,m):return x@m['weight'].T+m['bias']
def budget():
    used=read(OUT/'ledger.json')['fit_seconds']+(0. if FIT_START is None else time.perf_counter()-FIT_START)
    require(used<3600,'Cumulative 3600s fit budget exhausted')
@contextlib.contextmanager
def stage(name):
    global ACTIVE
    configure();ACTIVE=name;READS.clear();verify(OUT/'manifests/code.json')
    require(sha(PLAN)==contract()['plan_sha256'],'Plan changed')
    require(not (OUT/'stages'/f'{name}.json').exists(),'Completed stage cannot repeat')
    start=time.perf_counter();progress(name+'_running')
    try:
        yield
        write(OUT/'stages'/f'{name}.json',dict(passed=True,seconds=time.perf_counter()-start,reads=READS))
        progress(name+'_complete')
    except BaseException as exc:
        write(OUT/'failures'/f'{name}-{time.time_ns()}.json',dict(reason=str(exc),traceback=traceback.format_exc(),reads=READS))
        write(OUT/'completion.json',dict(passed=False,status='stop_stage_gate',stage=name,reason=str(exc),H_scored=False,automatic_retry=False))
        progress(name+'_failed',reason=str(exc));raise
    finally:ACTIVE=None
