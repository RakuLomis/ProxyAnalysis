"""Audit lifecycle evidence before interpreting shared carrier transformations."""
from __future__ import annotations

from collections import Counter, defaultdict
from decimal import Decimal
import argparse
import calendar
from datetime import datetime
import json
from pathlib import Path

import pyarrow.parquet as pq

from .preflight import write_json, write_table
from .registry import read_json


def timestamp_ns(value: str) -> int:
    whole, _, fraction = value.removesuffix("Z").partition(".")
    seconds = calendar.timegm(datetime.strptime(whole, "%Y-%m-%dT%H:%M:%S").timetuple())
    return seconds * 1_000_000_000 + int(Decimal("0." + (fraction or "0")) * 1_000_000_000)


def bounded_events(events: list[dict], summary: dict) -> list[dict]:
    snapshots = summary.get("trace_snapshot", {}).get("traces", [])
    if len(snapshots) != 1 or not snapshots[0].get("barrier_verified"):
        raise ValueError("single verified trace barrier required")
    snapshot = snapshots[0]
    cutoff = snapshot["cutoff_event_seq"]
    causal = set(snapshot.get("causal_tail_event_seqs", []))
    return [e for e in events if e.get("event_seq", cutoff + 1) <= cutoff
            or e.get("event_seq") in causal]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output_root", type=Path)
    args = parser.parse_args()
    root = args.output_root
    registry = pq.read_table(root / "run_registry.parquet").to_pylist()
    global_opens = defaultdict(list)
    cached = {}
    # Search all 275 attempts, including earlier captures, for missing carrier opens.
    for row in registry:
        path = Path(row["session_path"])
        events = [json.loads(line) for line in (path / "raw/mihomo-trace.jsonl").read_text(
            encoding="utf-8").splitlines() if line.strip()]
        for event in events:
            if event.get("type") == "carrier_open":
                global_opens[event.get("carrier_id")].append(row["session_id"])
        if row["protocol"] == "HYSTERIA2" and row["is_final"]:
            cached[row["session_id"]] = events
    results = []
    for row in registry:
        if row["session_id"] not in cached:
            continue
        path = Path(row["session_path"])
        flows = read_json(path / "analysis/flow-index.json")["items"]
        summary = read_json(path / "analysis/summary.json")
        try:
            events = bounded_events(cached[row["session_id"]], summary)
            trace_error = None
        except ValueError as exc:
            events = []
            trace_error = str(exc)
        audit_path = root / "preflight-sessions" / (row["session_id"] + ".json")
        audit = read_json(audit_path) if audit_path.is_file() else {}
        for carrier in audit.get("carriers", []):
            cid = carrier["carrier_id"]
            selected_flows = [f for f in flows if f.get("carrier_binding", {}).get("carrier_id") == cid]
            logical_ids = {f["conn_id"] for f in selected_flows}
            related = [e for e in events if e.get("carrier_id") == cid or e.get("outer_conn_id") == cid]
            bindings = {e.get("logical_conn_id", e.get("conn_id")) for e in related
                        if e.get("type") == "logical_carrier_bind"}
            opens = [e for e in related if e.get("type") == "carrier_open"]
            starts = {e.get("conn_id") for e in events if e.get("type") in {"tcp_connect", "udp_connect"}}
            closes = {e.get("conn_id") for e in events if e.get("type") in {"tcp_close", "udp_close"}}
            reasons = []
            if trace_error:
                reasons.append("trace_boundary_unverified")
            if not opens:
                reasons.append("carrier_open_not_in_session_trace")
            if not global_opens[cid]:
                reasons.append("carrier_open_not_in_any_attempt_trace")
            if logical_ids - bindings or bindings - logical_ids:
                reasons.append("trace_index_membership_mismatch")
            if logical_ids - starts:
                reasons.append("member_start_not_observed")
            if logical_ids - closes:
                reasons.append("member_close_not_in_bounded_trace")
            if carrier["members_without_pre_packets"]:
                reasons.append("member_pre_packets_missing")
            if carrier["ambiguous_pre_members"]:
                reasons.append("member_pre_tuple_ambiguous")
            if not carrier["post_packets_observed"]:
                reasons.append("carrier_post_packets_missing")
            # No active-member inventory at capture start is available in this contract.
            if not opens:
                reasons.append("initial_active_member_inventory_unavailable")
            results.append({**carrier, "target_domain": row["target_domain"],
                            "repetition": row["repetition"],
                            "bounded_trace_events": len(events),
                            "local_carrier_open_events": len(opens),
                            "global_carrier_open_sessions": len(set(global_opens[cid])),
                            "missing_member_starts": len(logical_ids - starts),
                            "missing_member_closes": len(logical_ids - closes),
                            "index_members_without_trace_bind": len(logical_ids - bindings),
                            "trace_bind_members_without_index": len(bindings - logical_ids),
                            "path_update_events": sum(e.get("type") == "carrier_path_update" for e in related),
                            "system_scope_validated": not reasons,
                            "gate_reasons_json": json.dumps(reasons)})
    write_table(root / "carrier_lifecycle_gate.parquet", results)
    write_json(root / "carrier-lifecycle-summary.json", {
        "hy2_session_carriers_audited": len(results),
        "all_indexed_members_observed": sum(r["all_indexed_members_observed"] for r in results),
        "system_scope_validated": sum(r["system_scope_validated"] for r in results),
        "reason_counts": dict(Counter(reason for r in results
                                      for reason in json.loads(r["gate_reasons_json"]))),
        "global_trace_attempts_searched": len(registry),
    })
    print(json.dumps(read_json(root / "carrier-lifecycle-summary.json"), indent=2))


if __name__ == "__main__":
    main()
