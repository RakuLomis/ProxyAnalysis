"""Original accepted solver and bounded refinement, no fake coarse snapshots."""
from common import *
G,IM,OB=math_modules()

def feedback(theta,view):
    cuda(theta,view['query_x'],view['query_mass'])
    z=view['query_x']@theta[:,:96].T+theta[:,96]
    ce=torch.logsumexp(z,1)-z.gather(1,view['query_y'][:,None]).squeeze(1)
    return (ce*view['query_mass']).sum(),torch.softmax(z,1),z

def refine(theta,s,t,e,inv,log):
    c=contract();u=G.encode(theta,e,inv).detach();coarse=None;trace=[];log['trace']=trace
    for i in range(31):
        th=G.decode(u,e,inv);raw=G.raw_gradient(th,s,t);mx=float(raw.abs().max())
        value=G.objective(u,s,t,e,inv).detach();row=dict(iteration=i,objective=float(value),original_gradient=mx)
        trace.append(row);log['refinement_steps']=i
        if mx<=1e-9:
            audit=G.audit(th,s,t,e,inv)
            return dict(theta=th.detach(),**audit),coarse
        if mx<=1e-8 and coarse is None:
            coarse=dict(theta=th.detach().clone(),original_gradient=mx,iteration=i)
        require(i<30,'Fine refinement budget exhausted')
        h=G.hessian(th,s,t,e,inv);grad=((e.T@raw)@inv.T).flatten()
        delta=-torch.cholesky_solve(grad[:,None],torch.linalg.cholesky(h)).reshape(5,97)
        gtd=float(grad@delta.flatten());require(np.isfinite(gtd) and gtd<0,'Non-descent refinement')
        accepted=False
        for j in range(25):
            step=.5**j; candidate=u+step*delta
            jnew=G.objective(candidate,s,t,e,inv).detach()
            if bool(torch.isfinite(jnew)) and float(jnew)<=float(value)+1e-4*step*gtd:
                row.update(step=step,line_trials=j+1,gtd=gtd);u=candidate.detach();ledger(refinement_steps=1)
                accepted=True;break
        require(accepted,'Armijo refinement failed; no extension')
    raise RuntimeError('Unreachable')

def fine(r,arm,q,key):
    p=OUT/'points'/r['id']/arm/f'{key}-f.pt'; require(not p.exists(),'Fine already created')
    begin=time.perf_counter();a,U,o,rr=production();view=task(r,arm)['view'];co=coordinate(r,arm)
    s=U.pack(view,arm,q);e=G.basis();inv=co['inv'];cuda(q,s['x'],inv)
    log=dict(schema='solve_log',role_id=r['id'],arm=arm,key=key,accepted=False,q=q.tolist())
    lp=p.parent/(key+'-solve.json');write(lp,log)
    try:
        reused=(r['id']==contract()['first_role'] and arm=='D-P' and key in contract()['reused'])
        if reused:
            paths=contract()['reused'][key]
            f=asset(ROOT/paths['1'],arm,'accepted-fine-reuse');coarse=asset(ROOT/paths['0'],arm,'coarse-diagnostic-reuse')
            require(torch.equal(f['q'],q) and torch.equal(f['inv'],inv) and torch.equal(f['e'],e),'Reuse conditions changed')
            log.update(reused_from=paths['1'],refinement_steps=0);ledger(fine_states_reused=1)
        else:
            old=key=='one-center'
            if old:
                m=reference(r,arm);ledger(old_reference_refinements=1)
                require(torch.equal(m['mu'],view['mu']) and torch.equal(m['scale'],view['scale']),'Preprocessing changed')
            else:
                ledger(new_LR_attempted=1)
                m,sl=solver().fit_preconditioned(s['x'],s['y'],s['mass'],r['t'],dict(role_id=r['id'],arm=arm+'-'+key),diagnostic=True)
                log['initial_solver']=sl;ledger(new_LR_accepted=1)
            th=torch.cat([m['weight'],m['bias'][:,None]],1)
            require(float(U.original_gradient(th,s,r['t']).abs().max())<=1e-5,'Initial forward rejected')
            f,coarse=refine(th,s,r['t'],e,inv,log)
            f.update(q=q.detach(),e=e,inv=inv);ledger(fine_states_created=1)
        risk,pred,z=feedback(f['theta'],view)
        if reused:require(abs(float(risk-f['Q']))<1e-10,'Fine risk replay changed')
        f.update(Q=risk.detach(),probability=pred.detach(),logits=z.detach(),q=q.detach(),e=e,inv=inv)
        if coarse is not None:
            if 'Q' not in coarse:coarse['Q']=feedback(coarse['theta'],view)[0].detach()
            f['coarse_Q']=coarse['Q'].detach();f['coarse_independently_observed']=True
        else:f['coarse_independently_observed']=False
        put(f,p,schema='fine_state',role_id=r['id'],arm=arm,key=key,source_reused=reused)
        log.update(accepted=True,seconds=time.perf_counter()-begin,coarse_independently_observed=coarse is not None)
        write(lp,log);progress('fine_state_ready',role=r['id'],arm=arm,key=key,reused=reused)
        return f
    except Exception as exc:
        log.update(exception=str(exc),seconds=time.perf_counter()-begin);write(lp,log);raise
