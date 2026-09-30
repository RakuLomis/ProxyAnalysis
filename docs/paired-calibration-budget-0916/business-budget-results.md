# 配对预算：完整统计表

指标先汇总五折OOF，再平均seed/轮换；没有概率集成。CE为bits，Brier为六类概率平方误差之和。

## 36格均值

| protocol    |   k | arm   |       F1 |       BA |   CE_bits |    Brier |
|:------------|----:|:------|---------:|---------:|----------:|---------:|
| SHADOWSOCKS |   1 | B0    | 0.940961 | 0.940972 |  0.350004 | 0.096516 |
| SHADOWSOCKS |   1 | B1    | 0.955765 | 0.955556 |  0.333412 | 0.091801 |
| SHADOWSOCKS |   1 | B2    | 0.962507 | 0.962500 |  0.309163 | 0.074672 |
| SHADOWSOCKS |   1 | B3    | 0.964514 | 0.964583 |  0.302204 | 0.072187 |
| SHADOWSOCKS |   1 | B4    | 0.963134 | 0.963194 |  0.295386 | 0.070051 |
| SHADOWSOCKS |   1 | B5    | 0.927402 | 0.927778 |  0.473612 | 0.151682 |
| SHADOWSOCKS |   2 | B0    | 0.949293 | 0.949306 |  0.325247 | 0.084613 |
| SHADOWSOCKS |   2 | B1    | 0.964674 | 0.964583 |  0.300701 | 0.073172 |
| SHADOWSOCKS |   2 | B2    | 0.965926 | 0.965972 |  0.300788 | 0.071015 |
| SHADOWSOCKS |   2 | B3    | 0.966626 | 0.966667 |  0.301271 | 0.071243 |
| SHADOWSOCKS |   2 | B4    | 0.967315 | 0.967361 |  0.299721 | 0.070337 |
| SHADOWSOCKS |   2 | B5    | 0.945054 | 0.945139 |  0.442068 | 0.133168 |
| SHADOWSOCKS |   3 | B0    | 0.959697 | 0.959722 |  0.300652 | 0.072499 |
| SHADOWSOCKS |   3 | B1    | 0.967349 | 0.967361 |  0.297237 | 0.070533 |
| SHADOWSOCKS |   3 | B2    | 0.964560 | 0.964583 |  0.295590 | 0.068356 |
| SHADOWSOCKS |   3 | B3    | 0.964556 | 0.964583 |  0.297635 | 0.069523 |
| SHADOWSOCKS |   3 | B4    | 0.965253 | 0.965278 |  0.294925 | 0.068038 |
| SHADOWSOCKS |   3 | B5    | 0.956883 | 0.956944 |  0.347847 | 0.087835 |
| VLESS       |   1 | B0    | 0.726497 | 0.730556 |  1.326262 | 0.409080 |
| VLESS       |   1 | B1    | 0.786466 | 0.794444 |  0.797543 | 0.297714 |
| VLESS       |   1 | B2    | 0.778052 | 0.784028 |  0.821395 | 0.312777 |
| VLESS       |   1 | B3    | 0.791903 | 0.798611 |  0.766278 | 0.293128 |
| VLESS       |   1 | B4    | 0.805795 | 0.814583 |  0.738678 | 0.280861 |
| VLESS       |   1 | B5    | 0.780427 | 0.793750 |  0.768203 | 0.308909 |
| VLESS       |   2 | B0    | 0.776464 | 0.778472 |  0.862056 | 0.307534 |
| VLESS       |   2 | B1    | 0.819549 | 0.826389 |  0.720036 | 0.267568 |
| VLESS       |   2 | B2    | 0.808865 | 0.815972 |  0.727970 | 0.276563 |
| VLESS       |   2 | B3    | 0.801930 | 0.810417 |  0.720792 | 0.274141 |
| VLESS       |   2 | B4    | 0.823317 | 0.830556 |  0.709704 | 0.264763 |
| VLESS       |   2 | B5    | 0.810647 | 0.823611 |  0.702923 | 0.280109 |
| VLESS       |   3 | B0    | 0.809455 | 0.813194 |  0.711316 | 0.267378 |
| VLESS       |   3 | B1    | 0.827379 | 0.834722 |  0.690579 | 0.255570 |
| VLESS       |   3 | B2    | 0.823402 | 0.831250 |  0.691910 | 0.258911 |
| VLESS       |   3 | B3    | 0.817139 | 0.825000 |  0.697940 | 0.261659 |
| VLESS       |   3 | B4    | 0.821500 | 0.830556 |  0.684335 | 0.255002 |
| VLESS       |   3 | B5    | 0.825928 | 0.838194 |  0.650073 | 0.253828 |

## 逐seed（平均轮换）

| protocol    |   k | arm   |     seed |       F1 |       BA |   CE_bits |    Brier |
|:------------|----:|:------|---------:|---------:|---------:|----------:|---------:|
| SHADOWSOCKS |   1 | B0    | 20260918 | 0.929211 | 0.929167 |  0.375128 | 0.105630 |
| SHADOWSOCKS |   1 | B0    | 20260919 | 0.939498 | 0.939583 |  0.370966 | 0.102602 |
| SHADOWSOCKS |   1 | B0    | 20260920 | 0.954175 | 0.954167 |  0.303919 | 0.081316 |
| SHADOWSOCKS |   1 | B1    | 20260918 | 0.941961 | 0.941667 |  0.377797 | 0.112408 |
| SHADOWSOCKS |   1 | B1    | 20260919 | 0.956550 | 0.956250 |  0.327292 | 0.089199 |
| SHADOWSOCKS |   1 | B1    | 20260920 | 0.968783 | 0.968750 |  0.295147 | 0.073797 |
| SHADOWSOCKS |   1 | B2    | 20260918 | 0.956261 | 0.956250 |  0.345448 | 0.086772 |
| SHADOWSOCKS |   1 | B2    | 20260919 | 0.962530 | 0.962500 |  0.306698 | 0.074737 |
| SHADOWSOCKS |   1 | B2    | 20260920 | 0.968729 | 0.968750 |  0.275344 | 0.062508 |
| SHADOWSOCKS |   1 | B3    | 20260918 | 0.956160 | 0.956250 |  0.346594 | 0.088191 |
| SHADOWSOCKS |   1 | B3    | 20260919 | 0.968678 | 0.968750 |  0.290920 | 0.067829 |
| SHADOWSOCKS |   1 | B3    | 20260920 | 0.968703 | 0.968750 |  0.269099 | 0.060542 |
| SHADOWSOCKS |   1 | B4    | 20260918 | 0.956168 | 0.956250 |  0.337641 | 0.085107 |
| SHADOWSOCKS |   1 | B4    | 20260919 | 0.968685 | 0.968750 |  0.281704 | 0.064671 |
| SHADOWSOCKS |   1 | B4    | 20260920 | 0.964549 | 0.964583 |  0.266814 | 0.060376 |
| SHADOWSOCKS |   1 | B5    | 20260918 | 0.916135 | 0.916667 |  0.490609 | 0.161058 |
| SHADOWSOCKS |   1 | B5    | 20260919 | 0.926695 | 0.927083 |  0.474362 | 0.151630 |
| SHADOWSOCKS |   1 | B5    | 20260920 | 0.939375 | 0.939583 |  0.455864 | 0.142358 |
| SHADOWSOCKS |   2 | B0    | 20260918 | 0.939583 | 0.939583 |  0.358405 | 0.097515 |
| SHADOWSOCKS |   2 | B0    | 20260919 | 0.949946 | 0.950000 |  0.339942 | 0.087764 |
| SHADOWSOCKS |   2 | B0    | 20260920 | 0.958351 | 0.958333 |  0.277393 | 0.068559 |
| SHADOWSOCKS |   2 | B1    | 20260918 | 0.954354 | 0.954167 |  0.334267 | 0.085992 |
| SHADOWSOCKS |   2 | B1    | 20260919 | 0.968790 | 0.968750 |  0.297323 | 0.071455 |
| SHADOWSOCKS |   2 | B1    | 20260920 | 0.970878 | 0.970833 |  0.270515 | 0.062068 |
| SHADOWSOCKS |   2 | B2    | 20260918 | 0.956198 | 0.956250 |  0.336031 | 0.083030 |
| SHADOWSOCKS |   2 | B2    | 20260919 | 0.968710 | 0.968750 |  0.300124 | 0.071144 |
| SHADOWSOCKS |   2 | B2    | 20260920 | 0.972870 | 0.972917 |  0.266209 | 0.058872 |
| SHADOWSOCKS |   2 | B3    | 20260918 | 0.960389 | 0.960417 |  0.341448 | 0.085187 |
| SHADOWSOCKS |   2 | B3    | 20260919 | 0.968703 | 0.968750 |  0.294479 | 0.068581 |
| SHADOWSOCKS |   2 | B3    | 20260920 | 0.970786 | 0.970833 |  0.267886 | 0.059961 |
| SHADOWSOCKS |   2 | B4    | 20260918 | 0.958281 | 0.958333 |  0.338904 | 0.084949 |
| SHADOWSOCKS |   2 | B4    | 20260919 | 0.972870 | 0.972917 |  0.293625 | 0.066873 |
| SHADOWSOCKS |   2 | B4    | 20260920 | 0.970793 | 0.970833 |  0.266634 | 0.059187 |
| SHADOWSOCKS |   2 | B5    | 20260918 | 0.945748 | 0.945833 |  0.455812 | 0.138790 |
| SHADOWSOCKS |   2 | B5    | 20260919 | 0.939542 | 0.939583 |  0.452215 | 0.139586 |
| SHADOWSOCKS |   2 | B5    | 20260920 | 0.949873 | 0.950000 |  0.418176 | 0.121129 |
| SHADOWSOCKS |   3 | B0    | 20260918 | 0.947871 | 0.947917 |  0.338923 | 0.086758 |
| SHADOWSOCKS |   3 | B0    | 20260919 | 0.964566 | 0.964583 |  0.298308 | 0.069444 |
| SHADOWSOCKS |   3 | B0    | 20260920 | 0.966654 | 0.966667 |  0.264724 | 0.061296 |
| SHADOWSOCKS |   3 | B1    | 20260918 | 0.956233 | 0.956250 |  0.335291 | 0.084720 |
| SHADOWSOCKS |   3 | B1    | 20260919 | 0.972908 | 0.972917 |  0.294177 | 0.067577 |
| SHADOWSOCKS |   3 | B1    | 20260920 | 0.972908 | 0.972917 |  0.262242 | 0.059302 |
| SHADOWSOCKS |   3 | B2    | 20260918 | 0.958312 | 0.958333 |  0.329633 | 0.080115 |
| SHADOWSOCKS |   3 | B2    | 20260919 | 0.966646 | 0.966667 |  0.296320 | 0.067850 |
| SHADOWSOCKS |   3 | B2    | 20260920 | 0.968723 | 0.968750 |  0.260817 | 0.057103 |
| SHADOWSOCKS |   3 | B3    | 20260918 | 0.958312 | 0.958333 |  0.332454 | 0.082051 |
| SHADOWSOCKS |   3 | B3    | 20260919 | 0.968716 | 0.968750 |  0.295367 | 0.067699 |
| SHADOWSOCKS |   3 | B3    | 20260920 | 0.966639 | 0.966667 |  0.265083 | 0.058818 |
| SHADOWSOCKS |   3 | B4    | 20260918 | 0.958312 | 0.958333 |  0.329584 | 0.081543 |
| SHADOWSOCKS |   3 | B4    | 20260919 | 0.970799 | 0.970833 |  0.295215 | 0.065410 |
| SHADOWSOCKS |   3 | B4    | 20260920 | 0.966646 | 0.966667 |  0.259978 | 0.057161 |
| SHADOWSOCKS |   3 | B5    | 20260918 | 0.952012 | 0.952083 |  0.376007 | 0.099152 |
| SHADOWSOCKS |   3 | B5    | 20260919 | 0.956181 | 0.956250 |  0.353029 | 0.087842 |
| SHADOWSOCKS |   3 | B5    | 20260920 | 0.962456 | 0.962500 |  0.314505 | 0.076510 |
| VLESS       |   1 | B0    | 20260918 | 0.702464 | 0.706250 |  1.273118 | 0.424076 |
| VLESS       |   1 | B0    | 20260919 | 0.738349 | 0.741667 |  1.269375 | 0.393383 |
| VLESS       |   1 | B0    | 20260920 | 0.738677 | 0.743750 |  1.436294 | 0.409782 |
| VLESS       |   1 | B1    | 20260918 | 0.783832 | 0.789583 |  0.792213 | 0.305129 |
| VLESS       |   1 | B1    | 20260919 | 0.798665 | 0.804167 |  0.778598 | 0.284209 |
| VLESS       |   1 | B1    | 20260920 | 0.776902 | 0.789583 |  0.821818 | 0.303804 |
| VLESS       |   1 | B2    | 20260918 | 0.780830 | 0.785417 |  0.817061 | 0.320117 |
| VLESS       |   1 | B2    | 20260919 | 0.788774 | 0.793750 |  0.802049 | 0.301533 |
| VLESS       |   1 | B2    | 20260920 | 0.764552 | 0.772917 |  0.845075 | 0.316682 |
| VLESS       |   1 | B3    | 20260918 | 0.787467 | 0.793750 |  0.765057 | 0.301422 |
| VLESS       |   1 | B3    | 20260919 | 0.775848 | 0.785417 |  0.748920 | 0.285637 |
| VLESS       |   1 | B3    | 20260920 | 0.812395 | 0.816667 |  0.784858 | 0.292325 |
| VLESS       |   1 | B4    | 20260918 | 0.799792 | 0.808333 |  0.749764 | 0.292518 |
| VLESS       |   1 | B4    | 20260919 | 0.799986 | 0.810417 |  0.724248 | 0.274562 |
| VLESS       |   1 | B4    | 20260920 | 0.817605 | 0.825000 |  0.742023 | 0.275503 |
| VLESS       |   1 | B5    | 20260918 | 0.766887 | 0.785417 |  0.774956 | 0.313711 |
| VLESS       |   1 | B5    | 20260919 | 0.772241 | 0.785417 |  0.765498 | 0.306194 |
| VLESS       |   1 | B5    | 20260920 | 0.802154 | 0.810417 |  0.764154 | 0.306821 |
| VLESS       |   2 | B0    | 20260918 | 0.766680 | 0.768750 |  0.881492 | 0.321855 |
| VLESS       |   2 | B0    | 20260919 | 0.781113 | 0.783333 |  0.831895 | 0.294045 |
| VLESS       |   2 | B0    | 20260920 | 0.781598 | 0.783333 |  0.872781 | 0.306703 |
| VLESS       |   2 | B1    | 20260918 | 0.818144 | 0.822917 |  0.721945 | 0.277390 |
| VLESS       |   2 | B1    | 20260919 | 0.811559 | 0.818750 |  0.709451 | 0.256754 |
| VLESS       |   2 | B1    | 20260920 | 0.828943 | 0.837500 |  0.728713 | 0.268560 |
| VLESS       |   2 | B2    | 20260918 | 0.802236 | 0.808333 |  0.725529 | 0.285944 |
| VLESS       |   2 | B2    | 20260919 | 0.812107 | 0.820833 |  0.714712 | 0.267498 |
| VLESS       |   2 | B2    | 20260920 | 0.812254 | 0.818750 |  0.743670 | 0.276248 |
| VLESS       |   2 | B3    | 20260918 | 0.806360 | 0.814583 |  0.728162 | 0.284681 |
| VLESS       |   2 | B3    | 20260919 | 0.807908 | 0.816667 |  0.702338 | 0.266844 |
| VLESS       |   2 | B3    | 20260920 | 0.791521 | 0.800000 |  0.731875 | 0.270897 |
| VLESS       |   2 | B4    | 20260918 | 0.813355 | 0.818750 |  0.722564 | 0.275568 |
| VLESS       |   2 | B4    | 20260919 | 0.828002 | 0.837500 |  0.700471 | 0.260142 |
| VLESS       |   2 | B4    | 20260920 | 0.828593 | 0.835417 |  0.706077 | 0.258581 |
| VLESS       |   2 | B5    | 20260918 | 0.805657 | 0.818750 |  0.715443 | 0.286355 |
| VLESS       |   2 | B5    | 20260919 | 0.803847 | 0.820833 |  0.696292 | 0.276862 |
| VLESS       |   2 | B5    | 20260920 | 0.822437 | 0.831250 |  0.697033 | 0.277110 |
| VLESS       |   3 | B0    | 20260918 | 0.794785 | 0.800000 |  0.735194 | 0.284026 |
| VLESS       |   3 | B0    | 20260919 | 0.812111 | 0.814583 |  0.688066 | 0.256303 |
| VLESS       |   3 | B0    | 20260920 | 0.821470 | 0.825000 |  0.710687 | 0.261805 |
| VLESS       |   3 | B1    | 20260918 | 0.806338 | 0.812500 |  0.706195 | 0.270144 |
| VLESS       |   3 | B1    | 20260919 | 0.832982 | 0.841667 |  0.679210 | 0.245658 |
| VLESS       |   3 | B1    | 20260920 | 0.842817 | 0.850000 |  0.686334 | 0.250909 |
| VLESS       |   3 | B2    | 20260918 | 0.812818 | 0.820833 |  0.701627 | 0.270717 |
| VLESS       |   3 | B2    | 20260919 | 0.835176 | 0.843750 |  0.681978 | 0.251934 |
| VLESS       |   3 | B2    | 20260920 | 0.822211 | 0.829167 |  0.692125 | 0.254083 |
| VLESS       |   3 | B3    | 20260918 | 0.815505 | 0.822917 |  0.715524 | 0.273238 |
| VLESS       |   3 | B3    | 20260919 | 0.820592 | 0.831250 |  0.679455 | 0.253655 |
| VLESS       |   3 | B3    | 20260920 | 0.815322 | 0.820833 |  0.698841 | 0.258085 |
| VLESS       |   3 | B4    | 20260918 | 0.801415 | 0.814583 |  0.698566 | 0.267672 |
| VLESS       |   3 | B4    | 20260919 | 0.832970 | 0.841667 |  0.670070 | 0.248844 |
| VLESS       |   3 | B4    | 20260920 | 0.830115 | 0.835417 |  0.684368 | 0.248490 |
| VLESS       |   3 | B5    | 20260918 | 0.820205 | 0.833333 |  0.672402 | 0.263465 |
| VLESS       |   3 | B5    | 20260919 | 0.814266 | 0.829167 |  0.627913 | 0.247258 |
| VLESS       |   3 | B5    | 20260920 | 0.843313 | 0.852083 |  0.649905 | 0.250762 |

## 逐轮换（平均seed）

| protocol    |   k | arm   |   rotation |       F1 |       BA |   CE_bits |    Brier |
|:------------|----:|:------|-----------:|---------:|---------:|----------:|---------:|
| SHADOWSOCKS |   1 | B0    |          0 | 0.952659 | 0.952778 |  0.319204 | 0.087105 |
| SHADOWSOCKS |   1 | B0    |          1 | 0.944259 | 0.944444 |  0.349231 | 0.096386 |
| SHADOWSOCKS |   1 | B0    |          2 | 0.919528 | 0.919444 |  0.417866 | 0.120206 |
| SHADOWSOCKS |   1 | B0    |          3 | 0.947400 | 0.947222 |  0.313716 | 0.082368 |
| SHADOWSOCKS |   1 | B1    |          0 | 0.955496 | 0.955556 |  0.332950 | 0.093300 |
| SHADOWSOCKS |   1 | B1    |          1 | 0.961411 | 0.961111 |  0.321195 | 0.082238 |
| SHADOWSOCKS |   1 | B1    |          2 | 0.953116 | 0.952778 |  0.338089 | 0.097269 |
| SHADOWSOCKS |   1 | B1    |          3 | 0.953036 | 0.952778 |  0.341413 | 0.094398 |
| SHADOWSOCKS |   1 | B2    |          0 | 0.966628 | 0.966667 |  0.301688 | 0.071858 |
| SHADOWSOCKS |   1 | B2    |          1 | 0.969364 | 0.969444 |  0.317123 | 0.075338 |
| SHADOWSOCKS |   1 | B2    |          2 | 0.950057 | 0.950000 |  0.312335 | 0.078956 |
| SHADOWSOCKS |   1 | B2    |          3 | 0.963977 | 0.963889 |  0.305507 | 0.072537 |
| SHADOWSOCKS |   1 | B3    |          0 | 0.961064 | 0.961111 |  0.302041 | 0.072601 |
| SHADOWSOCKS |   1 | B3    |          1 | 0.966586 | 0.966667 |  0.305442 | 0.071914 |
| SHADOWSOCKS |   1 | B3    |          2 | 0.960998 | 0.961111 |  0.305562 | 0.075353 |
| SHADOWSOCKS |   1 | B3    |          3 | 0.969406 | 0.969444 |  0.295773 | 0.068881 |
| SHADOWSOCKS |   1 | B4    |          0 | 0.955526 | 0.955556 |  0.297004 | 0.071864 |
| SHADOWSOCKS |   1 | B4    |          1 | 0.969397 | 0.969444 |  0.297202 | 0.068957 |
| SHADOWSOCKS |   1 | B4    |          2 | 0.966553 | 0.966667 |  0.294778 | 0.070746 |
| SHADOWSOCKS |   1 | B4    |          3 | 0.961059 | 0.961111 |  0.292560 | 0.068638 |
| SHADOWSOCKS |   1 | B5    |          0 | 0.935673 | 0.936111 |  0.474848 | 0.147342 |
| SHADOWSOCKS |   1 | B5    |          1 | 0.924953 | 0.925000 |  0.491351 | 0.161406 |
| SHADOWSOCKS |   1 | B5    |          2 | 0.918838 | 0.919444 |  0.472290 | 0.151632 |
| SHADOWSOCKS |   1 | B5    |          3 | 0.930143 | 0.930556 |  0.455959 | 0.146349 |
| SHADOWSOCKS |   2 | B0    |          0 | 0.955517 | 0.955556 |  0.311144 | 0.080217 |
| SHADOWSOCKS |   2 | B0    |          1 | 0.944422 | 0.944444 |  0.354778 | 0.093225 |
| SHADOWSOCKS |   2 | B0    |          2 | 0.938911 | 0.938889 |  0.353401 | 0.098891 |
| SHADOWSOCKS |   2 | B0    |          3 | 0.958323 | 0.958333 |  0.281663 | 0.066119 |
| SHADOWSOCKS |   2 | B1    |          0 | 0.963878 | 0.963889 |  0.302184 | 0.072587 |
| SHADOWSOCKS |   2 | B1    |          1 | 0.966795 | 0.966667 |  0.291266 | 0.069696 |
| SHADOWSOCKS |   2 | B1    |          2 | 0.955811 | 0.955556 |  0.307347 | 0.077805 |
| SHADOWSOCKS |   2 | B1    |          3 | 0.972212 | 0.972222 |  0.302009 | 0.072598 |
| SHADOWSOCKS |   2 | B2    |          0 | 0.966628 | 0.966667 |  0.304028 | 0.070200 |
| SHADOWSOCKS |   2 | B2    |          1 | 0.966586 | 0.966667 |  0.308879 | 0.073755 |
| SHADOWSOCKS |   2 | B2    |          2 | 0.963851 | 0.963889 |  0.299265 | 0.073440 |
| SHADOWSOCKS |   2 | B2    |          3 | 0.966637 | 0.966667 |  0.290980 | 0.066665 |
| SHADOWSOCKS |   2 | B3    |          0 | 0.969406 | 0.969444 |  0.308639 | 0.072669 |
| SHADOWSOCKS |   2 | B3    |          1 | 0.966620 | 0.966667 |  0.302706 | 0.072326 |
| SHADOWSOCKS |   2 | B3    |          2 | 0.966628 | 0.966667 |  0.295150 | 0.069943 |
| SHADOWSOCKS |   2 | B3    |          3 | 0.963851 | 0.963889 |  0.298590 | 0.070033 |
| SHADOWSOCKS |   2 | B4    |          0 | 0.969406 | 0.969444 |  0.308852 | 0.073898 |
| SHADOWSOCKS |   2 | B4    |          1 | 0.969364 | 0.969444 |  0.301021 | 0.070313 |
| SHADOWSOCKS |   2 | B4    |          2 | 0.966637 | 0.966667 |  0.293414 | 0.068141 |
| SHADOWSOCKS |   2 | B4    |          3 | 0.963851 | 0.963889 |  0.295598 | 0.068994 |
| SHADOWSOCKS |   2 | B5    |          0 | 0.949940 | 0.950000 |  0.438513 | 0.129813 |
| SHADOWSOCKS |   2 | B5    |          1 | 0.941627 | 0.941667 |  0.432457 | 0.128847 |
| SHADOWSOCKS |   2 | B5    |          2 | 0.947013 | 0.947222 |  0.444271 | 0.133451 |
| SHADOWSOCKS |   2 | B5    |          3 | 0.941637 | 0.941667 |  0.453031 | 0.140563 |
| SHADOWSOCKS |   3 | B0    |          0 | 0.963878 | 0.963889 |  0.303206 | 0.073860 |
| SHADOWSOCKS |   3 | B0    |          1 | 0.952722 | 0.952778 |  0.313377 | 0.077509 |
| SHADOWSOCKS |   3 | B0    |          2 | 0.952753 | 0.952778 |  0.301577 | 0.076075 |
| SHADOWSOCKS |   3 | B0    |          3 | 0.969434 | 0.969444 |  0.284447 | 0.062553 |
| SHADOWSOCKS |   3 | B1    |          0 | 0.966661 | 0.966667 |  0.295351 | 0.070463 |
| SHADOWSOCKS |   3 | B1    |          1 | 0.966651 | 0.966667 |  0.291906 | 0.068828 |
| SHADOWSOCKS |   3 | B1    |          2 | 0.966651 | 0.966667 |  0.303162 | 0.074189 |
| SHADOWSOCKS |   3 | B1    |          3 | 0.969434 | 0.969444 |  0.298527 | 0.068652 |
| SHADOWSOCKS |   3 | B2    |          0 | 0.966637 | 0.966667 |  0.302047 | 0.070797 |
| SHADOWSOCKS |   3 | B2    |          1 | 0.963868 | 0.963889 |  0.300323 | 0.070461 |
| SHADOWSOCKS |   3 | B2    |          2 | 0.963868 | 0.963889 |  0.286860 | 0.067545 |
| SHADOWSOCKS |   3 | B2    |          3 | 0.963868 | 0.963889 |  0.293129 | 0.064621 |
| SHADOWSOCKS |   3 | B3    |          0 | 0.969406 | 0.969444 |  0.305026 | 0.072438 |
| SHADOWSOCKS |   3 | B3    |          1 | 0.963868 | 0.963889 |  0.297494 | 0.069052 |
| SHADOWSOCKS |   3 | B3    |          2 | 0.961082 | 0.961111 |  0.288714 | 0.067681 |
| SHADOWSOCKS |   3 | B3    |          3 | 0.963868 | 0.963889 |  0.299305 | 0.068920 |
| SHADOWSOCKS |   3 | B4    |          0 | 0.963868 | 0.963889 |  0.299149 | 0.070421 |
| SHADOWSOCKS |   3 | B4    |          1 | 0.966637 | 0.966667 |  0.292969 | 0.066257 |
| SHADOWSOCKS |   3 | B4    |          2 | 0.966637 | 0.966667 |  0.290203 | 0.067929 |
| SHADOWSOCKS |   3 | B4    |          3 | 0.963868 | 0.963889 |  0.297380 | 0.067544 |
| SHADOWSOCKS |   3 | B5    |          0 | 0.961057 | 0.961111 |  0.355197 | 0.091477 |
| SHADOWSOCKS |   3 | B5    |          1 | 0.958290 | 0.958333 |  0.335678 | 0.082942 |
| SHADOWSOCKS |   3 | B5    |          2 | 0.952695 | 0.952778 |  0.353292 | 0.088417 |
| SHADOWSOCKS |   3 | B5    |          3 | 0.955489 | 0.955556 |  0.347221 | 0.088504 |
| VLESS       |   1 | B0    |          0 | 0.685132 | 0.694444 |  1.407762 | 0.430131 |
| VLESS       |   1 | B0    |          1 | 0.736723 | 0.736111 |  1.433522 | 0.428300 |
| VLESS       |   1 | B0    |          2 | 0.716682 | 0.722222 |  1.484299 | 0.435350 |
| VLESS       |   1 | B0    |          3 | 0.767450 | 0.769444 |  0.979466 | 0.342540 |
| VLESS       |   1 | B1    |          0 | 0.796938 | 0.802778 |  0.780434 | 0.287102 |
| VLESS       |   1 | B1    |          1 | 0.775039 | 0.783333 |  0.818840 | 0.312375 |
| VLESS       |   1 | B1    |          2 | 0.756032 | 0.763889 |  0.825812 | 0.304698 |
| VLESS       |   1 | B1    |          3 | 0.817856 | 0.827778 |  0.765085 | 0.286680 |
| VLESS       |   1 | B2    |          0 | 0.769392 | 0.775000 |  0.833498 | 0.310795 |
| VLESS       |   1 | B2    |          1 | 0.783814 | 0.791667 |  0.835221 | 0.321994 |
| VLESS       |   1 | B2    |          2 | 0.774560 | 0.777778 |  0.801530 | 0.302687 |
| VLESS       |   1 | B2    |          3 | 0.784443 | 0.791667 |  0.815331 | 0.315635 |
| VLESS       |   1 | B3    |          0 | 0.780257 | 0.786111 |  0.778530 | 0.293097 |
| VLESS       |   1 | B3    |          1 | 0.789276 | 0.797222 |  0.762388 | 0.294273 |
| VLESS       |   1 | B3    |          2 | 0.798454 | 0.802778 |  0.762859 | 0.290046 |
| VLESS       |   1 | B3    |          3 | 0.799627 | 0.808333 |  0.761336 | 0.295096 |
| VLESS       |   1 | B4    |          0 | 0.809625 | 0.819444 |  0.758520 | 0.286892 |
| VLESS       |   1 | B4    |          1 | 0.796313 | 0.808333 |  0.725969 | 0.279769 |
| VLESS       |   1 | B4    |          2 | 0.810385 | 0.816667 |  0.733045 | 0.276464 |
| VLESS       |   1 | B4    |          3 | 0.806854 | 0.813889 |  0.737180 | 0.280318 |
| VLESS       |   1 | B5    |          0 | 0.739492 | 0.755556 |  0.892823 | 0.361810 |
| VLESS       |   1 | B5    |          1 | 0.778655 | 0.791667 |  0.722004 | 0.292643 |
| VLESS       |   1 | B5    |          2 | 0.784285 | 0.788889 |  0.751126 | 0.302078 |
| VLESS       |   1 | B5    |          3 | 0.819276 | 0.838889 |  0.706858 | 0.279104 |
| VLESS       |   2 | B0    |          0 | 0.756590 | 0.758333 |  0.841235 | 0.312084 |
| VLESS       |   2 | B0    |          1 | 0.760702 | 0.763889 |  0.885565 | 0.325626 |
| VLESS       |   2 | B0    |          2 | 0.778167 | 0.780556 |  0.946215 | 0.327362 |
| VLESS       |   2 | B0    |          3 | 0.810397 | 0.811111 |  0.775208 | 0.265065 |
| VLESS       |   2 | B1    |          0 | 0.811986 | 0.822222 |  0.713790 | 0.266437 |
| VLESS       |   2 | B1    |          1 | 0.787837 | 0.794444 |  0.749091 | 0.284097 |
| VLESS       |   2 | B1    |          2 | 0.829773 | 0.833333 |  0.720345 | 0.262030 |
| VLESS       |   2 | B1    |          3 | 0.848599 | 0.855556 |  0.696919 | 0.257708 |
| VLESS       |   2 | B2    |          0 | 0.807453 | 0.813889 |  0.731999 | 0.277350 |
| VLESS       |   2 | B2    |          1 | 0.787569 | 0.797222 |  0.732058 | 0.285220 |
| VLESS       |   2 | B2    |          2 | 0.809147 | 0.813889 |  0.729141 | 0.276924 |
| VLESS       |   2 | B2    |          3 | 0.831293 | 0.838889 |  0.718684 | 0.266759 |
| VLESS       |   2 | B3    |          0 | 0.796075 | 0.802778 |  0.717019 | 0.273261 |
| VLESS       |   2 | B3    |          1 | 0.794973 | 0.802778 |  0.721594 | 0.277675 |
| VLESS       |   2 | B3    |          2 | 0.813362 | 0.822222 |  0.723935 | 0.274497 |
| VLESS       |   2 | B3    |          3 | 0.803308 | 0.813889 |  0.720618 | 0.271129 |
| VLESS       |   2 | B4    |          0 | 0.796380 | 0.805556 |  0.712215 | 0.270306 |
| VLESS       |   2 | B4    |          1 | 0.807142 | 0.813889 |  0.705324 | 0.265837 |
| VLESS       |   2 | B4    |          2 | 0.851651 | 0.855556 |  0.711166 | 0.261978 |
| VLESS       |   2 | B4    |          3 | 0.838094 | 0.847222 |  0.710110 | 0.260933 |
| VLESS       |   2 | B5    |          0 | 0.805491 | 0.816667 |  0.722698 | 0.287667 |
| VLESS       |   2 | B5    |          1 | 0.810308 | 0.816667 |  0.679039 | 0.274334 |
| VLESS       |   2 | B5    |          2 | 0.836836 | 0.847222 |  0.674796 | 0.268259 |
| VLESS       |   2 | B5    |          3 | 0.789953 | 0.813889 |  0.735157 | 0.290176 |
| VLESS       |   3 | B0    |          0 | 0.788805 | 0.791667 |  0.718654 | 0.278274 |
| VLESS       |   3 | B0    |          1 | 0.815182 | 0.819444 |  0.700082 | 0.266656 |
| VLESS       |   3 | B0    |          2 | 0.821981 | 0.827778 |  0.702576 | 0.254909 |
| VLESS       |   3 | B0    |          3 | 0.811854 | 0.813889 |  0.723952 | 0.269674 |
| VLESS       |   3 | B1    |          0 | 0.808925 | 0.816667 |  0.696448 | 0.261351 |
| VLESS       |   3 | B1    |          1 | 0.830612 | 0.836111 |  0.694802 | 0.255211 |
| VLESS       |   3 | B1    |          2 | 0.836812 | 0.844444 |  0.691542 | 0.253011 |
| VLESS       |   3 | B1    |          3 | 0.833165 | 0.841667 |  0.679526 | 0.252708 |
| VLESS       |   3 | B2    |          0 | 0.815624 | 0.822222 |  0.694928 | 0.263540 |
| VLESS       |   3 | B2    |          1 | 0.809367 | 0.816667 |  0.689177 | 0.262668 |
| VLESS       |   3 | B2    |          2 | 0.840065 | 0.847222 |  0.698484 | 0.255931 |
| VLESS       |   3 | B2    |          3 | 0.828552 | 0.838889 |  0.685051 | 0.253506 |
| VLESS       |   3 | B3    |          0 | 0.806133 | 0.813889 |  0.701357 | 0.262342 |
| VLESS       |   3 | B3    |          1 | 0.810959 | 0.819444 |  0.692442 | 0.262804 |
| VLESS       |   3 | B3    |          2 | 0.831414 | 0.838889 |  0.709454 | 0.262208 |
| VLESS       |   3 | B3    |          3 | 0.820052 | 0.827778 |  0.688506 | 0.259283 |
| VLESS       |   3 | B4    |          0 | 0.809790 | 0.816667 |  0.684210 | 0.253927 |
| VLESS       |   3 | B4    |          1 | 0.812587 | 0.822222 |  0.682132 | 0.257918 |
| VLESS       |   3 | B4    |          2 | 0.839090 | 0.847222 |  0.690062 | 0.253084 |
| VLESS       |   3 | B4    |          3 | 0.824533 | 0.836111 |  0.680935 | 0.255079 |
| VLESS       |   3 | B5    |          0 | 0.809713 | 0.819444 |  0.654378 | 0.258045 |
| VLESS       |   3 | B5    |          1 | 0.829732 | 0.838889 |  0.637962 | 0.249406 |
| VLESS       |   3 | B5    |          2 | 0.842234 | 0.855556 |  0.654644 | 0.255172 |
| VLESS       |   3 | B5    |          3 | 0.822034 | 0.838889 |  0.653310 | 0.252690 |

## 业务召回

| protocol    |   k | arm   | label_id                             |   recall |
|:------------|----:|:------|:-------------------------------------|---------:|
| SHADOWSOCKS |   1 | B0    | bing.com::search_results_view        | 0.937500 |
| SHADOWSOCKS |   1 | B0    | developer.mozilla.org::document_view | 0.987500 |
| SHADOWSOCKS |   1 | B0    | github.com::repository_view          | 0.929167 |
| SHADOWSOCKS |   1 | B0    | wikipedia.org::article_view          | 0.970833 |
| SHADOWSOCKS |   1 | B0    | youtube.com::search_results_view     | 0.904167 |
| SHADOWSOCKS |   1 | B0    | youtube.com::video_playback          | 0.916667 |
| SHADOWSOCKS |   1 | B1    | bing.com::search_results_view        | 0.950000 |
| SHADOWSOCKS |   1 | B1    | developer.mozilla.org::document_view | 0.937500 |
| SHADOWSOCKS |   1 | B1    | github.com::repository_view          | 0.966667 |
| SHADOWSOCKS |   1 | B1    | wikipedia.org::article_view          | 1.000000 |
| SHADOWSOCKS |   1 | B1    | youtube.com::search_results_view     | 0.941667 |
| SHADOWSOCKS |   1 | B1    | youtube.com::video_playback          | 0.937500 |
| SHADOWSOCKS |   1 | B2    | bing.com::search_results_view        | 0.950000 |
| SHADOWSOCKS |   1 | B2    | developer.mozilla.org::document_view | 0.979167 |
| SHADOWSOCKS |   1 | B2    | github.com::repository_view          | 0.995833 |
| SHADOWSOCKS |   1 | B2    | wikipedia.org::article_view          | 0.970833 |
| SHADOWSOCKS |   1 | B2    | youtube.com::search_results_view     | 0.883333 |
| SHADOWSOCKS |   1 | B2    | youtube.com::video_playback          | 0.995833 |
| SHADOWSOCKS |   1 | B3    | bing.com::search_results_view        | 0.950000 |
| SHADOWSOCKS |   1 | B3    | developer.mozilla.org::document_view | 1.000000 |
| SHADOWSOCKS |   1 | B3    | github.com::repository_view          | 1.000000 |
| SHADOWSOCKS |   1 | B3    | wikipedia.org::article_view          | 0.958333 |
| SHADOWSOCKS |   1 | B3    | youtube.com::search_results_view     | 0.887500 |
| SHADOWSOCKS |   1 | B3    | youtube.com::video_playback          | 0.991667 |
| SHADOWSOCKS |   1 | B4    | bing.com::search_results_view        | 0.950000 |
| SHADOWSOCKS |   1 | B4    | developer.mozilla.org::document_view | 1.000000 |
| SHADOWSOCKS |   1 | B4    | github.com::repository_view          | 1.000000 |
| SHADOWSOCKS |   1 | B4    | wikipedia.org::article_view          | 0.962500 |
| SHADOWSOCKS |   1 | B4    | youtube.com::search_results_view     | 0.887500 |
| SHADOWSOCKS |   1 | B4    | youtube.com::video_playback          | 0.979167 |
| SHADOWSOCKS |   1 | B5    | bing.com::search_results_view        | 0.950000 |
| SHADOWSOCKS |   1 | B5    | developer.mozilla.org::document_view | 0.933333 |
| SHADOWSOCKS |   1 | B5    | github.com::repository_view          | 0.995833 |
| SHADOWSOCKS |   1 | B5    | wikipedia.org::article_view          | 0.945833 |
| SHADOWSOCKS |   1 | B5    | youtube.com::search_results_view     | 0.762500 |
| SHADOWSOCKS |   1 | B5    | youtube.com::video_playback          | 0.979167 |
| SHADOWSOCKS |   2 | B0    | bing.com::search_results_view        | 0.945833 |
| SHADOWSOCKS |   2 | B0    | developer.mozilla.org::document_view | 0.995833 |
| SHADOWSOCKS |   2 | B0    | github.com::repository_view          | 0.962500 |
| SHADOWSOCKS |   2 | B0    | wikipedia.org::article_view          | 0.958333 |
| SHADOWSOCKS |   2 | B0    | youtube.com::search_results_view     | 0.904167 |
| SHADOWSOCKS |   2 | B0    | youtube.com::video_playback          | 0.929167 |
| SHADOWSOCKS |   2 | B1    | bing.com::search_results_view        | 0.950000 |
| SHADOWSOCKS |   2 | B1    | developer.mozilla.org::document_view | 0.995833 |
| SHADOWSOCKS |   2 | B1    | github.com::repository_view          | 0.983333 |
| SHADOWSOCKS |   2 | B1    | wikipedia.org::article_view          | 0.995833 |
| SHADOWSOCKS |   2 | B1    | youtube.com::search_results_view     | 0.925000 |
| SHADOWSOCKS |   2 | B1    | youtube.com::video_playback          | 0.937500 |
| SHADOWSOCKS |   2 | B2    | bing.com::search_results_view        | 0.950000 |
| SHADOWSOCKS |   2 | B2    | developer.mozilla.org::document_view | 1.000000 |
| SHADOWSOCKS |   2 | B2    | github.com::repository_view          | 0.991667 |
| SHADOWSOCKS |   2 | B2    | wikipedia.org::article_view          | 0.975000 |
| SHADOWSOCKS |   2 | B2    | youtube.com::search_results_view     | 0.895833 |
| SHADOWSOCKS |   2 | B2    | youtube.com::video_playback          | 0.983333 |
| SHADOWSOCKS |   2 | B3    | bing.com::search_results_view        | 0.950000 |
| SHADOWSOCKS |   2 | B3    | developer.mozilla.org::document_view | 1.000000 |
| SHADOWSOCKS |   2 | B3    | github.com::repository_view          | 1.000000 |
| SHADOWSOCKS |   2 | B3    | wikipedia.org::article_view          | 0.962500 |
| SHADOWSOCKS |   2 | B3    | youtube.com::search_results_view     | 0.900000 |
| SHADOWSOCKS |   2 | B3    | youtube.com::video_playback          | 0.987500 |
| SHADOWSOCKS |   2 | B4    | bing.com::search_results_view        | 0.950000 |
| SHADOWSOCKS |   2 | B4    | developer.mozilla.org::document_view | 1.000000 |
| SHADOWSOCKS |   2 | B4    | github.com::repository_view          | 1.000000 |
| SHADOWSOCKS |   2 | B4    | wikipedia.org::article_view          | 0.975000 |
| SHADOWSOCKS |   2 | B4    | youtube.com::search_results_view     | 0.895833 |
| SHADOWSOCKS |   2 | B4    | youtube.com::video_playback          | 0.983333 |
| SHADOWSOCKS |   2 | B5    | bing.com::search_results_view        | 0.950000 |
| SHADOWSOCKS |   2 | B5    | developer.mozilla.org::document_view | 0.979167 |
| SHADOWSOCKS |   2 | B5    | github.com::repository_view          | 1.000000 |
| SHADOWSOCKS |   2 | B5    | wikipedia.org::article_view          | 0.929167 |
| SHADOWSOCKS |   2 | B5    | youtube.com::search_results_view     | 0.837500 |
| SHADOWSOCKS |   2 | B5    | youtube.com::video_playback          | 0.975000 |
| SHADOWSOCKS |   3 | B0    | bing.com::search_results_view        | 0.945833 |
| SHADOWSOCKS |   3 | B0    | developer.mozilla.org::document_view | 1.000000 |
| SHADOWSOCKS |   3 | B0    | github.com::repository_view          | 1.000000 |
| SHADOWSOCKS |   3 | B0    | wikipedia.org::article_view          | 0.966667 |
| SHADOWSOCKS |   3 | B0    | youtube.com::search_results_view     | 0.908333 |
| SHADOWSOCKS |   3 | B0    | youtube.com::video_playback          | 0.937500 |
| SHADOWSOCKS |   3 | B1    | bing.com::search_results_view        | 0.950000 |
| SHADOWSOCKS |   3 | B1    | developer.mozilla.org::document_view | 1.000000 |
| SHADOWSOCKS |   3 | B1    | github.com::repository_view          | 1.000000 |
| SHADOWSOCKS |   3 | B1    | wikipedia.org::article_view          | 0.983333 |
| SHADOWSOCKS |   3 | B1    | youtube.com::search_results_view     | 0.925000 |
| SHADOWSOCKS |   3 | B1    | youtube.com::video_playback          | 0.945833 |
| SHADOWSOCKS |   3 | B2    | bing.com::search_results_view        | 0.950000 |
| SHADOWSOCKS |   3 | B2    | developer.mozilla.org::document_view | 1.000000 |
| SHADOWSOCKS |   3 | B2    | github.com::repository_view          | 1.000000 |
| SHADOWSOCKS |   3 | B2    | wikipedia.org::article_view          | 0.983333 |
| SHADOWSOCKS |   3 | B2    | youtube.com::search_results_view     | 0.900000 |
| SHADOWSOCKS |   3 | B2    | youtube.com::video_playback          | 0.954167 |
| SHADOWSOCKS |   3 | B3    | bing.com::search_results_view        | 0.950000 |
| SHADOWSOCKS |   3 | B3    | developer.mozilla.org::document_view | 1.000000 |
| SHADOWSOCKS |   3 | B3    | github.com::repository_view          | 1.000000 |
| SHADOWSOCKS |   3 | B3    | wikipedia.org::article_view          | 0.975000 |
| SHADOWSOCKS |   3 | B3    | youtube.com::search_results_view     | 0.900000 |
| SHADOWSOCKS |   3 | B3    | youtube.com::video_playback          | 0.962500 |
| SHADOWSOCKS |   3 | B4    | bing.com::search_results_view        | 0.950000 |
| SHADOWSOCKS |   3 | B4    | developer.mozilla.org::document_view | 1.000000 |
| SHADOWSOCKS |   3 | B4    | github.com::repository_view          | 1.000000 |
| SHADOWSOCKS |   3 | B4    | wikipedia.org::article_view          | 0.983333 |
| SHADOWSOCKS |   3 | B4    | youtube.com::search_results_view     | 0.900000 |
| SHADOWSOCKS |   3 | B4    | youtube.com::video_playback          | 0.958333 |
| SHADOWSOCKS |   3 | B5    | bing.com::search_results_view        | 0.950000 |
| SHADOWSOCKS |   3 | B5    | developer.mozilla.org::document_view | 1.000000 |
| SHADOWSOCKS |   3 | B5    | github.com::repository_view          | 1.000000 |
| SHADOWSOCKS |   3 | B5    | wikipedia.org::article_view          | 0.958333 |
| SHADOWSOCKS |   3 | B5    | youtube.com::search_results_view     | 0.875000 |
| SHADOWSOCKS |   3 | B5    | youtube.com::video_playback          | 0.958333 |
| VLESS       |   1 | B0    | bing.com::search_results_view        | 0.775000 |
| VLESS       |   1 | B0    | developer.mozilla.org::document_view | 0.720833 |
| VLESS       |   1 | B0    | github.com::repository_view          | 0.900000 |
| VLESS       |   1 | B0    | wikipedia.org::article_view          | 0.987500 |
| VLESS       |   1 | B0    | youtube.com::search_results_view     | 0.466667 |
| VLESS       |   1 | B0    | youtube.com::video_playback          | 0.533333 |
| VLESS       |   1 | B1    | bing.com::search_results_view        | 0.737500 |
| VLESS       |   1 | B1    | developer.mozilla.org::document_view | 0.816667 |
| VLESS       |   1 | B1    | github.com::repository_view          | 1.000000 |
| VLESS       |   1 | B1    | wikipedia.org::article_view          | 0.987500 |
| VLESS       |   1 | B1    | youtube.com::search_results_view     | 0.370833 |
| VLESS       |   1 | B1    | youtube.com::video_playback          | 0.854167 |
| VLESS       |   1 | B2    | bing.com::search_results_view        | 0.729167 |
| VLESS       |   1 | B2    | developer.mozilla.org::document_view | 0.733333 |
| VLESS       |   1 | B2    | github.com::repository_view          | 0.991667 |
| VLESS       |   1 | B2    | wikipedia.org::article_view          | 1.000000 |
| VLESS       |   1 | B2    | youtube.com::search_results_view     | 0.420833 |
| VLESS       |   1 | B2    | youtube.com::video_playback          | 0.829167 |
| VLESS       |   1 | B3    | bing.com::search_results_view        | 0.820833 |
| VLESS       |   1 | B3    | developer.mozilla.org::document_view | 0.733333 |
| VLESS       |   1 | B3    | github.com::repository_view          | 0.991667 |
| VLESS       |   1 | B3    | wikipedia.org::article_view          | 0.995833 |
| VLESS       |   1 | B3    | youtube.com::search_results_view     | 0.404167 |
| VLESS       |   1 | B3    | youtube.com::video_playback          | 0.845833 |
| VLESS       |   1 | B4    | bing.com::search_results_view        | 0.862500 |
| VLESS       |   1 | B4    | developer.mozilla.org::document_view | 0.745833 |
| VLESS       |   1 | B4    | github.com::repository_view          | 1.000000 |
| VLESS       |   1 | B4    | wikipedia.org::article_view          | 0.991667 |
| VLESS       |   1 | B4    | youtube.com::search_results_view     | 0.391667 |
| VLESS       |   1 | B4    | youtube.com::video_playback          | 0.895833 |
| VLESS       |   1 | B5    | bing.com::search_results_view        | 0.833333 |
| VLESS       |   1 | B5    | developer.mozilla.org::document_view | 0.795833 |
| VLESS       |   1 | B5    | github.com::repository_view          | 0.983333 |
| VLESS       |   1 | B5    | wikipedia.org::article_view          | 0.995833 |
| VLESS       |   1 | B5    | youtube.com::search_results_view     | 0.283333 |
| VLESS       |   1 | B5    | youtube.com::video_playback          | 0.870833 |
| VLESS       |   2 | B0    | bing.com::search_results_view        | 0.879167 |
| VLESS       |   2 | B0    | developer.mozilla.org::document_view | 0.795833 |
| VLESS       |   2 | B0    | github.com::repository_view          | 0.975000 |
| VLESS       |   2 | B0    | wikipedia.org::article_view          | 0.991667 |
| VLESS       |   2 | B0    | youtube.com::search_results_view     | 0.441667 |
| VLESS       |   2 | B0    | youtube.com::video_playback          | 0.587500 |
| VLESS       |   2 | B1    | bing.com::search_results_view        | 0.858333 |
| VLESS       |   2 | B1    | developer.mozilla.org::document_view | 0.862500 |
| VLESS       |   2 | B1    | github.com::repository_view          | 1.000000 |
| VLESS       |   2 | B1    | wikipedia.org::article_view          | 0.975000 |
| VLESS       |   2 | B1    | youtube.com::search_results_view     | 0.400000 |
| VLESS       |   2 | B1    | youtube.com::video_playback          | 0.862500 |
| VLESS       |   2 | B2    | bing.com::search_results_view        | 0.854167 |
| VLESS       |   2 | B2    | developer.mozilla.org::document_view | 0.779167 |
| VLESS       |   2 | B2    | github.com::repository_view          | 1.000000 |
| VLESS       |   2 | B2    | wikipedia.org::article_view          | 1.000000 |
| VLESS       |   2 | B2    | youtube.com::search_results_view     | 0.395833 |
| VLESS       |   2 | B2    | youtube.com::video_playback          | 0.866667 |
| VLESS       |   2 | B3    | bing.com::search_results_view        | 0.870833 |
| VLESS       |   2 | B3    | developer.mozilla.org::document_view | 0.745833 |
| VLESS       |   2 | B3    | github.com::repository_view          | 1.000000 |
| VLESS       |   2 | B3    | wikipedia.org::article_view          | 0.991667 |
| VLESS       |   2 | B3    | youtube.com::search_results_view     | 0.375000 |
| VLESS       |   2 | B3    | youtube.com::video_playback          | 0.879167 |
| VLESS       |   2 | B4    | bing.com::search_results_view        | 0.887500 |
| VLESS       |   2 | B4    | developer.mozilla.org::document_view | 0.833333 |
| VLESS       |   2 | B4    | github.com::repository_view          | 1.000000 |
| VLESS       |   2 | B4    | wikipedia.org::article_view          | 0.970833 |
| VLESS       |   2 | B4    | youtube.com::search_results_view     | 0.416667 |
| VLESS       |   2 | B4    | youtube.com::video_playback          | 0.875000 |
| VLESS       |   2 | B5    | bing.com::search_results_view        | 0.883333 |
| VLESS       |   2 | B5    | developer.mozilla.org::document_view | 0.883333 |
| VLESS       |   2 | B5    | github.com::repository_view          | 1.000000 |
| VLESS       |   2 | B5    | wikipedia.org::article_view          | 0.991667 |
| VLESS       |   2 | B5    | youtube.com::search_results_view     | 0.308333 |
| VLESS       |   2 | B5    | youtube.com::video_playback          | 0.875000 |
| VLESS       |   3 | B0    | bing.com::search_results_view        | 0.904167 |
| VLESS       |   3 | B0    | developer.mozilla.org::document_view | 0.833333 |
| VLESS       |   3 | B0    | github.com::repository_view          | 0.983333 |
| VLESS       |   3 | B0    | wikipedia.org::article_view          | 0.979167 |
| VLESS       |   3 | B0    | youtube.com::search_results_view     | 0.445833 |
| VLESS       |   3 | B0    | youtube.com::video_playback          | 0.733333 |
| VLESS       |   3 | B1    | bing.com::search_results_view        | 0.895833 |
| VLESS       |   3 | B1    | developer.mozilla.org::document_view | 0.850000 |
| VLESS       |   3 | B1    | github.com::repository_view          | 1.000000 |
| VLESS       |   3 | B1    | wikipedia.org::article_view          | 0.979167 |
| VLESS       |   3 | B1    | youtube.com::search_results_view     | 0.404167 |
| VLESS       |   3 | B1    | youtube.com::video_playback          | 0.879167 |
| VLESS       |   3 | B2    | bing.com::search_results_view        | 0.900000 |
| VLESS       |   3 | B2    | developer.mozilla.org::document_view | 0.808333 |
| VLESS       |   3 | B2    | github.com::repository_view          | 1.000000 |
| VLESS       |   3 | B2    | wikipedia.org::article_view          | 1.000000 |
| VLESS       |   3 | B2    | youtube.com::search_results_view     | 0.395833 |
| VLESS       |   3 | B2    | youtube.com::video_playback          | 0.883333 |
| VLESS       |   3 | B3    | bing.com::search_results_view        | 0.916667 |
| VLESS       |   3 | B3    | developer.mozilla.org::document_view | 0.770833 |
| VLESS       |   3 | B3    | github.com::repository_view          | 1.000000 |
| VLESS       |   3 | B3    | wikipedia.org::article_view          | 0.987500 |
| VLESS       |   3 | B3    | youtube.com::search_results_view     | 0.404167 |
| VLESS       |   3 | B3    | youtube.com::video_playback          | 0.870833 |
| VLESS       |   3 | B4    | bing.com::search_results_view        | 0.933333 |
| VLESS       |   3 | B4    | developer.mozilla.org::document_view | 0.837500 |
| VLESS       |   3 | B4    | github.com::repository_view          | 1.000000 |
| VLESS       |   3 | B4    | wikipedia.org::article_view          | 0.979167 |
| VLESS       |   3 | B4    | youtube.com::search_results_view     | 0.379167 |
| VLESS       |   3 | B4    | youtube.com::video_playback          | 0.854167 |
| VLESS       |   3 | B5    | bing.com::search_results_view        | 0.904167 |
| VLESS       |   3 | B5    | developer.mozilla.org::document_view | 0.891667 |
| VLESS       |   3 | B5    | github.com::repository_view          | 1.000000 |
| VLESS       |   3 | B5    | wikipedia.org::article_view          | 1.000000 |
| VLESS       |   3 | B5    | youtube.com::search_results_view     | 0.329167 |
| VLESS       |   3 | B5    | youtube.com::video_playback          | 0.904167 |

## B4主对照与95%内容bootstrap区间

| protocol    |   k | contrast   | metric   |     delta |       low |      high | positive_favors_B4   |
|:------------|----:|:-----------|:---------|----------:|----------:|----------:|:---------------------|
| SHADOWSOCKS |   1 | B4-B0      | F1       |  0.022173 |  0.004822 |  0.040868 | True                 |
| SHADOWSOCKS |   1 | B4-B0      | BA       |  0.022222 |  0.004861 |  0.040972 | True                 |
| SHADOWSOCKS |   1 | B4-B0      | CE_bits  | -0.054618 | -0.105542 | -0.009175 | False                |
| SHADOWSOCKS |   1 | B4-B0      | Brier    | -0.026465 | -0.046366 | -0.008906 | False                |
| SHADOWSOCKS |   1 | B4-B1      | F1       |  0.007369 | -0.015519 |  0.030201 | True                 |
| SHADOWSOCKS |   1 | B4-B1      | BA       |  0.007639 | -0.015278 |  0.030556 | True                 |
| SHADOWSOCKS |   1 | B4-B1      | CE_bits  | -0.038026 | -0.061655 | -0.013924 | False                |
| SHADOWSOCKS |   1 | B4-B1      | Brier    | -0.021750 | -0.035894 | -0.008183 | False                |
| SHADOWSOCKS |   1 | B4-B2      | F1       |  0.000627 | -0.007605 |  0.008907 | True                 |
| SHADOWSOCKS |   1 | B4-B2      | BA       |  0.000694 | -0.007639 |  0.009028 | True                 |
| SHADOWSOCKS |   1 | B4-B2      | CE_bits  | -0.013777 | -0.038221 |  0.006929 | False                |
| SHADOWSOCKS |   1 | B4-B2      | Brier    | -0.004621 | -0.013150 |  0.003021 | False                |
| SHADOWSOCKS |   1 | B4-B3      | F1       | -0.001380 | -0.006215 |  0.001392 | True                 |
| SHADOWSOCKS |   1 | B4-B3      | BA       | -0.001389 | -0.006250 |  0.001389 | True                 |
| SHADOWSOCKS |   1 | B4-B3      | CE_bits  | -0.006818 | -0.013140 | -0.000632 | False                |
| SHADOWSOCKS |   1 | B4-B3      | Brier    | -0.002136 | -0.005423 |  0.001047 | False                |
| SHADOWSOCKS |   1 | B4-B5      | F1       |  0.035732 |  0.016933 |  0.055639 | True                 |
| SHADOWSOCKS |   1 | B4-B5      | BA       |  0.035417 |  0.016667 |  0.054184 | True                 |
| SHADOWSOCKS |   1 | B4-B5      | CE_bits  | -0.178226 | -0.199141 | -0.157059 | False                |
| SHADOWSOCKS |   1 | B4-B5      | Brier    | -0.081631 | -0.092413 | -0.071231 | False                |
| SHADOWSOCKS |   2 | B4-B0      | F1       |  0.018021 |  0.005574 |  0.031187 | True                 |
| SHADOWSOCKS |   2 | B4-B0      | BA       |  0.018056 |  0.005556 |  0.031250 | True                 |
| SHADOWSOCKS |   2 | B4-B0      | CE_bits  | -0.025525 | -0.051571 | -0.001890 | False                |
| SHADOWSOCKS |   2 | B4-B0      | Brier    | -0.014276 | -0.025561 | -0.003840 | False                |
| SHADOWSOCKS |   2 | B4-B1      | F1       |  0.002640 | -0.011892 |  0.017196 | True                 |
| SHADOWSOCKS |   2 | B4-B1      | BA       |  0.002778 | -0.011806 |  0.017361 | True                 |
| SHADOWSOCKS |   2 | B4-B1      | CE_bits  | -0.000980 | -0.017673 |  0.017713 | False                |
| SHADOWSOCKS |   2 | B4-B1      | Brier    | -0.002835 | -0.010845 |  0.005357 | False                |
| SHADOWSOCKS |   2 | B4-B2      | F1       |  0.001389 |  0.000000 |  0.002790 | True                 |
| SHADOWSOCKS |   2 | B4-B2      | BA       |  0.001389 |  0.000000 |  0.002778 | True                 |
| SHADOWSOCKS |   2 | B4-B2      | CE_bits  | -0.001067 | -0.012744 |  0.009195 | False                |
| SHADOWSOCKS |   2 | B4-B2      | Brier    | -0.000679 | -0.005572 |  0.003572 | False                |
| SHADOWSOCKS |   2 | B4-B3      | F1       |  0.000688 | -0.002799 |  0.004896 | True                 |
| SHADOWSOCKS |   2 | B4-B3      | BA       |  0.000694 | -0.002778 |  0.004861 | True                 |
| SHADOWSOCKS |   2 | B4-B3      | CE_bits  | -0.001550 | -0.006019 |  0.003062 | False                |
| SHADOWSOCKS |   2 | B4-B3      | Brier    | -0.000906 | -0.002966 |  0.001010 | False                |
| SHADOWSOCKS |   2 | B4-B5      | F1       |  0.022260 |  0.007616 |  0.039657 | True                 |
| SHADOWSOCKS |   2 | B4-B5      | BA       |  0.022222 |  0.007639 |  0.039583 | True                 |
| SHADOWSOCKS |   2 | B4-B5      | CE_bits  | -0.142347 | -0.166600 | -0.110890 | False                |
| SHADOWSOCKS |   2 | B4-B5      | Brier    | -0.062832 | -0.074980 | -0.049131 | False                |
| SHADOWSOCKS |   3 | B4-B0      | F1       |  0.005556 | -0.002801 |  0.013259 | True                 |
| SHADOWSOCKS |   3 | B4-B0      | BA       |  0.005556 | -0.002778 |  0.013194 | True                 |
| SHADOWSOCKS |   3 | B4-B0      | CE_bits  | -0.005727 | -0.013938 |  0.001671 | False                |
| SHADOWSOCKS |   3 | B4-B0      | Brier    | -0.004461 | -0.008216 | -0.001091 | False                |
| SHADOWSOCKS |   3 | B4-B1      | F1       | -0.002097 | -0.011246 |  0.004180 | True                 |
| SHADOWSOCKS |   3 | B4-B1      | BA       | -0.002083 | -0.011111 |  0.004167 | True                 |
| SHADOWSOCKS |   3 | B4-B1      | CE_bits  | -0.002311 | -0.015742 |  0.015138 | False                |
| SHADOWSOCKS |   3 | B4-B1      | Brier    | -0.002495 | -0.007281 |  0.002677 | False                |
| SHADOWSOCKS |   3 | B4-B2      | F1       |  0.000692 |  0.000000 |  0.002090 | True                 |
| SHADOWSOCKS |   3 | B4-B2      | BA       |  0.000694 |  0.000000 |  0.002083 | True                 |
| SHADOWSOCKS |   3 | B4-B2      | CE_bits  | -0.000665 | -0.007299 |  0.004785 | False                |
| SHADOWSOCKS |   3 | B4-B2      | Brier    | -0.000318 | -0.002498 |  0.001675 | False                |
| SHADOWSOCKS |   3 | B4-B3      | F1       |  0.000697 | -0.001392 |  0.003498 | True                 |
| SHADOWSOCKS |   3 | B4-B3      | BA       |  0.000694 | -0.001389 |  0.003472 | True                 |
| SHADOWSOCKS |   3 | B4-B3      | CE_bits  | -0.002709 | -0.007107 |  0.002482 | False                |
| SHADOWSOCKS |   3 | B4-B3      | Brier    | -0.001485 | -0.003217 |  0.000300 | False                |
| SHADOWSOCKS |   3 | B4-B5      | F1       |  0.008370 |  0.000000 |  0.018176 | True                 |
| SHADOWSOCKS |   3 | B4-B5      | BA       |  0.008333 |  0.000000 |  0.018056 | True                 |
| SHADOWSOCKS |   3 | B4-B5      | CE_bits  | -0.052922 | -0.064940 | -0.038334 | False                |
| SHADOWSOCKS |   3 | B4-B5      | Brier    | -0.019797 | -0.025836 | -0.013154 | False                |
| VLESS       |   1 | B4-B0      | F1       |  0.079298 |  0.038742 |  0.118631 | True                 |
| VLESS       |   1 | B4-B0      | BA       |  0.084028 |  0.045833 |  0.120156 | True                 |
| VLESS       |   1 | B4-B0      | CE_bits  | -0.587584 | -0.794433 | -0.398741 | False                |
| VLESS       |   1 | B4-B0      | Brier    | -0.128220 | -0.168690 | -0.086514 | False                |
| VLESS       |   1 | B4-B1      | F1       |  0.019328 | -0.002691 |  0.041667 | True                 |
| VLESS       |   1 | B4-B1      | BA       |  0.020139 | -0.000694 |  0.040972 | True                 |
| VLESS       |   1 | B4-B1      | CE_bits  | -0.058864 | -0.126508 | -0.005993 | False                |
| VLESS       |   1 | B4-B1      | Brier    | -0.016853 | -0.039093 |  0.004339 | False                |
| VLESS       |   1 | B4-B2      | F1       |  0.027742 |  0.003263 |  0.055855 | True                 |
| VLESS       |   1 | B4-B2      | BA       |  0.030556 |  0.007639 |  0.056250 | True                 |
| VLESS       |   1 | B4-B2      | CE_bits  | -0.082717 | -0.145426 | -0.034446 | False                |
| VLESS       |   1 | B4-B2      | Brier    | -0.031917 | -0.054900 | -0.013383 | False                |
| VLESS       |   1 | B4-B3      | F1       |  0.013891 | -0.002468 |  0.031432 | True                 |
| VLESS       |   1 | B4-B3      | BA       |  0.015972 |  0.000000 |  0.033333 | True                 |
| VLESS       |   1 | B4-B3      | CE_bits  | -0.027600 | -0.051401 | -0.006953 | False                |
| VLESS       |   1 | B4-B3      | Brier    | -0.012267 | -0.021912 | -0.005193 | False                |
| VLESS       |   1 | B4-B5      | F1       |  0.025367 | -0.007245 |  0.057102 | True                 |
| VLESS       |   1 | B4-B5      | BA       |  0.020833 | -0.009722 |  0.050712 | True                 |
| VLESS       |   1 | B4-B5      | CE_bits  | -0.029524 | -0.107273 |  0.060861 | False                |
| VLESS       |   1 | B4-B5      | Brier    | -0.028048 | -0.053566 | -0.002513 | False                |
| VLESS       |   2 | B4-B0      | F1       |  0.046853 |  0.019541 |  0.078608 | True                 |
| VLESS       |   2 | B4-B0      | BA       |  0.052083 |  0.026389 |  0.079861 | True                 |
| VLESS       |   2 | B4-B0      | CE_bits  | -0.152352 | -0.238626 | -0.073087 | False                |
| VLESS       |   2 | B4-B0      | Brier    | -0.042771 | -0.065491 | -0.021335 | False                |
| VLESS       |   2 | B4-B1      | F1       |  0.003768 | -0.011577 |  0.019911 | True                 |
| VLESS       |   2 | B4-B1      | BA       |  0.004167 | -0.011806 |  0.020851 | True                 |
| VLESS       |   2 | B4-B1      | CE_bits  | -0.010332 | -0.049434 |  0.022329 | False                |
| VLESS       |   2 | B4-B1      | Brier    | -0.002805 | -0.017780 |  0.010460 | False                |
| VLESS       |   2 | B4-B2      | F1       |  0.014451 | -0.000612 |  0.031744 | True                 |
| VLESS       |   2 | B4-B2      | BA       |  0.014583 | -0.000017 |  0.031944 | True                 |
| VLESS       |   2 | B4-B2      | CE_bits  | -0.018267 | -0.053131 |  0.010919 | False                |
| VLESS       |   2 | B4-B2      | Brier    | -0.011800 | -0.025788 | -0.001144 | False                |
| VLESS       |   2 | B4-B3      | F1       |  0.021387 |  0.005252 |  0.042389 | True                 |
| VLESS       |   2 | B4-B3      | BA       |  0.020139 |  0.003472 |  0.040278 | True                 |
| VLESS       |   2 | B4-B3      | CE_bits  | -0.011088 | -0.027817 |  0.007300 | False                |
| VLESS       |   2 | B4-B3      | Brier    | -0.009377 | -0.016595 | -0.003247 | False                |
| VLESS       |   2 | B4-B5      | F1       |  0.012670 | -0.007983 |  0.031670 | True                 |
| VLESS       |   2 | B4-B5      | BA       |  0.006944 | -0.012500 |  0.025694 | True                 |
| VLESS       |   2 | B4-B5      | CE_bits  |  0.006781 | -0.075262 |  0.112498 | False                |
| VLESS       |   2 | B4-B5      | Brier    | -0.015346 | -0.031307 |  0.000932 | False                |
| VLESS       |   3 | B4-B0      | F1       |  0.012044 | -0.009654 |  0.032700 | True                 |
| VLESS       |   3 | B4-B0      | BA       |  0.017361 | -0.000712 |  0.036111 | True                 |
| VLESS       |   3 | B4-B0      | CE_bits  | -0.026981 | -0.047292 | -0.007200 | False                |
| VLESS       |   3 | B4-B0      | Brier    | -0.012376 | -0.021205 | -0.004402 | False                |
| VLESS       |   3 | B4-B1      | F1       | -0.005879 | -0.019127 |  0.008703 | True                 |
| VLESS       |   3 | B4-B1      | BA       | -0.004167 | -0.018056 |  0.011823 | True                 |
| VLESS       |   3 | B4-B1      | CE_bits  | -0.006245 | -0.025275 |  0.009652 | False                |
| VLESS       |   3 | B4-B1      | Brier    | -0.000568 | -0.009754 |  0.007596 | False                |
| VLESS       |   3 | B4-B2      | F1       | -0.001902 | -0.013929 |  0.012691 | True                 |
| VLESS       |   3 | B4-B2      | BA       | -0.000694 | -0.013194 |  0.013889 | True                 |
| VLESS       |   3 | B4-B2      | CE_bits  | -0.007575 | -0.025397 |  0.006018 | False                |
| VLESS       |   3 | B4-B2      | Brier    | -0.003909 | -0.012196 |  0.002261 | False                |
| VLESS       |   3 | B4-B3      | F1       |  0.004360 | -0.011648 |  0.021366 | True                 |
| VLESS       |   3 | B4-B3      | BA       |  0.005556 | -0.008351 |  0.020833 | True                 |
| VLESS       |   3 | B4-B3      | CE_bits  | -0.013605 | -0.023820 | -0.004008 | False                |
| VLESS       |   3 | B4-B3      | Brier    | -0.006658 | -0.011885 | -0.002205 | False                |
| VLESS       |   3 | B4-B5      | F1       | -0.004428 | -0.024602 |  0.014167 | True                 |
| VLESS       |   3 | B4-B5      | BA       | -0.007639 | -0.029167 |  0.012500 | True                 |
| VLESS       |   3 | B4-B5      | CE_bits  |  0.034261 | -0.023823 |  0.107397 | False                |
| VLESS       |   3 | B4-B5      | Brier    |  0.001174 | -0.010482 |  0.013609 | False                |

## 修复/新增错误（平均seed/轮换的访问数）

| protocol    |   k | contrast   |   repaired |   introduced |   changed |
|:------------|----:|:-----------|-----------:|-------------:|----------:|
| SHADOWSOCKS |   1 | B4-B0      |   3.666667 |     1.000000 |  4.666667 |
| SHADOWSOCKS |   1 | B4-B1      |   2.750000 |     1.833333 |  4.916667 |
| SHADOWSOCKS |   1 | B4-B2      |   0.916667 |     0.833333 |  1.750000 |
| SHADOWSOCKS |   1 | B4-B3      |   0.333333 |     0.500000 |  0.833333 |
| SHADOWSOCKS |   1 | B4-B5      |   4.750000 |     0.500000 |  5.250000 |
| SHADOWSOCKS |   2 | B4-B0      |   2.750000 |     0.583333 |  3.333333 |
| SHADOWSOCKS |   2 | B4-B1      |   1.333333 |     1.000000 |  2.583333 |
| SHADOWSOCKS |   2 | B4-B2      |   0.416667 |     0.250000 |  0.666667 |
| SHADOWSOCKS |   2 | B4-B3      |   0.250000 |     0.166667 |  0.416667 |
| SHADOWSOCKS |   2 | B4-B5      |   2.833333 |     0.166667 |  3.000000 |
| SHADOWSOCKS |   3 | B4-B0      |   1.000000 |     0.333333 |  1.333333 |
| SHADOWSOCKS |   3 | B4-B1      |   0.250000 |     0.500000 |  0.750000 |
| SHADOWSOCKS |   3 | B4-B2      |   0.166667 |     0.083333 |  0.250000 |
| SHADOWSOCKS |   3 | B4-B3      |   0.250000 |     0.166667 |  0.416667 |
| SHADOWSOCKS |   3 | B4-B5      |   1.166667 |     0.166667 |  1.500000 |
| VLESS       |   1 | B4-B0      |  17.833333 |     7.750000 | 26.583333 |
| VLESS       |   1 | B4-B1      |   6.833333 |     4.416667 | 12.083333 |
| VLESS       |   1 | B4-B2      |   6.833333 |     3.166667 | 10.750000 |
| VLESS       |   1 | B4-B3      |   4.416667 |     2.500000 |  6.916667 |
| VLESS       |   1 | B4-B5      |   7.000000 |     4.500000 | 12.000000 |
| VLESS       |   2 | B4-B0      |  11.666667 |     5.416667 | 17.500000 |
| VLESS       |   2 | B4-B1      |   3.500000 |     3.000000 |  7.166667 |
| VLESS       |   2 | B4-B2      |   4.166667 |     2.416667 |  7.250000 |
| VLESS       |   2 | B4-B3      |   4.000000 |     1.583333 |  5.833333 |
| VLESS       |   2 | B4-B5      |   4.833333 |     4.000000 |  9.250000 |
| VLESS       |   3 | B4-B0      |   6.833333 |     4.750000 | 11.750000 |
| VLESS       |   3 | B4-B1      |   2.416667 |     2.916667 |  5.583333 |
| VLESS       |   3 | B4-B2      |   2.666667 |     2.750000 |  5.583333 |
| VLESS       |   3 | B4-B3      |   3.083333 |     2.416667 |  5.833333 |
| VLESS       |   3 | B4-B5      |   2.833333 |     3.750000 |  6.750000 |

