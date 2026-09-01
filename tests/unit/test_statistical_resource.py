from proxy_analysis.statistical.resource import _aggregate_long


def test_weighted_url_aggregation_uses_comparison_entity_weight() -> None:
    base = {
        "session_id": "s",
        "target_url_hash": "t",
        "normalized_url_hash": "u",
        "host": "example.com",
        "protocol_dataset": "VLESS",
        "target_domain": "example.com",
        "shared_connection": True,
    }
    rows = [
        {
            **base,
            "comparison_entity_incidence_weight": 0.25,
            "transform__scalar__packet_count__log_ratio": 1.0,
        },
        {
            **base,
            "comparison_entity_incidence_weight": 0.75,
            "transform__scalar__packet_count__log_ratio": 3.0,
        },
    ]
    result = _aggregate_long(rows, level="url", weighted=True, cohort="weighted")
    packet = next(row for row in result if row["metric_id"] == "packet_count")
    assert packet["value"] == 2.5
    assert packet["effective_weight_sum"] == 1.0
