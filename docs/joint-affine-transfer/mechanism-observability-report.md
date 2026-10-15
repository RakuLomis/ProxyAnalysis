# 协议机制可观测性资格报告

本轮仅使用固定训练样本与现有抓包。记录是语法证据，不是initial或relay阶段；不增加业务输入。

登记16访问、32连接对；实际读取16个PCAP，含哈希和解码两遍共0.855 GiB；记录828条。

文件预算耗尽的样本保持原登记且标注未解析，不拿成功子集替换分类队列。

| 协议 | 侧 | 状态 | 方向数 |
| --- | --- | --- | ---: |
| shadowsocks | post | SS_ciphertext_chunks_unobservable_no_keys | 8 |
| shadowsocks | post | fixed_file_budget_exhausted | 8 |
| shadowsocks | pre | fixed_file_budget_exhausted | 8 |
| shadowsocks | pre | invalid_header_no_resynchronization | 2 |
| shadowsocks | pre | syntax_prefix_complete | 6 |
| trojan | post | fixed_file_budget_exhausted | 8 |
| trojan | post | syntax_prefix_complete | 8 |
| trojan | pre | empty_prefix | 1 |
| trojan | pre | fixed_file_budget_exhausted | 8 |
| trojan | pre | invalid_header_no_resynchronization | 2 |
| trojan | pre | partial_record_body | 1 |
| trojan | pre | syntax_prefix_complete | 4 |
| vless | post | fixed_file_budget_exhausted | 8 |
| vless | post | syntax_prefix_complete | 8 |
| vless | pre | fixed_file_budget_exhausted | 8 |
| vless | pre | invalid_header_no_resynchronization | 4 |
| vless | pre | partial_record_body | 1 |
| vless | pre | syntax_prefix_complete | 3 |
| vmess | post | fixed_file_budget_exhausted | 8 |
| vmess | post | syntax_prefix_complete | 8 |
| vmess | pre | fixed_file_budget_exhausted | 8 |
| vmess | pre | partial_record_body | 1 |
| vmess | pre | syntax_prefix_complete | 7 |

SS实际chunk、VMess内部块与initial/relay仍不得补成观测量。AnyTLS及Hy2仍未进入本轮排他TCP分类。

训练特权与测试post可生成性分开登记；详细来源、预算和失败见本地observability证据目录。
