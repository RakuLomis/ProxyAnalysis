"""Finite raw first/second conditional moments, no per-visit 9312 expansion."""
from common import *

def grouping(ci,w):
    c=int(ci.max())+1;counts=torch.bincount(ci,minlength=c)
    require(bool((counts==counts[0]).all()),'Complete conditional grid required')
    idx=torch.argsort(ci,stable=True).reshape(c,int(counts[0]));mass=w[idx];pi=mass.sum(1)
    return idx,mass/pi[:,None],pi
def moments(a,idx,cw):
    g=a[idx];first=(g*cw[...,None]).sum(1)
    second=torch.bmm(g.transpose(1,2),g*cw[...,None])
    return first,second
def losses(a,d):
    first,second=moments(a,d['condition_rows'],d['conditional_w'])
    e1=first-d['mom1'];e2=second-d['mom2']
    fid1=(d['pi']*e1.square().sum(1)/10).sum();fid2=(d['pi']*e2.square().sum((1,2))/100).sum()
    t,s=d['gap'].unbind(1);gap1=(e1[t]-e1[s]).square().sum(1).mean()/10
    gap2=(e2[t]-e2[s]).square().sum((1,2)).mean()/100
    return fid1,fid2,gap1,gap2


