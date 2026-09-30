"""Uniform primary-document lineage diagnostic for the fixed 600 visit pool."""
from pathlib import Path
import sys
import json
import gc

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from proxy_analysis.extend_calibration.audit import fs_path, read, write, file_hash, url_key, path_identity
from proxy_analysis.extend_calibration.forensic import successful_socket, flow_tuple


def main():
    prior = ROOT / "outputs/extend-calibration-20260930/run-01"
    out = prior / "primary-lineage-01"
    if (out / "status.json").exists():
        raise RuntimeError("Output finalized; use a new output version")
    out.mkdir(exist_ok=True)
    visits = pd.read_parquet(prior / "cohort-candidates.parquet")
    pool = visits[(visits.domain != "bilibili.com") & visits.repetition.isin([1, 2, 3, 4]) & (visits.protocol != "hysteria2")]
    assert len(pool) == 600 and pool.groupby("protocol").size().eq(120).all()
    source = fs_path(ROOT / "Datasets/extend")
    rows, hashes = [], {}
    for num, visit in enumerate(pool.to_dict("records")):
        sid = visit["session_id"]
        base = (source / visit["manifest_relative"]).parent
        files = {name: base / name for name in ["analysis/summary.json", "analysis/request-index-v2.json",
            "analysis/connection-index-v2.json", "analysis/flow-index.json", "raw/netlog.json"]}
        for p in files.values():
            hashes[str(p.relative_to(source))] = file_hash(p)
        summary = read(files["analysis/summary.json"])
        nav = summary.get("navigation_outcome") or {}
        requests = read(files["analysis/request-index-v2.json"])["items"]
        conns = {c["connection_id"]:c for c in read(files["analysis/connection-index-v2.json"])["items"]}
        flows = read(files["analysis/flow-index.json"])["items"]
        allowed = {url_key(visit["url"]), url_key(nav.get("final_url") or visit["url"])}
        docs = [r for r in requests if r.get("resource_type") == "Document" and url_key(r.get("url", "")) in allowed
                and r.get("response_status") == 200 and not (r.get("failure") or {}).get("failed", False)
                and (not nav.get("main_target_id") or r.get("target_id") == nav["main_target_id"])]
        netlog = read(files["raw/netlog.json"])
        # Report every successful target document; do not pick the most favorable attempt.
        for request in docs or [{}]:
            conn = conns.get(request.get("connection_id"), {})
            row = {"session_id": sid, "protocol": visit["protocol"], "content_id": visit["content_id"],
                "repetition": visit["repetition"], "request_id": request.get("request_id"),
                "is_final_loader": request.get("request_id") == nav.get("main_loader_id"),
                "old_connection_id": request.get("connection_id"), "old_logical_id": conn.get("mihomo_connection_id"),
                "old_disposition": conn.get("post_flow_disposition"), "old_application_protocol": conn.get("application_protocol"),
                "overlay_applied": False, "pcap_validation": "not_performed_by_this_audit"}
            try:
                if not request or conn.get("netlog_source_id") is None:
                    raise ValueError("missing successful target document or NetLog source identity")
                result = successful_socket(netlog, conn["netlog_source_id"], request["url"])
                matched = [f for f in flows if flow_tuple(f.get("pre_flow") or {}) == flow_tuple(result["pre_flow"])]
                row.update(h2_source=result["h2_source"], socket_source=result["socket_source"],
                    exact_flow_candidates=len(matched),
                    old_pre_hash=path_identity(conn.get("pre_flow") or {}), actual_pre_hash=path_identity(result["pre_flow"]),
                    tuple_changed=flow_tuple(conn.get("pre_flow") or {}) != flow_tuple(result["pre_flow"]))
                if len(matched) != 1:
                    raise ValueError("successful socket has nonunique/missing flow-index tuple")
                f = matched[0]
                sem = f.get("proxy_semantics") or {}
                proto = sem.get("protocol")
                if proto == "ss":
                    proto = "shadowsocks"
                row.update(actual_logical_id=f.get("conn_id"), actual_flow_id=f.get("flow_id"),
                    actual_egress=f.get("egress_outcome"), actual_protocol=proto,
                    actual_disposition=f.get("post_flow_disposition"),
                    actual_binding_mode=(f.get("carrier_binding") or {}).get("mode"))
                if f.get("egress_outcome") != "proxy" or proto != visit["protocol"]:
                    row["status"] = "actual_route_or_protocol_requires_review"
                elif row["tuple_changed"]:
                    row["status"] = "different_successful_socket"
                else:
                    row["status"] = "consistent_direct_dependency"
            except (ValueError, KeyError, TypeError) as exc:
                row["status"] = "direct_dependency_unresolved"
                row["reason"] = str(exc)
            rows.append(row)
        del netlog
        if num % 25 == 0:
            gc.collect()
            print(f"Primary lineage {num + 1}/600", flush=True)
    frame = pd.DataFrame(rows)
    frame.to_parquet(out / "primary-document-lineage.parquet", index=False)
    write(out / "source-hashes.json", hashes)
    grouped = frame.groupby(["protocol", "status"]).agg(documents=("session_id", "size"), visits=("session_id", "nunique")).reset_index()
    grouped.to_parquet(out / "counts.parquet", index=False)
    write(out / "status.json", {"status": "read_only_lineage_audit_complete", "visits": 600,
        "document_rows": len(frame), "training_performed": False, "overlay_applied": False,
        "counts": grouped.to_dict("records"), "script_hash": file_hash(Path(__file__)),
        "hashes": {p.name:file_hash(p) for p in out.iterdir() if p.is_file()}})
    print(grouped.to_string(index=False), flush=True)


if __name__ == "__main__":
    main()
