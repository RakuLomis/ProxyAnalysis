# 解级反馈第二版执行结果摘要

2026年10月12日。完整预定先导已通过，状态为`qualified_solution_feedback_v2`。正式q学习和业务分类矩阵没有启动，因此本轮没有新的F1结论。

## 完成范围

六个固定源内角色、P/G两种数值问题，分别在q=1和交替0.9／1.1点核对。全部96条两方向、两步长差分检查通过；24个中心的f/v十维梯度稳定性通过，共48次隐式评估。216个不同q点各执行且只执行一次独立Newton校验，全部通过。288条f/v及D-P、T-P、D-G惩罚组合分项记录也通过。

新增202个源内LR全部接受，11个旧q=1参照精炼，3个旧fine直接复用。获得fine共426次Newton精炼更新，另216次一次校验。主要三个数值阶段合计约131秒，不含启动、合同封存、哈希核验和报告。

全部模型、Hessian、线性求解及求导在Pytorch312的CUDA float64中运行，无CPU数值回退。实际目标C/U/H及PCAP读取为零，新漂移映射和正式分类器均为零。

## 精度检查

| 量 | 实际结果 |
| --- | ---: |
| fine原梯度最大值 | 3.87488e-11 |
| 校验状态原梯度最大值 | 3.03841e-16 |
| 解析H与AD归一化差最大值 | 1.33878e-15 |
| 校验Newton系统后向误差最大值 | 1.98973e-16 |
| 双求解校正相对差最大值 | 3.25932e-13 |
| fine/校验状态风险变化最大值 | 1.31949e-8 |
| 满足预定平台标签的点 | 138/216 |
| 校验参数与fine完全相同的点 | 0/216 |

风险变化不全为零，平台标签也不是全部通过的理由。每个点均有实际校正向量、独立残差、H和双求解记录，不是把同一快照重新命名。

## 首例修订与最接近门限的案例

首例原粗细诊断仍为2.95031e-5，旧停止判定未改。新带底限U_fv为1.00139e-8，小于同一允许上限1.14608e-5。新合同检查最终fine的稳定性，而不是重新判定旧粗细指标通过。

最大细档隐式导数与差分绝对差为4.29745e-4，但不能脱离对应方向尺度解释：全部案例的误差除自身允许误差，最大仅为0.0675442。该相对最接近门限的案例是Trojan排除角色G0的源内G问题、q=1、全同向h=1e-4；误差7.10457e-6，上限1.05184e-4。

U_fv与自身允许上限的最大比值为0.692123。对应SS排除角色G2的源内G问题、q_alt、交替方向h=3e-5；指标1.28782e-6，上限1.86068e-6。该项通过但裕量小于首例，不能将全队列称为统一接近机器精度。

96条方向导数中46为正、50为负；没有删去提高CE的扰动，也没有因方向不改善业务而判失败。本轮预定检查中没有信号未决项。

## 结论边界

可以停止围绕有限展开长度的数值修复，转向登记正式D-P、T-P、D-G与P-small业务比较。当前通过的是固定源内先导的解级反馈资格，不证明整个q范围、全部正式角色或未来优化轨迹上的点都可靠，更不证明动态约束已提高分类。

修订基于已分析首例形成，属于源内数值复核，不是外部盲测。旧第一版停止记录与所有父产物保持不变。独立交付核对检查了2038项封存哈希，并再次逐项核对全部96差分、216校验、48隐式评估及288组合分项。

- [完整报告](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/dynamic-soft-drift-calibration/implicit-v2-20261012/implicit-fine-validation-v2-report-20261012.md)
- [完成状态](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/dynamic-soft-drift-implicit-v2-20261012/run-01/completion.json)
- [计算账本](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/dynamic-soft-drift-implicit-v2-20261012/run-01/ledger.json)
- [封存合同](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/dynamic-soft-drift-implicit-v2-20261012/run-01/manifests/contract.json)
- [实现及重放说明](F:/Program/VSCode/MyGit/ProxyAnalysis/eval/dynamic_soft_drift_implicit_v2/README.md)
