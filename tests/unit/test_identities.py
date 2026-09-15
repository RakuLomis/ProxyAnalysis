from __future__ import annotations

import json
from pathlib import Path

from proxy_analysis.indexing.identities import build_entity_descriptors


def _write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def test_shared_carrier_descriptors_are_deduplicated(tmp_path: Path) -> None:
    session = tmp_path / "session"
    _write(session / "manifest.json", {"session_id": "session-1"})
    connections = []
    pcaps = []
    for index, remote_port in enumerate((36001, 36002), start=1):
        connection_id = f"conn-{index}"
        connections.append(
            {
                "connection_id": connection_id,
                "outer_connection_id": "carrier-1",
                "egress": {"outcome": "proxy"},
                "pre_flow": {
                    "network": "tcp",
                    "src_ip": "198.18.0.1",
                    "src_port": 50000 + index,
                    "dst_ip": "198.18.0.2",
                    "dst_port": 443,
                },
                "post_flow": {
                    "network": "udp",
                    "src_ip": "192.0.2.1",
                    "src_port": 55000,
                    "dst_ip": "198.51.100.1",
                    "dst_port": remote_port,
                    "shared": True,
                },
                "carrier_binding": {
                    "carrier_id": "carrier-1",
                    "mode": "shared",
                },
            }
        )
        pcaps.append(
            {
                "connection_id": connection_id,
                "pre_proxy": {
                    "status": "success",
                    "path": f"analysis/{connection_id}/pre.pcap",
                    "artifact_id": f"{connection_id}-pre",
                },
                "post_proxy": {
                    "status": "success",
                    "path": "analysis/carriers/carrier-1/post.pcap",
                    "artifact_id": "carrier-1-post",
                },
            }
        )
    _write(session / "analysis/connection-index-v2.json", {"items": connections})
    _write(session / "analysis/pcap-index-v1.json", {"connections": pcaps})
    descriptors = build_entity_descriptors(session, "HYSTERIA2")
    pre = [item for item in descriptors if item.capture_side == "pre"]
    post = [item for item in descriptors if item.capture_side == "post"]
    assert len(pre) == 2
    assert len(post) == 1
    assert post[0].entity_level == "carrier"
    assert post[0].logical_connection_ids == ("conn-1", "conn-2")
    assert {b.port for _, b in post[0].physical_paths} == {36001, 36002}
