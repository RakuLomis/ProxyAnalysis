# 动态软约束漂移解级反馈先导完整报告

2026年10月12日。本轮状态为`stop_implicit_gradient_not_verified`，执行完整性通过为True，数值资格为False。没有正式q学习，没有新业务F1结果，也没有读取实际目标C/U/H或PCAP。

## 实验问题和冻结范围

本轮以原LR充分求解后的源内留出CE作为反馈，替代质量不合格的有限展开反馈。旧Q64/Q128/Q256没有迁入本轮资格。基础漂移映射、P-small槽位、96维、十块、标签、质量、标准化和t保持不变。

原目标为加权六类CE加0.0005(1+t)乘原W平方；bias不正则。训练槽位480行，反馈为原源内留出的8次访问。调整pre占总CE质量1/30。所有内容重复、两侧及内部flow整体划分，实际目标业务队列不参与拟合或反馈。

| role_id                          | target_exclusion   | mask   | source_calibration   |   t |
|:---------------------------------|:-------------------|:-------|:---------------------|----:|
| main/f0/shadowsocks/G0/i1/trojan | shadowsocks        | G0     | trojan               |   4 |
| main/f0/shadowsocks/G2/i1/trojan | shadowsocks        | G2     | trojan               |   0 |
| main/f0/vless/G1/i1/shadowsocks  | vless              | G1     | shadowsocks          |   4 |
| main/f0/trojan/G0/i1/shadowsocks | trojan             | G0     | shadowsocks          |   4 |
| main/f0/trojan/G2/i1/shadowsocks | trojan             | G2     | shadowsocks          |   4 |
| main/f0/vmess/G1/i1/shadowsocks  | vmess              | G1     | shadowsocks          |   1 |

## CUDA环境和前向政策

Python为D:\Tools\Anaconda\envs\Pytorch312\python.exe，PyTorch 2.5.1，CUDA 12.4，GPU为NVIDIA GeForce RTX 4060 Ti。模型、Hessian、求解和求导均使用CUDA float64，未启用CPU数值回退。

旧q=1参照按SHA复用为起点。新q点使用原v4 LBFGS，max_iter=2000、max_eval=10000、原梯度门1e-5。之后同目标Newton精炼，原梯度门为1e-8和1e-9，每点两档合计最多30次更新。Armijo常数1e-4，缩小因子0.5，每次最多25次回溯；没有jitter、bias正则或额外科学候选。

## 失败计数纠正

旧_pass列实际存放失败计数。新表以passed_count和failed_count独立导出并核对，不更改原运行及0/24停止结论。

|   K | gate      | original_column   |   tested_count |   passed_count |   failed_count | old_value_is_failure_count   |
|----:|:----------|:------------------|---------------:|---------------:|---------------:|:-----------------------------|
|  64 | objective | objective_pass    |             24 |              0 |             24 | True                         |
|  64 | remaining | remaining_pass    |             24 |              0 |             24 | True                         |
|  64 | gradient  | gradient_pass     |             24 |              0 |             24 | True                         |
|  64 | CE_mean   | CE_mean_pass      |             24 |              0 |             24 | True                         |
|  64 | CE_row    | CE_row_pass       |             24 |              0 |             24 | True                         |
|  64 | TV_mean   | TV_mean_pass      |             24 |              0 |             24 | True                         |
|  64 | TV_row    | TV_row_pass       |             24 |              0 |             24 | True                         |
|  64 | logit     | logit_pass        |             24 |              0 |             24 | True                         |
|  64 | decisions | decisions_pass    |             24 |              4 |             20 | True                         |
| 128 | objective | objective_pass    |             24 |              0 |             24 | True                         |
| 128 | remaining | remaining_pass    |             24 |              0 |             24 | True                         |
| 128 | gradient  | gradient_pass     |             24 |              0 |             24 | True                         |
| 128 | CE_mean   | CE_mean_pass      |             24 |              0 |             24 | True                         |
| 128 | CE_row    | CE_row_pass       |             24 |              0 |             24 | True                         |
| 128 | TV_mean   | TV_mean_pass      |             24 |              0 |             24 | True                         |
| 128 | TV_row    | TV_row_pass       |             24 |              0 |             24 | True                         |
| 128 | logit     | logit_pass        |             24 |              0 |             24 | True                         |
| 128 | decisions | decisions_pass    |             24 |              4 |             20 | True                         |
| 256 | objective | objective_pass    |             24 |              0 |             24 | True                         |
| 256 | remaining | remaining_pass    |             24 |              0 |             24 | True                         |
| 256 | gradient  | gradient_pass     |             24 |              0 |             24 | True                         |
| 256 | CE_mean   | CE_mean_pass      |             24 |              0 |             24 | True                         |
| 256 | CE_row    | CE_row_pass       |             24 |              0 |             24 | True                         |
| 256 | TV_mean   | TV_mean_pass      |             24 |              0 |             24 | True                         |
| 256 | TV_row    | TV_row_pass       |             24 |              0 |             24 | True                         |
| 256 | logit     | logit_pass        |             24 |              0 |             24 | True                         |
| 256 | decisions | decisions_pass    |             24 |              4 |             20 | True                         |

## 数值坐标与Hessian几何

完成24个训练问题的界重放，以及72个参数位置的实际Hessian几何。实际Hessian使用485维对比坐标，消去共同bias，并解析最小化受L2约束的共同W分量。原／变换坐标分列，不含已知共同bias零方向。

全范围界与q=1局部设计界的比值为21280.301至2106335.1；与q_alt局部设计界的比值为749.4455至7897.6823。这些比较对象均为设计矩阵界，不是实际Hessian特征值。

| ('arm', '')   | ('point', '')   |   ('raw_contrast_condition', 'min') |   ('raw_contrast_condition', 'max') |   ('whitened_contrast_condition', 'min') |   ('whitened_contrast_condition', 'max') |
|:--------------|:----------------|------------------------------------:|------------------------------------:|-----------------------------------------:|-----------------------------------------:|
| D-G           | K256            |                          1579.0734  |                           4522.1252 |                                1.0001651 |                                1.0149424 |
| D-G           | old_LR          |                           638.85089 |                           3106.2154 |                              127.78681   |                              800.9389    |
| D-G           | zero            |                          1579.0481  |                           4521.6773 |                                1         |                                1         |
| D-P           | K256            |                          1598.7508  |                           4576.469  |                                1.000165  |                                1.0155345 |
| D-P           | old_LR          |                           638.99847 |                           3105.0288 |                              130.54275   |                              674.37692   |
| D-P           | zero            |                          1598.7237  |                           4576.0138 |                                1         |                                1         |


## 解级求导与独立验证

隐式导数通过解Hv=g后计算−M转置v，不显式求逆、不穿过LBFGS更新。解析H和混合偏导与自动微分独立核对；线性残差门1e-10，另用CUDA通用线性求解作同矩阵复核。对比参数化保持原目标，485是数值未知量数，不是修改了业务分类器维数。

| role_id                          | arm   | point   |   level |   hessian_error |      symmetry |   linear_residual |   linear_absolute |   independent_solve_error |   mixed_VJP_error |    eigen_min |   eigen_max |   condition | precision_risk   |    v_norm |   stationarity_response_norm |   risk_response_proxy |   original_gradient |          Q | passed   | precision_stability_passed   |   precision_stability_error |
|:---------------------------------|:------|:--------|--------:|----------------:|--------------:|------------------:|------------------:|--------------------------:|------------------:|-------------:|------------:|------------:|:-----------------|----------:|-----------------------------:|----------------------:|--------------------:|-----------:|:---------|:-----------------------------|----------------------------:|
| main/f0/shadowsocks/G0/i1/trojan | D-P   | one     |       0 |   1.3766516e-15 | 2.9594476e-17 |     5.902704e-16  |     6.7600251e-15 |             5.2180482e-15 |     6.4254158e-14 | 0.0085880386 |   1.2760956 |   148.58987 | False            | 35.821158 |                4.433689e-07  |         2.9389408e-09 |       3.3615576e-09 | 0.62376227 | True     |                              |             nan             |
| main/f0/shadowsocks/G0/i1/trojan | D-P   | one     |       1 |   1.211178e-15  | 2.9981465e-17 |     6.0721648e-16 |     6.9540988e-15 |             2.220446e-15  |     5.0903726e-14 | 0.0085880356 |   1.2760956 |   148.58992 | False            | 35.82116  |                6.1155403e-13 |         1.6006772e-15 |       5.8301888e-15 | 0.62376227 | True     | True                         |               5.6706274e-08 |

## 两档中心端点

| role_id                          | arm   | point   |   Q_coarse |     Q_fine |   grad_coarse |     grad_fine |
|:---------------------------------|:------|:--------|-----------:|-----------:|--------------:|--------------:|
| main/f0/shadowsocks/G0/i1/trojan | D-P   | one     | 0.62376227 | 0.62376227 | 3.3615576e-09 | 5.8301888e-15 |

## 充分重训差分和信号

固定两方向为全同向和交替方向，均单位归一化；固定h=1e-4、3e-5。信号与两档前向风险差及1e-12底限比较，不以微小正负号判定。误差门为1e-5加1e-3乘差分绝对值；跨惩罚分支时用任务项差分与原独立oracle组合，保存完整差分截断项。

| role_id                          | arm   | point   | direction   |      h |        D_h |   D_h_coarse |   implicit |         error |         limit |   FD_precision_error |        signal |   signal_floor | signal_identifiable   | numerical_passed   |   level_difference | weak_direction   | passed   |     Q_plus |    Q_minus |
|:---------------------------------|:------|:--------|:------------|-------:|-----------:|-------------:|-----------:|--------------:|--------------:|---------------------:|--------------:|---------------:|:----------------------|:-------------------|-------------------:|:-----------------|:---------|-----------:|-----------:|
| main/f0/shadowsocks/G0/i1/trojan | D-P   | one     | all         | 0.0001 | 0.10460755 |   0.10460714 | 0.10460755 | 4.9944495e-09 | 0.00011460755 |        2.9503136e-05 | 2.0921509e-05 |  5.9006271e-08 | True                  | False              |      4.0860426e-07 | False            | False    | 0.62377273 | 0.62375181 |

## 阶段状态与停止证据

| point   | executed   | arm   |   checks | passed   | reason                                   | role_id                          | status                              |
|:--------|:-----------|:------|---------:|:---------|:-----------------------------------------|:---------------------------------|:------------------------------------|
| one     | True       | D-P   |        1 | False    | fixed fully-retrained finite differences | main/f0/shadowsocks/G0/i1/trojan | stop_implicit_gradient_not_verified |
| alt     | False      | nan   |      nan | False    | nan                                      | nan                              | conditional_not_executed            |

| path                                                                                                                                  | role_id                          | arm   | key              | exception   | Newton_updates   | seconds   |
|:--------------------------------------------------------------------------------------------------------------------------------------|:---------------------------------|:------|:-----------------|:------------|:-----------------|:----------|
| outputs/dynamic-soft-drift-implicit-pilot-20261012/run-01/endpoints/main/f0/shadowsocks/G0/i1/trojan/D-P/one-all-h0-minus-level0.json | main/f0/shadowsocks/G0/i1/trojan | D-P   | one-all-h0-minus |             |                  |           |
| outputs/dynamic-soft-drift-implicit-pilot-20261012/run-01/endpoints/main/f0/shadowsocks/G0/i1/trojan/D-P/one-all-h0-minus-level1.json | main/f0/shadowsocks/G0/i1/trojan | D-P   | one-all-h0-minus |             |                  |           |
| outputs/dynamic-soft-drift-implicit-pilot-20261012/run-01/endpoints/main/f0/shadowsocks/G0/i1/trojan/D-P/one-all-h0-plus-level0.json  | main/f0/shadowsocks/G0/i1/trojan | D-P   | one-all-h0-plus  |             |                  |           |
| outputs/dynamic-soft-drift-implicit-pilot-20261012/run-01/endpoints/main/f0/shadowsocks/G0/i1/trojan/D-P/one-all-h0-plus-level1.json  | main/f0/shadowsocks/G0/i1/trojan | D-P   | one-all-h0-plus  |             |                  |           |
| outputs/dynamic-soft-drift-implicit-pilot-20261012/run-01/endpoints/main/f0/shadowsocks/G0/i1/trojan/D-P/one-center-level0.json       | main/f0/shadowsocks/G0/i1/trojan | D-P   | one-center       |             |                  |           |
| outputs/dynamic-soft-drift-implicit-pilot-20261012/run-01/endpoints/main/f0/shadowsocks/G0/i1/trojan/D-P/one-center-level1.json       | main/f0/shadowsocks/G0/i1/trojan | D-P   | one-center       |             |                  |           |

逐步精炼日志见refinement-traces.parquet，原始端点JSON保留目标、梯度、步长、下降内积及回溯次数。阶段失败JSON保留异常和读取账本。未执行阶段不能计为失败的分类实验。

## 计算与权限账本

|   Newton_updates |   formal_classifier_fits |   new_mapping_fits |   new_q_LR_accepted |   new_q_LR_attempted |   old_reference_refinements |   precision_endpoints |   q_points_attempted |   q_points_refined |
|-----------------:|-------------------------:|-------------------:|--------------------:|---------------------:|----------------------------:|----------------------:|---------------------:|-------------------:|
|                6 |                        0 |                  0 |                   2 |                    2 |                           1 |                     6 |                    3 |                  3 |

完整预登记上限为216个不同q点，其中12个复用端点精炼、204个新LR问题。当前表为实际执行量，不将两档快照称为独立访问。失败点的精炼更新亦计入账本，已产生的端点和失败日志不覆盖。

父产物SHA复核通过；P/G资产按臂权限加载；G未读取P身份或映射。实际目标C/U/H数值读取0，PCAP读取0，漂移映射新拟合0，正式分类器0。旧P-small的正向结果及精确身份归因边界保持原样。

## 结论和下一步边界

本轮只检验反馈取得方式的数值资格，不能据此声称动态系数已提高分类。当前状态为`stop_implicit_gradient_not_verified`，不自动进入D-P、T-P、D-G正式矩阵。若存在精度、差分或信号失败，应先根据封存日志决定是否授权独立修订；不扩K、不改损失、不按真实目标F1选择方向或后端。

## 可复核文件

- [批准的实施方案](F:/Program/VSCode/MyGit/ProxyAnalysis/plan/dynamic-soft-drift-implicit-solution-pilot-plan-20261012.md)
- [封存实验合同](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/dynamic-soft-drift-implicit-pilot-20261012/run-01/manifests/contract.json)
- [完成状态](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/dynamic-soft-drift-implicit-pilot-20261012/run-01/completion.json)
- [完整性验证](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/dynamic-soft-drift-implicit-pilot-20261012/run-01/verification.json)
- [实际计算账本](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/dynamic-soft-drift-implicit-pilot-20261012/run-01/ledger.json)
- [代码与重放说明](F:/Program/VSCode/MyGit/ProxyAnalysis/eval/dynamic_soft_drift_implicit_pilot/README.md)
