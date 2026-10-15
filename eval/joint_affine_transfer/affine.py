"""Common 96-coordinate objective. Group loss retains all input variance."""
from common import *

def data_moments(x,y,w):
    require(x.is_cuda and y.is_cuda and x.dtype==torch.float64,'CUDA float64 mapping required')
    require(x.shape==y.shape and x.shape[1]==96 and abs(float(w.sum())-1)<1e-12,'Mapping shape/mass')
    require(torch.isfinite(x).all() and torch.isfinite(y).all() and (w>0).all(),'Invalid mapping values')
    mx=(x*w[:,None]).sum(0); my=(y*w[:,None]).sum(0)
    xc=x-mx; yc=y-my
    return mx,my,xc.T@(xc*w[:,None]),yc.T@(xc*w[:,None])

def group_targets(pre,post):
    group_schema(pre); group_schema(post)
    require(set(pre.content_token)==set(post.content_token),'Group content mismatch')
    pp=post.groupby('content_token',sort=True)
    centers={}; variance=0.
    for token,d in pp:
        mass=float(d.fit_mass.sum()); z=tensor(d[HIST]); local=tensor(d.fit_mass)/mass
        mean=(z*local[:,None]).sum(0); centers[token]=mean
        variance += float((local[:,None]*(z-mean).square()).sum())*mass
    yy=torch.stack([centers[t] for t in pre.content_token])
    require(abs(float(pre.fit_mass.sum())-1)<1e-12 and abs(float(post.fit_mass.sum())-1)<1e-12,'Group mass')
    for token,d in pre.groupby('content_token'):
        require(abs(float(d.fit_mass.sum())-float(pp.get_group(token).fit_mass.sum()))<1e-12,'Group marginal mass')
    return yy,variance

def objective_parts(m,b,x,y,w,alpha,constant=0.):
    recovery=((x@m.T+b-y).square()*w[:,None]).sum()/96+constant/96
    reg=alpha*(m-torch.eye(96,device=x.device,dtype=x.dtype)).square().sum()/96
    return recovery,reg

def fit(x,y,w,eta,arm,constant=0.):
    started=time.perf_counter(); mx,my,sxx,syx=data_moments(x,y,w)
    tau=max(float(sxx.trace())/96,1e-12); alpha=eta*tau
    identity=torch.eye(96,device=device(),dtype=torch.float64)
    m=torch.zeros_like(identity); ranges=[block(j) for j in range(10)] if arm=='JA0' else [slice(0,96)]
    residual=0.
    for sl in ranges:
        a=sxx[sl,sl]+alpha*identity[sl,sl]; right=syx[sl,sl]+alpha*identity[sl,sl]
        chol=torch.linalg.cholesky(a)
        sol=torch.cholesky_solve(right.T,chol).T; m[sl,sl]=sol
        norm=float((sol@a-right).abs().max())/max(1.,float(right.abs().max()))
        residual=max(residual,norm)
    b=my-m@mx
    mm=m.clone().requires_grad_(); bb=b.clone().requires_grad_()
    rec,reg=objective_parts(mm,bb,x,y,w,alpha,constant)
    gm,gb=torch.autograd.grad(rec+reg,(mm,bb))
    mask=torch.ones_like(m,dtype=torch.bool)
    if arm=='JA0':
        mask.zero_()
        for sl in ranges: mask[sl,sl]=True
    # Independent moment-form objective and analytic gradient in original coordinates.
    yy=(y*y*w[:,None]).sum()
    rawxx=sxx+mx[:,None]*mx[None,:]; rawyx=syx+my[:,None]*mx[None,:]
    replay=(torch.trace(m@rawxx@m.T)+2*b@(m@mx)+(b*b).sum()-2*(m*rawyx).sum()
            -2*b@my+yy+constant+alpha*(m-identity).square().sum())/96
    agm=2*((m@rawxx+b[:,None]*mx[None,:]-rawyx)+alpha*(m-identity))/96
    agb=2*(m@mx+b-my)/96
    gerr=max(float((agm[mask]-gm[mask]).abs().max()),float((agb-gb).abs().max()))
    error=abs(float(replay)-float(rec+reg)); gradient=max(float(gm[mask].abs().max()),float(gb.abs().max()))
    eig=torch.linalg.eigvalsh(sxx+alpha*identity)
    log={'eta':eta,'arm':arm,'tau':tau,'alpha':alpha,'objective':float((rec+reg).detach()),
        'recovery':float(rec.detach()),'regularization':float(reg.detach()),'group_constant':constant,
        'gradient_max':gradient,'objective_replay_error':error,'gradient_replay_error':gerr,
        'normalized_equation_residual':residual,'eigen_min':float(eig.min()),'eigen_max':float(eig.max()),
        'seconds':time.perf_counter()-started,'device':'cuda:0','dtype':'float64',
        'parameters':1020 if arm=='JA0' else 9312}
    log['accepted']=bool(gradient<=1e-8 and error<1e-10 and gerr<1e-10 and residual<=1e-10
                         and torch.isfinite(m).all() and torch.isfinite(b).all())
    require(log['accepted'],'Affine original-coordinate precision gate failed: '+str(log))
    return {'matrix':m.detach(),'bias':b.detach(),'pre_mean':mx,'post_mean':my,
            'sxx':sxx,'syx':syx,'alpha':torch.tensor(alpha,device=device(),dtype=torch.float64),
            'tau':torch.tensor(tau,device=device(),dtype=torch.float64)},log

def apply(model,x):
    require(x.is_cuda and x.dtype==torch.float64,'CUDA inference required')
    with torch.no_grad(): y=x@model['matrix'].T+model['bias']
    require(torch.isfinite(y).all(),'Nonfinite adapted vector')
    return y
