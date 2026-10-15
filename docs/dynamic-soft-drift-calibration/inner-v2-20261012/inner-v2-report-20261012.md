# 可微内层第二版源内资格报告

2026年10月12日。本轮执行了完整q=1训练槽位Cholesky坐标与配套固定谱界步长。当前状态为`stop_inner_quality_not_met`。原业务目标、基础映射、损失权重和数据权限不变；有限训练轨迹已改变，不与旧Q64混装。

## 执行范围与复用

同一12个源内任务，P/G共24个训练问题；P与T-P共享相同内层。原24个q=1收敛参照按SHA和数值验收直接复用，重复拟合为零。新基础映射拟合为零，实际目标C/U/H数值及PCAP读取为零。

使用Pytorch312、PyTorch 2.5.1、CUDA 12.4和NVIDIA GeForce RTX 4060 Ti。模型运算全部CUDA float64，没有CPU训练或推理回退。

## 坐标与步长

矩阵从q=1的完整480行加权槽位构造，最后一维bias不正则。新参数经冻结L逆解码，原W仍承担0.0005(1+t)平方惩罚，没有把正则改施在新参数上。构造函数只接收训练字段，不接收源内留出post或标签。

步长来自新坐标下的加权谱范数上界，固定安全因子1+1e-12。谱界涵盖q范围[0,2]，不是按留出CE选取。记录各块漂移范数及q=1／q_alt的独立Gram谱界见coordinates表。

新固定步长范围为1.06820610474e-07至1.05731587979e-05；旧步长范围为1.91943829362e-08至2.23125349537e-06。原／新坐标目标重放最大误差4.4408920985e-16，梯度重放最大误差2.91433543964e-15。训练目标及坐标等价检查通过，不等于有限轨迹近似质量通过。

## 已预登记的起点质量门

每任务同时要求目标差不超过0.01、剩余目标差距绝对值不超过1%、原梯度不超过1e-3、8行平均绝对CE差不超过0.02、逐行不超过0.05、概率总变差均值不超过0.02且逐行不超过0.05、相对logit RMSE不超过0.10，并满足高margin预测一致及至多一行弱margin改变。全部24组合通过才选择K。

这些是数值近似门，不是业务成功门，也不要求新CE更低。源内反馈用于长度资格，不再是该选择程序的独立验证。门限没有按本轮结果回调。

## 起点质量结果

|   K | arm   |   tasks |   passed |   remaining_min |   remaining_median |   remaining_max |     CE_new |      CE_ref |   CE_mean_abs |          TV |   logit_RMSE |   gradient_max |
|----:|:------|--------:|---------:|----------------:|-------------------:|----------------:|-----------:|------------:|--------------:|------------:|-------------:|---------------:|
|  64 | D-G   |      12 |        0 |     0.998660796 |        0.999251162 |     0.999986248 | 1.79110117 | 0.998763935 |    1.50218253 | 0.692733081 |   3.84007052 |    0.253113471 |
|  64 | D-P   |      12 |        0 |     0.998607548 |        0.999237069 |     0.999986244 | 1.79107239 | 1.02869694  |    1.4854123  | 0.691017885 |   3.81891461 |    0.253113471 |
| 128 | D-G   |      12 |        0 |     0.997323338 |        0.998502907 |     0.999972496 | 1.79044366 | 0.998763935 |    1.50164416 | 0.692584529 |   3.83961718 |    0.253104649 |
| 128 | D-P   |      12 |        0 |     0.997216981 |        0.998474739 |     0.999972488 | 1.79038617 | 1.02869694  |    1.48485047 | 0.690855655 |   3.81843587 |    0.253104649 |
| 256 | D-G   |      12 |        0 |     0.994653663 |        0.99700814  |     0.999944992 | 1.78913105 | 0.998763935 |    1.50056918 | 0.692287271 |   3.83871129 |    0.253087004 |
| 256 | D-P   |      12 |        0 |     0.994441506 |        0.996951886 |     0.999944976 | 1.78901632 | 1.02869694  |    1.48372872 | 0.690531016 |   3.81747925 |    0.253087003 |

各门失败数量可重叠，不能相加当作失败任务数：

|   K |   objective_pass |   remaining_pass |   gradient_pass |   CE_mean_pass |   CE_row_pass |   TV_mean_pass |   TV_row_pass |   logit_pass |   decisions_pass |
|----:|-----------------:|-----------------:|----------------:|---------------:|--------------:|---------------:|--------------:|-------------:|-----------------:|
|  64 |               24 |               24 |              24 |             24 |            24 |             24 |            24 |           24 |               20 |
| 128 |               24 |               24 |              24 |             24 |            24 |             24 |            24 |           24 |               20 |
| 256 |               24 |               24 |              24 |             24 |            24 |             24 |            24 |           24 |               20 |

逐任务完整表包括未截断的剩余比例、原梯度、CE差、概率差、相对logits和改变类别。数据行包含重复角色暴露，不是独立内容数量。没有用更低的源内CE掩盖与参照的近似失配。

## 长度选择与条件阶段

候选长度按64、128、256顺序执行，全任务从零开始；没有逐任务选择不同K。选定长度为None。起点累计执行72条单任务前向轨迹、10752次内层更新。

新版梯度扫描及q_alt参照未执行，因为没有起点资格通过的K。

新版梯度记录：未执行，无新版Q求导通过结论。

扰动阶段记录：未执行，新增q_alt收敛LR为零，Delta反馈可靠性尚未评价。

## 当前结论和停止边界

新坐标与步长可能显著推进训练，但平均改善、目标降低或坐标等价并不自动满足逐任务近似资格。通过量与失败项应分开看。本轮不支持任何新的动态约束业务增益数字。

若最大长度仍未合格，应接受这个限定内层候选未达到近似要求，不继续扩大K、放宽门或调整步长。尚未执行的求导与固定扰动不能写成失败，亦不能提前放行。下一项数值修订必须独立登记并由用户确认。

所有结果交付后暂停。没有正式q学习、60角色训练或180个最终分类器授权。原先导失败、上一轮修复完成和24个参照保持不变。

## 复现产物

代码目录为eval/dynamic_soft_drift_inner_v2，运行目录为outputs/dynamic-soft-drift-inner-v2-20261012/run-01。contract、reference-reuse、coordinates、quality-models、q-one-quality、summary、failure-path、selection及阶段读取账本构成复核链。条件阶段若执行，会另存gradients与perturbation-models。

完整逐任务结果：

| role_id                          | arm   |   K |      J_new |       J_ref |   remaining |    gradient |     CE_new |      CE_ref |   CE_mean_abs |     TV_mean |   logit_RMSE | passed   | failed_gates                                                              |
|:---------------------------------|:------|----:|-----------:|------------:|------------:|------------:|-----------:|------------:|--------------:|------------:|-------------:|:---------|:--------------------------------------------------------------------------|
| main/f0/shadowsocks/G0/i1/trojan | D-P   |  64 | 1.79165222 | 0.237805607 | 0.999930981 | 0.253113471 | 1.79164381 | 0.6237089   |   1.88705222  | 0.785760921 |   4.70289855 | False    | ['objective' 'remaining' 'gradient' 'CE_mean' 'CE_row' 'TV_mean' 'TV_row' |
|                                  |       |     |            |             |             |             |            |             |               |             |              |          |  'logit' 'decisions']                                                     |
| main/f0/shadowsocks/G1/i1/trojan | D-P   |  64 | 1.79173214 | 0.12371521  | 0.999983615 | 0.21727796  | 1.79174123 | 1.24813422  |   1.61317032  | 0.724154043 |   4.69825491 | False    | ['objective' 'remaining' 'gradient' 'CE_mean' 'CE_row' 'TV_mean' 'TV_row' |
|                                  |       |     |            |             |             |             |            |             |               |             |              |          |  'logit' 'decisions']                                                     |
| main/f0/shadowsocks/G2/i1/trojan | D-P   |  64 | 1.79173657 | 0.126917412 | 0.999986244 | 0.226064617 | 1.7917438  | 1.15299127  |   2.20748859  | 0.761788246 |   4.39648229 | False    | ['objective' 'remaining' 'gradient' 'CE_mean' 'CE_row' 'TV_mean' 'TV_row' |
|                                  |       |     |            |             |             |             |            |             |               |             |              |          |  'logit' 'decisions']                                                     |
| main/f0/vless/G0/i1/shadowsocks  | D-P   |  64 | 1.78988434 | 0.243025387 | 0.99878925  | 0.233005642 | 1.79000108 | 0.60251542  |   1.72304682  | 0.738219085 |   4.24589922 | False    | ['objective' 'remaining' 'gradient' 'CE_mean' 'CE_row' 'TV_mean' 'TV_row' |
|                                  |       |     |            |             |             |             |            |             |               |             |              |          |  'logit' 'decisions']                                                     |
| main/f0/vless/G1/i1/shadowsocks  | D-P   |  64 | 1.79010939 | 0.234947452 | 0.998940088 | 0.216252836 | 1.79100964 | 0.901905073 |   1.18010377  | 0.670417723 |   2.37287379 | False    | ['objective' 'remaining' 'gradient' 'CE_mean' 'CE_row' 'TV_mean' 'TV_row' |
|                                  |       |     |            |             |             |             |            |             |               |             |              |          |  'logit' 'decisions']                                                     |
| main/f0/vless/G2/i1/shadowsocks  | D-P   |  64 | 1.7911938  | 0.177562288 | 0.999649565 | 0.223353353 | 1.79150067 | 1.49856623  |   0.943457313 | 0.627328044 |   4.18988144 | False    | ['objective' 'remaining' 'gradient' 'CE_mean' 'CE_row' 'TV_mean' 'TV_row' |
|                                  |       |     |            |             |             |             |            |             |               |             |              |          |  'logit' 'decisions']                                                     |
| main/f0/trojan/G0/i1/shadowsocks | D-P   |  64 | 1.78960176 | 0.242187332 | 0.998607548 | 0.208025676 | 1.78977159 | 0.785382313 |   1.80605316  | 0.711848061 |   4.50950946 | False    | ['objective' 'remaining' 'gradient' 'CE_mean' 'CE_row' 'TV_mean' 'TV_row' |
|                                  |       |     |            |             |             |             |            |             |               |             |              |          |  'logit' 'decisions']                                                     |
| main/f0/trojan/G1/i1/shadowsocks | D-P   |  64 | 1.78982506 | 0.228075677 | 0.998762913 | 0.198034682 | 1.79089372 | 1.27411935  |   1.44863409  | 0.651086047 |   2.60354763 | False    | ['objective' 'remaining' 'gradient' 'CE_mean' 'CE_row' 'TV_mean' 'TV_row' |
|                                  |       |     |            |             |             |             |            |             |               |             |              |          |  'logit' 'decisions']                                                     |
| main/f0/trojan/G2/i1/shadowsocks | D-P   |  64 | 1.79010349 | 0.230312873 | 0.998939458 | 0.219966375 | 1.79106986 | 1.47490412  |   1.23102952  | 0.612738223 |   3.27642794 | False    | ['objective' 'remaining' 'gradient' 'CE_mean' 'CE_row' 'TV_mean' 'TV_row' |
|                                  |       |     |            |             |             |             |            |             |               |             |              |          |  'logit']                                                                 |
| main/f0/vmess/G0/i1/shadowsocks  | D-P   |  64 | 1.79021912 | 0.195441078 | 0.999035064 | 0.217239866 | 1.79055479 | 0.975630867 |   1.70454777  | 0.710889738 |   4.08192349 | False    | ['objective' 'remaining' 'gradient' 'CE_mean' 'CE_row' 'TV_mean' 'TV_row' |
|                                  |       |     |            |             |             |             |            |             |               |             |              |          |  'logit']                                                                 |
| main/f0/vmess/G1/i1/shadowsocks  | D-P   |  64 | 1.79122823 | 0.113386817 | 0.999683478 | 0.217654346 | 1.79155378 | 1.15055229  |   0.94184118  | 0.667636528 |   3.01913842 | False    | ['objective' 'remaining' 'gradient' 'CE_mean' 'CE_row' 'TV_mean' 'TV_row' |
|                                  |       |     |            |             |             |             |            |             |               |             |              |          |  'logit' 'decisions']                                                     |
| main/f0/vmess/G2/i1/shadowsocks  | D-P   |  64 | 1.79085566 | 0.18048101  | 0.999439074 | 0.214617572 | 1.79138471 | 0.655953187 |   1.1385229   | 0.630347959 |   3.73013819 | False    | ['objective' 'remaining' 'gradient' 'CE_mean' 'CE_row' 'TV_mean' 'TV_row' |
|                                  |       |     |            |             |             |             |            |             |               |             |              |          |  'logit' 'decisions']                                                     |
| main/f0/shadowsocks/G0/i1/trojan | D-G   |  64 | 1.79165222 | 0.23779931  | 0.999930981 | 0.253113471 | 1.79164378 | 0.620741442 |   1.88412459  | 0.785392635 |   4.70235398 | False    | ['objective' 'remaining' 'gradient' 'CE_mean' 'CE_row' 'TV_mean' 'TV_row' |
|                                  |       |     |            |             |             |             |            |             |               |             |              |          |  'logit' 'decisions']                                                     |
| main/f0/shadowsocks/G1/i1/trojan | D-G   |  64 | 1.79173215 | 0.124683614 | 0.999983613 | 0.217102683 | 1.79174153 | 1.266939    |   1.6262993   | 0.727324182 |   4.51472044 | False    | ['objective' 'remaining' 'gradient' 'CE_mean' 'CE_row' 'TV_mean' 'TV_row' |
|                                  |       |     |            |             |             |             |            |             |               |             |              |          |  'logit' 'decisions']                                                     |
| main/f0/shadowsocks/G2/i1/trojan | D-G   |  64 | 1.79173657 | 0.12697109  | 0.999986248 | 0.227456091 | 1.79174425 | 1.41182511  |   2.45476141  | 0.748510887 |   4.43460652 | False    | ['objective' 'remaining' 'gradient' 'CE_mean' 'CE_row' 'TV_mean' 'TV_row' |
|                                  |       |     |            |             |             |             |            |             |               |             |              |          |  'logit' 'decisions']                                                     |
| main/f0/vless/G0/i1/shadowsocks  | D-G   |  64 | 1.78994554 | 0.246497902 | 0.998826135 | 0.23232499  | 1.79007345 | 0.341174378 |   1.52674343  | 0.743114529 |   4.4023864  | False    | ['objective' 'remaining' 'gradient' 'CE_mean' 'CE_row' 'TV_mean' 'TV_row' |
|                                  |       |     |            |             |             |             |            |             |               |             |              |          |  'logit' 'decisions']                                                     |
| main/f0/vless/G1/i1/shadowsocks  | D-G   |  64 | 1.79017843 | 0.237188078 | 0.998982974 | 0.215176197 | 1.7910342  | 0.788343789 |   1.22155087  | 0.693300093 |   2.59992942 | False    | ['objective' 'remaining' 'gradient' 'CE_mean' 'CE_row' 'TV_mean' 'TV_row' |
|                                  |       |     |            |             |             |             |            |             |               |             |              |          |  'logit' 'decisions']                                                     |
| main/f0/vless/G2/i1/shadowsocks  | D-G   |  64 | 1.79120951 | 0.175727918 | 0.999659685 | 0.22321917  | 1.79151355 | 1.49900085  |   1.02915921  | 0.619078056 |   4.11749633 | False    | ['objective' 'remaining' 'gradient' 'CE_mean' 'CE_row' 'TV_mean' 'TV_row' |
|                                  |       |     |            |             |             |             |            |             |               |             |              |          |  'logit' 'decisions']                                                     |
| main/f0/trojan/G0/i1/shadowsocks | D-G   |  64 | 1.78968833 | 0.245211676 | 0.998660796 | 0.205880961 | 1.78988793 | 0.601479276 |   1.61124407  | 0.716814087 |   4.32328786 | False    | ['objective' 'remaining' 'gradient' 'CE_mean' 'CE_row' 'TV_mean' 'TV_row' |
|                                  |       |     |            |             |             |             |            |             |               |             |              |          |  'logit' 'decisions']                                                     |
| main/f0/trojan/G1/i1/shadowsocks | D-G   |  64 | 1.78992406 | 0.230672148 | 0.998824273 | 0.197098237 | 1.79092665 | 1.15474592  |   1.40311121  | 0.677806388 |   2.78192122 | False    | ['objective' 'remaining' 'gradient' 'CE_mean' 'CE_row' 'TV_mean' 'TV_row' |
|                                  |       |     |            |             |             |             |            |             |               |             |              |          |  'logit' 'decisions']                                                     |
| main/f0/trojan/G2/i1/shadowsocks | D-G   |  64 | 1.79016356 | 0.230886645 | 0.998977554 | 0.218314314 | 1.79110991 | 1.62625846  |   1.33637565  | 0.613309814 |   3.267379   | False    | ['objective' 'remaining' 'gradient' 'CE_mean' 'CE_row' 'TV_mean' 'TV_row' |
|                                  |       |     |            |             |             |             |            |             |               |             |              |          |  'logit']                                                                 |
| main/f0/vmess/G0/i1/shadowsocks  | D-G   |  64 | 1.79023958 | 0.194758533 | 0.999048286 | 0.217973814 | 1.790576   | 1.05905654  |   1.8300647   | 0.702493259 |   4.05101467 | False    | ['objective' 'remaining' 'gradient' 'CE_mean' 'CE_row' 'TV_mean' 'TV_row' |
|                                  |       |     |            |             |             |             |            |             |               |             |              |          |  'logit']                                                                 |
| main/f0/vmess/G1/i1/shadowsocks  | D-G   |  64 | 1.79125185 | 0.114729373 | 0.999697311 | 0.216226018 | 1.79156183 | 0.888717954 |   0.987525768 | 0.667754036 |   3.15190187 | False    | ['objective' 'remaining' 'gradient' 'CE_mean' 'CE_row' 'TV_mean' 'TV_row' |
|                                  |       |     |            |             |             |             |            |             |               |             |              |          |  'logit' 'decisions']                                                     |
| main/f0/vmess/G2/i1/shadowsocks  | D-G   |  64 | 1.79087934 | 0.179681146 | 0.999454039 | 0.21454693  | 1.79140091 | 0.726884495 |   1.11523014  | 0.617899001 |   3.73384854 | False    | ['objective' 'remaining' 'gradient' 'CE_mean' 'CE_row' 'TV_mean' 'TV_row' |
|                                  |       |     |            |             |             |             |            |             |               |             |              |          |  'logit' 'decisions']                                                     |
| main/f0/shadowsocks/G0/i1/trojan | D-P   | 128 | 1.79154497 | 0.237805607 | 0.999861967 | 0.253104649 | 1.79152817 | 0.6237089   |   1.88695057  | 0.785741168 |   4.7028354  | False    | ['objective' 'remaining' 'gradient' 'CE_mean' 'CE_row' 'TV_mean' 'TV_row' |
|                                  |       |     |            |             |             |             |            |             |               |             |              |          |  'logit' 'decisions']                                                     |
| main/f0/shadowsocks/G1/i1/trojan | D-P   | 128 | 1.79170481 | 0.12371521  | 0.99996723  | 0.217276178 | 1.79172299 | 1.24813422  |   1.61316416  | 0.724151117 |   4.69824357 | False    | ['objective' 'remaining' 'gradient' 'CE_mean' 'CE_row' 'TV_mean' 'TV_row' |
|                                  |       |     |            |             |             |             |            |             |               |             |              |          |  'logit' 'decisions']                                                     |
| main/f0/shadowsocks/G2/i1/trojan | D-P   | 128 | 1.79171367 | 0.126917412 | 0.999972488 | 0.226063071 | 1.79172812 | 1.15299127  |   2.20747957  | 0.761785432 |   4.39647427 | False    | ['objective' 'remaining' 'gradient' 'CE_mean' 'CE_row' 'TV_mean' 'TV_row' |
|                                  |       |     |            |             |             |             |            |             |               |             |              |          |  'logit' 'decisions']                                                     |
| main/f0/vless/G0/i1/shadowsocks  | D-P   | 128 | 1.78801142 | 0.243025387 | 0.997579927 | 0.232868265 | 1.78824504 | 0.60251542  |   1.72161599  | 0.737888248 |   4.24488748 | False    | ['objective' 'remaining' 'gradient' 'CE_mean' 'CE_row' 'TV_mean' 'TV_row' |
|                                  |       |     |            |             |             |             |            |             |               |             |              |          |  'logit' 'decisions']                                                     |
| main/f0/vless/G1/i1/shadowsocks  | D-P   | 128 | 1.78846104 | 0.234947452 | 0.997881294 | 0.216138653 | 1.79026068 | 0.901905073 |   1.17937213  | 0.670219086 |   2.3723015  | False    | ['objective' 'remaining' 'gradient' 'CE_mean' 'CE_row' 'TV_mean' 'TV_row' |
|                                  |       |     |            |             |             |             |            |             |               |             |              |          |  'logit' 'decisions']                                                     |
| main/f0/vless/G2/i1/shadowsocks  | D-P   | 128 | 1.79062833 | 0.177562288 | 0.999299254 | 0.223314128 | 1.79124197 | 1.49856623  |   0.943353759 | 0.627259392 |   4.18968584 | False    | ['objective' 'remaining' 'gradient' 'CE_mean' 'CE_row' 'TV_mean' 'TV_row' |
|                                  |       |     |            |             |             |             |            |             |               |             |              |          |  'logit' 'decisions']                                                     |
| main/f0/trojan/G0/i1/shadowsocks | D-P   | 128 | 1.78744698 | 0.242187332 | 0.997216981 | 0.207884606 | 1.78778696 | 0.785382313 |   1.80430525  | 0.711416795 |   4.5082179  | False    | ['objective' 'remaining' 'gradient' 'CE_mean' 'CE_row' 'TV_mean' 'TV_row' |
|                                  |       |     |            |             |             |             |            |             |               |             |              |          |  'logit' 'decisions']                                                     |
| main/f0/trojan/G1/i1/shadowsocks | D-P   | 128 | 1.78789299 | 0.228075677 | 0.997527327 | 0.197914489 | 1.79002921 | 1.27411935  |   1.44794911  | 0.650833382 |   2.60281039 | False    | ['objective' 'remaining' 'gradient' 'CE_mean' 'CE_row' 'TV_mean' 'TV_row' |
|                                  |       |     |            |             |             |             |            |             |               |             |              |          |  'logit' 'decisions']                                                     |
| main/f0/trojan/G2/i1/shadowsocks | D-P   | 128 | 1.78844923 | 0.230312873 | 0.997880016 | 0.219852084 | 1.79038108 | 1.47490412  |   1.23067209  | 0.612565189 |   3.27586228 | False    | ['objective' 'remaining' 'gradient' 'CE_mean' 'CE_row' 'TV_mean' 'TV_row' |
|                                  |       |     |            |             |             |             |            |             |               |             |              |          |  'logit']                                                                 |
| main/f0/vmess/G0/i1/shadowsocks  | D-P   | 128 | 1.78868022 | 0.195441078 | 0.99807103  | 0.217138161 | 1.78935145 | 0.975630867 |   1.70351687  | 0.7105922   |   4.08111791 | False    | ['objective' 'remaining' 'gradient' 'CE_mean' 'CE_row' 'TV_mean' 'TV_row' |
|                                  |       |     |            |             |             |             |            |             |               |             |              |          |  'logit']                                                                 |
| main/f0/vmess/G1/i1/shadowsocks  | D-P   | 128 | 1.79069715 | 0.113386817 | 0.999367054 | 0.217620518 | 1.79134817 | 1.15055229  |   0.941703353 | 0.667573505 |   3.01896339 | False    | ['objective' 'remaining' 'gradient' 'CE_mean' 'CE_row' 'TV_mean' 'TV_row' |
|                                  |       |     |            |             |             |             |            |             |               |             |              |          |  'logit' 'decisions']                                                     |
| main/f0/vmess/G2/i1/shadowsocks  | D-P   | 128 | 1.78995234 | 0.18048101  | 0.998878449 | 0.214559927 | 1.79101018 | 0.655953187 |   1.1381228   | 0.630242352 |   3.72983053 | False    | ['objective' 'remaining' 'gradient' 'CE_mean' 'CE_row' 'TV_mean' 'TV_row' |
|                                  |       |     |            |             |             |             |            |             |               |             |              |          |  'logit' 'decisions']                                                     |
| main/f0/shadowsocks/G0/i1/trojan | D-G   | 128 | 1.79154497 | 0.23779931  | 0.999861967 | 0.253104649 | 1.7915281  | 0.620741442 |   1.88402298  | 0.785372897 |   4.70229086 | False    | ['objective' 'remaining' 'gradient' 'CE_mean' 'CE_row' 'TV_mean' 'TV_row' |
|                                  |       |     |            |             |             |             |            |             |               |             |              |          |  'logit' 'decisions']                                                     |
| main/f0/shadowsocks/G1/i1/trojan | D-G   | 128 | 1.79170483 | 0.124683614 | 0.999967227 | 0.217100903 | 1.7917236  | 1.266939    |   1.62629328  | 0.727321285 |   4.51470948 | False    | ['objective' 'remaining' 'gradient' 'CE_mean' 'CE_row' 'TV_mean' 'TV_row' |
|                                  |       |     |            |             |             |             |            |             |               |             |              |          |  'logit' 'decisions']                                                     |
| main/f0/shadowsocks/G2/i1/trojan | D-G   | 128 | 1.79171368 | 0.12697109  | 0.999972496 | 0.227454536 | 1.79172903 | 1.41182511  |   2.45475202  | 0.748507873 |   4.43459859 | False    | ['objective' 'remaining' 'gradient' 'CE_mean' 'CE_row' 'TV_mean' 'TV_row' |
|                                  |       |     |            |             |             |             |            |             |               |             |              |          |  'logit' 'decisions']                                                     |
| main/f0/vless/G0/i1/shadowsocks  | D-G   | 128 | 1.78813369 | 0.246497902 | 0.997653613 | 0.232191897 | 1.78838964 | 0.341174378 |   1.52535475  | 0.742823991 |   4.40139241 | False    | ['objective' 'remaining' 'gradient' 'CE_mean' 'CE_row' 'TV_mean' 'TV_row' |
|                                  |       |     |            |             |             |             |            |             |               |             |              |          |  'logit' 'decisions']                                                     |
| main/f0/vless/G1/i1/shadowsocks  | D-G   | 128 | 1.78859899 | 0.237188078 | 0.997966979 | 0.215067026 | 1.79030974 | 0.788343789 |   1.22100938  | 0.693144632 |   2.5994407  | False    | ['objective' 'remaining' 'gradient' 'CE_mean' 'CE_row' 'TV_mean' 'TV_row' |
|                                  |       |     |            |             |             |             |            |             |               |             |              |          |  'logit' 'decisions']                                                     |
| main/f0/vless/G2/i1/shadowsocks  | D-G   | 128 | 1.79065974 | 0.175727918 | 0.999319486 | 0.223181054 | 1.79126774 | 1.49900085  |   1.02902922  | 0.619008101 |   4.11730404 | False    | ['objective' 'remaining' 'gradient' 'CE_mean' 'CE_row' 'TV_mean' 'TV_row' |
|                                  |       |     |            |             |             |             |            |             |               |             |              |          |  'logit' 'decisions']                                                     |
| main/f0/trojan/G0/i1/shadowsocks | D-G   | 128 | 1.78761988 | 0.245211676 | 0.997323338 | 0.205746495 | 1.78801933 | 0.601479276 |   1.60958794  | 0.716391096 |   4.32207908 | False    | ['objective' 'remaining' 'gradient' 'CE_mean' 'CE_row' 'TV_mean' 'TV_row' |
|                                  |       |     |            |             |             |             |            |             |               |             |              |          |  'logit' 'decisions']                                                     |
| main/f0/trojan/G1/i1/shadowsocks | D-G   | 128 | 1.78809076 | 0.230672148 | 0.997649903 | 0.196984412 | 1.79009497 | 1.15474592  |   1.40244521  | 0.677619788 |   2.78126296 | False    | ['objective' 'remaining' 'gradient' 'CE_mean' 'CE_row' 'TV_mean' 'TV_row' |
|                                  |       |     |            |             |             |             |            |             |               |             |              |          |  'logit' 'decisions']                                                     |
| main/f0/trojan/G2/i1/shadowsocks | D-G   | 128 | 1.78856925 | 0.230886645 | 0.997956133 | 0.218204857 | 1.79046112 | 1.62625846  |   1.33596339  | 0.613139712 |   3.26683032 | False    | ['objective' 'remaining' 'gradient' 'CE_mean' 'CE_row' 'TV_mean' 'TV_row' |
|                                  |       |     |            |             |             |             |            |             |               |             |              |          |  'logit']                                                                 |
| main/f0/vmess/G0/i1/shadowsocks  | D-G   | 128 | 1.78872109 | 0.194758533 | 0.998097449 | 0.217873154 | 1.78939384 | 1.05905654  |   1.82904852  | 0.702199839 |   4.05022129 | False    | ['objective' 'remaining' 'gradient' 'CE_mean' 'CE_row' 'TV_mean' 'TV_row' |
|                                  |       |     |            |             |             |             |            |             |               |             |              |          |  'logit']                                                                 |
| main/f0/vmess/G1/i1/shadowsocks  | D-G   | 128 | 1.79074438 | 0.114729373 | 0.999394712 | 0.216193847 | 1.79136428 | 0.888717954 |   0.987382438 | 0.667697493 |   3.15172947 | False    | ['objective' 'remaining' 'gradient' 'CE_mean' 'CE_row' 'TV_mean' 'TV_row' |
|                                  |       |     |            |             |             |             |            |             |               |             |              |          |  'logit' 'decisions']                                                     |
| main/f0/vmess/G2/i1/shadowsocks  | D-G   | 128 | 1.78999967 | 0.179681146 | 0.998908364 | 0.214490798 | 1.79104257 | 0.726884495 |   1.11484077  | 0.61778764  |   3.73354701 | False    | ['objective' 'remaining' 'gradient' 'CE_mean' 'CE_row' 'TV_mean' 'TV_row' |
|                                  |       |     |            |             |             |             |            |             |               |             |              |          |  'logit' 'decisions']                                                     |
| main/f0/shadowsocks/G0/i1/trojan | D-P   | 256 | 1.79133051 | 0.237805607 | 0.999723954 | 0.253087003 | 1.7912969  | 0.6237089   |   1.88674728  | 0.785701661 |   4.70270912 | False    | ['objective' 'remaining' 'gradient' 'CE_mean' 'CE_row' 'TV_mean' 'TV_row' |
|                                  |       |     |            |             |             |             |            |             |               |             |              |          |  'logit' 'decisions']                                                     |
| main/f0/shadowsocks/G1/i1/trojan | D-P   | 256 | 1.79165015 | 0.12371521  | 0.999934462 | 0.217272614 | 1.79168652 | 1.24813422  |   1.61315184  | 0.724145265 |   4.69822089 | False    | ['objective' 'remaining' 'gradient' 'CE_mean' 'CE_row' 'TV_mean' 'TV_row' |
|                                  |       |     |            |             |             |             |            |             |               |             |              |          |  'logit' 'decisions']                                                     |
| main/f0/shadowsocks/G2/i1/trojan | D-P   | 256 | 1.79166786 | 0.126917412 | 0.999944976 | 0.226059979 | 1.79169678 | 1.15299127  |   2.20746154  | 0.761779804 |   4.39645823 | False    | ['objective' 'remaining' 'gradient' 'CE_mean' 'CE_row' 'TV_mean' 'TV_row' |
|                                  |       |     |            |             |             |             |            |             |               |             |              |          |  'logit' 'decisions']                                                     |
| main/f0/vless/G0/i1/shadowsocks  | D-P   | 256 | 1.7842722  | 0.243025387 | 0.995165558 | 0.232593214 | 1.78474001 | 0.60251542  |   1.71876024  | 0.737225999 |   4.242866   | False    | ['objective' 'remaining' 'gradient' 'CE_mean' 'CE_row' 'TV_mean' 'TV_row' |
|                                  |       |     |            |             |             |             |            |             |               |             |              |          |  'logit' 'decisions']                                                     |
| main/f0/vless/G1/i1/shadowsocks  | D-P   | 256 | 1.78516958 | 0.234947452 | 0.995767061 | 0.215910094 | 1.78876541 | 0.901905073 |   1.17791098  | 0.669821691 |   2.37115804 | False    | ['objective' 'remaining' 'gradient' 'CE_mean' 'CE_row' 'TV_mean' 'TV_row' |
|                                  |       |     |            |             |             |             |            |             |               |             |              |          |  'logit' 'decisions']                                                     |
| main/f0/vless/G2/i1/shadowsocks  | D-P   | 256 | 1.78949798 | 0.177562288 | 0.998599    | 0.223235649 | 1.79072492 | 1.49856623  |   0.943146701 | 0.627122093 |   4.18929478 | False    | ['objective' 'remaining' 'gradient' 'CE_mean' 'CE_row' 'TV_mean' 'TV_row' |
|                                  |       |     |            |             |             |             |            |             |               |             |              |          |  'logit' 'decisions']                                                     |
| main/f0/trojan/G0/i1/shadowsocks | D-P   | 256 | 1.78314618 | 0.242187332 | 0.994441506 | 0.207602058 | 1.78382743 | 0.785382313 |   1.80081741  | 0.710553209 |   4.50563755 | False    | ['objective' 'remaining' 'gradient' 'CE_mean' 'CE_row' 'TV_mean' 'TV_row' |
|                                  |       |     |            |             |             |             |            |             |               |             |              |          |  'logit' 'decisions']                                                     |
| main/f0/trojan/G1/i1/shadowsocks | D-P   | 256 | 1.78403589 | 0.228075677 | 0.995060654 | 0.197673874 | 1.78830394 | 1.27411935  |   1.44658132  | 0.650327774 |   2.60133744 | False    | ['objective' 'remaining' 'gradient' 'CE_mean' 'CE_row' 'TV_mean' 'TV_row' |
|                                  |       |     |            |             |             |             |            |             |               |             |              |          |  'logit' 'decisions']                                                     |
| main/f0/trojan/G2/i1/shadowsocks | D-P   | 256 | 1.78514587 | 0.230312873 | 0.995764438 | 0.219623339 | 1.78900602 | 1.47490412  |   1.22995819  | 0.61221915  |   3.27473199 | False    | ['objective' 'remaining' 'gradient' 'CE_mean' 'CE_row' 'TV_mean' 'TV_row' |
|                                  |       |     |            |             |             |             |            |             |               |             |              |          |  'logit']                                                                 |
| main/f0/vmess/G0/i1/shadowsocks  | D-P   | 256 | 1.78560673 | 0.195441078 | 0.99614567  | 0.216934478 | 1.78694884 | 0.975630867 |   1.70145813  | 0.709996966 |   4.07950798 | False    | ['objective' 'remaining' 'gradient' 'CE_mean' 'CE_row' 'TV_mean' 'TV_row' |
|                                  |       |     |            |             |             |             |            |             |               |             |              |          |  'logit']                                                                 |
| main/f0/vmess/G1/i1/shadowsocks  | D-P   | 256 | 1.78963549 | 0.113386817 | 0.998734502 | 0.217552845 | 1.79093719 | 1.15055229  |   0.941427835 | 0.667447426 |   3.01861344 | False    | ['objective' 'remaining' 'gradient' 'CE_mean' 'CE_row' 'TV_mean' 'TV_row' |
|                                  |       |     |            |             |             |             |            |             |               |             |              |          |  'logit' 'decisions']                                                     |
| main/f0/vmess/G2/i1/shadowsocks  | D-P   | 256 | 1.78814715 | 0.18048101  | 0.997758102 | 0.214444573 | 1.79026183 | 0.655953187 |   1.13732321  | 0.630031159 |   3.72921551 | False    | ['objective' 'remaining' 'gradient' 'CE_mean' 'CE_row' 'TV_mean' 'TV_row' |
|                                  |       |     |            |             |             |             |            |             |               |             |              |          |  'logit' 'decisions']                                                     |
| main/f0/shadowsocks/G0/i1/trojan | D-G   | 256 | 1.7913305  | 0.23779931  | 0.999723953 | 0.253087004 | 1.79129677 | 0.620741442 |   1.88381979  | 0.78533342  |   4.70216464 | False    | ['objective' 'remaining' 'gradient' 'CE_mean' 'CE_row' 'TV_mean' 'TV_row' |
|                                  |       |     |            |             |             |             |            |             |               |             |              |          |  'logit' 'decisions']                                                     |
| main/f0/shadowsocks/G1/i1/trojan | D-G   | 256 | 1.7916502  | 0.124683614 | 0.999934455 | 0.217097342 | 1.79168773 | 1.266939    |   1.62628124  | 0.727315492 |   4.51468755 | False    | ['objective' 'remaining' 'gradient' 'CE_mean' 'CE_row' 'TV_mean' 'TV_row' |
|                                  |       |     |            |             |             |             |            |             |               |             |              |          |  'logit' 'decisions']                                                     |
| main/f0/shadowsocks/G2/i1/trojan | D-G   | 256 | 1.79166789 | 0.12697109  | 0.999944992 | 0.227451426 | 1.79169858 | 1.41182511  |   2.45473325  | 0.748501847 |   4.43458271 | False    | ['objective' 'remaining' 'gradient' 'CE_mean' 'CE_row' 'TV_mean' 'TV_row' |
|                                  |       |     |            |             |             |             |            |             |               |             |              |          |  'logit' 'decisions']                                                     |
| main/f0/vless/G0/i1/shadowsocks  | D-G   | 256 | 1.78451621 | 0.246497902 | 0.995312601 | 0.231925437 | 1.7850286  | 0.341174378 |   1.52258299  | 0.742242425 |   4.39940631 | False    | ['objective' 'remaining' 'gradient' 'CE_mean' 'CE_row' 'TV_mean' 'TV_row' |
|                                  |       |     |            |             |             |             |            |             |               |             |              |          |  'logit' 'decisions']                                                     |
| main/f0/vless/G1/i1/shadowsocks  | D-G   | 256 | 1.78544493 | 0.237188078 | 0.995938083 | 0.214848508 | 1.78886329 | 0.788343789 |   1.21992806  | 0.692833542 |   2.59846424 | False    | ['objective' 'remaining' 'gradient' 'CE_mean' 'CE_row' 'TV_mean' 'TV_row' |
|                                  |       |     |            |             |             |             |            |             |               |             |              |          |  'logit' 'decisions']                                                     |
| main/f0/vless/G2/i1/shadowsocks  | D-G   | 256 | 1.78956076 | 0.175727918 | 0.998639437 | 0.223104796 | 1.79077641 | 1.49900085  |   1.02876929  | 0.618868202 |   4.11691958 | False    | ['objective' 'remaining' 'gradient' 'CE_mean' 'CE_row' 'TV_mean' 'TV_row' |
|                                  |       |     |            |             |             |             |            |             |               |             |              |          |  'logit' 'decisions']                                                     |
| main/f0/trojan/G0/i1/shadowsocks | D-G   | 256 | 1.7834911  | 0.245211676 | 0.994653663 | 0.205477175 | 1.78429093 | 0.601479276 |   1.60628298  | 0.715544261 |   4.31966406 | False    | ['objective' 'remaining' 'gradient' 'CE_mean' 'CE_row' 'TV_mean' 'TV_row' |
|                                  |       |     |            |             |             |             |            |             |               |             |              |          |  'logit' 'decisions']                                                     |
| main/f0/trojan/G1/i1/shadowsocks | D-G   | 256 | 1.78443053 | 0.230672148 | 0.995305232 | 0.196756559 | 1.78843505 | 1.15474592  |   1.40111525  | 0.677246369 |   2.77994783 | False    | ['objective' 'remaining' 'gradient' 'CE_mean' 'CE_row' 'TV_mean' 'TV_row' |
|                                  |       |     |            |             |             |             |            |             |               |             |              |          |  'logit' 'decisions']                                                     |
| main/f0/trojan/G2/i1/shadowsocks | D-G   | 256 | 1.78538543 | 0.230886645 | 0.995916364 | 0.21798579  | 1.78916585 | 1.62625846  |   1.33513958  | 0.612799527 |   3.2657339  | False    | ['objective' 'remaining' 'gradient' 'CE_mean' 'CE_row' 'TV_mean' 'TV_row' |
|                                  |       |     |            |             |             |             |            |             |               |             |              |          |  'logit']                                                                 |
| main/f0/vmess/G0/i1/shadowsocks  | D-G   | 256 | 1.78568833 | 0.194758533 | 0.99619841  | 0.217671566 | 1.78703346 | 1.05905654  |   1.82701915  | 0.701612851 |   4.04863572 | False    | ['objective' 'remaining' 'gradient' 'CE_mean' 'CE_row' 'TV_mean' 'TV_row' |
|                                  |       |     |            |             |             |             |            |             |               |             |              |          |  'logit']                                                                 |
| main/f0/vmess/G1/i1/shadowsocks  | D-G   | 256 | 1.7897299  | 0.114729373 | 0.998789784 | 0.216129489 | 1.79096939 | 0.888717954 |   0.987095948 | 0.667584375 |   3.15138475 | False    | ['objective' 'remaining' 'gradient' 'CE_mean' 'CE_row' 'TV_mean' 'TV_row' |
|                                  |       |     |            |             |             |             |            |             |               |             |              |          |  'logit' 'decisions']                                                     |
| main/f0/vmess/G2/i1/shadowsocks  | D-G   | 256 | 1.78824171 | 0.179681146 | 0.99781787  | 0.214378474 | 1.79032657 | 0.726884495 |   1.11406262  | 0.61756494  |   3.73294422 | False    | ['objective' 'remaining' 'gradient' 'CE_mean' 'CE_row' 'TV_mean' 'TV_row' |
|                                  |       |     |            |             |             |             |            |             |               |             |              |          |  'logit' 'decisions']                                                     |
