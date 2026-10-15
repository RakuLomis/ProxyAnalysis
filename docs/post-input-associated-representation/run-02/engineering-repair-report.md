# post关联分支批处理数值接口修订报告

日期：2026年10月14日。独立工程修订完成，P1通过；正式Stage A已继续到P2。原run-01停止保留，不改判为通过。

## 修订范围

只改变工程记录和批处理数值接口。原模型维度、ReLU、参数数量、损失、质量、L2、Adam超参数、1000步、seed、lambda候选、源内启用门、数据权限和预算门保持不变。新合同核对了31个原科学字段全部相同。

780个已通过P0的训练包和基座通过封存哈希复用，没有重扫PCAP、重新配对或重新拟合LR。run-01原代码保持只读；v2保存独立旧接口诊断，v3提供稳定接口和正式执行。

## 新增旧接口重放记录

这是新执行的独立诊断，不是补造run-01丢失的误差。已保存初始参数、输入、标签与质量，以及第1、10、100、1000步的参数、logits、损失分项、限幅前后梯度和Adam状态。

| 步数 | 最大参数差 | 最大logit差 | 最大概率差 | 最大限幅前梯度差 |
| --- | ---: | ---: | ---: | ---: |
| 0 | 0 | 0 | 0 | 不适用 |
| 1 | 1.15575e-5 | 5.14314e-6 | 1.34445e-6 | 6.58474e-10 |
| 10 | 5.58887e-6 | 3.56138e-6 | 1.29826e-6 | 3.51429e-9 |
| 100 | 2.35686e-4 | 3.72203e-7 | 4.65697e-8 | 5.84787e-9 |
| 1000 | 2.37698e-4 | 1.06557e-3 | 4.03002e-4 | 1.26658e-6 |

初始化及输入相同，差异已经在第一次反向与更新出现。初始目标值相同不等于梯度算术相同；微小梯度差可以影响近零梯度下的Adam轨迹。本诊断没有用任何H或实际目标U解释这些差异。

## 稳定接口与原门限验收

每个头采用独立参数对象、同形状CUDA线性运算、独立损失归约、反向图和梯度限幅。Adam仍以同样超参数更新各头独立状态，不共享参数或业务监督。批次接口仍容纳多个模型，但不将不同头合并为依赖批次大小的矩阵和归约算术。

P1原11项零初始化、容量、组损失、权限及血缘检查再次通过。相同固定1000步的单头与双头重放结果为：

| 验收项 | 原门限 | 新结果 |
| --- | ---: | ---: |
| 最大logit绝对差 | 1e-4 | 0 |
| 最大概率绝对差 | 1e-5 | 0 |
| 类别变化 | 记录 | 0 |

没有放宽门限、修改模型容量或改为较短训练。新重放明细在执行判定前已经保存，失败也会留下完整记录。

独立只读复核进一步确认：初始输入、标签与质量精确相同；第1、10、100、1000步的参数、logits、梯度及Adam第一矩在两个执行方式间均精确相同。原停止文件、旧账本以及旧/新代码快照哈希未变。该复核没有新增拟合。

## 九任务先导与预算

固定九个合法源内任务完成九份教师和45份分支拟合，没有按效果挑选任务。CUDA为RTX 4060 Ti；训练、教师和数值推理仍在CUDA执行。

| 项目 | 测量 |
| --- | ---: |
| 九教师总时间 | 8.159秒 |
| 32独立头批次 | 51.230秒 |
| 13独立头批次 | 20.855秒 |
| 较慢批次每头耗时 | 1.604秒 |
| 预估训练总时间 | 7.865小时 |
| 启动门 | 9.6小时 |
| 训练安全上限 | 12小时 |
| 先导CUDA峰值分配 | 99.191 MiB |

外推采用原上界模型数并乘1.5的额外开销系数，属于当前设备的估计，不是完成时间承诺。IO、最终预测和bootstrap另行计费。原失败训练10.757秒计入新预算；旧接口独立诊断和新工程重放各三个拟合，分别计数。尚未执行的角色不能按预算原因默认为回退。

## 后续执行

P2完成全部720个合法源内任务，再封存180个启用/回退决定；随后P3封存全部最终模型，P4才打开H-post。全部H预测封存后才读取H标签评分。

当前仍没有业务F1或配对收益新结论。P1通过确认的是数值接口及预算可执行性。GAN/Stage B没有授权，不会自动启动。

## 证据入口

- [独立修订范围](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/post-input-associated-representation-20261014/run-02/manifests/repair-scope.json)。
- [旧接口独立诊断](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/post-input-associated-representation-20261014/run-02/pilot/legacy-diagnostic.json)。
- [新接口重放](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/post-input-associated-representation-20261014/run-02/pilot/batch-replay.json)。
- [保存轨迹的独立复核](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/post-input-associated-representation-20261014/run-02/pilot/repair-record-verification.json)。
- [CUDA先导预算](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/post-input-associated-representation-20261014/run-02/pilot/summary.json)。
- [实时进度](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/post-input-associated-representation-20261014/run-02/progress.json)。
- [执行入口](F:/Program/VSCode/MyGit/ProxyAnalysis/eval/post_input_associated_representation_v3/run.py)。
