"""One actual full-step Newton validation, independent residual/Hessian checks."""
from common import *
import forward as FW
G,IM,OB=math_modules()

def independent(theta,s,t):
    th=theta.detach().clone().requires_grad_();z=s['x']@th[:,:96].T+th[:,96]
    j=(s['mass']*(torch.logsumexp(z,1)-z.gather(1,s['y'][:,None]).squeeze(1))).sum()+.0005*(1+t)*th[:,:96].square().sum()
    grad=torch.autograd.grad(j,th)[0]
    analytical=G.raw_gradient(theta,s,t)
    replay=(s['mass']*F.cross_entropy(s['x']@theta[:,:96].T+theta[:,96],s['y'],reduction='none')).sum()+.0005*(1+t)*theta[:,:96].square().sum()
    error=float((grad-analytical).abs().max());je=abs(float(j.detach()-replay.detach()))
    require(error<=1e-10 and je<=1e-10,'Independent original residual replay')
    return dict(J=float(j.detach()),gradient=max(float(grad.abs().max()),float(analytical.abs().max())),
                gradient_replay_error=error,objective_replay_error=je),analytical

def evidence_gate(m):
    require(m['correction_executed'] and m['independent_residual_checked'] and m['independent_H_checked'] and
            m['independent_solve_checked'],'A copied state or incomplete evidence cannot qualify')
    require(m['steps']==1 and m['step_size']==1.,'Only one actual full-step correction allowed')

def validate(r,arm,key,f):
    begin=time.perf_counter();a,U,o,rr=production();view=task(r,arm)['view'];s=U.pack(view,arm,f['q'])
    logpath=OUT/'points'/r['id']/arm/f'{key}-validation.json'
    partial=dict(schema='validation_log',role_id=r['id'],arm=arm,key=key,passed=False)
    write(logpath,partial)
    e=f['e'];inv=f['inv'];theta=f['theta'];cuda(theta,s['x'],inv)
    uf=G.encode(theta,e,inv).detach();reencoded=G.decode(uf,e,inv)
    before,raw_f=independent(theta,s,r['t']); rec,raw_rec=independent(reencoded,s,r['t'])
    partial.update(gradient_f=before['gradient'],reencoded_gradient=rec['gradient'],J_f=before['J']);write(logpath,partial)
    require(before['gradient']<=1e-9 and rec['gradient']<=1e-9,'Fine residual no longer accepted')
    # Both differentiation paths are evaluated at the same decoded u state.
    h=G.hessian(reencoded,s,r['t'],e,inv)
    ah=torch.autograd.functional.hessian(lambda z:G.objective(z.reshape(5,97),s,r['t'],e,inv),uf.flatten(),vectorize=True)
    he=float((h-ah).norm()/h.norm().clamp_min(1));sym=float((h-h.T).norm()/h.norm().clamp_min(1))
    partial.update(hessian_error=he,symmetry=sym);write(logpath,partial)
    require(he<=1e-10 and sym<=1e-12,'Validation Hessian mismatch')
    eig=torch.linalg.eigvalsh(h);require(float(eig.min())>0,'Reduced Hessian not positive')
    residual=((e.T@raw_rec)@inv.T).flatten()
    ch=torch.linalg.cholesky(h);delta=-torch.cholesky_solve(residual[:,None],ch).flatten()
    delta_lu=-torch.linalg.solve(h,residual)
    denominator=float(eig.max()*delta.norm()+residual.norm())
    numerator=float((h@delta+residual).norm())
    if denominator==0:
        require(numerator==0 and bool((delta==0).all()) and bool((residual==0).all()),'Undefined zero RHS')
        backward=0.;zero_rhs=True
    else:backward=numerator/denominator;zero_rhs=False
    diff=float((delta-delta_lu).norm());relative=diff/max(float(delta.norm()),float(delta_lu.norm()),1e-30)
    partial.update(Newton_backward_error=backward,independent_step_relative=relative,correction_norm=float(delta.norm()));write(logpath,partial)
    require(backward<=1e-12 and relative<=1e-8,'One-step system not independently verified')
    ledger(validation_steps=1)
    uv=uf+delta.reshape(5,97);tv=G.decode(uv,e,inv)
    after,raw_v=independent(tv,s,r['t'])
    jlimit=1e-12*max(1.,abs(before['J']))
    partial.update(gradient_v=after['gradient'],J_v=after['J'],J_increase=after['J']-before['J'],J_limit=jlimit);write(logpath,partial)
    require(after['gradient']<=1e-9 and after['J']<=before['J']+jlimit,'Validation step violates residual/objective gate')
    rf,pf,zf=FW.feedback(theta,view);rv,pv,zv=FW.feedback(tv,view);rq,_,_=FW.feedback(reencoded,view)
    require(abs(float(rf-f['Q']))<=1e-10,'Original fine risk mismatch')
    relative_step=float(delta.norm()/(1+uf.norm()))
    platform=before['gradient']<=1e-12 and after['gradient']<=1e-12 and relative_step<=1e-10 and abs(after['J']-before['J'])<=jlimit
    meta=dict(schema='validation_log',role_id=r['id'],arm=arm,key=key,
      correction_executed=True,independent_residual_checked=True,independent_H_checked=True,independent_solve_checked=True,
      steps=1,step_size=1.,gradient_f=before['gradient'],gradient_v=after['gradient'],J_f=before['J'],J_v=after['J'],
      gradient_replay_error=max(before['gradient_replay_error'],after['gradient_replay_error']),
      hessian_error=he,symmetry=sym,condition=float(eig.max()/eig.min()),Newton_backward_error=backward,
      independent_step_relative=relative,independent_step_absolute=diff,zero_rhs=zero_rhs,
      correction_norm=float(delta.norm()),relative_correction=relative_step,parameter_change=float((tv-theta).norm()),
      parameter_equal=bool(torch.equal(tv,theta)),Q_f=float(rf),Q_v=float(rv),risk_change=abs(float(rv-rf)),
      reencoding_parameter_change=float((reencoded-theta).norm()),reencoding_J_change=rec['J']-before['J'],
      reencoding_risk_change=float(rq-rf),floating_platform=platform,passed=True)
    evidence_gate(meta)
    ep=dict(theta=tv.detach(),q=f['q'],e=e,inv=inv,Q=rv.detach(),probability=pv.detach(),logits=zv.detach(),
            original_gradient=after['gradient'],objective=after['J'],correction=delta.detach(),parameter_u_before=uf,parameter_u_after=uv)
    put(ep,OUT/'points'/r['id']/arm/f'{key}-v.pt',schema='validation_state',role_id=r['id'],arm=arm,key=key)
    torch.cuda.synchronize();meta['seconds']=time.perf_counter()-begin
    write(OUT/'points'/r['id']/arm/f'{key}-validation.json',meta)
    progress('fine_validated_once',role=r['id'],arm=arm,key=key,platform=platform,risk_change=meta['risk_change'])
    return ep,meta

def tests():
    G.synthetic_tests()
    negatives=0
    base=dict(correction_executed=True,independent_residual_checked=True,independent_H_checked=True,
              independent_solve_checked=True,steps=1,step_size=1.)
    for k in ['correction_executed','independent_residual_checked','independent_H_checked','independent_solve_checked']:
        d=dict(base);d[k]=False
        try:evidence_gate(d)
        except RuntimeError:negatives+=1
        else:raise RuntimeError('Incomplete validation accepted')
    for k,val in [('steps',2),('step_size',.5)]:
        d=dict(base);d[k]=val
        try:evidence_gate(d)
        except RuntimeError:negatives+=1
        else:raise RuntimeError('Unregistered correction accepted')
    return dict(passed=True,synthetic_and_CPU_negative_passed=True,validation_negatives=negatives)
