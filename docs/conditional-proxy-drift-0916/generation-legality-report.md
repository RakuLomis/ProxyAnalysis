# F4–F5 前向漂移：训练OOF生成与合法性门

> 阶段时点说明：本文件保留对应阶段的执行记录；其中“尚未分类/尚未测试”描述该阶段时点。现F0–F10均已完成，最终结论见[综合总结](summary.md)。

40个训练内生成任务全部完成；仅使用各外层训练内容。每任务72访问拟合，24访问生成，LOCO残差不见对应内容；未读取外层测试pre进行生成，未训练业务分类器。

所有Ridge拟合、条件中心预测均CUDA float64；中心中位数在CUDA计算。采样、整数解码及审计在CPU。

## 冻结门限

按每部署×臂汇总全部训练OOF视图：首次非法率不得超过10%，最终fallback率不得超过1%。门限和汇总口径先于结果冻结。

| protocol    | arm   |   source_views |   first_invalid_rate |   fallback_rate |   mean_attempts | gate_passed   |
|:------------|:------|---------------:|---------------------:|----------------:|----------------:|:--------------|
| SHADOWSOCKS | T1    |          11520 |             0.000000 |        0.000000 |        1.000000 | True          |
| SHADOWSOCKS | T2    |          11520 |             0.001910 |        0.000000 |        1.001997 | True          |
| SHADOWSOCKS | T3    |          11520 |             0.000000 |        0.000000 |        1.000000 | True          |
| SHADOWSOCKS | T4    |          11520 |             0.000000 |        0.000000 |        1.000000 | True          |
| SHADOWSOCKS | T5    |          11520 |             0.039931 |        0.000000 |        1.044358 | True          |
| VLESS       | T1    |          11520 |             0.000000 |        0.000000 |        1.000000 | True          |
| VLESS       | T2    |          11520 |             0.083507 |        0.000000 |        1.101736 | True          |
| VLESS       | T3    |          11520 |             0.000000 |        0.000000 |        1.000000 | True          |
| VLESS       | T4    |          11520 |             0.034635 |        0.000000 |        1.039062 | True          |
| VLESS       | T5    |          11520 |             0.042882 |        0.000000 |        1.047830 | True          |

T1固定中心；T2无条件联合漂移；T3条件中心；T4真配条件联合残差；T5错配同机制。确定性臂复制8视图仅保持预算，不增加独立样本量；全部115200行重复使用相同240访问/30内容。

## 首次失败原因

| protocol    | arm   | first_reason           |   source_views |
|:------------|:------|:-----------------------|---------------:|
| SHADOWSOCKS | T2    | direction_imbalance    |             22 |
| SHADOWSOCKS | T5    | R_E_U_order            |             56 |
| SHADOWSOCKS | T5    | direction_imbalance    |            360 |
| SHADOWSOCKS | T5    | runs_below_connections |             44 |
| VLESS       | T2    | R_E_U_order            |            917 |
| VLESS       | T2    | direction_imbalance    |             45 |
| VLESS       | T4    | R_E_U_order            |            399 |
| VLESS       | T5    | R_E_U_order            |            492 |
| VLESS       | T5    | direction_imbalance    |              2 |

输出保存first_raw、last_raw、整数结果及每次尝试的原因；最多32次重抽，仍失败显式回退原pre，不逐维裁剪。未将fallback标志作为分类特征。中间重抽的原始六维向量未全部持久化，可由固定输入、seed与代码重放。

## 阶段结论

通过，可继续F6–F10。

失败说明当前坐标加法采样不保证必要摘要约束，不证明代理变换不可学习，也没有产生新的分类收益数字。
