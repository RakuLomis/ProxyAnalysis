# 0914数据最新实验结果详细报告

报告日期：2026-09-15。范围：仅 `TrafficTracer-Datasets-20260914`，截至敏感性与采集执行诊断完成。

本报告整合0914已完成的测量/统计基础、最新配对信息实验及其敏感性检查。不引入此前数据集的数值比较，不包含新流量采集、业务分类训练或业务蒸馏。本报告是当前综合入口；早期阶段报告中的“尚未执行错配/敏感性”等历史状态由本文更新。

## 摘要

当前最重要的成果，不是又得到一个较高的部署分类F1，而是把三个问题区分开并补上了对应证据：

1. **部署辨识性：** pre、post及其变换表示均携带部署相关的可预测结构；pre并非天然与部署无关的“纯语义视图”。
2. **精确配对价值：** 在相同URL、相同部署内跨重复打乱pre/post后，分类仍然较强，但预测损失明显增大。真实配对在当前主队列与部分敏感性口径下提供额外预测价值。
3. **单侧恢复与业务有效性：** 部分Δ可以被当前post特征有限恢复，效果依赖目标与模型；尚未验证配对信息能改善业务Y的post-only分类。

主实验使用14个URL、SS/VLESS两个部署、各5次重复，共140个会话。Δ17真实配对的log-loss为0.0109 bits，100次错配平均为0.2354 bits；真实配对损失优势为0.2244 bits，URL级条件性95%区间为[0.0634, 0.4327]。但是，仅保留非空包时，该优势区间跨零，不能概括为对所有包选择口径无条件稳健。

双侧分布普通拼接同样达到F1=1，说明不能把Δ相对单侧的改善解释成Δ独有的信息优势。训练侧调参及强相关量剔除改善了部分Δ恢复，进一步否定了“固定ridge失败，所以信息不存在”的推断。

## 1. 数据范围与样本单位

### 1.1 唯一数据来源

原始数据仅来自：`Datasets/TrafficTracer-Datasets-20260914`。

| 数据组 | 目标 | 部署 | 每目标每部署重复 | 选定会话 | 存储尝试 |
|---|---:|---:|---:|---:|---:|
| broad：sites-64url-repetition-1 | 64 URL、50 domain | SS/VLESS/Hy2 | 1 | 192 | 194 |
| repeat：sites-detailed-18url-repetition-5 | 18 URL | SS/VLESS/Hy2 | 5 | 270 | 270 |
| 合计 | 两组目标有重叠，不直接相加为独立内容数 | — | — | 462 | 464 |

重复次数、分流连接数、包数、错配种子数与OOF记录数都不是独立内容样本数。broad的额外2次尝试只参与尝试审计，不混入选定主数据。

### 1.2 最新机制实验主队列

主队列使用repeat中的SS/VLESS、`exclusive_page`、`observed`口径，要求同URL形成完整部署×五轮网格，并满足既有路由、质量和特征可用条件。重建后为：

`14 URL × 2部署 × 5轮 = 140会话`。

14个目标domain为：arxiv.org、bing.com、cloudflare.com、developer.mozilla.org、example.com、github.com、openstreetmap.org、rottentomatoes.com、tradingview.com、unsplash.com、vimeo.com、weather.com、wikipedia.org、youtube.com。这里每个domain对应本队列中的一个目标URL，不表示抽样覆盖该网站的全部内容。

完整网格筛选有助于可比性，但结论条件于这个被筛选的队列，不能外推到全部失败、缺失或无法严格配对的访问。Bilibili未进入该队列的原因见第12节。

### 1.3 三种观测层级不能混淆

- **broad部署分类：** 三个部署标签，网站分组评估；不是业务分类。
- **repeat双侧机制分析：** SS/VLESS严格页面聚合，保留原始实体内边界。
- **Hy2：** 共享carrier/context范围，不能当作页面专属外层流量，与前两者分开解释。

现有post特征可能依赖离线索引和双侧关联确定哪些流量属于目标，因此保留 `offline_index_assisted_post` 观测声明。分类器只输入post数值，不等于已经实现未知活动边界下的在线混合流量识别。

## 2. 已提取特征与本轮实际输入

### 2.1 已有特征基础

0914复现产物已覆盖：方向/带符号长度/IAT序列，长度和IAT分布，上下行包数与字节量，方向burst，TCP FR与归一化FR，方向转移及熵，累计流量形状，pre/post比值与差值，分布距离，页面连接/并发/共享信息，以及已有TCP与active/idle扩展。

基础字段由项目解析，统计特征由自有实现计算，不依赖Wireshark内置统计量。IP、端口、域名、URL等用于关联、标签或分组，不进入主模型。本轮未新增SNI解析，也没有以SNI确定CDN供应商、出口服务器或PoP。

### 2.2 代表指标的口径

| 家族 | 本轮代表量 |
|---|---|
| workload | packet_count、transport_bytes、ip_bytes、up_transport_bytes、down_transport_bytes |
| interaction | burst_count、fr_runs、fr_switches、fr_runs_per_packet |
| direction | up_byte_fraction、transition_p_pm、direction_entropy |
| packetization | length_median；双侧距离length_js |
| timing | iat_median_us；双侧距离iat_js |
| cumulative | cumulative_l1 |
| entity/multiplexing | entity_count：登记/质量和变换统计使用，不进入本轮14维单侧模型 |

长度主口径为transport payload，IP长度为另一统计量，不能直接等同应用有效字节。IAT在实体内计算，不跨不相关连接串接。burst和FR保持原有连接边界后汇总；累计曲线按既有聚合契约计算。

FR-runs计数包含第一个非空方向段，FR-switches为非空方向切换次数，两者不能混称。归一化FR采用既有非空包分母。UDP方向反转不自动等价于原TCP FR。

对于严格正的计数量：`Δ = ln(post/pre)`；比例类采用差值；JS采用base 2；累计L1为归一化曲线平均绝对差。零比值操作数不以任意常数替代，保留缺失原因，伪计数仅在明确的辅助口径使用。

### 2.3 四视图展开为六组实验

| 视图 | 维数 | 信息来源与用途 |
|---|---:|---|
| pre | 14 | 单侧代表量 |
| post | 14 | 单侧代表量 |
| joint_scalar | 28 | 同14对单侧量直接拼接 |
| delta_scalar | 14 | 由同14对标量计算Δ，适合标量信息来源匹配比较 |
| joint_distribution | 314 | 双侧标量、归一化直方图和累计曲线 |
| delta_distribution | 17 | 标量Δ14加length JS、IAT JS、累计L1 |

314维拼接与Δ17源自对应双侧分布信息，但维数、压缩方式和模型参数规模不同，不能称为容量完全匹配实验。Δ17与joint_scalar28的信息来源并不相同：三个分布距离无法仅从标量中位数恢复。

## 3. 0914已有统计基础：本轮研究的出发点

本节引用同一0914数据的既有结果，说明背景；不是本次错配实验重新估计的变换中心。此处有效URL数与最新140会话分类队列按不同规则筛选，不能直接视为同一cohort。

### 3.1 变换中心与重复性

以下百分比是每URL的重复Δ均值，再跨URL取中位数并指数变换；不是整个数据集的总包数/总字节比。

| 部署 | 指标 | 有≥3轮的URL | 中心变化 | 重复MAD中位数（log尺度） | ICC(A,1) | ICC完整URL |
|---|---|---:|---:|---:|---:|---:|
| SS | packet_count | 14 | +64.44% | 0.05664 | 0.7241 | 14 |
| SS | transport_bytes | 14 | +1.73% | 0.00148 | 0.6810 | 14 |
| SS | burst_count | 14 | +83.91% | 0.04962 | 0.7872 | 14 |
| SS | fr_runs | 14 | +3.29% | 0.00430 | 0.4054 | 14 |
| VLESS | packet_count | 16 | +26.24% | 0.04845 | 0.8707 | 15 |
| VLESS | transport_bytes | 16 | +6.95% | 0.00190 | 0.9633 | 15 |
| VLESS | burst_count | 16 | +14.19% | 0.03333 | 0.8331 | 15 |
| VLESS | fr_runs | 16 | +24.53% | 0.01186 | 0.7788 | 15 |

SS的“packet增加、burst增加、bytes在既有等效范围内”联合profile为12/14 URL，去首轮后仍12/14。等效范围沿用post/pre∈[0.9,1.1]及既有判定，不改成新采集草案未确认的±5%。

不能仅按ICC高低排序绝对稳定性。例如SS FR的ICC低于VLESS，但其重复MAD也更小；ICC还受URL之间差异影响。总传输字节近似保持，也不等于已经证明业务语义保持。

### 3.2 部署间变换分离

| 指标 | 完整共同URL | S_local | S_global | 既有BH q |
|---|---:|---:|---:|---:|
| packet_count | 14 | 4.933 | 2.061 | 0.0144196 |
| fr_runs | 14 | 11.700 | 9.050 | 0.000439453 |
| length_js | 14 | 24.309 | 22.882 | 0.000313895 |

S是部署间变换差异相对部署内重复波动的描述性比值，不是因果强度、互信息或配对价值检验。上述q来自先前变换统计，不是本轮错配实验的p值。

### 3.3 broad三部署分类仍是另一项任务

| 特征/模型 | mean-fold macro-F1 |
|---|---:|
| A-core 235维 logistic | 0.7962 |
| packetization+timing 61维 logistic | 0.7967 |
| FR-only logistic | 0.6797 |
| A-core去reversal logistic | 0.7849 |
| A-core random forest | 0.7651 |
| A+B 961维 random forest | 0.8089 |

这些是5折×5次外层评估的fold均值，不能和本轮140会话二分类的pooled OOF F1直接比较。0.7967与0.7962的接近不等于显著优劣；FR具有单独辨识力，其增量依赖其他特征和模型。

VLESS资源级burst仍保留scope警告：strict中位log-ratio=0，weighted≈0.1029（+10.84%）。页面级+14.19%不能替代资源strict结论；中位为零不证明等效。

## 4. 最新实验方法与防泄漏规则

### 4.1 分组与模型

主划分为LOUO：留出整个URL及其两部署全部重复，训练与测试URL不重合。训练内使用3折GroupKFold调参，logistic的C候选为[0.1,1,10]，按训练侧验证损失选择。填补和标准化都只在相应训练折拟合。

LOUO检验的是部署标签C的未见URL辨识，不能解释为domain×activity业务任务的未见类别泛化。LORO旧基线仍保留，但新错配主任务不使用其单例测试层。

### 4.2 错配方式

在同URL、同部署、同当前分区内，跨不同重复访问，对pre做无固定点的一一置换，post保持不变：

`Δ_wrong[i] = Ψ(pre[donor_i], post[i])`。

每个donor与receiver都保留真实身份。外层训练/测试、内层训练/验证分别重配对；不能先全局置换再切折。全部标量Δ、JS和累计L1均从新组合重算，不是交换已经算好的Δ值。

repeat的LOUO测试保留同URL多轮，能够错配；LORO测试每URL×部署通常只有一条，无法合法跨重复错配，不从训练集借pre。broad的单次访问也不用于该错配对照。

### 4.3 不确定性与任务预算

- 主对照100次错配，保存100种唯一全局映射配置。
- 三种敏感性各20次错配；双向扰动每种方向20次、两种Δ表示。
- URL级bootstrap 1,000次。先按会话平均不同错配种子的损失，再保留同URL内所有部署/轮次成组重采样。
- 区间条件于已拟合的OOF模型，不包含完整模型重训练不确定性、未来日期变化或更多节点变化。
- 无固定点错配是破坏对应关系的对照，不自动满足可交换性；不把错配胜负频率称为p值。

## 5. 四视图的最新结果

全部为140会话LOUO pooled指标，未校准。

| 视图 | macro-F1↑ | balanced accuracy↑ | log-loss(bits)↓ | Brier↓ |
|---|---:|---:|---:|---:|
| pre14 | 0.9212 | 0.9214 | 0.411672 | 0.065994 |
| post14 | 0.8786 | 0.8786 | 0.866909 | 0.120084 |
| joint_scalar28 | 0.9356 | 0.9357 | 0.229472 | 0.047480 |
| Δ14 | 0.9714 | 0.9714 | 0.101261 | 0.023390 |
| joint_distribution314 | 1.0000 | 1.0000 | 0.010355 | 0.000977 |
| Δ17 | 1.0000 | 1.0000 | 0.010923 | 0.000959 |

### 如何解读

1. **pre不是部署无关视图。** 它甚至在该模型与队列下比post单侧更易辨识部署。
2. **双侧信息有预测用途。** 标量拼接优于post14；Δ14进一步改善当前线性学习器的表现，可能体现有用的变换参数化，而不是新增信息。
3. **Δ不是唯一有效的双侧表示。** 加入分布信息后的普通拼接也达到F1=1。两者loss极接近，尚无根据声称Δ17明显优于314维联合输入。
4. **完美F1只针对该有限队列。** 它不保证后续内容、时间、节点或采集条件下仍完美，也不是业务Y分类成绩。

标量联合视图相对post的经验损失改善约0.6374 bits，定义为两模型测试CE之差。它受拟合误差、容量和校准影响，不能直接写成条件互信息的估计或下界。

### 为什么与前一轮pre/post数字不同

同一0914旧OOF已经独立重算，LOUO pre仍为F1=0.9283、loss=0.5077；post仍为F1=0.8786、loss=1.7201。本轮新模型使用规范URL作为内层组标识，旧实现使用activity_id哈希；GroupKFold的组排序改变内层分配和所选C。

因此，本轮post loss=0.8669不等于旧模型被原样复现后性能变好。它是同数据、不同合法内层划分下重新拟合的结果，不能归因为数据改变，更不能包装为跨批次泛化改善。所有本轮四视图使用一致的新划分规则。

## 6. pre辨识力来自哪些特征

### 6.1 单家族结果

| pre家族 | 代表维数/内容 | macro-F1 | log-loss(bits) |
|---|---|---:|---:|
| direction | 3个方向比例/转移/熵量 | 0.6191 | 0.9677 |
| interaction | 4个burst/FR量 | 0.5185 | 1.0317 |
| packetization | length_median，1维 | 0.7958 | 0.7695 |
| timing | iat_median_us，1维 | 0.8855 | 1.0253 |
| workload | 5个包/字节量 | 0.7133 | 1.1042 |

### 6.2 删除家族结果

| 删除的pre家族 | macro-F1 | log-loss(bits) |
|---|---:|---:|
| direction | 0.9000 | 0.5733 |
| interaction | 0.9285 | 0.3979 |
| packetization | 0.9285 | 0.5472 |
| timing | 0.8641 | 0.5112 |
| workload | 0.9357 | 0.3619 |

IAT单量的F1较高，删除timing后完整pre的F1下降，支持时间特征是当前部署可辨识结构的重要部分。不过IAT单量的loss超过1 bit，说明决策正确率与概率可靠性不同；高F1不能替代概率质量检查。

删除workload后分数有所提高，不能据此认定工作量没有信息；其单家族仍有辨识力。共线性、尺度、有限样本调参和特征交互都可能影响增量表现。

旧OOF的metadata诊断balanced accuracy=0.5、missingness也为0.5；分别对应macro-F1约0.4949、0.3333。平衡二分类下常数预测的macro-F1可为1/3，所以不能只看F1把后者解释成“比随机更差”的特殊现象。

这些诊断没有找出一个足以解释全部pre高分的简单metadata通道，但也没有排除所有实现/环境/执行差异。尤其不能把IAT差异直接定性为拥塞控制导致的因果效应。

## 7. 精确配对是否有额外价值

### 7.1 主对照：各自训练、各自测试

| 表示 | 真→真 F1 | 真→真 loss | 错→错平均F1 | 错→错平均loss | 真配对损失优势及95%URL区间 |
|---|---:|---:|---:|---:|---|
| Δ14 | 0.9714 | 0.1013 | 0.9245 | 0.3767 | 0.2754 [0.0909, 0.5158] |
| Δ17 | 1.0000 | 0.0109 | 0.9450 | 0.2354 | 0.2244 [0.0634, 0.4327] |

损失优势定义为 `CE_wrong − CE_true`，正值有利于真实配对。100次错配F1的2.5%—97.5%种子范围分别约为Δ14：[0.9071,0.9357]，Δ17：[0.9284,0.9643]。这是错配构造随机性的范围，不是独立样本总体置信区间。

**主结论：** 当前表示与学习器确实可以利用同次访问对应关系改善部署预测，但错配仍有较强辨识力，说明仅部署的两侧边缘分布差异也已贡献大量可预测结构。

这不等同于条件独立检验，不证明精确配对的全部信息已经被提取，更不证明它有助于业务Y。

### 7.2 包选择与去首轮敏感性

| 口径 | n | 表示 | 真loss | 错平均loss | 优势及95%URL区间 |
|---|---:|---|---:|---:|---|
| 去首轮，rounds2–5 | 112 | Δ14 | 0.1147 | 0.3907 | 0.2759 [0.0916,0.5279] |
| 去首轮，rounds2–5 | 112 | Δ17 | 0.0157 | 0.2056 | 0.1899 [0.0509,0.3705] |
| 仅非空包 | 140 | Δ14 | 0.1455 | 0.3289 | 0.1834 [0.0596,0.3616] |
| 仅非空包 | 140 | Δ17 | 0.0634 | 0.1571 | 0.0937 [-0.0282,0.2257] |
| 排除完整重传包 | 140 | Δ14 | 0.1487 | 0.3924 | 0.2437 [0.0868,0.4280] |
| 排除完整重传包 | 140 | Δ17 | 0.0077 | 0.2282 | 0.2205 [0.0699,0.4107] |

Δ14在这些检查中区间均为正；Δ17在nonempty下区间跨零，应表述为“该口径下优势尚不明确”，而不是“没有优势”或“已经证明无效”。

nonempty会改变包序列及相邻包IAT的定义对象；排除完整重传也不代表消除了全部网络效应或部分重传。不能从该差异单独锁定ACK、重传或某个协议机制。

### 7.3 真/错训练测试的双向扰动

每个方向20次，主队列140会话：

| 表示 | 训练 | 测试 | 平均F1 | 平均loss(bits) |
|---|---|---|---:|---:|
| Δ14 | 真 | 错 | 0.8260 | 2.1441 |
| Δ14 | 错 | 真 | 0.9410 | 0.2675 |
| Δ17 | 真 | 错 | 0.8923 | 1.3757 |
| Δ17 | 错 | 真 | 0.9693 | 0.1322 |

训练及内层调参都遵循训练侧配对方式，只在外层测试切换配对。这些结果说明：训练在真实对应关系上的模型，对测试配对结构被破坏更敏感；不能拿真→错下降幅度替代主对照中的配对价值估计。

错→真效果较好也不等于错配训练更优，因为真→真仍是本条件下的直接基准，且扰动本身改变输入分布。

## 8. post能恢复哪些Δ

### 8.1 目标、模型与度量

输入为post14。六个目标是packet、transport bytes、burst、FR-runs的log-ratio，以及length JS和IAT JS。固定ridge使用alpha=1；调参ridge只在外层训练内按URL分组从[0.1,1,10,100]选择，按MAE选取。

报告pooled OOF R²与MAE。前四个MAE单位是自然对数比值，不是包数、字节或百分数；后两个为JS divergence单位。MAE与R²关注不同误差性质，按MAE调参不保证测试R²改善。

### 8.2 最新R²对照

| 目标 | 训练均值 | 固定ridge | 调参ridge | 名义家族剔除 | 原强相关量剔除 | 已知部署均值oracle |
|---|---:|---:|---:|---:|---:|---:|
| packet | -0.0775 | -0.6526 | 0.0293 | -0.4639 | 0.0685 | 0.0488 |
| bytes | -0.0785 | -0.1242 | 0.3393 | 0.2107 | 0.3127 | -0.0131 |
| burst | -0.0698 | -0.5849 | 0.3805 | 0.2465 | 0.4036 | 0.2325 |
| FR-runs | -0.0100 | -0.0348 | 0.1858 | 0.1099 | 0.1148 | 0.5979 |
| length JS | -0.0117 | 0.1451 | -0.0850 | 0.1816 | 0.1816 | 0.7988 |
| IAT JS | -0.0271 | 0.2250 | 0.2277 | 0.0542 | 0.0542 | 0.5723 |

| 目标 | 固定ridge MAE | 调参ridge MAE | 原强相关剔除MAE |
|---|---:|---:|---:|
| packet | 0.19741 | 0.17083 | 0.1626 |
| bytes | 0.08464 | 0.04991 | 0.0573 |
| burst | 0.26533 | 0.20673 | 0.1906 |
| FR-runs | 0.08386 | 0.08110 | 0.0765 |
| length JS | 0.08592 | 0.09398 | 0.0840 |
| IAT JS | 0.05320 | 0.05315 | 0.0582 |

名义家族剔除只移除配置taxonomy中的同家族；原强相关剔除对packet/bytes/burst/FR还移除相关计数、字节、FR派生量与length_median，保留更小输入集。原规则840条预测与0914先前OOF核对通过，不能把两个drop版本混写。

### 如何解读

- bytes和burst在调参/剔除后出现有限但实际可观测的正R²，固定ridge失败不是“信息不存在”的证据。
- packet仍较弱，FR与分布距离的恢复依赖目标和表示；不是所有变换都稳定可恢复。
- known-deployment均值oracle对FR和两个JS较强，提示这些目标的部署间中心差异可能解释相当部分变异；但其读取真实部署类别，不是未知部署的post-only模型。
- 不能在看完测试成绩后选每行最好者作为一个预先确定的方法。表格是对照，不是经独立测试确认的自动模型选择策略。
- R²不是恢复的信息比例或信息论可逆性；有限样本正值也不意味着重建了每次访问的完整变换。

### 8.3 代数基线

对log-ratio目标使用：`ln(post_test) − mean_train(ln(pre))`；oracle版本仅按已知部署选训练均值，不读取测试pre。

| 目标 | global代数R² | 已知部署代数R² |
|---|---:|---:|
| packet | -37.3914 | -37.4896 |
| bytes | -151.7778 | -151.6236 |
| burst | -16.2048 | -16.2119 |
| FR-runs | -87.2048 | -87.4153 |

该简单均值代数恢复在未见URL上很差。一个合理解释是不同URL的工作量差异不能由全局/部署均值pre替代；但这里是对结果的解释候选，不是正式因果识别。不能因为这个简单基线失败就认为数学耦合已被彻底排除。

## 9. 概率校准：不能只保留改善的结果

每个外层训练集内部，再生成嵌套调参的URL组外概率，拟合单一温度；外层测试标签不用于拟合温度。保留未校准与校准结果，不在测试上挑较好版本。

| 视图 | 未校准loss(bits) | 校准后loss(bits) | 变化 |
|---|---:|---:|---|
| pre14 | 0.411672 | 0.813870 | 恶化 |
| post14 | 0.866909 | 1.158193 | 恶化 |
| joint_scalar28 | 0.229472 | 0.319721 | 恶化 |
| Δ14 | 0.101261 | 0.894678 | 明显恶化 |
| joint_distribution314 | 0.010355 | 0.00000395 | 改善 |
| Δ17 | 0.010923 | 0.00000836 | 改善 |

温度为正且不改变0.5阈值的分类决策，因此F1保持不变，但置信程度和错误代价可大幅改变。数据小、URL间差异和训练侧校准关系的迁移限制，都可能影响结果；未确定具体原因。

接近零的测试loss只说明当前有限测试点上高置信正确，不证明未来样本完美校准。主真/错配比较统一采用未校准预测，避免拿真配对校准值与错配未校准值混比。

## 10. 配置一致，但同轮不是同时

执行因素审计覆盖全部462个选定会话：

| 检查项 | 结果 |
|---|---|
| TrafficTracer版本 | 462/462为1.0.27 |
| cache模式 | 462/462为cold |
| 主队列同URL同轮次SS/VLESS对数 | 70 |
| 配置目标时长相同 | 70/70 |
| 活动状态相同 | 70/70；表示状态相同，不另外推断每项均成功 |
| 导航状态相同 | 70/70 |
| cache模式相同 | 70/70 |
| profile fingerprint相同 | 0/70；生成机制未解释，不据此判定采集契约不一致 |
| 访问起点间隔 | 中位56.79秒，IQR [36.02,73.41]秒 |
| pre选定实体时间跨度差（VLESS−SS） | 中位−0.475秒，IQR [−2.382,1.046]秒 |

这些结果支持沿用用户确认的统一采集设置，但不能保证相邻访问时的网络环境、远端内容、CDN响应、广告或传输反馈完全一致。

`run_elapsed`表示会话生命周期耗时，不是精确捕获窗口。pre/post span只覆盖选择出来的exclusive实体，不是全部浏览器业务时长。它们可以用于诊断，不能无说明地替代用户设定的观测窗口或播放时间。

目前尚未通过实验干预将pre中的时间差异归因于拥塞、节点、协议实现或内容执行中的某一个因素。

## 11. 信息论框架：已能说什么，不能说什么

设C为部署、Y为业务标签、U为具体内容，X⁻/X⁺为pre/post观测。当前从联合观测出发，允许部署与两侧都有关联，不假定pre是未受部署影响的反事实访问。

### 已有经验支持

- 所选X⁻、X⁺和Δ对C具有不同程度的预测能力。
- 双侧联合输入及Δ提供比某些单侧基线更有效的表示。
- 真实配对相对错配，在当前模型、队列和部分口径下改善C的预测损失。
- 部分Δ目标可由post有限恢复；效果依赖目标、正则化和特征剔除。

### 尚未建立

- `I(C;pre|post)`的精确估计或可靠总体下界。
- `I(Y;pre|post)`及业务分类实际收益。
- Δ与业务Y独立、pre是纯语义、变换可逆或已经完成语义—代理风格解耦。
- 任意部署、节点、未来日期及未见业务上的泛化。

只有理想真实条件概率下的条件熵差才对应条件互信息。有限模型CE(post)−CE(joint)既受模型误差影响，也不一般构成条件互信息下界。Δ是双侧输入的确定性函数，不创造额外信息。

同样，不能仅凭观测位置套用 `I(Y;post)≤I(Y;pre)`；需要相应Markov条件。pre可辨识部署本身也不是该Markov关系不成立的形式证明。

业务学习不要求完整Δ可逆，但要直接检验训练期配对监督是否改善post-only的Y预测。当前C任务的成功不能替代这个闭环。

## 12. 业务标签、Bilibili与当前可行性

业务标签继续采用 `domain × activity`。Bilibili播放和YouTube播放为不同标签；同一平台不同视频共享播放业务标签，但需保留内容ID。

| 播放业务 | broad与repeat去重后的已登记URL | 当前结论 |
|---|---:|---|
| bilibili.com::video_playback | 2 | 使用用户的目标级正片播放确认；内容覆盖仍少 |
| youtube.com::video_playback | 1 | 有会话播放证据，但无法做该业务的未见视频划分 |
| vimeo.com视频播放 | 0 | 首页和固定简介页不标播放 |

正片存在即有效，不以播放满20秒作为必要条件。机器证据、人工证据、目标达成时长、路由质量分别保存；人工目标级确认不伪装成逐会话播放器遥测。

**Bilibili标签有效不等于严格配对可用。** 其repeat会话排除原因包含route_or_quality、no_usable_exclusive_side和incomplete_grid。部分VLESS会话自身可用，也可能因对应SS会话不满足条件而被完整网格规则排除。未因此撤销播放标签，也未因标签确认而绕过特征质量门。

其他page_load标签中，Baidu和GitHub各有3个登记URL，但这只是URL数量上界，不是已审核的同业务独立内容数。不同主页、资源页、搜索或文档行为不能只因同域名合并成一个明确业务任务。

当前未训练Y分类器或业务teacher。需要先确认活动语义、独立内容和可用配对范围；不能随机拆同视频重复访问、切出多个窗口或把子域请求当新内容来虚增泛化证据。也不据此宣布所有非视频业务实验都不可能。

## 13. 验证与复现保障

### 13.1 已通过的检查

| 项目 | 数量/状态 | 含义 |
|---|---:|---|
| 最新单元/回归测试 | 136 passed | 包括来源门、错配、分区、扰动及回放检查 |
| 真配对回放 | 7,560条 | 140会话×3种selection×18指标，数值/缺失原因一致 |
| 主阶段donor映射检查 | 1,602,720条 | 结构/分区/一一映射审计，不是独立访问 |
| 主阶段分类OOF检查 | 30,240条 | 多视图、多种子、多模型任务的预测记录 |
| 敏感性完整LOUO任务 | 218组 | 3×(6视图+20×2错配表示)+20×2方向×2表示 |
| 敏感性donor映射检查 | 1,549,296条 | 另一次结构验收 |
| 原强相关剔除预测回放 | 840条 | 140会话×6目标，与0914既有预测一致 |

来源检查拒绝非0914原始路径和混合旧新数据的comparison目录。已有原始捕获及旧产物未覆盖。运行使用Pytorch312及现有依赖，本阶段没有新增采集。

### 13.2 “独立验证”的准确含义

当前审计独立检查了来源、身份、分区、donor关系、OOF覆盖和部分数值复现，但没有把所有新模型在另一套完全独立实现中重新训练。不要将结构审计通过写成独立训练复现已全部完成。

所有结果都来自曾被分析过的0914数据，属于回顾性研究。代码和参数可追溯，并不自动消除研究过程中选择问题和指标的历史影响。

## 14. 阶段性主张清单

| 主张 | 当前状态 | 必须保留的限定 |
|---|---|---|
| 当前部署存在可辨识post差异 | 支持 | 固定部署、当前目标与观测层级 |
| SS有packet/burst重组且bytes相对保持的候选profile | 支持 | 既有统计队列与等效范围；不是语义保持证明 |
| pre携带部署相关结构 | 支持 | 来源仍未因果分解，不能叫纯语义视图 |
| 精确配对对部署预测有额外用途 | 主口径及部分敏感性支持 | 有限表示/学习器、URL条件性区间 |
| Δ17对所有包选择均稳健优于错配 | 不支持该无条件表述 | nonempty区间跨零 |
| Δ优于任何普通双侧表示 | 未建立 | 分布拼接也F1=1，维数/容量不同 |
| 固定ridge失败证明信息不存在 | 不成立 | 调参与剔除改善部分目标 |
| post可以恢复完整代理变换 | 未建立 | 仅六目标有限预测表现 |
| 配对监督改善domain×activity业务识别 | 未检验 | 尚无合适内容隔离的Y学习闭环 |
| 当前结果是纯协议因果效应 | 未建立 | 节点/实现/配置/反馈未充分分离 |

建议采用的总体表述：

> 在0914统一TrafficTracer采集设置及所观测代理部署下，入口和出口流量均具有部署相关结构；同次访问的精确配对，在当前表示和学习器中可提供额外的部署预测价值，但这一优势存在观测口径依赖。变换辨识性、单侧恢复性与业务学习收益是不同问题，后两者不能由分类高分直接推出。

## 15. 剩余问题与下一步建议

1. **原因诊断：** 对profile指纹生成机制、访问顺序、内容执行及路由覆盖进一步核实，区分可以观测的关联与无法识别的因果来源。
2. **不确定性：** 若要加强主张，补URL组层面的训练重复/内层划分敏感性，明确其仍不提供未来时间或节点外部验证。
3. **业务可行性：** 审核0914中确实可比的同domain活动与内容组；不足则保留业务收益未验证，不强行改标签或虚增样本。
4. **复现：** 对新配对与校准模型做独立重训练核对，而不仅是结构验证和既有预测回放。

上述建议不自动授权新采集、额外节点配置或新数据混入。本报告也未启动这些步骤。

## 16. 文件与结果追溯入口

### 最新配对实验

- [主队列、来源与模型输出根目录](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/paired-information-0914/run-01)
- [主队列清单](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/paired-information-0914/run-01/cohort.parquet)
- [排除原因](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/paired-information-0914/run-01/exclusions.parquet)
- [双侧摘要](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/paired-information-0914/run-01/side-summaries.parquet)
- [六视图结果](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/paired-information-0914/run-01/views/summary.parquet)
- [pre家族结果](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/paired-information-0914/run-01/families/summary.parquet)
- [主配对价值与区间](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/paired-information-0914/run-01/report/pairing-value.parquet)
- [敏感性配对区间](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/paired-information-0914/run-01/sensitivity-01/pairing-sensitivity.parquet)
- [敏感性与双向扰动完整分数](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/paired-information-0914/run-01/sensitivity-01/summary.parquet)
- [恢复主对照](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/paired-information-0914/run-01/recovery/summary.parquet)
- [原强相关剔除与代数对照](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/paired-information-0914/run-01/sensitivity-01/recovery-controls-summary.parquet)
- [校准结果](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/paired-information-0914/run-01/calibration/summary.parquet)
- [逐会话执行证据](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/paired-information-0914/run-01/execution-diagnostics/session-execution.parquet)
- [业务覆盖门](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/paired-information-0914/run-01/report/business-feasibility.json)
- [主阶段审计](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/paired-information-0914/run-01/report/independent-validation.json)、[敏感性审计](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/paired-information-0914/run-01/sensitivity-01/validation.json)

### 0914统计基础及标签

- [变换重复性完整报告](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/replication-20260914/run-01/repeat/audit/transformation-reproducibility-report.md)
- [broad统计说明](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/replication-20260914/run-01/broad/statistics/README.md)
- [当前人工活动确认](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/replication-20260914/run-01/activity-confirmation-v3/README.md)

### 实现与配置

- [0914-only主配置](F:/Program/VSCode/MyGit/ProxyAnalysis/configs/paired-information-0914.yaml)
- [敏感性配置](F:/Program/VSCode/MyGit/ProxyAnalysis/configs/paired-information-0914-sensitivity.yaml)
- [实现模块](F:/Program/VSCode/MyGit/ProxyAnalysis/src/proxy_analysis/paired_information)
- [连续实施记录](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/paired-information-0914-progress.md)

显示数字按表格精度四舍五入，机器表保留原精度。可读报告用于综合解释，逐会话结果、配置、源数据指纹和审计表用于复核。
