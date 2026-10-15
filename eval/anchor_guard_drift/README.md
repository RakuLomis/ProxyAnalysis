# 不变锚点约束漂移第一阶段

使用已批准的 `plan/invariant-anchor-guarded-drift-plan-20261012.md`。全部数值计算使用Pytorch312 CUDA float64；没有新分类器、没有PCAP扫描、没有目标U或H查询。

先进行无真实数据、无写盘的合成预检：

```powershell
& D:/Tools/Anaconda/envs/Pytorch312/python.exe eval/anchor_guard_drift/tests.py --preflight
```

预检通过后，一次性执行：

```powershell
& D:/Tools/Anaconda/envs/Pytorch312/python.exe -u eval/anchor_guard_drift/run.py
```

inventory封存源码、门限和历史来源。prepare只从合法C及源训练包生成分离的拟合、预测和评分输入。diagnostics封存全部预测后，score才能读取C验证post。score产生真配与匿名组独立的规则，source_audit只对合法源pre应用冻结历史映射，report与verify最终输出结构诊断及停止决定。

新运行位于 `outputs/invariant-anchor-guarded-drift-20261012/run-01`；报告位于 `docs/invariant-anchor-guarded-drift`。旧产物只读。不改阈值，不在此入口启动分类；阶段二需单独确认。

失败保留在新运行的failures目录。未完成的工程阶段可单独核查，但修改已封存代码必须登记工程修订，不能将方法或阈值变更混作修复。
