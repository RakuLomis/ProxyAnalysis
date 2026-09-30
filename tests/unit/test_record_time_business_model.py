import copy
import numpy as np
import pandas as pd
import torch
from proxy_analysis.crosscontent.record_time_business.model import SequenceEncoder,Hierarchy,transformed
from proxy_analysis.crosscontent.record_time_business.tensors import token_structure,time_tokens,schedule

def test_structure_positions_and_syntax():
    x=token_structure([5,15],[22,23])
    np.testing.assert_allclose(x[:,1:3],[[0,.25],[.25,1]])
    assert x[0,5]==1 and x[1,6]==1

def test_time_ties_and_no_record_timestamp():
    e=pd.DataFrame({'relative_time_ns':[50,50,1050],'direction':[1,-1,1],'new_payload_bytes':[3,4,5]})
    a=time_tokens(e);b=time_tokens(e.iloc[::-1]);np.testing.assert_array_equal(a,b)
    assert a.shape==(2,4) and a[0,0]==a[0,1]==0
    np.testing.assert_allclose(a[0,2:],np.log1p([3,4]),rtol=1e-6)

def test_chunk_and_padding_forward_backward_equivalence():
    torch.set_num_threads(1);torch.manual_seed(2)
    full=SequenceEncoder(7,chunk=1000);chunked=copy.deepcopy(full);chunked.chunk=17
    seq=[np.random.default_rng(i).normal(size=(n,7)).astype(np.float32) for i,n in enumerate([1,3,16,17,18,59,103])]
    x=full(seq);y=chunked(seq);torch.testing.assert_close(x,y,atol=2e-6,rtol=2e-5)
    x.sum().backward();y.sum().backward()
    for a,b in zip(full.parameters(),chunked.parameters()):torch.testing.assert_close(a.grad,b.grad,atol=1e-5,rtol=1e-4)
    alone=torch.cat([full([s]) for s in seq]);torch.testing.assert_close(x,alone,atol=2e-6,rtol=2e-5)

def test_balanced_donors_preserve_exact_per_flow_side_exposure():
    class Store:pass
    store=Store();store.visit={};store.uid_to_visit={};rows=[]
    for c in range(24):
        for r in [1,2,4,5]:
            sid=f'{c}:{r}';ids=[f'{sid}:{j}' for j in range(1+(c+r)%4)]
            store.visit[sid]=ids
            for u in ids:store.uid_to_visit[u]=sid
            rows.append({'session_id':sid,'content_id':str(c),'repetition':r})
    slots,pool,audit=schedule(pd.DataFrame(rows),store,1,1000)
    assert audit['preserves_exposure_per_uid_side'] and audit['slots_per_visit']==250
    assert len(slots)==1000 and len(slots[0]['batch'])==24

def test_post_transform_ignores_pre_and_type_ablation_keeps_time():
    class Store:pass
    s=Store();data={'T':np.ones((3,4),np.float32),'R_up':np.ones((2,7),np.float32),'R_down':np.ones((4,7),np.float32)}
    s.data={('a','post'):data,('a','pre'):data};state={'R':{'mean':[0]*7,'scale':[1]*7},'T':{'mean':[0]*4,'scale':[1]*4}}
    a=transformed(s,'a','post','R',state);s.data['a','pre']={'bad':None};b=transformed(s,'a','post','R',state,no_type=True)
    np.testing.assert_array_equal(a['T'],b['T']);np.testing.assert_array_equal(a['up'][:,:3],b['up'][:,:3])
    assert np.count_nonzero(b['up'][:,3:])==0
