# RA1-NR2 二阶收尾数值先导详细报告

状态：**numeric_pilot_stopped**。本轮是数值求解实验，不是新的业务评价。完整实验未恢复，实际H/U未读取。

## 1. 授权、目标与数据边界

用户批准30分钟活动上限，保持模型、损失、权限、正则和原门不变。训练材料来自原RA1训练-only包，沿用原x/y/mass/mu/scale、t/eta、P/G及CORAL；不重新组织访问或拟合映射。

原目标是加权六分类CE＋0.0005*(1+t)||W||²，bias不惩罚；原坐标梯度≤1e-5、目标/梯度重放<1e-10、目标不增及严格总更新<4000保持。单个问题优化评价额度20000，原LBFGS评价停止时点保留。

## 2. 数值程序与工程验收

从零：原LBFGS最多1024次，未合格则至多32次Newton；易例原门合格即停止，不强制精炼。全部数值CUDA float64，禁用TF32/AMP，无CPU回退。

二阶阶段581维，保留完整576维W，仅固定共同bias均值，另外5维使用Helmert对比基；不是直接删除共同W的485维旧方法。解析Hessian来自原CE和原W-L2。先尝试无阻尼Cholesky，必要时按事前固定数值阻尼序列求方向；阻尼不计入损失。Armijo c1=1e-4、步长1至2^-24，共25候选。

工程验收记录：未完成。包括四档t的原目标/梯度/解析Hessian对照、两真实失败槽的六个固定HVP核对、CUDA/精度/非有限/阻尼/无下降线搜索/权限及预算负例。详见audits/engineering.json和backend-diff.json；这些工程门不要求业务增益。

## 3. 快照诊断：不修改旧失败

| id | parent_iterations | Newton | gradient | objective | seconds | scientific_accepted |
| --- | --- | --- | --- | --- | --- | --- |

两个诊断各最多8次Newton；即使梯度达标，也不能将旧2000/4000次触顶改判通过，不能直接用于正式模型。原失败快照只读，新输出在独立目录。

## 4. 从零的已知困难点

| role | policy | LBFGS | Newton | total_updates | evaluations | gradient | objective | seconds |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |

新算法没有在4000次后追加求解，而是在1024次内部切换，仍在原总预算内。两个困难点的1024步前缀另作独立重放，和新混合程序的阶段参数比较；结果见audits/prefix-comparison.json。不能将“同目标”误写为全程相同轨迹。

## 5. 固定矩阵与计数

设计52个唯一案例，10角色，四部署、五折、G0/G1/G2及t=0/0.25/1/4。当前接受0/52。新增从零拟合含重复、快照诊断、前缀诊断均独立记账。

| optimization_attempts | unique_zero_start_accepted | fresh_zero_start_final_fits_attempted | accepted_repeats | snapshot_diagnostics_qualified | prefix_diagnostics_complete | failed_or_interrupted_attempts | pending_unique_cases |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 0 | 0 | 0 | 0 | 0 | 0 | 52 |

| source | count | Newton_cases | max_LBFGS | max_Newton | solver_seconds | max_gradient |
| --- | --- | --- | --- | --- | --- | --- |

案例不是发生率抽样；不以通过率保证其他未运行角色必定合格。

## 6. 原端点保护与独立审核

已完成旧端点原坐标复核0/1024；其中604个科学端点和420历史逻辑参照均应保留源后端、政策、额度与哈希，不能改写为走过NR2轨迹。最终来源保护状态：False。

尚未完成交叠对照。

两次新Z确定性重复见audits/deterministic-repeats.json。旧新参数不必相等；同一新算法、同输入的重复则要求参数和训练logits精确一致。新旧交叠比较不用于选择模型或调参。

## 7. 实际成本与停止状态

报告生成时先导活动7.160秒，先导上限1800秒；父累计收费约7.160秒，父上限28800秒，不重置。最终含报告写盘的数值见cost-final.json。

新结果及快照诊断求解计时0.000秒；另有前缀诊断0.000秒。记录到的Newton方向步骤0，非零阻尼步骤0。Hessian/分解/求解/审核都消耗活动预算，不以“小LR”掩盖其成本。

父活动账继承Full NR1的1622.342958秒，加入已记录后续只读分析和明确的60秒保守历史分析收费；后者不是实测。源码编写与人工沟通不被伪装成训练活动计时。

异常：[Errno 2] No such file or directory: 'F:\\Program\\VSCode\\MyGit\\ProxyAnalysis\\outputs\\role-asymmetric-transfer-v1-20261017\\numeric-pilot-nr1\\manifests\\numeric-policy.json'。

## 8. 结论边界与下一节点

本轮尚未获得完整数值先导资格；保留停止和已完成产物，不能通过追加步骤、换门或跳过失败项制造通过。

没有H预测、标签评分、新F1/CE/Brier或混淆矩阵。这不是分类正负结果，不能说明RA1一定有效或无效。现有合格端点继续保留，未来采纳仍须明确恢复合同；两个快照诊断不能被采纳。

## 9. 主要产物

- 计划：plan/RA1-NR2-same-objective-second-order-pilot-plan-20261018.md
- 代码：eval/role_asymmetric_transfer_nr2_pilot/
- 运行：outputs/role-asymmetric-transfer-v1-20261017/numeric-pilot-nr2/
- contract/seal、input-fingerprints、engineering、snapshot-diagnostics、prefix-comparison、deterministic-repeats、independent-new-endpoints、old-endpoint-compatibility及verification分别保存。
- attempts/results/live/lbfgs-logs保留成功、失败、内部阶段与逐步轨迹；reads.json、cost-final.json及failure/completion保留权限和结项状态。
