# RA1 Full NR2：恢复核验与启动记录

日期：2026-10-18。本页为恢复工程验收后的启动快照，不是完整实验结果。

## 已完成

- R0合同已封存：原60角色、39政策及科学比较不变。
- E0适配器工程检查通过，没有额外拟合；已验收NR2数值函数体不变，IO和预算注入到独立运行根。
- R1全部1044个复用逻辑端点独立审核通过：624科学端点＋420历史参照。来源政策、预算和原日志保留；NR2的52个从零唯一端点优先，交叠32个旧模型仍只读保留。
- 预测和评分模块与原RA1的AST一致，没有重新选择比例、正则、尺度或模型。
- 原两次科学停止、NR1/NR2先导及工程停止均保留，不向失败优化器追加步骤。

## 当前执行

P3正在补齐1296个科学端点，进程启动PID为32312。最近检查时心跳已报告48个新增合格端点，而逐端点台账已有59个；程序每12个更新汇总心跳，两个数字的短时差异不代表漏记。后续以运行目录实时progress.json及new-endpoints为准，不将本快照当作最终计数。

每个新模型均从零，使用最多1024次原LBFGS更新；未按原门合格才进入最多32次Newton。原目标、W-L2、bias不惩罚、完整原梯度≤1e-5及重放/严格总预算门不变，数值全程CUDA float64。

检查时没有failure.json，也没有H预测或标签评分。当前不存在新的F1、CE、Brier或混淆矩阵结论。

## 预算与权限

继承最新已记录父累计2048.441729秒；其后未单独计量的只读结项检查保守收费60秒，明确非实测，新执行父基数为2108.441729秒。原8小时上限不重置，28680秒停止计算并保留120秒结项。

所有1044复用核验完成后才进入当前P3。后续固定顺序：1296新拟合全部合格→2340端点封存→56160条H-post预测及封存→H标签评分→完整报告和独立复核。

发生新数值不合格、预算或来源完整性问题时，程序保留失败、已接受端点和pending，停止而不自动重试/回退；未运行不能当成功。当前不需要新增用户决定，完整流程由既定调度继续。

## 路径

- 恢复合同：`plan/RA1-NR2-full-resume-contract-20261018.md`
- 代码：`eval/role_asymmetric_transfer_nr2_full/`
- 运行：`outputs/role-asymmetric-transfer-v1-20261017/full-nr2-01/`
- R1证明：`audits/adoption-complete.json`、`manifests/adopted-endpoints.parquet`
- 活动基数：`manifests/prior-activity.json`
- 当前进度：`progress.json`、`new-endpoints/`
- 成功终态：`completion.json`及`verification.json`；停止终态：`failure.json`、`run-closeout.json`及`pending-on-stop.json`

完整完成后才会生成本目录`complete-report.md`，不以启动记录冒充结果报告。
