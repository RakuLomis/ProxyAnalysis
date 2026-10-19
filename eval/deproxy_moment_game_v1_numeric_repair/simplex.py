"""Euclidean simplex projection with saved active-set generalized derivative."""
from common import *

class Simplex(torch.autograd.Function):
    @staticmethod
    def forward(ctx,v):
        u=v.sort(dim=-1,descending=True).values;j=torch.arange(1,v.shape[-1]+1,device=v.device,dtype=v.dtype)
        # CUDA cumsum is rejected by deterministic mode in this installed torch.
        # A fixed upper-triangular prefix-sum matrix implements the same sums.
        n=v.shape[-1]
        css=u@torch.ones((n,n),device=v.device,dtype=v.dtype).triu()-1;rho=(u-css/j>0).sum(-1,keepdim=True)
        tau=css.gather(-1,rho-1)/rho;out=(v-tau).clamp_min(0)
        active=out>0;ctx.save_for_backward(active);return out
    @staticmethod
    def backward(ctx,g):
        active,=ctx.saved_tensors;masked=g*active
        return active*(g-masked.sum(-1,keepdim=True)/active.sum(-1,keepdim=True))

def project_blocks(a):return torch.cat([Simplex.apply(a[...,block(j)]) for j in range(10)],-1)
def valid(a):
    require(torch.isfinite(a).all(),'Nonfinite histogram')
    require(float(a.min())>=-1e-12,'Negative simplex output')
    require(max(float((a[...,block(j)].sum(-1)-1).abs().max()) for j in range(10))<=1e-10,'Simplex block sum')


