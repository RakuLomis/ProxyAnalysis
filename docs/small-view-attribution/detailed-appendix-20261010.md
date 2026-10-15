# 小比例收益归因详细附录

## 逐类别结果

| arm | target | group | label | label_index | F1 | uncovered | support | TP | FP | FN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| G-small | shadowsocks | G0 | bing.com::search_results_view | 0 | 0.810811 | False | 20 | 15 | 2 | 5 |
| G-small | shadowsocks | G0 | developer.mozilla.org::document_view | 1 | 0.780488 | False | 20 | 16 | 5 | 4 |
| G-small | shadowsocks | G0 | github.com::repository_view | 2 | 0.823529 | True | 20 | 14 | 0 | 6 |
| G-small | shadowsocks | G0 | wikipedia.org::article_view | 3 | 0.789474 | False | 20 | 15 | 3 | 5 |
| G-small | shadowsocks | G0 | youtube.com::search_results_view | 4 | 0.850000 | True | 20 | 17 | 3 | 3 |
| G-small | shadowsocks | G0 | youtube.com::video_playback | 5 | 0.760000 | False | 20 | 19 | 11 | 1 |
| G-small | shadowsocks | G1 | bing.com::search_results_view | 0 | 0.722222 | True | 20 | 13 | 3 | 7 |
| G-small | shadowsocks | G1 | developer.mozilla.org::document_view | 1 | 0.680851 | False | 20 | 16 | 11 | 4 |
| G-small | shadowsocks | G1 | github.com::repository_view | 2 | 0.842105 | False | 20 | 16 | 2 | 4 |
| G-small | shadowsocks | G1 | wikipedia.org::article_view | 3 | 0.687500 | True | 20 | 11 | 1 | 9 |
| G-small | shadowsocks | G1 | youtube.com::search_results_view | 4 | 0.820513 | False | 20 | 16 | 3 | 4 |
| G-small | shadowsocks | G1 | youtube.com::video_playback | 5 | 0.833333 | False | 20 | 20 | 8 | 0 |
| G-small | shadowsocks | G2 | bing.com::search_results_view | 0 | 0.711111 | False | 20 | 16 | 9 | 4 |
| G-small | shadowsocks | G2 | developer.mozilla.org::document_view | 1 | 0.400000 | True | 20 | 6 | 4 | 14 |
| G-small | shadowsocks | G2 | github.com::repository_view | 2 | 0.894737 | False | 20 | 17 | 1 | 3 |
| G-small | shadowsocks | G2 | wikipedia.org::article_view | 3 | 0.705882 | False | 20 | 18 | 13 | 2 |
| G-small | shadowsocks | G2 | youtube.com::search_results_view | 4 | 0.820513 | False | 20 | 16 | 3 | 4 |
| G-small | shadowsocks | G2 | youtube.com::video_playback | 5 | 0.810811 | True | 20 | 15 | 2 | 5 |
| G-small | trojan | G0 | bing.com::search_results_view | 0 | 0.829268 | False | 20 | 17 | 4 | 3 |
| G-small | trojan | G0 | developer.mozilla.org::document_view | 1 | 0.820513 | False | 20 | 16 | 3 | 4 |
| G-small | trojan | G0 | github.com::repository_view | 2 | 0.975610 | True | 20 | 20 | 1 | 0 |
| G-small | trojan | G0 | wikipedia.org::article_view | 3 | 0.842105 | False | 20 | 16 | 2 | 4 |
| G-small | trojan | G0 | youtube.com::search_results_view | 4 | 0.850000 | True | 20 | 17 | 3 | 3 |
| G-small | trojan | G0 | youtube.com::video_playback | 5 | 0.829268 | False | 20 | 17 | 4 | 3 |
| G-small | trojan | G1 | bing.com::search_results_view | 0 | 0.871795 | True | 20 | 17 | 2 | 3 |
| G-small | trojan | G1 | developer.mozilla.org::document_view | 1 | 0.809524 | False | 20 | 17 | 5 | 3 |
| G-small | trojan | G1 | github.com::repository_view | 2 | 1.000000 | False | 20 | 20 | 0 | 0 |
| G-small | trojan | G1 | wikipedia.org::article_view | 3 | 0.923077 | True | 20 | 18 | 1 | 2 |
| G-small | trojan | G1 | youtube.com::search_results_view | 4 | 0.842105 | False | 20 | 16 | 2 | 4 |
| G-small | trojan | G1 | youtube.com::video_playback | 5 | 0.857143 | False | 20 | 18 | 4 | 2 |
| G-small | trojan | G2 | bing.com::search_results_view | 0 | 0.871795 | False | 20 | 17 | 2 | 3 |
| G-small | trojan | G2 | developer.mozilla.org::document_view | 1 | 0.789474 | True | 20 | 15 | 3 | 5 |
| G-small | trojan | G2 | github.com::repository_view | 2 | 0.975610 | False | 20 | 20 | 1 | 0 |
| G-small | trojan | G2 | wikipedia.org::article_view | 3 | 0.800000 | False | 20 | 16 | 4 | 4 |
| G-small | trojan | G2 | youtube.com::search_results_view | 4 | 0.883721 | False | 20 | 19 | 4 | 1 |
| G-small | trojan | G2 | youtube.com::video_playback | 5 | 0.820513 | True | 20 | 16 | 3 | 4 |
| G-small | vless | G0 | bing.com::search_results_view | 0 | 0.900000 | False | 20 | 18 | 2 | 2 |
| G-small | vless | G0 | developer.mozilla.org::document_view | 1 | 0.820513 | False | 20 | 16 | 3 | 4 |
| G-small | vless | G0 | github.com::repository_view | 2 | 0.871795 | True | 20 | 17 | 2 | 3 |
| G-small | vless | G0 | wikipedia.org::article_view | 3 | 0.666667 | False | 20 | 14 | 8 | 6 |
| G-small | vless | G0 | youtube.com::search_results_view | 4 | 0.810811 | True | 20 | 15 | 2 | 5 |
| G-small | vless | G0 | youtube.com::video_playback | 5 | 0.837209 | False | 20 | 18 | 5 | 2 |
| G-small | vless | G1 | bing.com::search_results_view | 0 | 0.878049 | True | 20 | 18 | 3 | 2 |
| G-small | vless | G1 | developer.mozilla.org::document_view | 1 | 0.800000 | False | 20 | 16 | 4 | 4 |
| G-small | vless | G1 | github.com::repository_view | 2 | 0.900000 | False | 20 | 18 | 2 | 2 |
| G-small | vless | G1 | wikipedia.org::article_view | 3 | 0.684211 | True | 20 | 13 | 5 | 7 |
| G-small | vless | G1 | youtube.com::search_results_view | 4 | 0.780488 | False | 20 | 16 | 5 | 4 |
| G-small | vless | G1 | youtube.com::video_playback | 5 | 0.900000 | False | 20 | 18 | 2 | 2 |
| G-small | vless | G2 | bing.com::search_results_view | 0 | 0.950000 | False | 20 | 19 | 1 | 1 |
| G-small | vless | G2 | developer.mozilla.org::document_view | 1 | 0.789474 | True | 20 | 15 | 3 | 5 |
| G-small | vless | G2 | github.com::repository_view | 2 | 0.894737 | False | 20 | 17 | 1 | 3 |
| G-small | vless | G2 | wikipedia.org::article_view | 3 | 0.636364 | False | 20 | 14 | 10 | 6 |
| G-small | vless | G2 | youtube.com::search_results_view | 4 | 0.717949 | False | 20 | 14 | 5 | 6 |
| G-small | vless | G2 | youtube.com::video_playback | 5 | 0.878049 | True | 20 | 18 | 3 | 2 |
| G-small | vmess | G0 | bing.com::search_results_view | 0 | 0.769231 | False | 20 | 15 | 4 | 5 |
| G-small | vmess | G0 | developer.mozilla.org::document_view | 1 | 0.682927 | False | 20 | 14 | 7 | 6 |
| G-small | vmess | G0 | github.com::repository_view | 2 | 0.864865 | True | 20 | 16 | 1 | 4 |
| G-small | vmess | G0 | wikipedia.org::article_view | 3 | 0.714286 | False | 20 | 15 | 7 | 5 |
| G-small | vmess | G0 | youtube.com::search_results_view | 4 | 0.878049 | True | 20 | 18 | 3 | 2 |
| G-small | vmess | G0 | youtube.com::video_playback | 5 | 0.950000 | False | 20 | 19 | 1 | 1 |
| G-small | vmess | G1 | bing.com::search_results_view | 0 | 0.780488 | True | 20 | 16 | 5 | 4 |
| G-small | vmess | G1 | developer.mozilla.org::document_view | 1 | 0.717949 | False | 20 | 14 | 5 | 6 |
| G-small | vmess | G1 | github.com::repository_view | 2 | 0.950000 | False | 20 | 19 | 1 | 1 |
| G-small | vmess | G1 | wikipedia.org::article_view | 3 | 0.756757 | True | 20 | 14 | 3 | 6 |
| G-small | vmess | G1 | youtube.com::search_results_view | 4 | 0.909091 | False | 20 | 20 | 4 | 0 |
| G-small | vmess | G1 | youtube.com::video_playback | 5 | 0.974359 | False | 20 | 19 | 0 | 1 |
| G-small | vmess | G2 | bing.com::search_results_view | 0 | 0.731707 | False | 20 | 15 | 6 | 5 |
| G-small | vmess | G2 | developer.mozilla.org::document_view | 1 | 0.413793 | True | 20 | 6 | 3 | 14 |
| G-small | vmess | G2 | github.com::repository_view | 2 | 0.883721 | False | 20 | 19 | 4 | 1 |
| G-small | vmess | G2 | wikipedia.org::article_view | 3 | 0.695652 | False | 20 | 16 | 10 | 4 |
| G-small | vmess | G2 | youtube.com::search_results_view | 4 | 0.883721 | False | 20 | 19 | 4 | 1 |
| G-small | vmess | G2 | youtube.com::video_playback | 5 | 0.947368 | True | 20 | 18 | 0 | 2 |
| Marginal-small | shadowsocks | G0 | bing.com::search_results_view | 0 | 0.842105 | False | 20 | 16 | 2 | 4 |
| Marginal-small | shadowsocks | G0 | developer.mozilla.org::document_view | 1 | 0.780488 | False | 20 | 16 | 5 | 4 |
| Marginal-small | shadowsocks | G0 | github.com::repository_view | 2 | 0.750000 | True | 20 | 12 | 0 | 8 |
| Marginal-small | shadowsocks | G0 | wikipedia.org::article_view | 3 | 0.769231 | False | 20 | 15 | 4 | 5 |
| Marginal-small | shadowsocks | G0 | youtube.com::search_results_view | 4 | 0.820513 | True | 20 | 16 | 3 | 4 |
| Marginal-small | shadowsocks | G0 | youtube.com::video_playback | 5 | 0.784314 | False | 20 | 20 | 11 | 0 |
| Marginal-small | shadowsocks | G1 | bing.com::search_results_view | 0 | 0.722222 | True | 20 | 13 | 3 | 7 |
| Marginal-small | shadowsocks | G1 | developer.mozilla.org::document_view | 1 | 0.695652 | False | 20 | 16 | 10 | 4 |
| Marginal-small | shadowsocks | G1 | github.com::repository_view | 2 | 0.820513 | False | 20 | 16 | 3 | 4 |
| Marginal-small | shadowsocks | G1 | wikipedia.org::article_view | 3 | 0.687500 | True | 20 | 11 | 1 | 9 |
| Marginal-small | shadowsocks | G1 | youtube.com::search_results_view | 4 | 0.850000 | False | 20 | 17 | 3 | 3 |
| Marginal-small | shadowsocks | G1 | youtube.com::video_playback | 5 | 0.851064 | False | 20 | 20 | 7 | 0 |
| Marginal-small | shadowsocks | G2 | bing.com::search_results_view | 0 | 0.651163 | False | 20 | 14 | 9 | 6 |
| Marginal-small | shadowsocks | G2 | developer.mozilla.org::document_view | 1 | 0.387097 | True | 20 | 6 | 5 | 14 |
| Marginal-small | shadowsocks | G2 | github.com::repository_view | 2 | 0.871795 | False | 20 | 17 | 2 | 3 |
| Marginal-small | shadowsocks | G2 | wikipedia.org::article_view | 3 | 0.653061 | False | 20 | 16 | 13 | 4 |
| Marginal-small | shadowsocks | G2 | youtube.com::search_results_view | 4 | 0.850000 | False | 20 | 17 | 3 | 3 |
| Marginal-small | shadowsocks | G2 | youtube.com::video_playback | 5 | 0.789474 | True | 20 | 15 | 3 | 5 |
| Marginal-small | trojan | G0 | bing.com::search_results_view | 0 | 0.878049 | False | 20 | 18 | 3 | 2 |
| Marginal-small | trojan | G0 | developer.mozilla.org::document_view | 1 | 0.789474 | False | 20 | 15 | 3 | 5 |
| Marginal-small | trojan | G0 | github.com::repository_view | 2 | 0.975610 | True | 20 | 20 | 1 | 0 |
| Marginal-small | trojan | G0 | wikipedia.org::article_view | 3 | 0.842105 | False | 20 | 16 | 2 | 4 |
| Marginal-small | trojan | G0 | youtube.com::search_results_view | 4 | 0.850000 | True | 20 | 17 | 3 | 3 |
| Marginal-small | trojan | G0 | youtube.com::video_playback | 5 | 0.857143 | False | 20 | 18 | 4 | 2 |
| Marginal-small | trojan | G1 | bing.com::search_results_view | 0 | 0.894737 | True | 20 | 17 | 1 | 3 |
| Marginal-small | trojan | G1 | developer.mozilla.org::document_view | 1 | 0.731707 | False | 20 | 15 | 6 | 5 |
| Marginal-small | trojan | G1 | github.com::repository_view | 2 | 1.000000 | False | 20 | 20 | 0 | 0 |
| Marginal-small | trojan | G1 | wikipedia.org::article_view | 3 | 0.800000 | True | 20 | 16 | 4 | 4 |
| Marginal-small | trojan | G1 | youtube.com::search_results_view | 4 | 0.871795 | False | 20 | 17 | 2 | 3 |
| Marginal-small | trojan | G1 | youtube.com::video_playback | 5 | 0.857143 | False | 20 | 18 | 4 | 2 |
| Marginal-small | trojan | G2 | bing.com::search_results_view | 0 | 0.900000 | False | 20 | 18 | 2 | 2 |
| Marginal-small | trojan | G2 | developer.mozilla.org::document_view | 1 | 0.756757 | True | 20 | 14 | 3 | 6 |
| Marginal-small | trojan | G2 | github.com::repository_view | 2 | 0.975610 | False | 20 | 20 | 1 | 0 |
| Marginal-small | trojan | G2 | wikipedia.org::article_view | 3 | 0.761905 | False | 20 | 16 | 6 | 4 |
| Marginal-small | trojan | G2 | youtube.com::search_results_view | 4 | 0.857143 | False | 20 | 18 | 4 | 2 |
| Marginal-small | trojan | G2 | youtube.com::video_playback | 5 | 0.842105 | True | 20 | 16 | 2 | 4 |
| Marginal-small | vless | G0 | bing.com::search_results_view | 0 | 0.878049 | False | 20 | 18 | 3 | 2 |
| Marginal-small | vless | G0 | developer.mozilla.org::document_view | 1 | 0.800000 | False | 20 | 16 | 4 | 4 |
| Marginal-small | vless | G0 | github.com::repository_view | 2 | 0.894737 | True | 20 | 17 | 1 | 3 |
| Marginal-small | vless | G0 | wikipedia.org::article_view | 3 | 0.761905 | False | 20 | 16 | 6 | 4 |
| Marginal-small | vless | G0 | youtube.com::search_results_view | 4 | 0.833333 | True | 20 | 15 | 1 | 5 |
| Marginal-small | vless | G0 | youtube.com::video_playback | 5 | 0.883721 | False | 20 | 19 | 4 | 1 |
| Marginal-small | vless | G1 | bing.com::search_results_view | 0 | 0.850000 | True | 20 | 17 | 3 | 3 |
| Marginal-small | vless | G1 | developer.mozilla.org::document_view | 1 | 0.750000 | False | 20 | 15 | 5 | 5 |
| Marginal-small | vless | G1 | github.com::repository_view | 2 | 0.900000 | False | 20 | 18 | 2 | 2 |
| Marginal-small | vless | G1 | wikipedia.org::article_view | 3 | 0.648649 | True | 20 | 12 | 5 | 8 |
| Marginal-small | vless | G1 | youtube.com::search_results_view | 4 | 0.744186 | False | 20 | 16 | 7 | 4 |
| Marginal-small | vless | G1 | youtube.com::video_playback | 5 | 0.900000 | False | 20 | 18 | 2 | 2 |
| Marginal-small | vless | G2 | bing.com::search_results_view | 0 | 0.950000 | False | 20 | 19 | 1 | 1 |
| Marginal-small | vless | G2 | developer.mozilla.org::document_view | 1 | 0.789474 | True | 20 | 15 | 3 | 5 |
| Marginal-small | vless | G2 | github.com::repository_view | 2 | 0.923077 | False | 20 | 18 | 1 | 2 |
| Marginal-small | vless | G2 | wikipedia.org::article_view | 3 | 0.636364 | False | 20 | 14 | 10 | 6 |
| Marginal-small | vless | G2 | youtube.com::search_results_view | 4 | 0.769231 | False | 20 | 15 | 4 | 5 |
| Marginal-small | vless | G2 | youtube.com::video_playback | 5 | 0.900000 | True | 20 | 18 | 2 | 2 |
| Marginal-small | vmess | G0 | bing.com::search_results_view | 0 | 0.750000 | False | 20 | 15 | 5 | 5 |
| Marginal-small | vmess | G0 | developer.mozilla.org::document_view | 1 | 0.619048 | False | 20 | 13 | 9 | 7 |
| Marginal-small | vmess | G0 | github.com::repository_view | 2 | 0.800000 | True | 20 | 14 | 1 | 6 |
| Marginal-small | vmess | G0 | wikipedia.org::article_view | 3 | 0.697674 | False | 20 | 15 | 8 | 5 |
| Marginal-small | vmess | G0 | youtube.com::search_results_view | 4 | 0.900000 | True | 20 | 18 | 2 | 2 |
| Marginal-small | vmess | G0 | youtube.com::video_playback | 5 | 0.950000 | False | 20 | 19 | 1 | 1 |
| Marginal-small | vmess | G1 | bing.com::search_results_view | 0 | 0.769231 | True | 20 | 15 | 4 | 5 |
| Marginal-small | vmess | G1 | developer.mozilla.org::document_view | 1 | 0.651163 | False | 20 | 14 | 9 | 6 |
| Marginal-small | vmess | G1 | github.com::repository_view | 2 | 0.926829 | False | 20 | 19 | 2 | 1 |
| Marginal-small | vmess | G1 | wikipedia.org::article_view | 3 | 0.705882 | True | 20 | 12 | 2 | 8 |
| Marginal-small | vmess | G1 | youtube.com::search_results_view | 4 | 0.883721 | False | 20 | 19 | 4 | 1 |
| Marginal-small | vmess | G1 | youtube.com::video_playback | 5 | 0.950000 | False | 20 | 19 | 1 | 1 |
| Marginal-small | vmess | G2 | bing.com::search_results_view | 0 | 0.731707 | False | 20 | 15 | 6 | 5 |
| Marginal-small | vmess | G2 | developer.mozilla.org::document_view | 1 | 0.333333 | True | 20 | 5 | 5 | 15 |
| Marginal-small | vmess | G2 | github.com::repository_view | 2 | 0.883721 | False | 20 | 19 | 4 | 1 |
| Marginal-small | vmess | G2 | wikipedia.org::article_view | 3 | 0.666667 | False | 20 | 15 | 10 | 5 |
| Marginal-small | vmess | G2 | youtube.com::search_results_view | 4 | 0.883721 | False | 20 | 19 | 4 | 1 |
| Marginal-small | vmess | G2 | youtube.com::video_playback | 5 | 0.947368 | True | 20 | 18 | 0 | 2 |
| P-small | shadowsocks | G0 | bing.com::search_results_view | 0 | 0.810811 | False | 20 | 15 | 2 | 5 |
| P-small | shadowsocks | G0 | developer.mozilla.org::document_view | 1 | 0.780488 | False | 20 | 16 | 5 | 4 |
| P-small | shadowsocks | G0 | github.com::repository_view | 2 | 0.857143 | True | 20 | 15 | 0 | 5 |
| P-small | shadowsocks | G0 | wikipedia.org::article_view | 3 | 0.789474 | False | 20 | 15 | 3 | 5 |
| P-small | shadowsocks | G0 | youtube.com::search_results_view | 4 | 0.850000 | True | 20 | 17 | 3 | 3 |
| P-small | shadowsocks | G0 | youtube.com::video_playback | 5 | 0.775510 | False | 20 | 19 | 10 | 1 |
| P-small | shadowsocks | G1 | bing.com::search_results_view | 0 | 0.722222 | True | 20 | 13 | 3 | 7 |
| P-small | shadowsocks | G1 | developer.mozilla.org::document_view | 1 | 0.680851 | False | 20 | 16 | 11 | 4 |
| P-small | shadowsocks | G1 | github.com::repository_view | 2 | 0.842105 | False | 20 | 16 | 2 | 4 |
| P-small | shadowsocks | G1 | wikipedia.org::article_view | 3 | 0.645161 | True | 20 | 10 | 1 | 10 |
| P-small | shadowsocks | G1 | youtube.com::search_results_view | 4 | 0.800000 | False | 20 | 16 | 4 | 4 |
| P-small | shadowsocks | G1 | youtube.com::video_playback | 5 | 0.833333 | False | 20 | 20 | 8 | 0 |
| P-small | shadowsocks | G2 | bing.com::search_results_view | 0 | 0.739130 | False | 20 | 17 | 9 | 3 |
| P-small | shadowsocks | G2 | developer.mozilla.org::document_view | 1 | 0.413793 | True | 20 | 6 | 3 | 14 |
| P-small | shadowsocks | G2 | github.com::repository_view | 2 | 0.894737 | False | 20 | 17 | 1 | 3 |
| P-small | shadowsocks | G2 | wikipedia.org::article_view | 3 | 0.705882 | False | 20 | 18 | 13 | 2 |
| P-small | shadowsocks | G2 | youtube.com::search_results_view | 4 | 0.820513 | False | 20 | 16 | 3 | 4 |
| P-small | shadowsocks | G2 | youtube.com::video_playback | 5 | 0.810811 | True | 20 | 15 | 2 | 5 |
| P-small | trojan | G0 | bing.com::search_results_view | 0 | 0.871795 | False | 20 | 17 | 2 | 3 |
| P-small | trojan | G0 | developer.mozilla.org::document_view | 1 | 0.850000 | False | 20 | 17 | 3 | 3 |
| P-small | trojan | G0 | github.com::repository_view | 2 | 0.975610 | True | 20 | 20 | 1 | 0 |
| P-small | trojan | G0 | wikipedia.org::article_view | 3 | 0.842105 | False | 20 | 16 | 2 | 4 |
| P-small | trojan | G0 | youtube.com::search_results_view | 4 | 0.850000 | True | 20 | 17 | 3 | 3 |
| P-small | trojan | G0 | youtube.com::video_playback | 5 | 0.857143 | False | 20 | 18 | 4 | 2 |
| P-small | trojan | G1 | bing.com::search_results_view | 0 | 0.871795 | True | 20 | 17 | 2 | 3 |
| P-small | trojan | G1 | developer.mozilla.org::document_view | 1 | 0.829268 | False | 20 | 17 | 4 | 3 |
| P-small | trojan | G1 | github.com::repository_view | 2 | 1.000000 | False | 20 | 20 | 0 | 0 |
| P-small | trojan | G1 | wikipedia.org::article_view | 3 | 0.923077 | True | 20 | 18 | 1 | 2 |
| P-small | trojan | G1 | youtube.com::search_results_view | 4 | 0.871795 | False | 20 | 17 | 2 | 3 |
| P-small | trojan | G1 | youtube.com::video_playback | 5 | 0.857143 | False | 20 | 18 | 4 | 2 |
| P-small | trojan | G2 | bing.com::search_results_view | 0 | 0.871795 | False | 20 | 17 | 2 | 3 |
| P-small | trojan | G2 | developer.mozilla.org::document_view | 1 | 0.789474 | True | 20 | 15 | 3 | 5 |
| P-small | trojan | G2 | github.com::repository_view | 2 | 0.975610 | False | 20 | 20 | 1 | 0 |
| P-small | trojan | G2 | wikipedia.org::article_view | 3 | 0.829268 | False | 20 | 17 | 4 | 3 |
| P-small | trojan | G2 | youtube.com::search_results_view | 4 | 0.883721 | False | 20 | 19 | 4 | 1 |
| P-small | trojan | G2 | youtube.com::video_playback | 5 | 0.842105 | True | 20 | 16 | 2 | 4 |
| P-small | vless | G0 | bing.com::search_results_view | 0 | 0.923077 | False | 20 | 18 | 1 | 2 |
| P-small | vless | G0 | developer.mozilla.org::document_view | 1 | 0.820513 | False | 20 | 16 | 3 | 4 |
| P-small | vless | G0 | github.com::repository_view | 2 | 0.894737 | True | 20 | 17 | 1 | 3 |
| P-small | vless | G0 | wikipedia.org::article_view | 3 | 0.681818 | False | 20 | 15 | 9 | 5 |
| P-small | vless | G0 | youtube.com::search_results_view | 4 | 0.810811 | True | 20 | 15 | 2 | 5 |
| P-small | vless | G0 | youtube.com::video_playback | 5 | 0.837209 | False | 20 | 18 | 5 | 2 |
| P-small | vless | G1 | bing.com::search_results_view | 0 | 0.850000 | True | 20 | 17 | 3 | 3 |
| P-small | vless | G1 | developer.mozilla.org::document_view | 1 | 0.780488 | False | 20 | 16 | 5 | 4 |
| P-small | vless | G1 | github.com::repository_view | 2 | 0.900000 | False | 20 | 18 | 2 | 2 |
| P-small | vless | G1 | wikipedia.org::article_view | 3 | 0.684211 | True | 20 | 13 | 5 | 7 |
| P-small | vless | G1 | youtube.com::search_results_view | 4 | 0.780488 | False | 20 | 16 | 5 | 4 |
| P-small | vless | G1 | youtube.com::video_playback | 5 | 0.900000 | False | 20 | 18 | 2 | 2 |
| P-small | vless | G2 | bing.com::search_results_view | 0 | 0.894737 | False | 20 | 17 | 1 | 3 |
| P-small | vless | G2 | developer.mozilla.org::document_view | 1 | 0.769231 | True | 20 | 15 | 4 | 5 |
| P-small | vless | G2 | github.com::repository_view | 2 | 0.894737 | False | 20 | 17 | 1 | 3 |
| P-small | vless | G2 | wikipedia.org::article_view | 3 | 0.666667 | False | 20 | 15 | 10 | 5 |
| P-small | vless | G2 | youtube.com::search_results_view | 4 | 0.717949 | False | 20 | 14 | 5 | 6 |
| P-small | vless | G2 | youtube.com::video_playback | 5 | 0.878049 | True | 20 | 18 | 3 | 2 |
| P-small | vmess | G0 | bing.com::search_results_view | 0 | 0.769231 | False | 20 | 15 | 4 | 5 |
| P-small | vmess | G0 | developer.mozilla.org::document_view | 1 | 0.682927 | False | 20 | 14 | 7 | 6 |
| P-small | vmess | G0 | github.com::repository_view | 2 | 0.864865 | True | 20 | 16 | 1 | 4 |
| P-small | vmess | G0 | wikipedia.org::article_view | 3 | 0.714286 | False | 20 | 15 | 7 | 5 |
| P-small | vmess | G0 | youtube.com::search_results_view | 4 | 0.878049 | True | 20 | 18 | 3 | 2 |
| P-small | vmess | G0 | youtube.com::video_playback | 5 | 0.950000 | False | 20 | 19 | 1 | 1 |
| P-small | vmess | G1 | bing.com::search_results_view | 0 | 0.789474 | True | 20 | 15 | 3 | 5 |
| P-small | vmess | G1 | developer.mozilla.org::document_view | 1 | 0.731707 | False | 20 | 15 | 6 | 5 |
| P-small | vmess | G1 | github.com::repository_view | 2 | 0.926829 | False | 20 | 19 | 2 | 1 |
| P-small | vmess | G1 | wikipedia.org::article_view | 3 | 0.756757 | True | 20 | 14 | 3 | 6 |
| P-small | vmess | G1 | youtube.com::search_results_view | 4 | 0.909091 | False | 20 | 20 | 4 | 0 |
| P-small | vmess | G1 | youtube.com::video_playback | 5 | 0.974359 | False | 20 | 19 | 0 | 1 |
| P-small | vmess | G2 | bing.com::search_results_view | 0 | 0.750000 | False | 20 | 15 | 5 | 5 |
| P-small | vmess | G2 | developer.mozilla.org::document_view | 1 | 0.451613 | True | 20 | 7 | 4 | 13 |
| P-small | vmess | G2 | github.com::repository_view | 2 | 0.904762 | False | 20 | 19 | 3 | 1 |
| P-small | vmess | G2 | wikipedia.org::article_view | 3 | 0.739130 | False | 20 | 17 | 9 | 3 |
| P-small | vmess | G2 | youtube.com::search_results_view | 4 | 0.883721 | False | 20 | 19 | 4 | 1 |
| P-small | vmess | G2 | youtube.com::video_playback | 5 | 0.947368 | True | 20 | 18 | 0 | 2 |
| RawPost-small | shadowsocks | G0 | bing.com::search_results_view | 0 | 0.789474 | False | 20 | 15 | 3 | 5 |
| RawPost-small | shadowsocks | G0 | developer.mozilla.org::document_view | 1 | 0.780488 | False | 20 | 16 | 5 | 4 |
| RawPost-small | shadowsocks | G0 | github.com::repository_view | 2 | 0.709677 | True | 20 | 11 | 0 | 9 |
| RawPost-small | shadowsocks | G0 | wikipedia.org::article_view | 3 | 0.850000 | False | 20 | 17 | 3 | 3 |
| RawPost-small | shadowsocks | G0 | youtube.com::search_results_view | 4 | 0.789474 | True | 20 | 15 | 3 | 5 |
| RawPost-small | shadowsocks | G0 | youtube.com::video_playback | 5 | 0.769231 | False | 20 | 20 | 12 | 0 |
| RawPost-small | shadowsocks | G1 | bing.com::search_results_view | 0 | 0.810811 | True | 20 | 15 | 2 | 5 |
| RawPost-small | shadowsocks | G1 | developer.mozilla.org::document_view | 1 | 0.739130 | False | 20 | 17 | 9 | 3 |
| RawPost-small | shadowsocks | G1 | github.com::repository_view | 2 | 0.888889 | False | 20 | 16 | 0 | 4 |
| RawPost-small | shadowsocks | G1 | wikipedia.org::article_view | 3 | 0.687500 | True | 20 | 11 | 1 | 9 |
| RawPost-small | shadowsocks | G1 | youtube.com::search_results_view | 4 | 0.857143 | False | 20 | 18 | 4 | 2 |
| RawPost-small | shadowsocks | G1 | youtube.com::video_playback | 5 | 0.808511 | False | 20 | 19 | 8 | 1 |
| RawPost-small | shadowsocks | G2 | bing.com::search_results_view | 0 | 0.755556 | False | 20 | 17 | 8 | 3 |
| RawPost-small | shadowsocks | G2 | developer.mozilla.org::document_view | 1 | 0.400000 | True | 20 | 6 | 4 | 14 |
| RawPost-small | shadowsocks | G2 | github.com::repository_view | 2 | 0.871795 | False | 20 | 17 | 2 | 3 |
| RawPost-small | shadowsocks | G2 | wikipedia.org::article_view | 3 | 0.641509 | False | 20 | 17 | 16 | 3 |
| RawPost-small | shadowsocks | G2 | youtube.com::search_results_view | 4 | 0.790698 | False | 20 | 17 | 6 | 3 |
| RawPost-small | shadowsocks | G2 | youtube.com::video_playback | 5 | 0.600000 | True | 20 | 9 | 1 | 11 |
| RawPost-small | trojan | G0 | bing.com::search_results_view | 0 | 0.850000 | False | 20 | 17 | 3 | 3 |
| RawPost-small | trojan | G0 | developer.mozilla.org::document_view | 1 | 0.820513 | False | 20 | 16 | 3 | 4 |
| RawPost-small | trojan | G0 | github.com::repository_view | 2 | 0.975610 | True | 20 | 20 | 1 | 0 |
| RawPost-small | trojan | G0 | wikipedia.org::article_view | 3 | 0.842105 | False | 20 | 16 | 2 | 4 |
| RawPost-small | trojan | G0 | youtube.com::search_results_view | 4 | 0.850000 | True | 20 | 17 | 3 | 3 |
| RawPost-small | trojan | G0 | youtube.com::video_playback | 5 | 0.857143 | False | 20 | 18 | 4 | 2 |
| RawPost-small | trojan | G1 | bing.com::search_results_view | 0 | 0.918919 | True | 20 | 17 | 0 | 3 |
| RawPost-small | trojan | G1 | developer.mozilla.org::document_view | 1 | 0.837209 | False | 20 | 18 | 5 | 2 |
| RawPost-small | trojan | G1 | github.com::repository_view | 2 | 1.000000 | False | 20 | 20 | 0 | 0 |
| RawPost-small | trojan | G1 | wikipedia.org::article_view | 3 | 0.871795 | True | 20 | 17 | 2 | 3 |
| RawPost-small | trojan | G1 | youtube.com::search_results_view | 4 | 0.820513 | False | 20 | 16 | 3 | 4 |
| RawPost-small | trojan | G1 | youtube.com::video_playback | 5 | 0.857143 | False | 20 | 18 | 4 | 2 |
| RawPost-small | trojan | G2 | bing.com::search_results_view | 0 | 0.878049 | False | 20 | 18 | 3 | 2 |
| RawPost-small | trojan | G2 | developer.mozilla.org::document_view | 1 | 0.756757 | True | 20 | 14 | 3 | 6 |
| RawPost-small | trojan | G2 | github.com::repository_view | 2 | 0.975610 | False | 20 | 20 | 1 | 0 |
| RawPost-small | trojan | G2 | wikipedia.org::article_view | 3 | 0.820513 | False | 20 | 16 | 3 | 4 |
| RawPost-small | trojan | G2 | youtube.com::search_results_view | 4 | 0.883721 | False | 20 | 19 | 4 | 1 |
| RawPost-small | trojan | G2 | youtube.com::video_playback | 5 | 0.820513 | True | 20 | 16 | 3 | 4 |
| RawPost-small | vless | G0 | bing.com::search_results_view | 0 | 0.923077 | False | 20 | 18 | 1 | 2 |
| RawPost-small | vless | G0 | developer.mozilla.org::document_view | 1 | 0.820513 | False | 20 | 16 | 3 | 4 |
| RawPost-small | vless | G0 | github.com::repository_view | 2 | 0.894737 | True | 20 | 17 | 1 | 3 |
| RawPost-small | vless | G0 | wikipedia.org::article_view | 3 | 0.681818 | False | 20 | 15 | 9 | 5 |
| RawPost-small | vless | G0 | youtube.com::search_results_view | 4 | 0.810811 | True | 20 | 15 | 2 | 5 |
| RawPost-small | vless | G0 | youtube.com::video_playback | 5 | 0.837209 | False | 20 | 18 | 5 | 2 |
| RawPost-small | vless | G1 | bing.com::search_results_view | 0 | 0.829268 | True | 20 | 17 | 4 | 3 |
| RawPost-small | vless | G1 | developer.mozilla.org::document_view | 1 | 0.750000 | False | 20 | 15 | 5 | 5 |
| RawPost-small | vless | G1 | github.com::repository_view | 2 | 0.923077 | False | 20 | 18 | 1 | 2 |
| RawPost-small | vless | G1 | wikipedia.org::article_view | 3 | 0.684211 | True | 20 | 13 | 5 | 7 |
| RawPost-small | vless | G1 | youtube.com::search_results_view | 4 | 0.731707 | False | 20 | 15 | 6 | 5 |
| RawPost-small | vless | G1 | youtube.com::video_playback | 5 | 0.878049 | False | 20 | 18 | 3 | 2 |
| RawPost-small | vless | G2 | bing.com::search_results_view | 0 | 0.904762 | False | 20 | 19 | 3 | 1 |
| RawPost-small | vless | G2 | developer.mozilla.org::document_view | 1 | 0.777778 | True | 20 | 14 | 2 | 6 |
| RawPost-small | vless | G2 | github.com::repository_view | 2 | 0.894737 | False | 20 | 17 | 1 | 3 |
| RawPost-small | vless | G2 | wikipedia.org::article_view | 3 | 0.666667 | False | 20 | 15 | 10 | 5 |
| RawPost-small | vless | G2 | youtube.com::search_results_view | 4 | 0.684211 | False | 20 | 13 | 5 | 7 |
| RawPost-small | vless | G2 | youtube.com::video_playback | 5 | 0.878049 | True | 20 | 18 | 3 | 2 |
| RawPost-small | vmess | G0 | bing.com::search_results_view | 0 | 0.769231 | False | 20 | 15 | 4 | 5 |
| RawPost-small | vmess | G0 | developer.mozilla.org::document_view | 1 | 0.585366 | False | 20 | 12 | 9 | 8 |
| RawPost-small | vmess | G0 | github.com::repository_view | 2 | 0.800000 | True | 20 | 14 | 1 | 6 |
| RawPost-small | vmess | G0 | wikipedia.org::article_view | 3 | 0.711111 | False | 20 | 16 | 9 | 4 |
| RawPost-small | vmess | G0 | youtube.com::search_results_view | 4 | 0.878049 | True | 20 | 18 | 3 | 2 |
| RawPost-small | vmess | G0 | youtube.com::video_playback | 5 | 0.974359 | False | 20 | 19 | 0 | 1 |
| RawPost-small | vmess | G1 | bing.com::search_results_view | 0 | 0.789474 | True | 20 | 15 | 3 | 5 |
| RawPost-small | vmess | G1 | developer.mozilla.org::document_view | 1 | 0.727273 | False | 20 | 16 | 8 | 4 |
| RawPost-small | vmess | G1 | github.com::repository_view | 2 | 0.926829 | False | 20 | 19 | 2 | 1 |
| RawPost-small | vmess | G1 | wikipedia.org::article_view | 3 | 0.764706 | True | 20 | 13 | 1 | 7 |
| RawPost-small | vmess | G1 | youtube.com::search_results_view | 4 | 0.909091 | False | 20 | 20 | 4 | 0 |
| RawPost-small | vmess | G1 | youtube.com::video_playback | 5 | 0.974359 | False | 20 | 19 | 0 | 1 |
| RawPost-small | vmess | G2 | bing.com::search_results_view | 0 | 0.731707 | False | 20 | 15 | 6 | 5 |
| RawPost-small | vmess | G2 | developer.mozilla.org::document_view | 1 | 0.344828 | True | 20 | 5 | 4 | 15 |
| RawPost-small | vmess | G2 | github.com::repository_view | 2 | 0.883721 | False | 20 | 19 | 4 | 1 |
| RawPost-small | vmess | G2 | wikipedia.org::article_view | 3 | 0.695652 | False | 20 | 16 | 10 | 4 |
| RawPost-small | vmess | G2 | youtube.com::search_results_view | 4 | 0.883721 | False | 20 | 19 | 4 | 1 |
| RawPost-small | vmess | G2 | youtube.com::video_playback | 5 | 0.947368 | True | 20 | 18 | 0 | 2 |
| RawPre-small | shadowsocks | G0 | bing.com::search_results_view | 0 | 0.789474 | False | 20 | 15 | 3 | 5 |
| RawPre-small | shadowsocks | G0 | developer.mozilla.org::document_view | 1 | 0.809524 | False | 20 | 17 | 5 | 3 |
| RawPre-small | shadowsocks | G0 | github.com::repository_view | 2 | 0.823529 | True | 20 | 14 | 0 | 6 |
| RawPre-small | shadowsocks | G0 | wikipedia.org::article_view | 3 | 0.777778 | False | 20 | 14 | 2 | 6 |
| RawPre-small | shadowsocks | G0 | youtube.com::search_results_view | 4 | 0.871795 | True | 20 | 17 | 2 | 3 |
| RawPre-small | shadowsocks | G0 | youtube.com::video_playback | 5 | 0.784314 | False | 20 | 20 | 11 | 0 |
| RawPre-small | shadowsocks | G1 | bing.com::search_results_view | 0 | 0.842105 | True | 20 | 16 | 2 | 4 |
| RawPre-small | shadowsocks | G1 | developer.mozilla.org::document_view | 1 | 0.765957 | False | 20 | 18 | 9 | 2 |
| RawPre-small | shadowsocks | G1 | github.com::repository_view | 2 | 0.871795 | False | 20 | 17 | 2 | 3 |
| RawPre-small | shadowsocks | G1 | wikipedia.org::article_view | 3 | 0.666667 | True | 20 | 11 | 2 | 9 |
| RawPre-small | shadowsocks | G1 | youtube.com::search_results_view | 4 | 0.894737 | False | 20 | 17 | 1 | 3 |
| RawPre-small | shadowsocks | G1 | youtube.com::video_playback | 5 | 0.844444 | False | 20 | 19 | 6 | 1 |
| RawPre-small | shadowsocks | G2 | bing.com::search_results_view | 0 | 0.739130 | False | 20 | 17 | 9 | 3 |
| RawPre-small | shadowsocks | G2 | developer.mozilla.org::document_view | 1 | 0.413793 | True | 20 | 6 | 3 | 14 |
| RawPre-small | shadowsocks | G2 | github.com::repository_view | 2 | 0.923077 | False | 20 | 18 | 1 | 2 |
| RawPre-small | shadowsocks | G2 | wikipedia.org::article_view | 3 | 0.705882 | False | 20 | 18 | 13 | 2 |
| RawPre-small | shadowsocks | G2 | youtube.com::search_results_view | 4 | 0.820513 | False | 20 | 16 | 3 | 4 |
| RawPre-small | shadowsocks | G2 | youtube.com::video_playback | 5 | 0.833333 | True | 20 | 15 | 1 | 5 |
| RawPre-small | trojan | G0 | bing.com::search_results_view | 0 | 0.850000 | False | 20 | 17 | 3 | 3 |
| RawPre-small | trojan | G0 | developer.mozilla.org::document_view | 1 | 0.820513 | False | 20 | 16 | 3 | 4 |
| RawPre-small | trojan | G0 | github.com::repository_view | 2 | 0.975610 | True | 20 | 20 | 1 | 0 |
| RawPre-small | trojan | G0 | wikipedia.org::article_view | 3 | 0.810811 | False | 20 | 15 | 2 | 5 |
| RawPre-small | trojan | G0 | youtube.com::search_results_view | 4 | 0.850000 | True | 20 | 17 | 3 | 3 |
| RawPre-small | trojan | G0 | youtube.com::video_playback | 5 | 0.837209 | False | 20 | 18 | 5 | 2 |
| RawPre-small | trojan | G1 | bing.com::search_results_view | 0 | 0.894737 | True | 20 | 17 | 1 | 3 |
| RawPre-small | trojan | G1 | developer.mozilla.org::document_view | 1 | 0.809524 | False | 20 | 17 | 5 | 3 |
| RawPre-small | trojan | G1 | github.com::repository_view | 2 | 0.952381 | False | 20 | 20 | 2 | 0 |
| RawPre-small | trojan | G1 | wikipedia.org::article_view | 3 | 0.842105 | True | 20 | 16 | 2 | 4 |
| RawPre-small | trojan | G1 | youtube.com::search_results_view | 4 | 0.871795 | False | 20 | 17 | 2 | 3 |
| RawPre-small | trojan | G1 | youtube.com::video_playback | 5 | 0.829268 | False | 20 | 17 | 4 | 3 |
| RawPre-small | trojan | G2 | bing.com::search_results_view | 0 | 0.878049 | False | 20 | 18 | 3 | 2 |
| RawPre-small | trojan | G2 | developer.mozilla.org::document_view | 1 | 0.810811 | True | 20 | 15 | 2 | 5 |
| RawPre-small | trojan | G2 | github.com::repository_view | 2 | 0.952381 | False | 20 | 20 | 2 | 0 |
| RawPre-small | trojan | G2 | wikipedia.org::article_view | 3 | 0.769231 | False | 20 | 15 | 4 | 5 |
| RawPre-small | trojan | G2 | youtube.com::search_results_view | 4 | 0.883721 | False | 20 | 19 | 4 | 1 |
| RawPre-small | trojan | G2 | youtube.com::video_playback | 5 | 0.789474 | True | 20 | 15 | 3 | 5 |
| RawPre-small | vless | G0 | bing.com::search_results_view | 0 | 0.900000 | False | 20 | 18 | 2 | 2 |
| RawPre-small | vless | G0 | developer.mozilla.org::document_view | 1 | 0.820513 | False | 20 | 16 | 3 | 4 |
| RawPre-small | vless | G0 | github.com::repository_view | 2 | 0.894737 | True | 20 | 17 | 1 | 3 |
| RawPre-small | vless | G0 | wikipedia.org::article_view | 3 | 0.714286 | False | 20 | 15 | 7 | 5 |
| RawPre-small | vless | G0 | youtube.com::search_results_view | 4 | 0.777778 | True | 20 | 14 | 2 | 6 |
| RawPre-small | vless | G0 | youtube.com::video_playback | 5 | 0.844444 | False | 20 | 19 | 6 | 1 |
| RawPre-small | vless | G1 | bing.com::search_results_view | 0 | 0.850000 | True | 20 | 17 | 3 | 3 |
| RawPre-small | vless | G1 | developer.mozilla.org::document_view | 1 | 0.750000 | False | 20 | 15 | 5 | 5 |
| RawPre-small | vless | G1 | github.com::repository_view | 2 | 0.900000 | False | 20 | 18 | 2 | 2 |
| RawPre-small | vless | G1 | wikipedia.org::article_view | 3 | 0.648649 | True | 20 | 12 | 5 | 8 |
| RawPre-small | vless | G1 | youtube.com::search_results_view | 4 | 0.714286 | False | 20 | 15 | 7 | 5 |
| RawPre-small | vless | G1 | youtube.com::video_playback | 5 | 0.878049 | False | 20 | 18 | 3 | 2 |
| RawPre-small | vless | G2 | bing.com::search_results_view | 0 | 0.900000 | False | 20 | 18 | 2 | 2 |
| RawPre-small | vless | G2 | developer.mozilla.org::document_view | 1 | 0.769231 | True | 20 | 15 | 4 | 5 |
| RawPre-small | vless | G2 | github.com::repository_view | 2 | 0.923077 | False | 20 | 18 | 1 | 2 |
| RawPre-small | vless | G2 | wikipedia.org::article_view | 3 | 0.636364 | False | 20 | 14 | 10 | 6 |
| RawPre-small | vless | G2 | youtube.com::search_results_view | 4 | 0.736842 | False | 20 | 14 | 4 | 6 |
| RawPre-small | vless | G2 | youtube.com::video_playback | 5 | 0.800000 | True | 20 | 16 | 4 | 4 |
| RawPre-small | vmess | G0 | bing.com::search_results_view | 0 | 0.750000 | False | 20 | 15 | 5 | 5 |
| RawPre-small | vmess | G0 | developer.mozilla.org::document_view | 1 | 0.585366 | False | 20 | 12 | 9 | 8 |
| RawPre-small | vmess | G0 | github.com::repository_view | 2 | 0.727273 | True | 20 | 12 | 1 | 8 |
| RawPre-small | vmess | G0 | wikipedia.org::article_view | 3 | 0.681818 | False | 20 | 15 | 9 | 5 |
| RawPre-small | vmess | G0 | youtube.com::search_results_view | 4 | 0.878049 | True | 20 | 18 | 3 | 2 |
| RawPre-small | vmess | G0 | youtube.com::video_playback | 5 | 0.926829 | False | 20 | 19 | 2 | 1 |
| RawPre-small | vmess | G1 | bing.com::search_results_view | 0 | 0.789474 | True | 20 | 15 | 3 | 5 |
| RawPre-small | vmess | G1 | developer.mozilla.org::document_view | 1 | 0.697674 | False | 20 | 15 | 8 | 5 |
| RawPre-small | vmess | G1 | github.com::repository_view | 2 | 0.926829 | False | 20 | 19 | 2 | 1 |
| RawPre-small | vmess | G1 | wikipedia.org::article_view | 3 | 0.742857 | True | 20 | 13 | 2 | 7 |
| RawPre-small | vmess | G1 | youtube.com::search_results_view | 4 | 0.909091 | False | 20 | 20 | 4 | 0 |
| RawPre-small | vmess | G1 | youtube.com::video_playback | 5 | 0.974359 | False | 20 | 19 | 0 | 1 |
| RawPre-small | vmess | G2 | bing.com::search_results_view | 0 | 0.714286 | False | 20 | 15 | 7 | 5 |
| RawPre-small | vmess | G2 | developer.mozilla.org::document_view | 1 | 0.516129 | True | 20 | 8 | 3 | 12 |
| RawPre-small | vmess | G2 | github.com::repository_view | 2 | 0.926829 | False | 20 | 19 | 2 | 1 |
| RawPre-small | vmess | G2 | wikipedia.org::article_view | 3 | 0.711111 | False | 20 | 16 | 9 | 4 |
| RawPre-small | vmess | G2 | youtube.com::search_results_view | 4 | 0.883721 | False | 20 | 19 | 4 | 1 |
| RawPre-small | vmess | G2 | youtube.com::video_playback | 5 | 0.947368 | True | 20 | 18 | 0 | 2 |
| S | shadowsocks | G0 | bing.com::search_results_view | 0 | 0.789474 | False | 20 | 15 | 3 | 5 |
| S | shadowsocks | G0 | developer.mozilla.org::document_view | 1 | 0.780488 | False | 20 | 16 | 5 | 4 |
| S | shadowsocks | G0 | github.com::repository_view | 2 | 0.709677 | True | 20 | 11 | 0 | 9 |
| S | shadowsocks | G0 | wikipedia.org::article_view | 3 | 0.850000 | False | 20 | 17 | 3 | 3 |
| S | shadowsocks | G0 | youtube.com::search_results_view | 4 | 0.789474 | True | 20 | 15 | 3 | 5 |
| S | shadowsocks | G0 | youtube.com::video_playback | 5 | 0.769231 | False | 20 | 20 | 12 | 0 |
| S | shadowsocks | G1 | bing.com::search_results_view | 0 | 0.777778 | True | 20 | 14 | 2 | 6 |
| S | shadowsocks | G1 | developer.mozilla.org::document_view | 1 | 0.723404 | False | 20 | 17 | 10 | 3 |
| S | shadowsocks | G1 | github.com::repository_view | 2 | 0.864865 | False | 20 | 16 | 1 | 4 |
| S | shadowsocks | G1 | wikipedia.org::article_view | 3 | 0.687500 | True | 20 | 11 | 1 | 9 |
| S | shadowsocks | G1 | youtube.com::search_results_view | 4 | 0.857143 | False | 20 | 18 | 4 | 2 |
| S | shadowsocks | G1 | youtube.com::video_playback | 5 | 0.826087 | False | 20 | 19 | 7 | 1 |
| S | shadowsocks | G2 | bing.com::search_results_view | 0 | 0.755556 | False | 20 | 17 | 8 | 3 |
| S | shadowsocks | G2 | developer.mozilla.org::document_view | 1 | 0.400000 | True | 20 | 6 | 4 | 14 |
| S | shadowsocks | G2 | github.com::repository_view | 2 | 0.871795 | False | 20 | 17 | 2 | 3 |
| S | shadowsocks | G2 | wikipedia.org::article_view | 3 | 0.641509 | False | 20 | 17 | 16 | 3 |
| S | shadowsocks | G2 | youtube.com::search_results_view | 4 | 0.790698 | False | 20 | 17 | 6 | 3 |
| S | shadowsocks | G2 | youtube.com::video_playback | 5 | 0.600000 | True | 20 | 9 | 1 | 11 |
| S | trojan | G0 | bing.com::search_results_view | 0 | 0.850000 | False | 20 | 17 | 3 | 3 |
| S | trojan | G0 | developer.mozilla.org::document_view | 1 | 0.820513 | False | 20 | 16 | 3 | 4 |
| S | trojan | G0 | github.com::repository_view | 2 | 0.975610 | True | 20 | 20 | 1 | 0 |
| S | trojan | G0 | wikipedia.org::article_view | 3 | 0.842105 | False | 20 | 16 | 2 | 4 |
| S | trojan | G0 | youtube.com::search_results_view | 4 | 0.850000 | True | 20 | 17 | 3 | 3 |
| S | trojan | G0 | youtube.com::video_playback | 5 | 0.857143 | False | 20 | 18 | 4 | 2 |
| S | trojan | G1 | bing.com::search_results_view | 0 | 0.918919 | True | 20 | 17 | 0 | 3 |
| S | trojan | G1 | developer.mozilla.org::document_view | 1 | 0.837209 | False | 20 | 18 | 5 | 2 |
| S | trojan | G1 | github.com::repository_view | 2 | 1.000000 | False | 20 | 20 | 0 | 0 |
| S | trojan | G1 | wikipedia.org::article_view | 3 | 0.871795 | True | 20 | 17 | 2 | 3 |
| S | trojan | G1 | youtube.com::search_results_view | 4 | 0.820513 | False | 20 | 16 | 3 | 4 |
| S | trojan | G1 | youtube.com::video_playback | 5 | 0.857143 | False | 20 | 18 | 4 | 2 |
| S | trojan | G2 | bing.com::search_results_view | 0 | 0.878049 | False | 20 | 18 | 3 | 2 |
| S | trojan | G2 | developer.mozilla.org::document_view | 1 | 0.756757 | True | 20 | 14 | 3 | 6 |
| S | trojan | G2 | github.com::repository_view | 2 | 0.975610 | False | 20 | 20 | 1 | 0 |
| S | trojan | G2 | wikipedia.org::article_view | 3 | 0.820513 | False | 20 | 16 | 3 | 4 |
| S | trojan | G2 | youtube.com::search_results_view | 4 | 0.883721 | False | 20 | 19 | 4 | 1 |
| S | trojan | G2 | youtube.com::video_playback | 5 | 0.820513 | True | 20 | 16 | 3 | 4 |
| S | vless | G0 | bing.com::search_results_view | 0 | 0.923077 | False | 20 | 18 | 1 | 2 |
| S | vless | G0 | developer.mozilla.org::document_view | 1 | 0.800000 | False | 20 | 16 | 4 | 4 |
| S | vless | G0 | github.com::repository_view | 2 | 0.894737 | True | 20 | 17 | 1 | 3 |
| S | vless | G0 | wikipedia.org::article_view | 3 | 0.681818 | False | 20 | 15 | 9 | 5 |
| S | vless | G0 | youtube.com::search_results_view | 4 | 0.777778 | True | 20 | 14 | 2 | 6 |
| S | vless | G0 | youtube.com::video_playback | 5 | 0.837209 | False | 20 | 18 | 5 | 2 |
| S | vless | G1 | bing.com::search_results_view | 0 | 0.850000 | True | 20 | 17 | 3 | 3 |
| S | vless | G1 | developer.mozilla.org::document_view | 1 | 0.750000 | False | 20 | 15 | 5 | 5 |
| S | vless | G1 | github.com::repository_view | 2 | 0.900000 | False | 20 | 18 | 2 | 2 |
| S | vless | G1 | wikipedia.org::article_view | 3 | 0.684211 | True | 20 | 13 | 5 | 7 |
| S | vless | G1 | youtube.com::search_results_view | 4 | 0.731707 | False | 20 | 15 | 6 | 5 |
| S | vless | G1 | youtube.com::video_playback | 5 | 0.878049 | False | 20 | 18 | 3 | 2 |
| S | vless | G2 | bing.com::search_results_view | 0 | 0.904762 | False | 20 | 19 | 3 | 1 |
| S | vless | G2 | developer.mozilla.org::document_view | 1 | 0.777778 | True | 20 | 14 | 2 | 6 |
| S | vless | G2 | github.com::repository_view | 2 | 0.894737 | False | 20 | 17 | 1 | 3 |
| S | vless | G2 | wikipedia.org::article_view | 3 | 0.666667 | False | 20 | 15 | 10 | 5 |
| S | vless | G2 | youtube.com::search_results_view | 4 | 0.684211 | False | 20 | 13 | 5 | 7 |
| S | vless | G2 | youtube.com::video_playback | 5 | 0.878049 | True | 20 | 18 | 3 | 2 |
| S | vmess | G0 | bing.com::search_results_view | 0 | 0.769231 | False | 20 | 15 | 4 | 5 |
| S | vmess | G0 | developer.mozilla.org::document_view | 1 | 0.585366 | False | 20 | 12 | 9 | 8 |
| S | vmess | G0 | github.com::repository_view | 2 | 0.800000 | True | 20 | 14 | 1 | 6 |
| S | vmess | G0 | wikipedia.org::article_view | 3 | 0.711111 | False | 20 | 16 | 9 | 4 |
| S | vmess | G0 | youtube.com::search_results_view | 4 | 0.878049 | True | 20 | 18 | 3 | 2 |
| S | vmess | G0 | youtube.com::video_playback | 5 | 0.974359 | False | 20 | 19 | 0 | 1 |
| S | vmess | G1 | bing.com::search_results_view | 0 | 0.789474 | True | 20 | 15 | 3 | 5 |
| S | vmess | G1 | developer.mozilla.org::document_view | 1 | 0.727273 | False | 20 | 16 | 8 | 4 |
| S | vmess | G1 | github.com::repository_view | 2 | 0.926829 | False | 20 | 19 | 2 | 1 |
| S | vmess | G1 | wikipedia.org::article_view | 3 | 0.764706 | True | 20 | 13 | 1 | 7 |
| S | vmess | G1 | youtube.com::search_results_view | 4 | 0.909091 | False | 20 | 20 | 4 | 0 |
| S | vmess | G1 | youtube.com::video_playback | 5 | 0.974359 | False | 20 | 19 | 0 | 1 |
| S | vmess | G2 | bing.com::search_results_view | 0 | 0.731707 | False | 20 | 15 | 6 | 5 |
| S | vmess | G2 | developer.mozilla.org::document_view | 1 | 0.344828 | True | 20 | 5 | 4 | 15 |
| S | vmess | G2 | github.com::repository_view | 2 | 0.883721 | False | 20 | 19 | 4 | 1 |
| S | vmess | G2 | wikipedia.org::article_view | 3 | 0.695652 | False | 20 | 16 | 10 | 4 |
| S | vmess | G2 | youtube.com::search_results_view | 4 | 0.883721 | False | 20 | 19 | 4 | 1 |
| S | vmess | G2 | youtube.com::video_playback | 5 | 0.947368 | True | 20 | 18 | 0 | 2 |

## 逐角色结果

| arm | target | group | outer | F1_all | accuracy | CE_nats | Brier | CE_bits | F1_uncovered | F1_aux |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| G-small | shadowsocks | G0 | 0 | 0.795635 | 0.791667 | 0.428584 | 0.257855 | 0.618317 | 0.928571 | 0.729167 |
| G-small | shadowsocks | G0 | 1 | 0.770899 | 0.791667 | 0.900989 | 0.339635 | 1.299853 | 0.873016 | 0.719841 |
| G-small | shadowsocks | G0 | 2 | 0.722932 | 0.750000 | 0.939861 | 0.400133 | 1.355933 | 0.644444 | 0.762175 |
| G-small | shadowsocks | G0 | 3 | 0.865741 | 0.875000 | 0.866499 | 0.233421 | 1.250093 | 0.944444 | 0.826389 |
| G-small | shadowsocks | G0 | 4 | 0.782588 | 0.791667 | 0.772759 | 0.375611 | 1.114856 | 0.666667 | 0.840548 |
| G-small | shadowsocks | G1 | 0 | 0.827116 | 0.833333 | 1.384861 | 0.285013 | 1.997932 | 0.761905 | 0.859722 |
| G-small | shadowsocks | G1 | 1 | 0.836640 | 0.833333 | 0.576863 | 0.281305 | 0.832237 | 0.761905 | 0.874008 |
| G-small | shadowsocks | G1 | 2 | 0.787037 | 0.791667 | 0.814459 | 0.354928 | 1.175017 | 0.833333 | 0.763889 |
| G-small | shadowsocks | G1 | 3 | 0.668687 | 0.708333 | 0.889114 | 0.355561 | 1.282721 | 0.400000 | 0.803030 |
| G-small | shadowsocks | G1 | 4 | 0.663672 | 0.666667 | 0.692640 | 0.389548 | 0.999268 | 0.660714 | 0.665152 |
| G-small | shadowsocks | G2 | 0 | 0.698593 | 0.708333 | 0.904147 | 0.416510 | 1.304408 | 0.571429 | 0.762175 |
| G-small | shadowsocks | G2 | 1 | 0.697403 | 0.750000 | 0.795175 | 0.386190 | 1.147195 | 0.500000 | 0.796104 |
| G-small | shadowsocks | G2 | 2 | 0.633333 | 0.666667 | 1.006443 | 0.445706 | 1.451991 | 0.366667 | 0.766667 |
| G-small | shadowsocks | G2 | 3 | 0.831746 | 0.833333 | 0.901056 | 0.324221 | 1.299949 | 0.833333 | 0.830952 |
| G-small | shadowsocks | G2 | 4 | 0.706530 | 0.708333 | 0.659353 | 0.344555 | 0.951245 | 0.619048 | 0.750271 |
| G-small | trojan | G0 | 0 | 0.876720 | 0.875000 | 0.355596 | 0.193367 | 0.513016 | 0.944444 | 0.842857 |
| G-small | trojan | G0 | 1 | 0.915344 | 0.916667 | 0.377833 | 0.180007 | 0.545097 | 0.944444 | 0.900794 |
| G-small | trojan | G0 | 2 | 0.868783 | 0.875000 | 0.337870 | 0.196830 | 0.487444 | 0.833333 | 0.886508 |
| G-small | trojan | G0 | 3 | 0.784392 | 0.791667 | 0.509733 | 0.294674 | 0.735389 | 0.888889 | 0.732143 |
| G-small | trojan | G0 | 4 | 0.832672 | 0.833333 | 0.392677 | 0.240896 | 0.566512 | 0.928571 | 0.784722 |
| G-small | trojan | G1 | 0 | 0.916667 | 0.916667 | 0.220152 | 0.112541 | 0.317612 | 0.875000 | 0.937500 |
| G-small | trojan | G1 | 1 | 0.919048 | 0.916667 | 0.562059 | 0.199868 | 0.810880 | 0.928571 | 0.914286 |
| G-small | trojan | G1 | 2 | 0.780423 | 0.791667 | 0.487518 | 0.299067 | 0.703340 | 0.888889 | 0.726190 |
| G-small | trojan | G1 | 3 | 0.873677 | 0.875000 | 0.388247 | 0.217584 | 0.560123 | 0.857143 | 0.881944 |
| G-small | trojan | G1 | 4 | 0.915344 | 0.916667 | 0.395480 | 0.221177 | 0.570557 | 0.928571 | 0.908730 |
| G-small | trojan | G2 | 0 | 0.865741 | 0.875000 | 0.369756 | 0.202983 | 0.533445 | 0.833333 | 0.881944 |
| G-small | trojan | G2 | 1 | 0.957672 | 0.958333 | 0.275671 | 0.148867 | 0.397709 | 0.944444 | 0.964286 |
| G-small | trojan | G2 | 2 | 0.784127 | 0.791667 | 0.442186 | 0.257451 | 0.637940 | 0.619048 | 0.866667 |
| G-small | trojan | G2 | 3 | 0.740741 | 0.750000 | 0.508169 | 0.291249 | 0.733133 | 0.625000 | 0.798611 |
| G-small | trojan | G2 | 4 | 0.916005 | 0.916667 | 0.318576 | 0.183921 | 0.459608 | 0.944444 | 0.901786 |
| G-small | vless | G0 | 0 | 0.749206 | 0.750000 | 0.657303 | 0.337036 | 0.948287 | 0.785714 | 0.730952 |
| G-small | vless | G0 | 1 | 0.729894 | 0.750000 | 0.632393 | 0.314109 | 0.912351 | 0.750000 | 0.719841 |
| G-small | vless | G0 | 2 | 0.802381 | 0.791667 | 0.648403 | 0.372657 | 0.935448 | 0.857143 | 0.775000 |
| G-small | vless | G0 | 3 | 0.916005 | 0.916667 | 0.283022 | 0.129626 | 0.408314 | 1.000000 | 0.874008 |
| G-small | vless | G0 | 4 | 0.877381 | 0.875000 | 0.658951 | 0.237709 | 0.950665 | 0.803571 | 0.914286 |
| G-small | vless | G1 | 0 | 0.790079 | 0.791667 | 0.650748 | 0.338998 | 0.938831 | 0.733333 | 0.818452 |
| G-small | vless | G1 | 1 | 0.805820 | 0.833333 | 0.658263 | 0.279147 | 0.949672 | 0.700000 | 0.858730 |
| G-small | vless | G1 | 2 | 0.717063 | 0.708333 | 0.959088 | 0.477254 | 1.383672 | 0.761905 | 0.694643 |
| G-small | vless | G1 | 3 | 0.873677 | 0.875000 | 0.468116 | 0.169027 | 0.675349 | 0.819444 | 0.900794 |
| G-small | vless | G1 | 4 | 0.915344 | 0.916667 | 0.617612 | 0.210051 | 0.891026 | 0.857143 | 0.944444 |
| G-small | vless | G2 | 0 | 0.787831 | 0.791667 | 0.648273 | 0.330198 | 0.935260 | 0.833333 | 0.765079 |
| G-small | vless | G2 | 1 | 0.826058 | 0.833333 | 0.485246 | 0.224916 | 0.700062 | 0.888889 | 0.794643 |
| G-small | vless | G2 | 2 | 0.756746 | 0.750000 | 0.836850 | 0.427214 | 1.207319 | 0.708333 | 0.780952 |
| G-small | vless | G2 | 3 | 0.916005 | 0.916667 | 0.447026 | 0.192099 | 0.644922 | 0.928571 | 0.909722 |
| G-small | vless | G2 | 4 | 0.757937 | 0.750000 | 0.676759 | 0.278515 | 0.976357 | 0.803571 | 0.735119 |
| G-small | vmess | G0 | 0 | 0.867725 | 0.875000 | 0.413450 | 0.200003 | 0.596483 | 0.873016 | 0.865079 |
| G-small | vmess | G0 | 1 | 0.777297 | 0.791667 | 0.615507 | 0.308210 | 0.887990 | 0.857143 | 0.737374 |
| G-small | vmess | G0 | 2 | 0.662698 | 0.666667 | 1.517942 | 0.443290 | 2.189928 | 0.803571 | 0.592262 |
| G-small | vmess | G0 | 3 | 0.868783 | 0.875000 | 0.775466 | 0.237603 | 1.118761 | 1.000000 | 0.803175 |
| G-small | vmess | G0 | 4 | 0.835714 | 0.833333 | 0.702060 | 0.262513 | 1.012859 | 0.828571 | 0.839286 |
| G-small | vmess | G1 | 0 | 0.907407 | 0.916667 | 0.484870 | 0.168404 | 0.699520 | 0.833333 | 0.944444 |
| G-small | vmess | G1 | 1 | 0.724868 | 0.750000 | 0.862848 | 0.362221 | 1.244826 | 0.619048 | 0.777778 |
| G-small | vmess | G1 | 2 | 0.870370 | 0.875000 | 0.394522 | 0.231312 | 0.569175 | 0.777778 | 0.916667 |
| G-small | vmess | G1 | 3 | 0.796429 | 0.791667 | 0.798427 | 0.246386 | 1.151886 | 0.675000 | 0.857143 |
| G-small | vmess | G1 | 4 | 0.919048 | 0.916667 | 0.709644 | 0.209420 | 1.023800 | 0.928571 | 0.914286 |
| G-small | vmess | G2 | 0 | 0.778836 | 0.791667 | 0.384401 | 0.227242 | 0.554573 | 0.761905 | 0.787302 |
| G-small | vmess | G2 | 1 | 0.686243 | 0.708333 | 1.184014 | 0.443467 | 1.708171 | 0.642857 | 0.707937 |
| G-small | vmess | G2 | 2 | 0.779894 | 0.791667 | 0.862983 | 0.395110 | 1.245021 | 0.666667 | 0.836508 |
| G-small | vmess | G2 | 3 | 0.809524 | 0.833333 | 0.913545 | 0.290072 | 1.317966 | 0.628571 | 0.900000 |
| G-small | vmess | G2 | 4 | 0.727778 | 0.750000 | 0.898272 | 0.371220 | 1.295933 | 0.700000 | 0.741667 |
| Marginal-small | shadowsocks | G0 | 0 | 0.873677 | 0.875000 | 0.341681 | 0.190490 | 0.492941 | 0.928571 | 0.846230 |
| Marginal-small | shadowsocks | G0 | 1 | 0.770899 | 0.791667 | 0.798676 | 0.325611 | 1.152246 | 0.873016 | 0.719841 |
| Marginal-small | shadowsocks | G0 | 2 | 0.641450 | 0.708333 | 1.047904 | 0.452997 | 1.511806 | 0.400000 | 0.762175 |
| Marginal-small | shadowsocks | G0 | 3 | 0.832672 | 0.833333 | 0.756711 | 0.227786 | 1.091704 | 0.928571 | 0.784722 |
| Marginal-small | shadowsocks | G0 | 4 | 0.728042 | 0.750000 | 0.812149 | 0.386957 | 1.171683 | 0.533333 | 0.825397 |
| Marginal-small | shadowsocks | G1 | 0 | 0.865079 | 0.875000 | 0.818754 | 0.250984 | 1.181213 | 0.761905 | 0.916667 |
| Marginal-small | shadowsocks | G1 | 1 | 0.836640 | 0.833333 | 0.626185 | 0.290757 | 0.903394 | 0.761905 | 0.874008 |
| Marginal-small | shadowsocks | G1 | 2 | 0.787037 | 0.791667 | 0.840402 | 0.369952 | 1.212444 | 0.833333 | 0.763889 |
| Marginal-small | shadowsocks | G1 | 3 | 0.662963 | 0.708333 | 0.840641 | 0.383650 | 1.212788 | 0.400000 | 0.794444 |
| Marginal-small | shadowsocks | G1 | 4 | 0.663672 | 0.666667 | 0.689396 | 0.388421 | 0.994589 | 0.660714 | 0.665152 |
| Marginal-small | shadowsocks | G2 | 0 | 0.646032 | 0.666667 | 0.811519 | 0.418558 | 1.170775 | 0.571429 | 0.683333 |
| Marginal-small | shadowsocks | G2 | 1 | 0.697403 | 0.750000 | 0.848441 | 0.404641 | 1.224041 | 0.500000 | 0.796104 |
| Marginal-small | shadowsocks | G2 | 2 | 0.595815 | 0.625000 | 0.960762 | 0.474715 | 1.386086 | 0.309524 | 0.738961 |
| Marginal-small | shadowsocks | G2 | 3 | 0.798413 | 0.791667 | 0.810799 | 0.345599 | 1.169736 | 0.833333 | 0.780952 |
| Marginal-small | shadowsocks | G2 | 4 | 0.706530 | 0.708333 | 0.708845 | 0.359959 | 1.022647 | 0.619048 | 0.750271 |
| Marginal-small | trojan | G0 | 0 | 0.915344 | 0.916667 | 0.309305 | 0.164218 | 0.446233 | 0.944444 | 0.900794 |
| Marginal-small | trojan | G0 | 1 | 0.874339 | 0.875000 | 0.383225 | 0.179002 | 0.552877 | 0.944444 | 0.839286 |
| Marginal-small | trojan | G0 | 2 | 0.818519 | 0.833333 | 0.359156 | 0.209532 | 0.518152 | 0.833333 | 0.811111 |
| Marginal-small | trojan | G0 | 3 | 0.825397 | 0.833333 | 0.444971 | 0.251099 | 0.641958 | 0.888889 | 0.793651 |
| Marginal-small | trojan | G0 | 4 | 0.873677 | 0.875000 | 0.403972 | 0.238904 | 0.582809 | 0.928571 | 0.846230 |
| Marginal-small | trojan | G1 | 0 | 0.874339 | 0.875000 | 0.253529 | 0.138944 | 0.365765 | 0.803571 | 0.909722 |
| Marginal-small | trojan | G1 | 1 | 0.878968 | 0.875000 | 0.502012 | 0.214862 | 0.724250 | 0.803571 | 0.916667 |
| Marginal-small | trojan | G1 | 2 | 0.780423 | 0.791667 | 0.646123 | 0.327282 | 0.932158 | 0.888889 | 0.726190 |
| Marginal-small | trojan | G1 | 3 | 0.873677 | 0.875000 | 0.415795 | 0.217295 | 0.599866 | 0.857143 | 0.881944 |
| Marginal-small | trojan | G1 | 4 | 0.874339 | 0.875000 | 0.410290 | 0.237340 | 0.591923 | 0.875000 | 0.874008 |
| Marginal-small | trojan | G2 | 0 | 0.865741 | 0.875000 | 0.346570 | 0.187115 | 0.499995 | 0.833333 | 0.881944 |
| Marginal-small | trojan | G2 | 1 | 0.874339 | 0.875000 | 0.427191 | 0.188295 | 0.616307 | 0.944444 | 0.839286 |
| Marginal-small | trojan | G2 | 2 | 0.782143 | 0.791667 | 0.512726 | 0.273477 | 0.739707 | 0.571429 | 0.887500 |
| Marginal-small | trojan | G2 | 3 | 0.784392 | 0.791667 | 0.539818 | 0.288096 | 0.778793 | 0.714286 | 0.819444 |
| Marginal-small | trojan | G2 | 4 | 0.916667 | 0.916667 | 0.326606 | 0.187519 | 0.471193 | 0.875000 | 0.937500 |
| Marginal-small | vless | G0 | 0 | 0.830159 | 0.833333 | 0.716564 | 0.353763 | 1.033783 | 0.928571 | 0.780952 |
| Marginal-small | vless | G0 | 1 | 0.787434 | 0.791667 | 0.590638 | 0.308052 | 0.852110 | 0.803571 | 0.779365 |
| Marginal-small | vless | G0 | 2 | 0.791005 | 0.791667 | 0.797005 | 0.432954 | 1.149835 | 0.761905 | 0.805556 |
| Marginal-small | vless | G0 | 3 | 0.916005 | 0.916667 | 0.284831 | 0.125243 | 0.410925 | 1.000000 | 0.874008 |
| Marginal-small | vless | G0 | 4 | 0.874339 | 0.875000 | 0.577154 | 0.207736 | 0.832657 | 0.803571 | 0.909722 |
| Marginal-small | vless | G1 | 0 | 0.748413 | 0.750000 | 0.758200 | 0.364598 | 1.093851 | 0.650000 | 0.797619 |
| Marginal-small | vless | G1 | 1 | 0.767196 | 0.791667 | 0.787145 | 0.321727 | 1.135611 | 0.628571 | 0.836508 |
| Marginal-small | vless | G1 | 2 | 0.673280 | 0.666667 | 1.014753 | 0.452130 | 1.463979 | 0.708333 | 0.655754 |
| Marginal-small | vless | G1 | 3 | 0.874339 | 0.875000 | 0.441024 | 0.155506 | 0.636264 | 0.875000 | 0.874008 |
| Marginal-small | vless | G1 | 4 | 0.915344 | 0.916667 | 0.582143 | 0.193645 | 0.839855 | 0.857143 | 0.944444 |
| Marginal-small | vless | G2 | 0 | 0.787831 | 0.791667 | 0.700108 | 0.357741 | 1.010043 | 0.833333 | 0.765079 |
| Marginal-small | vless | G2 | 1 | 0.826058 | 0.833333 | 0.451847 | 0.205555 | 0.651878 | 0.888889 | 0.794643 |
| Marginal-small | vless | G2 | 2 | 0.756746 | 0.750000 | 0.993769 | 0.492979 | 1.433706 | 0.708333 | 0.780952 |
| Marginal-small | vless | G2 | 3 | 0.916005 | 0.916667 | 0.430310 | 0.185511 | 0.620806 | 0.928571 | 0.909722 |
| Marginal-small | vless | G2 | 4 | 0.835979 | 0.833333 | 0.612422 | 0.245049 | 0.883537 | 0.857143 | 0.825397 |
| Marginal-small | vmess | G0 | 0 | 0.871429 | 0.875000 | 0.399216 | 0.193767 | 0.575947 | 0.928571 | 0.842857 |
| Marginal-small | vmess | G0 | 1 | 0.777297 | 0.791667 | 0.605271 | 0.308955 | 0.873222 | 0.857143 | 0.737374 |
| Marginal-small | vmess | G0 | 2 | 0.524339 | 0.541667 | 1.590523 | 0.535543 | 2.294640 | 0.595238 | 0.488889 |
| Marginal-small | vmess | G0 | 3 | 0.868783 | 0.875000 | 0.774215 | 0.247471 | 1.116957 | 1.000000 | 0.803175 |
| Marginal-small | vmess | G0 | 4 | 0.835714 | 0.833333 | 0.646074 | 0.250980 | 0.932088 | 0.828571 | 0.839286 |
| Marginal-small | vmess | G1 | 0 | 0.907407 | 0.916667 | 0.462424 | 0.158488 | 0.667137 | 0.833333 | 0.944444 |
| Marginal-small | vmess | G1 | 1 | 0.740741 | 0.750000 | 0.775806 | 0.379243 | 1.119251 | 0.708333 | 0.756944 |
| Marginal-small | vmess | G1 | 2 | 0.787037 | 0.791667 | 0.548213 | 0.316440 | 0.790904 | 0.666667 | 0.847222 |
| Marginal-small | vmess | G1 | 3 | 0.795635 | 0.791667 | 0.743918 | 0.246352 | 1.073247 | 0.708333 | 0.839286 |
| Marginal-small | vmess | G1 | 4 | 0.830159 | 0.833333 | 0.695943 | 0.213043 | 1.004033 | 0.761905 | 0.864286 |
| Marginal-small | vmess | G2 | 0 | 0.829762 | 0.833333 | 0.357344 | 0.205061 | 0.515538 | 0.803571 | 0.842857 |
| Marginal-small | vmess | G2 | 1 | 0.623810 | 0.666667 | 1.271834 | 0.427543 | 1.834868 | 0.500000 | 0.685714 |
| Marginal-small | vmess | G2 | 2 | 0.706481 | 0.750000 | 1.026992 | 0.434759 | 1.481636 | 0.500000 | 0.809722 |
| Marginal-small | vmess | G2 | 3 | 0.776190 | 0.791667 | 0.936633 | 0.332942 | 1.351276 | 0.595238 | 0.866667 |
| Marginal-small | vmess | G2 | 4 | 0.727778 | 0.750000 | 0.848894 | 0.368976 | 1.224695 | 0.700000 | 0.741667 |
| P-small | shadowsocks | G0 | 0 | 0.795635 | 0.791667 | 0.425968 | 0.258061 | 0.614542 | 0.928571 | 0.729167 |
| P-small | shadowsocks | G0 | 1 | 0.770899 | 0.791667 | 0.887547 | 0.345744 | 1.280460 | 0.873016 | 0.719841 |
| P-small | shadowsocks | G0 | 2 | 0.779497 | 0.791667 | 0.832811 | 0.374841 | 1.201492 | 0.777778 | 0.780357 |
| P-small | shadowsocks | G0 | 3 | 0.865741 | 0.875000 | 0.839835 | 0.236988 | 1.211626 | 0.944444 | 0.826389 |
| P-small | shadowsocks | G0 | 4 | 0.782588 | 0.791667 | 0.749307 | 0.364839 | 1.081022 | 0.666667 | 0.840548 |
| P-small | shadowsocks | G1 | 0 | 0.780556 | 0.791667 | 1.003243 | 0.286122 | 1.447374 | 0.666667 | 0.837500 |
| P-small | shadowsocks | G1 | 1 | 0.836640 | 0.833333 | 0.607045 | 0.286002 | 0.875781 | 0.761905 | 0.874008 |
| P-small | shadowsocks | G1 | 2 | 0.787037 | 0.791667 | 0.815270 | 0.355585 | 1.176187 | 0.833333 | 0.763889 |
| P-small | shadowsocks | G1 | 3 | 0.662963 | 0.708333 | 0.819042 | 0.349430 | 1.181628 | 0.400000 | 0.794444 |
| P-small | shadowsocks | G1 | 4 | 0.663672 | 0.666667 | 0.706392 | 0.405963 | 1.019108 | 0.660714 | 0.665152 |
| P-small | shadowsocks | G2 | 0 | 0.736291 | 0.750000 | 0.856737 | 0.399765 | 1.236010 | 0.595238 | 0.806818 |
| P-small | shadowsocks | G2 | 1 | 0.697403 | 0.750000 | 0.792647 | 0.381792 | 1.143548 | 0.500000 | 0.796104 |
| P-small | shadowsocks | G2 | 2 | 0.633333 | 0.666667 | 0.986975 | 0.444287 | 1.423905 | 0.366667 | 0.766667 |
| P-small | shadowsocks | G2 | 3 | 0.831746 | 0.833333 | 0.860468 | 0.310101 | 1.241393 | 0.833333 | 0.830952 |
| P-small | shadowsocks | G2 | 4 | 0.706530 | 0.708333 | 0.647538 | 0.343414 | 0.934200 | 0.619048 | 0.750271 |
| P-small | trojan | G0 | 0 | 0.915344 | 0.916667 | 0.340116 | 0.179051 | 0.490684 | 0.944444 | 0.900794 |
| P-small | trojan | G0 | 1 | 0.915344 | 0.916667 | 0.376294 | 0.176279 | 0.542878 | 0.944444 | 0.900794 |
| P-small | trojan | G0 | 2 | 0.868783 | 0.875000 | 0.330529 | 0.193127 | 0.476852 | 0.833333 | 0.886508 |
| P-small | trojan | G0 | 3 | 0.825397 | 0.833333 | 0.521160 | 0.296779 | 0.751875 | 0.888889 | 0.793651 |
| P-small | trojan | G0 | 4 | 0.832672 | 0.833333 | 0.392049 | 0.237978 | 0.565607 | 0.928571 | 0.784722 |
| P-small | trojan | G1 | 0 | 0.916667 | 0.916667 | 0.231583 | 0.119226 | 0.334103 | 0.875000 | 0.937500 |
| P-small | trojan | G1 | 1 | 0.957672 | 0.958333 | 0.521232 | 0.207487 | 0.751979 | 0.928571 | 0.972222 |
| P-small | trojan | G1 | 2 | 0.780423 | 0.791667 | 0.512845 | 0.301195 | 0.739879 | 0.888889 | 0.726190 |
| P-small | trojan | G1 | 3 | 0.873677 | 0.875000 | 0.383011 | 0.214572 | 0.552567 | 0.857143 | 0.881944 |
| P-small | trojan | G1 | 4 | 0.915344 | 0.916667 | 0.391438 | 0.224869 | 0.564726 | 0.928571 | 0.908730 |
| P-small | trojan | G2 | 0 | 0.865741 | 0.875000 | 0.371669 | 0.206345 | 0.536205 | 0.833333 | 0.881944 |
| P-small | trojan | G2 | 1 | 0.957672 | 0.958333 | 0.250686 | 0.130415 | 0.361663 | 0.944444 | 0.964286 |
| P-small | trojan | G2 | 2 | 0.784127 | 0.791667 | 0.457907 | 0.255872 | 0.660620 | 0.619048 | 0.866667 |
| P-small | trojan | G2 | 3 | 0.784392 | 0.791667 | 0.529870 | 0.294550 | 0.764441 | 0.660714 | 0.846230 |
| P-small | trojan | G2 | 4 | 0.916005 | 0.916667 | 0.313422 | 0.179663 | 0.452172 | 0.944444 | 0.901786 |
| P-small | vless | G0 | 0 | 0.754930 | 0.750000 | 0.680935 | 0.349048 | 0.982381 | 0.785714 | 0.739538 |
| P-small | vless | G0 | 1 | 0.787434 | 0.791667 | 0.787492 | 0.305929 | 1.136111 | 0.803571 | 0.779365 |
| P-small | vless | G0 | 2 | 0.802381 | 0.791667 | 0.635225 | 0.365016 | 0.916436 | 0.857143 | 0.775000 |
| P-small | vless | G0 | 3 | 0.916005 | 0.916667 | 0.281963 | 0.126850 | 0.406787 | 1.000000 | 0.874008 |
| P-small | vless | G0 | 4 | 0.877381 | 0.875000 | 0.716362 | 0.242581 | 1.033492 | 0.803571 | 0.914286 |
| P-small | vless | G1 | 0 | 0.790079 | 0.791667 | 0.649593 | 0.332311 | 0.937165 | 0.733333 | 0.818452 |
| P-small | vless | G1 | 1 | 0.767196 | 0.791667 | 0.688395 | 0.293671 | 0.993144 | 0.628571 | 0.836508 |
| P-small | vless | G1 | 2 | 0.717063 | 0.708333 | 0.772144 | 0.440582 | 1.113968 | 0.761905 | 0.694643 |
| P-small | vless | G1 | 3 | 0.873677 | 0.875000 | 0.498226 | 0.174669 | 0.718789 | 0.819444 | 0.900794 |
| P-small | vless | G1 | 4 | 0.915344 | 0.916667 | 0.619008 | 0.213050 | 0.893040 | 0.857143 | 0.944444 |
| P-small | vless | G2 | 0 | 0.787831 | 0.791667 | 0.621658 | 0.319155 | 0.896864 | 0.833333 | 0.765079 |
| P-small | vless | G2 | 1 | 0.787434 | 0.791667 | 0.487932 | 0.223500 | 0.703937 | 0.844444 | 0.758929 |
| P-small | vless | G2 | 2 | 0.754149 | 0.750000 | 0.846760 | 0.435317 | 1.221617 | 0.708333 | 0.777056 |
| P-small | vless | G2 | 3 | 0.916005 | 0.916667 | 0.429313 | 0.186903 | 0.619368 | 0.928571 | 0.909722 |
| P-small | vless | G2 | 4 | 0.757937 | 0.750000 | 0.677102 | 0.283248 | 0.976851 | 0.803571 | 0.735119 |
| P-small | vmess | G0 | 0 | 0.867725 | 0.875000 | 0.407877 | 0.197622 | 0.588443 | 0.873016 | 0.865079 |
| P-small | vmess | G0 | 1 | 0.777297 | 0.791667 | 0.609713 | 0.306766 | 0.879630 | 0.857143 | 0.737374 |
| P-small | vmess | G0 | 2 | 0.662698 | 0.666667 | 1.364411 | 0.458680 | 1.968429 | 0.803571 | 0.592262 |
| P-small | vmess | G0 | 3 | 0.868783 | 0.875000 | 0.780258 | 0.247523 | 1.125674 | 1.000000 | 0.803175 |
| P-small | vmess | G0 | 4 | 0.835714 | 0.833333 | 0.702872 | 0.263071 | 1.014029 | 0.828571 | 0.839286 |
| P-small | vmess | G1 | 0 | 0.907407 | 0.916667 | 0.482137 | 0.173152 | 0.695577 | 0.833333 | 0.944444 |
| P-small | vmess | G1 | 1 | 0.780423 | 0.791667 | 0.693251 | 0.345310 | 1.000150 | 0.666667 | 0.837302 |
| P-small | vmess | G1 | 2 | 0.828704 | 0.833333 | 0.434062 | 0.265219 | 0.626219 | 0.708333 | 0.888889 |
| P-small | vmess | G1 | 3 | 0.795635 | 0.791667 | 0.799018 | 0.247064 | 1.152740 | 0.708333 | 0.839286 |
| P-small | vmess | G1 | 4 | 0.919048 | 0.916667 | 0.705524 | 0.201501 | 1.017857 | 0.928571 | 0.914286 |
| P-small | vmess | G2 | 0 | 0.829762 | 0.833333 | 0.382677 | 0.226660 | 0.552086 | 0.803571 | 0.842857 |
| P-small | vmess | G2 | 1 | 0.686243 | 0.708333 | 1.240195 | 0.450887 | 1.789223 | 0.642857 | 0.707937 |
| P-small | vmess | G2 | 2 | 0.773148 | 0.791667 | 0.880364 | 0.393303 | 1.270097 | 0.666667 | 0.826389 |
| P-small | vmess | G2 | 3 | 0.809524 | 0.833333 | 0.921213 | 0.294646 | 1.329029 | 0.628571 | 0.900000 |
| P-small | vmess | G2 | 4 | 0.767857 | 0.791667 | 0.889250 | 0.365085 | 1.282916 | 0.700000 | 0.801786 |
| RawPost-small | shadowsocks | G0 | 0 | 0.841450 | 0.833333 | 0.443539 | 0.257316 | 0.639892 | 0.857143 | 0.833604 |
| RawPost-small | shadowsocks | G0 | 1 | 0.774603 | 0.791667 | 0.802553 | 0.318509 | 1.157839 | 0.857143 | 0.733333 |
| RawPost-small | shadowsocks | G0 | 2 | 0.635053 | 0.708333 | 1.154011 | 0.465192 | 1.664886 | 0.400000 | 0.752579 |
| RawPost-small | shadowsocks | G0 | 3 | 0.826720 | 0.833333 | 0.898361 | 0.262899 | 1.296062 | 0.875000 | 0.802579 |
| RawPost-small | shadowsocks | G0 | 4 | 0.728042 | 0.750000 | 0.971470 | 0.424705 | 1.401535 | 0.533333 | 0.825397 |
| RawPost-small | shadowsocks | G1 | 0 | 0.865079 | 0.875000 | 0.775129 | 0.247175 | 1.118275 | 0.761905 | 0.916667 |
| RawPost-small | shadowsocks | G1 | 1 | 0.836640 | 0.833333 | 0.527860 | 0.261411 | 0.761541 | 0.761905 | 0.874008 |
| RawPost-small | shadowsocks | G1 | 2 | 0.790079 | 0.791667 | 0.801101 | 0.350847 | 1.155745 | 0.833333 | 0.768452 |
| RawPost-small | shadowsocks | G1 | 3 | 0.768783 | 0.791667 | 0.807991 | 0.321422 | 1.165685 | 0.628571 | 0.838889 |
| RawPost-small | shadowsocks | G1 | 4 | 0.702742 | 0.708333 | 0.717228 | 0.380660 | 1.034742 | 0.714286 | 0.696970 |
| RawPost-small | shadowsocks | G2 | 0 | 0.694444 | 0.708333 | 1.036976 | 0.487669 | 1.496040 | 0.500000 | 0.791667 |
| RawPost-small | shadowsocks | G2 | 1 | 0.571429 | 0.625000 | 1.020968 | 0.536153 | 1.472945 | 0.200000 | 0.757143 |
| RawPost-small | shadowsocks | G2 | 2 | 0.484524 | 0.541667 | 1.410867 | 0.689559 | 2.035451 | 0.142857 | 0.655357 |
| RawPost-small | shadowsocks | G2 | 3 | 0.827778 | 0.833333 | 0.961248 | 0.355291 | 1.386788 | 0.833333 | 0.825000 |
| RawPost-small | shadowsocks | G2 | 4 | 0.753968 | 0.750000 | 0.746173 | 0.346898 | 1.076500 | 0.571429 | 0.845238 |
| RawPost-small | trojan | G0 | 0 | 0.915344 | 0.916667 | 0.313103 | 0.165142 | 0.451713 | 0.944444 | 0.900794 |
| RawPost-small | trojan | G0 | 1 | 0.915344 | 0.916667 | 0.354731 | 0.167452 | 0.511769 | 0.944444 | 0.900794 |
| RawPost-small | trojan | G0 | 2 | 0.868783 | 0.875000 | 0.358923 | 0.213840 | 0.517816 | 0.833333 | 0.886508 |
| RawPost-small | trojan | G0 | 3 | 0.784392 | 0.791667 | 0.453658 | 0.264293 | 0.654490 | 0.888889 | 0.732143 |
| RawPost-small | trojan | G0 | 4 | 0.832672 | 0.833333 | 0.391976 | 0.237086 | 0.565502 | 0.928571 | 0.784722 |
| RawPost-small | trojan | G1 | 0 | 0.874339 | 0.875000 | 0.278375 | 0.156343 | 0.401610 | 0.803571 | 0.909722 |
| RawPost-small | trojan | G1 | 1 | 0.919048 | 0.916667 | 0.539458 | 0.189173 | 0.778274 | 0.928571 | 0.914286 |
| RawPost-small | trojan | G1 | 2 | 0.830688 | 0.833333 | 0.514049 | 0.301704 | 0.741616 | 0.944444 | 0.773810 |
| RawPost-small | trojan | G1 | 3 | 0.873677 | 0.875000 | 0.384084 | 0.210289 | 0.554116 | 0.857143 | 0.881944 |
| RawPost-small | trojan | G1 | 4 | 0.915344 | 0.916667 | 0.411380 | 0.220290 | 0.593496 | 0.928571 | 0.908730 |
| RawPost-small | trojan | G2 | 0 | 0.865741 | 0.875000 | 0.369635 | 0.205064 | 0.533271 | 0.833333 | 0.881944 |
| RawPost-small | trojan | G2 | 1 | 0.915344 | 0.916667 | 0.270524 | 0.148892 | 0.390284 | 0.888889 | 0.928571 |
| RawPost-small | trojan | G2 | 2 | 0.784127 | 0.791667 | 0.461001 | 0.271950 | 0.665083 | 0.619048 | 0.866667 |
| RawPost-small | trojan | G2 | 3 | 0.784392 | 0.791667 | 0.515206 | 0.288649 | 0.743285 | 0.660714 | 0.846230 |
| RawPost-small | trojan | G2 | 4 | 0.916005 | 0.916667 | 0.326480 | 0.189136 | 0.471011 | 0.875000 | 0.936508 |
| RawPost-small | vless | G0 | 0 | 0.754930 | 0.750000 | 0.684656 | 0.349067 | 0.987750 | 0.785714 | 0.739538 |
| RawPost-small | vless | G0 | 1 | 0.787434 | 0.791667 | 0.673418 | 0.340936 | 0.971537 | 0.803571 | 0.779365 |
| RawPost-small | vless | G0 | 2 | 0.802381 | 0.791667 | 0.716975 | 0.375034 | 1.034377 | 0.857143 | 0.775000 |
| RawPost-small | vless | G0 | 3 | 0.916005 | 0.916667 | 0.291943 | 0.132141 | 0.421184 | 1.000000 | 0.874008 |
| RawPost-small | vless | G0 | 4 | 0.877381 | 0.875000 | 0.725582 | 0.255105 | 1.046793 | 0.803571 | 0.914286 |
| RawPost-small | vless | G1 | 0 | 0.790079 | 0.791667 | 0.658492 | 0.320319 | 0.950003 | 0.733333 | 0.818452 |
| RawPost-small | vless | G1 | 1 | 0.767196 | 0.791667 | 0.711611 | 0.293518 | 1.026638 | 0.628571 | 0.836508 |
| RawPost-small | vless | G1 | 2 | 0.673280 | 0.666667 | 0.865839 | 0.457682 | 1.249142 | 0.708333 | 0.655754 |
| RawPost-small | vless | G1 | 3 | 0.874339 | 0.875000 | 0.513364 | 0.182260 | 0.740627 | 0.819444 | 0.901786 |
| RawPost-small | vless | G1 | 4 | 0.873677 | 0.875000 | 0.609072 | 0.202870 | 0.878705 | 0.857143 | 0.881944 |
| RawPost-small | vless | G2 | 0 | 0.787831 | 0.791667 | 0.678403 | 0.339041 | 0.978729 | 0.833333 | 0.765079 |
| RawPost-small | vless | G2 | 1 | 0.826058 | 0.833333 | 0.486765 | 0.221779 | 0.702254 | 0.888889 | 0.794643 |
| RawPost-small | vless | G2 | 2 | 0.743567 | 0.750000 | 0.826833 | 0.421308 | 1.192868 | 0.660714 | 0.784993 |
| RawPost-small | vless | G2 | 3 | 0.874339 | 0.875000 | 0.486889 | 0.212509 | 0.702433 | 0.928571 | 0.847222 |
| RawPost-small | vless | G2 | 4 | 0.757937 | 0.750000 | 0.712489 | 0.295341 | 1.027904 | 0.803571 | 0.735119 |
| RawPost-small | vmess | G0 | 0 | 0.832672 | 0.833333 | 0.420332 | 0.210813 | 0.606412 | 0.873016 | 0.812500 |
| RawPost-small | vmess | G0 | 1 | 0.778307 | 0.791667 | 0.614107 | 0.298876 | 0.885970 | 0.857143 | 0.738889 |
| RawPost-small | vmess | G0 | 2 | 0.567100 | 0.583333 | 1.659846 | 0.573718 | 2.394651 | 0.595238 | 0.553030 |
| RawPost-small | vmess | G0 | 3 | 0.868783 | 0.875000 | 0.841443 | 0.250494 | 1.213946 | 1.000000 | 0.803175 |
| RawPost-small | vmess | G0 | 4 | 0.835714 | 0.833333 | 0.696128 | 0.259770 | 1.004300 | 0.828571 | 0.839286 |
| RawPost-small | vmess | G1 | 0 | 0.907407 | 0.916667 | 0.495574 | 0.183431 | 0.714963 | 0.833333 | 0.944444 |
| RawPost-small | vmess | G1 | 1 | 0.828042 | 0.833333 | 0.531269 | 0.277588 | 0.766459 | 0.761905 | 0.861111 |
| RawPost-small | vmess | G1 | 2 | 0.828704 | 0.833333 | 0.548390 | 0.303518 | 0.791160 | 0.708333 | 0.888889 |
| RawPost-small | vmess | G1 | 3 | 0.795635 | 0.791667 | 0.864750 | 0.273280 | 1.247571 | 0.708333 | 0.839286 |
| RawPost-small | vmess | G1 | 4 | 0.876720 | 0.875000 | 0.708128 | 0.212103 | 1.021613 | 0.857143 | 0.886508 |
| RawPost-small | vmess | G2 | 0 | 0.781481 | 0.791667 | 0.416419 | 0.251127 | 0.600766 | 0.714286 | 0.815079 |
| RawPost-small | vmess | G2 | 1 | 0.686243 | 0.708333 | 1.234182 | 0.442518 | 1.780548 | 0.642857 | 0.707937 |
| RawPost-small | vmess | G2 | 2 | 0.706481 | 0.750000 | 0.968170 | 0.440061 | 1.396775 | 0.500000 | 0.809722 |
| RawPost-small | vmess | G2 | 3 | 0.809524 | 0.833333 | 0.919193 | 0.285702 | 1.326116 | 0.628571 | 0.900000 |
| RawPost-small | vmess | G2 | 4 | 0.727778 | 0.750000 | 0.892943 | 0.370622 | 1.288245 | 0.700000 | 0.741667 |
| RawPre-small | shadowsocks | G0 | 0 | 0.835714 | 0.833333 | 0.385337 | 0.224308 | 0.555924 | 0.928571 | 0.789286 |
| RawPre-small | shadowsocks | G0 | 1 | 0.770899 | 0.791667 | 0.889795 | 0.322963 | 1.283702 | 0.873016 | 0.719841 |
| RawPre-small | shadowsocks | G0 | 2 | 0.716534 | 0.750000 | 0.950187 | 0.410929 | 1.370830 | 0.644444 | 0.752579 |
| RawPre-small | shadowsocks | G0 | 3 | 0.848148 | 0.875000 | 0.691863 | 0.200917 | 0.998148 | 1.000000 | 0.772222 |
| RawPre-small | shadowsocks | G0 | 4 | 0.782588 | 0.791667 | 0.778507 | 0.378668 | 1.123148 | 0.666667 | 0.840548 |
| RawPre-small | shadowsocks | G1 | 0 | 0.877381 | 0.875000 | 0.807693 | 0.263277 | 1.165255 | 0.803571 | 0.914286 |
| RawPre-small | shadowsocks | G1 | 1 | 0.836640 | 0.833333 | 0.578165 | 0.274719 | 0.834116 | 0.761905 | 0.874008 |
| RawPre-small | shadowsocks | G1 | 2 | 0.787037 | 0.791667 | 0.772440 | 0.354917 | 1.114395 | 0.833333 | 0.763889 |
| RawPre-small | shadowsocks | G1 | 3 | 0.805820 | 0.833333 | 0.720111 | 0.262432 | 1.038900 | 0.628571 | 0.894444 |
| RawPre-small | shadowsocks | G1 | 4 | 0.746609 | 0.750000 | 0.719577 | 0.394982 | 1.038131 | 0.714286 | 0.762771 |
| RawPre-small | shadowsocks | G2 | 0 | 0.736291 | 0.750000 | 1.029544 | 0.442634 | 1.485318 | 0.595238 | 0.806818 |
| RawPre-small | shadowsocks | G2 | 1 | 0.697403 | 0.750000 | 0.821293 | 0.409862 | 1.184875 | 0.500000 | 0.796104 |
| RawPre-small | shadowsocks | G2 | 2 | 0.633333 | 0.666667 | 0.970728 | 0.458526 | 1.400464 | 0.366667 | 0.766667 |
| RawPre-small | shadowsocks | G2 | 3 | 0.831746 | 0.833333 | 0.703745 | 0.283915 | 1.015289 | 0.833333 | 0.830952 |
| RawPre-small | shadowsocks | G2 | 4 | 0.744228 | 0.750000 | 0.664312 | 0.354950 | 0.958400 | 0.660714 | 0.785985 |
| RawPre-small | trojan | G0 | 0 | 0.915344 | 0.916667 | 0.331615 | 0.175481 | 0.478419 | 0.944444 | 0.900794 |
| RawPre-small | trojan | G0 | 1 | 0.915344 | 0.916667 | 0.361214 | 0.161590 | 0.521122 | 0.944444 | 0.900794 |
| RawPre-small | trojan | G0 | 2 | 0.818519 | 0.833333 | 0.366915 | 0.217812 | 0.529347 | 0.833333 | 0.811111 |
| RawPre-small | trojan | G0 | 3 | 0.781746 | 0.791667 | 0.515364 | 0.292899 | 0.743513 | 0.888889 | 0.728175 |
| RawPre-small | trojan | G0 | 4 | 0.832672 | 0.833333 | 0.362958 | 0.224957 | 0.523638 | 0.928571 | 0.784722 |
| RawPre-small | trojan | G1 | 0 | 0.874339 | 0.875000 | 0.265686 | 0.147870 | 0.383304 | 0.803571 | 0.909722 |
| RawPre-small | trojan | G1 | 1 | 0.919048 | 0.916667 | 0.438621 | 0.197792 | 0.632796 | 0.857143 | 0.950000 |
| RawPre-small | trojan | G1 | 2 | 0.777778 | 0.791667 | 0.433917 | 0.269701 | 0.626011 | 0.888889 | 0.722222 |
| RawPre-small | trojan | G1 | 3 | 0.825397 | 0.833333 | 0.413083 | 0.227169 | 0.595952 | 0.857143 | 0.809524 |
| RawPre-small | trojan | G1 | 4 | 0.915344 | 0.916667 | 0.342637 | 0.203075 | 0.494321 | 0.928571 | 0.908730 |
| RawPre-small | trojan | G2 | 0 | 0.827116 | 0.833333 | 0.418333 | 0.238770 | 0.603527 | 0.761905 | 0.859722 |
| RawPre-small | trojan | G2 | 1 | 0.916005 | 0.916667 | 0.334915 | 0.148001 | 0.483180 | 1.000000 | 0.874008 |
| RawPre-small | trojan | G2 | 2 | 0.779497 | 0.791667 | 0.433501 | 0.257223 | 0.625409 | 0.619048 | 0.859722 |
| RawPre-small | trojan | G2 | 3 | 0.740741 | 0.750000 | 0.563880 | 0.307122 | 0.813507 | 0.625000 | 0.798611 |
| RawPre-small | trojan | G2 | 4 | 0.957672 | 0.958333 | 0.323424 | 0.185826 | 0.466603 | 0.944444 | 0.964286 |
| RawPre-small | vless | G0 | 0 | 0.749206 | 0.750000 | 0.743284 | 0.370191 | 1.072332 | 0.785714 | 0.730952 |
| RawPre-small | vless | G0 | 1 | 0.742857 | 0.750000 | 0.677657 | 0.341535 | 0.977652 | 0.714286 | 0.757143 |
| RawPre-small | vless | G0 | 2 | 0.836640 | 0.833333 | 0.703433 | 0.387164 | 1.014840 | 0.857143 | 0.826389 |
| RawPre-small | vless | G0 | 3 | 0.916005 | 0.916667 | 0.262481 | 0.114203 | 0.378679 | 1.000000 | 0.874008 |
| RawPre-small | vless | G0 | 4 | 0.877381 | 0.875000 | 0.710052 | 0.263994 | 1.024389 | 0.803571 | 0.914286 |
| RawPre-small | vless | G1 | 0 | 0.748413 | 0.750000 | 0.745809 | 0.357430 | 1.075975 | 0.650000 | 0.797619 |
| RawPre-small | vless | G1 | 1 | 0.767196 | 0.791667 | 0.760246 | 0.310214 | 1.096803 | 0.628571 | 0.836508 |
| RawPre-small | vless | G1 | 2 | 0.673280 | 0.666667 | 0.815269 | 0.465949 | 1.176185 | 0.708333 | 0.655754 |
| RawPre-small | vless | G1 | 3 | 0.874339 | 0.875000 | 0.465922 | 0.158823 | 0.672184 | 0.875000 | 0.874008 |
| RawPre-small | vless | G1 | 4 | 0.873677 | 0.875000 | 0.614086 | 0.196583 | 0.885939 | 0.857143 | 0.881944 |
| RawPre-small | vless | G2 | 0 | 0.749206 | 0.750000 | 0.744272 | 0.385842 | 1.073758 | 0.761905 | 0.742857 |
| RawPre-small | vless | G2 | 1 | 0.826058 | 0.833333 | 0.492868 | 0.217842 | 0.711059 | 0.888889 | 0.794643 |
| RawPre-small | vless | G2 | 2 | 0.676190 | 0.666667 | 0.858481 | 0.483165 | 1.238527 | 0.585714 | 0.721429 |
| RawPre-small | vless | G2 | 3 | 0.916005 | 0.916667 | 0.421172 | 0.180135 | 0.607623 | 0.873016 | 0.937500 |
| RawPre-small | vless | G2 | 4 | 0.794974 | 0.791667 | 0.677483 | 0.272789 | 0.977402 | 0.803571 | 0.790675 |
| RawPre-small | vmess | G0 | 0 | 0.867725 | 0.875000 | 0.434058 | 0.210022 | 0.626213 | 0.873016 | 0.865079 |
| RawPre-small | vmess | G0 | 1 | 0.741270 | 0.750000 | 0.604602 | 0.313518 | 0.872256 | 0.857143 | 0.683333 |
| RawPre-small | vmess | G0 | 2 | 0.523413 | 0.541667 | 1.490581 | 0.538485 | 2.150453 | 0.595238 | 0.487500 |
| RawPre-small | vmess | G0 | 3 | 0.785233 | 0.791667 | 0.819119 | 0.259080 | 1.181739 | 0.833333 | 0.761183 |
| RawPre-small | vmess | G0 | 4 | 0.835714 | 0.833333 | 0.720744 | 0.266673 | 1.039814 | 0.828571 | 0.839286 |
| RawPre-small | vmess | G1 | 0 | 0.907407 | 0.916667 | 0.508705 | 0.180009 | 0.733906 | 0.833333 | 0.944444 |
| RawPre-small | vmess | G1 | 1 | 0.782407 | 0.791667 | 0.637031 | 0.310230 | 0.919042 | 0.708333 | 0.819444 |
| RawPre-small | vmess | G1 | 2 | 0.828704 | 0.833333 | 0.611319 | 0.302710 | 0.881947 | 0.708333 | 0.888889 |
| RawPre-small | vmess | G1 | 3 | 0.795635 | 0.791667 | 0.801118 | 0.246139 | 1.155769 | 0.708333 | 0.839286 |
| RawPre-small | vmess | G1 | 4 | 0.876720 | 0.875000 | 0.724876 | 0.218728 | 1.045774 | 0.857143 | 0.886508 |
| RawPre-small | vmess | G2 | 0 | 0.829101 | 0.833333 | 0.356563 | 0.208020 | 0.514411 | 0.857143 | 0.815079 |
| RawPre-small | vmess | G2 | 1 | 0.686243 | 0.708333 | 1.298357 | 0.411526 | 1.873133 | 0.642857 | 0.707937 |
| RawPre-small | vmess | G2 | 2 | 0.773148 | 0.791667 | 0.963519 | 0.396337 | 1.390064 | 0.666667 | 0.826389 |
| RawPre-small | vmess | G2 | 3 | 0.809524 | 0.833333 | 0.879546 | 0.290675 | 1.268917 | 0.628571 | 0.900000 |
| RawPre-small | vmess | G2 | 4 | 0.790079 | 0.791667 | 0.856919 | 0.363750 | 1.236273 | 0.833333 | 0.768452 |
| S | shadowsocks | G0 | 0 | 0.841450 | 0.833333 | 0.440739 | 0.255382 | 0.635852 | 0.857143 | 0.833604 |
| S | shadowsocks | G0 | 1 | 0.774603 | 0.791667 | 0.813660 | 0.321727 | 1.173863 | 0.857143 | 0.733333 |
| S | shadowsocks | G0 | 2 | 0.635053 | 0.708333 | 1.158501 | 0.466025 | 1.671363 | 0.400000 | 0.752579 |
| S | shadowsocks | G0 | 3 | 0.826720 | 0.833333 | 0.900484 | 0.263456 | 1.299123 | 0.875000 | 0.802579 |
| S | shadowsocks | G0 | 4 | 0.728042 | 0.750000 | 0.971594 | 0.426195 | 1.401714 | 0.533333 | 0.825397 |
| S | shadowsocks | G1 | 0 | 0.865079 | 0.875000 | 0.783844 | 0.248230 | 1.130847 | 0.761905 | 0.916667 |
| S | shadowsocks | G1 | 1 | 0.836640 | 0.833333 | 0.527269 | 0.260026 | 0.760689 | 0.761905 | 0.874008 |
| S | shadowsocks | G1 | 2 | 0.790079 | 0.791667 | 0.802268 | 0.350444 | 1.157428 | 0.833333 | 0.768452 |
| S | shadowsocks | G1 | 3 | 0.722222 | 0.750000 | 0.808231 | 0.320799 | 1.166030 | 0.533333 | 0.816667 |
| S | shadowsocks | G1 | 4 | 0.702742 | 0.708333 | 0.718567 | 0.384229 | 1.036673 | 0.714286 | 0.696970 |
| S | shadowsocks | G2 | 0 | 0.694444 | 0.708333 | 1.044395 | 0.488614 | 1.506743 | 0.500000 | 0.791667 |
| S | shadowsocks | G2 | 1 | 0.571429 | 0.625000 | 1.022656 | 0.537885 | 1.475381 | 0.200000 | 0.757143 |
| S | shadowsocks | G2 | 2 | 0.484524 | 0.541667 | 1.416834 | 0.691490 | 2.044059 | 0.142857 | 0.655357 |
| S | shadowsocks | G2 | 3 | 0.827778 | 0.833333 | 0.958801 | 0.353135 | 1.383258 | 0.833333 | 0.825000 |
| S | shadowsocks | G2 | 4 | 0.753968 | 0.750000 | 0.743137 | 0.346318 | 1.072120 | 0.571429 | 0.845238 |
| S | trojan | G0 | 0 | 0.915344 | 0.916667 | 0.316601 | 0.166678 | 0.456758 | 0.944444 | 0.900794 |
| S | trojan | G0 | 1 | 0.915344 | 0.916667 | 0.358469 | 0.168140 | 0.517162 | 0.944444 | 0.900794 |
| S | trojan | G0 | 2 | 0.868783 | 0.875000 | 0.356769 | 0.212508 | 0.514709 | 0.833333 | 0.886508 |
| S | trojan | G0 | 3 | 0.784392 | 0.791667 | 0.450550 | 0.264504 | 0.650007 | 0.888889 | 0.732143 |
| S | trojan | G0 | 4 | 0.832672 | 0.833333 | 0.391123 | 0.236858 | 0.564272 | 0.928571 | 0.784722 |
| S | trojan | G1 | 0 | 0.874339 | 0.875000 | 0.278787 | 0.156368 | 0.402205 | 0.803571 | 0.909722 |
| S | trojan | G1 | 1 | 0.919048 | 0.916667 | 0.543539 | 0.189025 | 0.784161 | 0.928571 | 0.914286 |
| S | trojan | G1 | 2 | 0.830688 | 0.833333 | 0.515054 | 0.303101 | 0.743066 | 0.944444 | 0.773810 |
| S | trojan | G1 | 3 | 0.873677 | 0.875000 | 0.382418 | 0.209032 | 0.551713 | 0.857143 | 0.881944 |
| S | trojan | G1 | 4 | 0.915344 | 0.916667 | 0.408417 | 0.219574 | 0.589222 | 0.928571 | 0.908730 |
| S | trojan | G2 | 0 | 0.865741 | 0.875000 | 0.372098 | 0.207034 | 0.536824 | 0.833333 | 0.881944 |
| S | trojan | G2 | 1 | 0.915344 | 0.916667 | 0.276294 | 0.151772 | 0.398609 | 0.888889 | 0.928571 |
| S | trojan | G2 | 2 | 0.784127 | 0.791667 | 0.464700 | 0.274186 | 0.670421 | 0.619048 | 0.866667 |
| S | trojan | G2 | 3 | 0.784392 | 0.791667 | 0.513590 | 0.288086 | 0.740953 | 0.660714 | 0.846230 |
| S | trojan | G2 | 4 | 0.916005 | 0.916667 | 0.326284 | 0.189009 | 0.470728 | 0.875000 | 0.936508 |
| S | vless | G0 | 0 | 0.754930 | 0.750000 | 0.683289 | 0.347713 | 0.985778 | 0.785714 | 0.739538 |
| S | vless | G0 | 1 | 0.787434 | 0.791667 | 0.682205 | 0.341960 | 0.984214 | 0.803571 | 0.779365 |
| S | vless | G0 | 2 | 0.756746 | 0.750000 | 0.716803 | 0.376796 | 1.034128 | 0.761905 | 0.754167 |
| S | vless | G0 | 3 | 0.916005 | 0.916667 | 0.293534 | 0.132173 | 0.423479 | 1.000000 | 0.874008 |
| S | vless | G0 | 4 | 0.877381 | 0.875000 | 0.721234 | 0.253667 | 1.040521 | 0.803571 | 0.914286 |
| S | vless | G1 | 0 | 0.790079 | 0.791667 | 0.658470 | 0.319920 | 0.949971 | 0.733333 | 0.818452 |
| S | vless | G1 | 1 | 0.767196 | 0.791667 | 0.716419 | 0.294478 | 1.033575 | 0.628571 | 0.836508 |
| S | vless | G1 | 2 | 0.673280 | 0.666667 | 0.849921 | 0.453918 | 1.226177 | 0.708333 | 0.655754 |
| S | vless | G1 | 3 | 0.874339 | 0.875000 | 0.514973 | 0.183101 | 0.742949 | 0.875000 | 0.874008 |
| S | vless | G1 | 4 | 0.873677 | 0.875000 | 0.612155 | 0.205797 | 0.883153 | 0.857143 | 0.881944 |
| S | vless | G2 | 0 | 0.787831 | 0.791667 | 0.677247 | 0.339393 | 0.977061 | 0.833333 | 0.765079 |
| S | vless | G2 | 1 | 0.826058 | 0.833333 | 0.485366 | 0.222004 | 0.700234 | 0.888889 | 0.794643 |
| S | vless | G2 | 2 | 0.743567 | 0.750000 | 0.823879 | 0.419464 | 1.188607 | 0.660714 | 0.784993 |
| S | vless | G2 | 3 | 0.874339 | 0.875000 | 0.490625 | 0.212995 | 0.707822 | 0.928571 | 0.847222 |
| S | vless | G2 | 4 | 0.757937 | 0.750000 | 0.710873 | 0.295445 | 1.025573 | 0.803571 | 0.735119 |
| S | vmess | G0 | 0 | 0.832672 | 0.833333 | 0.420336 | 0.211746 | 0.606417 | 0.873016 | 0.812500 |
| S | vmess | G0 | 1 | 0.778307 | 0.791667 | 0.613581 | 0.298838 | 0.885210 | 0.857143 | 0.738889 |
| S | vmess | G0 | 2 | 0.567100 | 0.583333 | 1.678055 | 0.574303 | 2.420922 | 0.595238 | 0.553030 |
| S | vmess | G0 | 3 | 0.868783 | 0.875000 | 0.832990 | 0.246527 | 1.201750 | 1.000000 | 0.803175 |
| S | vmess | G0 | 4 | 0.835714 | 0.833333 | 0.697858 | 0.261445 | 1.006797 | 0.828571 | 0.839286 |
| S | vmess | G1 | 0 | 0.907407 | 0.916667 | 0.493011 | 0.185163 | 0.711264 | 0.833333 | 0.944444 |
| S | vmess | G1 | 1 | 0.828042 | 0.833333 | 0.522460 | 0.273116 | 0.753751 | 0.761905 | 0.861111 |
| S | vmess | G1 | 2 | 0.828704 | 0.833333 | 0.545520 | 0.303474 | 0.787019 | 0.708333 | 0.888889 |
| S | vmess | G1 | 3 | 0.795635 | 0.791667 | 0.865684 | 0.275559 | 1.248918 | 0.708333 | 0.839286 |
| S | vmess | G1 | 4 | 0.876720 | 0.875000 | 0.704257 | 0.208945 | 1.016029 | 0.857143 | 0.886508 |
| S | vmess | G2 | 0 | 0.781481 | 0.791667 | 0.414995 | 0.249447 | 0.598712 | 0.714286 | 0.815079 |
| S | vmess | G2 | 1 | 0.686243 | 0.708333 | 1.232840 | 0.440531 | 1.778611 | 0.642857 | 0.707937 |
| S | vmess | G2 | 2 | 0.706481 | 0.750000 | 0.972225 | 0.442069 | 1.402624 | 0.500000 | 0.809722 |
| S | vmess | G2 | 3 | 0.809524 | 0.833333 | 0.913365 | 0.284916 | 1.317707 | 0.628571 | 0.900000 |
| S | vmess | G2 | 4 | 0.727778 | 0.750000 | 0.896819 | 0.372266 | 1.293837 | 0.700000 | 0.741667 |

## 留出覆盖分项

| arm | target | group | scope | exposures | CE_nats | Brier | accuracy | F1_full_six_class_CM |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| G-small | shadowsocks | G0 | C | 80 | 0.747219 | 0.293357 | 0.812500 | 0.785193 |
| G-small | shadowsocks | G0 | U | 40 | 0.850777 | 0.377279 | 0.775000 | 0.836765 |
| G-small | shadowsocks | G1 | C | 80 | 0.422218 | 0.205099 | 0.850000 | 0.794201 |
| G-small | shadowsocks | G1 | U | 40 | 1.770326 | 0.589615 | 0.600000 | 0.704861 |
| G-small | shadowsocks | G2 | C | 80 | 0.616091 | 0.245252 | 0.837500 | 0.783061 |
| G-small | shadowsocks | G2 | U | 40 | 1.327522 | 0.659805 | 0.525000 | 0.605405 |
| G-small | trojan | G0 | C | 80 | 0.490086 | 0.271565 | 0.825000 | 0.830289 |
| G-small | trojan | G0 | U | 40 | 0.204053 | 0.120335 | 0.925000 | 0.912805 |
| G-small | trojan | G1 | C | 80 | 0.324363 | 0.180317 | 0.887500 | 0.877193 |
| G-small | trojan | G1 | U | 40 | 0.583347 | 0.269509 | 0.875000 | 0.897436 |
| G-small | trojan | G2 | C | 80 | 0.273396 | 0.151894 | 0.900000 | 0.882781 |
| G-small | trojan | G2 | U | 40 | 0.601823 | 0.346894 | 0.775000 | 0.804993 |
| G-small | vless | G0 | C | 80 | 0.542837 | 0.266004 | 0.825000 | 0.806097 |
| G-small | vless | G0 | U | 40 | 0.642369 | 0.302674 | 0.800000 | 0.841303 |
| G-small | vless | G1 | C | 80 | 0.514739 | 0.248650 | 0.850000 | 0.845122 |
| G-small | vless | G1 | U | 40 | 0.982819 | 0.387386 | 0.775000 | 0.781130 |
| G-small | vless | G2 | C | 80 | 0.656181 | 0.295635 | 0.800000 | 0.799762 |
| G-small | vless | G2 | U | 40 | 0.544130 | 0.280495 | 0.825000 | 0.833761 |
| G-small | vmess | G0 | C | 80 | 1.015405 | 0.328335 | 0.787500 | 0.779111 |
| G-small | vmess | G0 | U | 40 | 0.383846 | 0.214301 | 0.850000 | 0.871457 |
| G-small | vmess | G1 | C | 80 | 0.414392 | 0.148335 | 0.900000 | 0.887850 |
| G-small | vmess | G1 | U | 40 | 1.121402 | 0.433976 | 0.750000 | 0.768622 |
| G-small | vmess | G2 | C | 80 | 0.522698 | 0.225812 | 0.862500 | 0.798700 |
| G-small | vmess | G2 | U | 40 | 1.500533 | 0.584643 | 0.600000 | 0.680581 |
| Marginal-small | shadowsocks | G0 | C | 80 | 0.680390 | 0.270615 | 0.837500 | 0.794034 |
| Marginal-small | shadowsocks | G0 | U | 40 | 0.893493 | 0.409075 | 0.700000 | 0.785256 |
| Marginal-small | shadowsocks | G1 | C | 80 | 0.444795 | 0.215400 | 0.862500 | 0.804307 |
| Marginal-small | shadowsocks | G1 | U | 40 | 1.399638 | 0.579459 | 0.600000 | 0.704861 |
| Marginal-small | shadowsocks | G2 | C | 80 | 0.636940 | 0.283267 | 0.800000 | 0.756505 |
| Marginal-small | shadowsocks | G2 | U | 40 | 1.210340 | 0.635550 | 0.525000 | 0.588285 |
| Marginal-small | trojan | G0 | C | 80 | 0.459620 | 0.249801 | 0.837500 | 0.841693 |
| Marginal-small | trojan | G0 | U | 40 | 0.221138 | 0.126052 | 0.925000 | 0.912805 |
| Marginal-small | trojan | G1 | C | 80 | 0.384171 | 0.194586 | 0.875000 | 0.865161 |
| Marginal-small | trojan | G1 | U | 40 | 0.568307 | 0.292262 | 0.825000 | 0.847368 |
| Marginal-small | trojan | G2 | C | 80 | 0.307282 | 0.152273 | 0.900000 | 0.873664 |
| Marginal-small | trojan | G2 | U | 40 | 0.677183 | 0.370155 | 0.750000 | 0.799431 |
| Marginal-small | vless | G0 | C | 80 | 0.591464 | 0.280307 | 0.862500 | 0.830919 |
| Marginal-small | vless | G0 | U | 40 | 0.596787 | 0.296034 | 0.800000 | 0.864035 |
| Marginal-small | vless | G1 | C | 80 | 0.505550 | 0.237575 | 0.837500 | 0.823547 |
| Marginal-small | vless | G1 | U | 40 | 1.138860 | 0.417414 | 0.725000 | 0.749324 |
| Marginal-small | vless | G2 | C | 80 | 0.670040 | 0.298186 | 0.825000 | 0.819668 |
| Marginal-small | vless | G2 | U | 40 | 0.572993 | 0.295729 | 0.825000 | 0.844737 |
| Marginal-small | vmess | G0 | C | 80 | 0.980103 | 0.335749 | 0.775000 | 0.754181 |
| Marginal-small | vmess | G0 | U | 40 | 0.448973 | 0.250531 | 0.800000 | 0.850000 |
| Marginal-small | vmess | G1 | C | 80 | 0.370028 | 0.150920 | 0.887500 | 0.852928 |
| Marginal-small | vmess | G1 | U | 40 | 1.195727 | 0.486301 | 0.675000 | 0.737557 |
| Marginal-small | vmess | G2 | C | 80 | 0.538166 | 0.224865 | 0.850000 | 0.791454 |
| Marginal-small | vmess | G2 | U | 40 | 1.588685 | 0.611838 | 0.575000 | 0.640351 |
| P-small | shadowsocks | G0 | C | 80 | 0.736127 | 0.295981 | 0.812500 | 0.789071 |
| P-small | shadowsocks | G0 | U | 40 | 0.769028 | 0.356322 | 0.800000 | 0.853571 |
| P-small | shadowsocks | G1 | C | 80 | 0.430062 | 0.207661 | 0.850000 | 0.789072 |
| P-small | shadowsocks | G1 | U | 40 | 1.510471 | 0.594540 | 0.575000 | 0.683692 |
| P-small | shadowsocks | G2 | C | 80 | 0.591342 | 0.237810 | 0.850000 | 0.790066 |
| P-small | shadowsocks | G2 | U | 40 | 1.303936 | 0.651995 | 0.525000 | 0.612302 |
| P-small | trojan | G0 | C | 80 | 0.487349 | 0.266445 | 0.850000 | 0.855261 |
| P-small | trojan | G0 | U | 40 | 0.201391 | 0.117039 | 0.925000 | 0.912805 |
| P-small | trojan | G1 | C | 80 | 0.335559 | 0.183474 | 0.900000 | 0.889552 |
| P-small | trojan | G1 | U | 40 | 0.552946 | 0.273461 | 0.875000 | 0.897436 |
| P-small | trojan | G2 | C | 80 | 0.257265 | 0.142176 | 0.912500 | 0.890098 |
| P-small | trojan | G2 | U | 40 | 0.639601 | 0.355755 | 0.775000 | 0.815789 |
| P-small | vless | G0 | C | 80 | 0.539706 | 0.262907 | 0.837500 | 0.815654 |
| P-small | vless | G0 | U | 40 | 0.781774 | 0.307839 | 0.800000 | 0.852774 |
| P-small | vless | G1 | C | 80 | 0.496333 | 0.246011 | 0.850000 | 0.840244 |
| P-small | vless | G1 | U | 40 | 0.943754 | 0.380547 | 0.750000 | 0.767105 |
| P-small | vless | G2 | C | 80 | 0.648290 | 0.293897 | 0.787500 | 0.793522 |
| P-small | vless | G2 | U | 40 | 0.541080 | 0.281080 | 0.825000 | 0.823640 |
| P-small | vmess | G0 | C | 80 | 0.961887 | 0.330155 | 0.787500 | 0.779111 |
| P-small | vmess | G0 | U | 40 | 0.395305 | 0.223887 | 0.850000 | 0.871457 |
| P-small | vmess | G1 | C | 80 | 0.357487 | 0.137112 | 0.912500 | 0.885497 |
| P-small | vmess | G1 | U | 40 | 1.153423 | 0.465123 | 0.725000 | 0.773115 |
| P-small | vmess | G2 | C | 80 | 0.522381 | 0.223310 | 0.875000 | 0.819403 |
| P-small | vmess | G2 | U | 40 | 1.543458 | 0.591728 | 0.625000 | 0.699491 |
| RawPost-small | shadowsocks | G0 | C | 80 | 0.727846 | 0.264756 | 0.850000 | 0.797298 |
| RawPost-small | shadowsocks | G0 | U | 40 | 1.106269 | 0.507661 | 0.650000 | 0.749576 |
| RawPost-small | shadowsocks | G1 | C | 80 | 0.362386 | 0.180433 | 0.875000 | 0.823418 |
| RawPost-small | shadowsocks | G1 | U | 40 | 1.452815 | 0.576043 | 0.650000 | 0.749155 |
| RawPost-small | shadowsocks | G2 | C | 80 | 0.645402 | 0.257309 | 0.850000 | 0.764889 |
| RawPost-small | shadowsocks | G2 | U | 40 | 1.814935 | 0.934724 | 0.375000 | 0.500000 |
| RawPost-small | trojan | G0 | C | 80 | 0.454664 | 0.252008 | 0.837500 | 0.842440 |
| RawPost-small | trojan | G0 | U | 40 | 0.214106 | 0.124672 | 0.925000 | 0.912805 |
| RawPost-small | trojan | G1 | C | 80 | 0.324299 | 0.176674 | 0.900000 | 0.878716 |
| RawPost-small | trojan | G1 | U | 40 | 0.627810 | 0.293332 | 0.850000 | 0.895357 |
| RawPost-small | trojan | G2 | C | 80 | 0.268197 | 0.149280 | 0.912500 | 0.889473 |
| RawPost-small | trojan | G2 | U | 40 | 0.629313 | 0.363653 | 0.750000 | 0.788635 |
| RawPost-small | vless | G0 | C | 80 | 0.535672 | 0.261253 | 0.837500 | 0.815654 |
| RawPost-small | vless | G0 | U | 40 | 0.784200 | 0.348864 | 0.800000 | 0.852774 |
| RawPost-small | vless | G1 | C | 80 | 0.520860 | 0.246932 | 0.825000 | 0.820708 |
| RawPost-small | vless | G1 | U | 40 | 0.973307 | 0.380126 | 0.750000 | 0.756739 |
| RawPost-small | vless | G2 | C | 80 | 0.660291 | 0.292520 | 0.800000 | 0.787594 |
| RawPost-small | vless | G2 | U | 40 | 0.594246 | 0.308947 | 0.800000 | 0.827913 |
| RawPost-small | vmess | G0 | C | 80 | 1.035679 | 0.346736 | 0.775000 | 0.760017 |
| RawPost-small | vmess | G0 | U | 40 | 0.467756 | 0.262731 | 0.800000 | 0.839024 |
| RawPost-small | vmess | G1 | C | 80 | 0.341538 | 0.125483 | 0.925000 | 0.884388 |
| RawPost-small | vmess | G1 | U | 40 | 1.205792 | 0.498987 | 0.700000 | 0.777090 |
| RawPost-small | vmess | G2 | C | 80 | 0.536999 | 0.224154 | 0.862500 | 0.798700 |
| RawPost-small | vmess | G2 | U | 40 | 1.584547 | 0.625710 | 0.575000 | 0.646098 |
| RawPre-small | shadowsocks | G0 | C | 80 | 0.670635 | 0.267047 | 0.825000 | 0.790272 |
| RawPre-small | shadowsocks | G0 | U | 40 | 0.876142 | 0.388577 | 0.775000 | 0.847662 |
| RawPre-small | shadowsocks | G1 | C | 80 | 0.380042 | 0.183831 | 0.887500 | 0.844233 |
| RawPre-small | shadowsocks | G1 | U | 40 | 1.398707 | 0.562534 | 0.675000 | 0.754386 |
| RawPre-small | shadowsocks | G2 | C | 80 | 0.600778 | 0.236955 | 0.862500 | 0.797151 |
| RawPre-small | shadowsocks | G2 | U | 40 | 1.312217 | 0.696021 | 0.525000 | 0.623563 |
| RawPre-small | trojan | G0 | C | 80 | 0.478734 | 0.260584 | 0.825000 | 0.829633 |
| RawPre-small | trojan | G0 | U | 40 | 0.205372 | 0.122474 | 0.925000 | 0.912805 |
| RawPre-small | trojan | G1 | C | 80 | 0.292590 | 0.166933 | 0.887500 | 0.865742 |
| RawPre-small | trojan | G1 | U | 40 | 0.551187 | 0.293499 | 0.825000 | 0.868421 |
| RawPre-small | trojan | G2 | C | 80 | 0.295052 | 0.152053 | 0.900000 | 0.870845 |
| RawPre-small | trojan | G2 | U | 40 | 0.654328 | 0.378060 | 0.750000 | 0.800142 |
| RawPre-small | vless | G0 | C | 80 | 0.570129 | 0.273282 | 0.850000 | 0.819811 |
| RawPre-small | vless | G0 | U | 40 | 0.717886 | 0.339689 | 0.775000 | 0.836257 |
| RawPre-small | vless | G1 | C | 80 | 0.486349 | 0.243319 | 0.825000 | 0.810584 |
| RawPre-small | vless | G1 | U | 40 | 1.068100 | 0.406760 | 0.725000 | 0.749324 |
| RawPre-small | vless | G2 | C | 80 | 0.668352 | 0.306312 | 0.800000 | 0.799071 |
| RawPre-small | vless | G2 | U | 40 | 0.579863 | 0.311239 | 0.775000 | 0.784615 |
| RawPre-small | vmess | G0 | C | 80 | 0.977672 | 0.339129 | 0.762500 | 0.736003 |
| RawPre-small | vmess | G0 | U | 40 | 0.486117 | 0.274409 | 0.750000 | 0.802661 |
| RawPre-small | vmess | G1 | C | 80 | 0.338876 | 0.127951 | 0.912500 | 0.876988 |
| RawPre-small | vmess | G1 | U | 40 | 1.292077 | 0.498787 | 0.700000 | 0.766165 |
| RawPre-small | vmess | G2 | C | 80 | 0.529644 | 0.213839 | 0.862500 | 0.808987 |
| RawPre-small | vmess | G2 | U | 40 | 1.553654 | 0.574508 | 0.650000 | 0.731749 |
| S | shadowsocks | G0 | C | 80 | 0.733467 | 0.267078 | 0.850000 | 0.797298 |
| S | shadowsocks | G0 | U | 40 | 1.104052 | 0.505514 | 0.650000 | 0.749576 |
| S | shadowsocks | G1 | C | 80 | 0.367891 | 0.183739 | 0.875000 | 0.817875 |
| S | shadowsocks | G1 | U | 40 | 1.448326 | 0.570760 | 0.625000 | 0.732639 |
| S | shadowsocks | G2 | C | 80 | 0.652378 | 0.259360 | 0.850000 | 0.764889 |
| S | shadowsocks | G2 | U | 40 | 1.806738 | 0.931745 | 0.375000 | 0.500000 |
| S | trojan | G0 | C | 80 | 0.456125 | 0.252836 | 0.837500 | 0.842440 |
| S | trojan | G0 | U | 40 | 0.211858 | 0.123541 | 0.925000 | 0.912805 |
| S | trojan | G1 | C | 80 | 0.324906 | 0.177313 | 0.900000 | 0.878716 |
| S | trojan | G1 | U | 40 | 0.627118 | 0.291635 | 0.850000 | 0.895357 |
| S | trojan | G2 | C | 80 | 0.270277 | 0.150716 | 0.912500 | 0.889473 |
| S | trojan | G2 | U | 40 | 0.631225 | 0.364619 | 0.750000 | 0.788635 |
| S | vless | G0 | C | 80 | 0.537294 | 0.261666 | 0.837500 | 0.810526 |
| S | vless | G0 | U | 40 | 0.783650 | 0.348053 | 0.775000 | 0.836257 |
| S | vless | G1 | C | 80 | 0.522028 | 0.248174 | 0.825000 | 0.814939 |
| S | vless | G1 | U | 40 | 0.967108 | 0.377981 | 0.750000 | 0.767105 |
| S | vless | G2 | C | 80 | 0.659741 | 0.292907 | 0.800000 | 0.787594 |
| S | vless | G2 | U | 40 | 0.593311 | 0.307768 | 0.800000 | 0.827913 |
| S | vmess | G0 | C | 80 | 1.041615 | 0.347629 | 0.775000 | 0.760017 |
| S | vmess | G0 | U | 40 | 0.462463 | 0.260457 | 0.800000 | 0.839024 |
| S | vmess | G1 | C | 80 | 0.344497 | 0.127711 | 0.925000 | 0.884388 |
| S | vmess | G1 | U | 40 | 1.189565 | 0.492333 | 0.700000 | 0.777090 |
| S | vmess | G2 | C | 80 | 0.538790 | 0.225277 | 0.862500 | 0.798700 |
| S | vmess | G2 | U | 40 | 1.580565 | 0.622984 | 0.575000 | 0.646098 |

## 全部内容错误翻转

| candidate | reference | content_id | label_id | exposures | unique_visits | repaired | added | changed | mean_delta_CE | mean_probability_L1 | unique_fixed_visits | unique_added_visits |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P-small | G-small | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | developer.mozilla.org::document_view | 48 | 16 | 1 | 0 | 2 | -0.014514 | 0.038946 | 1.000000 | 0.000000 |
| P-small | G-small | https://developer.mozilla.org/en-US/docs/Web/HTTP | developer.mozilla.org::document_view | 48 | 16 | 1 | 0 | 1 | 0.008060 | 0.036239 | 1.000000 | 0.000000 |
| P-small | G-small | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | developer.mozilla.org::document_view | 48 | 16 | 1 | 0 | 1 | -0.067055 | 0.043407 | 1.000000 | 0.000000 |
| P-small | G-small | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | developer.mozilla.org::document_view | 48 | 16 | 0 | 0 | 0 | -0.001035 | 0.030922 | 0.000000 | 0.000000 |
| P-small | G-small | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | developer.mozilla.org::document_view | 48 | 16 | 0 | 0 | 1 | -0.011684 | 0.043938 | 0.000000 | 0.000000 |
| P-small | G-small | https://en.wikipedia.org/wiki/Computer_network | wikipedia.org::article_view | 48 | 16 | 1 | 0 | 1 | 0.006152 | 0.053089 | 1.000000 | 0.000000 |
| P-small | G-small | https://en.wikipedia.org/wiki/Domain_Name_System | wikipedia.org::article_view | 48 | 16 | 1 | 0 | 1 | -0.008790 | 0.022012 | 1.000000 | 0.000000 |
| P-small | G-small | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | wikipedia.org::article_view | 48 | 16 | 0 | 1 | 2 | 0.003933 | 0.061343 | 0.000000 | 1.000000 |
| P-small | G-small | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | wikipedia.org::article_view | 48 | 16 | 1 | 0 | 1 | -0.078591 | 0.034685 | 1.000000 | 0.000000 |
| P-small | G-small | https://en.wikipedia.org/wiki/Transport_Layer_Security | wikipedia.org::article_view | 48 | 16 | 1 | 0 | 1 | -0.016922 | 0.041348 | 1.000000 | 0.000000 |
| P-small | G-small | https://github.com/RakuLomis/TrafficTracer | github.com::repository_view | 48 | 16 | 0 | 0 | 0 | -0.009175 | 0.011149 | 0.000000 | 0.000000 |
| P-small | G-small | https://github.com/numpy/numpy | github.com::repository_view | 48 | 16 | 1 | 0 | 1 | -0.076897 | 0.041327 | 1.000000 | 0.000000 |
| P-small | G-small | https://github.com/pallets/flask | github.com::repository_view | 48 | 16 | 0 | 0 | 0 | 0.087803 | 0.004044 | 0.000000 | 0.000000 |
| P-small | G-small | https://github.com/python/cpython | github.com::repository_view | 48 | 16 | 0 | 0 | 0 | 0.003204 | 0.009778 | 0.000000 | 0.000000 |
| P-small | G-small | https://github.com/scikit-learn/scikit-learn | github.com::repository_view | 48 | 16 | 0 | 0 | 0 | 0.019271 | 0.019628 | 0.000000 | 0.000000 |
| P-small | G-small | https://www.bing.com/search?q=beginner+guitar+chords | bing.com::search_results_view | 48 | 16 | 0 | 2 | 2 | -0.018841 | 0.041834 | 0.000000 | 1.000000 |
| P-small | G-small | https://www.bing.com/search?q=indoor+plant+care | bing.com::search_results_view | 48 | 16 | 0 | 2 | 2 | -0.050557 | 0.046587 | 0.000000 | 2.000000 |
| P-small | G-small | https://www.bing.com/search?q=network+traffic+analysis | bing.com::search_results_view | 48 | 16 | 0 | 0 | 0 | -0.009286 | 0.012343 | 0.000000 | 0.000000 |
| P-small | G-small | https://www.bing.com/search?q=solar+system+facts | bing.com::search_results_view | 48 | 16 | 0 | 0 | 1 | -0.059468 | 0.040644 | 0.000000 | 0.000000 |
| P-small | G-small | https://www.bing.com/search?q=sourdough+bread+recipe | bing.com::search_results_view | 48 | 16 | 1 | 0 | 1 | -0.208123 | 0.031404 | 1.000000 | 0.000000 |
| P-small | G-small | https://www.youtube.com/results?search_query=astronomy+documentary | youtube.com::search_results_view | 48 | 16 | 0 | 0 | 0 | -0.003386 | 0.017200 | 0.000000 | 0.000000 |
| P-small | G-small | https://www.youtube.com/results?search_query=bicycle+maintenance | youtube.com::search_results_view | 48 | 16 | 0 | 0 | 0 | 0.006947 | 0.019112 | 0.000000 | 0.000000 |
| P-small | G-small | https://www.youtube.com/results?search_query=bread+baking | youtube.com::search_results_view | 48 | 16 | 0 | 0 | 0 | -0.019647 | 0.026182 | 0.000000 | 0.000000 |
| P-small | G-small | https://www.youtube.com/results?search_query=piano+practice | youtube.com::search_results_view | 48 | 16 | 1 | 0 | 1 | 0.001165 | 0.027888 | 1.000000 | 0.000000 |
| P-small | G-small | https://www.youtube.com/results?search_query=watercolor+tutorial | youtube.com::search_results_view | 48 | 16 | 0 | 0 | 0 | 0.005501 | 0.013027 | 0.000000 | 0.000000 |
| P-small | G-small | youtube_video:R6MlUcmOul8 | youtube.com::video_playback | 48 | 16 | 0 | 0 | 0 | 0.021371 | 0.020712 | 0.000000 | 0.000000 |
| P-small | G-small | youtube_video:aircAruvnKk | youtube.com::video_playback | 48 | 16 | 1 | 0 | 1 | 0.007292 | 0.027084 | 1.000000 | 0.000000 |
| P-small | G-small | youtube_video:aqz-KE-bpKQ | youtube.com::video_playback | 48 | 16 | 0 | 0 | 0 | 0.002080 | 0.012382 | 0.000000 | 0.000000 |
| P-small | G-small | youtube_video:eRsGyueVLvQ | youtube.com::video_playback | 48 | 16 | 0 | 0 | 0 | -0.001441 | 0.005512 | 0.000000 | 0.000000 |
| P-small | G-small | youtube_video:sAWK0mgrMp4 | youtube.com::video_playback | 48 | 16 | 0 | 0 | 1 | 0.042252 | 0.023782 | 0.000000 | 0.000000 |
| P-small | Marginal-small | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | developer.mozilla.org::document_view | 48 | 16 | 0 | 0 | 2 | 0.021222 | 0.098406 | 0.000000 | 0.000000 |
| P-small | Marginal-small | https://developer.mozilla.org/en-US/docs/Web/HTTP | developer.mozilla.org::document_view | 48 | 16 | 0 | 0 | 1 | 0.007024 | 0.129625 | 0.000000 | 0.000000 |
| P-small | Marginal-small | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | developer.mozilla.org::document_view | 48 | 16 | 3 | 0 | 3 | -0.145190 | 0.107326 | 2.000000 | 0.000000 |
| P-small | Marginal-small | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | developer.mozilla.org::document_view | 48 | 16 | 2 | 0 | 2 | -0.043267 | 0.079498 | 1.000000 | 0.000000 |
| P-small | Marginal-small | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | developer.mozilla.org::document_view | 48 | 16 | 5 | 0 | 6 | -0.059013 | 0.148315 | 3.000000 | 0.000000 |
| P-small | Marginal-small | https://en.wikipedia.org/wiki/Computer_network | wikipedia.org::article_view | 48 | 16 | 2 | 0 | 2 | -0.026671 | 0.113870 | 2.000000 | 0.000000 |
| P-small | Marginal-small | https://en.wikipedia.org/wiki/Domain_Name_System | wikipedia.org::article_view | 48 | 16 | 3 | 0 | 3 | 0.012747 | 0.070604 | 3.000000 | 0.000000 |
| P-small | Marginal-small | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | wikipedia.org::article_view | 48 | 16 | 3 | 2 | 6 | -0.006812 | 0.146183 | 3.000000 | 2.000000 |
| P-small | Marginal-small | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | wikipedia.org::article_view | 48 | 16 | 2 | 0 | 2 | -0.281898 | 0.108704 | 2.000000 | 0.000000 |
| P-small | Marginal-small | https://en.wikipedia.org/wiki/Transport_Layer_Security | wikipedia.org::article_view | 48 | 16 | 1 | 0 | 3 | 0.159591 | 0.133238 | 1.000000 | 0.000000 |
| P-small | Marginal-small | https://github.com/RakuLomis/TrafficTracer | github.com::repository_view | 48 | 16 | 0 | 1 | 1 | 0.014107 | 0.054540 | 0.000000 | 1.000000 |
| P-small | Marginal-small | https://github.com/numpy/numpy | github.com::repository_view | 48 | 16 | 5 | 0 | 5 | -0.122527 | 0.190763 | 5.000000 | 0.000000 |
| P-small | Marginal-small | https://github.com/pallets/flask | github.com::repository_view | 48 | 16 | 0 | 0 | 0 | 0.083961 | 0.018181 | 0.000000 | 0.000000 |
| P-small | Marginal-small | https://github.com/python/cpython | github.com::repository_view | 48 | 16 | 0 | 0 | 0 | -0.020508 | 0.035738 | 0.000000 | 0.000000 |
| P-small | Marginal-small | https://github.com/scikit-learn/scikit-learn | github.com::repository_view | 48 | 16 | 1 | 1 | 3 | 0.087919 | 0.129275 | 1.000000 | 1.000000 |
| P-small | Marginal-small | https://www.bing.com/search?q=beginner+guitar+chords | bing.com::search_results_view | 48 | 16 | 0 | 1 | 3 | 0.010536 | 0.127919 | 0.000000 | 1.000000 |
| P-small | Marginal-small | https://www.bing.com/search?q=indoor+plant+care | bing.com::search_results_view | 48 | 16 | 0 | 1 | 1 | -0.180726 | 0.075695 | 0.000000 | 1.000000 |
| P-small | Marginal-small | https://www.bing.com/search?q=network+traffic+analysis | bing.com::search_results_view | 48 | 16 | 0 | 2 | 2 | 0.052210 | 0.035507 | 0.000000 | 1.000000 |
| P-small | Marginal-small | https://www.bing.com/search?q=solar+system+facts | bing.com::search_results_view | 48 | 16 | 1 | 0 | 3 | -0.099350 | 0.070793 | 1.000000 | 0.000000 |
| P-small | Marginal-small | https://www.bing.com/search?q=sourdough+bread+recipe | bing.com::search_results_view | 48 | 16 | 2 | 1 | 4 | 0.067171 | 0.114420 | 2.000000 | 1.000000 |
| P-small | Marginal-small | https://www.youtube.com/results?search_query=astronomy+documentary | youtube.com::search_results_view | 48 | 16 | 1 | 3 | 4 | 0.015618 | 0.067780 | 1.000000 | 3.000000 |
| P-small | Marginal-small | https://www.youtube.com/results?search_query=bicycle+maintenance | youtube.com::search_results_view | 48 | 16 | 1 | 1 | 2 | -0.090660 | 0.096862 | 1.000000 | 1.000000 |
| P-small | Marginal-small | https://www.youtube.com/results?search_query=bread+baking | youtube.com::search_results_view | 48 | 16 | 1 | 0 | 1 | -0.009454 | 0.051777 | 1.000000 | 0.000000 |
| P-small | Marginal-small | https://www.youtube.com/results?search_query=piano+practice | youtube.com::search_results_view | 48 | 16 | 2 | 0 | 2 | 0.023197 | 0.057428 | 2.000000 | 0.000000 |
| P-small | Marginal-small | https://www.youtube.com/results?search_query=watercolor+tutorial | youtube.com::search_results_view | 48 | 16 | 0 | 1 | 1 | -0.016471 | 0.053216 | 0.000000 | 1.000000 |
| P-small | Marginal-small | youtube_video:R6MlUcmOul8 | youtube.com::video_playback | 48 | 16 | 0 | 1 | 3 | 0.000313 | 0.152484 | 0.000000 | 1.000000 |
| P-small | Marginal-small | youtube_video:aircAruvnKk | youtube.com::video_playback | 48 | 16 | 0 | 1 | 1 | -0.021816 | 0.086450 | 0.000000 | 1.000000 |
| P-small | Marginal-small | youtube_video:aqz-KE-bpKQ | youtube.com::video_playback | 48 | 16 | 0 | 0 | 0 | 0.005051 | 0.030725 | 0.000000 | 0.000000 |
| P-small | Marginal-small | youtube_video:eRsGyueVLvQ | youtube.com::video_playback | 48 | 16 | 0 | 0 | 0 | -0.008753 | 0.020423 | 0.000000 | 0.000000 |
| P-small | Marginal-small | youtube_video:sAWK0mgrMp4 | youtube.com::video_playback | 48 | 16 | 0 | 0 | 0 | 0.084552 | 0.068833 | 0.000000 | 0.000000 |
| P-small | RawPost-small | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | developer.mozilla.org::document_view | 48 | 16 | 2 | 0 | 3 | -0.134727 | 0.120252 | 1.000000 | 0.000000 |
| P-small | RawPost-small | https://developer.mozilla.org/en-US/docs/Web/HTTP | developer.mozilla.org::document_view | 48 | 16 | 1 | 0 | 2 | -0.016470 | 0.135062 | 1.000000 | 0.000000 |
| P-small | RawPost-small | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | developer.mozilla.org::document_view | 48 | 16 | 0 | 1 | 1 | 0.096245 | 0.140459 | 0.000000 | 1.000000 |
| P-small | RawPost-small | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | developer.mozilla.org::document_view | 48 | 16 | 1 | 1 | 3 | -0.003197 | 0.110213 | 1.000000 | 1.000000 |
| P-small | RawPost-small | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | developer.mozilla.org::document_view | 48 | 16 | 4 | 1 | 6 | -0.071120 | 0.152598 | 2.000000 | 1.000000 |
| P-small | RawPost-small | https://en.wikipedia.org/wiki/Computer_network | wikipedia.org::article_view | 48 | 16 | 1 | 1 | 2 | 0.031181 | 0.108082 | 1.000000 | 1.000000 |
| P-small | RawPost-small | https://en.wikipedia.org/wiki/Domain_Name_System | wikipedia.org::article_view | 48 | 16 | 2 | 0 | 2 | -0.027274 | 0.062625 | 2.000000 | 0.000000 |
| P-small | RawPost-small | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | wikipedia.org::article_view | 48 | 16 | 1 | 2 | 3 | 0.014002 | 0.114871 | 1.000000 | 2.000000 |
| P-small | RawPost-small | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | wikipedia.org::article_view | 48 | 16 | 1 | 1 | 2 | -0.086717 | 0.063140 | 1.000000 | 1.000000 |
| P-small | RawPost-small | https://en.wikipedia.org/wiki/Transport_Layer_Security | wikipedia.org::article_view | 48 | 16 | 0 | 0 | 2 | -0.091847 | 0.079165 | 0.000000 | 0.000000 |
| P-small | RawPost-small | https://github.com/RakuLomis/TrafficTracer | github.com::repository_view | 48 | 16 | 1 | 0 | 1 | -0.032831 | 0.067339 | 1.000000 | 0.000000 |
| P-small | RawPost-small | https://github.com/numpy/numpy | github.com::repository_view | 48 | 16 | 5 | 0 | 5 | -0.334041 | 0.168272 | 4.000000 | 0.000000 |
| P-small | RawPost-small | https://github.com/pallets/flask | github.com::repository_view | 48 | 16 | 0 | 0 | 0 | 0.219953 | 0.016449 | 0.000000 | 0.000000 |
| P-small | RawPost-small | https://github.com/python/cpython | github.com::repository_view | 48 | 16 | 0 | 0 | 0 | -0.001048 | 0.020983 | 0.000000 | 0.000000 |
| P-small | RawPost-small | https://github.com/scikit-learn/scikit-learn | github.com::repository_view | 48 | 16 | 1 | 1 | 2 | -0.070665 | 0.089961 | 1.000000 | 1.000000 |
| P-small | RawPost-small | https://www.bing.com/search?q=beginner+guitar+chords | bing.com::search_results_view | 48 | 16 | 0 | 1 | 3 | -0.073540 | 0.136502 | 0.000000 | 1.000000 |
| P-small | RawPost-small | https://www.bing.com/search?q=indoor+plant+care | bing.com::search_results_view | 48 | 16 | 0 | 1 | 1 | -0.079790 | 0.078939 | 0.000000 | 1.000000 |
| P-small | RawPost-small | https://www.bing.com/search?q=network+traffic+analysis | bing.com::search_results_view | 48 | 16 | 0 | 1 | 1 | -0.035455 | 0.030994 | 0.000000 | 1.000000 |
| P-small | RawPost-small | https://www.bing.com/search?q=solar+system+facts | bing.com::search_results_view | 48 | 16 | 0 | 2 | 2 | -0.000487 | 0.068425 | 0.000000 | 2.000000 |
| P-small | RawPost-small | https://www.bing.com/search?q=sourdough+bread+recipe | bing.com::search_results_view | 48 | 16 | 0 | 0 | 0 | 0.130129 | 0.083000 | 0.000000 | 0.000000 |
| P-small | RawPost-small | https://www.youtube.com/results?search_query=astronomy+documentary | youtube.com::search_results_view | 48 | 16 | 0 | 1 | 1 | -0.031795 | 0.053042 | 0.000000 | 1.000000 |
| P-small | RawPost-small | https://www.youtube.com/results?search_query=bicycle+maintenance | youtube.com::search_results_view | 48 | 16 | 0 | 1 | 2 | 0.012993 | 0.056799 | 0.000000 | 1.000000 |
| P-small | RawPost-small | https://www.youtube.com/results?search_query=bread+baking | youtube.com::search_results_view | 48 | 16 | 2 | 0 | 3 | -0.040639 | 0.051229 | 2.000000 | 0.000000 |
| P-small | RawPost-small | https://www.youtube.com/results?search_query=piano+practice | youtube.com::search_results_view | 48 | 16 | 2 | 0 | 3 | -0.081277 | 0.068322 | 2.000000 | 0.000000 |
| P-small | RawPost-small | https://www.youtube.com/results?search_query=watercolor+tutorial | youtube.com::search_results_view | 48 | 16 | 1 | 1 | 2 | -0.031853 | 0.039086 | 1.000000 | 1.000000 |
| P-small | RawPost-small | youtube_video:R6MlUcmOul8 | youtube.com::video_playback | 48 | 16 | 2 | 0 | 2 | -0.149675 | 0.124582 | 2.000000 | 0.000000 |
| P-small | RawPost-small | youtube_video:aircAruvnKk | youtube.com::video_playback | 48 | 16 | 1 | 1 | 2 | -0.002998 | 0.096664 | 1.000000 | 1.000000 |
| P-small | RawPost-small | youtube_video:aqz-KE-bpKQ | youtube.com::video_playback | 48 | 16 | 1 | 0 | 1 | -0.030949 | 0.034405 | 1.000000 | 0.000000 |
| P-small | RawPost-small | youtube_video:eRsGyueVLvQ | youtube.com::video_playback | 48 | 16 | 3 | 0 | 3 | -0.105072 | 0.089481 | 3.000000 | 0.000000 |
| P-small | RawPost-small | youtube_video:sAWK0mgrMp4 | youtube.com::video_playback | 48 | 16 | 0 | 0 | 0 | 0.013114 | 0.084974 | 0.000000 | 0.000000 |
| P-small | RawPre-small | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | developer.mozilla.org::document_view | 48 | 16 | 0 | 0 | 2 | -0.041316 | 0.081493 | 0.000000 | 0.000000 |
| P-small | RawPre-small | https://developer.mozilla.org/en-US/docs/Web/HTTP | developer.mozilla.org::document_view | 48 | 16 | 0 | 2 | 2 | 0.226497 | 0.139138 | 0.000000 | 1.000000 |
| P-small | RawPre-small | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | developer.mozilla.org::document_view | 48 | 16 | 1 | 0 | 1 | -0.001633 | 0.079699 | 1.000000 | 0.000000 |
| P-small | RawPre-small | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | developer.mozilla.org::document_view | 48 | 16 | 0 | 2 | 2 | 0.016211 | 0.059570 | 0.000000 | 2.000000 |
| P-small | RawPre-small | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | developer.mozilla.org::document_view | 48 | 16 | 3 | 0 | 3 | 0.008585 | 0.101562 | 3.000000 | 0.000000 |
| P-small | RawPre-small | https://en.wikipedia.org/wiki/Computer_network | wikipedia.org::article_view | 48 | 16 | 2 | 0 | 2 | -0.029060 | 0.094653 | 2.000000 | 0.000000 |
| P-small | RawPre-small | https://en.wikipedia.org/wiki/Domain_Name_System | wikipedia.org::article_view | 48 | 16 | 2 | 0 | 2 | -0.039357 | 0.051489 | 2.000000 | 0.000000 |
| P-small | RawPre-small | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | wikipedia.org::article_view | 48 | 16 | 2 | 1 | 4 | -0.058955 | 0.089824 | 2.000000 | 1.000000 |
| P-small | RawPre-small | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | wikipedia.org::article_view | 48 | 16 | 1 | 0 | 1 | -0.122285 | 0.073088 | 1.000000 | 0.000000 |
| P-small | RawPre-small | https://en.wikipedia.org/wiki/Transport_Layer_Security | wikipedia.org::article_view | 48 | 16 | 3 | 0 | 6 | -0.019694 | 0.084057 | 2.000000 | 0.000000 |
| P-small | RawPre-small | https://github.com/RakuLomis/TrafficTracer | github.com::repository_view | 48 | 16 | 0 | 0 | 0 | -0.003277 | 0.021727 | 0.000000 | 0.000000 |
| P-small | RawPre-small | https://github.com/numpy/numpy | github.com::repository_view | 48 | 16 | 3 | 0 | 3 | -0.090367 | 0.111690 | 3.000000 | 0.000000 |
| P-small | RawPre-small | https://github.com/pallets/flask | github.com::repository_view | 48 | 16 | 0 | 0 | 0 | 0.053627 | 0.009925 | 0.000000 | 0.000000 |
| P-small | RawPre-small | https://github.com/python/cpython | github.com::repository_view | 48 | 16 | 2 | 0 | 2 | -0.018926 | 0.032422 | 2.000000 | 0.000000 |
| P-small | RawPre-small | https://github.com/scikit-learn/scikit-learn | github.com::repository_view | 48 | 16 | 0 | 3 | 3 | 0.009139 | 0.090532 | 0.000000 | 3.000000 |
| P-small | RawPre-small | https://www.bing.com/search?q=beginner+guitar+chords | bing.com::search_results_view | 48 | 16 | 0 | 1 | 3 | -0.015341 | 0.106911 | 0.000000 | 1.000000 |
| P-small | RawPre-small | https://www.bing.com/search?q=indoor+plant+care | bing.com::search_results_view | 48 | 16 | 0 | 0 | 0 | -0.116802 | 0.048020 | 0.000000 | 0.000000 |
| P-small | RawPre-small | https://www.bing.com/search?q=network+traffic+analysis | bing.com::search_results_view | 48 | 16 | 0 | 1 | 1 | -0.016383 | 0.027432 | 0.000000 | 1.000000 |
| P-small | RawPre-small | https://www.bing.com/search?q=solar+system+facts | bing.com::search_results_view | 48 | 16 | 0 | 2 | 2 | -0.003397 | 0.068412 | 0.000000 | 2.000000 |
| P-small | RawPre-small | https://www.bing.com/search?q=sourdough+bread+recipe | bing.com::search_results_view | 48 | 16 | 0 | 1 | 2 | 0.067367 | 0.098126 | 0.000000 | 1.000000 |
| P-small | RawPre-small | https://www.youtube.com/results?search_query=astronomy+documentary | youtube.com::search_results_view | 48 | 16 | 0 | 1 | 1 | -0.018108 | 0.045984 | 0.000000 | 1.000000 |
| P-small | RawPre-small | https://www.youtube.com/results?search_query=bicycle+maintenance | youtube.com::search_results_view | 48 | 16 | 0 | 0 | 0 | 0.019967 | 0.054609 | 0.000000 | 0.000000 |
| P-small | RawPre-small | https://www.youtube.com/results?search_query=bread+baking | youtube.com::search_results_view | 48 | 16 | 0 | 0 | 0 | 0.008688 | 0.047633 | 0.000000 | 0.000000 |
| P-small | RawPre-small | https://www.youtube.com/results?search_query=piano+practice | youtube.com::search_results_view | 48 | 16 | 1 | 0 | 1 | 0.025705 | 0.061788 | 1.000000 | 0.000000 |
| P-small | RawPre-small | https://www.youtube.com/results?search_query=watercolor+tutorial | youtube.com::search_results_view | 48 | 16 | 1 | 0 | 1 | 0.037202 | 0.029224 | 1.000000 | 0.000000 |
| P-small | RawPre-small | youtube_video:R6MlUcmOul8 | youtube.com::video_playback | 48 | 16 | 1 | 1 | 4 | 0.050409 | 0.099369 | 1.000000 | 1.000000 |
| P-small | RawPre-small | youtube_video:aircAruvnKk | youtube.com::video_playback | 48 | 16 | 3 | 1 | 4 | -0.104064 | 0.100318 | 3.000000 | 1.000000 |
| P-small | RawPre-small | youtube_video:aqz-KE-bpKQ | youtube.com::video_playback | 48 | 16 | 0 | 0 | 0 | 0.000531 | 0.024147 | 0.000000 | 0.000000 |
| P-small | RawPre-small | youtube_video:eRsGyueVLvQ | youtube.com::video_playback | 48 | 16 | 0 | 0 | 0 | -0.009465 | 0.025020 | 0.000000 | 0.000000 |
| P-small | RawPre-small | youtube_video:sAWK0mgrMp4 | youtube.com::video_playback | 48 | 16 | 1 | 0 | 1 | 0.009819 | 0.059662 | 1.000000 | 0.000000 |
| P-small | S | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | developer.mozilla.org::document_view | 48 | 16 | 2 | 0 | 3 | -0.141890 | 0.123551 | 1.000000 | 0.000000 |
| P-small | S | https://developer.mozilla.org/en-US/docs/Web/HTTP | developer.mozilla.org::document_view | 48 | 16 | 1 | 0 | 2 | -0.016229 | 0.136107 | 1.000000 | 0.000000 |
| P-small | S | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | developer.mozilla.org::document_view | 48 | 16 | 0 | 1 | 1 | 0.095697 | 0.142121 | 0.000000 | 1.000000 |
| P-small | S | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | developer.mozilla.org::document_view | 48 | 16 | 1 | 1 | 3 | -0.002014 | 0.107263 | 1.000000 | 1.000000 |
| P-small | S | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | developer.mozilla.org::document_view | 48 | 16 | 4 | 1 | 6 | -0.081836 | 0.152210 | 2.000000 | 1.000000 |
| P-small | S | https://en.wikipedia.org/wiki/Computer_network | wikipedia.org::article_view | 48 | 16 | 1 | 1 | 2 | 0.030966 | 0.108136 | 1.000000 | 1.000000 |
| P-small | S | https://en.wikipedia.org/wiki/Domain_Name_System | wikipedia.org::article_view | 48 | 16 | 2 | 0 | 2 | -0.025291 | 0.062695 | 2.000000 | 0.000000 |
| P-small | S | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | wikipedia.org::article_view | 48 | 16 | 1 | 2 | 3 | 0.017496 | 0.117106 | 1.000000 | 2.000000 |
| P-small | S | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | wikipedia.org::article_view | 48 | 16 | 1 | 1 | 2 | -0.082549 | 0.062372 | 1.000000 | 1.000000 |
| P-small | S | https://en.wikipedia.org/wiki/Transport_Layer_Security | wikipedia.org::article_view | 48 | 16 | 0 | 0 | 1 | -0.095630 | 0.080563 | 0.000000 | 0.000000 |
| P-small | S | https://github.com/RakuLomis/TrafficTracer | github.com::repository_view | 48 | 16 | 1 | 0 | 1 | -0.032143 | 0.066434 | 1.000000 | 0.000000 |
| P-small | S | https://github.com/numpy/numpy | github.com::repository_view | 48 | 16 | 5 | 0 | 5 | -0.327116 | 0.167540 | 4.000000 | 0.000000 |
| P-small | S | https://github.com/pallets/flask | github.com::repository_view | 48 | 16 | 0 | 0 | 0 | 0.214786 | 0.016459 | 0.000000 | 0.000000 |
| P-small | S | https://github.com/python/cpython | github.com::repository_view | 48 | 16 | 0 | 0 | 0 | -0.000561 | 0.020014 | 0.000000 | 0.000000 |
| P-small | S | https://github.com/scikit-learn/scikit-learn | github.com::repository_view | 48 | 16 | 1 | 1 | 2 | -0.072877 | 0.087282 | 1.000000 | 1.000000 |
| P-small | S | https://www.bing.com/search?q=beginner+guitar+chords | bing.com::search_results_view | 48 | 16 | 0 | 1 | 3 | -0.084303 | 0.136393 | 0.000000 | 1.000000 |
| P-small | S | https://www.bing.com/search?q=indoor+plant+care | bing.com::search_results_view | 48 | 16 | 0 | 1 | 1 | -0.084978 | 0.079308 | 0.000000 | 1.000000 |
| P-small | S | https://www.bing.com/search?q=network+traffic+analysis | bing.com::search_results_view | 48 | 16 | 0 | 1 | 1 | -0.034622 | 0.029981 | 0.000000 | 1.000000 |
| P-small | S | https://www.bing.com/search?q=solar+system+facts | bing.com::search_results_view | 48 | 16 | 0 | 1 | 1 | 0.001757 | 0.066216 | 0.000000 | 1.000000 |
| P-small | S | https://www.bing.com/search?q=sourdough+bread+recipe | bing.com::search_results_view | 48 | 16 | 0 | 0 | 0 | 0.125338 | 0.083253 | 0.000000 | 0.000000 |
| P-small | S | https://www.youtube.com/results?search_query=astronomy+documentary | youtube.com::search_results_view | 48 | 16 | 0 | 1 | 1 | -0.031985 | 0.051606 | 0.000000 | 1.000000 |
| P-small | S | https://www.youtube.com/results?search_query=bicycle+maintenance | youtube.com::search_results_view | 48 | 16 | 1 | 1 | 3 | 0.009278 | 0.057428 | 1.000000 | 1.000000 |
| P-small | S | https://www.youtube.com/results?search_query=bread+baking | youtube.com::search_results_view | 48 | 16 | 2 | 0 | 2 | -0.040549 | 0.048768 | 2.000000 | 0.000000 |
| P-small | S | https://www.youtube.com/results?search_query=piano+practice | youtube.com::search_results_view | 48 | 16 | 2 | 0 | 3 | -0.078466 | 0.067858 | 2.000000 | 0.000000 |
| P-small | S | https://www.youtube.com/results?search_query=watercolor+tutorial | youtube.com::search_results_view | 48 | 16 | 1 | 1 | 2 | -0.031358 | 0.036871 | 1.000000 | 1.000000 |
| P-small | S | youtube_video:R6MlUcmOul8 | youtube.com::video_playback | 48 | 16 | 2 | 0 | 2 | -0.148411 | 0.123531 | 2.000000 | 0.000000 |
| P-small | S | youtube_video:aircAruvnKk | youtube.com::video_playback | 48 | 16 | 1 | 1 | 2 | -0.001624 | 0.096474 | 1.000000 | 1.000000 |
| P-small | S | youtube_video:aqz-KE-bpKQ | youtube.com::video_playback | 48 | 16 | 1 | 0 | 1 | -0.029867 | 0.034174 | 1.000000 | 0.000000 |
| P-small | S | youtube_video:eRsGyueVLvQ | youtube.com::video_playback | 48 | 16 | 3 | 0 | 3 | -0.104844 | 0.089462 | 3.000000 | 0.000000 |
| P-small | S | youtube_video:sAWK0mgrMp4 | youtube.com::video_playback | 48 | 16 | 0 | 0 | 0 | 0.020278 | 0.085794 | 0.000000 | 0.000000 |

## 逐业务与覆盖错误翻转

| candidate | reference | label_id | scope | exposures | unique_visits | repaired | added | changed | mean_delta_CE | mean_probability_L1 | unique_fixed_visits | unique_added_visits |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P-small | G-small | bing.com::search_results_view | C | 160 | 80 | 1 | 2 | 3 | -0.037231 | 0.020417 | 1.000000 | 2.000000 |
| P-small | G-small | bing.com::search_results_view | U | 80 | 80 | 0 | 2 | 3 | -0.133304 | 0.062852 | 0.000000 | 2.000000 |
| P-small | G-small | developer.mozilla.org::document_view | C | 160 | 80 | 2 | 0 | 3 | -0.030351 | 0.039440 | 2.000000 | 0.000000 |
| P-small | G-small | developer.mozilla.org::document_view | U | 80 | 80 | 1 | 0 | 2 | 0.008967 | 0.037191 | 1.000000 | 0.000000 |
| P-small | G-small | github.com::repository_view | C | 160 | 80 | 0 | 0 | 0 | -0.002720 | 0.010863 | 0.000000 | 0.000000 |
| P-small | G-small | github.com::repository_view | U | 80 | 80 | 1 | 0 | 1 | 0.019964 | 0.029831 | 1.000000 | 0.000000 |
| P-small | G-small | wikipedia.org::article_view | C | 160 | 80 | 4 | 0 | 5 | -0.020592 | 0.034433 | 4.000000 | 0.000000 |
| P-small | G-small | wikipedia.org::article_view | U | 80 | 80 | 0 | 1 | 1 | -0.015346 | 0.058619 | 0.000000 | 1.000000 |
| P-small | G-small | youtube.com::search_results_view | C | 160 | 80 | 1 | 0 | 1 | -0.009457 | 0.017917 | 1.000000 | 0.000000 |
| P-small | G-small | youtube.com::search_results_view | U | 80 | 80 | 0 | 0 | 0 | 0.013263 | 0.026210 | 0.000000 | 0.000000 |
| P-small | G-small | youtube.com::video_playback | C | 160 | 80 | 1 | 0 | 2 | 0.012432 | 0.017279 | 1.000000 | 0.000000 |
| P-small | G-small | youtube.com::video_playback | U | 80 | 80 | 0 | 0 | 0 | 0.018067 | 0.019124 | 0.000000 | 0.000000 |
| P-small | Marginal-small | bing.com::search_results_view | C | 160 | 80 | 3 | 5 | 10 | -0.024433 | 0.076503 | 3.000000 | 4.000000 |
| P-small | Marginal-small | bing.com::search_results_view | U | 80 | 80 | 0 | 0 | 3 | -0.041230 | 0.101595 | 0.000000 | 0.000000 |
| P-small | Marginal-small | developer.mozilla.org::document_view | C | 160 | 80 | 7 | 0 | 10 | -0.028119 | 0.110467 | 5.000000 | 0.000000 |
| P-small | Marginal-small | developer.mozilla.org::document_view | U | 80 | 80 | 3 | 0 | 4 | -0.075297 | 0.116968 | 3.000000 | 0.000000 |
| P-small | Marginal-small | github.com::repository_view | C | 160 | 80 | 1 | 2 | 3 | 0.008104 | 0.072341 | 1.000000 | 2.000000 |
| P-small | Marginal-small | github.com::repository_view | U | 80 | 80 | 5 | 0 | 6 | 0.009562 | 0.112416 | 5.000000 | 0.000000 |
| P-small | Marginal-small | wikipedia.org::article_view | C | 160 | 80 | 6 | 1 | 8 | -0.028043 | 0.105841 | 6.000000 | 1.000000 |
| P-small | Marginal-small | wikipedia.org::article_view | U | 80 | 80 | 5 | 1 | 8 | -0.029739 | 0.131878 | 5.000000 | 1.000000 |
| P-small | Marginal-small | youtube.com::search_results_view | C | 160 | 80 | 2 | 3 | 5 | -0.015327 | 0.056059 | 2.000000 | 3.000000 |
| P-small | Marginal-small | youtube.com::search_results_view | U | 80 | 80 | 3 | 2 | 5 | -0.016009 | 0.084120 | 3.000000 | 2.000000 |
| P-small | Marginal-small | youtube.com::video_playback | C | 160 | 80 | 0 | 2 | 3 | -0.014563 | 0.063757 | 0.000000 | 2.000000 |
| P-small | Marginal-small | youtube.com::video_playback | U | 80 | 80 | 0 | 0 | 1 | 0.064734 | 0.087836 | 0.000000 | 0.000000 |
| P-small | RawPost-small | bing.com::search_results_view | C | 160 | 80 | 0 | 3 | 4 | -0.025173 | 0.069739 | 0.000000 | 3.000000 |
| P-small | RawPost-small | bing.com::search_results_view | U | 80 | 80 | 0 | 2 | 3 | 0.014860 | 0.099239 | 0.000000 | 2.000000 |
| P-small | RawPost-small | developer.mozilla.org::document_view | C | 160 | 80 | 4 | 3 | 8 | 0.016554 | 0.108418 | 4.000000 | 3.000000 |
| P-small | RawPost-small | developer.mozilla.org::document_view | U | 80 | 80 | 4 | 0 | 7 | -0.110670 | 0.178315 | 4.000000 | 0.000000 |
| P-small | RawPost-small | github.com::repository_view | C | 160 | 80 | 1 | 1 | 2 | 0.001170 | 0.046764 | 1.000000 | 1.000000 |
| P-small | RawPost-small | github.com::repository_view | U | 80 | 80 | 6 | 0 | 6 | -0.133519 | 0.124274 | 6.000000 | 0.000000 |
| P-small | RawPost-small | wikipedia.org::article_view | C | 160 | 80 | 3 | 3 | 6 | -0.015984 | 0.077554 | 3.000000 | 3.000000 |
| P-small | RawPost-small | wikipedia.org::article_view | U | 80 | 80 | 2 | 1 | 5 | -0.064425 | 0.101621 | 2.000000 | 1.000000 |
| P-small | RawPost-small | youtube.com::search_results_view | C | 160 | 80 | 3 | 3 | 8 | -0.012323 | 0.037367 | 3.000000 | 3.000000 |
| P-small | RawPost-small | youtube.com::search_results_view | U | 80 | 80 | 2 | 0 | 3 | -0.078898 | 0.086353 | 2.000000 | 0.000000 |
| P-small | RawPost-small | youtube.com::video_playback | C | 160 | 80 | 1 | 1 | 2 | 0.010733 | 0.055933 | 1.000000 | 1.000000 |
| P-small | RawPost-small | youtube.com::video_playback | U | 80 | 80 | 6 | 0 | 6 | -0.186813 | 0.146198 | 6.000000 | 0.000000 |
| P-small | RawPre-small | bing.com::search_results_view | C | 160 | 80 | 0 | 2 | 3 | -0.032317 | 0.050546 | 0.000000 | 2.000000 |
| P-small | RawPre-small | bing.com::search_results_view | U | 80 | 80 | 0 | 3 | 5 | 0.013900 | 0.108248 | 0.000000 | 3.000000 |
| P-small | RawPre-small | developer.mozilla.org::document_view | C | 160 | 80 | 4 | 3 | 9 | 0.069445 | 0.097926 | 4.000000 | 2.000000 |
| P-small | RawPre-small | developer.mozilla.org::document_view | U | 80 | 80 | 0 | 1 | 1 | -0.013884 | 0.081026 | 0.000000 | 1.000000 |
| P-small | RawPre-small | github.com::repository_view | C | 160 | 80 | 0 | 3 | 3 | 0.020416 | 0.037713 | 0.000000 | 3.000000 |
| P-small | RawPre-small | github.com::repository_view | U | 80 | 80 | 5 | 0 | 5 | -0.070715 | 0.084352 | 5.000000 | 0.000000 |
| P-small | RawPre-small | wikipedia.org::article_view | C | 160 | 80 | 6 | 0 | 8 | -0.036486 | 0.070172 | 5.000000 | 0.000000 |
| P-small | RawPre-small | wikipedia.org::article_view | U | 80 | 80 | 4 | 1 | 7 | -0.088639 | 0.095524 | 4.000000 | 1.000000 |
| P-small | RawPre-small | youtube.com::search_results_view | C | 160 | 80 | 1 | 1 | 2 | 0.021184 | 0.041527 | 1.000000 | 1.000000 |
| P-small | RawPre-small | youtube.com::search_results_view | U | 80 | 80 | 1 | 0 | 1 | 0.001705 | 0.060489 | 1.000000 | 0.000000 |
| P-small | RawPre-small | youtube.com::video_playback | C | 160 | 80 | 2 | 2 | 5 | -0.004777 | 0.053189 | 2.000000 | 2.000000 |
| P-small | RawPre-small | youtube.com::video_playback | U | 80 | 80 | 3 | 0 | 4 | -0.022109 | 0.078731 | 3.000000 | 0.000000 |
| P-small | S | bing.com::search_results_view | C | 160 | 80 | 0 | 3 | 4 | -0.031546 | 0.069367 | 0.000000 | 3.000000 |
| P-small | S | bing.com::search_results_view | U | 80 | 80 | 0 | 1 | 2 | 0.017008 | 0.098357 | 0.000000 | 1.000000 |
| P-small | S | developer.mozilla.org::document_view | C | 160 | 80 | 4 | 3 | 8 | 0.010703 | 0.108886 | 4.000000 | 3.000000 |
| P-small | S | developer.mozilla.org::document_view | U | 80 | 80 | 4 | 0 | 7 | -0.109169 | 0.178980 | 4.000000 | 0.000000 |
| P-small | S | github.com::repository_view | C | 160 | 80 | 1 | 1 | 2 | 0.000057 | 0.045881 | 1.000000 | 1.000000 |
| P-small | S | github.com::repository_view | U | 80 | 80 | 6 | 0 | 6 | -0.130861 | 0.122875 | 6.000000 | 0.000000 |
| P-small | S | wikipedia.org::article_view | C | 160 | 80 | 3 | 3 | 6 | -0.020118 | 0.079589 | 3.000000 | 3.000000 |
| P-small | S | wikipedia.org::article_view | U | 80 | 80 | 2 | 1 | 4 | -0.052769 | 0.099346 | 2.000000 | 1.000000 |
| P-small | S | youtube.com::search_results_view | C | 160 | 80 | 3 | 3 | 7 | -0.013723 | 0.036068 | 3.000000 | 3.000000 |
| P-small | S | youtube.com::search_results_view | U | 80 | 80 | 3 | 0 | 4 | -0.076401 | 0.085384 | 3.000000 | 0.000000 |
| P-small | S | youtube.com::video_playback | C | 160 | 80 | 1 | 1 | 2 | 0.012016 | 0.056240 | 1.000000 | 1.000000 |
| P-small | S | youtube.com::video_playback | U | 80 | 80 | 6 | 0 | 6 | -0.182714 | 0.145181 | 6.000000 | 0.000000 |

## 留一内容描述性敏感性

| excluded_content | candidate | reference | delta_uncovered_F1 | retrained | new_test |
| --- | --- | --- | --- | --- | --- |
| https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | P-small | S | 0.022997 | False | False |
| https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | P-small | G-small | -0.000244 | False | False |
| https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | P-small | RawPre-small | 0.006159 | False | False |
| https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | P-small | RawPost-small | 0.021152 | False | False |
| https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | P-small | Marginal-small | 0.022039 | False | False |
| https://developer.mozilla.org/en-US/docs/Web/HTTP | P-small | S | 0.025410 | False | False |
| https://developer.mozilla.org/en-US/docs/Web/HTTP | P-small | G-small | 0.002239 | False | False |
| https://developer.mozilla.org/en-US/docs/Web/HTTP | P-small | RawPre-small | 0.007309 | False | False |
| https://developer.mozilla.org/en-US/docs/Web/HTTP | P-small | RawPost-small | 0.023522 | False | False |
| https://developer.mozilla.org/en-US/docs/Web/HTTP | P-small | Marginal-small | 0.022079 | False | False |
| https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | P-small | S | 0.026741 | False | False |
| https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | P-small | G-small | 0.001538 | False | False |
| https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | P-small | RawPre-small | 0.006314 | False | False |
| https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | P-small | RawPost-small | 0.024839 | False | False |
| https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | P-small | Marginal-small | 0.018021 | False | False |
| https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | P-small | S | 0.024638 | False | False |
| https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | P-small | G-small | 0.002163 | False | False |
| https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | P-small | RawPre-small | 0.009733 | False | False |
| https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | P-small | RawPost-small | 0.022749 | False | False |
| https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | P-small | Marginal-small | 0.018564 | False | False |
| https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | P-small | S | 0.021079 | False | False |
| https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | P-small | G-small | 0.002378 | False | False |
| https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | P-small | RawPre-small | 0.005470 | False | False |
| https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | P-small | RawPost-small | 0.019234 | False | False |
| https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | P-small | Marginal-small | 0.016724 | False | False |
| https://en.wikipedia.org/wiki/Computer_network | P-small | S | 0.024126 | False | False |
| https://en.wikipedia.org/wiki/Computer_network | P-small | G-small | 0.000406 | False | False |
| https://en.wikipedia.org/wiki/Computer_network | P-small | RawPre-small | 0.006396 | False | False |
| https://en.wikipedia.org/wiki/Computer_network | P-small | RawPost-small | 0.022237 | False | False |
| https://en.wikipedia.org/wiki/Computer_network | P-small | Marginal-small | 0.019761 | False | False |
| https://en.wikipedia.org/wiki/Domain_Name_System | P-small | S | 0.022491 | False | False |
| https://en.wikipedia.org/wiki/Domain_Name_System | P-small | G-small | 0.001589 | False | False |
| https://en.wikipedia.org/wiki/Domain_Name_System | P-small | RawPre-small | 0.006391 | False | False |
| https://en.wikipedia.org/wiki/Domain_Name_System | P-small | RawPost-small | 0.020602 | False | False |
| https://en.wikipedia.org/wiki/Domain_Name_System | P-small | Marginal-small | 0.017888 | False | False |
| https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | P-small | S | 0.025004 | False | False |
| https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | P-small | G-small | 0.004396 | False | False |
| https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | P-small | RawPre-small | 0.007583 | False | False |
| https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | P-small | RawPost-small | 0.023103 | False | False |
| https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | P-small | Marginal-small | 0.021731 | False | False |
| https://en.wikipedia.org/wiki/Transmission_Control_Protocol | P-small | S | 0.023750 | False | False |
| https://en.wikipedia.org/wiki/Transmission_Control_Protocol | P-small | G-small | 0.000753 | False | False |
| https://en.wikipedia.org/wiki/Transmission_Control_Protocol | P-small | RawPre-small | 0.007368 | False | False |
| https://en.wikipedia.org/wiki/Transmission_Control_Protocol | P-small | RawPost-small | 0.021861 | False | False |
| https://en.wikipedia.org/wiki/Transmission_Control_Protocol | P-small | Marginal-small | 0.020310 | False | False |
| https://en.wikipedia.org/wiki/Transport_Layer_Security | P-small | S | 0.025416 | False | False |
| https://en.wikipedia.org/wiki/Transport_Layer_Security | P-small | G-small | 0.000921 | False | False |
| https://en.wikipedia.org/wiki/Transport_Layer_Security | P-small | RawPre-small | 0.007630 | False | False |
| https://en.wikipedia.org/wiki/Transport_Layer_Security | P-small | RawPost-small | 0.023527 | False | False |
| https://en.wikipedia.org/wiki/Transport_Layer_Security | P-small | Marginal-small | 0.022315 | False | False |
| https://github.com/RakuLomis/TrafficTracer | P-small | S | 0.024963 | False | False |
| https://github.com/RakuLomis/TrafficTracer | P-small | G-small | 0.002754 | False | False |
| https://github.com/RakuLomis/TrafficTracer | P-small | RawPre-small | 0.009150 | False | False |
| https://github.com/RakuLomis/TrafficTracer | P-small | RawPost-small | 0.023074 | False | False |
| https://github.com/RakuLomis/TrafficTracer | P-small | Marginal-small | 0.022925 | False | False |
| https://github.com/numpy/numpy | P-small | S | 0.017893 | False | False |
| https://github.com/numpy/numpy | P-small | G-small | 0.000824 | False | False |
| https://github.com/numpy/numpy | P-small | RawPre-small | 0.003418 | False | False |
| https://github.com/numpy/numpy | P-small | RawPost-small | 0.016004 | False | False |
| https://github.com/numpy/numpy | P-small | Marginal-small | 0.012570 | False | False |
| https://github.com/pallets/flask | P-small | S | 0.026632 | False | False |
| https://github.com/pallets/flask | P-small | G-small | 0.002588 | False | False |
| https://github.com/pallets/flask | P-small | RawPre-small | 0.008938 | False | False |
| https://github.com/pallets/flask | P-small | RawPost-small | 0.024718 | False | False |
| https://github.com/pallets/flask | P-small | Marginal-small | 0.021797 | False | False |
| https://github.com/python/cpython | P-small | S | 0.027583 | False | False |
| https://github.com/python/cpython | P-small | G-small | 0.002713 | False | False |
| https://github.com/python/cpython | P-small | RawPre-small | 0.005503 | False | False |
| https://github.com/python/cpython | P-small | RawPost-small | 0.025694 | False | False |
| https://github.com/python/cpython | P-small | Marginal-small | 0.022555 | False | False |
| https://github.com/scikit-learn/scikit-learn | P-small | S | 0.024993 | False | False |
| https://github.com/scikit-learn/scikit-learn | P-small | G-small | 0.002466 | False | False |
| https://github.com/scikit-learn/scikit-learn | P-small | RawPre-small | 0.009831 | False | False |
| https://github.com/scikit-learn/scikit-learn | P-small | RawPost-small | 0.023104 | False | False |
| https://github.com/scikit-learn/scikit-learn | P-small | Marginal-small | 0.019545 | False | False |
| https://www.bing.com/search?q=beginner+guitar+chords | P-small | S | 0.025163 | False | False |
| https://www.bing.com/search?q=beginner+guitar+chords | P-small | G-small | 0.004184 | False | False |
| https://www.bing.com/search?q=beginner+guitar+chords | P-small | RawPre-small | 0.008106 | False | False |
| https://www.bing.com/search?q=beginner+guitar+chords | P-small | RawPost-small | 0.023103 | False | False |
| https://www.bing.com/search?q=beginner+guitar+chords | P-small | Marginal-small | 0.022807 | False | False |
| https://www.bing.com/search?q=indoor+plant+care | P-small | S | 0.023979 | False | False |
| https://www.bing.com/search?q=indoor+plant+care | P-small | G-small | 0.004186 | False | False |
| https://www.bing.com/search?q=indoor+plant+care | P-small | RawPre-small | 0.005411 | False | False |
| https://www.bing.com/search?q=indoor+plant+care | P-small | RawPost-small | 0.021795 | False | False |
| https://www.bing.com/search?q=indoor+plant+care | P-small | Marginal-small | 0.020750 | False | False |
| https://www.bing.com/search?q=network+traffic+analysis | P-small | S | 0.023259 | False | False |
| https://www.bing.com/search?q=network+traffic+analysis | P-small | G-small | 0.001876 | False | False |
| https://www.bing.com/search?q=network+traffic+analysis | P-small | RawPre-small | 0.005694 | False | False |
| https://www.bing.com/search?q=network+traffic+analysis | P-small | RawPost-small | 0.021198 | False | False |
| https://www.bing.com/search?q=network+traffic+analysis | P-small | Marginal-small | 0.019917 | False | False |
| https://www.bing.com/search?q=solar+system+facts | P-small | S | 0.025009 | False | False |
| https://www.bing.com/search?q=solar+system+facts | P-small | G-small | 0.001695 | False | False |
| https://www.bing.com/search?q=solar+system+facts | P-small | RawPre-small | 0.009156 | False | False |
| https://www.bing.com/search?q=solar+system+facts | P-small | RawPost-small | 0.024658 | False | False |
| https://www.bing.com/search?q=solar+system+facts | P-small | Marginal-small | 0.020764 | False | False |
| https://www.bing.com/search?q=sourdough+bread+recipe | P-small | S | 0.023293 | False | False |
| https://www.bing.com/search?q=sourdough+bread+recipe | P-small | G-small | 0.000978 | False | False |
| https://www.bing.com/search?q=sourdough+bread+recipe | P-small | RawPre-small | 0.007503 | False | False |
| https://www.bing.com/search?q=sourdough+bread+recipe | P-small | RawPost-small | 0.021330 | False | False |
| https://www.bing.com/search?q=sourdough+bread+recipe | P-small | Marginal-small | 0.019315 | False | False |
| https://www.youtube.com/results?search_query=astronomy+documentary | P-small | S | 0.025033 | False | False |
| https://www.youtube.com/results?search_query=astronomy+documentary | P-small | G-small | 0.002005 | False | False |
| https://www.youtube.com/results?search_query=astronomy+documentary | P-small | RawPre-small | 0.007178 | False | False |
| https://www.youtube.com/results?search_query=astronomy+documentary | P-small | RawPost-small | 0.022908 | False | False |
| https://www.youtube.com/results?search_query=astronomy+documentary | P-small | Marginal-small | 0.021433 | False | False |
| https://www.youtube.com/results?search_query=bicycle+maintenance | P-small | S | 0.023597 | False | False |
| https://www.youtube.com/results?search_query=bicycle+maintenance | P-small | G-small | 0.001959 | False | False |
| https://www.youtube.com/results?search_query=bicycle+maintenance | P-small | RawPre-small | 0.007366 | False | False |
| https://www.youtube.com/results?search_query=bicycle+maintenance | P-small | RawPost-small | 0.023085 | False | False |
| https://www.youtube.com/results?search_query=bicycle+maintenance | P-small | Marginal-small | 0.018391 | False | False |
| https://www.youtube.com/results?search_query=bread+baking | P-small | S | 0.023768 | False | False |
| https://www.youtube.com/results?search_query=bread+baking | P-small | G-small | 0.002005 | False | False |
| https://www.youtube.com/results?search_query=bread+baking | P-small | RawPre-small | 0.007406 | False | False |
| https://www.youtube.com/results?search_query=bread+baking | P-small | RawPost-small | 0.020545 | False | False |
| https://www.youtube.com/results?search_query=bread+baking | P-small | Marginal-small | 0.018321 | False | False |
| https://www.youtube.com/results?search_query=piano+practice | P-small | S | 0.023645 | False | False |
| https://www.youtube.com/results?search_query=piano+practice | P-small | G-small | 0.002005 | False | False |
| https://www.youtube.com/results?search_query=piano+practice | P-small | RawPre-small | 0.005558 | False | False |
| https://www.youtube.com/results?search_query=piano+practice | P-small | RawPost-small | 0.021408 | False | False |
| https://www.youtube.com/results?search_query=piano+practice | P-small | Marginal-small | 0.019012 | False | False |
| https://www.youtube.com/results?search_query=watercolor+tutorial | P-small | S | 0.025008 | False | False |
| https://www.youtube.com/results?search_query=watercolor+tutorial | P-small | G-small | 0.001977 | False | False |
| https://www.youtube.com/results?search_query=watercolor+tutorial | P-small | RawPre-small | 0.007295 | False | False |
| https://www.youtube.com/results?search_query=watercolor+tutorial | P-small | RawPost-small | 0.022771 | False | False |
| https://www.youtube.com/results?search_query=watercolor+tutorial | P-small | Marginal-small | 0.020648 | False | False |
| youtube_video:R6MlUcmOul8 | P-small | S | 0.023257 | False | False |
| youtube_video:R6MlUcmOul8 | P-small | G-small | 0.002210 | False | False |
| youtube_video:R6MlUcmOul8 | P-small | RawPre-small | 0.006491 | False | False |
| youtube_video:R6MlUcmOul8 | P-small | RawPost-small | 0.021368 | False | False |
| youtube_video:R6MlUcmOul8 | P-small | Marginal-small | 0.019071 | False | False |
| youtube_video:aircAruvnKk | P-small | S | 0.024643 | False | False |
| youtube_video:aircAruvnKk | P-small | G-small | 0.002174 | False | False |
| youtube_video:aircAruvnKk | P-small | RawPre-small | 0.004195 | False | False |
| youtube_video:aircAruvnKk | P-small | RawPost-small | 0.022798 | False | False |
| youtube_video:aircAruvnKk | P-small | Marginal-small | 0.019927 | False | False |
| youtube_video:aqz-KE-bpKQ | P-small | S | 0.024643 | False | False |
| youtube_video:aqz-KE-bpKQ | P-small | G-small | 0.002180 | False | False |
| youtube_video:aqz-KE-bpKQ | P-small | RawPre-small | 0.008177 | False | False |
| youtube_video:aqz-KE-bpKQ | P-small | RawPost-small | 0.022754 | False | False |
| youtube_video:aqz-KE-bpKQ | P-small | Marginal-small | 0.019917 | False | False |
| youtube_video:eRsGyueVLvQ | P-small | S | 0.020557 | False | False |
| youtube_video:eRsGyueVLvQ | P-small | G-small | 0.002180 | False | False |
| youtube_video:eRsGyueVLvQ | P-small | RawPre-small | 0.008365 | False | False |
| youtube_video:eRsGyueVLvQ | P-small | RawPost-small | 0.018669 | False | False |
| youtube_video:eRsGyueVLvQ | P-small | Marginal-small | 0.019905 | False | False |
| youtube_video:sAWK0mgrMp4 | P-small | S | 0.028314 | False | False |
| youtube_video:sAWK0mgrMp4 | P-small | G-small | 0.001397 | False | False |
| youtube_video:sAWK0mgrMp4 | P-small | RawPre-small | 0.008191 | False | False |
| youtube_video:sAWK0mgrMp4 | P-small | RawPost-small | 0.026425 | False | False |
| youtube_video:sAWK0mgrMp4 | P-small | Marginal-small | 0.019905 | False | False |

## 新分类器数值验收

| role_id | target | group | outer | arm | model_path | model_sha256 | seconds | objective | gradient_inf | objective_replay_error | gradient_replay_error |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| main/f0/shadowsocks/G0/outer | shadowsocks | G0 | 0 | RawPre-small | outputs/small-view-attribution-20261010/run-02/models/main/f0/shadowsocks/G0/outer/RawPre-small.pt | fcdd5e1f61ef01497257dc93d55181dadb301cce14295ef811f5139b42704f3c | 8.119489 | 0.292627 | 0.000005 | 0.000000 | 0.000000 |
| main/f0/shadowsocks/G0/outer | shadowsocks | G0 | 0 | RawPost-small | outputs/small-view-attribution-20261010/run-02/models/main/f0/shadowsocks/G0/outer/RawPost-small.pt | ecc17255bb7b070d5acd1fc6a0a332a5a6f1838d6706a580259c071bde866683 | 0.459132 | 0.275426 | 0.000007 | 0.000000 | 0.000000 |
| main/f0/shadowsocks/G0/outer | shadowsocks | G0 | 0 | Marginal-small | outputs/small-view-attribution-20261010/run-02/models/main/f0/shadowsocks/G0/outer/Marginal-small.pt | bd1d602eacddc059351b5fa407205f16367f5126d99d41331727b8223cae9f00 | 0.383150 | 0.308187 | 0.000010 | 0.000000 | 0.000000 |
| main/f0/shadowsocks/G1/outer | shadowsocks | G1 | 0 | RawPre-small | outputs/small-view-attribution-20261010/run-02/models/main/f0/shadowsocks/G1/outer/RawPre-small.pt | 04963ea7d99903badf91c938ec2bada840451d17d9cb631515a2cdd67dffe3b2 | 1.838959 | 0.186964 | 0.000006 | 0.000000 | 0.000000 |
| main/f0/shadowsocks/G1/outer | shadowsocks | G1 | 0 | RawPost-small | outputs/small-view-attribution-20261010/run-02/models/main/f0/shadowsocks/G1/outer/RawPost-small.pt | 91b790dea5f23c3580782e6f3ae7a73f3e3ca65591f7a5bbe21e8edaa310d3d9 | 1.070082 | 0.163504 | 0.000010 | 0.000000 | 0.000000 |
| main/f0/shadowsocks/G1/outer | shadowsocks | G1 | 0 | Marginal-small | outputs/small-view-attribution-20261010/run-02/models/main/f0/shadowsocks/G1/outer/Marginal-small.pt | a630b2e8115ca4221f262264244c55a37f5e3c5d3e34e62c2617e76f6ac731b1 | 0.705072 | 0.209930 | 0.000010 | 0.000000 | 0.000000 |
| main/f0/shadowsocks/G2/outer | shadowsocks | G2 | 0 | RawPre-small | outputs/small-view-attribution-20261010/run-02/models/main/f0/shadowsocks/G2/outer/RawPre-small.pt | 014ba4d9cf2ba771087b2bb0bc184d52f383f20224de224e05956f06c7ea7e09 | 1.370266 | 0.172490 | 0.000010 | 0.000000 | 0.000000 |
| main/f0/shadowsocks/G2/outer | shadowsocks | G2 | 0 | RawPost-small | outputs/small-view-attribution-20261010/run-02/models/main/f0/shadowsocks/G2/outer/RawPost-small.pt | c9b06394db11f18b3bcbc063efa471ca06b588f09da84a3a4e0f65ff400853c1 | 0.926789 | 0.148726 | 0.000009 | 0.000000 | 0.000000 |
| main/f0/shadowsocks/G2/outer | shadowsocks | G2 | 0 | Marginal-small | outputs/small-view-attribution-20261010/run-02/models/main/f0/shadowsocks/G2/outer/Marginal-small.pt | 72fc8653de19571cac9413fafb332ceea922ffbfd3b74466327a81141dcd5b49 | 0.699851 | 0.195680 | 0.000010 | 0.000000 | 0.000000 |
| main/f0/vless/G0/outer | vless | G0 | 0 | RawPre-small | outputs/small-view-attribution-20261010/run-02/models/main/f0/vless/G0/outer/RawPre-small.pt | 259969de9d432abe3f8cc5b1f5d923d000e77efc8595ceba2ccdb5e1f47c6b80 | 0.425671 | 0.272538 | 0.000009 | 0.000000 | 0.000000 |
| main/f0/vless/G0/outer | vless | G0 | 0 | RawPost-small | outputs/small-view-attribution-20261010/run-02/models/main/f0/vless/G0/outer/RawPost-small.pt | ad9cf7298862ead4e6a8225730a4b1dc89bd05a95007d33d78861a09cb69b86e | 0.352835 | 0.258731 | 0.000007 | 0.000000 | 0.000000 |
| main/f0/vless/G0/outer | vless | G0 | 0 | Marginal-small | outputs/small-view-attribution-20261010/run-02/models/main/f0/vless/G0/outer/Marginal-small.pt | b7ee31b9cab504ddb62a97ddbff5d49d99d83741bd6efaf15c9385a6424a3405 | 0.331523 | 0.294056 | 0.000008 | 0.000000 | 0.000000 |
| main/f0/vless/G1/outer | vless | G1 | 0 | RawPre-small | outputs/small-view-attribution-20261010/run-02/models/main/f0/vless/G1/outer/RawPre-small.pt | 7740664e3b1cfd438db639aecab39d730ae54ecc1cca3cd11bbd5205e901e990 | 0.567320 | 0.303070 | 0.000007 | 0.000000 | 0.000000 |
| main/f0/vless/G1/outer | vless | G1 | 0 | RawPost-small | outputs/small-view-attribution-20261010/run-02/models/main/f0/vless/G1/outer/RawPost-small.pt | 676987384e2dba609a6033b894fa5c523f520383459b0ccee25851529ce3014c | 0.417092 | 0.289975 | 0.000009 | 0.000000 | 0.000000 |
| main/f0/vless/G1/outer | vless | G1 | 0 | Marginal-small | outputs/small-view-attribution-20261010/run-02/models/main/f0/vless/G1/outer/Marginal-small.pt | de453aa02d5f21cead0c3e37867ff563b90e44f3f4729038a7c1579c5b3f4106 | 0.387723 | 0.334125 | 0.000010 | 0.000000 | 0.000000 |
| main/f0/vless/G2/outer | vless | G2 | 0 | RawPre-small | outputs/small-view-attribution-20261010/run-02/models/main/f0/vless/G2/outer/RawPre-small.pt | 12c2ee7fb54c4adb7aa585da7994ea9eb950b76d34255339d6c2c160accd7ca2 | 0.642909 | 0.225081 | 0.000010 | 0.000000 | 0.000000 |
| main/f0/vless/G2/outer | vless | G2 | 0 | RawPost-small | outputs/small-view-attribution-20261010/run-02/models/main/f0/vless/G2/outer/RawPost-small.pt | 4d08b80f7a7a4c836a87ba5629ba5f726c3fad5882ad14d46354d16f08a3fe59 | 0.347315 | 0.210018 | 0.000010 | 0.000000 | 0.000000 |
| main/f0/vless/G2/outer | vless | G2 | 0 | Marginal-small | outputs/small-view-attribution-20261010/run-02/models/main/f0/vless/G2/outer/Marginal-small.pt | 9e0bb4f7c50618267d1e9d0e6e55dafba2235559ea3d1e3e8a2dc9d1cc1b4a39 | 0.378317 | 0.243491 | 0.000009 | 0.000000 | 0.000000 |
| main/f0/trojan/G0/outer | trojan | G0 | 0 | RawPre-small | outputs/small-view-attribution-20261010/run-02/models/main/f0/trojan/G0/outer/RawPre-small.pt | b5628586b441a3a35ff553a03d62c480bb13c994dc570a659f234d5522acf4ef | 0.445438 | 0.298040 | 0.000010 | 0.000000 | 0.000000 |
| main/f0/trojan/G0/outer | trojan | G0 | 0 | RawPost-small | outputs/small-view-attribution-20261010/run-02/models/main/f0/trojan/G0/outer/RawPost-small.pt | 31204ac7895576ccb03cc84951557acd8a0c3134d1c942b789bfe0a47fc96a27 | 0.367209 | 0.282368 | 0.000008 | 0.000000 | 0.000000 |
| main/f0/trojan/G0/outer | trojan | G0 | 0 | Marginal-small | outputs/small-view-attribution-20261010/run-02/models/main/f0/trojan/G0/outer/Marginal-small.pt | 1633a40251d52bd24312bc5ab62445f2b634650716d9b71dbcb6227ad58d8cf6 | 0.360654 | 0.318024 | 0.000008 | 0.000000 | 0.000000 |
| main/f0/trojan/G1/outer | trojan | G1 | 0 | RawPre-small | outputs/small-view-attribution-20261010/run-02/models/main/f0/trojan/G1/outer/RawPre-small.pt | 57c57e47ed6c661b95e7840c89981a499e9f3ff8f64e0a83486ef25b984b1d3b | 0.638216 | 0.301152 | 0.000007 | 0.000000 | 0.000000 |
| main/f0/trojan/G1/outer | trojan | G1 | 0 | RawPost-small | outputs/small-view-attribution-20261010/run-02/models/main/f0/trojan/G1/outer/RawPost-small.pt | bd18fc37c4b309c474eec754614d86ecb5b82f961a5a4cf8e5f5c215134c2c49 | 0.356930 | 0.284485 | 0.000010 | 0.000000 | 0.000000 |
| main/f0/trojan/G1/outer | trojan | G1 | 0 | Marginal-small | outputs/small-view-attribution-20261010/run-02/models/main/f0/trojan/G1/outer/Marginal-small.pt | 274b8ad6e473c57def432bd705ff7dfe33ef14b578d63f6fb2bcd909a001a204 | 0.396613 | 0.333643 | 0.000009 | 0.000000 | 0.000000 |
| main/f0/trojan/G2/outer | trojan | G2 | 0 | RawPre-small | outputs/small-view-attribution-20261010/run-02/models/main/f0/trojan/G2/outer/RawPre-small.pt | ff22aacec7ab0685ee6821727f9c6da302bd7dab9b5031acf7fed1582dfeca64 | 0.510491 | 0.289907 | 0.000009 | 0.000000 | 0.000000 |
| main/f0/trojan/G2/outer | trojan | G2 | 0 | RawPost-small | outputs/small-view-attribution-20261010/run-02/models/main/f0/trojan/G2/outer/RawPost-small.pt | 059f18e613552cc6edb42b16049adb29d93fad03917c570f6697aabfc622abe2 | 0.319136 | 0.275971 | 0.000007 | 0.000000 | 0.000000 |
| main/f0/trojan/G2/outer | trojan | G2 | 0 | Marginal-small | outputs/small-view-attribution-20261010/run-02/models/main/f0/trojan/G2/outer/Marginal-small.pt | 66de69a35798f22d42f19adfbacbc34c4ebb74057ff3295077011d0048ef8bd7 | 0.337108 | 0.313762 | 0.000010 | 0.000000 | 0.000000 |
| main/f0/vmess/G0/outer | vmess | G0 | 0 | RawPre-small | outputs/small-view-attribution-20261010/run-02/models/main/f0/vmess/G0/outer/RawPre-small.pt | f7dc351e6f80e2d4086017977ed6d29b722fb9cf4eafc2fca7fce030d803429e | 0.462524 | 0.304938 | 0.000007 | 0.000000 | 0.000000 |
| main/f0/vmess/G0/outer | vmess | G0 | 0 | RawPost-small | outputs/small-view-attribution-20261010/run-02/models/main/f0/vmess/G0/outer/RawPost-small.pt | 5841db02a2cbe1221c2faaf8e31fa2612c69f6e85c595ecb5612ae07017c45d2 | 0.472533 | 0.289365 | 0.000009 | 0.000000 | 0.000000 |
| main/f0/vmess/G0/outer | vmess | G0 | 0 | Marginal-small | outputs/small-view-attribution-20261010/run-02/models/main/f0/vmess/G0/outer/Marginal-small.pt | e5f830b523bcdeba01fb3d7559c49595a236ea3328f0d099c79c3e051d490b86 | 0.347785 | 0.323073 | 0.000009 | 0.000000 | 0.000000 |
| main/f0/vmess/G1/outer | vmess | G1 | 0 | RawPre-small | outputs/small-view-attribution-20261010/run-02/models/main/f0/vmess/G1/outer/RawPre-small.pt | b73934cdd181665cc6f8eba988263542fadcfa5e66ab42ef984496a84658372b | 0.852024 | 0.207702 | 0.000009 | 0.000000 | 0.000000 |
| main/f0/vmess/G1/outer | vmess | G1 | 0 | RawPost-small | outputs/small-view-attribution-20261010/run-02/models/main/f0/vmess/G1/outer/RawPost-small.pt | 97dc55b705cc483765c9f51f5b4c4278f5f4aac5fca388f070b0638dc79112ea | 0.520656 | 0.191667 | 0.000009 | 0.000000 | 0.000000 |
| main/f0/vmess/G1/outer | vmess | G1 | 0 | Marginal-small | outputs/small-view-attribution-20261010/run-02/models/main/f0/vmess/G1/outer/Marginal-small.pt | cf8f089abe44decf93131c0717263d2cd95212919d504f472649fa6a99b1dfa4 | 0.626898 | 0.238040 | 0.000009 | 0.000000 | 0.000000 |
| main/f0/vmess/G2/outer | vmess | G2 | 0 | RawPre-small | outputs/small-view-attribution-20261010/run-02/models/main/f0/vmess/G2/outer/RawPre-small.pt | acc033a3c2b3cb2101f98e804ca9c6adc790e321de26a844e34eaff9ca19f396 | 0.638227 | 0.286181 | 0.000008 | 0.000000 | 0.000000 |
| main/f0/vmess/G2/outer | vmess | G2 | 0 | RawPost-small | outputs/small-view-attribution-20261010/run-02/models/main/f0/vmess/G2/outer/RawPost-small.pt | c54ea9fcfe325f3d344fdd60bb8c610d017f1b229261faf58a299299b44975a5 | 0.353249 | 0.271690 | 0.000010 | 0.000000 | 0.000000 |
| main/f0/vmess/G2/outer | vmess | G2 | 0 | Marginal-small | outputs/small-view-attribution-20261010/run-02/models/main/f0/vmess/G2/outer/Marginal-small.pt | d13676fd1f97d3df34ca8ccca8365fc6ea3d175d3cbd1ad065ef43fe4c09de49 | 0.510509 | 0.310250 | 0.000010 | 0.000000 | 0.000000 |
| main/f1/shadowsocks/G0/outer | shadowsocks | G0 | 1 | RawPre-small | outputs/small-view-attribution-20261010/run-02/models/main/f1/shadowsocks/G0/outer/RawPre-small.pt | 8ca8c13dd5b204046129bf5cf31b1db85f0bffa53196386260b63fba4ca7e078 | 1.830381 | 0.205721 | 0.000007 | 0.000000 | 0.000000 |
| main/f1/shadowsocks/G0/outer | shadowsocks | G0 | 1 | RawPost-small | outputs/small-view-attribution-20261010/run-02/models/main/f1/shadowsocks/G0/outer/RawPost-small.pt | d2d6beb346c85b2d750d423409b4bc8b37c0c1400177eb7d26699d68d86f4e08 | 0.371185 | 0.187066 | 0.000009 | 0.000000 | 0.000000 |
| main/f1/shadowsocks/G0/outer | shadowsocks | G0 | 1 | Marginal-small | outputs/small-view-attribution-20261010/run-02/models/main/f1/shadowsocks/G0/outer/Marginal-small.pt | 0ee8f03b9930b959370429fc5d05df92286574e2ffd7e1682ffdd7625b1091c1 | 0.432846 | 0.219927 | 0.000010 | 0.000000 | 0.000000 |
| main/f1/shadowsocks/G1/outer | shadowsocks | G1 | 1 | RawPre-small | outputs/small-view-attribution-20261010/run-02/models/main/f1/shadowsocks/G1/outer/RawPre-small.pt | 5a58de7c80d95963ed4664254e1f029c581364eb7778a588ba48d310f2186cf9 | 0.394018 | 0.270966 | 0.000009 | 0.000000 | 0.000000 |
| main/f1/shadowsocks/G1/outer | shadowsocks | G1 | 1 | RawPost-small | outputs/small-view-attribution-20261010/run-02/models/main/f1/shadowsocks/G1/outer/RawPost-small.pt | 9c17bc33a9956a53813197ce0c8e900977757964118ae0214c63777d010d7969 | 0.261307 | 0.253867 | 0.000007 | 0.000000 | 0.000000 |
| main/f1/shadowsocks/G1/outer | shadowsocks | G1 | 1 | Marginal-small | outputs/small-view-attribution-20261010/run-02/models/main/f1/shadowsocks/G1/outer/Marginal-small.pt | 28c86aec33d8a4c6b1717899883be700d69c21261e8a967d3ee592297c6b56c1 | 0.244326 | 0.290524 | 0.000010 | 0.000000 | 0.000000 |
| main/f1/shadowsocks/G2/outer | shadowsocks | G2 | 1 | RawPre-small | outputs/small-view-attribution-20261010/run-02/models/main/f1/shadowsocks/G2/outer/RawPre-small.pt | fd74261999d701cb295255598c990763c89448df816d26a378505fc6319fe940 | 0.386886 | 0.262598 | 0.000009 | 0.000000 | 0.000000 |
| main/f1/shadowsocks/G2/outer | shadowsocks | G2 | 1 | RawPost-small | outputs/small-view-attribution-20261010/run-02/models/main/f1/shadowsocks/G2/outer/RawPost-small.pt | d8d1115adc35bd5bffdc4e5f589c01a7b1b95026b370a7b40f2df077e934e35d | 0.247496 | 0.242514 | 0.000009 | 0.000000 | 0.000000 |
| main/f1/shadowsocks/G2/outer | shadowsocks | G2 | 1 | Marginal-small | outputs/small-view-attribution-20261010/run-02/models/main/f1/shadowsocks/G2/outer/Marginal-small.pt | 461990e4b4f13a7c846aee28a9e0afffc4dba6f98c76923891d07b9ec1a2c2e5 | 0.232071 | 0.282254 | 0.000009 | 0.000000 | 0.000000 |
| main/f1/vless/G0/outer | vless | G0 | 1 | RawPre-small | outputs/small-view-attribution-20261010/run-02/models/main/f1/vless/G0/outer/RawPre-small.pt | 3a7d6ad898b78e9c7ff041621d56a327e8cb490ea10d8f9ff72fbc5af5013025 | 0.861367 | 0.163779 | 0.000009 | 0.000000 | 0.000000 |
| main/f1/vless/G0/outer | vless | G0 | 1 | RawPost-small | outputs/small-view-attribution-20261010/run-02/models/main/f1/vless/G0/outer/RawPost-small.pt | d07f6eb34af3a4e7a9d5dd30e2429af400fa5d45a6e033e12e241cef09785374 | 0.593916 | 0.147989 | 0.000009 | 0.000000 | 0.000000 |
| main/f1/vless/G0/outer | vless | G0 | 1 | Marginal-small | outputs/small-view-attribution-20261010/run-02/models/main/f1/vless/G0/outer/Marginal-small.pt | 52b0121d502408d61f050c5010927f703c71ffc806b552df56b5fdb853cac9a5 | 0.499868 | 0.185401 | 0.000009 | 0.000000 | 0.000000 |
| main/f1/vless/G1/outer | vless | G1 | 1 | RawPre-small | outputs/small-view-attribution-20261010/run-02/models/main/f1/vless/G1/outer/RawPre-small.pt | 3959a8ade9f3ffa6905f2e0ee791c838f7ee01979a4715c102ea315d8878c35f | 0.425267 | 0.284387 | 0.000007 | 0.000000 | 0.000000 |
| main/f1/vless/G1/outer | vless | G1 | 1 | RawPost-small | outputs/small-view-attribution-20261010/run-02/models/main/f1/vless/G1/outer/RawPost-small.pt | fba19f56733251e5333c606ce39da7f64b5fc72d3ca39e09b77452ab1528fe8a | 0.332406 | 0.272621 | 0.000009 | 0.000000 | 0.000000 |
| main/f1/vless/G1/outer | vless | G1 | 1 | Marginal-small | outputs/small-view-attribution-20261010/run-02/models/main/f1/vless/G1/outer/Marginal-small.pt | 614ee3e240ef3ee81e060aa5a10ebfec8d54daae28ac1769f9758516c1900025 | 0.447255 | 0.301914 | 0.000009 | 0.000000 | 0.000000 |
| main/f1/vless/G2/outer | vless | G2 | 1 | RawPre-small | outputs/small-view-attribution-20261010/run-02/models/main/f1/vless/G2/outer/RawPre-small.pt | e54e8c7e11e067adcbc08bcc1186c7cd4a6ca89d7ac609975bafbdc3a2c6e2de | 0.414490 | 0.280519 | 0.000008 | 0.000000 | 0.000000 |
| main/f1/vless/G2/outer | vless | G2 | 1 | RawPost-small | outputs/small-view-attribution-20261010/run-02/models/main/f1/vless/G2/outer/RawPost-small.pt | 6b5c798c2b3c912eec438e2333dab8dc604e88246dcca654a6200f921f818f2a | 0.288251 | 0.266944 | 0.000006 | 0.000000 | 0.000000 |
| main/f1/vless/G2/outer | vless | G2 | 1 | Marginal-small | outputs/small-view-attribution-20261010/run-02/models/main/f1/vless/G2/outer/Marginal-small.pt | 17e2f9a96d5441d3bf06c8436707a5782fce7ea4034962a7806f95db7ae76c48 | 0.269832 | 0.299834 | 0.000010 | 0.000000 | 0.000000 |
| main/f1/trojan/G0/outer | trojan | G0 | 1 | RawPre-small | outputs/small-view-attribution-20261010/run-02/models/main/f1/trojan/G0/outer/RawPre-small.pt | 793a468f787ce835f0a7406c4896a5121d68ae6ebf3589b6db45360799fca67e | 0.434530 | 0.286397 | 0.000010 | 0.000000 | 0.000000 |
| main/f1/trojan/G0/outer | trojan | G0 | 1 | RawPost-small | outputs/small-view-attribution-20261010/run-02/models/main/f1/trojan/G0/outer/RawPost-small.pt | 654d9fb730c8e36bad408dfdab682099aaaab3c7398d5125d0d0e006d362790e | 0.331326 | 0.271157 | 0.000007 | 0.000000 | 0.000000 |
| main/f1/trojan/G0/outer | trojan | G0 | 1 | Marginal-small | outputs/small-view-attribution-20261010/run-02/models/main/f1/trojan/G0/outer/Marginal-small.pt | a81f1b8a184d6053ab83b055a345c79b7c20af6871c788fa825c4893dd7b6bff | 0.385916 | 0.302879 | 0.000010 | 0.000000 | 0.000000 |
| main/f1/trojan/G1/outer | trojan | G1 | 1 | RawPre-small | outputs/small-view-attribution-20261010/run-02/models/main/f1/trojan/G1/outer/RawPre-small.pt | 08f04b5b1a4a9a45acdb8d591b4386f6f6d1072ee0cea95366ce4a736f1d5597 | 0.605980 | 0.281090 | 0.000009 | 0.000000 | 0.000000 |
| main/f1/trojan/G1/outer | trojan | G1 | 1 | RawPost-small | outputs/small-view-attribution-20261010/run-02/models/main/f1/trojan/G1/outer/RawPost-small.pt | cdc7587e750d61f91d94944443524ff5516ee12a02f5eb150ab932c42a33e90b | 0.422211 | 0.263426 | 0.000009 | 0.000000 | 0.000000 |
| main/f1/trojan/G1/outer | trojan | G1 | 1 | Marginal-small | outputs/small-view-attribution-20261010/run-02/models/main/f1/trojan/G1/outer/Marginal-small.pt | 44cac201dd854bdebb2f20c2aa2e5c5da536a64960a284a7e627a6eff23b0a5f | 0.362763 | 0.304093 | 0.000010 | 0.000000 | 0.000000 |
| main/f1/trojan/G2/outer | trojan | G2 | 1 | RawPre-small | outputs/small-view-attribution-20261010/run-02/models/main/f1/trojan/G2/outer/RawPre-small.pt | a1e39cf24e845e37712e6d6fbef37c1e3942f13b1d19246a1484303c46cf985d | 0.598215 | 0.208977 | 0.000009 | 0.000000 | 0.000000 |
| main/f1/trojan/G2/outer | trojan | G2 | 1 | RawPost-small | outputs/small-view-attribution-20261010/run-02/models/main/f1/trojan/G2/outer/RawPost-small.pt | a6bb6b4a5ac19c30b1b0ba0ec2b03ffa8737cb0b94f9475bf56cca807383d328 | 0.327791 | 0.193802 | 0.000009 | 0.000000 | 0.000000 |
| main/f1/trojan/G2/outer | trojan | G2 | 1 | Marginal-small | outputs/small-view-attribution-20261010/run-02/models/main/f1/trojan/G2/outer/Marginal-small.pt | 18daf7d889c5b748b9fcce42f935ca0ea3ac51d31486983e0f3f4669bb63217d | 0.331913 | 0.225781 | 0.000009 | 0.000000 | 0.000000 |
| main/f1/vmess/G0/outer | vmess | G0 | 1 | RawPre-small | outputs/small-view-attribution-20261010/run-02/models/main/f1/vmess/G0/outer/RawPre-small.pt | 0540ba2b23810b8f3afee0081443b91727dcc1d00958408ced46ce82ff937c2d | 0.298706 | 0.289616 | 0.000009 | 0.000000 | 0.000000 |
| main/f1/vmess/G0/outer | vmess | G0 | 1 | RawPost-small | outputs/small-view-attribution-20261010/run-02/models/main/f1/vmess/G0/outer/RawPost-small.pt | 224f576dcfcf889c04892c6165ac716777c4f631ac157c0c4a3b020799636d7f | 0.255098 | 0.272038 | 0.000009 | 0.000000 | 0.000000 |
| main/f1/vmess/G0/outer | vmess | G0 | 1 | Marginal-small | outputs/small-view-attribution-20261010/run-02/models/main/f1/vmess/G0/outer/Marginal-small.pt | f81b286f12cd5bf7968f6d5b91c156559618114c3b479a68848296c101a82174 | 0.223973 | 0.300253 | 0.000010 | 0.000000 | 0.000000 |
| main/f1/vmess/G1/outer | vmess | G1 | 1 | RawPre-small | outputs/small-view-attribution-20261010/run-02/models/main/f1/vmess/G1/outer/RawPre-small.pt | 0359bb3aa77bc074073047d57ca1c6f463f33ef1633cf041a920ebad7dbb8a7f | 1.516034 | 0.145125 | 0.000008 | 0.000000 | 0.000000 |
| main/f1/vmess/G1/outer | vmess | G1 | 1 | RawPost-small | outputs/small-view-attribution-20261010/run-02/models/main/f1/vmess/G1/outer/RawPost-small.pt | 7d73e1de00d8e31a5c4f92cf025ff9d10c95c0b940ff332af19538835311331d | 0.906624 | 0.128585 | 0.000010 | 0.000000 | 0.000000 |
| main/f1/vmess/G1/outer | vmess | G1 | 1 | Marginal-small | outputs/small-view-attribution-20261010/run-02/models/main/f1/vmess/G1/outer/Marginal-small.pt | 54454515b0d787c245db09c45f4b29086f0b2efdc83ebe6a09669841cc6a3ed7 | 0.867200 | 0.158603 | 0.000009 | 0.000000 | 0.000000 |
| main/f1/vmess/G2/outer | vmess | G2 | 1 | RawPre-small | outputs/small-view-attribution-20261010/run-02/models/main/f1/vmess/G2/outer/RawPre-small.pt | 21a9534dce35babfbc50cf2ff517b7609878fd16e0b0423e07d78362c6e2f851 | 0.833297 | 0.212030 | 0.000009 | 0.000000 | 0.000000 |
| main/f1/vmess/G2/outer | vmess | G2 | 1 | RawPost-small | outputs/small-view-attribution-20261010/run-02/models/main/f1/vmess/G2/outer/RawPost-small.pt | d7f5505da54090c79638250f5dddc4ee02816dc055692ff8df7bc3fc301b68e2 | 0.585687 | 0.191905 | 0.000009 | 0.000000 | 0.000000 |
| main/f1/vmess/G2/outer | vmess | G2 | 1 | Marginal-small | outputs/small-view-attribution-20261010/run-02/models/main/f1/vmess/G2/outer/Marginal-small.pt | 68420d1ecfbc54df469ba6b7053b7ace1e34aa46353c815c1d3e885e07515de3 | 0.702923 | 0.227979 | 0.000009 | 0.000000 | 0.000000 |
| main/f2/shadowsocks/G0/outer | shadowsocks | G0 | 2 | RawPre-small | outputs/small-view-attribution-20261010/run-02/models/main/f2/shadowsocks/G0/outer/RawPre-small.pt | 552330b5afb04ded310bd9fc4a98ac3b3ae4d57af3be445687dd3cb6677be5ca | 0.476898 | 0.269630 | 0.000008 | 0.000000 | 0.000000 |
| main/f2/shadowsocks/G0/outer | shadowsocks | G0 | 2 | RawPost-small | outputs/small-view-attribution-20261010/run-02/models/main/f2/shadowsocks/G0/outer/RawPost-small.pt | e3707dcae878c6838739748954b9d7bd9a951a87a6899aa0d033aa1f5ee5dacb | 0.361468 | 0.255135 | 0.000010 | 0.000000 | 0.000000 |
| main/f2/shadowsocks/G0/outer | shadowsocks | G0 | 2 | Marginal-small | outputs/small-view-attribution-20261010/run-02/models/main/f2/shadowsocks/G0/outer/Marginal-small.pt | 159881ade06e582163a98606387dd63c7bb22757263f315a4753499416bce0cc | 0.304218 | 0.283271 | 0.000010 | 0.000000 | 0.000000 |
| main/f2/shadowsocks/G1/outer | shadowsocks | G1 | 2 | RawPre-small | outputs/small-view-attribution-20261010/run-02/models/main/f2/shadowsocks/G1/outer/RawPre-small.pt | ac0a02eb88f51e873df0e02c211c7a4616d1106867f3b32994695fbb7469f9bd | 0.360308 | 0.273267 | 0.000009 | 0.000000 | 0.000000 |
| main/f2/shadowsocks/G1/outer | shadowsocks | G1 | 2 | RawPost-small | outputs/small-view-attribution-20261010/run-02/models/main/f2/shadowsocks/G1/outer/RawPost-small.pt | bb2969b6ad76103c296bb7d1deeb9fb397edd99e313ef588af471d475cf839de | 0.283378 | 0.253760 | 0.000009 | 0.000000 | 0.000000 |
| main/f2/shadowsocks/G1/outer | shadowsocks | G1 | 2 | Marginal-small | outputs/small-view-attribution-20261010/run-02/models/main/f2/shadowsocks/G1/outer/Marginal-small.pt | 2ed3a073baf94201f0ed9711891e0139dbcb0886b78f84a1476a93799b9f03dd | 0.316801 | 0.302575 | 0.000008 | 0.000000 | 0.000000 |
| main/f2/shadowsocks/G2/outer | shadowsocks | G2 | 2 | RawPre-small | outputs/small-view-attribution-20261010/run-02/models/main/f2/shadowsocks/G2/outer/RawPre-small.pt | 38d3bb41f5285214a0586c33bbc4f2878404e624b100a5189aa786e04d9298da | 1.224379 | 0.170373 | 0.000010 | 0.000000 | 0.000000 |
| main/f2/shadowsocks/G2/outer | shadowsocks | G2 | 2 | RawPost-small | outputs/small-view-attribution-20261010/run-02/models/main/f2/shadowsocks/G2/outer/RawPost-small.pt | 81689f1fb8a6175bc071afcc29d18b6d4dfe043b17d899a5f7ca8446fee5a26f | 0.719030 | 0.149601 | 0.000010 | 0.000000 | 0.000000 |
| main/f2/shadowsocks/G2/outer | shadowsocks | G2 | 2 | Marginal-small | outputs/small-view-attribution-20261010/run-02/models/main/f2/shadowsocks/G2/outer/Marginal-small.pt | 7cb489a0e30f63b033ea6568f9984a922aa0fcedf472f6c4661a2c5610f16662 | 0.756962 | 0.185462 | 0.000009 | 0.000000 | 0.000000 |
| main/f2/vless/G0/outer | vless | G0 | 2 | RawPre-small | outputs/small-view-attribution-20261010/run-02/models/main/f2/vless/G0/outer/RawPre-small.pt | e3763d6ebb3990cf353db5e216d6d64f8d000c2491576853b1da25c6a6a112eb | 0.449840 | 0.262511 | 0.000007 | 0.000000 | 0.000000 |
| main/f2/vless/G0/outer | vless | G0 | 2 | RawPost-small | outputs/small-view-attribution-20261010/run-02/models/main/f2/vless/G0/outer/RawPost-small.pt | f80b23c567bd9b1992bdbfcbaca44aaa3b9061a423b3fa731a3251d0a3d5d6c1 | 0.368854 | 0.249461 | 0.000006 | 0.000000 | 0.000000 |
| main/f2/vless/G0/outer | vless | G0 | 2 | Marginal-small | outputs/small-view-attribution-20261010/run-02/models/main/f2/vless/G0/outer/Marginal-small.pt | 51c72771227e152d64284a394b4ef2f10fb9a421c5a5ff201d1ba8e797ba89d2 | 0.336973 | 0.285682 | 0.000009 | 0.000000 | 0.000000 |
| main/f2/vless/G1/outer | vless | G1 | 2 | RawPre-small | outputs/small-view-attribution-20261010/run-02/models/main/f2/vless/G1/outer/RawPre-small.pt | b755cf885281ac9a68c1583085daa506ed41e59bab8bf13ee9ace7dfd75e21e7 | 1.238805 | 0.160430 | 0.000009 | 0.000000 | 0.000000 |
| main/f2/vless/G1/outer | vless | G1 | 2 | RawPost-small | outputs/small-view-attribution-20261010/run-02/models/main/f2/vless/G1/outer/RawPost-small.pt | 69e4af130afa00bfbff6352b447345761448b3fd57db86b89827b329e44f86cf | 0.780713 | 0.146358 | 0.000007 | 0.000000 | 0.000000 |
| main/f2/vless/G1/outer | vless | G1 | 2 | Marginal-small | outputs/small-view-attribution-20261010/run-02/models/main/f2/vless/G1/outer/Marginal-small.pt | dcb177b0ce807846506e3ea1771fa44df657888059a5fd2feb74eaa5895742f7 | 0.871905 | 0.189717 | 0.000008 | 0.000000 | 0.000000 |
| main/f2/vless/G2/outer | vless | G2 | 2 | RawPre-small | outputs/small-view-attribution-20261010/run-02/models/main/f2/vless/G2/outer/RawPre-small.pt | 38ef22b5434fb1771e520433c2ab5d059f16af9e27f3b862582321a7d9e67859 | 0.411979 | 0.283059 | 0.000007 | 0.000000 | 0.000000 |
| main/f2/vless/G2/outer | vless | G2 | 2 | RawPost-small | outputs/small-view-attribution-20261010/run-02/models/main/f2/vless/G2/outer/RawPost-small.pt | fd7fb2424ade81a9993b908f91b671e8c90250e07ce5b7a7c17c066dd63b88d9 | 0.268633 | 0.268720 | 0.000010 | 0.000000 | 0.000000 |
| main/f2/vless/G2/outer | vless | G2 | 2 | Marginal-small | outputs/small-view-attribution-20261010/run-02/models/main/f2/vless/G2/outer/Marginal-small.pt | 120597f1724ec3fc21c9c273c046070b756b69b609b6a869a72ad5e637383294 | 0.280140 | 0.302903 | 0.000009 | 0.000000 | 0.000000 |
| main/f2/trojan/G0/outer | trojan | G0 | 2 | RawPre-small | outputs/small-view-attribution-20261010/run-02/models/main/f2/trojan/G0/outer/RawPre-small.pt | a742235546f81f9e9dbdb8602050b549f21cb26be78beaab345966d6d2bd21ce | 0.349992 | 0.285606 | 0.000010 | 0.000000 | 0.000000 |
| main/f2/trojan/G0/outer | trojan | G0 | 2 | RawPost-small | outputs/small-view-attribution-20261010/run-02/models/main/f2/trojan/G0/outer/RawPost-small.pt | 5051d5ee8ad4f697d590690e18267c645d3f263ae2567b09668e5d60091947e3 | 0.374385 | 0.270175 | 0.000009 | 0.000000 | 0.000000 |
| main/f2/trojan/G0/outer | trojan | G0 | 2 | Marginal-small | outputs/small-view-attribution-20261010/run-02/models/main/f2/trojan/G0/outer/Marginal-small.pt | d3b13ecfc5bd226ba9fac62733ff4a525fa03b89b1ecca11e08e83670f167360 | 0.332865 | 0.305923 | 0.000008 | 0.000000 | 0.000000 |
| main/f2/trojan/G1/outer | trojan | G1 | 2 | RawPre-small | outputs/small-view-attribution-20261010/run-02/models/main/f2/trojan/G1/outer/RawPre-small.pt | 4e44c2e4ed82adad9556e0a6ebdaee1d6a84283efd955c76d282961539cb48f4 | 1.616103 | 0.164850 | 0.000009 | 0.000000 | 0.000000 |
| main/f2/trojan/G1/outer | trojan | G1 | 2 | RawPost-small | outputs/small-view-attribution-20261010/run-02/models/main/f2/trojan/G1/outer/RawPost-small.pt | 8c05a0e852658eabdda70b7d676a42229e44431d0a3942de16007b425ae57c4b | 0.884388 | 0.144994 | 0.000009 | 0.000000 | 0.000000 |
| main/f2/trojan/G1/outer | trojan | G1 | 2 | Marginal-small | outputs/small-view-attribution-20261010/run-02/models/main/f2/trojan/G1/outer/Marginal-small.pt | 3ddfde9f9b24e9df24bd812c50232666291196bcfa84bd7b6811d69c1ef45f75 | 1.022852 | 0.198507 | 0.000009 | 0.000000 | 0.000000 |
| main/f2/trojan/G2/outer | trojan | G2 | 2 | RawPre-small | outputs/small-view-attribution-20261010/run-02/models/main/f2/trojan/G2/outer/RawPre-small.pt | 7c85f2f9c03756d9402b89de0e7d8a6b62dea443e28bd2c803851d90989bbe22 | 0.413969 | 0.269600 | 0.000008 | 0.000000 | 0.000000 |
| main/f2/trojan/G2/outer | trojan | G2 | 2 | RawPost-small | outputs/small-view-attribution-20261010/run-02/models/main/f2/trojan/G2/outer/RawPost-small.pt | 38081f073e155317910d4a97d8bb91a2bd3a23c4ed7dbb7f6522cc09502cc63b | 0.351797 | 0.254602 | 0.000009 | 0.000000 | 0.000000 |
| main/f2/trojan/G2/outer | trojan | G2 | 2 | Marginal-small | outputs/small-view-attribution-20261010/run-02/models/main/f2/trojan/G2/outer/Marginal-small.pt | 5732787181f16317b02e9843b1352e33f9f5e0808e167e4627816163251861a0 | 0.284067 | 0.290177 | 0.000010 | 0.000000 | 0.000000 |
| main/f2/vmess/G0/outer | vmess | G0 | 2 | RawPre-small | outputs/small-view-attribution-20261010/run-02/models/main/f2/vmess/G0/outer/RawPre-small.pt | dde802aa6234267a2733d31d0bf5f8df930feae8a84e64c0c6f19a080c1f6769 | 1.213841 | 0.172408 | 0.000009 | 0.000000 | 0.000000 |
| main/f2/vmess/G0/outer | vmess | G0 | 2 | RawPost-small | outputs/small-view-attribution-20261010/run-02/models/main/f2/vmess/G0/outer/RawPost-small.pt | a2245c5181497a1d705ae837fc4e4bdc8b44fc8a26e64d38d89df6d48c6d3a1b | 0.821525 | 0.156141 | 0.000009 | 0.000000 | 0.000000 |
| main/f2/vmess/G0/outer | vmess | G0 | 2 | Marginal-small | outputs/small-view-attribution-20261010/run-02/models/main/f2/vmess/G0/outer/Marginal-small.pt | ea120adc012195ea1cce9293dfc8413a2934f43999c6f6f018b3a21baccb3d33 | 0.784185 | 0.189268 | 0.000009 | 0.000000 | 0.000000 |
| main/f2/vmess/G1/outer | vmess | G1 | 2 | RawPre-small | outputs/small-view-attribution-20261010/run-02/models/main/f2/vmess/G1/outer/RawPre-small.pt | 3150cface0542444020e82f37d2804e8dada1c4ab3af40c3d11689e985f32704 | 0.483396 | 0.282755 | 0.000005 | 0.000000 | 0.000000 |
| main/f2/vmess/G1/outer | vmess | G1 | 2 | RawPost-small | outputs/small-view-attribution-20261010/run-02/models/main/f2/vmess/G1/outer/RawPost-small.pt | 04b956c2a32191da5c0612f7c73632feb0b22c23299718961b9d85e406f75343 | 0.375129 | 0.268105 | 0.000009 | 0.000000 | 0.000000 |
| main/f2/vmess/G1/outer | vmess | G1 | 2 | Marginal-small | outputs/small-view-attribution-20261010/run-02/models/main/f2/vmess/G1/outer/Marginal-small.pt | c721263a90bc78efe8225f0854531349e4d1bb07b1f0491bc03e9e7c9add44a1 | 0.323217 | 0.303831 | 0.000009 | 0.000000 | 0.000000 |
| main/f2/vmess/G2/outer | vmess | G2 | 2 | RawPre-small | outputs/small-view-attribution-20261010/run-02/models/main/f2/vmess/G2/outer/RawPre-small.pt | 915649ed6654e4ae587371ba56272a51694acb36b11d467a7f8c5589fbf7ff9d | 0.542592 | 0.269481 | 0.000009 | 0.000000 | 0.000000 |
| main/f2/vmess/G2/outer | vmess | G2 | 2 | RawPost-small | outputs/small-view-attribution-20261010/run-02/models/main/f2/vmess/G2/outer/RawPost-small.pt | 7091375f450c865bdb8bbc812313582cd6d67f7b01094d7aa84e8a1bfef97208 | 0.371149 | 0.253056 | 0.000009 | 0.000000 | 0.000000 |
| main/f2/vmess/G2/outer | vmess | G2 | 2 | Marginal-small | outputs/small-view-attribution-20261010/run-02/models/main/f2/vmess/G2/outer/Marginal-small.pt | 91f54060f797423d0734c1abcbb294812bdd9d0506459da18019eb046ab98fed | 0.385981 | 0.289069 | 0.000008 | 0.000000 | 0.000000 |
| main/f3/shadowsocks/G0/outer | shadowsocks | G0 | 3 | RawPre-small | outputs/small-view-attribution-20261010/run-02/models/main/f3/shadowsocks/G0/outer/RawPre-small.pt | 5be7339287d1380fcfa38f0e64a6a7accd820f86d43d1c499bf9c9df14d92c7a | 0.496850 | 0.277973 | 0.000007 | 0.000000 | 0.000000 |
| main/f3/shadowsocks/G0/outer | shadowsocks | G0 | 3 | RawPost-small | outputs/small-view-attribution-20261010/run-02/models/main/f3/shadowsocks/G0/outer/RawPost-small.pt | ec8605c0e2c9730890c8d21ac26142c6bea8b4a6da72d08c64faeb6c2f4dcba0 | 0.345016 | 0.255208 | 0.000010 | 0.000000 | 0.000000 |
| main/f3/shadowsocks/G0/outer | shadowsocks | G0 | 3 | Marginal-small | outputs/small-view-attribution-20261010/run-02/models/main/f3/shadowsocks/G0/outer/Marginal-small.pt | 862aaf0b9481033a9a634c39fcac6ac06f4d205c2b2e2902cbd6a3c4c8585387 | 0.376364 | 0.292843 | 0.000009 | 0.000000 | 0.000000 |
| main/f3/shadowsocks/G1/outer | shadowsocks | G1 | 3 | RawPre-small | outputs/small-view-attribution-20261010/run-02/models/main/f3/shadowsocks/G1/outer/RawPre-small.pt | 233aaa7d042b08471b28592e5909534cbb5ff814bedb38c17759449295f2b8cf | 0.627699 | 0.277421 | 0.000008 | 0.000000 | 0.000000 |
| main/f3/shadowsocks/G1/outer | shadowsocks | G1 | 3 | RawPost-small | outputs/small-view-attribution-20261010/run-02/models/main/f3/shadowsocks/G1/outer/RawPost-small.pt | 95a093da145e87274a4964c14e1296b9f8122252a5d34b4820f4005110b7bf4e | 0.442956 | 0.253283 | 0.000008 | 0.000000 | 0.000000 |
| main/f3/shadowsocks/G1/outer | shadowsocks | G1 | 3 | Marginal-small | outputs/small-view-attribution-20261010/run-02/models/main/f3/shadowsocks/G1/outer/Marginal-small.pt | b57e54c552352f1332ab8cd2bc26eb72f061193a5d650ce1e3fe827abbc11f1b | 0.397784 | 0.308789 | 0.000010 | 0.000000 | 0.000000 |
| main/f3/shadowsocks/G2/outer | shadowsocks | G2 | 3 | RawPre-small | outputs/small-view-attribution-20261010/run-02/models/main/f3/shadowsocks/G2/outer/RawPre-small.pt | 6d472c4708d1376338e989b39b0713aa0a61fa07db75faf35e1d43558a8d6bef | 0.484705 | 0.260613 | 0.000009 | 0.000000 | 0.000000 |
| main/f3/shadowsocks/G2/outer | shadowsocks | G2 | 3 | RawPost-small | outputs/small-view-attribution-20261010/run-02/models/main/f3/shadowsocks/G2/outer/RawPost-small.pt | 58d6b180d6182937dbde43fa59ba0402ded802edefe7d0f3b7723a1373c4d9a8 | 0.346652 | 0.239005 | 0.000009 | 0.000000 | 0.000000 |
| main/f3/shadowsocks/G2/outer | shadowsocks | G2 | 3 | Marginal-small | outputs/small-view-attribution-20261010/run-02/models/main/f3/shadowsocks/G2/outer/Marginal-small.pt | dc239f896f33c578e22b386760ff91c977e0da8ac1df06d75b061cd3455f0e57 | 0.360123 | 0.282579 | 0.000008 | 0.000000 | 0.000000 |
| main/f3/vless/G0/outer | vless | G0 | 3 | RawPre-small | outputs/small-view-attribution-20261010/run-02/models/main/f3/vless/G0/outer/RawPre-small.pt | 0100e739828837d61321ca3614b705ef09b8024d7e4794e78e20b62f4a5ed70b | 0.599302 | 0.265935 | 0.000006 | 0.000000 | 0.000000 |
| main/f3/vless/G0/outer | vless | G0 | 3 | RawPost-small | outputs/small-view-attribution-20261010/run-02/models/main/f3/vless/G0/outer/RawPost-small.pt | 61a4b805f1e22e742601472b0e7c7370026a5f168ff630dcfaa39ef9d6168c30 | 0.381149 | 0.250293 | 0.000009 | 0.000000 | 0.000000 |
| main/f3/vless/G0/outer | vless | G0 | 3 | Marginal-small | outputs/small-view-attribution-20261010/run-02/models/main/f3/vless/G0/outer/Marginal-small.pt | 5c4469c3c63a40abe1bb748d50b85cfd450a903c481c2283a7f8b00e4364e69e | 0.356228 | 0.288374 | 0.000009 | 0.000000 | 0.000000 |
| main/f3/vless/G1/outer | vless | G1 | 3 | RawPre-small | outputs/small-view-attribution-20261010/run-02/models/main/f3/vless/G1/outer/RawPre-small.pt | 1329bc0089186c7cb5c09487f17018fb29b414159caebafc8f6e4085d4a1feb8 | 1.014981 | 0.218066 | 0.000009 | 0.000000 | 0.000000 |
| main/f3/vless/G1/outer | vless | G1 | 3 | RawPost-small | outputs/small-view-attribution-20261010/run-02/models/main/f3/vless/G1/outer/RawPost-small.pt | 229430107d31f47ce202565065ffb44db81354e804d867e1c5fd4182201871b0 | 0.539086 | 0.198670 | 0.000009 | 0.000000 | 0.000000 |
| main/f3/vless/G1/outer | vless | G1 | 3 | Marginal-small | outputs/small-view-attribution-20261010/run-02/models/main/f3/vless/G1/outer/Marginal-small.pt | 6f72a2753407a6e116d0f87de1fc6382f22534f5a63fd8b838aa927b88759fd8 | 0.713490 | 0.241782 | 0.000009 | 0.000000 | 0.000000 |
| main/f3/vless/G2/outer | vless | G2 | 3 | RawPre-small | outputs/small-view-attribution-20261010/run-02/models/main/f3/vless/G2/outer/RawPre-small.pt | d1d5612d9e38d40b4f51a933f6a925e91125c6fdf3be71eaa553ff594b8aed06 | 0.448003 | 0.279887 | 0.000008 | 0.000000 | 0.000000 |
| main/f3/vless/G2/outer | vless | G2 | 3 | RawPost-small | outputs/small-view-attribution-20261010/run-02/models/main/f3/vless/G2/outer/RawPost-small.pt | 59f5f0112656e89fd9e28c0f7671d0ec53173db8179ae825b1151421872c7dc3 | 0.305405 | 0.260894 | 0.000009 | 0.000000 | 0.000000 |
| main/f3/vless/G2/outer | vless | G2 | 3 | Marginal-small | outputs/small-view-attribution-20261010/run-02/models/main/f3/vless/G2/outer/Marginal-small.pt | 7a0de755191d7d1d8c8175a4e8e4a7d26bf6e7cf4081d0c99e0639e8d6488a16 | 0.324085 | 0.294739 | 0.000007 | 0.000000 | 0.000000 |
| main/f3/trojan/G0/outer | trojan | G0 | 3 | RawPre-small | outputs/small-view-attribution-20261010/run-02/models/main/f3/trojan/G0/outer/RawPre-small.pt | 7151b0659db24ca15698b14a0ca76494b256e73bf993384f5e4bf946f39f1b1a | 0.788183 | 0.218900 | 0.000010 | 0.000000 | 0.000000 |
| main/f3/trojan/G0/outer | trojan | G0 | 3 | RawPost-small | outputs/small-view-attribution-20261010/run-02/models/main/f3/trojan/G0/outer/RawPost-small.pt | c5e9823a3f408fd2af7dd9c389c788eee0a3e156c9e197d275d9508c5d5a95a2 | 0.608923 | 0.197087 | 0.000010 | 0.000000 | 0.000000 |
| main/f3/trojan/G0/outer | trojan | G0 | 3 | Marginal-small | outputs/small-view-attribution-20261010/run-02/models/main/f3/trojan/G0/outer/Marginal-small.pt | 0009dbad9022a57e86ff591fbda63941fcf78621d680ffbf152025a53bf51fc5 | 0.487777 | 0.239349 | 0.000008 | 0.000000 | 0.000000 |
| main/f3/trojan/G1/outer | trojan | G1 | 3 | RawPre-small | outputs/small-view-attribution-20261010/run-02/models/main/f3/trojan/G1/outer/RawPre-small.pt | 045924be5e2e99cb9a7cdab6c27967e757bcc5e4fc4847ff2d550fb80dc15e91 | 0.705099 | 0.291576 | 0.000005 | 0.000000 | 0.000000 |
| main/f3/trojan/G1/outer | trojan | G1 | 3 | RawPost-small | outputs/small-view-attribution-20261010/run-02/models/main/f3/trojan/G1/outer/RawPost-small.pt | 2082e07610974452f76e3fb104a199f9cfc3092cb80a93ee13a439fc9a66ea5f | 0.417226 | 0.272358 | 0.000009 | 0.000000 | 0.000000 |
| main/f3/trojan/G1/outer | trojan | G1 | 3 | Marginal-small | outputs/small-view-attribution-20261010/run-02/models/main/f3/trojan/G1/outer/Marginal-small.pt | 9d43637dce920b34403422c6df47da72f02f47d5a5f2b86dab029ade2d6f295d | 0.414444 | 0.323805 | 0.000010 | 0.000000 | 0.000000 |
| main/f3/trojan/G2/outer | trojan | G2 | 3 | RawPre-small | outputs/small-view-attribution-20261010/run-02/models/main/f3/trojan/G2/outer/RawPre-small.pt | e5acefe67259a9e8e238d9e033639d9c24543fc1355478c20071087eb95b9573 | 0.450153 | 0.272840 | 0.000010 | 0.000000 | 0.000000 |
| main/f3/trojan/G2/outer | trojan | G2 | 3 | RawPost-small | outputs/small-view-attribution-20261010/run-02/models/main/f3/trojan/G2/outer/RawPost-small.pt | 8b36de3cd391371f23d5daecc4404a689db75930eea38618d64d2f4a55d41d8d | 0.384698 | 0.256026 | 0.000008 | 0.000000 | 0.000000 |
| main/f3/trojan/G2/outer | trojan | G2 | 3 | Marginal-small | outputs/small-view-attribution-20261010/run-02/models/main/f3/trojan/G2/outer/Marginal-small.pt | dcfe4be801c0d1f71912a3c8923a99703610f927fd83f9bfd24267e95779b4c7 | 0.342767 | 0.294924 | 0.000007 | 0.000000 | 0.000000 |
| main/f3/vmess/G0/outer | vmess | G0 | 3 | RawPre-small | outputs/small-view-attribution-20261010/run-02/models/main/f3/vmess/G0/outer/RawPre-small.pt | 6c6c9580465dc90ca63077d6245b7d03ddd29b4d0db0f069ed525bd9073048d1 | 0.432190 | 0.293942 | 0.000008 | 0.000000 | 0.000000 |
| main/f3/vmess/G0/outer | vmess | G0 | 3 | RawPost-small | outputs/small-view-attribution-20261010/run-02/models/main/f3/vmess/G0/outer/RawPost-small.pt | 00f4be5f81ea8aa4a1de6f6125600157df39936bfad62430e8501d67d71cd242 | 0.338840 | 0.270160 | 0.000008 | 0.000000 | 0.000000 |
| main/f3/vmess/G0/outer | vmess | G0 | 3 | Marginal-small | outputs/small-view-attribution-20261010/run-02/models/main/f3/vmess/G0/outer/Marginal-small.pt | 59d2576f802b589dec3fee78f321f1609a52eb62a1bf21a340a33a0f32ecc85b | 0.295183 | 0.307488 | 0.000009 | 0.000000 | 0.000000 |
| main/f3/vmess/G1/outer | vmess | G1 | 3 | RawPre-small | outputs/small-view-attribution-20261010/run-02/models/main/f3/vmess/G1/outer/RawPre-small.pt | a24c86de14631f554af4e342019f7faea63d824e1513b5800f19b1b175fc6b8b | 0.591393 | 0.264767 | 0.000006 | 0.000000 | 0.000000 |
| main/f3/vmess/G1/outer | vmess | G1 | 3 | RawPost-small | outputs/small-view-attribution-20261010/run-02/models/main/f3/vmess/G1/outer/RawPost-small.pt | 10dcdccde68bb05d84cbd8c74815b78d1e678ada75d15d369448dc500955e948 | 0.315410 | 0.242722 | 0.000010 | 0.000000 | 0.000000 |
| main/f3/vmess/G1/outer | vmess | G1 | 3 | Marginal-small | outputs/small-view-attribution-20261010/run-02/models/main/f3/vmess/G1/outer/Marginal-small.pt | 52ac18d0fa9ea7d90ec8b9103367203670752a5a3ad2e54cf12bc5e71dbd1f74 | 0.340181 | 0.284951 | 0.000008 | 0.000000 | 0.000000 |
| main/f3/vmess/G2/outer | vmess | G2 | 3 | RawPre-small | outputs/small-view-attribution-20261010/run-02/models/main/f3/vmess/G2/outer/RawPre-small.pt | 62fd25a2fa10eb0cc68ac0c8b73a8975dfe145be8dbe63e4228dcc47f1315551 | 0.530266 | 0.304365 | 0.000006 | 0.000000 | 0.000000 |
| main/f3/vmess/G2/outer | vmess | G2 | 3 | RawPost-small | outputs/small-view-attribution-20261010/run-02/models/main/f3/vmess/G2/outer/RawPost-small.pt | 04081e736a03ac4cc4114f10f7aa7269d86a893dc13ac6877c657e28a2c32336 | 0.308707 | 0.282303 | 0.000010 | 0.000000 | 0.000000 |
| main/f3/vmess/G2/outer | vmess | G2 | 3 | Marginal-small | outputs/small-view-attribution-20261010/run-02/models/main/f3/vmess/G2/outer/Marginal-small.pt | d329c6c716c9d0324a5c7ec69923ad24d6555b1deb5d1fccb45429a0cf61ab5c | 0.472530 | 0.320700 | 0.000009 | 0.000000 | 0.000000 |
| main/f4/shadowsocks/G0/outer | shadowsocks | G0 | 4 | RawPre-small | outputs/small-view-attribution-20261010/run-02/models/main/f4/shadowsocks/G0/outer/RawPre-small.pt | 23bba5649f1cfc660278b933595883d3df4c3f4e7f398e9043440c9eaceaeb8d | 0.508494 | 0.283554 | 0.000006 | 0.000000 | 0.000000 |
| main/f4/shadowsocks/G0/outer | shadowsocks | G0 | 4 | RawPost-small | outputs/small-view-attribution-20261010/run-02/models/main/f4/shadowsocks/G0/outer/RawPost-small.pt | 13093143111a4c26d2256b7731027109b395022acc1403cccec31a9a6ead03da | 0.431223 | 0.261429 | 0.000010 | 0.000000 | 0.000000 |
| main/f4/shadowsocks/G0/outer | shadowsocks | G0 | 4 | Marginal-small | outputs/small-view-attribution-20261010/run-02/models/main/f4/shadowsocks/G0/outer/Marginal-small.pt | 2d2ca8c559fdf0bb5da1c0956039d965c48c402531f70c87eb3b72d36c97e2ea | 0.350977 | 0.291565 | 0.000009 | 0.000000 | 0.000000 |
| main/f4/shadowsocks/G1/outer | shadowsocks | G1 | 4 | RawPre-small | outputs/small-view-attribution-20261010/run-02/models/main/f4/shadowsocks/G1/outer/RawPre-small.pt | 076adb5711e71116d9916fae6842d4a5f35f95738ce5cf67fd376c3dd3ce4099 | 0.494016 | 0.267684 | 0.000005 | 0.000000 | 0.000000 |
| main/f4/shadowsocks/G1/outer | shadowsocks | G1 | 4 | RawPost-small | outputs/small-view-attribution-20261010/run-02/models/main/f4/shadowsocks/G1/outer/RawPost-small.pt | 9c7cb3d65db3b416722da8c4b112a2657ba5f9e579e4e9906ca03c6d4cbc19c9 | 0.384351 | 0.248520 | 0.000009 | 0.000000 | 0.000000 |
| main/f4/shadowsocks/G1/outer | shadowsocks | G1 | 4 | Marginal-small | outputs/small-view-attribution-20261010/run-02/models/main/f4/shadowsocks/G1/outer/Marginal-small.pt | 6e0c919823b0b2522a037c032a5351e59e0ac360de88c7aeee3a94011e22240f | 0.382690 | 0.292945 | 0.000009 | 0.000000 | 0.000000 |
| main/f4/shadowsocks/G2/outer | shadowsocks | G2 | 4 | RawPre-small | outputs/small-view-attribution-20261010/run-02/models/main/f4/shadowsocks/G2/outer/RawPre-small.pt | ddec95eac3879512835a5686e31cfef43c33f03787000c5f853c7f300cbc4d62 | 0.528482 | 0.267753 | 0.000008 | 0.000000 | 0.000000 |
| main/f4/shadowsocks/G2/outer | shadowsocks | G2 | 4 | RawPost-small | outputs/small-view-attribution-20261010/run-02/models/main/f4/shadowsocks/G2/outer/RawPost-small.pt | fc5150a2e5b72f8a730c986312737b8316676669a7cfdc8c94edd158f585ead8 | 0.367618 | 0.246073 | 0.000010 | 0.000000 | 0.000000 |
| main/f4/shadowsocks/G2/outer | shadowsocks | G2 | 4 | Marginal-small | outputs/small-view-attribution-20261010/run-02/models/main/f4/shadowsocks/G2/outer/Marginal-small.pt | e569bdab2ceca34c4294a36908e20e51e4b94a103ccf1e2d1b36f896f0877424 | 0.377775 | 0.283780 | 0.000008 | 0.000000 | 0.000000 |
| main/f4/vless/G0/outer | vless | G0 | 4 | RawPre-small | outputs/small-view-attribution-20261010/run-02/models/main/f4/vless/G0/outer/RawPre-small.pt | ecef468dfab406b492f84dd112c247be01e095a4045794d5f31f072db51bd67f | 0.552202 | 0.258686 | 0.000007 | 0.000000 | 0.000000 |
| main/f4/vless/G0/outer | vless | G0 | 4 | RawPost-small | outputs/small-view-attribution-20261010/run-02/models/main/f4/vless/G0/outer/RawPost-small.pt | a40b3143620bf0c734c126fc2fbbd91f0adf81d0ea273843b4cefadd899e7dfc | 0.382487 | 0.242988 | 0.000008 | 0.000000 | 0.000000 |
| main/f4/vless/G0/outer | vless | G0 | 4 | Marginal-small | outputs/small-view-attribution-20261010/run-02/models/main/f4/vless/G0/outer/Marginal-small.pt | 3298ddae10bb27d97051dd6ceb8eca1d70d20916322b48d0d3cddd2ac06882c1 | 0.351729 | 0.281645 | 0.000010 | 0.000000 | 0.000000 |
| main/f4/vless/G1/outer | vless | G1 | 4 | RawPre-small | outputs/small-view-attribution-20261010/run-02/models/main/f4/vless/G1/outer/RawPre-small.pt | 983d52c05bc28464fcc66bca2cdff4ebfe1bda240bd6b005c1df5e4f1d2af1d9 | 0.595705 | 0.279639 | 0.000009 | 0.000000 | 0.000000 |
| main/f4/vless/G1/outer | vless | G1 | 4 | RawPost-small | outputs/small-view-attribution-20261010/run-02/models/main/f4/vless/G1/outer/RawPost-small.pt | 78c79dfea94e697722d22dcb05874fadf1540dc6342a4c325f08f75d5d59a44d | 0.387608 | 0.263337 | 0.000008 | 0.000000 | 0.000000 |
| main/f4/vless/G1/outer | vless | G1 | 4 | Marginal-small | outputs/small-view-attribution-20261010/run-02/models/main/f4/vless/G1/outer/Marginal-small.pt | e08f4812e354bae232fbf845bc796a5c8fe3122a0a054d8494e6ee800ae629d3 | 0.442415 | 0.307031 | 0.000010 | 0.000000 | 0.000000 |
| main/f4/vless/G2/outer | vless | G2 | 4 | RawPre-small | outputs/small-view-attribution-20261010/run-02/models/main/f4/vless/G2/outer/RawPre-small.pt | 4bfc453b68f2102c5f7eb9aa2077bb36c3f1eab3ea3a9e38121e17f6dd92775f | 0.463363 | 0.276463 | 0.000007 | 0.000000 | 0.000000 |
| main/f4/vless/G2/outer | vless | G2 | 4 | RawPost-small | outputs/small-view-attribution-20261010/run-02/models/main/f4/vless/G2/outer/RawPost-small.pt | fb6c164306c54930ccb292964b160f1679204ff0ad6af7815ce92e47e9bb2329 | 0.311630 | 0.257978 | 0.000010 | 0.000000 | 0.000000 |
| main/f4/vless/G2/outer | vless | G2 | 4 | Marginal-small | outputs/small-view-attribution-20261010/run-02/models/main/f4/vless/G2/outer/Marginal-small.pt | 9ec8deb1253f999e3eeede5f536cafb93b51bb854eea7b5df5cca2497be2cdf1 | 0.319961 | 0.295938 | 0.000010 | 0.000000 | 0.000000 |
| main/f4/trojan/G0/outer | trojan | G0 | 4 | RawPre-small | outputs/small-view-attribution-20261010/run-02/models/main/f4/trojan/G0/outer/RawPre-small.pt | b5e0d393bc0c096079305082438df2e2e914183a67ad9ff446c79c18641bbf99 | 0.464153 | 0.278154 | 0.000008 | 0.000000 | 0.000000 |
| main/f4/trojan/G0/outer | trojan | G0 | 4 | RawPost-small | outputs/small-view-attribution-20261010/run-02/models/main/f4/trojan/G0/outer/RawPost-small.pt | 12f276b334e479ec18eab5611ccfdbb1ba6fb88d40e0eddd239d7dee9e978208 | 0.377684 | 0.260043 | 0.000008 | 0.000000 | 0.000000 |
| main/f4/trojan/G0/outer | trojan | G0 | 4 | Marginal-small | outputs/small-view-attribution-20261010/run-02/models/main/f4/trojan/G0/outer/Marginal-small.pt | 13d57a29d232f5ee652e93b7c5ded2dd03e8e144f077bfb644462ee80ad144bb | 0.310477 | 0.298343 | 0.000008 | 0.000000 | 0.000000 |
| main/f4/trojan/G1/outer | trojan | G1 | 4 | RawPre-small | outputs/small-view-attribution-20261010/run-02/models/main/f4/trojan/G1/outer/RawPre-small.pt | fff46ba63a567c7ad07371873f4e80e0bded475bcb6c5497638494daeefd5dd3 | 1.442930 | 0.175050 | 0.000007 | 0.000000 | 0.000000 |
| main/f4/trojan/G1/outer | trojan | G1 | 4 | RawPost-small | outputs/small-view-attribution-20261010/run-02/models/main/f4/trojan/G1/outer/RawPost-small.pt | 2cb6d34b8b6be6bcdf73691745ce811e63a7c3956f4577f604fb83242bb171c6 | 0.708149 | 0.152753 | 0.000009 | 0.000000 | 0.000000 |
| main/f4/trojan/G1/outer | trojan | G1 | 4 | Marginal-small | outputs/small-view-attribution-20261010/run-02/models/main/f4/trojan/G1/outer/Marginal-small.pt | b8f36044910dda43ef4c254ea5ae54309131848cd0def70ca75fd34d96a9f083 | 0.789938 | 0.204648 | 0.000009 | 0.000000 | 0.000000 |
| main/f4/trojan/G2/outer | trojan | G2 | 4 | RawPre-small | outputs/small-view-attribution-20261010/run-02/models/main/f4/trojan/G2/outer/RawPre-small.pt | a21cf46d81adc7286fab3e4e8d1dddc5f04f2220fcba83e83e0a07dfc3ff403b | 0.459583 | 0.274427 | 0.000007 | 0.000000 | 0.000000 |
| main/f4/trojan/G2/outer | trojan | G2 | 4 | RawPost-small | outputs/small-view-attribution-20261010/run-02/models/main/f4/trojan/G2/outer/RawPost-small.pt | 7a1cc63be0d1ace3d1fd9b06789993a3a81eef056ead65acb0d235b6702a93fe | 0.347502 | 0.257587 | 0.000006 | 0.000000 | 0.000000 |
| main/f4/trojan/G2/outer | trojan | G2 | 4 | Marginal-small | outputs/small-view-attribution-20261010/run-02/models/main/f4/trojan/G2/outer/Marginal-small.pt | 3ec62b9e40fea30a226e3bf7e7ae40bc514508014020a5a8a5aa1adc2d6eccbc | 0.315128 | 0.297619 | 0.000009 | 0.000000 | 0.000000 |
| main/f4/vmess/G0/outer | vmess | G0 | 4 | RawPre-small | outputs/small-view-attribution-20261010/run-02/models/main/f4/vmess/G0/outer/RawPre-small.pt | 7d3df078c77b8a757f793599945ded6c2428dd895a16eadcd0e7760d0c274d97 | 0.846601 | 0.217926 | 0.000009 | 0.000000 | 0.000000 |
| main/f4/vmess/G0/outer | vmess | G0 | 4 | RawPost-small | outputs/small-view-attribution-20261010/run-02/models/main/f4/vmess/G0/outer/RawPost-small.pt | b0f92b71ec13345e171dd80c24aad5bed7dba9f4897fc36b0688bd2c301c6bed | 0.607814 | 0.195552 | 0.000008 | 0.000000 | 0.000000 |
| main/f4/vmess/G0/outer | vmess | G0 | 4 | Marginal-small | outputs/small-view-attribution-20261010/run-02/models/main/f4/vmess/G0/outer/Marginal-small.pt | 0892692a43d5b38815c9c0b636fd2381d0ea9d793527e3e8185cb65731e7d40d | 0.471216 | 0.229793 | 0.000009 | 0.000000 | 0.000000 |
| main/f4/vmess/G1/outer | vmess | G1 | 4 | RawPre-small | outputs/small-view-attribution-20261010/run-02/models/main/f4/vmess/G1/outer/RawPre-small.pt | ab9ffd1da199cec33f5642f08ce165cff938cc3101db6934bc8a3130c1ac78bb | 1.197669 | 0.159200 | 0.000010 | 0.000000 | 0.000000 |
| main/f4/vmess/G1/outer | vmess | G1 | 4 | RawPost-small | outputs/small-view-attribution-20261010/run-02/models/main/f4/vmess/G1/outer/RawPost-small.pt | 1444332d2ad53e55ef136e45605949099fcdecb0ccadbaa0990fbcb7a5eb7717 | 0.781046 | 0.138618 | 0.000009 | 0.000000 | 0.000000 |
| main/f4/vmess/G1/outer | vmess | G1 | 4 | Marginal-small | outputs/small-view-attribution-20261010/run-02/models/main/f4/vmess/G1/outer/Marginal-small.pt | e8e8f780e28bbcbe23af7bb9960ad982a1155c4b7cbd2b33da8cc4150af49c16 | 0.782437 | 0.174495 | 0.000010 | 0.000000 | 0.000000 |
| main/f4/vmess/G2/outer | vmess | G2 | 4 | RawPre-small | outputs/small-view-attribution-20261010/run-02/models/main/f4/vmess/G2/outer/RawPre-small.pt | 4cd000f67aacf5d046edf0418c5a55b020f96bf4ea82a3bd0bbf0500f1d25440 | 1.166124 | 0.194046 | 0.000009 | 0.000000 | 0.000000 |
| main/f4/vmess/G2/outer | vmess | G2 | 4 | RawPost-small | outputs/small-view-attribution-20261010/run-02/models/main/f4/vmess/G2/outer/RawPost-small.pt | 4e84ab23447c81e293277549563748b3aef95e383b7b6d4eebc5df6033bf7486 | 0.686919 | 0.174178 | 0.000010 | 0.000000 | 0.000000 |
| main/f4/vmess/G2/outer | vmess | G2 | 4 | Marginal-small | outputs/small-view-attribution-20261010/run-02/models/main/f4/vmess/G2/outer/Marginal-small.pt | 0ea159daed1f3344bc344f4e28503898993be33886027aea89a577f3be6da0f2 | 0.637144 | 0.212386 | 0.000010 | 0.000000 | 0.000000 |

## 原四项检验保留

```json
{
  "bootstrap_samples": 10000,
  "bootstrap_seed": 20261009,
  "comparisons": [
    {
      "CI_95": [
        0.008927741830241724,
        0.045683629080055146
      ],
      "CI_98_75": [
        0.005680955552747767,
        0.052704928240476186
      ],
      "candidate": "P-small",
      "delta_F1_uncovered": 0.024223160734752947,
      "positive_increment": true,
      "reference": "S"
    },
    {
      "CI_95": [
        -0.006762637075588593,
        0.010523408036560806
      ],
      "CI_98_75": [
        -0.009232797901167501,
        0.012691711090137859
      ],
      "candidate": "P-small",
      "delta_F1_uncovered": 0.002004843156121705,
      "positive_increment": false,
      "reference": "G-small"
    },
    {
      "CI_95": [
        -0.13147609471787194,
        -0.054661159819997904
      ],
      "CI_98_75": [
        -0.14088021244217405,
        -0.04203248894804346
      ],
      "candidate": "P-full",
      "delta_F1_uncovered": -0.09471624901990927,
      "positive_increment": false,
      "reference": "S"
    },
    {
      "CI_95": [
        -0.029715457607890433,
        0.007148176216400566
      ],
      "CI_98_75": [
        -0.03494094660905553,
        0.01185954949652142
      ],
      "candidate": "P-full",
      "delta_F1_uncovered": -0.010718733339383668,
      "positive_increment": false,
      "reference": "G-full"
    }
  ],
  "family": 4,
  "local_derivative_precision_validated": false,
  "model_conditional_not_external_validation": true,
  "selected_winner": null
}
```
