"""Weighted blockwise inverse Ridge, alpha=1, intercept unpenalized."""
from common import *

def fit_inverse(z,t,w):
    out={};errors=[]
    for j in range(10):
        x=z[:,block(j)];a=t[:,block(j)];xm=(w[:,None]*x).sum(0);am=(w[:,None]*a).sum(0)
        xc=x-xm;ac=a-am;cov=xc.T@(w[:,None]*xc);cross=ac.T@(w[:,None]*xc)
        h=cov+torch.eye(SIZES[j],device='cuda',dtype=torch.float64);L=torch.linalg.cholesky(h)
        M=torch.cholesky_solve(cross.T,L).T;c=am-M@xm
        err=float((M@h-cross).norm()/cross.norm().clamp_min(1));require(err<=1e-10,'Ridge normalized linear residual')
        # Independent original objective gradient, including /10 and alpha.
        Mw=M.detach().clone().requires_grad_();cw=c.detach().clone().requires_grad_()
        loss=((F.linear(x,Mw,cw)-a).square().sum(1)*w).sum()/10+Mw.square().sum()/10
        gm,gc=torch.autograd.grad(loss,(Mw,cw));gerr=max(float(gm.abs().max()),float(gc.abs().max()))
        require(gerr<=1e-10,'Ridge independent gradient')
        out[f'M{j}']=M.detach();out[f'c{j}']=c.detach();errors.append(dict(block=j,residual=err,gradient=gerr))
    return out,errors
def forward(z,s):return torch.cat([F.linear(z[:,block(j)],s[f'M{j}'],s[f'c{j}']) for j in range(10)],1)
