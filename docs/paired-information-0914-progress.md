# 0914-only 配对信息分析进度

## 最新补充（2026-09-15）

已完成固定主队列的去首轮、nonempty、排除完整重传敏感性：每种20次错配；以及真训练→错测试、错训练→真测试各20次、两种Δ表示，共218组完整LOUO任务。原强相关量剔除及代数恢复基线已补齐，840条强相关剔除预测与0914旧OOF逐值核对通过。

补充报告：`outputs/paired-information-0914/run-01/execution-diagnostics/report.md`。机器产物位于`sensitivity-01/`与`execution-diagnostics/`。

结论需收紧：Δ17真配对损失优势在去首轮时为0.1899 bits，URL区间[0.0509,0.3705]；排除完整重传为0.2205，[0.0699,0.4107]；nonempty为0.0937，区间[-0.0282,0.2257]跨零。不能声称所有包选择口径下都已证实稳定优势。

462个选定会话均为TrafficTracer 1.0.27、cold模式。主队列70个同URL同轮次SS/VLESS对的配置时长、活动状态、导航状态与缓存模式均相同，但访问起点间隔中位数56.79秒；同轮不等于同步网络条件。profile指纹均不同，未解释指纹生成机制，不能直接将其解释为配置不一致。

Bilibili的有效播放标签仍保留；其未进入主队列的原因包含路由/质量、无可用exclusive侧与完整网格不齐，不是单纯因播放验证未通过。相应逐会话证据见`session-execution.parquet`。

以下为上一阶段记录，原“剩余工作”中的本轮已完成项由本节更新，不改写历史结果。尚未做全部实验的独立重训练复现与业务内容语义完整审核。

日期：2026-09-15。数据仅0914；未新增采集、未加载旧批次、未推送本轮代码。

## 已执行

来源登记464个存储尝试、462个选定会话；主队列由规则重新构造为14 URL×SS/VLESS×5轮=140会话，与既有主队列身份一致。人工活动标签仍采用effective口径。

导出140会话、3种selection的双侧标量/直方图/累计曲线。7,560条真实比较（含18项指标）回放通过，包括数值、缺失原因与层级；原始捕获、旧产物不修改。

已运行：

- 旧OOF指标复核，含metadata/missingness诊断；
- 完整LOUO六视图和10项pre家族/家族剔除；
- 100次错配，每次两种Δ表示、每次完整LOUO，并在内层调参中分别重配对；
- 六视图的训练侧嵌套组外温度校准；
- 六目标恢复、训练均值、已知部署oracle、固定/调参ridge与名义家族剔除；
- donor映射、内外折身份、OOF覆盖、来源指纹结构验收；URL级bootstrap；
- 业务URL覆盖以及70组同URL同轮次SS/VLESS的pre工作量、时间间隔和质量记录。

全部134项单元/回归测试通过。独立验收是结构与身份检查，不冒充独立模型重训。

## 主结果

| 未校准视图 | macro-F1 | log-loss(bits) |
|---|---:|---:|
| pre14 | 0.9212 | 0.4117 |
| post14 | 0.8786 | 0.8669 |
| 双侧标量28 | 0.9356 | 0.2295 |
| 标量Δ14 | 0.9714 | 0.1013 |
| 双侧标量+分布 | 1.0000 | 0.0104 |
| Δ17 | 1.0000 | 0.0109 |

分布联合对照包含双侧归一化直方图与累计曲线，不与标量拼接混淆。其结果说明不能从Δ优于单侧直接推断Δ具有独有优势。

新内层分组以规范URL标识，旧模型用activity_id哈希；GroupKFold的组排序改变内层划分与C选择。新post损失0.8669并非旧模型1.7201的原样复现，也不归因于数据改变；旧OOF在baseline-recheck中复核仍为1.7201。

| 错配对照 | 真配对loss | 错配平均loss | 真配对优势及URL区间 | 错配平均F1 |
|---|---:|---:|---|---:|
| Δ14 | 0.1013 | 0.3767 | 0.2754 [0.0909, 0.5158] | 0.9245 |
| Δ17 | 0.0109 | 0.2354 | 0.2244 [0.0634, 0.4327] | 0.9450 |

真配对优势为错配loss减真实loss。区间按100次错配的样本平均损失，再对14 URL重采样，条件于已经拟合的OOF模型，不包含完整训练不确定性，不是互信息区间或因果效应。

pre的IAT单量F1约0.8855、长度单量约0.7958；metadata诊断balanced accuracy为0.5，missingness也是0.5。这不足以排除所有环境混杂或证明拥塞机制。

训练侧调参ridge：packet R²约0.0293、bytes 0.3393、burst 0.3805、FR 0.1858、length JS -0.0850、IAT JS 0.2277。它们是有限模型的LOUO结果，不证明完整变换可逆。名义家族剔除与旧实现额外剔除强相关量的规则不同，已在报告中标注。

校准并不总改善：post损失从0.8669增至1.1582，Δ14从0.1013增至0.8947，均保留，不事后择优替换。

## 业务门与剩余工作

0914 broad/repeat去重后，Bilibili视频2个URL、YouTube视频1个URL；不能用重复访问当独立内容。未启动业务teacher。其他page_load的业务语义、内容独立性与workload兼容性仍需审核，不笼统宣布所有业务任务不可行。

当前完成的是主队列LOUO阶段，不是整份计划的所有敏感性。后续仍包括：去首轮及其他selection模型敏感性、真训练→错测试扰动、完整辅助代数恢复基线、原强相关剔除对照，以及更完整的活动/观测跨度/路由执行因素分析。无需新增采集或旧批数据。

## 产物入口

- `outputs/paired-information-0914/run-01/report/report.md`：详细结果。
- 同目录`independent-validation.json`、`pairing-value.parquet`、`pre-quality-pairs.parquet`、`business-feasibility.json`。
- 上级目录`source-manifest.json`、`cohort.parquet`、`exclusions.parquet`、`baseline-recheck.parquet`、`side-summaries.parquet`。
- `views/`、`families/`、`wrong-000/`至`wrong-099/`、`calibration/`、`recovery/`：预测、映射、调参记录和汇总。

## 可运行入口

从仓库根目录，在Pytorch312设置`PYTHONPATH=src`：

```powershell
python -m proxy_analysis.paired_information.prepare --stage prepare
python -m proxy_analysis.paired_information.prepare --stage summaries
python -m proxy_analysis.paired_information.experiments --mode smoke
python -m proxy_analysis.paired_information.experiments --mode views
python -m proxy_analysis.paired_information.experiments --mode families
python -m proxy_analysis.paired_information.experiments --mode wrong --seed-index 0
python -m proxy_analysis.paired_information.extensions --stage recovery
python -m proxy_analysis.paired_information.extensions --stage calibration
python -m proxy_analysis.paired_information.report
```

wrong需0至99各运行一次。准备、模型、报告目录拒绝覆盖；重跑需新配置output_root，摘要阶段可按指纹复用本轮缓存。report当前默认读取默认配置，若另起输出需先为报告入口增加对应配置参数，不能直接声称支持任意新配置的一键完整重跑。
