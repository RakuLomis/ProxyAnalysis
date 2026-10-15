# 动态软约束漂移实验安全序列化修复记录

2026年10月12日，正式实验以独立run-02重新启动。修复针对检查点的保存和读取格式，不改变科学任务、学习目标或数值验收政策。run-01的停止记录、代码和全部产物保留且纳入新版本的哈希核验；其q、业务模型和反馈缓存均不导入新训练。

## 原停止原因

run-01完成了首个D-P角色的20次更新、q20终态审计、252个源内数值解及一个最终LR。随后T-P读取共享P反馈缓存时，安全加载器拒绝了NumPy标量。隐式梯度诊断中的precision_risk由NumPy运算产生，随嵌套checks字典写入检查点。这是缓存序列化错误，不是数值求解拒绝，也不是业务分类失败。

## 修复范围

新IO层递归将NumPy元数据标量转换为Python基本类型，Torch张量保持原数据。其他自定义对象及NumPy数组被明确拒绝，不静默转换模型表示。在发布每份检查点及接受标志前，程序使用weights_only=True重读，并核对字段类型、键顺序、标量数值和张量字节。安全读回失败就停止，不发布已接受资产。

不使用weights_only=False，不添加全局反序列化白名单，不修改安装的PyTorch或旧隐式梯度实现。新代码位于eval/dynamic_soft_drift_formal_v2，输出位于outputs/dynamic-soft-drift-business-formal-20261012/run-02。

## 已通过的修复检查

| 检查 | 结果 |
| --- | --- |
| 含NumPy标量的旧式缓存错误复现 | 安全加载正确拒绝 |
| 嵌套检查字典与Adam状态安全保存及重读 | 通过 |
| 独立Python进程重读合成检查点 | 通过，无全局白名单 |
| 元数据转换后的NumPy对象残留 | 0 |
| 张量字节、大整数和负零保留 | 通过 |
| 不支持对象与读回不一致负例 | 六项均正确拒绝 |
| 新正式真实反馈缓存独立进程重读 | 通过，CUDA float64，无NumPy元数据 |
| 新旧科学契约对比 | 28项字段一致 |
| 新旧计算模块AST对比 | 九个模块一致 |
| 旧封存代码哈希 | 13份均未改变 |

正式准备还重新通过了全部权限负例、480份实际C-OOF重放、120组关系系数、720个源内任务的P/G缓存以及120份最终训练缓存检查。没有新增映射拟合或读取H/U数值。

## 重启后的实验边界

run-02于20时21分04秒启动，使用Pytorch312、CUDA float64。先完成外折0的12个角色与三臂，数值和资源门通过后继续全矩阵。修复没有增加更新次数、候选数、求解预算或改变损失权重；旧七类冻结参照继续按原来源复用。

源内求解、细档校验和导数稳定性失败仍会停止评分链。所有600个端点封存后才允许H-post查询，全部14400行预测封存后才允许H标签评分。修复检查通过不等于业务增量成立。

## 证据入口

- [修复契约](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/dynamic-soft-drift-business-formal-20261012/run-02/manifests/repair-contract.json)
- [安全格式回归检查](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/dynamic-soft-drift-business-formal-20261012/run-02/audits/payload-roundtrip.json)
- [真实缓存独立重读检查](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/dynamic-soft-drift-business-formal-20261012/run-02/audits/real-feedback-readback.json)
- [原停止记录](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/dynamic-soft-drift-business-formal-20261012/run-01/completion.json)
- [run-02进度](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/dynamic-soft-drift-business-formal-20261012/run-02/progress.json)
