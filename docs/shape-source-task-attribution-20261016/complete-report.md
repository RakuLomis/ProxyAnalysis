# 固定映射形状来源替换的业务归因实验报告

日期：2026-10-16。ST1 已完成固定48个源内任务、192个新LR和4608行预测；来源、数值、预测和统计重放均通过。未读取实际目标H/U，未训练新映射或表征网络。

## 核心结论

在P质量与位置背景下，PP相对PG的U业务F1差为 -0.2658 个百分点，家族区间跨零。在G背景下，GP相对GG为 -0.1901 个百分点，家族区间跨零。

新组合GP相对完整PP为 +0.2624 个百分点，家族区间跨零。这三项分别回答形状的条件性分类作用和组合是否形成新增收益，不能相互替代。GP的C代价实践筛查为 **通过**。

## 数据和权限

沿用Extend的96维访问直方图及六个domain乘activity业务。仅使用outer f0训练范围内的24个内容，每业务4内容。四个源内留出折每次训练18内容、查询6内容；同内容的重复、两侧及内部连接整体分组，不随机拆flow。

每任务两个源部署提供144个真实访问的独立pre包与post包；伪目标C提供48个访问，共192次真实训练访问。pre144行不代表额外144次独立采集。伪目标U训练内容的两侧均禁止读取。480计算行只是四槽重复利用，不是480次独立访问。

| role_target组织角色 | query_deployment实际查询部署 | 源部署 |
| --- | --- | --- |
| shadowsocks | vless | trojan、vmess |
| vless | trojan | shadowsocks、vmess |
| trojan | vmess | shadowsocks、vless |
| vmess | shadowsocks | vless、trojan |

48任务为4角色乘3遮蔽组乘4内折。查询共1152次角色暴露、384次不同部署访问、24个不同内容。四臂产生4608行预测，不能将其当作4608份独立样本。role_target并非该行成绩所对应的流量部署。

G0遮蔽GitHub仓库和YouTube搜索，G1遮蔽Bing搜索和Wikipedia文章，G2遮蔽MDN文档和YouTube视频播放。每次仍是完整六分类。

## 固定方法与几何

P/G分别为冻结的真配与匿名组全仿射前向映射，不是旧的post恢复网络。十个直方图块全部参与，不按SD1的D单元筛选。前四块9箱、后六块10箱；固定分解为10维质量M、10维位置L、76维剩余形状R。

| 臂 | 质量及位置ML来源 | 形状R来源 |
| --- | --- | --- |
| PP | P | P |
| PG | P | G |
| GP | G | P |
| GG | G | G |

混合在原频率坐标中执行：d_raw=scale乘(zG减zP)，r为各块PR投影；PG=zP+r/scale，GP=zG减r/scale。PP/GG直接保留原辅助矩阵，不旋转重算。没有把位置锁回pre，没有截负、重新归一化或合法性筛选。混合后的负值和块质量偏离在view-diagnostics中全量记录，仅作描述。

原映射前向最大绝对重放误差 0.000e+00；几何恒等最大归一化误差 4.441e-16。非均匀尺度的负夹具能检出错误的标准化空间投影。

## 训练材料和数值配置

每任务依次为源post144行、CORAL144行、映射pre144行、C post48行，CE总质量分别1/3、0.3、1/30、1/3。逐行标签、质量和顺序直接继承原CT/JA槽；总质量1，各类别质量1/6，PP与既有纯classification张量精确一致。

模型为96到6的LR，原参数582个。目标是带权CE之和加0.0005乘(1+t)乘W平方和；bias不惩罚，不额外除以行数或类别数。eta/t逐角色继承，eta分布100四项、0.1三十六项、1四项、10四项；t分布4三十二项、0.25四项、0四项、1八项。

所有四臂统一零初始化，CUDA float64，可逆Cholesky预条件化，原v4 LBFGS，max_iter=2000、max_eval=10000、history=100、strong_wolfe。原坐标最大梯度门1e-5，目标及梯度重放门1e-10。未新增Newton精炼。旧纯PP模型因经过额外精炼，仅作训练目标兼容性审计，没有混入主结果。

实际192个物理拟合全部验收；工程先导16个已包含其中，无额外seed矩阵。独立原坐标梯度最大 9.990e-06，目标重放误差最大 0.000e+00，梯度重放误差最大 4.770e-18。

## 完整总体结果

F1和概率误差均为比例或原单位，不是百分数；F1越高越好，CE和Brier越低越好。

| arm | F1_U | F1_C | F1_all | CE_U | CE_C | CE_all | Brier_U | Brier_C | Brier_all |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| GG | 0.726538 | 0.780666 | 0.762623 | 1.134658 | 0.673779 | 0.827406 | 0.498164 | 0.276605 | 0.350458 |
| GP | 0.724637 | 0.779105 | 0.760949 | 1.163091 | 0.683426 | 0.843314 | 0.504988 | 0.276506 | 0.352667 |
| PG | 0.724672 | 0.777076 | 0.759608 | 1.157252 | 0.657978 | 0.824403 | 0.507373 | 0.275296 | 0.352655 |
| PP | 0.722013 | 0.784472 | 0.763652 | 1.161432 | 0.669327 | 0.833362 | 0.509143 | 0.272870 | 0.351628 |

## 三项主要比较

先合并四内折，再为每个角色乘遮蔽组建立完整6乘6混淆矩阵。U/C F1提取自该矩阵中的两类或四类，保留其他业务造成的FP。12单元等权，不平均内折F1。差值均为候选减参照。

| comparison | F1_U_delta | CI95 | family_CI | family_result | CE_U_delta | Brier_U_delta |
| --- | --- | --- | --- | --- | --- | --- |
| GP-GG | -0.001901 | [-0.016552139781911564, 0.013905233970882974] | [-0.020240020814758706, 0.017085807368809505] | 家族区间跨零 | 0.028432 | 0.006824 |
| GP-PP | 0.002624 | [-0.009298822370487042, 0.01741686990642038] | [-0.011733134160948483, 0.02131688493984428] | 家族区间跨零 | 0.001659 | -0.004154 |
| PP-PG | -0.002658 | [-0.016610033516544324, 0.011448835736750793] | [-0.019858130122242763, 0.014098799902096544] | 家族区间跨零 | 0.004179 | 0.001770 |

10000次六业务分层的共同内容簇bootstrap，每业务4内容有放回抽4；同内容次数在部署、遮蔽、重复和四臂共享。三项主F1差同时报告95%描述区间和Bonferroni 98.3333%家族区间。CE、Brier和交互只作95%描述区间，详见primary-comparisons.json。

交互I=PP减PG减GP加GG，点估计 -0.000758，95%区间 [-0.013098020194846717, 0.010657914354268294]。这是训练材料的非加性，不是物理因果交互或互信息。

## 各查询部署结果

各部署先对三个遮蔽组等权；不是按role_target名称解释部署。

| role_target | query_deployment | arm | F1_U | F1_C | F1_all | CE_U | Brier_U |
| --- | --- | --- | --- | --- | --- | --- | --- |
| shadowsocks | vless | GG | 0.779968 | 0.776295 | 0.777519 | 1.021968 | 0.402330 |
| shadowsocks | vless | GP | 0.788492 | 0.782649 | 0.784597 | 1.035055 | 0.401901 |
| shadowsocks | vless | PG | 0.779968 | 0.776295 | 0.777519 | 1.079661 | 0.409472 |
| shadowsocks | vless | PP | 0.780847 | 0.786322 | 0.784497 | 1.058050 | 0.406515 |
| trojan | vmess | GG | 0.688610 | 0.757337 | 0.734428 | 1.299680 | 0.565391 |
| trojan | vmess | GP | 0.682534 | 0.753157 | 0.729616 | 1.309357 | 0.573511 |
| trojan | vmess | PG | 0.691696 | 0.759356 | 0.736803 | 1.321593 | 0.573743 |
| trojan | vmess | PP | 0.684962 | 0.752781 | 0.730175 | 1.341881 | 0.579959 |
| vless | trojan | GG | 0.710523 | 0.783892 | 0.759435 | 0.958767 | 0.500875 |
| vless | trojan | GP | 0.713097 | 0.778421 | 0.756647 | 1.034428 | 0.521880 |
| vless | trojan | PG | 0.710523 | 0.783892 | 0.759435 | 0.975331 | 0.506602 |
| vless | trojan | PP | 0.714807 | 0.790398 | 0.765201 | 1.022609 | 0.510636 |
| vmess | shadowsocks | GG | 0.727050 | 0.805140 | 0.779110 | 1.258218 | 0.524061 |
| vmess | shadowsocks | GP | 0.714423 | 0.802194 | 0.772937 | 1.273522 | 0.522662 |
| vmess | shadowsocks | PG | 0.716500 | 0.788763 | 0.764675 | 1.252424 | 0.539673 |
| vmess | shadowsocks | PP | 0.707437 | 0.808387 | 0.774737 | 1.223186 | 0.539461 |

最差部署完整保留：

| arm | query_deployment | F1_U |
| --- | --- | --- |
| GG | vmess | 0.688610 |
| GP | vmess | 0.682534 |
| PG | vmess | 0.691696 |
| PP | vmess | 0.684962 |

## 错误修复和概率代价

下表是角色暴露计数，同一次访问会跨遮蔽重复，不能作独立样本显著性。repair指候选正确而参照错误，new_error相反。CE和Brier列是该组差值之和。

| comparison | is_U | case | exposures | CE_delta_sum | Brier_delta_sum |
| --- | --- | --- | --- | --- | --- |
| GP-GG | False | both_correct | 619 | -1.183263 | -0.820932 |
| GP-GG | False | both_wrong | 135 | 9.076457 | 1.165609 |
| GP-GG | False | new_error | 6 | 6.335620 | 3.623535 |
| GP-GG | False | repair | 8 | -6.820497 | -4.044220 |
| GP-GG | True | both_correct | 252 | -0.248203 | -0.465387 |
| GP-GG | True | both_wrong | 123 | 4.191149 | 0.268714 |
| GP-GG | True | new_error | 6 | 8.380661 | 3.946596 |
| GP-GG | True | repair | 3 | -1.405609 | -1.129435 |
| GP-PP | False | both_correct | 626 | -0.919508 | -0.568892 |
| GP-PP | False | both_wrong | 137 | 10.821928 | 2.504475 |
| GP-PP | False | new_error | 4 | 1.411490 | 1.303935 |
| GP-PP | False | repair | 1 | -0.485802 | -0.447288 |
| GP-PP | True | both_correct | 250 | -1.086881 | -0.989434 |
| GP-PP | True | both_wrong | 124 | -3.443097 | -1.827244 |
| GP-PP | True | new_error | 5 | 6.479739 | 2.384440 |
| GP-PP | True | repair | 5 | -1.312754 | -1.163082 |
| PP-PG | False | both_correct | 619 | 0.005946 | -0.085284 |
| PP-PG | False | both_wrong | 134 | 13.668500 | 2.118879 |
| PP-PG | False | new_error | 4 | 2.374863 | 1.893311 |
| PP-PG | False | repair | 11 | -7.333834 | -5.789774 |
| PP-PG | True | both_correct | 251 | -1.232404 | -0.475308 |
| PP-PG | True | both_wrong | 123 | 1.556968 | -0.023168 |
| PP-PG | True | new_error | 6 | 2.163041 | 1.933100 |
| PP-PG | True | repair | 4 | -0.882728 | -0.754816 |

共同错误的置信度及真类概率、逐内容修复与新增错误均保存在error-flips和shared-error-probability-cost。若分类点估计变好而概率代价变差，两者同时保留，本轮不追加温度校准。

## C业务实践筛查

GP减PP的F1_C总体差 -0.5367 个百分点，上限允许损失1个百分点。各部署允许损失2个百分点：

| query_deployment | F1_C_delta | passed |
| --- | --- | --- |
| shadowsocks | -0.006193 | True |
| trojan | -0.011977 | True |
| vless | -0.003673 | True |
| vmess | 0.000376 | True |

筛查通过不等于统计非劣效，也不构成正式60角色评价授权。

## 独立核验和计算量

全部模型由封存训练槽独立复算原目标和解析梯度；推理用展开后的原始输入仿射式重放，最大概率差 7.661e-15。完整混淆矩阵独立逐类别重建；全部10000次bootstrap用NumPy独立重算，最大指标差 6.661e-16，家族区间差 1.492e-16。

累计活动预算记账 135.05 秒，上限3600秒；其中求解器记录拟合时间合计 98.22 秒，单模型中位数 0.398 秒，最大 10.087 秒。活动段包含必要的封装与槽加载开销，采用保守记账，不把它当作纯GPU核时间。源内优化、预测和统计均未扩大原拟合上限。

读取台账覆盖ST1受控适配器，不是操作系统级系统调用审计。重新核验全部 1013 个登记输入散列，旧产物未变。顺序为训练槽封存、全部模型封存、全部预测封存、源内标签开放。实际H/U、query-pre、native、PCAP和含query的旧反馈包读取均为0。

## 适用范围和停止边界

本轮是同批历史数据上的固定材料干预。eta/t的旧选择已使用过相关内折内容；模型固定的bootstrap不能消除回顾性选择，也不是外部验证。源内24内容不能替代实际目标或异批次数据。

形状来源替换还可能改变两种映射输出的联合结构。因此某个混合臂的退化不能自动解释为所有形状无用，也不能仅凭一个正方向宣布精确身份具有普遍不可替代作用。SD1原来的停止记录不变；本轮没有恢复LOC保护，没有估计信息量，没有证明协议语义分解。

本轮到此结项。不会自动打开实际H/U、训练G/GAN、搜索子集或扩大分类器。是否进入新的全角色评价，需要另行确认。

## 产物索引

- 机器可读合同及封存：contract.json、seal.json、slots-complete.json、models-complete.json、predictions-complete.json、scores-complete.json。
- 来源与成员：source-bindings.parquet、role-membership.parquet、slot-row-ledger.parquet、compatibility.parquet、ledger.json。
- 几何与数值：geometry-synthetic-tests.parquet、geometry-tests.parquet、affine-replay.parquet、view-diagnostics.parquet、independent-endpoint-checks.parquet、verification.json。
- 分项结果：metrics-by-role-group.parquet、metrics-by-query-deployment.parquet、metrics-by-business.parquet、metrics-by-content.parquet、confusion-matrices.parquet。
- 比较和错误：primary-comparisons.json、interaction.json、bootstrap.npz、error-flips.parquet、error-flip-summary.parquet、shared-error-probability-cost.parquet、C-practical-screen.json。
- 完成状态：completion.json、budget.json、model-endpoints.parquet。

原子方案位于plan/ST1-shape-source-downstream-attribution-plan-20261016.md。全部结果路径相对于outputs/shape-source-task-attribution-20261016/run-01。
