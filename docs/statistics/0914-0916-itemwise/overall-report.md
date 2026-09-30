# 0914 / 0916 逐条目统计总报告

本轮从原始连接捕获重新计算，覆盖 987 次选定访问、117 个分批条目；全量登记 1002 次存储尝试。提取错误 0。

## 先看范围，再看变化

本报告区分网页/访问上下文中的严格 TCP 配对、Hy2 共享载体、DIRECT-only 观测。主请求路由、播放有效性与配对可用性独立保留。没有把直连 Bilibili 视频或 Hy2 的 UDP 方向段重新解释为 TCP 代理变换。

## 关键统计

以下仅汇总主请求明确 proxy 的条目；每条目等权。表中倍率是 exp(条目中位 ln(post/pre) 的中位数)。长度/IAT/曲线距离与绝对流量规模另见批次和逐条目报告。

| 批次 | 部署 | 范围 | 指标 | 条目数 | 访问数 | 典型倍率 | Δ中位 | 重复MAD中位 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0914-broad | Hy2 | carrier_context_envelope | burst_count | 37 | 37 | 11.203 | 2.4162 | — |
| 0914-broad | Hy2 | carrier_context_envelope | iat_js | 37 | 37 | — | 0.38716 | — |
| 0914-broad | Hy2 | carrier_context_envelope | length_js | 37 | 37 | — | 0.71605 | — |
| 0914-broad | Hy2 | carrier_context_envelope | packet_count | 37 | 37 | 23.215 | 3.1448 | — |
| 0914-broad | Hy2 | carrier_context_envelope | transport_bytes | 37 | 37 | 16.015 | 2.7736 | — |
| 0914-broad | SS | exclusive_page | burst_count | 39 | 39 | 1.8592 | 0.62016 | — |
| 0914-broad | SS | exclusive_page | fr_runs | 39 | 39 | 1.0329 | 0.032391 | — |
| 0914-broad | SS | exclusive_page | iat_js | 39 | 39 | — | 0.2 | — |
| 0914-broad | SS | exclusive_page | length_js | 39 | 39 | — | 0.31749 | — |
| 0914-broad | SS | exclusive_page | packet_count | 39 | 39 | 1.6603 | 0.507 | — |
| 0914-broad | SS | exclusive_page | transport_bytes | 39 | 39 | 1.0144 | 0.01428 | — |
| 0914-broad | VLESS | exclusive_page | burst_count | 41 | 41 | 1.0705 | 0.068153 | — |
| 0914-broad | VLESS | exclusive_page | fr_runs | 41 | 41 | 1.2439 | 0.21825 | — |
| 0914-broad | VLESS | exclusive_page | iat_js | 41 | 41 | — | 0.072271 | — |
| 0914-broad | VLESS | exclusive_page | length_js | 41 | 41 | — | 0.054306 | — |
| 0914-broad | VLESS | exclusive_page | packet_count | 41 | 41 | 1.2498 | 0.22296 | — |
| 0914-broad | VLESS | exclusive_page | transport_bytes | 41 | 41 | 1.0569 | 0.055321 | — |
| 0914-repeat | Hy2 | carrier_context_envelope | burst_count | 12 | 60 | 17.88 | 2.8837 | 0.14289 |
| 0914-repeat | Hy2 | carrier_context_envelope | iat_js | 12 | 60 | — | 0.35616 | 0.033549 |
| 0914-repeat | Hy2 | carrier_context_envelope | length_js | 12 | 60 | — | 0.70358 | 0.023239 |
| 0914-repeat | Hy2 | carrier_context_envelope | packet_count | 12 | 60 | 33.459 | 3.5103 | 0.16071 |
| 0914-repeat | Hy2 | carrier_context_envelope | transport_bytes | 12 | 60 | 27.586 | 3.3173 | 0.062694 |
| 0914-repeat | SS | exclusive_page | burst_count | 13 | 65 | 1.8256 | 0.60189 | 0.051098 |
| 0914-repeat | SS | exclusive_page | fr_runs | 13 | 65 | 1.0267 | 0.026317 | 0.0048111 |
| 0914-repeat | SS | exclusive_page | iat_js | 13 | 65 | — | 0.22625 | 0.022443 |
| 0914-repeat | SS | exclusive_page | length_js | 13 | 65 | — | 0.33436 | 0.024973 |
| 0914-repeat | SS | exclusive_page | packet_count | 13 | 65 | 1.6311 | 0.48924 | 0.057158 |
| 0914-repeat | SS | exclusive_page | transport_bytes | 13 | 65 | 1.0166 | 0.016481 | 0.0014589 |
| 0914-repeat | VLESS | exclusive_page | burst_count | 14 | 70 | 1.1727 | 0.15932 | 0.033328 |
| 0914-repeat | VLESS | exclusive_page | fr_runs | 14 | 70 | 1.2304 | 0.20734 | 0.011858 |
| 0914-repeat | VLESS | exclusive_page | iat_js | 14 | 70 | — | 0.072237 | 0.012439 |
| 0914-repeat | VLESS | exclusive_page | length_js | 14 | 70 | — | 0.060592 | 0.017699 |
| 0914-repeat | VLESS | exclusive_page | packet_count | 14 | 70 | 1.2834 | 0.24951 | 0.04845 |
| 0914-repeat | VLESS | exclusive_page | transport_bytes | 14 | 70 | 1.06 | 0.058284 | 0.0018359 |
| 0916 | Hy2 | carrier_context_envelope | burst_count | 25 | 125 | 16.142 | 2.7814 | 0.089258 |
| 0916 | Hy2 | carrier_context_envelope | iat_js | 25 | 125 | — | 0.37835 | 0.016607 |
| 0916 | Hy2 | carrier_context_envelope | length_js | 25 | 125 | — | 0.71745 | 0.026201 |
| 0916 | Hy2 | carrier_context_envelope | packet_count | 25 | 125 | 32.977 | 3.4958 | 0.070519 |
| 0916 | Hy2 | carrier_context_envelope | transport_bytes | 25 | 125 | 21.505 | 3.0683 | 0.018316 |
| 0916 | SS | exclusive_page | burst_count | 30 | 150 | 1.7494 | 0.55925 | 0.060446 |
| 0916 | SS | exclusive_page | fr_runs | 30 | 150 | 1.0508 | 0.04954 | 0.024962 |
| 0916 | SS | exclusive_page | iat_js | 30 | 150 | — | 0.19959 | 0.021336 |
| 0916 | SS | exclusive_page | length_js | 30 | 150 | — | 0.34833 | 0.02336 |
| 0916 | SS | exclusive_page | packet_count | 30 | 150 | 1.6383 | 0.49367 | 0.048306 |
| 0916 | SS | exclusive_page | transport_bytes | 30 | 150 | 1.0194 | 0.019171 | 0.0025234 |
| 0916 | VLESS | exclusive_page | burst_count | 30 | 150 | 1.0768 | 0.07398 | 0.095967 |
| 0916 | VLESS | exclusive_page | fr_runs | 30 | 150 | 1.2324 | 0.20897 | 0.014851 |
| 0916 | VLESS | exclusive_page | iat_js | 30 | 150 | — | 0.076912 | 0.013243 |
| 0916 | VLESS | exclusive_page | length_js | 30 | 150 | — | 0.050631 | 0.01177 |
| 0916 | VLESS | exclusive_page | packet_count | 30 | 150 | 1.2241 | 0.20218 | 0.063637 |
| 0916 | VLESS | exclusive_page | transport_bytes | 30 | 150 | 1.0588 | 0.057094 | 0.0039363 |


## 如何理解与此前结果的关系

本轮不是训练集、验证集或测试集上的新模型结果，而是全部条目清单的流量描述。此前 0916 的 240 访问主队列与 299/300 候选只占本轮的一部分；样本范围不同导致总中位数不同，不构成旧实验被推翻。

SS/VLESS 的严格 TCP 上下文可以同口径比较；与 Hy2 的三方比较只能称部署条件下的观测差异。包数、burst、FR 的不同变化不矛盾：burst 含空载荷包，FR 只看非空方向交替；字节守恒也不意味着分包或时间结构守恒。

重复间 MAD/IQR 反映当前少量访问的离散程度，不证明总体稳定性。大包、重传、RTT、路由和实际页面加载变化均可能影响统计，不能归因于代理协议本身。

## 数据与质量

侧特征表 9,954 行；变换明细 459,966 行。旧 0916 业务缓存数值交叉核对 36,000 项，差异 0。质量状态：True。

详细字段定义、缺失与零值政策见 [methods](methods.md)。可用性见 coverage-and-eligibility.parquet；原始来源摘要见 source-hashes.json；每次访问缓存可增量重用。

## 分报告

- [0914 broad：64 个条目](dataset-0914-broad.md)
- [0914 repeat：18 个条目](dataset-0914-repeat.md)
- [0916：35 个条目](dataset-0916.md)
- [跨批次参考](cross-dataset-comparison.md)
- [全条目入口](README.md)

## 统计解读补充

[重点发现、共同条目比较、六业务统计及 Hy2 解释边界](findings.md)
