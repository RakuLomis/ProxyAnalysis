"""Small independent fixtures for the descriptive-report contract."""
from pathlib import Path
import sys

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'eval/itemwise_statistics'))
from extract import ROOT, arrays, extended, distances, resource, stats
from report import delta, transform_kind
from proxy_analysis.config import FeatureConfig
from proxy_analysis.features.models import PacketMeasure


def packet(i, t, d, length):
    return PacketMeasure(str(i), t, i, d, length, length+40, length+54)


def test_strict_zero_and_bounded_policy():
    assert delta(0, 1, 'log_ratio') == (None, 'pre_zero')
    assert delta(1, 0, 'log_ratio') == (None, 'post_zero')
    assert delta(0, 0, 'log_ratio') == (None, 'both_zero')
    assert delta(None, 3, 'log_ratio')[0] is None
    assert np.isclose(delta(3, 6, 'log_ratio')[0], np.log(2))
    assert delta(0, 1, 'difference') == (1, None)
    assert transform_kind('fr_runs_per_packet') == 'difference'
    assert transform_kind('transition_entropy') == 'difference'


def test_iat_does_not_cross_connections_and_sorts_regressions():
    groups = [[packet(1, 4000, 1, 10), packet(2, 1000, -1, 30)],
              [packet(3, 999000, 1, 0)]]
    lengths, iat = arrays(groups)
    assert lengths == [30, 10]
    assert iat == [3.0]


def test_fr_and_burst_distinct_denominators():
    cfg = FeatureConfig.load(ROOT/'configs/feature-defaults.yaml')
    groups = [[packet(1, 1000, 1, 10), packet(2, 2000, -1, 0), packet(3, 3000, 1, 20)],
              [packet(4, 4000, -1, 30), packet(5, 6000, 1, 40)]]
    d = extended(groups, cfg)
    assert d['burst_count'] == 5
    assert d['fr_runs'] == 3 and d['fr_switches'] == 1
    assert d['fr_runs'] == d['fr_switches']+d['nonempty_entity_count']
    assert d['fr_runs_per_packet'] == .75
    assert d['fr_switches_per_possible_transition'] == .5
    assert d['iat_count'] == 3
    assert sum(d['length_hist']) == 4
    assert sum(d['iat_hist']) == 3
    assert d['transport_bytes'] == d['up_transport_bytes']+d['down_transport_bytes']
    assert distances(groups, groups, d, d)['length_js'] == 0
    assert distances(groups, groups, d, d)['iat_wasserstein_log1p_us'] == 0


def test_empty_and_single_packet_features():
    cfg = FeatureConfig.load(ROOT/'configs/feature-defaults.yaml')
    assert extended([], cfg) == {}
    d = extended([[packet(1, 1, 1, 2)]], cfg)
    assert d['fr_runs'] == 1
    assert d['fr_switches_per_possible_transition'] is None
    assert d['iat_median_us'] is None
    assert d['connection_span_concurrency_max'] == 1


def test_resource_identity_preserves_content():
    assert resource('https://www.bilibili.com/video/BV123?p=2') != resource('https://www.bilibili.com/video/BV123')
    assert resource('https://www.bing.com/search?q=x&rdr=1') == resource('https://www.bing.com/search?q=x')


def test_unscaled_mad_and_linear_quantiles():
    d = stats([1, 2, 3, 10])
    assert d['median'] == 2.5
    assert d['mad'] == 1
    assert d['iqr'] == 3
    assert stats([])['median'] is None
