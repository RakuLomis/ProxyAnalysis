import math

import numpy as np
import pytest
from sklearn.linear_model import Ridge

from proxy_analysis.information_validation.data import classify_activity, split_indices, validate_feature_identity
from proxy_analysis.information_validation.experiments import (
    bit_loss, conditional_mean, entropy_binary, pipeline, dropped_columns,
)


def test_page_is_not_playback():
    x = classify_activity({'activity_outcome': {'kind': 'page_load', 'state': 'passed'},
                           'navigation_outcome': {'state': 'passed'}})
    assert x['verified_activity'] == 'page_load'
    assert not x['playback_verified']


def test_playback_validity_does_not_require_duration_goal():
    x = {'activity_outcome': {'state': 'passed'}, 'playback': {
        'primary_goal_met': True, 'primary_content_observed': True,
        'primary_content_seconds': 26, 'desired_primary_seconds': 25}}
    assert classify_activity(x)['playback_verified']
    assert classify_activity(x)['playback_goal_met']
    x['playback']['primary_content_seconds'] = 2
    x['playback']['primary_goal_met'] = False
    x['activity_outcome']['state'] = 'degraded'
    assert classify_activity(x)['playback_verified']
    assert classify_activity(x)['video_capture_valid']
    assert not classify_activity(x)['playback_goal_met']


def test_ad_or_player_presence_does_not_prove_main_content():
    x={'playback':{'ad_observed':True,'primary_content_seconds':0,
                   'diagnostics':{'counts':{'playing':20}}}}
    assert not classify_activity(x)['video_capture_valid']


def test_main_content_evidence_without_configured_target():
    assert classify_activity({'activity_outcome':{'primary_content_observed':True}})['video_capture_valid']
    assert classify_activity({'playback':{'primary_content_seconds':0.1}})['video_capture_valid']


@pytest.mark.parametrize('scheme,key', [('LORO', 'repetition'), ('LOUO', 'target_domain')])
def test_outer_views_stay_together(scheme, key):
    rows = [{'target_domain': u, 'repetition': r, 'protocol': p}
            for u in ['a', 'b', 'c'] for r in [1,2,3] for p in ['SS','V']]
    seen = []
    for held, tr, te in split_indices(rows, scheme):
        assert {rows[i][key] for i in tr}.isdisjoint({rows[i][key] for i in te})
        seen.extend(te)
    assert sorted(seen) == list(range(len(rows)))


def test_oracle_never_uses_test_and_unseen_falls_back():
    rows = [{'u': 'a'}, {'u': 'a'}, {'u': 'b'}]
    value, fallback = conditional_mean(rows, [0,1], [1,3,1000], 2, ['u'])
    assert value == 2 and fallback


def test_training_imputer_does_not_change_at_inference():
    model = pipeline(Ridge()).fit([[1, np.nan], [2, 3], [3, 5]], [1,2,3])
    initial = model[0].statistics_.copy()
    model.predict([[1e12, np.nan]])
    np.testing.assert_equal(initial, model[0].statistics_)


def test_constant_and_all_missing_features_supported():
    model = pipeline(Ridge()).fit([[0, np.nan]]*4, [1,2,3,4])
    assert np.isfinite(model.predict([[0, np.nan]])).all()


def test_information_prior_and_fano():
    assert entropy_binary(.5) == 1
    assert np.mean(bit_loss([0,1], [.5,.5])) == 1
    error = 129/960
    assert math.isclose(math.log2(3)-entropy_binary(error)-error, .8812717947332168)


def test_algebra_can_predict_delta_without_pre_information():
    post = np.array([1.,2.,4.,8.])
    pre = np.ones(4)
    delta = np.log(post/pre)
    # This success is an identity and is NOT evidence of learned transformation.
    np.testing.assert_allclose(delta, np.log(post)-np.mean(np.log(pre)))


def test_xor_pair_information_does_not_imply_post_information():
    a = np.array([0,0,1,1]); c = np.array([0,1,0,1])
    post = a ^ c
    np.testing.assert_equal(a ^ post, c)
    assert all(c[post == v].mean() == .5 for v in [0,1])


def test_remove_shared_packet_family():
    scalar = ['packet_count', 'fr_runs_per_packet', 'iat_median_us']
    families = {'packet_count':'workload', 'fr_runs_per_packet':'interaction', 'iat_median_us':'timing'}
    assert dropped_columns('packet_count', scalar, families) == ['iat_median_us']


def test_feature_registry_label_mismatch_rejected():
    row = dict(session_id='s', protocol='VLESS', repetition=1, activity_id='u', target_domain='d', is_final=True)
    validate_feature_identity(row, row)
    with pytest.raises(ValueError, match='protocol'):
        validate_feature_identity({**row, 'protocol':'SHADOWSOCKS'}, row)
