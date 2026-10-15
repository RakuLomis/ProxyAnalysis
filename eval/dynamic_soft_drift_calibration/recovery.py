"""Own-arm quadratic recovery and shared anonymous population variance."""
from common import *
from amplitude import adjust

def coefficients(a,b0,b,w,variance=None):
    delta0=b0-a;delta=b-a
    A=[];B=[];C=[]
    for j in range(10):
        sl=block(j);A.append((w[:,None]*delta0[:,sl].square()).sum()/size(j))
        B.append((w[:,None]*delta0[:,sl]*delta[:,sl]).sum()/size(j))
        C.append((w[:,None]*delta[:,sl].square()).sum()/size(j))
    C=torch.stack(C)
    if variance is not None: C=C+variance
    return {'A':torch.stack(A),'B':torch.stack(B),'C':C}

def anonymous_variance(b,w):
    mean=(b*w[:,None]).sum(0)
    raw=torch.stack([(w[:,None]*(b[:,block(j)]-mean[block(j)]).square()).sum()/size(j) for j in range(10)])
    return raw.clamp_min(1e-6),raw

def gap(q,c): return (q-1)*(c['A']*(q+1)-2*c['B'])/c['s']
def error(q,c): return c['A']*q.square()-2*c['B']*q+c['C']
def soft(q,c):
    g=gap(q,c);lam=g.clamp_min(0)
    return lam.square().mean(-1)/2,lam,g

def explicit_error(a,b0,b,w,q):
    e=(adjust(a,b0,q)-b).square()
    return torch.stack([(e[:,block(j)]*w[:,None]).sum()/size(j) for j in range(10)])

def group_center_targets(pre,post):
    group_schema(pre);group_schema(post)
    groups=post.groupby('content_token');centers={};variances={}
    for token,d in groups:
        z=tensor(d[HIST]);w=tensor(d.fit_mass)/float(d.fit_mass.sum())
        mean=(z*w[:,None]).sum(0);centers[token]=mean
        variances[token]=torch.stack([(w[:,None]*(z[:,block(j)]-mean[block(j)]).square()).sum()/size(j) for j in range(10)])
    yy=torch.stack([centers[t] for t in pre.content_token])
    var=sum(variances[t]*float(d.fit_mass.sum()) for t,d in pre.groupby('content_token'))
    return yy,var
