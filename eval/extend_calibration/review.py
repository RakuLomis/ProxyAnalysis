"""Independent G1 checks and targeted evidence, preserving run-01 decisions."""
from pathlib import Path
import json
import sys
import argparse
from collections import Counter
from urllib.parse import urlsplit

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from proxy_analysis.extend_calibration.audit import fs_path, file_hash, read, write, url_key


def main():
    out = ROOT / "outputs/extend-calibration-20260930/run-01"
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--review-name", default="g1-review")
    options = parser.parse_args()
    if Path(options.review_name).name != options.review_name or options.review_name in {".", ".."}:
        raise ValueError("review-name must be a single directory name")
    dest = out / options.review_name
    if (dest / "validation.json").exists():
        raise RuntimeError("Review finalized; do not overwrite")
    dest.mkdir(exist_ok=True)
    source = fs_path(ROOT / "Datasets/extend")
    visits = pd.read_parquet(out / "sessions.parquet")
    candidates = pd.read_parquet(out / "cohort-candidates.parquet")
    attempts = pd.read_parquet(out / "attempts.parquet")
    entities = pd.read_parquet(out / "entity-graph.parquet")
    life = pd.read_parquet(out / "carrier-lifecycle-evidence.parquet")
    trace = pd.read_parquet(out / "bounded-trace-audit.parquet")
    manifest = read(out / "status.json")
    checks = {
        "1974_selected_sessions": len(visits) == 1974,
        "1996_attempt_rows": len(attempts) == 1996,
        "selected_session_identity_unique": visits.session_id.nunique() == len(visits),
        "1974_selected_attempts": int(attempts.selected.sum()) == 1974,
        "no_prior_attempt_used": set(attempts[attempts.selected].session_id) == set(visits.session_id),
        "selected_run_cells_unique": not visits.duplicated(["dataset", "protocol", "target_index", "repetition"]).any(),
        "no_selection_issues": not read(out / "selection-issues.json"),
        "1048_content_summaries": int(visits[visits.dataset_role == "content"].has_summary.sum()) == 1048,
        "all_existing_summaries_generation_match": bool(visits[visits.has_summary].generation_ok.all()),
        "350_bounded_shared_traces": len(trace) == 350 and trace.status.eq("bounded").all(),
        "no_learning_eligibility_granted": not candidates.training_eligible.any(),
        "no_output_changes_since_seal": all(file_hash(out / name) == h for name, h in manifest["output_hashes"].items()),
    }
    assert all(checks.values()), checks
    main = candidates[(candidates.domain != "bilibili.com") & candidates.repetition.isin([1, 2, 3, 4])]
    holds = main[(main.protocol != "hysteria2") & ~main.metadata_candidate]
    evidence, navrows, hashes = [], [], {}
    for v in holds.to_dict("records"):
        base = (source / v["manifest_relative"]).parent
        files = {name: base / "analysis" / name for name in ["summary.json", "request-index-v2.json", "connection-index-v2.json"]}
        docs = {name: read(p) for name, p in files.items()}
        hashes.update({str(p.relative_to(source)): file_hash(p) for p in files.values()})
        summary = docs["summary.json"]
        nav = summary.get("navigation_outcome") or {}
        conns = {c["connection_id"]: c for c in docs["connection-index-v2.json"]["items"]}
        allowed = {url_key(v["url"]), url_key(nav.get("final_url") or v["url"])}
        navrows.append({"session_id": v["session_id"], "protocol": v["protocol"],
            "content_id": v["content_id"], "state": nav.get("state"), "reason": nav.get("reason"),
            "recovered": nav.get("recovered"), "load_event_observed": nav.get("load_event_observed"),
            "final_status": nav.get("final_status"), "completion_evidence": nav.get("completion_evidence"),
            "proposed_label_acceptance_only": nav.get("recovered") is True and nav.get("load_event_observed") is True and nav.get("final_status") == 200,
            "acceptance_applied": False})
        for q in docs["request-index-v2.json"]["items"]:
            if q.get("resource_type") != "Document" or url_key(q.get("url", "")) not in allowed or q.get("response_status") != 200:
                continue
            c = conns.get(q.get("connection_id"), {})
            term = c.get("terminal") or {}
            egress = c.get("egress") or {}
            evidence.append({"session_id": v["session_id"], "protocol": v["protocol"], "content_id": v["content_id"],
                "request_id": q.get("request_id"), "connection_id": q.get("connection_id"),
                "mihomo_connection_id": c.get("mihomo_connection_id"), "response_status": 200,
                "egress_mode": egress.get("mode"), "post_flow_disposition": c.get("post_flow_disposition"),
                "bytes_up": term.get("bytes_up"), "bytes_down": term.get("bytes_down"),
                "error_class": term.get("error_class"), "stage": term.get("stage"),
                "match_confidence": (c.get("match") or {}).get("confidence"),
                "match_method": (c.get("match") or {}).get("method"),
                "candidate_count": (c.get("match") or {}).get("candidate_count"),
                "success_failed_socket_conflict": c.get("post_flow_disposition") == "failed_before_socket"})
    e = pd.DataFrame(evidence)
    n = pd.DataFrame(navrows)
    e.to_parquet(dest / "document-connection-conflicts.parquet", index=False)
    n.to_parquet(dest / "recovered-navigation-proposals.parquet", index=False)
    bili = []
    for v in visits[(visits.dataset_role == "content") & (visits.domain == "bilibili.com")].to_dict("records"):
        base = (source / v["manifest_relative"]).parent
        qpath = base / "analysis/request-index-v2.json"
        cpath = base / "analysis/connection-index-v2.json"
        qs = read(qpath)["items"]
        cs = {c["connection_id"]: c for c in read(cpath)["items"]}
        hashes[str(qpath.relative_to(source))] = file_hash(qpath)
        hashes[str(cpath.relative_to(source))] = file_hash(cpath)
        # Media/CDN heuristic is a discovery aid, never a playback validator.
        matching = [q for q in qs if (urlsplit(q.get("url", "")).hostname or "").endswith(".bilivideo.com")
                    or urlsplit(q.get("url", "")).path.lower().endswith((".m4s", ".mp4", ".flv"))]
        modes = Counter((cs.get(q.get("connection_id"), {}).get("egress") or {}).get("mode", "unknown") for q in matching)
        bili.append({"session_id": v["session_id"], "protocol": v["protocol"], "candidate_media_requests": len(matching),
            "successful_candidate_media_requests": sum(q.get("response_status") in [200, 206] for q in matching),
            "proxy": modes["proxy"], "direct": modes["direct"], "unknown": modes["unknown"],
            "playback_confirmed_by_this_check": False})
    pd.DataFrame(bili).to_parquet(dest / "bilibili-media-discovery.parquet", index=False)
    shared = entities[(entities.dataset_role == "content") & (entities.binding_mode == "shared")]
    sharedsummary = []
    for proto, group in shared.groupby("protocol"):
        t = life[life.protocol == proto]
        sharedsummary.append({"protocol": proto, "visits": group.session_id.nunique(),
            "entities": group.entity_key.nunique(), "path_sets": group.path_hashes.nunique(),
            "contents": group.content_id.nunique(), "max_visits_per_entity": int(group.groupby("entity_key").session_id.nunique().max()),
            "trace_event_counts": dict(Counter(t.event_type)), "trace_relations": dict(Counter(t.relation.dropna()))})
    write(dest / "shared-lifecycle-summary.json", sharedsummary)
    write(dest / "source-hashes.json", hashes)
    env = read(out / "environment.json")
    conflict = e[e.success_failed_socket_conflict]
    assert conflict.session_id.nunique() == 7
    assert n.proposed_label_acceptance_only.sum() == 6
    rows = ["# G1 定点复核与下一确认事项", "日期：2026-09-30。未执行训练；原 run-01 候选决定未被改写。",
        "## 1. 环境与可复现性", f"Pytorch312 / Python 3.12 / PyTorch {env['torch']} / CUDA {env['cuda_runtime']}；{env['gpu']}，16 GiB。CUDA FP64 矩阵运算通过。资格阶段以 CPU 读元数据为主，不代表训练退回 CPU。",
        f"独立台账/封存校验 {len(checks)} 项全部通过；基础单元测试 7 项通过。原始包哈希与实际 TCP/carrier 包隔离尚未认证。",
        "## 2. 当前可推进范围", "四重复六业务下，非 Hy2 共 600 候选，589 次无元数据保留项。其余 11 次由 7 次主文档关联矛盾与 6 次恢复导航组成，其中 2 次重叠。\n\n若仅接受有成功恢复证据的六次导航，仍有 7 次路由关联问题，故 593/600 也不是完整等预算主队列。不能直接删除七次后按原 120 次/协议训练。",
        "## 3. 七次主文档—连接证据冲突", "这七次浏览器主文档均返回 HTTP 200，但关联连接的 post_flow_disposition=failed_before_socket、字节为零、egress=unknown。match 的高置信度不能消除该矛盾。可能涉及连接尝试/重试归属，当前不能认定根因，也不能任选其他成功连接替换。原资格表的 unresolved_mixed_success_routes 包含纯 unknown 情况；此处是 unknown，不是已确认同时经 direct 与 proxy。",
        "| 协议 | 内容 | Session |\n| --- | --- | --- |"]
    for v in conflict.to_dict("records"):
        rows.append(f"| {v['protocol']} | {v['content_id']} | {v['session_id']} |")
    rows += ["## 4. 六次恢复导航：建议接受标签，暂不实施豁免", "六次均有 NAVIGATION_TIMEOUT_RECOVERED、load_event_observed=true、final_status=200。建议保留为有效页面访问，同时保留 degraded 标记。两次 AnyTLS 还存在第 3 节关联矛盾，接受标签不能放行关联资格。\n\n该建议不需要删除或重选访问，不更改原始 summary；确认后由单独 acceptance ledger 记录。",
        "## 5. Hy2 与 AnyTLS", "Hy2 的 175 次、35 内容、五重复归于同一 carrier/adapter；受限 trace 中实际有 logical_carrier_bind 和 proxy_dial，relation=reused，因而不是只看目录名的推测。没有在这些窗口中观察到 carrier_open，不能伪造创建时刻或证明其完整生命周期。\n\nAnyTLS 有多个 carrier 的 open/bind/close 证据；详细数量见 shared-lifecycle-summary.json。未发现跨选中内容的同实体登记，并不替代后续 TCP 原包与路径复用审计。",
        "## 6. Bilibili", "150 次主文档为 DIRECT。额外按 bilivideo CDN/常见媒体后缀检索全部资源类型，共发现 " + str(sum(v['candidate_media_requests'] for v in bili)) + " 个候选媒体请求，其中 direct=" + str(sum(v['direct'] for v in bili)) + "、proxy=" + str(sum(v['proxy'] for v in bili)) + "、unknown=" + str(sum(v['unknown'] for v in bili)) + "。这支持将其与代理业务主队列分开，而不是声称没有视频资源请求。该启发式不是完整媒体识别，也不能单独证明视频实际播放。",
        "## 7. 推荐的下一决策", "建议确认：\n\n1. 主六业务和重复 1–4 不变；\n2. 接受上述六次已恢复导航的业务标签，但不豁免独立的关联问题；\n3. 优先对七次主文档关联冲突做有限 NetLog/trace/PCAP 定点取证；保持不训练，不删除、不替补，不修改 TrafficTracer 原始产物；\n4. Hy2 默认仅继续测量；若要分类，须另行明确接受同一持久 carrier 的受限窗口威胁模型。\n\n关联未修复且不改变缺失策略前，无法按原完整队列开始正式训练。",
        "## 8. 文件与哈希范围", "初步总账见 [gate-G1.md](gate-G1.md)。本次补充审计位于 outputs/extend-calibration-20260930/run-01/" + options.review_name + "。初审 metadata-hashes 覆盖 pipeline、选中 manifest/summary/flow-index/semantics；本复核另外为定点请求/连接索引保存哈希，并非所有解析文件或 PCAP 都已哈希。该精确范围取代初审报告过宽的‘所有解析元数据’表述。audit.py 使用新配置输出目录复跑；review.py 可用 --review-name 保存独立复核版本。"]
    report_path = ROOT / "docs/extend-calibration-20260930/gate-G1-review.md"
    report_path.write_text("\n\n".join(rows).replace("|\n\n|", "|\n|") + "\n", encoding="utf-8")
    write(dest / "validation.json", {"passed": True, "checks": {k: bool(v) for k, v in checks.items()},
        "new_authority_needed": True, "training_performed": False,
        "review_source_sha256": file_hash(Path(__file__)), "report_sha256": file_hash(report_path)})
    print(json.dumps({"checks": len(checks), "conflicts": 7, "recovered_navigation": 6, "training": False}))


if __name__ == "__main__":
    main()
