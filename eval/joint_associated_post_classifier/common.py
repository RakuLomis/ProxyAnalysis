"""JAT1 source-only engineering boundary, immutable measurements and CUDA policy."""
from pathlib import Path
import contextlib
import hashlib
import json
import os
import sys
import time
import traceback

os.environ.setdefault('CUBLAS_WORKSPACE_CONFIG', ':4096:8')
import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F

ROOT=Path(__file__).resolve().parents[2]
CODE=Path(__file__).resolve().parent
OUT=ROOT/'outputs/joint-associated-post-classifier-20261016/run-01'
DOC=ROOT/'docs/joint-associated-post-classifier-20261016'
PARENT=ROOT/'outputs/post-input-associated-representation-20261014/run-01'
SOURCE=PARENT.parent/'run-02'
PREP=ROOT/'outputs/calibrated-deployment-business-transfer-20261006/run-01'
PLAN=ROOT/'plan/JAT1-joint-associated-post-classifier-plan-20261016.md'
PROTOCOLS=['shadowsocks','vless','trojan','vmess']
SEEDS=[20261014,20261015,20261016]
SOURCE_SEED=SEEDS[0]
KEYS=['a0','d0','a1','d1','W','V','c']
GKEYS=KEYS[:4]
HKEYS=KEYS[4:]
MASKS={'G0':[2,4],'G1':[0,3],'G2':[1,5]}
READS=[]
_CONTRACT=None
_HASH_CACHE={}

RECIPES=[dict(id=f'C{i+1:02}',lam=lv,lr=lr,gamma=ga)
         for i,(lv,lr,ga) in enumerate([(v,lr,ga) for lr,ga in [(.001,.001),(.0003,.0001)] for v in [0.,.1,1.]])]
POST_RECIPES=[dict(id=f'JC{i+1:02}',lam=0.,lr=lr,gamma=ga)
              for i,(lr,ga) in enumerate((lr,ga) for lr in [.0003,.001] for ga in [.0001,.001,.01])]

def require(ok,message):
    if not bool(ok):raise RuntimeError(message)

def read(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def rel(path):return Path(path).resolve().relative_to(ROOT).as_posix()
def sha(path):
    path=Path(path);require(path.suffix.lower() not in {'.pcap','.pcapng','.cap'},'PCAP forbidden')
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()

def writable(path):
    p=Path(path).resolve();require(p.is_relative_to(OUT) or p.is_relative_to(DOC),'Write outside JAT1')
    p.parent.mkdir(parents=True,exist_ok=True);return p

def scalar(v):
    if isinstance(v,np.generic):return v.item()
    if isinstance(v,Path):return str(v)
    raise TypeError(type(v).__name__)

def write(path,value):
    p=writable(path);tmp=p.with_name(p.name+'.tmp')
    tmp.write_text(json.dumps(value,ensure_ascii=False,indent=2,sort_keys=True,allow_nan=False,default=scalar)+'\n',encoding='utf-8')
    os.replace(tmp,p)

def immutable(path,value):
    require(not Path(path).exists(),'Refuse to replace accepted record');write(path,value)

def put(path,value,**meta):
    p=writable(path);require(not p.exists(),'Refuse tensor overwrite')
    torch.save(value,p);immutable(p.with_suffix('.json'),dict(sha256=sha(p),**meta))

def own(path):
    p=Path(path);require(sha(p)==read(p.with_suffix('.json'))['sha256'],'Own tensor changed')
    return torch.load(p,map_location='cuda:0',weights_only=True)

def configure():
    require(torch.cuda.is_available(),'CUDA mandatory; no CPU training fallback')
    torch.set_num_threads(1);torch.use_deterministic_algorithms(True)
    torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False

def tensor(x,dtype=torch.float64):return torch.as_tensor(np.asarray(x),device='cuda:0',dtype=dtype)
def cpu(x):return x.detach().cpu().numpy()

def contract():
    global _CONTRACT
    if _CONTRACT is None:
        p=OUT/'manifests/contract.json';require(sha(p)==read(OUT/'manifests/contract-seal.json')['sha256'],'Contract changed')
        _CONTRACT=read(p)
    return _CONTRACT

def asset(path,rid,kind):
    path=Path(path);info=contract()['files'].get(rel(path))
    require(info is not None and info.get('role_id')==rid and info['kind']==kind,'Unregistered/cross-role input')
    require(kind in {'classification','base','target-P','target-G','teacher','teacher-fit','groups'},'Engineering numeric reader forbids query/labels')
    sig=(path.stat().st_size,path.stat().st_mtime_ns)
    if _HASH_CACHE.get(rel(path))!=(sig,info['sha256']):
        require(sha(path)==info['sha256'],'Input hash mismatch');_HASH_CACHE[rel(path)]=(sig,info['sha256'])
    READS.append(dict(path=rel(path),role_id=rid,kind=kind,sha256=info['sha256']))
    return torch.load(path,map_location='cuda:0',weights_only=True)

def progress(stage,**kw):
    write(OUT/'progress.json',dict(stage=stage,unix=time.time(),**kw));print(stage,kw,flush=True)

def code_snapshot(tag):
    dst=OUT/'engineering'/tag/'code';require(not dst.exists(),'Engineering tag already exists')
    hashes={}
    for p in sorted(CODE.glob('*.py')):
        h=sha(p);q=writable(dst/p.name);q.write_bytes(p.read_bytes());hashes[rel(p)]=h
    immutable(dst.parent/'code-seal.json',dict(files=hashes,plan_sha256=sha(PLAN)))
    return hashes

@contextlib.contextmanager
def engineering(tag):
    configure();READS.clear();hashes=code_snapshot(tag);started=time.perf_counter()
    progress(tag+'_started')
    try:
        yield OUT/'engineering'/tag
    except BaseException as exc:
        immutable(OUT/'engineering'/tag/'failure.json',dict(error=repr(exc),traceback=traceback.format_exc(),no_auto_retry=True))
        progress(tag+'_stopped',reason=str(exc));raise
    finally:
        for p,h in hashes.items():require(sha(ROOT/p)==h,'Code changed during engineering run')
        immutable(OUT/'engineering'/tag/'io-ledger.json',dict(reads=READS,seconds=time.perf_counter()-started,
                  query_reads=0,H_reads=0,U_training_reads=0,PCAP_reads=0,science_matrix_started=False))
