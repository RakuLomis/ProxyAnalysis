# Extend 机制启发中心实验契约

日期：2026-10-04。G2已获确认，本轮只执行已见五部署E1 W；保留600访问、30内容、六业务、四重复、全局五折。不执行留一协议、T或Hy2分类，不新增采集。本契约在工程重放和业务结果前登记。

W保留旧定义：登记窗口正TCP/UDP载荷总字节（含重复传输）、正载荷事件P和窗口全局方向段R。R不是原stream FR，也不是记录时间排序所得特征。六业务为GitHub仓库浏览、YouTube搜索、Bing搜索、Wikipedia文章、MDN文档、YouTube视频播放。该说明补充观测单位，不改变封存方法或输入数值。

## 固定方法与权限

六臂为M0真实post、D0旧paired、D1同增强输入通用paired、D2机制paired、D2group、D2cyclic。D0有42参数，D1有90，D2有92。D1/D2的八个pre统计相同；业务分类器仍只读post六量，不读协议身份、地址、SNI、pre或增强统计。元数据只用于配对、内容划分及审计。

中心每方向以pre正载荷实体数N估计非负beta=sum N*(目标原始字节-pre字节)/sum N²；零分母取0。字节增量固定floor(beta*N+0.5)，P/R保持pre。旧65527P容量若越界则停止，不裁剪重抽。raw中心经原phi编码；Ridge拟合encoded目标减center，保留原pre phi的std及alpha1。beta不是精确协议K，实体数不等于新建物理carrier。

真配使用同次原始post估计beta；cyclic使用原roll(-1) donor；group只使用同内容匿名post原始字节均值估计beta。group的latent目标仍是encoded post的组均值，两种均值不混同；LOCO残差为四pre×四匿名post的Cartesian差，共288向量。group无session/repetition字段，pre自身八统计与其六量一起匿名排序，不借目标身份恢复配对。beta、q尺度、原pre phi尺度和剩余Ridge均在每个内层重新拟合。

生成器拥有fit pre/post和query pre的独立软件权限包，没有query post、test pre/post或标签；group有匿名包。LOCO保留完整内容，不随机拆flow。复用P2注册实体资格，保留5例未见SYN及其仪器条件；不宣称普遍无泄漏或外部盲测。诊断阶段的预检曝光例外仍保留。

## 预算和公平对照

100个生成任务，每方法19次Ridge，五方法合计9500个生产拟合；三seed复用同一拟合，各生成8视图，不改变整向量残差抽样或解码器。D0先与原生成数组、残差池和抽样索引复现。D2各臂的beta只用本臂允许目标，不能共享paired系数。

90个分类器：六臂×五折×三seed。6→32→6 ReLU MLP，422参数，CUDA float32、关闭TF32；1,000步Adam，lr0.001，权重L2=5e-5。每步相同内容/重复槽，0.5真实post CE+0.5辅助CE+L2；M0辅助槽重复真实post。post log1p标准化只由本折480训练post拟合，不测试重新标准化，不早停或选择checkpoint。每seed同初始化、主调度和视图调度；多头批处理不共享模型参数。

## 固定评价与停止

业务四项主要比较为D2pair−D0pair、−D2group、−M0、−D1pair，作为一个新家族；cyclic次要。30内容按六业务分层、跨协议/seed/臂共用10,000 bootstrap抽样，seed20260928，Bonferroni区间分位0.00625/0.99375。主要量为三seed平均的协议等权完整六类macroF1；并报每协议、最差协议、CE bits、Brier、逐类、逐seed及修复/新增错误。区间条件于固定模型，跨零不是等效。

分布诊断在全部生成冻结后由独立评分worker读取训练query post，检查方向MAE、偏差、latent误差及整池经验区间覆盖，不反馈生成器和模型选择。源码规则与本轮经验预测不可互相替代；增强输入或中心有效也不意味着精确封装机制已验证。

CUDA、权限、数值、容量、基线重放或旧哈希失败时停对应任务。没有收益不授权扩模型、删业务或再选中心。文档采用写作技能的证据区分规范；契约与结果分别保存，不覆盖旧实验。
