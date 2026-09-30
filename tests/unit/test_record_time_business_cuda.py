import pandas as pd  # Arrow DLLs before torch on this Windows environment.
import numpy as np
import torch
import pytest
from proxy_analysis.crosscontent.record_time_business.engineering import setup,predict_visits
from proxy_analysis.crosscontent.record_time_business.model import SequenceEncoder,Hierarchy
from proxy_analysis.crosscontent.record_time_business.cuda_packing import pack_sequences,require_cuda
from proxy_analysis.crosscontent.record_time_business.cuda_reference import ReferenceSequenceEncoder

def test_full_visit_prediction_and_cache_are_cuda():
    if not torch.cuda.is_available():pytest.skip('CUDA hardware absent')
    class Store:pass
    store=Store();store.visit={'visit':['u']}
    store.data={('u','post'):{'T':np.ones((3,4),np.float32),'R_up':np.ones((2,7),np.float32),'R_down':np.ones((4,7),np.float32)}}
    state={'R':{'mean':[0]*7,'scale':[1]*7},'T':{'mean':[0]*4,'scale':[1]*4}}
    model=Hierarchy().to('cuda:0');a=predict_visits(model,store,['visit'],'S2',state)
    b=predict_visits(model,store,['visit'],'S2',state)
    assert a.is_cuda and a.shape==(1,6) and len(store._gpu_visit_cache)==1
    assert torch.equal(a,b)
    state['R']['scale']=[2]*7
    predict_visits(model,store,['visit'],'S2',state)
    assert len(store._gpu_visit_cache)==1

def test_no_silent_fallback(monkeypatch):
    monkeypatch.setattr(torch.cuda,'is_available',lambda:False)
    with pytest.raises(RuntimeError,match='CUDA is required'):setup(3)

def test_cpu_business_inference_rejected():
    model=Hierarchy()
    with pytest.raises(RuntimeError,match='requires CUDA'):require_cuda(model)
    with pytest.raises(RuntimeError,match='requires CUDA'):predict_visits(model,None,[], 'S2',{})

@pytest.mark.parametrize('device',['cpu','cuda:0'])
def test_original_vs_packed_forward_and_gradient(device):
    if device.startswith('cuda') and not torch.cuda.is_available():pytest.skip('CUDA hardware absent')
    torch.set_num_threads(1);torch.manual_seed(8)
    a=ReferenceSequenceEncoder(7,chunk=31).to(device);b=SequenceEncoder(7,chunk=31).to(device);b.load_state_dict(a.state_dict())
    arrays=[np.random.default_rng(i).normal(size=(n,7)).astype(np.float32) for i,n in enumerate([1,3,31,32,89])]
    packed=pack_sequences(arrays,device,31)
    x=a(arrays);y=b(packed);torch.testing.assert_close(x,y,atol=2e-6,rtol=2e-5)
    x.square().sum().backward();y.square().sum().backward()
    for p,q in zip(a.parameters(),b.parameters()):torch.testing.assert_close(p.grad,q.grad,atol=2e-5,rtol=2e-4)
    before=[z.clone() for batch in packed.batches for z in batch];b(packed)
    for old,new in zip(before,[z for batch in packed.batches for z in batch]):assert torch.equal(old,new)
