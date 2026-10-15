"""Independent intervention IO boundary; all historical runs are read-only."""
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
OUT = ROOT/'outputs/strongpost-training-intervention-20261009/run-01'
DOC = ROOT/'docs/strongpost-training-intervention'
PLAN = ROOT/'plan/strongpost-auxiliary-view-training-intervention-plan-20261009.md'
JA = ROOT/'outputs/joint-affine-transfer-20261007/run-01'
V4 = ROOT/'outputs/calibrated-deployment-business-transfer-20261006/run-04'

def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

base = module('ti_frozen_definitions', ROOT/'eval/calibrated_deployment_transfer/common.py')
for name in ['PROTOCOLS','LABELS','FEATURES','HIST','MASKS','TS','require','read','sha','rel',
             'device','configure','tensor','truths','block','size','bins','weighted','scaler',
             'predict','metrics','objective']:
    globals()[name] = getattr(base, name)
PREP = base.OUT
policy = module('ti_frozen_policy',ROOT/'eval/calibrated_deployment_transfer_v4/numeric_policy.py')
POLICY, SOLVER, acceptance_gates = policy.POLICY, policy.SOLVER, policy.acceptance_gates
ARMS = ['S','P-small','G-small','P-full','G-full']
ACCESS = []
_CONTRACT = None
_CHECKED = {}

def writable(path):
    p=Path(path).resolve()
    require(p.is_relative_to(OUT) or p.is_relative_to(DOC), 'TI write outside new roots')
    return p

def write(path, value):
    p=writable(path);p.parent.mkdir(parents=True,exist_ok=True)
    tmp=p.with_name(p.name+'.tmp')
    tmp.write_text(json.dumps(value,ensure_ascii=False,indent=2,sort_keys=True,
                             allow_nan=False,default=base.json_scalar)+'\n',encoding='utf-8')
    os.replace(tmp,p)

def textfile(path, value):
    p=writable(path);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(value,encoding='utf-8')

def save(df,path):
    p=writable(path);p.parent.mkdir(parents=True,exist_ok=True)
    tmp=p.with_name(p.name+'.tmp');df.to_parquet(tmp,index=False);os.replace(tmp,p)

def put(obj,path,**meta):
    p=writable(path);require(not p.with_suffix('.json').exists(),'Accepted artifact already exists')
    p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_name(p.name+'.tmp')
    torch.save(obj,tmp);os.replace(tmp,p);write(p.with_suffix('.json'),{'sha256':sha(p),**meta})

def checked(path, expected, purpose):
    p=Path(path);stat=p.stat();sig=(stat.st_size,stat.st_mtime_ns)
    if _CHECKED.get(str(p))!=(sig,expected):
        require(sha(p)==expected,'Changed sealed input: '+rel(p));_CHECKED[str(p)]=(sig,expected)
    ACCESS.append({'path':rel(p),'sha256':expected,'purpose':purpose})

def contract():
    global _CONTRACT
    if _CONTRACT is None:
        p=OUT/'manifests/experiment-contract.json'
        require(sha(p)==read(p.with_name('seal.json'))['contract_sha256'],'TI contract changed')
        _CONTRACT=read(p)
    return _CONTRACT

def artifact(path):
    p=Path(path);c=contract()
    if not p.is_relative_to(OUT):
        require(rel(p) in c['artifacts'],'Unregistered historical artifact')
        checked(p,c['artifacts'][rel(p)],'artifact')
        checked(p.with_suffix('.json'),c['fixed_files'][rel(p.with_suffix('.json'))],'artifact-metadata')
    info=read(p.with_suffix('.json'));checked(p,info['sha256'],'artifact')
    if info.get('optimizer'):
        log=info['optimizer']
        require(log['solver']==SOLVER and log['accepted'],'Unaccepted historical classifier')
        require(all(acceptance_gates(log['objective'],log['initial_objective'],log['max_gradient'],
                    log['iterations'],log['objective_replay_error'],log['gradient_replay_error']).values()),
                    'Classifier precision gate')
        require(log['settings']['max_iter']==2000 and log['settings']['max_eval']==10000,'Classifier budget')
        require(log['numeric_policy_sha256']==sha(OUT/'manifests/numeric-policy.json'),'Policy mismatch')
    return torch.load(p,map_location=device(),weights_only=True)

def group_schema(d):
    require(set(d)=={'content_token','fit_mass',*HIST},'Group identity/schema leak')

def permission(kind,purpose):
    allowed={'train':{'source-post','source-pre','C-post'},'paired-map':{'JA-C-paired'},
             'group-map':{'JA-C-group'},'pilot-query':{'main-query'},'query':{'main-query'},
             'pilot-labels':{'main-inner-labels'},'score':{'main-outer-labels'}}
    require(purpose in allowed and kind in allowed[purpose],'Illegal package permission')

def validate_scope(d,info):
    kind=info['kind'];s=info['scope']
    if kind in ['source-post','source-pre']:
        require(set(d.content_id)<=set(s['train_contents']),'Heldout content in training')
        require(set(d.protocol)<=set(s['sources']),'Forbidden source deployment')
        if kind=='source-pre':require('visit_id' not in d and 'session_id' not in d,'Source pre identity')
    elif kind=='C-post':
        require(set(d.content_id)<=set(s['C_contents']),'Target U in C')
        require(set(d.protocol)=={s['calibration']},'Wrong calibration deployment')
    elif kind in ['JA-C-paired','JA-C-group']:
        tokens={hashlib.sha256(('ja-content:'+str(u)).encode()).hexdigest() for u in s['C_contents']}
        require(set(d.content_token)==tokens,'C content scope')
        require(abs(float(d.fit_mass.sum())-1)<1e-12 and (d.fit_mass>0).all(),'C mass')
        if kind=='JA-C-group':group_schema(d)
        else:require(set(d)=={'visit_id','content_token','fit_mass',*['pre_'+h for h in HIST],
                           *['post_'+h for h in HIST]} and d.visit_id.is_unique,'Paired schema')
    elif kind in ['main-inner-labels','main-outer-labels']:
        require(set(d.content_id)<=set(s['validation_contents']),'Label content scope')
    elif kind=='main-query':base.validate_query(d)

def package(path,purpose):
    p=Path(path);c=contract();info=c['packages'][rel(p)];permission(info['kind'],purpose)
    if purpose=='pilot-labels':
        seal=OUT/'pilot/predictions-complete.json'
        require(seal.exists(),'Seal ALL pilot predictions before labels')
        checked(OUT/'pilot/predictions.parquet',read(seal)['sha256'],'pilot-predictions')
    if purpose=='score':
        seal=OUT/'predictions/complete.json'
        require(seal.exists(),'Seal ALL formal predictions before target labels')
        checked(OUT/'predictions/visits.parquet',read(seal)['sha256'],'formal-predictions')
    checked(p,info['sha256'],purpose);d=pd.read_parquet(p)
    require(list(d)==info['columns'],'Package schema changed');validate_scope(d,info)
    is_inner=info['scope'].get('inner') is not None
    # Package scope is authenticated by the registered role rather than optional scope field.
    if purpose in ['pilot-query','pilot-labels']:
        require(rel(p) in c['pilot_packages'],'Actual target query/labels forbidden in pilot')
    if purpose in ['query','score']:
        require(rel(p) in c['outer_packages'],'Pseudo-target mistaken for outer test')
    return d

def rolepath(r):return PREP/'packages'/r['id']
def oldmap(r,arm,eta):return JA/'maps'/r['id']/f'{arm}-eta{eta:g}.pt'
def oldslot(r,arm,eta):return JA/'slots'/r['id']/f'{arm}-eta{eta:g}.pt'
def oldmodel(r,arm,eta,t):return JA/'models'/r['id']/f'{arm}-eta{eta:g}-t{t:g}.pt'
def basemodel(r):return V4/'models'/r['id']/f'CT2-t{r["t"]:g}.pt'
def viewpath(r):return OUT/'slots'/r['id']/'views.pt'
def solver():return module('ti_sealed_v4_optimizer',ROOT/'eval/calibrated_deployment_transfer_v4/optimizer_preconditioning.py')
def affine():return module('ti_sealed_affine',ROOT/'eval/joint_affine_transfer/affine.py')
def weights():return module('ti_sealed_weight_function',ROOT/'eval/calibrated_deployment_transfer/representation.py')

def progress(stage,**details):
    write(OUT/'progress.json',{'stage':stage,'time_unix':time.time(),**details});print(stage,details,flush=True)

def start(stage):
    configure();ACCESS.clear();c=contract()
    checked(PLAN,c['plan_sha256'],'plan')
    for p,h in {**c['source_sha256'],**c['historical_source_sha256']}.items():checked(ROOT/p,h,'source')
    for p,h in c['fixed_files'].items():checked(ROOT/p,h,'lineage')
    require(read(OUT/'manifests/numeric-policy.json')==POLICY,'Numeric policy changed')
    e=c['environment'];require(sha(Path(e['installed_LBFGS_path']))==e['installed_LBFGS_sha256'],'Installed solver changed')
    return c

@contextlib.contextmanager
def stage(name):
    start(name);marker=OUT/'stages'/f'{name}.json';require(not marker.exists(),'Stage already completed')
    started=time.time();lock=OUT/'stage.lock';lock.parent.mkdir(parents=True,exist_ok=True)
    fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY);os.write(fd,str(os.getpid()).encode());os.close(fd)
    try:
        progress(name+'_running',pid=os.getpid());yield
        write(marker,{'passed':True,'seconds':time.time()-started,'time_unix':time.time(),
                     'script':rel(Path(sys.argv[0])),'reads':ACCESS})
        progress(name+'_complete',seconds=time.time()-started)
    except BaseException as exc:
        write(OUT/'failure.json',{'stage':name,'exception':str(exc),'type':type(exc).__name__,
                                'time_unix':time.time(),'automatic_retry':False});raise
    finally:
        if lock.exists() and lock.read_text()==str(os.getpid()):lock.unlink()

def residual(a,b):return float((a-b).abs().max())/max(1.,float(a.abs().max()),float(b.abs().max()))
