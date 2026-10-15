# 联合仿射迁移实验详细结果附录

这些表来自2026年10月9日独立报告重放。原runner保留失败状态；主报告说明设计、统计和结论范围。表内F1、CE及Brier采用完整六类预测，逐折表仅作描述，不把六内容的小折当作独立seed。

## 全部120个目标业务组评分单元

| arm | target | group | F1_all | accuracy | CE_nats | Brier | CE_bits | F1_uncovered | F1_aux |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CT0 | shadowsocks | G0 | 0.660366 | 0.675000 | 1.635564 | 0.523092 | 2.359619 | 0.473545 | 0.753776 |
| CT0 | shadowsocks | G1 | 0.628416 | 0.691667 | 2.104775 | 0.550143 | 3.036548 | 0.259259 | 0.812994 |
| CT0 | shadowsocks | G2 | 0.509695 | 0.616667 | 2.101826 | 0.637570 | 3.032293 | 0.047619 | 0.740733 |
| CT0 | trojan | G0 | 0.859085 | 0.858333 | 0.389917 | 0.220089 | 0.562532 | 0.897436 | 0.839910 |
| CT0 | trojan | G1 | 0.841974 | 0.841667 | 0.488852 | 0.236595 | 0.705264 | 0.848348 | 0.838786 |
| CT0 | trojan | G2 | 0.836207 | 0.841667 | 0.404591 | 0.219525 | 0.583701 | 0.744582 | 0.882019 |
| CT0 | vless | G0 | 0.824833 | 0.825000 | 0.697572 | 0.309840 | 1.006383 | 0.836257 | 0.819121 |
| CT0 | vless | G1 | 0.815839 | 0.816667 | 0.841899 | 0.271481 | 1.214603 | 0.771693 | 0.837912 |
| CT0 | vless | G2 | 0.806385 | 0.808333 | 0.727813 | 0.319084 | 1.050013 | 0.804839 | 0.807158 |
| CT0 | vmess | G0 | 0.715108 | 0.716667 | 1.181982 | 0.436627 | 1.705239 | 0.711470 | 0.716927 |
| CT0 | vmess | G1 | 0.585385 | 0.666667 | 2.095708 | 0.549890 | 3.023468 | 0.178054 | 0.789050 |
| CT0 | vmess | G2 | 0.674586 | 0.733333 | 1.305332 | 0.446147 | 1.883197 | 0.473684 | 0.775037 |
| CT1 | shadowsocks | G0 | 0.661914 | 0.683333 | 1.417072 | 0.479720 | 2.044402 | 0.533333 | 0.726205 |
| CT1 | shadowsocks | G1 | 0.601072 | 0.666667 | 2.288812 | 0.577458 | 3.302058 | 0.200000 | 0.801608 |
| CT1 | shadowsocks | G2 | 0.501445 | 0.591667 | 1.870509 | 0.625512 | 2.698574 | 0.086957 | 0.708689 |
| CT1 | trojan | G0 | 0.809006 | 0.808333 | 0.577903 | 0.283412 | 0.833738 | 0.841303 | 0.792857 |
| CT1 | trojan | G1 | 0.831741 | 0.833333 | 0.492236 | 0.259862 | 0.710146 | 0.794737 | 0.850243 |
| CT1 | trojan | G2 | 0.805739 | 0.808333 | 0.621236 | 0.291960 | 0.896254 | 0.752941 | 0.832138 |
| CT1 | vless | G0 | 0.818425 | 0.816667 | 0.715093 | 0.305261 | 1.031662 | 0.864865 | 0.795205 |
| CT1 | vless | G1 | 0.830076 | 0.833333 | 0.888210 | 0.303317 | 1.281416 | 0.773994 | 0.858117 |
| CT1 | vless | G2 | 0.794555 | 0.791667 | 0.752206 | 0.323864 | 1.085204 | 0.778755 | 0.802455 |
| CT1 | vmess | G0 | 0.733545 | 0.733333 | 1.171878 | 0.433332 | 1.690662 | 0.732432 | 0.734101 |
| CT1 | vmess | G1 | 0.586789 | 0.666667 | 2.184127 | 0.589804 | 3.151030 | 0.166667 | 0.796850 |
| CT1 | vmess | G2 | 0.666721 | 0.725000 | 1.540798 | 0.479740 | 2.222902 | 0.473684 | 0.763239 |
| CT2 | shadowsocks | G0 | 0.781391 | 0.783333 | 0.856995 | 0.346557 | 1.236383 | 0.749576 | 0.797298 |
| CT2 | shadowsocks | G1 | 0.789463 | 0.791667 | 0.728036 | 0.312746 | 1.050334 | 0.732639 | 0.817875 |
| CT2 | shadowsocks | G2 | 0.676593 | 0.691667 | 1.037165 | 0.483488 | 1.496312 | 0.500000 | 0.764889 |
| CT2 | trojan | G0 | 0.865895 | 0.866667 | 0.374703 | 0.209737 | 0.540581 | 0.912805 | 0.842440 |
| CT2 | trojan | G1 | 0.884263 | 0.883333 | 0.425643 | 0.215420 | 0.614073 | 0.895357 | 0.878716 |
| CT2 | trojan | G2 | 0.855860 | 0.858333 | 0.390593 | 0.222017 | 0.563507 | 0.788635 | 0.889473 |
| CT2 | vless | G0 | 0.819103 | 0.816667 | 0.619413 | 0.290462 | 0.893624 | 0.836257 | 0.810526 |
| CT2 | vless | G1 | 0.798994 | 0.800000 | 0.670388 | 0.291443 | 0.967165 | 0.767105 | 0.814939 |
| CT2 | vless | G2 | 0.801034 | 0.800000 | 0.637598 | 0.297860 | 0.919859 | 0.827913 | 0.787594 |
| CT2 | vmess | G0 | 0.786353 | 0.783333 | 0.848564 | 0.318572 | 1.224219 | 0.839024 | 0.760017 |
| CT2 | vmess | G1 | 0.848622 | 0.850000 | 0.626187 | 0.249251 | 0.903396 | 0.777090 | 0.884388 |
| CT2 | vmess | G2 | 0.747833 | 0.766667 | 0.886049 | 0.357846 | 1.278298 | 0.646098 | 0.798700 |
| CT3 | shadowsocks | G0 | 0.722696 | 0.725000 | 1.090941 | 0.417165 | 1.573895 | 0.642857 | 0.762616 |
| CT3 | shadowsocks | G1 | 0.726764 | 0.750000 | 1.318897 | 0.422394 | 1.902766 | 0.530303 | 0.824994 |
| CT3 | shadowsocks | G2 | 0.577158 | 0.641667 | 1.245427 | 0.520694 | 1.796771 | 0.233333 | 0.749070 |
| CT3 | trojan | G0 | 0.849543 | 0.850000 | 0.423157 | 0.232231 | 0.610486 | 0.889634 | 0.829498 |
| CT3 | trojan | G1 | 0.840185 | 0.841667 | 0.433279 | 0.234514 | 0.625090 | 0.818797 | 0.850879 |
| CT3 | trojan | G2 | 0.810759 | 0.816667 | 0.404689 | 0.240606 | 0.583843 | 0.713287 | 0.859494 |
| CT3 | vless | G0 | 0.791109 | 0.791667 | 0.698658 | 0.309975 | 1.007950 | 0.783784 | 0.794771 |
| CT3 | vless | G1 | 0.781774 | 0.783333 | 0.853488 | 0.321540 | 1.231323 | 0.736842 | 0.804239 |
| CT3 | vless | G2 | 0.765509 | 0.766667 | 0.928184 | 0.391761 | 1.339087 | 0.763636 | 0.766445 |
| CT3 | vmess | G0 | 0.789199 | 0.791667 | 0.784140 | 0.319636 | 1.131274 | 0.884467 | 0.741565 |
| CT3 | vmess | G1 | 0.694744 | 0.725000 | 1.107415 | 0.429303 | 1.597662 | 0.450323 | 0.816954 |
| CT3 | vmess | G2 | 0.683080 | 0.741667 | 1.345821 | 0.425434 | 1.941609 | 0.450000 | 0.799619 |
| CT4 | shadowsocks | G0 | 0.791113 | 0.791667 | 0.644172 | 0.282941 | 0.929344 | 0.775745 | 0.798797 |
| CT4 | shadowsocks | G1 | 0.718052 | 0.741667 | 1.088381 | 0.414769 | 1.570201 | 0.496429 | 0.828864 |
| CT4 | shadowsocks | G2 | 0.713613 | 0.733333 | 1.103940 | 0.424012 | 1.592649 | 0.536866 | 0.801986 |
| CT4 | trojan | G0 | 0.857394 | 0.858333 | 0.379359 | 0.214919 | 0.547299 | 0.875598 | 0.848292 |
| CT4 | trojan | G1 | 0.849741 | 0.850000 | 0.394321 | 0.221301 | 0.568884 | 0.805405 | 0.871909 |
| CT4 | trojan | G2 | 0.900194 | 0.900000 | 0.367240 | 0.172589 | 0.529816 | 0.888031 | 0.906276 |
| CT4 | vless | G0 | 0.807163 | 0.808333 | 0.635886 | 0.292799 | 0.917389 | 0.807326 | 0.807082 |
| CT4 | vless | G1 | 0.770371 | 0.775000 | 1.008401 | 0.334675 | 1.454815 | 0.709635 | 0.800739 |
| CT4 | vless | G2 | 0.773448 | 0.775000 | 0.750772 | 0.329928 | 1.083134 | 0.758333 | 0.781005 |
| CT4 | vmess | G0 | 0.791870 | 0.791667 | 1.080114 | 0.332912 | 1.558276 | 0.820802 | 0.777405 |
| CT4 | vmess | G1 | 0.753906 | 0.766667 | 1.155379 | 0.377447 | 1.666859 | 0.581840 | 0.839938 |
| CT4 | vmess | G2 | 0.699363 | 0.733333 | 1.353685 | 0.400204 | 1.952955 | 0.553684 | 0.772202 |
| CT5 | shadowsocks | G0 | 0.852144 | 0.850000 | 0.583730 | 0.226160 | 0.842144 | 0.962179 | 0.797127 |
| CT5 | shadowsocks | G1 | 0.852144 | 0.850000 | 0.583730 | 0.226160 | 0.842144 | 0.773115 | 0.891659 |
| CT5 | shadowsocks | G2 | 0.852144 | 0.850000 | 0.583730 | 0.226160 | 0.842144 | 0.821138 | 0.867647 |
| CT5 | trojan | G0 | 0.831921 | 0.833333 | 0.663361 | 0.262865 | 0.957028 | 0.914024 | 0.790870 |
| CT5 | trojan | G1 | 0.831921 | 0.833333 | 0.663361 | 0.262865 | 0.957028 | 0.814634 | 0.840565 |
| CT5 | trojan | G2 | 0.831921 | 0.833333 | 0.663361 | 0.262865 | 0.957028 | 0.767105 | 0.864329 |
| CT5 | vless | G0 | 0.799486 | 0.800000 | 0.750140 | 0.315853 | 1.082223 | 0.820513 | 0.788972 |
| CT5 | vless | G1 | 0.799486 | 0.800000 | 0.750140 | 0.315853 | 1.082223 | 0.757143 | 0.820657 |
| CT5 | vless | G2 | 0.799486 | 0.800000 | 0.750140 | 0.315853 | 1.082223 | 0.820802 | 0.788828 |
| CT5 | vmess | G0 | 0.766246 | 0.766667 | 1.047577 | 0.394490 | 1.511334 | 0.825000 | 0.736869 |
| CT5 | vmess | G1 | 0.766246 | 0.766667 | 1.047577 | 0.394490 | 1.511334 | 0.718182 | 0.790278 |
| CT5 | vmess | G2 | 0.766246 | 0.766667 | 1.047577 | 0.394490 | 1.511334 | 0.755556 | 0.771591 |
| JA0 | shadowsocks | G0 | 0.773750 | 0.775000 | 0.746056 | 0.317911 | 1.076331 | 0.769042 | 0.776105 |
| JA0 | shadowsocks | G1 | 0.744680 | 0.758333 | 1.038454 | 0.405951 | 1.498172 | 0.579167 | 0.827437 |
| JA0 | shadowsocks | G2 | 0.596796 | 0.658333 | 1.603688 | 0.536200 | 2.313633 | 0.303030 | 0.743679 |
| JA0 | trojan | G0 | 0.800223 | 0.800000 | 0.517585 | 0.285048 | 0.746718 | 0.830634 | 0.785017 |
| JA0 | trojan | G1 | 0.803971 | 0.808333 | 0.493280 | 0.270220 | 0.711652 | 0.704762 | 0.853576 |
| JA0 | trojan | G2 | 0.812189 | 0.816667 | 0.580676 | 0.266497 | 0.837738 | 0.741830 | 0.847368 |
| JA0 | vless | G0 | 0.800888 | 0.800000 | 0.720865 | 0.310643 | 1.039988 | 0.837719 | 0.782473 |
| JA0 | vless | G1 | 0.785676 | 0.791667 | 0.783168 | 0.301385 | 1.129873 | 0.695971 | 0.830529 |
| JA0 | vless | G2 | 0.761228 | 0.758333 | 0.719273 | 0.327239 | 1.037692 | 0.708752 | 0.787466 |
| JA0 | vmess | G0 | 0.794677 | 0.791667 | 0.895666 | 0.344710 | 1.292173 | 0.832353 | 0.775839 |
| JA0 | vmess | G1 | 0.706782 | 0.733333 | 1.090773 | 0.417673 | 1.573653 | 0.492308 | 0.814020 |
| JA0 | vmess | G2 | 0.716485 | 0.766667 | 1.182778 | 0.399168 | 1.706388 | 0.521303 | 0.814077 |
| JA1 | shadowsocks | G0 | 0.791188 | 0.791667 | 0.784266 | 0.326246 | 1.131457 | 0.800000 | 0.786782 |
| JA1 | shadowsocks | G1 | 0.711294 | 0.733333 | 1.223107 | 0.460455 | 1.764571 | 0.512500 | 0.810692 |
| JA1 | shadowsocks | G2 | 0.632909 | 0.683333 | 1.153962 | 0.489914 | 1.664815 | 0.368035 | 0.765346 |
| JA1 | trojan | G0 | 0.818239 | 0.816667 | 0.472365 | 0.257471 | 0.681479 | 0.847368 | 0.803675 |
| JA1 | trojan | G1 | 0.805746 | 0.808333 | 0.537683 | 0.276557 | 0.775713 | 0.749807 | 0.833716 |
| JA1 | trojan | G2 | 0.786716 | 0.791667 | 0.497648 | 0.242320 | 0.717954 | 0.719697 | 0.820225 |
| JA1 | vless | G0 | 0.841879 | 0.841667 | 0.753227 | 0.286833 | 1.086676 | 0.857432 | 0.834103 |
| JA1 | vless | G1 | 0.813102 | 0.825000 | 0.713541 | 0.274330 | 1.029423 | 0.691667 | 0.873819 |
| JA1 | vless | G2 | 0.825453 | 0.825000 | 0.729561 | 0.288847 | 1.052534 | 0.836996 | 0.819682 |
| JA1 | vmess | G0 | 0.778714 | 0.775000 | 0.712673 | 0.313899 | 1.028170 | 0.831301 | 0.752421 |
| JA1 | vmess | G1 | 0.692142 | 0.725000 | 1.126600 | 0.446784 | 1.625340 | 0.460000 | 0.808212 |
| JA1 | vmess | G2 | 0.733075 | 0.775000 | 0.992927 | 0.367386 | 1.432490 | 0.552448 | 0.823389 |
| JA2 | shadowsocks | G0 | 0.800903 | 0.800000 | 0.939390 | 0.341506 | 1.355253 | 0.816667 | 0.793021 |
| JA2 | shadowsocks | G1 | 0.703646 | 0.725000 | 1.200066 | 0.421160 | 1.731329 | 0.514286 | 0.798327 |
| JA2 | shadowsocks | G2 | 0.612978 | 0.666667 | 1.433566 | 0.513408 | 2.068199 | 0.352941 | 0.742997 |
| JA2 | trojan | G0 | 0.793642 | 0.791667 | 0.511520 | 0.280641 | 0.737967 | 0.842105 | 0.769411 |
| JA2 | trojan | G1 | 0.831013 | 0.833333 | 0.468762 | 0.239979 | 0.676280 | 0.771429 | 0.860806 |
| JA2 | trojan | G2 | 0.816502 | 0.816667 | 0.481775 | 0.243574 | 0.695054 | 0.756757 | 0.846375 |
| JA2 | vless | G0 | 0.817870 | 0.816667 | 0.649814 | 0.281671 | 0.937483 | 0.852564 | 0.800523 |
| JA2 | vless | G1 | 0.831641 | 0.833333 | 0.779716 | 0.274594 | 1.124892 | 0.787249 | 0.853837 |
| JA2 | vless | G2 | 0.826857 | 0.825000 | 0.699186 | 0.282047 | 1.008712 | 0.836996 | 0.821787 |
| JA2 | vmess | G0 | 0.761397 | 0.758333 | 0.861162 | 0.344975 | 1.242395 | 0.813636 | 0.735277 |
| JA2 | vmess | G1 | 0.672739 | 0.716667 | 1.198342 | 0.422274 | 1.728842 | 0.397301 | 0.810458 |
| JA2 | vmess | G2 | 0.709117 | 0.758333 | 0.964372 | 0.371067 | 1.391294 | 0.509158 | 0.809097 |
| StrongPost | shadowsocks | G0 | 0.781391 | 0.783333 | 0.856995 | 0.346557 | 1.236383 | 0.749576 | 0.797298 |
| StrongPost | shadowsocks | G1 | 0.789463 | 0.791667 | 0.728036 | 0.312746 | 1.050334 | 0.732639 | 0.817875 |
| StrongPost | shadowsocks | G2 | 0.676593 | 0.691667 | 1.037165 | 0.483488 | 1.496312 | 0.500000 | 0.764889 |
| StrongPost | trojan | G0 | 0.865895 | 0.866667 | 0.374703 | 0.209737 | 0.540581 | 0.912805 | 0.842440 |
| StrongPost | trojan | G1 | 0.884263 | 0.883333 | 0.425643 | 0.215420 | 0.614073 | 0.895357 | 0.878716 |
| StrongPost | trojan | G2 | 0.855860 | 0.858333 | 0.390593 | 0.222017 | 0.563507 | 0.788635 | 0.889473 |
| StrongPost | vless | G0 | 0.819103 | 0.816667 | 0.619413 | 0.290462 | 0.893624 | 0.836257 | 0.810526 |
| StrongPost | vless | G1 | 0.798994 | 0.800000 | 0.670388 | 0.291443 | 0.967165 | 0.767105 | 0.814939 |
| StrongPost | vless | G2 | 0.801034 | 0.800000 | 0.637598 | 0.297860 | 0.919859 | 0.827913 | 0.787594 |
| StrongPost | vmess | G0 | 0.786353 | 0.783333 | 0.848564 | 0.318572 | 1.224219 | 0.839024 | 0.760017 |
| StrongPost | vmess | G1 | 0.848622 | 0.850000 | 0.626187 | 0.249251 | 0.903396 | 0.777090 | 0.884388 |
| StrongPost | vmess | G2 | 0.747833 | 0.766667 | 0.886049 | 0.357846 | 1.278298 | 0.646098 | 0.798700 |

## 全部720条逐类别结果

| arm | target | group | label | label_index | F1 | precision | recall | uncovered | support | TP | FP | FN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CT0 | shadowsocks | G0 | bing.com::search_results_view | 0 | 0.769231 | 0.789474 | 0.750000 | 否 | 20 | 15 | 4 | 5 |
| CT0 | shadowsocks | G0 | developer.mozilla.org::document_view | 1 | 0.780488 | 0.761905 | 0.800000 | 否 | 20 | 16 | 5 | 4 |
| CT0 | shadowsocks | G0 | github.com::repository_view | 2 | 0.518519 | 1.000000 | 0.350000 | 是 | 20 | 7 | 0 | 13 |
| CT0 | shadowsocks | G0 | wikipedia.org::article_view | 3 | 0.850000 | 0.850000 | 0.850000 | 否 | 20 | 17 | 3 | 3 |
| CT0 | shadowsocks | G0 | youtube.com::search_results_view | 4 | 0.428571 | 0.750000 | 0.300000 | 是 | 20 | 6 | 2 | 14 |
| CT0 | shadowsocks | G0 | youtube.com::video_playback | 5 | 0.615385 | 0.444444 | 1.000000 | 否 | 20 | 20 | 25 | 0 |
| CT0 | shadowsocks | G1 | bing.com::search_results_view | 0 | 0.518519 | 1.000000 | 0.350000 | 是 | 20 | 7 | 0 | 13 |
| CT0 | shadowsocks | G1 | developer.mozilla.org::document_view | 1 | 0.571429 | 0.418605 | 0.900000 | 否 | 20 | 18 | 25 | 2 |
| CT0 | shadowsocks | G1 | github.com::repository_view | 2 | 0.952381 | 0.909091 | 1.000000 | 否 | 20 | 20 | 2 | 0 |
| CT0 | shadowsocks | G1 | wikipedia.org::article_view | 3 | 0.000000 | 0.000000 | 0.000000 | 是 | 20 | 0 | 0 | 20 |
| CT0 | shadowsocks | G1 | youtube.com::search_results_view | 4 | 0.883721 | 0.826087 | 0.950000 | 否 | 20 | 19 | 4 | 1 |
| CT0 | shadowsocks | G1 | youtube.com::video_playback | 5 | 0.844444 | 0.760000 | 0.950000 | 否 | 20 | 19 | 6 | 1 |
| CT0 | shadowsocks | G2 | bing.com::search_results_view | 0 | 0.708333 | 0.607143 | 0.850000 | 否 | 20 | 17 | 11 | 3 |
| CT0 | shadowsocks | G2 | developer.mozilla.org::document_view | 1 | 0.000000 | 0.000000 | 0.000000 | 是 | 20 | 0 | 0 | 20 |
| CT0 | shadowsocks | G2 | github.com::repository_view | 2 | 0.883721 | 0.826087 | 0.950000 | 否 | 20 | 19 | 4 | 1 |
| CT0 | shadowsocks | G2 | wikipedia.org::article_view | 3 | 0.678571 | 0.527778 | 0.950000 | 否 | 20 | 19 | 17 | 1 |
| CT0 | shadowsocks | G2 | youtube.com::search_results_view | 4 | 0.692308 | 0.562500 | 0.900000 | 否 | 20 | 18 | 14 | 2 |
| CT0 | shadowsocks | G2 | youtube.com::video_playback | 5 | 0.095238 | 1.000000 | 0.050000 | 是 | 20 | 1 | 0 | 19 |
| CT0 | trojan | G0 | bing.com::search_results_view | 0 | 0.857143 | 0.818182 | 0.900000 | 否 | 20 | 18 | 4 | 2 |
| CT0 | trojan | G0 | developer.mozilla.org::document_view | 1 | 0.780488 | 0.761905 | 0.800000 | 否 | 20 | 16 | 5 | 4 |
| CT0 | trojan | G0 | github.com::repository_view | 2 | 0.974359 | 1.000000 | 0.950000 | 是 | 20 | 19 | 0 | 1 |
| CT0 | trojan | G0 | wikipedia.org::article_view | 3 | 0.864865 | 0.941176 | 0.800000 | 否 | 20 | 16 | 1 | 4 |
| CT0 | trojan | G0 | youtube.com::search_results_view | 4 | 0.820513 | 0.842105 | 0.800000 | 是 | 20 | 16 | 3 | 4 |
| CT0 | trojan | G0 | youtube.com::video_playback | 5 | 0.857143 | 0.818182 | 0.900000 | 否 | 20 | 18 | 4 | 2 |
| CT0 | trojan | G1 | bing.com::search_results_view | 0 | 0.918919 | 1.000000 | 0.850000 | 是 | 20 | 17 | 0 | 3 |
| CT0 | trojan | G1 | developer.mozilla.org::document_view | 1 | 0.772727 | 0.708333 | 0.850000 | 否 | 20 | 17 | 7 | 3 |
| CT0 | trojan | G1 | github.com::repository_view | 2 | 0.952381 | 0.909091 | 1.000000 | 否 | 20 | 20 | 2 | 0 |
| CT0 | trojan | G1 | wikipedia.org::article_view | 3 | 0.777778 | 0.875000 | 0.700000 | 是 | 20 | 14 | 2 | 6 |
| CT0 | trojan | G1 | youtube.com::search_results_view | 4 | 0.820513 | 0.842105 | 0.800000 | 否 | 20 | 16 | 3 | 4 |
| CT0 | trojan | G1 | youtube.com::video_playback | 5 | 0.809524 | 0.772727 | 0.850000 | 否 | 20 | 17 | 5 | 3 |
| CT0 | trojan | G2 | bing.com::search_results_view | 0 | 0.878049 | 0.857143 | 0.900000 | 否 | 20 | 18 | 3 | 2 |
| CT0 | trojan | G2 | developer.mozilla.org::document_view | 1 | 0.647059 | 0.785714 | 0.550000 | 是 | 20 | 11 | 3 | 9 |
| CT0 | trojan | G2 | github.com::repository_view | 2 | 0.975610 | 0.952381 | 1.000000 | 否 | 20 | 20 | 1 | 0 |
| CT0 | trojan | G2 | wikipedia.org::article_view | 3 | 0.790698 | 0.739130 | 0.850000 | 否 | 20 | 17 | 6 | 3 |
| CT0 | trojan | G2 | youtube.com::search_results_view | 4 | 0.883721 | 0.826087 | 0.950000 | 否 | 20 | 19 | 4 | 1 |
| CT0 | trojan | G2 | youtube.com::video_playback | 5 | 0.842105 | 0.888889 | 0.800000 | 是 | 20 | 16 | 2 | 4 |
| CT0 | vless | G0 | bing.com::search_results_view | 0 | 0.878049 | 0.857143 | 0.900000 | 否 | 20 | 18 | 3 | 2 |
| CT0 | vless | G0 | developer.mozilla.org::document_view | 1 | 0.820513 | 0.842105 | 0.800000 | 否 | 20 | 16 | 3 | 4 |
| CT0 | vless | G0 | github.com::repository_view | 2 | 0.894737 | 0.944444 | 0.850000 | 是 | 20 | 17 | 1 | 3 |
| CT0 | vless | G0 | wikipedia.org::article_view | 3 | 0.714286 | 0.681818 | 0.750000 | 否 | 20 | 15 | 7 | 5 |
| CT0 | vless | G0 | youtube.com::search_results_view | 4 | 0.777778 | 0.875000 | 0.700000 | 是 | 20 | 14 | 2 | 6 |
| CT0 | vless | G0 | youtube.com::video_playback | 5 | 0.863636 | 0.791667 | 0.950000 | 否 | 20 | 19 | 5 | 1 |
| CT0 | vless | G1 | bing.com::search_results_view | 0 | 0.894737 | 0.944444 | 0.850000 | 是 | 20 | 17 | 1 | 3 |
| CT0 | vless | G1 | developer.mozilla.org::document_view | 1 | 0.809524 | 0.772727 | 0.850000 | 否 | 20 | 17 | 5 | 3 |
| CT0 | vless | G1 | github.com::repository_view | 2 | 0.923077 | 0.947368 | 0.900000 | 否 | 20 | 18 | 1 | 2 |
| CT0 | vless | G1 | wikipedia.org::article_view | 3 | 0.648649 | 0.705882 | 0.600000 | 是 | 20 | 12 | 5 | 8 |
| CT0 | vless | G1 | youtube.com::search_results_view | 4 | 0.714286 | 0.681818 | 0.750000 | 否 | 20 | 15 | 7 | 5 |
| CT0 | vless | G1 | youtube.com::video_playback | 5 | 0.904762 | 0.863636 | 0.950000 | 否 | 20 | 19 | 3 | 1 |
| CT0 | vless | G2 | bing.com::search_results_view | 0 | 0.844444 | 0.760000 | 0.950000 | 否 | 20 | 19 | 6 | 1 |
| CT0 | vless | G2 | developer.mozilla.org::document_view | 1 | 0.709677 | 1.000000 | 0.550000 | 是 | 20 | 11 | 0 | 9 |
| CT0 | vless | G2 | github.com::repository_view | 2 | 0.923077 | 0.947368 | 0.900000 | 否 | 20 | 18 | 1 | 2 |
| CT0 | vless | G2 | wikipedia.org::article_view | 3 | 0.711111 | 0.640000 | 0.800000 | 否 | 20 | 16 | 9 | 4 |
| CT0 | vless | G2 | youtube.com::search_results_view | 4 | 0.750000 | 0.750000 | 0.750000 | 否 | 20 | 15 | 5 | 5 |
| CT0 | vless | G2 | youtube.com::video_playback | 5 | 0.900000 | 0.900000 | 0.900000 | 是 | 20 | 18 | 2 | 2 |
| CT0 | vmess | G0 | bing.com::search_results_view | 0 | 0.731707 | 0.714286 | 0.750000 | 否 | 20 | 15 | 6 | 5 |
| CT0 | vmess | G0 | developer.mozilla.org::document_view | 1 | 0.571429 | 0.545455 | 0.600000 | 否 | 20 | 12 | 10 | 8 |
| CT0 | vmess | G0 | github.com::repository_view | 2 | 0.645161 | 0.909091 | 0.500000 | 是 | 20 | 10 | 1 | 10 |
| CT0 | vmess | G0 | wikipedia.org::article_view | 3 | 0.680851 | 0.592593 | 0.800000 | 否 | 20 | 16 | 11 | 4 |
| CT0 | vmess | G0 | youtube.com::search_results_view | 4 | 0.777778 | 0.875000 | 0.700000 | 是 | 20 | 14 | 2 | 6 |
| CT0 | vmess | G0 | youtube.com::video_playback | 5 | 0.883721 | 0.826087 | 0.950000 | 否 | 20 | 19 | 4 | 1 |
| CT0 | vmess | G1 | bing.com::search_results_view | 0 | 0.260870 | 1.000000 | 0.150000 | 是 | 20 | 3 | 0 | 17 |
| CT0 | vmess | G1 | developer.mozilla.org::document_view | 1 | 0.633333 | 0.475000 | 0.950000 | 否 | 20 | 19 | 21 | 1 |
| CT0 | vmess | G1 | github.com::repository_view | 2 | 0.883721 | 0.826087 | 0.950000 | 否 | 20 | 19 | 4 | 1 |
| CT0 | vmess | G1 | wikipedia.org::article_view | 3 | 0.095238 | 1.000000 | 0.050000 | 是 | 20 | 1 | 0 | 19 |
| CT0 | vmess | G1 | youtube.com::search_results_view | 4 | 0.775510 | 0.655172 | 0.950000 | 否 | 20 | 19 | 10 | 1 |
| CT0 | vmess | G1 | youtube.com::video_playback | 5 | 0.863636 | 0.791667 | 0.950000 | 否 | 20 | 19 | 5 | 1 |
| CT0 | vmess | G2 | bing.com::search_results_view | 0 | 0.739130 | 0.653846 | 0.850000 | 否 | 20 | 17 | 9 | 3 |
| CT0 | vmess | G2 | developer.mozilla.org::document_view | 1 | 0.000000 | 0.000000 | 0.000000 | 是 | 20 | 0 | 0 | 20 |
| CT0 | vmess | G2 | github.com::repository_view | 2 | 0.837209 | 0.782609 | 0.900000 | 否 | 20 | 18 | 5 | 2 |
| CT0 | vmess | G2 | wikipedia.org::article_view | 3 | 0.666667 | 0.548387 | 0.850000 | 否 | 20 | 17 | 14 | 3 |
| CT0 | vmess | G2 | youtube.com::search_results_view | 4 | 0.857143 | 0.818182 | 0.900000 | 否 | 20 | 18 | 4 | 2 |
| CT0 | vmess | G2 | youtube.com::video_playback | 5 | 0.947368 | 1.000000 | 0.900000 | 是 | 20 | 18 | 0 | 2 |
| CT1 | shadowsocks | G0 | bing.com::search_results_view | 0 | 0.736842 | 0.777778 | 0.700000 | 否 | 20 | 14 | 4 | 6 |
| CT1 | shadowsocks | G0 | developer.mozilla.org::document_view | 1 | 0.711111 | 0.640000 | 0.800000 | 否 | 20 | 16 | 9 | 4 |
| CT1 | shadowsocks | G0 | github.com::repository_view | 2 | 0.400000 | 1.000000 | 0.250000 | 是 | 20 | 5 | 0 | 15 |
| CT1 | shadowsocks | G0 | wikipedia.org::article_view | 3 | 0.765957 | 0.666667 | 0.900000 | 否 | 20 | 18 | 9 | 2 |
| CT1 | shadowsocks | G0 | youtube.com::search_results_view | 4 | 0.666667 | 1.000000 | 0.500000 | 是 | 20 | 10 | 0 | 10 |
| CT1 | shadowsocks | G0 | youtube.com::video_playback | 5 | 0.690909 | 0.542857 | 0.950000 | 否 | 20 | 19 | 16 | 1 |
| CT1 | shadowsocks | G1 | bing.com::search_results_view | 0 | 0.400000 | 1.000000 | 0.250000 | 是 | 20 | 5 | 0 | 15 |
| CT1 | shadowsocks | G1 | developer.mozilla.org::document_view | 1 | 0.558824 | 0.395833 | 0.950000 | 否 | 20 | 19 | 29 | 1 |
| CT1 | shadowsocks | G1 | github.com::repository_view | 2 | 0.857143 | 0.818182 | 0.900000 | 否 | 20 | 18 | 4 | 2 |
| CT1 | shadowsocks | G1 | wikipedia.org::article_view | 3 | 0.000000 | 0.000000 | 0.000000 | 是 | 20 | 0 | 0 | 20 |
| CT1 | shadowsocks | G1 | youtube.com::search_results_view | 4 | 0.926829 | 0.904762 | 0.950000 | 否 | 20 | 19 | 2 | 1 |
| CT1 | shadowsocks | G1 | youtube.com::video_playback | 5 | 0.863636 | 0.791667 | 0.950000 | 否 | 20 | 19 | 5 | 1 |
| CT1 | shadowsocks | G2 | bing.com::search_results_view | 0 | 0.666667 | 0.600000 | 0.750000 | 否 | 20 | 15 | 10 | 5 |
| CT1 | shadowsocks | G2 | developer.mozilla.org::document_view | 1 | 0.000000 | 0.000000 | 0.000000 | 是 | 20 | 0 | 0 | 20 |
| CT1 | shadowsocks | G2 | github.com::repository_view | 2 | 0.883721 | 0.826087 | 0.950000 | 否 | 20 | 19 | 4 | 1 |
| CT1 | shadowsocks | G2 | wikipedia.org::article_view | 3 | 0.642857 | 0.500000 | 0.900000 | 否 | 20 | 18 | 18 | 2 |
| CT1 | shadowsocks | G2 | youtube.com::search_results_view | 4 | 0.641509 | 0.515152 | 0.850000 | 否 | 20 | 17 | 16 | 3 |
| CT1 | shadowsocks | G2 | youtube.com::video_playback | 5 | 0.173913 | 0.666667 | 0.100000 | 是 | 20 | 2 | 1 | 18 |
| CT1 | trojan | G0 | bing.com::search_results_view | 0 | 0.800000 | 0.800000 | 0.800000 | 否 | 20 | 16 | 4 | 4 |
| CT1 | trojan | G0 | developer.mozilla.org::document_view | 1 | 0.714286 | 0.681818 | 0.750000 | 否 | 20 | 15 | 7 | 5 |
| CT1 | trojan | G0 | github.com::repository_view | 2 | 0.871795 | 0.894737 | 0.850000 | 是 | 20 | 17 | 2 | 3 |
| CT1 | trojan | G0 | wikipedia.org::article_view | 3 | 0.800000 | 0.800000 | 0.800000 | 否 | 20 | 16 | 4 | 4 |
| CT1 | trojan | G0 | youtube.com::search_results_view | 4 | 0.810811 | 0.882353 | 0.750000 | 是 | 20 | 15 | 2 | 5 |
| CT1 | trojan | G0 | youtube.com::video_playback | 5 | 0.857143 | 0.818182 | 0.900000 | 否 | 20 | 18 | 4 | 2 |
| CT1 | trojan | G1 | bing.com::search_results_view | 0 | 0.789474 | 0.833333 | 0.750000 | 是 | 20 | 15 | 3 | 5 |
| CT1 | trojan | G1 | developer.mozilla.org::document_view | 1 | 0.808511 | 0.703704 | 0.950000 | 否 | 20 | 19 | 8 | 1 |
| CT1 | trojan | G1 | github.com::repository_view | 2 | 0.952381 | 0.909091 | 1.000000 | 否 | 20 | 20 | 2 | 0 |
| CT1 | trojan | G1 | wikipedia.org::article_view | 3 | 0.800000 | 0.933333 | 0.700000 | 是 | 20 | 14 | 1 | 6 |
| CT1 | trojan | G1 | youtube.com::search_results_view | 4 | 0.810811 | 0.882353 | 0.750000 | 否 | 20 | 15 | 2 | 5 |
| CT1 | trojan | G1 | youtube.com::video_playback | 5 | 0.829268 | 0.809524 | 0.850000 | 否 | 20 | 17 | 4 | 3 |
| CT1 | trojan | G2 | bing.com::search_results_view | 0 | 0.850000 | 0.850000 | 0.850000 | 否 | 20 | 17 | 3 | 3 |
| CT1 | trojan | G2 | developer.mozilla.org::document_view | 1 | 0.705882 | 0.857143 | 0.600000 | 是 | 20 | 12 | 2 | 8 |
| CT1 | trojan | G2 | github.com::repository_view | 2 | 0.930233 | 0.869565 | 1.000000 | 否 | 20 | 20 | 3 | 0 |
| CT1 | trojan | G2 | wikipedia.org::article_view | 3 | 0.711111 | 0.640000 | 0.800000 | 否 | 20 | 16 | 9 | 4 |
| CT1 | trojan | G2 | youtube.com::search_results_view | 4 | 0.837209 | 0.782609 | 0.900000 | 否 | 20 | 18 | 5 | 2 |
| CT1 | trojan | G2 | youtube.com::video_playback | 5 | 0.800000 | 0.933333 | 0.700000 | 是 | 20 | 14 | 1 | 6 |
| CT1 | vless | G0 | bing.com::search_results_view | 0 | 0.850000 | 0.850000 | 0.850000 | 否 | 20 | 17 | 3 | 3 |
| CT1 | vless | G0 | developer.mozilla.org::document_view | 1 | 0.761905 | 0.727273 | 0.800000 | 否 | 20 | 16 | 6 | 4 |
| CT1 | vless | G0 | github.com::repository_view | 2 | 0.918919 | 1.000000 | 0.850000 | 是 | 20 | 17 | 0 | 3 |
| CT1 | vless | G0 | wikipedia.org::article_view | 3 | 0.731707 | 0.714286 | 0.750000 | 否 | 20 | 15 | 6 | 5 |
| CT1 | vless | G0 | youtube.com::search_results_view | 4 | 0.810811 | 0.882353 | 0.750000 | 是 | 20 | 15 | 2 | 5 |
| CT1 | vless | G0 | youtube.com::video_playback | 5 | 0.837209 | 0.782609 | 0.900000 | 否 | 20 | 18 | 5 | 2 |
| CT1 | vless | G1 | bing.com::search_results_view | 0 | 0.842105 | 0.888889 | 0.800000 | 是 | 20 | 16 | 2 | 4 |
| CT1 | vless | G1 | developer.mozilla.org::document_view | 1 | 0.818182 | 0.750000 | 0.900000 | 否 | 20 | 18 | 6 | 2 |
| CT1 | vless | G1 | github.com::repository_view | 2 | 0.900000 | 0.900000 | 0.900000 | 否 | 20 | 18 | 2 | 2 |
| CT1 | vless | G1 | wikipedia.org::article_view | 3 | 0.705882 | 0.857143 | 0.600000 | 是 | 20 | 12 | 2 | 8 |
| CT1 | vless | G1 | youtube.com::search_results_view | 4 | 0.809524 | 0.772727 | 0.850000 | 否 | 20 | 17 | 5 | 3 |
| CT1 | vless | G1 | youtube.com::video_playback | 5 | 0.904762 | 0.863636 | 0.950000 | 否 | 20 | 19 | 3 | 1 |
| CT1 | vless | G2 | bing.com::search_results_view | 0 | 0.878049 | 0.857143 | 0.900000 | 否 | 20 | 18 | 3 | 2 |
| CT1 | vless | G2 | developer.mozilla.org::document_view | 1 | 0.685714 | 0.800000 | 0.600000 | 是 | 20 | 12 | 3 | 8 |
| CT1 | vless | G2 | github.com::repository_view | 2 | 0.923077 | 0.947368 | 0.900000 | 否 | 20 | 18 | 1 | 2 |
| CT1 | vless | G2 | wikipedia.org::article_view | 3 | 0.608696 | 0.538462 | 0.700000 | 否 | 20 | 14 | 12 | 6 |
| CT1 | vless | G2 | youtube.com::search_results_view | 4 | 0.800000 | 0.800000 | 0.800000 | 否 | 20 | 16 | 4 | 4 |
| CT1 | vless | G2 | youtube.com::video_playback | 5 | 0.871795 | 0.894737 | 0.850000 | 是 | 20 | 17 | 2 | 3 |
| CT1 | vmess | G0 | bing.com::search_results_view | 0 | 0.769231 | 0.789474 | 0.750000 | 否 | 20 | 15 | 4 | 5 |
| CT1 | vmess | G0 | developer.mozilla.org::document_view | 1 | 0.595745 | 0.518519 | 0.700000 | 否 | 20 | 14 | 13 | 6 |
| CT1 | vmess | G0 | github.com::repository_view | 2 | 0.600000 | 0.900000 | 0.450000 | 是 | 20 | 9 | 1 | 11 |
| CT1 | vmess | G0 | wikipedia.org::article_view | 3 | 0.666667 | 0.600000 | 0.750000 | 否 | 20 | 15 | 10 | 5 |
| CT1 | vmess | G0 | youtube.com::search_results_view | 4 | 0.864865 | 0.941176 | 0.800000 | 是 | 20 | 16 | 1 | 4 |
| CT1 | vmess | G0 | youtube.com::video_playback | 5 | 0.904762 | 0.863636 | 0.950000 | 否 | 20 | 19 | 3 | 1 |
| CT1 | vmess | G1 | bing.com::search_results_view | 0 | 0.333333 | 1.000000 | 0.200000 | 是 | 20 | 4 | 0 | 16 |
| CT1 | vmess | G1 | developer.mozilla.org::document_view | 1 | 0.593750 | 0.431818 | 0.950000 | 否 | 20 | 19 | 25 | 1 |
| CT1 | vmess | G1 | github.com::repository_view | 2 | 0.904762 | 0.863636 | 0.950000 | 否 | 20 | 19 | 3 | 1 |
| CT1 | vmess | G1 | wikipedia.org::article_view | 3 | 0.000000 | 0.000000 | 0.000000 | 是 | 20 | 0 | 0 | 20 |
| CT1 | vmess | G1 | youtube.com::search_results_view | 4 | 0.844444 | 0.760000 | 0.950000 | 否 | 20 | 19 | 6 | 1 |
| CT1 | vmess | G1 | youtube.com::video_playback | 5 | 0.844444 | 0.760000 | 0.950000 | 否 | 20 | 19 | 6 | 1 |
| CT1 | vmess | G2 | bing.com::search_results_view | 0 | 0.693878 | 0.586207 | 0.850000 | 否 | 20 | 17 | 12 | 3 |
| CT1 | vmess | G2 | developer.mozilla.org::document_view | 1 | 0.000000 | 0.000000 | 0.000000 | 是 | 20 | 0 | 0 | 20 |
| CT1 | vmess | G2 | github.com::repository_view | 2 | 0.863636 | 0.791667 | 0.950000 | 否 | 20 | 19 | 5 | 1 |
| CT1 | vmess | G2 | wikipedia.org::article_view | 3 | 0.638298 | 0.555556 | 0.750000 | 否 | 20 | 15 | 12 | 5 |
| CT1 | vmess | G2 | youtube.com::search_results_view | 4 | 0.857143 | 0.818182 | 0.900000 | 否 | 20 | 18 | 4 | 2 |
| CT1 | vmess | G2 | youtube.com::video_playback | 5 | 0.947368 | 1.000000 | 0.900000 | 是 | 20 | 18 | 0 | 2 |
| CT2 | shadowsocks | G0 | bing.com::search_results_view | 0 | 0.789474 | 0.833333 | 0.750000 | 否 | 20 | 15 | 3 | 5 |
| CT2 | shadowsocks | G0 | developer.mozilla.org::document_view | 1 | 0.780488 | 0.761905 | 0.800000 | 否 | 20 | 16 | 5 | 4 |
| CT2 | shadowsocks | G0 | github.com::repository_view | 2 | 0.709677 | 1.000000 | 0.550000 | 是 | 20 | 11 | 0 | 9 |
| CT2 | shadowsocks | G0 | wikipedia.org::article_view | 3 | 0.850000 | 0.850000 | 0.850000 | 否 | 20 | 17 | 3 | 3 |
| CT2 | shadowsocks | G0 | youtube.com::search_results_view | 4 | 0.789474 | 0.833333 | 0.750000 | 是 | 20 | 15 | 3 | 5 |
| CT2 | shadowsocks | G0 | youtube.com::video_playback | 5 | 0.769231 | 0.625000 | 1.000000 | 否 | 20 | 20 | 12 | 0 |
| CT2 | shadowsocks | G1 | bing.com::search_results_view | 0 | 0.777778 | 0.875000 | 0.700000 | 是 | 20 | 14 | 2 | 6 |
| CT2 | shadowsocks | G1 | developer.mozilla.org::document_view | 1 | 0.723404 | 0.629630 | 0.850000 | 否 | 20 | 17 | 10 | 3 |
| CT2 | shadowsocks | G1 | github.com::repository_view | 2 | 0.864865 | 0.941176 | 0.800000 | 否 | 20 | 16 | 1 | 4 |
| CT2 | shadowsocks | G1 | wikipedia.org::article_view | 3 | 0.687500 | 0.916667 | 0.550000 | 是 | 20 | 11 | 1 | 9 |
| CT2 | shadowsocks | G1 | youtube.com::search_results_view | 4 | 0.857143 | 0.818182 | 0.900000 | 否 | 20 | 18 | 4 | 2 |
| CT2 | shadowsocks | G1 | youtube.com::video_playback | 5 | 0.826087 | 0.730769 | 0.950000 | 否 | 20 | 19 | 7 | 1 |
| CT2 | shadowsocks | G2 | bing.com::search_results_view | 0 | 0.755556 | 0.680000 | 0.850000 | 否 | 20 | 17 | 8 | 3 |
| CT2 | shadowsocks | G2 | developer.mozilla.org::document_view | 1 | 0.400000 | 0.600000 | 0.300000 | 是 | 20 | 6 | 4 | 14 |
| CT2 | shadowsocks | G2 | github.com::repository_view | 2 | 0.871795 | 0.894737 | 0.850000 | 否 | 20 | 17 | 2 | 3 |
| CT2 | shadowsocks | G2 | wikipedia.org::article_view | 3 | 0.641509 | 0.515152 | 0.850000 | 否 | 20 | 17 | 16 | 3 |
| CT2 | shadowsocks | G2 | youtube.com::search_results_view | 4 | 0.790698 | 0.739130 | 0.850000 | 否 | 20 | 17 | 6 | 3 |
| CT2 | shadowsocks | G2 | youtube.com::video_playback | 5 | 0.600000 | 0.900000 | 0.450000 | 是 | 20 | 9 | 1 | 11 |
| CT2 | trojan | G0 | bing.com::search_results_view | 0 | 0.850000 | 0.850000 | 0.850000 | 否 | 20 | 17 | 3 | 3 |
| CT2 | trojan | G0 | developer.mozilla.org::document_view | 1 | 0.820513 | 0.842105 | 0.800000 | 否 | 20 | 16 | 3 | 4 |
| CT2 | trojan | G0 | github.com::repository_view | 2 | 0.975610 | 0.952381 | 1.000000 | 是 | 20 | 20 | 1 | 0 |
| CT2 | trojan | G0 | wikipedia.org::article_view | 3 | 0.842105 | 0.888889 | 0.800000 | 否 | 20 | 16 | 2 | 4 |
| CT2 | trojan | G0 | youtube.com::search_results_view | 4 | 0.850000 | 0.850000 | 0.850000 | 是 | 20 | 17 | 3 | 3 |
| CT2 | trojan | G0 | youtube.com::video_playback | 5 | 0.857143 | 0.818182 | 0.900000 | 否 | 20 | 18 | 4 | 2 |
| CT2 | trojan | G1 | bing.com::search_results_view | 0 | 0.918919 | 1.000000 | 0.850000 | 是 | 20 | 17 | 0 | 3 |
| CT2 | trojan | G1 | developer.mozilla.org::document_view | 1 | 0.837209 | 0.782609 | 0.900000 | 否 | 20 | 18 | 5 | 2 |
| CT2 | trojan | G1 | github.com::repository_view | 2 | 1.000000 | 1.000000 | 1.000000 | 否 | 20 | 20 | 0 | 0 |
| CT2 | trojan | G1 | wikipedia.org::article_view | 3 | 0.871795 | 0.894737 | 0.850000 | 是 | 20 | 17 | 2 | 3 |
| CT2 | trojan | G1 | youtube.com::search_results_view | 4 | 0.820513 | 0.842105 | 0.800000 | 否 | 20 | 16 | 3 | 4 |
| CT2 | trojan | G1 | youtube.com::video_playback | 5 | 0.857143 | 0.818182 | 0.900000 | 否 | 20 | 18 | 4 | 2 |
| CT2 | trojan | G2 | bing.com::search_results_view | 0 | 0.878049 | 0.857143 | 0.900000 | 否 | 20 | 18 | 3 | 2 |
| CT2 | trojan | G2 | developer.mozilla.org::document_view | 1 | 0.756757 | 0.823529 | 0.700000 | 是 | 20 | 14 | 3 | 6 |
| CT2 | trojan | G2 | github.com::repository_view | 2 | 0.975610 | 0.952381 | 1.000000 | 否 | 20 | 20 | 1 | 0 |
| CT2 | trojan | G2 | wikipedia.org::article_view | 3 | 0.820513 | 0.842105 | 0.800000 | 否 | 20 | 16 | 3 | 4 |
| CT2 | trojan | G2 | youtube.com::search_results_view | 4 | 0.883721 | 0.826087 | 0.950000 | 否 | 20 | 19 | 4 | 1 |
| CT2 | trojan | G2 | youtube.com::video_playback | 5 | 0.820513 | 0.842105 | 0.800000 | 是 | 20 | 16 | 3 | 4 |
| CT2 | vless | G0 | bing.com::search_results_view | 0 | 0.923077 | 0.947368 | 0.900000 | 否 | 20 | 18 | 1 | 2 |
| CT2 | vless | G0 | developer.mozilla.org::document_view | 1 | 0.800000 | 0.800000 | 0.800000 | 否 | 20 | 16 | 4 | 4 |
| CT2 | vless | G0 | github.com::repository_view | 2 | 0.894737 | 0.944444 | 0.850000 | 是 | 20 | 17 | 1 | 3 |
| CT2 | vless | G0 | wikipedia.org::article_view | 3 | 0.681818 | 0.625000 | 0.750000 | 否 | 20 | 15 | 9 | 5 |
| CT2 | vless | G0 | youtube.com::search_results_view | 4 | 0.777778 | 0.875000 | 0.700000 | 是 | 20 | 14 | 2 | 6 |
| CT2 | vless | G0 | youtube.com::video_playback | 5 | 0.837209 | 0.782609 | 0.900000 | 否 | 20 | 18 | 5 | 2 |
| CT2 | vless | G1 | bing.com::search_results_view | 0 | 0.850000 | 0.850000 | 0.850000 | 是 | 20 | 17 | 3 | 3 |
| CT2 | vless | G1 | developer.mozilla.org::document_view | 1 | 0.750000 | 0.750000 | 0.750000 | 否 | 20 | 15 | 5 | 5 |
| CT2 | vless | G1 | github.com::repository_view | 2 | 0.900000 | 0.900000 | 0.900000 | 否 | 20 | 18 | 2 | 2 |
| CT2 | vless | G1 | wikipedia.org::article_view | 3 | 0.684211 | 0.722222 | 0.650000 | 是 | 20 | 13 | 5 | 7 |
| CT2 | vless | G1 | youtube.com::search_results_view | 4 | 0.731707 | 0.714286 | 0.750000 | 否 | 20 | 15 | 6 | 5 |
| CT2 | vless | G1 | youtube.com::video_playback | 5 | 0.878049 | 0.857143 | 0.900000 | 否 | 20 | 18 | 3 | 2 |
| CT2 | vless | G2 | bing.com::search_results_view | 0 | 0.904762 | 0.863636 | 0.950000 | 否 | 20 | 19 | 3 | 1 |
| CT2 | vless | G2 | developer.mozilla.org::document_view | 1 | 0.777778 | 0.875000 | 0.700000 | 是 | 20 | 14 | 2 | 6 |
| CT2 | vless | G2 | github.com::repository_view | 2 | 0.894737 | 0.944444 | 0.850000 | 否 | 20 | 17 | 1 | 3 |
| CT2 | vless | G2 | wikipedia.org::article_view | 3 | 0.666667 | 0.600000 | 0.750000 | 否 | 20 | 15 | 10 | 5 |
| CT2 | vless | G2 | youtube.com::search_results_view | 4 | 0.684211 | 0.722222 | 0.650000 | 否 | 20 | 13 | 5 | 7 |
| CT2 | vless | G2 | youtube.com::video_playback | 5 | 0.878049 | 0.857143 | 0.900000 | 是 | 20 | 18 | 3 | 2 |
| CT2 | vmess | G0 | bing.com::search_results_view | 0 | 0.769231 | 0.789474 | 0.750000 | 否 | 20 | 15 | 4 | 5 |
| CT2 | vmess | G0 | developer.mozilla.org::document_view | 1 | 0.585366 | 0.571429 | 0.600000 | 否 | 20 | 12 | 9 | 8 |
| CT2 | vmess | G0 | github.com::repository_view | 2 | 0.800000 | 0.933333 | 0.700000 | 是 | 20 | 14 | 1 | 6 |
| CT2 | vmess | G0 | wikipedia.org::article_view | 3 | 0.711111 | 0.640000 | 0.800000 | 否 | 20 | 16 | 9 | 4 |
| CT2 | vmess | G0 | youtube.com::search_results_view | 4 | 0.878049 | 0.857143 | 0.900000 | 是 | 20 | 18 | 3 | 2 |
| CT2 | vmess | G0 | youtube.com::video_playback | 5 | 0.974359 | 1.000000 | 0.950000 | 否 | 20 | 19 | 0 | 1 |
| CT2 | vmess | G1 | bing.com::search_results_view | 0 | 0.789474 | 0.833333 | 0.750000 | 是 | 20 | 15 | 3 | 5 |
| CT2 | vmess | G1 | developer.mozilla.org::document_view | 1 | 0.727273 | 0.666667 | 0.800000 | 否 | 20 | 16 | 8 | 4 |
| CT2 | vmess | G1 | github.com::repository_view | 2 | 0.926829 | 0.904762 | 0.950000 | 否 | 20 | 19 | 2 | 1 |
| CT2 | vmess | G1 | wikipedia.org::article_view | 3 | 0.764706 | 0.928571 | 0.650000 | 是 | 20 | 13 | 1 | 7 |
| CT2 | vmess | G1 | youtube.com::search_results_view | 4 | 0.909091 | 0.833333 | 1.000000 | 否 | 20 | 20 | 4 | 0 |
| CT2 | vmess | G1 | youtube.com::video_playback | 5 | 0.974359 | 1.000000 | 0.950000 | 否 | 20 | 19 | 0 | 1 |
| CT2 | vmess | G2 | bing.com::search_results_view | 0 | 0.731707 | 0.714286 | 0.750000 | 否 | 20 | 15 | 6 | 5 |
| CT2 | vmess | G2 | developer.mozilla.org::document_view | 1 | 0.344828 | 0.555556 | 0.250000 | 是 | 20 | 5 | 4 | 15 |
| CT2 | vmess | G2 | github.com::repository_view | 2 | 0.883721 | 0.826087 | 0.950000 | 否 | 20 | 19 | 4 | 1 |
| CT2 | vmess | G2 | wikipedia.org::article_view | 3 | 0.695652 | 0.615385 | 0.800000 | 否 | 20 | 16 | 10 | 4 |
| CT2 | vmess | G2 | youtube.com::search_results_view | 4 | 0.883721 | 0.826087 | 0.950000 | 否 | 20 | 19 | 4 | 1 |
| CT2 | vmess | G2 | youtube.com::video_playback | 5 | 0.947368 | 1.000000 | 0.900000 | 是 | 20 | 18 | 0 | 2 |
| CT3 | shadowsocks | G0 | bing.com::search_results_view | 0 | 0.789474 | 0.833333 | 0.750000 | 否 | 20 | 15 | 3 | 5 |
| CT3 | shadowsocks | G0 | developer.mozilla.org::document_view | 1 | 0.761905 | 0.727273 | 0.800000 | 否 | 20 | 16 | 6 | 4 |
| CT3 | shadowsocks | G0 | github.com::repository_view | 2 | 0.600000 | 0.900000 | 0.450000 | 是 | 20 | 9 | 1 | 11 |
| CT3 | shadowsocks | G0 | wikipedia.org::article_view | 3 | 0.820513 | 0.842105 | 0.800000 | 否 | 20 | 16 | 3 | 4 |
| CT3 | shadowsocks | G0 | youtube.com::search_results_view | 4 | 0.685714 | 0.800000 | 0.600000 | 是 | 20 | 12 | 3 | 8 |
| CT3 | shadowsocks | G0 | youtube.com::video_playback | 5 | 0.678571 | 0.527778 | 0.950000 | 否 | 20 | 19 | 17 | 1 |
| CT3 | shadowsocks | G1 | bing.com::search_results_view | 0 | 0.727273 | 0.923077 | 0.600000 | 是 | 20 | 12 | 1 | 8 |
| CT3 | shadowsocks | G1 | developer.mozilla.org::document_view | 1 | 0.631579 | 0.486486 | 0.900000 | 否 | 20 | 18 | 19 | 2 |
| CT3 | shadowsocks | G1 | github.com::repository_view | 2 | 0.900000 | 0.900000 | 0.900000 | 否 | 20 | 18 | 2 | 2 |
| CT3 | shadowsocks | G1 | wikipedia.org::article_view | 3 | 0.333333 | 1.000000 | 0.200000 | 是 | 20 | 4 | 0 | 16 |
| CT3 | shadowsocks | G1 | youtube.com::search_results_view | 4 | 0.904762 | 0.863636 | 0.950000 | 否 | 20 | 19 | 3 | 1 |
| CT3 | shadowsocks | G1 | youtube.com::video_playback | 5 | 0.863636 | 0.791667 | 0.950000 | 否 | 20 | 19 | 5 | 1 |
| CT3 | shadowsocks | G2 | bing.com::search_results_view | 0 | 0.695652 | 0.615385 | 0.800000 | 否 | 20 | 16 | 10 | 4 |
| CT3 | shadowsocks | G2 | developer.mozilla.org::document_view | 1 | 0.000000 | 0.000000 | 0.000000 | 是 | 20 | 0 | 0 | 20 |
| CT3 | shadowsocks | G2 | github.com::repository_view | 2 | 0.923077 | 0.947368 | 0.900000 | 否 | 20 | 18 | 1 | 2 |
| CT3 | shadowsocks | G2 | wikipedia.org::article_view | 3 | 0.642857 | 0.500000 | 0.900000 | 否 | 20 | 18 | 18 | 2 |
| CT3 | shadowsocks | G2 | youtube.com::search_results_view | 4 | 0.734694 | 0.620690 | 0.900000 | 否 | 20 | 18 | 11 | 2 |
| CT3 | shadowsocks | G2 | youtube.com::video_playback | 5 | 0.466667 | 0.700000 | 0.350000 | 是 | 20 | 7 | 3 | 13 |
| CT3 | trojan | G0 | bing.com::search_results_view | 0 | 0.829268 | 0.809524 | 0.850000 | 否 | 20 | 17 | 4 | 3 |
| CT3 | trojan | G0 | developer.mozilla.org::document_view | 1 | 0.789474 | 0.833333 | 0.750000 | 否 | 20 | 15 | 3 | 5 |
| CT3 | trojan | G0 | github.com::repository_view | 2 | 0.950000 | 0.950000 | 0.950000 | 是 | 20 | 19 | 1 | 1 |
| CT3 | trojan | G0 | wikipedia.org::article_view | 3 | 0.842105 | 0.888889 | 0.800000 | 否 | 20 | 16 | 2 | 4 |
| CT3 | trojan | G0 | youtube.com::search_results_view | 4 | 0.829268 | 0.809524 | 0.850000 | 是 | 20 | 17 | 4 | 3 |
| CT3 | trojan | G0 | youtube.com::video_playback | 5 | 0.857143 | 0.818182 | 0.900000 | 否 | 20 | 18 | 4 | 2 |
| CT3 | trojan | G1 | bing.com::search_results_view | 0 | 0.894737 | 0.944444 | 0.850000 | 是 | 20 | 17 | 1 | 3 |
| CT3 | trojan | G1 | developer.mozilla.org::document_view | 1 | 0.790698 | 0.739130 | 0.850000 | 否 | 20 | 17 | 6 | 3 |
| CT3 | trojan | G1 | github.com::repository_view | 2 | 0.975610 | 0.952381 | 1.000000 | 否 | 20 | 20 | 1 | 0 |
| CT3 | trojan | G1 | wikipedia.org::article_view | 3 | 0.742857 | 0.866667 | 0.650000 | 是 | 20 | 13 | 2 | 7 |
| CT3 | trojan | G1 | youtube.com::search_results_view | 4 | 0.800000 | 0.800000 | 0.800000 | 否 | 20 | 16 | 4 | 4 |
| CT3 | trojan | G1 | youtube.com::video_playback | 5 | 0.837209 | 0.782609 | 0.900000 | 否 | 20 | 18 | 5 | 2 |
| CT3 | trojan | G2 | bing.com::search_results_view | 0 | 0.900000 | 0.900000 | 0.900000 | 否 | 20 | 18 | 2 | 2 |
| CT3 | trojan | G2 | developer.mozilla.org::document_view | 1 | 0.606061 | 0.769231 | 0.500000 | 是 | 20 | 10 | 3 | 10 |
| CT3 | trojan | G2 | github.com::repository_view | 2 | 0.975610 | 0.952381 | 1.000000 | 否 | 20 | 20 | 1 | 0 |
| CT3 | trojan | G2 | wikipedia.org::article_view | 3 | 0.744186 | 0.695652 | 0.800000 | 否 | 20 | 16 | 7 | 4 |
| CT3 | trojan | G2 | youtube.com::search_results_view | 4 | 0.818182 | 0.750000 | 0.900000 | 否 | 20 | 18 | 6 | 2 |
| CT3 | trojan | G2 | youtube.com::video_playback | 5 | 0.820513 | 0.842105 | 0.800000 | 是 | 20 | 16 | 3 | 4 |
| CT3 | vless | G0 | bing.com::search_results_view | 0 | 0.857143 | 0.818182 | 0.900000 | 否 | 20 | 18 | 4 | 2 |
| CT3 | vless | G0 | developer.mozilla.org::document_view | 1 | 0.789474 | 0.833333 | 0.750000 | 否 | 20 | 15 | 3 | 5 |
| CT3 | vless | G0 | github.com::repository_view | 2 | 0.810811 | 0.882353 | 0.750000 | 是 | 20 | 15 | 2 | 5 |
| CT3 | vless | G0 | wikipedia.org::article_view | 3 | 0.714286 | 0.681818 | 0.750000 | 否 | 20 | 15 | 7 | 5 |
| CT3 | vless | G0 | youtube.com::search_results_view | 4 | 0.756757 | 0.823529 | 0.700000 | 是 | 20 | 14 | 3 | 6 |
| CT3 | vless | G0 | youtube.com::video_playback | 5 | 0.818182 | 0.750000 | 0.900000 | 否 | 20 | 18 | 6 | 2 |
| CT3 | vless | G1 | bing.com::search_results_view | 0 | 0.789474 | 0.833333 | 0.750000 | 是 | 20 | 15 | 3 | 5 |
| CT3 | vless | G1 | developer.mozilla.org::document_view | 1 | 0.780488 | 0.761905 | 0.800000 | 否 | 20 | 16 | 5 | 4 |
| CT3 | vless | G1 | github.com::repository_view | 2 | 0.800000 | 0.800000 | 0.800000 | 否 | 20 | 16 | 4 | 4 |
| CT3 | vless | G1 | wikipedia.org::article_view | 3 | 0.684211 | 0.722222 | 0.650000 | 是 | 20 | 13 | 5 | 7 |
| CT3 | vless | G1 | youtube.com::search_results_view | 4 | 0.731707 | 0.714286 | 0.750000 | 否 | 20 | 15 | 6 | 5 |
| CT3 | vless | G1 | youtube.com::video_playback | 5 | 0.904762 | 0.863636 | 0.950000 | 否 | 20 | 19 | 3 | 1 |
| CT3 | vless | G2 | bing.com::search_results_view | 0 | 0.837209 | 0.782609 | 0.900000 | 否 | 20 | 18 | 5 | 2 |
| CT3 | vless | G2 | developer.mozilla.org::document_view | 1 | 0.727273 | 0.923077 | 0.600000 | 是 | 20 | 12 | 1 | 8 |
| CT3 | vless | G2 | github.com::repository_view | 2 | 0.800000 | 0.800000 | 0.800000 | 否 | 20 | 16 | 4 | 4 |
| CT3 | vless | G2 | wikipedia.org::article_view | 3 | 0.666667 | 0.636364 | 0.700000 | 否 | 20 | 14 | 8 | 6 |
| CT3 | vless | G2 | youtube.com::search_results_view | 4 | 0.761905 | 0.727273 | 0.800000 | 否 | 20 | 16 | 6 | 4 |
| CT3 | vless | G2 | youtube.com::video_playback | 5 | 0.800000 | 0.800000 | 0.800000 | 是 | 20 | 16 | 4 | 4 |
| CT3 | vmess | G0 | bing.com::search_results_view | 0 | 0.769231 | 0.789474 | 0.750000 | 否 | 20 | 15 | 4 | 5 |
| CT3 | vmess | G0 | developer.mozilla.org::document_view | 1 | 0.594595 | 0.647059 | 0.550000 | 否 | 20 | 11 | 6 | 9 |
| CT3 | vmess | G0 | github.com::repository_view | 2 | 0.842105 | 0.888889 | 0.800000 | 是 | 20 | 16 | 2 | 4 |
| CT3 | vmess | G0 | wikipedia.org::article_view | 3 | 0.697674 | 0.652174 | 0.750000 | 否 | 20 | 15 | 8 | 5 |
| CT3 | vmess | G0 | youtube.com::search_results_view | 4 | 0.926829 | 0.904762 | 0.950000 | 是 | 20 | 19 | 2 | 1 |
| CT3 | vmess | G0 | youtube.com::video_playback | 5 | 0.904762 | 0.863636 | 0.950000 | 否 | 20 | 19 | 3 | 1 |
| CT3 | vmess | G1 | bing.com::search_results_view | 0 | 0.580645 | 0.818182 | 0.450000 | 是 | 20 | 9 | 2 | 11 |
| CT3 | vmess | G1 | developer.mozilla.org::document_view | 1 | 0.654545 | 0.514286 | 0.900000 | 否 | 20 | 18 | 17 | 2 |
| CT3 | vmess | G1 | github.com::repository_view | 2 | 0.900000 | 0.900000 | 0.900000 | 否 | 20 | 18 | 2 | 2 |
| CT3 | vmess | G1 | wikipedia.org::article_view | 3 | 0.320000 | 0.800000 | 0.200000 | 是 | 20 | 4 | 1 | 16 |
| CT3 | vmess | G1 | youtube.com::search_results_view | 4 | 0.808511 | 0.703704 | 0.950000 | 否 | 20 | 19 | 8 | 1 |
| CT3 | vmess | G1 | youtube.com::video_playback | 5 | 0.904762 | 0.863636 | 0.950000 | 否 | 20 | 19 | 3 | 1 |
| CT3 | vmess | G2 | bing.com::search_results_view | 0 | 0.780488 | 0.761905 | 0.800000 | 否 | 20 | 16 | 5 | 4 |
| CT3 | vmess | G2 | developer.mozilla.org::document_view | 1 | 0.000000 | 0.000000 | 0.000000 | 是 | 20 | 0 | 1 | 20 |
| CT3 | vmess | G2 | github.com::repository_view | 2 | 0.857143 | 0.818182 | 0.900000 | 否 | 20 | 18 | 4 | 2 |
| CT3 | vmess | G2 | wikipedia.org::article_view | 3 | 0.703704 | 0.558824 | 0.950000 | 否 | 20 | 19 | 15 | 1 |
| CT3 | vmess | G2 | youtube.com::search_results_view | 4 | 0.857143 | 0.818182 | 0.900000 | 否 | 20 | 18 | 4 | 2 |
| CT3 | vmess | G2 | youtube.com::video_playback | 5 | 0.900000 | 0.900000 | 0.900000 | 是 | 20 | 18 | 2 | 2 |
| CT4 | shadowsocks | G0 | bing.com::search_results_view | 0 | 0.820513 | 0.842105 | 0.800000 | 否 | 20 | 16 | 3 | 4 |
| CT4 | shadowsocks | G0 | developer.mozilla.org::document_view | 1 | 0.780488 | 0.761905 | 0.800000 | 否 | 20 | 16 | 5 | 4 |
| CT4 | shadowsocks | G0 | github.com::repository_view | 2 | 0.829268 | 0.809524 | 0.850000 | 是 | 20 | 17 | 4 | 3 |
| CT4 | shadowsocks | G0 | wikipedia.org::article_view | 3 | 0.744186 | 0.695652 | 0.800000 | 否 | 20 | 16 | 7 | 4 |
| CT4 | shadowsocks | G0 | youtube.com::search_results_view | 4 | 0.722222 | 0.812500 | 0.650000 | 是 | 20 | 13 | 3 | 7 |
| CT4 | shadowsocks | G0 | youtube.com::video_playback | 5 | 0.850000 | 0.850000 | 0.850000 | 否 | 20 | 17 | 3 | 3 |
| CT4 | shadowsocks | G1 | bing.com::search_results_view | 0 | 0.742857 | 0.866667 | 0.650000 | 是 | 20 | 13 | 2 | 7 |
| CT4 | shadowsocks | G1 | developer.mozilla.org::document_view | 1 | 0.610169 | 0.461538 | 0.900000 | 否 | 20 | 18 | 21 | 2 |
| CT4 | shadowsocks | G1 | github.com::repository_view | 2 | 0.883721 | 0.826087 | 0.950000 | 否 | 20 | 19 | 4 | 1 |
| CT4 | shadowsocks | G1 | wikipedia.org::article_view | 3 | 0.250000 | 0.750000 | 0.150000 | 是 | 20 | 3 | 1 | 17 |
| CT4 | shadowsocks | G1 | youtube.com::search_results_view | 4 | 0.894737 | 0.944444 | 0.850000 | 否 | 20 | 17 | 1 | 3 |
| CT4 | shadowsocks | G1 | youtube.com::video_playback | 5 | 0.926829 | 0.904762 | 0.950000 | 否 | 20 | 19 | 2 | 1 |
| CT4 | shadowsocks | G2 | bing.com::search_results_view | 0 | 0.755556 | 0.680000 | 0.850000 | 否 | 20 | 17 | 8 | 3 |
| CT4 | shadowsocks | G2 | developer.mozilla.org::document_view | 1 | 0.428571 | 0.750000 | 0.300000 | 是 | 20 | 6 | 2 | 14 |
| CT4 | shadowsocks | G2 | github.com::repository_view | 2 | 0.950000 | 0.950000 | 0.950000 | 否 | 20 | 19 | 1 | 1 |
| CT4 | shadowsocks | G2 | wikipedia.org::article_view | 3 | 0.693878 | 0.586207 | 0.850000 | 否 | 20 | 17 | 12 | 3 |
| CT4 | shadowsocks | G2 | youtube.com::search_results_view | 4 | 0.808511 | 0.703704 | 0.950000 | 否 | 20 | 19 | 8 | 1 |
| CT4 | shadowsocks | G2 | youtube.com::video_playback | 5 | 0.645161 | 0.909091 | 0.500000 | 是 | 20 | 10 | 1 | 10 |
| CT4 | trojan | G0 | bing.com::search_results_view | 0 | 0.871795 | 0.894737 | 0.850000 | 否 | 20 | 17 | 2 | 3 |
| CT4 | trojan | G0 | developer.mozilla.org::document_view | 1 | 0.829268 | 0.809524 | 0.850000 | 否 | 20 | 17 | 4 | 3 |
| CT4 | trojan | G0 | github.com::repository_view | 2 | 0.909091 | 0.833333 | 1.000000 | 是 | 20 | 20 | 4 | 0 |
| CT4 | trojan | G0 | wikipedia.org::article_view | 3 | 0.842105 | 0.888889 | 0.800000 | 否 | 20 | 16 | 2 | 4 |
| CT4 | trojan | G0 | youtube.com::search_results_view | 4 | 0.842105 | 0.888889 | 0.800000 | 是 | 20 | 16 | 2 | 4 |
| CT4 | trojan | G0 | youtube.com::video_playback | 5 | 0.850000 | 0.850000 | 0.850000 | 否 | 20 | 17 | 3 | 3 |
| CT4 | trojan | G1 | bing.com::search_results_view | 0 | 0.810811 | 0.882353 | 0.750000 | 是 | 20 | 15 | 2 | 5 |
| CT4 | trojan | G1 | developer.mozilla.org::document_view | 1 | 0.791667 | 0.678571 | 0.950000 | 否 | 20 | 19 | 9 | 1 |
| CT4 | trojan | G1 | github.com::repository_view | 2 | 0.952381 | 0.909091 | 1.000000 | 否 | 20 | 20 | 2 | 0 |
| CT4 | trojan | G1 | wikipedia.org::article_view | 3 | 0.800000 | 0.933333 | 0.700000 | 是 | 20 | 14 | 1 | 6 |
| CT4 | trojan | G1 | youtube.com::search_results_view | 4 | 0.871795 | 0.894737 | 0.850000 | 否 | 20 | 17 | 2 | 3 |
| CT4 | trojan | G1 | youtube.com::video_playback | 5 | 0.871795 | 0.894737 | 0.850000 | 否 | 20 | 17 | 2 | 3 |
| CT4 | trojan | G2 | bing.com::search_results_view | 0 | 0.923077 | 0.947368 | 0.900000 | 否 | 20 | 18 | 1 | 2 |
| CT4 | trojan | G2 | developer.mozilla.org::document_view | 1 | 0.857143 | 0.818182 | 0.900000 | 是 | 20 | 18 | 4 | 2 |
| CT4 | trojan | G2 | github.com::repository_view | 2 | 0.930233 | 0.869565 | 1.000000 | 否 | 20 | 20 | 3 | 0 |
| CT4 | trojan | G2 | wikipedia.org::article_view | 3 | 0.871795 | 0.894737 | 0.850000 | 否 | 20 | 17 | 2 | 3 |
| CT4 | trojan | G2 | youtube.com::search_results_view | 4 | 0.900000 | 0.900000 | 0.900000 | 否 | 20 | 18 | 2 | 2 |
| CT4 | trojan | G2 | youtube.com::video_playback | 5 | 0.918919 | 1.000000 | 0.850000 | 是 | 20 | 17 | 0 | 3 |
| CT4 | vless | G0 | bing.com::search_results_view | 0 | 0.790698 | 0.739130 | 0.850000 | 否 | 20 | 17 | 6 | 3 |
| CT4 | vless | G0 | developer.mozilla.org::document_view | 1 | 0.800000 | 0.800000 | 0.800000 | 否 | 20 | 16 | 4 | 4 |
| CT4 | vless | G0 | github.com::repository_view | 2 | 0.871795 | 0.894737 | 0.850000 | 是 | 20 | 17 | 2 | 3 |
| CT4 | vless | G0 | wikipedia.org::article_view | 3 | 0.780488 | 0.761905 | 0.800000 | 否 | 20 | 16 | 5 | 4 |
| CT4 | vless | G0 | youtube.com::search_results_view | 4 | 0.742857 | 0.866667 | 0.650000 | 是 | 20 | 13 | 2 | 7 |
| CT4 | vless | G0 | youtube.com::video_playback | 5 | 0.857143 | 0.818182 | 0.900000 | 否 | 20 | 18 | 4 | 2 |
| CT4 | vless | G1 | bing.com::search_results_view | 0 | 0.790698 | 0.739130 | 0.850000 | 是 | 20 | 17 | 6 | 3 |
| CT4 | vless | G1 | developer.mozilla.org::document_view | 1 | 0.790698 | 0.739130 | 0.850000 | 否 | 20 | 17 | 6 | 3 |
| CT4 | vless | G1 | github.com::repository_view | 2 | 0.878049 | 0.857143 | 0.900000 | 否 | 20 | 18 | 3 | 2 |
| CT4 | vless | G1 | wikipedia.org::article_view | 3 | 0.628571 | 0.733333 | 0.550000 | 是 | 20 | 11 | 4 | 9 |
| CT4 | vless | G1 | youtube.com::search_results_view | 4 | 0.684211 | 0.722222 | 0.650000 | 否 | 20 | 13 | 5 | 7 |
| CT4 | vless | G1 | youtube.com::video_playback | 5 | 0.850000 | 0.850000 | 0.850000 | 否 | 20 | 17 | 3 | 3 |
| CT4 | vless | G2 | bing.com::search_results_view | 0 | 0.829268 | 0.809524 | 0.850000 | 否 | 20 | 17 | 4 | 3 |
| CT4 | vless | G2 | developer.mozilla.org::document_view | 1 | 0.666667 | 0.846154 | 0.550000 | 是 | 20 | 11 | 2 | 9 |
| CT4 | vless | G2 | github.com::repository_view | 2 | 0.857143 | 0.818182 | 0.900000 | 否 | 20 | 18 | 4 | 2 |
| CT4 | vless | G2 | wikipedia.org::article_view | 3 | 0.680851 | 0.592593 | 0.800000 | 否 | 20 | 16 | 11 | 4 |
| CT4 | vless | G2 | youtube.com::search_results_view | 4 | 0.756757 | 0.823529 | 0.700000 | 否 | 20 | 14 | 3 | 6 |
| CT4 | vless | G2 | youtube.com::video_playback | 5 | 0.850000 | 0.850000 | 0.850000 | 是 | 20 | 17 | 3 | 3 |
| CT4 | vmess | G0 | bing.com::search_results_view | 0 | 0.769231 | 0.789474 | 0.750000 | 否 | 20 | 15 | 4 | 5 |
| CT4 | vmess | G0 | developer.mozilla.org::document_view | 1 | 0.681818 | 0.625000 | 0.750000 | 否 | 20 | 15 | 9 | 5 |
| CT4 | vmess | G0 | github.com::repository_view | 2 | 0.904762 | 0.863636 | 0.950000 | 是 | 20 | 19 | 3 | 1 |
| CT4 | vmess | G0 | wikipedia.org::article_view | 3 | 0.684211 | 0.722222 | 0.650000 | 否 | 20 | 13 | 5 | 7 |
| CT4 | vmess | G0 | youtube.com::search_results_view | 4 | 0.736842 | 0.777778 | 0.700000 | 是 | 20 | 14 | 4 | 6 |
| CT4 | vmess | G0 | youtube.com::video_playback | 5 | 0.974359 | 1.000000 | 0.950000 | 否 | 20 | 19 | 0 | 1 |
| CT4 | vmess | G1 | bing.com::search_results_view | 0 | 0.645161 | 0.909091 | 0.500000 | 是 | 20 | 10 | 1 | 10 |
| CT4 | vmess | G1 | developer.mozilla.org::document_view | 1 | 0.654545 | 0.514286 | 0.900000 | 否 | 20 | 18 | 17 | 2 |
| CT4 | vmess | G1 | github.com::repository_view | 2 | 0.904762 | 0.863636 | 0.950000 | 否 | 20 | 19 | 3 | 1 |
| CT4 | vmess | G1 | wikipedia.org::article_view | 3 | 0.518519 | 1.000000 | 0.350000 | 是 | 20 | 7 | 0 | 13 |
| CT4 | vmess | G1 | youtube.com::search_results_view | 4 | 0.826087 | 0.730769 | 0.950000 | 否 | 20 | 19 | 7 | 1 |
| CT4 | vmess | G1 | youtube.com::video_playback | 5 | 0.974359 | 1.000000 | 0.950000 | 否 | 20 | 19 | 0 | 1 |
| CT4 | vmess | G2 | bing.com::search_results_view | 0 | 0.761905 | 0.727273 | 0.800000 | 否 | 20 | 16 | 6 | 4 |
| CT4 | vmess | G2 | developer.mozilla.org::document_view | 1 | 0.160000 | 0.400000 | 0.100000 | 是 | 20 | 2 | 3 | 18 |
| CT4 | vmess | G2 | github.com::repository_view | 2 | 0.883721 | 0.826087 | 0.950000 | 否 | 20 | 19 | 4 | 1 |
| CT4 | vmess | G2 | wikipedia.org::article_view | 3 | 0.625000 | 0.535714 | 0.750000 | 否 | 20 | 15 | 13 | 5 |
| CT4 | vmess | G2 | youtube.com::search_results_view | 4 | 0.818182 | 0.750000 | 0.900000 | 否 | 20 | 18 | 6 | 2 |
| CT4 | vmess | G2 | youtube.com::video_playback | 5 | 0.947368 | 1.000000 | 0.900000 | 是 | 20 | 18 | 0 | 2 |
| CT5 | shadowsocks | G0 | bing.com::search_results_view | 0 | 0.756757 | 0.823529 | 0.700000 | 否 | 20 | 14 | 3 | 6 |
| CT5 | shadowsocks | G0 | developer.mozilla.org::document_view | 1 | 0.666667 | 0.600000 | 0.750000 | 否 | 20 | 15 | 10 | 5 |
| CT5 | shadowsocks | G0 | github.com::repository_view | 2 | 0.974359 | 1.000000 | 0.950000 | 是 | 20 | 19 | 0 | 1 |
| CT5 | shadowsocks | G0 | wikipedia.org::article_view | 3 | 0.789474 | 0.833333 | 0.750000 | 否 | 20 | 15 | 3 | 5 |
| CT5 | shadowsocks | G0 | youtube.com::search_results_view | 4 | 0.950000 | 0.950000 | 0.950000 | 是 | 20 | 19 | 1 | 1 |
| CT5 | shadowsocks | G0 | youtube.com::video_playback | 5 | 0.975610 | 0.952381 | 1.000000 | 否 | 20 | 20 | 1 | 0 |
| CT5 | shadowsocks | G1 | bing.com::search_results_view | 0 | 0.756757 | 0.823529 | 0.700000 | 是 | 20 | 14 | 3 | 6 |
| CT5 | shadowsocks | G1 | developer.mozilla.org::document_view | 1 | 0.666667 | 0.600000 | 0.750000 | 否 | 20 | 15 | 10 | 5 |
| CT5 | shadowsocks | G1 | github.com::repository_view | 2 | 0.974359 | 1.000000 | 0.950000 | 否 | 20 | 19 | 0 | 1 |
| CT5 | shadowsocks | G1 | wikipedia.org::article_view | 3 | 0.789474 | 0.833333 | 0.750000 | 是 | 20 | 15 | 3 | 5 |
| CT5 | shadowsocks | G1 | youtube.com::search_results_view | 4 | 0.950000 | 0.950000 | 0.950000 | 否 | 20 | 19 | 1 | 1 |
| CT5 | shadowsocks | G1 | youtube.com::video_playback | 5 | 0.975610 | 0.952381 | 1.000000 | 否 | 20 | 20 | 1 | 0 |
| CT5 | shadowsocks | G2 | bing.com::search_results_view | 0 | 0.756757 | 0.823529 | 0.700000 | 否 | 20 | 14 | 3 | 6 |
| CT5 | shadowsocks | G2 | developer.mozilla.org::document_view | 1 | 0.666667 | 0.600000 | 0.750000 | 是 | 20 | 15 | 10 | 5 |
| CT5 | shadowsocks | G2 | github.com::repository_view | 2 | 0.974359 | 1.000000 | 0.950000 | 否 | 20 | 19 | 0 | 1 |
| CT5 | shadowsocks | G2 | wikipedia.org::article_view | 3 | 0.789474 | 0.833333 | 0.750000 | 否 | 20 | 15 | 3 | 5 |
| CT5 | shadowsocks | G2 | youtube.com::search_results_view | 4 | 0.950000 | 0.950000 | 0.950000 | 否 | 20 | 19 | 1 | 1 |
| CT5 | shadowsocks | G2 | youtube.com::video_playback | 5 | 0.975610 | 0.952381 | 1.000000 | 是 | 20 | 20 | 1 | 0 |
| CT5 | trojan | G0 | bing.com::search_results_view | 0 | 0.829268 | 0.809524 | 0.850000 | 否 | 20 | 17 | 4 | 3 |
| CT5 | trojan | G0 | developer.mozilla.org::document_view | 1 | 0.684211 | 0.722222 | 0.650000 | 否 | 20 | 13 | 5 | 7 |
| CT5 | trojan | G0 | github.com::repository_view | 2 | 0.950000 | 0.950000 | 0.950000 | 是 | 20 | 19 | 1 | 1 |
| CT5 | trojan | G0 | wikipedia.org::article_view | 3 | 0.800000 | 0.800000 | 0.800000 | 否 | 20 | 16 | 4 | 4 |
| CT5 | trojan | G0 | youtube.com::search_results_view | 4 | 0.878049 | 0.857143 | 0.900000 | 是 | 20 | 18 | 3 | 2 |
| CT5 | trojan | G0 | youtube.com::video_playback | 5 | 0.850000 | 0.850000 | 0.850000 | 否 | 20 | 17 | 3 | 3 |
| CT5 | trojan | G1 | bing.com::search_results_view | 0 | 0.829268 | 0.809524 | 0.850000 | 是 | 20 | 17 | 4 | 3 |
| CT5 | trojan | G1 | developer.mozilla.org::document_view | 1 | 0.684211 | 0.722222 | 0.650000 | 否 | 20 | 13 | 5 | 7 |
| CT5 | trojan | G1 | github.com::repository_view | 2 | 0.950000 | 0.950000 | 0.950000 | 否 | 20 | 19 | 1 | 1 |
| CT5 | trojan | G1 | wikipedia.org::article_view | 3 | 0.800000 | 0.800000 | 0.800000 | 是 | 20 | 16 | 4 | 4 |
| CT5 | trojan | G1 | youtube.com::search_results_view | 4 | 0.878049 | 0.857143 | 0.900000 | 否 | 20 | 18 | 3 | 2 |
| CT5 | trojan | G1 | youtube.com::video_playback | 5 | 0.850000 | 0.850000 | 0.850000 | 否 | 20 | 17 | 3 | 3 |
| CT5 | trojan | G2 | bing.com::search_results_view | 0 | 0.829268 | 0.809524 | 0.850000 | 否 | 20 | 17 | 4 | 3 |
| CT5 | trojan | G2 | developer.mozilla.org::document_view | 1 | 0.684211 | 0.722222 | 0.650000 | 是 | 20 | 13 | 5 | 7 |
| CT5 | trojan | G2 | github.com::repository_view | 2 | 0.950000 | 0.950000 | 0.950000 | 否 | 20 | 19 | 1 | 1 |
| CT5 | trojan | G2 | wikipedia.org::article_view | 3 | 0.800000 | 0.800000 | 0.800000 | 否 | 20 | 16 | 4 | 4 |
| CT5 | trojan | G2 | youtube.com::search_results_view | 4 | 0.878049 | 0.857143 | 0.900000 | 否 | 20 | 18 | 3 | 2 |
| CT5 | trojan | G2 | youtube.com::video_playback | 5 | 0.850000 | 0.850000 | 0.850000 | 是 | 20 | 17 | 3 | 3 |
| CT5 | vless | G0 | bing.com::search_results_view | 0 | 0.800000 | 0.800000 | 0.800000 | 否 | 20 | 16 | 4 | 4 |
| CT5 | vless | G0 | developer.mozilla.org::document_view | 1 | 0.736842 | 0.777778 | 0.700000 | 否 | 20 | 14 | 4 | 6 |
| CT5 | vless | G0 | github.com::repository_view | 2 | 0.871795 | 0.894737 | 0.850000 | 是 | 20 | 17 | 2 | 3 |
| CT5 | vless | G0 | wikipedia.org::article_view | 3 | 0.714286 | 0.681818 | 0.750000 | 否 | 20 | 15 | 7 | 5 |
| CT5 | vless | G0 | youtube.com::search_results_view | 4 | 0.769231 | 0.789474 | 0.750000 | 是 | 20 | 15 | 4 | 5 |
| CT5 | vless | G0 | youtube.com::video_playback | 5 | 0.904762 | 0.863636 | 0.950000 | 否 | 20 | 19 | 3 | 1 |
| CT5 | vless | G1 | bing.com::search_results_view | 0 | 0.800000 | 0.800000 | 0.800000 | 是 | 20 | 16 | 4 | 4 |
| CT5 | vless | G1 | developer.mozilla.org::document_view | 1 | 0.736842 | 0.777778 | 0.700000 | 否 | 20 | 14 | 4 | 6 |
| CT5 | vless | G1 | github.com::repository_view | 2 | 0.871795 | 0.894737 | 0.850000 | 否 | 20 | 17 | 2 | 3 |
| CT5 | vless | G1 | wikipedia.org::article_view | 3 | 0.714286 | 0.681818 | 0.750000 | 是 | 20 | 15 | 7 | 5 |
| CT5 | vless | G1 | youtube.com::search_results_view | 4 | 0.769231 | 0.789474 | 0.750000 | 否 | 20 | 15 | 4 | 5 |
| CT5 | vless | G1 | youtube.com::video_playback | 5 | 0.904762 | 0.863636 | 0.950000 | 否 | 20 | 19 | 3 | 1 |
| CT5 | vless | G2 | bing.com::search_results_view | 0 | 0.800000 | 0.800000 | 0.800000 | 否 | 20 | 16 | 4 | 4 |
| CT5 | vless | G2 | developer.mozilla.org::document_view | 1 | 0.736842 | 0.777778 | 0.700000 | 是 | 20 | 14 | 4 | 6 |
| CT5 | vless | G2 | github.com::repository_view | 2 | 0.871795 | 0.894737 | 0.850000 | 否 | 20 | 17 | 2 | 3 |
| CT5 | vless | G2 | wikipedia.org::article_view | 3 | 0.714286 | 0.681818 | 0.750000 | 否 | 20 | 15 | 7 | 5 |
| CT5 | vless | G2 | youtube.com::search_results_view | 4 | 0.769231 | 0.789474 | 0.750000 | 否 | 20 | 15 | 4 | 5 |
| CT5 | vless | G2 | youtube.com::video_playback | 5 | 0.904762 | 0.863636 | 0.950000 | 是 | 20 | 19 | 3 | 1 |
| CT5 | vmess | G0 | bing.com::search_results_view | 0 | 0.800000 | 0.800000 | 0.800000 | 否 | 20 | 16 | 4 | 4 |
| CT5 | vmess | G0 | developer.mozilla.org::document_view | 1 | 0.611111 | 0.687500 | 0.550000 | 否 | 20 | 11 | 5 | 9 |
| CT5 | vmess | G0 | github.com::repository_view | 2 | 0.850000 | 0.850000 | 0.850000 | 是 | 20 | 17 | 3 | 3 |
| CT5 | vmess | G0 | wikipedia.org::article_view | 3 | 0.636364 | 0.583333 | 0.700000 | 否 | 20 | 14 | 10 | 6 |
| CT5 | vmess | G0 | youtube.com::search_results_view | 4 | 0.800000 | 0.800000 | 0.800000 | 是 | 20 | 16 | 4 | 4 |
| CT5 | vmess | G0 | youtube.com::video_playback | 5 | 0.900000 | 0.900000 | 0.900000 | 否 | 20 | 18 | 2 | 2 |
| CT5 | vmess | G1 | bing.com::search_results_view | 0 | 0.800000 | 0.800000 | 0.800000 | 是 | 20 | 16 | 4 | 4 |
| CT5 | vmess | G1 | developer.mozilla.org::document_view | 1 | 0.611111 | 0.687500 | 0.550000 | 否 | 20 | 11 | 5 | 9 |
| CT5 | vmess | G1 | github.com::repository_view | 2 | 0.850000 | 0.850000 | 0.850000 | 否 | 20 | 17 | 3 | 3 |
| CT5 | vmess | G1 | wikipedia.org::article_view | 3 | 0.636364 | 0.583333 | 0.700000 | 是 | 20 | 14 | 10 | 6 |
| CT5 | vmess | G1 | youtube.com::search_results_view | 4 | 0.800000 | 0.800000 | 0.800000 | 否 | 20 | 16 | 4 | 4 |
| CT5 | vmess | G1 | youtube.com::video_playback | 5 | 0.900000 | 0.900000 | 0.900000 | 否 | 20 | 18 | 2 | 2 |
| CT5 | vmess | G2 | bing.com::search_results_view | 0 | 0.800000 | 0.800000 | 0.800000 | 否 | 20 | 16 | 4 | 4 |
| CT5 | vmess | G2 | developer.mozilla.org::document_view | 1 | 0.611111 | 0.687500 | 0.550000 | 是 | 20 | 11 | 5 | 9 |
| CT5 | vmess | G2 | github.com::repository_view | 2 | 0.850000 | 0.850000 | 0.850000 | 否 | 20 | 17 | 3 | 3 |
| CT5 | vmess | G2 | wikipedia.org::article_view | 3 | 0.636364 | 0.583333 | 0.700000 | 否 | 20 | 14 | 10 | 6 |
| CT5 | vmess | G2 | youtube.com::search_results_view | 4 | 0.800000 | 0.800000 | 0.800000 | 否 | 20 | 16 | 4 | 4 |
| CT5 | vmess | G2 | youtube.com::video_playback | 5 | 0.900000 | 0.900000 | 0.900000 | 是 | 20 | 18 | 2 | 2 |
| JA0 | shadowsocks | G0 | bing.com::search_results_view | 0 | 0.769231 | 0.789474 | 0.750000 | 否 | 20 | 15 | 4 | 5 |
| JA0 | shadowsocks | G0 | developer.mozilla.org::document_view | 1 | 0.769231 | 0.789474 | 0.750000 | 否 | 20 | 15 | 4 | 5 |
| JA0 | shadowsocks | G0 | github.com::repository_view | 2 | 0.810811 | 0.882353 | 0.750000 | 是 | 20 | 15 | 2 | 5 |
| JA0 | shadowsocks | G0 | wikipedia.org::article_view | 3 | 0.800000 | 0.720000 | 0.900000 | 否 | 20 | 18 | 7 | 2 |
| JA0 | shadowsocks | G0 | youtube.com::search_results_view | 4 | 0.727273 | 0.923077 | 0.600000 | 是 | 20 | 12 | 1 | 8 |
| JA0 | shadowsocks | G0 | youtube.com::video_playback | 5 | 0.765957 | 0.666667 | 0.900000 | 否 | 20 | 18 | 9 | 2 |
| JA0 | shadowsocks | G1 | bing.com::search_results_view | 0 | 0.625000 | 0.833333 | 0.500000 | 是 | 20 | 10 | 2 | 10 |
| JA0 | shadowsocks | G1 | developer.mozilla.org::document_view | 1 | 0.692308 | 0.562500 | 0.900000 | 否 | 20 | 18 | 14 | 2 |
| JA0 | shadowsocks | G1 | github.com::repository_view | 2 | 0.850000 | 0.850000 | 0.850000 | 否 | 20 | 17 | 3 | 3 |
| JA0 | shadowsocks | G1 | wikipedia.org::article_view | 3 | 0.533333 | 0.800000 | 0.400000 | 是 | 20 | 8 | 2 | 12 |
| JA0 | shadowsocks | G1 | youtube.com::search_results_view | 4 | 0.883721 | 0.826087 | 0.950000 | 否 | 20 | 19 | 4 | 1 |
| JA0 | shadowsocks | G1 | youtube.com::video_playback | 5 | 0.883721 | 0.826087 | 0.950000 | 否 | 20 | 19 | 4 | 1 |
| JA0 | shadowsocks | G2 | bing.com::search_results_view | 0 | 0.666667 | 0.571429 | 0.800000 | 否 | 20 | 16 | 12 | 4 |
| JA0 | shadowsocks | G2 | developer.mozilla.org::document_view | 1 | 0.000000 | 0.000000 | 0.000000 | 是 | 20 | 0 | 0 | 20 |
| JA0 | shadowsocks | G2 | github.com::repository_view | 2 | 0.878049 | 0.857143 | 0.900000 | 否 | 20 | 18 | 3 | 2 |
| JA0 | shadowsocks | G2 | wikipedia.org::article_view | 3 | 0.680000 | 0.566667 | 0.850000 | 否 | 20 | 17 | 13 | 3 |
| JA0 | shadowsocks | G2 | youtube.com::search_results_view | 4 | 0.750000 | 0.642857 | 0.900000 | 否 | 20 | 18 | 10 | 2 |
| JA0 | shadowsocks | G2 | youtube.com::video_playback | 5 | 0.606061 | 0.769231 | 0.500000 | 是 | 20 | 10 | 3 | 10 |
| JA0 | trojan | G0 | bing.com::search_results_view | 0 | 0.800000 | 0.800000 | 0.800000 | 否 | 20 | 16 | 4 | 4 |
| JA0 | trojan | G0 | developer.mozilla.org::document_view | 1 | 0.682927 | 0.666667 | 0.700000 | 否 | 20 | 14 | 7 | 6 |
| JA0 | trojan | G0 | github.com::repository_view | 2 | 0.871795 | 0.894737 | 0.850000 | 是 | 20 | 17 | 2 | 3 |
| JA0 | trojan | G0 | wikipedia.org::article_view | 3 | 0.800000 | 0.800000 | 0.800000 | 否 | 20 | 16 | 4 | 4 |
| JA0 | trojan | G0 | youtube.com::search_results_view | 4 | 0.789474 | 0.833333 | 0.750000 | 是 | 20 | 15 | 3 | 5 |
| JA0 | trojan | G0 | youtube.com::video_playback | 5 | 0.857143 | 0.818182 | 0.900000 | 否 | 20 | 18 | 4 | 2 |
| JA0 | trojan | G1 | bing.com::search_results_view | 0 | 0.742857 | 0.866667 | 0.650000 | 是 | 20 | 13 | 2 | 7 |
| JA0 | trojan | G1 | developer.mozilla.org::document_view | 1 | 0.800000 | 0.720000 | 0.900000 | 否 | 20 | 18 | 7 | 2 |
| JA0 | trojan | G1 | github.com::repository_view | 2 | 0.975610 | 0.952381 | 1.000000 | 否 | 20 | 20 | 1 | 0 |
| JA0 | trojan | G1 | wikipedia.org::article_view | 3 | 0.666667 | 0.750000 | 0.600000 | 是 | 20 | 12 | 4 | 8 |
| JA0 | trojan | G1 | youtube.com::search_results_view | 4 | 0.820513 | 0.842105 | 0.800000 | 否 | 20 | 16 | 3 | 4 |
| JA0 | trojan | G1 | youtube.com::video_playback | 5 | 0.818182 | 0.750000 | 0.900000 | 否 | 20 | 18 | 6 | 2 |
| JA0 | trojan | G2 | bing.com::search_results_view | 0 | 0.829268 | 0.809524 | 0.850000 | 否 | 20 | 17 | 4 | 3 |
| JA0 | trojan | G2 | developer.mozilla.org::document_view | 1 | 0.705882 | 0.857143 | 0.600000 | 是 | 20 | 12 | 2 | 8 |
| JA0 | trojan | G2 | github.com::repository_view | 2 | 0.952381 | 0.909091 | 1.000000 | 否 | 20 | 20 | 2 | 0 |
| JA0 | trojan | G2 | wikipedia.org::article_view | 3 | 0.744186 | 0.695652 | 0.800000 | 否 | 20 | 16 | 7 | 4 |
| JA0 | trojan | G2 | youtube.com::search_results_view | 4 | 0.863636 | 0.791667 | 0.950000 | 否 | 20 | 19 | 5 | 1 |
| JA0 | trojan | G2 | youtube.com::video_playback | 5 | 0.777778 | 0.875000 | 0.700000 | 是 | 20 | 14 | 2 | 6 |
| JA0 | vless | G0 | bing.com::search_results_view | 0 | 0.878049 | 0.857143 | 0.900000 | 否 | 20 | 18 | 3 | 2 |
| JA0 | vless | G0 | developer.mozilla.org::document_view | 1 | 0.731707 | 0.714286 | 0.750000 | 否 | 20 | 15 | 6 | 5 |
| JA0 | vless | G0 | github.com::repository_view | 2 | 0.833333 | 0.937500 | 0.750000 | 是 | 20 | 15 | 1 | 5 |
| JA0 | vless | G0 | wikipedia.org::article_view | 3 | 0.682927 | 0.666667 | 0.700000 | 否 | 20 | 14 | 7 | 6 |
| JA0 | vless | G0 | youtube.com::search_results_view | 4 | 0.842105 | 0.888889 | 0.800000 | 是 | 20 | 16 | 2 | 4 |
| JA0 | vless | G0 | youtube.com::video_playback | 5 | 0.837209 | 0.782609 | 0.900000 | 否 | 20 | 18 | 5 | 2 |
| JA0 | vless | G1 | bing.com::search_results_view | 0 | 0.820513 | 0.842105 | 0.800000 | 是 | 20 | 16 | 3 | 4 |
| JA0 | vless | G1 | developer.mozilla.org::document_view | 1 | 0.731707 | 0.714286 | 0.750000 | 否 | 20 | 15 | 6 | 5 |
| JA0 | vless | G1 | github.com::repository_view | 2 | 0.871795 | 0.894737 | 0.850000 | 否 | 20 | 17 | 2 | 3 |
| JA0 | vless | G1 | wikipedia.org::article_view | 3 | 0.571429 | 0.666667 | 0.500000 | 是 | 20 | 10 | 5 | 10 |
| JA0 | vless | G1 | youtube.com::search_results_view | 4 | 0.809524 | 0.772727 | 0.850000 | 否 | 20 | 17 | 5 | 3 |
| JA0 | vless | G1 | youtube.com::video_playback | 5 | 0.909091 | 0.833333 | 1.000000 | 否 | 20 | 20 | 4 | 0 |
| JA0 | vless | G2 | bing.com::search_results_view | 0 | 0.871795 | 0.894737 | 0.850000 | 否 | 20 | 17 | 2 | 3 |
| JA0 | vless | G2 | developer.mozilla.org::document_view | 1 | 0.588235 | 0.714286 | 0.500000 | 是 | 20 | 10 | 4 | 10 |
| JA0 | vless | G2 | github.com::repository_view | 2 | 0.894737 | 0.944444 | 0.850000 | 否 | 20 | 17 | 1 | 3 |
| JA0 | vless | G2 | wikipedia.org::article_view | 3 | 0.583333 | 0.500000 | 0.700000 | 否 | 20 | 14 | 14 | 6 |
| JA0 | vless | G2 | youtube.com::search_results_view | 4 | 0.800000 | 0.800000 | 0.800000 | 否 | 20 | 16 | 4 | 4 |
| JA0 | vless | G2 | youtube.com::video_playback | 5 | 0.829268 | 0.809524 | 0.850000 | 是 | 20 | 17 | 4 | 3 |
| JA0 | vmess | G0 | bing.com::search_results_view | 0 | 0.769231 | 0.789474 | 0.750000 | 否 | 20 | 15 | 4 | 5 |
| JA0 | vmess | G0 | developer.mozilla.org::document_view | 1 | 0.622222 | 0.560000 | 0.700000 | 否 | 20 | 14 | 11 | 6 |
| JA0 | vmess | G0 | github.com::repository_view | 2 | 0.764706 | 0.928571 | 0.650000 | 是 | 20 | 13 | 1 | 7 |
| JA0 | vmess | G0 | wikipedia.org::article_view | 3 | 0.761905 | 0.727273 | 0.800000 | 否 | 20 | 16 | 6 | 4 |
| JA0 | vmess | G0 | youtube.com::search_results_view | 4 | 0.900000 | 0.900000 | 0.900000 | 是 | 20 | 18 | 2 | 2 |
| JA0 | vmess | G0 | youtube.com::video_playback | 5 | 0.950000 | 0.950000 | 0.950000 | 否 | 20 | 19 | 1 | 1 |
| JA0 | vmess | G1 | bing.com::search_results_view | 0 | 0.600000 | 0.900000 | 0.450000 | 是 | 20 | 9 | 1 | 11 |
| JA0 | vmess | G1 | developer.mozilla.org::document_view | 1 | 0.641509 | 0.515152 | 0.850000 | 否 | 20 | 17 | 16 | 3 |
| JA0 | vmess | G1 | github.com::repository_view | 2 | 0.904762 | 0.863636 | 0.950000 | 否 | 20 | 19 | 3 | 1 |
| JA0 | vmess | G1 | wikipedia.org::article_view | 3 | 0.384615 | 0.833333 | 0.250000 | 是 | 20 | 5 | 1 | 15 |
| JA0 | vmess | G1 | youtube.com::search_results_view | 4 | 0.826087 | 0.730769 | 0.950000 | 否 | 20 | 19 | 7 | 1 |
| JA0 | vmess | G1 | youtube.com::video_playback | 5 | 0.883721 | 0.826087 | 0.950000 | 否 | 20 | 19 | 4 | 1 |
| JA0 | vmess | G2 | bing.com::search_results_view | 0 | 0.790698 | 0.739130 | 0.850000 | 否 | 20 | 17 | 6 | 3 |
| JA0 | vmess | G2 | developer.mozilla.org::document_view | 1 | 0.095238 | 1.000000 | 0.050000 | 是 | 20 | 1 | 0 | 19 |
| JA0 | vmess | G2 | github.com::repository_view | 2 | 0.904762 | 0.863636 | 0.950000 | 否 | 20 | 19 | 3 | 1 |
| JA0 | vmess | G2 | wikipedia.org::article_view | 3 | 0.703704 | 0.558824 | 0.950000 | 否 | 20 | 19 | 15 | 1 |
| JA0 | vmess | G2 | youtube.com::search_results_view | 4 | 0.857143 | 0.818182 | 0.900000 | 否 | 20 | 18 | 4 | 2 |
| JA0 | vmess | G2 | youtube.com::video_playback | 5 | 0.947368 | 1.000000 | 0.900000 | 是 | 20 | 18 | 0 | 2 |
| JA1 | shadowsocks | G0 | bing.com::search_results_view | 0 | 0.789474 | 0.833333 | 0.750000 | 否 | 20 | 15 | 3 | 5 |
| JA1 | shadowsocks | G0 | developer.mozilla.org::document_view | 1 | 0.789474 | 0.833333 | 0.750000 | 否 | 20 | 15 | 3 | 5 |
| JA1 | shadowsocks | G0 | github.com::repository_view | 2 | 0.850000 | 0.850000 | 0.850000 | 是 | 20 | 17 | 3 | 3 |
| JA1 | shadowsocks | G0 | wikipedia.org::article_view | 3 | 0.818182 | 0.750000 | 0.900000 | 否 | 20 | 18 | 6 | 2 |
| JA1 | shadowsocks | G0 | youtube.com::search_results_view | 4 | 0.750000 | 1.000000 | 0.600000 | 是 | 20 | 12 | 0 | 8 |
| JA1 | shadowsocks | G0 | youtube.com::video_playback | 5 | 0.750000 | 0.642857 | 0.900000 | 否 | 20 | 18 | 10 | 2 |
| JA1 | shadowsocks | G1 | bing.com::search_results_view | 0 | 0.625000 | 0.833333 | 0.500000 | 是 | 20 | 10 | 2 | 10 |
| JA1 | shadowsocks | G1 | developer.mozilla.org::document_view | 1 | 0.618182 | 0.485714 | 0.850000 | 否 | 20 | 17 | 18 | 3 |
| JA1 | shadowsocks | G1 | github.com::repository_view | 2 | 0.857143 | 0.818182 | 0.900000 | 否 | 20 | 18 | 4 | 2 |
| JA1 | shadowsocks | G1 | wikipedia.org::article_view | 3 | 0.400000 | 1.000000 | 0.250000 | 是 | 20 | 5 | 0 | 15 |
| JA1 | shadowsocks | G1 | youtube.com::search_results_view | 4 | 0.883721 | 0.826087 | 0.950000 | 否 | 20 | 19 | 4 | 1 |
| JA1 | shadowsocks | G1 | youtube.com::video_playback | 5 | 0.883721 | 0.826087 | 0.950000 | 否 | 20 | 19 | 4 | 1 |
| JA1 | shadowsocks | G2 | bing.com::search_results_view | 0 | 0.711111 | 0.640000 | 0.800000 | 否 | 20 | 16 | 9 | 4 |
| JA1 | shadowsocks | G2 | developer.mozilla.org::document_view | 1 | 0.090909 | 0.500000 | 0.050000 | 是 | 20 | 1 | 1 | 19 |
| JA1 | shadowsocks | G2 | github.com::repository_view | 2 | 0.904762 | 0.863636 | 0.950000 | 否 | 20 | 19 | 3 | 1 |
| JA1 | shadowsocks | G2 | wikipedia.org::article_view | 3 | 0.653846 | 0.531250 | 0.850000 | 否 | 20 | 17 | 15 | 3 |
| JA1 | shadowsocks | G2 | youtube.com::search_results_view | 4 | 0.791667 | 0.678571 | 0.950000 | 否 | 20 | 19 | 9 | 1 |
| JA1 | shadowsocks | G2 | youtube.com::video_playback | 5 | 0.645161 | 0.909091 | 0.500000 | 是 | 20 | 10 | 1 | 10 |
| JA1 | trojan | G0 | bing.com::search_results_view | 0 | 0.800000 | 0.800000 | 0.800000 | 否 | 20 | 16 | 4 | 4 |
| JA1 | trojan | G0 | developer.mozilla.org::document_view | 1 | 0.744186 | 0.695652 | 0.800000 | 否 | 20 | 16 | 7 | 4 |
| JA1 | trojan | G0 | github.com::repository_view | 2 | 0.894737 | 0.944444 | 0.850000 | 是 | 20 | 17 | 1 | 3 |
| JA1 | trojan | G0 | wikipedia.org::article_view | 3 | 0.820513 | 0.842105 | 0.800000 | 否 | 20 | 16 | 3 | 4 |
| JA1 | trojan | G0 | youtube.com::search_results_view | 4 | 0.800000 | 0.800000 | 0.800000 | 是 | 20 | 16 | 4 | 4 |
| JA1 | trojan | G0 | youtube.com::video_playback | 5 | 0.850000 | 0.850000 | 0.850000 | 否 | 20 | 17 | 3 | 3 |
| JA1 | trojan | G1 | bing.com::search_results_view | 0 | 0.756757 | 0.823529 | 0.700000 | 是 | 20 | 14 | 3 | 6 |
| JA1 | trojan | G1 | developer.mozilla.org::document_view | 1 | 0.772727 | 0.708333 | 0.850000 | 否 | 20 | 17 | 7 | 3 |
| JA1 | trojan | G1 | github.com::repository_view | 2 | 0.952381 | 0.909091 | 1.000000 | 否 | 20 | 20 | 2 | 0 |
| JA1 | trojan | G1 | wikipedia.org::article_view | 3 | 0.742857 | 0.866667 | 0.650000 | 是 | 20 | 13 | 2 | 7 |
| JA1 | trojan | G1 | youtube.com::search_results_view | 4 | 0.829268 | 0.809524 | 0.850000 | 否 | 20 | 17 | 4 | 3 |
| JA1 | trojan | G1 | youtube.com::video_playback | 5 | 0.780488 | 0.761905 | 0.800000 | 否 | 20 | 16 | 5 | 4 |
| JA1 | trojan | G2 | bing.com::search_results_view | 0 | 0.769231 | 0.789474 | 0.750000 | 否 | 20 | 15 | 4 | 5 |
| JA1 | trojan | G2 | developer.mozilla.org::document_view | 1 | 0.606061 | 0.769231 | 0.500000 | 是 | 20 | 10 | 3 | 10 |
| JA1 | trojan | G2 | github.com::repository_view | 2 | 0.952381 | 0.909091 | 1.000000 | 否 | 20 | 20 | 2 | 0 |
| JA1 | trojan | G2 | wikipedia.org::article_view | 3 | 0.695652 | 0.615385 | 0.800000 | 否 | 20 | 16 | 10 | 4 |
| JA1 | trojan | G2 | youtube.com::search_results_view | 4 | 0.863636 | 0.791667 | 0.950000 | 否 | 20 | 19 | 5 | 1 |
| JA1 | trojan | G2 | youtube.com::video_playback | 5 | 0.833333 | 0.937500 | 0.750000 | 是 | 20 | 15 | 1 | 5 |
| JA1 | vless | G0 | bing.com::search_results_view | 0 | 0.900000 | 0.900000 | 0.900000 | 否 | 20 | 18 | 2 | 2 |
| JA1 | vless | G0 | developer.mozilla.org::document_view | 1 | 0.829268 | 0.809524 | 0.850000 | 否 | 20 | 17 | 4 | 3 |
| JA1 | vless | G0 | github.com::repository_view | 2 | 0.864865 | 0.941176 | 0.800000 | 是 | 20 | 16 | 1 | 4 |
| JA1 | vless | G0 | wikipedia.org::article_view | 3 | 0.750000 | 0.750000 | 0.750000 | 否 | 20 | 15 | 5 | 5 |
| JA1 | vless | G0 | youtube.com::search_results_view | 4 | 0.850000 | 0.850000 | 0.850000 | 是 | 20 | 17 | 3 | 3 |
| JA1 | vless | G0 | youtube.com::video_playback | 5 | 0.857143 | 0.818182 | 0.900000 | 否 | 20 | 18 | 4 | 2 |
| JA1 | vless | G1 | bing.com::search_results_view | 0 | 0.850000 | 0.850000 | 0.850000 | 是 | 20 | 17 | 3 | 3 |
| JA1 | vless | G1 | developer.mozilla.org::document_view | 1 | 0.782609 | 0.692308 | 0.900000 | 否 | 20 | 18 | 8 | 2 |
| JA1 | vless | G1 | github.com::repository_view | 2 | 0.923077 | 0.947368 | 0.900000 | 否 | 20 | 18 | 1 | 2 |
| JA1 | vless | G1 | wikipedia.org::article_view | 3 | 0.533333 | 0.800000 | 0.400000 | 是 | 20 | 8 | 2 | 12 |
| JA1 | vless | G1 | youtube.com::search_results_view | 4 | 0.837209 | 0.782609 | 0.900000 | 否 | 20 | 18 | 5 | 2 |
| JA1 | vless | G1 | youtube.com::video_playback | 5 | 0.952381 | 0.909091 | 1.000000 | 否 | 20 | 20 | 2 | 0 |
| JA1 | vless | G2 | bing.com::search_results_view | 0 | 0.871795 | 0.894737 | 0.850000 | 否 | 20 | 17 | 2 | 3 |
| JA1 | vless | G2 | developer.mozilla.org::document_view | 1 | 0.769231 | 0.789474 | 0.750000 | 是 | 20 | 15 | 4 | 5 |
| JA1 | vless | G2 | github.com::repository_view | 2 | 0.894737 | 0.944444 | 0.850000 | 否 | 20 | 17 | 1 | 3 |
| JA1 | vless | G2 | wikipedia.org::article_view | 3 | 0.682927 | 0.666667 | 0.700000 | 否 | 20 | 14 | 7 | 6 |
| JA1 | vless | G2 | youtube.com::search_results_view | 4 | 0.829268 | 0.809524 | 0.850000 | 否 | 20 | 17 | 4 | 3 |
| JA1 | vless | G2 | youtube.com::video_playback | 5 | 0.904762 | 0.863636 | 0.950000 | 是 | 20 | 19 | 3 | 1 |
| JA1 | vmess | G0 | bing.com::search_results_view | 0 | 0.789474 | 0.833333 | 0.750000 | 否 | 20 | 15 | 3 | 5 |
| JA1 | vmess | G0 | developer.mozilla.org::document_view | 1 | 0.619048 | 0.590909 | 0.650000 | 否 | 20 | 13 | 9 | 7 |
| JA1 | vmess | G0 | github.com::repository_view | 2 | 0.833333 | 0.937500 | 0.750000 | 是 | 20 | 15 | 1 | 5 |
| JA1 | vmess | G0 | wikipedia.org::article_view | 3 | 0.651163 | 0.608696 | 0.700000 | 否 | 20 | 14 | 9 | 6 |
| JA1 | vmess | G0 | youtube.com::search_results_view | 4 | 0.829268 | 0.809524 | 0.850000 | 是 | 20 | 17 | 4 | 3 |
| JA1 | vmess | G0 | youtube.com::video_playback | 5 | 0.950000 | 0.950000 | 0.950000 | 否 | 20 | 19 | 1 | 1 |
| JA1 | vmess | G1 | bing.com::search_results_view | 0 | 0.600000 | 0.900000 | 0.450000 | 是 | 20 | 9 | 1 | 11 |
| JA1 | vmess | G1 | developer.mozilla.org::document_view | 1 | 0.653846 | 0.531250 | 0.850000 | 否 | 20 | 17 | 15 | 3 |
| JA1 | vmess | G1 | github.com::repository_view | 2 | 0.926829 | 0.904762 | 0.950000 | 否 | 20 | 19 | 2 | 1 |
| JA1 | vmess | G1 | wikipedia.org::article_view | 3 | 0.320000 | 0.800000 | 0.200000 | 是 | 20 | 4 | 1 | 16 |
| JA1 | vmess | G1 | youtube.com::search_results_view | 4 | 0.826087 | 0.730769 | 0.950000 | 否 | 20 | 19 | 7 | 1 |
| JA1 | vmess | G1 | youtube.com::video_playback | 5 | 0.826087 | 0.730769 | 0.950000 | 否 | 20 | 19 | 7 | 1 |
| JA1 | vmess | G2 | bing.com::search_results_view | 0 | 0.837209 | 0.782609 | 0.900000 | 否 | 20 | 18 | 5 | 2 |
| JA1 | vmess | G2 | developer.mozilla.org::document_view | 1 | 0.181818 | 1.000000 | 0.100000 | 是 | 20 | 2 | 0 | 18 |
| JA1 | vmess | G2 | github.com::repository_view | 2 | 0.926829 | 0.904762 | 0.950000 | 否 | 20 | 19 | 2 | 1 |
| JA1 | vmess | G2 | wikipedia.org::article_view | 3 | 0.692308 | 0.562500 | 0.900000 | 否 | 20 | 18 | 14 | 2 |
| JA1 | vmess | G2 | youtube.com::search_results_view | 4 | 0.837209 | 0.782609 | 0.900000 | 否 | 20 | 18 | 5 | 2 |
| JA1 | vmess | G2 | youtube.com::video_playback | 5 | 0.923077 | 0.947368 | 0.900000 | 是 | 20 | 18 | 1 | 2 |
| JA2 | shadowsocks | G0 | bing.com::search_results_view | 0 | 0.789474 | 0.833333 | 0.750000 | 否 | 20 | 15 | 3 | 5 |
| JA2 | shadowsocks | G0 | developer.mozilla.org::document_view | 1 | 0.800000 | 0.800000 | 0.800000 | 否 | 20 | 16 | 4 | 4 |
| JA2 | shadowsocks | G0 | github.com::repository_view | 2 | 0.833333 | 0.937500 | 0.750000 | 是 | 20 | 15 | 1 | 5 |
| JA2 | shadowsocks | G0 | wikipedia.org::article_view | 3 | 0.800000 | 0.720000 | 0.900000 | 否 | 20 | 18 | 7 | 2 |
| JA2 | shadowsocks | G0 | youtube.com::search_results_view | 4 | 0.800000 | 0.933333 | 0.700000 | 是 | 20 | 14 | 1 | 6 |
| JA2 | shadowsocks | G0 | youtube.com::video_playback | 5 | 0.782609 | 0.692308 | 0.900000 | 否 | 20 | 18 | 8 | 2 |
| JA2 | shadowsocks | G1 | bing.com::search_results_view | 0 | 0.628571 | 0.733333 | 0.550000 | 是 | 20 | 11 | 4 | 9 |
| JA2 | shadowsocks | G1 | developer.mozilla.org::document_view | 1 | 0.615385 | 0.500000 | 0.800000 | 否 | 20 | 16 | 16 | 4 |
| JA2 | shadowsocks | G1 | github.com::repository_view | 2 | 0.857143 | 0.818182 | 0.900000 | 否 | 20 | 18 | 4 | 2 |
| JA2 | shadowsocks | G1 | wikipedia.org::article_view | 3 | 0.400000 | 1.000000 | 0.250000 | 是 | 20 | 5 | 0 | 15 |
| JA2 | shadowsocks | G1 | youtube.com::search_results_view | 4 | 0.857143 | 0.818182 | 0.900000 | 否 | 20 | 18 | 4 | 2 |
| JA2 | shadowsocks | G1 | youtube.com::video_playback | 5 | 0.863636 | 0.791667 | 0.950000 | 否 | 20 | 19 | 5 | 1 |
| JA2 | shadowsocks | G2 | bing.com::search_results_view | 0 | 0.666667 | 0.600000 | 0.750000 | 否 | 20 | 15 | 10 | 5 |
| JA2 | shadowsocks | G2 | developer.mozilla.org::document_view | 1 | 0.000000 | 0.000000 | 0.000000 | 是 | 20 | 0 | 1 | 20 |
| JA2 | shadowsocks | G2 | github.com::repository_view | 2 | 0.878049 | 0.857143 | 0.900000 | 否 | 20 | 18 | 3 | 2 |
| JA2 | shadowsocks | G2 | wikipedia.org::article_view | 3 | 0.654545 | 0.514286 | 0.900000 | 否 | 20 | 18 | 17 | 2 |
| JA2 | shadowsocks | G2 | youtube.com::search_results_view | 4 | 0.772727 | 0.708333 | 0.850000 | 否 | 20 | 17 | 7 | 3 |
| JA2 | shadowsocks | G2 | youtube.com::video_playback | 5 | 0.705882 | 0.857143 | 0.600000 | 是 | 20 | 12 | 2 | 8 |
| JA2 | trojan | G0 | bing.com::search_results_view | 0 | 0.780488 | 0.761905 | 0.800000 | 否 | 20 | 16 | 5 | 4 |
| JA2 | trojan | G0 | developer.mozilla.org::document_view | 1 | 0.666667 | 0.636364 | 0.700000 | 否 | 20 | 14 | 8 | 6 |
| JA2 | trojan | G0 | github.com::repository_view | 2 | 0.894737 | 0.944444 | 0.850000 | 是 | 20 | 17 | 1 | 3 |
| JA2 | trojan | G0 | wikipedia.org::article_view | 3 | 0.780488 | 0.761905 | 0.800000 | 否 | 20 | 16 | 5 | 4 |
| JA2 | trojan | G0 | youtube.com::search_results_view | 4 | 0.789474 | 0.833333 | 0.750000 | 是 | 20 | 15 | 3 | 5 |
| JA2 | trojan | G0 | youtube.com::video_playback | 5 | 0.850000 | 0.850000 | 0.850000 | 否 | 20 | 17 | 3 | 3 |
| JA2 | trojan | G1 | bing.com::search_results_view | 0 | 0.742857 | 0.866667 | 0.650000 | 是 | 20 | 13 | 2 | 7 |
| JA2 | trojan | G1 | developer.mozilla.org::document_view | 1 | 0.761905 | 0.727273 | 0.800000 | 否 | 20 | 16 | 6 | 4 |
| JA2 | trojan | G1 | github.com::repository_view | 2 | 0.952381 | 0.909091 | 1.000000 | 否 | 20 | 20 | 2 | 0 |
| JA2 | trojan | G1 | wikipedia.org::article_view | 3 | 0.800000 | 0.800000 | 0.800000 | 是 | 20 | 16 | 4 | 4 |
| JA2 | trojan | G1 | youtube.com::search_results_view | 4 | 0.871795 | 0.894737 | 0.850000 | 否 | 20 | 17 | 2 | 3 |
| JA2 | trojan | G1 | youtube.com::video_playback | 5 | 0.857143 | 0.818182 | 0.900000 | 否 | 20 | 18 | 4 | 2 |
| JA2 | trojan | G2 | bing.com::search_results_view | 0 | 0.864865 | 0.941176 | 0.800000 | 否 | 20 | 16 | 1 | 4 |
| JA2 | trojan | G2 | developer.mozilla.org::document_view | 1 | 0.702703 | 0.764706 | 0.650000 | 是 | 20 | 13 | 4 | 7 |
| JA2 | trojan | G2 | github.com::repository_view | 2 | 0.952381 | 0.909091 | 1.000000 | 否 | 20 | 20 | 2 | 0 |
| JA2 | trojan | G2 | wikipedia.org::article_view | 3 | 0.711111 | 0.640000 | 0.800000 | 否 | 20 | 16 | 9 | 4 |
| JA2 | trojan | G2 | youtube.com::search_results_view | 4 | 0.857143 | 0.818182 | 0.900000 | 否 | 20 | 18 | 4 | 2 |
| JA2 | trojan | G2 | youtube.com::video_playback | 5 | 0.810811 | 0.882353 | 0.750000 | 是 | 20 | 15 | 2 | 5 |
| JA2 | vless | G0 | bing.com::search_results_view | 0 | 0.878049 | 0.857143 | 0.900000 | 否 | 20 | 18 | 3 | 2 |
| JA2 | vless | G0 | developer.mozilla.org::document_view | 1 | 0.780488 | 0.761905 | 0.800000 | 否 | 20 | 16 | 5 | 4 |
| JA2 | vless | G0 | github.com::repository_view | 2 | 0.833333 | 0.937500 | 0.750000 | 是 | 20 | 15 | 1 | 5 |
| JA2 | vless | G0 | wikipedia.org::article_view | 3 | 0.714286 | 0.681818 | 0.750000 | 否 | 20 | 15 | 7 | 5 |
| JA2 | vless | G0 | youtube.com::search_results_view | 4 | 0.871795 | 0.894737 | 0.850000 | 是 | 20 | 17 | 2 | 3 |
| JA2 | vless | G0 | youtube.com::video_playback | 5 | 0.829268 | 0.809524 | 0.850000 | 否 | 20 | 17 | 4 | 3 |
| JA2 | vless | G1 | bing.com::search_results_view | 0 | 0.871795 | 0.894737 | 0.850000 | 是 | 20 | 17 | 2 | 3 |
| JA2 | vless | G1 | developer.mozilla.org::document_view | 1 | 0.829268 | 0.809524 | 0.850000 | 否 | 20 | 17 | 4 | 3 |
| JA2 | vless | G1 | github.com::repository_view | 2 | 0.871795 | 0.894737 | 0.850000 | 否 | 20 | 17 | 2 | 3 |
| JA2 | vless | G1 | wikipedia.org::article_view | 3 | 0.702703 | 0.764706 | 0.650000 | 是 | 20 | 13 | 4 | 7 |
| JA2 | vless | G1 | youtube.com::search_results_view | 4 | 0.809524 | 0.772727 | 0.850000 | 否 | 20 | 17 | 5 | 3 |
| JA2 | vless | G1 | youtube.com::video_playback | 5 | 0.904762 | 0.863636 | 0.950000 | 否 | 20 | 19 | 3 | 1 |
| JA2 | vless | G2 | bing.com::search_results_view | 0 | 0.894737 | 0.944444 | 0.850000 | 否 | 20 | 17 | 1 | 3 |
| JA2 | vless | G2 | developer.mozilla.org::document_view | 1 | 0.769231 | 0.789474 | 0.750000 | 是 | 20 | 15 | 4 | 5 |
| JA2 | vless | G2 | github.com::repository_view | 2 | 0.894737 | 0.944444 | 0.850000 | 否 | 20 | 17 | 1 | 3 |
| JA2 | vless | G2 | wikipedia.org::article_view | 3 | 0.697674 | 0.652174 | 0.750000 | 否 | 20 | 15 | 8 | 5 |
| JA2 | vless | G2 | youtube.com::search_results_view | 4 | 0.800000 | 0.800000 | 0.800000 | 否 | 20 | 16 | 4 | 4 |
| JA2 | vless | G2 | youtube.com::video_playback | 5 | 0.904762 | 0.863636 | 0.950000 | 是 | 20 | 19 | 3 | 1 |
| JA2 | vmess | G0 | bing.com::search_results_view | 0 | 0.789474 | 0.833333 | 0.750000 | 否 | 20 | 15 | 3 | 5 |
| JA2 | vmess | G0 | developer.mozilla.org::document_view | 1 | 0.558140 | 0.521739 | 0.600000 | 否 | 20 | 12 | 11 | 8 |
| JA2 | vmess | G0 | github.com::repository_view | 2 | 0.727273 | 0.923077 | 0.600000 | 是 | 20 | 12 | 1 | 8 |
| JA2 | vmess | G0 | wikipedia.org::article_view | 3 | 0.666667 | 0.600000 | 0.750000 | 否 | 20 | 15 | 10 | 5 |
| JA2 | vmess | G0 | youtube.com::search_results_view | 4 | 0.900000 | 0.900000 | 0.900000 | 是 | 20 | 18 | 2 | 2 |
| JA2 | vmess | G0 | youtube.com::video_playback | 5 | 0.926829 | 0.904762 | 0.950000 | 否 | 20 | 19 | 2 | 1 |
| JA2 | vmess | G1 | bing.com::search_results_view | 0 | 0.620690 | 1.000000 | 0.450000 | 是 | 20 | 9 | 0 | 11 |
| JA2 | vmess | G1 | developer.mozilla.org::document_view | 1 | 0.642857 | 0.500000 | 0.900000 | 否 | 20 | 18 | 18 | 2 |
| JA2 | vmess | G1 | github.com::repository_view | 2 | 0.926829 | 0.904762 | 0.950000 | 否 | 20 | 19 | 2 | 1 |
| JA2 | vmess | G1 | wikipedia.org::article_view | 3 | 0.173913 | 0.666667 | 0.100000 | 是 | 20 | 2 | 1 | 18 |
| JA2 | vmess | G1 | youtube.com::search_results_view | 4 | 0.808511 | 0.703704 | 0.950000 | 否 | 20 | 19 | 8 | 1 |
| JA2 | vmess | G1 | youtube.com::video_playback | 5 | 0.863636 | 0.791667 | 0.950000 | 否 | 20 | 19 | 5 | 1 |
| JA2 | vmess | G2 | bing.com::search_results_view | 0 | 0.800000 | 0.720000 | 0.900000 | 否 | 20 | 18 | 7 | 2 |
| JA2 | vmess | G2 | developer.mozilla.org::document_view | 1 | 0.095238 | 1.000000 | 0.050000 | 是 | 20 | 1 | 0 | 19 |
| JA2 | vmess | G2 | github.com::repository_view | 2 | 0.900000 | 0.900000 | 0.900000 | 否 | 20 | 18 | 2 | 2 |
| JA2 | vmess | G2 | wikipedia.org::article_view | 3 | 0.679245 | 0.545455 | 0.900000 | 否 | 20 | 18 | 15 | 2 |
| JA2 | vmess | G2 | youtube.com::search_results_view | 4 | 0.857143 | 0.818182 | 0.900000 | 否 | 20 | 18 | 4 | 2 |
| JA2 | vmess | G2 | youtube.com::video_playback | 5 | 0.923077 | 0.947368 | 0.900000 | 是 | 20 | 18 | 1 | 2 |
| StrongPost | shadowsocks | G0 | bing.com::search_results_view | 0 | 0.789474 | 0.833333 | 0.750000 | 否 | 20 | 15 | 3 | 5 |
| StrongPost | shadowsocks | G0 | developer.mozilla.org::document_view | 1 | 0.780488 | 0.761905 | 0.800000 | 否 | 20 | 16 | 5 | 4 |
| StrongPost | shadowsocks | G0 | github.com::repository_view | 2 | 0.709677 | 1.000000 | 0.550000 | 是 | 20 | 11 | 0 | 9 |
| StrongPost | shadowsocks | G0 | wikipedia.org::article_view | 3 | 0.850000 | 0.850000 | 0.850000 | 否 | 20 | 17 | 3 | 3 |
| StrongPost | shadowsocks | G0 | youtube.com::search_results_view | 4 | 0.789474 | 0.833333 | 0.750000 | 是 | 20 | 15 | 3 | 5 |
| StrongPost | shadowsocks | G0 | youtube.com::video_playback | 5 | 0.769231 | 0.625000 | 1.000000 | 否 | 20 | 20 | 12 | 0 |
| StrongPost | shadowsocks | G1 | bing.com::search_results_view | 0 | 0.777778 | 0.875000 | 0.700000 | 是 | 20 | 14 | 2 | 6 |
| StrongPost | shadowsocks | G1 | developer.mozilla.org::document_view | 1 | 0.723404 | 0.629630 | 0.850000 | 否 | 20 | 17 | 10 | 3 |
| StrongPost | shadowsocks | G1 | github.com::repository_view | 2 | 0.864865 | 0.941176 | 0.800000 | 否 | 20 | 16 | 1 | 4 |
| StrongPost | shadowsocks | G1 | wikipedia.org::article_view | 3 | 0.687500 | 0.916667 | 0.550000 | 是 | 20 | 11 | 1 | 9 |
| StrongPost | shadowsocks | G1 | youtube.com::search_results_view | 4 | 0.857143 | 0.818182 | 0.900000 | 否 | 20 | 18 | 4 | 2 |
| StrongPost | shadowsocks | G1 | youtube.com::video_playback | 5 | 0.826087 | 0.730769 | 0.950000 | 否 | 20 | 19 | 7 | 1 |
| StrongPost | shadowsocks | G2 | bing.com::search_results_view | 0 | 0.755556 | 0.680000 | 0.850000 | 否 | 20 | 17 | 8 | 3 |
| StrongPost | shadowsocks | G2 | developer.mozilla.org::document_view | 1 | 0.400000 | 0.600000 | 0.300000 | 是 | 20 | 6 | 4 | 14 |
| StrongPost | shadowsocks | G2 | github.com::repository_view | 2 | 0.871795 | 0.894737 | 0.850000 | 否 | 20 | 17 | 2 | 3 |
| StrongPost | shadowsocks | G2 | wikipedia.org::article_view | 3 | 0.641509 | 0.515152 | 0.850000 | 否 | 20 | 17 | 16 | 3 |
| StrongPost | shadowsocks | G2 | youtube.com::search_results_view | 4 | 0.790698 | 0.739130 | 0.850000 | 否 | 20 | 17 | 6 | 3 |
| StrongPost | shadowsocks | G2 | youtube.com::video_playback | 5 | 0.600000 | 0.900000 | 0.450000 | 是 | 20 | 9 | 1 | 11 |
| StrongPost | trojan | G0 | bing.com::search_results_view | 0 | 0.850000 | 0.850000 | 0.850000 | 否 | 20 | 17 | 3 | 3 |
| StrongPost | trojan | G0 | developer.mozilla.org::document_view | 1 | 0.820513 | 0.842105 | 0.800000 | 否 | 20 | 16 | 3 | 4 |
| StrongPost | trojan | G0 | github.com::repository_view | 2 | 0.975610 | 0.952381 | 1.000000 | 是 | 20 | 20 | 1 | 0 |
| StrongPost | trojan | G0 | wikipedia.org::article_view | 3 | 0.842105 | 0.888889 | 0.800000 | 否 | 20 | 16 | 2 | 4 |
| StrongPost | trojan | G0 | youtube.com::search_results_view | 4 | 0.850000 | 0.850000 | 0.850000 | 是 | 20 | 17 | 3 | 3 |
| StrongPost | trojan | G0 | youtube.com::video_playback | 5 | 0.857143 | 0.818182 | 0.900000 | 否 | 20 | 18 | 4 | 2 |
| StrongPost | trojan | G1 | bing.com::search_results_view | 0 | 0.918919 | 1.000000 | 0.850000 | 是 | 20 | 17 | 0 | 3 |
| StrongPost | trojan | G1 | developer.mozilla.org::document_view | 1 | 0.837209 | 0.782609 | 0.900000 | 否 | 20 | 18 | 5 | 2 |
| StrongPost | trojan | G1 | github.com::repository_view | 2 | 1.000000 | 1.000000 | 1.000000 | 否 | 20 | 20 | 0 | 0 |
| StrongPost | trojan | G1 | wikipedia.org::article_view | 3 | 0.871795 | 0.894737 | 0.850000 | 是 | 20 | 17 | 2 | 3 |
| StrongPost | trojan | G1 | youtube.com::search_results_view | 4 | 0.820513 | 0.842105 | 0.800000 | 否 | 20 | 16 | 3 | 4 |
| StrongPost | trojan | G1 | youtube.com::video_playback | 5 | 0.857143 | 0.818182 | 0.900000 | 否 | 20 | 18 | 4 | 2 |
| StrongPost | trojan | G2 | bing.com::search_results_view | 0 | 0.878049 | 0.857143 | 0.900000 | 否 | 20 | 18 | 3 | 2 |
| StrongPost | trojan | G2 | developer.mozilla.org::document_view | 1 | 0.756757 | 0.823529 | 0.700000 | 是 | 20 | 14 | 3 | 6 |
| StrongPost | trojan | G2 | github.com::repository_view | 2 | 0.975610 | 0.952381 | 1.000000 | 否 | 20 | 20 | 1 | 0 |
| StrongPost | trojan | G2 | wikipedia.org::article_view | 3 | 0.820513 | 0.842105 | 0.800000 | 否 | 20 | 16 | 3 | 4 |
| StrongPost | trojan | G2 | youtube.com::search_results_view | 4 | 0.883721 | 0.826087 | 0.950000 | 否 | 20 | 19 | 4 | 1 |
| StrongPost | trojan | G2 | youtube.com::video_playback | 5 | 0.820513 | 0.842105 | 0.800000 | 是 | 20 | 16 | 3 | 4 |
| StrongPost | vless | G0 | bing.com::search_results_view | 0 | 0.923077 | 0.947368 | 0.900000 | 否 | 20 | 18 | 1 | 2 |
| StrongPost | vless | G0 | developer.mozilla.org::document_view | 1 | 0.800000 | 0.800000 | 0.800000 | 否 | 20 | 16 | 4 | 4 |
| StrongPost | vless | G0 | github.com::repository_view | 2 | 0.894737 | 0.944444 | 0.850000 | 是 | 20 | 17 | 1 | 3 |
| StrongPost | vless | G0 | wikipedia.org::article_view | 3 | 0.681818 | 0.625000 | 0.750000 | 否 | 20 | 15 | 9 | 5 |
| StrongPost | vless | G0 | youtube.com::search_results_view | 4 | 0.777778 | 0.875000 | 0.700000 | 是 | 20 | 14 | 2 | 6 |
| StrongPost | vless | G0 | youtube.com::video_playback | 5 | 0.837209 | 0.782609 | 0.900000 | 否 | 20 | 18 | 5 | 2 |
| StrongPost | vless | G1 | bing.com::search_results_view | 0 | 0.850000 | 0.850000 | 0.850000 | 是 | 20 | 17 | 3 | 3 |
| StrongPost | vless | G1 | developer.mozilla.org::document_view | 1 | 0.750000 | 0.750000 | 0.750000 | 否 | 20 | 15 | 5 | 5 |
| StrongPost | vless | G1 | github.com::repository_view | 2 | 0.900000 | 0.900000 | 0.900000 | 否 | 20 | 18 | 2 | 2 |
| StrongPost | vless | G1 | wikipedia.org::article_view | 3 | 0.684211 | 0.722222 | 0.650000 | 是 | 20 | 13 | 5 | 7 |
| StrongPost | vless | G1 | youtube.com::search_results_view | 4 | 0.731707 | 0.714286 | 0.750000 | 否 | 20 | 15 | 6 | 5 |
| StrongPost | vless | G1 | youtube.com::video_playback | 5 | 0.878049 | 0.857143 | 0.900000 | 否 | 20 | 18 | 3 | 2 |
| StrongPost | vless | G2 | bing.com::search_results_view | 0 | 0.904762 | 0.863636 | 0.950000 | 否 | 20 | 19 | 3 | 1 |
| StrongPost | vless | G2 | developer.mozilla.org::document_view | 1 | 0.777778 | 0.875000 | 0.700000 | 是 | 20 | 14 | 2 | 6 |
| StrongPost | vless | G2 | github.com::repository_view | 2 | 0.894737 | 0.944444 | 0.850000 | 否 | 20 | 17 | 1 | 3 |
| StrongPost | vless | G2 | wikipedia.org::article_view | 3 | 0.666667 | 0.600000 | 0.750000 | 否 | 20 | 15 | 10 | 5 |
| StrongPost | vless | G2 | youtube.com::search_results_view | 4 | 0.684211 | 0.722222 | 0.650000 | 否 | 20 | 13 | 5 | 7 |
| StrongPost | vless | G2 | youtube.com::video_playback | 5 | 0.878049 | 0.857143 | 0.900000 | 是 | 20 | 18 | 3 | 2 |
| StrongPost | vmess | G0 | bing.com::search_results_view | 0 | 0.769231 | 0.789474 | 0.750000 | 否 | 20 | 15 | 4 | 5 |
| StrongPost | vmess | G0 | developer.mozilla.org::document_view | 1 | 0.585366 | 0.571429 | 0.600000 | 否 | 20 | 12 | 9 | 8 |
| StrongPost | vmess | G0 | github.com::repository_view | 2 | 0.800000 | 0.933333 | 0.700000 | 是 | 20 | 14 | 1 | 6 |
| StrongPost | vmess | G0 | wikipedia.org::article_view | 3 | 0.711111 | 0.640000 | 0.800000 | 否 | 20 | 16 | 9 | 4 |
| StrongPost | vmess | G0 | youtube.com::search_results_view | 4 | 0.878049 | 0.857143 | 0.900000 | 是 | 20 | 18 | 3 | 2 |
| StrongPost | vmess | G0 | youtube.com::video_playback | 5 | 0.974359 | 1.000000 | 0.950000 | 否 | 20 | 19 | 0 | 1 |
| StrongPost | vmess | G1 | bing.com::search_results_view | 0 | 0.789474 | 0.833333 | 0.750000 | 是 | 20 | 15 | 3 | 5 |
| StrongPost | vmess | G1 | developer.mozilla.org::document_view | 1 | 0.727273 | 0.666667 | 0.800000 | 否 | 20 | 16 | 8 | 4 |
| StrongPost | vmess | G1 | github.com::repository_view | 2 | 0.926829 | 0.904762 | 0.950000 | 否 | 20 | 19 | 2 | 1 |
| StrongPost | vmess | G1 | wikipedia.org::article_view | 3 | 0.764706 | 0.928571 | 0.650000 | 是 | 20 | 13 | 1 | 7 |
| StrongPost | vmess | G1 | youtube.com::search_results_view | 4 | 0.909091 | 0.833333 | 1.000000 | 否 | 20 | 20 | 4 | 0 |
| StrongPost | vmess | G1 | youtube.com::video_playback | 5 | 0.974359 | 1.000000 | 0.950000 | 否 | 20 | 19 | 0 | 1 |
| StrongPost | vmess | G2 | bing.com::search_results_view | 0 | 0.731707 | 0.714286 | 0.750000 | 否 | 20 | 15 | 6 | 5 |
| StrongPost | vmess | G2 | developer.mozilla.org::document_view | 1 | 0.344828 | 0.555556 | 0.250000 | 是 | 20 | 5 | 4 | 15 |
| StrongPost | vmess | G2 | github.com::repository_view | 2 | 0.883721 | 0.826087 | 0.950000 | 否 | 20 | 19 | 4 | 1 |
| StrongPost | vmess | G2 | wikipedia.org::article_view | 3 | 0.695652 | 0.615385 | 0.800000 | 否 | 20 | 16 | 10 | 4 |
| StrongPost | vmess | G2 | youtube.com::search_results_view | 4 | 0.883721 | 0.826087 | 0.950000 | 否 | 20 | 19 | 4 | 1 |
| StrongPost | vmess | G2 | youtube.com::video_playback | 5 | 0.947368 | 1.000000 | 0.900000 | 是 | 20 | 18 | 0 | 2 |

## 全部600个外层折评分

| arm | target | group | outer | F1_all | accuracy | CE_nats | Brier | CE_bits | F1_uncovered | F1_aux |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CT0 | shadowsocks | G0 | 0 | 0.634524 | 0.666667 | 0.978913 | 0.462313 | 1.412273 | 0.333333 | 0.785119 |
| CT0 | shadowsocks | G0 | 1 | 0.570370 | 0.625000 | 1.516027 | 0.585864 | 2.187165 | 0.333333 | 0.688889 |
| CT0 | shadowsocks | G0 | 2 | 0.604497 | 0.666667 | 2.262100 | 0.679139 | 3.263520 | 0.285714 | 0.763889 |
| CT0 | shadowsocks | G0 | 3 | 0.742725 | 0.750000 | 1.101438 | 0.312403 | 1.589040 | 0.803571 | 0.712302 |
| CT0 | shadowsocks | G0 | 4 | 0.601058 | 0.666667 | 2.319340 | 0.575741 | 3.346100 | 0.200000 | 0.801587 |
| CT0 | shadowsocks | G1 | 0 | 0.632194 | 0.708333 | 1.873602 | 0.516885 | 2.703036 | 0.200000 | 0.848291 |
| CT0 | shadowsocks | G1 | 1 | 0.550712 | 0.666667 | 1.598624 | 0.525639 | 2.306326 | 0.000000 | 0.826068 |
| CT0 | shadowsocks | G1 | 2 | 0.630891 | 0.666667 | 2.014569 | 0.590263 | 2.906409 | 0.333333 | 0.779670 |
| CT0 | shadowsocks | G1 | 3 | 0.594444 | 0.666667 | 2.855664 | 0.627220 | 4.119852 | 0.200000 | 0.791667 |
| CT0 | shadowsocks | G1 | 4 | 0.696825 | 0.750000 | 2.181416 | 0.490708 | 3.147119 | 0.428571 | 0.830952 |
| CT0 | shadowsocks | G2 | 0 | 0.503704 | 0.625000 | 2.069503 | 0.622687 | 2.985661 | 0.000000 | 0.755556 |
| CT0 | shadowsocks | G2 | 1 | 0.475180 | 0.583333 | 2.001421 | 0.691316 | 2.887440 | 0.000000 | 0.712771 |
| CT0 | shadowsocks | G2 | 2 | 0.547138 | 0.666667 | 2.129050 | 0.595434 | 3.071570 | 0.000000 | 0.820707 |
| CT0 | shadowsocks | G2 | 3 | 0.466667 | 0.583333 | 2.763435 | 0.693250 | 3.986794 | 0.000000 | 0.700000 |
| CT0 | shadowsocks | G2 | 4 | 0.553490 | 0.625000 | 1.545719 | 0.585160 | 2.230002 | 0.200000 | 0.730235 |
| CT0 | trojan | G0 | 0 | 0.915344 | 0.916667 | 0.281475 | 0.147522 | 0.406082 | 0.944444 | 0.900794 |
| CT0 | trojan | G0 | 1 | 0.877381 | 0.875000 | 0.277587 | 0.164791 | 0.400474 | 0.875000 | 0.878571 |
| CT0 | trojan | G0 | 2 | 0.868783 | 0.875000 | 0.382876 | 0.227842 | 0.552373 | 0.833333 | 0.886508 |
| CT0 | trojan | G0 | 3 | 0.751323 | 0.750000 | 0.567981 | 0.324125 | 0.819423 | 0.873016 | 0.690476 |
| CT0 | trojan | G0 | 4 | 0.873677 | 0.875000 | 0.439667 | 0.236166 | 0.634306 | 0.928571 | 0.846230 |
| CT0 | trojan | G1 | 0 | 0.874339 | 0.875000 | 0.343518 | 0.196979 | 0.495592 | 0.803571 | 0.909722 |
| CT0 | trojan | G1 | 1 | 0.883117 | 0.875000 | 0.611054 | 0.182708 | 0.881564 | 0.857143 | 0.896104 |
| CT0 | trojan | G1 | 2 | 0.830688 | 0.833333 | 0.507197 | 0.281429 | 0.731731 | 0.944444 | 0.773810 |
| CT0 | trojan | G1 | 3 | 0.781746 | 0.791667 | 0.483167 | 0.275192 | 0.697063 | 0.761905 | 0.791667 |
| CT0 | trojan | G1 | 4 | 0.828042 | 0.833333 | 0.499322 | 0.246669 | 0.720369 | 0.833333 | 0.825397 |
| CT0 | trojan | G2 | 0 | 0.826720 | 0.833333 | 0.379335 | 0.218220 | 0.547265 | 0.785714 | 0.847222 |
| CT0 | trojan | G2 | 1 | 0.957672 | 0.958333 | 0.218121 | 0.100906 | 0.314682 | 0.928571 | 0.972222 |
| CT0 | trojan | G2 | 2 | 0.784127 | 0.791667 | 0.525911 | 0.291079 | 0.758729 | 0.619048 | 0.866667 |
| CT0 | trojan | G2 | 3 | 0.784392 | 0.791667 | 0.577549 | 0.300255 | 0.833228 | 0.660714 | 0.846230 |
| CT0 | trojan | G2 | 4 | 0.814815 | 0.833333 | 0.322037 | 0.187163 | 0.464602 | 0.666667 | 0.888889 |
| CT0 | vless | G0 | 0 | 0.749206 | 0.750000 | 0.947026 | 0.402068 | 1.366270 | 0.785714 | 0.730952 |
| CT0 | vless | G0 | 1 | 0.787434 | 0.791667 | 0.578589 | 0.344794 | 0.834728 | 0.803571 | 0.779365 |
| CT0 | vless | G0 | 2 | 0.836640 | 0.833333 | 0.875737 | 0.368055 | 1.263422 | 0.857143 | 0.826389 |
| CT0 | vless | G0 | 3 | 0.873677 | 0.875000 | 0.332108 | 0.172305 | 0.479131 | 0.928571 | 0.846230 |
| CT0 | vless | G0 | 4 | 0.877381 | 0.875000 | 0.754397 | 0.261975 | 1.088365 | 0.803571 | 0.914286 |
| CT0 | vless | G1 | 0 | 0.837302 | 0.833333 | 0.864776 | 0.278255 | 1.247608 | 0.750000 | 0.880952 |
| CT0 | vless | G1 | 1 | 0.767196 | 0.791667 | 0.936853 | 0.336963 | 1.351593 | 0.628571 | 0.836508 |
| CT0 | vless | G1 | 2 | 0.717063 | 0.708333 | 0.947062 | 0.384779 | 1.366322 | 0.761905 | 0.694643 |
| CT0 | vless | G1 | 3 | 0.874339 | 0.875000 | 0.598708 | 0.178833 | 0.863753 | 0.819444 | 0.901786 |
| CT0 | vless | G1 | 4 | 0.873677 | 0.875000 | 0.862095 | 0.178577 | 1.243741 | 0.857143 | 0.881944 |
| CT0 | vless | G2 | 0 | 0.828704 | 0.833333 | 0.618057 | 0.320401 | 0.891668 | 0.833333 | 0.826389 |
| CT0 | vless | G2 | 1 | 0.874339 | 0.875000 | 0.466472 | 0.207880 | 0.672977 | 0.944444 | 0.839286 |
| CT0 | vless | G2 | 2 | 0.684307 | 0.708333 | 1.023175 | 0.477850 | 1.476129 | 0.575000 | 0.738961 |
| CT0 | vless | G2 | 3 | 0.827778 | 0.833333 | 0.559496 | 0.255067 | 0.807183 | 0.833333 | 0.825000 |
| CT0 | vless | G2 | 4 | 0.786376 | 0.791667 | 0.971866 | 0.334221 | 1.402106 | 0.761905 | 0.798611 |
| CT0 | vmess | G0 | 0 | 0.728884 | 0.750000 | 0.707417 | 0.321777 | 1.020587 | 0.628571 | 0.779040 |
| CT0 | vmess | G0 | 1 | 0.741270 | 0.750000 | 1.009179 | 0.379843 | 1.455937 | 0.857143 | 0.683333 |
| CT0 | vmess | G0 | 2 | 0.617857 | 0.625000 | 1.482125 | 0.651192 | 2.138255 | 0.595238 | 0.629167 |
| CT0 | vmess | G0 | 3 | 0.689069 | 0.708333 | 1.907007 | 0.477454 | 2.751229 | 0.761905 | 0.652652 |
| CT0 | vmess | G0 | 4 | 0.731746 | 0.750000 | 0.804181 | 0.352869 | 1.160187 | 0.600000 | 0.797619 |
| CT0 | vmess | G1 | 0 | 0.625926 | 0.708333 | 1.848179 | 0.458358 | 2.666358 | 0.200000 | 0.838889 |
| CT0 | vmess | G1 | 1 | 0.470455 | 0.583333 | 1.720737 | 0.628553 | 2.482499 | 0.000000 | 0.705682 |
| CT0 | vmess | G1 | 2 | 0.550712 | 0.666667 | 2.935502 | 0.625067 | 4.235035 | 0.000000 | 0.826068 |
| CT0 | vmess | G1 | 3 | 0.728704 | 0.750000 | 1.972755 | 0.428065 | 2.846084 | 0.533333 | 0.826389 |
| CT0 | vmess | G1 | 4 | 0.513228 | 0.625000 | 2.001367 | 0.609407 | 2.887362 | 0.000000 | 0.769841 |
| CT0 | vmess | G2 | 0 | 0.641005 | 0.708333 | 0.887188 | 0.374611 | 1.279942 | 0.428571 | 0.747222 |
| CT0 | vmess | G2 | 1 | 0.687302 | 0.750000 | 1.046395 | 0.455089 | 1.509629 | 0.500000 | 0.780952 |
| CT0 | vmess | G2 | 2 | 0.656746 | 0.708333 | 1.634400 | 0.526374 | 2.357941 | 0.500000 | 0.735119 |
| CT0 | vmess | G2 | 3 | 0.730736 | 0.791667 | 1.470334 | 0.369130 | 2.121244 | 0.428571 | 0.881818 |
| CT0 | vmess | G2 | 4 | 0.650000 | 0.708333 | 1.488344 | 0.505529 | 2.147226 | 0.500000 | 0.725000 |
| CT1 | shadowsocks | G0 | 0 | 0.698413 | 0.708333 | 0.968094 | 0.391051 | 1.396664 | 0.533333 | 0.780952 |
| CT1 | shadowsocks | G0 | 1 | 0.564550 | 0.583333 | 1.581755 | 0.621467 | 2.281991 | 0.400000 | 0.646825 |
| CT1 | shadowsocks | G0 | 2 | 0.650974 | 0.666667 | 1.645861 | 0.529481 | 2.374475 | 0.628571 | 0.662175 |
| CT1 | shadowsocks | G0 | 3 | 0.703755 | 0.750000 | 1.165136 | 0.366570 | 1.680937 | 0.500000 | 0.805632 |
| CT1 | shadowsocks | G0 | 4 | 0.668783 | 0.708333 | 1.724511 | 0.490033 | 2.487944 | 0.400000 | 0.803175 |
| CT1 | shadowsocks | G1 | 0 | 0.643386 | 0.708333 | 2.469144 | 0.565864 | 3.562222 | 0.200000 | 0.865079 |
| CT1 | shadowsocks | G1 | 1 | 0.519577 | 0.625000 | 1.618661 | 0.585285 | 2.335235 | 0.000000 | 0.779365 |
| CT1 | shadowsocks | G1 | 2 | 0.564886 | 0.625000 | 2.119662 | 0.634719 | 3.058027 | 0.200000 | 0.747329 |
| CT1 | shadowsocks | G1 | 3 | 0.594231 | 0.666667 | 2.935780 | 0.558194 | 4.235435 | 0.200000 | 0.791346 |
| CT1 | shadowsocks | G1 | 4 | 0.664021 | 0.708333 | 2.300812 | 0.543227 | 3.319370 | 0.333333 | 0.829365 |
| CT1 | shadowsocks | G2 | 0 | 0.503704 | 0.625000 | 2.182306 | 0.647069 | 3.148402 | 0.000000 | 0.755556 |
| CT1 | shadowsocks | G2 | 1 | 0.522655 | 0.583333 | 1.781613 | 0.631703 | 2.570324 | 0.200000 | 0.683983 |
| CT1 | shadowsocks | G2 | 2 | 0.547138 | 0.666667 | 1.641692 | 0.515617 | 2.368461 | 0.000000 | 0.820707 |
| CT1 | shadowsocks | G2 | 3 | 0.405724 | 0.500000 | 2.434706 | 0.770247 | 3.512538 | 0.000000 | 0.608586 |
| CT1 | shadowsocks | G2 | 4 | 0.513889 | 0.583333 | 1.312228 | 0.562926 | 1.893144 | 0.166667 | 0.687500 |
| CT1 | trojan | G0 | 0 | 0.878307 | 0.875000 | 0.395241 | 0.224010 | 0.570212 | 0.928571 | 0.853175 |
| CT1 | trojan | G0 | 1 | 0.785053 | 0.791667 | 0.550764 | 0.271210 | 0.794585 | 0.875000 | 0.740079 |
| CT1 | trojan | G0 | 2 | 0.679497 | 0.708333 | 0.948661 | 0.411445 | 1.368629 | 0.533333 | 0.752579 |
| CT1 | trojan | G0 | 3 | 0.835053 | 0.833333 | 0.622331 | 0.287714 | 0.897834 | 0.873016 | 0.816071 |
| CT1 | trojan | G0 | 4 | 0.832672 | 0.833333 | 0.372519 | 0.222679 | 0.537432 | 0.928571 | 0.784722 |
| CT1 | trojan | G1 | 0 | 0.871429 | 0.875000 | 0.270233 | 0.179784 | 0.389864 | 0.785714 | 0.914286 |
| CT1 | trojan | G1 | 1 | 0.785895 | 0.791667 | 0.698758 | 0.286339 | 1.008095 | 0.619048 | 0.869318 |
| CT1 | trojan | G1 | 2 | 0.764153 | 0.791667 | 0.554948 | 0.321861 | 0.800620 | 0.888889 | 0.701786 |
| CT1 | trojan | G1 | 3 | 0.828042 | 0.833333 | 0.563975 | 0.283618 | 0.813644 | 0.761905 | 0.861111 |
| CT1 | trojan | G1 | 4 | 0.868783 | 0.875000 | 0.373265 | 0.227705 | 0.538507 | 0.833333 | 0.886508 |
| CT1 | trojan | G2 | 0 | 0.827116 | 0.833333 | 0.741823 | 0.268949 | 1.070224 | 0.761905 | 0.859722 |
| CT1 | trojan | G2 | 1 | 0.828704 | 0.833333 | 0.420112 | 0.239998 | 0.606093 | 0.875000 | 0.805556 |
| CT1 | trojan | G2 | 2 | 0.675709 | 0.708333 | 0.857524 | 0.426473 | 1.237146 | 0.533333 | 0.746898 |
| CT1 | trojan | G2 | 3 | 0.826058 | 0.833333 | 0.767223 | 0.332994 | 1.106869 | 0.785714 | 0.846230 |
| CT1 | trojan | G2 | 4 | 0.830688 | 0.833333 | 0.319498 | 0.191385 | 0.460938 | 0.714286 | 0.888889 |
| CT1 | vless | G0 | 0 | 0.749206 | 0.750000 | 0.896964 | 0.400105 | 1.294046 | 0.785714 | 0.730952 |
| CT1 | vless | G0 | 1 | 0.748413 | 0.750000 | 0.591979 | 0.290690 | 0.854045 | 0.803571 | 0.720833 |
| CT1 | vless | G0 | 2 | 0.756085 | 0.750000 | 0.908745 | 0.459894 | 1.311042 | 0.761905 | 0.753175 |
| CT1 | vless | G0 | 3 | 0.957672 | 0.958333 | 0.291494 | 0.112004 | 0.420536 | 1.000000 | 0.936508 |
| CT1 | vless | G0 | 4 | 0.873677 | 0.875000 | 0.886285 | 0.263610 | 1.278640 | 0.928571 | 0.846230 |
| CT1 | vless | G1 | 0 | 0.782540 | 0.791667 | 0.771407 | 0.358887 | 1.112905 | 0.685714 | 0.830952 |
| CT1 | vless | G1 | 1 | 0.767196 | 0.791667 | 1.212582 | 0.373534 | 1.749386 | 0.628571 | 0.836508 |
| CT1 | vless | G1 | 2 | 0.687037 | 0.708333 | 1.314425 | 0.513420 | 1.896315 | 0.708333 | 0.676389 |
| CT1 | vless | G1 | 3 | 0.957672 | 0.958333 | 0.489743 | 0.096506 | 0.706550 | 0.928571 | 0.972222 |
| CT1 | vless | G1 | 4 | 0.915344 | 0.916667 | 0.652892 | 0.174240 | 0.941924 | 0.857143 | 0.944444 |
| CT1 | vless | G2 | 0 | 0.711159 | 0.708333 | 0.808239 | 0.386770 | 1.166042 | 0.761905 | 0.685786 |
| CT1 | vless | G2 | 1 | 0.915344 | 0.916667 | 0.588863 | 0.190041 | 0.849550 | 0.944444 | 0.900794 |
| CT1 | vless | G2 | 2 | 0.646825 | 0.625000 | 1.189929 | 0.586714 | 1.716704 | 0.500000 | 0.720238 |
| CT1 | vless | G2 | 3 | 0.870370 | 0.875000 | 0.334877 | 0.160984 | 0.483125 | 0.833333 | 0.888889 |
| CT1 | vless | G2 | 4 | 0.835979 | 0.833333 | 0.839124 | 0.294811 | 1.210600 | 0.857143 | 0.825397 |
| CT1 | vmess | G0 | 0 | 0.835714 | 0.833333 | 0.847925 | 0.273738 | 1.223297 | 0.857143 | 0.825000 |
| CT1 | vmess | G0 | 1 | 0.739586 | 0.750000 | 0.986218 | 0.427829 | 1.422811 | 0.857143 | 0.680808 |
| CT1 | vmess | G0 | 2 | 0.621561 | 0.625000 | 1.324108 | 0.594124 | 1.910284 | 0.595238 | 0.634722 |
| CT1 | vmess | G0 | 3 | 0.690043 | 0.708333 | 1.786771 | 0.481434 | 2.577766 | 0.628571 | 0.720779 |
| CT1 | vmess | G0 | 4 | 0.728042 | 0.750000 | 0.914366 | 0.389533 | 1.319152 | 0.644444 | 0.769841 |
| CT1 | vmess | G1 | 0 | 0.735450 | 0.791667 | 1.870616 | 0.403347 | 2.698728 | 0.428571 | 0.888889 |
| CT1 | vmess | G1 | 1 | 0.470455 | 0.583333 | 2.146949 | 0.686527 | 3.097393 | 0.000000 | 0.705682 |
| CT1 | vmess | G1 | 2 | 0.547009 | 0.666667 | 2.586559 | 0.638079 | 3.731616 | 0.000000 | 0.820513 |
| CT1 | vmess | G1 | 3 | 0.613889 | 0.666667 | 1.502662 | 0.552979 | 2.167883 | 0.200000 | 0.820833 |
| CT1 | vmess | G1 | 4 | 0.514782 | 0.625000 | 2.813851 | 0.668086 | 4.059528 | 0.000000 | 0.772172 |
| CT1 | vmess | G2 | 0 | 0.640789 | 0.708333 | 1.074496 | 0.473971 | 1.550170 | 0.428571 | 0.746898 |
| CT1 | vmess | G2 | 1 | 0.687302 | 0.750000 | 1.897738 | 0.504918 | 2.737856 | 0.500000 | 0.780952 |
| CT1 | vmess | G2 | 2 | 0.622655 | 0.666667 | 1.599738 | 0.509323 | 2.307934 | 0.500000 | 0.683983 |
| CT1 | vmess | G2 | 3 | 0.730736 | 0.791667 | 1.823821 | 0.443898 | 2.631217 | 0.428571 | 0.881818 |
| CT1 | vmess | G2 | 4 | 0.650000 | 0.708333 | 1.308198 | 0.466588 | 1.887331 | 0.500000 | 0.725000 |
| CT2 | shadowsocks | G0 | 0 | 0.841450 | 0.833333 | 0.440739 | 0.255382 | 0.635852 | 0.857143 | 0.833604 |
| CT2 | shadowsocks | G0 | 1 | 0.774603 | 0.791667 | 0.813660 | 0.321727 | 1.173863 | 0.857143 | 0.733333 |
| CT2 | shadowsocks | G0 | 2 | 0.635053 | 0.708333 | 1.158501 | 0.466025 | 1.671363 | 0.400000 | 0.752579 |
| CT2 | shadowsocks | G0 | 3 | 0.826720 | 0.833333 | 0.900484 | 0.263456 | 1.299123 | 0.875000 | 0.802579 |
| CT2 | shadowsocks | G0 | 4 | 0.728042 | 0.750000 | 0.971594 | 0.426195 | 1.401714 | 0.533333 | 0.825397 |
| CT2 | shadowsocks | G1 | 0 | 0.865079 | 0.875000 | 0.783844 | 0.248230 | 1.130847 | 0.761905 | 0.916667 |
| CT2 | shadowsocks | G1 | 1 | 0.836640 | 0.833333 | 0.527269 | 0.260026 | 0.760689 | 0.761905 | 0.874008 |
| CT2 | shadowsocks | G1 | 2 | 0.790079 | 0.791667 | 0.802268 | 0.350444 | 1.157428 | 0.833333 | 0.768452 |
| CT2 | shadowsocks | G1 | 3 | 0.722222 | 0.750000 | 0.808231 | 0.320799 | 1.166030 | 0.533333 | 0.816667 |
| CT2 | shadowsocks | G1 | 4 | 0.702742 | 0.708333 | 0.718567 | 0.384229 | 1.036673 | 0.714286 | 0.696970 |
| CT2 | shadowsocks | G2 | 0 | 0.694444 | 0.708333 | 1.044395 | 0.488614 | 1.506743 | 0.500000 | 0.791667 |
| CT2 | shadowsocks | G2 | 1 | 0.571429 | 0.625000 | 1.022656 | 0.537885 | 1.475381 | 0.200000 | 0.757143 |
| CT2 | shadowsocks | G2 | 2 | 0.484524 | 0.541667 | 1.416834 | 0.691490 | 2.044059 | 0.142857 | 0.655357 |
| CT2 | shadowsocks | G2 | 3 | 0.827778 | 0.833333 | 0.958801 | 0.353135 | 1.383258 | 0.833333 | 0.825000 |
| CT2 | shadowsocks | G2 | 4 | 0.753968 | 0.750000 | 0.743137 | 0.346318 | 1.072120 | 0.571429 | 0.845238 |
| CT2 | trojan | G0 | 0 | 0.915344 | 0.916667 | 0.316601 | 0.166678 | 0.456758 | 0.944444 | 0.900794 |
| CT2 | trojan | G0 | 1 | 0.915344 | 0.916667 | 0.358469 | 0.168140 | 0.517162 | 0.944444 | 0.900794 |
| CT2 | trojan | G0 | 2 | 0.868783 | 0.875000 | 0.356769 | 0.212508 | 0.514709 | 0.833333 | 0.886508 |
| CT2 | trojan | G0 | 3 | 0.784392 | 0.791667 | 0.450550 | 0.264504 | 0.650007 | 0.888889 | 0.732143 |
| CT2 | trojan | G0 | 4 | 0.832672 | 0.833333 | 0.391123 | 0.236858 | 0.564272 | 0.928571 | 0.784722 |
| CT2 | trojan | G1 | 0 | 0.874339 | 0.875000 | 0.278787 | 0.156368 | 0.402205 | 0.803571 | 0.909722 |
| CT2 | trojan | G1 | 1 | 0.919048 | 0.916667 | 0.543539 | 0.189025 | 0.784161 | 0.928571 | 0.914286 |
| CT2 | trojan | G1 | 2 | 0.830688 | 0.833333 | 0.515054 | 0.303101 | 0.743066 | 0.944444 | 0.773810 |
| CT2 | trojan | G1 | 3 | 0.873677 | 0.875000 | 0.382418 | 0.209032 | 0.551713 | 0.857143 | 0.881944 |
| CT2 | trojan | G1 | 4 | 0.915344 | 0.916667 | 0.408417 | 0.219574 | 0.589222 | 0.928571 | 0.908730 |
| CT2 | trojan | G2 | 0 | 0.865741 | 0.875000 | 0.372098 | 0.207034 | 0.536824 | 0.833333 | 0.881944 |
| CT2 | trojan | G2 | 1 | 0.915344 | 0.916667 | 0.276294 | 0.151772 | 0.398609 | 0.888889 | 0.928571 |
| CT2 | trojan | G2 | 2 | 0.784127 | 0.791667 | 0.464700 | 0.274186 | 0.670421 | 0.619048 | 0.866667 |
| CT2 | trojan | G2 | 3 | 0.784392 | 0.791667 | 0.513590 | 0.288086 | 0.740953 | 0.660714 | 0.846230 |
| CT2 | trojan | G2 | 4 | 0.916005 | 0.916667 | 0.326284 | 0.189009 | 0.470728 | 0.875000 | 0.936508 |
| CT2 | vless | G0 | 0 | 0.754930 | 0.750000 | 0.683289 | 0.347713 | 0.985778 | 0.785714 | 0.739538 |
| CT2 | vless | G0 | 1 | 0.787434 | 0.791667 | 0.682205 | 0.341960 | 0.984214 | 0.803571 | 0.779365 |
| CT2 | vless | G0 | 2 | 0.756746 | 0.750000 | 0.716803 | 0.376796 | 1.034128 | 0.761905 | 0.754167 |
| CT2 | vless | G0 | 3 | 0.916005 | 0.916667 | 0.293534 | 0.132173 | 0.423479 | 1.000000 | 0.874008 |
| CT2 | vless | G0 | 4 | 0.877381 | 0.875000 | 0.721234 | 0.253667 | 1.040521 | 0.803571 | 0.914286 |
| CT2 | vless | G1 | 0 | 0.790079 | 0.791667 | 0.658470 | 0.319920 | 0.949971 | 0.733333 | 0.818452 |
| CT2 | vless | G1 | 1 | 0.767196 | 0.791667 | 0.716419 | 0.294478 | 1.033575 | 0.628571 | 0.836508 |
| CT2 | vless | G1 | 2 | 0.673280 | 0.666667 | 0.849921 | 0.453918 | 1.226177 | 0.708333 | 0.655754 |
| CT2 | vless | G1 | 3 | 0.874339 | 0.875000 | 0.514973 | 0.183101 | 0.742949 | 0.875000 | 0.874008 |
| CT2 | vless | G1 | 4 | 0.873677 | 0.875000 | 0.612155 | 0.205797 | 0.883153 | 0.857143 | 0.881944 |
| CT2 | vless | G2 | 0 | 0.787831 | 0.791667 | 0.677247 | 0.339393 | 0.977061 | 0.833333 | 0.765079 |
| CT2 | vless | G2 | 1 | 0.826058 | 0.833333 | 0.485366 | 0.222004 | 0.700234 | 0.888889 | 0.794643 |
| CT2 | vless | G2 | 2 | 0.743567 | 0.750000 | 0.823879 | 0.419464 | 1.188607 | 0.660714 | 0.784993 |
| CT2 | vless | G2 | 3 | 0.874339 | 0.875000 | 0.490625 | 0.212995 | 0.707822 | 0.928571 | 0.847222 |
| CT2 | vless | G2 | 4 | 0.757937 | 0.750000 | 0.710873 | 0.295445 | 1.025573 | 0.803571 | 0.735119 |
| CT2 | vmess | G0 | 0 | 0.832672 | 0.833333 | 0.420336 | 0.211746 | 0.606417 | 0.873016 | 0.812500 |
| CT2 | vmess | G0 | 1 | 0.778307 | 0.791667 | 0.613581 | 0.298838 | 0.885210 | 0.857143 | 0.738889 |
| CT2 | vmess | G0 | 2 | 0.567100 | 0.583333 | 1.678055 | 0.574303 | 2.420922 | 0.595238 | 0.553030 |
| CT2 | vmess | G0 | 3 | 0.868783 | 0.875000 | 0.832990 | 0.246527 | 1.201750 | 1.000000 | 0.803175 |
| CT2 | vmess | G0 | 4 | 0.835714 | 0.833333 | 0.697858 | 0.261445 | 1.006797 | 0.828571 | 0.839286 |
| CT2 | vmess | G1 | 0 | 0.907407 | 0.916667 | 0.493011 | 0.185163 | 0.711264 | 0.833333 | 0.944444 |
| CT2 | vmess | G1 | 1 | 0.828042 | 0.833333 | 0.522460 | 0.273116 | 0.753751 | 0.761905 | 0.861111 |
| CT2 | vmess | G1 | 2 | 0.828704 | 0.833333 | 0.545520 | 0.303474 | 0.787019 | 0.708333 | 0.888889 |
| CT2 | vmess | G1 | 3 | 0.795635 | 0.791667 | 0.865684 | 0.275559 | 1.248918 | 0.708333 | 0.839286 |
| CT2 | vmess | G1 | 4 | 0.876720 | 0.875000 | 0.704257 | 0.208945 | 1.016029 | 0.857143 | 0.886508 |
| CT2 | vmess | G2 | 0 | 0.781481 | 0.791667 | 0.414995 | 0.249447 | 0.598712 | 0.714286 | 0.815079 |
| CT2 | vmess | G2 | 1 | 0.686243 | 0.708333 | 1.232840 | 0.440531 | 1.778611 | 0.642857 | 0.707937 |
| CT2 | vmess | G2 | 2 | 0.706481 | 0.750000 | 0.972225 | 0.442069 | 1.402624 | 0.500000 | 0.809722 |
| CT2 | vmess | G2 | 3 | 0.809524 | 0.833333 | 0.913365 | 0.284916 | 1.317707 | 0.628571 | 0.900000 |
| CT2 | vmess | G2 | 4 | 0.727778 | 0.750000 | 0.896819 | 0.372266 | 1.293837 | 0.700000 | 0.741667 |
| CT3 | shadowsocks | G0 | 0 | 0.651984 | 0.666667 | 1.428391 | 0.453584 | 2.060732 | 0.366667 | 0.794643 |
| CT3 | shadowsocks | G0 | 1 | 0.694805 | 0.708333 | 1.009929 | 0.469765 | 1.457019 | 0.761905 | 0.661255 |
| CT3 | shadowsocks | G0 | 2 | 0.637747 | 0.708333 | 1.083278 | 0.480041 | 1.562839 | 0.444444 | 0.734398 |
| CT3 | shadowsocks | G0 | 3 | 0.785053 | 0.791667 | 1.105858 | 0.348626 | 1.595417 | 0.819444 | 0.767857 |
| CT3 | shadowsocks | G0 | 4 | 0.728042 | 0.750000 | 0.827249 | 0.333810 | 1.193468 | 0.533333 | 0.825397 |
| CT3 | shadowsocks | G1 | 0 | 0.826455 | 0.833333 | 0.805503 | 0.298767 | 1.162096 | 0.761905 | 0.858730 |
| CT3 | shadowsocks | G1 | 1 | 0.734295 | 0.750000 | 0.699476 | 0.337379 | 1.009130 | 0.485714 | 0.858586 |
| CT3 | shadowsocks | G1 | 2 | 0.665344 | 0.708333 | 1.136232 | 0.508488 | 1.639236 | 0.428571 | 0.783730 |
| CT3 | shadowsocks | G1 | 3 | 0.665657 | 0.708333 | 3.025649 | 0.549129 | 4.365089 | 0.400000 | 0.798485 |
| CT3 | shadowsocks | G1 | 4 | 0.703093 | 0.750000 | 0.927624 | 0.418207 | 1.338278 | 0.428571 | 0.840354 |
| CT3 | shadowsocks | G2 | 0 | 0.574339 | 0.625000 | 1.570890 | 0.512759 | 2.266316 | 0.300000 | 0.711508 |
| CT3 | shadowsocks | G2 | 1 | 0.553968 | 0.625000 | 1.174449 | 0.573448 | 1.694372 | 0.200000 | 0.730952 |
| CT3 | shadowsocks | G2 | 2 | 0.544444 | 0.666667 | 1.046368 | 0.500741 | 1.509590 | 0.000000 | 0.816667 |
| CT3 | shadowsocks | G2 | 3 | 0.548148 | 0.625000 | 1.480181 | 0.546502 | 2.135450 | 0.200000 | 0.722222 |
| CT3 | shadowsocks | G2 | 4 | 0.623016 | 0.666667 | 0.955244 | 0.470019 | 1.378126 | 0.333333 | 0.767857 |
| CT3 | trojan | G0 | 0 | 0.915344 | 0.916667 | 0.354952 | 0.169170 | 0.512087 | 0.944444 | 0.900794 |
| CT3 | trojan | G0 | 1 | 0.915344 | 0.916667 | 0.347338 | 0.168203 | 0.501102 | 0.888889 | 0.928571 |
| CT3 | trojan | G0 | 2 | 0.818519 | 0.833333 | 0.383379 | 0.218802 | 0.553098 | 0.833333 | 0.811111 |
| CT3 | trojan | G0 | 3 | 0.750397 | 0.750000 | 0.586134 | 0.334369 | 0.845613 | 0.828571 | 0.711310 |
| CT3 | trojan | G0 | 4 | 0.832672 | 0.833333 | 0.443983 | 0.270609 | 0.640531 | 0.928571 | 0.784722 |
| CT3 | trojan | G1 | 0 | 0.874339 | 0.875000 | 0.281325 | 0.166260 | 0.405866 | 0.803571 | 0.909722 |
| CT3 | trojan | G1 | 1 | 0.827778 | 0.833333 | 0.530641 | 0.213250 | 0.765552 | 0.708333 | 0.887500 |
| CT3 | trojan | G1 | 2 | 0.830688 | 0.833333 | 0.364133 | 0.229954 | 0.525333 | 0.944444 | 0.773810 |
| CT3 | trojan | G1 | 3 | 0.828042 | 0.833333 | 0.503945 | 0.275993 | 0.727039 | 0.761905 | 0.861111 |
| CT3 | trojan | G1 | 4 | 0.828042 | 0.833333 | 0.486352 | 0.287113 | 0.701657 | 0.833333 | 0.825397 |
| CT3 | trojan | G2 | 0 | 0.870370 | 0.875000 | 0.397150 | 0.184412 | 0.572966 | 0.833333 | 0.888889 |
| CT3 | trojan | G2 | 1 | 0.874339 | 0.875000 | 0.297783 | 0.183965 | 0.429610 | 0.875000 | 0.874008 |
| CT3 | trojan | G2 | 2 | 0.784127 | 0.791667 | 0.440162 | 0.290358 | 0.635020 | 0.619048 | 0.866667 |
| CT3 | trojan | G2 | 3 | 0.785053 | 0.791667 | 0.450719 | 0.264725 | 0.650250 | 0.660714 | 0.847222 |
| CT3 | trojan | G2 | 4 | 0.726852 | 0.750000 | 0.437631 | 0.279571 | 0.631368 | 0.541667 | 0.819444 |
| CT3 | vless | G0 | 0 | 0.750361 | 0.750000 | 0.986226 | 0.400745 | 1.422824 | 0.761905 | 0.744589 |
| CT3 | vless | G0 | 1 | 0.645238 | 0.666667 | 0.635931 | 0.375407 | 0.917454 | 0.660714 | 0.637500 |
| CT3 | vless | G0 | 2 | 0.802381 | 0.791667 | 0.781746 | 0.341847 | 1.127821 | 0.803571 | 0.801786 |
| CT3 | vless | G0 | 3 | 0.873677 | 0.875000 | 0.355067 | 0.162747 | 0.512253 | 0.873016 | 0.874008 |
| CT3 | vless | G0 | 4 | 0.877381 | 0.875000 | 0.734318 | 0.269130 | 1.059398 | 0.803571 | 0.914286 |
| CT3 | vless | G1 | 0 | 0.716270 | 0.708333 | 1.152686 | 0.428374 | 1.662974 | 0.583333 | 0.782738 |
| CT3 | vless | G1 | 1 | 0.745370 | 0.750000 | 0.696304 | 0.383990 | 1.004554 | 0.708333 | 0.763889 |
| CT3 | vless | G1 | 2 | 0.794974 | 0.791667 | 0.974315 | 0.361083 | 1.405639 | 0.761905 | 0.811508 |
| CT3 | vless | G1 | 3 | 0.832672 | 0.833333 | 0.464395 | 0.190488 | 0.669980 | 0.803571 | 0.847222 |
| CT3 | vless | G1 | 4 | 0.836640 | 0.833333 | 0.979740 | 0.243763 | 1.413466 | 0.857143 | 0.826389 |
| CT3 | vless | G2 | 0 | 0.754149 | 0.750000 | 1.008201 | 0.453544 | 1.454527 | 0.761905 | 0.750271 |
| CT3 | vless | G2 | 1 | 0.794974 | 0.791667 | 0.836334 | 0.356475 | 1.206576 | 0.819444 | 0.782738 |
| CT3 | vless | G2 | 2 | 0.646164 | 0.666667 | 1.165391 | 0.535711 | 1.681304 | 0.533333 | 0.702579 |
| CT3 | vless | G2 | 3 | 0.821164 | 0.833333 | 0.505340 | 0.226434 | 0.729051 | 0.833333 | 0.815079 |
| CT3 | vless | G2 | 4 | 0.794974 | 0.791667 | 1.125656 | 0.386642 | 1.623978 | 0.803571 | 0.790675 |
| CT3 | vmess | G0 | 0 | 0.868386 | 0.875000 | 0.500967 | 0.247601 | 0.722743 | 1.000000 | 0.802579 |
| CT3 | vmess | G0 | 1 | 0.772487 | 0.791667 | 0.670365 | 0.295858 | 0.967133 | 0.873016 | 0.722222 |
| CT3 | vmess | G0 | 2 | 0.704762 | 0.708333 | 1.046329 | 0.418905 | 1.509534 | 0.785714 | 0.664286 |
| CT3 | vmess | G0 | 3 | 0.773593 | 0.791667 | 1.038388 | 0.348068 | 1.498077 | 0.928571 | 0.696104 |
| CT3 | vmess | G0 | 4 | 0.792063 | 0.791667 | 0.664649 | 0.287748 | 0.958885 | 0.828571 | 0.773810 |
| CT3 | vmess | G1 | 0 | 0.828042 | 0.833333 | 0.751183 | 0.297490 | 1.083728 | 0.761905 | 0.861111 |
| CT3 | vmess | G1 | 1 | 0.670370 | 0.708333 | 0.965422 | 0.491512 | 1.392810 | 0.400000 | 0.805556 |
| CT3 | vmess | G1 | 2 | 0.641835 | 0.666667 | 1.780622 | 0.555150 | 2.568895 | 0.333333 | 0.796086 |
| CT3 | vmess | G1 | 3 | 0.694444 | 0.750000 | 0.985419 | 0.380665 | 1.421659 | 0.375000 | 0.854167 |
| CT3 | vmess | G1 | 4 | 0.589995 | 0.666667 | 1.054428 | 0.421699 | 1.521218 | 0.200000 | 0.784993 |
| CT3 | vmess | G2 | 0 | 0.683598 | 0.750000 | 0.682968 | 0.368164 | 0.985314 | 0.428571 | 0.811111 |
| CT3 | vmess | G2 | 1 | 0.655820 | 0.708333 | 0.868671 | 0.442418 | 1.253227 | 0.444444 | 0.761508 |
| CT3 | vmess | G2 | 2 | 0.661427 | 0.708333 | 2.634091 | 0.479160 | 3.800191 | 0.444444 | 0.769918 |
| CT3 | vmess | G2 | 3 | 0.730736 | 0.791667 | 1.292983 | 0.372219 | 1.865380 | 0.428571 | 0.881818 |
| CT3 | vmess | G2 | 4 | 0.689069 | 0.750000 | 1.250391 | 0.465210 | 1.803933 | 0.500000 | 0.783604 |
| CT4 | shadowsocks | G0 | 0 | 0.782540 | 0.791667 | 0.487115 | 0.261514 | 0.702758 | 0.685714 | 0.830952 |
| CT4 | shadowsocks | G0 | 1 | 0.836640 | 0.833333 | 0.552703 | 0.289102 | 0.797381 | 0.928571 | 0.790675 |
| CT4 | shadowsocks | G0 | 2 | 0.699735 | 0.708333 | 0.614791 | 0.301039 | 0.886956 | 0.660714 | 0.719246 |
| CT4 | shadowsocks | G0 | 3 | 0.789021 | 0.791667 | 0.849138 | 0.278763 | 1.225047 | 0.819444 | 0.773810 |
| CT4 | shadowsocks | G0 | 4 | 0.805820 | 0.833333 | 0.717114 | 0.284289 | 1.034578 | 0.700000 | 0.858730 |
| CT4 | shadowsocks | G1 | 0 | 0.735450 | 0.791667 | 0.999669 | 0.369225 | 1.442218 | 0.428571 | 0.888889 |
| CT4 | shadowsocks | G1 | 1 | 0.791005 | 0.791667 | 0.881870 | 0.369839 | 1.272269 | 0.666667 | 0.853175 |
| CT4 | shadowsocks | G1 | 2 | 0.666005 | 0.708333 | 0.901727 | 0.435141 | 1.300917 | 0.428571 | 0.784722 |
| CT4 | shadowsocks | G1 | 3 | 0.604762 | 0.666667 | 1.374974 | 0.453921 | 1.983668 | 0.200000 | 0.807143 |
| CT4 | shadowsocks | G1 | 4 | 0.735450 | 0.750000 | 1.283663 | 0.445717 | 1.851934 | 0.595238 | 0.805556 |
| CT4 | shadowsocks | G2 | 0 | 0.607407 | 0.666667 | 1.614735 | 0.512509 | 2.329570 | 0.333333 | 0.744444 |
| CT4 | shadowsocks | G2 | 1 | 0.781914 | 0.791667 | 0.674006 | 0.342085 | 0.972385 | 0.700000 | 0.822872 |
| CT4 | shadowsocks | G2 | 2 | 0.727561 | 0.750000 | 0.803589 | 0.415768 | 1.159333 | 0.485714 | 0.848485 |
| CT4 | shadowsocks | G2 | 3 | 0.727694 | 0.750000 | 0.976927 | 0.354476 | 1.409408 | 0.500000 | 0.841540 |
| CT4 | shadowsocks | G2 | 4 | 0.703755 | 0.708333 | 1.450443 | 0.495223 | 2.092548 | 0.500000 | 0.805632 |
| CT4 | trojan | G0 | 0 | 0.919048 | 0.916667 | 0.234721 | 0.143467 | 0.338631 | 1.000000 | 0.878571 |
| CT4 | trojan | G0 | 1 | 0.916005 | 0.916667 | 0.290720 | 0.166855 | 0.419420 | 0.875000 | 0.936508 |
| CT4 | trojan | G0 | 2 | 0.827116 | 0.833333 | 0.426065 | 0.256212 | 0.614681 | 0.733333 | 0.874008 |
| CT4 | trojan | G0 | 3 | 0.825397 | 0.833333 | 0.416402 | 0.236994 | 0.600742 | 0.888889 | 0.793651 |
| CT4 | trojan | G0 | 4 | 0.784392 | 0.791667 | 0.528886 | 0.271068 | 0.763022 | 0.873016 | 0.740079 |
| CT4 | trojan | G1 | 0 | 0.875180 | 0.875000 | 0.258235 | 0.172121 | 0.372555 | 0.761905 | 0.931818 |
| CT4 | trojan | G1 | 1 | 0.785895 | 0.791667 | 0.531537 | 0.277230 | 0.766846 | 0.619048 | 0.869318 |
| CT4 | trojan | G1 | 2 | 0.915344 | 0.916667 | 0.382055 | 0.178312 | 0.551189 | 0.944444 | 0.900794 |
| CT4 | trojan | G1 | 3 | 0.826058 | 0.833333 | 0.353363 | 0.207766 | 0.509796 | 0.803571 | 0.837302 |
| CT4 | trojan | G1 | 4 | 0.828042 | 0.833333 | 0.446413 | 0.271076 | 0.644037 | 0.833333 | 0.825397 |
| CT4 | trojan | G2 | 0 | 0.957672 | 0.958333 | 0.237374 | 0.131399 | 0.342458 | 0.944444 | 0.964286 |
| CT4 | trojan | G2 | 1 | 0.916005 | 0.916667 | 0.268591 | 0.156539 | 0.387496 | 0.944444 | 0.901786 |
| CT4 | trojan | G2 | 2 | 0.915344 | 0.916667 | 0.362364 | 0.153335 | 0.522780 | 0.928571 | 0.908730 |
| CT4 | trojan | G2 | 3 | 0.865079 | 0.875000 | 0.690076 | 0.241647 | 0.995569 | 0.777778 | 0.908730 |
| CT4 | trojan | G2 | 4 | 0.826720 | 0.833333 | 0.277796 | 0.180023 | 0.400775 | 0.785714 | 0.847222 |
| CT4 | vless | G0 | 0 | 0.830159 | 0.833333 | 0.889969 | 0.348509 | 1.283954 | 0.928571 | 0.780952 |
| CT4 | vless | G0 | 1 | 0.745370 | 0.750000 | 0.653679 | 0.331637 | 0.943059 | 0.750000 | 0.743056 |
| CT4 | vless | G0 | 2 | 0.715079 | 0.708333 | 0.792741 | 0.397215 | 1.143684 | 0.761905 | 0.691667 |
| CT4 | vless | G0 | 3 | 0.868783 | 0.875000 | 0.271792 | 0.141255 | 0.392113 | 0.833333 | 0.886508 |
| CT4 | vless | G0 | 4 | 0.874339 | 0.875000 | 0.571248 | 0.245378 | 0.824137 | 0.750000 | 0.936508 |
| CT4 | vless | G1 | 0 | 0.748413 | 0.750000 | 1.223490 | 0.409652 | 1.765123 | 0.650000 | 0.797619 |
| CT4 | vless | G1 | 1 | 0.689815 | 0.708333 | 1.252359 | 0.433604 | 1.806772 | 0.575000 | 0.747222 |
| CT4 | vless | G1 | 2 | 0.702778 | 0.708333 | 1.311255 | 0.449373 | 1.891740 | 0.708333 | 0.700000 |
| CT4 | vless | G1 | 3 | 0.818519 | 0.833333 | 0.546331 | 0.209291 | 0.788188 | 0.733333 | 0.861111 |
| CT4 | vless | G1 | 4 | 0.873677 | 0.875000 | 0.708570 | 0.171457 | 1.022250 | 0.857143 | 0.881944 |
| CT4 | vless | G2 | 0 | 0.790079 | 0.791667 | 0.666900 | 0.362069 | 0.962134 | 0.761905 | 0.804167 |
| CT4 | vless | G2 | 1 | 0.748016 | 0.750000 | 0.673639 | 0.304869 | 0.971855 | 0.785714 | 0.729167 |
| CT4 | vless | G2 | 2 | 0.710317 | 0.708333 | 1.272354 | 0.454718 | 1.835618 | 0.660714 | 0.735119 |
| CT4 | vless | G2 | 3 | 0.828042 | 0.833333 | 0.478131 | 0.243300 | 0.689797 | 0.777778 | 0.853175 |
| CT4 | vless | G2 | 4 | 0.794974 | 0.791667 | 0.662834 | 0.284684 | 0.956268 | 0.803571 | 0.790675 |
| CT4 | vmess | G0 | 0 | 0.868386 | 0.875000 | 0.622153 | 0.253218 | 0.897578 | 0.875000 | 0.865079 |
| CT4 | vmess | G0 | 1 | 0.738228 | 0.750000 | 0.874649 | 0.368334 | 1.261852 | 0.819444 | 0.697619 |
| CT4 | vmess | G0 | 2 | 0.788095 | 0.791667 | 1.290432 | 0.419562 | 1.861700 | 0.775000 | 0.794643 |
| CT4 | vmess | G0 | 3 | 0.794228 | 0.791667 | 1.900447 | 0.353195 | 2.741765 | 0.857143 | 0.762771 |
| CT4 | vmess | G0 | 4 | 0.757576 | 0.750000 | 0.712891 | 0.270253 | 1.028485 | 0.785714 | 0.743506 |
| CT4 | vmess | G1 | 0 | 0.868783 | 0.875000 | 0.878588 | 0.259010 | 1.267535 | 0.761905 | 0.922222 |
| CT4 | vmess | G1 | 1 | 0.590909 | 0.666667 | 1.428855 | 0.558943 | 2.061401 | 0.200000 | 0.786364 |
| CT4 | vmess | G1 | 2 | 0.676094 | 0.708333 | 1.045530 | 0.404828 | 1.508382 | 0.366667 | 0.830808 |
| CT4 | vmess | G1 | 3 | 0.778307 | 0.791667 | 1.593623 | 0.324336 | 2.299112 | 0.628571 | 0.853175 |
| CT4 | vmess | G1 | 4 | 0.795815 | 0.791667 | 0.830298 | 0.340117 | 1.197867 | 0.761905 | 0.812771 |
| CT4 | vmess | G2 | 0 | 0.624339 | 0.666667 | 0.982631 | 0.473028 | 1.417636 | 0.428571 | 0.722222 |
| CT4 | vmess | G2 | 1 | 0.787037 | 0.791667 | 0.854131 | 0.307734 | 1.232251 | 0.833333 | 0.763889 |
| CT4 | vmess | G2 | 2 | 0.657407 | 0.708333 | 2.085934 | 0.514839 | 3.009367 | 0.500000 | 0.736111 |
| CT4 | vmess | G2 | 3 | 0.708514 | 0.750000 | 1.847851 | 0.370327 | 2.665885 | 0.428571 | 0.848485 |
| CT4 | vmess | G2 | 4 | 0.689069 | 0.750000 | 0.997878 | 0.335090 | 1.439634 | 0.500000 | 0.783604 |
| CT5 | shadowsocks | G0 | 0 | 0.916005 | 0.916667 | 0.222803 | 0.115897 | 0.321437 | 1.000000 | 0.874008 |
| CT5 | shadowsocks | G0 | 1 | 0.671347 | 0.708333 | 0.715611 | 0.368934 | 1.032408 | 0.928571 | 0.542735 |
| CT5 | shadowsocks | G0 | 2 | 0.814815 | 0.833333 | 0.939056 | 0.317160 | 1.354771 | 0.944444 | 0.750000 |
| CT5 | shadowsocks | G0 | 3 | 0.878968 | 0.875000 | 0.557404 | 0.180192 | 0.804164 | 1.000000 | 0.818452 |
| CT5 | shadowsocks | G0 | 4 | 0.916005 | 0.916667 | 0.483774 | 0.148619 | 0.697939 | 0.928571 | 0.909722 |
| CT5 | shadowsocks | G1 | 0 | 0.916005 | 0.916667 | 0.222803 | 0.115897 | 0.321437 | 0.873016 | 0.937500 |
| CT5 | shadowsocks | G1 | 1 | 0.671347 | 0.708333 | 0.715611 | 0.368934 | 1.032408 | 0.333333 | 0.840354 |
| CT5 | shadowsocks | G1 | 2 | 0.814815 | 0.833333 | 0.939056 | 0.317160 | 1.354771 | 0.833333 | 0.805556 |
| CT5 | shadowsocks | G1 | 3 | 0.878968 | 0.875000 | 0.557404 | 0.180192 | 0.804164 | 0.803571 | 0.916667 |
| CT5 | shadowsocks | G1 | 4 | 0.916005 | 0.916667 | 0.483774 | 0.148619 | 0.697939 | 0.875000 | 0.936508 |
| CT5 | shadowsocks | G2 | 0 | 0.916005 | 0.916667 | 0.222803 | 0.115897 | 0.321437 | 0.875000 | 0.936508 |
| CT5 | shadowsocks | G2 | 1 | 0.671347 | 0.708333 | 0.715611 | 0.368934 | 1.032408 | 0.752137 | 0.630952 |
| CT5 | shadowsocks | G2 | 2 | 0.814815 | 0.833333 | 0.939056 | 0.317160 | 1.354771 | 0.666667 | 0.888889 |
| CT5 | shadowsocks | G2 | 3 | 0.878968 | 0.875000 | 0.557404 | 0.180192 | 0.804164 | 0.833333 | 0.901786 |
| CT5 | shadowsocks | G2 | 4 | 0.916005 | 0.916667 | 0.483774 | 0.148619 | 0.697939 | 0.944444 | 0.901786 |
| CT5 | trojan | G0 | 0 | 0.833333 | 0.833333 | 1.107612 | 0.264289 | 1.597947 | 1.000000 | 0.750000 |
| CT5 | trojan | G0 | 1 | 0.835714 | 0.833333 | 0.555585 | 0.278078 | 0.801539 | 0.900000 | 0.803571 |
| CT5 | trojan | G0 | 2 | 0.865079 | 0.875000 | 0.284839 | 0.151902 | 0.410936 | 0.944444 | 0.825397 |
| CT5 | trojan | G0 | 3 | 0.794974 | 0.791667 | 0.722100 | 0.332524 | 1.041770 | 0.803571 | 0.790675 |
| CT5 | trojan | G0 | 4 | 0.832672 | 0.833333 | 0.646669 | 0.287530 | 0.932946 | 0.928571 | 0.784722 |
| CT5 | trojan | G1 | 0 | 0.833333 | 0.833333 | 1.107612 | 0.264289 | 1.597947 | 0.750000 | 0.875000 |
| CT5 | trojan | G1 | 1 | 0.835714 | 0.833333 | 0.555585 | 0.278078 | 0.801539 | 0.803571 | 0.851786 |
| CT5 | trojan | G1 | 2 | 0.865079 | 0.875000 | 0.284839 | 0.151902 | 0.410936 | 0.888889 | 0.853175 |
| CT5 | trojan | G1 | 3 | 0.794974 | 0.791667 | 0.722100 | 0.332524 | 1.041770 | 0.803571 | 0.790675 |
| CT5 | trojan | G1 | 4 | 0.832672 | 0.833333 | 0.646669 | 0.287530 | 0.932946 | 0.819444 | 0.839286 |
| CT5 | trojan | G2 | 0 | 0.833333 | 0.833333 | 1.107612 | 0.264289 | 1.597947 | 0.750000 | 0.875000 |
| CT5 | trojan | G2 | 1 | 0.835714 | 0.833333 | 0.555585 | 0.278078 | 0.801539 | 0.803571 | 0.851786 |
| CT5 | trojan | G2 | 2 | 0.865079 | 0.875000 | 0.284839 | 0.151902 | 0.410936 | 0.761905 | 0.916667 |
| CT5 | trojan | G2 | 3 | 0.794974 | 0.791667 | 0.722100 | 0.332524 | 1.041770 | 0.777778 | 0.803571 |
| CT5 | trojan | G2 | 4 | 0.832672 | 0.833333 | 0.646669 | 0.287530 | 0.932946 | 0.750000 | 0.874008 |
| CT5 | vless | G0 | 0 | 0.802381 | 0.791667 | 1.038591 | 0.381911 | 1.498370 | 0.928571 | 0.739286 |
| CT5 | vless | G0 | 1 | 0.874339 | 0.875000 | 0.668815 | 0.269078 | 0.964897 | 0.803571 | 0.909722 |
| CT5 | vless | G0 | 2 | 0.695948 | 0.708333 | 0.677568 | 0.379290 | 0.977524 | 0.708333 | 0.689755 |
| CT5 | vless | G0 | 3 | 0.870370 | 0.875000 | 0.576925 | 0.223074 | 0.832327 | 0.833333 | 0.888889 |
| CT5 | vless | G0 | 4 | 0.728704 | 0.750000 | 0.788800 | 0.325914 | 1.137999 | 0.819444 | 0.683333 |
| CT5 | vless | G1 | 0 | 0.802381 | 0.791667 | 1.038591 | 0.381911 | 1.498370 | 0.675000 | 0.866071 |
| CT5 | vless | G1 | 1 | 0.874339 | 0.875000 | 0.668815 | 0.269078 | 0.964897 | 0.875000 | 0.874008 |
| CT5 | vless | G1 | 2 | 0.695948 | 0.708333 | 0.677568 | 0.379290 | 0.977524 | 0.730159 | 0.678842 |
| CT5 | vless | G1 | 3 | 0.870370 | 0.875000 | 0.576925 | 0.223074 | 0.832327 | 0.833333 | 0.888889 |
| CT5 | vless | G1 | 4 | 0.728704 | 0.750000 | 0.788800 | 0.325914 | 1.137999 | 0.666667 | 0.759722 |
| CT5 | vless | G2 | 0 | 0.802381 | 0.791667 | 1.038591 | 0.381911 | 1.498370 | 0.803571 | 0.801786 |
| CT5 | vless | G2 | 1 | 0.874339 | 0.875000 | 0.668815 | 0.269078 | 0.964897 | 0.944444 | 0.839286 |
| CT5 | vless | G2 | 2 | 0.695948 | 0.708333 | 0.677568 | 0.379290 | 0.977524 | 0.649351 | 0.719246 |
| CT5 | vless | G2 | 3 | 0.870370 | 0.875000 | 0.576925 | 0.223074 | 0.832327 | 0.944444 | 0.833333 |
| CT5 | vless | G2 | 4 | 0.728704 | 0.750000 | 0.788800 | 0.325914 | 1.137999 | 0.700000 | 0.743056 |
| CT5 | vmess | G0 | 0 | 0.733862 | 0.750000 | 1.215703 | 0.448409 | 1.753888 | 0.828571 | 0.686508 |
| CT5 | vmess | G0 | 1 | 0.782540 | 0.791667 | 0.993641 | 0.342379 | 1.433520 | 0.733333 | 0.807143 |
| CT5 | vmess | G0 | 2 | 0.705556 | 0.708333 | 1.106975 | 0.452079 | 1.597027 | 0.708333 | 0.704167 |
| CT5 | vmess | G0 | 3 | 0.813228 | 0.833333 | 0.850107 | 0.318380 | 1.226445 | 1.000000 | 0.719841 |
| CT5 | vmess | G0 | 4 | 0.752381 | 0.750000 | 1.071460 | 0.411201 | 1.545791 | 0.828571 | 0.714286 |
| CT5 | vmess | G1 | 0 | 0.733862 | 0.750000 | 1.215703 | 0.448409 | 1.753888 | 0.611111 | 0.795238 |
| CT5 | vmess | G1 | 1 | 0.782540 | 0.791667 | 0.993641 | 0.342379 | 1.433520 | 0.685714 | 0.830952 |
| CT5 | vmess | G1 | 2 | 0.705556 | 0.708333 | 1.106975 | 0.452079 | 1.597027 | 0.675000 | 0.720833 |
| CT5 | vmess | G1 | 3 | 0.813228 | 0.833333 | 0.850107 | 0.318380 | 1.226445 | 0.844444 | 0.797619 |
| CT5 | vmess | G1 | 4 | 0.752381 | 0.750000 | 1.071460 | 0.411201 | 1.545791 | 0.678571 | 0.789286 |
| CT5 | vmess | G2 | 0 | 0.733862 | 0.750000 | 1.215703 | 0.448409 | 1.753888 | 0.761905 | 0.719841 |
| CT5 | vmess | G2 | 1 | 0.782540 | 0.791667 | 0.993641 | 0.342379 | 1.433520 | 0.928571 | 0.709524 |
| CT5 | vmess | G2 | 2 | 0.705556 | 0.708333 | 1.106975 | 0.452079 | 1.597027 | 0.733333 | 0.691667 |
| CT5 | vmess | G2 | 3 | 0.813228 | 0.833333 | 0.850107 | 0.318380 | 1.226445 | 0.595238 | 0.922222 |
| CT5 | vmess | G2 | 4 | 0.752381 | 0.750000 | 1.071460 | 0.411201 | 1.545791 | 0.750000 | 0.753571 |
| JA0 | shadowsocks | G0 | 0 | 0.876720 | 0.875000 | 0.603931 | 0.219830 | 0.871288 | 0.928571 | 0.850794 |
| JA0 | shadowsocks | G0 | 1 | 0.676638 | 0.666667 | 0.959264 | 0.416431 | 1.383925 | 0.666667 | 0.681624 |
| JA0 | shadowsocks | G0 | 2 | 0.699735 | 0.708333 | 0.733591 | 0.368295 | 1.058348 | 0.660714 | 0.719246 |
| JA0 | shadowsocks | G0 | 3 | 0.836640 | 0.833333 | 0.701715 | 0.246394 | 1.012361 | 0.873016 | 0.818452 |
| JA0 | shadowsocks | G0 | 4 | 0.769889 | 0.791667 | 0.731780 | 0.338607 | 1.055735 | 0.628571 | 0.840548 |
| JA0 | shadowsocks | G1 | 0 | 0.822222 | 0.833333 | 1.416338 | 0.351211 | 2.043343 | 0.666667 | 0.900000 |
| JA0 | shadowsocks | G1 | 1 | 0.778836 | 0.791667 | 0.804396 | 0.380070 | 1.160498 | 0.619048 | 0.858730 |
| JA0 | shadowsocks | G1 | 2 | 0.649110 | 0.666667 | 1.186959 | 0.524475 | 1.712421 | 0.452381 | 0.747475 |
| JA0 | shadowsocks | G1 | 3 | 0.628704 | 0.666667 | 0.933942 | 0.452289 | 1.347393 | 0.366667 | 0.759722 |
| JA0 | shadowsocks | G1 | 4 | 0.832852 | 0.833333 | 0.850634 | 0.321708 | 1.227206 | 0.761905 | 0.868326 |
| JA0 | shadowsocks | G2 | 0 | 0.548148 | 0.625000 | 1.982936 | 0.596072 | 2.860772 | 0.200000 | 0.722222 |
| JA0 | shadowsocks | G2 | 1 | 0.655063 | 0.708333 | 1.447446 | 0.433015 | 2.088223 | 0.444444 | 0.760372 |
| JA0 | shadowsocks | G2 | 2 | 0.680471 | 0.750000 | 0.946621 | 0.352906 | 1.365686 | 0.333333 | 0.854040 |
| JA0 | shadowsocks | G2 | 3 | 0.570370 | 0.625000 | 2.087454 | 0.662015 | 3.011560 | 0.333333 | 0.688889 |
| JA0 | shadowsocks | G2 | 4 | 0.526587 | 0.583333 | 1.553985 | 0.636990 | 2.241926 | 0.142857 | 0.718452 |
| JA0 | trojan | G0 | 0 | 0.826058 | 0.833333 | 0.494148 | 0.256053 | 0.712905 | 0.873016 | 0.802579 |
| JA0 | trojan | G0 | 1 | 0.789683 | 0.791667 | 0.422509 | 0.254765 | 0.609552 | 0.875000 | 0.747024 |
| JA0 | trojan | G0 | 2 | 0.755556 | 0.791667 | 0.503003 | 0.293235 | 0.725679 | 0.644444 | 0.811111 |
| JA0 | trojan | G0 | 3 | 0.745551 | 0.750000 | 0.725926 | 0.383375 | 1.047290 | 0.730159 | 0.753247 |
| JA0 | trojan | G0 | 4 | 0.832672 | 0.833333 | 0.442341 | 0.237814 | 0.638163 | 0.928571 | 0.784722 |
| JA0 | trojan | G1 | 0 | 0.868783 | 0.875000 | 0.326181 | 0.196673 | 0.470579 | 0.761905 | 0.922222 |
| JA0 | trojan | G1 | 1 | 0.730820 | 0.750000 | 0.617202 | 0.303667 | 0.890435 | 0.428571 | 0.881944 |
| JA0 | trojan | G1 | 2 | 0.777778 | 0.791667 | 0.521278 | 0.277814 | 0.752045 | 0.888889 | 0.722222 |
| JA0 | trojan | G1 | 3 | 0.828042 | 0.833333 | 0.547229 | 0.287905 | 0.789484 | 0.761905 | 0.861111 |
| JA0 | trojan | G1 | 4 | 0.785233 | 0.791667 | 0.454508 | 0.285043 | 0.655716 | 0.619048 | 0.868326 |
| JA0 | trojan | G2 | 0 | 0.827116 | 0.833333 | 0.828605 | 0.320237 | 1.195424 | 0.761905 | 0.859722 |
| JA0 | trojan | G2 | 1 | 0.826058 | 0.833333 | 0.414105 | 0.251438 | 0.597427 | 0.819444 | 0.829365 |
| JA0 | trojan | G2 | 2 | 0.727694 | 0.750000 | 0.533311 | 0.256678 | 0.769406 | 0.500000 | 0.841540 |
| JA0 | trojan | G2 | 3 | 0.826058 | 0.833333 | 0.812515 | 0.326979 | 1.172211 | 0.785714 | 0.846230 |
| JA0 | trojan | G2 | 4 | 0.823413 | 0.833333 | 0.314842 | 0.177152 | 0.454221 | 0.761905 | 0.854167 |
| JA0 | vless | G0 | 0 | 0.749206 | 0.750000 | 0.818880 | 0.390126 | 1.181395 | 0.785714 | 0.730952 |
| JA0 | vless | G0 | 1 | 0.765079 | 0.791667 | 0.631936 | 0.260930 | 0.911691 | 0.873016 | 0.711111 |
| JA0 | vless | G0 | 2 | 0.756085 | 0.750000 | 1.042943 | 0.442620 | 1.504649 | 0.761905 | 0.753175 |
| JA0 | vless | G0 | 3 | 0.915344 | 0.916667 | 0.241721 | 0.114256 | 0.348729 | 0.928571 | 0.908730 |
| JA0 | vless | G0 | 4 | 0.792063 | 0.791667 | 0.868842 | 0.345285 | 1.253475 | 0.785714 | 0.795238 |
| JA0 | vless | G1 | 0 | 0.748016 | 0.750000 | 0.926419 | 0.332053 | 1.336541 | 0.625000 | 0.809524 |
| JA0 | vless | G1 | 1 | 0.688228 | 0.708333 | 1.139067 | 0.367226 | 1.643326 | 0.541667 | 0.761508 |
| JA0 | vless | G1 | 2 | 0.749339 | 0.750000 | 0.790576 | 0.420213 | 1.140560 | 0.761905 | 0.743056 |
| JA0 | vless | G1 | 3 | 0.907407 | 0.916667 | 0.420299 | 0.138569 | 0.606363 | 0.777778 | 0.972222 |
| JA0 | vless | G1 | 4 | 0.823413 | 0.833333 | 0.639481 | 0.248863 | 0.922575 | 0.761905 | 0.854167 |
| JA0 | vless | G2 | 0 | 0.749206 | 0.750000 | 0.645936 | 0.336336 | 0.931889 | 0.761905 | 0.742857 |
| JA0 | vless | G2 | 1 | 0.832011 | 0.833333 | 0.670822 | 0.223239 | 0.967791 | 0.819444 | 0.838294 |
| JA0 | vless | G2 | 2 | 0.646825 | 0.625000 | 1.169863 | 0.551136 | 1.687755 | 0.500000 | 0.720238 |
| JA0 | vless | G2 | 3 | 0.824074 | 0.833333 | 0.371175 | 0.199324 | 0.535493 | 0.777778 | 0.847222 |
| JA0 | vless | G2 | 4 | 0.752116 | 0.750000 | 0.738570 | 0.326161 | 1.065531 | 0.708333 | 0.774008 |
| JA0 | vmess | G0 | 0 | 0.835714 | 0.833333 | 0.750448 | 0.243630 | 1.082668 | 0.857143 | 0.825000 |
| JA0 | vmess | G0 | 1 | 0.739586 | 0.750000 | 1.172654 | 0.435703 | 1.691783 | 0.857143 | 0.680808 |
| JA0 | vmess | G0 | 2 | 0.752646 | 0.750000 | 0.912376 | 0.420311 | 1.316280 | 0.785714 | 0.736111 |
| JA0 | vmess | G0 | 3 | 0.785233 | 0.791667 | 1.026156 | 0.342734 | 1.480431 | 0.833333 | 0.761183 |
| JA0 | vmess | G0 | 4 | 0.835714 | 0.833333 | 0.616696 | 0.281171 | 0.889705 | 0.828571 | 0.839286 |
| JA0 | vmess | G1 | 0 | 0.868783 | 0.875000 | 0.580395 | 0.217297 | 0.837333 | 0.761905 | 0.922222 |
| JA0 | vmess | G1 | 1 | 0.587963 | 0.625000 | 1.452528 | 0.546634 | 2.095555 | 0.366667 | 0.698611 |
| JA0 | vmess | G1 | 2 | 0.594613 | 0.666667 | 1.061516 | 0.547239 | 1.531443 | 0.166667 | 0.808586 |
| JA0 | vmess | G1 | 3 | 0.703755 | 0.750000 | 1.528941 | 0.446967 | 2.205796 | 0.428571 | 0.841346 |
| JA0 | vmess | G1 | 4 | 0.723329 | 0.750000 | 0.830486 | 0.330228 | 1.198138 | 0.533333 | 0.818326 |
| JA0 | vmess | G2 | 0 | 0.776190 | 0.791667 | 0.582218 | 0.276258 | 0.839963 | 0.628571 | 0.850000 |
| JA0 | vmess | G2 | 1 | 0.687302 | 0.750000 | 1.938581 | 0.507208 | 2.796781 | 0.500000 | 0.780952 |
| JA0 | vmess | G2 | 2 | 0.730736 | 0.791667 | 1.021667 | 0.382531 | 1.473954 | 0.500000 | 0.846104 |
| JA0 | vmess | G2 | 3 | 0.698413 | 0.750000 | 1.480660 | 0.428899 | 2.136141 | 0.428571 | 0.833333 |
| JA0 | vmess | G2 | 4 | 0.689069 | 0.750000 | 0.890765 | 0.400943 | 1.285102 | 0.500000 | 0.783604 |
| JA1 | shadowsocks | G0 | 0 | 0.877381 | 0.875000 | 0.708955 | 0.223636 | 1.022806 | 0.928571 | 0.851786 |
| JA1 | shadowsocks | G0 | 1 | 0.716931 | 0.708333 | 0.801232 | 0.371832 | 1.155933 | 0.761905 | 0.694444 |
| JA1 | shadowsocks | G0 | 2 | 0.750397 | 0.750000 | 0.761874 | 0.379628 | 1.099152 | 0.803571 | 0.723810 |
| JA1 | shadowsocks | G0 | 3 | 0.835714 | 0.833333 | 0.971151 | 0.318718 | 1.401074 | 0.828571 | 0.839286 |
| JA1 | shadowsocks | G0 | 4 | 0.769889 | 0.791667 | 0.678118 | 0.337416 | 0.978318 | 0.628571 | 0.840548 |
| JA1 | shadowsocks | G1 | 0 | 0.765657 | 0.791667 | 1.199870 | 0.351481 | 1.731046 | 0.533333 | 0.881818 |
| JA1 | shadowsocks | G1 | 1 | 0.689153 | 0.708333 | 0.952648 | 0.469229 | 1.374381 | 0.450000 | 0.808730 |
| JA1 | shadowsocks | G1 | 2 | 0.665344 | 0.708333 | 1.461737 | 0.574765 | 2.108840 | 0.428571 | 0.783730 |
| JA1 | shadowsocks | G1 | 3 | 0.625000 | 0.666667 | 1.518598 | 0.544998 | 2.190874 | 0.400000 | 0.737500 |
| JA1 | shadowsocks | G1 | 4 | 0.791005 | 0.791667 | 0.982683 | 0.361805 | 1.417712 | 0.666667 | 0.853175 |
| JA1 | shadowsocks | G2 | 0 | 0.472391 | 0.583333 | 1.357747 | 0.567685 | 1.958815 | 0.000000 | 0.708586 |
| JA1 | shadowsocks | G2 | 1 | 0.659692 | 0.708333 | 1.136304 | 0.447000 | 1.639341 | 0.500000 | 0.739538 |
| JA1 | shadowsocks | G2 | 2 | 0.686869 | 0.750000 | 0.975783 | 0.362346 | 1.407757 | 0.333333 | 0.863636 |
| JA1 | shadowsocks | G2 | 3 | 0.684259 | 0.708333 | 1.142930 | 0.500735 | 1.648900 | 0.500000 | 0.776389 |
| JA1 | shadowsocks | G2 | 4 | 0.609127 | 0.666667 | 1.157046 | 0.571806 | 1.669264 | 0.285714 | 0.770833 |
| JA1 | trojan | G0 | 0 | 0.835053 | 0.833333 | 0.416107 | 0.216161 | 0.600316 | 0.873016 | 0.816071 |
| JA1 | trojan | G0 | 1 | 0.789683 | 0.791667 | 0.440600 | 0.233645 | 0.635652 | 0.875000 | 0.747024 |
| JA1 | trojan | G0 | 2 | 0.814815 | 0.833333 | 0.353456 | 0.201015 | 0.509929 | 0.777778 | 0.833333 |
| JA1 | trojan | G0 | 3 | 0.746609 | 0.750000 | 0.707103 | 0.391479 | 1.020134 | 0.733333 | 0.753247 |
| JA1 | trojan | G0 | 4 | 0.873677 | 0.875000 | 0.444561 | 0.245056 | 0.641366 | 0.928571 | 0.846230 |
| JA1 | trojan | G1 | 0 | 0.878968 | 0.875000 | 0.421496 | 0.235739 | 0.608091 | 0.833333 | 0.901786 |
| JA1 | trojan | G1 | 1 | 0.759259 | 0.791667 | 0.665843 | 0.302120 | 0.960608 | 0.533333 | 0.872222 |
| JA1 | trojan | G1 | 2 | 0.826058 | 0.833333 | 0.500326 | 0.253341 | 0.721818 | 0.888889 | 0.794643 |
| JA1 | trojan | G1 | 3 | 0.781746 | 0.791667 | 0.656174 | 0.313693 | 0.946660 | 0.761905 | 0.791667 |
| JA1 | trojan | G1 | 4 | 0.745503 | 0.750000 | 0.444576 | 0.277891 | 0.641388 | 0.619048 | 0.808730 |
| JA1 | trojan | G2 | 0 | 0.827116 | 0.833333 | 0.573218 | 0.233564 | 0.826979 | 0.761905 | 0.859722 |
| JA1 | trojan | G2 | 1 | 0.828704 | 0.833333 | 0.380902 | 0.246874 | 0.549525 | 0.875000 | 0.805556 |
| JA1 | trojan | G2 | 2 | 0.724916 | 0.750000 | 0.573211 | 0.232143 | 0.826969 | 0.533333 | 0.820707 |
| JA1 | trojan | G2 | 3 | 0.738757 | 0.750000 | 0.632994 | 0.309551 | 0.913218 | 0.619048 | 0.798611 |
| JA1 | trojan | G2 | 4 | 0.787037 | 0.791667 | 0.327913 | 0.189467 | 0.473079 | 0.750000 | 0.805556 |
| JA1 | vless | G0 | 0 | 0.836640 | 0.833333 | 0.646890 | 0.331076 | 0.933265 | 0.875000 | 0.817460 |
| JA1 | vless | G0 | 1 | 0.823413 | 0.833333 | 0.653840 | 0.231367 | 0.943291 | 0.873016 | 0.798611 |
| JA1 | vless | G0 | 2 | 0.756085 | 0.750000 | 1.150745 | 0.469540 | 1.660173 | 0.761905 | 0.753175 |
| JA1 | vless | G0 | 3 | 0.957672 | 0.958333 | 0.246315 | 0.101514 | 0.355357 | 1.000000 | 0.936508 |
| JA1 | vless | G0 | 4 | 0.826058 | 0.833333 | 1.068344 | 0.300668 | 1.541295 | 0.730159 | 0.874008 |
| JA1 | vless | G1 | 0 | 0.782143 | 0.791667 | 0.668455 | 0.263451 | 0.964377 | 0.660714 | 0.842857 |
| JA1 | vless | G1 | 1 | 0.805820 | 0.833333 | 0.941959 | 0.322375 | 1.358959 | 0.700000 | 0.858730 |
| JA1 | vless | G1 | 2 | 0.751323 | 0.750000 | 0.906603 | 0.423920 | 1.307952 | 0.714286 | 0.769841 |
| JA1 | vless | G1 | 3 | 0.911111 | 0.916667 | 0.474096 | 0.135762 | 0.683975 | 0.733333 | 1.000000 |
| JA1 | vless | G1 | 4 | 0.805820 | 0.833333 | 0.576594 | 0.226141 | 0.831850 | 0.628571 | 0.894444 |
| JA1 | vless | G2 | 0 | 0.831746 | 0.833333 | 0.508377 | 0.264618 | 0.733433 | 0.833333 | 0.830952 |
| JA1 | vless | G2 | 1 | 0.826455 | 0.833333 | 0.774558 | 0.220833 | 1.117451 | 0.888889 | 0.795238 |
| JA1 | vless | G2 | 2 | 0.756085 | 0.750000 | 1.409011 | 0.522241 | 2.032773 | 0.744444 | 0.761905 |
| JA1 | vless | G2 | 3 | 0.916005 | 0.916667 | 0.327979 | 0.146969 | 0.473173 | 0.873016 | 0.937500 |
| JA1 | vless | G2 | 4 | 0.798016 | 0.791667 | 0.627882 | 0.289575 | 0.905842 | 0.857143 | 0.768452 |
| JA1 | vmess | G0 | 0 | 0.832672 | 0.833333 | 0.700265 | 0.239990 | 1.010269 | 0.803571 | 0.847222 |
| JA1 | vmess | G0 | 1 | 0.746612 | 0.750000 | 0.650176 | 0.338939 | 0.938006 | 0.803571 | 0.718132 |
| JA1 | vmess | G0 | 2 | 0.673148 | 0.666667 | 0.700430 | 0.413445 | 1.010507 | 0.803571 | 0.607937 |
| JA1 | vmess | G0 | 3 | 0.773593 | 0.791667 | 0.829967 | 0.323614 | 1.197390 | 0.928571 | 0.696104 |
| JA1 | vmess | G0 | 4 | 0.835714 | 0.833333 | 0.682526 | 0.253508 | 0.984676 | 0.828571 | 0.839286 |
| JA1 | vmess | G1 | 0 | 0.868783 | 0.875000 | 0.830192 | 0.267998 | 1.197714 | 0.761905 | 0.922222 |
| JA1 | vmess | G1 | 1 | 0.446212 | 0.541667 | 1.696028 | 0.676361 | 2.446851 | 0.000000 | 0.669318 |
| JA1 | vmess | G1 | 2 | 0.650168 | 0.708333 | 0.996696 | 0.511139 | 1.437929 | 0.333333 | 0.808586 |
| JA1 | vmess | G1 | 3 | 0.771212 | 0.791667 | 0.703172 | 0.292158 | 1.014463 | 0.575000 | 0.869318 |
| JA1 | vmess | G1 | 4 | 0.668783 | 0.708333 | 1.406911 | 0.486265 | 2.029744 | 0.400000 | 0.803175 |
| JA1 | vmess | G2 | 0 | 0.776190 | 0.791667 | 0.531293 | 0.302039 | 0.766494 | 0.628571 | 0.850000 |
| JA1 | vmess | G2 | 1 | 0.643519 | 0.708333 | 1.124812 | 0.439141 | 1.622761 | 0.444444 | 0.743056 |
| JA1 | vmess | G2 | 2 | 0.812217 | 0.833333 | 0.941807 | 0.328235 | 1.358740 | 0.700000 | 0.868326 |
| JA1 | vmess | G2 | 3 | 0.730736 | 0.791667 | 1.325322 | 0.395447 | 1.912035 | 0.428571 | 0.881818 |
| JA1 | vmess | G2 | 4 | 0.689069 | 0.750000 | 1.041399 | 0.372067 | 1.502421 | 0.500000 | 0.783604 |
| JA2 | shadowsocks | G0 | 0 | 0.876720 | 0.875000 | 0.624393 | 0.219041 | 0.900808 | 0.928571 | 0.850794 |
| JA2 | shadowsocks | G0 | 1 | 0.758778 | 0.750000 | 0.855824 | 0.373618 | 1.234693 | 0.857143 | 0.709596 |
| JA2 | shadowsocks | G0 | 2 | 0.691847 | 0.708333 | 1.524775 | 0.460535 | 2.199785 | 0.575000 | 0.750271 |
| JA2 | shadowsocks | G0 | 3 | 0.836640 | 0.833333 | 1.092929 | 0.340852 | 1.576763 | 0.873016 | 0.818452 |
| JA2 | shadowsocks | G0 | 4 | 0.826455 | 0.833333 | 0.599029 | 0.313482 | 0.864216 | 0.761905 | 0.858730 |
| JA2 | shadowsocks | G1 | 0 | 0.716534 | 0.750000 | 1.728811 | 0.370370 | 2.494147 | 0.485714 | 0.831944 |
| JA2 | shadowsocks | G1 | 1 | 0.745503 | 0.750000 | 0.686979 | 0.352736 | 0.991102 | 0.633333 | 0.801587 |
| JA2 | shadowsocks | G1 | 2 | 0.665344 | 0.708333 | 1.458299 | 0.574413 | 2.103880 | 0.428571 | 0.783730 |
| JA2 | shadowsocks | G1 | 3 | 0.630724 | 0.666667 | 1.154723 | 0.427816 | 1.665913 | 0.400000 | 0.746086 |
| JA2 | shadowsocks | G1 | 4 | 0.728042 | 0.750000 | 0.971517 | 0.380464 | 1.401603 | 0.533333 | 0.825397 |
| JA2 | shadowsocks | G2 | 0 | 0.593025 | 0.625000 | 1.502934 | 0.520770 | 2.168276 | 0.333333 | 0.722872 |
| JA2 | shadowsocks | G2 | 1 | 0.700433 | 0.750000 | 1.131967 | 0.421100 | 1.633083 | 0.500000 | 0.800649 |
| JA2 | shadowsocks | G2 | 2 | 0.686869 | 0.750000 | 0.984858 | 0.364158 | 1.420850 | 0.333333 | 0.863636 |
| JA2 | shadowsocks | G2 | 3 | 0.537037 | 0.583333 | 2.341842 | 0.660978 | 3.378564 | 0.333333 | 0.638889 |
| JA2 | shadowsocks | G2 | 4 | 0.565657 | 0.625000 | 1.206229 | 0.600036 | 1.740220 | 0.250000 | 0.723485 |
| JA2 | trojan | G0 | 0 | 0.839683 | 0.833333 | 0.476998 | 0.252271 | 0.688163 | 0.928571 | 0.795238 |
| JA2 | trojan | G0 | 1 | 0.789683 | 0.791667 | 0.542203 | 0.266686 | 0.782233 | 0.875000 | 0.747024 |
| JA2 | trojan | G0 | 2 | 0.755556 | 0.791667 | 0.408033 | 0.246103 | 0.588668 | 0.644444 | 0.811111 |
| JA2 | trojan | G0 | 3 | 0.707540 | 0.708333 | 0.720367 | 0.381030 | 1.039270 | 0.733333 | 0.694643 |
| JA2 | trojan | G0 | 4 | 0.836640 | 0.833333 | 0.409998 | 0.257113 | 0.591502 | 0.928571 | 0.790675 |
| JA2 | trojan | G1 | 0 | 0.873016 | 0.875000 | 0.201834 | 0.123256 | 0.291185 | 0.785714 | 0.916667 |
| JA2 | trojan | G1 | 1 | 0.828704 | 0.833333 | 0.712818 | 0.282172 | 1.028379 | 0.666667 | 0.909722 |
| JA2 | trojan | G1 | 2 | 0.823413 | 0.833333 | 0.499457 | 0.267382 | 0.720564 | 0.888889 | 0.790675 |
| JA2 | trojan | G1 | 3 | 0.828042 | 0.833333 | 0.545431 | 0.283917 | 0.786890 | 0.761905 | 0.861111 |
| JA2 | trojan | G1 | 4 | 0.786376 | 0.791667 | 0.384270 | 0.243169 | 0.554384 | 0.708333 | 0.825397 |
| JA2 | trojan | G2 | 0 | 0.868386 | 0.875000 | 0.391264 | 0.195623 | 0.564474 | 0.785714 | 0.909722 |
| JA2 | trojan | G2 | 1 | 0.787037 | 0.791667 | 0.682966 | 0.268925 | 0.985312 | 0.777778 | 0.791667 |
| JA2 | trojan | G2 | 2 | 0.783249 | 0.791667 | 0.457786 | 0.246513 | 0.660445 | 0.666667 | 0.841540 |
| JA2 | trojan | G2 | 3 | 0.788360 | 0.791667 | 0.595565 | 0.329808 | 0.859218 | 0.714286 | 0.825397 |
| JA2 | trojan | G2 | 4 | 0.836640 | 0.833333 | 0.281293 | 0.177003 | 0.405820 | 0.803571 | 0.853175 |
| JA2 | vless | G0 | 0 | 0.876720 | 0.875000 | 0.689495 | 0.326502 | 0.994731 | 0.928571 | 0.850794 |
| JA2 | vless | G0 | 1 | 0.765079 | 0.791667 | 0.602375 | 0.261611 | 0.869043 | 0.873016 | 0.711111 |
| JA2 | vless | G0 | 2 | 0.752116 | 0.750000 | 0.746239 | 0.380756 | 1.076595 | 0.761905 | 0.747222 |
| JA2 | vless | G0 | 3 | 0.836640 | 0.833333 | 0.270979 | 0.146462 | 0.390940 | 0.928571 | 0.790675 |
| JA2 | vless | G0 | 4 | 0.826058 | 0.833333 | 0.939980 | 0.293025 | 1.356105 | 0.730159 | 0.874008 |
| JA2 | vless | G1 | 0 | 0.751984 | 0.750000 | 0.620691 | 0.339076 | 0.895468 | 0.666667 | 0.794643 |
| JA2 | vless | G1 | 1 | 0.805820 | 0.833333 | 0.652953 | 0.243356 | 0.942012 | 0.700000 | 0.858730 |
| JA2 | vless | G1 | 2 | 0.749339 | 0.750000 | 1.568111 | 0.459752 | 2.262306 | 0.761905 | 0.743056 |
| JA2 | vless | G1 | 3 | 0.957672 | 0.958333 | 0.385184 | 0.119731 | 0.555704 | 0.928571 | 0.972222 |
| JA2 | vless | G1 | 4 | 0.877381 | 0.875000 | 0.671640 | 0.211053 | 0.968971 | 0.857143 | 0.887500 |
| JA2 | vless | G2 | 0 | 0.828704 | 0.833333 | 0.547802 | 0.278203 | 0.790312 | 0.833333 | 0.826389 |
| JA2 | vless | G2 | 1 | 0.832011 | 0.833333 | 0.650645 | 0.230862 | 0.938682 | 0.888889 | 0.803571 |
| JA2 | vless | G2 | 2 | 0.756085 | 0.750000 | 1.224112 | 0.465328 | 1.766021 | 0.744444 | 0.761905 |
| JA2 | vless | G2 | 3 | 0.916005 | 0.916667 | 0.350398 | 0.178169 | 0.505518 | 0.873016 | 0.937500 |
| JA2 | vless | G2 | 4 | 0.798016 | 0.791667 | 0.722970 | 0.257670 | 1.043025 | 0.857143 | 0.768452 |
| JA2 | vmess | G0 | 0 | 0.835714 | 0.833333 | 0.615796 | 0.240898 | 0.888406 | 0.857143 | 0.825000 |
| JA2 | vmess | G0 | 1 | 0.739586 | 0.750000 | 1.183644 | 0.432652 | 1.707638 | 0.857143 | 0.680808 |
| JA2 | vmess | G0 | 2 | 0.704365 | 0.708333 | 0.857770 | 0.424184 | 1.237501 | 0.875000 | 0.619048 |
| JA2 | vmess | G0 | 3 | 0.730736 | 0.750000 | 0.818823 | 0.306327 | 1.181312 | 0.833333 | 0.679437 |
| JA2 | vmess | G0 | 4 | 0.731746 | 0.750000 | 0.829778 | 0.320815 | 1.197117 | 0.600000 | 0.797619 |
| JA2 | vmess | G1 | 0 | 0.868783 | 0.875000 | 0.805754 | 0.244477 | 1.162457 | 0.761905 | 0.922222 |
| JA2 | vmess | G1 | 1 | 0.444444 | 0.541667 | 1.782313 | 0.613709 | 2.571335 | 0.000000 | 0.666667 |
| JA2 | vmess | G1 | 2 | 0.685185 | 0.750000 | 0.685841 | 0.388284 | 0.989459 | 0.333333 | 0.861111 |
| JA2 | vmess | G1 | 3 | 0.703755 | 0.750000 | 1.523211 | 0.446046 | 2.197529 | 0.428571 | 0.841346 |
| JA2 | vmess | G1 | 4 | 0.589995 | 0.666667 | 1.194591 | 0.418854 | 1.723431 | 0.200000 | 0.784993 |
| JA2 | vmess | G2 | 0 | 0.650265 | 0.708333 | 0.543904 | 0.311576 | 0.784688 | 0.428571 | 0.761111 |
| JA2 | vmess | G2 | 1 | 0.683598 | 0.750000 | 1.332017 | 0.453716 | 1.921694 | 0.444444 | 0.803175 |
| JA2 | vmess | G2 | 2 | 0.778307 | 0.791667 | 0.812290 | 0.320625 | 1.171886 | 0.700000 | 0.817460 |
| JA2 | vmess | G2 | 3 | 0.730736 | 0.791667 | 1.186451 | 0.361912 | 1.711687 | 0.428571 | 0.881818 |
| JA2 | vmess | G2 | 4 | 0.689069 | 0.750000 | 0.947198 | 0.407502 | 1.366518 | 0.500000 | 0.783604 |
| StrongPost | shadowsocks | G0 | 0 | 0.841450 | 0.833333 | 0.440739 | 0.255382 | 0.635852 | 0.857143 | 0.833604 |
| StrongPost | shadowsocks | G0 | 1 | 0.774603 | 0.791667 | 0.813660 | 0.321727 | 1.173863 | 0.857143 | 0.733333 |
| StrongPost | shadowsocks | G0 | 2 | 0.635053 | 0.708333 | 1.158501 | 0.466025 | 1.671363 | 0.400000 | 0.752579 |
| StrongPost | shadowsocks | G0 | 3 | 0.826720 | 0.833333 | 0.900484 | 0.263456 | 1.299123 | 0.875000 | 0.802579 |
| StrongPost | shadowsocks | G0 | 4 | 0.728042 | 0.750000 | 0.971594 | 0.426195 | 1.401714 | 0.533333 | 0.825397 |
| StrongPost | shadowsocks | G1 | 0 | 0.865079 | 0.875000 | 0.783844 | 0.248230 | 1.130847 | 0.761905 | 0.916667 |
| StrongPost | shadowsocks | G1 | 1 | 0.836640 | 0.833333 | 0.527269 | 0.260026 | 0.760689 | 0.761905 | 0.874008 |
| StrongPost | shadowsocks | G1 | 2 | 0.790079 | 0.791667 | 0.802268 | 0.350444 | 1.157428 | 0.833333 | 0.768452 |
| StrongPost | shadowsocks | G1 | 3 | 0.722222 | 0.750000 | 0.808231 | 0.320799 | 1.166030 | 0.533333 | 0.816667 |
| StrongPost | shadowsocks | G1 | 4 | 0.702742 | 0.708333 | 0.718567 | 0.384229 | 1.036673 | 0.714286 | 0.696970 |
| StrongPost | shadowsocks | G2 | 0 | 0.694444 | 0.708333 | 1.044395 | 0.488614 | 1.506743 | 0.500000 | 0.791667 |
| StrongPost | shadowsocks | G2 | 1 | 0.571429 | 0.625000 | 1.022656 | 0.537885 | 1.475381 | 0.200000 | 0.757143 |
| StrongPost | shadowsocks | G2 | 2 | 0.484524 | 0.541667 | 1.416834 | 0.691490 | 2.044059 | 0.142857 | 0.655357 |
| StrongPost | shadowsocks | G2 | 3 | 0.827778 | 0.833333 | 0.958801 | 0.353135 | 1.383258 | 0.833333 | 0.825000 |
| StrongPost | shadowsocks | G2 | 4 | 0.753968 | 0.750000 | 0.743137 | 0.346318 | 1.072120 | 0.571429 | 0.845238 |
| StrongPost | trojan | G0 | 0 | 0.915344 | 0.916667 | 0.316601 | 0.166678 | 0.456758 | 0.944444 | 0.900794 |
| StrongPost | trojan | G0 | 1 | 0.915344 | 0.916667 | 0.358469 | 0.168140 | 0.517162 | 0.944444 | 0.900794 |
| StrongPost | trojan | G0 | 2 | 0.868783 | 0.875000 | 0.356769 | 0.212508 | 0.514709 | 0.833333 | 0.886508 |
| StrongPost | trojan | G0 | 3 | 0.784392 | 0.791667 | 0.450550 | 0.264504 | 0.650007 | 0.888889 | 0.732143 |
| StrongPost | trojan | G0 | 4 | 0.832672 | 0.833333 | 0.391123 | 0.236858 | 0.564272 | 0.928571 | 0.784722 |
| StrongPost | trojan | G1 | 0 | 0.874339 | 0.875000 | 0.278787 | 0.156368 | 0.402205 | 0.803571 | 0.909722 |
| StrongPost | trojan | G1 | 1 | 0.919048 | 0.916667 | 0.543539 | 0.189025 | 0.784161 | 0.928571 | 0.914286 |
| StrongPost | trojan | G1 | 2 | 0.830688 | 0.833333 | 0.515054 | 0.303101 | 0.743066 | 0.944444 | 0.773810 |
| StrongPost | trojan | G1 | 3 | 0.873677 | 0.875000 | 0.382418 | 0.209032 | 0.551713 | 0.857143 | 0.881944 |
| StrongPost | trojan | G1 | 4 | 0.915344 | 0.916667 | 0.408417 | 0.219574 | 0.589222 | 0.928571 | 0.908730 |
| StrongPost | trojan | G2 | 0 | 0.865741 | 0.875000 | 0.372098 | 0.207034 | 0.536824 | 0.833333 | 0.881944 |
| StrongPost | trojan | G2 | 1 | 0.915344 | 0.916667 | 0.276294 | 0.151772 | 0.398609 | 0.888889 | 0.928571 |
| StrongPost | trojan | G2 | 2 | 0.784127 | 0.791667 | 0.464700 | 0.274186 | 0.670421 | 0.619048 | 0.866667 |
| StrongPost | trojan | G2 | 3 | 0.784392 | 0.791667 | 0.513590 | 0.288086 | 0.740953 | 0.660714 | 0.846230 |
| StrongPost | trojan | G2 | 4 | 0.916005 | 0.916667 | 0.326284 | 0.189009 | 0.470728 | 0.875000 | 0.936508 |
| StrongPost | vless | G0 | 0 | 0.754930 | 0.750000 | 0.683289 | 0.347713 | 0.985778 | 0.785714 | 0.739538 |
| StrongPost | vless | G0 | 1 | 0.787434 | 0.791667 | 0.682205 | 0.341960 | 0.984214 | 0.803571 | 0.779365 |
| StrongPost | vless | G0 | 2 | 0.756746 | 0.750000 | 0.716803 | 0.376796 | 1.034128 | 0.761905 | 0.754167 |
| StrongPost | vless | G0 | 3 | 0.916005 | 0.916667 | 0.293534 | 0.132173 | 0.423479 | 1.000000 | 0.874008 |
| StrongPost | vless | G0 | 4 | 0.877381 | 0.875000 | 0.721234 | 0.253667 | 1.040521 | 0.803571 | 0.914286 |
| StrongPost | vless | G1 | 0 | 0.790079 | 0.791667 | 0.658470 | 0.319920 | 0.949971 | 0.733333 | 0.818452 |
| StrongPost | vless | G1 | 1 | 0.767196 | 0.791667 | 0.716419 | 0.294478 | 1.033575 | 0.628571 | 0.836508 |
| StrongPost | vless | G1 | 2 | 0.673280 | 0.666667 | 0.849921 | 0.453918 | 1.226177 | 0.708333 | 0.655754 |
| StrongPost | vless | G1 | 3 | 0.874339 | 0.875000 | 0.514973 | 0.183101 | 0.742949 | 0.875000 | 0.874008 |
| StrongPost | vless | G1 | 4 | 0.873677 | 0.875000 | 0.612155 | 0.205797 | 0.883153 | 0.857143 | 0.881944 |
| StrongPost | vless | G2 | 0 | 0.787831 | 0.791667 | 0.677247 | 0.339393 | 0.977061 | 0.833333 | 0.765079 |
| StrongPost | vless | G2 | 1 | 0.826058 | 0.833333 | 0.485366 | 0.222004 | 0.700234 | 0.888889 | 0.794643 |
| StrongPost | vless | G2 | 2 | 0.743567 | 0.750000 | 0.823879 | 0.419464 | 1.188607 | 0.660714 | 0.784993 |
| StrongPost | vless | G2 | 3 | 0.874339 | 0.875000 | 0.490625 | 0.212995 | 0.707822 | 0.928571 | 0.847222 |
| StrongPost | vless | G2 | 4 | 0.757937 | 0.750000 | 0.710873 | 0.295445 | 1.025573 | 0.803571 | 0.735119 |
| StrongPost | vmess | G0 | 0 | 0.832672 | 0.833333 | 0.420336 | 0.211746 | 0.606417 | 0.873016 | 0.812500 |
| StrongPost | vmess | G0 | 1 | 0.778307 | 0.791667 | 0.613581 | 0.298838 | 0.885210 | 0.857143 | 0.738889 |
| StrongPost | vmess | G0 | 2 | 0.567100 | 0.583333 | 1.678055 | 0.574303 | 2.420922 | 0.595238 | 0.553030 |
| StrongPost | vmess | G0 | 3 | 0.868783 | 0.875000 | 0.832990 | 0.246527 | 1.201750 | 1.000000 | 0.803175 |
| StrongPost | vmess | G0 | 4 | 0.835714 | 0.833333 | 0.697858 | 0.261445 | 1.006797 | 0.828571 | 0.839286 |
| StrongPost | vmess | G1 | 0 | 0.907407 | 0.916667 | 0.493011 | 0.185163 | 0.711264 | 0.833333 | 0.944444 |
| StrongPost | vmess | G1 | 1 | 0.828042 | 0.833333 | 0.522460 | 0.273116 | 0.753751 | 0.761905 | 0.861111 |
| StrongPost | vmess | G1 | 2 | 0.828704 | 0.833333 | 0.545520 | 0.303474 | 0.787019 | 0.708333 | 0.888889 |
| StrongPost | vmess | G1 | 3 | 0.795635 | 0.791667 | 0.865684 | 0.275559 | 1.248918 | 0.708333 | 0.839286 |
| StrongPost | vmess | G1 | 4 | 0.876720 | 0.875000 | 0.704257 | 0.208945 | 1.016029 | 0.857143 | 0.886508 |
| StrongPost | vmess | G2 | 0 | 0.781481 | 0.791667 | 0.414995 | 0.249447 | 0.598712 | 0.714286 | 0.815079 |
| StrongPost | vmess | G2 | 1 | 0.686243 | 0.708333 | 1.232840 | 0.440531 | 1.778611 | 0.642857 | 0.707937 |
| StrongPost | vmess | G2 | 2 | 0.706481 | 0.750000 | 0.972225 | 0.442069 | 1.402624 | 0.500000 | 0.809722 |
| StrongPost | vmess | G2 | 3 | 0.809524 | 0.833333 | 0.913365 | 0.284916 | 1.317707 | 0.628571 | 0.900000 |
| StrongPost | vmess | G2 | 4 | 0.727778 | 0.750000 | 0.896819 | 0.372266 | 1.293837 | 0.700000 | 0.741667 |

## 180个外层参数选择

| arm | eta | group | outer | source_inner_F1 | t | target |
| --- | --- | --- | --- | --- | --- | --- |
| JA0 | 100.000000 | G0 | 0 | 0.786875 | 1.000000 | shadowsocks |
| JA0 | 100.000000 | G0 | 1 | 0.797966 | 4.000000 | shadowsocks |
| JA0 | 0.100000 | G0 | 2 | 0.850787 | 4.000000 | shadowsocks |
| JA0 | 0.100000 | G0 | 3 | 0.801078 | 4.000000 | shadowsocks |
| JA0 | 1.000000 | G0 | 4 | 0.823222 | 0.250000 | shadowsocks |
| JA0 | 1.000000 | G1 | 0 | 0.593468 | 0.000000 | shadowsocks |
| JA0 | 0.100000 | G1 | 1 | 0.643188 | 4.000000 | shadowsocks |
| JA0 | 0.100000 | G1 | 2 | 0.632752 | 1.000000 | shadowsocks |
| JA0 | 0.100000 | G1 | 3 | 0.633124 | 4.000000 | shadowsocks |
| JA0 | 0.100000 | G1 | 4 | 0.631306 | 0.000000 | shadowsocks |
| JA0 | 100.000000 | G2 | 0 | 0.647480 | 0.000000 | shadowsocks |
| JA0 | 0.100000 | G2 | 1 | 0.582604 | 0.000000 | shadowsocks |
| JA0 | 1.000000 | G2 | 2 | 0.686291 | 4.000000 | shadowsocks |
| JA0 | 100.000000 | G2 | 3 | 0.649470 | 0.000000 | shadowsocks |
| JA0 | 10.000000 | G2 | 4 | 0.660264 | 0.250000 | shadowsocks |
| JA0 | 0.100000 | G0 | 0 | 0.728006 | 4.000000 | trojan |
| JA0 | 0.100000 | G0 | 1 | 0.742387 | 4.000000 | trojan |
| JA0 | 0.100000 | G0 | 2 | 0.797557 | 1.000000 | trojan |
| JA0 | 0.100000 | G0 | 3 | 0.751552 | 4.000000 | trojan |
| JA0 | 0.100000 | G0 | 4 | 0.791327 | 4.000000 | trojan |
| JA0 | 0.100000 | G1 | 0 | 0.508489 | 4.000000 | trojan |
| JA0 | 0.100000 | G1 | 1 | 0.526384 | 0.250000 | trojan |
| JA0 | 0.100000 | G1 | 2 | 0.523300 | 0.000000 | trojan |
| JA0 | 0.100000 | G1 | 3 | 0.491867 | 4.000000 | trojan |
| JA0 | 0.100000 | G1 | 4 | 0.529487 | 0.000000 | trojan |
| JA0 | 0.100000 | G2 | 0 | 0.566474 | 0.000000 | trojan |
| JA0 | 0.100000 | G2 | 1 | 0.525053 | 0.250000 | trojan |
| JA0 | 0.100000 | G2 | 2 | 0.581992 | 4.000000 | trojan |
| JA0 | 0.100000 | G2 | 3 | 0.549171 | 0.000000 | trojan |
| JA0 | 0.100000 | G2 | 4 | 0.530990 | 4.000000 | trojan |
| JA0 | 0.100000 | G0 | 0 | 0.812012 | 4.000000 | vless |
| JA0 | 0.100000 | G0 | 1 | 0.803270 | 4.000000 | vless |
| JA0 | 0.100000 | G0 | 2 | 0.823692 | 4.000000 | vless |
| JA0 | 0.100000 | G0 | 3 | 0.796216 | 4.000000 | vless |
| JA0 | 0.100000 | G0 | 4 | 0.870424 | 4.000000 | vless |
| JA0 | 0.100000 | G1 | 0 | 0.576547 | 0.250000 | vless |
| JA0 | 0.100000 | G1 | 1 | 0.610960 | 0.000000 | vless |
| JA0 | 0.100000 | G1 | 2 | 0.583273 | 0.250000 | vless |
| JA0 | 0.100000 | G1 | 3 | 0.589024 | 0.000000 | vless |
| JA0 | 0.100000 | G1 | 4 | 0.558523 | 4.000000 | vless |
| JA0 | 0.100000 | G2 | 0 | 0.528015 | 4.000000 | vless |
| JA0 | 0.100000 | G2 | 1 | 0.466721 | 0.000000 | vless |
| JA0 | 0.100000 | G2 | 2 | 0.482938 | 1.000000 | vless |
| JA0 | 0.100000 | G2 | 3 | 0.516448 | 0.000000 | vless |
| JA0 | 0.100000 | G2 | 4 | 0.486641 | 4.000000 | vless |
| JA0 | 10.000000 | G0 | 0 | 0.830426 | 0.000000 | vmess |
| JA0 | 10.000000 | G0 | 1 | 0.847622 | 0.000000 | vmess |
| JA0 | 0.100000 | G0 | 2 | 0.857766 | 4.000000 | vmess |
| JA0 | 0.100000 | G0 | 3 | 0.819959 | 4.000000 | vmess |
| JA0 | 0.100000 | G0 | 4 | 0.848912 | 4.000000 | vmess |
| JA0 | 0.100000 | G1 | 0 | 0.707138 | 4.000000 | vmess |
| JA0 | 0.100000 | G1 | 1 | 0.725611 | 0.000000 | vmess |
| JA0 | 0.100000 | G1 | 2 | 0.631367 | 0.250000 | vmess |
| JA0 | 100.000000 | G1 | 3 | 0.606984 | 0.250000 | vmess |
| JA0 | 0.100000 | G1 | 4 | 0.615627 | 4.000000 | vmess |
| JA0 | 0.100000 | G2 | 0 | 0.679431 | 1.000000 | vmess |
| JA0 | 0.100000 | G2 | 1 | 0.508949 | 0.250000 | vmess |
| JA0 | 0.100000 | G2 | 2 | 0.654374 | 0.250000 | vmess |
| JA0 | 0.100000 | G2 | 3 | 0.612948 | 0.250000 | vmess |
| JA0 | 0.100000 | G2 | 4 | 0.572966 | 4.000000 | vmess |
| JA1 | 10.000000 | G0 | 0 | 0.791893 | 1.000000 | shadowsocks |
| JA1 | 10.000000 | G0 | 1 | 0.801568 | 4.000000 | shadowsocks |
| JA1 | 1.000000 | G0 | 2 | 0.855886 | 4.000000 | shadowsocks |
| JA1 | 0.100000 | G0 | 3 | 0.823248 | 0.000000 | shadowsocks |
| JA1 | 10.000000 | G0 | 4 | 0.825014 | 4.000000 | shadowsocks |
| JA1 | 0.100000 | G1 | 0 | 0.610018 | 4.000000 | shadowsocks |
| JA1 | 0.100000 | G1 | 1 | 0.674702 | 1.000000 | shadowsocks |
| JA1 | 100.000000 | G1 | 2 | 0.622622 | 1.000000 | shadowsocks |
| JA1 | 0.100000 | G1 | 3 | 0.684568 | 1.000000 | shadowsocks |
| JA1 | 1.000000 | G1 | 4 | 0.637159 | 0.000000 | shadowsocks |
| JA1 | 10.000000 | G2 | 0 | 0.664799 | 4.000000 | shadowsocks |
| JA1 | 1.000000 | G2 | 1 | 0.605410 | 4.000000 | shadowsocks |
| JA1 | 10.000000 | G2 | 2 | 0.677274 | 4.000000 | shadowsocks |
| JA1 | 0.100000 | G2 | 3 | 0.668298 | 0.000000 | shadowsocks |
| JA1 | 1.000000 | G2 | 4 | 0.660205 | 0.000000 | shadowsocks |
| JA1 | 0.100000 | G0 | 0 | 0.748081 | 4.000000 | trojan |
| JA1 | 0.100000 | G0 | 1 | 0.721629 | 4.000000 | trojan |
| JA1 | 0.100000 | G0 | 2 | 0.779101 | 4.000000 | trojan |
| JA1 | 0.100000 | G0 | 3 | 0.724225 | 4.000000 | trojan |
| JA1 | 0.100000 | G0 | 4 | 0.792936 | 1.000000 | trojan |
| JA1 | 0.100000 | G1 | 0 | 0.415629 | 0.000000 | trojan |
| JA1 | 1.000000 | G1 | 1 | 0.464535 | 0.000000 | trojan |
| JA1 | 0.100000 | G1 | 2 | 0.449874 | 0.250000 | trojan |
| JA1 | 10.000000 | G1 | 3 | 0.431073 | 0.000000 | trojan |
| JA1 | 0.100000 | G1 | 4 | 0.520281 | 1.000000 | trojan |
| JA1 | 0.100000 | G2 | 0 | 0.569857 | 1.000000 | trojan |
| JA1 | 0.100000 | G2 | 1 | 0.576211 | 0.250000 | trojan |
| JA1 | 0.100000 | G2 | 2 | 0.577630 | 1.000000 | trojan |
| JA1 | 0.100000 | G2 | 3 | 0.536580 | 4.000000 | trojan |
| JA1 | 0.100000 | G2 | 4 | 0.547172 | 4.000000 | trojan |
| JA1 | 0.100000 | G0 | 0 | 0.785395 | 4.000000 | vless |
| JA1 | 0.100000 | G0 | 1 | 0.780031 | 4.000000 | vless |
| JA1 | 1.000000 | G0 | 2 | 0.799380 | 0.000000 | vless |
| JA1 | 0.100000 | G0 | 3 | 0.780105 | 0.000000 | vless |
| JA1 | 0.100000 | G0 | 4 | 0.862104 | 0.250000 | vless |
| JA1 | 0.100000 | G1 | 0 | 0.476784 | 1.000000 | vless |
| JA1 | 0.100000 | G1 | 1 | 0.531562 | 0.000000 | vless |
| JA1 | 0.100000 | G1 | 2 | 0.462977 | 4.000000 | vless |
| JA1 | 0.100000 | G1 | 3 | 0.545884 | 0.250000 | vless |
| JA1 | 0.100000 | G1 | 4 | 0.551861 | 4.000000 | vless |
| JA1 | 0.100000 | G2 | 0 | 0.503155 | 4.000000 | vless |
| JA1 | 0.100000 | G2 | 1 | 0.464505 | 0.000000 | vless |
| JA1 | 0.100000 | G2 | 2 | 0.502309 | 0.000000 | vless |
| JA1 | 1.000000 | G2 | 3 | 0.493433 | 1.000000 | vless |
| JA1 | 0.100000 | G2 | 4 | 0.501610 | 4.000000 | vless |
| JA1 | 10.000000 | G0 | 0 | 0.834312 | 0.000000 | vmess |
| JA1 | 0.100000 | G0 | 1 | 0.853537 | 4.000000 | vmess |
| JA1 | 0.100000 | G0 | 2 | 0.855738 | 4.000000 | vmess |
| JA1 | 0.100000 | G0 | 3 | 0.849935 | 4.000000 | vmess |
| JA1 | 10.000000 | G0 | 4 | 0.852740 | 0.250000 | vmess |
| JA1 | 0.100000 | G1 | 0 | 0.649214 | 1.000000 | vmess |
| JA1 | 0.100000 | G1 | 1 | 0.708339 | 0.000000 | vmess |
| JA1 | 0.100000 | G1 | 2 | 0.630267 | 0.250000 | vmess |
| JA1 | 0.100000 | G1 | 3 | 0.620442 | 4.000000 | vmess |
| JA1 | 0.100000 | G1 | 4 | 0.650141 | 0.000000 | vmess |
| JA1 | 0.100000 | G2 | 0 | 0.683617 | 4.000000 | vmess |
| JA1 | 0.100000 | G2 | 1 | 0.578343 | 4.000000 | vmess |
| JA1 | 0.100000 | G2 | 2 | 0.719659 | 0.000000 | vmess |
| JA1 | 0.100000 | G2 | 3 | 0.633156 | 0.000000 | vmess |
| JA1 | 0.100000 | G2 | 4 | 0.649580 | 0.250000 | vmess |
| JA2 | 100.000000 | G0 | 0 | 0.786875 | 1.000000 | shadowsocks |
| JA2 | 10.000000 | G0 | 1 | 0.807661 | 4.000000 | shadowsocks |
| JA2 | 1.000000 | G0 | 2 | 0.866639 | 0.000000 | shadowsocks |
| JA2 | 0.100000 | G0 | 3 | 0.827161 | 0.250000 | shadowsocks |
| JA2 | 1.000000 | G0 | 4 | 0.838128 | 4.000000 | shadowsocks |
| JA2 | 0.100000 | G1 | 0 | 0.595124 | 1.000000 | shadowsocks |
| JA2 | 0.100000 | G1 | 1 | 0.680762 | 4.000000 | shadowsocks |
| JA2 | 100.000000 | G1 | 2 | 0.622622 | 1.000000 | shadowsocks |
| JA2 | 0.100000 | G1 | 3 | 0.652593 | 4.000000 | shadowsocks |
| JA2 | 1.000000 | G1 | 4 | 0.627827 | 0.000000 | shadowsocks |
| JA2 | 1.000000 | G2 | 0 | 0.666797 | 0.000000 | shadowsocks |
| JA2 | 1.000000 | G2 | 1 | 0.604471 | 4.000000 | shadowsocks |
| JA2 | 10.000000 | G2 | 2 | 0.677274 | 4.000000 | shadowsocks |
| JA2 | 10.000000 | G2 | 3 | 0.657877 | 0.000000 | shadowsocks |
| JA2 | 1.000000 | G2 | 4 | 0.646608 | 0.250000 | shadowsocks |
| JA2 | 0.100000 | G0 | 0 | 0.770778 | 4.000000 | trojan |
| JA2 | 0.100000 | G0 | 1 | 0.728418 | 4.000000 | trojan |
| JA2 | 0.100000 | G0 | 2 | 0.781091 | 4.000000 | trojan |
| JA2 | 0.100000 | G0 | 3 | 0.781870 | 4.000000 | trojan |
| JA2 | 0.100000 | G0 | 4 | 0.785091 | 4.000000 | trojan |
| JA2 | 0.100000 | G1 | 0 | 0.520255 | 1.000000 | trojan |
| JA2 | 0.100000 | G1 | 1 | 0.466610 | 4.000000 | trojan |
| JA2 | 0.100000 | G1 | 2 | 0.495503 | 0.000000 | trojan |
| JA2 | 0.100000 | G1 | 3 | 0.450482 | 1.000000 | trojan |
| JA2 | 0.100000 | G1 | 4 | 0.508911 | 0.000000 | trojan |
| JA2 | 0.100000 | G2 | 0 | 0.559091 | 4.000000 | trojan |
| JA2 | 0.100000 | G2 | 1 | 0.531951 | 0.000000 | trojan |
| JA2 | 0.100000 | G2 | 2 | 0.606563 | 4.000000 | trojan |
| JA2 | 0.100000 | G2 | 3 | 0.553153 | 4.000000 | trojan |
| JA2 | 0.100000 | G2 | 4 | 0.558921 | 0.000000 | trojan |
| JA2 | 0.100000 | G0 | 0 | 0.791339 | 4.000000 | vless |
| JA2 | 0.100000 | G0 | 1 | 0.777235 | 4.000000 | vless |
| JA2 | 0.100000 | G0 | 2 | 0.837311 | 4.000000 | vless |
| JA2 | 0.100000 | G0 | 3 | 0.800509 | 4.000000 | vless |
| JA2 | 0.100000 | G0 | 4 | 0.854725 | 0.250000 | vless |
| JA2 | 0.100000 | G1 | 0 | 0.540568 | 4.000000 | vless |
| JA2 | 0.100000 | G1 | 1 | 0.596460 | 1.000000 | vless |
| JA2 | 0.100000 | G1 | 2 | 0.543015 | 0.000000 | vless |
| JA2 | 0.100000 | G1 | 3 | 0.572825 | 1.000000 | vless |
| JA2 | 0.100000 | G1 | 4 | 0.636002 | 1.000000 | vless |
| JA2 | 0.100000 | G2 | 0 | 0.495498 | 4.000000 | vless |
| JA2 | 0.100000 | G2 | 1 | 0.517657 | 0.000000 | vless |
| JA2 | 0.100000 | G2 | 2 | 0.485813 | 0.000000 | vless |
| JA2 | 0.100000 | G2 | 3 | 0.519679 | 4.000000 | vless |
| JA2 | 0.100000 | G2 | 4 | 0.487292 | 1.000000 | vless |
| JA2 | 10.000000 | G0 | 0 | 0.832218 | 1.000000 | vmess |
| JA2 | 10.000000 | G0 | 1 | 0.842696 | 0.000000 | vmess |
| JA2 | 0.100000 | G0 | 2 | 0.872524 | 1.000000 | vmess |
| JA2 | 0.100000 | G0 | 3 | 0.839825 | 4.000000 | vmess |
| JA2 | 100.000000 | G0 | 4 | 0.845761 | 0.000000 | vmess |
| JA2 | 0.100000 | G1 | 0 | 0.726170 | 1.000000 | vmess |
| JA2 | 0.100000 | G1 | 1 | 0.757206 | 0.000000 | vmess |
| JA2 | 0.100000 | G1 | 2 | 0.628075 | 4.000000 | vmess |
| JA2 | 100.000000 | G1 | 3 | 0.606984 | 0.250000 | vmess |
| JA2 | 0.100000 | G1 | 4 | 0.627565 | 0.000000 | vmess |
| JA2 | 0.100000 | G2 | 0 | 0.697158 | 4.000000 | vmess |
| JA2 | 0.100000 | G2 | 1 | 0.641787 | 1.000000 | vmess |
| JA2 | 0.100000 | G2 | 2 | 0.716192 | 1.000000 | vmess |
| JA2 | 0.100000 | G2 | 3 | 0.673854 | 1.000000 | vmess |
| JA2 | 0.100000 | G2 | 4 | 0.696031 | 4.000000 | vmess |

## 源内及外层恢复概览

| partition | arm | calibration | MSE |
| --- | --- | --- | --- |
| outer-heldout | JA0 | shadowsocks | 2.916974 |
| outer-heldout | JA0 | trojan | 0.370959 |
| outer-heldout | JA0 | vless | 0.430440 |
| outer-heldout | JA0 | vmess | 1.218200 |
| outer-heldout | JA1 | shadowsocks | 1.236075 |
| outer-heldout | JA1 | trojan | 0.372168 |
| outer-heldout | JA1 | vless | 0.409343 |
| outer-heldout | JA1 | vmess | 0.792297 |
| outer-heldout | JA2 | shadowsocks | 1.601544 |
| outer-heldout | JA2 | trojan | 0.360847 |
| outer-heldout | JA2 | vless | 0.417817 |
| outer-heldout | JA2 | vmess | 1.427163 |
| source-inner-heldout | JA0 | shadowsocks | 0.778842 |
| source-inner-heldout | JA0 | trojan | 11.133802 |
| source-inner-heldout | JA0 | vless | 11.888096 |
| source-inner-heldout | JA0 | vmess | 10.002224 |
| source-inner-heldout | JA1 | shadowsocks | 0.502536 |
| source-inner-heldout | JA1 | trojan | 3.715670 |
| source-inner-heldout | JA1 | vless | 3.948426 |
| source-inner-heldout | JA1 | vmess | 3.340842 |
| source-inner-heldout | JA2 | shadowsocks | 0.947382 |
| source-inner-heldout | JA2 | trojan | 4.825655 |
| source-inner-heldout | JA2 | vless | 5.281746 |
| source-inner-heldout | JA2 | vmess | 4.059466 |

## 十特征块外层恢复误差

| arm | calibration | MSE_W_up | MSE_W_down | MSE_U_up | MSE_U_down | MSE_P_up | MSE_P_down | MSE_E_up | MSE_E_down | MSE_FR_packet_runs | MSE_R_unique_zero_runs |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| JA0 | shadowsocks | 0.379053 | 0.577208 | 0.102112 | 0.330840 | 11.938391 | 1.481130 | 11.938406 | 1.343863 | 0.031518 | 0.019349 |
| JA0 | trojan | 0.328442 | 0.252550 | 0.139318 | 0.328849 | 0.475369 | 0.497080 | 0.512430 | 0.548931 | 0.298249 | 0.284903 |
| JA0 | vless | 0.438468 | 0.300281 | 0.212863 | 0.412518 | 0.612895 | 0.564367 | 0.468548 | 0.580646 | 0.345385 | 0.332665 |
| JA0 | vmess | 0.422691 | 1.905145 | 0.389971 | 2.554116 | 2.222596 | 0.806741 | 2.217632 | 0.775084 | 0.508356 | 0.419582 |
| JA1 | shadowsocks | 0.326874 | 0.588449 | 0.099852 | 0.328287 | 3.702926 | 1.655921 | 3.782953 | 1.461455 | 0.032987 | 0.020963 |
| JA1 | trojan | 0.264370 | 0.249243 | 0.135448 | 0.329919 | 0.528756 | 0.538246 | 0.579820 | 0.581159 | 0.242441 | 0.221304 |
| JA1 | vless | 0.364002 | 0.289235 | 0.224734 | 0.442829 | 0.578809 | 0.562247 | 0.516985 | 0.558321 | 0.274766 | 0.249844 |
| JA1 | vmess | 0.275231 | 1.432933 | 0.248110 | 2.370096 | 0.939361 | 0.615696 | 0.904599 | 0.594495 | 0.363100 | 0.295065 |
| JA2 | shadowsocks | 0.418912 | 0.787248 | 0.239803 | 0.587144 | 5.052833 | 1.652545 | 5.048103 | 1.471788 | 0.171169 | 0.148588 |
| JA2 | trojan | 0.335510 | 0.218443 | 0.173669 | 0.300994 | 0.423222 | 0.484673 | 0.457119 | 0.580359 | 0.300493 | 0.292512 |
| JA2 | vless | 0.467426 | 0.258285 | 0.263839 | 0.380168 | 0.592288 | 0.561834 | 0.438845 | 0.574001 | 0.316285 | 0.295044 |
| JA2 | vmess | 0.399628 | 1.938948 | 0.359686 | 2.632392 | 3.280568 | 0.869078 | 3.098081 | 0.825535 | 0.454522 | 0.375391 |
