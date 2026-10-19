# 前向决策空间漂移精炼源内先导完整报告



日期：2026-10-17。DA-FGAN1-Pilot v1。



程序完整完成；本轮只有固定48个源内任务，没有实际H/U评价。DA-P相对B0的ΔF1_U=0.683069个百分点，相对DA-G为-0.056602个百分点。预定源内推进屏通过=False。



## 1 研究问题与边界



本轮只调整原P-small的1/30映射槽：冻结原JA1全仿射、原B0尺度及正则t，训练96→8→96残差；最终仍是只读取post的96→6线性分类器。没有逆向pre恢复推理、没有概率融合、没有神经判别器或GAN极小极大训练；决策空间/有限矩是具体训练目标，不是协议语义或类间拓扑不变性的证明。



## 2 数据与权限



48任务=outer f0×四内折×四组织role_target×三业务遮蔽。每任务两个源144访问＋伪目标C48访问，共192不同训练访问；query24访问。跨任务合计24内容、384次不同query访问；5760逻辑预测包含五管线，不是5760个独立样本。训练18内容与query六内容无交叉，两侧/重复/内部flow随内容分折。



role_target用于组织，并不是查询部署：SS→VLESS、VLESS→Trojan、Trojan→VMess、VMess→SS。实际role_target被排除。本轮批准的源内query-pre仅在全部模型及分类post预测封存后读取，用于离线诊断；没有进入拟合、尺度、checkpoint或候选选择，实际目标H/U保持禁读。



G进程只接触独立训练边际与匿名同内容中心；与P共享原P-small真配锚点。因此P−G检验共同P-small之上的新增精确监督，不是整系统有无精确关联。



六类为Bing搜索、MDN文档、GitHub仓库、Wikipedia文章、YouTube搜索、YouTube播放；G0遮蔽GitHub/YouTube搜索，G1遮蔽Bing/Wikipedia，G2遮蔽MDN/YouTube播放。



## 3 四槽、尺度、零起点与数值基线



源post144行质量1/3、CORAL144行质量0.3、mapped-pre144行质量1/30、目标C-post48行质量1/3。全部槽质量合计1，每类1/6；带权CE不再除行数。原mapped-pre覆盖六类，而非只有U。修正只在该槽施加；其余三槽、标签、顺序、质量精确保留。



ZERO直接引用原B0，材料逐位相同；不以新拟合制造“模型逐位相同”。B0-R是同目标新数值求解对照，独立列出。原B0/eta/t已由历史研究选择，源内内容也被多次研究，本次不是新的外部盲测。



## 4 模型与固定配置



Q_feat由类别中心化B0权重SVD提取，秩≤5，不与6×5类别基Q_class混用。48角色有效秩分布：{5: 48}。正交误差最大5.995e-15；权重重构误差最大5.158e-15。



生成器1544参数：U1随机N(0,1/96)，d1=0，U2=0；seed20261017。三臂全部2000步Adam，lr0.0003、betas(0.9,0.999)、eps1e−8、clip范数5。没有网格、早停或checkpoint择优。模型全CUDA float64，禁AMP/TF32；最多32独立模型、8 streams、CUDA Graph，凸头4并发。



J=监督误差/d＋业务条件协方差差/d²＋源侧六类残差中心关系项＋0.1dev＋1e−4(||U1||²+||U2||²)。DA-P用真配Q空间目标；DA-G用同内容post中心与真实post边际协方差；Full-P仅将监督及协方差改为全96空间，其余项一致。类中心项是相对旧映射的软先验，不保证真实业务不变，本轮没有其独立消融。



最终LR：CE_mass＋0.0005(1+t)||W||²，bias不惩罚，统一零初始化；原W/c梯度≤1e−5，独立重放≤1e−10，迭代严格<2000、函数评价严格<10000。没有增加模型容量到H推理接口，亦没有读取任何H。



## 5 全部源内结果



| pipeline | F1_U | F1_C | F1_all | CE_U | CE_C | CE_all | Brier_U | Brier_C | Brier_all |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B0 | 0.720417 | 0.783976 | 0.762790 | 1.161592 | 0.669324 | 0.833413 | 0.509162 | 0.272811 | 0.351595 |
| B0-R | 0.720417 | 0.783976 | 0.762790 | 1.161458 | 0.669296 | 0.833350 | 0.509135 | 0.272870 | 0.351625 |
| DA-G | 0.727814 | 0.785274 | 0.766121 | 1.143984 | 0.693615 | 0.843738 | 0.496570 | 0.277627 | 0.350608 |
| DA-P | 0.727248 | 0.789551 | 0.768783 | 1.174942 | 0.690783 | 0.852170 | 0.500716 | 0.273801 | 0.349439 |
| Full-P | 0.726253 | 0.781925 | 0.763368 | 1.166128 | 0.672160 | 0.836816 | 0.505889 | 0.274354 | 0.351532 |



F1由完整六类CM得到，保留其他类别造成的FP；四内折先合并，再按四query部署×三遮蔽组等权。不是逐折F1平均，不是U二分类。CE越低越好，Brier为六类概率平方误差之和。



## 6 三项预定主比较



| reference | delta_F1_U_pp | CI95_pp | family_CI_pp | family_positive | delta_CE_U | delta_Brier_U |
| --- | --- | --- | --- | --- | --- | --- |
| B0 | 0.683069 | [-0.644181417404154, 2.1274594831354707] | [-0.9673141096918029, 2.4109332943134865] | False | 0.013350 | -0.008446 |
| DA-G | -0.056602 | [-1.9503383023391514, 1.9752777990165948] | [-2.40364041834289, 2.4593781435170428] | False | 0.030958 | 0.004147 |
| Full-P | 0.099471 | [-1.0084540703890925, 1.3243524586220279] | [-1.2165592897130793, 1.5830929313847801] | False | 0.008814 | -0.005173 |



10000次六业务分层共享全局内容簇bootstrap，seed20261017；每业务四内容抽四。三比较Bonferroni边际98.333333%区间，另报95%。独立NumPy重建与CUDA结果误差见最终验证。区间条件于固定模型，不能消除历史数据反复开发；本轮没有选参，亦未据结果删任务。



## 7 逐查询部署与业务



| pipeline | query_deployment | F1_U | F1_C | F1_all | CE_U | CE_C | CE_all | Brier_U | Brier_C | Brier_all |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B0 | shadowsocks | 0.701053 | 0.806403 | 0.771286 | 1.223187 | 0.766436 | 0.918686 | 0.539404 | 0.252860 | 0.348375 |
| B0 | trojan | 0.714807 | 0.790398 | 0.765201 | 1.022609 | 0.461786 | 0.648727 | 0.510660 | 0.237827 | 0.328771 |
| B0 | vless | 0.780847 | 0.786322 | 0.784497 | 1.058432 | 0.747501 | 0.851145 | 0.406559 | 0.303945 | 0.338150 |
| B0 | vmess | 0.684962 | 0.752781 | 0.730175 | 1.342141 | 0.701571 | 0.915094 | 0.580025 | 0.296614 | 0.391084 |
| B0-R | shadowsocks | 0.701053 | 0.806403 | 0.771286 | 1.223200 | 0.766949 | 0.919033 | 0.539441 | 0.252874 | 0.348396 |
| B0-R | trojan | 0.714807 | 0.790398 | 0.765201 | 1.022642 | 0.461869 | 0.648793 | 0.510620 | 0.237874 | 0.328789 |
| B0-R | vless | 0.780847 | 0.786322 | 0.784497 | 1.058081 | 0.746642 | 0.850455 | 0.406505 | 0.304080 | 0.338222 |
| B0-R | vmess | 0.684962 | 0.752781 | 0.730175 | 1.341907 | 0.701723 | 0.915118 | 0.579972 | 0.296653 | 0.391093 |
| DA-G | shadowsocks | 0.722834 | 0.788552 | 0.766646 | 1.185607 | 0.806907 | 0.933140 | 0.527559 | 0.265040 | 0.352546 |
| DA-G | trojan | 0.724941 | 0.806114 | 0.779056 | 0.997048 | 0.443846 | 0.628247 | 0.496728 | 0.228322 | 0.317790 |
| DA-G | vless | 0.769650 | 0.785798 | 0.780416 | 1.101935 | 0.816435 | 0.911602 | 0.397010 | 0.316274 | 0.343186 |
| DA-G | vmess | 0.693830 | 0.760632 | 0.738365 | 1.291343 | 0.707271 | 0.901962 | 0.564982 | 0.300872 | 0.388909 |
| DA-P | shadowsocks | 0.725499 | 0.812554 | 0.783536 | 1.189981 | 0.792250 | 0.924827 | 0.515332 | 0.260505 | 0.345447 |
| DA-P | trojan | 0.716866 | 0.802033 | 0.773644 | 1.021950 | 0.447800 | 0.639183 | 0.508038 | 0.233454 | 0.324982 |
| DA-P | vless | 0.784191 | 0.784501 | 0.784398 | 1.127164 | 0.842803 | 0.937590 | 0.401599 | 0.313459 | 0.342839 |
| DA-P | vmess | 0.682436 | 0.759115 | 0.733555 | 1.360673 | 0.680282 | 0.907079 | 0.577896 | 0.287785 | 0.384489 |
| Full-P | shadowsocks | 0.716222 | 0.800048 | 0.772106 | 1.256819 | 0.760306 | 0.925810 | 0.532269 | 0.254432 | 0.347044 |
| Full-P | trojan | 0.719847 | 0.793479 | 0.768935 | 1.017413 | 0.459597 | 0.645536 | 0.515137 | 0.237647 | 0.330144 |
| Full-P | vless | 0.792054 | 0.786868 | 0.788597 | 1.083301 | 0.778112 | 0.879842 | 0.403599 | 0.310989 | 0.341859 |
| Full-P | vmess | 0.676890 | 0.747304 | 0.723833 | 1.306978 | 0.690624 | 0.896076 | 0.572552 | 0.294347 | 0.387082 |



| pipeline | business | scope | F1 |
| --- | --- | --- | --- |
| B0 | bing.com::search_results_view | C | 0.757528 |
| B0 | bing.com::search_results_view | U | 0.805712 |
| B0 | developer.mozilla.org::document_view | C | 0.675088 |
| B0 | developer.mozilla.org::document_view | U | 0.529006 |
| B0 | github.com::repository_view | C | 0.909633 |
| B0 | github.com::repository_view | U | 0.826042 |
| B0 | wikipedia.org::article_view | C | 0.693313 |
| B0 | wikipedia.org::article_view | U | 0.534406 |
| B0 | youtube.com::search_results_view | C | 0.817017 |
| B0 | youtube.com::search_results_view | U | 0.805670 |
| B0 | youtube.com::video_playback | C | 0.851277 |
| B0 | youtube.com::video_playback | U | 0.821668 |
| B0-R | bing.com::search_results_view | C | 0.757528 |
| B0-R | bing.com::search_results_view | U | 0.805712 |
| B0-R | developer.mozilla.org::document_view | C | 0.675088 |
| B0-R | developer.mozilla.org::document_view | U | 0.529006 |
| B0-R | github.com::repository_view | C | 0.909633 |
| B0-R | github.com::repository_view | U | 0.826042 |
| B0-R | wikipedia.org::article_view | C | 0.693313 |
| B0-R | wikipedia.org::article_view | U | 0.534406 |
| B0-R | youtube.com::search_results_view | C | 0.817017 |
| B0-R | youtube.com::search_results_view | U | 0.805670 |
| B0-R | youtube.com::video_playback | C | 0.851277 |
| B0-R | youtube.com::video_playback | U | 0.821668 |
| DA-G | bing.com::search_results_view | C | 0.762652 |
| DA-G | bing.com::search_results_view | U | 0.745455 |
| DA-G | developer.mozilla.org::document_view | C | 0.667751 |
| DA-G | developer.mozilla.org::document_view | U | 0.557358 |
| DA-G | github.com::repository_view | C | 0.909087 |
| DA-G | github.com::repository_view | U | 0.843899 |
| DA-G | wikipedia.org::article_view | C | 0.699025 |
| DA-G | wikipedia.org::article_view | U | 0.546703 |
| DA-G | youtube.com::search_results_view | C | 0.795363 |
| DA-G | youtube.com::search_results_view | U | 0.850714 |
| DA-G | youtube.com::video_playback | C | 0.877766 |
| DA-G | youtube.com::video_playback | U | 0.822754 |
| DA-P | bing.com::search_results_view | C | 0.770980 |
| DA-P | bing.com::search_results_view | U | 0.772130 |
| DA-P | developer.mozilla.org::document_view | C | 0.679641 |
| DA-P | developer.mozilla.org::document_view | U | 0.550366 |
| DA-P | github.com::repository_view | C | 0.916503 |
| DA-P | github.com::repository_view | U | 0.835468 |
| DA-P | wikipedia.org::article_view | C | 0.697710 |
| DA-P | wikipedia.org::article_view | U | 0.549666 |
| DA-P | youtube.com::search_results_view | C | 0.807666 |
| DA-P | youtube.com::search_results_view | U | 0.817791 |
| DA-P | youtube.com::video_playback | C | 0.864804 |
| DA-P | youtube.com::video_playback | U | 0.838066 |
| Full-P | bing.com::search_results_view | C | 0.758057 |
| Full-P | bing.com::search_results_view | U | 0.793603 |
| Full-P | developer.mozilla.org::document_view | C | 0.664612 |
| Full-P | developer.mozilla.org::document_view | U | 0.533187 |
| Full-P | github.com::repository_view | C | 0.908826 |
| Full-P | github.com::repository_view | U | 0.833602 |
| Full-P | wikipedia.org::article_view | C | 0.686584 |
| Full-P | wikipedia.org::article_view | U | 0.550535 |
| Full-P | youtube.com::search_results_view | C | 0.807453 |
| Full-P | youtube.com::search_results_view | U | 0.833920 |
| Full-P | youtube.com::video_playback | C | 0.866018 |
| Full-P | youtube.com::video_playback | U | 0.812671 |



逐业务表按其作为U/C的上下文分开，不能混作同一业务单一分数。部署分项为描述性结果，不另外制造逐部署显著性家族。



## 8 C实践代价与推进判定



总体C ΔF1=0.557489个百分点，总体1个百分点门通过=True。



| delta_F1_C | passed | query_deployment |
| --- | --- | --- |
| 0.006151 | True | shadowsocks |
| 0.011635 | True | trojan |
| -0.001821 | True | vless |
| 0.006334 | True | vmess |



预定推进屏同时要求P相对B0/G的U-F1点估计为正、U-CE相对两者不恶化及C总体1pp/各部署2pp筛查。结果passed=False。它只是是否值得申请完整实验的探索性筛查，不是确认性成功或统计非劣效证明。



## 9 错误修复、新增错误及概率贡献



| reference | scope | flip | n | delta_CE | delta_Brier | CE_contribution |
| --- | --- | --- | --- | --- | --- | --- |
| B0 | C | both_correct | 625 | 0.003021 | 0.001428 | 0.002459 |
| B0 | C | both_wrong | 130 | 0.127779 | 0.012554 | 0.021629 |
| B0 | C | introduced | 5 | 0.287758 | 0.223231 | 0.001873 |
| B0 | C | repaired | 8 | -0.432155 | -0.360092 | -0.004502 |
| B0 | U | both_correct | 249 | -0.000759 | 0.000187 | -0.000492 |
| B0 | U | both_wrong | 122 | 0.056198 | -0.018480 | 0.017855 |
| B0 | U | introduced | 5 | 0.194823 | 0.170417 | 0.002537 |
| B0 | U | repaired | 8 | -0.314386 | -0.235908 | -0.006550 |
| B0-R | C | both_correct | 625 | 0.003015 | 0.001422 | 0.002454 |
| B0-R | C | both_wrong | 130 | 0.127973 | 0.012248 | 0.021662 |
| B0-R | C | introduced | 5 | 0.287999 | 0.223447 | 0.001875 |
| B0-R | C | repaired | 8 | -0.432283 | -0.360434 | -0.004503 |
| B0-R | U | both_correct | 249 | -0.000743 | 0.000200 | -0.000482 |
| B0-R | U | both_wrong | 122 | 0.056598 | -0.018433 | 0.017982 |
| B0-R | U | introduced | 5 | 0.194995 | 0.170606 | 0.002539 |
| B0-R | U | repaired | 8 | -0.314633 | -0.235828 | -0.006555 |
| DA-G | C | both_correct | 622 | -0.001569 | -0.000963 | -0.001270 |
| DA-G | C | both_wrong | 127 | 0.015920 | -0.000603 | 0.002633 |
| DA-G | C | introduced | 8 | 0.422609 | 0.340801 | 0.004402 |
| DA-G | C | repaired | 11 | -0.600145 | -0.453599 | -0.008596 |
| DA-G | U | both_correct | 249 | 0.001943 | 0.001519 | 0.001260 |
| DA-G | U | both_wrong | 118 | 0.087127 | 0.003739 | 0.026773 |
| DA-G | U | introduced | 9 | 0.370637 | 0.310357 | 0.008687 |
| DA-G | U | repaired | 8 | -0.276568 | -0.252557 | -0.005762 |
| Full-P | C | both_correct | 623 | 0.002836 | 0.001737 | 0.002301 |
| Full-P | C | both_wrong | 131 | 0.102634 | -0.002666 | 0.017507 |
| Full-P | C | introduced | 4 | 0.751751 | 0.569367 | 0.003915 |
| Full-P | C | repaired | 10 | -0.391610 | -0.343548 | -0.005099 |
| Full-P | U | both_correct | 251 | -0.000787 | 0.000250 | -0.000515 |
| Full-P | U | both_wrong | 121 | 0.047821 | -0.009238 | 0.015069 |
| Full-P | U | introduced | 6 | 0.819832 | 0.383751 | 0.012810 |
| Full-P | U | repaired | 6 | -1.187181 | -0.539015 | -0.018550 |



每参照U384、C768条角色暴露行，不是新增独立内容。修复与新增计数不是宏F1；共同正确/共同错误的概率变化也影响CE。



## 10 源内留出生成诊断



| pipeline | scope | Q_MSE | relative_logit_MSE | std_MSE | raw_MSE |
| --- | --- | --- | --- | --- | --- |
| B0 | C | 0.846003 | 6.841818 | 6.419333 | 0.000869 |
| B0 | U | 1.387400 | 10.432828 | 7.497088 | 0.001206 |
| DA-G | C | 1.730180 | 11.924702 | 6.462460 | 0.001283 |
| DA-G | U | 3.185137 | 21.869615 | 7.594152 | 0.001975 |
| DA-P | C | 1.389096 | 9.351187 | 6.440010 | 0.001199 |
| DA-P | U | 2.113003 | 15.478294 | 7.530386 | 0.001682 |
| Full-P | C | 0.813349 | 6.664808 | 1.373965 | 0.000865 |
| Full-P | U | 1.326420 | 10.180665 | 1.614666 | 0.001180 |



| pipeline | scope | mean_error | covariance_error |
| --- | --- | --- | --- |
| B0 | C | 0.346521 | 0.508601 |
| B0 | U | 0.839959 | 0.807841 |
| DA-G | C | 0.488555 | 19.163442 |
| DA-G | U | 1.820200 | 6.586906 |
| DA-P | C | 0.436682 | 17.544814 |
| DA-P | U | 1.075705 | 2.133939 |
| Full-P | C | 0.329271 | 0.465899 |
| Full-P | U | 0.782450 | 0.703633 |



B0在本节代表原前向映射的生成输出，不是用分类器概率当恢复结果。Q误差与相对logit误差权重不同；raw误差与std误差亦不可混同。诊断只使用新授权的源内留出pre；不是实际H恢复诊断。前两阶矩比较不足以证明完整条件分布逼真、协议语义或标签保持。



## 11 生成值的必要合法性边界



| pipeline | negative_fraction | minimum | maximum | block_mass_error_max |
| --- | --- | --- | --- | --- |
| B0 | 0.185515 | -0.253729 | 1.027615 | 0.000000 |
| DA-G | 0.245573 | -0.661239 | 1.627441 | 0.442762 |
| DA-P | 0.251565 | -0.724401 | 1.650950 | 0.312534 |
| Full-P | 0.249939 | -0.160047 | 1.039194 | 0.033281 |



原仿射和新视图均按原值报告，没有裁剪、投影或重新归一化。本轮生成的是训练协变量，不是合法TCP/协议流量生成器。十个raw块均值在合法直方图中是常量，未被伪装成协议风格判别维度。



## 12 训练轨迹与目标取舍



| pipeline | J0 | Jend | decreased | C_Q0 | C_Qend | C_std0 | C_stdend | residual_rms | std_max | clips | sup | cov | relation | dev_weighted | L2 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DA-G | 0.920542 | 0.288079 | 1.000000 | 0.763618 | 0.206312 | 5.502964 | 5.466443 | 0.259669 | 19.730620 | 120.458333 | 0.206312 | 0.070359 | 0.003804 | 0.005717 | 0.001887 |
| DA-P | 0.680424 | 0.163811 | 1.000000 | 0.523501 | 0.141610 | 5.378898 | 5.351650 | 0.218676 | 19.429116 | 126.500000 | 0.141610 | 0.013039 | 0.003255 | 0.004152 | 0.001755 |
| Full-P | 127.663823 | 0.797618 | 1.000000 | 0.523501 | 0.387609 | 5.378898 | 0.307771 | 0.844101 | 15.581212 | 102.875000 | 0.307771 | 0.066344 | 0.000972 | 0.419518 | 0.003014 |



训练C恢复目标的真配/组中心含义不同，不能按绝对大小排名。源内留出指标另表报告，不用训练损失代替泛化。2000步非凸路径没有被宣称全局最优；本轮没有根据梯度冲突更换损失。



## 13 数值、来源与CUDA成本



| pipeline | heads | accepted | max_iter | max_eval | max_gradient | max_objective_error | max_gradient_error |
| --- | --- | --- | --- | --- | --- | --- | --- |
| B0-R | 48 | 48 | 85 | 88 | 9.96222128e-06 | 8.32667268e-17 | 1.72157752e-16 |
| DA-G | 48 | 48 | 84 | 88 | 9.94717334e-06 | 8.32667268e-17 | 2.01620947e-16 |
| DA-P | 48 | 48 | 87 | 93 | 9.96730070e-06 | 1.11022302e-16 | 2.06961913e-16 |
| Full-P | 48 | 48 | 83 | 87 | 9.97789917e-06 | 1.11022302e-16 | 2.10339457e-16 |



正式生成144条路径、最终LR192个；B0/ZERO均为别名。工程重放另计。P1保守预计总活动0.4751小时，门2.4小时；截至报告生成活动约0.1916小时，保护3小时。最终精确累计以completion.json为准。



独立CM最大差0.000e+00，独立bootstrap最大差3.331e-16；32/8 CUDA重放、权限负例及数学测试见tests/engineering.parquet。无实际H/U读取，源内query-pre在predictions-complete之后开放。



| stage | seconds |
| --- | --- |
| inherited-parent-and-engineering-repair | 350.104746 |
| register | 14.105183 |
| prepare | 27.650401 |
| tests | 22.497454 |
| worker:generate,--cap,P,--which,pilot | 15.006899 |
| worker:generate,--cap,G,--which,pilot | 12.915303 |
| worker:fit,--which,pilot | 13.389195 |
| worker:generate,--cap,P,--which,rest | 57.662333 |
| worker:generate,--cap,G,--which,rest | 31.375744 |
| worker:fit,--which,rest | 93.935138 |
| evaluate:seal | 11.592303 |
| evaluate:predict | 13.316900 |
| evaluate:diagnose | 16.043368 |
| score | 10.172185 |



## 14 结项与后续边界



预定源内筛查未通过，按合同停止当前配置，不自动启动完整H、不扩权重或步数搜索。



整体效果、精确监督增量、决策空间聚焦、类中心先验的独立贡献必须分开。第一版无类中心项独立消融；即使结果正向也不能宣称物理不变性成立。若P未优于Full-P，不能说全空间方向均无用；若P未优于G，也不能把更多源pre材料的收益归因精确身份。



## 15 追溯



[实施计划](F:/Program/VSCode/MyGit/ProxyAnalysis/plan/DA-FGAN1-forward-decision-space-pilot-plan-20261017.md)；[代码](F:/Program/VSCode/MyGit/ProxyAnalysis/eval/decision_aware_forward_drift_r3/driver.py)；[运行目录](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/decision-aware-forward-drift-20261017/pilot-03)。原Full NER1、ST1、JA、P-small模型与原结果未修改。
