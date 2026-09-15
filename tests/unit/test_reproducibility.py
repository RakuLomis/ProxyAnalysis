from __future__ import annotations

import json
from pathlib import Path

import pytest

from proxy_analysis.features.models import PacketMeasure
from proxy_analysis.features.reversal import reversal_features
from proxy_analysis.inventory import InventoryScanner
from proxy_analysis.reproducibility.registry import discover_runs
from proxy_analysis.reproducibility.preflight import tuple_key
from proxy_analysis.reproducibility.scope_gate import bounded_events, timestamp_ns
from proxy_analysis.reproducibility.metadata_report import document_route


def make_pipeline(root: Path) -> None:
    pipeline = {"pipeline_id": "pipeline", "targets": [{"index": 0,
                "domain": "map.test", "url": "https://map.test/#map=13"}],
                "runs": [{"run_id": "run", "target_index": 0, "ordinal": 1,
                          "expected_protocol": "hysteria2", "repetition_index": 1,
                          "session_ids": ["final"], "prior_session_ids": ["first"],
                          "quality": {}}]}
    (root / "pipeline-manifest.json").write_text(json.dumps(pipeline))
    for attempt, sid in enumerate(("first", "final")):
        path = root / "runs" / "run" / sid / "domain" / "activity"
        (path / "raw").mkdir(parents=True)
        (path / "manifest.json").write_text(json.dumps({"session_id": sid}))
        (path / "raw/capture-context.json").write_text(json.dumps({"orchestration": {
            "run_id": "run", "target_index": 0, "repetition_index": 1,
            "application_retry_attempt": attempt}}))


def test_pipeline_discovery_excludes_retry_from_inventory(tmp_path: Path) -> None:
    make_pipeline(tmp_path)
    rows = discover_runs(tmp_path)
    assert len(rows) == 2
    assert [r["is_final"] for r in rows] == [False, True]
    assert rows[0]["activity_id"] == rows[1]["activity_id"]
    assert rows[0]["target_url"].endswith("#map=13")
    assert [s.session_id for s in InventoryScanner(tmp_path).scan()] == ["final"]


def test_pipeline_rejects_duplicate_cells(tmp_path: Path) -> None:
    make_pipeline(tmp_path)
    path = tmp_path / "pipeline-manifest.json"
    data = json.loads(path.read_text())
    data["runs"].append(data["runs"][0])
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="duplicate experiment cell"):
        discover_runs(tmp_path)


def test_pipeline_rejects_context_mismatch(tmp_path: Path) -> None:
    make_pipeline(tmp_path)
    path = tmp_path / "runs/run/final/domain/activity/raw/capture-context.json"
    path.write_text(json.dumps({"orchestration": {"repetition_index": 2}}))
    with pytest.raises(ValueError, match="context mismatch"):
        discover_runs(tmp_path)


def test_bidirectional_tuple_keeps_transport_and_ports() -> None:
    flow = dict(network="tcp", src_ip="a", dst_ip="b", src_port=1, dst_port=2)
    reverse = dict(network="tcp", src_ip="b", dst_ip="a", src_port=2, dst_port=1)
    assert tuple_key(flow) == tuple_key(reverse)
    assert tuple_key(flow) != tuple_key({**flow, "network": "udp"})
    assert tuple_key({}) is None


def packet(ordinal, timestamp, direction, payload, classification=None):
    return PacketMeasure(str(ordinal), timestamp, ordinal, direction,
                         payload, payload + 40, payload + 54, classification)


def test_runs_normalization_empty_single_and_zero_duration() -> None:
    assert reversal_features([]).fr_runs_per_packet is None
    single = reversal_features([packet(1, 0, 1, 1024)])
    assert single.fr_runs_per_packet == 1
    assert single.fr_runs_per_kib == 1
    assert single.fr_runs_per_second is None
    assert single.fr_reversals == 0
    both = reversal_features([packet(2, 0, -1, 1024), packet(1, 0, 1, 1024)])
    assert both.fr_runs == 2
    assert both.fr_runs_per_second is None


def test_runs_ack_filter_sort_and_retransmission_policy() -> None:
    packets = [packet(4, 3_000_000_000, 1, 1024),
               packet(1, 0, 1, 1024), packet(2, 1_000_000_000, -1, 0),
               packet(3, 2_000_000_000, -1, 1024, "full_retransmission")]
    full = reversal_features(packets)
    assert full.fr_runs == 3
    assert full.fr_runs_per_second == 1
    assert full.fr_per_second == pytest.approx(2 / 3)
    unique = reversal_features(packets, unique_seq=True)
    assert unique.fr_runs == 1
    assert unique.fr_runs_per_packet == 0.5
    partial = reversal_features([packet(1, 0, 1, 1),
                                 packet(2, 1, -1, 1, "partial_retransmission")], unique_seq=True)
    assert partial.fr_runs == 2


def test_trace_boundary_does_not_include_unrelated_late_close() -> None:
    events = [{"event_seq": n} for n in (1, 2, 3, 100)]
    summary = {"trace_snapshot": {"traces": [{"barrier_verified": True,
               "cutoff_event_seq": 2, "causal_tail_event_seqs": [3]}]}}
    assert [e["event_seq"] for e in bounded_events(events, summary)] == [1, 2, 3]
    with pytest.raises(ValueError, match="verified trace barrier"):
        bounded_events(events, {})


def test_trace_timestamp_preserves_nanoseconds() -> None:
    assert timestamp_ns("1970-01-01T00:00:01.123456789Z") == 1_123_456_789
    assert timestamp_ns("1970-01-01T00:00:01Z") == 1_000_000_000


def test_main_document_route_does_not_use_proxy_subresource() -> None:
    connections = [{"connection_id": "main", "egress": {"outcome": "direct"}},
                   {"connection_id": "other", "egress": {"outcome": "proxy"}}]
    requests = [{"resource_type": "Document", "target_id": "page", "url": "https://a/",
                 "connection_id": "main"},
                {"resource_type": "Document", "target_id": "iframe", "url": "https://a/",
                 "connection_id": "other"}]
    result = document_route(requests, connections,
                            {"main_target_id": "page", "final_url": "https://a/#view"})
    assert result["main_document_route"] == "direct"
    assert result["document_occurrences"] == 1


def test_missing_main_document_identity_is_unavailable() -> None:
    assert document_route([], [], {})["main_document_route"] == "unavailable"
