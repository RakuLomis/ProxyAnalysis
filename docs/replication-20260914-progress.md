# 20260914 数据集复现：阶段产物与验收记录

更新：2026-09-14。结果根目录：`outputs/replication-20260914/run-01`。

## 1. 当前结论

两批最新数据的全量基础特征、机器学习宽表、双轨表和三张对齐表已经生成并通过质量门。repeat 的 18 个代表指标及 A/B/C 重复性分析、工作负载敏感性和报告已完成。

broad 的 Q1/Q2/Q3 与敏感性汇总现已验收通过。用户已确认 VLESS 资源级 burst_count 的口径敏感性解释，记录于 `configs/interpretation-20260914.json`；没有修改数值、阈值或原统计配置。

broad 探索性分类与16组正式嵌套 CV 已完成，15,360条OOF的site/session/索引实体隔离验收通过。repeat 信息论试跑、全量、独立重跑及OOF验收已完成；两次运行12张Parquet表逐值一致。

完整结果见[阶段总结](../outputs/replication-20260914/run-01/stage-results-report.md)，机器产物摘要见 `outputs/replication-20260914/run-01/stage-artifacts.json`。当前停止在业务Y/teacher训练之前，而不是旧的burst解释节点。

## 2. 已完成与质量证据

| 项目 | broad | repeat |
|---|---:|---:|
| 存储 attempt | 194 | 270 |
| 选定会话 | 192 | 270 |
| 全量实体特征记录 | 10,078 | 7,892 |
| 严格配对特征记录 | 1,641 | 1,838 |
| Hy2 载体窗口记录 | 41 | 65 |
| Web 会话记录 | 192 | 270 |
| 请求—连接索引记录 | 35,028 | 46,232 |
| URL—连接关联特征记录 | 15,370 | 29,446 |
| 页面协议特征记录 | 192 | 270 |

上述数量是记录数，不等于独立推断样本量。未归属连接的请求仍保留原因；没有用填补特征伪造可配对流量。Hy2 不作为严格一对一 TCP 配对，也不将 UDP 方向切换称为原始 TCP FR。

- 原始捕获审计合计 25,658,738 条记录，解析错误及 snaplen 截断均为 0。
- 时间戳回退仍保留审计记录；提取时按时间戳和包序号稳定排序。
- 两批 `features-quality.json` 均为 passed，错误和警告均为 0；ML 导出校验、双轨构建成功。
- 两批 `aligned/aligned-quality-report.json` 均通过；请求无法归属和代理覆盖不完整属于显式警告，不将相关行无条件纳入变换推断。
- repeat 长表 19,440 行；独立验证通过：270 个 selected 会话覆盖、metric 唯一性、登记身份、缺失原因与单一提取契约。
- repeat 统计产物：within 22,968 行、ICC 1,980 行、separation 6,804 行、consistency 1,980 行。这些含多种口径/敏感性，不能累加为独立样本 n。

环境为 Pytorch312；未安装或升级依赖。最终测试日志见 `outputs/replication-20260914/run-01/execution/final-tests.log`。原始数据未修改，未提交或推送 Git。

## 3. 本次修复

1. 依据 manifest 的真实 selected attempt 登记样本；保留首次被选中但仍存在后次尝试的情况。
2. Hy2 多路径方向解析：统一提取器使用索引和经过 trace barrier 限制的声明路径。两条原失败载体的 69,864 和 64,977 个包均能解析，无需丢包。未知或矛盾方向仍失败。
3. 基础特征实现版本提升至 4，避免复用旧方向错误缓存。
4. 特征与对齐质量门取消旧数据集固定行数假设，按当前登记表和引用关系检查。
5. 对齐表保留 repetition/activity_id/target_key/target_index；页面记录 ID 区分会话，三协议覆盖按目标和轮次分组。对齐实现版本提升至 2。
6. 正式 CV 加入逐样本 OOF、训练/测试名单、特征白名单、输入指纹与 pooled 指标，防止复用不同输入的缓存；尚未执行新正式实验。
7. 执行日志重跑时归档旧日志；新增独立验收和保守新旧契约对照脚本。

## 4. 已获用户确认：VLESS burst_count 的解释

`broad/statistics/sensitivity-summary.json` 共评估 140 项方向检查，仅一项被判不一致：`url_strict_vs_weighted / VLESS / burst_count`。

| 资源口径 | 有效记录 n（不是独立站点数） | 中位 log-ratio | 转回比例 |
|---|---:|---:|---:|
| URL strict | 440 | 0 | 0% |
| URL weighted | 5,248 | 0.1029239 | 约 +10.84% |

两种口径的样本集合和权重不同，不能把差异直接当作同一批样本的效应变化。这是零变化与正变化，不是正负方向反转；中位数为零也不能证明等效保持。

strict Q3：31 个 site cluster、40 个 target cluster；中位 log-ratio 的 site-cluster bootstrap 95% CI 为 [0, 0.0165293]，paired rank-biserial 为 0.0866。blocked permutation BH q 约 0.00183，但统计显著不等于具有明显实际效应，更不能覆盖口径敏感性。

页面级 Q1 是另一个 estimand：44 个会话、34 个 site cluster，中位 log-ratio 0.1168645，95% CI [0.0141963, 0.2048436]，BH q 约 0.000116。该结果不能替代资源级 strict 结果。

**已确认并实施的处理方式**：继续以 URL-strict 为资源级主分析，weighted 仅作敏感性；为 VLESS burst_count 增加“资源口径敏感”的明确解释标记，不宣称其资源级增加具有跨口径稳健性。保留页面级、资源级各自的结果和分母。冲突作为带用户授权记录的解释警告保留。

原始统计配置及其指纹不变；新批次附录单独记录用户确认、作用目录与解释，最终汇总记录附录摘要，不能自动用于其他批次。

## 5. repeat 结果与新旧对照范围

repeat 的完整 A/B/C 结果在 `repeat/audit/transformation-reproducibility-report.md`，包含逐 URL 的重复内离散程度、ICC、SS/VLESS 分离、跨 URL 方向和各类敏感性。Hy2 仍为 context 描述，未提升为完整系统范围。

初步新旧重复契约对照：17 个共同 URL 中，14 个声明 workload 契约相同，bilibili/youtube/vimeo 三者的观测时长改变；douban 仅旧批存在，rottentomatoes 仅新批存在。相同声明契约不代表网络、日期或采集版本受控。

`comparison/repeat-descriptive-comparison.parquet` 是全样本描述汇总；`repeat-common-complete-summary.parquet` 限定相同声明workload且两批均完整五轮的共同URL。broad共同有效URL、三分类同类成绩和重复二分类OOF的新旧对照也已生成。没有合并重复轮次，也没有在共同cohort上重新训练分类器。

## 6. 文件入口

每个 batch 目录下：

- `features/<protocol>/<session>/`：完整 JSON-in-Parquet 特征及 checkpoint/lineage。
- `ml/`：entity、exclusive_pair、hysteria2_window、web_session 宽表。
- `experiments/`：双轨变换与协议分类输入。
- `aligned/url-connection-index.parquet`：请求—连接索引。
- `aligned/url-aligned-pair-features.parquet`：资源关联 pre/post 特征。
- `aligned/page-aligned-protocol-features.parquet`：页面会话级三协议特征。

分析与审计：

- `broad/statistics/`：Q1/Q2/Q3、敏感性、图和机器结果；最终质量状态已通过。
- `repeat/audit/repeat_feature_long.parquet`：代表量 pre/post/Δ。
- `repeat/audit/within_protocol_repeatability.parquet`、`repeatability_icc.parquet`、`between_protocol_separation.parquet`、`cross_url_consistency.parquet`：A/B/C。
- `repeat/audit/independent-validation.json`：重复特征独立验收。
- `broad/formal/`：16组正式分类、逐样本OOF及独立验收。
- `repeat/information-validation/` 与 `information-validation-reproduction/`：独立两次信息论基线。
- `repeat/audit/repeat_statistics-validation.json`：A/B/C分母验收。
- `repeat/reproduction-validation.json`：信息论12张表逐值一致性验收。
- `comparison/`：新旧契约、共同有效样本及同类实验描述性对照。
- `execution/`：各原子命令、实现摘要、日志及历史失败记录。

## 7. 下一研究决策节点

上述复现任务已完成。YouTube在repeat中15/15播放验证通过，但只覆盖一个主要内容；Bilibili/Vimeo没有充分播放证据。若进入domain × activity业务学习，需要先确定跨内容采样和可验证活动类别，不能用page_load替代播放。信息论数学耦合的完整分布置换实验仍是新扩展，未混入本轮复现。

不自动启动业务 Y 分类、teacher/LUPI，不改变 domain × activity 标签定义，不自动补采或查询外部 CDN。
