from __future__ import annotations

import json
from pathlib import Path

from proxy_analysis.indexing.traffictracer import audit_session_indexes


def _write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def _session(tmp_path: Path, protocol: str, shared: bool = False) -> Path:
    session = tmp_path / "session"
    connection = {
        "connection_id": "conn-1",
        "request_ids": ["req-1"],
        "outer_connection_id": "outer-1",
        "egress": {"outcome": "proxy"},
        "post_flow": {"network": "udp" if shared else "tcp", "shared": shared},
        "carrier_binding": {
            "carrier_id": "carrier-1",
            "mode": "shared" if shared else "exclusive",
        },
    }
    _write(session / "manifest.json", {"session_id": "session-1"})
    _write(session / "analysis/connection-index-v2.json", {"items": [connection]})
    _write(
        session / "analysis/request-index-v2.json",
        {
            "items": [
                {
                    "request_id": "req-1",
                    "request_occurrence_id": "occ-1",
                    "connection_id": "conn-1",
                }
            ]
        },
    )
    _write(session / "analysis/flow-index.json", {"items": [{"flow_id": "flow-1"}]})
    _write(
        session / "analysis/pcap-index-v1.json",
        {
            "connections": [
                {
                    "connection_id": "conn-1",
                    "pre_proxy": {"status": "success"},
                    "post_proxy": {"status": "success"},
                }
            ]
        },
    )
    return session


def test_vless_exclusive_connection_is_pair_eligible(tmp_path: Path) -> None:
    audit = audit_session_indexes(_session(tmp_path, "VLESS"), "VLESS")
    assert audit.eligible_exclusive_pair_count == 1
    assert audit.eligibility[0].eligible is True
    assert audit.request_connection_orphans == 0


def test_hysteria2_logical_connection_is_never_exclusive_pair(tmp_path: Path) -> None:
    audit = audit_session_indexes(
        _session(tmp_path, "HYSTERIA2", shared=True), "HYSTERIA2"
    )
    assert audit.eligible_exclusive_pair_count == 0
    assert audit.shared_proxy_connection_count == 1
    assert audit.eligibility[0].reason == "shared_carrier"

