# RA1 v1实施进度与工程先导验收

日期：2026-10-18。用户已授权按RA1计划实施。

## 已完成

- 新建独立实现：`eval/role_asymmetric_transfer_v1/`；旧实验源代码、合同、模型和分数不修改。
- P0完成：60个外层角色、各60个P/G映射、420个历史参考端点的来源绑定；60份训练-only包构建与原视图/映射数值重放通过。
- P1完成：2340个角色—政策权重组合通过，420个历史分类目标与原坐标梯度重放通过。
- 独立合成目标误差0、梯度误差约4.16e-17、有限差分误差约1.56e-11；两次结构重复拟合参数完全一致。
- P1附加拟合为1个合成LR及2个结构重复LR，共3个，均单独计费，不当作科学seed或独立样本。
- P2完成：f0全部12外层角色，每角色P/G/RawPre/RawPost的U50各一个，共48新LR全部验收通过，已包含于1920计划数。
- 源码AST核对确认本轮LBFGS与历史v4后端算法一致；CUDA float64，未改模型、损失、分类正则、数值门或数据权限。
- P0/P1/P2均未读取H query、H标签或实际目标U训练数值。

## 后续调度

P3剩余1872个新LR已经开始。执行器按固定顺序继续：完整拟合→全部2340端点封存→全部H-post预测→56160预测封存→统一标签评分→六项区间和诊断报告→独立复核。

不以训练CE或f0业务分数决定科学推进；工程先导不属于源内业务显著性筛查，也不冒充完整H结果。任何数值、来源或权限失败均保留终态，不静默删角色或回退。

## 预算与估时

P2结束时累计活动约206.6秒。按16个部署×来源单元的先导最大拟合耗时，估计其各117个剩余模型成本，并预留600秒非拟合成本，保守总活动估计5262.3秒，约87.7分钟。估计没有覆盖所有新权重的真实求解难度，不能当作完成承诺；正式活动上限仍为28800秒（8小时）。

每个模型只有582个参数，动态线搜索和原坐标验收需要CPU/GPU同步；显存不满或瞬时GPU占用较低不表示转为CPU训练。本轮没有未经核验换成32模型共享批量退出、CUDA Graph、AMP或低精度路径。

## 可核对文件

- 合同：`outputs/role-asymmetric-transfer-v1-20261017/run-01/manifests/contract.json`
- 来源：同根`manifests/source-bindings.parquet`、`role-membership.parquet`
- P1：`audits/P1-complete.json`、`manifests/verified-aliases.parquet`
- P2：`pilot/promotion.json`、`manifests/P2-endpoints.parquet`
- 状态与成本：`progress.json`、`cost-ledger.json`、`fit-logs/`
- 运行入口：`eval/role_asymmetric_transfer_v1/run.py`

本文件是工程进度记录，不含新业务成绩。是否完成以最终`completion.json`和`verification.json`为准，不以进程是否退出或某批模型数量判断。
