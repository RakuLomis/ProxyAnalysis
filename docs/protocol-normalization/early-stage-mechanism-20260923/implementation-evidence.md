# 历史实现与可观测性证据

以精确 commit 获取官方源码，不以最新版本替代；只读核验。所有源码 SHA256、URL 和本地缓存路径在 implementation-sources.json。

重要纠正：go.mod 中存在 sing-vmess 依赖，但本次追踪的 VLESS TCP 调用链实际进入 Mihomo 仓库内 transport/vless/vision。sing-vmess 的实现只作为依赖证据保存，不用它替代实际代码路径。

调用链：adapter/outbound/vless.go 的 TCP 分支先建立 TLS/REALITY 连接，再调用 transport/vless/conn.go；后者检查 XRV 并构造本仓库 vision.NewConn。该实现读写 padding 控制，按内部命令及状态切换 direct 路径。源码存在该路径与某条捕获实际发生该状态切换是不同证据。

因此，本轮只能从连续 TCP 字节观测到可解释的记录语法和明文 Hello 起点，不能从长度、段数 +2 或第一次 application_data 直接识别 Vision initial/relay 边界。post 中合法的记录语法也不能保证之后每条都属于同一外层加密层。

协议基础：[RFC 8446 §5](https://www.rfc-editor.org/rfc/rfc8446.html#section-5)。记录解析不等于解析受保护的内部类型或控制命令。

## 源码定位

- [adapter/outbound/vless.go:163](https://github.com/MetaCubeX/mihomo/blob/fcacc8696dfd574d0faa2770c5d3151e21dd9bbc/adapter/outbound/vless.go#L163)：`// default tcp network`。
- [adapter/outbound/vless.go:203](https://github.com/MetaCubeX/mihomo/blob/fcacc8696dfd574d0faa2770c5d3151e21dd9bbc/adapter/outbound/vless.go#L203)：`func (v *Vless) streamTLSConn`。
- [transport/vless/conn.go:202](https://github.com/MetaCubeX/mihomo/blob/fcacc8696dfd574d0faa2770c5d3151e21dd9bbc/transport/vless/conn.go#L202)：`case XRV:`。
- [transport/vless/conn.go:203](https://github.com/MetaCubeX/mihomo/blob/fcacc8696dfd574d0faa2770c5d3151e21dd9bbc/transport/vless/conn.go#L203)：`vision.NewConn`。
- [transport/vmess/tls.go:43](https://github.com/MetaCubeX/mihomo/blob/fcacc8696dfd574d0faa2770c5d3151e21dd9bbc/transport/vmess/tls.go#L43)：`GetRealityConn`。
- [transport/vless/vision/conn.go:109](https://github.com/MetaCubeX/mihomo/blob/fcacc8696dfd574d0faa2770c5d3151e21dd9bbc/transport/vless/vision/conn.go#L109)：`readLastCommand =`。
- [transport/vless/vision/conn.go:117](https://github.com/MetaCubeX/mihomo/blob/fcacc8696dfd574d0faa2770c5d3151e21dd9bbc/transport/vless/vision/conn.go#L117)：`case commandPaddingDirect:`。
- [transport/vless/vision/conn.go:144](https://github.com/MetaCubeX/mihomo/blob/fcacc8696dfd574d0faa2770c5d3151e21dd9bbc/transport/vless/vision/conn.go#L144)：`direct read start`。
- [transport/vless/vision/conn.go:222](https://github.com/MetaCubeX/mihomo/blob/fcacc8696dfd574d0faa2770c5d3151e21dd9bbc/transport/vless/vision/conn.go#L222)：`direct write start`。
- [transport/vless/vision/padding.go:17](https://github.com/MetaCubeX/mihomo/blob/fcacc8696dfd574d0faa2770c5d3151e21dd9bbc/transport/vless/vision/padding.go#L17)：`commandPaddingContinue`。
- [transport/vless/vision/padding.go:18](https://github.com/MetaCubeX/mihomo/blob/fcacc8696dfd574d0faa2770c5d3151e21dd9bbc/transport/vless/vision/padding.go#L18)：`commandPaddingEnd`。
- [transport/vless/vision/padding.go:19](https://github.com/MetaCubeX/mihomo/blob/fcacc8696dfd574d0faa2770c5d3151e21dd9bbc/transport/vless/vision/padding.go#L19)：`commandPaddingDirect`。
- [transport/vless/vision/padding.go:46](https://github.com/MetaCubeX/mihomo/blob/fcacc8696dfd574d0faa2770c5d3151e21dd9bbc/transport/vless/vision/padding.go#L46)：`func ApplyPadding`。
- [transport/vless/vision/vision.go:28](https://github.com/MetaCubeX/mihomo/blob/fcacc8696dfd574d0faa2770c5d3151e21dd9bbc/transport/vless/vision/vision.go#L28)：`func NewConn`。
- [transport/vless/vision/vision.go:30](https://github.com/MetaCubeX/mihomo/blob/fcacc8696dfd574d0faa2770c5d3151e21dd9bbc/transport/vless/vision/vision.go#L30)：`ExtendedReader:`。
- [transport/vless/vision/vision.go:45](https://github.com/MetaCubeX/mihomo/blob/fcacc8696dfd574d0faa2770c5d3151e21dd9bbc/transport/vless/vision/vision.go#L45)：`underlying.NetConn()`。
