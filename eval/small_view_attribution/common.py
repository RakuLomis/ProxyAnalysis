"""Independent SA run; sealed historical files are read-only dependencies."""
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
OUT = ROOT/'outputs/small-view-attribution-20261010/run-02'
DOC = ROOT/'docs/small-view-attribution'
PLAN = ROOT/'plan/small-view-attribution-controls-and-validation-plan-20261010.md'
PARENT = ROOT/'outputs/strongpost-training-intervention-20261009/run-01'
PREP = ROOT/'outputs/calibrated-deployment-business-transfer-20261006/run-01'
V4 = ROOT/'outputs/calibrated-deployment-business-transfer-20261006/run-04'

def module(name, path):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

base=module('sa_frozen_definitions',ROOT/'eval/calibrated_deployment_transfer/common.py')
for name in ['PROTOCOLS','LABELS','FEATURES','HIST','MASKS','TS','require','read','sha','rel',
             'device','configure','tensor','truths','block','size','bins','weighted','scaler',
             'predict','metrics','objective']:
    globals()[name]=getattr(base,name)
policy=module('sa_numeric_policy',ROOT/'eval/calibrated_deployment_transfer_v4/numeric_policy.py')
POLICY,SOLVER,acceptance_gates=policy.POLICY,policy.SOLVER,policy.acceptance_gates
ARMS=['S','P-small','G-small','RawPre-small','RawPost-small','Marginal-small']
NEW_ARMS=ARMS[3:]
COMPARISONS=[('P-small',a) for a in NEW_ARMS]
ACCESS=[]
_CONTRACT=None
_CACHE={}

def writable(p):
    p=Path(p).resolve();require(p.is_relative_to(OUT) or p.is_relative_to(DOC),'Write outside SA roots');return p

def write(p, value):
    p=writable(p);p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_name(p.name+'.tmp')
    tmp.write_text(json.dumps(value,ensure_ascii=False,indent=2,sort_keys=True,allow_nan=False,
                              default=base.json_scalar)+'\n',encoding='utf-8');os.replace(tmp,p)

def textfile(p, value):
    p=writable(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(value,encoding='utf-8')

def save(df,p):
    p=writable(p);p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_name(p.name+'.tmp')
    df.to_parquet(tmp,index=False);os.replace(tmp,p)

def put(obj,p,**details):
    p=writable(p);require(not p.with_suffix('.json').exists(),'Accepted artifact already exists')
    p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_name(p.name+'.tmp');torch.save(obj,tmp);os.replace(tmp,p)
    write(p.with_suffix('.json'),{'sha256':sha(p),**details})

def checked(p,h,purpose):
    p=Path(p);sig=(p.stat().st_size,p.stat().st_mtime_ns)
    label=rel(p) if p.resolve().is_relative_to(ROOT) else str(p.resolve())
    if _CACHE.get(str(p))!=(sig,h):
        require(sha(p)==h,'Changed sealed input '+label);_CACHE[str(p)]=(sig,h)
    ACCESS.append({'path':label,'sha256':h,'purpose':purpose})

def contract():
    global _CONTRACT
    if _CONTRACT is None:
        p=OUT/'manifests/experiment-contract.json'
        require(sha(p)==read(p.with_name('seal.json'))['contract_sha256'],'SA contract seal')
        _CONTRACT=read(p)
    return _CONTRACT

def artifact(p):
    p=Path(p)
    if not p.is_relative_to(OUT):
        expected=contract()['artifacts'].get(rel(p));require(expected is not None,'Unregistered historical artifact')
        checked(p,expected,'artifact');checked(p.with_suffix('.json'),contract()['fixed_files'][rel(p.with_suffix('.json'))],'metadata')
    info=read(p.with_suffix('.json'));checked(p,info['sha256'],'artifact')
    log=info.get('optimizer')
    if log:
        require(log['solver']==SOLVER and log['accepted'],'Unaccepted model')
        require(log['numeric_policy_sha256']==sha(OUT/'manifests/numeric-policy.json'),'Numeric policy differs')
        require(log['settings']['max_iter']==2000 and log['settings']['max_eval']==10000,'Solver budgets differ')
        require(all(acceptance_gates(log['objective'],log['initial_objective'],log['max_gradient'],
            log['iterations'],log['objective_replay_error'],log['gradient_replay_error']).values()),'Model precision gates')
    return torch.load(p,map_location=device(),weights_only=True)

def package(p,purpose):
    p=Path(p);info=contract()['packages'][rel(p)];kind=info['kind'];s=info['scope']
    allow={'train':{'source-pre','source-post','C-post'},'marginal-pack':{'JA-C-group'},
           'query':{'main-query'},'score':{'main-outer-labels'}}
    require(kind in allow.get(purpose,set()),'Illegal package purpose')
    if purpose=='score':
        require((OUT/'predictions/complete.json').exists(),'Seal ALL predictions before labels')
        checked(OUT/'predictions/visits.parquet',read(OUT/'predictions/complete.json')['sha256'],'prediction-seal')
    checked(p,info['sha256'],purpose);d=pd.read_parquet(p)
    require(list(d)==info['columns'] and len(d)==info['rows'],'Schema/count changed')
    if kind in ['source-pre','source-post']:
        require(set(d.content_id)<=set(s['train_contents']) and set(d.protocol)<=set(s['sources']),'Source scope')
        if kind=='source-pre':require('visit_id' not in d and 'session_id' not in d,'Source pre identity')
    elif kind=='C-post':
        require(set(d.content_id)<=set(s['C_contents']) and set(d.protocol)=={s['calibration']},'C scope')
    elif kind=='JA-C-group':
        require(set(d)=={'content_token','fit_mass',*HIST},'Anonymous upstream schema')
        allowed={hashlib.sha256(('ja-content:'+str(u)).encode()).hexdigest() for u in s['C_contents']}
        require(set(d.content_token)==allowed,'C token scope')
        require(abs(float(d.fit_mass.sum())-1)<1e-12 and np.allclose(d.fit_mass,1/64,rtol=0,atol=1e-15),'Unexpected C weights')
    elif kind=='main-query':base.validate_query(d)
    elif kind=='main-outer-labels':require(set(d.content_id)<=set(s['validation_contents']),'Heldout labels scope')
    return d

def rolepath(r):return PREP/'packages'/r['id']
def oldviews(r):return PARENT/'slots'/r['id']/'views.pt'
def basemodel(r):return V4/'models'/r['id']/f'CT2-t{r["t"]:g}.pt'
def newslot(r,a):return OUT/'slots'/r['id']/(a+'.pt')
def newmodel(r,a):return OUT/'models'/r['id']/(a+'.pt')
def anonymous_path(r):return OUT/'packages'/r['id']/'marginal.pt'
def transformpath(r):return OUT/'transforms'/r['id']/'marginal.pt'
def solver():return module('sa_solver',ROOT/'eval/calibrated_deployment_transfer_v4/optimizer_preconditioning.py')

def start(name):
    configure();ACCESS.clear();c=contract();checked(PLAN,c['plan_sha256'],'plan')
    for p,h in {**c['source_sha256'],**c['historical_source_sha256'],**c['fixed_files']}.items():checked(ROOT/p,h,'source-or-lineage')
    require(read(OUT/'manifests/numeric-policy.json')==POLICY,'Changed numeric policy')
    checked(Path(c['environment']['installed_LBFGS_path']),c['environment']['installed_LBFGS_sha256'],'installed-optimizer')
    return c

def progress(name,**details):
    write(OUT/'progress.json',{'stage':name,'time_unix':time.time(),**details});print(name,details,flush=True)

@contextlib.contextmanager
def stage(name):
    start(name);marker=OUT/'stages'/(name+'.json');require(not marker.exists(),'Completed stage')
    lock=OUT/'stage.lock';fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY)
    os.write(fd,str(os.getpid()).encode());os.close(fd);beg=time.time()
    try:
        progress(name+'_running',pid=os.getpid());yield
        write(marker,{'passed':True,'seconds':time.time()-beg,'reads':ACCESS,'time_unix':time.time()})
        progress(name+'_complete',seconds=time.time()-beg)
    except BaseException as exc:
        write(OUT/'failure.json',{'stage':name,'type':type(exc).__name__,'exception':str(exc),
                                 'time_unix':time.time(),'automatic_retry':False});raise
    finally:
        if lock.exists() and lock.read_text()==str(os.getpid()):lock.unlink()

def residual(a,b):return float((a-b).abs().max())/max(1.,float(a.abs().max()),float(b.abs().max()))
