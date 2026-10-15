# 辅助业务校准迁移实验第四版实施状态

记录时间：2026年10月6日20时57分53秒，上海时区。本文件是启动阶段快照；后续实时状态以run-04的progress与终态文件为准。

第四版统一预算修订已实现，准备和单元验证通过，契约已封存，后台运行器正在执行固定300候选先导。两个历史失败角色的CT1、t为0已通过原坐标精度门。完整先导、确定性重复及主矩阵尚未完成，因此仍没有新的主业务比较结果。

## 一 实现范围

遵循[第四版批准计划](F:/Program/VSCode/MyGit/ProxyAnalysis/plan/calibrated-deployment-unified-budget-repair-plan-20261006.md)，新代码放在 `eval/calibrated_deployment_transfer_v4/`，新输出仅写run-04，新报告写本目录。前三版源码、模型、失败状态和报告未修改；未修改PyTorch安装，未补采或扫描PCAP。

统一政策将max_iter改为2000、max_eval改为10000，正式迭代资格同步改为小于2000。原CE、原W的L2、无bias正则、预条件化、96维表示、五主臂、四个t、资源权限与科学终点全部保留。原坐标梯度门仍为不超过10⁻⁵，两项重放精度仍小于10⁻¹⁰。

新增独立的numeric_policy模块，求解、模型发布、重启跳过和最终核验共同读取该政策。侧车记录政策hash，禁止混用旧主候选；旧680诊断仍按历史小于500次政策核验。

函数评价预算继续在一轮线搜索后检查，实际超出量单独记录，不改为逐closure硬截断。日志分开记录迭代预算命中、评价预算命中、超出量、实际退出、原梯度审核计数及接受门。原坐标梯度感知停止和第三版数值保险丝保持不变，没有Newton或CPU后备。

## 二 准备和验证结果

| 检查 | 实际结果 |
| --- | --- |
| 旧实验进程 | 启动前未发现旧校准迁移进程 |
| 新运行根 | 启动前不存在run-04 |
| 旧来源和源码 | 按封存hash检查通过 |
| 训练slot | 3900个，有限值、形状和业务质量审核通过 |
| 复用登记 | 15570项记录；含历史引用，不等于15570个新样本 |
| 先导角色 | 与第三版15角色清单一致，全部合法内层角色 |
| 单元检查 | 44项通过 |
| 完整合成拟合 | 固定4次；未扩成求解器搜索 |
| 无效质量负测试 | 1次零优化步骤尝试，拒绝并保存状态 |
| 目标等价最大绝对误差 | 2.0250467969162855×10⁻¹³ |
| 原模式对照 | 参数与closure轨迹逐元素／逐值一致 |
| CUDA资格 | Pytorch312，CUDA float64，无CPU数值回退 |

预算状态注入覆盖1999／2000、9999／10000、旧500／625边界，以及超出评价预算后不再更新。发布日志负测试拒绝错误政策hash。正常和固定300倍列尺度压力拟合均通过原精度门。

单测只使用合成数据和两个历史失败角色的合法训练slot，不读取目标U、验证成绩或测试流量进行数值政策选择。

## 三 历史失败角色的新结果

两行均为SS外层G0、伪校准VLESS、CT1、t为0。内层训练内容不同，目标值不能用于跨行比较方法好坏。

| 内层角色 | 接受 | 迭代 | 优化函数评价 | 原坐标最大梯度 | 原目标 |
| --- | --- | ---: | ---: | ---: | ---: |
| i1 | 是 | 276 | 286 | 8.021533031976074×10⁻⁶ | 0.09129222115374153 |
| i2 | 是 | 567 | 929 | 9.993422908570845×10⁻⁶ | 0.100527014283807 |

两者退出均为原梯度验收收敛，未触发新版迭代或评价上限。两者目标重放误差均为2.7755575615628914×10⁻¹⁷；梯度重放误差分别为2.8129337373934346×10⁻¹⁵和1.440849418333427×10⁻¹⁴。

i2在第三版415次、625评价时未通过，本版从零开始，使用567次、929评价通过。这支持配套预算修订足以处理该固定历史失败角色，不证明全部300候选或14700主模型均可求解，也不代表CT4已取得分类增量。

## 四 后台运行与条件启动

运行器于20时55分37秒在隐藏后台启动，父进程PID为25360。20时57分53秒快照为先导69／300接受，无failure.json，stderr为空。RTX 4060 Ti上已核验到CUDA进程和显存占用；这不是显卡持续利用率保证。

运行器已登记以下顺序，不需要在先导通过后重新改参数：300先导全部通过，两个历史失败CT1确定性重复均参数差0，680诊断和20参照兼容性审核，通过后晋升本版先导，再执行剩余14100内层、源内选择、300外层、封存post预测、原统计、离线解释、全量核验和最终报告。

任一模型数值失败即保存失败参数和日志并停止；不会跳过CT1、放宽梯度门、临时增预算或切换Newton。工程失败后禁止原runner静默重试。新的主业务结论必须等待完整预测、检验和verification，不能从训练目标推导。

## 五 直接入口

- [第四版代码说明](F:/Program/VSCode/MyGit/ProxyAnalysis/eval/calibrated_deployment_transfer_v4/README.md)
- [统一数值政策](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/calibrated-deployment-business-transfer-20261006/run-04/manifests/numeric-policy.json)
- [封存实验契约](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/calibrated-deployment-business-transfer-20261006/run-04/manifests/experiment-contract-v4.json)
- [单元验证](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/calibrated-deployment-business-transfer-20261006/run-04/manifests/optimizer-unit-tests.json)
- [等价检查](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/calibrated-deployment-business-transfer-20261006/run-04/manifests/objective-equivalence.json)
- [实时状态](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/calibrated-deployment-business-transfer-20261006/run-04/progress.json)
- [后台日志](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/calibrated-deployment-business-transfer-20261006/run-04/runner.stdout.log)

数值政策SHA256为 `7c8c5d444546fb0cac4a9b44ed4ec29b37dafd9338957776d52010780d64373f`。本机LBFGS源码SHA256为 `bdffab66a92c3792148ca581dd1f831a777b170151828863cf5b4e4bbd94b361`，未修改安装文件。

后台状态会继续变化，本文件中的69／300和PID只是上述时间点的记录。最终以completion和verification确认成功，或以failure与工程中止状态确认停止。
