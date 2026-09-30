# 六协议迁移 G1：元数据资格与关联审核

日期：2026-09-30。状态：需要队列决策；没有拟合或训练模型。

## 1. 执行范围

已实现 E00–E06 的元数据路径、选中 attempt、文件大小、配置、业务路由与实体图审计。共享连接的 Content trace 按 verified barrier 和授权 causal tail 读取。原始包哈希、实际包覆盖、跨文件包重叠及排他 TCP 生命周期仍待 E07/E08，不能据本报告宣称训练资格全部通过。

## 2. 数据库存

| role | runs | attempts | targets | yaml_matches |
| --- | --- | --- | --- | --- |
| broad | 384 | 387 | 64 | True |
| content | 1050 | 1066 | 35 | True |
| detailed | 540 | 543 | 18 | True |

## 3. 四重复六业务候选

metadata_candidate 只表示本阶段未触发保留项，不是最终可训练。全部 training_eligible=false。

| protocol | proposed | metadata_candidate |
| --- | --- | --- |
| anytls | 120 | 116 |
| hysteria2 | 120 | 0 |
| shadowsocks | 120 | 117 |
| trojan | 120 | 119 |
| vless | 120 | 118 |
| vmess | 120 | 119 |

候选范围内保留原因（可重叠）：

| reason | visits |
| --- | --- |
| carrier_cross_content | 120 |
| label_evidence_requires_review | 6 |
| primary_route_unresolved_or_direct | 7 |

## 4. 主文档路由

成功主文档仅接受目标 URL 或导航证据的 final_url；成功关联可以解释同次失败/取消重试，不能借同域任意资源替代。下表含全部五重复和七业务。

| protocol | route_decision | visits |
| --- | --- | --- |
| anytls | direct_success | 25 |
| anytls | proxy_success | 143 |
| anytls | unresolved_mixed_success_routes | 7 |
| hysteria2 | direct_success | 25 |
| hysteria2 | proxy_success | 150 |
| shadowsocks | direct_success | 25 |
| shadowsocks | proxy_success | 148 |
| shadowsocks | unresolved_mixed_success_routes | 2 |
| trojan | direct_success | 25 |
| trojan | proxy_success | 147 |
| trojan | unresolved_mixed_success_routes | 2 |
| vless | direct_success | 25 |
| vless | proxy_success | 146 |
| vless | unresolved_mixed_success_routes | 3 |
| vmess | direct_success | 25 |
| vmess | proxy_success | 148 |
| vmess | unresolved_mixed_success_routes | 2 |

Bilibili 仍单列。Media 类型请求仅作为资源路由证据，不能等同于正式视频播放或覆盖所有 XHR/MSE 媒体请求。

| protocol | visits | media_requests | media_proxy | media_direct |
| --- | --- | --- | --- | --- |
| anytls | 25 | 0 | 0 | 0 |
| hysteria2 | 25 | 0 | 0 | 0 |
| shadowsocks | 25 | 0 | 0 | 0 |
| trojan | 25 | 0 | 0 | 0 |
| vless | 25 | 0 | 0 | 0 |
| vmess | 25 | 0 | 0 | 0 |

## 5. 非 Hy2 主候选待定访问

不得替换 prior attempt，不补零；逐条原因如下。

| protocol | repetition | content_id | session_id | reasons |
| --- | --- | --- | --- | --- |
| vless | 1 | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 437cf42b-162d-4807-9a82-0a422a01059e | ["label_evidence_requires_review"] |
| anytls | 1 | https://www.youtube.com/results?search_query=watercolor+tutorial | f601f165-b9dc-49fa-b04e-3ef22527e909 | ["primary_route_unresolved_or_direct"] |
| trojan | 2 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 66fc3aec-992b-480b-b1d3-e1fc28ab7f3a | ["primary_route_unresolved_or_direct"] |
| shadowsocks | 4 | https://en.wikipedia.org/wiki/Transport_Layer_Security | 91ef7df6-017e-452a-9f52-e90b3b5d1d2e | ["primary_route_unresolved_or_direct"] |
| anytls | 4 | https://en.wikipedia.org/wiki/Transport_Layer_Security | 0229d915-efa0-4347-965f-6c858aaee098 | ["label_evidence_requires_review", "primary_route_unresolved_or_direct"] |
| vmess | 4 | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | b1cb419d-0c8f-4bfb-bd2c-9601b15d3f84 | ["primary_route_unresolved_or_direct"] |
| anytls | 4 | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | c9bf41e6-7219-4684-b71f-56de4a43f320 | ["label_evidence_requires_review", "primary_route_unresolved_or_direct"] |
| anytls | 4 | https://www.bing.com/search?q=network+traffic+analysis | 760d6951-6319-45c6-88b2-b586b6a2469f | ["primary_route_unresolved_or_direct"] |
| shadowsocks | 4 | https://www.bing.com/search?q=sourdough+bread+recipe | 474b6cb8-e05a-468e-9981-64140efcab01 | ["label_evidence_requires_review"] |
| vless | 4 | https://www.bing.com/search?q=beginner+guitar+chords | 755d4827-f719-46a8-870e-c454b1b6f01e | ["label_evidence_requires_review"] |
| shadowsocks | 4 | https://www.bing.com/search?q=beginner+guitar+chords | 2a04ede3-e579-490e-999c-7b320a943252 | ["label_evidence_requires_review"] |

## 6. 载体与内容独立性

以下是登记实体跨 Session 引用，非自动证明所有引用时间内均有包。严格分组不能忽略这些边。

| protocol | sessions | contents | binding_modes |
| --- | --- | --- | --- |
| hysteria2 | 175 | 35 | ['shared'] |

Hy2 默认不进入 carrier-disjoint 主分类。若接受同一个持久 carrier 内的非重叠窗口研究，须明确批准且单列结论；不能声称无同连接跨集合。AnyTLS 未发现相同登记 ID 跨内容也不等于完成原包独立性审核。

## 7. 文件与证据边界

| status | artifacts |
| --- | --- |
| as_of_growth | 1974 |
| match | 97654 |
| size_mismatch | 4 |

as_of_growth 是显式增长语义，不与固定尺寸不一致混为一谈。原始 PCAP 尚未全量哈希；所有解析得到的元数据有源文件指纹，bounded trace 另有完整文件 SHA256。配置只输出白名单字段，路径身份只保存哈希；这些身份字段不允许进入后续模型。

## 8. 下一步决策

1. 确认六业务、重复 1–4 的等预算设计，第五重复保留但暂不训练。
2. 对第 5 节逐项给定接受或继续审核方向，不能因删除而不对称改变 C/U 预算。
3. 确认 Hy2 只保留测量，或单独批准同持久 carrier 的受限窗口分支。

通过这些决策后再做 E07–E13 原始事件、特征与权限门；本报告不是启动正式训练的许可。

## 9. 复现与产物

运行：`D:/Tools/Anaconda/envs/Pytorch312/python.exe eval/extend_calibration/audit.py`。已完成输出目录不会被覆盖；复跑应使用新配置的输出目录。

产物位于 `F:\Program\VSCode\MyGit\ProxyAnalysis\outputs\extend-calibration-20260930\run-01`，包括 inventory、sessions、attempts、artifact-audit、deployment-registry、label-route-ledger、request-route-evidence、entity-graph、carrier-overlap、bounded-trace-audit、carrier-lifecycle-evidence、cohort-candidates、environment、source-lock、metadata-hashes 与 stage-boundaries。
