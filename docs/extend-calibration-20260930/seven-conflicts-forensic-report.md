# 七次主文档关联冲突：定点取证报告

日期：2026-09-30。状态：七例独立证据链全部得到支持；另已完成固定600访问的统一主文档核对。尚未应用关联修正，未训练。

## 1. 结论

七次浏览器返回 HTTP 200、但索引指向 failed_before_socket 的矛盾均已得到具体解释：**导出的 connection-index 将成功 HTTP/2 会话关联到另一次失败的 TCP 尝试，而不是它实际依赖的成功 socket。**

这不是靠相同域名、近邻时间或较大流量猜测得到的替换。七例均有以下链路：

```text
目标 URL 的 HTTP/2 SEND_HEADERS
    → 同 stream 的 HTTP/2 RECV_HEADERS :status: 200
    → 该 HTTP/2 会话唯一 HTTP2_SESSION_INITIALIZED.source_dependency
    → 指向的 socket 唯一成功 TCP_CONNECT END
    → 成功 socket 的真实本地/远端 tuple
    → flow-index 中唯一相同 tuple 的逻辑 flow
    → verified barrier 内的 tcp_proxy_dial 及 post 路径
    → 原始 TUN/physical PCAP 中实际包
```

上述结论针对七例导出结果；没有检查 TrafficTracer 生成索引的源码，不能进一步断言具体是哪段生成算法、某个版本提交或时间窗口规则造成错误。也不能据七例通过推断其余所有关联正确。

## 2. 已落实的用户决定

依据用户确认“是，按照推荐口径继续”：

- 六业务、重复 1–4 保持不变，第五重复不替补。
- 六次 NAVIGATION_TIMEOUT_RECOVERED 且 load_event_observed=true、HTTP 200 的访问，接受其业务标签。
- 接受仅作用于标签；两次同时具有路由关联问题的 AnyTLS 访问没有因此自动放行。
- Hy2 保留测量，不启动同一持久 carrier 下的分类分支。
- 不删除访问、不替换为其他 attempt、不改写 Datasets 中的任何文件。

决定保存在 `outputs/extend-calibration-20260930/run-01/forensic-01/user-decisions.json`，六次标签接受保存在同目录 `accepted-navigation-labels.parquet`。旧 G1 台账保持不变。

## 3. 七例证据概览

包数和字节量均是对应 tuple 在该份捕获中的观测，不是业务对象解密结果；包含传输重传。

| 协议 | 内容 | 旧 tuple 入口包 | 旧 tuple 下行 payload | 成功 tuple 入口包 | 成功 tuple 下行 payload（字节） | 对应外层包 | 外层关系 |
|---|---|---:|---:|---:|---:|---:|---|
| AnyTLS | YouTube watercolor 搜索 | 15 | 0 | 1,900 | 2,669,239 | 3,580 | shared |
| Trojan | MDN HTTP Caching | 15 | 0 | 401 | 514,098 | 641 | exclusive |
| SS | Wikipedia TLS | 14 | 0 | 536 | 601,374 | 784 | exclusive |
| AnyTLS | Wikipedia TLS | 14 | 0 | 562 | 601,372 | 779 | shared |
| VMess | Wikipedia HTTP | 14 | 0 | 471 | 483,305 | 658 | exclusive |
| AnyTLS | Wikipedia HTTP | 14 | 0 | 452 | 461,174 | 8,822 | shared |
| AnyTLS | Bing network traffic analysis 搜索 | 14 | 0 | 277 | 244,641 | 451 | shared |

每例成功 tuple 都只匹配一个 flow-index 逻辑 flow，并都有一条匹配外层路径的 tcp_proxy_dial 证据；对应入口流的包时间范围覆盖目标 HTTP/2 200 响应时刻。

AnyTLS 外层包属于共享 carrier，可能包含其他逻辑成员。因此本表不能将外层包总量解释为该主文档专属流量，也不能以此创建排他 TCP pair。

## 4. NetLog 源 ID 的直接关系

| 协议/内容 | HTTP/2 source ID | 直接依赖的 socket source ID |
|---|---:|---:|
| AnyTLS / YouTube 搜索 | 295 | 270 |
| Trojan / MDN Caching | 323 | 319 |
| SS / Wikipedia TLS | 268 | 252 |
| AnyTLS / Wikipedia TLS | 297 | 289 |
| VMess / Wikipedia HTTP | 327 | 298 |
| AnyTLS / Wikipedia HTTP | 261 | 198 |
| AnyTLS / Bing 搜索 | 281 | 228 |

这些 ID 都只在各自 NetLog 内解释，不跨 Session 合并。取证代码没有遍历同域名候选并按最高分选择，也没有把同一 source 内多个 socket 模糊合并。

NetLog 时间使用其 timeTickOffset 进行整数纳秒换算。TCP_CONNECT END 与入口首包的差约 -1.45 至 +2.64 ms；没有据此拟合新时钟偏移或选择“最佳”连接。NetLog 毫秒量化和捕获时钟之间的小差值保留，不强行改为零。

浏览器 NetLog 的 HTTP/2 proxy=[direct://] 描述的是浏览器未配置显式 HTTP 代理，**不能**据此判定 TUN 之后的流量绕过代理。代理路由证据来自独立 flow-index/trace；七例新定位的逻辑 flow 均记录 egress_outcome=proxy。

## 5. 读取范围与证据完整性

- 只处理七个选中 Session；没有重新扫描整个约 178 GB 数据导出目录。
- 对七份 NetLog、七份 trace、七份 TUN PCAP、七份 physical PCAP，以及对应索引和 summary 保存了文件 SHA256。
- 共验证 14 份原始 PCAP；此结论不代表整个新数据集 PCAP 已通过审核。
- trace 仅接受 verified cutoff 之前和明确 causal_tail_event_seqs 指定的事件。
- 原始包使用项目已有 PCAPNG reader 和 L2/L3/L4 字段解码器；未依赖 Wireshark 内置派生特征。
- 输出只保存 source/connection/carrier 身份和 tuple 哈希，不导出节点凭据、完整 HTTP headers 或明文 endpoint。
- 没有实际应用新的关联，也没有重新打包 C/U/H、生成合成样本或训练分类器。

12 项相关单元测试通过，其中包含错误 URL、不同 HTTP/2 stream、多个成功 socket、失败连接、非法路径、错误 attempt 和越过 trace 截点等负例。测试记录：`outputs/extend-tests-forensic-01.xml`。

## 6. 当前队列状态

四重复六业务的五协议候选仍为 600 次。

六次恢复导航的标签已接受；因此，标签接受后的元数据无保留项数量为 593/600，剩余七次是本报告的关联项。七例修正均有独立证据支持，但仍保存为 **proposed-lineage-overlay.parquet，applied=false**。

如果应用七例可追溯本地关联侧表，理论上这 600 次可继续进入下一轮原始事件与特征资格审核。但这不等于：

- 已经认证全部 600 次连接映射正确；
- 已经排除所有 TCP/carrier 跨集合问题；
- 全部实际捕获窗口、覆盖和必要特征约束通过；
- AnyTLS 可以按排他连接解释；
- 已获得新的分类收益。

既有 `cohort-after-label-acceptance.parquet` 只更新标签相关 reasons/metadata_candidate，原轨道状态仍是先前 gate 的保守保留，training_eligible 始终 false。后续新 gate 应重新计算 W/T 状态，不能把旧标志当最终授权。

## 7. 建议的下一步

### 7.1 600次主文档统一核对：已完成

七例取证后，以相同规则检查了五协议600次固定候选的全部成功目标主文档。每次访问恰有一条符合条件的成功主文档，共600行；没有挑选最有利的重复或连接。

| 协议 | 直接依赖与原索引一致 | 直接依赖指向不同成功socket | 无法解析/路由协议不符 |
|---|---:|---:|---:|
| SS | 119 | 1 | 0 |
| VLESS | 120 | 0 | 0 |
| Trojan | 119 | 1 | 0 |
| VMess | 119 | 1 | 0 |
| AnyTLS | 116 | 4 | 0 |
| 合计 | 593 | 7 | 0 |

七次不同socket恰好就是前述七例，没有新增同类主文档问题。600次依赖定位出的逻辑flow都记录为本次选定代理协议，且均为唯一tuple匹配。统一检查读取并保存了这600份NetLog及相应索引/summary的哈希；除了七例外，没有对其余593份访问逐一重复原始PCAP取证。

这缩小了修正范围，但不是所有子资源请求、所有逻辑成员或原包级生命周期的全量认证。

结果目录：`outputs/extend-calibration-20260930/run-01/primary-lineage-01/`，包含 `primary-document-lineage.parquet`、`counts.parquet`、`source-hashes.json` 和封存状态。入口为 `eval/extend_calibration/lineage_audit.py`。

### 7.2 下一阶段

不建议现在立刻训练。七例已证明现有高置信度 matched 并不保证 socket lineage 正确，下一阶段应：

1. 将本报告的七例定位结果登记为可追溯的本地关联修正侧表；保留原 connection-index、旧关联和全部依据，绝不覆盖原数据。
2. 使用本节已完成的600次核对作为主文档审核依据；不要把它外推为全部子资源的关联已正确。
3. 接受本地关联侧表后继续 E07–E13：W 多 carrier 集合提取、T 排他 TCP 提取、原始包与跨集合审计、预算与权限冻结。
4. 正式训练仍等待 G2 通过；Hy2 按已确认口径只继续测量。

本次没有修改 TrafficTracer 本体。若需要从上游修复导出逻辑，应作为另一项代码任务，依据本报告的复现样本定位；不能在没有检查源码前声称已修复 TrafficTracer。

## 8. 复现和文件

入口：`eval/extend_calibration/forensic.py`。

共用取证逻辑：`src/proxy_analysis/extend_calibration/forensic.py`。

数据结果：`outputs/extend-calibration-20260930/run-01/forensic-01/`：

- `user-decisions.json`、`accepted-navigation-labels.parquet`：已授权的口径和标签接受；
- `findings.parquet`：七例证据量和结论；
- `proposed-lineage-overlay.parquet`：尚未应用的局部关联修正建议；
- 每 Session 的 `*-trace.json`、`*-packets.json`：经过范围约束的取证记录；
- `source-hashes.json`、`status.json`：输入/输出指纹与阶段封存；
- `cohort-after-label-acceptance.parquet`：标签接受后的资格候选台账。

已完成输出拒绝覆盖；后续版本应使用新输出目录，而不是重写本次记录。
