import numpy as np
import pandas as pd
import pytest
from proxy_analysis.feasible_summary_calibration.model import encode,decode,fit,Ridge,torch,FEATURES,NUMERIC,tensor
from proxy_analysis.conditional_drift.common import illegal

def test_zero_parity_and_roundtrip():
    a=np.array([[1,0,1,0,1,0],[0,100,0,30,0,1],[100,100,10,10,3,2],[10**11,10**9,1000000,1000,32,33]])
    f=np.array([1,1,3,10]);b,log=decode(encode(a),f);np.testing.assert_array_equal(b.cpu(),a)
    for v,F in zip(b.cpu().numpy(),f):assert not illegal(v,F)

def test_unbounded_negative_coordinates_give_nonnegative_output():
    z=np.full((3,6),-1000.);f=np.array([1,2,3]);b,log=decode(z,f)
    for v,F in zip(b.cpu().numpy(),f):assert not illegal(v,F)
    assert log['N_floor_active'].all()

def test_overflow_and_nonfinite_fail_not_fallback():
    for x in [1000.,np.inf,np.nan]:
        with pytest.raises(FloatingPointError):decode(np.full((1,6),x),[1])

def test_group_rejects_identity_and_is_permutation_invariant():
    rng=np.random.default_rng(3);R=rng.integers(1,10,(12,2));E=R+rng.integers(0,20,(12,2));U=E+rng.integers(0,100,(12,2))
    pre=pd.DataFrame(np.c_[U,E,R,np.ones(12)*10],columns=NUMERIC);pre['content_id']=np.repeat(['a','b','c'],4)
    post=pre[['content_id']+FEATURES].copy();post['U_up']+=20
    m,p,_,_=fit(pre,post,'group');n,q,_,_=fit(pre.sample(frac=1,random_state=4),post.sample(frac=1,random_state=5),'group')
    torch.testing.assert_close(m.weight,n.weight,rtol=0,atol=0);pd.testing.assert_frame_equal(p,q)
    with pytest.raises(AssertionError):fit(pre,post.assign(F=10),'group')

def test_group_gradient_equivalence_away_from_optimum():
    torch.manual_seed(8);a=tensor(np.array([[100,100,10,10,3,3]]*8));z=encode(a)
    target=z+torch.randn_like(z);x=torch.randn((8,8),device=z.device,dtype=z.dtype);theta=torch.randn((8,6),device=z.device,dtype=z.dtype,requires_grad=True)
    means=target.reshape(2,4,6).mean(1).repeat_interleave(4,0)
    scale=torch.arange(1,7,device=z.device,dtype=z.dtype)
    center=(((z+x@theta*scale-means)/scale)**2).sum(1).mean()+theta[:-1].square().sum()
    expanded=((((z+x@theta*scale).reshape(2,4,1,6)-target.reshape(2,1,4,6))/scale)**2).sum(-1).mean()+theta[:-1].square().sum()
    g1=torch.autograd.grad(center,theta,retain_graph=True)[0];g2=torch.autograd.grad(expanded,theta)[0]
    torch.testing.assert_close(g1,g2,atol=1e-10,rtol=1e-10)
