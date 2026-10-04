# 多部署统一业务模型与留一部署实验：详细结果表

本文件由 `eval/business_protocol_eval/report_results.py` 从封存预测生成，无模型拟合或选择。所有F1为0–1；先逐seed合并五折OOF，再对seed取均值。主报告见 [formal-results.md](formal-results.md)。

## E1 汇总

| arm | protocol_equal_F1 | worst_protocol_F1 | pooled_F1 |
|---|---|---|---|
| M0 | 0.7159 | 0.6335 | 0.7262 |
| M1 | 0.6190 | 0.2769 | 0.6332 |
| M2 | 0.7248 | 0.6529 | 0.7324 |
| M3 | 0.6556 | 0.5222 | 0.6744 |
| M4 | 0.6516 | 0.5443 | 0.6717 |

最差F1为每seed先取五部署最小值，再平均，不等于先平均seed再取最小值。

### 逐部署三seed均值

| arm | protocol | F1 | CE_bits | Brier | accuracy | BA |
|---|---|---|---|---|---|---|
| M0 | anytls | 0.8251 | 0.9249 | 0.3151 | 0.8306 | 0.8306 |
| M0 | shadowsocks | 0.6343 | 1.2478 | 0.4485 | 0.6694 | 0.6694 |
| M0 | trojan | 0.6547 | 1.2832 | 0.4449 | 0.6556 | 0.6556 |
| M0 | vless | 0.6954 | 1.1265 | 0.3908 | 0.6917 | 0.6917 |
| M0 | vmess | 0.7701 | 0.9563 | 0.3197 | 0.7861 | 0.7861 |
| M1 | anytls | 0.6904 | 1.1716 | 0.3937 | 0.7444 | 0.7444 |
| M1 | shadowsocks | 0.2769 | 1.9835 | 0.7252 | 0.3444 | 0.3444 |
| M1 | trojan | 0.7023 | 1.2552 | 0.4210 | 0.7056 | 0.7056 |
| M1 | vless | 0.7170 | 1.1452 | 0.3998 | 0.7333 | 0.7333 |
| M1 | vmess | 0.7085 | 1.2619 | 0.3992 | 0.7500 | 0.7500 |
| M2 | anytls | 0.8218 | 0.9192 | 0.3155 | 0.8306 | 0.8306 |
| M2 | shadowsocks | 0.6529 | 1.2126 | 0.4356 | 0.6861 | 0.6861 |
| M2 | trojan | 0.6895 | 1.3200 | 0.4545 | 0.6861 | 0.6861 |
| M2 | vless | 0.7067 | 1.1022 | 0.3944 | 0.7028 | 0.7028 |
| M2 | vmess | 0.7530 | 0.9793 | 0.3216 | 0.7778 | 0.7778 |
| M3 | anytls | 0.7737 | 1.1666 | 0.4225 | 0.7806 | 0.7806 |
| M3 | shadowsocks | 0.5222 | 1.3540 | 0.5006 | 0.6111 | 0.6111 |
| M3 | trojan | 0.5946 | 1.3843 | 0.5271 | 0.5917 | 0.5917 |
| M3 | vless | 0.6791 | 1.2950 | 0.4800 | 0.6750 | 0.6750 |
| M3 | vmess | 0.7083 | 1.0793 | 0.4028 | 0.7389 | 0.7389 |
| M4 | anytls | 0.7527 | 1.1978 | 0.4352 | 0.7611 | 0.7611 |
| M4 | shadowsocks | 0.5443 | 1.3699 | 0.5060 | 0.6194 | 0.6194 |
| M4 | trojan | 0.5863 | 1.3992 | 0.5299 | 0.5861 | 0.5861 |
| M4 | vless | 0.6612 | 1.3265 | 0.4886 | 0.6639 | 0.6639 |
| M4 | vmess | 0.7135 | 1.1173 | 0.4163 | 0.7389 | 0.7389 |

### 主对照与次要错配对照

| experiment | contrast | primary | delta | low95 | high95 | adjusted_low | adjusted_high |
|---|---|---|---|---|---|---|---|
| E1 | M2-M0 | True | 0.0088 | -0.0067 | 0.0261 | -0.0097 | 0.0303 |
| E1 | M2-M1 | True | 0.1058 | 0.0748 | 0.1334 | 0.0685 | 0.1399 |
| E1 | M2-M3 | True | 0.0692 | 0.0421 | 0.0979 | 0.0368 | 0.1045 |
| E1 | M2-M4 | False | 0.0732 | 0.0458 | 0.1039 | — | — |

adjusted为本实验三项主比较的Bonferroni分位区间；M2−M4仅提供未校正描述区间。

### 每个seed的完整OOF成绩

| experiment | arm | seed | protocol_equal_F1 | worst_protocol_F1 | worst_protocol | pooled_F1 |
|---|---|---|---|---|---|---|
| E1 | M0 | 20260918 | 0.7081 | 0.6297 | trojan | 0.7184 |
| E1 | M0 | 20260919 | 0.7175 | 0.6337 | shadowsocks | 0.7278 |
| E1 | M0 | 20260920 | 0.7222 | 0.6371 | shadowsocks | 0.7322 |
| E1 | M1 | 20260918 | 0.6160 | 0.2645 | shadowsocks | 0.6298 |
| E1 | M1 | 20260919 | 0.6166 | 0.2719 | shadowsocks | 0.6332 |
| E1 | M1 | 20260920 | 0.6244 | 0.2943 | shadowsocks | 0.6365 |
| E1 | M2 | 20260918 | 0.7142 | 0.6468 | shadowsocks | 0.7229 |
| E1 | M2 | 20260919 | 0.7285 | 0.6637 | shadowsocks | 0.7358 |
| E1 | M2 | 20260920 | 0.7315 | 0.6481 | shadowsocks | 0.7387 |
| E1 | M3 | 20260918 | 0.6617 | 0.5509 | shadowsocks | 0.6793 |
| E1 | M3 | 20260919 | 0.6520 | 0.5234 | shadowsocks | 0.6746 |
| E1 | M3 | 20260920 | 0.6531 | 0.4923 | shadowsocks | 0.6693 |
| E1 | M4 | 20260918 | 0.6421 | 0.5425 | shadowsocks | 0.6646 |
| E1 | M4 | 20260919 | 0.6512 | 0.5651 | shadowsocks | 0.6715 |
| E1 | M4 | 20260920 | 0.6615 | 0.5252 | shadowsocks | 0.6789 |

### 六业务逐类F1（部署等权、seed平均）

| arm | business | F1 | recall |
|---|---|---|---|
| M0 | bing.com::search_results_view | 0.7228 | 0.7433 |
| M0 | developer.mozilla.org::document_view | 0.5879 | 0.6500 |
| M0 | github.com::repository_view | 0.7163 | 0.7233 |
| M0 | wikipedia.org::article_view | 0.5316 | 0.5000 |
| M0 | youtube.com::search_results_view | 0.8441 | 0.8367 |
| M0 | youtube.com::video_playback | 0.8929 | 0.9067 |
| M1 | bing.com::search_results_view | 0.6031 | 0.6333 |
| M1 | developer.mozilla.org::document_view | 0.5240 | 0.6000 |
| M1 | github.com::repository_view | 0.6706 | 0.7067 |
| M1 | wikipedia.org::article_view | 0.2309 | 0.1867 |
| M1 | youtube.com::search_results_view | 0.8568 | 0.8533 |
| M1 | youtube.com::video_playback | 0.8287 | 0.9533 |
| M2 | bing.com::search_results_view | 0.7357 | 0.7467 |
| M2 | developer.mozilla.org::document_view | 0.6391 | 0.7833 |
| M2 | github.com::repository_view | 0.7513 | 0.7700 |
| M2 | wikipedia.org::article_view | 0.4620 | 0.3833 |
| M2 | youtube.com::search_results_view | 0.8610 | 0.8367 |
| M2 | youtube.com::video_playback | 0.8995 | 0.9000 |
| M3 | bing.com::search_results_view | 0.6936 | 0.6800 |
| M3 | developer.mozilla.org::document_view | 0.5559 | 0.6600 |
| M3 | github.com::repository_view | 0.6297 | 0.6833 |
| M3 | wikipedia.org::article_view | 0.3553 | 0.3367 |
| M3 | youtube.com::search_results_view | 0.8208 | 0.8000 |
| M3 | youtube.com::video_playback | 0.8783 | 0.9167 |
| M4 | bing.com::search_results_view | 0.6882 | 0.6800 |
| M4 | developer.mozilla.org::document_view | 0.4946 | 0.5733 |
| M4 | github.com::repository_view | 0.6461 | 0.6800 |
| M4 | wikipedia.org::article_view | 0.3812 | 0.3900 |
| M4 | youtube.com::search_results_view | 0.8238 | 0.8000 |
| M4 | youtube.com::video_playback | 0.8756 | 0.9200 |

### 修复／新增错误（全部seed判断次数之和，不是独立样本数）

| comparison | protocol | repaired | new_error |
|---|---|---|---|
| M2-M0 | anytls | 5 | 5 |
| M2-M0 | shadowsocks | 27 | 21 |
| M2-M0 | trojan | 20 | 9 |
| M2-M0 | vless | 15 | 11 |
| M2-M0 | vmess | 4 | 7 |
| M2-M1 | anytls | 34 | 3 |
| M2-M1 | shadowsocks | 127 | 4 |
| M2-M1 | trojan | 20 | 27 |
| M2-M1 | vless | 21 | 32 |
| M2-M1 | vmess | 22 | 12 |
| M2-M3 | anytls | 28 | 10 |
| M2-M3 | shadowsocks | 35 | 8 |
| M2-M3 | trojan | 51 | 17 |
| M2-M3 | vless | 32 | 22 |
| M2-M3 | vmess | 19 | 5 |
| M2-M4 | anytls | 35 | 10 |
| M2-M4 | shadowsocks | 30 | 6 |
| M2-M4 | trojan | 56 | 20 |
| M2-M4 | vless | 45 | 31 |
| M2-M4 | vmess | 20 | 6 |

## E2 汇总

| arm | protocol_equal_F1 | worst_protocol_F1 | pooled_F1 |
|---|---|---|---|
| M0 | 0.6061 | 0.2432 | 0.6219 |
| M1 | 0.5809 | 0.1543 | 0.5994 |
| M2 | 0.6097 | 0.2549 | 0.6275 |
| M3 | 0.5713 | 0.3449 | 0.5936 |
| M4 | 0.5731 | 0.3635 | 0.5974 |

最差F1为每seed先取五部署最小值，再平均，不等于先平均seed再取最小值。

### 逐部署三seed均值

| arm | protocol | F1 | CE_bits | Brier | accuracy | BA |
|---|---|---|---|---|---|---|
| M0 | anytls | 0.7837 | 0.9885 | 0.3403 | 0.7917 | 0.7917 |
| M0 | shadowsocks | 0.2432 | 4.1826 | 1.1178 | 0.3083 | 0.3083 |
| M0 | trojan | 0.6118 | 1.4624 | 0.5093 | 0.6083 | 0.6083 |
| M0 | vless | 0.6787 | 1.1752 | 0.4175 | 0.6750 | 0.6750 |
| M0 | vmess | 0.7133 | 0.9899 | 0.3378 | 0.7389 | 0.7389 |
| M1 | anytls | 0.6689 | 1.2422 | 0.4195 | 0.7139 | 0.7139 |
| M1 | shadowsocks | 0.1543 | 6.9123 | 1.2031 | 0.2417 | 0.2417 |
| M1 | trojan | 0.6962 | 1.2796 | 0.4301 | 0.6972 | 0.6972 |
| M1 | vless | 0.6878 | 1.1949 | 0.4169 | 0.7056 | 0.7056 |
| M1 | vmess | 0.6972 | 1.2968 | 0.4104 | 0.7417 | 0.7417 |
| M2 | anytls | 0.8001 | 0.9763 | 0.3366 | 0.8111 | 0.8111 |
| M2 | shadowsocks | 0.2549 | 3.1995 | 0.9894 | 0.3278 | 0.3278 |
| M2 | trojan | 0.6171 | 1.4903 | 0.5185 | 0.6139 | 0.6139 |
| M2 | vless | 0.6523 | 1.1756 | 0.4267 | 0.6472 | 0.6472 |
| M2 | vmess | 0.7241 | 1.0056 | 0.3369 | 0.7583 | 0.7583 |
| M3 | anytls | 0.7466 | 1.2186 | 0.4410 | 0.7583 | 0.7583 |
| M3 | shadowsocks | 0.3449 | 1.7949 | 0.6465 | 0.4139 | 0.4139 |
| M3 | trojan | 0.5115 | 1.5569 | 0.5930 | 0.5056 | 0.5056 |
| M3 | vless | 0.5768 | 1.3667 | 0.5144 | 0.5944 | 0.5944 |
| M3 | vmess | 0.6768 | 1.1445 | 0.4270 | 0.7194 | 0.7194 |
| M4 | anytls | 0.7463 | 1.2503 | 0.4532 | 0.7583 | 0.7583 |
| M4 | shadowsocks | 0.3635 | 1.7496 | 0.6318 | 0.4333 | 0.4333 |
| M4 | trojan | 0.5083 | 1.5471 | 0.5862 | 0.4944 | 0.4944 |
| M4 | vless | 0.5822 | 1.3707 | 0.5154 | 0.6056 | 0.6056 |
| M4 | vmess | 0.6654 | 1.1895 | 0.4414 | 0.7111 | 0.7111 |

### 主对照与次要错配对照

| experiment | contrast | primary | delta | low95 | high95 | adjusted_low | adjusted_high |
|---|---|---|---|---|---|---|---|
| E2 | M2-M0 | True | 0.0036 | -0.0096 | 0.0160 | -0.0125 | 0.0185 |
| E2 | M2-M1 | True | 0.0288 | -0.0020 | 0.0567 | -0.0089 | 0.0627 |
| E2 | M2-M3 | True | 0.0384 | 0.0122 | 0.0666 | 0.0063 | 0.0719 |
| E2 | M2-M4 | False | 0.0366 | 0.0066 | 0.0670 | — | — |

adjusted为本实验三项主比较的Bonferroni分位区间；M2−M4仅提供未校正描述区间。

### 每个seed的完整OOF成绩

| experiment | arm | seed | protocol_equal_F1 | worst_protocol_F1 | worst_protocol | pooled_F1 |
|---|---|---|---|---|---|---|
| E2 | M0 | 20260918 | 0.6036 | 0.2366 | shadowsocks | 0.6174 |
| E2 | M0 | 20260919 | 0.5996 | 0.2447 | shadowsocks | 0.6169 |
| E2 | M0 | 20260920 | 0.6153 | 0.2482 | shadowsocks | 0.6313 |
| E2 | M1 | 20260918 | 0.5875 | 0.1553 | shadowsocks | 0.6052 |
| E2 | M1 | 20260919 | 0.5763 | 0.1547 | shadowsocks | 0.5939 |
| E2 | M1 | 20260920 | 0.5788 | 0.1528 | shadowsocks | 0.5991 |
| E2 | M2 | 20260918 | 0.6127 | 0.2699 | shadowsocks | 0.6333 |
| E2 | M2 | 20260919 | 0.5955 | 0.2424 | shadowsocks | 0.6113 |
| E2 | M2 | 20260920 | 0.6209 | 0.2523 | shadowsocks | 0.6379 |
| E2 | M3 | 20260918 | 0.5649 | 0.3577 | shadowsocks | 0.5889 |
| E2 | M3 | 20260919 | 0.5683 | 0.3390 | shadowsocks | 0.5927 |
| E2 | M3 | 20260920 | 0.5807 | 0.3379 | shadowsocks | 0.5993 |
| E2 | M4 | 20260918 | 0.5781 | 0.3684 | shadowsocks | 0.6027 |
| E2 | M4 | 20260919 | 0.5733 | 0.3673 | shadowsocks | 0.5981 |
| E2 | M4 | 20260920 | 0.5679 | 0.3547 | shadowsocks | 0.5916 |

### 六业务逐类F1（部署等权、seed平均）

| arm | business | F1 | recall |
|---|---|---|---|
| M0 | bing.com::search_results_view | 0.5477 | 0.5500 |
| M0 | developer.mozilla.org::document_view | 0.4752 | 0.5367 |
| M0 | github.com::repository_view | 0.6044 | 0.6533 |
| M0 | wikipedia.org::article_view | 0.3862 | 0.3633 |
| M0 | youtube.com::search_results_view | 0.8015 | 0.7667 |
| M0 | youtube.com::video_playback | 0.8219 | 0.8767 |
| M1 | bing.com::search_results_view | 0.5590 | 0.5867 |
| M1 | developer.mozilla.org::document_view | 0.5031 | 0.5567 |
| M1 | github.com::repository_view | 0.6172 | 0.6767 |
| M1 | wikipedia.org::article_view | 0.2186 | 0.1833 |
| M1 | youtube.com::search_results_view | 0.8034 | 0.7800 |
| M1 | youtube.com::video_playback | 0.7839 | 0.9367 |
| M2 | bing.com::search_results_view | 0.5762 | 0.5833 |
| M2 | developer.mozilla.org::document_view | 0.4852 | 0.5800 |
| M2 | github.com::repository_view | 0.6376 | 0.7033 |
| M2 | wikipedia.org::article_view | 0.3310 | 0.3067 |
| M2 | youtube.com::search_results_view | 0.8160 | 0.7667 |
| M2 | youtube.com::video_playback | 0.8123 | 0.8500 |
| M3 | bing.com::search_results_view | 0.5554 | 0.5667 |
| M3 | developer.mozilla.org::document_view | 0.4198 | 0.4467 |
| M3 | github.com::repository_view | 0.5555 | 0.6200 |
| M3 | wikipedia.org::article_view | 0.3049 | 0.3433 |
| M3 | youtube.com::search_results_view | 0.7719 | 0.7367 |
| M3 | youtube.com::video_playback | 0.8203 | 0.8767 |
| M4 | bing.com::search_results_view | 0.5718 | 0.5933 |
| M4 | developer.mozilla.org::document_view | 0.3996 | 0.4167 |
| M4 | github.com::repository_view | 0.5417 | 0.5867 |
| M4 | wikipedia.org::article_view | 0.3125 | 0.3767 |
| M4 | youtube.com::search_results_view | 0.7856 | 0.7467 |
| M4 | youtube.com::video_playback | 0.8275 | 0.8833 |

### 修复／新增错误（全部seed判断次数之和，不是独立样本数）

| comparison | protocol | repaired | new_error |
|---|---|---|---|
| M2-M0 | anytls | 13 | 6 |
| M2-M0 | shadowsocks | 8 | 1 |
| M2-M0 | trojan | 20 | 18 |
| M2-M0 | vless | 7 | 17 |
| M2-M0 | vmess | 15 | 8 |
| M2-M1 | anytls | 43 | 8 |
| M2-M1 | shadowsocks | 31 | 0 |
| M2-M1 | trojan | 24 | 54 |
| M2-M1 | vless | 31 | 52 |
| M2-M1 | vmess | 20 | 14 |
| M2-M3 | anytls | 39 | 20 |
| M2-M3 | shadowsocks | 4 | 35 |
| M2-M3 | trojan | 61 | 22 |
| M2-M3 | vless | 39 | 20 |
| M2-M3 | vmess | 20 | 6 |
| M2-M4 | anytls | 41 | 22 |
| M2-M4 | shadowsocks | 4 | 42 |
| M2-M4 | trojan | 64 | 21 |
| M2-M4 | vless | 40 | 25 |
| M2-M4 | vmess | 25 | 8 |

## I0 独立部署参照

| protocol | F1 | CE_bits | Brier | accuracy |
|---|---|---|---|---|
| anytls | 0.8125 | 1.3882 | 0.3201 | 0.8139 |
| shadowsocks | 0.8197 | 0.9825 | 0.3059 | 0.8222 |
| trojan | 0.6888 | 1.2195 | 0.4196 | 0.6889 |
| vless | 0.7196 | 1.5734 | 0.3905 | 0.7222 |
| vmess | 0.7421 | 1.1857 | 0.3421 | 0.7528 |

| experiment | arm | seed | protocol_equal_F1 | worst_protocol_F1 | worst_protocol | pooled_F1 |
|---|---|---|---|---|---|---|
| I0 | I0 | 20260918 | 0.7514 | 0.6846 | trojan | 0.7556 |
| I0 | I0 | 20260919 | 0.7576 | 0.6724 | trojan | 0.7619 |
| I0 | I0 | 20260920 | 0.7605 | 0.7076 | vless | 0.7637 |

I0需部署身份路由且合计五个模型，不能把其与M0的差直接归因为参数共享。

## 完整逐部署逐业务表

| experiment | arm | protocol | business | F1 | recall |
|---|---|---|---|---|---|
| E1 | M0 | anytls | bing.com::search_results_view | 0.8068 | 0.8000 |
| E1 | M0 | anytls | developer.mozilla.org::document_view | 0.7502 | 0.9000 |
| E1 | M0 | anytls | github.com::repository_view | 0.8854 | 0.9000 |
| E1 | M0 | anytls | wikipedia.org::article_view | 0.6301 | 0.4833 |
| E1 | M0 | anytls | youtube.com::search_results_view | 0.9121 | 0.9500 |
| E1 | M0 | anytls | youtube.com::video_playback | 0.9662 | 0.9500 |
| E1 | M0 | shadowsocks | bing.com::search_results_view | 0.6027 | 0.7333 |
| E1 | M0 | shadowsocks | developer.mozilla.org::document_view | 0.5917 | 0.5500 |
| E1 | M0 | shadowsocks | github.com::repository_view | 0.2345 | 0.1333 |
| E1 | M0 | shadowsocks | wikipedia.org::article_view | 0.6667 | 0.7000 |
| E1 | M0 | shadowsocks | youtube.com::search_results_view | 0.9154 | 0.9000 |
| E1 | M0 | shadowsocks | youtube.com::video_playback | 0.7948 | 1.0000 |
| E1 | M0 | trojan | bing.com::search_results_view | 0.6661 | 0.6833 |
| E1 | M0 | trojan | developer.mozilla.org::document_view | 0.4260 | 0.4000 |
| E1 | M0 | trojan | github.com::repository_view | 0.7385 | 0.8000 |
| E1 | M0 | trojan | wikipedia.org::article_view | 0.5823 | 0.6500 |
| E1 | M0 | trojan | youtube.com::search_results_view | 0.6737 | 0.6000 |
| E1 | M0 | trojan | youtube.com::video_playback | 0.8416 | 0.8000 |
| E1 | M0 | vless | bing.com::search_results_view | 0.7201 | 0.7500 |
| E1 | M0 | vless | developer.mozilla.org::document_view | 0.5266 | 0.5667 |
| E1 | M0 | vless | github.com::repository_view | 0.8098 | 0.8167 |
| E1 | M0 | vless | wikipedia.org::article_view | 0.4275 | 0.4167 |
| E1 | M0 | vless | youtube.com::search_results_view | 0.8102 | 0.8167 |
| E1 | M0 | vless | youtube.com::video_playback | 0.8783 | 0.7833 |
| E1 | M0 | vmess | bing.com::search_results_view | 0.8183 | 0.7500 |
| E1 | M0 | vmess | developer.mozilla.org::document_view | 0.6451 | 0.8333 |
| E1 | M0 | vmess | github.com::repository_view | 0.9133 | 0.9667 |
| E1 | M0 | vmess | wikipedia.org::article_view | 0.3511 | 0.2500 |
| E1 | M0 | vmess | youtube.com::search_results_view | 0.9089 | 0.9167 |
| E1 | M0 | vmess | youtube.com::video_playback | 0.9837 | 1.0000 |
| E1 | M1 | anytls | bing.com::search_results_view | 0.7495 | 0.7500 |
| E1 | M1 | anytls | developer.mozilla.org::document_view | 0.7631 | 0.8833 |
| E1 | M1 | anytls | github.com::repository_view | 0.7484 | 0.9167 |
| E1 | M1 | anytls | wikipedia.org::article_view | 0.0952 | 0.0500 |
| E1 | M1 | anytls | youtube.com::search_results_view | 0.9016 | 0.9167 |
| E1 | M1 | anytls | youtube.com::video_playback | 0.8847 | 0.9500 |
| E1 | M1 | shadowsocks | bing.com::search_results_view | 0.1095 | 0.1833 |
| E1 | M1 | shadowsocks | developer.mozilla.org::document_view | 0.0000 | 0.0000 |
| E1 | M1 | shadowsocks | github.com::repository_view | 0.1793 | 0.1000 |
| E1 | M1 | shadowsocks | wikipedia.org::article_view | 0.0000 | 0.0000 |
| E1 | M1 | shadowsocks | youtube.com::search_results_view | 0.8114 | 0.7833 |
| E1 | M1 | shadowsocks | youtube.com::video_playback | 0.5612 | 1.0000 |
| E1 | M1 | trojan | bing.com::search_results_view | 0.6721 | 0.7000 |
| E1 | M1 | trojan | developer.mozilla.org::document_view | 0.5635 | 0.5500 |
| E1 | M1 | trojan | github.com::repository_view | 0.7681 | 0.8000 |
| E1 | M1 | trojan | wikipedia.org::article_view | 0.5782 | 0.5500 |
| E1 | M1 | trojan | youtube.com::search_results_view | 0.7638 | 0.7000 |
| E1 | M1 | trojan | youtube.com::video_playback | 0.8682 | 0.9333 |
| E1 | M1 | vless | bing.com::search_results_view | 0.7503 | 0.7500 |
| E1 | M1 | vless | developer.mozilla.org::document_view | 0.6577 | 0.7667 |
| E1 | M1 | vless | github.com::repository_view | 0.7719 | 0.8167 |
| E1 | M1 | vless | wikipedia.org::article_view | 0.3347 | 0.2500 |
| E1 | M1 | vless | youtube.com::search_results_view | 0.8892 | 0.9333 |
| E1 | M1 | vless | youtube.com::video_playback | 0.8982 | 0.8833 |
| E1 | M1 | vmess | bing.com::search_results_view | 0.7342 | 0.7833 |
| E1 | M1 | vmess | developer.mozilla.org::document_view | 0.6358 | 0.8000 |
| E1 | M1 | vmess | github.com::repository_view | 0.8854 | 0.9000 |
| E1 | M1 | vmess | wikipedia.org::article_view | 0.1462 | 0.0833 |
| E1 | M1 | vmess | youtube.com::search_results_view | 0.9179 | 0.9333 |
| E1 | M1 | vmess | youtube.com::video_playback | 0.9312 | 1.0000 |
| E1 | M2 | anytls | bing.com::search_results_view | 0.8263 | 0.8333 |
| E1 | M2 | anytls | developer.mozilla.org::document_view | 0.7249 | 0.9000 |
| E1 | M2 | anytls | github.com::repository_view | 0.9047 | 0.9500 |
| E1 | M2 | anytls | wikipedia.org::article_view | 0.5506 | 0.4000 |
| E1 | M2 | anytls | youtube.com::search_results_view | 0.9500 | 0.9500 |
| E1 | M2 | anytls | youtube.com::video_playback | 0.9744 | 0.9500 |
| E1 | M2 | shadowsocks | bing.com::search_results_view | 0.6240 | 0.7333 |
| E1 | M2 | shadowsocks | developer.mozilla.org::document_view | 0.6973 | 0.8833 |
| E1 | M2 | shadowsocks | github.com::repository_view | 0.3778 | 0.2333 |
| E1 | M2 | shadowsocks | wikipedia.org::article_view | 0.4926 | 0.3500 |
| E1 | M2 | shadowsocks | youtube.com::search_results_view | 0.9089 | 0.9167 |
| E1 | M2 | shadowsocks | youtube.com::video_playback | 0.8166 | 1.0000 |
| E1 | M2 | trojan | bing.com::search_results_view | 0.6919 | 0.7000 |
| E1 | M2 | trojan | developer.mozilla.org::document_view | 0.5642 | 0.6167 |
| E1 | M2 | trojan | github.com::repository_view | 0.7322 | 0.8167 |
| E1 | M2 | trojan | wikipedia.org::article_view | 0.5883 | 0.5833 |
| E1 | M2 | trojan | youtube.com::search_results_view | 0.7239 | 0.6333 |
| E1 | M2 | trojan | youtube.com::video_playback | 0.8363 | 0.7667 |
| E1 | M2 | vless | bing.com::search_results_view | 0.7214 | 0.7333 |
| E1 | M2 | vless | developer.mozilla.org::document_view | 0.5792 | 0.6500 |
| E1 | M2 | vless | github.com::repository_view | 0.8125 | 0.8667 |
| E1 | M2 | vless | wikipedia.org::article_view | 0.4449 | 0.4333 |
| E1 | M2 | vless | youtube.com::search_results_view | 0.8041 | 0.7500 |
| E1 | M2 | vless | youtube.com::video_playback | 0.8783 | 0.7833 |
| E1 | M2 | vmess | bing.com::search_results_view | 0.8147 | 0.7333 |
| E1 | M2 | vmess | developer.mozilla.org::document_view | 0.6302 | 0.8667 |
| E1 | M2 | vmess | github.com::repository_view | 0.9294 | 0.9833 |
| E1 | M2 | vmess | wikipedia.org::article_view | 0.2338 | 0.1500 |
| E1 | M2 | vmess | youtube.com::search_results_view | 0.9179 | 0.9333 |
| E1 | M2 | vmess | youtube.com::video_playback | 0.9919 | 1.0000 |
| E1 | M3 | anytls | bing.com::search_results_view | 0.8645 | 0.8500 |
| E1 | M3 | anytls | developer.mozilla.org::document_view | 0.6425 | 0.7000 |
| E1 | M3 | anytls | github.com::repository_view | 0.8090 | 0.8833 |
| E1 | M3 | anytls | wikipedia.org::article_view | 0.5319 | 0.4333 |
| E1 | M3 | anytls | youtube.com::search_results_view | 0.8805 | 0.8833 |
| E1 | M3 | anytls | youtube.com::video_playback | 0.9139 | 0.9333 |
| E1 | M3 | shadowsocks | bing.com::search_results_view | 0.5987 | 0.7833 |
| E1 | M3 | shadowsocks | developer.mozilla.org::document_view | 0.6799 | 0.9333 |
| E1 | M3 | shadowsocks | github.com::repository_view | 0.0635 | 0.0333 |
| E1 | M3 | shadowsocks | wikipedia.org::article_view | 0.1600 | 0.1000 |
| E1 | M3 | shadowsocks | youtube.com::search_results_view | 0.8520 | 0.8167 |
| E1 | M3 | shadowsocks | youtube.com::video_playback | 0.7793 | 1.0000 |
| E1 | M3 | trojan | bing.com::search_results_view | 0.5206 | 0.4333 |
| E1 | M3 | trojan | developer.mozilla.org::document_view | 0.4160 | 0.4333 |
| E1 | M3 | trojan | github.com::repository_view | 0.6342 | 0.7667 |
| E1 | M3 | trojan | wikipedia.org::article_view | 0.4152 | 0.4500 |
| E1 | M3 | trojan | youtube.com::search_results_view | 0.7222 | 0.6500 |
| E1 | M3 | trojan | youtube.com::video_playback | 0.8596 | 0.8167 |
| E1 | M3 | vless | bing.com::search_results_view | 0.7193 | 0.6833 |
| E1 | M3 | vless | developer.mozilla.org::document_view | 0.4163 | 0.3833 |
| E1 | M3 | vless | github.com::repository_view | 0.7579 | 0.7833 |
| E1 | M3 | vless | wikipedia.org::article_view | 0.4739 | 0.5667 |
| E1 | M3 | vless | youtube.com::search_results_view | 0.8062 | 0.8000 |
| E1 | M3 | vless | youtube.com::video_playback | 0.9008 | 0.8333 |
| E1 | M3 | vmess | bing.com::search_results_view | 0.7647 | 0.6500 |
| E1 | M3 | vmess | developer.mozilla.org::document_view | 0.6248 | 0.8500 |
| E1 | M3 | vmess | github.com::repository_view | 0.8837 | 0.9500 |
| E1 | M3 | vmess | wikipedia.org::article_view | 0.1957 | 0.1333 |
| E1 | M3 | vmess | youtube.com::search_results_view | 0.8431 | 0.8500 |
| E1 | M3 | vmess | youtube.com::video_playback | 0.9376 | 1.0000 |
| E1 | M4 | anytls | bing.com::search_results_view | 0.8524 | 0.8667 |
| E1 | M4 | anytls | developer.mozilla.org::document_view | 0.5810 | 0.6000 |
| E1 | M4 | anytls | github.com::repository_view | 0.8036 | 0.8833 |
| E1 | M4 | anytls | wikipedia.org::article_view | 0.5207 | 0.4500 |
| E1 | M4 | anytls | youtube.com::search_results_view | 0.8550 | 0.8333 |
| E1 | M4 | anytls | youtube.com::video_playback | 0.9035 | 0.9333 |
| E1 | M4 | shadowsocks | bing.com::search_results_view | 0.6085 | 0.7500 |
| E1 | M4 | shadowsocks | developer.mozilla.org::document_view | 0.6677 | 0.9333 |
| E1 | M4 | shadowsocks | github.com::repository_view | 0.1739 | 0.1000 |
| E1 | M4 | shadowsocks | wikipedia.org::article_view | 0.1888 | 0.1167 |
| E1 | M4 | shadowsocks | youtube.com::search_results_view | 0.8524 | 0.8167 |
| E1 | M4 | shadowsocks | youtube.com::video_playback | 0.7743 | 1.0000 |
| E1 | M4 | trojan | bing.com::search_results_view | 0.5286 | 0.4500 |
| E1 | M4 | trojan | developer.mozilla.org::document_view | 0.3181 | 0.2833 |
| E1 | M4 | trojan | github.com::repository_view | 0.6331 | 0.7333 |
| E1 | M4 | trojan | wikipedia.org::article_view | 0.4508 | 0.5667 |
| E1 | M4 | trojan | youtube.com::search_results_view | 0.7275 | 0.6667 |
| E1 | M4 | trojan | youtube.com::video_playback | 0.8596 | 0.8167 |
| E1 | M4 | vless | bing.com::search_results_view | 0.7037 | 0.6667 |
| E1 | M4 | vless | developer.mozilla.org::document_view | 0.2821 | 0.2167 |
| E1 | M4 | vless | github.com::repository_view | 0.7511 | 0.7500 |
| E1 | M4 | vless | wikipedia.org::article_view | 0.4902 | 0.6500 |
| E1 | M4 | vless | youtube.com::search_results_view | 0.8296 | 0.8500 |
| E1 | M4 | vless | youtube.com::video_playback | 0.9104 | 0.8500 |
| E1 | M4 | vmess | bing.com::search_results_view | 0.7479 | 0.6667 |
| E1 | M4 | vmess | developer.mozilla.org::document_view | 0.6241 | 0.8333 |
| E1 | M4 | vmess | github.com::repository_view | 0.8685 | 0.9333 |
| E1 | M4 | vmess | wikipedia.org::article_view | 0.2553 | 0.1667 |
| E1 | M4 | vmess | youtube.com::search_results_view | 0.8547 | 0.8333 |
| E1 | M4 | vmess | youtube.com::video_playback | 0.9302 | 1.0000 |
| E2 | M0 | anytls | bing.com::search_results_view | 0.7817 | 0.7167 |
| E2 | M0 | anytls | developer.mozilla.org::document_view | 0.7647 | 0.8667 |
| E2 | M0 | anytls | github.com::repository_view | 0.7738 | 0.8833 |
| E2 | M0 | anytls | wikipedia.org::article_view | 0.5935 | 0.4500 |
| E2 | M0 | anytls | youtube.com::search_results_view | 0.8613 | 0.8833 |
| E2 | M0 | anytls | youtube.com::video_playback | 0.9272 | 0.9500 |
| E2 | M0 | shadowsocks | bing.com::search_results_view | 0.0964 | 0.1833 |
| E2 | M0 | shadowsocks | developer.mozilla.org::document_view | 0.0000 | 0.0000 |
| E2 | M0 | shadowsocks | github.com::repository_view | 0.0000 | 0.0000 |
| E2 | M0 | shadowsocks | wikipedia.org::article_view | 0.0000 | 0.0000 |
| E2 | M0 | shadowsocks | youtube.com::search_results_view | 0.7684 | 0.6667 |
| E2 | M0 | shadowsocks | youtube.com::video_playback | 0.5942 | 1.0000 |
| E2 | M0 | trojan | bing.com::search_results_view | 0.4717 | 0.4833 |
| E2 | M0 | trojan | developer.mozilla.org::document_view | 0.5169 | 0.5167 |
| E2 | M0 | trojan | github.com::repository_view | 0.6763 | 0.8000 |
| E2 | M0 | trojan | wikipedia.org::article_view | 0.5711 | 0.6167 |
| E2 | M0 | trojan | youtube.com::search_results_view | 0.6856 | 0.5833 |
| E2 | M0 | trojan | youtube.com::video_playback | 0.7495 | 0.6500 |
| E2 | M0 | vless | bing.com::search_results_view | 0.6995 | 0.7000 |
| E2 | M0 | vless | developer.mozilla.org::document_view | 0.4355 | 0.4000 |
| E2 | M0 | vless | github.com::repository_view | 0.7687 | 0.8000 |
| E2 | M0 | vless | wikipedia.org::article_view | 0.5068 | 0.5833 |
| E2 | M0 | vless | youtube.com::search_results_view | 0.7832 | 0.7833 |
| E2 | M0 | vless | youtube.com::video_playback | 0.8783 | 0.7833 |
| E2 | M0 | vmess | bing.com::search_results_view | 0.6895 | 0.6667 |
| E2 | M0 | vmess | developer.mozilla.org::document_view | 0.6586 | 0.9000 |
| E2 | M0 | vmess | github.com::repository_view | 0.8033 | 0.7833 |
| E2 | M0 | vmess | wikipedia.org::article_view | 0.2595 | 0.1667 |
| E2 | M0 | vmess | youtube.com::search_results_view | 0.9089 | 0.9167 |
| E2 | M0 | vmess | youtube.com::video_playback | 0.9601 | 1.0000 |
| E2 | M1 | anytls | bing.com::search_results_view | 0.7004 | 0.7167 |
| E2 | M1 | anytls | developer.mozilla.org::document_view | 0.6856 | 0.7167 |
| E2 | M1 | anytls | github.com::repository_view | 0.7503 | 0.9500 |
| E2 | M1 | anytls | wikipedia.org::article_view | 0.1462 | 0.0833 |
| E2 | M1 | anytls | youtube.com::search_results_view | 0.8735 | 0.8667 |
| E2 | M1 | anytls | youtube.com::video_playback | 0.8572 | 0.9500 |
| E2 | M1 | shadowsocks | bing.com::search_results_view | 0.0000 | 0.0000 |
| E2 | M1 | shadowsocks | developer.mozilla.org::document_view | 0.0000 | 0.0000 |
| E2 | M1 | shadowsocks | github.com::repository_view | 0.0000 | 0.0000 |
| E2 | M1 | shadowsocks | wikipedia.org::article_view | 0.0000 | 0.0000 |
| E2 | M1 | shadowsocks | youtube.com::search_results_view | 0.5806 | 0.4500 |
| E2 | M1 | shadowsocks | youtube.com::video_playback | 0.3449 | 1.0000 |
| E2 | M1 | trojan | bing.com::search_results_view | 0.6250 | 0.6667 |
| E2 | M1 | trojan | developer.mozilla.org::document_view | 0.5520 | 0.5167 |
| E2 | M1 | trojan | github.com::repository_view | 0.7481 | 0.8167 |
| E2 | M1 | trojan | wikipedia.org::article_view | 0.5933 | 0.5833 |
| E2 | M1 | trojan | youtube.com::search_results_view | 0.7897 | 0.7167 |
| E2 | M1 | trojan | youtube.com::video_playback | 0.8692 | 0.8833 |
| E2 | M1 | vless | bing.com::search_results_view | 0.7228 | 0.7167 |
| E2 | M1 | vless | developer.mozilla.org::document_view | 0.6372 | 0.7333 |
| E2 | M1 | vless | github.com::repository_view | 0.7512 | 0.8000 |
| E2 | M1 | vless | wikipedia.org::article_view | 0.2650 | 0.2000 |
| E2 | M1 | vless | youtube.com::search_results_view | 0.8463 | 0.9167 |
| E2 | M1 | vless | youtube.com::video_playback | 0.9042 | 0.8667 |
| E2 | M1 | vmess | bing.com::search_results_view | 0.7470 | 0.8333 |
| E2 | M1 | vmess | developer.mozilla.org::document_view | 0.6405 | 0.8167 |
| E2 | M1 | vmess | github.com::repository_view | 0.8365 | 0.8167 |
| E2 | M1 | vmess | wikipedia.org::article_view | 0.0883 | 0.0500 |
| E2 | M1 | vmess | youtube.com::search_results_view | 0.9268 | 0.9500 |
| E2 | M1 | vmess | youtube.com::video_playback | 0.9439 | 0.9833 |
| E2 | M2 | anytls | bing.com::search_results_view | 0.8623 | 0.8333 |
| E2 | M2 | anytls | developer.mozilla.org::document_view | 0.7804 | 0.9167 |
| E2 | M2 | anytls | github.com::repository_view | 0.7959 | 0.9333 |
| E2 | M2 | anytls | wikipedia.org::article_view | 0.5345 | 0.3833 |
| E2 | M2 | anytls | youtube.com::search_results_view | 0.8932 | 0.8500 |
| E2 | M2 | anytls | youtube.com::video_playback | 0.9346 | 0.9500 |
| E2 | M2 | shadowsocks | bing.com::search_results_view | 0.1482 | 0.2833 |
| E2 | M2 | shadowsocks | developer.mozilla.org::document_view | 0.0278 | 0.0167 |
| E2 | M2 | shadowsocks | github.com::repository_view | 0.0000 | 0.0000 |
| E2 | M2 | shadowsocks | wikipedia.org::article_view | 0.0000 | 0.0000 |
| E2 | M2 | shadowsocks | youtube.com::search_results_view | 0.7468 | 0.6667 |
| E2 | M2 | shadowsocks | youtube.com::video_playback | 0.6064 | 1.0000 |
| E2 | M2 | trojan | bing.com::search_results_view | 0.4596 | 0.4667 |
| E2 | M2 | trojan | developer.mozilla.org::document_view | 0.5936 | 0.7167 |
| E2 | M2 | trojan | github.com::repository_view | 0.6934 | 0.8000 |
| E2 | M2 | trojan | wikipedia.org::article_view | 0.4865 | 0.4500 |
| E2 | M2 | trojan | youtube.com::search_results_view | 0.7433 | 0.6500 |
| E2 | M2 | trojan | youtube.com::video_playback | 0.7265 | 0.6000 |
| E2 | M2 | vless | bing.com::search_results_view | 0.6443 | 0.6500 |
| E2 | M2 | vless | developer.mozilla.org::document_view | 0.3890 | 0.3500 |
| E2 | M2 | vless | github.com::repository_view | 0.7777 | 0.8167 |
| E2 | M2 | vless | wikipedia.org::article_view | 0.4972 | 0.6167 |
| E2 | M2 | vless | youtube.com::search_results_view | 0.7786 | 0.7333 |
| E2 | M2 | vless | youtube.com::video_playback | 0.8269 | 0.7167 |
| E2 | M2 | vmess | bing.com::search_results_view | 0.7665 | 0.6833 |
| E2 | M2 | vmess | developer.mozilla.org::document_view | 0.6355 | 0.9000 |
| E2 | M2 | vmess | github.com::repository_view | 0.9210 | 0.9667 |
| E2 | M2 | vmess | wikipedia.org::article_view | 0.1367 | 0.0833 |
| E2 | M2 | vmess | youtube.com::search_results_view | 0.9179 | 0.9333 |
| E2 | M2 | vmess | youtube.com::video_playback | 0.9671 | 0.9833 |
| E2 | M3 | anytls | bing.com::search_results_view | 0.9093 | 0.9167 |
| E2 | M3 | anytls | developer.mozilla.org::document_view | 0.5476 | 0.5000 |
| E2 | M3 | anytls | github.com::repository_view | 0.7852 | 0.8833 |
| E2 | M3 | anytls | wikipedia.org::article_view | 0.5373 | 0.5000 |
| E2 | M3 | anytls | youtube.com::search_results_view | 0.8492 | 0.8000 |
| E2 | M3 | anytls | youtube.com::video_playback | 0.8511 | 0.9500 |
| E2 | M3 | shadowsocks | bing.com::search_results_view | 0.2883 | 0.5500 |
| E2 | M3 | shadowsocks | developer.mozilla.org::document_view | 0.2779 | 0.2000 |
| E2 | M3 | shadowsocks | github.com::repository_view | 0.0000 | 0.0000 |
| E2 | M3 | shadowsocks | wikipedia.org::article_view | 0.0303 | 0.0167 |
| E2 | M3 | shadowsocks | youtube.com::search_results_view | 0.7743 | 0.7167 |
| E2 | M3 | shadowsocks | youtube.com::video_playback | 0.6984 | 1.0000 |
| E2 | M3 | trojan | bing.com::search_results_view | 0.3483 | 0.3000 |
| E2 | M3 | trojan | developer.mozilla.org::document_view | 0.4809 | 0.5333 |
| E2 | M3 | trojan | github.com::repository_view | 0.4918 | 0.6000 |
| E2 | M3 | trojan | wikipedia.org::article_view | 0.3445 | 0.3833 |
| E2 | M3 | trojan | youtube.com::search_results_view | 0.6354 | 0.5500 |
| E2 | M3 | trojan | youtube.com::video_playback | 0.7684 | 0.6667 |
| E2 | M3 | vless | bing.com::search_results_view | 0.5068 | 0.4500 |
| E2 | M3 | vless | developer.mozilla.org::document_view | 0.1692 | 0.1167 |
| E2 | M3 | vless | github.com::repository_view | 0.6369 | 0.7167 |
| E2 | M3 | vless | wikipedia.org::article_view | 0.5257 | 0.7667 |
| E2 | M3 | vless | youtube.com::search_results_view | 0.7548 | 0.7500 |
| E2 | M3 | vless | youtube.com::video_playback | 0.8677 | 0.7667 |
| E2 | M3 | vmess | bing.com::search_results_view | 0.7245 | 0.6167 |
| E2 | M3 | vmess | developer.mozilla.org::document_view | 0.6234 | 0.8833 |
| E2 | M3 | vmess | github.com::repository_view | 0.8637 | 0.9000 |
| E2 | M3 | vmess | wikipedia.org::article_view | 0.0870 | 0.0500 |
| E2 | M3 | vmess | youtube.com::search_results_view | 0.8459 | 0.8667 |
| E2 | M3 | vmess | youtube.com::video_playback | 0.9161 | 1.0000 |
| E2 | M4 | anytls | bing.com::search_results_view | 0.9089 | 0.9167 |
| E2 | M4 | anytls | developer.mozilla.org::document_view | 0.5138 | 0.4500 |
| E2 | M4 | anytls | github.com::repository_view | 0.7909 | 0.8833 |
| E2 | M4 | anytls | wikipedia.org::article_view | 0.5831 | 0.5667 |
| E2 | M4 | anytls | youtube.com::search_results_view | 0.8173 | 0.7833 |
| E2 | M4 | anytls | youtube.com::video_playback | 0.8639 | 0.9500 |
| E2 | M4 | shadowsocks | bing.com::search_results_view | 0.3015 | 0.5500 |
| E2 | M4 | shadowsocks | developer.mozilla.org::document_view | 0.3363 | 0.2667 |
| E2 | M4 | shadowsocks | github.com::repository_view | 0.0000 | 0.0000 |
| E2 | M4 | shadowsocks | wikipedia.org::article_view | 0.0303 | 0.0167 |
| E2 | M4 | shadowsocks | youtube.com::search_results_view | 0.8069 | 0.7667 |
| E2 | M4 | shadowsocks | youtube.com::video_playback | 0.7059 | 1.0000 |
| E2 | M4 | trojan | bing.com::search_results_view | 0.4139 | 0.3667 |
| E2 | M4 | trojan | developer.mozilla.org::document_view | 0.4256 | 0.4333 |
| E2 | M4 | trojan | github.com::repository_view | 0.4290 | 0.4833 |
| E2 | M4 | trojan | wikipedia.org::article_view | 0.3478 | 0.4333 |
| E2 | M4 | trojan | youtube.com::search_results_view | 0.6465 | 0.5667 |
| E2 | M4 | trojan | youtube.com::video_playback | 0.7869 | 0.6833 |
| E2 | M4 | vless | bing.com::search_results_view | 0.5185 | 0.4833 |
| E2 | M4 | vless | developer.mozilla.org::document_view | 0.0992 | 0.0667 |
| E2 | M4 | vless | github.com::repository_view | 0.6510 | 0.7000 |
| E2 | M4 | vless | wikipedia.org::article_view | 0.5457 | 0.8333 |
| E2 | M4 | vless | youtube.com::search_results_view | 0.8003 | 0.7667 |
| E2 | M4 | vless | youtube.com::video_playback | 0.8783 | 0.7833 |
| E2 | M4 | vmess | bing.com::search_results_view | 0.7161 | 0.6500 |
| E2 | M4 | vmess | developer.mozilla.org::document_view | 0.6229 | 0.8667 |
| E2 | M4 | vmess | github.com::repository_view | 0.8378 | 0.8667 |
| E2 | M4 | vmess | wikipedia.org::article_view | 0.0556 | 0.0333 |
| E2 | M4 | vmess | youtube.com::search_results_view | 0.8573 | 0.8500 |
| E2 | M4 | vmess | youtube.com::video_playback | 0.9027 | 1.0000 |
| I0 | I0 | anytls | bing.com::search_results_view | 0.8095 | 0.8500 |
| I0 | I0 | anytls | developer.mozilla.org::document_view | 0.7049 | 0.8167 |
| I0 | I0 | anytls | github.com::repository_view | 0.8645 | 0.8500 |
| I0 | I0 | anytls | wikipedia.org::article_view | 0.6399 | 0.5333 |
| I0 | I0 | anytls | youtube.com::search_results_view | 0.9136 | 0.8833 |
| I0 | I0 | anytls | youtube.com::video_playback | 0.9423 | 0.9500 |
| I0 | I0 | shadowsocks | bing.com::search_results_view | 0.8871 | 0.8500 |
| I0 | I0 | shadowsocks | developer.mozilla.org::document_view | 0.7245 | 0.8333 |
| I0 | I0 | shadowsocks | github.com::repository_view | 0.8928 | 0.8333 |
| I0 | I0 | shadowsocks | wikipedia.org::article_view | 0.5654 | 0.5000 |
| I0 | I0 | shadowsocks | youtube.com::search_results_view | 0.9321 | 0.9167 |
| I0 | I0 | shadowsocks | youtube.com::video_playback | 0.9161 | 1.0000 |
| I0 | I0 | trojan | bing.com::search_results_view | 0.6842 | 0.6500 |
| I0 | I0 | trojan | developer.mozilla.org::document_view | 0.5059 | 0.5000 |
| I0 | I0 | trojan | github.com::repository_view | 0.8003 | 0.8000 |
| I0 | I0 | trojan | wikipedia.org::article_view | 0.6094 | 0.6500 |
| I0 | I0 | trojan | youtube.com::search_results_view | 0.6832 | 0.6833 |
| I0 | I0 | trojan | youtube.com::video_playback | 0.8500 | 0.8500 |
| I0 | I0 | vless | bing.com::search_results_view | 0.7309 | 0.7000 |
| I0 | I0 | vless | developer.mozilla.org::document_view | 0.5987 | 0.7000 |
| I0 | I0 | vless | github.com::repository_view | 0.8040 | 0.7833 |
| I0 | I0 | vless | wikipedia.org::article_view | 0.4152 | 0.3667 |
| I0 | I0 | vless | youtube.com::search_results_view | 0.8833 | 0.8833 |
| I0 | I0 | vless | youtube.com::video_playback | 0.8854 | 0.9000 |
| I0 | I0 | vmess | bing.com::search_results_view | 0.7467 | 0.7833 |
| I0 | I0 | vmess | developer.mozilla.org::document_view | 0.4028 | 0.3000 |
| I0 | I0 | vmess | github.com::repository_view | 0.9179 | 0.9333 |
| I0 | I0 | vmess | wikipedia.org::article_view | 0.6352 | 0.7833 |
| I0 | I0 | vmess | youtube.com::search_results_view | 0.7998 | 0.7667 |
| I0 | I0 | vmess | youtube.com::video_playback | 0.9500 | 0.9500 |

## 每内容每seed的错误转移

| seed | protocol | content_id | y | repaired | new_error | experiment | comparison | business |
|---|---|---|---|---|---|---|---|---|
| 20260918 | anytls | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 0 | E1 | M2-M0 | developer.mozilla.org::document_view |
| 20260918 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 0 | 0 | E1 | M2-M0 | developer.mozilla.org::document_view |
| 20260918 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 0 | E1 | M2-M0 | developer.mozilla.org::document_view |
| 20260918 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 0 | 0 | E1 | M2-M0 | developer.mozilla.org::document_view |
| 20260918 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 0 | 0 | E1 | M2-M0 | developer.mozilla.org::document_view |
| 20260918 | anytls | https://en.wikipedia.org/wiki/Computer_network | 3 | 0 | 1 | E1 | M2-M0 | wikipedia.org::article_view |
| 20260918 | anytls | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 0 | E1 | M2-M0 | wikipedia.org::article_view |
| 20260918 | anytls | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 0 | 0 | E1 | M2-M0 | wikipedia.org::article_view |
| 20260918 | anytls | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 0 | E1 | M2-M0 | wikipedia.org::article_view |
| 20260918 | anytls | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E1 | M2-M0 | wikipedia.org::article_view |
| 20260918 | anytls | https://github.com/RakuLomis/TrafficTracer | 2 | 1 | 0 | E1 | M2-M0 | github.com::repository_view |
| 20260918 | anytls | https://github.com/numpy/numpy | 2 | 0 | 0 | E1 | M2-M0 | github.com::repository_view |
| 20260918 | anytls | https://github.com/pallets/flask | 2 | 1 | 0 | E1 | M2-M0 | github.com::repository_view |
| 20260918 | anytls | https://github.com/python/cpython | 2 | 0 | 0 | E1 | M2-M0 | github.com::repository_view |
| 20260918 | anytls | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E1 | M2-M0 | github.com::repository_view |
| 20260918 | anytls | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 0 | E1 | M2-M0 | bing.com::search_results_view |
| 20260918 | anytls | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 0 | E1 | M2-M0 | bing.com::search_results_view |
| 20260918 | anytls | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E1 | M2-M0 | bing.com::search_results_view |
| 20260918 | anytls | https://www.bing.com/search?q=solar+system+facts | 0 | 0 | 0 | E1 | M2-M0 | bing.com::search_results_view |
| 20260918 | anytls | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 0 | E1 | M2-M0 | bing.com::search_results_view |
| 20260918 | anytls | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E1 | M2-M0 | youtube.com::search_results_view |
| 20260918 | anytls | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 0 | E1 | M2-M0 | youtube.com::search_results_view |
| 20260918 | anytls | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E1 | M2-M0 | youtube.com::search_results_view |
| 20260918 | anytls | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 0 | E1 | M2-M0 | youtube.com::search_results_view |
| 20260918 | anytls | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E1 | M2-M0 | youtube.com::search_results_view |
| 20260918 | anytls | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E1 | M2-M0 | youtube.com::video_playback |
| 20260918 | anytls | youtube_video:aircAruvnKk | 5 | 0 | 0 | E1 | M2-M0 | youtube.com::video_playback |
| 20260918 | anytls | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E1 | M2-M0 | youtube.com::video_playback |
| 20260918 | anytls | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E1 | M2-M0 | youtube.com::video_playback |
| 20260918 | anytls | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E1 | M2-M0 | youtube.com::video_playback |
| 20260918 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 1 | 0 | E1 | M2-M0 | developer.mozilla.org::document_view |
| 20260918 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 2 | 0 | E1 | M2-M0 | developer.mozilla.org::document_view |
| 20260918 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 3 | 0 | E1 | M2-M0 | developer.mozilla.org::document_view |
| 20260918 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 2 | 0 | E1 | M2-M0 | developer.mozilla.org::document_view |
| 20260918 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 1 | 0 | E1 | M2-M0 | developer.mozilla.org::document_view |
| 20260918 | shadowsocks | https://en.wikipedia.org/wiki/Computer_network | 3 | 0 | 1 | E1 | M2-M0 | wikipedia.org::article_view |
| 20260918 | shadowsocks | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 2 | E1 | M2-M0 | wikipedia.org::article_view |
| 20260918 | shadowsocks | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 0 | 0 | E1 | M2-M0 | wikipedia.org::article_view |
| 20260918 | shadowsocks | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 3 | E1 | M2-M0 | wikipedia.org::article_view |
| 20260918 | shadowsocks | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 2 | E1 | M2-M0 | wikipedia.org::article_view |
| 20260918 | shadowsocks | https://github.com/RakuLomis/TrafficTracer | 2 | 0 | 0 | E1 | M2-M0 | github.com::repository_view |
| 20260918 | shadowsocks | https://github.com/numpy/numpy | 2 | 0 | 0 | E1 | M2-M0 | github.com::repository_view |
| 20260918 | shadowsocks | https://github.com/pallets/flask | 2 | 1 | 0 | E1 | M2-M0 | github.com::repository_view |
| 20260918 | shadowsocks | https://github.com/python/cpython | 2 | 0 | 0 | E1 | M2-M0 | github.com::repository_view |
| 20260918 | shadowsocks | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E1 | M2-M0 | github.com::repository_view |
| 20260918 | shadowsocks | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 0 | E1 | M2-M0 | bing.com::search_results_view |
| 20260918 | shadowsocks | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 0 | E1 | M2-M0 | bing.com::search_results_view |
| 20260918 | shadowsocks | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E1 | M2-M0 | bing.com::search_results_view |
| 20260918 | shadowsocks | https://www.bing.com/search?q=solar+system+facts | 0 | 0 | 0 | E1 | M2-M0 | bing.com::search_results_view |
| 20260918 | shadowsocks | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 0 | E1 | M2-M0 | bing.com::search_results_view |
| 20260918 | shadowsocks | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E1 | M2-M0 | youtube.com::search_results_view |
| 20260918 | shadowsocks | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 0 | E1 | M2-M0 | youtube.com::search_results_view |
| 20260918 | shadowsocks | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E1 | M2-M0 | youtube.com::search_results_view |
| 20260918 | shadowsocks | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 0 | E1 | M2-M0 | youtube.com::search_results_view |
| 20260918 | shadowsocks | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E1 | M2-M0 | youtube.com::search_results_view |
| 20260918 | shadowsocks | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E1 | M2-M0 | youtube.com::video_playback |
| 20260918 | shadowsocks | youtube_video:aircAruvnKk | 5 | 0 | 0 | E1 | M2-M0 | youtube.com::video_playback |
| 20260918 | shadowsocks | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E1 | M2-M0 | youtube.com::video_playback |
| 20260918 | shadowsocks | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E1 | M2-M0 | youtube.com::video_playback |
| 20260918 | shadowsocks | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E1 | M2-M0 | youtube.com::video_playback |
| 20260918 | trojan | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 0 | E1 | M2-M0 | developer.mozilla.org::document_view |
| 20260918 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 0 | 0 | E1 | M2-M0 | developer.mozilla.org::document_view |
| 20260918 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 2 | 0 | E1 | M2-M0 | developer.mozilla.org::document_view |
| 20260918 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 2 | 0 | E1 | M2-M0 | developer.mozilla.org::document_view |
| 20260918 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 1 | 0 | E1 | M2-M0 | developer.mozilla.org::document_view |
| 20260918 | trojan | https://en.wikipedia.org/wiki/Computer_network | 3 | 0 | 0 | E1 | M2-M0 | wikipedia.org::article_view |
| 20260918 | trojan | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 1 | E1 | M2-M0 | wikipedia.org::article_view |
| 20260918 | trojan | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 0 | 0 | E1 | M2-M0 | wikipedia.org::article_view |
| 20260918 | trojan | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 0 | E1 | M2-M0 | wikipedia.org::article_view |
| 20260918 | trojan | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E1 | M2-M0 | wikipedia.org::article_view |
| 20260918 | trojan | https://github.com/RakuLomis/TrafficTracer | 2 | 0 | 0 | E1 | M2-M0 | github.com::repository_view |
| 20260918 | trojan | https://github.com/numpy/numpy | 2 | 0 | 0 | E1 | M2-M0 | github.com::repository_view |
| 20260918 | trojan | https://github.com/pallets/flask | 2 | 1 | 0 | E1 | M2-M0 | github.com::repository_view |
| 20260918 | trojan | https://github.com/python/cpython | 2 | 0 | 0 | E1 | M2-M0 | github.com::repository_view |
| 20260918 | trojan | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E1 | M2-M0 | github.com::repository_view |
| 20260918 | trojan | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 1 | E1 | M2-M0 | bing.com::search_results_view |
| 20260918 | trojan | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 1 | E1 | M2-M0 | bing.com::search_results_view |
| 20260918 | trojan | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E1 | M2-M0 | bing.com::search_results_view |
| 20260918 | trojan | https://www.bing.com/search?q=solar+system+facts | 0 | 1 | 0 | E1 | M2-M0 | bing.com::search_results_view |
| 20260918 | trojan | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 0 | E1 | M2-M0 | bing.com::search_results_view |
| 20260918 | trojan | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E1 | M2-M0 | youtube.com::search_results_view |
| 20260918 | trojan | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 1 | 0 | E1 | M2-M0 | youtube.com::search_results_view |
| 20260918 | trojan | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E1 | M2-M0 | youtube.com::search_results_view |
| 20260918 | trojan | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 0 | E1 | M2-M0 | youtube.com::search_results_view |
| 20260918 | trojan | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E1 | M2-M0 | youtube.com::search_results_view |
| 20260918 | trojan | youtube_video:R6MlUcmOul8 | 5 | 0 | 1 | E1 | M2-M0 | youtube.com::video_playback |
| 20260918 | trojan | youtube_video:aircAruvnKk | 5 | 0 | 0 | E1 | M2-M0 | youtube.com::video_playback |
| 20260918 | trojan | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E1 | M2-M0 | youtube.com::video_playback |
| 20260918 | trojan | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E1 | M2-M0 | youtube.com::video_playback |
| 20260918 | trojan | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E1 | M2-M0 | youtube.com::video_playback |
| 20260918 | vless | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 0 | E1 | M2-M0 | developer.mozilla.org::document_view |
| 20260918 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 0 | 0 | E1 | M2-M0 | developer.mozilla.org::document_view |
| 20260918 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 1 | E1 | M2-M0 | developer.mozilla.org::document_view |
| 20260918 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 1 | 0 | E1 | M2-M0 | developer.mozilla.org::document_view |
| 20260918 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 0 | 0 | E1 | M2-M0 | developer.mozilla.org::document_view |
| 20260918 | vless | https://en.wikipedia.org/wiki/Computer_network | 3 | 1 | 1 | E1 | M2-M0 | wikipedia.org::article_view |
| 20260918 | vless | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 0 | E1 | M2-M0 | wikipedia.org::article_view |
| 20260918 | vless | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 0 | 0 | E1 | M2-M0 | wikipedia.org::article_view |
| 20260918 | vless | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 0 | E1 | M2-M0 | wikipedia.org::article_view |
| 20260918 | vless | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E1 | M2-M0 | wikipedia.org::article_view |
| 20260918 | vless | https://github.com/RakuLomis/TrafficTracer | 2 | 1 | 0 | E1 | M2-M0 | github.com::repository_view |
| 20260918 | vless | https://github.com/numpy/numpy | 2 | 0 | 0 | E1 | M2-M0 | github.com::repository_view |
| 20260918 | vless | https://github.com/pallets/flask | 2 | 1 | 0 | E1 | M2-M0 | github.com::repository_view |
| 20260918 | vless | https://github.com/python/cpython | 2 | 0 | 0 | E1 | M2-M0 | github.com::repository_view |
| 20260918 | vless | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E1 | M2-M0 | github.com::repository_view |
| 20260918 | vless | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 0 | E1 | M2-M0 | bing.com::search_results_view |
| 20260918 | vless | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 1 | E1 | M2-M0 | bing.com::search_results_view |
| 20260918 | vless | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E1 | M2-M0 | bing.com::search_results_view |
| 20260918 | vless | https://www.bing.com/search?q=solar+system+facts | 0 | 0 | 0 | E1 | M2-M0 | bing.com::search_results_view |
| 20260918 | vless | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 0 | E1 | M2-M0 | bing.com::search_results_view |
| 20260918 | vless | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E1 | M2-M0 | youtube.com::search_results_view |
| 20260918 | vless | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 1 | E1 | M2-M0 | youtube.com::search_results_view |
| 20260918 | vless | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E1 | M2-M0 | youtube.com::search_results_view |
| 20260918 | vless | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 0 | E1 | M2-M0 | youtube.com::search_results_view |
| 20260918 | vless | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E1 | M2-M0 | youtube.com::search_results_view |
| 20260918 | vless | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E1 | M2-M0 | youtube.com::video_playback |
| 20260918 | vless | youtube_video:aircAruvnKk | 5 | 0 | 0 | E1 | M2-M0 | youtube.com::video_playback |
| 20260918 | vless | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E1 | M2-M0 | youtube.com::video_playback |
| 20260918 | vless | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E1 | M2-M0 | youtube.com::video_playback |
| 20260918 | vless | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E1 | M2-M0 | youtube.com::video_playback |
| 20260918 | vmess | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 0 | E1 | M2-M0 | developer.mozilla.org::document_view |
| 20260918 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 0 | 0 | E1 | M2-M0 | developer.mozilla.org::document_view |
| 20260918 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 0 | E1 | M2-M0 | developer.mozilla.org::document_view |
| 20260918 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 1 | 0 | E1 | M2-M0 | developer.mozilla.org::document_view |
| 20260918 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 0 | 0 | E1 | M2-M0 | developer.mozilla.org::document_view |
| 20260918 | vmess | https://en.wikipedia.org/wiki/Computer_network | 3 | 0 | 1 | E1 | M2-M0 | wikipedia.org::article_view |
| 20260918 | vmess | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 0 | E1 | M2-M0 | wikipedia.org::article_view |
| 20260918 | vmess | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 0 | 0 | E1 | M2-M0 | wikipedia.org::article_view |
| 20260918 | vmess | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 1 | E1 | M2-M0 | wikipedia.org::article_view |
| 20260918 | vmess | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 1 | E1 | M2-M0 | wikipedia.org::article_view |
| 20260918 | vmess | https://github.com/RakuLomis/TrafficTracer | 2 | 0 | 0 | E1 | M2-M0 | github.com::repository_view |
| 20260918 | vmess | https://github.com/numpy/numpy | 2 | 0 | 0 | E1 | M2-M0 | github.com::repository_view |
| 20260918 | vmess | https://github.com/pallets/flask | 2 | 0 | 0 | E1 | M2-M0 | github.com::repository_view |
| 20260918 | vmess | https://github.com/python/cpython | 2 | 0 | 0 | E1 | M2-M0 | github.com::repository_view |
| 20260918 | vmess | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E1 | M2-M0 | github.com::repository_view |
| 20260918 | vmess | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 1 | E1 | M2-M0 | bing.com::search_results_view |
| 20260918 | vmess | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 0 | E1 | M2-M0 | bing.com::search_results_view |
| 20260918 | vmess | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E1 | M2-M0 | bing.com::search_results_view |
| 20260918 | vmess | https://www.bing.com/search?q=solar+system+facts | 0 | 0 | 0 | E1 | M2-M0 | bing.com::search_results_view |
| 20260918 | vmess | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 0 | E1 | M2-M0 | bing.com::search_results_view |
| 20260918 | vmess | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E1 | M2-M0 | youtube.com::search_results_view |
| 20260918 | vmess | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 0 | E1 | M2-M0 | youtube.com::search_results_view |
| 20260918 | vmess | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E1 | M2-M0 | youtube.com::search_results_view |
| 20260918 | vmess | https://www.youtube.com/results?search_query=piano+practice | 4 | 1 | 0 | E1 | M2-M0 | youtube.com::search_results_view |
| 20260918 | vmess | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E1 | M2-M0 | youtube.com::search_results_view |
| 20260918 | vmess | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E1 | M2-M0 | youtube.com::video_playback |
| 20260918 | vmess | youtube_video:aircAruvnKk | 5 | 0 | 0 | E1 | M2-M0 | youtube.com::video_playback |
| 20260918 | vmess | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E1 | M2-M0 | youtube.com::video_playback |
| 20260918 | vmess | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E1 | M2-M0 | youtube.com::video_playback |
| 20260918 | vmess | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E1 | M2-M0 | youtube.com::video_playback |
| 20260919 | anytls | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 0 | E1 | M2-M0 | developer.mozilla.org::document_view |
| 20260919 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 0 | 0 | E1 | M2-M0 | developer.mozilla.org::document_view |
| 20260919 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 0 | E1 | M2-M0 | developer.mozilla.org::document_view |
| 20260919 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 0 | 0 | E1 | M2-M0 | developer.mozilla.org::document_view |
| 20260919 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 0 | 0 | E1 | M2-M0 | developer.mozilla.org::document_view |
| 20260919 | anytls | https://en.wikipedia.org/wiki/Computer_network | 3 | 0 | 1 | E1 | M2-M0 | wikipedia.org::article_view |
| 20260919 | anytls | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 1 | E1 | M2-M0 | wikipedia.org::article_view |
| 20260919 | anytls | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 0 | 0 | E1 | M2-M0 | wikipedia.org::article_view |
| 20260919 | anytls | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 0 | E1 | M2-M0 | wikipedia.org::article_view |
| 20260919 | anytls | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 1 | E1 | M2-M0 | wikipedia.org::article_view |
| 20260919 | anytls | https://github.com/RakuLomis/TrafficTracer | 2 | 0 | 0 | E1 | M2-M0 | github.com::repository_view |
| 20260919 | anytls | https://github.com/numpy/numpy | 2 | 0 | 0 | E1 | M2-M0 | github.com::repository_view |
| 20260919 | anytls | https://github.com/pallets/flask | 2 | 0 | 0 | E1 | M2-M0 | github.com::repository_view |
| 20260919 | anytls | https://github.com/python/cpython | 2 | 0 | 0 | E1 | M2-M0 | github.com::repository_view |
| 20260919 | anytls | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E1 | M2-M0 | github.com::repository_view |
| 20260919 | anytls | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 0 | E1 | M2-M0 | bing.com::search_results_view |
| 20260919 | anytls | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 0 | E1 | M2-M0 | bing.com::search_results_view |
| 20260919 | anytls | https://www.bing.com/search?q=network+traffic+analysis | 0 | 1 | 0 | E1 | M2-M0 | bing.com::search_results_view |
| 20260919 | anytls | https://www.bing.com/search?q=solar+system+facts | 0 | 0 | 0 | E1 | M2-M0 | bing.com::search_results_view |
| 20260919 | anytls | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 0 | E1 | M2-M0 | bing.com::search_results_view |
| 20260919 | anytls | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E1 | M2-M0 | youtube.com::search_results_view |
| 20260919 | anytls | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 0 | E1 | M2-M0 | youtube.com::search_results_view |
| 20260919 | anytls | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E1 | M2-M0 | youtube.com::search_results_view |
| 20260919 | anytls | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 0 | E1 | M2-M0 | youtube.com::search_results_view |
| 20260919 | anytls | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E1 | M2-M0 | youtube.com::search_results_view |
| 20260919 | anytls | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E1 | M2-M0 | youtube.com::video_playback |
| 20260919 | anytls | youtube_video:aircAruvnKk | 5 | 0 | 0 | E1 | M2-M0 | youtube.com::video_playback |
| 20260919 | anytls | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E1 | M2-M0 | youtube.com::video_playback |
| 20260919 | anytls | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E1 | M2-M0 | youtube.com::video_playback |
| 20260919 | anytls | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E1 | M2-M0 | youtube.com::video_playback |
| 20260919 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 1 | 0 | E1 | M2-M0 | developer.mozilla.org::document_view |
| 20260919 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 1 | 0 | E1 | M2-M0 | developer.mozilla.org::document_view |
| 20260919 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 1 | 0 | E1 | M2-M0 | developer.mozilla.org::document_view |
| 20260919 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 2 | 0 | E1 | M2-M0 | developer.mozilla.org::document_view |
| 20260919 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 1 | 0 | E1 | M2-M0 | developer.mozilla.org::document_view |
| 20260919 | shadowsocks | https://en.wikipedia.org/wiki/Computer_network | 3 | 0 | 1 | E1 | M2-M0 | wikipedia.org::article_view |
| 20260919 | shadowsocks | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 1 | E1 | M2-M0 | wikipedia.org::article_view |
| 20260919 | shadowsocks | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 0 | 0 | E1 | M2-M0 | wikipedia.org::article_view |
| 20260919 | shadowsocks | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 2 | E1 | M2-M0 | wikipedia.org::article_view |
| 20260919 | shadowsocks | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 2 | E1 | M2-M0 | wikipedia.org::article_view |
| 20260919 | shadowsocks | https://github.com/RakuLomis/TrafficTracer | 2 | 1 | 0 | E1 | M2-M0 | github.com::repository_view |
| 20260919 | shadowsocks | https://github.com/numpy/numpy | 2 | 0 | 0 | E1 | M2-M0 | github.com::repository_view |
| 20260919 | shadowsocks | https://github.com/pallets/flask | 2 | 0 | 0 | E1 | M2-M0 | github.com::repository_view |
| 20260919 | shadowsocks | https://github.com/python/cpython | 2 | 0 | 0 | E1 | M2-M0 | github.com::repository_view |
| 20260919 | shadowsocks | https://github.com/scikit-learn/scikit-learn | 2 | 1 | 0 | E1 | M2-M0 | github.com::repository_view |
| 20260919 | shadowsocks | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 0 | E1 | M2-M0 | bing.com::search_results_view |
| 20260919 | shadowsocks | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 0 | E1 | M2-M0 | bing.com::search_results_view |
| 20260919 | shadowsocks | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E1 | M2-M0 | bing.com::search_results_view |
| 20260919 | shadowsocks | https://www.bing.com/search?q=solar+system+facts | 0 | 0 | 0 | E1 | M2-M0 | bing.com::search_results_view |
| 20260919 | shadowsocks | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 0 | E1 | M2-M0 | bing.com::search_results_view |
| 20260919 | shadowsocks | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E1 | M2-M0 | youtube.com::search_results_view |
| 20260919 | shadowsocks | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 1 | 0 | E1 | M2-M0 | youtube.com::search_results_view |
| 20260919 | shadowsocks | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E1 | M2-M0 | youtube.com::search_results_view |
| 20260919 | shadowsocks | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 0 | E1 | M2-M0 | youtube.com::search_results_view |
| 20260919 | shadowsocks | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E1 | M2-M0 | youtube.com::search_results_view |
| 20260919 | shadowsocks | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E1 | M2-M0 | youtube.com::video_playback |
| 20260919 | shadowsocks | youtube_video:aircAruvnKk | 5 | 0 | 0 | E1 | M2-M0 | youtube.com::video_playback |
| 20260919 | shadowsocks | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E1 | M2-M0 | youtube.com::video_playback |
| 20260919 | shadowsocks | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E1 | M2-M0 | youtube.com::video_playback |
| 20260919 | shadowsocks | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E1 | M2-M0 | youtube.com::video_playback |
| 20260919 | trojan | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 0 | E1 | M2-M0 | developer.mozilla.org::document_view |
| 20260919 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 2 | 0 | E1 | M2-M0 | developer.mozilla.org::document_view |
| 20260919 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 0 | E1 | M2-M0 | developer.mozilla.org::document_view |
| 20260919 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 1 | 0 | E1 | M2-M0 | developer.mozilla.org::document_view |
| 20260919 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 1 | 0 | E1 | M2-M0 | developer.mozilla.org::document_view |
| 20260919 | trojan | https://en.wikipedia.org/wiki/Computer_network | 3 | 0 | 0 | E1 | M2-M0 | wikipedia.org::article_view |
| 20260919 | trojan | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 1 | E1 | M2-M0 | wikipedia.org::article_view |
| 20260919 | trojan | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 0 | 0 | E1 | M2-M0 | wikipedia.org::article_view |
| 20260919 | trojan | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 1 | E1 | M2-M0 | wikipedia.org::article_view |
| 20260919 | trojan | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E1 | M2-M0 | wikipedia.org::article_view |
| 20260919 | trojan | https://github.com/RakuLomis/TrafficTracer | 2 | 0 | 0 | E1 | M2-M0 | github.com::repository_view |
| 20260919 | trojan | https://github.com/numpy/numpy | 2 | 0 | 0 | E1 | M2-M0 | github.com::repository_view |
| 20260919 | trojan | https://github.com/pallets/flask | 2 | 0 | 0 | E1 | M2-M0 | github.com::repository_view |
| 20260919 | trojan | https://github.com/python/cpython | 2 | 0 | 0 | E1 | M2-M0 | github.com::repository_view |
| 20260919 | trojan | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E1 | M2-M0 | github.com::repository_view |
| 20260919 | trojan | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 0 | E1 | M2-M0 | bing.com::search_results_view |
| 20260919 | trojan | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 0 | E1 | M2-M0 | bing.com::search_results_view |
| 20260919 | trojan | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E1 | M2-M0 | bing.com::search_results_view |
| 20260919 | trojan | https://www.bing.com/search?q=solar+system+facts | 0 | 0 | 0 | E1 | M2-M0 | bing.com::search_results_view |
| 20260919 | trojan | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 1 | 0 | E1 | M2-M0 | bing.com::search_results_view |
| 20260919 | trojan | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E1 | M2-M0 | youtube.com::search_results_view |
| 20260919 | trojan | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 1 | 0 | E1 | M2-M0 | youtube.com::search_results_view |
| 20260919 | trojan | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E1 | M2-M0 | youtube.com::search_results_view |
| 20260919 | trojan | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 0 | E1 | M2-M0 | youtube.com::search_results_view |
| 20260919 | trojan | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E1 | M2-M0 | youtube.com::search_results_view |
| 20260919 | trojan | youtube_video:R6MlUcmOul8 | 5 | 1 | 1 | E1 | M2-M0 | youtube.com::video_playback |
| 20260919 | trojan | youtube_video:aircAruvnKk | 5 | 0 | 0 | E1 | M2-M0 | youtube.com::video_playback |
| 20260919 | trojan | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E1 | M2-M0 | youtube.com::video_playback |
| 20260919 | trojan | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E1 | M2-M0 | youtube.com::video_playback |
| 20260919 | trojan | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E1 | M2-M0 | youtube.com::video_playback |
| 20260919 | vless | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 0 | E1 | M2-M0 | developer.mozilla.org::document_view |
| 20260919 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 1 | 0 | E1 | M2-M0 | developer.mozilla.org::document_view |
| 20260919 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 0 | E1 | M2-M0 | developer.mozilla.org::document_view |
| 20260919 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 1 | 0 | E1 | M2-M0 | developer.mozilla.org::document_view |
| 20260919 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 0 | 0 | E1 | M2-M0 | developer.mozilla.org::document_view |
| 20260919 | vless | https://en.wikipedia.org/wiki/Computer_network | 3 | 1 | 1 | E1 | M2-M0 | wikipedia.org::article_view |
| 20260919 | vless | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 1 | 0 | E1 | M2-M0 | wikipedia.org::article_view |
| 20260919 | vless | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 0 | 0 | E1 | M2-M0 | wikipedia.org::article_view |
| 20260919 | vless | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 0 | E1 | M2-M0 | wikipedia.org::article_view |
| 20260919 | vless | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E1 | M2-M0 | wikipedia.org::article_view |
| 20260919 | vless | https://github.com/RakuLomis/TrafficTracer | 2 | 0 | 0 | E1 | M2-M0 | github.com::repository_view |
| 20260919 | vless | https://github.com/numpy/numpy | 2 | 0 | 0 | E1 | M2-M0 | github.com::repository_view |
| 20260919 | vless | https://github.com/pallets/flask | 2 | 0 | 0 | E1 | M2-M0 | github.com::repository_view |
| 20260919 | vless | https://github.com/python/cpython | 2 | 0 | 0 | E1 | M2-M0 | github.com::repository_view |
| 20260919 | vless | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E1 | M2-M0 | github.com::repository_view |
| 20260919 | vless | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 0 | E1 | M2-M0 | bing.com::search_results_view |
| 20260919 | vless | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 0 | E1 | M2-M0 | bing.com::search_results_view |
| 20260919 | vless | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E1 | M2-M0 | bing.com::search_results_view |
| 20260919 | vless | https://www.bing.com/search?q=solar+system+facts | 0 | 0 | 0 | E1 | M2-M0 | bing.com::search_results_view |
| 20260919 | vless | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 0 | E1 | M2-M0 | bing.com::search_results_view |
| 20260919 | vless | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E1 | M2-M0 | youtube.com::search_results_view |
| 20260919 | vless | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 1 | E1 | M2-M0 | youtube.com::search_results_view |
| 20260919 | vless | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E1 | M2-M0 | youtube.com::search_results_view |
| 20260919 | vless | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 1 | E1 | M2-M0 | youtube.com::search_results_view |
| 20260919 | vless | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E1 | M2-M0 | youtube.com::search_results_view |
| 20260919 | vless | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E1 | M2-M0 | youtube.com::video_playback |
| 20260919 | vless | youtube_video:aircAruvnKk | 5 | 0 | 0 | E1 | M2-M0 | youtube.com::video_playback |
| 20260919 | vless | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E1 | M2-M0 | youtube.com::video_playback |
| 20260919 | vless | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E1 | M2-M0 | youtube.com::video_playback |
| 20260919 | vless | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E1 | M2-M0 | youtube.com::video_playback |
| 20260919 | vmess | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 0 | E1 | M2-M0 | developer.mozilla.org::document_view |
| 20260919 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 0 | 0 | E1 | M2-M0 | developer.mozilla.org::document_view |
| 20260919 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 0 | E1 | M2-M0 | developer.mozilla.org::document_view |
| 20260919 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 1 | 0 | E1 | M2-M0 | developer.mozilla.org::document_view |
| 20260919 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 0 | 0 | E1 | M2-M0 | developer.mozilla.org::document_view |
| 20260919 | vmess | https://en.wikipedia.org/wiki/Computer_network | 3 | 0 | 1 | E1 | M2-M0 | wikipedia.org::article_view |
| 20260919 | vmess | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 0 | E1 | M2-M0 | wikipedia.org::article_view |
| 20260919 | vmess | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 0 | 0 | E1 | M2-M0 | wikipedia.org::article_view |
| 20260919 | vmess | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 0 | E1 | M2-M0 | wikipedia.org::article_view |
| 20260919 | vmess | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E1 | M2-M0 | wikipedia.org::article_view |
| 20260919 | vmess | https://github.com/RakuLomis/TrafficTracer | 2 | 0 | 0 | E1 | M2-M0 | github.com::repository_view |
| 20260919 | vmess | https://github.com/numpy/numpy | 2 | 0 | 0 | E1 | M2-M0 | github.com::repository_view |
| 20260919 | vmess | https://github.com/pallets/flask | 2 | 1 | 0 | E1 | M2-M0 | github.com::repository_view |
| 20260919 | vmess | https://github.com/python/cpython | 2 | 0 | 0 | E1 | M2-M0 | github.com::repository_view |
| 20260919 | vmess | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E1 | M2-M0 | github.com::repository_view |
| 20260919 | vmess | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 0 | E1 | M2-M0 | bing.com::search_results_view |
| 20260919 | vmess | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 0 | E1 | M2-M0 | bing.com::search_results_view |
| 20260919 | vmess | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E1 | M2-M0 | bing.com::search_results_view |
| 20260919 | vmess | https://www.bing.com/search?q=solar+system+facts | 0 | 0 | 0 | E1 | M2-M0 | bing.com::search_results_view |
| 20260919 | vmess | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 0 | E1 | M2-M0 | bing.com::search_results_view |
| 20260919 | vmess | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E1 | M2-M0 | youtube.com::search_results_view |
| 20260919 | vmess | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 0 | E1 | M2-M0 | youtube.com::search_results_view |
| 20260919 | vmess | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E1 | M2-M0 | youtube.com::search_results_view |
| 20260919 | vmess | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 0 | E1 | M2-M0 | youtube.com::search_results_view |
| 20260919 | vmess | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E1 | M2-M0 | youtube.com::search_results_view |
| 20260919 | vmess | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E1 | M2-M0 | youtube.com::video_playback |
| 20260919 | vmess | youtube_video:aircAruvnKk | 5 | 0 | 0 | E1 | M2-M0 | youtube.com::video_playback |
| 20260919 | vmess | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E1 | M2-M0 | youtube.com::video_playback |
| 20260919 | vmess | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E1 | M2-M0 | youtube.com::video_playback |
| 20260919 | vmess | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E1 | M2-M0 | youtube.com::video_playback |
| 20260920 | anytls | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 0 | E1 | M2-M0 | developer.mozilla.org::document_view |
| 20260920 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 0 | 0 | E1 | M2-M0 | developer.mozilla.org::document_view |
| 20260920 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 0 | E1 | M2-M0 | developer.mozilla.org::document_view |
| 20260920 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 0 | 0 | E1 | M2-M0 | developer.mozilla.org::document_view |
| 20260920 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 0 | 0 | E1 | M2-M0 | developer.mozilla.org::document_view |
| 20260920 | anytls | https://en.wikipedia.org/wiki/Computer_network | 3 | 0 | 1 | E1 | M2-M0 | wikipedia.org::article_view |
| 20260920 | anytls | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 0 | E1 | M2-M0 | wikipedia.org::article_view |
| 20260920 | anytls | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 0 | 0 | E1 | M2-M0 | wikipedia.org::article_view |
| 20260920 | anytls | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 0 | E1 | M2-M0 | wikipedia.org::article_view |
| 20260920 | anytls | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E1 | M2-M0 | wikipedia.org::article_view |
| 20260920 | anytls | https://github.com/RakuLomis/TrafficTracer | 2 | 1 | 0 | E1 | M2-M0 | github.com::repository_view |
| 20260920 | anytls | https://github.com/numpy/numpy | 2 | 0 | 0 | E1 | M2-M0 | github.com::repository_view |
| 20260920 | anytls | https://github.com/pallets/flask | 2 | 0 | 0 | E1 | M2-M0 | github.com::repository_view |
| 20260920 | anytls | https://github.com/python/cpython | 2 | 0 | 0 | E1 | M2-M0 | github.com::repository_view |
| 20260920 | anytls | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E1 | M2-M0 | github.com::repository_view |
| 20260920 | anytls | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 0 | E1 | M2-M0 | bing.com::search_results_view |
| 20260920 | anytls | https://www.bing.com/search?q=indoor+plant+care | 0 | 1 | 0 | E1 | M2-M0 | bing.com::search_results_view |
| 20260920 | anytls | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E1 | M2-M0 | bing.com::search_results_view |
| 20260920 | anytls | https://www.bing.com/search?q=solar+system+facts | 0 | 0 | 0 | E1 | M2-M0 | bing.com::search_results_view |
| 20260920 | anytls | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 0 | E1 | M2-M0 | bing.com::search_results_view |
| 20260920 | anytls | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E1 | M2-M0 | youtube.com::search_results_view |
| 20260920 | anytls | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 0 | E1 | M2-M0 | youtube.com::search_results_view |
| 20260920 | anytls | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E1 | M2-M0 | youtube.com::search_results_view |
| 20260920 | anytls | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 0 | E1 | M2-M0 | youtube.com::search_results_view |
| 20260920 | anytls | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E1 | M2-M0 | youtube.com::search_results_view |
| 20260920 | anytls | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E1 | M2-M0 | youtube.com::video_playback |
| 20260920 | anytls | youtube_video:aircAruvnKk | 5 | 0 | 0 | E1 | M2-M0 | youtube.com::video_playback |
| 20260920 | anytls | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E1 | M2-M0 | youtube.com::video_playback |
| 20260920 | anytls | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E1 | M2-M0 | youtube.com::video_playback |
| 20260920 | anytls | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E1 | M2-M0 | youtube.com::video_playback |
| 20260920 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 1 | 0 | E1 | M2-M0 | developer.mozilla.org::document_view |
| 20260920 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 1 | 0 | E1 | M2-M0 | developer.mozilla.org::document_view |
| 20260920 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 0 | E1 | M2-M0 | developer.mozilla.org::document_view |
| 20260920 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 2 | 0 | E1 | M2-M0 | developer.mozilla.org::document_view |
| 20260920 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 1 | 0 | E1 | M2-M0 | developer.mozilla.org::document_view |
| 20260920 | shadowsocks | https://en.wikipedia.org/wiki/Computer_network | 3 | 0 | 2 | E1 | M2-M0 | wikipedia.org::article_view |
| 20260920 | shadowsocks | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 2 | E1 | M2-M0 | wikipedia.org::article_view |
| 20260920 | shadowsocks | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 0 | 0 | E1 | M2-M0 | wikipedia.org::article_view |
| 20260920 | shadowsocks | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 1 | E1 | M2-M0 | wikipedia.org::article_view |
| 20260920 | shadowsocks | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 2 | E1 | M2-M0 | wikipedia.org::article_view |
| 20260920 | shadowsocks | https://github.com/RakuLomis/TrafficTracer | 2 | 0 | 0 | E1 | M2-M0 | github.com::repository_view |
| 20260920 | shadowsocks | https://github.com/numpy/numpy | 2 | 2 | 0 | E1 | M2-M0 | github.com::repository_view |
| 20260920 | shadowsocks | https://github.com/pallets/flask | 2 | 1 | 0 | E1 | M2-M0 | github.com::repository_view |
| 20260920 | shadowsocks | https://github.com/python/cpython | 2 | 0 | 0 | E1 | M2-M0 | github.com::repository_view |
| 20260920 | shadowsocks | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E1 | M2-M0 | github.com::repository_view |
| 20260920 | shadowsocks | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 0 | E1 | M2-M0 | bing.com::search_results_view |
| 20260920 | shadowsocks | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 0 | E1 | M2-M0 | bing.com::search_results_view |
| 20260920 | shadowsocks | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E1 | M2-M0 | bing.com::search_results_view |
| 20260920 | shadowsocks | https://www.bing.com/search?q=solar+system+facts | 0 | 0 | 0 | E1 | M2-M0 | bing.com::search_results_view |
| 20260920 | shadowsocks | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 0 | E1 | M2-M0 | bing.com::search_results_view |
| 20260920 | shadowsocks | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E1 | M2-M0 | youtube.com::search_results_view |
| 20260920 | shadowsocks | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 0 | E1 | M2-M0 | youtube.com::search_results_view |
| 20260920 | shadowsocks | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E1 | M2-M0 | youtube.com::search_results_view |
| 20260920 | shadowsocks | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 0 | E1 | M2-M0 | youtube.com::search_results_view |
| 20260920 | shadowsocks | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E1 | M2-M0 | youtube.com::search_results_view |
| 20260920 | shadowsocks | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E1 | M2-M0 | youtube.com::video_playback |
| 20260920 | shadowsocks | youtube_video:aircAruvnKk | 5 | 0 | 0 | E1 | M2-M0 | youtube.com::video_playback |
| 20260920 | shadowsocks | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E1 | M2-M0 | youtube.com::video_playback |
| 20260920 | shadowsocks | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E1 | M2-M0 | youtube.com::video_playback |
| 20260920 | shadowsocks | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E1 | M2-M0 | youtube.com::video_playback |
| 20260920 | trojan | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 0 | E1 | M2-M0 | developer.mozilla.org::document_view |
| 20260920 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 1 | 0 | E1 | M2-M0 | developer.mozilla.org::document_view |
| 20260920 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 0 | E1 | M2-M0 | developer.mozilla.org::document_view |
| 20260920 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 2 | 0 | E1 | M2-M0 | developer.mozilla.org::document_view |
| 20260920 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 1 | 0 | E1 | M2-M0 | developer.mozilla.org::document_view |
| 20260920 | trojan | https://en.wikipedia.org/wiki/Computer_network | 3 | 0 | 0 | E1 | M2-M0 | wikipedia.org::article_view |
| 20260920 | trojan | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 0 | E1 | M2-M0 | wikipedia.org::article_view |
| 20260920 | trojan | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 0 | 1 | E1 | M2-M0 | wikipedia.org::article_view |
| 20260920 | trojan | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 0 | E1 | M2-M0 | wikipedia.org::article_view |
| 20260920 | trojan | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E1 | M2-M0 | wikipedia.org::article_view |
| 20260920 | trojan | https://github.com/RakuLomis/TrafficTracer | 2 | 0 | 0 | E1 | M2-M0 | github.com::repository_view |
| 20260920 | trojan | https://github.com/numpy/numpy | 2 | 0 | 0 | E1 | M2-M0 | github.com::repository_view |
| 20260920 | trojan | https://github.com/pallets/flask | 2 | 0 | 0 | E1 | M2-M0 | github.com::repository_view |
| 20260920 | trojan | https://github.com/python/cpython | 2 | 0 | 0 | E1 | M2-M0 | github.com::repository_view |
| 20260920 | trojan | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E1 | M2-M0 | github.com::repository_view |
| 20260920 | trojan | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 0 | E1 | M2-M0 | bing.com::search_results_view |
| 20260920 | trojan | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 0 | E1 | M2-M0 | bing.com::search_results_view |
| 20260920 | trojan | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E1 | M2-M0 | bing.com::search_results_view |
| 20260920 | trojan | https://www.bing.com/search?q=solar+system+facts | 0 | 0 | 0 | E1 | M2-M0 | bing.com::search_results_view |
| 20260920 | trojan | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 1 | 0 | E1 | M2-M0 | bing.com::search_results_view |
| 20260920 | trojan | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E1 | M2-M0 | youtube.com::search_results_view |
| 20260920 | trojan | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 0 | E1 | M2-M0 | youtube.com::search_results_view |
| 20260920 | trojan | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E1 | M2-M0 | youtube.com::search_results_view |
| 20260920 | trojan | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 0 | E1 | M2-M0 | youtube.com::search_results_view |
| 20260920 | trojan | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E1 | M2-M0 | youtube.com::search_results_view |
| 20260920 | trojan | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E1 | M2-M0 | youtube.com::video_playback |
| 20260920 | trojan | youtube_video:aircAruvnKk | 5 | 0 | 0 | E1 | M2-M0 | youtube.com::video_playback |
| 20260920 | trojan | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E1 | M2-M0 | youtube.com::video_playback |
| 20260920 | trojan | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E1 | M2-M0 | youtube.com::video_playback |
| 20260920 | trojan | youtube_video:sAWK0mgrMp4 | 5 | 0 | 1 | E1 | M2-M0 | youtube.com::video_playback |
| 20260920 | vless | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 0 | E1 | M2-M0 | developer.mozilla.org::document_view |
| 20260920 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 1 | 0 | E1 | M2-M0 | developer.mozilla.org::document_view |
| 20260920 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 1 | 0 | E1 | M2-M0 | developer.mozilla.org::document_view |
| 20260920 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 1 | 0 | E1 | M2-M0 | developer.mozilla.org::document_view |
| 20260920 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 0 | 0 | E1 | M2-M0 | developer.mozilla.org::document_view |
| 20260920 | vless | https://en.wikipedia.org/wiki/Computer_network | 3 | 1 | 1 | E1 | M2-M0 | wikipedia.org::article_view |
| 20260920 | vless | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 0 | E1 | M2-M0 | wikipedia.org::article_view |
| 20260920 | vless | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 0 | 0 | E1 | M2-M0 | wikipedia.org::article_view |
| 20260920 | vless | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 0 | E1 | M2-M0 | wikipedia.org::article_view |
| 20260920 | vless | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E1 | M2-M0 | wikipedia.org::article_view |
| 20260920 | vless | https://github.com/RakuLomis/TrafficTracer | 2 | 0 | 0 | E1 | M2-M0 | github.com::repository_view |
| 20260920 | vless | https://github.com/numpy/numpy | 2 | 0 | 0 | E1 | M2-M0 | github.com::repository_view |
| 20260920 | vless | https://github.com/pallets/flask | 2 | 1 | 0 | E1 | M2-M0 | github.com::repository_view |
| 20260920 | vless | https://github.com/python/cpython | 2 | 0 | 0 | E1 | M2-M0 | github.com::repository_view |
| 20260920 | vless | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E1 | M2-M0 | github.com::repository_view |
| 20260920 | vless | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 0 | E1 | M2-M0 | bing.com::search_results_view |
| 20260920 | vless | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 0 | E1 | M2-M0 | bing.com::search_results_view |
| 20260920 | vless | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E1 | M2-M0 | bing.com::search_results_view |
| 20260920 | vless | https://www.bing.com/search?q=solar+system+facts | 0 | 1 | 0 | E1 | M2-M0 | bing.com::search_results_view |
| 20260920 | vless | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 1 | E1 | M2-M0 | bing.com::search_results_view |
| 20260920 | vless | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E1 | M2-M0 | youtube.com::search_results_view |
| 20260920 | vless | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 1 | E1 | M2-M0 | youtube.com::search_results_view |
| 20260920 | vless | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E1 | M2-M0 | youtube.com::search_results_view |
| 20260920 | vless | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 1 | E1 | M2-M0 | youtube.com::search_results_view |
| 20260920 | vless | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 1 | 0 | E1 | M2-M0 | youtube.com::search_results_view |
| 20260920 | vless | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E1 | M2-M0 | youtube.com::video_playback |
| 20260920 | vless | youtube_video:aircAruvnKk | 5 | 0 | 0 | E1 | M2-M0 | youtube.com::video_playback |
| 20260920 | vless | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E1 | M2-M0 | youtube.com::video_playback |
| 20260920 | vless | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E1 | M2-M0 | youtube.com::video_playback |
| 20260920 | vless | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E1 | M2-M0 | youtube.com::video_playback |
| 20260920 | vmess | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 0 | E1 | M2-M0 | developer.mozilla.org::document_view |
| 20260920 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 0 | 0 | E1 | M2-M0 | developer.mozilla.org::document_view |
| 20260920 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 0 | E1 | M2-M0 | developer.mozilla.org::document_view |
| 20260920 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 0 | 0 | E1 | M2-M0 | developer.mozilla.org::document_view |
| 20260920 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 0 | 0 | E1 | M2-M0 | developer.mozilla.org::document_view |
| 20260920 | vmess | https://en.wikipedia.org/wiki/Computer_network | 3 | 0 | 1 | E1 | M2-M0 | wikipedia.org::article_view |
| 20260920 | vmess | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 0 | E1 | M2-M0 | wikipedia.org::article_view |
| 20260920 | vmess | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 0 | 0 | E1 | M2-M0 | wikipedia.org::article_view |
| 20260920 | vmess | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 1 | E1 | M2-M0 | wikipedia.org::article_view |
| 20260920 | vmess | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E1 | M2-M0 | wikipedia.org::article_view |
| 20260920 | vmess | https://github.com/RakuLomis/TrafficTracer | 2 | 0 | 0 | E1 | M2-M0 | github.com::repository_view |
| 20260920 | vmess | https://github.com/numpy/numpy | 2 | 0 | 0 | E1 | M2-M0 | github.com::repository_view |
| 20260920 | vmess | https://github.com/pallets/flask | 2 | 0 | 0 | E1 | M2-M0 | github.com::repository_view |
| 20260920 | vmess | https://github.com/python/cpython | 2 | 0 | 0 | E1 | M2-M0 | github.com::repository_view |
| 20260920 | vmess | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E1 | M2-M0 | github.com::repository_view |
| 20260920 | vmess | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 0 | E1 | M2-M0 | bing.com::search_results_view |
| 20260920 | vmess | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 0 | E1 | M2-M0 | bing.com::search_results_view |
| 20260920 | vmess | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E1 | M2-M0 | bing.com::search_results_view |
| 20260920 | vmess | https://www.bing.com/search?q=solar+system+facts | 0 | 0 | 0 | E1 | M2-M0 | bing.com::search_results_view |
| 20260920 | vmess | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 0 | E1 | M2-M0 | bing.com::search_results_view |
| 20260920 | vmess | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E1 | M2-M0 | youtube.com::search_results_view |
| 20260920 | vmess | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 0 | E1 | M2-M0 | youtube.com::search_results_view |
| 20260920 | vmess | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E1 | M2-M0 | youtube.com::search_results_view |
| 20260920 | vmess | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 0 | E1 | M2-M0 | youtube.com::search_results_view |
| 20260920 | vmess | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E1 | M2-M0 | youtube.com::search_results_view |
| 20260920 | vmess | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E1 | M2-M0 | youtube.com::video_playback |
| 20260920 | vmess | youtube_video:aircAruvnKk | 5 | 0 | 0 | E1 | M2-M0 | youtube.com::video_playback |
| 20260920 | vmess | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E1 | M2-M0 | youtube.com::video_playback |
| 20260920 | vmess | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E1 | M2-M0 | youtube.com::video_playback |
| 20260920 | vmess | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E1 | M2-M0 | youtube.com::video_playback |
| 20260918 | anytls | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 0 | E1 | M2-M1 | developer.mozilla.org::document_view |
| 20260918 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 0 | 0 | E1 | M2-M1 | developer.mozilla.org::document_view |
| 20260918 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 0 | E1 | M2-M1 | developer.mozilla.org::document_view |
| 20260918 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 0 | 0 | E1 | M2-M1 | developer.mozilla.org::document_view |
| 20260918 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 1 | 0 | E1 | M2-M1 | developer.mozilla.org::document_view |
| 20260918 | anytls | https://en.wikipedia.org/wiki/Computer_network | 3 | 2 | 0 | E1 | M2-M1 | wikipedia.org::article_view |
| 20260918 | anytls | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 2 | 0 | E1 | M2-M1 | wikipedia.org::article_view |
| 20260918 | anytls | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 1 | 0 | E1 | M2-M1 | wikipedia.org::article_view |
| 20260918 | anytls | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 2 | 0 | E1 | M2-M1 | wikipedia.org::article_view |
| 20260918 | anytls | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E1 | M2-M1 | wikipedia.org::article_view |
| 20260918 | anytls | https://github.com/RakuLomis/TrafficTracer | 2 | 1 | 0 | E1 | M2-M1 | github.com::repository_view |
| 20260918 | anytls | https://github.com/numpy/numpy | 2 | 0 | 0 | E1 | M2-M1 | github.com::repository_view |
| 20260918 | anytls | https://github.com/pallets/flask | 2 | 1 | 0 | E1 | M2-M1 | github.com::repository_view |
| 20260918 | anytls | https://github.com/python/cpython | 2 | 0 | 0 | E1 | M2-M1 | github.com::repository_view |
| 20260918 | anytls | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E1 | M2-M1 | github.com::repository_view |
| 20260918 | anytls | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 0 | E1 | M2-M1 | bing.com::search_results_view |
| 20260918 | anytls | https://www.bing.com/search?q=indoor+plant+care | 0 | 1 | 0 | E1 | M2-M1 | bing.com::search_results_view |
| 20260918 | anytls | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E1 | M2-M1 | bing.com::search_results_view |
| 20260918 | anytls | https://www.bing.com/search?q=solar+system+facts | 0 | 1 | 0 | E1 | M2-M1 | bing.com::search_results_view |
| 20260918 | anytls | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 0 | E1 | M2-M1 | bing.com::search_results_view |
| 20260918 | anytls | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 1 | 0 | E1 | M2-M1 | youtube.com::search_results_view |
| 20260918 | anytls | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 0 | E1 | M2-M1 | youtube.com::search_results_view |
| 20260918 | anytls | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E1 | M2-M1 | youtube.com::search_results_view |
| 20260918 | anytls | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 0 | E1 | M2-M1 | youtube.com::search_results_view |
| 20260918 | anytls | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E1 | M2-M1 | youtube.com::search_results_view |
| 20260918 | anytls | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E1 | M2-M1 | youtube.com::video_playback |
| 20260918 | anytls | youtube_video:aircAruvnKk | 5 | 0 | 0 | E1 | M2-M1 | youtube.com::video_playback |
| 20260918 | anytls | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E1 | M2-M1 | youtube.com::video_playback |
| 20260918 | anytls | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E1 | M2-M1 | youtube.com::video_playback |
| 20260918 | anytls | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E1 | M2-M1 | youtube.com::video_playback |
| 20260918 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 4 | 0 | E1 | M2-M1 | developer.mozilla.org::document_view |
| 20260918 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 4 | 0 | E1 | M2-M1 | developer.mozilla.org::document_view |
| 20260918 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 4 | 0 | E1 | M2-M1 | developer.mozilla.org::document_view |
| 20260918 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 3 | 0 | E1 | M2-M1 | developer.mozilla.org::document_view |
| 20260918 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 3 | 0 | E1 | M2-M1 | developer.mozilla.org::document_view |
| 20260918 | shadowsocks | https://en.wikipedia.org/wiki/Computer_network | 3 | 3 | 0 | E1 | M2-M1 | wikipedia.org::article_view |
| 20260918 | shadowsocks | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 0 | E1 | M2-M1 | wikipedia.org::article_view |
| 20260918 | shadowsocks | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 3 | 0 | E1 | M2-M1 | wikipedia.org::article_view |
| 20260918 | shadowsocks | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 0 | E1 | M2-M1 | wikipedia.org::article_view |
| 20260918 | shadowsocks | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 1 | 0 | E1 | M2-M1 | wikipedia.org::article_view |
| 20260918 | shadowsocks | https://github.com/RakuLomis/TrafficTracer | 2 | 0 | 0 | E1 | M2-M1 | github.com::repository_view |
| 20260918 | shadowsocks | https://github.com/numpy/numpy | 2 | 2 | 0 | E1 | M2-M1 | github.com::repository_view |
| 20260918 | shadowsocks | https://github.com/pallets/flask | 2 | 1 | 0 | E1 | M2-M1 | github.com::repository_view |
| 20260918 | shadowsocks | https://github.com/python/cpython | 2 | 0 | 0 | E1 | M2-M1 | github.com::repository_view |
| 20260918 | shadowsocks | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E1 | M2-M1 | github.com::repository_view |
| 20260918 | shadowsocks | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 3 | 0 | E1 | M2-M1 | bing.com::search_results_view |
| 20260918 | shadowsocks | https://www.bing.com/search?q=indoor+plant+care | 0 | 1 | 0 | E1 | M2-M1 | bing.com::search_results_view |
| 20260918 | shadowsocks | https://www.bing.com/search?q=network+traffic+analysis | 0 | 2 | 0 | E1 | M2-M1 | bing.com::search_results_view |
| 20260918 | shadowsocks | https://www.bing.com/search?q=solar+system+facts | 0 | 3 | 0 | E1 | M2-M1 | bing.com::search_results_view |
| 20260918 | shadowsocks | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 2 | 0 | E1 | M2-M1 | bing.com::search_results_view |
| 20260918 | shadowsocks | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 1 | 0 | E1 | M2-M1 | youtube.com::search_results_view |
| 20260918 | shadowsocks | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 0 | E1 | M2-M1 | youtube.com::search_results_view |
| 20260918 | shadowsocks | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E1 | M2-M1 | youtube.com::search_results_view |
| 20260918 | shadowsocks | https://www.youtube.com/results?search_query=piano+practice | 4 | 1 | 0 | E1 | M2-M1 | youtube.com::search_results_view |
| 20260918 | shadowsocks | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 1 | 0 | E1 | M2-M1 | youtube.com::search_results_view |
| 20260918 | shadowsocks | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E1 | M2-M1 | youtube.com::video_playback |
| 20260918 | shadowsocks | youtube_video:aircAruvnKk | 5 | 0 | 0 | E1 | M2-M1 | youtube.com::video_playback |
| 20260918 | shadowsocks | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E1 | M2-M1 | youtube.com::video_playback |
| 20260918 | shadowsocks | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E1 | M2-M1 | youtube.com::video_playback |
| 20260918 | shadowsocks | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E1 | M2-M1 | youtube.com::video_playback |
| 20260918 | trojan | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 0 | E1 | M2-M1 | developer.mozilla.org::document_view |
| 20260918 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 0 | 2 | E1 | M2-M1 | developer.mozilla.org::document_view |
| 20260918 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 1 | 1 | E1 | M2-M1 | developer.mozilla.org::document_view |
| 20260918 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 0 | 0 | E1 | M2-M1 | developer.mozilla.org::document_view |
| 20260918 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 1 | 0 | E1 | M2-M1 | developer.mozilla.org::document_view |
| 20260918 | trojan | https://en.wikipedia.org/wiki/Computer_network | 3 | 1 | 0 | E1 | M2-M1 | wikipedia.org::article_view |
| 20260918 | trojan | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 1 | E1 | M2-M1 | wikipedia.org::article_view |
| 20260918 | trojan | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 0 | 0 | E1 | M2-M1 | wikipedia.org::article_view |
| 20260918 | trojan | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 0 | E1 | M2-M1 | wikipedia.org::article_view |
| 20260918 | trojan | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 2 | 0 | E1 | M2-M1 | wikipedia.org::article_view |
| 20260918 | trojan | https://github.com/RakuLomis/TrafficTracer | 2 | 0 | 0 | E1 | M2-M1 | github.com::repository_view |
| 20260918 | trojan | https://github.com/numpy/numpy | 2 | 0 | 0 | E1 | M2-M1 | github.com::repository_view |
| 20260918 | trojan | https://github.com/pallets/flask | 2 | 1 | 0 | E1 | M2-M1 | github.com::repository_view |
| 20260918 | trojan | https://github.com/python/cpython | 2 | 0 | 0 | E1 | M2-M1 | github.com::repository_view |
| 20260918 | trojan | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E1 | M2-M1 | github.com::repository_view |
| 20260918 | trojan | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 0 | E1 | M2-M1 | bing.com::search_results_view |
| 20260918 | trojan | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 1 | E1 | M2-M1 | bing.com::search_results_view |
| 20260918 | trojan | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E1 | M2-M1 | bing.com::search_results_view |
| 20260918 | trojan | https://www.bing.com/search?q=solar+system+facts | 0 | 0 | 0 | E1 | M2-M1 | bing.com::search_results_view |
| 20260918 | trojan | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 1 | E1 | M2-M1 | bing.com::search_results_view |
| 20260918 | trojan | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E1 | M2-M1 | youtube.com::search_results_view |
| 20260918 | trojan | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 1 | 1 | E1 | M2-M1 | youtube.com::search_results_view |
| 20260918 | trojan | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E1 | M2-M1 | youtube.com::search_results_view |
| 20260918 | trojan | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 0 | E1 | M2-M1 | youtube.com::search_results_view |
| 20260918 | trojan | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 1 | E1 | M2-M1 | youtube.com::search_results_view |
| 20260918 | trojan | youtube_video:R6MlUcmOul8 | 5 | 0 | 1 | E1 | M2-M1 | youtube.com::video_playback |
| 20260918 | trojan | youtube_video:aircAruvnKk | 5 | 0 | 0 | E1 | M2-M1 | youtube.com::video_playback |
| 20260918 | trojan | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E1 | M2-M1 | youtube.com::video_playback |
| 20260918 | trojan | youtube_video:eRsGyueVLvQ | 5 | 0 | 2 | E1 | M2-M1 | youtube.com::video_playback |
| 20260918 | trojan | youtube_video:sAWK0mgrMp4 | 5 | 0 | 1 | E1 | M2-M1 | youtube.com::video_playback |
| 20260918 | vless | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 0 | E1 | M2-M1 | developer.mozilla.org::document_view |
| 20260918 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 0 | 4 | E1 | M2-M1 | developer.mozilla.org::document_view |
| 20260918 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 2 | E1 | M2-M1 | developer.mozilla.org::document_view |
| 20260918 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 0 | 0 | E1 | M2-M1 | developer.mozilla.org::document_view |
| 20260918 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 0 | 0 | E1 | M2-M1 | developer.mozilla.org::document_view |
| 20260918 | vless | https://en.wikipedia.org/wiki/Computer_network | 3 | 1 | 0 | E1 | M2-M1 | wikipedia.org::article_view |
| 20260918 | vless | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 1 | 0 | E1 | M2-M1 | wikipedia.org::article_view |
| 20260918 | vless | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 1 | 0 | E1 | M2-M1 | wikipedia.org::article_view |
| 20260918 | vless | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 0 | E1 | M2-M1 | wikipedia.org::article_view |
| 20260918 | vless | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 1 | 0 | E1 | M2-M1 | wikipedia.org::article_view |
| 20260918 | vless | https://github.com/RakuLomis/TrafficTracer | 2 | 1 | 0 | E1 | M2-M1 | github.com::repository_view |
| 20260918 | vless | https://github.com/numpy/numpy | 2 | 0 | 0 | E1 | M2-M1 | github.com::repository_view |
| 20260918 | vless | https://github.com/pallets/flask | 2 | 1 | 0 | E1 | M2-M1 | github.com::repository_view |
| 20260918 | vless | https://github.com/python/cpython | 2 | 0 | 0 | E1 | M2-M1 | github.com::repository_view |
| 20260918 | vless | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 1 | E1 | M2-M1 | github.com::repository_view |
| 20260918 | vless | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 0 | E1 | M2-M1 | bing.com::search_results_view |
| 20260918 | vless | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 1 | E1 | M2-M1 | bing.com::search_results_view |
| 20260918 | vless | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E1 | M2-M1 | bing.com::search_results_view |
| 20260918 | vless | https://www.bing.com/search?q=solar+system+facts | 0 | 0 | 0 | E1 | M2-M1 | bing.com::search_results_view |
| 20260918 | vless | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 0 | E1 | M2-M1 | bing.com::search_results_view |
| 20260918 | vless | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E1 | M2-M1 | youtube.com::search_results_view |
| 20260918 | vless | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 2 | E1 | M2-M1 | youtube.com::search_results_view |
| 20260918 | vless | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 1 | E1 | M2-M1 | youtube.com::search_results_view |
| 20260918 | vless | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 1 | E1 | M2-M1 | youtube.com::search_results_view |
| 20260918 | vless | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E1 | M2-M1 | youtube.com::search_results_view |
| 20260918 | vless | youtube_video:R6MlUcmOul8 | 5 | 0 | 1 | E1 | M2-M1 | youtube.com::video_playback |
| 20260918 | vless | youtube_video:aircAruvnKk | 5 | 0 | 0 | E1 | M2-M1 | youtube.com::video_playback |
| 20260918 | vless | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E1 | M2-M1 | youtube.com::video_playback |
| 20260918 | vless | youtube_video:eRsGyueVLvQ | 5 | 0 | 1 | E1 | M2-M1 | youtube.com::video_playback |
| 20260918 | vless | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E1 | M2-M1 | youtube.com::video_playback |
| 20260918 | vmess | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 0 | E1 | M2-M1 | developer.mozilla.org::document_view |
| 20260918 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 0 | 0 | E1 | M2-M1 | developer.mozilla.org::document_view |
| 20260918 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 0 | E1 | M2-M1 | developer.mozilla.org::document_view |
| 20260918 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 0 | 1 | E1 | M2-M1 | developer.mozilla.org::document_view |
| 20260918 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 2 | 0 | E1 | M2-M1 | developer.mozilla.org::document_view |
| 20260918 | vmess | https://en.wikipedia.org/wiki/Computer_network | 3 | 1 | 0 | E1 | M2-M1 | wikipedia.org::article_view |
| 20260918 | vmess | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 0 | E1 | M2-M1 | wikipedia.org::article_view |
| 20260918 | vmess | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 1 | 0 | E1 | M2-M1 | wikipedia.org::article_view |
| 20260918 | vmess | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 1 | E1 | M2-M1 | wikipedia.org::article_view |
| 20260918 | vmess | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E1 | M2-M1 | wikipedia.org::article_view |
| 20260918 | vmess | https://github.com/RakuLomis/TrafficTracer | 2 | 0 | 0 | E1 | M2-M1 | github.com::repository_view |
| 20260918 | vmess | https://github.com/numpy/numpy | 2 | 0 | 0 | E1 | M2-M1 | github.com::repository_view |
| 20260918 | vmess | https://github.com/pallets/flask | 2 | 1 | 0 | E1 | M2-M1 | github.com::repository_view |
| 20260918 | vmess | https://github.com/python/cpython | 2 | 0 | 0 | E1 | M2-M1 | github.com::repository_view |
| 20260918 | vmess | https://github.com/scikit-learn/scikit-learn | 2 | 1 | 0 | E1 | M2-M1 | github.com::repository_view |
| 20260918 | vmess | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 1 | E1 | M2-M1 | bing.com::search_results_view |
| 20260918 | vmess | https://www.bing.com/search?q=indoor+plant+care | 0 | 1 | 1 | E1 | M2-M1 | bing.com::search_results_view |
| 20260918 | vmess | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E1 | M2-M1 | bing.com::search_results_view |
| 20260918 | vmess | https://www.bing.com/search?q=solar+system+facts | 0 | 0 | 1 | E1 | M2-M1 | bing.com::search_results_view |
| 20260918 | vmess | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 0 | E1 | M2-M1 | bing.com::search_results_view |
| 20260918 | vmess | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E1 | M2-M1 | youtube.com::search_results_view |
| 20260918 | vmess | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 0 | E1 | M2-M1 | youtube.com::search_results_view |
| 20260918 | vmess | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E1 | M2-M1 | youtube.com::search_results_view |
| 20260918 | vmess | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 0 | E1 | M2-M1 | youtube.com::search_results_view |
| 20260918 | vmess | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E1 | M2-M1 | youtube.com::search_results_view |
| 20260918 | vmess | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E1 | M2-M1 | youtube.com::video_playback |
| 20260918 | vmess | youtube_video:aircAruvnKk | 5 | 0 | 0 | E1 | M2-M1 | youtube.com::video_playback |
| 20260918 | vmess | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E1 | M2-M1 | youtube.com::video_playback |
| 20260918 | vmess | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E1 | M2-M1 | youtube.com::video_playback |
| 20260918 | vmess | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E1 | M2-M1 | youtube.com::video_playback |
| 20260919 | anytls | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 0 | E1 | M2-M1 | developer.mozilla.org::document_view |
| 20260919 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 0 | 0 | E1 | M2-M1 | developer.mozilla.org::document_view |
| 20260919 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 0 | E1 | M2-M1 | developer.mozilla.org::document_view |
| 20260919 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 0 | 0 | E1 | M2-M1 | developer.mozilla.org::document_view |
| 20260919 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 0 | 0 | E1 | M2-M1 | developer.mozilla.org::document_view |
| 20260919 | anytls | https://en.wikipedia.org/wiki/Computer_network | 3 | 1 | 0 | E1 | M2-M1 | wikipedia.org::article_view |
| 20260919 | anytls | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 2 | 0 | E1 | M2-M1 | wikipedia.org::article_view |
| 20260919 | anytls | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 1 | 0 | E1 | M2-M1 | wikipedia.org::article_view |
| 20260919 | anytls | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 2 | 0 | E1 | M2-M1 | wikipedia.org::article_view |
| 20260919 | anytls | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E1 | M2-M1 | wikipedia.org::article_view |
| 20260919 | anytls | https://github.com/RakuLomis/TrafficTracer | 2 | 0 | 1 | E1 | M2-M1 | github.com::repository_view |
| 20260919 | anytls | https://github.com/numpy/numpy | 2 | 0 | 0 | E1 | M2-M1 | github.com::repository_view |
| 20260919 | anytls | https://github.com/pallets/flask | 2 | 0 | 0 | E1 | M2-M1 | github.com::repository_view |
| 20260919 | anytls | https://github.com/python/cpython | 2 | 0 | 0 | E1 | M2-M1 | github.com::repository_view |
| 20260919 | anytls | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E1 | M2-M1 | github.com::repository_view |
| 20260919 | anytls | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 0 | E1 | M2-M1 | bing.com::search_results_view |
| 20260919 | anytls | https://www.bing.com/search?q=indoor+plant+care | 0 | 1 | 0 | E1 | M2-M1 | bing.com::search_results_view |
| 20260919 | anytls | https://www.bing.com/search?q=network+traffic+analysis | 0 | 1 | 0 | E1 | M2-M1 | bing.com::search_results_view |
| 20260919 | anytls | https://www.bing.com/search?q=solar+system+facts | 0 | 1 | 0 | E1 | M2-M1 | bing.com::search_results_view |
| 20260919 | anytls | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 1 | E1 | M2-M1 | bing.com::search_results_view |
| 20260919 | anytls | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 1 | 0 | E1 | M2-M1 | youtube.com::search_results_view |
| 20260919 | anytls | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 0 | E1 | M2-M1 | youtube.com::search_results_view |
| 20260919 | anytls | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E1 | M2-M1 | youtube.com::search_results_view |
| 20260919 | anytls | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 0 | E1 | M2-M1 | youtube.com::search_results_view |
| 20260919 | anytls | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E1 | M2-M1 | youtube.com::search_results_view |
| 20260919 | anytls | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E1 | M2-M1 | youtube.com::video_playback |
| 20260919 | anytls | youtube_video:aircAruvnKk | 5 | 0 | 0 | E1 | M2-M1 | youtube.com::video_playback |
| 20260919 | anytls | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E1 | M2-M1 | youtube.com::video_playback |
| 20260919 | anytls | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E1 | M2-M1 | youtube.com::video_playback |
| 20260919 | anytls | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E1 | M2-M1 | youtube.com::video_playback |
| 20260919 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 3 | 0 | E1 | M2-M1 | developer.mozilla.org::document_view |
| 20260919 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 4 | 0 | E1 | M2-M1 | developer.mozilla.org::document_view |
| 20260919 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 4 | 0 | E1 | M2-M1 | developer.mozilla.org::document_view |
| 20260919 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 3 | 0 | E1 | M2-M1 | developer.mozilla.org::document_view |
| 20260919 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 3 | 0 | E1 | M2-M1 | developer.mozilla.org::document_view |
| 20260919 | shadowsocks | https://en.wikipedia.org/wiki/Computer_network | 3 | 3 | 0 | E1 | M2-M1 | wikipedia.org::article_view |
| 20260919 | shadowsocks | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 1 | 0 | E1 | M2-M1 | wikipedia.org::article_view |
| 20260919 | shadowsocks | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 3 | 0 | E1 | M2-M1 | wikipedia.org::article_view |
| 20260919 | shadowsocks | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 0 | E1 | M2-M1 | wikipedia.org::article_view |
| 20260919 | shadowsocks | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 1 | 0 | E1 | M2-M1 | wikipedia.org::article_view |
| 20260919 | shadowsocks | https://github.com/RakuLomis/TrafficTracer | 2 | 1 | 0 | E1 | M2-M1 | github.com::repository_view |
| 20260919 | shadowsocks | https://github.com/numpy/numpy | 2 | 2 | 0 | E1 | M2-M1 | github.com::repository_view |
| 20260919 | shadowsocks | https://github.com/pallets/flask | 2 | 0 | 1 | E1 | M2-M1 | github.com::repository_view |
| 20260919 | shadowsocks | https://github.com/python/cpython | 2 | 0 | 0 | E1 | M2-M1 | github.com::repository_view |
| 20260919 | shadowsocks | https://github.com/scikit-learn/scikit-learn | 2 | 1 | 0 | E1 | M2-M1 | github.com::repository_view |
| 20260919 | shadowsocks | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 3 | 0 | E1 | M2-M1 | bing.com::search_results_view |
| 20260919 | shadowsocks | https://www.bing.com/search?q=indoor+plant+care | 0 | 1 | 0 | E1 | M2-M1 | bing.com::search_results_view |
| 20260919 | shadowsocks | https://www.bing.com/search?q=network+traffic+analysis | 0 | 3 | 0 | E1 | M2-M1 | bing.com::search_results_view |
| 20260919 | shadowsocks | https://www.bing.com/search?q=solar+system+facts | 0 | 3 | 0 | E1 | M2-M1 | bing.com::search_results_view |
| 20260919 | shadowsocks | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 2 | 1 | E1 | M2-M1 | bing.com::search_results_view |
| 20260919 | shadowsocks | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 1 | 1 | E1 | M2-M1 | youtube.com::search_results_view |
| 20260919 | shadowsocks | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 1 | 0 | E1 | M2-M1 | youtube.com::search_results_view |
| 20260919 | shadowsocks | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E1 | M2-M1 | youtube.com::search_results_view |
| 20260919 | shadowsocks | https://www.youtube.com/results?search_query=piano+practice | 4 | 1 | 0 | E1 | M2-M1 | youtube.com::search_results_view |
| 20260919 | shadowsocks | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 1 | 0 | E1 | M2-M1 | youtube.com::search_results_view |
| 20260919 | shadowsocks | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E1 | M2-M1 | youtube.com::video_playback |
| 20260919 | shadowsocks | youtube_video:aircAruvnKk | 5 | 0 | 0 | E1 | M2-M1 | youtube.com::video_playback |
| 20260919 | shadowsocks | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E1 | M2-M1 | youtube.com::video_playback |
| 20260919 | shadowsocks | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E1 | M2-M1 | youtube.com::video_playback |
| 20260919 | shadowsocks | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E1 | M2-M1 | youtube.com::video_playback |
| 20260919 | trojan | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 0 | E1 | M2-M1 | developer.mozilla.org::document_view |
| 20260919 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 0 | 0 | E1 | M2-M1 | developer.mozilla.org::document_view |
| 20260919 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 1 | 0 | E1 | M2-M1 | developer.mozilla.org::document_view |
| 20260919 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 1 | 0 | E1 | M2-M1 | developer.mozilla.org::document_view |
| 20260919 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 1 | 0 | E1 | M2-M1 | developer.mozilla.org::document_view |
| 20260919 | trojan | https://en.wikipedia.org/wiki/Computer_network | 3 | 0 | 0 | E1 | M2-M1 | wikipedia.org::article_view |
| 20260919 | trojan | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 2 | E1 | M2-M1 | wikipedia.org::article_view |
| 20260919 | trojan | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 0 | 0 | E1 | M2-M1 | wikipedia.org::article_view |
| 20260919 | trojan | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 1 | E1 | M2-M1 | wikipedia.org::article_view |
| 20260919 | trojan | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 2 | 0 | E1 | M2-M1 | wikipedia.org::article_view |
| 20260919 | trojan | https://github.com/RakuLomis/TrafficTracer | 2 | 0 | 0 | E1 | M2-M1 | github.com::repository_view |
| 20260919 | trojan | https://github.com/numpy/numpy | 2 | 0 | 0 | E1 | M2-M1 | github.com::repository_view |
| 20260919 | trojan | https://github.com/pallets/flask | 2 | 0 | 0 | E1 | M2-M1 | github.com::repository_view |
| 20260919 | trojan | https://github.com/python/cpython | 2 | 0 | 0 | E1 | M2-M1 | github.com::repository_view |
| 20260919 | trojan | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E1 | M2-M1 | github.com::repository_view |
| 20260919 | trojan | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 1 | 0 | E1 | M2-M1 | bing.com::search_results_view |
| 20260919 | trojan | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 0 | E1 | M2-M1 | bing.com::search_results_view |
| 20260919 | trojan | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E1 | M2-M1 | bing.com::search_results_view |
| 20260919 | trojan | https://www.bing.com/search?q=solar+system+facts | 0 | 0 | 1 | E1 | M2-M1 | bing.com::search_results_view |
| 20260919 | trojan | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 0 | E1 | M2-M1 | bing.com::search_results_view |
| 20260919 | trojan | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E1 | M2-M1 | youtube.com::search_results_view |
| 20260919 | trojan | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 1 | 1 | E1 | M2-M1 | youtube.com::search_results_view |
| 20260919 | trojan | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E1 | M2-M1 | youtube.com::search_results_view |
| 20260919 | trojan | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 0 | E1 | M2-M1 | youtube.com::search_results_view |
| 20260919 | trojan | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 1 | E1 | M2-M1 | youtube.com::search_results_view |
| 20260919 | trojan | youtube_video:R6MlUcmOul8 | 5 | 0 | 1 | E1 | M2-M1 | youtube.com::video_playback |
| 20260919 | trojan | youtube_video:aircAruvnKk | 5 | 0 | 0 | E1 | M2-M1 | youtube.com::video_playback |
| 20260919 | trojan | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E1 | M2-M1 | youtube.com::video_playback |
| 20260919 | trojan | youtube_video:eRsGyueVLvQ | 5 | 0 | 2 | E1 | M2-M1 | youtube.com::video_playback |
| 20260919 | trojan | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E1 | M2-M1 | youtube.com::video_playback |
| 20260919 | vless | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 0 | E1 | M2-M1 | developer.mozilla.org::document_view |
| 20260919 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 0 | 1 | E1 | M2-M1 | developer.mozilla.org::document_view |
| 20260919 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 1 | E1 | M2-M1 | developer.mozilla.org::document_view |
| 20260919 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 1 | 0 | E1 | M2-M1 | developer.mozilla.org::document_view |
| 20260919 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 0 | 0 | E1 | M2-M1 | developer.mozilla.org::document_view |
| 20260919 | vless | https://en.wikipedia.org/wiki/Computer_network | 3 | 1 | 1 | E1 | M2-M1 | wikipedia.org::article_view |
| 20260919 | vless | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 1 | 0 | E1 | M2-M1 | wikipedia.org::article_view |
| 20260919 | vless | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 1 | 0 | E1 | M2-M1 | wikipedia.org::article_view |
| 20260919 | vless | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 0 | E1 | M2-M1 | wikipedia.org::article_view |
| 20260919 | vless | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 1 | 0 | E1 | M2-M1 | wikipedia.org::article_view |
| 20260919 | vless | https://github.com/RakuLomis/TrafficTracer | 2 | 0 | 0 | E1 | M2-M1 | github.com::repository_view |
| 20260919 | vless | https://github.com/numpy/numpy | 2 | 0 | 0 | E1 | M2-M1 | github.com::repository_view |
| 20260919 | vless | https://github.com/pallets/flask | 2 | 1 | 0 | E1 | M2-M1 | github.com::repository_view |
| 20260919 | vless | https://github.com/python/cpython | 2 | 0 | 0 | E1 | M2-M1 | github.com::repository_view |
| 20260919 | vless | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E1 | M2-M1 | github.com::repository_view |
| 20260919 | vless | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 0 | E1 | M2-M1 | bing.com::search_results_view |
| 20260919 | vless | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 0 | E1 | M2-M1 | bing.com::search_results_view |
| 20260919 | vless | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E1 | M2-M1 | bing.com::search_results_view |
| 20260919 | vless | https://www.bing.com/search?q=solar+system+facts | 0 | 0 | 0 | E1 | M2-M1 | bing.com::search_results_view |
| 20260919 | vless | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 0 | E1 | M2-M1 | bing.com::search_results_view |
| 20260919 | vless | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E1 | M2-M1 | youtube.com::search_results_view |
| 20260919 | vless | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 2 | E1 | M2-M1 | youtube.com::search_results_view |
| 20260919 | vless | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 1 | E1 | M2-M1 | youtube.com::search_results_view |
| 20260919 | vless | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 1 | E1 | M2-M1 | youtube.com::search_results_view |
| 20260919 | vless | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E1 | M2-M1 | youtube.com::search_results_view |
| 20260919 | vless | youtube_video:R6MlUcmOul8 | 5 | 0 | 1 | E1 | M2-M1 | youtube.com::video_playback |
| 20260919 | vless | youtube_video:aircAruvnKk | 5 | 1 | 0 | E1 | M2-M1 | youtube.com::video_playback |
| 20260919 | vless | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E1 | M2-M1 | youtube.com::video_playback |
| 20260919 | vless | youtube_video:eRsGyueVLvQ | 5 | 0 | 1 | E1 | M2-M1 | youtube.com::video_playback |
| 20260919 | vless | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E1 | M2-M1 | youtube.com::video_playback |
| 20260919 | vmess | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 0 | E1 | M2-M1 | developer.mozilla.org::document_view |
| 20260919 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 0 | 0 | E1 | M2-M1 | developer.mozilla.org::document_view |
| 20260919 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 0 | E1 | M2-M1 | developer.mozilla.org::document_view |
| 20260919 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 0 | 0 | E1 | M2-M1 | developer.mozilla.org::document_view |
| 20260919 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 2 | 0 | E1 | M2-M1 | developer.mozilla.org::document_view |
| 20260919 | vmess | https://en.wikipedia.org/wiki/Computer_network | 3 | 1 | 0 | E1 | M2-M1 | wikipedia.org::article_view |
| 20260919 | vmess | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 0 | E1 | M2-M1 | wikipedia.org::article_view |
| 20260919 | vmess | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 1 | 0 | E1 | M2-M1 | wikipedia.org::article_view |
| 20260919 | vmess | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 0 | E1 | M2-M1 | wikipedia.org::article_view |
| 20260919 | vmess | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E1 | M2-M1 | wikipedia.org::article_view |
| 20260919 | vmess | https://github.com/RakuLomis/TrafficTracer | 2 | 0 | 0 | E1 | M2-M1 | github.com::repository_view |
| 20260919 | vmess | https://github.com/numpy/numpy | 2 | 0 | 0 | E1 | M2-M1 | github.com::repository_view |
| 20260919 | vmess | https://github.com/pallets/flask | 2 | 1 | 0 | E1 | M2-M1 | github.com::repository_view |
| 20260919 | vmess | https://github.com/python/cpython | 2 | 0 | 0 | E1 | M2-M1 | github.com::repository_view |
| 20260919 | vmess | https://github.com/scikit-learn/scikit-learn | 2 | 1 | 0 | E1 | M2-M1 | github.com::repository_view |
| 20260919 | vmess | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 1 | 0 | E1 | M2-M1 | bing.com::search_results_view |
| 20260919 | vmess | https://www.bing.com/search?q=indoor+plant+care | 0 | 1 | 2 | E1 | M2-M1 | bing.com::search_results_view |
| 20260919 | vmess | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E1 | M2-M1 | bing.com::search_results_view |
| 20260919 | vmess | https://www.bing.com/search?q=solar+system+facts | 0 | 0 | 1 | E1 | M2-M1 | bing.com::search_results_view |
| 20260919 | vmess | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 1 | 0 | E1 | M2-M1 | bing.com::search_results_view |
| 20260919 | vmess | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E1 | M2-M1 | youtube.com::search_results_view |
| 20260919 | vmess | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 0 | E1 | M2-M1 | youtube.com::search_results_view |
| 20260919 | vmess | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E1 | M2-M1 | youtube.com::search_results_view |
| 20260919 | vmess | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 0 | E1 | M2-M1 | youtube.com::search_results_view |
| 20260919 | vmess | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E1 | M2-M1 | youtube.com::search_results_view |
| 20260919 | vmess | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E1 | M2-M1 | youtube.com::video_playback |
| 20260919 | vmess | youtube_video:aircAruvnKk | 5 | 0 | 0 | E1 | M2-M1 | youtube.com::video_playback |
| 20260919 | vmess | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E1 | M2-M1 | youtube.com::video_playback |
| 20260919 | vmess | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E1 | M2-M1 | youtube.com::video_playback |
| 20260919 | vmess | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E1 | M2-M1 | youtube.com::video_playback |
| 20260920 | anytls | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 0 | E1 | M2-M1 | developer.mozilla.org::document_view |
| 20260920 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 0 | 0 | E1 | M2-M1 | developer.mozilla.org::document_view |
| 20260920 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 0 | E1 | M2-M1 | developer.mozilla.org::document_view |
| 20260920 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 0 | 0 | E1 | M2-M1 | developer.mozilla.org::document_view |
| 20260920 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 0 | 0 | E1 | M2-M1 | developer.mozilla.org::document_view |
| 20260920 | anytls | https://en.wikipedia.org/wiki/Computer_network | 3 | 2 | 0 | E1 | M2-M1 | wikipedia.org::article_view |
| 20260920 | anytls | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 2 | 0 | E1 | M2-M1 | wikipedia.org::article_view |
| 20260920 | anytls | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 1 | 0 | E1 | M2-M1 | wikipedia.org::article_view |
| 20260920 | anytls | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 2 | 0 | E1 | M2-M1 | wikipedia.org::article_view |
| 20260920 | anytls | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 1 | 0 | E1 | M2-M1 | wikipedia.org::article_view |
| 20260920 | anytls | https://github.com/RakuLomis/TrafficTracer | 2 | 1 | 0 | E1 | M2-M1 | github.com::repository_view |
| 20260920 | anytls | https://github.com/numpy/numpy | 2 | 0 | 0 | E1 | M2-M1 | github.com::repository_view |
| 20260920 | anytls | https://github.com/pallets/flask | 2 | 0 | 0 | E1 | M2-M1 | github.com::repository_view |
| 20260920 | anytls | https://github.com/python/cpython | 2 | 0 | 0 | E1 | M2-M1 | github.com::repository_view |
| 20260920 | anytls | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E1 | M2-M1 | github.com::repository_view |
| 20260920 | anytls | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 0 | E1 | M2-M1 | bing.com::search_results_view |
| 20260920 | anytls | https://www.bing.com/search?q=indoor+plant+care | 0 | 1 | 0 | E1 | M2-M1 | bing.com::search_results_view |
| 20260920 | anytls | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E1 | M2-M1 | bing.com::search_results_view |
| 20260920 | anytls | https://www.bing.com/search?q=solar+system+facts | 0 | 1 | 0 | E1 | M2-M1 | bing.com::search_results_view |
| 20260920 | anytls | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 1 | E1 | M2-M1 | bing.com::search_results_view |
| 20260920 | anytls | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E1 | M2-M1 | youtube.com::search_results_view |
| 20260920 | anytls | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 0 | E1 | M2-M1 | youtube.com::search_results_view |
| 20260920 | anytls | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E1 | M2-M1 | youtube.com::search_results_view |
| 20260920 | anytls | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 0 | E1 | M2-M1 | youtube.com::search_results_view |
| 20260920 | anytls | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E1 | M2-M1 | youtube.com::search_results_view |
| 20260920 | anytls | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E1 | M2-M1 | youtube.com::video_playback |
| 20260920 | anytls | youtube_video:aircAruvnKk | 5 | 0 | 0 | E1 | M2-M1 | youtube.com::video_playback |
| 20260920 | anytls | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E1 | M2-M1 | youtube.com::video_playback |
| 20260920 | anytls | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E1 | M2-M1 | youtube.com::video_playback |
| 20260920 | anytls | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E1 | M2-M1 | youtube.com::video_playback |
| 20260920 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 4 | 0 | E1 | M2-M1 | developer.mozilla.org::document_view |
| 20260920 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 4 | 0 | E1 | M2-M1 | developer.mozilla.org::document_view |
| 20260920 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 4 | 0 | E1 | M2-M1 | developer.mozilla.org::document_view |
| 20260920 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 3 | 0 | E1 | M2-M1 | developer.mozilla.org::document_view |
| 20260920 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 3 | 0 | E1 | M2-M1 | developer.mozilla.org::document_view |
| 20260920 | shadowsocks | https://en.wikipedia.org/wiki/Computer_network | 3 | 2 | 0 | E1 | M2-M1 | wikipedia.org::article_view |
| 20260920 | shadowsocks | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 0 | E1 | M2-M1 | wikipedia.org::article_view |
| 20260920 | shadowsocks | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 3 | 0 | E1 | M2-M1 | wikipedia.org::article_view |
| 20260920 | shadowsocks | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 0 | E1 | M2-M1 | wikipedia.org::article_view |
| 20260920 | shadowsocks | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 1 | 0 | E1 | M2-M1 | wikipedia.org::article_view |
| 20260920 | shadowsocks | https://github.com/RakuLomis/TrafficTracer | 2 | 0 | 0 | E1 | M2-M1 | github.com::repository_view |
| 20260920 | shadowsocks | https://github.com/numpy/numpy | 2 | 2 | 0 | E1 | M2-M1 | github.com::repository_view |
| 20260920 | shadowsocks | https://github.com/pallets/flask | 2 | 0 | 0 | E1 | M2-M1 | github.com::repository_view |
| 20260920 | shadowsocks | https://github.com/python/cpython | 2 | 0 | 0 | E1 | M2-M1 | github.com::repository_view |
| 20260920 | shadowsocks | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E1 | M2-M1 | github.com::repository_view |
| 20260920 | shadowsocks | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 3 | 0 | E1 | M2-M1 | bing.com::search_results_view |
| 20260920 | shadowsocks | https://www.bing.com/search?q=indoor+plant+care | 0 | 1 | 0 | E1 | M2-M1 | bing.com::search_results_view |
| 20260920 | shadowsocks | https://www.bing.com/search?q=network+traffic+analysis | 0 | 3 | 0 | E1 | M2-M1 | bing.com::search_results_view |
| 20260920 | shadowsocks | https://www.bing.com/search?q=solar+system+facts | 0 | 2 | 0 | E1 | M2-M1 | bing.com::search_results_view |
| 20260920 | shadowsocks | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 2 | 0 | E1 | M2-M1 | bing.com::search_results_view |
| 20260920 | shadowsocks | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 1 | 1 | E1 | M2-M1 | youtube.com::search_results_view |
| 20260920 | shadowsocks | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 0 | E1 | M2-M1 | youtube.com::search_results_view |
| 20260920 | shadowsocks | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E1 | M2-M1 | youtube.com::search_results_view |
| 20260920 | shadowsocks | https://www.youtube.com/results?search_query=piano+practice | 4 | 1 | 0 | E1 | M2-M1 | youtube.com::search_results_view |
| 20260920 | shadowsocks | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 1 | 0 | E1 | M2-M1 | youtube.com::search_results_view |
| 20260920 | shadowsocks | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E1 | M2-M1 | youtube.com::video_playback |
| 20260920 | shadowsocks | youtube_video:aircAruvnKk | 5 | 0 | 0 | E1 | M2-M1 | youtube.com::video_playback |
| 20260920 | shadowsocks | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E1 | M2-M1 | youtube.com::video_playback |
| 20260920 | shadowsocks | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E1 | M2-M1 | youtube.com::video_playback |
| 20260920 | shadowsocks | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E1 | M2-M1 | youtube.com::video_playback |
| 20260920 | trojan | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 0 | E1 | M2-M1 | developer.mozilla.org::document_view |
| 20260920 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 0 | 0 | E1 | M2-M1 | developer.mozilla.org::document_view |
| 20260920 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 1 | 0 | E1 | M2-M1 | developer.mozilla.org::document_view |
| 20260920 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 0 | 0 | E1 | M2-M1 | developer.mozilla.org::document_view |
| 20260920 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 1 | 0 | E1 | M2-M1 | developer.mozilla.org::document_view |
| 20260920 | trojan | https://en.wikipedia.org/wiki/Computer_network | 3 | 0 | 0 | E1 | M2-M1 | wikipedia.org::article_view |
| 20260920 | trojan | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 0 | E1 | M2-M1 | wikipedia.org::article_view |
| 20260920 | trojan | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 0 | 1 | E1 | M2-M1 | wikipedia.org::article_view |
| 20260920 | trojan | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 0 | E1 | M2-M1 | wikipedia.org::article_view |
| 20260920 | trojan | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 2 | 0 | E1 | M2-M1 | wikipedia.org::article_view |
| 20260920 | trojan | https://github.com/RakuLomis/TrafficTracer | 2 | 0 | 0 | E1 | M2-M1 | github.com::repository_view |
| 20260920 | trojan | https://github.com/numpy/numpy | 2 | 0 | 0 | E1 | M2-M1 | github.com::repository_view |
| 20260920 | trojan | https://github.com/pallets/flask | 2 | 0 | 0 | E1 | M2-M1 | github.com::repository_view |
| 20260920 | trojan | https://github.com/python/cpython | 2 | 0 | 0 | E1 | M2-M1 | github.com::repository_view |
| 20260920 | trojan | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E1 | M2-M1 | github.com::repository_view |
| 20260920 | trojan | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 1 | 0 | E1 | M2-M1 | bing.com::search_results_view |
| 20260920 | trojan | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 0 | E1 | M2-M1 | bing.com::search_results_view |
| 20260920 | trojan | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E1 | M2-M1 | bing.com::search_results_view |
| 20260920 | trojan | https://www.bing.com/search?q=solar+system+facts | 0 | 1 | 0 | E1 | M2-M1 | bing.com::search_results_view |
| 20260920 | trojan | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 0 | E1 | M2-M1 | bing.com::search_results_view |
| 20260920 | trojan | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E1 | M2-M1 | youtube.com::search_results_view |
| 20260920 | trojan | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 1 | E1 | M2-M1 | youtube.com::search_results_view |
| 20260920 | trojan | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E1 | M2-M1 | youtube.com::search_results_view |
| 20260920 | trojan | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 0 | E1 | M2-M1 | youtube.com::search_results_view |
| 20260920 | trojan | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 1 | E1 | M2-M1 | youtube.com::search_results_view |
| 20260920 | trojan | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E1 | M2-M1 | youtube.com::video_playback |
| 20260920 | trojan | youtube_video:aircAruvnKk | 5 | 0 | 0 | E1 | M2-M1 | youtube.com::video_playback |
| 20260920 | trojan | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E1 | M2-M1 | youtube.com::video_playback |
| 20260920 | trojan | youtube_video:eRsGyueVLvQ | 5 | 0 | 2 | E1 | M2-M1 | youtube.com::video_playback |
| 20260920 | trojan | youtube_video:sAWK0mgrMp4 | 5 | 0 | 1 | E1 | M2-M1 | youtube.com::video_playback |
| 20260920 | vless | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 0 | E1 | M2-M1 | developer.mozilla.org::document_view |
| 20260920 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 0 | 1 | E1 | M2-M1 | developer.mozilla.org::document_view |
| 20260920 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 0 | E1 | M2-M1 | developer.mozilla.org::document_view |
| 20260920 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 1 | 0 | E1 | M2-M1 | developer.mozilla.org::document_view |
| 20260920 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 0 | 0 | E1 | M2-M1 | developer.mozilla.org::document_view |
| 20260920 | vless | https://en.wikipedia.org/wiki/Computer_network | 3 | 2 | 1 | E1 | M2-M1 | wikipedia.org::article_view |
| 20260920 | vless | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 1 | 0 | E1 | M2-M1 | wikipedia.org::article_view |
| 20260920 | vless | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 1 | 0 | E1 | M2-M1 | wikipedia.org::article_view |
| 20260920 | vless | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 0 | E1 | M2-M1 | wikipedia.org::article_view |
| 20260920 | vless | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 1 | 0 | E1 | M2-M1 | wikipedia.org::article_view |
| 20260920 | vless | https://github.com/RakuLomis/TrafficTracer | 2 | 0 | 0 | E1 | M2-M1 | github.com::repository_view |
| 20260920 | vless | https://github.com/numpy/numpy | 2 | 0 | 0 | E1 | M2-M1 | github.com::repository_view |
| 20260920 | vless | https://github.com/pallets/flask | 2 | 1 | 0 | E1 | M2-M1 | github.com::repository_view |
| 20260920 | vless | https://github.com/python/cpython | 2 | 0 | 0 | E1 | M2-M1 | github.com::repository_view |
| 20260920 | vless | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E1 | M2-M1 | github.com::repository_view |
| 20260920 | vless | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 0 | E1 | M2-M1 | bing.com::search_results_view |
| 20260920 | vless | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 0 | E1 | M2-M1 | bing.com::search_results_view |
| 20260920 | vless | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E1 | M2-M1 | bing.com::search_results_view |
| 20260920 | vless | https://www.bing.com/search?q=solar+system+facts | 0 | 1 | 0 | E1 | M2-M1 | bing.com::search_results_view |
| 20260920 | vless | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 1 | E1 | M2-M1 | bing.com::search_results_view |
| 20260920 | vless | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E1 | M2-M1 | youtube.com::search_results_view |
| 20260920 | vless | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 2 | E1 | M2-M1 | youtube.com::search_results_view |
| 20260920 | vless | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E1 | M2-M1 | youtube.com::search_results_view |
| 20260920 | vless | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 1 | E1 | M2-M1 | youtube.com::search_results_view |
| 20260920 | vless | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E1 | M2-M1 | youtube.com::search_results_view |
| 20260920 | vless | youtube_video:R6MlUcmOul8 | 5 | 0 | 2 | E1 | M2-M1 | youtube.com::video_playback |
| 20260920 | vless | youtube_video:aircAruvnKk | 5 | 0 | 0 | E1 | M2-M1 | youtube.com::video_playback |
| 20260920 | vless | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E1 | M2-M1 | youtube.com::video_playback |
| 20260920 | vless | youtube_video:eRsGyueVLvQ | 5 | 0 | 1 | E1 | M2-M1 | youtube.com::video_playback |
| 20260920 | vless | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E1 | M2-M1 | youtube.com::video_playback |
| 20260920 | vmess | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 0 | E1 | M2-M1 | developer.mozilla.org::document_view |
| 20260920 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 0 | 0 | E1 | M2-M1 | developer.mozilla.org::document_view |
| 20260920 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 0 | E1 | M2-M1 | developer.mozilla.org::document_view |
| 20260920 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 0 | 1 | E1 | M2-M1 | developer.mozilla.org::document_view |
| 20260920 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 2 | 0 | E1 | M2-M1 | developer.mozilla.org::document_view |
| 20260920 | vmess | https://en.wikipedia.org/wiki/Computer_network | 3 | 1 | 0 | E1 | M2-M1 | wikipedia.org::article_view |
| 20260920 | vmess | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 0 | E1 | M2-M1 | wikipedia.org::article_view |
| 20260920 | vmess | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 1 | 0 | E1 | M2-M1 | wikipedia.org::article_view |
| 20260920 | vmess | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 1 | E1 | M2-M1 | wikipedia.org::article_view |
| 20260920 | vmess | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E1 | M2-M1 | wikipedia.org::article_view |
| 20260920 | vmess | https://github.com/RakuLomis/TrafficTracer | 2 | 0 | 0 | E1 | M2-M1 | github.com::repository_view |
| 20260920 | vmess | https://github.com/numpy/numpy | 2 | 0 | 0 | E1 | M2-M1 | github.com::repository_view |
| 20260920 | vmess | https://github.com/pallets/flask | 2 | 0 | 0 | E1 | M2-M1 | github.com::repository_view |
| 20260920 | vmess | https://github.com/python/cpython | 2 | 0 | 0 | E1 | M2-M1 | github.com::repository_view |
| 20260920 | vmess | https://github.com/scikit-learn/scikit-learn | 2 | 1 | 0 | E1 | M2-M1 | github.com::repository_view |
| 20260920 | vmess | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 0 | E1 | M2-M1 | bing.com::search_results_view |
| 20260920 | vmess | https://www.bing.com/search?q=indoor+plant+care | 0 | 1 | 1 | E1 | M2-M1 | bing.com::search_results_view |
| 20260920 | vmess | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E1 | M2-M1 | bing.com::search_results_view |
| 20260920 | vmess | https://www.bing.com/search?q=solar+system+facts | 0 | 0 | 1 | E1 | M2-M1 | bing.com::search_results_view |
| 20260920 | vmess | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 0 | E1 | M2-M1 | bing.com::search_results_view |
| 20260920 | vmess | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E1 | M2-M1 | youtube.com::search_results_view |
| 20260920 | vmess | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 0 | E1 | M2-M1 | youtube.com::search_results_view |
| 20260920 | vmess | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E1 | M2-M1 | youtube.com::search_results_view |
| 20260920 | vmess | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 0 | E1 | M2-M1 | youtube.com::search_results_view |
| 20260920 | vmess | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E1 | M2-M1 | youtube.com::search_results_view |
| 20260920 | vmess | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E1 | M2-M1 | youtube.com::video_playback |
| 20260920 | vmess | youtube_video:aircAruvnKk | 5 | 0 | 0 | E1 | M2-M1 | youtube.com::video_playback |
| 20260920 | vmess | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E1 | M2-M1 | youtube.com::video_playback |
| 20260920 | vmess | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E1 | M2-M1 | youtube.com::video_playback |
| 20260920 | vmess | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E1 | M2-M1 | youtube.com::video_playback |
| 20260918 | anytls | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 0 | E1 | M2-M3 | developer.mozilla.org::document_view |
| 20260918 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 1 | 0 | E1 | M2-M3 | developer.mozilla.org::document_view |
| 20260918 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 1 | 0 | E1 | M2-M3 | developer.mozilla.org::document_view |
| 20260918 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 0 | 0 | E1 | M2-M3 | developer.mozilla.org::document_view |
| 20260918 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 0 | 0 | E1 | M2-M3 | developer.mozilla.org::document_view |
| 20260918 | anytls | https://en.wikipedia.org/wiki/Computer_network | 3 | 1 | 1 | E1 | M2-M3 | wikipedia.org::article_view |
| 20260918 | anytls | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 0 | E1 | M2-M3 | wikipedia.org::article_view |
| 20260918 | anytls | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 0 | 0 | E1 | M2-M3 | wikipedia.org::article_view |
| 20260918 | anytls | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 0 | E1 | M2-M3 | wikipedia.org::article_view |
| 20260918 | anytls | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E1 | M2-M3 | wikipedia.org::article_view |
| 20260918 | anytls | https://github.com/RakuLomis/TrafficTracer | 2 | 1 | 0 | E1 | M2-M3 | github.com::repository_view |
| 20260918 | anytls | https://github.com/numpy/numpy | 2 | 0 | 0 | E1 | M2-M3 | github.com::repository_view |
| 20260918 | anytls | https://github.com/pallets/flask | 2 | 0 | 0 | E1 | M2-M3 | github.com::repository_view |
| 20260918 | anytls | https://github.com/python/cpython | 2 | 1 | 0 | E1 | M2-M3 | github.com::repository_view |
| 20260918 | anytls | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E1 | M2-M3 | github.com::repository_view |
| 20260918 | anytls | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 0 | E1 | M2-M3 | bing.com::search_results_view |
| 20260918 | anytls | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 1 | E1 | M2-M3 | bing.com::search_results_view |
| 20260918 | anytls | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E1 | M2-M3 | bing.com::search_results_view |
| 20260918 | anytls | https://www.bing.com/search?q=solar+system+facts | 0 | 0 | 0 | E1 | M2-M3 | bing.com::search_results_view |
| 20260918 | anytls | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 0 | E1 | M2-M3 | bing.com::search_results_view |
| 20260918 | anytls | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 2 | 0 | E1 | M2-M3 | youtube.com::search_results_view |
| 20260918 | anytls | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 1 | 0 | E1 | M2-M3 | youtube.com::search_results_view |
| 20260918 | anytls | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E1 | M2-M3 | youtube.com::search_results_view |
| 20260918 | anytls | https://www.youtube.com/results?search_query=piano+practice | 4 | 1 | 0 | E1 | M2-M3 | youtube.com::search_results_view |
| 20260918 | anytls | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E1 | M2-M3 | youtube.com::search_results_view |
| 20260918 | anytls | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E1 | M2-M3 | youtube.com::video_playback |
| 20260918 | anytls | youtube_video:aircAruvnKk | 5 | 0 | 0 | E1 | M2-M3 | youtube.com::video_playback |
| 20260918 | anytls | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E1 | M2-M3 | youtube.com::video_playback |
| 20260918 | anytls | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E1 | M2-M3 | youtube.com::video_playback |
| 20260918 | anytls | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E1 | M2-M3 | youtube.com::video_playback |
| 20260918 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 1 | 0 | E1 | M2-M3 | developer.mozilla.org::document_view |
| 20260918 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 0 | 0 | E1 | M2-M3 | developer.mozilla.org::document_view |
| 20260918 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 0 | E1 | M2-M3 | developer.mozilla.org::document_view |
| 20260918 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 0 | 1 | E1 | M2-M3 | developer.mozilla.org::document_view |
| 20260918 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 0 | 0 | E1 | M2-M3 | developer.mozilla.org::document_view |
| 20260918 | shadowsocks | https://en.wikipedia.org/wiki/Computer_network | 3 | 1 | 0 | E1 | M2-M3 | wikipedia.org::article_view |
| 20260918 | shadowsocks | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 0 | E1 | M2-M3 | wikipedia.org::article_view |
| 20260918 | shadowsocks | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 0 | 0 | E1 | M2-M3 | wikipedia.org::article_view |
| 20260918 | shadowsocks | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 0 | E1 | M2-M3 | wikipedia.org::article_view |
| 20260918 | shadowsocks | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 1 | 0 | E1 | M2-M3 | wikipedia.org::article_view |
| 20260918 | shadowsocks | https://github.com/RakuLomis/TrafficTracer | 2 | 1 | 0 | E1 | M2-M3 | github.com::repository_view |
| 20260918 | shadowsocks | https://github.com/numpy/numpy | 2 | 2 | 0 | E1 | M2-M3 | github.com::repository_view |
| 20260918 | shadowsocks | https://github.com/pallets/flask | 2 | 1 | 0 | E1 | M2-M3 | github.com::repository_view |
| 20260918 | shadowsocks | https://github.com/python/cpython | 2 | 0 | 0 | E1 | M2-M3 | github.com::repository_view |
| 20260918 | shadowsocks | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E1 | M2-M3 | github.com::repository_view |
| 20260918 | shadowsocks | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 0 | E1 | M2-M3 | bing.com::search_results_view |
| 20260918 | shadowsocks | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 0 | E1 | M2-M3 | bing.com::search_results_view |
| 20260918 | shadowsocks | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E1 | M2-M3 | bing.com::search_results_view |
| 20260918 | shadowsocks | https://www.bing.com/search?q=solar+system+facts | 0 | 0 | 0 | E1 | M2-M3 | bing.com::search_results_view |
| 20260918 | shadowsocks | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 1 | E1 | M2-M3 | bing.com::search_results_view |
| 20260918 | shadowsocks | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 1 | 0 | E1 | M2-M3 | youtube.com::search_results_view |
| 20260918 | shadowsocks | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 0 | E1 | M2-M3 | youtube.com::search_results_view |
| 20260918 | shadowsocks | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E1 | M2-M3 | youtube.com::search_results_view |
| 20260918 | shadowsocks | https://www.youtube.com/results?search_query=piano+practice | 4 | 1 | 0 | E1 | M2-M3 | youtube.com::search_results_view |
| 20260918 | shadowsocks | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E1 | M2-M3 | youtube.com::search_results_view |
| 20260918 | shadowsocks | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E1 | M2-M3 | youtube.com::video_playback |
| 20260918 | shadowsocks | youtube_video:aircAruvnKk | 5 | 0 | 0 | E1 | M2-M3 | youtube.com::video_playback |
| 20260918 | shadowsocks | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E1 | M2-M3 | youtube.com::video_playback |
| 20260918 | shadowsocks | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E1 | M2-M3 | youtube.com::video_playback |
| 20260918 | shadowsocks | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E1 | M2-M3 | youtube.com::video_playback |
| 20260918 | trojan | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 1 | E1 | M2-M3 | developer.mozilla.org::document_view |
| 20260918 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 1 | 0 | E1 | M2-M3 | developer.mozilla.org::document_view |
| 20260918 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 1 | 0 | E1 | M2-M3 | developer.mozilla.org::document_view |
| 20260918 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 0 | 0 | E1 | M2-M3 | developer.mozilla.org::document_view |
| 20260918 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 2 | 0 | E1 | M2-M3 | developer.mozilla.org::document_view |
| 20260918 | trojan | https://en.wikipedia.org/wiki/Computer_network | 3 | 0 | 0 | E1 | M2-M3 | wikipedia.org::article_view |
| 20260918 | trojan | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 2 | 0 | E1 | M2-M3 | wikipedia.org::article_view |
| 20260918 | trojan | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 1 | 0 | E1 | M2-M3 | wikipedia.org::article_view |
| 20260918 | trojan | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 0 | E1 | M2-M3 | wikipedia.org::article_view |
| 20260918 | trojan | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E1 | M2-M3 | wikipedia.org::article_view |
| 20260918 | trojan | https://github.com/RakuLomis/TrafficTracer | 2 | 2 | 0 | E1 | M2-M3 | github.com::repository_view |
| 20260918 | trojan | https://github.com/numpy/numpy | 2 | 0 | 0 | E1 | M2-M3 | github.com::repository_view |
| 20260918 | trojan | https://github.com/pallets/flask | 2 | 0 | 0 | E1 | M2-M3 | github.com::repository_view |
| 20260918 | trojan | https://github.com/python/cpython | 2 | 0 | 0 | E1 | M2-M3 | github.com::repository_view |
| 20260918 | trojan | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 1 | E1 | M2-M3 | github.com::repository_view |
| 20260918 | trojan | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 1 | 0 | E1 | M2-M3 | bing.com::search_results_view |
| 20260918 | trojan | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 1 | E1 | M2-M3 | bing.com::search_results_view |
| 20260918 | trojan | https://www.bing.com/search?q=network+traffic+analysis | 0 | 1 | 0 | E1 | M2-M3 | bing.com::search_results_view |
| 20260918 | trojan | https://www.bing.com/search?q=solar+system+facts | 0 | 1 | 0 | E1 | M2-M3 | bing.com::search_results_view |
| 20260918 | trojan | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 1 | 0 | E1 | M2-M3 | bing.com::search_results_view |
| 20260918 | trojan | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E1 | M2-M3 | youtube.com::search_results_view |
| 20260918 | trojan | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 0 | E1 | M2-M3 | youtube.com::search_results_view |
| 20260918 | trojan | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E1 | M2-M3 | youtube.com::search_results_view |
| 20260918 | trojan | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 0 | E1 | M2-M3 | youtube.com::search_results_view |
| 20260918 | trojan | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 1 | E1 | M2-M3 | youtube.com::search_results_view |
| 20260918 | trojan | youtube_video:R6MlUcmOul8 | 5 | 0 | 1 | E1 | M2-M3 | youtube.com::video_playback |
| 20260918 | trojan | youtube_video:aircAruvnKk | 5 | 0 | 0 | E1 | M2-M3 | youtube.com::video_playback |
| 20260918 | trojan | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E1 | M2-M3 | youtube.com::video_playback |
| 20260918 | trojan | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E1 | M2-M3 | youtube.com::video_playback |
| 20260918 | trojan | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E1 | M2-M3 | youtube.com::video_playback |
| 20260918 | vless | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 0 | E1 | M2-M3 | developer.mozilla.org::document_view |
| 20260918 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 0 | 0 | E1 | M2-M3 | developer.mozilla.org::document_view |
| 20260918 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 0 | E1 | M2-M3 | developer.mozilla.org::document_view |
| 20260918 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 1 | 0 | E1 | M2-M3 | developer.mozilla.org::document_view |
| 20260918 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 0 | 0 | E1 | M2-M3 | developer.mozilla.org::document_view |
| 20260918 | vless | https://en.wikipedia.org/wiki/Computer_network | 3 | 0 | 2 | E1 | M2-M3 | wikipedia.org::article_view |
| 20260918 | vless | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 0 | E1 | M2-M3 | wikipedia.org::article_view |
| 20260918 | vless | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 0 | 0 | E1 | M2-M3 | wikipedia.org::article_view |
| 20260918 | vless | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 1 | E1 | M2-M3 | wikipedia.org::article_view |
| 20260918 | vless | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 1 | E1 | M2-M3 | wikipedia.org::article_view |
| 20260918 | vless | https://github.com/RakuLomis/TrafficTracer | 2 | 1 | 0 | E1 | M2-M3 | github.com::repository_view |
| 20260918 | vless | https://github.com/numpy/numpy | 2 | 0 | 0 | E1 | M2-M3 | github.com::repository_view |
| 20260918 | vless | https://github.com/pallets/flask | 2 | 1 | 0 | E1 | M2-M3 | github.com::repository_view |
| 20260918 | vless | https://github.com/python/cpython | 2 | 0 | 0 | E1 | M2-M3 | github.com::repository_view |
| 20260918 | vless | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E1 | M2-M3 | github.com::repository_view |
| 20260918 | vless | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 1 | 0 | E1 | M2-M3 | bing.com::search_results_view |
| 20260918 | vless | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 1 | E1 | M2-M3 | bing.com::search_results_view |
| 20260918 | vless | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E1 | M2-M3 | bing.com::search_results_view |
| 20260918 | vless | https://www.bing.com/search?q=solar+system+facts | 0 | 0 | 1 | E1 | M2-M3 | bing.com::search_results_view |
| 20260918 | vless | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 2 | 0 | E1 | M2-M3 | bing.com::search_results_view |
| 20260918 | vless | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E1 | M2-M3 | youtube.com::search_results_view |
| 20260918 | vless | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 2 | E1 | M2-M3 | youtube.com::search_results_view |
| 20260918 | vless | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E1 | M2-M3 | youtube.com::search_results_view |
| 20260918 | vless | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 0 | E1 | M2-M3 | youtube.com::search_results_view |
| 20260918 | vless | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E1 | M2-M3 | youtube.com::search_results_view |
| 20260918 | vless | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E1 | M2-M3 | youtube.com::video_playback |
| 20260918 | vless | youtube_video:aircAruvnKk | 5 | 0 | 0 | E1 | M2-M3 | youtube.com::video_playback |
| 20260918 | vless | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E1 | M2-M3 | youtube.com::video_playback |
| 20260918 | vless | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E1 | M2-M3 | youtube.com::video_playback |
| 20260918 | vless | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E1 | M2-M3 | youtube.com::video_playback |
| 20260918 | vmess | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 0 | E1 | M2-M3 | developer.mozilla.org::document_view |
| 20260918 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 0 | 0 | E1 | M2-M3 | developer.mozilla.org::document_view |
| 20260918 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 0 | E1 | M2-M3 | developer.mozilla.org::document_view |
| 20260918 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 0 | 1 | E1 | M2-M3 | developer.mozilla.org::document_view |
| 20260918 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 0 | 0 | E1 | M2-M3 | developer.mozilla.org::document_view |
| 20260918 | vmess | https://en.wikipedia.org/wiki/Computer_network | 3 | 0 | 0 | E1 | M2-M3 | wikipedia.org::article_view |
| 20260918 | vmess | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 0 | E1 | M2-M3 | wikipedia.org::article_view |
| 20260918 | vmess | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 1 | 0 | E1 | M2-M3 | wikipedia.org::article_view |
| 20260918 | vmess | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 1 | 0 | E1 | M2-M3 | wikipedia.org::article_view |
| 20260918 | vmess | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E1 | M2-M3 | wikipedia.org::article_view |
| 20260918 | vmess | https://github.com/RakuLomis/TrafficTracer | 2 | 1 | 0 | E1 | M2-M3 | github.com::repository_view |
| 20260918 | vmess | https://github.com/numpy/numpy | 2 | 0 | 0 | E1 | M2-M3 | github.com::repository_view |
| 20260918 | vmess | https://github.com/pallets/flask | 2 | 0 | 0 | E1 | M2-M3 | github.com::repository_view |
| 20260918 | vmess | https://github.com/python/cpython | 2 | 0 | 0 | E1 | M2-M3 | github.com::repository_view |
| 20260918 | vmess | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E1 | M2-M3 | github.com::repository_view |
| 20260918 | vmess | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 0 | E1 | M2-M3 | bing.com::search_results_view |
| 20260918 | vmess | https://www.bing.com/search?q=indoor+plant+care | 0 | 1 | 0 | E1 | M2-M3 | bing.com::search_results_view |
| 20260918 | vmess | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E1 | M2-M3 | bing.com::search_results_view |
| 20260918 | vmess | https://www.bing.com/search?q=solar+system+facts | 0 | 0 | 0 | E1 | M2-M3 | bing.com::search_results_view |
| 20260918 | vmess | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 0 | E1 | M2-M3 | bing.com::search_results_view |
| 20260918 | vmess | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E1 | M2-M3 | youtube.com::search_results_view |
| 20260918 | vmess | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 1 | 0 | E1 | M2-M3 | youtube.com::search_results_view |
| 20260918 | vmess | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E1 | M2-M3 | youtube.com::search_results_view |
| 20260918 | vmess | https://www.youtube.com/results?search_query=piano+practice | 4 | 1 | 0 | E1 | M2-M3 | youtube.com::search_results_view |
| 20260918 | vmess | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E1 | M2-M3 | youtube.com::search_results_view |
| 20260918 | vmess | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E1 | M2-M3 | youtube.com::video_playback |
| 20260918 | vmess | youtube_video:aircAruvnKk | 5 | 0 | 0 | E1 | M2-M3 | youtube.com::video_playback |
| 20260918 | vmess | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E1 | M2-M3 | youtube.com::video_playback |
| 20260918 | vmess | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E1 | M2-M3 | youtube.com::video_playback |
| 20260918 | vmess | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E1 | M2-M3 | youtube.com::video_playback |
| 20260919 | anytls | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 0 | E1 | M2-M3 | developer.mozilla.org::document_view |
| 20260919 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 1 | 0 | E1 | M2-M3 | developer.mozilla.org::document_view |
| 20260919 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 1 | 0 | E1 | M2-M3 | developer.mozilla.org::document_view |
| 20260919 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 1 | 0 | E1 | M2-M3 | developer.mozilla.org::document_view |
| 20260919 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 0 | 0 | E1 | M2-M3 | developer.mozilla.org::document_view |
| 20260919 | anytls | https://en.wikipedia.org/wiki/Computer_network | 3 | 0 | 1 | E1 | M2-M3 | wikipedia.org::article_view |
| 20260919 | anytls | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 1 | E1 | M2-M3 | wikipedia.org::article_view |
| 20260919 | anytls | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 0 | 0 | E1 | M2-M3 | wikipedia.org::article_view |
| 20260919 | anytls | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 0 | E1 | M2-M3 | wikipedia.org::article_view |
| 20260919 | anytls | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E1 | M2-M3 | wikipedia.org::article_view |
| 20260919 | anytls | https://github.com/RakuLomis/TrafficTracer | 2 | 0 | 0 | E1 | M2-M3 | github.com::repository_view |
| 20260919 | anytls | https://github.com/numpy/numpy | 2 | 0 | 0 | E1 | M2-M3 | github.com::repository_view |
| 20260919 | anytls | https://github.com/pallets/flask | 2 | 0 | 0 | E1 | M2-M3 | github.com::repository_view |
| 20260919 | anytls | https://github.com/python/cpython | 2 | 1 | 0 | E1 | M2-M3 | github.com::repository_view |
| 20260919 | anytls | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E1 | M2-M3 | github.com::repository_view |
| 20260919 | anytls | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 0 | E1 | M2-M3 | bing.com::search_results_view |
| 20260919 | anytls | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 1 | E1 | M2-M3 | bing.com::search_results_view |
| 20260919 | anytls | https://www.bing.com/search?q=network+traffic+analysis | 0 | 1 | 0 | E1 | M2-M3 | bing.com::search_results_view |
| 20260919 | anytls | https://www.bing.com/search?q=solar+system+facts | 0 | 0 | 0 | E1 | M2-M3 | bing.com::search_results_view |
| 20260919 | anytls | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 0 | E1 | M2-M3 | bing.com::search_results_view |
| 20260919 | anytls | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 1 | 0 | E1 | M2-M3 | youtube.com::search_results_view |
| 20260919 | anytls | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 0 | E1 | M2-M3 | youtube.com::search_results_view |
| 20260919 | anytls | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E1 | M2-M3 | youtube.com::search_results_view |
| 20260919 | anytls | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 0 | E1 | M2-M3 | youtube.com::search_results_view |
| 20260919 | anytls | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E1 | M2-M3 | youtube.com::search_results_view |
| 20260919 | anytls | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E1 | M2-M3 | youtube.com::video_playback |
| 20260919 | anytls | youtube_video:aircAruvnKk | 5 | 0 | 0 | E1 | M2-M3 | youtube.com::video_playback |
| 20260919 | anytls | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E1 | M2-M3 | youtube.com::video_playback |
| 20260919 | anytls | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E1 | M2-M3 | youtube.com::video_playback |
| 20260919 | anytls | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E1 | M2-M3 | youtube.com::video_playback |
| 20260919 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 1 | E1 | M2-M3 | developer.mozilla.org::document_view |
| 20260919 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 0 | 0 | E1 | M2-M3 | developer.mozilla.org::document_view |
| 20260919 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 0 | E1 | M2-M3 | developer.mozilla.org::document_view |
| 20260919 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 0 | 1 | E1 | M2-M3 | developer.mozilla.org::document_view |
| 20260919 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 0 | 0 | E1 | M2-M3 | developer.mozilla.org::document_view |
| 20260919 | shadowsocks | https://en.wikipedia.org/wiki/Computer_network | 3 | 3 | 0 | E1 | M2-M3 | wikipedia.org::article_view |
| 20260919 | shadowsocks | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 1 | 0 | E1 | M2-M3 | wikipedia.org::article_view |
| 20260919 | shadowsocks | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 2 | 0 | E1 | M2-M3 | wikipedia.org::article_view |
| 20260919 | shadowsocks | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 0 | E1 | M2-M3 | wikipedia.org::article_view |
| 20260919 | shadowsocks | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 1 | 0 | E1 | M2-M3 | wikipedia.org::article_view |
| 20260919 | shadowsocks | https://github.com/RakuLomis/TrafficTracer | 2 | 1 | 0 | E1 | M2-M3 | github.com::repository_view |
| 20260919 | shadowsocks | https://github.com/numpy/numpy | 2 | 2 | 0 | E1 | M2-M3 | github.com::repository_view |
| 20260919 | shadowsocks | https://github.com/pallets/flask | 2 | 0 | 0 | E1 | M2-M3 | github.com::repository_view |
| 20260919 | shadowsocks | https://github.com/python/cpython | 2 | 0 | 0 | E1 | M2-M3 | github.com::repository_view |
| 20260919 | shadowsocks | https://github.com/scikit-learn/scikit-learn | 2 | 1 | 0 | E1 | M2-M3 | github.com::repository_view |
| 20260919 | shadowsocks | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 1 | E1 | M2-M3 | bing.com::search_results_view |
| 20260919 | shadowsocks | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 0 | E1 | M2-M3 | bing.com::search_results_view |
| 20260919 | shadowsocks | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E1 | M2-M3 | bing.com::search_results_view |
| 20260919 | shadowsocks | https://www.bing.com/search?q=solar+system+facts | 0 | 0 | 0 | E1 | M2-M3 | bing.com::search_results_view |
| 20260919 | shadowsocks | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 1 | E1 | M2-M3 | bing.com::search_results_view |
| 20260919 | shadowsocks | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E1 | M2-M3 | youtube.com::search_results_view |
| 20260919 | shadowsocks | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 1 | 0 | E1 | M2-M3 | youtube.com::search_results_view |
| 20260919 | shadowsocks | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E1 | M2-M3 | youtube.com::search_results_view |
| 20260919 | shadowsocks | https://www.youtube.com/results?search_query=piano+practice | 4 | 1 | 0 | E1 | M2-M3 | youtube.com::search_results_view |
| 20260919 | shadowsocks | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E1 | M2-M3 | youtube.com::search_results_view |
| 20260919 | shadowsocks | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E1 | M2-M3 | youtube.com::video_playback |
| 20260919 | shadowsocks | youtube_video:aircAruvnKk | 5 | 0 | 0 | E1 | M2-M3 | youtube.com::video_playback |
| 20260919 | shadowsocks | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E1 | M2-M3 | youtube.com::video_playback |
| 20260919 | shadowsocks | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E1 | M2-M3 | youtube.com::video_playback |
| 20260919 | shadowsocks | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E1 | M2-M3 | youtube.com::video_playback |
| 20260919 | trojan | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 1 | E1 | M2-M3 | developer.mozilla.org::document_view |
| 20260919 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 3 | 0 | E1 | M2-M3 | developer.mozilla.org::document_view |
| 20260919 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 0 | E1 | M2-M3 | developer.mozilla.org::document_view |
| 20260919 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 3 | 0 | E1 | M2-M3 | developer.mozilla.org::document_view |
| 20260919 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 1 | 0 | E1 | M2-M3 | developer.mozilla.org::document_view |
| 20260919 | trojan | https://en.wikipedia.org/wiki/Computer_network | 3 | 0 | 0 | E1 | M2-M3 | wikipedia.org::article_view |
| 20260919 | trojan | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 2 | E1 | M2-M3 | wikipedia.org::article_view |
| 20260919 | trojan | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 2 | 0 | E1 | M2-M3 | wikipedia.org::article_view |
| 20260919 | trojan | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 0 | E1 | M2-M3 | wikipedia.org::article_view |
| 20260919 | trojan | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E1 | M2-M3 | wikipedia.org::article_view |
| 20260919 | trojan | https://github.com/RakuLomis/TrafficTracer | 2 | 2 | 0 | E1 | M2-M3 | github.com::repository_view |
| 20260919 | trojan | https://github.com/numpy/numpy | 2 | 0 | 0 | E1 | M2-M3 | github.com::repository_view |
| 20260919 | trojan | https://github.com/pallets/flask | 2 | 1 | 0 | E1 | M2-M3 | github.com::repository_view |
| 20260919 | trojan | https://github.com/python/cpython | 2 | 0 | 0 | E1 | M2-M3 | github.com::repository_view |
| 20260919 | trojan | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 1 | E1 | M2-M3 | github.com::repository_view |
| 20260919 | trojan | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 1 | 0 | E1 | M2-M3 | bing.com::search_results_view |
| 20260919 | trojan | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 0 | E1 | M2-M3 | bing.com::search_results_view |
| 20260919 | trojan | https://www.bing.com/search?q=network+traffic+analysis | 0 | 1 | 0 | E1 | M2-M3 | bing.com::search_results_view |
| 20260919 | trojan | https://www.bing.com/search?q=solar+system+facts | 0 | 1 | 0 | E1 | M2-M3 | bing.com::search_results_view |
| 20260919 | trojan | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 2 | 0 | E1 | M2-M3 | bing.com::search_results_view |
| 20260919 | trojan | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E1 | M2-M3 | youtube.com::search_results_view |
| 20260919 | trojan | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 1 | 0 | E1 | M2-M3 | youtube.com::search_results_view |
| 20260919 | trojan | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E1 | M2-M3 | youtube.com::search_results_view |
| 20260919 | trojan | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 0 | E1 | M2-M3 | youtube.com::search_results_view |
| 20260919 | trojan | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E1 | M2-M3 | youtube.com::search_results_view |
| 20260919 | trojan | youtube_video:R6MlUcmOul8 | 5 | 1 | 1 | E1 | M2-M3 | youtube.com::video_playback |
| 20260919 | trojan | youtube_video:aircAruvnKk | 5 | 0 | 0 | E1 | M2-M3 | youtube.com::video_playback |
| 20260919 | trojan | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E1 | M2-M3 | youtube.com::video_playback |
| 20260919 | trojan | youtube_video:eRsGyueVLvQ | 5 | 0 | 1 | E1 | M2-M3 | youtube.com::video_playback |
| 20260919 | trojan | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E1 | M2-M3 | youtube.com::video_playback |
| 20260919 | vless | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 0 | E1 | M2-M3 | developer.mozilla.org::document_view |
| 20260919 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 3 | 0 | E1 | M2-M3 | developer.mozilla.org::document_view |
| 20260919 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 1 | 0 | E1 | M2-M3 | developer.mozilla.org::document_view |
| 20260919 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 3 | 0 | E1 | M2-M3 | developer.mozilla.org::document_view |
| 20260919 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 2 | 0 | E1 | M2-M3 | developer.mozilla.org::document_view |
| 20260919 | vless | https://en.wikipedia.org/wiki/Computer_network | 3 | 0 | 0 | E1 | M2-M3 | wikipedia.org::article_view |
| 20260919 | vless | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 2 | E1 | M2-M3 | wikipedia.org::article_view |
| 20260919 | vless | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 0 | 0 | E1 | M2-M3 | wikipedia.org::article_view |
| 20260919 | vless | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 0 | E1 | M2-M3 | wikipedia.org::article_view |
| 20260919 | vless | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 1 | E1 | M2-M3 | wikipedia.org::article_view |
| 20260919 | vless | https://github.com/RakuLomis/TrafficTracer | 2 | 2 | 1 | E1 | M2-M3 | github.com::repository_view |
| 20260919 | vless | https://github.com/numpy/numpy | 2 | 0 | 0 | E1 | M2-M3 | github.com::repository_view |
| 20260919 | vless | https://github.com/pallets/flask | 2 | 0 | 0 | E1 | M2-M3 | github.com::repository_view |
| 20260919 | vless | https://github.com/python/cpython | 2 | 0 | 0 | E1 | M2-M3 | github.com::repository_view |
| 20260919 | vless | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E1 | M2-M3 | github.com::repository_view |
| 20260919 | vless | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 1 | 0 | E1 | M2-M3 | bing.com::search_results_view |
| 20260919 | vless | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 0 | E1 | M2-M3 | bing.com::search_results_view |
| 20260919 | vless | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E1 | M2-M3 | bing.com::search_results_view |
| 20260919 | vless | https://www.bing.com/search?q=solar+system+facts | 0 | 0 | 0 | E1 | M2-M3 | bing.com::search_results_view |
| 20260919 | vless | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 0 | E1 | M2-M3 | bing.com::search_results_view |
| 20260919 | vless | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E1 | M2-M3 | youtube.com::search_results_view |
| 20260919 | vless | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 1 | 1 | E1 | M2-M3 | youtube.com::search_results_view |
| 20260919 | vless | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E1 | M2-M3 | youtube.com::search_results_view |
| 20260919 | vless | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 0 | E1 | M2-M3 | youtube.com::search_results_view |
| 20260919 | vless | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E1 | M2-M3 | youtube.com::search_results_view |
| 20260919 | vless | youtube_video:R6MlUcmOul8 | 5 | 0 | 1 | E1 | M2-M3 | youtube.com::video_playback |
| 20260919 | vless | youtube_video:aircAruvnKk | 5 | 1 | 0 | E1 | M2-M3 | youtube.com::video_playback |
| 20260919 | vless | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E1 | M2-M3 | youtube.com::video_playback |
| 20260919 | vless | youtube_video:eRsGyueVLvQ | 5 | 0 | 1 | E1 | M2-M3 | youtube.com::video_playback |
| 20260919 | vless | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E1 | M2-M3 | youtube.com::video_playback |
| 20260919 | vmess | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 0 | E1 | M2-M3 | developer.mozilla.org::document_view |
| 20260919 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 0 | 0 | E1 | M2-M3 | developer.mozilla.org::document_view |
| 20260919 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 0 | E1 | M2-M3 | developer.mozilla.org::document_view |
| 20260919 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 0 | 0 | E1 | M2-M3 | developer.mozilla.org::document_view |
| 20260919 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 0 | 0 | E1 | M2-M3 | developer.mozilla.org::document_view |
| 20260919 | vmess | https://en.wikipedia.org/wiki/Computer_network | 3 | 0 | 0 | E1 | M2-M3 | wikipedia.org::article_view |
| 20260919 | vmess | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 0 | E1 | M2-M3 | wikipedia.org::article_view |
| 20260919 | vmess | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 1 | 0 | E1 | M2-M3 | wikipedia.org::article_view |
| 20260919 | vmess | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 0 | E1 | M2-M3 | wikipedia.org::article_view |
| 20260919 | vmess | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E1 | M2-M3 | wikipedia.org::article_view |
| 20260919 | vmess | https://github.com/RakuLomis/TrafficTracer | 2 | 1 | 0 | E1 | M2-M3 | github.com::repository_view |
| 20260919 | vmess | https://github.com/numpy/numpy | 2 | 0 | 0 | E1 | M2-M3 | github.com::repository_view |
| 20260919 | vmess | https://github.com/pallets/flask | 2 | 0 | 0 | E1 | M2-M3 | github.com::repository_view |
| 20260919 | vmess | https://github.com/python/cpython | 2 | 0 | 0 | E1 | M2-M3 | github.com::repository_view |
| 20260919 | vmess | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E1 | M2-M3 | github.com::repository_view |
| 20260919 | vmess | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 0 | E1 | M2-M3 | bing.com::search_results_view |
| 20260919 | vmess | https://www.bing.com/search?q=indoor+plant+care | 0 | 1 | 0 | E1 | M2-M3 | bing.com::search_results_view |
| 20260919 | vmess | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E1 | M2-M3 | bing.com::search_results_view |
| 20260919 | vmess | https://www.bing.com/search?q=solar+system+facts | 0 | 1 | 0 | E1 | M2-M3 | bing.com::search_results_view |
| 20260919 | vmess | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 0 | E1 | M2-M3 | bing.com::search_results_view |
| 20260919 | vmess | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E1 | M2-M3 | youtube.com::search_results_view |
| 20260919 | vmess | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 1 | 0 | E1 | M2-M3 | youtube.com::search_results_view |
| 20260919 | vmess | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E1 | M2-M3 | youtube.com::search_results_view |
| 20260919 | vmess | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 0 | E1 | M2-M3 | youtube.com::search_results_view |
| 20260919 | vmess | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E1 | M2-M3 | youtube.com::search_results_view |
| 20260919 | vmess | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E1 | M2-M3 | youtube.com::video_playback |
| 20260919 | vmess | youtube_video:aircAruvnKk | 5 | 0 | 0 | E1 | M2-M3 | youtube.com::video_playback |
| 20260919 | vmess | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E1 | M2-M3 | youtube.com::video_playback |
| 20260919 | vmess | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E1 | M2-M3 | youtube.com::video_playback |
| 20260919 | vmess | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E1 | M2-M3 | youtube.com::video_playback |
| 20260920 | anytls | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 3 | 0 | E1 | M2-M3 | developer.mozilla.org::document_view |
| 20260920 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 1 | 0 | E1 | M2-M3 | developer.mozilla.org::document_view |
| 20260920 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 1 | 0 | E1 | M2-M3 | developer.mozilla.org::document_view |
| 20260920 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 2 | 0 | E1 | M2-M3 | developer.mozilla.org::document_view |
| 20260920 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 0 | 0 | E1 | M2-M3 | developer.mozilla.org::document_view |
| 20260920 | anytls | https://en.wikipedia.org/wiki/Computer_network | 3 | 1 | 0 | E1 | M2-M3 | wikipedia.org::article_view |
| 20260920 | anytls | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 1 | E1 | M2-M3 | wikipedia.org::article_view |
| 20260920 | anytls | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 0 | 1 | E1 | M2-M3 | wikipedia.org::article_view |
| 20260920 | anytls | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 1 | 0 | E1 | M2-M3 | wikipedia.org::article_view |
| 20260920 | anytls | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E1 | M2-M3 | wikipedia.org::article_view |
| 20260920 | anytls | https://github.com/RakuLomis/TrafficTracer | 2 | 1 | 0 | E1 | M2-M3 | github.com::repository_view |
| 20260920 | anytls | https://github.com/numpy/numpy | 2 | 0 | 0 | E1 | M2-M3 | github.com::repository_view |
| 20260920 | anytls | https://github.com/pallets/flask | 2 | 0 | 1 | E1 | M2-M3 | github.com::repository_view |
| 20260920 | anytls | https://github.com/python/cpython | 2 | 1 | 0 | E1 | M2-M3 | github.com::repository_view |
| 20260920 | anytls | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E1 | M2-M3 | github.com::repository_view |
| 20260920 | anytls | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 0 | E1 | M2-M3 | bing.com::search_results_view |
| 20260920 | anytls | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 1 | E1 | M2-M3 | bing.com::search_results_view |
| 20260920 | anytls | https://www.bing.com/search?q=network+traffic+analysis | 0 | 1 | 0 | E1 | M2-M3 | bing.com::search_results_view |
| 20260920 | anytls | https://www.bing.com/search?q=solar+system+facts | 0 | 0 | 0 | E1 | M2-M3 | bing.com::search_results_view |
| 20260920 | anytls | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 0 | E1 | M2-M3 | bing.com::search_results_view |
| 20260920 | anytls | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E1 | M2-M3 | youtube.com::search_results_view |
| 20260920 | anytls | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 0 | E1 | M2-M3 | youtube.com::search_results_view |
| 20260920 | anytls | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E1 | M2-M3 | youtube.com::search_results_view |
| 20260920 | anytls | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 1 | E1 | M2-M3 | youtube.com::search_results_view |
| 20260920 | anytls | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E1 | M2-M3 | youtube.com::search_results_view |
| 20260920 | anytls | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E1 | M2-M3 | youtube.com::video_playback |
| 20260920 | anytls | youtube_video:aircAruvnKk | 5 | 0 | 0 | E1 | M2-M3 | youtube.com::video_playback |
| 20260920 | anytls | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E1 | M2-M3 | youtube.com::video_playback |
| 20260920 | anytls | youtube_video:eRsGyueVLvQ | 5 | 1 | 0 | E1 | M2-M3 | youtube.com::video_playback |
| 20260920 | anytls | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E1 | M2-M3 | youtube.com::video_playback |
| 20260920 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 0 | E1 | M2-M3 | developer.mozilla.org::document_view |
| 20260920 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 0 | 0 | E1 | M2-M3 | developer.mozilla.org::document_view |
| 20260920 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 0 | E1 | M2-M3 | developer.mozilla.org::document_view |
| 20260920 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 0 | 1 | E1 | M2-M3 | developer.mozilla.org::document_view |
| 20260920 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 0 | 0 | E1 | M2-M3 | developer.mozilla.org::document_view |
| 20260920 | shadowsocks | https://en.wikipedia.org/wiki/Computer_network | 3 | 2 | 0 | E1 | M2-M3 | wikipedia.org::article_view |
| 20260920 | shadowsocks | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 0 | E1 | M2-M3 | wikipedia.org::article_view |
| 20260920 | shadowsocks | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 3 | 0 | E1 | M2-M3 | wikipedia.org::article_view |
| 20260920 | shadowsocks | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 0 | E1 | M2-M3 | wikipedia.org::article_view |
| 20260920 | shadowsocks | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 1 | 0 | E1 | M2-M3 | wikipedia.org::article_view |
| 20260920 | shadowsocks | https://github.com/RakuLomis/TrafficTracer | 2 | 2 | 0 | E1 | M2-M3 | github.com::repository_view |
| 20260920 | shadowsocks | https://github.com/numpy/numpy | 2 | 1 | 0 | E1 | M2-M3 | github.com::repository_view |
| 20260920 | shadowsocks | https://github.com/pallets/flask | 2 | 1 | 0 | E1 | M2-M3 | github.com::repository_view |
| 20260920 | shadowsocks | https://github.com/python/cpython | 2 | 0 | 0 | E1 | M2-M3 | github.com::repository_view |
| 20260920 | shadowsocks | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E1 | M2-M3 | github.com::repository_view |
| 20260920 | shadowsocks | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 0 | E1 | M2-M3 | bing.com::search_results_view |
| 20260920 | shadowsocks | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 0 | E1 | M2-M3 | bing.com::search_results_view |
| 20260920 | shadowsocks | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E1 | M2-M3 | bing.com::search_results_view |
| 20260920 | shadowsocks | https://www.bing.com/search?q=solar+system+facts | 0 | 0 | 1 | E1 | M2-M3 | bing.com::search_results_view |
| 20260920 | shadowsocks | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 1 | 0 | E1 | M2-M3 | bing.com::search_results_view |
| 20260920 | shadowsocks | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 1 | 0 | E1 | M2-M3 | youtube.com::search_results_view |
| 20260920 | shadowsocks | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 0 | E1 | M2-M3 | youtube.com::search_results_view |
| 20260920 | shadowsocks | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E1 | M2-M3 | youtube.com::search_results_view |
| 20260920 | shadowsocks | https://www.youtube.com/results?search_query=piano+practice | 4 | 1 | 0 | E1 | M2-M3 | youtube.com::search_results_view |
| 20260920 | shadowsocks | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E1 | M2-M3 | youtube.com::search_results_view |
| 20260920 | shadowsocks | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E1 | M2-M3 | youtube.com::video_playback |
| 20260920 | shadowsocks | youtube_video:aircAruvnKk | 5 | 0 | 0 | E1 | M2-M3 | youtube.com::video_playback |
| 20260920 | shadowsocks | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E1 | M2-M3 | youtube.com::video_playback |
| 20260920 | shadowsocks | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E1 | M2-M3 | youtube.com::video_playback |
| 20260920 | shadowsocks | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E1 | M2-M3 | youtube.com::video_playback |
| 20260920 | trojan | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 1 | E1 | M2-M3 | developer.mozilla.org::document_view |
| 20260920 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 3 | 0 | E1 | M2-M3 | developer.mozilla.org::document_view |
| 20260920 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 0 | E1 | M2-M3 | developer.mozilla.org::document_view |
| 20260920 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 0 | 0 | E1 | M2-M3 | developer.mozilla.org::document_view |
| 20260920 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 0 | 0 | E1 | M2-M3 | developer.mozilla.org::document_view |
| 20260920 | trojan | https://en.wikipedia.org/wiki/Computer_network | 3 | 0 | 0 | E1 | M2-M3 | wikipedia.org::article_view |
| 20260920 | trojan | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 3 | 1 | E1 | M2-M3 | wikipedia.org::article_view |
| 20260920 | trojan | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 1 | 0 | E1 | M2-M3 | wikipedia.org::article_view |
| 20260920 | trojan | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 2 | 0 | E1 | M2-M3 | wikipedia.org::article_view |
| 20260920 | trojan | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E1 | M2-M3 | wikipedia.org::article_view |
| 20260920 | trojan | https://github.com/RakuLomis/TrafficTracer | 2 | 2 | 0 | E1 | M2-M3 | github.com::repository_view |
| 20260920 | trojan | https://github.com/numpy/numpy | 2 | 0 | 0 | E1 | M2-M3 | github.com::repository_view |
| 20260920 | trojan | https://github.com/pallets/flask | 2 | 0 | 1 | E1 | M2-M3 | github.com::repository_view |
| 20260920 | trojan | https://github.com/python/cpython | 2 | 0 | 0 | E1 | M2-M3 | github.com::repository_view |
| 20260920 | trojan | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 1 | E1 | M2-M3 | github.com::repository_view |
| 20260920 | trojan | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 2 | 0 | E1 | M2-M3 | bing.com::search_results_view |
| 20260920 | trojan | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 0 | E1 | M2-M3 | bing.com::search_results_view |
| 20260920 | trojan | https://www.bing.com/search?q=network+traffic+analysis | 0 | 1 | 0 | E1 | M2-M3 | bing.com::search_results_view |
| 20260920 | trojan | https://www.bing.com/search?q=solar+system+facts | 0 | 4 | 0 | E1 | M2-M3 | bing.com::search_results_view |
| 20260920 | trojan | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 1 | 0 | E1 | M2-M3 | bing.com::search_results_view |
| 20260920 | trojan | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E1 | M2-M3 | youtube.com::search_results_view |
| 20260920 | trojan | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 0 | E1 | M2-M3 | youtube.com::search_results_view |
| 20260920 | trojan | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E1 | M2-M3 | youtube.com::search_results_view |
| 20260920 | trojan | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 1 | E1 | M2-M3 | youtube.com::search_results_view |
| 20260920 | trojan | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E1 | M2-M3 | youtube.com::search_results_view |
| 20260920 | trojan | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E1 | M2-M3 | youtube.com::video_playback |
| 20260920 | trojan | youtube_video:aircAruvnKk | 5 | 0 | 0 | E1 | M2-M3 | youtube.com::video_playback |
| 20260920 | trojan | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E1 | M2-M3 | youtube.com::video_playback |
| 20260920 | trojan | youtube_video:eRsGyueVLvQ | 5 | 0 | 1 | E1 | M2-M3 | youtube.com::video_playback |
| 20260920 | trojan | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E1 | M2-M3 | youtube.com::video_playback |
| 20260920 | vless | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 0 | E1 | M2-M3 | developer.mozilla.org::document_view |
| 20260920 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 3 | 0 | E1 | M2-M3 | developer.mozilla.org::document_view |
| 20260920 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 2 | 0 | E1 | M2-M3 | developer.mozilla.org::document_view |
| 20260920 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 1 | 0 | E1 | M2-M3 | developer.mozilla.org::document_view |
| 20260920 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 0 | 0 | E1 | M2-M3 | developer.mozilla.org::document_view |
| 20260920 | vless | https://en.wikipedia.org/wiki/Computer_network | 3 | 0 | 0 | E1 | M2-M3 | wikipedia.org::article_view |
| 20260920 | vless | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 1 | E1 | M2-M3 | wikipedia.org::article_view |
| 20260920 | vless | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 1 | 0 | E1 | M2-M3 | wikipedia.org::article_view |
| 20260920 | vless | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 0 | E1 | M2-M3 | wikipedia.org::article_view |
| 20260920 | vless | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 1 | E1 | M2-M3 | wikipedia.org::article_view |
| 20260920 | vless | https://github.com/RakuLomis/TrafficTracer | 2 | 2 | 1 | E1 | M2-M3 | github.com::repository_view |
| 20260920 | vless | https://github.com/numpy/numpy | 2 | 0 | 0 | E1 | M2-M3 | github.com::repository_view |
| 20260920 | vless | https://github.com/pallets/flask | 2 | 1 | 0 | E1 | M2-M3 | github.com::repository_view |
| 20260920 | vless | https://github.com/python/cpython | 2 | 0 | 0 | E1 | M2-M3 | github.com::repository_view |
| 20260920 | vless | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E1 | M2-M3 | github.com::repository_view |
| 20260920 | vless | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 1 | 0 | E1 | M2-M3 | bing.com::search_results_view |
| 20260920 | vless | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 0 | E1 | M2-M3 | bing.com::search_results_view |
| 20260920 | vless | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E1 | M2-M3 | bing.com::search_results_view |
| 20260920 | vless | https://www.bing.com/search?q=solar+system+facts | 0 | 1 | 0 | E1 | M2-M3 | bing.com::search_results_view |
| 20260920 | vless | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 1 | E1 | M2-M3 | bing.com::search_results_view |
| 20260920 | vless | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E1 | M2-M3 | youtube.com::search_results_view |
| 20260920 | vless | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 1 | E1 | M2-M3 | youtube.com::search_results_view |
| 20260920 | vless | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E1 | M2-M3 | youtube.com::search_results_view |
| 20260920 | vless | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 0 | E1 | M2-M3 | youtube.com::search_results_view |
| 20260920 | vless | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E1 | M2-M3 | youtube.com::search_results_view |
| 20260920 | vless | youtube_video:R6MlUcmOul8 | 5 | 0 | 1 | E1 | M2-M3 | youtube.com::video_playback |
| 20260920 | vless | youtube_video:aircAruvnKk | 5 | 0 | 1 | E1 | M2-M3 | youtube.com::video_playback |
| 20260920 | vless | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E1 | M2-M3 | youtube.com::video_playback |
| 20260920 | vless | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E1 | M2-M3 | youtube.com::video_playback |
| 20260920 | vless | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E1 | M2-M3 | youtube.com::video_playback |
| 20260920 | vmess | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 0 | E1 | M2-M3 | developer.mozilla.org::document_view |
| 20260920 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 2 | 0 | E1 | M2-M3 | developer.mozilla.org::document_view |
| 20260920 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 0 | E1 | M2-M3 | developer.mozilla.org::document_view |
| 20260920 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 0 | 0 | E1 | M2-M3 | developer.mozilla.org::document_view |
| 20260920 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 0 | 0 | E1 | M2-M3 | developer.mozilla.org::document_view |
| 20260920 | vmess | https://en.wikipedia.org/wiki/Computer_network | 3 | 0 | 0 | E1 | M2-M3 | wikipedia.org::article_view |
| 20260920 | vmess | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 1 | E1 | M2-M3 | wikipedia.org::article_view |
| 20260920 | vmess | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 0 | 0 | E1 | M2-M3 | wikipedia.org::article_view |
| 20260920 | vmess | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 1 | 0 | E1 | M2-M3 | wikipedia.org::article_view |
| 20260920 | vmess | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 2 | E1 | M2-M3 | wikipedia.org::article_view |
| 20260920 | vmess | https://github.com/RakuLomis/TrafficTracer | 2 | 1 | 0 | E1 | M2-M3 | github.com::repository_view |
| 20260920 | vmess | https://github.com/numpy/numpy | 2 | 0 | 0 | E1 | M2-M3 | github.com::repository_view |
| 20260920 | vmess | https://github.com/pallets/flask | 2 | 0 | 1 | E1 | M2-M3 | github.com::repository_view |
| 20260920 | vmess | https://github.com/python/cpython | 2 | 0 | 0 | E1 | M2-M3 | github.com::repository_view |
| 20260920 | vmess | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E1 | M2-M3 | github.com::repository_view |
| 20260920 | vmess | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 1 | 0 | E1 | M2-M3 | bing.com::search_results_view |
| 20260920 | vmess | https://www.bing.com/search?q=indoor+plant+care | 0 | 1 | 0 | E1 | M2-M3 | bing.com::search_results_view |
| 20260920 | vmess | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E1 | M2-M3 | bing.com::search_results_view |
| 20260920 | vmess | https://www.bing.com/search?q=solar+system+facts | 0 | 0 | 0 | E1 | M2-M3 | bing.com::search_results_view |
| 20260920 | vmess | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 0 | E1 | M2-M3 | bing.com::search_results_view |
| 20260920 | vmess | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E1 | M2-M3 | youtube.com::search_results_view |
| 20260920 | vmess | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 1 | 0 | E1 | M2-M3 | youtube.com::search_results_view |
| 20260920 | vmess | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E1 | M2-M3 | youtube.com::search_results_view |
| 20260920 | vmess | https://www.youtube.com/results?search_query=piano+practice | 4 | 1 | 0 | E1 | M2-M3 | youtube.com::search_results_view |
| 20260920 | vmess | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E1 | M2-M3 | youtube.com::search_results_view |
| 20260920 | vmess | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E1 | M2-M3 | youtube.com::video_playback |
| 20260920 | vmess | youtube_video:aircAruvnKk | 5 | 0 | 0 | E1 | M2-M3 | youtube.com::video_playback |
| 20260920 | vmess | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E1 | M2-M3 | youtube.com::video_playback |
| 20260920 | vmess | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E1 | M2-M3 | youtube.com::video_playback |
| 20260920 | vmess | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E1 | M2-M3 | youtube.com::video_playback |
| 20260918 | anytls | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 0 | E1 | M2-M4 | developer.mozilla.org::document_view |
| 20260918 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 1 | 0 | E1 | M2-M4 | developer.mozilla.org::document_view |
| 20260918 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 0 | E1 | M2-M4 | developer.mozilla.org::document_view |
| 20260918 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 1 | 0 | E1 | M2-M4 | developer.mozilla.org::document_view |
| 20260918 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 1 | 0 | E1 | M2-M4 | developer.mozilla.org::document_view |
| 20260918 | anytls | https://en.wikipedia.org/wiki/Computer_network | 3 | 1 | 0 | E1 | M2-M4 | wikipedia.org::article_view |
| 20260918 | anytls | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 0 | E1 | M2-M4 | wikipedia.org::article_view |
| 20260918 | anytls | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 0 | 0 | E1 | M2-M4 | wikipedia.org::article_view |
| 20260918 | anytls | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 0 | E1 | M2-M4 | wikipedia.org::article_view |
| 20260918 | anytls | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E1 | M2-M4 | wikipedia.org::article_view |
| 20260918 | anytls | https://github.com/RakuLomis/TrafficTracer | 2 | 1 | 0 | E1 | M2-M4 | github.com::repository_view |
| 20260918 | anytls | https://github.com/numpy/numpy | 2 | 0 | 0 | E1 | M2-M4 | github.com::repository_view |
| 20260918 | anytls | https://github.com/pallets/flask | 2 | 0 | 0 | E1 | M2-M4 | github.com::repository_view |
| 20260918 | anytls | https://github.com/python/cpython | 2 | 1 | 0 | E1 | M2-M4 | github.com::repository_view |
| 20260918 | anytls | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E1 | M2-M4 | github.com::repository_view |
| 20260918 | anytls | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 0 | E1 | M2-M4 | bing.com::search_results_view |
| 20260918 | anytls | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 1 | E1 | M2-M4 | bing.com::search_results_view |
| 20260918 | anytls | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E1 | M2-M4 | bing.com::search_results_view |
| 20260918 | anytls | https://www.bing.com/search?q=solar+system+facts | 0 | 0 | 0 | E1 | M2-M4 | bing.com::search_results_view |
| 20260918 | anytls | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 0 | E1 | M2-M4 | bing.com::search_results_view |
| 20260918 | anytls | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 2 | 0 | E1 | M2-M4 | youtube.com::search_results_view |
| 20260918 | anytls | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 0 | E1 | M2-M4 | youtube.com::search_results_view |
| 20260918 | anytls | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E1 | M2-M4 | youtube.com::search_results_view |
| 20260918 | anytls | https://www.youtube.com/results?search_query=piano+practice | 4 | 1 | 0 | E1 | M2-M4 | youtube.com::search_results_view |
| 20260918 | anytls | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E1 | M2-M4 | youtube.com::search_results_view |
| 20260918 | anytls | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E1 | M2-M4 | youtube.com::video_playback |
| 20260918 | anytls | youtube_video:aircAruvnKk | 5 | 0 | 0 | E1 | M2-M4 | youtube.com::video_playback |
| 20260918 | anytls | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E1 | M2-M4 | youtube.com::video_playback |
| 20260918 | anytls | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E1 | M2-M4 | youtube.com::video_playback |
| 20260918 | anytls | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E1 | M2-M4 | youtube.com::video_playback |
| 20260918 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 1 | 0 | E1 | M2-M4 | developer.mozilla.org::document_view |
| 20260918 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 0 | 0 | E1 | M2-M4 | developer.mozilla.org::document_view |
| 20260918 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 0 | E1 | M2-M4 | developer.mozilla.org::document_view |
| 20260918 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 0 | 1 | E1 | M2-M4 | developer.mozilla.org::document_view |
| 20260918 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 0 | 0 | E1 | M2-M4 | developer.mozilla.org::document_view |
| 20260918 | shadowsocks | https://en.wikipedia.org/wiki/Computer_network | 3 | 1 | 0 | E1 | M2-M4 | wikipedia.org::article_view |
| 20260918 | shadowsocks | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 0 | E1 | M2-M4 | wikipedia.org::article_view |
| 20260918 | shadowsocks | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 0 | 0 | E1 | M2-M4 | wikipedia.org::article_view |
| 20260918 | shadowsocks | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 0 | E1 | M2-M4 | wikipedia.org::article_view |
| 20260918 | shadowsocks | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 1 | 0 | E1 | M2-M4 | wikipedia.org::article_view |
| 20260918 | shadowsocks | https://github.com/RakuLomis/TrafficTracer | 2 | 1 | 0 | E1 | M2-M4 | github.com::repository_view |
| 20260918 | shadowsocks | https://github.com/numpy/numpy | 2 | 2 | 0 | E1 | M2-M4 | github.com::repository_view |
| 20260918 | shadowsocks | https://github.com/pallets/flask | 2 | 1 | 0 | E1 | M2-M4 | github.com::repository_view |
| 20260918 | shadowsocks | https://github.com/python/cpython | 2 | 0 | 0 | E1 | M2-M4 | github.com::repository_view |
| 20260918 | shadowsocks | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E1 | M2-M4 | github.com::repository_view |
| 20260918 | shadowsocks | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 0 | E1 | M2-M4 | bing.com::search_results_view |
| 20260918 | shadowsocks | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 0 | E1 | M2-M4 | bing.com::search_results_view |
| 20260918 | shadowsocks | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E1 | M2-M4 | bing.com::search_results_view |
| 20260918 | shadowsocks | https://www.bing.com/search?q=solar+system+facts | 0 | 0 | 0 | E1 | M2-M4 | bing.com::search_results_view |
| 20260918 | shadowsocks | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 0 | E1 | M2-M4 | bing.com::search_results_view |
| 20260918 | shadowsocks | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 1 | 0 | E1 | M2-M4 | youtube.com::search_results_view |
| 20260918 | shadowsocks | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 0 | E1 | M2-M4 | youtube.com::search_results_view |
| 20260918 | shadowsocks | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E1 | M2-M4 | youtube.com::search_results_view |
| 20260918 | shadowsocks | https://www.youtube.com/results?search_query=piano+practice | 4 | 1 | 0 | E1 | M2-M4 | youtube.com::search_results_view |
| 20260918 | shadowsocks | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E1 | M2-M4 | youtube.com::search_results_view |
| 20260918 | shadowsocks | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E1 | M2-M4 | youtube.com::video_playback |
| 20260918 | shadowsocks | youtube_video:aircAruvnKk | 5 | 0 | 0 | E1 | M2-M4 | youtube.com::video_playback |
| 20260918 | shadowsocks | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E1 | M2-M4 | youtube.com::video_playback |
| 20260918 | shadowsocks | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E1 | M2-M4 | youtube.com::video_playback |
| 20260918 | shadowsocks | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E1 | M2-M4 | youtube.com::video_playback |
| 20260918 | trojan | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 1 | E1 | M2-M4 | developer.mozilla.org::document_view |
| 20260918 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 1 | 0 | E1 | M2-M4 | developer.mozilla.org::document_view |
| 20260918 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 1 | 0 | E1 | M2-M4 | developer.mozilla.org::document_view |
| 20260918 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 3 | 0 | E1 | M2-M4 | developer.mozilla.org::document_view |
| 20260918 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 2 | 0 | E1 | M2-M4 | developer.mozilla.org::document_view |
| 20260918 | trojan | https://en.wikipedia.org/wiki/Computer_network | 3 | 0 | 0 | E1 | M2-M4 | wikipedia.org::article_view |
| 20260918 | trojan | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 2 | E1 | M2-M4 | wikipedia.org::article_view |
| 20260918 | trojan | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 2 | 0 | E1 | M2-M4 | wikipedia.org::article_view |
| 20260918 | trojan | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 0 | E1 | M2-M4 | wikipedia.org::article_view |
| 20260918 | trojan | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E1 | M2-M4 | wikipedia.org::article_view |
| 20260918 | trojan | https://github.com/RakuLomis/TrafficTracer | 2 | 2 | 0 | E1 | M2-M4 | github.com::repository_view |
| 20260918 | trojan | https://github.com/numpy/numpy | 2 | 0 | 0 | E1 | M2-M4 | github.com::repository_view |
| 20260918 | trojan | https://github.com/pallets/flask | 2 | 1 | 0 | E1 | M2-M4 | github.com::repository_view |
| 20260918 | trojan | https://github.com/python/cpython | 2 | 0 | 0 | E1 | M2-M4 | github.com::repository_view |
| 20260918 | trojan | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 1 | E1 | M2-M4 | github.com::repository_view |
| 20260918 | trojan | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 1 | 0 | E1 | M2-M4 | bing.com::search_results_view |
| 20260918 | trojan | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 1 | E1 | M2-M4 | bing.com::search_results_view |
| 20260918 | trojan | https://www.bing.com/search?q=network+traffic+analysis | 0 | 1 | 0 | E1 | M2-M4 | bing.com::search_results_view |
| 20260918 | trojan | https://www.bing.com/search?q=solar+system+facts | 0 | 2 | 0 | E1 | M2-M4 | bing.com::search_results_view |
| 20260918 | trojan | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 1 | 0 | E1 | M2-M4 | bing.com::search_results_view |
| 20260918 | trojan | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E1 | M2-M4 | youtube.com::search_results_view |
| 20260918 | trojan | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 0 | E1 | M2-M4 | youtube.com::search_results_view |
| 20260918 | trojan | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E1 | M2-M4 | youtube.com::search_results_view |
| 20260918 | trojan | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 0 | E1 | M2-M4 | youtube.com::search_results_view |
| 20260918 | trojan | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 1 | E1 | M2-M4 | youtube.com::search_results_view |
| 20260918 | trojan | youtube_video:R6MlUcmOul8 | 5 | 0 | 1 | E1 | M2-M4 | youtube.com::video_playback |
| 20260918 | trojan | youtube_video:aircAruvnKk | 5 | 0 | 0 | E1 | M2-M4 | youtube.com::video_playback |
| 20260918 | trojan | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E1 | M2-M4 | youtube.com::video_playback |
| 20260918 | trojan | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E1 | M2-M4 | youtube.com::video_playback |
| 20260918 | trojan | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E1 | M2-M4 | youtube.com::video_playback |
| 20260918 | vless | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 0 | E1 | M2-M4 | developer.mozilla.org::document_view |
| 20260918 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 0 | 0 | E1 | M2-M4 | developer.mozilla.org::document_view |
| 20260918 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 0 | E1 | M2-M4 | developer.mozilla.org::document_view |
| 20260918 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 3 | 0 | E1 | M2-M4 | developer.mozilla.org::document_view |
| 20260918 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 3 | 0 | E1 | M2-M4 | developer.mozilla.org::document_view |
| 20260918 | vless | https://en.wikipedia.org/wiki/Computer_network | 3 | 1 | 2 | E1 | M2-M4 | wikipedia.org::article_view |
| 20260918 | vless | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 3 | E1 | M2-M4 | wikipedia.org::article_view |
| 20260918 | vless | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 1 | 0 | E1 | M2-M4 | wikipedia.org::article_view |
| 20260918 | vless | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 2 | E1 | M2-M4 | wikipedia.org::article_view |
| 20260918 | vless | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 1 | E1 | M2-M4 | wikipedia.org::article_view |
| 20260918 | vless | https://github.com/RakuLomis/TrafficTracer | 2 | 2 | 0 | E1 | M2-M4 | github.com::repository_view |
| 20260918 | vless | https://github.com/numpy/numpy | 2 | 0 | 0 | E1 | M2-M4 | github.com::repository_view |
| 20260918 | vless | https://github.com/pallets/flask | 2 | 1 | 0 | E1 | M2-M4 | github.com::repository_view |
| 20260918 | vless | https://github.com/python/cpython | 2 | 1 | 0 | E1 | M2-M4 | github.com::repository_view |
| 20260918 | vless | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E1 | M2-M4 | github.com::repository_view |
| 20260918 | vless | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 1 | 0 | E1 | M2-M4 | bing.com::search_results_view |
| 20260918 | vless | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 1 | E1 | M2-M4 | bing.com::search_results_view |
| 20260918 | vless | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E1 | M2-M4 | bing.com::search_results_view |
| 20260918 | vless | https://www.bing.com/search?q=solar+system+facts | 0 | 1 | 0 | E1 | M2-M4 | bing.com::search_results_view |
| 20260918 | vless | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 2 | 0 | E1 | M2-M4 | bing.com::search_results_view |
| 20260918 | vless | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E1 | M2-M4 | youtube.com::search_results_view |
| 20260918 | vless | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 1 | E1 | M2-M4 | youtube.com::search_results_view |
| 20260918 | vless | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E1 | M2-M4 | youtube.com::search_results_view |
| 20260918 | vless | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 0 | E1 | M2-M4 | youtube.com::search_results_view |
| 20260918 | vless | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E1 | M2-M4 | youtube.com::search_results_view |
| 20260918 | vless | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E1 | M2-M4 | youtube.com::video_playback |
| 20260918 | vless | youtube_video:aircAruvnKk | 5 | 0 | 0 | E1 | M2-M4 | youtube.com::video_playback |
| 20260918 | vless | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E1 | M2-M4 | youtube.com::video_playback |
| 20260918 | vless | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E1 | M2-M4 | youtube.com::video_playback |
| 20260918 | vless | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E1 | M2-M4 | youtube.com::video_playback |
| 20260918 | vmess | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 0 | E1 | M2-M4 | developer.mozilla.org::document_view |
| 20260918 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 0 | 0 | E1 | M2-M4 | developer.mozilla.org::document_view |
| 20260918 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 0 | E1 | M2-M4 | developer.mozilla.org::document_view |
| 20260918 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 0 | 1 | E1 | M2-M4 | developer.mozilla.org::document_view |
| 20260918 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 0 | 0 | E1 | M2-M4 | developer.mozilla.org::document_view |
| 20260918 | vmess | https://en.wikipedia.org/wiki/Computer_network | 3 | 1 | 0 | E1 | M2-M4 | wikipedia.org::article_view |
| 20260918 | vmess | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 0 | E1 | M2-M4 | wikipedia.org::article_view |
| 20260918 | vmess | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 0 | 0 | E1 | M2-M4 | wikipedia.org::article_view |
| 20260918 | vmess | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 1 | E1 | M2-M4 | wikipedia.org::article_view |
| 20260918 | vmess | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E1 | M2-M4 | wikipedia.org::article_view |
| 20260918 | vmess | https://github.com/RakuLomis/TrafficTracer | 2 | 1 | 0 | E1 | M2-M4 | github.com::repository_view |
| 20260918 | vmess | https://github.com/numpy/numpy | 2 | 1 | 0 | E1 | M2-M4 | github.com::repository_view |
| 20260918 | vmess | https://github.com/pallets/flask | 2 | 0 | 0 | E1 | M2-M4 | github.com::repository_view |
| 20260918 | vmess | https://github.com/python/cpython | 2 | 0 | 0 | E1 | M2-M4 | github.com::repository_view |
| 20260918 | vmess | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E1 | M2-M4 | github.com::repository_view |
| 20260918 | vmess | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 0 | E1 | M2-M4 | bing.com::search_results_view |
| 20260918 | vmess | https://www.bing.com/search?q=indoor+plant+care | 0 | 1 | 0 | E1 | M2-M4 | bing.com::search_results_view |
| 20260918 | vmess | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E1 | M2-M4 | bing.com::search_results_view |
| 20260918 | vmess | https://www.bing.com/search?q=solar+system+facts | 0 | 0 | 0 | E1 | M2-M4 | bing.com::search_results_view |
| 20260918 | vmess | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 0 | E1 | M2-M4 | bing.com::search_results_view |
| 20260918 | vmess | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E1 | M2-M4 | youtube.com::search_results_view |
| 20260918 | vmess | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 1 | 0 | E1 | M2-M4 | youtube.com::search_results_view |
| 20260918 | vmess | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E1 | M2-M4 | youtube.com::search_results_view |
| 20260918 | vmess | https://www.youtube.com/results?search_query=piano+practice | 4 | 1 | 0 | E1 | M2-M4 | youtube.com::search_results_view |
| 20260918 | vmess | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E1 | M2-M4 | youtube.com::search_results_view |
| 20260918 | vmess | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E1 | M2-M4 | youtube.com::video_playback |
| 20260918 | vmess | youtube_video:aircAruvnKk | 5 | 0 | 0 | E1 | M2-M4 | youtube.com::video_playback |
| 20260918 | vmess | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E1 | M2-M4 | youtube.com::video_playback |
| 20260918 | vmess | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E1 | M2-M4 | youtube.com::video_playback |
| 20260918 | vmess | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E1 | M2-M4 | youtube.com::video_playback |
| 20260919 | anytls | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 3 | 0 | E1 | M2-M4 | developer.mozilla.org::document_view |
| 20260919 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 1 | 0 | E1 | M2-M4 | developer.mozilla.org::document_view |
| 20260919 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 1 | 0 | E1 | M2-M4 | developer.mozilla.org::document_view |
| 20260919 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 3 | 0 | E1 | M2-M4 | developer.mozilla.org::document_view |
| 20260919 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 2 | 0 | E1 | M2-M4 | developer.mozilla.org::document_view |
| 20260919 | anytls | https://en.wikipedia.org/wiki/Computer_network | 3 | 0 | 1 | E1 | M2-M4 | wikipedia.org::article_view |
| 20260919 | anytls | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 1 | E1 | M2-M4 | wikipedia.org::article_view |
| 20260919 | anytls | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 0 | 2 | E1 | M2-M4 | wikipedia.org::article_view |
| 20260919 | anytls | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 0 | E1 | M2-M4 | wikipedia.org::article_view |
| 20260919 | anytls | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E1 | M2-M4 | wikipedia.org::article_view |
| 20260919 | anytls | https://github.com/RakuLomis/TrafficTracer | 2 | 0 | 0 | E1 | M2-M4 | github.com::repository_view |
| 20260919 | anytls | https://github.com/numpy/numpy | 2 | 0 | 0 | E1 | M2-M4 | github.com::repository_view |
| 20260919 | anytls | https://github.com/pallets/flask | 2 | 0 | 0 | E1 | M2-M4 | github.com::repository_view |
| 20260919 | anytls | https://github.com/python/cpython | 2 | 1 | 0 | E1 | M2-M4 | github.com::repository_view |
| 20260919 | anytls | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E1 | M2-M4 | github.com::repository_view |
| 20260919 | anytls | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 0 | E1 | M2-M4 | bing.com::search_results_view |
| 20260919 | anytls | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 1 | E1 | M2-M4 | bing.com::search_results_view |
| 20260919 | anytls | https://www.bing.com/search?q=network+traffic+analysis | 0 | 1 | 0 | E1 | M2-M4 | bing.com::search_results_view |
| 20260919 | anytls | https://www.bing.com/search?q=solar+system+facts | 0 | 0 | 0 | E1 | M2-M4 | bing.com::search_results_view |
| 20260919 | anytls | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 0 | E1 | M2-M4 | bing.com::search_results_view |
| 20260919 | anytls | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 1 | 0 | E1 | M2-M4 | youtube.com::search_results_view |
| 20260919 | anytls | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 0 | E1 | M2-M4 | youtube.com::search_results_view |
| 20260919 | anytls | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E1 | M2-M4 | youtube.com::search_results_view |
| 20260919 | anytls | https://www.youtube.com/results?search_query=piano+practice | 4 | 1 | 0 | E1 | M2-M4 | youtube.com::search_results_view |
| 20260919 | anytls | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E1 | M2-M4 | youtube.com::search_results_view |
| 20260919 | anytls | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E1 | M2-M4 | youtube.com::video_playback |
| 20260919 | anytls | youtube_video:aircAruvnKk | 5 | 0 | 0 | E1 | M2-M4 | youtube.com::video_playback |
| 20260919 | anytls | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E1 | M2-M4 | youtube.com::video_playback |
| 20260919 | anytls | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E1 | M2-M4 | youtube.com::video_playback |
| 20260919 | anytls | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E1 | M2-M4 | youtube.com::video_playback |
| 20260919 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 1 | E1 | M2-M4 | developer.mozilla.org::document_view |
| 20260919 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 0 | 0 | E1 | M2-M4 | developer.mozilla.org::document_view |
| 20260919 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 0 | E1 | M2-M4 | developer.mozilla.org::document_view |
| 20260919 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 0 | 1 | E1 | M2-M4 | developer.mozilla.org::document_view |
| 20260919 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 0 | 0 | E1 | M2-M4 | developer.mozilla.org::document_view |
| 20260919 | shadowsocks | https://en.wikipedia.org/wiki/Computer_network | 3 | 3 | 0 | E1 | M2-M4 | wikipedia.org::article_view |
| 20260919 | shadowsocks | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 1 | 0 | E1 | M2-M4 | wikipedia.org::article_view |
| 20260919 | shadowsocks | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 1 | 0 | E1 | M2-M4 | wikipedia.org::article_view |
| 20260919 | shadowsocks | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 0 | E1 | M2-M4 | wikipedia.org::article_view |
| 20260919 | shadowsocks | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 1 | 0 | E1 | M2-M4 | wikipedia.org::article_view |
| 20260919 | shadowsocks | https://github.com/RakuLomis/TrafficTracer | 2 | 1 | 0 | E1 | M2-M4 | github.com::repository_view |
| 20260919 | shadowsocks | https://github.com/numpy/numpy | 2 | 0 | 0 | E1 | M2-M4 | github.com::repository_view |
| 20260919 | shadowsocks | https://github.com/pallets/flask | 2 | 0 | 0 | E1 | M2-M4 | github.com::repository_view |
| 20260919 | shadowsocks | https://github.com/python/cpython | 2 | 0 | 0 | E1 | M2-M4 | github.com::repository_view |
| 20260919 | shadowsocks | https://github.com/scikit-learn/scikit-learn | 2 | 1 | 0 | E1 | M2-M4 | github.com::repository_view |
| 20260919 | shadowsocks | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 1 | E1 | M2-M4 | bing.com::search_results_view |
| 20260919 | shadowsocks | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 0 | E1 | M2-M4 | bing.com::search_results_view |
| 20260919 | shadowsocks | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E1 | M2-M4 | bing.com::search_results_view |
| 20260919 | shadowsocks | https://www.bing.com/search?q=solar+system+facts | 0 | 0 | 0 | E1 | M2-M4 | bing.com::search_results_view |
| 20260919 | shadowsocks | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 0 | E1 | M2-M4 | bing.com::search_results_view |
| 20260919 | shadowsocks | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E1 | M2-M4 | youtube.com::search_results_view |
| 20260919 | shadowsocks | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 1 | 0 | E1 | M2-M4 | youtube.com::search_results_view |
| 20260919 | shadowsocks | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E1 | M2-M4 | youtube.com::search_results_view |
| 20260919 | shadowsocks | https://www.youtube.com/results?search_query=piano+practice | 4 | 1 | 0 | E1 | M2-M4 | youtube.com::search_results_view |
| 20260919 | shadowsocks | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E1 | M2-M4 | youtube.com::search_results_view |
| 20260919 | shadowsocks | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E1 | M2-M4 | youtube.com::video_playback |
| 20260919 | shadowsocks | youtube_video:aircAruvnKk | 5 | 0 | 0 | E1 | M2-M4 | youtube.com::video_playback |
| 20260919 | shadowsocks | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E1 | M2-M4 | youtube.com::video_playback |
| 20260919 | shadowsocks | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E1 | M2-M4 | youtube.com::video_playback |
| 20260919 | shadowsocks | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E1 | M2-M4 | youtube.com::video_playback |
| 20260919 | trojan | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 1 | 0 | E1 | M2-M4 | developer.mozilla.org::document_view |
| 20260919 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 3 | 0 | E1 | M2-M4 | developer.mozilla.org::document_view |
| 20260919 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 1 | 0 | E1 | M2-M4 | developer.mozilla.org::document_view |
| 20260919 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 3 | 0 | E1 | M2-M4 | developer.mozilla.org::document_view |
| 20260919 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 1 | 0 | E1 | M2-M4 | developer.mozilla.org::document_view |
| 20260919 | trojan | https://en.wikipedia.org/wiki/Computer_network | 3 | 0 | 0 | E1 | M2-M4 | wikipedia.org::article_view |
| 20260919 | trojan | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 2 | E1 | M2-M4 | wikipedia.org::article_view |
| 20260919 | trojan | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 1 | 2 | E1 | M2-M4 | wikipedia.org::article_view |
| 20260919 | trojan | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 1 | 0 | E1 | M2-M4 | wikipedia.org::article_view |
| 20260919 | trojan | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E1 | M2-M4 | wikipedia.org::article_view |
| 20260919 | trojan | https://github.com/RakuLomis/TrafficTracer | 2 | 2 | 0 | E1 | M2-M4 | github.com::repository_view |
| 20260919 | trojan | https://github.com/numpy/numpy | 2 | 0 | 0 | E1 | M2-M4 | github.com::repository_view |
| 20260919 | trojan | https://github.com/pallets/flask | 2 | 1 | 0 | E1 | M2-M4 | github.com::repository_view |
| 20260919 | trojan | https://github.com/python/cpython | 2 | 0 | 0 | E1 | M2-M4 | github.com::repository_view |
| 20260919 | trojan | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 1 | E1 | M2-M4 | github.com::repository_view |
| 20260919 | trojan | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 1 | 0 | E1 | M2-M4 | bing.com::search_results_view |
| 20260919 | trojan | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 0 | E1 | M2-M4 | bing.com::search_results_view |
| 20260919 | trojan | https://www.bing.com/search?q=network+traffic+analysis | 0 | 1 | 0 | E1 | M2-M4 | bing.com::search_results_view |
| 20260919 | trojan | https://www.bing.com/search?q=solar+system+facts | 0 | 1 | 0 | E1 | M2-M4 | bing.com::search_results_view |
| 20260919 | trojan | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 2 | 0 | E1 | M2-M4 | bing.com::search_results_view |
| 20260919 | trojan | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E1 | M2-M4 | youtube.com::search_results_view |
| 20260919 | trojan | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 1 | 0 | E1 | M2-M4 | youtube.com::search_results_view |
| 20260919 | trojan | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E1 | M2-M4 | youtube.com::search_results_view |
| 20260919 | trojan | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 0 | E1 | M2-M4 | youtube.com::search_results_view |
| 20260919 | trojan | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 1 | E1 | M2-M4 | youtube.com::search_results_view |
| 20260919 | trojan | youtube_video:R6MlUcmOul8 | 5 | 1 | 1 | E1 | M2-M4 | youtube.com::video_playback |
| 20260919 | trojan | youtube_video:aircAruvnKk | 5 | 0 | 0 | E1 | M2-M4 | youtube.com::video_playback |
| 20260919 | trojan | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E1 | M2-M4 | youtube.com::video_playback |
| 20260919 | trojan | youtube_video:eRsGyueVLvQ | 5 | 0 | 1 | E1 | M2-M4 | youtube.com::video_playback |
| 20260919 | trojan | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E1 | M2-M4 | youtube.com::video_playback |
| 20260919 | vless | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 2 | 0 | E1 | M2-M4 | developer.mozilla.org::document_view |
| 20260919 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 3 | 0 | E1 | M2-M4 | developer.mozilla.org::document_view |
| 20260919 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 1 | 0 | E1 | M2-M4 | developer.mozilla.org::document_view |
| 20260919 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 4 | 0 | E1 | M2-M4 | developer.mozilla.org::document_view |
| 20260919 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 0 | 0 | E1 | M2-M4 | developer.mozilla.org::document_view |
| 20260919 | vless | https://en.wikipedia.org/wiki/Computer_network | 3 | 1 | 1 | E1 | M2-M4 | wikipedia.org::article_view |
| 20260919 | vless | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 2 | E1 | M2-M4 | wikipedia.org::article_view |
| 20260919 | vless | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 0 | 0 | E1 | M2-M4 | wikipedia.org::article_view |
| 20260919 | vless | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 1 | 0 | E1 | M2-M4 | wikipedia.org::article_view |
| 20260919 | vless | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 1 | E1 | M2-M4 | wikipedia.org::article_view |
| 20260919 | vless | https://github.com/RakuLomis/TrafficTracer | 2 | 2 | 1 | E1 | M2-M4 | github.com::repository_view |
| 20260919 | vless | https://github.com/numpy/numpy | 2 | 0 | 0 | E1 | M2-M4 | github.com::repository_view |
| 20260919 | vless | https://github.com/pallets/flask | 2 | 0 | 0 | E1 | M2-M4 | github.com::repository_view |
| 20260919 | vless | https://github.com/python/cpython | 2 | 1 | 0 | E1 | M2-M4 | github.com::repository_view |
| 20260919 | vless | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E1 | M2-M4 | github.com::repository_view |
| 20260919 | vless | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 1 | 0 | E1 | M2-M4 | bing.com::search_results_view |
| 20260919 | vless | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 0 | E1 | M2-M4 | bing.com::search_results_view |
| 20260919 | vless | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E1 | M2-M4 | bing.com::search_results_view |
| 20260919 | vless | https://www.bing.com/search?q=solar+system+facts | 0 | 0 | 0 | E1 | M2-M4 | bing.com::search_results_view |
| 20260919 | vless | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 0 | E1 | M2-M4 | bing.com::search_results_view |
| 20260919 | vless | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E1 | M2-M4 | youtube.com::search_results_view |
| 20260919 | vless | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 2 | E1 | M2-M4 | youtube.com::search_results_view |
| 20260919 | vless | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E1 | M2-M4 | youtube.com::search_results_view |
| 20260919 | vless | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 1 | E1 | M2-M4 | youtube.com::search_results_view |
| 20260919 | vless | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E1 | M2-M4 | youtube.com::search_results_view |
| 20260919 | vless | youtube_video:R6MlUcmOul8 | 5 | 0 | 1 | E1 | M2-M4 | youtube.com::video_playback |
| 20260919 | vless | youtube_video:aircAruvnKk | 5 | 1 | 0 | E1 | M2-M4 | youtube.com::video_playback |
| 20260919 | vless | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E1 | M2-M4 | youtube.com::video_playback |
| 20260919 | vless | youtube_video:eRsGyueVLvQ | 5 | 0 | 1 | E1 | M2-M4 | youtube.com::video_playback |
| 20260919 | vless | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E1 | M2-M4 | youtube.com::video_playback |
| 20260919 | vmess | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 0 | E1 | M2-M4 | developer.mozilla.org::document_view |
| 20260919 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 0 | 0 | E1 | M2-M4 | developer.mozilla.org::document_view |
| 20260919 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 0 | E1 | M2-M4 | developer.mozilla.org::document_view |
| 20260919 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 0 | 0 | E1 | M2-M4 | developer.mozilla.org::document_view |
| 20260919 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 1 | 0 | E1 | M2-M4 | developer.mozilla.org::document_view |
| 20260919 | vmess | https://en.wikipedia.org/wiki/Computer_network | 3 | 1 | 0 | E1 | M2-M4 | wikipedia.org::article_view |
| 20260919 | vmess | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 0 | E1 | M2-M4 | wikipedia.org::article_view |
| 20260919 | vmess | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 0 | 1 | E1 | M2-M4 | wikipedia.org::article_view |
| 20260919 | vmess | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 0 | E1 | M2-M4 | wikipedia.org::article_view |
| 20260919 | vmess | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E1 | M2-M4 | wikipedia.org::article_view |
| 20260919 | vmess | https://github.com/RakuLomis/TrafficTracer | 2 | 1 | 0 | E1 | M2-M4 | github.com::repository_view |
| 20260919 | vmess | https://github.com/numpy/numpy | 2 | 0 | 0 | E1 | M2-M4 | github.com::repository_view |
| 20260919 | vmess | https://github.com/pallets/flask | 2 | 0 | 0 | E1 | M2-M4 | github.com::repository_view |
| 20260919 | vmess | https://github.com/python/cpython | 2 | 0 | 0 | E1 | M2-M4 | github.com::repository_view |
| 20260919 | vmess | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E1 | M2-M4 | github.com::repository_view |
| 20260919 | vmess | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 0 | E1 | M2-M4 | bing.com::search_results_view |
| 20260919 | vmess | https://www.bing.com/search?q=indoor+plant+care | 0 | 1 | 0 | E1 | M2-M4 | bing.com::search_results_view |
| 20260919 | vmess | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E1 | M2-M4 | bing.com::search_results_view |
| 20260919 | vmess | https://www.bing.com/search?q=solar+system+facts | 0 | 0 | 0 | E1 | M2-M4 | bing.com::search_results_view |
| 20260919 | vmess | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 0 | E1 | M2-M4 | bing.com::search_results_view |
| 20260919 | vmess | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E1 | M2-M4 | youtube.com::search_results_view |
| 20260919 | vmess | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 1 | 0 | E1 | M2-M4 | youtube.com::search_results_view |
| 20260919 | vmess | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E1 | M2-M4 | youtube.com::search_results_view |
| 20260919 | vmess | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 0 | E1 | M2-M4 | youtube.com::search_results_view |
| 20260919 | vmess | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E1 | M2-M4 | youtube.com::search_results_view |
| 20260919 | vmess | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E1 | M2-M4 | youtube.com::video_playback |
| 20260919 | vmess | youtube_video:aircAruvnKk | 5 | 0 | 0 | E1 | M2-M4 | youtube.com::video_playback |
| 20260919 | vmess | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E1 | M2-M4 | youtube.com::video_playback |
| 20260919 | vmess | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E1 | M2-M4 | youtube.com::video_playback |
| 20260919 | vmess | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E1 | M2-M4 | youtube.com::video_playback |
| 20260920 | anytls | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 3 | 0 | E1 | M2-M4 | developer.mozilla.org::document_view |
| 20260920 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 1 | 0 | E1 | M2-M4 | developer.mozilla.org::document_view |
| 20260920 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 0 | E1 | M2-M4 | developer.mozilla.org::document_view |
| 20260920 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 1 | 0 | E1 | M2-M4 | developer.mozilla.org::document_view |
| 20260920 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 0 | 0 | E1 | M2-M4 | developer.mozilla.org::document_view |
| 20260920 | anytls | https://en.wikipedia.org/wiki/Computer_network | 3 | 1 | 0 | E1 | M2-M4 | wikipedia.org::article_view |
| 20260920 | anytls | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 0 | E1 | M2-M4 | wikipedia.org::article_view |
| 20260920 | anytls | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 0 | 2 | E1 | M2-M4 | wikipedia.org::article_view |
| 20260920 | anytls | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 0 | E1 | M2-M4 | wikipedia.org::article_view |
| 20260920 | anytls | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 1 | 0 | E1 | M2-M4 | wikipedia.org::article_view |
| 20260920 | anytls | https://github.com/RakuLomis/TrafficTracer | 2 | 1 | 0 | E1 | M2-M4 | github.com::repository_view |
| 20260920 | anytls | https://github.com/numpy/numpy | 2 | 0 | 0 | E1 | M2-M4 | github.com::repository_view |
| 20260920 | anytls | https://github.com/pallets/flask | 2 | 0 | 1 | E1 | M2-M4 | github.com::repository_view |
| 20260920 | anytls | https://github.com/python/cpython | 2 | 1 | 0 | E1 | M2-M4 | github.com::repository_view |
| 20260920 | anytls | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E1 | M2-M4 | github.com::repository_view |
| 20260920 | anytls | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 0 | E1 | M2-M4 | bing.com::search_results_view |
| 20260920 | anytls | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 1 | E1 | M2-M4 | bing.com::search_results_view |
| 20260920 | anytls | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E1 | M2-M4 | bing.com::search_results_view |
| 20260920 | anytls | https://www.bing.com/search?q=solar+system+facts | 0 | 0 | 0 | E1 | M2-M4 | bing.com::search_results_view |
| 20260920 | anytls | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 0 | E1 | M2-M4 | bing.com::search_results_view |
| 20260920 | anytls | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E1 | M2-M4 | youtube.com::search_results_view |
| 20260920 | anytls | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 1 | 0 | E1 | M2-M4 | youtube.com::search_results_view |
| 20260920 | anytls | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E1 | M2-M4 | youtube.com::search_results_view |
| 20260920 | anytls | https://www.youtube.com/results?search_query=piano+practice | 4 | 1 | 0 | E1 | M2-M4 | youtube.com::search_results_view |
| 20260920 | anytls | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E1 | M2-M4 | youtube.com::search_results_view |
| 20260920 | anytls | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E1 | M2-M4 | youtube.com::video_playback |
| 20260920 | anytls | youtube_video:aircAruvnKk | 5 | 0 | 0 | E1 | M2-M4 | youtube.com::video_playback |
| 20260920 | anytls | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E1 | M2-M4 | youtube.com::video_playback |
| 20260920 | anytls | youtube_video:eRsGyueVLvQ | 5 | 1 | 0 | E1 | M2-M4 | youtube.com::video_playback |
| 20260920 | anytls | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E1 | M2-M4 | youtube.com::video_playback |
| 20260920 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 0 | E1 | M2-M4 | developer.mozilla.org::document_view |
| 20260920 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 0 | 0 | E1 | M2-M4 | developer.mozilla.org::document_view |
| 20260920 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 0 | E1 | M2-M4 | developer.mozilla.org::document_view |
| 20260920 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 0 | 1 | E1 | M2-M4 | developer.mozilla.org::document_view |
| 20260920 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 0 | 0 | E1 | M2-M4 | developer.mozilla.org::document_view |
| 20260920 | shadowsocks | https://en.wikipedia.org/wiki/Computer_network | 3 | 2 | 0 | E1 | M2-M4 | wikipedia.org::article_view |
| 20260920 | shadowsocks | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 0 | E1 | M2-M4 | wikipedia.org::article_view |
| 20260920 | shadowsocks | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 3 | 0 | E1 | M2-M4 | wikipedia.org::article_view |
| 20260920 | shadowsocks | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 0 | E1 | M2-M4 | wikipedia.org::article_view |
| 20260920 | shadowsocks | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 1 | 0 | E1 | M2-M4 | wikipedia.org::article_view |
| 20260920 | shadowsocks | https://github.com/RakuLomis/TrafficTracer | 2 | 1 | 0 | E1 | M2-M4 | github.com::repository_view |
| 20260920 | shadowsocks | https://github.com/numpy/numpy | 2 | 1 | 0 | E1 | M2-M4 | github.com::repository_view |
| 20260920 | shadowsocks | https://github.com/pallets/flask | 2 | 0 | 0 | E1 | M2-M4 | github.com::repository_view |
| 20260920 | shadowsocks | https://github.com/python/cpython | 2 | 0 | 0 | E1 | M2-M4 | github.com::repository_view |
| 20260920 | shadowsocks | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E1 | M2-M4 | github.com::repository_view |
| 20260920 | shadowsocks | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 0 | E1 | M2-M4 | bing.com::search_results_view |
| 20260920 | shadowsocks | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 0 | E1 | M2-M4 | bing.com::search_results_view |
| 20260920 | shadowsocks | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E1 | M2-M4 | bing.com::search_results_view |
| 20260920 | shadowsocks | https://www.bing.com/search?q=solar+system+facts | 0 | 0 | 1 | E1 | M2-M4 | bing.com::search_results_view |
| 20260920 | shadowsocks | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 1 | 0 | E1 | M2-M4 | bing.com::search_results_view |
| 20260920 | shadowsocks | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 1 | 0 | E1 | M2-M4 | youtube.com::search_results_view |
| 20260920 | shadowsocks | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 0 | E1 | M2-M4 | youtube.com::search_results_view |
| 20260920 | shadowsocks | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E1 | M2-M4 | youtube.com::search_results_view |
| 20260920 | shadowsocks | https://www.youtube.com/results?search_query=piano+practice | 4 | 1 | 0 | E1 | M2-M4 | youtube.com::search_results_view |
| 20260920 | shadowsocks | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E1 | M2-M4 | youtube.com::search_results_view |
| 20260920 | shadowsocks | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E1 | M2-M4 | youtube.com::video_playback |
| 20260920 | shadowsocks | youtube_video:aircAruvnKk | 5 | 0 | 0 | E1 | M2-M4 | youtube.com::video_playback |
| 20260920 | shadowsocks | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E1 | M2-M4 | youtube.com::video_playback |
| 20260920 | shadowsocks | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E1 | M2-M4 | youtube.com::video_playback |
| 20260920 | shadowsocks | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E1 | M2-M4 | youtube.com::video_playback |
| 20260920 | trojan | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 1 | 0 | E1 | M2-M4 | developer.mozilla.org::document_view |
| 20260920 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 3 | 0 | E1 | M2-M4 | developer.mozilla.org::document_view |
| 20260920 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 0 | E1 | M2-M4 | developer.mozilla.org::document_view |
| 20260920 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 1 | 0 | E1 | M2-M4 | developer.mozilla.org::document_view |
| 20260920 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 0 | 0 | E1 | M2-M4 | developer.mozilla.org::document_view |
| 20260920 | trojan | https://en.wikipedia.org/wiki/Computer_network | 3 | 0 | 0 | E1 | M2-M4 | wikipedia.org::article_view |
| 20260920 | trojan | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 3 | 1 | E1 | M2-M4 | wikipedia.org::article_view |
| 20260920 | trojan | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 0 | 0 | E1 | M2-M4 | wikipedia.org::article_view |
| 20260920 | trojan | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 1 | 0 | E1 | M2-M4 | wikipedia.org::article_view |
| 20260920 | trojan | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E1 | M2-M4 | wikipedia.org::article_view |
| 20260920 | trojan | https://github.com/RakuLomis/TrafficTracer | 2 | 2 | 0 | E1 | M2-M4 | github.com::repository_view |
| 20260920 | trojan | https://github.com/numpy/numpy | 2 | 0 | 0 | E1 | M2-M4 | github.com::repository_view |
| 20260920 | trojan | https://github.com/pallets/flask | 2 | 1 | 1 | E1 | M2-M4 | github.com::repository_view |
| 20260920 | trojan | https://github.com/python/cpython | 2 | 0 | 0 | E1 | M2-M4 | github.com::repository_view |
| 20260920 | trojan | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 1 | E1 | M2-M4 | github.com::repository_view |
| 20260920 | trojan | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 2 | 0 | E1 | M2-M4 | bing.com::search_results_view |
| 20260920 | trojan | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 0 | E1 | M2-M4 | bing.com::search_results_view |
| 20260920 | trojan | https://www.bing.com/search?q=network+traffic+analysis | 0 | 1 | 0 | E1 | M2-M4 | bing.com::search_results_view |
| 20260920 | trojan | https://www.bing.com/search?q=solar+system+facts | 0 | 2 | 0 | E1 | M2-M4 | bing.com::search_results_view |
| 20260920 | trojan | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 1 | 0 | E1 | M2-M4 | bing.com::search_results_view |
| 20260920 | trojan | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E1 | M2-M4 | youtube.com::search_results_view |
| 20260920 | trojan | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 0 | E1 | M2-M4 | youtube.com::search_results_view |
| 20260920 | trojan | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E1 | M2-M4 | youtube.com::search_results_view |
| 20260920 | trojan | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 0 | E1 | M2-M4 | youtube.com::search_results_view |
| 20260920 | trojan | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 1 | E1 | M2-M4 | youtube.com::search_results_view |
| 20260920 | trojan | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E1 | M2-M4 | youtube.com::video_playback |
| 20260920 | trojan | youtube_video:aircAruvnKk | 5 | 0 | 0 | E1 | M2-M4 | youtube.com::video_playback |
| 20260920 | trojan | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E1 | M2-M4 | youtube.com::video_playback |
| 20260920 | trojan | youtube_video:eRsGyueVLvQ | 5 | 0 | 1 | E1 | M2-M4 | youtube.com::video_playback |
| 20260920 | trojan | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E1 | M2-M4 | youtube.com::video_playback |
| 20260920 | vless | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 2 | 0 | E1 | M2-M4 | developer.mozilla.org::document_view |
| 20260920 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 3 | 0 | E1 | M2-M4 | developer.mozilla.org::document_view |
| 20260920 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 2 | 0 | E1 | M2-M4 | developer.mozilla.org::document_view |
| 20260920 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 2 | 0 | E1 | M2-M4 | developer.mozilla.org::document_view |
| 20260920 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 1 | 0 | E1 | M2-M4 | developer.mozilla.org::document_view |
| 20260920 | vless | https://en.wikipedia.org/wiki/Computer_network | 3 | 0 | 0 | E1 | M2-M4 | wikipedia.org::article_view |
| 20260920 | vless | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 2 | E1 | M2-M4 | wikipedia.org::article_view |
| 20260920 | vless | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 0 | 0 | E1 | M2-M4 | wikipedia.org::article_view |
| 20260920 | vless | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 2 | E1 | M2-M4 | wikipedia.org::article_view |
| 20260920 | vless | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 1 | E1 | M2-M4 | wikipedia.org::article_view |
| 20260920 | vless | https://github.com/RakuLomis/TrafficTracer | 2 | 1 | 0 | E1 | M2-M4 | github.com::repository_view |
| 20260920 | vless | https://github.com/numpy/numpy | 2 | 0 | 0 | E1 | M2-M4 | github.com::repository_view |
| 20260920 | vless | https://github.com/pallets/flask | 2 | 0 | 0 | E1 | M2-M4 | github.com::repository_view |
| 20260920 | vless | https://github.com/python/cpython | 2 | 0 | 0 | E1 | M2-M4 | github.com::repository_view |
| 20260920 | vless | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E1 | M2-M4 | github.com::repository_view |
| 20260920 | vless | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 0 | E1 | M2-M4 | bing.com::search_results_view |
| 20260920 | vless | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 0 | E1 | M2-M4 | bing.com::search_results_view |
| 20260920 | vless | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E1 | M2-M4 | bing.com::search_results_view |
| 20260920 | vless | https://www.bing.com/search?q=solar+system+facts | 0 | 1 | 0 | E1 | M2-M4 | bing.com::search_results_view |
| 20260920 | vless | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 1 | E1 | M2-M4 | bing.com::search_results_view |
| 20260920 | vless | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E1 | M2-M4 | youtube.com::search_results_view |
| 20260920 | vless | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 2 | E1 | M2-M4 | youtube.com::search_results_view |
| 20260920 | vless | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E1 | M2-M4 | youtube.com::search_results_view |
| 20260920 | vless | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 0 | E1 | M2-M4 | youtube.com::search_results_view |
| 20260920 | vless | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E1 | M2-M4 | youtube.com::search_results_view |
| 20260920 | vless | youtube_video:R6MlUcmOul8 | 5 | 0 | 1 | E1 | M2-M4 | youtube.com::video_playback |
| 20260920 | vless | youtube_video:aircAruvnKk | 5 | 0 | 1 | E1 | M2-M4 | youtube.com::video_playback |
| 20260920 | vless | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E1 | M2-M4 | youtube.com::video_playback |
| 20260920 | vless | youtube_video:eRsGyueVLvQ | 5 | 0 | 1 | E1 | M2-M4 | youtube.com::video_playback |
| 20260920 | vless | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E1 | M2-M4 | youtube.com::video_playback |
| 20260920 | vmess | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 1 | 0 | E1 | M2-M4 | developer.mozilla.org::document_view |
| 20260920 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 0 | 0 | E1 | M2-M4 | developer.mozilla.org::document_view |
| 20260920 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 0 | E1 | M2-M4 | developer.mozilla.org::document_view |
| 20260920 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 0 | 0 | E1 | M2-M4 | developer.mozilla.org::document_view |
| 20260920 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 1 | 0 | E1 | M2-M4 | developer.mozilla.org::document_view |
| 20260920 | vmess | https://en.wikipedia.org/wiki/Computer_network | 3 | 1 | 0 | E1 | M2-M4 | wikipedia.org::article_view |
| 20260920 | vmess | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 0 | E1 | M2-M4 | wikipedia.org::article_view |
| 20260920 | vmess | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 0 | 1 | E1 | M2-M4 | wikipedia.org::article_view |
| 20260920 | vmess | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 1 | E1 | M2-M4 | wikipedia.org::article_view |
| 20260920 | vmess | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E1 | M2-M4 | wikipedia.org::article_view |
| 20260920 | vmess | https://github.com/RakuLomis/TrafficTracer | 2 | 1 | 0 | E1 | M2-M4 | github.com::repository_view |
| 20260920 | vmess | https://github.com/numpy/numpy | 2 | 0 | 0 | E1 | M2-M4 | github.com::repository_view |
| 20260920 | vmess | https://github.com/pallets/flask | 2 | 0 | 1 | E1 | M2-M4 | github.com::repository_view |
| 20260920 | vmess | https://github.com/python/cpython | 2 | 0 | 0 | E1 | M2-M4 | github.com::repository_view |
| 20260920 | vmess | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E1 | M2-M4 | github.com::repository_view |
| 20260920 | vmess | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 1 | 0 | E1 | M2-M4 | bing.com::search_results_view |
| 20260920 | vmess | https://www.bing.com/search?q=indoor+plant+care | 0 | 1 | 0 | E1 | M2-M4 | bing.com::search_results_view |
| 20260920 | vmess | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E1 | M2-M4 | bing.com::search_results_view |
| 20260920 | vmess | https://www.bing.com/search?q=solar+system+facts | 0 | 0 | 0 | E1 | M2-M4 | bing.com::search_results_view |
| 20260920 | vmess | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 0 | E1 | M2-M4 | bing.com::search_results_view |
| 20260920 | vmess | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E1 | M2-M4 | youtube.com::search_results_view |
| 20260920 | vmess | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 1 | 0 | E1 | M2-M4 | youtube.com::search_results_view |
| 20260920 | vmess | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E1 | M2-M4 | youtube.com::search_results_view |
| 20260920 | vmess | https://www.youtube.com/results?search_query=piano+practice | 4 | 1 | 0 | E1 | M2-M4 | youtube.com::search_results_view |
| 20260920 | vmess | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 1 | 0 | E1 | M2-M4 | youtube.com::search_results_view |
| 20260920 | vmess | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E1 | M2-M4 | youtube.com::video_playback |
| 20260920 | vmess | youtube_video:aircAruvnKk | 5 | 0 | 0 | E1 | M2-M4 | youtube.com::video_playback |
| 20260920 | vmess | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E1 | M2-M4 | youtube.com::video_playback |
| 20260920 | vmess | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E1 | M2-M4 | youtube.com::video_playback |
| 20260920 | vmess | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E1 | M2-M4 | youtube.com::video_playback |
| 20260918 | anytls | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 0 | E2 | M2-M0 | developer.mozilla.org::document_view |
| 20260918 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 0 | 0 | E2 | M2-M0 | developer.mozilla.org::document_view |
| 20260918 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 0 | E2 | M2-M0 | developer.mozilla.org::document_view |
| 20260918 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 0 | 0 | E2 | M2-M0 | developer.mozilla.org::document_view |
| 20260918 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 0 | 0 | E2 | M2-M0 | developer.mozilla.org::document_view |
| 20260918 | anytls | https://en.wikipedia.org/wiki/Computer_network | 3 | 0 | 1 | E2 | M2-M0 | wikipedia.org::article_view |
| 20260918 | anytls | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 0 | E2 | M2-M0 | wikipedia.org::article_view |
| 20260918 | anytls | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 0 | 0 | E2 | M2-M0 | wikipedia.org::article_view |
| 20260918 | anytls | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 0 | E2 | M2-M0 | wikipedia.org::article_view |
| 20260918 | anytls | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 1 | E2 | M2-M0 | wikipedia.org::article_view |
| 20260918 | anytls | https://github.com/RakuLomis/TrafficTracer | 2 | 0 | 0 | E2 | M2-M0 | github.com::repository_view |
| 20260918 | anytls | https://github.com/numpy/numpy | 2 | 0 | 0 | E2 | M2-M0 | github.com::repository_view |
| 20260918 | anytls | https://github.com/pallets/flask | 2 | 1 | 0 | E2 | M2-M0 | github.com::repository_view |
| 20260918 | anytls | https://github.com/python/cpython | 2 | 1 | 0 | E2 | M2-M0 | github.com::repository_view |
| 20260918 | anytls | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E2 | M2-M0 | github.com::repository_view |
| 20260918 | anytls | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 0 | E2 | M2-M0 | bing.com::search_results_view |
| 20260918 | anytls | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 0 | E2 | M2-M0 | bing.com::search_results_view |
| 20260918 | anytls | https://www.bing.com/search?q=network+traffic+analysis | 0 | 1 | 0 | E2 | M2-M0 | bing.com::search_results_view |
| 20260918 | anytls | https://www.bing.com/search?q=solar+system+facts | 0 | 1 | 0 | E2 | M2-M0 | bing.com::search_results_view |
| 20260918 | anytls | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 0 | E2 | M2-M0 | bing.com::search_results_view |
| 20260918 | anytls | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E2 | M2-M0 | youtube.com::search_results_view |
| 20260918 | anytls | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 0 | E2 | M2-M0 | youtube.com::search_results_view |
| 20260918 | anytls | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E2 | M2-M0 | youtube.com::search_results_view |
| 20260918 | anytls | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 0 | E2 | M2-M0 | youtube.com::search_results_view |
| 20260918 | anytls | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 1 | E2 | M2-M0 | youtube.com::search_results_view |
| 20260918 | anytls | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E2 | M2-M0 | youtube.com::video_playback |
| 20260918 | anytls | youtube_video:aircAruvnKk | 5 | 0 | 0 | E2 | M2-M0 | youtube.com::video_playback |
| 20260918 | anytls | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E2 | M2-M0 | youtube.com::video_playback |
| 20260918 | anytls | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E2 | M2-M0 | youtube.com::video_playback |
| 20260918 | anytls | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E2 | M2-M0 | youtube.com::video_playback |
| 20260918 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 1 | 0 | E2 | M2-M0 | developer.mozilla.org::document_view |
| 20260918 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 0 | 0 | E2 | M2-M0 | developer.mozilla.org::document_view |
| 20260918 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 0 | E2 | M2-M0 | developer.mozilla.org::document_view |
| 20260918 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 0 | 0 | E2 | M2-M0 | developer.mozilla.org::document_view |
| 20260918 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 0 | 0 | E2 | M2-M0 | developer.mozilla.org::document_view |
| 20260918 | shadowsocks | https://en.wikipedia.org/wiki/Computer_network | 3 | 0 | 0 | E2 | M2-M0 | wikipedia.org::article_view |
| 20260918 | shadowsocks | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 0 | E2 | M2-M0 | wikipedia.org::article_view |
| 20260918 | shadowsocks | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 0 | 0 | E2 | M2-M0 | wikipedia.org::article_view |
| 20260918 | shadowsocks | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 0 | E2 | M2-M0 | wikipedia.org::article_view |
| 20260918 | shadowsocks | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E2 | M2-M0 | wikipedia.org::article_view |
| 20260918 | shadowsocks | https://github.com/RakuLomis/TrafficTracer | 2 | 0 | 0 | E2 | M2-M0 | github.com::repository_view |
| 20260918 | shadowsocks | https://github.com/numpy/numpy | 2 | 0 | 0 | E2 | M2-M0 | github.com::repository_view |
| 20260918 | shadowsocks | https://github.com/pallets/flask | 2 | 0 | 0 | E2 | M2-M0 | github.com::repository_view |
| 20260918 | shadowsocks | https://github.com/python/cpython | 2 | 0 | 0 | E2 | M2-M0 | github.com::repository_view |
| 20260918 | shadowsocks | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E2 | M2-M0 | github.com::repository_view |
| 20260918 | shadowsocks | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 1 | 0 | E2 | M2-M0 | bing.com::search_results_view |
| 20260918 | shadowsocks | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 0 | E2 | M2-M0 | bing.com::search_results_view |
| 20260918 | shadowsocks | https://www.bing.com/search?q=network+traffic+analysis | 0 | 2 | 0 | E2 | M2-M0 | bing.com::search_results_view |
| 20260918 | shadowsocks | https://www.bing.com/search?q=solar+system+facts | 0 | 0 | 0 | E2 | M2-M0 | bing.com::search_results_view |
| 20260918 | shadowsocks | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 1 | 0 | E2 | M2-M0 | bing.com::search_results_view |
| 20260918 | shadowsocks | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E2 | M2-M0 | youtube.com::search_results_view |
| 20260918 | shadowsocks | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 0 | E2 | M2-M0 | youtube.com::search_results_view |
| 20260918 | shadowsocks | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E2 | M2-M0 | youtube.com::search_results_view |
| 20260918 | shadowsocks | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 0 | E2 | M2-M0 | youtube.com::search_results_view |
| 20260918 | shadowsocks | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E2 | M2-M0 | youtube.com::search_results_view |
| 20260918 | shadowsocks | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E2 | M2-M0 | youtube.com::video_playback |
| 20260918 | shadowsocks | youtube_video:aircAruvnKk | 5 | 0 | 0 | E2 | M2-M0 | youtube.com::video_playback |
| 20260918 | shadowsocks | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E2 | M2-M0 | youtube.com::video_playback |
| 20260918 | shadowsocks | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E2 | M2-M0 | youtube.com::video_playback |
| 20260918 | shadowsocks | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E2 | M2-M0 | youtube.com::video_playback |
| 20260918 | trojan | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 1 | 0 | E2 | M2-M0 | developer.mozilla.org::document_view |
| 20260918 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 1 | 0 | E2 | M2-M0 | developer.mozilla.org::document_view |
| 20260918 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 2 | 0 | E2 | M2-M0 | developer.mozilla.org::document_view |
| 20260918 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 0 | 1 | E2 | M2-M0 | developer.mozilla.org::document_view |
| 20260918 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 1 | 0 | E2 | M2-M0 | developer.mozilla.org::document_view |
| 20260918 | trojan | https://en.wikipedia.org/wiki/Computer_network | 3 | 0 | 1 | E2 | M2-M0 | wikipedia.org::article_view |
| 20260918 | trojan | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 1 | 0 | E2 | M2-M0 | wikipedia.org::article_view |
| 20260918 | trojan | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 0 | 1 | E2 | M2-M0 | wikipedia.org::article_view |
| 20260918 | trojan | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 0 | E2 | M2-M0 | wikipedia.org::article_view |
| 20260918 | trojan | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E2 | M2-M0 | wikipedia.org::article_view |
| 20260918 | trojan | https://github.com/RakuLomis/TrafficTracer | 2 | 0 | 0 | E2 | M2-M0 | github.com::repository_view |
| 20260918 | trojan | https://github.com/numpy/numpy | 2 | 0 | 0 | E2 | M2-M0 | github.com::repository_view |
| 20260918 | trojan | https://github.com/pallets/flask | 2 | 1 | 0 | E2 | M2-M0 | github.com::repository_view |
| 20260918 | trojan | https://github.com/python/cpython | 2 | 0 | 0 | E2 | M2-M0 | github.com::repository_view |
| 20260918 | trojan | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E2 | M2-M0 | github.com::repository_view |
| 20260918 | trojan | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 1 | E2 | M2-M0 | bing.com::search_results_view |
| 20260918 | trojan | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 0 | E2 | M2-M0 | bing.com::search_results_view |
| 20260918 | trojan | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E2 | M2-M0 | bing.com::search_results_view |
| 20260918 | trojan | https://www.bing.com/search?q=solar+system+facts | 0 | 0 | 0 | E2 | M2-M0 | bing.com::search_results_view |
| 20260918 | trojan | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 0 | E2 | M2-M0 | bing.com::search_results_view |
| 20260918 | trojan | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E2 | M2-M0 | youtube.com::search_results_view |
| 20260918 | trojan | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 0 | E2 | M2-M0 | youtube.com::search_results_view |
| 20260918 | trojan | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E2 | M2-M0 | youtube.com::search_results_view |
| 20260918 | trojan | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 0 | E2 | M2-M0 | youtube.com::search_results_view |
| 20260918 | trojan | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E2 | M2-M0 | youtube.com::search_results_view |
| 20260918 | trojan | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E2 | M2-M0 | youtube.com::video_playback |
| 20260918 | trojan | youtube_video:aircAruvnKk | 5 | 0 | 0 | E2 | M2-M0 | youtube.com::video_playback |
| 20260918 | trojan | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E2 | M2-M0 | youtube.com::video_playback |
| 20260918 | trojan | youtube_video:eRsGyueVLvQ | 5 | 0 | 1 | E2 | M2-M0 | youtube.com::video_playback |
| 20260918 | trojan | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E2 | M2-M0 | youtube.com::video_playback |
| 20260918 | vless | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 0 | E2 | M2-M0 | developer.mozilla.org::document_view |
| 20260918 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 0 | 0 | E2 | M2-M0 | developer.mozilla.org::document_view |
| 20260918 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 0 | E2 | M2-M0 | developer.mozilla.org::document_view |
| 20260918 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 0 | 1 | E2 | M2-M0 | developer.mozilla.org::document_view |
| 20260918 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 0 | 2 | E2 | M2-M0 | developer.mozilla.org::document_view |
| 20260918 | vless | https://en.wikipedia.org/wiki/Computer_network | 3 | 0 | 0 | E2 | M2-M0 | wikipedia.org::article_view |
| 20260918 | vless | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 1 | 0 | E2 | M2-M0 | wikipedia.org::article_view |
| 20260918 | vless | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 1 | 0 | E2 | M2-M0 | wikipedia.org::article_view |
| 20260918 | vless | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 2 | 0 | E2 | M2-M0 | wikipedia.org::article_view |
| 20260918 | vless | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E2 | M2-M0 | wikipedia.org::article_view |
| 20260918 | vless | https://github.com/RakuLomis/TrafficTracer | 2 | 0 | 0 | E2 | M2-M0 | github.com::repository_view |
| 20260918 | vless | https://github.com/numpy/numpy | 2 | 0 | 0 | E2 | M2-M0 | github.com::repository_view |
| 20260918 | vless | https://github.com/pallets/flask | 2 | 0 | 0 | E2 | M2-M0 | github.com::repository_view |
| 20260918 | vless | https://github.com/python/cpython | 2 | 0 | 0 | E2 | M2-M0 | github.com::repository_view |
| 20260918 | vless | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E2 | M2-M0 | github.com::repository_view |
| 20260918 | vless | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 0 | E2 | M2-M0 | bing.com::search_results_view |
| 20260918 | vless | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 0 | E2 | M2-M0 | bing.com::search_results_view |
| 20260918 | vless | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E2 | M2-M0 | bing.com::search_results_view |
| 20260918 | vless | https://www.bing.com/search?q=solar+system+facts | 0 | 0 | 0 | E2 | M2-M0 | bing.com::search_results_view |
| 20260918 | vless | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 1 | E2 | M2-M0 | bing.com::search_results_view |
| 20260918 | vless | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E2 | M2-M0 | youtube.com::search_results_view |
| 20260918 | vless | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 0 | E2 | M2-M0 | youtube.com::search_results_view |
| 20260918 | vless | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 1 | E2 | M2-M0 | youtube.com::search_results_view |
| 20260918 | vless | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 0 | E2 | M2-M0 | youtube.com::search_results_view |
| 20260918 | vless | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E2 | M2-M0 | youtube.com::search_results_view |
| 20260918 | vless | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E2 | M2-M0 | youtube.com::video_playback |
| 20260918 | vless | youtube_video:aircAruvnKk | 5 | 0 | 0 | E2 | M2-M0 | youtube.com::video_playback |
| 20260918 | vless | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E2 | M2-M0 | youtube.com::video_playback |
| 20260918 | vless | youtube_video:eRsGyueVLvQ | 5 | 0 | 1 | E2 | M2-M0 | youtube.com::video_playback |
| 20260918 | vless | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E2 | M2-M0 | youtube.com::video_playback |
| 20260918 | vmess | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 0 | E2 | M2-M0 | developer.mozilla.org::document_view |
| 20260918 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 0 | 0 | E2 | M2-M0 | developer.mozilla.org::document_view |
| 20260918 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 0 | E2 | M2-M0 | developer.mozilla.org::document_view |
| 20260918 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 0 | 0 | E2 | M2-M0 | developer.mozilla.org::document_view |
| 20260918 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 0 | 0 | E2 | M2-M0 | developer.mozilla.org::document_view |
| 20260918 | vmess | https://en.wikipedia.org/wiki/Computer_network | 3 | 0 | 0 | E2 | M2-M0 | wikipedia.org::article_view |
| 20260918 | vmess | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 0 | E2 | M2-M0 | wikipedia.org::article_view |
| 20260918 | vmess | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 0 | 0 | E2 | M2-M0 | wikipedia.org::article_view |
| 20260918 | vmess | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 1 | E2 | M2-M0 | wikipedia.org::article_view |
| 20260918 | vmess | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E2 | M2-M0 | wikipedia.org::article_view |
| 20260918 | vmess | https://github.com/RakuLomis/TrafficTracer | 2 | 0 | 0 | E2 | M2-M0 | github.com::repository_view |
| 20260918 | vmess | https://github.com/numpy/numpy | 2 | 1 | 0 | E2 | M2-M0 | github.com::repository_view |
| 20260918 | vmess | https://github.com/pallets/flask | 2 | 0 | 0 | E2 | M2-M0 | github.com::repository_view |
| 20260918 | vmess | https://github.com/python/cpython | 2 | 0 | 0 | E2 | M2-M0 | github.com::repository_view |
| 20260918 | vmess | https://github.com/scikit-learn/scikit-learn | 2 | 2 | 0 | E2 | M2-M0 | github.com::repository_view |
| 20260918 | vmess | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 0 | E2 | M2-M0 | bing.com::search_results_view |
| 20260918 | vmess | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 0 | E2 | M2-M0 | bing.com::search_results_view |
| 20260918 | vmess | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E2 | M2-M0 | bing.com::search_results_view |
| 20260918 | vmess | https://www.bing.com/search?q=solar+system+facts | 0 | 1 | 1 | E2 | M2-M0 | bing.com::search_results_view |
| 20260918 | vmess | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 0 | E2 | M2-M0 | bing.com::search_results_view |
| 20260918 | vmess | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E2 | M2-M0 | youtube.com::search_results_view |
| 20260918 | vmess | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 0 | E2 | M2-M0 | youtube.com::search_results_view |
| 20260918 | vmess | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E2 | M2-M0 | youtube.com::search_results_view |
| 20260918 | vmess | https://www.youtube.com/results?search_query=piano+practice | 4 | 1 | 0 | E2 | M2-M0 | youtube.com::search_results_view |
| 20260918 | vmess | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E2 | M2-M0 | youtube.com::search_results_view |
| 20260918 | vmess | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E2 | M2-M0 | youtube.com::video_playback |
| 20260918 | vmess | youtube_video:aircAruvnKk | 5 | 0 | 0 | E2 | M2-M0 | youtube.com::video_playback |
| 20260918 | vmess | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E2 | M2-M0 | youtube.com::video_playback |
| 20260918 | vmess | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E2 | M2-M0 | youtube.com::video_playback |
| 20260918 | vmess | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E2 | M2-M0 | youtube.com::video_playback |
| 20260919 | anytls | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 0 | E2 | M2-M0 | developer.mozilla.org::document_view |
| 20260919 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 1 | 0 | E2 | M2-M0 | developer.mozilla.org::document_view |
| 20260919 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 0 | E2 | M2-M0 | developer.mozilla.org::document_view |
| 20260919 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 0 | 0 | E2 | M2-M0 | developer.mozilla.org::document_view |
| 20260919 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 0 | 0 | E2 | M2-M0 | developer.mozilla.org::document_view |
| 20260919 | anytls | https://en.wikipedia.org/wiki/Computer_network | 3 | 0 | 0 | E2 | M2-M0 | wikipedia.org::article_view |
| 20260919 | anytls | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 1 | E2 | M2-M0 | wikipedia.org::article_view |
| 20260919 | anytls | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 0 | 0 | E2 | M2-M0 | wikipedia.org::article_view |
| 20260919 | anytls | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 0 | E2 | M2-M0 | wikipedia.org::article_view |
| 20260919 | anytls | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E2 | M2-M0 | wikipedia.org::article_view |
| 20260919 | anytls | https://github.com/RakuLomis/TrafficTracer | 2 | 0 | 0 | E2 | M2-M0 | github.com::repository_view |
| 20260919 | anytls | https://github.com/numpy/numpy | 2 | 0 | 0 | E2 | M2-M0 | github.com::repository_view |
| 20260919 | anytls | https://github.com/pallets/flask | 2 | 0 | 0 | E2 | M2-M0 | github.com::repository_view |
| 20260919 | anytls | https://github.com/python/cpython | 2 | 0 | 0 | E2 | M2-M0 | github.com::repository_view |
| 20260919 | anytls | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E2 | M2-M0 | github.com::repository_view |
| 20260919 | anytls | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 0 | E2 | M2-M0 | bing.com::search_results_view |
| 20260919 | anytls | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 0 | E2 | M2-M0 | bing.com::search_results_view |
| 20260919 | anytls | https://www.bing.com/search?q=network+traffic+analysis | 0 | 1 | 0 | E2 | M2-M0 | bing.com::search_results_view |
| 20260919 | anytls | https://www.bing.com/search?q=solar+system+facts | 0 | 1 | 0 | E2 | M2-M0 | bing.com::search_results_view |
| 20260919 | anytls | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 0 | E2 | M2-M0 | bing.com::search_results_view |
| 20260919 | anytls | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E2 | M2-M0 | youtube.com::search_results_view |
| 20260919 | anytls | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 0 | E2 | M2-M0 | youtube.com::search_results_view |
| 20260919 | anytls | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E2 | M2-M0 | youtube.com::search_results_view |
| 20260919 | anytls | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 0 | E2 | M2-M0 | youtube.com::search_results_view |
| 20260919 | anytls | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 1 | E2 | M2-M0 | youtube.com::search_results_view |
| 20260919 | anytls | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E2 | M2-M0 | youtube.com::video_playback |
| 20260919 | anytls | youtube_video:aircAruvnKk | 5 | 0 | 0 | E2 | M2-M0 | youtube.com::video_playback |
| 20260919 | anytls | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E2 | M2-M0 | youtube.com::video_playback |
| 20260919 | anytls | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E2 | M2-M0 | youtube.com::video_playback |
| 20260919 | anytls | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E2 | M2-M0 | youtube.com::video_playback |
| 20260919 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 0 | E2 | M2-M0 | developer.mozilla.org::document_view |
| 20260919 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 0 | 0 | E2 | M2-M0 | developer.mozilla.org::document_view |
| 20260919 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 0 | E2 | M2-M0 | developer.mozilla.org::document_view |
| 20260919 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 0 | 0 | E2 | M2-M0 | developer.mozilla.org::document_view |
| 20260919 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 0 | 0 | E2 | M2-M0 | developer.mozilla.org::document_view |
| 20260919 | shadowsocks | https://en.wikipedia.org/wiki/Computer_network | 3 | 0 | 0 | E2 | M2-M0 | wikipedia.org::article_view |
| 20260919 | shadowsocks | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 0 | E2 | M2-M0 | wikipedia.org::article_view |
| 20260919 | shadowsocks | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 0 | 0 | E2 | M2-M0 | wikipedia.org::article_view |
| 20260919 | shadowsocks | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 0 | E2 | M2-M0 | wikipedia.org::article_view |
| 20260919 | shadowsocks | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E2 | M2-M0 | wikipedia.org::article_view |
| 20260919 | shadowsocks | https://github.com/RakuLomis/TrafficTracer | 2 | 0 | 0 | E2 | M2-M0 | github.com::repository_view |
| 20260919 | shadowsocks | https://github.com/numpy/numpy | 2 | 0 | 0 | E2 | M2-M0 | github.com::repository_view |
| 20260919 | shadowsocks | https://github.com/pallets/flask | 2 | 0 | 0 | E2 | M2-M0 | github.com::repository_view |
| 20260919 | shadowsocks | https://github.com/python/cpython | 2 | 0 | 0 | E2 | M2-M0 | github.com::repository_view |
| 20260919 | shadowsocks | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E2 | M2-M0 | github.com::repository_view |
| 20260919 | shadowsocks | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 0 | E2 | M2-M0 | bing.com::search_results_view |
| 20260919 | shadowsocks | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 0 | E2 | M2-M0 | bing.com::search_results_view |
| 20260919 | shadowsocks | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E2 | M2-M0 | bing.com::search_results_view |
| 20260919 | shadowsocks | https://www.bing.com/search?q=solar+system+facts | 0 | 0 | 0 | E2 | M2-M0 | bing.com::search_results_view |
| 20260919 | shadowsocks | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 1 | 0 | E2 | M2-M0 | bing.com::search_results_view |
| 20260919 | shadowsocks | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E2 | M2-M0 | youtube.com::search_results_view |
| 20260919 | shadowsocks | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 0 | E2 | M2-M0 | youtube.com::search_results_view |
| 20260919 | shadowsocks | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E2 | M2-M0 | youtube.com::search_results_view |
| 20260919 | shadowsocks | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 0 | E2 | M2-M0 | youtube.com::search_results_view |
| 20260919 | shadowsocks | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E2 | M2-M0 | youtube.com::search_results_view |
| 20260919 | shadowsocks | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E2 | M2-M0 | youtube.com::video_playback |
| 20260919 | shadowsocks | youtube_video:aircAruvnKk | 5 | 0 | 0 | E2 | M2-M0 | youtube.com::video_playback |
| 20260919 | shadowsocks | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E2 | M2-M0 | youtube.com::video_playback |
| 20260919 | shadowsocks | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E2 | M2-M0 | youtube.com::video_playback |
| 20260919 | shadowsocks | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E2 | M2-M0 | youtube.com::video_playback |
| 20260919 | trojan | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 0 | E2 | M2-M0 | developer.mozilla.org::document_view |
| 20260919 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 2 | 0 | E2 | M2-M0 | developer.mozilla.org::document_view |
| 20260919 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 1 | 0 | E2 | M2-M0 | developer.mozilla.org::document_view |
| 20260919 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 0 | 0 | E2 | M2-M0 | developer.mozilla.org::document_view |
| 20260919 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 1 | 0 | E2 | M2-M0 | developer.mozilla.org::document_view |
| 20260919 | trojan | https://en.wikipedia.org/wiki/Computer_network | 3 | 0 | 0 | E2 | M2-M0 | wikipedia.org::article_view |
| 20260919 | trojan | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 2 | E2 | M2-M0 | wikipedia.org::article_view |
| 20260919 | trojan | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 0 | 0 | E2 | M2-M0 | wikipedia.org::article_view |
| 20260919 | trojan | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 1 | E2 | M2-M0 | wikipedia.org::article_view |
| 20260919 | trojan | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E2 | M2-M0 | wikipedia.org::article_view |
| 20260919 | trojan | https://github.com/RakuLomis/TrafficTracer | 2 | 0 | 1 | E2 | M2-M0 | github.com::repository_view |
| 20260919 | trojan | https://github.com/numpy/numpy | 2 | 0 | 0 | E2 | M2-M0 | github.com::repository_view |
| 20260919 | trojan | https://github.com/pallets/flask | 2 | 0 | 0 | E2 | M2-M0 | github.com::repository_view |
| 20260919 | trojan | https://github.com/python/cpython | 2 | 0 | 0 | E2 | M2-M0 | github.com::repository_view |
| 20260919 | trojan | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E2 | M2-M0 | github.com::repository_view |
| 20260919 | trojan | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 1 | E2 | M2-M0 | bing.com::search_results_view |
| 20260919 | trojan | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 0 | E2 | M2-M0 | bing.com::search_results_view |
| 20260919 | trojan | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E2 | M2-M0 | bing.com::search_results_view |
| 20260919 | trojan | https://www.bing.com/search?q=solar+system+facts | 0 | 0 | 0 | E2 | M2-M0 | bing.com::search_results_view |
| 20260919 | trojan | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 0 | E2 | M2-M0 | bing.com::search_results_view |
| 20260919 | trojan | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E2 | M2-M0 | youtube.com::search_results_view |
| 20260919 | trojan | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 1 | 0 | E2 | M2-M0 | youtube.com::search_results_view |
| 20260919 | trojan | https://www.youtube.com/results?search_query=bread+baking | 4 | 1 | 0 | E2 | M2-M0 | youtube.com::search_results_view |
| 20260919 | trojan | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 0 | E2 | M2-M0 | youtube.com::search_results_view |
| 20260919 | trojan | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E2 | M2-M0 | youtube.com::search_results_view |
| 20260919 | trojan | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E2 | M2-M0 | youtube.com::video_playback |
| 20260919 | trojan | youtube_video:aircAruvnKk | 5 | 0 | 0 | E2 | M2-M0 | youtube.com::video_playback |
| 20260919 | trojan | youtube_video:aqz-KE-bpKQ | 5 | 0 | 1 | E2 | M2-M0 | youtube.com::video_playback |
| 20260919 | trojan | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E2 | M2-M0 | youtube.com::video_playback |
| 20260919 | trojan | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E2 | M2-M0 | youtube.com::video_playback |
| 20260919 | vless | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 0 | E2 | M2-M0 | developer.mozilla.org::document_view |
| 20260919 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 0 | 0 | E2 | M2-M0 | developer.mozilla.org::document_view |
| 20260919 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 0 | E2 | M2-M0 | developer.mozilla.org::document_view |
| 20260919 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 0 | 0 | E2 | M2-M0 | developer.mozilla.org::document_view |
| 20260919 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 0 | 0 | E2 | M2-M0 | developer.mozilla.org::document_view |
| 20260919 | vless | https://en.wikipedia.org/wiki/Computer_network | 3 | 0 | 2 | E2 | M2-M0 | wikipedia.org::article_view |
| 20260919 | vless | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 1 | E2 | M2-M0 | wikipedia.org::article_view |
| 20260919 | vless | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 0 | 0 | E2 | M2-M0 | wikipedia.org::article_view |
| 20260919 | vless | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 0 | E2 | M2-M0 | wikipedia.org::article_view |
| 20260919 | vless | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E2 | M2-M0 | wikipedia.org::article_view |
| 20260919 | vless | https://github.com/RakuLomis/TrafficTracer | 2 | 0 | 0 | E2 | M2-M0 | github.com::repository_view |
| 20260919 | vless | https://github.com/numpy/numpy | 2 | 0 | 0 | E2 | M2-M0 | github.com::repository_view |
| 20260919 | vless | https://github.com/pallets/flask | 2 | 1 | 0 | E2 | M2-M0 | github.com::repository_view |
| 20260919 | vless | https://github.com/python/cpython | 2 | 0 | 0 | E2 | M2-M0 | github.com::repository_view |
| 20260919 | vless | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E2 | M2-M0 | github.com::repository_view |
| 20260919 | vless | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 0 | E2 | M2-M0 | bing.com::search_results_view |
| 20260919 | vless | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 0 | E2 | M2-M0 | bing.com::search_results_view |
| 20260919 | vless | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E2 | M2-M0 | bing.com::search_results_view |
| 20260919 | vless | https://www.bing.com/search?q=solar+system+facts | 0 | 0 | 0 | E2 | M2-M0 | bing.com::search_results_view |
| 20260919 | vless | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 1 | E2 | M2-M0 | bing.com::search_results_view |
| 20260919 | vless | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E2 | M2-M0 | youtube.com::search_results_view |
| 20260919 | vless | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 1 | E2 | M2-M0 | youtube.com::search_results_view |
| 20260919 | vless | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E2 | M2-M0 | youtube.com::search_results_view |
| 20260919 | vless | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 0 | E2 | M2-M0 | youtube.com::search_results_view |
| 20260919 | vless | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E2 | M2-M0 | youtube.com::search_results_view |
| 20260919 | vless | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E2 | M2-M0 | youtube.com::video_playback |
| 20260919 | vless | youtube_video:aircAruvnKk | 5 | 0 | 1 | E2 | M2-M0 | youtube.com::video_playback |
| 20260919 | vless | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E2 | M2-M0 | youtube.com::video_playback |
| 20260919 | vless | youtube_video:eRsGyueVLvQ | 5 | 0 | 1 | E2 | M2-M0 | youtube.com::video_playback |
| 20260919 | vless | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E2 | M2-M0 | youtube.com::video_playback |
| 20260919 | vmess | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 0 | E2 | M2-M0 | developer.mozilla.org::document_view |
| 20260919 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 0 | 0 | E2 | M2-M0 | developer.mozilla.org::document_view |
| 20260919 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 0 | E2 | M2-M0 | developer.mozilla.org::document_view |
| 20260919 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 0 | 0 | E2 | M2-M0 | developer.mozilla.org::document_view |
| 20260919 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 0 | 0 | E2 | M2-M0 | developer.mozilla.org::document_view |
| 20260919 | vmess | https://en.wikipedia.org/wiki/Computer_network | 3 | 0 | 0 | E2 | M2-M0 | wikipedia.org::article_view |
| 20260919 | vmess | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 0 | E2 | M2-M0 | wikipedia.org::article_view |
| 20260919 | vmess | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 0 | 1 | E2 | M2-M0 | wikipedia.org::article_view |
| 20260919 | vmess | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 1 | E2 | M2-M0 | wikipedia.org::article_view |
| 20260919 | vmess | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E2 | M2-M0 | wikipedia.org::article_view |
| 20260919 | vmess | https://github.com/RakuLomis/TrafficTracer | 2 | 0 | 0 | E2 | M2-M0 | github.com::repository_view |
| 20260919 | vmess | https://github.com/numpy/numpy | 2 | 1 | 0 | E2 | M2-M0 | github.com::repository_view |
| 20260919 | vmess | https://github.com/pallets/flask | 2 | 1 | 0 | E2 | M2-M0 | github.com::repository_view |
| 20260919 | vmess | https://github.com/python/cpython | 2 | 1 | 0 | E2 | M2-M0 | github.com::repository_view |
| 20260919 | vmess | https://github.com/scikit-learn/scikit-learn | 2 | 2 | 0 | E2 | M2-M0 | github.com::repository_view |
| 20260919 | vmess | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 1 | E2 | M2-M0 | bing.com::search_results_view |
| 20260919 | vmess | https://www.bing.com/search?q=indoor+plant+care | 0 | 1 | 0 | E2 | M2-M0 | bing.com::search_results_view |
| 20260919 | vmess | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E2 | M2-M0 | bing.com::search_results_view |
| 20260919 | vmess | https://www.bing.com/search?q=solar+system+facts | 0 | 0 | 0 | E2 | M2-M0 | bing.com::search_results_view |
| 20260919 | vmess | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 0 | E2 | M2-M0 | bing.com::search_results_view |
| 20260919 | vmess | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E2 | M2-M0 | youtube.com::search_results_view |
| 20260919 | vmess | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 0 | E2 | M2-M0 | youtube.com::search_results_view |
| 20260919 | vmess | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E2 | M2-M0 | youtube.com::search_results_view |
| 20260919 | vmess | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 0 | E2 | M2-M0 | youtube.com::search_results_view |
| 20260919 | vmess | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E2 | M2-M0 | youtube.com::search_results_view |
| 20260919 | vmess | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E2 | M2-M0 | youtube.com::video_playback |
| 20260919 | vmess | youtube_video:aircAruvnKk | 5 | 0 | 0 | E2 | M2-M0 | youtube.com::video_playback |
| 20260919 | vmess | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E2 | M2-M0 | youtube.com::video_playback |
| 20260919 | vmess | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E2 | M2-M0 | youtube.com::video_playback |
| 20260919 | vmess | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E2 | M2-M0 | youtube.com::video_playback |
| 20260920 | anytls | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 0 | E2 | M2-M0 | developer.mozilla.org::document_view |
| 20260920 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 2 | 0 | E2 | M2-M0 | developer.mozilla.org::document_view |
| 20260920 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 0 | E2 | M2-M0 | developer.mozilla.org::document_view |
| 20260920 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 0 | 0 | E2 | M2-M0 | developer.mozilla.org::document_view |
| 20260920 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 0 | 0 | E2 | M2-M0 | developer.mozilla.org::document_view |
| 20260920 | anytls | https://en.wikipedia.org/wiki/Computer_network | 3 | 0 | 0 | E2 | M2-M0 | wikipedia.org::article_view |
| 20260920 | anytls | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 0 | E2 | M2-M0 | wikipedia.org::article_view |
| 20260920 | anytls | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 0 | 0 | E2 | M2-M0 | wikipedia.org::article_view |
| 20260920 | anytls | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 0 | E2 | M2-M0 | wikipedia.org::article_view |
| 20260920 | anytls | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 1 | E2 | M2-M0 | wikipedia.org::article_view |
| 20260920 | anytls | https://github.com/RakuLomis/TrafficTracer | 2 | 0 | 0 | E2 | M2-M0 | github.com::repository_view |
| 20260920 | anytls | https://github.com/numpy/numpy | 2 | 0 | 0 | E2 | M2-M0 | github.com::repository_view |
| 20260920 | anytls | https://github.com/pallets/flask | 2 | 1 | 0 | E2 | M2-M0 | github.com::repository_view |
| 20260920 | anytls | https://github.com/python/cpython | 2 | 0 | 0 | E2 | M2-M0 | github.com::repository_view |
| 20260920 | anytls | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E2 | M2-M0 | github.com::repository_view |
| 20260920 | anytls | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 0 | E2 | M2-M0 | bing.com::search_results_view |
| 20260920 | anytls | https://www.bing.com/search?q=indoor+plant+care | 0 | 2 | 0 | E2 | M2-M0 | bing.com::search_results_view |
| 20260920 | anytls | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E2 | M2-M0 | bing.com::search_results_view |
| 20260920 | anytls | https://www.bing.com/search?q=solar+system+facts | 0 | 1 | 0 | E2 | M2-M0 | bing.com::search_results_view |
| 20260920 | anytls | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 0 | E2 | M2-M0 | bing.com::search_results_view |
| 20260920 | anytls | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E2 | M2-M0 | youtube.com::search_results_view |
| 20260920 | anytls | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 0 | E2 | M2-M0 | youtube.com::search_results_view |
| 20260920 | anytls | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E2 | M2-M0 | youtube.com::search_results_view |
| 20260920 | anytls | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 0 | E2 | M2-M0 | youtube.com::search_results_view |
| 20260920 | anytls | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E2 | M2-M0 | youtube.com::search_results_view |
| 20260920 | anytls | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E2 | M2-M0 | youtube.com::video_playback |
| 20260920 | anytls | youtube_video:aircAruvnKk | 5 | 0 | 0 | E2 | M2-M0 | youtube.com::video_playback |
| 20260920 | anytls | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E2 | M2-M0 | youtube.com::video_playback |
| 20260920 | anytls | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E2 | M2-M0 | youtube.com::video_playback |
| 20260920 | anytls | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E2 | M2-M0 | youtube.com::video_playback |
| 20260920 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 0 | E2 | M2-M0 | developer.mozilla.org::document_view |
| 20260920 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 0 | 0 | E2 | M2-M0 | developer.mozilla.org::document_view |
| 20260920 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 0 | E2 | M2-M0 | developer.mozilla.org::document_view |
| 20260920 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 0 | 0 | E2 | M2-M0 | developer.mozilla.org::document_view |
| 20260920 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 0 | 0 | E2 | M2-M0 | developer.mozilla.org::document_view |
| 20260920 | shadowsocks | https://en.wikipedia.org/wiki/Computer_network | 3 | 0 | 0 | E2 | M2-M0 | wikipedia.org::article_view |
| 20260920 | shadowsocks | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 0 | E2 | M2-M0 | wikipedia.org::article_view |
| 20260920 | shadowsocks | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 0 | 0 | E2 | M2-M0 | wikipedia.org::article_view |
| 20260920 | shadowsocks | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 0 | E2 | M2-M0 | wikipedia.org::article_view |
| 20260920 | shadowsocks | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E2 | M2-M0 | wikipedia.org::article_view |
| 20260920 | shadowsocks | https://github.com/RakuLomis/TrafficTracer | 2 | 0 | 0 | E2 | M2-M0 | github.com::repository_view |
| 20260920 | shadowsocks | https://github.com/numpy/numpy | 2 | 0 | 0 | E2 | M2-M0 | github.com::repository_view |
| 20260920 | shadowsocks | https://github.com/pallets/flask | 2 | 0 | 0 | E2 | M2-M0 | github.com::repository_view |
| 20260920 | shadowsocks | https://github.com/python/cpython | 2 | 0 | 0 | E2 | M2-M0 | github.com::repository_view |
| 20260920 | shadowsocks | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E2 | M2-M0 | github.com::repository_view |
| 20260920 | shadowsocks | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 0 | E2 | M2-M0 | bing.com::search_results_view |
| 20260920 | shadowsocks | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 0 | E2 | M2-M0 | bing.com::search_results_view |
| 20260920 | shadowsocks | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E2 | M2-M0 | bing.com::search_results_view |
| 20260920 | shadowsocks | https://www.bing.com/search?q=solar+system+facts | 0 | 1 | 0 | E2 | M2-M0 | bing.com::search_results_view |
| 20260920 | shadowsocks | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 1 | 1 | E2 | M2-M0 | bing.com::search_results_view |
| 20260920 | shadowsocks | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E2 | M2-M0 | youtube.com::search_results_view |
| 20260920 | shadowsocks | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 0 | E2 | M2-M0 | youtube.com::search_results_view |
| 20260920 | shadowsocks | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E2 | M2-M0 | youtube.com::search_results_view |
| 20260920 | shadowsocks | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 0 | E2 | M2-M0 | youtube.com::search_results_view |
| 20260920 | shadowsocks | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E2 | M2-M0 | youtube.com::search_results_view |
| 20260920 | shadowsocks | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E2 | M2-M0 | youtube.com::video_playback |
| 20260920 | shadowsocks | youtube_video:aircAruvnKk | 5 | 0 | 0 | E2 | M2-M0 | youtube.com::video_playback |
| 20260920 | shadowsocks | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E2 | M2-M0 | youtube.com::video_playback |
| 20260920 | shadowsocks | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E2 | M2-M0 | youtube.com::video_playback |
| 20260920 | shadowsocks | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E2 | M2-M0 | youtube.com::video_playback |
| 20260920 | trojan | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 1 | 0 | E2 | M2-M0 | developer.mozilla.org::document_view |
| 20260920 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 1 | 0 | E2 | M2-M0 | developer.mozilla.org::document_view |
| 20260920 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 0 | E2 | M2-M0 | developer.mozilla.org::document_view |
| 20260920 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 1 | 0 | E2 | M2-M0 | developer.mozilla.org::document_view |
| 20260920 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 1 | 0 | E2 | M2-M0 | developer.mozilla.org::document_view |
| 20260920 | trojan | https://en.wikipedia.org/wiki/Computer_network | 3 | 0 | 1 | E2 | M2-M0 | wikipedia.org::article_view |
| 20260920 | trojan | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 2 | E2 | M2-M0 | wikipedia.org::article_view |
| 20260920 | trojan | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 0 | 2 | E2 | M2-M0 | wikipedia.org::article_view |
| 20260920 | trojan | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 1 | E2 | M2-M0 | wikipedia.org::article_view |
| 20260920 | trojan | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E2 | M2-M0 | wikipedia.org::article_view |
| 20260920 | trojan | https://github.com/RakuLomis/TrafficTracer | 2 | 0 | 0 | E2 | M2-M0 | github.com::repository_view |
| 20260920 | trojan | https://github.com/numpy/numpy | 2 | 0 | 0 | E2 | M2-M0 | github.com::repository_view |
| 20260920 | trojan | https://github.com/pallets/flask | 2 | 0 | 0 | E2 | M2-M0 | github.com::repository_view |
| 20260920 | trojan | https://github.com/python/cpython | 2 | 0 | 0 | E2 | M2-M0 | github.com::repository_view |
| 20260920 | trojan | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E2 | M2-M0 | github.com::repository_view |
| 20260920 | trojan | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 0 | E2 | M2-M0 | bing.com::search_results_view |
| 20260920 | trojan | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 0 | E2 | M2-M0 | bing.com::search_results_view |
| 20260920 | trojan | https://www.bing.com/search?q=network+traffic+analysis | 0 | 1 | 0 | E2 | M2-M0 | bing.com::search_results_view |
| 20260920 | trojan | https://www.bing.com/search?q=solar+system+facts | 0 | 0 | 0 | E2 | M2-M0 | bing.com::search_results_view |
| 20260920 | trojan | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 0 | E2 | M2-M0 | bing.com::search_results_view |
| 20260920 | trojan | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E2 | M2-M0 | youtube.com::search_results_view |
| 20260920 | trojan | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 1 | 0 | E2 | M2-M0 | youtube.com::search_results_view |
| 20260920 | trojan | https://www.youtube.com/results?search_query=bread+baking | 4 | 1 | 0 | E2 | M2-M0 | youtube.com::search_results_view |
| 20260920 | trojan | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 0 | E2 | M2-M0 | youtube.com::search_results_view |
| 20260920 | trojan | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E2 | M2-M0 | youtube.com::search_results_view |
| 20260920 | trojan | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E2 | M2-M0 | youtube.com::video_playback |
| 20260920 | trojan | youtube_video:aircAruvnKk | 5 | 0 | 0 | E2 | M2-M0 | youtube.com::video_playback |
| 20260920 | trojan | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E2 | M2-M0 | youtube.com::video_playback |
| 20260920 | trojan | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E2 | M2-M0 | youtube.com::video_playback |
| 20260920 | trojan | youtube_video:sAWK0mgrMp4 | 5 | 0 | 1 | E2 | M2-M0 | youtube.com::video_playback |
| 20260920 | vless | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 0 | E2 | M2-M0 | developer.mozilla.org::document_view |
| 20260920 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 0 | 0 | E2 | M2-M0 | developer.mozilla.org::document_view |
| 20260920 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 0 | E2 | M2-M0 | developer.mozilla.org::document_view |
| 20260920 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 0 | 0 | E2 | M2-M0 | developer.mozilla.org::document_view |
| 20260920 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 0 | 0 | E2 | M2-M0 | developer.mozilla.org::document_view |
| 20260920 | vless | https://en.wikipedia.org/wiki/Computer_network | 3 | 0 | 0 | E2 | M2-M0 | wikipedia.org::article_view |
| 20260920 | vless | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 0 | E2 | M2-M0 | wikipedia.org::article_view |
| 20260920 | vless | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 0 | 0 | E2 | M2-M0 | wikipedia.org::article_view |
| 20260920 | vless | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 1 | 0 | E2 | M2-M0 | wikipedia.org::article_view |
| 20260920 | vless | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E2 | M2-M0 | wikipedia.org::article_view |
| 20260920 | vless | https://github.com/RakuLomis/TrafficTracer | 2 | 0 | 0 | E2 | M2-M0 | github.com::repository_view |
| 20260920 | vless | https://github.com/numpy/numpy | 2 | 0 | 0 | E2 | M2-M0 | github.com::repository_view |
| 20260920 | vless | https://github.com/pallets/flask | 2 | 0 | 0 | E2 | M2-M0 | github.com::repository_view |
| 20260920 | vless | https://github.com/python/cpython | 2 | 0 | 0 | E2 | M2-M0 | github.com::repository_view |
| 20260920 | vless | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E2 | M2-M0 | github.com::repository_view |
| 20260920 | vless | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 0 | E2 | M2-M0 | bing.com::search_results_view |
| 20260920 | vless | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 1 | E2 | M2-M0 | bing.com::search_results_view |
| 20260920 | vless | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E2 | M2-M0 | bing.com::search_results_view |
| 20260920 | vless | https://www.bing.com/search?q=solar+system+facts | 0 | 1 | 0 | E2 | M2-M0 | bing.com::search_results_view |
| 20260920 | vless | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 1 | E2 | M2-M0 | bing.com::search_results_view |
| 20260920 | vless | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E2 | M2-M0 | youtube.com::search_results_view |
| 20260920 | vless | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 1 | E2 | M2-M0 | youtube.com::search_results_view |
| 20260920 | vless | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E2 | M2-M0 | youtube.com::search_results_view |
| 20260920 | vless | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 0 | E2 | M2-M0 | youtube.com::search_results_view |
| 20260920 | vless | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E2 | M2-M0 | youtube.com::search_results_view |
| 20260920 | vless | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E2 | M2-M0 | youtube.com::video_playback |
| 20260920 | vless | youtube_video:aircAruvnKk | 5 | 0 | 0 | E2 | M2-M0 | youtube.com::video_playback |
| 20260920 | vless | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E2 | M2-M0 | youtube.com::video_playback |
| 20260920 | vless | youtube_video:eRsGyueVLvQ | 5 | 0 | 1 | E2 | M2-M0 | youtube.com::video_playback |
| 20260920 | vless | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E2 | M2-M0 | youtube.com::video_playback |
| 20260920 | vmess | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 0 | E2 | M2-M0 | developer.mozilla.org::document_view |
| 20260920 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 0 | 0 | E2 | M2-M0 | developer.mozilla.org::document_view |
| 20260920 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 0 | E2 | M2-M0 | developer.mozilla.org::document_view |
| 20260920 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 0 | 0 | E2 | M2-M0 | developer.mozilla.org::document_view |
| 20260920 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 0 | 0 | E2 | M2-M0 | developer.mozilla.org::document_view |
| 20260920 | vmess | https://en.wikipedia.org/wiki/Computer_network | 3 | 0 | 1 | E2 | M2-M0 | wikipedia.org::article_view |
| 20260920 | vmess | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 0 | E2 | M2-M0 | wikipedia.org::article_view |
| 20260920 | vmess | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 0 | 0 | E2 | M2-M0 | wikipedia.org::article_view |
| 20260920 | vmess | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 1 | E2 | M2-M0 | wikipedia.org::article_view |
| 20260920 | vmess | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E2 | M2-M0 | wikipedia.org::article_view |
| 20260920 | vmess | https://github.com/RakuLomis/TrafficTracer | 2 | 0 | 0 | E2 | M2-M0 | github.com::repository_view |
| 20260920 | vmess | https://github.com/numpy/numpy | 2 | 1 | 0 | E2 | M2-M0 | github.com::repository_view |
| 20260920 | vmess | https://github.com/pallets/flask | 2 | 0 | 0 | E2 | M2-M0 | github.com::repository_view |
| 20260920 | vmess | https://github.com/python/cpython | 2 | 0 | 0 | E2 | M2-M0 | github.com::repository_view |
| 20260920 | vmess | https://github.com/scikit-learn/scikit-learn | 2 | 2 | 0 | E2 | M2-M0 | github.com::repository_view |
| 20260920 | vmess | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 1 | 0 | E2 | M2-M0 | bing.com::search_results_view |
| 20260920 | vmess | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 0 | E2 | M2-M0 | bing.com::search_results_view |
| 20260920 | vmess | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E2 | M2-M0 | bing.com::search_results_view |
| 20260920 | vmess | https://www.bing.com/search?q=solar+system+facts | 0 | 0 | 0 | E2 | M2-M0 | bing.com::search_results_view |
| 20260920 | vmess | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 0 | E2 | M2-M0 | bing.com::search_results_view |
| 20260920 | vmess | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E2 | M2-M0 | youtube.com::search_results_view |
| 20260920 | vmess | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 0 | E2 | M2-M0 | youtube.com::search_results_view |
| 20260920 | vmess | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E2 | M2-M0 | youtube.com::search_results_view |
| 20260920 | vmess | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 0 | E2 | M2-M0 | youtube.com::search_results_view |
| 20260920 | vmess | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E2 | M2-M0 | youtube.com::search_results_view |
| 20260920 | vmess | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E2 | M2-M0 | youtube.com::video_playback |
| 20260920 | vmess | youtube_video:aircAruvnKk | 5 | 0 | 1 | E2 | M2-M0 | youtube.com::video_playback |
| 20260920 | vmess | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E2 | M2-M0 | youtube.com::video_playback |
| 20260920 | vmess | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E2 | M2-M0 | youtube.com::video_playback |
| 20260920 | vmess | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E2 | M2-M0 | youtube.com::video_playback |
| 20260918 | anytls | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 0 | E2 | M2-M1 | developer.mozilla.org::document_view |
| 20260918 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 1 | 0 | E2 | M2-M1 | developer.mozilla.org::document_view |
| 20260918 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 0 | E2 | M2-M1 | developer.mozilla.org::document_view |
| 20260918 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 3 | 0 | E2 | M2-M1 | developer.mozilla.org::document_view |
| 20260918 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 2 | 0 | E2 | M2-M1 | developer.mozilla.org::document_view |
| 20260918 | anytls | https://en.wikipedia.org/wiki/Computer_network | 3 | 1 | 1 | E2 | M2-M1 | wikipedia.org::article_view |
| 20260918 | anytls | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 2 | 0 | E2 | M2-M1 | wikipedia.org::article_view |
| 20260918 | anytls | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 1 | 0 | E2 | M2-M1 | wikipedia.org::article_view |
| 20260918 | anytls | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 2 | 0 | E2 | M2-M1 | wikipedia.org::article_view |
| 20260918 | anytls | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E2 | M2-M1 | wikipedia.org::article_view |
| 20260918 | anytls | https://github.com/RakuLomis/TrafficTracer | 2 | 0 | 1 | E2 | M2-M1 | github.com::repository_view |
| 20260918 | anytls | https://github.com/numpy/numpy | 2 | 0 | 0 | E2 | M2-M1 | github.com::repository_view |
| 20260918 | anytls | https://github.com/pallets/flask | 2 | 1 | 0 | E2 | M2-M1 | github.com::repository_view |
| 20260918 | anytls | https://github.com/python/cpython | 2 | 0 | 0 | E2 | M2-M1 | github.com::repository_view |
| 20260918 | anytls | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E2 | M2-M1 | github.com::repository_view |
| 20260918 | anytls | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 0 | E2 | M2-M1 | bing.com::search_results_view |
| 20260918 | anytls | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 1 | E2 | M2-M1 | bing.com::search_results_view |
| 20260918 | anytls | https://www.bing.com/search?q=network+traffic+analysis | 0 | 1 | 0 | E2 | M2-M1 | bing.com::search_results_view |
| 20260918 | anytls | https://www.bing.com/search?q=solar+system+facts | 0 | 2 | 0 | E2 | M2-M1 | bing.com::search_results_view |
| 20260918 | anytls | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 0 | E2 | M2-M1 | bing.com::search_results_view |
| 20260918 | anytls | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E2 | M2-M1 | youtube.com::search_results_view |
| 20260918 | anytls | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 1 | E2 | M2-M1 | youtube.com::search_results_view |
| 20260918 | anytls | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E2 | M2-M1 | youtube.com::search_results_view |
| 20260918 | anytls | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 0 | E2 | M2-M1 | youtube.com::search_results_view |
| 20260918 | anytls | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 1 | E2 | M2-M1 | youtube.com::search_results_view |
| 20260918 | anytls | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E2 | M2-M1 | youtube.com::video_playback |
| 20260918 | anytls | youtube_video:aircAruvnKk | 5 | 0 | 0 | E2 | M2-M1 | youtube.com::video_playback |
| 20260918 | anytls | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E2 | M2-M1 | youtube.com::video_playback |
| 20260918 | anytls | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E2 | M2-M1 | youtube.com::video_playback |
| 20260918 | anytls | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E2 | M2-M1 | youtube.com::video_playback |
| 20260918 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 1 | 0 | E2 | M2-M1 | developer.mozilla.org::document_view |
| 20260918 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 0 | 0 | E2 | M2-M1 | developer.mozilla.org::document_view |
| 20260918 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 0 | E2 | M2-M1 | developer.mozilla.org::document_view |
| 20260918 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 0 | 0 | E2 | M2-M1 | developer.mozilla.org::document_view |
| 20260918 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 0 | 0 | E2 | M2-M1 | developer.mozilla.org::document_view |
| 20260918 | shadowsocks | https://en.wikipedia.org/wiki/Computer_network | 3 | 0 | 0 | E2 | M2-M1 | wikipedia.org::article_view |
| 20260918 | shadowsocks | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 0 | E2 | M2-M1 | wikipedia.org::article_view |
| 20260918 | shadowsocks | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 0 | 0 | E2 | M2-M1 | wikipedia.org::article_view |
| 20260918 | shadowsocks | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 0 | E2 | M2-M1 | wikipedia.org::article_view |
| 20260918 | shadowsocks | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E2 | M2-M1 | wikipedia.org::article_view |
| 20260918 | shadowsocks | https://github.com/RakuLomis/TrafficTracer | 2 | 0 | 0 | E2 | M2-M1 | github.com::repository_view |
| 20260918 | shadowsocks | https://github.com/numpy/numpy | 2 | 0 | 0 | E2 | M2-M1 | github.com::repository_view |
| 20260918 | shadowsocks | https://github.com/pallets/flask | 2 | 0 | 0 | E2 | M2-M1 | github.com::repository_view |
| 20260918 | shadowsocks | https://github.com/python/cpython | 2 | 0 | 0 | E2 | M2-M1 | github.com::repository_view |
| 20260918 | shadowsocks | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E2 | M2-M1 | github.com::repository_view |
| 20260918 | shadowsocks | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 1 | 0 | E2 | M2-M1 | bing.com::search_results_view |
| 20260918 | shadowsocks | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 0 | E2 | M2-M1 | bing.com::search_results_view |
| 20260918 | shadowsocks | https://www.bing.com/search?q=network+traffic+analysis | 0 | 4 | 0 | E2 | M2-M1 | bing.com::search_results_view |
| 20260918 | shadowsocks | https://www.bing.com/search?q=solar+system+facts | 0 | 2 | 0 | E2 | M2-M1 | bing.com::search_results_view |
| 20260918 | shadowsocks | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 1 | 0 | E2 | M2-M1 | bing.com::search_results_view |
| 20260918 | shadowsocks | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 1 | 0 | E2 | M2-M1 | youtube.com::search_results_view |
| 20260918 | shadowsocks | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 0 | E2 | M2-M1 | youtube.com::search_results_view |
| 20260918 | shadowsocks | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E2 | M2-M1 | youtube.com::search_results_view |
| 20260918 | shadowsocks | https://www.youtube.com/results?search_query=piano+practice | 4 | 2 | 0 | E2 | M2-M1 | youtube.com::search_results_view |
| 20260918 | shadowsocks | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E2 | M2-M1 | youtube.com::search_results_view |
| 20260918 | shadowsocks | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E2 | M2-M1 | youtube.com::video_playback |
| 20260918 | shadowsocks | youtube_video:aircAruvnKk | 5 | 0 | 0 | E2 | M2-M1 | youtube.com::video_playback |
| 20260918 | shadowsocks | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E2 | M2-M1 | youtube.com::video_playback |
| 20260918 | shadowsocks | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E2 | M2-M1 | youtube.com::video_playback |
| 20260918 | shadowsocks | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E2 | M2-M1 | youtube.com::video_playback |
| 20260918 | trojan | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 1 | 0 | E2 | M2-M1 | developer.mozilla.org::document_view |
| 20260918 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 0 | 1 | E2 | M2-M1 | developer.mozilla.org::document_view |
| 20260918 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 2 | 0 | E2 | M2-M1 | developer.mozilla.org::document_view |
| 20260918 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 0 | 0 | E2 | M2-M1 | developer.mozilla.org::document_view |
| 20260918 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 1 | 0 | E2 | M2-M1 | developer.mozilla.org::document_view |
| 20260918 | trojan | https://en.wikipedia.org/wiki/Computer_network | 3 | 0 | 0 | E2 | M2-M1 | wikipedia.org::article_view |
| 20260918 | trojan | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 2 | E2 | M2-M1 | wikipedia.org::article_view |
| 20260918 | trojan | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 0 | 1 | E2 | M2-M1 | wikipedia.org::article_view |
| 20260918 | trojan | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 1 | E2 | M2-M1 | wikipedia.org::article_view |
| 20260918 | trojan | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 2 | 0 | E2 | M2-M1 | wikipedia.org::article_view |
| 20260918 | trojan | https://github.com/RakuLomis/TrafficTracer | 2 | 0 | 0 | E2 | M2-M1 | github.com::repository_view |
| 20260918 | trojan | https://github.com/numpy/numpy | 2 | 0 | 0 | E2 | M2-M1 | github.com::repository_view |
| 20260918 | trojan | https://github.com/pallets/flask | 2 | 1 | 0 | E2 | M2-M1 | github.com::repository_view |
| 20260918 | trojan | https://github.com/python/cpython | 2 | 0 | 0 | E2 | M2-M1 | github.com::repository_view |
| 20260918 | trojan | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E2 | M2-M1 | github.com::repository_view |
| 20260918 | trojan | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 1 | E2 | M2-M1 | bing.com::search_results_view |
| 20260918 | trojan | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 0 | E2 | M2-M1 | bing.com::search_results_view |
| 20260918 | trojan | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 1 | E2 | M2-M1 | bing.com::search_results_view |
| 20260918 | trojan | https://www.bing.com/search?q=solar+system+facts | 0 | 0 | 3 | E2 | M2-M1 | bing.com::search_results_view |
| 20260918 | trojan | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 1 | E2 | M2-M1 | bing.com::search_results_view |
| 20260918 | trojan | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E2 | M2-M1 | youtube.com::search_results_view |
| 20260918 | trojan | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 1 | 1 | E2 | M2-M1 | youtube.com::search_results_view |
| 20260918 | trojan | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E2 | M2-M1 | youtube.com::search_results_view |
| 20260918 | trojan | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 0 | E2 | M2-M1 | youtube.com::search_results_view |
| 20260918 | trojan | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 1 | E2 | M2-M1 | youtube.com::search_results_view |
| 20260918 | trojan | youtube_video:R6MlUcmOul8 | 5 | 0 | 2 | E2 | M2-M1 | youtube.com::video_playback |
| 20260918 | trojan | youtube_video:aircAruvnKk | 5 | 0 | 1 | E2 | M2-M1 | youtube.com::video_playback |
| 20260918 | trojan | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E2 | M2-M1 | youtube.com::video_playback |
| 20260918 | trojan | youtube_video:eRsGyueVLvQ | 5 | 0 | 3 | E2 | M2-M1 | youtube.com::video_playback |
| 20260918 | trojan | youtube_video:sAWK0mgrMp4 | 5 | 0 | 1 | E2 | M2-M1 | youtube.com::video_playback |
| 20260918 | vless | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 0 | E2 | M2-M1 | developer.mozilla.org::document_view |
| 20260918 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 0 | 4 | E2 | M2-M1 | developer.mozilla.org::document_view |
| 20260918 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 2 | E2 | M2-M1 | developer.mozilla.org::document_view |
| 20260918 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 0 | 2 | E2 | M2-M1 | developer.mozilla.org::document_view |
| 20260918 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 0 | 2 | E2 | M2-M1 | developer.mozilla.org::document_view |
| 20260918 | vless | https://en.wikipedia.org/wiki/Computer_network | 3 | 4 | 0 | E2 | M2-M1 | wikipedia.org::article_view |
| 20260918 | vless | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 3 | 0 | E2 | M2-M1 | wikipedia.org::article_view |
| 20260918 | vless | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 2 | 0 | E2 | M2-M1 | wikipedia.org::article_view |
| 20260918 | vless | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 1 | 0 | E2 | M2-M1 | wikipedia.org::article_view |
| 20260918 | vless | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 2 | 0 | E2 | M2-M1 | wikipedia.org::article_view |
| 20260918 | vless | https://github.com/RakuLomis/TrafficTracer | 2 | 0 | 0 | E2 | M2-M1 | github.com::repository_view |
| 20260918 | vless | https://github.com/numpy/numpy | 2 | 0 | 0 | E2 | M2-M1 | github.com::repository_view |
| 20260918 | vless | https://github.com/pallets/flask | 2 | 0 | 0 | E2 | M2-M1 | github.com::repository_view |
| 20260918 | vless | https://github.com/python/cpython | 2 | 0 | 0 | E2 | M2-M1 | github.com::repository_view |
| 20260918 | vless | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E2 | M2-M1 | github.com::repository_view |
| 20260918 | vless | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 0 | E2 | M2-M1 | bing.com::search_results_view |
| 20260918 | vless | https://www.bing.com/search?q=indoor+plant+care | 0 | 1 | 0 | E2 | M2-M1 | bing.com::search_results_view |
| 20260918 | vless | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E2 | M2-M1 | bing.com::search_results_view |
| 20260918 | vless | https://www.bing.com/search?q=solar+system+facts | 0 | 0 | 0 | E2 | M2-M1 | bing.com::search_results_view |
| 20260918 | vless | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 1 | E2 | M2-M1 | bing.com::search_results_view |
| 20260918 | vless | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E2 | M2-M1 | youtube.com::search_results_view |
| 20260918 | vless | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 1 | E2 | M2-M1 | youtube.com::search_results_view |
| 20260918 | vless | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 2 | E2 | M2-M1 | youtube.com::search_results_view |
| 20260918 | vless | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 0 | E2 | M2-M1 | youtube.com::search_results_view |
| 20260918 | vless | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 1 | E2 | M2-M1 | youtube.com::search_results_view |
| 20260918 | vless | youtube_video:R6MlUcmOul8 | 5 | 0 | 1 | E2 | M2-M1 | youtube.com::video_playback |
| 20260918 | vless | youtube_video:aircAruvnKk | 5 | 0 | 0 | E2 | M2-M1 | youtube.com::video_playback |
| 20260918 | vless | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E2 | M2-M1 | youtube.com::video_playback |
| 20260918 | vless | youtube_video:eRsGyueVLvQ | 5 | 0 | 2 | E2 | M2-M1 | youtube.com::video_playback |
| 20260918 | vless | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E2 | M2-M1 | youtube.com::video_playback |
| 20260918 | vmess | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 0 | E2 | M2-M1 | developer.mozilla.org::document_view |
| 20260918 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 0 | 0 | E2 | M2-M1 | developer.mozilla.org::document_view |
| 20260918 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 0 | E2 | M2-M1 | developer.mozilla.org::document_view |
| 20260918 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 0 | 0 | E2 | M2-M1 | developer.mozilla.org::document_view |
| 20260918 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 1 | 0 | E2 | M2-M1 | developer.mozilla.org::document_view |
| 20260918 | vmess | https://en.wikipedia.org/wiki/Computer_network | 3 | 1 | 0 | E2 | M2-M1 | wikipedia.org::article_view |
| 20260918 | vmess | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 0 | E2 | M2-M1 | wikipedia.org::article_view |
| 20260918 | vmess | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 1 | 0 | E2 | M2-M1 | wikipedia.org::article_view |
| 20260918 | vmess | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 1 | E2 | M2-M1 | wikipedia.org::article_view |
| 20260918 | vmess | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E2 | M2-M1 | wikipedia.org::article_view |
| 20260918 | vmess | https://github.com/RakuLomis/TrafficTracer | 2 | 0 | 0 | E2 | M2-M1 | github.com::repository_view |
| 20260918 | vmess | https://github.com/numpy/numpy | 2 | 0 | 0 | E2 | M2-M1 | github.com::repository_view |
| 20260918 | vmess | https://github.com/pallets/flask | 2 | 0 | 0 | E2 | M2-M1 | github.com::repository_view |
| 20260918 | vmess | https://github.com/python/cpython | 2 | 0 | 0 | E2 | M2-M1 | github.com::repository_view |
| 20260918 | vmess | https://github.com/scikit-learn/scikit-learn | 2 | 1 | 0 | E2 | M2-M1 | github.com::repository_view |
| 20260918 | vmess | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 1 | E2 | M2-M1 | bing.com::search_results_view |
| 20260918 | vmess | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 2 | E2 | M2-M1 | bing.com::search_results_view |
| 20260918 | vmess | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E2 | M2-M1 | bing.com::search_results_view |
| 20260918 | vmess | https://www.bing.com/search?q=solar+system+facts | 0 | 0 | 1 | E2 | M2-M1 | bing.com::search_results_view |
| 20260918 | vmess | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 0 | E2 | M2-M1 | bing.com::search_results_view |
| 20260918 | vmess | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E2 | M2-M1 | youtube.com::search_results_view |
| 20260918 | vmess | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 0 | E2 | M2-M1 | youtube.com::search_results_view |
| 20260918 | vmess | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E2 | M2-M1 | youtube.com::search_results_view |
| 20260918 | vmess | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 0 | E2 | M2-M1 | youtube.com::search_results_view |
| 20260918 | vmess | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E2 | M2-M1 | youtube.com::search_results_view |
| 20260918 | vmess | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E2 | M2-M1 | youtube.com::video_playback |
| 20260918 | vmess | youtube_video:aircAruvnKk | 5 | 0 | 0 | E2 | M2-M1 | youtube.com::video_playback |
| 20260918 | vmess | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E2 | M2-M1 | youtube.com::video_playback |
| 20260918 | vmess | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E2 | M2-M1 | youtube.com::video_playback |
| 20260918 | vmess | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E2 | M2-M1 | youtube.com::video_playback |
| 20260919 | anytls | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 0 | E2 | M2-M1 | developer.mozilla.org::document_view |
| 20260919 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 2 | 0 | E2 | M2-M1 | developer.mozilla.org::document_view |
| 20260919 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 1 | E2 | M2-M1 | developer.mozilla.org::document_view |
| 20260919 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 0 | 0 | E2 | M2-M1 | developer.mozilla.org::document_view |
| 20260919 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 2 | 0 | E2 | M2-M1 | developer.mozilla.org::document_view |
| 20260919 | anytls | https://en.wikipedia.org/wiki/Computer_network | 3 | 1 | 0 | E2 | M2-M1 | wikipedia.org::article_view |
| 20260919 | anytls | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 2 | 0 | E2 | M2-M1 | wikipedia.org::article_view |
| 20260919 | anytls | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 1 | 0 | E2 | M2-M1 | wikipedia.org::article_view |
| 20260919 | anytls | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 2 | 0 | E2 | M2-M1 | wikipedia.org::article_view |
| 20260919 | anytls | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E2 | M2-M1 | wikipedia.org::article_view |
| 20260919 | anytls | https://github.com/RakuLomis/TrafficTracer | 2 | 0 | 1 | E2 | M2-M1 | github.com::repository_view |
| 20260919 | anytls | https://github.com/numpy/numpy | 2 | 0 | 0 | E2 | M2-M1 | github.com::repository_view |
| 20260919 | anytls | https://github.com/pallets/flask | 2 | 0 | 0 | E2 | M2-M1 | github.com::repository_view |
| 20260919 | anytls | https://github.com/python/cpython | 2 | 0 | 0 | E2 | M2-M1 | github.com::repository_view |
| 20260919 | anytls | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E2 | M2-M1 | github.com::repository_view |
| 20260919 | anytls | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 0 | E2 | M2-M1 | bing.com::search_results_view |
| 20260919 | anytls | https://www.bing.com/search?q=indoor+plant+care | 0 | 1 | 0 | E2 | M2-M1 | bing.com::search_results_view |
| 20260919 | anytls | https://www.bing.com/search?q=network+traffic+analysis | 0 | 1 | 0 | E2 | M2-M1 | bing.com::search_results_view |
| 20260919 | anytls | https://www.bing.com/search?q=solar+system+facts | 0 | 1 | 0 | E2 | M2-M1 | bing.com::search_results_view |
| 20260919 | anytls | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 0 | E2 | M2-M1 | bing.com::search_results_view |
| 20260919 | anytls | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E2 | M2-M1 | youtube.com::search_results_view |
| 20260919 | anytls | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 0 | E2 | M2-M1 | youtube.com::search_results_view |
| 20260919 | anytls | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E2 | M2-M1 | youtube.com::search_results_view |
| 20260919 | anytls | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 0 | E2 | M2-M1 | youtube.com::search_results_view |
| 20260919 | anytls | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E2 | M2-M1 | youtube.com::search_results_view |
| 20260919 | anytls | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E2 | M2-M1 | youtube.com::video_playback |
| 20260919 | anytls | youtube_video:aircAruvnKk | 5 | 0 | 0 | E2 | M2-M1 | youtube.com::video_playback |
| 20260919 | anytls | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E2 | M2-M1 | youtube.com::video_playback |
| 20260919 | anytls | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E2 | M2-M1 | youtube.com::video_playback |
| 20260919 | anytls | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E2 | M2-M1 | youtube.com::video_playback |
| 20260919 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 0 | E2 | M2-M1 | developer.mozilla.org::document_view |
| 20260919 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 0 | 0 | E2 | M2-M1 | developer.mozilla.org::document_view |
| 20260919 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 0 | E2 | M2-M1 | developer.mozilla.org::document_view |
| 20260919 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 0 | 0 | E2 | M2-M1 | developer.mozilla.org::document_view |
| 20260919 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 0 | 0 | E2 | M2-M1 | developer.mozilla.org::document_view |
| 20260919 | shadowsocks | https://en.wikipedia.org/wiki/Computer_network | 3 | 0 | 0 | E2 | M2-M1 | wikipedia.org::article_view |
| 20260919 | shadowsocks | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 0 | E2 | M2-M1 | wikipedia.org::article_view |
| 20260919 | shadowsocks | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 0 | 0 | E2 | M2-M1 | wikipedia.org::article_view |
| 20260919 | shadowsocks | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 0 | E2 | M2-M1 | wikipedia.org::article_view |
| 20260919 | shadowsocks | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E2 | M2-M1 | wikipedia.org::article_view |
| 20260919 | shadowsocks | https://github.com/RakuLomis/TrafficTracer | 2 | 0 | 0 | E2 | M2-M1 | github.com::repository_view |
| 20260919 | shadowsocks | https://github.com/numpy/numpy | 2 | 0 | 0 | E2 | M2-M1 | github.com::repository_view |
| 20260919 | shadowsocks | https://github.com/pallets/flask | 2 | 0 | 0 | E2 | M2-M1 | github.com::repository_view |
| 20260919 | shadowsocks | https://github.com/python/cpython | 2 | 0 | 0 | E2 | M2-M1 | github.com::repository_view |
| 20260919 | shadowsocks | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E2 | M2-M1 | github.com::repository_view |
| 20260919 | shadowsocks | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 0 | E2 | M2-M1 | bing.com::search_results_view |
| 20260919 | shadowsocks | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 0 | E2 | M2-M1 | bing.com::search_results_view |
| 20260919 | shadowsocks | https://www.bing.com/search?q=network+traffic+analysis | 0 | 2 | 0 | E2 | M2-M1 | bing.com::search_results_view |
| 20260919 | shadowsocks | https://www.bing.com/search?q=solar+system+facts | 0 | 1 | 0 | E2 | M2-M1 | bing.com::search_results_view |
| 20260919 | shadowsocks | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 1 | 0 | E2 | M2-M1 | bing.com::search_results_view |
| 20260919 | shadowsocks | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 1 | 0 | E2 | M2-M1 | youtube.com::search_results_view |
| 20260919 | shadowsocks | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 1 | 0 | E2 | M2-M1 | youtube.com::search_results_view |
| 20260919 | shadowsocks | https://www.youtube.com/results?search_query=bread+baking | 4 | 1 | 0 | E2 | M2-M1 | youtube.com::search_results_view |
| 20260919 | shadowsocks | https://www.youtube.com/results?search_query=piano+practice | 4 | 2 | 0 | E2 | M2-M1 | youtube.com::search_results_view |
| 20260919 | shadowsocks | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E2 | M2-M1 | youtube.com::search_results_view |
| 20260919 | shadowsocks | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E2 | M2-M1 | youtube.com::video_playback |
| 20260919 | shadowsocks | youtube_video:aircAruvnKk | 5 | 0 | 0 | E2 | M2-M1 | youtube.com::video_playback |
| 20260919 | shadowsocks | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E2 | M2-M1 | youtube.com::video_playback |
| 20260919 | shadowsocks | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E2 | M2-M1 | youtube.com::video_playback |
| 20260919 | shadowsocks | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E2 | M2-M1 | youtube.com::video_playback |
| 20260919 | trojan | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 0 | E2 | M2-M1 | developer.mozilla.org::document_view |
| 20260919 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 0 | 0 | E2 | M2-M1 | developer.mozilla.org::document_view |
| 20260919 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 2 | 0 | E2 | M2-M1 | developer.mozilla.org::document_view |
| 20260919 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 2 | 0 | E2 | M2-M1 | developer.mozilla.org::document_view |
| 20260919 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 1 | 0 | E2 | M2-M1 | developer.mozilla.org::document_view |
| 20260919 | trojan | https://en.wikipedia.org/wiki/Computer_network | 3 | 0 | 0 | E2 | M2-M1 | wikipedia.org::article_view |
| 20260919 | trojan | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 2 | E2 | M2-M1 | wikipedia.org::article_view |
| 20260919 | trojan | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 0 | 1 | E2 | M2-M1 | wikipedia.org::article_view |
| 20260919 | trojan | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 1 | E2 | M2-M1 | wikipedia.org::article_view |
| 20260919 | trojan | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 2 | 0 | E2 | M2-M1 | wikipedia.org::article_view |
| 20260919 | trojan | https://github.com/RakuLomis/TrafficTracer | 2 | 0 | 1 | E2 | M2-M1 | github.com::repository_view |
| 20260919 | trojan | https://github.com/numpy/numpy | 2 | 0 | 0 | E2 | M2-M1 | github.com::repository_view |
| 20260919 | trojan | https://github.com/pallets/flask | 2 | 0 | 1 | E2 | M2-M1 | github.com::repository_view |
| 20260919 | trojan | https://github.com/python/cpython | 2 | 0 | 0 | E2 | M2-M1 | github.com::repository_view |
| 20260919 | trojan | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E2 | M2-M1 | github.com::repository_view |
| 20260919 | trojan | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 1 | E2 | M2-M1 | bing.com::search_results_view |
| 20260919 | trojan | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 0 | E2 | M2-M1 | bing.com::search_results_view |
| 20260919 | trojan | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 1 | E2 | M2-M1 | bing.com::search_results_view |
| 20260919 | trojan | https://www.bing.com/search?q=solar+system+facts | 0 | 0 | 2 | E2 | M2-M1 | bing.com::search_results_view |
| 20260919 | trojan | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 1 | E2 | M2-M1 | bing.com::search_results_view |
| 20260919 | trojan | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E2 | M2-M1 | youtube.com::search_results_view |
| 20260919 | trojan | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 1 | E2 | M2-M1 | youtube.com::search_results_view |
| 20260919 | trojan | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E2 | M2-M1 | youtube.com::search_results_view |
| 20260919 | trojan | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 0 | E2 | M2-M1 | youtube.com::search_results_view |
| 20260919 | trojan | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 1 | E2 | M2-M1 | youtube.com::search_results_view |
| 20260919 | trojan | youtube_video:R6MlUcmOul8 | 5 | 0 | 2 | E2 | M2-M1 | youtube.com::video_playback |
| 20260919 | trojan | youtube_video:aircAruvnKk | 5 | 0 | 0 | E2 | M2-M1 | youtube.com::video_playback |
| 20260919 | trojan | youtube_video:aqz-KE-bpKQ | 5 | 0 | 2 | E2 | M2-M1 | youtube.com::video_playback |
| 20260919 | trojan | youtube_video:eRsGyueVLvQ | 5 | 0 | 2 | E2 | M2-M1 | youtube.com::video_playback |
| 20260919 | trojan | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E2 | M2-M1 | youtube.com::video_playback |
| 20260919 | vless | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 0 | E2 | M2-M1 | developer.mozilla.org::document_view |
| 20260919 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 0 | 4 | E2 | M2-M1 | developer.mozilla.org::document_view |
| 20260919 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 2 | E2 | M2-M1 | developer.mozilla.org::document_view |
| 20260919 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 0 | 1 | E2 | M2-M1 | developer.mozilla.org::document_view |
| 20260919 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 0 | 0 | E2 | M2-M1 | developer.mozilla.org::document_view |
| 20260919 | vless | https://en.wikipedia.org/wiki/Computer_network | 3 | 1 | 0 | E2 | M2-M1 | wikipedia.org::article_view |
| 20260919 | vless | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 1 | 0 | E2 | M2-M1 | wikipedia.org::article_view |
| 20260919 | vless | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 1 | 0 | E2 | M2-M1 | wikipedia.org::article_view |
| 20260919 | vless | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 0 | E2 | M2-M1 | wikipedia.org::article_view |
| 20260919 | vless | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 2 | 0 | E2 | M2-M1 | wikipedia.org::article_view |
| 20260919 | vless | https://github.com/RakuLomis/TrafficTracer | 2 | 0 | 0 | E2 | M2-M1 | github.com::repository_view |
| 20260919 | vless | https://github.com/numpy/numpy | 2 | 0 | 0 | E2 | M2-M1 | github.com::repository_view |
| 20260919 | vless | https://github.com/pallets/flask | 2 | 1 | 0 | E2 | M2-M1 | github.com::repository_view |
| 20260919 | vless | https://github.com/python/cpython | 2 | 0 | 0 | E2 | M2-M1 | github.com::repository_view |
| 20260919 | vless | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E2 | M2-M1 | github.com::repository_view |
| 20260919 | vless | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 1 | E2 | M2-M1 | bing.com::search_results_view |
| 20260919 | vless | https://www.bing.com/search?q=indoor+plant+care | 0 | 1 | 0 | E2 | M2-M1 | bing.com::search_results_view |
| 20260919 | vless | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E2 | M2-M1 | bing.com::search_results_view |
| 20260919 | vless | https://www.bing.com/search?q=solar+system+facts | 0 | 0 | 1 | E2 | M2-M1 | bing.com::search_results_view |
| 20260919 | vless | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 1 | E2 | M2-M1 | bing.com::search_results_view |
| 20260919 | vless | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E2 | M2-M1 | youtube.com::search_results_view |
| 20260919 | vless | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 2 | E2 | M2-M1 | youtube.com::search_results_view |
| 20260919 | vless | https://www.youtube.com/results?search_query=bread+baking | 4 | 1 | 1 | E2 | M2-M1 | youtube.com::search_results_view |
| 20260919 | vless | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 1 | E2 | M2-M1 | youtube.com::search_results_view |
| 20260919 | vless | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 1 | E2 | M2-M1 | youtube.com::search_results_view |
| 20260919 | vless | youtube_video:R6MlUcmOul8 | 5 | 0 | 1 | E2 | M2-M1 | youtube.com::video_playback |
| 20260919 | vless | youtube_video:aircAruvnKk | 5 | 0 | 0 | E2 | M2-M1 | youtube.com::video_playback |
| 20260919 | vless | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E2 | M2-M1 | youtube.com::video_playback |
| 20260919 | vless | youtube_video:eRsGyueVLvQ | 5 | 0 | 2 | E2 | M2-M1 | youtube.com::video_playback |
| 20260919 | vless | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E2 | M2-M1 | youtube.com::video_playback |
| 20260919 | vmess | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 0 | E2 | M2-M1 | developer.mozilla.org::document_view |
| 20260919 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 0 | 0 | E2 | M2-M1 | developer.mozilla.org::document_view |
| 20260919 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 0 | E2 | M2-M1 | developer.mozilla.org::document_view |
| 20260919 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 0 | 0 | E2 | M2-M1 | developer.mozilla.org::document_view |
| 20260919 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 2 | 0 | E2 | M2-M1 | developer.mozilla.org::document_view |
| 20260919 | vmess | https://en.wikipedia.org/wiki/Computer_network | 3 | 1 | 0 | E2 | M2-M1 | wikipedia.org::article_view |
| 20260919 | vmess | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 0 | E2 | M2-M1 | wikipedia.org::article_view |
| 20260919 | vmess | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 0 | 0 | E2 | M2-M1 | wikipedia.org::article_view |
| 20260919 | vmess | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 1 | E2 | M2-M1 | wikipedia.org::article_view |
| 20260919 | vmess | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E2 | M2-M1 | wikipedia.org::article_view |
| 20260919 | vmess | https://github.com/RakuLomis/TrafficTracer | 2 | 0 | 0 | E2 | M2-M1 | github.com::repository_view |
| 20260919 | vmess | https://github.com/numpy/numpy | 2 | 1 | 0 | E2 | M2-M1 | github.com::repository_view |
| 20260919 | vmess | https://github.com/pallets/flask | 2 | 1 | 0 | E2 | M2-M1 | github.com::repository_view |
| 20260919 | vmess | https://github.com/python/cpython | 2 | 1 | 0 | E2 | M2-M1 | github.com::repository_view |
| 20260919 | vmess | https://github.com/scikit-learn/scikit-learn | 2 | 2 | 0 | E2 | M2-M1 | github.com::repository_view |
| 20260919 | vmess | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 1 | E2 | M2-M1 | bing.com::search_results_view |
| 20260919 | vmess | https://www.bing.com/search?q=indoor+plant+care | 0 | 1 | 1 | E2 | M2-M1 | bing.com::search_results_view |
| 20260919 | vmess | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E2 | M2-M1 | bing.com::search_results_view |
| 20260919 | vmess | https://www.bing.com/search?q=solar+system+facts | 0 | 0 | 1 | E2 | M2-M1 | bing.com::search_results_view |
| 20260919 | vmess | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 0 | E2 | M2-M1 | bing.com::search_results_view |
| 20260919 | vmess | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E2 | M2-M1 | youtube.com::search_results_view |
| 20260919 | vmess | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 0 | E2 | M2-M1 | youtube.com::search_results_view |
| 20260919 | vmess | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E2 | M2-M1 | youtube.com::search_results_view |
| 20260919 | vmess | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 1 | E2 | M2-M1 | youtube.com::search_results_view |
| 20260919 | vmess | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E2 | M2-M1 | youtube.com::search_results_view |
| 20260919 | vmess | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E2 | M2-M1 | youtube.com::video_playback |
| 20260919 | vmess | youtube_video:aircAruvnKk | 5 | 0 | 0 | E2 | M2-M1 | youtube.com::video_playback |
| 20260919 | vmess | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E2 | M2-M1 | youtube.com::video_playback |
| 20260919 | vmess | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E2 | M2-M1 | youtube.com::video_playback |
| 20260919 | vmess | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E2 | M2-M1 | youtube.com::video_playback |
| 20260920 | anytls | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 0 | E2 | M2-M1 | developer.mozilla.org::document_view |
| 20260920 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 2 | 0 | E2 | M2-M1 | developer.mozilla.org::document_view |
| 20260920 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 0 | E2 | M2-M1 | developer.mozilla.org::document_view |
| 20260920 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 0 | 0 | E2 | M2-M1 | developer.mozilla.org::document_view |
| 20260920 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 1 | 0 | E2 | M2-M1 | developer.mozilla.org::document_view |
| 20260920 | anytls | https://en.wikipedia.org/wiki/Computer_network | 3 | 2 | 0 | E2 | M2-M1 | wikipedia.org::article_view |
| 20260920 | anytls | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 2 | 0 | E2 | M2-M1 | wikipedia.org::article_view |
| 20260920 | anytls | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 1 | 0 | E2 | M2-M1 | wikipedia.org::article_view |
| 20260920 | anytls | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 2 | 0 | E2 | M2-M1 | wikipedia.org::article_view |
| 20260920 | anytls | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E2 | M2-M1 | wikipedia.org::article_view |
| 20260920 | anytls | https://github.com/RakuLomis/TrafficTracer | 2 | 0 | 1 | E2 | M2-M1 | github.com::repository_view |
| 20260920 | anytls | https://github.com/numpy/numpy | 2 | 0 | 0 | E2 | M2-M1 | github.com::repository_view |
| 20260920 | anytls | https://github.com/pallets/flask | 2 | 1 | 0 | E2 | M2-M1 | github.com::repository_view |
| 20260920 | anytls | https://github.com/python/cpython | 2 | 0 | 0 | E2 | M2-M1 | github.com::repository_view |
| 20260920 | anytls | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E2 | M2-M1 | github.com::repository_view |
| 20260920 | anytls | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 0 | E2 | M2-M1 | bing.com::search_results_view |
| 20260920 | anytls | https://www.bing.com/search?q=indoor+plant+care | 0 | 1 | 0 | E2 | M2-M1 | bing.com::search_results_view |
| 20260920 | anytls | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E2 | M2-M1 | bing.com::search_results_view |
| 20260920 | anytls | https://www.bing.com/search?q=solar+system+facts | 0 | 1 | 0 | E2 | M2-M1 | bing.com::search_results_view |
| 20260920 | anytls | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 0 | E2 | M2-M1 | bing.com::search_results_view |
| 20260920 | anytls | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 1 | 0 | E2 | M2-M1 | youtube.com::search_results_view |
| 20260920 | anytls | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 0 | E2 | M2-M1 | youtube.com::search_results_view |
| 20260920 | anytls | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E2 | M2-M1 | youtube.com::search_results_view |
| 20260920 | anytls | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 0 | E2 | M2-M1 | youtube.com::search_results_view |
| 20260920 | anytls | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E2 | M2-M1 | youtube.com::search_results_view |
| 20260920 | anytls | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E2 | M2-M1 | youtube.com::video_playback |
| 20260920 | anytls | youtube_video:aircAruvnKk | 5 | 0 | 0 | E2 | M2-M1 | youtube.com::video_playback |
| 20260920 | anytls | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E2 | M2-M1 | youtube.com::video_playback |
| 20260920 | anytls | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E2 | M2-M1 | youtube.com::video_playback |
| 20260920 | anytls | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E2 | M2-M1 | youtube.com::video_playback |
| 20260920 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 0 | E2 | M2-M1 | developer.mozilla.org::document_view |
| 20260920 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 0 | 0 | E2 | M2-M1 | developer.mozilla.org::document_view |
| 20260920 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 0 | E2 | M2-M1 | developer.mozilla.org::document_view |
| 20260920 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 0 | 0 | E2 | M2-M1 | developer.mozilla.org::document_view |
| 20260920 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 0 | 0 | E2 | M2-M1 | developer.mozilla.org::document_view |
| 20260920 | shadowsocks | https://en.wikipedia.org/wiki/Computer_network | 3 | 0 | 0 | E2 | M2-M1 | wikipedia.org::article_view |
| 20260920 | shadowsocks | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 0 | E2 | M2-M1 | wikipedia.org::article_view |
| 20260920 | shadowsocks | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 0 | 0 | E2 | M2-M1 | wikipedia.org::article_view |
| 20260920 | shadowsocks | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 0 | E2 | M2-M1 | wikipedia.org::article_view |
| 20260920 | shadowsocks | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E2 | M2-M1 | wikipedia.org::article_view |
| 20260920 | shadowsocks | https://github.com/RakuLomis/TrafficTracer | 2 | 0 | 0 | E2 | M2-M1 | github.com::repository_view |
| 20260920 | shadowsocks | https://github.com/numpy/numpy | 2 | 0 | 0 | E2 | M2-M1 | github.com::repository_view |
| 20260920 | shadowsocks | https://github.com/pallets/flask | 2 | 0 | 0 | E2 | M2-M1 | github.com::repository_view |
| 20260920 | shadowsocks | https://github.com/python/cpython | 2 | 0 | 0 | E2 | M2-M1 | github.com::repository_view |
| 20260920 | shadowsocks | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E2 | M2-M1 | github.com::repository_view |
| 20260920 | shadowsocks | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 0 | E2 | M2-M1 | bing.com::search_results_view |
| 20260920 | shadowsocks | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 0 | E2 | M2-M1 | bing.com::search_results_view |
| 20260920 | shadowsocks | https://www.bing.com/search?q=network+traffic+analysis | 0 | 2 | 0 | E2 | M2-M1 | bing.com::search_results_view |
| 20260920 | shadowsocks | https://www.bing.com/search?q=solar+system+facts | 0 | 2 | 0 | E2 | M2-M1 | bing.com::search_results_view |
| 20260920 | shadowsocks | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 1 | 0 | E2 | M2-M1 | bing.com::search_results_view |
| 20260920 | shadowsocks | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 1 | 0 | E2 | M2-M1 | youtube.com::search_results_view |
| 20260920 | shadowsocks | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 1 | 0 | E2 | M2-M1 | youtube.com::search_results_view |
| 20260920 | shadowsocks | https://www.youtube.com/results?search_query=bread+baking | 4 | 1 | 0 | E2 | M2-M1 | youtube.com::search_results_view |
| 20260920 | shadowsocks | https://www.youtube.com/results?search_query=piano+practice | 4 | 2 | 0 | E2 | M2-M1 | youtube.com::search_results_view |
| 20260920 | shadowsocks | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E2 | M2-M1 | youtube.com::search_results_view |
| 20260920 | shadowsocks | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E2 | M2-M1 | youtube.com::video_playback |
| 20260920 | shadowsocks | youtube_video:aircAruvnKk | 5 | 0 | 0 | E2 | M2-M1 | youtube.com::video_playback |
| 20260920 | shadowsocks | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E2 | M2-M1 | youtube.com::video_playback |
| 20260920 | shadowsocks | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E2 | M2-M1 | youtube.com::video_playback |
| 20260920 | shadowsocks | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E2 | M2-M1 | youtube.com::video_playback |
| 20260920 | trojan | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 1 | 0 | E2 | M2-M1 | developer.mozilla.org::document_view |
| 20260920 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 0 | 0 | E2 | M2-M1 | developer.mozilla.org::document_view |
| 20260920 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 1 | 0 | E2 | M2-M1 | developer.mozilla.org::document_view |
| 20260920 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 1 | 0 | E2 | M2-M1 | developer.mozilla.org::document_view |
| 20260920 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 1 | 0 | E2 | M2-M1 | developer.mozilla.org::document_view |
| 20260920 | trojan | https://en.wikipedia.org/wiki/Computer_network | 3 | 0 | 0 | E2 | M2-M1 | wikipedia.org::article_view |
| 20260920 | trojan | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 2 | E2 | M2-M1 | wikipedia.org::article_view |
| 20260920 | trojan | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 0 | 3 | E2 | M2-M1 | wikipedia.org::article_view |
| 20260920 | trojan | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 1 | E2 | M2-M1 | wikipedia.org::article_view |
| 20260920 | trojan | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 2 | 0 | E2 | M2-M1 | wikipedia.org::article_view |
| 20260920 | trojan | https://github.com/RakuLomis/TrafficTracer | 2 | 0 | 0 | E2 | M2-M1 | github.com::repository_view |
| 20260920 | trojan | https://github.com/numpy/numpy | 2 | 0 | 0 | E2 | M2-M1 | github.com::repository_view |
| 20260920 | trojan | https://github.com/pallets/flask | 2 | 0 | 0 | E2 | M2-M1 | github.com::repository_view |
| 20260920 | trojan | https://github.com/python/cpython | 2 | 0 | 0 | E2 | M2-M1 | github.com::repository_view |
| 20260920 | trojan | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E2 | M2-M1 | github.com::repository_view |
| 20260920 | trojan | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 1 | 1 | E2 | M2-M1 | bing.com::search_results_view |
| 20260920 | trojan | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 0 | E2 | M2-M1 | bing.com::search_results_view |
| 20260920 | trojan | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E2 | M2-M1 | bing.com::search_results_view |
| 20260920 | trojan | https://www.bing.com/search?q=solar+system+facts | 0 | 1 | 1 | E2 | M2-M1 | bing.com::search_results_view |
| 20260920 | trojan | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 1 | E2 | M2-M1 | bing.com::search_results_view |
| 20260920 | trojan | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E2 | M2-M1 | youtube.com::search_results_view |
| 20260920 | trojan | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 1 | 1 | E2 | M2-M1 | youtube.com::search_results_view |
| 20260920 | trojan | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E2 | M2-M1 | youtube.com::search_results_view |
| 20260920 | trojan | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 0 | E2 | M2-M1 | youtube.com::search_results_view |
| 20260920 | trojan | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 1 | E2 | M2-M1 | youtube.com::search_results_view |
| 20260920 | trojan | youtube_video:R6MlUcmOul8 | 5 | 0 | 2 | E2 | M2-M1 | youtube.com::video_playback |
| 20260920 | trojan | youtube_video:aircAruvnKk | 5 | 0 | 0 | E2 | M2-M1 | youtube.com::video_playback |
| 20260920 | trojan | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E2 | M2-M1 | youtube.com::video_playback |
| 20260920 | trojan | youtube_video:eRsGyueVLvQ | 5 | 0 | 2 | E2 | M2-M1 | youtube.com::video_playback |
| 20260920 | trojan | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E2 | M2-M1 | youtube.com::video_playback |
| 20260920 | vless | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 1 | 0 | E2 | M2-M1 | developer.mozilla.org::document_view |
| 20260920 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 0 | 3 | E2 | M2-M1 | developer.mozilla.org::document_view |
| 20260920 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 2 | E2 | M2-M1 | developer.mozilla.org::document_view |
| 20260920 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 0 | 1 | E2 | M2-M1 | developer.mozilla.org::document_view |
| 20260920 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 0 | 1 | E2 | M2-M1 | developer.mozilla.org::document_view |
| 20260920 | vless | https://en.wikipedia.org/wiki/Computer_network | 3 | 2 | 0 | E2 | M2-M1 | wikipedia.org::article_view |
| 20260920 | vless | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 3 | 0 | E2 | M2-M1 | wikipedia.org::article_view |
| 20260920 | vless | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 1 | 0 | E2 | M2-M1 | wikipedia.org::article_view |
| 20260920 | vless | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 0 | E2 | M2-M1 | wikipedia.org::article_view |
| 20260920 | vless | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 2 | 0 | E2 | M2-M1 | wikipedia.org::article_view |
| 20260920 | vless | https://github.com/RakuLomis/TrafficTracer | 2 | 0 | 0 | E2 | M2-M1 | github.com::repository_view |
| 20260920 | vless | https://github.com/numpy/numpy | 2 | 0 | 0 | E2 | M2-M1 | github.com::repository_view |
| 20260920 | vless | https://github.com/pallets/flask | 2 | 0 | 0 | E2 | M2-M1 | github.com::repository_view |
| 20260920 | vless | https://github.com/python/cpython | 2 | 0 | 0 | E2 | M2-M1 | github.com::repository_view |
| 20260920 | vless | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E2 | M2-M1 | github.com::repository_view |
| 20260920 | vless | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 1 | E2 | M2-M1 | bing.com::search_results_view |
| 20260920 | vless | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 1 | E2 | M2-M1 | bing.com::search_results_view |
| 20260920 | vless | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E2 | M2-M1 | bing.com::search_results_view |
| 20260920 | vless | https://www.bing.com/search?q=solar+system+facts | 0 | 1 | 0 | E2 | M2-M1 | bing.com::search_results_view |
| 20260920 | vless | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 1 | E2 | M2-M1 | bing.com::search_results_view |
| 20260920 | vless | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E2 | M2-M1 | youtube.com::search_results_view |
| 20260920 | vless | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 2 | E2 | M2-M1 | youtube.com::search_results_view |
| 20260920 | vless | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E2 | M2-M1 | youtube.com::search_results_view |
| 20260920 | vless | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 0 | E2 | M2-M1 | youtube.com::search_results_view |
| 20260920 | vless | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 1 | E2 | M2-M1 | youtube.com::search_results_view |
| 20260920 | vless | youtube_video:R6MlUcmOul8 | 5 | 0 | 1 | E2 | M2-M1 | youtube.com::video_playback |
| 20260920 | vless | youtube_video:aircAruvnKk | 5 | 0 | 0 | E2 | M2-M1 | youtube.com::video_playback |
| 20260920 | vless | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E2 | M2-M1 | youtube.com::video_playback |
| 20260920 | vless | youtube_video:eRsGyueVLvQ | 5 | 0 | 2 | E2 | M2-M1 | youtube.com::video_playback |
| 20260920 | vless | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E2 | M2-M1 | youtube.com::video_playback |
| 20260920 | vmess | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 0 | E2 | M2-M1 | developer.mozilla.org::document_view |
| 20260920 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 0 | 0 | E2 | M2-M1 | developer.mozilla.org::document_view |
| 20260920 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 0 | E2 | M2-M1 | developer.mozilla.org::document_view |
| 20260920 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 0 | 0 | E2 | M2-M1 | developer.mozilla.org::document_view |
| 20260920 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 2 | 0 | E2 | M2-M1 | developer.mozilla.org::document_view |
| 20260920 | vmess | https://en.wikipedia.org/wiki/Computer_network | 3 | 1 | 0 | E2 | M2-M1 | wikipedia.org::article_view |
| 20260920 | vmess | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 0 | E2 | M2-M1 | wikipedia.org::article_view |
| 20260920 | vmess | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 1 | 0 | E2 | M2-M1 | wikipedia.org::article_view |
| 20260920 | vmess | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 1 | E2 | M2-M1 | wikipedia.org::article_view |
| 20260920 | vmess | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E2 | M2-M1 | wikipedia.org::article_view |
| 20260920 | vmess | https://github.com/RakuLomis/TrafficTracer | 2 | 0 | 0 | E2 | M2-M1 | github.com::repository_view |
| 20260920 | vmess | https://github.com/numpy/numpy | 2 | 0 | 0 | E2 | M2-M1 | github.com::repository_view |
| 20260920 | vmess | https://github.com/pallets/flask | 2 | 0 | 0 | E2 | M2-M1 | github.com::repository_view |
| 20260920 | vmess | https://github.com/python/cpython | 2 | 1 | 0 | E2 | M2-M1 | github.com::repository_view |
| 20260920 | vmess | https://github.com/scikit-learn/scikit-learn | 2 | 2 | 0 | E2 | M2-M1 | github.com::repository_view |
| 20260920 | vmess | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 0 | E2 | M2-M1 | bing.com::search_results_view |
| 20260920 | vmess | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 2 | E2 | M2-M1 | bing.com::search_results_view |
| 20260920 | vmess | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E2 | M2-M1 | bing.com::search_results_view |
| 20260920 | vmess | https://www.bing.com/search?q=solar+system+facts | 0 | 0 | 1 | E2 | M2-M1 | bing.com::search_results_view |
| 20260920 | vmess | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 0 | E2 | M2-M1 | bing.com::search_results_view |
| 20260920 | vmess | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E2 | M2-M1 | youtube.com::search_results_view |
| 20260920 | vmess | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 0 | E2 | M2-M1 | youtube.com::search_results_view |
| 20260920 | vmess | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E2 | M2-M1 | youtube.com::search_results_view |
| 20260920 | vmess | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 0 | E2 | M2-M1 | youtube.com::search_results_view |
| 20260920 | vmess | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E2 | M2-M1 | youtube.com::search_results_view |
| 20260920 | vmess | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E2 | M2-M1 | youtube.com::video_playback |
| 20260920 | vmess | youtube_video:aircAruvnKk | 5 | 0 | 0 | E2 | M2-M1 | youtube.com::video_playback |
| 20260920 | vmess | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E2 | M2-M1 | youtube.com::video_playback |
| 20260920 | vmess | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E2 | M2-M1 | youtube.com::video_playback |
| 20260920 | vmess | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E2 | M2-M1 | youtube.com::video_playback |
| 20260918 | anytls | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 1 | 0 | E2 | M2-M3 | developer.mozilla.org::document_view |
| 20260918 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 1 | 0 | E2 | M2-M3 | developer.mozilla.org::document_view |
| 20260918 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 1 | 0 | E2 | M2-M3 | developer.mozilla.org::document_view |
| 20260918 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 1 | 0 | E2 | M2-M3 | developer.mozilla.org::document_view |
| 20260918 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 1 | 0 | E2 | M2-M3 | developer.mozilla.org::document_view |
| 20260918 | anytls | https://en.wikipedia.org/wiki/Computer_network | 3 | 0 | 0 | E2 | M2-M3 | wikipedia.org::article_view |
| 20260918 | anytls | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 0 | E2 | M2-M3 | wikipedia.org::article_view |
| 20260918 | anytls | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 1 | 0 | E2 | M2-M3 | wikipedia.org::article_view |
| 20260918 | anytls | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 0 | E2 | M2-M3 | wikipedia.org::article_view |
| 20260918 | anytls | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E2 | M2-M3 | wikipedia.org::article_view |
| 20260918 | anytls | https://github.com/RakuLomis/TrafficTracer | 2 | 0 | 0 | E2 | M2-M3 | github.com::repository_view |
| 20260918 | anytls | https://github.com/numpy/numpy | 2 | 0 | 0 | E2 | M2-M3 | github.com::repository_view |
| 20260918 | anytls | https://github.com/pallets/flask | 2 | 0 | 0 | E2 | M2-M3 | github.com::repository_view |
| 20260918 | anytls | https://github.com/python/cpython | 2 | 1 | 0 | E2 | M2-M3 | github.com::repository_view |
| 20260918 | anytls | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E2 | M2-M3 | github.com::repository_view |
| 20260918 | anytls | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 0 | E2 | M2-M3 | bing.com::search_results_view |
| 20260918 | anytls | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 3 | E2 | M2-M3 | bing.com::search_results_view |
| 20260918 | anytls | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E2 | M2-M3 | bing.com::search_results_view |
| 20260918 | anytls | https://www.bing.com/search?q=solar+system+facts | 0 | 1 | 0 | E2 | M2-M3 | bing.com::search_results_view |
| 20260918 | anytls | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 0 | E2 | M2-M3 | bing.com::search_results_view |
| 20260918 | anytls | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 1 | 0 | E2 | M2-M3 | youtube.com::search_results_view |
| 20260918 | anytls | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 1 | 1 | E2 | M2-M3 | youtube.com::search_results_view |
| 20260918 | anytls | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E2 | M2-M3 | youtube.com::search_results_view |
| 20260918 | anytls | https://www.youtube.com/results?search_query=piano+practice | 4 | 1 | 0 | E2 | M2-M3 | youtube.com::search_results_view |
| 20260918 | anytls | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 1 | E2 | M2-M3 | youtube.com::search_results_view |
| 20260918 | anytls | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E2 | M2-M3 | youtube.com::video_playback |
| 20260918 | anytls | youtube_video:aircAruvnKk | 5 | 0 | 0 | E2 | M2-M3 | youtube.com::video_playback |
| 20260918 | anytls | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E2 | M2-M3 | youtube.com::video_playback |
| 20260918 | anytls | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E2 | M2-M3 | youtube.com::video_playback |
| 20260918 | anytls | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E2 | M2-M3 | youtube.com::video_playback |
| 20260918 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 1 | 0 | E2 | M2-M3 | developer.mozilla.org::document_view |
| 20260918 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 0 | 3 | E2 | M2-M3 | developer.mozilla.org::document_view |
| 20260918 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 0 | E2 | M2-M3 | developer.mozilla.org::document_view |
| 20260918 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 0 | 0 | E2 | M2-M3 | developer.mozilla.org::document_view |
| 20260918 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 0 | 0 | E2 | M2-M3 | developer.mozilla.org::document_view |
| 20260918 | shadowsocks | https://en.wikipedia.org/wiki/Computer_network | 3 | 0 | 0 | E2 | M2-M3 | wikipedia.org::article_view |
| 20260918 | shadowsocks | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 0 | E2 | M2-M3 | wikipedia.org::article_view |
| 20260918 | shadowsocks | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 0 | 1 | E2 | M2-M3 | wikipedia.org::article_view |
| 20260918 | shadowsocks | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 0 | E2 | M2-M3 | wikipedia.org::article_view |
| 20260918 | shadowsocks | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E2 | M2-M3 | wikipedia.org::article_view |
| 20260918 | shadowsocks | https://github.com/RakuLomis/TrafficTracer | 2 | 0 | 0 | E2 | M2-M3 | github.com::repository_view |
| 20260918 | shadowsocks | https://github.com/numpy/numpy | 2 | 0 | 0 | E2 | M2-M3 | github.com::repository_view |
| 20260918 | shadowsocks | https://github.com/pallets/flask | 2 | 0 | 0 | E2 | M2-M3 | github.com::repository_view |
| 20260918 | shadowsocks | https://github.com/python/cpython | 2 | 0 | 0 | E2 | M2-M3 | github.com::repository_view |
| 20260918 | shadowsocks | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E2 | M2-M3 | github.com::repository_view |
| 20260918 | shadowsocks | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 3 | E2 | M2-M3 | bing.com::search_results_view |
| 20260918 | shadowsocks | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 1 | E2 | M2-M3 | bing.com::search_results_view |
| 20260918 | shadowsocks | https://www.bing.com/search?q=network+traffic+analysis | 0 | 1 | 0 | E2 | M2-M3 | bing.com::search_results_view |
| 20260918 | shadowsocks | https://www.bing.com/search?q=solar+system+facts | 0 | 0 | 0 | E2 | M2-M3 | bing.com::search_results_view |
| 20260918 | shadowsocks | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 1 | E2 | M2-M3 | bing.com::search_results_view |
| 20260918 | shadowsocks | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E2 | M2-M3 | youtube.com::search_results_view |
| 20260918 | shadowsocks | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 1 | E2 | M2-M3 | youtube.com::search_results_view |
| 20260918 | shadowsocks | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 1 | E2 | M2-M3 | youtube.com::search_results_view |
| 20260918 | shadowsocks | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 1 | E2 | M2-M3 | youtube.com::search_results_view |
| 20260918 | shadowsocks | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E2 | M2-M3 | youtube.com::search_results_view |
| 20260918 | shadowsocks | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E2 | M2-M3 | youtube.com::video_playback |
| 20260918 | shadowsocks | youtube_video:aircAruvnKk | 5 | 0 | 0 | E2 | M2-M3 | youtube.com::video_playback |
| 20260918 | shadowsocks | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E2 | M2-M3 | youtube.com::video_playback |
| 20260918 | shadowsocks | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E2 | M2-M3 | youtube.com::video_playback |
| 20260918 | shadowsocks | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E2 | M2-M3 | youtube.com::video_playback |
| 20260918 | trojan | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 0 | E2 | M2-M3 | developer.mozilla.org::document_view |
| 20260918 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 3 | 0 | E2 | M2-M3 | developer.mozilla.org::document_view |
| 20260918 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 1 | 1 | E2 | M2-M3 | developer.mozilla.org::document_view |
| 20260918 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 1 | 1 | E2 | M2-M3 | developer.mozilla.org::document_view |
| 20260918 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 0 | 0 | E2 | M2-M3 | developer.mozilla.org::document_view |
| 20260918 | trojan | https://en.wikipedia.org/wiki/Computer_network | 3 | 2 | 0 | E2 | M2-M3 | wikipedia.org::article_view |
| 20260918 | trojan | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 1 | 0 | E2 | M2-M3 | wikipedia.org::article_view |
| 20260918 | trojan | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 0 | 0 | E2 | M2-M3 | wikipedia.org::article_view |
| 20260918 | trojan | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 0 | E2 | M2-M3 | wikipedia.org::article_view |
| 20260918 | trojan | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E2 | M2-M3 | wikipedia.org::article_view |
| 20260918 | trojan | https://github.com/RakuLomis/TrafficTracer | 2 | 2 | 0 | E2 | M2-M3 | github.com::repository_view |
| 20260918 | trojan | https://github.com/numpy/numpy | 2 | 0 | 0 | E2 | M2-M3 | github.com::repository_view |
| 20260918 | trojan | https://github.com/pallets/flask | 2 | 1 | 0 | E2 | M2-M3 | github.com::repository_view |
| 20260918 | trojan | https://github.com/python/cpython | 2 | 1 | 0 | E2 | M2-M3 | github.com::repository_view |
| 20260918 | trojan | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 1 | E2 | M2-M3 | github.com::repository_view |
| 20260918 | trojan | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 0 | E2 | M2-M3 | bing.com::search_results_view |
| 20260918 | trojan | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 0 | E2 | M2-M3 | bing.com::search_results_view |
| 20260918 | trojan | https://www.bing.com/search?q=network+traffic+analysis | 0 | 1 | 0 | E2 | M2-M3 | bing.com::search_results_view |
| 20260918 | trojan | https://www.bing.com/search?q=solar+system+facts | 0 | 0 | 1 | E2 | M2-M3 | bing.com::search_results_view |
| 20260918 | trojan | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 2 | 0 | E2 | M2-M3 | bing.com::search_results_view |
| 20260918 | trojan | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E2 | M2-M3 | youtube.com::search_results_view |
| 20260918 | trojan | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 0 | E2 | M2-M3 | youtube.com::search_results_view |
| 20260918 | trojan | https://www.youtube.com/results?search_query=bread+baking | 4 | 1 | 0 | E2 | M2-M3 | youtube.com::search_results_view |
| 20260918 | trojan | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 0 | E2 | M2-M3 | youtube.com::search_results_view |
| 20260918 | trojan | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 1 | 0 | E2 | M2-M3 | youtube.com::search_results_view |
| 20260918 | trojan | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E2 | M2-M3 | youtube.com::video_playback |
| 20260918 | trojan | youtube_video:aircAruvnKk | 5 | 0 | 0 | E2 | M2-M3 | youtube.com::video_playback |
| 20260918 | trojan | youtube_video:aqz-KE-bpKQ | 5 | 2 | 0 | E2 | M2-M3 | youtube.com::video_playback |
| 20260918 | trojan | youtube_video:eRsGyueVLvQ | 5 | 0 | 2 | E2 | M2-M3 | youtube.com::video_playback |
| 20260918 | trojan | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E2 | M2-M3 | youtube.com::video_playback |
| 20260918 | vless | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 2 | 0 | E2 | M2-M3 | developer.mozilla.org::document_view |
| 20260918 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 0 | 0 | E2 | M2-M3 | developer.mozilla.org::document_view |
| 20260918 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 0 | E2 | M2-M3 | developer.mozilla.org::document_view |
| 20260918 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 0 | 0 | E2 | M2-M3 | developer.mozilla.org::document_view |
| 20260918 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 2 | 0 | E2 | M2-M3 | developer.mozilla.org::document_view |
| 20260918 | vless | https://en.wikipedia.org/wiki/Computer_network | 3 | 0 | 0 | E2 | M2-M3 | wikipedia.org::article_view |
| 20260918 | vless | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 0 | E2 | M2-M3 | wikipedia.org::article_view |
| 20260918 | vless | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 1 | 0 | E2 | M2-M3 | wikipedia.org::article_view |
| 20260918 | vless | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 2 | E2 | M2-M3 | wikipedia.org::article_view |
| 20260918 | vless | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E2 | M2-M3 | wikipedia.org::article_view |
| 20260918 | vless | https://github.com/RakuLomis/TrafficTracer | 2 | 2 | 1 | E2 | M2-M3 | github.com::repository_view |
| 20260918 | vless | https://github.com/numpy/numpy | 2 | 0 | 0 | E2 | M2-M3 | github.com::repository_view |
| 20260918 | vless | https://github.com/pallets/flask | 2 | 0 | 0 | E2 | M2-M3 | github.com::repository_view |
| 20260918 | vless | https://github.com/python/cpython | 2 | 1 | 0 | E2 | M2-M3 | github.com::repository_view |
| 20260918 | vless | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E2 | M2-M3 | github.com::repository_view |
| 20260918 | vless | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 2 | 0 | E2 | M2-M3 | bing.com::search_results_view |
| 20260918 | vless | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 0 | E2 | M2-M3 | bing.com::search_results_view |
| 20260918 | vless | https://www.bing.com/search?q=network+traffic+analysis | 0 | 1 | 0 | E2 | M2-M3 | bing.com::search_results_view |
| 20260918 | vless | https://www.bing.com/search?q=solar+system+facts | 0 | 3 | 0 | E2 | M2-M3 | bing.com::search_results_view |
| 20260918 | vless | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 1 | 0 | E2 | M2-M3 | bing.com::search_results_view |
| 20260918 | vless | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E2 | M2-M3 | youtube.com::search_results_view |
| 20260918 | vless | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 1 | E2 | M2-M3 | youtube.com::search_results_view |
| 20260918 | vless | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 1 | E2 | M2-M3 | youtube.com::search_results_view |
| 20260918 | vless | https://www.youtube.com/results?search_query=piano+practice | 4 | 1 | 0 | E2 | M2-M3 | youtube.com::search_results_view |
| 20260918 | vless | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 1 | E2 | M2-M3 | youtube.com::search_results_view |
| 20260918 | vless | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E2 | M2-M3 | youtube.com::video_playback |
| 20260918 | vless | youtube_video:aircAruvnKk | 5 | 0 | 0 | E2 | M2-M3 | youtube.com::video_playback |
| 20260918 | vless | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E2 | M2-M3 | youtube.com::video_playback |
| 20260918 | vless | youtube_video:eRsGyueVLvQ | 5 | 0 | 1 | E2 | M2-M3 | youtube.com::video_playback |
| 20260918 | vless | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E2 | M2-M3 | youtube.com::video_playback |
| 20260918 | vmess | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 0 | E2 | M2-M3 | developer.mozilla.org::document_view |
| 20260918 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 0 | 0 | E2 | M2-M3 | developer.mozilla.org::document_view |
| 20260918 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 0 | E2 | M2-M3 | developer.mozilla.org::document_view |
| 20260918 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 0 | 0 | E2 | M2-M3 | developer.mozilla.org::document_view |
| 20260918 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 0 | 0 | E2 | M2-M3 | developer.mozilla.org::document_view |
| 20260918 | vmess | https://en.wikipedia.org/wiki/Computer_network | 3 | 1 | 0 | E2 | M2-M3 | wikipedia.org::article_view |
| 20260918 | vmess | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 0 | E2 | M2-M3 | wikipedia.org::article_view |
| 20260918 | vmess | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 0 | 0 | E2 | M2-M3 | wikipedia.org::article_view |
| 20260918 | vmess | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 0 | E2 | M2-M3 | wikipedia.org::article_view |
| 20260918 | vmess | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E2 | M2-M3 | wikipedia.org::article_view |
| 20260918 | vmess | https://github.com/RakuLomis/TrafficTracer | 2 | 1 | 0 | E2 | M2-M3 | github.com::repository_view |
| 20260918 | vmess | https://github.com/numpy/numpy | 2 | 2 | 0 | E2 | M2-M3 | github.com::repository_view |
| 20260918 | vmess | https://github.com/pallets/flask | 2 | 0 | 1 | E2 | M2-M3 | github.com::repository_view |
| 20260918 | vmess | https://github.com/python/cpython | 2 | 0 | 0 | E2 | M2-M3 | github.com::repository_view |
| 20260918 | vmess | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E2 | M2-M3 | github.com::repository_view |
| 20260918 | vmess | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 0 | E2 | M2-M3 | bing.com::search_results_view |
| 20260918 | vmess | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 0 | E2 | M2-M3 | bing.com::search_results_view |
| 20260918 | vmess | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E2 | M2-M3 | bing.com::search_results_view |
| 20260918 | vmess | https://www.bing.com/search?q=solar+system+facts | 0 | 0 | 0 | E2 | M2-M3 | bing.com::search_results_view |
| 20260918 | vmess | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 2 | 0 | E2 | M2-M3 | bing.com::search_results_view |
| 20260918 | vmess | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E2 | M2-M3 | youtube.com::search_results_view |
| 20260918 | vmess | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 1 | 0 | E2 | M2-M3 | youtube.com::search_results_view |
| 20260918 | vmess | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E2 | M2-M3 | youtube.com::search_results_view |
| 20260918 | vmess | https://www.youtube.com/results?search_query=piano+practice | 4 | 1 | 0 | E2 | M2-M3 | youtube.com::search_results_view |
| 20260918 | vmess | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E2 | M2-M3 | youtube.com::search_results_view |
| 20260918 | vmess | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E2 | M2-M3 | youtube.com::video_playback |
| 20260918 | vmess | youtube_video:aircAruvnKk | 5 | 0 | 0 | E2 | M2-M3 | youtube.com::video_playback |
| 20260918 | vmess | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E2 | M2-M3 | youtube.com::video_playback |
| 20260918 | vmess | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E2 | M2-M3 | youtube.com::video_playback |
| 20260918 | vmess | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E2 | M2-M3 | youtube.com::video_playback |
| 20260919 | anytls | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 1 | 0 | E2 | M2-M3 | developer.mozilla.org::document_view |
| 20260919 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 2 | 0 | E2 | M2-M3 | developer.mozilla.org::document_view |
| 20260919 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 2 | 0 | E2 | M2-M3 | developer.mozilla.org::document_view |
| 20260919 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 4 | 0 | E2 | M2-M3 | developer.mozilla.org::document_view |
| 20260919 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 2 | 0 | E2 | M2-M3 | developer.mozilla.org::document_view |
| 20260919 | anytls | https://en.wikipedia.org/wiki/Computer_network | 3 | 0 | 1 | E2 | M2-M3 | wikipedia.org::article_view |
| 20260919 | anytls | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 2 | E2 | M2-M3 | wikipedia.org::article_view |
| 20260919 | anytls | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 0 | 0 | E2 | M2-M3 | wikipedia.org::article_view |
| 20260919 | anytls | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 1 | E2 | M2-M3 | wikipedia.org::article_view |
| 20260919 | anytls | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 1 | E2 | M2-M3 | wikipedia.org::article_view |
| 20260919 | anytls | https://github.com/RakuLomis/TrafficTracer | 2 | 0 | 0 | E2 | M2-M3 | github.com::repository_view |
| 20260919 | anytls | https://github.com/numpy/numpy | 2 | 0 | 0 | E2 | M2-M3 | github.com::repository_view |
| 20260919 | anytls | https://github.com/pallets/flask | 2 | 0 | 0 | E2 | M2-M3 | github.com::repository_view |
| 20260919 | anytls | https://github.com/python/cpython | 2 | 1 | 0 | E2 | M2-M3 | github.com::repository_view |
| 20260919 | anytls | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E2 | M2-M3 | github.com::repository_view |
| 20260919 | anytls | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 0 | E2 | M2-M3 | bing.com::search_results_view |
| 20260919 | anytls | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 2 | E2 | M2-M3 | bing.com::search_results_view |
| 20260919 | anytls | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E2 | M2-M3 | bing.com::search_results_view |
| 20260919 | anytls | https://www.bing.com/search?q=solar+system+facts | 0 | 0 | 0 | E2 | M2-M3 | bing.com::search_results_view |
| 20260919 | anytls | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 0 | E2 | M2-M3 | bing.com::search_results_view |
| 20260919 | anytls | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 1 | 0 | E2 | M2-M3 | youtube.com::search_results_view |
| 20260919 | anytls | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 1 | E2 | M2-M3 | youtube.com::search_results_view |
| 20260919 | anytls | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E2 | M2-M3 | youtube.com::search_results_view |
| 20260919 | anytls | https://www.youtube.com/results?search_query=piano+practice | 4 | 1 | 0 | E2 | M2-M3 | youtube.com::search_results_view |
| 20260919 | anytls | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 1 | E2 | M2-M3 | youtube.com::search_results_view |
| 20260919 | anytls | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E2 | M2-M3 | youtube.com::video_playback |
| 20260919 | anytls | youtube_video:aircAruvnKk | 5 | 0 | 0 | E2 | M2-M3 | youtube.com::video_playback |
| 20260919 | anytls | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E2 | M2-M3 | youtube.com::video_playback |
| 20260919 | anytls | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E2 | M2-M3 | youtube.com::video_playback |
| 20260919 | anytls | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E2 | M2-M3 | youtube.com::video_playback |
| 20260919 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 1 | E2 | M2-M3 | developer.mozilla.org::document_view |
| 20260919 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 0 | 3 | E2 | M2-M3 | developer.mozilla.org::document_view |
| 20260919 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 0 | E2 | M2-M3 | developer.mozilla.org::document_view |
| 20260919 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 0 | 1 | E2 | M2-M3 | developer.mozilla.org::document_view |
| 20260919 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 0 | 0 | E2 | M2-M3 | developer.mozilla.org::document_view |
| 20260919 | shadowsocks | https://en.wikipedia.org/wiki/Computer_network | 3 | 0 | 0 | E2 | M2-M3 | wikipedia.org::article_view |
| 20260919 | shadowsocks | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 0 | E2 | M2-M3 | wikipedia.org::article_view |
| 20260919 | shadowsocks | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 0 | 0 | E2 | M2-M3 | wikipedia.org::article_view |
| 20260919 | shadowsocks | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 0 | E2 | M2-M3 | wikipedia.org::article_view |
| 20260919 | shadowsocks | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E2 | M2-M3 | wikipedia.org::article_view |
| 20260919 | shadowsocks | https://github.com/RakuLomis/TrafficTracer | 2 | 0 | 0 | E2 | M2-M3 | github.com::repository_view |
| 20260919 | shadowsocks | https://github.com/numpy/numpy | 2 | 0 | 0 | E2 | M2-M3 | github.com::repository_view |
| 20260919 | shadowsocks | https://github.com/pallets/flask | 2 | 0 | 0 | E2 | M2-M3 | github.com::repository_view |
| 20260919 | shadowsocks | https://github.com/python/cpython | 2 | 0 | 0 | E2 | M2-M3 | github.com::repository_view |
| 20260919 | shadowsocks | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E2 | M2-M3 | github.com::repository_view |
| 20260919 | shadowsocks | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 1 | E2 | M2-M3 | bing.com::search_results_view |
| 20260919 | shadowsocks | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 1 | E2 | M2-M3 | bing.com::search_results_view |
| 20260919 | shadowsocks | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 1 | E2 | M2-M3 | bing.com::search_results_view |
| 20260919 | shadowsocks | https://www.bing.com/search?q=solar+system+facts | 0 | 0 | 1 | E2 | M2-M3 | bing.com::search_results_view |
| 20260919 | shadowsocks | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 1 | E2 | M2-M3 | bing.com::search_results_view |
| 20260919 | shadowsocks | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E2 | M2-M3 | youtube.com::search_results_view |
| 20260919 | shadowsocks | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 0 | E2 | M2-M3 | youtube.com::search_results_view |
| 20260919 | shadowsocks | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E2 | M2-M3 | youtube.com::search_results_view |
| 20260919 | shadowsocks | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 1 | E2 | M2-M3 | youtube.com::search_results_view |
| 20260919 | shadowsocks | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E2 | M2-M3 | youtube.com::search_results_view |
| 20260919 | shadowsocks | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E2 | M2-M3 | youtube.com::video_playback |
| 20260919 | shadowsocks | youtube_video:aircAruvnKk | 5 | 0 | 0 | E2 | M2-M3 | youtube.com::video_playback |
| 20260919 | shadowsocks | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E2 | M2-M3 | youtube.com::video_playback |
| 20260919 | shadowsocks | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E2 | M2-M3 | youtube.com::video_playback |
| 20260919 | shadowsocks | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E2 | M2-M3 | youtube.com::video_playback |
| 20260919 | trojan | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 1 | E2 | M2-M3 | developer.mozilla.org::document_view |
| 20260919 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 3 | 0 | E2 | M2-M3 | developer.mozilla.org::document_view |
| 20260919 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 1 | 0 | E2 | M2-M3 | developer.mozilla.org::document_view |
| 20260919 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 3 | 0 | E2 | M2-M3 | developer.mozilla.org::document_view |
| 20260919 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 0 | 0 | E2 | M2-M3 | developer.mozilla.org::document_view |
| 20260919 | trojan | https://en.wikipedia.org/wiki/Computer_network | 3 | 0 | 0 | E2 | M2-M3 | wikipedia.org::article_view |
| 20260919 | trojan | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 3 | E2 | M2-M3 | wikipedia.org::article_view |
| 20260919 | trojan | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 2 | 0 | E2 | M2-M3 | wikipedia.org::article_view |
| 20260919 | trojan | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 0 | E2 | M2-M3 | wikipedia.org::article_view |
| 20260919 | trojan | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E2 | M2-M3 | wikipedia.org::article_view |
| 20260919 | trojan | https://github.com/RakuLomis/TrafficTracer | 2 | 2 | 0 | E2 | M2-M3 | github.com::repository_view |
| 20260919 | trojan | https://github.com/numpy/numpy | 2 | 0 | 0 | E2 | M2-M3 | github.com::repository_view |
| 20260919 | trojan | https://github.com/pallets/flask | 2 | 1 | 1 | E2 | M2-M3 | github.com::repository_view |
| 20260919 | trojan | https://github.com/python/cpython | 2 | 3 | 0 | E2 | M2-M3 | github.com::repository_view |
| 20260919 | trojan | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 1 | E2 | M2-M3 | github.com::repository_view |
| 20260919 | trojan | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 0 | E2 | M2-M3 | bing.com::search_results_view |
| 20260919 | trojan | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 0 | E2 | M2-M3 | bing.com::search_results_view |
| 20260919 | trojan | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E2 | M2-M3 | bing.com::search_results_view |
| 20260919 | trojan | https://www.bing.com/search?q=solar+system+facts | 0 | 1 | 0 | E2 | M2-M3 | bing.com::search_results_view |
| 20260919 | trojan | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 2 | 0 | E2 | M2-M3 | bing.com::search_results_view |
| 20260919 | trojan | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E2 | M2-M3 | youtube.com::search_results_view |
| 20260919 | trojan | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 1 | 0 | E2 | M2-M3 | youtube.com::search_results_view |
| 20260919 | trojan | https://www.youtube.com/results?search_query=bread+baking | 4 | 1 | 0 | E2 | M2-M3 | youtube.com::search_results_view |
| 20260919 | trojan | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 0 | E2 | M2-M3 | youtube.com::search_results_view |
| 20260919 | trojan | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E2 | M2-M3 | youtube.com::search_results_view |
| 20260919 | trojan | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E2 | M2-M3 | youtube.com::video_playback |
| 20260919 | trojan | youtube_video:aircAruvnKk | 5 | 0 | 0 | E2 | M2-M3 | youtube.com::video_playback |
| 20260919 | trojan | youtube_video:aqz-KE-bpKQ | 5 | 0 | 2 | E2 | M2-M3 | youtube.com::video_playback |
| 20260919 | trojan | youtube_video:eRsGyueVLvQ | 5 | 0 | 1 | E2 | M2-M3 | youtube.com::video_playback |
| 20260919 | trojan | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E2 | M2-M3 | youtube.com::video_playback |
| 20260919 | vless | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 1 | 0 | E2 | M2-M3 | developer.mozilla.org::document_view |
| 20260919 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 0 | 0 | E2 | M2-M3 | developer.mozilla.org::document_view |
| 20260919 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 0 | E2 | M2-M3 | developer.mozilla.org::document_view |
| 20260919 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 2 | 0 | E2 | M2-M3 | developer.mozilla.org::document_view |
| 20260919 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 3 | 0 | E2 | M2-M3 | developer.mozilla.org::document_view |
| 20260919 | vless | https://en.wikipedia.org/wiki/Computer_network | 3 | 0 | 1 | E2 | M2-M3 | wikipedia.org::article_view |
| 20260919 | vless | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 2 | E2 | M2-M3 | wikipedia.org::article_view |
| 20260919 | vless | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 0 | 0 | E2 | M2-M3 | wikipedia.org::article_view |
| 20260919 | vless | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 3 | E2 | M2-M3 | wikipedia.org::article_view |
| 20260919 | vless | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E2 | M2-M3 | wikipedia.org::article_view |
| 20260919 | vless | https://github.com/RakuLomis/TrafficTracer | 2 | 1 | 1 | E2 | M2-M3 | github.com::repository_view |
| 20260919 | vless | https://github.com/numpy/numpy | 2 | 0 | 0 | E2 | M2-M3 | github.com::repository_view |
| 20260919 | vless | https://github.com/pallets/flask | 2 | 1 | 0 | E2 | M2-M3 | github.com::repository_view |
| 20260919 | vless | https://github.com/python/cpython | 2 | 1 | 0 | E2 | M2-M3 | github.com::repository_view |
| 20260919 | vless | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E2 | M2-M3 | github.com::repository_view |
| 20260919 | vless | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 0 | E2 | M2-M3 | bing.com::search_results_view |
| 20260919 | vless | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 0 | E2 | M2-M3 | bing.com::search_results_view |
| 20260919 | vless | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E2 | M2-M3 | bing.com::search_results_view |
| 20260919 | vless | https://www.bing.com/search?q=solar+system+facts | 0 | 1 | 0 | E2 | M2-M3 | bing.com::search_results_view |
| 20260919 | vless | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 1 | 0 | E2 | M2-M3 | bing.com::search_results_view |
| 20260919 | vless | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E2 | M2-M3 | youtube.com::search_results_view |
| 20260919 | vless | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 0 | E2 | M2-M3 | youtube.com::search_results_view |
| 20260919 | vless | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E2 | M2-M3 | youtube.com::search_results_view |
| 20260919 | vless | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 0 | E2 | M2-M3 | youtube.com::search_results_view |
| 20260919 | vless | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E2 | M2-M3 | youtube.com::search_results_view |
| 20260919 | vless | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E2 | M2-M3 | youtube.com::video_playback |
| 20260919 | vless | youtube_video:aircAruvnKk | 5 | 0 | 0 | E2 | M2-M3 | youtube.com::video_playback |
| 20260919 | vless | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E2 | M2-M3 | youtube.com::video_playback |
| 20260919 | vless | youtube_video:eRsGyueVLvQ | 5 | 0 | 1 | E2 | M2-M3 | youtube.com::video_playback |
| 20260919 | vless | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E2 | M2-M3 | youtube.com::video_playback |
| 20260919 | vmess | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 0 | E2 | M2-M3 | developer.mozilla.org::document_view |
| 20260919 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 0 | 0 | E2 | M2-M3 | developer.mozilla.org::document_view |
| 20260919 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 0 | E2 | M2-M3 | developer.mozilla.org::document_view |
| 20260919 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 0 | 0 | E2 | M2-M3 | developer.mozilla.org::document_view |
| 20260919 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 1 | 0 | E2 | M2-M3 | developer.mozilla.org::document_view |
| 20260919 | vmess | https://en.wikipedia.org/wiki/Computer_network | 3 | 1 | 0 | E2 | M2-M3 | wikipedia.org::article_view |
| 20260919 | vmess | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 0 | E2 | M2-M3 | wikipedia.org::article_view |
| 20260919 | vmess | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 0 | 0 | E2 | M2-M3 | wikipedia.org::article_view |
| 20260919 | vmess | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 1 | E2 | M2-M3 | wikipedia.org::article_view |
| 20260919 | vmess | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E2 | M2-M3 | wikipedia.org::article_view |
| 20260919 | vmess | https://github.com/RakuLomis/TrafficTracer | 2 | 1 | 0 | E2 | M2-M3 | github.com::repository_view |
| 20260919 | vmess | https://github.com/numpy/numpy | 2 | 0 | 0 | E2 | M2-M3 | github.com::repository_view |
| 20260919 | vmess | https://github.com/pallets/flask | 2 | 0 | 0 | E2 | M2-M3 | github.com::repository_view |
| 20260919 | vmess | https://github.com/python/cpython | 2 | 0 | 0 | E2 | M2-M3 | github.com::repository_view |
| 20260919 | vmess | https://github.com/scikit-learn/scikit-learn | 2 | 1 | 0 | E2 | M2-M3 | github.com::repository_view |
| 20260919 | vmess | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 1 | E2 | M2-M3 | bing.com::search_results_view |
| 20260919 | vmess | https://www.bing.com/search?q=indoor+plant+care | 0 | 1 | 0 | E2 | M2-M3 | bing.com::search_results_view |
| 20260919 | vmess | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E2 | M2-M3 | bing.com::search_results_view |
| 20260919 | vmess | https://www.bing.com/search?q=solar+system+facts | 0 | 0 | 0 | E2 | M2-M3 | bing.com::search_results_view |
| 20260919 | vmess | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 0 | E2 | M2-M3 | bing.com::search_results_view |
| 20260919 | vmess | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E2 | M2-M3 | youtube.com::search_results_view |
| 20260919 | vmess | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 1 | 0 | E2 | M2-M3 | youtube.com::search_results_view |
| 20260919 | vmess | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E2 | M2-M3 | youtube.com::search_results_view |
| 20260919 | vmess | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 0 | E2 | M2-M3 | youtube.com::search_results_view |
| 20260919 | vmess | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E2 | M2-M3 | youtube.com::search_results_view |
| 20260919 | vmess | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E2 | M2-M3 | youtube.com::video_playback |
| 20260919 | vmess | youtube_video:aircAruvnKk | 5 | 0 | 0 | E2 | M2-M3 | youtube.com::video_playback |
| 20260919 | vmess | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E2 | M2-M3 | youtube.com::video_playback |
| 20260919 | vmess | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E2 | M2-M3 | youtube.com::video_playback |
| 20260919 | vmess | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E2 | M2-M3 | youtube.com::video_playback |
| 20260920 | anytls | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 3 | 0 | E2 | M2-M3 | developer.mozilla.org::document_view |
| 20260920 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 4 | 0 | E2 | M2-M3 | developer.mozilla.org::document_view |
| 20260920 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 0 | E2 | M2-M3 | developer.mozilla.org::document_view |
| 20260920 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 2 | 0 | E2 | M2-M3 | developer.mozilla.org::document_view |
| 20260920 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 0 | 0 | E2 | M2-M3 | developer.mozilla.org::document_view |
| 20260920 | anytls | https://en.wikipedia.org/wiki/Computer_network | 3 | 1 | 0 | E2 | M2-M3 | wikipedia.org::article_view |
| 20260920 | anytls | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 1 | E2 | M2-M3 | wikipedia.org::article_view |
| 20260920 | anytls | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 0 | 2 | E2 | M2-M3 | wikipedia.org::article_view |
| 20260920 | anytls | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 0 | E2 | M2-M3 | wikipedia.org::article_view |
| 20260920 | anytls | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 1 | E2 | M2-M3 | wikipedia.org::article_view |
| 20260920 | anytls | https://github.com/RakuLomis/TrafficTracer | 2 | 0 | 0 | E2 | M2-M3 | github.com::repository_view |
| 20260920 | anytls | https://github.com/numpy/numpy | 2 | 0 | 0 | E2 | M2-M3 | github.com::repository_view |
| 20260920 | anytls | https://github.com/pallets/flask | 2 | 0 | 0 | E2 | M2-M3 | github.com::repository_view |
| 20260920 | anytls | https://github.com/python/cpython | 2 | 1 | 0 | E2 | M2-M3 | github.com::repository_view |
| 20260920 | anytls | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E2 | M2-M3 | github.com::repository_view |
| 20260920 | anytls | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 0 | E2 | M2-M3 | bing.com::search_results_view |
| 20260920 | anytls | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 1 | E2 | M2-M3 | bing.com::search_results_view |
| 20260920 | anytls | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E2 | M2-M3 | bing.com::search_results_view |
| 20260920 | anytls | https://www.bing.com/search?q=solar+system+facts | 0 | 0 | 0 | E2 | M2-M3 | bing.com::search_results_view |
| 20260920 | anytls | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 0 | E2 | M2-M3 | bing.com::search_results_view |
| 20260920 | anytls | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 2 | 0 | E2 | M2-M3 | youtube.com::search_results_view |
| 20260920 | anytls | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 0 | E2 | M2-M3 | youtube.com::search_results_view |
| 20260920 | anytls | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E2 | M2-M3 | youtube.com::search_results_view |
| 20260920 | anytls | https://www.youtube.com/results?search_query=piano+practice | 4 | 1 | 1 | E2 | M2-M3 | youtube.com::search_results_view |
| 20260920 | anytls | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E2 | M2-M3 | youtube.com::search_results_view |
| 20260920 | anytls | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E2 | M2-M3 | youtube.com::video_playback |
| 20260920 | anytls | youtube_video:aircAruvnKk | 5 | 0 | 0 | E2 | M2-M3 | youtube.com::video_playback |
| 20260920 | anytls | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E2 | M2-M3 | youtube.com::video_playback |
| 20260920 | anytls | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E2 | M2-M3 | youtube.com::video_playback |
| 20260920 | anytls | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E2 | M2-M3 | youtube.com::video_playback |
| 20260920 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 1 | E2 | M2-M3 | developer.mozilla.org::document_view |
| 20260920 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 0 | 3 | E2 | M2-M3 | developer.mozilla.org::document_view |
| 20260920 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 0 | E2 | M2-M3 | developer.mozilla.org::document_view |
| 20260920 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 0 | 0 | E2 | M2-M3 | developer.mozilla.org::document_view |
| 20260920 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 0 | 0 | E2 | M2-M3 | developer.mozilla.org::document_view |
| 20260920 | shadowsocks | https://en.wikipedia.org/wiki/Computer_network | 3 | 0 | 0 | E2 | M2-M3 | wikipedia.org::article_view |
| 20260920 | shadowsocks | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 0 | E2 | M2-M3 | wikipedia.org::article_view |
| 20260920 | shadowsocks | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 0 | 0 | E2 | M2-M3 | wikipedia.org::article_view |
| 20260920 | shadowsocks | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 0 | E2 | M2-M3 | wikipedia.org::article_view |
| 20260920 | shadowsocks | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E2 | M2-M3 | wikipedia.org::article_view |
| 20260920 | shadowsocks | https://github.com/RakuLomis/TrafficTracer | 2 | 0 | 0 | E2 | M2-M3 | github.com::repository_view |
| 20260920 | shadowsocks | https://github.com/numpy/numpy | 2 | 0 | 0 | E2 | M2-M3 | github.com::repository_view |
| 20260920 | shadowsocks | https://github.com/pallets/flask | 2 | 0 | 0 | E2 | M2-M3 | github.com::repository_view |
| 20260920 | shadowsocks | https://github.com/python/cpython | 2 | 0 | 0 | E2 | M2-M3 | github.com::repository_view |
| 20260920 | shadowsocks | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E2 | M2-M3 | github.com::repository_view |
| 20260920 | shadowsocks | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 4 | E2 | M2-M3 | bing.com::search_results_view |
| 20260920 | shadowsocks | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 1 | E2 | M2-M3 | bing.com::search_results_view |
| 20260920 | shadowsocks | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 2 | E2 | M2-M3 | bing.com::search_results_view |
| 20260920 | shadowsocks | https://www.bing.com/search?q=solar+system+facts | 0 | 0 | 0 | E2 | M2-M3 | bing.com::search_results_view |
| 20260920 | shadowsocks | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 1 | 1 | E2 | M2-M3 | bing.com::search_results_view |
| 20260920 | shadowsocks | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E2 | M2-M3 | youtube.com::search_results_view |
| 20260920 | shadowsocks | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 0 | E2 | M2-M3 | youtube.com::search_results_view |
| 20260920 | shadowsocks | https://www.youtube.com/results?search_query=bread+baking | 4 | 1 | 0 | E2 | M2-M3 | youtube.com::search_results_view |
| 20260920 | shadowsocks | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 0 | E2 | M2-M3 | youtube.com::search_results_view |
| 20260920 | shadowsocks | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E2 | M2-M3 | youtube.com::search_results_view |
| 20260920 | shadowsocks | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E2 | M2-M3 | youtube.com::video_playback |
| 20260920 | shadowsocks | youtube_video:aircAruvnKk | 5 | 0 | 0 | E2 | M2-M3 | youtube.com::video_playback |
| 20260920 | shadowsocks | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E2 | M2-M3 | youtube.com::video_playback |
| 20260920 | shadowsocks | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E2 | M2-M3 | youtube.com::video_playback |
| 20260920 | shadowsocks | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E2 | M2-M3 | youtube.com::video_playback |
| 20260920 | trojan | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 0 | E2 | M2-M3 | developer.mozilla.org::document_view |
| 20260920 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 3 | 0 | E2 | M2-M3 | developer.mozilla.org::document_view |
| 20260920 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 1 | 2 | E2 | M2-M3 | developer.mozilla.org::document_view |
| 20260920 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 0 | 0 | E2 | M2-M3 | developer.mozilla.org::document_view |
| 20260920 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 0 | 0 | E2 | M2-M3 | developer.mozilla.org::document_view |
| 20260920 | trojan | https://en.wikipedia.org/wiki/Computer_network | 3 | 2 | 0 | E2 | M2-M3 | wikipedia.org::article_view |
| 20260920 | trojan | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 1 | 1 | E2 | M2-M3 | wikipedia.org::article_view |
| 20260920 | trojan | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 0 | 1 | E2 | M2-M3 | wikipedia.org::article_view |
| 20260920 | trojan | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 1 | 0 | E2 | M2-M3 | wikipedia.org::article_view |
| 20260920 | trojan | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E2 | M2-M3 | wikipedia.org::article_view |
| 20260920 | trojan | https://github.com/RakuLomis/TrafficTracer | 2 | 3 | 0 | E2 | M2-M3 | github.com::repository_view |
| 20260920 | trojan | https://github.com/numpy/numpy | 2 | 0 | 0 | E2 | M2-M3 | github.com::repository_view |
| 20260920 | trojan | https://github.com/pallets/flask | 2 | 1 | 1 | E2 | M2-M3 | github.com::repository_view |
| 20260920 | trojan | https://github.com/python/cpython | 2 | 3 | 0 | E2 | M2-M3 | github.com::repository_view |
| 20260920 | trojan | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 1 | E2 | M2-M3 | github.com::repository_view |
| 20260920 | trojan | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 1 | 0 | E2 | M2-M3 | bing.com::search_results_view |
| 20260920 | trojan | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 0 | E2 | M2-M3 | bing.com::search_results_view |
| 20260920 | trojan | https://www.bing.com/search?q=network+traffic+analysis | 0 | 1 | 0 | E2 | M2-M3 | bing.com::search_results_view |
| 20260920 | trojan | https://www.bing.com/search?q=solar+system+facts | 0 | 2 | 0 | E2 | M2-M3 | bing.com::search_results_view |
| 20260920 | trojan | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 1 | 0 | E2 | M2-M3 | bing.com::search_results_view |
| 20260920 | trojan | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 1 | 0 | E2 | M2-M3 | youtube.com::search_results_view |
| 20260920 | trojan | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 0 | E2 | M2-M3 | youtube.com::search_results_view |
| 20260920 | trojan | https://www.youtube.com/results?search_query=bread+baking | 4 | 1 | 0 | E2 | M2-M3 | youtube.com::search_results_view |
| 20260920 | trojan | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 0 | E2 | M2-M3 | youtube.com::search_results_view |
| 20260920 | trojan | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E2 | M2-M3 | youtube.com::search_results_view |
| 20260920 | trojan | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E2 | M2-M3 | youtube.com::video_playback |
| 20260920 | trojan | youtube_video:aircAruvnKk | 5 | 0 | 0 | E2 | M2-M3 | youtube.com::video_playback |
| 20260920 | trojan | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E2 | M2-M3 | youtube.com::video_playback |
| 20260920 | trojan | youtube_video:eRsGyueVLvQ | 5 | 0 | 1 | E2 | M2-M3 | youtube.com::video_playback |
| 20260920 | trojan | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E2 | M2-M3 | youtube.com::video_playback |
| 20260920 | vless | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 3 | 0 | E2 | M2-M3 | developer.mozilla.org::document_view |
| 20260920 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 0 | 0 | E2 | M2-M3 | developer.mozilla.org::document_view |
| 20260920 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 0 | E2 | M2-M3 | developer.mozilla.org::document_view |
| 20260920 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 2 | 0 | E2 | M2-M3 | developer.mozilla.org::document_view |
| 20260920 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 0 | 1 | E2 | M2-M3 | developer.mozilla.org::document_view |
| 20260920 | vless | https://en.wikipedia.org/wiki/Computer_network | 3 | 0 | 1 | E2 | M2-M3 | wikipedia.org::article_view |
| 20260920 | vless | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 1 | E2 | M2-M3 | wikipedia.org::article_view |
| 20260920 | vless | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 0 | 0 | E2 | M2-M3 | wikipedia.org::article_view |
| 20260920 | vless | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 0 | E2 | M2-M3 | wikipedia.org::article_view |
| 20260920 | vless | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E2 | M2-M3 | wikipedia.org::article_view |
| 20260920 | vless | https://github.com/RakuLomis/TrafficTracer | 2 | 2 | 0 | E2 | M2-M3 | github.com::repository_view |
| 20260920 | vless | https://github.com/numpy/numpy | 2 | 0 | 0 | E2 | M2-M3 | github.com::repository_view |
| 20260920 | vless | https://github.com/pallets/flask | 2 | 0 | 0 | E2 | M2-M3 | github.com::repository_view |
| 20260920 | vless | https://github.com/python/cpython | 2 | 0 | 0 | E2 | M2-M3 | github.com::repository_view |
| 20260920 | vless | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E2 | M2-M3 | github.com::repository_view |
| 20260920 | vless | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 0 | E2 | M2-M3 | bing.com::search_results_view |
| 20260920 | vless | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 1 | E2 | M2-M3 | bing.com::search_results_view |
| 20260920 | vless | https://www.bing.com/search?q=network+traffic+analysis | 0 | 1 | 0 | E2 | M2-M3 | bing.com::search_results_view |
| 20260920 | vless | https://www.bing.com/search?q=solar+system+facts | 0 | 2 | 0 | E2 | M2-M3 | bing.com::search_results_view |
| 20260920 | vless | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 1 | 0 | E2 | M2-M3 | bing.com::search_results_view |
| 20260920 | vless | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E2 | M2-M3 | youtube.com::search_results_view |
| 20260920 | vless | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 0 | E2 | M2-M3 | youtube.com::search_results_view |
| 20260920 | vless | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E2 | M2-M3 | youtube.com::search_results_view |
| 20260920 | vless | https://www.youtube.com/results?search_query=piano+practice | 4 | 1 | 0 | E2 | M2-M3 | youtube.com::search_results_view |
| 20260920 | vless | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E2 | M2-M3 | youtube.com::search_results_view |
| 20260920 | vless | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E2 | M2-M3 | youtube.com::video_playback |
| 20260920 | vless | youtube_video:aircAruvnKk | 5 | 0 | 0 | E2 | M2-M3 | youtube.com::video_playback |
| 20260920 | vless | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E2 | M2-M3 | youtube.com::video_playback |
| 20260920 | vless | youtube_video:eRsGyueVLvQ | 5 | 0 | 1 | E2 | M2-M3 | youtube.com::video_playback |
| 20260920 | vless | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E2 | M2-M3 | youtube.com::video_playback |
| 20260920 | vmess | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 0 | E2 | M2-M3 | developer.mozilla.org::document_view |
| 20260920 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 0 | 0 | E2 | M2-M3 | developer.mozilla.org::document_view |
| 20260920 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 0 | E2 | M2-M3 | developer.mozilla.org::document_view |
| 20260920 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 0 | 0 | E2 | M2-M3 | developer.mozilla.org::document_view |
| 20260920 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 0 | 0 | E2 | M2-M3 | developer.mozilla.org::document_view |
| 20260920 | vmess | https://en.wikipedia.org/wiki/Computer_network | 3 | 1 | 0 | E2 | M2-M3 | wikipedia.org::article_view |
| 20260920 | vmess | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 0 | E2 | M2-M3 | wikipedia.org::article_view |
| 20260920 | vmess | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 0 | 0 | E2 | M2-M3 | wikipedia.org::article_view |
| 20260920 | vmess | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 0 | E2 | M2-M3 | wikipedia.org::article_view |
| 20260920 | vmess | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E2 | M2-M3 | wikipedia.org::article_view |
| 20260920 | vmess | https://github.com/RakuLomis/TrafficTracer | 2 | 1 | 0 | E2 | M2-M3 | github.com::repository_view |
| 20260920 | vmess | https://github.com/numpy/numpy | 2 | 0 | 0 | E2 | M2-M3 | github.com::repository_view |
| 20260920 | vmess | https://github.com/pallets/flask | 2 | 0 | 1 | E2 | M2-M3 | github.com::repository_view |
| 20260920 | vmess | https://github.com/python/cpython | 2 | 0 | 0 | E2 | M2-M3 | github.com::repository_view |
| 20260920 | vmess | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E2 | M2-M3 | github.com::repository_view |
| 20260920 | vmess | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 2 | 0 | E2 | M2-M3 | bing.com::search_results_view |
| 20260920 | vmess | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 0 | E2 | M2-M3 | bing.com::search_results_view |
| 20260920 | vmess | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E2 | M2-M3 | bing.com::search_results_view |
| 20260920 | vmess | https://www.bing.com/search?q=solar+system+facts | 0 | 0 | 0 | E2 | M2-M3 | bing.com::search_results_view |
| 20260920 | vmess | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 0 | E2 | M2-M3 | bing.com::search_results_view |
| 20260920 | vmess | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E2 | M2-M3 | youtube.com::search_results_view |
| 20260920 | vmess | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 1 | 0 | E2 | M2-M3 | youtube.com::search_results_view |
| 20260920 | vmess | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E2 | M2-M3 | youtube.com::search_results_view |
| 20260920 | vmess | https://www.youtube.com/results?search_query=piano+practice | 4 | 1 | 1 | E2 | M2-M3 | youtube.com::search_results_view |
| 20260920 | vmess | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E2 | M2-M3 | youtube.com::search_results_view |
| 20260920 | vmess | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E2 | M2-M3 | youtube.com::video_playback |
| 20260920 | vmess | youtube_video:aircAruvnKk | 5 | 0 | 1 | E2 | M2-M3 | youtube.com::video_playback |
| 20260920 | vmess | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E2 | M2-M3 | youtube.com::video_playback |
| 20260920 | vmess | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E2 | M2-M3 | youtube.com::video_playback |
| 20260920 | vmess | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E2 | M2-M3 | youtube.com::video_playback |
| 20260918 | anytls | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 1 | 0 | E2 | M2-M4 | developer.mozilla.org::document_view |
| 20260918 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 1 | 0 | E2 | M2-M4 | developer.mozilla.org::document_view |
| 20260918 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 0 | E2 | M2-M4 | developer.mozilla.org::document_view |
| 20260918 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 3 | 0 | E2 | M2-M4 | developer.mozilla.org::document_view |
| 20260918 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 3 | 0 | E2 | M2-M4 | developer.mozilla.org::document_view |
| 20260918 | anytls | https://en.wikipedia.org/wiki/Computer_network | 3 | 0 | 0 | E2 | M2-M4 | wikipedia.org::article_view |
| 20260918 | anytls | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 2 | E2 | M2-M4 | wikipedia.org::article_view |
| 20260918 | anytls | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 0 | 0 | E2 | M2-M4 | wikipedia.org::article_view |
| 20260918 | anytls | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 1 | E2 | M2-M4 | wikipedia.org::article_view |
| 20260918 | anytls | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E2 | M2-M4 | wikipedia.org::article_view |
| 20260918 | anytls | https://github.com/RakuLomis/TrafficTracer | 2 | 0 | 0 | E2 | M2-M4 | github.com::repository_view |
| 20260918 | anytls | https://github.com/numpy/numpy | 2 | 0 | 0 | E2 | M2-M4 | github.com::repository_view |
| 20260918 | anytls | https://github.com/pallets/flask | 2 | 0 | 0 | E2 | M2-M4 | github.com::repository_view |
| 20260918 | anytls | https://github.com/python/cpython | 2 | 1 | 0 | E2 | M2-M4 | github.com::repository_view |
| 20260918 | anytls | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E2 | M2-M4 | github.com::repository_view |
| 20260918 | anytls | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 0 | E2 | M2-M4 | bing.com::search_results_view |
| 20260918 | anytls | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 3 | E2 | M2-M4 | bing.com::search_results_view |
| 20260918 | anytls | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E2 | M2-M4 | bing.com::search_results_view |
| 20260918 | anytls | https://www.bing.com/search?q=solar+system+facts | 0 | 0 | 0 | E2 | M2-M4 | bing.com::search_results_view |
| 20260918 | anytls | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 0 | E2 | M2-M4 | bing.com::search_results_view |
| 20260918 | anytls | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 1 | 0 | E2 | M2-M4 | youtube.com::search_results_view |
| 20260918 | anytls | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 1 | E2 | M2-M4 | youtube.com::search_results_view |
| 20260918 | anytls | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E2 | M2-M4 | youtube.com::search_results_view |
| 20260918 | anytls | https://www.youtube.com/results?search_query=piano+practice | 4 | 1 | 0 | E2 | M2-M4 | youtube.com::search_results_view |
| 20260918 | anytls | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 1 | E2 | M2-M4 | youtube.com::search_results_view |
| 20260918 | anytls | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E2 | M2-M4 | youtube.com::video_playback |
| 20260918 | anytls | youtube_video:aircAruvnKk | 5 | 0 | 0 | E2 | M2-M4 | youtube.com::video_playback |
| 20260918 | anytls | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E2 | M2-M4 | youtube.com::video_playback |
| 20260918 | anytls | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E2 | M2-M4 | youtube.com::video_playback |
| 20260918 | anytls | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E2 | M2-M4 | youtube.com::video_playback |
| 20260918 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 1 | 0 | E2 | M2-M4 | developer.mozilla.org::document_view |
| 20260918 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 0 | 3 | E2 | M2-M4 | developer.mozilla.org::document_view |
| 20260918 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 1 | E2 | M2-M4 | developer.mozilla.org::document_view |
| 20260918 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 0 | 1 | E2 | M2-M4 | developer.mozilla.org::document_view |
| 20260918 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 0 | 0 | E2 | M2-M4 | developer.mozilla.org::document_view |
| 20260918 | shadowsocks | https://en.wikipedia.org/wiki/Computer_network | 3 | 0 | 0 | E2 | M2-M4 | wikipedia.org::article_view |
| 20260918 | shadowsocks | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 0 | E2 | M2-M4 | wikipedia.org::article_view |
| 20260918 | shadowsocks | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 0 | 1 | E2 | M2-M4 | wikipedia.org::article_view |
| 20260918 | shadowsocks | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 0 | E2 | M2-M4 | wikipedia.org::article_view |
| 20260918 | shadowsocks | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E2 | M2-M4 | wikipedia.org::article_view |
| 20260918 | shadowsocks | https://github.com/RakuLomis/TrafficTracer | 2 | 0 | 0 | E2 | M2-M4 | github.com::repository_view |
| 20260918 | shadowsocks | https://github.com/numpy/numpy | 2 | 0 | 0 | E2 | M2-M4 | github.com::repository_view |
| 20260918 | shadowsocks | https://github.com/pallets/flask | 2 | 0 | 0 | E2 | M2-M4 | github.com::repository_view |
| 20260918 | shadowsocks | https://github.com/python/cpython | 2 | 0 | 0 | E2 | M2-M4 | github.com::repository_view |
| 20260918 | shadowsocks | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E2 | M2-M4 | github.com::repository_view |
| 20260918 | shadowsocks | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 3 | E2 | M2-M4 | bing.com::search_results_view |
| 20260918 | shadowsocks | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 1 | E2 | M2-M4 | bing.com::search_results_view |
| 20260918 | shadowsocks | https://www.bing.com/search?q=network+traffic+analysis | 0 | 1 | 0 | E2 | M2-M4 | bing.com::search_results_view |
| 20260918 | shadowsocks | https://www.bing.com/search?q=solar+system+facts | 0 | 0 | 0 | E2 | M2-M4 | bing.com::search_results_view |
| 20260918 | shadowsocks | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 0 | E2 | M2-M4 | bing.com::search_results_view |
| 20260918 | shadowsocks | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E2 | M2-M4 | youtube.com::search_results_view |
| 20260918 | shadowsocks | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 1 | E2 | M2-M4 | youtube.com::search_results_view |
| 20260918 | shadowsocks | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 1 | E2 | M2-M4 | youtube.com::search_results_view |
| 20260918 | shadowsocks | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 1 | E2 | M2-M4 | youtube.com::search_results_view |
| 20260918 | shadowsocks | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E2 | M2-M4 | youtube.com::search_results_view |
| 20260918 | shadowsocks | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E2 | M2-M4 | youtube.com::video_playback |
| 20260918 | shadowsocks | youtube_video:aircAruvnKk | 5 | 0 | 0 | E2 | M2-M4 | youtube.com::video_playback |
| 20260918 | shadowsocks | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E2 | M2-M4 | youtube.com::video_playback |
| 20260918 | shadowsocks | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E2 | M2-M4 | youtube.com::video_playback |
| 20260918 | shadowsocks | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E2 | M2-M4 | youtube.com::video_playback |
| 20260918 | trojan | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 0 | E2 | M2-M4 | developer.mozilla.org::document_view |
| 20260918 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 3 | 0 | E2 | M2-M4 | developer.mozilla.org::document_view |
| 20260918 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 3 | 0 | E2 | M2-M4 | developer.mozilla.org::document_view |
| 20260918 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 1 | 0 | E2 | M2-M4 | developer.mozilla.org::document_view |
| 20260918 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 0 | 0 | E2 | M2-M4 | developer.mozilla.org::document_view |
| 20260918 | trojan | https://en.wikipedia.org/wiki/Computer_network | 3 | 0 | 0 | E2 | M2-M4 | wikipedia.org::article_view |
| 20260918 | trojan | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 2 | E2 | M2-M4 | wikipedia.org::article_view |
| 20260918 | trojan | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 1 | 0 | E2 | M2-M4 | wikipedia.org::article_view |
| 20260918 | trojan | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 0 | E2 | M2-M4 | wikipedia.org::article_view |
| 20260918 | trojan | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E2 | M2-M4 | wikipedia.org::article_view |
| 20260918 | trojan | https://github.com/RakuLomis/TrafficTracer | 2 | 3 | 0 | E2 | M2-M4 | github.com::repository_view |
| 20260918 | trojan | https://github.com/numpy/numpy | 2 | 0 | 0 | E2 | M2-M4 | github.com::repository_view |
| 20260918 | trojan | https://github.com/pallets/flask | 2 | 1 | 0 | E2 | M2-M4 | github.com::repository_view |
| 20260918 | trojan | https://github.com/python/cpython | 2 | 3 | 0 | E2 | M2-M4 | github.com::repository_view |
| 20260918 | trojan | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 1 | E2 | M2-M4 | github.com::repository_view |
| 20260918 | trojan | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 0 | E2 | M2-M4 | bing.com::search_results_view |
| 20260918 | trojan | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 0 | E2 | M2-M4 | bing.com::search_results_view |
| 20260918 | trojan | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E2 | M2-M4 | bing.com::search_results_view |
| 20260918 | trojan | https://www.bing.com/search?q=solar+system+facts | 0 | 1 | 1 | E2 | M2-M4 | bing.com::search_results_view |
| 20260918 | trojan | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 2 | 0 | E2 | M2-M4 | bing.com::search_results_view |
| 20260918 | trojan | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E2 | M2-M4 | youtube.com::search_results_view |
| 20260918 | trojan | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 0 | E2 | M2-M4 | youtube.com::search_results_view |
| 20260918 | trojan | https://www.youtube.com/results?search_query=bread+baking | 4 | 1 | 0 | E2 | M2-M4 | youtube.com::search_results_view |
| 20260918 | trojan | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 0 | E2 | M2-M4 | youtube.com::search_results_view |
| 20260918 | trojan | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E2 | M2-M4 | youtube.com::search_results_view |
| 20260918 | trojan | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E2 | M2-M4 | youtube.com::video_playback |
| 20260918 | trojan | youtube_video:aircAruvnKk | 5 | 0 | 0 | E2 | M2-M4 | youtube.com::video_playback |
| 20260918 | trojan | youtube_video:aqz-KE-bpKQ | 5 | 2 | 0 | E2 | M2-M4 | youtube.com::video_playback |
| 20260918 | trojan | youtube_video:eRsGyueVLvQ | 5 | 0 | 2 | E2 | M2-M4 | youtube.com::video_playback |
| 20260918 | trojan | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E2 | M2-M4 | youtube.com::video_playback |
| 20260918 | vless | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 2 | 0 | E2 | M2-M4 | developer.mozilla.org::document_view |
| 20260918 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 0 | 0 | E2 | M2-M4 | developer.mozilla.org::document_view |
| 20260918 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 0 | E2 | M2-M4 | developer.mozilla.org::document_view |
| 20260918 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 2 | 0 | E2 | M2-M4 | developer.mozilla.org::document_view |
| 20260918 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 2 | 0 | E2 | M2-M4 | developer.mozilla.org::document_view |
| 20260918 | vless | https://en.wikipedia.org/wiki/Computer_network | 3 | 0 | 0 | E2 | M2-M4 | wikipedia.org::article_view |
| 20260918 | vless | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 1 | E2 | M2-M4 | wikipedia.org::article_view |
| 20260918 | vless | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 1 | 1 | E2 | M2-M4 | wikipedia.org::article_view |
| 20260918 | vless | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 2 | E2 | M2-M4 | wikipedia.org::article_view |
| 20260918 | vless | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E2 | M2-M4 | wikipedia.org::article_view |
| 20260918 | vless | https://github.com/RakuLomis/TrafficTracer | 2 | 2 | 0 | E2 | M2-M4 | github.com::repository_view |
| 20260918 | vless | https://github.com/numpy/numpy | 2 | 0 | 0 | E2 | M2-M4 | github.com::repository_view |
| 20260918 | vless | https://github.com/pallets/flask | 2 | 0 | 0 | E2 | M2-M4 | github.com::repository_view |
| 20260918 | vless | https://github.com/python/cpython | 2 | 1 | 0 | E2 | M2-M4 | github.com::repository_view |
| 20260918 | vless | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E2 | M2-M4 | github.com::repository_view |
| 20260918 | vless | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 1 | 0 | E2 | M2-M4 | bing.com::search_results_view |
| 20260918 | vless | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 0 | E2 | M2-M4 | bing.com::search_results_view |
| 20260918 | vless | https://www.bing.com/search?q=network+traffic+analysis | 0 | 1 | 0 | E2 | M2-M4 | bing.com::search_results_view |
| 20260918 | vless | https://www.bing.com/search?q=solar+system+facts | 0 | 3 | 1 | E2 | M2-M4 | bing.com::search_results_view |
| 20260918 | vless | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 1 | 0 | E2 | M2-M4 | bing.com::search_results_view |
| 20260918 | vless | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E2 | M2-M4 | youtube.com::search_results_view |
| 20260918 | vless | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 0 | E2 | M2-M4 | youtube.com::search_results_view |
| 20260918 | vless | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 1 | E2 | M2-M4 | youtube.com::search_results_view |
| 20260918 | vless | https://www.youtube.com/results?search_query=piano+practice | 4 | 1 | 0 | E2 | M2-M4 | youtube.com::search_results_view |
| 20260918 | vless | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 1 | E2 | M2-M4 | youtube.com::search_results_view |
| 20260918 | vless | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E2 | M2-M4 | youtube.com::video_playback |
| 20260918 | vless | youtube_video:aircAruvnKk | 5 | 0 | 0 | E2 | M2-M4 | youtube.com::video_playback |
| 20260918 | vless | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E2 | M2-M4 | youtube.com::video_playback |
| 20260918 | vless | youtube_video:eRsGyueVLvQ | 5 | 0 | 1 | E2 | M2-M4 | youtube.com::video_playback |
| 20260918 | vless | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E2 | M2-M4 | youtube.com::video_playback |
| 20260918 | vmess | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 0 | E2 | M2-M4 | developer.mozilla.org::document_view |
| 20260918 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 0 | 0 | E2 | M2-M4 | developer.mozilla.org::document_view |
| 20260918 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 0 | E2 | M2-M4 | developer.mozilla.org::document_view |
| 20260918 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 0 | 0 | E2 | M2-M4 | developer.mozilla.org::document_view |
| 20260918 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 0 | 0 | E2 | M2-M4 | developer.mozilla.org::document_view |
| 20260918 | vmess | https://en.wikipedia.org/wiki/Computer_network | 3 | 1 | 0 | E2 | M2-M4 | wikipedia.org::article_view |
| 20260918 | vmess | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 0 | E2 | M2-M4 | wikipedia.org::article_view |
| 20260918 | vmess | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 0 | 0 | E2 | M2-M4 | wikipedia.org::article_view |
| 20260918 | vmess | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 1 | E2 | M2-M4 | wikipedia.org::article_view |
| 20260918 | vmess | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E2 | M2-M4 | wikipedia.org::article_view |
| 20260918 | vmess | https://github.com/RakuLomis/TrafficTracer | 2 | 1 | 0 | E2 | M2-M4 | github.com::repository_view |
| 20260918 | vmess | https://github.com/numpy/numpy | 2 | 2 | 0 | E2 | M2-M4 | github.com::repository_view |
| 20260918 | vmess | https://github.com/pallets/flask | 2 | 0 | 1 | E2 | M2-M4 | github.com::repository_view |
| 20260918 | vmess | https://github.com/python/cpython | 2 | 0 | 0 | E2 | M2-M4 | github.com::repository_view |
| 20260918 | vmess | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E2 | M2-M4 | github.com::repository_view |
| 20260918 | vmess | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 0 | E2 | M2-M4 | bing.com::search_results_view |
| 20260918 | vmess | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 0 | E2 | M2-M4 | bing.com::search_results_view |
| 20260918 | vmess | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E2 | M2-M4 | bing.com::search_results_view |
| 20260918 | vmess | https://www.bing.com/search?q=solar+system+facts | 0 | 0 | 1 | E2 | M2-M4 | bing.com::search_results_view |
| 20260918 | vmess | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 0 | E2 | M2-M4 | bing.com::search_results_view |
| 20260918 | vmess | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E2 | M2-M4 | youtube.com::search_results_view |
| 20260918 | vmess | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 1 | 0 | E2 | M2-M4 | youtube.com::search_results_view |
| 20260918 | vmess | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E2 | M2-M4 | youtube.com::search_results_view |
| 20260918 | vmess | https://www.youtube.com/results?search_query=piano+practice | 4 | 1 | 0 | E2 | M2-M4 | youtube.com::search_results_view |
| 20260918 | vmess | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E2 | M2-M4 | youtube.com::search_results_view |
| 20260918 | vmess | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E2 | M2-M4 | youtube.com::video_playback |
| 20260918 | vmess | youtube_video:aircAruvnKk | 5 | 0 | 0 | E2 | M2-M4 | youtube.com::video_playback |
| 20260918 | vmess | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E2 | M2-M4 | youtube.com::video_playback |
| 20260918 | vmess | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E2 | M2-M4 | youtube.com::video_playback |
| 20260918 | vmess | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E2 | M2-M4 | youtube.com::video_playback |
| 20260919 | anytls | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 3 | 0 | E2 | M2-M4 | developer.mozilla.org::document_view |
| 20260919 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 2 | 0 | E2 | M2-M4 | developer.mozilla.org::document_view |
| 20260919 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 3 | 0 | E2 | M2-M4 | developer.mozilla.org::document_view |
| 20260919 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 3 | 0 | E2 | M2-M4 | developer.mozilla.org::document_view |
| 20260919 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 2 | 0 | E2 | M2-M4 | developer.mozilla.org::document_view |
| 20260919 | anytls | https://en.wikipedia.org/wiki/Computer_network | 3 | 0 | 1 | E2 | M2-M4 | wikipedia.org::article_view |
| 20260919 | anytls | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 2 | E2 | M2-M4 | wikipedia.org::article_view |
| 20260919 | anytls | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 0 | 2 | E2 | M2-M4 | wikipedia.org::article_view |
| 20260919 | anytls | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 1 | E2 | M2-M4 | wikipedia.org::article_view |
| 20260919 | anytls | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E2 | M2-M4 | wikipedia.org::article_view |
| 20260919 | anytls | https://github.com/RakuLomis/TrafficTracer | 2 | 0 | 0 | E2 | M2-M4 | github.com::repository_view |
| 20260919 | anytls | https://github.com/numpy/numpy | 2 | 0 | 0 | E2 | M2-M4 | github.com::repository_view |
| 20260919 | anytls | https://github.com/pallets/flask | 2 | 0 | 0 | E2 | M2-M4 | github.com::repository_view |
| 20260919 | anytls | https://github.com/python/cpython | 2 | 1 | 0 | E2 | M2-M4 | github.com::repository_view |
| 20260919 | anytls | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E2 | M2-M4 | github.com::repository_view |
| 20260919 | anytls | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 0 | E2 | M2-M4 | bing.com::search_results_view |
| 20260919 | anytls | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 2 | E2 | M2-M4 | bing.com::search_results_view |
| 20260919 | anytls | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E2 | M2-M4 | bing.com::search_results_view |
| 20260919 | anytls | https://www.bing.com/search?q=solar+system+facts | 0 | 0 | 0 | E2 | M2-M4 | bing.com::search_results_view |
| 20260919 | anytls | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 0 | E2 | M2-M4 | bing.com::search_results_view |
| 20260919 | anytls | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 1 | 0 | E2 | M2-M4 | youtube.com::search_results_view |
| 20260919 | anytls | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 1 | E2 | M2-M4 | youtube.com::search_results_view |
| 20260919 | anytls | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E2 | M2-M4 | youtube.com::search_results_view |
| 20260919 | anytls | https://www.youtube.com/results?search_query=piano+practice | 4 | 1 | 0 | E2 | M2-M4 | youtube.com::search_results_view |
| 20260919 | anytls | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 1 | E2 | M2-M4 | youtube.com::search_results_view |
| 20260919 | anytls | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E2 | M2-M4 | youtube.com::video_playback |
| 20260919 | anytls | youtube_video:aircAruvnKk | 5 | 0 | 0 | E2 | M2-M4 | youtube.com::video_playback |
| 20260919 | anytls | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E2 | M2-M4 | youtube.com::video_playback |
| 20260919 | anytls | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E2 | M2-M4 | youtube.com::video_playback |
| 20260919 | anytls | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E2 | M2-M4 | youtube.com::video_playback |
| 20260919 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 1 | E2 | M2-M4 | developer.mozilla.org::document_view |
| 20260919 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 0 | 3 | E2 | M2-M4 | developer.mozilla.org::document_view |
| 20260919 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 0 | E2 | M2-M4 | developer.mozilla.org::document_view |
| 20260919 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 0 | 1 | E2 | M2-M4 | developer.mozilla.org::document_view |
| 20260919 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 0 | 1 | E2 | M2-M4 | developer.mozilla.org::document_view |
| 20260919 | shadowsocks | https://en.wikipedia.org/wiki/Computer_network | 3 | 0 | 0 | E2 | M2-M4 | wikipedia.org::article_view |
| 20260919 | shadowsocks | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 0 | E2 | M2-M4 | wikipedia.org::article_view |
| 20260919 | shadowsocks | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 0 | 0 | E2 | M2-M4 | wikipedia.org::article_view |
| 20260919 | shadowsocks | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 0 | E2 | M2-M4 | wikipedia.org::article_view |
| 20260919 | shadowsocks | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E2 | M2-M4 | wikipedia.org::article_view |
| 20260919 | shadowsocks | https://github.com/RakuLomis/TrafficTracer | 2 | 0 | 0 | E2 | M2-M4 | github.com::repository_view |
| 20260919 | shadowsocks | https://github.com/numpy/numpy | 2 | 0 | 0 | E2 | M2-M4 | github.com::repository_view |
| 20260919 | shadowsocks | https://github.com/pallets/flask | 2 | 0 | 0 | E2 | M2-M4 | github.com::repository_view |
| 20260919 | shadowsocks | https://github.com/python/cpython | 2 | 0 | 0 | E2 | M2-M4 | github.com::repository_view |
| 20260919 | shadowsocks | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E2 | M2-M4 | github.com::repository_view |
| 20260919 | shadowsocks | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 4 | E2 | M2-M4 | bing.com::search_results_view |
| 20260919 | shadowsocks | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 1 | E2 | M2-M4 | bing.com::search_results_view |
| 20260919 | shadowsocks | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 1 | E2 | M2-M4 | bing.com::search_results_view |
| 20260919 | shadowsocks | https://www.bing.com/search?q=solar+system+facts | 0 | 0 | 1 | E2 | M2-M4 | bing.com::search_results_view |
| 20260919 | shadowsocks | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 1 | 1 | E2 | M2-M4 | bing.com::search_results_view |
| 20260919 | shadowsocks | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E2 | M2-M4 | youtube.com::search_results_view |
| 20260919 | shadowsocks | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 0 | E2 | M2-M4 | youtube.com::search_results_view |
| 20260919 | shadowsocks | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E2 | M2-M4 | youtube.com::search_results_view |
| 20260919 | shadowsocks | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 1 | E2 | M2-M4 | youtube.com::search_results_view |
| 20260919 | shadowsocks | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 1 | E2 | M2-M4 | youtube.com::search_results_view |
| 20260919 | shadowsocks | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E2 | M2-M4 | youtube.com::video_playback |
| 20260919 | shadowsocks | youtube_video:aircAruvnKk | 5 | 0 | 0 | E2 | M2-M4 | youtube.com::video_playback |
| 20260919 | shadowsocks | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E2 | M2-M4 | youtube.com::video_playback |
| 20260919 | shadowsocks | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E2 | M2-M4 | youtube.com::video_playback |
| 20260919 | shadowsocks | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E2 | M2-M4 | youtube.com::video_playback |
| 20260919 | trojan | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 1 | E2 | M2-M4 | developer.mozilla.org::document_view |
| 20260919 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 2 | 0 | E2 | M2-M4 | developer.mozilla.org::document_view |
| 20260919 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 2 | 0 | E2 | M2-M4 | developer.mozilla.org::document_view |
| 20260919 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 3 | 0 | E2 | M2-M4 | developer.mozilla.org::document_view |
| 20260919 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 0 | 0 | E2 | M2-M4 | developer.mozilla.org::document_view |
| 20260919 | trojan | https://en.wikipedia.org/wiki/Computer_network | 3 | 0 | 0 | E2 | M2-M4 | wikipedia.org::article_view |
| 20260919 | trojan | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 3 | E2 | M2-M4 | wikipedia.org::article_view |
| 20260919 | trojan | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 2 | 0 | E2 | M2-M4 | wikipedia.org::article_view |
| 20260919 | trojan | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 1 | 0 | E2 | M2-M4 | wikipedia.org::article_view |
| 20260919 | trojan | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E2 | M2-M4 | wikipedia.org::article_view |
| 20260919 | trojan | https://github.com/RakuLomis/TrafficTracer | 2 | 2 | 0 | E2 | M2-M4 | github.com::repository_view |
| 20260919 | trojan | https://github.com/numpy/numpy | 2 | 0 | 0 | E2 | M2-M4 | github.com::repository_view |
| 20260919 | trojan | https://github.com/pallets/flask | 2 | 1 | 0 | E2 | M2-M4 | github.com::repository_view |
| 20260919 | trojan | https://github.com/python/cpython | 2 | 4 | 0 | E2 | M2-M4 | github.com::repository_view |
| 20260919 | trojan | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 1 | E2 | M2-M4 | github.com::repository_view |
| 20260919 | trojan | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 1 | E2 | M2-M4 | bing.com::search_results_view |
| 20260919 | trojan | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 0 | E2 | M2-M4 | bing.com::search_results_view |
| 20260919 | trojan | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E2 | M2-M4 | bing.com::search_results_view |
| 20260919 | trojan | https://www.bing.com/search?q=solar+system+facts | 0 | 1 | 1 | E2 | M2-M4 | bing.com::search_results_view |
| 20260919 | trojan | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 2 | 0 | E2 | M2-M4 | bing.com::search_results_view |
| 20260919 | trojan | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E2 | M2-M4 | youtube.com::search_results_view |
| 20260919 | trojan | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 0 | E2 | M2-M4 | youtube.com::search_results_view |
| 20260919 | trojan | https://www.youtube.com/results?search_query=bread+baking | 4 | 1 | 0 | E2 | M2-M4 | youtube.com::search_results_view |
| 20260919 | trojan | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 0 | E2 | M2-M4 | youtube.com::search_results_view |
| 20260919 | trojan | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E2 | M2-M4 | youtube.com::search_results_view |
| 20260919 | trojan | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E2 | M2-M4 | youtube.com::video_playback |
| 20260919 | trojan | youtube_video:aircAruvnKk | 5 | 0 | 0 | E2 | M2-M4 | youtube.com::video_playback |
| 20260919 | trojan | youtube_video:aqz-KE-bpKQ | 5 | 0 | 2 | E2 | M2-M4 | youtube.com::video_playback |
| 20260919 | trojan | youtube_video:eRsGyueVLvQ | 5 | 0 | 2 | E2 | M2-M4 | youtube.com::video_playback |
| 20260919 | trojan | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E2 | M2-M4 | youtube.com::video_playback |
| 20260919 | vless | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 2 | 0 | E2 | M2-M4 | developer.mozilla.org::document_view |
| 20260919 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 0 | 0 | E2 | M2-M4 | developer.mozilla.org::document_view |
| 20260919 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 0 | E2 | M2-M4 | developer.mozilla.org::document_view |
| 20260919 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 2 | 0 | E2 | M2-M4 | developer.mozilla.org::document_view |
| 20260919 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 0 | 0 | E2 | M2-M4 | developer.mozilla.org::document_view |
| 20260919 | vless | https://en.wikipedia.org/wiki/Computer_network | 3 | 0 | 2 | E2 | M2-M4 | wikipedia.org::article_view |
| 20260919 | vless | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 2 | E2 | M2-M4 | wikipedia.org::article_view |
| 20260919 | vless | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 0 | 1 | E2 | M2-M4 | wikipedia.org::article_view |
| 20260919 | vless | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 0 | E2 | M2-M4 | wikipedia.org::article_view |
| 20260919 | vless | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E2 | M2-M4 | wikipedia.org::article_view |
| 20260919 | vless | https://github.com/RakuLomis/TrafficTracer | 2 | 1 | 1 | E2 | M2-M4 | github.com::repository_view |
| 20260919 | vless | https://github.com/numpy/numpy | 2 | 0 | 0 | E2 | M2-M4 | github.com::repository_view |
| 20260919 | vless | https://github.com/pallets/flask | 2 | 1 | 0 | E2 | M2-M4 | github.com::repository_view |
| 20260919 | vless | https://github.com/python/cpython | 2 | 1 | 0 | E2 | M2-M4 | github.com::repository_view |
| 20260919 | vless | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E2 | M2-M4 | github.com::repository_view |
| 20260919 | vless | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 0 | E2 | M2-M4 | bing.com::search_results_view |
| 20260919 | vless | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 0 | E2 | M2-M4 | bing.com::search_results_view |
| 20260919 | vless | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E2 | M2-M4 | bing.com::search_results_view |
| 20260919 | vless | https://www.bing.com/search?q=solar+system+facts | 0 | 1 | 0 | E2 | M2-M4 | bing.com::search_results_view |
| 20260919 | vless | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 1 | 0 | E2 | M2-M4 | bing.com::search_results_view |
| 20260919 | vless | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E2 | M2-M4 | youtube.com::search_results_view |
| 20260919 | vless | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 1 | E2 | M2-M4 | youtube.com::search_results_view |
| 20260919 | vless | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E2 | M2-M4 | youtube.com::search_results_view |
| 20260919 | vless | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 0 | E2 | M2-M4 | youtube.com::search_results_view |
| 20260919 | vless | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E2 | M2-M4 | youtube.com::search_results_view |
| 20260919 | vless | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E2 | M2-M4 | youtube.com::video_playback |
| 20260919 | vless | youtube_video:aircAruvnKk | 5 | 0 | 1 | E2 | M2-M4 | youtube.com::video_playback |
| 20260919 | vless | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E2 | M2-M4 | youtube.com::video_playback |
| 20260919 | vless | youtube_video:eRsGyueVLvQ | 5 | 0 | 1 | E2 | M2-M4 | youtube.com::video_playback |
| 20260919 | vless | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E2 | M2-M4 | youtube.com::video_playback |
| 20260919 | vmess | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 0 | E2 | M2-M4 | developer.mozilla.org::document_view |
| 20260919 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 0 | 0 | E2 | M2-M4 | developer.mozilla.org::document_view |
| 20260919 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 0 | E2 | M2-M4 | developer.mozilla.org::document_view |
| 20260919 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 0 | 0 | E2 | M2-M4 | developer.mozilla.org::document_view |
| 20260919 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 1 | 0 | E2 | M2-M4 | developer.mozilla.org::document_view |
| 20260919 | vmess | https://en.wikipedia.org/wiki/Computer_network | 3 | 1 | 0 | E2 | M2-M4 | wikipedia.org::article_view |
| 20260919 | vmess | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 0 | E2 | M2-M4 | wikipedia.org::article_view |
| 20260919 | vmess | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 0 | 0 | E2 | M2-M4 | wikipedia.org::article_view |
| 20260919 | vmess | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 0 | E2 | M2-M4 | wikipedia.org::article_view |
| 20260919 | vmess | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E2 | M2-M4 | wikipedia.org::article_view |
| 20260919 | vmess | https://github.com/RakuLomis/TrafficTracer | 2 | 1 | 0 | E2 | M2-M4 | github.com::repository_view |
| 20260919 | vmess | https://github.com/numpy/numpy | 2 | 2 | 0 | E2 | M2-M4 | github.com::repository_view |
| 20260919 | vmess | https://github.com/pallets/flask | 2 | 0 | 0 | E2 | M2-M4 | github.com::repository_view |
| 20260919 | vmess | https://github.com/python/cpython | 2 | 0 | 0 | E2 | M2-M4 | github.com::repository_view |
| 20260919 | vmess | https://github.com/scikit-learn/scikit-learn | 2 | 1 | 0 | E2 | M2-M4 | github.com::repository_view |
| 20260919 | vmess | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 1 | 1 | E2 | M2-M4 | bing.com::search_results_view |
| 20260919 | vmess | https://www.bing.com/search?q=indoor+plant+care | 0 | 1 | 0 | E2 | M2-M4 | bing.com::search_results_view |
| 20260919 | vmess | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E2 | M2-M4 | bing.com::search_results_view |
| 20260919 | vmess | https://www.bing.com/search?q=solar+system+facts | 0 | 0 | 1 | E2 | M2-M4 | bing.com::search_results_view |
| 20260919 | vmess | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 1 | 0 | E2 | M2-M4 | bing.com::search_results_view |
| 20260919 | vmess | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E2 | M2-M4 | youtube.com::search_results_view |
| 20260919 | vmess | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 1 | 0 | E2 | M2-M4 | youtube.com::search_results_view |
| 20260919 | vmess | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E2 | M2-M4 | youtube.com::search_results_view |
| 20260919 | vmess | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 0 | E2 | M2-M4 | youtube.com::search_results_view |
| 20260919 | vmess | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E2 | M2-M4 | youtube.com::search_results_view |
| 20260919 | vmess | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E2 | M2-M4 | youtube.com::video_playback |
| 20260919 | vmess | youtube_video:aircAruvnKk | 5 | 0 | 0 | E2 | M2-M4 | youtube.com::video_playback |
| 20260919 | vmess | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E2 | M2-M4 | youtube.com::video_playback |
| 20260919 | vmess | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E2 | M2-M4 | youtube.com::video_playback |
| 20260919 | vmess | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E2 | M2-M4 | youtube.com::video_playback |
| 20260920 | anytls | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 3 | 0 | E2 | M2-M4 | developer.mozilla.org::document_view |
| 20260920 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 2 | 0 | E2 | M2-M4 | developer.mozilla.org::document_view |
| 20260920 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 0 | E2 | M2-M4 | developer.mozilla.org::document_view |
| 20260920 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 2 | 0 | E2 | M2-M4 | developer.mozilla.org::document_view |
| 20260920 | anytls | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 0 | 0 | E2 | M2-M4 | developer.mozilla.org::document_view |
| 20260920 | anytls | https://en.wikipedia.org/wiki/Computer_network | 3 | 1 | 0 | E2 | M2-M4 | wikipedia.org::article_view |
| 20260920 | anytls | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 1 | E2 | M2-M4 | wikipedia.org::article_view |
| 20260920 | anytls | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 0 | 2 | E2 | M2-M4 | wikipedia.org::article_view |
| 20260920 | anytls | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 0 | E2 | M2-M4 | wikipedia.org::article_view |
| 20260920 | anytls | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E2 | M2-M4 | wikipedia.org::article_view |
| 20260920 | anytls | https://github.com/RakuLomis/TrafficTracer | 2 | 0 | 0 | E2 | M2-M4 | github.com::repository_view |
| 20260920 | anytls | https://github.com/numpy/numpy | 2 | 0 | 0 | E2 | M2-M4 | github.com::repository_view |
| 20260920 | anytls | https://github.com/pallets/flask | 2 | 0 | 0 | E2 | M2-M4 | github.com::repository_view |
| 20260920 | anytls | https://github.com/python/cpython | 2 | 1 | 0 | E2 | M2-M4 | github.com::repository_view |
| 20260920 | anytls | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E2 | M2-M4 | github.com::repository_view |
| 20260920 | anytls | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 0 | E2 | M2-M4 | bing.com::search_results_view |
| 20260920 | anytls | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 1 | E2 | M2-M4 | bing.com::search_results_view |
| 20260920 | anytls | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E2 | M2-M4 | bing.com::search_results_view |
| 20260920 | anytls | https://www.bing.com/search?q=solar+system+facts | 0 | 0 | 0 | E2 | M2-M4 | bing.com::search_results_view |
| 20260920 | anytls | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 1 | 0 | E2 | M2-M4 | bing.com::search_results_view |
| 20260920 | anytls | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 2 | 0 | E2 | M2-M4 | youtube.com::search_results_view |
| 20260920 | anytls | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 1 | 0 | E2 | M2-M4 | youtube.com::search_results_view |
| 20260920 | anytls | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E2 | M2-M4 | youtube.com::search_results_view |
| 20260920 | anytls | https://www.youtube.com/results?search_query=piano+practice | 4 | 1 | 0 | E2 | M2-M4 | youtube.com::search_results_view |
| 20260920 | anytls | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E2 | M2-M4 | youtube.com::search_results_view |
| 20260920 | anytls | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E2 | M2-M4 | youtube.com::video_playback |
| 20260920 | anytls | youtube_video:aircAruvnKk | 5 | 0 | 0 | E2 | M2-M4 | youtube.com::video_playback |
| 20260920 | anytls | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E2 | M2-M4 | youtube.com::video_playback |
| 20260920 | anytls | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E2 | M2-M4 | youtube.com::video_playback |
| 20260920 | anytls | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E2 | M2-M4 | youtube.com::video_playback |
| 20260920 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 1 | E2 | M2-M4 | developer.mozilla.org::document_view |
| 20260920 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 0 | 3 | E2 | M2-M4 | developer.mozilla.org::document_view |
| 20260920 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 0 | E2 | M2-M4 | developer.mozilla.org::document_view |
| 20260920 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 0 | 1 | E2 | M2-M4 | developer.mozilla.org::document_view |
| 20260920 | shadowsocks | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 0 | 0 | E2 | M2-M4 | developer.mozilla.org::document_view |
| 20260920 | shadowsocks | https://en.wikipedia.org/wiki/Computer_network | 3 | 0 | 0 | E2 | M2-M4 | wikipedia.org::article_view |
| 20260920 | shadowsocks | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 0 | E2 | M2-M4 | wikipedia.org::article_view |
| 20260920 | shadowsocks | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 0 | 0 | E2 | M2-M4 | wikipedia.org::article_view |
| 20260920 | shadowsocks | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 0 | E2 | M2-M4 | wikipedia.org::article_view |
| 20260920 | shadowsocks | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E2 | M2-M4 | wikipedia.org::article_view |
| 20260920 | shadowsocks | https://github.com/RakuLomis/TrafficTracer | 2 | 0 | 0 | E2 | M2-M4 | github.com::repository_view |
| 20260920 | shadowsocks | https://github.com/numpy/numpy | 2 | 0 | 0 | E2 | M2-M4 | github.com::repository_view |
| 20260920 | shadowsocks | https://github.com/pallets/flask | 2 | 0 | 0 | E2 | M2-M4 | github.com::repository_view |
| 20260920 | shadowsocks | https://github.com/python/cpython | 2 | 0 | 0 | E2 | M2-M4 | github.com::repository_view |
| 20260920 | shadowsocks | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E2 | M2-M4 | github.com::repository_view |
| 20260920 | shadowsocks | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 4 | E2 | M2-M4 | bing.com::search_results_view |
| 20260920 | shadowsocks | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 1 | E2 | M2-M4 | bing.com::search_results_view |
| 20260920 | shadowsocks | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 1 | E2 | M2-M4 | bing.com::search_results_view |
| 20260920 | shadowsocks | https://www.bing.com/search?q=solar+system+facts | 0 | 0 | 0 | E2 | M2-M4 | bing.com::search_results_view |
| 20260920 | shadowsocks | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 1 | 1 | E2 | M2-M4 | bing.com::search_results_view |
| 20260920 | shadowsocks | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E2 | M2-M4 | youtube.com::search_results_view |
| 20260920 | shadowsocks | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 0 | E2 | M2-M4 | youtube.com::search_results_view |
| 20260920 | shadowsocks | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E2 | M2-M4 | youtube.com::search_results_view |
| 20260920 | shadowsocks | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 1 | E2 | M2-M4 | youtube.com::search_results_view |
| 20260920 | shadowsocks | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E2 | M2-M4 | youtube.com::search_results_view |
| 20260920 | shadowsocks | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E2 | M2-M4 | youtube.com::video_playback |
| 20260920 | shadowsocks | youtube_video:aircAruvnKk | 5 | 0 | 0 | E2 | M2-M4 | youtube.com::video_playback |
| 20260920 | shadowsocks | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E2 | M2-M4 | youtube.com::video_playback |
| 20260920 | shadowsocks | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E2 | M2-M4 | youtube.com::video_playback |
| 20260920 | shadowsocks | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E2 | M2-M4 | youtube.com::video_playback |
| 20260920 | trojan | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 2 | 0 | E2 | M2-M4 | developer.mozilla.org::document_view |
| 20260920 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 3 | 0 | E2 | M2-M4 | developer.mozilla.org::document_view |
| 20260920 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 1 | E2 | M2-M4 | developer.mozilla.org::document_view |
| 20260920 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 0 | 1 | E2 | M2-M4 | developer.mozilla.org::document_view |
| 20260920 | trojan | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 1 | 0 | E2 | M2-M4 | developer.mozilla.org::document_view |
| 20260920 | trojan | https://en.wikipedia.org/wiki/Computer_network | 3 | 1 | 0 | E2 | M2-M4 | wikipedia.org::article_view |
| 20260920 | trojan | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 1 | 0 | E2 | M2-M4 | wikipedia.org::article_view |
| 20260920 | trojan | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 0 | 1 | E2 | M2-M4 | wikipedia.org::article_view |
| 20260920 | trojan | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 1 | 0 | E2 | M2-M4 | wikipedia.org::article_view |
| 20260920 | trojan | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E2 | M2-M4 | wikipedia.org::article_view |
| 20260920 | trojan | https://github.com/RakuLomis/TrafficTracer | 2 | 3 | 0 | E2 | M2-M4 | github.com::repository_view |
| 20260920 | trojan | https://github.com/numpy/numpy | 2 | 0 | 0 | E2 | M2-M4 | github.com::repository_view |
| 20260920 | trojan | https://github.com/pallets/flask | 2 | 1 | 0 | E2 | M2-M4 | github.com::repository_view |
| 20260920 | trojan | https://github.com/python/cpython | 2 | 3 | 0 | E2 | M2-M4 | github.com::repository_view |
| 20260920 | trojan | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E2 | M2-M4 | github.com::repository_view |
| 20260920 | trojan | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 0 | E2 | M2-M4 | bing.com::search_results_view |
| 20260920 | trojan | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 0 | E2 | M2-M4 | bing.com::search_results_view |
| 20260920 | trojan | https://www.bing.com/search?q=network+traffic+analysis | 0 | 1 | 0 | E2 | M2-M4 | bing.com::search_results_view |
| 20260920 | trojan | https://www.bing.com/search?q=solar+system+facts | 0 | 1 | 0 | E2 | M2-M4 | bing.com::search_results_view |
| 20260920 | trojan | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 1 | 0 | E2 | M2-M4 | bing.com::search_results_view |
| 20260920 | trojan | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 2 | 0 | E2 | M2-M4 | youtube.com::search_results_view |
| 20260920 | trojan | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 0 | E2 | M2-M4 | youtube.com::search_results_view |
| 20260920 | trojan | https://www.youtube.com/results?search_query=bread+baking | 4 | 1 | 0 | E2 | M2-M4 | youtube.com::search_results_view |
| 20260920 | trojan | https://www.youtube.com/results?search_query=piano+practice | 4 | 0 | 0 | E2 | M2-M4 | youtube.com::search_results_view |
| 20260920 | trojan | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 0 | E2 | M2-M4 | youtube.com::search_results_view |
| 20260920 | trojan | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E2 | M2-M4 | youtube.com::video_playback |
| 20260920 | trojan | youtube_video:aircAruvnKk | 5 | 0 | 0 | E2 | M2-M4 | youtube.com::video_playback |
| 20260920 | trojan | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E2 | M2-M4 | youtube.com::video_playback |
| 20260920 | trojan | youtube_video:eRsGyueVLvQ | 5 | 0 | 1 | E2 | M2-M4 | youtube.com::video_playback |
| 20260920 | trojan | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E2 | M2-M4 | youtube.com::video_playback |
| 20260920 | vless | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 3 | 0 | E2 | M2-M4 | developer.mozilla.org::document_view |
| 20260920 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 0 | 0 | E2 | M2-M4 | developer.mozilla.org::document_view |
| 20260920 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 0 | E2 | M2-M4 | developer.mozilla.org::document_view |
| 20260920 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 2 | 0 | E2 | M2-M4 | developer.mozilla.org::document_view |
| 20260920 | vless | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 2 | 0 | E2 | M2-M4 | developer.mozilla.org::document_view |
| 20260920 | vless | https://en.wikipedia.org/wiki/Computer_network | 3 | 0 | 1 | E2 | M2-M4 | wikipedia.org::article_view |
| 20260920 | vless | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 1 | E2 | M2-M4 | wikipedia.org::article_view |
| 20260920 | vless | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 0 | 1 | E2 | M2-M4 | wikipedia.org::article_view |
| 20260920 | vless | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 2 | E2 | M2-M4 | wikipedia.org::article_view |
| 20260920 | vless | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E2 | M2-M4 | wikipedia.org::article_view |
| 20260920 | vless | https://github.com/RakuLomis/TrafficTracer | 2 | 1 | 0 | E2 | M2-M4 | github.com::repository_view |
| 20260920 | vless | https://github.com/numpy/numpy | 2 | 0 | 0 | E2 | M2-M4 | github.com::repository_view |
| 20260920 | vless | https://github.com/pallets/flask | 2 | 0 | 0 | E2 | M2-M4 | github.com::repository_view |
| 20260920 | vless | https://github.com/python/cpython | 2 | 1 | 0 | E2 | M2-M4 | github.com::repository_view |
| 20260920 | vless | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E2 | M2-M4 | github.com::repository_view |
| 20260920 | vless | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 0 | 0 | E2 | M2-M4 | bing.com::search_results_view |
| 20260920 | vless | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 1 | E2 | M2-M4 | bing.com::search_results_view |
| 20260920 | vless | https://www.bing.com/search?q=network+traffic+analysis | 0 | 1 | 0 | E2 | M2-M4 | bing.com::search_results_view |
| 20260920 | vless | https://www.bing.com/search?q=solar+system+facts | 0 | 2 | 0 | E2 | M2-M4 | bing.com::search_results_view |
| 20260920 | vless | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 1 | 0 | E2 | M2-M4 | bing.com::search_results_view |
| 20260920 | vless | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E2 | M2-M4 | youtube.com::search_results_view |
| 20260920 | vless | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 0 | 0 | E2 | M2-M4 | youtube.com::search_results_view |
| 20260920 | vless | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E2 | M2-M4 | youtube.com::search_results_view |
| 20260920 | vless | https://www.youtube.com/results?search_query=piano+practice | 4 | 1 | 0 | E2 | M2-M4 | youtube.com::search_results_view |
| 20260920 | vless | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 0 | 1 | E2 | M2-M4 | youtube.com::search_results_view |
| 20260920 | vless | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E2 | M2-M4 | youtube.com::video_playback |
| 20260920 | vless | youtube_video:aircAruvnKk | 5 | 0 | 0 | E2 | M2-M4 | youtube.com::video_playback |
| 20260920 | vless | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E2 | M2-M4 | youtube.com::video_playback |
| 20260920 | vless | youtube_video:eRsGyueVLvQ | 5 | 0 | 1 | E2 | M2-M4 | youtube.com::video_playback |
| 20260920 | vless | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E2 | M2-M4 | youtube.com::video_playback |
| 20260920 | vmess | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | 1 | 0 | 0 | E2 | M2-M4 | developer.mozilla.org::document_view |
| 20260920 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP | 1 | 0 | 0 | E2 | M2-M4 | developer.mozilla.org::document_view |
| 20260920 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | 1 | 0 | 0 | E2 | M2-M4 | developer.mozilla.org::document_view |
| 20260920 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | 1 | 0 | 0 | E2 | M2-M4 | developer.mozilla.org::document_view |
| 20260920 | vmess | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 1 | 1 | 0 | E2 | M2-M4 | developer.mozilla.org::document_view |
| 20260920 | vmess | https://en.wikipedia.org/wiki/Computer_network | 3 | 1 | 0 | E2 | M2-M4 | wikipedia.org::article_view |
| 20260920 | vmess | https://en.wikipedia.org/wiki/Domain_Name_System | 3 | 0 | 0 | E2 | M2-M4 | wikipedia.org::article_view |
| 20260920 | vmess | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | 3 | 1 | 0 | E2 | M2-M4 | wikipedia.org::article_view |
| 20260920 | vmess | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | 3 | 0 | 0 | E2 | M2-M4 | wikipedia.org::article_view |
| 20260920 | vmess | https://en.wikipedia.org/wiki/Transport_Layer_Security | 3 | 0 | 0 | E2 | M2-M4 | wikipedia.org::article_view |
| 20260920 | vmess | https://github.com/RakuLomis/TrafficTracer | 2 | 1 | 0 | E2 | M2-M4 | github.com::repository_view |
| 20260920 | vmess | https://github.com/numpy/numpy | 2 | 0 | 0 | E2 | M2-M4 | github.com::repository_view |
| 20260920 | vmess | https://github.com/pallets/flask | 2 | 0 | 1 | E2 | M2-M4 | github.com::repository_view |
| 20260920 | vmess | https://github.com/python/cpython | 2 | 0 | 0 | E2 | M2-M4 | github.com::repository_view |
| 20260920 | vmess | https://github.com/scikit-learn/scikit-learn | 2 | 0 | 0 | E2 | M2-M4 | github.com::repository_view |
| 20260920 | vmess | https://www.bing.com/search?q=beginner+guitar+chords | 0 | 2 | 0 | E2 | M2-M4 | bing.com::search_results_view |
| 20260920 | vmess | https://www.bing.com/search?q=indoor+plant+care | 0 | 0 | 0 | E2 | M2-M4 | bing.com::search_results_view |
| 20260920 | vmess | https://www.bing.com/search?q=network+traffic+analysis | 0 | 0 | 0 | E2 | M2-M4 | bing.com::search_results_view |
| 20260920 | vmess | https://www.bing.com/search?q=solar+system+facts | 0 | 0 | 0 | E2 | M2-M4 | bing.com::search_results_view |
| 20260920 | vmess | https://www.bing.com/search?q=sourdough+bread+recipe | 0 | 0 | 0 | E2 | M2-M4 | bing.com::search_results_view |
| 20260920 | vmess | https://www.youtube.com/results?search_query=astronomy+documentary | 4 | 0 | 0 | E2 | M2-M4 | youtube.com::search_results_view |
| 20260920 | vmess | https://www.youtube.com/results?search_query=bicycle+maintenance | 4 | 1 | 0 | E2 | M2-M4 | youtube.com::search_results_view |
| 20260920 | vmess | https://www.youtube.com/results?search_query=bread+baking | 4 | 0 | 0 | E2 | M2-M4 | youtube.com::search_results_view |
| 20260920 | vmess | https://www.youtube.com/results?search_query=piano+practice | 4 | 1 | 1 | E2 | M2-M4 | youtube.com::search_results_view |
| 20260920 | vmess | https://www.youtube.com/results?search_query=watercolor+tutorial | 4 | 1 | 0 | E2 | M2-M4 | youtube.com::search_results_view |
| 20260920 | vmess | youtube_video:R6MlUcmOul8 | 5 | 0 | 0 | E2 | M2-M4 | youtube.com::video_playback |
| 20260920 | vmess | youtube_video:aircAruvnKk | 5 | 0 | 1 | E2 | M2-M4 | youtube.com::video_playback |
| 20260920 | vmess | youtube_video:aqz-KE-bpKQ | 5 | 0 | 0 | E2 | M2-M4 | youtube.com::video_playback |
| 20260920 | vmess | youtube_video:eRsGyueVLvQ | 5 | 0 | 0 | E2 | M2-M4 | youtube.com::video_playback |
| 20260920 | vmess | youtube_video:sAWK0mgrMp4 | 5 | 0 | 0 | E2 | M2-M4 | youtube.com::video_playback |

这部分列出所有比较，不筛选有利内容。四重复×三seed的判断不能视为十二个独立内容。
