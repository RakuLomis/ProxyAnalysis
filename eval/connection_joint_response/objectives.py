"""Dimension-generic v4 coordinates, unchanged CE/L2 and local LBFGS policy."""
from common import *

_step = None
def step_reference():
    global _step
    if _step is None:_step=module('cj_local_v4_step',ROOT/'eval/calibrated_deployment_transfer_v4/optimizer_preconditioning.py')
    return _step

def original(theta,x,y,mass,t):
    with torch.enable_grad():
        w=theta[:,:-1].detach().clone().requires_grad_(); b=theta[:,-1].detach().clone().requires_grad_()
        logits=x@w.T+b
        value=(mass*(torch.logsumexp(logits,1)-logits.gather(1,y[:,None]).squeeze(1))).sum()+.0005*(1+t)*w.square().sum()
        gw,gb=torch.autograd.grad(value,(w,b))
    return value.detach(),torch.cat([gw,gb[:,None]],1)

def fit(x,y,mass,t,context):
    require(x.is_cuda and x.dtype==torch.float64,'CUDA float64 classifier required')
    require(x.shape[1] in [96,162] and (mass>0).all() and abs(float(mass.sum())-1)<1e-12,'Coordinates/mass')
    require(float((weighted(y,mass,6)-1/6).abs().max())<1e-12,'Class weights changed')
    d=x.shape[1]; ref=step_reference(); started=time.perf_counter(); record={}; calls=0; heartbeat=started
    a=torch.cat([x,torch.ones((len(x),1),device=device(),dtype=torch.float64)],1)
    curvature=a.T@(a*mass[:,None])/6+torch.diag(torch.cat([
        torch.full((d,),.001*(1+t),device=device(),dtype=torch.float64),torch.zeros(1,device=device(),dtype=torch.float64)]))
    l=torch.linalg.cholesky(curvature); ax=torch.linalg.solve_triangular(l,a.T,upper=False).T
    v=torch.nn.Parameter(torch.zeros((6,d+1),device=device(),dtype=torch.float64))
    def decode():return torch.linalg.solve_triangular(l.T,v.T,upper=True).T
    def loss():
        z=ax@v.T
        return (F.cross_entropy(z,y,reduction='none')*mass).sum()+.0005*(1+t)*decode()[:,:d].square().sum()
    initial=float(loss().detach()); opt=torch.optim.LBFGS([v],**ref.SETTINGS)
    def converge(flat):
        chain=flat.reshape(6,d+1)@l.T
        record['current_original_gradient_proxy']=float(chain.abs().max())
        require(torch.isfinite(chain).all(),'Nonfinite original gradient proxy')
        if float(chain.abs().max())>1e-5:return False
        record['original_audit_evaluations']=record.get('original_audit_evaluations',0)+1
        _,gradient=original(decode(),x,y,mass,t)
        require(float((gradient-chain).abs().max())<1e-10,'Original gradient chain mismatch')
        return float(gradient.abs().max())<=1e-5
    ref.install_local_step(opt,record,converge)
    def closure():
        nonlocal calls,heartbeat
        calls+=1; opt.zero_grad(); value=loss(); require(torch.isfinite(value),'Nonfinite classifier objective')
        value.backward(); require(torch.isfinite(v.grad).all(),'Nonfinite transformed gradient')
        if time.perf_counter()-heartbeat>=45:
            progress('classifier_heartbeat',**context,t=t,evaluations=calls,iterations=int(opt.state[v].get('n_iter',0)))
            heartbeat=time.perf_counter()
        return value
    try:
        opt.step(closure); value=float(closure().detach()); theta=decode().detach()
        replay,gradient=original(theta,x,y,mass,t)
        error=abs(float(replay)-value); gerror=float((gradient-v.grad@l.T).abs().max())
        iterations=int(opt.state[v].get('n_iter',0)); maximum=float(gradient.abs().max())
        gates=acceptance_gates(float(replay),initial,maximum,iterations,error,gerror)
        log={**context,'solver':SOLVER,'dimensions':d,'parameters':6*(d+1),'settings':ref.SETTINGS,
             'numeric_policy_sha256':sha(OUT/'manifests/numeric-policy.json'),'initialization':'zero',
             'initial_objective':initial,'objective':float(replay),'max_gradient':maximum,'iterations':iterations,
             'function_evaluations':int(opt.state[v].get('func_evals',0)),'closure_evaluations':calls,
             'objective_replay_error':error,'gradient_replay_error':gerror,'gates':gates,'actual_optimizer_break':record,
             'seconds':time.perf_counter()-started,'device':'cuda:0','dtype':'float64',
             'cuda_peak_MiB':torch.cuda.max_memory_allocated()/1048576,
             'accepted':all(gates.values()) and record.get('reason') not in ['non_descent_failure','unchanged_parameter_failure']}
        write(OUT/'fit-logs'/context['role_id']/f'{context["arm"]}-t{t:g}.json',log)
        require(log['accepted'],'Original-coordinate numerical gate failed; no budget extension')
        return {'weight':theta[:,:d],'bias':theta[:,d]},log
    except BaseException as exc:
        p=OUT/'failures'/context['role_id']/f'{context["arm"]}-t{t:g}.json'
        write(p,{'exception':str(exc),'settings':ref.SETTINGS,'record':record,'seconds':time.perf_counter()-started})
        raise
