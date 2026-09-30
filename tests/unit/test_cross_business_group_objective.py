import numpy as np
import torch
from proxy_analysis.cross_business_calibration.group import device

def test_group_objective_gradients_at_nonoptimal_parameters():
    # Eight real inputs, not 32 independent observations. Two groups of four.
    dev=device();rng=np.random.default_rng(17)
    x=torch.tensor(rng.normal(size=(8,8)),device=dev,dtype=torch.float64);x[:,-1]=1
    a=torch.tensor(rng.normal(size=(8,6)),device=dev,dtype=torch.float64)
    b=torch.tensor(rng.normal(size=(2,4,6)),device=dev,dtype=torch.float64)
    target=b.mean(1).repeat_interleave(4,0)-a
    theta=torch.tensor(rng.normal(size=(8,6)),device=dev,dtype=torch.float64,requires_grad=True)
    penalty=theta[:-1].square().sum()
    center=((x@theta-target)**2).sum(1).mean()+penalty
    expanded=((x.reshape(2,4,8)@theta+a.reshape(2,4,6))[:,:,None,:]-b[:,None,:,:]).square().sum(-1).mean()+penalty
    g1=torch.autograd.grad(center,theta,retain_graph=True)[0];g2=torch.autograd.grad(expanded,theta)[0]
    torch.testing.assert_close(g1,g2,atol=1e-12,rtol=1e-12)
    expected=(b-b.mean(1,keepdim=True)).square().sum(-1).mean()
    torch.testing.assert_close(expanded-center,expected,atol=1e-12,rtol=1e-12)
    assert float(g1.abs().max())>1 # Test away from the fitted stationary point.

def test_log_center_not_raw_center():
    raw=np.array([1.,3.,15.,255.])
    assert not np.isclose(np.log1p(raw).mean(),np.log1p(raw.mean()))

def test_full_confusion_counts_false_positives_from_auxiliary_classes():
    # A new class predicted perfectly for its own rows can still have poor precision.
    cm=np.eye(6)*4;cm[2,0]=4;cm[2,2]=0
    f1=2*cm[0,0]/(cm[0].sum()+cm[:,0].sum())
    assert np.isclose(f1,2/3) # Filtering true-label rows first would incorrectly yield 1.
