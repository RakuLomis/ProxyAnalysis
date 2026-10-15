# 动态软约束漂移外层优化先导结果

本轮状态为pilot_complete。12/36条轨迹获得预登记数值资格；未获资格轨迹保留在分母中，不自动进入业务。本轮没有拟合最终业务分类器，没有读取H或实际目标U，也没有新增F1、CE业务评价或bootstrap。

## 实验范围

固定外层f0的四部署、三个遮蔽组，共12角色和36轨迹；每条轨迹使用12个等权合法源内任务。P/T共享P映射与尺度，G只用自己的匿名组资产。允许实际目标C原训练系数，不把本轮称为完全无目标部署信息的泛化实验。

原目标、0.1 small比例、96维输入、LR的原W正则与bias无正则均保持。新增外层程序使用M=1+A/s固定度量、尺度位移0.1限幅、[0,2]投影、最多8次双档Armijo回溯。所有目标和质量仍在原q坐标计算。候选使用充分LR、fine精炼和真实一次Newton校验，接受后才计算并验收f/v隐式梯度。

## 逐角色结果

| 部署 | 组 | 臂 | 状态 | 接受更新 | 总目标起点 | 总目标终点 | 原投影残差终点 |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: |
| shadowsocks | G0 | O-DP | finite_progress | 20 | 0.7077 | 0.692309 | 0.0485951 |
| shadowsocks | G0 | O-TP | finite_progress | 20 | 0.7077 | 0.692308 | 0.0484375 |
| shadowsocks | G0 | O-DG | finite_progress | 20 | 0.707652 | 0.692251 | 0.0510418 |
| shadowsocks | G1 | O-DP | stop_budget | 6 | 1.18579 | 1.17994 | 0.948446 |
| shadowsocks | G1 | O-TP | stop_budget | 6 | 1.18579 | 1.17994 | 0.948447 |
| shadowsocks | G1 | O-DG | stop_budget | 6 | 1.17167 | 1.16311 | 0.472549 |
| shadowsocks | G2 | O-DP | stop_budget | 17 | 1.80383 | 1.63703 | 0.779301 |
| shadowsocks | G2 | O-TP | stop_budget | 17 | 1.80383 | 1.63697 | 0.778747 |
| shadowsocks | G2 | O-DG | stop_budget | 10 | 1.83062 | 1.6266 | 0.999637 |
| vless | G0 | O-DP | qualified_descent_only | 20 | 0.686523 | 0.675704 | 0.594513 |
| vless | G0 | O-TP | qualified_descent_only | 20 | 0.686523 | 0.67468 | 0.67854 |
| vless | G0 | O-DG | qualified_descent_only | 20 | 0.676801 | 0.664639 | 0.214187 |
| vless | G1 | O-DP | qualified_descent_only | 20 | 1.32743 | 1.28782 | 0.085955 |
| vless | G1 | O-TP | finite_progress | 20 | 1.32743 | 1.28108 | 0.074578 |
| vless | G1 | O-DG | finite_progress | 20 | 1.32446 | 1.27031 | 0.0101265 |
| vless | G2 | O-DP | qualified_descent_only | 20 | 1.65168 | 1.61038 | 0.395513 |
| vless | G2 | O-TP | qualified_descent_only | 20 | 1.65168 | 1.59588 | 0.601537 |
| vless | G2 | O-DG | finite_progress | 20 | 1.59157 | 1.58281 | 0.0634828 |
| trojan | G0 | O-DP | qualified_descent_only | 20 | 0.690813 | 0.673322 | 0.167296 |
| trojan | G0 | O-TP | qualified_descent_only | 20 | 0.690813 | 0.672309 | 0.195784 |
| trojan | G0 | O-DG | finite_progress | 20 | 0.671176 | 0.655763 | 0.0171607 |
| trojan | G1 | O-DP | finite_progress | 20 | 1.64026 | 1.59768 | 0.0636936 |
| trojan | G1 | O-TP | finite_progress | 20 | 1.64026 | 1.5893 | 0.0664358 |
| trojan | G1 | O-DG | qualified_descent_only | 20 | 1.54534 | 1.51122 | 0.308638 |
| trojan | G2 | O-DP | qualified_descent_only | 20 | 1.47293 | 1.46822 | 0.115875 |
| trojan | G2 | O-TP | qualified_descent_only | 20 | 1.47293 | 1.46798 | 0.121189 |
| trojan | G2 | O-DG | qualified_descent_only | 20 | 1.48815 | 1.48448 | 0.0929291 |
| vmess | G0 | O-DP | qualified_descent_only | 20 | 0.64931 | 0.64646 | 0.267422 |
| vmess | G0 | O-TP | qualified_descent_only | 20 | 0.64931 | 0.64645 | 0.26762 |
| vmess | G0 | O-DG | qualified_descent_only | 20 | 0.673912 | 0.671959 | 0.155759 |
| vmess | G1 | O-DP | finite_progress | 20 | 1.18803 | 1.17434 | 0.101226 |
| vmess | G1 | O-TP | finite_progress | 20 | 1.18803 | 1.17388 | 0.11191 |
| vmess | G1 | O-DG | finite_progress | 20 | 1.17124 | 1.15171 | 0.0884001 |
| vmess | G2 | O-DP | qualified_descent_only | 20 | 0.846538 | 0.830991 | 0.376367 |
| vmess | G2 | O-TP | qualified_descent_only | 20 | 0.846538 | 0.829262 | 0.68591 |
| vmess | G2 | O-DG | qualified_descent_only | 20 | 0.828991 | 0.808817 | 0.384386 |

stationary只表示本政策下近似一阶驻点。finite_progress只允许在20个接受更新的正常终态评定，需总目标改善和原投影残差下降80%。预算、线搜索、信号或小步长停止不重命名为成功；单调下降不等于充分优化。

## 计算与权限

实际新源内LR 9877次，逻辑任务前向10512次，初始化缓存复用720次，其他精确缓存命中211次，隐式评估15600次，接受更新662次。累计活动计算2.3037小时，上限4小时。业务LR、H查询、H评分与bootstrap计数均为零。

## 解释边界和停止决定

源内目标变化只能说明既定数值程序的优化质量，不证明真实目标post收益，也不替代未见内容、跨配置或外部批次验证。旧q20、P-small及run-02业务结果不覆盖、不回选。旧源内轨迹仅作为描述参照，不用于本轮初值或更新选择。

完整状态表、接受及拒绝候选、块梯度与惩罚分项、原投影残差、旧源内参照、计数与独立核验保存在新运行目录。无论是否获资格，本轮到先导报告停止；新的180模型业务矩阵必须另行确认。

## 中断恢复与审计边界

本结果由run-02的17条完成轨迹与run-03受控续跑构成。旧停止结果不改变，恢复前已接受更新逐项重放，旧缓存逐字节复制并核验。累计成本继承旧计数与活动时间，并增加60秒保守尾部预留，没有重置4小时预算。

旧中断阶段没有完整读取台账，因此产物完整性核验和后续持久读取审计不等于恢复了旧进程丢失的读取日志。没有据此声称全过程读取审计已经完整。
