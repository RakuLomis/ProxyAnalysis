"""Accepted v4 forward LR plus bounded same-objective Newton refinement."""
from common import *
import gauge as G

def feedback(theta,v):
    cuda(theta,v['query_x'],v['query_mass'])
    z=v['query_x']@theta[:,:96].T+theta[:,96]
    ce=torch.logsumexp(z,1)-z.gather(1,v['query_y'][:,None]).squeeze(1)
    return (ce*v['query_mass']).sum(),torch.softmax(z,1),z

def refine(theta,s,t,e,inv,log,callback):
    c=contract(); u=G.encode(theta,e,inv).detach(); projected=G.decode(u,e,inv)
    common_change=float(.0005*(1+t)*(theta[:,:96].square().sum()-projected[:,:96].square().sum()))
    trace=[]; endpoints=[]; reached=0; log['trace']=trace
    for iteration in range(c['Newton_max']+1):
        log['Newton_updates']=iteration
        theta=G.decode(u,e,inv); raw=G.raw_gradient(theta,s,t)
        maximum=float(raw.abs().max()); value=G.objective(u,s,t,e,inv).detach()
        row=dict(iteration=iteration,objective=float(value),original_gradient=maximum)
        trace.append(row)
        while reached<2 and maximum<=c['forward_precision'][reached]:
            audit=G.audit(theta,s,t,e,inv)
            ep=dict(theta=theta.detach().clone(),threshold=c['forward_precision'][reached],**audit)
            endpoints.append(ep); callback(ep,reached,iteration)
            reached+=1
        if reached==2:
            log.update(Newton_updates=iteration,projection_L2_change=common_change,trace=trace,accepted=True)
            return endpoints,log
        require(iteration<c['Newton_max'],'Newton refinement budget exhausted')
        h=G.hessian(theta,s,t,e,inv)
        grad=((e.T@raw)@inv.T).reshape(-1)
        chol=torch.linalg.cholesky(h)
        delta=-torch.cholesky_solve(grad[:,None],chol).reshape(5,97)
        gtd=float((grad*delta.flatten()).sum())
        require(np.isfinite(gtd) and gtd<0,'Non-descent Newton refinement direction')
        accepted=False
        for j in range(c['backtrack_max']):
            step=c['backtrack']**j; candidate=u+step*delta
            candidate_value=G.objective(candidate,s,t,e,inv).detach()
            if bool(torch.isfinite(candidate_value)) and float(candidate_value)<=float(value)+c['Armijo_c1']*step*gtd:
                row.update(step=step,line_trials=j+1,gtd=gtd)
                u=candidate.detach(); accepted=True; ledger(Newton_updates=1); break
        require(accepted,'Armijo refinement failed; no adaptive budget extension')
    raise RuntimeError('Unreachable refinement exit')

def solve(r,arm,q,key,old_reference=False):
    a,u,o,rr=production(); v=task(r,arm)['view']; co=coordinate(r,arm)
    s=u.pack(v,arm,q); e=G.basis(); inv=co['inv']
    cuda(s['x'],s['mass'],inv,q)
    path=OUT/'endpoints'/r['id']/arm/key
    require(not path.with_suffix('.json').exists(),'No endpoint overwrite')
    beg=time.perf_counter(); log=dict(role_id=r['id'],arm=arm,key=key,q=q.tolist(),old_reference=old_reference,accepted=False)
    write(path.with_suffix('.json'),log); ledger(q_points_attempted=1)
    try:
        if old_reference:
            m=reference(r,arm); ledger(old_reference_refinements=1)
            require(torch.equal(v['mu'],m['mu']) and torch.equal(v['scale'],m['scale']),'Reference scale changed')
        else:
            ledger(new_q_LR_attempted=1)
            sol=solver(); m,lrlog=sol.fit_preconditioned(s['x'],s['y'],s['mass'],r['t'],
                        dict(role_id=r['id'],arm=arm+'-'+key),diagnostic=True)
            log['initial_solver']=lrlog; ledger(new_q_LR_accepted=1)
        theta=torch.cat([m['weight'],m['bias'][:,None]],1)
        require(float(u.original_gradient(theta,s,r['t']).abs().max())<=1e-5,'Old precision not accepted')
        def callback(ep,level,iteration):
            risk,p,z=feedback(ep['theta'],v)
            ep.update(Q=risk.detach(),probability=p.detach(),logits=z.detach())
            put(dict(**ep,q=q.detach(),inv=inv,e=e),path.parent/(path.name+f'-level{level}.pt'),
                role_id=r['id'],arm=arm,key=key,threshold=ep['threshold'],iteration=iteration)
            ledger(precision_endpoints=1)
        endpoints,log=refine(theta,s,r['t'],e,inv,log,callback)
        torch.cuda.synchronize(); log['seconds']=time.perf_counter()-beg
        write(path.with_suffix('.json'),log)
        ledger(q_points_refined=1)
        progress('solution_point_complete',role=r['id'],arm=arm,key=key,seconds=log['seconds'],Newton_updates=log['Newton_updates'])
        return endpoints
    except BaseException as exc:
        log.update(exception=str(exc),seconds=time.perf_counter()-beg)
        write(path.with_suffix('.json'),log); raise
