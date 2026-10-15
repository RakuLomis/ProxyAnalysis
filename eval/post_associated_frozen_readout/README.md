# 固定G的源内输出坐标读出

按`plan/post-input-representation-output-scale-plan-v2-20261014.md`实现。G、教师、基座和原数据权限冻结；只拟合输出坐标中的小型读出。X/R/G/P四类输入，η=1/0.01两项固定政策，240个实际头部、288个逻辑端点。

主入口：

```powershell
& 'D:\Tools\Anaconda\envs\Pytorch312\python.exe' -B -u 'eval\post_associated_frozen_readout\run.py'
```

`register.py`登记只读来源与权限；`features.py`只读取并冻结G；`head.py`定义共同类别零均值正交坐标及独立梯度；`solve.py`执行固定CUDA float64 LBFGS；`pipeline.py`负责接口先导、全部拟合、封存预测后评分及精确重放。没有原训练总调度器或H评分调用。

历史结果不覆盖，主入口拒绝已存在运行目录；不能通过重跑清除失败或重新选η。X的三个seed引用同一头部，并非三个独立拟合。

独立审计入口：

```powershell
& 'D:\Tools\Anaconda\envs\Pytorch312\python.exe' -B 'eval\post_associated_frozen_readout_audit\analyze.py'
```

独立审计同样拒绝覆盖已有分析记录，不拟合任何模型。业务结果仅限12个结构性源内任务，不启用实际外层角色，也不读取H/U。完整报告位于`docs/post-associated-frozen-readout-20261014/complete-report.md`。
