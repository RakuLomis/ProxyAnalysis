# 0914：配对价值重训练验证与业务补采前资格报告

日期：2026-09-15。仅使用 `TrafficTracer-Datasets-20260914`。

本报告对应补采前实施阶段。已完成部署配对结果的独立重训练、训练不确定性与敏感性实验，以及业务内容上界和索引配对审核。未采集新流量，未训练业务教师/学生模型，未合并其他批次。

## 1. 核心结论

1. 六种真实配对视图及两个代表性错配实验均被独立实现重新训练复现，选定 C 与预测概率一致。
2. 主口径的真实配对优势不是某一套内层 URL 划分或某一次训练 URL 抽样的偶然结果：Δ14、Δ17 的主要重复实验均保持正向平均优势。
3. 表示与包口径依赖仍存在。非空包 Δ17 的 URL 条件性区间继续跨零，不能写成无条件稳健。
4. 主队列未发现跨会话重复捕获或相同 TCP 元组下重复包/时间重叠证据；该审计不排除部署与环境混杂，也不覆盖全部 Hy2 原始捕获。
5. 当前业务独立内容不足。即使采用尚未合并别名的不同 URL 上界，52 个既有标签组也没有一组达到本设计的五内容工程门槛。业务训练停在资格门之前。

## 2. 实施量与数据单位

部署队列仍为 14 URL × SS/VLESS × 5 次访问 = 140 会话。一条模型样本是访问级聚合，不是单条 TCP flow，也不是一个包或截断窗口。

| 工作 | 实验任务数 | 实际模型拟合次数 |
|---|---:|---:|
| 六个真实视图＋两个代表性错配的独立参考训练 | 8 | 1,120 |
| 主口径内层划分 × 错配 | 260 | 36,400 |
| 主口径 URL 组训练重采样 | 240 | 33,600 |
| 非空包内层划分 × 错配 | 260 | 36,400 |
| 排除完整重传内层划分 × 错配 | 260 | 36,400 |
| 去除 IP 总字节量的次要敏感性 | 220 | 30,800 |
| 合计 | 1,248 | 174,720 |

每个任务包含 14 个外层折，每折内层 3 折 × 3 个 C，再拟合一个外层最终模型。拟合次数、种子数和重复预测数都不是独立样本量。没有借此扩大统计自由度。

环境检查：Pytorch312，Python 3.12.8，scikit-learn 1.6.1；未安装额外依赖。完整测试 142 项通过。首次全量测试因系统 pytest 临时目录权限产生 setup errors，使用确认不存在的项目内独立临时目录后全部通过。

## 3. 冻结与独立重训练

冻结了源清单、现有数据/代码哈希、配置、标量白名单及 420 条显式内层划分记录。所有新结果写入独立输出根，不覆盖已有 run-01。

参考实现未调用既有 evaluate、matrix、compare、预处理工厂或损失函数；重新实现标量/分布构造、转换、错配算法及训练循环。原始解析和保存的侧摘要仍共用；估计器仍为相同 sklearn LogisticRegression。因此这是同数据同算法的实现级复核，不是独立数据、不同模型族或外部复现。

| 视图 | macro-F1 | log-loss，bits | 与旧预测最大差异 |
|---|---:|---:|---:|
| pre 14 | 0.9212 | 0.411672 | 0 |
| post 14 | 0.8786 | 0.866909 | 0 |
| joint scalar 28 | 0.9356 | 0.229472 | 0 |
| Δ14 | 0.9714 | 0.101261 | 0 |
| joint distribution 314 | 1.0000 | 0.010355 | 0 |
| Δ17 | 1.0000 | 0.010923 | 0 |
| Δ14，代表性错配种子 | 0.9214 | 0.311068 | 0 |
| Δ17，代表性错配种子 | 0.9428 | 0.223989 | 0 |

旧预测只在重新拟合结束后读入作比较，未用于新拟合。所有选定 C 一致。代表性错配仅核对一个既有种子，不冒充对全部历史种子的独立实现复核。

## 4. 训练不确定性的实施方法

### 4.1 内层划分变化

外层固定留一 URL，训练侧 13 URL。生成 10 套随机但固定种子的内层三折 URL 分组，组数 4/4/5。所有表示使用共同划分。

每套划分运行六种真实视图；两个 Δ 视图分别运行 10 个错配种子。真配模型不因错配种子变化而重复计数。

错配保持同 URL × 部署内跨重复的双射与无固定点；内层训练、验证及外层训练、测试分别构造，映射不跨分区。预处理和调参在对应训练分区拟合。

### 4.2 训练 URL 组重采样

每个外层训练集中抽取 13 个 URL 组，有放回，重复 20 次。测试 URL 完全不参与抽样。每次使用固定内层分组种子和五个错配种子。

抽中的重复 URL 保留原始 group_id；先在唯一原始会话上构造配对，再按 URL 抽样次数扩展训练矩阵。内层验证损失同步体现组抽样权重。没有把同一会话副本当成新 donor，也没有让副本分散进入不同内层折。

### 4.3 不确定性解释

主要量 G = CE(错配) − CE(真配)。正值代表真实对应具有较低预测损失。

算法组合的分布用于训练敏感性描述，不作为总体置信区间。另将每个 URL 在已完成训练组合中的平均 G 作为该 URL 的贡献，对 14 个 URL 做 5,000 次 bootstrap。下表区间是条件于已完成重拟合模型集合的 URL 区间，不是联合涵盖全部训练随机性、模型选择历史和外部环境变化的区间。

## 5. 主要结果

| 实验口径 | 标量变换平均 G | 分布增强变换平均 G | 两种表示的正向算法组合 |
|---|---:|---:|---:|
| observed，改变内层划分 | 0.2828 | 0.2349 | 均 100/100 |
| observed，训练 URL 组重采样 | 0.2597 | 0.2121 | 均 100/100 |
| nonempty，改变内层划分 | 0.1848 | 0.1185 | 均 100/100 |
| 排除完整重传，改变内层划分 | 0.2422 | 0.2257 | 均 100/100 |
| 去除 ip_bytes，改变内层划分 | 0.2858 | 0.2312 | 均 100/100 |

单位 bits。前四行是 Δ14/Δ17；去除 ip_bytes 后实际为 13/16 维，输出中的 delta_scalar/delta_distribution 是视图类型名，不代表仍有 14/17 个输入。

### 5.1 URL 级条件性区间

| 口径 | 标量：G 的 95% 条件性区间 | 分布增强：G 的 95% 条件性区间 | URL 平均贡献为正：标量/分布 |
|---|---|---|---|
| observed，改变内层划分 | [0.1015, 0.5076] | [0.0649, 0.4449] | 14/14；14/14 |
| observed，训练组重采样 | [0.1004, 0.4793] | [0.0712, 0.3892] | 14/14；14/14 |
| nonempty | [0.0478, 0.3561] | **[-0.0317, 0.3129]** | 12/14；12/14 |
| 排除完整重传 | [0.0955, 0.4090] | [0.0704, 0.4123] | 13/14；14/14 |
| 去除 ip_bytes | [0.1005, 0.5188] | [0.0647, 0.4358] | 14/14；14/14 |

这不是“非空包结果已被新实验挽救”。它再次表明：固定这 14 个 URL 改变训练设置时，平均优势可以稳定为正；但 URL 间异质性仍然足以使 Δ17 的 URL 区间跨零。

### 5.2 是否由单个 URL 驱动？

observed 主口径中 Example 与 GitHub 贡献较大。例如 Example 的 Δ14/Δ17 URL 平均 G 分别为 1.3225/1.1707 bits。

但从主口径 14 个 URL 中删除任意一个，再计算剩余 URL 的平均贡献，最小值仍分别为 0.2028/0.1629 bits。总体优势并非完全依赖一个 URL；这不等于所有 URL 的效应大小相近，也不是经过删除 URL 后独立重新拟合的实验。

非空包下负向 URL：Δ14 为 MDN HTTP 文档和 TradingView；Δ17 为 Unsplash 和 TradingView。尤其 Unsplash 的 Δ17 平均贡献约 −0.4063 bits，不能只汇报总体正向均值。

## 6. 输入与原始连接审计

### 6.1 输入

新阶段通过白名单构造输入，未输入 IP/MAC 地址、端口、SNI、domain、路径、会话 ID 或绝对时间。标量输入的元数据扰动检查保持矩阵不变；分布参考实现显式读取直方图与归一化曲线。

ip_bytes 是 IP 层总字节量，不是 IP 地址。去除此列后优势接近原结果，说明主配对结果不单独依赖这一列。其他流量特征仍可能携带路径、拥塞、部署参数等间接线索，不能据此宣称环境影响已排除。

此前 broad 旧模型的 captured_bytes 派生字段问题没有在本轮被修订重跑；本轮未沿用该模型，也不将其旧结果作为新的无链路层输入证据。

### 6.2 原始捕获身份

主 140 会话中：

- 1,711 个通过既有排他 TCP 规则的配对；两侧合计 3,422 个捕获记录。
- 跨会话相同捕获路径或文件哈希组为 0。
- 49 组跨会话 TCP 元组复用比较，时间重叠为 0，时间戳＋原始包字节身份交集为 0。
- TCP 初始 SYN 与序号比较细节已经保存，不把端口复用直接认定为同一连接。
- 审计执行错误为 0。

这一结果不支持“同一 flow 被切开混入训练/测试”作为当前主队列高性能的解释。范围仅为本轮主队列，且不能替代对环境混杂、页面边界选择依赖或其他潜在泄漏渠道的检查。

## 7. 全部业务访问的资格检查

### 7.1 审核范围与四道门

审核全部 462 个选定访问；140 主队列之外的访问没有自动判为配对失败。

必须区分：标签有效 → 独立内容充足 → 排他配对索引和文件可用 → 提取质量与合法业务划分通过。

当前完成了既有标签证据的继承、不同 URL 内容上界、SS/VLESS 排他配对索引/文件存在性复核。没有完成所有候选业务访问的重新特征提取、完整捕获质量审核和非视频业务的人工语义定类。因此下文使用“索引配对候选”，不写成全部合格的业务样本。

### 7.2 配对索引复核

| 状态 | 会话数 |
|---|---:|
| SS/VLESS：存在合格排他 TCP 索引与文件 | 235 |
| SS/VLESS：没有合格排他 TCP 配对 | 73 |
| Hy2：不适用当前严格 TCP 配对设计 | 154 |

235 不是业务合格样本数。业务执行标签和特征质量还需分别成立。Hy2 不适用不是缺包或需要补五个内容；修正版缺口表已将其严格 TCP 补采缺口设为不适用。

### 7.3 视频业务

| 业务 | 部署 | 已确认标签访问数 | 视频 URL 上界 | 索引配对候选访问 | 候选 URL 上界 |
|---|---|---:|---:|---:|---:|
| Bilibili 视频播放 | SS | 7 | 2 | 1 | 1 |
| Bilibili 视频播放 | VLESS | 7 | 2 | 4 | 1 |
| YouTube 视频播放 | SS | 6 | 1 | 6 | 1 |
| YouTube 视频播放 | VLESS | 6 | 1 | 6 | 1 |

Bilibili 仍按用户确认保留正片播放有效性，不能回退为“没有正式播放证据所以全部无效”。但标签有效不等于严格配对成立。

YouTube 的六次访问含 broad 与 repeat 对同一登记视频的访问，不是六个视频。Bilibili 的不同视频中，目前每部署仅一个 URL 有索引配对候选；若已有另一个视频重新采集后满足配对，也可增加可用内容，不一定全部都要换成新视频。

按每类别五个独立严格配对内容的工程设计，SS/VLESS 两个视频业务均至少还缺四个可用内容位置。这里是最乐观下界，不是最终采集任务单：现有候选进一步质量审查失败会增加缺口，协议间内容还需交集对齐。

### 7.4 为什么业务训练暂停？

当前 52 个既有 domain × activity 标签组，在不同 URL 上界层面均不足五个。合并同内容别名、将 page_load 细分为真实业务后，不会凭空增加内容。

五内容门槛来自本设计的外层留出和教师交叉拟合：每类外层留一个内容，训练侧四个内容分两折，每个教师留出折至少两个内容，才能实现教师均未见过 donor/receiver 的跨内容错配。它是合法划分的工程条件，不是样本量或统计功效充分的保证。

因此没有运行四臂业务模型，没有随机拆重复访问制造“未见内容”结果，也没有产生 post-only 业务收益数字。

## 8. 已交付文件

配置：[paired-value-next-stage-0914.yaml](F:/Program/VSCode/MyGit/ProxyAnalysis/configs/paired-value-next-stage-0914.yaml)。

可复用实现：

- [冻结与业务初筛入口](F:/Program/VSCode/MyGit/ProxyAnalysis/src/proxy_analysis/paired_information/next_stage.py)
- [独立标量重训练](F:/Program/VSCode/MyGit/ProxyAnalysis/src/proxy_analysis/paired_information/reference_retrain.py)
- [独立分布与错配复核](F:/Program/VSCode/MyGit/ProxyAnalysis/src/proxy_analysis/paired_information/reference_distribution.py)
- [URL 划分与组重采样](F:/Program/VSCode/MyGit/ProxyAnalysis/src/proxy_analysis/paired_information/uncertainty.py)
- [原始捕获与索引配对审计](F:/Program/VSCode/MyGit/ProxyAnalysis/src/proxy_analysis/paired_information/input_audit.py)
- [IP 总字节量敏感性](F:/Program/VSCode/MyGit/ProxyAnalysis/src/proxy_analysis/paired_information/ip_volume_ablation.py)
- [最终汇总入口](F:/Program/VSCode/MyGit/ProxyAnalysis/src/proxy_analysis/paired_information/next_stage_report.py)

新输出根：`outputs/paired-value-next-stage-0914/run-01/`。最终汇总以 **report-v2** 为准；第一版 report 保留用于追踪，但其 Hy2 缺口字段已由 v2 的“不适用”替代。训练结果未变。

- [最终机器可读摘要](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/paired-value-next-stage-0914/run-01/report-v2/summary.json)
- [URL 贡献表](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/paired-value-next-stage-0914/run-01/report-v2/url-contributions.parquet)
- [URL 稳定性与条件性区间](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/paired-value-next-stage-0914/run-01/report-v2/url-stability.parquet)
- [全部业务访问资格表](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/paired-value-next-stage-0914/run-01/report-v2/business-session-eligibility.parquet)
- [业务内容缺口表](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/paired-value-next-stage-0914/run-01/report-v2/business-content-deficits.parquet)
- [原始流审计摘要](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/paired-value-next-stage-0914/run-01/raw-and-pair-audit/result.json)

每项重训练另有 OOF、调参记录及配对映射。主/非空/去重传/训练组重采样执行器支持带哈希验证的完成任务恢复；独立参考和 IP 消融入口拒绝覆盖已有输出。不要将再次读取完成缓存称为重新训练。

PowerShell 示例（首次运行时输出目录必须不存在）：

```powershell
$env:PYTHONPATH = 'src'
& D:/Tools/Anaconda/envs/Pytorch312/python.exe -m proxy_analysis.paired_information.next_stage --mode freeze
& D:/Tools/Anaconda/envs/Pytorch312/python.exe -m proxy_analysis.paired_information.next_stage --mode reference
& D:/Tools/Anaconda/envs/Pytorch312/python.exe -m proxy_analysis.paired_information.next_stage --mode business
& D:/Tools/Anaconda/envs/Pytorch312/python.exe -m proxy_analysis.paired_information.reference_distribution
& D:/Tools/Anaconda/envs/Pytorch312/python.exe -m proxy_analysis.paired_information.input_audit
& D:/Tools/Anaconda/envs/Pytorch312/python.exe -m proxy_analysis.paired_information.uncertainty --mode partitions
& D:/Tools/Anaconda/envs/Pytorch312/python.exe -m proxy_analysis.paired_information.uncertainty --mode bootstrap
& D:/Tools/Anaconda/envs/Pytorch312/python.exe -m proxy_analysis.paired_information.uncertainty --mode partitions --selection nonempty
& D:/Tools/Anaconda/envs/Pytorch312/python.exe -m proxy_analysis.paired_information.uncertainty --mode partitions --selection exclude_full_retransmission
& D:/Tools/Anaconda/envs/Pytorch312/python.exe -m proxy_analysis.paired_information.ip_volume_ablation
& D:/Tools/Anaconda/envs/Pytorch312/python.exe -m proxy_analysis.paired_information.next_stage_report --report-name report-v2
```

以上为执行顺序记录，不应直接在已有输出上完整重复执行。需要真正新的完整重训练时，应先建立新配置/输出根并冻结新契约；少数当前入口仍固定默认配置路径，需要显式扩展 CLI 参数后重新冻结，不能声称任意数据集已一键通用。

## 9. 当前停止点与论文表述

部署主线的内部补强已完成。可以加强表述为：在所观测的 SS/VLESS 部署、严格配对队列和给定表示口径下，同次访问对应的预测价值在 URL 分组调参与训练组重采样下保持；主口径优势不是单个 URL 或单次调参结果造成的。

不能增加的主张：部署混杂已排除、变换可逆、业务语义解耦、真实互信息大小、post-only 业务收益、在线原始流量选择已闭环或未见环境泛化。

下一关键节点是确认补采的业务标签、独立内容和协议覆盖，或明确缩窄到已知内容重复访问问题。非视频 page_load 的细分语义仍需确认；所有候选业务捕获的完整质量复核也尚未完成。此阶段不擅自新增采集或替用户选择新业务内容。
