# 校准迁移主实验的优化异常定位

日期：2026年10月6日。

异常已经在隔离 CUDA 复现中定位：首个 CT1 候选同时未通过迭代预算和原坐标梯度检查。优化器确实完成了500次迭代，而最大梯度仍为0.0022676853，大于接受阈值0.00001。独立目标和梯度公式复核通过，训练视图重构也完全一致。

这将此前“具体失败条件尚未记录”的结论更新为可重复的数值证据。它不是CT4分类测试失败，不是已发现的数据泄漏，也不是CUDA未被使用；主实验在拟合CT4之前已经停止。

## 复现范围

读取的训练角色是 `main/f0/shadowsocks/G0/i1/vless`：外层实际目标SS不参与该内层拟合，伪目标校准来自VLESS四类辅助业务，源部署为Trojan和VMess。GitHub仓库与YouTube搜索为伪目标未提供训练侧两侧数据的两类业务。

使用原封存训练视图、零初始化、原目标函数、原PyTorch版本与原LBFGS配置，全部数值运算使用CUDA float64。仅完成3次隔离诊断拟合：CT0控制1次，CT1失败任务重复2次。没有读取查询或评分包，没有写入正式模型，没有重启运行器，也没有修改原源码、失败记录和进度状态。

观察性Python跟踪记录了本机LBFGS实际执行的退出分支。该跟踪只记录控制流和标量，不改变优化器公式或参数。CT0复现与原正式模型参数最大差异为0；两次CT1复现参数最大差异也为0。

## 具体未通过的检查

| 指标 | CT0控制 | CT1第一次复现 | CT1第二次复现 |
| --- | ---: | ---: | ---: |
| 初始目标 | 1.791759469228055 | 1.791759469228055 | 1.791759469228055 |
| 最终目标 | 0.104161038617 | 0.091429113125 | 0.091429113125 |
| LBFGS迭代数 | 98 | 500 | 500 |
| 优化器函数评价次数 | 103 | 518 | 518 |
| 包含最终复核的closure调用数 | 104 | 519 | 519 |
| 最大原坐标梯度 | 6.9464×10⁻⁸ | 2.2676853×10⁻³ | 2.2676853×10⁻³ |
| 独立目标复核误差 | 5.55×10⁻¹⁷ | 0 | 0 |
| 独立梯度复核误差 | 7.05×10⁻¹⁷ | 1.78×10⁻¹⁵ | 1.78×10⁻¹⁵ |
| 实际退出分支 | 方向导数变化容差 | 迭代上限 | 迭代上限 |
| 原接受条件 | 全部通过 | 梯度与迭代两项不通过 | 梯度与迭代两项不通过 |

CT1最大梯度约为门限的226.8倍，不是小幅越界。其目标仍在下降，但“目标比初始低”不足以证明收敛。在不同训练视图上的CT0和CT1最终目标也不能直接拿来比较方法优劣。

本机PyTorch的 `max_eval` 未显式设置时为625；这次CT1只发生518次优化器函数评价，因此退出不是函数评价次数上限。500次迭代是一次 `optimizer.step(closure)` 内部的迭代，不是500次外层训练epoch。实现细节由本机源码核验，并与 [PyTorch v2.5.1 LBFGS源码](https://github.com/pytorch/pytorch/blob/v2.5.1/torch/optim/lbfgs.py) 相符。

## 输入尺度和曲率

CT1辅助槽直接使用源pre，却沿用真实post训练数据拟合的共享缩放器。部分分箱在post中变化很小，在pre中却占有较大比例，因此映射到原post标准化坐标后数值较大。

| 指标 | CT0 | CT1 |
| --- | ---: | ---: |
| 输入形状 | 336乘96 | 336乘96 |
| 全部输入有限 | 是 | 是 |
| 最大绝对输入值 | 13.820275 | 266.666185 |
| 最大按损失质量加权的二阶矩 | 1.219426 | 7642.070348 |
| 初始有效曲率最小特征值 | 约0.001 | 约0.001 |
| 初始有效曲率最大特征值 | 2.485289 | 7700.787767 |
| 初始有效曲率条件数 | 2485.289 | 7700787.767 |
| 小于10⁻¹²的正缩放标准差个数 | 0 | 0 |

这里的有效曲率是零初始化时、五个正交类别对比方向共享的97维 Hessian 块，包含96个特征与偏置以及原L2正则；排除了softmax共有偏置平移这一不可辨识方向。它不是把有零特征值的完整参数Hessian直接求条件数。

CT1初始曲率条件数约为CT0的3100倍，且初始最大梯度约6.93，CT0约0.233。配合固定预算重复失败，这强烈支持数值病态造成收敛困难的解释，但没有证明初始条件数能够完整解释后续全部迭代过程。

最大的分箱列为 `h01_03` 和 `h03_03`，对应 W_down 与 U_down 的 `[1024,4096)` 字节箱，最大绝对标准化值为266.666185，其post训练标准差为0.001199677。接下来还有上行包数、上行新字节事件数及方向段分箱的较大幅度差异，问题不只涉及一个字节量特征。

从允许的 `source-pre.parquet` 重新计算该CT1辅助槽，最大误差为0。两臂六类损失质量均为1/6。当前没有看到非有限输入、近零浮点标准差、辅助槽数值重构错误或类质量错误。

这些检查没有新增全数据集TCP身份审计，不能借此升级为“全部数据泄漏风险已经排除”。

## 工程问题与修复方向

现行运行器在质量门失败时正确停止，没有偷偷切CPU、扩预算或保存未合格模型。缺陷在于失败任务的优化数值和状态没有在抛异常前保存，导致第一次正式报错只给出组合门名称。

另一个问题是共同post统计缩放虽然满足实验对照要求，却不能保证原样pre辅助槽的数值条件适合同一默认LBFGS求解路径。直接改成每臂各自输入缩放、截断大特征或提高L2，都可能改变原分类目标或实验坐标，不应当伪装成纯日志修复。

优先候选是原目标等价的参数预条件化：改变优化器搜索参数的数值坐标，严格保留原损失、原L2、原post缩放、输入字段、标签权限和部署内容划分。接受时仍映回原W与偏置，并在原坐标检查梯度；新参数坐标的较小梯度不能代替原门限。

预条件化方案尚未训练验证，不承诺500次内一定通过。若工程试运行仍失败，应保留完整状态并请求新的数值方案或统一预算修订，不能继续隐式增加预算。

## 诊断产物

| 产物 | 链接 |
| --- | --- |
| 复现脚本 | [diagnose_optimizer_stop.py](F:/Program/VSCode/MyGit/ProxyAnalysis/eval/calibrated_deployment_transfer_analysis/diagnose_optimizer_stop.py) |
| 诊断结果 | [diagnosis.json](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/calibrated-deployment-optimizer-diagnosis-20261006/run-01/diagnosis.json) |
| CT0控制轨迹 | [CT0-control-closure-trajectory.parquet](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/calibrated-deployment-optimizer-diagnosis-20261006/run-01/CT0-control-closure-trajectory.parquet) |
| CT1第一次轨迹 | [CT1-failure-replay-1-closure-trajectory.parquet](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/calibrated-deployment-optimizer-diagnosis-20261006/run-01/CT1-failure-replay-1-closure-trajectory.parquet) |
| CT1第二次轨迹 | [CT1-failure-replay-2-closure-trajectory.parquet](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/calibrated-deployment-optimizer-diagnosis-20261006/run-01/CT1-failure-replay-2-closure-trajectory.parquet) |
| 修复计划 | [calibrated-deployment-optimizer-repair-plan-20261006.md](F:/Program/VSCode/MyGit/ProxyAnalysis/plan/calibrated-deployment-optimizer-repair-plan-20261006.md) |

本次3个拟合仅为异常复现，不纳入正式分类拟合数量，也不进入任何业务评分或模型选择。
