"""Implicit solution derivative, independent analytic mixed derivative and AD."""
from common import *
import gauge as G

def mixed(theta,s,view,e,inv):
    x=s['x']; aug=G.augmented(s); p=torch.softmax(aug@theta.T,1)
    residual=(p-F.one_hot(s['y'],6))*s['mass'][:,None]
    n=len(view['main_x'])+len(view['S_x']); m=len(view['pre_x']); cols=[]
    for j in range(10):
        dx=torch.zeros_like(x)
        dx[n:n+m,block(j)]=view['mapped_x'][:,block(j)]-view['pre_x'][:,block(j)]
        da=torch.cat([dx,torch.zeros_like(dx[:,:1])],1)
        dl=da@theta.T
        dp=p*(dl-(p*dl).sum(1,keepdim=True))
        dg=(dp*s['mass'][:,None]).T@aug+residual.T@da
        cols.append(((e.T@dg)@inv.T).flatten())
    return torch.stack(cols,1)

def evaluate(r,arm,ep):
    a,u,o,rr=production(); view=task(r,arm)['view']; q=ep['q']; s=u.pack(view,arm,q)
    e=ep['e']; inv=ep['inv']; theta=ep['theta']; v0=G.encode(theta,e,inv).detach()
    h=G.hessian(theta,s,r['t'],e,inv)
    ah=torch.autograd.functional.hessian(lambda z:G.objective(z.reshape(5,97),s,r['t'],e,inv),v0.flatten(),vectorize=True)
    he=float((h-ah).norm()/h.norm().clamp_min(1)); sym=float((h-h.T).norm()/h.norm().clamp_min(1))
    require(he<=1e-10 and sym<=1e-12,'Implicit Hessian verification failed')
    # Query is fixed, only parameters receive this gradient.
    vv=v0.clone().requires_grad_(); query=view['query_x']; qa=torch.cat([query,torch.ones_like(query[:,:1])],1)
    logits=qa@G.decode(vv,e,inv).T
    risk=(view['query_mass']*F.cross_entropy(logits,view['query_y'],reduction='none')).sum()
    g=torch.autograd.grad(risk,vv)[0].flatten().detach()
    ch=torch.linalg.cholesky(h)
    vec=torch.cholesky_solve(g[:,None],ch).flatten()
    lu=torch.linalg.solve(h,g)
    res=float((h@vec-g).norm()/g.norm().clamp_min(1e-12))
    absolute_residual=float((h@vec-g).norm())
    require(res<=1e-10,'Implicit linear residual failed')
    mm=mixed(theta,s,view,e,inv)
    grad=-(mm.T@vec); gold=-(mm.T@lu)
    tol=1e-6+1e-3*torch.maximum(grad.abs(),gold.abs())
    require(bool(((grad-gold).abs()<=tol).all()),'Independent linear-solve gradient disagreement')
    # Partial theta-q derivative: endpoints and vec are constants, q is the sole variable.
    qauto=q.detach().clone().requires_grad_(); z=v0.clone().requires_grad_()
    sq=u.pack(view,arm,qauto)
    j=G.objective(z,sq,r['t'],e,inv)
    train_grad=torch.autograd.grad(j,z,create_graph=True)[0]
    auto=-torch.autograd.grad((train_grad.flatten()*vec.detach()).sum(),qauto)[0]
    require(bool(((grad-auto).abs()<=1e-6+1e-3*torch.maximum(grad.abs(),auto.abs())).all()),'Mixed VJP disagreement')
    eig=torch.linalg.eigvalsh(h)
    require(float(eig.min())>0,'Nonpositive reduced Hessian')
    condition=float(eig.max()/eig.min())
    # Linear response to residual is diagnostic, not a global accuracy bound.
    residual_gradient=G.gradient(theta,s,r['t'],e,inv).flatten()
    displacement=torch.cholesky_solve(residual_gradient[:,None],ch).flatten()
    meta=dict(hessian_error=he,symmetry=sym,linear_residual=res,linear_absolute=absolute_residual,
              independent_solve_error=float((grad-gold).abs().max()),mixed_VJP_error=float((grad-auto).abs().max()),
              eigen_min=float(eig.min()),eigen_max=float(eig.max()),condition=condition,
              precision_risk=condition*np.finfo(float).eps>=.01,v_norm=float(vec.norm()),
              stationarity_response_norm=float(displacement.norm()),risk_response_proxy=abs(float(g@displacement)),
              original_gradient=ep['original_gradient'],Q=float(ep['Q']),passed=True)
    return dict(gradient=grad.detach(),auto_gradient=auto.detach(),LU_gradient=gold.detach(),**meta)

def stability(lo,hi):
    diff=(lo['gradient']-hi['gradient']).abs()
    lim=1e-6+1e-3*torch.maximum(lo['gradient'].abs(),hi['gradient'].abs())
    return bool((diff<=lim).all()),float(diff.max())
