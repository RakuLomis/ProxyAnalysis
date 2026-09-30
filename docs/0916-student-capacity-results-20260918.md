# N1：固定监督下的学生模型能力对照实验结果

日期：2026-09-18。状态：正式实验、独立审核、交付完成；P7继续暂缓。

## 1. 核心结论

本轮完成了“原监督不变，只将线性学生换为小型MLP”的固定实验。结果并非简单地推翻或重复原线性结果：

1. **出现任务/方向特定的配对收益。** YouTube二类、distribution157、SS→VLESS中，M2同时改善平均CE和F1，并超过同族M0、M1、M3；五个种子上的CE优势方向一致。
2. **这不是普遍业务闭环。** 六类任务没有任何设置同时取得三项CE收益区间均在零以上；不同表示和方向仍有负向或不确定结果。
3. **更强模型不是更强泛化的保证。** 一些MLP硬标签模型的跨部署CE严重恶化；软监督大幅降低CE有时只是缓解高置信错误，并未改善F1。
4. **不能把MLP收益直接归因为表达能力一个因素。** 学生模型族、优化和正则几何同时发生变化；跨族收益差也并非所有指标都具有方向明确的区间。
5. **结论应进一步具体化。** 现有数据支持“固定统计表示上，监督可利用性依赖具体学习程序、任务与部署方向”，既不支持普遍不可利用，也不支持换成神经网络即可解决。

## 2. 实验设计与数据

主队列仍为0916的240次访问：六业务、30内容、SS/VLESS、每内容每部署第1/2/4/5轮。YouTube二类是其中10内容的子集。两任务分别每源外层训练96/32次访问；不是因为原始PCAP体积大就拥有更多独立内容。

复用原五折内容划分、teacher_scheme=0、scalar14/distribution157特征字典、同部署与双向跨部署测试。不补采、不重新提取PCAP、不加入299/Hy2/Bilibili，不改变标签口径。模型推理仅post，保留offline/index-assisted的观测边界。

| 臂 | 固定监督 |
|---|---|
| M0 | one-hot硬标签 |
| M1 | 0.5硬标签＋0.5历史post OOF教师 |
| M2 | 0.5硬标签＋0.5历史真实pre OOF教师 |
| M3 | 0.5硬标签＋0.5历史同业务错配pre OOF教师 |

每种表示复用其对应教师，未重训教师。历史OOF概率、原2+2教师分区内的错配映射和fit-ledger实际targets三路核验一致；没有换用P7的四内容循环错配。

原线性M0–M3结果为历史参照。本轮不将新P7高精度R0与旧线性M1–M3混用。

## 3. 固定模型、优化与预算

- PyTorch 2.5.1，CPU、float64、单线程、确定性算法。
- Linear(d,32) → ReLU → Linear(32,K)，两类也输出K个logits。
- 全批次Adam：lr=0.001，betas=(0.9,0.999)，eps=1e−8，optimizer weight_decay=0。
- 目标：平均软目标CE（nats）＋(1e−4/2)×两层权重平方和；bias不正则。
- 每模型固定1000步，使用最后一步；无early stopping、scheduler、dropout、batch normalization、梯度裁剪或目标域校准。
- 五种子：20260918–20260922。每个上下文/种子的四臂具有相同初始化，各自重置优化器。
- 源训练post的median填补与StandardScaler复用历史参数，并重新仅从源训练post拟合核对。
- 六类参数量：scalar14为678，distribution157为5254；二类分别546/5122。

正式预算：2表示×2任务×2源部署×5折×4臂×5seed=800次，全部完成。另有16次工程拟合（8个设置重复训练），确认确定性；工程阶段不评估测试成绩。新增教师拟合0、目标域拟合0。

没有设置学生内层早停集：直接复用原OOF监督时，重新拆出的早停内容可能已经进入某些教师训练；本轮以固定步数避免该选择路径。不保证固定1000步等于所有模型收敛到最优。

## 4. 工程与统计审核

- 40个原作业的成员、教师OOF、错配、预处理和目标全部审核。
- 800个模型全部保存初始/最终权重、哈希、目标与训练矩阵哈希、1000步轨迹。
- 200组初始化（40上下文×5seed），每组四臂一致。
- 用独立NumPy前向计算重放25,600条预测；最大概率误差4.4409e−16。
- 按源训练数据独立重建填补/标准化矩阵，核对最终训练目标与参数。
- 全套185项测试通过。Windows本地库初次加载异常通过先导入Arrow再导入PyTorch解决；未改动环境依赖。
- 全部旧冻结文件保持不变，没有覆盖P0–P6结果，也没有启动P7正式约束模型。

统计口径：每seed先汇总完整外层预测，F1/BA/Brier再取5seed均值和范围。CE收益先按内容平均重复访问及seed，再做按业务分层的2000次内容bootstrap。区间条件于已有5seed模型，不覆盖新采集、重新训练或历史选择影响；种子和重复访问不是新增独立内容。没有先平均概率建立集成模型。

定义：G_task=CE(M0)−CE(M2)，G_pair=CE(M3)−CE(M2)，G_soft=CE(M1)−CE(M2)。正数支持M2；所有设置完整报告，无多重检验校正，不作为确认性显著结论。

## 5. 最值得关注的局部结果

### 5.1 YouTube、distribution157、SS→VLESS

| 学生臂 | 五seed平均CE bits | 五seed平均macro-F1 |
|---|---:|---:|
| M0 | 9.5205 | 0.3440 |
| M1 | 5.1782 | 0.3333 |
| M2 | 1.6380 | 0.5811 |
| M3 | 4.7320 | 0.4401 |

M2的G_task=7.8825 [5.9580,9.7862]，G_pair=3.0940 [1.0766,5.6122]，G_soft=3.5402 [2.6197,4.4099] bits。三项在五个种子的点估计中均为正。

M2五seed F1范围为0.5442–0.6577；BA为0.5750–0.6750。每seed的M2 F1也都超过相同seed的M0/M1/M3。这不只是CE改善的局部例子。

但是该任务仅10个登记内容，且M2 CE=1.6380仍高于均匀预测的1 bit参考；不能称已具备良好的概率预测，更不能据此宣称可部署或跨业务普适。

与历史线性同设置相比，G_task的增量为2.0272 [0.2877,3.2726]；G_pair的增量为1.2026 [−0.2716,3.2178]，G_soft的增量为0.4992 [−0.2699,1.7704]。后两项区间跨零，因此不能宣称已经稳健证明“非线性特有地增加了精确配对价值”。

### 5.2 YouTube、scalar14、SS→VLESS：CE优势不等于识别优势

三项CE收益区间也均为正，但M0→M2平均F1从0.4407降到0.3814，CE从11.5975降到4.8004。这个设置应描述为概率损失改善，不能与上面的分类改善混为一谈。

### 5.3 六类任务仍没有普遍优势

- SS同部署scalar14：M2 CE=0.5215优于M0=0.6040，G_pair和G_soft区间为正，但G_task区间[−0.0666,0.2700]跨零。
- SS→VLESS scalar14：M2优于M0/M3，却不如普通post教师M1，G_soft=−0.4179 [−0.5855,−0.2554]。
- SS→VLESS distribution157：M2比错配更差，G_pair=−0.9502 [−1.4855,−0.4578]。
- VLESS→SS scalar14：M2改善CE且F1从0.5781到0.6349；但M1 F1=0.6521，G_soft区间跨零。
- VLESS同部署distribution157：M0 CE/F1为0.5689/0.9128，M2为0.6301/0.8606，真实配对未改善这两个指标。

## 6. 训练拟合与泛化边界

M0在六类各训练上下文的平均训练准确率约0.9856、平均训练硬标签CE约0.0870 bits；YouTube平均训练准确率1.0000、平均CE约0.00549 bits。与部分严重恶化的测试CE并列看，存在明显训练/测试差距，不能仅以“模型能够拟合训练标签”证明可泛化。

固定步数下最后梯度并非全为零，不能声称找到了模型族最优风险。也不能看到这些结果后在同一报告中增加early stopping或换正则，再称其为原冻结实验。

MLP不能恢复统计摘要已经丢失的包顺序和连接结构；本轮不是原始序列表示学习实验。没有估计Shannon互信息或predictive V-information。

## 7. 后续建议与停止边界

本轮已回答一个此前缺失的问题：至少在一个预设任务/方向/表示上，相同线性教师监督能够被小型非线性学生利用，获得同族对照下的局部分类收益。因此应保留这个正例，而不是继续将线性负向结果外推到全部配对学习。

但本轮仍不足以支持全面升级网络或恢复大规模搜索。建议先审核本报告中的局部正例和反例，再由用户选择是否恢复线性P7、进行299/教师分法敏感性，或引入非线性教师。上述扩展均未自动启动，不追加宽度、α、学习率或训练步数搜索。

## 8. 完整数字附录

下表来源于已通过独立审核的结果文件。student为同部署，cross为另一部署；protocol列始终指训练源部署。区间为条件内容bootstrap区间，seed范围不是置信区间。

### A. All arms: five-seed mean and range

#### six_business / SS / distribution157 / cross

| Arm | CE bits: mean [min,max] | Macro-F1: mean [min,max] | BA mean | Brier mean |
| --- | --- | --- | --- | --- |
| M0 | 6.5740 [5.6653, 7.2586] | 0.4073 [0.3591, 0.4529] | 0.4350 | 0.9716 |
| M1 | 3.7770 [3.3876, 4.0271] | 0.3434 [0.3064, 0.3714] | 0.3850 | 0.8974 |
| M2 | 4.2127 [3.8424, 4.4699] | 0.3463 [0.3127, 0.3785] | 0.3717 | 1.0397 |
| M3 | 3.2625 [3.1418, 3.4801] | 0.3803 [0.3515, 0.4135] | 0.4117 | 0.8738 |

#### six_business / SS / distribution157 / student

| Arm | CE bits: mean [min,max] | Macro-F1: mean [min,max] | BA mean | Brier mean |
| --- | --- | --- | --- | --- |
| M0 | 0.8344 [0.6866, 0.9569] | 0.8599 [0.8514, 0.8757] | 0.8583 | 0.2075 |
| M1 | 0.6993 [0.6573, 0.7339] | 0.8297 [0.8010, 0.8430] | 0.8283 | 0.2466 |
| M2 | 0.6857 [0.6570, 0.7045] | 0.8384 [0.8105, 0.8609] | 0.8367 | 0.2495 |
| M3 | 0.9032 [0.7628, 0.9637] | 0.7993 [0.7786, 0.8261] | 0.7967 | 0.2857 |

#### six_business / SS / scalar14 / cross

| Arm | CE bits: mean [min,max] | Macro-F1: mean [min,max] | BA mean | Brier mean |
| --- | --- | --- | --- | --- |
| M0 | 5.8240 [5.5644, 6.2055] | 0.4702 [0.4558, 0.4869] | 0.5233 | 0.8547 |
| M1 | 2.7400 [2.5726, 2.9071] | 0.4741 [0.4555, 0.4866] | 0.5300 | 0.7817 |
| M2 | 3.1579 [2.9734, 3.3770] | 0.4494 [0.4155, 0.4941] | 0.5017 | 0.8298 |
| M3 | 3.7429 [3.3854, 4.1924] | 0.3907 [0.3515, 0.4515] | 0.4400 | 0.8885 |

#### six_business / SS / scalar14 / student

| Arm | CE bits: mean [min,max] | Macro-F1: mean [min,max] | BA mean | Brier mean |
| --- | --- | --- | --- | --- |
| M0 | 0.6040 [0.5792, 0.6294] | 0.8674 [0.8506, 0.8757] | 0.8667 | 0.1855 |
| M1 | 0.5555 [0.5435, 0.5643] | 0.8810 [0.8760, 0.8845] | 0.8800 | 0.1838 |
| M2 | 0.5215 [0.5135, 0.5300] | 0.8790 [0.8757, 0.8839] | 0.8783 | 0.1770 |
| M3 | 0.5847 [0.5730, 0.5974] | 0.8637 [0.8582, 0.8754] | 0.8633 | 0.1961 |

#### six_business / VLESS / distribution157 / cross

| Arm | CE bits: mean [min,max] | Macro-F1: mean [min,max] | BA mean | Brier mean |
| --- | --- | --- | --- | --- |
| M0 | 6.5109 [6.1570, 7.2560] | 0.4053 [0.3614, 0.4527] | 0.4133 | 1.0375 |
| M1 | 3.9060 [3.6614, 4.2227] | 0.3780 [0.3646, 0.4142] | 0.3933 | 0.9485 |
| M2 | 3.7395 [3.5784, 3.9714] | 0.3878 [0.3689, 0.4171] | 0.3850 | 0.8904 |
| M3 | 4.0897 [3.4464, 5.0372] | 0.3902 [0.3091, 0.4266] | 0.4050 | 0.9199 |

#### six_business / VLESS / distribution157 / student

| Arm | CE bits: mean [min,max] | Macro-F1: mean [min,max] | BA mean | Brier mean |
| --- | --- | --- | --- | --- |
| M0 | 0.5689 [0.5164, 0.6370] | 0.9128 [0.9013, 0.9265] | 0.9117 | 0.1385 |
| M1 | 0.6204 [0.5858, 0.6647] | 0.8765 [0.8661, 0.8832] | 0.8767 | 0.2016 |
| M2 | 0.6301 [0.5655, 0.6666] | 0.8606 [0.8418, 0.8929] | 0.8600 | 0.2004 |
| M3 | 0.5237 [0.4882, 0.5852] | 0.8675 [0.8433, 0.8922] | 0.8667 | 0.1789 |

#### six_business / VLESS / scalar14 / cross

| Arm | CE bits: mean [min,max] | Macro-F1: mean [min,max] | BA mean | Brier mean |
| --- | --- | --- | --- | --- |
| M0 | 2.4422 [1.9506, 3.0172] | 0.5781 [0.5579, 0.5971] | 0.6000 | 0.6508 |
| M1 | 1.2608 [1.0966, 1.3348] | 0.6521 [0.6368, 0.6665] | 0.6567 | 0.5041 |
| M2 | 1.2451 [1.1666, 1.2804] | 0.6349 [0.5844, 0.6654] | 0.6417 | 0.5100 |
| M3 | 1.7122 [1.4513, 2.0264] | 0.5492 [0.5194, 0.5968] | 0.5983 | 0.5847 |

#### six_business / VLESS / scalar14 / student

| Arm | CE bits: mean [min,max] | Macro-F1: mean [min,max] | BA mean | Brier mean |
| --- | --- | --- | --- | --- |
| M0 | 0.9392 [0.9042, 0.9902] | 0.8246 [0.7912, 0.8505] | 0.8250 | 0.2718 |
| M1 | 0.8955 [0.8710, 0.9251] | 0.7901 [0.7646, 0.8242] | 0.7917 | 0.3287 |
| M2 | 0.7845 [0.7150, 0.8379] | 0.8201 [0.8078, 0.8428] | 0.8200 | 0.2848 |
| M3 | 0.7542 [0.6933, 0.7975] | 0.8070 [0.7821, 0.8248] | 0.8083 | 0.2866 |

#### youtube_activity / SS / distribution157 / cross

| Arm | CE bits: mean [min,max] | Macro-F1: mean [min,max] | BA mean | Brier mean |
| --- | --- | --- | --- | --- |
| M0 | 9.5205 [8.8099, 10.6549] | 0.3440 [0.3333, 0.3866] | 0.5050 | 0.9577 |
| M1 | 5.1782 [4.4343, 5.8878] | 0.3333 [0.3333, 0.3333] | 0.5000 | 0.9734 |
| M2 | 1.6380 [1.3939, 1.8867] | 0.5811 [0.5442, 0.6577] | 0.6100 | 0.5897 |
| M3 | 4.7320 [3.9875, 5.2430] | 0.4401 [0.3593, 0.5248] | 0.5250 | 0.7861 |

#### youtube_activity / SS / distribution157 / student

| Arm | CE bits: mean [min,max] | Macro-F1: mean [min,max] | BA mean | Brier mean |
| --- | --- | --- | --- | --- |
| M0 | 0.5627 [0.5194, 0.6067] | 0.8249 [0.8249, 0.8249] | 0.8250 | 0.2345 |
| M1 | 0.3579 [0.3357, 0.3920] | 0.9049 [0.8749, 0.9250] | 0.9050 | 0.1554 |
| M2 | 0.5062 [0.4797, 0.5293] | 0.8746 [0.8496, 0.9000] | 0.8750 | 0.2089 |
| M3 | 0.4492 [0.3887, 0.5782] | 0.8646 [0.8240, 0.8997] | 0.8650 | 0.1864 |

#### youtube_activity / SS / scalar14 / cross

| Arm | CE bits: mean [min,max] | Macro-F1: mean [min,max] | BA mean | Brier mean |
| --- | --- | --- | --- | --- |
| M0 | 11.5975 [10.4662, 12.3264] | 0.4407 [0.4000, 0.4747] | 0.4450 | 1.0747 |
| M1 | 5.6789 [5.2190, 6.2145] | 0.3336 [0.3143, 0.3985] | 0.3750 | 1.1162 |
| M2 | 4.8004 [3.7724, 5.2514] | 0.3814 [0.3162, 0.4500] | 0.4150 | 1.0442 |
| M3 | 10.6286 [8.5402, 12.3827] | 0.3646 [0.3012, 0.4470] | 0.4250 | 1.0962 |

#### youtube_activity / SS / scalar14 / student

| Arm | CE bits: mean [min,max] | Macro-F1: mean [min,max] | BA mean | Brier mean |
| --- | --- | --- | --- | --- |
| M0 | 1.7517 [1.4763, 2.0403] | 0.7740 [0.7494, 0.7995] | 0.7750 | 0.3595 |
| M1 | 0.7040 [0.6600, 0.7583] | 0.8599 [0.8249, 0.8997] | 0.8600 | 0.2138 |
| M2 | 0.7211 [0.6243, 0.8446] | 0.8748 [0.8249, 0.8997] | 0.8750 | 0.2105 |
| M3 | 0.8327 [0.7397, 0.9766] | 0.7694 [0.7494, 0.7995] | 0.7700 | 0.3460 |

#### youtube_activity / VLESS / distribution157 / cross

| Arm | CE bits: mean [min,max] | Macro-F1: mean [min,max] | BA mean | Brier mean |
| --- | --- | --- | --- | --- |
| M0 | 11.1969 [10.4084, 11.7880] | 0.5778 [0.5604, 0.6132] | 0.6050 | 0.7819 |
| M1 | 7.9427 [6.3227, 8.8909] | 0.5456 [0.5200, 0.5833] | 0.5700 | 0.8176 |
| M2 | 5.7520 [4.3148, 6.6636] | 0.4247 [0.3730, 0.4813] | 0.5250 | 0.8311 |
| M3 | 6.3678 [3.6194, 8.0071] | 0.5534 [0.5055, 0.6484] | 0.6050 | 0.7449 |

#### youtube_activity / VLESS / distribution157 / student

| Arm | CE bits: mean [min,max] | Macro-F1: mean [min,max] | BA mean | Brier mean |
| --- | --- | --- | --- | --- |
| M0 | 1.3535 [0.6400, 1.9337] | 0.8549 [0.8249, 0.8749] | 0.8550 | 0.2051 |
| M1 | 1.4134 [0.6282, 1.6184] | 0.8750 [0.8500, 0.9000] | 0.8750 | 0.2337 |
| M2 | 1.4416 [1.3976, 1.4625] | 0.8948 [0.8749, 0.8997] | 0.8950 | 0.2230 |
| M3 | 1.2876 [0.5100, 1.5104] | 0.8447 [0.7995, 0.8749] | 0.8450 | 0.2496 |

#### youtube_activity / VLESS / scalar14 / cross

| Arm | CE bits: mean [min,max] | Macro-F1: mean [min,max] | BA mean | Brier mean |
| --- | --- | --- | --- | --- |
| M0 | 17.5798 [17.0266, 18.3880] | 0.4573 [0.4048, 0.4872] | 0.5350 | 0.9300 |
| M1 | 5.9278 [5.6316, 6.2082] | 0.5277 [0.5055, 0.5616] | 0.5600 | 0.7966 |
| M2 | 5.4749 [4.4890, 6.6555] | 0.5754 [0.5200, 0.6419] | 0.5950 | 0.7701 |
| M3 | 9.1657 [7.9416, 10.3196] | 0.4530 [0.4320, 0.4813] | 0.5100 | 0.9546 |

#### youtube_activity / VLESS / scalar14 / student

| Arm | CE bits: mean [min,max] | Macro-F1: mean [min,max] | BA mean | Brier mean |
| --- | --- | --- | --- | --- |
| M0 | 3.0901 [2.5089, 3.6402] | 0.7618 [0.7206, 0.7980] | 0.7650 | 0.4059 |
| M1 | 0.8931 [0.7957, 0.9272] | 0.7189 [0.6970, 0.7500] | 0.7200 | 0.3827 |
| M2 | 1.3941 [1.2249, 1.5922] | 0.6861 [0.6465, 0.7206] | 0.6900 | 0.4514 |
| M3 | 1.0531 [0.9427, 1.1866] | 0.7049 [0.6748, 0.7248] | 0.7050 | 0.4072 |

### B. Three within-MLP gains

Cell = mean advantage [95% conditional interval]; positive favors M2.

| Setting | G_task | G_pair | G_soft |
| --- | --- | --- | --- |
| six_business / SS / distribution157 / cross | 2.3613 [1.6076, 3.2310] | -0.9502 [-1.4855, -0.4578] | -0.4357 [-0.8586, 0.0286] |
| six_business / SS / distribution157 / student | 0.1487 [-0.1871, 0.5808] | 0.2174 [-0.0419, 0.5675] | 0.0135 [-0.1033, 0.1370] |
| six_business / SS / scalar14 / cross | 2.6661 [1.9901, 3.3251] | 0.5850 [0.2092, 1.0294] | -0.4179 [-0.5855, -0.2554] |
| six_business / SS / scalar14 / student | 0.0825 [-0.0666, 0.2700] | 0.0633 [0.0140, 0.1199] | 0.0340 [0.0075, 0.0615] |
| six_business / VLESS / distribution157 / cross | 2.7714 [2.0367, 3.5785] | 0.3503 [-0.4550, 1.2257] | 0.1665 [-0.5267, 0.7417] |
| six_business / VLESS / distribution157 / student | -0.0612 [-0.2801, 0.1870] | -0.1064 [-0.2978, 0.0639] | -0.0097 [-0.1001, 0.0776] |
| six_business / VLESS / scalar14 / cross | 1.1971 [0.8396, 1.5346] | 0.4672 [0.1754, 0.7812] | 0.0158 [-0.1296, 0.1613] |
| six_business / VLESS / scalar14 / student | 0.1547 [-0.1154, 0.4364] | -0.0303 [-0.0977, 0.0293] | 0.1109 [0.0462, 0.1810] |
| youtube_activity / SS / distribution157 / cross | 7.8825 [5.9580, 9.7862] | 3.0940 [1.0766, 5.6122] | 3.5402 [2.6197, 4.4099] |
| youtube_activity / SS / distribution157 / student | 0.0565 [-0.2523, 0.4792] | -0.0570 [-0.3614, 0.2355] | -0.1483 [-0.2721, -0.0529] |
| youtube_activity / SS / scalar14 / cross | 6.7971 [2.4454, 11.6347] | 5.8282 [2.5535, 8.7701] | 0.8785 [0.3537, 1.4244] |
| youtube_activity / SS / scalar14 / student | 1.0306 [0.2793, 1.9790] | 0.1116 [-0.4358, 0.5052] | -0.0171 [-0.1160, 0.0693] |
| youtube_activity / VLESS / distribution157 / cross | 5.4449 [-0.6344, 11.0457] | 0.6158 [-1.7344, 2.4592] | 2.1907 [-2.3868, 9.1195] |
| youtube_activity / VLESS / distribution157 / student | -0.0881 [-1.1975, 0.9669] | -0.1540 [-0.5737, 0.1535] | -0.0282 [-0.5474, 0.5061] |
| youtube_activity / VLESS / scalar14 / cross | 12.1049 [8.3664, 16.0641] | 3.6908 [0.8251, 6.7358] | 0.4529 [-1.4975, 2.0896] |
| youtube_activity / VLESS / scalar14 / student | 1.6960 [0.2335, 3.5004] | -0.3410 [-1.1648, 0.2225] | -0.5010 [-1.3629, 0.0671] |

### C. Positive gain counts across five seeds

| Setting | G_task positive | G_pair positive | G_soft positive |
| --- | --- | --- | --- |
| six_business / SS / distribution157 / cross | 5/5 | 0/5 | 0/5 |
| six_business / SS / distribution157 / student | 4/5 | 5/5 | 4/5 |
| six_business / SS / scalar14 / cross | 5/5 | 5/5 | 0/5 |
| six_business / SS / scalar14 / student | 5/5 | 5/5 | 5/5 |
| six_business / VLESS / distribution157 / cross | 5/5 | 4/5 | 3/5 |
| six_business / VLESS / distribution157 / student | 1/5 | 0/5 | 2/5 |
| six_business / VLESS / scalar14 / cross | 5/5 | 5/5 | 3/5 |
| six_business / VLESS / scalar14 / student | 5/5 | 0/5 | 5/5 |
| youtube_activity / SS / distribution157 / cross | 5/5 | 5/5 | 5/5 |
| youtube_activity / SS / distribution157 / student | 5/5 | 1/5 | 0/5 |
| youtube_activity / SS / scalar14 / cross | 5/5 | 5/5 | 5/5 |
| youtube_activity / SS / scalar14 / student | 5/5 | 5/5 | 2/5 |
| youtube_activity / VLESS / distribution157 / cross | 5/5 | 4/5 | 5/5 |
| youtube_activity / VLESS / distribution157 / student | 3/5 | 4/5 | 4/5 |
| youtube_activity / VLESS / scalar14 / cross | 5/5 | 5/5 | 3/5 |
| youtube_activity / VLESS / scalar14 / student | 5/5 | 0/5 | 0/5 |

### D. Descriptive model-program interaction: G_MLP - G_LR

Historical LR uses its original M0-M3, same teacher scheme and alpha; no replacement by P7 R0. These are not pure causal effects of capacity.

| Setting | Task interaction | Pair interaction | Soft interaction |
| --- | --- | --- | --- |
| six_business / SS / distribution157 / cross | 1.7843 [1.2240, 2.4232] | -0.6711 [-1.0851, -0.2370] | -0.1709 [-0.4785, 0.1529] |
| six_business / SS / distribution157 / student | 0.1423 [-0.0902, 0.4046] | -0.0142 [-0.1195, 0.0953] | -0.0603 [-0.1219, 0.0022] |
| six_business / SS / scalar14 / cross | 2.3502 [1.7736, 2.9139] | 0.2485 [-0.0896, 0.6319] | -0.2554 [-0.3921, -0.1200] |
| six_business / SS / scalar14 / student | 0.1457 [0.0184, 0.3063] | 0.0037 [-0.0357, 0.0536] | 0.0053 [-0.0157, 0.0255] |
| six_business / VLESS / distribution157 / cross | 0.6718 [0.0770, 1.3418] | -0.1517 [-0.7779, 0.5177] | -0.4615 [-0.9824, -0.0097] |
| six_business / VLESS / distribution157 / student | -0.0038 [-0.1272, 0.1472] | -0.0876 [-0.2194, 0.0286] | -0.0928 [-0.1795, -0.0138] |
| six_business / VLESS / scalar14 / cross | 1.2983 [0.9549, 1.6011] | 0.5253 [0.2922, 0.7770] | 0.0438 [-0.0773, 0.1782] |
| six_business / VLESS / scalar14 / student | 0.2233 [-0.0210, 0.4829] | -0.0418 [-0.0841, -0.0016] | 0.0579 [-0.0015, 0.1157] |
| youtube_activity / SS / distribution157 / cross | 2.0272 [0.2877, 3.2726] | 1.2026 [-0.2716, 3.2178] | 0.4992 [-0.2699, 1.7704] |
| youtube_activity / SS / distribution157 / student | 0.1533 [-0.1208, 0.5426] | -0.3885 [-1.0093, -0.0076] | -0.0912 [-0.1628, -0.0312] |
| youtube_activity / SS / scalar14 / cross | 5.3381 [1.1650, 10.1592] | 5.9403 [2.5925, 8.9557] | 0.4867 [-0.0290, 0.9629] |
| youtube_activity / SS / scalar14 / student | 1.0127 [0.2664, 1.9638] | 0.0824 [-0.3161, 0.3884] | -0.0169 [-0.0900, 0.0523] |
| youtube_activity / VLESS / distribution157 / cross | 3.5733 [-0.5326, 7.6840] | 1.3000 [-1.1415, 3.6599] | 1.9448 [-0.8748, 5.8992] |
| youtube_activity / VLESS / distribution157 / student | -0.0834 [-1.0401, 0.6937] | -0.1323 [-0.6041, 0.1713] | -0.1461 [-0.5733, 0.1357] |
| youtube_activity / VLESS / scalar14 / cross | 11.6837 [7.9030, 15.7230] | 3.1006 [0.9160, 5.2661] | -0.2003 [-1.8000, 1.1151] |
| youtube_activity / VLESS / scalar14 / student | 1.5282 [0.2100, 3.2188] | -0.3347 [-1.2823, 0.2664] | -0.5077 [-1.3458, 0.0458] |

## 9. 产物与复用

- [固定配置](F:/Program/VSCode/MyGit/ProxyAnalysis/configs/content-generalization-20260916-student-capacity.yaml)
- [训练与冻结入口](F:/Program/VSCode/MyGit/ProxyAnalysis/src/proxy_analysis/crosscontent/student_capacity.py)
- [独立审核与统计入口](F:/Program/VSCode/MyGit/ProxyAnalysis/src/proxy_analysis/crosscontent/student_capacity_report.py)
- [完整逐seed指标](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/content-generalization-20260916/student-capacity-01/report/metrics-per-seed.json)
- [五seed汇总指标](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/content-generalization-20260916/student-capacity-01/report/metrics-summary.json)
- [三项收益与条件区间](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/content-generalization-20260916/student-capacity-01/report/gains-seed-average.json)
- [模型程序间收益差](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/content-generalization-20260916/student-capacity-01/report/model-family-interaction.json)
- [训练拟合诊断](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/content-generalization-20260916/student-capacity-01/report/training-diagnostics.parquet)
- [独立审核结果](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/content-generalization-20260916/student-capacity-01/report/validation.json)
- [全设置收益图](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/content-generalization-20260916/student-capacity-01/delivery/paired-gains.png)

运行环境Pytorch312、PYTHONPATH=src、OMP/MKL/OPENBLAS线程数均1。已完成目录禁止再次freeze；以下命令会核验已完成产物而不会重复训练：

```powershell
& D:/Tools/Anaconda/envs/Pytorch312/python.exe -m proxy_analysis.crosscontent.student_capacity --mode verify
& D:/Tools/Anaconda/envs/Pytorch312/python.exe -m proxy_analysis.crosscontent.student_capacity --mode run
& D:/Tools/Anaconda/envs/Pytorch312/python.exe -m proxy_analysis.crosscontent.student_capacity_report
& D:/Tools/Anaconda/envs/Pytorch312/python.exe -m proxy_analysis.crosscontent.student_capacity_delivery
```

所有原始及派生大文件仍为本地数据，本次未推送仓库。
