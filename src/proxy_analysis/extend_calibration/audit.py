"""Versioned metadata qualification, with bounded shared-carrier trace evidence.

Raw captures are not modified or loaded. No model, feature or split is fitted.
Endpoints are hashed only for identity auditing and never exported in plaintext.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import platform
import shutil
import sys
from urllib.parse import urlsplit, urlunsplit, parse_qs

import pandas as pd
import yaml


SAFE_FIELDS = {
    "alpn", "cipher", "plugin", "plugin_mode", "plugin_mux", "plugin_tls",
    "smux_enabled", "smux_protocol", "transport", "tls", "reality", "vision",
    "flow", "packet_encoding", "udp", "udp_over_tcp", "udp_over_tcp_version",
    "obfs", "port_hopping", "hop_interval_seconds", "udp_mtu", "ip_version",
    "tcp_fast_open", "multipath_tcp", "dialer_proxy_enabled", "secondary_shadowsocks",
    "secondary_cipher", "authenticated_length", "global_padding",
    "idle_session_check_interval_seconds", "idle_session_timeout_seconds",
    "minimum_idle_sessions",
}


def fs_path(path: Path) -> Path:
    text = str(path.absolute())
    if os.name == "nt" and not text.startswith("\\\\?\\"):
        text = "\\\\?\\" + text
    return Path(text)


def child(base: Path, relative: str) -> Path:
    """Accept only portable relative paths, never a historic absolute path."""
    p = PurePosixPath(relative.replace("\\", "/"))
    if p.is_absolute() or ".." in p.parts or ":" in relative:
        raise ValueError("unsafe artifact/catalog path")
    return base.joinpath(*p.parts)


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(data) -> str:
    return hashlib.sha256(json.dumps(data, sort_keys=True, ensure_ascii=True).encode()).hexdigest()


def file_hash(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def write(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def url_key(url: str) -> str:
    p = urlsplit(url)
    return urlunsplit((p.scheme.lower(), p.netloc.lower(), p.path.rstrip("/") or "/", p.query, ""))


def content_key(url: str) -> str:
    p = urlsplit(url)
    if p.hostname in {"www.youtube.com", "youtube.com"} and p.path == "/watch":
        vid = parse_qs(p.query).get("v", [])
        if vid:
            return "youtube_video:" + vid[0]
    return url_key(url)


def resolve_selected(run: dict, catalog: dict) -> tuple[list[dict], list[str]]:
    issues = []
    attempts = [a for a in run.get("attempts", []) if a.get("ordinal") == run.get("selected_attempt")]
    if len(attempts) != 1:
        issues.append("selected_attempt_not_unique")
    elif set(attempts[0].get("session_ids", [])) != set(run.get("session_ids", [])):
        issues.append("selected_attempt_session_mismatch")
    entries = []
    for sid in run.get("session_ids", []):
        found = [e for e in catalog.get("entries", []) if e.get("session_id") == sid]
        if len(found) != 1:
            issues.append("selected_catalog_session_not_unique")
        else:
            entries.append(found[0])
    return entries, issues


def path_identity(flow: dict) -> str | None:
    keys = ["network", "src_ip", "src_port", "dst_ip", "dst_port"]
    if not flow or any(flow.get(k) in [None, ""] for k in keys):
        return None
    return digest([flow[k] for k in keys])


def route_evidence(requests: list[dict], connections: list[dict], target: dict, summary: dict):
    """Only successful document evidence can resolve a failed/unmatched retry.

    final_url is supplied by navigation evidence, never arbitrary same-domain fallback.
    Media rows are descriptive: resource_type alone cannot confirm primary playback.
    """
    index = {c["connection_id"]: c for c in connections}
    nav = summary.get("navigation_outcome") or {}
    allowed = {url_key(target["url"])}
    if nav.get("final_url"):
        allowed.add(url_key(nav["final_url"]))
    rows = []
    for q in requests:
        typ = q.get("resource_type", "")
        primary = typ == "Document" and url_key(q.get("url", "")) in allowed
        media = typ == "Media"
        if not primary and not media:
            continue
        c = index.get(q.get("connection_id"), {})
        status = q.get("response_status")
        success = isinstance(status, int) and 200 <= status < 300 and not (q.get("failure") or {}).get("failed", False)
        egress = c.get("egress") or {}
        rows.append({
            "kind": "primary_document" if primary else "media_resource",
            "request_id": q.get("request_occurrence_id") or q.get("request_id"),
            "connection_id": q.get("connection_id"),
            "route": egress.get("mode", "unknown"), "status": status,
            "success": success, "matched": bool(c),
            "attribution_status": (q.get("attribution") or {}).get("status"),
        })
    docs = [r for r in rows if r["kind"] == "primary_document"]
    good = {r["route"] for r in docs if r["success"]}
    if good == {"proxy"}:
        decision = "proxy_success"
    elif good == {"direct"}:
        decision = "direct_success"
    elif not good:
        decision = "unresolved_no_successful_document"
    else:
        decision = "unresolved_mixed_success_routes"
    return decision, rows


def bounded_trace(path: Path, summary: dict, selected_carriers: set[str]):
    snapshots = summary.get("trace_snapshot", {}).get("traces", [])
    if len(snapshots) != 1 or snapshots[0].get("barrier_verified") is not True:
        return [], {"status": "unverified_barrier", "sha256": None}
    snap = snapshots[0]
    cutoff = snap["cutoff_event_seq"]
    causal = set(snap.get("causal_tail_event_seqs", []))
    counts = Counter()
    evidence = []
    h = hashlib.sha256()
    with path.open("rb") as f:
        for line in f:
            h.update(line)
            counts["lines"] += 1
            if b'"carrier_id"' not in line:
                continue
            try:
                e = json.loads(line)
            except (ValueError, UnicodeDecodeError):
                counts["malformed_carrier_lines"] += 1
                continue
            seq = e.get("event_seq")
            if not isinstance(seq, int) or not (seq <= cutoff or seq in causal):
                counts["outside_barrier_carrier_lines"] += 1
                continue
            cid = e.get("carrier_id")
            if cid not in selected_carriers:
                counts["other_carrier_lines"] += 1
                continue
            counts["selected_carrier_lines"] += 1
            typ = e.get("type", "unknown")
            counts["type:" + typ] += 1
            # Compact independent lifecycle references, no endpoints/host/credentials.
            evidence.append({"carrier_id": cid, "adapter_instance_id": e.get("adapter_instance_id"),
                "generation": e.get("carrier_generation"), "event_seq": seq,
                "event_type": typ, "ts": e.get("ts"),
                "relation": e.get("carrier_relation"), "logical_conn_id": e.get("logical_conn_id"),
                "post_path_hash": path_identity(e.get("post_flow") or {})})
    return evidence, {"status": "bounded", "cutoff_event_seq": cutoff, "sha256": h.hexdigest(), **counts}


def environment(root: Path):
    import torch
    result = {"python": sys.version, "executable": sys.executable, "platform": platform.platform(),
        "torch": torch.__version__, "cuda_runtime": torch.version.cuda,
        "cuda_available": torch.cuda.is_available(), "free_bytes": shutil.disk_usage(root).free,
        "checked_at": datetime.now(timezone.utc).isoformat(), "training_performed": False}
    if result["cuda_available"]:
        a = torch.arange(64, dtype=torch.float64, device="cuda").reshape(8, 8)
        result["cuda_smoke_checksum"] = float((a @ a.T).sum().item())
        result["gpu"] = torch.cuda.get_device_name(0)
        result["gpu_memory_bytes"] = torch.cuda.get_device_properties(0).total_memory
    return result


def main(root: Path):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/extend-calibration-20260930.yaml")
    args = parser.parse_args()
    config = yaml.safe_load((root / args.config).read_text(encoding="utf-8"))
    out = root / config["output"]
    if (out / "status.json").exists():
        raise RuntimeError("Output already finalized; use a new output path/config, never overwrite")
    out.mkdir(parents=True, exist_ok=True)
    write(out / "environment.json", environment(root))
    source_files = [root / args.config, Path(__file__), Path(__file__).with_name("__init__.py"),
        root / "eval/extend_calibration/audit.py",
        root / "plan/extend-six-protocol-calibration-migration-plan-20260930.md"]
    for folder in ["src/proxy_analysis/feasible_summary_calibration", "eval/hy2_carrier_calibration"]:
        source_files.extend(sorted((root / folder).glob("*.py")))
    write(out / "source-lock.json", {str(p.relative_to(root)): file_hash(p) for p in source_files})
    data = fs_path(root / config["dataset_root"])
    rows, attempts, artifacts, entities, route_rows, labels, traces = [], [], [], [], [], [], []
    lifecycle = []
    deployments = {}
    inventory = []
    issues = []
    metadata_hashes = {}
    for pipe in sorted(data.glob("*/*/pipeline-manifest.json")):
        doc = read(pipe)
        dataset = pipe.parent.parent.name
        role = "content" if "Content-Generalization" in dataset else "detailed" if "Detailed" in dataset else "broad"
        target_index = {t["index"]: t for t in doc["targets"]}
        yaml_file = pipe.parent.parent / "target-configs" / PurePosixPath(doc["config"]["path"]).name
        actual_yaml = file_hash(yaml_file)
        inventory.append({"dataset": dataset, "role": role, "pipeline_id": doc["pipeline_id"],
            "schema": doc["schema_version"], "runs": len(doc["runs"]), "targets": len(doc["targets"]),
            "attempts": sum(len(r.get("attempts", [])) for r in doc["runs"]),
            "states": dict(Counter(r["state"] for r in doc["runs"])),
            "yaml_sha256": actual_yaml, "yaml_matches": actual_yaml == doc["config"]["sha256"],
            "schedule": doc["schedule"], "runtime_options": doc["execution"]["options"]})
        metadata_hashes[str(pipe.relative_to(data))] = file_hash(pipe)
        for n, run in enumerate(doc["runs"]):
            rdir = pipe.parent / "runs" / PurePosixPath(run["output_path"]).name
            catalog_path = rdir / ".session-catalog/catalog-v1.json"
            catalog = read(catalog_path)
            entries, selection_issues = resolve_selected(run, catalog)
            if selection_issues:
                issues.append({"run_id": run["run_id"], "issues": selection_issues})
            for a in run.get("attempts", []):
                for sid in a.get("session_ids", []):
                    attempts.append({"dataset": dataset, "run_id": run["run_id"], "session_id": sid,
                        "attempt": a["ordinal"], "state": a["state"],
                        "selected": a["ordinal"] == run.get("selected_attempt")})
            target = target_index[run["target_index"]]
            for entry in entries:
                mp = child(rdir, entry["path"])
                base = mp.parent
                manifest = read(mp)
                sid = entry["session_id"]
                summary_path = base / "analysis/summary.json"
                summary = read(summary_path) if summary_path.is_file() else {}
                generation = summary.get("analysis_generation_id")
                expected_gen = [g["generation_id"] for g in run.get("quality", {}).get("analysis_generations", []) if g["session_id"] == sid]
                generation_ok = bool(summary) and expected_gen == [generation]
                row = {"dataset": dataset, "dataset_role": role, "run_id": run["run_id"], "session_id": sid,
                    "protocol": run["expected_protocol"], "observed_protocol": run.get("observed_protocol"),
                    "repetition": run["repetition_index"], "target_index": run["target_index"],
                    "url": target["url"], "content_id": content_key(target["url"]),
                    "label": target["domain"] + "::" + target["run_label"], "domain": target["domain"],
                    "run_state": run["state"], "session_state": manifest["state"],
                    "started_at": manifest.get("started_at"), "completed_at": manifest.get("completed_at"),
                    "manifest_relative": str(mp.relative_to(data)), "has_summary": bool(summary),
                    "selection_ok": not selection_issues, "generation_ok": generation_ok,
                    "analysis_generation_id": generation,
                    "capture_state": summary.get("capture_global_quality_state", "missing"),
                    "correlation_state": run.get("quality", {}).get("correlation", {}).get("state", "missing"),
                    "application_state": run.get("quality", {}).get("application", {}).get("state", "missing"),
                    "raw_packet_validation": "pending_E07", "raw_packet_hash": "not_computed"}
                for art in manifest.get("artifacts", []):
                    ap = child(base, art["path"])
                    exists = ap.is_file()
                    actual = ap.stat().st_size if exists else None
                    recorded = art.get("size_bytes")
                    asof = art.get("size_semantics") == "as_of"
                    status = "missing" if not exists else "match" if actual == recorded else "as_of_growth" if asof and recorded is not None and actual >= recorded else "size_mismatch"
                    artifacts.append({"session_id": sid, "dataset_role": role, "path": art["path"],
                        "role": art.get("role"), "recorded_bytes": recorded, "actual_bytes": actual,
                        "size_semantics": art.get("size_semantics", "exact"), "status": status,
                        "content_hash_status": "deferred_raw" if art.get("role") in {"tun_pcap", "physical_pcap", "derived_pcap"} else "not_hashed_by_artifact_scan"})
                if not summary:
                    rows.append(row)
                    continue
                for needed in [mp, summary_path, base / "analysis/flow-index.json", base / "raw/proxy-semantics.json"]:
                    metadata_hashes[str(needed.relative_to(data))] = file_hash(needed)
                sem = read(base / "raw/proxy-semantics.json")
                start, end = sem.get("start", {}), sem.get("end", {})
                row["semantics_stable"] = start.get("behavior_fingerprint") == end.get("behavior_fingerprint")
                row["adapter_instance_id"] = start.get("adapter_instance_id")
                row["behavior_fingerprint"] = start.get("behavior_fingerprint")
                evidence = start.get("evidence", {})
                safe = {layer: {k: v for k, v in evidence.get(layer, {}).items() if k in SAFE_FIELDS}
                    for layer in ["configured", "effective"]}
                dep_key = digest([row["protocol"], safe, start.get("build", {}).get("executable_sha256")])
                if dep_key not in deployments:
                    deployments[dep_key] = {"deployment_id": dep_key, "protocol": row["protocol"],
                        "evidence": safe, "coverage": start.get("coverage"), "build": start.get("build"),
                        "sessions": 0, "datasets": []}
                deployments[dep_key]["sessions"] += 1
                if dataset not in deployments[dep_key]["datasets"]:
                    deployments[dep_key]["datasets"].append(dataset)
                row["deployment_id"] = dep_key
                cb = summary.get("carrier_bindings", {})
                row.update({"shared_carriers": cb.get("shared_carrier_count", 0),
                    "physical_carriers": cb.get("physical_carriers_observed", 0),
                    "missing_bindings": cb.get("missing_binding", 0)})
                flow_doc = read(base / "analysis/flow-index.json")
                row["flow_index_generation_ok"] = flow_doc.get("analysis_generation_id") == generation
                flows = flow_doc.get("items", [])
                row["flow_count"] = len(flows)
                proxy_count = 0
                selected_cids = set()
                for f in flows:
                    binding = f.get("carrier_binding") or {}
                    semantic = f.get("proxy_semantics") or {}
                    cid = binding.get("carrier_id") or f.get("outer_conn_id")
                    adapter = semantic.get("adapter_instance_id") or row["adapter_instance_id"]
                    mode = binding.get("mode", "unknown")
                    proxy = f.get("egress_outcome") == "proxy"
                    proxy_count += int(proxy)
                    if cid and mode == "shared":
                        selected_cids.add(cid)
                    paths = binding.get("physical_paths") or [f.get("post_flow") or {}]
                    keys = sorted({p for q in paths if (p := path_identity(q)) is not None})
                    entities.append({"dataset": dataset, "dataset_role": role, "session_id": sid,
                        "protocol": row["protocol"], "content_id": row["content_id"],
                        "flow_id": f.get("flow_id"), "logical_conn_id": f.get("conn_id"),
                        "carrier_id": cid, "adapter_instance_id": adapter, "binding_mode": mode,
                        "carrier_generation": binding.get("generation"), "relation": binding.get("relation"),
                        "entity_key": digest([row["protocol"], adapter, cid]) if cid else None,
                        "path_hashes": json.dumps(keys), "pre_path_hash": path_identity(f.get("pre_flow") or {}),
                        "pre_network": (f.get("pre_flow") or {}).get("network"),
                        "post_network": (f.get("post_flow") or {}).get("network"),
                        "post_disposition": f.get("post_flow_disposition"),
                        "egress_outcome": f.get("egress_outcome"), "proxy": proxy,
                        "match_status": (f.get("match") or {}).get("status"),
                        "attribution_scope": f.get("attribution_scope")})
                row["proxy_flow_count"] = proxy_count
                if role == "content":
                    requests_doc = read(base / "analysis/request-index-v2.json")
                    conns_doc = read(base / "analysis/connection-index-v2.json")
                    row["request_generation_ok"] = requests_doc.get("analysis_generation_id") == generation and conns_doc.get("analysis_generation_id") == generation
                    decision, detail = route_evidence(requests_doc["items"], conns_doc["items"], target, summary)
                    route_rows.extend({"session_id": sid, **v} for v in detail)
                    activity = summary.get("activity_outcome") or {}
                    video = target["run_label"] == "video_playback"
                    label_status = "playback_confirmed" if video and activity.get("primary_content_observed") is True else "playback_unverified" if video else "navigation_confirmed" if (summary.get("navigation_outcome") or {}).get("state") == "passed" else "navigation_review"
                    lr = {"session_id": sid, "protocol": row["protocol"], "content_id": row["content_id"],
                        "label": row["label"], "repetition": row["repetition"],
                        "route_decision": decision, "label_status": label_status,
                        "activity_kind": activity.get("kind"), "activity_state": activity.get("state"),
                        "primary_seconds": activity.get("primary_content_seconds"),
                        "primary_goal_met": activity.get("primary_goal_met"),
                        "media_requests": sum(v["kind"] == "media_resource" for v in detail),
                        "media_proxy": sum(v["kind"] == "media_resource" and v["route"] == "proxy" for v in detail),
                        "media_direct": sum(v["kind"] == "media_resource" and v["route"] == "direct" for v in detail)}
                    labels.append(lr)
                    row.update(route_decision=decision, label_status=label_status)
                    if selected_cids:
                        events, stat = bounded_trace(base / "raw/mihomo-trace.jsonl", summary, selected_cids)
                        lifecycle.extend({"session_id": sid, "protocol": row["protocol"], **e} for e in events)
                        traces.append({"session_id": sid, **stat})
                rows.append(row)
            if n % 100 == 0:
                print(f"{role}: {n + 1}/{len(doc['runs'])} runs audited", flush=True)
    sessions = pd.DataFrame(rows)
    entity = pd.DataFrame(entities)
    overlap = []
    for key, group in entity.dropna(subset=["entity_key"]).groupby("entity_key"):
        distinct = group.drop_duplicates("session_id")
        if len(distinct) < 2:
            continue
        overlap.append({"entity_key": key, "protocol": group.iloc[0]["protocol"],
            "carrier_id": group.iloc[0]["carrier_id"], "adapter_instance_id": group.iloc[0]["adapter_instance_id"],
            "sessions": len(distinct), "contents": distinct.content_id.nunique(),
            "datasets": sorted(distinct.dataset.unique()), "binding_modes": sorted(group.binding_mode.unique()),
            "session_ids": sorted(distinct.session_id), "content_ids": sorted(distinct.content_id.unique())})
    reused = {s for g in overlap for s in g["session_ids"] if g["contents"] > 1}
    art = pd.DataFrame(artifacts)
    bad_files = set(art[art.status.isin(["missing", "size_mismatch"])].session_id)
    candidates = []
    for r in sessions[sessions.dataset_role == "content"].to_dict("records"):
        reasons = []
        if r["domain"] in config["excluded_main_domains"]:
            reasons.append("outside_main_six_businesses")
        if r["repetition"] not in config["proposed_repetitions"]:
            reasons.append("outside_proposed_repetitions")
        for key in ["selection_ok", "generation_ok", "has_summary", "flow_index_generation_ok", "request_generation_ok", "semantics_stable"]:
            if r.get(key) is not True:
                reasons.append(key + "_not_passed")
        if r["session_id"] in bad_files:
            reasons.append("artifact_discrepancy")
        if r.get("route_decision") != "proxy_success":
            reasons.append("primary_route_unresolved_or_direct")
        if r.get("label_status") not in {"playback_confirmed", "navigation_confirmed"}:
            reasons.append("label_evidence_requires_review")
        if r.get("capture_state") != "passed" or r.get("correlation_state") != "passed":
            reasons.append("capture_or_correlation_requires_review")
        if r["session_id"] in reused:
            reasons.append("carrier_cross_content")
        reasons = sorted(set(reasons))
        candidates.append({**r, "metadata_candidate": not reasons, "reasons": json.dumps(reasons),
            "W_status": "pending_raw_validation" if not reasons else "hold",
            "T_status": "pending_exclusive_tcp_validation" if not reasons and r["protocol"] in {"shadowsocks", "vless", "vmess", "trojan"} else "hold_or_not_applicable",
            "training_eligible": False})
    frames = {"sessions": sessions, "attempts": pd.DataFrame(attempts), "artifact-audit": art,
        "entity-graph": entity, "label-route-ledger": pd.DataFrame(labels),
        "request-route-evidence": pd.DataFrame(route_rows), "bounded-trace-audit": pd.DataFrame(traces),
        "carrier-lifecycle-evidence": pd.DataFrame(lifecycle), "cohort-candidates": pd.DataFrame(candidates)}
    for name, frame in frames.items():
        frame.to_parquet(out / (name + ".parquet"), index=False)
    write(out / "inventory.json", inventory)
    write(out / "selection-issues.json", issues)
    write(out / "metadata-hashes.json", metadata_hashes)
    write(out / "deployment-registry.json", list(deployments.values()))
    write(out / "carrier-overlap.json", overlap)
    write(out / "stage-boundaries.json", {"raw_pcap_read": False, "raw_hash_pending": True,
        "lifecycle_scope": "full flow-index all selected sessions; bounded carrier trace content shared sessions only",
        "packet_overlap_and_tcp_lifecycle_pending": True, "training_performed": False,
        "strict_train_test_isolation_certified": False, "hy2_exception_approved": False})
    report(root / config["report"], frames, inventory, overlap, out)
    write(out / "status.json", {"status": "G1_requires_confirmation", "training_performed": False,
        "selected_sessions": len(sessions), "attempt_rows": len(attempts),
        "selection_issues": len(issues), "output_hashes": {p.name: file_hash(p) for p in sorted(out.iterdir()) if p.is_file()}})
    print(f"Qualification saved to {out}; no training performed", flush=True)


def report(path: Path, frames: dict, inventory: list, overlap: list, out: Path):
    def table(frame):
        # Avoid an optional tabulate dependency.
        columns = list(frame.columns)
        lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
        for values in frame.itertuples(index=False, name=None):
            lines.append("| " + " | ".join(str(v).replace("|", "/").replace("\n", " ") for v in values) + " |")
        return "\n".join(lines)
    s = frames["sessions"]
    c = frames["cohort-candidates"]
    l = frames["label-route-ledger"]
    a = frames["artifact-audit"]
    main = c[(c.domain != "bilibili.com") & c.repetition.isin([1, 2, 3, 4])]
    counts = main.groupby("protocol").agg(proposed=("session_id", "size"), metadata_candidate=("metadata_candidate", "sum")).reset_index()
    routes = l.groupby(["protocol", "route_decision"]).size().reset_index(name="visits")
    reasons = Counter(reason for v in main.reasons for reason in json.loads(v))
    exception_cols = ["protocol", "repetition", "content_id", "session_id", "reasons"]
    exceptions = main[(~main.metadata_candidate) & (main.protocol != "hysteria2")][exception_cols]
    content_overlap = [g for g in overlap if any("Content-Generalization" in d for d in g["datasets"])]
    text = "\n\n".join([
        "# 六协议迁移 G1：元数据资格与关联审核\n\n日期：2026-09-30。状态：需要队列决策；没有拟合或训练模型。",
        "## 1. 执行范围\n\n已实现 E00–E06 的元数据路径、选中 attempt、文件大小、配置、业务路由与实体图审计。共享连接的 Content trace 按 verified barrier 和授权 causal tail 读取。原始包哈希、实际包覆盖、跨文件包重叠及排他 TCP 生命周期仍待 E07/E08，不能据本报告宣称训练资格全部通过。",
        "## 2. 数据库存\n\n" + table(pd.DataFrame([{k: d[k] for k in ["role", "runs", "attempts", "targets", "yaml_matches"]} for d in inventory])),
        "## 3. 四重复六业务候选\n\nmetadata_candidate 只表示本阶段未触发保留项，不是最终可训练。全部 training_eligible=false。\n\n" + table(counts),
        "候选范围内保留原因（可重叠）：\n\n" + table(pd.DataFrame(list(reasons.items()), columns=["reason", "visits"])),
        "## 4. 主文档路由\n\n成功主文档仅接受目标 URL 或导航证据的 final_url；成功关联可以解释同次失败/取消重试，不能借同域任意资源替代。下表含全部五重复和七业务。\n\n" + table(routes),
        "Bilibili 仍单列。Media 类型请求仅作为资源路由证据，不能等同于正式视频播放或覆盖所有 XHR/MSE 媒体请求。\n\n" + table(l[l.label.str.startswith("bilibili.com")].groupby("protocol").agg(visits=("session_id", "size"), media_requests=("media_requests", "sum"), media_proxy=("media_proxy", "sum"), media_direct=("media_direct", "sum")).reset_index()),
        "## 5. 非 Hy2 主候选待定访问\n\n不得替换 prior attempt，不补零；逐条原因如下。\n\n" + (table(exceptions) if len(exceptions) else "无元数据保留项；仍须原始包资格验证。"),
        "## 6. 载体与内容独立性\n\n以下是登记实体跨 Session 引用，非自动证明所有引用时间内均有包。严格分组不能忽略这些边。\n\n" + table(pd.DataFrame([{k:g[k] for k in ["protocol", "sessions", "contents", "binding_modes"]} for g in content_overlap])),
        "Hy2 默认不进入 carrier-disjoint 主分类。若接受同一个持久 carrier 内的非重叠窗口研究，须明确批准且单列结论；不能声称无同连接跨集合。AnyTLS 未发现相同登记 ID 跨内容也不等于完成原包独立性审核。",
        "## 7. 文件与证据边界\n\n" + table(a.groupby("status").size().reset_index(name="artifacts")),
        "as_of_growth 是显式增长语义，不与固定尺寸不一致混为一谈。原始 PCAP 尚未全量哈希；所有解析得到的元数据有源文件指纹，bounded trace 另有完整文件 SHA256。配置只输出白名单字段，路径身份只保存哈希；这些身份字段不允许进入后续模型。",
        "## 8. 下一步决策\n\n1. 确认六业务、重复 1–4 的等预算设计，第五重复保留但暂不训练。\n2. 对第 5 节逐项给定接受或继续审核方向，不能因删除而不对称改变 C/U 预算。\n3. 确认 Hy2 只保留测量，或单独批准同持久 carrier 的受限窗口分支。\n\n通过这些决策后再做 E07–E13 原始事件、特征与权限门；本报告不是启动正式训练的许可。",
        "## 9. 复现与产物\n\n运行：`D:/Tools/Anaconda/envs/Pytorch312/python.exe eval/extend_calibration/audit.py`。已完成输出目录不会被覆盖；复跑应使用新配置的输出目录。\n\n产物位于 `" + str(out) + "`，包括 inventory、sessions、attempts、artifact-audit、deployment-registry、label-route-ledger、request-route-evidence、entity-graph、carrier-overlap、bounded-trace-audit、carrier-lifecycle-evidence、cohort-candidates、environment、source-lock、metadata-hashes 与 stage-boundaries。",
    ])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text + "\n", encoding="utf-8")
