# Extend 机制条件化配对表示学习正式结果

日期：2026-10-04。本报告区分固定候选的实测结果、解释性诊断与未验证外推。五项主比较中 1 项建立正向校正区间，不能宣称完整假设全部通过。

## 数据模型与权限

仅已见五部署 E1、600访问、30内容、六业务、四重复、全局内容五折。W含重复传输，P为正载荷事件，R为窗口全局方向段，不是旧FR。Hy2、E2、外部日期、独立配置及在线无索引识别均未执行。 正式推理只有post六量。所有训练/编码/推理使用CUDA，无TF32/AMP。B4/B5/B6使用旧P3的18内容拟合、6内容查询decoded中心，不用真实query漂移；B6全流程匿名组。 E为6→64→32，P为32→32→16，A为无偏置6→32；最终E+32→32→6共3782参数。各SSL1000步，微调/探针1000步，B0L监督2000步；三seed固定，不早停、不选择测试checkpoint。

## 完整实验臂

B0同架构监督；B0L同总更新监督；B1充分post SSL；B2两侧侧内SSL；B3无条件真配；B4通用中心条件；B5机制中心条件主方法；B6匿名组条件。所有SSL每步四编码槽；B1四post，B2两post两pre，B3至B6三post一pre。因此编码槽数相同不意味着各侧曝光完全相同。组级16组合不是16独立访问。

## 最终业务表现

| arm   |       F1 |   min_seed |   max_seed |   worst_F1 |   CE_bits |    Brier |
|:------|---------:|-----------:|-----------:|-----------:|----------:|---------:|
| B0    | 0.768447 |   0.760448 |   0.782992 |   0.735034 |  1.161222 | 0.328063 |
| B0L   | 0.766975 |   0.764252 |   0.769993 |   0.727432 |  1.619890 | 0.348138 |
| B1    | 0.773833 |   0.770131 |   0.781091 |   0.743662 |  1.118941 | 0.321803 |
| B2    | 0.778655 |   0.770624 |   0.783031 |   0.722941 |  1.134280 | 0.315337 |
| B3    | 0.774352 |   0.771461 |   0.777339 |   0.737675 |  1.065742 | 0.314896 |
| B4    | 0.777292 |   0.771478 |   0.785849 |   0.738404 |  1.082292 | 0.314895 |
| B5    | 0.780593 |   0.774039 |   0.785715 |   0.752253 |  1.107235 | 0.316050 |
| B6    | 0.769109 |   0.760862 |   0.776429 |   0.736609 |  1.151282 | 0.325962 |

## 五项主要比较与解释比较

| contrast   | primary   |    delta |     low95 |   high95 |   adjusted_low |   adjusted_high |
|:-----------|:----------|---------:|----------:|---------:|---------------:|----------------:|
| B5-B0      | True      | 0.012146 |  0.002147 | 0.022463 |      -0.000590 |        0.026247 |
| B5-B0L     | True      | 0.013618 |  0.003311 | 0.024134 |       0.000007 |        0.027456 |
| B5-B1      | True      | 0.006760 | -0.003493 | 0.016488 |      -0.007059 |        0.019133 |
| B5-B2      | False     | 0.001938 | -0.007095 | 0.011693 |     nan        |      nan        |
| B5-B3      | False     | 0.006242 | -0.001743 | 0.013377 |     nan        |      nan        |
| B5-B4      | True      | 0.003302 | -0.003416 | 0.010059 |      -0.005619 |        0.012388 |
| B5-B6      | True      | 0.011485 |  0.001101 | 0.023155 |      -0.001491 |        0.027025 |

10,000次按业务分层内容簇bootstrap，部署/seed/方法共享成员。五项主家族分位0.005/0.995；次要比较为普通95%。区间条件于固定模型，跨零不是等效。

## 冻结表示的业务可读性

| stage   | arm   | head   |       F1 |   min_seed |   max_seed |   worst_F1 |   CE_bits |    Brier |
|:--------|:------|:-------|---------:|-----------:|-----------:|-----------:|----------:|---------:|
| probe   | B1    | linear | 0.639310 |   0.632118 |   0.642927 |   0.511702 |  1.400920 | 0.485675 |
| probe   | B1    | mlp    | 0.736386 |   0.719598 |   0.759399 |   0.670263 |  1.062360 | 0.351630 |
| probe   | B2    | linear | 0.633061 |   0.611271 |   0.651872 |   0.492782 |  1.400614 | 0.489397 |
| probe   | B2    | mlp    | 0.747021 |   0.733371 |   0.761972 |   0.686430 |  1.059498 | 0.350912 |
| probe   | B3    | linear | 0.662403 |   0.661025 |   0.664441 |   0.543898 |  1.363721 | 0.473406 |
| probe   | B3    | mlp    | 0.746512 |   0.736325 |   0.761182 |   0.683278 |  1.067319 | 0.339274 |
| probe   | B4    | linear | 0.663520 |   0.657543 |   0.667753 |   0.555671 |  1.354851 | 0.471526 |
| probe   | B4    | mlp    | 0.751558 |   0.739749 |   0.767357 |   0.691507 |  1.078820 | 0.345692 |
| probe   | B5    | linear | 0.665009 |   0.660121 |   0.668521 |   0.552503 |  1.353809 | 0.469354 |
| probe   | B5    | mlp    | 0.746133 |   0.730487 |   0.757990 |   0.687686 |  1.068688 | 0.346237 |
| probe   | B6    | linear | 0.667107 |   0.665407 |   0.670069 |   0.538332 |  1.272434 | 0.439570 |
| probe   | B6    | mlp    | 0.750074 |   0.743553 |   0.755606 |   0.703758 |  1.070590 | 0.339004 |
| probe   | R0    | linear | 0.662261 |   0.657479 |   0.668162 |   0.532643 |  1.301118 | 0.459084 |
| probe   | R0    | mlp    | 0.751450 |   0.727718 |   0.766454 |   0.692173 |  1.062073 | 0.340150 |

R0是未训练随机E，不是已接受标签的B0。线性和MLP各自使用相同读出预算，诊断不替代最终主终点。

## 逐部署成绩

| stage    | arm   | head   | protocol    |       F1 |   accuracy |   CE_bits |    Brier |
|:---------|:------|:-------|:------------|---------:|-----------:|----------:|---------:|
| finetune | B0    | mlp    | anytls      | 0.797338 |   0.808333 |  0.866855 | 0.284716 |
| finetune | B0    | mlp    | shadowsocks | 0.791242 |   0.794444 |  1.240675 | 0.311220 |
| finetune | B0    | mlp    | trojan      | 0.740963 |   0.738889 |  1.296936 | 0.365105 |
| finetune | B0    | mlp    | vless       | 0.746737 |   0.744444 |  1.368342 | 0.355034 |
| finetune | B0    | mlp    | vmess       | 0.765955 |   0.772222 |  1.033300 | 0.324238 |
| finetune | B0L   | mlp    | anytls      | 0.796943 |   0.808333 |  1.311805 | 0.296457 |
| finetune | B0L   | mlp    | shadowsocks | 0.792916 |   0.794444 |  1.694760 | 0.324810 |
| finetune | B0L   | mlp    | trojan      | 0.727432 |   0.725000 |  1.767076 | 0.391180 |
| finetune | B0L   | mlp    | vless       | 0.757051 |   0.755556 |  1.961423 | 0.377849 |
| finetune | B0L   | mlp    | vmess       | 0.760533 |   0.766667 |  1.364384 | 0.350391 |
| finetune | B1    | mlp    | anytls      | 0.814936 |   0.822222 |  0.852820 | 0.272479 |
| finetune | B1    | mlp    | shadowsocks | 0.780763 |   0.783333 |  1.154704 | 0.306695 |
| finetune | B1    | mlp    | trojan      | 0.743662 |   0.741667 |  1.256412 | 0.354424 |
| finetune | B1    | mlp    | vless       | 0.765222 |   0.763889 |  1.341444 | 0.353536 |
| finetune | B1    | mlp    | vmess       | 0.764585 |   0.772222 |  0.989325 | 0.321880 |
| finetune | B2    | mlp    | anytls      | 0.822023 |   0.830556 |  0.768821 | 0.255387 |
| finetune | B2    | mlp    | shadowsocks | 0.806290 |   0.808333 |  1.189726 | 0.297613 |
| finetune | B2    | mlp    | trojan      | 0.722941 |   0.722222 |  1.334231 | 0.363008 |
| finetune | B2    | mlp    | vless       | 0.780076 |   0.777778 |  1.360022 | 0.339628 |
| finetune | B2    | mlp    | vmess       | 0.761947 |   0.769444 |  1.018597 | 0.321047 |
| finetune | B3    | mlp    | anytls      | 0.814712 |   0.822222 |  0.783900 | 0.260890 |
| finetune | B3    | mlp    | shadowsocks | 0.788887 |   0.791667 |  1.066077 | 0.291424 |
| finetune | B3    | mlp    | trojan      | 0.739871 |   0.738889 |  1.305753 | 0.360869 |
| finetune | B3    | mlp    | vless       | 0.760510 |   0.758333 |  1.198032 | 0.342844 |
| finetune | B3    | mlp    | vmess       | 0.767777 |   0.775000 |  0.974949 | 0.318451 |
| finetune | B4    | mlp    | anytls      | 0.817106 |   0.827778 |  0.775541 | 0.252788 |
| finetune | B4    | mlp    | shadowsocks | 0.802927 |   0.805556 |  1.091632 | 0.289863 |
| finetune | B4    | mlp    | trojan      | 0.746607 |   0.744444 |  1.280130 | 0.353727 |
| finetune | B4    | mlp    | vless       | 0.755719 |   0.752778 |  1.256791 | 0.357582 |
| finetune | B4    | mlp    | vmess       | 0.764100 |   0.769444 |  1.007364 | 0.320517 |
| finetune | B5    | mlp    | anytls      | 0.810186 |   0.822222 |  0.778091 | 0.252432 |
| finetune | B5    | mlp    | shadowsocks | 0.800085 |   0.802778 |  1.109000 | 0.294096 |
| finetune | B5    | mlp    | trojan      | 0.752253 |   0.750000 |  1.326722 | 0.359120 |
| finetune | B5    | mlp    | vless       | 0.768440 |   0.766667 |  1.283786 | 0.349788 |
| finetune | B5    | mlp    | vmess       | 0.772004 |   0.777778 |  1.038579 | 0.324813 |
| finetune | B6    | mlp    | anytls      | 0.793862 |   0.805556 |  0.792539 | 0.272100 |
| finetune | B6    | mlp    | shadowsocks | 0.796892 |   0.800000 |  1.255388 | 0.303981 |
| finetune | B6    | mlp    | trojan      | 0.736609 |   0.736111 |  1.370310 | 0.372872 |
| finetune | B6    | mlp    | vless       | 0.753879 |   0.752778 |  1.333866 | 0.352990 |
| finetune | B6    | mlp    | vmess       | 0.764300 |   0.772222 |  1.004306 | 0.327867 |
| probe    | B1    | linear | anytls      | 0.767650 |   0.780556 |  1.203738 | 0.412267 |
| probe    | B1    | linear | shadowsocks | 0.511702 |   0.552778 |  1.652779 | 0.563119 |
| probe    | B1    | linear | trojan      | 0.578233 |   0.575000 |  1.502829 | 0.535171 |
| probe    | B1    | linear | vless       | 0.635189 |   0.630556 |  1.454866 | 0.500837 |
| probe    | B1    | linear | vmess       | 0.703774 |   0.722222 |  1.190390 | 0.416982 |
| probe    | B1    | mlp    | anytls      | 0.797541 |   0.805556 |  0.781710 | 0.275352 |
| probe    | B1    | mlp    | shadowsocks | 0.676797 |   0.694444 |  1.194554 | 0.409346 |
| probe    | B1    | mlp    | trojan      | 0.699890 |   0.697222 |  1.290360 | 0.412180 |
| probe    | B1    | mlp    | vless       | 0.725651 |   0.725000 |  1.107841 | 0.351536 |
| probe    | B1    | mlp    | vmess       | 0.782049 |   0.788889 |  0.937333 | 0.309733 |
| probe    | B2    | linear | anytls      | 0.744250 |   0.758333 |  1.232681 | 0.418202 |
| probe    | B2    | linear | shadowsocks | 0.495050 |   0.544444 |  1.643075 | 0.562513 |
| probe    | B2    | linear | trojan      | 0.570232 |   0.563889 |  1.520004 | 0.545528 |
| probe    | B2    | linear | vless       | 0.635473 |   0.630556 |  1.441808 | 0.504579 |
| probe    | B2    | linear | vmess       | 0.720299 |   0.736111 |  1.165503 | 0.416163 |
| probe    | B2    | mlp    | anytls      | 0.814478 |   0.822222 |  0.782912 | 0.277523 |
| probe    | B2    | mlp    | shadowsocks | 0.689520 |   0.702778 |  1.215870 | 0.398926 |
| probe    | B2    | mlp    | trojan      | 0.715832 |   0.713889 |  1.259687 | 0.406581 |
| probe    | B2    | mlp    | vless       | 0.733298 |   0.733333 |  1.136839 | 0.360855 |
| probe    | B2    | mlp    | vmess       | 0.781979 |   0.788889 |  0.902182 | 0.310675 |
| probe    | B3    | linear | anytls      | 0.755086 |   0.766667 |  1.184692 | 0.410218 |
| probe    | B3    | linear | shadowsocks | 0.543898 |   0.569444 |  1.635895 | 0.550579 |
| probe    | B3    | linear | trojan      | 0.620492 |   0.619444 |  1.473992 | 0.521912 |
| probe    | B3    | linear | vless       | 0.652869 |   0.650000 |  1.379318 | 0.485027 |
| probe    | B3    | linear | vmess       | 0.739672 |   0.755556 |  1.144707 | 0.399297 |
| probe    | B3    | mlp    | anytls      | 0.787349 |   0.797222 |  0.750660 | 0.267698 |
| probe    | B3    | mlp    | shadowsocks | 0.685821 |   0.702778 |  1.154882 | 0.382861 |
| probe    | B3    | mlp    | trojan      | 0.727072 |   0.725000 |  1.315259 | 0.391035 |
| probe    | B3    | mlp    | vless       | 0.756586 |   0.755556 |  1.120329 | 0.350220 |
| probe    | B3    | mlp    | vmess       | 0.775730 |   0.783333 |  0.995466 | 0.304556 |
| probe    | B4    | linear | anytls      | 0.766487 |   0.780556 |  1.177110 | 0.403656 |
| probe    | B4    | linear | shadowsocks | 0.555671 |   0.580556 |  1.619851 | 0.552650 |
| probe    | B4    | linear | trojan      | 0.611375 |   0.608333 |  1.463492 | 0.523026 |
| probe    | B4    | linear | vless       | 0.667518 |   0.663889 |  1.381939 | 0.482577 |
| probe    | B4    | linear | vmess       | 0.716549 |   0.738889 |  1.131864 | 0.395719 |
| probe    | B4    | mlp    | anytls      | 0.811944 |   0.822222 |  0.753803 | 0.268300 |
| probe    | B4    | mlp    | shadowsocks | 0.705533 |   0.719444 |  1.179748 | 0.389673 |
| probe    | B4    | mlp    | trojan      | 0.717429 |   0.713889 |  1.313682 | 0.408884 |
| probe    | B4    | mlp    | vless       | 0.734304 |   0.733333 |  1.168555 | 0.356930 |
| probe    | B4    | mlp    | vmess       | 0.788580 |   0.794444 |  0.978313 | 0.304675 |
| probe    | B5    | linear | anytls      | 0.742600 |   0.758333 |  1.182750 | 0.404297 |
| probe    | B5    | linear | shadowsocks | 0.552503 |   0.580556 |  1.609095 | 0.549851 |
| probe    | B5    | linear | trojan      | 0.608849 |   0.605556 |  1.471550 | 0.523820 |
| probe    | B5    | linear | vless       | 0.672546 |   0.669444 |  1.373216 | 0.474620 |
| probe    | B5    | linear | vmess       | 0.748547 |   0.763889 |  1.132435 | 0.394183 |
| probe    | B5    | mlp    | anytls      | 0.801334 |   0.808333 |  0.750793 | 0.270829 |
| probe    | B5    | mlp    | shadowsocks | 0.692537 |   0.708333 |  1.182001 | 0.386562 |
| probe    | B5    | mlp    | trojan      | 0.710196 |   0.708333 |  1.348341 | 0.410075 |
| probe    | B5    | mlp    | vless       | 0.730485 |   0.727778 |  1.101156 | 0.358706 |
| probe    | B5    | mlp    | vmess       | 0.796113 |   0.802778 |  0.961150 | 0.305012 |
| probe    | B6    | linear | anytls      | 0.756539 |   0.766667 |  1.089496 | 0.372153 |
| probe    | B6    | linear | shadowsocks | 0.538332 |   0.572222 |  1.510622 | 0.516844 |
| probe    | B6    | linear | trojan      | 0.609884 |   0.605556 |  1.412292 | 0.501567 |
| probe    | B6    | linear | vless       | 0.691660 |   0.686111 |  1.310976 | 0.452879 |
| probe    | B6    | linear | vmess       | 0.739121 |   0.758333 |  1.038786 | 0.354407 |
| probe    | B6    | mlp    | anytls      | 0.796454 |   0.805556 |  0.736654 | 0.271672 |
| probe    | B6    | mlp    | shadowsocks | 0.735681 |   0.744444 |  1.113928 | 0.355933 |
| probe    | B6    | mlp    | trojan      | 0.703758 |   0.700000 |  1.275968 | 0.401436 |
| probe    | B6    | mlp    | vless       | 0.739406 |   0.736111 |  1.227422 | 0.359141 |
| probe    | B6    | mlp    | vmess       | 0.775072 |   0.783333 |  0.998977 | 0.306837 |
| probe    | R0    | linear | anytls      | 0.769155 |   0.777778 |  1.126885 | 0.394673 |
| probe    | R0    | linear | shadowsocks | 0.536513 |   0.577778 |  1.539011 | 0.530142 |
| probe    | R0    | linear | trojan      | 0.584493 |   0.580556 |  1.423086 | 0.519942 |
| probe    | R0    | linear | vless       | 0.676277 |   0.672222 |  1.386308 | 0.475589 |
| probe    | R0    | linear | vmess       | 0.744867 |   0.761111 |  1.030301 | 0.375075 |
| probe    | R0    | mlp    | anytls      | 0.804040 |   0.811111 |  0.765603 | 0.273767 |
| probe    | R0    | mlp    | shadowsocks | 0.754989 |   0.761111 |  1.084420 | 0.360293 |
| probe    | R0    | mlp    | trojan      | 0.692173 |   0.688889 |  1.283383 | 0.401473 |
| probe    | R0    | mlp    | vless       | 0.745929 |   0.744444 |  1.197609 | 0.359817 |
| probe    | R0    | mlp    | vmess       | 0.760118 |   0.769444 |  0.979350 | 0.305400 |

## 逐业务成绩

| stage    | arm   | head   | class                                |   precision |   recall |       F1 |
|:---------|:------|:-------|:-------------------------------------|------------:|---------:|---------:|
| finetune | B0    | mlp    | bing.com::search_results_view        |    0.798385 | 0.703333 | 0.745054 |
| finetune | B0    | mlp    | developer.mozilla.org::document_view |    0.596979 | 0.703333 | 0.643071 |
| finetune | B0    | mlp    | github.com::repository_view          |    0.842857 | 0.853333 | 0.839673 |
| finetune | B0    | mlp    | wikipedia.org::article_view          |    0.654172 | 0.506667 | 0.554799 |
| finetune | B0    | mlp    | youtube.com::search_results_view     |    0.883665 | 0.920000 | 0.899892 |
| finetune | B0    | mlp    | youtube.com::video_playback          |    0.918948 | 0.943333 | 0.928194 |
| finetune | B0L   | mlp    | bing.com::search_results_view        |    0.767015 | 0.706667 | 0.733010 |
| finetune | B0L   | mlp    | developer.mozilla.org::document_view |    0.600046 | 0.700000 | 0.644397 |
| finetune | B0L   | mlp    | github.com::repository_view          |    0.859751 | 0.870000 | 0.860132 |
| finetune | B0L   | mlp    | wikipedia.org::article_view          |    0.654454 | 0.513333 | 0.562186 |
| finetune | B0L   | mlp    | youtube.com::search_results_view     |    0.863719 | 0.903333 | 0.882197 |
| finetune | B0L   | mlp    | youtube.com::video_playback          |    0.916823 | 0.926667 | 0.919928 |
| finetune | B1    | mlp    | bing.com::search_results_view        |    0.820215 | 0.730000 | 0.769351 |
| finetune | B1    | mlp    | developer.mozilla.org::document_view |    0.589146 | 0.706667 | 0.641265 |
| finetune | B1    | mlp    | github.com::repository_view          |    0.856143 | 0.846667 | 0.843045 |
| finetune | B1    | mlp    | wikipedia.org::article_view          |    0.646078 | 0.503333 | 0.557381 |
| finetune | B1    | mlp    | youtube.com::search_results_view     |    0.882417 | 0.930000 | 0.903850 |
| finetune | B1    | mlp    | youtube.com::video_playback          |    0.918818 | 0.943333 | 0.928108 |
| finetune | B2    | mlp    | bing.com::search_results_view        |    0.820980 | 0.730000 | 0.769044 |
| finetune | B2    | mlp    | developer.mozilla.org::document_view |    0.608020 | 0.690000 | 0.644477 |
| finetune | B2    | mlp    | github.com::repository_view          |    0.861140 | 0.866667 | 0.855573 |
| finetune | B2    | mlp    | wikipedia.org::article_view          |    0.649468 | 0.526667 | 0.570116 |
| finetune | B2    | mlp    | youtube.com::search_results_view     |    0.873807 | 0.926667 | 0.897561 |
| finetune | B2    | mlp    | youtube.com::video_playback          |    0.925290 | 0.950000 | 0.935162 |
| finetune | B3    | mlp    | bing.com::search_results_view        |    0.816140 | 0.730000 | 0.767973 |
| finetune | B3    | mlp    | developer.mozilla.org::document_view |    0.593762 | 0.686667 | 0.633225 |
| finetune | B3    | mlp    | github.com::repository_view          |    0.859436 | 0.860000 | 0.852942 |
| finetune | B3    | mlp    | wikipedia.org::article_view          |    0.650844 | 0.523333 | 0.567892 |
| finetune | B3    | mlp    | youtube.com::search_results_view     |    0.868786 | 0.916667 | 0.891005 |
| finetune | B3    | mlp    | youtube.com::video_playback          |    0.924300 | 0.946667 | 0.933073 |
| finetune | B4    | mlp    | bing.com::search_results_view        |    0.827214 | 0.746667 | 0.782002 |
| finetune | B4    | mlp    | developer.mozilla.org::document_view |    0.589362 | 0.693333 | 0.634846 |
| finetune | B4    | mlp    | github.com::repository_view          |    0.862009 | 0.866667 | 0.858324 |
| finetune | B4    | mlp    | wikipedia.org::article_view          |    0.653991 | 0.506667 | 0.555899 |
| finetune | B4    | mlp    | youtube.com::search_results_view     |    0.875832 | 0.923333 | 0.897150 |
| finetune | B4    | mlp    | youtube.com::video_playback          |    0.932123 | 0.943333 | 0.935529 |
| finetune | B5    | mlp    | bing.com::search_results_view        |    0.833389 | 0.743333 | 0.781085 |
| finetune | B5    | mlp    | developer.mozilla.org::document_view |    0.599042 | 0.703333 | 0.643828 |
| finetune | B5    | mlp    | github.com::repository_view          |    0.863076 | 0.873333 | 0.860960 |
| finetune | B5    | mlp    | wikipedia.org::article_view          |    0.660094 | 0.510000 | 0.559823 |
| finetune | B5    | mlp    | youtube.com::search_results_view     |    0.887496 | 0.923333 | 0.902996 |
| finetune | B5    | mlp    | youtube.com::video_playback          |    0.923878 | 0.950000 | 0.934868 |
| finetune | B6    | mlp    | bing.com::search_results_view        |    0.785344 | 0.710000 | 0.741710 |
| finetune | B6    | mlp    | developer.mozilla.org::document_view |    0.604028 | 0.693333 | 0.643572 |
| finetune | B6    | mlp    | github.com::repository_view          |    0.833729 | 0.863333 | 0.840239 |
| finetune | B6    | mlp    | wikipedia.org::article_view          |    0.672826 | 0.506667 | 0.562530 |
| finetune | B6    | mlp    | youtube.com::search_results_view     |    0.877562 | 0.916667 | 0.895075 |
| finetune | B6    | mlp    | youtube.com::video_playback          |    0.918421 | 0.950000 | 0.931524 |
| probe    | B1    | linear | bing.com::search_results_view        |    0.623949 | 0.560000 | 0.584767 |
| probe    | B1    | linear | developer.mozilla.org::document_view |    0.482180 | 0.566667 | 0.487014 |
| probe    | B1    | linear | github.com::repository_view          |    0.705950 | 0.760000 | 0.703514 |
| probe    | B1    | linear | wikipedia.org::article_view          |    0.545260 | 0.416667 | 0.442870 |
| probe    | B1    | linear | youtube.com::search_results_view     |    0.864814 | 0.740000 | 0.791627 |
| probe    | B1    | linear | youtube.com::video_playback          |    0.825692 | 0.870000 | 0.826066 |
| probe    | B1    | mlp    | bing.com::search_results_view        |    0.752357 | 0.693333 | 0.718238 |
| probe    | B1    | mlp    | developer.mozilla.org::document_view |    0.562157 | 0.690000 | 0.617693 |
| probe    | B1    | mlp    | github.com::repository_view          |    0.848818 | 0.776667 | 0.776612 |
| probe    | B1    | mlp    | wikipedia.org::article_view          |    0.619684 | 0.470000 | 0.524986 |
| probe    | B1    | mlp    | youtube.com::search_results_view     |    0.869715 | 0.906667 | 0.885781 |
| probe    | B1    | mlp    | youtube.com::video_playback          |    0.885216 | 0.916667 | 0.895005 |
| probe    | B2    | linear | bing.com::search_results_view        |    0.628575 | 0.580000 | 0.599325 |
| probe    | B2    | linear | developer.mozilla.org::document_view |    0.458726 | 0.560000 | 0.483342 |
| probe    | B2    | linear | github.com::repository_view          |    0.688816 | 0.716667 | 0.667564 |
| probe    | B2    | linear | wikipedia.org::article_view          |    0.528664 | 0.406667 | 0.429059 |
| probe    | B2    | linear | youtube.com::search_results_view     |    0.851901 | 0.753333 | 0.792895 |
| probe    | B2    | linear | youtube.com::video_playback          |    0.833442 | 0.863333 | 0.826179 |
| probe    | B2    | mlp    | bing.com::search_results_view        |    0.780468 | 0.723333 | 0.747543 |
| probe    | B2    | mlp    | developer.mozilla.org::document_view |    0.575790 | 0.723333 | 0.640077 |
| probe    | B2    | mlp    | github.com::repository_view          |    0.837243 | 0.783333 | 0.785196 |
| probe    | B2    | mlp    | wikipedia.org::article_view          |    0.626807 | 0.463333 | 0.525029 |
| probe    | B2    | mlp    | youtube.com::search_results_view     |    0.872222 | 0.903333 | 0.885225 |
| probe    | B2    | mlp    | youtube.com::video_playback          |    0.894380 | 0.916667 | 0.899058 |
| probe    | B3    | linear | bing.com::search_results_view        |    0.652439 | 0.613333 | 0.627885 |
| probe    | B3    | linear | developer.mozilla.org::document_view |    0.497873 | 0.620000 | 0.544446 |
| probe    | B3    | linear | github.com::repository_view          |    0.728614 | 0.766667 | 0.720751 |
| probe    | B3    | linear | wikipedia.org::article_view          |    0.548500 | 0.403333 | 0.442984 |
| probe    | B3    | linear | youtube.com::search_results_view     |    0.870485 | 0.746667 | 0.800519 |
| probe    | B3    | linear | youtube.com::video_playback          |    0.830273 | 0.883333 | 0.837836 |
| probe    | B3    | mlp    | bing.com::search_results_view        |    0.738435 | 0.706667 | 0.719071 |
| probe    | B3    | mlp    | developer.mozilla.org::document_view |    0.594782 | 0.720000 | 0.649383 |
| probe    | B3    | mlp    | github.com::repository_view          |    0.845636 | 0.776667 | 0.778680 |
| probe    | B3    | mlp    | wikipedia.org::article_view          |    0.651052 | 0.480000 | 0.539012 |
| probe    | B3    | mlp    | youtube.com::search_results_view     |    0.862404 | 0.903333 | 0.880761 |
| probe    | B3    | mlp    | youtube.com::video_playback          |    0.905377 | 0.930000 | 0.912163 |
| probe    | B4    | linear | bing.com::search_results_view        |    0.656515 | 0.613333 | 0.630294 |
| probe    | B4    | linear | developer.mozilla.org::document_view |    0.519161 | 0.596667 | 0.533564 |
| probe    | B4    | linear | github.com::repository_view          |    0.758925 | 0.746667 | 0.709515 |
| probe    | B4    | linear | wikipedia.org::article_view          |    0.566409 | 0.443333 | 0.458475 |
| probe    | B4    | linear | youtube.com::search_results_view     |    0.857121 | 0.766667 | 0.806712 |
| probe    | B4    | linear | youtube.com::video_playback          |    0.849517 | 0.880000 | 0.842560 |
| probe    | B4    | mlp    | bing.com::search_results_view        |    0.771547 | 0.726667 | 0.746482 |
| probe    | B4    | mlp    | developer.mozilla.org::document_view |    0.582258 | 0.713333 | 0.638464 |
| probe    | B4    | mlp    | github.com::repository_view          |    0.858130 | 0.793333 | 0.801005 |
| probe    | B4    | mlp    | wikipedia.org::article_view          |    0.650316 | 0.483333 | 0.538812 |
| probe    | B4    | mlp    | youtube.com::search_results_view     |    0.865756 | 0.906667 | 0.883638 |
| probe    | B4    | mlp    | youtube.com::video_playback          |    0.897279 | 0.916667 | 0.900946 |
| probe    | B5    | linear | bing.com::search_results_view        |    0.665884 | 0.606667 | 0.631521 |
| probe    | B5    | linear | developer.mozilla.org::document_view |    0.540309 | 0.630000 | 0.561558 |
| probe    | B5    | linear | github.com::repository_view          |    0.756540 | 0.746667 | 0.695465 |
| probe    | B5    | linear | wikipedia.org::article_view          |    0.587776 | 0.440000 | 0.471980 |
| probe    | B5    | linear | youtube.com::search_results_view     |    0.861028 | 0.756667 | 0.802810 |
| probe    | B5    | linear | youtube.com::video_playback          |    0.826202 | 0.873333 | 0.826720 |
| probe    | B5    | mlp    | bing.com::search_results_view        |    0.776559 | 0.726667 | 0.748152 |
| probe    | B5    | mlp    | developer.mozilla.org::document_view |    0.574131 | 0.706667 | 0.632412 |
| probe    | B5    | mlp    | github.com::repository_view          |    0.847040 | 0.776667 | 0.782909 |
| probe    | B5    | mlp    | wikipedia.org::article_view          |    0.625150 | 0.476667 | 0.532348 |
| probe    | B5    | mlp    | youtube.com::search_results_view     |    0.865297 | 0.890000 | 0.875159 |
| probe    | B5    | mlp    | youtube.com::video_playback          |    0.893481 | 0.930000 | 0.905819 |
| probe    | B6    | linear | bing.com::search_results_view        |    0.684306 | 0.633333 | 0.654401 |
| probe    | B6    | linear | developer.mozilla.org::document_view |    0.497719 | 0.580000 | 0.525784 |
| probe    | B6    | linear | github.com::repository_view          |    0.751557 | 0.746667 | 0.712304 |
| probe    | B6    | linear | wikipedia.org::article_view          |    0.541359 | 0.443333 | 0.456394 |
| probe    | B6    | linear | youtube.com::search_results_view     |    0.841045 | 0.776667 | 0.805817 |
| probe    | B6    | linear | youtube.com::video_playback          |    0.847002 | 0.886667 | 0.847944 |
| probe    | B6    | mlp    | bing.com::search_results_view        |    0.788347 | 0.700000 | 0.737666 |
| probe    | B6    | mlp    | developer.mozilla.org::document_view |    0.562559 | 0.693333 | 0.618065 |
| probe    | B6    | mlp    | github.com::repository_view          |    0.846790 | 0.813333 | 0.815115 |
| probe    | B6    | mlp    | wikipedia.org::article_view          |    0.633622 | 0.473333 | 0.527649 |
| probe    | B6    | mlp    | youtube.com::search_results_view     |    0.871295 | 0.913333 | 0.890432 |
| probe    | B6    | mlp    | youtube.com::video_playback          |    0.900850 | 0.930000 | 0.911519 |
| probe    | R0    | linear | bing.com::search_results_view        |    0.684721 | 0.636667 | 0.654978 |
| probe    | R0    | linear | developer.mozilla.org::document_view |    0.518498 | 0.580000 | 0.529378 |
| probe    | R0    | linear | github.com::repository_view          |    0.774477 | 0.716667 | 0.681324 |
| probe    | R0    | linear | wikipedia.org::article_view          |    0.527422 | 0.446667 | 0.457477 |
| probe    | R0    | linear | youtube.com::search_results_view     |    0.851306 | 0.766667 | 0.801209 |
| probe    | R0    | linear | youtube.com::video_playback          |    0.842116 | 0.896667 | 0.849200 |
| probe    | R0    | mlp    | bing.com::search_results_view        |    0.777015 | 0.730000 | 0.749952 |
| probe    | R0    | mlp    | developer.mozilla.org::document_view |    0.573077 | 0.676667 | 0.617541 |
| probe    | R0    | mlp    | github.com::repository_view          |    0.845138 | 0.826667 | 0.819663 |
| probe    | R0    | mlp    | wikipedia.org::article_view          |    0.601821 | 0.470000 | 0.519042 |
| probe    | R0    | mlp    | youtube.com::search_results_view     |    0.880551 | 0.893333 | 0.885402 |
| probe    | R0    | mlp    | youtube.com::video_playback          |    0.908640 | 0.933333 | 0.917099 |

## 逐seed原始部署成绩

| stage    | arm   | head   |     seed | protocol    |       F1 |   accuracy |   CE_bits |    Brier |
|:---------|:------|:-------|---------:|:------------|---------:|-----------:|----------:|---------:|
| finetune | B0    | mlp    | 20260918 | anytls      | 0.797022 |   0.808333 |  0.893760 | 0.281642 |
| finetune | B0    | mlp    | 20260918 | shadowsocks | 0.771100 |   0.775000 |  1.153467 | 0.309561 |
| finetune | B0    | mlp    | 20260918 | trojan      | 0.725404 |   0.725000 |  1.395664 | 0.372128 |
| finetune | B0    | mlp    | 20260918 | vless       | 0.730207 |   0.725000 |  1.414009 | 0.353176 |
| finetune | B0    | mlp    | 20260918 | vmess       | 0.785773 |   0.791667 |  1.062924 | 0.315572 |
| finetune | B0    | mlp    | 20260919 | anytls      | 0.836792 |   0.841667 |  0.794873 | 0.272123 |
| finetune | B0    | mlp    | 20260919 | shadowsocks | 0.789040 |   0.791667 |  1.322363 | 0.328126 |
| finetune | B0    | mlp    | 20260919 | trojan      | 0.769153 |   0.766667 |  1.115306 | 0.340911 |
| finetune | B0    | mlp    | 20260919 | vless       | 0.768606 |   0.766667 |  1.371972 | 0.349815 |
| finetune | B0    | mlp    | 20260919 | vmess       | 0.751367 |   0.758333 |  1.072390 | 0.334421 |
| finetune | B0    | mlp    | 20260920 | anytls      | 0.758200 |   0.775000 |  0.911932 | 0.300383 |
| finetune | B0    | mlp    | 20260920 | shadowsocks | 0.813588 |   0.816667 |  1.246194 | 0.295973 |
| finetune | B0    | mlp    | 20260920 | trojan      | 0.728331 |   0.725000 |  1.379839 | 0.382275 |
| finetune | B0    | mlp    | 20260920 | vless       | 0.741398 |   0.741667 |  1.319046 | 0.362110 |
| finetune | B0    | mlp    | 20260920 | vmess       | 0.760725 |   0.766667 |  0.964588 | 0.322722 |
| finetune | B0L   | mlp    | 20260918 | anytls      | 0.787550 |   0.800000 |  1.289419 | 0.295800 |
| finetune | B0L   | mlp    | 20260918 | shadowsocks | 0.791167 |   0.791667 |  1.600702 | 0.317673 |
| finetune | B0L   | mlp    | 20260918 | trojan      | 0.728382 |   0.725000 |  1.835439 | 0.388067 |
| finetune | B0L   | mlp    | 20260918 | vless       | 0.766000 |   0.766667 |  1.928434 | 0.368865 |
| finetune | B0L   | mlp    | 20260918 | vmess       | 0.760300 |   0.766667 |  1.339354 | 0.354699 |
| finetune | B0L   | mlp    | 20260919 | anytls      | 0.819334 |   0.825000 |  1.218210 | 0.282798 |
| finetune | B0L   | mlp    | 20260919 | shadowsocks | 0.788830 |   0.791667 |  1.695573 | 0.336204 |
| finetune | B0L   | mlp    | 20260919 | trojan      | 0.727442 |   0.725000 |  1.567087 | 0.377313 |
| finetune | B0L   | mlp    | 20260919 | vless       | 0.753064 |   0.750000 |  1.990874 | 0.375249 |
| finetune | B0L   | mlp    | 20260919 | vmess       | 0.761295 |   0.766667 |  1.476617 | 0.357684 |
| finetune | B0L   | mlp    | 20260920 | anytls      | 0.783944 |   0.800000 |  1.427786 | 0.310774 |
| finetune | B0L   | mlp    | 20260920 | shadowsocks | 0.798750 |   0.800000 |  1.788004 | 0.320553 |
| finetune | B0L   | mlp    | 20260920 | trojan      | 0.726472 |   0.725000 |  1.898701 | 0.408160 |
| finetune | B0L   | mlp    | 20260920 | vless       | 0.752090 |   0.750000 |  1.964962 | 0.389433 |
| finetune | B0L   | mlp    | 20260920 | vmess       | 0.760005 |   0.766667 |  1.277181 | 0.338790 |
| finetune | B1    | mlp    | 20260918 | anytls      | 0.837439 |   0.841667 |  0.820390 | 0.266309 |
| finetune | B1    | mlp    | 20260918 | shadowsocks | 0.781273 |   0.783333 |  1.059461 | 0.293857 |
| finetune | B1    | mlp    | 20260918 | trojan      | 0.752282 |   0.750000 |  1.285807 | 0.355676 |
| finetune | B1    | mlp    | 20260918 | vless       | 0.757981 |   0.758333 |  1.442446 | 0.367894 |
| finetune | B1    | mlp    | 20260918 | vmess       | 0.776481 |   0.783333 |  0.993273 | 0.324192 |
| finetune | B1    | mlp    | 20260919 | anytls      | 0.807331 |   0.816667 |  0.787256 | 0.263627 |
| finetune | B1    | mlp    | 20260919 | shadowsocks | 0.781631 |   0.783333 |  1.317502 | 0.324797 |
| finetune | B1    | mlp    | 20260919 | trojan      | 0.736378 |   0.733333 |  1.238667 | 0.364733 |
| finetune | B1    | mlp    | 20260919 | vless       | 0.776971 |   0.775000 |  1.420806 | 0.342312 |
| finetune | B1    | mlp    | 20260919 | vmess       | 0.748343 |   0.758333 |  1.078959 | 0.333580 |
| finetune | B1    | mlp    | 20260920 | anytls      | 0.800038 |   0.808333 |  0.950815 | 0.287502 |
| finetune | B1    | mlp    | 20260920 | shadowsocks | 0.779385 |   0.783333 |  1.087149 | 0.301431 |
| finetune | B1    | mlp    | 20260920 | trojan      | 0.742328 |   0.741667 |  1.244761 | 0.342863 |
| finetune | B1    | mlp    | 20260920 | vless       | 0.760713 |   0.758333 |  1.161081 | 0.350403 |
| finetune | B1    | mlp    | 20260920 | vmess       | 0.768929 |   0.775000 |  0.895743 | 0.307867 |
| finetune | B2    | mlp    | 20260918 | anytls      | 0.822854 |   0.833333 |  0.694052 | 0.239811 |
| finetune | B2    | mlp    | 20260918 | shadowsocks | 0.821962 |   0.825000 |  1.073885 | 0.279699 |
| finetune | B2    | mlp    | 20260918 | trojan      | 0.724128 |   0.725000 |  1.417915 | 0.376115 |
| finetune | B2    | mlp    | 20260918 | vless       | 0.779317 |   0.775000 |  1.420645 | 0.334918 |
| finetune | B2    | mlp    | 20260918 | vmess       | 0.766896 |   0.775000 |  1.048824 | 0.315188 |
| finetune | B2    | mlp    | 20260919 | anytls      | 0.809945 |   0.816667 |  0.845910 | 0.267052 |
| finetune | B2    | mlp    | 20260919 | shadowsocks | 0.789885 |   0.791667 |  1.395756 | 0.323272 |
| finetune | B2    | mlp    | 20260919 | trojan      | 0.717250 |   0.716667 |  1.252278 | 0.371094 |
| finetune | B2    | mlp    | 20260919 | vless       | 0.803037 |   0.800000 |  1.399028 | 0.326288 |
| finetune | B2    | mlp    | 20260919 | vmess       | 0.733004 |   0.741667 |  1.182227 | 0.353170 |
| finetune | B2    | mlp    | 20260920 | anytls      | 0.833270 |   0.841667 |  0.766501 | 0.259298 |
| finetune | B2    | mlp    | 20260920 | shadowsocks | 0.807022 |   0.808333 |  1.099538 | 0.289868 |
| finetune | B2    | mlp    | 20260920 | trojan      | 0.727446 |   0.725000 |  1.332501 | 0.341816 |
| finetune | B2    | mlp    | 20260920 | vless       | 0.757875 |   0.758333 |  1.260394 | 0.357677 |
| finetune | B2    | mlp    | 20260920 | vmess       | 0.785941 |   0.791667 |  0.824740 | 0.294784 |
| finetune | B3    | mlp    | 20260918 | anytls      | 0.821043 |   0.825000 |  0.754112 | 0.259802 |
| finetune | B3    | mlp    | 20260918 | shadowsocks | 0.778830 |   0.783333 |  0.988288 | 0.292276 |
| finetune | B3    | mlp    | 20260918 | trojan      | 0.759492 |   0.758333 |  1.375356 | 0.375483 |
| finetune | B3    | mlp    | 20260918 | vless       | 0.752902 |   0.750000 |  1.190968 | 0.341802 |
| finetune | B3    | mlp    | 20260918 | vmess       | 0.774425 |   0.783333 |  0.906420 | 0.319220 |
| finetune | B3    | mlp    | 20260919 | anytls      | 0.823633 |   0.833333 |  0.806434 | 0.248619 |
| finetune | B3    | mlp    | 20260919 | shadowsocks | 0.797265 |   0.800000 |  1.209094 | 0.293194 |
| finetune | B3    | mlp    | 20260919 | trojan      | 0.716406 |   0.716667 |  1.208057 | 0.363450 |
| finetune | B3    | mlp    | 20260919 | vless       | 0.769207 |   0.766667 |  1.273213 | 0.338724 |
| finetune | B3    | mlp    | 20260919 | vmess       | 0.750794 |   0.758333 |  0.969010 | 0.336166 |
| finetune | B3    | mlp    | 20260920 | anytls      | 0.799460 |   0.808333 |  0.791153 | 0.274249 |
| finetune | B3    | mlp    | 20260920 | shadowsocks | 0.790567 |   0.791667 |  1.000848 | 0.288803 |
| finetune | B3    | mlp    | 20260920 | trojan      | 0.743716 |   0.741667 |  1.333845 | 0.343673 |
| finetune | B3    | mlp    | 20260920 | vless       | 0.759420 |   0.758333 |  1.129915 | 0.348005 |
| finetune | B3    | mlp    | 20260920 | vmess       | 0.778112 |   0.783333 |  1.049418 | 0.299968 |
| finetune | B4    | mlp    | 20260918 | anytls      | 0.851036 |   0.858333 |  0.673273 | 0.229443 |
| finetune | B4    | mlp    | 20260918 | shadowsocks | 0.795640 |   0.800000 |  1.157316 | 0.273549 |
| finetune | B4    | mlp    | 20260918 | trojan      | 0.768404 |   0.766667 |  1.399013 | 0.359862 |
| finetune | B4    | mlp    | 20260918 | vless       | 0.744189 |   0.741667 |  1.316485 | 0.372203 |
| finetune | B4    | mlp    | 20260918 | vmess       | 0.769978 |   0.775000 |  1.040909 | 0.323497 |
| finetune | B4    | mlp    | 20260919 | anytls      | 0.804415 |   0.816667 |  0.793907 | 0.251811 |
| finetune | B4    | mlp    | 20260919 | shadowsocks | 0.815089 |   0.816667 |  1.191782 | 0.306564 |
| finetune | B4    | mlp    | 20260919 | trojan      | 0.734356 |   0.733333 |  1.154294 | 0.346844 |
| finetune | B4    | mlp    | 20260919 | vless       | 0.769571 |   0.766667 |  1.315477 | 0.349391 |
| finetune | B4    | mlp    | 20260919 | vmess       | 0.733961 |   0.741667 |  1.060148 | 0.351021 |
| finetune | B4    | mlp    | 20260920 | anytls      | 0.795868 |   0.808333 |  0.859444 | 0.277111 |
| finetune | B4    | mlp    | 20260920 | shadowsocks | 0.798051 |   0.800000 |  0.925799 | 0.289475 |
| finetune | B4    | mlp    | 20260920 | trojan      | 0.737061 |   0.733333 |  1.287084 | 0.354476 |
| finetune | B4    | mlp    | 20260920 | vless       | 0.753396 |   0.750000 |  1.138410 | 0.351151 |
| finetune | B4    | mlp    | 20260920 | vmess       | 0.788362 |   0.791667 |  0.921037 | 0.287034 |
| finetune | B5    | mlp    | 20260918 | anytls      | 0.828194 |   0.841667 |  0.715373 | 0.233715 |
| finetune | B5    | mlp    | 20260918 | shadowsocks | 0.810575 |   0.816667 |  1.080140 | 0.279789 |
| finetune | B5    | mlp    | 20260918 | trojan      | 0.752237 |   0.750000 |  1.417805 | 0.367915 |
| finetune | B5    | mlp    | 20260918 | vless       | 0.758426 |   0.758333 |  1.345323 | 0.356905 |
| finetune | B5    | mlp    | 20260918 | vmess       | 0.760699 |   0.766667 |  1.106777 | 0.341251 |
| finetune | B5    | mlp    | 20260919 | anytls      | 0.817633 |   0.825000 |  0.780928 | 0.250034 |
| finetune | B5    | mlp    | 20260919 | shadowsocks | 0.788465 |   0.791667 |  1.315270 | 0.308460 |
| finetune | B5    | mlp    | 20260919 | trojan      | 0.751022 |   0.750000 |  1.207839 | 0.356796 |
| finetune | B5    | mlp    | 20260919 | vless       | 0.761251 |   0.758333 |  1.367477 | 0.344747 |
| finetune | B5    | mlp    | 20260919 | vmess       | 0.751824 |   0.758333 |  1.059741 | 0.338217 |
| finetune | B5    | mlp    | 20260920 | anytls      | 0.784731 |   0.800000 |  0.837970 | 0.273547 |
| finetune | B5    | mlp    | 20260920 | shadowsocks | 0.801214 |   0.800000 |  0.931591 | 0.294038 |
| finetune | B5    | mlp    | 20260920 | trojan      | 0.753500 |   0.750000 |  1.354521 | 0.352648 |
| finetune | B5    | mlp    | 20260920 | vless       | 0.785642 |   0.783333 |  1.138557 | 0.347710 |
| finetune | B5    | mlp    | 20260920 | vmess       | 0.803488 |   0.808333 |  0.949218 | 0.294970 |
| finetune | B6    | mlp    | 20260918 | anytls      | 0.792691 |   0.808333 |  0.738626 | 0.258132 |
| finetune | B6    | mlp    | 20260918 | shadowsocks | 0.803956 |   0.808333 |  1.130302 | 0.292491 |
| finetune | B6    | mlp    | 20260918 | trojan      | 0.750502 |   0.750000 |  1.445826 | 0.372551 |
| finetune | B6    | mlp    | 20260918 | vless       | 0.767929 |   0.766667 |  1.329805 | 0.361491 |
| finetune | B6    | mlp    | 20260918 | vmess       | 0.767068 |   0.775000 |  1.019845 | 0.324367 |
| finetune | B6    | mlp    | 20260919 | anytls      | 0.801935 |   0.808333 |  0.756607 | 0.265841 |
| finetune | B6    | mlp    | 20260919 | shadowsocks | 0.806458 |   0.808333 |  1.455549 | 0.308079 |
| finetune | B6    | mlp    | 20260919 | trojan      | 0.732890 |   0.733333 |  1.274699 | 0.365057 |
| finetune | B6    | mlp    | 20260919 | vless       | 0.751196 |   0.750000 |  1.309410 | 0.330184 |
| finetune | B6    | mlp    | 20260919 | vmess       | 0.757690 |   0.766667 |  0.989525 | 0.339539 |
| finetune | B6    | mlp    | 20260920 | anytls      | 0.786961 |   0.800000 |  0.882384 | 0.292328 |
| finetune | B6    | mlp    | 20260920 | shadowsocks | 0.780263 |   0.783333 |  1.180314 | 0.311373 |
| finetune | B6    | mlp    | 20260920 | trojan      | 0.726436 |   0.725000 |  1.390404 | 0.381007 |
| finetune | B6    | mlp    | 20260920 | vless       | 0.742510 |   0.741667 |  1.362384 | 0.367297 |
| finetune | B6    | mlp    | 20260920 | vmess       | 0.768142 |   0.775000 |  1.003549 | 0.319695 |
| probe    | B1    | linear | 20260918 | anytls      | 0.742532 |   0.750000 |  1.199700 | 0.417800 |
| probe    | B1    | linear | 20260918 | shadowsocks | 0.547368 |   0.575000 |  1.642022 | 0.562628 |
| probe    | B1    | linear | 20260918 | trojan      | 0.557634 |   0.558333 |  1.480217 | 0.527911 |
| probe    | B1    | linear | 20260918 | vless       | 0.628179 |   0.625000 |  1.496762 | 0.513550 |
| probe    | B1    | linear | 20260918 | vmess       | 0.684878 |   0.708333 |  1.185843 | 0.411753 |
| probe    | B1    | linear | 20260919 | anytls      | 0.774536 |   0.791667 |  1.205899 | 0.402741 |
| probe    | B1    | linear | 20260919 | shadowsocks | 0.498938 |   0.533333 |  1.710942 | 0.576309 |
| probe    | B1    | linear | 20260919 | trojan      | 0.586591 |   0.583333 |  1.542315 | 0.535022 |
| probe    | B1    | linear | 20260919 | vless       | 0.622920 |   0.616667 |  1.519841 | 0.503110 |
| probe    | B1    | linear | 20260919 | vmess       | 0.731652 |   0.741667 |  1.223194 | 0.428619 |
| probe    | B1    | linear | 20260920 | anytls      | 0.785882 |   0.800000 |  1.205616 | 0.416261 |
| probe    | B1    | linear | 20260920 | shadowsocks | 0.488800 |   0.550000 |  1.605373 | 0.550421 |
| probe    | B1    | linear | 20260920 | trojan      | 0.590474 |   0.583333 |  1.485956 | 0.542580 |
| probe    | B1    | linear | 20260920 | vless       | 0.654467 |   0.650000 |  1.347995 | 0.485852 |
| probe    | B1    | linear | 20260920 | vmess       | 0.694793 |   0.716667 |  1.162134 | 0.410574 |
| probe    | B1    | mlp    | 20260918 | anytls      | 0.783655 |   0.791667 |  0.781273 | 0.274899 |
| probe    | B1    | mlp    | 20260918 | shadowsocks | 0.639785 |   0.666667 |  1.202809 | 0.425330 |
| probe    | B1    | mlp    | 20260918 | trojan      | 0.692744 |   0.691667 |  1.325933 | 0.401912 |
| probe    | B1    | mlp    | 20260918 | vless       | 0.715376 |   0.716667 |  1.186104 | 0.360257 |
| probe    | B1    | mlp    | 20260918 | vmess       | 0.766433 |   0.775000 |  1.046193 | 0.320217 |
| probe    | B1    | mlp    | 20260919 | anytls      | 0.829306 |   0.833333 |  0.699950 | 0.257257 |
| probe    | B1    | mlp    | 20260919 | shadowsocks | 0.738597 |   0.741667 |  1.216796 | 0.382509 |
| probe    | B1    | mlp    | 20260919 | trojan      | 0.718994 |   0.716667 |  1.242654 | 0.413763 |
| probe    | B1    | mlp    | 20260919 | vless       | 0.719366 |   0.716667 |  1.051527 | 0.350417 |
| probe    | B1    | mlp    | 20260919 | vmess       | 0.790733 |   0.800000 |  0.894226 | 0.309845 |
| probe    | B1    | mlp    | 20260920 | anytls      | 0.779664 |   0.791667 |  0.863907 | 0.293901 |
| probe    | B1    | mlp    | 20260920 | shadowsocks | 0.652010 |   0.675000 |  1.164057 | 0.420199 |
| probe    | B1    | mlp    | 20260920 | trojan      | 0.687933 |   0.683333 |  1.302494 | 0.420864 |
| probe    | B1    | mlp    | 20260920 | vless       | 0.742212 |   0.741667 |  1.085893 | 0.343934 |
| probe    | B1    | mlp    | 20260920 | vmess       | 0.788981 |   0.791667 |  0.871579 | 0.299137 |
| probe    | B2    | linear | 20260918 | anytls      | 0.723668 |   0.733333 |  1.273362 | 0.430168 |
| probe    | B2    | linear | 20260918 | shadowsocks | 0.397885 |   0.491667 |  1.610377 | 0.559999 |
| probe    | B2    | linear | 20260918 | trojan      | 0.587856 |   0.583333 |  1.529489 | 0.544727 |
| probe    | B2    | linear | 20260918 | vless       | 0.627573 |   0.625000 |  1.516500 | 0.512126 |
| probe    | B2    | linear | 20260918 | vmess       | 0.719370 |   0.741667 |  1.192775 | 0.421919 |
| probe    | B2    | linear | 20260919 | anytls      | 0.799325 |   0.816667 |  1.193826 | 0.395358 |
| probe    | B2    | linear | 20260919 | shadowsocks | 0.518993 |   0.558333 |  1.672736 | 0.568220 |
| probe    | B2    | linear | 20260919 | trojan      | 0.561370 |   0.558333 |  1.519316 | 0.540643 |
| probe    | B2    | linear | 20260919 | vless       | 0.646190 |   0.641667 |  1.425155 | 0.496604 |
| probe    | B2    | linear | 20260919 | vmess       | 0.733484 |   0.750000 |  1.151146 | 0.406829 |
| probe    | B2    | linear | 20260920 | anytls      | 0.709758 |   0.725000 |  1.230856 | 0.429080 |
| probe    | B2    | linear | 20260920 | shadowsocks | 0.568273 |   0.583333 |  1.646113 | 0.559320 |
| probe    | B2    | linear | 20260920 | trojan      | 0.561469 |   0.550000 |  1.511207 | 0.551214 |
| probe    | B2    | linear | 20260920 | vless       | 0.632655 |   0.625000 |  1.383767 | 0.505008 |
| probe    | B2    | linear | 20260920 | vmess       | 0.708042 |   0.716667 |  1.152587 | 0.419742 |
| probe    | B2    | mlp    | 20260918 | anytls      | 0.813826 |   0.825000 |  0.764736 | 0.268634 |
| probe    | B2    | mlp    | 20260918 | shadowsocks | 0.649660 |   0.675000 |  1.213500 | 0.418390 |
| probe    | B2    | mlp    | 20260918 | trojan      | 0.724260 |   0.725000 |  1.340565 | 0.400470 |
| probe    | B2    | mlp    | 20260918 | vless       | 0.730787 |   0.733333 |  1.200804 | 0.356412 |
| probe    | B2    | mlp    | 20260918 | vmess       | 0.810073 |   0.816667 |  0.897695 | 0.280310 |
| probe    | B2    | mlp    | 20260919 | anytls      | 0.845527 |   0.850000 |  0.771808 | 0.272023 |
| probe    | B2    | mlp    | 20260919 | shadowsocks | 0.730214 |   0.733333 |  1.257443 | 0.376808 |
| probe    | B2    | mlp    | 20260919 | trojan      | 0.720945 |   0.716667 |  1.211118 | 0.402906 |
| probe    | B2    | mlp    | 20260919 | vless       | 0.754359 |   0.750000 |  1.074727 | 0.359438 |
| probe    | B2    | mlp    | 20260919 | vmess       | 0.758815 |   0.766667 |  0.958927 | 0.334007 |
| probe    | B2    | mlp    | 20260920 | anytls      | 0.784081 |   0.791667 |  0.812192 | 0.291913 |
| probe    | B2    | mlp    | 20260920 | shadowsocks | 0.688685 |   0.700000 |  1.176667 | 0.401580 |
| probe    | B2    | mlp    | 20260920 | trojan      | 0.702292 |   0.700000 |  1.227378 | 0.416365 |
| probe    | B2    | mlp    | 20260920 | vless       | 0.714747 |   0.716667 |  1.134985 | 0.366716 |
| probe    | B2    | mlp    | 20260920 | vmess       | 0.777048 |   0.783333 |  0.849923 | 0.317709 |
| probe    | B3    | linear | 20260918 | anytls      | 0.781928 |   0.783333 |  1.180248 | 0.405767 |
| probe    | B3    | linear | 20260918 | shadowsocks | 0.533969 |   0.558333 |  1.514100 | 0.541299 |
| probe    | B3    | linear | 20260918 | trojan      | 0.590637 |   0.591667 |  1.493420 | 0.521214 |
| probe    | B3    | linear | 20260918 | vless       | 0.643198 |   0.641667 |  1.377383 | 0.496380 |
| probe    | B3    | linear | 20260918 | vmess       | 0.758987 |   0.766667 |  1.147063 | 0.395895 |
| probe    | B3    | linear | 20260919 | anytls      | 0.754389 |   0.775000 |  1.176745 | 0.405271 |
| probe    | B3    | linear | 20260919 | shadowsocks | 0.499248 |   0.541667 |  1.760854 | 0.562967 |
| probe    | B3    | linear | 20260919 | trojan      | 0.645090 |   0.641667 |  1.493192 | 0.524993 |
| probe    | B3    | linear | 20260919 | vless       | 0.670639 |   0.666667 |  1.405400 | 0.473672 |
| probe    | B3    | linear | 20260919 | vmess       | 0.752839 |   0.758333 |  1.156792 | 0.404142 |
| probe    | B3    | linear | 20260920 | anytls      | 0.728941 |   0.741667 |  1.197084 | 0.419616 |
| probe    | B3    | linear | 20260920 | shadowsocks | 0.598476 |   0.608333 |  1.632733 | 0.547470 |
| probe    | B3    | linear | 20260920 | trojan      | 0.625749 |   0.625000 |  1.435366 | 0.519529 |
| probe    | B3    | linear | 20260920 | vless       | 0.644769 |   0.641667 |  1.355169 | 0.485030 |
| probe    | B3    | linear | 20260920 | vmess       | 0.707190 |   0.741667 |  1.130266 | 0.397853 |
| probe    | B3    | mlp    | 20260918 | anytls      | 0.772274 |   0.783333 |  0.729258 | 0.261040 |
| probe    | B3    | mlp    | 20260918 | shadowsocks | 0.657463 |   0.683333 |  1.101516 | 0.376501 |
| probe    | B3    | mlp    | 20260918 | trojan      | 0.735713 |   0.733333 |  1.346457 | 0.382091 |
| probe    | B3    | mlp    | 20260918 | vless       | 0.732116 |   0.733333 |  1.172833 | 0.356078 |
| probe    | B3    | mlp    | 20260918 | vmess       | 0.784056 |   0.791667 |  0.928825 | 0.300683 |
| probe    | B3    | mlp    | 20260919 | anytls      | 0.806106 |   0.816667 |  0.771958 | 0.269686 |
| probe    | B3    | mlp    | 20260919 | shadowsocks | 0.726804 |   0.733333 |  1.316485 | 0.400962 |
| probe    | B3    | mlp    | 20260919 | trojan      | 0.719175 |   0.716667 |  1.281133 | 0.387666 |
| probe    | B3    | mlp    | 20260919 | vless       | 0.787608 |   0.783333 |  1.137265 | 0.348590 |
| probe    | B3    | mlp    | 20260919 | vmess       | 0.766219 |   0.775000 |  1.064155 | 0.312198 |
| probe    | B3    | mlp    | 20260920 | anytls      | 0.783667 |   0.791667 |  0.750764 | 0.272367 |
| probe    | B3    | mlp    | 20260920 | shadowsocks | 0.673197 |   0.691667 |  1.046644 | 0.371121 |
| probe    | B3    | mlp    | 20260920 | trojan      | 0.726329 |   0.725000 |  1.318188 | 0.403349 |
| probe    | B3    | mlp    | 20260920 | vless       | 0.750034 |   0.750000 |  1.050889 | 0.345992 |
| probe    | B3    | mlp    | 20260920 | vmess       | 0.776915 |   0.783333 |  0.993418 | 0.300786 |
| probe    | B4    | linear | 20260918 | anytls      | 0.758690 |   0.775000 |  1.181461 | 0.403001 |
| probe    | B4    | linear | 20260918 | shadowsocks | 0.555563 |   0.575000 |  1.543017 | 0.552051 |
| probe    | B4    | linear | 20260918 | trojan      | 0.638990 |   0.633333 |  1.484129 | 0.519393 |
| probe    | B4    | linear | 20260918 | vless       | 0.646949 |   0.641667 |  1.430022 | 0.496924 |
| probe    | B4    | linear | 20260918 | vmess       | 0.726123 |   0.750000 |  1.167068 | 0.401567 |
| probe    | B4    | linear | 20260919 | anytls      | 0.795156 |   0.808333 |  1.141953 | 0.390071 |
| probe    | B4    | linear | 20260919 | shadowsocks | 0.502112 |   0.533333 |  1.623652 | 0.555555 |
| probe    | B4    | linear | 20260919 | trojan      | 0.584710 |   0.583333 |  1.481711 | 0.528050 |
| probe    | B4    | linear | 20260919 | vless       | 0.676305 |   0.675000 |  1.357039 | 0.465034 |
| probe    | B4    | linear | 20260919 | vmess       | 0.729433 |   0.741667 |  1.135438 | 0.391718 |
| probe    | B4    | linear | 20260920 | anytls      | 0.745614 |   0.758333 |  1.207918 | 0.417895 |
| probe    | B4    | linear | 20260920 | shadowsocks | 0.609338 |   0.633333 |  1.692884 | 0.550345 |
| probe    | B4    | linear | 20260920 | trojan      | 0.610424 |   0.608333 |  1.424636 | 0.521634 |
| probe    | B4    | linear | 20260920 | vless       | 0.679301 |   0.675000 |  1.358754 | 0.485774 |
| probe    | B4    | linear | 20260920 | vmess       | 0.694091 |   0.725000 |  1.093084 | 0.393872 |
| probe    | B4    | mlp    | 20260918 | anytls      | 0.803611 |   0.816667 |  0.765360 | 0.270843 |
| probe    | B4    | mlp    | 20260918 | shadowsocks | 0.666952 |   0.691667 |  1.151447 | 0.403177 |
| probe    | B4    | mlp    | 20260918 | trojan      | 0.744717 |   0.741667 |  1.371931 | 0.397917 |
| probe    | B4    | mlp    | 20260918 | vless       | 0.716252 |   0.716667 |  1.283767 | 0.369348 |
| probe    | B4    | mlp    | 20260918 | vmess       | 0.767213 |   0.775000 |  0.992076 | 0.310596 |
| probe    | B4    | mlp    | 20260919 | anytls      | 0.828461 |   0.833333 |  0.745315 | 0.261352 |
| probe    | B4    | mlp    | 20260919 | shadowsocks | 0.733979 |   0.741667 |  1.264903 | 0.384395 |
| probe    | B4    | mlp    | 20260919 | trojan      | 0.703179 |   0.700000 |  1.288420 | 0.414387 |
| probe    | B4    | mlp    | 20260919 | vless       | 0.765635 |   0.766667 |  1.175405 | 0.340363 |
| probe    | B4    | mlp    | 20260919 | vmess       | 0.805533 |   0.808333 |  1.011126 | 0.301139 |
| probe    | B4    | mlp    | 20260920 | anytls      | 0.803759 |   0.816667 |  0.750734 | 0.272705 |
| probe    | B4    | mlp    | 20260920 | shadowsocks | 0.715668 |   0.725000 |  1.122893 | 0.381447 |
| probe    | B4    | mlp    | 20260920 | trojan      | 0.704391 |   0.700000 |  1.280694 | 0.414347 |
| probe    | B4    | mlp    | 20260920 | vless       | 0.721026 |   0.716667 |  1.046493 | 0.361078 |
| probe    | B4    | mlp    | 20260920 | vmess       | 0.792994 |   0.800000 |  0.931736 | 0.302288 |
| probe    | B5    | linear | 20260918 | anytls      | 0.743872 |   0.758333 |  1.191722 | 0.404357 |
| probe    | B5    | linear | 20260918 | shadowsocks | 0.557647 |   0.583333 |  1.544287 | 0.552234 |
| probe    | B5    | linear | 20260918 | trojan      | 0.618904 |   0.616667 |  1.496527 | 0.516933 |
| probe    | B5    | linear | 20260918 | vless       | 0.661036 |   0.658333 |  1.481026 | 0.495878 |
| probe    | B5    | linear | 20260918 | vmess       | 0.750466 |   0.766667 |  1.180467 | 0.394457 |
| probe    | B5    | linear | 20260919 | anytls      | 0.769356 |   0.791667 |  1.143543 | 0.392208 |
| probe    | B5    | linear | 20260919 | shadowsocks | 0.503800 |   0.533333 |  1.665381 | 0.555558 |
| probe    | B5    | linear | 20260919 | trojan      | 0.603413 |   0.600000 |  1.472861 | 0.526051 |
| probe    | B5    | linear | 20260919 | vless       | 0.704195 |   0.700000 |  1.327503 | 0.449954 |
| probe    | B5    | linear | 20260919 | vmess       | 0.761843 |   0.766667 |  1.126432 | 0.396104 |
| probe    | B5    | linear | 20260920 | anytls      | 0.714573 |   0.725000 |  1.212987 | 0.416326 |
| probe    | B5    | linear | 20260920 | shadowsocks | 0.596062 |   0.625000 |  1.617617 | 0.541762 |
| probe    | B5    | linear | 20260920 | trojan      | 0.604230 |   0.600000 |  1.445260 | 0.528475 |
| probe    | B5    | linear | 20260920 | vless       | 0.652407 |   0.650000 |  1.311120 | 0.478026 |
| probe    | B5    | linear | 20260920 | vmess       | 0.733333 |   0.758333 |  1.090406 | 0.391987 |
| probe    | B5    | mlp    | 20260918 | anytls      | 0.811218 |   0.816667 |  0.726064 | 0.263656 |
| probe    | B5    | mlp    | 20260918 | shadowsocks | 0.674922 |   0.700000 |  1.184611 | 0.393913 |
| probe    | B5    | mlp    | 20260918 | trojan      | 0.711379 |   0.708333 |  1.348884 | 0.393204 |
| probe    | B5    | mlp    | 20260918 | vless       | 0.750991 |   0.750000 |  1.097031 | 0.357275 |
| probe    | B5    | mlp    | 20260918 | vmess       | 0.801104 |   0.808333 |  0.944416 | 0.313477 |
| probe    | B5    | mlp    | 20260919 | anytls      | 0.818566 |   0.825000 |  0.737269 | 0.266602 |
| probe    | B5    | mlp    | 20260919 | shadowsocks | 0.723845 |   0.733333 |  1.244323 | 0.394070 |
| probe    | B5    | mlp    | 20260919 | trojan      | 0.709291 |   0.708333 |  1.325175 | 0.422544 |
| probe    | B5    | mlp    | 20260919 | vless       | 0.735508 |   0.733333 |  1.124962 | 0.348370 |
| probe    | B5    | mlp    | 20260919 | vmess       | 0.802738 |   0.808333 |  0.974995 | 0.293810 |
| probe    | B5    | mlp    | 20260920 | anytls      | 0.774218 |   0.783333 |  0.789044 | 0.282228 |
| probe    | B5    | mlp    | 20260920 | shadowsocks | 0.678845 |   0.691667 |  1.117069 | 0.371702 |
| probe    | B5    | mlp    | 20260920 | trojan      | 0.709917 |   0.708333 |  1.370963 | 0.414476 |
| probe    | B5    | mlp    | 20260920 | vless       | 0.704956 |   0.700000 |  1.081474 | 0.370473 |
| probe    | B5    | mlp    | 20260920 | vmess       | 0.784497 |   0.791667 |  0.964041 | 0.307748 |
| probe    | B6    | linear | 20260918 | anytls      | 0.748602 |   0.750000 |  1.099294 | 0.375990 |
| probe    | B6    | linear | 20260918 | shadowsocks | 0.549527 |   0.583333 |  1.471954 | 0.505895 |
| probe    | B6    | linear | 20260918 | trojan      | 0.620250 |   0.616667 |  1.430883 | 0.496298 |
| probe    | B6    | linear | 20260918 | vless       | 0.663389 |   0.658333 |  1.357187 | 0.468533 |
| probe    | B6    | linear | 20260918 | vmess       | 0.768576 |   0.783333 |  1.089662 | 0.345576 |
| probe    | B6    | linear | 20260919 | anytls      | 0.786435 |   0.800000 |  1.086961 | 0.367406 |
| probe    | B6    | linear | 20260919 | shadowsocks | 0.523898 |   0.575000 |  1.539224 | 0.521660 |
| probe    | B6    | linear | 20260919 | trojan      | 0.578534 |   0.575000 |  1.409717 | 0.507814 |
| probe    | B6    | linear | 20260919 | vless       | 0.714253 |   0.708333 |  1.267513 | 0.448106 |
| probe    | B6    | linear | 20260919 | vmess       | 0.726109 |   0.733333 |  1.040724 | 0.376362 |
| probe    | B6    | linear | 20260920 | anytls      | 0.734581 |   0.750000 |  1.082235 | 0.373063 |
| probe    | B6    | linear | 20260920 | shadowsocks | 0.541571 |   0.558333 |  1.520687 | 0.522977 |
| probe    | B6    | linear | 20260920 | trojan      | 0.630869 |   0.625000 |  1.396275 | 0.500590 |
| probe    | B6    | linear | 20260920 | vless       | 0.697337 |   0.691667 |  1.308228 | 0.441998 |
| probe    | B6    | linear | 20260920 | vmess       | 0.722679 |   0.758333 |  0.985973 | 0.341283 |
| probe    | B6    | mlp    | 20260918 | anytls      | 0.787711 |   0.800000 |  0.734943 | 0.268233 |
| probe    | B6    | mlp    | 20260918 | shadowsocks | 0.701799 |   0.716667 |  1.053296 | 0.363636 |
| probe    | B6    | mlp    | 20260918 | trojan      | 0.688966 |   0.683333 |  1.305287 | 0.413822 |
| probe    | B6    | mlp    | 20260918 | vless       | 0.754046 |   0.750000 |  1.257148 | 0.354181 |
| probe    | B6    | mlp    | 20260918 | vmess       | 0.785241 |   0.791667 |  0.935480 | 0.302110 |
| probe    | B6    | mlp    | 20260919 | anytls      | 0.809202 |   0.816667 |  0.717074 | 0.271686 |
| probe    | B6    | mlp    | 20260919 | shadowsocks | 0.769397 |   0.775000 |  1.165627 | 0.339415 |
| probe    | B6    | mlp    | 20260919 | trojan      | 0.693568 |   0.691667 |  1.266086 | 0.402462 |
| probe    | B6    | mlp    | 20260919 | vless       | 0.733656 |   0.733333 |  1.274267 | 0.368358 |
| probe    | B6    | mlp    | 20260919 | vmess       | 0.749501 |   0.758333 |  1.078853 | 0.335882 |
| probe    | B6    | mlp    | 20260920 | anytls      | 0.792448 |   0.800000 |  0.757944 | 0.275098 |
| probe    | B6    | mlp    | 20260920 | shadowsocks | 0.735847 |   0.741667 |  1.122862 | 0.364749 |
| probe    | B6    | mlp    | 20260920 | trojan      | 0.728742 |   0.725000 |  1.256532 | 0.388022 |
| probe    | B6    | mlp    | 20260920 | vless       | 0.730517 |   0.725000 |  1.150853 | 0.354885 |
| probe    | B6    | mlp    | 20260920 | vmess       | 0.790474 |   0.800000 |  0.982599 | 0.282520 |
| probe    | R0    | linear | 20260918 | anytls      | 0.726302 |   0.733333 |  1.184635 | 0.416915 |
| probe    | R0    | linear | 20260918 | shadowsocks | 0.587883 |   0.625000 |  1.472021 | 0.501728 |
| probe    | R0    | linear | 20260918 | trojan      | 0.576274 |   0.575000 |  1.437630 | 0.525458 |
| probe    | R0    | linear | 20260918 | vless       | 0.695339 |   0.691667 |  1.452083 | 0.485999 |
| probe    | R0    | linear | 20260918 | vmess       | 0.755013 |   0.766667 |  1.045288 | 0.380974 |
| probe    | R0    | linear | 20260919 | anytls      | 0.765895 |   0.783333 |  1.104832 | 0.383293 |
| probe    | R0    | linear | 20260919 | shadowsocks | 0.510705 |   0.558333 |  1.590726 | 0.554452 |
| probe    | R0    | linear | 20260919 | trojan      | 0.578955 |   0.575000 |  1.414567 | 0.512284 |
| probe    | R0    | linear | 20260919 | vless       | 0.695824 |   0.691667 |  1.332396 | 0.460632 |
| probe    | R0    | linear | 20260919 | vmess       | 0.736018 |   0.766667 |  1.022593 | 0.375056 |
| probe    | R0    | linear | 20260920 | anytls      | 0.815269 |   0.816667 |  1.091188 | 0.383812 |
| probe    | R0    | linear | 20260920 | shadowsocks | 0.510951 |   0.550000 |  1.554285 | 0.534246 |
| probe    | R0    | linear | 20260920 | trojan      | 0.598250 |   0.591667 |  1.417059 | 0.522082 |
| probe    | R0    | linear | 20260920 | vless       | 0.637666 |   0.633333 |  1.374446 | 0.480137 |
| probe    | R0    | linear | 20260920 | vmess       | 0.743571 |   0.750000 |  1.023023 | 0.369195 |
| probe    | R0    | mlp    | 20260918 | anytls      | 0.779489 |   0.791667 |  0.751000 | 0.270625 |
| probe    | R0    | mlp    | 20260918 | shadowsocks | 0.789590 |   0.791667 |  0.990311 | 0.311542 |
| probe    | R0    | mlp    | 20260918 | trojan      | 0.694887 |   0.691667 |  1.341892 | 0.401758 |
| probe    | R0    | mlp    | 20260918 | vless       | 0.769027 |   0.766667 |  1.204237 | 0.346765 |
| probe    | R0    | mlp    | 20260918 | vmess       | 0.767894 |   0.775000 |  0.926071 | 0.297161 |
| probe    | R0    | mlp    | 20260919 | anytls      | 0.836781 |   0.841667 |  0.734101 | 0.265734 |
| probe    | R0    | mlp    | 20260919 | shadowsocks | 0.788615 |   0.791667 |  1.031367 | 0.340093 |
| probe    | R0    | mlp    | 20260919 | trojan      | 0.701317 |   0.700000 |  1.210038 | 0.372180 |
| probe    | R0    | mlp    | 20260919 | vless       | 0.747342 |   0.750000 |  1.221762 | 0.364850 |
| probe    | R0    | mlp    | 20260919 | vmess       | 0.758216 |   0.766667 |  1.045354 | 0.324346 |
| probe    | R0    | mlp    | 20260920 | anytls      | 0.795850 |   0.800000 |  0.811710 | 0.284942 |
| probe    | R0    | mlp    | 20260920 | shadowsocks | 0.686763 |   0.700000 |  1.231583 | 0.429244 |
| probe    | R0    | mlp    | 20260920 | trojan      | 0.680314 |   0.675000 |  1.298218 | 0.430481 |
| probe    | R0    | mlp    | 20260920 | vless       | 0.721420 |   0.716667 |  1.166828 | 0.367834 |
| probe    | R0    | mlp    | 20260920 | vmess       | 0.754245 |   0.766667 |  0.966626 | 0.294692 |

## 错误修复与新增错误

| reference   |   repaired |   new_error |
|:------------|-----------:|------------:|
| B0          |         60 |          38 |
| B0L         |         64 |          39 |
| B1          |         51 |          38 |
| B2          |         42 |          38 |
| B3          |         48 |          36 |
| B4          |         26 |          19 |
| B6          |         52 |          33 |

计数包含三seed，不能将1800次预测当成1800独立访问。内容和业务详细台账见error-transitions.parquet。

## 配对检索与条件敏感性

| arm   | mode               |     top1 |     rank |       gap |
|:------|:-------------------|---------:|---------:|----------:|
| B1    | predicted          | 0.713333 | 1.979444 |  0.171974 |
| B2    | predicted          | 0.762222 | 1.555556 |  0.226069 |
| B3    | predicted          | 0.905000 | 1.156667 |  0.361597 |
| B4    | center_direct      | 0.915000 | 1.150000 |  2.271593 |
| B4    | permuted_condition | 0.818333 | 1.925000 |  0.267798 |
| B4    | predicted          | 0.933333 | 1.101111 |  0.372108 |
| B4    | zero_condition     | 0.796667 | 1.574444 |  0.269164 |
| B5    | center_direct      | 0.931667 | 1.131667 |  2.205906 |
| B5    | permuted_condition | 0.819444 | 1.932222 |  0.264548 |
| B5    | predicted          | 0.928333 | 1.112778 |  0.366246 |
| B5    | zero_condition     | 0.799444 | 1.519444 |  0.280876 |
| B6    | center_direct      | 0.473333 | 3.510000 | -1.188719 |
| B6    | permuted_condition | 0.757778 | 1.966111 |  0.188937 |
| B6    | predicted          | 0.841667 | 1.289444 |  0.269033 |
| B6    | zero_condition     | 0.808333 | 1.365556 |  0.274386 |

此处单独使用test pre作封存后离线诊断，不是业务推理权限。候选仅同部署，屏蔽同内容其他重复。三种中心各25个source-only全训练范围回归，共75拟合，不用测试内容拟合。center_direct与神经检索尺度/目标不同，均不是业务互信息或协议机制识别证据。

## CUDA算量与工程审计

| stage    |   fold |   tasks |   seconds |
|:---------|-------:|--------:|----------:|
| ssl      |      0 |      18 | 11.516866 |
| ssl      |      1 |      18 | 11.488670 |
| ssl      |      2 |      18 | 12.120502 |
| ssl      |      3 |      18 | 11.272663 |
| ssl      |      4 |      18 | 11.545435 |
| probe    |      0 |      42 |  4.618397 |
| probe    |      1 |      42 |  4.745442 |
| probe    |      2 |      42 |  4.987581 |
| probe    |      3 |      42 |  4.769385 |
| probe    |      4 |      42 |  4.855279 |
| finetune |      0 |      24 |  6.923631 |
| finetune |      1 |      24 |  6.886723 |
| finetune |      2 |      24 |  7.061657 |
| finetune |      3 |      24 |  6.741250 |
| finetune |      4 |      24 |  7.295813 |

90个SSL、210个冻结读出、120个最终分类器。每折独立批处理，权重不共享。39600条OOF来自600独立访问，全部重载CUDA预测回放。旧封存输入/源码哈希保持。物理身份资格沿用P2/P3注册，五例未见SYN和历史预检曝光限制继续披露；不是普遍无泄漏数学证明。

## 结项与未验证范围

本轮固定停止，不自动扩大网络、改变lambda或mask、删除业务、补采或启动E2。若只优于group而不优于普通SSL，不能写成普遍配对收益；若不优于B4，新增机制中心用途尚未建立。六维升维不恢复丢失的顺序。本数据已反复研究，不是外部盲测。

## 图与复现

![Final comparisons](../../outputs/mechanism-conditioned-ssl-extend/run-01/figures/final-comparisons.png)

![Frozen probes](../../outputs/mechanism-conditioned-ssl-extend/run-01/figures/frozen-probes.png)

实现为eval/mechanism_conditioned_ssl；契约见experiment-contract.md。执行prepare→engineering→run各stage→diagnose→score→verify→report；E2需另行确认。

## 结果解释与固定诊断补充

B5最终部署等权F1为0.780593，是本轮最高点估计；但相对普通post SSL的+0.006760、通用中心的+0.003302、匿名组的+0.011485，其预登记五项家族校正区间均跨零。相对B0的+0.012146也在校正后跨零。只有相对2000步监督B0L的+0.013618边界通过，校正下界约+0.000007，非常接近零；不能将这一有限结果表述为全面、稳健的机制配对优势。

冻结读出也没有显示B5稳定占优：B5线性F1为0.665009，接近随机E的0.662261，低于group的0.667107；B5冻结MLP为0.746133，低于通用条件B4的0.751558、随机E的0.751450及group的0.750074。这里只是点序，下面按原预登记描述性口径给出普通95%区间，不纳入最终五项家族。随机非线性特征本身具有业务可读性，因此不能把任意SSL高于机会水平当作预训练增量。

最终B5的CE为1.107235 bits，Brier为0.316050，均未优于B4的1.082292和0.314895，也未优于B3的1.065742和0.314896。业务决策、概率质量与上游关系不是同一终点。B5最差部署F1为0.752253，点估计优于各参照；但AnyTLS和SS的B5 F1低于B4，不能以最差部署改善掩盖逐部署例外。

本轮支持继续保留一个可执行、权限清晰的机制条件化表示候选，不支持宣称机制与精确配对已共同建立相对普通SSL和通用中心的独立业务收益。固定摘要、训练日程与反复研究的数据限制继续保留。没有据此新增方法、模型或参数搜索。

| head   | contrast   |     delta |     low95 |   high95 | primary   |
|:-------|:-----------|----------:|----------:|---------:|:----------|
| linear | B5-R0      |  0.002748 | -0.014995 | 0.020930 | False     |
| linear | B5-B1      |  0.025699 |  0.003942 | 0.048629 | False     |
| linear | B5-B2      |  0.031948 |  0.015589 | 0.050146 | False     |
| linear | B5-B3      |  0.002606 | -0.016104 | 0.019106 | False     |
| linear | B5-B4      |  0.001489 | -0.008775 | 0.012115 | False     |
| linear | B5-B6      | -0.002098 | -0.016104 | 0.012191 | False     |
| mlp    | B5-R0      | -0.005317 | -0.015786 | 0.004592 | False     |
| mlp    | B5-B1      |  0.009747 | -0.003797 | 0.023035 | False     |
| mlp    | B5-B2      | -0.000888 | -0.017216 | 0.014723 | False     |
| mlp    | B5-B3      | -0.000379 | -0.015366 | 0.015113 | False     |
| mlp    | B5-B4      | -0.005425 | -0.015096 | 0.004325 | False     |
| mlp    | B5-B6      | -0.003941 | -0.016998 | 0.009023 | False     |

330个部署/seed/头F1点值及三个原抽样上的24个最终臂bootstrap值，经独立sklearn实现重算一致，最大误差小于1e−12。内容级错误台账已补齐，不重造抽样或改五项主比较。
