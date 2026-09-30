# 未来脱敏配置建议（不是历史快照）

采用明确类型白名单：schema_version、capture_time、implementation_version、protocol、cipher、transport、tls/reality/vision、mux、plugin/obfs 类型、port_hopping_enabled。缺失值为 null，不能猜默认值。

禁止复制原节点对象或自由文本配置；不写 endpoint、域名、端口值/范围值、UUID、密码、密钥、原始插件参数。不将任意字典递归复制。写盘前测试禁止字段和非白名单字段均被拒绝；仅在未来采集时生成 sanitized-proxy-config-v1.json。本轮未修改采集程序，也未创建伪历史配置。
