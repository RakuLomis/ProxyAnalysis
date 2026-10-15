# 概率核引导分类敏感度正则实验报告

日期：2026年10月5日。原G系列冻结不变。

本轮完成已登记的嵌套内容评价。真配核正则的12项主比较中，1项校正区间完全大于0，0项完全小于0；其余区间包含0。KSR2在20个外层部署折角色中有6个选择零权重。

若某部署仅有点估计改善或区间包含零，不能升级为该部署已建立额外收益；也不能把不同臂选择不同t的结果全部归因于矩阵方向。

唯一通过校正的比较是VLESS的KSR2减KSR4，F1差为0.046128，校正区间为[0.004929, 0.116859]。没有任何部署建立KSR2优于公平调参L2或匿名组核的校正证据，因此不能主张本轮已经验证了精确配对的独立分类增量。

KSR2部署等权平均F1为0.814133，略高于KSR1的0.812449，但合并CE为0.778291，高于KSR1的0.761202；Brier也为0.302104对0.299842。F1点估计改善不代表概率质量全面改善，部署等权平均差也没有在本轮被另设为显著性检验终点。

## 研究问题与已冻结前序结果

固定概率分类G4虽然优于入口原样和组级对照，却显著弱于充分post判别模型。本轮不再把核变成固定类别分布，而让核估计的条件波动几何约束自由训练的96维post LR。研究问题是这种结构能否优于有同样四候选选择预算的普通L2、匿名组核和单侧重复变化，而非必须超过旧G4。

## 数据与任务范围

四个已见部署SS、VLESS、Trojan、VMess，共23,566对合格排他TCP连接、480访问、30内容、六业务。每部署每内容四重复，每类五内容。部署连接数分别5,608、5,957、5,919、6,082。AnyTLS和Hy2不在本轮同粒度实验中。

外层五个全局内容折，每折24训练内容96访问与6测试内容24访问。每个外层训练区再以其余四个原折轮流作为验证：18训练内容72访问、6验证内容24访问。跨部署的相同内容、全部重复、双侧及内部连接整体划分。登记实体未跨折；这不等于完整历史TCP epoch的普遍重建证明。

标签顺序为：

1. `bing.com::search_results_view`
2. `developer.mozilla.org::document_view`
3. `github.com::repository_view`
4. `wikipedia.org::article_view`
5. `youtube.com::search_results_view`
6. `youtube.com::video_playback`

## 表示与预处理

每访问汇聚十个连接特征的固定箱频率，字节特征九箱、计数特征十箱，共96维。W/U上下行、P/E上下行、FR_packet_runs与R_unique_zero_runs保持前序定义，后两者没有互相替换。字节边界为1、256、1024、4096、16384、65536、262144、1048576；计数边界为1、2、3、4、8、16、32、64、128，right查箱，零独立且顶部开放。

标准化均值和总体标准差只拟合允许训练post访问，常数维尺度设1，不删除维度。分类器六类权重96×6和六偏置，共582参数。没有IP、端口、SNI、URL、业务真值、内容ID或协议身份数值编码；模型按已知部署路由独立拟合，不是统一未知协议模型。

## 核矩阵与损失

连接质量为 $1/(r_u n_v)$，内容等权、内容内访问等权、访问内连接等权。入口频率nu不平滑，M1与M2均保持alpha=beta=1。M2只读独立打乱的匿名单侧包，保留内容及质量，移除pair/session/carrier/logical身份。

$\Gamma_j=\mathrm{diag}(\nu_j^T K_j)-K_j^T\mathrm{diag}(\nu_j)K_j$，边际来自同一nu和K。八个W/U/P/E块权重1/12，两个交互块1/6。按 $D^{-1}\Gamma_hD^{-1}$ 转换，再整体trace归一到96，不逐块归一。post重复控制同样十块，按训练内容四访问残差总体方差计算，分母4，不引入跨特征协方差。

额外项为 $\lambda\|P_6\Theta L\|_F^2/5$。t仅为0、0.25、1、4，lambda为0、0.000625、0.0025、0.01。基本loss为平均CE加0.0005倍权重平方和，偏置不惩罚。普通L2 rho为0.001、0.00125、0.002、0.005。零候选直接执行原目标分支。

CUDA上的PSD因子按 $q=\sqrt k$、$L_a=\mathrm{diag}(q)(I-qq^T)$ 构造。QR仅把因子压缩到96列，保存压缩前因子与误差；没有用特征值截断掩盖非PSD。经验未平滑核只作描述，没有另设分类臂。

Gamma是分类敏感度先验，不是已验证的访问级噪声协方差或合法TCP生成器；二次项也不等于期望CE。共同trace归一丢弃总体波动强度，平滑可产生并放大小幅波动。严格正核理论rank86不等于观测了86种代理噪声。

## 方法与资源公平性

| 臂 | 方法 | 选择规则 | 训练资源 |
| --- | --- | --- | --- |
| KSR0 | 原固定G1复现 | 无选择 | 完整训练post及标签 |
| KSR1 | 普通L2 | 四候选独立内层选择 | 相同post及标签 |
| KSR2 | 真配核结构正则 | 相同四候选 | 另有训练pre及精确对应 |
| KSR3 | 匿名内容组核结构正则 | 相同四候选 | 另有同内容两侧及质量，无实例身份 |
| KSR4 | post重复块正则 | 相同四候选 | 训练内容分组，四post重复 |

## 嵌套选择与优化配置

每个方法以四内层合并96访问的完整六类macro F1选t，差距不超过1e-12时选最小t。CE/Brier不参与选择。每内层重新估计nu、核、尺度和重复矩阵，不复用见过验证内容的旧外层核；封存80条选择后才拟合选定外层方法。没有生成外层四候选性能曲线。

所有拟合、矩阵计算和推理均为Pytorch312 CUDA float64、关闭TF32、确定性算法。LR从零初始化，LBFGS max_iter=500、tolerance_grad=1e-9、tolerance_change=1e-12、strong_wolfe。停止可以由目标变化触发，不要求最终梯度全部小于1e-9。

| 阶段 | 独立拟合数 | 拟合计时合计秒 | 触及500迭代数 | 最大最终梯度 |
| --- | --- | --- | --- | --- |
| 内层 | 1040 | 1391.943774 | 0 | 1.655109e-7 |
| 外层含零参照 | 75 | 93.537223 | 0 | 1.494975e-7 |

## 零权重复现与工程资格

20个原G1零重放均通过预登记容差：目标1e-12、梯度1e-10、概率1e-8且类别完全一致。实际最大概率误差为0.0。人工矩阵测试和最终SHA、依赖、模型重载验证均通过。

首个内层核任务曾因CUDA加权bincount不支持严格确定性而停止。修复在任何真实内层核或正权重模型产生前完成，改用相同公式的CUDA float64 one-hot加权求和，保留原代码、原契约和显式修复附记；没有改动科学候选、质量、平滑或容差。详见[工程说明](engineering-note.md)。

最终推理仅加载冻结582参数模型、训练尺度和post查询，不加载pre、Gamma或K。标签在候选/最终预测封存之后由独立评分或选择进程读取。记录读取白名单不是OS级安全沙箱；共同资格和父访问范围仍来自双侧离线关联。

## 外层总体结果

| protocol | arm | visits | F1 | accuracy | CE | Brier |
| --- | --- | --- | --- | --- | --- | --- |
| shadowsocks | KSR0 | 120 | 0.852836 | 0.850000 | 0.651379 | 0.237950 |
| shadowsocks | KSR1 | 120 | 0.852144 | 0.850000 | 0.583730 | 0.226160 |
| shadowsocks | KSR2 | 120 | 0.842329 | 0.841667 | 0.637390 | 0.236673 |
| shadowsocks | KSR3 | 120 | 0.852144 | 0.850000 | 0.653064 | 0.236237 |
| shadowsocks | KSR4 | 120 | 0.835003 | 0.833333 | 0.517546 | 0.223583 |
| trojan | KSR0 | 120 | 0.822704 | 0.825000 | 0.732356 | 0.273935 |
| trojan | KSR1 | 120 | 0.831921 | 0.833333 | 0.663361 | 0.262865 |
| trojan | KSR2 | 120 | 0.820938 | 0.825000 | 0.666653 | 0.263400 |
| trojan | KSR3 | 120 | 0.821946 | 0.825000 | 0.690705 | 0.266047 |
| trojan | KSR4 | 120 | 0.815382 | 0.816667 | 0.683625 | 0.279657 |
| vless | KSR0 | 120 | 0.808583 | 0.808333 | 0.900850 | 0.322152 |
| vless | KSR1 | 120 | 0.799486 | 0.800000 | 0.750140 | 0.315853 |
| vless | KSR2 | 120 | 0.816538 | 0.816667 | 0.752867 | 0.309275 |
| vless | KSR3 | 120 | 0.799812 | 0.800000 | 0.800511 | 0.318992 |
| vless | KSR4 | 120 | 0.770410 | 0.766667 | 0.966416 | 0.365197 |
| vmess | KSR0 | 120 | 0.759006 | 0.758333 | 1.203157 | 0.413686 |
| vmess | KSR1 | 120 | 0.766246 | 0.766667 | 1.047577 | 0.394490 |
| vmess | KSR2 | 120 | 0.776729 | 0.775000 | 1.056255 | 0.399066 |
| vmess | KSR3 | 120 | 0.768395 | 0.766667 | 1.089620 | 0.396527 |
| vmess | KSR4 | 120 | 0.765557 | 0.766667 | 0.972751 | 0.379879 |

| arm | protocol_equal_mean_F1 | worst_protocol_F1 |
| --- | --- | --- |
| KSR0 | 0.810782 | 0.759006 |
| KSR1 | 0.812449 | 0.766246 |
| KSR2 | 0.814133 | 0.776729 |
| KSR3 | 0.810574 | 0.768395 |
| KSR4 | 0.796588 | 0.765557 |

![四部署五臂F1](../../outputs/kernel-sensitivity-regularization-20261005/run-01/figures/protocol-F1.png)

## 预登记十二项主比较

10000次六业务分层内容bootstrap，每类五内容重采样，四重复及全部部署随内容抽取，共用索引。普通95%区间与12项Bonferroni家族对应的99.583333%边际区间都报告。区间条件于已选择固定模型，未重做嵌套拟合，不是外部验证或研究者盲测。区间跨零不是等效证明。

| protocol | comparison | point | lo95 | hi95 | family_lo | family_hi | family_positive | family_negative | family_size |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| shadowsocks | KSR2-KSR1 | -0.009816 | -0.028012 | 0.000000 | -0.037037 | 0.000000 | False | False | 12 |
| shadowsocks | KSR2-KSR3 | -0.009816 | -0.028012 | 0.000000 | -0.037037 | 0.000000 | False | False | 12 |
| shadowsocks | KSR2-KSR4 | 0.007326 | -0.018860 | 0.035999 | -0.029061 | 0.052777 | False | False | 12 |
| vless | KSR2-KSR1 | 0.017052 | -0.015010 | 0.056334 | -0.025056 | 0.077069 | False | False | 12 |
| vless | KSR2-KSR3 | 0.016726 | -0.008344 | 0.039934 | -0.018064 | 0.046499 | False | False | 12 |
| vless | KSR2-KSR4 | 0.046128 | 0.014077 | 0.089743 | 0.004929 | 0.116859 | True | False | 12 |
| trojan | KSR2-KSR1 | -0.010983 | -0.037736 | 0.015635 | -0.047108 | 0.025037 | False | False | 12 |
| trojan | KSR2-KSR3 | -0.001008 | -0.020778 | 0.018693 | -0.035028 | 0.032591 | False | False | 12 |
| trojan | KSR2-KSR4 | 0.005556 | -0.026978 | 0.039501 | -0.038633 | 0.055686 | False | False | 12 |
| vmess | KSR2-KSR1 | 0.010483 | -0.000879 | 0.027499 | -0.002492 | 0.034385 | False | False | 12 |
| vmess | KSR2-KSR3 | 0.008333 | 0.000000 | 0.024505 | 0.000000 | 0.032182 | False | False | 12 |
| vmess | KSR2-KSR4 | 0.011172 | -0.027585 | 0.045612 | -0.046944 | 0.059027 | False | False | 12 |

![主比较校正区间](../../outputs/kernel-sensitivity-regularization-20261005/run-01/figures/main-contrasts.png)

## 全部内层强度选择

| arm | t | roles |
| --- | --- | --- |
| KSR1 | 0.000000 | 6 |
| KSR1 | 1.000000 | 4 |
| KSR1 | 4.000000 | 10 |
| KSR2 | 0.000000 | 6 |
| KSR2 | 0.250000 | 5 |
| KSR2 | 1.000000 | 4 |
| KSR2 | 4.000000 | 5 |
| KSR3 | 0.000000 | 8 |
| KSR3 | 0.250000 | 3 |
| KSR3 | 1.000000 | 5 |
| KSR3 | 4.000000 | 4 |
| KSR4 | 0.000000 | 5 |
| KSR4 | 0.250000 | 3 |
| KSR4 | 1.000000 | 2 |
| KSR4 | 4.000000 | 10 |

| arm | inner_F1 | outer | protocol | t |
| --- | --- | --- | --- | --- |
| KSR1 | 0.790557 | 0 | shadowsocks | 4.000000 |
| KSR2 | 0.770355 | 0 | shadowsocks | 0.250000 |
| KSR3 | 0.760430 | 0 | shadowsocks | 0.000000 |
| KSR4 | 0.772105 | 0 | shadowsocks | 1.000000 |
| KSR1 | 0.823699 | 1 | shadowsocks | 4.000000 |
| KSR2 | 0.806728 | 1 | shadowsocks | 0.250000 |
| KSR3 | 0.806728 | 1 | shadowsocks | 0.250000 |
| KSR4 | 0.815644 | 1 | shadowsocks | 4.000000 |
| KSR1 | 0.865103 | 2 | shadowsocks | 0.000000 |
| KSR2 | 0.865957 | 2 | shadowsocks | 0.250000 |
| KSR3 | 0.865103 | 2 | shadowsocks | 0.000000 |
| KSR4 | 0.866629 | 2 | shadowsocks | 4.000000 |
| KSR1 | 0.788938 | 3 | shadowsocks | 4.000000 |
| KSR2 | 0.788131 | 3 | shadowsocks | 0.000000 |
| KSR3 | 0.788131 | 3 | shadowsocks | 0.000000 |
| KSR4 | 0.790560 | 3 | shadowsocks | 4.000000 |
| KSR1 | 0.792939 | 4 | shadowsocks | 0.000000 |
| KSR2 | 0.794332 | 4 | shadowsocks | 0.250000 |
| KSR3 | 0.794332 | 4 | shadowsocks | 0.250000 |
| KSR4 | 0.792939 | 4 | shadowsocks | 0.000000 |
| KSR1 | 0.747688 | 0 | trojan | 0.000000 |
| KSR2 | 0.747688 | 0 | trojan | 0.000000 |
| KSR3 | 0.747688 | 0 | trojan | 0.000000 |
| KSR4 | 0.747783 | 0 | trojan | 0.250000 |
| KSR1 | 0.809021 | 1 | trojan | 1.000000 |
| KSR2 | 0.798003 | 1 | trojan | 0.000000 |
| KSR3 | 0.798003 | 1 | trojan | 0.000000 |
| KSR4 | 0.798003 | 1 | trojan | 0.000000 |
| KSR1 | 0.760104 | 2 | trojan | 4.000000 |
| KSR2 | 0.731291 | 2 | trojan | 0.000000 |
| KSR3 | 0.748979 | 2 | trojan | 4.000000 |
| KSR4 | 0.771828 | 2 | trojan | 4.000000 |
| KSR1 | 0.811805 | 3 | trojan | 4.000000 |
| KSR2 | 0.832559 | 3 | trojan | 4.000000 |
| KSR3 | 0.833717 | 3 | trojan | 4.000000 |
| KSR4 | 0.841804 | 3 | trojan | 4.000000 |
| KSR1 | 0.820586 | 4 | trojan | 1.000000 |
| KSR2 | 0.863725 | 4 | trojan | 4.000000 |
| KSR3 | 0.843028 | 4 | trojan | 1.000000 |
| KSR4 | 0.831512 | 4 | trojan | 4.000000 |
| KSR1 | 0.781036 | 0 | vless | 4.000000 |
| KSR2 | 0.791188 | 0 | vless | 4.000000 |
| KSR3 | 0.780947 | 0 | vless | 1.000000 |
| KSR4 | 0.779511 | 0 | vless | 0.250000 |
| KSR1 | 0.753524 | 1 | vless | 1.000000 |
| KSR2 | 0.743549 | 1 | vless | 0.250000 |
| KSR3 | 0.753045 | 1 | vless | 0.250000 |
| KSR4 | 0.734748 | 1 | vless | 0.000000 |
| KSR1 | 0.716451 | 2 | vless | 0.000000 |
| KSR2 | 0.718919 | 2 | vless | 1.000000 |
| KSR3 | 0.716451 | 2 | vless | 0.000000 |
| KSR4 | 0.738729 | 2 | vless | 4.000000 |
| KSR1 | 0.763446 | 3 | vless | 4.000000 |
| KSR2 | 0.762857 | 3 | vless | 1.000000 |
| KSR3 | 0.753968 | 3 | vless | 1.000000 |
| KSR4 | 0.752105 | 3 | vless | 0.000000 |
| KSR1 | 0.735548 | 4 | vless | 4.000000 |
| KSR2 | 0.754913 | 4 | vless | 1.000000 |
| KSR3 | 0.744036 | 4 | vless | 4.000000 |
| KSR4 | 0.744384 | 4 | vless | 0.250000 |
| KSR1 | 0.751856 | 0 | vmess | 0.000000 |
| KSR2 | 0.751856 | 0 | vmess | 0.000000 |
| KSR3 | 0.759401 | 0 | vmess | 4.000000 |
| KSR4 | 0.751856 | 0 | vmess | 0.000000 |
| KSR1 | 0.730287 | 1 | vmess | 0.000000 |
| KSR2 | 0.758951 | 1 | vmess | 1.000000 |
| KSR3 | 0.752753 | 1 | vmess | 1.000000 |
| KSR4 | 0.748899 | 1 | vmess | 1.000000 |
| KSR1 | 0.761935 | 2 | vmess | 1.000000 |
| KSR2 | 0.752574 | 2 | vmess | 0.000000 |
| KSR3 | 0.752574 | 2 | vmess | 0.000000 |
| KSR4 | 0.771322 | 2 | vmess | 4.000000 |
| KSR1 | 0.728803 | 3 | vmess | 4.000000 |
| KSR2 | 0.737000 | 3 | vmess | 4.000000 |
| KSR3 | 0.738446 | 3 | vmess | 1.000000 |
| KSR4 | 0.776322 | 3 | vmess | 4.000000 |
| KSR1 | 0.770695 | 4 | vmess | 4.000000 |
| KSR2 | 0.767929 | 4 | vmess | 4.000000 |
| KSR3 | 0.760397 | 4 | vmess | 0.000000 |
| KSR4 | 0.801894 | 4 | vmess | 4.000000 |

![所选强度](../../outputs/kernel-sensitivity-regularization-20261005/run-01/figures/selection-frequency.png)

## 逐业务结果和错误变化

| protocol | arm | label | support | precision | recall | F1 |
| --- | --- | --- | --- | --- | --- | --- |
| shadowsocks | KSR0 | bing.com::search_results_view | 20 | 0.823529 | 0.700000 | 0.756757 |
| shadowsocks | KSR1 | bing.com::search_results_view | 20 | 0.823529 | 0.700000 | 0.756757 |
| shadowsocks | KSR2 | bing.com::search_results_view | 20 | 0.812500 | 0.650000 | 0.722222 |
| shadowsocks | KSR3 | bing.com::search_results_view | 20 | 0.823529 | 0.700000 | 0.756757 |
| shadowsocks | KSR4 | bing.com::search_results_view | 20 | 0.777778 | 0.700000 | 0.736842 |
| shadowsocks | KSR0 | developer.mozilla.org::document_view | 20 | 0.600000 | 0.750000 | 0.666667 |
| shadowsocks | KSR1 | developer.mozilla.org::document_view | 20 | 0.600000 | 0.750000 | 0.666667 |
| shadowsocks | KSR2 | developer.mozilla.org::document_view | 20 | 0.600000 | 0.750000 | 0.666667 |
| shadowsocks | KSR3 | developer.mozilla.org::document_view | 20 | 0.600000 | 0.750000 | 0.666667 |
| shadowsocks | KSR4 | developer.mozilla.org::document_view | 20 | 0.583333 | 0.700000 | 0.636364 |
| shadowsocks | KSR0 | github.com::repository_view | 20 | 1.000000 | 0.950000 | 0.974359 |
| shadowsocks | KSR1 | github.com::repository_view | 20 | 1.000000 | 0.950000 | 0.974359 |
| shadowsocks | KSR2 | github.com::repository_view | 20 | 0.950000 | 0.950000 | 0.950000 |
| shadowsocks | KSR3 | github.com::repository_view | 20 | 1.000000 | 0.950000 | 0.974359 |
| shadowsocks | KSR4 | github.com::repository_view | 20 | 1.000000 | 0.950000 | 0.974359 |
| shadowsocks | KSR0 | wikipedia.org::article_view | 20 | 0.789474 | 0.750000 | 0.769231 |
| shadowsocks | KSR1 | wikipedia.org::article_view | 20 | 0.833333 | 0.750000 | 0.789474 |
| shadowsocks | KSR2 | wikipedia.org::article_view | 20 | 0.833333 | 0.750000 | 0.789474 |
| shadowsocks | KSR3 | wikipedia.org::article_view | 20 | 0.833333 | 0.750000 | 0.789474 |
| shadowsocks | KSR4 | wikipedia.org::article_view | 20 | 0.777778 | 0.700000 | 0.736842 |
| shadowsocks | KSR0 | youtube.com::search_results_view | 20 | 0.950000 | 0.950000 | 0.950000 |
| shadowsocks | KSR1 | youtube.com::search_results_view | 20 | 0.950000 | 0.950000 | 0.950000 |
| shadowsocks | KSR2 | youtube.com::search_results_view | 20 | 0.950000 | 0.950000 | 0.950000 |
| shadowsocks | KSR3 | youtube.com::search_results_view | 20 | 0.950000 | 0.950000 | 0.950000 |
| shadowsocks | KSR4 | youtube.com::search_results_view | 20 | 0.950000 | 0.950000 | 0.950000 |
| shadowsocks | KSR0 | youtube.com::video_playback | 20 | 1.000000 | 1.000000 | 1.000000 |
| shadowsocks | KSR1 | youtube.com::video_playback | 20 | 0.952381 | 1.000000 | 0.975610 |
| shadowsocks | KSR2 | youtube.com::video_playback | 20 | 0.952381 | 1.000000 | 0.975610 |
| shadowsocks | KSR3 | youtube.com::video_playback | 20 | 0.952381 | 1.000000 | 0.975610 |
| shadowsocks | KSR4 | youtube.com::video_playback | 20 | 0.952381 | 1.000000 | 0.975610 |
| trojan | KSR0 | bing.com::search_results_view | 20 | 0.772727 | 0.850000 | 0.809524 |
| trojan | KSR1 | bing.com::search_results_view | 20 | 0.809524 | 0.850000 | 0.829268 |
| trojan | KSR2 | bing.com::search_results_view | 20 | 0.809524 | 0.850000 | 0.829268 |
| trojan | KSR3 | bing.com::search_results_view | 20 | 0.809524 | 0.850000 | 0.829268 |
| trojan | KSR4 | bing.com::search_results_view | 20 | 0.800000 | 0.800000 | 0.800000 |
| trojan | KSR0 | developer.mozilla.org::document_view | 20 | 0.705882 | 0.600000 | 0.648649 |
| trojan | KSR1 | developer.mozilla.org::document_view | 20 | 0.722222 | 0.650000 | 0.684211 |
| trojan | KSR2 | developer.mozilla.org::document_view | 20 | 0.687500 | 0.550000 | 0.611111 |
| trojan | KSR3 | developer.mozilla.org::document_view | 20 | 0.705882 | 0.600000 | 0.648649 |
| trojan | KSR4 | developer.mozilla.org::document_view | 20 | 0.722222 | 0.650000 | 0.684211 |
| trojan | KSR0 | github.com::repository_view | 20 | 0.950000 | 0.950000 | 0.950000 |
| trojan | KSR1 | github.com::repository_view | 20 | 0.950000 | 0.950000 | 0.950000 |
| trojan | KSR2 | github.com::repository_view | 20 | 0.950000 | 0.950000 | 0.950000 |
| trojan | KSR3 | github.com::repository_view | 20 | 0.950000 | 0.950000 | 0.950000 |
| trojan | KSR4 | github.com::repository_view | 20 | 1.000000 | 0.950000 | 0.974359 |
| trojan | KSR0 | wikipedia.org::article_view | 20 | 0.800000 | 0.800000 | 0.800000 |
| trojan | KSR1 | wikipedia.org::article_view | 20 | 0.800000 | 0.800000 | 0.800000 |
| trojan | KSR2 | wikipedia.org::article_view | 20 | 0.761905 | 0.800000 | 0.780488 |
| trojan | KSR3 | wikipedia.org::article_view | 20 | 0.833333 | 0.750000 | 0.789474 |
| trojan | KSR4 | wikipedia.org::article_view | 20 | 0.750000 | 0.750000 | 0.750000 |
| trojan | KSR0 | youtube.com::search_results_view | 20 | 0.857143 | 0.900000 | 0.878049 |
| trojan | KSR1 | youtube.com::search_results_view | 20 | 0.857143 | 0.900000 | 0.878049 |
| trojan | KSR2 | youtube.com::search_results_view | 20 | 0.863636 | 0.950000 | 0.904762 |
| trojan | KSR3 | youtube.com::search_results_view | 20 | 0.863636 | 0.950000 | 0.904762 |
| trojan | KSR4 | youtube.com::search_results_view | 20 | 0.826087 | 0.950000 | 0.883721 |
| trojan | KSR0 | youtube.com::video_playback | 20 | 0.850000 | 0.850000 | 0.850000 |
| trojan | KSR1 | youtube.com::video_playback | 20 | 0.850000 | 0.850000 | 0.850000 |
| trojan | KSR2 | youtube.com::video_playback | 20 | 0.850000 | 0.850000 | 0.850000 |
| trojan | KSR3 | youtube.com::video_playback | 20 | 0.772727 | 0.850000 | 0.809524 |
| trojan | KSR4 | youtube.com::video_playback | 20 | 0.800000 | 0.800000 | 0.800000 |
| vless | KSR0 | bing.com::search_results_view | 20 | 0.842105 | 0.800000 | 0.820513 |
| vless | KSR1 | bing.com::search_results_view | 20 | 0.800000 | 0.800000 | 0.800000 |
| vless | KSR2 | bing.com::search_results_view | 20 | 0.888889 | 0.800000 | 0.842105 |
| vless | KSR3 | bing.com::search_results_view | 20 | 0.761905 | 0.800000 | 0.780488 |
| vless | KSR4 | bing.com::search_results_view | 20 | 0.777778 | 0.700000 | 0.736842 |
| vless | KSR0 | developer.mozilla.org::document_view | 20 | 0.800000 | 0.800000 | 0.800000 |
| vless | KSR1 | developer.mozilla.org::document_view | 20 | 0.777778 | 0.700000 | 0.736842 |
| vless | KSR2 | developer.mozilla.org::document_view | 20 | 0.772727 | 0.850000 | 0.809524 |
| vless | KSR3 | developer.mozilla.org::document_view | 20 | 0.736842 | 0.700000 | 0.717949 |
| vless | KSR4 | developer.mozilla.org::document_view | 20 | 0.636364 | 0.700000 | 0.666667 |
| vless | KSR0 | github.com::repository_view | 20 | 0.894737 | 0.850000 | 0.871795 |
| vless | KSR1 | github.com::repository_view | 20 | 0.894737 | 0.850000 | 0.871795 |
| vless | KSR2 | github.com::repository_view | 20 | 0.894737 | 0.850000 | 0.871795 |
| vless | KSR3 | github.com::repository_view | 20 | 0.944444 | 0.850000 | 0.894737 |
| vless | KSR4 | github.com::repository_view | 20 | 1.000000 | 0.850000 | 0.918919 |
| vless | KSR0 | wikipedia.org::article_view | 20 | 0.652174 | 0.750000 | 0.697674 |
| vless | KSR1 | wikipedia.org::article_view | 20 | 0.681818 | 0.750000 | 0.714286 |
| vless | KSR2 | wikipedia.org::article_view | 20 | 0.681818 | 0.750000 | 0.714286 |
| vless | KSR3 | wikipedia.org::article_view | 20 | 0.714286 | 0.750000 | 0.731707 |
| vless | KSR4 | wikipedia.org::article_view | 20 | 0.583333 | 0.700000 | 0.636364 |
| vless | KSR0 | youtube.com::search_results_view | 20 | 0.823529 | 0.700000 | 0.756757 |
| vless | KSR1 | youtube.com::search_results_view | 20 | 0.789474 | 0.750000 | 0.769231 |
| vless | KSR2 | youtube.com::search_results_view | 20 | 0.823529 | 0.700000 | 0.756757 |
| vless | KSR3 | youtube.com::search_results_view | 20 | 0.789474 | 0.750000 | 0.769231 |
| vless | KSR4 | youtube.com::search_results_view | 20 | 0.777778 | 0.700000 | 0.736842 |
| vless | KSR0 | youtube.com::video_playback | 20 | 0.863636 | 0.950000 | 0.904762 |
| vless | KSR1 | youtube.com::video_playback | 20 | 0.863636 | 0.950000 | 0.904762 |
| vless | KSR2 | youtube.com::video_playback | 20 | 0.863636 | 0.950000 | 0.904762 |
| vless | KSR3 | youtube.com::video_playback | 20 | 0.863636 | 0.950000 | 0.904762 |
| vless | KSR4 | youtube.com::video_playback | 20 | 0.904762 | 0.950000 | 0.926829 |
| vmess | KSR0 | bing.com::search_results_view | 20 | 0.750000 | 0.750000 | 0.750000 |
| vmess | KSR1 | bing.com::search_results_view | 20 | 0.800000 | 0.800000 | 0.800000 |
| vmess | KSR2 | bing.com::search_results_view | 20 | 0.761905 | 0.800000 | 0.780488 |
| vmess | KSR3 | bing.com::search_results_view | 20 | 0.750000 | 0.750000 | 0.750000 |
| vmess | KSR4 | bing.com::search_results_view | 20 | 0.823529 | 0.700000 | 0.756757 |
| vmess | KSR0 | developer.mozilla.org::document_view | 20 | 0.647059 | 0.550000 | 0.594595 |
| vmess | KSR1 | developer.mozilla.org::document_view | 20 | 0.687500 | 0.550000 | 0.611111 |
| vmess | KSR2 | developer.mozilla.org::document_view | 20 | 0.705882 | 0.600000 | 0.648649 |
| vmess | KSR3 | developer.mozilla.org::document_view | 20 | 0.705882 | 0.600000 | 0.648649 |
| vmess | KSR4 | developer.mozilla.org::document_view | 20 | 0.631579 | 0.600000 | 0.615385 |
| vmess | KSR0 | github.com::repository_view | 20 | 0.850000 | 0.850000 | 0.850000 |
| vmess | KSR1 | github.com::repository_view | 20 | 0.850000 | 0.850000 | 0.850000 |
| vmess | KSR2 | github.com::repository_view | 20 | 0.894737 | 0.850000 | 0.871795 |
| vmess | KSR3 | github.com::repository_view | 20 | 0.894737 | 0.850000 | 0.871795 |
| vmess | KSR4 | github.com::repository_view | 20 | 0.894737 | 0.850000 | 0.871795 |
| vmess | KSR0 | wikipedia.org::article_view | 20 | 0.583333 | 0.700000 | 0.636364 |
| vmess | KSR1 | wikipedia.org::article_view | 20 | 0.583333 | 0.700000 | 0.636364 |
| vmess | KSR2 | wikipedia.org::article_view | 20 | 0.583333 | 0.700000 | 0.636364 |
| vmess | KSR3 | wikipedia.org::article_view | 20 | 0.583333 | 0.700000 | 0.636364 |
| vmess | KSR4 | wikipedia.org::article_view | 20 | 0.619048 | 0.650000 | 0.634146 |
| vmess | KSR0 | youtube.com::search_results_view | 20 | 0.800000 | 0.800000 | 0.800000 |
| vmess | KSR1 | youtube.com::search_results_view | 20 | 0.800000 | 0.800000 | 0.800000 |
| vmess | KSR2 | youtube.com::search_results_view | 20 | 0.800000 | 0.800000 | 0.800000 |
| vmess | KSR3 | youtube.com::search_results_view | 20 | 0.761905 | 0.800000 | 0.780488 |
| vmess | KSR4 | youtube.com::search_results_view | 20 | 0.782609 | 0.900000 | 0.837209 |
| vmess | KSR0 | youtube.com::video_playback | 20 | 0.947368 | 0.900000 | 0.923077 |
| vmess | KSR1 | youtube.com::video_playback | 20 | 0.900000 | 0.900000 | 0.900000 |
| vmess | KSR2 | youtube.com::video_playback | 20 | 0.947368 | 0.900000 | 0.923077 |
| vmess | KSR3 | youtube.com::video_playback | 20 | 0.947368 | 0.900000 | 0.923077 |
| vmess | KSR4 | youtube.com::video_playback | 20 | 0.857143 | 0.900000 | 0.878049 |

| protocol | comparison | repaired_errors | added_errors | changed_predictions |
| --- | --- | --- | --- | --- |
| shadowsocks | KSR2-KSR0 | 0 | 1 | 2 |
| shadowsocks | KSR2-KSR1 | 0 | 1 | 1 |
| shadowsocks | KSR2-KSR3 | 0 | 1 | 1 |
| shadowsocks | KSR2-KSR4 | 2 | 1 | 3 |
| vless | KSR2-KSR0 | 1 | 0 | 2 |
| vless | KSR2-KSR1 | 3 | 1 | 6 |
| vless | KSR2-KSR3 | 3 | 1 | 6 |
| vless | KSR2-KSR4 | 6 | 0 | 11 |
| trojan | KSR2-KSR0 | 1 | 1 | 3 |
| trojan | KSR2-KSR1 | 1 | 2 | 4 |
| trojan | KSR2-KSR3 | 1 | 1 | 4 |
| trojan | KSR2-KSR4 | 3 | 2 | 6 |
| vmess | KSR2-KSR0 | 2 | 0 | 2 |
| vmess | KSR2-KSR1 | 1 | 0 | 3 |
| vmess | KSR2-KSR3 | 1 | 0 | 1 |
| vmess | KSR2-KSR4 | 3 | 2 | 8 |

![逐业务recall](../../outputs/kernel-sensitivity-regularization-20261005/run-01/figures/class-recall.png)

完整内容错误、访问级修复与新增错误及六类混淆矩阵保存在scores目录，不以困难YouTube业务退化为由删类或重选队列。

## 训练矩阵尺度和谱

下表按外层角色报告原生标准化与整体trace归一后的谱。原生尺度不是归一后的惩罚强度，各族实际trace也不会因登记权重而自动一致。

| outer | protocol | arm | coordinates | trace_multiplier | smoothing_difference_Frobenius | effective_rank | max_eigenvalue | min_eigenvalue | numerical_rank | trace |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | shadowsocks | KSR2 | normalized | 0.261478 | 43.863867 | 58.339785 | 6.411352 | -0.000000 | 86 | 96.000000 |
| 0 | shadowsocks | KSR2 | raw | 0.261478 | 43.863867 | 58.339785 | 24.519696 | -0.000000 | 86 | 367.144227 |
| 0 | shadowsocks | KSR3 | normalized | 0.151802 | 43.863867 | 64.018970 | 4.649096 | -0.000000 | 86 | 96.000000 |
| 0 | shadowsocks | KSR3 | raw | 0.151802 | 43.863867 | 64.018970 | 30.626097 | -0.000000 | 86 | 632.403627 |
| 0 | shadowsocks | KSR4 | normalized | 18.126681 | 43.863867 | 58.751667 | 4.563957 | -0.000000 | 76 | 96.000000 |
| 0 | shadowsocks | KSR4 | raw | 18.126681 | 43.863867 | 58.751667 | 0.251781 | -0.000000 | 76 | 5.296060 |
| 0 | shadowsocks | empirical | normalized | 0.645488 | 43.863867 | 34.295980 | 8.513653 | -0.000000 | 60 | 96.000000 |
| 0 | shadowsocks | empirical | raw | 0.645488 | 43.863867 | 34.295980 | 13.189490 | -0.000000 | 60 | 148.724759 |
| 1 | shadowsocks | KSR2 | normalized | 0.272216 | 42.885067 | 58.614177 | 6.684615 | -0.000000 | 86 | 96.000000 |
| 1 | shadowsocks | KSR2 | raw | 0.272216 | 42.885067 | 58.614177 | 24.556318 | -0.000000 | 86 | 352.661540 |
| 1 | shadowsocks | KSR3 | normalized | 0.158450 | 42.885067 | 64.489456 | 4.858488 | -0.000000 | 86 | 96.000000 |
| 1 | shadowsocks | KSR3 | raw | 0.158450 | 42.885067 | 64.489456 | 30.662498 | -0.000000 | 86 | 605.867492 |
| 1 | shadowsocks | KSR4 | normalized | 17.556591 | 42.885067 | 57.938387 | 4.781061 | -0.000000 | 77 | 96.000000 |
| 1 | shadowsocks | KSR4 | raw | 17.556591 | 42.885067 | 57.938387 | 0.272323 | -0.000000 | 77 | 5.468032 |
| 1 | shadowsocks | empirical | normalized | 0.651561 | 42.885067 | 36.479891 | 6.923242 | -0.000000 | 63 | 96.000000 |
| 1 | shadowsocks | empirical | raw | 0.651561 | 42.885067 | 36.479891 | 10.625621 | -0.000000 | 63 | 147.338441 |
| 2 | shadowsocks | KSR2 | normalized | 0.302823 | 27.297337 | 62.959952 | 3.795224 | -0.000000 | 86 | 96.000000 |
| 2 | shadowsocks | KSR2 | raw | 0.302823 | 27.297337 | 62.959952 | 12.532818 | -0.000000 | 86 | 317.017006 |
| 2 | shadowsocks | KSR3 | normalized | 0.170477 | 27.297337 | 66.265517 | 3.032527 | -0.000000 | 86 | 96.000000 |
| 2 | shadowsocks | KSR3 | raw | 0.170477 | 27.297337 | 66.265517 | 17.788447 | -0.000000 | 86 | 563.124748 |
| 2 | shadowsocks | KSR4 | normalized | 18.498983 | 27.297337 | 57.620653 | 4.839367 | -0.000000 | 75 | 96.000000 |
| 2 | shadowsocks | KSR4 | raw | 18.498983 | 27.297337 | 57.620653 | 0.261602 | -0.000000 | 75 | 5.189475 |
| 2 | shadowsocks | empirical | normalized | 0.664516 | 27.297337 | 35.739884 | 7.468051 | -0.000000 | 63 | 96.000000 |
| 2 | shadowsocks | empirical | raw | 0.664516 | 27.297337 | 35.739884 | 11.238335 | -0.000000 | 63 | 144.466099 |
| 3 | shadowsocks | KSR2 | normalized | 0.248544 | 48.232972 | 56.993962 | 6.064263 | -0.000000 | 86 | 96.000000 |
| 3 | shadowsocks | KSR2 | raw | 0.248544 | 48.232972 | 56.993962 | 24.399168 | -0.000000 | 86 | 386.249768 |
| 3 | shadowsocks | KSR3 | normalized | 0.148246 | 48.232972 | 64.192749 | 4.522061 | -0.000000 | 86 | 96.000000 |
| 3 | shadowsocks | KSR3 | raw | 0.148246 | 48.232972 | 64.192749 | 30.503805 | -0.000000 | 86 | 647.573103 |
| 3 | shadowsocks | KSR4 | normalized | 17.629874 | 48.232972 | 58.375479 | 4.775469 | -0.000000 | 77 | 96.000000 |
| 3 | shadowsocks | KSR4 | raw | 17.629874 | 48.232972 | 58.375479 | 0.270874 | -0.000000 | 77 | 5.445303 |
| 3 | shadowsocks | empirical | normalized | 0.644289 | 48.232972 | 36.859023 | 6.695627 | -0.000000 | 62 | 96.000000 |
| 3 | shadowsocks | empirical | raw | 0.644289 | 48.232972 | 36.859023 | 10.392277 | -0.000000 | 62 | 149.001516 |
| 4 | shadowsocks | KSR2 | normalized | 0.247040 | 49.192490 | 56.588034 | 6.051261 | -0.000000 | 86 | 96.000000 |
| 4 | shadowsocks | KSR2 | raw | 0.247040 | 49.192490 | 56.588034 | 24.495037 | -0.000000 | 86 | 388.600564 |
| 4 | shadowsocks | KSR3 | normalized | 0.148631 | 49.192490 | 63.372896 | 4.548698 | -0.000000 | 86 | 96.000000 |
| 4 | shadowsocks | KSR3 | raw | 0.148631 | 49.192490 | 63.372896 | 30.604064 | -0.000000 | 86 | 645.896951 |
| 4 | shadowsocks | KSR4 | normalized | 17.670572 | 49.192490 | 58.708121 | 4.797083 | -0.000000 | 77 | 96.000000 |
| 4 | shadowsocks | KSR4 | raw | 17.670572 | 49.192490 | 58.708121 | 0.271473 | -0.000000 | 77 | 5.432761 |
| 4 | shadowsocks | empirical | normalized | 0.636227 | 49.192490 | 35.978191 | 7.888044 | -0.000000 | 63 | 96.000000 |
| 4 | shadowsocks | empirical | raw | 0.636227 | 49.192490 | 35.978191 | 12.398153 | -0.000000 | 63 | 150.889466 |
| 0 | trojan | KSR2 | normalized | 0.190406 | 63.540256 | 46.476800 | 5.852599 | -0.000000 | 86 | 96.000000 |
| 0 | trojan | KSR2 | raw | 0.190406 | 63.540256 | 46.476800 | 30.737482 | -0.000000 | 86 | 504.185950 |
| 0 | trojan | KSR3 | normalized | 0.136731 | 63.540256 | 51.860983 | 5.127990 | -0.000000 | 86 | 96.000000 |
| 0 | trojan | KSR3 | raw | 0.136731 | 63.540256 | 51.860983 | 37.504345 | -0.000000 | 86 | 702.110738 |
| 0 | trojan | KSR4 | normalized | 20.524302 | 63.540256 | 45.608213 | 6.809212 | -0.000000 | 63 | 96.000000 |
| 0 | trojan | KSR4 | raw | 20.524302 | 63.540256 | 45.608213 | 0.331763 | -0.000000 | 63 | 4.677382 |
| 0 | trojan | empirical | normalized | 0.479939 | 63.540256 | 42.291332 | 4.805124 | -0.000000 | 55 | 96.000000 |
| 0 | trojan | empirical | raw | 0.479939 | 63.540256 | 42.291332 | 10.011939 | -0.000000 | 55 | 200.025235 |
| 1 | trojan | KSR2 | normalized | 0.116007 | 163.098127 | 29.576452 | 10.250462 | -0.000000 | 86 | 96.000000 |
| 1 | trojan | KSR2 | raw | 0.116007 | 163.098127 | 29.576452 | 88.360757 | -0.000000 | 86 | 827.536608 |
| 1 | trojan | KSR3 | normalized | 0.092292 | 163.098127 | 38.200314 | 8.139958 | -0.000000 | 86 | 96.000000 |
| 1 | trojan | KSR3 | raw | 0.092292 | 163.098127 | 38.200314 | 88.197914 | -0.000000 | 86 | 1040.177336 |
| 1 | trojan | KSR4 | normalized | 21.639023 | 163.098127 | 43.133377 | 8.002135 | -0.000000 | 61 | 96.000000 |
| 1 | trojan | KSR4 | raw | 21.639023 | 163.098127 | 43.133377 | 0.369801 | -0.000000 | 61 | 4.436429 |
| 1 | trojan | empirical | normalized | 0.451973 | 163.098127 | 39.228707 | 6.088212 | -0.000000 | 53 | 96.000000 |
| 1 | trojan | empirical | raw | 0.451973 | 163.098127 | 39.228707 | 13.470313 | -0.000000 | 53 | 212.402286 |
| 2 | trojan | KSR2 | normalized | 0.181163 | 64.846925 | 47.084090 | 5.549543 | -0.000000 | 86 | 96.000000 |
| 2 | trojan | KSR2 | raw | 0.181163 | 64.846925 | 47.084090 | 30.632865 | -0.000000 | 86 | 529.909432 |
| 2 | trojan | KSR3 | normalized | 0.130416 | 64.846925 | 52.346621 | 4.557214 | -0.000000 | 86 | 96.000000 |
| 2 | trojan | KSR3 | raw | 0.130416 | 64.846925 | 52.346621 | 34.943591 | -0.000000 | 86 | 736.104306 |
| 2 | trojan | KSR4 | normalized | 20.429078 | 64.846925 | 46.465248 | 6.954175 | -0.000000 | 64 | 96.000000 |
| 2 | trojan | KSR4 | raw | 20.429078 | 64.846925 | 46.465248 | 0.340406 | -0.000000 | 64 | 4.699184 |
| 2 | trojan | empirical | normalized | 0.494585 | 64.846925 | 43.625056 | 4.494090 | -0.000000 | 56 | 96.000000 |
| 2 | trojan | empirical | raw | 0.494585 | 64.846925 | 43.625056 | 9.086586 | -0.000000 | 56 | 194.102109 |
| 3 | trojan | KSR2 | normalized | 0.161468 | 99.145688 | 41.001715 | 9.522001 | -0.000000 | 86 | 96.000000 |
| 3 | trojan | KSR2 | raw | 0.161468 | 99.145688 | 41.001715 | 58.971421 | -0.000000 | 86 | 594.544841 |
| 3 | trojan | KSR3 | normalized | 0.118862 | 99.145688 | 46.958146 | 8.152686 | -0.000000 | 86 | 96.000000 |
| 3 | trojan | KSR3 | raw | 0.118862 | 99.145688 | 46.958146 | 68.589269 | -0.000000 | 86 | 807.656506 |
| 3 | trojan | KSR4 | normalized | 20.565120 | 99.145688 | 47.047509 | 7.045278 | -0.000000 | 64 | 96.000000 |
| 3 | trojan | KSR4 | raw | 20.565120 | 99.145688 | 47.047509 | 0.342584 | -0.000000 | 64 | 4.668098 |
| 3 | trojan | empirical | normalized | 0.470722 | 99.145688 | 43.552283 | 4.712572 | -0.000000 | 56 | 96.000000 |
| 3 | trojan | empirical | raw | 0.470722 | 99.145688 | 43.552283 | 10.011368 | -0.000000 | 56 | 203.942019 |
| 4 | trojan | KSR2 | normalized | 0.191550 | 60.028053 | 47.452523 | 5.846764 | -0.000000 | 86 | 96.000000 |
| 4 | trojan | KSR2 | raw | 0.191550 | 60.028053 | 47.452523 | 30.523359 | -0.000000 | 86 | 501.173382 |
| 4 | trojan | KSR3 | normalized | 0.136440 | 60.028053 | 52.604168 | 4.754329 | -0.000000 | 86 | 96.000000 |
| 4 | trojan | KSR3 | raw | 0.136440 | 60.028053 | 52.604168 | 34.845660 | -0.000000 | 86 | 703.607948 |
| 4 | trojan | KSR4 | normalized | 20.182918 | 60.028053 | 46.254601 | 7.126595 | -0.000000 | 64 | 96.000000 |
| 4 | trojan | KSR4 | raw | 20.182918 | 60.028053 | 46.254601 | 0.353100 | -0.000000 | 64 | 4.756498 |
| 4 | trojan | empirical | normalized | 0.485784 | 60.028053 | 43.431275 | 4.863778 | -0.000000 | 56 | 96.000000 |
| 4 | trojan | empirical | raw | 0.485784 | 60.028053 | 43.431275 | 10.012230 | -0.000000 | 56 | 197.618823 |
| 0 | vless | KSR2 | normalized | 0.264091 | 39.201418 | 45.353667 | 6.338745 | -0.000000 | 86 | 96.000000 |
| 0 | vless | KSR2 | raw | 0.264091 | 39.201418 | 45.353667 | 24.002097 | -0.000000 | 86 | 363.510680 |
| 0 | vless | KSR3 | normalized | 0.180075 | 39.201418 | 50.163753 | 4.271673 | -0.000000 | 86 | 96.000000 |
| 0 | vless | KSR3 | raw | 0.180075 | 39.201418 | 50.163753 | 23.721637 | -0.000000 | 86 | 533.111247 |
| 0 | vless | KSR4 | normalized | 22.865752 | 39.201418 | 42.891445 | 8.022164 | -0.000000 | 58 | 96.000000 |
| 0 | vless | KSR4 | raw | 22.865752 | 39.201418 | 42.891445 | 0.350838 | -0.000000 | 58 | 4.198419 |
| 0 | vless | empirical | normalized | 0.575367 | 39.201418 | 41.893076 | 4.851932 | -0.000000 | 57 | 96.000000 |
| 0 | vless | empirical | raw | 0.575367 | 39.201418 | 41.893076 | 8.432754 | -0.000000 | 57 | 166.849908 |
| 1 | vless | KSR2 | normalized | 0.205372 | 57.472443 | 48.871759 | 5.715300 | -0.000000 | 86 | 96.000000 |
| 1 | vless | KSR2 | raw | 0.205372 | 57.472443 | 48.871759 | 27.829016 | -0.000000 | 86 | 467.444475 |
| 1 | vless | KSR3 | normalized | 0.142717 | 57.472443 | 53.521302 | 4.919441 | -0.000000 | 86 | 96.000000 |
| 1 | vless | KSR3 | raw | 0.142717 | 57.472443 | 53.521302 | 34.469931 | -0.000000 | 86 | 672.660399 |
| 1 | vless | KSR4 | normalized | 20.356628 | 57.472443 | 47.988878 | 7.348370 | -0.000000 | 64 | 96.000000 |
| 1 | vless | KSR4 | raw | 20.356628 | 57.472443 | 47.988878 | 0.360982 | -0.000000 | 64 | 4.715909 |
| 1 | vless | empirical | normalized | 0.510180 | 57.472443 | 44.768523 | 4.491804 | -0.000000 | 60 | 96.000000 |
| 1 | vless | empirical | raw | 0.510180 | 57.472443 | 44.768523 | 8.804355 | -0.000000 | 60 | 188.168938 |
| 2 | vless | KSR2 | normalized | 0.198978 | 64.074928 | 47.206169 | 5.584978 | -0.000000 | 86 | 96.000000 |
| 2 | vless | KSR2 | raw | 0.198978 | 64.074928 | 47.206169 | 28.068352 | -0.000000 | 86 | 482.465981 |
| 2 | vless | KSR3 | normalized | 0.141260 | 64.074928 | 53.045035 | 4.903317 | -0.000000 | 86 | 96.000000 |
| 2 | vless | KSR3 | raw | 0.141260 | 64.074928 | 53.045035 | 34.711264 | -0.000000 | 86 | 679.597364 |
| 2 | vless | KSR4 | normalized | 19.780801 | 64.074928 | 48.406897 | 6.865847 | -0.000000 | 64 | 96.000000 |
| 2 | vless | KSR4 | raw | 19.780801 | 64.074928 | 48.406897 | 0.347097 | -0.000000 | 64 | 4.853191 |
| 2 | vless | empirical | normalized | 0.544886 | 64.074928 | 45.377916 | 4.440598 | -0.000000 | 58 | 96.000000 |
| 2 | vless | empirical | raw | 0.544886 | 64.074928 | 45.377916 | 8.149586 | -0.000000 | 58 | 176.183553 |
| 3 | vless | KSR2 | normalized | 0.210348 | 57.377451 | 48.338193 | 5.945198 | -0.000000 | 86 | 96.000000 |
| 3 | vless | KSR2 | raw | 0.210348 | 57.377451 | 48.338193 | 28.263636 | -0.000000 | 86 | 456.386655 |
| 3 | vless | KSR3 | normalized | 0.147162 | 57.377451 | 53.761645 | 5.136888 | -0.000000 | 86 | 96.000000 |
| 3 | vless | KSR3 | raw | 0.147162 | 57.377451 | 53.761645 | 34.906242 | -0.000000 | 86 | 652.340319 |
| 3 | vless | KSR4 | normalized | 19.712364 | 57.377451 | 48.764324 | 7.137316 | -0.000000 | 64 | 96.000000 |
| 3 | vless | KSR4 | raw | 19.712364 | 57.377451 | 48.764324 | 0.362073 | -0.000000 | 64 | 4.870040 |
| 3 | vless | empirical | normalized | 0.520412 | 57.377451 | 44.834007 | 4.388132 | -0.000000 | 60 | 96.000000 |
| 3 | vless | empirical | raw | 0.520412 | 57.377451 | 44.834007 | 8.432028 | -0.000000 | 60 | 184.469094 |
| 4 | vless | KSR2 | normalized | 0.128564 | 135.976763 | 33.693943 | 9.358793 | -0.000000 | 86 | 96.000000 |
| 4 | vless | KSR2 | raw | 0.128564 | 135.976763 | 33.693943 | 72.794881 | -0.000000 | 86 | 746.710428 |
| 4 | vless | KSR3 | normalized | 0.101527 | 135.976763 | 42.664840 | 7.368591 | -0.000000 | 86 | 96.000000 |
| 4 | vless | KSR3 | raw | 0.101527 | 135.976763 | 42.664840 | 72.577440 | -0.000000 | 86 | 945.558556 |
| 4 | vless | KSR4 | normalized | 20.209211 | 135.976763 | 50.195971 | 5.985026 | -0.000000 | 64 | 96.000000 |
| 4 | vless | KSR4 | raw | 20.209211 | 135.976763 | 50.195971 | 0.296153 | -0.000000 | 64 | 4.750309 |
| 4 | vless | empirical | normalized | 0.464510 | 135.976763 | 43.242710 | 5.631420 | -0.000000 | 60 | 96.000000 |
| 4 | vless | empirical | raw | 0.464510 | 135.976763 | 43.242710 | 12.123347 | -0.000000 | 60 | 206.669256 |
| 0 | vmess | KSR2 | normalized | 0.125800 | 102.311595 | 48.109746 | 7.817594 | -0.000000 | 86 | 96.000000 |
| 0 | vmess | KSR2 | raw | 0.125800 | 102.311595 | 48.109746 | 62.142995 | -0.000000 | 86 | 763.115592 |
| 0 | vmess | KSR3 | normalized | 0.100038 | 102.311595 | 54.127708 | 6.224649 | -0.000000 | 86 | 96.000000 |
| 0 | vmess | KSR3 | raw | 0.100038 | 102.311595 | 54.127708 | 62.222545 | -0.000000 | 86 | 959.630663 |
| 0 | vmess | KSR4 | normalized | 18.156104 | 102.311595 | 57.747497 | 4.641659 | -0.000000 | 70 | 96.000000 |
| 0 | vmess | KSR4 | raw | 18.156104 | 102.311595 | 57.747497 | 0.255653 | -0.000000 | 70 | 5.287478 |
| 0 | vmess | empirical | normalized | 0.359055 | 102.311595 | 49.984653 | 4.705352 | -0.000000 | 66 | 96.000000 |
| 0 | vmess | empirical | raw | 0.359055 | 102.311595 | 49.984653 | 13.104808 | -0.000000 | 66 | 267.368229 |
| 1 | vmess | KSR2 | normalized | 0.144931 | 67.961891 | 56.558645 | 4.435762 | -0.000000 | 86 | 96.000000 |
| 1 | vmess | KSR2 | raw | 0.144931 | 67.961891 | 56.558645 | 30.606087 | -0.000000 | 86 | 662.385450 |
| 1 | vmess | KSR3 | normalized | 0.112160 | 67.961891 | 61.427254 | 3.806703 | -0.000000 | 86 | 96.000000 |
| 1 | vmess | KSR3 | raw | 0.112160 | 67.961891 | 61.427254 | 33.940008 | -0.000000 | 86 | 855.921908 |
| 1 | vmess | KSR4 | normalized | 18.017433 | 67.961891 | 59.723666 | 4.296238 | -0.000000 | 72 | 96.000000 |
| 1 | vmess | KSR4 | raw | 18.017433 | 67.961891 | 59.723666 | 0.238449 | -0.000000 | 72 | 5.328173 |
| 1 | vmess | empirical | normalized | 0.344294 | 67.961891 | 52.815295 | 4.905568 | -0.000000 | 68 | 96.000000 |
| 1 | vmess | empirical | raw | 0.344294 | 67.961891 | 52.815295 | 14.248190 | -0.000000 | 68 | 278.831391 |
| 2 | vmess | KSR2 | normalized | 0.125404 | 94.880716 | 47.884282 | 6.077045 | -0.000000 | 86 | 96.000000 |
| 2 | vmess | KSR2 | raw | 0.125404 | 94.880716 | 47.884282 | 48.459718 | -0.000000 | 86 | 765.525555 |
| 2 | vmess | KSR3 | normalized | 0.100345 | 94.880716 | 53.989691 | 4.791403 | -0.000000 | 86 | 96.000000 |
| 2 | vmess | KSR3 | raw | 0.100345 | 94.880716 | 53.989691 | 47.749259 | -0.000000 | 86 | 956.698647 |
| 2 | vmess | KSR4 | normalized | 19.959645 | 94.880716 | 55.023024 | 4.628987 | -0.000000 | 66 | 96.000000 |
| 2 | vmess | KSR4 | raw | 19.959645 | 94.880716 | 55.023024 | 0.231917 | -0.000000 | 66 | 4.809705 |
| 2 | vmess | empirical | normalized | 0.377378 | 94.880716 | 44.635077 | 4.703831 | -0.000000 | 59 | 96.000000 |
| 2 | vmess | empirical | raw | 0.377378 | 94.880716 | 44.635077 | 12.464523 | -0.000000 | 59 | 254.387135 |
| 3 | vmess | KSR2 | normalized | 0.137597 | 71.453853 | 58.785188 | 4.205348 | -0.000000 | 86 | 96.000000 |
| 3 | vmess | KSR2 | raw | 0.137597 | 71.453853 | 58.785188 | 30.562823 | -0.000000 | 86 | 697.690433 |
| 3 | vmess | KSR3 | normalized | 0.106441 | 71.453853 | 63.973945 | 3.615207 | -0.000000 | 86 | 96.000000 |
| 3 | vmess | KSR3 | raw | 0.106441 | 71.453853 | 63.973945 | 33.964269 | -0.000000 | 86 | 901.903974 |
| 3 | vmess | KSR4 | normalized | 17.195407 | 71.453853 | 61.439075 | 4.287578 | -0.000000 | 74 | 96.000000 |
| 3 | vmess | KSR4 | raw | 17.195407 | 71.453853 | 61.439075 | 0.249344 | -0.000000 | 74 | 5.582886 |
| 3 | vmess | empirical | normalized | 0.353006 | 71.453853 | 51.497719 | 4.658596 | -0.000000 | 68 | 96.000000 |
| 3 | vmess | empirical | raw | 0.353006 | 71.453853 | 51.497719 | 13.196926 | -0.000000 | 68 | 271.949951 |
| 4 | vmess | KSR2 | normalized | 0.143871 | 71.091380 | 56.859933 | 5.127169 | -0.000000 | 86 | 96.000000 |
| 4 | vmess | KSR2 | raw | 0.143871 | 71.091380 | 56.859933 | 35.637166 | -0.000000 | 86 | 667.262520 |
| 4 | vmess | KSR3 | normalized | 0.111794 | 71.091380 | 62.249325 | 4.022132 | -0.000000 | 86 | 96.000000 |
| 4 | vmess | KSR3 | raw | 0.111794 | 71.091380 | 62.249325 | 35.978202 | -0.000000 | 86 | 858.725561 |
| 4 | vmess | KSR4 | normalized | 17.659745 | 71.091380 | 60.449493 | 4.316571 | -0.000000 | 73 | 96.000000 |
| 4 | vmess | KSR4 | raw | 17.659745 | 71.091380 | 60.449493 | 0.244430 | -0.000000 | 73 | 5.436092 |
| 4 | vmess | empirical | normalized | 0.358074 | 71.091380 | 52.279298 | 4.653991 | -0.000000 | 67 | 96.000000 |
| 4 | vmess | empirical | raw | 0.358074 | 71.091380 | 52.279298 | 12.997271 | -0.000000 | 67 | 268.100640 |

![矩阵尺度及有效rank](../../outputs/kernel-sensitivity-regularization-20261005/run-01/figures/matrix-scale-spectrum-reviewed.png)

小特征值在上表按六位小数展示，不应把显示为0或负0的值当作精确数学零；完整浮点谱、容差和原始矩阵保存在regularizers目录。视觉复核统一了不同部署中同一方法的颜色，未更改任何矩阵、预测、选择或检验。

## 特征块尺度与训练敏感度

以下为外层五折平均，仅作训练描述，不参与重新选矩阵或lambda。

| protocol | arm | feature | hist_trace | standardized_trace |
| --- | --- | --- | --- | --- |
| shadowsocks | KSR2 | E_down | 0.048946 | 39.393045 |
| shadowsocks | KSR2 | E_up | 0.036807 | 40.563164 |
| shadowsocks | KSR2 | FR_packet_runs | 0.043050 | 51.238183 |
| shadowsocks | KSR2 | P_down | 0.048961 | 40.022568 |
| shadowsocks | KSR2 | P_up | 0.041123 | 36.136428 |
| shadowsocks | KSR2 | R_unique_zero_runs | 0.040883 | 50.435033 |
| shadowsocks | KSR2 | U_down | 0.023005 | 25.224184 |
| shadowsocks | KSR2 | U_up | 0.010518 | 24.917226 |
| shadowsocks | KSR2 | W_down | 0.023054 | 32.933141 |
| shadowsocks | KSR2 | W_up | 0.015491 | 21.471649 |
| shadowsocks | KSR3 | E_down | 0.070633 | 53.798332 |
| shadowsocks | KSR3 | E_up | 0.059766 | 54.734991 |
| shadowsocks | KSR3 | FR_packet_runs | 0.125533 | 98.530329 |
| shadowsocks | KSR3 | P_down | 0.070625 | 54.507028 |
| shadowsocks | KSR3 | P_up | 0.060446 | 47.434778 |
| shadowsocks | KSR3 | R_unique_zero_runs | 0.125004 | 100.576183 |
| shadowsocks | KSR3 | U_down | 0.053738 | 51.125758 |
| shadowsocks | KSR3 | U_up | 0.027604 | 53.438022 |
| shadowsocks | KSR3 | W_down | 0.053729 | 61.349962 |
| shadowsocks | KSR3 | W_up | 0.031066 | 43.477802 |
| shadowsocks | KSR4 | E_down | 0.001500 | 0.522380 |
| shadowsocks | KSR4 | E_up | 0.000847 | 0.457121 |
| shadowsocks | KSR4 | FR_packet_runs | 0.002867 | 0.972351 |
| shadowsocks | KSR4 | P_down | 0.001511 | 0.523976 |
| shadowsocks | KSR4 | P_up | 0.000969 | 0.452447 |
| shadowsocks | KSR4 | R_unique_zero_runs | 0.002792 | 0.978096 |
| shadowsocks | KSR4 | U_down | 0.001293 | 0.356918 |
| shadowsocks | KSR4 | U_up | 0.000161 | 0.325348 |
| shadowsocks | KSR4 | W_down | 0.001288 | 0.410300 |
| shadowsocks | KSR4 | W_up | 0.001017 | 0.367390 |
| shadowsocks | empirical | E_down | 0.029699 | 28.118215 |
| shadowsocks | empirical | E_up | 0.025295 | 30.588178 |
| shadowsocks | empirical | FR_packet_runs | 0.004394 | 6.590554 |
| shadowsocks | empirical | P_down | 0.029792 | 28.640128 |
| shadowsocks | empirical | P_up | 0.030754 | 25.738894 |
| shadowsocks | empirical | R_unique_zero_runs | 0.001485 | 3.755279 |
| shadowsocks | empirical | U_down | 0.005425 | 7.397303 |
| shadowsocks | empirical | U_up | 0.002936 | 3.191238 |
| shadowsocks | empirical | W_down | 0.005580 | 10.823254 |
| shadowsocks | empirical | W_up | 0.008370 | 3.241013 |
| trojan | KSR2 | E_down | 0.043482 | 56.252397 |
| trojan | KSR2 | E_up | 0.018764 | 67.665242 |
| trojan | KSR2 | FR_packet_runs | 0.039650 | 98.499362 |
| trojan | KSR2 | P_down | 0.043902 | 59.509537 |
| trojan | KSR2 | P_up | 0.025976 | 68.066905 |
| trojan | KSR2 | R_unique_zero_runs | 0.038430 | 98.567395 |
| trojan | KSR2 | U_down | 0.017575 | 57.591490 |
| trojan | KSR2 | U_up | 0.016468 | 17.759459 |
| trojan | KSR2 | W_down | 0.017750 | 56.721333 |
| trojan | KSR2 | W_up | 0.021641 | 10.836922 |
| trojan | KSR3 | E_down | 0.064367 | 70.081052 |
| trojan | KSR3 | E_up | 0.047937 | 85.779797 |
| trojan | KSR3 | FR_packet_runs | 0.094160 | 131.938867 |
| trojan | KSR3 | P_down | 0.064195 | 73.503297 |
| trojan | KSR3 | P_up | 0.049810 | 78.144531 |
| trojan | KSR3 | R_unique_zero_runs | 0.094094 | 135.875329 |
| trojan | KSR3 | U_down | 0.032681 | 83.606476 |
| trojan | KSR3 | U_up | 0.027293 | 34.762207 |
| trojan | KSR3 | W_down | 0.032815 | 81.849748 |
| trojan | KSR3 | W_up | 0.031137 | 22.390063 |
| trojan | KSR4 | E_down | 0.000938 | 0.486424 |
| trojan | KSR4 | E_up | 0.000378 | 0.405871 |
| trojan | KSR4 | FR_packet_runs | 0.000920 | 0.913340 |
| trojan | KSR4 | P_down | 0.000737 | 0.470720 |
| trojan | KSR4 | P_up | 0.001286 | 0.434265 |
| trojan | KSR4 | R_unique_zero_runs | 0.000983 | 0.908754 |
| trojan | KSR4 | U_down | 0.000105 | 0.274954 |
| trojan | KSR4 | U_up | 0.000177 | 0.214589 |
| trojan | KSR4 | W_down | 0.000109 | 0.272666 |
| trojan | KSR4 | W_up | 0.001455 | 0.265935 |
| trojan | empirical | E_down | 0.026239 | 25.410720 |
| trojan | empirical | E_up | 0.007187 | 24.913288 |
| trojan | empirical | FR_packet_runs | 0.014946 | 29.524207 |
| trojan | empirical | P_down | 0.026961 | 27.418987 |
| trojan | empirical | P_up | 0.015825 | 23.178955 |
| trojan | empirical | R_unique_zero_runs | 0.012704 | 24.949712 |
| trojan | empirical | U_down | 0.005273 | 13.899105 |
| trojan | empirical | U_up | 0.011937 | 10.410803 |
| trojan | empirical | W_down | 0.005478 | 13.735898 |
| trojan | empirical | W_up | 0.017449 | 8.176418 |
| vless | KSR2 | E_down | 0.043861 | 54.617506 |
| vless | KSR2 | E_up | 0.018672 | 51.450285 |
| vless | KSR2 | FR_packet_runs | 0.039440 | 86.423423 |
| vless | KSR2 | P_down | 0.044336 | 55.859824 |
| vless | KSR2 | P_up | 0.025109 | 43.915320 |
| vless | KSR2 | R_unique_zero_runs | 0.038254 | 86.627362 |
| vless | KSR2 | U_down | 0.017663 | 43.752259 |
| vless | KSR2 | U_up | 0.015845 | 21.062801 |
| vless | KSR2 | W_down | 0.017920 | 42.765321 |
| vless | KSR2 | W_up | 0.022841 | 16.829543 |
| vless | KSR3 | E_down | 0.064852 | 68.102556 |
| vless | KSR3 | E_up | 0.046450 | 68.498436 |
| vless | KSR3 | FR_packet_runs | 0.094029 | 117.869035 |
| vless | KSR3 | P_down | 0.064761 | 69.232623 |
| vless | KSR3 | P_up | 0.048409 | 54.071366 |
| vless | KSR3 | R_unique_zero_runs | 0.093879 | 120.344062 |
| vless | KSR3 | U_down | 0.032723 | 66.304797 |
| vless | KSR3 | U_up | 0.027265 | 38.128523 |
| vless | KSR3 | W_down | 0.032918 | 64.229819 |
| vless | KSR3 | W_up | 0.032292 | 29.872360 |
| vless | KSR4 | E_down | 0.000846 | 0.458466 |
| vless | KSR4 | E_up | 0.000314 | 0.407366 |
| vless | KSR4 | FR_packet_runs | 0.001107 | 0.917849 |
| vless | KSR4 | P_down | 0.000777 | 0.462970 |
| vless | KSR4 | P_up | 0.001140 | 0.449386 |
| vless | KSR4 | R_unique_zero_runs | 0.001045 | 0.883437 |
| vless | KSR4 | U_down | 0.000114 | 0.227021 |
| vless | KSR4 | U_up | 0.000296 | 0.300649 |
| vless | KSR4 | W_down | 0.000127 | 0.230680 |
| vless | KSR4 | W_up | 0.001959 | 0.339750 |
| vless | empirical | E_down | 0.026549 | 24.878573 |
| vless | empirical | E_up | 0.008524 | 23.263875 |
| vless | empirical | FR_packet_runs | 0.015307 | 28.878815 |
| vless | empirical | P_down | 0.027319 | 25.780024 |
| vless | empirical | P_up | 0.016479 | 20.716102 |
| vless | empirical | R_unique_zero_runs | 0.012994 | 25.693246 |
| vless | empirical | U_down | 0.005481 | 10.231410 |
| vless | empirical | U_up | 0.011170 | 7.935601 |
| vless | empirical | W_down | 0.005767 | 10.088672 |
| vless | empirical | W_up | 0.018641 | 7.001833 |
| vmess | KSR2 | E_down | 0.039547 | 63.620053 |
| vmess | KSR2 | E_up | 0.021624 | 76.929268 |
| vmess | KSR2 | FR_packet_runs | 0.054976 | 105.719466 |
| vmess | KSR2 | P_down | 0.039537 | 75.680035 |
| vmess | KSR2 | P_up | 0.023687 | 81.999126 |
| vmess | KSR2 | R_unique_zero_runs | 0.052502 | 114.323854 |
| vmess | KSR2 | U_down | 0.017975 | 71.925923 |
| vmess | KSR2 | U_up | 0.020956 | 28.039579 |
| vmess | KSR2 | W_down | 0.018083 | 71.517303 |
| vmess | KSR2 | W_up | 0.023888 | 21.441304 |
| vmess | KSR3 | E_down | 0.055917 | 78.865406 |
| vmess | KSR3 | E_up | 0.028103 | 93.756976 |
| vmess | KSR3 | FR_packet_runs | 0.085821 | 130.451586 |
| vmess | KSR3 | P_down | 0.055776 | 91.140299 |
| vmess | KSR3 | P_up | 0.029667 | 94.520088 |
| vmess | KSR3 | R_unique_zero_runs | 0.085697 | 144.574374 |
| vmess | KSR3 | U_down | 0.032589 | 98.830219 |
| vmess | KSR3 | U_up | 0.027273 | 42.218338 |
| vmess | KSR3 | W_down | 0.032667 | 98.044773 |
| vmess | KSR3 | W_up | 0.029591 | 34.174092 |
| vmess | KSR4 | E_down | 0.000557 | 0.451519 |
| vmess | KSR4 | E_up | 0.000264 | 0.470756 |
| vmess | KSR4 | FR_packet_runs | 0.001551 | 1.044778 |
| vmess | KSR4 | P_down | 0.000517 | 0.448238 |
| vmess | KSR4 | P_up | 0.000741 | 0.493136 |
| vmess | KSR4 | R_unique_zero_runs | 0.001314 | 1.028519 |
| vmess | KSR4 | U_down | 0.000107 | 0.348745 |
| vmess | KSR4 | U_up | 0.000172 | 0.314610 |
| vmess | KSR4 | W_down | 0.000110 | 0.349514 |
| vmess | KSR4 | W_up | 0.000831 | 0.339051 |
| vmess | empirical | E_down | 0.023131 | 29.098978 |
| vmess | empirical | E_up | 0.017210 | 31.593768 |
| vmess | empirical | FR_packet_runs | 0.041198 | 42.110108 |
| vmess | empirical | P_down | 0.023273 | 29.481916 |
| vmess | empirical | P_up | 0.019460 | 33.462118 |
| vmess | empirical | R_unique_zero_runs | 0.037725 | 46.073621 |
| vmess | empirical | U_down | 0.005998 | 18.322543 |
| vmess | empirical | U_up | 0.016942 | 12.240034 |
| vmess | empirical | W_down | 0.006118 | 18.222388 |
| vmess | empirical | W_up | 0.020110 | 7.521994 |

| protocol | classifier_arm | matrix_arm | family | sensitivity |
| --- | --- | --- | --- | --- |
| shadowsocks | KSR0 | KSR2 | bytes | 3.842788 |
| shadowsocks | KSR0 | KSR2 | events | 3.671725 |
| shadowsocks | KSR0 | KSR2 | interaction | 1.618423 |
| shadowsocks | KSR0 | KSR3 | bytes | 5.040121 |
| shadowsocks | KSR0 | KSR3 | events | 3.038954 |
| shadowsocks | KSR0 | KSR3 | interaction | 2.311807 |
| shadowsocks | KSR0 | KSR4 | bytes | 2.623524 |
| shadowsocks | KSR0 | KSR4 | events | 2.730215 |
| shadowsocks | KSR0 | KSR4 | interaction | 1.913412 |
| shadowsocks | KSR1 | KSR2 | bytes | 2.726773 |
| shadowsocks | KSR1 | KSR2 | events | 2.608975 |
| shadowsocks | KSR1 | KSR2 | interaction | 1.128233 |
| shadowsocks | KSR1 | KSR3 | bytes | 3.580733 |
| shadowsocks | KSR1 | KSR3 | events | 2.141415 |
| shadowsocks | KSR1 | KSR3 | interaction | 1.621459 |
| shadowsocks | KSR1 | KSR4 | bytes | 1.856603 |
| shadowsocks | KSR1 | KSR4 | events | 1.920353 |
| shadowsocks | KSR1 | KSR4 | interaction | 1.366947 |
| shadowsocks | KSR2 | KSR2 | bytes | 3.555010 |
| shadowsocks | KSR2 | KSR2 | events | 3.173965 |
| shadowsocks | KSR2 | KSR2 | interaction | 1.415117 |
| shadowsocks | KSR2 | KSR3 | bytes | 4.709554 |
| shadowsocks | KSR2 | KSR3 | events | 2.704420 |
| shadowsocks | KSR2 | KSR3 | interaction | 2.042936 |
| shadowsocks | KSR2 | KSR4 | bytes | 2.509402 |
| shadowsocks | KSR2 | KSR4 | events | 2.541059 |
| shadowsocks | KSR2 | KSR4 | interaction | 1.756611 |
| shadowsocks | KSR3 | KSR2 | bytes | 3.643552 |
| shadowsocks | KSR3 | KSR2 | events | 3.570009 |
| shadowsocks | KSR3 | KSR2 | interaction | 1.502689 |
| shadowsocks | KSR3 | KSR3 | bytes | 4.778177 |
| shadowsocks | KSR3 | KSR3 | events | 2.962804 |
| shadowsocks | KSR3 | KSR3 | interaction | 2.150545 |
| shadowsocks | KSR3 | KSR4 | bytes | 2.525845 |
| shadowsocks | KSR3 | KSR4 | events | 2.686777 |
| shadowsocks | KSR3 | KSR4 | interaction | 1.798060 |
| shadowsocks | KSR4 | KSR2 | bytes | 3.352830 |
| shadowsocks | KSR4 | KSR2 | events | 2.830580 |
| shadowsocks | KSR4 | KSR2 | interaction | 0.971723 |
| shadowsocks | KSR4 | KSR3 | bytes | 4.421227 |
| shadowsocks | KSR4 | KSR3 | events | 2.454242 |
| shadowsocks | KSR4 | KSR3 | interaction | 1.366815 |
| shadowsocks | KSR4 | KSR4 | bytes | 1.704400 |
| shadowsocks | KSR4 | KSR4 | events | 1.677756 |
| shadowsocks | KSR4 | KSR4 | interaction | 0.840716 |
| trojan | KSR0 | KSR2 | bytes | 4.702777 |
| trojan | KSR0 | KSR2 | events | 2.693040 |
| trojan | KSR0 | KSR2 | interaction | 0.988171 |
| trojan | KSR0 | KSR3 | bytes | 6.517175 |
| trojan | KSR0 | KSR3 | events | 3.584854 |
| trojan | KSR0 | KSR3 | interaction | 1.553198 |
| trojan | KSR0 | KSR4 | bytes | 5.508982 |
| trojan | KSR0 | KSR4 | events | 4.459694 |
| trojan | KSR0 | KSR4 | interaction | 2.140171 |
| trojan | KSR1 | KSR2 | bytes | 3.299654 |
| trojan | KSR1 | KSR2 | events | 1.925951 |
| trojan | KSR1 | KSR2 | interaction | 0.711283 |
| trojan | KSR1 | KSR3 | bytes | 4.578615 |
| trojan | KSR1 | KSR3 | events | 2.537049 |
| trojan | KSR1 | KSR3 | interaction | 1.109920 |
| trojan | KSR1 | KSR4 | bytes | 3.883352 |
| trojan | KSR1 | KSR4 | events | 3.091413 |
| trojan | KSR1 | KSR4 | interaction | 1.540175 |
| trojan | KSR2 | KSR2 | bytes | 3.754739 |
| trojan | KSR2 | KSR2 | events | 2.180681 |
| trojan | KSR2 | KSR2 | interaction | 0.761185 |
| trojan | KSR2 | KSR3 | bytes | 5.237454 |
| trojan | KSR2 | KSR3 | events | 2.967244 |
| trojan | KSR2 | KSR3 | interaction | 1.203478 |
| trojan | KSR2 | KSR4 | bytes | 4.875333 |
| trojan | KSR2 | KSR4 | events | 3.905501 |
| trojan | KSR2 | KSR4 | interaction | 1.760303 |
| trojan | KSR3 | KSR2 | bytes | 3.183303 |
| trojan | KSR3 | KSR2 | events | 2.057694 |
| trojan | KSR3 | KSR2 | interaction | 0.629185 |
| trojan | KSR3 | KSR3 | bytes | 4.420564 |
| trojan | KSR3 | KSR3 | events | 2.689572 |
| trojan | KSR3 | KSR3 | interaction | 0.974813 |
| trojan | KSR3 | KSR4 | bytes | 4.644359 |
| trojan | KSR3 | KSR4 | events | 3.711505 |
| trojan | KSR3 | KSR4 | interaction | 1.498848 |
| trojan | KSR4 | KSR2 | bytes | 3.622105 |
| trojan | KSR4 | KSR2 | events | 2.302787 |
| trojan | KSR4 | KSR2 | interaction | 0.594794 |
| trojan | KSR4 | KSR3 | bytes | 5.160865 |
| trojan | KSR4 | KSR3 | events | 2.860928 |
| trojan | KSR4 | KSR3 | interaction | 0.871613 |
| trojan | KSR4 | KSR4 | bytes | 3.488552 |
| trojan | KSR4 | KSR4 | events | 2.655957 |
| trojan | KSR4 | KSR4 | interaction | 1.064966 |
| vless | KSR0 | KSR2 | bytes | 5.220814 |
| vless | KSR0 | KSR2 | events | 3.417864 |
| vless | KSR0 | KSR2 | interaction | 1.871409 |
| vless | KSR0 | KSR3 | bytes | 7.082846 |
| vless | KSR0 | KSR3 | events | 4.281704 |
| vless | KSR0 | KSR3 | interaction | 2.875951 |
| vless | KSR0 | KSR4 | bytes | 6.622572 |
| vless | KSR0 | KSR4 | events | 4.530187 |
| vless | KSR0 | KSR4 | interaction | 3.549453 |
| vless | KSR1 | KSR2 | bytes | 3.469916 |
| vless | KSR1 | KSR2 | events | 2.140816 |
| vless | KSR1 | KSR2 | interaction | 1.158100 |
| vless | KSR1 | KSR3 | bytes | 4.692585 |
| vless | KSR1 | KSR3 | events | 2.652353 |
| vless | KSR1 | KSR3 | interaction | 1.764065 |
| vless | KSR1 | KSR4 | bytes | 4.247408 |
| vless | KSR1 | KSR4 | events | 2.720045 |
| vless | KSR1 | KSR4 | interaction | 2.204580 |
| vless | KSR2 | KSR2 | bytes | 3.661448 |
| vless | KSR2 | KSR2 | events | 2.473481 |
| vless | KSR2 | KSR2 | interaction | 1.154917 |
| vless | KSR2 | KSR3 | bytes | 5.038109 |
| vless | KSR2 | KSR3 | events | 3.180427 |
| vless | KSR2 | KSR3 | interaction | 1.794151 |
| vless | KSR2 | KSR4 | bytes | 5.211568 |
| vless | KSR2 | KSR4 | events | 3.608166 |
| vless | KSR2 | KSR4 | interaction | 2.291353 |
| vless | KSR3 | KSR2 | bytes | 3.977898 |
| vless | KSR3 | KSR2 | events | 2.729047 |
| vless | KSR3 | KSR2 | interaction | 1.221391 |
| vless | KSR3 | KSR3 | bytes | 5.340011 |
| vless | KSR3 | KSR3 | events | 3.327020 |
| vless | KSR3 | KSR3 | interaction | 1.830728 |
| vless | KSR3 | KSR4 | bytes | 5.310294 |
| vless | KSR3 | KSR4 | events | 3.671128 |
| vless | KSR3 | KSR4 | interaction | 2.288920 |
| vless | KSR4 | KSR2 | bytes | 4.645975 |
| vless | KSR4 | KSR2 | events | 3.201907 |
| vless | KSR4 | KSR2 | interaction | 1.437829 |
| vless | KSR4 | KSR3 | bytes | 6.313993 |
| vless | KSR4 | KSR3 | events | 3.951183 |
| vless | KSR4 | KSR3 | interaction | 2.174947 |
| vless | KSR4 | KSR4 | bytes | 5.490279 |
| vless | KSR4 | KSR4 | events | 3.814022 |
| vless | KSR4 | KSR4 | interaction | 2.487322 |
| vmess | KSR0 | KSR2 | bytes | 3.290785 |
| vmess | KSR0 | KSR2 | events | 5.080930 |
| vmess | KSR0 | KSR2 | interaction | 1.127322 |
| vmess | KSR0 | KSR3 | bytes | 4.288963 |
| vmess | KSR0 | KSR3 | events | 5.583885 |
| vmess | KSR0 | KSR3 | interaction | 1.516699 |
| vmess | KSR0 | KSR4 | bytes | 3.914763 |
| vmess | KSR0 | KSR4 | events | 5.184461 |
| vmess | KSR0 | KSR4 | interaction | 2.097712 |
| vmess | KSR1 | KSR2 | bytes | 2.416378 |
| vmess | KSR1 | KSR2 | events | 3.731514 |
| vmess | KSR1 | KSR2 | interaction | 0.882119 |
| vmess | KSR1 | KSR3 | bytes | 3.167392 |
| vmess | KSR1 | KSR3 | events | 4.125177 |
| vmess | KSR1 | KSR3 | interaction | 1.174073 |
| vmess | KSR1 | KSR4 | bytes | 2.919808 |
| vmess | KSR1 | KSR4 | events | 3.813516 |
| vmess | KSR1 | KSR4 | interaction | 1.635130 |
| vmess | KSR2 | KSR2 | bytes | 2.397267 |
| vmess | KSR2 | KSR2 | events | 3.477911 |
| vmess | KSR2 | KSR2 | interaction | 0.783833 |
| vmess | KSR2 | KSR3 | bytes | 3.238445 |
| vmess | KSR2 | KSR3 | events | 3.991718 |
| vmess | KSR2 | KSR3 | interaction | 1.062459 |
| vmess | KSR2 | KSR4 | bytes | 3.312943 |
| vmess | KSR2 | KSR4 | events | 3.951508 |
| vmess | KSR2 | KSR4 | interaction | 1.581251 |
| vmess | KSR3 | KSR2 | bytes | 2.605617 |
| vmess | KSR3 | KSR2 | events | 3.808322 |
| vmess | KSR3 | KSR2 | interaction | 0.709133 |
| vmess | KSR3 | KSR3 | bytes | 3.396601 |
| vmess | KSR3 | KSR3 | events | 4.206583 |
| vmess | KSR3 | KSR3 | interaction | 0.976411 |
| vmess | KSR3 | KSR4 | bytes | 3.439127 |
| vmess | KSR3 | KSR4 | events | 4.252025 |
| vmess | KSR3 | KSR4 | interaction | 1.428319 |
| vmess | KSR4 | KSR2 | bytes | 2.242122 |
| vmess | KSR4 | KSR2 | events | 3.700830 |
| vmess | KSR4 | KSR2 | interaction | 0.571828 |
| vmess | KSR4 | KSR3 | bytes | 3.080907 |
| vmess | KSR4 | KSR3 | events | 4.061697 |
| vmess | KSR4 | KSR3 | interaction | 0.758476 |
| vmess | KSR4 | KSR4 | bytes | 2.432774 |
| vmess | KSR4 | KSR4 | events | 2.977315 |
| vmess | KSR4 | KSR4 | interaction | 0.901085 |

| protocol | arm | weight_Frobenius | baseline_weight_difference | common_class_weight_max |
| --- | --- | --- | --- | --- |
| shadowsocks | KSR0 | 6.315142 | 0.000000 | 0.000000 |
| shadowsocks | KSR1 | 5.244147 | 1.105279 | 0.000000 |
| shadowsocks | KSR2 | 6.114965 | 0.410599 | 0.000000 |
| shadowsocks | KSR3 | 6.205521 | 0.191749 | 0.000000 |
| shadowsocks | KSR4 | 5.598614 | 1.652961 | 0.000000 |
| trojan | KSR0 | 7.125749 | 0.000000 | 0.000000 |
| trojan | KSR1 | 5.932774 | 1.222784 | 0.000000 |
| trojan | KSR2 | 6.501587 | 0.882040 | 0.000000 |
| trojan | KSR3 | 6.211632 | 1.344896 | 0.000000 |
| trojan | KSR4 | 6.198882 | 1.829877 | 0.000000 |
| vless | KSR0 | 7.711427 | 0.000000 | 0.000000 |
| vless | KSR1 | 6.097808 | 1.666474 | 0.000000 |
| vless | KSR2 | 6.744627 | 1.338604 | 0.000000 |
| vless | KSR3 | 6.794992 | 1.258270 | 0.000000 |
| vless | KSR4 | 7.235238 | 0.951629 | 0.000000 |
| vmess | KSR0 | 7.640592 | 0.000000 | 0.000000 |
| vmess | KSR1 | 6.498343 | 1.184501 | 0.000000 |
| vmess | KSR2 | 6.816530 | 1.330497 | 0.000000 |
| vmess | KSR3 | 6.908384 | 1.139027 | 0.000000 |
| vmess | KSR4 | 6.444397 | 1.986426 | 0.000000 |

## 完整内容错误台账

| protocol | arm | content_id | label | visits | errors |
| --- | --- | --- | --- | --- | --- |
| shadowsocks | KSR0 | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | developer.mozilla.org::document_view | 4 | 1 |
| shadowsocks | KSR1 | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | developer.mozilla.org::document_view | 4 | 1 |
| shadowsocks | KSR2 | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | developer.mozilla.org::document_view | 4 | 1 |
| shadowsocks | KSR3 | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | developer.mozilla.org::document_view | 4 | 1 |
| shadowsocks | KSR4 | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | developer.mozilla.org::document_view | 4 | 1 |
| shadowsocks | KSR0 | https://developer.mozilla.org/en-US/docs/Web/HTTP | developer.mozilla.org::document_view | 4 | 1 |
| shadowsocks | KSR1 | https://developer.mozilla.org/en-US/docs/Web/HTTP | developer.mozilla.org::document_view | 4 | 1 |
| shadowsocks | KSR2 | https://developer.mozilla.org/en-US/docs/Web/HTTP | developer.mozilla.org::document_view | 4 | 1 |
| shadowsocks | KSR3 | https://developer.mozilla.org/en-US/docs/Web/HTTP | developer.mozilla.org::document_view | 4 | 1 |
| shadowsocks | KSR4 | https://developer.mozilla.org/en-US/docs/Web/HTTP | developer.mozilla.org::document_view | 4 | 1 |
| shadowsocks | KSR0 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | developer.mozilla.org::document_view | 4 | 0 |
| shadowsocks | KSR1 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | developer.mozilla.org::document_view | 4 | 0 |
| shadowsocks | KSR2 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | developer.mozilla.org::document_view | 4 | 0 |
| shadowsocks | KSR3 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | developer.mozilla.org::document_view | 4 | 0 |
| shadowsocks | KSR4 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | developer.mozilla.org::document_view | 4 | 0 |
| shadowsocks | KSR0 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | developer.mozilla.org::document_view | 4 | 0 |
| shadowsocks | KSR1 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | developer.mozilla.org::document_view | 4 | 0 |
| shadowsocks | KSR2 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | developer.mozilla.org::document_view | 4 | 0 |
| shadowsocks | KSR3 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | developer.mozilla.org::document_view | 4 | 0 |
| shadowsocks | KSR4 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | developer.mozilla.org::document_view | 4 | 0 |
| shadowsocks | KSR0 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | developer.mozilla.org::document_view | 4 | 3 |
| shadowsocks | KSR1 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | developer.mozilla.org::document_view | 4 | 3 |
| shadowsocks | KSR2 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | developer.mozilla.org::document_view | 4 | 3 |
| shadowsocks | KSR3 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | developer.mozilla.org::document_view | 4 | 3 |
| shadowsocks | KSR4 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | developer.mozilla.org::document_view | 4 | 4 |
| shadowsocks | KSR0 | https://en.wikipedia.org/wiki/Computer_network | wikipedia.org::article_view | 4 | 2 |
| shadowsocks | KSR1 | https://en.wikipedia.org/wiki/Computer_network | wikipedia.org::article_view | 4 | 2 |
| shadowsocks | KSR2 | https://en.wikipedia.org/wiki/Computer_network | wikipedia.org::article_view | 4 | 2 |
| shadowsocks | KSR3 | https://en.wikipedia.org/wiki/Computer_network | wikipedia.org::article_view | 4 | 2 |
| shadowsocks | KSR4 | https://en.wikipedia.org/wiki/Computer_network | wikipedia.org::article_view | 4 | 2 |
| shadowsocks | KSR0 | https://en.wikipedia.org/wiki/Domain_Name_System | wikipedia.org::article_view | 4 | 0 |
| shadowsocks | KSR1 | https://en.wikipedia.org/wiki/Domain_Name_System | wikipedia.org::article_view | 4 | 0 |
| shadowsocks | KSR2 | https://en.wikipedia.org/wiki/Domain_Name_System | wikipedia.org::article_view | 4 | 0 |
| shadowsocks | KSR3 | https://en.wikipedia.org/wiki/Domain_Name_System | wikipedia.org::article_view | 4 | 0 |
| shadowsocks | KSR4 | https://en.wikipedia.org/wiki/Domain_Name_System | wikipedia.org::article_view | 4 | 0 |
| shadowsocks | KSR0 | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | wikipedia.org::article_view | 4 | 1 |
| shadowsocks | KSR1 | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | wikipedia.org::article_view | 4 | 1 |
| shadowsocks | KSR2 | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | wikipedia.org::article_view | 4 | 1 |
| shadowsocks | KSR3 | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | wikipedia.org::article_view | 4 | 1 |
| shadowsocks | KSR4 | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | wikipedia.org::article_view | 4 | 2 |
| shadowsocks | KSR0 | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | wikipedia.org::article_view | 4 | 1 |
| shadowsocks | KSR1 | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | wikipedia.org::article_view | 4 | 1 |
| shadowsocks | KSR2 | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | wikipedia.org::article_view | 4 | 1 |
| shadowsocks | KSR3 | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | wikipedia.org::article_view | 4 | 1 |
| shadowsocks | KSR4 | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | wikipedia.org::article_view | 4 | 1 |
| shadowsocks | KSR0 | https://en.wikipedia.org/wiki/Transport_Layer_Security | wikipedia.org::article_view | 4 | 1 |
| shadowsocks | KSR1 | https://en.wikipedia.org/wiki/Transport_Layer_Security | wikipedia.org::article_view | 4 | 1 |
| shadowsocks | KSR2 | https://en.wikipedia.org/wiki/Transport_Layer_Security | wikipedia.org::article_view | 4 | 1 |
| shadowsocks | KSR3 | https://en.wikipedia.org/wiki/Transport_Layer_Security | wikipedia.org::article_view | 4 | 1 |
| shadowsocks | KSR4 | https://en.wikipedia.org/wiki/Transport_Layer_Security | wikipedia.org::article_view | 4 | 1 |
| shadowsocks | KSR0 | https://github.com/RakuLomis/TrafficTracer | github.com::repository_view | 4 | 0 |
| shadowsocks | KSR1 | https://github.com/RakuLomis/TrafficTracer | github.com::repository_view | 4 | 0 |
| shadowsocks | KSR2 | https://github.com/RakuLomis/TrafficTracer | github.com::repository_view | 4 | 0 |
| shadowsocks | KSR3 | https://github.com/RakuLomis/TrafficTracer | github.com::repository_view | 4 | 0 |
| shadowsocks | KSR4 | https://github.com/RakuLomis/TrafficTracer | github.com::repository_view | 4 | 0 |
| shadowsocks | KSR0 | https://github.com/numpy/numpy | github.com::repository_view | 4 | 0 |
| shadowsocks | KSR1 | https://github.com/numpy/numpy | github.com::repository_view | 4 | 0 |
| shadowsocks | KSR2 | https://github.com/numpy/numpy | github.com::repository_view | 4 | 0 |
| shadowsocks | KSR3 | https://github.com/numpy/numpy | github.com::repository_view | 4 | 0 |
| shadowsocks | KSR4 | https://github.com/numpy/numpy | github.com::repository_view | 4 | 0 |
| shadowsocks | KSR0 | https://github.com/pallets/flask | github.com::repository_view | 4 | 1 |
| shadowsocks | KSR1 | https://github.com/pallets/flask | github.com::repository_view | 4 | 1 |
| shadowsocks | KSR2 | https://github.com/pallets/flask | github.com::repository_view | 4 | 1 |
| shadowsocks | KSR3 | https://github.com/pallets/flask | github.com::repository_view | 4 | 1 |
| shadowsocks | KSR4 | https://github.com/pallets/flask | github.com::repository_view | 4 | 1 |
| shadowsocks | KSR0 | https://github.com/python/cpython | github.com::repository_view | 4 | 0 |
| shadowsocks | KSR1 | https://github.com/python/cpython | github.com::repository_view | 4 | 0 |
| shadowsocks | KSR2 | https://github.com/python/cpython | github.com::repository_view | 4 | 0 |
| shadowsocks | KSR3 | https://github.com/python/cpython | github.com::repository_view | 4 | 0 |
| shadowsocks | KSR4 | https://github.com/python/cpython | github.com::repository_view | 4 | 0 |
| shadowsocks | KSR0 | https://github.com/scikit-learn/scikit-learn | github.com::repository_view | 4 | 0 |
| shadowsocks | KSR1 | https://github.com/scikit-learn/scikit-learn | github.com::repository_view | 4 | 0 |
| shadowsocks | KSR2 | https://github.com/scikit-learn/scikit-learn | github.com::repository_view | 4 | 0 |
| shadowsocks | KSR3 | https://github.com/scikit-learn/scikit-learn | github.com::repository_view | 4 | 0 |
| shadowsocks | KSR4 | https://github.com/scikit-learn/scikit-learn | github.com::repository_view | 4 | 0 |
| shadowsocks | KSR0 | https://www.bing.com/search?q=beginner+guitar+chords | bing.com::search_results_view | 4 | 4 |
| shadowsocks | KSR1 | https://www.bing.com/search?q=beginner+guitar+chords | bing.com::search_results_view | 4 | 4 |
| shadowsocks | KSR2 | https://www.bing.com/search?q=beginner+guitar+chords | bing.com::search_results_view | 4 | 4 |
| shadowsocks | KSR3 | https://www.bing.com/search?q=beginner+guitar+chords | bing.com::search_results_view | 4 | 4 |
| shadowsocks | KSR4 | https://www.bing.com/search?q=beginner+guitar+chords | bing.com::search_results_view | 4 | 4 |
| shadowsocks | KSR0 | https://www.bing.com/search?q=indoor+plant+care | bing.com::search_results_view | 4 | 0 |
| shadowsocks | KSR1 | https://www.bing.com/search?q=indoor+plant+care | bing.com::search_results_view | 4 | 0 |
| shadowsocks | KSR2 | https://www.bing.com/search?q=indoor+plant+care | bing.com::search_results_view | 4 | 1 |
| shadowsocks | KSR3 | https://www.bing.com/search?q=indoor+plant+care | bing.com::search_results_view | 4 | 0 |
| shadowsocks | KSR4 | https://www.bing.com/search?q=indoor+plant+care | bing.com::search_results_view | 4 | 0 |
| shadowsocks | KSR0 | https://www.bing.com/search?q=network+traffic+analysis | bing.com::search_results_view | 4 | 1 |
| shadowsocks | KSR1 | https://www.bing.com/search?q=network+traffic+analysis | bing.com::search_results_view | 4 | 1 |
| shadowsocks | KSR2 | https://www.bing.com/search?q=network+traffic+analysis | bing.com::search_results_view | 4 | 1 |
| shadowsocks | KSR3 | https://www.bing.com/search?q=network+traffic+analysis | bing.com::search_results_view | 4 | 1 |
| shadowsocks | KSR4 | https://www.bing.com/search?q=network+traffic+analysis | bing.com::search_results_view | 4 | 1 |
| shadowsocks | KSR0 | https://www.bing.com/search?q=solar+system+facts | bing.com::search_results_view | 4 | 1 |
| shadowsocks | KSR1 | https://www.bing.com/search?q=solar+system+facts | bing.com::search_results_view | 4 | 1 |
| shadowsocks | KSR2 | https://www.bing.com/search?q=solar+system+facts | bing.com::search_results_view | 4 | 1 |
| shadowsocks | KSR3 | https://www.bing.com/search?q=solar+system+facts | bing.com::search_results_view | 4 | 1 |
| shadowsocks | KSR4 | https://www.bing.com/search?q=solar+system+facts | bing.com::search_results_view | 4 | 1 |
| shadowsocks | KSR0 | https://www.bing.com/search?q=sourdough+bread+recipe | bing.com::search_results_view | 4 | 0 |
| shadowsocks | KSR1 | https://www.bing.com/search?q=sourdough+bread+recipe | bing.com::search_results_view | 4 | 0 |
| shadowsocks | KSR2 | https://www.bing.com/search?q=sourdough+bread+recipe | bing.com::search_results_view | 4 | 0 |
| shadowsocks | KSR3 | https://www.bing.com/search?q=sourdough+bread+recipe | bing.com::search_results_view | 4 | 0 |
| shadowsocks | KSR4 | https://www.bing.com/search?q=sourdough+bread+recipe | bing.com::search_results_view | 4 | 0 |
| shadowsocks | KSR0 | https://www.youtube.com/results?search_query=astronomy+documentary | youtube.com::search_results_view | 4 | 0 |
| shadowsocks | KSR1 | https://www.youtube.com/results?search_query=astronomy+documentary | youtube.com::search_results_view | 4 | 0 |
| shadowsocks | KSR2 | https://www.youtube.com/results?search_query=astronomy+documentary | youtube.com::search_results_view | 4 | 0 |
| shadowsocks | KSR3 | https://www.youtube.com/results?search_query=astronomy+documentary | youtube.com::search_results_view | 4 | 0 |
| shadowsocks | KSR4 | https://www.youtube.com/results?search_query=astronomy+documentary | youtube.com::search_results_view | 4 | 0 |
| shadowsocks | KSR0 | https://www.youtube.com/results?search_query=bicycle+maintenance | youtube.com::search_results_view | 4 | 0 |
| shadowsocks | KSR1 | https://www.youtube.com/results?search_query=bicycle+maintenance | youtube.com::search_results_view | 4 | 0 |
| shadowsocks | KSR2 | https://www.youtube.com/results?search_query=bicycle+maintenance | youtube.com::search_results_view | 4 | 0 |
| shadowsocks | KSR3 | https://www.youtube.com/results?search_query=bicycle+maintenance | youtube.com::search_results_view | 4 | 0 |
| shadowsocks | KSR4 | https://www.youtube.com/results?search_query=bicycle+maintenance | youtube.com::search_results_view | 4 | 0 |
| shadowsocks | KSR0 | https://www.youtube.com/results?search_query=bread+baking | youtube.com::search_results_view | 4 | 0 |
| shadowsocks | KSR1 | https://www.youtube.com/results?search_query=bread+baking | youtube.com::search_results_view | 4 | 0 |
| shadowsocks | KSR2 | https://www.youtube.com/results?search_query=bread+baking | youtube.com::search_results_view | 4 | 0 |
| shadowsocks | KSR3 | https://www.youtube.com/results?search_query=bread+baking | youtube.com::search_results_view | 4 | 0 |
| shadowsocks | KSR4 | https://www.youtube.com/results?search_query=bread+baking | youtube.com::search_results_view | 4 | 0 |
| shadowsocks | KSR0 | https://www.youtube.com/results?search_query=piano+practice | youtube.com::search_results_view | 4 | 0 |
| shadowsocks | KSR1 | https://www.youtube.com/results?search_query=piano+practice | youtube.com::search_results_view | 4 | 0 |
| shadowsocks | KSR2 | https://www.youtube.com/results?search_query=piano+practice | youtube.com::search_results_view | 4 | 0 |
| shadowsocks | KSR3 | https://www.youtube.com/results?search_query=piano+practice | youtube.com::search_results_view | 4 | 0 |
| shadowsocks | KSR4 | https://www.youtube.com/results?search_query=piano+practice | youtube.com::search_results_view | 4 | 0 |
| shadowsocks | KSR0 | https://www.youtube.com/results?search_query=watercolor+tutorial | youtube.com::search_results_view | 4 | 1 |
| shadowsocks | KSR1 | https://www.youtube.com/results?search_query=watercolor+tutorial | youtube.com::search_results_view | 4 | 1 |
| shadowsocks | KSR2 | https://www.youtube.com/results?search_query=watercolor+tutorial | youtube.com::search_results_view | 4 | 1 |
| shadowsocks | KSR3 | https://www.youtube.com/results?search_query=watercolor+tutorial | youtube.com::search_results_view | 4 | 1 |
| shadowsocks | KSR4 | https://www.youtube.com/results?search_query=watercolor+tutorial | youtube.com::search_results_view | 4 | 1 |
| shadowsocks | KSR0 | youtube_video:R6MlUcmOul8 | youtube.com::video_playback | 4 | 0 |
| shadowsocks | KSR1 | youtube_video:R6MlUcmOul8 | youtube.com::video_playback | 4 | 0 |
| shadowsocks | KSR2 | youtube_video:R6MlUcmOul8 | youtube.com::video_playback | 4 | 0 |
| shadowsocks | KSR3 | youtube_video:R6MlUcmOul8 | youtube.com::video_playback | 4 | 0 |
| shadowsocks | KSR4 | youtube_video:R6MlUcmOul8 | youtube.com::video_playback | 4 | 0 |
| shadowsocks | KSR0 | youtube_video:aircAruvnKk | youtube.com::video_playback | 4 | 0 |
| shadowsocks | KSR1 | youtube_video:aircAruvnKk | youtube.com::video_playback | 4 | 0 |
| shadowsocks | KSR2 | youtube_video:aircAruvnKk | youtube.com::video_playback | 4 | 0 |
| shadowsocks | KSR3 | youtube_video:aircAruvnKk | youtube.com::video_playback | 4 | 0 |
| shadowsocks | KSR4 | youtube_video:aircAruvnKk | youtube.com::video_playback | 4 | 0 |
| shadowsocks | KSR0 | youtube_video:aqz-KE-bpKQ | youtube.com::video_playback | 4 | 0 |
| shadowsocks | KSR1 | youtube_video:aqz-KE-bpKQ | youtube.com::video_playback | 4 | 0 |
| shadowsocks | KSR2 | youtube_video:aqz-KE-bpKQ | youtube.com::video_playback | 4 | 0 |
| shadowsocks | KSR3 | youtube_video:aqz-KE-bpKQ | youtube.com::video_playback | 4 | 0 |
| shadowsocks | KSR4 | youtube_video:aqz-KE-bpKQ | youtube.com::video_playback | 4 | 0 |
| shadowsocks | KSR0 | youtube_video:eRsGyueVLvQ | youtube.com::video_playback | 4 | 0 |
| shadowsocks | KSR1 | youtube_video:eRsGyueVLvQ | youtube.com::video_playback | 4 | 0 |
| shadowsocks | KSR2 | youtube_video:eRsGyueVLvQ | youtube.com::video_playback | 4 | 0 |
| shadowsocks | KSR3 | youtube_video:eRsGyueVLvQ | youtube.com::video_playback | 4 | 0 |
| shadowsocks | KSR4 | youtube_video:eRsGyueVLvQ | youtube.com::video_playback | 4 | 0 |
| shadowsocks | KSR0 | youtube_video:sAWK0mgrMp4 | youtube.com::video_playback | 4 | 0 |
| shadowsocks | KSR1 | youtube_video:sAWK0mgrMp4 | youtube.com::video_playback | 4 | 0 |
| shadowsocks | KSR2 | youtube_video:sAWK0mgrMp4 | youtube.com::video_playback | 4 | 0 |
| shadowsocks | KSR3 | youtube_video:sAWK0mgrMp4 | youtube.com::video_playback | 4 | 0 |
| shadowsocks | KSR4 | youtube_video:sAWK0mgrMp4 | youtube.com::video_playback | 4 | 0 |
| trojan | KSR0 | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | developer.mozilla.org::document_view | 4 | 2 |
| trojan | KSR1 | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | developer.mozilla.org::document_view | 4 | 2 |
| trojan | KSR2 | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | developer.mozilla.org::document_view | 4 | 2 |
| trojan | KSR3 | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | developer.mozilla.org::document_view | 4 | 2 |
| trojan | KSR4 | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | developer.mozilla.org::document_view | 4 | 2 |
| trojan | KSR0 | https://developer.mozilla.org/en-US/docs/Web/HTTP | developer.mozilla.org::document_view | 4 | 2 |
| trojan | KSR1 | https://developer.mozilla.org/en-US/docs/Web/HTTP | developer.mozilla.org::document_view | 4 | 1 |
| trojan | KSR2 | https://developer.mozilla.org/en-US/docs/Web/HTTP | developer.mozilla.org::document_view | 4 | 2 |
| trojan | KSR3 | https://developer.mozilla.org/en-US/docs/Web/HTTP | developer.mozilla.org::document_view | 4 | 1 |
| trojan | KSR4 | https://developer.mozilla.org/en-US/docs/Web/HTTP | developer.mozilla.org::document_view | 4 | 1 |
| trojan | KSR0 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | developer.mozilla.org::document_view | 4 | 1 |
| trojan | KSR1 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | developer.mozilla.org::document_view | 4 | 1 |
| trojan | KSR2 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | developer.mozilla.org::document_view | 4 | 1 |
| trojan | KSR3 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | developer.mozilla.org::document_view | 4 | 1 |
| trojan | KSR4 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | developer.mozilla.org::document_view | 4 | 1 |
| trojan | KSR0 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | developer.mozilla.org::document_view | 4 | 1 |
| trojan | KSR1 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | developer.mozilla.org::document_view | 4 | 1 |
| trojan | KSR2 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | developer.mozilla.org::document_view | 4 | 2 |
| trojan | KSR3 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | developer.mozilla.org::document_view | 4 | 2 |
| trojan | KSR4 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | developer.mozilla.org::document_view | 4 | 1 |
| trojan | KSR0 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | developer.mozilla.org::document_view | 4 | 2 |
| trojan | KSR1 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | developer.mozilla.org::document_view | 4 | 2 |
| trojan | KSR2 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | developer.mozilla.org::document_view | 4 | 2 |
| trojan | KSR3 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | developer.mozilla.org::document_view | 4 | 2 |
| trojan | KSR4 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | developer.mozilla.org::document_view | 4 | 2 |
| trojan | KSR0 | https://en.wikipedia.org/wiki/Computer_network | wikipedia.org::article_view | 4 | 1 |
| trojan | KSR1 | https://en.wikipedia.org/wiki/Computer_network | wikipedia.org::article_view | 4 | 1 |
| trojan | KSR2 | https://en.wikipedia.org/wiki/Computer_network | wikipedia.org::article_view | 4 | 1 |
| trojan | KSR3 | https://en.wikipedia.org/wiki/Computer_network | wikipedia.org::article_view | 4 | 1 |
| trojan | KSR4 | https://en.wikipedia.org/wiki/Computer_network | wikipedia.org::article_view | 4 | 1 |
| trojan | KSR0 | https://en.wikipedia.org/wiki/Domain_Name_System | wikipedia.org::article_view | 4 | 1 |
| trojan | KSR1 | https://en.wikipedia.org/wiki/Domain_Name_System | wikipedia.org::article_view | 4 | 1 |
| trojan | KSR2 | https://en.wikipedia.org/wiki/Domain_Name_System | wikipedia.org::article_view | 4 | 1 |
| trojan | KSR3 | https://en.wikipedia.org/wiki/Domain_Name_System | wikipedia.org::article_view | 4 | 1 |
| trojan | KSR4 | https://en.wikipedia.org/wiki/Domain_Name_System | wikipedia.org::article_view | 4 | 1 |
| trojan | KSR0 | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | wikipedia.org::article_view | 4 | 1 |
| trojan | KSR1 | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | wikipedia.org::article_view | 4 | 1 |
| trojan | KSR2 | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | wikipedia.org::article_view | 4 | 1 |
| trojan | KSR3 | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | wikipedia.org::article_view | 4 | 1 |
| trojan | KSR4 | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | wikipedia.org::article_view | 4 | 1 |
| trojan | KSR0 | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | wikipedia.org::article_view | 4 | 0 |
| trojan | KSR1 | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | wikipedia.org::article_view | 4 | 0 |
| trojan | KSR2 | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | wikipedia.org::article_view | 4 | 0 |
| trojan | KSR3 | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | wikipedia.org::article_view | 4 | 0 |
| trojan | KSR4 | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | wikipedia.org::article_view | 4 | 0 |
| trojan | KSR0 | https://en.wikipedia.org/wiki/Transport_Layer_Security | wikipedia.org::article_view | 4 | 1 |
| trojan | KSR1 | https://en.wikipedia.org/wiki/Transport_Layer_Security | wikipedia.org::article_view | 4 | 1 |
| trojan | KSR2 | https://en.wikipedia.org/wiki/Transport_Layer_Security | wikipedia.org::article_view | 4 | 1 |
| trojan | KSR3 | https://en.wikipedia.org/wiki/Transport_Layer_Security | wikipedia.org::article_view | 4 | 2 |
| trojan | KSR4 | https://en.wikipedia.org/wiki/Transport_Layer_Security | wikipedia.org::article_view | 4 | 2 |
| trojan | KSR0 | https://github.com/RakuLomis/TrafficTracer | github.com::repository_view | 4 | 0 |
| trojan | KSR1 | https://github.com/RakuLomis/TrafficTracer | github.com::repository_view | 4 | 0 |
| trojan | KSR2 | https://github.com/RakuLomis/TrafficTracer | github.com::repository_view | 4 | 0 |
| trojan | KSR3 | https://github.com/RakuLomis/TrafficTracer | github.com::repository_view | 4 | 0 |
| trojan | KSR4 | https://github.com/RakuLomis/TrafficTracer | github.com::repository_view | 4 | 0 |
| trojan | KSR0 | https://github.com/numpy/numpy | github.com::repository_view | 4 | 0 |
| trojan | KSR1 | https://github.com/numpy/numpy | github.com::repository_view | 4 | 0 |
| trojan | KSR2 | https://github.com/numpy/numpy | github.com::repository_view | 4 | 0 |
| trojan | KSR3 | https://github.com/numpy/numpy | github.com::repository_view | 4 | 0 |
| trojan | KSR4 | https://github.com/numpy/numpy | github.com::repository_view | 4 | 0 |
| trojan | KSR0 | https://github.com/pallets/flask | github.com::repository_view | 4 | 0 |
| trojan | KSR1 | https://github.com/pallets/flask | github.com::repository_view | 4 | 0 |
| trojan | KSR2 | https://github.com/pallets/flask | github.com::repository_view | 4 | 0 |
| trojan | KSR3 | https://github.com/pallets/flask | github.com::repository_view | 4 | 0 |
| trojan | KSR4 | https://github.com/pallets/flask | github.com::repository_view | 4 | 0 |
| trojan | KSR0 | https://github.com/python/cpython | github.com::repository_view | 4 | 1 |
| trojan | KSR1 | https://github.com/python/cpython | github.com::repository_view | 4 | 1 |
| trojan | KSR2 | https://github.com/python/cpython | github.com::repository_view | 4 | 1 |
| trojan | KSR3 | https://github.com/python/cpython | github.com::repository_view | 4 | 1 |
| trojan | KSR4 | https://github.com/python/cpython | github.com::repository_view | 4 | 1 |
| trojan | KSR0 | https://github.com/scikit-learn/scikit-learn | github.com::repository_view | 4 | 0 |
| trojan | KSR1 | https://github.com/scikit-learn/scikit-learn | github.com::repository_view | 4 | 0 |
| trojan | KSR2 | https://github.com/scikit-learn/scikit-learn | github.com::repository_view | 4 | 0 |
| trojan | KSR3 | https://github.com/scikit-learn/scikit-learn | github.com::repository_view | 4 | 0 |
| trojan | KSR4 | https://github.com/scikit-learn/scikit-learn | github.com::repository_view | 4 | 0 |
| trojan | KSR0 | https://www.bing.com/search?q=beginner+guitar+chords | bing.com::search_results_view | 4 | 1 |
| trojan | KSR1 | https://www.bing.com/search?q=beginner+guitar+chords | bing.com::search_results_view | 4 | 1 |
| trojan | KSR2 | https://www.bing.com/search?q=beginner+guitar+chords | bing.com::search_results_view | 4 | 1 |
| trojan | KSR3 | https://www.bing.com/search?q=beginner+guitar+chords | bing.com::search_results_view | 4 | 1 |
| trojan | KSR4 | https://www.bing.com/search?q=beginner+guitar+chords | bing.com::search_results_view | 4 | 1 |
| trojan | KSR0 | https://www.bing.com/search?q=indoor+plant+care | bing.com::search_results_view | 4 | 0 |
| trojan | KSR1 | https://www.bing.com/search?q=indoor+plant+care | bing.com::search_results_view | 4 | 0 |
| trojan | KSR2 | https://www.bing.com/search?q=indoor+plant+care | bing.com::search_results_view | 4 | 0 |
| trojan | KSR3 | https://www.bing.com/search?q=indoor+plant+care | bing.com::search_results_view | 4 | 0 |
| trojan | KSR4 | https://www.bing.com/search?q=indoor+plant+care | bing.com::search_results_view | 4 | 0 |
| trojan | KSR0 | https://www.bing.com/search?q=network+traffic+analysis | bing.com::search_results_view | 4 | 0 |
| trojan | KSR1 | https://www.bing.com/search?q=network+traffic+analysis | bing.com::search_results_view | 4 | 0 |
| trojan | KSR2 | https://www.bing.com/search?q=network+traffic+analysis | bing.com::search_results_view | 4 | 0 |
| trojan | KSR3 | https://www.bing.com/search?q=network+traffic+analysis | bing.com::search_results_view | 4 | 0 |
| trojan | KSR4 | https://www.bing.com/search?q=network+traffic+analysis | bing.com::search_results_view | 4 | 1 |
| trojan | KSR0 | https://www.bing.com/search?q=solar+system+facts | bing.com::search_results_view | 4 | 1 |
| trojan | KSR1 | https://www.bing.com/search?q=solar+system+facts | bing.com::search_results_view | 4 | 1 |
| trojan | KSR2 | https://www.bing.com/search?q=solar+system+facts | bing.com::search_results_view | 4 | 1 |
| trojan | KSR3 | https://www.bing.com/search?q=solar+system+facts | bing.com::search_results_view | 4 | 1 |
| trojan | KSR4 | https://www.bing.com/search?q=solar+system+facts | bing.com::search_results_view | 4 | 1 |
| trojan | KSR0 | https://www.bing.com/search?q=sourdough+bread+recipe | bing.com::search_results_view | 4 | 1 |
| trojan | KSR1 | https://www.bing.com/search?q=sourdough+bread+recipe | bing.com::search_results_view | 4 | 1 |
| trojan | KSR2 | https://www.bing.com/search?q=sourdough+bread+recipe | bing.com::search_results_view | 4 | 1 |
| trojan | KSR3 | https://www.bing.com/search?q=sourdough+bread+recipe | bing.com::search_results_view | 4 | 1 |
| trojan | KSR4 | https://www.bing.com/search?q=sourdough+bread+recipe | bing.com::search_results_view | 4 | 1 |
| trojan | KSR0 | https://www.youtube.com/results?search_query=astronomy+documentary | youtube.com::search_results_view | 4 | 0 |
| trojan | KSR1 | https://www.youtube.com/results?search_query=astronomy+documentary | youtube.com::search_results_view | 4 | 0 |
| trojan | KSR2 | https://www.youtube.com/results?search_query=astronomy+documentary | youtube.com::search_results_view | 4 | 0 |
| trojan | KSR3 | https://www.youtube.com/results?search_query=astronomy+documentary | youtube.com::search_results_view | 4 | 0 |
| trojan | KSR4 | https://www.youtube.com/results?search_query=astronomy+documentary | youtube.com::search_results_view | 4 | 0 |
| trojan | KSR0 | https://www.youtube.com/results?search_query=bicycle+maintenance | youtube.com::search_results_view | 4 | 0 |
| trojan | KSR1 | https://www.youtube.com/results?search_query=bicycle+maintenance | youtube.com::search_results_view | 4 | 0 |
| trojan | KSR2 | https://www.youtube.com/results?search_query=bicycle+maintenance | youtube.com::search_results_view | 4 | 0 |
| trojan | KSR3 | https://www.youtube.com/results?search_query=bicycle+maintenance | youtube.com::search_results_view | 4 | 0 |
| trojan | KSR4 | https://www.youtube.com/results?search_query=bicycle+maintenance | youtube.com::search_results_view | 4 | 0 |
| trojan | KSR0 | https://www.youtube.com/results?search_query=bread+baking | youtube.com::search_results_view | 4 | 1 |
| trojan | KSR1 | https://www.youtube.com/results?search_query=bread+baking | youtube.com::search_results_view | 4 | 1 |
| trojan | KSR2 | https://www.youtube.com/results?search_query=bread+baking | youtube.com::search_results_view | 4 | 0 |
| trojan | KSR3 | https://www.youtube.com/results?search_query=bread+baking | youtube.com::search_results_view | 4 | 0 |
| trojan | KSR4 | https://www.youtube.com/results?search_query=bread+baking | youtube.com::search_results_view | 4 | 0 |
| trojan | KSR0 | https://www.youtube.com/results?search_query=piano+practice | youtube.com::search_results_view | 4 | 0 |
| trojan | KSR1 | https://www.youtube.com/results?search_query=piano+practice | youtube.com::search_results_view | 4 | 0 |
| trojan | KSR2 | https://www.youtube.com/results?search_query=piano+practice | youtube.com::search_results_view | 4 | 0 |
| trojan | KSR3 | https://www.youtube.com/results?search_query=piano+practice | youtube.com::search_results_view | 4 | 0 |
| trojan | KSR4 | https://www.youtube.com/results?search_query=piano+practice | youtube.com::search_results_view | 4 | 0 |
| trojan | KSR0 | https://www.youtube.com/results?search_query=watercolor+tutorial | youtube.com::search_results_view | 4 | 1 |
| trojan | KSR1 | https://www.youtube.com/results?search_query=watercolor+tutorial | youtube.com::search_results_view | 4 | 1 |
| trojan | KSR2 | https://www.youtube.com/results?search_query=watercolor+tutorial | youtube.com::search_results_view | 4 | 1 |
| trojan | KSR3 | https://www.youtube.com/results?search_query=watercolor+tutorial | youtube.com::search_results_view | 4 | 1 |
| trojan | KSR4 | https://www.youtube.com/results?search_query=watercolor+tutorial | youtube.com::search_results_view | 4 | 1 |
| trojan | KSR0 | youtube_video:R6MlUcmOul8 | youtube.com::video_playback | 4 | 1 |
| trojan | KSR1 | youtube_video:R6MlUcmOul8 | youtube.com::video_playback | 4 | 1 |
| trojan | KSR2 | youtube_video:R6MlUcmOul8 | youtube.com::video_playback | 4 | 1 |
| trojan | KSR3 | youtube_video:R6MlUcmOul8 | youtube.com::video_playback | 4 | 1 |
| trojan | KSR4 | youtube_video:R6MlUcmOul8 | youtube.com::video_playback | 4 | 1 |
| trojan | KSR0 | youtube_video:aircAruvnKk | youtube.com::video_playback | 4 | 0 |
| trojan | KSR1 | youtube_video:aircAruvnKk | youtube.com::video_playback | 4 | 0 |
| trojan | KSR2 | youtube_video:aircAruvnKk | youtube.com::video_playback | 4 | 0 |
| trojan | KSR3 | youtube_video:aircAruvnKk | youtube.com::video_playback | 4 | 0 |
| trojan | KSR4 | youtube_video:aircAruvnKk | youtube.com::video_playback | 4 | 0 |
| trojan | KSR0 | youtube_video:aqz-KE-bpKQ | youtube.com::video_playback | 4 | 1 |
| trojan | KSR1 | youtube_video:aqz-KE-bpKQ | youtube.com::video_playback | 4 | 1 |
| trojan | KSR2 | youtube_video:aqz-KE-bpKQ | youtube.com::video_playback | 4 | 1 |
| trojan | KSR3 | youtube_video:aqz-KE-bpKQ | youtube.com::video_playback | 4 | 1 |
| trojan | KSR4 | youtube_video:aqz-KE-bpKQ | youtube.com::video_playback | 4 | 1 |
| trojan | KSR0 | youtube_video:eRsGyueVLvQ | youtube.com::video_playback | 4 | 1 |
| trojan | KSR1 | youtube_video:eRsGyueVLvQ | youtube.com::video_playback | 4 | 1 |
| trojan | KSR2 | youtube_video:eRsGyueVLvQ | youtube.com::video_playback | 4 | 1 |
| trojan | KSR3 | youtube_video:eRsGyueVLvQ | youtube.com::video_playback | 4 | 1 |
| trojan | KSR4 | youtube_video:eRsGyueVLvQ | youtube.com::video_playback | 4 | 1 |
| trojan | KSR0 | youtube_video:sAWK0mgrMp4 | youtube.com::video_playback | 4 | 0 |
| trojan | KSR1 | youtube_video:sAWK0mgrMp4 | youtube.com::video_playback | 4 | 0 |
| trojan | KSR2 | youtube_video:sAWK0mgrMp4 | youtube.com::video_playback | 4 | 0 |
| trojan | KSR3 | youtube_video:sAWK0mgrMp4 | youtube.com::video_playback | 4 | 0 |
| trojan | KSR4 | youtube_video:sAWK0mgrMp4 | youtube.com::video_playback | 4 | 1 |
| vless | KSR0 | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | developer.mozilla.org::document_view | 4 | 1 |
| vless | KSR1 | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | developer.mozilla.org::document_view | 4 | 1 |
| vless | KSR2 | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | developer.mozilla.org::document_view | 4 | 1 |
| vless | KSR3 | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | developer.mozilla.org::document_view | 4 | 1 |
| vless | KSR4 | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | developer.mozilla.org::document_view | 4 | 2 |
| vless | KSR0 | https://developer.mozilla.org/en-US/docs/Web/HTTP | developer.mozilla.org::document_view | 4 | 0 |
| vless | KSR1 | https://developer.mozilla.org/en-US/docs/Web/HTTP | developer.mozilla.org::document_view | 4 | 0 |
| vless | KSR2 | https://developer.mozilla.org/en-US/docs/Web/HTTP | developer.mozilla.org::document_view | 4 | 0 |
| vless | KSR3 | https://developer.mozilla.org/en-US/docs/Web/HTTP | developer.mozilla.org::document_view | 4 | 0 |
| vless | KSR4 | https://developer.mozilla.org/en-US/docs/Web/HTTP | developer.mozilla.org::document_view | 4 | 0 |
| vless | KSR0 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | developer.mozilla.org::document_view | 4 | 0 |
| vless | KSR1 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | developer.mozilla.org::document_view | 4 | 0 |
| vless | KSR2 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | developer.mozilla.org::document_view | 4 | 0 |
| vless | KSR3 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | developer.mozilla.org::document_view | 4 | 1 |
| vless | KSR4 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | developer.mozilla.org::document_view | 4 | 0 |
| vless | KSR0 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | developer.mozilla.org::document_view | 4 | 1 |
| vless | KSR1 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | developer.mozilla.org::document_view | 4 | 3 |
| vless | KSR2 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | developer.mozilla.org::document_view | 4 | 1 |
| vless | KSR3 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | developer.mozilla.org::document_view | 4 | 2 |
| vless | KSR4 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | developer.mozilla.org::document_view | 4 | 2 |
| vless | KSR0 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | developer.mozilla.org::document_view | 4 | 2 |
| vless | KSR1 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | developer.mozilla.org::document_view | 4 | 2 |
| vless | KSR2 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | developer.mozilla.org::document_view | 4 | 1 |
| vless | KSR3 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | developer.mozilla.org::document_view | 4 | 2 |
| vless | KSR4 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | developer.mozilla.org::document_view | 4 | 2 |
| vless | KSR0 | https://en.wikipedia.org/wiki/Computer_network | wikipedia.org::article_view | 4 | 1 |
| vless | KSR1 | https://en.wikipedia.org/wiki/Computer_network | wikipedia.org::article_view | 4 | 1 |
| vless | KSR2 | https://en.wikipedia.org/wiki/Computer_network | wikipedia.org::article_view | 4 | 1 |
| vless | KSR3 | https://en.wikipedia.org/wiki/Computer_network | wikipedia.org::article_view | 4 | 1 |
| vless | KSR4 | https://en.wikipedia.org/wiki/Computer_network | wikipedia.org::article_view | 4 | 1 |
| vless | KSR0 | https://en.wikipedia.org/wiki/Domain_Name_System | wikipedia.org::article_view | 4 | 1 |
| vless | KSR1 | https://en.wikipedia.org/wiki/Domain_Name_System | wikipedia.org::article_view | 4 | 1 |
| vless | KSR2 | https://en.wikipedia.org/wiki/Domain_Name_System | wikipedia.org::article_view | 4 | 1 |
| vless | KSR3 | https://en.wikipedia.org/wiki/Domain_Name_System | wikipedia.org::article_view | 4 | 1 |
| vless | KSR4 | https://en.wikipedia.org/wiki/Domain_Name_System | wikipedia.org::article_view | 4 | 1 |
| vless | KSR0 | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | wikipedia.org::article_view | 4 | 1 |
| vless | KSR1 | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | wikipedia.org::article_view | 4 | 1 |
| vless | KSR2 | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | wikipedia.org::article_view | 4 | 1 |
| vless | KSR3 | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | wikipedia.org::article_view | 4 | 1 |
| vless | KSR4 | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | wikipedia.org::article_view | 4 | 1 |
| vless | KSR0 | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | wikipedia.org::article_view | 4 | 0 |
| vless | KSR1 | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | wikipedia.org::article_view | 4 | 0 |
| vless | KSR2 | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | wikipedia.org::article_view | 4 | 0 |
| vless | KSR3 | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | wikipedia.org::article_view | 4 | 0 |
| vless | KSR4 | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | wikipedia.org::article_view | 4 | 1 |
| vless | KSR0 | https://en.wikipedia.org/wiki/Transport_Layer_Security | wikipedia.org::article_view | 4 | 2 |
| vless | KSR1 | https://en.wikipedia.org/wiki/Transport_Layer_Security | wikipedia.org::article_view | 4 | 2 |
| vless | KSR2 | https://en.wikipedia.org/wiki/Transport_Layer_Security | wikipedia.org::article_view | 4 | 2 |
| vless | KSR3 | https://en.wikipedia.org/wiki/Transport_Layer_Security | wikipedia.org::article_view | 4 | 2 |
| vless | KSR4 | https://en.wikipedia.org/wiki/Transport_Layer_Security | wikipedia.org::article_view | 4 | 2 |
| vless | KSR0 | https://github.com/RakuLomis/TrafficTracer | github.com::repository_view | 4 | 0 |
| vless | KSR1 | https://github.com/RakuLomis/TrafficTracer | github.com::repository_view | 4 | 0 |
| vless | KSR2 | https://github.com/RakuLomis/TrafficTracer | github.com::repository_view | 4 | 0 |
| vless | KSR3 | https://github.com/RakuLomis/TrafficTracer | github.com::repository_view | 4 | 0 |
| vless | KSR4 | https://github.com/RakuLomis/TrafficTracer | github.com::repository_view | 4 | 0 |
| vless | KSR0 | https://github.com/numpy/numpy | github.com::repository_view | 4 | 1 |
| vless | KSR1 | https://github.com/numpy/numpy | github.com::repository_view | 4 | 1 |
| vless | KSR2 | https://github.com/numpy/numpy | github.com::repository_view | 4 | 1 |
| vless | KSR3 | https://github.com/numpy/numpy | github.com::repository_view | 4 | 1 |
| vless | KSR4 | https://github.com/numpy/numpy | github.com::repository_view | 4 | 1 |
| vless | KSR0 | https://github.com/pallets/flask | github.com::repository_view | 4 | 1 |
| vless | KSR1 | https://github.com/pallets/flask | github.com::repository_view | 4 | 1 |
| vless | KSR2 | https://github.com/pallets/flask | github.com::repository_view | 4 | 1 |
| vless | KSR3 | https://github.com/pallets/flask | github.com::repository_view | 4 | 1 |
| vless | KSR4 | https://github.com/pallets/flask | github.com::repository_view | 4 | 1 |
| vless | KSR0 | https://github.com/python/cpython | github.com::repository_view | 4 | 0 |
| vless | KSR1 | https://github.com/python/cpython | github.com::repository_view | 4 | 0 |
| vless | KSR2 | https://github.com/python/cpython | github.com::repository_view | 4 | 0 |
| vless | KSR3 | https://github.com/python/cpython | github.com::repository_view | 4 | 0 |
| vless | KSR4 | https://github.com/python/cpython | github.com::repository_view | 4 | 0 |
| vless | KSR0 | https://github.com/scikit-learn/scikit-learn | github.com::repository_view | 4 | 1 |
| vless | KSR1 | https://github.com/scikit-learn/scikit-learn | github.com::repository_view | 4 | 1 |
| vless | KSR2 | https://github.com/scikit-learn/scikit-learn | github.com::repository_view | 4 | 1 |
| vless | KSR3 | https://github.com/scikit-learn/scikit-learn | github.com::repository_view | 4 | 1 |
| vless | KSR4 | https://github.com/scikit-learn/scikit-learn | github.com::repository_view | 4 | 1 |
| vless | KSR0 | https://www.bing.com/search?q=beginner+guitar+chords | bing.com::search_results_view | 4 | 0 |
| vless | KSR1 | https://www.bing.com/search?q=beginner+guitar+chords | bing.com::search_results_view | 4 | 0 |
| vless | KSR2 | https://www.bing.com/search?q=beginner+guitar+chords | bing.com::search_results_view | 4 | 0 |
| vless | KSR3 | https://www.bing.com/search?q=beginner+guitar+chords | bing.com::search_results_view | 4 | 0 |
| vless | KSR4 | https://www.bing.com/search?q=beginner+guitar+chords | bing.com::search_results_view | 4 | 0 |
| vless | KSR0 | https://www.bing.com/search?q=indoor+plant+care | bing.com::search_results_view | 4 | 2 |
| vless | KSR1 | https://www.bing.com/search?q=indoor+plant+care | bing.com::search_results_view | 4 | 2 |
| vless | KSR2 | https://www.bing.com/search?q=indoor+plant+care | bing.com::search_results_view | 4 | 2 |
| vless | KSR3 | https://www.bing.com/search?q=indoor+plant+care | bing.com::search_results_view | 4 | 2 |
| vless | KSR4 | https://www.bing.com/search?q=indoor+plant+care | bing.com::search_results_view | 4 | 4 |
| vless | KSR0 | https://www.bing.com/search?q=network+traffic+analysis | bing.com::search_results_view | 4 | 1 |
| vless | KSR1 | https://www.bing.com/search?q=network+traffic+analysis | bing.com::search_results_view | 4 | 1 |
| vless | KSR2 | https://www.bing.com/search?q=network+traffic+analysis | bing.com::search_results_view | 4 | 1 |
| vless | KSR3 | https://www.bing.com/search?q=network+traffic+analysis | bing.com::search_results_view | 4 | 1 |
| vless | KSR4 | https://www.bing.com/search?q=network+traffic+analysis | bing.com::search_results_view | 4 | 1 |
| vless | KSR0 | https://www.bing.com/search?q=solar+system+facts | bing.com::search_results_view | 4 | 0 |
| vless | KSR1 | https://www.bing.com/search?q=solar+system+facts | bing.com::search_results_view | 4 | 0 |
| vless | KSR2 | https://www.bing.com/search?q=solar+system+facts | bing.com::search_results_view | 4 | 0 |
| vless | KSR3 | https://www.bing.com/search?q=solar+system+facts | bing.com::search_results_view | 4 | 0 |
| vless | KSR4 | https://www.bing.com/search?q=solar+system+facts | bing.com::search_results_view | 4 | 0 |
| vless | KSR0 | https://www.bing.com/search?q=sourdough+bread+recipe | bing.com::search_results_view | 4 | 1 |
| vless | KSR1 | https://www.bing.com/search?q=sourdough+bread+recipe | bing.com::search_results_view | 4 | 1 |
| vless | KSR2 | https://www.bing.com/search?q=sourdough+bread+recipe | bing.com::search_results_view | 4 | 1 |
| vless | KSR3 | https://www.bing.com/search?q=sourdough+bread+recipe | bing.com::search_results_view | 4 | 1 |
| vless | KSR4 | https://www.bing.com/search?q=sourdough+bread+recipe | bing.com::search_results_view | 4 | 1 |
| vless | KSR0 | https://www.youtube.com/results?search_query=astronomy+documentary | youtube.com::search_results_view | 4 | 1 |
| vless | KSR1 | https://www.youtube.com/results?search_query=astronomy+documentary | youtube.com::search_results_view | 4 | 1 |
| vless | KSR2 | https://www.youtube.com/results?search_query=astronomy+documentary | youtube.com::search_results_view | 4 | 1 |
| vless | KSR3 | https://www.youtube.com/results?search_query=astronomy+documentary | youtube.com::search_results_view | 4 | 1 |
| vless | KSR4 | https://www.youtube.com/results?search_query=astronomy+documentary | youtube.com::search_results_view | 4 | 1 |
| vless | KSR0 | https://www.youtube.com/results?search_query=bicycle+maintenance | youtube.com::search_results_view | 4 | 2 |
| vless | KSR1 | https://www.youtube.com/results?search_query=bicycle+maintenance | youtube.com::search_results_view | 4 | 2 |
| vless | KSR2 | https://www.youtube.com/results?search_query=bicycle+maintenance | youtube.com::search_results_view | 4 | 2 |
| vless | KSR3 | https://www.youtube.com/results?search_query=bicycle+maintenance | youtube.com::search_results_view | 4 | 2 |
| vless | KSR4 | https://www.youtube.com/results?search_query=bicycle+maintenance | youtube.com::search_results_view | 4 | 2 |
| vless | KSR0 | https://www.youtube.com/results?search_query=bread+baking | youtube.com::search_results_view | 4 | 1 |
| vless | KSR1 | https://www.youtube.com/results?search_query=bread+baking | youtube.com::search_results_view | 4 | 1 |
| vless | KSR2 | https://www.youtube.com/results?search_query=bread+baking | youtube.com::search_results_view | 4 | 1 |
| vless | KSR3 | https://www.youtube.com/results?search_query=bread+baking | youtube.com::search_results_view | 4 | 0 |
| vless | KSR4 | https://www.youtube.com/results?search_query=bread+baking | youtube.com::search_results_view | 4 | 1 |
| vless | KSR0 | https://www.youtube.com/results?search_query=piano+practice | youtube.com::search_results_view | 4 | 1 |
| vless | KSR1 | https://www.youtube.com/results?search_query=piano+practice | youtube.com::search_results_view | 4 | 1 |
| vless | KSR2 | https://www.youtube.com/results?search_query=piano+practice | youtube.com::search_results_view | 4 | 1 |
| vless | KSR3 | https://www.youtube.com/results?search_query=piano+practice | youtube.com::search_results_view | 4 | 1 |
| vless | KSR4 | https://www.youtube.com/results?search_query=piano+practice | youtube.com::search_results_view | 4 | 1 |
| vless | KSR0 | https://www.youtube.com/results?search_query=watercolor+tutorial | youtube.com::search_results_view | 4 | 1 |
| vless | KSR1 | https://www.youtube.com/results?search_query=watercolor+tutorial | youtube.com::search_results_view | 4 | 0 |
| vless | KSR2 | https://www.youtube.com/results?search_query=watercolor+tutorial | youtube.com::search_results_view | 4 | 1 |
| vless | KSR3 | https://www.youtube.com/results?search_query=watercolor+tutorial | youtube.com::search_results_view | 4 | 1 |
| vless | KSR4 | https://www.youtube.com/results?search_query=watercolor+tutorial | youtube.com::search_results_view | 4 | 1 |
| vless | KSR0 | youtube_video:R6MlUcmOul8 | youtube.com::video_playback | 4 | 0 |
| vless | KSR1 | youtube_video:R6MlUcmOul8 | youtube.com::video_playback | 4 | 0 |
| vless | KSR2 | youtube_video:R6MlUcmOul8 | youtube.com::video_playback | 4 | 0 |
| vless | KSR3 | youtube_video:R6MlUcmOul8 | youtube.com::video_playback | 4 | 0 |
| vless | KSR4 | youtube_video:R6MlUcmOul8 | youtube.com::video_playback | 4 | 0 |
| vless | KSR0 | youtube_video:aircAruvnKk | youtube.com::video_playback | 4 | 1 |
| vless | KSR1 | youtube_video:aircAruvnKk | youtube.com::video_playback | 4 | 1 |
| vless | KSR2 | youtube_video:aircAruvnKk | youtube.com::video_playback | 4 | 1 |
| vless | KSR3 | youtube_video:aircAruvnKk | youtube.com::video_playback | 4 | 1 |
| vless | KSR4 | youtube_video:aircAruvnKk | youtube.com::video_playback | 4 | 1 |
| vless | KSR0 | youtube_video:aqz-KE-bpKQ | youtube.com::video_playback | 4 | 0 |
| vless | KSR1 | youtube_video:aqz-KE-bpKQ | youtube.com::video_playback | 4 | 0 |
| vless | KSR2 | youtube_video:aqz-KE-bpKQ | youtube.com::video_playback | 4 | 0 |
| vless | KSR3 | youtube_video:aqz-KE-bpKQ | youtube.com::video_playback | 4 | 0 |
| vless | KSR4 | youtube_video:aqz-KE-bpKQ | youtube.com::video_playback | 4 | 0 |
| vless | KSR0 | youtube_video:eRsGyueVLvQ | youtube.com::video_playback | 4 | 0 |
| vless | KSR1 | youtube_video:eRsGyueVLvQ | youtube.com::video_playback | 4 | 0 |
| vless | KSR2 | youtube_video:eRsGyueVLvQ | youtube.com::video_playback | 4 | 0 |
| vless | KSR3 | youtube_video:eRsGyueVLvQ | youtube.com::video_playback | 4 | 0 |
| vless | KSR4 | youtube_video:eRsGyueVLvQ | youtube.com::video_playback | 4 | 0 |
| vless | KSR0 | youtube_video:sAWK0mgrMp4 | youtube.com::video_playback | 4 | 0 |
| vless | KSR1 | youtube_video:sAWK0mgrMp4 | youtube.com::video_playback | 4 | 0 |
| vless | KSR2 | youtube_video:sAWK0mgrMp4 | youtube.com::video_playback | 4 | 0 |
| vless | KSR3 | youtube_video:sAWK0mgrMp4 | youtube.com::video_playback | 4 | 0 |
| vless | KSR4 | youtube_video:sAWK0mgrMp4 | youtube.com::video_playback | 4 | 0 |
| vmess | KSR0 | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | developer.mozilla.org::document_view | 4 | 1 |
| vmess | KSR1 | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | developer.mozilla.org::document_view | 4 | 1 |
| vmess | KSR2 | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | developer.mozilla.org::document_view | 4 | 1 |
| vmess | KSR3 | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | developer.mozilla.org::document_view | 4 | 1 |
| vmess | KSR4 | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | developer.mozilla.org::document_view | 4 | 1 |
| vmess | KSR0 | https://developer.mozilla.org/en-US/docs/Web/HTTP | developer.mozilla.org::document_view | 4 | 3 |
| vmess | KSR1 | https://developer.mozilla.org/en-US/docs/Web/HTTP | developer.mozilla.org::document_view | 4 | 3 |
| vmess | KSR2 | https://developer.mozilla.org/en-US/docs/Web/HTTP | developer.mozilla.org::document_view | 4 | 3 |
| vmess | KSR3 | https://developer.mozilla.org/en-US/docs/Web/HTTP | developer.mozilla.org::document_view | 4 | 3 |
| vmess | KSR4 | https://developer.mozilla.org/en-US/docs/Web/HTTP | developer.mozilla.org::document_view | 4 | 3 |
| vmess | KSR0 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | developer.mozilla.org::document_view | 4 | 1 |
| vmess | KSR1 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | developer.mozilla.org::document_view | 4 | 1 |
| vmess | KSR2 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | developer.mozilla.org::document_view | 4 | 0 |
| vmess | KSR3 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | developer.mozilla.org::document_view | 4 | 0 |
| vmess | KSR4 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | developer.mozilla.org::document_view | 4 | 0 |
| vmess | KSR0 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | developer.mozilla.org::document_view | 4 | 2 |
| vmess | KSR1 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | developer.mozilla.org::document_view | 4 | 2 |
| vmess | KSR2 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | developer.mozilla.org::document_view | 4 | 2 |
| vmess | KSR3 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | developer.mozilla.org::document_view | 4 | 2 |
| vmess | KSR4 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | developer.mozilla.org::document_view | 4 | 2 |
| vmess | KSR0 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | developer.mozilla.org::document_view | 4 | 2 |
| vmess | KSR1 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | developer.mozilla.org::document_view | 4 | 2 |
| vmess | KSR2 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | developer.mozilla.org::document_view | 4 | 2 |
| vmess | KSR3 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | developer.mozilla.org::document_view | 4 | 2 |
| vmess | KSR4 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | developer.mozilla.org::document_view | 4 | 2 |
| vmess | KSR0 | https://en.wikipedia.org/wiki/Computer_network | wikipedia.org::article_view | 4 | 0 |
| vmess | KSR1 | https://en.wikipedia.org/wiki/Computer_network | wikipedia.org::article_view | 4 | 0 |
| vmess | KSR2 | https://en.wikipedia.org/wiki/Computer_network | wikipedia.org::article_view | 4 | 0 |
| vmess | KSR3 | https://en.wikipedia.org/wiki/Computer_network | wikipedia.org::article_view | 4 | 0 |
| vmess | KSR4 | https://en.wikipedia.org/wiki/Computer_network | wikipedia.org::article_view | 4 | 0 |
| vmess | KSR0 | https://en.wikipedia.org/wiki/Domain_Name_System | wikipedia.org::article_view | 4 | 2 |
| vmess | KSR1 | https://en.wikipedia.org/wiki/Domain_Name_System | wikipedia.org::article_view | 4 | 2 |
| vmess | KSR2 | https://en.wikipedia.org/wiki/Domain_Name_System | wikipedia.org::article_view | 4 | 2 |
| vmess | KSR3 | https://en.wikipedia.org/wiki/Domain_Name_System | wikipedia.org::article_view | 4 | 2 |
| vmess | KSR4 | https://en.wikipedia.org/wiki/Domain_Name_System | wikipedia.org::article_view | 4 | 2 |
| vmess | KSR0 | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | wikipedia.org::article_view | 4 | 3 |
| vmess | KSR1 | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | wikipedia.org::article_view | 4 | 3 |
| vmess | KSR2 | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | wikipedia.org::article_view | 4 | 3 |
| vmess | KSR3 | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | wikipedia.org::article_view | 4 | 3 |
| vmess | KSR4 | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | wikipedia.org::article_view | 4 | 3 |
| vmess | KSR0 | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | wikipedia.org::article_view | 4 | 1 |
| vmess | KSR1 | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | wikipedia.org::article_view | 4 | 1 |
| vmess | KSR2 | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | wikipedia.org::article_view | 4 | 1 |
| vmess | KSR3 | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | wikipedia.org::article_view | 4 | 1 |
| vmess | KSR4 | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | wikipedia.org::article_view | 4 | 2 |
| vmess | KSR0 | https://en.wikipedia.org/wiki/Transport_Layer_Security | wikipedia.org::article_view | 4 | 0 |
| vmess | KSR1 | https://en.wikipedia.org/wiki/Transport_Layer_Security | wikipedia.org::article_view | 4 | 0 |
| vmess | KSR2 | https://en.wikipedia.org/wiki/Transport_Layer_Security | wikipedia.org::article_view | 4 | 0 |
| vmess | KSR3 | https://en.wikipedia.org/wiki/Transport_Layer_Security | wikipedia.org::article_view | 4 | 0 |
| vmess | KSR4 | https://en.wikipedia.org/wiki/Transport_Layer_Security | wikipedia.org::article_view | 4 | 0 |
| vmess | KSR0 | https://github.com/RakuLomis/TrafficTracer | github.com::repository_view | 4 | 1 |
| vmess | KSR1 | https://github.com/RakuLomis/TrafficTracer | github.com::repository_view | 4 | 1 |
| vmess | KSR2 | https://github.com/RakuLomis/TrafficTracer | github.com::repository_view | 4 | 1 |
| vmess | KSR3 | https://github.com/RakuLomis/TrafficTracer | github.com::repository_view | 4 | 1 |
| vmess | KSR4 | https://github.com/RakuLomis/TrafficTracer | github.com::repository_view | 4 | 1 |
| vmess | KSR0 | https://github.com/numpy/numpy | github.com::repository_view | 4 | 1 |
| vmess | KSR1 | https://github.com/numpy/numpy | github.com::repository_view | 4 | 1 |
| vmess | KSR2 | https://github.com/numpy/numpy | github.com::repository_view | 4 | 1 |
| vmess | KSR3 | https://github.com/numpy/numpy | github.com::repository_view | 4 | 1 |
| vmess | KSR4 | https://github.com/numpy/numpy | github.com::repository_view | 4 | 1 |
| vmess | KSR0 | https://github.com/pallets/flask | github.com::repository_view | 4 | 0 |
| vmess | KSR1 | https://github.com/pallets/flask | github.com::repository_view | 4 | 0 |
| vmess | KSR2 | https://github.com/pallets/flask | github.com::repository_view | 4 | 0 |
| vmess | KSR3 | https://github.com/pallets/flask | github.com::repository_view | 4 | 0 |
| vmess | KSR4 | https://github.com/pallets/flask | github.com::repository_view | 4 | 0 |
| vmess | KSR0 | https://github.com/python/cpython | github.com::repository_view | 4 | 0 |
| vmess | KSR1 | https://github.com/python/cpython | github.com::repository_view | 4 | 0 |
| vmess | KSR2 | https://github.com/python/cpython | github.com::repository_view | 4 | 0 |
| vmess | KSR3 | https://github.com/python/cpython | github.com::repository_view | 4 | 0 |
| vmess | KSR4 | https://github.com/python/cpython | github.com::repository_view | 4 | 0 |
| vmess | KSR0 | https://github.com/scikit-learn/scikit-learn | github.com::repository_view | 4 | 1 |
| vmess | KSR1 | https://github.com/scikit-learn/scikit-learn | github.com::repository_view | 4 | 1 |
| vmess | KSR2 | https://github.com/scikit-learn/scikit-learn | github.com::repository_view | 4 | 1 |
| vmess | KSR3 | https://github.com/scikit-learn/scikit-learn | github.com::repository_view | 4 | 1 |
| vmess | KSR4 | https://github.com/scikit-learn/scikit-learn | github.com::repository_view | 4 | 1 |
| vmess | KSR0 | https://www.bing.com/search?q=beginner+guitar+chords | bing.com::search_results_view | 4 | 2 |
| vmess | KSR1 | https://www.bing.com/search?q=beginner+guitar+chords | bing.com::search_results_view | 4 | 2 |
| vmess | KSR2 | https://www.bing.com/search?q=beginner+guitar+chords | bing.com::search_results_view | 4 | 2 |
| vmess | KSR3 | https://www.bing.com/search?q=beginner+guitar+chords | bing.com::search_results_view | 4 | 2 |
| vmess | KSR4 | https://www.bing.com/search?q=beginner+guitar+chords | bing.com::search_results_view | 4 | 2 |
| vmess | KSR0 | https://www.bing.com/search?q=indoor+plant+care | bing.com::search_results_view | 4 | 1 |
| vmess | KSR1 | https://www.bing.com/search?q=indoor+plant+care | bing.com::search_results_view | 4 | 1 |
| vmess | KSR2 | https://www.bing.com/search?q=indoor+plant+care | bing.com::search_results_view | 4 | 1 |
| vmess | KSR3 | https://www.bing.com/search?q=indoor+plant+care | bing.com::search_results_view | 4 | 1 |
| vmess | KSR4 | https://www.bing.com/search?q=indoor+plant+care | bing.com::search_results_view | 4 | 1 |
| vmess | KSR0 | https://www.bing.com/search?q=network+traffic+analysis | bing.com::search_results_view | 4 | 1 |
| vmess | KSR1 | https://www.bing.com/search?q=network+traffic+analysis | bing.com::search_results_view | 4 | 1 |
| vmess | KSR2 | https://www.bing.com/search?q=network+traffic+analysis | bing.com::search_results_view | 4 | 1 |
| vmess | KSR3 | https://www.bing.com/search?q=network+traffic+analysis | bing.com::search_results_view | 4 | 1 |
| vmess | KSR4 | https://www.bing.com/search?q=network+traffic+analysis | bing.com::search_results_view | 4 | 2 |
| vmess | KSR0 | https://www.bing.com/search?q=solar+system+facts | bing.com::search_results_view | 4 | 1 |
| vmess | KSR1 | https://www.bing.com/search?q=solar+system+facts | bing.com::search_results_view | 4 | 0 |
| vmess | KSR2 | https://www.bing.com/search?q=solar+system+facts | bing.com::search_results_view | 4 | 0 |
| vmess | KSR3 | https://www.bing.com/search?q=solar+system+facts | bing.com::search_results_view | 4 | 1 |
| vmess | KSR4 | https://www.bing.com/search?q=solar+system+facts | bing.com::search_results_view | 4 | 1 |
| vmess | KSR0 | https://www.bing.com/search?q=sourdough+bread+recipe | bing.com::search_results_view | 4 | 0 |
| vmess | KSR1 | https://www.bing.com/search?q=sourdough+bread+recipe | bing.com::search_results_view | 4 | 0 |
| vmess | KSR2 | https://www.bing.com/search?q=sourdough+bread+recipe | bing.com::search_results_view | 4 | 0 |
| vmess | KSR3 | https://www.bing.com/search?q=sourdough+bread+recipe | bing.com::search_results_view | 4 | 0 |
| vmess | KSR4 | https://www.bing.com/search?q=sourdough+bread+recipe | bing.com::search_results_view | 4 | 0 |
| vmess | KSR0 | https://www.youtube.com/results?search_query=astronomy+documentary | youtube.com::search_results_view | 4 | 0 |
| vmess | KSR1 | https://www.youtube.com/results?search_query=astronomy+documentary | youtube.com::search_results_view | 4 | 0 |
| vmess | KSR2 | https://www.youtube.com/results?search_query=astronomy+documentary | youtube.com::search_results_view | 4 | 0 |
| vmess | KSR3 | https://www.youtube.com/results?search_query=astronomy+documentary | youtube.com::search_results_view | 4 | 0 |
| vmess | KSR4 | https://www.youtube.com/results?search_query=astronomy+documentary | youtube.com::search_results_view | 4 | 0 |
| vmess | KSR0 | https://www.youtube.com/results?search_query=bicycle+maintenance | youtube.com::search_results_view | 4 | 2 |
| vmess | KSR1 | https://www.youtube.com/results?search_query=bicycle+maintenance | youtube.com::search_results_view | 4 | 2 |
| vmess | KSR2 | https://www.youtube.com/results?search_query=bicycle+maintenance | youtube.com::search_results_view | 4 | 2 |
| vmess | KSR3 | https://www.youtube.com/results?search_query=bicycle+maintenance | youtube.com::search_results_view | 4 | 2 |
| vmess | KSR4 | https://www.youtube.com/results?search_query=bicycle+maintenance | youtube.com::search_results_view | 4 | 0 |
| vmess | KSR0 | https://www.youtube.com/results?search_query=bread+baking | youtube.com::search_results_view | 4 | 0 |
| vmess | KSR1 | https://www.youtube.com/results?search_query=bread+baking | youtube.com::search_results_view | 4 | 0 |
| vmess | KSR2 | https://www.youtube.com/results?search_query=bread+baking | youtube.com::search_results_view | 4 | 0 |
| vmess | KSR3 | https://www.youtube.com/results?search_query=bread+baking | youtube.com::search_results_view | 4 | 0 |
| vmess | KSR4 | https://www.youtube.com/results?search_query=bread+baking | youtube.com::search_results_view | 4 | 0 |
| vmess | KSR0 | https://www.youtube.com/results?search_query=piano+practice | youtube.com::search_results_view | 4 | 2 |
| vmess | KSR1 | https://www.youtube.com/results?search_query=piano+practice | youtube.com::search_results_view | 4 | 2 |
| vmess | KSR2 | https://www.youtube.com/results?search_query=piano+practice | youtube.com::search_results_view | 4 | 2 |
| vmess | KSR3 | https://www.youtube.com/results?search_query=piano+practice | youtube.com::search_results_view | 4 | 2 |
| vmess | KSR4 | https://www.youtube.com/results?search_query=piano+practice | youtube.com::search_results_view | 4 | 2 |
| vmess | KSR0 | https://www.youtube.com/results?search_query=watercolor+tutorial | youtube.com::search_results_view | 4 | 0 |
| vmess | KSR1 | https://www.youtube.com/results?search_query=watercolor+tutorial | youtube.com::search_results_view | 4 | 0 |
| vmess | KSR2 | https://www.youtube.com/results?search_query=watercolor+tutorial | youtube.com::search_results_view | 4 | 0 |
| vmess | KSR3 | https://www.youtube.com/results?search_query=watercolor+tutorial | youtube.com::search_results_view | 4 | 0 |
| vmess | KSR4 | https://www.youtube.com/results?search_query=watercolor+tutorial | youtube.com::search_results_view | 4 | 0 |
| vmess | KSR0 | youtube_video:R6MlUcmOul8 | youtube.com::video_playback | 4 | 0 |
| vmess | KSR1 | youtube_video:R6MlUcmOul8 | youtube.com::video_playback | 4 | 0 |
| vmess | KSR2 | youtube_video:R6MlUcmOul8 | youtube.com::video_playback | 4 | 0 |
| vmess | KSR3 | youtube_video:R6MlUcmOul8 | youtube.com::video_playback | 4 | 0 |
| vmess | KSR4 | youtube_video:R6MlUcmOul8 | youtube.com::video_playback | 4 | 0 |
| vmess | KSR0 | youtube_video:aircAruvnKk | youtube.com::video_playback | 4 | 1 |
| vmess | KSR1 | youtube_video:aircAruvnKk | youtube.com::video_playback | 4 | 1 |
| vmess | KSR2 | youtube_video:aircAruvnKk | youtube.com::video_playback | 4 | 1 |
| vmess | KSR3 | youtube_video:aircAruvnKk | youtube.com::video_playback | 4 | 1 |
| vmess | KSR4 | youtube_video:aircAruvnKk | youtube.com::video_playback | 4 | 1 |
| vmess | KSR0 | youtube_video:aqz-KE-bpKQ | youtube.com::video_playback | 4 | 0 |
| vmess | KSR1 | youtube_video:aqz-KE-bpKQ | youtube.com::video_playback | 4 | 0 |
| vmess | KSR2 | youtube_video:aqz-KE-bpKQ | youtube.com::video_playback | 4 | 0 |
| vmess | KSR3 | youtube_video:aqz-KE-bpKQ | youtube.com::video_playback | 4 | 0 |
| vmess | KSR4 | youtube_video:aqz-KE-bpKQ | youtube.com::video_playback | 4 | 0 |
| vmess | KSR0 | youtube_video:eRsGyueVLvQ | youtube.com::video_playback | 4 | 0 |
| vmess | KSR1 | youtube_video:eRsGyueVLvQ | youtube.com::video_playback | 4 | 0 |
| vmess | KSR2 | youtube_video:eRsGyueVLvQ | youtube.com::video_playback | 4 | 0 |
| vmess | KSR3 | youtube_video:eRsGyueVLvQ | youtube.com::video_playback | 4 | 0 |
| vmess | KSR4 | youtube_video:eRsGyueVLvQ | youtube.com::video_playback | 4 | 0 |
| vmess | KSR0 | youtube_video:sAWK0mgrMp4 | youtube.com::video_playback | 4 | 1 |
| vmess | KSR1 | youtube_video:sAWK0mgrMp4 | youtube.com::video_playback | 4 | 1 |
| vmess | KSR2 | youtube_video:sAWK0mgrMp4 | youtube.com::video_playback | 4 | 1 |
| vmess | KSR3 | youtube_video:sAWK0mgrMp4 | youtube.com::video_playback | 4 | 1 |
| vmess | KSR4 | youtube_video:sAWK0mgrMp4 | youtube.com::video_playback | 4 | 1 |

## 结论与停止记录

本轮完成已登记的嵌套内容评价。真配核正则的12项主比较中，1项校正区间完全大于0，0项完全小于0；其余区间包含0。KSR2在20个外层部署折角色中有6个选择零权重。

若某部署仅有点估计改善或区间包含零，不能升级为该部署已建立额外收益；也不能把不同臂选择不同t的结果全部归因于矩阵方向。

本轮到此冻结，不增加权重、温度、特征、核条件或网络。不将负结果解释为漂移概率信息永远无用；也不将局部正向点估计扩展为未知部署、跨日期、真实DIRECT或无索引在线识别。推理路由已知且数据资格离线给定，所有部署历史上已被反复研究，因此回顾性选择风险仍在。

## 产物与复现

代码在`eval/kernel_sensitivity_regularization`。本次输出目录为`outputs/kernel-sensitivity-regularization-20261005/run-01`。依次运行setup的inventory/prepare/tests/zero/register，train的inner-matrix/inner-fit/inner-predict/select/outer-matrix/outer-fit/predict，results的evaluate/bootstrap/explain/plot/verify/report。封存后不得重新打包或改变源文件；拟合阶段支持complete.json断点续跑。详细命令见代码README。

预测2400行、选择80条、内层800个核bundle、外层200个核副本并核验原文件、全部谱与因子保存；SHA契约、实际读取台账、优化记录和验证报告均独立存储。本文档依据这些冻结产物生成，未扫描PCAP。
