# 代理前后漂移模型的构建原理与实现报告

核对日期：2026-10-02。本文解释已有模型，不提出或执行新训练。依据为当前仓库源码、冻结配置和已完成实验报告，重点说明前向摘要生成器怎样从真实pre/post对应关系学习，以及它如何演变为最新多部署实验中的增广模型。

## 一 核心答案

我们的前向代理漂移模型可以概括为：

> 在训练区真实pre/post摘要对上，用小型Ridge学习“入口摘要对应的出口摘要中心”；用留一内容预测得到整向量残差池；为新的训练pre抽取一个完整残差向量，与预测中心相加，再通过固定解码器还原为post风格摘要。

其统一表达为：

\[
\widehat z_B(a)=\phi(a)+g_\Theta(a),\qquad
\widetilde b=\operatorname{Decode}\left(\widehat z_B(a)+\varepsilon_J;F_a\right).
\]

其中，\(a\) 是pre摘要，\(b\) 是post摘要，\(\phi\) 是该版本的编码，\(g_\Theta\) 是学习到的漂移中心，\(\varepsilon_J\) 是某一训练残差的完整六维向量。只有连接汇聚T版本使用查询pre的固定连接数 \(F_a\)；窗口W版本没有F参数。

这里没有GAN、VAE、扩散模型或用于生成的MLP，也没有生成PCAP、包序列、TLS记录或可重放的协议会话。**MLP是后续业务分类器，Ridge加经验残差才是漂移生成器。**

目前最准确的方法名是“基于真实配对、内容交叉拟合残差和必要摘要约束的前向特征增广”。它拟合观测到的部署相关统计变换，不是从协议源码推导出来的精确封装公式。

## 二 不要混淆的两条研究路线

| 路线 | 方向 | 输入输出 | 目的 | 与本报告的关系 |
|---|---|---|---|---|
| 早期源分类器校准 | post→pre | 原157维统计，源侧149个有效坐标 | 保留pre分类器，让post经校准后复用它 | 独立历史路线，不是下面生成器的逆函数 |
| 后来的前向漂移增广 | pre→post风格摘要 | 生成六个计数摘要量，T另保留F | 扩充post业务分类器的训练表示 | 本报告主体 |

旧反向路线最初是逐特征一维Ridge，后续加入固定源模型的决策保持目标。前向路线则直接重新拟合pre→post，而且每个输出可使用全部pre输入维度，**不是将旧逐维回归器求逆**，也不含旧源分类器的logit保持损失。

对应历史说明见 [源分类器跨侧迁移](0916-source-classifier-cross-side-transfer-results.md) 与 [决策感知校准](0916-source-decision-aware-calibration-results.md)。前向模型由配对观测提供回归目标；其下游分类器依然使用业务标签，两条监督来源需分别说明。

## 三 模型版本与观测口径

| 版本 | 观测 | 生成坐标 | 核心变化 |
|---|---|---|---|
| 早期条件漂移 | 0916 SS/VLESS连接汇聚，六量加F | 六个原始量的log1p | 条件中心加整向量OOF残差，非法候选拒绝重抽 |
| 可行摘要版本 | 同类连接汇聚T，六量加F | 段总数、方向差、事件余量、字节余量 | 从输出构造保证已登记必要约束 |
| Hy2窗口W版本 | 访问窗口的观测载荷六量 | 全局段数及有界字节余量 | 适应共享carrier，不套用内层连接F |
| Extend v3 | 五部署W与四部署T分别实验 | 分别复用W/T编码器 | 新数据和角色适配，不把W/T数值含义混同 |
| 最新多部署评价 | 五部署共同W六量 | 复用W编码器与Ridge | 改为全局内容划分、强post混合基线及留一部署 |

### T口径

\[
a=(U_\uparrow,U_\downarrow,E_\uparrow,E_\downarrow,R_\uparrow,R_\downarrow),\quad F.
\]

- U：合格连接的观测唯一TCP字节，重传不重复增加相同序列字节。
- E：正新字节事件数，不是全部TCP包数。
- R：先在各连接的新字节时间线上计算零阈值方向段，再按方向汇总。
- F：同次访问共同合格连接数，保留查询pre的F，不生成、不复制donor post的F。

pre/post采用相同合格连接集合，因此F含有既有双侧资格审核基础。它不是已被证明可以无索引在线独立获得的变量。R也不是原始论文定义的FR；当前模型没有直接加入旧FR列、归一化FR或157维特征组。

### W口径

\[
a=(W_\uparrow,W_\downarrow,P_\uparrow,P_\downarrow,R_\uparrow,R_\downarrow).
\]

W为访问窗口内正TCP/UDP传输载荷字节，P为正载荷事件数，R为该窗口合并事件序列的方向段数。实际重传等观测可以保留，不能称为唯一应用字节。所有连接/载体事件汇在一条有序时间线上，因此上下行段数最多差一。

W不加入内层连接数、carrier数或协议身份作为生成器数值输入。W最初用于Hy2共享carrier问题，后来用于Extend的共同观测；这不意味着所有协议具有相同封装机制。

两种R尤其不同：T是各连接段数之和，方向差可到F；W是一条合并序列的段数，方向差至多1。W不是“将T的F直接设为1”。

## 四 训练样本如何形成

基本训练单元不是“一个pre包对应一个post包”，而是**同一登记访问两侧经过资格筛选和汇聚的摘要对**：

\[
\mathcal D_c=\{(a_i,b_i,F_i,u_i)\}_{i=1}^{n_c}.
\]

\(c\) 标识实际部署，\(u_i\) 为内容分组，F只在T存在。配对身份来自历史流量关联与访问台账，不是模型通过SNI或长度相似性自行猜出的对应。

按部署分别拟合，不让一个映射把不同部署混在一起。内容ID、访问ID、重复号和部署名可用于配对、分折和审计，但不进入数值回归向量。生成器没有业务类别embedding，也没有显式业务标签损失；业务标签由生成后样本继承给下游分类器。

这只是说明生成器的数值拟合不读业务标签，不能把整个流程称为无监督：内容分组、配对关系和下游业务标签都是所使用的监督或辅助信息。

## 五 Ridge条件中心的实际数学形式

以当前可行T/W版本为例，定义：

\[
q_i=\begin{cases}
[\log(1+a_i),\log(1+F_i)],&T,\\
\log(1+a_i),&W.
\end{cases}
\]

只在当前允许的拟合集合计算输入均值 \(\mu_q\)、总体标准差 \(\sigma_q\)，并计算pre编码 \(z_{A,i}=\phi(a_i)\) 的总体标准差 \(s_z\)。小于 \(10^{-10}\) 的尺度设为1。没有使用测试均值方差，也没有用真实post目标的标准差替代pre编码尺度。

令设计矩阵第i行为：

\[
x_i=\left[\frac{q_i-\mu_q}{\sigma_q},1\right],
\qquad
y_i=\frac{z_{B,i}-z_{A,i}}{s_z}.
\]

优化目标为：

\[
\min_\Theta\frac1n\lVert X\Theta-Y\rVert_F^2+
\alpha\lVert\Theta_{\mathrm{nonbias}}\rVert_F^2,
\qquad \alpha=1.
\]

末行截距不惩罚。实现直接解线性方程：

\[
\left(\frac{X^\top X}{n}+\alpha P\right)\Theta
=\frac{X^\top Y}{n},\qquad
P=\operatorname{diag}(1,\ldots,1,0).
\]

源码使用 `torch.linalg.solve`，不是默认参数的sklearn Ridge，也不是梯度下降训练这个生成器。目标除以样本数，因此若拿其他软件复现，必须对齐正则尺度；不能把“alpha同为1”直接当作相同目标。

预测为：

\[
\widehat z_B(a)=\phi(a)+[x(a)\Theta]\odot s_z.
\]

也就是“保留pre编码作为基准，加上回归预测的漂移”。Ridge学的不是原始post字节数本身，而是经过尺度处理的编码差。

### 模型容量

| 模型 | 输入数 | 输出数 | 含截距回归系数 |
|---|---:|---:|---:|
| 原log漂移与可行T | 7 | 6 | 8×6=48 |
| W | 6 | 6 | 7×6=42 |

这只是回归系数数量，不含均值、尺度和经验残差池存储。每个输出可依赖全部输入，不是逐维仿射；但平方目标可按输出分解，并没有显式学习完整协方差矩阵或输出协方差损失。

“线性模型”也只针对上述标准化输入与漂移目标而言：外面存在log、asinh、logit、整数化及边界解码，整个原始计数空间的生成映射并不是线性的。

实现依据：[可行T模型](../src/proxy_analysis/feasible_summary_calibration/model.py)、[W模型](../eval/hy2_carrier_calibration/window_model.py)。

## 六 第一代为什么使用log漂移及它的局限

第一代设 \(\phi(a)=\log(1+a)\)，学习：

\[
\Delta_i=\log(1+b_i)-\log(1+a_i).
\]

大字节量下，它近似相对倍率的对数；小值和零值下则不等于严格log-ratio。固定漂移也不是固定字节附加量，更不是协议头部长度K。

当时输入为 \([\log(1+a),\log(1+F)]\)，输出漂移用输入前六维的标准差缩放，而不是后来独立计算的pre latent尺度。改变坐标后虽然仍有48系数和alpha=1，实际优化几何已经变化。

第一代解码先expm1，再四舍六入五成双式的最近整数舍入 `np.rint`，检查：

\[
0\le R_d\le E_d\le U_d,\quad
R_\uparrow+R_\downarrow\ge F,\quad
\lvert R_\uparrow-R_\downarrow\rvert\le F,
\]

以及零方向一致性、整数和溢出规则。随机臂最多32次重抽，仍失败则显式回退原pre；不把fallback标志交给分类器。初次非法率10%、最终fallback率1%为当时冻结门限。

这一机制在早期F0–F10任务执行完成；但后续“新增业务完全无训练post”的更严格实验中，60个合法性单元有8个超过首次非法率门限，均在VLESS，分类因此停止。主要越界是上行R>E，不能因最终重抽后全部合法就说原候选分布合格。

根本问题是：一个残差在donor附近合法，不代表加到另一个query中心后仍满足联合计数关系。完整向量抽样保留了donor内部依赖，却不保证平移后的必要可行域。因此后续改的是输出参数化，而不只是扩大回归器。

原实现见 [conditional_drift/model.py](../src/proxy_analysis/conditional_drift/model.py)、[generate.py](../src/proxy_analysis/conditional_drift/generate.py)，失败证据见 [跨业务完整报告](cross-business-calibration-0916/complete-report.md)。

## 七 可行T坐标如何构造

定义：

\[
N=R_\uparrow+R_\downarrow,\quad
D=R_\uparrow-R_\downarrow,\quad
G_d=E_d-R_d,\quad H_d=U_d-E_d.
\]

于是六维编码为：

\[
\phi_T(a)=\left[
\log(N+\tfrac12),\operatorname{asinh}(D),
\log(G_\uparrow+\tfrac12),\log(G_\downarrow+\tfrac12),
\log(H_\uparrow+\tfrac12),\log(H_\downarrow+\tfrac12)
\right].
\]

正数余量使用log压缩，D可正可负所以用asinh。半整数偏移使零余量也有有限编码，并与floor-exp整数解码配套。

给定生成的latent \(z\) 和查询F，执行：

1. \(N_0=\lfloor\exp(z_N)\rfloor\)，\(N=\max(F,N_0)\)。
2. 定义最大合法方向差 \(B=F-((F-N)\bmod2)\)，保证与N同奇偶。
3. 将 \(z_D\) 限制在 \([-\operatorname{asinh}B,\operatorname{asinh}B]\)，经sinh后取 \(-B,-B+2,\ldots,B\) 中的合法整数格点D。
4. \(R_\uparrow=(N+D)/2\)，\(R_\downarrow=(N-D)/2\)。
5. \(G_d=\lfloor e^{z_{G_d}}\rfloor\)，\(H_d=\lfloor e^{z_{H_d}}\rfloor\)，非零方向 \(E_d=R_d+G_d\)、\(U_d=E_d+H_d\)。
6. 若 \(R_d=0\)，该方向E和U联动为0，记录被忽略的余量。

计数超过精确整数范围 \(2^{53}-1\) 或数值非有限时立即停止，不静默裁剪溢出，不重抽、不fallback。每次donor抽取对应一次固定解码。

这是**带明确边界映射的支持保持构造**，不是“从头到尾无裁剪、无投影”：N下界、D边界、奇偶格点和零方向联动确实会改变latent样本，必须记录其作用。保证的仅是当前登记的必要摘要约束，不保证存在真实TCP会话实现这些总量。

更换坐标同时更改目标、误差尺度和解码行为，不能把最终收益唯一归因于“去掉非法候选”。旧失败版本没有对应分类结果，也不能声称它在业务上被新版本直接击败。

详见 [可行摘要实验](feasible-summary-calibration-0916/summary.md)。

## 八 当前W坐标与T有什么不同

W的必要关系为：

\[
0\le R_d\le P_d\le W_d\le LP_d,\quad
N\ge1,\quad\lvert D\rvert\le1,\quad L=65527.
\]

L是本口径采用的非jumbo传输payload保守计数上界，不是实际MTU，也不是协议精确开销。

令：

\[
G_d=P_d-R_d,\quad H_d=W_d-P_d,\quad M_d=(L-1)P_d.
\]

编码为：

\[
\phi_W(a)=\left[
\log(N-\tfrac12),\operatorname{asinh}(D),
\log(G_\uparrow+\tfrac12),\log(G_\downarrow+\tfrac12),
\log\frac{H_\uparrow+\tfrac12}{M_\uparrow-H_\uparrow+\tfrac12},
\log\frac{H_\downarrow+\tfrac12}{M_\downarrow-H_\downarrow+\tfrac12}
\right].
\]

与T相比，两处关键差别是：N使用 \(N-1/2\)，字节余量使用有界logit式编码，而不再是无上界的log H。

解码过程：

\[
N=1+\lfloor e^{z_N}\rfloor.
\]

N为偶数时D只能是0，N为奇数时D只能是−1或1；用固定的边界与格点规则取得D，再计算两方向R。之后：

\[
P_d=R_d+\lfloor e^{z_{G_d}}\rfloor,
\]

\[
H_d=\min\left(M_d,\left\lfloor(M_d+1)\sigma(z_{H_d})\right\rfloor\right),\qquad W_d=P_d+H_d.
\]

零R方向依然联动P/W为零。sigmoid端点有限精度、方向边界及零方向作用分别记录。W的整数容量检查比最终 \(2^{53}-1\) 上界还包含乘L前的保守检查，溢出停止。

对合法观测摘要，编码后解码在已执行观测与边界测试中精确还原；这并不意味着任意latent下无失真。尤其N为偶数时方向差必须归零，方向边界操作频繁并不自动代表算法报错。

当前最新实验生成的172800条视图中，每种方法57600条；direction_bound计数为paired 31404、group 32158、cyclic 32441。这是已定义解码的作用次数，不是首次非法率或拒绝率，也不能据此证明真实性。

来源：[W编码器](../eval/hy2_carrier_calibration/window_model.py)、[Hy2窗口报告](hy2-window-calibration-0916/summary.md)、[最新正式报告](business-protocol-eval-extend/formal-results.md)。

## 九 随机性从哪里来

单独的Ridge只给出一个确定性中心。为表示相同pre附近仍可能存在的post变化，我们构建经验残差池，不使用高斯噪声假设。

对每个校准内容u：

1. 删除该内容所有重复及双侧样本。
2. 在其他校准内容上重新拟合输入均值、输入尺度、pre latent尺度及Ridge。
3. 预测被删除内容的pre。
4. 保存其目标latent减去留一预测的残差。

公式为：

\[
\varepsilon_i=\phi(b_i)-\widehat z_B^{(-u_i)}(a_i).
\]

这称为leave-one-content-out，简称LOCO。残差形成时，该内容未参加对应模型拟合；它不是最终全C模型的训练内残差。使用完整C再拟合的主模型为查询提供中心，使用LOCO池提供随机扰动。

预测结果已经回到共同latent坐标，所以不同LOCO模型虽有各自标准化参数，其残差可以在同一编码坐标下汇合。不能直接混合不同fold未还原尺度的标准化误差。

抽样时一次抽取一整行六维残差：

\[
\widetilde z_B(a)=\widehat z_B(a)+
(\varepsilon_{J,1},\ldots,\varepsilon_{J,6}).
\]

不是六列分别找六个donor。这样保留训练残差向量中方向、事件和字节之间的联合变化，但不能保证在新的a上仍具有正确条件协方差。LOCO残差也可能带有模型偏差，不是纯粹“网络随机噪声”。

残差池没有额外强制均值归零。因此 \(\widehat z_B(a)\) 更准确地称为回归中心；加上经验残差、再经过非线性解码后的样本均值，不必等于解码后的该中心。

### 各版本的donor选择

| 版本 | 候选池 | 抽样规则 |
|---|---|---|
| 第一代18内容校准 | 18个内容×4重复 | 条件随机臂在训练pre标准化空间取最近8个内容，再抽内容内donor |
| 跨业务T六内容校准 | 6个内容×4重复 | 六个内容全部可选；虽按距离排序，仍均匀选全部六个，不是局部近邻过滤 |
| Extend W六内容校准 | paired/cyclic 24行，group 96行 | 直接均匀抽池中整行 |
| 最新多部署W交叉生成 | paired/cyclic 72行，group 288行 | 每任务每seed固定RNG直接均匀抽整行 |

所以，最新模型是“输入条件化的中心，加固定经验联合残差池，并经输入相关解码”，不是已学习任意 \(p(B\mid A=a)\) 的灵活概率模型。早期近邻描述不能直接套到最新W实现上。

## 十 真配错配与内容组控制如何构造

### 真配 paired

对同一部署、同次访问：

\[
a_{u,r}\longrightarrow z_{u,r}=\phi(b_{u,r}).
\]

既用此目标拟合中心，也用此对应计算LOCO残差。真实对应不是只用于保存文件名，而是直接决定训练目标和残差。

### 循环错配 cyclic

同一内容的pre仍对应同一内容的post，但重复号循环替换：旧0916为1→2→4→5→1，Extend及最新实验为1→2→3→4→1。

中心与残差都针对错配目标重新拟合，不能拿真配模型再临时换一个残差就称同机制错配。它保留部署、业务和内容，仅打破同次访问身份；因此不是“不同业务负例”，也不是从独立条件分布重新采样。

### 内容组 group

只知道两侧属于同内容、同部署，不知道四个pre分别对应哪个post。生成worker中删除session、重复号、时间、连接ID及post F，两侧独立规范排序。

对每个pre的中心训练目标是：

\[
\bar z_{B,u}=\frac14\sum_{s=1}^{4}\phi(b_{u,s}).
\]

注意是**先编码，再平均**，不是 \(\phi(\frac14\sum_s b_{u,s})\)。由于非线性，两者通常不同。

对被LOCO留出的内容，生成全部4×4组合残差：

\[
\varepsilon_{u,r,s}=\phi(b_{u,s})-
\widehat z_{B,\mathrm{group}}^{(-u)}(a_{u,r}).
\]

六内容时池96行，18内容时288行，但仍只来自每内容四次真实重复，不是多了四倍独立数据。group不使用真配残差池。

平方目标满足：

\[
\frac14\sum_s\lVert f(a_{u,r})-z_{u,s}\rVert^2
=\lVert f(a_{u,r})-\bar z_u\rVert^2+
\frac14\sum_s\lVert z_{u,s}-\bar z_u\rVert^2.
\]

后一项与模型参数无关，因此在相同归一化和正则下，组中心目标等价于组内完整Cartesian平均平方损失；工程测试在新坐标重新核验了这一点。它不等价于给每个输入只分配一个循环donor的cyclic。

实现来源：[可行T的fit](../src/proxy_analysis/feasible_summary_calibration/model.py)、[Extend拟合与采样](../eval/extend_calibration/formal_generate.py)、[最新W拟合与采样](../eval/business_protocol_eval/generation.py)。

## 十一 简单漂移对照具体做什么

| 臂 | 生成latent | 是否需要真实配对信息 |
|---|---|---|
| raw | 不变换，使用原pre | 不拟合漂移 |
| center | \(\phi(a)+\operatorname{median}_i[\phi(b_i)-\phi(a_i)]\) | 是 |
| marginal | \(\phi(a)+[\phi(b_J)-\phi(a_J)]\) | 是 |
| paired | \(\widehat z_B(a)+\varepsilon_J\) | 是 |
| cyclic | 错配中心加错配LOCO残差 | 使用同内容及重复置换关系 |
| group | 组目标中心加Cartesian LOCO残差 | 只需内容组关系 |
| reference | 直接用额外真实post | 使用额外目标侧资源 |

center的中位数逐维计算，marginal则抽完整漂移向量。**marginal抽的是总漂移，paired抽的是扣除条件中心后的残差，二者不是同一个池。**

center/marginal也依赖真实漂移，不能因为它们偶尔高于paired，就据此得出“配对不重要”。那说明当前条件中心加残差未必比简单真实漂移更有用。固定latent中心也不对应从post删掉一个固定字节前缀。

最新多部署实验只保留M0/M1以及paired/group/cyclic三种生成方案，没有重新运行center/marginal；不可将旧分数挪作本轮对照。

## 十二 分类训练与生成器如何衔接

生成器的训练目标不含业务分类损失。生成完成后，摘要还原为原数值空间，沿用来源pre已有业务标签交给MLP。donor身份、latent坐标、fallback或边界标志不作为分类器额外特征。

```text
允许的真实pre/post配对
        │
        ├─ 拟合pre输入尺度与latent漂移Ridge ── 条件中心
        │
        └─ 按内容LOCO重新拟合 ─────────── 完整残差池
                                             │
额外训练pre ── 编码/条件中心 ── 加整行残差 ── 固定合法域解码
                                             │
                                   合成post风格摘要 + 原标签
                                             │
                                      业务MLP训练
                                             │
真实测试post ── 冻结分类预处理 ─────────────── 业务预测
```

测试时分类器只用真实post，不需要测试pre，也不需要给测试样本查询生成器。旧第一代曾额外使用测试pre进行离线生成质量评价，但该分支与分类训练/推理分离，不能把它误写成攻击推理所需输入。

| 项目 | 跨业务T | Extend W跨业务 | 最新多部署W |
|---|---|---|---|
| MLP输入 | 六量加固定F，共7维 | 六维 | 六维 |
| MLP结构 | 7→32→6 | 6→32→6 | 6→32→6 |
| 参数 | 454 | 422 | 422 |
| 分类缩放来源 | C_pre | C_pre | 全部允许训练真实post |
| 真实post资源 | C_post，U_post禁止 | C_post，U_post禁止 | 所有源部署六类训练post可用 |
| 主问题 | 缺post业务增广 | 缺post业务增广 | 已见覆盖及拟合期留部署 |

生成器pre尺度与分类器尺度是两套不同用途的参数。最新分类尺度来自训练post，并不改变生成器仍从其拟合pre估计尺度的事实。

MLP采用固定Adam、1000步、lr=0.001、权重L2，没有端到端反向更新Ridge或按业务结果优化残差池。生成器未因某业务测试失误而重拟合。

## 十三 两种主要权限设计

### 跨业务校准预算实验

每部署每折训练24内容96访问，分为C的6内容24配对访问与U的18内容72个pre访问。C只来自四个辅助业务，两个目标业务在C没有post；U含目标业务32次以及辅助业务40次。

生成器只拟合C，为U_pre生成八视图，U_post从受限训练流程隔离。H是留出六内容24访问，H_post只用于冻结推理；真实U_post只在独立reference权限下开放。每个生成方法一次全C拟合加六次LOCO，共7次Ridge。

这是学习权限模拟。既有双侧资格整理仍曾读取两侧数据，不能推断现实采集流程已经无需U_post。

### 最新多部署实验

E1每外折有24训练内容，每部署96访问。将训练内容固定分成四个内部生成组：

- 查询组：6内容24访问。
- 生成器拟合：另外18内容72访问。
- 其残差LOCO：每次17内容68访问。
- 每查询访问八视图；最终覆盖每部署全部96个训练访问。

五外折×五源部署×四组=100生成任务；每任务三方法，各1+18次拟合，共5700次。拟合不因seed重复，三seed只改变随机抽样与后续分类训练。

E2留一个目标部署，分类预处理和模型只拟合其余四部署；生成缓存也只能读取这四源，且查询/拟合成员都须在该场景训练区。目标pre不参与查询，目标post不参与尺度或残差选择；所有源部署的测试内容也不能参加训练。

这轮改变了资源设置，不再限制目标业务post缺失，因此不能要求结果必然重现旧F1_new大增益。

## 十四 一个已保存生成器的实物检查

本次只读检查了最新 `vless-f0-q0/paired` 的已保存模型，没有重新拟合：

| 项目 | 实际记录 |
|---|---|
| 输入mean、scale | 各6维 |
| pre latent zscale | 6维 |
| weight | 7×6，42系数 |
| 正规方程最大绝对残差 | 2.220446049250313×10^-16 |
| 残差池 | 72×6 |
| 一个seed的视图张量 | 24×8×6 |

同一查询的前两个已保存视图，按W_up、W_down、P_up、P_down、R_up、R_down排列，分别是：

```text
[452352, 30277253, 2830, 20753, 2375, 2375]
[468063, 30545997, 1475, 21183, 1174, 1175]
```

两者来自同一个预测中心和不同donor残差，经相同W解码得到。第一个全局方向段差为0，第二个为−1，都满足必要W关系。这个例子只展示实际存储形式及随机视图差异，不证明两个视图对应真实可执行会话，也不是挑选“最接近真实post”的样本。

小的正规方程残差只验证数值求解，不是生成误差小、业务有效或无泄漏的证明。

## 十五 历次结果对模型提供了什么证据

| 实验 | 主要观察 | 可支持的范围 |
|---|---|---|
| 第一代条件前向漂移 | 有部署相关业务用途，但T4对错配T5的F1增益未稳定建立 | 摘要适配可有用途，不足以证明精确配对普遍额外有效 |
| 旧跨业务log版本 | VLESS部分单元超过合法性门，未分类 | 暴露联合约束缺陷，不是分类负结果 |
| 0916可行T | SS paired F1_new=0.9610，VLESS=0.7478；相对raw及group均通过预定双增量 | 该缺post任务内的正向业务证据 |
| 0916 Hy2窗口W | paired F1_new=0.6126，group=0.6014；二者调整区间跨零 | 变换优于raw，但精确身份相对group未确立额外收益 |
| Extend v3 W/T | 五W、四T部署各自全部通过预定paired−raw及paired−group | 新数据上登记的同部署缺post实验，不是未见部署结论 |
| 最新五部署W | E1 M2=0.7248、M0=0.7159；E2 M2=0.6097、M0=0.6061 | 相对group有证据，超过强post基线尚未确立 |

这些终点不能直接横向排名：历史F1_new针对缺post目标业务，Hy2是五业务，最新是完整六类协议等权F1。数据批次、真实post资源、观测和分类尺度也不完全相同。

因此，既不能将旧成功说成任何监督设置下都会获益，也不能用最新增益不显著推翻旧缺post任务。模型的实用性要与训练资源条件绑定。

## 十六 当前模型的明确限制

1. **不是精确协议开销模型。** 漂移可同时包含封装、分段、重传、捕获窗口、业务加载和网络环境变化，未分离协议标准的因果作用。
2. **不是完整流量生成器。** 满足计数必要条件不保证时序、连接结构、TLS语法或应用语义存在一致实现。
3. **低容量中心加有限经验池。** Ridge可能欠拟合；LOCO残差包含模型误差，均匀池也不学习任意输入相关方差。
4. **保留联合残差不等于条件联合分布正确。** 输出尺度改变、边界映射和零方向处理还会影响生成分布。
5. **没有源域支持范围之外的自动保证。** 新业务、新负载或新部署可能需要无法从现有C外推的结构；当前不按测试结果自适应修正。
6. **标签继承只是训练构造。** 生成摘要被赋予源标签，不代表每个样本已被证明语义保持。
7. **八视图不增加独立内容。** 不能把生成样本数或seed当作真实独立样本量，也不能用全部视图估计外部泛化置信度。
8. **分组控制不是无信息控制。** group知道内容关系，cyclic保留内容；它们检验特定对应层级，不代表所有无配对方法。
9. **部署划分不等于协议因果分解。** 最新E2是拟合期留部署；历史已分析目标数据，不是研究者全盲外部测试。
10. **元数据不入数值模型不等于研究不用元数据。** 采集关联、内容标签和资格审核依赖台账；离线索引辅助边界仍存在。

## 十七 代码与产物导航

| 内容 | 入口 |
|---|---|
| 原log漂移回归与解码 | [conditional_drift/model.py](../src/proxy_analysis/conditional_drift/model.py) |
| 原近邻残差、拒绝与fallback | [conditional_drift/generate.py](../src/proxy_analysis/conditional_drift/generate.py) |
| T可行编码、解码、Ridge、三种对应 | [feasible_summary_calibration/model.py](../src/proxy_analysis/feasible_summary_calibration/model.py) |
| T生成流程与边界审计 | [feasible_summary_calibration/run.py](../eval/feasible_summary_calibration/run.py) |
| W编码与CUDA Ridge | [window_model.py](../eval/hy2_carrier_calibration/window_model.py) |
| Extend W/T生成适配 | [formal_generate.py](../eval/extend_calibration/formal_generate.py) |
| 最新内容交叉拟合、池和抽样 | [business_protocol_eval/generation.py](../eval/business_protocol_eval/generation.py) |
| 最新生成、分类与预测封存 | [business_protocol_eval/run.py](../eval/business_protocol_eval/run.py) |
| 最新小MLP与训练日程 | [business_protocol_eval/learning.py](../eval/business_protocol_eval/learning.py) |
| Extend权限、参数与指标完整说明 | [v3实验契约](extend-calibration-20260930/v3-experiment-contract.md) |
| 最新正式结果与统计范围 | [多部署正式报告](business-protocol-eval-extend/formal-results.md) |

最新已保存实例位于 `outputs/business-protocol-eval-extend/run-01/generation/vless-f0-q0/paired/`，包含 `model.pt`、`residual-pool.npy`、`loco.json`、各seed的samples、decoder-effects和完成哈希。文件位于本地忽略的outputs目录，不在Git源码链接中附带大模型或数据。

本次仅增加方法报告，没有修改模型、阈值、训练数据、冻结合同或历史结果。最终应记住的区别是：**配对关系决定我们如何估计漂移，合法域决定生成结果必须满足哪些计数关系，而业务分类结果才决定这种合成在特定监督条件下是否有用。三者不能相互替代。**
