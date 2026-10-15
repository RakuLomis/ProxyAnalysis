# P3封存接口修复与精确回退结项报告

日期：2026年10月14日。结项范围：post输入关联表征残差分支实验的P3封存接口与精确回退核验。

## 1 结项结论

P3封存接口修复及独立验收已经完成。720个逻辑端点全部封存，60份P-small基座与原登记模型的权重、偏置和尺度精确一致。CUDA上的54,000次合成输入端点重放通过，logit、log概率、同计算口径的概率及类别差异均为0。

180项源内策略决定保持全部回退，没有改判任何不合格候选。本次新增教师、残差分支和LR拟合均为0，没有修改模型、损失、数据权限或资格门，没有读取实际H/U数据，也没有执行新的业务评分。

原run-02仍保留`stop_stage_gate`及P3路径错误。独立run-03的成功状态为`closed_all_exact_fallback`，表示本次工程结项完成，**不表示新的H业务评价完成或新增分类收益成立**。

## 2 历史停止与修复方式

### 2.1 原停止记录保留

原P3在最终模型路径收集处使用了：

```python
ROOT[e['base_path']]
```

`ROOT`为WindowsPath，下标操作导致`'WindowsPath' object is not subscriptable`。原程序已经写出720条端点，但尚未生成最终模型封存，随后按门控停止。

本次没有修改原代码、封存、日志、`completion.json`或`progress.json`。历史v3中的错误写法也保留为原运行证据；不能通过重新启动旧总调度器完成此次结项。

### 2.2 独立只封存入口

修复落地在`eval/post_associated_p3_closeout/`，其路径收集接口改为：

```python
paths = {root / e['base_path'] for e in endpoints}
paths |= {root / e['residual_path'] for e in endpoints if e['residual_path']}
```

接口同时核验路径去重、可选残差路径和工作区路径边界。它不导入或调用原`final_train`、教师、分支训练器或LR求解器。出现任一启用决定、身份冲突或哈希不一致都会停止，不能自动补训或改为安全回退。

新目录为`outputs/post-input-associated-representation-20261014/run-03/`，只引用run-01的冻结基座和run-02的合同、来源及策略决定。没有复制重训或覆盖旧产物。

## 3 封存与身份核验

| 项目 | 核验结果 |
| --- | --- |
| 外层角色 | 60个，身份唯一 |
| 新增方法策略 | 180项，0启用、180回退 |
| 角色方法seed组合 | 720条，完整覆盖60×4臂×3seed，无缺失或重复 |
| 原P-small参考端点 | 180条A0端点 |
| 新臂精确回退端点 | 540条A1/A2/A3端点 |
| 实际唯一基座模型 | 60份，每角色12个端点共享其原P-small |
| 残差状态 | 全部为None |
| 选定λ | 全部为None，没有重新选模 |
| 新旧端点列表 | 逐项一致 |
| 最终模型封存 | 通过，绑定186项来源文件 |

封存绑定包含60份基座、其60份来源侧记录、60份已登记原模型及端点、修复合同、修复代码和原源内决策等文件。参数核验同时对照基座副本与原登记P-small，覆盖`weight`、`bias`、`mu`和`scale`四项；不是仅凭模型文件名或端点标签宣布回退。

## 4 CUDA精确回退核验

### 4.1 核验输入与接口

使用Pytorch312、PyTorch 2.5.1和NVIDIA GeForce RTX 4060 Ti，全部数值重放在CUDA float64上执行，关闭TF32，没有CPU推理回退。

核验复用原封存的纯post部署函数`predict_post`，部署代码没有修改。输入为固定seed 20261014生成的75行合成96维直方图：64行随机归一化块、1行均匀块和10行边界块。它们仅用于接口与函数一致性测试，不是采集访问、不具备业务标签，也不证明对应真实TCP会话。

同一组输入用于60个角色的720个逻辑端点，共54,000次端点输入重放，涉及4500个角色输入组合。seed和方法之间重复核验同一函数不增加独立业务样本量。

参考计算直接使用原登记P-small的尺度、权重及偏置；实际端点使用封存基座及`residual_state=None`。没有入口教师、pre表征或融合分支参与回退计算。

### 4.2 数值结果

| 核验项 | 结果 |
| --- | ---: |
| 原模型与基座参数严格相等 | 60/60 |
| 最大logit差 | 0 |
| 最大log概率差 | 0 |
| 同计算口径最大概率差 | 0 |
| 类别改变次数 | 0 |
| CUDA float64及96维接口要求 | 通过 |
| CPU输入负例 | 正确拒绝 |
| float32输入负例 | 正确拒绝 |
| 95维输入负例 | 正确拒绝 |

`softmax(logits)`与`exp(log_softmax(logits))`是不同的浮点计算路径，本次合成输入上两者最大舍入差为1.110223×10⁻¹⁶。分别沿用同一种算法比较原模型与回退端点时，差异均严格为0。没有通过放宽容差掩盖差异，也没有为制造零差改写部署函数。

模型参数和尺度相同、残差为空，建立的是原post函数与回退函数的恒等关系。合成重放验证了端点连接及计算接口，不能替代真实H上的分类或泛化测量。

## 5 历史完整性与独立验收

修复前后对run-01、run-02、原实验代码及冻结计划进行完整字节SHA256核对，共65,465份文件：

| 项目 | 数量 |
| --- | ---: |
| 新增历史文件 | 0 |
| 删除历史文件 | 0 |
| 内容发生变化的历史文件 | 0 |

原停止记录、训练台账、科学合同、资格决定及原代码全部保持不变。历史核对仅针对已生成实验产物及代码，没有重新扫描PCAP或打开外部H/U数据包。

另用`eval/post_associated_p3_audit/verify.py`进行独立验收。该验收器不导入torch或训练模块，核对结项和模型封存、修复代码封存、全部720条端点、180项原策略、CUDA重放结果及零新增训练记录。共复核200项清单文件绑定，并额外核对8个关键历史文件，全部通过。

## 6 权限与计算成本

| 项目 | 本次新增 |
| --- | ---: |
| 教师拟合 | 0 |
| 残差分支拟合 | 0 |
| LR拟合 | 0 |
| 训练墙钟 | 0秒 |
| 实际H-post读取 | 0 |
| 实际H-pre读取 | 0 |
| 实际H标签读取 | 0 |
| 实际目标U读取 | 0 |
| 新业务评分及bootstrap | 0 |

工程结项主程序耗时约840.312秒，即14分钟，主要用于两轮完整历史文件哈希核对，不是训练或选模成本。独立验收另耗时约1秒。

历史训练台账仍为720份教师、10,800次正式源内残差拟合、0个新基座LR，累计训练墙钟18,006.894秒，约5.002小时。原工程拟合计数也原样保留，没有因结项重启而清零或增加。

## 7 科学结论与停止边界

本次修复没有改变源内结果：五个非等价配置的300项角色候选全部未通过CE至少下降0.002 nats的启用门，最终180项新策略全部回退。参数化、λ候选、修正系数、L2、训练步数和数据权限均未改动。

因此，当前固定Stage A候选以“没有源内合格新增分支、全部精确回退P-small”结项。四臂最终是各角色同一post函数的别名，不是统计上未拒绝差异，也不是通过重训得到了近似相同的模型。

历史P-small的F1_U为0.796931，本次没有重新计算它。结项没有生成新的A3−A0、A3−A1、A3−A2区间、H上的CE/Brier或逐业务增量。若未来对相同H输入重放这些别名，其方法间差异由函数恒等关系决定；这不能被包装为关联表征分支的新业务收益。

不进入Stage B条件GAN，不因本次封存成功而扩大模型、调整λ或放宽门限。P-small的既有业务收益及其身份归因边界保持不变。

## 8 结项状态与产物

新结项状态：

```text
status = closed_all_exact_fallback
engineering_closeout_complete = true
P3_sealed = true
fallback_verified = true
original_stop_preserved = true
new_training_fits = 0
formal_complete = false
H_scored = false
primary_comparisons_scored = false
```

`formal_complete=false`是正确状态：本次只完成用户授权的工程结项，没有执行P4正式业务评价。原run-02的错误终态继续保留；run-03成功状态是补充结项，不是改写原失败。

- [结项记录](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/post-input-associated-representation-20261014/run-03/completion.json)。
- [最终模型封存](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/post-input-associated-representation-20261014/run-03/manifests/models-complete.json)。
- [720条端点](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/post-input-associated-representation-20261014/run-03/manifests/endpoints.json)。
- [CUDA精确回退核验](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/post-input-associated-representation-20261014/run-03/audits/fallback-replay.json)。
- [历史完整性核验](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/post-input-associated-representation-20261014/run-03/audits/historical-integrity.json)。
- [独立验收](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/post-input-associated-representation-20261014/run-03/independent-audit.json)。
- [结项封存](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/post-input-associated-representation-20261014/run-03/verification.json)。
- [新增成本与继承台账](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/post-input-associated-representation-20261014/run-03/ledger.json)。
- [P3只封存修复入口](F:/Program/VSCode/MyGit/ProxyAnalysis/eval/post_associated_p3_closeout/run.py)与[说明](F:/Program/VSCode/MyGit/ProxyAnalysis/eval/post_associated_p3_closeout/README.md)。
- [原运行结果分析](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/post-input-associated-representation/run-02/results-analysis-20261014.md)。

本次没有推送仓库、改写旧报告或启动后续训练。
