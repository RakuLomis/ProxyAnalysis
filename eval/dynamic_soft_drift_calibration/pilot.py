"""Batched source-only full-program finite differences; no actual target reads."""
from common import *
from amplitude import regularizer
import recovery as R
import unroll as U

def evaluate(batch,c,q,arm):
    risk,theta=U.run(batch,q)
    relation=R.soft(q,c)[0] if arm!='T-P' else torch.zeros_like(risk)
    return risk+regularizer(q)+relation,risk,theta

def gradient_checks():
    with stage('hypergradients'):
        require((OUT/'stages/tests.json').exists(),'Unit tests first')
        roles=contract()['pilot_roles'];rows=[];timings=[];trajectories=0
        for arm in ARMS:
            tasks=[pilot_task(r,arm) for r in roles]
            batch=U.batch([t['view'] for t in tasks])
            c={k:torch.stack([t['coeff'][k] for t in tasks]) for k in ['A','B','C','s']}
            for point,values in [('one',np.ones(10)),('interior',np.array([.9,1.1]*5))]:
                q=tensor(np.tile(values,(12,1))).requires_grad_()
                torch.cuda.synchronize();torch.cuda.reset_peak_memory_stats();began=time.perf_counter()
                value,risk,theta=evaluate(batch,c,q,arm)
                gradient=torch.autograd.grad(value.sum(),q)[0].detach()
                torch.cuda.synchronize();elapsed=time.perf_counter()-began
                timings.append(dict(arm=arm,point=point,batch_tasks=12,seconds=elapsed,
                                    peak_MiB=torch.cuda.max_memory_allocated()/1048576))
                trajectories+=12
                put(dict(q=q.detach(),gradient=gradient,value=value.detach(),risk=risk.detach(),theta=theta.detach()),
                    OUT/'pilot/gradients'/f'{arm}-{point}.pt',source_only=True)
                for step in [1e-3,3e-4]:
                    for j in range(10):
                        plus=q.detach().clone();minus=plus.clone();plus[:,j]+=step;minus[:,j]-=step
                        with torch.no_grad():vp=evaluate(batch,c,plus,arm)[0];vm=evaluate(batch,c,minus,arm)[0]
                        fd=(vp-vm)/(2*step);difference=(fd-gradient[:,j]).abs()
                        limit=1e-5+1e-3*fd.abs();trajectories+=24
                        for i,r in enumerate(roles):
                            rows.append(dict(role_id=r['id'],arm=arm,point=point,coordinate=j,step=step,
                                    automatic=float(gradient[i,j]),finite_difference=float(fd[i]),
                                    absolute_error=float(difference[i]),limit=float(limit[i]),passed=bool(difference[i]<=limit[i])))
                        save(pd.DataFrame(rows),OUT/'pilot/hypergradient-checks.parquet')
                        progress('hypergradient_checks',arm=arm,point=point,step=step,coordinate=j,
                                 checks=len(rows),failed=sum(not x['passed'] for x in rows),trajectories=trajectories)
            del batch,c,tasks
        save(pd.DataFrame(timings),OUT/'pilot/hypergradient-timings.parquet')
        result=dict(passed=all(x['passed'] for x in rows),checks=len(rows),
                    failed=sum(not x['passed'] for x in rows),single_episode_trajectories=trajectories,
                    inner_updates=trajectories*64,max_error=max(x['absolute_error'] for x in rows),
                    target_numeric_reads=0,actual_target_C_reads=0,formal_meta_started=False)
        write(OUT/'pilot/hypergradient-completion.json',result)
        require(result['passed'],'Full-program hypergradient finite-difference acceptance failed; inspect saved checks')

def converged_reference():
    with stage('converged_reference'):
        require(read(OUT/'pilot/hypergradient-completion.json')['passed'],'Gradient acceptance first')
        rows=[];optimizer=solver();one=tensor(np.ones(10))
        for r in contract()['pilot_roles']:
            for arm in ['D-P','D-G']:
                dst=OUT/'pilot/models'/r['id']/f'{arm}.pt'
                task=pilot_task(r,arm);v=task['view'];s=U.pack(v,arm,one)
                m,log=optimizer.fit_preconditioned(s['x'],s['y'],s['mass'],r['t'],dict(role_id=r['id'],arm=arm),diagnostic=True)
                put(m,dst,optimizer=log,source_only=True)
                with torch.no_grad():
                    risk,theta=U.run(U.batch([v]),one[None,:])
                    obj=U.original_objective(theta[0],s,r['t'])
                    grad=U.original_gradient(theta[0],s,r['t']).abs().max()
                    z=v['query_x']@m['weight'].T+m['bias']
                    exact=((torch.logsumexp(z,1)-z.gather(1,v['query_y'][:,None]).squeeze(1))*v['query_mass']).sum()
                rows.append(dict(role_id=r['id'],arm=arm,finite_step_objective=float(obj),
                     converged_objective=log['objective'],objective_gap=float(obj)-log['objective'],
                     finite_step_gradient=float(grad),converged_gradient=log['max_gradient'],
                     finite_step_meta_CE=float(risk[0]),converged_meta_CE=float(exact),
                     meta_CE_gap=float(risk[0]-exact),solver_seconds=log['seconds'],accepted=log['accepted']))
                save(pd.DataFrame(rows),OUT/'pilot/surrogate-gap.parquet')
                progress('converged_source_reference',fits=len(rows),cap=24)
        write(OUT/'pilot/converged-reference-completion.json',dict(passed=True,new_classifier_fits=len(rows),target_numeric_reads=0))

if __name__=='__main__':
    {'gradients':gradient_checks,'reference':converged_reference}[sys.argv[1]]()
