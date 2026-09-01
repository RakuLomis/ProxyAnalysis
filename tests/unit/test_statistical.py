from pathlib import Path

import pytest

from proxy_analysis.statistical.config import MetricSpec, StatisticalConfig
from proxy_analysis.statistical.marts import _matched_key_count


def test_statistical_config_loads_frozen_metric_dictionary() -> None:
    config = StatisticalConfig.load(Path("configs/statistical-analysis.yaml"))
    assert config.minimum_paired_clusters == 20
    assert len(config.metrics) == 12
    assert len(config.sha256) == 64
    assert config.interpretation_policy["transition_p_pm"]["exclude_from_a_core"] is False
    fr = next(metric for metric in config.metrics if metric.metric_id == "flow_reversals")
    assert fr.protocols == ("SHADOWSOCKS", "VLESS")


def test_distance_metric_cannot_define_pre_post_columns() -> None:
    with pytest.raises(ValueError, match="distance metric"):
        MetricSpec.from_mapping(
            {
                "id": "bad",
                "family": "x",
                "transform": "distance",
                "protocols": ["VLESS"],
                "practical_threshold": "x",
                "distance_column": "distance",
                "pre_column": "pre",
            }
        )


def test_matched_key_count_requires_all_three_protocols() -> None:
    rows = [
        {"target": "a", "resource": "r", "protocol_dataset": protocol}
        for protocol in ("HYSTERIA2", "SHADOWSOCKS", "VLESS")
    ]
    rows.append({"target": "b", "resource": "r", "protocol_dataset": "VLESS"})
    assert _matched_key_count(rows, ("target", "resource")) == 1
