# Extend v3 路径类型与断点恢复修复

## 原始故障

首次正式流水线在读取提前生成的 `W-shadowsocks-f0-g0-r0` 完成标记时停止。JSON 文件路径是字符串，底层 `file_hash` 直接调用 `path.open()`，因此抛出 `AttributeError: 'str' object has no attribute 'open'`。正式分类尚未启动；这不是科学门限失败。

## 修复范围

- 仅在正式执行公共模块中增加 `sha(path) -> file_hash(Path(path))` 适配，不修改准备阶段封存的 `audit.py`。
- 原 `execution-contract.json`、失败记录和修复前代码保留；修复前快照在 `formal-01/repair-02/before`。
- 新执行合同为 `execution-contract-revision-02.json`，科学字段与旧合同逐项比较；只登记工程代码、修复原因及兼容清单。
- 旧产物仅接受兼容清单中逐项登记且哈希一致的生成完成标记；不开放任意旧合同、不将兼容范围扩大到分类模型。
- 新生成故障写入独立 `generation-failure-revision-02.json`。只有原始故障的精确哈希被登记为已处理；新故障仍阻止继续。

数据成员、C/U/H 权限、生成坐标、种子、视图、CUDA 模型与预算、评分脚本及科学门限均未改变。

## 验证

14 项测试通过，包括：字符串/Path 哈希一致、JSON 完成标记恢复、损坏与缺失文件拒绝、未知合同拒绝、无完成标记拒绝、旧生成完成标记的严格白名单、reference/H 标签封锁、真实恢复分支不读取训练包且不写已有文件，以及原有 CUDA 数学测试。

第一次测试运行因系统 pytest 临时目录访问权限失败；改用核对后新建的工作区专用临时目录运行，未改变测试断言。通过记录为 `outputs/extend-formal-v3-repair-tests-02b.xml`。

重新审计了 601 个完整场景（T 480、W 121），共 1,202 个生成包、5,192,640 条生成样本。所有文件哈希、访问/视图完整性、必要摘要可行域均通过；T 的生成 F 与查询 pre F 一致。兼容清单为 `formal-01/repair-02/compatibility.json`。

真实断点跳过及既有文件内容/修改时间验证结果保存为 `formal-01/repair-02/resume-verification.json`。完成后的流水线将从剩余场景继续，仍先通过全量生成门控，才允许正式分类。修复通过不等于业务实验已完成，更不构成方法有效性结论。

## 运行与结果位置

使用 Pytorch312：

```powershell
& 'D:/Tools/Anaconda/envs/Pytorch312/python.exe' eval/extend_calibration/run_formal_pipeline.py
```

此有限任务按原顺序运行：生成工程验证 → 剩余生成 → 全量生成门控 → CUDA 独立头验证 → 受限分类训练/推理封存 → reference 训练/推理 → 统计评分。

查看 `formal-01/pipeline-progress.json` 与阶段日志了解实际状态。任一阶段返回错误即停止，不修改阈值、不换样本、不自动绕过门控。分类与统计尚未完成时，不应报告新的 F1 或增量结论。
