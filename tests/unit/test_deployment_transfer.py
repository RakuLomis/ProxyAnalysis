import numpy as np
import pytest
from proxy_analysis.crosscontent.deployment_transfer_prepare import prepare_state
from proxy_analysis.crosscontent.deployment_transfer_runner import forward
from proxy_analysis.crosscontent.deployment_transfer_report import domain_contrast


def package():
    rng=np.random.default_rng(96);pre=rng.normal(size=(96,157));post=rng.normal(size=(96,157));pre[:,0]=2
    rows=[{'session_id':str(i),'content_id':str(i//4),'protocol':'S','repetition':[1,2,4,5][i%4]} for i in range(96)]
    return {'context':'S-0','fold':0,'source_protocol':'S','labels':['a'],'rows':rows,'raw_pre':pre.tolist(),'raw_post':post.tolist()}


def test_source_only_state_and_const():
    p=package();s=prepare_state(p)
    assert 0 not in s['indices'] and 0 in s['pre_inactive_post_variable_indices']
    assert np.allclose(s['source_scaler']['mean'],np.mean(p['raw_pre'],0))
    assert np.allclose(s['center'][:4],np.mean(s['t'][:4],0))


def test_target_rows_rejected():
    p=package();p['rows'][0]['protocol']='T'
    with pytest.raises(ValueError):prepare_state(p)


def test_missing_active_target_rejected():
    p=package();p['raw_pre'][0][1]=None
    with pytest.raises(ValueError):prepare_state(p)


@pytest.mark.parametrize('arm',['B','F','H','E'])
def test_no_test_pre_or_centers(arm):
    p=package();s=prepare_state(p);model={'coef':np.zeros((6,157)).tolist(),'intercept':[0]*6}
    params={'coef':[1]*157,'intercept':[0]*157}
    for field in ('raw_pre','centers','labels','protocol'):
        with pytest.raises(ValueError):forward({'fold':0,'session_ids':['s'],'raw_post':[[0]*157],field:[]},s,model,arm,params)


def test_domain_contrast_preserves_different_visits():
    a=[];b=[]
    for y in range(6):
        for rep in range(4):
            p=[.02]*6;p[y]=.9
            common={'content_id':str(y),'label_id':str(y),'labels':list(map(str,range(6))),'probabilities':p,'logits':np.log(p).tolist()}
            a.append({**common,'session_id':f't{y}-{rep}'});b.append({**common,'session_id':f's{y}-{rep}'})
    r=domain_contrast(a,b,{'bootstrap_repetitions':50,'bootstrap_seed':1})
    assert r['macro_f1_gain']==0 and r['macro_f1_ci']==[0,0]
    with pytest.raises(ValueError):domain_contrast(a,a,{'bootstrap_repetitions':50,'bootstrap_seed':1})
