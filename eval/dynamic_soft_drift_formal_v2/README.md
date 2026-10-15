# 动态软约束漂移解级正式业务实验

使用已批准的20261012正式计划，独立于Q64及两个隐式先导版本。默认环境Pytorch312；训练、Hessian、微分及推理只允许CUDA float64。

运行入口：

```powershell
& 'D:/Tools/Anaconda/envs/Pytorch312/python.exe' eval/dynamic_soft_drift_formal_v2/run.py prepare
& 'D:/Tools/Anaconda/envs/Pytorch312/python.exe' eval/dynamic_soft_drift_formal_v2/run.py formal
```

prepare封存合同、全部角色/来源和420旧模型，检验权限、480份实际C-OOF、720源内任务及120最终训练缓存。formal先完成外折0的36个新端点，不读取H；数值与资源门通过后完成144个其余端点。600端点共同封存后预测，全部预测封存后评分。

每个新q点采用原LBFGS、最多30步Newton精炼、一次完整Newton校验以及f/v双隐式梯度核验。任一资格失败停止整条评分链，不自动重试或混装旧版本。每个臂固定20次Adam更新加q20终态审计。

训练q的C-OOF关系误差不是独立恢复测试。T-P仍使用P映射；D-P与D-G是全流程对应权限对照。全部科学参数、主比较及bootstrap口径固定，不依据H结果选方法。

新产物位于outputs/dynamic-soft-drift-business-formal-20261012/run-02，执行报告位于docs/dynamic-soft-drift-calibration/formal-20261012/run-02。旧数据、代码及停止记录只读。


本版本只修复序列化：递归转为Python基本标量与Torch张量，写入后在weights_only=True下重读并逐项核对，再发布接受标志。旧run-01代码、停止记录与缓存只读，不使用不安全加载或全局allowlist；不导入旧q、模型或反馈缓存，新正式矩阵从零运行。

