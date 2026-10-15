# 动态漂移资格策略合同与实施状态

2026年10月13日。原资格启用、固定回退、全五折累计20小时优化上限和C业务代价门已按用户确认冻结。P1审计通过，P2条件已封存，P3剩余144条轨迹已启动；本页记录启动状态，不代表业务实验完成。

## 合同与任务

QP、QT、QG分别使用P、P、G数学后端。QP与QT只在获得原资格时使用实际终态q，否则精确引用同角色P-small；QG相应引用G-small。启用依据仍为原stationary或finite_progress，不选最佳历史checkpoint，也不放宽残差门。

单轨迹最多20次接受更新、40个trial-q评价，每轮最多8个回溯候选。资格失败和单轨迹预算停止按合同回退；身份冲突、越权读取、SHA不一致、后端数值失败、全局资源不足及尚未执行的角色均不能默认为回退。

队列保持SS、VLESS、Trojan、VMess四部署，六业务、30内容、480访问、96维、五个全局内容折、三组遮蔽、60角色及每角色12个合法源内任务。内容的全部重复、两侧和内部flow共同划分。模型输入不包含协议身份、IP、端口、SNI、URL文字或访问身份。

全五折累计优化上限为72000秒，包含复用f0的8293.487963500433秒及此前保守尾部计费；新增优化剩余额度约17.6963小时。暂停不能重置预算。最终模型、预测、统计和报告的成本独立记录。

C代价门为QP相对P-small的总体F1_C下降不超过1个百分点、每部署下降不超过2个百分点。该门是预先冻结的描述性推进条件，不是统计非劣效性证明。

## P1只读审计结果

| 项目 | 结果 |
| --- | --- |
| P/G回退模型 | 120个全部通过 |
| 最终训练槽位 | 每个928行，原标签与质量、90% CORAL加10% mapped-pre |
| 最大q=1槽位误差 | 2.8310687127941492e-14，小于原1e-12重放容差 |
| 最大冻结模型目标误差 | 0 |
| 模型梯度 | 均通过原坐标1e-5验收门 |
| 原参照完整性 | 420个全部通过 |
| f0复用决定 | 36条，12启用、24回退 |
| 新增源内或最终拟合 | P1阶段均为0 |
| H/U数值读取 | P1阶段为0 |

回退核验覆盖角色与内容来源、固定P/G映射及eta、分类正则t、预处理、两侧排序、最终槽位、原W正则与无bias正则政策。映射与槽位均来自冻结资产，不重新拟合。推理时使用同一模型/query缓存，要求回退与对应基线的概率、log-prob和类别精确一致。

原优化政策单元检查25项、权限负例7项、新资格策略检查13项均通过。后两类包括QT不得读取完整关系目标、G不得读P资产、未执行及完整性失败不能回退，以及模型未封存前禁止H查询、预测未封存前禁止H标签读取。这些是新策略及权限检查，不是重新进行旧LR、隐式导数或激活边界研究。

## 预备审计修订记录

第一次预备审计在读取P映射eta时因字段接口不一致停止：P映射的eta位于mapping.eta，G映射还另有顶层eta。两种映射的实际eta均为100。失败发生在新增训练和H/U读取之前，旧运行及其代码保持不变。

独立修订版使用两者都提供的mapping.eta进行核对，目标、门限、数据权限和预算未变。失败预备版本保留于run-01；正式就绪版本为run-02，代码为eval/dynamic_soft_drift_qualified_policy_v2。旧P0及f0全过程读取日志的已知缺口继续保留，不补造历史审计。

## 后续执行顺序

固定按f1至f4及原角色顺序完成144条新轨迹。全部180个启用或回退决定及q-use封存后，才为启用且非恒等端点拟合最终LR；回退直接引用冻结模型，不制造新拟合。三策略与七参照合计600逻辑端点，实际新增模型数按启用情况统计，最多156个。

全部模型端点封存后才使用CUDA float64生成14400行H-post预测；全部预测封存后才打开H标签。主评价包含全部60角色，使用完整六分类混淆矩阵、部署及遮蔽等权F1_U，以及预登记七项共同内容簇bootstrap家族。不会先看f0新F1再决定其他折是否继续。

执行采用无周期、无自动重试的一次性监督任务，保存逐trial状态、心跳、退出码和账本。若完整性、数值或全局资源门失败，程序停止并留下未决角色；不会静默删角色、增加预算或改门。按原先导外推，新增优化约9小时数量级，尚不能保证该耗时。

## 产物入口

- [冻结合同](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/dynamic-soft-drift-qualified-policy-business-20261013/run-02/manifests/experiment-contract.json)
- [回退兼容性审计](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/dynamic-soft-drift-qualified-policy-business-20261013/run-02/audits/fallback-compatibility.parquet)
- [f0复用决定](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/dynamic-soft-drift-qualified-policy-business-20261013/run-02/audits/pilot-reuse-index.parquet)
- [运行进度](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/dynamic-soft-drift-qualified-policy-business-20261013/run-02/progress.json)
- [累计账本](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/dynamic-soft-drift-qualified-policy-business-20261013/run-02/ledger.json)

正式结束后在对应run-02报告目录生成complete-report.md，包含七项主比较、C/U分项、部署及业务结果、启用与回退覆盖、实际计算量和预登记结项判断。后续是否继续新的研究分支仍需独立确认。
