# G1 定点复核与下一确认事项

日期：2026-09-30。未执行训练；原 run-01 候选决定未被改写。

## 1. 环境与可复现性

Pytorch312 / Python 3.12 / PyTorch 2.5.1 / CUDA 12.4；NVIDIA GeForce RTX 4060 Ti，16 GiB。CUDA FP64 矩阵运算通过。资格阶段以 CPU 读元数据为主，不代表训练退回 CPU。

独立台账/封存校验 12 项全部通过；基础单元测试 7 项通过。原始包哈希与实际 TCP/carrier 包隔离尚未认证。

## 2. 当前可推进范围

四重复六业务下，非 Hy2 共 600 候选，589 次无元数据保留项。其余 11 次由 7 次主文档关联矛盾与 6 次恢复导航组成，其中 2 次重叠。

若仅接受有成功恢复证据的六次导航，仍有 7 次路由关联问题，故 593/600 也不是完整等预算主队列。不能直接删除七次后按原 120 次/协议训练。

## 3. 七次主文档—连接证据冲突

这七次浏览器主文档均返回 HTTP 200，但关联连接的 post_flow_disposition=failed_before_socket、字节为零、egress=unknown。match 的高置信度不能消除该矛盾。可能涉及连接尝试/重试归属，当前不能认定根因，也不能任选其他成功连接替换。原资格表的 unresolved_mixed_success_routes 包含纯 unknown 情况；此处是 unknown，不是已确认同时经 direct 与 proxy。

| 协议 | 内容 | Session |
| --- | --- | --- |
| anytls | https://www.youtube.com/results?search_query=watercolor+tutorial | f601f165-b9dc-49fa-b04e-3ef22527e909 |
| trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 66fc3aec-992b-480b-b1d3-e1fc28ab7f3a |
| shadowsocks | https://en.wikipedia.org/wiki/Transport_Layer_Security | 91ef7df6-017e-452a-9f52-e90b3b5d1d2e |
| anytls | https://en.wikipedia.org/wiki/Transport_Layer_Security | 0229d915-efa0-4347-965f-6c858aaee098 |
| vmess | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | b1cb419d-0c8f-4bfb-bd2c-9601b15d3f84 |
| anytls | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | c9bf41e6-7219-4684-b71f-56de4a43f320 |
| anytls | https://www.bing.com/search?q=network+traffic+analysis | 760d6951-6319-45c6-88b2-b586b6a2469f |

## 4. 六次恢复导航：建议接受标签，暂不实施豁免

六次均有 NAVIGATION_TIMEOUT_RECOVERED、load_event_observed=true、final_status=200。建议保留为有效页面访问，同时保留 degraded 标记。两次 AnyTLS 还存在第 3 节关联矛盾，接受标签不能放行关联资格。

该建议不需要删除或重选访问，不更改原始 summary；确认后由单独 acceptance ledger 记录。

## 5. Hy2 与 AnyTLS

Hy2 的 175 次、35 内容、五重复归于同一 carrier/adapter；受限 trace 中实际有 logical_carrier_bind 和 proxy_dial，relation=reused，因而不是只看目录名的推测。没有在这些窗口中观察到 carrier_open，不能伪造创建时刻或证明其完整生命周期。

AnyTLS 有多个 carrier 的 open/bind/close 证据；详细数量见 shared-lifecycle-summary.json。未发现跨选中内容的同实体登记，并不替代后续 TCP 原包与路径复用审计。

## 6. Bilibili

150 次主文档为 DIRECT。额外按 bilivideo CDN/常见媒体后缀检索全部资源类型，共发现 8832 个候选媒体请求，其中 direct=8813、proxy=0、unknown=19。这支持将其与代理业务主队列分开，而不是声称没有视频资源请求。该启发式不是完整媒体识别，也不能单独证明视频实际播放。

## 7. 推荐的下一决策

建议确认：

1. 主六业务和重复 1–4 不变；
2. 接受上述六次已恢复导航的业务标签，但不豁免独立的关联问题；
3. 优先对七次主文档关联冲突做有限 NetLog/trace/PCAP 定点取证；保持不训练，不删除、不替补，不修改 TrafficTracer 原始产物；
4. Hy2 默认仅继续测量；若要分类，须另行明确接受同一持久 carrier 的受限窗口威胁模型。

关联未修复且不改变缺失策略前，无法按原完整队列开始正式训练。

## 8. 文件与哈希范围

初步总账见 [gate-G1.md](gate-G1.md)。本次补充审计位于 outputs/extend-calibration-20260930/run-01/g1-review-v2。初审 metadata-hashes 覆盖 pipeline、选中 manifest/summary/flow-index/semantics；本复核另外为定点请求/连接索引保存哈希，并非所有解析文件或 PCAP 都已哈希。该精确范围取代初审报告过宽的‘所有解析元数据’表述。audit.py 使用新配置输出目录复跑；review.py 可用 --review-name 保存独立复核版本。
