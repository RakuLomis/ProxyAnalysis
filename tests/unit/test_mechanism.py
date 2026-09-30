import numpy as np
import pytest
from scipy.special import expit, softmax, logsumexp

from proxy_analysis.crosscontent.business_representations import vector, transform, dictionary, probability_histogram
from proxy_analysis.crosscontent.joint_teacher import source_guard
from proxy_analysis.crosscontent.privileged_learning import LinearStudent
from proxy_analysis.crosscontent.teacher_diagnostics import probabilities_from_state


def test_representation_is_single_side_and_frozen():
    s=dict.fromkeys(dictionary()['scalar14'],2.)
    s.update(length_hist=[1]*19,iat_hist=[2]*23,curve=np.linspace(0,1,101).tolist(),ip_src='do-not-use')
    v=vector(s,'distribution157')
    assert v.shape==(157,)
    assert np.isclose(v[14:33].sum(),1) and np.isclose(v[33:56].sum(),1)
    np.testing.assert_array_equal(transform(v[None,:],v[None,:]),np.zeros((1,157)))
    assert np.isnan(probability_histogram([0]*19,19)).all()
    with pytest.raises(ValueError): probability_histogram([1]*18,19)
    with pytest.raises(ValueError): vector(s,'unknown')


@pytest.mark.parametrize('k',[2,6])
def test_soft_weight_objective_gradient_and_state(k):
    rng=np.random.default_rng(7); x=rng.normal(size=(24,5)); y=np.arange(24)%k
    hard=np.eye(k)[y]; q=.5*hard+.5/k; n=len(x)
    assert q.sum()==pytest.approx(n)
    expanded=np.repeat(x,k,axis=0); labels=np.tile(np.arange(k),n); weights=q.ravel()
    if k==2:
        w=rng.normal(size=5); b=.3; z=x@w+b; p=expit(z)
        direct=np.mean(np.logaddexp(0,z)-q[:,1]*z)+np.sum(w*w)/(2*n)
        ze=expanded@w+b; pe=expit(ze)
        actual=np.sum(weights*(np.logaddexp(0,ze)-labels*ze))/n+np.sum(w*w)/(2*n)
        grad=x.T@(p-q[:,1])/n+w/n
        grad_e=expanded.T@(weights*(pe-labels))/n+w/n
    else:
        w=rng.normal(size=(k,5)); b=rng.normal(size=k); z=x@w.T+b; p=softmax(z,axis=1)
        direct=np.mean(logsumexp(z,axis=1)-np.sum(q*z,axis=1))+np.sum(w*w)/(2*n)
        ze=expanded@w.T+b; pe=softmax(ze,axis=1)
        actual=np.sum(weights*(logsumexp(ze,axis=1)-ze[np.arange(n*k),labels]))/n+np.sum(w*w)/(2*n)
        grad=(p-q).T@x/n+w/n
        grad_e=((pe-np.eye(k)[labels])*weights[:,None]).T@expanded/n+w/n
    assert direct==pytest.approx(actual,abs=1e-12)
    np.testing.assert_allclose(grad,grad_e,atol=1e-12)
    cfg={'model_C':1.,'max_iter':3000,'seed':1}
    model=LinearStudent(cfg).fit(x,q)
    np.testing.assert_allclose(model.predict(x),probabilities_from_state(x,model.state()),atol=1e-12)
    baseline=LinearStudent(cfg).fit(x,hard)
    for alpha in (0,.1,.25,.5):
        equivalent=LinearStudent(cfg).fit(x,(1-alpha)*hard+alpha*hard)
        np.testing.assert_allclose(baseline.predict(x),equivalent.predict(x),atol=1e-10)


def test_target_deployment_and_content_guard():
    def row(s,c,p): return {'session_id':s,'content_id':c,'protocol':p,'repetition':1}
    train=[row('a','a','SS')]; test=[row('b','b','SS')]; target=[row('c','b','VLESS')]
    source_guard(train,test,target,'SS')
    with pytest.raises(ValueError): source_guard(train+target,test,target,'SS')
    with pytest.raises(ValueError): source_guard([row('d','b','SS')],test,target,'SS')
