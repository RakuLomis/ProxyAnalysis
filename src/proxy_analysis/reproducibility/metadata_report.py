"""Build reviewable quality, route and implementation-gate evidence."""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
from urllib.parse import urldefrag
from datetime import date

import pyarrow.parquet as pq

from .preflight import write_json, write_table
from .registry import read_json


def document_route(requests: list[dict], connections: list[dict], navigation: dict) -> dict:
    """Use main target and final URL together; never guess from same-site resources."""
    main_target = navigation.get("main_target_id")
    final_url = navigation.get("final_url")
    if not main_target or not final_url:
        return {"main_document_route": "unavailable", "document_occurrences": 0}
    candidates = [r for r in requests if r.get("resource_type") == "Document"
                  and r.get("target_id") == main_target
                  and urldefrag(r.get("url", ""))[0] == urldefrag(final_url)[0]]
    index = {c["connection_id"]: c for c in connections}
    routes = {index.get(r.get("connection_id"), {}).get("egress", {}).get("outcome", "unavailable")
              for r in candidates}
    route = next(iter(routes)) if len(routes) == 1 else "ambiguous" if routes else "unavailable"
    return {"main_document_route": route, "document_occurrences": len(candidates)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output_root", type=Path)
    parser.add_argument('--legacy-report', action='store_true', help='render historical narrative only for legacy reproduction')
    args = parser.parse_args()
    root = args.output_root
    registry = pq.read_table(root / "run_registry.parquet").to_pylist()
    rows = [r for r in registry if r["is_final"]]
    eligibility = {r["session_id"]: r for r in pq.read_table(root / "cohort_eligibility.parquet").to_pylist()}
    routes = []
    for row in rows:
        path = Path(row["session_path"])
        summary = read_json(path / "analysis/summary.json")
        requests = read_json(path / "analysis/request-index-v2.json")["items"]
        connections = read_json(path / "analysis/connection-index-v2.json")["items"]
        route = document_route(requests, connections, summary.get("navigation_outcome", {}))
        connection_map = {c["connection_id"]: c for c in connections}
        request_routes = Counter(connection_map.get(r.get("connection_id"), {}).get(
            "egress", {}).get("outcome", "unavailable") for r in requests)
        routes.append({"session_id": row["session_id"], "protocol": row["protocol"],
                       "target_domain": row["target_domain"], "repetition": row["repetition"],
                       'target_index': row['target_index'], 'target_url': row['target_url'],
                       'activity_id': row['activity_id'],
                       "traffictracer_commit": row["traffictracer_commit"], **route,
                       "request_count": len(requests),
                       "proxy_request_count": request_routes["proxy"],
                       "direct_request_count": request_routes["direct"],
                       "unavailable_request_count": request_routes["unavailable"],
                       "page_context_candidate": eligibility[row["session_id"]]["page_context_candidate"],
                       "main_document_proxy_candidate": route["main_document_route"] == "proxy"
                       and eligibility[row["session_id"]]["page_context_candidate"]})
    write_table(root / "routing_eligibility.parquet", routes)
    versions = Counter(r["traffictracer_commit"] for r in rows)
    write_json(root / "version-strata.json", {
        "manifest_recorded_versions": dict(versions),
        "capture_vs_reanalysis_version_provenance": "unresolved",
        "by_repetition": {str(rep): dict(Counter(r["traffictracer_commit"] for r in rows
                            if r["repetition"] == rep)) for rep in sorted({r['repetition'] for r in rows})},
    })
    summary = read_json(root / "preflight-summary.json")
    lifecycle = read_json(root / "carrier-lifecycle-summary.json")
    if not args.legacy_report:
        lines = ['# 数据门禁与路由报告', '', f'日期：{date.today().isoformat()}。', '',
                 f'登记attempt {len(registry)}；选定会话 {len(rows)}。历史尝试不增加独立重复。',
                 f"独立预检：{json.dumps(summary, ensure_ascii=False)}", '',
                 f"Carrier门禁：{json.dumps(lifecycle, ensure_ascii=False)}", '',
                 f"Manifest记录版本：{json.dumps(dict(versions), ensure_ascii=False)}", '',
                 '| 目标序号 | domain | 部署 | 轮次 | 页面候选 | 主文档路由 |', '|---|---|---|---:|---|---|']
        lines += [f"| {r['target_index']} | {r['target_domain']} | {r['protocol']} | {r['repetition']} | {r['page_context_candidate']} | {r['main_document_route']} |" for r in routes]
        lines += ['', '同domain不同目标不合并。页面候选包含质量/路由门槛，不等同于严格完整carrier系统范围通过。',
                  '同记录版本下，去首轮只作为轮次敏感性，不称版本控制。Hy2默认仍是carrier-context。']
        (root/'implementation-gate-report.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
        print(f'Wrote {len(routes)} route records and current metadata report')
        return
    lines = ["# 重复性研究：实施进度与首个关键节点", "", "日期：2026-09-07。", "",
             "## 已完成", "",
             "- P00：Pytorch312 环境记录；未安装或升级依赖。",
             "- P01–P03：新旧布局兼容，275 attempt / 270 final 登记；历史重试不增加重复数。",
             "- P04：540 个 raw PCAPNG 全量块级读取，逐文件 SHA-256 基线；必要文件及声明大小检查。",
             "- P05：页面候选、主文档路由和请求路由表；主文档按 main_target_id + final_url 匹配。",
             "- P06–P07：全局 carrier 成员与包可观测性核查，以及全部275 attempt的创建记录追溯；严格门禁未通过。",
             "- P08：新增 runs 归一化字段，保留旧 switch 语义；pipeline implementation version 从2变为3。",
             "- P09及以后：主统计范围待关键节点确定；尚未生成新数据的正式MAD/ICC/S结论。", "",
             "## 原始包验证", "",
             f"读取 {summary['packet_count']:,} 条包记录，块级解析错误 {summary['pcap_parse_errors']}，"
             f"captured_len < original_len 的记录 {summary['snaplen_truncated_packets']}。",
             f"捕获顺序中出现 {summary['timestamp_regressions']:,} 次相邻时间戳回退；后续IAT/FR必须延续"
             "(timestamp_ns, packet_ordinal)稳定排序，不能将这些回退直接认定为网络乱序或负IAT。",
             "PCAP文件魔数和块完整性不证明没有内核丢包；未把缺失的drop统计当作0。",
             "222个会话的mihomo-trace大于manifest声明，现有规则记为late trace增长警告；生命周期核查按verified barrier和causal tail筛选。",
             "SHA-256作为本次源文件基线保存；原manifest未统一提供可比较的密码学摘要，不宣称校验了不存在的原始hash。", "",
             "## Hy2关键发现", "",
             f"审计90个Hy2 session-carrier，其中{lifecycle['all_indexed_members_observed']}个可在tun找到全部索引成员；"
             "Wikipedia第1轮、Apple第3轮各缺1个成员的pre包。没有观察到包也可能是该成员在抓包窗口内无流量，不能直接推断为丢包。",
             "90个carrier均未在本会话找到carrier_open；追溯全部275个attempt也未找到这些carrier的创建事件。"
             "因此目前缺少抓包开始时完整active-member集合的证据。即使所有已索引成员都有包，也无法证明没有抓包前已存在的成员或未被记录的输入。",
             "另有8个carrier缺成员connect记录、15个carrier的有界trace缺部分close记录。关闭缺失可能表示仍活跃，不能自动判定捕获损坏。",
             "严格完整输入→完整carrier transformation门禁目前0/90通过。这不否定数据价值：已观测inner集合→carrier的上下文变化仍可描述，但不能写成纯页面或完整系统开销。", "",
             "## 记录版本分层", "",
             *[f"- `{version}`：{count}个最终会话。" for version, count in versions.items()], "",
             "前35个run记录旧commit，run36（weather.com Hy2第1轮）开始记录新commit；第2–5轮均记录新commit。"
             "这些是manifest中的组件版本。目前尚未证实它们对应采集二进制变化还是后续分析/元数据更新，不能直接断言采集中途升级。"
             "未核清来源前建议同时保留五轮结果与第2–5轮同记录版本敏感性，不把版本标签差异当成协议效应。", "",
             "## 样本与路由", "",
             "下表是application/抓包/关联通过且存在页面代理连接的候选数，不代表严格carrier系统范围已通过。", "",
             "| 域名 | VLESS | SS | Hy2 |", "|---|---:|---:|---:|"]
    for domain in dict.fromkeys(r["target_domain"] for r in rows):
        counts = [sum(r["target_domain"] == domain and r["protocol"] == p and r["page_context_candidate"]
                      for r in routes) for p in ("VLESS", "SHADOWSOCKS", "HYSTERIA2")]
        lines.append(f"| {domain} | {' | '.join(map(str, counts))} |")
    lines += ["", f"任意页面代理连接候选 {sum(r['page_context_candidate'] for r in routes)} 个；"
              f"同时满足最终主文档走代理的候选 {sum(r['main_document_proxy_candidate'] for r in routes)} 个。",
              "主文档走代理仍不意味着所有子资源走代理，分流结构保留在routing_eligibility中。", "",
              "## 建议的下一步", "",
              "建议继续现有数据：SS/VLESS作为exclusive配对主分析，Hy2作为明确标记的carrier-context描述；"
              "五轮与第2–5轮分层对照，并在解释版本影响前核实版本记录来源。",
              "若研究目标必须是三协议同口径的纯页面/完整系统变换，应先补采或补充carrier创建前后的active-member快照、生命周期和隔离背景证据。",
              "这是方案预设的P06–P09关键节点，涉及主研究结论范围；未默认把上下文描述升级为严格变换证据。", "",
              "## 运行方式", "", "```powershell", "$env:PYTHONPATH='src'",
              "& D:/Tools/Anaconda/envs/Pytorch312/python.exe -m proxy_analysis.reproducibility.preflight Datasets/TrafficTracer-Detailed-5Reps outputs/detailed-5reps",
              "& D:/Tools/Anaconda/envs/Pytorch312/python.exe -m proxy_analysis.reproducibility.scope_gate outputs/detailed-5reps",
              "& D:/Tools/Anaconda/envs/Pytorch312/python.exe -m proxy_analysis.reproducibility.metadata_report outputs/detailed-5reps", "```", "",
              "preflight按会话保存checkpoint；同源文件大小/mtime、登记行和审计代码指纹命中则跳过。"
              "重新处理源文件或依赖解析器改动时，应使用新的输出目录或更新审计版本。", "",
              "正式统计未启动；原始数据与上一阶段outputs保持不变。"]
    (root / "implementation-gate-report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {len(routes)} route records and implementation-gate-report.md")


if __name__ == "__main__":
    main()
