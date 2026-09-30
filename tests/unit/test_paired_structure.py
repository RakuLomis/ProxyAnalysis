import numpy as np
import pytest
from scipy.optimize import check_grad
from proxy_analysis.crosscontent.paired_constraint_objective import objective, moment, donor_indices
from proxy_analysis.crosscontent.count_decomposition import counts,decompose
from proxy_analysis.crosscontent.frozen_margin_diagnostics import coefficients,contributions


@pytest.mark.parametrize('k',[2,6])
def test_gradient(k):
    rng=np.random.default_rng(11);x=rng.normal(size=(24,4));y=np.arange(24)%k
    _,c=moment(rng.normal(size=x.shape));t=rng.normal(size=(1 if k==2 else k)*5)
    f=lambda v:objective(v,x,y,k,c,.1)[0]
    g=lambda v:objective(v,x,y,k,c,.1)[1]
    assert check_grad(f,g,t)<2e-6


def test_moment_and_centered_penalty():
    rng=np.random.default_rng(1);d=rng.normal(size=(20,4));raw,c=moment(d);w=rng.normal(size=(6,4))
    w-=w.mean(axis=0)
    assert np.trace(c)==pytest.approx(4)
    assert np.sum(w@raw*w)==pytest.approx(np.mean(np.sum((d@w.T)**2,axis=1)))
    assert np.linalg.eigvalsh(c).min()>=-1e-12
    assert np.count_nonzero(moment(np.zeros_like(d))[1])==0
    assert np.allclose(raw, np.cov(d,rowvar=False,bias=True)+np.outer(d.mean(0),d.mean(0)))


def test_logits_and_binary_penalty():
    s={'coef':[[2.,-1.]],'intercept':[.4]};w,b=coefficients(s);z=np.array([.1,.8])
    parts,m,_=contributions(z,w,b,1,0)
    assert m==pytest.approx(-.2)
    assert sum(parts.values())==pytest.approx(m)
    v=np.asarray(s['coef']);assert np.sum(w*w)==pytest.approx(np.sum(v*v)/2)


def test_counts():
    a={'packet_count':5,'nonempty_packets':3,'burst_count':4,'fr_runs':2}
    b={'packet_count':8,'nonempty_packets':4,'burst_count':5,'fr_runs':3}
    _,_,d=decompose(a,b);assert d['N_all']==d['N_data']+d['N_empty']
    with pytest.raises(ValueError):counts({**a,'fr_runs':5})


def test_donors_cover_other_contents():
    rows=[{'label_id':l,'protocol':'SS','content_id':f'{l}{c}','repetition':r}
          for l in ['a','b'] for c in range(4) for r in [1,2,4,5]]
    maps=[donor_indices(rows,s) for s in [1,2,3]]
    for i,r in enumerate(rows):
        assert len({rows[m[i]]['content_id'] for m in maps})==3
        for m in maps:
            assert rows[m[i]]['label_id']==r['label_id']
            assert rows[m[i]]['repetition']==r['repetition']


def test_common_logit_shift():
    rng=np.random.default_rng(4);x=rng.normal(size=(18,4));y=np.arange(18)%6
    _,c=moment(x);t=rng.normal(size=(6,5));u=t.copy();u+=rng.normal(size=(1,5))
    a=objective(t.ravel(),x,y,6,c,.1)[2];b=objective(u.ravel(),x,y,6,c,.1)[2]
    assert a['ce_nats']==pytest.approx(b['ce_nats'])
    assert a['pair_penalty']==pytest.approx(b['pair_penalty'])
