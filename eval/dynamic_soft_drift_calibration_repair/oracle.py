"""Independent explicit observations and scalar polynomial derivative oracle."""
from common import *

def coefficients(t,arm):
    f=t['fixture'];a=f['a'];b0=f['b0'];delta0=b0-a
    if arm=='D-G':
        post=f['post'];wp=f['post_mass'];w=f['w'];tokens=f['pre_tokens'];pt=f['post_tokens']
        same=tensor([[u==v for v in pt] for u in tokens],torch.bool)
        groupmass=same.to(torch.float64)@wp
        ww=w[:,None]*wp[None,:]*same/groupmass[:,None]
        target=post[None,:,:]-a[:,None,:];dx=delta0[:,None,:]
        require(abs(float(ww.sum())-1)<1e-12,'Anonymous Cartesian mass')
    else:
        ww=f['w'];target=f['b']-a;dx=delta0
    A=[];B=[];C=[]
    for j in range(10):
        sl=block(j)
        A.append((ww*dx[...,sl].square().mean(-1)).sum())
        B.append((ww*(dx[...,sl]*target[...,sl]).mean(-1)).sum())
        C.append((ww*target[...,sl].square().mean(-1)).sum())
    post=t['view']['C_x'];center=post.mean(0)
    s=torch.stack([(post[:,block(j)]-center[block(j)]).square().mean() for j in range(10)]).clamp_min(1e-6)
    return dict(A=torch.stack(A),B=torch.stack(B),C=torch.stack(C),s=s)

def g(q,A,B,s):return (q-1)*(A*(q+1)-2*B)/s
def derivative(q,A,B,s):
    z=g(q,A,B,s);return 0. if z<=0 else z*(2*A*q-2*B)/s/10
def phi(q,A,B,s):return max(g(q,A,B,s),0.)**2/20
def branch(q,h,A,B,s):
    if A==0 and B==0:return 'constant_zero'
    lo=q-h;hi=q+h;roots=[1.]
    if A!=0:roots.append(2*B/A-1)
    if any(lo<=v<=hi for v in roots):return 'boundary'
    points=[lo,hi]
    if A!=0 and lo<=B/A<=hi:points.append(B/A)
    values=[g(v,A,B,s) for v in points]
    return 'active' if min(values)>0 else 'inactive' if max(values)<0 else 'boundary'

def tests():
    cases=[('positive',1.1,.001,1.,0.,1.,'active'),
           ('negative',.9,.001,1.,0.,1.,'inactive'),
           ('root',1.,.001,1.,0.,1.,'boundary'),
           ('zero',1.,.001,0.,0.,1.,'constant_zero'),
           ('linear',1.1,.001,0.,-1.,1.,'active'),
           ('two_roots',.9998,.001,1.,.9998,1.,'boundary')]
    result=[]
    for name,q,h,A,B,s,expected in cases:
        got=branch(q,h,A,B,s);require(got==expected,'Oracle branch '+name)
        if name=='root':require(derivative(q,A,B,s)==0,'Root derivative')
        if name=='two_roots':require(g(q-h,A,B,s)>0 and g(q+h,A,B,s)>0 and g(q,A,B,s)<0,'Endpoint same sign counterexample')
        result.append(dict(name=name,expected=expected,actual=got,passed=True))
    return result
