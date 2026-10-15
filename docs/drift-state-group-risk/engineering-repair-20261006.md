# DSR梯度日志工程修订 2026 10 06

根据用户2026-10-06的确认，本轮修复仅将L2单项的bias梯度显式记为零。L2仍为 `0.0005 * ||W||²`，没有给bias增加正则化；CE、组风险增量及logit保护仍严格求取W与bias的梯度。分类目标、alpha候选、温度、保护系数、模型容量、划分与预算未改变。

原封存契约未覆盖，全部原源码已保存快照。修订使用独立的 `experiment-contract-amended-v1.json`，运行时校验其封存SHA及原契约SHA；原目标、风险、分组、推理与优化函数的AST一致，训练主函数AST一致。报告日期及复现说明属于记录更新，不参与学习。

## 复用范围

修订前记录了3405个已有文件的SHA。封存修订时逐一验证旧来源、角色包、核、难度模型和内层状态未变。240个内层CF查询对应40个独立训练集合；400个新核bundle、40个难度LR及已完成的内层gamma均继续复用，不扩大任何源模型的训练范围。

首个失败角色尚未写出完整候选，正alpha模型数量为零，alpha选择及外层预测均未生成。因此修复不依赖本轮分类效果。原停止记录保留作历史事件，不代表修订后的当前状态。

## 修复测试

| 测试 | 结果 |
| --- | --- |
| 人工基座处的单项梯度 | L2的bias梯度为零；W梯度范数与解析式一致 |
| 人工非零修正处的单项梯度 | 同样通过，其他项严格求导 |
| 实际首失败角色 f0/shadowsocks/i1 | 四项日志均为有限值，L2的bias范数为零 |
| 原目标及训练主函数AST | 与快照一致 |
| 旧来源、包及既有CF产物SHA | 修订封存前全部一致 |

原16项封存前数值与权限测试保留，新增修复测试另存。恢复点为D14，依次完成内层固定矩阵、内容OOF选择、外层训练及post-only推理、独立评分、内容bootstrap、封存后状态诊断和最终重放。任何新增工程门限失败仍停止，不通过扩大预算或改变目标掩盖问题。

## 可追溯文件

- `outputs/drift-state-group-risk-20261005/run-01/manifests/experiment-contract.json`：原登记契约。
- `outputs/drift-state-group-risk-20261005/run-01/manifests/experiment-contract-amended-v1.json`：当前工程修订契约。
- `outputs/drift-state-group-risk-20261005/run-01/manifests/engineering-repair-v1/original-source/`：原源码快照。
- `outputs/drift-state-group-risk-20261005/run-01/manifests/engineering-repair-v1/original-contract.json`：原契约快照。
- `outputs/drift-state-group-risk-20261005/run-01/manifests/engineering-repair-v1/preservation.json`：原来源及既有文件SHA。
- `outputs/drift-state-group-risk-20261005/run-01/manifests/engineering-repair-v1/repair-tests.json`：新增CUDA梯度诊断测试。
- `outputs/drift-state-group-risk-20261005/run-01/manifests/engineering-repair-v1/amendment-seal.json`：修订封存SHA。

最终阶段状态以本轮 `progress.json`、阶段读取台账及 `report-complete.json` 为准。本修订记录不提前评价分类收益。
