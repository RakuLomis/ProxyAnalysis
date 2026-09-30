# 0916 六项变换指标复核：重复性、业务差异与 0914 对照

日期：2026-09-18。状态：P4 已完成；不新增采集、不重新解析 PCAP、不训练模型。

## 1. 核心结论

本轮对预先指定的 packet_count、transport_bytes、burst_count、fr_runs、length_js、iat_js 六项进行描述性复核，结果支持一个有边界的阶段性结论：

> 在所观察的 SS 严格配对流量中，代理后包数和包含空载荷包的方向段数量普遍增加，传输载荷字节量变化较小，同时包长与 IAT 分布发生变化。VLESS 的非空方向段 FR 增加更一致，但包数和 burst 的变化更依赖业务。部分现象在 0914 与 0916 的共同资源及新增资源上都能观察到，但不能据此分离纯协议因果效应。

0916 主队列的典型 post/pre 比值为：

| 部署 | 包数 | 载荷字节 | burst | FR-runs |
|---|---:|---:|---:|---:|
| SS | 1.6746 | 1.0196 | 1.7509 | 1.0561 |
| VLESS | 1.2453 | 1.0589 | 1.0720 | 1.2303 |

“典型比值”严格定义为：每内容先求重复访问的 ln(post/pre) 中位数，再对内容中位数取中位数，最后取 exp。不是总字节之比，也不是全部连接或访问简单混合的中位数。

本轮补强了测量层的变换描述，**不改变此前“配对监督尚未稳定形成单侧业务净收益”的模型结论**。

## 2. 范围、来源与审计

| 队列 | 访问数 | 资源数 | 每资源每部署重复 |
|---|---:|---:|---|
| 0916 主队列 | 240 | 30 | 第 1/2/4/5 轮，4 次 |
| 0916 保守敏感性 | 299 | 30 | 通常 5 次，唯一 MDN 恢复访问仍排除 |
| 0914 严格配对历史参考 | 140 | 14 | 5 次 |

仅分析 SS/VLESS、observed、排他 TCP 配对范围。0914 未混入 0916 模型训练，也未新增任何跨批次分类器。

旧摘要来自 `paired-information-0914/run-01/side-summaries.parquet`。对其全部 140 个会话缓存核对特征配置哈希、提取器哈希、缓存指纹、既有 replay 审核，以及总表与逐会话摘要的一致性。0916 输入继续核验冻结来源。

契约检查支持当前六项的定义和直方图边界可比，不代表两批次的节点、网络状态、动作时长和内容响应相同；也没有独立重建旧缓存所有底层 helper 的历史版本或重新解析原始包。

输出 4,074 条访问×指标记录、888 条内容×部署×指标汇总，未定义指标数为 0。240 与 299 高度重叠，这些记录数不能当作独立样本量。

独立审核另外使用 SciPy 的 Jensen–Shannon 距离平方核验 JS 散度，核对严格对数比、MAD/IQR 和内容等权聚合。审核通过，完整测试 **166 项通过**。

## 3. 计算口径

### 3.1 四个尺度指标

\[
\Delta_{u,r,p,j}=\ln\left(\frac{X_{post}}{X_{pre}}\right).
\]

只在两侧严格为正时定义，不加 1、不做平滑；这与上一轮业务变换表示 `log1p(post)−log1p(pre)` 不同。若有零值应单列，本次实际没有未定义记录。

### 3.2 两个分布指标

分别对每侧直方图归一化，以 2 为底计算 JS **散度**：长度 19 桶、IAT 23 桶，均包含尾桶。取值范围 [0,1]。它不是 JS 距离平方根，也没有正负变化方向，不能把 JS>0 解释为“长度增加”或“速度变慢”。

长度基于非空传输载荷包；IAT 在原始连接内部计算，observed 口径包括空载荷包，不跨无关连接构造 IAT。

### 3.3 重复内与内容间统计

每个内容、部署、指标分别计算：

- 重复访问的 Δ 中位数。
- 未缩放 MAD：median(|Δ−median(Δ)|)，不乘 1.4826。
- IQR：Q75−Q25，使用线性分位数插值。
- 各次重复的方向，以及落入预指定参考带的比例。

再按内容等权汇总，不把连接多的网站赋予更多权重，也不把重复记录视为新的独立内容。

参考带沿用既有契约：比值 [0.9,1.1]，对数区间 [ln(0.9),ln(1.1)]；JS 参考阈值为 0.05。它们是描述性阈值，不是已通过的统计等效性检验或经本数据优化的最佳分界。

### 3.4 burst 不等于 FR

burst_count 在 observed 包序列中按方向连续段统计，包含空载荷包；FR-runs 先筛选非空 TCP 包，再统计方向连续段，首个非空段计 1。两者均先在原始实体内计算再聚合。

因此，SS burst 明显增加而 FR 只小幅变化并不矛盾。该差异与包筛选口径有关，但本次没有通过机制干预证明其具体成因，不能直接断言完全由 ACK 或某一实现细节造成。

## 4. 0916 主队列：总体变换与重复内离散

下表 MAD/IQR 均为“每内容重复内统计，再跨内容取中位数”；前四项单位为自然对数比，后两项为 JS bits。

| 部署、指标 | 典型比值或 JS | 重复内 MAD 中位数 | 重复内 IQR 中位数 | 内容中位数分类，n=30 |
|---|---:|---:|---:|---|
| SS packet_count | 1.6746 | 0.05519 | 0.09377 | 30 个 >1.1 |
| SS transport_bytes | 1.0196 | 0.00326 | 0.00612 | 30 个在 [0.9,1.1] |
| SS burst_count | 1.7509 | 0.05829 | 0.12244 | 30 个 >1.1 |
| SS fr_runs | 1.0561 | 0.02553 | 0.05083 | 24 个在带内，6 个 >1.1 |
| SS length_js | 0.35094 | 0.02454 | 0.04167 | 30 个 >0.05 |
| SS iat_js | 0.19731 | 0.01539 | 0.03116 | 30 个 >0.05 |
| VLESS packet_count | 1.2453 | 0.04650 | 0.09542 | 21 个 >1.1，9 个在带内 |
| VLESS transport_bytes | 1.0589 | 0.00337 | 0.01448 | 26 个在带内，4 个 >1.1 |
| VLESS burst_count | 1.0720 | 0.08151 | 0.15034 | 13 个 >1.1，13 个在带内，4 个 <0.9 |
| VLESS fr_runs | 1.2303 | 0.01305 | 0.02619 | 29 个 >1.1，1 个在带内 |
| VLESS length_js | 0.06266 | 0.00994 | 0.02486 | 16 个 >0.05，14 个 ≤0.05 |
| VLESS iat_js | 0.07825 | 0.01341 | 0.02363 | 30 个 >0.05 |

可见：

- SS 的包数与 burst 增加覆盖全部 30 内容，并且每个内容的四次访问都为正向变化；这不仅是总体中位数为正。
- SS 全部 120 次访问的载荷字节比值都在 ±10% 参考带内。其 27 个内容的四次访问均为正增加，说明“接近原值”不等于零开销。
- VLESS 的 FR 在全部 30 内容、所有四次重复中均增加；但部分增幅不超过 10%。
- VLESS burst 的跨内容方向和重复内波动更复杂：只有 7 个内容四次均增加，2 个内容四次均减少，其余不是全正或全负。因此不宜写成 VLESS 普遍增加 burst。
- VLESS 的字节比值在参考带内的访问比例约 81.7%，低于 SS 的 100%；不能把“多数接近原值”写成完全字节守恒。

MAD/IQR 的大小是描述性的，受单位和指标尺度影响，不直接等同 ICC、绝对可重复性等级或协议可分离性评分。

## 5. 业务分层：总体描述不能掩盖差异

每业务有五个内容。下表为四个尺度指标的典型比值：

| 部署、业务 | packet | bytes | burst | FR |
|---|---:|---:|---:|---:|
| SS YouTube 播放 | 1.9453 | 1.0113 | 2.2326 | 1.0485 |
| SS YouTube 搜索 | 2.0586 | 1.0167 | 2.4274 | 1.0680 |
| SS Wikipedia | 1.6708 | 1.0211 | 1.7925 | 1.0600 |
| SS MDN | 1.4231 | 1.0198 | 1.5664 | 1.1175 |
| SS GitHub | 1.6937 | 1.0084 | 1.6915 | 1.0511 |
| SS Bing | 1.2743 | 1.0243 | 1.3392 | 1.0348 |
| VLESS YouTube 播放 | 1.6353 | 1.0300 | 1.4109 | 1.2402 |
| VLESS YouTube 搜索 | 1.5758 | 1.0321 | 1.4323 | 1.2490 |
| VLESS Wikipedia | 1.1378 | 1.0601 | 1.0639 | 1.2403 |
| VLESS MDN | 1.0670 | 1.0648 | 1.0302 | 1.1949 |
| VLESS GitHub | 1.2535 | 1.1107 | 1.0261 | 1.2453 |
| VLESS Bing | 0.9654 | 1.0760 | 0.8899 | 1.1760 |

值得保留的例外：

- SS 的 MDN FR 增幅较大，五个内容中四个中位数超过 1.1；不能将 SS 的 FR 一概称为几乎不变。
- VLESS GitHub 的载荷字节典型比值约 1.111，五个内容中三个超过 1.1。
- VLESS Bing 的包数略减少，burst 典型比值低于 0.9；五个 Bing 内容的包数中位数都在 ±10% 带内。
- VLESS 的长度 JS 在 Wikipedia 五内容全部 ≤0.05，GitHub 五内容全部 >0.05；包长分布保留程度也依赖业务。

这些都是同批次固定部署关联，不是业务语义对协议变换的独立因果作用。

## 6. 299 队列敏感性

按内容聚合，不按四次/五次重复数量加权。该统计分析不需要模型错配，因此使用全部 299 个有效访问，不额外删去共同轮次以配教师。

| 指标 | SS：240 → 299 | VLESS：240 → 299 |
|---|---|---|
| packet_count 比值 | 1.6746 → 1.6383 | 1.2453 → 1.2241 |
| transport_bytes 比值 | 1.0196 → 1.0180 | 1.0589 → 1.0588 |
| burst_count 比值 | 1.7509 → 1.7494 | 1.0720 → 1.0768 |
| fr_runs 比值 | 1.0561 → 1.0517 | 1.2303 → 1.2324 |
| length_js | 0.35094 → 0.34833 | 0.06266 → 0.05063 |
| iat_js | 0.19731 → 0.19959 | 0.07825 → 0.07691 |

主要方向没有逆转：SS 的包数和 burst 仍为 30/30 内容超过 1.1、字节仍为 30/30 内容在参考带；VLESS 的 FR 改为 30/30 内容超过 1.1。

同时保留变化：VLESS 的包数在 299 中出现一个内容中位数低于 0.9；长度 JS 的总体典型值靠近 0.05。阈值分类不能代替连续值和离散度的报告。

## 7. 与 0914 的有限跨批次复核

### 7.1 两批总体仅并列，不作同质总体检验

| 指标 | SS 0914 / 0916 主队列 | VLESS 0914 / 0916 主队列 |
|---|---|---|
| packet_count 比值 | 1.6363 / 1.6746 | 1.2664 / 1.2453 |
| transport_bytes 比值 | 1.0170 / 1.0196 | 1.0667 / 1.0589 |
| burst_count 比值 | 1.8203 / 1.7509 | 1.1491 / 1.0720 |
| fr_runs 比值 | 1.0241 / 1.0561 | 1.2423 / 1.2303 |
| length_js | 0.32636 / 0.35094 | 0.06059 / 0.06266 |
| iat_js | 0.22565 / 0.19731 | 0.06501 / 0.07825 |

总体方向相近，但旧批次 14 个资源与新批次 30 个资源组成不同，上表不是配对检验，也不支持仅从总体差值判定日期或部署改变了机制。

### 7.2 共同资源是五个，而非全批次旧结论中的 URL 数

本次比较的是两个严格队列，规范化后有五个共同资源：

1. MDN HTTP 文档。
2. Wikipedia Computer_network。
3. GitHub RakuLomis/TrafficTracer 仓库。
4. YouTube 视频 `sAWK0mgrMp4`。
5. Bing 查询 `network traffic analysis`。

前四个 URL 字符串相同；Bing 的 `%20` 与 `+` 通过查询参数解码对应同一搜索词。规范化不删除内容查询参数。Bilibili 没有进入这里的严格代理队列，因此不能沿用全原始批次包含 Bilibili 的重叠计数。

共同资源不保证业务动作、播放时长、返回内容或网络条件相同。旧资源按新标签展示时只是资源对齐，不是重新核准旧活动标签。

对 0916 主队列，与 0914 相比，五共同资源 × 六指标的参考带分类：SS 为 29/30 一致，VLESS 为 25/30 一致。这是描述性的格子计数，不是 30 次独立复现，更没有把不同指标视为独立试验。

例外包括：

- SS Wikipedia FR 从参考带内到超过 1.1。
- VLESS MDN 和 Bing 的长度 JS 从 >0.05 到 ≤0.05。
- VLESS GitHub burst 从带内到 >1.1。
- VLESS Bing 包数从 <0.9 到带内，FR 从 >1.1 到带内。

### 7.3 新增资源也有支持，但不叫独立盲测

0916 的其余 25 个资源中：

- SS：25/25 内容包数和 burst 中位数 >1.1，25/25 字节在参考带内。
- VLESS：25/25 FR 中位数 >1.1；包数 18/25 >1.1；burst 仅 10/25 >1.1、3/25 <0.9，其余在带内。

这说明主要模式不完全由五个重复资源支撑。但本批次已经多轮分析，新增资源也不应被包装为事前封存的独立盲测集。

## 8. 对研究主线的意义

现在可以将测量与预测结果并列而不互相替代：

- 测量层：当前部署下存在可重复观察到的 pre→post 变化模式，SS 与 VLESS 的典型变化不同，也受业务影响。
- 配对分析层：保持真实对应可以改变模型可学到的结构，但并不是任何真配学生都优于错配。
- 单侧业务层：前几轮的监督与迁移实验仍揭示明显利用限制；本轮描述性复核不会自动弥补这一缺口。

“macro workload preservation + micro packetization reconstruction”可以作为 SS 现象的概括性解释，但需要限定为：**当前严格 TCP 范围内载荷量相对接近、包数与方向段增加、分布发生改变**。它不是应用有效字节严格守恒、代理包化机制已被因果验证或对所有网络环境成立的定理。

本轮没有计算 ICC、变换 separability、全特征发现性筛选、CDN/SNI 变化、Hy2 carrier 复核或正式等效性检验。不能以 MAD 较小替代这些尚未完成的分析。

## 9. 产物与复用

- [六指标冻结契约](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/content-generalization-20260916/mechanism-01/p4-transformation/contract.json)
- [逐访问变换表](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/content-generalization-20260916/mechanism-01/p4-transformation/session-transformations.parquet)
- [逐内容重复性表](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/content-generalization-20260916/mechanism-01/p4-transformation/content-repeatability.parquet)
- [总体、业务与重叠分层汇总](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/content-generalization-20260916/mechanism-01/p4-transformation/group-summary.json)
- [共同资源映射](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/content-generalization-20260916/mechanism-01/p4-transformation/overlap-resources.json)
- [共同资源逐指标比较](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/content-generalization-20260916/mechanism-01/p4-transformation/shared-resource-comparison.parquet)
- [独立算术审核](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/content-generalization-20260916/mechanism-01/p4-transformation/independent-validation.json)
- [执行模块](F:/Program/VSCode/MyGit/ProxyAnalysis/src/proxy_analysis/crosscontent/transformation_replication.py)
- [审核模块](F:/Program/VSCode/MyGit/ProxyAnalysis/src/proxy_analysis/crosscontent/transformation_replication_audit.py)

执行环境为 Pytorch312；运行记录：

```powershell
$env:PYTHONPATH='src'
& D:/Tools/Anaconda/envs/Pytorch312/python.exe -m proxy_analysis.crosscontent.transformation_replication
& D:/Tools/Anaconda/envs/Pytorch312/python.exe -m proxy_analysis.crosscontent.transformation_replication_audit
```

入口拒绝覆盖现有目录。报告为已有数据上的预指定小范围描述性复核；本次代码、测试和报告为本地新增，未提交/推送。

至此，原计划 P0–P4 及已确认的教师分法/299 敏感性范围均已完成。未自动启动其他模型、全 300 队列或新的跨批次预测实验。
