# 基于 mihomo 实现的六协议漂移分布建模分析

日期：2026-10-03。本文是源码核对、方法分析与后续实施建议，不是新模型效果报告。本轮没有重新采集、扫描全量 PCAP、训练分类器或修改冻结实验。

## 1. 结论

可以根据实现优化现有漂移模型，但应当把目标定为**机制引导、状态条件化的观测摘要分布模型**，而不是“从协议名计算精确开销”或“生成合法协议会话”。

当前模型用 Ridge 学习六维编码漂移中心，配合留一内容整向量残差和必要可行域解码。源码提供了它目前没有显式表达的结构：一次性请求开销、分块开销、条件随机填充、传输路径状态和共享载体生命周期。最有价值的改进是把这些结构放入中心函数及残差条件中，保留现有小模型和解码器，而不是先扩大容量。

但是，源码中的内部 write、加密 chunk、逻辑 stream 和外层 TCP/QUIC 包不是同一单位；历史配置、远端实现和状态也并非都已保存。**可精确计算的封装局部量，不等于可精确计算整个访问的 pre→post 漂移。**

| 协议 | 实现中最值得建模的机制 | 建议的分布结构 | 本轮不能直接宣称的结论 |
|---|---|---|---|
| SS | cipher 家族、salt/IV、加密分块、原生 UDP/UOT/plugin 分支 | 配置条件的分块计数模型＋剩余漂移 | 未知 cipher 下的精确开销 |
| VLESS | 请求头、Vision 条件填充、方向相关 direct/非 direct 状态 | 有证据约束的状态混合＋早期长度响应 | 已找到 initial/relay 边界或精确 K |
| VMess | 安全模式、请求随机填充、chunk 长度及认证方式 | 分块/模式条件的复合开销分布 | 每个 TCP 包都有固定 VMess 开销 |
| Trojan | 一次性请求头、外层 TLS/WS/gRPC、UDP 封装 | 连接初始化＋外层传输条件残差 | 请求头长度就是观测 TCP 字节差 |
| AnyTLS | 帧、初期 padding、服务端更新 scheme、空闲会话复用 | 载体年龄/新建复用混合＋帧开销 | 每个逻辑连接都承担一次完整 TLS 握手 |
| Hy2 | 共享 QUIC、逻辑流请求、随机 padding、拥塞/恢复、端口跳跃 | 载体窗口条件过程模型 | 内层 TCP flow 与外层 UDP flow 一一对应 |

上述建议没有证明分类性能会提升。需要同权限、同输入、同预算的新对照验证。

## 2. 版本与证据范围

### 2.1 本地 Meta 与采集构建不是同一版本

`../mihomo` 工作区当前为 `main`，Go 核心位于本地 `origin/Meta`。本次使用 Git 对象读取，没有切换分支、重置文件或修改参考仓库。

| 证据 | 固定版本 | 用途 |
|---|---|---|
| 本地 `origin/Meta` | `88dcbf7f1614a67c3b36b848ee3592dfa92ada36` | 当前参考核心，提交日期 2026-09-30 |
| Extend 身份审计登记的采集构建 | `74cfed919c03f07a21b252328fe48b72c5361215` | 历史抓包的客户端实现证据 |

历史版本来自 `outputs/extend-calibration-20260930/run-01/extraction-03/identity-source-evidence/qualification.json`：600 个 manifest 的构建登记核对通过。这个核对证明身份关联所引用的构建，不证明所有节点配置或远端服务端版本都已知。

采集提交不在本地 Git 对象库中，因此通过固定提交的公开源码补齐。当前核心与历史核心的依赖不同：

| 活跃依赖 | 当前 Meta | 采集构建 |
|---|---|---|
| sing-shadowsocks2 | v0.2.8 / `706d31e8…` | v0.2.2 / `a296403d…` |
| sing-vmess | v0.2.5 / `9b7fdbf4…` | `abc39e113b82…` |
| sing-quic | `1c242664697a…` | `2a19cce83925…` |
| quic-go | v0.61.1 系列伪版本 | v0.49.1 系列伪版本 |

因此，历史数据的解释优先采用采集构建及其依赖；当前实现用于核对机制是否保留，以及提出未来建模建议。不能把新版参数或连接管理修复倒推为旧抓包的原因。其他历史数据集也不能自动继承 Extend 构建标注，应分别查登记。

### 2.2 已保存的源码证据

本轮增加可重运行的 [源码收集脚本](../eval/mihomo_protocol_audit/collect_sources.py)。证据目录为 `outputs/mihomo-protocol-audit-20261003/`，包括当前核心、采集核心、两代固定依赖源码、依赖树及 `manifest.json`。

manifest 保存固定提交、下载地址、逐文件 SHA256、读取错误和参考仓库未改变的检查结果。完整源码快照属于本地输出，不替代代码库中可追溯的收集脚本。

重要的调用路径辨别：SS 与 VMess 的活跃加密实现分别委托给 sing-shadowsocks2、sing-vmess。不能因为 mihomo 本仓库仍保留旧实现文件，就把旧文件当作当前适配器实际调用的路径。

本次没有在 `Datasets/extend` 检出命名为 sanitized 配置的文件。这只是文件名检查，不证明任意 manifest 中绝无相关字段。既有用户确认的 SS/VLESS/Hy2 配置可作为对应历史队列的证据，但不能据此补全全部 Extend 节点参数，尤其 VMess/Trojan/AnyTLS。

## 3. 必须先区分实现过程与观测过程

设 A 为入口观测，B 为出口观测，c 为部署配置，s 为连接/载体状态，η 为网络与调度因素。更准确的框架是：

\[
B=\mathcal O_{\mathrm{window,transport}}
\bigl(\mathcal M_{c,s}(\mathrm{application\ writes});\eta\bigr).
\]

源码主要限定封装过程 M；现有实验测量的是 O 后的汇聚量。入口抓包也不是 application writes 的完整登记。

- T 的 U 是观测唯一 TCP 字节，E 是正新字节事件，R 是各连接新字节方向段之和；不能直接当作应用内容量、加密块数与应用交互次数。
- W 的 W/P 是窗口内正 TCP/UDP 载荷字节/事件，重传等传输现象仍可能计入；R 是所有事件合并后的方向段。不能用一条完整字节流的加密公式直接精确预测窗口 W。
- 同一协议字节流可被 TCP 重新分段，改变 E/P 与时间线而不改变完整唯一字节总量。
- 共享 carrier 会把本次逻辑流、其他逻辑流、控制与恢复事件交织在一起；固定访问窗口还可能截断初始化和结束过程。
- 首次观测时间、完整可用时间与静态记录边界应分开。不能将整条记录压成一个时刻，再悄悄替换原 FR。

所以，协议机制对字节量的约束通常强于对包数/方向段的约束。事件数、方向段和时间应保留经验响应，不能由“增加若干头字节”直接推出固定增量。

## 4. 六协议逐项源码分析

### 4.1 Shadowsocks：先固定 cipher 家族，再谈分块

活跃路径为 `adapter/outbound/shadowsocks.go → sing-shadowsocks2.CreateMethod → DialConn/DialEarlyConn`，UDP 走 `DialPacketConn`；plugin、UOT 是额外分支。

在经典 AEAD 的采集版本中，`shadowaead/protocol.go` 规定块负载上限 16383；`internal/shadowio/writer.go` 为每块写加密长度、认证标签和加密负载。标准 16 字节标签下，每块额外量为 `2+16+16=34` 字节。首次请求还有 salt 和 SOCKS 目标地址；响应方向有自己的 salt。不同 cipher 的 salt/key 长度不同。

对完整、无 plugin 的经典 AEAD TCP 字节流，示意关系可写为：

\[
L^+_d=L^{\mathrm{app}}_d+\mathrm{salt}_d
+\mathrm{address}_d+34K_d.
\]

地址项主要属于请求方向，K 含首次请求封装形成的块。此式的条件很强：需要明确 cipher、完整边界、正确应用字节范围和实际块数。**K 取决于每次 write 的大小及实现拆分，不能简单取总字节量除以 16383，也不能用 TCP 包数代替。** Stream cipher、AEAD2022 与 UDP 不能共用这条公式。

建模建议：

1. 已确认 cipher 时固定封装家族，不让学习器重新猜盐和标签的常量。
2. 以入口长度结构、小块比例、方向段负载等作为潜在 write/chunk 数的代理变量，明确它们不是直接观测的块数。
3. 未知 cipher 时保留候选家族范围或配置混合，报告敏感性；不根据测试 post 选择最贴近的 cipher。
4. 不用 SS 的历史配置缺失解释最新留出 SS 分类失败：它只是未识别因素，不是因果证据。

现有六维摘要可先拟合“附加量随负载变化”的有限模型；要识别分块机制则需要序列或可靠的 write 计数证据。

### 4.2 VLESS＋REALITY＋Vision：不是一个固定前缀

`transport/vless/conn.go` 的请求包含 version、UUID、addons 长度及内容、command、端口、地址类型和地址。非 mux 请求头为 `22+addons长度+地址字节长度`；响应有 version、addons 长度及可选 addons。首次应用 write 可以与请求一起提交。

Vision 的独立机制更关键。采集版本的 `vision/padding.go` 规定：

- 首次携带 UUID 时，Vision 头为 21 字节；后续不重复 UUID 的头为 5 字节。
- 当内容长度 l<900 且启用 TLS 长填充时，padding 为 `[900-l,1399-l]` 的离散随机数，使内容与填充总长落在 900–1399。
- 当 l<900 而不采用长填充时，padding 为 0–255。
- l≥900 时，该函数不再附加上述随机 padding。
- 大 buffer 可能按 TLS application-data 标记或备用位置重切；这不是 TCP 包分段规则。

`vision/filter.go`、`conn.go` 根据内层 TLS 检测、TLS 版本/密码套件及 command 决定继续填充、结束填充或切换 direct 读写路径。过滤预算按内部处理调用消耗，不是“前八个抓包 TCP 包”。读写路径具有各自状态，不能统一减去两段。

REALITY 属于外层安全连接建立的一条实现路径，不应机械计算“完整 TLS 开销＋另一套完整 REALITY 开销”。当前版本还具有历史版本未必包含的其他 VLESS 功能，不能应用到原 Vision 队列。

建模建议是**配置受限的状态混合**：初始化/填充、非 direct 转发、direct 候选等。源码定义允许状态及条件，日志或独立解析定义可观测状态；不可观测时对状态边缘化并保留不确定性。

既有研究得到 E1 记录语法证据，但未得到 E2 initial/relay 语义边界。本次源码没有补上捕获中的状态证据。禁止重新按 pre/post 最相似切点伪造阶段；也不能把 TLS type 23 自动解释为 Vision 已 direct。

优先研究可检验的长度响应：小块比例/初期负载与附加量的关系；在相同捕获完整性下检验条件异方差，而非宣布 1.9KB/6KB 中心就是协议 K。

### 4.3 VMess：安全模式与 chunk 是两个显式条件

适配器使用 sing-vmess 客户端。`client.go` 按 security 与 alterId 选择分支；global padding 由选项决定。`protocol.go` 的写块负载尺度为 15000，读块尺度为 16384。不能把这些尺度当作固定 TCP MSS。

请求头含 0–15 字节随机 padding。AEAD 请求还包含认证 ID、加密长度、nonce 及相应标签；legacy/none/zero 等分支不同。正文封装有长度字段、AEAD 标签或 checksum 等模式差异；认证长度模式又会改变长度字段开销。

采集版本 `chunk_length_stream.go` 的 global padding 由哈希流取模 64 得到 0–63 字节。这是随会话密钥/种子产生的序列，不应在未验证独立性时假设每块 padding 都是独立均匀抽样。长度 masking 改变字节值，本身不增加字段长度。

因此应建模：

\[
\Delta L=H_{\mathrm{request}}(c)
+\sum_{k=1}^{K}\{h_{\mathrm{chunk}}(c)+Q_k(c)\}
+H_{\mathrm{outer}}.
\]

H_outer 仅在实际启用 TLS/WS/gRPC 等外层时出现。加密标签、长度认证、global padding 应由配置确定；不是把所有可选开销都累加。

先补全 security、alterId、network、TLS、global-padding 等脱敏证据；再做分块计数代理与状态条件残差。现有六维总量不足以识别这些分支；不能仅凭拟合一个高斜率就判断启用了 padding。

### 4.4 Trojan：局部请求头可计算，完整连接差仍需外层模型

`transport/trojan/trojan.go` 将密码 SHA224 后写入 56 字节十六进制认证值，再写 CRLF、command、SOCKS 地址及 CRLF。TCP 请求头长度为 `61+SOCKS地址长度`，即 IPv4 为 68、IPv6 为 80、域名长度 n 时为 `65+n`。

这些是**编码后请求头长度**，不是出口 TCP 唯一字节必然比入口多的量。适配器可能先建立 TLS，并支持其他传输或附加分支；TLS record、握手、结束及窗口截断另行影响观测。远端响应机制也不能只由客户端代码完整推出。

UDP 帧包含目标地址、2 字节长度、CRLF 和载荷；实现会处理超过 8192 的载荷分块。UDP 的逻辑帧不等于外层 TCP 包。

建议拆为新建物理连接成本、逻辑请求头成本、外层 record 成本及网络残差。优先在配置确认且边界完整的连接上检验“开销随新建连接数变化”；禁止把目标 IP、实际域名或端口作为业务分类捷径。即使使用地址编码长度作为机制诊断，也应单列 metadata-only 敏感性分析，不悄悄进入原主模型。

### 4.5 AnyTLS：必须以物理 session 状态为条件

客户端先建立 TLS，再在新物理连接中发送认证与初始 padding。默认 index 0 padding 为 30 字节，32 字节认证值加 2 字节 padding 长度，因此该默认初始明文总量为 64；外层 TLS 开销另计。

session 帧头为 7 字节：command 1、stream ID 4、长度 2。SYN、PSH、FIN、settings、waste 等均可产生流量；不能把所有帧视作业务负载。

采集版本默认 scheme：

```text
stop=8
0=30-30
1=100-400
2=400-500,c,500-1000,c,500-1000,c,500-1000,c,500-1000
3=9-9,500-1000
4=500-1000
5=500-1000
6=500-1000
7=500-1000
```

不等端点随机范围为左闭右开，相等端点为定值；`c` 是条件继续标记，不是普通长度。writeConn 的 session 计数控制前期 padding；它不是 wire packet 序号，也不是每个逻辑 stream 重置。waste 帧本身还有 7 字节头；某些路径会分多次底层 write。

服务端可更新 padding scheme。因此默认 scheme 是实现初值，不保证整个采集过程一直使用该配置。

`session/client.go` 会取得空闲 session，新逻辑 stream 结束后可归还并复用。**具备多 stream 帧语法，不等于这个客户端始终把所有并发业务放在同一 carrier**；其空闲复用选择必须按实际路径解释。当前版本新增的关闭复用选项也不能默认存在于采集版本。

模型条件至少区分新建/复用、载体早期/成熟、控制/业务、是否有 scheme 更新证据。AnyTLS 的初始化成本按新物理 session 计，而不是每个访问或每个内层 TCP 连接计。

历史载体年龄等变量如果只能由两侧日志恢复，可用于离线解释，不能直接当作在线 post-only 分类输入。跨折必须检查物理载体历史共享，不能只检查逻辑 flow ID。

### 4.6 Hysteria2：共享载体的复合过程，而非逐 TCP flow 加头

适配器使用 sing-quic/hysteria2 客户端，认证走 HTTP/3，实际传输走 QUIC/UDP。客户端复用活跃 QUIC connection；逻辑 TCP 连接通过 QUIC stream 打开。端口跳跃改变远端 UDP 端口，不能按外层 5-tuple 变化就必然判为新 carrier。

采集版本明确的默认随机长度范围为：认证请求/响应 `[256,2048)`，TCP 请求 `[64,512)`，TCP 响应 `[128,1024)`。响应范围属于该库实现定义，不证明远端实际服务使用同版本/策略。

逻辑请求包括 QUIC varint frame type、目标地址长度与地址、padding 长度与 padding；逻辑响应包含状态、消息与 padding。原生 UDP message 还有 session/packet/fragment 字段、地址和数据，协议分片不等于 IP 分片。

客户端还有 MTU、流控、拥塞控制、keepalive、恢复/重连与 hopping 相关参数。认证结果与带宽选项会影响拥塞选择，不能从 Hy2 协议名固定推断某一种拥塞控制。

建议以载体窗口表示以下组成：

\[
Y_w=Y_{\mathrm{init},w}+\sum_jY_{\mathrm{stream}\,j,w}
+Y_{\mathrm{datagram},w}+Y_{\mathrm{control/recovery},w}.
\]

但这首先是机制分解框架，不是从当前加密 UDP 包已经独立识别出的四个标签。无密钥时不能凭长度声称已解码所有 QUIC STREAM/ACK 帧；也不能把重传解释成 TCP 式“相同 UDP 字节去重”。

在允许的范围中，使用载体新建/延续、逻辑请求密度、入口 TCP/UDP 构成、窗口持续时间和方向负载作为候选条件。carrier ID 只用于审计/分组，不作为数值类别特征。若测试只能提供 post，训练所依赖的载体状态必须有相应 post-only 可生成定义，或在生成器中边缘化。

当前 Extend Hy2 因跨内容共享载体的资格问题未进入既有分类主队列。源码理解不会自动解除此限制；不能把其他五协议实验扩成“已完成六协议分类”。可以先做 Hy2 测量与生成分布诊断，待划分/权限契约成立后再进入业务终点。

## 5. 对现有模型的具体改法

### 5.1 保留可行域，替换没有解释的中心基准

现有版本详情见 [漂移模型构建报告](proxy-drift-model-construction.md)。保持 W/T 各自解码器、输出六量、业务分类器和内容折不变。

建议候选形式为：

\[
\widetilde B=\operatorname{Decode}_{W/T}
\left[m_c(A,S)+g_c(q(A,S))+L_c(A,S)\varepsilon;F_A\right].
\]

- m：机制引导的编码空间中心。只有支持证据充分的局部量固定；不确定项使用明确的估计或范围。
- g：小型 Ridge 学习剩余漂移，不先改成大型神经生成器。
- S：配置/状态，已知者条件化，未知者按训练侧登记的候选分布边缘化。
- L：可选的有限条件尺度；第一版可设恒等，只先验证中心改动，避免同时改多个因素。
- ε：内容交叉拟合的完整残差向量，保留跨输出耦合，不独立抽六维。

若机制先在原始字节空间描述，必须先得到完整候选摘要并编码；**不能把“34 字节”直接加在 log/asinh/logit 坐标上**。只推导出字节量时，不虚构事件数和段数的机械公式；这些输出仍由预登记的低容量部分建模。

必要可行域通过仍不保证符合真实协议、保持标签或产生收益。这一边界与旧模型完全相同。

### 5.2 两层可实施方案，避免混淆新增输入收益

**方案 A：严格不加输入。** 保持 W 六维、T 六维加 F，增加方向分开、负载规模响应和机制受限的有限基线。它最易做公平对照，但只能称为机制启发模型，不能识别 chunk 数、Vision direct 或载体年龄。

**方案 B：增加已有 pre 序列中的机制代理。** 候选包括方向载荷大小分位数、小载荷比例、pre 新字节事件/连接负载分布、初期长度摘要、可用的 pre 记录语法；载体日志变量另设审计支线。不得在没有资格时使用 donor post 的连接数、状态或窗口信息补输入。

新增输入必须同时提供给通用 Ridge 和机制模型，形成“原输入/增强输入 × 通用/机制中心”的受控比较。否则提升可能只是信息变多，不是机制结构更好。诊断 metadata 与主数值输入名单严格分开。

### 5.3 让残差反映机制，但不把小样本切碎

按配置与方向保留差异；只预登记少量状态/负载组。内容交叉拟合的每个子训练区要重新拟合中心、尺度和任何分层规则，不能先在全部训练内容拟合，再把残差称为 OOF。

每个状态样本不足时回退到部署级整向量池，不拟合大量精细状态 KDE。回退门限必须先定。padding 序列、TCP 调度与共享载体相关性不能通过独立逐块采样被默默抹去。

如果沿用 paired/group/cyclic 控制，三者必须共享参数化、输入预算和合法性设计。group 不能通过构造状态或块数恢复被禁止的同次 post 身份；不同对应控制的机制输入权限必须同样明确。

### 5.4 参数来源与测试接口

源码确定的结构常量与训练估计参数分开登记。历史配置未知时不拿测试后验选择配置；目标部署留出实验中也不能使用目标部署 pre/post 来拟合尺度、状态概率或残差池。

训练生成器可以有源部署的配置条件，但最终业务分类器不因此获得协议身份、节点地址、UUID、密码、SNI 或 domain。加入配置路由会改变威胁模型，必须单独命名。

## 6. 怎样检验解释性确实增强

最先检查的不是 F1，而是预先限定的机制预测是否成立：

| 机制候选 | 可检验现象 | 相反证据如何处理 |
|---|---|---|
| 分块开销 | 完整连接字节差随合理的块数代理变化 | 不宣称块数已识别；保留负载描述模型 |
| 条件 padding | 小负载区间的附加量/方差响应与实现分支相容 | 检查配置及捕获边界，不重选最像切点 |
| 新建成本 | 物理新建与复用样本的漂移不同 | 检查 session 定义，不能用访问号代替 |
| carrier 状态 | 年龄/请求密度解释窗口残差的一部分 | 保留不可识别范围，不自动分摊成本 |

报告内容 OOF 的误差、方向偏差、预测区间覆盖、分布距离及条件残差。覆盖的区间若仅来自经验池，应如实称经验预测区间，不默认具有有限样本校准保证。与“部署常数附加量”“现有 Ridge＋残差”比较；源码局部量验证与捕获拟合是两类证据。

只靠回归残差变小不能证明机制归因。配置与网络条件共变、远端未知、诊断队列选择等仍需保留。

后续业务评估必须保留强 post 混合 M0。最新结果中，E1 配对 M2 为 0.7248、M0 为 0.7159；E2 为 0.6097、0.6061，但两项家族校正增量区间均跨零。M2 对 group 有增益，不等于已超越充分 post 监督。详见 [最新多部署结果](business-protocol-eval-extend/formal-results.md)。

因此新方法的合理目标是解释更清楚、分布拟合更稳健，并检验是否出现业务增量；不能预设“协议化以后一定让 M2 胜出”。

## 7. 原子化实施建议与阶段门

本节是待确认的后续执行方案；除 A0 的源码收集，均未在本轮执行。

| 编号 | 单一任务 | 输出 | 验收/停止条件 |
|---|---|---|---|
| A0 | 固定两代核心和活跃依赖源码 | 收集脚本、源码 manifest、本报告 | 已执行；错误须显式登记 |
| A1 | 每队列建立脱敏实现配置证据表 | protocol-profile-registry.json | 已确认/部分确认/证据不足，不猜未知字段 |
| A2 | 建立常量、状态、调用单位登记 | mechanism-contract.md/json | 每条规则对应固定源码与配置条件 |
| A3 | 清点已有缓存可用的 pre-only 机制代理 | feature-availability-audit | 不读测试 post 建输入；缺失分支保留 |
| A4 | 用人工小输入验证长度/填充计算 | 固定单元测试与期望值 | 覆盖 SS chunk、Vision 小块、VMess 模式、Trojan 头、AnyTLS 帧、Hy2 varint；不称真实网络验证 |
| A5 | 登记唯一第一版候选与对照 | 冻结模型配置、输入权限表 | 优先只改中心；不同时改分类器/任务/预算 |
| A6 | 在训练内容内拟合并做内容 OOF | 逐协议生成误差与残差表 | 不使用外层测试结果选机制/状态/参数 |
| A7 | 独立检查生成权限与必要可行域 | access-audit、support-audit | 不满足则停止对应业务实验，不放宽门限 |
| A8 | 按原折/资源执行核心分类比较 | 与旧模型及强 post 基线的成对结果 | 保留逐协议、等权与最差成绩及既定统计家族 |
| A9 | 汇总成功、负向与未识别结果 | 完整机制与业务报告 | 不覆盖旧冻结结果，不宣称精确协议生成 |

优先次序：先完成六协议配置注册，再在合格 T 连接上检验 SS/VMess/Trojan 的局部长度机制；VLESS 仅做可观测条件响应，不恢复旧阶段搜索；AnyTLS 在 W 下注册复用条件；Hy2 先解决载体与划分资格。若协议关键配置不能闭合，可以继续范围诊断，但不能发布精确开销结论。

这一路线首先利用现有数据，不要求新 VPS 或补采。历史没有保存的 write/状态不能靠更多摘要拟合补回；必要时未来只增加非秘密机制日志用于独立验证，不与本轮历史测量混算。

## 8. 固定源码入口

以下是实际查阅的主要固定版本入口，依赖的完整提交及逐文件哈希见本地 manifest：

- [当前 Meta 核心 go.mod](https://github.com/MetaCubeX/mihomo/blob/88dcbf7f1614a67c3b36b848ee3592dfa92ada36/go.mod)
- [采集构建 go.mod](https://github.com/RakuLomis/mihomo/blob/74cfed919c03f07a21b252328fe48b72c5361215/go.mod)
- [采集 SS 适配器](https://github.com/RakuLomis/mihomo/blob/74cfed919c03f07a21b252328fe48b72c5361215/adapter/outbound/shadowsocks.go)；[采集 AEAD writer](https://github.com/MetaCubeX/sing-shadowsocks2/blob/a296403d51aa42afa313030f25fe43181883d239/internal/shadowio/writer.go)
- [采集 VLESS 请求](https://github.com/RakuLomis/mihomo/blob/74cfed919c03f07a21b252328fe48b72c5361215/transport/vless/conn.go)；[Vision padding](https://github.com/RakuLomis/mihomo/blob/74cfed919c03f07a21b252328fe48b72c5361215/transport/vless/vision/padding.go)；[Vision 状态路径](https://github.com/RakuLomis/mihomo/blob/74cfed919c03f07a21b252328fe48b72c5361215/transport/vless/vision/conn.go)
- [采集 VMess client](https://github.com/MetaCubeX/sing-vmess/blob/abc39e113b82f7ab2ab6450d86f11e2731e13795/client.go)；[chunk 长度流](https://github.com/MetaCubeX/sing-vmess/blob/abc39e113b82f7ab2ab6450d86f11e2731e13795/chunk_length_stream.go)
- [采集 Trojan 封装](https://github.com/RakuLomis/mihomo/blob/74cfed919c03f07a21b252328fe48b72c5361215/transport/trojan/trojan.go)
- [采集 AnyTLS session](https://github.com/RakuLomis/mihomo/blob/74cfed919c03f07a21b252328fe48b72c5361215/transport/anytls/session/session.go)；[padding scheme](https://github.com/RakuLomis/mihomo/blob/74cfed919c03f07a21b252328fe48b72c5361215/transport/anytls/padding/padding.go)
- [采集 Hy2 client](https://github.com/MetaCubeX/sing-quic/blob/2a19cce83925b7b35ded9fc0f38ecd578e16b744/hysteria2/client.go)；[请求/UDP 帧](https://github.com/MetaCubeX/sing-quic/blob/2a19cce83925b7b35ded9fc0f38ecd578e16b744/hysteria2/internal/protocol/proxy.go)；[随机填充范围](https://github.com/MetaCubeX/sing-quic/blob/2a19cce83925b7b35ded9fc0f38ecd578e16b744/hysteria2/internal/protocol/padding.go)

## 9. 最终判断

当前“配对 Ridge＋残差”可以升级为“实现机制约束的条件漂移分布”，但要有三个诚实边界：**机制存在不等于捕获中可定位；必要摘要合法不等于协议合法；更可解释不等于业务分类一定更好。**

最值得做的是一次有界改动：固定真实配置和源码，把可证实的开销/状态结构加入中心，保留小型剩余回归、OOF 整向量残差与既有可行域；然后在原任务及强基线下检验。不能用协议知识绕过 Hy2 队列资格，也不应把 SS/Vision 的未知部分重新包装成精确常数。
