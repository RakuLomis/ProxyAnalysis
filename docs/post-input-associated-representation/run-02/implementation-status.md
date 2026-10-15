# post关联表征分支独立修订版运行状态

2026年10月14日。P0按哈希复用，P1单元检查、数值重放与CUDA预算先导均通过，Stage A正在执行P2。

本版只修工程记录和批处理数值接口；31个科学字段与原合同一致。原run-01失败和v2旧接口诊断保留。实际执行为eval/post_input_associated_representation_v3，输出为run-02。

P1固定1000步的单头/双头最大概率差与logit差均为0。九教师和45先导分支完成，保守外推训练约7.9小时，低于9.6小时启动门及12小时安全上限。旧失败及本轮工程成本累计计费，不因重新登记而清零。

后续顺序为源内矩阵、源内选择、最终模型封存、H-post预测、预测封存、H标签评分。任何数值、权限或全局预算门失败会停止，不自动删角色、放宽门或重试失败阶段。

当前没有读取实际目标U或H-pre，没有新业务评分，没有启动Stage B。

启动复核时P2已完成首12/720个源内任务，累计18份教师和210份正式/先导分支拟合；该数包含P1九教师和45分支，不是新增独立访问。监督器和CUDA训练进程正常，未出现错误日志。本文是启动状态快照，后续实际状态以progress.json和completion.json为准。

来源：[工程修订与验收](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/post-input-associated-representation/run-02/engineering-repair-report.md)、[实时进度](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/post-input-associated-representation-20261014/run-02/progress.json)、[累计账本](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/post-input-associated-representation-20261014/run-02/ledger.json)。
