import numpy as np
import pytest
from proxy_analysis.crosscontent.student_capacity import network,loss_parts,train,state_hash,preprocess
import torch


def cfg():
    return dict(hidden_width=32,learning_rate=.001,adam_betas=[.9,.999],adam_eps=1e-8,steps=4,weight_l2=1e-4)


def test_onehot_and_explicit_soft_ce():
    m=network(3,2,19);x=torch.ones((4,3),dtype=torch.float64);y=torch.tensor([0,1,0,1])
    q=torch.nn.functional.one_hot(y,2).double();_,ce,_=loss_parts(m,x,q,0.)
    assert float(ce.detach())==pytest.approx(float(torch.nn.functional.cross_entropy(m(x),y).detach()))
    soft=.5*q+.25
    _,a,_=loss_parts(m,x,soft,0.)
    direct=-(soft*torch.log_softmax(m(x),1)).sum()/4
    assert float(a.detach())==pytest.approx(float(direct.detach()))


def test_regularizer_excludes_bias():
    m=network(3,2,19);x=torch.ones((4,3),dtype=torch.float64);q=torch.ones((4,2),dtype=torch.float64)/2
    _,_,a=loss_parts(m,x,q,.01)
    with torch.no_grad():
        for name,p in m.named_parameters():
            if name.endswith('bias'):p.add_(100)
    _,_,b=loss_parts(m,x,q,.01)
    assert float(a.detach())==pytest.approx(float(b.detach()))


def test_determinism_and_initialization_reset():
    torch.set_num_threads(1);torch.use_deterministic_algorithms(True)
    x=np.random.default_rng(3).normal(size=(6,3));q=np.eye(2)[np.arange(6)%2]
    _,a,ta=train(x,q,19,cfg());_,b,tb=train(x,q,19,cfg())
    _,c,_=train(x,q*.5+.25,19,cfg())
    assert a['final_sha256']==b['final_sha256'] and ta==tb
    assert a['initial_sha256']==b['initial_sha256']==c['initial_sha256']
    assert a['steps']==4 and len(ta)==4


def test_gradient():
    m=network(3,2,13);x=torch.randn(5,3,dtype=torch.float64);q=torch.full((5,2),.5,dtype=torch.float64)
    loss,_,_=loss_parts(m,x,q,.01);loss.backward();parameter=m[2].weight
    analytical=float(parameter.grad[0,0]);original=float(parameter.detach()[0,0]);eps=1e-6
    with torch.no_grad():
        parameter[0,0]=original+eps;plus=float(loss_parts(m,x,q,.01)[0])
        parameter[0,0]=original-eps;minus=float(loss_parts(m,x,q,.01)[0])
        parameter[0,0]=original
    assert analytical==pytest.approx((plus-minus)/(2*eps),abs=1e-8)


def test_invalid_targets_and_frozen_preprocess():
    with pytest.raises(ValueError):train([[1,2]],[[.2,.2]],0,cfg())
    s={'imputer_statistics':[2,3],'scaler_mean':[1,1],'scaler_scale':[2,4]}
    assert np.allclose(preprocess([[np.nan,5]],s),[[.5,1]])
    saved={k:list(v) for k,v in s.items()};preprocess([[1e8,-1e8]],s)
    assert saved==s


@pytest.mark.parametrize('d,k,total',[(14,6,678),(157,6,5254),(14,2,546),(157,2,5122)])
def test_parameter_count(d,k,total):
    assert sum(p.numel() for p in network(d,k,1).parameters())==total
