# ProxyAnalysis 阶段性成果总结

日期：2026-09-01  
项目阶段：原始数据审计、特征提取、URL/页面对齐、统计分析和协议识别基线均已完成  
研究对象：Hysteria2、Shadowsocks、VLESS 三种代理协议的代理前/后加密流量

## 1. 执行摘要

本阶段已经建立了一条不依赖 Wireshark/TShark 派生统计特征的可复现分析链：从 PCAPNG 和 TrafficTracer 原始索引出发，自行解析包头和 TCP 状态，建立 pre/post entity、exclusive pair、Hysteria2 shared carrier、request、URL、host 和页面级身份关系，提取时序、包长、方向、交互、FR、传输层和网页语义特征，再进行页面内配对统计、URL/host 分层统计和站点隔离的协议识别实验。

目前最重要的阶段性结论如下：

1. 三种代理都显著改变了包数、burst、包长分布和 IAT 结构，但改变幅度和机制不同。
2. Hysteria2 的变化最强：页面级平滑 log-ratio 中位数对应约 9.27 倍包数、6.38 倍 transport bytes、7.56 倍 burst count；其 packet-length JS、累计形状距离和方向转移变化也显著最大。
3. Shadowsocks 和 VLESS 的页面 transport-byte 总量变化相对小，但 packet count 和 burst count 明显增加，表明代理主要改变 packetization/segmentation 和交互节奏，而不一定等比例增加应用有效负载。
4. VLESS 的 FR-switch（只计方向切换）页面级中位 log-ratio 为 0.2356，对应平滑比值约 1.27；Shadowsocks 的中位数为 0，未显示稳定的 FR-switch 放大。
5. 三协议在 11 个公共 delta/distance 指标上均存在显著 omnibus 差异；其中 Hysteria2 与另外两种协议的差距最明显。
6. `transition_p_pm` 是 pre 层唯一出现显著三协议差异的核心指标，因此其 post/delta 结果必须解释为协议机制、采集批次和初始流量结构的联合关联，不能直接写成纯代理因果效应。
7. URL-strict 分析支持 Shadowsocks/VLESS 的确认性结论；Hysteria2 因 shared carrier 是协议内生机制，URL 级只能作为 weighted carrier-context 描述，不能声称精确的 post-to-URL 归属。
8. 协议识别方面，站点隔离的 5-fold × 5-repeat nested CV 中，A-core multinomial logistic regression 的 mean macro-F1 为 0.867，是当前首选基线。
9. FR-only macro-F1 为 0.754，说明 FR 本身具有明显辨识力；但从完整 A-core 中移除 reversal 后性能几乎不变，说明 FR 与 transition、burst、packetization 等特征高度冗余。FR 更适合作为低维、可解释的代理变换指标，而不是声称其必然提升完整分类器性能。
10. 当前捕获点只观察到 pre Fake-IP 和 post proxy endpoint，不观察代理出口到源站/CDN 的连接。SNI/host 只能作为 metadata，不能据此确定 CDN IP、供应商或 PoP。

## 2. 原始数据集与审计结果

### 2.1 数据规模

| 项目 | 数量 |
| --- | ---: |
| 总 session | 192 |
| Hysteria2 session | 64 |
| Shadowsocks session | 64 |
| VLESS session | 64 |
| 顶层 target URL | 64 |
| site group | 50 |
| request occurrence | 32,713 |
| connection | 5,024 |
| logical flow | 18,571 |
| proxy connection | 2,048 |
| direct connection | 2,625 |
| rejected connection | 325 |
| shared proxy connection | 616 |
| eligible exclusive pre/post pair | 1,432 |

每个 target URL 在三种协议中各采集一次，因此形成 64 × 3 的页面矩阵。它支持“同页面、跨协议”的配对比较，但不是同一协议、同一页面的多次重复实验。

### 2.2 分协议连接结构

| 协议 | Request | Connection | Logical flow | Proxy conn. | Direct conn. | Rejected conn. | Exclusive pair | Shared proxy conn. |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Hysteria2 | 10,736 | 1,679 | 7,039 | 616 | 965 | 84 | 0 | 616 |
| Shadowsocks | 10,708 | 1,634 | 5,412 | 666 | 881 | 85 | 666 | 0 |
| VLESS | 11,269 | 1,711 | 6,120 | 766 | 779 | 156 | 766 | 0 |

Hysteria2 的 616 个 proxy logical connection 绑定到 41 个可用 shared carrier window；它没有可解释为一一对应 logical post flow 的 exclusive pair。Shadowsocks 和 VLESS 分别有 666 和 766 个可用 exclusive pair。

### 2.3 索引完整性

- request → connection orphan：0；
- PCAP connection → index orphan：0；
- connection → request orphan：0；
- duplicate connection ID：0；
- duplicate request occurrence ID：0；
- feature extraction 全量质量报告：0 error、0 warning；
- inventory 有 164 个 `artifact_grew_after_manifest` warning，说明部分 artifact 的最终大小晚于 manifest 记录；这是一项采集过程 provenance 警告，但没有导致索引外键或特征质量门失败。

## 3. 统一的观测与身份口径

### 3.1 Entity、pair 与 carrier

- `entity`：一个实际被分析的 pre flow、post outer connection 或 Hysteria2 carrier/page window；
- `exclusive pair`：Shadowsocks/VLESS 中可以一一关联的 pre TCP 与 post TCP entity；
- `shared carrier`：Hysteria2 中多个 logical pre connections 共享的 post UDP carrier；
- `session`：一次顶层页面访问，是主要推断单位；
- `target_url_hash`：顶层访问 URL 的稳定 SHA-256 身份；
- `normalized_url_hash`：移除 query/fragment、规范默认端口后的资源 URL 身份；
- `request_occurrence_id`：一次具体 request；
- `url_connection_incidence_id`：`session × normalized URL × connection` 去重后的关联单位。

### 3.2 方向口径

- `+1/up`：第一个包的发起方 → 响应方；
- `-1/down`：响应方 → 发起方；
- 所有方向序列、signed length、volume、transition、burst、FR 都使用这一统一口径；
- 只使用 TCP/UDP data payload 是否非空来定义 non-empty packet，不依赖 Wireshark 的高级流分析字段。

### 3.3 隐私与 metadata

- 不保存 payload，也不保存 payload prefix/hash；
- full resource URL 默认不进入特征表，使用 SHA-256 identity；
- URL、host、IP、port、SNI、协议字符串、session ID 仅作为 metadata、分组或审计字段；
- 这些字段被排除出主模型特征 allowlist；
- `198.18.0.0/15` 明确标记为 Fake-IP；post proxy node 不标记为 origin/CDN。

## 4. 已提取的特征全集

本项目区分“已经提取并落盘”“进入统计确认性 allowlist”“进入协议识别模型”三个层次。以下特征并非全部同时进入每一项分析。

### 4.1 原始序列特征

每个 entity 保存最多前 32 个包的：

- direction sequence；
- signed TCP/UDP transport payload-length sequence；
- signed IP total-length sequence；
- packet IAT sequence，单位 ns；
- 配置中冻结的分析 prefix 长度为 8、16、32。

这些序列已经提取，但当前 tabular 协议分类器并未直接使用完整序列模型；现阶段主要使用其分布、histogram、transition、burst 和累计形状派生量。

### 4.2 Directional workload / volume

对 packet、transport payload bytes、IP bytes 和 captured bytes 分别计算：

- total；
- up；
- down；
- up/down log-ratio；
- up/down normalized difference。

代理前后 scalar 变化采用：

\[
\log\text{-ratio}=\ln\frac{post+\epsilon}{pre+\epsilon},\qquad \epsilon=1
\]

以及：

\[
\text{normalized difference}=\frac{post-pre}{post+pre}.
\]

### 4.3 Packet length 与 IAT 分布

对 transport payload length、IP total length、all-packet IAT 和 non-empty-packet IAT 计算：

- count、min、max、sum、mean、population SD；
- p01、p05、p10、p25、p50、p75、p90、p95、p99；
- zero fraction；
- coefficient of variation。

固定 histogram 包括：

- transport payload length：0–65,536 bytes 的 17 个区间；
- IP total length：0–65,536 bytes 的 17 个区间；
- IAT：0 μs–30 s 的 20 个对数式区间。

代理前后分布距离包括：

- fixed-bin Jensen–Shannon divergence，log base 2；
- Wasserstein distance；
- two-sample KS statistic 与 p value；
- IAT Wasserstein 在 `log1p(μs)` 域计算；
- 少于 20 个样本时标记 `low_power`。

### 4.4 Direction transition matrix 与 entropy

只使用 non-empty packet direction，构造：

- `n_pp`：up → up；
- `n_pm`：up → down；
- `n_mp`：down → up；
- `n_mm`：down → down；
- 条件概率 `p_pp/p_pm/p_mp/p_mm`；
- direction entropy；
- conditional transition entropy；
- pre/post transition vector 的 L1 和 Frobenius distance。

其中 `p_pm` 表示在前一个 non-empty packet 为 up 时，下一个包切换为 down 的概率。

### 4.5 Burst 与 active/idle

Direction-run burst：

- 连续同方向包组成一个 burst；
- burst count；
- 每个 burst 的 packet count、payload bytes、duration 分布。

Time-gap burst：

- 以 1 ms、10 ms、100 ms 为 gap threshold；
- 计算 burst count、packet count、payload bytes 和 duration 分布。

Active/idle：

- 使用 100 ms、500 ms、1,000 ms threshold；
- 分别统计 active duration 与 idle duration 分布。

### 4.6 Cumulative traffic shape

在 normalized time 与 normalized packet index 两个横轴上，使用 101 个固定 grid points 和 previous/step interpolation，计算：

- signed cumulative transport bytes；
- absolute cumulative transport bytes；
- up cumulative transport bytes；
- down cumulative transport bytes。

代理前后比较包括：

- absolute curve 的 L1 mean、L2 RMS、max absolute distance；
- endpoint 归一化后的累计曲线距离；
- 页面聚合表使用 entity-normalized curve 的均值/packet-weighted mean，不把多个 entity 的均值曲线伪称为一个全局时间序列。

### 4.7 Flow Reversal / carrier reversal

当前实现同时保存：

- `fr_runs`：第一个 non-empty direction run 计 1，此后每次方向切换加 1；
- `fr_reversals`：只计相邻 non-empty packet 的方向切换次数，即 `fr_runs - 1`；
- non-empty packet count；
- payload bytes；
- non-empty sequence duration；
- `fr_norm_packets = reversals/(N-1)`；
- FR per second；
- FR per KiB；
- observed 与 `unique_seq` 两种版本。

需要特别说明：用户论文定义中“第一个非空 flow 将 FR 从 0 增为 1”的 \(\mathcal{FR}\) 对应当前代码的 `fr_runs`。当前统计主表标记为 `flow_reversals` 的结果实际使用 `fr_reversals`，即零起始的 direction-switch count。论文定稿前必须用 `fr_runs` 再做一次正式复核，或明确把现有指标改名为 FR-switch。

此外，`unique_seq` 当前排除 full retransmission，但 partial retransmission 仍按观测 packet 保留，因此不能解释为严格的 payload-byte 去重序列。

对 Hysteria2：

- pre inner logical connections 是 TCP，可计算 inner FR；
- post carrier 是 UDP，只计算 carrier datagram reversal；
- `flow_reversal_preservation_applicable=false`；
- 禁止把 TCP FR 与 UDP carrier reversal 当作同一个量做 preservation 检验。

### 4.8 TCP state、RTT、重传与乱序

项目根据原始 TCP seq/ack/flags 自行完成：

- 32-bit TCP sequence unwrap；
- sequence/payload interval coverage；
- control-only、new data、full retransmission、partial retransmission、out-of-order-or-late 分类；
- retransmitted payload bytes 与 unique payload bytes；
- ACK-based RTT samples；
- conservative Karn 处理：重传后 ambiguous segment 不生成 RTT sample；
- 当前 primary RTT 不使用 SACK 推断。

### 4.9 TCP flags、window 与 handshake

- FIN/SYN/RST/PSH/ACK/URG/ECE/CWR/NS count；
- raw advertised window 的 all/up/down 分布与 zero-window count；
- SYN/SYN-ACK options 自解析；
- 双方 window scale 均成功协商时才计算 effective window；
- 3-way handshake completeness；
- SYN → SYN-ACK、SYN → final ACK；
- first reverse、first non-empty reverse latency；
- first/second directional flight 的 packet、byte、duration。

### 4.10 URL、host、concurrency 与 multiplexing

- request count、connection count；
- request concurrency 与 connection concurrency；
- URL-level/host-level request occurrence、unique connection、proxy/direct/rejected connection count；
- connection reuse factor；
- Hysteria2 carrier 上 logical connection、unique URL、unique host 与 connection concurrency；
- request/connection end-time source 与 fallback reason；
- 页面级 proxy/direct/rejected/unavailable request 和 unique connection count；
- direct/rejected workload 与 proxy transformation 分开保存。

### 4.11 Metadata-only 特征

- IP、port；
- target domain、host/subdomain；
- URL hash；
- protocol label；
- SNI placeholder/role；
- Fake-IP、proxy endpoint、direct-origin-candidate role。

这些字段只用于分组、coverage、异常和混杂审计，不进入主模型。当前尚未运行独立的原始 ClientHello/SNI 自解析阶段。

## 5. 已生成的数据产品

### 5.1 基础特征表

| 表 | 行数 | 特征列数/说明 |
| --- | ---: | --- |
| entity-wide | 9,121 | 1,881 个数值特征列 |
| exclusive-pair-wide | 1,432 | 46 个 pair feature columns |
| Hysteria2-window-wide | 41 | 114 个 window feature columns |
| web-session-wide | 192 | 21 个 web feature columns |

所有表的 site/session/carrier group split 交叉数均为 0。

### 5.2 URL 对齐表

| 表 | 行数 | 列数 | 作用 |
| --- | ---: | ---: | --- |
| `url-connection-index.parquet` | 32,713 | 60 | request、URL、connection、entity、endpoint 关联 |
| `url-aligned-pair-features.parquet` | 13,211 | 797 | URL incidence 级 pre/post 与 transformation |
| `page-aligned-protocol-features.parquet` | 192 | 1,129 | 64 target URL × 3 协议页面聚合 |

Request 归属语义：

- direct：17,207；
- exclusive pair：10,928；
- shared carrier：4,128；
- rejected：333；
- unavailable：117；
- 无 connection 的 request：74，原样保留且不填补。

URL identity coverage：

- raw exact resource URL：16,617；其中 4,153 在三协议中都出现；
- query-stripped URL：11,207；其中 4,424 在三协议中都出现；
- host：969；其中 639 在三协议中都出现；
- feature-complete URL 表实际包含 5,938 个 normalized URL；
- weighted、且保留 target context 的三协议 matched resource key：2,239；
- feature-complete matched host key：296。

### 5.3 Page proxy coverage

| 协议 | 可用 proxy pre/post page |
| --- | ---: |
| Hysteria2 | 41 |
| Shadowsocks | 41 |
| VLESS | 44 |

40 个 target URL 同时具备三协议完整 proxy coverage，构成主要 Q2 确认性队列。其余 66 个 page–protocol 行保留为 `proxy_coverage=false`，没有做数值填补。

## 6. 统计分析设计

### 6.1 推断单位

- 页面级主推断单位：session/target URL；
- uncertainty 按 site cluster 处理；
- URL/connection incidence 不被当作独立样本；
- shared connection/carrier 使用 connection、post entity、comparison entity 三类去重权重；
- 同一 target 内多个资源不会增加独立 target/site 数。

### 6.2 队列

- 页面 available：126 行；
- 页面完整 triplet：40 target × 3 = 120 行；
- URL-strict：677 incidence；Hysteria2 2、Shadowsocks 306、VLESS 369；
- URL-weighted：13,211 incidence；
- Shadowsocks/VLESS URL-strict 作为确认性分析；
- Hysteria2 URL-weighted 仅作 descriptive carrier-context；
- 三协议 URL/host weighted 比较标记为 exploratory。

### 6.3 检验与校正

- Q1：paired Wilcoxon signed-rank；大量 ties/低非零数时可退化为 sign-flip；
- Q2：target URL block 内 Friedman test；报告 Kendall's W；
- pairwise：paired Wilcoxon 与 site-blocked sign-flip permutation；
- 5,000 次 site-cluster bootstrap；
- 10,000 次 blocked permutation；
- Benjamini–Hochberg FDR 0.05；
- 固定随机种子 20260901；
- 同时报告效应量、95% CI、raw p、BH q 和 practical threshold。

需要注意：当前 Q1/Q2 表中的 `qvalue_bh` 基于注册的 Wilcoxon/Friedman family；blocked permutation p value 单独保留。若 q 显著但 site-cluster CI 跨 0，应优先报告该不确定性，而不是只引用 q value。

### 6.4 Practical thresholds

- log-ratio：约对应至少 10% 平滑相对变化，即 \(|\log ratio| \ge \ln(1.1)=0.0953\)；
- normalized difference：绝对值至少 0.05；
- JS divergence：至少 0.05；
- normalized cumulative L1：至少 0.05；
- paired rank-biserial：绝对值至少 0.2。

35 个 Q1 结果中 29 个 BH 显著，但只有 20 个同时达到冻结的 practical threshold。因此“统计显著”不能自动写成“变化幅度有实际意义”。

## 7. Q1：同协议页面级代理前后规律

下表中 log-ratio 指标为平滑后的 \(\ln((post+1)/(pre+1))\)；JS 与累计距离为非负 distance；directional 和 transition 指标为 post − pre。

| 协议 | 指标 | 中位数 | Site-cluster 95% CI | BH q | 超过 practical threshold |
| --- | --- | ---: | ---: | ---: | --- |
| Hysteria2 | packet count log-ratio | 2.227 | [1.672, 2.724] | 1.77e-12 | 是 |
| Shadowsocks | packet count log-ratio | 0.856 | [0.780, 0.942] | 1.77e-12 | 是 |
| VLESS | packet count log-ratio | 0.678 | [0.617, 0.759] | 6.63e-13 | 是 |
| Hysteria2 | transport bytes log-ratio | 1.853 | [1.321, 2.392] | 1.86e-11 | 是 |
| Shadowsocks | transport bytes log-ratio | 0.008 | [0.005, 0.010] | 0.00346 | 否 |
| VLESS | transport bytes log-ratio | 0.058 | [0.045, 0.081] | 1.04e-11 | 否 |
| Hysteria2 | IP bytes log-ratio | 1.845 | [1.321, 2.376] | 1.38e-11 | 是 |
| Shadowsocks | IP bytes log-ratio | 0.049 | [0.043, 0.054] | 9.75e-7 | 否 |
| VLESS | IP bytes log-ratio | 0.105 | [0.079, 0.131] | 6.63e-13 | 是 |
| Hysteria2 | directional transport-byte difference | 0.008 | [-0.016, 0.019] | 0.720 | 否 |
| Shadowsocks | directional transport-byte difference | 0.006 | [0.005, 0.008] | 1.77e-12 | 否 |
| VLESS | directional transport-byte difference | 0.031 | [0.017, 0.040] | 6.86e-10 | 否 |
| Hysteria2 | burst count log-ratio | 2.023 | [1.376, 2.535] | 3.18e-12 | 是 |
| Shadowsocks | burst count log-ratio | 0.800 | [0.711, 0.851] | 1.38e-11 | 是 |
| VLESS | burst count log-ratio | 0.578 | [0.480, 0.684] | 1.14e-12 | 是 |
| Hysteria2 | transition `p_pm` difference | 0.492 | [0.406, 0.565] | 3.18e-12 | 是 |
| Shadowsocks | transition `p_pm` difference | 0.014 | [-0.024, 0.043] | 0.707 | 否 |
| VLESS | transition `p_pm` difference | 0.006 | [-0.040, 0.067] | 0.468 | 否 |
| Hysteria2 | entity count log-ratio | -1.609 | [-2.015, -1.253] | 2.21e-7 | 是 |
| Shadowsocks | entity count log-ratio | 0 | [0, 0] | 0.0766 | 否 |
| VLESS | entity count log-ratio | 0 | [0, 0] | 0.119 | 否 |
| Hysteria2 | packet-length JS | 0.701 | [0.615, 0.755] | 1.77e-12 | 是 |
| Shadowsocks | packet-length JS | 0.293 | [0.260, 0.329] | 1.77e-12 | 是 |
| VLESS | packet-length JS | 0.114 | [0.093, 0.161] | 6.63e-13 | 是 |
| Hysteria2 | IAT JS | 0.137 | [0.127, 0.170] | 1.77e-12 | 是 |
| Shadowsocks | IAT JS | 0.073 | [0.065, 0.103] | 1.77e-12 | 是 |
| VLESS | IAT JS | 0.107 | [0.096, 0.128] | 6.63e-13 | 是 |
| Hysteria2 | cumulative L1 | 0.260 | [0.211, 0.319] | 1.77e-12 | 是 |
| Shadowsocks | cumulative L1 | 0.0029 | [0.0023, 0.0044] | 1.77e-12 | 否 |
| VLESS | cumulative L1 | 0.0081 | [0.0065, 0.0136] | 6.63e-13 | 否 |
| Hysteria2 | cumulative max abs | 0.534 | [0.476, 0.629] | 1.77e-12 | 是 |
| Shadowsocks | cumulative max abs | 0.016 | [0.011, 0.021] | 1.77e-12 | 否 |
| VLESS | cumulative max abs | 0.044 | [0.030, 0.068] | 6.63e-13 | 否 |
| Shadowsocks | FR-switch log-ratio | 0 | [0, 0.0066] | 0.0578 | 否 |
| VLESS | FR-switch log-ratio | 0.236 | [0.211, 0.254] | 2.85e-7 | 是 |

### 7.1 更直观的平滑倍数

以下为 `exp(median log-ratio)`，表示 \((post+1)/(pre+1)\)，不是去掉 epsilon 后的精确 raw ratio：

| 指标 | Hysteria2 | Shadowsocks | VLESS |
| --- | ---: | ---: | ---: |
| Packet count | 9.27× | 2.35× | 1.97× |
| Transport bytes | 6.38× | 1.008× | 1.06× |
| IP bytes | 6.33× | 1.05× | 1.11× |
| Burst count | 7.56× | 2.23× | 1.78× |
| Entity count | 0.20× | 1.00× | 1.00× |
| FR-switch | 不适用 | 1.00× | 1.27× |

### 7.2 机制解释

Hysteria2：

- packet/byte/burst 放大远高于 Shadowsocks/VLESS；
- packet-length JS = 0.701、cumulative L1 = 0.260，说明 packetization 和流量随时间的形状被强烈重构；
- `p_pm` 增加约 0.492，说明 outer carrier 的方向切换结构明显不同；
- entity count 约为 pre 的 0.2 倍，是多个 inner logical flows 汇聚为少量 shared carrier 的结构结果，不能解释为页面真实连接需求下降 80%；
- Hysteria2 的结果同时包含协议机制和 carrier-window 观测粒度效应。

Shadowsocks：

- packet count 约 2.35×、burst 约 2.23×，但 transport bytes 只增加约 0.8%；
- 主要变化表现为分片、封装和交互节奏，而不是大量增加有效负载；
- packet-length JS 明显，但 normalized cumulative shape 差异很小；
- FR-switch 中位数为 0，未观察到稳定放大。

VLESS：

- packet count 约 1.97×、burst 约 1.78×；
- transport bytes 增加约 6%，IP bytes 平滑比约 1.11×；
- packet-length 与 IAT 都有稳定变化，但累计形状差异仍小于 practical threshold；
- FR-switch 平滑比约 1.27×，说明方向交互切换增加；
- `p_pm` 的 within-VLESS 中位变化接近 0、CI 跨 0、q=0.468，且 leave-one-site-out 方向不稳定，因此不作正向变化主张。

## 8. Q2：同页面三协议比较

### 8.1 Omnibus effect size

| 指标 | Pre Kendall W / q | Post W / q | Delta W / q |
| --- | ---: | ---: | ---: |
| Packet count | 0.082 / 0.132 | 0.582 / 9.09e-11 | 0.573 / 1.56e-10 |
| Transport bytes | 0.008 / 0.975 | 0.623 / 3.49e-11 | 0.879 / 2.91e-15 |
| IP bytes | 0.001 / 0.975 | 0.601 / 5.15e-11 | 0.837 / 1.06e-14 |
| Directional transport bytes | 0.002 / 0.975 | 0.214 / 1.89e-4 | 0.444 / 2.10e-8 |
| Burst count | 0.044 / 0.404 | 0.613 / 3.91e-11 | 0.520 / 1.13e-9 |
| Transition `p_pm` | 0.262 / 2.58e-4 | 0.910 / 1.09e-15 | 0.770 / 1.43e-13 |
| Entity count | 0.026 / 0.614 | 0.758 / 2.35e-13 | 0.816 / 1.82e-14 |
| Packet-length JS | — | — | 0.910 / 1.71e-15 |
| IAT JS | — | — | 0.310 / 4.12e-6 |
| Cumulative L1 | — | — | 0.758 / 1.24e-13 |
| Cumulative max abs | — | — | 0.811 / 1.82e-14 |

除 `transition_p_pm` 外，packet/byte/direction/burst/entity 的 pre 层没有显著三协议差异，这为 delta 比较提供了较好的 balance 证据。`transition_p_pm` 的 pre imbalance 已冻结为 caveat。

### 8.2 Delta 两两比较的主要方向

以下值为“左协议 delta − 右协议 delta”的配对中位数：

| 指标 | Hysteria2 − Shadowsocks | Hysteria2 − VLESS | Shadowsocks − VLESS |
| --- | ---: | ---: | ---: |
| Packet count log-ratio | +1.286 | +1.443 | +0.199 |
| Transport-byte log-ratio | +1.804 | +1.793 | -0.059 |
| IP-byte log-ratio | +1.755 | +1.745 | -0.055 |
| Directional-byte difference | +0.004，ns | -0.029 | -0.024 |
| Burst-count log-ratio | +1.185 | +1.342 | +0.146 |
| Transition `p_pm` difference | +0.474 | +0.448 | -0.014，ns |
| Entity-count log-ratio | -1.562 | -1.609 | 0，ns |
| Packet-length JS | +0.397 | +0.548 | +0.168 |
| IAT JS | +0.063 | +0.033 | -0.023 |
| Cumulative L1 | +0.244 | +0.240 | -0.005 |
| Cumulative max abs | +0.523 | +0.469 | -0.025 |
| FR-switch log-ratio | 不适用 | 不适用 | -0.230 |

除表中标记 `ns` 的三项外，其余 pairwise q < 0.05。需要注意，Shadowsocks − VLESS 的 packet-count pairwise q 虽显著，但 site-cluster CI 为 [-0.022, 0.304]，跨越 0，说明该差异对站点组成仍有不确定性。

综合来看：

- Hysteria2 对 packetization、payload envelope、burst、transition 和 cumulative shape 的重构最强；
- Shadowsocks 相比 VLESS 有更高的 packet-count/burst/packet-length divergence；
- VLESS 相比 Shadowsocks 有更高的 byte overhead、IAT JS、cumulative distance 和 FR-switch 放大；
- Shadowsocks/VLESS 的 entity count 基本一致；
- Hysteria2 的较低 entity count 是 shared-carrier 聚合语义，不能和 exclusive TCP outer connection count 作简单物理等价解释。

## 9. Q3：URL/host 分层规律

### 9.1 冻结口径

- Shadowsocks、VLESS：`unique_url_count_on_connection=1`、非 shared、非 reused comparison entity 的 URL-strict 队列用于确认性统计；
- Hysteria2：URL-strict 只有 2 个 target cluster，低于最小 20，因此使用 URL-weighted carrier-context 描述；
- 跨三协议 URL/host 比较使用 weighted 队列，但明确标记 exploratory；
- 匹配键始终包含 `target_url_hash`，避免把不同顶层页面中的同名资源错误合并。

### 9.2 Within-protocol URL 结果

| 协议/口径 | 指标 | 中位数 | Site-cluster 95% CI | BH q |
| --- | --- | ---: | ---: | ---: |
| Hysteria2 weighted descriptive | Packet-count log-ratio | 1.535 | [1.223, 1.987] | N/A |
| Hysteria2 weighted descriptive | Payload-byte log-ratio | 1.198 | [1.077, 1.762] | N/A |
| Hysteria2 weighted descriptive | Burst-count log-ratio | 1.310 | [1.005, 1.861] | N/A |
| Hysteria2 weighted descriptive | Packet-length JS | 0.615 | [0.459, 0.721] | N/A |
| Hysteria2 weighted descriptive | IAT Wasserstein | 0.671 | [0.606, 0.699] | N/A |
| Hysteria2 weighted descriptive | Cumulative L1 | 0.320 | [0.255, 0.411] | N/A |
| Shadowsocks strict | Packet-count log-ratio | 0.317 | [0.278, 0.369] | 1.08e-4 |
| Shadowsocks strict | Payload-byte log-ratio | 0.040 | [0.033, 0.042] | 1.08e-4 |
| Shadowsocks strict | Burst-count log-ratio | 0.105 | [0.080, 0.167] | 1.08e-4 |
| Shadowsocks strict | Packet-length JS | 0.436 | [0.412, 0.453] | 1.08e-4 |
| Shadowsocks strict | IAT Wasserstein | 1.153 | [1.075, 1.207] | 1.08e-4 |
| Shadowsocks strict | Cumulative L1 | 0.0026 | [0.0018, 0.0037] | 1.08e-4 |
| Shadowsocks strict | FR-switch log-ratio | 0 | [0, 0] | 0.133 |
| VLESS strict | Packet-count log-ratio | 0.516 | [0.491, 0.560] | 1.08e-4 |
| VLESS strict | Payload-byte log-ratio | 0.668 | [0.565, 0.688] | 1.08e-4 |
| VLESS strict | Burst-count log-ratio | 0.251 | [0.194, 0.319] | 1.08e-4 |
| VLESS strict | Packet-length JS | 0.272 | [0.252, 0.300] | 1.08e-4 |
| VLESS strict | IAT Wasserstein | 1.236 | [1.165, 1.307] | 1.08e-4 |
| VLESS strict | Cumulative L1 | 0.0144 | [0.0095, 0.0197] | 1.08e-4 |
| VLESS strict | FR-switch log-ratio | 0.288 | [0.288, 0.288] | 1.08e-4 |

URL-strict 结果与页面级结果在主要方向上相符：VLESS 的 payload/FR 变化高于 Shadowsocks；Shadowsocks 的 packet-length divergence 较高；两者累计形状变化都较小。Hysteria2 数值只表示一个 URL 与共享 carrier context 的加权关联，不表示该 URL 独占这些 outer packets。

### 9.3 Host/subdomain 与 CDN 边界

- raw host identity 共 969 个；
- feature-complete weighted host metric long 表 9,801 行；
- 三协议 feature-complete matched `target × host` key 为 296；
- 可以分析“同一观测 host 下的流量特征差异”；
- 不可以把 host/SNI 的变化自动解释为 CDN 节点、CDN 供应商或目标服务器变化；
- 当前 `cdn_endpoint_observed=false`，没有可用的 proxy-exit capture、出口 DNS answer、origin IP、ASN 或 PoP 证据。

## 10. 双轨实验与协议识别

### 10.1 Track A：代理变换

- 1,473 个 transformation unit；
- Hysteria2 41、Shadowsocks 666、VLESS 766；
- FR comparable 的 TCP exclusive pair 为 1,432；
- 同一 session 内多个 pair 先取均值，再做协议级统计，避免连接数多的页面获得更高权重；
- 早期 connection/carrier-level 结果与页面级结论一致：Hysteria2 的 packet/byte/cumulative 变化最大，VLESS 的 FR-switch 高于 Shadowsocks。

### 10.2 Track B：协议分类

分类单位为一个 session，只使用 post-side 流量：

- 192 行，三协议各 64；
- A-core：235 个实际模型特征；
- A+B：978 个实际模型特征；
- site-group split，禁止同一 site 跨 fold；
- Hysteria2 carrier group 跨 split 数为 0；
- metadata、协议字符串、session ID、host/IP/port 不进入模型；
- `post_carrier_count/post_outer_connection_count` 这类能够直接泄露 Hysteria2 类型的 index-derived shortcut 被排除。

正式评估采用：

- 5-fold StratifiedGroupKFold；
- 5 个外层重复，共 25 个 outer folds；
- 4-fold inner site-group CV；
- imputation、variance filter、feature selection 和超参数选择全部只在 outer-train 内完成；
- 25 个重复 fold 相关，因此只报告描述性 fold 分布，不做普通独立样本显著性检验。

### 10.3 正式模型结果

| Feature set | Model | Feature count | Mean macro-F1 | SD | Fold Q2.5%–Q97.5% |
| --- | --- | ---: | ---: | ---: | ---: |
| A-core | Multinomial logistic | 235 | **0.867** | 0.048 | 0.796–0.943 |
| A-core | Random forest | 235 | 0.838 | 0.066 | 0.714–0.930 |
| A+B | Multinomial logistic | 978 | 0.861 | 0.064 | 0.734–0.959 |
| A+B | Random forest | 978 | 0.848 | 0.074 | 0.736–0.957 |

A-core logistic summed confusion matrix（重复外层 folds 汇总，每个原始 session 会在不同 repeat 的 test fold 中重复出现）：

| True \ Pred | Hysteria2 | Shadowsocks | VLESS |
| --- | ---: | ---: | ---: |
| Hysteria2 | 261 | 53 | 6 |
| Shadowsocks | 41 | 263 | 16 |
| VLESS | 3 | 10 | 307 |

| 协议 | Precision | Recall | F1 |
| --- | ---: | ---: | ---: |
| Hysteria2 | 0.856 | 0.816 | 0.835 |
| Shadowsocks | 0.807 | 0.822 | 0.814 |
| VLESS | 0.933 | 0.959 | 0.946 |

### 10.4 消融结果

| 特征子集/消融 | Feature count | Mean macro-F1 | 相对完整 A-core logistic |
| --- | ---: | ---: | ---: |
| Transition + burst | 120 | 0.863 | -0.0037 |
| Packet length + IAT | 61 | 0.861 | -0.0061 |
| Packet length only | 38 | 0.851 | -0.0157 |
| A-core 去掉 cumulative | 224 | 0.859 | -0.0077 |
| A-core 去掉 packetization/timing | 174 | 0.844 | -0.0225 |
| B transport only | 743 | 0.839 | -0.0280 |
| Interaction family | 131 | 0.839 | -0.0280 |
| IAT only | 23 | 0.834 | -0.0328 |
| FR/reversal only | 11 | 0.754 | -0.1133 |
| Workload/volume only | 32 | 0.743 | -0.1237 |
| Cumulative shape only | 11 | 0.595 | -0.2719 |
| A-core 去掉 reversal | 224 | 0.868 | +0.0005 |

由此可以得出：

- transition + burst 已经捕获了大部分分类信息；
- packet length + IAT 也接近完整 A-core；
- workload 单独不足以区分机制；
- cumulative shape 单独较弱，但从完整 A-core 中移除后仍有小幅下降，说明它提供少量互补信息；
- B 类 transport 特征没有带来稳定增益；
- FR-only 明显优于随机水平，但加入完整交互/packetization 特征后增益被其他相关特征吸收。

## 11. FR 的当前证据定位

### 11.1 已经支持的主张

- FR/FR-switch 是低维、方向可解释的交互结构指标；
- VLESS 的 proxy transformation 中 FR-switch 增加，Shadowsocks 未显示同样的稳定增加；
- FR-only 对协议分类具有明显辨识力，mean macro-F1 约 0.754；
- FR 与 transition/burst 相关，但从交互结构角度容易解释，适合用于机制分析和低维 fingerprint。

### 11.2 当前不支持的主张

- 不能声称 FR 必然提高完整分类器性能；
- 不能把 Hysteria2 UDP carrier reversal 等同于 TCP Flow Reversal preservation；
- 不能忽略 `fr_runs` 与 `fr_reversals` 的定义差异；
- 不能把 URL-weighted Hysteria2 reversal 解释为单个 URL 的精确 post FR。

### 11.3 推荐论文定位

将 FR 定位为：

> 面向代理前后流量的可解释交互结构与保持性指标。它单独具有协议辨识能力，并能揭示 Shadowsocks/VLESS 的不同方向切换变换；在完整特征集中，其信息与 transition、burst 和 packetization 高度重叠，因此主要贡献是机制解释和低维表示，而不是保证提升高维分类器性能。

论文中应优先使用与你原始定义一致的 `fr_runs`；现有 `fr_reversals` 结果可以作为“direction-switch count”敏感性分析。

## 12. 稳健性与质量

### 12.1 统计稳健性

- 140 项方向稳定性检查；
- 139 项方向稳定；
- 唯一不稳定项：VLESS `transition_p_pm`；
- 该项中位数 0.006，低于 0.05 practical threshold；
- q=0.468；blocked permutation p=0.344；
- site-cluster CI [-0.040, 0.067]；
- leave-one-site-out 方向稳定率 58.8%；
- 已冻结表述为“无稳定或实际意义充分的 within-VLESS directional shift”。

已执行的主要 sensitivity 包括：

- page available vs complete triplets；
- URL-strict vs URL-weighted；
- query-stripped vs single exact URL；
- 排除 direct/rejected 比例最高的 10% session；
- leave-one-site-out；
- Hysteria2 inner-union envelope vs carrier-full-lifetime packet-count 口径。

### 12.2 自动质量门

- 特征提取：passed，0 error、0 warning；
- URL aligned tables：passed，0 error、2 个 coverage warning；
- 统计分析：passed，0 error、3 个已解释 warning；
- 71 项单元测试通过；
- 特征配置 SHA-256：`458a117213c3b83cc9aa2a835ec292404f20d9055d5c7b3c98c9e847b3360d27`；
- 最终统计配置 SHA-256：`52cb27635037b5c09ab92ac79f0bd64e1a12e1138753aaf80eaa9c9ab2e8ccbf`。

## 13. 当前限制

1. 每个 target URL 每协议只有一次访问，没有重复采集，无法完全分离协议、时间、网络、缓存和服务端状态。
2. 完整三协议 proxy coverage 只有 40/64 个 target URL；缺失样本没有填补。
3. Hysteria2 的观测单位是 shared carrier window，与 Shadowsocks/VLESS exclusive pair 不同；跨协议效应包含观测粒度差异。
4. HTTP/2/HTTP/3 multiplexing 下无法把一个共享 connection/carrier 的全部 packet 无歧义分给单个 request。
5. URL weighted analysis 控制了伪重复，但不等于 packet-to-request ground truth attribution。
6. 当前统计主表使用 `fr_reversals`，而原论文定义更接近 `fr_runs`；正式发表前必须复核。
7. `unique_seq` 只排除 full retransmission，不是严格 payload interval 去重。
8. SNI 尚未自解析；即使解析成功也只能提供 hostname metadata，不能单独识别 CDN endpoint。
9. 没有代理出口侧 PCAP/DNS，因此不能研究真实 origin/CDN IP、ASN、provider 或 PoP 变化。
10. RTT/retransmission/window 等 B 类特征受路径网络条件影响，当前主要作为辅助和敏感性特征，不作为纯协议因果证据。
11. 多个显著结果的实际效应很小；必须联合报告 q、effect、cluster CI 和 practical threshold。
12. 模型评估的 25 个 outer folds 来自重复 CV，彼此相关，不能作为 25 个独立实验做普通显著性检验。

## 14. 当前阶段可以支持的研究结论

### 14.1 强支持

- 三种代理协议会以不同方式重构 packetization、方向交互、burst、IAT 和累计流量形状；
- Hysteria2 的 shared UDP carrier 机制产生最强的 packet/byte/burst/cumulative transformation；
- Shadowsocks 和 VLESS 虽然 byte-volume overhead 相对小，但 packet-count 和 burst 明显增加；
- VLESS 的 FR-switch 变化高于 Shadowsocks；
- A-core 流量统计能够在 site-isolated 条件下较好地区分三种代理协议；
- transition、burst、packet length 和 IAT 是当前最稳定的判别信息来源。

### 14.2 中等支持/需 caveat

- Hysteria2 和其他协议的差异是协议机制与 carrier observation granularity 的联合效应；
- URL-weighted 的 Hysteria2 结果是 carrier-context association；
- `transition_p_pm` 跨协议差异明显，但存在 pre imbalance；
- cumulative shape 对 Shadowsocks/VLESS 的变化统计显著但实际幅度较小。

### 14.3 当前不支持

- CDN provider、CDN node 或 origin IP 变化；
- 单个 Hysteria2 URL 的精确 post packet attribution；
- FR 为完整分类器带来独立、稳定的增量性能；
- 当前结果是严格因果效应；
- 用一次页面访问代表网站长期稳定行为。

## 15. 建议的下一阶段

按优先级建议：

1. **FR 定义复核**：以 `fr_runs` 重跑页面、URL-strict、Track A 和 FR-only/without-FR 消融；保留 `fr_reversals` 作为敏感性指标。
2. **重复采集设计**：对每个 `target URL × protocol` 至少重复多轮，并随机化协议采集顺序，以分离 protocol 与 temporal/network confounding。
3. **扩大完整 proxy coverage**：调查 24 个未形成完整三协议 proxy pair 的 target URL/session。
4. **序列模型分支**：基于已提取的 signed length、direction、IAT sequence 建立严格 site-group split 的 1D CNN/Transformer baseline，与 tabular A-core 比较。
5. **协议机制分层**：Hysteria2 单独研究 logical-inner → carrier 的 multiplexing/concurrency；Shadowsocks/VLESS 继续使用 exclusive pair。
6. **层级统计模型**：在重复采集后引入 site/target/resource random intercept，估计 protocol × side interaction。
7. **可信 CDN 研究设计**：如确有 CDN 研究目标，需要增加代理出口侧 PCAP 或捕获时刻 DNS answer、origin IP、ASN/PoP 证据；SNI 只作为 hostname metadata。
8. **SNI 自解析**：可从 TCP ClientHello 自解析 SNI，并独立处理 ECH/QUIC Initial；不得由 SNI 推断 CDN IP/provider。
9. **论文结果表冻结**：把 effect、cluster CI、BH q、practical threshold、coverage 和 inference scope 同时纳入每张主表。

## 16. 主要可复现产物

| 产物 | 路径 |
| --- | --- |
| 特征默认配置 | `configs/feature-defaults.yaml` |
| 统计冻结配置 | `configs/statistical-analysis.yaml` |
| 特征质量报告 | `outputs/features/quality-report.json` |
| ML 宽表 manifest | `outputs/ml/ml-export-manifest.json` |
| URL 对齐说明 | `outputs/aligned/README.md` |
| URL 对齐质量报告 | `outputs/aligned/aligned-quality-report.json` |
| 页面 Q1 结果 | `outputs/statistics/url-aligned/q1-within-protocol-results.parquet` |
| 页面 Q2 omnibus | `outputs/statistics/url-aligned/q2-cross-protocol-omnibus.parquet` |
| 页面 Q2 pairwise | `outputs/statistics/url-aligned/q2-cross-protocol-pairwise.parquet` |
| URL/host Q3 结果 | `outputs/statistics/url-aligned/q3-resource-host-results.json` |
| 稳健性矩阵 | `outputs/statistics/url-aligned/sensitivity-matrix.parquet` |
| 统计质量报告 | `outputs/statistics/url-aligned/statistical-quality-report.json` |
| 统计 artifact manifest | `outputs/statistics/url-aligned/statistical-analysis-manifest.json` |
| 正式 nested CV manifest | `outputs/experiments/formal/formal-evaluation-manifest.json` |
| Q1 forest plot | `outputs/statistics/url-aligned/figures/q1-within-protocol-forest.png` |
| Q2 Kendall's W heatmap | `outputs/statistics/url-aligned/figures/q2-cross-protocol-kendalls-w.png` |

## 17. 一句话总结

当前项目已经从“能否从代理前后加密流量中提取稳定特征”推进到“能够以统一口径量化三种代理的 transformation、进行 URL/页面配对统计，并在站点隔离条件下识别协议”的阶段；最清晰的机制证据是 Hysteria2 的强 carrier 重构、Shadowsocks/VLESS 的 packetization–byte overhead 差异，以及 VLESS 相对 Shadowsocks 更明显的 FR-switch 变化。下一阶段的首要任务不是继续堆叠特征，而是统一 `fr_runs`/`fr_reversals` 的论文定义并进行重复采集，从而把当前稳定的关联证据提升为更强的可推广结论。
