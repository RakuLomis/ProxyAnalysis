# JAT1 显卡利用率与CUDA工程验收报告

日期：2026-10-16。完成训练核心实现、780角色资产登记、源内数值验收与显卡观测。正式业务矩阵尚未启动，未读取query数值/标签、实际H/U、native或PCAP。

## 实测结果

显卡为RTX 4060 Ti，显存16380 MiB。以下是相邻时间窗口的真实CUDA训练计算，重复使用12个固定合法源内任务，不是空矩阵或分配显存的占位负载。

| 路径 | 模型并发 | 模型更新每秒 | GPU忙碌均值 | PyTorch峰值MiB | 整卡峰值MiB | 样本数 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| independent-8-eager | 8 | 382.3 | 36.0% | 1608.0 | 2800 | 8 |
| independent-32-graph | 32 | 2108.5 | 100.0% | 1738.6 | 2934 | 9 |
| streams-32-graph | 32 | 8822.6 | 87.9% | 1930.6 | 3142 | 32 |

8-stream、32个独立模型加CUDA Graph的实测吞吐是普通执行的约 **23.08倍**。32模型持续观测 32.64 秒，累计 288000 次模型更新；每个探针块最多1000步，块间复原初值和Adam状态，不导出正式模型或业务评价。

观测基线整卡GPU忙碌均值为 5.57%。nvidia-smi是整卡时间忙碌比例，含Windows桌面及其他进程，不是本进程SM occupancy或理论FLOPS。更高的GPU百分比不一定更快；本轮以合法更新吞吐为主要性能依据。

## 为什么不把16GB显存填满

模型仅2318个参数，当前真实训练槽480行。显存占用主要是数据、CUDA工作区、图及自动微分缓冲，而非参数本身。先前批大小扫描中，多stream的8/32/64/128模型吞吐依次约为 7929, 8099, 7599, 7539 次模型更新/秒；扩大到64、128没有继续加速，却提高了显存占用。

因此推荐32模型、最多8个CUDA streams，并缓存合法源内输入。保留余量比重复堆数据或空缓存更有意义。PyTorch allocated/reserved与整卡显存分别记录，不能把nvidia-smi的memory utilization当作容量使用比例。当前还没有测量SM占用率、显存带宽峰值或理论算力利用率，不能说已达到硬件峰值。

## 数值资格与保留的失败

独立CUDA Graph及多stream路径通过原计划的参数/Adam前缀门。当前选定32模型规模全部模型在1/10/100步与独立执行比较通过，最大参数差 0.000e+00，Adam差 0.000e+00；两种冻结续训的参数和冻结Adam状态保持不变。

张量化BMM路径未通过门限，因而未用于性能推荐或正式训练。它在float32分支的不同数值路径造成后续float64头参数偏差，不能为追求速度把门限放宽。失败详情保留在numeric-01/02/03/04中。

numeric-02还出现两项工程记录问题：多stream检查点误把独立Adam矩当成堆叠矩切片；再次发布时尝试覆盖旧latest记录。修订仅涉及状态导出和版本索引。其失败记录未覆盖；修订后的numeric-03/04重新验收。冻结参数的Adam状态保留接口也已纳入numeric-04及32模型复核。

## 已实现与尚未执行

已实现完整可训练W/V/c/G、原带权分类与关联目标、实际输出单位L2、独立模型优化器/clip、两种冻结继续、检查点继承、CUDA Graph与多stream、训练数据权限适配器、数值测试及遥测。

未执行720源内完整选择、60外层角色训练、H预测或业务评分。完整P2至P5调度和评分程序尚未封存为可执行实验，当前CLI只提供register/tests/profile，不能把训练核心完成写成全方案实施完成。

下一步先完成固定12任务P1工程先导，并实测2000步、中点分叉及928行外层规模，再冻结全矩阵执行版本。按本次内层稳态吞吐简单折算24480000次源内更新约 0.77 小时；它不包含图准备、IO、外层、教师和审计，也没有测量所有λ/lr/冻结模式，不能当作整轮完成时间承诺。

## 产物与复核

- 当前32模型复核与长窗口观测：`outputs/joint-associated-post-classifier-20261016/run-01/engineering/occupancy-01`。
- 原始显卡样本：`sustained-nvidia-smi.json`，包含每秒采样、窗口标签与整卡范围说明。
- 批大小扫描：`outputs/joint-associated-post-classifier-20261016/run-01/engineering/gpu-02/summary.json`。
- 最终核心资格：`outputs/joint-associated-post-classifier-20261016/run-01/engineering/numeric-04/qualification.json`。
- 实现：`eval/joint_associated_post_classifier/`；独立复核脚本位于`eval/joint_associated_post_classifier_gpu_analysis/`。

这是性能与工程报告，不包含任何新F1、CE或Brier实验结论。
