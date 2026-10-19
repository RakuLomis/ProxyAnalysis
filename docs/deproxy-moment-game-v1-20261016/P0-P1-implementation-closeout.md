# DP-GAN1-M v1：P0/P1实施、合同复核与停止报告

日期：2026-10-16。

## 1 当前结论与权威状态

**P0可信raw训练包已完成；P1未通过整体工程与预算资格；P2—P6未启动。**

本次已实际执行固定先导的88条2000步动态路径、24个逆锚点bundle及232次凸头拟合。最终独立对照原合同发现：

1. 232个头均达到原坐标梯度和独立数值重放误差门，但一个F-G头触及2000次迭代预算。原验收接口漏检了这项拒绝条件，错误写成了`passed=true`。严格合同资格应为231/232，而不是232/232。
2. 四个实际动态CUDA桶均混合了0.0003与0.001两种学习率，不符合批准计划的“同尺寸、同lr、同阶段分桶”。每模型确实使用了各自登记的学习率和独立Adam，但这不等于已完成合规调度验收。
3. 原后端的成本诊断外推已经远超预算：中心约61.34小时，保守约116.33小时；自动推进上限19.2小时，活动保护上限24小时。

因此，**不能将本轮标为“工程通过，只差预算”**，也不能启动完整矩阵、源query评分或H评价。早先的通过标志全部保留为原始记录，由新增合同复核明确否决，不覆盖或删除失败证据。

权威当前状态：

- [当前状态指针](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/deproxy-moment-game-v1-20261016/run-01/completion-current.json)
- [修订状态记录](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/deproxy-moment-game-v1-20261016/run-01/completion-revision-02.json)
- [严格合同复核](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/deproxy-moment-game-v1-20261016/run-01/tests/P1-contract-gate-audit-02.json)

最终状态为`stop_P1_contract_and_budget_confirmation_required`。没有运行中的训练任务；不存在未运行任务自动变成β0的情况。

## 2 批准方案与代码落点

依据[批准实施计划](F:/Program/VSCode/MyGit/ProxyAnalysis/plan/DP-GAN1-M-v1-local-implementation-plan-20261016.md)，新增独立代码目录：

[eval/deproxy_moment_game_v1](F:/Program/VSCode/MyGit/ProxyAnalysis/eval/deproxy_moment_game_v1/README.md)。

本次没有修改历史实验模型、预测、分数或代码，没有推送Git，也未安装新依赖。环境为Pytorch312，使用RTX 4060 Ti 16GB、PyTorch 2.5.1、CUDA 12.4。新模型、投影、矩、线性求解、凸读出和推理均使用CUDA float64；无AMP、TF32或CPU训练回退。

主要实现文件：

| 文件 | 职责 |
| --- | --- |
| [contract.py](F:/Program/VSCode/MyGit/ProxyAnalysis/eval/deproxy_moment_game_v1/contract.py) | 数据来源、780角色、旧B0、候选及阶段权限登记 |
| [prepare.py](F:/Program/VSCode/MyGit/ProxyAnalysis/eval/deproxy_moment_game_v1/prepare.py) | 可信生产器，先按角色过滤native，再重建整数计数和raw直方图 |
| [data.py](F:/Program/VSCode/MyGit/ProxyAnalysis/eval/deproxy_moment_game_v1/data.py) | P/G/E独立能力包加载、锚点和初始化 |
| [simplex.py](F:/Program/VSCode/MyGit/ProxyAnalysis/eval/deproxy_moment_game_v1/simplex.py) | 十块欧氏单纯形投影及约定广义导数 |
| [ridge_anchor.py](F:/Program/VSCode/MyGit/ProxyAnalysis/eval/deproxy_moment_game_v1/ridge_anchor.py) | 十块加权逆Ridge |
| [moment_features.py](F:/Program/VSCode/MyGit/ProxyAnalysis/eval/deproxy_moment_game_v1/moment_features.py) | 条件一阶及原始二阶矩、fid/gap |
| [models.py](F:/Program/VSCode/MyGit/ProxyAnalysis/eval/deproxy_moment_game_v1/models.py) | 96→8→96残差、联合分类头和四动态目标 |
| [classifier.py](F:/Program/VSCode/MyGit/ProxyAnalysis/eval/deproxy_moment_game_v1/classifier.py) | 显式γ、原W上的L2、凸头求解与原坐标终验 |
| [engine.py](F:/Program/VSCode/MyGit/ProxyAnalysis/eval/deproxy_moment_game_v1/engine.py) | 每模型独立Adam、裁剪、8 streams和Graph |
| [worker.py](F:/Program/VSCode/MyGit/ProxyAnalysis/eval/deproxy_moment_game_v1/worker.py) | 分能力进程、静态/动态拟合和导出 |
| [deploy.py](F:/Program/VSCode/MyGit/ProxyAnalysis/eval/deproxy_moment_game_v1/deploy.py) | 不接收pre、标签、索引或协议条件的封闭post推理 |
| [cost.py](F:/Program/VSCode/MyGit/ProxyAnalysis/eval/deproxy_moment_game_v1/cost.py) | 形状计时及预算外推 |

后续源内选择、外层训练、预测封存、完整六类评分及复核的调度接口也已编写，但**没有据此运行P2—P6，更不能视为这些阶段已经通过真实数据验收**。

## 3 P0可信raw训练包

### 3.1 数据范围

沿用Extend中固定四TCP部署：SS、VLESS、Trojan、VMess；480次访问、30个全局内容、六业务、每内容四重复。

没有加入AnyTLS、Hy2、64URL、0914或0916；没有扫描PCAP，没有改变队列、业务标签、内容折或原B0尺度。

780个上下文为720个源内任务与60个外层角色。每源内任务192次合法真实训练访问；每外层角色352次合法真实训练访问。跨上下文累计159,360行并非159,360次独立访问，原始总体仍是480次访问。

### 3.2 raw的具体含义

这里的raw是**未标准化的96维访问直方图**，不是新提取的PCAP字节流。

从权威paired-flow数值表中按角色谓词过滤，然后针对十个特征建立整数bin计数，以该访问保留连接数归一化。没有从旧标准化教师目标、八维瓶颈或逆变换估算raw pre。

十块依次为：W_up/down、U_up/down、P_up/down、E_up/down、FR_packet_runs、R_unique_zero_runs。前四块各9箱，后六块各10箱，总计96维。

访问身份沿用`session_id → SHA256(business-query-v1:session_id) → 注册visit_id`；整数计数与分母保存在可信台账侧，不能进入G或E学习器。

### 3.3 实际验收

| 项目 | 结果 |
| --- | ---: |
| 已封存上下文 | 780/780 |
| 外层/源内角色 | 60/720 |
| 跨角色累计真实训练行 | 159,360 |
| 跨角色累计native连接行 | 7,823,912，存在跨角色复用，不是独立连接总数 |
| raw post与注册直方图最大误差 | 1.1102230246251565e−16 |
| source pre匿名多重集最大误差 | 1.1102230246251565e−16 |
| 深层复核P0封存文件 | 14,820 |
| 实际目标U训练数值行 | 0 |
| H/query特征及query标签读取 | 0 |

source pre匿名多重集重放针对旧source-pre边际；目标C的pre由可信native关联直接重建，不声称旧source-pre包本来就包含目标C。

P/G/E分别存为真配训练包、独立置乱边际与组中心/边际矩包、post-only包。G没有共同visit/session/repetition键；P/G/E训练由不同OS进程执行，不是先把P读入G再删字段。

三组训练质量各1/3，总质量1，各业务质量1/6。内层16个条件单元、48个四重复匿名组；外层22个条件单元、88个四重复组。S_A使用合法真实pre无权均值/总体标准差，低方差维保留；S_B直接绑定原B0，不重拟合。

额外元数据审计确认：每个源内任务的18训练内容加6个query内容，恰为其外层24训练内容；不包含外层H的6内容。实际目标部署不进入源内任务的两源库或伪目标校准。

### 3.4 边界

P0通过说明本轮训练材料可追溯、与注册统计口径一致；不等于重新证明了完整physical连接重建、无索引在线分段或外部DIRECT观测可行性。

## 4 实现的模型与损失

P/G分别拟合十块逆Ridge，α=1；P使用同次raw pre，G使用同内容同部署组中心。逆锚点共1020参数。

动态生成分支为96→8→96的ReLU低秩残差，无输出bias，U2零初始化；与固定逆锚点相加后投影至十块单位单纯形。E-post采用raw post恒等锚点，不读取pre。

分类头使用标准化96维估计pre，保持真实侧与估计侧各0.5质量的CE。头为六类、五维类别对比坐标；原W施加显式γ L2，bias不罚。

F-P/F-G包含rec、fid、gap、0.1dev和既定L2；N-P只删除fid/gap；E-post采用对应的纯post任务和dev/L2。fid/gap在raw频率中计算；二阶目标是平均aaᵀ，不是组中心的外积。gap保留真实pre域差，而不是把域差压为零。

2000步后冻结生成器，重新充分拟合最终凸头；没有用Adam头的业务表现决定是否执行refit。

这里没有训练二分类GAN判别器。有限二次矩对偶已被消去，以既定矩差平方训练；单纯形约束只保证直方图块合法，不保证完整TCP/协议会话、联合跨块可实现性或逐访问恢复正确。

## 5 固定P1实际执行范围

固定f0/i1，四role_target×三个业务遮蔽组，共12个任务；三个字段不能混称：

| role_target，仅角色组织标签 | 合法query所属伪目标部署 |
| --- | --- |
| SS | VLESS |
| VLESS | Trojan |
| Trojan | VMess |
| VMess | SS |

query身份只用于合同说明，P1未读取query数值或评分。

- 12角色×P/G：24个逆锚点bundle。
- 真实pre/post各三γ初始化：72个凸头。
- R-P/R-G各三γ：72个静态凸头。
- 所有12任务四动态臂H01：48条路径。
- 固定SS/G0和VMess/G2补H02—H06：40条路径。
- 动态共88条，每条2000步，总176,000次正式逐模型Adam更新；最终refit88个头。
- 共232次物理凸头拟合。它们计入完整计划上限，不是完整业务矩阵已经完成。

源内种子20261014。lr为0.0003/0.001；γ为0.0001/0.001/0.01。没有新增秩、损失权重、训练长度或候选搜索。

## 6 已通过的数值检查，以及未通过的整体资格

### 6.1 数学与局部工程证据

35项主要合成检查覆盖Ridge、投影KKT/幂等/常数平移、边界约定、显式Φ与快速矩、矩梯度、组中心恒等式、类别对比坐标、独立分类梯度、融合及能力权限负例。

四动态臂完整目标在h=1e−4和1e−5下的8项差分，最大误差约3.48e−11，达到原atol=1e−8/rtol=1e−6门。

32模型、8 streams、Graph的合成前缀1/10/100步，参数、梯度和Adam状态与独立执行的最大差为0，step精确一致。**该夹具使用单一H01学习率，不能覆盖实际运行中混合lr分桶的合同偏差。**

232个凸头的原始数值摘要：

| 项目 | 最大值 | 原数值门 |
| --- | ---: | ---: |
| 原W/c最大梯度 | 3.1045185363e−6 | 1e−5 |
| 独立目标归一化误差 | 1.6653345369e−16 | 1e−10 |
| 独立梯度归一化误差 | 3.5285776603e−16 | 1e−10 |
| 迭代数 | 2000 | 触及此预算须拒绝 |
| 优化函数评价数 | 3654 | 10000 |

post-only导出独立重放覆盖六种分支，最大log概率误差5.68e−14；源内和H的提前query读取均被阶段屏障拒绝。能力读取台账复核没有G读取P训练包或E读取pre包。

### 6.2 漏检一：预算触顶头

问题头：`main/f0/vmess/G1/i1/shadowsocks`，F-G，H01，γ=0.0001。

其原坐标梯度约7.013e−7、函数评价3654次、迭代2000次。数值误差门达标不抵消原合同的预算拒绝条件。

旧实现只检验最终梯度、目标/梯度重放与目标下降，没有把`iterations >= 2000`并入拒绝条件，因此错误接受并继续了后续拟合。严格说，本应在这个头停止；后续实际计算仍如实保留并计费，不能据已完成的232拟合倒推“合同已经通过”。

已修正：拟合终验和缓存复用均检查累计迭代/函数预算；触顶保存失败，不自动续跑，不增加Newton步骤、不放宽门、不回退β0。

**没有给问题头追加步骤，也没有覆盖旧passed=true、模型或封存记录。**新增合同审计将其明确判为未获资格。

### 6.3 漏检二：学习率分桶

实际四桶为P 32、P 12、G 22、E 22，每桶都包含两种lr，共88条路径受到调度资格影响。

每个模型有独立参数、梯度、优化器与登记lr，并没有把所有模型错误地使用同一个lr；但批准的调度合同要求同lr分桶，而且当前并发重放只覆盖了单lr夹具。不能将“算式看起来独立”当成完成了缺失的工程验证。

已修正：先按lr分组，再分最多32模型的桶；Engine独立拒绝混合lr/行形状；旧混合桶产物不能被新调度静默复用。新增元数据守卫测试通过。

**修正后的真实调度尚未重放；需要另行登记有限修复/兼容性验收，不能声称P1已经修复完成。**

## 7 保留的其他工程停止记录

1. CUDA cumsum在当前PyTorch确定性模式下不受支持：改用同数学定义的固定三角前缀和。
2. 首次等价实现存在局部变量引用错误：修正后原数学门重放通过。
3. 最初pre初始化期间扩展了调度源码，触发运行期源码封存检查。保留停止；36个已保存初始头只在原数据、原目标、原坐标梯度独立重放通过后复用，没有再次拟合。

以上旧记录及本次两项合同漏检均没有删除。后两项合同漏检决定当前P1整体仍未通过，不能用之前的工程修复成功来覆盖。

## 8 CUDA、实际成本与预算诊断

### 8.1 CUDA证据

动态训练期间整卡利用率采样98%—99%，整卡显存约1.7—1.9GiB。这是局部采样，不是全流程平均或峰值算力证明。

单lr合成90步区间：独立执行20.485秒，Graph执行1.161秒，约17.6倍。它只证明该合成区间的调度加速，不等于完整实验加速17.6倍。

合成32模型形状测试：

| 行数/条件数 | 100步秒数 | PyTorch allocated MiB | reserved MiB |
| --- | ---: | ---: | ---: |
| 192/16 | 1.524 | 548.1 | 784 |
| 352/22 | 2.049 | 1061.1 | 1312 |

这些是合成计时，不是新增外层业务模型；计入活动成本，不计正式路径数。

### 8.2 实际凸头成本

| 类别 | 拟合数 | 总秒数 | 平均秒数 | 最慢秒数 |
| --- | ---: | ---: | ---: | ---: |
| 真实侧初始化 | 72 | 324.29 | 4.50 | 19.59 |
| 静态头 | 72 | 203.82 | 2.83 | 11.62 |
| 动态最终refit | 88 | 949.24 | 10.79 | 47.20 |
| 合计 | 232 | 1477.35 | — | — |

四个动态桶包括Graph准备、诊断及检查点的实际计时分别39.19、16.11、31.77、22.79秒，总计109.85秒。由此可见当前瓶颈主要不是这88条Adam路径，而是逐问题充分求解的凸头。

截至成本封存，累计活动计账约1679.51秒，即28.0分钟，包含失败/工程重放。额外补计19.30秒worker墙钟差额，以保守覆盖未单独计时的加载、缓存重放及开销；其中包括部分IO，不能将该数字称为纯GPU时间。开发、文件hash及CPU汇总不与模型秒混作并行活动时间。

### 8.3 完整范围外推

完整合同上限为18,720条动态路径、37,440,000次逐模型Adam更新、27,960个凸头。不能称为“只有几个小MLP”。

原后端成本诊断按side/arm/γ分层，以中位数给中心外推，以1.25×P90给保守外推；外层因子取至少352/192=1.833，并使用外层配置并集上限，再预留5%重放/预测及一分钟。

| 项目 | 小时 |
| --- | ---: |
| 中心外推 | 61.34 |
| 保守外推 | 116.33 |
| 自动推进门 | 19.2 |
| 活动保护上限 | 24 |

这两个外推值不是运行时间置信区间，也不是承诺。它们包含未获资格头的真实计算成本，基于旧混合桶后端；不能作为修正后后端的通过证明。即使暂不考虑合同漏检，这一量级也不支持原预算内自动推进。

未借此删除SS、缩减候选、挑容易的业务/角色、减少seed、用β0替代pending，或打开query后按分数选范围。

## 9 下一步需要确认什么

建议先登记**仅数值执行修订的有限先导**，再决定是否启动完整范围，而不是直接提高科学模型容量或放宽门限。

需明确的内容为：

- 预算触顶头采用什么重新登记的求解/退出政策；不得从失败终态偷偷追加步骤或把小梯度改称预算通过。
- 单lr分桶修正如何重放，以及旧混合桶路径在何种独立兼容性证据下才可复用。
- 在原模型、损失、数据权限和精度/门限不变的前提下，能否通过凸头执行并行化降低总成本；必须实测，不能承诺与并发数成比例加速。
- 若仍不能压回预算，才请用户决定提高活动上限或预先登记更小但全臂、同权限的范围；不得按query/H分数删选。

本次只修正了工程接口与记录，**没有执行新一轮训练、追加求解、query选择或H评分**。

## 10 结论边界

本次证明了raw训练材料可以可信重建，且投影、条件矩、梯度、独立优化与post-only导出具备局部工程可行性。

本次没有完成新版方案的整体工程资格，也没有任何新增源query/H分类F1、CE或Brier结果。不能判断新方法改善、退化或无效；不能用历史P-small分数填成本轮结果。

后续即便完成完整H评价，也仍是同批历史数据的内部验证，不是外部盲测、未见代理配置、跨日期DIRECT或无索引在线攻击验证。

## 11 核心产物

- [P0封存](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/deproxy-moment-game-v1-20261016/run-01/manifests/P0-complete.json)
- [P0 raw重放审计](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/deproxy-moment-game-v1-20261016/run-01/manifests/raw-package-audit.parquet)
- [嵌套内容隔离审计](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/deproxy-moment-game-v1-20261016/run-01/manifests/P0-nested-fold-audit.json)
- [原232头数值记录，须结合修订审计阅读](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/deproxy-moment-game-v1-20261016/run-01/tests/P1-head-quality.parquet)
- [来源与能力读取审计](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/deproxy-moment-game-v1-20261016/run-01/tests/P1-provenance-audit.json)
- [单lr CUDA合成重放](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/deproxy-moment-game-v1-20261016/run-01/tests/P1-CUDA-01/replay.json)
- [post-only独立重放](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/deproxy-moment-game-v1-20261016/run-01/tests/P1-inference.json)
- [原后端成本诊断](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/deproxy-moment-game-v1-20261016/run-01/manifests/P1-cost-forecast.json)
- [当前合同否决审计](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/deproxy-moment-game-v1-20261016/run-01/tests/P1-contract-gate-audit-02.json)

原`P1-numeric-complete`、`P1-closeout`和`completion.json`中的工程通过字段已被本报告与revision-02明确否决，保留它们是为了审计，不是将其视为仍有效。
