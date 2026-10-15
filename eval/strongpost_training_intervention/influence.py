"""Original-coordinate Hessian; remove only unpenalized common-bias gauge."""
from common import *
import objectives as O

def basis():
    q=torch.zeros((6,5),device=device(),dtype=torch.float64)
    for j in range(5):
        den=((j+1)*(j+2))**.5;q[:j+1,j]=1/den;q[j+1,j]=-(j+1)/den
    return q

def encode(model,q):return torch.cat([model['weight'].reshape(-1),q.T@model['bias']])
def decode(z,q):return {'weight':z[:576].reshape(6,96),'bias':q@z[576:]}
def pack_gradient(g,q):return torch.cat([g[0].reshape(-1),q.T@g[1]])

def hessian(model,s,t,q):
    x=s['x'];p=torch.softmax(x@model['weight'].T+model['bias'],1)
    cov=torch.diag_embed(p)-p[:,:,None]*p[:,None,:]
    cov=cov*s['mass'][:,None,None]
    ww=torch.einsum('nab,ni,nj->aibj',cov,x,x).reshape(576,576)
    ww=ww+torch.eye(576,device=device(),dtype=torch.float64)*(.001*(1+t))
    wb=torch.einsum('nab,ni,bk->aik',cov,x,q).reshape(576,5)
    bb=q.T@cov.sum(0)@q
    return torch.cat([torch.cat([ww,wb],1),torch.cat([wb.T,bb],1)],0)

def auto_hessian(model,s,t,q):
    z=encode(model,q).detach().requires_grad_()
    return torch.autograd.functional.hessian(lambda zz:O.loss(decode(zz,q),s,t),z,vectorize=True)

def directions(r,v,model,check_autograd=False):
    started=time.perf_counter();q=basis();m=O.normalized_model(model);s=O.slot(v,'P',0.)
    H=hessian(m,s,r['t'],q)
    require(residual(H,H.T)<=1e-12,'Hessian symmetry')
    ha=auto_hessian(m,s,r['t'],q) if check_autograd else None
    if ha is not None:require(residual(H,ha)<=1e-10,'Analytic/autograd Hessian')
    z=encode(m,q).detach().requires_grad_();ag=torch.autograd.grad(O.loss(decode(z,q),s,r['t']),z)[0]
    g0=pack_gradient(O.gradient(m,s,r['t']),q)
    require(residual(ag,g0)<=1e-10,'Analytic/autograd gradient')
    dg=[]
    gs=O.gradient(m,O.auxiliary(v,'S'),r['t'],False)
    for a in ['P','G']:
        gm=O.gradient(m,O.auxiliary(v,a),r['t'],False)
        dg.append(pack_gradient((gm[0]-gs[0],gm[1]-gs[1]),q))
    rhs=torch.stack([g0,*dg],1);chol=torch.linalg.cholesky(H)
    sol=torch.cholesky_solve(rhs,chol)
    equation=residual(H@sol,rhs);require(equation<=1e-10,'Hessian equation residual')
    eig=torch.linalg.eigvalsh(H)
    data={'q':q,'H':H,'cholesky':chol,'base':encode(m,q).detach(),'g0':g0,'e0':-sol[:,0],
          'delta_P':dg[0],'delta_G':dg[1],'d_P':-sol[:,1],'d_G':-sol[:,2]}
    log={'role_id':r['id'],'dimension':581,'gradient_inf':float(g0.abs().max()),
         'stationarity_displacement_norm':float(sol[:,0].norm()),'linear_system_residual':equation,
         'hessian_symmetry_residual':residual(H,H.T),'hessian_autograd_residual':None if ha is None else residual(H,ha),
         'gradient_autograd_residual':residual(ag,g0),'eigen_min':float(eig.min()),'eigen_max':float(eig.max()),
         'condition_number':float(eig.max()/eig.min()),'seconds':time.perf_counter()-started,
         'cuda_peak_MiB':torch.cuda.max_memory_allocated()/1048576,'device':'cuda:0','dtype':'float64',
         'jitter':0,'new_bias_regularization':0}
    return data,log
