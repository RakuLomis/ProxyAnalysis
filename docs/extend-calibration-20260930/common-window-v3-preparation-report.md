# Extend 共同窗口 v3：资格、隔离、权限包与 CUDA 准备报告

日期：2026-09-30。实验目录：`outputs/extend-calibration-20260930/run-01/extraction-03/`。

## 1. 执行结论

已按用户确认，将研究对象统一为双侧共同稳定采集区间内的代理流量，重新处理全部 600 次访问，没有删访问、替换重复或修补原始 PCAP。

**600/600 次访问通过新窗口下的 W 覆盖检查。准备阶段通过，正式生成、分类与评分尚未运行。**

本轮完成：

- 采集器/浏览器时钟源码与实际构建身份核查；
- 600 次访问的统一窗口、生命周期范围和原始特征重算；
- 30,080 个建连区间与原始 TCP 握手的独立时钟核验；
- 内容、登记 carrier、原文件、SYN 身份和部分原始正载荷包指纹隔离审核；
- 1,080 个情景、4,320 个权限目录以及 4,320 项负权限检查；
- W/T 各一个仅训练区的 1,000 步 CUDA 冒烟；
- 36 项测试和实验预算封存。

不应把这些数字解释为业务收益。**没有正式留出预测，没有新 F1/CE/Brier，没有 paired 优于 raw/group 的新结论。**

## 2. 共同窗口的最终定义及依据

### 2.1 为什么没有直接采用 `min(stopped)`

精确历史提交表明，TrafficTracer 的 `ready` 是抓包文件头就绪、进程仍存活后记录的 `time.monotonic()`；`stopped` 则在停止函数返回后记录，即进程退出完成时刻，而非严格的最后有效捕获时刻。

因此，“`stopped` 前一瞬仍在采集”不是保存数据能够支持的事实。若直接把它作为共同稳定区间结束点，会把关闭等待期间纳入研究总体。

本轮采用更保守、对全部会话一致的：

\[
[\max(t_{\mathrm{ready,pre}},t_{\mathrm{ready,post}}),\;t_{\mathrm{browser\_quiescent}}).
\]

源码中的采集健康检查发生在 browser_quiescent 之后、停止抓包之前；全部会话还要求 coverage=passed、无错误、两侧正常退出，并验证窗口包含浏览器启动/导航顺序。这一窗口不是“整个会话完整生命周期”，也不等于抓包文件首末包区间。

共同窗口长度：最小 62.396 秒，中位数 66.488 秒，均值 70.355 秒，最大 103.983 秒。没有按模型结果选窗口长度。

依据为实际 [TrafficTracer job 源码](https://github.com/RakuLomis/TrafficTracer/blob/1be20b929ba8454678f5a33b68fd7f3b97edadf4/traffictracer/capture/job.py)与[抓包就绪实现](https://github.com/RakuLomis/TrafficTracer/blob/1be20b929ba8454678f5a33b68fd7f3b97edadf4/traffictracer/capture/tshark.py)，完整只读副本及哈希保存在 `clock-source-evidence/`。

### 2.2 时钟映射核查

保存的 Chrome/Linux 构建使用 CLOCK_MONOTONIC；NetLog 的 timeTickOffset 将毫秒 TimeTicks 映射到 Unix 时间。每个会话使用其自己的偏移，不采用整批统一常数。600 次会话有两个保存值，相差 441 ms。

独立核验使用精确 TCP 端点，将原始 PCAP 的 SYN/SYN-ACK 与 NetLog 建连 begin/end 区间比较：

| 检查 | 结果 |
|---|---:|
| 有可观测锚点的会话 | 600/600 |
| 可观测成功建连 | 30,080 |
| 固定 2 ms 量化包络内通过 | 30,080 |
| 不通过 | 0 |
| 根据 PCAP 重新拟合 offset | 没有 |

2 ms 是登记的量化容差，不是从结果选择的 offset，也不是对任意时钟跳变/漂移的误差上界。NetLog 源码本身说明这一换算有精度限制，故不声称 UTC 边界精确到纳秒。

参考实际 [Chromium 时间实现](https://github.com/chromium/chromium/blob/8f5d36bc16f57115aeeff34baf4ad6aa964d509c/base/time/time_now_posix.cc)与 [NetLog 偏移实现](https://github.com/chromium/chromium/blob/8f5d36bc16f57115aeeff34baf4ad6aa964d509c/net/log/net_log_util.cc)。保存的 CPython 3.12 源码仅作单调时钟实现参照，不冒充已经获得采集端 Python 的精确二进制构建号。

## 3. 成员范围不是针对 9 次访问的豁免

对全部 600 次会话读取经过快照边界限定的 TCP connect/close 记录。只有确切逻辑 ID 存在唯一、顺序一致的生命周期时，才允许将其判为窗口外：

- connect 在共同窗口结束之后：9 个成员；
- connect/close 完整且 close 在共同窗口开始之前：2 个成员。

合计 11 个成员，涉及 11 次访问。没有直接用较晚 bind、局部地址别名、无包、域名相似或最近时间代替生命周期证据。缺乏明确证据的成员保守保留。

原来 SS 的早期会话依旧是实际发生过的流量；其 trace 中的 369,245 下行字节没有被改写成零。它只是被明确划在本轮共同观测窗口之外。闭合业务的完整会话捕获仍是不同的研究目标。

## 4. 新特征与数值校验

| 协议 | 访问 | W 覆盖通过 | 排除窗口外成员 | T 候选 pair | T 共同有效 pair |
|---|---:|---:|---:|---:|---:|
| SS | 120 | 120 | 2 | 5,615 | 5,608 |
| VLESS | 120 | 120 | 2 | 5,988 | 5,957 |
| Trojan | 120 | 120 | 4 | 5,956 | 5,919 |
| VMess | 120 | 120 | 2 | 6,101 | 6,082 |
| AnyTLS | 120 | 120 | 1 | 不适用 | 不适用 |
| 合计 | 600 | 600 | 11 | 23,660 | 23,566 |

W 为六维运输层数据报载荷、正载荷数据报数及访问全局方向段；T 为共同有效排他 TCP 的唯一字节、新字节事件、逐连接方向段之和及 F。AnyTLS 不伪装为排他 TCP 对；Hy2 仍不进入这套分类主队列。

全部 600 次从原始 PCAP 重提取，没有只过滤旧摘要。相对 v2，116 个 side 的 W 摘要改变。T 共同有效 pair 从 23,571 变为 23,566，是窗口重算结果，不是选择更容易的内容。

本轮仍有 11,953 个完整 UDP 数据报，来源 23,906 个 IPv4 分片；逐字节覆盖、重叠、长度、完成时刻独立复核通过。窗口边界处不跨范围补片。1,200 行 W、960 行适用 T 的独立事件复算和 CUDA 整数往返全部通过。

## 5. 如何回答同 flow/carrier 跨集合的问题

### 5.1 实际检查

沿用同一套 30 内容五折；同一内容的重复、父访问、双侧及内部连接整体随内容分组，不随机拆包或拆 flow。检查结果：

| 审核对象 | 结果 |
|---|---:|
| 共同窗口重叠 | 0 |
| 跨折登记 carrier ID 复用 | 0 |
| 原始 PCAP 文件哈希复用 | 0 |
| 跨折 TCP SYN 身份指纹冲突 | 0 |
| 跨折完整正载荷 IP 包哈希匹配 | 0 |
| 被核查的跨折复用路径哈希 | 5,065 |
| 被核查的正载荷包指纹 | 3,454,055 |

包内容检查限于这些可能跨折复用路径上的完整、非分片正载荷 IP 包；空 ACK 与非首分片不是这项内容指纹检查的对象。原分片来源另行审核，不能把上表包装成另一套解析器逐包证明所有网络现象。

### 5.2 五处未观测主动 SYN 的处理

原始隔离表仍保留 `passed_without_unresolved_TCP_epochs=false`，因为确有 5 个路径没有捕获主动 SYN；没有覆盖该历史检查或伪造握手。

后续独立证据为：

- 四个排他 carrier 有本次会话的 `created` dial/bind，其中一个只有 ACK、没有正载荷 W 贡献；
- 一个 AnyTLS carrier 是 `reused`，在这 600 份有界 trace 中未找到出生事件，实际贡献 318 个正载荷事件、398,151 字节；
- 对实际 mihomo 构建源码核查：物理 AnyTLS session 具有稳定序号，注册表保存其 OuterConnID；逻辑流复用只复制原 observation，不分配新 ID；关闭 adapter 时关闭底层 session，而不是让旧连接换新 ID 继续存在；
- 对 600 次会话的 36,098 条选定绑定，逐条核对 `outer_conn_id == carrier_id`，并核对实际 mihomo commit 与源码一致。

因此建立了**单独的、源码支持的登记实体分组资格**。这不是声称已观测 AnyTLS 的出生时刻，而是确认使用的 carrier ID 确实代表稳定物理 session，且这套选定队列中没有同 carrier 被分到不同折。

源码依据：[AnyTLS carrier 注册表](https://github.com/RakuLomis/mihomo/blob/74cfed919c03f07a21b252328fe48b72c5361215/adapter/outbound/anytls.go)、[session 序号](https://github.com/RakuLomis/mihomo/blob/74cfed919c03f07a21b252328fe48b72c5361215/transport/anytls/session/client.go)、[身份通知接口](https://github.com/RakuLomis/mihomo/blob/74cfed919c03f07a21b252328fe48b72c5361215/common/traffictrace/context.go)。保存证据在 `identity-source-evidence/`。

结论应写成：**当前分组与审计未发现跨集合共享登记 flow/carrier，且不会把同一访问拆入训练和测试；这一判断依赖已核验构建及其运行时登记语义，不是排除任意未观测实现错误的数学证明。**

## 6. 权限包及情景

直接复用旧跨业务实验的内容角色模板，不读取旧模型分数重新选内容。每协议、每表示有 5 折 × 3 个目标业务组 × 8 个轮换 = 120 个情景。

| 项目 | 数量 |
|---|---:|
| W 情景：五协议 | 600 |
| T 情景：四协议 | 480 |
| 总情景 | 1,080 |
| 每情景 C | 6 内容 / 24 访问 |
| 每情景 U | 18 内容 / 72 访问 |
| 每情景 H | 6 内容 / 24 访问 |
| 角色权限目录 | 4,320 |
| 负权限测试 | 4,320，全部通过 |

paired 包只提供 C_pre、C_post、U_pre 和训练标签。group 的 C 侧仅保留内容组标识及允许的数值坐标，post 不携带访问 ID、重复号或 T 的 post F。reference 的 U_post、scoring 的 H_post/H_labels 放在不同目录；没有导出 H_pre。

所有文件有哈希与列白名单；配对 worker 读取 U_post/H_pre/H_post、group worker 读取 labels 均会拒绝。模型数值输入仍只有 W 六维或 T 七维，IP/端口/SNI/内容名/协议名/质量标记不作为分类输入。

这里是可审计的实验访问约束，不是操作系统权限沙箱；具有整个工作区访问权的主体并非物理上无法读取 reference。正式执行器仍须冻结读依赖和阶段封存，不能把这些目录当普通整表混读。

## 7. CUDA 冒烟与测试

固定选择 `shadowsocks-f0-g0-r0`，W/T 各一个训练区情景：

- C 的 24 次真实配对拟合固定 Ridge；
- 对 72 次 U_pre 做映射与必要域解码检查；
- 用原样增广参照做六类 MLP 工程检查，输入 6/7 维，隐藏 32，ReLU，输出 6；
- CUDA 上执行 1,000 步、batch=24、Adam lr=0.001；
- 96 次训练访问各参与 250 次，训练前向、梯度及训练区推理均在 CUDA；
- 只读取 C_pre、C_post、U_pre、labels，没有读取 H 或 reference；
- 单个训练循环约 1.77 秒和 1.60 秒，不含所有准备/拟合开销，不能直接视作完整实验 ETA。

GPU：RTX 4060 Ti。36 项测试通过，包括原 FSC/HFC-W 数学回归、重组、生命周期与权限校验。记录：`outputs/extend-v3-final-tests-01.xml`。

这些是两次工程冒烟，不计作正式实验结果，也没有留出评估。

## 8. 已封存的正式实验预算

`training-preparation-01/preregistration.json` 固定：

- 六个 restricted 臂：raw、center、marginal、paired、cyclic、group；
- 三 seed：20260918、20260919、20260920；每 U 访问 8 个合成视图；
- 每分类器 1,000 步、batch=24、hidden=32，CUDA；
- restricted 分类器拟合：1,080 × 6 × 3 = **19,440**；
- 后置 reference：1,080 × 3 = **3,240**；
- 总分类器拟合预算 **22,680**，不包含生成器拟合、重放或 bootstrap。

paired−raw 与 paired−group 为预定主对比。F1_new 仍来自完整六类混淆矩阵；W 的十项比较与 T 的八项比较分属统计家族，分别给 99.5% / 99.375% 家族调整区间及普通 95% 区间。按内容簇、业务分层 bootstrap 10,000 次，保留重复与跨协议依赖。不搜索阈值或更容易子集。

**正式训练授权仍为 false。** 下一阶段还需将生产用生成、独立批量分类与评分执行器适配并冻结到当前六业务、重复 1–4、W/T 权限包；不能直接运行旧 Hy2 五类脚本或含旧重复 `[1,2,4,5]` 的旧入口。

## 9. 主要交付文件

- 特征：`extraction-03/catalog-01/{W,T}-candidate-features.parquet`；
- 窗口与范围：`prepared-windows.json`、`full-coverage.parquet`；
- 时钟：`clock-source-evidence/`、`clock-anchors-01/`；
- 原始隔离结果：`isolation-01/`；
- 无 SYN 定点证据：`isolation-followup-01/`；
- 源码支持的实体资格：`identity-source-evidence/qualification.json`；
- 权限角色：`training-preparation-01/roles.parquet`、`packages/`；
- CUDA 工程检查：`training-preparation-01/cuda-smoke.json`；
- 准备阶段封存：`training-preparation-01/preregistration.json`。

本轮没有更新 Git 远端，没有新增采集，没有将 Hy2 或 Bilibili重新加入分类，也没有覆盖 v1/v2。

**当前停点：共同窗口与训练准备已完成；等待进入冻结预算下的正式生成/训练阶段。**
