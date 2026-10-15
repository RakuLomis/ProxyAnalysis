"""Frozen positive diagonal metric, capped direction and actual projection."""
from common import *

def direction(g,m):
    cuda(g,m);require(bool((m>=1).all()),'Metric must be positive')
    p=-g/m;norm=float((p*m.sqrt()).abs().max())
    gamma=1. if norm==0 else min(1.,.1/norm)
    return p*gamma,gamma

def candidate(q,p,alpha):
    new=(q+alpha*p).clamp(0,2);return new,new-q

def projected_gradient(q,g,m=None):
    if m is None:return q-(q-g).clamp(0,2)
    return m.sqrt()*(q-(q-g/m).clamp(0,2))


