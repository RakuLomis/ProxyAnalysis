# Hy2 HFC0–HFC3 资格审核

状态：尚未进入特征生成或训练；原始数据与旧FSC实验未修改。

固定候选：100访问、25内容、五类，重复1/2/4/5；原内容五折映射核对通过。

扫描全部538个历史尝试的有界trace；主索引carrier 100个。

## 资格缺口

| 原因 | 涉及访问 |
|---|---:|
| carrier_members_missing_request_index | 100 |
| carrier_open_absent_all_attempts | 98 |
| carrier_referenced_other_attempt | 100 |
| carrier_start_precedes_or_missing_from_visit_trace | 98 |
| activity_evidence_not_valid | 1 |
| member_start_evidence_missing | 4 |

## 解释边界

carrier UUID没有重复不等于完整生命周期隔离已经证明。创建事件缺失不能自动判定存在泄漏，也不能自动判定不存在历史成员。
请求索引只覆盖请求关联成员；trace绑定成员更广时，旧pre集合不能代表完整carrier输入。须先检查raw TUN是否可补全，不能把剩余carrier字节分摊给已有成员。
manifest保存独立UTC会话边界，capture ready/stop保存单调时钟。二者不能直接相减；本审核未使用pre首尾或包相似度推算窗口。
成员close不作为硬门：本任务是窗口观测，不要求全部连接在窗口内正常结束。

## 产物

可复用脚本：`eval/hy2_carrier_calibration/prepare.py`；配置：`configs/hy2-carrier-calibration-0916.yaml`。
机器台账：`outputs/hy2-carrier-calibration-0916/run-02/`下contract、候选、carrier、成员、时间窗、来源hash、逐访问资格及qualification-gate。run-01仅为内容键工程检查失败的初始contract，保留不覆盖，未产生模型。
本阶段尚无分类性能，缺口不代表配对增广无效。
