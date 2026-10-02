# Extend v3 结果补充

本附件追溯整理已完成实验，不是新预注册或新检验。不重训、不重新抽样；全部区间来自已保存的内容簇 bootstrap 数组。分数为 0–1，差值也使用该尺度，乘 100 才是百分点。

主比较 W 十项与 T 八项分别校正，不构成合并十八项家族的统一错误率保证。其余对照仅显示普通 95% 区间，是描述性次要比较；不得根据这里的高分替换主方法。reference 不是同资源参照或理论上界。

## 总体指标

| track   | protocol    | arm       |   F1_new |   F1_all |   BA_all |   CE_all_bits |   Brier_all |   CE_new_bits |   Brier_new |
|:--------|:------------|:----------|---------:|---------:|---------:|--------------:|------------:|--------------:|------------:|
| T       | shadowsocks | center    | 0.559742 | 0.654885 | 0.674884 |      1.574419 |    0.472494 |      2.158400 |    0.690583 |
| T       | shadowsocks | cyclic    | 0.542866 | 0.652641 | 0.667477 |      1.305077 |    0.465530 |      1.556031 |    0.633192 |
| T       | shadowsocks | group     | 0.563215 | 0.659903 | 0.671991 |      1.283424 |    0.449435 |      1.477410 |    0.593864 |
| T       | shadowsocks | marginal  | 0.702987 | 0.726737 | 0.726157 |      1.357554 |    0.397454 |      1.478975 |    0.451228 |
| T       | shadowsocks | paired    | 0.663410 | 0.716945 | 0.721991 |      1.349372 |    0.398837 |      1.490508 |    0.484646 |
| T       | shadowsocks | raw       | 0.355590 | 0.583857 | 0.634491 |      1.916133 |    0.566422 |      3.568498 |    1.096453 |
| T       | shadowsocks | reference | 0.734534 | 0.735676 | 0.734722 |      1.342975 |    0.379184 |      1.279209 |    0.371825 |
| T       | trojan      | center    | 0.589109 | 0.665213 | 0.693866 |      1.224449 |    0.438315 |      1.716830 |    0.599757 |
| T       | trojan      | cyclic    | 0.585566 | 0.668398 | 0.683218 |      1.274704 |    0.462055 |      1.582310 |    0.587990 |
| T       | trojan      | group     | 0.618981 | 0.683174 | 0.695602 |      1.215455 |    0.444904 |      1.459494 |    0.543913 |
| T       | trojan      | marginal  | 0.707125 | 0.734483 | 0.740856 |      1.001909 |    0.374128 |      1.139036 |    0.424762 |
| T       | trojan      | paired    | 0.723723 | 0.751898 | 0.756250 |      0.965505 |    0.359364 |      1.114355 |    0.417378 |
| T       | trojan      | raw       | 0.072201 | 0.449468 | 0.532292 |      2.747142 |    0.699836 |      6.482648 |    1.459940 |
| T       | trojan      | reference | 0.771780 | 0.776593 | 0.778009 |      0.885923 |    0.330243 |      0.893945 |    0.332249 |
| T       | vless       | center    | 0.485231 | 0.600433 | 0.627662 |      1.840806 |    0.549905 |      2.518870 |    0.752665 |
| T       | vless       | cyclic    | 0.558723 | 0.648381 | 0.665046 |      1.560889 |    0.510583 |      1.826407 |    0.611113 |
| T       | vless       | group     | 0.603920 | 0.674280 | 0.687153 |      1.521669 |    0.492873 |      1.720309 |    0.571477 |
| T       | vless       | marginal  | 0.695267 | 0.717542 | 0.721991 |      1.528895 |    0.457353 |      1.693614 |    0.517185 |
| T       | vless       | paired    | 0.708135 | 0.729445 | 0.733333 |      1.523888 |    0.450067 |      1.689968 |    0.510011 |
| T       | vless       | raw       | 0.068934 | 0.431327 | 0.508449 |      3.247543 |    0.765048 |      7.214442 |    1.512530 |
| T       | vless       | reference | 0.734373 | 0.736099 | 0.737037 |      1.478567 |    0.422787 |      1.470041 |    0.421866 |
| T       | vmess       | center    | 0.554975 | 0.631973 | 0.655208 |      1.529634 |    0.498528 |      2.061251 |    0.654485 |
| T       | vmess       | cyclic    | 0.532414 | 0.621814 | 0.638079 |      1.445462 |    0.513233 |      1.784169 |    0.643661 |
| T       | vmess       | group     | 0.577776 | 0.645454 | 0.660648 |      1.387121 |    0.489781 |      1.668611 |    0.596649 |
| T       | vmess       | marginal  | 0.671004 | 0.694926 | 0.705324 |      1.316585 |    0.434833 |      1.498792 |    0.490083 |
| T       | vmess       | paired    | 0.666663 | 0.695838 | 0.705556 |      1.315892 |    0.432830 |      1.536496 |    0.509323 |
| T       | vmess       | raw       | 0.092886 | 0.441539 | 0.508912 |      3.851693 |    0.759848 |      9.397263 |    1.505282 |
| T       | vmess       | reference | 0.716351 | 0.718542 | 0.723380 |      1.236020 |    0.409848 |      1.240257 |    0.411193 |
| W       | anytls      | center    | 0.752645 | 0.784601 | 0.795486 |      1.793451 |    0.351670 |      1.809001 |    0.413220 |
| W       | anytls      | cyclic    | 0.559699 | 0.667061 | 0.693403 |      1.691649 |    0.492272 |      1.619865 |    0.540637 |
| W       | anytls      | group     | 0.628466 | 0.701176 | 0.718519 |      1.676682 |    0.478012 |      1.582319 |    0.513173 |
| W       | anytls      | marginal  | 0.762472 | 0.790625 | 0.799884 |      1.726596 |    0.361611 |      1.647352 |    0.403636 |
| W       | anytls      | paired    | 0.796008 | 0.807323 | 0.811111 |      1.813202 |    0.356617 |      1.719929 |    0.382076 |
| W       | anytls      | raw       | 0.386694 | 0.545292 | 0.601852 |      2.616613 |    0.544098 |      3.968197 |    0.858210 |
| W       | anytls      | reference | 0.809061 | 0.802334 | 0.805093 |      1.928818 |    0.339152 |      1.813973 |    0.342232 |
| W       | shadowsocks | center    | 0.760891 | 0.786030 | 0.794444 |      1.103258 |    0.334998 |      1.128205 |    0.389295 |
| W       | shadowsocks | cyclic    | 0.563510 | 0.670857 | 0.700579 |      1.333028 |    0.476056 |      1.419287 |    0.534835 |
| W       | shadowsocks | group     | 0.601528 | 0.683536 | 0.708912 |      1.299565 |    0.459640 |      1.350029 |    0.507211 |
| W       | shadowsocks | marginal  | 0.778918 | 0.798514 | 0.806713 |      1.068913 |    0.335003 |      1.052642 |    0.375362 |
| W       | shadowsocks | paired    | 0.787975 | 0.800746 | 0.807523 |      1.083311 |    0.333292 |      1.066951 |    0.361282 |
| W       | shadowsocks | raw       | 0.359264 | 0.539545 | 0.601620 |      2.059027 |    0.564749 |      3.669172 |    0.970579 |
| W       | shadowsocks | reference | 0.809060 | 0.815129 | 0.817824 |      1.099231 |    0.315808 |      0.982624 |    0.323228 |
| W       | trojan      | center    | 0.685506 | 0.688897 | 0.694676 |      1.343983 |    0.433418 |      1.397294 |    0.450469 |
| W       | trojan      | cyclic    | 0.533663 | 0.618308 | 0.641898 |      1.481600 |    0.534484 |      1.566135 |    0.592622 |
| W       | trojan      | group     | 0.579938 | 0.637203 | 0.655208 |      1.428258 |    0.518961 |      1.468174 |    0.555994 |
| W       | trojan      | marginal  | 0.672354 | 0.686976 | 0.692245 |      1.343109 |    0.442615 |      1.374372 |    0.461394 |
| W       | trojan      | paired    | 0.670733 | 0.690679 | 0.695833 |      1.341252 |    0.440370 |      1.352708 |    0.455446 |
| W       | trojan      | raw       | 0.235365 | 0.394009 | 0.454282 |      2.237400 |    0.688788 |      3.392724 |    0.959381 |
| W       | trojan      | reference | 0.683214 | 0.681901 | 0.683102 |      1.291823 |    0.436460 |      1.273280 |    0.436036 |
| W       | vless       | center    | 0.702154 | 0.725805 | 0.729167 |      1.628871 |    0.405797 |      1.558107 |    0.431240 |
| W       | vless       | cyclic    | 0.535887 | 0.649732 | 0.670023 |      1.672425 |    0.536154 |      1.585742 |    0.575900 |
| W       | vless       | group     | 0.575971 | 0.664519 | 0.681597 |      1.625773 |    0.519400 |      1.513984 |    0.544003 |
| W       | vless       | marginal  | 0.704055 | 0.730914 | 0.734491 |      1.603362 |    0.416857 |      1.515048 |    0.440532 |
| W       | vless       | paired    | 0.702982 | 0.725298 | 0.728588 |      1.629557 |    0.414506 |      1.525261 |    0.434262 |
| W       | vless       | raw       | 0.357915 | 0.496001 | 0.545833 |      2.271998 |    0.609868 |      3.083534 |    0.833744 |
| W       | vless       | reference | 0.715347 | 0.719882 | 0.726042 |      1.704820 |    0.402690 |      1.597371 |    0.400694 |
| W       | vmess       | center    | 0.676473 | 0.738726 | 0.753588 |      1.405802 |    0.389226 |      1.488318 |    0.441307 |
| W       | vmess       | cyclic    | 0.575039 | 0.672181 | 0.704398 |      1.350033 |    0.471026 |      1.461949 |    0.548272 |
| W       | vmess       | group     | 0.607290 | 0.683180 | 0.711227 |      1.333127 |    0.458997 |      1.391207 |    0.516371 |
| W       | vmess       | marginal  | 0.669691 | 0.729001 | 0.743403 |      1.360093 |    0.398217 |      1.387640 |    0.435716 |
| W       | vmess       | paired    | 0.686778 | 0.738353 | 0.752546 |      1.355045 |    0.385593 |      1.328962 |    0.410198 |
| W       | vmess       | raw       | 0.276378 | 0.458323 | 0.518403 |      2.384353 |    0.648626 |      4.037347 |    1.023228 |
| W       | vmess       | reference | 0.743356 | 0.743918 | 0.754398 |      1.313493 |    0.361901 |      1.293536 |    0.361122 |

## 预定主比较

| track   | protocol    |   business_group | contrast     | metric   |    delta |    low95 |   high95 |   adjusted_low |   adjusted_high |   family_size | primary   |
|:--------|:------------|-----------------:|:-------------|:---------|---------:|---------:|---------:|---------------:|----------------:|--------------:|:----------|
| T       | shadowsocks |               -1 | paired-raw   | F1_new   | 0.307820 | 0.259842 | 0.361104 |       0.239119 |        0.380216 |      8.000000 | True      |
| T       | shadowsocks |               -1 | paired-group | F1_new   | 0.100196 | 0.062826 | 0.140412 |       0.049376 |        0.156770 |      8.000000 | True      |
| T       | trojan      |               -1 | paired-raw   | F1_new   | 0.651522 | 0.584058 | 0.715315 |       0.558924 |        0.740565 |      8.000000 | True      |
| T       | trojan      |               -1 | paired-group | F1_new   | 0.104742 | 0.065928 | 0.149224 |       0.052931 |        0.166271 |      8.000000 | True      |
| T       | vless       |               -1 | paired-raw   | F1_new   | 0.639201 | 0.555616 | 0.717867 |       0.521795 |        0.746977 |      8.000000 | True      |
| T       | vless       |               -1 | paired-group | F1_new   | 0.104215 | 0.068374 | 0.139848 |       0.054338 |        0.153848 |      8.000000 | True      |
| T       | vmess       |               -1 | paired-raw   | F1_new   | 0.573777 | 0.503308 | 0.642719 |       0.472896 |        0.668425 |      8.000000 | True      |
| T       | vmess       |               -1 | paired-group | F1_new   | 0.088887 | 0.061476 | 0.116557 |       0.051737 |        0.126738 |      8.000000 | True      |
| W       | anytls      |               -1 | paired-raw   | F1_new   | 0.409314 | 0.350185 | 0.469105 |       0.327325 |        0.493688 |     10.000000 | True      |
| W       | anytls      |               -1 | paired-group | F1_new   | 0.167542 | 0.132097 | 0.203602 |       0.114180 |        0.216592 |     10.000000 | True      |
| W       | shadowsocks |               -1 | paired-raw   | F1_new   | 0.428711 | 0.343315 | 0.507842 |       0.306958 |        0.538302 |     10.000000 | True      |
| W       | shadowsocks |               -1 | paired-group | F1_new   | 0.186446 | 0.139148 | 0.230214 |       0.114007 |        0.244408 |     10.000000 | True      |
| W       | trojan      |               -1 | paired-raw   | F1_new   | 0.435368 | 0.378871 | 0.487570 |       0.358506 |        0.508190 |     10.000000 | True      |
| W       | trojan      |               -1 | paired-group | F1_new   | 0.090794 | 0.056061 | 0.129289 |       0.042065 |        0.143622 |     10.000000 | True      |
| W       | vless       |               -1 | paired-raw   | F1_new   | 0.345067 | 0.279117 | 0.400697 |       0.251078 |        0.421647 |     10.000000 | True      |
| W       | vless       |               -1 | paired-group | F1_new   | 0.127011 | 0.080766 | 0.167850 |       0.062567 |        0.184269 |     10.000000 | True      |
| W       | vmess       |               -1 | paired-raw   | F1_new   | 0.410400 | 0.373372 | 0.446304 |       0.359626 |        0.461578 |     10.000000 | True      |
| W       | vmess       |               -1 | paired-group | F1_new   | 0.079488 | 0.052654 | 0.109789 |       0.042180 |        0.122137 |     10.000000 | True      |

## 全部次要 F1 对照区间

| track   | protocol    |   business_group | contrast         | metric   |     delta |     low95 |    high95 |   adjusted_low |   adjusted_high |   family_size | primary   |
|:--------|:------------|-----------------:|:-----------------|:---------|----------:|----------:|----------:|---------------:|----------------:|--------------:|:----------|
| T       | shadowsocks |               -1 | paired-cyclic    | F1_new   |  0.120544 |  0.082777 |  0.162044 |            nan |             nan |           nan | False     |
| T       | shadowsocks |               -1 | paired-center    | F1_new   |  0.103668 |  0.065150 |  0.144408 |            nan |             nan |           nan | False     |
| T       | shadowsocks |               -1 | paired-marginal  | F1_new   | -0.039577 | -0.060557 | -0.018665 |            nan |             nan |           nan | False     |
| T       | shadowsocks |               -1 | paired-reference | F1_new   | -0.071124 | -0.107624 | -0.037924 |            nan |             nan |           nan | False     |
| T       | shadowsocks |                0 | paired-raw       | F1_new   |  0.335465 |  0.236729 |  0.431552 |            nan |             nan |           nan | False     |
| T       | shadowsocks |                0 | paired-group     | F1_new   |  0.067376 |  0.025183 |  0.112326 |            nan |             nan |           nan | False     |
| T       | shadowsocks |                0 | paired-cyclic    | F1_new   |  0.069398 |  0.024779 |  0.114669 |            nan |             nan |           nan | False     |
| T       | shadowsocks |                0 | paired-center    | F1_new   |  0.108623 |  0.068479 |  0.153284 |            nan |             nan |           nan | False     |
| T       | shadowsocks |                0 | paired-marginal  | F1_new   |  0.003947 | -0.017370 |  0.031213 |            nan |             nan |           nan | False     |
| T       | shadowsocks |                0 | paired-reference | F1_new   | -0.036287 | -0.089574 |  0.004455 |            nan |             nan |           nan | False     |
| T       | shadowsocks |                1 | paired-raw       | F1_new   |  0.261537 |  0.193432 |  0.344759 |            nan |             nan |           nan | False     |
| T       | shadowsocks |                1 | paired-group     | F1_new   |  0.113368 |  0.072493 |  0.158291 |            nan |             nan |           nan | False     |
| T       | shadowsocks |                1 | paired-cyclic    | F1_new   |  0.143004 |  0.101490 |  0.195037 |            nan |             nan |           nan | False     |
| T       | shadowsocks |                1 | paired-center    | F1_new   |  0.067709 |  0.020850 |  0.120553 |            nan |             nan |           nan | False     |
| T       | shadowsocks |                1 | paired-marginal  | F1_new   | -0.092586 | -0.119138 | -0.060922 |            nan |             nan |           nan | False     |
| T       | shadowsocks |                1 | paired-reference | F1_new   | -0.132420 | -0.185450 | -0.075904 |            nan |             nan |           nan | False     |
| T       | shadowsocks |                2 | paired-raw       | F1_new   |  0.326458 |  0.249265 |  0.403118 |            nan |             nan |           nan | False     |
| T       | shadowsocks |                2 | paired-group     | F1_new   |  0.119842 |  0.049968 |  0.193480 |            nan |             nan |           nan | False     |
| T       | shadowsocks |                2 | paired-cyclic    | F1_new   |  0.149231 |  0.070903 |  0.228306 |            nan |             nan |           nan | False     |
| T       | shadowsocks |                2 | paired-center    | F1_new   |  0.134673 |  0.037405 |  0.222384 |            nan |             nan |           nan | False     |
| T       | shadowsocks |                2 | paired-marginal  | F1_new   | -0.030091 | -0.081681 |  0.013868 |            nan |             nan |           nan | False     |
| T       | shadowsocks |                2 | paired-reference | F1_new   | -0.044666 | -0.113102 |  0.011224 |            nan |             nan |           nan | False     |
| T       | trojan      |               -1 | paired-cyclic    | F1_new   |  0.138157 |  0.096377 |  0.187343 |            nan |             nan |           nan | False     |
| T       | trojan      |               -1 | paired-center    | F1_new   |  0.134614 |  0.088924 |  0.177015 |            nan |             nan |           nan | False     |
| T       | trojan      |               -1 | paired-marginal  | F1_new   |  0.016598 |  0.001357 |  0.032099 |            nan |             nan |           nan | False     |
| T       | trojan      |               -1 | paired-reference | F1_new   | -0.048057 | -0.076970 | -0.022732 |            nan |             nan |           nan | False     |
| T       | trojan      |                0 | paired-raw       | F1_new   |  0.827826 |  0.772075 |  0.877463 |            nan |             nan |           nan | False     |
| T       | trojan      |                0 | paired-group     | F1_new   |  0.052772 |  0.002492 |  0.112194 |            nan |             nan |           nan | False     |
| T       | trojan      |                0 | paired-cyclic    | F1_new   |  0.087499 |  0.025855 |  0.161819 |            nan |             nan |           nan | False     |
| T       | trojan      |                0 | paired-center    | F1_new   |  0.035395 |  0.001380 |  0.075886 |            nan |             nan |           nan | False     |
| T       | trojan      |                0 | paired-marginal  | F1_new   |  0.008158 | -0.010550 |  0.036480 |            nan |             nan |           nan | False     |
| T       | trojan      |                0 | paired-reference | F1_new   |  0.002671 | -0.036685 |  0.035994 |            nan |             nan |           nan | False     |
| T       | trojan      |                1 | paired-raw       | F1_new   |  0.497582 |  0.366796 |  0.614630 |            nan |             nan |           nan | False     |
| T       | trojan      |                1 | paired-group     | F1_new   |  0.219737 |  0.146083 |  0.306453 |            nan |             nan |           nan | False     |
| T       | trojan      |                1 | paired-cyclic    | F1_new   |  0.267912 |  0.202059 |  0.347820 |            nan |             nan |           nan | False     |
| T       | trojan      |                1 | paired-center    | F1_new   |  0.289790 |  0.181031 |  0.382263 |            nan |             nan |           nan | False     |
| T       | trojan      |                1 | paired-marginal  | F1_new   |  0.017550 | -0.022823 |  0.058920 |            nan |             nan |           nan | False     |
| T       | trojan      |                1 | paired-reference | F1_new   | -0.142978 | -0.213794 | -0.083196 |            nan |             nan |           nan | False     |
| T       | trojan      |                2 | paired-raw       | F1_new   |  0.629158 |  0.522649 |  0.748801 |            nan |             nan |           nan | False     |
| T       | trojan      |                2 | paired-group     | F1_new   |  0.041718 | -0.000011 |  0.088173 |            nan |             nan |           nan | False     |
| T       | trojan      |                2 | paired-cyclic    | F1_new   |  0.059059 |  0.005496 |  0.121278 |            nan |             nan |           nan | False     |
| T       | trojan      |                2 | paired-center    | F1_new   |  0.078656 |  0.026954 |  0.149013 |            nan |             nan |           nan | False     |
| T       | trojan      |                2 | paired-marginal  | F1_new   |  0.024085 |  0.010287 |  0.039330 |            nan |             nan |           nan | False     |
| T       | trojan      |                2 | paired-reference | F1_new   | -0.003865 | -0.025445 |  0.016583 |            nan |             nan |           nan | False     |
| T       | vless       |               -1 | paired-cyclic    | F1_new   |  0.149412 |  0.106053 |  0.194284 |            nan |             nan |           nan | False     |
| T       | vless       |               -1 | paired-center    | F1_new   |  0.222904 |  0.163922 |  0.282308 |            nan |             nan |           nan | False     |
| T       | vless       |               -1 | paired-marginal  | F1_new   |  0.012869 |  0.004050 |  0.021605 |            nan |             nan |           nan | False     |
| T       | vless       |               -1 | paired-reference | F1_new   | -0.026238 | -0.056462 |  0.003005 |            nan |             nan |           nan | False     |
| T       | vless       |                0 | paired-raw       | F1_new   |  0.712202 |  0.564664 |  0.831344 |            nan |             nan |           nan | False     |
| T       | vless       |                0 | paired-group     | F1_new   |  0.035426 | -0.015100 |  0.079504 |            nan |             nan |           nan | False     |
| T       | vless       |                0 | paired-cyclic    | F1_new   |  0.076036 |  0.017928 |  0.132478 |            nan |             nan |           nan | False     |
| T       | vless       |                0 | paired-center    | F1_new   |  0.130888 |  0.046280 |  0.226077 |            nan |             nan |           nan | False     |
| T       | vless       |                0 | paired-marginal  | F1_new   |  0.022921 |  0.005690 |  0.040379 |            nan |             nan |           nan | False     |
| T       | vless       |                0 | paired-reference | F1_new   |  0.001350 | -0.017535 |  0.018921 |            nan |             nan |           nan | False     |
| T       | vless       |                1 | paired-raw       | F1_new   |  0.559401 |  0.461450 |  0.653569 |            nan |             nan |           nan | False     |
| T       | vless       |                1 | paired-group     | F1_new   |  0.236440 |  0.165740 |  0.308761 |            nan |             nan |           nan | False     |
| T       | vless       |                1 | paired-cyclic    | F1_new   |  0.287487 |  0.198802 |  0.373762 |            nan |             nan |           nan | False     |
| T       | vless       |                1 | paired-center    | F1_new   |  0.367559 |  0.258722 |  0.473987 |            nan |             nan |           nan | False     |
| T       | vless       |                1 | paired-marginal  | F1_new   |  0.016711 | -0.004578 |  0.036974 |            nan |             nan |           nan | False     |
| T       | vless       |                1 | paired-reference | F1_new   | -0.089884 | -0.159719 | -0.023609 |            nan |             nan |           nan | False     |
| T       | vless       |                2 | paired-raw       | F1_new   |  0.646002 |  0.520007 |  0.774344 |            nan |             nan |           nan | False     |
| T       | vless       |                2 | paired-group     | F1_new   |  0.040780 | -0.004502 |  0.089192 |            nan |             nan |           nan | False     |
| T       | vless       |                2 | paired-cyclic    | F1_new   |  0.084714 |  0.030276 |  0.148597 |            nan |             nan |           nan | False     |
| T       | vless       |                2 | paired-center    | F1_new   |  0.170266 |  0.096977 |  0.237163 |            nan |             nan |           nan | False     |
| T       | vless       |                2 | paired-marginal  | F1_new   | -0.001027 | -0.014565 |  0.012577 |            nan |             nan |           nan | False     |
| T       | vless       |                2 | paired-reference | F1_new   |  0.009821 | -0.024791 |  0.043883 |            nan |             nan |           nan | False     |
| T       | vmess       |               -1 | paired-cyclic    | F1_new   |  0.134249 |  0.098132 |  0.175826 |            nan |             nan |           nan | False     |
| T       | vmess       |               -1 | paired-center    | F1_new   |  0.111688 |  0.071833 |  0.152437 |            nan |             nan |           nan | False     |
| T       | vmess       |               -1 | paired-marginal  | F1_new   | -0.004341 | -0.013790 |  0.004831 |            nan |             nan |           nan | False     |
| T       | vmess       |               -1 | paired-reference | F1_new   | -0.049688 | -0.083690 | -0.018082 |            nan |             nan |           nan | False     |
| T       | vmess       |                0 | paired-raw       | F1_new   |  0.765021 |  0.666092 |  0.857895 |            nan |             nan |           nan | False     |
| T       | vmess       |                0 | paired-group     | F1_new   |  0.068536 |  0.021630 |  0.121054 |            nan |             nan |           nan | False     |
| T       | vmess       |                0 | paired-cyclic    | F1_new   |  0.129070 |  0.059902 |  0.216972 |            nan |             nan |           nan | False     |
| T       | vmess       |                0 | paired-center    | F1_new   |  0.036469 | -0.006382 |  0.088257 |            nan |             nan |           nan | False     |
| T       | vmess       |                0 | paired-marginal  | F1_new   | -0.003448 | -0.011436 |  0.004353 |            nan |             nan |           nan | False     |
| T       | vmess       |                0 | paired-reference | F1_new   | -0.005715 | -0.035460 |  0.021432 |            nan |             nan |           nan | False     |
| T       | vmess       |                1 | paired-raw       | F1_new   |  0.391948 |  0.266840 |  0.488295 |            nan |             nan |           nan | False     |
| T       | vmess       |                1 | paired-group     | F1_new   |  0.168459 |  0.100817 |  0.229424 |            nan |             nan |           nan | False     |
| T       | vmess       |                1 | paired-cyclic    | F1_new   |  0.214729 |  0.137755 |  0.289141 |            nan |             nan |           nan | False     |
| T       | vmess       |                1 | paired-center    | F1_new   |  0.185257 |  0.113419 |  0.255152 |            nan |             nan |           nan | False     |
| T       | vmess       |                1 | paired-marginal  | F1_new   | -0.024599 | -0.049442 |  0.006157 |            nan |             nan |           nan | False     |
| T       | vmess       |                1 | paired-reference | F1_new   | -0.142809 | -0.218814 | -0.078768 |            nan |             nan |           nan | False     |
| T       | vmess       |                2 | paired-raw       | F1_new   |  0.564360 |  0.453924 |  0.688321 |            nan |             nan |           nan | False     |
| T       | vmess       |                2 | paired-group     | F1_new   |  0.029667 |  0.014441 |  0.046582 |            nan |             nan |           nan | False     |
| T       | vmess       |                2 | paired-cyclic    | F1_new   |  0.058948 |  0.029787 |  0.091115 |            nan |             nan |           nan | False     |
| T       | vmess       |                2 | paired-center    | F1_new   |  0.113337 |  0.037304 |  0.192339 |            nan |             nan |           nan | False     |
| T       | vmess       |                2 | paired-marginal  | F1_new   |  0.015024 | -0.002443 |  0.031112 |            nan |             nan |           nan | False     |
| T       | vmess       |                2 | paired-reference | F1_new   | -0.000539 | -0.030153 |  0.031926 |            nan |             nan |           nan | False     |
| W       | anytls      |               -1 | paired-cyclic    | F1_new   |  0.236309 |  0.196483 |  0.282092 |            nan |             nan |           nan | False     |
| W       | anytls      |               -1 | paired-center    | F1_new   |  0.043364 |  0.012088 |  0.075690 |            nan |             nan |           nan | False     |
| W       | anytls      |               -1 | paired-marginal  | F1_new   |  0.033536 |  0.012821 |  0.053946 |            nan |             nan |           nan | False     |
| W       | anytls      |               -1 | paired-reference | F1_new   | -0.013053 | -0.040618 |  0.012186 |            nan |             nan |           nan | False     |
| W       | anytls      |                0 | paired-raw       | F1_new   |  0.319493 |  0.244382 |  0.404211 |            nan |             nan |           nan | False     |
| W       | anytls      |                0 | paired-group     | F1_new   |  0.125802 |  0.069712 |  0.185775 |            nan |             nan |           nan | False     |
| W       | anytls      |                0 | paired-cyclic    | F1_new   |  0.190520 |  0.134617 |  0.254507 |            nan |             nan |           nan | False     |
| W       | anytls      |                0 | paired-center    | F1_new   |  0.004644 | -0.008795 |  0.017496 |            nan |             nan |           nan | False     |
| W       | anytls      |                0 | paired-marginal  | F1_new   |  0.002915 | -0.009573 |  0.014549 |            nan |             nan |           nan | False     |
| W       | anytls      |                0 | paired-reference | F1_new   |  0.017287 |  0.000641 |  0.033692 |            nan |             nan |           nan | False     |
| W       | anytls      |                1 | paired-raw       | F1_new   |  0.517563 |  0.408038 |  0.623550 |            nan |             nan |           nan | False     |
| W       | anytls      |                1 | paired-group     | F1_new   |  0.139572 |  0.066463 |  0.202661 |            nan |             nan |           nan | False     |
| W       | anytls      |                1 | paired-cyclic    | F1_new   |  0.197424 |  0.117410 |  0.285413 |            nan |             nan |           nan | False     |
| W       | anytls      |                1 | paired-center    | F1_new   |  0.098857 |  0.043253 |  0.152594 |            nan |             nan |           nan | False     |
| W       | anytls      |                1 | paired-marginal  | F1_new   |  0.086183 |  0.047001 |  0.119688 |            nan |             nan |           nan | False     |
| W       | anytls      |                1 | paired-reference | F1_new   | -0.069666 | -0.136309 | -0.012819 |            nan |             nan |           nan | False     |
| W       | anytls      |                2 | paired-raw       | F1_new   |  0.390886 |  0.333779 |  0.461015 |            nan |             nan |           nan | False     |
| W       | anytls      |                2 | paired-group     | F1_new   |  0.237254 |  0.204795 |  0.271763 |            nan |             nan |           nan | False     |
| W       | anytls      |                2 | paired-cyclic    | F1_new   |  0.320984 |  0.275702 |  0.363674 |            nan |             nan |           nan | False     |
| W       | anytls      |                2 | paired-center    | F1_new   |  0.026590 | -0.027335 |  0.084842 |            nan |             nan |           nan | False     |
| W       | anytls      |                2 | paired-marginal  | F1_new   |  0.011511 | -0.021617 |  0.045478 |            nan |             nan |           nan | False     |
| W       | anytls      |                2 | paired-reference | F1_new   |  0.013221 | -0.020229 |  0.045549 |            nan |             nan |           nan | False     |
| W       | shadowsocks |               -1 | paired-cyclic    | F1_new   |  0.224465 |  0.169661 |  0.274423 |            nan |             nan |           nan | False     |
| W       | shadowsocks |               -1 | paired-center    | F1_new   |  0.027084 |  0.013240 |  0.041426 |            nan |             nan |           nan | False     |
| W       | shadowsocks |               -1 | paired-marginal  | F1_new   |  0.009057 | -0.001351 |  0.019209 |            nan |             nan |           nan | False     |
| W       | shadowsocks |               -1 | paired-reference | F1_new   | -0.021085 | -0.044631 |  0.002230 |            nan |             nan |           nan | False     |
| W       | shadowsocks |                0 | paired-raw       | F1_new   |  0.327868 |  0.245091 |  0.439978 |            nan |             nan |           nan | False     |
| W       | shadowsocks |                0 | paired-group     | F1_new   |  0.109947 |  0.070285 |  0.150315 |            nan |             nan |           nan | False     |
| W       | shadowsocks |                0 | paired-cyclic    | F1_new   |  0.150454 |  0.103433 |  0.201741 |            nan |             nan |           nan | False     |
| W       | shadowsocks |                0 | paired-center    | F1_new   |  0.035179 |  0.017622 |  0.054014 |            nan |             nan |           nan | False     |
| W       | shadowsocks |                0 | paired-marginal  | F1_new   |  0.006466 | -0.003351 |  0.016097 |            nan |             nan |           nan | False     |
| W       | shadowsocks |                0 | paired-reference | F1_new   |  0.006987 | -0.008598 |  0.034154 |            nan |             nan |           nan | False     |
| W       | shadowsocks |                1 | paired-raw       | F1_new   |  0.533916 |  0.357759 |  0.671273 |            nan |             nan |           nan | False     |
| W       | shadowsocks |                1 | paired-group     | F1_new   |  0.175942 |  0.081733 |  0.246632 |            nan |             nan |           nan | False     |
| W       | shadowsocks |                1 | paired-cyclic    | F1_new   |  0.205116 |  0.094667 |  0.285654 |            nan |             nan |           nan | False     |
| W       | shadowsocks |                1 | paired-center    | F1_new   |  0.027324 |  0.004113 |  0.065755 |            nan |             nan |           nan | False     |
| W       | shadowsocks |                1 | paired-marginal  | F1_new   |  0.007407 | -0.008877 |  0.027685 |            nan |             nan |           nan | False     |
| W       | shadowsocks |                1 | paired-reference | F1_new   | -0.043096 | -0.083512 | -0.003623 |            nan |             nan |           nan | False     |
| W       | shadowsocks |                2 | paired-raw       | F1_new   |  0.424348 |  0.359898 |  0.500872 |            nan |             nan |           nan | False     |
| W       | shadowsocks |                2 | paired-group     | F1_new   |  0.273450 |  0.215302 |  0.345145 |            nan |             nan |           nan | False     |
| W       | shadowsocks |                2 | paired-cyclic    | F1_new   |  0.317826 |  0.254620 |  0.392777 |            nan |             nan |           nan | False     |
| W       | shadowsocks |                2 | paired-center    | F1_new   |  0.018748 | -0.012556 |  0.047664 |            nan |             nan |           nan | False     |
| W       | shadowsocks |                2 | paired-marginal  | F1_new   |  0.013298 | -0.007449 |  0.032629 |            nan |             nan |           nan | False     |
| W       | shadowsocks |                2 | paired-reference | F1_new   | -0.027146 | -0.061470 |  0.004353 |            nan |             nan |           nan | False     |
| W       | trojan      |               -1 | paired-cyclic    | F1_new   |  0.137070 |  0.094958 |  0.184540 |            nan |             nan |           nan | False     |
| W       | trojan      |               -1 | paired-center    | F1_new   | -0.014773 | -0.037192 |  0.012175 |            nan |             nan |           nan | False     |
| W       | trojan      |               -1 | paired-marginal  | F1_new   | -0.001622 | -0.017389 |  0.015772 |            nan |             nan |           nan | False     |
| W       | trojan      |               -1 | paired-reference | F1_new   | -0.012482 | -0.040349 |  0.013133 |            nan |             nan |           nan | False     |
| W       | trojan      |                0 | paired-raw       | F1_new   |  0.438020 |  0.378173 |  0.494991 |            nan |             nan |           nan | False     |
| W       | trojan      |                0 | paired-group     | F1_new   |  0.017239 | -0.036472 |  0.075806 |            nan |             nan |           nan | False     |
| W       | trojan      |                0 | paired-cyclic    | F1_new   |  0.049462 | -0.015160 |  0.122713 |            nan |             nan |           nan | False     |
| W       | trojan      |                0 | paired-center    | F1_new   | -0.013038 | -0.030235 |  0.006078 |            nan |             nan |           nan | False     |
| W       | trojan      |                0 | paired-marginal  | F1_new   | -0.002041 | -0.013957 |  0.011514 |            nan |             nan |           nan | False     |
| W       | trojan      |                0 | paired-reference | F1_new   | -0.012002 | -0.047441 |  0.021045 |            nan |             nan |           nan | False     |
| W       | trojan      |                1 | paired-raw       | F1_new   |  0.528885 |  0.397815 |  0.638883 |            nan |             nan |           nan | False     |
| W       | trojan      |                1 | paired-group     | F1_new   |  0.094908 |  0.016881 |  0.171650 |            nan |             nan |           nan | False     |
| W       | trojan      |                1 | paired-cyclic    | F1_new   |  0.173003 |  0.086755 |  0.269773 |            nan |             nan |           nan | False     |
| W       | trojan      |                1 | paired-center    | F1_new   | -0.018451 | -0.070197 |  0.042656 |            nan |             nan |           nan | False     |
| W       | trojan      |                1 | paired-marginal  | F1_new   | -0.007543 | -0.051155 |  0.036051 |            nan |             nan |           nan | False     |
| W       | trojan      |                1 | paired-reference | F1_new   | -0.049148 | -0.111025 | -0.001288 |            nan |             nan |           nan | False     |
| W       | trojan      |                2 | paired-raw       | F1_new   |  0.339198 |  0.290251 |  0.391190 |            nan |             nan |           nan | False     |
| W       | trojan      |                2 | paired-group     | F1_new   |  0.160236 |  0.119647 |  0.211123 |            nan |             nan |           nan | False     |
| W       | trojan      |                2 | paired-cyclic    | F1_new   |  0.188744 |  0.139403 |  0.243021 |            nan |             nan |           nan | False     |
| W       | trojan      |                2 | paired-center    | F1_new   | -0.012831 | -0.050791 |  0.035138 |            nan |             nan |           nan | False     |
| W       | trojan      |                2 | paired-marginal  | F1_new   |  0.004719 | -0.012391 |  0.025470 |            nan |             nan |           nan | False     |
| W       | trojan      |                2 | paired-reference | F1_new   |  0.023705 | -0.003247 |  0.050693 |            nan |             nan |           nan | False     |
| W       | vless       |               -1 | paired-cyclic    | F1_new   |  0.167095 |  0.118974 |  0.210653 |            nan |             nan |           nan | False     |
| W       | vless       |               -1 | paired-center    | F1_new   |  0.000829 | -0.024424 |  0.025244 |            nan |             nan |           nan | False     |
| W       | vless       |               -1 | paired-marginal  | F1_new   | -0.001073 | -0.022289 |  0.018846 |            nan |             nan |           nan | False     |
| W       | vless       |               -1 | paired-reference | F1_new   | -0.012364 | -0.038489 |  0.012268 |            nan |             nan |           nan | False     |
| W       | vless       |                0 | paired-raw       | F1_new   |  0.216754 |  0.181739 |  0.255230 |            nan |             nan |           nan | False     |
| W       | vless       |                0 | paired-group     | F1_new   |  0.052004 |  0.013190 |  0.093330 |            nan |             nan |           nan | False     |
| W       | vless       |                0 | paired-cyclic    | F1_new   |  0.109685 |  0.059016 |  0.167493 |            nan |             nan |           nan | False     |
| W       | vless       |                0 | paired-center    | F1_new   |  0.004302 | -0.027833 |  0.035428 |            nan |             nan |           nan | False     |
| W       | vless       |                0 | paired-marginal  | F1_new   | -0.008497 | -0.027696 |  0.006211 |            nan |             nan |           nan | False     |
| W       | vless       |                0 | paired-reference | F1_new   | -0.013841 | -0.041500 |  0.009954 |            nan |             nan |           nan | False     |
| W       | vless       |                1 | paired-raw       | F1_new   |  0.484901 |  0.344626 |  0.603827 |            nan |             nan |           nan | False     |
| W       | vless       |                1 | paired-group     | F1_new   |  0.096031 |  0.029151 |  0.156948 |            nan |             nan |           nan | False     |
| W       | vless       |                1 | paired-cyclic    | F1_new   |  0.147639 |  0.068634 |  0.225999 |            nan |             nan |           nan | False     |
| W       | vless       |                1 | paired-center    | F1_new   |  0.006180 | -0.009481 |  0.019984 |            nan |             nan |           nan | False     |
| W       | vless       |                1 | paired-marginal  | F1_new   |  0.000293 | -0.015130 |  0.017248 |            nan |             nan |           nan | False     |
| W       | vless       |                1 | paired-reference | F1_new   |  0.011274 | -0.020357 |  0.049664 |            nan |             nan |           nan | False     |
| W       | vless       |                2 | paired-raw       | F1_new   |  0.333547 |  0.239858 |  0.405352 |            nan |             nan |           nan | False     |
| W       | vless       |                2 | paired-group     | F1_new   |  0.232998 |  0.119092 |  0.320273 |            nan |             nan |           nan | False     |
| W       | vless       |                2 | paired-cyclic    | F1_new   |  0.243962 |  0.129819 |  0.321969 |            nan |             nan |           nan | False     |
| W       | vless       |                2 | paired-center    | F1_new   | -0.007996 | -0.074588 |  0.053759 |            nan |             nan |           nan | False     |
| W       | vless       |                2 | paired-marginal  | F1_new   |  0.004986 | -0.051257 |  0.053108 |            nan |             nan |           nan | False     |
| W       | vless       |                2 | paired-reference | F1_new   | -0.034526 | -0.087053 |  0.010247 |            nan |             nan |           nan | False     |
| W       | vmess       |               -1 | paired-cyclic    | F1_new   |  0.111739 |  0.082854 |  0.146769 |            nan |             nan |           nan | False     |
| W       | vmess       |               -1 | paired-center    | F1_new   |  0.010305 | -0.019286 |  0.039662 |            nan |             nan |           nan | False     |
| W       | vmess       |               -1 | paired-marginal  | F1_new   |  0.017086 |  0.002200 |  0.034929 |            nan |             nan |           nan | False     |
| W       | vmess       |               -1 | paired-reference | F1_new   | -0.056578 | -0.100479 | -0.013881 |            nan |             nan |           nan | False     |
| W       | vmess       |                0 | paired-raw       | F1_new   |  0.544086 |  0.510267 |  0.582160 |            nan |             nan |           nan | False     |
| W       | vmess       |                0 | paired-group     | F1_new   |  0.087567 |  0.038631 |  0.140743 |            nan |             nan |           nan | False     |
| W       | vmess       |                0 | paired-cyclic    | F1_new   |  0.119694 |  0.062639 |  0.186863 |            nan |             nan |           nan | False     |
| W       | vmess       |                0 | paired-center    | F1_new   |  0.003975 | -0.010648 |  0.019087 |            nan |             nan |           nan | False     |
| W       | vmess       |                0 | paired-marginal  | F1_new   |  0.043314 |  0.014666 |  0.076387 |            nan |             nan |           nan | False     |
| W       | vmess       |                0 | paired-reference | F1_new   |  0.007322 | -0.019282 |  0.034898 |            nan |             nan |           nan | False     |
| W       | vmess       |                1 | paired-raw       | F1_new   |  0.538920 |  0.463512 |  0.608057 |            nan |             nan |           nan | False     |
| W       | vmess       |                1 | paired-group     | F1_new   |  0.104499 |  0.061352 |  0.160271 |            nan |             nan |           nan | False     |
| W       | vmess       |                1 | paired-cyclic    | F1_new   |  0.154335 |  0.108685 |  0.223352 |            nan |             nan |           nan | False     |
| W       | vmess       |                1 | paired-center    | F1_new   |  0.099477 |  0.040473 |  0.156870 |            nan |             nan |           nan | False     |
| W       | vmess       |                1 | paired-marginal  | F1_new   |  0.015489 | -0.009084 |  0.045182 |            nan |             nan |           nan | False     |
| W       | vmess       |                1 | paired-reference | F1_new   | -0.112541 | -0.210697 | -0.021227 |            nan |             nan |           nan | False     |
| W       | vmess       |                2 | paired-raw       | F1_new   |  0.148193 |  0.062928 |  0.235220 |            nan |             nan |           nan | False     |
| W       | vmess       |                2 | paired-group     | F1_new   |  0.046396 | -0.001025 |  0.100188 |            nan |             nan |           nan | False     |
| W       | vmess       |                2 | paired-cyclic    | F1_new   |  0.061186 |  0.016328 |  0.105508 |            nan |             nan |           nan | False     |
| W       | vmess       |                2 | paired-center    | F1_new   | -0.072538 | -0.133941 | -0.013980 |            nan |             nan |           nan | False     |
| W       | vmess       |                2 | paired-marginal  | F1_new   | -0.007544 | -0.028670 |  0.021778 |            nan |             nan |           nan | False     |
| W       | vmess       |                2 | paired-reference | F1_new   | -0.064516 | -0.128710 | -0.000736 |            nan |             nan |           nan | False     |

## 概率指标对照区间

| track   | protocol    |   business_group | contrast         | metric      |     delta |     low95 |    high95 |   adjusted_low |   adjusted_high |   family_size | primary   |
|:--------|:------------|-----------------:|:-----------------|:------------|----------:|----------:|----------:|---------------:|----------------:|--------------:|:----------|
| T       | shadowsocks |               -1 | paired-raw       | CE_new_bits | -2.077990 | -2.247849 | -1.905635 |            nan |             nan |           nan | False     |
| T       | shadowsocks |               -1 | paired-raw       | Brier_new   | -0.611808 | -0.677093 | -0.545934 |            nan |             nan |           nan | False     |
| T       | shadowsocks |               -1 | paired-group     | CE_new_bits |  0.013098 | -0.214931 |  0.294154 |            nan |             nan |           nan | False     |
| T       | shadowsocks |               -1 | paired-group     | Brier_new   | -0.109218 | -0.148501 | -0.071447 |            nan |             nan |           nan | False     |
| T       | shadowsocks |               -1 | paired-cyclic    | CE_new_bits | -0.065523 | -0.306868 |  0.237217 |            nan |             nan |           nan | False     |
| T       | shadowsocks |               -1 | paired-cyclic    | Brier_new   | -0.148546 | -0.189534 | -0.108773 |            nan |             nan |           nan | False     |
| T       | shadowsocks |               -1 | paired-center    | CE_new_bits | -0.667891 | -0.818875 | -0.536931 |            nan |             nan |           nan | False     |
| T       | shadowsocks |               -1 | paired-center    | Brier_new   | -0.205938 | -0.240413 | -0.169479 |            nan |             nan |           nan | False     |
| T       | shadowsocks |               -1 | paired-marginal  | CE_new_bits |  0.011533 | -0.034489 |  0.050641 |            nan |             nan |           nan | False     |
| T       | shadowsocks |               -1 | paired-marginal  | Brier_new   |  0.033418 |  0.017075 |  0.050482 |            nan |             nan |           nan | False     |
| T       | shadowsocks |               -1 | paired-reference | CE_new_bits |  0.211299 |  0.156594 |  0.265829 |            nan |             nan |           nan | False     |
| T       | shadowsocks |               -1 | paired-reference | Brier_new   |  0.112821 |  0.088620 |  0.138463 |            nan |             nan |           nan | False     |
| T       | trojan      |               -1 | paired-raw       | CE_new_bits | -5.368294 | -5.712385 | -5.053971 |            nan |             nan |           nan | False     |
| T       | trojan      |               -1 | paired-raw       | Brier_new   | -1.042562 | -1.103669 | -0.980042 |            nan |             nan |           nan | False     |
| T       | trojan      |               -1 | paired-group     | CE_new_bits | -0.345139 | -0.450897 | -0.244535 |            nan |             nan |           nan | False     |
| T       | trojan      |               -1 | paired-group     | Brier_new   | -0.126535 | -0.166201 | -0.087244 |            nan |             nan |           nan | False     |
| T       | trojan      |               -1 | paired-cyclic    | CE_new_bits | -0.467956 | -0.591158 | -0.352809 |            nan |             nan |           nan | False     |
| T       | trojan      |               -1 | paired-cyclic    | Brier_new   | -0.170611 | -0.212389 | -0.130094 |            nan |             nan |           nan | False     |
| T       | trojan      |               -1 | paired-center    | CE_new_bits | -0.602475 | -0.702552 | -0.499934 |            nan |             nan |           nan | False     |
| T       | trojan      |               -1 | paired-center    | Brier_new   | -0.182379 | -0.215809 | -0.148200 |            nan |             nan |           nan | False     |
| T       | trojan      |               -1 | paired-marginal  | CE_new_bits | -0.024681 | -0.045956 | -0.002999 |            nan |             nan |           nan | False     |
| T       | trojan      |               -1 | paired-marginal  | Brier_new   | -0.007384 | -0.018408 |  0.003436 |            nan |             nan |           nan | False     |
| T       | trojan      |               -1 | paired-reference | CE_new_bits |  0.220409 |  0.132354 |  0.334229 |            nan |             nan |           nan | False     |
| T       | trojan      |               -1 | paired-reference | Brier_new   |  0.085129 |  0.064808 |  0.106513 |            nan |             nan |           nan | False     |
| T       | vless       |               -1 | paired-raw       | CE_new_bits | -5.524474 | -5.972380 | -5.074600 |            nan |             nan |           nan | False     |
| T       | vless       |               -1 | paired-raw       | Brier_new   | -1.002519 | -1.089011 | -0.909866 |            nan |             nan |           nan | False     |
| T       | vless       |               -1 | paired-group     | CE_new_bits | -0.030340 | -0.234086 |  0.195756 |            nan |             nan |           nan | False     |
| T       | vless       |               -1 | paired-group     | Brier_new   | -0.061466 | -0.109036 | -0.008557 |            nan |             nan |           nan | False     |
| T       | vless       |               -1 | paired-cyclic    | CE_new_bits | -0.136438 | -0.362116 |  0.114493 |            nan |             nan |           nan | False     |
| T       | vless       |               -1 | paired-cyclic    | Brier_new   | -0.101102 | -0.155857 | -0.038572 |            nan |             nan |           nan | False     |
| T       | vless       |               -1 | paired-center    | CE_new_bits | -0.828902 | -0.977078 | -0.691995 |            nan |             nan |           nan | False     |
| T       | vless       |               -1 | paired-center    | Brier_new   | -0.242654 | -0.286045 | -0.200008 |            nan |             nan |           nan | False     |
| T       | vless       |               -1 | paired-marginal  | CE_new_bits | -0.003645 | -0.059516 |  0.051144 |            nan |             nan |           nan | False     |
| T       | vless       |               -1 | paired-marginal  | Brier_new   | -0.007174 | -0.018269 |  0.003018 |            nan |             nan |           nan | False     |
| T       | vless       |               -1 | paired-reference | CE_new_bits |  0.219927 |  0.157492 |  0.282895 |            nan |             nan |           nan | False     |
| T       | vless       |               -1 | paired-reference | Brier_new   |  0.088145 |  0.061160 |  0.114493 |            nan |             nan |           nan | False     |
| T       | vmess       |               -1 | paired-raw       | CE_new_bits | -7.860767 | -8.368783 | -7.371972 |            nan |             nan |           nan | False     |
| T       | vmess       |               -1 | paired-raw       | Brier_new   | -0.995958 | -1.066979 | -0.923959 |            nan |             nan |           nan | False     |
| T       | vmess       |               -1 | paired-group     | CE_new_bits | -0.132115 | -0.313281 |  0.059780 |            nan |             nan |           nan | False     |
| T       | vmess       |               -1 | paired-group     | Brier_new   | -0.087326 | -0.119581 | -0.056215 |            nan |             nan |           nan | False     |
| T       | vmess       |               -1 | paired-cyclic    | CE_new_bits | -0.247673 | -0.457677 | -0.023782 |            nan |             nan |           nan | False     |
| T       | vmess       |               -1 | paired-cyclic    | Brier_new   | -0.134337 | -0.178005 | -0.091924 |            nan |             nan |           nan | False     |
| T       | vmess       |               -1 | paired-center    | CE_new_bits | -0.524755 | -0.637047 | -0.407354 |            nan |             nan |           nan | False     |
| T       | vmess       |               -1 | paired-center    | Brier_new   | -0.145161 | -0.172644 | -0.116446 |            nan |             nan |           nan | False     |
| T       | vmess       |               -1 | paired-marginal  | CE_new_bits |  0.037704 | -0.015343 |  0.097514 |            nan |             nan |           nan | False     |
| T       | vmess       |               -1 | paired-marginal  | Brier_new   |  0.019240 |  0.010136 |  0.028227 |            nan |             nan |           nan | False     |
| T       | vmess       |               -1 | paired-reference | CE_new_bits |  0.296238 |  0.217024 |  0.378015 |            nan |             nan |           nan | False     |
| T       | vmess       |               -1 | paired-reference | Brier_new   |  0.098130 |  0.073505 |  0.122021 |            nan |             nan |           nan | False     |
| W       | anytls      |               -1 | paired-raw       | CE_new_bits | -2.248268 | -2.613046 | -1.932189 |            nan |             nan |           nan | False     |
| W       | anytls      |               -1 | paired-raw       | Brier_new   | -0.476133 | -0.541611 | -0.407560 |            nan |             nan |           nan | False     |
| W       | anytls      |               -1 | paired-group     | CE_new_bits |  0.137610 | -0.255316 |  0.612458 |            nan |             nan |           nan | False     |
| W       | anytls      |               -1 | paired-group     | Brier_new   | -0.131096 | -0.155747 | -0.103023 |            nan |             nan |           nan | False     |
| W       | anytls      |               -1 | paired-cyclic    | CE_new_bits |  0.100064 | -0.324089 |  0.598472 |            nan |             nan |           nan | False     |
| W       | anytls      |               -1 | paired-cyclic    | Brier_new   | -0.158561 | -0.185769 | -0.127972 |            nan |             nan |           nan | False     |
| W       | anytls      |               -1 | paired-center    | CE_new_bits | -0.089072 | -0.257039 |  0.045938 |            nan |             nan |           nan | False     |
| W       | anytls      |               -1 | paired-center    | Brier_new   | -0.031144 | -0.057570 | -0.007464 |            nan |             nan |           nan | False     |
| W       | anytls      |               -1 | paired-marginal  | CE_new_bits |  0.072577 | -0.021080 |  0.173921 |            nan |             nan |           nan | False     |
| W       | anytls      |               -1 | paired-marginal  | Brier_new   | -0.021560 | -0.032802 | -0.010322 |            nan |             nan |           nan | False     |
| W       | anytls      |               -1 | paired-reference | CE_new_bits | -0.094044 | -0.275403 |  0.069909 |            nan |             nan |           nan | False     |
| W       | anytls      |               -1 | paired-reference | Brier_new   |  0.039844 |  0.018162 |  0.062225 |            nan |             nan |           nan | False     |
| W       | shadowsocks |               -1 | paired-raw       | CE_new_bits | -2.602222 | -2.877334 | -2.335823 |            nan |             nan |           nan | False     |
| W       | shadowsocks |               -1 | paired-raw       | Brier_new   | -0.609297 | -0.665992 | -0.554971 |            nan |             nan |           nan | False     |
| W       | shadowsocks |               -1 | paired-group     | CE_new_bits | -0.283078 | -0.411628 | -0.150009 |            nan |             nan |           nan | False     |
| W       | shadowsocks |               -1 | paired-group     | Brier_new   | -0.145929 | -0.177435 | -0.112866 |            nan |             nan |           nan | False     |
| W       | shadowsocks |               -1 | paired-cyclic    | CE_new_bits | -0.352337 | -0.512086 | -0.182308 |            nan |             nan |           nan | False     |
| W       | shadowsocks |               -1 | paired-cyclic    | Brier_new   | -0.173553 | -0.208466 | -0.136910 |            nan |             nan |           nan | False     |
| W       | shadowsocks |               -1 | paired-center    | CE_new_bits | -0.061255 | -0.188927 |  0.073180 |            nan |             nan |           nan | False     |
| W       | shadowsocks |               -1 | paired-center    | Brier_new   | -0.028013 | -0.047627 | -0.009111 |            nan |             nan |           nan | False     |
| W       | shadowsocks |               -1 | paired-marginal  | CE_new_bits |  0.014308 | -0.047226 |  0.110783 |            nan |             nan |           nan | False     |
| W       | shadowsocks |               -1 | paired-marginal  | Brier_new   | -0.014081 | -0.023120 | -0.004461 |            nan |             nan |           nan | False     |
| W       | shadowsocks |               -1 | paired-reference | CE_new_bits |  0.084327 |  0.004740 |  0.163741 |            nan |             nan |           nan | False     |
| W       | shadowsocks |               -1 | paired-reference | Brier_new   |  0.038054 |  0.023478 |  0.051618 |            nan |             nan |           nan | False     |
| W       | trojan      |               -1 | paired-raw       | CE_new_bits | -2.040016 | -2.365778 | -1.727898 |            nan |             nan |           nan | False     |
| W       | trojan      |               -1 | paired-raw       | Brier_new   | -0.503935 | -0.554195 | -0.456610 |            nan |             nan |           nan | False     |
| W       | trojan      |               -1 | paired-group     | CE_new_bits | -0.115466 | -0.261222 |  0.048229 |            nan |             nan |           nan | False     |
| W       | trojan      |               -1 | paired-group     | Brier_new   | -0.100548 | -0.129360 | -0.073073 |            nan |             nan |           nan | False     |
| W       | trojan      |               -1 | paired-cyclic    | CE_new_bits | -0.213426 | -0.369797 | -0.035563 |            nan |             nan |           nan | False     |
| W       | trojan      |               -1 | paired-cyclic    | Brier_new   | -0.137176 | -0.172238 | -0.104354 |            nan |             nan |           nan | False     |
| W       | trojan      |               -1 | paired-center    | CE_new_bits | -0.044585 | -0.126422 |  0.029510 |            nan |             nan |           nan | False     |
| W       | trojan      |               -1 | paired-center    | Brier_new   |  0.004977 | -0.014161 |  0.023424 |            nan |             nan |           nan | False     |
| W       | trojan      |               -1 | paired-marginal  | CE_new_bits | -0.021663 | -0.055245 |  0.011541 |            nan |             nan |           nan | False     |
| W       | trojan      |               -1 | paired-marginal  | Brier_new   | -0.005948 | -0.015386 |  0.004292 |            nan |             nan |           nan | False     |
| W       | trojan      |               -1 | paired-reference | CE_new_bits |  0.079428 |  0.008341 |  0.157079 |            nan |             nan |           nan | False     |
| W       | trojan      |               -1 | paired-reference | Brier_new   |  0.019410 | -0.000305 |  0.040718 |            nan |             nan |           nan | False     |
| W       | vless       |               -1 | paired-raw       | CE_new_bits | -1.558273 | -1.918746 | -1.158328 |            nan |             nan |           nan | False     |
| W       | vless       |               -1 | paired-raw       | Brier_new   | -0.399483 | -0.449683 | -0.348064 |            nan |             nan |           nan | False     |
| W       | vless       |               -1 | paired-group     | CE_new_bits |  0.011277 | -0.218250 |  0.260094 |            nan |             nan |           nan | False     |
| W       | vless       |               -1 | paired-group     | Brier_new   | -0.109741 | -0.145754 | -0.072562 |            nan |             nan |           nan | False     |
| W       | vless       |               -1 | paired-cyclic    | CE_new_bits | -0.060481 | -0.308445 |  0.213119 |            nan |             nan |           nan | False     |
| W       | vless       |               -1 | paired-cyclic    | Brier_new   | -0.141638 | -0.181428 | -0.098750 |            nan |             nan |           nan | False     |
| W       | vless       |               -1 | paired-center    | CE_new_bits | -0.032846 | -0.156279 |  0.083995 |            nan |             nan |           nan | False     |
| W       | vless       |               -1 | paired-center    | Brier_new   |  0.003022 | -0.022314 |  0.026680 |            nan |             nan |           nan | False     |
| W       | vless       |               -1 | paired-marginal  | CE_new_bits |  0.010213 | -0.030154 |  0.053549 |            nan |             nan |           nan | False     |
| W       | vless       |               -1 | paired-marginal  | Brier_new   | -0.006270 | -0.016795 |  0.004133 |            nan |             nan |           nan | False     |
| W       | vless       |               -1 | paired-reference | CE_new_bits | -0.072110 | -0.214629 |  0.054900 |            nan |             nan |           nan | False     |
| W       | vless       |               -1 | paired-reference | Brier_new   |  0.033567 |  0.012549 |  0.053304 |            nan |             nan |           nan | False     |
| W       | vmess       |               -1 | paired-raw       | CE_new_bits | -2.708384 | -2.997200 | -2.444249 |            nan |             nan |           nan | False     |
| W       | vmess       |               -1 | paired-raw       | Brier_new   | -0.613031 | -0.663639 | -0.564238 |            nan |             nan |           nan | False     |
| W       | vmess       |               -1 | paired-group     | CE_new_bits | -0.062245 | -0.296341 |  0.244964 |            nan |             nan |           nan | False     |
| W       | vmess       |               -1 | paired-group     | Brier_new   | -0.106174 | -0.138294 | -0.073713 |            nan |             nan |           nan | False     |
| W       | vmess       |               -1 | paired-cyclic    | CE_new_bits | -0.132986 | -0.383257 |  0.196698 |            nan |             nan |           nan | False     |
| W       | vmess       |               -1 | paired-cyclic    | Brier_new   | -0.138074 | -0.172333 | -0.103571 |            nan |             nan |           nan | False     |
| W       | vmess       |               -1 | paired-center    | CE_new_bits | -0.159356 | -0.278455 | -0.058558 |            nan |             nan |           nan | False     |
| W       | vmess       |               -1 | paired-center    | Brier_new   | -0.031109 | -0.054660 | -0.010059 |            nan |             nan |           nan | False     |
| W       | vmess       |               -1 | paired-marginal  | CE_new_bits | -0.058677 | -0.126696 | -0.004577 |            nan |             nan |           nan | False     |
| W       | vmess       |               -1 | paired-marginal  | Brier_new   | -0.025518 | -0.043786 | -0.010839 |            nan |             nan |           nan | False     |
| W       | vmess       |               -1 | paired-reference | CE_new_bits |  0.035426 | -0.092702 |  0.147664 |            nan |             nan |           nan | False     |
| W       | vmess       |               -1 | paired-reference | Brier_new   |  0.049076 |  0.029860 |  0.068522 |            nan |             nan |           nan | False     |

## 命名业务组

| track   | protocol    |   business_group | arm       |   F1_new |   F1_all |   BA_all |   CE_all_bits |   Brier_all |   CE_new_bits |   Brier_new | 新增业务组                     |
|:--------|:------------|-----------------:|:----------|---------:|---------:|---------:|--------------:|------------:|--------------:|------------:|:-------------------------------|
| T       | shadowsocks |                0 | center    | 0.699719 | 0.699932 | 0.703819 |      1.420102 |    0.430068 |      1.710915 |    0.568053 | GitHub 仓库浏览 + YouTube 搜索 |
| T       | shadowsocks |                0 | cyclic    | 0.738945 | 0.689657 | 0.689931 |      1.310826 |    0.443800 |      1.125107 |    0.404624 | GitHub 仓库浏览 + YouTube 搜索 |
| T       | shadowsocks |                0 | group     | 0.740966 | 0.689413 | 0.688889 |      1.300443 |    0.432773 |      1.079781 |    0.384246 | GitHub 仓库浏览 + YouTube 搜索 |
| T       | shadowsocks |                0 | marginal  | 0.804395 | 0.732242 | 0.730556 |      1.336818 |    0.395153 |      1.167184 |    0.363154 | GitHub 仓库浏览 + YouTube 搜索 |
| T       | shadowsocks |                0 | paired    | 0.808342 | 0.734789 | 0.734028 |      1.354471 |    0.398072 |      1.135439 |    0.341269 | GitHub 仓库浏览 + YouTube 搜索 |
| T       | shadowsocks |                0 | raw       | 0.472878 | 0.577306 | 0.618750 |      1.817917 |    0.564916 |      2.983749 |    0.920278 | GitHub 仓库浏览 + YouTube 搜索 |
| T       | shadowsocks |                0 | reference | 0.844630 | 0.741175 | 0.740278 |      1.363532 |    0.383823 |      1.065125 |    0.302244 | GitHub 仓库浏览 + YouTube 搜索 |
| T       | shadowsocks |                1 | center    | 0.519640 | 0.615141 | 0.641667 |      1.746336 |    0.522969 |      2.145247 |    0.699510 | Bing 搜索 + Wikipedia 文章     |
| T       | shadowsocks |                1 | cyclic    | 0.444345 | 0.613863 | 0.637500 |      1.363731 |    0.498868 |      1.837182 |    0.777255 | Bing 搜索 + Wikipedia 文章     |
| T       | shadowsocks |                1 | group     | 0.473981 | 0.627568 | 0.648958 |      1.324124 |    0.473297 |      1.690594 |    0.717001 | Bing 搜索 + Wikipedia 文章     |
| T       | shadowsocks |                1 | marginal  | 0.679936 | 0.718129 | 0.717014 |      1.420827 |    0.410435 |      1.391494 |    0.472190 | Bing 搜索 + Wikipedia 文章     |
| T       | shadowsocks |                1 | paired    | 0.587350 | 0.691802 | 0.701736 |      1.374508 |    0.406884 |      1.385646 |    0.546446 | Bing 搜索 + Wikipedia 文章     |
| T       | shadowsocks |                1 | raw       | 0.325813 | 0.584751 | 0.637500 |      2.148436 |    0.608132 |      3.915583 |    1.242174 | Bing 搜索 + Wikipedia 文章     |
| T       | shadowsocks |                1 | reference | 0.719770 | 0.729405 | 0.728472 |      1.369098 |    0.380626 |      0.999347 |    0.367210 | Bing 搜索 + Wikipedia 文章     |
| T       | shadowsocks |                2 | center    | 0.459866 | 0.649582 | 0.679167 |      1.556819 |    0.464446 |      2.619037 |    0.804186 | MDN 文档 + YouTube 视频播放    |
| T       | shadowsocks |                2 | cyclic    | 0.445308 | 0.654404 | 0.675000 |      1.240676 |    0.453921 |      1.705804 |    0.717696 | MDN 文档 + YouTube 视频播放    |
| T       | shadowsocks |                2 | group     | 0.474697 | 0.662727 | 0.678125 |      1.225704 |    0.442236 |      1.661855 |    0.680345 | MDN 文档 + YouTube 视频播放    |
| T       | shadowsocks |                2 | marginal  | 0.624629 | 0.729840 | 0.730903 |      1.315015 |    0.386773 |      1.878248 |    0.518338 | MDN 文档 + YouTube 视频播放    |
| T       | shadowsocks |                2 | paired    | 0.594539 | 0.724243 | 0.730208 |      1.319138 |    0.391556 |      1.950441 |    0.566221 | MDN 文档 + YouTube 视频播放    |
| T       | shadowsocks |                2 | raw       | 0.268081 | 0.589513 | 0.647222 |      1.782047 |    0.526219 |      3.806162 |    1.126908 | MDN 文档 + YouTube 视频播放    |
| T       | shadowsocks |                2 | reference | 0.639204 | 0.736447 | 0.735417 |      1.296295 |    0.373104 |      1.773156 |    0.446021 | MDN 文档 + YouTube 视频播放    |
| T       | trojan      |                0 | center    | 0.800097 | 0.704308 | 0.714236 |      1.067091 |    0.398097 |      0.855423 |    0.325849 | GitHub 仓库浏览 + YouTube 搜索 |
| T       | trojan      |                0 | cyclic    | 0.747993 | 0.694152 | 0.701389 |      1.208581 |    0.446746 |      1.129856 |    0.423957 | GitHub 仓库浏览 + YouTube 搜索 |
| T       | trojan      |                0 | group     | 0.782720 | 0.707154 | 0.712500 |      1.148486 |    0.428668 |      0.997791 |    0.369447 | GitHub 仓库浏览 + YouTube 搜索 |
| T       | trojan      |                0 | marginal  | 0.827333 | 0.754101 | 0.756944 |      0.981778 |    0.366519 |      0.722742 |    0.267303 | GitHub 仓库浏览 + YouTube 搜索 |
| T       | trojan      |                0 | paired    | 0.835492 | 0.771878 | 0.772917 |      0.946901 |    0.354333 |      0.680091 |    0.250681 | GitHub 仓库浏览 + YouTube 搜索 |
| T       | trojan      |                0 | raw       | 0.007666 | 0.355136 | 0.445833 |      2.747830 |    0.812081 |      5.976698 |    1.562659 | GitHub 仓库浏览 + YouTube 搜索 |
| T       | trojan      |                0 | reference | 0.832821 | 0.783503 | 0.784722 |      0.891653 |    0.331550 |      0.601985 |    0.212269 | GitHub 仓库浏览 + YouTube 搜索 |
| T       | trojan      |                1 | center    | 0.255135 | 0.590617 | 0.651736 |      1.503233 |    0.512670 |      3.403791 |    1.106870 | Bing 搜索 + Wikipedia 文章     |
| T       | trojan      |                1 | cyclic    | 0.277013 | 0.601211 | 0.638194 |      1.431956 |    0.505788 |      2.644790 |    0.951532 | Bing 搜索 + Wikipedia 文章     |
| T       | trojan      |                1 | group     | 0.325188 | 0.625398 | 0.655208 |      1.361606 |    0.487664 |      2.489065 |    0.912735 | Bing 搜索 + Wikipedia 文章     |
| T       | trojan      |                1 | marginal  | 0.527375 | 0.701948 | 0.713889 |      1.063921 |    0.398702 |      1.972976 |    0.730559 | Bing 搜索 + Wikipedia 文章     |
| T       | trojan      |                1 | paired    | 0.544925 | 0.712326 | 0.722917 |      1.028652 |    0.383171 |      1.912517 |    0.711605 | Bing 搜索 + Wikipedia 文章     |
| T       | trojan      |                1 | raw       | 0.047344 | 0.496108 | 0.591667 |      3.043510 |    0.625689 |      8.105148 |    1.494607 | Bing 搜索 + Wikipedia 文章     |
| T       | trojan      |                1 | reference | 0.687904 | 0.769301 | 0.771181 |      0.884118 |    0.331215 |      1.326175 |    0.505844 | Bing 搜索 + Wikipedia 文章     |
| T       | trojan      |                2 | center    | 0.712096 | 0.700713 | 0.715625 |      1.103023 |    0.404177 |      0.891276 |    0.366553 | MDN 文档 + YouTube 视频播放    |
| T       | trojan      |                2 | cyclic    | 0.731693 | 0.709831 | 0.710069 |      1.183575 |    0.433631 |      0.972285 |    0.388480 | MDN 文档 + YouTube 视频播放    |
| T       | trojan      |                2 | group     | 0.749034 | 0.716970 | 0.719097 |      1.136273 |    0.418381 |      0.891624 |    0.349555 | MDN 文档 + YouTube 视频播放    |
| T       | trojan      |                2 | marginal  | 0.766667 | 0.747400 | 0.751736 |      0.960028 |    0.357164 |      0.721391 |    0.276424 | MDN 文档 + YouTube 视频播放    |
| T       | trojan      |                2 | paired    | 0.790752 | 0.771489 | 0.772917 |      0.920961 |    0.340590 |      0.750456 |    0.289847 | MDN 文档 + YouTube 视频播放    |
| T       | trojan      |                2 | raw       | 0.161593 | 0.497161 | 0.559375 |      2.450087 |    0.661738 |      5.366098 |    1.322554 | MDN 文档 + YouTube 视频播放    |
| T       | trojan      |                2 | reference | 0.794616 | 0.776975 | 0.778125 |      0.881997 |    0.327964 |      0.753676 |    0.278634 | MDN 文档 + YouTube 视频播放    |
| T       | vless       |                0 | center    | 0.670357 | 0.663788 | 0.671181 |      1.663914 |    0.501580 |      1.824602 |    0.597860 | GitHub 仓库浏览 + YouTube 搜索 |
| T       | vless       |                0 | cyclic    | 0.725209 | 0.687632 | 0.693056 |      1.516389 |    0.496233 |      1.187355 |    0.451724 | GitHub 仓库浏览 + YouTube 搜索 |
| T       | vless       |                0 | group     | 0.765820 | 0.715292 | 0.718403 |      1.470414 |    0.472875 |      1.086261 |    0.406386 | GitHub 仓库浏览 + YouTube 搜索 |
| T       | vless       |                0 | marginal  | 0.778324 | 0.731316 | 0.732639 |      1.492559 |    0.447973 |      1.263316 |    0.447206 | GitHub 仓库浏览 + YouTube 搜索 |
| T       | vless       |                0 | paired    | 0.801245 | 0.745447 | 0.746181 |      1.482075 |    0.436700 |      1.165778 |    0.409009 | GitHub 仓库浏览 + YouTube 搜索 |
| T       | vless       |                0 | raw       | 0.089044 | 0.418417 | 0.488542 |      3.589346 |    0.836895 |      7.816458 |    1.599032 | GitHub 仓库浏览 + YouTube 搜索 |
| T       | vless       |                0 | reference | 0.799895 | 0.745639 | 0.746528 |      1.477464 |    0.422761 |      1.078340 |    0.362798 | GitHub 仓库浏览 + YouTube 搜索 |
| T       | vless       |                1 | center    | 0.225931 | 0.510765 | 0.570139 |      2.116758 |    0.623411 |      4.232930 |    1.106895 | Bing 搜索 + Wikipedia 文章     |
| T       | vless       |                1 | cyclic    | 0.306003 | 0.585545 | 0.627778 |      1.650135 |    0.536195 |      3.125554 |    0.922292 | Bing 搜索 + Wikipedia 文章     |
| T       | vless       |                1 | group     | 0.357050 | 0.608588 | 0.642361 |      1.606842 |    0.524495 |      3.006959 |    0.900207 | Bing 搜索 + Wikipedia 文章     |
| T       | vless       |                1 | marginal  | 0.576779 | 0.690357 | 0.700347 |      1.569934 |    0.479219 |      2.745512 |    0.744597 | Bing 搜索 + Wikipedia 文章     |
| T       | vless       |                1 | paired    | 0.593490 | 0.703746 | 0.713542 |      1.565551 |    0.472274 |      2.778034 |    0.752724 | Bing 搜索 + Wikipedia 文章     |
| T       | vless       |                1 | raw       | 0.034089 | 0.426773 | 0.519097 |      3.276217 |    0.717388 |      7.970376 |    1.485484 | Bing 搜索 + Wikipedia 文章     |
| T       | vless       |                1 | reference | 0.683373 | 0.728670 | 0.729514 |      1.464519 |    0.422669 |      2.185057 |    0.527115 | Bing 搜索 + Wikipedia 文章     |
| T       | vless       |                2 | center    | 0.559404 | 0.626747 | 0.641667 |      1.741746 |    0.524724 |      1.499077 |    0.553238 | MDN 文档 + YouTube 视频播放    |
| T       | vless       |                2 | cyclic    | 0.644956 | 0.671967 | 0.674306 |      1.516142 |    0.499323 |      1.166310 |    0.459323 | MDN 文档 + YouTube 视频播放    |
| T       | vless       |                2 | group     | 0.688890 | 0.698960 | 0.700694 |      1.487750 |    0.481249 |      1.067706 |    0.407838 | MDN 文档 + YouTube 视频播放    |
| T       | vless       |                2 | marginal  | 0.730697 | 0.730954 | 0.732986 |      1.524190 |    0.444868 |      1.072014 |    0.359753 | MDN 文档 + YouTube 视频播放    |
| T       | vless       |                2 | paired    | 0.729670 | 0.739142 | 0.740278 |      1.524039 |    0.441228 |      1.126094 |    0.368299 | MDN 文档 + YouTube 视频播放    |
| T       | vless       |                2 | raw       | 0.083669 | 0.448790 | 0.517708 |      2.877067 |    0.740862 |      5.856492 |    1.453074 | MDN 文档 + YouTube 视频播放    |
| T       | vless       |                2 | reference | 0.719850 | 0.733989 | 0.735069 |      1.493719 |    0.422933 |      1.146726 |    0.375686 | MDN 文档 + YouTube 视频播放    |
| T       | vmess       |                0 | center    | 0.782124 | 0.687805 | 0.690972 |      1.410553 |    0.468835 |      1.434098 |    0.437387 | GitHub 仓库浏览 + YouTube 搜索 |
| T       | vmess       |                0 | cyclic    | 0.689522 | 0.626521 | 0.632639 |      1.397832 |    0.513931 |      1.186065 |    0.458423 | GitHub 仓库浏览 + YouTube 搜索 |
| T       | vmess       |                0 | group     | 0.750057 | 0.653727 | 0.660417 |      1.319482 |    0.483481 |      1.027368 |    0.387975 | GitHub 仓库浏览 + YouTube 搜索 |
| T       | vmess       |                0 | marginal  | 0.822041 | 0.720971 | 0.724653 |      1.279083 |    0.428182 |      1.041910 |    0.327755 | GitHub 仓库浏览 + YouTube 搜索 |
| T       | vmess       |                0 | paired    | 0.818593 | 0.716764 | 0.720486 |      1.270059 |    0.424555 |      0.976552 |    0.306498 | GitHub 仓库浏览 + YouTube 搜索 |
| T       | vmess       |                0 | raw       | 0.053571 | 0.363253 | 0.423611 |      4.315522 |    0.894592 |     10.319447 |    1.639580 | GitHub 仓库浏览 + YouTube 搜索 |
| T       | vmess       |                0 | reference | 0.824308 | 0.720050 | 0.724306 |      1.234457 |    0.408927 |      0.832811 |    0.245563 | GitHub 仓库浏览 + YouTube 搜索 |
| T       | vmess       |                1 | center    | 0.286369 | 0.571890 | 0.622222 |      1.709114 |    0.537228 |      3.244038 |    0.976953 | Bing 搜索 + Wikipedia 文章     |
| T       | vmess       |                1 | cyclic    | 0.256898 | 0.572156 | 0.613194 |      1.544862 |    0.533173 |      2.936299 |    0.981824 | Bing 搜索 + Wikipedia 文章     |
| T       | vmess       |                1 | group     | 0.303167 | 0.596960 | 0.632986 |      1.492491 |    0.513827 |      2.818565 |    0.943827 | Bing 搜索 + Wikipedia 文章     |
| T       | vmess       |                1 | marginal  | 0.496226 | 0.670888 | 0.691667 |      1.364461 |    0.443471 |      2.300381 |    0.738105 | Bing 搜索 + Wikipedia 文章     |
| T       | vmess       |                1 | paired    | 0.471626 | 0.659805 | 0.679861 |      1.373553 |    0.447613 |      2.422351 |    0.796110 | Bing 搜索 + Wikipedia 文章     |
| T       | vmess       |                1 | raw       | 0.079678 | 0.495660 | 0.576736 |      4.216033 |    0.645873 |     11.007513 |    1.423600 | Bing 搜索 + Wikipedia 文章     |
| T       | vmess       |                1 | reference | 0.614435 | 0.716124 | 0.721528 |      1.225703 |    0.411223 |      1.691279 |    0.576000 | Bing 搜索 + Wikipedia 文章     |
| T       | vmess       |                2 | center    | 0.596433 | 0.636224 | 0.652431 |      1.469237 |    0.489522 |      1.505617 |    0.549114 | MDN 文档 + YouTube 视频播放    |
| T       | vmess       |                2 | cyclic    | 0.650821 | 0.666765 | 0.668403 |      1.393693 |    0.492595 |      1.230142 |    0.490734 | MDN 文档 + YouTube 视频播放    |
| T       | vmess       |                2 | group     | 0.680103 | 0.685674 | 0.688542 |      1.349390 |    0.472035 |      1.159900 |    0.458145 | MDN 文档 + YouTube 视频播放    |
| T       | vmess       |                2 | marginal  | 0.694746 | 0.692920 | 0.699653 |      1.306210 |    0.432847 |      1.154084 |    0.404389 | MDN 文档 + YouTube 视频播放    |
| T       | vmess       |                2 | paired    | 0.709770 | 0.710945 | 0.716319 |      1.304063 |    0.426324 |      1.210584 |    0.425362 | MDN 文档 + YouTube 视频播放    |
| T       | vmess       |                2 | raw       | 0.145410 | 0.465702 | 0.526389 |      3.023523 |    0.739079 |      6.864828 |    1.452665 | MDN 文档 + YouTube 视频播放    |
| T       | vmess       |                2 | reference | 0.710309 | 0.719452 | 0.724306 |      1.247900 |    0.409392 |      1.196682 |    0.412017 | MDN 文档 + YouTube 视频播放    |
| W       | anytls      |                0 | center    | 0.883576 | 0.802325 | 0.809722 |      1.795190 |    0.345840 |      1.679169 |    0.225073 | GitHub 仓库浏览 + YouTube 搜索 |
| W       | anytls      |                0 | cyclic    | 0.697699 | 0.655304 | 0.671875 |      1.702814 |    0.505621 |      1.406316 |    0.491516 | GitHub 仓库浏览 + YouTube 搜索 |
| W       | anytls      |                0 | group     | 0.762417 | 0.692494 | 0.704861 |      1.671948 |    0.490789 |      1.347066 |    0.463187 | GitHub 仓库浏览 + YouTube 搜索 |
| W       | anytls      |                0 | marginal  | 0.885304 | 0.801825 | 0.807292 |      1.739543 |    0.371062 |      1.555555 |    0.265189 | GitHub 仓库浏览 + YouTube 搜索 |
| W       | anytls      |                0 | paired    | 0.888219 | 0.808644 | 0.812153 |      1.850371 |    0.370969 |      1.672151 |    0.265368 | GitHub 仓库浏览 + YouTube 搜索 |
| W       | anytls      |                0 | raw       | 0.568727 | 0.567167 | 0.603819 |      2.330410 |    0.517680 |      2.873239 |    0.620705 | GitHub 仓库浏览 + YouTube 搜索 |
| W       | anytls      |                0 | reference | 0.870933 | 0.800579 | 0.803472 |      1.920850 |    0.342779 |      1.885435 |    0.253885 | GitHub 仓库浏览 + YouTube 搜索 |
| W       | anytls      |                1 | center    | 0.566868 | 0.756385 | 0.778472 |      1.898124 |    0.362234 |      2.164803 |    0.682208 | Bing 搜索 + Wikipedia 文章     |
| W       | anytls      |                1 | cyclic    | 0.468302 | 0.687200 | 0.711806 |      1.793387 |    0.464862 |      1.848634 |    0.636234 | Bing 搜索 + Wikipedia 文章     |
| W       | anytls      |                1 | group     | 0.526154 | 0.715215 | 0.734028 |      1.783846 |    0.451839 |      1.870805 |    0.620597 | Bing 搜索 + Wikipedia 文章     |
| W       | anytls      |                1 | marginal  | 0.579543 | 0.760859 | 0.779861 |      1.802191 |    0.359377 |      1.820886 |    0.609418 | Bing 搜索 + Wikipedia 文章     |
| W       | anytls      |                1 | paired    | 0.665726 | 0.793676 | 0.799653 |      1.880521 |    0.347344 |      1.895928 |    0.561144 | Bing 搜索 + Wikipedia 文章     |
| W       | anytls      |                1 | raw       | 0.148163 | 0.519151 | 0.591319 |      2.965130 |    0.561219 |      5.194213 |    1.132869 | Bing 搜索 + Wikipedia 文章     |
| W       | anytls      |                1 | reference | 0.735392 | 0.809924 | 0.811458 |      2.022864 |    0.334526 |      2.023048 |    0.479321 | Bing 搜索 + Wikipedia 文章     |
| W       | anytls      |                2 | center    | 0.807490 | 0.795093 | 0.798264 |      1.687039 |    0.346938 |      1.583031 |    0.332379 | MDN 文档 + YouTube 视频播放    |
| W       | anytls      |                2 | cyclic    | 0.513095 | 0.658679 | 0.696528 |      1.578747 |    0.506333 |      1.604645 |    0.494162 | MDN 文档 + YouTube 视频播放    |
| W       | anytls      |                2 | group     | 0.596825 | 0.695820 | 0.716667 |      1.574250 |    0.491409 |      1.529087 |    0.455734 | MDN 文档 + YouTube 视频播放    |
| W       | anytls      |                2 | marginal  | 0.822568 | 0.809192 | 0.812500 |      1.638054 |    0.354395 |      1.565617 |    0.336302 | MDN 文档 + YouTube 视频播放    |
| W       | anytls      |                2 | paired    | 0.834079 | 0.819650 | 0.821528 |      1.708715 |    0.351539 |      1.591710 |    0.319717 | MDN 文档 + YouTube 视频播放    |
| W       | anytls      |                2 | raw       | 0.443193 | 0.549557 | 0.610417 |      2.554299 |    0.553396 |      3.837140 |    0.821055 | MDN 文档 + YouTube 视频播放    |
| W       | anytls      |                2 | reference | 0.820858 | 0.796500 | 0.800347 |      1.842741 |    0.340152 |      1.533437 |    0.293490 | MDN 文档 + YouTube 视频播放    |
| W       | shadowsocks |                0 | center    | 0.885381 | 0.792107 | 0.796875 |      1.004399 |    0.335757 |      0.983444 |    0.222384 | GitHub 仓库浏览 + YouTube 搜索 |
| W       | shadowsocks |                0 | cyclic    | 0.770106 | 0.675015 | 0.690972 |      1.305520 |    0.476532 |      1.368663 |    0.477141 | GitHub 仓库浏览 + YouTube 搜索 |
| W       | shadowsocks |                0 | group     | 0.810613 | 0.697112 | 0.710764 |      1.274883 |    0.460524 |      1.355763 |    0.446898 | GitHub 仓库浏览 + YouTube 搜索 |
| W       | shadowsocks |                0 | marginal  | 0.914094 | 0.807870 | 0.812847 |      0.989040 |    0.337728 |      0.943736 |    0.231577 | GitHub 仓库浏览 + YouTube 搜索 |
| W       | shadowsocks |                0 | paired    | 0.920560 | 0.809721 | 0.813194 |      1.034026 |    0.338612 |      1.114214 |    0.249800 | GitHub 仓库浏览 + YouTube 搜索 |
| W       | shadowsocks |                0 | raw       | 0.592691 | 0.569848 | 0.616667 |      1.470032 |    0.518965 |      1.984966 |    0.655409 | GitHub 仓库浏览 + YouTube 搜索 |
| W       | shadowsocks |                0 | reference | 0.913573 | 0.815462 | 0.817708 |      0.988181 |    0.320213 |      1.157718 |    0.252863 | GitHub 仓库浏览 + YouTube 搜索 |
| W       | shadowsocks |                1 | center    | 0.623880 | 0.775809 | 0.794097 |      1.183597 |    0.325311 |      1.447772 |    0.563826 | Bing 搜索 + Wikipedia 文章     |
| W       | shadowsocks |                1 | cyclic    | 0.446088 | 0.688459 | 0.726042 |      1.262728 |    0.428765 |      1.612217 |    0.610883 | Bing 搜索 + Wikipedia 文章     |
| W       | shadowsocks |                1 | group     | 0.475261 | 0.705510 | 0.739931 |      1.218064 |    0.410244 |      1.497442 |    0.587940 | Bing 搜索 + Wikipedia 文章     |
| W       | shadowsocks |                1 | marginal  | 0.643797 | 0.795143 | 0.811458 |      1.127813 |    0.319009 |      1.312612 |    0.536150 | Bing 搜索 + Wikipedia 文章     |
| W       | shadowsocks |                1 | paired    | 0.651203 | 0.796435 | 0.808681 |      1.129696 |    0.314519 |      1.241351 |    0.498995 | Bing 搜索 + Wikipedia 文章     |
| W       | shadowsocks |                1 | raw       | 0.117288 | 0.513888 | 0.596528 |      2.459789 |    0.598856 |      5.210876 |    1.363874 | Bing 搜索 + Wikipedia 文章     |
| W       | shadowsocks |                1 | reference | 0.694300 | 0.812252 | 0.815972 |      1.230688 |    0.304860 |      1.125286 |    0.462859 | Bing 搜索 + Wikipedia 文章     |
| W       | shadowsocks |                2 | center    | 0.773413 | 0.790175 | 0.792361 |      1.121778 |    0.343925 |      0.953400 |    0.381675 | MDN 文档 + YouTube 视频播放    |
| W       | shadowsocks |                2 | cyclic    | 0.474335 | 0.649098 | 0.684722 |      1.430836 |    0.522872 |      1.276983 |    0.516482 | MDN 文档 + YouTube 视频播放    |
| W       | shadowsocks |                2 | group     | 0.518711 | 0.647986 | 0.676042 |      1.405748 |    0.508152 |      1.196881 |    0.486795 | MDN 文档 + YouTube 视频播放    |
| W       | shadowsocks |                2 | marginal  | 0.778863 | 0.792529 | 0.795833 |      1.089887 |    0.348274 |      0.901579 |    0.358361 | MDN 文档 + YouTube 视频播放    |
| W       | shadowsocks |                2 | paired    | 0.792161 | 0.796083 | 0.800694 |      1.086210 |    0.346744 |      0.845287 |    0.335050 | MDN 文档 + YouTube 视频播放    |
| W       | shadowsocks |                2 | raw       | 0.367813 | 0.534898 | 0.591667 |      2.247260 |    0.576426 |      3.811676 |    0.892453 | MDN 文档 + YouTube 视频播放    |
| W       | shadowsocks |                2 | reference | 0.819307 | 0.817675 | 0.819792 |      1.078823 |    0.322351 |      0.664866 |    0.253961 | MDN 文档 + YouTube 视频播放    |
| W       | trojan      |                0 | center    | 0.752280 | 0.696517 | 0.698958 |      1.367520 |    0.445435 |      1.307460 |    0.379451 | GitHub 仓库浏览 + YouTube 搜索 |
| W       | trojan      |                0 | cyclic    | 0.689780 | 0.623398 | 0.636111 |      1.515892 |    0.543000 |      1.626805 |    0.578619 | GitHub 仓库浏览 + YouTube 搜索 |
| W       | trojan      |                0 | group     | 0.722003 | 0.638705 | 0.648958 |      1.446498 |    0.526476 |      1.527556 |    0.550979 | GitHub 仓库浏览 + YouTube 搜索 |
| W       | trojan      |                0 | marginal  | 0.741283 | 0.690197 | 0.693056 |      1.371459 |    0.457176 |      1.308528 |    0.396204 | GitHub 仓库浏览 + YouTube 搜索 |
| W       | trojan      |                0 | paired    | 0.739242 | 0.692749 | 0.695833 |      1.363644 |    0.452990 |      1.314625 |    0.394183 | GitHub 仓库浏览 + YouTube 搜索 |
| W       | trojan      |                0 | raw       | 0.301221 | 0.353424 | 0.391319 |      2.262202 |    0.726541 |      3.061479 |    0.921337 | GitHub 仓库浏览 + YouTube 搜索 |
| W       | trojan      |                0 | reference | 0.751244 | 0.686264 | 0.687847 |      1.295323 |    0.439924 |      1.221243 |    0.374361 | GitHub 仓库浏览 + YouTube 搜索 |
| W       | trojan      |                1 | center    | 0.590713 | 0.699162 | 0.706250 |      1.317144 |    0.420954 |      1.913031 |    0.629851 | Bing 搜索 + Wikipedia 文章     |
| W       | trojan      |                1 | cyclic    | 0.399259 | 0.616116 | 0.644444 |      1.419190 |    0.517973 |      1.772753 |    0.696649 | Bing 搜索 + Wikipedia 文章     |
| W       | trojan      |                1 | group     | 0.477355 | 0.642020 | 0.660764 |      1.385561 |    0.504575 |      1.723537 |    0.669734 | Bing 搜索 + Wikipedia 文章     |
| W       | trojan      |                1 | marginal  | 0.579806 | 0.694053 | 0.702431 |      1.310870 |    0.430424 |      1.855148 |    0.630516 | Bing 搜索 + Wikipedia 文章     |
| W       | trojan      |                1 | paired    | 0.572263 | 0.689181 | 0.697569 |      1.323993 |    0.433970 |      1.867681 |    0.632515 | Bing 搜索 + Wikipedia 文章     |
| W       | trojan      |                1 | raw       | 0.043378 | 0.383583 | 0.467014 |      2.267696 |    0.691580 |      4.438494 |    1.250303 | Bing 搜索 + Wikipedia 文章     |
| W       | trojan      |                1 | reference | 0.621411 | 0.676450 | 0.677083 |      1.267242 |    0.430782 |      1.730069 |    0.576978 | Bing 搜索 + Wikipedia 文章     |
| W       | trojan      |                2 | center    | 0.713524 | 0.671011 | 0.678819 |      1.347286 |    0.433864 |      0.971391 |    0.342105 | MDN 文档 + YouTube 视频播放    |
| W       | trojan      |                2 | cyclic    | 0.511949 | 0.615409 | 0.645139 |      1.509718 |    0.542477 |      1.298847 |    0.502599 | MDN 文档 + YouTube 视频播放    |
| W       | trojan      |                2 | group     | 0.540457 | 0.630884 | 0.655903 |      1.452714 |    0.525832 |      1.153429 |    0.447269 | MDN 文档 + YouTube 视频播放    |
| W       | trojan      |                2 | marginal  | 0.695974 | 0.676678 | 0.681250 |      1.346998 |    0.440244 |      0.959439 |    0.357461 | MDN 文档 + YouTube 视频播放    |
| W       | trojan      |                2 | paired    | 0.700693 | 0.690108 | 0.694097 |      1.336120 |    0.434152 |      0.875819 |    0.339640 | MDN 文档 + YouTube 视频播放    |
| W       | trojan      |                2 | raw       | 0.361495 | 0.445020 | 0.504514 |      2.182301 |    0.648242 |      2.678199 |    0.706504 | MDN 文档 + YouTube 视频播放    |
| W       | trojan      |                2 | reference | 0.676988 | 0.682988 | 0.684375 |      1.312906 |    0.438674 |      0.868529 |    0.356769 | MDN 文档 + YouTube 视频播放    |
| W       | vless       |                0 | center    | 0.825576 | 0.727714 | 0.728125 |      1.710971 |    0.411199 |      1.321564 |    0.322845 | GitHub 仓库浏览 + YouTube 搜索 |
| W       | vless       |                0 | cyclic    | 0.720194 | 0.676558 | 0.679861 |      1.704714 |    0.523762 |      1.542445 |    0.551443 | GitHub 仓库浏览 + YouTube 搜索 |
| W       | vless       |                0 | group     | 0.777874 | 0.693540 | 0.696875 |      1.665795 |    0.509889 |      1.474422 |    0.518886 | GitHub 仓库浏览 + YouTube 搜索 |
| W       | vless       |                0 | marginal  | 0.838375 | 0.732119 | 0.734722 |      1.687870 |    0.422838 |      1.333025 |    0.339171 | GitHub 仓库浏览 + YouTube 搜索 |
| W       | vless       |                0 | paired    | 0.829878 | 0.724464 | 0.726042 |      1.747745 |    0.425695 |      1.343426 |    0.345865 | GitHub 仓库浏览 + YouTube 搜索 |
| W       | vless       |                0 | raw       | 0.613125 | 0.516978 | 0.551042 |      2.165582 |    0.583718 |      2.021943 |    0.544620 | GitHub 仓库浏览 + YouTube 搜索 |
| W       | vless       |                0 | reference | 0.843719 | 0.718754 | 0.726389 |      1.760769 |    0.404777 |      1.281840 |    0.290477 | GitHub 仓库浏览 + YouTube 搜索 |
| W       | vless       |                1 | center    | 0.564587 | 0.724439 | 0.734028 |      1.562240 |    0.400072 |      1.735265 |    0.547582 | Bing 搜索 + Wikipedia 文章     |
| W       | vless       |                1 | cyclic    | 0.423128 | 0.639562 | 0.663889 |      1.659026 |    0.536107 |      1.956778 |    0.684182 | Bing 搜索 + Wikipedia 文章     |
| W       | vless       |                1 | group     | 0.474736 | 0.665996 | 0.685764 |      1.595357 |    0.518683 |      1.853641 |    0.643929 | Bing 搜索 + Wikipedia 文章     |
| W       | vless       |                1 | marginal  | 0.570474 | 0.732530 | 0.741319 |      1.572694 |    0.410029 |      1.742422 |    0.541822 | Bing 搜索 + Wikipedia 文章     |
| W       | vless       |                1 | paired    | 0.570767 | 0.731512 | 0.740625 |      1.585474 |    0.404534 |      1.760296 |    0.530018 | Bing 搜索 + Wikipedia 文章     |
| W       | vless       |                1 | raw       | 0.085866 | 0.466374 | 0.530556 |      2.364809 |    0.650737 |      4.021854 |    1.219060 | Bing 搜索 + Wikipedia 文章     |
| W       | vless       |                1 | reference | 0.559493 | 0.723242 | 0.728819 |      1.658516 |    0.396245 |      1.822264 |    0.518465 | Bing 搜索 + Wikipedia 文章     |
| W       | vless       |                2 | center    | 0.716298 | 0.725261 | 0.725347 |      1.613403 |    0.406119 |      1.617492 |    0.423292 | MDN 文档 + YouTube 视频播放    |
| W       | vless       |                2 | cyclic    | 0.464340 | 0.633075 | 0.666319 |      1.653533 |    0.548594 |      1.258002 |    0.492073 | MDN 文档 + YouTube 视频播放    |
| W       | vless       |                2 | group     | 0.475303 | 0.634020 | 0.662153 |      1.616166 |    0.529628 |      1.213888 |    0.469193 | MDN 文档 + YouTube 视频播放    |
| W       | vless       |                2 | marginal  | 0.703316 | 0.728092 | 0.727431 |      1.549522 |    0.417704 |      1.469696 |    0.440604 | MDN 文档 + YouTube 视频播放    |
| W       | vless       |                2 | paired    | 0.708302 | 0.719919 | 0.719097 |      1.555453 |    0.413288 |      1.472061 |    0.426902 | MDN 文档 + YouTube 视频播放    |
| W       | vless       |                2 | raw       | 0.374755 | 0.504651 | 0.555903 |      2.285603 |    0.595149 |      3.206806 |    0.737553 | MDN 文档 + YouTube 视频播放    |
| W       | vless       |                2 | reference | 0.742828 | 0.717650 | 0.722917 |      1.695175 |    0.407048 |      1.688008 |    0.393141 | MDN 文档 + YouTube 视频播放    |
| W       | vmess       |                0 | center    | 0.894290 | 0.755364 | 0.761458 |      1.393027 |    0.390220 |      0.779840 |    0.192175 | GitHub 仓库浏览 + YouTube 搜索 |
| W       | vmess       |                0 | cyclic    | 0.778571 | 0.677513 | 0.701042 |      1.434103 |    0.505764 |      1.328235 |    0.484300 | GitHub 仓库浏览 + YouTube 搜索 |
| W       | vmess       |                0 | group     | 0.810698 | 0.683685 | 0.707986 |      1.426878 |    0.497590 |      1.227376 |    0.438341 | GitHub 仓库浏览 + YouTube 搜索 |
| W       | vmess       |                0 | marginal  | 0.854951 | 0.727116 | 0.737847 |      1.400568 |    0.405505 |      0.727033 |    0.202417 | GitHub 仓库浏览 + YouTube 搜索 |
| W       | vmess       |                0 | paired    | 0.898265 | 0.748627 | 0.758333 |      1.398667 |    0.389563 |      0.704454 |    0.185499 | GitHub 仓库浏览 + YouTube 搜索 |
| W       | vmess       |                0 | raw       | 0.354179 | 0.375035 | 0.416667 |      2.280576 |    0.718016 |      2.954549 |    0.922742 | GitHub 仓库浏览 + YouTube 搜索 |
| W       | vmess       |                0 | reference | 0.890943 | 0.746385 | 0.756597 |      1.301693 |    0.363842 |      0.831649 |    0.203281 | GitHub 仓库浏览 + YouTube 搜索 |
| W       | vmess       |                1 | center    | 0.468119 | 0.713141 | 0.742014 |      1.478030 |    0.397105 |      2.496392 |    0.742072 | Bing 搜索 + Wikipedia 文章     |
| W       | vmess       |                1 | cyclic    | 0.413261 | 0.665289 | 0.695833 |      1.304339 |    0.445110 |      1.718895 |    0.665147 | Bing 搜索 + Wikipedia 文章     |
| W       | vmess       |                1 | group     | 0.463097 | 0.682364 | 0.704514 |      1.268714 |    0.426767 |      1.649620 |    0.639208 | Bing 搜索 + Wikipedia 文章     |
| W       | vmess       |                1 | marginal  | 0.552107 | 0.741101 | 0.754861 |      1.368013 |    0.392620 |      2.201220 |    0.689934 | Bing 搜索 + Wikipedia 文章     |
| W       | vmess       |                1 | paired    | 0.567597 | 0.745777 | 0.758333 |      1.361066 |    0.379317 |      2.108147 |    0.649101 | Bing 搜索 + Wikipedia 文章     |
| W       | vmess       |                1 | raw       | 0.028676 | 0.459394 | 0.543403 |      2.647757 |    0.660801 |      5.732091 |    1.415247 | Bing 搜索 + Wikipedia 文章     |
| W       | vmess       |                1 | reference | 0.680138 | 0.745197 | 0.755556 |      1.338582 |    0.358895 |      1.966072 |    0.518795 | Bing 搜索 + Wikipedia 文章     |
| W       | vmess       |                2 | center    | 0.667009 | 0.747673 | 0.757292 |      1.346349 |    0.380352 |      1.188722 |    0.389673 | MDN 文档 + YouTube 视频播放    |
| W       | vmess       |                2 | cyclic    | 0.533285 | 0.673739 | 0.716319 |      1.311656 |    0.462204 |      1.338716 |    0.495367 | MDN 文档 + YouTube 视频播放    |
| W       | vmess       |                2 | group     | 0.548075 | 0.683491 | 0.721181 |      1.303789 |    0.452634 |      1.296626 |    0.471565 | MDN 文档 + YouTube 视频播放    |
| W       | vmess       |                2 | marginal  | 0.602015 | 0.718786 | 0.737500 |      1.311697 |    0.396527 |      1.234666 |    0.414797 | MDN 文档 + YouTube 视频播放    |
| W       | vmess       |                2 | paired    | 0.594471 | 0.720656 | 0.740972 |      1.305401 |    0.387898 |      1.174286 |    0.395992 | MDN 文档 + YouTube 视频播放    |
| W       | vmess       |                2 | raw       | 0.446278 | 0.540540 | 0.595139 |      2.224726 |    0.567060 |      3.425400 |    0.731697 | MDN 文档 + YouTube 视频播放    |
| W       | vmess       |                2 | reference | 0.658987 | 0.740170 | 0.751042 |      1.300203 |    0.362967 |      1.082887 |    0.361289 | MDN 文档 + YouTube 视频播放    |

## 逐类别作为新增业务

| track   | protocol    | 业务             | arm       |       F1 |   recall |
|:--------|:------------|:-----------------|:----------|---------:|---------:|
| T       | shadowsocks | Bing 搜索        | center    | 0.581905 | 0.456250 |
| T       | shadowsocks | Bing 搜索        | cyclic    | 0.723692 | 0.639583 |
| T       | shadowsocks | Bing 搜索        | group     | 0.752440 | 0.679167 |
| T       | shadowsocks | Bing 搜索        | marginal  | 0.822705 | 0.752083 |
| T       | shadowsocks | Bing 搜索        | paired    | 0.819118 | 0.793750 |
| T       | shadowsocks | Bing 搜索        | raw       | 0.651626 | 0.562500 |
| T       | shadowsocks | Bing 搜索        | reference | 0.818978 | 0.810417 |
| T       | shadowsocks | MDN 文档         | center    | 0.322403 | 0.333333 |
| T       | shadowsocks | MDN 文档         | cyclic    | 0.325929 | 0.260417 |
| T       | shadowsocks | MDN 文档         | group     | 0.350629 | 0.264583 |
| T       | shadowsocks | MDN 文档         | marginal  | 0.537289 | 0.533333 |
| T       | shadowsocks | MDN 文档         | paired    | 0.452111 | 0.381250 |
| T       | shadowsocks | MDN 文档         | raw       | 0.453463 | 0.377083 |
| T       | shadowsocks | MDN 文档         | reference | 0.526539 | 0.510417 |
| T       | shadowsocks | GitHub 仓库浏览  | center    | 0.821729 | 0.768750 |
| T       | shadowsocks | GitHub 仓库浏览  | cyclic    | 0.823428 | 0.791667 |
| T       | shadowsocks | GitHub 仓库浏览  | group     | 0.831699 | 0.789583 |
| T       | shadowsocks | GitHub 仓库浏览  | marginal  | 0.850724 | 0.802083 |
| T       | shadowsocks | GitHub 仓库浏览  | paired    | 0.836008 | 0.783333 |
| T       | shadowsocks | GitHub 仓库浏览  | raw       | 0.800835 | 0.756250 |
| T       | shadowsocks | GitHub 仓库浏览  | reference | 0.878697 | 0.852083 |
| T       | shadowsocks | Wikipedia 文章   | center    | 0.457376 | 0.593750 |
| T       | shadowsocks | Wikipedia 文章   | cyclic    | 0.164998 | 0.108333 |
| T       | shadowsocks | Wikipedia 文章   | group     | 0.195523 | 0.131250 |
| T       | shadowsocks | Wikipedia 文章   | marginal  | 0.537167 | 0.552083 |
| T       | shadowsocks | Wikipedia 文章   | paired    | 0.355581 | 0.268750 |
| T       | shadowsocks | Wikipedia 文章   | raw       | 0.000000 | 0.000000 |
| T       | shadowsocks | Wikipedia 文章   | reference | 0.620561 | 0.645833 |
| T       | shadowsocks | YouTube 搜索     | center    | 0.577710 | 0.443750 |
| T       | shadowsocks | YouTube 搜索     | cyclic    | 0.654461 | 0.618750 |
| T       | shadowsocks | YouTube 搜索     | group     | 0.650233 | 0.618750 |
| T       | shadowsocks | YouTube 搜索     | marginal  | 0.758066 | 0.687500 |
| T       | shadowsocks | YouTube 搜索     | paired    | 0.780677 | 0.745833 |
| T       | shadowsocks | YouTube 搜索     | raw       | 0.144920 | 0.079167 |
| T       | shadowsocks | YouTube 搜索     | reference | 0.810562 | 0.783333 |
| T       | shadowsocks | YouTube 视频播放 | center    | 0.597329 | 0.550000 |
| T       | shadowsocks | YouTube 视频播放 | cyclic    | 0.564687 | 0.547917 |
| T       | shadowsocks | YouTube 视频播放 | group     | 0.598765 | 0.602083 |
| T       | shadowsocks | YouTube 视频播放 | marginal  | 0.711970 | 0.681250 |
| T       | shadowsocks | YouTube 视频播放 | paired    | 0.736966 | 0.731250 |
| T       | shadowsocks | YouTube 视频播放 | raw       | 0.082698 | 0.052083 |
| T       | shadowsocks | YouTube 视频播放 | reference | 0.751870 | 0.789583 |
| T       | trojan      | Bing 搜索        | center    | 0.374536 | 0.268750 |
| T       | trojan      | Bing 搜索        | cyclic    | 0.324113 | 0.235417 |
| T       | trojan      | Bing 搜索        | group     | 0.367233 | 0.268750 |
| T       | trojan      | Bing 搜索        | marginal  | 0.545437 | 0.406250 |
| T       | trojan      | Bing 搜索        | paired    | 0.610865 | 0.487500 |
| T       | trojan      | Bing 搜索        | raw       | 0.094687 | 0.060417 |
| T       | trojan      | Bing 搜索        | reference | 0.763420 | 0.702083 |
| T       | trojan      | MDN 文档         | center    | 0.687623 | 0.762500 |
| T       | trojan      | MDN 文档         | cyclic    | 0.719280 | 0.729167 |
| T       | trojan      | MDN 文档         | group     | 0.722624 | 0.760417 |
| T       | trojan      | MDN 文档         | marginal  | 0.743540 | 0.804167 |
| T       | trojan      | MDN 文档         | paired    | 0.762143 | 0.797917 |
| T       | trojan      | MDN 文档         | raw       | 0.003968 | 0.002083 |
| T       | trojan      | MDN 文档         | reference | 0.775783 | 0.829167 |
| T       | trojan      | GitHub 仓库浏览  | center    | 0.915360 | 0.872917 |
| T       | trojan      | GitHub 仓库浏览  | cyclic    | 0.884242 | 0.814583 |
| T       | trojan      | GitHub 仓库浏览  | group     | 0.899320 | 0.841667 |
| T       | trojan      | GitHub 仓库浏览  | marginal  | 0.933611 | 0.897917 |
| T       | trojan      | GitHub 仓库浏览  | paired    | 0.935744 | 0.883333 |
| T       | trojan      | GitHub 仓库浏览  | raw       | 0.003968 | 0.002083 |
| T       | trojan      | GitHub 仓库浏览  | reference | 0.956220 | 0.958333 |
| T       | trojan      | Wikipedia 文章   | center    | 0.135734 | 0.185417 |
| T       | trojan      | Wikipedia 文章   | cyclic    | 0.229914 | 0.185417 |
| T       | trojan      | Wikipedia 文章   | group     | 0.283142 | 0.241667 |
| T       | trojan      | Wikipedia 文章   | marginal  | 0.509314 | 0.475000 |
| T       | trojan      | Wikipedia 文章   | paired    | 0.478985 | 0.410417 |
| T       | trojan      | Wikipedia 文章   | raw       | 0.000000 | 0.000000 |
| T       | trojan      | Wikipedia 文章   | reference | 0.612388 | 0.556250 |
| T       | trojan      | YouTube 搜索     | center    | 0.684834 | 0.675000 |
| T       | trojan      | YouTube 搜索     | cyclic    | 0.611743 | 0.587500 |
| T       | trojan      | YouTube 搜索     | group     | 0.666120 | 0.695833 |
| T       | trojan      | YouTube 搜索     | marginal  | 0.721056 | 0.760417 |
| T       | trojan      | YouTube 搜索     | paired    | 0.735240 | 0.793750 |
| T       | trojan      | YouTube 搜索     | raw       | 0.011364 | 0.006250 |
| T       | trojan      | YouTube 搜索     | reference | 0.709422 | 0.758333 |
| T       | trojan      | YouTube 视频播放 | center    | 0.736569 | 0.731250 |
| T       | trojan      | YouTube 视频播放 | cyclic    | 0.744105 | 0.712500 |
| T       | trojan      | YouTube 视频播放 | group     | 0.775444 | 0.772917 |
| T       | trojan      | YouTube 视频播放 | marginal  | 0.789794 | 0.843750 |
| T       | trojan      | YouTube 视频播放 | paired    | 0.819361 | 0.858333 |
| T       | trojan      | YouTube 视频播放 | raw       | 0.319219 | 0.200000 |
| T       | trojan      | YouTube 视频播放 | reference | 0.813449 | 0.860417 |
| T       | vless       | Bing 搜索        | center    | 0.166101 | 0.104167 |
| T       | vless       | Bing 搜索        | cyclic    | 0.149253 | 0.089583 |
| T       | vless       | Bing 搜索        | group     | 0.228564 | 0.143750 |
| T       | vless       | Bing 搜索        | marginal  | 0.514805 | 0.383333 |
| T       | vless       | Bing 搜索        | paired    | 0.543745 | 0.410417 |
| T       | vless       | Bing 搜索        | raw       | 0.068177 | 0.041667 |
| T       | vless       | Bing 搜索        | reference | 0.694495 | 0.641667 |
| T       | vless       | MDN 文档         | center    | 0.548143 | 0.620833 |
| T       | vless       | MDN 文档         | cyclic    | 0.746434 | 0.793750 |
| T       | vless       | MDN 文档         | group     | 0.760960 | 0.829167 |
| T       | vless       | MDN 文档         | marginal  | 0.757904 | 0.835417 |
| T       | vless       | MDN 文档         | paired    | 0.747743 | 0.802083 |
| T       | vless       | MDN 文档         | raw       | 0.007246 | 0.004167 |
| T       | vless       | MDN 文档         | reference | 0.742493 | 0.775000 |
| T       | vless       | GitHub 仓库浏览  | center    | 0.861151 | 0.814583 |
| T       | vless       | GitHub 仓库浏览  | cyclic    | 0.848168 | 0.829167 |
| T       | vless       | GitHub 仓库浏览  | group     | 0.851380 | 0.829167 |
| T       | vless       | GitHub 仓库浏览  | marginal  | 0.880410 | 0.866667 |
| T       | vless       | GitHub 仓库浏览  | paired    | 0.897010 | 0.879167 |
| T       | vless       | GitHub 仓库浏览  | raw       | 0.102453 | 0.054167 |
| T       | vless       | GitHub 仓库浏览  | reference | 0.874820 | 0.900000 |
| T       | vless       | Wikipedia 文章   | center    | 0.285761 | 0.314583 |
| T       | vless       | Wikipedia 文章   | cyclic    | 0.462753 | 0.472917 |
| T       | vless       | Wikipedia 文章   | group     | 0.485535 | 0.493750 |
| T       | vless       | Wikipedia 文章   | marginal  | 0.638752 | 0.641667 |
| T       | vless       | Wikipedia 文章   | paired    | 0.643234 | 0.597917 |
| T       | vless       | Wikipedia 文章   | raw       | 0.000000 | 0.000000 |
| T       | vless       | Wikipedia 文章   | reference | 0.672251 | 0.685417 |
| T       | vless       | YouTube 搜索     | center    | 0.479564 | 0.377083 |
| T       | vless       | YouTube 搜索     | cyclic    | 0.602250 | 0.545833 |
| T       | vless       | YouTube 搜索     | group     | 0.680259 | 0.627083 |
| T       | vless       | YouTube 搜索     | marginal  | 0.676237 | 0.581250 |
| T       | vless       | YouTube 搜索     | paired    | 0.705481 | 0.627083 |
| T       | vless       | YouTube 搜索     | raw       | 0.075634 | 0.043750 |
| T       | vless       | YouTube 搜索     | reference | 0.724970 | 0.654167 |
| T       | vless       | YouTube 视频播放 | center    | 0.570666 | 0.620833 |
| T       | vless       | YouTube 视频播放 | cyclic    | 0.543478 | 0.535417 |
| T       | vless       | YouTube 视频播放 | group     | 0.616820 | 0.664583 |
| T       | vless       | YouTube 视频播放 | marginal  | 0.703491 | 0.793750 |
| T       | vless       | YouTube 视频播放 | paired    | 0.711598 | 0.802083 |
| T       | vless       | YouTube 视频播放 | raw       | 0.160091 | 0.097917 |
| T       | vless       | YouTube 视频播放 | reference | 0.697206 | 0.754167 |
| T       | vmess       | Bing 搜索        | center    | 0.254241 | 0.237500 |
| T       | vmess       | Bing 搜索        | cyclic    | 0.176819 | 0.125000 |
| T       | vmess       | Bing 搜索        | group     | 0.193646 | 0.137500 |
| T       | vmess       | Bing 搜索        | marginal  | 0.281629 | 0.212500 |
| T       | vmess       | Bing 搜索        | paired    | 0.296366 | 0.225000 |
| T       | vmess       | Bing 搜索        | raw       | 0.159355 | 0.110417 |
| T       | vmess       | Bing 搜索        | reference | 0.471186 | 0.418750 |
| T       | vmess       | MDN 文档         | center    | 0.600336 | 0.629167 |
| T       | vmess       | MDN 文档         | cyclic    | 0.654741 | 0.652083 |
| T       | vmess       | MDN 文档         | group     | 0.681999 | 0.700000 |
| T       | vmess       | MDN 文档         | marginal  | 0.702896 | 0.735417 |
| T       | vmess       | MDN 文档         | paired    | 0.711574 | 0.722917 |
| T       | vmess       | MDN 文档         | raw       | 0.122702 | 0.066667 |
| T       | vmess       | MDN 文档         | reference | 0.728709 | 0.743750 |
| T       | vmess       | GitHub 仓库浏览  | center    | 0.950404 | 0.927083 |
| T       | vmess       | GitHub 仓库浏览  | cyclic    | 0.852105 | 0.783333 |
| T       | vmess       | GitHub 仓库浏览  | group     | 0.878095 | 0.829167 |
| T       | vmess       | GitHub 仓库浏览  | marginal  | 0.948034 | 0.931250 |
| T       | vmess       | GitHub 仓库浏览  | paired    | 0.948526 | 0.927083 |
| T       | vmess       | GitHub 仓库浏览  | raw       | 0.095238 | 0.050000 |
| T       | vmess       | GitHub 仓库浏览  | reference | 0.929818 | 0.950000 |
| T       | vmess       | Wikipedia 文章   | center    | 0.318498 | 0.331250 |
| T       | vmess       | Wikipedia 文章   | cyclic    | 0.336976 | 0.270833 |
| T       | vmess       | Wikipedia 文章   | group     | 0.412689 | 0.345833 |
| T       | vmess       | Wikipedia 文章   | marginal  | 0.710822 | 0.697917 |
| T       | vmess       | Wikipedia 文章   | paired    | 0.646886 | 0.581250 |
| T       | vmess       | Wikipedia 文章   | raw       | 0.000000 | 0.000000 |
| T       | vmess       | Wikipedia 文章   | reference | 0.757684 | 0.756250 |
| T       | vmess       | YouTube 搜索     | center    | 0.613843 | 0.516667 |
| T       | vmess       | YouTube 搜索     | cyclic    | 0.526940 | 0.512500 |
| T       | vmess       | YouTube 搜索     | group     | 0.622019 | 0.633333 |
| T       | vmess       | YouTube 搜索     | marginal  | 0.696047 | 0.681250 |
| T       | vmess       | YouTube 搜索     | paired    | 0.688660 | 0.695833 |
| T       | vmess       | YouTube 搜索     | raw       | 0.011905 | 0.006250 |
| T       | vmess       | YouTube 搜索     | reference | 0.718798 | 0.741667 |
| T       | vmess       | YouTube 视频播放 | center    | 0.592530 | 0.552083 |
| T       | vmess       | YouTube 视频播放 | cyclic    | 0.646902 | 0.608333 |
| T       | vmess       | YouTube 视频播放 | group     | 0.678206 | 0.658333 |
| T       | vmess       | YouTube 视频播放 | marginal  | 0.686596 | 0.689583 |
| T       | vmess       | YouTube 视频播放 | paired    | 0.707965 | 0.704167 |
| T       | vmess       | YouTube 视频播放 | raw       | 0.168118 | 0.093750 |
| T       | vmess       | YouTube 视频播放 | reference | 0.691909 | 0.714583 |
| W       | anytls      | Bing 搜索        | center    | 0.830269 | 0.825000 |
| W       | anytls      | Bing 搜索        | cyclic    | 0.625696 | 0.547917 |
| W       | anytls      | Bing 搜索        | group     | 0.701081 | 0.629167 |
| W       | anytls      | Bing 搜索        | marginal  | 0.819311 | 0.810417 |
| W       | anytls      | Bing 搜索        | paired    | 0.822137 | 0.775000 |
| W       | anytls      | Bing 搜索        | raw       | 0.296325 | 0.291667 |
| W       | anytls      | Bing 搜索        | reference | 0.822311 | 0.841667 |
| W       | anytls      | MDN 文档         | center    | 0.659297 | 0.775000 |
| W       | anytls      | MDN 文档         | cyclic    | 0.104068 | 0.085417 |
| W       | anytls      | MDN 文档         | group     | 0.265349 | 0.237500 |
| W       | anytls      | MDN 文档         | marginal  | 0.680570 | 0.806250 |
| W       | anytls      | MDN 文档         | paired    | 0.704058 | 0.825000 |
| W       | anytls      | MDN 文档         | raw       | 0.000000 | 0.000000 |
| W       | anytls      | MDN 文档         | reference | 0.696447 | 0.795833 |
| W       | anytls      | GitHub 仓库浏览  | center    | 0.877925 | 0.931250 |
| W       | anytls      | GitHub 仓库浏览  | cyclic    | 0.732992 | 0.772917 |
| W       | anytls      | GitHub 仓库浏览  | group     | 0.771458 | 0.806250 |
| W       | anytls      | GitHub 仓库浏览  | marginal  | 0.876528 | 0.931250 |
| W       | anytls      | GitHub 仓库浏览  | paired    | 0.875423 | 0.925000 |
| W       | anytls      | GitHub 仓库浏览  | raw       | 0.422767 | 0.420833 |
| W       | anytls      | GitHub 仓库浏览  | reference | 0.845811 | 0.875000 |
| W       | anytls      | Wikipedia 文章   | center    | 0.303467 | 0.187500 |
| W       | anytls      | Wikipedia 文章   | cyclic    | 0.310908 | 0.241667 |
| W       | anytls      | Wikipedia 文章   | group     | 0.351227 | 0.285417 |
| W       | anytls      | Wikipedia 文章   | marginal  | 0.339774 | 0.216667 |
| W       | anytls      | Wikipedia 文章   | paired    | 0.509314 | 0.410417 |
| W       | anytls      | Wikipedia 文章   | raw       | 0.000000 | 0.000000 |
| W       | anytls      | Wikipedia 文章   | reference | 0.648473 | 0.562500 |
| W       | anytls      | YouTube 搜索     | center    | 0.889226 | 0.881250 |
| W       | anytls      | YouTube 搜索     | cyclic    | 0.662406 | 0.652083 |
| W       | anytls      | YouTube 搜索     | group     | 0.753377 | 0.754167 |
| W       | anytls      | YouTube 搜索     | marginal  | 0.894080 | 0.860417 |
| W       | anytls      | YouTube 搜索     | paired    | 0.901016 | 0.881250 |
| W       | anytls      | YouTube 搜索     | raw       | 0.714686 | 0.606250 |
| W       | anytls      | YouTube 搜索     | reference | 0.896055 | 0.870833 |
| W       | anytls      | YouTube 视频播放 | center    | 0.955682 | 0.922917 |
| W       | anytls      | YouTube 视频播放 | cyclic    | 0.922121 | 0.931250 |
| W       | anytls      | YouTube 视频播放 | group     | 0.928302 | 0.943750 |
| W       | anytls      | YouTube 视频播放 | marginal  | 0.964566 | 0.937500 |
| W       | anytls      | YouTube 视频播放 | paired    | 0.964100 | 0.947917 |
| W       | anytls      | YouTube 视频播放 | raw       | 0.886386 | 0.808333 |
| W       | anytls      | YouTube 视频播放 | reference | 0.945268 | 0.950000 |
| W       | shadowsocks | Bing 搜索        | center    | 0.854859 | 0.833333 |
| W       | shadowsocks | Bing 搜索        | cyclic    | 0.744525 | 0.700000 |
| W       | shadowsocks | Bing 搜索        | group     | 0.769682 | 0.729167 |
| W       | shadowsocks | Bing 搜索        | marginal  | 0.865510 | 0.837500 |
| W       | shadowsocks | Bing 搜索        | paired    | 0.854449 | 0.831250 |
| W       | shadowsocks | Bing 搜索        | raw       | 0.234575 | 0.150000 |
| W       | shadowsocks | Bing 搜索        | reference | 0.876644 | 0.822917 |
| W       | shadowsocks | MDN 文档         | center    | 0.701657 | 0.772917 |
| W       | shadowsocks | MDN 文档         | cyclic    | 0.117041 | 0.085417 |
| W       | shadowsocks | MDN 文档         | group     | 0.202056 | 0.183333 |
| W       | shadowsocks | MDN 文档         | marginal  | 0.705015 | 0.814583 |
| W       | shadowsocks | MDN 文档         | paired    | 0.701813 | 0.843750 |
| W       | shadowsocks | MDN 文档         | raw       | 0.000000 | 0.000000 |
| W       | shadowsocks | MDN 文档         | reference | 0.717932 | 0.831250 |
| W       | shadowsocks | GitHub 仓库浏览  | center    | 0.877229 | 0.839583 |
| W       | shadowsocks | GitHub 仓库浏览  | cyclic    | 0.785192 | 0.770833 |
| W       | shadowsocks | GitHub 仓库浏览  | group     | 0.797074 | 0.777083 |
| W       | shadowsocks | GitHub 仓库浏览  | marginal  | 0.889532 | 0.845833 |
| W       | shadowsocks | GitHub 仓库浏览  | paired    | 0.898970 | 0.850000 |
| W       | shadowsocks | GitHub 仓库浏览  | raw       | 0.594983 | 0.593750 |
| W       | shadowsocks | GitHub 仓库浏览  | reference | 0.873483 | 0.812500 |
| W       | shadowsocks | Wikipedia 文章   | center    | 0.392900 | 0.264583 |
| W       | shadowsocks | Wikipedia 文章   | cyclic    | 0.147651 | 0.089583 |
| W       | shadowsocks | Wikipedia 文章   | group     | 0.180840 | 0.112500 |
| W       | shadowsocks | Wikipedia 文章   | marginal  | 0.422083 | 0.285417 |
| W       | shadowsocks | Wikipedia 文章   | paired    | 0.447958 | 0.325000 |
| W       | shadowsocks | Wikipedia 文章   | raw       | 0.000000 | 0.000000 |
| W       | shadowsocks | Wikipedia 文章   | reference | 0.511955 | 0.437500 |
| W       | shadowsocks | YouTube 搜索     | center    | 0.893532 | 0.987500 |
| W       | shadowsocks | YouTube 搜索     | cyclic    | 0.755020 | 0.743750 |
| W       | shadowsocks | YouTube 搜索     | group     | 0.824152 | 0.829167 |
| W       | shadowsocks | YouTube 搜索     | marginal  | 0.938655 | 0.987500 |
| W       | shadowsocks | YouTube 搜索     | paired    | 0.942149 | 0.964583 |
| W       | shadowsocks | YouTube 搜索     | raw       | 0.590400 | 0.456250 |
| W       | shadowsocks | YouTube 搜索     | reference | 0.953662 | 0.958333 |
| W       | shadowsocks | YouTube 视频播放 | center    | 0.845168 | 0.804167 |
| W       | shadowsocks | YouTube 视频播放 | cyclic    | 0.831629 | 0.900000 |
| W       | shadowsocks | YouTube 视频播放 | group     | 0.835366 | 0.916667 |
| W       | shadowsocks | YouTube 视频播放 | marginal  | 0.852710 | 0.835417 |
| W       | shadowsocks | YouTube 视频播放 | paired    | 0.882509 | 0.885417 |
| W       | shadowsocks | YouTube 视频播放 | raw       | 0.735625 | 0.704167 |
| W       | shadowsocks | YouTube 视频播放 | reference | 0.920683 | 0.989583 |
| W       | trojan      | Bing 搜索        | center    | 0.692410 | 0.647917 |
| W       | trojan      | Bing 搜索        | cyclic    | 0.507888 | 0.400000 |
| W       | trojan      | Bing 搜索        | group     | 0.558270 | 0.450000 |
| W       | trojan      | Bing 搜索        | marginal  | 0.684218 | 0.631250 |
| W       | trojan      | Bing 搜索        | paired    | 0.677707 | 0.625000 |
| W       | trojan      | Bing 搜索        | raw       | 0.039827 | 0.027083 |
| W       | trojan      | Bing 搜索        | reference | 0.686855 | 0.647917 |
| W       | trojan      | MDN 文档         | center    | 0.534287 | 0.604167 |
| W       | trojan      | MDN 文档         | cyclic    | 0.174066 | 0.120833 |
| W       | trojan      | MDN 文档         | group     | 0.217429 | 0.156250 |
| W       | trojan      | MDN 文档         | marginal  | 0.503249 | 0.531250 |
| W       | trojan      | MDN 文档         | paired    | 0.509638 | 0.545833 |
| W       | trojan      | MDN 文档         | raw       | 0.011364 | 0.006250 |
| W       | trojan      | MDN 文档         | reference | 0.499302 | 0.502083 |
| W       | trojan      | GitHub 仓库浏览  | center    | 0.758091 | 0.837500 |
| W       | trojan      | GitHub 仓库浏览  | cyclic    | 0.735697 | 0.806250 |
| W       | trojan      | GitHub 仓库浏览  | group     | 0.745597 | 0.818750 |
| W       | trojan      | GitHub 仓库浏览  | marginal  | 0.757004 | 0.845833 |
| W       | trojan      | GitHub 仓库浏览  | paired    | 0.764898 | 0.841667 |
| W       | trojan      | GitHub 仓库浏览  | raw       | 0.083239 | 0.068750 |
| W       | trojan      | GitHub 仓库浏览  | reference | 0.775872 | 0.814583 |
| W       | trojan      | Wikipedia 文章   | center    | 0.489017 | 0.375000 |
| W       | trojan      | Wikipedia 文章   | cyclic    | 0.290631 | 0.220833 |
| W       | trojan      | Wikipedia 文章   | group     | 0.396440 | 0.325000 |
| W       | trojan      | Wikipedia 文章   | marginal  | 0.475393 | 0.364583 |
| W       | trojan      | Wikipedia 文章   | paired    | 0.466818 | 0.368750 |
| W       | trojan      | Wikipedia 文章   | raw       | 0.046929 | 0.025000 |
| W       | trojan      | Wikipedia 文章   | reference | 0.555967 | 0.566667 |
| W       | trojan      | YouTube 搜索     | center    | 0.746468 | 0.706250 |
| W       | trojan      | YouTube 搜索     | cyclic    | 0.643863 | 0.554167 |
| W       | trojan      | YouTube 搜索     | group     | 0.698409 | 0.629167 |
| W       | trojan      | YouTube 搜索     | marginal  | 0.725562 | 0.675000 |
| W       | trojan      | YouTube 搜索     | paired    | 0.713586 | 0.693750 |
| W       | trojan      | YouTube 搜索     | raw       | 0.519203 | 0.464583 |
| W       | trojan      | YouTube 搜索     | reference | 0.726616 | 0.745833 |
| W       | trojan      | YouTube 视频播放 | center    | 0.892762 | 0.902083 |
| W       | trojan      | YouTube 视频播放 | cyclic    | 0.849833 | 0.902083 |
| W       | trojan      | YouTube 视频播放 | group     | 0.863486 | 0.927083 |
| W       | trojan      | YouTube 视频播放 | marginal  | 0.888699 | 0.897917 |
| W       | trojan      | YouTube 视频播放 | paired    | 0.891749 | 0.918750 |
| W       | trojan      | YouTube 视频播放 | raw       | 0.711627 | 0.868750 |
| W       | trojan      | YouTube 视频播放 | reference | 0.854673 | 0.850000 |
| W       | vless       | Bing 搜索        | center    | 0.758326 | 0.725000 |
| W       | vless       | Bing 搜索        | cyclic    | 0.641701 | 0.587500 |
| W       | vless       | Bing 搜索        | group     | 0.716323 | 0.693750 |
| W       | vless       | Bing 搜索        | marginal  | 0.756139 | 0.731250 |
| W       | vless       | Bing 搜索        | paired    | 0.771130 | 0.731250 |
| W       | vless       | Bing 搜索        | raw       | 0.097191 | 0.079167 |
| W       | vless       | Bing 搜索        | reference | 0.717666 | 0.683333 |
| W       | vless       | MDN 文档         | center    | 0.534863 | 0.550000 |
| W       | vless       | MDN 文档         | cyclic    | 0.083096 | 0.060417 |
| W       | vless       | MDN 文档         | group     | 0.103716 | 0.072917 |
| W       | vless       | MDN 文档         | marginal  | 0.506351 | 0.497917 |
| W       | vless       | MDN 文档         | paired    | 0.526385 | 0.579167 |
| W       | vless       | MDN 文档         | raw       | 0.000000 | 0.000000 |
| W       | vless       | MDN 文档         | reference | 0.617487 | 0.739583 |
| W       | vless       | GitHub 仓库浏览  | center    | 0.779603 | 0.827083 |
| W       | vless       | GitHub 仓库浏览  | cyclic    | 0.718389 | 0.743750 |
| W       | vless       | GitHub 仓库浏览  | group     | 0.733274 | 0.747917 |
| W       | vless       | GitHub 仓库浏览  | marginal  | 0.782660 | 0.831250 |
| W       | vless       | GitHub 仓库浏览  | paired    | 0.780911 | 0.818750 |
| W       | vless       | GitHub 仓库浏览  | raw       | 0.527879 | 0.520833 |
| W       | vless       | GitHub 仓库浏览  | reference | 0.799943 | 0.791667 |
| W       | vless       | Wikipedia 文章   | center    | 0.370849 | 0.283333 |
| W       | vless       | Wikipedia 文章   | cyclic    | 0.204556 | 0.143750 |
| W       | vless       | Wikipedia 文章   | group     | 0.233150 | 0.177083 |
| W       | vless       | Wikipedia 文章   | marginal  | 0.384809 | 0.295833 |
| W       | vless       | Wikipedia 文章   | paired    | 0.370404 | 0.287500 |
| W       | vless       | Wikipedia 文章   | raw       | 0.074540 | 0.039583 |
| W       | vless       | Wikipedia 文章   | reference | 0.401319 | 0.337500 |
| W       | vless       | YouTube 搜索     | center    | 0.871550 | 0.820833 |
| W       | vless       | YouTube 搜索     | cyclic    | 0.721999 | 0.629167 |
| W       | vless       | YouTube 搜索     | group     | 0.822474 | 0.760417 |
| W       | vless       | YouTube 搜索     | marginal  | 0.894090 | 0.843750 |
| W       | vless       | YouTube 搜索     | paired    | 0.878846 | 0.833333 |
| W       | vless       | YouTube 搜索     | raw       | 0.698371 | 0.712500 |
| W       | vless       | YouTube 搜索     | reference | 0.887495 | 0.885417 |
| W       | vless       | YouTube 视频播放 | center    | 0.897733 | 0.912500 |
| W       | vless       | YouTube 视频播放 | cyclic    | 0.845585 | 0.947917 |
| W       | vless       | YouTube 视频播放 | group     | 0.846890 | 0.941667 |
| W       | vless       | YouTube 视频播放 | marginal  | 0.900281 | 0.900000 |
| W       | vless       | YouTube 视频播放 | paired    | 0.890219 | 0.897917 |
| W       | vless       | YouTube 视频播放 | raw       | 0.749510 | 0.872917 |
| W       | vless       | YouTube 视频播放 | reference | 0.868169 | 0.897917 |
| W       | vmess       | Bing 搜索        | center    | 0.736524 | 0.704167 |
| W       | vmess       | Bing 搜索        | cyclic    | 0.529723 | 0.427083 |
| W       | vmess       | Bing 搜索        | group     | 0.548895 | 0.452083 |
| W       | vmess       | Bing 搜索        | marginal  | 0.729626 | 0.693750 |
| W       | vmess       | Bing 搜索        | paired    | 0.738988 | 0.706250 |
| W       | vmess       | Bing 搜索        | raw       | 0.057353 | 0.047917 |
| W       | vmess       | Bing 搜索        | reference | 0.744069 | 0.733333 |
| W       | vmess       | MDN 文档         | center    | 0.367203 | 0.304167 |
| W       | vmess       | MDN 文档         | cyclic    | 0.132668 | 0.083333 |
| W       | vmess       | MDN 文档         | group     | 0.156687 | 0.102083 |
| W       | vmess       | MDN 文档         | marginal  | 0.253933 | 0.185417 |
| W       | vmess       | MDN 文档         | paired    | 0.228739 | 0.166667 |
| W       | vmess       | MDN 文档         | raw       | 0.078824 | 0.041667 |
| W       | vmess       | MDN 文档         | reference | 0.365648 | 0.287500 |
| W       | vmess       | GitHub 仓库浏览  | center    | 0.906196 | 0.962500 |
| W       | vmess       | GitHub 仓库浏览  | cyclic    | 0.818092 | 0.916667 |
| W       | vmess       | GitHub 仓库浏览  | group     | 0.820376 | 0.927083 |
| W       | vmess       | GitHub 仓库浏览  | marginal  | 0.849494 | 0.972917 |
| W       | vmess       | GitHub 仓库浏览  | paired    | 0.901523 | 0.968750 |
| W       | vmess       | GitHub 仓库浏览  | raw       | 0.024837 | 0.016667 |
| W       | vmess       | GitHub 仓库浏览  | reference | 0.919760 | 0.954167 |
| W       | vmess       | Wikipedia 文章   | center    | 0.199715 | 0.122917 |
| W       | vmess       | Wikipedia 文章   | cyclic    | 0.296799 | 0.218750 |
| W       | vmess       | Wikipedia 文章   | group     | 0.377300 | 0.302083 |
| W       | vmess       | Wikipedia 文章   | marginal  | 0.374588 | 0.260417 |
| W       | vmess       | Wikipedia 文章   | paired    | 0.396206 | 0.293750 |
| W       | vmess       | Wikipedia 文章   | raw       | 0.000000 | 0.000000 |
| W       | vmess       | Wikipedia 文章   | reference | 0.616206 | 0.756250 |
| W       | vmess       | YouTube 搜索     | center    | 0.882385 | 0.870833 |
| W       | vmess       | YouTube 搜索     | cyclic    | 0.739050 | 0.683333 |
| W       | vmess       | YouTube 搜索     | group     | 0.801020 | 0.781250 |
| W       | vmess       | YouTube 搜索     | marginal  | 0.860409 | 0.831250 |
| W       | vmess       | YouTube 搜索     | paired    | 0.895008 | 0.891667 |
| W       | vmess       | YouTube 搜索     | raw       | 0.683521 | 0.589583 |
| W       | vmess       | YouTube 搜索     | reference | 0.862126 | 0.854167 |
| W       | vmess       | YouTube 视频播放 | center    | 0.966816 | 0.941667 |
| W       | vmess       | YouTube 视频播放 | cyclic    | 0.933902 | 0.989583 |
| W       | vmess       | YouTube 视频播放 | group     | 0.939462 | 0.991667 |
| W       | vmess       | YouTube 视频播放 | marginal  | 0.950098 | 0.910417 |
| W       | vmess       | YouTube 视频播放 | paired    | 0.960203 | 0.952083 |
| W       | vmess       | YouTube 视频播放 | raw       | 0.813731 | 0.939583 |
| W       | vmess       | YouTube 视频播放 | reference | 0.952327 | 0.950000 |

## 逐类别作为校准业务

| track   | protocol    | 业务             | arm       |       F1 |   recall |
|:--------|:------------|:-----------------|:----------|---------:|---------:|
| T       | shadowsocks | Bing 搜索        | center    | 0.810099 | 0.778125 |
| T       | shadowsocks | Bing 搜索        | cyclic    | 0.827809 | 0.807292 |
| T       | shadowsocks | Bing 搜索        | group     | 0.831955 | 0.816667 |
| T       | shadowsocks | Bing 搜索        | marginal  | 0.836925 | 0.816667 |
| T       | shadowsocks | Bing 搜索        | paired    | 0.836362 | 0.820833 |
| T       | shadowsocks | Bing 搜索        | raw       | 0.803170 | 0.819792 |
| T       | shadowsocks | Bing 搜索        | reference | 0.820649 | 0.812500 |
| T       | shadowsocks | MDN 文档         | center    | 0.531308 | 0.577083 |
| T       | shadowsocks | MDN 文档         | cyclic    | 0.592664 | 0.727083 |
| T       | shadowsocks | MDN 文档         | group     | 0.591864 | 0.727083 |
| T       | shadowsocks | MDN 文档         | marginal  | 0.581627 | 0.626042 |
| T       | shadowsocks | MDN 文档         | paired    | 0.584211 | 0.683333 |
| T       | shadowsocks | MDN 文档         | raw       | 0.603792 | 0.798958 |
| T       | shadowsocks | MDN 文档         | reference | 0.535430 | 0.526042 |
| T       | shadowsocks | GitHub 仓库浏览  | center    | 0.850564 | 0.817708 |
| T       | shadowsocks | GitHub 仓库浏览  | cyclic    | 0.849157 | 0.812500 |
| T       | shadowsocks | GitHub 仓库浏览  | group     | 0.845591 | 0.808333 |
| T       | shadowsocks | GitHub 仓库浏览  | marginal  | 0.868466 | 0.833333 |
| T       | shadowsocks | GitHub 仓库浏览  | paired    | 0.860815 | 0.822917 |
| T       | shadowsocks | GitHub 仓库浏览  | raw       | 0.845963 | 0.887500 |
| T       | shadowsocks | GitHub 仓库浏览  | reference | 0.870296 | 0.842708 |
| T       | shadowsocks | Wikipedia 文章   | center    | 0.622242 | 0.719792 |
| T       | shadowsocks | Wikipedia 文章   | cyclic    | 0.633913 | 0.759375 |
| T       | shadowsocks | Wikipedia 文章   | group     | 0.628005 | 0.741667 |
| T       | shadowsocks | Wikipedia 文章   | marginal  | 0.629722 | 0.655208 |
| T       | shadowsocks | Wikipedia 文章   | paired    | 0.652782 | 0.738542 |
| T       | shadowsocks | Wikipedia 文章   | raw       | 0.600275 | 0.658333 |
| T       | shadowsocks | Wikipedia 文章   | reference | 0.636161 | 0.667708 |
| T       | shadowsocks | YouTube 搜索     | center    | 0.728453 | 0.765625 |
| T       | shadowsocks | YouTube 搜索     | cyclic    | 0.683999 | 0.679167 |
| T       | shadowsocks | YouTube 搜索     | group     | 0.688814 | 0.675000 |
| T       | shadowsocks | YouTube 搜索     | marginal  | 0.769026 | 0.777083 |
| T       | shadowsocks | YouTube 搜索     | paired    | 0.785707 | 0.780208 |
| T       | shadowsocks | YouTube 搜索     | raw       | 0.689930 | 0.793750 |
| T       | shadowsocks | YouTube 搜索     | reference | 0.805227 | 0.787500 |
| T       | shadowsocks | YouTube 视频播放 | center    | 0.672074 | 0.842708 |
| T       | shadowsocks | YouTube 视频播放 | cyclic    | 0.657633 | 0.738542 |
| T       | shadowsocks | YouTube 视频播放 | group     | 0.663250 | 0.736458 |
| T       | shadowsocks | YouTube 视频播放 | marginal  | 0.745906 | 0.822917 |
| T       | shadowsocks | YouTube 视频播放 | paired    | 0.742397 | 0.800000 |
| T       | shadowsocks | YouTube 视频播放 | raw       | 0.644809 | 0.838542 |
| T       | shadowsocks | YouTube 视频播放 | reference | 0.749713 | 0.780208 |
| T       | trojan      | Bing 搜索        | center    | 0.635468 | 0.603125 |
| T       | trojan      | Bing 搜索        | cyclic    | 0.579009 | 0.511458 |
| T       | trojan      | Bing 搜索        | group     | 0.590738 | 0.509375 |
| T       | trojan      | Bing 搜索        | marginal  | 0.706507 | 0.641667 |
| T       | trojan      | Bing 搜索        | paired    | 0.751440 | 0.689583 |
| T       | trojan      | Bing 搜索        | raw       | 0.465491 | 0.708333 |
| T       | trojan      | Bing 搜索        | reference | 0.787558 | 0.714583 |
| T       | trojan      | MDN 文档         | center    | 0.658624 | 0.840625 |
| T       | trojan      | MDN 文档         | cyclic    | 0.715628 | 0.868750 |
| T       | trojan      | MDN 文档         | group     | 0.717372 | 0.858333 |
| T       | trojan      | MDN 文档         | marginal  | 0.733428 | 0.814583 |
| T       | trojan      | MDN 文档         | paired    | 0.746816 | 0.833333 |
| T       | trojan      | MDN 文档         | raw       | 0.602830 | 0.760417 |
| T       | trojan      | MDN 文档         | reference | 0.776477 | 0.829167 |
| T       | trojan      | GitHub 仓库浏览  | center    | 0.938151 | 0.933333 |
| T       | trojan      | GitHub 仓库浏览  | cyclic    | 0.877477 | 0.865625 |
| T       | trojan      | GitHub 仓库浏览  | group     | 0.891526 | 0.883333 |
| T       | trojan      | GitHub 仓库浏览  | marginal  | 0.955197 | 0.926042 |
| T       | trojan      | GitHub 仓库浏览  | paired    | 0.951205 | 0.935417 |
| T       | trojan      | GitHub 仓库浏览  | raw       | 0.876356 | 0.926042 |
| T       | trojan      | GitHub 仓库浏览  | reference | 0.942475 | 0.922917 |
| T       | trojan      | Wikipedia 文章   | center    | 0.478776 | 0.435417 |
| T       | trojan      | Wikipedia 文章   | cyclic    | 0.583446 | 0.598958 |
| T       | trojan      | Wikipedia 文章   | group     | 0.568798 | 0.570833 |
| T       | trojan      | Wikipedia 文章   | marginal  | 0.589871 | 0.538542 |
| T       | trojan      | Wikipedia 文章   | paired    | 0.636094 | 0.587500 |
| T       | trojan      | Wikipedia 文章   | raw       | 0.483312 | 0.530208 |
| T       | trojan      | Wikipedia 文章   | reference | 0.641882 | 0.585417 |
| T       | trojan      | YouTube 搜索     | center    | 0.741784 | 0.805208 |
| T       | trojan      | YouTube 搜索     | cyclic    | 0.717633 | 0.756250 |
| T       | trojan      | YouTube 搜索     | group     | 0.727902 | 0.758333 |
| T       | trojan      | YouTube 搜索     | marginal  | 0.728497 | 0.792708 |
| T       | trojan      | YouTube 搜索     | paired    | 0.725022 | 0.784375 |
| T       | trojan      | YouTube 搜索     | raw       | 0.705394 | 0.814583 |
| T       | trojan      | YouTube 搜索     | reference | 0.709310 | 0.757292 |
| T       | trojan      | YouTube 视频播放 | center    | 0.766783 | 0.879167 |
| T       | trojan      | YouTube 视频播放 | cyclic    | 0.785688 | 0.915625 |
| T       | trojan      | YouTube 视频播放 | group     | 0.795289 | 0.889583 |
| T       | trojan      | YouTube 视频播放 | marginal  | 0.775472 | 0.860417 |
| T       | trojan      | YouTube 视频播放 | paired    | 0.785333 | 0.860417 |
| T       | trojan      | YouTube 视频播放 | raw       | 0.695229 | 0.915625 |
| T       | trojan      | YouTube 视频播放 | reference | 0.816295 | 0.860417 |
| T       | vless       | Bing 搜索        | center    | 0.631274 | 0.597917 |
| T       | vless       | Bing 搜索        | cyclic    | 0.611632 | 0.531250 |
| T       | vless       | Bing 搜索        | group     | 0.644519 | 0.570833 |
| T       | vless       | Bing 搜索        | marginal  | 0.690539 | 0.627083 |
| T       | vless       | Bing 搜索        | paired    | 0.696894 | 0.630208 |
| T       | vless       | Bing 搜索        | raw       | 0.515466 | 0.695833 |
| T       | vless       | Bing 搜索        | reference | 0.718381 | 0.666667 |
| T       | vless       | MDN 文档         | center    | 0.632012 | 0.764583 |
| T       | vless       | MDN 文档         | cyclic    | 0.752669 | 0.877083 |
| T       | vless       | MDN 文档         | group     | 0.746133 | 0.861458 |
| T       | vless       | MDN 文档         | marginal  | 0.729723 | 0.801042 |
| T       | vless       | MDN 文档         | paired    | 0.739663 | 0.832292 |
| T       | vless       | MDN 文档         | raw       | 0.657137 | 0.794792 |
| T       | vless       | MDN 文档         | reference | 0.724980 | 0.741667 |
| T       | vless       | GitHub 仓库浏览  | center    | 0.830806 | 0.842708 |
| T       | vless       | GitHub 仓库浏览  | cyclic    | 0.818540 | 0.798958 |
| T       | vless       | GitHub 仓库浏览  | group     | 0.841941 | 0.823958 |
| T       | vless       | GitHub 仓库浏览  | marginal  | 0.862343 | 0.868750 |
| T       | vless       | GitHub 仓库浏览  | paired    | 0.870233 | 0.882292 |
| T       | vless       | GitHub 仓库浏览  | raw       | 0.753599 | 0.797917 |
| T       | vless       | GitHub 仓库浏览  | reference | 0.878664 | 0.898958 |
| T       | vless       | Wikipedia 文章   | center    | 0.580492 | 0.592708 |
| T       | vless       | Wikipedia 文章   | cyclic    | 0.656152 | 0.685417 |
| T       | vless       | Wikipedia 文章   | group     | 0.666209 | 0.672917 |
| T       | vless       | Wikipedia 文章   | marginal  | 0.682927 | 0.668750 |
| T       | vless       | Wikipedia 文章   | paired    | 0.699469 | 0.700000 |
| T       | vless       | Wikipedia 文章   | raw       | 0.566524 | 0.663542 |
| T       | vless       | Wikipedia 文章   | reference | 0.678458 | 0.683333 |
| T       | vless       | YouTube 搜索     | center    | 0.628781 | 0.563542 |
| T       | vless       | YouTube 搜索     | cyclic    | 0.636372 | 0.616667 |
| T       | vless       | YouTube 搜索     | group     | 0.651141 | 0.595833 |
| T       | vless       | YouTube 搜索     | marginal  | 0.694773 | 0.608333 |
| T       | vless       | YouTube 搜索     | paired    | 0.706250 | 0.621875 |
| T       | vless       | YouTube 搜索     | raw       | 0.600912 | 0.663542 |
| T       | vless       | YouTube 搜索     | reference | 0.701888 | 0.640625 |
| T       | vless       | YouTube 视频播放 | center    | 0.644843 | 0.861458 |
| T       | vless       | YouTube 视频播放 | cyclic    | 0.683900 | 0.842708 |
| T       | vless       | YouTube 视频播放 | group     | 0.706816 | 0.865625 |
| T       | vless       | YouTube 视频播放 | marginal  | 0.711778 | 0.872917 |
| T       | vless       | YouTube 视频播放 | paired    | 0.728092 | 0.873958 |
| T       | vless       | YouTube 视频播放 | raw       | 0.581500 | 0.839583 |
| T       | vless       | YouTube 视频播放 | reference | 0.719402 | 0.796875 |
| T       | vmess       | Bing 搜索        | center    | 0.431053 | 0.465625 |
| T       | vmess       | Bing 搜索        | cyclic    | 0.373256 | 0.355208 |
| T       | vmess       | Bing 搜索        | group     | 0.392566 | 0.358333 |
| T       | vmess       | Bing 搜索        | marginal  | 0.461089 | 0.419792 |
| T       | vmess       | Bing 搜索        | paired    | 0.469479 | 0.423958 |
| T       | vmess       | Bing 搜索        | raw       | 0.337690 | 0.511458 |
| T       | vmess       | Bing 搜索        | reference | 0.496800 | 0.447917 |
| T       | vmess       | MDN 文档         | center    | 0.655238 | 0.773958 |
| T       | vmess       | MDN 文档         | cyclic    | 0.705826 | 0.840625 |
| T       | vmess       | MDN 文档         | group     | 0.709836 | 0.825000 |
| T       | vmess       | MDN 文档         | marginal  | 0.739482 | 0.792708 |
| T       | vmess       | MDN 文档         | paired    | 0.731808 | 0.800000 |
| T       | vmess       | MDN 文档         | raw       | 0.632552 | 0.794792 |
| T       | vmess       | MDN 文档         | reference | 0.727174 | 0.733333 |
| T       | vmess       | GitHub 仓库浏览  | center    | 0.918803 | 0.944792 |
| T       | vmess       | GitHub 仓库浏览  | cyclic    | 0.910859 | 0.918750 |
| T       | vmess       | GitHub 仓库浏览  | group     | 0.912386 | 0.928125 |
| T       | vmess       | GitHub 仓库浏览  | marginal  | 0.924151 | 0.948958 |
| T       | vmess       | GitHub 仓库浏览  | paired    | 0.923190 | 0.948958 |
| T       | vmess       | GitHub 仓库浏览  | raw       | 0.886681 | 0.935417 |
| T       | vmess       | GitHub 仓库浏览  | reference | 0.923795 | 0.950000 |
| T       | vmess       | Wikipedia 文章   | center    | 0.641103 | 0.655208 |
| T       | vmess       | Wikipedia 文章   | cyclic    | 0.668139 | 0.714583 |
| T       | vmess       | Wikipedia 文章   | group     | 0.692163 | 0.734375 |
| T       | vmess       | Wikipedia 文章   | marginal  | 0.731164 | 0.737500 |
| T       | vmess       | Wikipedia 文章   | paired    | 0.760843 | 0.779167 |
| T       | vmess       | Wikipedia 文章   | raw       | 0.569117 | 0.677083 |
| T       | vmess       | Wikipedia 文章   | reference | 0.757362 | 0.753125 |
| T       | vmess       | YouTube 搜索     | center    | 0.693725 | 0.686458 |
| T       | vmess       | YouTube 搜索     | cyclic    | 0.678118 | 0.673958 |
| T       | vmess       | YouTube 搜索     | group     | 0.706176 | 0.702083 |
| T       | vmess       | YouTube 搜索     | marginal  | 0.698210 | 0.712500 |
| T       | vmess       | YouTube 搜索     | paired    | 0.699780 | 0.720833 |
| T       | vmess       | YouTube 搜索     | raw       | 0.658444 | 0.750000 |
| T       | vmess       | YouTube 搜索     | reference | 0.717756 | 0.735417 |
| T       | vmess       | YouTube 视频播放 | center    | 0.682913 | 0.773958 |
| T       | vmess       | YouTube 视频播放 | cyclic    | 0.662885 | 0.763542 |
| T       | vmess       | YouTube 视频播放 | group     | 0.662629 | 0.745833 |
| T       | vmess       | YouTube 视频播放 | marginal  | 0.687225 | 0.762500 |
| T       | vmess       | YouTube 视频播放 | paired    | 0.677451 | 0.748958 |
| T       | vmess       | YouTube 视频播放 | raw       | 0.610704 | 0.747917 |
| T       | vmess       | YouTube 视频播放 | reference | 0.694940 | 0.728125 |
| W       | anytls      | Bing 搜索        | center    | 0.810865 | 0.792708 |
| W       | anytls      | Bing 搜索        | cyclic    | 0.667620 | 0.602083 |
| W       | anytls      | Bing 搜索        | group     | 0.707563 | 0.643750 |
| W       | anytls      | Bing 搜索        | marginal  | 0.822847 | 0.819792 |
| W       | anytls      | Bing 搜索        | paired    | 0.836065 | 0.811458 |
| W       | anytls      | Bing 搜索        | raw       | 0.629228 | 0.813542 |
| W       | anytls      | Bing 搜索        | reference | 0.818231 | 0.833333 |
| W       | anytls      | MDN 文档         | center    | 0.691712 | 0.920833 |
| W       | anytls      | MDN 文档         | cyclic    | 0.572772 | 0.729167 |
| W       | anytls      | MDN 文档         | group     | 0.575452 | 0.725000 |
| W       | anytls      | MDN 文档         | marginal  | 0.681482 | 0.896875 |
| W       | anytls      | MDN 文档         | paired    | 0.679801 | 0.844792 |
| W       | anytls      | MDN 文档         | raw       | 0.539305 | 0.596875 |
| W       | anytls      | MDN 文档         | reference | 0.701380 | 0.788542 |
| W       | anytls      | GitHub 仓库浏览  | center    | 0.879644 | 0.907292 |
| W       | anytls      | GitHub 仓库浏览  | cyclic    | 0.805757 | 0.868750 |
| W       | anytls      | GitHub 仓库浏览  | group     | 0.822847 | 0.862500 |
| W       | anytls      | GitHub 仓库浏览  | marginal  | 0.887510 | 0.920833 |
| W       | anytls      | GitHub 仓库浏览  | paired    | 0.887612 | 0.921875 |
| W       | anytls      | GitHub 仓库浏览  | raw       | 0.637889 | 0.893750 |
| W       | anytls      | GitHub 仓库浏览  | reference | 0.841907 | 0.873958 |
| W       | anytls      | Wikipedia 文章   | center    | 0.563413 | 0.455208 |
| W       | anytls      | Wikipedia 文章   | cyclic    | 0.554875 | 0.690625 |
| W       | anytls      | Wikipedia 文章   | group     | 0.559409 | 0.650000 |
| W       | anytls      | Wikipedia 文章   | marginal  | 0.578106 | 0.473958 |
| W       | anytls      | Wikipedia 文章   | paired    | 0.599768 | 0.505208 |
| W       | anytls      | Wikipedia 文章   | raw       | 0.244364 | 0.238542 |
| W       | anytls      | Wikipedia 文章   | reference | 0.594962 | 0.495833 |
| W       | anytls      | YouTube 搜索     | center    | 0.899755 | 0.882292 |
| W       | anytls      | YouTube 搜索     | cyclic    | 0.811523 | 0.803125 |
| W       | anytls      | YouTube 搜索     | group     | 0.833602 | 0.822917 |
| W       | anytls      | YouTube 搜索     | marginal  | 0.903380 | 0.869792 |
| W       | anytls      | YouTube 搜索     | paired    | 0.910991 | 0.885417 |
| W       | anytls      | YouTube 搜索     | raw       | 0.826300 | 0.865625 |
| W       | anytls      | YouTube 搜索     | reference | 0.891110 | 0.856250 |
| W       | anytls      | YouTube 视频播放 | center    | 0.958083 | 0.939583 |
| W       | anytls      | YouTube 视频播放 | cyclic    | 0.911909 | 0.931250 |
| W       | anytls      | YouTube 视频播放 | group     | 0.926317 | 0.934375 |
| W       | anytls      | YouTube 视频播放 | marginal  | 0.954885 | 0.936458 |
| W       | anytls      | YouTube 视频播放 | paired    | 0.963647 | 0.948958 |
| W       | anytls      | YouTube 视频播放 | raw       | 0.870456 | 0.944792 |
| W       | anytls      | YouTube 视频播放 | reference | 0.946237 | 0.950000 |
| W       | shadowsocks | Bing 搜索        | center    | 0.833952 | 0.793750 |
| W       | shadowsocks | Bing 搜索        | cyclic    | 0.722723 | 0.635417 |
| W       | shadowsocks | Bing 搜索        | group     | 0.718445 | 0.623958 |
| W       | shadowsocks | Bing 搜索        | marginal  | 0.844217 | 0.808333 |
| W       | shadowsocks | Bing 搜索        | paired    | 0.842089 | 0.798958 |
| W       | shadowsocks | Bing 搜索        | raw       | 0.692930 | 0.756250 |
| W       | shadowsocks | Bing 搜索        | reference | 0.842957 | 0.808333 |
| W       | shadowsocks | MDN 文档         | center    | 0.715538 | 0.907292 |
| W       | shadowsocks | MDN 文档         | cyclic    | 0.620650 | 0.834375 |
| W       | shadowsocks | MDN 文档         | group     | 0.633063 | 0.854167 |
| W       | shadowsocks | MDN 文档         | marginal  | 0.721778 | 0.921875 |
| W       | shadowsocks | MDN 文档         | paired    | 0.707920 | 0.887500 |
| W       | shadowsocks | MDN 文档         | raw       | 0.557515 | 0.682292 |
| W       | shadowsocks | MDN 文档         | reference | 0.699709 | 0.825000 |
| W       | shadowsocks | GitHub 仓库浏览  | center    | 0.885431 | 0.846875 |
| W       | shadowsocks | GitHub 仓库浏览  | cyclic    | 0.811522 | 0.804167 |
| W       | shadowsocks | GitHub 仓库浏览  | group     | 0.811321 | 0.804167 |
| W       | shadowsocks | GitHub 仓库浏览  | marginal  | 0.891315 | 0.847917 |
| W       | shadowsocks | GitHub 仓库浏览  | paired    | 0.891804 | 0.846875 |
| W       | shadowsocks | GitHub 仓库浏览  | raw       | 0.611361 | 0.840625 |
| W       | shadowsocks | GitHub 仓库浏览  | reference | 0.884670 | 0.827083 |
| W       | shadowsocks | Wikipedia 文章   | center    | 0.582630 | 0.515625 |
| W       | shadowsocks | Wikipedia 文章   | cyclic    | 0.470027 | 0.578125 |
| W       | shadowsocks | Wikipedia 文章   | group     | 0.455134 | 0.523958 |
| W       | shadowsocks | Wikipedia 文章   | marginal  | 0.562360 | 0.482292 |
| W       | shadowsocks | Wikipedia 文章   | paired    | 0.548020 | 0.461458 |
| W       | shadowsocks | Wikipedia 文章   | raw       | 0.274648 | 0.290625 |
| W       | shadowsocks | Wikipedia 文章   | reference | 0.598941 | 0.528125 |
| W       | shadowsocks | YouTube 搜索     | center    | 0.908384 | 0.986458 |
| W       | shadowsocks | YouTube 搜索     | cyclic    | 0.856033 | 0.842708 |
| W       | shadowsocks | YouTube 搜索     | group     | 0.862703 | 0.853125 |
| W       | shadowsocks | YouTube 搜索     | marginal  | 0.933220 | 0.988542 |
| W       | shadowsocks | YouTube 搜索     | paired    | 0.944192 | 0.985417 |
| W       | shadowsocks | YouTube 搜索     | raw       | 0.884222 | 0.910417 |
| W       | shadowsocks | YouTube 搜索     | reference | 0.951888 | 0.954167 |
| W       | shadowsocks | YouTube 视频播放 | center    | 0.865664 | 0.848958 |
| W       | shadowsocks | YouTube 视频播放 | cyclic    | 0.866233 | 0.965625 |
| W       | shadowsocks | YouTube 视频播放 | group     | 0.866576 | 0.946875 |
| W       | shadowsocks | YouTube 视频播放 | marginal  | 0.896986 | 0.908333 |
| W       | shadowsocks | YouTube 视频播放 | paired    | 0.908768 | 0.937500 |
| W       | shadowsocks | YouTube 视频播放 | raw       | 0.757435 | 0.982292 |
| W       | shadowsocks | YouTube 视频播放 | reference | 0.930821 | 0.991667 |
| W       | trojan      | Bing 搜索        | center    | 0.685520 | 0.646875 |
| W       | trojan      | Bing 搜索        | cyclic    | 0.600926 | 0.550000 |
| W       | trojan      | Bing 搜索        | group     | 0.619411 | 0.561458 |
| W       | trojan      | Bing 搜索        | marginal  | 0.673176 | 0.633333 |
| W       | trojan      | Bing 搜索        | paired    | 0.693239 | 0.633333 |
| W       | trojan      | Bing 搜索        | raw       | 0.301429 | 0.313542 |
| W       | trojan      | Bing 搜索        | reference | 0.694205 | 0.647917 |
| W       | trojan      | MDN 文档         | center    | 0.575576 | 0.666667 |
| W       | trojan      | MDN 文档         | cyclic    | 0.458891 | 0.555208 |
| W       | trojan      | MDN 文档         | group     | 0.464636 | 0.529167 |
| W       | trojan      | MDN 文档         | marginal  | 0.576947 | 0.662500 |
| W       | trojan      | MDN 文档         | paired    | 0.562676 | 0.635417 |
| W       | trojan      | MDN 文档         | raw       | 0.337334 | 0.329167 |
| W       | trojan      | MDN 文档         | reference | 0.479531 | 0.477083 |
| W       | trojan      | GitHub 仓库浏览  | center    | 0.770275 | 0.844792 |
| W       | trojan      | GitHub 仓库浏览  | cyclic    | 0.760663 | 0.881250 |
| W       | trojan      | GitHub 仓库浏览  | group     | 0.781904 | 0.900000 |
| W       | trojan      | GitHub 仓库浏览  | marginal  | 0.776326 | 0.856250 |
| W       | trojan      | GitHub 仓库浏览  | paired    | 0.781197 | 0.843750 |
| W       | trojan      | GitHub 仓库浏览  | raw       | 0.545576 | 0.761458 |
| W       | trojan      | GitHub 仓库浏览  | reference | 0.777197 | 0.816667 |
| W       | trojan      | Wikipedia 文章   | center    | 0.485334 | 0.438542 |
| W       | trojan      | Wikipedia 文章   | cyclic    | 0.570005 | 0.707292 |
| W       | trojan      | Wikipedia 文章   | group     | 0.563439 | 0.671875 |
| W       | trojan      | Wikipedia 文章   | marginal  | 0.529317 | 0.502083 |
| W       | trojan      | Wikipedia 文章   | paired    | 0.556047 | 0.535417 |
| W       | trojan      | Wikipedia 文章   | raw       | 0.345778 | 0.300000 |
| W       | trojan      | Wikipedia 文章   | reference | 0.568155 | 0.571875 |
| W       | trojan      | YouTube 搜索     | center    | 0.739025 | 0.710417 |
| W       | trojan      | YouTube 搜索     | cyclic    | 0.696045 | 0.658333 |
| W       | trojan      | YouTube 搜索     | group     | 0.691597 | 0.654167 |
| W       | trojan      | YouTube 搜索     | marginal  | 0.724101 | 0.696875 |
| W       | trojan      | YouTube 搜索     | paired    | 0.721943 | 0.703125 |
| W       | trojan      | YouTube 搜索     | raw       | 0.660435 | 0.713542 |
| W       | trojan      | YouTube 搜索     | reference | 0.709572 | 0.719792 |
| W       | trojan      | YouTube 视频播放 | center    | 0.887821 | 0.908333 |
| W       | trojan      | YouTube 视频播放 | cyclic    | 0.877251 | 0.922917 |
| W       | trojan      | YouTube 视频播放 | group     | 0.874025 | 0.927083 |
| W       | trojan      | YouTube 视频播放 | marginal  | 0.885854 | 0.906250 |
| W       | trojan      | YouTube 视频播放 | paired    | 0.888816 | 0.914583 |
| W       | trojan      | YouTube 视频播放 | raw       | 0.649433 | 0.940625 |
| W       | trojan      | YouTube 视频播放 | reference | 0.858802 | 0.851042 |
| W       | vless       | Bing 搜索        | center    | 0.757802 | 0.736458 |
| W       | vless       | Bing 搜索        | cyclic    | 0.746083 | 0.734375 |
| W       | vless       | Bing 搜索        | group     | 0.750073 | 0.729167 |
| W       | vless       | Bing 搜索        | marginal  | 0.751218 | 0.730208 |
| W       | vless       | Bing 搜索        | paired    | 0.758591 | 0.719792 |
| W       | vless       | Bing 搜索        | raw       | 0.495873 | 0.516667 |
| W       | vless       | Bing 搜索        | reference | 0.715372 | 0.684375 |
| W       | vless       | MDN 文档         | center    | 0.614540 | 0.745833 |
| W       | vless       | MDN 文档         | cyclic    | 0.576628 | 0.719792 |
| W       | vless       | MDN 文档         | group     | 0.570947 | 0.711458 |
| W       | vless       | MDN 文档         | marginal  | 0.630069 | 0.780208 |
| W       | vless       | MDN 文档         | paired    | 0.617755 | 0.764583 |
| W       | vless       | MDN 文档         | raw       | 0.411858 | 0.433333 |
| W       | vless       | MDN 文档         | reference | 0.630164 | 0.769792 |
| W       | vless       | GitHub 仓库浏览  | center    | 0.788895 | 0.816667 |
| W       | vless       | GitHub 仓库浏览  | cyclic    | 0.760142 | 0.782292 |
| W       | vless       | GitHub 仓库浏览  | group     | 0.766016 | 0.776042 |
| W       | vless       | GitHub 仓库浏览  | marginal  | 0.792138 | 0.817708 |
| W       | vless       | GitHub 仓库浏览  | paired    | 0.800462 | 0.814583 |
| W       | vless       | GitHub 仓库浏览  | raw       | 0.661654 | 0.797917 |
| W       | vless       | GitHub 仓库浏览  | reference | 0.814234 | 0.795833 |
| W       | vless       | Wikipedia 文章   | center    | 0.465754 | 0.450000 |
| W       | vless       | Wikipedia 文章   | cyclic    | 0.499684 | 0.629167 |
| W       | vless       | Wikipedia 文章   | group     | 0.479916 | 0.592708 |
| W       | vless       | Wikipedia 文章   | marginal  | 0.472708 | 0.464583 |
| W       | vless       | Wikipedia 文章   | paired    | 0.434264 | 0.409375 |
| W       | vless       | Wikipedia 文章   | raw       | 0.337559 | 0.355208 |
| W       | vless       | Wikipedia 文章   | reference | 0.388460 | 0.322917 |
| W       | vless       | YouTube 搜索     | center    | 0.887210 | 0.860417 |
| W       | vless       | YouTube 搜索     | cyclic    | 0.768915 | 0.690625 |
| W       | vless       | YouTube 搜索     | group     | 0.796405 | 0.715625 |
| W       | vless       | YouTube 搜索     | marginal  | 0.906068 | 0.872917 |
| W       | vless       | YouTube 搜索     | paired    | 0.900026 | 0.879167 |
| W       | vless       | YouTube 搜索     | raw       | 0.807065 | 0.790625 |
| W       | vless       | YouTube 搜索     | reference | 0.906407 | 0.897917 |
| W       | vless       | YouTube 视频播放 | center    | 0.911580 | 0.893750 |
| W       | vless       | YouTube 视频播放 | cyclic    | 0.888472 | 0.917708 |
| W       | vless       | YouTube 视频播放 | group     | 0.889395 | 0.912500 |
| W       | vless       | YouTube 视频播放 | marginal  | 0.913858 | 0.894792 |
| W       | vless       | YouTube 视频播放 | paired    | 0.907640 | 0.895833 |
| W       | vless       | YouTube 视频播放 | raw       | 0.676255 | 0.906250 |
| W       | vless       | YouTube 视频播放 | reference | 0.878258 | 0.895833 |
| W       | vmess       | Bing 搜索        | center    | 0.735096 | 0.698958 |
| W       | vmess       | Bing 搜索        | cyclic    | 0.642410 | 0.554167 |
| W       | vmess       | Bing 搜索        | group     | 0.632699 | 0.533333 |
| W       | vmess       | Bing 搜索        | marginal  | 0.671268 | 0.613542 |
| W       | vmess       | Bing 搜索        | paired    | 0.720509 | 0.656250 |
| W       | vmess       | Bing 搜索        | raw       | 0.305456 | 0.378125 |
| W       | vmess       | Bing 搜索        | reference | 0.726697 | 0.698958 |
| W       | vmess       | MDN 文档         | center    | 0.555816 | 0.705208 |
| W       | vmess       | MDN 文档         | cyclic    | 0.449594 | 0.531250 |
| W       | vmess       | MDN 文档         | group     | 0.434159 | 0.483333 |
| W       | vmess       | MDN 文档         | marginal  | 0.518413 | 0.614583 |
| W       | vmess       | MDN 文档         | paired    | 0.503231 | 0.582292 |
| W       | vmess       | MDN 文档         | raw       | 0.374531 | 0.380208 |
| W       | vmess       | MDN 文档         | reference | 0.375053 | 0.301042 |
| W       | vmess       | GitHub 仓库浏览  | center    | 0.894022 | 0.950000 |
| W       | vmess       | GitHub 仓库浏览  | cyclic    | 0.825079 | 0.958333 |
| W       | vmess       | GitHub 仓库浏览  | group     | 0.834975 | 0.965625 |
| W       | vmess       | GitHub 仓库浏览  | marginal  | 0.888166 | 0.954167 |
| W       | vmess       | GitHub 仓库浏览  | paired    | 0.893163 | 0.953125 |
| W       | vmess       | GitHub 仓库浏览  | raw       | 0.729970 | 0.926042 |
| W       | vmess       | GitHub 仓库浏览  | reference | 0.922303 | 0.951042 |
| W       | vmess       | Wikipedia 文章   | center    | 0.595615 | 0.672917 |
| W       | vmess       | Wikipedia 文章   | cyclic    | 0.659406 | 0.883333 |
| W       | vmess       | Wikipedia 文章   | group     | 0.653476 | 0.869792 |
| W       | vmess       | Wikipedia 文章   | marginal  | 0.642650 | 0.793750 |
| W       | vmess       | Wikipedia 文章   | paired    | 0.627549 | 0.783333 |
| W       | vmess       | Wikipedia 文章   | raw       | 0.351831 | 0.377083 |
| W       | vmess       | Wikipedia 文章   | reference | 0.630599 | 0.758333 |
| W       | vmess       | YouTube 搜索     | center    | 0.879215 | 0.863542 |
| W       | vmess       | YouTube 搜索     | cyclic    | 0.814739 | 0.771875 |
| W       | vmess       | YouTube 搜索     | group     | 0.830980 | 0.792708 |
| W       | vmess       | YouTube 搜索     | marginal  | 0.871207 | 0.850000 |
| W       | vmess       | YouTube 搜索     | paired    | 0.875290 | 0.859375 |
| W       | vmess       | YouTube 搜索     | raw       | 0.821550 | 0.805208 |
| W       | vmess       | YouTube 搜索     | reference | 0.863644 | 0.862500 |
| W       | vmess       | YouTube 视频播放 | center    | 0.959350 | 0.938542 |
| W       | vmess       | YouTube 视频播放 | cyclic    | 0.933280 | 0.981250 |
| W       | vmess       | YouTube 视频播放 | group     | 0.940461 | 0.978125 |
| W       | vmess       | YouTube 视频播放 | marginal  | 0.960231 | 0.937500 |
| W       | vmess       | YouTube 视频播放 | paired    | 0.965104 | 0.948958 |
| W       | vmess       | YouTube 视频播放 | raw       | 0.712434 | 0.981250 |
| W       | vmess       | YouTube 视频播放 | reference | 0.946893 | 0.950000 |

## 逐种子

| track   | protocol    | arm       |     seed |   F1_new |   F1_all |   BA_all |   CE_all_bits |   Brier_all |   CE_new_bits |   Brier_new |
|:--------|:------------|:----------|---------:|---------:|---------:|---------:|--------------:|------------:|--------------:|------------:|
| T       | shadowsocks | center    | 20260918 | 0.581575 | 0.662690 | 0.680903 |      1.577501 |    0.464912 |      2.141754 |    0.667460 |
| T       | shadowsocks | center    | 20260919 | 0.556837 | 0.660665 | 0.680556 |      1.579624 |    0.470293 |      2.173991 |    0.701853 |
| T       | shadowsocks | center    | 20260920 | 0.540814 | 0.641300 | 0.663194 |      1.566133 |    0.482277 |      2.159454 |    0.702437 |
| T       | shadowsocks | cyclic    | 20260918 | 0.539809 | 0.651571 | 0.666319 |      1.291303 |    0.463501 |      1.537187 |    0.625320 |
| T       | shadowsocks | cyclic    | 20260919 | 0.539606 | 0.656673 | 0.671181 |      1.309317 |    0.462522 |      1.580355 |    0.643092 |
| T       | shadowsocks | cyclic    | 20260920 | 0.549183 | 0.649680 | 0.664931 |      1.314612 |    0.470567 |      1.550551 |    0.631164 |
| T       | shadowsocks | group     | 20260918 | 0.562100 | 0.657929 | 0.670139 |      1.278686 |    0.448377 |      1.464513 |    0.584963 |
| T       | shadowsocks | group     | 20260919 | 0.576828 | 0.671716 | 0.681944 |      1.289808 |    0.443965 |      1.497274 |    0.601715 |
| T       | shadowsocks | group     | 20260920 | 0.550716 | 0.650062 | 0.663889 |      1.281776 |    0.455965 |      1.470443 |    0.594914 |
| T       | shadowsocks | marginal  | 20260918 | 0.713384 | 0.732908 | 0.732292 |      1.379310 |    0.399339 |      1.491543 |    0.447581 |
| T       | shadowsocks | marginal  | 20260919 | 0.706643 | 0.731274 | 0.730903 |      1.371416 |    0.391648 |      1.510540 |    0.453515 |
| T       | shadowsocks | marginal  | 20260920 | 0.688933 | 0.716029 | 0.715278 |      1.321934 |    0.401375 |      1.434843 |    0.452586 |
| T       | shadowsocks | paired    | 20260918 | 0.664941 | 0.713773 | 0.719097 |      1.378166 |    0.403294 |      1.511692 |    0.483638 |
| T       | shadowsocks | paired    | 20260919 | 0.671943 | 0.722794 | 0.726736 |      1.354138 |    0.391196 |      1.508251 |    0.482907 |
| T       | shadowsocks | paired    | 20260920 | 0.653347 | 0.714268 | 0.720139 |      1.315812 |    0.402022 |      1.451583 |    0.487392 |
| T       | shadowsocks | raw       | 20260918 | 0.372104 | 0.586596 | 0.635069 |      1.878381 |    0.562835 |      3.450467 |    1.067157 |
| T       | shadowsocks | raw       | 20260919 | 0.350200 | 0.587086 | 0.637847 |      1.982205 |    0.566686 |      3.739705 |    1.115391 |
| T       | shadowsocks | raw       | 20260920 | 0.344468 | 0.577888 | 0.630556 |      1.887813 |    0.569746 |      3.515323 |    1.106812 |
| T       | shadowsocks | reference | 20260918 | 0.740219 | 0.743287 | 0.743056 |      1.379143 |    0.374593 |      1.318126 |    0.369020 |
| T       | shadowsocks | reference | 20260919 | 0.752525 | 0.754109 | 0.752778 |      1.327449 |    0.367438 |      1.252852 |    0.357979 |
| T       | shadowsocks | reference | 20260920 | 0.710860 | 0.709631 | 0.708333 |      1.322333 |    0.395521 |      1.266649 |    0.388476 |
| T       | trojan      | center    | 20260918 | 0.585784 | 0.663953 | 0.693056 |      1.238623 |    0.448465 |      1.741938 |    0.614040 |
| T       | trojan      | center    | 20260919 | 0.607085 | 0.679567 | 0.704514 |      1.167478 |    0.420898 |      1.603535 |    0.566033 |
| T       | trojan      | center    | 20260920 | 0.574459 | 0.652117 | 0.684028 |      1.267245 |    0.445581 |      1.805016 |    0.619198 |
| T       | trojan      | cyclic    | 20260918 | 0.584028 | 0.666311 | 0.680556 |      1.283373 |    0.464611 |      1.596018 |    0.595403 |
| T       | trojan      | cyclic    | 20260919 | 0.595877 | 0.673622 | 0.687500 |      1.264193 |    0.458911 |      1.553950 |    0.574170 |
| T       | trojan      | cyclic    | 20260920 | 0.576793 | 0.665260 | 0.681597 |      1.276546 |    0.462643 |      1.596963 |    0.594396 |
| T       | trojan      | group     | 20260918 | 0.613723 | 0.677870 | 0.689583 |      1.227918 |    0.448912 |      1.483439 |    0.553873 |
| T       | trojan      | group     | 20260919 | 0.631294 | 0.689673 | 0.701042 |      1.202905 |    0.440468 |      1.430713 |    0.531123 |
| T       | trojan      | group     | 20260920 | 0.611925 | 0.681979 | 0.696181 |      1.215542 |    0.445334 |      1.464329 |    0.546742 |
| T       | trojan      | marginal  | 20260918 | 0.693682 | 0.719424 | 0.727083 |      1.024405 |    0.383828 |      1.158203 |    0.435219 |
| T       | trojan      | marginal  | 20260919 | 0.731932 | 0.752627 | 0.756944 |      0.971606 |    0.362403 |      1.094607 |    0.405256 |
| T       | trojan      | marginal  | 20260920 | 0.695762 | 0.731398 | 0.738542 |      1.009717 |    0.376155 |      1.164299 |    0.433810 |
| T       | trojan      | paired    | 20260918 | 0.704020 | 0.737634 | 0.742708 |      0.997148 |    0.371096 |      1.144273 |    0.431131 |
| T       | trojan      | paired    | 20260919 | 0.747886 | 0.764487 | 0.767708 |      0.939613 |    0.349690 |      1.073777 |    0.399941 |
| T       | trojan      | paired    | 20260920 | 0.719263 | 0.753572 | 0.758333 |      0.959752 |    0.357307 |      1.125014 |    0.421063 |
| T       | trojan      | raw       | 20260918 | 0.072392 | 0.450737 | 0.532639 |      2.628216 |    0.701013 |      6.108258 |    1.456603 |
| T       | trojan      | raw       | 20260919 | 0.085186 | 0.455661 | 0.537500 |      2.795738 |    0.696283 |      6.649744 |    1.456925 |
| T       | trojan      | raw       | 20260920 | 0.059024 | 0.442007 | 0.526736 |      2.817472 |    0.702211 |      6.689943 |    1.466292 |
| T       | trojan      | reference | 20260918 | 0.752211 | 0.762734 | 0.764931 |      0.906136 |    0.337333 |      0.907173 |    0.336780 |
| T       | trojan      | reference | 20260919 | 0.785353 | 0.783943 | 0.784722 |      0.854770 |    0.320439 |      0.859367 |    0.322009 |
| T       | trojan      | reference | 20260920 | 0.777776 | 0.783103 | 0.784375 |      0.896862 |    0.332957 |      0.915296 |    0.337959 |
| T       | vless       | center    | 20260918 | 0.497135 | 0.602402 | 0.628819 |      1.809293 |    0.547250 |      2.470108 |    0.749476 |
| T       | vless       | center    | 20260919 | 0.485291 | 0.601396 | 0.628125 |      1.850758 |    0.550308 |      2.487925 |    0.744056 |
| T       | vless       | center    | 20260920 | 0.473266 | 0.597502 | 0.626042 |      1.862367 |    0.552157 |      2.598577 |    0.764462 |
| T       | vless       | cyclic    | 20260918 | 0.568895 | 0.654150 | 0.670486 |      1.550195 |    0.508705 |      1.799551 |    0.608921 |
| T       | vless       | cyclic    | 20260919 | 0.548960 | 0.645619 | 0.662847 |      1.584870 |    0.513873 |      1.862748 |    0.615853 |
| T       | vless       | cyclic    | 20260920 | 0.558313 | 0.645375 | 0.661806 |      1.547602 |    0.509171 |      1.816921 |    0.608565 |
| T       | vless       | group     | 20260918 | 0.616087 | 0.678945 | 0.691667 |      1.508421 |    0.490783 |      1.678479 |    0.566142 |
| T       | vless       | group     | 20260919 | 0.600122 | 0.675346 | 0.688542 |      1.547488 |    0.493530 |      1.753436 |    0.572378 |
| T       | vless       | group     | 20260920 | 0.595550 | 0.668549 | 0.681250 |      1.509097 |    0.494306 |      1.729011 |    0.575912 |
| T       | vless       | marginal  | 20260918 | 0.692764 | 0.713502 | 0.718403 |      1.515921 |    0.457098 |      1.662812 |    0.513637 |
| T       | vless       | marginal  | 20260919 | 0.696271 | 0.715813 | 0.719792 |      1.573843 |    0.462807 |      1.743645 |    0.528694 |
| T       | vless       | marginal  | 20260920 | 0.696764 | 0.723313 | 0.727778 |      1.496919 |    0.452155 |      1.674385 |    0.509224 |
| T       | vless       | paired    | 20260918 | 0.703470 | 0.725312 | 0.729167 |      1.520250 |    0.451311 |      1.681903 |    0.512186 |
| T       | vless       | paired    | 20260919 | 0.705126 | 0.726408 | 0.730556 |      1.556854 |    0.451408 |      1.710049 |    0.514002 |
| T       | vless       | paired    | 20260920 | 0.715809 | 0.736615 | 0.740278 |      1.494561 |    0.447483 |      1.677953 |    0.503843 |
| T       | vless       | raw       | 20260918 | 0.069697 | 0.431951 | 0.507639 |      3.181969 |    0.762280 |      7.040869 |    1.502951 |
| T       | vless       | raw       | 20260919 | 0.077683 | 0.434348 | 0.510764 |      3.272740 |    0.764186 |      7.232728 |    1.506816 |
| T       | vless       | raw       | 20260920 | 0.059422 | 0.427681 | 0.506944 |      3.287921 |    0.768679 |      7.369729 |    1.527823 |
| T       | vless       | reference | 20260918 | 0.731079 | 0.732481 | 0.733333 |      1.463186 |    0.420114 |      1.456833 |    0.422181 |
| T       | vless       | reference | 20260919 | 0.737453 | 0.739441 | 0.740625 |      1.516470 |    0.420455 |      1.507536 |    0.415972 |
| T       | vless       | reference | 20260920 | 0.734587 | 0.736376 | 0.737153 |      1.456046 |    0.427793 |      1.445754 |    0.427445 |
| T       | vmess       | center    | 20260918 | 0.557823 | 0.631588 | 0.654167 |      1.505457 |    0.501532 |      1.988175 |    0.649592 |
| T       | vmess       | center    | 20260919 | 0.576625 | 0.646587 | 0.668056 |      1.513478 |    0.485840 |      2.039310 |    0.638526 |
| T       | vmess       | center    | 20260920 | 0.530477 | 0.617745 | 0.643403 |      1.569968 |    0.508213 |      2.156268 |    0.675336 |
| T       | vmess       | cyclic    | 20260918 | 0.528895 | 0.615695 | 0.630903 |      1.449850 |    0.520067 |      1.789554 |    0.651940 |
| T       | vmess       | cyclic    | 20260919 | 0.549696 | 0.630006 | 0.646181 |      1.441404 |    0.506652 |      1.778393 |    0.631567 |
| T       | vmess       | cyclic    | 20260920 | 0.518650 | 0.619741 | 0.637153 |      1.445132 |    0.512979 |      1.784559 |    0.647476 |
| T       | vmess       | group     | 20260918 | 0.573435 | 0.638239 | 0.652431 |      1.391843 |    0.495777 |      1.665017 |    0.602893 |
| T       | vmess       | group     | 20260919 | 0.570159 | 0.644421 | 0.660417 |      1.388642 |    0.487156 |      1.681407 |    0.593978 |
| T       | vmess       | group     | 20260920 | 0.589733 | 0.653702 | 0.669097 |      1.380878 |    0.486410 |      1.659408 |    0.593076 |
| T       | vmess       | marginal  | 20260918 | 0.670647 | 0.689698 | 0.700347 |      1.330437 |    0.440731 |      1.480982 |    0.488983 |
| T       | vmess       | marginal  | 20260919 | 0.681637 | 0.706861 | 0.717014 |      1.302287 |    0.425796 |      1.501631 |    0.482697 |
| T       | vmess       | marginal  | 20260920 | 0.660728 | 0.688220 | 0.698611 |      1.317031 |    0.437973 |      1.513761 |    0.498570 |
| T       | vmess       | paired    | 20260918 | 0.661964 | 0.689079 | 0.698611 |      1.325917 |    0.439438 |      1.521050 |    0.509885 |
| T       | vmess       | paired    | 20260919 | 0.683933 | 0.706907 | 0.716667 |      1.302994 |    0.424178 |      1.533752 |    0.499041 |
| T       | vmess       | paired    | 20260920 | 0.654092 | 0.691527 | 0.701389 |      1.318765 |    0.434876 |      1.554685 |    0.519044 |
| T       | vmess       | raw       | 20260918 | 0.101924 | 0.445828 | 0.510417 |      3.720200 |    0.755810 |      9.012884 |    1.489778 |
| T       | vmess       | raw       | 20260919 | 0.099456 | 0.446978 | 0.514236 |      4.011072 |    0.755966 |      9.853333 |    1.504523 |
| T       | vmess       | raw       | 20260920 | 0.077279 | 0.431809 | 0.502083 |      3.823805 |    0.767768 |      9.325571 |    1.521545 |
| T       | vmess       | reference | 20260918 | 0.698520 | 0.707204 | 0.712500 |      1.273913 |    0.426422 |      1.279617 |    0.428676 |
| T       | vmess       | reference | 20260919 | 0.734646 | 0.734039 | 0.738542 |      1.206778 |    0.396038 |      1.221821 |    0.396886 |
| T       | vmess       | reference | 20260920 | 0.715885 | 0.714383 | 0.719097 |      1.227370 |    0.407083 |      1.219335 |    0.408017 |
| W       | anytls      | center    | 20260918 | 0.753589 | 0.782778 | 0.792014 |      1.923511 |    0.356479 |      1.880419 |    0.406939 |
| W       | anytls      | center    | 20260919 | 0.748821 | 0.783175 | 0.795139 |      1.711556 |    0.347711 |      1.731512 |    0.410150 |
| W       | anytls      | center    | 20260920 | 0.755523 | 0.787849 | 0.799306 |      1.745287 |    0.350822 |      1.815072 |    0.422571 |
| W       | anytls      | cyclic    | 20260918 | 0.538172 | 0.655813 | 0.685764 |      1.764910 |    0.496689 |      1.663809 |    0.548953 |
| W       | anytls      | cyclic    | 20260919 | 0.573122 | 0.676735 | 0.701389 |      1.644501 |    0.490233 |      1.564456 |    0.534306 |
| W       | anytls      | cyclic    | 20260920 | 0.567802 | 0.668636 | 0.693056 |      1.665536 |    0.489895 |      1.631330 |    0.538654 |
| W       | anytls      | group     | 20260918 | 0.626360 | 0.702372 | 0.721181 |      1.735237 |    0.478233 |      1.606795 |    0.518217 |
| W       | anytls      | group     | 20260919 | 0.633583 | 0.705723 | 0.720833 |      1.630909 |    0.477092 |      1.540009 |    0.509081 |
| W       | anytls      | group     | 20260920 | 0.625455 | 0.695434 | 0.713542 |      1.663899 |    0.478712 |      1.600154 |    0.512220 |
| W       | anytls      | marginal  | 20260918 | 0.754028 | 0.784671 | 0.794097 |      1.859276 |    0.368201 |      1.718554 |    0.407312 |
| W       | anytls      | marginal  | 20260919 | 0.767141 | 0.793083 | 0.802778 |      1.664855 |    0.357206 |      1.576772 |    0.399588 |
| W       | anytls      | marginal  | 20260920 | 0.766246 | 0.794122 | 0.802778 |      1.655657 |    0.359426 |      1.646731 |    0.404009 |
| W       | anytls      | paired    | 20260918 | 0.793670 | 0.805376 | 0.809375 |      1.967256 |    0.363580 |      1.804503 |    0.384156 |
| W       | anytls      | paired    | 20260919 | 0.797488 | 0.810111 | 0.814583 |      1.750511 |    0.354800 |      1.657853 |    0.379113 |
| W       | anytls      | paired    | 20260920 | 0.796866 | 0.806483 | 0.809375 |      1.721840 |    0.351472 |      1.697432 |    0.382961 |
| W       | anytls      | raw       | 20260918 | 0.369792 | 0.522011 | 0.579514 |      2.766856 |    0.563644 |      4.061061 |    0.866642 |
| W       | anytls      | raw       | 20260919 | 0.392525 | 0.550464 | 0.606944 |      2.481451 |    0.532556 |      3.767846 |    0.844411 |
| W       | anytls      | raw       | 20260920 | 0.397765 | 0.563400 | 0.619097 |      2.601533 |    0.536096 |      4.075685 |    0.863577 |
| W       | anytls      | reference | 20260918 | 0.806709 | 0.797681 | 0.801042 |      2.100471 |    0.349426 |      1.962157 |    0.350606 |
| W       | anytls      | reference | 20260919 | 0.815267 | 0.808703 | 0.811111 |      1.809203 |    0.334052 |      1.693036 |    0.338016 |
| W       | anytls      | reference | 20260920 | 0.805207 | 0.800618 | 0.803125 |      1.876782 |    0.333979 |      1.786727 |    0.338074 |
| W       | shadowsocks | center    | 20260918 | 0.761366 | 0.786203 | 0.794792 |      1.196103 |    0.337486 |      1.194147 |    0.390299 |
| W       | shadowsocks | center    | 20260919 | 0.766874 | 0.787526 | 0.795139 |      1.081917 |    0.337406 |      1.095429 |    0.389857 |
| W       | shadowsocks | center    | 20260920 | 0.754434 | 0.784362 | 0.793403 |      1.031754 |    0.330102 |      1.095040 |    0.387729 |
| W       | shadowsocks | cyclic    | 20260918 | 0.558019 | 0.673456 | 0.705903 |      1.338972 |    0.478973 |      1.436646 |    0.542330 |
| W       | shadowsocks | cyclic    | 20260919 | 0.571497 | 0.674156 | 0.702083 |      1.343499 |    0.475314 |      1.414323 |    0.535603 |
| W       | shadowsocks | cyclic    | 20260920 | 0.561013 | 0.664960 | 0.693750 |      1.316612 |    0.473881 |      1.406894 |    0.526572 |
| W       | shadowsocks | group     | 20260918 | 0.604765 | 0.687899 | 0.713194 |      1.307942 |    0.458623 |      1.365205 |    0.507977 |
| W       | shadowsocks | group     | 20260919 | 0.605268 | 0.687626 | 0.709375 |      1.318010 |    0.465391 |      1.355138 |    0.514387 |
| W       | shadowsocks | group     | 20260920 | 0.594552 | 0.675085 | 0.704167 |      1.272743 |    0.454907 |      1.329744 |    0.499269 |
| W       | shadowsocks | marginal  | 20260918 | 0.787821 | 0.802493 | 0.810417 |      1.140886 |    0.339396 |      1.094707 |    0.376731 |
| W       | shadowsocks | marginal  | 20260919 | 0.778671 | 0.796081 | 0.804861 |      1.057787 |    0.336501 |      1.060858 |    0.380631 |
| W       | shadowsocks | marginal  | 20260920 | 0.770261 | 0.796969 | 0.804861 |      1.008068 |    0.329114 |      1.002362 |    0.368725 |
| W       | shadowsocks | paired    | 20260918 | 0.794931 | 0.800493 | 0.806944 |      1.146118 |    0.337404 |      1.116450 |    0.362769 |
| W       | shadowsocks | paired    | 20260919 | 0.793197 | 0.803931 | 0.811458 |      1.083638 |    0.335937 |      1.065395 |    0.367020 |
| W       | shadowsocks | paired    | 20260920 | 0.775796 | 0.797814 | 0.804167 |      1.020177 |    0.326535 |      1.019006 |    0.354056 |
| W       | shadowsocks | raw       | 20260918 | 0.336227 | 0.524120 | 0.588194 |      2.168695 |    0.578729 |      3.752482 |    0.986244 |
| W       | shadowsocks | raw       | 20260919 | 0.374561 | 0.550224 | 0.610764 |      1.981898 |    0.556775 |      3.527287 |    0.947212 |
| W       | shadowsocks | raw       | 20260920 | 0.367004 | 0.544291 | 0.605903 |      2.026487 |    0.558744 |      3.727748 |    0.978280 |
| W       | shadowsocks | reference | 20260918 | 0.803503 | 0.807480 | 0.810417 |      1.247789 |    0.323604 |      1.081953 |    0.330558 |
| W       | shadowsocks | reference | 20260919 | 0.810336 | 0.815523 | 0.819097 |      1.066182 |    0.319788 |      0.971993 |    0.328283 |
| W       | shadowsocks | reference | 20260920 | 0.813340 | 0.822385 | 0.823958 |      0.983722 |    0.304032 |      0.893925 |    0.310842 |
| W       | trojan      | center    | 20260918 | 0.669141 | 0.675435 | 0.682986 |      1.398979 |    0.447038 |      1.452354 |    0.466059 |
| W       | trojan      | center    | 20260919 | 0.695138 | 0.692288 | 0.697222 |      1.283387 |    0.422880 |      1.336219 |    0.437423 |
| W       | trojan      | center    | 20260920 | 0.692238 | 0.698966 | 0.703819 |      1.349584 |    0.430335 |      1.403308 |    0.447924 |
| W       | trojan      | cyclic    | 20260918 | 0.522487 | 0.616620 | 0.641319 |      1.501737 |    0.543774 |      1.578037 |    0.602178 |
| W       | trojan      | cyclic    | 20260919 | 0.528288 | 0.617544 | 0.640625 |      1.468886 |    0.526304 |      1.564829 |    0.588412 |
| W       | trojan      | cyclic    | 20260920 | 0.550213 | 0.620759 | 0.643750 |      1.474177 |    0.533372 |      1.555537 |    0.587277 |
| W       | trojan      | group     | 20260918 | 0.577810 | 0.633814 | 0.653125 |      1.445352 |    0.522638 |      1.476268 |    0.560306 |
| W       | trojan      | group     | 20260919 | 0.584333 | 0.637587 | 0.654861 |      1.398824 |    0.510504 |      1.443454 |    0.546206 |
| W       | trojan      | group     | 20260920 | 0.577673 | 0.640208 | 0.657639 |      1.440598 |    0.523742 |      1.484801 |    0.561470 |
| W       | trojan      | marginal  | 20260918 | 0.656863 | 0.677460 | 0.684375 |      1.392302 |    0.454695 |      1.421690 |    0.477120 |
| W       | trojan      | marginal  | 20260919 | 0.682863 | 0.692998 | 0.697569 |      1.290572 |    0.432561 |      1.321121 |    0.448406 |
| W       | trojan      | marginal  | 20260920 | 0.677338 | 0.690470 | 0.694792 |      1.346451 |    0.440588 |      1.380304 |    0.458656 |
| W       | trojan      | paired    | 20260918 | 0.663272 | 0.684419 | 0.691319 |      1.389668 |    0.449984 |      1.383500 |    0.466795 |
| W       | trojan      | paired    | 20260919 | 0.674187 | 0.694251 | 0.698611 |      1.300995 |    0.433433 |      1.321540 |    0.448655 |
| W       | trojan      | paired    | 20260920 | 0.674738 | 0.693368 | 0.697569 |      1.333093 |    0.437694 |      1.353085 |    0.450889 |
| W       | trojan      | raw       | 20260918 | 0.235879 | 0.380193 | 0.441667 |      2.312292 |    0.701185 |      3.476218 |    0.970165 |
| W       | trojan      | raw       | 20260919 | 0.244387 | 0.400609 | 0.459375 |      2.147349 |    0.678510 |      3.264131 |    0.947092 |
| W       | trojan      | raw       | 20260920 | 0.225828 | 0.401224 | 0.461806 |      2.252558 |    0.686668 |      3.437822 |    0.960886 |
| W       | trojan      | reference | 20260918 | 0.677385 | 0.678675 | 0.680556 |      1.369148 |    0.449907 |      1.319397 |    0.448299 |
| W       | trojan      | reference | 20260919 | 0.681761 | 0.679811 | 0.681597 |      1.230417 |    0.425854 |      1.240691 |    0.427959 |
| W       | trojan      | reference | 20260920 | 0.690497 | 0.687215 | 0.687153 |      1.275905 |    0.433620 |      1.259752 |    0.431850 |
| W       | vless       | center    | 20260918 | 0.697181 | 0.722447 | 0.727083 |      1.726089 |    0.409310 |      1.646108 |    0.432442 |
| W       | vless       | center    | 20260919 | 0.705857 | 0.725419 | 0.729167 |      1.573914 |    0.401367 |      1.496586 |    0.426990 |
| W       | vless       | center    | 20260920 | 0.703423 | 0.729548 | 0.731250 |      1.586611 |    0.406713 |      1.531627 |    0.434287 |
| W       | vless       | cyclic    | 20260918 | 0.521570 | 0.643631 | 0.663889 |      1.728302 |    0.546959 |      1.644973 |    0.592885 |
| W       | vless       | cyclic    | 20260919 | 0.543450 | 0.650957 | 0.672222 |      1.670080 |    0.533933 |      1.573455 |    0.575575 |
| W       | vless       | cyclic    | 20260920 | 0.542642 | 0.654608 | 0.673958 |      1.618892 |    0.527571 |      1.538797 |    0.559239 |
| W       | vless       | group     | 20260918 | 0.580826 | 0.667319 | 0.682639 |      1.664605 |    0.523602 |      1.550316 |    0.551827 |
| W       | vless       | group     | 20260919 | 0.564492 | 0.659171 | 0.678819 |      1.643840 |    0.521936 |      1.523379 |    0.548615 |
| W       | vless       | group     | 20260920 | 0.582596 | 0.667066 | 0.683333 |      1.568873 |    0.512661 |      1.468256 |    0.531567 |
| W       | vless       | marginal  | 20260918 | 0.687835 | 0.725509 | 0.729861 |      1.720298 |    0.423779 |      1.622879 |    0.449121 |
| W       | vless       | marginal  | 20260919 | 0.711708 | 0.731107 | 0.735069 |      1.562498 |    0.410808 |      1.462320 |    0.433668 |
| W       | vless       | marginal  | 20260920 | 0.712623 | 0.736126 | 0.738542 |      1.527291 |    0.415983 |      1.459944 |    0.438808 |
| W       | vless       | paired    | 20260918 | 0.693500 | 0.723285 | 0.726736 |      1.738494 |    0.421158 |      1.616443 |    0.441887 |
| W       | vless       | paired    | 20260919 | 0.708246 | 0.724193 | 0.727778 |      1.606277 |    0.409505 |      1.490808 |    0.428719 |
| W       | vless       | paired    | 20260920 | 0.707201 | 0.728417 | 0.731250 |      1.543901 |    0.412855 |      1.468531 |    0.432179 |
| W       | vless       | raw       | 20260918 | 0.366160 | 0.494617 | 0.545833 |      2.374194 |    0.613351 |      3.170897 |    0.834137 |
| W       | vless       | raw       | 20260919 | 0.349437 | 0.490777 | 0.540278 |      2.244856 |    0.612399 |      2.997965 |    0.827888 |
| W       | vless       | raw       | 20260920 | 0.358148 | 0.502609 | 0.551389 |      2.196945 |    0.603854 |      3.081740 |    0.839208 |
| W       | vless       | reference | 20260918 | 0.721595 | 0.721865 | 0.729514 |      1.828214 |    0.411337 |      1.710110 |    0.407907 |
| W       | vless       | reference | 20260919 | 0.715617 | 0.719166 | 0.725694 |      1.662155 |    0.394843 |      1.546806 |    0.393634 |
| W       | vless       | reference | 20260920 | 0.708827 | 0.718614 | 0.722917 |      1.624092 |    0.401891 |      1.535196 |    0.400542 |
| W       | vmess       | center    | 20260918 | 0.677821 | 0.739993 | 0.755556 |      1.493882 |    0.389637 |      1.578418 |    0.443189 |
| W       | vmess       | center    | 20260919 | 0.678474 | 0.737414 | 0.751042 |      1.365373 |    0.388294 |      1.454916 |    0.432817 |
| W       | vmess       | center    | 20260920 | 0.673123 | 0.738770 | 0.754167 |      1.358151 |    0.389746 |      1.431620 |    0.447914 |
| W       | vmess       | cyclic    | 20260918 | 0.568212 | 0.669243 | 0.703472 |      1.382836 |    0.475556 |      1.520389 |    0.561368 |
| W       | vmess       | cyclic    | 20260919 | 0.586148 | 0.676799 | 0.707639 |      1.348381 |    0.468428 |      1.441228 |    0.542473 |
| W       | vmess       | cyclic    | 20260920 | 0.570757 | 0.670500 | 0.702083 |      1.318880 |    0.469094 |      1.424228 |    0.540973 |
| W       | vmess       | group     | 20260918 | 0.601316 | 0.680862 | 0.711111 |      1.348629 |    0.457637 |      1.423091 |    0.523452 |
| W       | vmess       | group     | 20260919 | 0.615616 | 0.689987 | 0.716319 |      1.321277 |    0.456570 |      1.381615 |    0.510797 |
| W       | vmess       | group     | 20260920 | 0.604938 | 0.678692 | 0.706250 |      1.329475 |    0.462786 |      1.368917 |    0.514865 |
| W       | vmess       | marginal  | 20260918 | 0.683724 | 0.736108 | 0.750000 |      1.446850 |    0.396724 |      1.454157 |    0.431502 |
| W       | vmess       | marginal  | 20260919 | 0.668561 | 0.725475 | 0.739583 |      1.314291 |    0.400259 |      1.365406 |    0.437088 |
| W       | vmess       | marginal  | 20260920 | 0.656789 | 0.725420 | 0.740625 |      1.319137 |    0.397668 |      1.343356 |    0.438557 |
| W       | vmess       | paired    | 20260918 | 0.701971 | 0.743564 | 0.757639 |      1.444628 |    0.385561 |      1.406734 |    0.406717 |
| W       | vmess       | paired    | 20260919 | 0.681832 | 0.735139 | 0.749306 |      1.300144 |    0.386871 |      1.288399 |    0.410187 |
| W       | vmess       | paired    | 20260920 | 0.676530 | 0.736357 | 0.750694 |      1.320362 |    0.384346 |      1.291753 |    0.413689 |
| W       | vmess       | raw       | 20260918 | 0.272429 | 0.450878 | 0.511806 |      2.479989 |    0.650553 |      4.105682 |    1.018963 |
| W       | vmess       | raw       | 20260919 | 0.281295 | 0.457168 | 0.516667 |      2.305661 |    0.647204 |      3.878744 |    1.012277 |
| W       | vmess       | raw       | 20260920 | 0.275409 | 0.466923 | 0.526736 |      2.367408 |    0.648120 |      4.127613 |    1.038445 |
| W       | vmess       | reference | 20260918 | 0.749299 | 0.749791 | 0.761111 |      1.376870 |    0.355985 |      1.339999 |    0.353161 |
| W       | vmess       | reference | 20260919 | 0.731826 | 0.736945 | 0.748264 |      1.319990 |    0.368900 |      1.310328 |    0.370612 |
| W       | vmess       | reference | 20260920 | 0.748943 | 0.745017 | 0.753819 |      1.243618 |    0.360820 |      1.230281 |    0.359592 |

## 错误修复与新增

| track   | protocol    | contrast         | business_role   |   repaired |   introduced |   changed |
|:--------|:------------|:-----------------|:----------------|-----------:|-------------:|----------:|
| T       | shadowsocks | paired-center    | cal             |        443 |          304 |       869 |
| T       | shadowsocks | paired-center    | new             |        545 |          277 |       885 |
| T       | shadowsocks | paired-cyclic    | cal             |        378 |          261 |       790 |
| T       | shadowsocks | paired-cyclic    | new             |        463 |          109 |       636 |
| T       | shadowsocks | paired-group     | cal             |        373 |          238 |       754 |
| T       | shadowsocks | paired-group     | new             |        407 |          110 |       577 |
| T       | shadowsocks | paired-marginal  | cal             |        246 |          136 |       482 |
| T       | shadowsocks | paired-marginal  | new             |        104 |          250 |       379 |
| T       | shadowsocks | paired-raw       | cal             |        262 |          407 |       781 |
| T       | shadowsocks | paired-raw       | new             |        985 |           84 |      1143 |
| T       | shadowsocks | paired-reference | cal             |        366 |          146 |       618 |
| T       | shadowsocks | paired-reference | new             |         54 |          384 |       478 |
| T       | trojan      | paired-center    | cal             |        391 |          205 |       656 |
| T       | trojan      | paired-center    | new             |        431 |           78 |       586 |
| T       | trojan      | paired-cyclic    | cal             |        493 |          326 |       907 |
| T       | trojan      | paired-cyclic    | new             |        540 |           76 |       696 |
| T       | trojan      | paired-group     | cal             |        469 |          257 |       814 |
| T       | trojan      | paired-group     | new             |        412 |          100 |       581 |
| T       | trojan      | paired-marginal  | cal             |        189 |           77 |       292 |
| T       | trojan      | paired-marginal  | new             |        101 |           80 |       193 |
| T       | trojan      | paired-raw       | cal             |        531 |          497 |      1214 |
| T       | trojan      | paired-raw       | new             |       1905 |            4 |      2061 |
| T       | trojan      | paired-reference | cal             |        162 |          142 |       339 |
| T       | trojan      | paired-reference | new             |         53 |          261 |       340 |
| T       | vless       | paired-center    | cal             |        454 |          149 |       643 |
| T       | vless       | paired-center    | new             |        679 |           71 |       802 |
| T       | vless       | paired-cyclic    | cal             |        368 |          187 |       661 |
| T       | vless       | paired-cyclic    | new             |        491 |           82 |       654 |
| T       | vless       | paired-group     | cal             |        278 |          134 |       480 |
| T       | vless       | paired-group     | new             |        336 |           81 |       485 |
| T       | vless       | paired-marginal  | cal             |        150 |           60 |       231 |
| T       | vless       | paired-marginal  | new             |         80 |           72 |       179 |
| T       | vless       | paired-raw       | cal             |        460 |          378 |      1110 |
| T       | vless       | paired-raw       | new             |       1869 |            8 |      1987 |
| T       | vless       | paired-reference | cal             |        249 |          141 |       418 |
| T       | vless       | paired-reference | new             |         77 |          217 |       300 |
| T       | vmess       | paired-center    | cal             |        378 |          261 |       795 |
| T       | vmess       | paired-center    | new             |        457 |          139 |       680 |
| T       | vmess       | paired-cyclic    | cal             |        338 |          189 |       708 |
| T       | vmess       | paired-cyclic    | new             |        501 |           67 |       698 |
| T       | vmess       | paired-group     | cal             |        273 |          150 |       585 |
| T       | vmess       | paired-group     | new             |        338 |           73 |       536 |
| T       | vmess       | paired-marginal  | cal             |        142 |           96 |       310 |
| T       | vmess       | paired-marginal  | new             |         82 |          126 |       238 |
| T       | vmess       | paired-raw       | cal             |        462 |          457 |      1203 |
| T       | vmess       | paired-raw       | new             |       1713 |           19 |      1879 |
| T       | vmess       | paired-reference | cal             |        241 |          170 |       475 |
| T       | vmess       | paired-reference | new             |         48 |          273 |       341 |
| W       | anytls      | paired-center    | cal             |        197 |          178 |       452 |
| W       | anytls      | paired-center    | new             |        203 |           87 |       320 |
| W       | anytls      | paired-cyclic    | cal             |        630 |          349 |      1123 |
| W       | anytls      | paired-cyclic    | new             |        798 |           62 |       919 |
| W       | anytls      | paired-group     | cal             |        564 |          296 |       976 |
| W       | anytls      | paired-group     | new             |        600 |           68 |       713 |
| W       | anytls      | paired-marginal  | cal             |        121 |          121 |       307 |
| W       | anytls      | paired-marginal  | new             |        162 |           65 |       252 |
| W       | anytls      | paired-raw       | cal             |        836 |          294 |      1439 |
| W       | anytls      | paired-raw       | new             |       1298 |           32 |      1590 |
| W       | anytls      | paired-reference | cal             |        244 |          129 |       468 |
| W       | anytls      | paired-reference | new             |        101 |          164 |       303 |
| W       | shadowsocks | paired-center    | cal             |        168 |          150 |       372 |
| W       | shadowsocks | paired-center    | new             |        136 |           41 |       184 |
| W       | shadowsocks | paired-cyclic    | cal             |        653 |          406 |      1185 |
| W       | shadowsocks | paired-cyclic    | new             |        741 |           64 |       845 |
| W       | shadowsocks | paired-group     | cal             |        658 |          359 |      1120 |
| W       | shadowsocks | paired-group     | new             |        613 |           60 |       695 |
| W       | shadowsocks | paired-marginal  | cal             |         75 |          113 |       215 |
| W       | shadowsocks | paired-marginal  | new             |         85 |           40 |       131 |
| W       | shadowsocks | paired-raw       | cal             |        772 |          335 |      1363 |
| W       | shadowsocks | paired-raw       | new             |       1360 |           18 |      1541 |
| W       | shadowsocks | paired-reference | cal             |        179 |          195 |       406 |
| W       | shadowsocks | paired-reference | new             |         68 |          141 |       230 |
| W       | trojan      | paired-center    | cal             |        238 |          190 |       604 |
| W       | trojan      | paired-center    | new             |         92 |          130 |       284 |
| W       | trojan      | paired-cyclic    | cal             |        492 |          501 |      1246 |
| W       | trojan      | paired-cyclic    | new             |        581 |          106 |       788 |
| W       | trojan      | paired-group     | cal             |        449 |          428 |      1098 |
| W       | trojan      | paired-group     | new             |        461 |          131 |       698 |
| W       | trojan      | paired-marginal  | cal             |        138 |          130 |       382 |
| W       | trojan      | paired-marginal  | new             |         86 |           63 |       195 |
| W       | trojan      | paired-raw       | cal             |       1291 |          420 |      2325 |
| W       | trojan      | paired-raw       | new             |       1229 |           13 |      1614 |
| W       | trojan      | paired-reference | cal             |        356 |          182 |       684 |
| W       | trojan      | paired-reference | new             |        134 |          198 |       390 |
| W       | vless       | paired-center    | cal             |        191 |          210 |       543 |
| W       | vless       | paired-center    | new             |        131 |          117 |       302 |
| W       | vless       | paired-cyclic    | cal             |        407 |          398 |      1055 |
| W       | vless       | paired-cyclic    | new             |        592 |           95 |       808 |
| W       | vless       | paired-group     | cal             |        418 |          374 |       995 |
| W       | vless       | paired-group     | new             |        466 |          104 |       661 |
| W       | vless       | paired-marginal  | cal             |         82 |          156 |       357 |
| W       | vless       | paired-marginal  | new             |         94 |           71 |       202 |
| W       | vless       | paired-raw       | cal             |        988 |          332 |      1871 |
| W       | vless       | paired-raw       | new             |        987 |           64 |      1358 |
| W       | vless       | paired-reference | cal             |        266 |          154 |       569 |
| W       | vless       | paired-reference | new             |         71 |          161 |       292 |
| W       | vmess       | paired-center    | cal             |        206 |          250 |       499 |
| W       | vmess       | paired-center    | new             |        136 |          101 |       261 |
| W       | vmess       | paired-cyclic    | cal             |        469 |          370 |       972 |
| W       | vmess       | paired-cyclic    | new             |        429 |          112 |       572 |
| W       | vmess       | paired-group     | cal             |        490 |          336 |       924 |
| W       | vmess       | paired-group     | new             |        338 |          135 |       506 |
| W       | vmess       | paired-marginal  | cal             |        154 |          135 |       325 |
| W       | vmess       | paired-marginal  | new             |        110 |           50 |       175 |
| W       | vmess       | paired-raw       | cal             |       1174 |          276 |      1790 |
| W       | vmess       | paired-raw       | new             |       1138 |           13 |      1537 |
| W       | vmess       | paired-reference | cal             |        466 |          215 |       765 |
| W       | vmess       | paired-reference | new             |         62 |          329 |       440 |

## 计数与解释边界

每部署每个对照，新增业务错误表包含 2880 个预测实例，即 120 个独立访问 × 8 轮换 × 3 种子；校准业务为 5760 个实例。同一内容重复、种子与轮换不是新的独立样本。逐类别作为新增业务只取该类别被留作新增业务的业务组；校准业务表平均另外两个组。逐 seed 表先平均业务组与轮换，不是 seed 级显著性检验。

所有九个轨道与部署组合通过预定双增量，不意味着条件模型普遍最优。T 的 SS 上 paired−marginal 为负且普通区间不跨零；W 的 Trojan/VLESS 与简单漂移方法接近。Brier 的改善不能替代 CE 的独立检查。区间条件于既有模型、内容和校准集合，不是外部验证；区间跨零不等于等效。
