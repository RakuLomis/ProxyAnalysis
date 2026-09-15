"""Checkpointed raw capture validation and carrier-member observability audit."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import asdict
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import sys
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq

from ..indexing.traffictracer import audit_session_indexes
from ..inventory import InventoryScanner, inventory_summary
from ..parsing import PcapNgReader, decode_packet
from .registry import discover_runs, read_json

VERSION = 1


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n",
                         encoding="utf-8")
    os.replace(temporary, path)


def write_table(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    pq.write_table(pa.Table.from_pylist(rows), temporary, compression="zstd")
    os.replace(temporary, path)


def tuple_key(flow: dict[str, Any]) -> tuple | None:
    try:
        protocol = flow["network"].lower()
        left = (flow["src_ip"], int(flow["src_port"]))
        right = (flow["dst_ip"], int(flow["dst_port"]))
    except (KeyError, TypeError, ValueError):
        return None
    if protocol not in {"tcp", "udp"} or not left[0] or not right[0]:
        return None
    return (protocol, *sorted((left, right)))


def capture_audit(path: Path, tracked: set[tuple]) -> tuple[dict, dict]:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b""):
            digest.update(block)
    result = {"size_bytes": path.stat().st_size, "sha256": digest.hexdigest(),
              "packet_count": 0, "snaplen_truncated_packets": 0,
              "timestamp_regressions": 0, "first_timestamp_ns": None,
              "last_timestamp_ns": None, "parse_error": None}
    matches: dict[tuple, dict] = {}
    previous = None
    decoded = Counter()
    reader = PcapNgReader(path)
    try:
        for packet in reader:
            result["packet_count"] += 1
            result["snaplen_truncated_packets"] += packet.captured_len < packet.original_len
            timestamp = packet.timestamp_ns
            if previous is not None:
                result["timestamp_regressions"] += timestamp < previous
            previous = timestamp
            start, end = result["first_timestamp_ns"], result["last_timestamp_ns"]
            result["first_timestamp_ns"] = timestamp if start is None else min(start, timestamp)
            result["last_timestamp_ns"] = timestamp if end is None else max(end, timestamp)
            if tracked:
                parsed = decode_packet(packet.link_type, packet.packet_data)
                decoded[parsed.decode_status] += 1
                key = tuple_key({"network": parsed.transport_protocol or "",
                                 "src_ip": parsed.ip_src, "src_port": parsed.src_port,
                                 "dst_ip": parsed.ip_dst, "dst_port": parsed.dst_port})
                if key in tracked:
                    match = matches.setdefault(key, {"packets": 0, "payload_bytes": 0,
                                                      "first_ns": timestamp, "last_ns": timestamp})
                    match["packets"] += 1
                    match["payload_bytes"] += parsed.transport_payload_len or 0
                    match["first_ns"] = min(match["first_ns"], timestamp)
                    match["last_ns"] = max(match["last_ns"], timestamp)
    except Exception as exc:
        result["parse_error"] = f"{type(exc).__name__}: {exc}"
    result["interfaces"] = [asdict(item) for item in reader.interfaces]
    result["decoded_status_counts"] = dict(decoded)
    return result, matches


def audit_one(row: dict) -> dict:
    path = Path(row["session_path"])
    flows_object = read_json(path / "analysis/flow-index.json")
    flows = flows_object["items"]
    connections = read_json(path / "analysis/connection-index-v2.json")["items"]
    summary = read_json(path / "analysis/summary.json")
    members = []
    tuple_owners = defaultdict(set)
    for flow in flows:
        binding = flow.get("carrier_binding") or {}
        if flow.get("egress_outcome") != "proxy" or not binding.get("carrier_id"):
            continue
        key = tuple_key(flow.get("pre_flow") or {})
        if key:
            tuple_owners[key].add((binding["carrier_id"], flow["flow_id"]))
        members.append((flow, key))
    pre_info, pre_matches = capture_audit(path / "raw/tun.pcap", set(tuple_owners))
    post_keys = {tuple_key(p) for f, _ in members
                 for p in (f.get("carrier_binding") or {}).get("physical_paths", [])}
    post_keys.discard(None)
    post_info, post_matches = capture_audit(path / "raw/phys.pcap", post_keys)
    membership = []
    for flow, key in members:
        binding = flow["carrier_binding"]
        observed = pre_matches.get(key, {})
        membership.append({
            "session_id": row["session_id"], "protocol": row["protocol"],
            "carrier_id": binding["carrier_id"], "flow_id": flow["flow_id"],
            "attribution_scope": flow.get("attribution_scope"),
            "generation": binding.get("generation"), "relation": binding.get("relation"),
            "pre_tuple_complete": key is not None,
            "pre_tuple_ambiguous": len(tuple_owners.get(key, [])) > 1,
            "pre_packets_observed": observed.get("packets", 0),
            "pre_payload_bytes_observed": observed.get("payload_bytes", 0),
            "pre_first_ns": observed.get("first_ns"), "pre_last_ns": observed.get("last_ns"),
            "pre_tuple_json": json.dumps(key),
        })
    carrier_rows = []
    for cid in sorted({item["carrier_id"] for item in membership}):
        group = [item for item in membership if item["carrier_id"] == cid]
        paths = {tuple_key(p) for f, _ in members if f["carrier_binding"]["carrier_id"] == cid
                 for p in f["carrier_binding"].get("physical_paths", [])}
        paths.discard(None)
        selected = [post_matches[k] for k in paths if k in post_matches]
        missing = sum(item["pre_packets_observed"] == 0 for item in group)
        carrier_rows.append({
            "session_id": row["session_id"], "protocol": row["protocol"],
            "carrier_id": cid, "inner_members": len(group),
            "page_members": sum(i["attribution_scope"] == "page_attributed" for i in group),
            "members_without_pre_packets": missing,
            "ambiguous_pre_members": sum(i["pre_tuple_ambiguous"] for i in group),
            "incomplete_pre_members": sum(not i["pre_tuple_complete"] for i in group),
            "post_packets_observed": sum(i["packets"] for i in selected),
            "post_payload_bytes_observed": sum(i["payload_bytes"] for i in selected),
            "post_first_ns": min((i["first_ns"] for i in selected), default=None),
            "post_last_ns": max((i["last_ns"] for i in selected), default=None),
            "all_indexed_members_observed": missing == 0 and bool(selected),
            # Observation alone does not prove complete lifetimes or trace completeness.
            "system_scope_validated": False,
            "gate_reason": "missing_pre_member_packets" if missing else
                           "lifetime_and_trace_completeness_not_validated",
        })
    quality = json.loads(row["quality_json"])
    proxy_count = sum(c.get("egress", {}).get("outcome") == "proxy" for c in connections)
    reasons = [f"{k}:{quality.get(k, {}).get('state', 'unavailable')}"
               for k in ("application", "capture_integrity", "correlation")
               if quality.get(k, {}).get("state") != "passed"]
    if not proxy_count:
        reasons.append("no_page_proxy_connection")
    for side, info in (("pre", pre_info), ("post", post_info)):
        if info["parse_error"]:
            reasons.append(f"{side}_pcap_parse_error")
        if info["snaplen_truncated_packets"]:
            reasons.append(f"{side}_snaplen_truncation")
    expected_flow_count = flows_object.get("pagination", {}).get("total")
    if expected_flow_count is not None and expected_flow_count != len(flows):
        reasons.append("flow_index_incomplete")
    return {"session_id": row["session_id"], "protocol": row["protocol"],
            "target_domain": row["target_domain"], "repetition": row["repetition"],
            "raw_capture_audit": {"pre": pre_info, "post": post_info},
            "membership": membership, "carriers": carrier_rows,
            "eligibility": {"session_id": row["session_id"],
                            "activity_id": row["activity_id"],
                            "protocol": row["protocol"], "repetition": row["repetition"],
                            "target_domain": row["target_domain"],
                            "page_proxy_connections": proxy_count,
                            "page_context_candidate": not reasons,
                            "reasons_json": json.dumps(reasons),
                            "system_scope_validated": False},
            "flow_index_items": len(flows), "flow_index_declared_total": expected_flow_count,
            "activity_outcome": summary.get("activity_outcome"),
            "index_audit": {k: v for k, v in asdict(audit_session_indexes(
                path, row["protocol"])).items() if k != "eligibility"}}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset_root", type=Path)
    parser.add_argument("output_root", type=Path)
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    out = args.output_root
    rows = discover_runs(args.dataset_root)
    write_table(out / "run_registry.parquet", rows)
    environment = {"python": sys.version, "executable": sys.executable,
                   "platform": platform.platform(), "packages": {}}
    for name in ("numpy", "scipy", "pyarrow", "dpkt", "PyYAML", "pytest", "statsmodels"):
        try:
            environment["packages"][name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            environment["packages"][name] = None
    write_json(out / "environment.json", environment)
    write_json(out / "inventory-summary.json", inventory_summary(
        InventoryScanner(args.dataset_root).scan()))
    selected = [r for r in rows if r["is_final"]]
    if args.limit:
        selected = selected[:args.limit]
    audits = []
    code_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    for index, row in enumerate(selected, 1):
        destination = out / "preflight-sessions" / (row["session_id"] + ".json")
        path = Path(row["session_path"])
        tracked = [path / f for f in ("manifest.json", "raw/tun.pcap", "raw/phys.pcap",
                    "analysis/flow-index.json", "analysis/connection-index-v2.json",
                    "analysis/summary.json")]
        fingerprint = hashlib.sha256(json.dumps([
            VERSION, code_hash, row, [(str(p), p.stat().st_size, p.stat().st_mtime_ns)
                                     for p in tracked]], sort_keys=True).encode()).hexdigest()
        existing = read_json(destination) if destination.is_file() else {}
        if existing.get("source_fingerprint") == fingerprint:
            audit = existing
        else:
            audit = audit_one(row)
            audit["source_fingerprint"] = fingerprint
            write_json(destination, audit)
        audits.append(audit)
        print(f"[{index}/{len(selected)}] {row['protocol']} {row['target_domain']} "
              f"r{row['repetition']} carriers={len(audit['carriers'])}", flush=True)
    write_table(out / "cohort_eligibility.parquet", [a["eligibility"] for a in audits])
    write_table(out / "carrier_membership.parquet", [m for a in audits for m in a["membership"]])
    write_table(out / "carrier_scope_audit.parquet", [c for a in audits for c in a["carriers"]])
    write_json(out / "preflight-summary.json", {
        "registered_attempts": len(rows), "final_sessions": sum(r["is_final"] for r in rows),
        "audited_sessions": len(audits),
        "page_context_candidates": sum(a["eligibility"]["page_context_candidate"] for a in audits),
        "pcap_parse_errors": sum(bool(c["parse_error"]) for a in audits
                                 for c in a["raw_capture_audit"].values()),
        "snaplen_truncated_packets": sum(c["snaplen_truncated_packets"] for a in audits
                                         for c in a["raw_capture_audit"].values()),
        "packet_count": sum(c["packet_count"] for a in audits
                            for c in a["raw_capture_audit"].values()),
        "timestamp_regressions": sum(c["timestamp_regressions"] for a in audits
                                     for c in a["raw_capture_audit"].values()),
    })


if __name__ == "__main__":
    main()
