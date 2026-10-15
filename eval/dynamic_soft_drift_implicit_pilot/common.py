"""Independent solution-level pilot. All numeric reads are sealed source assets."""
from pathlib import Path
import contextlib
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
SOURCE = ROOT/'outputs/dynamic-soft-drift-calibration-20261012/run-01'
REF = ROOT/'outputs/dynamic-soft-drift-calibration-repair-20261012/run-01'
V2 = ROOT/'outputs/dynamic-soft-drift-inner-v2-20261012/run-01'
OUT = ROOT/'outputs/dynamic-soft-drift-implicit-pilot-20261012/run-01'
DOC = ROOT/'docs/dynamic-soft-drift-calibration/implicit-20261012'
PLAN = ROOT/'plan/dynamic-soft-drift-implicit-solution-pilot-plan-20261012.md'

def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); sys.modules[name] = m
    spec.loader.exec_module(m)
    return m

IO = module('implicit_independent_io', ROOT/'eval/dynamic_soft_drift_calibration_repair/common.py')
IO.OUT = OUT; IO.DOC = DOC
for name in ['require','read','sha','rel','device','configure','tensor','block','size','weighted',
             'HIST','FEATURES','POLICY','SOLVER','acceptance_gates','writable','write','save','put',
             'textfile','progress','checked']:
    globals()[name] = getattr(IO, name)
ACCESS = IO.ACCESS
_C = None

def cuda(*xs):
    for x in xs:
        require(x.is_cuda, 'CUDA required; CPU numerical fallback forbidden')
        if x.is_floating_point(): require(x.dtype == torch.float64, 'float64 required')

def contract():
    global _C
    if _C is None:
        p = OUT/'manifests/contract.json'
        require(sha(p) == read(p.with_name('seal.json'))['contract_sha256'], 'Contract changed')
        _C = read(p)
    return _C

def integrity():
    for p,h in contract()['parent_files'].items(): require(sha(ROOT/p) == h, 'Parent changed '+p)

def start(name):
    configure(); ACCESS.clear(); c = contract()
    checked(PLAN, c['plan_sha256'], 'approved-plan')
    for p,h in {**c['code'], **c['math_code']}.items(): checked(ROOT/p,h,'sealed-code')
    checked(Path(c['environment']['installed_LBFGS_path']),c['environment']['installed_LBFGS_sha256'],'installed-LBFGS')
    integrity()
    return c

@contextlib.contextmanager
def stage(name):
    start(name); marker = OUT/'stages'/f'{name}.json'
    require(not marker.exists(), 'Stage already completed')
    lock = OUT/'stage.lock'; lock.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY)
    os.write(fd,str(os.getpid()).encode()); os.close(fd); began=time.time()
    try:
        progress(name+'_running',pid=os.getpid()); yield
        write(marker,dict(passed=True,seconds=time.time()-began,reads=list(ACCESS)))
        progress(name+'_complete',seconds=time.time()-began)
    except BaseException as exc:
        write(OUT/'failures'/f'{name}-{time.time_ns()}.json',dict(stage=name,type=type(exc).__name__,
              exception=str(exc),reads=list(ACCESS),automatic_retry=False))
        progress(name+'_failed',reason=str(exc)); raise
    finally: lock.unlink(missing_ok=True)

def sealed(path,purpose):
    p=Path(path); require(rel(p) in contract()['parent_files'],'Unregistered parent read')
    checked(p,contract()['parent_files'][rel(p)],purpose)
    return p

def asset(path,arm,purpose):
    p=Path(path); e=contract()['assets'].get(rel(p))
    require(e is not None and e['arm']==arm and arm in ['D-P','D-G'],'Numeric asset permission')
    checked(p,e['sha256'],purpose,arm)
    require(read(p.with_suffix('.json'))['sha256']==e['sha256'],'Sidecar mismatch')
    return torch.load(p,map_location=device(),weights_only=True)

def task(r,arm): return asset(SOURCE/'pilot/tasks'/r['id']/f'{arm}.pt',arm,'source-task')
def reference(r,arm): return asset(REF/'models'/r['id']/f'{arm}.pt',arm,'old-q-one-reference')
def coordinate(r,arm): return asset(V2/'coordinates'/r['id']/f'{arm}.pt',arm,'frozen-training-coordinate')
def own(path):
    p=writable(path); e=read(p.with_suffix('.json'))
    checked(p,e['sha256'],'own-sealed-numeric')
    return torch.load(p,map_location=device(),weights_only=True)

def production():
    a=module('amplitude',ROOT/'eval/dynamic_soft_drift_calibration/amplitude.py')
    u=module('implicit_original_objective',ROOT/'eval/dynamic_soft_drift_calibration/unroll.py')
    o=module('implicit_frozen_oracle',ROOT/'eval/dynamic_soft_drift_calibration_repair/oracle.py')
    rr=module('implicit_frozen_soft',ROOT/'eval/dynamic_soft_drift_calibration/recovery.py')
    return a,u,o,rr

def solver(): return module('implicit_original_v4_solver',ROOT/'eval/calibrated_deployment_transfer_v4/optimizer_preconditioning.py')

def register():
    configure(); require(not (OUT/'manifests/seal.json').exists(),'Already registered')
    vc=read(V2/'manifests/contract.json'); vv=read(V2/'verification.json'); end=read(V2/'completion.json')
    require(end['status']=='stop_inner_quality_not_met' and end['passed'],'Preserve v2 stop')
    require(sha(V2/'verification.json')==end['verification_sha256'],'v2 verification seal')
    parent={**vc['parent_files'],**vc['source_sha256'],**vc['math_source_sha256'],**vv['files']}
    for p in [V2/'completion.json',V2/'verification.json',V2/'manifests/contract.json',
              V2/'manifests/seal.json',ROOT/'docs/dynamic-soft-drift-calibration/inner-v2-20261012/numeric-stop-diagnosis-20261012.md']:
        parent[rel(p)]=sha(p)
    assets={}; reuse=[]
    for r in vc['roles']:
        require(r['inner']==1 and not set(r['train_contents'])&set(r['validation_contents']),'Content scope')
        require(r['target'] not in r['sources']+[r['calibration']],'Target leakage')
        for arm in ['D-P','D-G']:
            for p in [SOURCE/'pilot/tasks'/r['id']/f'{arm}.pt',REF/'models'/r['id']/f'{arm}.pt',V2/'coordinates'/r['id']/f'{arm}.pt']:
                meta=read(p.with_suffix('.json')); require(sha(p)==meta['sha256'],'Numeric asset SHA')
                assets[rel(p)]=dict(sha256=meta['sha256'],arm=arm,role_id=r['id'])
                parent[rel(p)]=meta['sha256']; parent[rel(p.with_suffix('.json'))]=sha(p.with_suffix('.json'))
                if 'optimizer' in meta:
                    require(meta['optimizer']['accepted'],'Rejected parent LR')
                    reuse.append(dict(role_id=r['id'],arm=arm,old_gradient=meta['optimizer']['max_gradient'],old_accepted=True))
    for p,h in parent.items(): require(sha(ROOT/p)==h,'Parent seal changed '+p)
    selection={'shadowsocks':['G0','G2'],'vless':['G1'],'trojan':['G0','G2'],'vmess':['G1']}
    selected=[r for r in vc['roles'] if r['group'] in selection[r['target']]]
    require(len(selected)==6 and len(reuse)==24,'Pre-fixed cohort')
    math={**vc['math_source_sha256']}
    for p in [ROOT/'eval/dynamic_soft_drift_calibration_repair/oracle.py',ROOT/'eval/dynamic_soft_drift_inner_v2/inner.py']:
        math[rel(p)]=sha(p)
    env=dict(python=sys.executable,torch=torch.__version__,cuda=torch.version.cuda,gpu=torch.cuda.get_device_name(0),
             dtype='float64',CPU_fallback=False,installed_LBFGS_path=inspect.getfile(torch.optim.LBFGS),
             installed_LBFGS_sha256=sha(Path(inspect.getfile(torch.optim.LBFGS))))
    c=dict(version='solution-implicit-source-pilot-v1',registered_unix=time.time(),roles=vc['roles'],selected=selected,
           assets=assets,parent_files=parent,math_code=math,code={rel(p):sha(p) for p in Path(__file__).parent.glob('*.py')},
           plan_sha256=sha(PLAN),environment=env,q_one=[1.]*10,q_alt=[.9,1.1]*5,
           h=[1e-4,3e-5],directions=dict(all=[1/np.sqrt(10)]*10,alt=[(-1 if j%2==0 else 1)/np.sqrt(10) for j in range(10)]),
           forward_precision=[1e-8,1e-9],Newton_max=30,Armijo_c1=1e-4,backtrack=.5,backtrack_max=25,
           gates=dict(replay=1e-10,hessian=1e-10,symmetry=1e-12,linear=1e-10,gradient_abs=1e-6,
                      gradient_rel=1e-3,FD_abs=1e-5,FD_rel=1e-3,rounding_floor=1e-12,signal_multiplier=10.),
           caps=dict(new_q_LR=204,refined_q_points=216,old_refinements=12,geometry_positions=72),
           feedback_definition='source-heldout-CE-at-solved-LR',old_unroll_reused_as_qualified=False,
           target_C_U_H_numeric_reads=0,PCAP_reads=0,formal_matrix_authorized=False)
    write(OUT/'manifests/contract.json',c); write(OUT/'manifests/seal.json',dict(contract_sha256=sha(OUT/'manifests/contract.json')))
    write(OUT/'manifests/numeric-policy.json',POLICY); write(OUT/'environment.json',env)
    save(pd.DataFrame(reuse),OUT/'audits/reference-reuse.parquet')
    write(OUT/'ledger.json',dict(new_q_LR_attempted=0,new_q_LR_accepted=0,old_reference_refinements=0,
          q_points_refined=0,precision_endpoints=0,Newton_updates=0,formal_classifier_fits=0,new_mapping_fits=0))
    progress('implicit_pilot_registered',selected_roles=6,old_references=24)

def ledger(**delta):
    p=OUT/'ledger.json'; d=read(p)
    for k,v in delta.items(): d[k]=d.get(k,0)+v
    require(d['new_q_LR_attempted']<=204 and d.get('q_points_attempted',0)<=216,'Pilot budget exceeded')
    write(p,d)
