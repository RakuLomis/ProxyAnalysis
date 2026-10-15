from common import *

def basis():
    q=torch.zeros((6,5),device=device(),dtype=torch.float64)
    for j in range(5):
        v=((j+1)*(j+2))**-.5;q[:j+1,j]=v;q[j+1,j]=-(j+1)*v
    return q
def projected(a,b,q):return q@a,q@b
def logits(a,b,phi,z0,q):
    d,e=projected(a,b,q);return z0+phi@d.T+e
def objective(a,b,phi,z0,y,mass,eta,q):
    z=logits(a,b,phi,z0,q)
    return (F.cross_entropy(z,y,reduction='none')*mass).sum()+eta*a.square().sum()
def independent(a,b,phi,z0,y,mass,eta,q):
    d,e=projected(a,b,q);z=z0+phi@d.T+e
    ce=(mass*(torch.logsumexp(z,1)-z.gather(1,y[:,None]).squeeze(1))).sum()
    reg=eta*d.square().sum();err=(torch.softmax(z,1)-F.one_hot(y,6).double())*mass[:,None]
    gd=err.T@phi+2*eta*d;ge=err.sum(0)
    gd=gd-gd.mean(0);ge=ge-ge.mean()
    ga=q.T@gd;gb=q.T@ge
    return dict(objective=ce+reg,CE=ce,L2=reg,ga=ga,gb=gb,gd=gd,ge=ge)
