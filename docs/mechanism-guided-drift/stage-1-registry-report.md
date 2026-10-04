# 六协议配置证据与第一阶段结果

日期：2026-10-04。本报告完成三步计划的第一步，不包含机制回归、生成采样或业务分类训练。核心结论是：Extend 已保存逐会话协议栈快照，不能把旧三协议队列的配置套用到它。字段确认指客户端适配器选项层，非完整协商或远端内部状态确认。

## 配置发现与历史口径修正

| 协议 | 选中会话证据 | 主分类成员 | 配置结论 |
|---|---:|---:|---|
| anytls | 329 | 120 | TLS carrier；idle 选项0/0；min idle0；内部默认规范化30s |
| hysteria2 | 329 | 0 | QUIC＋Salamander；hopping false；UDP MTU option1197 |
| shadowsocks | 329 | 120 | AES-256-GCM；无 plugin/smux；UDP enabled；UOT false |
| trojan | 329 | 120 | TCP＋TLS；REALITY false；附加 SS false；smux false |
| vless | 329 | 120 | TCP＋TLS；REALITY false；Vision false；flow none；XUDP；smux false |
| vmess | 329 | 120 | WS＋TLS；cipher auto；global padding false；authenticated length false；smux false |

上表来源为选中会话的 `raw/proxy-semantics.json`，与已有部署缓存逐字段核对。SS 的 cipher 在 Extend 不是未知；VLESS 也不是历史 REALITY/Vision 部署；Hy2 则启用了 Salamander 而没有开启端口跳跃。上述差异是跨数据队列的部署变化，不是同一部署内互相冲突的证据。

源码收集报告中对旧 SS cipher、旧 VLESS Vision 与旧 Hy2 hopping 的讨论依然适用于相应历史队列；不能用于 Extend 的机制规则选择。旧报告没有发现名为 sanitized 配置的文件，并不代表不存在原生逐会话栈记录。

## 覆盖与一致性

已登记 Extend 选中会话 1974 次，全部有可读协议栈证据。 此外清点到 1996 个协议栈文件，另外22个未选中文件只列索引，不补进旧主队列。

最新五部署 W 主队列 600 次访问全部获得原始记录核验，每部署120次；成员、折与旧分类结果未改变。选中会话与主队列是不同范围，不能把前者数量写成模型训练量。全文件计数也不代表同等数量的独立选中访问。

本轮核对了 start/end 白名单字段、协议、客户端构建、会话身份和既有部署缓存。工程审计通过。2个非主队列会话没有旧部署缓存，但有本次核验的原始栈记录；保留为原始来源登记，不冒称旧缓存核对通过。详细统计及逐会话缺失/冲突见本地注册表。未知也有登记，不因缺少字段而删会话。

首次工程运行把源码协议名ss与实验台账shadowsocks误判为不一致，也把两条没有旧缓存的非主会话误判为缓存冲突。已用明确名称映射及“缓存不可用”状态修复，并增加名称映射测试；没有改数据、访问资格或阶段门。修复记录见本目录engineering-repair.md。

## effective 字段的可解释边界

固定采集提交的 `adapter/semantics.go` 从配置映射及解析后的 option 构造 configured/effective 字段；`component/proxysemantics/contract.go` 明确将 negotiated/observed 层初始化为 unknown。记录来自采集进程，但不等于每个连接已经附上协商或内部 write 证据。

AnyTLS 的 effective idle0是 option 数值；下游 `session.NewClient` 会将小于等于5秒的值规范化为30秒。本轮保留原值，另写 source-derived 30秒，不能称连接定时器实测。VMess 的 auto 尚未记录最终安全算法，alterId 也未进入此版本栈 schema；不能给出精确 AEAD 请求开销。AnyTLS 动态 padding scheme、Hy2 协商拥塞/运行带宽与远端服务端版本仍不确定。

全部 profile 整体仍标为部分确认，因为客户端 option 确认不等于网络全过程参数完整。未保存实际地址长度、内部 chunk/write 数量、每次 TLS/WS record 数量或 QUIC 明文，不能发布精确访问 K。

## 源码规则资格

- SS 可注册 AES-256-GCM 的32字节 salt与每块34字节局部规则；实际块数未观测，不能用包数替代。
- Extend VLESS 注册 TCP/TLS 与请求封装；Vision padding 分支明确不适用，下一步不做 Vision 阶段切点诊断。
- VMess 必须包含 WS/TLS 外层；global padding/authenticated length 分支不启用，auto及alterId缺口保留。
- Trojan 注册一次性请求头与外层 TLS，目标地址不进入主模型。
- AnyTLS 注册帧、物理 session复用与初始 scheme范围；动态更新和载体阶段尚需现有日志资格检查。
- Hy2 注册 QUIC共享载体与Salamander每外层datagram的8字节salt；不再套用旧“无混淆＋跳跃”描述，且不解除现有分类资格限制。

每条规则在 `mechanism-contract.json` 绑定固定源码文件、行号、哈希、调用单位和配置前提。局部规则精确不等于捕获总开销精确。人工输入验证属于下一阶段，未在本轮提前执行。

## 输出与复现

Python入口为 [registry.py](../../eval/mechanism_guided_drift/registry.py)，脱敏测试为 [test_safe_profile.py](../../eval/mechanism_guided_drift/test_safe_profile.py)。先运行固定补充源码收集，再运行注册与测试：

```powershell
conda run -n Pytorch312 python eval/mechanism_guided_drift/collect_instrumentation.py
conda run -n Pytorch312 python -m unittest discover -s eval/mechanism_guided_drift -p "test_*.py"
conda run -n Pytorch312 python eval/mechanism_guided_drift/registry.py
```

本地结果在 `outputs/mechanism-guided-drift-20261003/registry/`：baseline-manifest、evidence-inventory、profile_schema、implementation-registry、protocol-profile-registry、session-profile-ledger、mechanism-contract、registry-audit。原始配置/endpoint/凭据未复制，原始PCAP未打开；旧输入哈希复核通过，未修改冻结实验。

## 第一确认节点

建议接受上述 Extend 队列专属配置表进入 P2，并修正诊断范围：SS重点验证经典AEAD负载关系；VLESS改为非Vision TCP/TLS；VMess明确WS/TLS及未解析安全模式；AnyTLS区分option与库状态；Hy2按Salamander共享载体只做测量诊断。缺失参数保持未知，不补默认运行状态、不加入分类器身份特征。

本轮在G1停下。确认后才能执行机制诊断；新中心候选和CUDA正式训练仍须等待G2。
