# Extend 迁移 v2：严格分片重组、W 并集与捕获边界审核

日期：2026-09-30。版本目录：`outputs/extend-calibration-20260930/run-01/extraction-02/`。

## 1. 当前结论

按用户确认实施了独立 v2，没有修改 extraction-01、原始数据、标签、内容折、重复预算或旧实验结果。

**W 覆盖检查由 559/600 提升为 591/600；剩余 9 次没有豁免。** 这不是分类性能提升，尚未拟合任何新模型。

| 协议 | 访问 | v1 W 通过 | v2 W 通过 | 剩余待审 | T 共同有效 pair（未变） |
|---|---:|---:|---:|---:|---:|
| SS | 120 | 100 | 118 | 2 | 5,609 |
| VLESS | 120 | 114 | 118 | 2 | 5,958 |
| Trojan | 120 | 111 | 118 | 2 | 5,921 |
| VMess | 120 | 115 | 118 | 2 | 6,083 |
| AnyTLS | 120 | 119 | 119 | 1 | 不适用 |
| 合计 | 600 | 559 | 591 | 9 | 23,571 |

Hy2 仍仅保留既定测量分支，不进入这 600 次分类候选。591 次也没有另立为新的训练队列。

## 2. 本轮完成的适配

### 2.1 严格 IPv4 分片重组

在运输层统计前完成 IPv4 重组，重组单位限定于当前会话/捕获接口/方向/协议/IP ID 的完整数据报生命周期：

- 必须先观测到 offset=0；非零片先到时保守 hold，不向后猜测归属；
- 无跨访问、跨窗口拼接，无缺口补零；
- 末尾长度唯一、覆盖连续，重叠字节必须相等；
- 未完成前 IP ID 冲突、截断、长度矛盾、运输层长度不一致均 hold；
- 一个完整运输层数据报计一个 P，事件时间为全部片可用时刻；
- 保存每个数据报的全部来源原包序号、首次/完整可用时刻及载荷长度；
- IPv6 分片暂不支持，若出现则显式 hold。本批通过的分片都是 IPv4/UDP，并不是完整 IPv6 重组实现。

18 次 SS 访问中，23,906 个分片组成 11,953 个完整 UDP 数据报。该批没有重组失败；独立按原始分片逐字节复核，覆盖、重叠一致性、长度和完成时刻全部通过。

这只保证所登记的重组条件，不证明网络中没有丢包或捕获前后没有未观测数据。P 现在明确表示运输层数据报观测次数，不再可不加说明地称为物理抓包数。

### 2.2 W 并集与 T 归属分开

当同一原始包映射到多个已选 carrier，但范围与方向完全一致时，W 只按原包计一次，保留 `union:` 来源标记。方向不一致仍 hold。

14 次多重登记访问的 W 因此恢复，不需要假定每个包属于哪一个 TCP epoch。**T 仍不能套用这项规则**：有归属歧义的逐连接观测没有通过并集规则强行分配，T 的全部数值与 v1 完全一致。

### 2.3 连接生命周期诊断

对 14 次访问的 28 组复用外层路径读取实际 TCP 包：

- 27 组具有两个 SYN 起始片段；1 组具有三个；
- 合计 57 个片段均以主动 SYN 开始；
- 56 个片段的观测时段内包含恰好一个对应 carrier 的有界 bind 记录。

这些结果支持“端口/五元组复用”和“永久连接身份”必须区分，但不是逐包归属已经全部验证。尤其存在登记两个 carrier、观察三个 SYN 片段的情况；重复 SYN、重连、延迟旧包、序号与 ACK 兼容性仍需联合判断。

当前 `epochs.json` 是定位台账，未被直接用于 T 重新归属，也未用于证明所有跨内容物理连接隔离。这保留了范围边界，避免把时间包含关系当作连接身份证明。

## 3. 剩余 9 次：已定位到捕获范围问题，但未改资格规则

原始 `capture-context.json` 确实保存了 tun/physical 的 `ready` 与 `stopped`，使用 `monotonic_seconds`；trace 使用 UTC。为定位，计算了通过 NetLog `timeTickOffset` 映射的候选 UTC 边界。

**这一步仍是条件性时钟映射。** 本地没有采集器实现可直接核实两处 monotonic 是否严格同源；CDP 请求时刻与该时间量级相容，但没有保存可直接形成 wall/monotonic 配对的 wallTime 锚点。本轮未因此自动发布捕获边界豁免。

另外 `ready` 是采集就绪通知，不必等于抓包器收到第一个包的瞬间。本次候选映射下，最早包可能在 ready 前约 39.49 ms；因此不能把 ready 直接改名为“真实捕获开始时刻”。

### 3.1 8 次偏晚登记

7 次双侧成员无包的访问，以及 1 次 AnyTLS 入口成员无包的访问，对应的精确逻辑成员 bind 均位于候选映射后的 stopped 之后。差值约 175.94–1,546.68 ms，按侧和会话详见 `missing-and-binding.json`。

AnyTLS 的判断使用确切 logical member 的 bind，而不是共享 carrier 的最早事件；不能因该 carrier 在窗口里其他成员有包，就说这个缺失成员也被捕获。

这是支持捕获停止边界解释的证据，仍不能替代时钟来源和成员纳入规则的统一审核。

### 3.2 1 次较早的 SS 会话

会话：`23e6e967-e6f6-48d9-af08-b3b7f41d4613`。

其外层绑定位于候选 physical ready 前约 1,508.75 ms；有完整 `tcp_connect → tcp_proxy_dial → logical_carrier_bind → tcp_close` 链。关闭时刻位于候选 ready 前约 381.62 ms。

trace 的关闭计数为上行 2,595 字节、下行 369,245 字节，持续约 1,222 ms。**这是 trace 计数，不是本次 PCAP 提取出的 W/U。** PCAP 中该 pre pair 没有正载荷、对应 post tuple 没有包，不能把真实传输写成零流量。

因此该例不能跟后 8 次一并解释为结束后的背景拨号，也不能用“没有包所以不重要”排除。它说明 manifest 时间段、代理 trace 观测范围与双侧稳定捕获区间不是同一个范围。

## 4. 验证与复用

- 600 次全部完成 v2：41 次受影响访问重提取；559 次未受影响访问先重算原始输入哈希，再继承数值不变的事件及摘要，保存 inheritance 记录。
- W 只有 32 个 side 摘要发生变化，均为 18 次分片及 14 次并集修复的 post；其余摘要不变。
- T 七维全部与 v1 一致，总计 23,571 对共同有效连接。
- 1,200 行 W、960 行适用 T 独立事件复算通过。
- 1,200 行 W、960 行 T 在 RTX 4060 Ti CUDA 上整数编解码往返精确一致。
- 分片来源额外做了原始 PCAP 逐字节复核，而不是只验证派生事件表；普通原始运输层解析器没有另写第二套全量实现。
- 24 项相关单元测试通过，报告在 `outputs/extend-tests-v2-final-01.xml`。
- CUDA 使用仅限无拟合的代数验证，不是 E12 训练冒烟，不产生模型或预测分数。

## 5. 新产物

以下路径相对 `outputs/extend-calibration-20260930/run-01/extraction-02/`：

| 路径 | 内容 |
|---|---|
| `contract.json` | 新规则、代码与输入指纹、禁止训练声明 |
| `full-W-features.parquet` / `full-T-features.parquet` | 底层摘要；不能绕过资格表使用 |
| `full-coverage.parquet` / `full-gate.json` | 600 次覆盖、9 次 hold 与阶段门 |
| `catalog-01/W-candidate-features.parquet` | 1,200 行带质量标记的 W 候选 |
| `catalog-01/T-candidate-features.parquet` | 960 行适用 T 候选，无 AnyTLS 零占位 |
| `sessions/<session>/*-reassembly.json` | 重组计数与逐数据报来源 |
| `sessions/<session>/inheritance.json` | 未受影响访问的原始输入重校验与继承说明 |
| `verification-01/` | 事件复算、分片源字节重放、W 变化、CUDA 验证 |
| `epoch-capture-audit-01/epochs.json` | 57 个 SYN 起始片段与 bind 包含关系 |
| `epoch-capture-audit-01/clock-candidates.json` | 明示条件性的时钟映射、就绪/停止边界 |
| `epoch-capture-audit-01/logical-boundary-evidence.json` | 9 次待审访问的 31 条有界逻辑生命周期事件 |

候选文件全部 `training_eligible=false`。尚无 restricted/group/reference/scoring 权限包。

可复用脚本：

```powershell
& D:/Tools/Anaconda/envs/Pytorch312/python.exe eval/extend_calibration/extract_v2.py --pilot
& D:/Tools/Anaconda/envs/Pytorch312/python.exe eval/extend_calibration/extract_v2.py --workers 4
& D:/Tools/Anaconda/envs/Pytorch312/python.exe eval/extend_calibration/audit_epochs_v2.py
& D:/Tools/Anaconda/envs/Pytorch312/python.exe eval/extend_calibration/audit_boundary_events_v2.py
& D:/Tools/Anaconda/envs/Pytorch312/python.exe eval/extend_calibration/verify_v2.py
```

提取支持哈希校验后的恢复；已经封存的审计/验证目录拒绝覆盖。要重新运行一份完整审计应显式新建版本，不能删除旧证据或覆盖输出后称原实验未变。

## 6. 下一关键决策：是否改为共同稳定采集窗口

不建议删除 9 次访问、用重复 5 替补，或将 591 次定义成更容易的新主队列。也不建议以旧 manifest 访问完整性名义直接放行这 9 次。

推荐将下一版本的研究对象明确为：

> 在双侧均已就绪、且任一侧尚未停止的共同稳定采集区间内，已登记代理成员与 carrier 并集的流量观测。

若获确认，需要按以下顺序推进，而不是立即解锁训练：

1. **时钟门。** 优先核实采集器 clock 实现或明确保存的时钟校准证据。可验证之前保留条件性，不用模型效果选择 offset，也不以最后一个包替代 stopped。
2. **固定统一窗口。** 时钟门通过后，可采用 `[max(ready_pre, ready_post), min(stopped_pre, stopped_post))`；称为共同稳定采集区间，不声称这是原始会话完整生命周期。
3. **统一成员生命周期规则。** 对所有 600 次访问计算 logical connect/close 与共同区间的交集，不能只对这 9 次作例外。对在窗口前开始但仍持续的连接/共享 carrier，不能仅因起点较早而排除；对缺乏结束证据或其他模糊成员继续 hold。
4. **统一重算。** 在独立 v3 重算 W/T 及跨边界分片来源，不仅删除 9 条原因标记。不得把跨窗口片段拼出完整数据报后藏掉边界不完整。
5. **完整隔离门。** 连接生命周期与 carrier/内容交叉、跨文件原包审核完成后，才建立 C/U/H 权限包与 CUDA 训练冒烟。

这项选择会改变观测总体：论文结论应限定于共同捕获窗口的代理摘要，而非整个 manifest 会话全部业务流量。未来若要研究完整会话捕获，应该另列任务，不能用此规则证明当前已完整抓到 369 KB 的早期 SS 流量。

**本轮停点：v2 测量适配已完成到上述阶段；需要确认是否接受这一统一研究范围变更。当前未获任何新的训练结果。**
