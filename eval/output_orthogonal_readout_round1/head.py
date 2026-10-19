"""Five-dimensional production projection and independent six-dimensional audit."""
from common import *

def basis():
    q=torch.zeros((6,5),device=device(),dtype=torch.float64)
    for j in range(5):
        v=((j+1)*(j+2))**-.5;q[:j+1,j]=v;q[j+1,j]=-(j+1)*v
    return q
def geometry(z0,q):
    require(z0.dtype==torch.float64 and bool(torch.isfinite(z0).all()),'Base logits nonfinite/precision')
    s=z0-z0.mean(1,keepdim=True);z=s@q
    return contrast_geometry(z,s)
def contrast_geometry(z,s):
    require(bool(torch.isfinite(z).all()) and bool(torch.isfinite(s).all()),'Nonfinite contrasts')
    norm=torch.linalg.vector_norm(z,dim=1);mask=norm>1e-12
    u=torch.zeros_like(z);u[mask]=z[mask]/norm[mask,None]
    return dict(s=s.detach(),u=u.detach(),mask=mask.detach(),norm=norm.detach())
def apply(h,geo):
    require(bool(torch.isfinite(h).all()),'Nonfinite residual')
    value=h-geo['u']*(h*geo['u']).sum(1,keepdim=True)
    return torch.where(geo['mask'][:,None],value,torch.zeros_like(value))
def logits(w,b,phi,z0,q,geo):
    h=phi@w.T+b;delta=apply(h,geo)@q.T
    return z0+delta,h,delta
def objective(w,b,phi,z0,y,mass,q,geo):
    z,_,_=logits(w,b,phi,z0,q,geo)
    return (mass*F.cross_entropy(z,y,reduction='none')).sum()+.01*w.square().sum()
def independent(w,b,phi,z0,y,mass,q):
    # Compute A in 6D independently; do not call production geometry/apply.
    s=z0-z0.mean(1,keepdim=True);n=torch.linalg.vector_norm(s@q,dim=1);mask=n>1e-12
    d=q@w;e=q@b;raw=phi@d.T+e
    corrected=raw-raw.mean(1,keepdim=True)
    norm2=s.square().sum(1);corrected[mask]-=s[mask]*(corrected[mask]*s[mask]).sum(1,keepdim=True)/norm2[mask,None]
    corrected[~mask]=0;z=z0+corrected
    ce=(mass*(torch.logsumexp(z,1)-z.gather(1,y[:,None]).squeeze(1))).sum();reg=.01*d.square().sum()
    err=(torch.softmax(z,1)-F.one_hot(y,6).double())*mass[:,None]
    pe=err-err.mean(1,keepdim=True)
    pe[mask]-=s[mask]*(pe[mask]*s[mask]).sum(1,keepdim=True)/norm2[mask,None];pe[~mask]=0
    gd=pe.T@phi+.02*d;ge=pe.sum(0)
    return dict(objective=ce+reg,CE=ce,L2=reg,gw=q.T@gd,gb=q.T@ge,gd=gd,ge=ge,logits=z)
def geometry_errors(s,delta,mask):
    norm=torch.linalg.vector_norm(delta,dim=1);sn=torch.linalg.vector_norm(s,dim=1)
    dot=(s*delta).sum(1).abs()/torch.maximum(torch.ones_like(norm),sn*norm)
    zero=delta.sum(1).abs()/torch.maximum(torch.ones_like(norm),norm)
    require(bool(torch.isfinite(delta).all()),'Nonfinite delta')
    require(float(dot.max())<=1e-10 and float(zero.max())<=1e-10,'Output orthogonality gate')
    require(bool((delta[~mask]==0).all()),'Near-zero correction must vanish exactly')
    return dict(max_relative_radial_error=float(dot.max()),max_relative_zero_sum_error=float(zero.max()),
                near_zero_rows=int((~mask).sum()),rows=len(delta))
def maxabs(x):return 0. if not x.numel() else float(x.abs().max())
