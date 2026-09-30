# N0–N2 协议栈与可观测性审计

已扫描 987 次选定会话的 manifest、上下文、proxy-info、trace 与保留的 trace journal。运行诊断共有 45 个 section，其中 45 个仅为哈希。

Mihomo 构建身份：{"fcacc8696dfd574d0faa2770c5d3151e21dd9bbc": 987}。精确 commit 能标识构建，但不能恢复 cipher/Vision/mux/obfs 的运行配置。

按命名搜索的配置/密钥/qlog 候选数：0；含 stream ID 与 offset 的 trace 候选事件：0。这是已扫描产物的可观测性结论，不声称环境中从未存在相关资料。UDP 收发事件的 seq/len 不是 SS 分块或 QUIC STREAM 字段。

当前只确认协议标签，精确 SS/VLESS 封装适配器暂停。空 network 不推断基础 TCP；不扣固定百分比或 34 字节/包。继续可独立验证的区间字节去重与字节方向段。

需要补充：采集时每个实际节点的脱敏 cipher/network/TLS/REALITY/flow/Vision/mux/obfs/plugin 配置，或可核对哈希的历史快照。不需要密码、UUID、私钥，也不要求重新采集。
