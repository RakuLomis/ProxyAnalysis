"""CJ cache-only contracts and CUDA arithmetic; historical runs remain immutable."""
from pathlib import Path
import contextlib
import hashlib
import importlib.util
import inspect
import json
import os
import sys
import time
os.environ.setdefault('CUBLAS_WORKSPACE_CONFIG', ':4096:8')
import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'outputs/connection-joint-response-20261010/run-01'
DOC = ROOT/'docs/connection-joint-response'
PLAN = ROOT/'plan/connection-joint-response-business-plan-20261010.md'
PARENT = ROOT/'outputs/small-view-attribution-20261010/run-02'
NATIVE = ROOT/'outputs/protocol-probability-drift-20261004/run-01/features/paired-flow-features.parquet'
FOLDS = NATIVE.parents[1]/'cohorts/folds.parquet'
AUDIT = ROOT/'outputs/mihomo-protocol-audit-20261003'

def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

base = module('cj_frozen_definitions', ROOT/'eval/calibrated_deployment_transfer/common.py')
for name in ['PROTOCOLS','LABELS','FEATURES','HIST','MASKS','TS','require','read','rel','device',
             'configure','tensor','truths','scaler','weighted','metrics']:
    globals()[name] = getattr(base, name)
numeric = module('cj_frozen_numeric', ROOT/'eval/calibrated_deployment_transfer_v4/numeric_policy.py')
POLICY, SOLVER, acceptance_gates = numeric.POLICY, numeric.SOLVER, numeric.acceptance_gates
SIZES = [17,17,16,16]
NAMES = ['UE_up','UE_down','U_unique_runs','U_packet_runs']
JOINT = [f'j{g}_{b:02d}' for g,k in enumerate(SIZES) for b in range(k)]
INPUTS = {'M':HIST, 'I':HIST+JOINT, 'J':HIST+JOINT}
ARMS = ['M-S','I-S','J-S','J-P-small','J-G-small','J-RawPre-small','J-RawPost-small','J-Marginal-small']
COMPARISONS = [('J-S','M-S'),('J-S','I-S'),('J-P-small','J-S'),
               ('J-P-small','J-G-small'),('J-P-small','J-RawPre-small')]
ACCESS = []
_HASH = {}

def sha(p):
    p = Path(p)
    require(p.suffix.lower() not in {'.pcap','.pcapng','.cap'}, 'Raw captures forbidden')
    sig = (p.stat().st_size,p.stat().st_mtime_ns)
    if str(p) not in _HASH or _HASH[str(p)][0] != sig:
        h = hashlib.sha256()
        with p.open('rb') as s:
            for b in iter(lambda:s.read(1024*1024),b''): h.update(b)
        _HASH[str(p)] = (sig,h.hexdigest())
    return _HASH[str(p)][1]

def writable(p):
    p = Path(p).resolve()
    require(p.is_relative_to(OUT) or p.is_relative_to(DOC), 'CJ write outside new roots')
    return p

def write(p, value):
    p = writable(p); p.parent.mkdir(parents=True,exist_ok=True)
    tmp = p.with_name(p.name+'.tmp')
    tmp.write_text(json.dumps(value,ensure_ascii=False,indent=2,sort_keys=True,
        allow_nan=False,default=base.json_scalar)+'\n',encoding='utf-8'); os.replace(tmp,p)

def textfile(p, value):
    p = writable(p); p.parent.mkdir(parents=True,exist_ok=True); p.write_text(value,encoding='utf-8')

def save(d,p):
    p = writable(p); p.parent.mkdir(parents=True,exist_ok=True)
    tmp = p.with_name(p.name+'.tmp'); d.to_parquet(tmp,index=False); os.replace(tmp,p)

def put(obj,p,**meta):
    p = writable(p); require(not p.with_suffix('.json').exists(),'Accepted artifact exists')
    p.parent.mkdir(parents=True,exist_ok=True); tmp=p.with_name(p.name+'.tmp')
    torch.save(obj,tmp); os.replace(tmp,p); write(p.with_suffix('.json'),{'sha256':sha(p),**meta})

def checked(p, expected, purpose):
    require(sha(p)==expected,'Changed sealed input '+str(p))
    ACCESS.append({'path':rel(p),'sha256':expected,'purpose':purpose})

def contract():
    p=OUT/'manifests/experiment-contract.json'
    require(sha(p)==read(p.with_name('seal.json'))['contract_sha256'],'Contract seal')
    return read(p)

def preparations():
    p=OUT/'manifests/preparation.json'
    require(sha(p)==read(p.with_name('preparation-seal.json'))['sha256'],'Preparation seal')
    return read(p)

def package(p,purpose):
    p=Path(p); info=preparations()['packages'][rel(p)]
    allow={'train':{'source-pre','source-post','C-post'}, 'paired-map':{'C-paired'},
           'group-map':{'C-group'}, 'marginal-map':{'C-marginal'}, 'query':{'query'},
           'select':{'inner-query'}, 'score':{'labels'}, 'diag-fit':{'diag-paired'},
           'diag-group':{'diag-group'}, 'diag-query':{'diag-query'}, 'diag-score':{'diag-score'}}
    require(info['kind'] in allow.get(purpose,set()),'Forbidden package purpose '+purpose)
    if purpose=='score':require((OUT/'predictions/complete.json').exists(),'ALL predictions must be sealed first')
    if purpose=='diag-score':require((OUT/'diagnostics/predictions/complete.json').exists(),'ALL diagnostic predictions first')
    checked(p,info['sha256'],purpose); d=pd.read_parquet(p)
    require(list(d)==info['columns'] and len(d)==info['rows'],'Changed package schema/count')
    return d

def artifact(p):
    p=Path(p)
    if not p.resolve().is_relative_to(OUT):
        require(rel(p) in contract()['artifacts'],'Unregistered historical artifact')
        checked(p,contract()['artifacts'][rel(p)],'historical-artifact')
    info=read(p.with_suffix('.json')); checked(p,info['sha256'],'artifact')
    return torch.load(p,map_location=device(),weights_only=True)

def progress(stage,**details):
    write(OUT/'progress.json',{'stage':stage,'time_unix':time.time(),**details})
    print(stage,details,flush=True)

@contextlib.contextmanager
def stage(name):
    configure(); ACCESS.clear(); c=contract()
    checked(PLAN,c['plan_sha256'],'approved-plan')
    for p,h in {**c['source_sha256'],**c['historical_source_sha256'],**c['fixed_files']}.items():
        checked(ROOT/p,h,'source-or-lineage')
    require(read(OUT/'manifests/numeric-policy.json')==POLICY,'Numeric policy differs')
    marker=OUT/'stages'/f'{name}.json'; require(not marker.exists(),'Stage already complete')
    lock=OUT/'stage.lock'; fd=os.open(lock,os.O_WRONLY|os.O_CREAT|os.O_EXCL)
    os.write(fd,str(os.getpid()).encode()); os.close(fd); started=time.time()
    try:
        progress(name+'_running',pid=os.getpid()); yield
        write(marker,{'passed':True,'seconds':time.time()-started,'reads':ACCESS})
        progress(name+'_complete',seconds=time.time()-started)
    except BaseException as exc:
        write(OUT/'failures'/f'{name}-{time.time_ns()}.json',{'stage':name,'exception':str(exc),
             'type':type(exc).__name__,'automatic_retry':False}); raise
    finally:
        if lock.exists() and lock.read_text()==str(os.getpid()):lock.unlink()

def token(prefix, value):return hashlib.sha256((prefix+str(value)).encode()).hexdigest()
def rolepath(r):return OUT/'packages'/r['id']
def slice_joint(g):return slice(sum(SIZES[:g]),sum(SIZES[:g+1]))
