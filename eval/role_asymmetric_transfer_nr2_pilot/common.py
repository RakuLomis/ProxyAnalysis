"""NR2 isolated train-only IO, provenance and bounded activity clock."""
from pathlib import Path
import os
os.environ.setdefault('CUBLAS_WORKSPACE_CONFIG', ':4096:8')
import ast
import collections
import hashlib
import inspect
import json
import textwrap
import time
import types
import traceback
import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'outputs/role-asymmetric-transfer-v1-20261017'
OLD=BASE/'run-01'; FULL=BASE/'full-nr1-01'; NR=BASE/'numeric-pilot-nr1'
BOOT=BASE/'numeric-pilot-nr2'
OUT=BASE/'numeric-pilot-nr2-02'
DOC=ROOT/'docs/role-asymmetric-transfer-v1-20261017/nr2-run02'
PLAN=ROOT/'plan/RA1-NR2-same-objective-second-order-pilot-plan-20261018.md'
DESIGN=ROOT/'plan/RA1-NR2-fixed-pilot-design-20261018.json'
CODE=Path(__file__).parent
LEGACY=ROOT/'eval/role_asymmetric_transfer_v1'
SOLVER='cholesky-original-gradient-aware-lbfgs-v4'
POLICY=dict(max_iter=4000,max_eval=20000)
START=None; PRIOR=None; PILOT_PRIOR=0.; READS=[]; CONTRACT=None; ATTEMPTS=[]

class BudgetStop(RuntimeError): pass
def require(ok,msg):
    if not bool(ok): raise RuntimeError(msg)
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def rel(p): return Path(p).resolve().relative_to(ROOT).as_posix()
def pathout(p):
    p=Path(p).resolve();require(p.is_relative_to(OUT) or p.is_relative_to(DOC),'Write outside NR2 roots')
    p.parent.mkdir(parents=True,exist_ok=True);return p
def write(p,v):
    p=pathout(p);tmp=p.with_name(p.name+'.tmp')
    tmp.write_text(json.dumps(v,ensure_ascii=False,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf-8');os.replace(tmp,p)
def save(p,v):
    p=pathout(p);require(not p.exists(),'No artifact overwrite');torch.save(v,p)
    write(p.with_suffix('.json'),dict(sha256=sha(p)))
def dev():
    require(torch.cuda.is_available(),'CUDA required');return torch.device('cuda:0')
def cuda(*args):
    for a in args:
        require(a.is_cuda,'CPU numeric input prohibited')
        if a.is_floating_point(): require(a.dtype==torch.float64,'float64 required')
def finite(*args):
    for a in args: require(torch.isfinite(a).all(),'Nonfinite numerical input')
def guard():
    if START is not None:
        elapsed=time.perf_counter()-START
        if PILOT_PRIOR+elapsed>=1740 or (PRIOR or 0.)+elapsed>=28740:raise BudgetStop('Activity safety limit; 60s reserved for closeout')
def progress(stage,**kw):
    guard();d=dict(stage=stage,time_unix=time.time(),pid=os.getpid(),pilot_seconds=time.perf_counter()-START,**kw)
    d['pilot_total_seconds']=PILOT_PRIOR+d['pilot_seconds'];write(OUT/'progress.json',d);print(stage,kw,flush=True)
def initialize_costs():
    global PRIOR,PILOT_PRIOR
    PILOT_PRIOR=read(BOOT/'cost-final.json')['pilot_activity_seconds']
    PRIOR=read(FULL/'cost-final.json')['cumulative_active_seconds']+read(BASE/'full-nr1-closeout-20261018/stop-analysis.json')['additional_readonly_analysis_seconds']+60.+PILOT_PRIOR
def acceptance_gates(value,initial,gradient,iterations,error,gradient_error):
    return dict(objective_nonincrease=bool(value<=initial+1e-10),original_coordinate_gradient=bool(gradient<=1e-5),
                iteration_budget=bool(iterations<4000),objective_replay=bool(error<1e-10),gradient_replay=bool(gradient_error<1e-10))
def configure():
    dev();torch.set_num_threads(1);torch.use_deterministic_algorithms(True)
    torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False;torch.cuda.reset_peak_memory_stats()
def checked(p,purpose):
    p=Path(p).resolve();k=rel(p);require(CONTRACT is not None and k in CONTRACT['protected'],'Unregistered read '+k)
    require(sha(p)==CONTRACT['protected'][k],'Source checksum mismatch '+k)
    READS.append(dict(path=k,purpose=purpose,sha256=CONTRACT['protected'][k]));return p
def load(p,purpose='train-artifact'):
    return torch.load(checked(p,purpose),map_location=dev(),weights_only=True)
def parents():
    c=read(FULL/'manifests/contract.json')
    require(sha(FULL/'manifests/contract.json')==read(FULL/'manifests/seal.json')['sha256'],'Parent seal')
    return c
def fingerprint(s):
    out={}
    for k in sorted(s):
        a=s[k].detach().cpu().contiguous()
        out[k]=dict(shape=list(a.shape),dtype=str(a.dtype),sha256=hashlib.sha256(a.numpy().tobytes()).hexdigest())
    return out
def build_slot(v,p,missing):
    # Exact original slot implementation injected into a train-only namespace.
    tree=ast.parse((ROOT/'eval/role_asymmetric_transfer_nr1_full/weight_schedule.py').read_text())
    tree.body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['registry','selection','slot']]
    ns=dict(require=require,torch=torch,tensor=lambda z,dtype=torch.float64:torch.as_tensor(z,device=dev(),dtype=dtype),
            weighted=lambda y,m,n:F.one_hot(y,n).double().T@m)
    exec(compile(ast.fix_missing_locations(tree),'<sealed-original-weight-slots>','exec'),ns)
    policy={r['id']:r for r in ns['registry']()}[p]
    return ns['slot'](v,policy,missing)
def getslot(case):
    role={r['id']:r for r in CONTRACT['roles']}[case['role_id']]
    v=load(OLD/'packages'/role['id']/'training.pt')
    s=build_slot(v,case['policy_id'],role['missing']);cuda(s['x'],s['mass']);finite(s['x'],s['mass'])
    require(abs(float(s['mass'].sum())-1)<1e-12,'Total mass')
    require(float((F.one_hot(s['y'],6).double().T@s['mass']-1/6).abs().max())<1e-12,'Class mass')
    require((s['mass']>0).all(),'Positive row mass')
    return s,role
def begin(kind,case):
    guard();require(len(ATTEMPTS)<58,'58-attempt cap')
    a=dict(index=len(ATTEMPTS)+1,kind=kind,**case,started_unix=time.time(),status='running')
    ATTEMPTS.append(a);write(OUT/'attempts'/f"{a['index']:03d}.json",a);return a
def end(a,**kw):
    a.update(**kw);write(OUT/'attempts'/f"{a['index']:03d}.json",a)

def register():
    global CONTRACT,PRIOR
    design=read(DESIGN);parent=parents();roles={r['id']:r for r in parent['roles']};policies={p['id'] for p in parent['policies']}
    cases=[]
    for g in design['case_groups']:
        row=[dict(role_id=r,policy_id=s+'__'+p,group=g['id']) for r in g['roles'] for s in g['source_values'] for p in g['policy_suffixes']]
        require(len(row)==g['cartesian_product_count'],'Group count');cases.extend(row)
    keys={(x['role_id'],x['policy_id']) for x in cases};require(len(cases)==len(keys)==52,'52 unique cases')
    require(all(x['role_id'] in roles and x['policy_id'] in policies for x in cases),'Case identity')
    adopted=pd.read_parquet(FULL/'manifests/adopted-endpoints.parquet').replace({np.nan:None}).to_dict('records')
    new=[read(p) for p in (FULL/'new-endpoints').rglob('*.json')]
    endpoints=adopted+new;require(len(endpoints)==1024,'Protected endpoint count')
    protected={}
    def protect(p,expected=None):
        guard();p=Path(p);h=sha(p);require(expected is None or h==expected,'Parent hash differs '+rel(p));protected[rel(p)]=h
    for p in [PLAN,DESIGN,FULL/'failure.json',FULL/'cost-final.json',FULL/'run-closeout.json',FULL/'manifests/contract.json',FULL/'manifests/seal.json',
              FULL/'manifests/numeric-policy.json',OLD/'failure.json',OLD/'cost-ledger.json',NR/'completion.json',NR/'verification.json',
              FULL/'manifests/adopted-endpoints.parquet']:
        protect(p)
    for d in [LEGACY,ROOT/'eval/role_asymmetric_transfer_nr1_full',ROOT/'eval/role_asymmetric_transfer_numeric_pilot_v1']:
        for p in d.glob('*.py'):protect(p,parent['fixed'].get(rel(p),parent['code'].get(rel(p))))
    for run in [OLD,FULL]:protect(run/'manifests/numeric-policy.json')
    for p in [BOOT/'failure.json',BOOT/'cost-final.json']:protect(p)
    for role in parent['roles']:
        p=OLD/'packages'/role['id']/'training.pt'
        protect(p,parent['artifacts'][rel(p)]);protect(p.with_suffix('.json'),parent['fixed'][rel(p.with_suffix('.json'))])
    for e in endpoints:
        p=ROOT/e['path'];protect(p,e['sha256']);protect(p.with_suffix('.json'))
        meta=read(p.with_suffix('.json'))
        source_policy=(p.parent/'manifests/numeric-policy.json') if e['source']=='NR1-pilot' else ((FULL if e['source']=='NR1-full-new' else OLD)/'manifests/numeric-policy.json')
        protect(source_policy,meta['optimizer']['numeric_policy_sha256'])
        if e.get('slot_path'):
            sp=ROOT/e['slot_path'];protect(sp);protect(sp.with_suffix('.json'))
    for e in design['snapshot_diagnostics']:
        p=ROOT/e['failure_json'];protect(p);protect(p.with_suffix('.pt'));f=read(p);require(not f['accepted'],'Old failure changed')
        run=FULL if e['id']=='D-new' else OLD
        sp=run/'numeric-slots'/f['role_id']/(f['arm']+'.pt');protect(sp,f['input_sha256'])
        e['slot_path']=rel(sp)
    analysis=BASE/'full-nr1-closeout-20261018/stop-analysis.json'
    protect(analysis)
    prior=read(FULL/'cost-final.json')['cumulative_active_seconds']
    added=read(analysis)['additional_readonly_analysis_seconds']
    # Explicit conservative accounting, not a fabricated wall-time measurement.
    PRIOR=prior+added+60.+PILOT_PRIOR
    CONTRACT=dict(version='RA1-NR2-second-order-pilot',authorization='User authorized NR2, 1800s activity cap, no full restart',
        roles=parent['roles'],cases=cases,design=design,protected=protected,endpoints=endpoints,
        code={rel(p):sha(p) for p in CODE.glob('*.py')},
        cost_basis=dict(parent_last_recorded_seconds=prior,recorded_subsequent_analysis_seconds=added,
                        conservative_unmetered_analysis_charge_seconds=60.,charge_not_measurement=True,
                        earlier_NR2_registration_stop_seconds=PILOT_PRIOR,prior_charged_seconds=PRIOR),
        environment=dict(python=os.sys.version,torch=str(torch.__version__),numpy=str(np.__version__),cuda=torch.version.cuda,
                         gpu=torch.cuda.get_device_name(),installed_LBFGS_sha256=sha(Path(inspect.getfile(torch.optim.LBFGS)))),
        full_matrix_auto_start=False,original_objective_unchanged=True,original_precision_gates_unchanged=True,solver_algorithm_changed=True)
    write(OUT/'manifests/contract.json',CONTRACT);write(OUT/'manifests/seal.json',dict(sha256=sha(OUT/'manifests/contract.json')))
    READS.extend(dict(path=p,purpose='registration-provenance',sha256=h) for p,h in protected.items())
    # Exact pre-existing slot replay for available pilot cases.
    available={(e['role_id'],e['policy_id']):e for e in endpoints};slot_audits=[]
    for case in cases:
        s,r=getslot(case);old=available.get((case['role_id'],case['policy_id']))
        if old and old.get('slot_path'):
            ss=load(ROOT/old['slot_path']);require(all(torch.equal(s[k],ss[k]) for k in s),'Existing slot differs')
        key=case['role_id']+'/'+case['policy_id'];p=OUT/'slots'/key
        save(p.with_suffix('.pt'),s)
        slot_audits.append(dict(**case,existing_slot_replayed=bool(old and old.get('slot_path')),fingerprint=fingerprint(s)))
    write(OUT/'audits/input-fingerprints.json',slot_audits)
    progress('P0_registered',unique_cases=52,protected_existing_endpoints=1024)

def pilot_slot(case):
    key=case['role_id']+'/'+case['policy_id'];p=OUT/'slots'/key
    meta=read(p.with_suffix('.json'));require(sha(p.with_suffix('.pt'))==meta['sha256'],'New slot checksum')
    READS.append(dict(path=rel(p.with_suffix('.pt')),purpose='pilot-training-slot',sha256=meta['sha256']))
    return torch.load(p.with_suffix('.pt'),map_location=dev(),weights_only=True)
