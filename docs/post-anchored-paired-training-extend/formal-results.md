# Extend post 单侧任务感知配对训练完整结果

日期：2026年10月4日。本报告覆盖固定J0至J7、五折、三seed的训练与业务评分，以及用户批准的15个J0数值修复重拟合。旧E1与第一次失败版本保留，没有重做探针、检索、追加权重或启动E2。

唯一主候选J4的部署等权macro-F1为0.778322；预定六项比较中0项获得家族校正后正向区间。下面逐项解释，而不是按最好点估计更换主方法。

## 数据观测和划分

固定600访问、30全局内容、六业务、五已见部署SS/VLESS/Trojan/VMess/AnyTLS，每内容每部署四次重复1至4。沿用五折全局内容留出，训练480、测试120；同内容全部部署、重复、两侧与内部连接整体同折。不是0914/旧0916/64URL任务。

输入只有W_up/W_down/P_up/P_down/R_up/R_down。W为窗口正传输载荷字节含重传，P为正载荷事件，R为窗口方向段，不是stream FR、TCP去重新字节段或记录时间FR。MAC、IP、端口、SNI、domain字符串、协议onehot、内容和重复均不是网络数值输入。标签、内容与部署元数据只服务训练授权、采样、划分及评分。

- bing.com::search_results_view
- developer.mozilla.org::document_view
- github.com::repository_view
- wikipedia.org::article_view
- youtube.com::search_results_view
- youtube.com::video_playback

资格继续沿用P2/P3物理身份注册，并保留五例未见SYN与历史P2预检限制；复用审核不是全量PCAP重新验证，更不是绝对无flow泄漏的数学证明。本批Hy2存在登记carrier跨内容/跨折及未映射访问，未进入此共同分类队列。

## 方法和任务权限

E为6→64→32，隐藏ReLU、最终线性；H为32→32→6，隐藏ReLU。E有2528参数，H有1254，部署共3782。训练条件A为零初始化无偏置6→32，另192参数；推理删除。pre与post分别采用训练侧log1p及均值标准差。条件是冻结phi(decoded raw_center)−phi(pre)经训练尺度处理，八个pre辅助统计只参与条件预测。300中心、7200条件行复用18训练内容/6查询内容交叉拟合，不使用真实query post作条件。

两分支共享E/H，post logits为H(E(post))，辅助logits为H(E(pre)+A m)。目标为0.5 post CE＋0.5 aux CE＋0.5 T² KL(stopgrad(aux softmax/T) ∥ post softmax/T)＋5e−5权重平方和，T=2，bias不惩罚。J0/J1/J6关闭KL。KL的直接梯度只经post路径；共享参数之后仍更新辅助分支，不是独立冻结教师。新方案显式使用业务标签，是任务感知训练，不是无标签SSL，也不把中心交叉拟合冒充业务OOF教师。

| 臂   | 辅助分支                   | 约束                  | 用途           |
|:-----|:---------------------------|:----------------------|:---------------|
| J0   | post单CE，原复制CE代数化简 | 无                    | 充分post监督   |
| J1   | pre业务CE，无条件          | 无                    | 额外pre监督    |
| J2   | pre业务CE，无条件          | 真配决策KL            | 无条件任务配对 |
| J3   | pre业务CE，D1_pair         | 真配决策KL            | 通用中心       |
| J4   | pre业务CE，D2_pair         | 真配决策KL            | 唯一主候选     |
| J5   | 匿名组pre业务CE，D2_group  | 四pre平均概率到组post | 较粗对应       |
| J6   | pre业务CE，D2_pair         | 无                    | 条件双侧CE     |
| J7   | masked post业务CE          | masked到clean post KL | 普通post一致性 |

J5组是同内容同部署的四次访问；两侧独立排序，无共同session/repetition。平均概率而非logits，四pre各编码一次，不把16组合当独立访问。J4−J5比较整条精确对应管线，包含中心和决策目标的关系，不能独立定位末端身份的因果贡献。J7只遮一个标准化数值坐标为0；这是学习扰动，不是合法代理流量。

## 优化配置和实际预算

三seed为20260918/19/20。各模型固定2000步；第1000步保留权重、重置Adam，重放同一1000步监督采样。每批120访问，各部署各业务一个内容的四重复。Adam lr0.001、betas0.9/0.999、eps1e−8、foreach=False、optimizer weight_decay=0；显式L2如前。无早停、checkpoint选择、BN、dropout、AMP、TF32、温度或权重搜索。

Pytorch312，PyTorch2.5.1/CUDA12.4，RTX4060Ti。全部训练、数值条件核验、编码与推理CUDA，网络float32，条件核验float64；元数据与bootstrap使用CPU。

第一次120正式模型加批准的15个J0修复，共实际执行135个2000步模型；最终评分使用120，原15个J0仅保留为失败实现记录。另8个20步工程烟测，不进入初始化。并行参数batch模型互不共享权重或优化器状态，不构成集成。

第一次拟合加修复的合计训练计时为135.646秒，这是各折记录之和，不是完整流水线墙钟时间。

| 臂       | 训练资源               |   更新步 |   每访问post编码曝光 |   每访问pre编码曝光 | 说明                       |
|:---------|:-----------------------|---------:|---------------------:|--------------------:|:---------------------------|
| J0       | post＋标签             |     2000 |                  500 |                   0 | 复制CE代数化简，单post前向 |
| J1/J2    | pre/post＋既有标签     |     2000 |                  500 |                 500 | 无条件                     |
| J3/J4/J6 | 同一双侧资源＋合法条件 |     2000 |                  500 |                 500 | 条件由训练侧预测           |
| J5       | 匿名组双侧资源＋组条件 |     2000 |                  500 |                 500 | 无精确身份                 |
| J7       | post＋标签             |     2000 |                 1000 |                   0 | clean和masked两次post前向  |

## 数值修复与不可改写的失败记录

第一次J0对旧B0L的最大概率差为0.30322763323783875，1800条中19个决策不同；评分在门前停止。训练侧15组输入、初始化、采样和缩放器一致，初始重复CE与单CE梯度存在1.862645149230957e−9差异，后续损失轨迹偏离；第一实现的继续布局为24模型，旧B0L为3。该审计没有单独分解两个数值因素的贡献。

用户批准追加15个J0之后，使用单CE旧求值路径，第一阶段24位置布局仅更新1/9/17三个位置，其他21个位置梯度为零、权重不变，属于计算填充而非新增学习器；第二阶段三个模型继续。修复15个模型前1000步损失与最终E/H哈希均精确复现旧B0L。训练验证先于业务评分，未按正确率选择旧/新模型。

修复预测与旧B0L的最大概率差为0，决策不同为0；120模型不同推理batch最大概率差2.11596488953e-06，决策全部一致。1e−5门限未放宽。

## 主要业务成绩

| arm   |       F1 |   min_seed |   max_seed |   worst_F1 |   CE_bits |    Brier |
|:------|---------:|-----------:|-----------:|-----------:|----------:|---------:|
| J0    | 0.766975 |   0.764252 |   0.769993 |   0.727432 |  1.619890 | 0.348138 |
| J1    | 0.762954 |   0.756650 |   0.774631 |   0.723590 |  1.322063 | 0.336784 |
| J2    | 0.771037 |   0.766316 |   0.778969 |   0.741142 |  1.228686 | 0.326405 |
| J3    | 0.771688 |   0.762234 |   0.786301 |   0.745181 |  1.340093 | 0.325920 |
| J4    | 0.778322 |   0.774655 |   0.783734 |   0.743444 |  1.277361 | 0.325533 |
| J5    | 0.774419 |   0.768330 |   0.781702 |   0.727912 |  0.968460 | 0.316033 |
| J6    | 0.762365 |   0.756856 |   0.769210 |   0.715690 |  1.409430 | 0.337286 |
| J7    | 0.766484 |   0.750307 |   0.783009 |   0.737310 |  0.925150 | 0.326828 |

F1先逐seed、逐部署从完整六类OOF计算，再部署与seed等权平均；min/max seed为部署等权的逐seed范围；worst F1是每seed最差部署F1的均值。不先平均概率，不以混合访问总F1代替部署等权。CE为bits，Brier为六类概率平方误差和。

## 六项主要比较与解释性比较

| contrast   | primary   |     delta |     low95 |   high95 |   adjusted_low |   adjusted_high |
|:-----------|:----------|----------:|----------:|---------:|---------------:|----------------:|
| J4-J0      | True      |  0.011347 | -0.004641 | 0.027813 |      -0.009332 |        0.033320 |
| J4-J7      | True      |  0.011839 | -0.011063 | 0.036001 |      -0.018967 |        0.044439 |
| J4-J6      | True      |  0.015957 |  0.002850 | 0.029135 |      -0.001510 |        0.033483 |
| J4-J2      | True      |  0.007285 | -0.003079 | 0.017805 |      -0.006424 |        0.021106 |
| J4-J3      | True      |  0.006634 | -0.003717 | 0.017068 |      -0.006973 |        0.020917 |
| J4-J5      | True      |  0.003903 | -0.008468 | 0.015299 |      -0.012436 |        0.018490 |
| J4-J1      | False     |  0.015368 | -0.000569 | 0.031399 |     nan        |      nan        |
| J2-J1      | False     |  0.008083 | -0.007100 | 0.023409 |     nan        |      nan        |
| J6-J1      | False     | -0.000589 | -0.011372 | 0.010233 |     nan        |      nan        |
| J7-J0      | False     | -0.000491 | -0.023566 | 0.021792 |     nan        |      nan        |

主要家族固定J4−J0/J7/J6/J2/J3/J5。10000次业务分层内容簇bootstrap，seed20260928，同内容所有部署、重复、seed和臂同步重采样。普通95%与六项Bonferroni分位0.05/12及1−0.05/12并报。固定模型区间不涵盖外部验证、独立重训或历史选择。三seed与四重复不是更多独立内容。

| 问题                       | 比较   | 判断                               |
|:---------------------------|:-------|:-----------------------------------|
| 相对充分post监督           | J4-J0  | 正向增量未建立；区间跨零不等于等效 |
| 相对普通post任务一致性     | J4-J7  | 正向增量未建立；区间跨零不等于等效 |
| 显式transfer相对条件双侧CE | J4-J6  | 正向增量未建立；区间跨零不等于等效 |
| 机制条件相对无条件任务配对 | J4-J2  | 正向增量未建立；区间跨零不等于等效 |
| 机制中心相对通用中心       | J4-J3  | 正向增量未建立；区间跨零不等于等效 |
| 精确对应管线相对匿名组管线 | J4-J5  | 正向增量未建立；区间跨零不等于等效 |

## 逐部署与逐seed

| protocol    |       J0 |       J1 |       J2 |       J3 |       J4 |       J5 |       J6 |       J7 |
|:------------|---------:|---------:|---------:|---------:|---------:|---------:|---------:|---------:|
| anytls      | 0.796943 | 0.811982 | 0.818809 | 0.828407 | 0.837481 | 0.821305 | 0.824829 | 0.795405 |
| shadowsocks | 0.792916 | 0.786228 | 0.778744 | 0.775514 | 0.775902 | 0.785703 | 0.779712 | 0.760038 |
| trojan      | 0.727432 | 0.738118 | 0.753455 | 0.747601 | 0.764652 | 0.775864 | 0.740378 | 0.737310 |
| vless       | 0.757051 | 0.730926 | 0.757889 | 0.748509 | 0.747594 | 0.737980 | 0.727531 | 0.772057 |
| vmess       | 0.760533 | 0.747515 | 0.746288 | 0.758407 | 0.765983 | 0.751245 | 0.739375 | 0.767608 |

| arm   |   20260918 |   20260919 |   20260920 |
|:------|-----------:|-----------:|-----------:|
| J0    |   0.766680 |   0.769993 |   0.764252 |
| J1    |   0.774631 |   0.756650 |   0.757581 |
| J2    |   0.778969 |   0.766316 |   0.767827 |
| J3    |   0.786301 |   0.762234 |   0.766529 |
| J4    |   0.783734 |   0.776578 |   0.774655 |
| J5    |   0.781702 |   0.768330 |   0.773226 |
| J6    |   0.769210 |   0.756856 |   0.761028 |
| J7    |   0.766135 |   0.783009 |   0.750307 |

### 全部部署逐seed指标

| arm   |     seed | protocol    |       F1 |   accuracy |   CE_bits |    Brier |
|:------|---------:|:------------|---------:|-----------:|----------:|---------:|
| J0    | 20260918 | anytls      | 0.787550 |   0.800000 |  1.289419 | 0.295800 |
| J0    | 20260918 | shadowsocks | 0.791167 |   0.791667 |  1.600702 | 0.317673 |
| J0    | 20260918 | trojan      | 0.728382 |   0.725000 |  1.835439 | 0.388067 |
| J0    | 20260918 | vless       | 0.766000 |   0.766667 |  1.928434 | 0.368865 |
| J0    | 20260918 | vmess       | 0.760300 |   0.766667 |  1.339354 | 0.354699 |
| J0    | 20260919 | anytls      | 0.819334 |   0.825000 |  1.218210 | 0.282798 |
| J0    | 20260919 | shadowsocks | 0.788830 |   0.791667 |  1.695573 | 0.336204 |
| J0    | 20260919 | trojan      | 0.727442 |   0.725000 |  1.567087 | 0.377313 |
| J0    | 20260919 | vless       | 0.753064 |   0.750000 |  1.990874 | 0.375249 |
| J0    | 20260919 | vmess       | 0.761295 |   0.766667 |  1.476617 | 0.357684 |
| J0    | 20260920 | anytls      | 0.783944 |   0.800000 |  1.427786 | 0.310774 |
| J0    | 20260920 | shadowsocks | 0.798750 |   0.800000 |  1.788004 | 0.320553 |
| J0    | 20260920 | trojan      | 0.726472 |   0.725000 |  1.898701 | 0.408160 |
| J0    | 20260920 | vless       | 0.752090 |   0.750000 |  1.964962 | 0.389433 |
| J0    | 20260920 | vmess       | 0.760005 |   0.766667 |  1.277181 | 0.338790 |
| J1    | 20260918 | anytls      | 0.828656 |   0.833333 |  0.738179 | 0.237957 |
| J1    | 20260918 | shadowsocks | 0.807609 |   0.808333 |  1.318877 | 0.301298 |
| J1    | 20260918 | trojan      | 0.740023 |   0.741667 |  1.749091 | 0.359267 |
| J1    | 20260918 | vless       | 0.719166 |   0.716667 |  1.764013 | 0.387972 |
| J1    | 20260918 | vmess       | 0.777698 |   0.783333 |  1.050908 | 0.328082 |
| J1    | 20260919 | anytls      | 0.811374 |   0.816667 |  0.969991 | 0.274459 |
| J1    | 20260919 | shadowsocks | 0.762695 |   0.766667 |  1.560247 | 0.365213 |
| J1    | 20260919 | trojan      | 0.748131 |   0.750000 |  1.327431 | 0.354178 |
| J1    | 20260919 | vless       | 0.735646 |   0.733333 |  1.506086 | 0.378007 |
| J1    | 20260919 | vmess       | 0.725406 |   0.733333 |  1.181004 | 0.394414 |
| J1    | 20260920 | anytls      | 0.795917 |   0.808333 |  0.886443 | 0.264766 |
| J1    | 20260920 | shadowsocks | 0.788379 |   0.791667 |  1.439698 | 0.317420 |
| J1    | 20260920 | trojan      | 0.726199 |   0.725000 |  1.711255 | 0.356368 |
| J1    | 20260920 | vless       | 0.737967 |   0.733333 |  1.500439 | 0.383482 |
| J1    | 20260920 | vmess       | 0.739441 |   0.750000 |  1.127277 | 0.348875 |
| J2    | 20260918 | anytls      | 0.820451 |   0.825000 |  0.670728 | 0.228528 |
| J2    | 20260918 | shadowsocks | 0.784988 |   0.783333 |  1.525509 | 0.313361 |
| J2    | 20260918 | trojan      | 0.766172 |   0.766667 |  1.370048 | 0.338316 |
| J2    | 20260918 | vless       | 0.763243 |   0.758333 |  1.444116 | 0.366098 |
| J2    | 20260918 | vmess       | 0.759991 |   0.766667 |  0.995558 | 0.326933 |
| J2    | 20260919 | anytls      | 0.822262 |   0.825000 |  0.708885 | 0.246740 |
| J2    | 20260919 | shadowsocks | 0.775442 |   0.775000 |  1.518759 | 0.351814 |
| J2    | 20260919 | trojan      | 0.758574 |   0.758333 |  1.262899 | 0.346972 |
| J2    | 20260919 | vless       | 0.747487 |   0.741667 |  1.541969 | 0.361207 |
| J2    | 20260919 | vmess       | 0.727816 |   0.733333 |  1.146973 | 0.357371 |
| J2    | 20260920 | anytls      | 0.813716 |   0.816667 |  1.002313 | 0.271979 |
| J2    | 20260920 | shadowsocks | 0.775803 |   0.775000 |  1.465310 | 0.346711 |
| J2    | 20260920 | trojan      | 0.735618 |   0.733333 |  1.257629 | 0.358472 |
| J2    | 20260920 | vless       | 0.762937 |   0.758333 |  1.389939 | 0.346021 |
| J2    | 20260920 | vmess       | 0.751058 |   0.758333 |  1.129657 | 0.335560 |
| J3    | 20260918 | anytls      | 0.872507 |   0.875000 |  0.647457 | 0.211487 |
| J3    | 20260918 | shadowsocks | 0.792110 |   0.791667 |  1.794077 | 0.333334 |
| J3    | 20260918 | trojan      | 0.750727 |   0.750000 |  1.532856 | 0.334970 |
| J3    | 20260918 | vless       | 0.747199 |   0.741667 |  1.620938 | 0.362349 |
| J3    | 20260918 | vmess       | 0.768962 |   0.775000 |  1.185310 | 0.339365 |
| J3    | 20260919 | anytls      | 0.820805 |   0.825000 |  0.768245 | 0.241625 |
| J3    | 20260919 | shadowsocks | 0.775088 |   0.775000 |  1.571396 | 0.346394 |
| J3    | 20260919 | trojan      | 0.740845 |   0.741667 |  1.555791 | 0.346849 |
| J3    | 20260919 | vless       | 0.737318 |   0.733333 |  1.537253 | 0.365784 |
| J3    | 20260919 | vmess       | 0.737112 |   0.741667 |  1.231139 | 0.350528 |
| J3    | 20260920 | anytls      | 0.791910 |   0.800000 |  0.761124 | 0.250421 |
| J3    | 20260920 | shadowsocks | 0.759344 |   0.758333 |  1.667897 | 0.363067 |
| J3    | 20260920 | trojan      | 0.751231 |   0.750000 |  1.638490 | 0.347255 |
| J3    | 20260920 | vless       | 0.761011 |   0.758333 |  1.486021 | 0.352357 |
| J3    | 20260920 | vmess       | 0.769148 |   0.775000 |  1.103394 | 0.343020 |
| J4    | 20260918 | anytls      | 0.855236 |   0.858333 |  0.736484 | 0.235817 |
| J4    | 20260918 | shadowsocks | 0.782350 |   0.783333 |  1.542712 | 0.343357 |
| J4    | 20260918 | trojan      | 0.759226 |   0.758333 |  1.461358 | 0.341045 |
| J4    | 20260918 | vless       | 0.743708 |   0.741667 |  1.577343 | 0.369593 |
| J4    | 20260918 | vmess       | 0.778149 |   0.783333 |  1.167104 | 0.328532 |
| J4    | 20260919 | anytls      | 0.840433 |   0.841667 |  0.735706 | 0.246724 |
| J4    | 20260919 | shadowsocks | 0.772002 |   0.775000 |  1.420337 | 0.340214 |
| J4    | 20260919 | trojan      | 0.776072 |   0.775000 |  1.426467 | 0.340647 |
| J4    | 20260919 | vless       | 0.753415 |   0.750000 |  1.416222 | 0.355874 |
| J4    | 20260919 | vmess       | 0.740967 |   0.750000 |  1.117730 | 0.351371 |
| J4    | 20260920 | anytls      | 0.816773 |   0.825000 |  0.961633 | 0.252333 |
| J4    | 20260920 | shadowsocks | 0.773354 |   0.775000 |  1.475296 | 0.334923 |
| J4    | 20260920 | trojan      | 0.758658 |   0.758333 |  1.462434 | 0.351516 |
| J4    | 20260920 | vless       | 0.745658 |   0.741667 |  1.475061 | 0.347253 |
| J4    | 20260920 | vmess       | 0.778834 |   0.783333 |  1.184527 | 0.343796 |
| J5    | 20260918 | anytls      | 0.830430 |   0.833333 |  0.725975 | 0.255609 |
| J5    | 20260918 | shadowsocks | 0.792498 |   0.791667 |  0.850848 | 0.296145 |
| J5    | 20260918 | trojan      | 0.784079 |   0.783333 |  1.081364 | 0.331342 |
| J5    | 20260918 | vless       | 0.715751 |   0.716667 |  1.171917 | 0.349499 |
| J5    | 20260918 | vmess       | 0.785750 |   0.791667 |  0.860328 | 0.321434 |
| J5    | 20260919 | anytls      | 0.836592 |   0.841667 |  0.726572 | 0.241356 |
| J5    | 20260919 | shadowsocks | 0.790136 |   0.791667 |  0.890043 | 0.318956 |
| J5    | 20260919 | trojan      | 0.759936 |   0.758333 |  1.169385 | 0.349047 |
| J5    | 20260919 | vless       | 0.737073 |   0.733333 |  1.031394 | 0.335324 |
| J5    | 20260919 | vmess       | 0.717914 |   0.725000 |  1.000104 | 0.359570 |
| J5    | 20260920 | anytls      | 0.796892 |   0.800000 |  0.878308 | 0.277341 |
| J5    | 20260920 | shadowsocks | 0.774476 |   0.775000 |  1.008628 | 0.328232 |
| J5    | 20260920 | trojan      | 0.783577 |   0.783333 |  1.121305 | 0.316416 |
| J5    | 20260920 | vless       | 0.761116 |   0.758333 |  1.155668 | 0.335903 |
| J5    | 20260920 | vmess       | 0.750070 |   0.758333 |  0.855067 | 0.324319 |
| J6    | 20260918 | anytls      | 0.827333 |   0.833333 |  0.818679 | 0.238358 |
| J6    | 20260918 | shadowsocks | 0.805352 |   0.808333 |  1.528630 | 0.309225 |
| J6    | 20260918 | trojan      | 0.758681 |   0.758333 |  1.637961 | 0.329093 |
| J6    | 20260918 | vless       | 0.693979 |   0.691667 |  1.857849 | 0.393828 |
| J6    | 20260918 | vmess       | 0.760704 |   0.766667 |  1.168575 | 0.335947 |
| J6    | 20260919 | anytls      | 0.830016 |   0.833333 |  0.846577 | 0.264793 |
| J6    | 20260919 | shadowsocks | 0.762892 |   0.766667 |  1.540493 | 0.335401 |
| J6    | 20260919 | trojan      | 0.725109 |   0.725000 |  1.517979 | 0.379620 |
| J6    | 20260919 | vless       | 0.750517 |   0.750000 |  1.674938 | 0.371421 |
| J6    | 20260919 | vmess       | 0.715749 |   0.725000 |  1.503453 | 0.409747 |
| J6    | 20260920 | anytls      | 0.817137 |   0.825000 |  0.979662 | 0.271333 |
| J6    | 20260920 | shadowsocks | 0.770893 |   0.775000 |  1.301648 | 0.323119 |
| J6    | 20260920 | trojan      | 0.737343 |   0.733333 |  1.906823 | 0.379515 |
| J6    | 20260920 | vless       | 0.738097 |   0.733333 |  1.619283 | 0.369049 |
| J6    | 20260920 | vmess       | 0.741671 |   0.750000 |  1.238898 | 0.348836 |
| J7    | 20260918 | anytls      | 0.812727 |   0.816667 |  0.734045 | 0.262070 |
| J7    | 20260918 | shadowsocks | 0.757678 |   0.766667 |  1.006103 | 0.348173 |
| J7    | 20260918 | trojan      | 0.727900 |   0.725000 |  1.084334 | 0.368759 |
| J7    | 20260918 | vless       | 0.764411 |   0.766667 |  0.923966 | 0.324791 |
| J7    | 20260918 | vmess       | 0.767959 |   0.775000 |  0.823139 | 0.304348 |
| J7    | 20260919 | anytls      | 0.819809 |   0.825000 |  0.740430 | 0.264467 |
| J7    | 20260919 | shadowsocks | 0.777233 |   0.783333 |  1.050498 | 0.348967 |
| J7    | 20260919 | trojan      | 0.751155 |   0.750000 |  1.018013 | 0.356590 |
| J7    | 20260919 | vless       | 0.791268 |   0.791667 |  0.919991 | 0.317691 |
| J7    | 20260919 | vmess       | 0.775579 |   0.783333 |  0.847317 | 0.311830 |
| J7    | 20260920 | anytls      | 0.753678 |   0.766667 |  0.818627 | 0.301695 |
| J7    | 20260920 | shadowsocks | 0.745202 |   0.750000 |  1.056611 | 0.367304 |
| J7    | 20260920 | trojan      | 0.732874 |   0.733333 |  1.088864 | 0.370965 |
| J7    | 20260920 | vless       | 0.760492 |   0.758333 |  0.923217 | 0.341536 |
| J7    | 20260920 | vmess       | 0.759287 |   0.766667 |  0.842096 | 0.313231 |

## 逐业务指标

| arm   | class                                |   precision |   recall |       F1 |
|:------|:-------------------------------------|------------:|---------:|---------:|
| J0    | bing.com::search_results_view        |    0.767015 | 0.706667 | 0.733010 |
| J0    | developer.mozilla.org::document_view |    0.600046 | 0.700000 | 0.644397 |
| J0    | github.com::repository_view          |    0.859751 | 0.870000 | 0.860132 |
| J0    | wikipedia.org::article_view          |    0.654454 | 0.513333 | 0.562186 |
| J0    | youtube.com::search_results_view     |    0.863719 | 0.903333 | 0.882197 |
| J0    | youtube.com::video_playback          |    0.916823 | 0.926667 | 0.919928 |
| J1    | bing.com::search_results_view        |    0.803546 | 0.716667 | 0.755592 |
| J1    | developer.mozilla.org::document_view |    0.581578 | 0.610000 | 0.591935 |
| J1    | github.com::repository_view          |    0.810019 | 0.890000 | 0.843912 |
| J1    | wikipedia.org::article_view          |    0.603899 | 0.520000 | 0.547471 |
| J1    | youtube.com::search_results_view     |    0.892963 | 0.910000 | 0.899532 |
| J1    | youtube.com::video_playback          |    0.930899 | 0.950000 | 0.939281 |
| J2    | bing.com::search_results_view        |    0.807320 | 0.743333 | 0.771896 |
| J2    | developer.mozilla.org::document_view |    0.577745 | 0.636667 | 0.603160 |
| J2    | github.com::repository_view          |    0.873350 | 0.856667 | 0.859836 |
| J2    | wikipedia.org::article_view          |    0.614574 | 0.550000 | 0.574556 |
| J2    | youtube.com::search_results_view     |    0.876424 | 0.910000 | 0.891159 |
| J2    | youtube.com::video_playback          |    0.920335 | 0.933333 | 0.925615 |
| J3    | bing.com::search_results_view        |    0.793679 | 0.736667 | 0.761711 |
| J3    | developer.mozilla.org::document_view |    0.586157 | 0.650000 | 0.614046 |
| J3    | github.com::repository_view          |    0.838814 | 0.870000 | 0.850248 |
| J3    | wikipedia.org::article_view          |    0.619644 | 0.543333 | 0.573734 |
| J3    | youtube.com::search_results_view     |    0.888352 | 0.913333 | 0.899175 |
| J3    | youtube.com::video_playback          |    0.942832 | 0.923333 | 0.931213 |
| J4    | bing.com::search_results_view        |    0.793547 | 0.753333 | 0.769772 |
| J4    | developer.mozilla.org::document_view |    0.590606 | 0.666667 | 0.623493 |
| J4    | github.com::repository_view          |    0.874715 | 0.866667 | 0.864068 |
| J4    | wikipedia.org::article_view          |    0.639321 | 0.543333 | 0.581495 |
| J4    | youtube.com::search_results_view     |    0.880345 | 0.906667 | 0.890396 |
| J4    | youtube.com::video_playback          |    0.941146 | 0.943333 | 0.940709 |
| J5    | bing.com::search_results_view        |    0.804320 | 0.736667 | 0.765627 |
| J5    | developer.mozilla.org::document_view |    0.588531 | 0.623333 | 0.601698 |
| J5    | github.com::repository_view          |    0.861785 | 0.866667 | 0.858229 |
| J5    | wikipedia.org::article_view          |    0.612643 | 0.560000 | 0.579007 |
| J5    | youtube.com::search_results_view     |    0.886479 | 0.913333 | 0.897485 |
| J5    | youtube.com::video_playback          |    0.935135 | 0.956667 | 0.944472 |
| J6    | bing.com::search_results_view        |    0.792988 | 0.730000 | 0.757986 |
| J6    | developer.mozilla.org::document_view |    0.589793 | 0.606667 | 0.593249 |
| J6    | github.com::repository_view          |    0.850219 | 0.866667 | 0.853739 |
| J6    | wikipedia.org::article_view          |    0.593476 | 0.530000 | 0.548870 |
| J6    | youtube.com::search_results_view     |    0.878141 | 0.910000 | 0.892393 |
| J6    | youtube.com::video_playback          |    0.912196 | 0.946667 | 0.927952 |
| J7    | bing.com::search_results_view        |    0.792763 | 0.710000 | 0.746144 |
| J7    | developer.mozilla.org::document_view |    0.598082 | 0.766667 | 0.671076 |
| J7    | github.com::repository_view          |    0.854466 | 0.796667 | 0.814668 |
| J7    | wikipedia.org::article_view          |    0.675013 | 0.483333 | 0.557501 |
| J7    | youtube.com::search_results_view     |    0.855884 | 0.926667 | 0.888710 |
| J7    | youtube.com::video_playback          |    0.909898 | 0.940000 | 0.920802 |

### 部署业务分项

| arm   | protocol    | class                                |   precision |   recall |       F1 |
|:------|:------------|:-------------------------------------|------------:|---------:|---------:|
| J0    | anytls      | bing.com::search_results_view        |    0.768031 | 0.716667 | 0.741341 |
| J0    | anytls      | developer.mozilla.org::document_view |    0.672497 | 0.883333 | 0.761885 |
| J0    | anytls      | github.com::repository_view          |    0.805556 | 0.966667 | 0.878788 |
| J0    | anytls      | wikipedia.org::article_view          |    0.911681 | 0.433333 | 0.578970 |
| J0    | anytls      | youtube.com::search_results_view     |    0.858442 | 0.900000 | 0.878397 |
| J0    | anytls      | youtube.com::video_playback          |    0.934921 | 0.950000 | 0.942276 |
| J0    | shadowsocks | bing.com::search_results_view        |    0.728947 | 0.716667 | 0.722650 |
| J0    | shadowsocks | developer.mozilla.org::document_view |    0.585284 | 0.700000 | 0.637007 |
| J0    | shadowsocks | github.com::repository_view          |    0.959559 | 0.783333 | 0.862362 |
| J0    | shadowsocks | wikipedia.org::article_view          |    0.692130 | 0.566667 | 0.622250 |
| J0    | shadowsocks | youtube.com::search_results_view     |    0.952381 | 1.000000 | 0.975610 |
| J0    | shadowsocks | youtube.com::video_playback          |    0.882740 | 1.000000 | 0.937615 |
| J0    | trojan      | bing.com::search_results_view        |    0.760512 | 0.733333 | 0.745927 |
| J0    | trojan      | developer.mozilla.org::document_view |    0.547222 | 0.600000 | 0.571573 |
| J0    | trojan      | github.com::repository_view          |    0.846839 | 0.816667 | 0.830629 |
| J0    | trojan      | wikipedia.org::article_view          |    0.542189 | 0.550000 | 0.545758 |
| J0    | trojan      | youtube.com::search_results_view     |    0.812448 | 0.783333 | 0.796825 |
| J0    | trojan      | youtube.com::video_playback          |    0.882206 | 0.866667 | 0.873880 |
| J0    | vless       | bing.com::search_results_view        |    0.751253 | 0.750000 | 0.750313 |
| J0    | vless       | developer.mozilla.org::document_view |    0.651010 | 0.683333 | 0.666531 |
| J0    | vless       | github.com::repository_view          |    0.842105 | 0.800000 | 0.820513 |
| J0    | vless       | wikipedia.org::article_view          |    0.541467 | 0.550000 | 0.545177 |
| J0    | vless       | youtube.com::search_results_view     |    0.819565 | 0.900000 | 0.856977 |
| J0    | vless       | youtube.com::video_playback          |    0.962963 | 0.850000 | 0.902798 |
| J0    | vmess       | bing.com::search_results_view        |    0.826331 | 0.616667 | 0.704822 |
| J0    | vmess       | developer.mozilla.org::document_view |    0.544216 | 0.633333 | 0.584988 |
| J0    | vmess       | github.com::repository_view          |    0.844697 | 0.983333 | 0.908369 |
| J0    | vmess       | wikipedia.org::article_view          |    0.584804 | 0.466667 | 0.518776 |
| J0    | vmess       | youtube.com::search_results_view     |    0.875758 | 0.933333 | 0.903175 |
| J0    | vmess       | youtube.com::video_playback          |    0.921284 | 0.966667 | 0.943070 |
| J1    | anytls      | bing.com::search_results_view        |    0.846878 | 0.733333 | 0.785016 |
| J1    | anytls      | developer.mozilla.org::document_view |    0.683317 | 0.783333 | 0.728374 |
| J1    | anytls      | github.com::repository_view          |    0.760494 | 1.000000 | 0.863672 |
| J1    | anytls      | wikipedia.org::article_view          |    0.802646 | 0.500000 | 0.609118 |
| J1    | anytls      | youtube.com::search_results_view     |    0.891053 | 0.950000 | 0.919473 |
| J1    | anytls      | youtube.com::video_playback          |    0.983333 | 0.950000 | 0.966239 |
| J1    | shadowsocks | bing.com::search_results_view        |    0.779825 | 0.716667 | 0.745299 |
| J1    | shadowsocks | developer.mozilla.org::document_view |    0.609668 | 0.650000 | 0.629113 |
| J1    | shadowsocks | github.com::repository_view          |    0.857700 | 0.800000 | 0.827710 |
| J1    | shadowsocks | wikipedia.org::article_view          |    0.607212 | 0.566667 | 0.586145 |
| J1    | shadowsocks | youtube.com::search_results_view     |    0.952381 | 1.000000 | 0.975610 |
| J1    | shadowsocks | youtube.com::video_playback          |    0.913043 | 1.000000 | 0.953488 |
| J1    | trojan      | bing.com::search_results_view        |    0.757937 | 0.783333 | 0.770325 |
| J1    | trojan      | developer.mozilla.org::document_view |    0.551100 | 0.533333 | 0.541501 |
| J1    | trojan      | github.com::repository_view          |    0.773794 | 0.850000 | 0.809830 |
| J1    | trojan      | wikipedia.org::article_view          |    0.572829 | 0.566667 | 0.567923 |
| J1    | trojan      | youtube.com::search_results_view     |    0.884532 | 0.766667 | 0.821242 |
| J1    | trojan      | youtube.com::video_playback          |    0.903175 | 0.933333 | 0.917886 |
| J1    | vless       | bing.com::search_results_view        |    0.882353 | 0.750000 | 0.810811 |
| J1    | vless       | developer.mozilla.org::document_view |    0.522141 | 0.416667 | 0.463192 |
| J1    | vless       | github.com::repository_view          |    0.860331 | 0.816667 | 0.837539 |
| J1    | vless       | wikipedia.org::article_view          |    0.404938 | 0.533333 | 0.460205 |
| J1    | vless       | youtube.com::search_results_view     |    0.838603 | 0.950000 | 0.890735 |
| J1    | vless       | youtube.com::video_playback          |    0.947368 | 0.900000 | 0.923077 |
| J1    | vmess       | bing.com::search_results_view        |    0.750735 | 0.600000 | 0.666509 |
| J1    | vmess       | developer.mozilla.org::document_view |    0.541667 | 0.666667 | 0.597497 |
| J1    | vmess       | github.com::repository_view          |    0.797778 | 0.983333 | 0.880808 |
| J1    | vmess       | wikipedia.org::article_view          |    0.631868 | 0.433333 | 0.513963 |
| J1    | vmess       | youtube.com::search_results_view     |    0.898246 | 0.883333 | 0.890598 |
| J1    | vmess       | youtube.com::video_playback          |    0.907576 | 0.966667 | 0.935714 |
| J2    | anytls      | bing.com::search_results_view        |    0.860294 | 0.716667 | 0.781782 |
| J2    | anytls      | developer.mozilla.org::document_view |    0.682759 | 0.750000 | 0.714556 |
| J2    | anytls      | github.com::repository_view          |    0.866805 | 0.966667 | 0.913594 |
| J2    | anytls      | wikipedia.org::article_view          |    0.740741 | 0.616667 | 0.672515 |
| J2    | anytls      | youtube.com::search_results_view     |    0.861472 | 0.933333 | 0.895858 |
| J2    | anytls      | youtube.com::video_playback          |    0.919841 | 0.950000 | 0.934553 |
| J2    | shadowsocks | bing.com::search_results_view        |    0.759550 | 0.783333 | 0.770541 |
| J2    | shadowsocks | developer.mozilla.org::document_view |    0.534444 | 0.650000 | 0.586532 |
| J2    | shadowsocks | github.com::repository_view          |    0.979167 | 0.750000 | 0.849206 |
| J2    | shadowsocks | wikipedia.org::article_view          |    0.615741 | 0.533333 | 0.571150 |
| J2    | shadowsocks | youtube.com::search_results_view     |    0.951587 | 0.983333 | 0.967073 |
| J2    | shadowsocks | youtube.com::video_playback          |    0.893030 | 0.966667 | 0.927964 |
| J2    | trojan      | bing.com::search_results_view        |    0.822055 | 0.833333 | 0.827184 |
| J2    | trojan      | developer.mozilla.org::document_view |    0.534646 | 0.633333 | 0.578730 |
| J2    | trojan      | github.com::repository_view          |    0.803968 | 0.816667 | 0.810163 |
| J2    | trojan      | wikipedia.org::article_view          |    0.641865 | 0.550000 | 0.589302 |
| J2    | trojan      | youtube.com::search_results_view     |    0.868192 | 0.766667 | 0.814130 |
| J2    | trojan      | youtube.com::video_playback          |    0.886508 | 0.916667 | 0.901220 |
| J2    | vless       | bing.com::search_results_view        |    0.870980 | 0.766667 | 0.814440 |
| J2    | vless       | developer.mozilla.org::document_view |    0.615741 | 0.533333 | 0.571150 |
| J2    | vless       | github.com::repository_view          |    0.890724 | 0.800000 | 0.842494 |
| J2    | vless       | wikipedia.org::article_view          |    0.461429 | 0.600000 | 0.521296 |
| J2    | vless       | youtube.com::search_results_view     |    0.811978 | 0.933333 | 0.868167 |
| J2    | vless       | youtube.com::video_playback          |    0.982456 | 0.883333 | 0.929788 |
| J2    | vmess       | bing.com::search_results_view        |    0.723720 | 0.616667 | 0.665534 |
| J2    | vmess       | developer.mozilla.org::document_view |    0.521135 | 0.616667 | 0.564834 |
| J2    | vmess       | github.com::repository_view          |    0.826087 | 0.950000 | 0.883721 |
| J2    | vmess       | wikipedia.org::article_view          |    0.613095 | 0.450000 | 0.518519 |
| J2    | vmess       | youtube.com::search_results_view     |    0.888889 | 0.933333 | 0.910569 |
| J2    | vmess       | youtube.com::video_playback          |    0.919841 | 0.950000 | 0.934553 |
| J3    | anytls      | bing.com::search_results_view        |    0.853457 | 0.783333 | 0.816355 |
| J3    | anytls      | developer.mozilla.org::document_view |    0.686869 | 0.766667 | 0.724035 |
| J3    | anytls      | github.com::repository_view          |    0.837218 | 1.000000 | 0.910346 |
| J3    | anytls      | wikipedia.org::article_view          |    0.730769 | 0.550000 | 0.626263 |
| J3    | anytls      | youtube.com::search_results_view     |    0.890332 | 0.950000 | 0.919086 |
| J3    | anytls      | youtube.com::video_playback          |    1.000000 | 0.950000 | 0.974359 |
| J3    | shadowsocks | bing.com::search_results_view        |    0.761839 | 0.683333 | 0.720089 |
| J3    | shadowsocks | developer.mozilla.org::document_view |    0.560000 | 0.700000 | 0.622222 |
| J3    | shadowsocks | github.com::repository_view          |    0.867725 | 0.783333 | 0.820900 |
| J3    | shadowsocks | wikipedia.org::article_view          |    0.648557 | 0.550000 | 0.594884 |
| J3    | shadowsocks | youtube.com::search_results_view     |    0.950794 | 0.966667 | 0.958537 |
| J3    | shadowsocks | youtube.com::video_playback          |    0.911067 | 0.966667 | 0.936451 |
| J3    | trojan      | bing.com::search_results_view        |    0.757921 | 0.833333 | 0.793570 |
| J3    | trojan      | developer.mozilla.org::document_view |    0.555731 | 0.600000 | 0.576523 |
| J3    | trojan      | github.com::repository_view          |    0.814035 | 0.800000 | 0.806838 |
| J3    | trojan      | wikipedia.org::article_view          |    0.621849 | 0.566667 | 0.591518 |
| J3    | trojan      | youtube.com::search_results_view     |    0.871116 | 0.783333 | 0.824476 |
| J3    | trojan      | youtube.com::video_playback          |    0.885714 | 0.900000 | 0.892683 |
| J3    | vless       | bing.com::search_results_view        |    0.822222 | 0.766667 | 0.792982 |
| J3    | vless       | developer.mozilla.org::document_view |    0.594298 | 0.533333 | 0.561254 |
| J3    | vless       | github.com::repository_view          |    0.857700 | 0.800000 | 0.827710 |
| J3    | vless       | wikipedia.org::article_view          |    0.474426 | 0.583333 | 0.522923 |
| J3    | vless       | youtube.com::search_results_view     |    0.826346 | 0.933333 | 0.875892 |
| J3    | vless       | youtube.com::video_playback          |    0.982456 | 0.850000 | 0.910295 |
| J3    | vmess       | bing.com::search_results_view        |    0.772958 | 0.616667 | 0.685557 |
| J3    | vmess       | developer.mozilla.org::document_view |    0.533889 | 0.650000 | 0.586195 |
| J3    | vmess       | github.com::repository_view          |    0.817391 | 0.966667 | 0.885444 |
| J3    | vmess       | wikipedia.org::article_view          |    0.622619 | 0.466667 | 0.533084 |
| J3    | vmess       | youtube.com::search_results_view     |    0.903175 | 0.933333 | 0.917886 |
| J3    | vmess       | youtube.com::video_playback          |    0.934921 | 0.950000 | 0.942276 |
| J4    | anytls      | bing.com::search_results_view        |    0.828070 | 0.800000 | 0.813675 |
| J4    | anytls      | developer.mozilla.org::document_view |    0.692035 | 0.783333 | 0.733850 |
| J4    | anytls      | github.com::repository_view          |    0.863726 | 1.000000 | 0.925136 |
| J4    | anytls      | wikipedia.org::article_view          |    0.798463 | 0.583333 | 0.668523 |
| J4    | anytls      | youtube.com::search_results_view     |    0.903030 | 0.933333 | 0.917460 |
| J4    | anytls      | youtube.com::video_playback          |    0.983333 | 0.950000 | 0.966239 |
| J4    | shadowsocks | bing.com::search_results_view        |    0.783991 | 0.716667 | 0.747151 |
| J4    | shadowsocks | developer.mozilla.org::document_view |    0.551905 | 0.716667 | 0.623148 |
| J4    | shadowsocks | github.com::repository_view          |    0.959559 | 0.750000 | 0.840576 |
| J4    | shadowsocks | wikipedia.org::article_view          |    0.626323 | 0.500000 | 0.554638 |
| J4    | shadowsocks | youtube.com::search_results_view     |    0.923521 | 1.000000 | 0.960124 |
| J4    | shadowsocks | youtube.com::video_playback          |    0.884300 | 0.983333 | 0.929774 |
| J4    | trojan      | bing.com::search_results_view        |    0.740064 | 0.850000 | 0.790983 |
| J4    | trojan      | developer.mozilla.org::document_view |    0.575556 | 0.700000 | 0.631650 |
| J4    | trojan      | github.com::repository_view          |    0.839181 | 0.783333 | 0.810166 |
| J4    | trojan      | wikipedia.org::article_view          |    0.682870 | 0.566667 | 0.618908 |
| J4    | trojan      | youtube.com::search_results_view     |    0.900735 | 0.750000 | 0.818318 |
| J4    | trojan      | youtube.com::video_playback          |    0.903175 | 0.933333 | 0.917886 |
| J4    | vless       | bing.com::search_results_view        |    0.823942 | 0.766667 | 0.793347 |
| J4    | vless       | developer.mozilla.org::document_view |    0.565531 | 0.500000 | 0.530377 |
| J4    | vless       | github.com::repository_view          |    0.888889 | 0.800000 | 0.842105 |
| J4    | vless       | wikipedia.org::article_view          |    0.464928 | 0.566667 | 0.510594 |
| J4    | vless       | youtube.com::search_results_view     |    0.801423 | 0.933333 | 0.861769 |
| J4    | vless       | youtube.com::video_playback          |    1.000000 | 0.900000 | 0.947368 |
| J4    | vmess       | bing.com::search_results_view        |    0.791667 | 0.633333 | 0.703704 |
| J4    | vmess       | developer.mozilla.org::document_view |    0.568001 | 0.633333 | 0.598441 |
| J4    | vmess       | github.com::repository_view          |    0.822222 | 1.000000 | 0.902357 |
| J4    | vmess       | wikipedia.org::article_view          |    0.624020 | 0.500000 | 0.554812 |
| J4    | vmess       | youtube.com::search_results_view     |    0.873016 | 0.916667 | 0.894309 |
| J4    | vmess       | youtube.com::video_playback          |    0.934921 | 0.950000 | 0.942276 |
| J5    | anytls      | bing.com::search_results_view        |    0.851508 | 0.766667 | 0.806458 |
| J5    | anytls      | developer.mozilla.org::document_view |    0.703030 | 0.750000 | 0.725397 |
| J5    | anytls      | github.com::repository_view          |    0.807879 | 0.966667 | 0.879365 |
| J5    | anytls      | wikipedia.org::article_view          |    0.747199 | 0.583333 | 0.654125 |
| J5    | anytls      | youtube.com::search_results_view     |    0.862193 | 0.933333 | 0.896245 |
| J5    | anytls      | youtube.com::video_playback          |    0.983333 | 0.950000 | 0.966239 |
| J5    | shadowsocks | bing.com::search_results_view        |    0.779825 | 0.766667 | 0.773077 |
| J5    | shadowsocks | developer.mozilla.org::document_view |    0.559343 | 0.633333 | 0.593795 |
| J5    | shadowsocks | github.com::repository_view          |    0.979167 | 0.766667 | 0.859788 |
| J5    | shadowsocks | wikipedia.org::article_view          |    0.600390 | 0.550000 | 0.573999 |
| J5    | shadowsocks | youtube.com::search_results_view     |    0.952381 | 1.000000 | 0.975610 |
| J5    | shadowsocks | youtube.com::video_playback          |    0.883838 | 1.000000 | 0.937951 |
| J5    | trojan      | bing.com::search_results_view        |    0.753968 | 0.816667 | 0.783972 |
| J5    | trojan      | developer.mozilla.org::document_view |    0.595575 | 0.683333 | 0.636246 |
| J5    | trojan      | github.com::repository_view          |    0.844737 | 0.816667 | 0.830342 |
| J5    | trojan      | wikipedia.org::article_view          |    0.665979 | 0.600000 | 0.630947 |
| J5    | trojan      | youtube.com::search_results_view     |    0.921569 | 0.783333 | 0.846847 |
| J5    | trojan      | youtube.com::video_playback          |    0.904762 | 0.950000 | 0.926829 |
| J5    | vless       | bing.com::search_results_view        |    0.849673 | 0.750000 | 0.796586 |
| J5    | vless       | developer.mozilla.org::document_view |    0.549679 | 0.416667 | 0.473064 |
| J5    | vless       | github.com::repository_view          |    0.857700 | 0.800000 | 0.827710 |
| J5    | vless       | wikipedia.org::article_view          |    0.439925 | 0.600000 | 0.507391 |
| J5    | vless       | youtube.com::search_results_view     |    0.823452 | 0.933333 | 0.874862 |
| J5    | vless       | youtube.com::video_playback          |    0.982456 | 0.916667 | 0.948268 |
| J5    | vmess       | bing.com::search_results_view        |    0.786626 | 0.583333 | 0.668039 |
| J5    | vmess       | developer.mozilla.org::document_view |    0.535024 | 0.633333 | 0.579986 |
| J5    | vmess       | github.com::repository_view          |    0.819444 | 0.983333 | 0.893939 |
| J5    | vmess       | wikipedia.org::article_view          |    0.609722 | 0.466667 | 0.528571 |
| J5    | vmess       | youtube.com::search_results_view     |    0.872799 | 0.916667 | 0.893864 |
| J5    | vmess       | youtube.com::video_playback          |    0.921284 | 0.966667 | 0.943070 |
| J6    | anytls      | bing.com::search_results_view        |    0.839286 | 0.766667 | 0.798840 |
| J6    | anytls      | developer.mozilla.org::document_view |    0.722281 | 0.766667 | 0.741168 |
| J6    | anytls      | github.com::repository_view          |    0.798077 | 0.983333 | 0.880764 |
| J6    | anytls      | wikipedia.org::article_view          |    0.818308 | 0.566667 | 0.665318 |
| J6    | anytls      | youtube.com::search_results_view     |    0.863636 | 0.950000 | 0.904762 |
| J6    | anytls      | youtube.com::video_playback          |    0.966667 | 0.950000 | 0.958120 |
| J6    | shadowsocks | bing.com::search_results_view        |    0.766835 | 0.766667 | 0.765455 |
| J6    | shadowsocks | developer.mozilla.org::document_view |    0.588933 | 0.666667 | 0.625323 |
| J6    | shadowsocks | github.com::repository_view          |    0.904003 | 0.766667 | 0.829224 |
| J6    | shadowsocks | wikipedia.org::article_view          |    0.599265 | 0.500000 | 0.545045 |
| J6    | shadowsocks | youtube.com::search_results_view     |    0.937951 | 1.000000 | 0.967867 |
| J6    | shadowsocks | youtube.com::video_playback          |    0.897170 | 1.000000 | 0.945358 |
| J6    | trojan      | bing.com::search_results_view        |    0.738038 | 0.750000 | 0.743284 |
| J6    | trojan      | developer.mozilla.org::document_view |    0.572631 | 0.583333 | 0.576910 |
| J6    | trojan      | github.com::repository_view          |    0.847059 | 0.800000 | 0.821622 |
| J6    | trojan      | wikipedia.org::article_view          |    0.536316 | 0.566667 | 0.549145 |
| J6    | trojan      | youtube.com::search_results_view     |    0.871116 | 0.783333 | 0.824476 |
| J6    | trojan      | youtube.com::video_playback          |    0.904762 | 0.950000 | 0.926829 |
| J6    | vless       | bing.com::search_results_view        |    0.882353 | 0.750000 | 0.810811 |
| J6    | vless       | developer.mozilla.org::document_view |    0.529412 | 0.383333 | 0.442806 |
| J6    | vless       | github.com::repository_view          |    0.860331 | 0.816667 | 0.837539 |
| J6    | vless       | wikipedia.org::article_view          |    0.408730 | 0.583333 | 0.480082 |
| J6    | vless       | youtube.com::search_results_view     |    0.864828 | 0.950000 | 0.905104 |
| J6    | vless       | youtube.com::video_playback          |    0.913060 | 0.866667 | 0.888844 |
| J6    | vmess       | bing.com::search_results_view        |    0.738426 | 0.616667 | 0.671540 |
| J6    | vmess       | developer.mozilla.org::document_view |    0.535707 | 0.633333 | 0.580038 |
| J6    | vmess       | github.com::repository_view          |    0.841623 | 0.966667 | 0.899544 |
| J6    | vmess       | wikipedia.org::article_view          |    0.604762 | 0.433333 | 0.504762 |
| J6    | vmess       | youtube.com::search_results_view     |    0.853175 | 0.866667 | 0.859756 |
| J6    | vmess       | youtube.com::video_playback          |    0.879321 | 0.966667 | 0.920608 |
| J7    | anytls      | bing.com::search_results_view        |    0.785185 | 0.666667 | 0.719799 |
| J7    | anytls      | developer.mozilla.org::document_view |    0.663004 | 0.883333 | 0.757246 |
| J7    | anytls      | github.com::repository_view          |    0.808838 | 0.883333 | 0.843290 |
| J7    | anytls      | wikipedia.org::article_view          |    0.883903 | 0.500000 | 0.635297 |
| J7    | anytls      | youtube.com::search_results_view     |    0.835968 | 0.933333 | 0.881875 |
| J7    | anytls      | youtube.com::video_playback          |    0.921212 | 0.950000 | 0.934921 |
| J7    | shadowsocks | bing.com::search_results_view        |    0.763158 | 0.750000 | 0.756410 |
| J7    | shadowsocks | developer.mozilla.org::document_view |    0.609877 | 0.783333 | 0.685579 |
| J7    | shadowsocks | github.com::repository_view          |    1.000000 | 0.616667 | 0.762626 |
| J7    | shadowsocks | wikipedia.org::article_view          |    0.679167 | 0.483333 | 0.562632 |
| J7    | shadowsocks | youtube.com::search_results_view     |    0.907648 | 0.983333 | 0.943864 |
| J7    | shadowsocks | youtube.com::video_playback          |    0.747839 | 0.983333 | 0.849114 |
| J7    | trojan      | bing.com::search_results_view        |    0.710606 | 0.733333 | 0.721429 |
| J7    | trojan      | developer.mozilla.org::document_view |    0.568519 | 0.683333 | 0.618322 |
| J7    | trojan      | github.com::repository_view          |    0.801337 | 0.800000 | 0.800334 |
| J7    | trojan      | wikipedia.org::article_view          |    0.596639 | 0.516667 | 0.549272 |
| J7    | trojan      | youtube.com::search_results_view     |    0.843665 | 0.800000 | 0.820873 |
| J7    | trojan      | youtube.com::video_playback          |    0.946394 | 0.883333 | 0.913630 |
| J7    | vless       | bing.com::search_results_view        |    0.850000 | 0.733333 | 0.785185 |
| J7    | vless       | developer.mozilla.org::document_view |    0.596049 | 0.783333 | 0.676753 |
| J7    | vless       | github.com::repository_view          |    0.838562 | 0.766667 | 0.800095 |
| J7    | vless       | wikipedia.org::article_view          |    0.588371 | 0.500000 | 0.540303 |
| J7    | vless       | youtube.com::search_results_view     |    0.838603 | 0.950000 | 0.890735 |
| J7    | vless       | youtube.com::video_playback          |    0.982456 | 0.900000 | 0.939271 |
| J7    | vmess       | bing.com::search_results_view        |    0.854867 | 0.666667 | 0.747895 |
| J7    | vmess       | developer.mozilla.org::document_view |    0.552963 | 0.700000 | 0.617480 |
| J7    | vmess       | github.com::repository_view          |    0.823593 | 0.916667 | 0.866998 |
| J7    | vmess       | wikipedia.org::article_view          |    0.626984 | 0.416667 | 0.500000 |
| J7    | vmess       | youtube.com::search_results_view     |    0.853535 | 0.966667 | 0.906205 |
| J7    | vmess       | youtube.com::video_playback          |    0.951587 | 0.983333 | 0.967073 |

## 修复错误和新增错误

| comparison   |   repaired |   new_error |
|:-------------|-----------:|------------:|
| J2-J1        |         53 |          43 |
| J4-J0        |         75 |          57 |
| J4-J1        |         69 |          44 |
| J4-J2        |         49 |          34 |
| J4-J3        |         38 |          25 |
| J4-J5        |         52 |          45 |
| J4-J6        |         67 |          40 |
| J4-J7        |         99 |          82 |
| J6-J1        |         37 |          39 |
| J7-J0        |         80 |          79 |

| comparison   | protocol    |   repaired |   new_error |
|:-------------|:------------|-----------:|------------:|
| J2-J1        | anytls      |         11 |          10 |
| J2-J1        | shadowsocks |          8 |          12 |
| J2-J1        | trojan      |         12 |           7 |
| J2-J1        | vless       |         15 |           6 |
| J2-J1        | vmess       |          7 |           8 |
| J4-J0        | anytls      |         21 |           9 |
| J4-J0        | shadowsocks |         11 |          17 |
| J4-J0        | trojan      |         23 |           9 |
| J4-J0        | vless       |         10 |          14 |
| J4-J0        | vmess       |         10 |           8 |
| J4-J1        | anytls      |         13 |           5 |
| J4-J1        | shadowsocks |         12 |          16 |
| J4-J1        | trojan      |         18 |           9 |
| J4-J1        | vless       |         12 |           6 |
| J4-J1        | vmess       |         14 |           8 |
| J4-J2        | anytls      |         14 |           7 |
| J4-J2        | shadowsocks |         11 |          11 |
| J4-J2        | trojan      |         10 |           6 |
| J4-J2        | vless       |          3 |           6 |
| J4-J2        | vmess       |         11 |           4 |
| J4-J3        | anytls      |          7 |           4 |
| J4-J3        | shadowsocks |          9 |           8 |
| J4-J3        | trojan      |         10 |           4 |
| J4-J3        | vless       |          4 |           4 |
| J4-J3        | vmess       |          8 |           5 |
| J4-J5        | anytls      |         13 |           7 |
| J4-J5        | shadowsocks |          8 |          11 |
| J4-J5        | trojan      |         10 |          14 |
| J4-J5        | vless       |         10 |           7 |
| J4-J5        | vmess       |         11 |           6 |
| J4-J6        | anytls      |         14 |          10 |
| J4-J6        | shadowsocks |         12 |          14 |
| J4-J6        | trojan      |         15 |           6 |
| J4-J6        | vless       |         11 |           4 |
| J4-J6        | vmess       |         15 |           6 |
| J4-J7        | anytls      |         27 |          13 |
| J4-J7        | shadowsocks |         21 |          17 |
| J4-J7        | trojan      |         21 |          11 |
| J4-J7        | vless       |         15 |          25 |
| J4-J7        | vmess       |         15 |          16 |
| J6-J1        | anytls      |          9 |           5 |
| J6-J1        | shadowsocks |          7 |           9 |
| J6-J1        | trojan      |          9 |           9 |
| J6-J1        | vless       |          8 |           9 |
| J6-J1        | vmess       |          4 |           7 |
| J7-J0        | anytls      |         18 |          20 |
| J7-J0        | shadowsocks |         13 |          23 |
| J7-J0        | trojan      |         17 |          13 |
| J7-J0        | vless       |         19 |          13 |
| J7-J0        | vmess       |         13 |          10 |

这些计数跨三seed的1800预测，不是1800独立访问。内容级台账另存content-error-transitions.parquet，不能据有利视频或协议重新选择目标。

## 完整混淆矩阵

### J0

| truth                                |   bing.com::search_results_view |   developer.mozilla.org::document_view |   github.com::repository_view |   wikipedia.org::article_view |   youtube.com::search_results_view |   youtube.com::video_playback |
|:-------------------------------------|--------------------------------:|---------------------------------------:|------------------------------:|------------------------------:|-----------------------------------:|------------------------------:|
| bing.com::search_results_view        |                             212 |                                     16 |                            18 |                            11 |                                 25 |                            18 |
| developer.mozilla.org::document_view |                              15 |                                    210 |                             1 |                            74 |                                  0 |                             0 |
| github.com::repository_view          |                              18 |                                      5 |                           261 |                             9 |                                  7 |                             0 |
| wikipedia.org::article_view          |                               9 |                                    119 |                            18 |                           154 |                                  0 |                             0 |
| youtube.com::search_results_view     |                              15 |                                      0 |                             6 |                             0 |                                271 |                             8 |
| youtube.com::video_playback          |                               9 |                                      0 |                             2 |                             0 |                                 11 |                           278 |

### J1

| truth                                |   bing.com::search_results_view |   developer.mozilla.org::document_view |   github.com::repository_view |   wikipedia.org::article_view |   youtube.com::search_results_view |   youtube.com::video_playback |
|:-------------------------------------|--------------------------------:|---------------------------------------:|------------------------------:|------------------------------:|-----------------------------------:|------------------------------:|
| bing.com::search_results_view        |                             215 |                                     13 |                            29 |                            10 |                                 20 |                            13 |
| developer.mozilla.org::document_view |                              18 |                                    183 |                             4 |                            95 |                                  0 |                             0 |
| github.com::repository_view          |                              12 |                                      1 |                           267 |                            13 |                                  5 |                             2 |
| wikipedia.org::article_view          |                               5 |                                    116 |                            23 |                           156 |                                  0 |                             0 |
| youtube.com::search_results_view     |                              13 |                                      0 |                             7 |                             0 |                                273 |                             7 |
| youtube.com::video_playback          |                               5 |                                      0 |                             2 |                             0 |                                  8 |                           285 |

### J2

| truth                                |   bing.com::search_results_view |   developer.mozilla.org::document_view |   github.com::repository_view |   wikipedia.org::article_view |   youtube.com::search_results_view |   youtube.com::video_playback |
|:-------------------------------------|--------------------------------:|---------------------------------------:|------------------------------:|------------------------------:|-----------------------------------:|------------------------------:|
| bing.com::search_results_view        |                             223 |                                     18 |                            17 |                             9 |                                 21 |                            12 |
| developer.mozilla.org::document_view |                              17 |                                    191 |                             2 |                            90 |                                  0 |                             0 |
| github.com::repository_view          |                              11 |                                      8 |                           257 |                            12 |                                  9 |                             3 |
| wikipedia.org::article_view          |                               5 |                                    115 |                            12 |                           165 |                                  0 |                             3 |
| youtube.com::search_results_view     |                              12 |                                      0 |                             8 |                             0 |                                273 |                             7 |
| youtube.com::video_playback          |                               9 |                                      1 |                             1 |                             0 |                                  9 |                           280 |

### J3

| truth                                |   bing.com::search_results_view |   developer.mozilla.org::document_view |   github.com::repository_view |   wikipedia.org::article_view |   youtube.com::search_results_view |   youtube.com::video_playback |
|:-------------------------------------|--------------------------------:|---------------------------------------:|------------------------------:|------------------------------:|-----------------------------------:|------------------------------:|
| bing.com::search_results_view        |                             221 |                                     17 |                            20 |                            10 |                                 21 |                            11 |
| developer.mozilla.org::document_view |                              14 |                                    195 |                             3 |                            88 |                                  0 |                             0 |
| github.com::repository_view          |                              16 |                                      8 |                           261 |                             9 |                                  5 |                             1 |
| wikipedia.org::article_view          |                               6 |                                    113 |                            18 |                           163 |                                  0 |                             0 |
| youtube.com::search_results_view     |                              13 |                                      0 |                             7 |                             0 |                                274 |                             6 |
| youtube.com::video_playback          |                               9 |                                      1 |                             4 |                             0 |                                  9 |                           277 |

### J4

| truth                                |   bing.com::search_results_view |   developer.mozilla.org::document_view |   github.com::repository_view |   wikipedia.org::article_view |   youtube.com::search_results_view |   youtube.com::video_playback |
|:-------------------------------------|--------------------------------:|---------------------------------------:|------------------------------:|------------------------------:|-----------------------------------:|------------------------------:|
| bing.com::search_results_view        |                             226 |                                     15 |                            18 |                             9 |                                 20 |                            12 |
| developer.mozilla.org::document_view |                              15 |                                    200 |                             2 |                            83 |                                  0 |                             0 |
| github.com::repository_view          |                              14 |                                     10 |                           260 |                             8 |                                  7 |                             1 |
| wikipedia.org::article_view          |                               8 |                                    114 |                            14 |                           163 |                                  1 |                             0 |
| youtube.com::search_results_view     |                              18 |                                      0 |                             4 |                             0 |                                272 |                             6 |
| youtube.com::video_playback          |                               5 |                                      0 |                             2 |                             0 |                                 10 |                           283 |

### J5

| truth                                |   bing.com::search_results_view |   developer.mozilla.org::document_view |   github.com::repository_view |   wikipedia.org::article_view |   youtube.com::search_results_view |   youtube.com::video_playback |
|:-------------------------------------|--------------------------------:|---------------------------------------:|------------------------------:|------------------------------:|-----------------------------------:|------------------------------:|
| bing.com::search_results_view        |                             221 |                                     20 |                            18 |                             8 |                                 23 |                            10 |
| developer.mozilla.org::document_view |                              15 |                                    187 |                             1 |                            97 |                                  0 |                             0 |
| github.com::repository_view          |                              14 |                                      4 |                           260 |                            11 |                                  7 |                             4 |
| wikipedia.org::article_view          |                               7 |                                    106 |                            19 |                           168 |                                  0 |                             0 |
| youtube.com::search_results_view     |                              14 |                                      0 |                             5 |                             0 |                                274 |                             7 |
| youtube.com::video_playback          |                               5 |                                      0 |                             2 |                             0 |                                  6 |                           287 |

### J6

| truth                                |   bing.com::search_results_view |   developer.mozilla.org::document_view |   github.com::repository_view |   wikipedia.org::article_view |   youtube.com::search_results_view |   youtube.com::video_playback |
|:-------------------------------------|--------------------------------:|---------------------------------------:|------------------------------:|------------------------------:|-----------------------------------:|------------------------------:|
| bing.com::search_results_view        |                             219 |                                     10 |                            19 |                            12 |                                 23 |                            17 |
| developer.mozilla.org::document_view |                              17 |                                    182 |                             2 |                            99 |                                  0 |                             0 |
| github.com::repository_view          |                              15 |                                      2 |                           260 |                            15 |                                  5 |                             3 |
| wikipedia.org::article_view          |                               8 |                                    113 |                            20 |                           159 |                                  0 |                             0 |
| youtube.com::search_results_view     |                              13 |                                      0 |                             6 |                             0 |                                273 |                             8 |
| youtube.com::video_playback          |                               5 |                                      0 |                             1 |                             0 |                                 10 |                           284 |

### J7

| truth                                |   bing.com::search_results_view |   developer.mozilla.org::document_view |   github.com::repository_view |   wikipedia.org::article_view |   youtube.com::search_results_view |   youtube.com::video_playback |
|:-------------------------------------|--------------------------------:|---------------------------------------:|------------------------------:|------------------------------:|-----------------------------------:|------------------------------:|
| bing.com::search_results_view        |                             213 |                                     13 |                            30 |                             8 |                                 23 |                            13 |
| developer.mozilla.org::document_view |                              11 |                                    230 |                             0 |                            59 |                                  0 |                             0 |
| github.com::repository_view          |                              17 |                                      5 |                           239 |                             9 |                                 16 |                            14 |
| wikipedia.org::article_view          |                               8 |                                    136 |                            11 |                           145 |                                  0 |                             0 |
| youtube.com::search_results_view     |                              16 |                                      0 |                             1 |                             0 |                                278 |                             5 |
| youtube.com::video_playback          |                               6 |                                      0 |                             4 |                             0 |                                  8 |                           282 |

## 工程审核与未验证范围

六项CUDA单元测试、170次权限拒绝、八臂20步烟测通过。独立sklearn核算120个点值及24个bootstrap值，最大误差分别0与0。修复版105个非J0模型权重逐位保持，原拟合和原预测哈希保留。

正式模型仅接受六个post数值，额外字段被拒绝；拟合和推理没有读取测试pre或评分标签。准备过程已有历史业务元数据，不能说研究者从未接触测试标签。观测为离线索引辅助post，不是全自动被动分段。既有物理身份检查不排除环境可预测性，也不是对未登记实体的普遍无泄漏证明。

结果仅针对五个已见Extend部署的未见内容任务，不证明未见协议、配置、日期、外部DIRECT或现场攻击。本批VLESS无REALITY/Vision，SS cipher已登记，VMess auto最终security与AnyTLS内部状态仍有边界。机制条件是经验先验，不是精确K、隐状态完整恢复或因果识别。

本次没有新检索、冻结探针或更大头，没有减少业务标签；结果不应被解释为无标签配对SSL终于成功。旧B系列只有历史参照意义，新联合业务监督的标签曝光和路径不同。

## 停止决定与产物

固定主候选J4、全部八臂和六项家族已完成，正向通过0/6。本候选在此冻结，不自动追加lambda、温度、更多seed、分类头、检索诊断或E2。失败数值实现记录和业务结果都保留，不围绕某项差距修改主方法。

代码在eval/post_anchored_paired_training；最终机器结果在outputs/post-anchored-paired-training-extend/run-01/repair-v1。包含最终预测、完整指标、混淆矩阵、内容错误台账、bootstrap索引、修复来源、模型检查点、纯post模型、CUDA回放与独立审核。plan和outputs保持Git忽略，本次没有推送远端。
