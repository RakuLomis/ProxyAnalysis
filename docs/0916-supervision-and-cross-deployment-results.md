# 0916：监督诊断、双侧表示与跨部署单侧验证

日期：2026-09-17。状态：已完成本轮 P0–P3；等待确认预指定敏感性扩展。

## 1. 摘要

本轮仅使用既有 0916 的 240 次平衡访问，完成实际 OOF 教师诊断、软目标核验、两套表示的四视图诊断、联合教师真/错配与有限 α 曲线，以及 SS→VLESS、VLESS→SS 未见内容测试。没有补采、混入 0914、纳入唯一 MDN 恢复访问或修改旧结果。

主要发现：

1. **未发现软监督实现尺度错误。** α=0、one-hot 教师、直接硬标签 LR 和历史 M0 通过数值等价核验；软目标总权重保持 N，显式软交叉熵与展开加权目标/梯度通过测试。
2. **实际 pre OOF 教师通常比 post OOF 教师好，但不足以保证学生获益。** 不能简单将既有退化归结为 pre 教师没有预测能力。
3. **双侧业务预测结构确实可见。** scalar14 的六类联合输入 CE 比 post 明显低；但它是测试时使用两侧的诊断，不是单侧学生，也不是互信息估计。
4. **联合教师没有普遍解决净收益问题。** scalar14 六类同部署的 J-True 仍比 M0 损失高，且相对 J-Wrong 的区间跨零。
5. **跨部署结果具有方向和表示依赖。** scalar14 六类 SS→VLESS 的 M2 比 M0 和 M3 损失低，但普通 post 教师 M1 更好；VLESS→SS 的 M2 则比 M0 退化。不能泛化成“配对监督稳定增强迁移”。
6. **分布表示提升部分同部署分类，却可能放大迁移脆弱性。** 六类 VLESS 的 post-only F1 从 0.7713 提高至 0.9414，但其跨到 SS 的 CE 从 scalar14 的 0.9415 升至 distribution157 的 6.3267。
7. **减少极端错误概率不等于形成可用分类器。** 某些跨部署 CE 改善很大，但 F1 仍接近弱基线，甚至低于原模型；所有结果同时报告 CE、F1 和 Brier。

当前结论是：配对监督的利用边界不是“统一有效/无效”，而依赖表示、任务、迁移方向和监督来源。联合教师的一致性理由尚未转化为普遍的经验优势。

## 2. 冻结口径与完成量

| 项目 | 本轮设置或完成结果 |
|---|---|
| 队列 | 240，六业务 × 五内容 × SS/VLESS × 第 1/2/4/5 轮 |
| 任务 | 六类 domain × activity；YouTube 播放/搜索二类 |
| 外层 | 原五折内容归组，直接复用既有 assignment |
| 教师 | scheme=0、训练内容内 2+2 交叉拟合 |
| 包口径 | observed |
| 表示 | scalar14；distribution157 |
| 模型 | LR，C=1、T=1、max_iter=3000，训练内填补与标准化 |
| 教师权重 | α=0、0.1、0.25、0.5；0 为共享 M0 |
| 标签平滑 | LS10：0.9 one-hot + 0.1 均匀分布 |
| 主对照 | scalar14、α=0.5，其余全部作为预设敏感性报告 |
| 正式 P1/P2 拟合 | 1,120：四视图 160、教师 320、教师学生 600、LS10 40 |
| P0 真实数据核验拟合 | 16 |
| 总拟合 | 1,136，不含合成单元测试 |
| 跨部署新增拟合 | 0，直接复用对应源模型 |
| 审核的预测记录 | 24,320，不是独立访问数 |
| 审核的配对映射记录 | 12,800，不是独立连接数 |
| 完整测试 | 159 项通过 |

本轮未重新解析原始 PCAP；来源冻结包含既有输入文件的哈希读取。训练使用已落盘的两侧摘要。旧 240 与 299 实验输出未覆盖。

全部内容在源/目标部署共用外层折。SS→VLESS 时只用 SS 的四个训练内容训练，VLESS 只提供留出内容的 post 测试输入；反向对称。目标部署不参与教师、学生、预处理、校准或参数选择。

## 3. P0：实际教师与优化目标诊断

### 3.1 实际交叉拟合教师质量

下表为 scheme=0、五个外层训练上下文中的内层 OOF 指标均值。每个上下文先独立计算指标，再平均；不是将重复出现的访问视为新的独立样本，F1 也不是全体记录混合后的 F1。

| 任务、部署 | 教师输入 | CE(bits) | 平均 F1 | 真实类平均概率 | 平均预测熵(bits) |
|---|---|---:|---:|---:|---:|
| 六类 SS | post | 0.6884 | 0.8963 | 0.6877 | 1.0516 |
| 六类 SS | pre | 0.4524 | 0.9354 | 0.7900 | 0.8152 |
| 六类 VLESS | post | 1.1229 | 0.6898 | 0.5454 | 1.2793 |
| 六类 VLESS | pre | 0.7132 | 0.8085 | 0.6656 | 1.0607 |
| YouTube SS | post | 0.5894 | 0.8559 | 0.7817 | 0.5215 |
| YouTube SS | pre | 0.3903 | 0.9499 | 0.8347 | 0.4520 |
| YouTube VLESS | post | 1.1360 | 0.6396 | 0.5918 | 0.7102 |
| YouTube VLESS | pre | 0.8890 | 0.6842 | 0.6264 | 0.7077 |

实际 pre 教师在这些汇总下均优于 post 教师，但 YouTube VLESS 的教师仍较弱。不能将完整训练教师每类见四个内容的性能，当作此处每类只见两个内容的 OOF 教师性能。

已经输出逐内容教师损失、真实类概率、预测熵、Brier、margin，以及外层学生退化表。教师训练侧 OOF 和学生外层测试 OOF 的成员不同，诊断只按训练上下文并列，不错误地将同一 session_id 的不同模型预测配成一条因果链。

### 3.2 软目标核验

四个真实任务/部署的首折分别核验：

- 直接硬标签 LR 与现有展开实现相同。
- α=0 回到 M0。
- 教师为 one-hot 时，α=0.5 回到同一 M0。
- 历史 M0 与新拟合预测相同，容差 1e-10。
- 保存参数重建预测与运行模型一致。
- 每个软目标权重和为 1，总权重为原训练样本数。

合成二类/六类测试另外核对 α=0/0.1/0.25/0.5 的 one-hot 等价、显式软 CE/L2 目标及梯度与展开权重形式相等。由此没有发现“样本展开改变总权重导致 C 不可比”的实现问题，但不意味着有限样本软监督必然有益。

## 4. P1：表示与双侧业务诊断

### 4.1 两套表示

scalar14 保持历史输入。distribution157 为 14 标量 + 19 维长度直方图概率 + 23 维 IAT 直方图概率 + 101 点累计曲线。每侧每直方图独立归一化，含尾桶；不使用目标部署或另一侧统计量帮助归一化。

变换诊断采用新命名口径：10 个尺度标量取 log1p(post)−log1p(pre)，4 个比例/概率/熵取差；分布版附加直方图及曲线逐维差。它不等同旧研究的严格 log-ratio Δ14。

### 4.2 四视图结果

单元为 F1 / CE(bits)。Joint 和 Transformation 使用测试 pre，只能视为诊断结果。

| 表示、任务、部署 | Post | Pre | Joint | Transformation |
|---|---|---|---|---|
| scalar14 六类 SS | 0.8927 / 0.5797 | 0.9585 / 0.3602 | 0.9498 / 0.3396 | 0.7398 / 1.0770 |
| scalar14 六类 VLESS | 0.7713 / 0.9310 | 0.8481 / 0.5910 | 0.8567 / 0.5553 | 0.7509 / 0.9025 |
| scalar14 YouTube SS | 0.8500 / 0.5773 | 0.9499 / 0.2747 | 0.8997 / 0.3165 | 0.7749 / 0.7721 |
| scalar14 YouTube VLESS | 0.6732 / 1.0680 | 0.7749 / 0.8060 | 0.7494 / 1.0558 | 0.6190 / 1.1407 |
| distribution157 六类 SS | 0.9332 / 0.5618 | 0.9666 / 0.2526 | 0.9500 / 0.2786 | 0.7691 / 0.8707 |
| distribution157 六类 VLESS | 0.9414 / 0.4142 | 0.9416 / 0.3537 | 0.9324 / 0.3154 | 0.8912 / 0.8272 |
| distribution157 YouTube SS | 0.8997 / 0.2709 | 0.9250 / 0.2489 | 0.9250 / 0.1997 | 0.7737 / 1.3376 |
| distribution157 YouTube VLESS | 0.9250 / 1.4121 | 0.8743 / 1.5138 | 0.8997 / 1.4381 | 0.7475 / 1.7958 |

业务双侧输入存在经验预测优势的情形，但并非所有任务/表示都获益，也不是 Joint 总优于 Pre。YouTube VLESS 的分布 post 模型 F1 高而 CE 高，说明少数高度自信的错误足以显著影响损失。不能只展示 F1 改善。

变换特征可以预测部分业务，但“变换预测业务”不等于业务语义解耦，也不证明它是纯协议信息。

## 5. P2：联合教师真/错配与同部署结果

J-True 在教师训练和内层 OOF 时均使用真实 `(A_i,B_i)`；J-Wrong 两处均在自身分区内按相同业务、部署和轮次交换 pre 内容，B 和 Y 始终属于 receiver。教师训练排除 OOF receiver 和 donor 的内容。不存在只在教师预测时临时破坏输入的控制。

以下为 α=0.5，单元 F1 / CE。完整 M1/M3/LS10 及 α 曲线保存在机器可读产物中。

| 表示、任务、部署 | M0 | M2 pre 真配 | J-True | J-Wrong |
|---|---|---|---|---|
| scalar14 六类 SS | 0.8927 / 0.5797 | 0.8841 / 0.6429 | 0.9008 / 0.6265 | 0.8922 / 0.6248 |
| scalar14 六类 VLESS | 0.7713 / 0.9310 | 0.7383 / 0.9996 | 0.7390 / 0.9956 | 0.7367 / 0.9830 |
| scalar14 YouTube SS | 0.8500 / 0.5773 | 0.8500 / 0.5594 | 0.8500 / 0.5622 | 0.8249 / 0.5687 |
| scalar14 YouTube VLESS | 0.6732 / 1.0680 | 0.6229 / 0.9003 | 0.6732 / 0.8990 | 0.6419 / 0.9025 |
| distribution157 六类 SS | 0.9332 / 0.5618 | 0.8528 / 0.5555 | 0.8681 / 0.5400 | 0.8854 / 0.5800 |
| distribution157 六类 VLESS | 0.9414 / 0.4142 | 0.8900 / 0.4715 | 0.8736 / 0.4814 | 0.8924 / 0.4986 |
| distribution157 YouTube SS | 0.8997 / 0.2709 | 0.9250 / 0.3677 | 0.9250 / 0.3170 | 0.8997 / 0.3474 |
| distribution157 YouTube VLESS | 0.9250 / 1.4121 | 0.8749 / 1.4168 | 0.8749 / 1.4264 | 0.8496 / 1.5306 |

对 J-True，定义 G_task=CE(M0)−CE(J-True)，G_pair=CE(J-Wrong)−CE(J-True)。主标量口径的条件性 95% 区间：

| 任务、部署 | G_task | G_pair |
|---|---|---|
| 六类 SS | −0.0469 [−0.0667, −0.0230] | −0.0018 [−0.0136, 0.0105] |
| 六类 VLESS | −0.0645 [−0.0921, −0.0360] | −0.0125 [−0.0378, 0.0125] |
| YouTube SS | 0.0151 [−0.0201, 0.0615] | 0.0065 [−0.0729, 0.0775] |
| YouTube VLESS | 0.1691 [−0.0440, 0.4440] | 0.0035 [−0.1325, 0.1193] |

distribution157 六类 SS 的 J-True 有小幅平均损失改善 0.0218，但区间 [−0.1227, 0.2362] 跨零，F1 也低于 M0。YouTube VLESS 的 J-True 相对 J-Wrong 差 0.1041 [0.0115, 0.2016]，但相对 M0 为 −0.0143，仍是“优于错配不等于优于无教师”的实例。

## 6. P3：跨部署结果

### 6.1 scalar14，α=0.5

箭头表示训练部署→测试部署。单元 F1 / CE。

| 任务、方向 | M0 | M1 | M2 | M3 | J-True | J-Wrong |
|---|---|---|---|---|---|---|
| 六类 SS→VLESS | 0.4220 / 2.8088 | 0.4063 / 2.3303 | 0.4053 / 2.4928 | 0.3617 / 2.8294 | 0.4048 / 2.5536 | 0.4137 / 2.5682 |
| 六类 VLESS→SS | 0.6615 / 0.9415 | 0.6659 / 1.0147 | 0.6217 / 1.0427 | 0.6908 / 0.9846 | 0.6768 / 1.0273 | 0.6481 / 0.9526 |
| YouTube SS→VLESS | 0.2698 / 5.5045 | 0.3162 / 4.4373 | 0.3162 / 4.0455 | 0.2857 / 3.9334 | 0.3012 / 4.4909 | 0.3309 / 4.7058 |
| YouTube VLESS→SS | 0.7103 / 1.5498 | 0.5807 / 1.7818 | 0.6931 / 1.1285 | 0.5442 / 1.7188 | 0.5807 / 1.7169 | 0.5807 / 1.6569 |

主要差值，条件性 95% 区间：

| 任务、方向、学生 | G_task | G_pair |
|---|---|---|
| 六类 SS→VLESS，M2 | 0.3160 [0.1827, 0.4495] | 0.3365 [0.1004, 0.5851] |
| 六类 SS→VLESS，J-True | 0.2552 [0.1269, 0.3857] | 0.0146 [−0.1396, 0.1666] |
| 六类 VLESS→SS，M2 | −0.1012 [−0.1969, −0.0194] | −0.0581 [−0.1956, 0.0691] |
| 六类 VLESS→SS，J-True | −0.0858 [−0.1594, −0.0247] | −0.0748 [−0.1933, 0.0271] |
| YouTube SS→VLESS，M2 | 1.4590 [0.7263, 2.2051] | −0.1121 [−0.5180, 0.3001] |
| YouTube SS→VLESS，J-True | 1.0136 [0.4954, 1.5114] | 0.2149 [−0.4117, 0.9660] |
| YouTube VLESS→SS，M2 | 0.4213 [0.0151, 0.8682] | 0.5903 [−0.2085, 1.5748] |
| YouTube VLESS→SS，J-True | −0.1672 [−0.6708, 0.3700] | −0.0600 [−0.6340, 0.4712] |

不能遗漏普通软监督控制：六类 SS→VLESS 的 M1 损失 2.3303，比 M2 的 2.4928 更低。M2 相对 M1 的优势为 −0.1625 [−0.2365, −0.0878]，所以不能把这一路径上的净改善全部归功于特有的 pre 配对信息。

YouTube SS→VLESS 的 LS10 CE=4.0087，也与 M2=4.0455 接近（M2 相对 LS10 的差 −0.0368，区间跨零）。尽管真配与 M0 差很大，仍不足以证明配对机制独有的收益。

### 6.2 distribution157，α=0.5

| 任务、方向 | M0 | M2 | J-True | J-Wrong |
|---|---|---|---|---|
| 六类 SS→VLESS | 0.4476 / 4.2093 | 0.3055 / 3.6323 | 0.3565 / 3.6593 | 0.3432 / 3.7443 |
| 六类 VLESS→SS | 0.3740 / 6.3267 | 0.4113 / 4.2271 | 0.3561 / 4.7339 | 0.4314 / 4.4769 |
| YouTube SS→VLESS | 0.3333 / 9.8781 | 0.3333 / 4.0229 | 0.3333 / 6.2096 | 0.3333 / 5.7989 |
| YouTube VLESS→SS | 0.4643 / 9.2728 | 0.3730 / 7.4012 | 0.4643 / 6.9873 | 0.5807 / 5.7920 |

存在局部正向结果：

- 六类 VLESS→SS 的 M2：G_task=2.0996 [1.6612, 2.5441]，G_pair=0.5020 [0.0469, 0.9777]。
- YouTube SS→VLESS 的 M2：G_task=5.8552 [4.3458, 7.2814]，G_pair=1.8914 [1.1580, 2.7085]；但其 F1 仍为 0.3333，不能描述为良好识别效果。

也有不支持精确对应的结果：六类 SS→VLESS 的 M2 G_pair=−0.2792，区间跨零；YouTube VLESS→SS 的 J-True G_pair=−1.1953，区间也跨零。

较强表示没有保证迁移稳定性。高维模型在源内表现很好、跨部署却产生高度自信错误，是结果中可见的风险；本轮没有进一步调正则或校准来改善这些数字。损失沿用历史 1e-12 概率下限，极端单次损失约封顶 39.86 bits，不能将被截断损失解释为精确无限尾部风险。

## 7. α 曲线：没有选取外层最优权重

下表为 scalar14 的 G_task，三列依次 α=0.1/0.25/0.5；α=0 固定为 0。它们是预设曲线，不是调参后只报告赢家。

| 任务、源部署、测试条件、学生 | 0.1 | 0.25 | 0.5 |
|---|---:|---:|---:|
| 六类 SS 同部署 M2 | −0.0103 | −0.0285 | −0.0632 |
| 六类 SS 同部署 J-True | −0.0081 | −0.0216 | −0.0469 |
| 六类 SS→VLESS M2 | 0.0860 | 0.1847 | 0.3160 |
| 六类 SS→VLESS J-True | 0.0657 | 0.1464 | 0.2552 |
| 六类 VLESS 同部署 M2 | −0.0102 | −0.0294 | −0.0686 |
| 六类 VLESS 同部署 J-True | −0.0102 | −0.0287 | −0.0645 |
| 六类 VLESS→SS M2 | −0.0105 | −0.0368 | −0.1012 |
| 六类 VLESS→SS J-True | −0.0131 | −0.0368 | −0.0858 |
| YouTube SS 同部署 M2 | 0.0070 | 0.0133 | 0.0179 |
| YouTube SS 同部署 J-True | 0.0045 | 0.0098 | 0.0151 |
| YouTube SS→VLESS M2 | 0.3515 | 0.8144 | 1.4590 |
| YouTube SS→VLESS J-True | 0.2299 | 0.5451 | 1.0136 |
| YouTube VLESS 同部署 M2 | 0.0432 | 0.0998 | 0.1677 |
| YouTube VLESS 同部署 J-True | 0.0415 | 0.0980 | 0.1691 |
| YouTube VLESS→SS M2 | 0.1096 | 0.2499 | 0.4213 |
| YouTube VLESS→SS J-True | −0.0181 | −0.0597 | −0.1672 |

减小 α 可减少六类同部署退化，但不构成新的成功方法。相反，同一个 SS 源模型的同部署和跨部署曲线方向不同，是监督与部署变化相互作用的线索，仍不是因果机制证明。

- [scalar14 权重曲线及条件性区间](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/content-generalization-20260916/mechanism-01/delivery/scalar14-alpha-curves.png)
- [distribution157 权重曲线及条件性区间](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/content-generalization-20260916/mechanism-01/delivery/distribution157-alpha-curves.png)

曲线图各子图纵轴范围不同，应读取数值而非仅比较视觉斜率。区间没有覆盖重新训练或环境变化的不确定性，也不是多比较同时置信区间。

## 8. 审核与测试

独立报告入口对全部 40 个实验单元进行以下检查：

- 从冻结队列重建源训练、源测试与目标测试成员。
- 核对教师训练/OOF 排除、真/错配双射和业务/部署/轮次约束。
- 从保存模型重建全部教师 OOF，重建学生软目标，核对实际输入矩阵哈希。
- 仅用源训练矩阵重新计算填补及标准化统计，并与保存参数比较，检查无目标域预处理污染。
- 从保存模型重建所有测试概率、真实标签与损失；核对所有预设臂及五折覆盖。
- 确认同源模型在源测试与目标测试中使用同一个 fit_id。
- scalar14 的 pre/post 及 M1/M2/M3、α=.5 全折复现历史结果。

新增负例测试故意污染临时副本的标准化统计，以及将 J-Wrong donor 改成 receiver；即使更新临时文件哈希，逻辑审核仍能拒绝。原始结果不被测试修改。

这些检查支持“当前实现按计划运行”，不排除固定采集时段、节点、网站模板等混杂，也不能把回顾性内部测试升级为外部盲测。

## 9. 理论与机制解释边界

联合教师条件一致性是理想总体性质；理想 post 教师也具有一致性。它不保证有限样本、每类仅两个内容的线性 OOF 教师优于 pre 教师，更不保证目标部署上的条件分布保持不变。

现有结果支持继续区分三个问题：

1. 双侧诊断能否利用额外输入？——若干任务中可以。
2. 教师输出能否形成适合单侧学生的监督？——并非由教师本身较好自动保证。
3. 这种监督是否改善迁移，且优势来自精确对应？——局部有正向结果，但方向、表示和普通软监督控制揭示了重要限制。

不能据本轮宣称语义解耦、变换可逆、获得真实互信息值或实现普适单侧业务闭环。也不能据联合教师未胜出就否定全部配对学习方法。

## 10. 产物与复跑入口

配置：[mechanism 配置](F:/Program/VSCode/MyGit/ProxyAnalysis/configs/content-generalization-20260916-mechanism.yaml)。

- [来源冻结清单](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/content-generalization-20260916/mechanism-01/contract/source-manifest.json)
- [P0 软目标核验](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/content-generalization-20260916/mechanism-01/p0-diagnostics/soft-target-sanity.json)
- [P0 实际教师汇总](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/content-generalization-20260916/mechanism-01/p0-diagnostics/teacher-summary.json)
- [表示字典](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/content-generalization-20260916/mechanism-01/representations/representation-dictionary.json)
- [完整模型指标](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/content-generalization-20260916/mechanism-01/report/metrics.json)
- [全部收益及区间](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/content-generalization-20260916/mechanism-01/report/paired-gains.parquet)
- [逐内容差值](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/content-generalization-20260916/mechanism-01/report/content-effects.parquet)
- [源/目标迁移差](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/content-generalization-20260916/mechanism-01/report/transfer-gaps.json)
- [独立审核结果](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/content-generalization-20260916/mechanism-01/report/validation.json)
- [下一阶段待确认任务清单](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/content-generalization-20260916/mechanism-01/delivery/next-sensitivity-review.json)

新增模块位于 `src/proxy_analysis/crosscontent/`：mechanism_contract、teacher_diagnostics、business_representations、joint_teacher、mechanism_report、mechanism_delivery。为直接复用同一个源模型，P1/P2/P3 在 joint_teacher 中按实验单元顺序执行；独立审核后分目录输出三阶段结果，而不是分别重训。

已执行命令顺序：

```powershell
$env:PYTHONPATH='src'
& D:/Tools/Anaconda/envs/Pytorch312/python.exe -m proxy_analysis.crosscontent.mechanism_contract
& D:/Tools/Anaconda/envs/Pytorch312/python.exe -m proxy_analysis.crosscontent.teacher_diagnostics
& D:/Tools/Anaconda/envs/Pytorch312/python.exe -m proxy_analysis.crosscontent.joint_teacher
& D:/Tools/Anaconda/envs/Pytorch312/python.exe -m proxy_analysis.crosscontent.mechanism_report
& D:/Tools/Anaconda/envs/Pytorch312/python.exe -m proxy_analysis.crosscontent.mechanism_delivery
```

不要在现有结果目录直接重复全流程。冻结、诊断、报告和交付目录拒绝覆盖；训练入口只能复用完整且哈希匹配的已完成单元，遇到未完成单元需审核。本轮新配置、代码、报告为本地工作，尚未提交/推送。

## 11. 当前确认节点

首轮 P0–P3 已结束，不因局部正向结果擅自挑选赢家扩展。

下一阶段按原计划固定为：

1. 240 队列补教师 scheme=1、2。
2. 299 保守队列运行 scheme=0，保持唯一 MDN 恢复访问排除及共同轮次训练池。
3. 两部分均固定 scalar14、α=.5、M0/M1/M2/M3/J-True/J-Wrong 六臂；同时报告同部署与双向跨部署。

已生成 60 个待确认实验单元，预计 800 次新拟合：240 的两个分法 520 次，299 的主分法 280 次。240 的 M0 仅在训练成员完全相同的前提下复用；跨部署不增加拟合。

这部分尚未执行。P4 少指标变换复核、非线性模型、自动选择 α、全 300 候选实验也尚未启动。下一步应确认是否执行上述固定敏感性，而不是先对已有最高分进行优化。
