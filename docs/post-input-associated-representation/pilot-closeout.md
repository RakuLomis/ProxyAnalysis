# post关联分支工程先导停止说明

日期：2026年10月14日。当前停止在P1多头训练数值重放门，未进入正式源内矩阵或业务评价。

## 已完成内容

P0的780任务全部通过：480访问、30内容、23566连接的来源绑定与每角色合法过滤、可信父访问配对恢复、两侧直方图和pre独立袋多重集合重放、原P-small目标与梯度审核完成。60外层及720源内基座均复用，新LR拟合为0。P0耗时788.193秒。

P1的11项检查全部通过：零初始化的logits、log-prob、概率和决策精确相同；CE可以更新残差头；起点CE对G梯度为0符合零头定义；组中心平方损失恒等式和置乱不变；权限负例；H提前读取拒绝；1560项父任务/模型绑定。检查耗时213.153秒。

Pytorch312运行PyTorch 2.5.1、CUDA 12.4，RTX 4060 Ti；工程拟合实际在CUDA执行。

## 先导为何停止

固定1000步A1训练，先独立训练一个任务，再在独立双头批次中训练同一任务和另一个任务。终态概率/logit比较没有满足以下合取门：

- 最大概率绝对差不超过1e-5。
- 最大logit绝对差不超过1e-4。

这不是新的业务负结果，也不是已确认的数据泄漏。当前只能确定新GPU批处理实现尚未获得与单头一致的资格，不能直接把差异归因于ReLU、FP32舍入、优化器或共享梯度中的某一项。

原先导在保存误差数值与终态张量之前触发异常，所以pe/le具体数值及其分布没有落盘，不能事后猜测哪一项、超出多少。后续独立重放必须先保存初始状态、逐阶段误差和终态，再执行门判定。

实际已执行三个工程残差拟合，每个1000步：一次单头和一次双头。由于原计数更新在失败门之后，原ledger没有加这三次；[补充结项记录](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/post-input-associated-representation-20261014/run-01/pilot/closeout.json)明确保留这个计数缺口，不覆盖原日志。训练墙钟计费为10.757秒，已进入原预算。教师、正式残差和新LR拟合均为0。

## 下一项有限工程修订

建议独立版本只修验收记录和批处理数值接口，不更改教师、分支、lambda、L2、1000步、标签、数据权限或误差门：

1. 复用已通过P0的780训练包及基座，按其封存哈希审核，不重扫PCAP、不重新配对。
2. 先保存单头/多头初始参数，检查同seed初始化、输入、标签和质量完全一致。
3. 对相同合法任务保存第1、10、100、1000步的logits、损失分项、每头梯度/限幅和Adam状态，定位第一次分歧。
4. 若是批量尺寸改变了算术路径，采用固定逐头算术或经验证的稳定分组后端；若是实现错误，修错误。保持每头独立训练与原目标，不放宽门。
5. 新工程先导通过后，重新测吞吐量；预计超过9.6小时则请求预算决定，不能直接改成单头跑完整矩阵。

run-01及其停止保持封存。新版本不得把本次未验收结果标为通过，不从失败终态接着训练，也不自动启动Stage B。

## 产物

- [P0审计](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/post-input-associated-representation-20261014/run-01/audits/P0-complete.json)。
- [CUDA单元检查](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/post-input-associated-representation-20261014/run-01/audits/unit-tests.json)。
- [原停止状态](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/post-input-associated-representation-20261014/run-01/completion.json)。
- [实施代码](F:/Program/VSCode/MyGit/ProxyAnalysis/eval/post_input_associated_representation/README.md)。
