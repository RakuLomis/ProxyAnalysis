"""Qualified forward/fine/one-validation/implicit policy at every actual q."""
from common import *
G=module('gauge',ROOT/'eval/dynamic_soft_drift_implicit_pilot/gauge.py')
IM=module('implicit',ROOT/'eval/dynamic_soft_drift_implicit_pilot/implicit.py')

def feedback(theta,v):
    z=v['query_x']@theta[:,:96].T+theta[:,96]
    q=(v['query_mass']*(torch.logsumexp(z,1)-z.gather(1,v['query_y'][:,None]).squeeze(1))).sum()
    require(torch.isfinite(q),'Nonfinite legal feedback');return q.detach()

def independent(theta,s,t):
    ztheta=theta.detach().clone().requires_grad_();z=s['x']@ztheta[:,:96].T+ztheta[:,96]
    j=(s['mass']*(torch.logsumexp(z,1)-z.gather(1,s['y'][:,None]).squeeze(1))).sum()+.0005*(1+t)*ztheta[:,:96].square().sum()
    grad=torch.autograd.grad(j,ztheta)[0];manual=G.raw_gradient(theta,s,t)
    other=(s['mass']*F.cross_entropy(s['x']@theta[:,:96].T+theta[:,96],s['y'],reduction='none')).sum()+.0005*(1+t)*theta[:,:96].square().sum()
    ge=float((grad-manual).abs().max());je=abs(float(j.detach()-other))
    require(ge<1e-10 and je<1e-10,'Original residual/target replay')
    return dict(J=float(j.detach()),original_gradient=max(float(grad.abs().max()),float(manual.abs().max())),gradient_replay_error=ge,objective_replay_error=je),manual

def refine(theta,s,t,e,inv):
    u=G.encode(theta,e,inv).detach();trace=[]
    for i in range(31):
        theta=G.decode(u,e,inv);raw=G.raw_gradient(theta,s,t);mx=float(raw.abs().max());j=G.objective(u,s,t,e,inv).detach()
        row=dict(iteration=i,J=float(j),original_gradient=mx);trace.append(row)
        if mx<=1e-9:
            audit,_=independent(theta,s,t);require(audit['original_gradient']<=1e-9,'Fine independent residual');return theta.detach(),audit,trace
        require(i<30,'Fine refinement budget exhausted')
        h=G.hessian(theta,s,t,e,inv);g=((e.T@raw)@inv.T).flatten()
        d=-torch.cholesky_solve(g[:,None],torch.linalg.cholesky(h)).reshape(5,97)
        gtd=float(g@d.flatten());require(np.isfinite(gtd) and gtd<0,'Non-descent fine update')
        accepted=False
        for k in range(25):
            alpha=.5**k;new=u+alpha*d;value=G.objective(new,s,t,e,inv).detach()
            if bool(torch.isfinite(value)) and float(value)<=float(j)+1e-4*alpha*gtd:
                u=new.detach();ledger(refinement=1);row.update(alpha=alpha,trials=k+1);accepted=True;break
        require(accepted,'Fine Armijo failure; no retry')
    raise RuntimeError('Unreachable refinement')

def validation(theta,s,t,e,inv):
    before,raw=independent(theta,s,t);require(before['original_gradient']<=1e-9,'Fine residual before validation')
    uf=G.encode(theta,e,inv).detach();rec=G.decode(uf,e,inv);replay,rg=independent(rec,s,t)
    require(replay['original_gradient']<=1e-9,'Reencoded fine residual')
    h=G.hessian(rec,s,t,e,inv)
    ad=torch.autograd.functional.hessian(lambda z:G.objective(z.reshape(5,97),s,t,e,inv),uf.flatten(),vectorize=True)
    he=float((h-ad).norm()/h.norm().clamp_min(1));sym=float((h-h.T).norm()/h.norm().clamp_min(1))
    require(he<=1e-10 and sym<=1e-12,'Validation Hessian verification')
    eig=torch.linalg.eigvalsh(h);require(float(eig.min())>0,'Hessian not positive')
    residual=((e.T@rg)@inv.T).flatten();ch=torch.linalg.cholesky(h)
    d=-torch.cholesky_solve(residual[:,None],ch).flatten();dl=-torch.linalg.solve(h,residual)
    denominator=float(eig.max()*d.norm()+residual.norm());numerator=float((h@d+residual).norm())
    if denominator==0:require(numerator==0 and bool((d==0).all()),'Zero RHS inconsistency');back=0.
    else:back=numerator/denominator
    relerr=float((d-dl).norm())/max(float(d.norm()),float(dl.norm()),1e-30)
    require(back<=1e-12 and relerr<=1e-8,'Validation linear-system gate')
    ledger(validation=1);tv=G.decode(uf+d.reshape(5,97),e,inv).detach();after,_=independent(tv,s,t)
    limit=1e-12*max(1,abs(before['J']))
    require(after['original_gradient']<=1e-9 and after['J']<=before['J']+limit,'Validation residual/objective gate')
    return tv,after,dict(H_error=he,symmetry=sym,condition=float(eig.max()/eig.min()),Newton_backward_error=back,
                       dual_step_relative=relerr,J_f=before['J'],J_v=after['J'],gradient_f=before['original_gradient'],gradient_v=after['original_gradient'],
                       correction_executed=True,steps=1,step_size=1.,parameter_equal=bool(torch.equal(theta,tv)),parameter_change=float((theta-tv).norm()))

def point(r,kind,q):
    arm='D-G' if kind=='G' else 'D-P';key=hashlib.sha256(q.detach().cpu().numpy().tobytes()).hexdigest()
    p=OUT/'feedback-cache'/kind/r['id']/(key+'.pt')
    if p.with_suffix('.json').exists():
        cached=own(p);require(torch.equal(cached['q'],q),'Cache q binary mismatch');ledger(cache_hits=1);return cached
    begin=time.perf_counter();v=task(r,arm)['view'];inv=task(r,arm)['inv'];amp,u,_,rec=production();s=u.pack(v,arm,q);e=G.basis()
    cuda(q,s['x'],inv);partial=dict(role_id=r['id'],kind=kind,q=q.tolist(),status='attempting',start_unix=time.time())
    logpath=OUT/'feedback-logs'/kind/r['id']/(key+'.json');write(logpath,partial)
    theta=None;tv=None
    try:
        ledger(new_source_LR=1)
        model,log=solver().fit_preconditioned(s['x'],s['y'],s['mass'],r['t'],dict(role_id=r['id'],arm=kind+'-'+key),diagnostic=True)
        theta=torch.cat([model['weight'],model['bias'][:,None]],1);partial['root_solver']=log
        theta,audit,trace=refine(theta,s,r['t'],e,inv);partial['fine_trace']=trace
        tv,vaudit,vcheck=validation(theta,s,r['t'],e,inv);partial['validation']=vcheck
        endpoints=[]
        for th,at in [(theta,audit),(tv,vaudit)]:
            ep=dict(theta=th,q=q,e=e,inv=inv,Q=feedback(th,v),original_gradient=at['original_gradient'])
            ledger(implicit=1);endpoints.append(IM.evaluate(r,arm,ep))
        f,validated=endpoints;ok,delta=IM.stability(f,validated);require(ok,'Fine/validated implicit gradient unstable')
        result=dict(q=q.detach().clone(),theta_f=theta,theta_v=tv,Q_f=f['Q'],Q_v=validated['Q'],gradient_f=f['gradient'],gradient_v=validated['gradient'],
                    checks=dict(fine=audit,validated=vaudit,validation=vcheck,implicit_f={k:x for k,x in f.items() if not isinstance(x,torch.Tensor)},
                                implicit_v={k:x for k,x in validated.items() if not isinstance(x,torch.Tensor)},gradient_delta=delta),seconds=time.perf_counter()-begin)
        put(result,p,role_id=r['id'],kind=kind,q_sha256=key,passed=True,coordinate_path=rel(OUT/'tasks'/r['id']/(kind+'.pt')))
        partial.update(status='accepted',seconds=result['seconds']);write(logpath,partial)
        return result
    except BaseException as exc:
        partial.update(status='failed',exception=str(exc),seconds=time.perf_counter()-begin);write(logpath,partial)
        state=dict(q=q.detach(),theta_f=theta,theta_v=tv)
        if theta is not None:
            state['failure_H']=G.hessian(theta,s,r['t'],e,inv).detach()
        put(state,OUT/'failures'/f'{kind}-{key}-{time.time_ns()}.pt',role_id=r['id'],kind=kind,automatic_retry=False)
        raise

def aggregate(rs,kind,q):
    ledger(logical_forward=12);require(len(rs)==12,'Exactly twelve source tasks')
    values=[point(r,kind,q) for r in rs]
    gf=torch.stack([v['gradient_f'] for v in values]).mean(0);gv=torch.stack([v['gradient_v'] for v in values]).mean(0)
    tol=1e-6+1e-3*torch.maximum(gf.abs(),gv.abs());require(bool(((gf-gv).abs()<=tol).all()),'Mean twelve-task implicit stability failed')
    return dict(Q=float(np.mean([v['Q_f'] for v in values])),gradient=gf,validated_gradient=gv,
                mean_gradient_max_difference=float((gf-gv).abs().max()),max_original_gradient=max(v['checks']['fine']['original_gradient'] for v in values),
                max_task_gradient_difference=max(v['checks']['gradient_delta'] for v in values),logical_tasks=12)

def synthetic_tests():return G.synthetic_tests()

