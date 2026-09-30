import copy
import numpy as np
import pyarrow
import pytest
import torch

from proxy_analysis.crosscontent.natural_pair_ssl_data import cyclic_donors, audit_partition, fingerprint
from proxy_analysis.crosscontent.natural_pair_ssl import networks, vicreg, views, pretrain, state, restore, diagnostics

CFG={'variance_eps':1e-4,'vicreg_weights':[25,25,1],'mask_rate':0.05,'learning_rate':0.001,'steps':2}


def test_donors_preserve_content_and_are_bijection():
    rows=[{'protocol':p,'content_id':c,'repetition':r} for p in ['SS','VL'] for c in ['a','b'] for r in [1,2,4,5]]
    d=cyclic_donors(rows)
    assert sorted(d)==list(range(16))
    for i,j in enumerate(d):
        assert i!=j and rows[i]['content_id']==rows[j]['content_id'] and rows[i]['protocol']==rows[j]['protocol']
    with pytest.raises(ValueError): cyclic_donors(rows[:-1])


def test_capture_and_content_isolation():
    a=[{'session_id':'a','content_id':'x'}];b=[{'session_id':'b','content_id':'y'}]
    captures={'a':[{'path':'C:\\X.pcap'}],'b':[{'path':'c:/x.pcap'}]}
    with pytest.raises(ValueError):audit_partition(a,b,captures)
    captures['b']=[{'path':'C:/y.pcap'}]
    assert audit_partition(a,b,captures)['overlaps']==0
    with pytest.raises(ValueError):audit_partition(a,a,captures)


def test_vicreg_constant_penalty_and_invalid_batch():
    x=torch.zeros((4,3),dtype=torch.float64,requires_grad=True)
    loss,parts=vicreg(x,x,CFG)
    assert float(loss)>20 and float(parts[0])==0 and float(parts[2])==0
    loss.backward();assert torch.isfinite(x.grad).all()
    with pytest.raises(ValueError):vicreg(x[:1],x[:1],CFG)


@pytest.mark.parametrize('arm',['B1','B2','B3','B4'])
def test_views_and_seeded_pretraining(arm):
    torch.set_num_threads(1)
    rng=np.random.default_rng(4)
    ssl={'session_ids':['a','b','c','d'],'pre':rng.normal(size=(4,157)).tolist(),
         'post':rng.normal(size=(4,157)).tolist(),'donor_indices':[1,2,3,0]}
    _,a,_=pretrain(ssl,arm,12,CFG);_,b,_=pretrain(ssl,arm,12,CFG)
    assert fingerprint(a)==fingerprint(b)
    bad={**ssl,'labels':[0,1,0,1]}
    with pytest.raises(ValueError):pretrain(bad,arm,12,CFG)


def test_b2_does_not_create_cross_boundary_pairs():
    a=torch.ones(4,3);b=torch.zeros(4,3);cfg={**CFG,'mask_rate':0}
    for step in [0,1]:
        x,y=views(a,b,[1,2,3,0],'B2',step,cfg,torch.Generator())
        assert torch.equal(x,y)
        assert torch.equal(x,a if step==0 else b)


def test_shared_initialization_and_post_only_restore():
    a,_=networks(2);b,_=networks(2)
    assert fingerprint(state(a))==fingerprint(state(b))
    restore(b,state(a));x=torch.zeros(1,157,dtype=torch.float64)
    assert torch.equal(a(x),b(x))
    assert diagnostics(np.zeros((4,3)))['effective_rank']==0


def test_report_numpy_forward_and_identical_control_interval():
    from proxy_analysis.crosscontent.natural_pair_ssl_report import mlp, compare
    encoder,_=networks(7);x=np.random.default_rng(9).normal(size=(8,157))
    with torch.no_grad():expected=encoder(torch.tensor(x,dtype=torch.float64)).numpy()
    assert np.allclose(expected,mlp(x,state(encoder)),atol=1e-12)
    rows=[]
    for seed in [1,2,3]:
        for i in range(4):
            rows.append({'content_id':str(i),'label_id':str(i%2),'labels':['0','1'],
                         'seed':seed,'probabilities':[.7,.3] if i%2==0 else [.2,.8]})
    result=compare(rows,rows,100,[1,2,3])
    assert result['f1_gain']==0 and result['ce_gain_bits']==0
    assert result['f1_ci']==[0,0] and result['ce_ci']==[0,0]
