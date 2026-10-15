"""Small CUDA conditional distributions, weighted by content not flow counts."""
from common import *

def smooth(counts):
    k=counts.shape[1]; require(abs(float(counts.sum())-12)<1e-10,'Twelve training content mass')
    q=(counts.sum(0)+1/k)/(counts.sum()+1)
    kernel=(counts+q)/(counts.sum(1)[:,None]+1)
    require(torch.isfinite(kernel).all() and (kernel>0).all() and
            float((kernel.sum(1)-1).abs().max())<1e-12,'Invalid conditional probability')
    return q,kernel

def fit_paired(d,g):
    require(set(d)=={'content_token','fit_mass',*[f's{j}_{side}' for j in range(4) for side in ['pre','post']]},'Paired state schema')
    k=SIZES[g]; a=tensor(d[f's{g}_pre'],torch.long); b=tensor(d[f's{g}_post'],torch.long)
    counts=weighted(a*k+b,tensor(d.fit_mass),k*k).reshape(k,k)
    q,m=smooth(counts); return {'counts':counts,'q':q,'matrix':m,'row_mass':counts.sum(1)}

def fit_group(pre,post,g):
    for d in [pre,post]:require(set(d)=={'content_token','fit_mass',*[f's{j}' for j in range(4)]},'Group state identity leak')
    groups=sorted(pre.content_token.unique()); require(set(groups)==set(post.content_token),'Group member mismatch')
    codes=dict(zip(groups,range(len(groups)))); k=SIZES[g]; margins=[]
    for d in [pre,post]:
        u=tensor(d.content_token.map(codes),torch.long); b=tensor(d[f's{g}'],torch.long)
        margins.append(weighted(u*k+b,tensor(d.fit_mass),len(groups)*k).reshape(-1,k))
    a,b=margins; require(float((a.sum(1)-b.sum(1)).abs().max())<1e-10,'Group mass')
    q,m=smooth(a.T@(b/a.sum(1)[:,None])); return {'counts':a.T@(b/a.sum(1)[:,None]),'q':q,'matrix':m,'row_mass':a.sum(0)}
