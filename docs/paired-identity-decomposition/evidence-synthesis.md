# 代理关联研究的主张证据与边界

已有证据支持条件性用途，不支持关联普遍成功或普遍无用。当前最强攻击增量目标仍未完成；测量价值不能替代它，但分类负结果也不能抹去准确测量和对应建立的价值。不同批次、表示、监督权限和区间家族分别列出，不构造成跨实验F1提升曲线。

## AH 证据

范围：0916，240访问，30个全局内容；SS/VLESS historical deployments。

任务与表示：source classifier; statistical/decision calibration；157-dimensional visit statistics。对应粒度：exact visits vs cyclic donors vs content-deployment centers。

权限：both sides and labels within training content; post-only inference。

支持：C improves B/D; F improves C; F/G/H do not establish exact identity advantage。

边界：No stable external transfer or pairing necessity theorem。

来源：[原报告](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/0916-A-H-mechanism-evidence-synthesis.md)；机器证据与哈希见evidence-index.json。

分类器：fixed linear source classifier, reused across B/C/D/F/G/H; separate post E。统计：95% uncorrected content-bootstrap; no equivalence margin。观测分母：240；重复编号：[1, 2, 4, 5]。本轮不重训。

## AH-cross 证据

范围：0916，240访问，30个全局内容；SS/VLESS historical deployments。

任务与表示：source-only deployment to other deployment；157-dimensional visit statistics。对应粒度：exact vs content centers。

权限：only source deployment fits; global held-out contents; target post inference。

支持：Directional transfer benefits; not bidirectionally robust。

边界：Not externally blind, direct-to-proxy or protocol causal。

来源：[原报告](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/0916-source-calibration-cross-deployment-results.md)；机器证据与哈希见evidence-index.json。

分类器：same fixed linear source classifier and registered affine calibration。统计：Original two-direction comparisons; retained source report family and intervals。观测分母：240；重复编号：[1, 2, 4, 5]。本轮不重训。

## R-T 证据

范围：0916，120访问，30个全局内容；VLESS historical deployment。

任务与表示：six-business supervised / VICReg pretraining；strict record structure plus independent new-byte time。对应粒度：exclusive flow pairs vs same-content cross-repeat flows。

权限：supervised post; SSL side access by arm; global content folds。

支持：Record representation benefits; exact pair pretraining does not exceed strong supervised S2。

边界：Not semantic record matching or unseen deployment。

来源：[原报告](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/record-time-business-0916/formal-results.md)；机器证据与哈希见evidence-index.json。

分类器：two-branch 32-channel CNN flow encoder; 65->32->6 visit head。统计：2000 business-stratified content draws; uncorrected descriptive 95%; three fixed seeds。观测分母：120；重复编号：[1, 2, 4, 5]。本轮不重训。

## R-T-probe 证据

范围：0916，120访问，30个全局内容；same VLESS as R-T。

任务与表示：frozen small nonlinear heads；frozen flow embedding and visit pooling。对应粒度：same L1-L4 frozen source encoders and random control。

权限：training content heads only; no encoder updates; post test。

支持：Pair representation readable but below post-only/side SSL controls。

边界：Not evidence that all downstream nonlinear reads are impossible。

来源：[原报告](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/record-time-business-0916/localization/summary.md)；机器证据与哈希见evidence-index.json。

分类器：frozen same flow encoder; train-only 65->32->6 nonlinear head。统计：2000 business-stratified content draws; uncorrected descriptive 95%; fixed models。观测分母：120；重复编号：[1, 2, 4, 5]。本轮不重训。

## CB 证据

范围：0916，240访问，30个全局内容；SS/VLESS historical deployments。

任务与表示：limited pair calibration and extra pre content；seven-variable visit summaries。对应粒度：exact versus donor controls。

权限：C two sides; U pre and label only; U post isolated。

支持：Extra contents help small post baseline; stable advantage over extra raw pre not established。

边界：No quantified real capture/label savings。

来源：[原报告](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/paired-calibration-budget-0916/summary.md)；机器证据与哈希见evidence-index.json。

分类器：7->32 ReLU->6 MLP; fixed 1000 Adam steps。统计：Original family and model-conditional intervals from linked report; no new pooled test。观测分母：240；重复编号：[1, 2, 4, 5]。本轮不重训。

## FSC 证据

范围：0916，240访问，30个全局内容；SS/VLESS historical deployments。

任务与表示：cross-business missing-post augmentation；feasible seven-variable summary coordinates。对应粒度：exact vs group/cyclic; center and marginal also pair-derived。

权限：C other business pairs; U pre and labels; test real post。

支持：Paired beats raw and group in both deployments under original corrected families。

边界：No generally best generator or full-target reference superiority。

来源：[原报告](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/feasible-summary-calibration-0916/summary.md)；机器证据与哈希见evidence-index.json。

分类器：7->32 ReLU->6 MLP; fixed 1000 Adam steps。统计：10000 content draws; four primary comparisons; 98.75% Bonferroni intervals。观测分母：240；重复编号：[1, 2, 4, 5]。本轮不重训。

## Extend-v3 证据

范围：Extend，600访问，30个全局内容；SS/VLESS/Trojan/VMess/AnyTLS; Hy2 ineligible。

任务与表示：within-deployment missing-business-post augmentation；W six-dimensional / T seven-dimensional visit summaries。对应粒度：exact versus anonymous group; center/marginal still pair-based。

权限：same C and U pre/labels; U post forbidden; full-post reference separate。

支持：W five deployments and T four pass registered raw/group comparisons。

边界：Not six-protocol classification, unseen deployment or independence from pairing of marginal。

来源：[原报告](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/extend-calibration-20260930/v3-experiment-contract.md)；机器证据与哈希见evidence-index.json。

分类器：W 6 / T 7 ->32 ReLU->6 MLP, registered original budgets。统计：10000 business-stratified content draws; W family 10 and T family 8 separately。观测分母：W 600 / T four-deployment 480 subset；重复编号：[1, 2, 3, 4]。本轮不重训。

## Unified 证据

范围：Extend，600访问，30个全局内容；five eligible W deployments。

任务与表示：E1 shared model / E2 leave-one deployment；six-variable W numeric summary。对应粒度：paired augmentation vs group and raw pre mix。

权限：E1 mixed source post; E2 target unavailable; global content exclusion。

支持：Paired beats group but reliable increment over strong post mix not established。

边界：E2 is fitting-time exclusion, not researcher-blind external protocol test。

来源：[原报告](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/business-protocol-eval-extend/formal-results.md)；机器证据与哈希见evidence-index.json。

分类器：6->32 ReLU->6 MLP; E1/E2 shared weights; independent I0 control。统计：10000 content draws; E1 and E2 separate three-comparison families; not joint six-test guarantee。观测分母：600；重复编号：[1, 2, 3, 4]。本轮不重训。

## Probability 证据

范围：Extend，480访问，30个全局内容；four exclusive TCP deployments; qualified current configs。

任务与表示：conditional probability and information measurement；ten binned connection statistics。对应粒度：exact connection joint table vs content-side products。

权限：train-content kernels; content-held-out probability scores。

支持：Exact joint kernels improve declared probability scores。

边界：No business classifier benefit or full channel information / precise overhead K。

来源：[原报告](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/protocol-probability-drift/formal-report.md)；机器证据与哈希见evidence-index.json。

分类器：no business classifier; discrete conditional kernel。统计：10000 content draws; eight primary probability comparisons; no classifier endpoint。观测分母：480；重复编号：[1, 2, 3, 4]。本轮不重训。

## KSR 证据

范围：Extend，480访问，30个全局内容；SS AES-GCM / VLESS TCP TLS / Trojan TCP TLS / VMess WS TLS。

任务与表示：within-deployment post LR with kernel geometry regularization；96-dimensional marginal histograms。对应粒度：exact vs anonymous group and post-repeat covariance。

权限：same allowed training post labels; kernels use legal training pairs。

支持：No corrected advantage over fair strong L2 or group kernel。

边界：Not evidence of information-theoretically optimal post model。

来源：[原报告](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/kernel-sensitivity-regularization/formal-report.md)；机器证据与哈希见evidence-index.json。

分类器：96->6 multinomial LR; 582 parameters。统计：Twelve prespecified deployment-comparison family; pooled mean not a new test。观测分母：480；重复编号：[1, 2, 3, 4]。本轮不重训。

## DSR 证据

范围：Extend，480访问，30个全局内容；four TCP deployments。

任务与表示：drift-state group-risk regularization；96-dimensional marginal histograms。对应粒度：exact / group / post-state controls。

权限：nested contents; same post labels; selected zero controls retained。

支持：Positive candidates ran, all outer alpha zero; no new gain。

边界：Identical final predictions are not statistical equivalence proof。

来源：[原报告](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/drift-state-group-risk/complete-report-20261006.md)；机器证据与哈希见evidence-index.json。

分类器：96->6 multinomial LR; fixed state-risk candidates。统计：Original family and model-conditional intervals from linked report; no new pooled test。观测分母：480；重复编号：[1, 2, 3, 4]。本轮不重训。

## RW 证据

范围：Extend，480访问，30个全局内容；four TCP deployments。

任务与表示：cross-fitted task-aware fixed reweighting；96-dimensional marginal histograms。对应粒度：exact state vs group vs post-CE state。

权限：OOF train-only difficulty; test real post; fixed label-informed weights。

支持：Parameters/predictions changed but full gain criterion failed。

边界：Not label-free drift or evidence that constraints were ignored。

来源：[原报告](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/cross-fitted-drift-reweighting/complete-report-20261006.md)；机器证据与哈希见evidence-index.json。

分类器：96->6 multinomial LR; fixed OOF reweighting plus protection。统计：10000 content draws; three-comparison Bonferroni 98.333333%; by-deployment 95% descriptive。观测分母：480；重复编号：[1, 2, 3, 4]。本轮不重训。

## CT-v4 证据

范围：Extend，480访问，30个全局内容；four current qualified TCP configs。

任务与表示：auxiliary-business-calibrated deployment transfer；connection kernels to 96-dimensional visit marginal histograms。对应粒度：exact connection vs group product kernel。

权限：source full business library; target C four businesses; target U both sides forbidden。

支持：CT4 beats CT1/CT3 but below same-target-permission StrongPost。

边界：Not best single-side attack, target-free transfer or universally useless pairing。

来源：[原报告](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/calibrated-deployment-business-transfer/v4/detailed-final-report-20261007.md)；机器证据与哈希见evidence-index.json。

分类器：96->6 multinomial LR with frozen v4 numeric policy。统计：10000 content draws; three-comparison Bonferroni 98.333333%; fixed selected models。观测分母：480；重复编号：[1, 2, 3, 4]。本轮不重训。

## JA 证据

范围：Extend，480访问，30个全局内容；same four current TCP deployments as CT。

任务与表示：auxiliary calibration joint conditional-mean adaptation；96-dimensional visit marginal histograms。对应粒度：exact visit vs same-content full-donor mean。

权限：CT permissions unchanged; selected maps and classifiers frozen。

支持：JA1 beats raw pre but not group/block/StrongPost increment criteria。

边界：Cannot revoke CT connection result or equate affine mean with full joint probability model。

来源：[原报告](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/joint-affine-transfer/detailed-experiment-report-20261009.md)；机器证据与哈希见evidence-index.json。

分类器：96->6 multinomial LR with same v4 numeric policy。统计：10000 content draws; four-comparison Bonferroni 98.75%; fixed selected models。观测分母：480；重复编号：[1, 2, 3, 4]。本轮不重训。

## B-SSL 证据

范围：Extend，600访问，30个全局内容；five qualified W deployments。

任务与表示：conditioned pair SSL, frozen readouts and post fine-tuning；six-window-statistic encoder with train-only mechanism conditions。对应粒度：exact visit vs group; side-only and same-architecture controls。

权限：train-content cross-fit conditions; pre/conditions deleted for post inference。

支持：One of five primary comparisons positive; full main claim not met。

边界：High pair retrieval does not prove superior post representation or business gain。

来源：[原报告](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/mechanism-conditioned-ssl-extend/formal-results.md)；机器证据与哈希见evidence-index.json。

分类器：6->64->32 encoder plus 32->32->6 business head; 3782 deployed parameters。统计：10000 business-stratified content draws; five-comparison family, 99% intervals。观测分母：600；重复编号：[1, 2, 3, 4]。本轮不重训。

## J-post 证据

范围：Extend，600访问，30个全局内容；same five W deployments。

任务与表示：task-aware pre auxiliary decisions / post-anchored consistency；six-window-statistic encoder and post business head。对应粒度：exact visit vs group and post consistency。

权限：both train sides and labels; conditions train-only; post-only inference。

支持：J4 obtains no corrected positive interval among six primary comparisons。

边界：Not justification to change weight, labels or classifier without a new information object。

来源：[原报告](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/post-anchored-paired-training-extend/formal-results.md)；机器证据与哈希见evidence-index.json。

分类器：same 3782-parameter deployed encoder/head; train-only condition branch deleted。统计：Original six-comparison corrected family; fixed three seeds and models。观测分母：600；重复编号：[1, 2, 3, 4]。本轮不重训。

## G-kernel 证据

范围：Extend，480访问，30个全局内容；four exclusive TCP deployments。

任务与表示：kernel-induced business probability distributions；connection kernels and 96-dimensional visit marginal histograms。对应粒度：exact connection vs anonymous content products。

权限：training content labels and kernels; frozen post probability decisions。

支持：Eight template-control contrasts positive; none of eight strong direct-post comparisons positive。

边界：Kernel score preservation is not competitive single-side attack performance。

来源：[原报告](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/drift-kernel-business/formal-report.md)；机器证据与哈希见evidence-index.json。

分类器：fixed kernel-induced six-class probabilities; direct-post probability and MLP controls。统计：Eight primary comparisons; additional eight strong-post comparisons kept separate。观测分母：480；重复编号：[1, 2, 3, 4]。本轮不重训。

## 不能再反复使用的解释

CT和JA已限制目标未覆盖业务两侧权限，不能只说目标post过于充分。RW确实改变参数和预测，不宜一概归为约束未使用。JA允许全矩阵，但仍没有完成强参照增量；这只关闭当前仿射摘要候选，不证明所有联合对象建模不可能。记录级输入曾产生明确表示收益，不能把它与配对SSL独立增量混为一谈。

## CT与统一模型的原主比较

以下直接读取封存机器表，区间家族不同，不合并检验。CT为三比较家族；统一模型E1和E2各自三比较，次要循环控制只给原普通区间。

| comparison | delta_F1_uncovered | CI95_low | CI95_high | CI98_333_low | CI98_333_high | primary_pass | delta_F1_aux | aux_CI95_low | aux_CI95_high | aux_practical_screen_pass |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CT4-StrongPost | -0.055234 | -0.086975 | -0.020118 | -0.093103 | -0.013149 | False | -0.001030 | -0.024936 | 0.023276 | True |
| CT4-CT1 | 0.134169 | 0.103041 | 0.167926 | 0.096370 | 0.175469 | True | 0.031066 | 0.012803 | 0.050593 | True |
| CT4-CT3 | 0.059369 | 0.022232 | 0.098594 | 0.012861 | 0.107516 | True | 0.019529 | 0.000811 | 0.038062 | True |

| experiment | contrast | primary | delta | low95 | high95 | adjusted_low | adjusted_high |
| --- | --- | --- | --- | --- | --- | --- | --- |
| E1 | M2-M0 | True | 0.008842 | -0.006699 | 0.026054 | -0.009673 | 0.030307 |
| E1 | M2-M1 | True | 0.105755 | 0.074828 | 0.133444 | 0.068472 | 0.139860 |
| E1 | M2-M3 | True | 0.069179 | 0.042114 | 0.097854 | 0.036770 | 0.104461 |
| E1 | M2-M4 | False | 0.073192 | 0.045781 | 0.103877 | nan | nan |
| E2 | M2-M0 | True | 0.003566 | -0.009556 | 0.016023 | -0.012454 | 0.018512 |
| E2 | M2-M1 | True | 0.028845 | -0.001987 | 0.056673 | -0.008945 | 0.062721 |
| E2 | M2-M3 | True | 0.038387 | 0.012182 | 0.066557 | 0.006266 | 0.071933 |
| E2 | M2-M4 | False | 0.036582 | 0.006599 | 0.067033 | nan | nan |

## 保留的总体主张

真实连接对应可以支持更准确的跨侧变换估计，并在部分受限迁移管线中优于原样入口与粗对应控制；在已研究的权限、表示和部署条件下，尚未形成稳定超过充分或适配强post参照的完整方案。内部内容隔离、代码追溯和大量模型不能替代外部验证，也不能消除同一内容长期反复开发造成的选择风险。
