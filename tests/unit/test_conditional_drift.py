import numpy as np
import pandas as pd
import pytest
from proxy_analysis.conditional_drift.common import illegal
from proxy_analysis.conditional_drift.model import Ridge,decode,targets

def test_valid_and_zero_direction():
    assert not illegal([100,80,10,9,3,4],2)
    assert not illegal([100,0,3,0,1,0],1)

@pytest.mark.parametrize('x,F,reason',[
 ([-1,2,0,1,0,1],1,'negative'),([1,1,2,1,1,1],1,'R_E_U_order'),
 ([10,10,1,1,1,1],3,'runs_below_connections'),([100,100,20,20,10,2],2,'direction_imbalance'),
 ([10,10,2,2,0,1],1,'zero_positive_mismatch'),([1.2,2,1,1,1,1],1,'noninteger')])
def test_reject(x,F,reason):assert illegal(x,F)==reason

def test_decode_does_not_clip_small_negative():
    _,_,why=decode(np.array([-.01,1,1,1,1,1]),1);assert why=='negative'

def test_cuda_identity_and_affine():
    rng=np.random.default_rng(9);a=rng.integers(10,1000,(30,6)).astype(float);F=np.ones(30)
    model=Ridge(a,a,F);np.testing.assert_allclose(model.predict(a,F),np.log1p(a),atol=1e-12)
    b=np.expm1(np.log1p(a)+.3);model=Ridge(a,b,F)
    np.testing.assert_allclose(model.predict(a,F),np.log1p(b),atol=1e-10)
    assert model.weight.is_cuda and model.normal_residual<1e-10

def test_cuda_affine_without_penalty():
    rng=np.random.default_rng(7);a=rng.integers(10,100,(40,6)).astype(float);F=rng.integers(1,8,40)
    z=np.log1p(a);b=np.expm1(z+.05*z+.2)
    model=Ridge(a,b,F,alpha=0.)
    np.testing.assert_allclose(model.predict(a,F),np.log1p(b),atol=1e-9)

def test_wrong_donors_are_same_content_bijection():
    from proxy_analysis.conditional_drift.common import FEATURES
    rows=[]
    for c in ['a','b']:
        for i,r in enumerate([1,2,4,5]):rows.append({'content_id':c,'repetition':r,'F':1,**{k+'_pre':1 for k in FEATURES},**{k+'_post':i+5 for k in FEATURES}})
    f=pd.DataFrame(rows);a,b,F,donor=targets(f,True)
    assert list(donor)==[1,2,3,0,5,6,7,4]
    assert (f.content_id.to_numpy()==f.iloc[donor].content_id.to_numpy()).all()
