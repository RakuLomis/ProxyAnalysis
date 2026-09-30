# 统计口径与使用边界

本报告是固定采集的描述性统计，不训练分类器，不开展新的特征筛选或显著性搜索。所有指标由项目自己的数据包/状态实现计算，未调用 Wireshark 内置统计。

## 样本与观察范围

- 全量 registry 含 1,002 次存储尝试；仅 987 次选定访问参与统计。0914 broad、0914 repeat、0916 三个批次分别报告。
- 同一条目按批次、目标索引、规范化资源标识；活动证据逐访问保留，不把异常访问改成新条目。查询参数保留，仅删除既有 Bing 重定向跟踪参数。
- exclusive_page：已有索引中排他、外侧实体未复用的 TCP→TCP 配对集合。不是网页所有流量，更不是每个应用资源都已解密归属。
- carrier_context_envelope：Hy2 相关逻辑连接的 pre 包络内截取共享 UDP 载体；full 是载体全范围敏感性。可能含共享背景流量，不能当作一对一逻辑流。
- direct_pre_only：有明确 DIRECT 路由的 pre 观测；不制造 post，不赋予代理变换。主文档 DIRECT 而存在辅助代理连接时，辅助连接仍展示但不纳入主请求代理汇总。
- 主请求 proxy 仅说明主请求路由，不保证页面所有资源均走代理。三种部署路由/传输范围差异是实测条件的一部分。

## 定义

- 方向由索引的发起端定义。长度用传输层载荷和 IP 总长；大于 MTU 的观测包保留并标记 offload 嫌疑，不等价于线上物理分包。
- IAT 在原连接内按时间戳＋序号排序后计算，单位 µs。原始时间回退计数保留；不跨连接拼接 IAT、FR 或 transition。
- 原 TCP FR=非空方向段数；总 FR=非空实体数＋总 switches。分别给出 runs/N 和 switches/(N−非空实体数)。Hy2 中相似方向段统计单独命名 analog，不称原 TCP FR。
- observed burst 包括纯 ACK 等空载荷包，因而不等于 FR。另给 nonempty 与 exclude_full_retransmission 敏感性，后者不等价于完整去重传字节。
- 分布距离：JS 是固定分箱的 base-2 散度（非平方根距离）；KS 是原始样本经验 CDF 最大差；Wasserstein 长度用 bytes、IAT 用 log1p(µs)。不解释依赖包样本的 KS p 值。
- 累积曲线各侧独立归一化时间/字节，101 点；其接近不代表绝对延迟或字节量接近。直方图和曲线保存在侧特征表。
- RTT 为现有 TCP ACK 匹配估计，不保证端到端网络 RTT；窗口为 raw 字段未应用缩放；无样本不补零。active/idle 是连接内 gap 阈值汇总，不是网页真实墙钟活跃时长。
- 并发是已观测连接生命周期包络的最大重叠（端点相等时闭区间处理），不是浏览器 HTTP 请求并发。载体扇出是索引映射比例，不是 QUIC 内部瞬时并发。

## 汇总规则

- 每次访问先算 pre/post 与严格 ln(post/pre)，再对重复汇总。零值保留，log-ratio 无定义时记录原因，不添加 epsilon。比例/概率/熵使用 post−pre。
- 重复报告中位数、min/max、Q25/Q75、IQR、未缩放 MAD；单次 broad 不提供重复离散性。4/5 次重复主要作描述，不估计高精度区间。
- 总览先取各条目重复中位数，再按条目等权取中位数。增长率 exp(中位 log-ratio)−1 不等于先混合所有包或字节求比。
- 跨协议相同 repetition 编号不是同时观测的因果配对；比较各自访问分布。SS/VLESS 同口径比较与 Hy2 异质范围比较明确区分。
- 跨批次仅列确切资源和兼容活动候选；采集时长、路由、实际内容交付未严格匹配，因此只作批次参考，不声称时间不变性或纯协议因果效应。
- SNI/域名/IP 是元数据，不用于这些统计主指标；SNI 不能单独确认 CDN 厂商。本轮不新增 TLS 指纹或 CDN 归因。

## 固定分箱边界

分布图横轴是分箱序号；序号 0 为 underflow，末序号为 overflow，其间按以下边界划分。

```json
{
  "transport_payload_len_edges_bytes": [
    0,
    1,
    32,
    64,
    128,
    256,
    512,
    768,
    1024,
    1280,
    1440,
    1460,
    1500,
    2048,
    4096,
    8192,
    16384,
    65536
  ],
  "ip_total_len_edges_bytes": [
    0,
    40,
    60,
    64,
    128,
    256,
    512,
    768,
    1024,
    1280,
    1440,
    1460,
    1500,
    2048,
    4096,
    8192,
    16384,
    65536
  ],
  "iat_edges_us": [
    0,
    1,
    2,
    5,
    10,
    20,
    50,
    100,
    200,
    500,
    1000,
    2000,
    5000,
    10000,
    20000,
    50000,
    100000,
    200000,
    500000,
    1000000,
    5000000,
    30000000
  ]
}
```

## 特征索引

| 字段 | 变换 |
| --- | --- |
| active_span_sum_s_1000ms | log_ratio |
| active_span_sum_s_100ms | log_ratio |
| active_span_sum_s_500ms | log_ratio |
| burst_bytes_iqr | log_ratio |
| burst_bytes_mad | log_ratio |
| burst_bytes_max | log_ratio |
| burst_bytes_mean | log_ratio |
| burst_bytes_median | log_ratio |
| burst_bytes_min | log_ratio |
| burst_bytes_p95 | log_ratio |
| burst_bytes_q25 | log_ratio |
| burst_bytes_q75 | log_ratio |
| burst_bytes_std | log_ratio |
| burst_count | log_ratio |
| burst_duration_ms_iqr | log_ratio |
| burst_duration_ms_mad | log_ratio |
| burst_duration_ms_max | log_ratio |
| burst_duration_ms_mean | log_ratio |
| burst_duration_ms_median | log_ratio |
| burst_duration_ms_min | log_ratio |
| burst_duration_ms_p95 | log_ratio |
| burst_duration_ms_q25 | log_ratio |
| burst_duration_ms_q75 | log_ratio |
| burst_duration_ms_std | log_ratio |
| burst_packets_iqr | log_ratio |
| burst_packets_mad | log_ratio |
| burst_packets_max | log_ratio |
| burst_packets_mean | log_ratio |
| burst_packets_median | log_ratio |
| burst_packets_min | log_ratio |
| burst_packets_p95 | log_ratio |
| burst_packets_q25 | log_ratio |
| burst_packets_q75 | log_ratio |
| burst_packets_std | log_ratio |
| connection_span_concurrency_max | log_ratio |
| direction_entropy | difference |
| direction_run_analog_runs | log_ratio |
| direction_run_analog_runs_per_packet | difference |
| direction_run_analog_switches | log_ratio |
| direction_run_analog_switches_per_possible_transition | difference |
| down_burst_count | log_ratio |
| down_ip_bytes | log_ratio |
| down_packets | log_ratio |
| down_transport_bytes | log_ratio |
| duration_s | log_ratio |
| entity_count | log_ratio |
| fr_runs | log_ratio |
| fr_runs_per_packet | difference |
| fr_switches | log_ratio |
| fr_switches_per_possible_transition | difference |
| full_retransmission_fraction | difference |
| full_retransmission_packets | log_ratio |
| iat_count | log_ratio |
| iat_median_us | log_ratio |
| iat_us_iqr | log_ratio |
| iat_us_mad | log_ratio |
| iat_us_max | log_ratio |
| iat_us_mean | log_ratio |
| iat_us_median | log_ratio |
| iat_us_min | log_ratio |
| iat_us_p95 | log_ratio |
| iat_us_q25 | log_ratio |
| iat_us_q75 | log_ratio |
| iat_us_std | log_ratio |
| idle_gap_count_1000ms | log_ratio |
| idle_gap_count_100ms | log_ratio |
| idle_gap_count_500ms | log_ratio |
| idle_gap_sum_s_1000ms | log_ratio |
| idle_gap_sum_s_100ms | log_ratio |
| idle_gap_sum_s_500ms | log_ratio |
| ip_bytes | log_ratio |
| length_iqr | log_ratio |
| length_mad | log_ratio |
| length_max | log_ratio |
| length_mean | log_ratio |
| length_median | log_ratio |
| length_min | log_ratio |
| length_p95 | log_ratio |
| length_q25 | log_ratio |
| length_q75 | log_ratio |
| length_std | log_ratio |
| nonempty_entity_count | log_ratio |
| nonempty_packets | log_ratio |
| offload_suspect_fraction | difference |
| packet_count | log_ratio |
| rtt_median_ms | log_ratio |
| rtt_sample_count | log_ratio |
| tcp_ack_count | log_ratio |
| tcp_fin_count | log_ratio |
| tcp_packet_count | log_ratio |
| tcp_rst_count | log_ratio |
| tcp_syn_count | log_ratio |
| tcp_window_raw_median | log_ratio |
| transition_entropy | difference |
| transition_n_mm | log_ratio |
| transition_n_mp | log_ratio |
| transition_n_pm | log_ratio |
| transition_n_pp | log_ratio |
| transition_p_mm | difference |
| transition_p_mp | difference |
| transition_p_pm | difference |
| transition_p_pp | difference |
| transport_bytes | log_ratio |
| up_burst_count | log_ratio |
| up_byte_fraction | difference |
| up_ip_bytes | log_ratio |
| up_packets | log_ratio |
| up_transport_bytes | log_ratio |
| zero_iat_count | log_ratio |
| zero_iat_fraction | difference |
