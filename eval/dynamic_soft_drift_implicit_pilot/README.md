# 解级反馈源内先导

保持原P-small/G-small目标，使用已验收LR和同目标Newton精炼获得前向解，再计算隐式梯度。所有数值运算仅CUDA float64；不读取实际目标C/U/H或PCAP。

运行环境：Pytorch312。先执行合成检查，再注册并封存代码和合同，后续不可原位修改已封存代码。

```powershell
& 'D:/Tools/Anaconda/envs/Pytorch312/python.exe' 'eval/dynamic_soft_drift_implicit_pilot/runner.py' test
& 'D:/Tools/Anaconda/envs/Pytorch312/python.exe' 'eval/dynamic_soft_drift_implicit_pilot/runner.py' all
```

`all`依次执行注册、旧计数纠正和几何、q=1、条件执行q_alt、完整性验证和报告。任何门失败即停止后续数值阶段，但保留失败日志并生成报告；完成状态的numeric_qualified才表示数值资格，execution_complete不表示成功。

也可按register、geometry、one、alt、verify分别运行。已完成阶段和已生成端点拒绝覆盖，失败不自动续跑。报告入口是report.py。软件修订需独立版本和账本；不允许靠重新运行同一命令覆盖失败。

固定六角色、P/G两种数值问题、两点、两方向和两个差分步长。P与T-P共享任务梯度，分别加惩罚；G使用自己的匿名资产。精确Helmert参数化消除共同bias并解析最小化共同W，但不新增正则。解析H及混合导数与AD复核，Cholesky和通用线性求解复核同一系统，不把后者作为失败回退。

产物位于outputs/dynamic-soft-drift-implicit-pilot-20261012/run-01/，报告位于docs/dynamic-soft-drift-calibration/implicit-20261012/。不授权正式q学习。
