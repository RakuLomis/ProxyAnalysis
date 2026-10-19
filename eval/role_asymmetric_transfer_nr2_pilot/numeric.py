"""Original objective, all W retained, mean-bias gauge, exact Hessian Newton."""
from common import *

def basis():
    q=torch.zeros((6,5),device=dev(),dtype=torch.float64)
    for j in range(5):
        den=((j+1)*(j+2))**.5;q[:j+1,j]=1/den;q[j+1,j]=-(j+1)/den
    require(float((q.T@q-torch.eye(5,device=dev(),dtype=torch.float64)).abs().max())<1e-14,'Q orthogonality')
    return q
def encode(theta):
    cuda(theta);finite(theta);q=basis();return torch.cat([theta[:,:96].flatten(),q.T@theta[:,96]]),theta[:,96].mean()
def decode(u,kappa):
    cuda(u);return torch.cat([u[:576].reshape(6,96),(basis()@u[576:]+kappa)[:,None]],1)
def value(theta,s,t):
    cuda(theta,s['x'],s['mass']);z=s['x']@theta[:,:96].T+theta[:,96]
    return (s['mass']*(z.logsumexp(1)-z.gather(1,s['y'][:,None]).squeeze(1))).sum()+.0005*(1+t)*theta[:,:96].square().sum()
def raw_gradient(theta,s,t):
    z=s['x']@theta[:,:96].T+theta[:,96]
    e=(z.softmax(1)-F.one_hot(s['y'],6))*s['mass'][:,None]
    return torch.cat([e.T@s['x']+.001*(1+t)*theta[:,:96],e.sum(0)[:,None]],1)
def gradient(theta,s,t):
    g=raw_gradient(theta,s,t);return torch.cat([g[:,:96].flatten(),basis().T@g[:,96]])
def hessian(theta,s,t):
    cuda(theta,s['x'],s['mass']);x=s['x'];m=s['mass'];q=basis()
    p=(x@theta[:,:96].T+theta[:,96]).softmax(1)
    cov=torch.diag_embed(p)-p[:,:,None]*p[:,None,:]
    ww=torch.einsum('nij,na,nb,n->iajb',cov,x,x,m).reshape(576,576)
    ww=ww+torch.eye(576,device=dev(),dtype=torch.float64)*(.001*(1+t))
    wb=torch.einsum('nij,jk,na,n->iak',cov,q,x,m).reshape(576,5)
    bb=torch.einsum('ij,njk,kl,n->il',q.T,cov,q,m)
    return torch.cat([torch.cat([ww,wb],1),torch.cat([wb.T,bb],1)],0)
def audit(theta,s,t):
    j=value(theta,s,t);g=raw_gradient(theta,s,t)
    a=theta.detach().clone().requires_grad_();z=s['x']@a[:,:96].T+a[:,96]
    aj=(F.cross_entropy(z,s['y'],reduction='none')*s['mass']).sum()+.0005*(1+t)*a[:,:96].square().sum()
    ag=torch.autograd.grad(aj,a)[0]
    oe=abs(float(j)-float(aj.detach()));ge=float((g-ag).abs().max())
    require(oe<1e-10 and ge<1e-10,'Original-coordinate replay')
    return dict(objective=float(j),max_gradient=float(g.abs().max()),objective_replay_error=oe,gradient_replay_error=ge)
def direction(h,g):
    guard();cuda(h,g);finite(h,g)
    sym=float(torch.linalg.matrix_norm(h-h.T,ord=float('inf'))/torch.linalg.matrix_norm(h,ord=float('inf')).clamp_min(1))
    require(sym<=1e-12,'Hessian asymmetry');h=(h+h.T)/2
    scale=max(1.,float(h.diag().abs().max()));tries=[];eye=torch.eye(len(g),device=dev(),dtype=torch.float64)
    for ratio in [0.,1e-12,1e-10,1e-8,1e-6]:
        guard();mu=ratio*scale;a=h+mu*eye;chol,info=torch.linalg.cholesky_ex(a)
        row=dict(mu=mu,relative_mu=ratio,cholesky_info=int(info));tries.append(row)
        if int(info):continue
        p=-torch.cholesky_solve(g[:,None],chol).squeeze(1);finite(p)
        res=float((a@p+g).abs().max()/g.abs().max().clamp_min(1e-30));gtd=float(g@p)
        row.update(linear_relative_residual=res,gtd=gtd,undamped_relative_residual=float((h@p+g).abs().max()/g.abs().max().clamp_min(1e-30)))
        if res<=1e-10 and gtd<0:return p,dict(symmetry_error=sym,damping_attempts=tries,**row)
    raise RuntimeError('Bounded Newton factor/direction policy failed: '+json.dumps(tries))
def search(u,p,current,gtd,objective,counter):
    for i in range(25):
        guard();require(counter['optimization_evaluations']<20000,'Newton evaluation budget')
        alpha=.5**i;candidate=u+alpha*p
        if torch.equal(candidate,u):continue
        counter['optimization_evaluations']+=1
        j=objective(candidate);finite(j)
        if float(j)<current and float(j)<=current+1e-4*alpha*gtd:
            return candidate.detach(),dict(step=alpha,line_candidates=i+1,objective=float(j))
    raise RuntimeError('newton_line_search_failed')
def refine(theta,s,t,limit,log,counter,tag):
    u,kappa=encode(theta);starttheta=theta.clone();theta=decode(u,kappa)
    require(torch.equal(theta[:,:96],starttheta[:,:96]),'Common W must remain unchanged')
    require(abs(float(value(theta,s,t)-value(starttheta,s,t)))<1e-10,'Gauge objective changed')
    require(float((raw_gradient(theta,s,t)-raw_gradient(starttheta,s,t)).abs().max())<1e-10,'Gauge gradient changed')
    trace=[];log['newton_trace']=trace
    for n in range(limit+1):
        guard();theta=decode(u,kappa);j=value(theta,s,t);raw=raw_gradient(theta,s,t);finite(j,raw)
        row=dict(update=n,objective=float(j),max_gradient=float(raw.abs().max()));trace.append(row)
        log.update(newton_updates=n,**audit(theta,s,t))
        counter['independent_Newton_audit_passes']=counter.get('independent_Newton_audit_passes',0)+1
        # Per pass: one explicit value/gradient and audit's independent manual/AD pair.
        counter['nonoptimizer_Newton_value_evaluations']=counter.get('nonoptimizer_Newton_value_evaluations',0)+3
        counter['nonoptimizer_Newton_gradient_evaluations']=counter.get('nonoptimizer_Newton_gradient_evaluations',0)+3
        statepath=pathout(OUT/'latest-states'/f'{tag}.pt')
        torch.save(dict(theta=theta.detach(),u=u.detach(),kappa=kappa.detach(),counters=counter.copy()),statepath)
        write(OUT/'live'/f'{tag}.json',log)
        if float(raw.abs().max())<=1e-5:return theta,log
        require(n<limit,'Newton update limit exhausted')
        require(counter.get('lbfgs_updates',0)+n<3999,'Global strict update boundary')
        before=time.perf_counter();h=hessian(theta,s,t);g=gradient(theta,s,t);torch.cuda.synchronize()
        row['hessian_and_gradient_seconds']=time.perf_counter()-before
        before=time.perf_counter();p,di=direction(h,g);torch.cuda.synchronize();row['factor_and_solve_seconds']=time.perf_counter()-before
        row.update(**di);write(OUT/'live'/f'{tag}.json',log)
        before=time.perf_counter();u,ls=search(u,p,float(j),di['gtd'],lambda z:value(decode(z,kappa),s,t),counter)
        row['line_search_seconds']=time.perf_counter()-before
        row.update(**di,**{k:v for k,v in ls.items() if k!='objective'},candidate_objective=ls['objective'])
        counter['hessian_builds']=counter.get('hessian_builds',0)+1
        counter['factor_attempts']=counter.get('factor_attempts',0)+len(di['damping_attempts'])
    raise RuntimeError('Unreachable Newton exit')
