import numpy as np

from proxy_analysis.modeling.baselines import _cluster_bootstrap_ci, _validate_group_split
from proxy_analysis.modeling.datasets import _canonical_reversal
from proxy_analysis.modeling.statistics import benjamini_hochberg, cliffs_delta
from proxy_analysis.modeling.evaluation import (
    ABLATION_RULES,
    _per_class_metrics,
    feature_family,
)


def test_canonical_reversal_selects_transport_semantics() -> None:
    tcp = _canonical_reversal(
        {
            "transport_protocol": "tcp",
            "flow_reversal__observed__fr_runs": 4,
            "carrier_datagram_reversal__observed__fr_runs": None,
        }
    )
    udp = _canonical_reversal(
        {
            "transport_protocol": "udp",
            "flow_reversal__observed__fr_runs": None,
            "carrier_datagram_reversal__observed__fr_runs": 7,
        }
    )
    assert tcp["fr_runs"] == 4
    assert udp["fr_runs"] == 7


def test_group_split_validation_accepts_isolated_groups() -> None:
    rows = [
        {"group_site": "a", "split_by_site": "train", "protocol_dataset": label}
        for label in ("HYSTERIA2", "SHADOWSOCKS", "VLESS")
    ] + [
        {"group_site": "b", "split_by_site": "validation", "protocol_dataset": label}
        for label in ("HYSTERIA2", "SHADOWSOCKS", "VLESS")
    ] + [
        {"group_site": "c", "split_by_site": "test", "protocol_dataset": label}
        for label in ("HYSTERIA2", "SHADOWSOCKS", "VLESS")
    ]
    report = _validate_group_split(
        rows, group_column="group_site", split_column="split_by_site"
    )
    assert report["cross_split_group_count"] == 0


def test_effect_size_and_bh_adjustment() -> None:
    assert cliffs_delta([3, 4], [1, 2]) == 1.0
    adjusted = benjamini_hochberg([0.01, 0.04, 0.03])
    assert adjusted == [0.03, 0.04, 0.04]


def test_cluster_bootstrap_is_deterministic() -> None:
    truth = np.asarray(["A", "B", "A", "B"])
    predicted = np.asarray(["A", "B", "B", "B"])
    groups = np.asarray(["s1", "s1", "s2", "s2"])
    first = _cluster_bootstrap_ci(
        truth, predicted, groups, ["A", "B"], seed=7, repetitions=20
    )
    second = _cluster_bootstrap_ci(
        truth, predicted, groups, ["A", "B"], seed=7, repetitions=20
    )
    assert first == second


def test_formal_ablation_families_exclude_index_shortcuts() -> None:
    assert feature_family("aggregate__volume__total_packets") == "workload_volume"
    assert feature_family("mean__proxy_reversal__fr_norm_packets") == "interaction"
    assert feature_family("post_carrier_count") is None
    assert ABLATION_RULES["a_core_minus_reversal"](
        "mean__transition_nonempty__p_pp"
    )
    assert not ABLATION_RULES["a_core_minus_reversal"](
        "mean__proxy_reversal__fr_norm_packets"
    )
    assert ABLATION_RULES["iat_timing"]("aggregate__histograms__iat_us__counts__001")
    assert not ABLATION_RULES["packet_length"](
        "aggregate__histograms__iat_us__counts__001"
    )


def test_per_class_metrics_from_confusion() -> None:
    result = _per_class_metrics(np.asarray([[8, 2], [1, 9]]), ["A", "B"])
    assert result["A"]["recall"] == 0.8
    assert result["B"]["precision"] == 9 / 11
