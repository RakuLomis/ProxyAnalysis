# 0916 记录结构＋独立时间：B0–B3 覆盖验收

日期：2026-09-26。资格门：通过。

保留原120访问、30内容、六业务、五折；规范化URL内容ID与旧注册短ID之间核验为一一对应，未重新划分。共1185个排他连接对，2370个捕获文件，唯一体积523,994,048 bytes。

共同合格连接 1179/1185；仅post合格 1180/1185；空共同集合访问 0/120。

| label_id | visits | contents | candidate_pairs | common_pairs | empty_visits | mean_pair_retention | mean_known_byte_retention |
| --- | --- | --- | --- | --- | --- | --- | --- |
| bing.com::search_results_view | 20 | 5 | 158 | 158 | 0 | 1 | 1 |
| developer.mozilla.org::document_view | 20 | 5 | 92 | 92 | 0 | 1 | 1 |
| github.com::repository_view | 20 | 5 | 162 | 161 | 0 | 0.99375 | 0.989607 |
| wikipedia.org::article_view | 20 | 5 | 91 | 91 | 0 | 1 | 1 |
| youtube.com::search_results_view | 20 | 5 | 328 | 328 | 0 | 1 | 1 |
| youtube.com::video_playback | 20 | 5 | 354 | 349 | 0 | 0.986741 | 0.977308 |

## 资格口径

每连接两侧上下行均须通过严格连续语法解析并覆盖全部有效唯一字节。Q0不填零；byte_retention的分母仅包含台账可知的唯一字节，unknown方向数量另报，不能将未知字节当作0。记录类型不代表业务阶段。没有新增分类训练。

## 方向级未通过原因

| side | reassembly_status | parse_status | direction_rows |
| --- | --- | --- | --- |
| post | contiguous | invalid_header_no_resynchronization | 3 |
| post | ledger_Q0 | empty_prefix | 4 |
| pre | ledger_Q0 | empty_prefix | 2 |

## 空共同集合访问

无。

## 当前执行边界

原120访问的成员保持，允许继续B4–B6工程验收；严格双侧筛选仍为离线队列限制。

完整逐访问、逐连接、逐方向台账位于 outputs/record-time-business-0916/run-01。所有原输入哈希复核未变；载荷未落盘。再提取只涉及现有PCAP，不是补采。
