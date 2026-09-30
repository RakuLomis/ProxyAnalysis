import numpy as np
import pytest
from proxy_analysis.crosscontent.decision_calibration_objective import fit,independent_lstsq,losses
from proxy_analysis.crosscontent.decision_calibration_runner import mapping
from proxy_analysis.crosscontent.source_transfer_coordinates import raw_input


def data():
    rng=np.random.default_rng(312);v=rng.normal(size=(15,4));t=.8*v+rng.normal(size=v.shape)*.3
    return v,t,np.array([.5,1,2,3]),rng.normal(size=(6,4))


@pytest.mark.parametrize('lam',[0,.1,1,10])
def test_independent_solution(lam):
    v,t,c,w=data();theta,stats=fit(v,t,c,w,lam)
    assert np.allclose(theta,independent_lstsq(v,t,c,w,lam),atol=1e-10)
    assert stats['normalized_gradient_residual']<1e-12


def test_zero_matches_ridge():
    v,t,c,w=data();a=((v-v.mean(0))*(t-t.mean(0))).sum(0)/(((v-v.mean(0))**2).sum(0)+1)
    expected=np.r_[a,t.mean(0)-a*v.mean(0)]
    assert np.allclose(fit(v,t,c,w,0)[0],expected)


def test_zero_weights():
    v,t,c,w=data();assert np.allclose(fit(v,t,c,w*0,10)[0],fit(v,t,c,w,0)[0])


def test_common_shift_and_row_permutation():
    v,t,c,w=data();ref=fit(v,t,c,w,1)[0]
    assert np.allclose(ref,fit(v,t,c,w+np.arange(4),1)[0])
    assert np.allclose(ref,fit(v,t,c,w[::-1],1)[0])


def test_offset_intercept_cancel():
    v,t,c,w=data();theta,_=fit(v,t,c,w,1);a,b=theta.reshape(2,4)
    offset=np.arange(4);beta=np.arange(6)*2
    delta=((v*a+b)*c+offset)@w.T+beta-((t*c+offset)@w.T+beta)
    delta-=delta.mean(1,keepdims=True)
    assert np.isclose(np.mean((delta**2).sum(1))/5,losses(theta,v,t,c,w,1)['decision'])


def test_missing_rejected():
    v,t,c,w=data();mask=np.ones_like(v,bool);mask[0,0]=False
    with pytest.raises(ValueError):fit(v,t,c,w,1,mask=mask)


def test_mapping_inactive_diagonal():
    p={'indices':[1,4]};m=mapping([2,3,4,5],p)
    assert np.count_nonzero(m['coef'])==2 and m['intercept'][0]==0
    x=np.arange(157.);a=x*np.array(m['coef'])+m['intercept'];x[4]+=10
    b=x*np.array(m['coef'])+m['intercept'];assert a[1]==b[1]


def test_wrong_target_consistent():
    v,t,c,w=data();donor=np.roll(np.arange(len(t)),1)
    theta,_=fit(v,t[donor],c,w,1)
    assert np.allclose(theta,independent_lstsq(v,t[donor],c,w,1))


@pytest.mark.parametrize('field',['raw_pre','labels','y'])
def test_post_rejects_extra(field):
    with pytest.raises(ValueError):raw_input({'fold':0,'session_ids':['s'],'raw_post':[[0]*157],field:[]},'post')
