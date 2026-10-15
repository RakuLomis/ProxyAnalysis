# 动态漂移资格策略实施模块

当前仅实现P0只读结项，不包含P1至P4训练或评价入口。

## P0命令

从仓库根目录使用Pytorch312：

```powershell
D:/Tools/Anaconda/envs/Pytorch312/python.exe eval/dynamic_soft_drift_qualified_policy/closeout.py --test
D:/Tools/Anaconda/envs/Pytorch312/python.exe -u eval/dynamic_soft_drift_qualified_policy/closeout.py
```

脚本拒绝覆盖已存在的P0目录；重新版本必须显式登记。它不导入旧运行的写日志模块，不拟合模型、不重做隐式微分、不读取H/U数值或PCAP。CPU只做安全checkpoint读取、哈希及已有数值的描述性重放，没有CPU训练或测试回退。

## 产物

当前输出为outputs/dynamic-soft-drift-optimizer-closeout-20261013/run-02，报告为docs/dynamic-soft-drift-calibration/qualified-policy-20261013/P0-optimizer-closeout.md。

主表36行，另含18条资格失败路径、6条预算原因、接受更新、所有候选、逐块梯度、后端起终点、P/G共享物理成本、来源链和独立稳定资产封存。rejection_reason_counts_json是明确的JSON文本，不是浮点值；需要明细时解析它或读取trial-decisions表。

run-01在36条数值重放完成后，因失败子表中的空字典不受Parquet支持而停止导出。其产物、failure.json和精确源码快照保留。run-02只修正该字段的导出schema，旧数值和资格不变。

## 停止范围

P0不生成q_use或新的策略端点。完成后状态为P0_complete_waiting_policy_confirmation，等待资格合同、资源预算和C业务代价门确认。不可将P0完成视为旧先导已通过或后续业务已授权。
