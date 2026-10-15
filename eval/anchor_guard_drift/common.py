"""Stage-one IO boundary. Historical results are immutable dependencies."""
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
import numpy as np
import pandas as pd
import torch

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'outputs/invariant-anchor-guarded-drift-20261012/run-01'
DOC = ROOT/'docs/invariant-anchor-guarded-drift'
PLAN = ROOT/'plan/invariant-anchor-guarded-drift-plan-20261012.md'
TI = ROOT/'outputs/strongpost-training-intervention-20261009/run-01'
SA = ROOT/'outputs/small-view-attribution-20261010/run-02'
CJ = ROOT/'outputs/connection-joint-response-20261010/run-01'
JA = ROOT/'outputs/joint-affine-transfer-20261007/run-01'
PREP = ROOT/'outputs/calibrated-deployment-business-transfer-20261006/run-01'
PROTOCOLS = ['shadowsocks', 'vless', 'trojan', 'vmess']
FEATURES = ['W_up','W_down','U_up','U_down','P_up','P_down','E_up','E_down',
            'FR_packet_runs','R_unique_zero_runs']
SIZES = [9]*4+[10]*6
HIST = [f'h{j:02d}_{b:02d}' for j,n in enumerate(SIZES) for b in range(n)]
RULE = {'variation_min':.10,'epsilon_max':.10,'epsilon_variation_ratio_max':.5,
        'quantile':.90,'fold_coverage_min':.875,'OOF_coverage_min':.90,
        'excess_min':.10,'excess_folds_min':2,'floating_comparison_tolerance':1e-12}
ACCESS = []
_CONTRACT = None
_INDEX = None
_HASH_CACHE = {}

def require(ok, message):
    if not bool(ok): raise RuntimeError(message)

def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def rel(p): return Path(p).resolve().relative_to(ROOT).as_posix()
def sha(p):
    p=Path(p); require(p.suffix.lower() not in {'.pcap','.pcapng','.cap'},'PCAP IO forbidden')
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()
def scalar(v):
    if isinstance(v,np.generic):return v.item()
    if isinstance(v,Path):return str(v)
    raise TypeError(type(v).__name__)
def writable(p):
    p=Path(p).resolve();require(p.is_relative_to(OUT) or p.is_relative_to(DOC),'Unsafe output path')
    p.parent.mkdir(parents=True,exist_ok=True);return p
def write(p,v):
    p=writable(p);q=p.with_name(p.name+'.tmp')
    q.write_text(json.dumps(v,ensure_ascii=False,indent=2,sort_keys=True,allow_nan=False,default=scalar)+'\n',encoding='utf-8')
    os.replace(q,p)
def save(d,p):
    p=writable(p);q=p.with_name(p.name+'.tmp');d.to_parquet(q,index=False);os.replace(q,p)
def textfile(p,s):writable(p).write_text(s,encoding='utf-8')
def checked(p,h,purpose):
    p=Path(p);sig=(p.stat().st_size,p.stat().st_mtime_ns)
    if _HASH_CACHE.get(str(p))!=(sig,h):
        require(sha(p)==h,'Changed sealed file: '+rel(p));_HASH_CACHE[str(p)]=(sig,h)
    ACCESS.append({'path':rel(p),'purpose':purpose,'sha256':h})
def device():
    require(torch.cuda.is_available(),'CUDA required; CPU fallback forbidden');return torch.device('cuda:0')
def configure():
    device();torch.set_num_threads(1);torch.use_deterministic_algorithms(True)
    torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
def tensor(x):return torch.as_tensor(np.asarray(x),device=device(),dtype=torch.float64)
def block(j):return slice(sum(SIZES[:j]),sum(SIZES[:j+1]))
def token(u):return hashlib.sha256(('ja-content:'+str(u)).encode()).hexdigest()
def module(name,p):
    spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def contract():
    global _CONTRACT
    if _CONTRACT is None:
        p=OUT/'manifests/experiment-contract.json'
        require(sha(p)==read(p.with_name('seal.json'))['contract_sha256'],'Contract changed');_CONTRACT=read(p)
    return _CONTRACT
def parent_package(p,purpose):
    c=contract();p=Path(p);info=c['parent_packages'].get(rel(p))
    require(info is not None,'Unregistered parent package')
    require(info['kind'] in {'source-pre','source-post','C-post','JA-C-paired','JA-C-group'},'Forbidden parent data')
    require(purpose=='trusted-C-source-packer','Parent packages unavailable to diagnostic workers')
    checked(p,info['sha256'],purpose);d=pd.read_parquet(p)
    require(list(d)==info['columns'] and len(d)==info['rows'],'Parent schema/count changed');return d
def artifact(p,purpose='artifact'):
    p=Path(p)
    if not p.is_relative_to(OUT):
        c=contract();require(rel(p) in c['artifacts'],'Unregistered historical artifact')
        checked(p,c['artifacts'][rel(p)],purpose);checked(p.with_suffix('.json'),c['fixed_files'][rel(p.with_suffix('.json'))],'metadata')
    info=read(p.with_suffix('.json'));checked(p,info['sha256'],purpose)
    return torch.load(p,map_location=device(),weights_only=True)
def put(v,p,**meta):
    p=writable(p);require(not p.with_suffix('.json').exists(),'Do not overwrite accepted artifact')
    q=p.with_name(p.name+'.tmp');torch.save(v,q);os.replace(q,p)
    write(p.with_suffix('.json'),{'sha256':sha(p),**meta})
def index():
    global _INDEX
    if _INDEX is None:
        p=OUT/'packages/index.json';require(sha(p)==read(p.with_name('complete.json'))['index_sha256'],'Package index changed');_INDEX=read(p)
    return _INDEX
def package(p,purpose):
    p=Path(p);info=index().get(rel(p));require(info is not None,'Unregistered package')
    allowed={'P-fit':{'P-train','P-full'},'G-fit':{'G-pre-train','G-post-train','G-pre-full','G-post-full'},
             'P-query':{'P-query'},'G-query':{'G-query'},'P-score':{'P-score'},'G-score':{'G-score'},
             'source-audit':{'source-pre'}}
    require(info['kind'] in allowed.get(purpose,set()),'Worker permission rejected')
    if purpose in {'P-score','G-score'}:
        seal=OUT/'diagnostics/predictions-complete.json'
        require(seal.exists(),'Seal ALL C forecasts before C score values')
    checked(p,info['sha256'],purpose);d=pd.read_parquet(p)
    require(list(d)==info['columns'] and len(d)==info['rows'],'New package schema/count changed')
    require(set(d.content_token)<=set(info['content_tokens']),'Content token scope leak')
    require(not set(d.columns)&{'label_id','protocol','content_id','visit_id','repetition','pair_id'},'Identity/label field leak')
    if purpose.startswith('G'):
        require(not any('pre_' in k or 'post_' in k for k in d.columns),'Mixed-side group package')
        require(set(d)<=set(['content_token','query_key','fit_mass',*HIST]),'Anonymous group schema')
    return d
def rolepath(r):return OUT/'packages'/r['id']
def progress(s,**v):
    write(OUT/'progress.json',{'stage':s,'time_unix':time.time(),**v});print(s,v,flush=True)
@contextlib.contextmanager
def stage(name):
    configure();ACCESS.clear();c=contract();checked(PLAN,c['plan_sha256'],'plan')
    for p,h in c['source_sha256'].items():checked(ROOT/p,h,'sealed-stage-one-code')
    require(not (OUT/'stages'/f'{name}.json').exists(),'Completed stage cannot be replayed implicitly')
    start=time.perf_counter();progress(name+'_started')
    try:
        yield
        write(OUT/'ledgers'/f'{name}.json',{'reads':ACCESS,'seconds':time.perf_counter()-start})
        write(OUT/'stages'/f'{name}.json',{'passed':True,'seconds':time.perf_counter()-start})
        progress(name+'_complete',seconds=time.perf_counter()-start)
    except Exception as e:
        write(OUT/'failures'/f'{name}.json',{'exception':repr(e),'traceback':traceback.format_exc(),'scientific_policy_unchanged':True})
        progress(name+'_failed',reason=str(e));raise
