import copy
import numpy as np
import pyarrow
import pytest
from proxy_analysis.crosscontent.group_anchor_diagnostics_contract import validate_input, nullable
from proxy_analysis.crosscontent.group_anchor_task_utility import subsets, predict
from proxy_analysis.crosscontent.group_anchor_holdout_recovery import ridge_fit, ridge_predict, neural_predict, torch_replay
from proxy_analysis.crosscontent.group_anchor_hierarchy import components, decompose
from proxy_analysis.crosscontent.group_anchor_diagnostics_report import group_error, cluster_weights
from proxy_analysis.crosscontent.group_anchor_reliability import feature_groups
from proxy_analysis.crosscontent.natural_pair_ssl_data import cyclic_donors
from proxy_analysis.crosscontent.natural_pair_ssl import networks, state


def rows():
    return [{'session_id':f'{c}-{r}','content_id':str(c),'label_id':str(c//2),'protocol':'SS','repetition':r}
            for c in range(4) for r in (1,2,4,5)]


def test_subsets_are_retrained_input_partitions():
    sets=subsets();assert len(sets)==13
    for g in feature_groups():
        assert set(sets['Only-'+g['group']]).isdisjoint(sets['Minus-'+g['group']])
        assert sorted(sets['Only-'+g['group']]+sets['Minus-'+g['group']])==sets['Full']


@pytest.mark.parametrize('field',['labels','pre','target','label_id'])
def test_inference_rejects_evaluation_fields(field):
    value={'fold':0,'session_ids':['x'],'post':np.zeros((1,157)).tolist()}
    with pytest.raises(ValueError):validate_input({**value,field:[]})


def test_nullable_and_missing_group_targets():
    assert nullable([[1.,np.nan]])==[[1.,None]]
    v=group_error(np.array([1.,999.]),np.zeros(2),np.array([True,False]),[0,1])
    assert v['mse']==1 and v['huber']==.5 and v['valid_dimensions']==1
    assert group_error(np.ones(2),np.zeros(2),np.zeros(2,bool),[0,1]) is None


def test_ridge_closed_form_and_donor_boundary():
    rr=rows();rng=np.random.default_rng(5);x=rng.normal(size=(16,157));y=2*x+3
    train={'post':x.tolist(),'pre_target':y.tolist(),'target_mask':np.ones_like(x,bool).tolist(),
           'donors':cyclic_donors(rr),'rows':rr}
    fit=ridge_fit(train,False,1.);assert fit['fits']==157 and fit['max_closed_form_error']<1e-10
    wrong=ridge_fit(train,True,1.);assert set(wrong['train_ids'])==set(wrong['donor_ids'])
    inputs={'fold':0,'session_ids':[r['session_id'] for r in rr],'post':x.tolist()}
    assert np.mean((ridge_predict(fit,inputs)-y)**2)<np.mean((ridge_predict(wrong,inputs)-y)**2)


def test_hierarchical_reconstruction_and_cycle_invariance():
    rr=rows();x=np.array([10*int(r['label_id'])+2*int(r['content_id'])+r['repetition'] for r in rr],float)
    a=decompose(x,2*x+7,rr);assert a['valid'] and abs(a['total_correlation']-1)<1e-12
    assert abs(sum(v['pre_energy'] for v in a['levels'])-1)<1e-12
    b=decompose(x[cyclic_donors(rr)],2*x+7,rr)
    for k in (0,1):assert np.isclose(a['levels'][k]['signed_total_contribution'],b['levels'][k]['signed_total_contribution'])
    assert b['levels'][2]['signed_total_contribution']<a['levels'][2]['signed_total_contribution']
    assert not decompose(np.zeros(len(rr)),x,rr)['valid']


def test_unbalanced_hierarchy_still_orthogonal():
    rr=rows()[:-4];x=np.arange(len(rr),dtype=float)
    result=decompose(x,x*x,rr);assert result['valid'] and result['identity_error']<1e-10


def test_constant_level_correlation_is_undefined():
    rr=rows();x=np.array([r['repetition'] for r in rr],float)
    result=decompose(x,x,rr)
    assert result['levels'][0]['correlation'] is None
    assert result['levels'][1]['correlation'] is None


def test_bootstrap_resamples_contents_and_not_seeds():
    weights=cluster_weights(['a','b','c','d'],{'a':0,'b':0,'c':1,'d':1},100,4)
    assert weights.shape==(100,4) and np.allclose(weights.sum(1),1)
    assert np.allclose(weights[:,:2].sum(1),.5)


def test_checkpoint_numpy_replay_and_test_target_perturbation():
    encoder,_=networks(1);rng=np.random.default_rng(2)
    fit={'encoder':state(encoder),'heads':{}}
    for i,g in enumerate(feature_groups()):
        fit['heads'][f'{i}.weight']=rng.normal(size=(len(g['indices']),32)).tolist()
        fit['heads'][f'{i}.bias']=rng.normal(size=len(g['indices'])).tolist()
    inputs={'fold':0,'session_ids':['a','b'],'post':rng.normal(size=(2,157)).tolist()}
    before=neural_predict(fit,inputs)
    assert np.allclose(before,torch_replay(fit,inputs),atol=1e-12)
    target=np.zeros(157);mask=np.ones(157,bool)
    original=group_error(before[0],target,mask,list(range(157)))
    altered=group_error(before[0],target+1000,mask,list(range(157)))
    assert original['mse']!=altered['mse']
    assert np.array_equal(before,neural_predict(fit,inputs))
