# 跨业务配对校准：生成阶段报告

日期：2026-09-28。

**状态：XBC0–XBC5已执行；XBC5阶段门未通过，按批准方案停止正式分类，等待用户决定。**

## 1. 本轮实际做了什么

沿用0916的SS/VLESS、六业务、30内容与240访问。五外折、三个目标post未覆盖业务组、八均衡校准轮换，共240个scenario。每个scenario的C只有四种辅助业务的6内容/24配对访问；U为18内容/72个pre访问，其中未覆盖业务32访问、辅助业务40访问。

|   group | target_post_uncovered                                              |
|--------:|:-------------------------------------------------------------------|
|       0 | github.com::repository_view / youtube.com::search_results_view     |
|       1 | wikipedia.org::article_view / bing.com::search_results_view        |
|       2 | youtube.com::video_playback / developer.mozilla.org::document_view |

原七维访问摘要、Ridge alpha=1、8视图、整数解码和最多32次完整向量重抽均未改变。X2固定中心、X3无条件联合漂移、X4真实配对、X5循环错配、X6组级无序集合。没有分类性能，不能据此判断真实配对是否改善新业务识别。

## 2. 实现和工程验收

- X6仅接收内容关联、pre七维和post六维；校准session/repetition/时间/连接索引及post F不在其生成包中。独立进程运行组级生成，没有读取配对训练包。
- X6在log坐标拟合内容均值；按内容LOCO构造全部4×4组内残差，等组、等访问权重。没有借用真配残差；96个组合不是96个独立访问。
- CUDA float64完整组合解与均值目标解最大差4.79e-16，梯度核对最大差1.14e-15；独立排列后的参数、残差多重集和固定随机样本不变。另有非最优参数梯度测试。
- 7项单元测试通过；角色污染、禁止字段、预算/轮换均衡、父内容/flow/capture互斥检查通过。生成后的5040个Ridge拟合、2073600个视图及所有donor/LOCO来源审计通过。
- 所有拟合使用CUDA；导出/采样/统计使用CPU。U_post、H_pre和H标签没有进入生成；额外权限XR尚未运行，测试预测尚未生成。
- 历史双侧共同资格仍保留，不能将权限屏蔽解释为无需捕获U_post。原始来源与旧实验哈希未改变。

## 3. 预定合法性门

门限在生成前冻结：首次非法率≤10%、fallback≤1%。按部署×未覆盖业务组×生成臂×new/cal独立判断，不按两个业务角色合并。

共60个门限单元，其中8个未通过。首次非法是第一次候选被拒绝，不是最终合成样本仍不合法。

| protocol   |   business_group | arm   | business_role   |   views |   first_invalid_rate |   fallback_rate | passed   |
|:-----------|-----------------:|:------|:----------------|--------:|---------------------:|----------------:|:---------|
| VLESS      |                0 | X3    | cal             |   38400 |             0.118724 |        0.000000 | False    |
| VLESS      |                0 | X3    | new             |   30720 |             0.139486 |        0.000000 | False    |
| VLESS      |                0 | X5    | new             |   30720 |             0.105339 |        0.000000 | False    |
| VLESS      |                2 | X3    | cal             |   38400 |             0.102682 |        0.000000 | False    |
| VLESS      |                2 | X3    | new             |   30720 |             0.107292 |        0.000000 | False    |
| VLESS      |                2 | X4    | new             |   30720 |             0.101074 |        0.000000 | False    |
| VLESS      |                2 | X5    | new             |   30720 |             0.104753 |        0.000000 | False    |
| VLESS      |                2 | X6    | new             |   30720 |             0.107292 |        0.000000 | False    |

### 未通过单元的首次非法原因

| protocol   |   business_group | arm   | business_role   | first_reason           |   views |
|:-----------|-----------------:|:------|:----------------|:-----------------------|--------:|
| VLESS      |                0 | X3    | cal             | R_E_U_order            |    4256 |
| VLESS      |                0 | X3    | cal             | direction_imbalance    |     303 |
| VLESS      |                0 | X3    | new             | R_E_U_order            |    4285 |
| VLESS      |                0 | X5    | new             | R_E_U_order            |    3050 |
| VLESS      |                0 | X5    | new             | direction_imbalance    |     186 |
| VLESS      |                2 | X3    | cal             | R_E_U_order            |    3608 |
| VLESS      |                2 | X3    | cal             | direction_imbalance    |     335 |
| VLESS      |                2 | X3    | new             | R_E_U_order            |    3296 |
| VLESS      |                2 | X4    | new             | R_E_U_order            |    3105 |
| VLESS      |                2 | X5    | new             | R_E_U_order            |    3215 |
| VLESS      |                2 | X5    | new             | runs_below_connections |       3 |
| VLESS      |                2 | X6    | new             | R_E_U_order            |    3294 |
| VLESS      |                2 | X6    | new             | runs_below_connections |       2 |

全部细项见[generation-legality.md](generation-legality.md)；训练侧范围描述与谱系检查见[support-and-audit.md](support-and-audit.md)。

## 4. 应怎样解释

若最终fallback为零，说明重抽可以返回满足必要摘要约束的样本；但并不能绕过首次非法率阶段门。高拒绝率意味着原候选分布经重抽筛选，最终分布已受合法性条件影响。它不自动证明业务标签失真、不可跨业务迁移，或配对方法没有价值。

门未过时不会把阈值放宽、只跑过关业务、删除X6或更换残差后继续称为同一实验。尤其X6是检验“精确对应增量”的必要控制，不能为了训练顺利而取消。

## 5. 后续需要的决定

当前保留全部生成产物，并停止XBC6–XBC10的分类/推理/评分。建议先冻结这次可行性结果，再单独批准一次仅使用C与U_pre的拒绝机制诊断，区分目标中心、残差尺度与约束边界，不使用U_post或测试成绩选修复。

若用户明确授权保留当前重抽机制运行探索性分类，可以另登记例外版本，保留所有业务和对照，并将合法性门失败写进结果；这不是原计划已通过的正式主实验。另一个选项是直接结束本轮。未经确认不自动修改方法或启动flow生成。

## 6. 文件与复现

配置：`configs/cross-business-calibration-0916.yaml`；代码：`src/proxy_analysis/cross_business_calibration/`；执行脚本：`eval/cross_business_calibration/`；全部权限包、模型、生成视图与审计：`outputs/cross-business-calibration-0916/run-01/`。

`contract.json`和`worker-contract.json`冻结来源与生成实现，`group-engineering.json`记录CUDA等价性，`generation-gate.json`记录逐单元失败，`generation-audit.json`记录谱系与数值审核。没有新分类F1、CE或双重增量区间。
