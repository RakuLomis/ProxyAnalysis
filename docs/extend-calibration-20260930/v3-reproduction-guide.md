# Extend v3 复核与复现指南

本指南区分文档复核、已有产物核对和重新运行实验。仓库不包含 Datasets、outputs、本地 plan、模型或大型二进制台账，仅克隆仓库不能端到端复跑。内容划分还依赖已冻结的历史角色模板；不得临时重新随机划分来冒充原实验。

## 已有结果的只读核对

在仓库根目录，使用 Pytorch312：

```powershell
& 'D:/Tools/Anaconda/envs/Pytorch312/python.exe' eval/extend_calibration/build_v3_evidence.py
```

新脚本不导入训练入口、不调用 freeze、不读取 PCAP、不重抽 bootstrap。它读取已有契约、manifest、模型文件哈希、预测、角色、事件和统计数组，独立重构完整六类 F1，并对照已保存 bootstrap 数组的分位数。输出仅写入：

- `docs/extend-calibration-20260930/v3-results-supplement.md`；
- `docs/extend-calibration-20260930/v3-coverage-tables.md`；
- `docs/extend-calibration-20260930/v3-evidence-index.md`；
- `outputs/extend-calibration-20260930/run-01/extraction-03/evidence-review-01/`。

证据目录 audit.json 保存输入相对路径、SHA256、脚本哈希、检查结果；读取结束后复核所有已登记输入未变化。它不宣称逐字节验证所有原始 PCAP，也不取代既有采集审核。CPU 汇总不违反训练与推理的 CUDA 要求。

## 环境与数值约定

原运行环境为 Pytorch312、Python 3.12、PyTorch 2.5.1、CUDA 12.4、RTX 4060 Ti 16 GiB；统计使用 NumPy/Pandas/Parquet 支持，Markdown 表格需 tabulate。生成 Ridge 为 CUDA float64，分类器为 CUDA float32。应记录实际包版本及驱动，不能仅因环境名一致就保证逐位复现。

冻结源文件按原始字节哈希验证。仓库存在 Git 行尾转换提示，另一台机器 checkout 后若 LF/CRLF 改变，字节哈希可能不同。不要直接覆盖原哈希或关闭校验；先比较语义和字节差异，并在新运行目录登记环境与合同。合同还包含历史绝对路径，不是已完成跨机器可移植化的一键入口。

## 所需本地证据

基础目录为 `outputs/extend-calibration-20260930/run-01/extraction-03`。

| 对象 | 所需文件与用途 |
|---|---|
| 原始资格来源 | Datasets/extend；run-01 的 G1 台账、定点审计及 extraction-01 元数据池 |
| v3 窗口与事件 | prepared-windows.json、sessions 下 W 事件/T-pairs、full-coverage、full W/T features |
| 资格边界 | clock-anchors-01、verification-01、isolation-01、identity-source-evidence |
| 训练角色与权限包 | training-preparation-01/roles.parquet、packages、preregistration.json |
| 原实验模型与统计 | formal-01/generation、classifiers、预测 seals、scored-predictions、metrics、contrasts、bootstrap 数组 |
| 修复链 | execution-contract.json、execution-contract-revision-02.json、repair-02/compatibility、修复前快照 |

如果只有仓库文档，可核对公式、设计和公开结果表，不能验证未提供的数据/模型哈希内容。如果只有统计产物，可复核评分，不等于从原始包重建观测。若缺旧 roles 模板，应索取原冻结表而非凭描述猜测成员。

## 正式流水线的历史顺序

以下是已运行阶段的入口说明，不是要求为本文重跑：

```powershell
python eval/extend_calibration/formal_generate.py --stage engineering
python eval/extend_calibration/formal_generate.py --stage generate
python eval/extend_calibration/formal_generate.py --stage gate
python eval/extend_calibration/formal_classify.py --stage engineering
python eval/extend_calibration/formal_classify.py --stage restricted
python eval/extend_calibration/formal_classify.py --stage infer
python eval/extend_calibration/formal_classify.py --stage reference
python eval/extend_calibration/formal_classify.py --stage infer-reference
python eval/extend_calibration/formal_score.py
```

统一有限批次入口为 `run_formal_pipeline.py`，各已完成部分可验证后跳过，但评分脚本会写统计文件，因此不要把它当只读核对工具。此次整理只运行 build_v3_evidence.py。

若确需独立重训，应先建立新实验目录、登记输入与代码、保留当前全部封存结果，再按相同角色和预算运行；现有入口硬编码当前目录，不应直接改动被封存源码或删除完成标记强迫重训。本工作没有实施新的可移植训练入口。

## 两版执行合同

首次正式生成在读取已有 JSON 完成标记时因字符串路径没有 open 方法而停止，601 场景已完整生成。修复只在正式层将路径转为 Path，增加恢复测试与精确旧产物兼容清单。准备阶段底层 audit.py 未修改。

旧合同、失败记录和产物保留；601 场景、1202 生成包兼容新执行合同，新增场景与分类器使用 revision-02。兼容清单不是接受所有旧合同。新故障使用独立记录并仍停止流水线。详见 [修复记录](formal-v3-repair-02.md)。

原准备合同授权为 false 是历史快照；正式合同记录后续用户授权。原 full-gate 的全 TCP 生命周期隔离字段为 false 也保留，通过的是后续源码支持的登记实体分组资格，而非把所有历史 false 改成 true。

## 论文引用的结论边界

引用配套契约和结果时应写“所观测的部署”“已见部署的未见内容”，保留双侧历史资格成本、C 配对预算和 U 标签预算。测试只输入 post 不等于采集和样本整理不需要双侧。更多部署不自动成为外部验证，普通区间跨零不构成等效。
