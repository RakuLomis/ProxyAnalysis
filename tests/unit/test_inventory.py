from __future__ import annotations

import json
from pathlib import Path

from proxy_analysis.inventory import InventoryScanner, inventory_summary


def _make_session(root: Path, protocol: str = "VLESS") -> Path:
    session = root / "datasets" / protocol / "example.com" / "example-page"
    required = (
        "raw/tun.pcap",
        "raw/phys.pcap",
        "raw/netlog.json",
        "raw/cdp.json",
        "raw/mihomo-trace.jsonl",
        "raw/capture-context.json",
        "analysis/summary.json",
        "analysis/connection-index-v2.json",
        "analysis/request-index-v2.json",
        "analysis/flow-index.json",
        "analysis/pcap-index-v1.json",
    )
    for relative in required:
        path = session / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"{}")
    manifest = {
        "session_id": "session-1",
        "state": "completed",
        "target": {"domain": "example.com", "url": "https://example.com/"},
        "component_versions": {"traffictracer": {"version": "1.0", "commit": "abc"}},
        "artifacts": [
            {"path": "raw/tun.pcap", "size_bytes": 2, "artifact_id": "tun"},
            {"path": "raw/phys.pcap", "size_bytes": 2, "artifact_id": "phys"},
        ],
    }
    (session / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    return session


def test_inventory_discovers_and_summarizes_session(tmp_path: Path) -> None:
    _make_session(tmp_path)
    sessions = InventoryScanner(tmp_path).scan()
    assert len(sessions) == 1
    assert sessions[0].protocol_dataset == "VLESS"
    assert sessions[0].issues == ()
    assert inventory_summary(sessions) == {
        "session_count": 1,
        "protocol_session_counts": {"VLESS": 1},
        "sessions_with_issues": 0,
        "sessions_with_errors": 0,
        "issue_counts": {},
        "severity_counts": {},
    }


def test_inventory_reports_declared_size_mismatch(tmp_path: Path) -> None:
    session = _make_session(tmp_path)
    manifest_path = session / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["artifacts"][0]["size_bytes"] = 999
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    issues = InventoryScanner(tmp_path).scan()[0].issues
    assert [issue.code for issue in issues] == ["artifact_size_mismatch"]
    assert [issue.severity for issue in issues] == ["error"]
