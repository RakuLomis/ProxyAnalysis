"""Apply approved label-only decisions; investigate seven socket conflicts."""
from pathlib import Path
import sys
import json
from collections import Counter

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from proxy_analysis.extend_calibration.audit import fs_path, file_hash, read, write, path_identity
from proxy_analysis.extend_calibration.forensic import successful_socket, flow_tuple
from proxy_analysis.parsing.pcapng import PcapNgReader
from proxy_analysis.parsing.packet_decoder import decode_packet


def packets(path, queries):
    # Counts are forensic observations, not new model features.
    stats = {name: dict(packets=0, payload_bytes=0, up_payload=0, down_payload=0,
        syn=0, syn_ack=0, rst=0, first_ns=None, last_ns=None, truncated=0) for name in queries}
    lookup = {}
    for name, flow in queries.items():
        t = flow_tuple(flow)
        rev = (t[0], t[3], t[4], t[1], t[2])
        lookup.setdefault(t, []).append((name, "up"))
        lookup.setdefault(rev, []).append((name, "down"))
    for raw in PcapNgReader(path):
        p = decode_packet(raw.link_type, raw.packet_data)
        t = (p.transport_protocol, p.ip_src, p.src_port, p.ip_dst, p.dst_port)
        for name, direction in lookup.get(t, []):
            s = stats[name]
            s["packets"] += 1
            s["payload_bytes"] += p.transport_payload_len or 0
            s[direction + "_payload"] += p.transport_payload_len or 0
            s["first_ns"] = raw.timestamp_ns if s["first_ns"] is None else min(raw.timestamp_ns, s["first_ns"])
            s["last_ns"] = raw.timestamp_ns if s["last_ns"] is None else max(raw.timestamp_ns, s["last_ns"])
            flags = p.tcp_flags_raw or 0
            s["syn"] += int(bool(flags & 2) and not bool(flags & 16))
            s["syn_ack"] += int(bool(flags & 2) and bool(flags & 16))
            s["rst"] += int(bool(flags & 4))
            s["truncated"] += int(raw.captured_len < raw.original_len)
    return stats


def main():
    prior = ROOT / "outputs/extend-calibration-20260930/run-01"
    out = prior / "forensic-01"
    if (out / "status.json").exists():
        raise RuntimeError("Forensic output already finalized")
    out.mkdir(exist_ok=True)
    review = prior / "g1-review-v2"
    nav = pd.read_parquet(review / "recovered-navigation-proposals.parquet")
    accepted = nav[nav.proposed_label_acceptance_only].copy()
    assert len(accepted) == 6
    accepted["acceptance_applied"] = True
    accepted["scope"] = "business_label_only; no route or capture waiver"
    accepted.to_parquet(out / "accepted-navigation-labels.parquet", index=False)
    write(out / "user-decisions.json", {"user_confirmed": True,
        "authorization": "是，按照推荐口径继续。", "repetitions": [1, 2, 3, 4],
        "classes": 6, "hy2": "measurement_only", "label_acceptances": accepted.session_id.tolist(),
        "training_allowed": False, "replace_attempts": False, "modify_raw_indexes": False})
    sessions = pd.read_parquet(prior / "sessions.parquet").set_index("session_id")
    cases = pd.read_parquet(review / "document-connection-conflicts.parquet")
    cases = cases[cases.success_failed_socket_conflict]
    assert len(cases) == 7
    source = fs_path(ROOT / "Datasets/extend")
    hashes, results, proposed = {}, [], []
    for case in cases.to_dict("records"):
        sid = case["session_id"]
        base = (source / sessions.loc[sid, "manifest_relative"]).parent
        paths = {name: base / name for name in ["raw/netlog.json", "raw/mihomo-trace.jsonl", "raw/tun.pcap", "raw/phys.pcap",
            "analysis/connection-index-v2.json", "analysis/flow-index.json", "analysis/summary.json"]}
        for path in paths.values():
            hashes[str(path.relative_to(source))] = file_hash(path)
        conns = read(paths["analysis/connection-index-v2.json"])["items"]
        conn = next(c for c in conns if c["connection_id"] == case["connection_id"])
        netlog = read(paths["raw/netlog.json"])
        direct = successful_socket(netlog, conn["netlog_source_id"], sessions.loc[sid, "url"])
        del netlog
        flowdoc = read(paths["analysis/flow-index.json"])
        matches = [f for f in flowdoc["items"] if flow_tuple(f.get("pre_flow") or {}) == flow_tuple(direct["pre_flow"])]
        result = {"session_id": sid, "protocol": case["protocol"], "content_id": case["content_id"],
            "old_connection_id": conn["connection_id"], "old_logical_id": conn.get("mihomo_connection_id"),
            **{k:v for k,v in direct.items() if k != "pre_flow"},
            "old_pre_hash": path_identity(conn["pre_flow"]), "actual_pre_hash": path_identity(direct["pre_flow"]),
            "tuple_changed": flow_tuple(conn["pre_flow"]) != flow_tuple(direct["pre_flow"]),
            "exact_flow_candidates": len(matches), "raw_index_modified": False}
        if len(matches) != 1:
            result["resolution"] = "hold_nonunique_flow"
            results.append(result)
            continue
        flow = matches[0]
        logical_id = flow["conn_id"]
        binding = flow.get("carrier_binding") or {}
        summary = read(paths["analysis/summary.json"])
        snapshots = summary.get("trace_snapshot", {}).get("traces", [])
        assert len(snapshots) == 1 and snapshots[0]["barrier_verified"]
        cutoff = snapshots[0]["cutoff_event_seq"]
        tail = set(snapshots[0].get("causal_tail_event_seqs", []))
        evidence = []
        for line in paths["raw/mihomo-trace.jsonl"].open(encoding="utf-8"):
            if logical_id not in line and str(conn.get("mihomo_connection_id")) not in line:
                continue
            event = json.loads(line)
            seq = event.get("event_seq")
            if not isinstance(seq, int) or not (seq <= cutoff or seq in tail):
                continue
            if event.get("conn_id") not in {logical_id, conn.get("mihomo_connection_id")} and event.get("logical_conn_id") not in {logical_id, conn.get("mihomo_connection_id")}:
                continue
            evidence.append({"event_seq": seq, "type": event.get("type"), "ts": event.get("ts"),
                "conn_id": event.get("conn_id"), "logical_conn_id": event.get("logical_conn_id"),
                "carrier_id": event.get("carrier_id"), "adapter_instance_id": event.get("adapter_instance_id"),
                "pre_path_hash": path_identity(event.get("pre_flow") or {}),
                "post_path_hash": path_identity(event.get("post_flow") or {})})
        write(out / (sid + "-trace.json"), evidence)
        new_events = [e for e in evidence if e["conn_id"] == logical_id or e["logical_conn_id"] == logical_id]
        tun = packets(paths["raw/tun.pcap"], {"old": conn["pre_flow"], "actual": direct["pre_flow"]})
        post = flow.get("post_flow") or {}
        phys = packets(paths["raw/phys.pcap"], {"actual": post}) if path_identity(post) else {}
        dial_evidence = [e for e in new_events if e["type"] == "tcp_proxy_dial" and e["post_path_hash"] == path_identity(post)]
        result.update(actual_logical_id=logical_id, actual_flow_id=flow.get("flow_id"),
            egress_outcome=flow.get("egress_outcome"), binding_mode=binding.get("mode"),
            carrier_id=binding.get("carrier_id"), pre_packets=tun["actual"]["packets"],
            pre_up_payload=tun["actual"]["up_payload"], pre_down_payload=tun["actual"]["down_payload"],
            old_pre_packets=tun["old"]["packets"], old_pre_down_payload=tun["old"]["down_payload"],
            post_packets=phys.get("actual", {}).get("packets", 0),
            post_payload=phys.get("actual", {}).get("payload_bytes", 0),
            trace_dial_events=len(dial_evidence), first_packet_to_connect_end_ms=(direct["tcp_connect_end_ns"]-tun["actual"]["first_ns"])/1e6 if tun["actual"]["first_ns"] else None,
            packet_span_covers_response=tun["actual"]["first_ns"] is not None and tun["actual"]["first_ns"] <= direct["response_first_ns"] <= tun["actual"]["last_ns"],
            matching_trace_types=json.dumps(dict(Counter(e["type"] for e in new_events))))
        passed = result["tuple_changed"] and flow.get("egress_outcome") == "proxy" and len(dial_evidence) > 0 and result["pre_up_payload"] > 0 and result["pre_down_payload"] > 0 and result["post_payload"] > 0 and result["packet_span_covers_response"]
        result["resolution"] = "independent_chain_supported" if passed else "hold_incomplete_evidence"
        proposed.append({"session_id": sid, "old_connection_id": conn["connection_id"],
            "proposed_logical_id": logical_id, "proposed_flow_id": flow.get("flow_id"),
            "carrier_id": binding.get("carrier_id"), "evidence_supported": passed,
            "applied": False, "basis": "HTTP2_SESSION_INITIALIZED -> successful TCP_CONNECT -> exact flow tuple -> bounded proxy dial -> PCAP"})
        write(out / (sid + "-packets.json"), {"tun": tun, "physical": phys})
        results.append(result)
        print(sid, result["resolution"], flush=True)
    pd.DataFrame(results).to_parquet(out / "findings.parquet", index=False)
    pd.DataFrame(proposed).to_parquet(out / "proposed-lineage-overlay.parquet", index=False)
    current = pd.read_parquet(prior / "cohort-candidates.parquet")
    current["reasons"] = current.apply(lambda r: json.dumps([v for v in json.loads(r.reasons) if not (r.session_id in set(accepted.session_id) and v == "label_evidence_requires_review")]), axis=1)
    current["metadata_candidate"] = current.reasons.eq("[]")
    current["training_eligible"] = False
    current["stage_note"] = "label decisions applied; forensic lineage overlay NOT applied; raw coverage remains pending"
    current.to_parquet(out / "cohort-after-label-acceptance.parquet", index=False)
    write(out / "source-hashes.json", hashes)
    write(out / "status.json", {"status": "forensic_complete_no_overlay_applied", "cases": len(results),
        "supported": sum(r["resolution"] == "independent_chain_supported" for r in results),
        "training_performed": False, "original_artifacts_modified": False,
        "script_hash": file_hash(Path(__file__)), "module_hash": file_hash(ROOT / "src/proxy_analysis/extend_calibration/forensic.py"),
        "artifact_hashes": {p.name:file_hash(p) for p in out.iterdir() if p.is_file()}})


if __name__ == "__main__":
    main()
