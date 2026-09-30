import numpy as np
import pytest
from proxy_analysis.crosscontent.source_hierarchy_contract import groups,center_targets
from proxy_analysis.crosscontent.source_center_runner import algebra
from proxy_analysis.crosscontent.decision_calibration_objective import fit,independent_lstsq
from proxy_analysis.crosscontent.source_transfer_coordinates import raw_input
from proxy_analysis.crosscontent.natural_pair_ssl_report import softmax


def sample():
    rows=[{'session_id':str(i),'content_id':str(i//4),'protocol':'P','repetition':[1,2,4,5][i%4]} for i in range(8)]
    rng=np.random.default_rng(21);t=rng.normal(size=(8,3));v=rng.normal(size=(8,3));w=rng.normal(size=(6,3))
    return rows,t,v,w


def test_centers_permutation_and_coordinates():
    rows,t,_,w=sample();tc=center_targets(t,rows,rows);c=np.array([1,2,3]);b=np.array([2,3,4])
    assert np.allclose(tc,center_targets(t[::-1],rows[::-1],rows))
    assert np.allclose(tc*c+b,center_targets(t*c+b,rows,rows))
    assert np.allclose(tc@w.T,center_targets(t@w.T,rows,rows))


def test_full_target_algebra_and_qr():
    rows,t,v,w=sample();tc=center_targets(t,rows,rows);c=np.array([1,.4,2])
    assert algebra(v,t,tc,c,w,groups(rows))['max_loss_identity_error']<1e-10
    theta,_=fit(v,tc,c,w,1)
    assert np.allclose(theta,independent_lstsq(v,tc,c,w,1))


def test_excluding_self_not_center():
    rows,t,_,_=sample();tc=center_targets(t,rows,rows)
    assert not np.allclose((4*tc-t)/3,tc)


def test_intercept_and_probability_mean():
    z=np.array([[0.,1.],[0.,5.]])
    beta=np.array([10.,0.]);assert not np.array_equal(z.argmax(1),(z+beta).argmax(1))
    assert np.allclose((z+beta)[0]-(z+beta)[1],z[0]-z[1])
    assert not np.allclose(softmax(z).mean(0),softmax(z.mean(0,keepdims=True))[0])


@pytest.mark.parametrize('case',['missing','repetition','duplicate','group_mismatch','target_nan'])
def test_qualification_reject(case):
    rows,t,_,_=sample();other=[dict(r) for r in rows]
    if case=='missing':other=other[:-1]
    elif case=='repetition':other[0]['repetition']=2
    elif case=='duplicate':other[0]['session_id']=other[1]['session_id']
    elif case=='group_mismatch':
        for r in other:r['content_id']='different'+r['content_id']
    elif case=='target_nan':t[0,0]=np.nan
    with pytest.raises(ValueError):center_targets(t,rows,other)


@pytest.mark.parametrize('field',['raw_pre','labels','content_id','protocol','centers'])
def test_prediction_white_list(field):
    with pytest.raises(ValueError):raw_input({'fold':0,'session_ids':['s'],'raw_post':[[0]*157],field:[]},'post')
