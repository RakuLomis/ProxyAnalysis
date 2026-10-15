"""Exact class-contrast reduction; the penalized common W optimum is zero."""
from common import *

def basis():
    e=torch.zeros((6,5),device=device(),dtype=torch.float64)
    for j in range(5):
        den=((j+1)*(j+2))**.5
        e[:j+1,j]=1/den; e[j+1,j]=-(j+1)/den
    require(float((e.T@e-torch.eye(5,device=device(),dtype=torch.float64)).abs().max())<1e-14,'Helmert orthogonality')
    return e

def encode(theta,e,inv): return torch.linalg.solve(inv.T,(e.T@theta).T).T
def decode(v,e,inv): return e@(v@inv)
def augmented(s): return torch.cat([s['x'],torch.ones_like(s['x'][:,:1])],1)

def objective(v,s,t,e,inv):
    theta=decode(v,e,inv); z=s['x']@theta[:,:96].T+theta[:,96]
    return (s['mass']*F.cross_entropy(z,s['y'],reduction='none')).sum()+.0005*(1+t)*theta[:,:96].square().sum()

def raw_gradient(theta,s,t):
    z=s['x']@theta[:,:96].T+theta[:,96]
    residual=(torch.softmax(z,1)-F.one_hot(s['y'],6))*s['mass'][:,None]
    return torch.cat([residual.T@s['x']+.001*(1+t)*theta[:,:96],residual.sum(0)[:,None]],1)

def gradient(theta,s,t,e,inv): return (e.T@raw_gradient(theta,s,t))@inv.T

def hessian(theta,s,t,e,inv):
    cuda(theta,s['x'],s['mass'],e,inv)
    p=torch.softmax(augmented(s)@theta.T,1)
    cov=torch.diag_embed(p)-p[:,:,None]*p[:,None,:]
    small=torch.einsum('ak,nab,bl->nkl',e,cov,e)*s['mass'][:,None,None]
    z=augmented(s)@inv.T
    h=torch.einsum('nab,ni,nj->aibj',small,z,z).reshape(485,485)
    reg=inv[:,:96]@inv[:,:96].T*.001*(1+t)
    h=h+torch.einsum('ab,ij->aibj',torch.eye(5,device=device(),dtype=torch.float64),reg).reshape(485,485)
    return h

def audit(theta,s,t,e,inv):
    v=encode(theta,e,inv).detach().requires_grad_(); decoded=decode(v,e,inv)
    value=objective(v,s,t,e,inv); auto=torch.autograd.grad(value,v)[0]
    raw=raw_gradient(decoded.detach(),s,t)
    err=float((auto-(e.T@raw)@inv.T).abs().max())
    # Independent logsumexp target, including L2 on original W only.
    z=s['x']@decoded[:,:96].T+decoded[:,96]
    j=(s['mass']*(torch.logsumexp(z,1)-z.gather(1,s['y'][:,None]).squeeze(1))).sum()+.0005*(1+t)*decoded[:,:96].square().sum()
    je=abs(float(j.detach()-value.detach()))
    require(je<1e-10 and err<1e-10,'Original-coordinate target/gradient replay')
    return dict(objective_error=je,gradient_error=err,original_gradient=float(raw.abs().max()))

def synthetic_tests():
    configure(); e=basis()
    inv=torch.eye(97,device=device(),dtype=torch.float64)*1.3
    inv=inv+torch.tril(torch.full_like(inv,.0003),diagonal=-1)
    x=torch.sin(torch.arange(12*96,device=device(),dtype=torch.float64).reshape(12,96)/17)/3
    s=dict(x=x,y=torch.arange(12,device=device())%6,mass=torch.full((12,),1/12,device=device(),dtype=torch.float64))
    theta=torch.cos(torch.arange(582,device=device(),dtype=torch.float64).reshape(6,97)/37)/100
    v=encode(theta,e,inv); dec=decode(v,e,inv)
    old=augmented(s)@theta.T; new=augmented(s)@dec.T
    require(float((torch.softmax(old,1)-torch.softmax(new,1)).abs().max())<1e-12,'Class-common removal changed probability')
    expected=.0005*6*theta[:,:96].mean(0).square().sum()
    oldj=(s['mass']*F.cross_entropy(old,s['y'],reduction='none')).sum()+.0005*theta[:,:96].square().sum()
    require(abs(float(oldj-objective(v,s,0.,e,inv)-expected))<1e-12,'Common W analytical minimization')
    h=hessian(dec,s,0.,e,inv)
    ah=torch.autograd.functional.hessian(lambda z:objective(z.reshape(5,97),s,0.,e,inv),v.flatten(),vectorize=True)
    err=float((h-ah).norm()/h.norm().clamp_min(1))
    require(err<1e-10,'Synthetic analytical Hessian')
    a=audit(dec,s,0.,e,inv)
    try: cuda(torch.ones(2))
    except RuntimeError: pass
    else: raise RuntimeError('CPU negative accepted')
    # Validate the mixed derivative with independent AD of the original objective.
    from implicit import mixed
    amp,unroll,oracle,soft=production()
    view=dict(main_x=x,main_y=s['y'],main_mass=s['mass']*4/12,
              S_x=x*.8,S_y=s['y'],S_mass=s['mass']*4/12,
              pre_x=x*.9,pre_y=s['y'],pre_mass=s['mass']*4/12,
              mapped_x=x*.9+torch.cos(x)/20,
              C_x=x[:6],C_y=s['y'][:6],C_mass=s['mass'][:6]*8/12)
    q=tensor([.9,1.1]*5); slot=unroll.pack(view,'synthetic',q)
    mm=mixed(dec,slot,view,e,inv)
    def train_gradient(qq):
        z=v.detach().clone().requires_grad_()
        return torch.autograd.grad(objective(z,unroll.pack(view,'synthetic',qq),0.,e,inv),z,create_graph=True)[0].flatten()
    ma=torch.autograd.functional.jacobian(train_gradient,q,vectorize=True)
    me=float((mm-ma).norm()/mm.norm().clamp_min(1))
    require(me<1e-10,'Synthetic mixed derivative')
    result=dict(passed=True,hessian_error=err,mixed_error=me,CPU_negative_passed=True,**a)
    print(result,flush=True)
    return result

if __name__=='__main__': synthetic_tests()
