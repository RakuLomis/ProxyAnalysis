"""Exact inherited JA full affine objective, not a new calibration model."""
from common import *

def group_targets(a,b,ta,tb):
    centers={u:b[np.flatnonzero(np.asarray(tb)==u)].mean(0) for u in sorted(set(tb))}
    y=torch.stack([centers[u] for u in ta]);constant=0.
    for u,c in centers.items():
        ix=np.flatnonzero(np.asarray(tb)==u);constant+=float((b[ix]-c).square().sum())/len(b)
    return y,constant
def fit(x,y,eta,constant=0.):
    started=time.perf_counter();n,k=x.shape;require(k==96 and x.shape==y.shape and x.is_cuda,'Affine input')
    w=torch.full((n,),1/n,device=device(),dtype=torch.float64)
    mx=w@x;my=w@y;xc=x-mx;yc=y-my;sxx=xc.T@(xc*w[:,None]);syx=yc.T@(xc*w[:,None])
    tau=max(float(sxx.trace())/96,1e-12);alpha=eta*tau;eye=torch.eye(96,device=device(),dtype=torch.float64)
    eq=sxx+alpha*eye;right=syx+alpha*eye
    m=torch.cholesky_solve(right.T,torch.linalg.cholesky(eq)).T;b=my-m@mx
    mm=m.detach().clone().requires_grad_();bb=b.detach().clone().requires_grad_()
    rec=((x@mm.T+bb-y).square()*w[:,None]).sum()/96+constant/96
    reg=alpha*(mm-eye).square().sum()/96;gm,gb=torch.autograd.grad(rec+reg,(mm,bb))
    xx=sxx+mx[:,None]*mx;yx=syx+my[:,None]*mx
    replay=(torch.trace(m@xx@m.T)+2*b@(m@mx)+b.square().sum()-2*(m*yx).sum()-2*b@my
            +(y*y*w[:,None]).sum()+constant+alpha*(m-eye).square().sum())/96
    agm=2*(m@xx+b[:,None]*mx-yx+alpha*(m-eye))/96;agb=2*(m@mx+b-my)/96
    log={'eta':eta,'tau':tau,'alpha':alpha,'objective':float((rec+reg).detach()),'recovery':float(rec.detach()),
         'regularization':float(reg.detach()),'group_constant':constant,'parameters':9312,
         'gradient_max':max(float(gm.abs().max()),float(gb.abs().max())),
         'objective_replay_error':abs(float(replay)-float((rec+reg).detach())),
         'gradient_replay_error':max(float((agm-gm).abs().max()),float((agb-gb).abs().max())),
         'normalized_equation_residual':float((m@eq-right).abs().max())/max(1.,float(right.abs().max())),
         'device':'cuda:0','dtype':'float64','seconds':time.perf_counter()-started}
    log['accepted']=log['gradient_max']<=1e-8 and log['objective_replay_error']<1e-10 and log['gradient_replay_error']<1e-10 and log['normalized_equation_residual']<=1e-10
    require(log['accepted'],'Affine numerical acceptance failed: '+str(log))
    return {'matrix':m.detach(),'bias':b.detach()},log

def apply(m,x):
    y=x@m['matrix'].T+m['bias'];require(torch.isfinite(y).all(),'Nonfinite map');return y
