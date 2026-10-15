"""Disjoint raw-frequency balls and same-amplitude uniform control."""
from common import *

def project(a,b,rules,active=None):
    require(a.is_cuda and b.is_cuda and a.dtype==b.dtype==torch.float64,'CUDA float64 projection')
    require(a.shape==b.shape and a.shape[1]==96,'Projection shape')
    selected={v['block'] for v in rules if v['train_eligible']} if active is None else set(active)
    z=b.clone()
    for v in rules:
        j=v['block']
        if j not in selected:continue
        d=b[:,block(j)]-a[:,block(j)];norm=torch.linalg.vector_norm(d,dim=1)
        radius=np.sqrt(2.)*v['epsilon']
        factor=torch.ones_like(norm);nonzero=norm>0
        factor[nonzero]=torch.minimum(torch.ones_like(norm[nonzero]),radius/norm[nonzero])
        hit=norm>radius
        z[hit,block(j)]=a[hit,block(j)]+d[hit]*factor[hit,None]
    require(torch.isfinite(z).all(),'Nonfinite guard')
    return z
def uniform(a,b,z):
    den=torch.linalg.vector_norm(b-a,dim=1);num=torch.linalg.vector_norm(z-a,dim=1)
    g=torch.ones_like(den);nz=den>0;g[nz]=num[nz]/den[nz]
    require(float(g.min())>=-1e-12 and float(g.max())<=1+1e-12,'Uniform amplitude outside [0,1]')
    g=g.clamp(0,1);out=torch.where((g==1)[:,None],b,a+g[:,None]*(b-a))
    require(float((torch.linalg.vector_norm(out-a,dim=1)-num).abs().max())<1e-10,'Uniform amplitude mismatch')
    return out,g
