# 辅助业务校准迁移实验修复版结果

日期：2026年10月6日。四部署、六业务、30全局内容、480访问、23566连接对。目标四类提供配对校准，目标另两类训练pre/post均禁止使用；测试仅输入post直方图。

## 优化修复

第四版仅将第三版全部主臂的预算统一改为2000次迭代和10000次优化函数评价，保留原CE、W的L2、预条件化、原梯度及重放精度门。迭代资格同步修订为小于2000；三版旧主模型不混用，14700模型按本版政策产生，300先导计入内层预算。复用680旧诊断，另做2次确定性重复和4次合成拟合。预算扩大不代表配对业务假设必然通过。

## 判定

| all_three_primary_pass | aux_pooled_screen_pass | conditional_on_fixed_selected_models | external_validation | independent_contents | registered_attack_increment_and_practical_screen_pass | statistical_noninferiority_claimed | worst_target_aux_gap | worst_target_aux_screen_pass |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| False | True | True | False | 30 | False | False | -0.017853 | True |


## 主要方法成绩

| arm | F1_all | accuracy | CE_nats | Brier | CE_bits | F1_uncovered | F1_aux | worst_target_F1_uncovered |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CT0 | 0.729823 | 0.757639 | 1.164652 | 0.393340 | 1.680238 | 0.587232 | 0.801119 | 0.260141 |
| CT1 | 0.720086 | 0.746528 | 1.210007 | 0.412770 | 1.745671 | 0.583306 | 0.788476 | 0.273430 |
| CT2 | 0.804617 | 0.807639 | 0.675111 | 0.299617 | 0.973979 | 0.772708 | 0.820571 | 0.660738 |
| CT3 | 0.752710 | 0.768750 | 0.886175 | 0.355438 | 1.278480 | 0.658105 | 0.800012 | 0.468831 |
| CT4 | 0.785519 | 0.793750 | 0.830137 | 0.316541 | 1.197635 | 0.717475 | 0.819541 | 0.603013 |
| CT5 | 0.812449 | 0.812500 | 0.761202 | 0.299842 | 1.098182 | 0.812449 | 0.812449 | 0.766246 |
| StrongPost | 0.804617 | 0.807639 | 0.675111 | 0.299617 | 0.973979 | 0.772708 | 0.820571 | 0.660738 |


## 三项主要比较

| comparison | delta_F1_uncovered | CI95_low | CI95_high | CI98_333_low | CI98_333_high | primary_pass | delta_F1_aux | aux_CI95_low | aux_CI95_high | aux_practical_screen_pass |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CT4-StrongPost | -0.055234 | -0.086975 | -0.020118 | -0.093103 | -0.013149 | False | -0.001030 | -0.024936 | 0.023276 | True |
| CT4-CT1 | 0.134169 | 0.103041 | 0.167926 | 0.096370 | 0.175469 | True | 0.031066 | 0.012803 | 0.050593 | True |
| CT4-CT3 | 0.059369 | 0.022232 | 0.098594 | 0.012861 | 0.107516 | True | 0.019529 | 0.000811 | 0.038062 | True |


## 各目标部署

| target | arm | F1_all | accuracy | CE_nats | Brier | CE_bits | F1_uncovered | F1_aux |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| shadowsocks | CT0 | 0.599492 | 0.661111 | 1.947388 | 0.570268 | 2.809487 | 0.260141 | 0.769168 |
| shadowsocks | CT1 | 0.588144 | 0.647222 | 1.858798 | 0.560897 | 2.681678 | 0.273430 | 0.745500 |
| shadowsocks | CT2 | 0.749149 | 0.755556 | 0.874065 | 0.380930 | 1.261010 | 0.660738 | 0.793354 |
| shadowsocks | CT3 | 0.675539 | 0.705556 | 1.218421 | 0.453418 | 1.757810 | 0.468831 | 0.778893 |
| shadowsocks | CT4 | 0.740926 | 0.755556 | 0.945498 | 0.373907 | 1.364065 | 0.603013 | 0.809882 |
| shadowsocks | CT5 | 0.852144 | 0.850000 | 0.583730 | 0.226160 | 0.842144 | 0.852144 | 0.852144 |
| shadowsocks | StrongPost | 0.749149 | 0.755556 | 0.874065 | 0.380930 | 1.261010 | 0.660738 | 0.793354 |
| trojan | CT0 | 0.845755 | 0.847222 | 0.427787 | 0.225403 | 0.617165 | 0.830122 | 0.853572 |
| trojan | CT1 | 0.815495 | 0.816667 | 0.563792 | 0.278411 | 0.813379 | 0.796327 | 0.825079 |
| trojan | CT2 | 0.868673 | 0.869444 | 0.396980 | 0.215725 | 0.572720 | 0.865599 | 0.870210 |
| trojan | CT3 | 0.833496 | 0.836111 | 0.420375 | 0.235784 | 0.606473 | 0.807239 | 0.846624 |
| trojan | CT4 | 0.869110 | 0.869444 | 0.380307 | 0.202936 | 0.548666 | 0.856345 | 0.875493 |
| trojan | CT5 | 0.831921 | 0.833333 | 0.663361 | 0.262865 | 0.957028 | 0.831921 | 0.831921 |
| trojan | StrongPost | 0.868673 | 0.869444 | 0.396980 | 0.215725 | 0.572720 | 0.865599 | 0.870210 |
| vless | CT0 | 0.815686 | 0.816667 | 0.755761 | 0.300135 | 1.090333 | 0.804263 | 0.821397 |
| vless | CT1 | 0.814352 | 0.813889 | 0.785170 | 0.310814 | 1.132761 | 0.805871 | 0.818593 |
| vless | CT2 | 0.806377 | 0.805556 | 0.642466 | 0.293255 | 0.926883 | 0.810425 | 0.804353 |
| vless | CT3 | 0.779464 | 0.780556 | 0.826777 | 0.341092 | 1.192787 | 0.761421 | 0.788485 |
| vless | CT4 | 0.783661 | 0.786111 | 0.798353 | 0.319134 | 1.151779 | 0.758431 | 0.796275 |
| vless | CT5 | 0.799486 | 0.800000 | 0.750140 | 0.315853 | 1.082223 | 0.799486 | 0.799486 |
| vless | StrongPost | 0.806377 | 0.805556 | 0.642466 | 0.293255 | 0.926883 | 0.810425 | 0.804353 |
| vmess | CT0 | 0.658360 | 0.705556 | 1.527674 | 0.477555 | 2.203968 | 0.454403 | 0.760338 |
| vmess | CT1 | 0.662351 | 0.708333 | 1.632268 | 0.500958 | 2.354864 | 0.457594 | 0.764730 |
| vmess | CT2 | 0.794269 | 0.800000 | 0.786933 | 0.308556 | 1.135305 | 0.754071 | 0.814368 |
| vmess | CT3 | 0.722341 | 0.752778 | 1.079125 | 0.391458 | 1.556848 | 0.594930 | 0.786046 |
| vmess | CT4 | 0.748380 | 0.763889 | 1.196393 | 0.370188 | 1.726030 | 0.652109 | 0.796515 |
| vmess | CT5 | 0.766246 | 0.766667 | 1.047577 | 0.394490 | 1.511334 | 0.766246 | 0.766246 |
| vmess | StrongPost | 0.794269 | 0.800000 | 0.786933 | 0.308556 | 1.135305 | 0.754071 | 0.814368 |


## 全部十二场景

| target | group | arm | F1_all | accuracy | CE_nats | Brier | CE_bits | F1_uncovered | F1_aux |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| shadowsocks | G0 | CT0 | 0.660366 | 0.675000 | 1.635564 | 0.523092 | 2.359619 | 0.473545 | 0.753776 |
| shadowsocks | G0 | CT1 | 0.661914 | 0.683333 | 1.417072 | 0.479720 | 2.044402 | 0.533333 | 0.726205 |
| shadowsocks | G0 | CT2 | 0.781391 | 0.783333 | 0.856995 | 0.346557 | 1.236383 | 0.749576 | 0.797298 |
| shadowsocks | G0 | CT3 | 0.722696 | 0.725000 | 1.090941 | 0.417165 | 1.573895 | 0.642857 | 0.762616 |
| shadowsocks | G0 | CT4 | 0.791113 | 0.791667 | 0.644172 | 0.282941 | 0.929344 | 0.775745 | 0.798797 |
| shadowsocks | G0 | CT5 | 0.852144 | 0.850000 | 0.583730 | 0.226160 | 0.842144 | 0.962179 | 0.797127 |
| shadowsocks | G0 | StrongPost | 0.781391 | 0.783333 | 0.856995 | 0.346557 | 1.236383 | 0.749576 | 0.797298 |
| shadowsocks | G1 | CT0 | 0.628416 | 0.691667 | 2.104775 | 0.550143 | 3.036548 | 0.259259 | 0.812994 |
| shadowsocks | G1 | CT1 | 0.601072 | 0.666667 | 2.288812 | 0.577458 | 3.302058 | 0.200000 | 0.801608 |
| shadowsocks | G1 | CT2 | 0.789463 | 0.791667 | 0.728036 | 0.312746 | 1.050334 | 0.732639 | 0.817875 |
| shadowsocks | G1 | CT3 | 0.726764 | 0.750000 | 1.318897 | 0.422394 | 1.902766 | 0.530303 | 0.824994 |
| shadowsocks | G1 | CT4 | 0.718052 | 0.741667 | 1.088381 | 0.414769 | 1.570201 | 0.496429 | 0.828864 |
| shadowsocks | G1 | CT5 | 0.852144 | 0.850000 | 0.583730 | 0.226160 | 0.842144 | 0.773115 | 0.891659 |
| shadowsocks | G1 | StrongPost | 0.789463 | 0.791667 | 0.728036 | 0.312746 | 1.050334 | 0.732639 | 0.817875 |
| shadowsocks | G2 | CT0 | 0.509695 | 0.616667 | 2.101826 | 0.637570 | 3.032293 | 0.047619 | 0.740733 |
| shadowsocks | G2 | CT1 | 0.501445 | 0.591667 | 1.870509 | 0.625512 | 2.698574 | 0.086957 | 0.708689 |
| shadowsocks | G2 | CT2 | 0.676593 | 0.691667 | 1.037165 | 0.483488 | 1.496312 | 0.500000 | 0.764889 |
| shadowsocks | G2 | CT3 | 0.577158 | 0.641667 | 1.245427 | 0.520694 | 1.796771 | 0.233333 | 0.749070 |
| shadowsocks | G2 | CT4 | 0.713613 | 0.733333 | 1.103940 | 0.424012 | 1.592649 | 0.536866 | 0.801986 |
| shadowsocks | G2 | CT5 | 0.852144 | 0.850000 | 0.583730 | 0.226160 | 0.842144 | 0.821138 | 0.867647 |
| shadowsocks | G2 | StrongPost | 0.676593 | 0.691667 | 1.037165 | 0.483488 | 1.496312 | 0.500000 | 0.764889 |
| trojan | G0 | CT0 | 0.859085 | 0.858333 | 0.389917 | 0.220089 | 0.562532 | 0.897436 | 0.839910 |
| trojan | G0 | CT1 | 0.809006 | 0.808333 | 0.577903 | 0.283412 | 0.833738 | 0.841303 | 0.792857 |
| trojan | G0 | CT2 | 0.865895 | 0.866667 | 0.374703 | 0.209737 | 0.540581 | 0.912805 | 0.842440 |
| trojan | G0 | CT3 | 0.849543 | 0.850000 | 0.423157 | 0.232231 | 0.610486 | 0.889634 | 0.829498 |
| trojan | G0 | CT4 | 0.857394 | 0.858333 | 0.379359 | 0.214919 | 0.547299 | 0.875598 | 0.848292 |
| trojan | G0 | CT5 | 0.831921 | 0.833333 | 0.663361 | 0.262865 | 0.957028 | 0.914024 | 0.790870 |
| trojan | G0 | StrongPost | 0.865895 | 0.866667 | 0.374703 | 0.209737 | 0.540581 | 0.912805 | 0.842440 |
| trojan | G1 | CT0 | 0.841974 | 0.841667 | 0.488852 | 0.236595 | 0.705264 | 0.848348 | 0.838786 |
| trojan | G1 | CT1 | 0.831741 | 0.833333 | 0.492236 | 0.259862 | 0.710146 | 0.794737 | 0.850243 |
| trojan | G1 | CT2 | 0.884263 | 0.883333 | 0.425643 | 0.215420 | 0.614073 | 0.895357 | 0.878716 |
| trojan | G1 | CT3 | 0.840185 | 0.841667 | 0.433279 | 0.234514 | 0.625090 | 0.818797 | 0.850879 |
| trojan | G1 | CT4 | 0.849741 | 0.850000 | 0.394321 | 0.221301 | 0.568884 | 0.805405 | 0.871909 |
| trojan | G1 | CT5 | 0.831921 | 0.833333 | 0.663361 | 0.262865 | 0.957028 | 0.814634 | 0.840565 |
| trojan | G1 | StrongPost | 0.884263 | 0.883333 | 0.425643 | 0.215420 | 0.614073 | 0.895357 | 0.878716 |
| trojan | G2 | CT0 | 0.836207 | 0.841667 | 0.404591 | 0.219525 | 0.583701 | 0.744582 | 0.882019 |
| trojan | G2 | CT1 | 0.805739 | 0.808333 | 0.621236 | 0.291960 | 0.896254 | 0.752941 | 0.832138 |
| trojan | G2 | CT2 | 0.855860 | 0.858333 | 0.390593 | 0.222017 | 0.563507 | 0.788635 | 0.889473 |
| trojan | G2 | CT3 | 0.810759 | 0.816667 | 0.404689 | 0.240606 | 0.583843 | 0.713287 | 0.859494 |
| trojan | G2 | CT4 | 0.900194 | 0.900000 | 0.367240 | 0.172589 | 0.529816 | 0.888031 | 0.906276 |
| trojan | G2 | CT5 | 0.831921 | 0.833333 | 0.663361 | 0.262865 | 0.957028 | 0.767105 | 0.864329 |
| trojan | G2 | StrongPost | 0.855860 | 0.858333 | 0.390593 | 0.222017 | 0.563507 | 0.788635 | 0.889473 |
| vless | G0 | CT0 | 0.824833 | 0.825000 | 0.697572 | 0.309840 | 1.006383 | 0.836257 | 0.819121 |
| vless | G0 | CT1 | 0.818425 | 0.816667 | 0.715093 | 0.305261 | 1.031662 | 0.864865 | 0.795205 |
| vless | G0 | CT2 | 0.819103 | 0.816667 | 0.619413 | 0.290462 | 0.893624 | 0.836257 | 0.810526 |
| vless | G0 | CT3 | 0.791109 | 0.791667 | 0.698658 | 0.309975 | 1.007950 | 0.783784 | 0.794771 |
| vless | G0 | CT4 | 0.807163 | 0.808333 | 0.635886 | 0.292799 | 0.917389 | 0.807326 | 0.807082 |
| vless | G0 | CT5 | 0.799486 | 0.800000 | 0.750140 | 0.315853 | 1.082223 | 0.820513 | 0.788972 |
| vless | G0 | StrongPost | 0.819103 | 0.816667 | 0.619413 | 0.290462 | 0.893624 | 0.836257 | 0.810526 |
| vless | G1 | CT0 | 0.815839 | 0.816667 | 0.841899 | 0.271481 | 1.214603 | 0.771693 | 0.837912 |
| vless | G1 | CT1 | 0.830076 | 0.833333 | 0.888210 | 0.303317 | 1.281416 | 0.773994 | 0.858117 |
| vless | G1 | CT2 | 0.798994 | 0.800000 | 0.670388 | 0.291443 | 0.967165 | 0.767105 | 0.814939 |
| vless | G1 | CT3 | 0.781774 | 0.783333 | 0.853488 | 0.321540 | 1.231323 | 0.736842 | 0.804239 |
| vless | G1 | CT4 | 0.770371 | 0.775000 | 1.008401 | 0.334675 | 1.454815 | 0.709635 | 0.800739 |
| vless | G1 | CT5 | 0.799486 | 0.800000 | 0.750140 | 0.315853 | 1.082223 | 0.757143 | 0.820657 |
| vless | G1 | StrongPost | 0.798994 | 0.800000 | 0.670388 | 0.291443 | 0.967165 | 0.767105 | 0.814939 |
| vless | G2 | CT0 | 0.806385 | 0.808333 | 0.727813 | 0.319084 | 1.050013 | 0.804839 | 0.807158 |
| vless | G2 | CT1 | 0.794555 | 0.791667 | 0.752206 | 0.323864 | 1.085204 | 0.778755 | 0.802455 |
| vless | G2 | CT2 | 0.801034 | 0.800000 | 0.637598 | 0.297860 | 0.919859 | 0.827913 | 0.787594 |
| vless | G2 | CT3 | 0.765509 | 0.766667 | 0.928184 | 0.391761 | 1.339087 | 0.763636 | 0.766445 |
| vless | G2 | CT4 | 0.773448 | 0.775000 | 0.750772 | 0.329928 | 1.083134 | 0.758333 | 0.781005 |
| vless | G2 | CT5 | 0.799486 | 0.800000 | 0.750140 | 0.315853 | 1.082223 | 0.820802 | 0.788828 |
| vless | G2 | StrongPost | 0.801034 | 0.800000 | 0.637598 | 0.297860 | 0.919859 | 0.827913 | 0.787594 |
| vmess | G0 | CT0 | 0.715108 | 0.716667 | 1.181982 | 0.436627 | 1.705239 | 0.711470 | 0.716927 |
| vmess | G0 | CT1 | 0.733545 | 0.733333 | 1.171878 | 0.433332 | 1.690662 | 0.732432 | 0.734101 |
| vmess | G0 | CT2 | 0.786353 | 0.783333 | 0.848564 | 0.318572 | 1.224219 | 0.839024 | 0.760017 |
| vmess | G0 | CT3 | 0.789199 | 0.791667 | 0.784140 | 0.319636 | 1.131274 | 0.884467 | 0.741565 |
| vmess | G0 | CT4 | 0.791870 | 0.791667 | 1.080114 | 0.332912 | 1.558276 | 0.820802 | 0.777405 |
| vmess | G0 | CT5 | 0.766246 | 0.766667 | 1.047577 | 0.394490 | 1.511334 | 0.825000 | 0.736869 |
| vmess | G0 | StrongPost | 0.786353 | 0.783333 | 0.848564 | 0.318572 | 1.224219 | 0.839024 | 0.760017 |
| vmess | G1 | CT0 | 0.585385 | 0.666667 | 2.095708 | 0.549890 | 3.023468 | 0.178054 | 0.789050 |
| vmess | G1 | CT1 | 0.586789 | 0.666667 | 2.184127 | 0.589804 | 3.151030 | 0.166667 | 0.796850 |
| vmess | G1 | CT2 | 0.848622 | 0.850000 | 0.626187 | 0.249251 | 0.903396 | 0.777090 | 0.884388 |
| vmess | G1 | CT3 | 0.694744 | 0.725000 | 1.107415 | 0.429303 | 1.597662 | 0.450323 | 0.816954 |
| vmess | G1 | CT4 | 0.753906 | 0.766667 | 1.155379 | 0.377447 | 1.666859 | 0.581840 | 0.839938 |
| vmess | G1 | CT5 | 0.766246 | 0.766667 | 1.047577 | 0.394490 | 1.511334 | 0.718182 | 0.790278 |
| vmess | G1 | StrongPost | 0.848622 | 0.850000 | 0.626187 | 0.249251 | 0.903396 | 0.777090 | 0.884388 |
| vmess | G2 | CT0 | 0.674586 | 0.733333 | 1.305332 | 0.446147 | 1.883197 | 0.473684 | 0.775037 |
| vmess | G2 | CT1 | 0.666721 | 0.725000 | 1.540798 | 0.479740 | 2.222902 | 0.473684 | 0.763239 |
| vmess | G2 | CT2 | 0.747833 | 0.766667 | 0.886049 | 0.357846 | 1.278298 | 0.646098 | 0.798700 |
| vmess | G2 | CT3 | 0.683080 | 0.741667 | 1.345821 | 0.425434 | 1.941609 | 0.450000 | 0.799619 |
| vmess | G2 | CT4 | 0.699363 | 0.733333 | 1.353685 | 0.400204 | 1.952955 | 0.553684 | 0.772202 |
| vmess | G2 | CT5 | 0.766246 | 0.766667 | 1.047577 | 0.394490 | 1.511334 | 0.755556 | 0.771591 |
| vmess | G2 | StrongPost | 0.747833 | 0.766667 | 0.886049 | 0.357846 | 1.278298 | 0.646098 | 0.798700 |


## 完整六类分项

| target | group | arm | label_id | F1 | precision | recall | support |
| --- | --- | --- | --- | --- | --- | --- | --- |
| shadowsocks | G0 | CT0 | bing.com::search_results_view | 0.769231 | 0.789474 | 0.750000 | 20 |
| shadowsocks | G0 | CT0 | developer.mozilla.org::document_view | 0.780488 | 0.761905 | 0.800000 | 20 |
| shadowsocks | G0 | CT0 | github.com::repository_view | 0.518519 | 1.000000 | 0.350000 | 20 |
| shadowsocks | G0 | CT0 | wikipedia.org::article_view | 0.850000 | 0.850000 | 0.850000 | 20 |
| shadowsocks | G0 | CT0 | youtube.com::search_results_view | 0.428571 | 0.750000 | 0.300000 | 20 |
| shadowsocks | G0 | CT0 | youtube.com::video_playback | 0.615385 | 0.444444 | 1.000000 | 20 |
| shadowsocks | G0 | CT1 | bing.com::search_results_view | 0.736842 | 0.777778 | 0.700000 | 20 |
| shadowsocks | G0 | CT1 | developer.mozilla.org::document_view | 0.711111 | 0.640000 | 0.800000 | 20 |
| shadowsocks | G0 | CT1 | github.com::repository_view | 0.400000 | 1.000000 | 0.250000 | 20 |
| shadowsocks | G0 | CT1 | wikipedia.org::article_view | 0.765957 | 0.666667 | 0.900000 | 20 |
| shadowsocks | G0 | CT1 | youtube.com::search_results_view | 0.666667 | 1.000000 | 0.500000 | 20 |
| shadowsocks | G0 | CT1 | youtube.com::video_playback | 0.690909 | 0.542857 | 0.950000 | 20 |
| shadowsocks | G0 | CT2 | bing.com::search_results_view | 0.789474 | 0.833333 | 0.750000 | 20 |
| shadowsocks | G0 | CT2 | developer.mozilla.org::document_view | 0.780488 | 0.761905 | 0.800000 | 20 |
| shadowsocks | G0 | CT2 | github.com::repository_view | 0.709677 | 1.000000 | 0.550000 | 20 |
| shadowsocks | G0 | CT2 | wikipedia.org::article_view | 0.850000 | 0.850000 | 0.850000 | 20 |
| shadowsocks | G0 | CT2 | youtube.com::search_results_view | 0.789474 | 0.833333 | 0.750000 | 20 |
| shadowsocks | G0 | CT2 | youtube.com::video_playback | 0.769231 | 0.625000 | 1.000000 | 20 |
| shadowsocks | G0 | CT3 | bing.com::search_results_view | 0.789474 | 0.833333 | 0.750000 | 20 |
| shadowsocks | G0 | CT3 | developer.mozilla.org::document_view | 0.761905 | 0.727273 | 0.800000 | 20 |
| shadowsocks | G0 | CT3 | github.com::repository_view | 0.600000 | 0.900000 | 0.450000 | 20 |
| shadowsocks | G0 | CT3 | wikipedia.org::article_view | 0.820513 | 0.842105 | 0.800000 | 20 |
| shadowsocks | G0 | CT3 | youtube.com::search_results_view | 0.685714 | 0.800000 | 0.600000 | 20 |
| shadowsocks | G0 | CT3 | youtube.com::video_playback | 0.678571 | 0.527778 | 0.950000 | 20 |
| shadowsocks | G0 | CT4 | bing.com::search_results_view | 0.820513 | 0.842105 | 0.800000 | 20 |
| shadowsocks | G0 | CT4 | developer.mozilla.org::document_view | 0.780488 | 0.761905 | 0.800000 | 20 |
| shadowsocks | G0 | CT4 | github.com::repository_view | 0.829268 | 0.809524 | 0.850000 | 20 |
| shadowsocks | G0 | CT4 | wikipedia.org::article_view | 0.744186 | 0.695652 | 0.800000 | 20 |
| shadowsocks | G0 | CT4 | youtube.com::search_results_view | 0.722222 | 0.812500 | 0.650000 | 20 |
| shadowsocks | G0 | CT4 | youtube.com::video_playback | 0.850000 | 0.850000 | 0.850000 | 20 |
| shadowsocks | G0 | CT5 | bing.com::search_results_view | 0.756757 | 0.823529 | 0.700000 | 20 |
| shadowsocks | G0 | CT5 | developer.mozilla.org::document_view | 0.666667 | 0.600000 | 0.750000 | 20 |
| shadowsocks | G0 | CT5 | github.com::repository_view | 0.974359 | 1.000000 | 0.950000 | 20 |
| shadowsocks | G0 | CT5 | wikipedia.org::article_view | 0.789474 | 0.833333 | 0.750000 | 20 |
| shadowsocks | G0 | CT5 | youtube.com::search_results_view | 0.950000 | 0.950000 | 0.950000 | 20 |
| shadowsocks | G0 | CT5 | youtube.com::video_playback | 0.975610 | 0.952381 | 1.000000 | 20 |
| shadowsocks | G0 | StrongPost | bing.com::search_results_view | 0.789474 | 0.833333 | 0.750000 | 20 |
| shadowsocks | G0 | StrongPost | developer.mozilla.org::document_view | 0.780488 | 0.761905 | 0.800000 | 20 |
| shadowsocks | G0 | StrongPost | github.com::repository_view | 0.709677 | 1.000000 | 0.550000 | 20 |
| shadowsocks | G0 | StrongPost | wikipedia.org::article_view | 0.850000 | 0.850000 | 0.850000 | 20 |
| shadowsocks | G0 | StrongPost | youtube.com::search_results_view | 0.789474 | 0.833333 | 0.750000 | 20 |
| shadowsocks | G0 | StrongPost | youtube.com::video_playback | 0.769231 | 0.625000 | 1.000000 | 20 |
| shadowsocks | G1 | CT0 | bing.com::search_results_view | 0.518519 | 1.000000 | 0.350000 | 20 |
| shadowsocks | G1 | CT0 | developer.mozilla.org::document_view | 0.571429 | 0.418605 | 0.900000 | 20 |
| shadowsocks | G1 | CT0 | github.com::repository_view | 0.952381 | 0.909091 | 1.000000 | 20 |
| shadowsocks | G1 | CT0 | wikipedia.org::article_view | 0.000000 | 0.000000 | 0.000000 | 20 |
| shadowsocks | G1 | CT0 | youtube.com::search_results_view | 0.883721 | 0.826087 | 0.950000 | 20 |
| shadowsocks | G1 | CT0 | youtube.com::video_playback | 0.844444 | 0.760000 | 0.950000 | 20 |
| shadowsocks | G1 | CT1 | bing.com::search_results_view | 0.400000 | 1.000000 | 0.250000 | 20 |
| shadowsocks | G1 | CT1 | developer.mozilla.org::document_view | 0.558824 | 0.395833 | 0.950000 | 20 |
| shadowsocks | G1 | CT1 | github.com::repository_view | 0.857143 | 0.818182 | 0.900000 | 20 |
| shadowsocks | G1 | CT1 | wikipedia.org::article_view | 0.000000 | 0.000000 | 0.000000 | 20 |
| shadowsocks | G1 | CT1 | youtube.com::search_results_view | 0.926829 | 0.904762 | 0.950000 | 20 |
| shadowsocks | G1 | CT1 | youtube.com::video_playback | 0.863636 | 0.791667 | 0.950000 | 20 |
| shadowsocks | G1 | CT2 | bing.com::search_results_view | 0.777778 | 0.875000 | 0.700000 | 20 |
| shadowsocks | G1 | CT2 | developer.mozilla.org::document_view | 0.723404 | 0.629630 | 0.850000 | 20 |
| shadowsocks | G1 | CT2 | github.com::repository_view | 0.864865 | 0.941176 | 0.800000 | 20 |
| shadowsocks | G1 | CT2 | wikipedia.org::article_view | 0.687500 | 0.916667 | 0.550000 | 20 |
| shadowsocks | G1 | CT2 | youtube.com::search_results_view | 0.857143 | 0.818182 | 0.900000 | 20 |
| shadowsocks | G1 | CT2 | youtube.com::video_playback | 0.826087 | 0.730769 | 0.950000 | 20 |
| shadowsocks | G1 | CT3 | bing.com::search_results_view | 0.727273 | 0.923077 | 0.600000 | 20 |
| shadowsocks | G1 | CT3 | developer.mozilla.org::document_view | 0.631579 | 0.486486 | 0.900000 | 20 |
| shadowsocks | G1 | CT3 | github.com::repository_view | 0.900000 | 0.900000 | 0.900000 | 20 |
| shadowsocks | G1 | CT3 | wikipedia.org::article_view | 0.333333 | 1.000000 | 0.200000 | 20 |
| shadowsocks | G1 | CT3 | youtube.com::search_results_view | 0.904762 | 0.863636 | 0.950000 | 20 |
| shadowsocks | G1 | CT3 | youtube.com::video_playback | 0.863636 | 0.791667 | 0.950000 | 20 |
| shadowsocks | G1 | CT4 | bing.com::search_results_view | 0.742857 | 0.866667 | 0.650000 | 20 |
| shadowsocks | G1 | CT4 | developer.mozilla.org::document_view | 0.610169 | 0.461538 | 0.900000 | 20 |
| shadowsocks | G1 | CT4 | github.com::repository_view | 0.883721 | 0.826087 | 0.950000 | 20 |
| shadowsocks | G1 | CT4 | wikipedia.org::article_view | 0.250000 | 0.750000 | 0.150000 | 20 |
| shadowsocks | G1 | CT4 | youtube.com::search_results_view | 0.894737 | 0.944444 | 0.850000 | 20 |
| shadowsocks | G1 | CT4 | youtube.com::video_playback | 0.926829 | 0.904762 | 0.950000 | 20 |
| shadowsocks | G1 | CT5 | bing.com::search_results_view | 0.756757 | 0.823529 | 0.700000 | 20 |
| shadowsocks | G1 | CT5 | developer.mozilla.org::document_view | 0.666667 | 0.600000 | 0.750000 | 20 |
| shadowsocks | G1 | CT5 | github.com::repository_view | 0.974359 | 1.000000 | 0.950000 | 20 |
| shadowsocks | G1 | CT5 | wikipedia.org::article_view | 0.789474 | 0.833333 | 0.750000 | 20 |
| shadowsocks | G1 | CT5 | youtube.com::search_results_view | 0.950000 | 0.950000 | 0.950000 | 20 |
| shadowsocks | G1 | CT5 | youtube.com::video_playback | 0.975610 | 0.952381 | 1.000000 | 20 |
| shadowsocks | G1 | StrongPost | bing.com::search_results_view | 0.777778 | 0.875000 | 0.700000 | 20 |
| shadowsocks | G1 | StrongPost | developer.mozilla.org::document_view | 0.723404 | 0.629630 | 0.850000 | 20 |
| shadowsocks | G1 | StrongPost | github.com::repository_view | 0.864865 | 0.941176 | 0.800000 | 20 |
| shadowsocks | G1 | StrongPost | wikipedia.org::article_view | 0.687500 | 0.916667 | 0.550000 | 20 |
| shadowsocks | G1 | StrongPost | youtube.com::search_results_view | 0.857143 | 0.818182 | 0.900000 | 20 |
| shadowsocks | G1 | StrongPost | youtube.com::video_playback | 0.826087 | 0.730769 | 0.950000 | 20 |
| shadowsocks | G2 | CT0 | bing.com::search_results_view | 0.708333 | 0.607143 | 0.850000 | 20 |
| shadowsocks | G2 | CT0 | developer.mozilla.org::document_view | 0.000000 | 0.000000 | 0.000000 | 20 |
| shadowsocks | G2 | CT0 | github.com::repository_view | 0.883721 | 0.826087 | 0.950000 | 20 |
| shadowsocks | G2 | CT0 | wikipedia.org::article_view | 0.678571 | 0.527778 | 0.950000 | 20 |
| shadowsocks | G2 | CT0 | youtube.com::search_results_view | 0.692308 | 0.562500 | 0.900000 | 20 |
| shadowsocks | G2 | CT0 | youtube.com::video_playback | 0.095238 | 1.000000 | 0.050000 | 20 |
| shadowsocks | G2 | CT1 | bing.com::search_results_view | 0.666667 | 0.600000 | 0.750000 | 20 |
| shadowsocks | G2 | CT1 | developer.mozilla.org::document_view | 0.000000 | 0.000000 | 0.000000 | 20 |
| shadowsocks | G2 | CT1 | github.com::repository_view | 0.883721 | 0.826087 | 0.950000 | 20 |
| shadowsocks | G2 | CT1 | wikipedia.org::article_view | 0.642857 | 0.500000 | 0.900000 | 20 |
| shadowsocks | G2 | CT1 | youtube.com::search_results_view | 0.641509 | 0.515152 | 0.850000 | 20 |
| shadowsocks | G2 | CT1 | youtube.com::video_playback | 0.173913 | 0.666667 | 0.100000 | 20 |
| shadowsocks | G2 | CT2 | bing.com::search_results_view | 0.755556 | 0.680000 | 0.850000 | 20 |
| shadowsocks | G2 | CT2 | developer.mozilla.org::document_view | 0.400000 | 0.600000 | 0.300000 | 20 |
| shadowsocks | G2 | CT2 | github.com::repository_view | 0.871795 | 0.894737 | 0.850000 | 20 |
| shadowsocks | G2 | CT2 | wikipedia.org::article_view | 0.641509 | 0.515152 | 0.850000 | 20 |
| shadowsocks | G2 | CT2 | youtube.com::search_results_view | 0.790698 | 0.739130 | 0.850000 | 20 |
| shadowsocks | G2 | CT2 | youtube.com::video_playback | 0.600000 | 0.900000 | 0.450000 | 20 |
| shadowsocks | G2 | CT3 | bing.com::search_results_view | 0.695652 | 0.615385 | 0.800000 | 20 |
| shadowsocks | G2 | CT3 | developer.mozilla.org::document_view | 0.000000 | 0.000000 | 0.000000 | 20 |
| shadowsocks | G2 | CT3 | github.com::repository_view | 0.923077 | 0.947368 | 0.900000 | 20 |
| shadowsocks | G2 | CT3 | wikipedia.org::article_view | 0.642857 | 0.500000 | 0.900000 | 20 |
| shadowsocks | G2 | CT3 | youtube.com::search_results_view | 0.734694 | 0.620690 | 0.900000 | 20 |
| shadowsocks | G2 | CT3 | youtube.com::video_playback | 0.466667 | 0.700000 | 0.350000 | 20 |
| shadowsocks | G2 | CT4 | bing.com::search_results_view | 0.755556 | 0.680000 | 0.850000 | 20 |
| shadowsocks | G2 | CT4 | developer.mozilla.org::document_view | 0.428571 | 0.750000 | 0.300000 | 20 |
| shadowsocks | G2 | CT4 | github.com::repository_view | 0.950000 | 0.950000 | 0.950000 | 20 |
| shadowsocks | G2 | CT4 | wikipedia.org::article_view | 0.693878 | 0.586207 | 0.850000 | 20 |
| shadowsocks | G2 | CT4 | youtube.com::search_results_view | 0.808511 | 0.703704 | 0.950000 | 20 |
| shadowsocks | G2 | CT4 | youtube.com::video_playback | 0.645161 | 0.909091 | 0.500000 | 20 |
| shadowsocks | G2 | CT5 | bing.com::search_results_view | 0.756757 | 0.823529 | 0.700000 | 20 |
| shadowsocks | G2 | CT5 | developer.mozilla.org::document_view | 0.666667 | 0.600000 | 0.750000 | 20 |
| shadowsocks | G2 | CT5 | github.com::repository_view | 0.974359 | 1.000000 | 0.950000 | 20 |
| shadowsocks | G2 | CT5 | wikipedia.org::article_view | 0.789474 | 0.833333 | 0.750000 | 20 |
| shadowsocks | G2 | CT5 | youtube.com::search_results_view | 0.950000 | 0.950000 | 0.950000 | 20 |
| shadowsocks | G2 | CT5 | youtube.com::video_playback | 0.975610 | 0.952381 | 1.000000 | 20 |
| shadowsocks | G2 | StrongPost | bing.com::search_results_view | 0.755556 | 0.680000 | 0.850000 | 20 |
| shadowsocks | G2 | StrongPost | developer.mozilla.org::document_view | 0.400000 | 0.600000 | 0.300000 | 20 |
| shadowsocks | G2 | StrongPost | github.com::repository_view | 0.871795 | 0.894737 | 0.850000 | 20 |
| shadowsocks | G2 | StrongPost | wikipedia.org::article_view | 0.641509 | 0.515152 | 0.850000 | 20 |
| shadowsocks | G2 | StrongPost | youtube.com::search_results_view | 0.790698 | 0.739130 | 0.850000 | 20 |
| shadowsocks | G2 | StrongPost | youtube.com::video_playback | 0.600000 | 0.900000 | 0.450000 | 20 |
| trojan | G0 | CT0 | bing.com::search_results_view | 0.857143 | 0.818182 | 0.900000 | 20 |
| trojan | G0 | CT0 | developer.mozilla.org::document_view | 0.780488 | 0.761905 | 0.800000 | 20 |
| trojan | G0 | CT0 | github.com::repository_view | 0.974359 | 1.000000 | 0.950000 | 20 |
| trojan | G0 | CT0 | wikipedia.org::article_view | 0.864865 | 0.941176 | 0.800000 | 20 |
| trojan | G0 | CT0 | youtube.com::search_results_view | 0.820513 | 0.842105 | 0.800000 | 20 |
| trojan | G0 | CT0 | youtube.com::video_playback | 0.857143 | 0.818182 | 0.900000 | 20 |
| trojan | G0 | CT1 | bing.com::search_results_view | 0.800000 | 0.800000 | 0.800000 | 20 |
| trojan | G0 | CT1 | developer.mozilla.org::document_view | 0.714286 | 0.681818 | 0.750000 | 20 |
| trojan | G0 | CT1 | github.com::repository_view | 0.871795 | 0.894737 | 0.850000 | 20 |
| trojan | G0 | CT1 | wikipedia.org::article_view | 0.800000 | 0.800000 | 0.800000 | 20 |
| trojan | G0 | CT1 | youtube.com::search_results_view | 0.810811 | 0.882353 | 0.750000 | 20 |
| trojan | G0 | CT1 | youtube.com::video_playback | 0.857143 | 0.818182 | 0.900000 | 20 |
| trojan | G0 | CT2 | bing.com::search_results_view | 0.850000 | 0.850000 | 0.850000 | 20 |
| trojan | G0 | CT2 | developer.mozilla.org::document_view | 0.820513 | 0.842105 | 0.800000 | 20 |
| trojan | G0 | CT2 | github.com::repository_view | 0.975610 | 0.952381 | 1.000000 | 20 |
| trojan | G0 | CT2 | wikipedia.org::article_view | 0.842105 | 0.888889 | 0.800000 | 20 |
| trojan | G0 | CT2 | youtube.com::search_results_view | 0.850000 | 0.850000 | 0.850000 | 20 |
| trojan | G0 | CT2 | youtube.com::video_playback | 0.857143 | 0.818182 | 0.900000 | 20 |
| trojan | G0 | CT3 | bing.com::search_results_view | 0.829268 | 0.809524 | 0.850000 | 20 |
| trojan | G0 | CT3 | developer.mozilla.org::document_view | 0.789474 | 0.833333 | 0.750000 | 20 |
| trojan | G0 | CT3 | github.com::repository_view | 0.950000 | 0.950000 | 0.950000 | 20 |
| trojan | G0 | CT3 | wikipedia.org::article_view | 0.842105 | 0.888889 | 0.800000 | 20 |
| trojan | G0 | CT3 | youtube.com::search_results_view | 0.829268 | 0.809524 | 0.850000 | 20 |
| trojan | G0 | CT3 | youtube.com::video_playback | 0.857143 | 0.818182 | 0.900000 | 20 |
| trojan | G0 | CT4 | bing.com::search_results_view | 0.871795 | 0.894737 | 0.850000 | 20 |
| trojan | G0 | CT4 | developer.mozilla.org::document_view | 0.829268 | 0.809524 | 0.850000 | 20 |
| trojan | G0 | CT4 | github.com::repository_view | 0.909091 | 0.833333 | 1.000000 | 20 |
| trojan | G0 | CT4 | wikipedia.org::article_view | 0.842105 | 0.888889 | 0.800000 | 20 |
| trojan | G0 | CT4 | youtube.com::search_results_view | 0.842105 | 0.888889 | 0.800000 | 20 |
| trojan | G0 | CT4 | youtube.com::video_playback | 0.850000 | 0.850000 | 0.850000 | 20 |
| trojan | G0 | CT5 | bing.com::search_results_view | 0.829268 | 0.809524 | 0.850000 | 20 |
| trojan | G0 | CT5 | developer.mozilla.org::document_view | 0.684211 | 0.722222 | 0.650000 | 20 |
| trojan | G0 | CT5 | github.com::repository_view | 0.950000 | 0.950000 | 0.950000 | 20 |
| trojan | G0 | CT5 | wikipedia.org::article_view | 0.800000 | 0.800000 | 0.800000 | 20 |
| trojan | G0 | CT5 | youtube.com::search_results_view | 0.878049 | 0.857143 | 0.900000 | 20 |
| trojan | G0 | CT5 | youtube.com::video_playback | 0.850000 | 0.850000 | 0.850000 | 20 |
| trojan | G0 | StrongPost | bing.com::search_results_view | 0.850000 | 0.850000 | 0.850000 | 20 |
| trojan | G0 | StrongPost | developer.mozilla.org::document_view | 0.820513 | 0.842105 | 0.800000 | 20 |
| trojan | G0 | StrongPost | github.com::repository_view | 0.975610 | 0.952381 | 1.000000 | 20 |
| trojan | G0 | StrongPost | wikipedia.org::article_view | 0.842105 | 0.888889 | 0.800000 | 20 |
| trojan | G0 | StrongPost | youtube.com::search_results_view | 0.850000 | 0.850000 | 0.850000 | 20 |
| trojan | G0 | StrongPost | youtube.com::video_playback | 0.857143 | 0.818182 | 0.900000 | 20 |
| trojan | G1 | CT0 | bing.com::search_results_view | 0.918919 | 1.000000 | 0.850000 | 20 |
| trojan | G1 | CT0 | developer.mozilla.org::document_view | 0.772727 | 0.708333 | 0.850000 | 20 |
| trojan | G1 | CT0 | github.com::repository_view | 0.952381 | 0.909091 | 1.000000 | 20 |
| trojan | G1 | CT0 | wikipedia.org::article_view | 0.777778 | 0.875000 | 0.700000 | 20 |
| trojan | G1 | CT0 | youtube.com::search_results_view | 0.820513 | 0.842105 | 0.800000 | 20 |
| trojan | G1 | CT0 | youtube.com::video_playback | 0.809524 | 0.772727 | 0.850000 | 20 |
| trojan | G1 | CT1 | bing.com::search_results_view | 0.789474 | 0.833333 | 0.750000 | 20 |
| trojan | G1 | CT1 | developer.mozilla.org::document_view | 0.808511 | 0.703704 | 0.950000 | 20 |
| trojan | G1 | CT1 | github.com::repository_view | 0.952381 | 0.909091 | 1.000000 | 20 |
| trojan | G1 | CT1 | wikipedia.org::article_view | 0.800000 | 0.933333 | 0.700000 | 20 |
| trojan | G1 | CT1 | youtube.com::search_results_view | 0.810811 | 0.882353 | 0.750000 | 20 |
| trojan | G1 | CT1 | youtube.com::video_playback | 0.829268 | 0.809524 | 0.850000 | 20 |
| trojan | G1 | CT2 | bing.com::search_results_view | 0.918919 | 1.000000 | 0.850000 | 20 |
| trojan | G1 | CT2 | developer.mozilla.org::document_view | 0.837209 | 0.782609 | 0.900000 | 20 |
| trojan | G1 | CT2 | github.com::repository_view | 1.000000 | 1.000000 | 1.000000 | 20 |
| trojan | G1 | CT2 | wikipedia.org::article_view | 0.871795 | 0.894737 | 0.850000 | 20 |
| trojan | G1 | CT2 | youtube.com::search_results_view | 0.820513 | 0.842105 | 0.800000 | 20 |
| trojan | G1 | CT2 | youtube.com::video_playback | 0.857143 | 0.818182 | 0.900000 | 20 |
| trojan | G1 | CT3 | bing.com::search_results_view | 0.894737 | 0.944444 | 0.850000 | 20 |
| trojan | G1 | CT3 | developer.mozilla.org::document_view | 0.790698 | 0.739130 | 0.850000 | 20 |
| trojan | G1 | CT3 | github.com::repository_view | 0.975610 | 0.952381 | 1.000000 | 20 |
| trojan | G1 | CT3 | wikipedia.org::article_view | 0.742857 | 0.866667 | 0.650000 | 20 |
| trojan | G1 | CT3 | youtube.com::search_results_view | 0.800000 | 0.800000 | 0.800000 | 20 |
| trojan | G1 | CT3 | youtube.com::video_playback | 0.837209 | 0.782609 | 0.900000 | 20 |
| trojan | G1 | CT4 | bing.com::search_results_view | 0.810811 | 0.882353 | 0.750000 | 20 |
| trojan | G1 | CT4 | developer.mozilla.org::document_view | 0.791667 | 0.678571 | 0.950000 | 20 |
| trojan | G1 | CT4 | github.com::repository_view | 0.952381 | 0.909091 | 1.000000 | 20 |
| trojan | G1 | CT4 | wikipedia.org::article_view | 0.800000 | 0.933333 | 0.700000 | 20 |
| trojan | G1 | CT4 | youtube.com::search_results_view | 0.871795 | 0.894737 | 0.850000 | 20 |
| trojan | G1 | CT4 | youtube.com::video_playback | 0.871795 | 0.894737 | 0.850000 | 20 |
| trojan | G1 | CT5 | bing.com::search_results_view | 0.829268 | 0.809524 | 0.850000 | 20 |
| trojan | G1 | CT5 | developer.mozilla.org::document_view | 0.684211 | 0.722222 | 0.650000 | 20 |
| trojan | G1 | CT5 | github.com::repository_view | 0.950000 | 0.950000 | 0.950000 | 20 |
| trojan | G1 | CT5 | wikipedia.org::article_view | 0.800000 | 0.800000 | 0.800000 | 20 |
| trojan | G1 | CT5 | youtube.com::search_results_view | 0.878049 | 0.857143 | 0.900000 | 20 |
| trojan | G1 | CT5 | youtube.com::video_playback | 0.850000 | 0.850000 | 0.850000 | 20 |
| trojan | G1 | StrongPost | bing.com::search_results_view | 0.918919 | 1.000000 | 0.850000 | 20 |
| trojan | G1 | StrongPost | developer.mozilla.org::document_view | 0.837209 | 0.782609 | 0.900000 | 20 |
| trojan | G1 | StrongPost | github.com::repository_view | 1.000000 | 1.000000 | 1.000000 | 20 |
| trojan | G1 | StrongPost | wikipedia.org::article_view | 0.871795 | 0.894737 | 0.850000 | 20 |
| trojan | G1 | StrongPost | youtube.com::search_results_view | 0.820513 | 0.842105 | 0.800000 | 20 |
| trojan | G1 | StrongPost | youtube.com::video_playback | 0.857143 | 0.818182 | 0.900000 | 20 |
| trojan | G2 | CT0 | bing.com::search_results_view | 0.878049 | 0.857143 | 0.900000 | 20 |
| trojan | G2 | CT0 | developer.mozilla.org::document_view | 0.647059 | 0.785714 | 0.550000 | 20 |
| trojan | G2 | CT0 | github.com::repository_view | 0.975610 | 0.952381 | 1.000000 | 20 |
| trojan | G2 | CT0 | wikipedia.org::article_view | 0.790698 | 0.739130 | 0.850000 | 20 |
| trojan | G2 | CT0 | youtube.com::search_results_view | 0.883721 | 0.826087 | 0.950000 | 20 |
| trojan | G2 | CT0 | youtube.com::video_playback | 0.842105 | 0.888889 | 0.800000 | 20 |
| trojan | G2 | CT1 | bing.com::search_results_view | 0.850000 | 0.850000 | 0.850000 | 20 |
| trojan | G2 | CT1 | developer.mozilla.org::document_view | 0.705882 | 0.857143 | 0.600000 | 20 |
| trojan | G2 | CT1 | github.com::repository_view | 0.930233 | 0.869565 | 1.000000 | 20 |
| trojan | G2 | CT1 | wikipedia.org::article_view | 0.711111 | 0.640000 | 0.800000 | 20 |
| trojan | G2 | CT1 | youtube.com::search_results_view | 0.837209 | 0.782609 | 0.900000 | 20 |
| trojan | G2 | CT1 | youtube.com::video_playback | 0.800000 | 0.933333 | 0.700000 | 20 |
| trojan | G2 | CT2 | bing.com::search_results_view | 0.878049 | 0.857143 | 0.900000 | 20 |
| trojan | G2 | CT2 | developer.mozilla.org::document_view | 0.756757 | 0.823529 | 0.700000 | 20 |
| trojan | G2 | CT2 | github.com::repository_view | 0.975610 | 0.952381 | 1.000000 | 20 |
| trojan | G2 | CT2 | wikipedia.org::article_view | 0.820513 | 0.842105 | 0.800000 | 20 |
| trojan | G2 | CT2 | youtube.com::search_results_view | 0.883721 | 0.826087 | 0.950000 | 20 |
| trojan | G2 | CT2 | youtube.com::video_playback | 0.820513 | 0.842105 | 0.800000 | 20 |
| trojan | G2 | CT3 | bing.com::search_results_view | 0.900000 | 0.900000 | 0.900000 | 20 |
| trojan | G2 | CT3 | developer.mozilla.org::document_view | 0.606061 | 0.769231 | 0.500000 | 20 |
| trojan | G2 | CT3 | github.com::repository_view | 0.975610 | 0.952381 | 1.000000 | 20 |
| trojan | G2 | CT3 | wikipedia.org::article_view | 0.744186 | 0.695652 | 0.800000 | 20 |
| trojan | G2 | CT3 | youtube.com::search_results_view | 0.818182 | 0.750000 | 0.900000 | 20 |
| trojan | G2 | CT3 | youtube.com::video_playback | 0.820513 | 0.842105 | 0.800000 | 20 |
| trojan | G2 | CT4 | bing.com::search_results_view | 0.923077 | 0.947368 | 0.900000 | 20 |
| trojan | G2 | CT4 | developer.mozilla.org::document_view | 0.857143 | 0.818182 | 0.900000 | 20 |
| trojan | G2 | CT4 | github.com::repository_view | 0.930233 | 0.869565 | 1.000000 | 20 |
| trojan | G2 | CT4 | wikipedia.org::article_view | 0.871795 | 0.894737 | 0.850000 | 20 |
| trojan | G2 | CT4 | youtube.com::search_results_view | 0.900000 | 0.900000 | 0.900000 | 20 |
| trojan | G2 | CT4 | youtube.com::video_playback | 0.918919 | 1.000000 | 0.850000 | 20 |
| trojan | G2 | CT5 | bing.com::search_results_view | 0.829268 | 0.809524 | 0.850000 | 20 |
| trojan | G2 | CT5 | developer.mozilla.org::document_view | 0.684211 | 0.722222 | 0.650000 | 20 |
| trojan | G2 | CT5 | github.com::repository_view | 0.950000 | 0.950000 | 0.950000 | 20 |
| trojan | G2 | CT5 | wikipedia.org::article_view | 0.800000 | 0.800000 | 0.800000 | 20 |
| trojan | G2 | CT5 | youtube.com::search_results_view | 0.878049 | 0.857143 | 0.900000 | 20 |
| trojan | G2 | CT5 | youtube.com::video_playback | 0.850000 | 0.850000 | 0.850000 | 20 |
| trojan | G2 | StrongPost | bing.com::search_results_view | 0.878049 | 0.857143 | 0.900000 | 20 |
| trojan | G2 | StrongPost | developer.mozilla.org::document_view | 0.756757 | 0.823529 | 0.700000 | 20 |
| trojan | G2 | StrongPost | github.com::repository_view | 0.975610 | 0.952381 | 1.000000 | 20 |
| trojan | G2 | StrongPost | wikipedia.org::article_view | 0.820513 | 0.842105 | 0.800000 | 20 |
| trojan | G2 | StrongPost | youtube.com::search_results_view | 0.883721 | 0.826087 | 0.950000 | 20 |
| trojan | G2 | StrongPost | youtube.com::video_playback | 0.820513 | 0.842105 | 0.800000 | 20 |
| vless | G0 | CT0 | bing.com::search_results_view | 0.878049 | 0.857143 | 0.900000 | 20 |
| vless | G0 | CT0 | developer.mozilla.org::document_view | 0.820513 | 0.842105 | 0.800000 | 20 |
| vless | G0 | CT0 | github.com::repository_view | 0.894737 | 0.944444 | 0.850000 | 20 |
| vless | G0 | CT0 | wikipedia.org::article_view | 0.714286 | 0.681818 | 0.750000 | 20 |
| vless | G0 | CT0 | youtube.com::search_results_view | 0.777778 | 0.875000 | 0.700000 | 20 |
| vless | G0 | CT0 | youtube.com::video_playback | 0.863636 | 0.791667 | 0.950000 | 20 |
| vless | G0 | CT1 | bing.com::search_results_view | 0.850000 | 0.850000 | 0.850000 | 20 |
| vless | G0 | CT1 | developer.mozilla.org::document_view | 0.761905 | 0.727273 | 0.800000 | 20 |
| vless | G0 | CT1 | github.com::repository_view | 0.918919 | 1.000000 | 0.850000 | 20 |
| vless | G0 | CT1 | wikipedia.org::article_view | 0.731707 | 0.714286 | 0.750000 | 20 |
| vless | G0 | CT1 | youtube.com::search_results_view | 0.810811 | 0.882353 | 0.750000 | 20 |
| vless | G0 | CT1 | youtube.com::video_playback | 0.837209 | 0.782609 | 0.900000 | 20 |
| vless | G0 | CT2 | bing.com::search_results_view | 0.923077 | 0.947368 | 0.900000 | 20 |
| vless | G0 | CT2 | developer.mozilla.org::document_view | 0.800000 | 0.800000 | 0.800000 | 20 |
| vless | G0 | CT2 | github.com::repository_view | 0.894737 | 0.944444 | 0.850000 | 20 |
| vless | G0 | CT2 | wikipedia.org::article_view | 0.681818 | 0.625000 | 0.750000 | 20 |
| vless | G0 | CT2 | youtube.com::search_results_view | 0.777778 | 0.875000 | 0.700000 | 20 |
| vless | G0 | CT2 | youtube.com::video_playback | 0.837209 | 0.782609 | 0.900000 | 20 |
| vless | G0 | CT3 | bing.com::search_results_view | 0.857143 | 0.818182 | 0.900000 | 20 |
| vless | G0 | CT3 | developer.mozilla.org::document_view | 0.789474 | 0.833333 | 0.750000 | 20 |
| vless | G0 | CT3 | github.com::repository_view | 0.810811 | 0.882353 | 0.750000 | 20 |
| vless | G0 | CT3 | wikipedia.org::article_view | 0.714286 | 0.681818 | 0.750000 | 20 |
| vless | G0 | CT3 | youtube.com::search_results_view | 0.756757 | 0.823529 | 0.700000 | 20 |
| vless | G0 | CT3 | youtube.com::video_playback | 0.818182 | 0.750000 | 0.900000 | 20 |
| vless | G0 | CT4 | bing.com::search_results_view | 0.790698 | 0.739130 | 0.850000 | 20 |
| vless | G0 | CT4 | developer.mozilla.org::document_view | 0.800000 | 0.800000 | 0.800000 | 20 |
| vless | G0 | CT4 | github.com::repository_view | 0.871795 | 0.894737 | 0.850000 | 20 |
| vless | G0 | CT4 | wikipedia.org::article_view | 0.780488 | 0.761905 | 0.800000 | 20 |
| vless | G0 | CT4 | youtube.com::search_results_view | 0.742857 | 0.866667 | 0.650000 | 20 |
| vless | G0 | CT4 | youtube.com::video_playback | 0.857143 | 0.818182 | 0.900000 | 20 |
| vless | G0 | CT5 | bing.com::search_results_view | 0.800000 | 0.800000 | 0.800000 | 20 |
| vless | G0 | CT5 | developer.mozilla.org::document_view | 0.736842 | 0.777778 | 0.700000 | 20 |
| vless | G0 | CT5 | github.com::repository_view | 0.871795 | 0.894737 | 0.850000 | 20 |
| vless | G0 | CT5 | wikipedia.org::article_view | 0.714286 | 0.681818 | 0.750000 | 20 |
| vless | G0 | CT5 | youtube.com::search_results_view | 0.769231 | 0.789474 | 0.750000 | 20 |
| vless | G0 | CT5 | youtube.com::video_playback | 0.904762 | 0.863636 | 0.950000 | 20 |
| vless | G0 | StrongPost | bing.com::search_results_view | 0.923077 | 0.947368 | 0.900000 | 20 |
| vless | G0 | StrongPost | developer.mozilla.org::document_view | 0.800000 | 0.800000 | 0.800000 | 20 |
| vless | G0 | StrongPost | github.com::repository_view | 0.894737 | 0.944444 | 0.850000 | 20 |
| vless | G0 | StrongPost | wikipedia.org::article_view | 0.681818 | 0.625000 | 0.750000 | 20 |
| vless | G0 | StrongPost | youtube.com::search_results_view | 0.777778 | 0.875000 | 0.700000 | 20 |
| vless | G0 | StrongPost | youtube.com::video_playback | 0.837209 | 0.782609 | 0.900000 | 20 |
| vless | G1 | CT0 | bing.com::search_results_view | 0.894737 | 0.944444 | 0.850000 | 20 |
| vless | G1 | CT0 | developer.mozilla.org::document_view | 0.809524 | 0.772727 | 0.850000 | 20 |
| vless | G1 | CT0 | github.com::repository_view | 0.923077 | 0.947368 | 0.900000 | 20 |
| vless | G1 | CT0 | wikipedia.org::article_view | 0.648649 | 0.705882 | 0.600000 | 20 |
| vless | G1 | CT0 | youtube.com::search_results_view | 0.714286 | 0.681818 | 0.750000 | 20 |
| vless | G1 | CT0 | youtube.com::video_playback | 0.904762 | 0.863636 | 0.950000 | 20 |
| vless | G1 | CT1 | bing.com::search_results_view | 0.842105 | 0.888889 | 0.800000 | 20 |
| vless | G1 | CT1 | developer.mozilla.org::document_view | 0.818182 | 0.750000 | 0.900000 | 20 |
| vless | G1 | CT1 | github.com::repository_view | 0.900000 | 0.900000 | 0.900000 | 20 |
| vless | G1 | CT1 | wikipedia.org::article_view | 0.705882 | 0.857143 | 0.600000 | 20 |
| vless | G1 | CT1 | youtube.com::search_results_view | 0.809524 | 0.772727 | 0.850000 | 20 |
| vless | G1 | CT1 | youtube.com::video_playback | 0.904762 | 0.863636 | 0.950000 | 20 |
| vless | G1 | CT2 | bing.com::search_results_view | 0.850000 | 0.850000 | 0.850000 | 20 |
| vless | G1 | CT2 | developer.mozilla.org::document_view | 0.750000 | 0.750000 | 0.750000 | 20 |
| vless | G1 | CT2 | github.com::repository_view | 0.900000 | 0.900000 | 0.900000 | 20 |
| vless | G1 | CT2 | wikipedia.org::article_view | 0.684211 | 0.722222 | 0.650000 | 20 |
| vless | G1 | CT2 | youtube.com::search_results_view | 0.731707 | 0.714286 | 0.750000 | 20 |
| vless | G1 | CT2 | youtube.com::video_playback | 0.878049 | 0.857143 | 0.900000 | 20 |
| vless | G1 | CT3 | bing.com::search_results_view | 0.789474 | 0.833333 | 0.750000 | 20 |
| vless | G1 | CT3 | developer.mozilla.org::document_view | 0.780488 | 0.761905 | 0.800000 | 20 |
| vless | G1 | CT3 | github.com::repository_view | 0.800000 | 0.800000 | 0.800000 | 20 |
| vless | G1 | CT3 | wikipedia.org::article_view | 0.684211 | 0.722222 | 0.650000 | 20 |
| vless | G1 | CT3 | youtube.com::search_results_view | 0.731707 | 0.714286 | 0.750000 | 20 |
| vless | G1 | CT3 | youtube.com::video_playback | 0.904762 | 0.863636 | 0.950000 | 20 |
| vless | G1 | CT4 | bing.com::search_results_view | 0.790698 | 0.739130 | 0.850000 | 20 |
| vless | G1 | CT4 | developer.mozilla.org::document_view | 0.790698 | 0.739130 | 0.850000 | 20 |
| vless | G1 | CT4 | github.com::repository_view | 0.878049 | 0.857143 | 0.900000 | 20 |
| vless | G1 | CT4 | wikipedia.org::article_view | 0.628571 | 0.733333 | 0.550000 | 20 |
| vless | G1 | CT4 | youtube.com::search_results_view | 0.684211 | 0.722222 | 0.650000 | 20 |
| vless | G1 | CT4 | youtube.com::video_playback | 0.850000 | 0.850000 | 0.850000 | 20 |
| vless | G1 | CT5 | bing.com::search_results_view | 0.800000 | 0.800000 | 0.800000 | 20 |
| vless | G1 | CT5 | developer.mozilla.org::document_view | 0.736842 | 0.777778 | 0.700000 | 20 |
| vless | G1 | CT5 | github.com::repository_view | 0.871795 | 0.894737 | 0.850000 | 20 |
| vless | G1 | CT5 | wikipedia.org::article_view | 0.714286 | 0.681818 | 0.750000 | 20 |
| vless | G1 | CT5 | youtube.com::search_results_view | 0.769231 | 0.789474 | 0.750000 | 20 |
| vless | G1 | CT5 | youtube.com::video_playback | 0.904762 | 0.863636 | 0.950000 | 20 |
| vless | G1 | StrongPost | bing.com::search_results_view | 0.850000 | 0.850000 | 0.850000 | 20 |
| vless | G1 | StrongPost | developer.mozilla.org::document_view | 0.750000 | 0.750000 | 0.750000 | 20 |
| vless | G1 | StrongPost | github.com::repository_view | 0.900000 | 0.900000 | 0.900000 | 20 |
| vless | G1 | StrongPost | wikipedia.org::article_view | 0.684211 | 0.722222 | 0.650000 | 20 |
| vless | G1 | StrongPost | youtube.com::search_results_view | 0.731707 | 0.714286 | 0.750000 | 20 |
| vless | G1 | StrongPost | youtube.com::video_playback | 0.878049 | 0.857143 | 0.900000 | 20 |
| vless | G2 | CT0 | bing.com::search_results_view | 0.844444 | 0.760000 | 0.950000 | 20 |
| vless | G2 | CT0 | developer.mozilla.org::document_view | 0.709677 | 1.000000 | 0.550000 | 20 |
| vless | G2 | CT0 | github.com::repository_view | 0.923077 | 0.947368 | 0.900000 | 20 |
| vless | G2 | CT0 | wikipedia.org::article_view | 0.711111 | 0.640000 | 0.800000 | 20 |
| vless | G2 | CT0 | youtube.com::search_results_view | 0.750000 | 0.750000 | 0.750000 | 20 |
| vless | G2 | CT0 | youtube.com::video_playback | 0.900000 | 0.900000 | 0.900000 | 20 |
| vless | G2 | CT1 | bing.com::search_results_view | 0.878049 | 0.857143 | 0.900000 | 20 |
| vless | G2 | CT1 | developer.mozilla.org::document_view | 0.685714 | 0.800000 | 0.600000 | 20 |
| vless | G2 | CT1 | github.com::repository_view | 0.923077 | 0.947368 | 0.900000 | 20 |
| vless | G2 | CT1 | wikipedia.org::article_view | 0.608696 | 0.538462 | 0.700000 | 20 |
| vless | G2 | CT1 | youtube.com::search_results_view | 0.800000 | 0.800000 | 0.800000 | 20 |
| vless | G2 | CT1 | youtube.com::video_playback | 0.871795 | 0.894737 | 0.850000 | 20 |
| vless | G2 | CT2 | bing.com::search_results_view | 0.904762 | 0.863636 | 0.950000 | 20 |
| vless | G2 | CT2 | developer.mozilla.org::document_view | 0.777778 | 0.875000 | 0.700000 | 20 |
| vless | G2 | CT2 | github.com::repository_view | 0.894737 | 0.944444 | 0.850000 | 20 |
| vless | G2 | CT2 | wikipedia.org::article_view | 0.666667 | 0.600000 | 0.750000 | 20 |
| vless | G2 | CT2 | youtube.com::search_results_view | 0.684211 | 0.722222 | 0.650000 | 20 |
| vless | G2 | CT2 | youtube.com::video_playback | 0.878049 | 0.857143 | 0.900000 | 20 |
| vless | G2 | CT3 | bing.com::search_results_view | 0.837209 | 0.782609 | 0.900000 | 20 |
| vless | G2 | CT3 | developer.mozilla.org::document_view | 0.727273 | 0.923077 | 0.600000 | 20 |
| vless | G2 | CT3 | github.com::repository_view | 0.800000 | 0.800000 | 0.800000 | 20 |
| vless | G2 | CT3 | wikipedia.org::article_view | 0.666667 | 0.636364 | 0.700000 | 20 |
| vless | G2 | CT3 | youtube.com::search_results_view | 0.761905 | 0.727273 | 0.800000 | 20 |
| vless | G2 | CT3 | youtube.com::video_playback | 0.800000 | 0.800000 | 0.800000 | 20 |
| vless | G2 | CT4 | bing.com::search_results_view | 0.829268 | 0.809524 | 0.850000 | 20 |
| vless | G2 | CT4 | developer.mozilla.org::document_view | 0.666667 | 0.846154 | 0.550000 | 20 |
| vless | G2 | CT4 | github.com::repository_view | 0.857143 | 0.818182 | 0.900000 | 20 |
| vless | G2 | CT4 | wikipedia.org::article_view | 0.680851 | 0.592593 | 0.800000 | 20 |
| vless | G2 | CT4 | youtube.com::search_results_view | 0.756757 | 0.823529 | 0.700000 | 20 |
| vless | G2 | CT4 | youtube.com::video_playback | 0.850000 | 0.850000 | 0.850000 | 20 |
| vless | G2 | CT5 | bing.com::search_results_view | 0.800000 | 0.800000 | 0.800000 | 20 |
| vless | G2 | CT5 | developer.mozilla.org::document_view | 0.736842 | 0.777778 | 0.700000 | 20 |
| vless | G2 | CT5 | github.com::repository_view | 0.871795 | 0.894737 | 0.850000 | 20 |
| vless | G2 | CT5 | wikipedia.org::article_view | 0.714286 | 0.681818 | 0.750000 | 20 |
| vless | G2 | CT5 | youtube.com::search_results_view | 0.769231 | 0.789474 | 0.750000 | 20 |
| vless | G2 | CT5 | youtube.com::video_playback | 0.904762 | 0.863636 | 0.950000 | 20 |
| vless | G2 | StrongPost | bing.com::search_results_view | 0.904762 | 0.863636 | 0.950000 | 20 |
| vless | G2 | StrongPost | developer.mozilla.org::document_view | 0.777778 | 0.875000 | 0.700000 | 20 |
| vless | G2 | StrongPost | github.com::repository_view | 0.894737 | 0.944444 | 0.850000 | 20 |
| vless | G2 | StrongPost | wikipedia.org::article_view | 0.666667 | 0.600000 | 0.750000 | 20 |
| vless | G2 | StrongPost | youtube.com::search_results_view | 0.684211 | 0.722222 | 0.650000 | 20 |
| vless | G2 | StrongPost | youtube.com::video_playback | 0.878049 | 0.857143 | 0.900000 | 20 |
| vmess | G0 | CT0 | bing.com::search_results_view | 0.731707 | 0.714286 | 0.750000 | 20 |
| vmess | G0 | CT0 | developer.mozilla.org::document_view | 0.571429 | 0.545455 | 0.600000 | 20 |
| vmess | G0 | CT0 | github.com::repository_view | 0.645161 | 0.909091 | 0.500000 | 20 |
| vmess | G0 | CT0 | wikipedia.org::article_view | 0.680851 | 0.592593 | 0.800000 | 20 |
| vmess | G0 | CT0 | youtube.com::search_results_view | 0.777778 | 0.875000 | 0.700000 | 20 |
| vmess | G0 | CT0 | youtube.com::video_playback | 0.883721 | 0.826087 | 0.950000 | 20 |
| vmess | G0 | CT1 | bing.com::search_results_view | 0.769231 | 0.789474 | 0.750000 | 20 |
| vmess | G0 | CT1 | developer.mozilla.org::document_view | 0.595745 | 0.518519 | 0.700000 | 20 |
| vmess | G0 | CT1 | github.com::repository_view | 0.600000 | 0.900000 | 0.450000 | 20 |
| vmess | G0 | CT1 | wikipedia.org::article_view | 0.666667 | 0.600000 | 0.750000 | 20 |
| vmess | G0 | CT1 | youtube.com::search_results_view | 0.864865 | 0.941176 | 0.800000 | 20 |
| vmess | G0 | CT1 | youtube.com::video_playback | 0.904762 | 0.863636 | 0.950000 | 20 |
| vmess | G0 | CT2 | bing.com::search_results_view | 0.769231 | 0.789474 | 0.750000 | 20 |
| vmess | G0 | CT2 | developer.mozilla.org::document_view | 0.585366 | 0.571429 | 0.600000 | 20 |
| vmess | G0 | CT2 | github.com::repository_view | 0.800000 | 0.933333 | 0.700000 | 20 |
| vmess | G0 | CT2 | wikipedia.org::article_view | 0.711111 | 0.640000 | 0.800000 | 20 |
| vmess | G0 | CT2 | youtube.com::search_results_view | 0.878049 | 0.857143 | 0.900000 | 20 |
| vmess | G0 | CT2 | youtube.com::video_playback | 0.974359 | 1.000000 | 0.950000 | 20 |
| vmess | G0 | CT3 | bing.com::search_results_view | 0.769231 | 0.789474 | 0.750000 | 20 |
| vmess | G0 | CT3 | developer.mozilla.org::document_view | 0.594595 | 0.647059 | 0.550000 | 20 |
| vmess | G0 | CT3 | github.com::repository_view | 0.842105 | 0.888889 | 0.800000 | 20 |
| vmess | G0 | CT3 | wikipedia.org::article_view | 0.697674 | 0.652174 | 0.750000 | 20 |
| vmess | G0 | CT3 | youtube.com::search_results_view | 0.926829 | 0.904762 | 0.950000 | 20 |
| vmess | G0 | CT3 | youtube.com::video_playback | 0.904762 | 0.863636 | 0.950000 | 20 |
| vmess | G0 | CT4 | bing.com::search_results_view | 0.769231 | 0.789474 | 0.750000 | 20 |
| vmess | G0 | CT4 | developer.mozilla.org::document_view | 0.681818 | 0.625000 | 0.750000 | 20 |
| vmess | G0 | CT4 | github.com::repository_view | 0.904762 | 0.863636 | 0.950000 | 20 |
| vmess | G0 | CT4 | wikipedia.org::article_view | 0.684211 | 0.722222 | 0.650000 | 20 |
| vmess | G0 | CT4 | youtube.com::search_results_view | 0.736842 | 0.777778 | 0.700000 | 20 |
| vmess | G0 | CT4 | youtube.com::video_playback | 0.974359 | 1.000000 | 0.950000 | 20 |
| vmess | G0 | CT5 | bing.com::search_results_view | 0.800000 | 0.800000 | 0.800000 | 20 |
| vmess | G0 | CT5 | developer.mozilla.org::document_view | 0.611111 | 0.687500 | 0.550000 | 20 |
| vmess | G0 | CT5 | github.com::repository_view | 0.850000 | 0.850000 | 0.850000 | 20 |
| vmess | G0 | CT5 | wikipedia.org::article_view | 0.636364 | 0.583333 | 0.700000 | 20 |
| vmess | G0 | CT5 | youtube.com::search_results_view | 0.800000 | 0.800000 | 0.800000 | 20 |
| vmess | G0 | CT5 | youtube.com::video_playback | 0.900000 | 0.900000 | 0.900000 | 20 |
| vmess | G0 | StrongPost | bing.com::search_results_view | 0.769231 | 0.789474 | 0.750000 | 20 |
| vmess | G0 | StrongPost | developer.mozilla.org::document_view | 0.585366 | 0.571429 | 0.600000 | 20 |
| vmess | G0 | StrongPost | github.com::repository_view | 0.800000 | 0.933333 | 0.700000 | 20 |
| vmess | G0 | StrongPost | wikipedia.org::article_view | 0.711111 | 0.640000 | 0.800000 | 20 |
| vmess | G0 | StrongPost | youtube.com::search_results_view | 0.878049 | 0.857143 | 0.900000 | 20 |
| vmess | G0 | StrongPost | youtube.com::video_playback | 0.974359 | 1.000000 | 0.950000 | 20 |
| vmess | G1 | CT0 | bing.com::search_results_view | 0.260870 | 1.000000 | 0.150000 | 20 |
| vmess | G1 | CT0 | developer.mozilla.org::document_view | 0.633333 | 0.475000 | 0.950000 | 20 |
| vmess | G1 | CT0 | github.com::repository_view | 0.883721 | 0.826087 | 0.950000 | 20 |
| vmess | G1 | CT0 | wikipedia.org::article_view | 0.095238 | 1.000000 | 0.050000 | 20 |
| vmess | G1 | CT0 | youtube.com::search_results_view | 0.775510 | 0.655172 | 0.950000 | 20 |
| vmess | G1 | CT0 | youtube.com::video_playback | 0.863636 | 0.791667 | 0.950000 | 20 |
| vmess | G1 | CT1 | bing.com::search_results_view | 0.333333 | 1.000000 | 0.200000 | 20 |
| vmess | G1 | CT1 | developer.mozilla.org::document_view | 0.593750 | 0.431818 | 0.950000 | 20 |
| vmess | G1 | CT1 | github.com::repository_view | 0.904762 | 0.863636 | 0.950000 | 20 |
| vmess | G1 | CT1 | wikipedia.org::article_view | 0.000000 | 0.000000 | 0.000000 | 20 |
| vmess | G1 | CT1 | youtube.com::search_results_view | 0.844444 | 0.760000 | 0.950000 | 20 |
| vmess | G1 | CT1 | youtube.com::video_playback | 0.844444 | 0.760000 | 0.950000 | 20 |
| vmess | G1 | CT2 | bing.com::search_results_view | 0.789474 | 0.833333 | 0.750000 | 20 |
| vmess | G1 | CT2 | developer.mozilla.org::document_view | 0.727273 | 0.666667 | 0.800000 | 20 |
| vmess | G1 | CT2 | github.com::repository_view | 0.926829 | 0.904762 | 0.950000 | 20 |
| vmess | G1 | CT2 | wikipedia.org::article_view | 0.764706 | 0.928571 | 0.650000 | 20 |
| vmess | G1 | CT2 | youtube.com::search_results_view | 0.909091 | 0.833333 | 1.000000 | 20 |
| vmess | G1 | CT2 | youtube.com::video_playback | 0.974359 | 1.000000 | 0.950000 | 20 |
| vmess | G1 | CT3 | bing.com::search_results_view | 0.580645 | 0.818182 | 0.450000 | 20 |
| vmess | G1 | CT3 | developer.mozilla.org::document_view | 0.654545 | 0.514286 | 0.900000 | 20 |
| vmess | G1 | CT3 | github.com::repository_view | 0.900000 | 0.900000 | 0.900000 | 20 |
| vmess | G1 | CT3 | wikipedia.org::article_view | 0.320000 | 0.800000 | 0.200000 | 20 |
| vmess | G1 | CT3 | youtube.com::search_results_view | 0.808511 | 0.703704 | 0.950000 | 20 |
| vmess | G1 | CT3 | youtube.com::video_playback | 0.904762 | 0.863636 | 0.950000 | 20 |
| vmess | G1 | CT4 | bing.com::search_results_view | 0.645161 | 0.909091 | 0.500000 | 20 |
| vmess | G1 | CT4 | developer.mozilla.org::document_view | 0.654545 | 0.514286 | 0.900000 | 20 |
| vmess | G1 | CT4 | github.com::repository_view | 0.904762 | 0.863636 | 0.950000 | 20 |
| vmess | G1 | CT4 | wikipedia.org::article_view | 0.518519 | 1.000000 | 0.350000 | 20 |
| vmess | G1 | CT4 | youtube.com::search_results_view | 0.826087 | 0.730769 | 0.950000 | 20 |
| vmess | G1 | CT4 | youtube.com::video_playback | 0.974359 | 1.000000 | 0.950000 | 20 |
| vmess | G1 | CT5 | bing.com::search_results_view | 0.800000 | 0.800000 | 0.800000 | 20 |
| vmess | G1 | CT5 | developer.mozilla.org::document_view | 0.611111 | 0.687500 | 0.550000 | 20 |
| vmess | G1 | CT5 | github.com::repository_view | 0.850000 | 0.850000 | 0.850000 | 20 |
| vmess | G1 | CT5 | wikipedia.org::article_view | 0.636364 | 0.583333 | 0.700000 | 20 |
| vmess | G1 | CT5 | youtube.com::search_results_view | 0.800000 | 0.800000 | 0.800000 | 20 |
| vmess | G1 | CT5 | youtube.com::video_playback | 0.900000 | 0.900000 | 0.900000 | 20 |
| vmess | G1 | StrongPost | bing.com::search_results_view | 0.789474 | 0.833333 | 0.750000 | 20 |
| vmess | G1 | StrongPost | developer.mozilla.org::document_view | 0.727273 | 0.666667 | 0.800000 | 20 |
| vmess | G1 | StrongPost | github.com::repository_view | 0.926829 | 0.904762 | 0.950000 | 20 |
| vmess | G1 | StrongPost | wikipedia.org::article_view | 0.764706 | 0.928571 | 0.650000 | 20 |
| vmess | G1 | StrongPost | youtube.com::search_results_view | 0.909091 | 0.833333 | 1.000000 | 20 |
| vmess | G1 | StrongPost | youtube.com::video_playback | 0.974359 | 1.000000 | 0.950000 | 20 |
| vmess | G2 | CT0 | bing.com::search_results_view | 0.739130 | 0.653846 | 0.850000 | 20 |
| vmess | G2 | CT0 | developer.mozilla.org::document_view | 0.000000 | 0.000000 | 0.000000 | 20 |
| vmess | G2 | CT0 | github.com::repository_view | 0.837209 | 0.782609 | 0.900000 | 20 |
| vmess | G2 | CT0 | wikipedia.org::article_view | 0.666667 | 0.548387 | 0.850000 | 20 |
| vmess | G2 | CT0 | youtube.com::search_results_view | 0.857143 | 0.818182 | 0.900000 | 20 |
| vmess | G2 | CT0 | youtube.com::video_playback | 0.947368 | 1.000000 | 0.900000 | 20 |
| vmess | G2 | CT1 | bing.com::search_results_view | 0.693878 | 0.586207 | 0.850000 | 20 |
| vmess | G2 | CT1 | developer.mozilla.org::document_view | 0.000000 | 0.000000 | 0.000000 | 20 |
| vmess | G2 | CT1 | github.com::repository_view | 0.863636 | 0.791667 | 0.950000 | 20 |
| vmess | G2 | CT1 | wikipedia.org::article_view | 0.638298 | 0.555556 | 0.750000 | 20 |
| vmess | G2 | CT1 | youtube.com::search_results_view | 0.857143 | 0.818182 | 0.900000 | 20 |
| vmess | G2 | CT1 | youtube.com::video_playback | 0.947368 | 1.000000 | 0.900000 | 20 |
| vmess | G2 | CT2 | bing.com::search_results_view | 0.731707 | 0.714286 | 0.750000 | 20 |
| vmess | G2 | CT2 | developer.mozilla.org::document_view | 0.344828 | 0.555556 | 0.250000 | 20 |
| vmess | G2 | CT2 | github.com::repository_view | 0.883721 | 0.826087 | 0.950000 | 20 |
| vmess | G2 | CT2 | wikipedia.org::article_view | 0.695652 | 0.615385 | 0.800000 | 20 |
| vmess | G2 | CT2 | youtube.com::search_results_view | 0.883721 | 0.826087 | 0.950000 | 20 |
| vmess | G2 | CT2 | youtube.com::video_playback | 0.947368 | 1.000000 | 0.900000 | 20 |
| vmess | G2 | CT3 | bing.com::search_results_view | 0.780488 | 0.761905 | 0.800000 | 20 |
| vmess | G2 | CT3 | developer.mozilla.org::document_view | 0.000000 | 0.000000 | 0.000000 | 20 |
| vmess | G2 | CT3 | github.com::repository_view | 0.857143 | 0.818182 | 0.900000 | 20 |
| vmess | G2 | CT3 | wikipedia.org::article_view | 0.703704 | 0.558824 | 0.950000 | 20 |
| vmess | G2 | CT3 | youtube.com::search_results_view | 0.857143 | 0.818182 | 0.900000 | 20 |
| vmess | G2 | CT3 | youtube.com::video_playback | 0.900000 | 0.900000 | 0.900000 | 20 |
| vmess | G2 | CT4 | bing.com::search_results_view | 0.761905 | 0.727273 | 0.800000 | 20 |
| vmess | G2 | CT4 | developer.mozilla.org::document_view | 0.160000 | 0.400000 | 0.100000 | 20 |
| vmess | G2 | CT4 | github.com::repository_view | 0.883721 | 0.826087 | 0.950000 | 20 |
| vmess | G2 | CT4 | wikipedia.org::article_view | 0.625000 | 0.535714 | 0.750000 | 20 |
| vmess | G2 | CT4 | youtube.com::search_results_view | 0.818182 | 0.750000 | 0.900000 | 20 |
| vmess | G2 | CT4 | youtube.com::video_playback | 0.947368 | 1.000000 | 0.900000 | 20 |
| vmess | G2 | CT5 | bing.com::search_results_view | 0.800000 | 0.800000 | 0.800000 | 20 |
| vmess | G2 | CT5 | developer.mozilla.org::document_view | 0.611111 | 0.687500 | 0.550000 | 20 |
| vmess | G2 | CT5 | github.com::repository_view | 0.850000 | 0.850000 | 0.850000 | 20 |
| vmess | G2 | CT5 | wikipedia.org::article_view | 0.636364 | 0.583333 | 0.700000 | 20 |
| vmess | G2 | CT5 | youtube.com::search_results_view | 0.800000 | 0.800000 | 0.800000 | 20 |
| vmess | G2 | CT5 | youtube.com::video_playback | 0.900000 | 0.900000 | 0.900000 | 20 |
| vmess | G2 | StrongPost | bing.com::search_results_view | 0.731707 | 0.714286 | 0.750000 | 20 |
| vmess | G2 | StrongPost | developer.mozilla.org::document_view | 0.344828 | 0.555556 | 0.250000 | 20 |
| vmess | G2 | StrongPost | github.com::repository_view | 0.883721 | 0.826087 | 0.950000 | 20 |
| vmess | G2 | StrongPost | wikipedia.org::article_view | 0.695652 | 0.615385 | 0.800000 | 20 |
| vmess | G2 | StrongPost | youtube.com::search_results_view | 0.883721 | 0.826087 | 0.950000 | 20 |
| vmess | G2 | StrongPost | youtube.com::video_playback | 0.947368 | 1.000000 | 0.900000 | 20 |


## 统计口径与边界

五折先汇总完整六类混淆矩阵，再取两未覆盖类F1。三项主要比较为CT4对StrongPost、CT1及CT3，10000次共同业务分层内容bootstrap，家族校正98.3333%区间；条件于固定选定模型，不是完整训练不确定性或外部盲测。2/5个百分点辅助代价是实践筛查，不是统计非劣效。部署混合协议、节点、配置及路径效应。尚未完成独立physical-only访问提取，不把给定双侧离线资格集合推广为在线无索引攻击。
