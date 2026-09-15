import pytest

from proxy_analysis.alignment.build import (
    _aggregate_page_entities,
    _histogram_js,
    _workload_from_entities,
    summarize_url_index,
)
from proxy_analysis.alignment.urls import endpoint_role, host_matches_domain, url_identity
from proxy_analysis.alignment.quality import _sum_to_one_error_count, _target_protocol_errors


def test_url_identity_strips_query_and_fragment_for_normalized_hash() -> None:
    left = url_identity("HTTPS://Example.COM:443/a/b?token=one#fragment")
    right = url_identity("https://example.com/a/b?token=two")
    assert left.resource_url_hash != right.resource_url_hash
    assert left.normalized_url_hash == right.normalized_url_hash
    assert left.host == "example.com"
    assert left.path_depth == 2
    assert left.has_query is True


def test_url_identity_failure_and_subdomain_match() -> None:
    identity = url_identity("not a URL")
    assert identity.url_parse_status == "failed"
    assert identity.normalized_url_hash is None
    assert host_matches_domain("cdn.example.com", "example.com") is True
    assert host_matches_domain("notexample.com", "example.com") is False


def test_endpoint_roles_do_not_call_proxy_endpoint_an_origin() -> None:
    assert endpoint_role("198.18.1.2", side="pre", outcome="proxy") == "fake_ip"
    assert endpoint_role("203.0.113.8", side="post", outcome="proxy") == "proxy_endpoint"
    assert (
        endpoint_role("203.0.113.8", side="post", outcome="direct")
        == "direct_origin_candidate"
    )


def test_url_index_summary_requires_three_protocols() -> None:
    rows = [
        {
            "target_url_hash": "target",
            "protocol_dataset": protocol,
            "request_occurrence_id": f"r-{protocol}",
            "session_id": f"s-{protocol}",
            "url_parse_status": "parsed",
            "connection_id": "c",
            "pairing_semantics": "exclusive_pair",
            "cdn_endpoint_observed": False,
        }
        for protocol in ("HYSTERIA2", "SHADOWSOCKS", "VLESS")
    ]
    summary = summarize_url_index(rows)
    assert summary["target_urls_with_all_protocols"] == 1
    assert summary["cdn_endpoint_observed_count"] == 0


def test_page_entity_aggregation_sums_additive_features_and_recomputes_rates() -> None:
    feature_names = [
        "packet_count",
        "volume__up_packets",
        "volume__down_packets",
        "histograms__transport_payload_len__counts__000",
        "histograms__transport_payload_len__counts__001",
        "transition_nonempty__n_pp",
        "transition_nonempty__n_pm",
        "flow_reversal__observed__fr_reversals",
        "flow_reversal__observed__nonempty_packet_count",
        "flow_reversal__observed__payload_bytes",
        "flow_reversal__observed__duration_ns",
    ]
    rows = [
        {
            "transport_protocol": "tcp",
            "packet_count": 10,
            "volume__up_packets": 6,
            "volume__down_packets": 4,
            "histograms__transport_payload_len__counts__000": 2,
            "histograms__transport_payload_len__counts__001": 8,
            "transition_nonempty__n_pp": 3,
            "transition_nonempty__n_pm": 1,
            "flow_reversal__observed__fr_reversals": 2,
            "flow_reversal__observed__nonempty_packet_count": 8,
            "flow_reversal__observed__payload_bytes": 1024,
            "flow_reversal__observed__duration_ns": 1_000_000_000,
        },
        {
            "transport_protocol": "tcp",
            "packet_count": 20,
            "volume__up_packets": 5,
            "volume__down_packets": 15,
            "histograms__transport_payload_len__counts__000": 3,
            "histograms__transport_payload_len__counts__001": 17,
            "transition_nonempty__n_pp": 1,
            "transition_nonempty__n_pm": 3,
            "flow_reversal__observed__fr_reversals": 4,
            "flow_reversal__observed__nonempty_packet_count": 16,
            "flow_reversal__observed__payload_bytes": 2048,
            "flow_reversal__observed__duration_ns": 2_000_000_000,
        },
    ]
    result = _aggregate_page_entities(rows, feature_names)
    assert result["entity_count"] == 2
    assert result["aggregate__packet_count"] == 30
    assert result["aggregate__volume__up_packets"] == 11
    assert result["aggregate__volume__down_packets"] == 19
    assert result["aggregate__histograms__transport_payload_len__counts__000"] == 5
    assert result["derived__transition_nonempty__p_pp"] == pytest.approx(0.5)
    assert result["aggregate__proxy_reversal__fr_reversals"] == 6
    assert result["derived__proxy_reversal__fr_norm_packets"] == pytest.approx(0.25)
    assert result["derived__proxy_reversal__fr_per_kib"] == pytest.approx(2.0)
    assert result["derived__proxy_reversal__fr_per_second"] == pytest.approx(2.0)


def test_histogram_js_is_zero_for_identical_page_distributions() -> None:
    features = {
        "aggregate__histograms__iat_us__counts__000": 3,
        "aggregate__histograms__iat_us__counts__001": 7,
    }
    assert _histogram_js(features, features, "iat_us") == pytest.approx(0.0)


def test_alignment_weight_gate_groups_by_independence_key() -> None:
    rows = [
        {"session_id": "s", "connection_id": "c", "weight": 0.25},
        {"session_id": "s", "connection_id": "c", "weight": 0.75},
        {"session_id": "s", "connection_id": "d", "weight": 1.0},
    ]
    assert _sum_to_one_error_count(rows, ("session_id", "connection_id"), "weight") == 0
    rows[0]["weight"] = 0.5
    assert _sum_to_one_error_count(rows, ("session_id", "connection_id"), "weight") == 1


def test_target_protocol_gate_allows_multiple_request_rows_only_for_index() -> None:
    rows = [
        {"target_url_hash": "u", "protocol_dataset": protocol}
        for protocol in ("HYSTERIA2", "SHADOWSOCKS", "VLESS", "VLESS")
    ]
    assert (
        _target_protocol_errors(rows, require_exactly_one_row_per_protocol=False) == 0
    )
    assert (
        _target_protocol_errors(rows, require_exactly_one_row_per_protocol=True) == 1
    )


def test_workload_aggregation_adds_unique_entity_values() -> None:
    entities = [
        {
            "packet_count": 2,
            "volume__total_packets": 2,
            "volume__total_transport_bytes": 100,
            "volume__total_ip_bytes": 140,
            "volume__up_packets": 1,
            "volume__down_packets": 1,
            "volume__up_transport_bytes": 40,
            "volume__down_transport_bytes": 60,
        }
    ]
    workload = _workload_from_entities(entities)
    assert workload["entity_count"] == 1
    assert workload["volume__total_transport_bytes"] == 100


def test_target_protocol_gate_separates_repetitions():
    rows=[{'target_url_hash':'u','protocol_dataset':p,'repetition':r}
          for r in range(1,6) for p in ['HYSTERIA2','SHADOWSOCKS','VLESS']]
    assert _target_protocol_errors(rows,require_exactly_one_row_per_protocol=True)==0
    rows.pop()
    assert _target_protocol_errors(rows,require_exactly_one_row_per_protocol=True)==1
