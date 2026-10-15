# StrongPost有限训练干预详细附录

## 逐业务分类

| arm | target | group | label | label_index | F1 | uncovered | support | TP | FP | FN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| G-full | shadowsocks | G0 | bing.com::search_results_view | 0 | 0.769231 | False | 20 | 15 | 4 | 5 |
| G-full | shadowsocks | G0 | developer.mozilla.org::document_view | 1 | 0.769231 | False | 20 | 15 | 4 | 5 |
| G-full | shadowsocks | G0 | github.com::repository_view | 2 | 0.810811 | True | 20 | 15 | 2 | 5 |
| G-full | shadowsocks | G0 | wikipedia.org::article_view | 3 | 0.772727 | False | 20 | 17 | 7 | 3 |
| G-full | shadowsocks | G0 | youtube.com::search_results_view | 4 | 0.800000 | True | 20 | 14 | 1 | 6 |
| G-full | shadowsocks | G0 | youtube.com::video_playback | 5 | 0.782609 | False | 20 | 18 | 8 | 2 |
| G-full | shadowsocks | G1 | bing.com::search_results_view | 0 | 0.666667 | True | 20 | 12 | 4 | 8 |
| G-full | shadowsocks | G1 | developer.mozilla.org::document_view | 1 | 0.603774 | False | 20 | 16 | 17 | 4 |
| G-full | shadowsocks | G1 | github.com::repository_view | 2 | 0.850000 | False | 20 | 17 | 3 | 3 |
| G-full | shadowsocks | G1 | wikipedia.org::article_view | 3 | 0.400000 | True | 20 | 5 | 0 | 15 |
| G-full | shadowsocks | G1 | youtube.com::search_results_view | 4 | 0.857143 | False | 20 | 18 | 4 | 2 |
| G-full | shadowsocks | G1 | youtube.com::video_playback | 5 | 0.863636 | False | 20 | 19 | 5 | 1 |
| G-full | shadowsocks | G2 | bing.com::search_results_view | 0 | 0.653061 | False | 20 | 16 | 13 | 4 |
| G-full | shadowsocks | G2 | developer.mozilla.org::document_view | 1 | 0.000000 | True | 20 | 0 | 1 | 20 |
| G-full | shadowsocks | G2 | github.com::repository_view | 2 | 0.878049 | False | 20 | 18 | 3 | 2 |
| G-full | shadowsocks | G2 | wikipedia.org::article_view | 3 | 0.692308 | False | 20 | 18 | 14 | 2 |
| G-full | shadowsocks | G2 | youtube.com::search_results_view | 4 | 0.790698 | False | 20 | 17 | 6 | 3 |
| G-full | shadowsocks | G2 | youtube.com::video_playback | 5 | 0.705882 | True | 20 | 12 | 2 | 8 |
| G-full | trojan | G0 | bing.com::search_results_view | 0 | 0.780488 | False | 20 | 16 | 5 | 4 |
| G-full | trojan | G0 | developer.mozilla.org::document_view | 1 | 0.666667 | False | 20 | 14 | 8 | 6 |
| G-full | trojan | G0 | github.com::repository_view | 2 | 0.894737 | True | 20 | 17 | 1 | 3 |
| G-full | trojan | G0 | wikipedia.org::article_view | 3 | 0.780488 | False | 20 | 16 | 5 | 4 |
| G-full | trojan | G0 | youtube.com::search_results_view | 4 | 0.789474 | True | 20 | 15 | 3 | 5 |
| G-full | trojan | G0 | youtube.com::video_playback | 5 | 0.850000 | False | 20 | 17 | 3 | 3 |
| G-full | trojan | G1 | bing.com::search_results_view | 0 | 0.777778 | True | 20 | 14 | 2 | 6 |
| G-full | trojan | G1 | developer.mozilla.org::document_view | 1 | 0.780488 | False | 20 | 16 | 5 | 4 |
| G-full | trojan | G1 | github.com::repository_view | 2 | 0.952381 | False | 20 | 20 | 2 | 0 |
| G-full | trojan | G1 | wikipedia.org::article_view | 3 | 0.800000 | True | 20 | 16 | 4 | 4 |
| G-full | trojan | G1 | youtube.com::search_results_view | 4 | 0.871795 | False | 20 | 17 | 2 | 3 |
| G-full | trojan | G1 | youtube.com::video_playback | 5 | 0.857143 | False | 20 | 18 | 4 | 2 |
| G-full | trojan | G2 | bing.com::search_results_view | 0 | 0.864865 | False | 20 | 16 | 1 | 4 |
| G-full | trojan | G2 | developer.mozilla.org::document_view | 1 | 0.702703 | True | 20 | 13 | 4 | 7 |
| G-full | trojan | G2 | github.com::repository_view | 2 | 0.930233 | False | 20 | 20 | 3 | 0 |
| G-full | trojan | G2 | wikipedia.org::article_view | 3 | 0.727273 | False | 20 | 16 | 8 | 4 |
| G-full | trojan | G2 | youtube.com::search_results_view | 4 | 0.857143 | False | 20 | 18 | 4 | 2 |
| G-full | trojan | G2 | youtube.com::video_playback | 5 | 0.810811 | True | 20 | 15 | 2 | 5 |
| G-full | vless | G0 | bing.com::search_results_view | 0 | 0.878049 | False | 20 | 18 | 3 | 2 |
| G-full | vless | G0 | developer.mozilla.org::document_view | 1 | 0.780488 | False | 20 | 16 | 5 | 4 |
| G-full | vless | G0 | github.com::repository_view | 2 | 0.833333 | True | 20 | 15 | 1 | 5 |
| G-full | vless | G0 | wikipedia.org::article_view | 3 | 0.714286 | False | 20 | 15 | 7 | 5 |
| G-full | vless | G0 | youtube.com::search_results_view | 4 | 0.871795 | True | 20 | 17 | 2 | 3 |
| G-full | vless | G0 | youtube.com::video_playback | 5 | 0.829268 | False | 20 | 17 | 4 | 3 |
| G-full | vless | G1 | bing.com::search_results_view | 0 | 0.871795 | True | 20 | 17 | 2 | 3 |
| G-full | vless | G1 | developer.mozilla.org::document_view | 1 | 0.829268 | False | 20 | 17 | 4 | 3 |
| G-full | vless | G1 | github.com::repository_view | 2 | 0.871795 | False | 20 | 17 | 2 | 3 |
| G-full | vless | G1 | wikipedia.org::article_view | 3 | 0.736842 | True | 20 | 14 | 4 | 6 |
| G-full | vless | G1 | youtube.com::search_results_view | 4 | 0.829268 | False | 20 | 17 | 4 | 3 |
| G-full | vless | G1 | youtube.com::video_playback | 5 | 0.904762 | False | 20 | 19 | 3 | 1 |
| G-full | vless | G2 | bing.com::search_results_view | 0 | 0.900000 | False | 20 | 18 | 2 | 2 |
| G-full | vless | G2 | developer.mozilla.org::document_view | 1 | 0.789474 | True | 20 | 15 | 3 | 5 |
| G-full | vless | G2 | github.com::repository_view | 2 | 0.894737 | False | 20 | 17 | 1 | 3 |
| G-full | vless | G2 | wikipedia.org::article_view | 3 | 0.681818 | False | 20 | 15 | 9 | 5 |
| G-full | vless | G2 | youtube.com::search_results_view | 4 | 0.820513 | False | 20 | 16 | 3 | 4 |
| G-full | vless | G2 | youtube.com::video_playback | 5 | 0.878049 | True | 20 | 18 | 3 | 2 |
| G-full | vmess | G0 | bing.com::search_results_view | 0 | 0.789474 | False | 20 | 15 | 3 | 5 |
| G-full | vmess | G0 | developer.mozilla.org::document_view | 1 | 0.571429 | False | 20 | 12 | 10 | 8 |
| G-full | vmess | G0 | github.com::repository_view | 2 | 0.727273 | True | 20 | 12 | 1 | 8 |
| G-full | vmess | G0 | wikipedia.org::article_view | 3 | 0.652174 | False | 20 | 15 | 11 | 5 |
| G-full | vmess | G0 | youtube.com::search_results_view | 4 | 0.871795 | True | 20 | 17 | 2 | 3 |
| G-full | vmess | G0 | youtube.com::video_playback | 5 | 0.904762 | False | 20 | 19 | 3 | 1 |
| G-full | vmess | G1 | bing.com::search_results_view | 0 | 0.620690 | True | 20 | 9 | 0 | 11 |
| G-full | vmess | G1 | developer.mozilla.org::document_view | 1 | 0.631579 | False | 20 | 18 | 19 | 2 |
| G-full | vmess | G1 | github.com::repository_view | 2 | 0.926829 | False | 20 | 19 | 2 | 1 |
| G-full | vmess | G1 | wikipedia.org::article_view | 3 | 0.173913 | True | 20 | 2 | 1 | 18 |
| G-full | vmess | G1 | youtube.com::search_results_view | 4 | 0.826087 | False | 20 | 19 | 7 | 1 |
| G-full | vmess | G1 | youtube.com::video_playback | 5 | 0.863636 | False | 20 | 19 | 5 | 1 |
| G-full | vmess | G2 | bing.com::search_results_view | 0 | 0.818182 | False | 20 | 18 | 6 | 2 |
| G-full | vmess | G2 | developer.mozilla.org::document_view | 1 | 0.095238 | True | 20 | 1 | 0 | 19 |
| G-full | vmess | G2 | github.com::repository_view | 2 | 0.926829 | False | 20 | 19 | 2 | 1 |
| G-full | vmess | G2 | wikipedia.org::article_view | 3 | 0.653846 | False | 20 | 17 | 15 | 3 |
| G-full | vmess | G2 | youtube.com::search_results_view | 4 | 0.857143 | False | 20 | 18 | 4 | 2 |
| G-full | vmess | G2 | youtube.com::video_playback | 5 | 0.900000 | True | 20 | 18 | 2 | 2 |
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
| P-full | shadowsocks | G0 | bing.com::search_results_view | 0 | 0.789474 | False | 20 | 15 | 3 | 5 |
| P-full | shadowsocks | G0 | developer.mozilla.org::document_view | 1 | 0.769231 | False | 20 | 15 | 4 | 5 |
| P-full | shadowsocks | G0 | github.com::repository_view | 2 | 0.871795 | True | 20 | 17 | 2 | 3 |
| P-full | shadowsocks | G0 | wikipedia.org::article_view | 3 | 0.772727 | False | 20 | 17 | 7 | 3 |
| P-full | shadowsocks | G0 | youtube.com::search_results_view | 4 | 0.787879 | True | 20 | 13 | 0 | 7 |
| P-full | shadowsocks | G0 | youtube.com::video_playback | 5 | 0.765957 | False | 20 | 18 | 9 | 2 |
| P-full | shadowsocks | G1 | bing.com::search_results_view | 0 | 0.647059 | True | 20 | 11 | 3 | 9 |
| P-full | shadowsocks | G1 | developer.mozilla.org::document_view | 1 | 0.581818 | False | 20 | 16 | 19 | 4 |
| P-full | shadowsocks | G1 | github.com::repository_view | 2 | 0.878049 | False | 20 | 18 | 3 | 2 |
| P-full | shadowsocks | G1 | wikipedia.org::article_view | 3 | 0.333333 | True | 20 | 4 | 0 | 16 |
| P-full | shadowsocks | G1 | youtube.com::search_results_view | 4 | 0.883721 | False | 20 | 19 | 4 | 1 |
| P-full | shadowsocks | G1 | youtube.com::video_playback | 5 | 0.883721 | False | 20 | 19 | 4 | 1 |
| P-full | shadowsocks | G2 | bing.com::search_results_view | 0 | 0.680000 | False | 20 | 17 | 13 | 3 |
| P-full | shadowsocks | G2 | developer.mozilla.org::document_view | 1 | 0.000000 | True | 20 | 0 | 0 | 20 |
| P-full | shadowsocks | G2 | github.com::repository_view | 2 | 0.883721 | False | 20 | 19 | 4 | 1 |
| P-full | shadowsocks | G2 | wikipedia.org::article_view | 3 | 0.666667 | False | 20 | 17 | 14 | 3 |
| P-full | shadowsocks | G2 | youtube.com::search_results_view | 4 | 0.755556 | False | 20 | 17 | 8 | 3 |
| P-full | shadowsocks | G2 | youtube.com::video_playback | 5 | 0.645161 | True | 20 | 10 | 1 | 10 |
| P-full | trojan | G0 | bing.com::search_results_view | 0 | 0.800000 | False | 20 | 16 | 4 | 4 |
| P-full | trojan | G0 | developer.mozilla.org::document_view | 1 | 0.714286 | False | 20 | 15 | 7 | 5 |
| P-full | trojan | G0 | github.com::repository_view | 2 | 0.894737 | True | 20 | 17 | 1 | 3 |
| P-full | trojan | G0 | wikipedia.org::article_view | 3 | 0.800000 | False | 20 | 16 | 4 | 4 |
| P-full | trojan | G0 | youtube.com::search_results_view | 4 | 0.800000 | True | 20 | 16 | 4 | 4 |
| P-full | trojan | G0 | youtube.com::video_playback | 5 | 0.850000 | False | 20 | 17 | 3 | 3 |
| P-full | trojan | G1 | bing.com::search_results_view | 0 | 0.777778 | True | 20 | 14 | 2 | 6 |
| P-full | trojan | G1 | developer.mozilla.org::document_view | 1 | 0.755556 | False | 20 | 17 | 8 | 3 |
| P-full | trojan | G1 | github.com::repository_view | 2 | 0.975610 | False | 20 | 20 | 1 | 0 |
| P-full | trojan | G1 | wikipedia.org::article_view | 3 | 0.736842 | True | 20 | 14 | 4 | 6 |
| P-full | trojan | G1 | youtube.com::search_results_view | 4 | 0.850000 | False | 20 | 17 | 3 | 3 |
| P-full | trojan | G1 | youtube.com::video_playback | 5 | 0.850000 | False | 20 | 17 | 3 | 3 |
| P-full | trojan | G2 | bing.com::search_results_view | 0 | 0.800000 | False | 20 | 16 | 4 | 4 |
| P-full | trojan | G2 | developer.mozilla.org::document_view | 1 | 0.588235 | True | 20 | 10 | 4 | 10 |
| P-full | trojan | G2 | github.com::repository_view | 2 | 0.952381 | False | 20 | 20 | 2 | 0 |
| P-full | trojan | G2 | wikipedia.org::article_view | 3 | 0.711111 | False | 20 | 16 | 9 | 4 |
| P-full | trojan | G2 | youtube.com::search_results_view | 4 | 0.883721 | False | 20 | 19 | 4 | 1 |
| P-full | trojan | G2 | youtube.com::video_playback | 5 | 0.833333 | True | 20 | 15 | 1 | 5 |
| P-full | vless | G0 | bing.com::search_results_view | 0 | 0.923077 | False | 20 | 18 | 1 | 2 |
| P-full | vless | G0 | developer.mozilla.org::document_view | 1 | 0.850000 | False | 20 | 17 | 3 | 3 |
| P-full | vless | G0 | github.com::repository_view | 2 | 0.833333 | True | 20 | 15 | 1 | 5 |
| P-full | vless | G0 | wikipedia.org::article_view | 3 | 0.714286 | False | 20 | 15 | 7 | 5 |
| P-full | vless | G0 | youtube.com::search_results_view | 4 | 0.857143 | True | 20 | 18 | 4 | 2 |
| P-full | vless | G0 | youtube.com::video_playback | 5 | 0.829268 | False | 20 | 17 | 4 | 3 |
| P-full | vless | G1 | bing.com::search_results_view | 0 | 0.829268 | True | 20 | 17 | 4 | 3 |
| P-full | vless | G1 | developer.mozilla.org::document_view | 1 | 0.772727 | False | 20 | 17 | 7 | 3 |
| P-full | vless | G1 | github.com::repository_view | 2 | 0.923077 | False | 20 | 18 | 1 | 2 |
| P-full | vless | G1 | wikipedia.org::article_view | 3 | 0.562500 | True | 20 | 9 | 3 | 11 |
| P-full | vless | G1 | youtube.com::search_results_view | 4 | 0.837209 | False | 20 | 18 | 5 | 2 |
| P-full | vless | G1 | youtube.com::video_playback | 5 | 0.926829 | False | 20 | 19 | 2 | 1 |
| P-full | vless | G2 | bing.com::search_results_view | 0 | 0.871795 | False | 20 | 17 | 2 | 3 |
| P-full | vless | G2 | developer.mozilla.org::document_view | 1 | 0.769231 | True | 20 | 15 | 4 | 5 |
| P-full | vless | G2 | github.com::repository_view | 2 | 0.894737 | False | 20 | 17 | 1 | 3 |
| P-full | vless | G2 | wikipedia.org::article_view | 3 | 0.666667 | False | 20 | 14 | 8 | 6 |
| P-full | vless | G2 | youtube.com::search_results_view | 4 | 0.809524 | False | 20 | 17 | 5 | 3 |
| P-full | vless | G2 | youtube.com::video_playback | 5 | 0.900000 | True | 20 | 18 | 2 | 2 |
| P-full | vmess | G0 | bing.com::search_results_view | 0 | 0.769231 | False | 20 | 15 | 4 | 5 |
| P-full | vmess | G0 | developer.mozilla.org::document_view | 1 | 0.585366 | False | 20 | 12 | 9 | 8 |
| P-full | vmess | G0 | github.com::repository_view | 2 | 0.764706 | True | 20 | 13 | 1 | 7 |
| P-full | vmess | G0 | wikipedia.org::article_view | 3 | 0.680851 | False | 20 | 16 | 11 | 4 |
| P-full | vmess | G0 | youtube.com::search_results_view | 4 | 0.871795 | True | 20 | 17 | 2 | 3 |
| P-full | vmess | G0 | youtube.com::video_playback | 5 | 0.950000 | False | 20 | 19 | 1 | 1 |
| P-full | vmess | G1 | bing.com::search_results_view | 0 | 0.620690 | True | 20 | 9 | 0 | 11 |
| P-full | vmess | G1 | developer.mozilla.org::document_view | 1 | 0.654545 | False | 20 | 18 | 17 | 2 |
| P-full | vmess | G1 | github.com::repository_view | 2 | 0.926829 | False | 20 | 19 | 2 | 1 |
| P-full | vmess | G1 | wikipedia.org::article_view | 3 | 0.250000 | True | 20 | 3 | 1 | 17 |
| P-full | vmess | G1 | youtube.com::search_results_view | 4 | 0.826087 | False | 20 | 19 | 7 | 1 |
| P-full | vmess | G1 | youtube.com::video_playback | 5 | 0.844444 | False | 20 | 19 | 6 | 1 |
| P-full | vmess | G2 | bing.com::search_results_view | 0 | 0.809524 | False | 20 | 17 | 5 | 3 |
| P-full | vmess | G2 | developer.mozilla.org::document_view | 1 | 0.173913 | True | 20 | 2 | 1 | 18 |
| P-full | vmess | G2 | github.com::repository_view | 2 | 0.926829 | False | 20 | 19 | 2 | 1 |
| P-full | vmess | G2 | wikipedia.org::article_view | 3 | 0.692308 | False | 20 | 18 | 14 | 2 |
| P-full | vmess | G2 | youtube.com::search_results_view | 4 | 0.837209 | False | 20 | 18 | 5 | 2 |
| P-full | vmess | G2 | youtube.com::video_playback | 5 | 0.923077 | True | 20 | 18 | 1 | 2 |
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

## 逐部署校准与未覆盖CE变化

| target | arm | scope | actual_delta_CE |
| --- | --- | --- | --- |
| shadowsocks | G-full | C | -0.035050 |
| shadowsocks | G-full | U | 0.643102 |
| shadowsocks | G-full | all | 0.191001 |
| shadowsocks | G-small | C | 0.010597 |
| shadowsocks | G-small | U | -0.136830 |
| shadowsocks | G-small | all | -0.038545 |
| shadowsocks | P-full | C | -0.086230 |
| shadowsocks | P-full | U | 0.583161 |
| shadowsocks | P-full | all | 0.136900 |
| shadowsocks | P-small | C | 0.001265 |
| shadowsocks | P-small | U | -0.258560 |
| shadowsocks | P-small | all | -0.085344 |
| trojan | G-full | C | 0.083612 |
| trojan | G-full | U | 0.104723 |
| trojan | G-full | all | 0.090649 |
| trojan | G-small | C | 0.012179 |
| trojan | G-small | U | -0.026993 |
| trojan | G-small | all | -0.000878 |
| trojan | P-full | C | 0.033249 |
| trojan | P-full | U | 0.137399 |
| trojan | P-full | all | 0.067966 |
| trojan | P-small | C | 0.009622 |
| trojan | P-small | U | -0.025421 |
| trojan | P-small | all | -0.002059 |
| vless | G-full | C | 0.027635 |
| vless | G-full | U | 0.018071 |
| vless | G-full | all | 0.024447 |
| vless | G-small | C | -0.001769 |
| vless | G-small | U | -0.058250 |
| vless | G-small | all | -0.020596 |
| vless | P-full | C | -0.032131 |
| vless | P-full | U | 0.079461 |
| vless | P-full | all | 0.005067 |
| vless | P-small | C | -0.011578 |
| vless | P-small | U | -0.025820 |
| vless | P-small | all | -0.016326 |
| vmess | G-full | C | -0.098746 |
| vmess | G-full | U | 0.684946 |
| vmess | G-full | all | 0.162485 |
| vmess | G-small | C | 0.009198 |
| vmess | G-small | U | -0.075604 |
| vmess | G-small | all | -0.019070 |
| vmess | P-full | C | -0.159459 |
| vmess | P-full | U | 0.800955 |
| vmess | P-full | all | 0.160679 |
| vmess | P-small | C | -0.027716 |
| vmess | P-small | U | -0.046802 |
| vmess | P-small | all | -0.034078 |

## 逐折角色指标

| arm | target | group | outer | F1_all | accuracy | CE_nats | Brier | CE_bits | F1_uncovered | F1_aux |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| G-full | shadowsocks | G0 | 0 | 0.836640 | 0.833333 | 0.546829 | 0.247493 | 0.788908 | 0.928571 | 0.790675 |
| G-full | shadowsocks | G0 | 1 | 0.758778 | 0.750000 | 0.986375 | 0.385417 | 1.423039 | 0.857143 | 0.709596 |
| G-full | shadowsocks | G0 | 2 | 0.645238 | 0.666667 | 0.996168 | 0.418755 | 1.437166 | 0.541667 | 0.697024 |
| G-full | shadowsocks | G0 | 3 | 0.836640 | 0.833333 | 0.811279 | 0.295475 | 1.170428 | 0.873016 | 0.818452 |
| G-full | shadowsocks | G0 | 4 | 0.826455 | 0.833333 | 0.599029 | 0.313482 | 0.864216 | 0.761905 | 0.858730 |
| G-full | shadowsocks | G1 | 0 | 0.681265 | 0.708333 | 1.958471 | 0.381796 | 2.825476 | 0.485714 | 0.779040 |
| G-full | shadowsocks | G1 | 1 | 0.745503 | 0.750000 | 0.686979 | 0.352736 | 0.991102 | 0.633333 | 0.801587 |
| G-full | shadowsocks | G1 | 2 | 0.665344 | 0.708333 | 1.149678 | 0.517875 | 1.658634 | 0.428571 | 0.783730 |
| G-full | shadowsocks | G1 | 3 | 0.630724 | 0.666667 | 1.154723 | 0.427816 | 1.665913 | 0.400000 | 0.746086 |
| G-full | shadowsocks | G1 | 4 | 0.778307 | 0.791667 | 0.723698 | 0.342674 | 1.044075 | 0.628571 | 0.853175 |
| G-full | shadowsocks | G2 | 0 | 0.593025 | 0.625000 | 1.502934 | 0.520770 | 2.168276 | 0.333333 | 0.722872 |
| G-full | shadowsocks | G2 | 1 | 0.700433 | 0.750000 | 1.131967 | 0.421100 | 1.633083 | 0.500000 | 0.800649 |
| G-full | shadowsocks | G2 | 2 | 0.680471 | 0.750000 | 1.203750 | 0.388306 | 1.736644 | 0.333333 | 0.854040 |
| G-full | shadowsocks | G2 | 3 | 0.575168 | 0.625000 | 1.539070 | 0.586222 | 2.220408 | 0.333333 | 0.696086 |
| G-full | shadowsocks | G2 | 4 | 0.565657 | 0.625000 | 0.985038 | 0.530251 | 1.421110 | 0.250000 | 0.723485 |
| G-full | trojan | G0 | 0 | 0.839683 | 0.833333 | 0.476998 | 0.252271 | 0.688163 | 0.928571 | 0.795238 |
| G-full | trojan | G0 | 1 | 0.789683 | 0.791667 | 0.542203 | 0.266686 | 0.782233 | 0.875000 | 0.747024 |
| G-full | trojan | G0 | 2 | 0.755556 | 0.791667 | 0.408033 | 0.246103 | 0.588668 | 0.644444 | 0.811111 |
| G-full | trojan | G0 | 3 | 0.707540 | 0.708333 | 0.822584 | 0.402103 | 1.186738 | 0.733333 | 0.694643 |
| G-full | trojan | G0 | 4 | 0.836640 | 0.833333 | 0.409998 | 0.257113 | 0.591502 | 0.928571 | 0.790675 |
| G-full | trojan | G1 | 0 | 0.916667 | 0.916667 | 0.228593 | 0.128414 | 0.329790 | 0.875000 | 0.937500 |
| G-full | trojan | G1 | 1 | 0.828704 | 0.833333 | 0.712818 | 0.282172 | 1.028379 | 0.666667 | 0.909722 |
| G-full | trojan | G1 | 2 | 0.823413 | 0.833333 | 0.499457 | 0.267382 | 0.720564 | 0.888889 | 0.790675 |
| G-full | trojan | G1 | 3 | 0.828042 | 0.833333 | 0.500004 | 0.281760 | 0.721353 | 0.761905 | 0.861111 |
| G-full | trojan | G1 | 4 | 0.786376 | 0.791667 | 0.395655 | 0.249245 | 0.570809 | 0.708333 | 0.825397 |
| G-full | trojan | G2 | 0 | 0.868386 | 0.875000 | 0.391264 | 0.195623 | 0.564474 | 0.785714 | 0.909722 |
| G-full | trojan | G2 | 1 | 0.787037 | 0.791667 | 0.534691 | 0.243108 | 0.771397 | 0.777778 | 0.791667 |
| G-full | trojan | G2 | 2 | 0.783249 | 0.791667 | 0.457786 | 0.246513 | 0.660445 | 0.666667 | 0.841540 |
| G-full | trojan | G2 | 3 | 0.788360 | 0.791667 | 0.595565 | 0.329808 | 0.859218 | 0.714286 | 0.825397 |
| G-full | trojan | G2 | 4 | 0.832011 | 0.833333 | 0.338777 | 0.196440 | 0.488752 | 0.803571 | 0.846230 |
| G-full | vless | G0 | 0 | 0.876720 | 0.875000 | 0.689495 | 0.326502 | 0.994731 | 0.928571 | 0.850794 |
| G-full | vless | G0 | 1 | 0.765079 | 0.791667 | 0.792287 | 0.260860 | 1.143029 | 0.873016 | 0.711111 |
| G-full | vless | G0 | 2 | 0.752116 | 0.750000 | 0.746239 | 0.380756 | 1.076595 | 0.761905 | 0.747222 |
| G-full | vless | G0 | 3 | 0.836640 | 0.833333 | 0.270979 | 0.146462 | 0.390940 | 0.928571 | 0.790675 |
| G-full | vless | G0 | 4 | 0.826058 | 0.833333 | 0.631884 | 0.251718 | 0.911616 | 0.730159 | 0.874008 |
| G-full | vless | G1 | 0 | 0.751984 | 0.750000 | 0.620691 | 0.339076 | 0.895468 | 0.666667 | 0.794643 |
| G-full | vless | G1 | 1 | 0.865079 | 0.875000 | 0.565784 | 0.234872 | 0.816254 | 0.833333 | 0.880952 |
| G-full | vless | G1 | 2 | 0.749339 | 0.750000 | 1.568111 | 0.459752 | 2.262306 | 0.761905 | 0.743056 |
| G-full | vless | G1 | 3 | 0.957672 | 0.958333 | 0.385184 | 0.119731 | 0.555704 | 0.928571 | 0.972222 |
| G-full | vless | G1 | 4 | 0.877381 | 0.875000 | 0.583784 | 0.222133 | 0.842223 | 0.857143 | 0.887500 |
| G-full | vless | G2 | 0 | 0.831746 | 0.833333 | 0.628720 | 0.287422 | 0.907051 | 0.833333 | 0.830952 |
| G-full | vless | G2 | 1 | 0.874339 | 0.875000 | 0.509295 | 0.211589 | 0.734757 | 0.944444 | 0.839286 |
| G-full | vless | G2 | 2 | 0.721825 | 0.708333 | 1.024201 | 0.486341 | 1.477610 | 0.675000 | 0.745238 |
| G-full | vless | G2 | 3 | 0.916005 | 0.916667 | 0.350398 | 0.178169 | 0.505518 | 0.873016 | 0.937500 |
| G-full | vless | G2 | 4 | 0.798016 | 0.791667 | 0.636642 | 0.267214 | 0.918480 | 0.857143 | 0.768452 |
| G-full | vmess | G0 | 0 | 0.832011 | 0.833333 | 0.531788 | 0.239199 | 0.767208 | 0.857143 | 0.819444 |
| G-full | vmess | G0 | 1 | 0.733862 | 0.750000 | 0.784621 | 0.385400 | 1.131969 | 0.857143 | 0.672222 |
| G-full | vmess | G0 | 2 | 0.674603 | 0.666667 | 1.036106 | 0.454237 | 1.494785 | 0.803571 | 0.610119 |
| G-full | vmess | G0 | 3 | 0.730736 | 0.750000 | 0.818823 | 0.306327 | 1.181312 | 0.833333 | 0.679437 |
| G-full | vmess | G0 | 4 | 0.731746 | 0.750000 | 0.741332 | 0.312351 | 1.069516 | 0.600000 | 0.797619 |
| G-full | vmess | G1 | 0 | 0.868783 | 0.875000 | 0.805754 | 0.244477 | 1.162457 | 0.761905 | 0.922222 |
| G-full | vmess | G1 | 1 | 0.444444 | 0.541667 | 1.782313 | 0.613709 | 2.571335 | 0.000000 | 0.666667 |
| G-full | vmess | G1 | 2 | 0.685185 | 0.750000 | 0.685841 | 0.388284 | 0.989459 | 0.333333 | 0.861111 |
| G-full | vmess | G1 | 3 | 0.703755 | 0.750000 | 1.159827 | 0.434157 | 1.673277 | 0.428571 | 0.841346 |
| G-full | vmess | G1 | 4 | 0.589995 | 0.666667 | 1.151565 | 0.419517 | 1.661357 | 0.200000 | 0.784993 |
| G-full | vmess | G2 | 0 | 0.650265 | 0.708333 | 0.543904 | 0.311576 | 0.784688 | 0.428571 | 0.761111 |
| G-full | vmess | G2 | 1 | 0.683598 | 0.750000 | 1.332017 | 0.453716 | 1.921694 | 0.444444 | 0.803175 |
| G-full | vmess | G2 | 2 | 0.781914 | 0.791667 | 0.702765 | 0.300774 | 1.013876 | 0.644444 | 0.850649 |
| G-full | vmess | G2 | 3 | 0.730736 | 0.791667 | 1.067261 | 0.351972 | 1.539732 | 0.428571 | 0.881818 |
| G-full | vmess | G2 | 4 | 0.689069 | 0.750000 | 1.097355 | 0.420012 | 1.583148 | 0.500000 | 0.783604 |
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
| P-full | shadowsocks | G0 | 0 | 0.836640 | 0.833333 | 0.536516 | 0.246586 | 0.774029 | 0.928571 | 0.790675 |
| P-full | shadowsocks | G0 | 1 | 0.716931 | 0.708333 | 0.913712 | 0.382480 | 1.318208 | 0.761905 | 0.694444 |
| P-full | shadowsocks | G0 | 2 | 0.750397 | 0.750000 | 0.761874 | 0.379628 | 1.099152 | 0.803571 | 0.723810 |
| P-full | shadowsocks | G0 | 3 | 0.874339 | 0.875000 | 0.649967 | 0.237478 | 0.937704 | 0.944444 | 0.839286 |
| P-full | shadowsocks | G0 | 4 | 0.767196 | 0.791667 | 0.597057 | 0.300676 | 0.861371 | 0.628571 | 0.836508 |
| P-full | shadowsocks | G1 | 0 | 0.770370 | 0.791667 | 1.652736 | 0.359316 | 2.384395 | 0.533333 | 0.888889 |
| P-full | shadowsocks | G1 | 1 | 0.653968 | 0.666667 | 0.795578 | 0.417586 | 1.147777 | 0.422222 | 0.769841 |
| P-full | shadowsocks | G1 | 2 | 0.665344 | 0.708333 | 1.151602 | 0.518093 | 1.661410 | 0.428571 | 0.783730 |
| P-full | shadowsocks | G1 | 3 | 0.625000 | 0.666667 | 1.159205 | 0.478055 | 1.672380 | 0.400000 | 0.737500 |
| P-full | shadowsocks | G1 | 4 | 0.778307 | 0.791667 | 0.721385 | 0.338633 | 1.040739 | 0.628571 | 0.853175 |
| P-full | shadowsocks | G2 | 0 | 0.515909 | 0.583333 | 1.510213 | 0.573226 | 2.178777 | 0.200000 | 0.673864 |
| P-full | shadowsocks | G2 | 1 | 0.659692 | 0.708333 | 1.136304 | 0.447000 | 1.639341 | 0.500000 | 0.739538 |
| P-full | shadowsocks | G2 | 2 | 0.680471 | 0.750000 | 1.189937 | 0.383694 | 1.716716 | 0.333333 | 0.854040 |
| P-full | shadowsocks | G2 | 3 | 0.614238 | 0.666667 | 1.440411 | 0.551692 | 2.078073 | 0.333333 | 0.754690 |
| P-full | shadowsocks | G2 | 4 | 0.549916 | 0.625000 | 0.947989 | 0.517649 | 1.367659 | 0.166667 | 0.741540 |
| P-full | trojan | G0 | 0 | 0.835053 | 0.833333 | 0.416107 | 0.216161 | 0.600316 | 0.873016 | 0.816071 |
| P-full | trojan | G0 | 1 | 0.789683 | 0.791667 | 0.440600 | 0.233645 | 0.635652 | 0.875000 | 0.747024 |
| P-full | trojan | G0 | 2 | 0.814815 | 0.833333 | 0.353456 | 0.201015 | 0.509929 | 0.777778 | 0.833333 |
| P-full | trojan | G0 | 3 | 0.746609 | 0.750000 | 0.780431 | 0.420984 | 1.125924 | 0.733333 | 0.753247 |
| P-full | trojan | G0 | 4 | 0.836640 | 0.833333 | 0.438783 | 0.254374 | 0.633030 | 0.928571 | 0.790675 |
| P-full | trojan | G1 | 0 | 0.878968 | 0.875000 | 0.294102 | 0.179835 | 0.424300 | 0.803571 | 0.916667 |
| P-full | trojan | G1 | 1 | 0.740212 | 0.750000 | 0.582165 | 0.305334 | 0.839887 | 0.476190 | 0.872222 |
| P-full | trojan | G1 | 2 | 0.826058 | 0.833333 | 0.525146 | 0.259510 | 0.757626 | 0.888889 | 0.794643 |
| P-full | trojan | G1 | 3 | 0.825397 | 0.833333 | 0.476229 | 0.273860 | 0.687053 | 0.857143 | 0.809524 |
| P-full | trojan | G1 | 4 | 0.827116 | 0.833333 | 0.418144 | 0.265124 | 0.603254 | 0.708333 | 0.886508 |
| P-full | trojan | G2 | 0 | 0.829762 | 0.833333 | 0.434973 | 0.235632 | 0.627533 | 0.714286 | 0.887500 |
| P-full | trojan | G2 | 1 | 0.874339 | 0.875000 | 0.343533 | 0.210577 | 0.495613 | 0.875000 | 0.874008 |
| P-full | trojan | G2 | 2 | 0.724916 | 0.750000 | 0.509600 | 0.218839 | 0.735198 | 0.533333 | 0.820707 |
| P-full | trojan | G2 | 3 | 0.738757 | 0.750000 | 0.632994 | 0.309551 | 0.913218 | 0.619048 | 0.798611 |
| P-full | trojan | G2 | 4 | 0.787037 | 0.791667 | 0.327913 | 0.189467 | 0.473079 | 0.750000 | 0.805556 |
| P-full | vless | G0 | 0 | 0.836640 | 0.833333 | 0.646890 | 0.331076 | 0.933265 | 0.875000 | 0.817460 |
| P-full | vless | G0 | 1 | 0.865079 | 0.875000 | 0.812614 | 0.187842 | 1.172354 | 0.873016 | 0.861111 |
| P-full | vless | G0 | 2 | 0.760714 | 0.750000 | 0.711616 | 0.382622 | 1.026644 | 0.803571 | 0.739286 |
| P-full | vless | G0 | 3 | 0.874339 | 0.875000 | 0.264483 | 0.126538 | 0.381568 | 0.928571 | 0.847222 |
| P-full | vless | G0 | 4 | 0.826058 | 0.833333 | 0.808665 | 0.284483 | 1.166656 | 0.730159 | 0.874008 |
| P-full | vless | G1 | 0 | 0.744444 | 0.750000 | 0.607950 | 0.301299 | 0.877086 | 0.619048 | 0.807143 |
| P-full | vless | G1 | 1 | 0.805820 | 0.833333 | 0.691038 | 0.292191 | 0.996957 | 0.700000 | 0.858730 |
| P-full | vless | G1 | 2 | 0.756085 | 0.750000 | 1.066757 | 0.448013 | 1.539006 | 0.761905 | 0.753175 |
| P-full | vless | G1 | 3 | 0.911111 | 0.916667 | 0.433065 | 0.127397 | 0.624781 | 0.733333 | 1.000000 |
| P-full | vless | G1 | 4 | 0.805820 | 0.833333 | 0.576594 | 0.226141 | 0.831850 | 0.628571 | 0.894444 |
| P-full | vless | G2 | 0 | 0.831746 | 0.833333 | 0.532580 | 0.252379 | 0.768350 | 0.833333 | 0.830952 |
| P-full | vless | G2 | 1 | 0.873016 | 0.875000 | 0.558185 | 0.200473 | 0.805291 | 0.888889 | 0.865079 |
| P-full | vless | G2 | 2 | 0.721825 | 0.708333 | 1.047323 | 0.531147 | 1.510968 | 0.675000 | 0.745238 |
| P-full | vless | G2 | 3 | 0.871429 | 0.875000 | 0.327349 | 0.169239 | 0.472265 | 0.928571 | 0.842857 |
| P-full | vless | G2 | 4 | 0.798016 | 0.791667 | 0.627882 | 0.289575 | 0.905842 | 0.857143 | 0.768452 |
| P-full | vmess | G0 | 0 | 0.835714 | 0.833333 | 0.520558 | 0.237450 | 0.751007 | 0.857143 | 0.825000 |
| P-full | vmess | G0 | 1 | 0.733862 | 0.750000 | 0.781818 | 0.388916 | 1.127926 | 0.857143 | 0.672222 |
| P-full | vmess | G0 | 2 | 0.707143 | 0.708333 | 0.833985 | 0.433526 | 1.203187 | 0.803571 | 0.658929 |
| P-full | vmess | G0 | 3 | 0.773593 | 0.791667 | 0.829967 | 0.323614 | 1.197390 | 0.928571 | 0.696104 |
| P-full | vmess | G0 | 4 | 0.731746 | 0.750000 | 0.741200 | 0.312084 | 1.069326 | 0.600000 | 0.797619 |
| P-full | vmess | G1 | 0 | 0.868783 | 0.875000 | 0.830192 | 0.267998 | 1.197714 | 0.761905 | 0.922222 |
| P-full | vmess | G1 | 1 | 0.446212 | 0.541667 | 1.696028 | 0.676361 | 2.446851 | 0.000000 | 0.669318 |
| P-full | vmess | G1 | 2 | 0.685185 | 0.750000 | 0.751374 | 0.419133 | 1.084003 | 0.333333 | 0.861111 |
| P-full | vmess | G1 | 3 | 0.703755 | 0.750000 | 1.161815 | 0.434630 | 1.676145 | 0.428571 | 0.841346 |
| P-full | vmess | G1 | 4 | 0.668783 | 0.708333 | 1.337297 | 0.477972 | 1.929312 | 0.400000 | 0.803175 |
| P-full | vmess | G2 | 0 | 0.776190 | 0.791667 | 0.531293 | 0.302039 | 0.766494 | 0.628571 | 0.850000 |
| P-full | vmess | G2 | 1 | 0.615741 | 0.666667 | 1.447706 | 0.476181 | 2.088599 | 0.444444 | 0.701389 |
| P-full | vmess | G2 | 2 | 0.812217 | 0.833333 | 0.703396 | 0.283930 | 1.014786 | 0.700000 | 0.868326 |
| P-full | vmess | G2 | 3 | 0.730736 | 0.791667 | 1.076362 | 0.366985 | 1.552863 | 0.428571 | 0.881818 |
| P-full | vmess | G2 | 4 | 0.689069 | 0.750000 | 0.971191 | 0.379704 | 1.401133 | 0.500000 | 0.783604 |
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

## 冻结选择与模型复用

| role_id | arm | beta | eta | t | reused | gradient_inf |
| --- | --- | --- | --- | --- | --- | --- |
| main/f0/shadowsocks/G0/outer | P-small | 0.100000 | 100.000000 | 4.000000 | False | 0.000009 |
| main/f0/shadowsocks/G0/outer | G-small | 0.100000 | 100.000000 | 4.000000 | False | 0.000007 |
| main/f0/shadowsocks/G0/outer | P-full | 1.000000 | 100.000000 | 4.000000 | False | 0.000010 |
| main/f0/shadowsocks/G0/outer | G-full | 1.000000 | 100.000000 | 4.000000 | False | 0.000009 |
| main/f0/shadowsocks/G1/outer | P-small | 0.100000 | 0.100000 | 0.250000 | False | 0.000009 |
| main/f0/shadowsocks/G1/outer | G-small | 0.100000 | 0.100000 | 0.250000 | False | 0.000010 |
| main/f0/shadowsocks/G1/outer | P-full | 1.000000 | 0.100000 | 0.250000 | False | 0.000009 |
| main/f0/shadowsocks/G1/outer | G-full | 1.000000 | 0.100000 | 0.250000 | False | 0.000009 |
| main/f0/shadowsocks/G2/outer | P-small | 0.100000 | 1.000000 | 0.000000 | False | 0.000008 |
| main/f0/shadowsocks/G2/outer | G-small | 0.100000 | 1.000000 | 0.000000 | False | 0.000008 |
| main/f0/shadowsocks/G2/outer | P-full | 1.000000 | 1.000000 | 0.000000 | False | 0.000010 |
| main/f0/shadowsocks/G2/outer | G-full | 1.000000 | 1.000000 | 0.000000 | True | 0.000009 |
| main/f0/vless/G0/outer | P-small | 0.100000 | 0.100000 | 4.000000 | False | 0.000009 |
| main/f0/vless/G0/outer | G-small | 0.100000 | 0.100000 | 4.000000 | False | 0.000007 |
| main/f0/vless/G0/outer | P-full | 1.000000 | 0.100000 | 4.000000 | True | 0.000006 |
| main/f0/vless/G0/outer | G-full | 1.000000 | 0.100000 | 4.000000 | True | 0.000007 |
| main/f0/vless/G1/outer | P-small | 0.100000 | 0.100000 | 4.000000 | False | 0.000008 |
| main/f0/vless/G1/outer | G-small | 0.100000 | 0.100000 | 4.000000 | False | 0.000008 |
| main/f0/vless/G1/outer | P-full | 1.000000 | 0.100000 | 4.000000 | False | 0.000010 |
| main/f0/vless/G1/outer | G-full | 1.000000 | 0.100000 | 4.000000 | True | 0.000008 |
| main/f0/vless/G2/outer | P-small | 0.100000 | 0.100000 | 1.000000 | False | 0.000008 |
| main/f0/vless/G2/outer | G-small | 0.100000 | 0.100000 | 1.000000 | False | 0.000008 |
| main/f0/vless/G2/outer | P-full | 1.000000 | 0.100000 | 1.000000 | False | 0.000010 |
| main/f0/vless/G2/outer | G-full | 1.000000 | 0.100000 | 1.000000 | False | 0.000009 |
| main/f0/trojan/G0/outer | P-small | 0.100000 | 0.100000 | 4.000000 | False | 0.000009 |
| main/f0/trojan/G0/outer | G-small | 0.100000 | 0.100000 | 4.000000 | False | 0.000008 |
| main/f0/trojan/G0/outer | P-full | 1.000000 | 0.100000 | 4.000000 | True | 0.000007 |
| main/f0/trojan/G0/outer | G-full | 1.000000 | 0.100000 | 4.000000 | True | 0.000007 |
| main/f0/trojan/G1/outer | P-small | 0.100000 | 0.100000 | 4.000000 | False | 0.000010 |
| main/f0/trojan/G1/outer | G-small | 0.100000 | 0.100000 | 4.000000 | False | 0.000007 |
| main/f0/trojan/G1/outer | P-full | 1.000000 | 0.100000 | 4.000000 | False | 0.000005 |
| main/f0/trojan/G1/outer | G-full | 1.000000 | 0.100000 | 4.000000 | False | 0.000007 |
| main/f0/trojan/G2/outer | P-small | 0.100000 | 0.100000 | 4.000000 | False | 0.000008 |
| main/f0/trojan/G2/outer | G-small | 0.100000 | 0.100000 | 4.000000 | False | 0.000007 |
| main/f0/trojan/G2/outer | P-full | 1.000000 | 0.100000 | 4.000000 | False | 0.000009 |
| main/f0/trojan/G2/outer | G-full | 1.000000 | 0.100000 | 4.000000 | True | 0.000010 |
| main/f0/vmess/G0/outer | P-small | 0.100000 | 10.000000 | 4.000000 | False | 0.000009 |
| main/f0/vmess/G0/outer | G-small | 0.100000 | 10.000000 | 4.000000 | False | 0.000006 |
| main/f0/vmess/G0/outer | P-full | 1.000000 | 10.000000 | 4.000000 | False | 0.000009 |
| main/f0/vmess/G0/outer | G-full | 1.000000 | 10.000000 | 4.000000 | False | 0.000010 |
| main/f0/vmess/G1/outer | P-small | 0.100000 | 0.100000 | 1.000000 | False | 0.000008 |
| main/f0/vmess/G1/outer | G-small | 0.100000 | 0.100000 | 1.000000 | False | 0.000009 |
| main/f0/vmess/G1/outer | P-full | 1.000000 | 0.100000 | 1.000000 | True | 0.000009 |
| main/f0/vmess/G1/outer | G-full | 1.000000 | 0.100000 | 1.000000 | True | 0.000008 |
| main/f0/vmess/G2/outer | P-small | 0.100000 | 0.100000 | 4.000000 | False | 0.000008 |
| main/f0/vmess/G2/outer | G-small | 0.100000 | 0.100000 | 4.000000 | False | 0.000009 |
| main/f0/vmess/G2/outer | P-full | 1.000000 | 0.100000 | 4.000000 | True | 0.000008 |
| main/f0/vmess/G2/outer | G-full | 1.000000 | 0.100000 | 4.000000 | True | 0.000009 |
| main/f1/shadowsocks/G0/outer | P-small | 0.100000 | 10.000000 | 1.000000 | False | 0.000010 |
| main/f1/shadowsocks/G0/outer | G-small | 0.100000 | 10.000000 | 1.000000 | False | 0.000010 |
| main/f1/shadowsocks/G0/outer | P-full | 1.000000 | 10.000000 | 1.000000 | False | 0.000007 |
| main/f1/shadowsocks/G0/outer | G-full | 1.000000 | 10.000000 | 1.000000 | False | 0.000008 |
| main/f1/shadowsocks/G1/outer | P-small | 0.100000 | 0.100000 | 4.000000 | False | 0.000008 |
| main/f1/shadowsocks/G1/outer | G-small | 0.100000 | 0.100000 | 4.000000 | False | 0.000010 |
| main/f1/shadowsocks/G1/outer | P-full | 1.000000 | 0.100000 | 4.000000 | False | 0.000007 |
| main/f1/shadowsocks/G1/outer | G-full | 1.000000 | 0.100000 | 4.000000 | True | 0.000010 |
| main/f1/shadowsocks/G2/outer | P-small | 0.100000 | 1.000000 | 4.000000 | False | 0.000010 |
| main/f1/shadowsocks/G2/outer | G-small | 0.100000 | 1.000000 | 4.000000 | False | 0.000010 |
| main/f1/shadowsocks/G2/outer | P-full | 1.000000 | 1.000000 | 4.000000 | True | 0.000010 |
| main/f1/shadowsocks/G2/outer | G-full | 1.000000 | 1.000000 | 4.000000 | True | 0.000008 |
| main/f1/vless/G0/outer | P-small | 0.100000 | 0.100000 | 0.000000 | False | 0.000009 |
| main/f1/vless/G0/outer | G-small | 0.100000 | 0.100000 | 0.000000 | False | 0.000009 |
| main/f1/vless/G0/outer | P-full | 1.000000 | 0.100000 | 0.000000 | False | 0.000009 |
| main/f1/vless/G0/outer | G-full | 1.000000 | 0.100000 | 0.000000 | False | 0.000010 |
| main/f1/vless/G1/outer | P-small | 0.100000 | 0.100000 | 4.000000 | False | 0.000007 |
| main/f1/vless/G1/outer | G-small | 0.100000 | 0.100000 | 4.000000 | False | 0.000009 |
| main/f1/vless/G1/outer | P-full | 1.000000 | 0.100000 | 4.000000 | False | 0.000010 |
| main/f1/vless/G1/outer | G-full | 1.000000 | 0.100000 | 4.000000 | False | 0.000008 |
| main/f1/vless/G2/outer | P-small | 0.100000 | 0.100000 | 4.000000 | False | 0.000006 |
| main/f1/vless/G2/outer | G-small | 0.100000 | 0.100000 | 4.000000 | False | 0.000009 |
| main/f1/vless/G2/outer | P-full | 1.000000 | 0.100000 | 4.000000 | False | 0.000008 |
| main/f1/vless/G2/outer | G-full | 1.000000 | 0.100000 | 4.000000 | False | 0.000007 |
| main/f1/trojan/G0/outer | P-small | 0.100000 | 0.100000 | 4.000000 | False | 0.000009 |
| main/f1/trojan/G0/outer | G-small | 0.100000 | 0.100000 | 4.000000 | False | 0.000009 |
| main/f1/trojan/G0/outer | P-full | 1.000000 | 0.100000 | 4.000000 | True | 0.000008 |
| main/f1/trojan/G0/outer | G-full | 1.000000 | 0.100000 | 4.000000 | True | 0.000005 |
| main/f1/trojan/G1/outer | P-small | 0.100000 | 0.100000 | 4.000000 | False | 0.000010 |
| main/f1/trojan/G1/outer | G-small | 0.100000 | 0.100000 | 4.000000 | False | 0.000008 |
| main/f1/trojan/G1/outer | P-full | 1.000000 | 0.100000 | 4.000000 | False | 0.000009 |
| main/f1/trojan/G1/outer | G-full | 1.000000 | 0.100000 | 4.000000 | True | 0.000010 |
| main/f1/trojan/G2/outer | P-small | 0.100000 | 0.100000 | 1.000000 | False | 0.000009 |
| main/f1/trojan/G2/outer | G-small | 0.100000 | 0.100000 | 1.000000 | False | 0.000007 |
| main/f1/trojan/G2/outer | P-full | 1.000000 | 0.100000 | 1.000000 | False | 0.000010 |
| main/f1/trojan/G2/outer | G-full | 1.000000 | 0.100000 | 1.000000 | False | 0.000010 |
| main/f1/vmess/G0/outer | P-small | 0.100000 | 10.000000 | 4.000000 | False | 0.000010 |
| main/f1/vmess/G0/outer | G-small | 0.100000 | 10.000000 | 4.000000 | False | 0.000008 |
| main/f1/vmess/G0/outer | P-full | 1.000000 | 10.000000 | 4.000000 | False | 0.000008 |
| main/f1/vmess/G0/outer | G-full | 1.000000 | 10.000000 | 4.000000 | False | 0.000008 |
| main/f1/vmess/G1/outer | P-small | 0.100000 | 0.100000 | 0.000000 | False | 0.000008 |
| main/f1/vmess/G1/outer | G-small | 0.100000 | 0.100000 | 0.000000 | False | 0.000009 |
| main/f1/vmess/G1/outer | P-full | 1.000000 | 0.100000 | 0.000000 | True | 0.000009 |
| main/f1/vmess/G1/outer | G-full | 1.000000 | 0.100000 | 0.000000 | True | 0.000009 |
| main/f1/vmess/G2/outer | P-small | 0.100000 | 0.100000 | 1.000000 | False | 0.000010 |
| main/f1/vmess/G2/outer | G-small | 0.100000 | 0.100000 | 1.000000 | False | 0.000010 |
| main/f1/vmess/G2/outer | P-full | 1.000000 | 0.100000 | 1.000000 | False | 0.000009 |
| main/f1/vmess/G2/outer | G-full | 1.000000 | 0.100000 | 1.000000 | True | 0.000010 |
| main/f2/shadowsocks/G0/outer | P-small | 0.100000 | 1.000000 | 4.000000 | False | 0.000009 |
| main/f2/shadowsocks/G0/outer | G-small | 0.100000 | 1.000000 | 4.000000 | False | 0.000008 |
| main/f2/shadowsocks/G0/outer | P-full | 1.000000 | 1.000000 | 4.000000 | True | 0.000009 |
| main/f2/shadowsocks/G0/outer | G-full | 1.000000 | 1.000000 | 4.000000 | False | 0.000009 |
| main/f2/shadowsocks/G1/outer | P-small | 0.100000 | 100.000000 | 4.000000 | False | 0.000010 |
| main/f2/shadowsocks/G1/outer | G-small | 0.100000 | 100.000000 | 4.000000 | False | 0.000010 |
| main/f2/shadowsocks/G1/outer | P-full | 1.000000 | 100.000000 | 4.000000 | False | 0.000010 |
| main/f2/shadowsocks/G1/outer | G-full | 1.000000 | 100.000000 | 4.000000 | False | 0.000008 |
| main/f2/shadowsocks/G2/outer | P-small | 0.100000 | 10.000000 | 0.250000 | False | 0.000010 |
| main/f2/shadowsocks/G2/outer | G-small | 0.100000 | 10.000000 | 0.250000 | False | 0.000010 |
| main/f2/shadowsocks/G2/outer | P-full | 1.000000 | 10.000000 | 0.250000 | False | 0.000010 |
| main/f2/shadowsocks/G2/outer | G-full | 1.000000 | 10.000000 | 0.250000 | False | 0.000010 |
| main/f2/vless/G0/outer | P-small | 0.100000 | 0.100000 | 4.000000 | False | 0.000009 |
| main/f2/vless/G0/outer | G-small | 0.100000 | 0.100000 | 4.000000 | False | 0.000009 |
| main/f2/vless/G0/outer | P-full | 1.000000 | 0.100000 | 4.000000 | False | 0.000009 |
| main/f2/vless/G0/outer | G-full | 1.000000 | 0.100000 | 4.000000 | True | 0.000008 |
| main/f2/vless/G1/outer | P-small | 0.100000 | 0.100000 | 0.000000 | False | 0.000008 |
| main/f2/vless/G1/outer | G-small | 0.100000 | 0.100000 | 0.000000 | False | 0.000010 |
| main/f2/vless/G1/outer | P-full | 1.000000 | 0.100000 | 0.000000 | False | 0.000008 |
| main/f2/vless/G1/outer | G-full | 1.000000 | 0.100000 | 0.000000 | True | 0.000009 |
| main/f2/vless/G2/outer | P-small | 0.100000 | 0.100000 | 4.000000 | False | 0.000010 |
| main/f2/vless/G2/outer | G-small | 0.100000 | 0.100000 | 4.000000 | False | 0.000009 |
| main/f2/vless/G2/outer | P-full | 1.000000 | 0.100000 | 4.000000 | False | 0.000010 |
| main/f2/vless/G2/outer | G-full | 1.000000 | 0.100000 | 4.000000 | False | 0.000008 |
| main/f2/trojan/G0/outer | P-small | 0.100000 | 0.100000 | 4.000000 | False | 0.000009 |
| main/f2/trojan/G0/outer | G-small | 0.100000 | 0.100000 | 4.000000 | False | 0.000008 |
| main/f2/trojan/G0/outer | P-full | 1.000000 | 0.100000 | 4.000000 | True | 0.000008 |
| main/f2/trojan/G0/outer | G-full | 1.000000 | 0.100000 | 4.000000 | True | 0.000007 |
| main/f2/trojan/G1/outer | P-small | 0.100000 | 0.100000 | 0.000000 | False | 0.000010 |
| main/f2/trojan/G1/outer | G-small | 0.100000 | 0.100000 | 0.000000 | False | 0.000010 |
| main/f2/trojan/G1/outer | P-full | 1.000000 | 0.100000 | 0.000000 | False | 0.000008 |
| main/f2/trojan/G1/outer | G-full | 1.000000 | 0.100000 | 0.000000 | True | 0.000010 |
| main/f2/trojan/G2/outer | P-small | 0.100000 | 0.100000 | 4.000000 | False | 0.000010 |
| main/f2/trojan/G2/outer | G-small | 0.100000 | 0.100000 | 4.000000 | False | 0.000009 |
| main/f2/trojan/G2/outer | P-full | 1.000000 | 0.100000 | 4.000000 | False | 0.000009 |
| main/f2/trojan/G2/outer | G-full | 1.000000 | 0.100000 | 4.000000 | True | 0.000010 |
| main/f2/vmess/G0/outer | P-small | 0.100000 | 0.100000 | 0.000000 | False | 0.000010 |
| main/f2/vmess/G0/outer | G-small | 0.100000 | 0.100000 | 0.000000 | False | 0.000010 |
| main/f2/vmess/G0/outer | P-full | 1.000000 | 0.100000 | 0.000000 | False | 0.000010 |
| main/f2/vmess/G0/outer | G-full | 1.000000 | 0.100000 | 0.000000 | False | 0.000009 |
| main/f2/vmess/G1/outer | P-small | 0.100000 | 0.100000 | 4.000000 | False | 0.000009 |
| main/f2/vmess/G1/outer | G-small | 0.100000 | 0.100000 | 4.000000 | False | 0.000010 |
| main/f2/vmess/G1/outer | P-full | 1.000000 | 0.100000 | 4.000000 | False | 0.000009 |
| main/f2/vmess/G1/outer | G-full | 1.000000 | 0.100000 | 4.000000 | True | 0.000007 |
| main/f2/vmess/G2/outer | P-small | 0.100000 | 0.100000 | 4.000000 | False | 0.000010 |
| main/f2/vmess/G2/outer | G-small | 0.100000 | 0.100000 | 4.000000 | False | 0.000009 |
| main/f2/vmess/G2/outer | P-full | 1.000000 | 0.100000 | 4.000000 | False | 0.000010 |
| main/f2/vmess/G2/outer | G-full | 1.000000 | 0.100000 | 4.000000 | False | 0.000008 |
| main/f3/shadowsocks/G0/outer | P-small | 0.100000 | 0.100000 | 4.000000 | False | 0.000009 |
| main/f3/shadowsocks/G0/outer | G-small | 0.100000 | 0.100000 | 4.000000 | False | 0.000007 |
| main/f3/shadowsocks/G0/outer | P-full | 1.000000 | 0.100000 | 4.000000 | False | 0.000009 |
| main/f3/shadowsocks/G0/outer | G-full | 1.000000 | 0.100000 | 4.000000 | False | 0.000009 |
| main/f3/shadowsocks/G1/outer | P-small | 0.100000 | 0.100000 | 4.000000 | False | 0.000010 |
| main/f3/shadowsocks/G1/outer | G-small | 0.100000 | 0.100000 | 4.000000 | False | 0.000010 |
| main/f3/shadowsocks/G1/outer | P-full | 1.000000 | 0.100000 | 4.000000 | False | 0.000009 |
| main/f3/shadowsocks/G1/outer | G-full | 1.000000 | 0.100000 | 4.000000 | True | 0.000009 |
| main/f3/shadowsocks/G2/outer | P-small | 0.100000 | 10.000000 | 4.000000 | False | 0.000010 |
| main/f3/shadowsocks/G2/outer | G-small | 0.100000 | 10.000000 | 4.000000 | False | 0.000008 |
| main/f3/shadowsocks/G2/outer | P-full | 1.000000 | 10.000000 | 4.000000 | False | 0.000008 |
| main/f3/shadowsocks/G2/outer | G-full | 1.000000 | 10.000000 | 4.000000 | False | 0.000010 |
| main/f3/vless/G0/outer | P-small | 0.100000 | 0.100000 | 4.000000 | False | 0.000009 |
| main/f3/vless/G0/outer | G-small | 0.100000 | 0.100000 | 4.000000 | False | 0.000010 |
| main/f3/vless/G0/outer | P-full | 1.000000 | 0.100000 | 4.000000 | False | 0.000009 |
| main/f3/vless/G0/outer | G-full | 1.000000 | 0.100000 | 4.000000 | True | 0.000010 |
| main/f3/vless/G1/outer | P-small | 0.100000 | 0.100000 | 1.000000 | False | 0.000008 |
| main/f3/vless/G1/outer | G-small | 0.100000 | 0.100000 | 1.000000 | False | 0.000010 |
| main/f3/vless/G1/outer | P-full | 1.000000 | 0.100000 | 1.000000 | False | 0.000009 |
| main/f3/vless/G1/outer | G-full | 1.000000 | 0.100000 | 1.000000 | True | 0.000010 |
| main/f3/vless/G2/outer | P-small | 0.100000 | 0.100000 | 4.000000 | False | 0.000006 |
| main/f3/vless/G2/outer | G-small | 0.100000 | 0.100000 | 4.000000 | False | 0.000009 |
| main/f3/vless/G2/outer | P-full | 1.000000 | 0.100000 | 4.000000 | False | 0.000008 |
| main/f3/vless/G2/outer | G-full | 1.000000 | 0.100000 | 4.000000 | True | 0.000006 |
| main/f3/trojan/G0/outer | P-small | 0.100000 | 0.100000 | 1.000000 | False | 0.000008 |
| main/f3/trojan/G0/outer | G-small | 0.100000 | 0.100000 | 1.000000 | False | 0.000010 |
| main/f3/trojan/G0/outer | P-full | 1.000000 | 0.100000 | 1.000000 | False | 0.000009 |
| main/f3/trojan/G0/outer | G-full | 1.000000 | 0.100000 | 1.000000 | False | 0.000010 |
| main/f3/trojan/G1/outer | P-small | 0.100000 | 0.100000 | 4.000000 | False | 0.000009 |
| main/f3/trojan/G1/outer | G-small | 0.100000 | 0.100000 | 4.000000 | False | 0.000010 |
| main/f3/trojan/G1/outer | P-full | 1.000000 | 0.100000 | 4.000000 | False | 0.000008 |
| main/f3/trojan/G1/outer | G-full | 1.000000 | 0.100000 | 4.000000 | False | 0.000009 |
| main/f3/trojan/G2/outer | P-small | 0.100000 | 0.100000 | 4.000000 | False | 0.000006 |
| main/f3/trojan/G2/outer | G-small | 0.100000 | 0.100000 | 4.000000 | False | 0.000010 |
| main/f3/trojan/G2/outer | P-full | 1.000000 | 0.100000 | 4.000000 | True | 0.000010 |
| main/f3/trojan/G2/outer | G-full | 1.000000 | 0.100000 | 4.000000 | True | 0.000010 |
| main/f3/vmess/G0/outer | P-small | 0.100000 | 0.100000 | 4.000000 | False | 0.000009 |
| main/f3/vmess/G0/outer | G-small | 0.100000 | 0.100000 | 4.000000 | False | 0.000009 |
| main/f3/vmess/G0/outer | P-full | 1.000000 | 0.100000 | 4.000000 | True | 0.000008 |
| main/f3/vmess/G0/outer | G-full | 1.000000 | 0.100000 | 4.000000 | True | 0.000008 |
| main/f3/vmess/G1/outer | P-small | 0.100000 | 100.000000 | 4.000000 | False | 0.000009 |
| main/f3/vmess/G1/outer | G-small | 0.100000 | 100.000000 | 4.000000 | False | 0.000007 |
| main/f3/vmess/G1/outer | P-full | 1.000000 | 100.000000 | 4.000000 | False | 0.000007 |
| main/f3/vmess/G1/outer | G-full | 1.000000 | 100.000000 | 4.000000 | False | 0.000008 |
| main/f3/vmess/G2/outer | P-small | 0.100000 | 0.100000 | 4.000000 | False | 0.000009 |
| main/f3/vmess/G2/outer | G-small | 0.100000 | 0.100000 | 4.000000 | False | 0.000008 |
| main/f3/vmess/G2/outer | P-full | 1.000000 | 0.100000 | 4.000000 | False | 0.000009 |
| main/f3/vmess/G2/outer | G-full | 1.000000 | 0.100000 | 4.000000 | False | 0.000008 |
| main/f4/shadowsocks/G0/outer | P-small | 0.100000 | 1.000000 | 4.000000 | False | 0.000007 |
| main/f4/shadowsocks/G0/outer | G-small | 0.100000 | 1.000000 | 4.000000 | False | 0.000007 |
| main/f4/shadowsocks/G0/outer | P-full | 1.000000 | 1.000000 | 4.000000 | False | 0.000009 |
| main/f4/shadowsocks/G0/outer | G-full | 1.000000 | 1.000000 | 4.000000 | True | 0.000008 |
| main/f4/shadowsocks/G1/outer | P-small | 0.100000 | 1.000000 | 4.000000 | False | 0.000009 |
| main/f4/shadowsocks/G1/outer | G-small | 0.100000 | 1.000000 | 4.000000 | False | 0.000010 |
| main/f4/shadowsocks/G1/outer | P-full | 1.000000 | 1.000000 | 4.000000 | False | 0.000010 |
| main/f4/shadowsocks/G1/outer | G-full | 1.000000 | 1.000000 | 4.000000 | False | 0.000007 |
| main/f4/shadowsocks/G2/outer | P-small | 0.100000 | 1.000000 | 4.000000 | False | 0.000007 |
| main/f4/shadowsocks/G2/outer | G-small | 0.100000 | 1.000000 | 4.000000 | False | 0.000008 |
| main/f4/shadowsocks/G2/outer | P-full | 1.000000 | 1.000000 | 4.000000 | False | 0.000008 |
| main/f4/shadowsocks/G2/outer | G-full | 1.000000 | 1.000000 | 4.000000 | False | 0.000010 |
| main/f4/vless/G0/outer | P-small | 0.100000 | 0.100000 | 4.000000 | False | 0.000008 |
| main/f4/vless/G0/outer | G-small | 0.100000 | 0.100000 | 4.000000 | False | 0.000008 |
| main/f4/vless/G0/outer | P-full | 1.000000 | 0.100000 | 4.000000 | False | 0.000009 |
| main/f4/vless/G0/outer | G-full | 1.000000 | 0.100000 | 4.000000 | False | 0.000009 |
| main/f4/vless/G1/outer | P-small | 0.100000 | 0.100000 | 4.000000 | False | 0.000010 |
| main/f4/vless/G1/outer | G-small | 0.100000 | 0.100000 | 4.000000 | False | 0.000008 |
| main/f4/vless/G1/outer | P-full | 1.000000 | 0.100000 | 4.000000 | True | 0.000010 |
| main/f4/vless/G1/outer | G-full | 1.000000 | 0.100000 | 4.000000 | False | 0.000010 |
| main/f4/vless/G2/outer | P-small | 0.100000 | 0.100000 | 4.000000 | False | 0.000008 |
| main/f4/vless/G2/outer | G-small | 0.100000 | 0.100000 | 4.000000 | False | 0.000008 |
| main/f4/vless/G2/outer | P-full | 1.000000 | 0.100000 | 4.000000 | True | 0.000010 |
| main/f4/vless/G2/outer | G-full | 1.000000 | 0.100000 | 4.000000 | False | 0.000010 |
| main/f4/trojan/G0/outer | P-small | 0.100000 | 0.100000 | 4.000000 | False | 0.000009 |
| main/f4/trojan/G0/outer | G-small | 0.100000 | 0.100000 | 4.000000 | False | 0.000009 |
| main/f4/trojan/G0/outer | P-full | 1.000000 | 0.100000 | 4.000000 | False | 0.000009 |
| main/f4/trojan/G0/outer | G-full | 1.000000 | 0.100000 | 4.000000 | True | 0.000008 |
| main/f4/trojan/G1/outer | P-small | 0.100000 | 0.100000 | 0.250000 | False | 0.000010 |
| main/f4/trojan/G1/outer | G-small | 0.100000 | 0.100000 | 0.250000 | False | 0.000009 |
| main/f4/trojan/G1/outer | P-full | 1.000000 | 0.100000 | 0.250000 | False | 0.000009 |
| main/f4/trojan/G1/outer | G-full | 1.000000 | 0.100000 | 0.250000 | False | 0.000009 |
| main/f4/trojan/G2/outer | P-small | 0.100000 | 0.100000 | 4.000000 | False | 0.000009 |
| main/f4/trojan/G2/outer | G-small | 0.100000 | 0.100000 | 4.000000 | False | 0.000008 |
| main/f4/trojan/G2/outer | P-full | 1.000000 | 0.100000 | 4.000000 | True | 0.000010 |
| main/f4/trojan/G2/outer | G-full | 1.000000 | 0.100000 | 4.000000 | False | 0.000010 |
| main/f4/vmess/G0/outer | P-small | 0.100000 | 100.000000 | 1.000000 | False | 0.000009 |
| main/f4/vmess/G0/outer | G-small | 0.100000 | 100.000000 | 1.000000 | False | 0.000009 |
| main/f4/vmess/G0/outer | P-full | 1.000000 | 100.000000 | 1.000000 | False | 0.000007 |
| main/f4/vmess/G0/outer | G-full | 1.000000 | 100.000000 | 1.000000 | False | 0.000010 |
| main/f4/vmess/G1/outer | P-small | 0.100000 | 0.100000 | 0.250000 | False | 0.000009 |
| main/f4/vmess/G1/outer | G-small | 0.100000 | 0.100000 | 0.250000 | False | 0.000007 |
| main/f4/vmess/G1/outer | P-full | 1.000000 | 0.100000 | 0.250000 | False | 0.000010 |
| main/f4/vmess/G1/outer | G-full | 1.000000 | 0.100000 | 0.250000 | False | 0.000010 |
| main/f4/vmess/G2/outer | P-small | 0.100000 | 0.100000 | 1.000000 | False | 0.000009 |
| main/f4/vmess/G2/outer | G-small | 0.100000 | 0.100000 | 1.000000 | False | 0.000009 |
| main/f4/vmess/G2/outer | P-full | 1.000000 | 0.100000 | 1.000000 | False | 0.000010 |
| main/f4/vmess/G2/outer | G-full | 1.000000 | 0.100000 | 1.000000 | False | 0.000009 |

## 未验收近似汇总

仅描述，不用于新的检验或归因结论。

| arm | scope | I_unvalidated | actual_delta_CE |
| --- | --- | --- | --- |
| G-full | C | 1.703625 | -0.005637 |
| G-full | U | -6.087497 | 0.362711 |
| G-full | all | -0.893416 | 0.117145 |
| G-small | C | 1.703625 | 0.007551 |
| G-small | U | -6.087497 | -0.074419 |
| G-small | all | -0.893416 | -0.019772 |
| P-full | C | 1.006671 | -0.061143 |
| P-full | U | -6.321573 | 0.400244 |
| P-full | all | -1.436077 | 0.092653 |
| P-small | C | 1.006671 | -0.007102 |
| P-small | U | -6.321573 | -0.089151 |
| P-small | all | -1.436077 | -0.034452 |
