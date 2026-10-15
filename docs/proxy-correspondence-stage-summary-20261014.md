# 代理前后关联研究阶段性总结

截至2026年10月14日。范围为ProxyAnalysis当前已实施的代理前后测量、对应关系诊断、表示学习、校准增广、概率漂移、业务迁移和动态约束实验，以及未通过资格的观测与数值分支。未执行的计划不作为实验结果；原始数据、历史模型、区间和停止记录均保持不变。

## 1 阶段结论

当前研究不能概括为“所有配对学习都成功”，也不能概括为“代理关联对分类无用”。最有证据支持的是：**代理边界两侧存在可重复、可预测的对应结构；这些结构有条件地改善测量、校准和训练增广，但其业务用途取决于表示、监督资源、对应层级、部署与观测范围。**

已获得四类实质成果。

1. **测量与数据工程。** 建立不依赖Wireshark内置派生特征的包、连接、访问及共享carrier分析链，形成两侧特征、严格配对、URL/host对齐、唯一TCP字节、新字节事件、记录语法和独立时间观测。
2. **对应关系确有预测价值。** 0914真实配对变换的部署预测优于同内容错配；Extend连接级真配概率核在内容外预测上优于出口边际和匿名内容组核。对应不只是“多观测一侧”，但这些结果本身不是业务收益。
3. **业务正结果已经出现。** 小MLP在特定YouTube跨部署任务中利用真实pre教师获益；源分类器经配对校准能够部分跨侧复用；0916可行摘要增广和Extend v3在目标业务没有训练post时通过各自paired−raw、paired−group双主比较。后期P-small又在辅助业务校准迁移中可靠超过CORAL强post参照。
4. **利用边界也已被系统检验。** 多轮VICReg、可靠性辅助目标、机制条件编码、任务感知蒸馏、核正则、状态风险及动态幅度学习，没有建立普遍超越充分post监督或固定P-small的新增收益。完整块硬不变保护没有获得最终资格。

最新资格启用与固定回退实验完整结束：QP的F1_U为79.3841%，相对S提高2.1133个百分点并通过七项家族校正；相对P-small的79.6931%低0.3090个百分点，未建立增量。按预登记规则，当前十维动态幅度候选结项，保留P-small，不默认继续增加步数或搜索权重。

这些结论来自已反复分析的固定队列。模型数、连接数、重复次数、合成视图数和bootstrap次数不增加独立内容数；内容级条件区间不是独立外部验证。

## 2 数据集与实际实验队列

### 2.1 数据库存

| 数据集或批次 | 原始选定访问 | 内容与重复 | 部署 | 实际用途 |
| --- | ---: | --- | --- | --- |
| TrafficTracer-Protocol-Datasets-raw | 192 | 64顶层URL、50站点组；每部署一次 | SS、VLESS、Hy2 | 最初特征提取、页面/资源对齐、统计与三部署识别 |
| TrafficTracer-Detailed-5Reps | 270 | 18登记URL，每部署五次；另有5次历史尝试 | SS、VLESS、Hy2 | MAD/IQR、ICC、变换分离和跨URL一致性；部分主分析只有12个有效URL |
| TrafficTracer-Datasets-20260914 broad | 192 | 64URL、50domain，每部署一次；194存储尝试 | SS、VLESS、Hy2 | 同配置批次广域统计、部署识别；不是64类未见内容识别 |
| TrafficTracer-Datasets-20260914 repeat | 270 | 18URL，每部署五次 | SS、VLESS、Hy2 | 14目标严格队列、配对价值与十四类闭集业务目标识别 |
| TrafficTracer-content-generalization-20260916 | 525 | 七业务、35内容，每部署五次；538存储尝试 | SS、VLESS、Hy2 | 跨内容业务、教师/SSL、校准、记录表示及摘要增广 |
| extend Broad 64URL | 384 | 64目标、六部署、一次；387尝试 | 六部署 | 64URL资格尝试，未完成分类 |
| extend Detailed 18URL | 540 | 18目标、六部署、五次；543尝试 | 六部署 | 扩展库存，未进入当前未见内容主分类 |
| extend Content Generalization | 1050 | 七业务、35内容、六部署、五次；1066尝试 | SS、VLESS、Trojan、VMess、AnyTLS、Hy2 | 后期主要实验来源 |

extend对应目录分别为TrafficTracer-Broad-64URL-6Protocols-R1-20260926、TrafficTracer-Detailed-18URL-6Protocols-R5-20260927和TrafficTracer-Content-Generalization-35-6Protocols-R5-20260927。latest-three-20260929-metadata属于元数据证据来源，不作为额外完整采集批次增加样本量。

0914 broad与repeat、不同批次之间存在目标重叠，不能把URL数直接相加成独立内容数。旧raw与Detailed、0914、0916、extend也不是同一配置下的可任意混合训练库；主要实验始终使用各自冻结队列。

### 2.2 常用模型队列

| 队列 | 规模 | 主要划分 | 结论范围 |
| --- | --- | --- | --- |
| 早期信息关系主队列 | 10URL×SS/VLESS×五次＝100访问 | 留URL与留轮次 | 双侧部署结构和恢复诊断 |
| 0914严格队列 | 14目标×两部署×五次＝140访问 | 部署研究留URL；十四类业务研究留轮次 | 后者是一类一固定目标，不是未见内容泛化 |
| 0916六业务候选 | 30内容×两部署×五次＝300访问 | 候选特征表 | 不等于300全部批准训练 |
| 0916主队列 | 30内容×两部署×四次＝240访问 | 五折全局内容留出 | 训练已见SS/VLESS；重复1/2/4/5 |
| 0916保守敏感性 | 299访问 | 内容留出 | 与240重叠；不是第二份独立复现数据 |
| 0916记录业务 | VLESS 120访问、30内容、1179连接对 | 原内容五折 | 同部署未见内容；共同可解析flow集合 |
| 0916 Hy2窗口实验 | 100访问、25内容、五业务 | 原内容五折 | 外部会话窗口观测，不是完整闭合carrier转换 |
| Extend W | 五部署×120＝600访问、30内容 | 全局内容五折 | 窗口六量；AnyTLS适用、Hy2未进入分类 |
| Extend T与96维主队列 | 四部署×120＝480访问、30内容、23566连接对 | 全局内容五折 | 排他共同有效TCP；AnyTLS/Hy2不适用 |

Extend主队列固定重复1至4；第五次采集不是被判无效，而是没有进入登记四重复预算。部分后期旧报告文字沿用了0916的“1/2/4/5”，本总结采用Extend成员与后续契约确认的1至4，不将文字笔误当成新采样规则。

### 2.3 业务标签与排除依据

正式六业务采用domain × activity：Bing搜索结果、MDN文档、GitHub仓库、Wikipedia文章、YouTube搜索结果、YouTube视频播放。每业务五内容。YouTube播放与搜索提供同域不同活动对照；其他多数domain只有一种活动，分类可能利用站点模板，不能称平台无关纯语义识别。MDN是开发文档网站，不是混合密度网络。

视频标签沿用用户确认：存在正片播放即可，不把未完成配置播放时长或degraded自动解释为标签无效。Bilibili已接受播放确认，但0916主目标75次均DIRECT；Extend本批150次主文档DIRECT，媒体候选没有确认proxy。因此不进入代理业务主队列，原因是路由，不是否认播放。

0914 Vimeo首页与固定视频简介页不能改标为正式视频播放。0914 YouTube只有一个登记内容，重复访问不能制造未见视频泛化。0916唯一暂未纳入299的MDN恢复访问保留其HTTP200及恢复状态，不宣称已证实业务失败。

Hy2的排除须按批次解释：旧批次共享UDP载体及部分业务DIRECT/路由差异；Extend的175次Content访问归于同一登记carrier/adapter，有跨内容复用证据，故当前measurement-only。不能借旧原因替代本批证据。AnyTLS适用于W窗口，不获得排他TCP的T资格。

### 2.4 W与T不是只差重传处理

Extend W有600访问，T有480；共同四部署父访问身份、内容、重复、折和角色一致，但流量范围不同。T候选23660对、共同有效23566对，约99.60%是相对选中候选连接的保留率，不是整个网页流量保留率。共同T成员的下行观测W字节只占全部选中W下行约16%–31%。

因此W/T分数差异同时涉及单位与纳入范围，不能归因于“只做了字节去重”。AnyTLS没有适用的T分母，不用零填补。

## 3 观测与特征体系

### 3.1 采集关联提供了什么

TrafficTracer的主要价值是登记父访问、请求、逻辑连接、两侧捕获及carrier关系。SS/VLESS等排他TCP对象可建立连接对；Hy2/AnyTLS的逻辑连接与物理carrier要分别处理，不能强行一一配对。

最终业务推理只输入post数值，不等于整个观测管线不依赖双侧或内部索引；pre-only、双侧和测试pre诊断臂另行注明。大部分正式post实验属于offline_index_assisted_post：连接纳入、共同资格和访问边界由离线关联形成。真实目标出口服务器/CDN不在当前客户端pre/post抓包的完整观测范围；SNI/host可作为资源元数据，不能单独确定CDN供应商、PoP或代理出口源站IP。

最初方向使用发起方；后期共同窗口按客户端到已登记服务端为up，返回为down。具体版本分别冻结，不能用捕获中任意首包重新翻转方向。

### 3.2 已提取的特征与实际输入不同

| 表示层 | 内容 | 使用方式 |
| --- | --- | --- |
| 初期实体特征全集 | 方向、带符号长度、IAT序列；长度/IAT统计与固定箱；方向包/字节量；burst、active/idle；FR、转移、熵；累计形状；TCP RTT、重传、flags/window、握手；访问并发与复用 | 原始特征表与统计分析，不是全部同时入模型 |
| scalar14 | 包数、字节、上下行、burst、FR及归一化、方向组成、转移、长度/IAT中位数等 | 初期业务、教师与P7 |
| distribution157 | scalar14＋19长度箱＋23 IAT箱＋101累计曲线点 | 教师、MLP、摘要SSL、G1–G6、反向校准 |
| 记录结构＋时间 | 每flow方向内记录长度/语法/位置；独立新字节时间线 | 0916 VLESS序列CNN与访问汇聚 |
| T七维 | 两方向U、E、R，加共同连接数F | TCP摘要前向增广 |
| W六维 | 两方向观测payload字节W、正payload事件P、访问合并方向段R | Hy2窗口、Extend五部署增广与神经研究 |
| 96维 | 四个W/U字节变量各9箱，六个P/E/方向run变量各10箱，访问内连接等权 | Extend概率融合、LR迁移、P-small、硬锚点与动态q |
| 162维 | 96维加同连接联合响应块；配套独立边际乘积控制 | 同连接联合响应支线 |

初期raw落盘实体宽表9121行、1881数值列，排他pair表1432行、Hy2窗口41行，页面对齐192行；它们是测量产品，不能拿1881维数或9121实体数替代后期模型的96/157维和30内容样本数。

基础字段可由包解析库提供，统计量及连接状态由项目自行计算，不依赖Wireshark内置FR、重传或流统计。IP/MAC、端口、SNI、URL、协议名、路径和身份字段用于标签、分组与审计，不进入主数值allowlist。ip_bytes是字节量，不是IP地址。

### 3.3 FR与各类方向段必须分名

非空包方向序列首段计1，对应用户定义的FR-runs；仅计切换为FR-switches，非空时等于runs−1。归一化FR是另列，不能混报。最早报告某些flow_reversals主表实际用switch，后续已显式保存runs/switch并分别解释。

FR_packet_runs按正payload包计算。R_unique_zero_runs按贡献唯一新字节的事件计算。T的方向段先在连接内计算再求和；W的方向段在访问合并时间线上计算。TLS记录时刻排序形成的方向段也不是原FR。这些量没有被悄悄互相替换。

U是观察到的唯一TCP字节，不自动等于完整成功交付的业务载荷；E不是总包数。早期exclude_full_retransmission仍可能保留部分重叠，不等于后期严格区间并集去重。

## 4 统计规律与对应关系测量

### 4.1 变换可重复 但不是所有指标都不变

重复采样阶段比较重复内MAD/IQR、ICC(A,1)、协议间与重复内方差比、跨URL方向一致性；保留五轮/四轮、非空包、排除完整重传和载荷分层敏感性。

旧Detailed有效12URL中，SS的典型中心表现为包数+59.8%、transport bytes+1.1%、burst+69.6%、FR-runs+3.2%；VLESS分别为+28.1%、+7.4%、+6.7%、+25.1%。SS“包增、burst增、字节近似保持”联合profile在五轮12个有效URL中有10个成立，不是对全部18目标的无条件定律。

同一报告中SS包数ICC约0.705、字节0.724、burst0.731；VLESS对应约0.923、0.932、0.772，FR-runs约0.816。区间、小样本及退化结果一起保留。MAD较小不能自行替代ICC或正式等效检验。

0916主240队列的内容等权复核如下；倍率来自该报告的ln(post/pre)中心，不能与其他加1、聚合权重或窗口定义混算。

| 指标 | SS典型倍率 | VLESS典型倍率 |
| --- | ---: | ---: |
| 包数 | 1.6746 | 1.2453 |
| transport bytes | 1.0196 | 1.0589 |
| burst | 1.7509 | 1.0720 |
| FR-runs | 1.0561 | 1.2303 |

SS更突出packetization重构，VLESS的非空方向段增加更一致；IAT、长度分布及累计过程还具有业务依赖。Hy2载体上下文倍数较大，但分子包含共享、控制和背景流量，不能当页面专属膨胀系数。跨0914/0916逐条目报告另覆盖987选定访问、117批次条目，已保留逐条目和路由分层结果。

### 4.2 部署预测与精确配对价值

最初raw三部署A-core站点隔离nested CV的mean macro-F1为0.867，FR-only约0.754；从完整模型去掉FR几乎不变，说明低维可解释性与独立增量不同。

早期100访问信息关系研究中，留URL的pre部署F1约0.930、post约0.770、变换约1.000。0914独立140队列中，pre14为0.9212、post14为0.8786、joint scalar为0.9356、joint distribution与Δ17均为1.0000。因此pre不是天然不含部署因素的语义真值；双侧拼接也强，不能把Δ视为独有信息通道。

0914 Δ17真配log-loss为0.0109 bits，同URL同部署跨重复错配平均0.2354 bits，优势0.2244 bits，URL条件区间[0.0634,0.4327]。独立实现重训、内层分法与训练URL重采样补强后，主口径优势仍在；非空包口径区间仍跨零。174720次拟合不是174720个独立样本。

这支持当前队列中真实对应的部署预测价值，不证明纯协议因果效应、变换可逆、业务收益或完整信道容量。

## 5 教师 学生与自然配对表示学习

### 5.1 P0至P7与MLP局部正结果

0916首轮固定线性监督比较硬标签M0、post OOF教师M1、真实pre OOF教师M2、同业务错配pre教师M3。六类SS中CE为M0 0.5797、M2 0.6429、M3 0.7024 bits：真配比错配好，但不如硬标签。P0–P4补齐软目标实现、post/pre/joint/Δ表示、联合教师、双向部署迁移、教师分法和299敏感性；P5/P6定位计数变化与跨部署错误。没有获得普遍单侧净收益。

固定监督换小MLP后，局部结果转为正：YouTube播放/搜索、distribution157、SS→VLESS，五seed均值如下。

| 学生监督 | CE bits | F1 |
| --- | ---: | ---: |
| 硬标签M0 | 9.5205 | 0.3440 |
| post教师M1 | 5.1782 | 0.3333 |
| 真pre教师M2 | 1.6380 | 0.5811 |
| 错配教师M3 | 4.7320 | 0.4401 |

M2相对三臂的CE收益区间为正，五seed的F1均超过相应控制。正式800个模型使用d→32 ReLU→K、固定1000步Adam，未重训教师或使用目标部署拟合。六类没有普遍复现该双重收益，不能把局部正例升级为一般机制，也不能将其抹去写成“蒸馏全部失败”。

P7另以scalar14的真实/三种错配漂移二阶矩及等trace各向同性正则比较，固定三λ、320次拟合，未获得任何设置的全部任务/身份/正则收益区间为正。它和MLP教师方法不是同一种实验。

### 5.2 自然配对VICReg与十四类目标识别

0916固定157维编码器比较普通post监督、post SSL、双侧侧内SSL、同次pre/post SSL、同内容跨重复SSL。六业务微调F1约为0.9017、0.8991、0.8992、0.9018、0.8978；真配没有稳定额外增益。冻结探针真配约0.7651，跨重复约0.8510，不能归咎于所有优势只在微调后丢失。

这些是VICReg非对比自监督，没有显式InfoNCE负例。错配是对应控制，不是“不同业务负样本”；自然正例也不要求逐条记录相同。

0914另做14类固定目标识别，留整重复轮次：157维LR F1 0.6297，小MLP三seed0.6323；前8秒分别0.5668、0.5453。它没有配对SSL，也不检验未见内容；每类只有一个资源，Example为控制类，Vimeo为简介页。

### 5.3 G1至G6可靠结构锚点与诊断

将157维分为字节4、方向2、非空交互4、包化22、时间24、累计形状101六组。训练内一维Ridge估计post→pre技能，以最差部署技能生成无业务标签的可靠性权重，再辅助post SSL预测pre统计。

5960次可靠性回归和285个正式阶段完成。R4可靠性加权微调F1 0.894817，普通监督0.901702；未建立新增业务收益。后续三项受控诊断显示：G4单组业务F1 0.814990，较强，但可靠权重只有约6.5%–6.7%；G1/G6很可预测，神经辅助头仍落后于一维Ridge；G6访问残差能量在SS约50%、VLESS约75%，同时保留业务和内容结构。

因此可预测性、近似不变性与业务增量不应混同。业务标签用于单组/删组诊断，没有回写无标签可靠性规则，也没有事后指定FR补位。

## 6 固定源分类器的反向跨侧校准

这条路线是post→pre坐标校准，不是后来的pre→post生成器求逆。固定pre分类器，比较源能力、原样迁移、真/错配一维Ridge、post监督；随后仅改变298参数逐维仿射的恢复目标，引入固定源相对logit保持项，并增加内容×部署中心H。

| 方法 | 0916两已见部署内容留出F1 |
| --- | ---: |
| A pre训练/pre测试 | 0.954656 |
| B 原源模型直接接收post | 0.455518 |
| C 真配Ridge校准 | 0.768683 |
| D 循环错配Ridge校准 | 0.645773 |
| E post监督 | 0.908219 |
| F 真配恢复＋决策保持，λ=1 | 0.853494 |
| G 错配恢复＋决策保持，λ=1 | 0.865603 |
| H 内容×部署pre中心目标 | 0.864561 |

真配统计校准有实际用途；决策保持改善迁移，但F没有可靠超过G/H。H仍使用组身份，并不完全无对应；未登记等效边界，不能称F/G/H等效。恢复MSE、源边界保持、物理范围与业务决策是不同终点，决策校准也增加了部分统计/物理范围违反。

只用单一部署拟合全部预处理与映射后，跨部署具有方向性：SS→VLESS的B/F/H/E_src F1为0.3503/0.3356/0.3685/0.4476；VLESS→SS为0.3653/0.5538/0.6059/0.3740。后者支持有限校准迁移，前者不支持稳定F1恢复。目标pre上的源诊断A也明显退化，说明偏移不只在出口映射。

## 7 协议观测与记录结构表示

### 7.1 字节去重与早期阶段定位

0914/0916重提取登记6596对严格TCP连接、26384方向侧记录，26358具有有效唯一字节。去重不保证pre/post比值靠近1：它同时改变两侧，不能把去重后的差直接当精确协议开销。

旧VLESS在主要上行负载层出现约1870B附加中心，下行约5.7–6.2KB；按内容OOF的上行MAE约152B、下行约441–446B。新增关系项改善有限，附加中心是描述模型，不是K。

57对冻结连接中45对VLESS、12对SS。VLESS严格语法证据只到E1：初始Hello与连续记录可解析；没有E2支持initial/relay语义边界。SS是平行诊断参照，不据此获得TLS记录资格。因此没有删除固定头部、固定两段或按最相似切点制造阶段校正。旧SS未知cipher保留，Hy2不套TLS解析。

### 7.2 记录结构与独立时间的正结果

记录静态结构通过同字节流重分段正/负测试；记录长度分布在定点样本整体更接近，但固定1024B分块距离更小，说明“更相似”不足以判优。记录first/all/prefix只是观测时刻，不自动是业务或Vision状态。

正式业务沿用0916 VLESS的120访问、30内容和1179共同可解析连接对。CNN分别编码方向内静态序列与独立新字节时间线，flow表示32维，访问mean/max汇聚加flow数量；固定监督与四种SSL共享成员、时间分支和训练预算。

| 表示或监督 | 三seed平均F1 |
| --- | ---: |
| 仅时间S0 | 0.883347 |
| 包级首次贡献字节＋时间S1 | 0.922420 |
| 严格记录＋时间S2 | 0.972320 |
| 固定分块＋时间S3 | 0.860670 |
| 记录不含类型＋时间S4 | 0.952780 |
| 真flow配对SSL后微调L3 | 0.947317 |
| post SSL后微调L1 | 0.946976 |
| 双侧侧内SSL后微调L2 | 0.955567 |
| 局部错配SSL后微调L4 | 0.955491 |

S2−S1约+4.99个百分点，描述性内容区间为[+1.93,+8.34]；L3没有额外超过直接监督或其他SSL控制。冻结探针L3来源约0.7897，post SSL约0.8850，说明当前配对表示也未显示更强的固定低容量业务可读性。

这一轮保留“结构化记录表示有业务用途”和“同一表示上的真实flow配对VICReg增量未建立”两项结论。静态重分段测试不是含时间完整分类器的扰动鲁棒性证明，也不外推到Extend全队列：Extend后来没有现成严格记录缓存。

## 8 前向漂移与有限校准增广

### 8.1 从校准特征到生成训练视图

前向模型直接学习pre→post风格摘要，不是反向校准的逆函数，也不是GAN、扩散模型或可执行PCAP生成器。其基本形式是：在编码坐标学习条件中心，为训练pre查询抽取一个完整留一内容残差向量，再经固定解码器生成摘要。生成器为小型Ridge和经验残差；MLP是下游分类器。

真实配对、循环错配、匿名组级关系分别拟合自己的中心与残差，不借用真配残差池。组级方法保留内容对应但删除逐访问身份；center和marginal仍可能使用真实漂移池，不能称为完全无关联参照。分类器最终只接收原七维T或六维W，不接收donor、生成坐标或校准身份。

训练内容交叉生成与LOCO残差使查询内容不进入自己的生成器拟合。一个访问的八个合成视图仍归属于该内容，不增加独立样本数。生成质量的离线测试pre只用于诊断，不进入正式post推理。

### 8.2 条件漂移与配对预算实验

0916最初条件漂移T0–T6比较原pre、固定中心、无条件联合残差、条件中心、真配随机、错配随机及真实post参照。SS的固定中心已接近复杂模型F1；VLESS的条件随机有部分用途；真配的生成质量优势没有普遍转化为真配−错配F1优势。

随后有限预算CB实验在24训练内容中开放25%、50%、75%的真实配对C，其余U只开放pre与标签。两部署低、中预算的真配增广相对只用C_post参照有正向F1区间；相对同样额外pre与标签的raw参照，六种部署×预算组合的F1区间全部跨零。SS部分预算真配优于错配，VLESS没有稳定对应F1优势。

这支持有限资源下的增广用途，不证明已经减少实际采集75%，也没有减少业务标签。历史共同连接资格曾读取两侧；屏蔽U_post拟合权限不等于观测与资格阶段从未捕获过U_post。

### 8.3 跨业务旧坐标在资格门停止

跨业务XBC任务固定两业务无训练post，C仅来自另四业务。240个scenario保留所有六标签、五折、三个业务组和八轮换。原log坐标候选在60个合法性门单元中有8个首次非法率超过10%，主要违反R≤E≤U与方向段联合约束；按原合同在分类前停止。

该实验没有新F1，不把拒绝后最终合法率当作原门已通过，不删失败业务或group控制。独立拒绝诊断定位了输出可行域随查询中心变化的问题。

### 8.4 可行摘要坐标获得双重业务增量

FSC独立版本改变输出参数化：生成段总数N、合法方向差D、事件余量G和字节余量H，还原R、E、U；保留F、分类输入、角色与预算。真配、错配和组级都采用相同必要约束。合法率按构造通过只是实施条件，主成功仍由业务对照决定。

| 0916部署 | paired F1_new | raw | group | paired−raw | paired−group |
| --- | ---: | ---: | ---: | ---: | ---: |
| SS | 0.961005 | 0.758973 | 0.896676 | +20.203个百分点 | +6.433个百分点 |
| VLESS | 0.747832 | 0.445694 | 0.652044 | +30.214个百分点 | +9.579个百分点 |

四项家族98.75%内容区间下界均为正：SS的两项分别[+15.505,+25.539]、[+3.642,+10.206]个百分点；VLESS分别[+22.723,+37.444]、[+5.123,+14.613]。这是当前训练权限下真实配对增广超过直接pre和匿名内容组的正式正结果。

SS的marginal点估计0.963339略高于paired；VLESS真实post参照0.821861仍高于paired。因此不是“条件生成器在所有指标与参照下最优”，也不是完整流量或业务语义保真。

### 8.5 Hy2改为窗口观测后收益边界不同

严格carrier资格先导发现98/100主carrier没有创建事件，完整成员不能只用1526请求关联连接，flow-index登记成员为5520；初始严格分支没有分类结果。用户确认窗口观测后，重建原始TUN/physical的实际会话窗口，不伪造完整生命周期。

HFC-W使用25内容、五业务、100访问，W/P/R六量，不使用TCP唯一字节或内层F。paired F1_new为0.612644、raw为0.029655、group为0.601417。paired−raw为+58.299个百分点，97.5%调整区间[+51.779,+63.777]；paired−group仅+1.123个百分点，区间[−0.471,+2.712]跨零。

因此Hy2窗口变换相对raw有用途，精确访问身份相对组级增量未建立。不能把它与SS/VLESS六分类T分数作协议排名，也不能将未通过直接归因为多路复用。carry-in和生命周期未知、一个尾部成员无包及用户确认的降级文章访问均保留。

## 9 六部署扩展与协议维度评价

### 9.1 Extend v3的W T独立主分析

Extend迁移冻结六业务、30内容、四重复，保留同部署、目标两业务无训练post的C/U/H任务。每部署每轨道120个scenario，W五部署600个、T四部署480个，七臂及三seed共同评价。C为六辅助内容24配对访问，U为18内容72pre访问，H为六内容24post访问。

| 轨道 | 部署 | paired F1_new | raw | group | paired−raw百分点 | paired−group百分点 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| W | SS | 0.787975 | 0.359264 | 0.601528 | +42.871 | +18.645 |
| W | VLESS | 0.702982 | 0.357915 | 0.575971 | +34.507 | +12.701 |
| W | Trojan | 0.670733 | 0.235365 | 0.579938 | +43.537 | +9.079 |
| W | VMess | 0.686778 | 0.276378 | 0.607290 | +41.040 | +7.949 |
| W | AnyTLS | 0.796008 | 0.386694 | 0.628466 | +40.931 | +16.754 |
| T | SS | 0.663410 | 0.355590 | 0.563215 | +30.782 | +10.020 |
| T | VLESS | 0.708135 | 0.068934 | 0.603920 | +63.920 | +10.422 |
| T | Trojan | 0.723723 | 0.072201 | 0.618981 | +65.152 | +10.474 |
| T | VMess | 0.666663 | 0.092886 | 0.577776 | +57.378 | +8.889 |

W十项、T八项主比较全部在各自家族校正后为正；两个家族分别校正，不冒充18项共同5%保证。这是对有限校准增广正结果的跨部署覆盖补充，不是六协议统一成功，因为Hy2未进入分类、AnyTLS无T结果。

Trojan W的center为0.685506，高于paired；SS T的marginal为0.702987，也高于paired。paired−center/marginal/reference没有同等级预登记内容显著性结果，不能用三seed均值重新造检验。更高部署数也不消除既有30内容的回顾性选择边界。

窗口身份、时钟、carrier冲突和七处关联问题通过本批来源证据与sidecar处理，不修改原始抓包；v3不混装较早失败版本。配套契约说明了W/T的流量保留分母、标签与每臂资源，不能把一个较弱raw参照替代充分真实post参照。

### 9.2 已见部署共享模型与留一部署

之后E1/E2改为所有源部署六业务都有真实post，不再叠加目标业务post缺失。共享分类器为6→32 ReLU→6，M0充分post混合、M1原pre混合、M2真配生成、M3组级、M4循环错配，另有部署独立I0。

| 实验 | M0等权F1 | M2等权F1 | M3等权F1 | M2−M0校正结论 |
| --- | ---: | ---: | ---: | --- |
| E1五部署已见共享 | 0.7159 | 0.7248 | 0.6556 | +0.88个百分点，区间跨零 |
| E2每次留一部署 | 0.6061 | 0.6097 | 0.5713 | +0.36个百分点，区间跨零 |

M2−M3在E1/E2均通过各自家族；E1 M2−M1通过，E2该比较跨零。独立I0等权F1约0.7565，SS尤其优于共享模型；E2留SS时group/cyclic点估计又超过paired。真实配对优于较粗生成控制，不等于超过充分多部署post监督。

E2同时禁止目标部署所有pre/post参与拟合，并禁止测试内容在任何源部署进入训练。部署不作为共享模型的测试数值输入，但用于训练分组与生成器路由。该评价是拟合期留部署，不是人类研究者从未见过目标部署的盲测。

### 9.3 64URL止于资格尝试

Broad 384访问完成路由与标签登记；六部署同一组23类主文档DIRECT。共同41类四部署的260访问做了资格复核，仍有9个缺SYN和45个多SYN路径待处理。正式特征权限包、训练和评分未完成。

因此目前没有64类或41类分类成绩。SNI子域与资源flow可以归属同一访问，却不是该URL的独立重复；随机拆它们只测试同访问内资源识别，不能宣称未见访问/内容泛化。此分支按用户决定记为“64url的实验尝试”，未继续训练。

## 10 协议实现与概率漂移测量

### 10.1 源码约束不等于可观测状态

研究核对了../mihomo的origin/Meta及采集构建和依赖快照。Extend采集构建74cfed919…与参考Meta 88dcbf7f…不同，历史解释优先绑定采集版本；活跃SS/VMess委托实现不能被本仓库残留旧文件替代。

| 部署 | 机制线索 | 当前实验解释边界 |
| --- | --- | --- |
| SS | AEAD salt与chunk开销；Extend AES-256-GCM，无plugin/smux | 32B salt、34B/chunk局部规则不能用TCP包数计算；旧批cipher未保存 |
| VLESS | 请求、TLS及可选Vision/direct状态 | 旧批为REALITY/Vision；Extend为TCP+TLS，无REALITY/Vision/smux，不能沿用1870B或+2先验 |
| Trojan | 初始化请求位于外层TLS等传输之内 | 请求头长度不等于捕获唯一字节差 |
| VMess | 模式、chunk、请求随机填充；Extend WS+TLS auto | alterId/最终安全模式缺口保留，不给每TCP包固定开销 |
| AnyTLS | 帧、初期padding、scheme更新和session复用 | carrier帧/stream与逻辑TCP不同；counter/scheme不能从现有摘要恢复 |
| Hy2 | 共享QUIC、逻辑stream、拥塞/恢复与obfs | Extend启用Salamander、无hopping，旧批设置不同；不映射成TCP pair |

已有规则测试和机制资格登记，没有可靠捕获依据的状态不生成、不补零。代码存在状态切换不意味着抓包已经定位切换；连续记录语法不意味着一直属于同一封装层。

机制启发中心D2加入pre实体数、长度分位和小载荷比例等八代理，保持小Ridge。五部署D2_pair F1 0.728858，通用六量D0 0.724772、同增强输入D1 0.722704、post M0 0.715930；相对后三者主区间均跨零，只相对D2_group的+6.23个百分点获得正向区间。机制候选未成为强基线赢家，也不识别精确协议K。

### 10.2 内容外连接概率预测提供明确对应证据

Extend四TCP部署23566连接对、480访问，十变量为两方向W/U/P/E及FR_packet_runs、R_unique_zero_runs。固定物理箱，按内容、访问、连接分层等权质量计数，构造真实联合条件核K(B|A)，对照post边际和同内容两侧边际乘积的匿名核。

| 部署 | post边际复合loss | 真配核 | 匿名组核 |
| --- | ---: | ---: | ---: |
| SS | 2.096503 | 0.599778 | 2.046395 |
| VLESS | 1.481072 | 0.554570 | 1.441824 |
| Trojan | 1.481938 | 0.549867 | 1.442702 |
| VMess | 1.301900 | 0.642306 | 1.264768 |

单位bit；八项主组合评分比较全部通过家族校正。这是精确连接统计对应的内容外预测用途，比简单相关性描述更强，但评分是十个单变量的复合log-loss，不是十维联合似然、完整流量信道容量或业务F1。

经验与平滑信息量分别从各自一致联合分布计算熵/互信息；离散化、样本质量和平滑均影响数值。分类CE差、配对相对错配的loss差、协方差能量或稳定秩均不能直接叫互信息。原单位长尾误差和负载条件扩展负结果保留，概率好不等于字节精确。

### 10.3 业务条件核是oracle测量 不是攻击分类

在训练核加入Y条件后，D1相对共同真配、条件匿名及条件post边际的十二项概率比较全部通过家族区间。但留出Y用于离线oracle概率诊断，不能作为推理可用条件。

统计关系资格1200角色关系中82通过基本可靠门，0进入预登记约束列表；该分支没有新业务分类器或F1。更精细的条件预测用途不自动保证形成准确、非冗余的类别统计先验。

## 11 将关联融入分类的多条受控分支

### 11.1 机制条件编码与post任务迁移

机制条件SSL B5使用6→64→32编码器、投影头和训练条件映射，最终测试删除pre及条件。五部署600访问E1中，B5 F1 0.780593；同架构监督B0 0.768447、post SSL B1 0.773833、通用条件B4 0.777292、匿名组B6 0.769109。五主比较只有B5−同总更新监督B0L的极小正向下界通过；其他关键对照未通过。

冻结线性与MLP读出、随机编码器、条件使用、检索与错误翻转诊断没有显示B5明显更强的post业务表示。配对匹配较好不能替代删除条件后的单侧业务可用性。

随后任务感知J4用双侧CE与stopgrad辅助概率到post的KL，仍只post推理。修复J0数值求值路径后120正式模型完成，J4 F1 0.778322，六项主比较0项通过。它使用业务标签，不是无标签SSL；没有据最好点估计换主候选。

### 11.2 生成式概率决策与敏感度正则

漂移核生成式分类将pre类别分布经K映成post类别分布，再对访问直方图评分。真配G4相对原pre和匿名组的八主比较为正，但相对直接post概率与小MLP的八关键比较没有正向增量；自由训练post LR在四部署的F1约0.759–0.853，而真配固定核分类约0.416–0.608。

KSR改为自由96维LR加核条件波动几何正则，四候选源内公平选择。KSR2等权F1 0.814133，强L2 KSR1 0.812449；十二主比较只有VLESS KSR2−post重复控制通过，没有部署获得相对公平L2和匿名核的校正增量。6/20外层角色选择零权重，概率质量也非全面改善。

### 11.3 状态风险和交叉拟合重加权

DSR将训练漂移状态作为风险分组，比较真实状态、匿名状态、post难度及强L2。三种方法60次外层选择全部为alpha=0，最终与原LR精确相同；720个正alpha内层模型确实执行，类别变化为0、概率改变量很小。零差区间来自模型恒等，不是等效性检验。

RW固定训练内OOF困难方向再重加权，保留基座决策保护。RW4等权F1 0.805799，强post RW1 0.812449；20角色16次选择均匀权重，完整主张未通过。DSR与RW分别检验动态风险和固定OOF权重，不能把两者合成一项成功的Group DRO或互信息最大化。

## 12 辅助业务校准下的跨部署迁移

### 12.1 目标权限与强参照

后期四TCP部署任务固定60角色：四目标×五全局内容折×三业务遮蔽。每角色三源库288访问，目标C四业务16内容64访问可校准，目标U两业务8内容32访问两侧均禁用，目标H六未见内容24post访问。12个合法源内伪目标任务用于选择，实际目标与H不得进入选择。

这与0916单部署C/U增广不同：这里不是用实际目标U_pre生成，而是将已有三源库pre迁移成目标风格。StrongPost用相同源post、目标C和CORAL适配，是充分、可源内调参的强参照，不是弱raw。

### 12.2 条件核CT与联合仿射JA

CT第四版统一提高迭代和函数评价预算、保留原坐标梯度验收，14700个主模型完成；旧三版数值停止不混装。CT4 F1_U为0.717475，StrongPost 0.772708。CT4−原pre CT1约+13.417个百分点、CT4−匿名核CT3约+5.937，家族区间为正；CT4−StrongPost为−5.523，区间完全为负。对应价值与强基线优势分开。

JA比较逐块与全96维确定性仿射、真配与匿名组同容量目标。JA1 F1_U 0.685604，CT1 0.583306，JA2 0.687591，JA0 0.668073；只有JA1−CT1主比较通过，没有联合结构或精确身份新增收益。Trojan辅助业务代价也越过当时登记门。

JA原runner在历史CT5元数据接口停止，训练、选择和4320新预测已封存；独立后处理完成原坐标审核、420旧参照与180新外层CUDA精确重放和既定评分，保留原failure及追加结项血缘，不改写原runner成正常结束。

同正则分解确认：真配与组映射之差来自内容内同次两侧交叉波动项，且映射确实保留了它；但它与业务增量不同。组方法也保留内容中心关系与入口协方差，不是把所有关联删光；矩阵范数比例不能算对应信息占比。

### 12.3 P-small的正结果与归因

保持StrongPost，辅助槽仅以10%真配视图替换CORAL，即全CE质量1/30；其余真实post主槽和目标C各1/3不变。与完整替换比较，结果如下。

| 方法 | F1_U | F1_all | 最差部署F1_U |
| --- | ---: | ---: | ---: |
| StrongPost S | 0.772708 | 0.804617 | 0.660738 |
| P-small | 0.796931 | 0.817674 | 0.716522 |
| G-small | 0.794927 | 0.813273 | 0.715677 |
| P-full | 0.677992 | 0.764549 | 0.547538 |
| G-full | 0.688711 | 0.765093 | 0.563893 |

P-small−S为+2.4223个百分点，四项家族98.75%区间[+0.5681,+5.2705]；P-full−S约−9.47，区间完全负。有限加入有益不代表整槽替换有益，也不是增加了新独立访问。

追加同样small比例的RawPre、RawPost、Marginal控制后，P-small−RawPost为+2.2334个百分点，三项家族区间[+0.2758,+4.9019]；相对RawPre、Marginal均跨零。原P-small−G-small也跨零。

因此P-small的用途已经建立，不能说所有漂移材料无益；但精确同次身份、该估计器相对简单pre或匿名矩适配的独立归因未闭合。旧四项与新三项分别登记，不将两次区间拼成共同七项家族。

### 12.4 同连接联合响应没有普遍胜出

162维J增加同连接响应组合，与同维边际乘积I及96维M比较。J-S F1_U 0.743745，I-S 0.753274，M-S 0.778115；J-P-small 0.775544。五项主比较只有J-P-small−J-S约+3.180个百分点通过，未超过组级或raw-pre控制，也未证明新增联合表示优于原边际。

该支线保留同连接信息的明确对照，不以更高维度自动称更强表示；不覆盖96维P-small结果。

## 13 单侧观测与跨批次资格仍未闭合

P-small后续O1先导仅从24个physical PCAP及自有C校准登记的端点提取，未读取TUN、NetLog/CDP、旧配对名单或业务标签。旧共同范围1235条post连接的十项统计精确重放，但完整端点范围新增9条非空连接缺初始SYN，导致9个父访问未通过冻结保守门。

因此计数实现通过，不等于完整攻击输入资格通过。480访问全量提取、独立固定窗口O2、冻结模型的新观测推理及同口径复训未执行，没有新F1。先导数值窗口仍来自旧browser_quiescent边界，不是完全被动在线分段。

端点IP/端口可用于已登记物理包选择，但不进入96维业务数值模型；“模型不输入地址”不等于整个研究从未使用地址或协议配置。提取资格需要生命周期、窗口和来源证据，不能单靠PCAP里有一个IP恢复所有逻辑配对。

0916与Extend当前30内容全部重叠，旧批96维输入也未准备为同口径外部测试。因此没有完成独立内容/外部节点/跨日期验证，也不能把0916敏感性或模型重训称为现成独立复现。

## 14 从硬不变保护到动态幅度策略

### 14.1 完整直方图块没有最终保护资格

不变锚点分支对96维十个完整块检验：同次近似恒等、跨内容非平凡变化、内容外覆盖，以及原映射是否额外破坏该关系。60角色P/G共1200个角色块、480个OOF映射完成；最终锚点数为0，未启动180业务分类器。

独立失败路径与四格投影重放确认实现与原合同一致：两个SS的R_unique_zero_runs块通过关系与完整C资格，却没有足够映射额外越界，因而不需要该保护；另两个W_up候选有映射破坏，却没有足够关系资格。它们不能拼成一项成功证据。

完整块保护失败不证明所有统计函数都不存在不变关系，也不支持指定FR补位或放宽阈值。真实界内的原始几何投影与标准化分类坐标误差可能异向；真实应当变化的样本被压回也没有误差非增保证。这些是几何诊断，没有新F1。

### 14.2 动态模型保持了什么

动态分支以冻结基础映射b0和pre a构造每块调整视图r_q(a)=a+q⊙(b0−a)，q为十维角色级参数，最终测试时冻结，并非逐访问在线门控。q=1恢复基础P/G映射，不表示pre/post相等；q=0才回到原pre。

源内Q来自充分拟合LR后的合法伪目标留出CE，实际目标H/U不参与。总目标为Q、rho=0.01的q收缩及nu=1的关系软惩罚；关系项只惩罚相对原映射的标准化恢复误差增加，不是让两侧越相同越好。small比例、96维、P/G映射、t/eta与分类正则均保持。

D-P或QP用真配映射与关系目标；T-P或QT仍用同一P映射，但不加完整关系软目标，因此不是“完全无配对”参照；D-G或QG使用自己的匿名组管线。对应管线比较包含映射和目标，不独立识别惩罚中实例身份的纯因果贡献。

### 14.3 数值先导与正式评价分开登记

| 阶段 | 已执行结果 | 可作何种判断 |
| --- | --- | --- |
| 原64步可微内层 | 激活边界中心差分门停止 | 不能作业务结论 |
| 分项梯度修订＋24收敛LR参照 | 1440项分项检查通过；64步剩余目标差约99.98% | 梯度检查通过不等于任务反馈有代表性 |
| 冻结Cholesky坐标，64/128/256步 | 24问题各长度起点质量均未通过 | 停止该固定全范围谱界有限展开，不否定动态研究 |
| 充分LR＋隐式解级反馈第一版 | 初始有限差分局部一致，但原精度稳定门未通过 | 保留原停止，不直接业务放行 |
| fine加独立一次Newton校验第二版 | 原残差、Hessian、线性系统、双精度梯度及固定非平凡点通过 | 允许解级反馈正式实验，不保证F1改善 |
| 固定20次Adam正式D-P/T-P/D-G | 60角色、180终态与业务评价完成 | D-P对S有收益，独立机制增量未建立；多数约束轨迹总目标未降 |
| 固定度量＋位移限幅＋双档Armijo f0先导 | 36轨迹12有限进展、18仅下降、6单轨迹预算停止 | 原全轨迹放行门未过，无新业务成绩 |
| 独立资格启用＋固定回退策略 | 全180决定、66新最终模型、114精确回退、完整业务评价 | 最新可审计完整策略的结项结果 |

充分LR始终保持原加权CE和原W的L2，不给bias新增正则，不在变换参数上偷换L2。隐式反馈解Hv=∇θR_val，再计算−Bᵀv，消除共同softmax偏置自由度并独立验收原坐标。前向、精炼和有限差分精度配套，软惩罚激活边界沿用独立解析分项核验。

这些修复没有更改业务标签、删除困难SS、扩大模型或根据目标H调权重。旧停止、进程中断、精度表头错误和恢复计费保留来源；新版本不借旧通过项混装为一次完整实验。

### 14.4 旧Adam业务结果

正式D-P的F1_U为79.8301%，S为77.2708%，P-small为79.6931%。D-P−S约+2.559个百分点通过七项家族；相对P-small、T-P、D-G等均未通过。D-P整体F1及U的CE/Brier还不如P-small，且多数约束终态总目标高于起点，不能将该结果称外层充分优化后的目标裁决。

### 14.5 最新原资格启用与固定回退

用户确认原资格、全五折累计20小时优化上限，以及QP−P-small总体C F1代价不超过1个百分点、各部署不超过2个百分点。未获原优化资格但完整安全结束者回到基线；完整性、后端失败、全局资源或尚未执行者不能冒充回退。

最新运行于北京时间2026年10月14日05:15结束，退出码0，约11小时57分30秒；含f0复用累计优化14.0825小时，没有触顶。180条实际轨迹全部降低总目标；QP/QT/QG启用21/17/28，分别回退39/43/32。31条40-trial停止全部属于SS；全部114回退的概率、log-prob、决策精确相同。

| 方法 | F1_U | F1_all | F1_C | CE_U nats | Brier_U |
| --- | ---: | ---: | ---: | ---: | ---: |
| P-small | 79.6931% | 81.7674% | 82.8046% | 0.861347 | 0.383276 |
| G-small | 79.4927% | 81.3273% | 82.2447% | 0.876079 | 0.380576 |
| QP | 79.3841% | 81.7012% | 82.8597% | 0.862971 | 0.384373 |
| QT | 79.5155% | 81.6931% | 82.7819% | 0.861637 | 0.383956 |
| QG | 79.0992% | 81.1150% | 82.1229% | 0.887212 | 0.383096 |
| S | 77.2708% | 80.4617% | 82.0571% | 0.950498 | 0.433116 |

七项主比较使用新预测、10000次共同内容簇bootstrap和99.285714%家族区间，旧区间保持不变。

| QP减参照 | F1_U变化百分点 | 家族区间百分点 | 正向增量 |
| --- | ---: | --- | --- |
| P-small | −0.3090 | [−0.9244,+0.1691] | 未建立 |
| QT | −0.1314 | [−0.6026,0] | 未建立 |
| QG | +0.2849 | [−1.1022,+1.5082] | 未建立 |
| G-small | −0.1085 | [−1.4413,+1.0420] | 未建立 |
| RawPre-small | +0.4029 | [−1.2403,+2.2532] | 未建立 |
| S | +2.1133 | [+0.2214,+4.8426] | 建立 |
| M-S | +1.5726 | [−0.4052,+4.1207] | 未建立 |

QP相对P-small仅改变5条访问—遮蔽组预测：C修复2个、U新增3个，没有U修复。启用子集也是0个U修复、3个新增，因此不能单以回退多解释失败。VLESS F1_U约+0.3374个百分点，Trojan−0.4723、VMess−1.1011，SS为0；VLESS提升来自C侧Bing纠错减少MDN假阳性，而非修复U访问。

C代价门全部通过，总体F1_C约+0.0551个百分点；最差下降为Trojan−0.1816个百分点。没有超过P-small才是当前关闭候选的主要理由，不是C代价超限。

本轮没有stationary轨迹，所有启用来自finite_progress，启用终态残差仍高于1e-3。所以可以确认受控优化与完整策略的业务表现，不能宣称外层已达驻点；但未验证的更充分最优解可能性也不构成默认继续搜索的依据。

## 15 共通实验设计与解释规则

### 15.1 正例 错配与组控制

正对应的粒度必须随实验注明：同次访问摘要、同条排他连接/flow表示、同连接箱统计，或共享carrier访问窗口。两侧第j条TLS记录没有被假定语义一一对应。

错配包括同业务跨内容、同内容跨重复循环、以及局部flow rank替换，不是相同控制。组级包括pre中心目标、全部Cartesian平方目标或两侧边际乘积，也不等于无对应。它们可能改变目标方差、连接角色和负载组成；真配优势不能直接叫纯访问噪声比例或对应信息量。

### 15.2 划分与flow泄漏

0916/Extend主内容任务将同内容所有部署、重复、父访问、两侧、内部连接和生成视图整体分折；不把同flow切片随机分入训练/验证/测试。源内交叉拟合重新限制映射、核、尺度、残差和教师范围；外层H不参与拟合和checkpoint选择。

0914十四类留轮次允许相同内容的新访问跨集合，是任务限制而不是同flow拆分。64URL的资源子流没有被实施为跨内容分类。已有捕获哈希、登记carrier、SYN及完整正载荷指纹审核在各自范围未发现跨折冲突，但生命周期未完全观测、内部索引与环境混杂的边界仍在，不能声称数学上排除任何未知泄漏。

### 15.3 模型与数值不是sklearn默认黑箱

早期LR/Ridge有冻结C/alpha、max_iter/tol、训练预处理及独立重放；小MLP有固定层宽、1000步、权重显式L2和匹配初始化；记录CNN固定卷积与汇聚。后期LR为CUDA float64的原坐标梯度感知求解，max_iter2000/max_eval10000，不更换原目标；隐式阶段另有fine精炼与一次Newton校验。

早期部分LR/MLP/仿射在Pytorch312的CPU float64上完成，后期按用户要求模型训练、推理、矩阵与梯度使用CUDA，无静默CPU回退。低GPU占用不是未用CUDA的充分证据，小LR串行线搜索和标量同步可限制利用率。最新实验没有擅自引入并行工程版本。

### 15.4 统计口径不能跨实验拼接

主要分析单位是内容，访问重复与内部连接随内容一起重采样。多seed结果先各自算指标再取均值，通常不集成概率。F1_new/F1_U取完整六类混淆矩阵中的未覆盖类，其他类的假阳性仍进入分母。

早期有未校正描述性95%区间，后期有各轮独立登记的多项家族，不能把所有“通过”叠成一个全项目确认性成功率。CE可能以bits或nats报告，必须按原单位；JS divergence不是平方根距离。缺失、不适用、空表、别名模型和零差必须按各自含义保留，不能补零造成虚假完成。

程序verification通过、观测资格通过、优化资格通过与业务主比较通过是四道不同门。数值/观测停止没有业务负结果；完整结果的局部正比较也不自动满足完整科研主张。所有目前区间都不替代独立批次、独立节点或全链路在线验证。

## 16 阶段性证据与未验证范围

| 研究主张 | 当前证据状态 |
| --- | --- |
| 不同部署造成可重复观测变换 | 支持；配置、路由、负载与观测范围条件需保留 |
| 真实连接/访问对应有额外预测价值 | 支持；部署变换和离散条件核有正式对照 |
| 真实配对可在部分任务改善post业务学习 | 支持；MLP局部任务、校准及合法摘要增广有实例 |
| 精确配对增广普遍优于充分post监督 | 不支持；E1/E2、机制SSL与多轮融合有明确限制 |
| 记录结构＋独立时间有同部署业务用途 | 支持；限0916 VLESS共同解析队列 |
| P-small优于当前StrongPost | 支持；固定四部署校准任务及家族对照 |
| P-small收益独立依赖精确访问身份 | 未建立；group、RawPre、匿名矩对照需保留 |
| 当前硬不变保护有合格作用对象 | 未建立；0最终锚点，未分类 |
| 当前动态幅度与关系惩罚有新增收益 | 未建立；最新QP未超过P-small/QT/QG |
| 已知精确initial/relay及协议K | 未完成，不生成或倒推 |
| 完全post侧无内部索引在线分段 | 未完成；O1完整范围资格未通过 |
| 六协议统一、64URL分类、外部日期泛化 | 不能宣称；适用队列不同，64URL未评分，独立外部验证未完成 |

论文最合适的主线是“可重复部署相关变换→真实对应的可利用价值→在不同学习与观测条件下的利用边界”。测量关联的价值与将关联放进某个损失后的增量应分开。负结果不能抹去FSC、Extend v3和P-small的正结果；局部正例也不能替代强post、组级、额外pre及跨部署对照。

当前可保留的稳定候选包括P-small及记录结构＋独立时间的同部署监督参照。动态十维候选按原规则结项，O1保持观测资格停止。后续任何单侧重建、异批次复核或新学习目标均须单独设计与确认，不由本总结自动启动。

## 17 原报告与复核入口

本总结按研究问题归并已经实施的实验，不替代各版本的成员清单、参数契约、逐类结果、模型及预测。下列入口对应正文各阶段；涉及历史停止和独立修复时，应同时保留两份来源，不以最后一个报告覆盖此前记录。

### 17.1 数据 特征与统计关系

| 正文范围 | 主要证据入口 |
| --- | --- |
| 初期raw库存、特征表与部署识别 | [最初阶段成果](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/stage-results-summary.md) |
| Detailed重复变换、ICC、跨URL规律 | [重复性统计报告](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/detailed-5reps/transformation-reproducibility-report.md) |
| 早期信息关系与恢复诊断 | [信息关系第一阶段](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/information-validation-stage1-results.md) |
| 0914同配置复核与配对价值 | [0914详细结果](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/0914-latest-experimental-results-detailed-20260915.md)、[不确定性与业务边界](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/0914-paired-value-uncertainty-and-business-boundary.md) |
| 0916库存与标签状态 | [0916数据及实验总结](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/0916-dataset-and-experiments-summary-20260917.md)、[299候选保守敏感性](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/0916-business-conservative-299-results-20260917.md) |
| 0916统计规律复核 | [变换复核报告](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/0916-transformation-replication-results-20260918.md) |
| 0914与0916逐条目、路由及部署统计 | [逐条目总报告](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/statistics/0914-0916-itemwise/overall-report.md)、[单项报告索引](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/statistics/0914-0916-itemwise/README.md) |

### 17.2 教师 SSL 特征组与源分类器校准

| 正文范围 | 主要证据入口 |
| --- | --- |
| P0–P4教师监督与机制诊断 | [P0–P4完整总结](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/P0-P4-experiments-comprehensive-summary-20260918.md) |
| P5–P6结构机制及线性P7 | [配对结构诊断](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/0916-paired-structure-mechanism-results.md)、[线性P7](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/0916-P7-linear-paired-constraint-results-20260918.md) |
| MLP教师与P7局部业务正结果 | [MLP详细实验记录](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/0916-MLP-detailed-experiment-record-20260918.md) |
| 自然flow配对VICReg与十四类0914任务 | [自然配对SSL](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/0916-natural-pair-ssl-results-20260918.md)、[0914十四类识别](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/0914-business14-classification-results-20260918.md) |
| G1–G6可靠关系、分类增量与层级 | [分组锚点结果](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/0916-group-anchor-results-20260919.md)、[三项受控诊断](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/0916-group-anchor-controlled-diagnostics-results-20260919.md) |
| A–E跨侧迁移、F/G决策保持、H中心控制 | [源分类器迁移](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/0916-source-classifier-cross-side-transfer-results.md)、[决策感知校准](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/0916-source-decision-aware-calibration-results.md)、[层级与中心目标](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/0916-source-score-hierarchy-center-control-results.md) |
| A–H结项与跨部署复用 | [机制证据综合](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/0916-A-H-mechanism-evidence-synthesis.md)、[源部署单独训练复核](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/0916-source-calibration-cross-deployment-results.md) |

### 17.3 协议观测 记录表示与前向增广

| 正文范围 | 主要证据入口 |
| --- | --- |
| 唯一字节、新字节事件及方向段 | [测量报告](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/protocol-normalization/measurement-report.md) |
| 配置不确定性、方向差及完整性分层 | [定点诊断](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/protocol-normalization/targeted-diagnostics-20260923/report.md) |
| 附加量描述与阶段定位停止 | [早期阶段机制检查](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/protocol-normalization/early-stage-mechanism-20260923/report.md) |
| 记录语法E1、重分段与独立时间 | [记录表示可行性](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/protocol-normalization/record-representation-20260926/report.md) |
| S/L记录业务实验及冻结诊断 | [正式分类结果](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/record-time-business-0916/formal-results.md)、[冻结探针](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/record-time-business-0916/localization/frozen-probe-results.md)、[错误定位](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/record-time-business-0916/localization/error-localization.md) |
| 漂移模型总体构建口径与条件生成 | [漂移模型构建报告](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/proxy-drift-model-construction.md)、[条件漂移第一轮](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/conditional-proxy-drift-0916/summary.md) |
| C/U权限隔离与校准预算 | [配对预算实验](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/paired-calibration-budget-0916/summary.md) |
| 原跨业务log坐标拒绝门停止 | [原跨业务完整报告](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/cross-business-calibration-0916/complete-report.md) |
| 必要可行域内生成与SS/VLESS双增量 | [合法摘要分类结果](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/feasible-summary-calibration-0916/summary.md) |
| Hy2闭合carrier停止与窗口独立任务 | [carrier资格报告](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/hy2-carrier-calibration-0916/summary.md)、[窗口业务结果](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/hy2-window-calibration-0916/summary.md) |

### 17.4 Extend 多协议 机制与概率核

| 正文范围 | 主要证据入口 |
| --- | --- |
| 六协议库存、W/T口径和训练权限 | [v3实验契约](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/extend-calibration-20260930/v3-experiment-contract.md)、[成员与观测范围](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/extend-calibration-20260930/v3-cohort-and-observation.md) |
| v3分类正结果、逐类及参照 | [正式v3结果](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/extend-calibration-20260930/formal-v3-results.md)、[结果补充](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/extend-calibration-20260930/v3-results-supplement.md)、[复现入口](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/extend-calibration-20260930/v3-reproduction-guide.md) |
| E1已见协议共享与E2拟合期留协议 | [协议维度正式评价](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/business-protocol-eval-extend/formal-results.md) |
| 64URL分类尝试的资格停止 | [尝试状态](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/url64-flow-transfer-extend/attempt-status.md) |
| mihomo源实现、配置及可观察边界 | [源码分析](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/mihomo-protocol-drift-analysis-20261003.md)、[机制诊断](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/mechanism-guided-drift/mechanism-diagnostic-report.md)、[机制引导增广](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/mechanism-guided-drift/formal-results.md) |
| B系列机制条件编码及J系列post锚定 | [机制条件SSL](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/mechanism-conditioned-ssl-extend/formal-results.md)、[post锚定训练](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/post-anchored-paired-training-extend/formal-results.md) |
| 条件概率核及信息量解释边界 | [协议概率漂移正式报告](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/protocol-probability-drift/formal-report.md) |
| 生成式业务决策、核敏感正则与业务条件oracle | [核业务融合](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/drift-kernel-business/formal-report.md)、[核敏感正则](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/kernel-sensitivity-regularization/formal-report.md)、[业务条件核](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/business-conditioned-kernel/formal-report.md) |
| 漂移状态风险与训练内交叉拟合重加权 | [状态分组风险](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/drift-state-group-risk/complete-report-20261006.md)、[交叉拟合重加权](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/cross-fitted-drift-reweighting/complete-report-20261006.md) |

### 17.5 P-small 观测条件与动态保护

| 正文范围 | 主要证据入口 |
| --- | --- |
| CT校准部署迁移与统一数值v4 | [CT最终详细报告](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/calibrated-deployment-business-transfer/v4/detailed-final-report-20261007.md) |
| 联合仿射、独立重放与身份分解 | [联合仿射完整报告](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/joint-affine-transfer/detailed-experiment-report-20261009.md)、[身份机制分解](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/paired-identity-decomposition/detailed-report.md) |
| small训练干预正结果及同预算控制 | [P-small详细报告](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/strongpost-training-intervention/detailed-report-20261009.md)、[小比例归因对照](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/small-view-attribution/detailed-report-20261010.md) |
| 162维同连接响应与独立边际控制 | [联合响应报告](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/connection-joint-response/detailed-report-20261010.md) |
| O1完整physical观测范围资格 | [O1先导与停止](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/p-small-observation-validation/o1-pilot-report-20261010.md) |
| 完整直方图硬保护及失败路径 | [锚点诊断](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/invariant-anchor-guarded-drift/anchor-diagnostic-report-20261012.md)、[资格与投影结项](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/invariant-anchor-guarded-drift/closeout-20261012/closeout-report-20261012.md) |
| 有限展开与修订梯度检查 | [原先导停止](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/dynamic-soft-drift-calibration/pilot-report-20261012.md)、[梯度修订及24参照](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/dynamic-soft-drift-calibration/repair-20261012/repair-report-20261012.md)、[可逆预条件展开停止](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/dynamic-soft-drift-calibration/inner-v2-20261012/inner-v2-report-20261012.md) |
| 解级反馈与配套精度验收 | [隐式首版结项](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/dynamic-soft-drift-calibration/implicit-20261012/implicit-pilot-closeout-20261012.md)、[fine独立核验第二版](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/dynamic-soft-drift-calibration/implicit-v2-20261012/implicit-fine-validation-v2-report-20261012.md) |
| 原固定20步业务、外层受控更新先导 | [旧Adam完整结果](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/dynamic-soft-drift-calibration/formal-20261012/run-02/complete-results-analysis-20261013.md)、[Armijo先导结果](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/dynamic-soft-drift-calibration/outer-pilot-20261013/run-03/pilot-results.md) |
| 最新资格回退策略的封存合同与36轨迹来源 | [P0优化器结项](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/dynamic-soft-drift-calibration/qualified-policy-20261013/P0-optimizer-closeout.md)、[P1合同](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/dynamic-soft-drift-calibration/qualified-policy-20261013/P1-contract-and-launch.md) |
| 最新完整策略业务成绩及独立解释 | [完整运行报告](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/dynamic-soft-drift-calibration/qualified-policy-20261013/run-02/complete-report.md)、[20261014独立分析](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/dynamic-soft-drift-calibration/qualified-policy-20261013/run-02/results-interpretation-20261014.md) |

### 17.6 最新运行的可追溯范围

最新业务运行根目录为`outputs/dynamic-soft-drift-qualified-policy-business-20261013/run-02/`，独立分析根目录为`outputs/dynamic-soft-drift-qualified-policy-analysis-20261014/run-01/`。对应实现为`eval/dynamic_soft_drift_qualified_policy_v2/`和`eval/dynamic_soft_drift_qualified_policy_analysis/analyze.py`。

最新运行有600个逻辑模型端点，其中114为精确回退别名、486个不同模型文件哈希；预测14400行。新增最终LR为66个，不能将600逻辑端点都记为新增拟合。源内优化累计50533次LR求解尝试、77880次隐式评价、3305次接受更新；含继承先导，其中一次历史中断尝试仍保留记录。

独立分析复核了2870个关键文件、指标与共享内容bootstrap口径，并核对全部114回退别名的概率、log-prob及类别。此处的“复核”沿用该独立分析产物，不是本次撰写总结重新训练或再次验证每一个历史模型。本总结仅归并已有证据，没有修改原实验合同、资格判定、统计区间或科研成功标准。
