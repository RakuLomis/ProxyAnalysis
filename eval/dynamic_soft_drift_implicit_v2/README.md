# 解级反馈最终细档校验第二版

原目标、原LR后端与隐式数学保持不变。第一版停止记录只读；旧粗细变化保留为诊断，新资格使用fine与真实一次Newton校验状态的差。模型与全部数值运算CUDA float64，Pytorch312，无CPU回退。

```powershell
& 'D:/Tools/Anaconda/envs/Pytorch312/python.exe' 'eval/dynamic_soft_drift_implicit_v2/runner.py' test
& 'D:/Tools/Anaconda/envs/Pytorch312/python.exe' 'eval/dynamic_soft_drift_implicit_v2/runner.py' all
```

all先执行合成检查、封存合同，再复用三fine并进行实际一次校验，随后按原角色顺序执行q=1的P/G、条件执行q_alt，最终验证与生成报告。任一门失败或信号未决即停止后续依赖计算。阶段与端点不覆盖，失败不自动重启。

每个不同q点只有一次额外完整步长Newton校验，原导数允许误差不放宽。参数重新编码影响单列。平台需独立残差、H和双求解检查，不能只靠零风险变化。coarse状态只有实际观察到时才保存；从不把fine复制成第二精度层级。

fine_state、validation_state和solve_log、validation_log分开，快照元数据不当作失败求解日志。数学复用eval/dynamic_soft_drift_implicit_pilot/内封存gauge、implicit和oracle_bridge，旧文件不修改。新IO只允许源内数值资产；G不能加载P资产；实际目标C/U/H及PCAP禁止。

最大新增LR202个、旧q=1参照精炼11个、一次校验216次、中心隐式评估48次。旧三个fine不重复训练。formal_matrix_authorized始终False，完整先导通过后仍报告并暂停。

运行产物outputs/dynamic-soft-drift-implicit-v2-20261012/run-01/，报告docs/dynamic-soft-drift-calibration/implicit-v2-20261012/。结果以completion.numeric_qualified为资格，不以execution_complete误称通过。
