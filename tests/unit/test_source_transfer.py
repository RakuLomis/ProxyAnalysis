import numpy as np
import pytest
from proxy_analysis.crosscontent.source_transfer_coordinates import fit_source,coordinate,subsets,source_selected
from proxy_analysis.crosscontent.source_transfer_report import fixed_margin_contributions,contrast,scores
from proxy_analysis.crosscontent.source_transfer_runner import physical_checks


def states():
    source={'median':[10.]*157,'mean':[12.]*157,'scale':[2.]*157,'active':[True]*156+[False]}
    post={'median':[20.]*157,'mean':[30.]*157,'scale':[5.]*157}
    target={'mean':[40.]*157,'scale':[3.]*157}
    mapping={'coef':[2.]*157,'intercept':[1.]*157}
    return source,post,target,mapping


def test_coordinate_conversion_uses_all_three_scales():
    s,p,t,m=states();bundle={'fold':0,'session_ids':['a'],'raw_post':[[35.]*157]}
    b,_=coordinate(bundle,'B',[0,156],s,p,t);c,raw=coordinate(bundle,'C',[0,156],s,p,t,m)
    assert np.allclose(b,[[11.5,0]]) and np.allclose(raw,[[49.,49.]]) and np.allclose(c,[[18.5,0]])
    e,_=coordinate(bundle,'E',[0],s,p,t);assert np.allclose(e,[[1.]])


def test_B_missing_values_use_source_median_not_post_median():
    s,p,t,m=states();raw=np.zeros((1,157));raw[0,0]=np.nan
    value,_=coordinate({'fold':0,'session_ids':['a'],'raw_post':raw.tolist()},'B',[0],s,p,t)
    assert value[0,0]==-1


@pytest.mark.parametrize('arm',['B','C','D','E'])
def test_post_interfaces_reject_pre_and_labels(arm):
    s,p,t,m=states();bundle={'fold':0,'session_ids':['a'],'raw_post':[[35.]*157],'raw_pre':[[0.]*157]}
    with pytest.raises(ValueError):coordinate(bundle,arm,[0],s,p,t,m)


def test_single_group_is_independent_of_other_group_values():
    s,p,t,m=states();bundle={'fold':0,'session_ids':['a'],'raw_post':[[35.]*157]}
    first,_=coordinate(bundle,'C',[0],s,p,t,m);bundle['raw_post'][0][5]=np.nan
    second,_=coordinate(bundle,'C',[0],s,p,t,m);assert np.array_equal(first,second)


def test_training_pre_only_and_constant_mask():
    raw=np.tile(np.arange(157,dtype=float),(4,1));raw[:,0]=[1,2,3,4]
    state=fit_source(raw,{'valid':[True]*157});assert sum(state['active'])==1
    altered=raw.copy();altered[:,1]=999
    transformed=source_selected(altered,state,list(range(157)));assert np.all(transformed[:,1:]==0)
    assert len(subsets())==7


def test_linear_boundary_decomposition_with_fixed_rival():
    fit={'coef':[[1,2],[0,-1],[-2,0]],'indices':[0,1],'train_margin_quartiles':[0,1,2]}
    a={'labels':['a','b','c'],'label_id':'a','logits':[0,0,0],'coordinates':[0,0]}
    c={'logits':[5,-2,-2],'coordinates':[1,2]}
    result=fixed_margin_contributions(a,c,fit)
    assert result['fixed_rival_margin_change']==7 and result['identity_error']==0


def test_probability_floor_is_visible_in_uncapped_ce():
    r={'labels':['a','b'],'label_id':'a','probabilities':[0.,1.],'logits':[-1000.,0.]}
    result=scores(r);assert result['ce_floor_applied'] and result['ce_uncapped']>result['ce']


def test_physical_mapping_violations_are_recorded_not_clipped():
    raw=np.array([-2.,1.3]);value=physical_checks(raw,[0,14])
    assert value['negative_indices']==[0] and value['unit_interval_violations']==[14]
    assert np.array_equal(raw,[-2.,1.3])


def test_identical_prediction_contrasts_have_zero_intervals():
    rows=[]
    for c in range(6):
        p=np.eye(6)[c]*.8+.2/6
        rows.append({'content_id':str(c),'session_id':str(c),'fold':0,'labels':list('abcdef'),
                     'label_id':'abcdef'[c],'probabilities':p.tolist(),'logits':np.log(p).tolist()})
    v=contrast(rows,rows,{'bootstrap_repetitions':20,'bootstrap_seed':4})
    for metric in ('macro_f1','balanced_accuracy','ce_bits','brier'):
        assert v[metric+'_gain']==0 and v[metric+'_ci']==[0.,0.]
