"""Qualified values for all trials, implicit derivatives only at accepted points."""
from common import *
FW=module('outer_frozen_feedback',ROOT/'eval/dynamic_soft_drift_formal_v2/solution_feedback.py')

def key(q):return hashlib.sha256(q.detach().cpu().numpy().tobytes()).hexdigest()
def legacy(kind):
    require(kind in ['P','G'],'Unknown backend kind');return {'P':'D-P','G':'D-G'}[kind]

def validate_task(r,kind,arm):
    role_permission(r,True)
    d=parent_asset(PARENT/'tasks'/r['id']/(kind+'.pt'),'task',kind,r['id'],arm)
    v=d['view'];cuda(d['inv'],v['main_x'],v['pre_x'],v['mapped_x'],v['query_x'])
    require([len(v[k]) for k in ['main_x','S_x','pre_x','C_x','query_x']]==[144,144,144,48,8],'Source-only shapes')
    require(set(v['query_y'].tolist())==set(r['missing']),'Legal uncovered feedback labels')
    _,u,_,_=production();s=u.pack(v,legacy(kind),tensor(np.ones(10)))
    require(s['x'].shape==(480,96) and abs(float(s['mass'].sum())-1)<1e-12,'Original training rows/mass')
    require(float((weighted(s['y'],s['mass'],6)-1/6).abs().max())<1e-12,'Original balanced class mass')
    require(abs(float(v['pre_mass'].sum()*.1)-1/30)<1e-12,'Original small mass');return d

def initial(r,kind,q,arm):
    require(key(q)==contract()['q_one_hash'] and bool((q==1).all()),'Old cache may only initialize q=1')
    d=parent_asset(PARENT/'feedback-cache'/kind/r['id']/(key(q)+'.pt'),'initial',kind,r['id'],arm)
    require(torch.equal(d['q'],q),'Initial bitwise q mismatch')
    v=task(r,legacy(kind))['view'];_,u,_,_=production();s=u.pack(v,legacy(kind),q)
    # Replay the immutable initial state, without a new fit or a new differentiation study.
    for suffix in ['f','v']:
        audit,_=FW.independent(d['theta_'+suffix],s,r['t'])
        require(audit['original_gradient']<=1e-9,'Initial original residual changed')
        require(abs(float(FW.feedback(d['theta_'+suffix],v))-d['Q_'+suffix])<1e-12,'Initial feedback coordinate mismatch')
        require(d['checks']['implicit_'+suffix]['passed'],'Initial derivative not accepted')
    require(d['checks']['validation']['correction_executed'] and d['checks']['validation']['steps']==1,'Distinct validated endpoint missing')
    require(bool(((d['gradient_f']-d['gradient_v']).abs()<=1e-6+1e-3*torch.maximum(d['gradient_f'].abs(),d['gradient_v'].abs())).all()),'Initial derivative stability')
    ledger(initial_reuse=1);return d

def value(r,kind,q,arm):
    resource_gate();h=key(q);p=OUT/'value-cache'/kind/r['id']/(h+'.pt')
    if p.exists():
        d=own(p);require(torch.equal(d['q'],q),'Exact cache mismatch');ledger(cache_hits=1);return d
    if h==contract()['q_one_hash']:return initial(r,kind,q,arm)
    started=time.perf_counter();v=task(r,legacy(kind))['view'];inv=task(r,legacy(kind))['inv']
    _,u,_,_=production();s=u.pack(v,legacy(kind),q);e=FW.G.basis();cuda(q,s['x'],inv)
    logpath=OUT/'feedback-logs'/kind/r['id']/(h+'.json');partial=dict(role_id=r['id'],kind=kind,q=q.tolist(),status='attempting')
    write(logpath,partial);theta=tv=None
    try:
        ledger(new_source_LR=1)
        model,log=solver().fit_preconditioned(s['x'],s['y'],s['mass'],r['t'],dict(role_id=r['id'],arm=kind+'-'+h),diagnostic=True)
        partial['root_solver']=log;theta=torch.cat([model['weight'],model['bias'][:,None]],1)
        theta,audit,trace=FW.refine(theta,s,r['t'],e,inv);partial['fine_trace']=trace
        tv,vaudit,vcheck=FW.validation(theta,s,r['t'],e,inv);partial['validation']=vcheck
        d=dict(q=q.detach().clone(),theta_f=theta,theta_v=tv,Q_f=float(FW.feedback(theta,v)),Q_v=float(FW.feedback(tv,v)),
               checks=dict(fine=audit,validated=vaudit,validation=vcheck),seconds=time.perf_counter()-started)
        put(d,p,role_id=r['id'],kind=kind,forward_passed=True,q_sha256=h)
        partial.update(status='forward_qualified',seconds=d['seconds']);write(logpath,partial);return d
    except BaseException as exc:
        partial.update(status='failed',exception=str(exc),seconds=time.perf_counter()-started);write(logpath,partial)
        state=dict(q=q,theta_f=theta,theta_v=tv)
        if theta is not None:state['failure_H']=FW.G.hessian(theta,s,r['t'],e,inv).detach()
        put(state,OUT/'failures'/f'{kind}-{h}-{time.time_ns()}.pt',role_id=r['id'],kind=kind,automatic_retry=False);raise

def gradient(r,kind,d):
    if 'gradient_f' in d:return d
    p=OUT/'gradient-cache'/kind/r['id']/(key(d['q'])+'.pt')
    if p.exists():return own(p)
    resource_gate();inv=task(r,legacy(kind))['inv'];e=FW.G.basis();ends=[]
    for suffix in ['f','v']:
        ledger(implicit=1)
        ends.append(FW.IM.evaluate(r,legacy(kind),dict(theta=d['theta_'+suffix],q=d['q'],e=e,inv=inv,Q=tensor(d['Q_'+suffix]),original_gradient=d['checks'][{'f':'fine','v':'validated'}[suffix]]['original_gradient'])))
    f,v=ends;ok,delta=FW.IM.stability(f,v);require(ok,'Fine/validated implicit gradient unstable')
    out=dict(q=d['q'],Q_f=d['Q_f'],Q_v=d['Q_v'],gradient_f=f['gradient'],gradient_v=v['gradient'],
             checks={**d['checks'],'implicit_f':{k:x for k,x in f.items() if not isinstance(x,torch.Tensor)},
                     'implicit_v':{k:x for k,x in v.items() if not isinstance(x,torch.Tensor)},'gradient_delta':delta})
    put(out,p,role_id=r['id'],kind=kind,gradient_passed=True,q_sha256=key(d['q']));return out

def aggregate(rs,kind,q,arm,need_gradient,values=None,reserved=False):
    require(kind==kind_for(arm) and len(rs)==12,'Typed twelve-task scope')
    if values is None:
        if not reserved:ledger(logical_forward=12)
        values=[value(r,kind,q,arm) for r in rs]
    if need_gradient:values=[gradient(r,kind,d) for r,d in zip(rs,values)]
    out=dict(Q_f=float(np.mean([d['Q_f'] for d in values])),Q_v=float(np.mean([d['Q_v'] for d in values])),
             max_original_gradient=max(max(d['checks']['fine']['original_gradient'],d['checks']['validated']['original_gradient']) for d in values),logical_tasks=12)
    if need_gradient:
        gf=torch.stack([d['gradient_f'] for d in values]).mean(0);gv=torch.stack([d['gradient_v'] for d in values]).mean(0)
        require(bool(((gf-gv).abs()<=1e-6+1e-3*torch.maximum(gf.abs(),gv.abs())).all()),'Mean twelve-task implicit stability')
        out.update(gradient_f=gf,gradient_v=gv,mean_gradient_max_difference=float((gf-gv).abs().max()),max_task_gradient_difference=max(d['checks']['gradient_delta'] for d in values))
    return out,values

