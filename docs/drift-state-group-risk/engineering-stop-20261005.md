# DSR实施进度与工程停止记录（2026-10-05）

## 当前状态

已执行至D13；D14的首个梯度诊断失败，按批准计划的工程阶段门停止。尚未训练正alpha候选、选择alpha、生成外层分类预测或统计区间。因此本记录不是分类结果报告，不能据此判断DSR4有效或无效。

旧来源、新契约及封存源码均保持不变；没有修改目标、温度、保护系数、L2尺度或优化预算。没有扫描PCAP，也没有推送仓库。

## 已完成的产物

| 阶段 | 已完成内容 |
| --- | --- |
| D00–D09 | 核验23566连接对、480访问、30内容；构建100分类角色、320逻辑CF查询及隔离包；16项数值与接口测试全部通过；封存契约及来源SHA |
| D10–D11 | 重放80个18内容来源角色；CUDA float64拟合40个独立12内容难度LR及400个核bundle，复用于240逻辑查询 |
| D12 | 为80个内层分类训练角色生成240个CF查询，查询内容均排除在源拟合之外 |
| D13 | 生成并封存DSR2/3/4的内层gamma、1440个业务边界、内容质量与支持诊断 |
| D14 | 在首角色 `f0/shadowsocks/i1` 的梯度诊断停止；正alpha模型文件数为0 |

环境为Pytorch312、PyTorch2.5.1、CUDA12.4、RTX4060Ti；数值拟合、分箱、查询和分组使用CUDA float64，关闭TF32并开启严格确定性。IO及审计不要求GPU。显卡利用率不能代替方法效果。

当前机器产物位于 `outputs/drift-state-group-risk-20261005/run-01/`：

- `manifests/experiment-contract.json`：源码、角色包和旧来源SHA，以及固定超参数与统计家族。
- `manifests/unit-tests.json`、`environment.json`、`role-audit.json`：封存前测试、环境与来源成员。
- `manifests/reuse-replay.json`、`CF12-optimizer.parquet`：旧来源重放与新增源拟合日志。
- `kernels/sources/`、`models/sources/`：400个新核bundle与40个难度LR。
- `CF-predictions/`：240个训练范围CF难度预测及各自封存记录。
- `states/inner-CF-scores.parquet`、`inner-boundaries.parquet`、`inner-composition.parquet`、`inner-visit-masses.parquet`：三种状态分数、阈值和完整诊断。
- `states/main/`：各内层角色冻结gamma。

首个业务模型目录存在一份复制的零基座，但没有 `complete.json`，不得将其视为完成的候选训练。尚不存在正式内层选择、最终外层分类结果或本轮主比较区间。

## 报错与只读验证

报错来自 `eval/drift_state_group_risk/train.py` 的 `activity()`：

```text
RuntimeError: One of the differentiated Tensors appears to not have been used in the graph.
```

诊断对每个单项同时调用 `torch.autograd.grad(target, [W, b])`。原契约的L2项是 `0.0005 * ||W||²`，不含bias，因此PyTorch认为bias未参与该项的计算图。它默认拒绝这种梯度请求，而不是自动返回数学上的零。

对首角色执行了只读CUDA核查，使用 `allow_unused=True` 仅查看哪些梯度不存在，没有优化或改写模型：

| 项 | W梯度未参与 | bias梯度未参与 |
| --- | --- | --- |
| CE | 否 | 否 |
| L2 | 否 | 是 |
| 平滑组风险增量 | 否 | 否 |
| logit保护 | 否 | 否 |

这定位为单项梯度日志的工程错误，不是已观察到的收敛失败，也不是CUDA失败。当前没有新的分类效果数据可供选择或解释。

## 待确认的最小修复

仅修正梯度诊断：对L2求W梯度，并将该项bias梯度显式记录为零；其他项继续严格请求W与bias梯度。不要通过给bias增加L2来修复，因为那会改变已批准目标；也不要对所有项无条件放宽缺失梯度检查。

确认后先保存原封存源码及契约的可追溯快照，单独登记工程修订、修改后的源码SHA与新增测试。测试需覆盖实际L2单项的bias零梯度及其他项图依赖。保留原合同，不静默覆盖。

修订只影响梯度日志，不影响已完成的CF核、难度模型、状态或角色包；在校验旧SHA和成员后复用这些产物，从D14恢复。固定模型、目标、alpha候选、tau、eta、预算及主终点全部不变；完整执行D14–D26后给出正式报告。

若尚未批准工程修订，保持停止，不自动执行后续拟合。
