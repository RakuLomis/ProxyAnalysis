"""P0 only: read frozen source/C artifacts, export optimizer closeout; no fits."""
from pathlib import Path
import argparse
import collections
import hashlib
import json
import math
import os
import sys
import time
import tempfile
import numpy as np
import pandas as pd
import torch

ROOT=Path(__file__).resolve().parents[2]
PILOT=ROOT/'outputs/dynamic-soft-drift-outer-pilot-20261013/run-03'
FORMAL=ROOT/'outputs/dynamic-soft-drift-business-formal-20261012/run-02'
OUT=ROOT/'outputs/dynamic-soft-drift-optimizer-closeout-20261013/run-02'
DOC=ROOT/'docs/dynamic-soft-drift-calibration/qualified-policy-20261013'
PLAN=ROOT/'plan/dynamic-soft-drift-qualified-policy-business-plan-20261013.md'
KINDS={'O-DP':'P','O-TP':'P','O-DG':'G'}
FEATURES=['W_up','W_down','U_up','U_down','P_up','P_down','E_up','E_down','FR_packet_runs','R_unique_zero_runs']
# Exact purpose-based categories fixed BEFORE checking any hash mismatch.
RUNTIME_NAMES={'runner.stdout.log','runner.stderr.log','progress.json','worker-heartbeat.json',
               'supervisor-heartbeat.json','supervisor.json','supervisor-exit.json','scheduled-task-cleanup.json',
               'access-journal.jsonl','stage.lock','pending-trial.json'}
READS={};ALLOWED=set();DIGESTS={};POINTS={};DERIVATIVES={}

def require(ok,msg):
    if not bool(ok):raise RuntimeError(msg)

def rel(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def canonical(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def category(p):return 'runtime-control' if Path(p).name in RUNTIME_NAMES or Path(p).name.endswith('.tmp') else 'immutable-artifact'

def read_gate(p):
    p=Path(p).resolve();require(p in ALLOWED,'Unregistered P0 read: '+str(p))
    require(p.suffix.lower() not in {'.pcap','.pcapng','.cap'},'PCAP forbidden')
    READS[rel(p) if p.is_relative_to(ROOT) else str(p)]=dict(path=rel(p) if p.is_relative_to(ROOT) else str(p),category=category(p))
    return p

def digest(p):
    p=read_gate(p)
    if p not in DIGESTS:
        h=hashlib.sha256()
        with p.open('rb') as f:
            for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
        DIGESTS[p]=h.hexdigest()
    return DIGESTS[p]

def js(p):return json.loads(read_gate(p).read_text(encoding='utf-8-sig'))
def df(p):return pd.read_parquet(read_gate(p))
def pt(p):
    # CPU is used only for serialized-artifact IO/statistics. No model runs here.
    return torch.load(read_gate(p),map_location='cpu',weights_only=True)
def arr(x):return np.array(x,dtype=np.float64,copy=True)
def qhash(q):return hashlib.sha256(arr(q).tobytes()).hexdigest()

def output(p):
    p=Path(p).resolve();require(p.is_relative_to(OUT) or p.is_relative_to(DOC),'Write outside P0 roots')
    p.parent.mkdir(parents=True,exist_ok=True);return p

def write(p,v):
    p=output(p);tmp=p.with_name(p.name+'.tmp')
    tmp.write_text(json.dumps(v,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False,default=lambda x:x.item() if isinstance(x,np.generic) else str(x))+'\n',encoding='utf-8');os.replace(tmp,p)

def save(name,rows):
    p=output(OUT/'tables'/(name+'.parquet'));tmp=p.with_name(p.name+'.tmp');d=pd.DataFrame(rows)
    if 'rejection_reason_counts' in d:
        d['rejection_reason_counts_json']=d.rejection_reason_counts.map(lambda v:json.dumps(v,sort_keys=True,separators=(',',':')))
        d=d.drop(columns='rejection_reason_counts')
    d.to_parquet(tmp,index=False);os.replace(tmp,p)
def note(p,text):output(p).write_text(text,encoding='utf-8')
def emit(s,**v):print(s,v,flush=True)

def own(p):
    m=js(p.with_suffix('.json'));require(m.get('safe_roundtrip_passed') and digest(p)==m['sha256'],'Unsafe/changed checkpoint: '+rel(p));return pt(p),m

def init():
    require(not OUT.exists(),'P0 run exists; refuse overwrite')
    ALLOWED.update({PLAN.resolve(),Path(__file__).resolve()})
    ALLOWED.update(p.resolve() for p in PILOT.rglob('*') if p.is_file() and not p.name.endswith('.tmp'))
    require((PILOT/'completion.json').resolve() in ALLOWED,'Pilot completion missing')
    end=js(PILOT/'completion.json');require(end['pilot_complete'] and end['completed_trajectories']==36,'Pilot incomplete')
    ver=js(PILOT/'verification.json');require(digest(PILOT/'verification.json')==end['verification_sha256'],'Pilot verification seal')
    c=js(PILOT/'manifests/experiment-contract.json');require(digest(PILOT/'manifests/experiment-contract.json')==js(PILOT/'manifests/seal.json')['contract_sha256'],'Pilot contract seal')
    require(c['rho']==.01 and c['nu']==1 and c['max_accepted']==20 and c['max_trials']==40 and c['max_backtracks']==8,'Frozen policy mismatch')
    expected={**c['code'],**c['fixed_code'],**c['parent_metadata'],**c['recovery']['old_files']}
    expected.update({p:v['sha256'] for p,v in c['inputs'].items()})
    ALLOWED.update((ROOT/p).resolve() for p in expected)
    envfile=Path(c['environment']['installed_LBFGS_path']).resolve();ALLOWED.add(envfile);expected[str(envfile)]=c['environment']['installed_LBFGS_sha256']
    fp=FORMAL/'manifests/experiment-contract.json';ALLOWED.add(fp.resolve());fc=js(fp)
    fv=js(FORMAL/'verification.json')['files']
    for r in c['roles']:
        for k in ['P','G']:
            p=FORMAL/'tasks'/r['id']/(k+'.pt');ALLOWED.update({p.resolve(),p.with_suffix('.json').resolve()})
            expected[rel(p)]=fv[rel(p)];expected[rel(p.with_suffix('.json'))]=fv[rel(p.with_suffix('.json'))]
            fr=next(x for x in fc['roles'] if x['id']==r['id']);mp=ROOT/fr['reuse_maps'][k]
            expected[rel(mp)]=fc['artifacts'][rel(mp)]['sha256'];expected[rel(mp.with_suffix('.json'))]=fc['fixed_files'][rel(mp.with_suffix('.json'))]
            ALLOWED.update({mp.resolve(),mp.with_suffix('.json').resolve()})
    require(len(c['roles'])==12 and len(c['inner_roles'])==144,'P0 role set')
    runtime=[];stable={};mismatches=[]
    # Historical manifests are checked only against their own declared artifacts,
    # never by scanning historical H predictions/datasets.
    for path,h in {**expected,**ver['files']}.items():
        p=Path(path) if Path(path).is_absolute() else ROOT/path
        ALLOWED.add(p.resolve());actual=digest(p)
        if category(p)=='runtime-control':
            runtime.append(dict(path=rel(p),previous_sha256=h,observed_sha256=actual,changed=actual!=h,observed_unix=time.time(),mtime_ns=p.stat().st_mtime_ns))
        else:
            if actual!=h:mismatches.append(str(p))
            stable[rel(p) if p.is_relative_to(ROOT) else str(p)]=actual
    require(not mismatches,'Immutable input mismatch: '+str(mismatches[:5]))
    for p in PILOT.rglob('*'):
        if p.is_file() and category(p)=='runtime-control' and not p.name.endswith('.tmp') and rel(p) not in {x['path'] for x in runtime}:
            runtime.append(dict(path=rel(p),previous_sha256=None,observed_sha256=digest(p),changed=None,observed_unix=time.time(),mtime_ns=p.stat().st_mtime_ns))
    save('runtime-inventory',runtime)
    write(OUT/'manifests/immutable-input-seal.json',dict(passed=True,classification_fixed=sorted(RUNTIME_NAMES),files=stable))
    write(OUT/'manifests/P0-contract.json',dict(plan_sha256=digest(PLAN),code_sha256=digest(Path(__file__)),stage='P0',new_training_authorized=False,
                                           H_U_reads_authorized=False,new_policy_decisions_authorized=False,parent_contract_sha256=digest(PILOT/'manifests/experiment-contract.json'),
                                           stopped_parent_access_log_complete=False,CPU_purpose='artifact IO and descriptive statistics only',
                                           export_repair=dict(previous_run='run-01',scope='empty rejection-count dictionary serialized as JSON text',numerical_policy_changed=False)))
    emit('immutable_inputs_verified',files=len(stable),runtime_changes=sum(x['changed'] is True for x in runtime))
    return c,fc,end,ver,runtime

def source_point(c,e,kind,q,gradient=False):
    h=qhash(q);cache=PILOT/('gradient-cache' if gradient else 'value-cache')/kind/e['id']/(h+'.pt')
    if h==c['q_one_hash']:cache=FORMAL/'feedback-cache'/kind/e['id']/(h+'.pt')
    memo=DERIVATIVES if gradient else POINTS
    key=str(cache)
    if key in memo:return memo[key]
    value,meta=own(cache);require(meta['role_id']==e['id'] and meta['kind']==kind and meta['q_sha256']==h,'Task/key identity mismatch')
    require(np.array_equal(arr(value['q']),arr(q)),'Bitwise q mismatch')
    ch=value['checks'];fine=ch['fine'];val=ch['validated'];vc=ch['validation']
    require(meta.get('passed') or meta.get('gradient_passed') or meta.get('forward_passed'),'Unqualified publication')
    require(max(fine['original_gradient'],val['original_gradient'])<=1e-9,'Stored original residual failed')
    require(max(fine['gradient_replay_error'],val['gradient_replay_error'],fine['objective_replay_error'],val['objective_replay_error'])<1e-10,'Original target/gradient replay gate')
    require(vc['correction_executed'] and vc['steps']==1 and vc['step_size']==1.,'Missing true one-step validation')
    require(vc['H_error']<=1e-10 and vc['symmetry']<=1e-12 and vc['Newton_backward_error']<=1e-12 and vc['dual_step_relative']<=1e-8,'Stored validation gates failed')
    out=dict(path=rel(cache),sha256=digest(cache),Q_f=value['Q_f'],Q_v=value['Q_v'],Je_f=fine['J'],Je_v=val['J'],
             raw_grad_f=fine['original_gradient'],raw_grad_v=val['original_gradient'],forward_pass=True,seconds=value.get('seconds'))
    if gradient:
        require(ch['implicit_f']['passed'] and ch['implicit_v']['passed'],'Stored implicit endpoint failed')
        gf=arr(value['gradient_f']);gv=arr(value['gradient_v']);require(np.all(np.abs(gf-gv)<=1e-6+1e-3*np.maximum(np.abs(gf),np.abs(gv))),'Task derivative stability')
        out.update(gf=gf,gv=gv,gradient_delta=float(np.max(np.abs(gf-gv))),gradient_pass=True)
    memo[key]=out;return out

def evaluate(q,Qf,Qv,coeff):
    q=arr(q);shrink=float(.001*np.square(q-1).sum());gs=.002*(q-1)
    if coeff is None:gap=np.zeros(10);parts=np.zeros(10);gp=np.zeros(10)
    else:
        A,B,s=(arr(coeff[x]) for x in ['A','B','s']);gap=(q-1)*(A*(q+1)-2*B)/s
        parts=np.square(np.maximum(gap,0))/20;gp=np.maximum(gap,0)*(2*A*q-2*B)/(10*s)
    penalty=float(parts.sum());return dict(shrink=shrink,penalty=penalty,Lf=Qf+shrink+penalty,Lv=Qv+shrink+penalty,gap=gap,parts=parts,gs=gs,gp=gp)

def gates(origin,last,n,dual):
    q0,qe=arr(origin.q),arr(last.q);result={}
    for suffix in ['f','v']:
        g0,ge=arr(origin['g_'+suffix]),arr(last['g_'+suffix]);a=float(np.max(np.abs(q0-np.clip(q0-g0,0,2))));b=float(np.max(np.abs(qe-np.clip(qe-ge,0,2))))
        result.update({f'PG0_{suffix}':a,f'PGend_{suffix}':b,f'ratio_{suffix}':None if a==0 else b/a,
                       f'reduction_pct_{suffix}':None if a==0 else 100*(1-b/a),f'residual_margin_{suffix}':.2*a-b,
                       f'residual_gate_{suffix}':b<=.2*a,f'stationary_margin_{suffix}':1e-3-b,f'stationary_gate_{suffix}':b<=1e-3})
    improvement=min(origin.L_f,origin.L_v)-max(last.L_f,last.L_v);required=1e-4*max(1.,abs(origin.L_f))
    result.update(improvement=improvement,improvement_required=required,improvement_margin=improvement-required,
                  improvement_gate=improvement>=required,normal20_gate=n==20,accepted_margin=20-n,dual_descent_gate=dual)
    result['stationary_gate']=result['stationary_gate_f'] and result['stationary_gate_v']
    result['finite_progress_gate']=n==20 and dual and result['improvement_gate'] and result['residual_gate_f'] and result['residual_gate_v']
    return result

def run():
    begin=time.perf_counter();c,fc,end,ver,runtime=init();fro={r['id']:r for r in fc['roles']}
    close=[];step_rows=[];trial_rows=[];block_rows=[];lineage=[];source_rows=[];kind_costs=[];accepted_total=0;trial_total=0
    for r in c['roles']:
        rs=[e for e in c['inner_roles'] if (e['target'],e['group'])==(r['target'],r['group'])];require(len(rs)==12,'Twelve source roles')
        for e in rs:require(e['target'] not in e['sources']+[e['calibration']] and not set(e['train_contents'])&set(e['validation_contents']),'Membership isolation')
        for kind in ['P','G']:
            logs=[];lost=0
            for e in rs:
                for p in (PILOT/'diagnostic-fit-logs'/e['id']).glob(kind+'-*.json'):
                    d=js(p);require(d['accepted'] and d['device']=='cuda:0' and d['dtype']=='float64','Backend log failed')
                    logs.append(d)
            pending=c['recovery']['pending']
            if pending['kind']==kind and pending['role_id']==r['id']:lost=1
            kind_costs.append(dict(role_id=r['id'],kind=kind,shared_methods=['O-DP','O-TP'] if kind=='P' else ['O-DG'],
                                   completed_new_source_LR=len(logs),interrupted_source_LR_attempts=lost,new_source_LR_attempts=len(logs)+lost,
                                   LBFGS_iterations=sum(x['iterations'] for x in logs),LBFGS_evaluations=sum(x['function_evaluations'] for x in logs),
                                   root_solver_seconds=sum(x['seconds'] for x in logs),lost_attempt_seconds=None,
                                   allocation_to_each_P_method='not_identifiable_without_full_historical_cache_access_trace' if kind=='P' else 'own_G',
                                   fine_max_per_task=30,validation_max_per_task=1,LR_max_iter=2000,LR_max_eval=10000))
        for arm,kind in KINDS.items():
            root=PILOT/'trajectories'/r['id']/arm;states=df(root/'states.parquet');trials=df(root/'trials.parquet');result=js(root/'result.json')
            require(len(states)==result['accepted_updates']+1 and int(trials.accepted.sum())==result['accepted_updates'],'Saved count mismatch')
            M,_=own(PILOT/'scales'/r['id']/(kind+'.pt'));metric=arr(M['M']);require(np.all(metric>=1),'Positive diagonal metric')
            cp=FORMAL/'C-coefficients'/r['id']/(kind+'.pt');fullcoef,_=own(cp);require(np.allclose(metric,1+arr(fullcoef['A'])/arr(fullcoef['s']),rtol=0,atol=0),'Original M replay')
            coeff=None if arm=='O-TP' else fullcoef
            op=FORMAL/'tasks'/r['id']/(kind+'.pt');outer,om=own(op);require(om['rows']==928 and om['train_only'],'Outer train-only provenance')
            for name in ['mu','scale']:
                x=outer['view'][name].contiguous();h=hashlib.sha256(x.view(torch.uint8).numpy().tobytes()).hexdigest()
                lineage.append(dict(role_id=r['id'],arm=arm,category=name,path=rel(op),sha256=digest(op),tensor_sha256=h))
            map_path=fro[r['id']]['reuse_maps'][kind];map_meta=fc['artifacts'][map_path]
            lineage.append(dict(role_id=r['id'],arm=arm,category='fixed-map',path=map_path,sha256=map_meta['sha256'],kind=kind,eta=r['eta'],t=r['t'],verification='registered_parent_lineage_not_refit'))
            for name,p in [('C-coefficients',cp),('metric',PILOT/'scales'/r['id']/(kind+'.pt')),('states',root/'states.parquet'),('trials',root/'trials.parquet'),('result',root/'result.json')]:
                lineage.append(dict(role_id=r['id'],arm=arm,category=name,path=rel(p),sha256=digest(p),kind=kind))
            numeric=True;max_target_error=0.;max_task_error=0.
            for _,s in states.iterrows():
                q=arr(s.q);checkpoint,meta=own(root/f'q{int(s.state):02d}.pt');require(meta['accepted'] and np.array_equal(arr(checkpoint['state']['q']),q),'Accepted-state identity')
                pts=[source_point(c,e,kind,q,True) for e in rs];Qf=float(np.mean([v['Q_f'] for v in pts]));Qv=float(np.mean([v['Q_v'] for v in pts]));gf=np.mean([v['gf'] for v in pts],0);gv=np.mean([v['gv'] for v in pts],0)
                require(np.all(np.abs(gf-gv)<=1e-6+1e-3*np.maximum(np.abs(gf),np.abs(gv))),'Mean gradient stability replay')
                val=evaluate(q,Qf,Qv,coeff);err=max(abs(Qf-s.Q_f),abs(Qv-s.Q_v),abs(val['Lf']-s.L_f),abs(val['Lv']-s.L_v),abs(val['shrink']-s.shrink),abs(val['penalty']-s.penalty))
                require(err<1e-12 and np.max(np.abs(gf+val['gs']+val['gp']-arr(s.g_f)))<1e-10 and np.max(np.abs(gv+val['gs']+val['gp']-arr(s.g_v)))<1e-10,'Saved outer target/gradient mismatch')
                max_target_error=max(max_target_error,err);max_task_error=max(max_task_error,float(np.max(np.abs(gf-arr(s.task_gradient_f)))))
                for j in range(10):block_rows.append(dict(role_id=r['id'],arm=arm,state=int(s.state),feature=FEATURES[j],q=q[j],M=metric[j],gap=val['gap'][j],penalty_part=val['parts'][j],task_gradient_f=gf[j],task_gradient_v=gv[j],shrink_gradient=val['gs'][j],relation_gradient=val['gp'][j],total_gradient_f=arr(s.g_f)[j]))
                if s.state in [0,states.iloc[-1].state]:
                    for e,v in zip(rs,pts):source_rows.append(dict(role_id=r['id'],arm=arm,state=int(s.state),source_task=e['id'],kind=kind,
                                                               **{k:x for k,x in v.items() if k not in ['gf','gv']}))
            accepted=[];signals=[];forward_count=0
            for _,tr in trials.iterrows():
                cur=states.iloc[int(tr.iteration)-1];q=arr(cur.q);gf=arr(cur.g_f);gv=arr(cur.g_v);p=-gf/metric;norm=float(np.max(np.abs(p*np.sqrt(metric))));gamma=1. if norm==0 else min(1.,.1/norm)
                nq=np.clip(q+tr.alpha*p*gamma,0,2);delta=nq-q;sf=float(gf@delta);sv=float(gv@delta);td=float((np.abs(gf-gv)*np.abs(delta)).sum())+1e-12*max(1.,abs(sf),abs(sv))
                require(np.max(np.abs(nq-arr(tr.q)))<1e-14 and np.max(np.abs(delta-arr(tr.delta)))<1e-14 and abs(gamma-tr.gamma)<1e-14,'Direction/cap/projection replay')
                rec=dict(role_id=r['id'],arm=arm,kind=kind,iteration=int(tr.iteration),backtrack=int(tr.backtrack),alpha=float(tr.alpha),gamma=gamma,
                         cap_triggered=gamma<1.,delta=delta.tolist(),delta_inf=float(np.max(np.abs(delta))),scaled_delta_inf=float(np.max(np.abs(delta*np.sqrt(metric)))),
                         direction_f=sf,direction_v=sv,tau_dir=td,direction_margin=-td-max(sf,sv),direction_pass=max(sf,sv)<-td,
                         forward_evaluated=bool(tr.forward_evaluated),accepted=bool(tr.accepted),reason=tr.reason,evaluation=None if pd.isna(tr.get('evaluation')) else int(tr.evaluation))
                if tr.forward_evaluated:
                    forward_count+=1;pts=[source_point(c,e,kind,nq,False) for e in rs];Qf=float(np.mean([v['Q_f'] for v in pts]));Qv=float(np.mean([v['Q_v'] for v in pts]));val=evaluate(nq,Qf,Qv,coeff)
                    require(max(abs(val['Lf']-tr.L_f),abs(val['Lv']-tr.L_v))<1e-12,'Trial target replay')
                    tl=1e-8*max(1.,abs(cur.L_f),abs(val['Lf']));bound=min(cur.L_f,cur.L_v)+1e-4*min(sf,sv)-tl;upper=max(val['Lf'],val['Lv'])
                    rec.update(Q_f=Qf,Q_v=Qv,J_f=val['Lf'],J_v=val['Lv'],tau_L=tl,acceptance_bound=bound,candidate_upper=upper,value_margin=bound-upper,value_pass=rec['direction_pass'] and upper<=bound)
                if tr.accepted:
                    require(rec['value_pass'],'Accepted update not qualified');accepted.append(rec)
                trial_rows.append(rec)
            require(forward_count==result['trial_evaluations'],'Trial evaluation accounting')
            gr=gates(states.iloc[0],states.iloc[-1],len(accepted),all(x['value_pass'] for x in accepted))
            recomputed='stationary_at_origin' if len(accepted)==0 and gr['stationary_gate'] else 'stationary' if gr['stationary_gate'] else 'finite_progress' if gr['finite_progress_gate'] else result['status']
            require(recomputed==result['status'] and bool(gr['stationary_gate'] or gr['finite_progress_gate'])==result['passed'],'Original qualification changed')
            if result['status']=='stop_budget':require(forward_count==40 and trials.iloc[-1].reason=='trial_budget','Unresolved budget type')
            for a in accepted:
                a=dict(a);a['backtracks_before_accept']=a['backtrack'];step_rows.append(a)
            first,last=states.iloc[0],states.iloc[-1];recovered=(r['id'],arm)==(c['recovery']['pending']['role_id'],c['recovery']['pending']['arm'])
            row=dict(role_id=r['id'],outer=r['outer'],target=r['target'],mask=r['group'],arm=arm,kind=kind,original_status=result['status'],original_pass=result['passed'],
                     J0_f=first.L_f,J0_v=first.L_v,Jend_f=last.L_f,Jend_v=last.L_v,Q0_f=first.Q_f,Q0_v=first.Q_v,Qend_f=last.Q_f,Qend_v=last.Q_v,
                     shrink0=first.shrink,shrink_end=last.shrink,relation0=first.penalty,relation_end=last.penalty,
                     raw_grad0_f=float(np.max(np.abs(arr(first.g_f)))),raw_gradend_f=float(np.max(np.abs(arr(last.g_f)))),
                     raw_grad0_v=float(np.max(np.abs(arr(first.g_v)))),raw_gradend_v=float(np.max(np.abs(arr(last.g_v)))),
                     scaled_PG0_f=first.scaled_PG_f,scaled_PGend_f=last.scaled_PG_f,scaled_PG0_v=first.scaled_PG_v,scaled_PGend_v=last.scaled_PG_v,
                     accepted_updates=len(accepted),accepted_limit=20,accepted_remaining=20-len(accepted),trial_evaluations=forward_count,trial_limit=40,trial_remaining=40-forward_count,
                     logical_source_forward=12*(1+forward_count),logical_limit=492,logical_remaining=492-12*(1+forward_count),
                     budget_type='per_trajectory_trial_q' if result['status']=='stop_budget' else 'normal_accepted_update_limit',
                     global_time_cap_seconds=14400,global_time_consumed_seconds=end['ledger']['active_seconds'],global_time_remaining_seconds=14400-end['ledger']['active_seconds'],
                     per_method_actual_source_LR=None,shared_cost_key=r['id']+'/'+kind,per_method_physical_cost_attribution='shared_P_not_identifiable' if kind=='P' else 'own_G_in_shared_cost_table',
                     source_LR_logical_upper=492,fine_updates_theoretical_upper=14760,validation_theoretical_upper=492,implicit_theoretical_upper=504,
                     per_method_fine_consumed=None,per_method_validation_consumed=None,per_method_implicit_consumed=None,
                     per_method_cache_hit_consumed=None,physical_counter_missing_reason='full_historical_cache_call_attribution_not_persisted',
                     execution_seconds_recorded=result['seconds'],execution_time_complete=not recovered,recovery_tail_seconds_not_role_allocated=60. if recovered else None,
                     alpha_min=min(x['alpha'] for x in accepted),alpha_max=max(x['alpha'] for x in accepted),alpha_mean=float(np.mean([x['alpha'] for x in accepted])),
                     cap_triggered_accepts=sum(x['cap_triggered'] for x in accepted),rejected_candidates=int((trials.forward_evaluated&~trials.accepted).sum()),
                     accepted_backtracks_mean=float(np.mean([x['backtrack'] for x in accepted])),accepted_backtracks_max=max(x['backtrack'] for x in accepted),
                     rejection_reason_counts=dict(collections.Counter(trials.loc[~trials.accepted,'reason'])),
                     max_original_LR_gradient=float(states.max_original_gradient.max()),max_mean_implicit_difference=float(states.mean_gradient_max_difference.max()),
                     target_replay_max_error=max_target_error,task_gradient_replay_max_error=max_task_error,numerical_replay_pass=True,immutable_integrity_pass=True,
                     permission_policy_no_H_U=True,old_interrupted_access_history_complete=False,full_historical_permission_audit_complete=False,
                     members_sha256=canonical(rs),source_task_ids=[e['id'] for e in rs],eta=r['eta'],t=r['t'],plan_sha256=digest(PLAN),
                     pilot_contract_sha256=digest(PILOT/'manifests/experiment-contract.json'),origin_q_sha256=qhash(first.q),end_q_sha256=qhash(last.q),
                     original_decision_preserved=True,source_reuse_note='optimizer_assets_intact_final_slot_fallback_compatibility_deferred_to_P1',**gr)
            close.append(row);accepted_total+=len(accepted);trial_total+=forward_count
            emit('trajectory_exported',target=r['target'],mask=r['group'],arm=arm,status=result['status'])
    require(accepted_total==662 and trial_total==840 and sum(x['logical_source_forward'] for x in close)==end['ledger']['logical_forward'],'Global logical count replay')
    require(sum(x['new_source_LR_attempts'] for x in kind_costs)==end['ledger']['new_source_LR'],'Physical attempts ledger mismatch')
    save('optimizer-closeout',close);save('accepted-steps',step_rows);save('trial-decisions',trial_rows);save('block-gradients',block_rows)
    save('backend-endpoints',source_rows);save('shared-backend-costs',kind_costs);save('lineage',lineage)
    save('qualified-descent-failure-paths',[x for x in close if x['original_status']=='qualified_descent_only'])
    save('budget-stop-reasons',[x for x in close if x['original_status']=='stop_budget'])
    write(OUT/'global-costs.json',dict(ledger=end['ledger'],per_method_shared_cost_not_allocated=True,interrupted_attempts_counted=1,
                                    role_specific_fine_implicit_cache_attribution_missing=True,initial_reuse_preparation=288,initial_reuse_trajectories=432,
                                    recovered_tail_reserve_seconds=60.,source_fits_or_feedback_new_in_P0=0))
    write(OUT/'recovery-lineage.json',dict(parent=c['recovery'],old_interrupted_reads_reconstructed=False,original_results_rewritten=False))
    render(close,runtime,end)
    write(OUT/'reads.json',dict(files=list(READS.values()),P0_only=True,H_U_numeric_reads=0,new_model_fits=0))
    files={rel(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.rglob('*') if p.is_file() and p.name!='completion.json'}
    files[rel(DOC/'P0-optimizer-closeout.md')]=hashlib.sha256((DOC/'P0-optimizer-closeout.md').read_bytes()).hexdigest()
    write(OUT/'verification.json',dict(passed=True,trajectories=36,accepted_replays=662,trial_replays=840,original_statuses_preserved=True,
                                     immutable_inputs_verified=True,runtime_change_count=sum(x['changed'] is True for x in runtime),
                                     source_cost_replayed=True,full_historical_access_audit_complete=False,new_training=0,H_U_numeric_reads=0,files=files))
    write(OUT/'completion.json',dict(status='P0_complete_waiting_policy_confirmation',passed=True,stopped_before_P1=True,
                                    new_training=0,H_U_numeric_reads=0,new_policy_decisions=0,seconds=time.perf_counter()-begin,
                                    verification_sha256=hashlib.sha256((OUT/'verification.json').read_bytes()).hexdigest()))
    emit('P0_complete',trajectories=36,accepted_replays=662,new_fits=0)

def render(rows,runtime,end):
    d=pd.DataFrame(rows);failure=d[d.original_status.eq('qualified_descent_only')];budget=d[d.original_status.eq('stop_budget')]
    txt='# 动态漂移优化器只读结项报告\n\nP0完成：36条轨迹原停止状态与资格保持不变。662次接受更新及840个已评价候选完成源内保存产物重放，没有新拟合、H/U读取或新业务分数。本阶段不生成q_use，不启用新策略，停在P1合同确认。\n\n'
    txt+='## 资格总览\n\n| 方法 | 有限改进 | 仅下降 | trial预算停止 | 驻点 |\n| --- | ---: | ---: | ---: | ---: |\n'
    for a in KINDS:
        part=d[d.arm.eq(a)];cnt=part.original_status.value_counts();txt+=f"| {a} | {cnt.get('finite_progress',0)} | {cnt.get('qualified_descent_only',0)} | {cnt.get('stop_budget',0)} | {int(part.stationary_gate.sum())} |\n"
    txt+='\n外层总目标J与内层LR目标Je分别保存，不能用其中一个替代另一个。12条有限改进不是充分收敛；18条仅下降没有达到原f/v各80%残差门。\n\n## 18条仅下降的失败路径\n\n'
    txt+='| 部署 | 组 | 方法 | f残差降低 | v残差降低 | f残差比 | f门余量 | 目标改善门 |\n| --- | --- | --- | ---: | ---: | ---: | ---: | --- |\n'
    for _,r in failure.iterrows():txt+=f"| {r.target} | {r['mask']} | {r.arm} | {r.reduction_pct_f:.4f}% | {r.reduction_pct_v:.4f}% | {r.ratio_f:.8f} | {r.residual_margin_f:.8f} | {'通过' if r.improvement_gate else '未通过'} |\n"
    txt+=f'\nf端降低范围为{failure.reduction_pct_f.min():.4f}%至{failure.reduction_pct_f.max():.4f}%。负的残差门余量表示未通过；原门、状态和终态均不调整，不从早期checkpoint选择更有利的状态。\n\n'
    txt+='## 6条预算停止的实际原因\n\n| 部署 | 组 | 方法 | 接受更新 | 试探实耗/上限 | 接受额度剩余 | 预算类型 |\n| --- | --- | --- | ---: | --- | ---: | --- |\n'
    for _,r in budget.iterrows():txt+=f"| {r.target} | {r['mask']} | {r.arm} | {r.accepted_updates} | {r.trial_evaluations}/40 | {r.accepted_remaining} | 单轨迹trial-q耗尽 |\n"
    txt+='\n这6条均不是全局时间、显存、磁盘或内层LR预算停止。不能把剩余接受额度当作可继续运行的授权；trial额度已耗尽。\n\n'
    txt+='## 更新效率和成本\n\n完整alpha、gamma限幅、投影位移、回溯次数、候选目标与拒绝裕量在accepted-steps和trial-decisions中。662次接受、178次目标下降不足拒绝；额外6行trial_budget仅为停止标志，不算已评价候选。逻辑前向10512，真实LR尝试9877，包括一次未完成且重算的尝试。\n\n'
    txt+='P/T共享同一P物理后端缓存，因此不能给两个方法分别填入独占求解成本。shared-backend-costs按角色和P/G记录实际完成、重算和求解成本；每臂仍单独保留逻辑预算。未保存的历史缓存访问和中断尾部耗时标为缺失，60秒保守预留不分摊给某臂制造精确耗时。\n\n'
    txt+=f"累计活动计算{end['ledger']['active_seconds']/3600:.6f}小时，原4小时上限剩余{(14400-end['ledger']['active_seconds'])/3600:.6f}小时。全局fine、validation、implicit实耗照实保留；P0没有重新执行任何后端训练或求导。\n\n"
    txt+='## 稳定封存和来源链\n\n按固定用途分类排除运行控制文件，而非按是否出现哈希差异挑选排除。旧runner.stdout.log、worker-heartbeat.json和supervisor-heartbeat.json在收尾更新导致旧哈希变化；数值资产、代码和成员输入哈希保持一致。immutable-input-seal是独立补充封存，旧verification和passed字段不覆盖。\n\n'
    txt+='每个角色保存数据/成员、P/G映射、eta/t、共同坐标、C系数与M、q及代码合同来源。映射来源来自已封存训练资产登记，不重训映射。恢复链和17条复用结果原样保留。旧中断阶段没有完整读取日志，后续审计不补造该历史，也不把政策隔离等同于完整历史访问证据。\n\n'
    txt+='首次P0导出run-01在36条数值重放完成后遇到Parquet空字典字段限制。失败现场与源码快照保留，本run-02仅将拒绝原因计数序列化为rejection_reason_counts_json文本；资格、数值、预算和原产物不变，无新增训练。P0可信审计可检查两种类型的C来源，但不向后续QT训练传递完整关系目标。\n\n'
    txt+='## 进入P1前的确认\n\n本P0没有发现数值资产或成员完整性阻断。现有优化产物可以进入兼容性与新策略合同审计，但928行最终槽位及冻结P/G基线的完整回退兼容性仍属于P1，尚未据此生成启用决定。\n\n下一节点需确认：保持原资格、未通过者安全回退；全五折累计优化20小时建议上限（包含已复用成本）；QP相对P-small的C总体F1下降不超过1个百分点且各部署不超过2个百分点的描述性推进门。预算和C门是待确认提议，不是本P0已批准或验证的结论。\n'
    note(DOC/'P0-optimizer-closeout.md',txt)

def tests():
    require(category('runner.stdout.log')=='runtime-control','Runtime class')
    require(category('diagnostic-fit-logs/role/P-key.json')=='immutable-artifact','Numerical logs cannot be excluded')
    require(category('value-cache/P/key.pt')=='immutable-artifact','Numerical artifact class')
    q=np.ones(10);require(qhash(q)==qhash(q.copy()),'Exact hash')
    require(qhash(q)!=qhash(np.nextafter(q,2.)),'No approximate cache')
    for p in [ROOT/'Datasets/forbidden.pcap',FORMAL/'predictions/visits.parquet',FORMAL/'scores/pooled.parquet']:
        try:read_gate(p)
        except RuntimeError:pass
        else:raise RuntimeError('Forbidden read accepted')
    with tempfile.TemporaryDirectory(prefix='proxy-p0-schema-') as tmp:
        p=Path(tmp)/'fixture.parquet';d=pd.DataFrame(dict(rejection_reason_counts_json=['{}','{}']))
        d.to_parquet(p,index=False);require(pd.read_parquet(p).equals(d),'Empty dictionary text roundtrip')
    print(dict(passed=True,tests=9,new_training=0),flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--test',action='store_true');a=ap.parse_args()
    if a.test:tests()
    else:
        try:run()
        except BaseException as exc:
            if OUT.exists():write(OUT/'failure.json',dict(stage='P0',exception=repr(exc),new_training=0,original_results_modified=False))
            raise
