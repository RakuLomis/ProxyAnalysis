# Extend v3 正式执行登记

## 授权与范围

本轮用户已确认启动准备报告中冻结的正式预算。准备阶段的 `formal_training_authorized:false` 是历史快照，未改写；新增 `formal-01/execution-contract.json` 记录正式授权并封存生产代码。

沿用 common-window v3 的共同窗口与全部资格约束。W 主轨包含 SS、VLESS、Trojan、VMess、AnyTLS；T 次轨包含前四种部署。Hy2 保持测量-only。六业务、30 内容、重复 1–4；不增加采集、不重新选择业务或阈值。

## 执行顺序

1. CUDA 生成器工程检查：旧拟合数值复现、组级行置换不变、Cartesian 目标等价、权限拒绝。
2. 1080 场景正式生成（600 W + 480 T）。只读取 C 双侧和 U pre；五种生成臂、三个种子、每 U 访问八视图，共 9,331,200 视图。失败即停止，不重抽样、不回退。
3. 全量可行域审计。合法性仅是必要摘要约束，不是协议真实性或业务有效性。
4. CUDA 独立分类头工程检查。
5. 19,440 个受限分类器拟合；H post 推理并封存预测。
6. 封存后开放 U post，运行 3,240 个 reference 分类器及独立推理。
7. 开放 H 标签评分。完整六类混淆矩阵、逐种子/业务组/轮换、错误修复与新增、10,000 次内容簇 bootstrap。

## 未改变的学习口径

W 保留旧 window-model 六坐标、联合方向约束及 24/96 行残差抽样；T 保留旧 feasible-summary 六生成坐标、固定 pre F 及按场景/访问/视图种子的内容-donor 抽样。二者不强行使用同一生成公式。组级 post 包没有访问身份或 post F。

分类器为 6/7 → 32 ReLU → 6；CUDA float32、Adam 0.001、1000 步、每批 24、权重正则 0.0001。缩放仅由 C pre 的 log1p 拟合。各臂同初始参数、同训练访问曝光/视图日程；18 个分类头只是并行计算，参数和梯度相互独立。每训练访问曝光 250 次。

主比较仅 paired−raw 与 paired−group。W 10 项、T 8 项分别进行家族校正；每部署两个调整后下界均大于零才通过。区间条件于冻结模型与校准集合，不代表外部验证。

## 工程记录与当前状态

生成器首次旧模型回放使用逐位相等检查时出现约 3.33e−16 的浮点差异。首次合同保留为 `engineering-attempt-01-contract.json`；正式生成前将数值回放检查改为 atol/rtol 1e−12，未改变拟合目标、数据、随机抽样或科学门限。组级置换仍要求逐位一致。

W/T 生成器工程检查已通过。18 头批量训练对逐个训练的最大 logit 差分别为 3.5763e−7 / 2.3842e−7；模型轴隔离检查通过。此时尚未读取测试标签，未产生新的业务效果结论。

全量完成情况以 `formal-01/pipeline-progress.json`、`generation-progress.json`、各阶段 seal/gate 为准，不能把启动或部分完成写成全部完成。有限批次入口为 `eval/extend_calibration/run_formal_pipeline.py`；可恢复已完成的哈希验证产物，不覆写历史实验。任一子进程失败后停止后续阶段并保存日志。

最终统计表由评分脚本生成到本目录 `formal-v3-results.md`。各模型、训练历史、残差池、生成视图、权限读记录和逐访问概率保存在 `outputs/extend-calibration-20260930/run-01/extraction-03/formal-01`。
