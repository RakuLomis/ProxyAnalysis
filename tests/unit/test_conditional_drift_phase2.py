import importlib.util
from pathlib import Path
import numpy as np
import pandas as pd

spec=importlib.util.spec_from_file_location('drift_phase2',Path(__file__).resolve().parents[2]/'eval/conditional_proxy_drift/phase2.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def test_schedule_all_visits_equal_weight():
    train=pd.DataFrame({'content_id':np.repeat([f'c{i}' for i in range(24)],4)})
    a,v=m.schedule(train,20260918)
    assert a.shape==v.shape==(1000,24)
    np.testing.assert_array_equal(np.bincount(a.ravel()),np.full(96,250))
    assert v.min()==0 and v.max()==7
    aa,vv=m.schedule(train,20260918);np.testing.assert_array_equal(aa,a);np.testing.assert_array_equal(vv,v)

def test_post_only_cuda_prediction():
    dev=m.device();head=m.torch.nn.Sequential(m.torch.nn.Linear(7,32),m.torch.nn.ReLU(),m.torch.nn.Linear(32,6)).to(dev)
    p=m.predict_post(head,np.ones((4,7)),np.zeros(7),np.ones(7),dev)
    assert p.shape==(4,6);np.testing.assert_allclose(p.sum(1),1,atol=1e-6)

def test_crps_and_energy_degenerate_distribution():
    a=np.repeat(np.array([[1.,2.,3.]]),8,axis=0);y=np.array([2.,2.,4.])
    crps=np.abs(a-y).mean(0)-.5*np.abs(a[:,None,:]-a[None,:,:]).mean((0,1))
    np.testing.assert_allclose(crps,[1,0,1])
    energy=np.linalg.norm(a-y,axis=1).mean()-.5*np.linalg.norm(a[:,None,:]-a[None,:,:],axis=2).mean()
    np.testing.assert_allclose(energy,np.sqrt(2))
