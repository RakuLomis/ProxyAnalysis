# 前向决策空间先导工程和预算验收

全部工程门、144条生成路径及192个新LR完成。P1固定两任务包含六条生成路径和八个头，已包含在正式总数中，不重复计算。

P1预计1710.456秒，低于8640秒门；最终去重累计690.0134秒，低于10800秒上限。附加结项只读重放约11.52秒。原始分项时间存在登记/继承区间重叠，不能机械求和代替累计保护时钟。

GPU：CUDA float64、32独立模型、8流、CUDA Graph、4并发凸头。生成阶段一次采样92%利用率、2851MiB显存；不是持续或平均测量。

pilot-01因浮点频率逐位检查停止，pilot-02因CUDA布尔赋值广播停止，均在训练前；pilot-03修订装包接口后完整完成。科学模型、损失、引擎与评分的九文件AST保持一致。原ZERO逐位门、分类原坐标梯度门及数据权限不变。

完整修订、数值及读取审计见[结项分析第10至11节](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/decision-aware-forward-drift-20261017/complete-results-analysis-20261017.md)和[独立复核记录](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/decision-aware-forward-drift-20261017/post-closeout-audit.json)。
