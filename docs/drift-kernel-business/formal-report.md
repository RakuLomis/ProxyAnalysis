# 漂移概率核与六类业务识别融合实验报告



日期：2026年10月5日。所有拟合、概率映射与推理已在Pytorch312的CUDA上完成。固定四已见部署、30内容、23566对连接、480父访问；原概率测量、采集数据与其他分类结果没有修改。



本轮预登记主F1家族的8项比较中，8项获得家族校正正向区间；直接post概率和小MLP的另8项关键基线比较中，0项获得正向区间。表中负差和跨零区间均保留，没有进行结果驱动调参。



## 1 核心结果与科学问题



| protocol | arm | F1 | accuracy | CE | Brier |
| --- | --- | --- | --- | --- | --- |
| shadowsocks | G0 | 0.633605 | 0.633333 | 1.773970 | 0.827367 |
| shadowsocks | G1 | 0.852836 | 0.850000 | 0.651379 | 0.237950 |
| shadowsocks | G2 | 0.808490 | 0.808333 | 0.826516 | 0.307267 |
| shadowsocks | G3 | 0.386991 | 0.433333 | 1.778638 | 0.828941 |
| shadowsocks | G4 | 0.607694 | 0.608333 | 1.783839 | 0.830686 |
| shadowsocks | G5 | 0.467988 | 0.483333 | 1.791608 | 0.833283 |
| trojan | G0 | 0.688860 | 0.691667 | 1.780223 | 0.829473 |
| trojan | G1 | 0.822704 | 0.825000 | 0.732356 | 0.273935 |
| trojan | G2 | 0.779338 | 0.780556 | 0.884642 | 0.328523 |
| trojan | G3 | 0.078612 | 0.183333 | 1.788020 | 0.832064 |
| trojan | G4 | 0.584930 | 0.600000 | 1.786674 | 0.831634 |
| trojan | G5 | 0.291363 | 0.366667 | 1.791671 | 0.833304 |
| vless | G0 | 0.573210 | 0.575000 | 1.781964 | 0.830063 |
| vless | G1 | 0.808583 | 0.808333 | 0.900850 | 0.322152 |
| vless | G2 | 0.769294 | 0.769444 | 1.057712 | 0.378629 |
| vless | G3 | 0.117261 | 0.208333 | 1.787994 | 0.832072 |
| vless | G4 | 0.415777 | 0.466667 | 1.787372 | 0.831869 |
| vless | G5 | 0.200602 | 0.250000 | 1.791681 | 0.833307 |
| vmess | G0 | 0.656223 | 0.666667 | 1.780899 | 0.829697 |
| vmess | G1 | 0.759006 | 0.758333 | 1.203157 | 0.413686 |
| vmess | G2 | 0.729359 | 0.727778 | 1.292913 | 0.445268 |
| vmess | G3 | 0.079027 | 0.183333 | 1.787373 | 0.831851 |
| vmess | G4 | 0.565249 | 0.566667 | 1.787877 | 0.832038 |
| vmess | G5 | 0.312689 | 0.400000 | 1.791673 | 0.833305 |



G0是直接post业务概率；G1是post LR；G2是post小MLP三seed指标均值；G3是pre业务分布原样迁移；G4是真实配对漂移核；G5是同内容匿名组级核。所有方法使用相同post访问直方图及已知部署路由。



三seed均值不是概率集成，也没有把一个访问复制成三个独立样本。确定性臂只拟合和报告一次。



![四部署F1](../../outputs/drift-kernel-business-20261005/run-01/figures/protocol-F1.png)



## 2 数据范围与业务标签



| protocol | pairs | visits | contents | repetitions |
| --- | --- | --- | --- | --- |
| shadowsocks | 5608 | 120 | 30 | 4 |
| vless | 5957 | 120 | 30 | 4 |
| trojan | 5919 | 120 | 30 | 4 |
| vmess | 6082 | 120 | 30 | 4 |



| label_index | business | contents_per_class | visits_per_protocol |
| --- | --- | --- | --- |
| 0 | bing.com::search_results_view | 5 | 20 |
| 1 | developer.mozilla.org::document_view | 5 | 20 |
| 2 | github.com::repository_view | 5 | 20 |
| 3 | wikipedia.org::article_view | 5 | 20 |
| 4 | youtube.com::search_results_view | 5 | 20 |
| 5 | youtube.com::video_playback | 5 | 20 |



沿用既有全局内容五折。每折24训练内容、6留出内容，每类4训练内容和1测试内容；每部署96训练访问、24测试访问。同内容的全部部署、重复、两侧与内部连接整体划分。最终OOF每部署120访问，业务支持均为20。



AnyTLS不具备当前排他TCP连接模型资格，Hy2是共享carrier单位，未进入主分类。不是沿用旧缺失原因猜测，也不是按性能筛选协议。给定访问范围及合格外层连接集合的条件仍存在，尚未验证无索引在线识别。



## 3 观测与方法



十项是W/U上下行字节、P/E上下行计数、原正载荷包FR run、零阈值唯一新字节run。W/P与U/E分开，原FR没有改名替代。字节9箱、计数10箱，零独立，上界开放，共96维。没有额外加入IP、端口、SNI、URL、时序或连接数。



训练频数按内容等权、内容内访问等权、访问内连接等权，每训练内容质量1。每类训练质量4，总质量24。S从带标签训练pre拟合；T从带标签训练post拟合，类分布平滑alpha=1、边际beta=1。真配与组级Q分别为S乘M1和S乘M2。



Q(y,b)=sum_a S(y,a) K(a,b)。核行是pre箱，列是post箱；没有求逆或把转置视为P(A|B)。十个核是单变量核，不是十维联合模型。推理以post连接箱频率h的平均log评分，字节/事件每项1/12，交互每项1/6，类先验1/6，自然对数，固定softmax温度1。



共同核近似P(B_j|A_j,Y,c)≈P(B_j|A_j,c)是待检验的模型假设。粗箱未必充分表达资源角色与业务相关变化。高跨侧MI或好的统计预测并不保证源业务差异经过核后可区分。



复合分数不是已校准的访问联合后验；CE用自然对数，Brier是六类误差平方和。相同特征频率输入下，判别式方法可以学习不同特征组合；本轮比较没有宣称这些学习器容量或优化预算完全相同。



## 4 固定训练配置与资源



20个LR使用CUDA float64、多类softmax、训练均值/总体标准差、bias不正则、权重正则1e-3、LBFGS最多500步、strong_wolfe。



60个MLP使用96→32→6、ReLU、3302参数，CUDA float32，AdamW lr=1e-3、weight_decay=1e-4，batch96，固定1000个更新；无dropout/BatchNorm/early stopping。seed为20261005、20261006、20261007。不按留出结果选择检查点。标准化先在float64计算，再转float32。



全部预处理只拟合训练post访问。生成式S/T/Q为闭式CUDA计算，复用每外层训练区的200个主核文件，没有重跑旧1150文件或新增SSL。



| protocol | fold | arm | seed | seconds | iterations | updates | objective | final_training_CE |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| shadowsocks | 0 | G1 |  | 2.474133 | 77.000000 |  | 0.031416 |  |
| shadowsocks | 0 | G2 | 20261005.000000 | 0.894901 |  | 1000.000000 |  | 0.001621 |
| shadowsocks | 0 | G2 | 20261006.000000 | 0.847401 |  | 1000.000000 |  | 0.001510 |
| shadowsocks | 0 | G2 | 20261007.000000 | 0.789834 |  | 1000.000000 |  | 0.001627 |
| vless | 0 | G1 |  | 1.372925 | 74.000000 |  | 0.041682 |  |
| vless | 0 | G2 | 20261005.000000 | 0.807980 |  | 1000.000000 |  | 0.002699 |
| vless | 0 | G2 | 20261006.000000 | 0.798247 |  | 1000.000000 |  | 0.002585 |
| vless | 0 | G2 | 20261007.000000 | 0.807623 |  | 1000.000000 |  | 0.002542 |
| trojan | 0 | G1 |  | 2.143836 | 94.000000 |  | 0.039730 |  |
| trojan | 0 | G2 | 20261005.000000 | 0.847295 |  | 1000.000000 |  | 0.002424 |
| trojan | 0 | G2 | 20261006.000000 | 0.861510 |  | 1000.000000 |  | 0.002360 |
| trojan | 0 | G2 | 20261007.000000 | 0.839075 |  | 1000.000000 |  | 0.002540 |
| vmess | 0 | G1 |  | 1.075910 | 66.000000 |  | 0.043488 |  |
| vmess | 0 | G2 | 20261005.000000 | 0.821817 |  | 1000.000000 |  | 0.002704 |
| vmess | 0 | G2 | 20261006.000000 | 0.800476 |  | 1000.000000 |  | 0.002556 |
| vmess | 0 | G2 | 20261007.000000 | 0.782485 |  | 1000.000000 |  | 0.002965 |
| shadowsocks | 1 | G1 |  | 1.436253 | 77.000000 |  | 0.026859 |  |
| shadowsocks | 1 | G2 | 20261005.000000 | 0.754874 |  | 1000.000000 |  | 0.001534 |
| shadowsocks | 1 | G2 | 20261006.000000 | 0.793122 |  | 1000.000000 |  | 0.001388 |
| shadowsocks | 1 | G2 | 20261007.000000 | 0.854303 |  | 1000.000000 |  | 0.001618 |
| vless | 1 | G1 |  | 1.373238 | 72.000000 |  | 0.045683 |  |
| vless | 1 | G2 | 20261005.000000 | 0.860461 |  | 1000.000000 |  | 0.002675 |
| vless | 1 | G2 | 20261006.000000 | 0.811827 |  | 1000.000000 |  | 0.002715 |
| vless | 1 | G2 | 20261007.000000 | 0.771340 |  | 1000.000000 |  | 0.002621 |
| trojan | 1 | G1 |  | 1.355971 | 73.000000 |  | 0.039210 |  |
| trojan | 1 | G2 | 20261005.000000 | 0.777250 |  | 1000.000000 |  | 0.002309 |
| trojan | 1 | G2 | 20261006.000000 | 0.799067 |  | 1000.000000 |  | 0.002223 |
| trojan | 1 | G2 | 20261007.000000 | 0.756678 |  | 1000.000000 |  | 0.002444 |
| vmess | 1 | G1 |  | 1.266331 | 72.000000 |  | 0.047866 |  |
| vmess | 1 | G2 | 20261005.000000 | 0.761600 |  | 1000.000000 |  | 0.002735 |
| vmess | 1 | G2 | 20261006.000000 | 0.775267 |  | 1000.000000 |  | 0.002643 |
| vmess | 1 | G2 | 20261007.000000 | 0.810022 |  | 1000.000000 |  | 0.002799 |
| shadowsocks | 2 | G1 |  | 1.512684 | 78.000000 |  | 0.025480 |  |
| shadowsocks | 2 | G2 | 20261005.000000 | 0.755738 |  | 1000.000000 |  | 0.001396 |
| shadowsocks | 2 | G2 | 20261006.000000 | 0.761999 |  | 1000.000000 |  | 0.001385 |
| shadowsocks | 2 | G2 | 20261007.000000 | 0.745430 |  | 1000.000000 |  | 0.001528 |
| vless | 2 | G1 |  | 1.407635 | 75.000000 |  | 0.045653 |  |
| vless | 2 | G2 | 20261005.000000 | 0.773520 |  | 1000.000000 |  | 0.002603 |
| vless | 2 | G2 | 20261006.000000 | 0.825517 |  | 1000.000000 |  | 0.002619 |
| vless | 2 | G2 | 20261007.000000 | 0.824491 |  | 1000.000000 |  | 0.002695 |
| trojan | 2 | G1 |  | 1.691909 | 81.000000 |  | 0.038805 |  |
| trojan | 2 | G2 | 20261005.000000 | 0.847662 |  | 1000.000000 |  | 0.002365 |
| trojan | 2 | G2 | 20261006.000000 | 0.805515 |  | 1000.000000 |  | 0.002375 |
| trojan | 2 | G2 | 20261007.000000 | 0.784005 |  | 1000.000000 |  | 0.002452 |
| vmess | 2 | G1 |  | 1.565188 | 79.000000 |  | 0.047478 |  |
| vmess | 2 | G2 | 20261005.000000 | 0.749797 |  | 1000.000000 |  | 0.002489 |
| vmess | 2 | G2 | 20261006.000000 | 0.757851 |  | 1000.000000 |  | 0.002687 |
| vmess | 2 | G2 | 20261007.000000 | 0.814174 |  | 1000.000000 |  | 0.002581 |
| shadowsocks | 3 | G1 |  | 1.460207 | 76.000000 |  | 0.031525 |  |
| shadowsocks | 3 | G2 | 20261005.000000 | 0.822165 |  | 1000.000000 |  | 0.001560 |
| shadowsocks | 3 | G2 | 20261006.000000 | 0.807988 |  | 1000.000000 |  | 0.001553 |
| shadowsocks | 3 | G2 | 20261007.000000 | 0.788879 |  | 1000.000000 |  | 0.001762 |
| vless | 3 | G1 |  | 1.335071 | 74.000000 |  | 0.049957 |  |
| vless | 3 | G2 | 20261005.000000 | 0.828112 |  | 1000.000000 |  | 0.002784 |
| vless | 3 | G2 | 20261006.000000 | 0.821699 |  | 1000.000000 |  | 0.002656 |
| vless | 3 | G2 | 20261007.000000 | 0.774986 |  | 1000.000000 |  | 0.002840 |
| trojan | 3 | G1 |  | 1.325611 | 72.000000 |  | 0.036912 |  |
| trojan | 3 | G2 | 20261005.000000 | 0.878362 |  | 1000.000000 |  | 0.002140 |
| trojan | 3 | G2 | 20261006.000000 | 0.828766 |  | 1000.000000 |  | 0.002136 |
| trojan | 3 | G2 | 20261007.000000 | 0.834876 |  | 1000.000000 |  | 0.002381 |
| vmess | 3 | G1 |  | 1.600815 | 79.000000 |  | 0.045815 |  |
| vmess | 3 | G2 | 20261005.000000 | 0.765391 |  | 1000.000000 |  | 0.002812 |
| vmess | 3 | G2 | 20261006.000000 | 0.768829 |  | 1000.000000 |  | 0.002724 |
| vmess | 3 | G2 | 20261007.000000 | 0.746927 |  | 1000.000000 |  | 0.003023 |
| shadowsocks | 4 | G1 |  | 1.187861 | 68.000000 |  | 0.028669 |  |
| shadowsocks | 4 | G2 | 20261005.000000 | 0.786350 |  | 1000.000000 |  | 0.001564 |
| shadowsocks | 4 | G2 | 20261006.000000 | 0.850167 |  | 1000.000000 |  | 0.001486 |
| shadowsocks | 4 | G2 | 20261007.000000 | 0.835435 |  | 1000.000000 |  | 0.001657 |
| vless | 4 | G1 |  | 1.387481 | 75.000000 |  | 0.044313 |  |
| vless | 4 | G2 | 20261005.000000 | 0.774431 |  | 1000.000000 |  | 0.002596 |
| vless | 4 | G2 | 20261006.000000 | 0.771234 |  | 1000.000000 |  | 0.002459 |
| vless | 4 | G2 | 20261007.000000 | 0.783999 |  | 1000.000000 |  | 0.002563 |
| trojan | 4 | G1 |  | 1.264594 | 71.000000 |  | 0.034389 |  |
| trojan | 4 | G2 | 20261005.000000 | 0.783249 |  | 1000.000000 |  | 0.002211 |
| trojan | 4 | G2 | 20261006.000000 | 0.748155 |  | 1000.000000 |  | 0.002031 |
| trojan | 4 | G2 | 20261007.000000 | 0.757271 |  | 1000.000000 |  | 0.002204 |
| vmess | 4 | G1 |  | 1.120220 | 66.000000 |  | 0.039153 |  |
| vmess | 4 | G2 | 20261005.000000 | 0.806576 |  | 1000.000000 |  | 0.002314 |
| vmess | 4 | G2 | 20261006.000000 | 0.816707 |  | 1000.000000 |  | 0.002249 |
| vmess | 4 | G2 | 20261007.000000 | 0.799660 |  | 1000.000000 |  | 0.002366 |



## 5 预登记主比较与不确定性



| protocol | comparison | point | lo95 | hi95 | family_lo | family_hi | family_positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| shadowsocks | G4-G3 | 0.220703 | 0.142811 | 0.300031 | 0.119334 | 0.332820 | 是 |
| shadowsocks | G4-G5 | 0.139706 | 0.057907 | 0.224838 | 0.030729 | 0.263751 | 是 |
| vless | G4-G3 | 0.298516 | 0.222641 | 0.374169 | 0.194786 | 0.404217 | 是 |
| vless | G4-G5 | 0.215175 | 0.119170 | 0.319892 | 0.084451 | 0.359696 | 是 |
| trojan | G4-G3 | 0.506317 | 0.415930 | 0.596724 | 0.379345 | 0.630277 | 是 |
| trojan | G4-G5 | 0.293567 | 0.187895 | 0.392783 | 0.140783 | 0.429616 | 是 |
| vmess | G4-G3 | 0.486222 | 0.391766 | 0.579931 | 0.353141 | 0.618962 | 是 |
| vmess | G4-G5 | 0.252560 | 0.151241 | 0.346966 | 0.112876 | 0.388600 | 是 |



主问题分别是真配G4是否优于原样G3，以及是否优于组级G5；这两种差异不能互相替代。主8项单独校正，不借用旧概率预测8项的结论。



## 6 充分post基线比较



| protocol | comparison | point | lo95 | hi95 | family_lo | family_hi | family_positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| shadowsocks | G4-G0 | -0.025911 | -0.094117 | 0.038449 | -0.123109 | 0.061691 | 否 |
| shadowsocks | G4-G2 | -0.200796 | -0.329481 | -0.073220 | -0.373584 | -0.022797 | 否 |
| vless | G4-G0 | -0.157433 | -0.211535 | -0.099299 | -0.230247 | -0.073123 | 否 |
| vless | G4-G2 | -0.353517 | -0.442039 | -0.268003 | -0.475448 | -0.235737 | 否 |
| trojan | G4-G0 | -0.103931 | -0.195631 | -0.019011 | -0.231510 | 0.011293 | 否 |
| trojan | G4-G2 | -0.194409 | -0.278578 | -0.116412 | -0.308521 | -0.087243 | 否 |
| vmess | G4-G0 | -0.090974 | -0.195592 | 0.005798 | -0.240243 | 0.038698 | 否 |
| vmess | G4-G2 | -0.164110 | -0.280401 | -0.050442 | -0.320607 | -0.008146 | 否 |



| protocol | comparison | point | lo95 | hi95 |
| --- | --- | --- | --- | --- |
| shadowsocks | G4-G1 | -0.245141 | -0.377702 | -0.107446 |
| vless | G4-G1 | -0.392807 | -0.485404 | -0.303807 |
| trojan | G4-G1 | -0.237774 | -0.323913 | -0.158496 |
| vmess | G4-G1 | -0.193757 | -0.311241 | -0.079520 |



G4优于G3但未优于充分post基线时，只能说明漂移模型帮助该生成式迁移链，不能宣布超越常规目标侧监督。G4与G5接近也不证明统计等效；本轮没有登记等效界限。



所有区间来自10000次六业务分层的内容组bootstrap，携带内容的全部重复和部署，共享同一抽样。主和基线家族各8项，Bonferroni置信度99.375%。区间条件于固定模型，不包含重训练、外部数据或研究者历史选择不确定性。每类仅5内容。



![增量区间](../../outputs/drift-kernel-business-20261005/run-01/figures/F1-contrasts.png)



## 7 部署等权与逐seed结果



| arm | protocol_equal_F1 | worst_protocol_F1 | protocol_equal_CE | protocol_equal_Brier |
| --- | --- | --- | --- | --- |
| G0 | 0.637975 | 0.573210 | 1.779264 | 0.829150 |
| G1 | 0.810782 | 0.759006 | 0.871935 | 0.311930 |
| G2 | 0.771621 | 0.729359 | 1.015446 | 0.364922 |
| G3 | 0.165473 | 0.078612 | 1.785506 | 0.831232 |
| G4 | 0.543412 | 0.415777 | 1.786441 | 0.831557 |
| G5 | 0.318160 | 0.200602 | 1.791658 | 0.833300 |



| protocol | seed | F1 | accuracy | CE | Brier |
| --- | --- | --- | --- | --- | --- |
| shadowsocks | 20261005 | 0.830055 | 0.833333 | 0.813629 | 0.296774 |
| shadowsocks | 20261006 | 0.776331 | 0.775000 | 0.805589 | 0.319370 |
| shadowsocks | 20261007 | 0.819085 | 0.816667 | 0.860330 | 0.305659 |
| trojan | 20261005 | 0.774257 | 0.775000 | 0.831459 | 0.340046 |
| trojan | 20261006 | 0.781397 | 0.783333 | 0.903269 | 0.329055 |
| trojan | 20261007 | 0.782361 | 0.783333 | 0.919199 | 0.316469 |
| vless | 20261005 | 0.783495 | 0.783333 | 0.944485 | 0.347928 |
| vless | 20261006 | 0.749112 | 0.750000 | 1.075613 | 0.397842 |
| vless | 20261007 | 0.775276 | 0.775000 | 1.153038 | 0.390116 |
| vmess | 20261005 | 0.750304 | 0.750000 | 1.272231 | 0.421052 |
| vmess | 20261006 | 0.709445 | 0.708333 | 1.299242 | 0.465209 |
| vmess | 20261007 | 0.728329 | 0.725000 | 1.307267 | 0.449541 |



| protocol | F1_min | F1_max | CE_min | CE_max | Brier_min | Brier_max |
| --- | --- | --- | --- | --- | --- | --- |
| shadowsocks | 0.776331 | 0.830055 | 0.805589 | 0.860330 | 0.296774 | 0.319370 |
| trojan | 0.774257 | 0.782361 | 0.831459 | 0.919199 | 0.316469 | 0.340046 |
| vless | 0.749112 | 0.783495 | 0.944485 | 1.153038 | 0.347928 | 0.397842 |
| vmess | 0.709445 | 0.750304 | 1.272231 | 1.307267 | 0.421052 | 0.465209 |



## 8 逐类别与混淆矩阵



| protocol | arm | label | F1 | precision | recall | support |
| --- | --- | --- | --- | --- | --- | --- |
| shadowsocks | G0 | bing.com::search_results_view | 0.487805 | 0.476190 | 0.500000 | 20.000000 |
| shadowsocks | G0 | developer.mozilla.org::document_view | 0.594595 | 0.647059 | 0.550000 | 20.000000 |
| shadowsocks | G0 | github.com::repository_view | 0.842105 | 0.888889 | 0.800000 | 20.000000 |
| shadowsocks | G0 | wikipedia.org::article_view | 0.577778 | 0.520000 | 0.650000 | 20.000000 |
| shadowsocks | G0 | youtube.com::search_results_view | 0.711111 | 0.640000 | 0.800000 | 20.000000 |
| shadowsocks | G0 | youtube.com::video_playback | 0.588235 | 0.714286 | 0.500000 | 20.000000 |
| shadowsocks | G1 | bing.com::search_results_view | 0.756757 | 0.823529 | 0.700000 | 20.000000 |
| shadowsocks | G1 | developer.mozilla.org::document_view | 0.666667 | 0.600000 | 0.750000 | 20.000000 |
| shadowsocks | G1 | github.com::repository_view | 0.974359 | 1.000000 | 0.950000 | 20.000000 |
| shadowsocks | G1 | wikipedia.org::article_view | 0.769231 | 0.789474 | 0.750000 | 20.000000 |
| shadowsocks | G1 | youtube.com::search_results_view | 0.950000 | 0.950000 | 0.950000 | 20.000000 |
| shadowsocks | G1 | youtube.com::video_playback | 1.000000 | 1.000000 | 1.000000 | 20.000000 |
| shadowsocks | G2 | bing.com::search_results_view | 0.738233 | 0.744709 | 0.733333 | 20.000000 |
| shadowsocks | G2 | developer.mozilla.org::document_view | 0.589302 | 0.601461 | 0.583333 | 20.000000 |
| shadowsocks | G2 | github.com::repository_view | 0.949145 | 0.965789 | 0.933333 | 20.000000 |
| shadowsocks | G2 | wikipedia.org::article_view | 0.747871 | 0.730519 | 0.766667 | 20.000000 |
| shadowsocks | G2 | youtube.com::search_results_view | 0.902033 | 0.888095 | 0.916667 | 20.000000 |
| shadowsocks | G2 | youtube.com::video_playback | 0.924359 | 0.932456 | 0.916667 | 20.000000 |
| shadowsocks | G3 | bing.com::search_results_view | 0.448980 | 0.379310 | 0.550000 | 20.000000 |
| shadowsocks | G3 | developer.mozilla.org::document_view | 0.333333 | 0.375000 | 0.300000 | 20.000000 |
| shadowsocks | G3 | github.com::repository_view | 0.000000 | 0.000000 | 0.000000 | 20.000000 |
| shadowsocks | G3 | wikipedia.org::article_view | 0.470588 | 0.571429 | 0.400000 | 20.000000 |
| shadowsocks | G3 | youtube.com::search_results_view | 0.535714 | 0.416667 | 0.750000 | 20.000000 |
| shadowsocks | G3 | youtube.com::video_playback | 0.533333 | 0.480000 | 0.600000 | 20.000000 |
| shadowsocks | G4 | bing.com::search_results_view | 0.480000 | 0.400000 | 0.600000 | 20.000000 |
| shadowsocks | G4 | developer.mozilla.org::document_view | 0.400000 | 0.466667 | 0.350000 | 20.000000 |
| shadowsocks | G4 | github.com::repository_view | 0.820513 | 0.842105 | 0.800000 | 20.000000 |
| shadowsocks | G4 | wikipedia.org::article_view | 0.650000 | 0.650000 | 0.650000 | 20.000000 |
| shadowsocks | G4 | youtube.com::search_results_view | 0.695652 | 0.615385 | 0.800000 | 20.000000 |
| shadowsocks | G4 | youtube.com::video_playback | 0.600000 | 0.900000 | 0.450000 | 20.000000 |
| shadowsocks | G5 | bing.com::search_results_view | 0.358974 | 0.368421 | 0.350000 | 20.000000 |
| shadowsocks | G5 | developer.mozilla.org::document_view | 0.230769 | 0.500000 | 0.150000 | 20.000000 |
| shadowsocks | G5 | github.com::repository_view | 0.789474 | 0.833333 | 0.750000 | 20.000000 |
| shadowsocks | G5 | wikipedia.org::article_view | 0.487805 | 0.476190 | 0.500000 | 20.000000 |
| shadowsocks | G5 | youtube.com::search_results_view | 0.508475 | 0.384615 | 0.750000 | 20.000000 |
| shadowsocks | G5 | youtube.com::video_playback | 0.432432 | 0.470588 | 0.400000 | 20.000000 |
| trojan | G0 | bing.com::search_results_view | 0.512821 | 0.526316 | 0.500000 | 20.000000 |
| trojan | G0 | developer.mozilla.org::document_view | 0.564103 | 0.578947 | 0.550000 | 20.000000 |
| trojan | G0 | github.com::repository_view | 0.904762 | 0.863636 | 0.950000 | 20.000000 |
| trojan | G0 | wikipedia.org::article_view | 0.682927 | 0.666667 | 0.700000 | 20.000000 |
| trojan | G0 | youtube.com::search_results_view | 0.731707 | 0.714286 | 0.750000 | 20.000000 |
| trojan | G0 | youtube.com::video_playback | 0.736842 | 0.777778 | 0.700000 | 20.000000 |
| trojan | G1 | bing.com::search_results_view | 0.809524 | 0.772727 | 0.850000 | 20.000000 |
| trojan | G1 | developer.mozilla.org::document_view | 0.648649 | 0.705882 | 0.600000 | 20.000000 |
| trojan | G1 | github.com::repository_view | 0.950000 | 0.950000 | 0.950000 | 20.000000 |
| trojan | G1 | wikipedia.org::article_view | 0.800000 | 0.800000 | 0.800000 | 20.000000 |
| trojan | G1 | youtube.com::search_results_view | 0.878049 | 0.857143 | 0.900000 | 20.000000 |
| trojan | G1 | youtube.com::video_playback | 0.850000 | 0.850000 | 0.850000 | 20.000000 |
| trojan | G2 | bing.com::search_results_view | 0.709640 | 0.687590 | 0.733333 | 20.000000 |
| trojan | G2 | developer.mozilla.org::document_view | 0.660977 | 0.712418 | 0.616667 | 20.000000 |
| trojan | G2 | github.com::repository_view | 0.884869 | 0.871839 | 0.900000 | 20.000000 |
| trojan | G2 | wikipedia.org::article_view | 0.793496 | 0.787302 | 0.800000 | 20.000000 |
| trojan | G2 | youtube.com::search_results_view | 0.807207 | 0.854902 | 0.766667 | 20.000000 |
| trojan | G2 | youtube.com::video_playback | 0.819841 | 0.780909 | 0.866667 | 20.000000 |
| trojan | G3 | bing.com::search_results_view | 0.181818 | 1.000000 | 0.100000 | 20.000000 |
| trojan | G3 | developer.mozilla.org::document_view | 0.000000 | 0.000000 | 0.000000 | 20.000000 |
| trojan | G3 | github.com::repository_view | 0.000000 | 0.000000 | 0.000000 | 20.000000 |
| trojan | G3 | wikipedia.org::article_view | 0.000000 | 0.000000 | 0.000000 | 20.000000 |
| trojan | G3 | youtube.com::search_results_view | 0.289855 | 0.169492 | 1.000000 | 20.000000 |
| trojan | G3 | youtube.com::video_playback | 0.000000 | 0.000000 | 0.000000 | 20.000000 |
| trojan | G4 | bing.com::search_results_view | 0.622222 | 0.560000 | 0.700000 | 20.000000 |
| trojan | G4 | developer.mozilla.org::document_view | 0.545455 | 0.500000 | 0.600000 | 20.000000 |
| trojan | G4 | github.com::repository_view | 0.692308 | 0.562500 | 0.900000 | 20.000000 |
| trojan | G4 | wikipedia.org::article_view | 0.500000 | 0.875000 | 0.350000 | 20.000000 |
| trojan | G4 | youtube.com::search_results_view | 0.682927 | 0.666667 | 0.700000 | 20.000000 |
| trojan | G4 | youtube.com::video_playback | 0.466667 | 0.700000 | 0.350000 | 20.000000 |
| trojan | G5 | bing.com::search_results_view | 0.074074 | 0.142857 | 0.050000 | 20.000000 |
| trojan | G5 | developer.mozilla.org::document_view | 0.000000 | 0.000000 | 0.000000 | 20.000000 |
| trojan | G5 | github.com::repository_view | 0.545455 | 0.692308 | 0.450000 | 20.000000 |
| trojan | G5 | wikipedia.org::article_view | 0.410256 | 0.275862 | 0.800000 | 20.000000 |
| trojan | G5 | youtube.com::search_results_view | 0.166667 | 0.500000 | 0.100000 | 20.000000 |
| trojan | G5 | youtube.com::video_playback | 0.551724 | 0.421053 | 0.800000 | 20.000000 |
| vless | G0 | bing.com::search_results_view | 0.516129 | 0.727273 | 0.400000 | 20.000000 |
| vless | G0 | developer.mozilla.org::document_view | 0.634146 | 0.619048 | 0.650000 | 20.000000 |
| vless | G0 | github.com::repository_view | 0.750000 | 0.750000 | 0.750000 | 20.000000 |
| vless | G0 | wikipedia.org::article_view | 0.518519 | 0.411765 | 0.700000 | 20.000000 |
| vless | G0 | youtube.com::search_results_view | 0.388889 | 0.437500 | 0.350000 | 20.000000 |
| vless | G0 | youtube.com::video_playback | 0.631579 | 0.666667 | 0.600000 | 20.000000 |
| vless | G1 | bing.com::search_results_view | 0.820513 | 0.842105 | 0.800000 | 20.000000 |
| vless | G1 | developer.mozilla.org::document_view | 0.800000 | 0.800000 | 0.800000 | 20.000000 |
| vless | G1 | github.com::repository_view | 0.871795 | 0.894737 | 0.850000 | 20.000000 |
| vless | G1 | wikipedia.org::article_view | 0.697674 | 0.652174 | 0.750000 | 20.000000 |
| vless | G1 | youtube.com::search_results_view | 0.756757 | 0.823529 | 0.700000 | 20.000000 |
| vless | G1 | youtube.com::video_playback | 0.904762 | 0.863636 | 0.950000 | 20.000000 |
| vless | G2 | bing.com::search_results_view | 0.717386 | 0.736355 | 0.700000 | 20.000000 |
| vless | G2 | developer.mozilla.org::document_view | 0.695479 | 0.709552 | 0.683333 | 20.000000 |
| vless | G2 | github.com::repository_view | 0.871795 | 0.894737 | 0.850000 | 20.000000 |
| vless | G2 | wikipedia.org::article_view | 0.672087 | 0.646465 | 0.700000 | 20.000000 |
| vless | G2 | youtube.com::search_results_view | 0.762821 | 0.776316 | 0.750000 | 20.000000 |
| vless | G2 | youtube.com::video_playback | 0.896200 | 0.862664 | 0.933333 | 20.000000 |
| vless | G3 | bing.com::search_results_view | 0.310345 | 0.236842 | 0.450000 | 20.000000 |
| vless | G3 | developer.mozilla.org::document_view | 0.000000 | 0.000000 | 0.000000 | 20.000000 |
| vless | G3 | github.com::repository_view | 0.000000 | 0.000000 | 0.000000 | 20.000000 |
| vless | G3 | wikipedia.org::article_view | 0.000000 | 0.000000 | 0.000000 | 20.000000 |
| vless | G3 | youtube.com::search_results_view | 0.074074 | 0.142857 | 0.050000 | 20.000000 |
| vless | G3 | youtube.com::video_playback | 0.319149 | 0.202703 | 0.750000 | 20.000000 |
| vless | G4 | bing.com::search_results_view | 0.380952 | 0.363636 | 0.400000 | 20.000000 |
| vless | G4 | developer.mozilla.org::document_view | 0.481481 | 0.382353 | 0.650000 | 20.000000 |
| vless | G4 | github.com::repository_view | 0.653061 | 0.551724 | 0.800000 | 20.000000 |
| vless | G4 | wikipedia.org::article_view | 0.312500 | 0.416667 | 0.250000 | 20.000000 |
| vless | G4 | youtube.com::search_results_view | 0.000000 | 0.000000 | 0.000000 | 20.000000 |
| vless | G4 | youtube.com::video_playback | 0.666667 | 0.636364 | 0.700000 | 20.000000 |
| vless | G5 | bing.com::search_results_view | 0.000000 | 0.000000 | 0.000000 | 20.000000 |
| vless | G5 | developer.mozilla.org::document_view | 0.000000 | 0.000000 | 0.000000 | 20.000000 |
| vless | G5 | github.com::repository_view | 0.206897 | 0.333333 | 0.150000 | 20.000000 |
| vless | G5 | wikipedia.org::article_view | 0.323529 | 0.229167 | 0.550000 | 20.000000 |
| vless | G5 | youtube.com::search_results_view | 0.328358 | 0.234043 | 0.550000 | 20.000000 |
| vless | G5 | youtube.com::video_playback | 0.344828 | 0.555556 | 0.250000 | 20.000000 |
| vmess | G0 | bing.com::search_results_view | 0.514286 | 0.600000 | 0.450000 | 20.000000 |
| vmess | G0 | developer.mozilla.org::document_view | 0.424242 | 0.538462 | 0.350000 | 20.000000 |
| vmess | G0 | github.com::repository_view | 0.850000 | 0.850000 | 0.850000 | 20.000000 |
| vmess | G0 | wikipedia.org::article_view | 0.625000 | 0.535714 | 0.750000 | 20.000000 |
| vmess | G0 | youtube.com::search_results_view | 0.714286 | 0.681818 | 0.750000 | 20.000000 |
| vmess | G0 | youtube.com::video_playback | 0.809524 | 0.772727 | 0.850000 | 20.000000 |
| vmess | G1 | bing.com::search_results_view | 0.750000 | 0.750000 | 0.750000 | 20.000000 |
| vmess | G1 | developer.mozilla.org::document_view | 0.594595 | 0.647059 | 0.550000 | 20.000000 |
| vmess | G1 | github.com::repository_view | 0.850000 | 0.850000 | 0.850000 | 20.000000 |
| vmess | G1 | wikipedia.org::article_view | 0.636364 | 0.583333 | 0.700000 | 20.000000 |
| vmess | G1 | youtube.com::search_results_view | 0.800000 | 0.800000 | 0.800000 | 20.000000 |
| vmess | G1 | youtube.com::video_playback | 0.923077 | 0.947368 | 0.900000 | 20.000000 |
| vmess | G2 | bing.com::search_results_view | 0.736259 | 0.777319 | 0.700000 | 20.000000 |
| vmess | G2 | developer.mozilla.org::document_view | 0.620783 | 0.643275 | 0.600000 | 20.000000 |
| vmess | G2 | github.com::repository_view | 0.789744 | 0.796491 | 0.783333 | 20.000000 |
| vmess | G2 | wikipedia.org::article_view | 0.615440 | 0.571970 | 0.666667 | 20.000000 |
| vmess | G2 | youtube.com::search_results_view | 0.748664 | 0.732035 | 0.766667 | 20.000000 |
| vmess | G2 | youtube.com::video_playback | 0.865267 | 0.882902 | 0.850000 | 20.000000 |
| vmess | G3 | bing.com::search_results_view | 0.090909 | 0.500000 | 0.050000 | 20.000000 |
| vmess | G3 | developer.mozilla.org::document_view | 0.000000 | 0.000000 | 0.000000 | 20.000000 |
| vmess | G3 | github.com::repository_view | 0.086957 | 0.333333 | 0.050000 | 20.000000 |
| vmess | G3 | wikipedia.org::article_view | 0.000000 | 0.000000 | 0.000000 | 20.000000 |
| vmess | G3 | youtube.com::search_results_view | 0.296296 | 0.173913 | 1.000000 | 20.000000 |
| vmess | G3 | youtube.com::video_playback | 0.000000 | 0.000000 | 0.000000 | 20.000000 |
| vmess | G4 | bing.com::search_results_view | 0.428571 | 0.409091 | 0.450000 | 20.000000 |
| vmess | G4 | developer.mozilla.org::document_view | 0.418605 | 0.391304 | 0.450000 | 20.000000 |
| vmess | G4 | github.com::repository_view | 0.697674 | 0.652174 | 0.750000 | 20.000000 |
| vmess | G4 | wikipedia.org::article_view | 0.451613 | 0.636364 | 0.350000 | 20.000000 |
| vmess | G4 | youtube.com::search_results_view | 0.652174 | 0.576923 | 0.750000 | 20.000000 |
| vmess | G4 | youtube.com::video_playback | 0.742857 | 0.866667 | 0.650000 | 20.000000 |
| vmess | G5 | bing.com::search_results_view | 0.000000 | 0.000000 | 0.000000 | 20.000000 |
| vmess | G5 | developer.mozilla.org::document_view | 0.000000 | 0.000000 | 0.000000 | 20.000000 |
| vmess | G5 | github.com::repository_view | 0.187500 | 0.250000 | 0.150000 | 20.000000 |
| vmess | G5 | wikipedia.org::article_view | 0.393939 | 0.282609 | 0.650000 | 20.000000 |
| vmess | G5 | youtube.com::search_results_view | 0.560000 | 0.466667 | 0.700000 | 20.000000 |
| vmess | G5 | youtube.com::video_playback | 0.734694 | 0.620690 | 0.900000 | 20.000000 |



![真配混淆矩阵](../../outputs/drift-kernel-business-20261005/run-01/figures/true-kernel-confusions.png)



## 9 概率输出与评分尺度



![概率质量](../../outputs/drift-kernel-business-20261005/run-01/figures/probability-quality.png)



![可靠性](../../outputs/drift-kernel-business-20261005/run-01/figures/reliability.png)



固定平均评分与温度1可能使生成式概率较平；未根据测试结果修改温度。MLP概率也不自动校准；CE/Brier与F1是不同终点。可靠性图中的三seed合并点只作描述，正式统计仍按seed分别计算。



## 10 业务分布经过核后的差异



| protocol | arm | JS_nats |
| --- | --- | --- |
| shadowsocks | G0 | 0.005495 |
| shadowsocks | G3 | 0.006035 |
| shadowsocks | G4 | 0.001562 |
| shadowsocks | G5 | 0.000002 |
| trojan | G0 | 0.003713 |
| trojan | G3 | 0.005486 |
| trojan | G4 | 0.000824 |
| trojan | G5 | 0.000002 |
| vless | G0 | 0.003489 |
| vless | G3 | 0.005799 |
| vless | G4 | 0.000813 |
| vless | G5 | 0.000002 |
| vmess | G0 | 0.003539 |
| vmess | G3 | 0.006794 |
| vmess | G4 | 0.000613 |
| vmess | G5 | 0.000002 |



| protocol | JS_true_vs_direct | JS_group_vs_direct |
| --- | --- | --- |
| shadowsocks | 0.003036 | 0.002297 |
| trojan | 0.002196 | 0.001574 |
| vless | 0.002222 | 0.001479 |
| vmess | 0.002112 | 0.001516 |



![训练类间距离](../../outputs/drift-kernel-business-20261005/run-01/figures/source-to-output-class-distances.png)



上表是训练区中全部15业务对、十变量、五fold的描述均值，不是业务互信息。源分布、真配Q、组级Q和直接post T的区别同时含有限估计及平滑；不能把每个差值都归为协议因果。Q与T不接近也不能单独定位一个具体协议阶段。



## 11 修复错误与新增错误



| protocol | comparator | seed | repaired | new_error | decision_changed |
| --- | --- | --- | --- | --- | --- |
| shadowsocks | G0 | -1 | 7 | 10 | 29 |
| shadowsocks | G1 | -1 | 7 | 36 | 50 |
| shadowsocks | G2 | 20261005 | 4 | 31 | 44 |
| shadowsocks | G2 | 20261006 | 10 | 30 | 50 |
| shadowsocks | G2 | 20261007 | 7 | 32 | 48 |
| shadowsocks | G3 | -1 | 29 | 8 | 46 |
| shadowsocks | G5 | -1 | 19 | 4 | 40 |
| trojan | G0 | -1 | 10 | 21 | 45 |
| trojan | G1 | -1 | 7 | 34 | 48 |
| trojan | G2 | 20261005 | 11 | 32 | 52 |
| trojan | G2 | 20261006 | 7 | 29 | 44 |
| trojan | G2 | 20261007 | 7 | 29 | 46 |
| trojan | G3 | -1 | 56 | 6 | 97 |
| trojan | G5 | -1 | 47 | 19 | 86 |
| vless | G0 | -1 | 8 | 21 | 52 |
| vless | G1 | -1 | 6 | 47 | 66 |
| vless | G2 | 20261005 | 7 | 45 | 64 |
| vless | G2 | 20261006 | 7 | 41 | 60 |
| vless | G2 | 20261007 | 5 | 42 | 59 |
| vless | G3 | -1 | 41 | 10 | 93 |
| vless | G5 | -1 | 46 | 20 | 101 |
| vmess | G0 | -1 | 13 | 25 | 50 |
| vmess | G1 | -1 | 10 | 33 | 50 |
| vmess | G2 | 20261005 | 9 | 31 | 49 |
| vmess | G2 | 20261006 | 12 | 29 | 50 |
| vmess | G2 | 20261007 | 11 | 30 | 49 |
| vmess | G3 | -1 | 51 | 5 | 90 |
| vmess | G5 | -1 | 35 | 15 | 76 |



![错误翻转](../../outputs/drift-kernel-business-20261005/run-01/figures/error-flips.png)



以下内容表按固定标签与内容列出各臂错误；三seed分别保留。完整访问台账保存在explanations/error-flips.parquet。



| protocol | arm | seed | content_id | label_id | visits | correct |
| --- | --- | --- | --- | --- | --- | --- |
| shadowsocks | G0 | -1 | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | developer.mozilla.org::document_view | 4 | 3 |
| shadowsocks | G0 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP | developer.mozilla.org::document_view | 4 | 2 |
| shadowsocks | G0 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | developer.mozilla.org::document_view | 4 | 2 |
| shadowsocks | G0 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | developer.mozilla.org::document_view | 4 | 3 |
| shadowsocks | G0 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | developer.mozilla.org::document_view | 4 | 1 |
| shadowsocks | G0 | -1 | https://en.wikipedia.org/wiki/Computer_network | wikipedia.org::article_view | 4 | 2 |
| shadowsocks | G0 | -1 | https://en.wikipedia.org/wiki/Domain_Name_System | wikipedia.org::article_view | 4 | 4 |
| shadowsocks | G0 | -1 | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | wikipedia.org::article_view | 4 | 1 |
| shadowsocks | G0 | -1 | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | wikipedia.org::article_view | 4 | 3 |
| shadowsocks | G0 | -1 | https://en.wikipedia.org/wiki/Transport_Layer_Security | wikipedia.org::article_view | 4 | 3 |
| shadowsocks | G0 | -1 | https://github.com/RakuLomis/TrafficTracer | github.com::repository_view | 4 | 4 |
| shadowsocks | G0 | -1 | https://github.com/numpy/numpy | github.com::repository_view | 4 | 3 |
| shadowsocks | G0 | -1 | https://github.com/pallets/flask | github.com::repository_view | 4 | 2 |
| shadowsocks | G0 | -1 | https://github.com/python/cpython | github.com::repository_view | 4 | 4 |
| shadowsocks | G0 | -1 | https://github.com/scikit-learn/scikit-learn | github.com::repository_view | 4 | 3 |
| shadowsocks | G0 | -1 | https://www.bing.com/search?q=beginner+guitar+chords | bing.com::search_results_view | 4 | 2 |
| shadowsocks | G0 | -1 | https://www.bing.com/search?q=indoor+plant+care | bing.com::search_results_view | 4 | 2 |
| shadowsocks | G0 | -1 | https://www.bing.com/search?q=network+traffic+analysis | bing.com::search_results_view | 4 | 2 |
| shadowsocks | G0 | -1 | https://www.bing.com/search?q=solar+system+facts | bing.com::search_results_view | 4 | 3 |
| shadowsocks | G0 | -1 | https://www.bing.com/search?q=sourdough+bread+recipe | bing.com::search_results_view | 4 | 1 |
| shadowsocks | G0 | -1 | https://www.youtube.com/results?search_query=astronomy+documentary | youtube.com::search_results_view | 4 | 3 |
| shadowsocks | G0 | -1 | https://www.youtube.com/results?search_query=bicycle+maintenance | youtube.com::search_results_view | 4 | 4 |
| shadowsocks | G0 | -1 | https://www.youtube.com/results?search_query=bread+baking | youtube.com::search_results_view | 4 | 3 |
| shadowsocks | G0 | -1 | https://www.youtube.com/results?search_query=piano+practice | youtube.com::search_results_view | 4 | 3 |
| shadowsocks | G0 | -1 | https://www.youtube.com/results?search_query=watercolor+tutorial | youtube.com::search_results_view | 4 | 3 |
| shadowsocks | G0 | -1 | youtube_video:R6MlUcmOul8 | youtube.com::video_playback | 4 | 2 |
| shadowsocks | G0 | -1 | youtube_video:aircAruvnKk | youtube.com::video_playback | 4 | 0 |
| shadowsocks | G0 | -1 | youtube_video:aqz-KE-bpKQ | youtube.com::video_playback | 4 | 1 |
| shadowsocks | G0 | -1 | youtube_video:eRsGyueVLvQ | youtube.com::video_playback | 4 | 4 |
| shadowsocks | G0 | -1 | youtube_video:sAWK0mgrMp4 | youtube.com::video_playback | 4 | 3 |
| shadowsocks | G1 | -1 | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | developer.mozilla.org::document_view | 4 | 3 |
| shadowsocks | G1 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP | developer.mozilla.org::document_view | 4 | 3 |
| shadowsocks | G1 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | developer.mozilla.org::document_view | 4 | 4 |
| shadowsocks | G1 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | developer.mozilla.org::document_view | 4 | 4 |
| shadowsocks | G1 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | developer.mozilla.org::document_view | 4 | 1 |
| shadowsocks | G1 | -1 | https://en.wikipedia.org/wiki/Computer_network | wikipedia.org::article_view | 4 | 2 |
| shadowsocks | G1 | -1 | https://en.wikipedia.org/wiki/Domain_Name_System | wikipedia.org::article_view | 4 | 4 |
| shadowsocks | G1 | -1 | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | wikipedia.org::article_view | 4 | 3 |
| shadowsocks | G1 | -1 | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | wikipedia.org::article_view | 4 | 3 |
| shadowsocks | G1 | -1 | https://en.wikipedia.org/wiki/Transport_Layer_Security | wikipedia.org::article_view | 4 | 3 |
| shadowsocks | G1 | -1 | https://github.com/RakuLomis/TrafficTracer | github.com::repository_view | 4 | 4 |
| shadowsocks | G1 | -1 | https://github.com/numpy/numpy | github.com::repository_view | 4 | 4 |
| shadowsocks | G1 | -1 | https://github.com/pallets/flask | github.com::repository_view | 4 | 3 |
| shadowsocks | G1 | -1 | https://github.com/python/cpython | github.com::repository_view | 4 | 4 |
| shadowsocks | G1 | -1 | https://github.com/scikit-learn/scikit-learn | github.com::repository_view | 4 | 4 |
| shadowsocks | G1 | -1 | https://www.bing.com/search?q=beginner+guitar+chords | bing.com::search_results_view | 4 | 0 |
| shadowsocks | G1 | -1 | https://www.bing.com/search?q=indoor+plant+care | bing.com::search_results_view | 4 | 4 |
| shadowsocks | G1 | -1 | https://www.bing.com/search?q=network+traffic+analysis | bing.com::search_results_view | 4 | 3 |
| shadowsocks | G1 | -1 | https://www.bing.com/search?q=solar+system+facts | bing.com::search_results_view | 4 | 3 |
| shadowsocks | G1 | -1 | https://www.bing.com/search?q=sourdough+bread+recipe | bing.com::search_results_view | 4 | 4 |
| shadowsocks | G1 | -1 | https://www.youtube.com/results?search_query=astronomy+documentary | youtube.com::search_results_view | 4 | 4 |
| shadowsocks | G1 | -1 | https://www.youtube.com/results?search_query=bicycle+maintenance | youtube.com::search_results_view | 4 | 4 |
| shadowsocks | G1 | -1 | https://www.youtube.com/results?search_query=bread+baking | youtube.com::search_results_view | 4 | 4 |
| shadowsocks | G1 | -1 | https://www.youtube.com/results?search_query=piano+practice | youtube.com::search_results_view | 4 | 4 |
| shadowsocks | G1 | -1 | https://www.youtube.com/results?search_query=watercolor+tutorial | youtube.com::search_results_view | 4 | 3 |
| shadowsocks | G1 | -1 | youtube_video:R6MlUcmOul8 | youtube.com::video_playback | 4 | 4 |
| shadowsocks | G1 | -1 | youtube_video:aircAruvnKk | youtube.com::video_playback | 4 | 4 |
| shadowsocks | G1 | -1 | youtube_video:aqz-KE-bpKQ | youtube.com::video_playback | 4 | 4 |
| shadowsocks | G1 | -1 | youtube_video:eRsGyueVLvQ | youtube.com::video_playback | 4 | 4 |
| shadowsocks | G1 | -1 | youtube_video:sAWK0mgrMp4 | youtube.com::video_playback | 4 | 4 |
| shadowsocks | G2 | 20261005 | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | developer.mozilla.org::document_view | 4 | 3 |
| shadowsocks | G2 | 20261005 | https://developer.mozilla.org/en-US/docs/Web/HTTP | developer.mozilla.org::document_view | 4 | 1 |
| shadowsocks | G2 | 20261005 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | developer.mozilla.org::document_view | 4 | 2 |
| shadowsocks | G2 | 20261005 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | developer.mozilla.org::document_view | 4 | 4 |
| shadowsocks | G2 | 20261005 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | developer.mozilla.org::document_view | 4 | 1 |
| shadowsocks | G2 | 20261005 | https://en.wikipedia.org/wiki/Computer_network | wikipedia.org::article_view | 4 | 3 |
| shadowsocks | G2 | 20261005 | https://en.wikipedia.org/wiki/Domain_Name_System | wikipedia.org::article_view | 4 | 4 |
| shadowsocks | G2 | 20261005 | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | wikipedia.org::article_view | 4 | 3 |
| shadowsocks | G2 | 20261005 | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | wikipedia.org::article_view | 4 | 3 |
| shadowsocks | G2 | 20261005 | https://en.wikipedia.org/wiki/Transport_Layer_Security | wikipedia.org::article_view | 4 | 3 |
| shadowsocks | G2 | 20261005 | https://github.com/RakuLomis/TrafficTracer | github.com::repository_view | 4 | 4 |
| shadowsocks | G2 | 20261005 | https://github.com/numpy/numpy | github.com::repository_view | 4 | 4 |
| shadowsocks | G2 | 20261005 | https://github.com/pallets/flask | github.com::repository_view | 4 | 3 |
| shadowsocks | G2 | 20261005 | https://github.com/python/cpython | github.com::repository_view | 4 | 4 |
| shadowsocks | G2 | 20261005 | https://github.com/scikit-learn/scikit-learn | github.com::repository_view | 4 | 4 |
| shadowsocks | G2 | 20261005 | https://www.bing.com/search?q=beginner+guitar+chords | bing.com::search_results_view | 4 | 2 |
| shadowsocks | G2 | 20261005 | https://www.bing.com/search?q=indoor+plant+care | bing.com::search_results_view | 4 | 3 |
| shadowsocks | G2 | 20261005 | https://www.bing.com/search?q=network+traffic+analysis | bing.com::search_results_view | 4 | 3 |
| shadowsocks | G2 | 20261005 | https://www.bing.com/search?q=solar+system+facts | bing.com::search_results_view | 4 | 4 |
| shadowsocks | G2 | 20261005 | https://www.bing.com/search?q=sourdough+bread+recipe | bing.com::search_results_view | 4 | 4 |
| shadowsocks | G2 | 20261005 | https://www.youtube.com/results?search_query=astronomy+documentary | youtube.com::search_results_view | 4 | 4 |
| shadowsocks | G2 | 20261005 | https://www.youtube.com/results?search_query=bicycle+maintenance | youtube.com::search_results_view | 4 | 4 |
| shadowsocks | G2 | 20261005 | https://www.youtube.com/results?search_query=bread+baking | youtube.com::search_results_view | 4 | 4 |
| shadowsocks | G2 | 20261005 | https://www.youtube.com/results?search_query=piano+practice | youtube.com::search_results_view | 4 | 4 |
| shadowsocks | G2 | 20261005 | https://www.youtube.com/results?search_query=watercolor+tutorial | youtube.com::search_results_view | 4 | 3 |
| shadowsocks | G2 | 20261005 | youtube_video:R6MlUcmOul8 | youtube.com::video_playback | 4 | 3 |
| shadowsocks | G2 | 20261005 | youtube_video:aircAruvnKk | youtube.com::video_playback | 4 | 4 |
| shadowsocks | G2 | 20261005 | youtube_video:aqz-KE-bpKQ | youtube.com::video_playback | 4 | 4 |
| shadowsocks | G2 | 20261005 | youtube_video:eRsGyueVLvQ | youtube.com::video_playback | 4 | 4 |
| shadowsocks | G2 | 20261005 | youtube_video:sAWK0mgrMp4 | youtube.com::video_playback | 4 | 4 |
| shadowsocks | G2 | 20261006 | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | developer.mozilla.org::document_view | 4 | 3 |
| shadowsocks | G2 | 20261006 | https://developer.mozilla.org/en-US/docs/Web/HTTP | developer.mozilla.org::document_view | 4 | 1 |
| shadowsocks | G2 | 20261006 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | developer.mozilla.org::document_view | 4 | 3 |
| shadowsocks | G2 | 20261006 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | developer.mozilla.org::document_view | 4 | 4 |
| shadowsocks | G2 | 20261006 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | developer.mozilla.org::document_view | 4 | 1 |
| shadowsocks | G2 | 20261006 | https://en.wikipedia.org/wiki/Computer_network | wikipedia.org::article_view | 4 | 3 |
| shadowsocks | G2 | 20261006 | https://en.wikipedia.org/wiki/Domain_Name_System | wikipedia.org::article_view | 4 | 4 |
| shadowsocks | G2 | 20261006 | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | wikipedia.org::article_view | 4 | 2 |
| shadowsocks | G2 | 20261006 | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | wikipedia.org::article_view | 4 | 3 |
| shadowsocks | G2 | 20261006 | https://en.wikipedia.org/wiki/Transport_Layer_Security | wikipedia.org::article_view | 4 | 3 |
| shadowsocks | G2 | 20261006 | https://github.com/RakuLomis/TrafficTracer | github.com::repository_view | 4 | 4 |
| shadowsocks | G2 | 20261006 | https://github.com/numpy/numpy | github.com::repository_view | 4 | 4 |
| shadowsocks | G2 | 20261006 | https://github.com/pallets/flask | github.com::repository_view | 4 | 3 |
| shadowsocks | G2 | 20261006 | https://github.com/python/cpython | github.com::repository_view | 4 | 4 |
| shadowsocks | G2 | 20261006 | https://github.com/scikit-learn/scikit-learn | github.com::repository_view | 4 | 3 |
| shadowsocks | G2 | 20261006 | https://www.bing.com/search?q=beginner+guitar+chords | bing.com::search_results_view | 4 | 0 |
| shadowsocks | G2 | 20261006 | https://www.bing.com/search?q=indoor+plant+care | bing.com::search_results_view | 4 | 3 |
| shadowsocks | G2 | 20261006 | https://www.bing.com/search?q=network+traffic+analysis | bing.com::search_results_view | 4 | 3 |
| shadowsocks | G2 | 20261006 | https://www.bing.com/search?q=solar+system+facts | bing.com::search_results_view | 4 | 3 |
| shadowsocks | G2 | 20261006 | https://www.bing.com/search?q=sourdough+bread+recipe | bing.com::search_results_view | 4 | 4 |
| shadowsocks | G2 | 20261006 | https://www.youtube.com/results?search_query=astronomy+documentary | youtube.com::search_results_view | 4 | 4 |
| shadowsocks | G2 | 20261006 | https://www.youtube.com/results?search_query=bicycle+maintenance | youtube.com::search_results_view | 4 | 3 |
| shadowsocks | G2 | 20261006 | https://www.youtube.com/results?search_query=bread+baking | youtube.com::search_results_view | 4 | 3 |
| shadowsocks | G2 | 20261006 | https://www.youtube.com/results?search_query=piano+practice | youtube.com::search_results_view | 4 | 4 |
| shadowsocks | G2 | 20261006 | https://www.youtube.com/results?search_query=watercolor+tutorial | youtube.com::search_results_view | 4 | 3 |
| shadowsocks | G2 | 20261006 | youtube_video:R6MlUcmOul8 | youtube.com::video_playback | 4 | 3 |
| shadowsocks | G2 | 20261006 | youtube_video:aircAruvnKk | youtube.com::video_playback | 4 | 4 |
| shadowsocks | G2 | 20261006 | youtube_video:aqz-KE-bpKQ | youtube.com::video_playback | 4 | 4 |
| shadowsocks | G2 | 20261006 | youtube_video:eRsGyueVLvQ | youtube.com::video_playback | 4 | 4 |
| shadowsocks | G2 | 20261006 | youtube_video:sAWK0mgrMp4 | youtube.com::video_playback | 4 | 3 |
| shadowsocks | G2 | 20261007 | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | developer.mozilla.org::document_view | 4 | 3 |
| shadowsocks | G2 | 20261007 | https://developer.mozilla.org/en-US/docs/Web/HTTP | developer.mozilla.org::document_view | 4 | 1 |
| shadowsocks | G2 | 20261007 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | developer.mozilla.org::document_view | 4 | 4 |
| shadowsocks | G2 | 20261007 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | developer.mozilla.org::document_view | 4 | 4 |
| shadowsocks | G2 | 20261007 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | developer.mozilla.org::document_view | 4 | 0 |
| shadowsocks | G2 | 20261007 | https://en.wikipedia.org/wiki/Computer_network | wikipedia.org::article_view | 4 | 3 |
| shadowsocks | G2 | 20261007 | https://en.wikipedia.org/wiki/Domain_Name_System | wikipedia.org::article_view | 4 | 4 |
| shadowsocks | G2 | 20261007 | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | wikipedia.org::article_view | 4 | 2 |
| shadowsocks | G2 | 20261007 | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | wikipedia.org::article_view | 4 | 3 |
| shadowsocks | G2 | 20261007 | https://en.wikipedia.org/wiki/Transport_Layer_Security | wikipedia.org::article_view | 4 | 3 |
| shadowsocks | G2 | 20261007 | https://github.com/RakuLomis/TrafficTracer | github.com::repository_view | 4 | 4 |
| shadowsocks | G2 | 20261007 | https://github.com/numpy/numpy | github.com::repository_view | 4 | 4 |
| shadowsocks | G2 | 20261007 | https://github.com/pallets/flask | github.com::repository_view | 4 | 3 |
| shadowsocks | G2 | 20261007 | https://github.com/python/cpython | github.com::repository_view | 4 | 4 |
| shadowsocks | G2 | 20261007 | https://github.com/scikit-learn/scikit-learn | github.com::repository_view | 4 | 4 |
| shadowsocks | G2 | 20261007 | https://www.bing.com/search?q=beginner+guitar+chords | bing.com::search_results_view | 4 | 0 |
| shadowsocks | G2 | 20261007 | https://www.bing.com/search?q=indoor+plant+care | bing.com::search_results_view | 4 | 4 |
| shadowsocks | G2 | 20261007 | https://www.bing.com/search?q=network+traffic+analysis | bing.com::search_results_view | 4 | 3 |
| shadowsocks | G2 | 20261007 | https://www.bing.com/search?q=solar+system+facts | bing.com::search_results_view | 4 | 4 |
| shadowsocks | G2 | 20261007 | https://www.bing.com/search?q=sourdough+bread+recipe | bing.com::search_results_view | 4 | 4 |
| shadowsocks | G2 | 20261007 | https://www.youtube.com/results?search_query=astronomy+documentary | youtube.com::search_results_view | 4 | 4 |
| shadowsocks | G2 | 20261007 | https://www.youtube.com/results?search_query=bicycle+maintenance | youtube.com::search_results_view | 4 | 4 |
| shadowsocks | G2 | 20261007 | https://www.youtube.com/results?search_query=bread+baking | youtube.com::search_results_view | 4 | 4 |
| shadowsocks | G2 | 20261007 | https://www.youtube.com/results?search_query=piano+practice | youtube.com::search_results_view | 4 | 4 |
| shadowsocks | G2 | 20261007 | https://www.youtube.com/results?search_query=watercolor+tutorial | youtube.com::search_results_view | 4 | 3 |
| shadowsocks | G2 | 20261007 | youtube_video:R6MlUcmOul8 | youtube.com::video_playback | 4 | 3 |
| shadowsocks | G2 | 20261007 | youtube_video:aircAruvnKk | youtube.com::video_playback | 4 | 4 |
| shadowsocks | G2 | 20261007 | youtube_video:aqz-KE-bpKQ | youtube.com::video_playback | 4 | 3 |
| shadowsocks | G2 | 20261007 | youtube_video:eRsGyueVLvQ | youtube.com::video_playback | 4 | 4 |
| shadowsocks | G2 | 20261007 | youtube_video:sAWK0mgrMp4 | youtube.com::video_playback | 4 | 4 |
| shadowsocks | G3 | -1 | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | developer.mozilla.org::document_view | 4 | 1 |
| shadowsocks | G3 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP | developer.mozilla.org::document_view | 4 | 1 |
| shadowsocks | G3 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | developer.mozilla.org::document_view | 4 | 1 |
| shadowsocks | G3 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | developer.mozilla.org::document_view | 4 | 1 |
| shadowsocks | G3 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | developer.mozilla.org::document_view | 4 | 2 |
| shadowsocks | G3 | -1 | https://en.wikipedia.org/wiki/Computer_network | wikipedia.org::article_view | 4 | 0 |
| shadowsocks | G3 | -1 | https://en.wikipedia.org/wiki/Domain_Name_System | wikipedia.org::article_view | 4 | 4 |
| shadowsocks | G3 | -1 | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | wikipedia.org::article_view | 4 | 0 |
| shadowsocks | G3 | -1 | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | wikipedia.org::article_view | 4 | 3 |
| shadowsocks | G3 | -1 | https://en.wikipedia.org/wiki/Transport_Layer_Security | wikipedia.org::article_view | 4 | 1 |
| shadowsocks | G3 | -1 | https://github.com/RakuLomis/TrafficTracer | github.com::repository_view | 4 | 0 |
| shadowsocks | G3 | -1 | https://github.com/numpy/numpy | github.com::repository_view | 4 | 0 |
| shadowsocks | G3 | -1 | https://github.com/pallets/flask | github.com::repository_view | 4 | 0 |
| shadowsocks | G3 | -1 | https://github.com/python/cpython | github.com::repository_view | 4 | 0 |
| shadowsocks | G3 | -1 | https://github.com/scikit-learn/scikit-learn | github.com::repository_view | 4 | 0 |
| shadowsocks | G3 | -1 | https://www.bing.com/search?q=beginner+guitar+chords | bing.com::search_results_view | 4 | 2 |
| shadowsocks | G3 | -1 | https://www.bing.com/search?q=indoor+plant+care | bing.com::search_results_view | 4 | 1 |
| shadowsocks | G3 | -1 | https://www.bing.com/search?q=network+traffic+analysis | bing.com::search_results_view | 4 | 3 |
| shadowsocks | G3 | -1 | https://www.bing.com/search?q=solar+system+facts | bing.com::search_results_view | 4 | 2 |
| shadowsocks | G3 | -1 | https://www.bing.com/search?q=sourdough+bread+recipe | bing.com::search_results_view | 4 | 3 |
| shadowsocks | G3 | -1 | https://www.youtube.com/results?search_query=astronomy+documentary | youtube.com::search_results_view | 4 | 3 |
| shadowsocks | G3 | -1 | https://www.youtube.com/results?search_query=bicycle+maintenance | youtube.com::search_results_view | 4 | 3 |
| shadowsocks | G3 | -1 | https://www.youtube.com/results?search_query=bread+baking | youtube.com::search_results_view | 4 | 3 |
| shadowsocks | G3 | -1 | https://www.youtube.com/results?search_query=piano+practice | youtube.com::search_results_view | 4 | 3 |
| shadowsocks | G3 | -1 | https://www.youtube.com/results?search_query=watercolor+tutorial | youtube.com::search_results_view | 4 | 3 |
| shadowsocks | G3 | -1 | youtube_video:R6MlUcmOul8 | youtube.com::video_playback | 4 | 3 |
| shadowsocks | G3 | -1 | youtube_video:aircAruvnKk | youtube.com::video_playback | 4 | 0 |
| shadowsocks | G3 | -1 | youtube_video:aqz-KE-bpKQ | youtube.com::video_playback | 4 | 2 |
| shadowsocks | G3 | -1 | youtube_video:eRsGyueVLvQ | youtube.com::video_playback | 4 | 3 |
| shadowsocks | G3 | -1 | youtube_video:sAWK0mgrMp4 | youtube.com::video_playback | 4 | 4 |
| shadowsocks | G4 | -1 | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | developer.mozilla.org::document_view | 4 | 1 |
| shadowsocks | G4 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP | developer.mozilla.org::document_view | 4 | 2 |
| shadowsocks | G4 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | developer.mozilla.org::document_view | 4 | 1 |
| shadowsocks | G4 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | developer.mozilla.org::document_view | 4 | 1 |
| shadowsocks | G4 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | developer.mozilla.org::document_view | 4 | 2 |
| shadowsocks | G4 | -1 | https://en.wikipedia.org/wiki/Computer_network | wikipedia.org::article_view | 4 | 2 |
| shadowsocks | G4 | -1 | https://en.wikipedia.org/wiki/Domain_Name_System | wikipedia.org::article_view | 4 | 4 |
| shadowsocks | G4 | -1 | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | wikipedia.org::article_view | 4 | 1 |
| shadowsocks | G4 | -1 | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | wikipedia.org::article_view | 4 | 3 |
| shadowsocks | G4 | -1 | https://en.wikipedia.org/wiki/Transport_Layer_Security | wikipedia.org::article_view | 4 | 3 |
| shadowsocks | G4 | -1 | https://github.com/RakuLomis/TrafficTracer | github.com::repository_view | 4 | 4 |
| shadowsocks | G4 | -1 | https://github.com/numpy/numpy | github.com::repository_view | 4 | 3 |
| shadowsocks | G4 | -1 | https://github.com/pallets/flask | github.com::repository_view | 4 | 2 |
| shadowsocks | G4 | -1 | https://github.com/python/cpython | github.com::repository_view | 4 | 4 |
| shadowsocks | G4 | -1 | https://github.com/scikit-learn/scikit-learn | github.com::repository_view | 4 | 3 |
| shadowsocks | G4 | -1 | https://www.bing.com/search?q=beginner+guitar+chords | bing.com::search_results_view | 4 | 4 |
| shadowsocks | G4 | -1 | https://www.bing.com/search?q=indoor+plant+care | bing.com::search_results_view | 4 | 0 |
| shadowsocks | G4 | -1 | https://www.bing.com/search?q=network+traffic+analysis | bing.com::search_results_view | 4 | 3 |
| shadowsocks | G4 | -1 | https://www.bing.com/search?q=solar+system+facts | bing.com::search_results_view | 4 | 3 |
| shadowsocks | G4 | -1 | https://www.bing.com/search?q=sourdough+bread+recipe | bing.com::search_results_view | 4 | 2 |
| shadowsocks | G4 | -1 | https://www.youtube.com/results?search_query=astronomy+documentary | youtube.com::search_results_view | 4 | 3 |
| shadowsocks | G4 | -1 | https://www.youtube.com/results?search_query=bicycle+maintenance | youtube.com::search_results_view | 4 | 4 |
| shadowsocks | G4 | -1 | https://www.youtube.com/results?search_query=bread+baking | youtube.com::search_results_view | 4 | 3 |
| shadowsocks | G4 | -1 | https://www.youtube.com/results?search_query=piano+practice | youtube.com::search_results_view | 4 | 3 |
| shadowsocks | G4 | -1 | https://www.youtube.com/results?search_query=watercolor+tutorial | youtube.com::search_results_view | 4 | 3 |
| shadowsocks | G4 | -1 | youtube_video:R6MlUcmOul8 | youtube.com::video_playback | 4 | 1 |
| shadowsocks | G4 | -1 | youtube_video:aircAruvnKk | youtube.com::video_playback | 4 | 0 |
| shadowsocks | G4 | -1 | youtube_video:aqz-KE-bpKQ | youtube.com::video_playback | 4 | 1 |
| shadowsocks | G4 | -1 | youtube_video:eRsGyueVLvQ | youtube.com::video_playback | 4 | 4 |
| shadowsocks | G4 | -1 | youtube_video:sAWK0mgrMp4 | youtube.com::video_playback | 4 | 3 |
| shadowsocks | G5 | -1 | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | developer.mozilla.org::document_view | 4 | 1 |
| shadowsocks | G5 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP | developer.mozilla.org::document_view | 4 | 1 |
| shadowsocks | G5 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | developer.mozilla.org::document_view | 4 | 1 |
| shadowsocks | G5 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | developer.mozilla.org::document_view | 4 | 0 |
| shadowsocks | G5 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | developer.mozilla.org::document_view | 4 | 0 |
| shadowsocks | G5 | -1 | https://en.wikipedia.org/wiki/Computer_network | wikipedia.org::article_view | 4 | 2 |
| shadowsocks | G5 | -1 | https://en.wikipedia.org/wiki/Domain_Name_System | wikipedia.org::article_view | 4 | 2 |
| shadowsocks | G5 | -1 | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | wikipedia.org::article_view | 4 | 1 |
| shadowsocks | G5 | -1 | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | wikipedia.org::article_view | 4 | 3 |
| shadowsocks | G5 | -1 | https://en.wikipedia.org/wiki/Transport_Layer_Security | wikipedia.org::article_view | 4 | 2 |
| shadowsocks | G5 | -1 | https://github.com/RakuLomis/TrafficTracer | github.com::repository_view | 4 | 4 |
| shadowsocks | G5 | -1 | https://github.com/numpy/numpy | github.com::repository_view | 4 | 2 |
| shadowsocks | G5 | -1 | https://github.com/pallets/flask | github.com::repository_view | 4 | 2 |
| shadowsocks | G5 | -1 | https://github.com/python/cpython | github.com::repository_view | 4 | 4 |
| shadowsocks | G5 | -1 | https://github.com/scikit-learn/scikit-learn | github.com::repository_view | 4 | 3 |
| shadowsocks | G5 | -1 | https://www.bing.com/search?q=beginner+guitar+chords | bing.com::search_results_view | 4 | 0 |
| shadowsocks | G5 | -1 | https://www.bing.com/search?q=indoor+plant+care | bing.com::search_results_view | 4 | 1 |
| shadowsocks | G5 | -1 | https://www.bing.com/search?q=network+traffic+analysis | bing.com::search_results_view | 4 | 3 |
| shadowsocks | G5 | -1 | https://www.bing.com/search?q=solar+system+facts | bing.com::search_results_view | 4 | 2 |
| shadowsocks | G5 | -1 | https://www.bing.com/search?q=sourdough+bread+recipe | bing.com::search_results_view | 4 | 1 |
| shadowsocks | G5 | -1 | https://www.youtube.com/results?search_query=astronomy+documentary | youtube.com::search_results_view | 4 | 3 |
| shadowsocks | G5 | -1 | https://www.youtube.com/results?search_query=bicycle+maintenance | youtube.com::search_results_view | 4 | 3 |
| shadowsocks | G5 | -1 | https://www.youtube.com/results?search_query=bread+baking | youtube.com::search_results_view | 4 | 3 |
| shadowsocks | G5 | -1 | https://www.youtube.com/results?search_query=piano+practice | youtube.com::search_results_view | 4 | 3 |
| shadowsocks | G5 | -1 | https://www.youtube.com/results?search_query=watercolor+tutorial | youtube.com::search_results_view | 4 | 3 |
| shadowsocks | G5 | -1 | youtube_video:R6MlUcmOul8 | youtube.com::video_playback | 4 | 2 |
| shadowsocks | G5 | -1 | youtube_video:aircAruvnKk | youtube.com::video_playback | 4 | 0 |
| shadowsocks | G5 | -1 | youtube_video:aqz-KE-bpKQ | youtube.com::video_playback | 4 | 1 |
| shadowsocks | G5 | -1 | youtube_video:eRsGyueVLvQ | youtube.com::video_playback | 4 | 3 |
| shadowsocks | G5 | -1 | youtube_video:sAWK0mgrMp4 | youtube.com::video_playback | 4 | 2 |
| trojan | G0 | -1 | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | developer.mozilla.org::document_view | 4 | 2 |
| trojan | G0 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP | developer.mozilla.org::document_view | 4 | 2 |
| trojan | G0 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | developer.mozilla.org::document_view | 4 | 2 |
| trojan | G0 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | developer.mozilla.org::document_view | 4 | 2 |
| trojan | G0 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | developer.mozilla.org::document_view | 4 | 3 |
| trojan | G0 | -1 | https://en.wikipedia.org/wiki/Computer_network | wikipedia.org::article_view | 4 | 2 |
| trojan | G0 | -1 | https://en.wikipedia.org/wiki/Domain_Name_System | wikipedia.org::article_view | 4 | 3 |
| trojan | G0 | -1 | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | wikipedia.org::article_view | 4 | 2 |
| trojan | G0 | -1 | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | wikipedia.org::article_view | 4 | 3 |
| trojan | G0 | -1 | https://en.wikipedia.org/wiki/Transport_Layer_Security | wikipedia.org::article_view | 4 | 4 |
| trojan | G0 | -1 | https://github.com/RakuLomis/TrafficTracer | github.com::repository_view | 4 | 4 |
| trojan | G0 | -1 | https://github.com/numpy/numpy | github.com::repository_view | 4 | 4 |
| trojan | G0 | -1 | https://github.com/pallets/flask | github.com::repository_view | 4 | 3 |
| trojan | G0 | -1 | https://github.com/python/cpython | github.com::repository_view | 4 | 4 |
| trojan | G0 | -1 | https://github.com/scikit-learn/scikit-learn | github.com::repository_view | 4 | 4 |
| trojan | G0 | -1 | https://www.bing.com/search?q=beginner+guitar+chords | bing.com::search_results_view | 4 | 1 |
| trojan | G0 | -1 | https://www.bing.com/search?q=indoor+plant+care | bing.com::search_results_view | 4 | 3 |
| trojan | G0 | -1 | https://www.bing.com/search?q=network+traffic+analysis | bing.com::search_results_view | 4 | 1 |
| trojan | G0 | -1 | https://www.bing.com/search?q=solar+system+facts | bing.com::search_results_view | 4 | 3 |
| trojan | G0 | -1 | https://www.bing.com/search?q=sourdough+bread+recipe | bing.com::search_results_view | 4 | 2 |
| trojan | G0 | -1 | https://www.youtube.com/results?search_query=astronomy+documentary | youtube.com::search_results_view | 4 | 1 |
| trojan | G0 | -1 | https://www.youtube.com/results?search_query=bicycle+maintenance | youtube.com::search_results_view | 4 | 3 |
| trojan | G0 | -1 | https://www.youtube.com/results?search_query=bread+baking | youtube.com::search_results_view | 4 | 4 |
| trojan | G0 | -1 | https://www.youtube.com/results?search_query=piano+practice | youtube.com::search_results_view | 4 | 4 |
| trojan | G0 | -1 | https://www.youtube.com/results?search_query=watercolor+tutorial | youtube.com::search_results_view | 4 | 3 |
| trojan | G0 | -1 | youtube_video:R6MlUcmOul8 | youtube.com::video_playback | 4 | 2 |
| trojan | G0 | -1 | youtube_video:aircAruvnKk | youtube.com::video_playback | 4 | 3 |
| trojan | G0 | -1 | youtube_video:aqz-KE-bpKQ | youtube.com::video_playback | 4 | 3 |
| trojan | G0 | -1 | youtube_video:eRsGyueVLvQ | youtube.com::video_playback | 4 | 4 |
| trojan | G0 | -1 | youtube_video:sAWK0mgrMp4 | youtube.com::video_playback | 4 | 2 |
| trojan | G1 | -1 | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | developer.mozilla.org::document_view | 4 | 2 |
| trojan | G1 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP | developer.mozilla.org::document_view | 4 | 2 |
| trojan | G1 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | developer.mozilla.org::document_view | 4 | 3 |
| trojan | G1 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | developer.mozilla.org::document_view | 4 | 3 |
| trojan | G1 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | developer.mozilla.org::document_view | 4 | 2 |
| trojan | G1 | -1 | https://en.wikipedia.org/wiki/Computer_network | wikipedia.org::article_view | 4 | 3 |
| trojan | G1 | -1 | https://en.wikipedia.org/wiki/Domain_Name_System | wikipedia.org::article_view | 4 | 3 |
| trojan | G1 | -1 | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | wikipedia.org::article_view | 4 | 3 |
| trojan | G1 | -1 | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | wikipedia.org::article_view | 4 | 4 |
| trojan | G1 | -1 | https://en.wikipedia.org/wiki/Transport_Layer_Security | wikipedia.org::article_view | 4 | 3 |
| trojan | G1 | -1 | https://github.com/RakuLomis/TrafficTracer | github.com::repository_view | 4 | 4 |
| trojan | G1 | -1 | https://github.com/numpy/numpy | github.com::repository_view | 4 | 4 |
| trojan | G1 | -1 | https://github.com/pallets/flask | github.com::repository_view | 4 | 4 |
| trojan | G1 | -1 | https://github.com/python/cpython | github.com::repository_view | 4 | 3 |
| trojan | G1 | -1 | https://github.com/scikit-learn/scikit-learn | github.com::repository_view | 4 | 4 |
| trojan | G1 | -1 | https://www.bing.com/search?q=beginner+guitar+chords | bing.com::search_results_view | 4 | 3 |
| trojan | G1 | -1 | https://www.bing.com/search?q=indoor+plant+care | bing.com::search_results_view | 4 | 4 |
| trojan | G1 | -1 | https://www.bing.com/search?q=network+traffic+analysis | bing.com::search_results_view | 4 | 4 |
| trojan | G1 | -1 | https://www.bing.com/search?q=solar+system+facts | bing.com::search_results_view | 4 | 3 |
| trojan | G1 | -1 | https://www.bing.com/search?q=sourdough+bread+recipe | bing.com::search_results_view | 4 | 3 |
| trojan | G1 | -1 | https://www.youtube.com/results?search_query=astronomy+documentary | youtube.com::search_results_view | 4 | 4 |
| trojan | G1 | -1 | https://www.youtube.com/results?search_query=bicycle+maintenance | youtube.com::search_results_view | 4 | 4 |
| trojan | G1 | -1 | https://www.youtube.com/results?search_query=bread+baking | youtube.com::search_results_view | 4 | 3 |
| trojan | G1 | -1 | https://www.youtube.com/results?search_query=piano+practice | youtube.com::search_results_view | 4 | 4 |
| trojan | G1 | -1 | https://www.youtube.com/results?search_query=watercolor+tutorial | youtube.com::search_results_view | 4 | 3 |
| trojan | G1 | -1 | youtube_video:R6MlUcmOul8 | youtube.com::video_playback | 4 | 3 |
| trojan | G1 | -1 | youtube_video:aircAruvnKk | youtube.com::video_playback | 4 | 4 |
| trojan | G1 | -1 | youtube_video:aqz-KE-bpKQ | youtube.com::video_playback | 4 | 3 |
| trojan | G1 | -1 | youtube_video:eRsGyueVLvQ | youtube.com::video_playback | 4 | 3 |
| trojan | G1 | -1 | youtube_video:sAWK0mgrMp4 | youtube.com::video_playback | 4 | 4 |
| trojan | G2 | 20261005 | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | developer.mozilla.org::document_view | 4 | 2 |
| trojan | G2 | 20261005 | https://developer.mozilla.org/en-US/docs/Web/HTTP | developer.mozilla.org::document_view | 4 | 1 |
| trojan | G2 | 20261005 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | developer.mozilla.org::document_view | 4 | 4 |
| trojan | G2 | 20261005 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | developer.mozilla.org::document_view | 4 | 3 |
| trojan | G2 | 20261005 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | developer.mozilla.org::document_view | 4 | 2 |
| trojan | G2 | 20261005 | https://en.wikipedia.org/wiki/Computer_network | wikipedia.org::article_view | 4 | 3 |
| trojan | G2 | 20261005 | https://en.wikipedia.org/wiki/Domain_Name_System | wikipedia.org::article_view | 4 | 3 |
| trojan | G2 | 20261005 | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | wikipedia.org::article_view | 4 | 3 |
| trojan | G2 | 20261005 | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | wikipedia.org::article_view | 4 | 4 |
| trojan | G2 | 20261005 | https://en.wikipedia.org/wiki/Transport_Layer_Security | wikipedia.org::article_view | 4 | 3 |
| trojan | G2 | 20261005 | https://github.com/RakuLomis/TrafficTracer | github.com::repository_view | 4 | 4 |
| trojan | G2 | 20261005 | https://github.com/numpy/numpy | github.com::repository_view | 4 | 3 |
| trojan | G2 | 20261005 | https://github.com/pallets/flask | github.com::repository_view | 4 | 3 |
| trojan | G2 | 20261005 | https://github.com/python/cpython | github.com::repository_view | 4 | 3 |
| trojan | G2 | 20261005 | https://github.com/scikit-learn/scikit-learn | github.com::repository_view | 4 | 4 |
| trojan | G2 | 20261005 | https://www.bing.com/search?q=beginner+guitar+chords | bing.com::search_results_view | 4 | 2 |
| trojan | G2 | 20261005 | https://www.bing.com/search?q=indoor+plant+care | bing.com::search_results_view | 4 | 4 |
| trojan | G2 | 20261005 | https://www.bing.com/search?q=network+traffic+analysis | bing.com::search_results_view | 4 | 4 |
| trojan | G2 | 20261005 | https://www.bing.com/search?q=solar+system+facts | bing.com::search_results_view | 4 | 2 |
| trojan | G2 | 20261005 | https://www.bing.com/search?q=sourdough+bread+recipe | bing.com::search_results_view | 4 | 3 |
| trojan | G2 | 20261005 | https://www.youtube.com/results?search_query=astronomy+documentary | youtube.com::search_results_view | 4 | 3 |
| trojan | G2 | 20261005 | https://www.youtube.com/results?search_query=bicycle+maintenance | youtube.com::search_results_view | 4 | 3 |
| trojan | G2 | 20261005 | https://www.youtube.com/results?search_query=bread+baking | youtube.com::search_results_view | 4 | 3 |
| trojan | G2 | 20261005 | https://www.youtube.com/results?search_query=piano+practice | youtube.com::search_results_view | 4 | 3 |
| trojan | G2 | 20261005 | https://www.youtube.com/results?search_query=watercolor+tutorial | youtube.com::search_results_view | 4 | 3 |
| trojan | G2 | 20261005 | youtube_video:R6MlUcmOul8 | youtube.com::video_playback | 4 | 4 |
| trojan | G2 | 20261005 | youtube_video:aircAruvnKk | youtube.com::video_playback | 4 | 4 |
| trojan | G2 | 20261005 | youtube_video:aqz-KE-bpKQ | youtube.com::video_playback | 4 | 3 |
| trojan | G2 | 20261005 | youtube_video:eRsGyueVLvQ | youtube.com::video_playback | 4 | 3 |
| trojan | G2 | 20261005 | youtube_video:sAWK0mgrMp4 | youtube.com::video_playback | 4 | 4 |
| trojan | G2 | 20261006 | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | developer.mozilla.org::document_view | 4 | 2 |
| trojan | G2 | 20261006 | https://developer.mozilla.org/en-US/docs/Web/HTTP | developer.mozilla.org::document_view | 4 | 2 |
| trojan | G2 | 20261006 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | developer.mozilla.org::document_view | 4 | 4 |
| trojan | G2 | 20261006 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | developer.mozilla.org::document_view | 4 | 2 |
| trojan | G2 | 20261006 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | developer.mozilla.org::document_view | 4 | 2 |
| trojan | G2 | 20261006 | https://en.wikipedia.org/wiki/Computer_network | wikipedia.org::article_view | 4 | 3 |
| trojan | G2 | 20261006 | https://en.wikipedia.org/wiki/Domain_Name_System | wikipedia.org::article_view | 4 | 3 |
| trojan | G2 | 20261006 | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | wikipedia.org::article_view | 4 | 3 |
| trojan | G2 | 20261006 | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | wikipedia.org::article_view | 4 | 4 |
| trojan | G2 | 20261006 | https://en.wikipedia.org/wiki/Transport_Layer_Security | wikipedia.org::article_view | 4 | 3 |
| trojan | G2 | 20261006 | https://github.com/RakuLomis/TrafficTracer | github.com::repository_view | 4 | 4 |
| trojan | G2 | 20261006 | https://github.com/numpy/numpy | github.com::repository_view | 4 | 4 |
| trojan | G2 | 20261006 | https://github.com/pallets/flask | github.com::repository_view | 4 | 4 |
| trojan | G2 | 20261006 | https://github.com/python/cpython | github.com::repository_view | 4 | 3 |
| trojan | G2 | 20261006 | https://github.com/scikit-learn/scikit-learn | github.com::repository_view | 4 | 4 |
| trojan | G2 | 20261006 | https://www.bing.com/search?q=beginner+guitar+chords | bing.com::search_results_view | 4 | 2 |
| trojan | G2 | 20261006 | https://www.bing.com/search?q=indoor+plant+care | bing.com::search_results_view | 4 | 4 |
| trojan | G2 | 20261006 | https://www.bing.com/search?q=network+traffic+analysis | bing.com::search_results_view | 4 | 3 |
| trojan | G2 | 20261006 | https://www.bing.com/search?q=solar+system+facts | bing.com::search_results_view | 4 | 2 |
| trojan | G2 | 20261006 | https://www.bing.com/search?q=sourdough+bread+recipe | bing.com::search_results_view | 4 | 4 |
| trojan | G2 | 20261006 | https://www.youtube.com/results?search_query=astronomy+documentary | youtube.com::search_results_view | 4 | 3 |
| trojan | G2 | 20261006 | https://www.youtube.com/results?search_query=bicycle+maintenance | youtube.com::search_results_view | 4 | 2 |
| trojan | G2 | 20261006 | https://www.youtube.com/results?search_query=bread+baking | youtube.com::search_results_view | 4 | 3 |
| trojan | G2 | 20261006 | https://www.youtube.com/results?search_query=piano+practice | youtube.com::search_results_view | 4 | 4 |
| trojan | G2 | 20261006 | https://www.youtube.com/results?search_query=watercolor+tutorial | youtube.com::search_results_view | 4 | 3 |
| trojan | G2 | 20261006 | youtube_video:R6MlUcmOul8 | youtube.com::video_playback | 4 | 3 |
| trojan | G2 | 20261006 | youtube_video:aircAruvnKk | youtube.com::video_playback | 4 | 4 |
| trojan | G2 | 20261006 | youtube_video:aqz-KE-bpKQ | youtube.com::video_playback | 4 | 3 |
| trojan | G2 | 20261006 | youtube_video:eRsGyueVLvQ | youtube.com::video_playback | 4 | 3 |
| trojan | G2 | 20261006 | youtube_video:sAWK0mgrMp4 | youtube.com::video_playback | 4 | 4 |
| trojan | G2 | 20261007 | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | developer.mozilla.org::document_view | 4 | 2 |
| trojan | G2 | 20261007 | https://developer.mozilla.org/en-US/docs/Web/HTTP | developer.mozilla.org::document_view | 4 | 3 |
| trojan | G2 | 20261007 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | developer.mozilla.org::document_view | 4 | 4 |
| trojan | G2 | 20261007 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | developer.mozilla.org::document_view | 4 | 2 |
| trojan | G2 | 20261007 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | developer.mozilla.org::document_view | 4 | 2 |
| trojan | G2 | 20261007 | https://en.wikipedia.org/wiki/Computer_network | wikipedia.org::article_view | 4 | 3 |
| trojan | G2 | 20261007 | https://en.wikipedia.org/wiki/Domain_Name_System | wikipedia.org::article_view | 4 | 3 |
| trojan | G2 | 20261007 | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | wikipedia.org::article_view | 4 | 3 |
| trojan | G2 | 20261007 | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | wikipedia.org::article_view | 4 | 4 |
| trojan | G2 | 20261007 | https://en.wikipedia.org/wiki/Transport_Layer_Security | wikipedia.org::article_view | 4 | 3 |
| trojan | G2 | 20261007 | https://github.com/RakuLomis/TrafficTracer | github.com::repository_view | 4 | 3 |
| trojan | G2 | 20261007 | https://github.com/numpy/numpy | github.com::repository_view | 4 | 4 |
| trojan | G2 | 20261007 | https://github.com/pallets/flask | github.com::repository_view | 4 | 4 |
| trojan | G2 | 20261007 | https://github.com/python/cpython | github.com::repository_view | 4 | 3 |
| trojan | G2 | 20261007 | https://github.com/scikit-learn/scikit-learn | github.com::repository_view | 4 | 4 |
| trojan | G2 | 20261007 | https://www.bing.com/search?q=beginner+guitar+chords | bing.com::search_results_view | 4 | 1 |
| trojan | G2 | 20261007 | https://www.bing.com/search?q=indoor+plant+care | bing.com::search_results_view | 4 | 4 |
| trojan | G2 | 20261007 | https://www.bing.com/search?q=network+traffic+analysis | bing.com::search_results_view | 4 | 3 |
| trojan | G2 | 20261007 | https://www.bing.com/search?q=solar+system+facts | bing.com::search_results_view | 4 | 2 |
| trojan | G2 | 20261007 | https://www.bing.com/search?q=sourdough+bread+recipe | bing.com::search_results_view | 4 | 4 |
| trojan | G2 | 20261007 | https://www.youtube.com/results?search_query=astronomy+documentary | youtube.com::search_results_view | 4 | 4 |
| trojan | G2 | 20261007 | https://www.youtube.com/results?search_query=bicycle+maintenance | youtube.com::search_results_view | 4 | 2 |
| trojan | G2 | 20261007 | https://www.youtube.com/results?search_query=bread+baking | youtube.com::search_results_view | 4 | 3 |
| trojan | G2 | 20261007 | https://www.youtube.com/results?search_query=piano+practice | youtube.com::search_results_view | 4 | 4 |
| trojan | G2 | 20261007 | https://www.youtube.com/results?search_query=watercolor+tutorial | youtube.com::search_results_view | 4 | 3 |
| trojan | G2 | 20261007 | youtube_video:R6MlUcmOul8 | youtube.com::video_playback | 4 | 3 |
| trojan | G2 | 20261007 | youtube_video:aircAruvnKk | youtube.com::video_playback | 4 | 4 |
| trojan | G2 | 20261007 | youtube_video:aqz-KE-bpKQ | youtube.com::video_playback | 4 | 3 |
| trojan | G2 | 20261007 | youtube_video:eRsGyueVLvQ | youtube.com::video_playback | 4 | 3 |
| trojan | G2 | 20261007 | youtube_video:sAWK0mgrMp4 | youtube.com::video_playback | 4 | 4 |
| trojan | G3 | -1 | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | developer.mozilla.org::document_view | 4 | 0 |
| trojan | G3 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP | developer.mozilla.org::document_view | 4 | 0 |
| trojan | G3 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | developer.mozilla.org::document_view | 4 | 0 |
| trojan | G3 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | developer.mozilla.org::document_view | 4 | 0 |
| trojan | G3 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | developer.mozilla.org::document_view | 4 | 0 |
| trojan | G3 | -1 | https://en.wikipedia.org/wiki/Computer_network | wikipedia.org::article_view | 4 | 0 |
| trojan | G3 | -1 | https://en.wikipedia.org/wiki/Domain_Name_System | wikipedia.org::article_view | 4 | 0 |
| trojan | G3 | -1 | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | wikipedia.org::article_view | 4 | 0 |
| trojan | G3 | -1 | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | wikipedia.org::article_view | 4 | 0 |
| trojan | G3 | -1 | https://en.wikipedia.org/wiki/Transport_Layer_Security | wikipedia.org::article_view | 4 | 0 |
| trojan | G3 | -1 | https://github.com/RakuLomis/TrafficTracer | github.com::repository_view | 4 | 0 |
| trojan | G3 | -1 | https://github.com/numpy/numpy | github.com::repository_view | 4 | 0 |
| trojan | G3 | -1 | https://github.com/pallets/flask | github.com::repository_view | 4 | 0 |
| trojan | G3 | -1 | https://github.com/python/cpython | github.com::repository_view | 4 | 0 |
| trojan | G3 | -1 | https://github.com/scikit-learn/scikit-learn | github.com::repository_view | 4 | 0 |
| trojan | G3 | -1 | https://www.bing.com/search?q=beginner+guitar+chords | bing.com::search_results_view | 4 | 0 |
| trojan | G3 | -1 | https://www.bing.com/search?q=indoor+plant+care | bing.com::search_results_view | 4 | 0 |
| trojan | G3 | -1 | https://www.bing.com/search?q=network+traffic+analysis | bing.com::search_results_view | 4 | 1 |
| trojan | G3 | -1 | https://www.bing.com/search?q=solar+system+facts | bing.com::search_results_view | 4 | 1 |
| trojan | G3 | -1 | https://www.bing.com/search?q=sourdough+bread+recipe | bing.com::search_results_view | 4 | 0 |
| trojan | G3 | -1 | https://www.youtube.com/results?search_query=astronomy+documentary | youtube.com::search_results_view | 4 | 4 |
| trojan | G3 | -1 | https://www.youtube.com/results?search_query=bicycle+maintenance | youtube.com::search_results_view | 4 | 4 |
| trojan | G3 | -1 | https://www.youtube.com/results?search_query=bread+baking | youtube.com::search_results_view | 4 | 4 |
| trojan | G3 | -1 | https://www.youtube.com/results?search_query=piano+practice | youtube.com::search_results_view | 4 | 4 |
| trojan | G3 | -1 | https://www.youtube.com/results?search_query=watercolor+tutorial | youtube.com::search_results_view | 4 | 4 |
| trojan | G3 | -1 | youtube_video:R6MlUcmOul8 | youtube.com::video_playback | 4 | 0 |
| trojan | G3 | -1 | youtube_video:aircAruvnKk | youtube.com::video_playback | 4 | 0 |
| trojan | G3 | -1 | youtube_video:aqz-KE-bpKQ | youtube.com::video_playback | 4 | 0 |
| trojan | G3 | -1 | youtube_video:eRsGyueVLvQ | youtube.com::video_playback | 4 | 0 |
| trojan | G3 | -1 | youtube_video:sAWK0mgrMp4 | youtube.com::video_playback | 4 | 0 |
| trojan | G4 | -1 | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | developer.mozilla.org::document_view | 4 | 3 |
| trojan | G4 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP | developer.mozilla.org::document_view | 4 | 2 |
| trojan | G4 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | developer.mozilla.org::document_view | 4 | 2 |
| trojan | G4 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | developer.mozilla.org::document_view | 4 | 2 |
| trojan | G4 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | developer.mozilla.org::document_view | 4 | 3 |
| trojan | G4 | -1 | https://en.wikipedia.org/wiki/Computer_network | wikipedia.org::article_view | 4 | 2 |
| trojan | G4 | -1 | https://en.wikipedia.org/wiki/Domain_Name_System | wikipedia.org::article_view | 4 | 0 |
| trojan | G4 | -1 | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | wikipedia.org::article_view | 4 | 1 |
| trojan | G4 | -1 | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | wikipedia.org::article_view | 4 | 3 |
| trojan | G4 | -1 | https://en.wikipedia.org/wiki/Transport_Layer_Security | wikipedia.org::article_view | 4 | 1 |
| trojan | G4 | -1 | https://github.com/RakuLomis/TrafficTracer | github.com::repository_view | 4 | 4 |
| trojan | G4 | -1 | https://github.com/numpy/numpy | github.com::repository_view | 4 | 4 |
| trojan | G4 | -1 | https://github.com/pallets/flask | github.com::repository_view | 4 | 3 |
| trojan | G4 | -1 | https://github.com/python/cpython | github.com::repository_view | 4 | 3 |
| trojan | G4 | -1 | https://github.com/scikit-learn/scikit-learn | github.com::repository_view | 4 | 4 |
| trojan | G4 | -1 | https://www.bing.com/search?q=beginner+guitar+chords | bing.com::search_results_view | 4 | 1 |
| trojan | G4 | -1 | https://www.bing.com/search?q=indoor+plant+care | bing.com::search_results_view | 4 | 4 |
| trojan | G4 | -1 | https://www.bing.com/search?q=network+traffic+analysis | bing.com::search_results_view | 4 | 2 |
| trojan | G4 | -1 | https://www.bing.com/search?q=solar+system+facts | bing.com::search_results_view | 4 | 3 |
| trojan | G4 | -1 | https://www.bing.com/search?q=sourdough+bread+recipe | bing.com::search_results_view | 4 | 4 |
| trojan | G4 | -1 | https://www.youtube.com/results?search_query=astronomy+documentary | youtube.com::search_results_view | 4 | 2 |
| trojan | G4 | -1 | https://www.youtube.com/results?search_query=bicycle+maintenance | youtube.com::search_results_view | 4 | 3 |
| trojan | G4 | -1 | https://www.youtube.com/results?search_query=bread+baking | youtube.com::search_results_view | 4 | 3 |
| trojan | G4 | -1 | https://www.youtube.com/results?search_query=piano+practice | youtube.com::search_results_view | 4 | 3 |
| trojan | G4 | -1 | https://www.youtube.com/results?search_query=watercolor+tutorial | youtube.com::search_results_view | 4 | 3 |
| trojan | G4 | -1 | youtube_video:R6MlUcmOul8 | youtube.com::video_playback | 4 | 1 |
| trojan | G4 | -1 | youtube_video:aircAruvnKk | youtube.com::video_playback | 4 | 3 |
| trojan | G4 | -1 | youtube_video:aqz-KE-bpKQ | youtube.com::video_playback | 4 | 0 |
| trojan | G4 | -1 | youtube_video:eRsGyueVLvQ | youtube.com::video_playback | 4 | 2 |
| trojan | G4 | -1 | youtube_video:sAWK0mgrMp4 | youtube.com::video_playback | 4 | 1 |
| trojan | G5 | -1 | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | developer.mozilla.org::document_view | 4 | 0 |
| trojan | G5 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP | developer.mozilla.org::document_view | 4 | 0 |
| trojan | G5 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | developer.mozilla.org::document_view | 4 | 0 |
| trojan | G5 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | developer.mozilla.org::document_view | 4 | 0 |
| trojan | G5 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | developer.mozilla.org::document_view | 4 | 0 |
| trojan | G5 | -1 | https://en.wikipedia.org/wiki/Computer_network | wikipedia.org::article_view | 4 | 3 |
| trojan | G5 | -1 | https://en.wikipedia.org/wiki/Domain_Name_System | wikipedia.org::article_view | 4 | 4 |
| trojan | G5 | -1 | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | wikipedia.org::article_view | 4 | 3 |
| trojan | G5 | -1 | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | wikipedia.org::article_view | 4 | 4 |
| trojan | G5 | -1 | https://en.wikipedia.org/wiki/Transport_Layer_Security | wikipedia.org::article_view | 4 | 2 |
| trojan | G5 | -1 | https://github.com/RakuLomis/TrafficTracer | github.com::repository_view | 4 | 1 |
| trojan | G5 | -1 | https://github.com/numpy/numpy | github.com::repository_view | 4 | 2 |
| trojan | G5 | -1 | https://github.com/pallets/flask | github.com::repository_view | 4 | 3 |
| trojan | G5 | -1 | https://github.com/python/cpython | github.com::repository_view | 4 | 1 |
| trojan | G5 | -1 | https://github.com/scikit-learn/scikit-learn | github.com::repository_view | 4 | 2 |
| trojan | G5 | -1 | https://www.bing.com/search?q=beginner+guitar+chords | bing.com::search_results_view | 4 | 1 |
| trojan | G5 | -1 | https://www.bing.com/search?q=indoor+plant+care | bing.com::search_results_view | 4 | 0 |
| trojan | G5 | -1 | https://www.bing.com/search?q=network+traffic+analysis | bing.com::search_results_view | 4 | 0 |
| trojan | G5 | -1 | https://www.bing.com/search?q=solar+system+facts | bing.com::search_results_view | 4 | 0 |
| trojan | G5 | -1 | https://www.bing.com/search?q=sourdough+bread+recipe | bing.com::search_results_view | 4 | 0 |
| trojan | G5 | -1 | https://www.youtube.com/results?search_query=astronomy+documentary | youtube.com::search_results_view | 4 | 1 |
| trojan | G5 | -1 | https://www.youtube.com/results?search_query=bicycle+maintenance | youtube.com::search_results_view | 4 | 1 |
| trojan | G5 | -1 | https://www.youtube.com/results?search_query=bread+baking | youtube.com::search_results_view | 4 | 0 |
| trojan | G5 | -1 | https://www.youtube.com/results?search_query=piano+practice | youtube.com::search_results_view | 4 | 0 |
| trojan | G5 | -1 | https://www.youtube.com/results?search_query=watercolor+tutorial | youtube.com::search_results_view | 4 | 0 |
| trojan | G5 | -1 | youtube_video:R6MlUcmOul8 | youtube.com::video_playback | 4 | 3 |
| trojan | G5 | -1 | youtube_video:aircAruvnKk | youtube.com::video_playback | 4 | 3 |
| trojan | G5 | -1 | youtube_video:aqz-KE-bpKQ | youtube.com::video_playback | 4 | 3 |
| trojan | G5 | -1 | youtube_video:eRsGyueVLvQ | youtube.com::video_playback | 4 | 4 |
| trojan | G5 | -1 | youtube_video:sAWK0mgrMp4 | youtube.com::video_playback | 4 | 3 |
| vless | G0 | -1 | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | developer.mozilla.org::document_view | 4 | 2 |
| vless | G0 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP | developer.mozilla.org::document_view | 4 | 2 |
| vless | G0 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | developer.mozilla.org::document_view | 4 | 3 |
| vless | G0 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | developer.mozilla.org::document_view | 4 | 2 |
| vless | G0 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | developer.mozilla.org::document_view | 4 | 4 |
| vless | G0 | -1 | https://en.wikipedia.org/wiki/Computer_network | wikipedia.org::article_view | 4 | 3 |
| vless | G0 | -1 | https://en.wikipedia.org/wiki/Domain_Name_System | wikipedia.org::article_view | 4 | 4 |
| vless | G0 | -1 | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | wikipedia.org::article_view | 4 | 1 |
| vless | G0 | -1 | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | wikipedia.org::article_view | 4 | 3 |
| vless | G0 | -1 | https://en.wikipedia.org/wiki/Transport_Layer_Security | wikipedia.org::article_view | 4 | 3 |
| vless | G0 | -1 | https://github.com/RakuLomis/TrafficTracer | github.com::repository_view | 4 | 3 |
| vless | G0 | -1 | https://github.com/numpy/numpy | github.com::repository_view | 4 | 3 |
| vless | G0 | -1 | https://github.com/pallets/flask | github.com::repository_view | 4 | 3 |
| vless | G0 | -1 | https://github.com/python/cpython | github.com::repository_view | 4 | 3 |
| vless | G0 | -1 | https://github.com/scikit-learn/scikit-learn | github.com::repository_view | 4 | 3 |
| vless | G0 | -1 | https://www.bing.com/search?q=beginner+guitar+chords | bing.com::search_results_view | 4 | 2 |
| vless | G0 | -1 | https://www.bing.com/search?q=indoor+plant+care | bing.com::search_results_view | 4 | 1 |
| vless | G0 | -1 | https://www.bing.com/search?q=network+traffic+analysis | bing.com::search_results_view | 4 | 2 |
| vless | G0 | -1 | https://www.bing.com/search?q=solar+system+facts | bing.com::search_results_view | 4 | 1 |
| vless | G0 | -1 | https://www.bing.com/search?q=sourdough+bread+recipe | bing.com::search_results_view | 4 | 2 |
| vless | G0 | -1 | https://www.youtube.com/results?search_query=astronomy+documentary | youtube.com::search_results_view | 4 | 2 |
| vless | G0 | -1 | https://www.youtube.com/results?search_query=bicycle+maintenance | youtube.com::search_results_view | 4 | 2 |
| vless | G0 | -1 | https://www.youtube.com/results?search_query=bread+baking | youtube.com::search_results_view | 4 | 2 |
| vless | G0 | -1 | https://www.youtube.com/results?search_query=piano+practice | youtube.com::search_results_view | 4 | 0 |
| vless | G0 | -1 | https://www.youtube.com/results?search_query=watercolor+tutorial | youtube.com::search_results_view | 4 | 1 |
| vless | G0 | -1 | youtube_video:R6MlUcmOul8 | youtube.com::video_playback | 4 | 2 |
| vless | G0 | -1 | youtube_video:aircAruvnKk | youtube.com::video_playback | 4 | 2 |
| vless | G0 | -1 | youtube_video:aqz-KE-bpKQ | youtube.com::video_playback | 4 | 2 |
| vless | G0 | -1 | youtube_video:eRsGyueVLvQ | youtube.com::video_playback | 4 | 2 |
| vless | G0 | -1 | youtube_video:sAWK0mgrMp4 | youtube.com::video_playback | 4 | 4 |
| vless | G1 | -1 | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | developer.mozilla.org::document_view | 4 | 3 |
| vless | G1 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP | developer.mozilla.org::document_view | 4 | 4 |
| vless | G1 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | developer.mozilla.org::document_view | 4 | 4 |
| vless | G1 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | developer.mozilla.org::document_view | 4 | 3 |
| vless | G1 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | developer.mozilla.org::document_view | 4 | 2 |
| vless | G1 | -1 | https://en.wikipedia.org/wiki/Computer_network | wikipedia.org::article_view | 4 | 3 |
| vless | G1 | -1 | https://en.wikipedia.org/wiki/Domain_Name_System | wikipedia.org::article_view | 4 | 3 |
| vless | G1 | -1 | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | wikipedia.org::article_view | 4 | 3 |
| vless | G1 | -1 | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | wikipedia.org::article_view | 4 | 4 |
| vless | G1 | -1 | https://en.wikipedia.org/wiki/Transport_Layer_Security | wikipedia.org::article_view | 4 | 2 |
| vless | G1 | -1 | https://github.com/RakuLomis/TrafficTracer | github.com::repository_view | 4 | 4 |
| vless | G1 | -1 | https://github.com/numpy/numpy | github.com::repository_view | 4 | 3 |
| vless | G1 | -1 | https://github.com/pallets/flask | github.com::repository_view | 4 | 3 |
| vless | G1 | -1 | https://github.com/python/cpython | github.com::repository_view | 4 | 4 |
| vless | G1 | -1 | https://github.com/scikit-learn/scikit-learn | github.com::repository_view | 4 | 3 |
| vless | G1 | -1 | https://www.bing.com/search?q=beginner+guitar+chords | bing.com::search_results_view | 4 | 4 |
| vless | G1 | -1 | https://www.bing.com/search?q=indoor+plant+care | bing.com::search_results_view | 4 | 2 |
| vless | G1 | -1 | https://www.bing.com/search?q=network+traffic+analysis | bing.com::search_results_view | 4 | 3 |
| vless | G1 | -1 | https://www.bing.com/search?q=solar+system+facts | bing.com::search_results_view | 4 | 4 |
| vless | G1 | -1 | https://www.bing.com/search?q=sourdough+bread+recipe | bing.com::search_results_view | 4 | 3 |
| vless | G1 | -1 | https://www.youtube.com/results?search_query=astronomy+documentary | youtube.com::search_results_view | 4 | 3 |
| vless | G1 | -1 | https://www.youtube.com/results?search_query=bicycle+maintenance | youtube.com::search_results_view | 4 | 2 |
| vless | G1 | -1 | https://www.youtube.com/results?search_query=bread+baking | youtube.com::search_results_view | 4 | 3 |
| vless | G1 | -1 | https://www.youtube.com/results?search_query=piano+practice | youtube.com::search_results_view | 4 | 3 |
| vless | G1 | -1 | https://www.youtube.com/results?search_query=watercolor+tutorial | youtube.com::search_results_view | 4 | 3 |
| vless | G1 | -1 | youtube_video:R6MlUcmOul8 | youtube.com::video_playback | 4 | 4 |
| vless | G1 | -1 | youtube_video:aircAruvnKk | youtube.com::video_playback | 4 | 3 |
| vless | G1 | -1 | youtube_video:aqz-KE-bpKQ | youtube.com::video_playback | 4 | 4 |
| vless | G1 | -1 | youtube_video:eRsGyueVLvQ | youtube.com::video_playback | 4 | 4 |
| vless | G1 | -1 | youtube_video:sAWK0mgrMp4 | youtube.com::video_playback | 4 | 4 |
| vless | G2 | 20261005 | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | developer.mozilla.org::document_view | 4 | 2 |
| vless | G2 | 20261005 | https://developer.mozilla.org/en-US/docs/Web/HTTP | developer.mozilla.org::document_view | 4 | 3 |
| vless | G2 | 20261005 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | developer.mozilla.org::document_view | 4 | 3 |
| vless | G2 | 20261005 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | developer.mozilla.org::document_view | 4 | 3 |
| vless | G2 | 20261005 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | developer.mozilla.org::document_view | 4 | 3 |
| vless | G2 | 20261005 | https://en.wikipedia.org/wiki/Computer_network | wikipedia.org::article_view | 4 | 3 |
| vless | G2 | 20261005 | https://en.wikipedia.org/wiki/Domain_Name_System | wikipedia.org::article_view | 4 | 3 |
| vless | G2 | 20261005 | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | wikipedia.org::article_view | 4 | 3 |
| vless | G2 | 20261005 | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | wikipedia.org::article_view | 4 | 4 |
| vless | G2 | 20261005 | https://en.wikipedia.org/wiki/Transport_Layer_Security | wikipedia.org::article_view | 4 | 2 |
| vless | G2 | 20261005 | https://github.com/RakuLomis/TrafficTracer | github.com::repository_view | 4 | 4 |
| vless | G2 | 20261005 | https://github.com/numpy/numpy | github.com::repository_view | 4 | 3 |
| vless | G2 | 20261005 | https://github.com/pallets/flask | github.com::repository_view | 4 | 3 |
| vless | G2 | 20261005 | https://github.com/python/cpython | github.com::repository_view | 4 | 4 |
| vless | G2 | 20261005 | https://github.com/scikit-learn/scikit-learn | github.com::repository_view | 4 | 3 |
| vless | G2 | 20261005 | https://www.bing.com/search?q=beginner+guitar+chords | bing.com::search_results_view | 4 | 4 |
| vless | G2 | 20261005 | https://www.bing.com/search?q=indoor+plant+care | bing.com::search_results_view | 4 | 1 |
| vless | G2 | 20261005 | https://www.bing.com/search?q=network+traffic+analysis | bing.com::search_results_view | 4 | 3 |
| vless | G2 | 20261005 | https://www.bing.com/search?q=solar+system+facts | bing.com::search_results_view | 4 | 4 |
| vless | G2 | 20261005 | https://www.bing.com/search?q=sourdough+bread+recipe | bing.com::search_results_view | 4 | 3 |
| vless | G2 | 20261005 | https://www.youtube.com/results?search_query=astronomy+documentary | youtube.com::search_results_view | 4 | 3 |
| vless | G2 | 20261005 | https://www.youtube.com/results?search_query=bicycle+maintenance | youtube.com::search_results_view | 4 | 2 |
| vless | G2 | 20261005 | https://www.youtube.com/results?search_query=bread+baking | youtube.com::search_results_view | 4 | 3 |
| vless | G2 | 20261005 | https://www.youtube.com/results?search_query=piano+practice | youtube.com::search_results_view | 4 | 3 |
| vless | G2 | 20261005 | https://www.youtube.com/results?search_query=watercolor+tutorial | youtube.com::search_results_view | 4 | 4 |
| vless | G2 | 20261005 | youtube_video:R6MlUcmOul8 | youtube.com::video_playback | 4 | 3 |
| vless | G2 | 20261005 | youtube_video:aircAruvnKk | youtube.com::video_playback | 4 | 3 |
| vless | G2 | 20261005 | youtube_video:aqz-KE-bpKQ | youtube.com::video_playback | 4 | 4 |
| vless | G2 | 20261005 | youtube_video:eRsGyueVLvQ | youtube.com::video_playback | 4 | 4 |
| vless | G2 | 20261005 | youtube_video:sAWK0mgrMp4 | youtube.com::video_playback | 4 | 4 |
| vless | G2 | 20261006 | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | developer.mozilla.org::document_view | 4 | 2 |
| vless | G2 | 20261006 | https://developer.mozilla.org/en-US/docs/Web/HTTP | developer.mozilla.org::document_view | 4 | 2 |
| vless | G2 | 20261006 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | developer.mozilla.org::document_view | 4 | 3 |
| vless | G2 | 20261006 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | developer.mozilla.org::document_view | 4 | 3 |
| vless | G2 | 20261006 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | developer.mozilla.org::document_view | 4 | 3 |
| vless | G2 | 20261006 | https://en.wikipedia.org/wiki/Computer_network | wikipedia.org::article_view | 4 | 3 |
| vless | G2 | 20261006 | https://en.wikipedia.org/wiki/Domain_Name_System | wikipedia.org::article_view | 4 | 2 |
| vless | G2 | 20261006 | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | wikipedia.org::article_view | 4 | 3 |
| vless | G2 | 20261006 | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | wikipedia.org::article_view | 4 | 3 |
| vless | G2 | 20261006 | https://en.wikipedia.org/wiki/Transport_Layer_Security | wikipedia.org::article_view | 4 | 2 |
| vless | G2 | 20261006 | https://github.com/RakuLomis/TrafficTracer | github.com::repository_view | 4 | 4 |
| vless | G2 | 20261006 | https://github.com/numpy/numpy | github.com::repository_view | 4 | 3 |
| vless | G2 | 20261006 | https://github.com/pallets/flask | github.com::repository_view | 4 | 3 |
| vless | G2 | 20261006 | https://github.com/python/cpython | github.com::repository_view | 4 | 4 |
| vless | G2 | 20261006 | https://github.com/scikit-learn/scikit-learn | github.com::repository_view | 4 | 3 |
| vless | G2 | 20261006 | https://www.bing.com/search?q=beginner+guitar+chords | bing.com::search_results_view | 4 | 3 |
| vless | G2 | 20261006 | https://www.bing.com/search?q=indoor+plant+care | bing.com::search_results_view | 4 | 1 |
| vless | G2 | 20261006 | https://www.bing.com/search?q=network+traffic+analysis | bing.com::search_results_view | 4 | 2 |
| vless | G2 | 20261006 | https://www.bing.com/search?q=solar+system+facts | bing.com::search_results_view | 4 | 4 |
| vless | G2 | 20261006 | https://www.bing.com/search?q=sourdough+bread+recipe | bing.com::search_results_view | 4 | 3 |
| vless | G2 | 20261006 | https://www.youtube.com/results?search_query=astronomy+documentary | youtube.com::search_results_view | 4 | 3 |
| vless | G2 | 20261006 | https://www.youtube.com/results?search_query=bicycle+maintenance | youtube.com::search_results_view | 4 | 3 |
| vless | G2 | 20261006 | https://www.youtube.com/results?search_query=bread+baking | youtube.com::search_results_view | 4 | 2 |
| vless | G2 | 20261006 | https://www.youtube.com/results?search_query=piano+practice | youtube.com::search_results_view | 4 | 3 |
| vless | G2 | 20261006 | https://www.youtube.com/results?search_query=watercolor+tutorial | youtube.com::search_results_view | 4 | 4 |
| vless | G2 | 20261006 | youtube_video:R6MlUcmOul8 | youtube.com::video_playback | 4 | 4 |
| vless | G2 | 20261006 | youtube_video:aircAruvnKk | youtube.com::video_playback | 4 | 3 |
| vless | G2 | 20261006 | youtube_video:aqz-KE-bpKQ | youtube.com::video_playback | 4 | 4 |
| vless | G2 | 20261006 | youtube_video:eRsGyueVLvQ | youtube.com::video_playback | 4 | 4 |
| vless | G2 | 20261006 | youtube_video:sAWK0mgrMp4 | youtube.com::video_playback | 4 | 4 |
| vless | G2 | 20261007 | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | developer.mozilla.org::document_view | 4 | 2 |
| vless | G2 | 20261007 | https://developer.mozilla.org/en-US/docs/Web/HTTP | developer.mozilla.org::document_view | 4 | 3 |
| vless | G2 | 20261007 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | developer.mozilla.org::document_view | 4 | 3 |
| vless | G2 | 20261007 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | developer.mozilla.org::document_view | 4 | 3 |
| vless | G2 | 20261007 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | developer.mozilla.org::document_view | 4 | 3 |
| vless | G2 | 20261007 | https://en.wikipedia.org/wiki/Computer_network | wikipedia.org::article_view | 4 | 3 |
| vless | G2 | 20261007 | https://en.wikipedia.org/wiki/Domain_Name_System | wikipedia.org::article_view | 4 | 2 |
| vless | G2 | 20261007 | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | wikipedia.org::article_view | 4 | 3 |
| vless | G2 | 20261007 | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | wikipedia.org::article_view | 4 | 4 |
| vless | G2 | 20261007 | https://en.wikipedia.org/wiki/Transport_Layer_Security | wikipedia.org::article_view | 4 | 2 |
| vless | G2 | 20261007 | https://github.com/RakuLomis/TrafficTracer | github.com::repository_view | 4 | 4 |
| vless | G2 | 20261007 | https://github.com/numpy/numpy | github.com::repository_view | 4 | 4 |
| vless | G2 | 20261007 | https://github.com/pallets/flask | github.com::repository_view | 4 | 3 |
| vless | G2 | 20261007 | https://github.com/python/cpython | github.com::repository_view | 4 | 3 |
| vless | G2 | 20261007 | https://github.com/scikit-learn/scikit-learn | github.com::repository_view | 4 | 3 |
| vless | G2 | 20261007 | https://www.bing.com/search?q=beginner+guitar+chords | bing.com::search_results_view | 4 | 4 |
| vless | G2 | 20261007 | https://www.bing.com/search?q=indoor+plant+care | bing.com::search_results_view | 4 | 0 |
| vless | G2 | 20261007 | https://www.bing.com/search?q=network+traffic+analysis | bing.com::search_results_view | 4 | 3 |
| vless | G2 | 20261007 | https://www.bing.com/search?q=solar+system+facts | bing.com::search_results_view | 4 | 4 |
| vless | G2 | 20261007 | https://www.bing.com/search?q=sourdough+bread+recipe | bing.com::search_results_view | 4 | 3 |
| vless | G2 | 20261007 | https://www.youtube.com/results?search_query=astronomy+documentary | youtube.com::search_results_view | 4 | 3 |
| vless | G2 | 20261007 | https://www.youtube.com/results?search_query=bicycle+maintenance | youtube.com::search_results_view | 4 | 3 |
| vless | G2 | 20261007 | https://www.youtube.com/results?search_query=bread+baking | youtube.com::search_results_view | 4 | 3 |
| vless | G2 | 20261007 | https://www.youtube.com/results?search_query=piano+practice | youtube.com::search_results_view | 4 | 3 |
| vless | G2 | 20261007 | https://www.youtube.com/results?search_query=watercolor+tutorial | youtube.com::search_results_view | 4 | 3 |
| vless | G2 | 20261007 | youtube_video:R6MlUcmOul8 | youtube.com::video_playback | 4 | 4 |
| vless | G2 | 20261007 | youtube_video:aircAruvnKk | youtube.com::video_playback | 4 | 3 |
| vless | G2 | 20261007 | youtube_video:aqz-KE-bpKQ | youtube.com::video_playback | 4 | 4 |
| vless | G2 | 20261007 | youtube_video:eRsGyueVLvQ | youtube.com::video_playback | 4 | 4 |
| vless | G2 | 20261007 | youtube_video:sAWK0mgrMp4 | youtube.com::video_playback | 4 | 4 |
| vless | G3 | -1 | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | developer.mozilla.org::document_view | 4 | 0 |
| vless | G3 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP | developer.mozilla.org::document_view | 4 | 0 |
| vless | G3 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | developer.mozilla.org::document_view | 4 | 0 |
| vless | G3 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | developer.mozilla.org::document_view | 4 | 0 |
| vless | G3 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | developer.mozilla.org::document_view | 4 | 0 |
| vless | G3 | -1 | https://en.wikipedia.org/wiki/Computer_network | wikipedia.org::article_view | 4 | 0 |
| vless | G3 | -1 | https://en.wikipedia.org/wiki/Domain_Name_System | wikipedia.org::article_view | 4 | 0 |
| vless | G3 | -1 | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | wikipedia.org::article_view | 4 | 0 |
| vless | G3 | -1 | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | wikipedia.org::article_view | 4 | 0 |
| vless | G3 | -1 | https://en.wikipedia.org/wiki/Transport_Layer_Security | wikipedia.org::article_view | 4 | 0 |
| vless | G3 | -1 | https://github.com/RakuLomis/TrafficTracer | github.com::repository_view | 4 | 0 |
| vless | G3 | -1 | https://github.com/numpy/numpy | github.com::repository_view | 4 | 0 |
| vless | G3 | -1 | https://github.com/pallets/flask | github.com::repository_view | 4 | 0 |
| vless | G3 | -1 | https://github.com/python/cpython | github.com::repository_view | 4 | 0 |
| vless | G3 | -1 | https://github.com/scikit-learn/scikit-learn | github.com::repository_view | 4 | 0 |
| vless | G3 | -1 | https://www.bing.com/search?q=beginner+guitar+chords | bing.com::search_results_view | 4 | 0 |
| vless | G3 | -1 | https://www.bing.com/search?q=indoor+plant+care | bing.com::search_results_view | 4 | 1 |
| vless | G3 | -1 | https://www.bing.com/search?q=network+traffic+analysis | bing.com::search_results_view | 4 | 1 |
| vless | G3 | -1 | https://www.bing.com/search?q=solar+system+facts | bing.com::search_results_view | 4 | 3 |
| vless | G3 | -1 | https://www.bing.com/search?q=sourdough+bread+recipe | bing.com::search_results_view | 4 | 4 |
| vless | G3 | -1 | https://www.youtube.com/results?search_query=astronomy+documentary | youtube.com::search_results_view | 4 | 0 |
| vless | G3 | -1 | https://www.youtube.com/results?search_query=bicycle+maintenance | youtube.com::search_results_view | 4 | 0 |
| vless | G3 | -1 | https://www.youtube.com/results?search_query=bread+baking | youtube.com::search_results_view | 4 | 0 |
| vless | G3 | -1 | https://www.youtube.com/results?search_query=piano+practice | youtube.com::search_results_view | 4 | 1 |
| vless | G3 | -1 | https://www.youtube.com/results?search_query=watercolor+tutorial | youtube.com::search_results_view | 4 | 0 |
| vless | G3 | -1 | youtube_video:R6MlUcmOul8 | youtube.com::video_playback | 4 | 4 |
| vless | G3 | -1 | youtube_video:aircAruvnKk | youtube.com::video_playback | 4 | 1 |
| vless | G3 | -1 | youtube_video:aqz-KE-bpKQ | youtube.com::video_playback | 4 | 4 |
| vless | G3 | -1 | youtube_video:eRsGyueVLvQ | youtube.com::video_playback | 4 | 4 |
| vless | G3 | -1 | youtube_video:sAWK0mgrMp4 | youtube.com::video_playback | 4 | 2 |
| vless | G4 | -1 | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | developer.mozilla.org::document_view | 4 | 3 |
| vless | G4 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP | developer.mozilla.org::document_view | 4 | 2 |
| vless | G4 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | developer.mozilla.org::document_view | 4 | 2 |
| vless | G4 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | developer.mozilla.org::document_view | 4 | 2 |
| vless | G4 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | developer.mozilla.org::document_view | 4 | 4 |
| vless | G4 | -1 | https://en.wikipedia.org/wiki/Computer_network | wikipedia.org::article_view | 4 | 1 |
| vless | G4 | -1 | https://en.wikipedia.org/wiki/Domain_Name_System | wikipedia.org::article_view | 4 | 2 |
| vless | G4 | -1 | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | wikipedia.org::article_view | 4 | 0 |
| vless | G4 | -1 | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | wikipedia.org::article_view | 4 | 0 |
| vless | G4 | -1 | https://en.wikipedia.org/wiki/Transport_Layer_Security | wikipedia.org::article_view | 4 | 2 |
| vless | G4 | -1 | https://github.com/RakuLomis/TrafficTracer | github.com::repository_view | 4 | 4 |
| vless | G4 | -1 | https://github.com/numpy/numpy | github.com::repository_view | 4 | 4 |
| vless | G4 | -1 | https://github.com/pallets/flask | github.com::repository_view | 4 | 3 |
| vless | G4 | -1 | https://github.com/python/cpython | github.com::repository_view | 4 | 2 |
| vless | G4 | -1 | https://github.com/scikit-learn/scikit-learn | github.com::repository_view | 4 | 3 |
| vless | G4 | -1 | https://www.bing.com/search?q=beginner+guitar+chords | bing.com::search_results_view | 4 | 2 |
| vless | G4 | -1 | https://www.bing.com/search?q=indoor+plant+care | bing.com::search_results_view | 4 | 1 |
| vless | G4 | -1 | https://www.bing.com/search?q=network+traffic+analysis | bing.com::search_results_view | 4 | 2 |
| vless | G4 | -1 | https://www.bing.com/search?q=solar+system+facts | bing.com::search_results_view | 4 | 1 |
| vless | G4 | -1 | https://www.bing.com/search?q=sourdough+bread+recipe | bing.com::search_results_view | 4 | 2 |
| vless | G4 | -1 | https://www.youtube.com/results?search_query=astronomy+documentary | youtube.com::search_results_view | 4 | 0 |
| vless | G4 | -1 | https://www.youtube.com/results?search_query=bicycle+maintenance | youtube.com::search_results_view | 4 | 0 |
| vless | G4 | -1 | https://www.youtube.com/results?search_query=bread+baking | youtube.com::search_results_view | 4 | 0 |
| vless | G4 | -1 | https://www.youtube.com/results?search_query=piano+practice | youtube.com::search_results_view | 4 | 0 |
| vless | G4 | -1 | https://www.youtube.com/results?search_query=watercolor+tutorial | youtube.com::search_results_view | 4 | 0 |
| vless | G4 | -1 | youtube_video:R6MlUcmOul8 | youtube.com::video_playback | 4 | 3 |
| vless | G4 | -1 | youtube_video:aircAruvnKk | youtube.com::video_playback | 4 | 2 |
| vless | G4 | -1 | youtube_video:aqz-KE-bpKQ | youtube.com::video_playback | 4 | 2 |
| vless | G4 | -1 | youtube_video:eRsGyueVLvQ | youtube.com::video_playback | 4 | 3 |
| vless | G4 | -1 | youtube_video:sAWK0mgrMp4 | youtube.com::video_playback | 4 | 4 |
| vless | G5 | -1 | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | developer.mozilla.org::document_view | 4 | 0 |
| vless | G5 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP | developer.mozilla.org::document_view | 4 | 0 |
| vless | G5 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | developer.mozilla.org::document_view | 4 | 0 |
| vless | G5 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | developer.mozilla.org::document_view | 4 | 0 |
| vless | G5 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | developer.mozilla.org::document_view | 4 | 0 |
| vless | G5 | -1 | https://en.wikipedia.org/wiki/Computer_network | wikipedia.org::article_view | 4 | 4 |
| vless | G5 | -1 | https://en.wikipedia.org/wiki/Domain_Name_System | wikipedia.org::article_view | 4 | 4 |
| vless | G5 | -1 | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | wikipedia.org::article_view | 4 | 3 |
| vless | G5 | -1 | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | wikipedia.org::article_view | 4 | 0 |
| vless | G5 | -1 | https://en.wikipedia.org/wiki/Transport_Layer_Security | wikipedia.org::article_view | 4 | 0 |
| vless | G5 | -1 | https://github.com/RakuLomis/TrafficTracer | github.com::repository_view | 4 | 1 |
| vless | G5 | -1 | https://github.com/numpy/numpy | github.com::repository_view | 4 | 0 |
| vless | G5 | -1 | https://github.com/pallets/flask | github.com::repository_view | 4 | 0 |
| vless | G5 | -1 | https://github.com/python/cpython | github.com::repository_view | 4 | 0 |
| vless | G5 | -1 | https://github.com/scikit-learn/scikit-learn | github.com::repository_view | 4 | 2 |
| vless | G5 | -1 | https://www.bing.com/search?q=beginner+guitar+chords | bing.com::search_results_view | 4 | 0 |
| vless | G5 | -1 | https://www.bing.com/search?q=indoor+plant+care | bing.com::search_results_view | 4 | 0 |
| vless | G5 | -1 | https://www.bing.com/search?q=network+traffic+analysis | bing.com::search_results_view | 4 | 0 |
| vless | G5 | -1 | https://www.bing.com/search?q=solar+system+facts | bing.com::search_results_view | 4 | 0 |
| vless | G5 | -1 | https://www.bing.com/search?q=sourdough+bread+recipe | bing.com::search_results_view | 4 | 0 |
| vless | G5 | -1 | https://www.youtube.com/results?search_query=astronomy+documentary | youtube.com::search_results_view | 4 | 2 |
| vless | G5 | -1 | https://www.youtube.com/results?search_query=bicycle+maintenance | youtube.com::search_results_view | 4 | 2 |
| vless | G5 | -1 | https://www.youtube.com/results?search_query=bread+baking | youtube.com::search_results_view | 4 | 3 |
| vless | G5 | -1 | https://www.youtube.com/results?search_query=piano+practice | youtube.com::search_results_view | 4 | 0 |
| vless | G5 | -1 | https://www.youtube.com/results?search_query=watercolor+tutorial | youtube.com::search_results_view | 4 | 4 |
| vless | G5 | -1 | youtube_video:R6MlUcmOul8 | youtube.com::video_playback | 4 | 0 |
| vless | G5 | -1 | youtube_video:aircAruvnKk | youtube.com::video_playback | 4 | 2 |
| vless | G5 | -1 | youtube_video:aqz-KE-bpKQ | youtube.com::video_playback | 4 | 1 |
| vless | G5 | -1 | youtube_video:eRsGyueVLvQ | youtube.com::video_playback | 4 | 2 |
| vless | G5 | -1 | youtube_video:sAWK0mgrMp4 | youtube.com::video_playback | 4 | 0 |
| vmess | G0 | -1 | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | developer.mozilla.org::document_view | 4 | 2 |
| vmess | G0 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP | developer.mozilla.org::document_view | 4 | 0 |
| vmess | G0 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | developer.mozilla.org::document_view | 4 | 2 |
| vmess | G0 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | developer.mozilla.org::document_view | 4 | 1 |
| vmess | G0 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | developer.mozilla.org::document_view | 4 | 2 |
| vmess | G0 | -1 | https://en.wikipedia.org/wiki/Computer_network | wikipedia.org::article_view | 4 | 4 |
| vmess | G0 | -1 | https://en.wikipedia.org/wiki/Domain_Name_System | wikipedia.org::article_view | 4 | 4 |
| vmess | G0 | -1 | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | wikipedia.org::article_view | 4 | 2 |
| vmess | G0 | -1 | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | wikipedia.org::article_view | 4 | 1 |
| vmess | G0 | -1 | https://en.wikipedia.org/wiki/Transport_Layer_Security | wikipedia.org::article_view | 4 | 4 |
| vmess | G0 | -1 | https://github.com/RakuLomis/TrafficTracer | github.com::repository_view | 4 | 3 |
| vmess | G0 | -1 | https://github.com/numpy/numpy | github.com::repository_view | 4 | 3 |
| vmess | G0 | -1 | https://github.com/pallets/flask | github.com::repository_view | 4 | 4 |
| vmess | G0 | -1 | https://github.com/python/cpython | github.com::repository_view | 4 | 4 |
| vmess | G0 | -1 | https://github.com/scikit-learn/scikit-learn | github.com::repository_view | 4 | 3 |
| vmess | G0 | -1 | https://www.bing.com/search?q=beginner+guitar+chords | bing.com::search_results_view | 4 | 1 |
| vmess | G0 | -1 | https://www.bing.com/search?q=indoor+plant+care | bing.com::search_results_view | 4 | 2 |
| vmess | G0 | -1 | https://www.bing.com/search?q=network+traffic+analysis | bing.com::search_results_view | 4 | 2 |
| vmess | G0 | -1 | https://www.bing.com/search?q=solar+system+facts | bing.com::search_results_view | 4 | 3 |
| vmess | G0 | -1 | https://www.bing.com/search?q=sourdough+bread+recipe | bing.com::search_results_view | 4 | 1 |
| vmess | G0 | -1 | https://www.youtube.com/results?search_query=astronomy+documentary | youtube.com::search_results_view | 4 | 3 |
| vmess | G0 | -1 | https://www.youtube.com/results?search_query=bicycle+maintenance | youtube.com::search_results_view | 4 | 4 |
| vmess | G0 | -1 | https://www.youtube.com/results?search_query=bread+baking | youtube.com::search_results_view | 4 | 3 |
| vmess | G0 | -1 | https://www.youtube.com/results?search_query=piano+practice | youtube.com::search_results_view | 4 | 2 |
| vmess | G0 | -1 | https://www.youtube.com/results?search_query=watercolor+tutorial | youtube.com::search_results_view | 4 | 3 |
| vmess | G0 | -1 | youtube_video:R6MlUcmOul8 | youtube.com::video_playback | 4 | 4 |
| vmess | G0 | -1 | youtube_video:aircAruvnKk | youtube.com::video_playback | 4 | 3 |
| vmess | G0 | -1 | youtube_video:aqz-KE-bpKQ | youtube.com::video_playback | 4 | 3 |
| vmess | G0 | -1 | youtube_video:eRsGyueVLvQ | youtube.com::video_playback | 4 | 4 |
| vmess | G0 | -1 | youtube_video:sAWK0mgrMp4 | youtube.com::video_playback | 4 | 3 |
| vmess | G1 | -1 | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | developer.mozilla.org::document_view | 4 | 3 |
| vmess | G1 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP | developer.mozilla.org::document_view | 4 | 1 |
| vmess | G1 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | developer.mozilla.org::document_view | 4 | 3 |
| vmess | G1 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | developer.mozilla.org::document_view | 4 | 2 |
| vmess | G1 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | developer.mozilla.org::document_view | 4 | 2 |
| vmess | G1 | -1 | https://en.wikipedia.org/wiki/Computer_network | wikipedia.org::article_view | 4 | 4 |
| vmess | G1 | -1 | https://en.wikipedia.org/wiki/Domain_Name_System | wikipedia.org::article_view | 4 | 2 |
| vmess | G1 | -1 | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | wikipedia.org::article_view | 4 | 1 |
| vmess | G1 | -1 | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | wikipedia.org::article_view | 4 | 3 |
| vmess | G1 | -1 | https://en.wikipedia.org/wiki/Transport_Layer_Security | wikipedia.org::article_view | 4 | 4 |
| vmess | G1 | -1 | https://github.com/RakuLomis/TrafficTracer | github.com::repository_view | 4 | 3 |
| vmess | G1 | -1 | https://github.com/numpy/numpy | github.com::repository_view | 4 | 3 |
| vmess | G1 | -1 | https://github.com/pallets/flask | github.com::repository_view | 4 | 4 |
| vmess | G1 | -1 | https://github.com/python/cpython | github.com::repository_view | 4 | 4 |
| vmess | G1 | -1 | https://github.com/scikit-learn/scikit-learn | github.com::repository_view | 4 | 3 |
| vmess | G1 | -1 | https://www.bing.com/search?q=beginner+guitar+chords | bing.com::search_results_view | 4 | 2 |
| vmess | G1 | -1 | https://www.bing.com/search?q=indoor+plant+care | bing.com::search_results_view | 4 | 3 |
| vmess | G1 | -1 | https://www.bing.com/search?q=network+traffic+analysis | bing.com::search_results_view | 4 | 3 |
| vmess | G1 | -1 | https://www.bing.com/search?q=solar+system+facts | bing.com::search_results_view | 4 | 3 |
| vmess | G1 | -1 | https://www.bing.com/search?q=sourdough+bread+recipe | bing.com::search_results_view | 4 | 4 |
| vmess | G1 | -1 | https://www.youtube.com/results?search_query=astronomy+documentary | youtube.com::search_results_view | 4 | 4 |
| vmess | G1 | -1 | https://www.youtube.com/results?search_query=bicycle+maintenance | youtube.com::search_results_view | 4 | 2 |
| vmess | G1 | -1 | https://www.youtube.com/results?search_query=bread+baking | youtube.com::search_results_view | 4 | 4 |
| vmess | G1 | -1 | https://www.youtube.com/results?search_query=piano+practice | youtube.com::search_results_view | 4 | 2 |
| vmess | G1 | -1 | https://www.youtube.com/results?search_query=watercolor+tutorial | youtube.com::search_results_view | 4 | 4 |
| vmess | G1 | -1 | youtube_video:R6MlUcmOul8 | youtube.com::video_playback | 4 | 4 |
| vmess | G1 | -1 | youtube_video:aircAruvnKk | youtube.com::video_playback | 4 | 3 |
| vmess | G1 | -1 | youtube_video:aqz-KE-bpKQ | youtube.com::video_playback | 4 | 4 |
| vmess | G1 | -1 | youtube_video:eRsGyueVLvQ | youtube.com::video_playback | 4 | 4 |
| vmess | G1 | -1 | youtube_video:sAWK0mgrMp4 | youtube.com::video_playback | 4 | 3 |
| vmess | G2 | 20261005 | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | developer.mozilla.org::document_view | 4 | 3 |
| vmess | G2 | 20261005 | https://developer.mozilla.org/en-US/docs/Web/HTTP | developer.mozilla.org::document_view | 4 | 2 |
| vmess | G2 | 20261005 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | developer.mozilla.org::document_view | 4 | 4 |
| vmess | G2 | 20261005 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | developer.mozilla.org::document_view | 4 | 2 |
| vmess | G2 | 20261005 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | developer.mozilla.org::document_view | 4 | 2 |
| vmess | G2 | 20261005 | https://en.wikipedia.org/wiki/Computer_network | wikipedia.org::article_view | 4 | 4 |
| vmess | G2 | 20261005 | https://en.wikipedia.org/wiki/Domain_Name_System | wikipedia.org::article_view | 4 | 2 |
| vmess | G2 | 20261005 | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | wikipedia.org::article_view | 4 | 1 |
| vmess | G2 | 20261005 | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | wikipedia.org::article_view | 4 | 2 |
| vmess | G2 | 20261005 | https://en.wikipedia.org/wiki/Transport_Layer_Security | wikipedia.org::article_view | 4 | 4 |
| vmess | G2 | 20261005 | https://github.com/RakuLomis/TrafficTracer | github.com::repository_view | 4 | 3 |
| vmess | G2 | 20261005 | https://github.com/numpy/numpy | github.com::repository_view | 4 | 3 |
| vmess | G2 | 20261005 | https://github.com/pallets/flask | github.com::repository_view | 4 | 4 |
| vmess | G2 | 20261005 | https://github.com/python/cpython | github.com::repository_view | 4 | 4 |
| vmess | G2 | 20261005 | https://github.com/scikit-learn/scikit-learn | github.com::repository_view | 4 | 3 |
| vmess | G2 | 20261005 | https://www.bing.com/search?q=beginner+guitar+chords | bing.com::search_results_view | 4 | 3 |
| vmess | G2 | 20261005 | https://www.bing.com/search?q=indoor+plant+care | bing.com::search_results_view | 4 | 3 |
| vmess | G2 | 20261005 | https://www.bing.com/search?q=network+traffic+analysis | bing.com::search_results_view | 4 | 2 |
| vmess | G2 | 20261005 | https://www.bing.com/search?q=solar+system+facts | bing.com::search_results_view | 4 | 2 |
| vmess | G2 | 20261005 | https://www.bing.com/search?q=sourdough+bread+recipe | bing.com::search_results_view | 4 | 4 |
| vmess | G2 | 20261005 | https://www.youtube.com/results?search_query=astronomy+documentary | youtube.com::search_results_view | 4 | 4 |
| vmess | G2 | 20261005 | https://www.youtube.com/results?search_query=bicycle+maintenance | youtube.com::search_results_view | 4 | 2 |
| vmess | G2 | 20261005 | https://www.youtube.com/results?search_query=bread+baking | youtube.com::search_results_view | 4 | 4 |
| vmess | G2 | 20261005 | https://www.youtube.com/results?search_query=piano+practice | youtube.com::search_results_view | 4 | 2 |
| vmess | G2 | 20261005 | https://www.youtube.com/results?search_query=watercolor+tutorial | youtube.com::search_results_view | 4 | 4 |
| vmess | G2 | 20261005 | youtube_video:R6MlUcmOul8 | youtube.com::video_playback | 4 | 3 |
| vmess | G2 | 20261005 | youtube_video:aircAruvnKk | youtube.com::video_playback | 4 | 3 |
| vmess | G2 | 20261005 | youtube_video:aqz-KE-bpKQ | youtube.com::video_playback | 4 | 4 |
| vmess | G2 | 20261005 | youtube_video:eRsGyueVLvQ | youtube.com::video_playback | 4 | 4 |
| vmess | G2 | 20261005 | youtube_video:sAWK0mgrMp4 | youtube.com::video_playback | 4 | 3 |
| vmess | G2 | 20261006 | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | developer.mozilla.org::document_view | 4 | 3 |
| vmess | G2 | 20261006 | https://developer.mozilla.org/en-US/docs/Web/HTTP | developer.mozilla.org::document_view | 4 | 1 |
| vmess | G2 | 20261006 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | developer.mozilla.org::document_view | 4 | 3 |
| vmess | G2 | 20261006 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | developer.mozilla.org::document_view | 4 | 2 |
| vmess | G2 | 20261006 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | developer.mozilla.org::document_view | 4 | 2 |
| vmess | G2 | 20261006 | https://en.wikipedia.org/wiki/Computer_network | wikipedia.org::article_view | 4 | 4 |
| vmess | G2 | 20261006 | https://en.wikipedia.org/wiki/Domain_Name_System | wikipedia.org::article_view | 4 | 2 |
| vmess | G2 | 20261006 | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | wikipedia.org::article_view | 4 | 1 |
| vmess | G2 | 20261006 | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | wikipedia.org::article_view | 4 | 3 |
| vmess | G2 | 20261006 | https://en.wikipedia.org/wiki/Transport_Layer_Security | wikipedia.org::article_view | 4 | 4 |
| vmess | G2 | 20261006 | https://github.com/RakuLomis/TrafficTracer | github.com::repository_view | 4 | 3 |
| vmess | G2 | 20261006 | https://github.com/numpy/numpy | github.com::repository_view | 4 | 3 |
| vmess | G2 | 20261006 | https://github.com/pallets/flask | github.com::repository_view | 4 | 3 |
| vmess | G2 | 20261006 | https://github.com/python/cpython | github.com::repository_view | 4 | 3 |
| vmess | G2 | 20261006 | https://github.com/scikit-learn/scikit-learn | github.com::repository_view | 4 | 3 |
| vmess | G2 | 20261006 | https://www.bing.com/search?q=beginner+guitar+chords | bing.com::search_results_view | 4 | 1 |
| vmess | G2 | 20261006 | https://www.bing.com/search?q=indoor+plant+care | bing.com::search_results_view | 4 | 3 |
| vmess | G2 | 20261006 | https://www.bing.com/search?q=network+traffic+analysis | bing.com::search_results_view | 4 | 2 |
| vmess | G2 | 20261006 | https://www.bing.com/search?q=solar+system+facts | bing.com::search_results_view | 4 | 3 |
| vmess | G2 | 20261006 | https://www.bing.com/search?q=sourdough+bread+recipe | bing.com::search_results_view | 4 | 4 |
| vmess | G2 | 20261006 | https://www.youtube.com/results?search_query=astronomy+documentary | youtube.com::search_results_view | 4 | 4 |
| vmess | G2 | 20261006 | https://www.youtube.com/results?search_query=bicycle+maintenance | youtube.com::search_results_view | 4 | 2 |
| vmess | G2 | 20261006 | https://www.youtube.com/results?search_query=bread+baking | youtube.com::search_results_view | 4 | 3 |
| vmess | G2 | 20261006 | https://www.youtube.com/results?search_query=piano+practice | youtube.com::search_results_view | 4 | 2 |
| vmess | G2 | 20261006 | https://www.youtube.com/results?search_query=watercolor+tutorial | youtube.com::search_results_view | 4 | 4 |
| vmess | G2 | 20261006 | youtube_video:R6MlUcmOul8 | youtube.com::video_playback | 4 | 3 |
| vmess | G2 | 20261006 | youtube_video:aircAruvnKk | youtube.com::video_playback | 4 | 3 |
| vmess | G2 | 20261006 | youtube_video:aqz-KE-bpKQ | youtube.com::video_playback | 4 | 4 |
| vmess | G2 | 20261006 | youtube_video:eRsGyueVLvQ | youtube.com::video_playback | 4 | 4 |
| vmess | G2 | 20261006 | youtube_video:sAWK0mgrMp4 | youtube.com::video_playback | 4 | 3 |
| vmess | G2 | 20261007 | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | developer.mozilla.org::document_view | 4 | 3 |
| vmess | G2 | 20261007 | https://developer.mozilla.org/en-US/docs/Web/HTTP | developer.mozilla.org::document_view | 4 | 1 |
| vmess | G2 | 20261007 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | developer.mozilla.org::document_view | 4 | 4 |
| vmess | G2 | 20261007 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | developer.mozilla.org::document_view | 4 | 2 |
| vmess | G2 | 20261007 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | developer.mozilla.org::document_view | 4 | 2 |
| vmess | G2 | 20261007 | https://en.wikipedia.org/wiki/Computer_network | wikipedia.org::article_view | 4 | 4 |
| vmess | G2 | 20261007 | https://en.wikipedia.org/wiki/Domain_Name_System | wikipedia.org::article_view | 4 | 2 |
| vmess | G2 | 20261007 | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | wikipedia.org::article_view | 4 | 0 |
| vmess | G2 | 20261007 | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | wikipedia.org::article_view | 4 | 3 |
| vmess | G2 | 20261007 | https://en.wikipedia.org/wiki/Transport_Layer_Security | wikipedia.org::article_view | 4 | 4 |
| vmess | G2 | 20261007 | https://github.com/RakuLomis/TrafficTracer | github.com::repository_view | 4 | 3 |
| vmess | G2 | 20261007 | https://github.com/numpy/numpy | github.com::repository_view | 4 | 3 |
| vmess | G2 | 20261007 | https://github.com/pallets/flask | github.com::repository_view | 4 | 3 |
| vmess | G2 | 20261007 | https://github.com/python/cpython | github.com::repository_view | 4 | 3 |
| vmess | G2 | 20261007 | https://github.com/scikit-learn/scikit-learn | github.com::repository_view | 4 | 3 |
| vmess | G2 | 20261007 | https://www.bing.com/search?q=beginner+guitar+chords | bing.com::search_results_view | 4 | 2 |
| vmess | G2 | 20261007 | https://www.bing.com/search?q=indoor+plant+care | bing.com::search_results_view | 4 | 3 |
| vmess | G2 | 20261007 | https://www.bing.com/search?q=network+traffic+analysis | bing.com::search_results_view | 4 | 2 |
| vmess | G2 | 20261007 | https://www.bing.com/search?q=solar+system+facts | bing.com::search_results_view | 4 | 4 |
| vmess | G2 | 20261007 | https://www.bing.com/search?q=sourdough+bread+recipe | bing.com::search_results_view | 4 | 4 |
| vmess | G2 | 20261007 | https://www.youtube.com/results?search_query=astronomy+documentary | youtube.com::search_results_view | 4 | 4 |
| vmess | G2 | 20261007 | https://www.youtube.com/results?search_query=bicycle+maintenance | youtube.com::search_results_view | 4 | 2 |
| vmess | G2 | 20261007 | https://www.youtube.com/results?search_query=bread+baking | youtube.com::search_results_view | 4 | 3 |
| vmess | G2 | 20261007 | https://www.youtube.com/results?search_query=piano+practice | youtube.com::search_results_view | 4 | 2 |
| vmess | G2 | 20261007 | https://www.youtube.com/results?search_query=watercolor+tutorial | youtube.com::search_results_view | 4 | 4 |
| vmess | G2 | 20261007 | youtube_video:R6MlUcmOul8 | youtube.com::video_playback | 4 | 3 |
| vmess | G2 | 20261007 | youtube_video:aircAruvnKk | youtube.com::video_playback | 4 | 3 |
| vmess | G2 | 20261007 | youtube_video:aqz-KE-bpKQ | youtube.com::video_playback | 4 | 4 |
| vmess | G2 | 20261007 | youtube_video:eRsGyueVLvQ | youtube.com::video_playback | 4 | 4 |
| vmess | G2 | 20261007 | youtube_video:sAWK0mgrMp4 | youtube.com::video_playback | 4 | 3 |
| vmess | G3 | -1 | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | developer.mozilla.org::document_view | 4 | 0 |
| vmess | G3 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP | developer.mozilla.org::document_view | 4 | 0 |
| vmess | G3 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | developer.mozilla.org::document_view | 4 | 0 |
| vmess | G3 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | developer.mozilla.org::document_view | 4 | 0 |
| vmess | G3 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | developer.mozilla.org::document_view | 4 | 0 |
| vmess | G3 | -1 | https://en.wikipedia.org/wiki/Computer_network | wikipedia.org::article_view | 4 | 0 |
| vmess | G3 | -1 | https://en.wikipedia.org/wiki/Domain_Name_System | wikipedia.org::article_view | 4 | 0 |
| vmess | G3 | -1 | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | wikipedia.org::article_view | 4 | 0 |
| vmess | G3 | -1 | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | wikipedia.org::article_view | 4 | 0 |
| vmess | G3 | -1 | https://en.wikipedia.org/wiki/Transport_Layer_Security | wikipedia.org::article_view | 4 | 0 |
| vmess | G3 | -1 | https://github.com/RakuLomis/TrafficTracer | github.com::repository_view | 4 | 1 |
| vmess | G3 | -1 | https://github.com/numpy/numpy | github.com::repository_view | 4 | 0 |
| vmess | G3 | -1 | https://github.com/pallets/flask | github.com::repository_view | 4 | 0 |
| vmess | G3 | -1 | https://github.com/python/cpython | github.com::repository_view | 4 | 0 |
| vmess | G3 | -1 | https://github.com/scikit-learn/scikit-learn | github.com::repository_view | 4 | 0 |
| vmess | G3 | -1 | https://www.bing.com/search?q=beginner+guitar+chords | bing.com::search_results_view | 4 | 1 |
| vmess | G3 | -1 | https://www.bing.com/search?q=indoor+plant+care | bing.com::search_results_view | 4 | 0 |
| vmess | G3 | -1 | https://www.bing.com/search?q=network+traffic+analysis | bing.com::search_results_view | 4 | 0 |
| vmess | G3 | -1 | https://www.bing.com/search?q=solar+system+facts | bing.com::search_results_view | 4 | 0 |
| vmess | G3 | -1 | https://www.bing.com/search?q=sourdough+bread+recipe | bing.com::search_results_view | 4 | 0 |
| vmess | G3 | -1 | https://www.youtube.com/results?search_query=astronomy+documentary | youtube.com::search_results_view | 4 | 4 |
| vmess | G3 | -1 | https://www.youtube.com/results?search_query=bicycle+maintenance | youtube.com::search_results_view | 4 | 4 |
| vmess | G3 | -1 | https://www.youtube.com/results?search_query=bread+baking | youtube.com::search_results_view | 4 | 4 |
| vmess | G3 | -1 | https://www.youtube.com/results?search_query=piano+practice | youtube.com::search_results_view | 4 | 4 |
| vmess | G3 | -1 | https://www.youtube.com/results?search_query=watercolor+tutorial | youtube.com::search_results_view | 4 | 4 |
| vmess | G3 | -1 | youtube_video:R6MlUcmOul8 | youtube.com::video_playback | 4 | 0 |
| vmess | G3 | -1 | youtube_video:aircAruvnKk | youtube.com::video_playback | 4 | 0 |
| vmess | G3 | -1 | youtube_video:aqz-KE-bpKQ | youtube.com::video_playback | 4 | 0 |
| vmess | G3 | -1 | youtube_video:eRsGyueVLvQ | youtube.com::video_playback | 4 | 0 |
| vmess | G3 | -1 | youtube_video:sAWK0mgrMp4 | youtube.com::video_playback | 4 | 0 |
| vmess | G4 | -1 | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | developer.mozilla.org::document_view | 4 | 1 |
| vmess | G4 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP | developer.mozilla.org::document_view | 4 | 1 |
| vmess | G4 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | developer.mozilla.org::document_view | 4 | 1 |
| vmess | G4 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | developer.mozilla.org::document_view | 4 | 2 |
| vmess | G4 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | developer.mozilla.org::document_view | 4 | 4 |
| vmess | G4 | -1 | https://en.wikipedia.org/wiki/Computer_network | wikipedia.org::article_view | 4 | 2 |
| vmess | G4 | -1 | https://en.wikipedia.org/wiki/Domain_Name_System | wikipedia.org::article_view | 4 | 0 |
| vmess | G4 | -1 | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | wikipedia.org::article_view | 4 | 2 |
| vmess | G4 | -1 | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | wikipedia.org::article_view | 4 | 0 |
| vmess | G4 | -1 | https://en.wikipedia.org/wiki/Transport_Layer_Security | wikipedia.org::article_view | 4 | 3 |
| vmess | G4 | -1 | https://github.com/RakuLomis/TrafficTracer | github.com::repository_view | 4 | 4 |
| vmess | G4 | -1 | https://github.com/numpy/numpy | github.com::repository_view | 4 | 3 |
| vmess | G4 | -1 | https://github.com/pallets/flask | github.com::repository_view | 4 | 3 |
| vmess | G4 | -1 | https://github.com/python/cpython | github.com::repository_view | 4 | 2 |
| vmess | G4 | -1 | https://github.com/scikit-learn/scikit-learn | github.com::repository_view | 4 | 3 |
| vmess | G4 | -1 | https://www.bing.com/search?q=beginner+guitar+chords | bing.com::search_results_view | 4 | 3 |
| vmess | G4 | -1 | https://www.bing.com/search?q=indoor+plant+care | bing.com::search_results_view | 4 | 0 |
| vmess | G4 | -1 | https://www.bing.com/search?q=network+traffic+analysis | bing.com::search_results_view | 4 | 1 |
| vmess | G4 | -1 | https://www.bing.com/search?q=solar+system+facts | bing.com::search_results_view | 4 | 4 |
| vmess | G4 | -1 | https://www.bing.com/search?q=sourdough+bread+recipe | bing.com::search_results_view | 4 | 1 |
| vmess | G4 | -1 | https://www.youtube.com/results?search_query=astronomy+documentary | youtube.com::search_results_view | 4 | 4 |
| vmess | G4 | -1 | https://www.youtube.com/results?search_query=bicycle+maintenance | youtube.com::search_results_view | 4 | 3 |
| vmess | G4 | -1 | https://www.youtube.com/results?search_query=bread+baking | youtube.com::search_results_view | 4 | 3 |
| vmess | G4 | -1 | https://www.youtube.com/results?search_query=piano+practice | youtube.com::search_results_view | 4 | 2 |
| vmess | G4 | -1 | https://www.youtube.com/results?search_query=watercolor+tutorial | youtube.com::search_results_view | 4 | 3 |
| vmess | G4 | -1 | youtube_video:R6MlUcmOul8 | youtube.com::video_playback | 4 | 3 |
| vmess | G4 | -1 | youtube_video:aircAruvnKk | youtube.com::video_playback | 4 | 3 |
| vmess | G4 | -1 | youtube_video:aqz-KE-bpKQ | youtube.com::video_playback | 4 | 3 |
| vmess | G4 | -1 | youtube_video:eRsGyueVLvQ | youtube.com::video_playback | 4 | 3 |
| vmess | G4 | -1 | youtube_video:sAWK0mgrMp4 | youtube.com::video_playback | 4 | 1 |
| vmess | G5 | -1 | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | developer.mozilla.org::document_view | 4 | 0 |
| vmess | G5 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP | developer.mozilla.org::document_view | 4 | 0 |
| vmess | G5 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | developer.mozilla.org::document_view | 4 | 0 |
| vmess | G5 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | developer.mozilla.org::document_view | 4 | 0 |
| vmess | G5 | -1 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | developer.mozilla.org::document_view | 4 | 0 |
| vmess | G5 | -1 | https://en.wikipedia.org/wiki/Computer_network | wikipedia.org::article_view | 4 | 1 |
| vmess | G5 | -1 | https://en.wikipedia.org/wiki/Domain_Name_System | wikipedia.org::article_view | 4 | 3 |
| vmess | G5 | -1 | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | wikipedia.org::article_view | 4 | 3 |
| vmess | G5 | -1 | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | wikipedia.org::article_view | 4 | 2 |
| vmess | G5 | -1 | https://en.wikipedia.org/wiki/Transport_Layer_Security | wikipedia.org::article_view | 4 | 4 |
| vmess | G5 | -1 | https://github.com/RakuLomis/TrafficTracer | github.com::repository_view | 4 | 2 |
| vmess | G5 | -1 | https://github.com/numpy/numpy | github.com::repository_view | 4 | 0 |
| vmess | G5 | -1 | https://github.com/pallets/flask | github.com::repository_view | 4 | 1 |
| vmess | G5 | -1 | https://github.com/python/cpython | github.com::repository_view | 4 | 0 |
| vmess | G5 | -1 | https://github.com/scikit-learn/scikit-learn | github.com::repository_view | 4 | 0 |
| vmess | G5 | -1 | https://www.bing.com/search?q=beginner+guitar+chords | bing.com::search_results_view | 4 | 0 |
| vmess | G5 | -1 | https://www.bing.com/search?q=indoor+plant+care | bing.com::search_results_view | 4 | 0 |
| vmess | G5 | -1 | https://www.bing.com/search?q=network+traffic+analysis | bing.com::search_results_view | 4 | 0 |
| vmess | G5 | -1 | https://www.bing.com/search?q=solar+system+facts | bing.com::search_results_view | 4 | 0 |
| vmess | G5 | -1 | https://www.bing.com/search?q=sourdough+bread+recipe | bing.com::search_results_view | 4 | 0 |
| vmess | G5 | -1 | https://www.youtube.com/results?search_query=astronomy+documentary | youtube.com::search_results_view | 4 | 4 |
| vmess | G5 | -1 | https://www.youtube.com/results?search_query=bicycle+maintenance | youtube.com::search_results_view | 4 | 3 |
| vmess | G5 | -1 | https://www.youtube.com/results?search_query=bread+baking | youtube.com::search_results_view | 4 | 2 |
| vmess | G5 | -1 | https://www.youtube.com/results?search_query=piano+practice | youtube.com::search_results_view | 4 | 2 |
| vmess | G5 | -1 | https://www.youtube.com/results?search_query=watercolor+tutorial | youtube.com::search_results_view | 4 | 3 |
| vmess | G5 | -1 | youtube_video:R6MlUcmOul8 | youtube.com::video_playback | 4 | 4 |
| vmess | G5 | -1 | youtube_video:aircAruvnKk | youtube.com::video_playback | 4 | 4 |
| vmess | G5 | -1 | youtube_video:aqz-KE-bpKQ | youtube.com::video_playback | 4 | 3 |
| vmess | G5 | -1 | youtube_video:eRsGyueVLvQ | youtube.com::video_playback | 4 | 4 |
| vmess | G5 | -1 | youtube_video:sAWK0mgrMp4 | youtube.com::video_playback | 4 | 3 |



## 12 可追溯的分类贡献



每访问G4前两名业务分数差分解为w_j h_j(b) log(Q_first/Q_second)。全部480访问贡献求和通过分数差重放。各部署各业务的展示访问按稳定匿名ID预定，不挑成功个案。



![固定个案贡献](../../outputs/drift-kernel-business-20261005/run-01/figures/fixed-example-contributions.png)



这些贡献解释模型计算，不为每条CDN连接赋予业务语义，也不将某箱解释为握手或精确协议头。



## 13 输入权限与可复现审计



| check | value |
| --- | --- |
| CUDA_fit_and_predict | 是 |
| external_score_noninterference_checks | 20 |
| forbidden_pre_column_rejections | 20 |
| given_dual_side_qualified_connections_and_visit_ranges | 是 |
| human_external_blind_validation | 否 |
| main_pairs | 23566 |
| max_histogram_replay_error | 0.000000 |
| max_probability_replay_error | 0.000000 |
| new_LR_models | 20 |
| new_MLP_models | 60 |
| no_new_SSL_or_kernel_fitting | 是 |
| old_inputs_and_results_unchanged | 是 |
| passed | 是 |
| query_pre_or_label_opened | 否 |
| raw_PCAP_reads | 0 |
| registered_entity_cross_fold | 0 |
| reused_kernel_files | 200 |
| unit_tests | 20 |
| universal_TCP_epoch_proof | 否 |
| visits | 480 |



可信包装曾读取双侧资格缓存；训练分包只提供训练范围，推理仅读取query-post-hist及冻结模型。测试pre、标签、content ID、地址/SNI/端口不进入预测接口。已知部署只作核与基线路由，所有方法权限相同。文件角色台账不是OS安全沙箱。



核频数、组级乘积和平滑已对20部署折、200核重新重放。登记实体不跨内容fold；仍保留历史不完整TCP epoch范围，不夸大为任意未观测会话的证明。全部模型重载后3840行概率及类别重放通过。



## 14 结论范围与停止决定



本轮把已测得的代理条件关系直接接入访问级业务评分，实际检验了源分布、核和出口观测的整条链。结论以第5和第6节的实际增量与家族区间为准，不将统计预测成功自动升级成分类成功。



现有数据仍是已见配置、已知路由、给定父访问范围、离线合格连接、未见内容任务。未检验未知部署、跨日期、外部DIRECT、少目标post/标签、AnyTLS/Hy2同粒度模型或在线无索引攻击。



候选在这里冻结；未修改alpha、温度、权重、业务、分箱或网络预算。后续新方法需另行登记与用户确认，不以G4必须胜出为理由扩大搜索。



## 15 文件与复现入口



代码：eval/drift_kernel_business。输出：outputs/drift-kernel-business-20261005/run-01。运行顺序及角色说明见该代码目录README.md。机器契约、原源SHA、包SHA、模型完成记录、预测封存和verification.json共同构成复现依据。



原实施计划在本地plan目录；本报告不替换其预登记内容，也不覆盖旧protocol-probability-drift正式报告。
