import pandas as pd
import numpy as np
import torch
import pytest
from sklearn.metrics import f1_score,balanced_accuracy_score,log_loss
from proxy_analysis.crosscontent.record_time_business import formal
from proxy_analysis.crosscontent.record_time_business.formal_report import scores
from proxy_analysis.crosscontent.record_time_business.model import Hierarchy
from proxy_analysis.crosscontent.record_time_business.engineering import setup

def test_formal_matrix_is_frozen_195():
    jobs=formal.specification();assert len(jobs)==195
    assert len({formal.job_name(j) for j in jobs})==195
    assert sum(j['phase']=='supervised' for j in jobs)==75
    assert sum(j['phase']=='ssl' for j in jobs)==sum(j['phase']=='finetune' for j in jobs)==60

def test_post_only_store_view():
    class Store:pass
    s=Store();s.visit={'train':['a'],'test':['b']};s.data={(u,side):{'sentinel':side} for u in ['a','b'] for side in ['pre','post']}
    v=formal.View(s,['test'],['post'])
    assert set(v.data)=={('b','post')} and 'a' not in v.uid_to_visit
    with pytest.raises(KeyError):v.data['b','pre']

def test_metrics_match_independent_sklearn():
    rng=np.random.default_rng(11);target=np.arange(120)%6;p=rng.random((120,6));p/=p.sum(1)[:,None]
    out=scores(target,p)
    assert out[0]==pytest.approx(f1_score(target,p.argmax(1),average='macro'))
    assert out[1]==pytest.approx(balanced_accuracy_score(target,p.argmax(1)))
    assert out[2]==pytest.approx(log_loss(target,p)/np.log(2))
    assert out[3]==pytest.approx(((p-np.eye(6)[target])**2).sum(1).mean())
    np.testing.assert_allclose(scores(np.arange(6),np.eye(6)),[1,1,0,0])

def test_finetune_copies_only_encoder_and_keeps_new_head(tmp_path,monkeypatch):
    if not torch.cuda.is_available():pytest.skip('CUDA required')
    monkeypatch.setattr(formal,'FORMAL',tmp_path)
    job={'fold':0,'seed':20260918,'arm':'L3','phase':'finetune'};device=setup(job['seed'])
    initial=Hierarchy().to(device);fresh={k:v.clone() for k,v in initial.state_dict().items()}
    source={k:v.clone()+1 for k,v in fresh.items()}
    folder=tmp_path/formal.job_name({**job,'phase':'ssl'});folder.mkdir()
    torch.save({'model':source},folder/'final.pt')
    formal.write_json(folder/'done.json',{'checkpoint_sha256':formal.digest(folder/'final.pt')})
    result=formal.initialize(job,device).state_dict()
    for k in result:assert torch.equal(result[k],source[k] if k.startswith(formal.ENCODER) else fresh[k])
