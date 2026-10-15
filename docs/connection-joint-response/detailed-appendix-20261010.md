# 同连接联合响应详细附录

## 分部署及遮蔽

| target      | group   | arm              |   F1_all |   accuracy |   CE_nats |    Brier |   CE_bits |   F1_uncovered |   F1_aux |
|:------------|:--------|:-----------------|---------:|-----------:|----------:|---------:|----------:|---------------:|---------:|
| shadowsocks | G0      | M-S              | 0.781391 |   0.783333 |  0.832462 | 0.344149 |  1.200988 |       0.749576 | 0.797298 |
| shadowsocks | G0      | I-S              | 0.740294 |   0.741667 |  0.898644 | 0.412900 |  1.296469 |       0.701754 | 0.759563 |
| shadowsocks | G0      | J-S              | 0.743599 |   0.750000 |  0.834337 | 0.363272 |  1.203694 |       0.686607 | 0.772096 |
| shadowsocks | G0      | J-P-small        | 0.780694 |   0.783333 |  0.673915 | 0.306776 |  0.972254 |       0.799020 | 0.771531 |
| shadowsocks | G0      | J-G-small        | 0.789910 |   0.791667 |  0.704306 | 0.306842 |  1.016099 |       0.844197 | 0.762766 |
| shadowsocks | G0      | J-RawPre-small   | 0.780192 |   0.783333 |  0.735445 | 0.319593 |  1.061023 |       0.775000 | 0.782788 |
| shadowsocks | G0      | J-RawPost-small  | 0.743599 |   0.750000 |  0.832206 | 0.362168 |  1.200620 |       0.686607 | 0.772096 |
| shadowsocks | G0      | J-Marginal-small | 0.782484 |   0.783333 |  0.704776 | 0.315469 |  1.016776 |       0.811765 | 0.767844 |
| shadowsocks | G1      | M-S              | 0.780454 |   0.783333 |  0.687189 | 0.314759 |  0.991405 |       0.717905 | 0.811728 |
| shadowsocks | G1      | I-S              | 0.748133 |   0.775000 |  0.733836 | 0.350394 |  1.058701 |       0.602564 | 0.820917 |
| shadowsocks | G1      | J-S              | 0.745784 |   0.766667 |  0.803851 | 0.360887 |  1.159711 |       0.588828 | 0.824262 |
| shadowsocks | G1      | J-P-small        | 0.787338 |   0.800000 |  0.768430 | 0.331114 |  1.108610 |       0.660256 | 0.850879 |
| shadowsocks | G1      | J-G-small        | 0.764030 |   0.775000 |  0.823462 | 0.343758 |  1.188004 |       0.617949 | 0.837071 |
| shadowsocks | G1      | J-RawPre-small   | 0.775969 |   0.791667 |  0.763830 | 0.333651 |  1.101973 |       0.651822 | 0.838043 |
| shadowsocks | G1      | J-RawPost-small  | 0.738313 |   0.758333 |  0.799797 | 0.359432 |  1.153863 |       0.573308 | 0.820815 |
| shadowsocks | G1      | J-Marginal-small | 0.762966 |   0.775000 |  0.753005 | 0.346338 |  1.086357 |       0.638889 | 0.825005 |
| shadowsocks | G2      | M-S              | 0.700225 |   0.716667 |  0.863845 | 0.430629 |  1.246265 |       0.506897 | 0.796890 |
| shadowsocks | G2      | I-S              | 0.686093 |   0.708333 |  0.856432 | 0.424557 |  1.235570 |       0.492308 | 0.782985 |
| shadowsocks | G2      | J-S              | 0.649076 |   0.658333 |  0.923400 | 0.478490 |  1.332184 |       0.516164 | 0.715532 |
| shadowsocks | G2      | J-P-small        | 0.732530 |   0.741667 |  0.743020 | 0.372554 |  1.071952 |       0.615686 | 0.790952 |
| shadowsocks | G2      | J-G-small        | 0.707154 |   0.716667 |  0.775094 | 0.396563 |  1.118224 |       0.589249 | 0.766106 |
| shadowsocks | G2      | J-RawPre-small   | 0.705440 |   0.716667 |  0.766741 | 0.398114 |  1.106174 |       0.570533 | 0.772894 |
| shadowsocks | G2      | J-RawPost-small  | 0.656503 |   0.666667 |  0.921043 | 0.477229 |  1.328785 |       0.516164 | 0.726672 |
| shadowsocks | G2      | J-Marginal-small | 0.725784 |   0.733333 |  0.735914 | 0.375703 |  1.061700 |       0.622222 | 0.777565 |
| vless       | G0      | M-S              | 0.819103 |   0.816667 |  0.601964 | 0.285436 |  0.868451 |       0.836257 | 0.810526 |
| vless       | G0      | I-S              | 0.827387 |   0.825000 |  0.575414 | 0.271528 |  0.830146 |       0.864865 | 0.808647 |
| vless       | G0      | J-S              | 0.808511 |   0.808333 |  0.586299 | 0.290099 |  0.845850 |       0.824786 | 0.800374 |
| vless       | G0      | J-P-small        | 0.817652 |   0.816667 |  0.578781 | 0.281767 |  0.835005 |       0.831984 | 0.810485 |
| vless       | G0      | J-G-small        | 0.808330 |   0.808333 |  0.546205 | 0.273273 |  0.788007 |       0.814276 | 0.805357 |
| vless       | G0      | J-RawPre-small   | 0.809095 |   0.808333 |  0.608462 | 0.296782 |  0.877825 |       0.825747 | 0.800769 |
| vless       | G0      | J-RawPost-small  | 0.808511 |   0.808333 |  0.586040 | 0.289625 |  0.845477 |       0.824786 | 0.800374 |
| vless       | G0      | J-Marginal-small | 0.808970 |   0.808333 |  0.574411 | 0.287984 |  0.828700 |       0.839917 | 0.793496 |
| vless       | G1      | M-S              | 0.823621 |   0.825000 |  0.625842 | 0.274524 |  0.902899 |       0.801351 | 0.834756 |
| vless       | G1      | I-S              | 0.802240 |   0.808333 |  0.604364 | 0.276330 |  0.871912 |       0.722689 | 0.842015 |
| vless       | G1      | J-S              | 0.792955 |   0.800000 |  0.646748 | 0.281746 |  0.933060 |       0.717664 | 0.830600 |
| vless       | G1      | J-P-small        | 0.801521 |   0.808333 |  0.644746 | 0.286589 |  0.930172 |       0.742055 | 0.831254 |
| vless       | G1      | J-G-small        | 0.801259 |   0.808333 |  0.636916 | 0.281832 |  0.918875 |       0.731602 | 0.836088 |
| vless       | G1      | J-RawPre-small   | 0.801085 |   0.808333 |  0.665422 | 0.287332 |  0.960000 |       0.742055 | 0.830600 |
| vless       | G1      | J-RawPost-small  | 0.792955 |   0.800000 |  0.646660 | 0.281188 |  0.932934 |       0.717664 | 0.830600 |
| vless       | G1      | J-Marginal-small | 0.793393 |   0.800000 |  0.682143 | 0.291791 |  0.984124 |       0.728030 | 0.826074 |
| vless       | G2      | M-S              | 0.809182 |   0.808333 |  0.617727 | 0.291812 |  0.891191 |       0.827913 | 0.799816 |
| vless       | G2      | I-S              | 0.784105 |   0.783333 |  0.647532 | 0.300883 |  0.934191 |       0.772404 | 0.789955 |
| vless       | G2      | J-S              | 0.791938 |   0.791667 |  0.606165 | 0.305289 |  0.874511 |       0.742857 | 0.816479 |
| vless       | G2      | J-P-small        | 0.793203 |   0.791667 |  0.585402 | 0.295606 |  0.844556 |       0.751351 | 0.814129 |
| vless       | G2      | J-G-small        | 0.793203 |   0.791667 |  0.582974 | 0.292341 |  0.841054 |       0.751351 | 0.814129 |
| vless       | G2      | J-RawPre-small   | 0.775363 |   0.775000 |  0.608577 | 0.307208 |  0.877991 |       0.751351 | 0.787369 |
| vless       | G2      | J-RawPost-small  | 0.791938 |   0.791667 |  0.605104 | 0.303984 |  0.872981 |       0.742857 | 0.816479 |
| vless       | G2      | J-Marginal-small | 0.801920 |   0.800000 |  0.611885 | 0.304490 |  0.882763 |       0.761608 | 0.822076 |
| trojan      | G0      | M-S              | 0.882937 |   0.883333 |  0.372270 | 0.206408 |  0.537072 |       0.925000 | 0.861905 |
| trojan      | G0      | I-S              | 0.883780 |   0.883333 |  0.321877 | 0.185740 |  0.464370 |       0.935897 | 0.857721 |
| trojan      | G0      | J-S              | 0.875017 |   0.875000 |  0.301953 | 0.172850 |  0.435626 |       0.935897 | 0.844577 |
| trojan      | G0      | J-P-small        | 0.858963 |   0.858333 |  0.314757 | 0.182118 |  0.454098 |       0.910897 | 0.832996 |
| trojan      | G0      | J-G-small        | 0.875574 |   0.875000 |  0.305353 | 0.175839 |  0.440531 |       0.923077 | 0.851822 |
| trojan      | G0      | J-RawPre-small   | 0.874040 |   0.875000 |  0.310703 | 0.180326 |  0.448249 |       0.935897 | 0.843111 |
| trojan      | G0      | J-RawPost-small  | 0.875017 |   0.875000 |  0.301831 | 0.172581 |  0.435450 |       0.935897 | 0.844577 |
| trojan      | G0      | J-Marginal-small | 0.865666 |   0.866667 |  0.316454 | 0.180405 |  0.456546 |       0.925000 | 0.835998 |
| trojan      | G1      | M-S              | 0.876144 |   0.875000 |  0.397528 | 0.205146 |  0.573511 |       0.880512 | 0.873959 |
| trojan      | G1      | I-S              | 0.851449 |   0.850000 |  0.375681 | 0.213463 |  0.541993 |       0.830634 | 0.861857 |
| trojan      | G1      | J-S              | 0.850945 |   0.850000 |  0.386652 | 0.219351 |  0.557820 |       0.814276 | 0.869279 |
| trojan      | G1      | J-P-small        | 0.832264 |   0.833333 |  0.365032 | 0.208687 |  0.526630 |       0.807445 | 0.844673 |
| trojan      | G1      | J-G-small        | 0.824285 |   0.825000 |  0.376052 | 0.208385 |  0.542528 |       0.787249 | 0.842804 |
| trojan      | G1      | J-RawPre-small   | 0.806930 |   0.808333 |  0.364224 | 0.212036 |  0.525465 |       0.758333 | 0.831228 |
| trojan      | G1      | J-RawPost-small  | 0.841705 |   0.841667 |  0.385965 | 0.219595 |  0.556830 |       0.797009 | 0.864053 |
| trojan      | G1      | J-Marginal-small | 0.841936 |   0.841667 |  0.398501 | 0.218316 |  0.574916 |       0.787249 | 0.869279 |
| trojan      | G2      | M-S              | 0.864374 |   0.866667 |  0.392410 | 0.221547 |  0.566128 |       0.799431 | 0.896845 |
| trojan      | G2      | I-S              | 0.824541 |   0.825000 |  0.376714 | 0.214859 |  0.543483 |       0.755405 | 0.859108 |
| trojan      | G2      | J-S              | 0.850653 |   0.850000 |  0.349471 | 0.199264 |  0.504180 |       0.805668 | 0.873145 |
| trojan      | G2      | J-P-small        | 0.858940 |   0.858333 |  0.346364 | 0.193776 |  0.499698 |       0.831309 | 0.872755 |
| trojan      | G2      | J-G-small        | 0.858940 |   0.858333 |  0.330820 | 0.188336 |  0.477272 |       0.831309 | 0.872755 |
| trojan      | G2      | J-RawPre-small   | 0.867807 |   0.866667 |  0.348096 | 0.196073 |  0.502196 |       0.846154 | 0.878633 |
| trojan      | G2      | J-RawPost-small  | 0.850653 |   0.850000 |  0.346264 | 0.197199 |  0.499553 |       0.805668 | 0.873145 |
| trojan      | G2      | J-Marginal-small | 0.859122 |   0.858333 |  0.366121 | 0.204744 |  0.528200 |       0.842689 | 0.867338 |
| vmess       | G0      | M-S              | 0.819534 |   0.816667 |  0.702086 | 0.295626 |  1.012897 |       0.869048 | 0.794777 |
| vmess       | G0      | I-S              | 0.796444 |   0.791667 |  0.669292 | 0.305678 |  0.965585 |       0.882432 | 0.753450 |
| vmess       | G0      | J-S              | 0.777967 |   0.775000 |  0.697935 | 0.325525 |  1.006907 |       0.818250 | 0.757825 |
| vmess       | G0      | J-P-small        | 0.801497 |   0.800000 |  0.670955 | 0.306501 |  0.967983 |       0.852381 | 0.776055 |
| vmess       | G0      | J-G-small        | 0.801497 |   0.800000 |  0.681086 | 0.307755 |  0.982599 |       0.852381 | 0.776055 |
| vmess       | G0      | J-RawPre-small   | 0.776249 |   0.775000 |  0.687367 | 0.322252 |  0.991661 |       0.802661 | 0.763043 |
| vmess       | G0      | J-RawPost-small  | 0.777967 |   0.775000 |  0.695562 | 0.324704 |  1.003484 |       0.818250 | 0.757825 |
| vmess       | G0      | J-Marginal-small | 0.784630 |   0.783333 |  0.679489 | 0.316136 |  0.980296 |       0.810924 | 0.771482 |
| vmess       | G1      | M-S              | 0.831239 |   0.833333 |  0.584078 | 0.252815 |  0.842647 |       0.749807 | 0.871956 |
| vmess       | G1      | I-S              | 0.857800 |   0.858333 |  0.568859 | 0.237017 |  0.820691 |       0.772404 | 0.900499 |
| vmess       | G1      | J-S              | 0.851268 |   0.850000 |  0.563638 | 0.243741 |  0.813157 |       0.768018 | 0.892892 |
| vmess       | G1      | J-P-small        | 0.851464 |   0.850000 |  0.548893 | 0.234893 |  0.791886 |       0.774538 | 0.889928 |
| vmess       | G1      | J-G-small        | 0.850771 |   0.850000 |  0.554632 | 0.235749 |  0.800165 |       0.783784 | 0.884264 |
| vmess       | G1      | J-RawPre-small   | 0.849945 |   0.850000 |  0.568529 | 0.247511 |  0.820214 |       0.768018 | 0.890909 |
| vmess       | G1      | J-RawPost-small  | 0.851268 |   0.850000 |  0.565638 | 0.243927 |  0.816043 |       0.768018 | 0.892892 |
| vmess       | G1      | J-Marginal-small | 0.842975 |   0.841667 |  0.558877 | 0.245558 |  0.806289 |       0.774538 | 0.877194 |
| vmess       | G2      | M-S              | 0.768209 |   0.783333 |  0.797325 | 0.345698 |  1.150297 |       0.673684 | 0.815472 |
| vmess       | G2      | I-S              | 0.776178 |   0.783333 |  0.748818 | 0.321925 |  1.080317 |       0.705929 | 0.811302 |
| vmess       | G2      | J-S              | 0.767653 |   0.775000 |  0.738456 | 0.342547 |  1.065367 |       0.705929 | 0.798515 |
| vmess       | G2      | J-P-small        | 0.779407 |   0.783333 |  0.733642 | 0.340139 |  1.058422 |       0.729604 | 0.804308 |
| vmess       | G2      | J-G-small        | 0.779407 |   0.783333 |  0.729185 | 0.339232 |  1.051991 |       0.729604 | 0.804308 |
| vmess       | G2      | J-RawPre-small   | 0.767653 |   0.775000 |  0.732330 | 0.339182 |  1.056529 |       0.705929 | 0.798515 |
| vmess       | G2      | J-RawPost-small  | 0.767653 |   0.775000 |  0.739936 | 0.343438 |  1.067503 |       0.705929 | 0.798515 |
| vmess       | G2      | J-Marginal-small | 0.787389 |   0.791667 |  0.749077 | 0.340458 |  1.080689 |       0.729604 | 0.816282 |

## 六业务分项

| target      | group   | arm              | label                                |       F1 |
|:------------|:--------|:-----------------|:-------------------------------------|---------:|
| shadowsocks | G0      | M-S              | bing.com::search_results_view        | 0.789474 |
| shadowsocks | G0      | M-S              | developer.mozilla.org::document_view | 0.780488 |
| shadowsocks | G0      | M-S              | github.com::repository_view          | 0.709677 |
| shadowsocks | G0      | M-S              | wikipedia.org::article_view          | 0.850000 |
| shadowsocks | G0      | M-S              | youtube.com::search_results_view     | 0.789474 |
| shadowsocks | G0      | M-S              | youtube.com::video_playback          | 0.769231 |
| shadowsocks | G0      | I-S              | bing.com::search_results_view        | 0.864865 |
| shadowsocks | G0      | I-S              | developer.mozilla.org::document_view | 0.761905 |
| shadowsocks | G0      | I-S              | github.com::repository_view          | 0.666667 |
| shadowsocks | G0      | I-S              | wikipedia.org::article_view          | 0.684211 |
| shadowsocks | G0      | I-S              | youtube.com::search_results_view     | 0.736842 |
| shadowsocks | G0      | I-S              | youtube.com::video_playback          | 0.727273 |
| shadowsocks | G0      | J-S              | bing.com::search_results_view        | 0.878049 |
| shadowsocks | G0      | J-S              | developer.mozilla.org::document_view | 0.809524 |
| shadowsocks | G0      | J-S              | github.com::repository_view          | 0.687500 |
| shadowsocks | G0      | J-S              | wikipedia.org::article_view          | 0.631579 |
| shadowsocks | G0      | J-S              | youtube.com::search_results_view     | 0.685714 |
| shadowsocks | G0      | J-S              | youtube.com::video_playback          | 0.769231 |
| shadowsocks | G0      | J-P-small        | bing.com::search_results_view        | 0.900000 |
| shadowsocks | G0      | J-P-small        | developer.mozilla.org::document_view | 0.790698 |
| shadowsocks | G0      | J-P-small        | github.com::repository_view          | 0.833333 |
| shadowsocks | G0      | J-P-small        | wikipedia.org::article_view          | 0.611111 |
| shadowsocks | G0      | J-P-small        | youtube.com::search_results_view     | 0.764706 |
| shadowsocks | G0      | J-P-small        | youtube.com::video_playback          | 0.784314 |
| shadowsocks | G0      | J-G-small        | bing.com::search_results_view        | 0.878049 |
| shadowsocks | G0      | J-G-small        | developer.mozilla.org::document_view | 0.761905 |
| shadowsocks | G0      | J-G-small        | github.com::repository_view          | 0.864865 |
| shadowsocks | G0      | J-G-small        | wikipedia.org::article_view          | 0.611111 |
| shadowsocks | G0      | J-G-small        | youtube.com::search_results_view     | 0.823529 |
| shadowsocks | G0      | J-G-small        | youtube.com::video_playback          | 0.800000 |
| shadowsocks | G0      | J-RawPre-small   | bing.com::search_results_view        | 0.878049 |
| shadowsocks | G0      | J-RawPre-small   | developer.mozilla.org::document_view | 0.837209 |
| shadowsocks | G0      | J-RawPre-small   | github.com::repository_view          | 0.800000 |
| shadowsocks | G0      | J-RawPre-small   | wikipedia.org::article_view          | 0.631579 |
| shadowsocks | G0      | J-RawPre-small   | youtube.com::search_results_view     | 0.750000 |
| shadowsocks | G0      | J-RawPre-small   | youtube.com::video_playback          | 0.784314 |
| shadowsocks | G0      | J-RawPost-small  | bing.com::search_results_view        | 0.878049 |
| shadowsocks | G0      | J-RawPost-small  | developer.mozilla.org::document_view | 0.809524 |
| shadowsocks | G0      | J-RawPost-small  | github.com::repository_view          | 0.687500 |
| shadowsocks | G0      | J-RawPost-small  | wikipedia.org::article_view          | 0.631579 |
| shadowsocks | G0      | J-RawPost-small  | youtube.com::search_results_view     | 0.685714 |
| shadowsocks | G0      | J-RawPost-small  | youtube.com::video_playback          | 0.769231 |
| shadowsocks | G0      | J-Marginal-small | bing.com::search_results_view        | 0.850000 |
| shadowsocks | G0      | J-Marginal-small | developer.mozilla.org::document_view | 0.772727 |
| shadowsocks | G0      | J-Marginal-small | github.com::repository_view          | 0.800000 |
| shadowsocks | G0      | J-Marginal-small | wikipedia.org::article_view          | 0.648649 |
| shadowsocks | G0      | J-Marginal-small | youtube.com::search_results_view     | 0.823529 |
| shadowsocks | G0      | J-Marginal-small | youtube.com::video_playback          | 0.800000 |
| shadowsocks | G1      | M-S              | bing.com::search_results_view        | 0.810811 |
| shadowsocks | G1      | M-S              | developer.mozilla.org::document_view | 0.708333 |
| shadowsocks | G1      | M-S              | github.com::repository_view          | 0.864865 |
| shadowsocks | G1      | M-S              | wikipedia.org::article_view          | 0.625000 |
| shadowsocks | G1      | M-S              | youtube.com::search_results_view     | 0.829268 |
| shadowsocks | G1      | M-S              | youtube.com::video_playback          | 0.844444 |
| shadowsocks | G1      | I-S              | bing.com::search_results_view        | 0.871795 |
| shadowsocks | G1      | I-S              | developer.mozilla.org::document_view | 0.692308 |
| shadowsocks | G1      | I-S              | github.com::repository_view          | 0.871795 |
| shadowsocks | G1      | I-S              | wikipedia.org::article_view          | 0.333333 |
| shadowsocks | G1      | I-S              | youtube.com::search_results_view     | 0.850000 |
| shadowsocks | G1      | I-S              | youtube.com::video_playback          | 0.869565 |
| shadowsocks | G1      | J-S              | bing.com::search_results_view        | 0.820513 |
| shadowsocks | G1      | J-S              | developer.mozilla.org::document_view | 0.730769 |
| shadowsocks | G1      | J-S              | github.com::repository_view          | 0.904762 |
| shadowsocks | G1      | J-S              | wikipedia.org::article_view          | 0.357143 |
| shadowsocks | G1      | J-S              | youtube.com::search_results_view     | 0.756757 |
| shadowsocks | G1      | J-S              | youtube.com::video_playback          | 0.904762 |
| shadowsocks | G1      | J-P-small        | bing.com::search_results_view        | 0.820513 |
| shadowsocks | G1      | J-P-small        | developer.mozilla.org::document_view | 0.693878 |
| shadowsocks | G1      | J-P-small        | github.com::repository_view          | 0.904762 |
| shadowsocks | G1      | J-P-small        | wikipedia.org::article_view          | 0.500000 |
| shadowsocks | G1      | J-P-small        | youtube.com::search_results_view     | 0.878049 |
| shadowsocks | G1      | J-P-small        | youtube.com::video_playback          | 0.926829 |
| shadowsocks | G1      | J-G-small        | bing.com::search_results_view        | 0.769231 |
| shadowsocks | G1      | J-G-small        | developer.mozilla.org::document_view | 0.705882 |
| shadowsocks | G1      | J-G-small        | github.com::repository_view          | 0.904762 |
| shadowsocks | G1      | J-G-small        | wikipedia.org::article_view          | 0.466667 |
| shadowsocks | G1      | J-G-small        | youtube.com::search_results_view     | 0.810811 |
| shadowsocks | G1      | J-G-small        | youtube.com::video_playback          | 0.926829 |
| shadowsocks | G1      | J-RawPre-small   | bing.com::search_results_view        | 0.842105 |
| shadowsocks | G1      | J-RawPre-small   | developer.mozilla.org::document_view | 0.716981 |
| shadowsocks | G1      | J-RawPre-small   | github.com::repository_view          | 0.857143 |
| shadowsocks | G1      | J-RawPre-small   | wikipedia.org::article_view          | 0.461538 |
| shadowsocks | G1      | J-RawPre-small   | youtube.com::search_results_view     | 0.900000 |
| shadowsocks | G1      | J-RawPre-small   | youtube.com::video_playback          | 0.878049 |
| shadowsocks | G1      | J-RawPost-small  | bing.com::search_results_view        | 0.789474 |
| shadowsocks | G1      | J-RawPost-small  | developer.mozilla.org::document_view | 0.716981 |
| shadowsocks | G1      | J-RawPost-small  | github.com::repository_view          | 0.904762 |
| shadowsocks | G1      | J-RawPost-small  | wikipedia.org::article_view          | 0.357143 |
| shadowsocks | G1      | J-RawPost-small  | youtube.com::search_results_view     | 0.756757 |
| shadowsocks | G1      | J-RawPost-small  | youtube.com::video_playback          | 0.904762 |
| shadowsocks | G1      | J-Marginal-small | bing.com::search_results_view        | 0.777778 |
| shadowsocks | G1      | J-Marginal-small | developer.mozilla.org::document_view | 0.680000 |
| shadowsocks | G1      | J-Marginal-small | github.com::repository_view          | 0.837209 |
| shadowsocks | G1      | J-Marginal-small | wikipedia.org::article_view          | 0.500000 |
| shadowsocks | G1      | J-Marginal-small | youtube.com::search_results_view     | 0.878049 |
| shadowsocks | G1      | J-Marginal-small | youtube.com::video_playback          | 0.904762 |
| shadowsocks | G2      | M-S              | bing.com::search_results_view        | 0.772727 |
| shadowsocks | G2      | M-S              | developer.mozilla.org::document_view | 0.413793 |
| shadowsocks | G2      | M-S              | github.com::repository_view          | 0.923077 |
| shadowsocks | G2      | M-S              | wikipedia.org::article_view          | 0.654545 |
| shadowsocks | G2      | M-S              | youtube.com::search_results_view     | 0.837209 |
| shadowsocks | G2      | M-S              | youtube.com::video_playback          | 0.600000 |
| shadowsocks | G2      | I-S              | bing.com::search_results_view        | 0.809524 |
| shadowsocks | G2      | I-S              | developer.mozilla.org::document_view | 0.384615 |
| shadowsocks | G2      | I-S              | github.com::repository_view          | 0.926829 |
| shadowsocks | G2      | I-S              | wikipedia.org::article_view          | 0.629630 |
| shadowsocks | G2      | I-S              | youtube.com::search_results_view     | 0.765957 |
| shadowsocks | G2      | I-S              | youtube.com::video_playback          | 0.600000 |
| shadowsocks | G2      | J-S              | bing.com::search_results_view        | 0.790698 |
| shadowsocks | G2      | J-S              | developer.mozilla.org::document_view | 0.344828 |
| shadowsocks | G2      | J-S              | github.com::repository_view          | 0.904762 |
| shadowsocks | G2      | J-S              | wikipedia.org::article_view          | 0.500000 |
| shadowsocks | G2      | J-S              | youtube.com::search_results_view     | 0.666667 |
| shadowsocks | G2      | J-S              | youtube.com::video_playback          | 0.687500 |
| shadowsocks | G2      | J-P-small        | bing.com::search_results_view        | 0.809524 |
| shadowsocks | G2      | J-P-small        | developer.mozilla.org::document_view | 0.466667 |
| shadowsocks | G2      | J-P-small        | github.com::repository_view          | 0.904762 |
| shadowsocks | G2      | J-P-small        | wikipedia.org::article_view          | 0.640000 |
| shadowsocks | G2      | J-P-small        | youtube.com::search_results_view     | 0.809524 |
| shadowsocks | G2      | J-P-small        | youtube.com::video_playback          | 0.764706 |
| shadowsocks | G2      | J-G-small        | bing.com::search_results_view        | 0.809524 |
| shadowsocks | G2      | J-G-small        | developer.mozilla.org::document_view | 0.413793 |
| shadowsocks | G2      | J-G-small        | github.com::repository_view          | 0.904762 |
| shadowsocks | G2      | J-G-small        | wikipedia.org::article_view          | 0.588235 |
| shadowsocks | G2      | J-G-small        | youtube.com::search_results_view     | 0.761905 |
| shadowsocks | G2      | J-G-small        | youtube.com::video_playback          | 0.764706 |
| shadowsocks | G2      | J-RawPre-small   | bing.com::search_results_view        | 0.809524 |
| shadowsocks | G2      | J-RawPre-small   | developer.mozilla.org::document_view | 0.413793 |
| shadowsocks | G2      | J-RawPre-small   | github.com::repository_view          | 0.904762 |
| shadowsocks | G2      | J-RawPre-small   | wikipedia.org::article_view          | 0.615385 |
| shadowsocks | G2      | J-RawPre-small   | youtube.com::search_results_view     | 0.761905 |
| shadowsocks | G2      | J-RawPre-small   | youtube.com::video_playback          | 0.727273 |
| shadowsocks | G2      | J-RawPost-small  | bing.com::search_results_view        | 0.790698 |
| shadowsocks | G2      | J-RawPost-small  | developer.mozilla.org::document_view | 0.344828 |
| shadowsocks | G2      | J-RawPost-small  | github.com::repository_view          | 0.904762 |
| shadowsocks | G2      | J-RawPost-small  | wikipedia.org::article_view          | 0.528302 |
| shadowsocks | G2      | J-RawPost-small  | youtube.com::search_results_view     | 0.682927 |
| shadowsocks | G2      | J-RawPost-small  | youtube.com::video_playback          | 0.687500 |
| shadowsocks | G2      | J-Marginal-small | bing.com::search_results_view        | 0.790698 |
| shadowsocks | G2      | J-Marginal-small | developer.mozilla.org::document_view | 0.466667 |
| shadowsocks | G2      | J-Marginal-small | github.com::repository_view          | 0.878049 |
| shadowsocks | G2      | J-Marginal-small | wikipedia.org::article_view          | 0.612245 |
| shadowsocks | G2      | J-Marginal-small | youtube.com::search_results_view     | 0.829268 |
| shadowsocks | G2      | J-Marginal-small | youtube.com::video_playback          | 0.777778 |
| vless       | G0      | M-S              | bing.com::search_results_view        | 0.923077 |
| vless       | G0      | M-S              | developer.mozilla.org::document_view | 0.800000 |
| vless       | G0      | M-S              | github.com::repository_view          | 0.894737 |
| vless       | G0      | M-S              | wikipedia.org::article_view          | 0.681818 |
| vless       | G0      | M-S              | youtube.com::search_results_view     | 0.777778 |
| vless       | G0      | M-S              | youtube.com::video_playback          | 0.837209 |
| vless       | G0      | I-S              | bing.com::search_results_view        | 0.878049 |
| vless       | G0      | I-S              | developer.mozilla.org::document_view | 0.800000 |
| vless       | G0      | I-S              | github.com::repository_view          | 0.918919 |
| vless       | G0      | I-S              | wikipedia.org::article_view          | 0.727273 |
| vless       | G0      | I-S              | youtube.com::search_results_view     | 0.810811 |
| vless       | G0      | I-S              | youtube.com::video_playback          | 0.829268 |
| vless       | G0      | J-S              | bing.com::search_results_view        | 0.850000 |
| vless       | G0      | J-S              | developer.mozilla.org::document_view | 0.800000 |
| vless       | G0      | J-S              | github.com::repository_view          | 0.871795 |
| vless       | G0      | J-S              | wikipedia.org::article_view          | 0.714286 |
| vless       | G0      | J-S              | youtube.com::search_results_view     | 0.777778 |
| vless       | G0      | J-S              | youtube.com::video_playback          | 0.837209 |
| vless       | G0      | J-P-small        | bing.com::search_results_view        | 0.850000 |
| vless       | G0      | J-P-small        | developer.mozilla.org::document_view | 0.820513 |
| vless       | G0      | J-P-small        | github.com::repository_view          | 0.894737 |
| vless       | G0      | J-P-small        | wikipedia.org::article_view          | 0.714286 |
| vless       | G0      | J-P-small        | youtube.com::search_results_view     | 0.769231 |
| vless       | G0      | J-P-small        | youtube.com::video_playback          | 0.857143 |
| vless       | G0      | J-G-small        | bing.com::search_results_view        | 0.850000 |
| vless       | G0      | J-G-small        | developer.mozilla.org::document_view | 0.800000 |
| vless       | G0      | J-G-small        | github.com::repository_view          | 0.871795 |
| vless       | G0      | J-G-small        | wikipedia.org::article_view          | 0.714286 |
| vless       | G0      | J-G-small        | youtube.com::search_results_view     | 0.756757 |
| vless       | G0      | J-G-small        | youtube.com::video_playback          | 0.857143 |
| vless       | G0      | J-RawPre-small   | bing.com::search_results_view        | 0.850000 |
| vless       | G0      | J-RawPre-small   | developer.mozilla.org::document_view | 0.829268 |
| vless       | G0      | J-RawPre-small   | github.com::repository_view          | 0.894737 |
| vless       | G0      | J-RawPre-small   | wikipedia.org::article_view          | 0.714286 |
| vless       | G0      | J-RawPre-small   | youtube.com::search_results_view     | 0.756757 |
| vless       | G0      | J-RawPre-small   | youtube.com::video_playback          | 0.809524 |
| vless       | G0      | J-RawPost-small  | bing.com::search_results_view        | 0.850000 |
| vless       | G0      | J-RawPost-small  | developer.mozilla.org::document_view | 0.800000 |
| vless       | G0      | J-RawPost-small  | github.com::repository_view          | 0.871795 |
| vless       | G0      | J-RawPost-small  | wikipedia.org::article_view          | 0.714286 |
| vless       | G0      | J-RawPost-small  | youtube.com::search_results_view     | 0.777778 |
| vless       | G0      | J-RawPost-small  | youtube.com::video_playback          | 0.837209 |
| vless       | G0      | J-Marginal-small | bing.com::search_results_view        | 0.878049 |
| vless       | G0      | J-Marginal-small | developer.mozilla.org::document_view | 0.800000 |
| vless       | G0      | J-Marginal-small | github.com::repository_view          | 0.923077 |
| vless       | G0      | J-Marginal-small | wikipedia.org::article_view          | 0.666667 |
| vless       | G0      | J-Marginal-small | youtube.com::search_results_view     | 0.756757 |
| vless       | G0      | J-Marginal-small | youtube.com::video_playback          | 0.829268 |
| vless       | G1      | M-S              | bing.com::search_results_view        | 0.900000 |
| vless       | G1      | M-S              | developer.mozilla.org::document_view | 0.829268 |
| vless       | G1      | M-S              | github.com::repository_view          | 0.900000 |
| vless       | G1      | M-S              | wikipedia.org::article_view          | 0.702703 |
| vless       | G1      | M-S              | youtube.com::search_results_view     | 0.731707 |
| vless       | G1      | M-S              | youtube.com::video_playback          | 0.878049 |
| vless       | G1      | I-S              | bing.com::search_results_view        | 0.857143 |
| vless       | G1      | I-S              | developer.mozilla.org::document_view | 0.809524 |
| vless       | G1      | I-S              | github.com::repository_view          | 0.900000 |
| vless       | G1      | I-S              | wikipedia.org::article_view          | 0.588235 |
| vless       | G1      | I-S              | youtube.com::search_results_view     | 0.780488 |
| vless       | G1      | I-S              | youtube.com::video_playback          | 0.878049 |
| vless       | G1      | J-S              | bing.com::search_results_view        | 0.829268 |
| vless       | G1      | J-S              | developer.mozilla.org::document_view | 0.837209 |
| vless       | G1      | J-S              | github.com::repository_view          | 0.878049 |
| vless       | G1      | J-S              | wikipedia.org::article_view          | 0.606061 |
| vless       | G1      | J-S              | youtube.com::search_results_view     | 0.750000 |
| vless       | G1      | J-S              | youtube.com::video_playback          | 0.857143 |
| vless       | G1      | J-P-small        | bing.com::search_results_view        | 0.878049 |
| vless       | G1      | J-P-small        | developer.mozilla.org::document_view | 0.837209 |
| vless       | G1      | J-P-small        | github.com::repository_view          | 0.878049 |
| vless       | G1      | J-P-small        | wikipedia.org::article_view          | 0.606061 |
| vless       | G1      | J-P-small        | youtube.com::search_results_view     | 0.780488 |
| vless       | G1      | J-P-small        | youtube.com::video_playback          | 0.829268 |
| vless       | G1      | J-G-small        | bing.com::search_results_view        | 0.857143 |
| vless       | G1      | J-G-small        | developer.mozilla.org::document_view | 0.837209 |
| vless       | G1      | J-G-small        | github.com::repository_view          | 0.900000 |
| vless       | G1      | J-G-small        | wikipedia.org::article_view          | 0.606061 |
| vless       | G1      | J-G-small        | youtube.com::search_results_view     | 0.750000 |
| vless       | G1      | J-G-small        | youtube.com::video_playback          | 0.857143 |
| vless       | G1      | J-RawPre-small   | bing.com::search_results_view        | 0.878049 |
| vless       | G1      | J-RawPre-small   | developer.mozilla.org::document_view | 0.837209 |
| vless       | G1      | J-RawPre-small   | github.com::repository_view          | 0.878049 |
| vless       | G1      | J-RawPre-small   | wikipedia.org::article_view          | 0.606061 |
| vless       | G1      | J-RawPre-small   | youtube.com::search_results_view     | 0.750000 |
| vless       | G1      | J-RawPre-small   | youtube.com::video_playback          | 0.857143 |
| vless       | G1      | J-RawPost-small  | bing.com::search_results_view        | 0.829268 |
| vless       | G1      | J-RawPost-small  | developer.mozilla.org::document_view | 0.837209 |
| vless       | G1      | J-RawPost-small  | github.com::repository_view          | 0.878049 |
| vless       | G1      | J-RawPost-small  | wikipedia.org::article_view          | 0.606061 |
| vless       | G1      | J-RawPost-small  | youtube.com::search_results_view     | 0.750000 |
| vless       | G1      | J-RawPost-small  | youtube.com::video_playback          | 0.857143 |
| vless       | G1      | J-Marginal-small | bing.com::search_results_view        | 0.850000 |
| vless       | G1      | J-Marginal-small | developer.mozilla.org::document_view | 0.857143 |
| vless       | G1      | J-Marginal-small | github.com::repository_view          | 0.857143 |
| vless       | G1      | J-Marginal-small | wikipedia.org::article_view          | 0.606061 |
| vless       | G1      | J-Marginal-small | youtube.com::search_results_view     | 0.780488 |
| vless       | G1      | J-Marginal-small | youtube.com::video_playback          | 0.809524 |
| vless       | G2      | M-S              | bing.com::search_results_view        | 0.904762 |
| vless       | G2      | M-S              | developer.mozilla.org::document_view | 0.777778 |
| vless       | G2      | M-S              | github.com::repository_view          | 0.894737 |
| vless       | G2      | M-S              | wikipedia.org::article_view          | 0.681818 |
| vless       | G2      | M-S              | youtube.com::search_results_view     | 0.717949 |
| vless       | G2      | M-S              | youtube.com::video_playback          | 0.878049 |
| vless       | G2      | I-S              | bing.com::search_results_view        | 0.837209 |
| vless       | G2      | I-S              | developer.mozilla.org::document_view | 0.702703 |
| vless       | G2      | I-S              | github.com::repository_view          | 0.923077 |
| vless       | G2      | I-S              | wikipedia.org::article_view          | 0.619048 |
| vless       | G2      | I-S              | youtube.com::search_results_view     | 0.780488 |
| vless       | G2      | I-S              | youtube.com::video_playback          | 0.842105 |
| vless       | G2      | J-S              | bing.com::search_results_view        | 0.857143 |
| vless       | G2      | J-S              | developer.mozilla.org::document_view | 0.685714 |
| vless       | G2      | J-S              | github.com::repository_view          | 0.900000 |
| vless       | G2      | J-S              | wikipedia.org::article_view          | 0.666667 |
| vless       | G2      | J-S              | youtube.com::search_results_view     | 0.842105 |
| vless       | G2      | J-S              | youtube.com::video_playback          | 0.800000 |
| vless       | G2      | J-P-small        | bing.com::search_results_view        | 0.878049 |
| vless       | G2      | J-P-small        | developer.mozilla.org::document_view | 0.702703 |
| vless       | G2      | J-P-small        | github.com::repository_view          | 0.900000 |
| vless       | G2      | J-P-small        | wikipedia.org::article_view          | 0.636364 |
| vless       | G2      | J-P-small        | youtube.com::search_results_view     | 0.842105 |
| vless       | G2      | J-P-small        | youtube.com::video_playback          | 0.800000 |
| vless       | G2      | J-G-small        | bing.com::search_results_view        | 0.878049 |
| vless       | G2      | J-G-small        | developer.mozilla.org::document_view | 0.702703 |
| vless       | G2      | J-G-small        | github.com::repository_view          | 0.900000 |
| vless       | G2      | J-G-small        | wikipedia.org::article_view          | 0.636364 |
| vless       | G2      | J-G-small        | youtube.com::search_results_view     | 0.842105 |
| vless       | G2      | J-G-small        | youtube.com::video_playback          | 0.800000 |
| vless       | G2      | J-RawPre-small   | bing.com::search_results_view        | 0.878049 |
| vless       | G2      | J-RawPre-small   | developer.mozilla.org::document_view | 0.702703 |
| vless       | G2      | J-RawPre-small   | github.com::repository_view          | 0.900000 |
| vless       | G2      | J-RawPre-small   | wikipedia.org::article_view          | 0.571429 |
| vless       | G2      | J-RawPre-small   | youtube.com::search_results_view     | 0.800000 |
| vless       | G2      | J-RawPre-small   | youtube.com::video_playback          | 0.800000 |
| vless       | G2      | J-RawPost-small  | bing.com::search_results_view        | 0.857143 |
| vless       | G2      | J-RawPost-small  | developer.mozilla.org::document_view | 0.685714 |
| vless       | G2      | J-RawPost-small  | github.com::repository_view          | 0.900000 |
| vless       | G2      | J-RawPost-small  | wikipedia.org::article_view          | 0.666667 |
| vless       | G2      | J-RawPost-small  | youtube.com::search_results_view     | 0.842105 |
| vless       | G2      | J-RawPost-small  | youtube.com::video_playback          | 0.800000 |
| vless       | G2      | J-Marginal-small | bing.com::search_results_view        | 0.878049 |
| vless       | G2      | J-Marginal-small | developer.mozilla.org::document_view | 0.702703 |
| vless       | G2      | J-Marginal-small | github.com::repository_view          | 0.923077 |
| vless       | G2      | J-Marginal-small | wikipedia.org::article_view          | 0.666667 |
| vless       | G2      | J-Marginal-small | youtube.com::search_results_view     | 0.820513 |
| vless       | G2      | J-Marginal-small | youtube.com::video_playback          | 0.820513 |
| trojan      | G0      | M-S              | bing.com::search_results_view        | 0.871795 |
| trojan      | G0      | M-S              | developer.mozilla.org::document_view | 0.850000 |
| trojan      | G0      | M-S              | github.com::repository_view          | 1.000000 |
| trojan      | G0      | M-S              | wikipedia.org::article_view          | 0.842105 |
| trojan      | G0      | M-S              | youtube.com::search_results_view     | 0.850000 |
| trojan      | G0      | M-S              | youtube.com::video_playback          | 0.883721 |
| trojan      | G0      | I-S              | bing.com::search_results_view        | 0.947368 |
| trojan      | G0      | I-S              | developer.mozilla.org::document_view | 0.809524 |
| trojan      | G0      | I-S              | github.com::repository_view          | 1.000000 |
| trojan      | G0      | I-S              | wikipedia.org::article_view          | 0.769231 |
| trojan      | G0      | I-S              | youtube.com::search_results_view     | 0.871795 |
| trojan      | G0      | I-S              | youtube.com::video_playback          | 0.904762 |
| trojan      | G0      | J-S              | bing.com::search_results_view        | 0.947368 |
| trojan      | G0      | J-S              | developer.mozilla.org::document_view | 0.829268 |
| trojan      | G0      | J-S              | github.com::repository_view          | 1.000000 |
| trojan      | G0      | J-S              | wikipedia.org::article_view          | 0.717949 |
| trojan      | G0      | J-S              | youtube.com::search_results_view     | 0.871795 |
| trojan      | G0      | J-S              | youtube.com::video_playback          | 0.883721 |
| trojan      | G0      | J-P-small        | bing.com::search_results_view        | 0.947368 |
| trojan      | G0      | J-P-small        | developer.mozilla.org::document_view | 0.809524 |
| trojan      | G0      | J-P-small        | github.com::repository_view          | 0.950000 |
| trojan      | G0      | J-P-small        | wikipedia.org::article_view          | 0.717949 |
| trojan      | G0      | J-P-small        | youtube.com::search_results_view     | 0.871795 |
| trojan      | G0      | J-P-small        | youtube.com::video_playback          | 0.857143 |
| trojan      | G0      | J-G-small        | bing.com::search_results_view        | 0.947368 |
| trojan      | G0      | J-G-small        | developer.mozilla.org::document_view | 0.837209 |
| trojan      | G0      | J-G-small        | github.com::repository_view          | 0.974359 |
| trojan      | G0      | J-G-small        | wikipedia.org::article_view          | 0.717949 |
| trojan      | G0      | J-G-small        | youtube.com::search_results_view     | 0.871795 |
| trojan      | G0      | J-G-small        | youtube.com::video_playback          | 0.904762 |
| trojan      | G0      | J-RawPre-small   | bing.com::search_results_view        | 0.947368 |
| trojan      | G0      | J-RawPre-small   | developer.mozilla.org::document_view | 0.857143 |
| trojan      | G0      | J-RawPre-small   | github.com::repository_view          | 1.000000 |
| trojan      | G0      | J-RawPre-small   | wikipedia.org::article_view          | 0.684211 |
| trojan      | G0      | J-RawPre-small   | youtube.com::search_results_view     | 0.871795 |
| trojan      | G0      | J-RawPre-small   | youtube.com::video_playback          | 0.883721 |
| trojan      | G0      | J-RawPost-small  | bing.com::search_results_view        | 0.947368 |
| trojan      | G0      | J-RawPost-small  | developer.mozilla.org::document_view | 0.829268 |
| trojan      | G0      | J-RawPost-small  | github.com::repository_view          | 1.000000 |
| trojan      | G0      | J-RawPost-small  | wikipedia.org::article_view          | 0.717949 |
| trojan      | G0      | J-RawPost-small  | youtube.com::search_results_view     | 0.871795 |
| trojan      | G0      | J-RawPost-small  | youtube.com::video_playback          | 0.883721 |
| trojan      | G0      | J-Marginal-small | bing.com::search_results_view        | 0.918919 |
| trojan      | G0      | J-Marginal-small | developer.mozilla.org::document_view | 0.857143 |
| trojan      | G0      | J-Marginal-small | github.com::repository_view          | 1.000000 |
| trojan      | G0      | J-Marginal-small | wikipedia.org::article_view          | 0.684211 |
| trojan      | G0      | J-Marginal-small | youtube.com::search_results_view     | 0.850000 |
| trojan      | G0      | J-Marginal-small | youtube.com::video_playback          | 0.883721 |
| trojan      | G1      | M-S              | bing.com::search_results_view        | 0.918919 |
| trojan      | G1      | M-S              | developer.mozilla.org::document_view | 0.818182 |
| trojan      | G1      | M-S              | github.com::repository_view          | 1.000000 |
| trojan      | G1      | M-S              | wikipedia.org::article_view          | 0.842105 |
| trojan      | G1      | M-S              | youtube.com::search_results_view     | 0.820513 |
| trojan      | G1      | M-S              | youtube.com::video_playback          | 0.857143 |
| trojan      | G1      | I-S              | bing.com::search_results_view        | 0.871795 |
| trojan      | G1      | I-S              | developer.mozilla.org::document_view | 0.727273 |
| trojan      | G1      | I-S              | github.com::repository_view          | 1.000000 |
| trojan      | G1      | I-S              | wikipedia.org::article_view          | 0.789474 |
| trojan      | G1      | I-S              | youtube.com::search_results_view     | 0.842105 |
| trojan      | G1      | I-S              | youtube.com::video_playback          | 0.878049 |
| trojan      | G1      | J-S              | bing.com::search_results_view        | 0.871795 |
| trojan      | G1      | J-S              | developer.mozilla.org::document_view | 0.727273 |
| trojan      | G1      | J-S              | github.com::repository_view          | 1.000000 |
| trojan      | G1      | J-S              | wikipedia.org::article_view          | 0.756757 |
| trojan      | G1      | J-S              | youtube.com::search_results_view     | 0.871795 |
| trojan      | G1      | J-S              | youtube.com::video_playback          | 0.878049 |
| trojan      | G1      | J-P-small        | bing.com::search_results_view        | 0.878049 |
| trojan      | G1      | J-P-small        | developer.mozilla.org::document_view | 0.731707 |
| trojan      | G1      | J-P-small        | github.com::repository_view          | 0.975610 |
| trojan      | G1      | J-P-small        | wikipedia.org::article_view          | 0.736842 |
| trojan      | G1      | J-P-small        | youtube.com::search_results_view     | 0.842105 |
| trojan      | G1      | J-P-small        | youtube.com::video_playback          | 0.829268 |
| trojan      | G1      | J-G-small        | bing.com::search_results_view        | 0.871795 |
| trojan      | G1      | J-G-small        | developer.mozilla.org::document_view | 0.714286 |
| trojan      | G1      | J-G-small        | github.com::repository_view          | 0.975610 |
| trojan      | G1      | J-G-small        | wikipedia.org::article_view          | 0.702703 |
| trojan      | G1      | J-G-small        | youtube.com::search_results_view     | 0.871795 |
| trojan      | G1      | J-G-small        | youtube.com::video_playback          | 0.809524 |
| trojan      | G1      | J-RawPre-small   | bing.com::search_results_view        | 0.850000 |
| trojan      | G1      | J-RawPre-small   | developer.mozilla.org::document_view | 0.697674 |
| trojan      | G1      | J-RawPre-small   | github.com::repository_view          | 0.975610 |
| trojan      | G1      | J-RawPre-small   | wikipedia.org::article_view          | 0.666667 |
| trojan      | G1      | J-RawPre-small   | youtube.com::search_results_view     | 0.842105 |
| trojan      | G1      | J-RawPre-small   | youtube.com::video_playback          | 0.809524 |
| trojan      | G1      | J-RawPost-small  | bing.com::search_results_view        | 0.871795 |
| trojan      | G1      | J-RawPost-small  | developer.mozilla.org::document_view | 0.727273 |
| trojan      | G1      | J-RawPost-small  | github.com::repository_view          | 1.000000 |
| trojan      | G1      | J-RawPost-small  | wikipedia.org::article_view          | 0.722222 |
| trojan      | G1      | J-RawPost-small  | youtube.com::search_results_view     | 0.871795 |
| trojan      | G1      | J-RawPost-small  | youtube.com::video_playback          | 0.857143 |
| trojan      | G1      | J-Marginal-small | bing.com::search_results_view        | 0.871795 |
| trojan      | G1      | J-Marginal-small | developer.mozilla.org::document_view | 0.727273 |
| trojan      | G1      | J-Marginal-small | github.com::repository_view          | 1.000000 |
| trojan      | G1      | J-Marginal-small | wikipedia.org::article_view          | 0.702703 |
| trojan      | G1      | J-Marginal-small | youtube.com::search_results_view     | 0.871795 |
| trojan      | G1      | J-Marginal-small | youtube.com::video_playback          | 0.878049 |
| trojan      | G2      | M-S              | bing.com::search_results_view        | 0.878049 |
| trojan      | G2      | M-S              | developer.mozilla.org::document_view | 0.756757 |
| trojan      | G2      | M-S              | github.com::repository_view          | 0.975610 |
| trojan      | G2      | M-S              | wikipedia.org::article_view          | 0.850000 |
| trojan      | G2      | M-S              | youtube.com::search_results_view     | 0.883721 |
| trojan      | G2      | M-S              | youtube.com::video_playback          | 0.842105 |
| trojan      | G2      | I-S              | bing.com::search_results_view        | 0.923077 |
| trojan      | G2      | I-S              | developer.mozilla.org::document_view | 0.700000 |
| trojan      | G2      | I-S              | github.com::repository_view          | 0.952381 |
| trojan      | G2      | I-S              | wikipedia.org::article_view          | 0.682927 |
| trojan      | G2      | I-S              | youtube.com::search_results_view     | 0.878049 |
| trojan      | G2      | I-S              | youtube.com::video_playback          | 0.810811 |
| trojan      | G2      | J-S              | bing.com::search_results_view        | 0.894737 |
| trojan      | G2      | J-S              | developer.mozilla.org::document_view | 0.769231 |
| trojan      | G2      | J-S              | github.com::repository_view          | 0.975610 |
| trojan      | G2      | J-S              | wikipedia.org::article_view          | 0.744186 |
| trojan      | G2      | J-S              | youtube.com::search_results_view     | 0.878049 |
| trojan      | G2      | J-S              | youtube.com::video_playback          | 0.842105 |
| trojan      | G2      | J-P-small        | bing.com::search_results_view        | 0.923077 |
| trojan      | G2      | J-P-small        | developer.mozilla.org::document_view | 0.820513 |
| trojan      | G2      | J-P-small        | github.com::repository_view          | 0.975610 |
| trojan      | G2      | J-P-small        | wikipedia.org::article_view          | 0.714286 |
| trojan      | G2      | J-P-small        | youtube.com::search_results_view     | 0.878049 |
| trojan      | G2      | J-P-small        | youtube.com::video_playback          | 0.842105 |
| trojan      | G2      | J-G-small        | bing.com::search_results_view        | 0.923077 |
| trojan      | G2      | J-G-small        | developer.mozilla.org::document_view | 0.820513 |
| trojan      | G2      | J-G-small        | github.com::repository_view          | 0.975610 |
| trojan      | G2      | J-G-small        | wikipedia.org::article_view          | 0.714286 |
| trojan      | G2      | J-G-small        | youtube.com::search_results_view     | 0.878049 |
| trojan      | G2      | J-G-small        | youtube.com::video_playback          | 0.842105 |
| trojan      | G2      | J-RawPre-small   | bing.com::search_results_view        | 0.894737 |
| trojan      | G2      | J-RawPre-small   | developer.mozilla.org::document_view | 0.820513 |
| trojan      | G2      | J-RawPre-small   | github.com::repository_view          | 0.975610 |
| trojan      | G2      | J-RawPre-small   | wikipedia.org::article_view          | 0.744186 |
| trojan      | G2      | J-RawPre-small   | youtube.com::search_results_view     | 0.900000 |
| trojan      | G2      | J-RawPre-small   | youtube.com::video_playback          | 0.871795 |
| trojan      | G2      | J-RawPost-small  | bing.com::search_results_view        | 0.894737 |
| trojan      | G2      | J-RawPost-small  | developer.mozilla.org::document_view | 0.769231 |
| trojan      | G2      | J-RawPost-small  | github.com::repository_view          | 0.975610 |
| trojan      | G2      | J-RawPost-small  | wikipedia.org::article_view          | 0.744186 |
| trojan      | G2      | J-RawPost-small  | youtube.com::search_results_view     | 0.878049 |
| trojan      | G2      | J-RawPost-small  | youtube.com::video_playback          | 0.842105 |
| trojan      | G2      | J-Marginal-small | bing.com::search_results_view        | 0.894737 |
| trojan      | G2      | J-Marginal-small | developer.mozilla.org::document_view | 0.820513 |
| trojan      | G2      | J-Marginal-small | github.com::repository_view          | 0.952381 |
| trojan      | G2      | J-Marginal-small | wikipedia.org::article_view          | 0.744186 |
| trojan      | G2      | J-Marginal-small | youtube.com::search_results_view     | 0.878049 |
| trojan      | G2      | J-Marginal-small | youtube.com::video_playback          | 0.864865 |
| vmess       | G0      | M-S              | bing.com::search_results_view        | 0.810811 |
| vmess       | G0      | M-S              | developer.mozilla.org::document_view | 0.666667 |
| vmess       | G0      | M-S              | github.com::repository_view          | 0.833333 |
| vmess       | G0      | M-S              | wikipedia.org::article_view          | 0.727273 |
| vmess       | G0      | M-S              | youtube.com::search_results_view     | 0.904762 |
| vmess       | G0      | M-S              | youtube.com::video_playback          | 0.974359 |
| vmess       | G0      | I-S              | bing.com::search_results_view        | 0.769231 |
| vmess       | G0      | I-S              | developer.mozilla.org::document_view | 0.619048 |
| vmess       | G0      | I-S              | github.com::repository_view          | 0.864865 |
| vmess       | G0      | I-S              | wikipedia.org::article_view          | 0.651163 |
| vmess       | G0      | I-S              | youtube.com::search_results_view     | 0.900000 |
| vmess       | G0      | I-S              | youtube.com::video_playback          | 0.974359 |
| vmess       | G0      | J-S              | bing.com::search_results_view        | 0.731707 |
| vmess       | G0      | J-S              | developer.mozilla.org::document_view | 0.666667 |
| vmess       | G0      | J-S              | github.com::repository_view          | 0.764706 |
| vmess       | G0      | J-S              | wikipedia.org::article_view          | 0.682927 |
| vmess       | G0      | J-S              | youtube.com::search_results_view     | 0.871795 |
| vmess       | G0      | J-S              | youtube.com::video_playback          | 0.950000 |
| vmess       | G0      | J-P-small        | bing.com::search_results_view        | 0.750000 |
| vmess       | G0      | J-P-small        | developer.mozilla.org::document_view | 0.695652 |
| vmess       | G0      | J-P-small        | github.com::repository_view          | 0.800000 |
| vmess       | G0      | J-P-small        | wikipedia.org::article_view          | 0.684211 |
| vmess       | G0      | J-P-small        | youtube.com::search_results_view     | 0.904762 |
| vmess       | G0      | J-P-small        | youtube.com::video_playback          | 0.974359 |
| vmess       | G0      | J-G-small        | bing.com::search_results_view        | 0.750000 |
| vmess       | G0      | J-G-small        | developer.mozilla.org::document_view | 0.695652 |
| vmess       | G0      | J-G-small        | github.com::repository_view          | 0.800000 |
| vmess       | G0      | J-G-small        | wikipedia.org::article_view          | 0.684211 |
| vmess       | G0      | J-G-small        | youtube.com::search_results_view     | 0.904762 |
| vmess       | G0      | J-G-small        | youtube.com::video_playback          | 0.974359 |
| vmess       | G0      | J-RawPre-small   | bing.com::search_results_view        | 0.750000 |
| vmess       | G0      | J-RawPre-small   | developer.mozilla.org::document_view | 0.652174 |
| vmess       | G0      | J-RawPre-small   | github.com::repository_view          | 0.727273 |
| vmess       | G0      | J-RawPre-small   | wikipedia.org::article_view          | 0.700000 |
| vmess       | G0      | J-RawPre-small   | youtube.com::search_results_view     | 0.878049 |
| vmess       | G0      | J-RawPre-small   | youtube.com::video_playback          | 0.950000 |
| vmess       | G0      | J-RawPost-small  | bing.com::search_results_view        | 0.731707 |
| vmess       | G0      | J-RawPost-small  | developer.mozilla.org::document_view | 0.666667 |
| vmess       | G0      | J-RawPost-small  | github.com::repository_view          | 0.764706 |
| vmess       | G0      | J-RawPost-small  | wikipedia.org::article_view          | 0.682927 |
| vmess       | G0      | J-RawPost-small  | youtube.com::search_results_view     | 0.871795 |
| vmess       | G0      | J-RawPost-small  | youtube.com::video_playback          | 0.950000 |
| vmess       | G0      | J-Marginal-small | bing.com::search_results_view        | 0.731707 |
| vmess       | G0      | J-Marginal-small | developer.mozilla.org::document_view | 0.695652 |
| vmess       | G0      | J-Marginal-small | github.com::repository_view          | 0.764706 |
| vmess       | G0      | J-Marginal-small | wikipedia.org::article_view          | 0.684211 |
| vmess       | G0      | J-Marginal-small | youtube.com::search_results_view     | 0.857143 |
| vmess       | G0      | J-Marginal-small | youtube.com::video_playback          | 0.974359 |
| vmess       | G1      | M-S              | bing.com::search_results_view        | 0.756757 |
| vmess       | G1      | M-S              | developer.mozilla.org::document_view | 0.727273 |
| vmess       | G1      | M-S              | github.com::repository_view          | 0.926829 |
| vmess       | G1      | M-S              | wikipedia.org::article_view          | 0.742857 |
| vmess       | G1      | M-S              | youtube.com::search_results_view     | 0.883721 |
| vmess       | G1      | M-S              | youtube.com::video_playback          | 0.950000 |
| vmess       | G1      | I-S              | bing.com::search_results_view        | 0.842105 |
| vmess       | G1      | I-S              | developer.mozilla.org::document_view | 0.744186 |
| vmess       | G1      | I-S              | github.com::repository_view          | 0.974359 |
| vmess       | G1      | I-S              | wikipedia.org::article_view          | 0.702703 |
| vmess       | G1      | I-S              | youtube.com::search_results_view     | 0.909091 |
| vmess       | G1      | I-S              | youtube.com::video_playback          | 0.974359 |
| vmess       | G1      | J-S              | bing.com::search_results_view        | 0.833333 |
| vmess       | G1      | J-S              | developer.mozilla.org::document_view | 0.739130 |
| vmess       | G1      | J-S              | github.com::repository_view          | 0.974359 |
| vmess       | G1      | J-S              | wikipedia.org::article_view          | 0.702703 |
| vmess       | G1      | J-S              | youtube.com::search_results_view     | 0.883721 |
| vmess       | G1      | J-S              | youtube.com::video_playback          | 0.974359 |
| vmess       | G1      | J-P-small        | bing.com::search_results_view        | 0.864865 |
| vmess       | G1      | J-P-small        | developer.mozilla.org::document_view | 0.727273 |
| vmess       | G1      | J-P-small        | github.com::repository_view          | 0.974359 |
| vmess       | G1      | J-P-small        | wikipedia.org::article_view          | 0.684211 |
| vmess       | G1      | J-P-small        | youtube.com::search_results_view     | 0.883721 |
| vmess       | G1      | J-P-small        | youtube.com::video_playback          | 0.974359 |
| vmess       | G1      | J-G-small        | bing.com::search_results_view        | 0.864865 |
| vmess       | G1      | J-G-small        | developer.mozilla.org::document_view | 0.755556 |
| vmess       | G1      | J-G-small        | github.com::repository_view          | 0.974359 |
| vmess       | G1      | J-G-small        | wikipedia.org::article_view          | 0.702703 |
| vmess       | G1      | J-G-small        | youtube.com::search_results_view     | 0.857143 |
| vmess       | G1      | J-G-small        | youtube.com::video_playback          | 0.950000 |
| vmess       | G1      | J-RawPre-small   | bing.com::search_results_view        | 0.833333 |
| vmess       | G1      | J-RawPre-small   | developer.mozilla.org::document_view | 0.755556 |
| vmess       | G1      | J-RawPre-small   | github.com::repository_view          | 0.950000 |
| vmess       | G1      | J-RawPre-small   | wikipedia.org::article_view          | 0.702703 |
| vmess       | G1      | J-RawPre-small   | youtube.com::search_results_view     | 0.883721 |
| vmess       | G1      | J-RawPre-small   | youtube.com::video_playback          | 0.974359 |
| vmess       | G1      | J-RawPost-small  | bing.com::search_results_view        | 0.833333 |
| vmess       | G1      | J-RawPost-small  | developer.mozilla.org::document_view | 0.739130 |
| vmess       | G1      | J-RawPost-small  | github.com::repository_view          | 0.974359 |
| vmess       | G1      | J-RawPost-small  | wikipedia.org::article_view          | 0.702703 |
| vmess       | G1      | J-RawPost-small  | youtube.com::search_results_view     | 0.883721 |
| vmess       | G1      | J-RawPost-small  | youtube.com::video_playback          | 0.974359 |
| vmess       | G1      | J-Marginal-small | bing.com::search_results_view        | 0.864865 |
| vmess       | G1      | J-Marginal-small | developer.mozilla.org::document_view | 0.727273 |
| vmess       | G1      | J-Marginal-small | github.com::repository_view          | 0.974359 |
| vmess       | G1      | J-Marginal-small | wikipedia.org::article_view          | 0.684211 |
| vmess       | G1      | J-Marginal-small | youtube.com::search_results_view     | 0.857143 |
| vmess       | G1      | J-Marginal-small | youtube.com::video_playback          | 0.950000 |
| vmess       | G2      | M-S              | bing.com::search_results_view        | 0.750000 |
| vmess       | G2      | M-S              | developer.mozilla.org::document_view | 0.400000 |
| vmess       | G2      | M-S              | github.com::repository_view          | 0.904762 |
| vmess       | G2      | M-S              | wikipedia.org::article_view          | 0.723404 |
| vmess       | G2      | M-S              | youtube.com::search_results_view     | 0.883721 |
| vmess       | G2      | M-S              | youtube.com::video_playback          | 0.947368 |
| vmess       | G2      | I-S              | bing.com::search_results_view        | 0.769231 |
| vmess       | G2      | I-S              | developer.mozilla.org::document_view | 0.437500 |
| vmess       | G2      | I-S              | github.com::repository_view          | 0.950000 |
| vmess       | G2      | I-S              | wikipedia.org::article_view          | 0.595745 |
| vmess       | G2      | I-S              | youtube.com::search_results_view     | 0.930233 |
| vmess       | G2      | I-S              | youtube.com::video_playback          | 0.974359 |
| vmess       | G2      | J-S              | bing.com::search_results_view        | 0.731707 |
| vmess       | G2      | J-S              | developer.mozilla.org::document_view | 0.437500 |
| vmess       | G2      | J-S              | github.com::repository_view          | 0.926829 |
| vmess       | G2      | J-S              | wikipedia.org::article_view          | 0.608696 |
| vmess       | G2      | J-S              | youtube.com::search_results_view     | 0.926829 |
| vmess       | G2      | J-S              | youtube.com::video_playback          | 0.974359 |
| vmess       | G2      | J-P-small        | bing.com::search_results_view        | 0.731707 |
| vmess       | G2      | J-P-small        | developer.mozilla.org::document_view | 0.484848 |
| vmess       | G2      | J-P-small        | github.com::repository_view          | 0.950000 |
| vmess       | G2      | J-P-small        | wikipedia.org::article_view          | 0.608696 |
| vmess       | G2      | J-P-small        | youtube.com::search_results_view     | 0.926829 |
| vmess       | G2      | J-P-small        | youtube.com::video_playback          | 0.974359 |
| vmess       | G2      | J-G-small        | bing.com::search_results_view        | 0.731707 |
| vmess       | G2      | J-G-small        | developer.mozilla.org::document_view | 0.484848 |
| vmess       | G2      | J-G-small        | github.com::repository_view          | 0.950000 |
| vmess       | G2      | J-G-small        | wikipedia.org::article_view          | 0.608696 |
| vmess       | G2      | J-G-small        | youtube.com::search_results_view     | 0.926829 |
| vmess       | G2      | J-G-small        | youtube.com::video_playback          | 0.974359 |
| vmess       | G2      | J-RawPre-small   | bing.com::search_results_view        | 0.731707 |
| vmess       | G2      | J-RawPre-small   | developer.mozilla.org::document_view | 0.437500 |
| vmess       | G2      | J-RawPre-small   | github.com::repository_view          | 0.926829 |
| vmess       | G2      | J-RawPre-small   | wikipedia.org::article_view          | 0.608696 |
| vmess       | G2      | J-RawPre-small   | youtube.com::search_results_view     | 0.926829 |
| vmess       | G2      | J-RawPre-small   | youtube.com::video_playback          | 0.974359 |
| vmess       | G2      | J-RawPost-small  | bing.com::search_results_view        | 0.731707 |
| vmess       | G2      | J-RawPost-small  | developer.mozilla.org::document_view | 0.437500 |
| vmess       | G2      | J-RawPost-small  | github.com::repository_view          | 0.926829 |
| vmess       | G2      | J-RawPost-small  | wikipedia.org::article_view          | 0.608696 |
| vmess       | G2      | J-RawPost-small  | youtube.com::search_results_view     | 0.926829 |
| vmess       | G2      | J-RawPost-small  | youtube.com::video_playback          | 0.974359 |
| vmess       | G2      | J-Marginal-small | bing.com::search_results_view        | 0.750000 |
| vmess       | G2      | J-Marginal-small | developer.mozilla.org::document_view | 0.484848 |
| vmess       | G2      | J-Marginal-small | github.com::repository_view          | 0.950000 |
| vmess       | G2      | J-Marginal-small | wikipedia.org::article_view          | 0.638298 |
| vmess       | G2      | J-Marginal-small | youtube.com::search_results_view     | 0.926829 |
| vmess       | G2      | J-Marginal-small | youtube.com::video_playback          | 0.974359 |

## 所有接受分类拟合

| role_id                      | arm              |   parameters |   dimensions |   seconds |   iterations |   max_gradient |
|:-----------------------------|:-----------------|-------------:|-------------:|----------:|-------------:|---------------:|
| main/f0/shadowsocks/G0/outer | I-S              |          978 |          162 |  0.774092 |           62 |    8.75553e-06 |
| main/f0/shadowsocks/G0/outer | J-G-small        |          978 |          162 |  0.50629  |           47 |    8.73342e-06 |
| main/f0/shadowsocks/G0/outer | J-Marginal-small |          978 |          162 |  0.514736 |           48 |    9.24842e-06 |
| main/f0/shadowsocks/G0/outer | J-P-small        |          978 |          162 |  0.524105 |           47 |    7.72578e-06 |
| main/f0/shadowsocks/G0/outer | J-RawPost-small  |          978 |          162 |  0.508096 |           47 |    8.85818e-06 |
| main/f0/shadowsocks/G0/outer | J-RawPre-small   |          978 |          162 |  0.722661 |           59 |    9.1691e-06  |
| main/f0/shadowsocks/G0/outer | J-S              |          978 |          162 |  0.479607 |           46 |    9.2046e-06  |
| main/f0/shadowsocks/G0/outer | M-S              |          582 |           96 |  0.412089 |           44 |    7.30727e-06 |
| main/f0/shadowsocks/G1/outer | I-S              |          978 |          162 |  0.719489 |           62 |    8.94223e-06 |
| main/f0/shadowsocks/G1/outer | J-G-small        |          978 |          162 |  0.537723 |           48 |    9.65192e-06 |
| main/f0/shadowsocks/G1/outer | J-Marginal-small |          978 |          162 |  0.543154 |           51 |    8.93389e-06 |
| main/f0/shadowsocks/G1/outer | J-P-small        |          978 |          162 |  0.549583 |           52 |    7.53792e-06 |
| main/f0/shadowsocks/G1/outer | J-RawPost-small  |          978 |          162 |  0.635631 |           56 |    9.70759e-06 |
| main/f0/shadowsocks/G1/outer | J-RawPre-small   |          978 |          162 |  0.833893 |           67 |    9.98947e-06 |
| main/f0/shadowsocks/G1/outer | J-S              |          978 |          162 |  0.614084 |           55 |    9.55984e-06 |
| main/f0/shadowsocks/G1/outer | M-S              |          582 |           96 |  0.566173 |           56 |    9.34058e-06 |
| main/f0/shadowsocks/G2/outer | I-S              |          978 |          162 |  0.721603 |           63 |    9.81572e-06 |
| main/f0/shadowsocks/G2/outer | J-G-small        |          978 |          162 |  0.502982 |           49 |    9.83935e-06 |
| main/f0/shadowsocks/G2/outer | J-Marginal-small |          978 |          162 |  0.520222 |           45 |    9.51359e-06 |
| main/f0/shadowsocks/G2/outer | J-P-small        |          978 |          162 |  0.532744 |           51 |    7.53482e-06 |
| main/f0/shadowsocks/G2/outer | J-RawPost-small  |          978 |          162 |  0.50622  |           48 |    9.56218e-06 |
| main/f0/shadowsocks/G2/outer | J-RawPre-small   |          978 |          162 |  0.749752 |           63 |    9.76378e-06 |
| main/f0/shadowsocks/G2/outer | J-S              |          978 |          162 |  0.49273  |           49 |    8.4753e-06  |
| main/f0/shadowsocks/G2/outer | M-S              |          582 |           96 |  0.373357 |           42 |    9.30841e-06 |
| main/f0/trojan/G0/outer      | I-S              |          978 |          162 |  0.502991 |           46 |    9.92737e-06 |
| main/f0/trojan/G0/outer      | J-G-small        |          978 |          162 |  0.438171 |           43 |    9.36486e-06 |
| main/f0/trojan/G0/outer      | J-Marginal-small |          978 |          162 |  0.454901 |           44 |    7.80362e-06 |
| main/f0/trojan/G0/outer      | J-P-small        |          978 |          162 |  0.502093 |           46 |    9.84322e-06 |
| main/f0/trojan/G0/outer      | J-RawPost-small  |          978 |          162 |  0.444553 |           44 |    8.59265e-06 |
| main/f0/trojan/G0/outer      | J-RawPre-small   |          978 |          162 |  0.552079 |           51 |    9.88489e-06 |
| main/f0/trojan/G0/outer      | J-S              |          978 |          162 |  0.476784 |           44 |    7.9997e-06  |
| main/f0/trojan/G0/outer      | M-S              |          582 |           96 |  0.368162 |           41 |    8.21695e-06 |
| main/f0/trojan/G1/outer      | I-S              |          978 |          162 |  0.410061 |           59 |    9.27529e-06 |
| main/f0/trojan/G1/outer      | J-G-small        |          978 |          162 |  0.404138 |           46 |    9.1697e-06  |
| main/f0/trojan/G1/outer      | J-Marginal-small |          978 |          162 |  0.483279 |           50 |    8.58699e-06 |
| main/f0/trojan/G1/outer      | J-P-small        |          978 |          162 |  0.430955 |           49 |    7.87504e-06 |
| main/f0/trojan/G1/outer      | J-RawPost-small  |          978 |          162 |  0.468133 |           48 |    6.62994e-06 |
| main/f0/trojan/G1/outer      | J-RawPre-small   |          978 |          162 |  0.644015 |           60 |    9.78486e-06 |
| main/f0/trojan/G1/outer      | J-S              |          978 |          162 |  0.385053 |           47 |    8.5757e-06  |
| main/f0/trojan/G1/outer      | M-S              |          582 |           96 |  0.266353 |           44 |    9.75078e-06 |
| main/f0/trojan/G2/outer      | I-S              |          978 |          162 |  0.468588 |           49 |    9.88018e-06 |
| main/f0/trojan/G2/outer      | J-G-small        |          978 |          162 |  0.488249 |           47 |    9.29928e-06 |
| main/f0/trojan/G2/outer      | J-Marginal-small |          978 |          162 |  0.423272 |           44 |    9.8953e-06  |
| main/f0/trojan/G2/outer      | J-P-small        |          978 |          162 |  0.487072 |           47 |    8.9747e-06  |
| main/f0/trojan/G2/outer      | J-RawPost-small  |          978 |          162 |  0.474169 |           47 |    7.86252e-06 |
| main/f0/trojan/G2/outer      | J-RawPre-small   |          978 |          162 |  0.606153 |           56 |    9.33347e-06 |
| main/f0/trojan/G2/outer      | J-S              |          978 |          162 |  0.454025 |           47 |    8.89434e-06 |
| main/f0/trojan/G2/outer      | M-S              |          582 |           96 |  0.31598  |           39 |    7.38984e-06 |
| main/f0/vless/G0/outer       | I-S              |          978 |          162 |  0.415318 |           44 |    9.81218e-06 |
| main/f0/vless/G0/outer       | J-G-small        |          978 |          162 |  0.347409 |           38 |    8.95838e-06 |
| main/f0/vless/G0/outer       | J-Marginal-small |          978 |          162 |  0.355808 |           39 |    8.74531e-06 |
| main/f0/vless/G0/outer       | J-P-small        |          978 |          162 |  0.374709 |           40 |    6.29661e-06 |
| main/f0/vless/G0/outer       | J-RawPost-small  |          978 |          162 |  0.367445 |           40 |    9.62179e-06 |
| main/f0/vless/G0/outer       | J-RawPre-small   |          978 |          162 |  0.56001  |           52 |    7.9616e-06  |
| main/f0/vless/G0/outer       | J-S              |          978 |          162 |  0.390125 |           41 |    7.83324e-06 |
| main/f0/vless/G0/outer       | M-S              |          582 |           96 |  0.313312 |           38 |    9.99787e-06 |
| main/f0/vless/G1/outer       | I-S              |          978 |          162 |  0.708545 |           62 |    8.98073e-06 |
| main/f0/vless/G1/outer       | J-G-small        |          978 |          162 |  0.541489 |           51 |    9.50771e-06 |
| main/f0/vless/G1/outer       | J-Marginal-small |          978 |          162 |  0.586569 |           55 |    8.46421e-06 |
| main/f0/vless/G1/outer       | J-P-small        |          978 |          162 |  0.638715 |           58 |    9.31428e-06 |
| main/f0/vless/G1/outer       | J-RawPost-small  |          978 |          162 |  0.491683 |           49 |    9.8597e-06  |
| main/f0/vless/G1/outer       | J-RawPre-small   |          978 |          162 |  0.773167 |           64 |    9.96541e-06 |
| main/f0/vless/G1/outer       | J-S              |          978 |          162 |  0.511978 |           51 |    9.19851e-06 |
| main/f0/vless/G1/outer       | M-S              |          582 |           96 |  0.41315  |           45 |    9.58696e-06 |
| main/f0/vless/G2/outer       | I-S              |          978 |          162 |  0.386576 |           38 |    9.45846e-06 |
| main/f0/vless/G2/outer       | J-G-small        |          978 |          162 |  0.299739 |           34 |    9.12406e-06 |
| main/f0/vless/G2/outer       | J-Marginal-small |          978 |          162 |  0.324089 |           36 |    7.81891e-06 |
| main/f0/vless/G2/outer       | J-P-small        |          978 |          162 |  0.318807 |           35 |    8.52254e-06 |
| main/f0/vless/G2/outer       | J-RawPost-small  |          978 |          162 |  0.318241 |           36 |    8.39067e-06 |
| main/f0/vless/G2/outer       | J-RawPre-small   |          978 |          162 |  0.524775 |           51 |    5.39e-06    |
| main/f0/vless/G2/outer       | J-S              |          978 |          162 |  0.33247  |           36 |    8.82645e-06 |
| main/f0/vless/G2/outer       | M-S              |          582 |           96 |  0.305545 |           33 |    9.73261e-06 |
| main/f0/vmess/G0/outer       | I-S              |          978 |          162 |  0.536682 |           49 |    8.90631e-06 |
| main/f0/vmess/G0/outer       | J-G-small        |          978 |          162 |  0.579846 |           53 |    9.2381e-06  |
| main/f0/vmess/G0/outer       | J-Marginal-small |          978 |          162 |  0.508238 |           49 |    9.16166e-06 |
| main/f0/vmess/G0/outer       | J-P-small        |          978 |          162 |  0.538006 |           51 |    9.42006e-06 |
| main/f0/vmess/G0/outer       | J-RawPost-small  |          978 |          162 |  0.549116 |           51 |    7.47638e-06 |
| main/f0/vmess/G0/outer       | J-RawPre-small   |          978 |          162 |  0.732339 |           62 |    3.77726e-06 |
| main/f0/vmess/G0/outer       | J-S              |          978 |          162 |  0.547904 |           50 |    9.59132e-06 |
| main/f0/vmess/G0/outer       | M-S              |          582 |           96 |  0.439162 |           45 |    7.85384e-06 |
| main/f0/vmess/G1/outer       | I-S              |          978 |          162 |  0.628879 |           55 |    9.6283e-06  |
| main/f0/vmess/G1/outer       | J-G-small        |          978 |          162 |  0.543367 |           51 |    8.57216e-06 |
| main/f0/vmess/G1/outer       | J-Marginal-small |          978 |          162 |  0.516607 |           49 |    9.50551e-06 |
| main/f0/vmess/G1/outer       | J-P-small        |          978 |          162 |  0.485929 |           48 |    8.84112e-06 |
| main/f0/vmess/G1/outer       | J-RawPost-small  |          978 |          162 |  0.509718 |           49 |    9.59471e-06 |
| main/f0/vmess/G1/outer       | J-RawPre-small   |          978 |          162 |  0.653753 |           57 |    9.34198e-06 |
| main/f0/vmess/G1/outer       | J-S              |          978 |          162 |  0.543078 |           50 |    9.16771e-06 |
| main/f0/vmess/G1/outer       | M-S              |          582 |           96 |  0.384876 |           42 |    8.03131e-06 |
| main/f0/vmess/G2/outer       | I-S              |          978 |          162 |  0.584071 |           55 |    6.25003e-06 |
| main/f0/vmess/G2/outer       | J-G-small        |          978 |          162 |  0.593278 |           54 |    9.89354e-06 |
| main/f0/vmess/G2/outer       | J-Marginal-small |          978 |          162 |  0.6695   |           59 |    9.2197e-06  |
| main/f0/vmess/G2/outer       | J-P-small        |          978 |          162 |  0.626971 |           56 |    9.94524e-06 |
| main/f0/vmess/G2/outer       | J-RawPost-small  |          978 |          162 |  0.629464 |           56 |    9.85742e-06 |
| main/f0/vmess/G2/outer       | J-RawPre-small   |          978 |          162 |  0.89851  |           70 |    9.86352e-06 |
| main/f0/vmess/G2/outer       | J-S              |          978 |          162 |  0.632443 |           56 |    9.61141e-06 |
| main/f0/vmess/G2/outer       | M-S              |          582 |           96 |  0.34981  |           42 |    9.4675e-06  |
| main/f1/shadowsocks/G0/outer | I-S              |          978 |          162 |  0.715808 |           63 |    9.2222e-06  |
| main/f1/shadowsocks/G0/outer | J-G-small        |          978 |          162 |  0.516951 |           49 |    8.79355e-06 |
| main/f1/shadowsocks/G0/outer | J-Marginal-small |          978 |          162 |  0.457733 |           47 |    8.19261e-06 |
| main/f1/shadowsocks/G0/outer | J-P-small        |          978 |          162 |  0.486966 |           48 |    9.3193e-06  |
| main/f1/shadowsocks/G0/outer | J-RawPost-small  |          978 |          162 |  0.45297  |           46 |    9.14807e-06 |
| main/f1/shadowsocks/G0/outer | J-RawPre-small   |          978 |          162 |  0.748844 |           63 |    8.37552e-06 |
| main/f1/shadowsocks/G0/outer | J-S              |          978 |          162 |  0.465363 |           46 |    9.408e-06   |
| main/f1/shadowsocks/G0/outer | M-S              |          582 |           96 |  0.346376 |           40 |    9.94423e-06 |
| main/f1/shadowsocks/G1/outer | I-S              |          978 |          162 |  0.434556 |           46 |    8.43043e-06 |
| main/f1/shadowsocks/G1/outer | J-G-small        |          978 |          162 |  0.436257 |           45 |    8.73245e-06 |
| main/f1/shadowsocks/G1/outer | J-Marginal-small |          978 |          162 |  0.464451 |           46 |    6.29373e-06 |
| main/f1/shadowsocks/G1/outer | J-P-small        |          978 |          162 |  0.445576 |           45 |    7.72907e-06 |
| main/f1/shadowsocks/G1/outer | J-RawPost-small  |          978 |          162 |  0.477688 |           46 |    8.13439e-06 |
| main/f1/shadowsocks/G1/outer | J-RawPre-small   |          978 |          162 |  0.726425 |           62 |    6.4007e-06  |
| main/f1/shadowsocks/G1/outer | J-S              |          978 |          162 |  0.459108 |           46 |    8.82468e-06 |
| main/f1/shadowsocks/G1/outer | M-S              |          582 |           96 |  0.346284 |           41 |    6.37854e-06 |
| main/f1/shadowsocks/G2/outer | I-S              |          978 |          162 |  0.47903  |           48 |    9.74665e-06 |
| main/f1/shadowsocks/G2/outer | J-G-small        |          978 |          162 |  0.56516  |           46 |    8.86647e-06 |
| main/f1/shadowsocks/G2/outer | J-Marginal-small |          978 |          162 |  0.484638 |           47 |    9.85126e-06 |
| main/f1/shadowsocks/G2/outer | J-P-small        |          978 |          162 |  0.482628 |           47 |    9.37032e-06 |
| main/f1/shadowsocks/G2/outer | J-RawPost-small  |          978 |          162 |  0.462776 |           46 |    9.7655e-06  |
| main/f1/shadowsocks/G2/outer | J-RawPre-small   |          978 |          162 |  0.651152 |           57 |    7.66108e-06 |
| main/f1/shadowsocks/G2/outer | J-S              |          978 |          162 |  0.458555 |           46 |    9.70407e-06 |
| main/f1/shadowsocks/G2/outer | M-S              |          582 |           96 |  0.32933  |           40 |    9.13292e-06 |
| main/f1/trojan/G0/outer      | I-S              |          978 |          162 |  0.44571  |           45 |    9.65293e-06 |
| main/f1/trojan/G0/outer      | J-G-small        |          978 |          162 |  0.415845 |           42 |    9.4478e-06  |
| main/f1/trojan/G0/outer      | J-Marginal-small |          978 |          162 |  0.42808  |           44 |    7.77516e-06 |
| main/f1/trojan/G0/outer      | J-P-small        |          978 |          162 |  0.410703 |           42 |    9.78882e-06 |
| main/f1/trojan/G0/outer      | J-RawPost-small  |          978 |          162 |  0.405496 |           42 |    7.49333e-06 |
| main/f1/trojan/G0/outer      | J-RawPre-small   |          978 |          162 |  0.539778 |           52 |    9.70464e-06 |
| main/f1/trojan/G0/outer      | J-S              |          978 |          162 |  0.394103 |           42 |    8.7854e-06  |
| main/f1/trojan/G0/outer      | M-S              |          582 |           96 |  0.318135 |           37 |    7.54175e-06 |
| main/f1/trojan/G1/outer      | I-S              |          978 |          162 |  0.760278 |           60 |    9.05024e-06 |
| main/f1/trojan/G1/outer      | J-G-small        |          978 |          162 |  0.480533 |           47 |    6.86456e-06 |
| main/f1/trojan/G1/outer      | J-Marginal-small |          978 |          162 |  0.476998 |           48 |    8.87176e-06 |
| main/f1/trojan/G1/outer      | J-P-small        |          978 |          162 |  0.472888 |           46 |    7.86471e-06 |
| main/f1/trojan/G1/outer      | J-RawPost-small  |          978 |          162 |  0.46683  |           47 |    8.92168e-06 |
| main/f1/trojan/G1/outer      | J-RawPre-small   |          978 |          162 |  0.728746 |           63 |    9.88582e-06 |
| main/f1/trojan/G1/outer      | J-S              |          978 |          162 |  0.511783 |           47 |    9.54576e-06 |
| main/f1/trojan/G1/outer      | M-S              |          582 |           96 |  0.430796 |           43 |    9.68829e-06 |
| main/f1/trojan/G2/outer      | I-S              |          978 |          162 |  0.47544  |           45 |    7.80771e-06 |
| main/f1/trojan/G2/outer      | J-G-small        |          978 |          162 |  0.377293 |           39 |    9.56936e-06 |
| main/f1/trojan/G2/outer      | J-Marginal-small |          978 |          162 |  0.430903 |           42 |    9.46004e-06 |
| main/f1/trojan/G2/outer      | J-P-small        |          978 |          162 |  0.428854 |           43 |    9.78719e-06 |
| main/f1/trojan/G2/outer      | J-RawPost-small  |          978 |          162 |  0.429528 |           42 |    9.36508e-06 |
| main/f1/trojan/G2/outer      | J-RawPre-small   |          978 |          162 |  0.65112  |           57 |    8.54511e-06 |
| main/f1/trojan/G2/outer      | J-S              |          978 |          162 |  0.419994 |           42 |    9.15973e-06 |
| main/f1/trojan/G2/outer      | M-S              |          582 |           96 |  0.318711 |           35 |    9.35777e-06 |
| main/f1/vless/G0/outer       | I-S              |          978 |          162 |  0.644358 |           48 |    9.35656e-06 |
| main/f1/vless/G0/outer       | J-G-small        |          978 |          162 |  0.401717 |           40 |    8.22266e-06 |
| main/f1/vless/G0/outer       | J-Marginal-small |          978 |          162 |  0.423543 |           42 |    9.02251e-06 |
| main/f1/vless/G0/outer       | J-P-small        |          978 |          162 |  0.462089 |           43 |    9.17711e-06 |
| main/f1/vless/G0/outer       | J-RawPost-small  |          978 |          162 |  0.432432 |           43 |    8.42779e-06 |
| main/f1/vless/G0/outer       | J-RawPre-small   |          978 |          162 |  0.630105 |           55 |    7.1444e-06  |
| main/f1/vless/G0/outer       | J-S              |          978 |          162 |  0.477703 |           43 |    9.10694e-06 |
| main/f1/vless/G0/outer       | M-S              |          582 |           96 |  0.501982 |           40 |    9.21606e-06 |
| main/f1/vless/G1/outer       | I-S              |          978 |          162 |  0.669859 |           56 |    9.49058e-06 |
| main/f1/vless/G1/outer       | J-G-small        |          978 |          162 |  0.493913 |           46 |    8.81948e-06 |
| main/f1/vless/G1/outer       | J-Marginal-small |          978 |          162 |  0.481052 |           48 |    7.55626e-06 |
| main/f1/vless/G1/outer       | J-P-small        |          978 |          162 |  0.496797 |           47 |    9.49516e-06 |
| main/f1/vless/G1/outer       | J-RawPost-small  |          978 |          162 |  0.426803 |           44 |    8.37555e-06 |
| main/f1/vless/G1/outer       | J-RawPre-small   |          978 |          162 |  0.759108 |           63 |    7.22046e-06 |
| main/f1/vless/G1/outer       | J-S              |          978 |          162 |  0.457846 |           44 |    8.02164e-06 |
| main/f1/vless/G1/outer       | M-S              |          582 |           96 |  0.421772 |           43 |    9.08821e-06 |
| main/f1/vless/G2/outer       | I-S              |          978 |          162 |  0.408329 |           42 |    7.03257e-06 |
| main/f1/vless/G2/outer       | J-G-small        |          978 |          162 |  0.342053 |           37 |    7.6085e-06  |
| main/f1/vless/G2/outer       | J-Marginal-small |          978 |          162 |  0.308215 |           35 |    9.95498e-06 |
| main/f1/vless/G2/outer       | J-P-small        |          978 |          162 |  0.335446 |           36 |    7.44264e-06 |
| main/f1/vless/G2/outer       | J-RawPost-small  |          978 |          162 |  0.351587 |           38 |    7.72158e-06 |
| main/f1/vless/G2/outer       | J-RawPre-small   |          978 |          162 |  0.455493 |           46 |    9.53999e-06 |
| main/f1/vless/G2/outer       | J-S              |          978 |          162 |  0.3424   |           37 |    9.90228e-06 |
| main/f1/vless/G2/outer       | M-S              |          582 |           96 |  0.301075 |           36 |    5.71699e-06 |
| main/f1/vmess/G0/outer       | I-S              |          978 |          162 |  0.399725 |           45 |    9.87078e-06 |
| main/f1/vmess/G0/outer       | J-G-small        |          978 |          162 |  0.487003 |           48 |    4.84309e-06 |
| main/f1/vmess/G0/outer       | J-Marginal-small |          978 |          162 |  0.376441 |           42 |    8.9503e-06  |
| main/f1/vmess/G0/outer       | J-P-small        |          978 |          162 |  0.443872 |           46 |    8.91835e-06 |
| main/f1/vmess/G0/outer       | J-RawPost-small  |          978 |          162 |  0.400636 |           43 |    9.42473e-06 |
| main/f1/vmess/G0/outer       | J-RawPre-small   |          978 |          162 |  0.538195 |           53 |    7.25946e-06 |
| main/f1/vmess/G0/outer       | J-S              |          978 |          162 |  0.37808  |           42 |    9.72726e-06 |
| main/f1/vmess/G0/outer       | M-S              |          582 |           96 |  0.303395 |           38 |    9.61981e-06 |
| main/f1/vmess/G1/outer       | I-S              |          978 |          162 |  0.556475 |           54 |    9.23947e-06 |
| main/f1/vmess/G1/outer       | J-G-small        |          978 |          162 |  0.421827 |           44 |    9.19643e-06 |
| main/f1/vmess/G1/outer       | J-Marginal-small |          978 |          162 |  0.458922 |           46 |    8.36054e-06 |
| main/f1/vmess/G1/outer       | J-P-small        |          978 |          162 |  0.458008 |           46 |    7.31492e-06 |
| main/f1/vmess/G1/outer       | J-RawPost-small  |          978 |          162 |  0.433301 |           45 |    9.76474e-06 |
| main/f1/vmess/G1/outer       | J-RawPre-small   |          978 |          162 |  0.728996 |           64 |    6.2971e-06  |
| main/f1/vmess/G1/outer       | J-S              |          978 |          162 |  0.431905 |           45 |    8.91557e-06 |
| main/f1/vmess/G1/outer       | M-S              |          582 |           96 |  0.343612 |           40 |    9.83743e-06 |
| main/f1/vmess/G2/outer       | I-S              |          978 |          162 |  0.576405 |           52 |    8.43941e-06 |
| main/f1/vmess/G2/outer       | J-G-small        |          978 |          162 |  0.509285 |           48 |    9.56631e-06 |
| main/f1/vmess/G2/outer       | J-Marginal-small |          978 |          162 |  0.553615 |           54 |    9.87058e-06 |
| main/f1/vmess/G2/outer       | J-P-small        |          978 |          162 |  0.490889 |           48 |    9.44516e-06 |
| main/f1/vmess/G2/outer       | J-RawPost-small  |          978 |          162 |  0.48564  |           49 |    9.54535e-06 |
| main/f1/vmess/G2/outer       | J-RawPre-small   |          978 |          162 |  0.937238 |           71 |    4.93874e-06 |
| main/f1/vmess/G2/outer       | J-S              |          978 |          162 |  0.521354 |           50 |    8.85413e-06 |
| main/f1/vmess/G2/outer       | M-S              |          582 |           96 |  0.315226 |           37 |    8.99571e-06 |
| main/f2/shadowsocks/G0/outer | I-S              |          978 |          162 |  0.658042 |           59 |    9.31882e-06 |
| main/f2/shadowsocks/G0/outer | J-G-small        |          978 |          162 |  0.464255 |           47 |    9.41453e-06 |
| main/f2/shadowsocks/G0/outer | J-Marginal-small |          978 |          162 |  0.511058 |           50 |    8.35199e-06 |
| main/f2/shadowsocks/G0/outer | J-P-small        |          978 |          162 |  0.456858 |           46 |    9.7051e-06  |
| main/f2/shadowsocks/G0/outer | J-RawPost-small  |          978 |          162 |  0.440032 |           44 |    9.27013e-06 |
| main/f2/shadowsocks/G0/outer | J-RawPre-small   |          978 |          162 |  0.654652 |           58 |    8.83464e-06 |
| main/f2/shadowsocks/G0/outer | J-S              |          978 |          162 |  0.435421 |           45 |    9.92734e-06 |
| main/f2/shadowsocks/G0/outer | M-S              |          582 |           96 |  0.458729 |           47 |    9.64306e-06 |
| main/f2/shadowsocks/G1/outer | I-S              |          978 |          162 |  0.476288 |           48 |    8.58356e-06 |
| main/f2/shadowsocks/G1/outer | J-G-small        |          978 |          162 |  0.479747 |           48 |    8.8231e-06  |
| main/f2/shadowsocks/G1/outer | J-Marginal-small |          978 |          162 |  0.482656 |           47 |    9.533e-06   |
| main/f2/shadowsocks/G1/outer | J-P-small        |          978 |          162 |  0.462975 |           47 |    9.5173e-06  |
| main/f2/shadowsocks/G1/outer | J-RawPost-small  |          978 |          162 |  0.455115 |           46 |    8.14342e-06 |
| main/f2/shadowsocks/G1/outer | J-RawPre-small   |          978 |          162 |  0.688445 |           60 |    7.60015e-06 |
| main/f2/shadowsocks/G1/outer | J-S              |          978 |          162 |  0.451577 |           46 |    9.11035e-06 |
| main/f2/shadowsocks/G1/outer | M-S              |          582 |           96 |  0.354219 |           41 |    9.39759e-06 |
| main/f2/shadowsocks/G2/outer | I-S              |          978 |          162 |  0.566795 |           50 |    8.36993e-06 |
| main/f2/shadowsocks/G2/outer | J-G-small        |          978 |          162 |  0.395373 |           41 |    9.95311e-06 |
| main/f2/shadowsocks/G2/outer | J-Marginal-small |          978 |          162 |  0.398978 |           43 |    9.91236e-06 |
| main/f2/shadowsocks/G2/outer | J-P-small        |          978 |          162 |  0.416575 |           42 |    8.73894e-06 |
| main/f2/shadowsocks/G2/outer | J-RawPost-small  |          978 |          162 |  0.445776 |           46 |    8.67066e-06 |
| main/f2/shadowsocks/G2/outer | J-RawPre-small   |          978 |          162 |  0.645233 |           58 |    7.94804e-06 |
| main/f2/shadowsocks/G2/outer | J-S              |          978 |          162 |  0.486854 |           45 |    9.15433e-06 |
| main/f2/shadowsocks/G2/outer | M-S              |          582 |           96 |  0.491407 |           43 |    9.60363e-06 |
| main/f2/trojan/G0/outer      | I-S              |          978 |          162 |  0.525287 |           48 |    9.18381e-06 |
| main/f2/trojan/G0/outer      | J-G-small        |          978 |          162 |  0.426307 |           43 |    6.80897e-06 |
| main/f2/trojan/G0/outer      | J-Marginal-small |          978 |          162 |  0.378897 |           40 |    8.51054e-06 |
| main/f2/trojan/G0/outer      | J-P-small        |          978 |          162 |  0.398981 |           41 |    9.2578e-06  |
| main/f2/trojan/G0/outer      | J-RawPost-small  |          978 |          162 |  0.381473 |           40 |    9.9513e-06  |
| main/f2/trojan/G0/outer      | J-RawPre-small   |          978 |          162 |  0.739901 |           62 |    8.83716e-06 |
| main/f2/trojan/G0/outer      | J-S              |          978 |          162 |  0.389975 |           40 |    9.71148e-06 |
| main/f2/trojan/G0/outer      | M-S              |          582 |           96 |  0.376539 |           40 |    9.01669e-06 |
| main/f2/trojan/G1/outer      | I-S              |          978 |          162 |  0.501324 |           50 |    9.66169e-06 |
| main/f2/trojan/G1/outer      | J-G-small        |          978 |          162 |  0.486302 |           46 |    8.42534e-06 |
| main/f2/trojan/G1/outer      | J-Marginal-small |          978 |          162 |  0.472325 |           46 |    8.72079e-06 |
| main/f2/trojan/G1/outer      | J-P-small        |          978 |          162 |  0.459935 |           45 |    9.13079e-06 |
| main/f2/trojan/G1/outer      | J-RawPost-small  |          978 |          162 |  0.475915 |           46 |    8.87773e-06 |
| main/f2/trojan/G1/outer      | J-RawPre-small   |          978 |          162 |  0.671147 |           58 |    8.70777e-06 |
| main/f2/trojan/G1/outer      | J-S              |          978 |          162 |  0.460131 |           47 |    8.74796e-06 |
| main/f2/trojan/G1/outer      | M-S              |          582 |           96 |  0.35221  |           42 |    8.32052e-06 |
| main/f2/trojan/G2/outer      | I-S              |          978 |          162 |  0.485772 |           45 |    8.29803e-06 |
| main/f2/trojan/G2/outer      | J-G-small        |          978 |          162 |  0.515578 |           48 |    9.82609e-06 |
| main/f2/trojan/G2/outer      | J-Marginal-small |          978 |          162 |  0.420609 |           44 |    9.73958e-06 |
| main/f2/trojan/G2/outer      | J-P-small        |          978 |          162 |  0.497989 |           47 |    9.08526e-06 |
| main/f2/trojan/G2/outer      | J-RawPost-small  |          978 |          162 |  0.460258 |           47 |    8.95187e-06 |
| main/f2/trojan/G2/outer      | J-RawPre-small   |          978 |          162 |  0.721131 |           61 |    6.85674e-06 |
| main/f2/trojan/G2/outer      | J-S              |          978 |          162 |  0.474512 |           46 |    7.59136e-06 |
| main/f2/trojan/G2/outer      | M-S              |          582 |           96 |  0.352187 |           37 |    7.09548e-06 |
| main/f2/vless/G0/outer       | I-S              |          978 |          162 |  0.551616 |           49 |    9.3802e-06  |
| main/f2/vless/G0/outer       | J-G-small        |          978 |          162 |  0.389848 |           38 |    9.19326e-06 |
| main/f2/vless/G0/outer       | J-Marginal-small |          978 |          162 |  0.357079 |           38 |    8.82997e-06 |
| main/f2/vless/G0/outer       | J-P-small        |          978 |          162 |  0.405692 |           39 |    8.32529e-06 |
| main/f2/vless/G0/outer       | J-RawPost-small  |          978 |          162 |  0.409115 |           41 |    9.01076e-06 |
| main/f2/vless/G0/outer       | J-RawPre-small   |          978 |          162 |  0.677952 |           56 |    8.69915e-06 |
| main/f2/vless/G0/outer       | J-S              |          978 |          162 |  0.441006 |           41 |    8.90836e-06 |
| main/f2/vless/G0/outer       | M-S              |          582 |           96 |  0.321563 |           37 |    7.75606e-06 |
| main/f2/vless/G1/outer       | I-S              |          978 |          162 |  0.53722  |           51 |    9.13497e-06 |
| main/f2/vless/G1/outer       | J-G-small        |          978 |          162 |  0.443359 |           43 |    9.37692e-06 |
| main/f2/vless/G1/outer       | J-Marginal-small |          978 |          162 |  0.429833 |           44 |    8.55881e-06 |
| main/f2/vless/G1/outer       | J-P-small        |          978 |          162 |  0.455063 |           45 |    8.07418e-06 |
| main/f2/vless/G1/outer       | J-RawPost-small  |          978 |          162 |  0.443822 |           44 |    9.86849e-06 |
| main/f2/vless/G1/outer       | J-RawPre-small   |          978 |          162 |  0.717727 |           59 |    9.74395e-06 |
| main/f2/vless/G1/outer       | J-S              |          978 |          162 |  0.449934 |           44 |    9.95887e-06 |
| main/f2/vless/G1/outer       | M-S              |          582 |           96 |  0.345027 |           39 |    8.87361e-06 |
| main/f2/vless/G2/outer       | I-S              |          978 |          162 |  0.404906 |           42 |    8.18341e-06 |
| main/f2/vless/G2/outer       | J-G-small        |          978 |          162 |  0.353186 |           38 |    9.58236e-06 |
| main/f2/vless/G2/outer       | J-Marginal-small |          978 |          162 |  0.325919 |           36 |    8.27514e-06 |
| main/f2/vless/G2/outer       | J-P-small        |          978 |          162 |  0.348297 |           37 |    9.13678e-06 |
| main/f2/vless/G2/outer       | J-RawPost-small  |          978 |          162 |  0.361835 |           39 |    8.87645e-06 |
| main/f2/vless/G2/outer       | J-RawPre-small   |          978 |          162 |  0.562876 |           53 |    9.88946e-06 |
| main/f2/vless/G2/outer       | J-S              |          978 |          162 |  0.363393 |           39 |    8.52314e-06 |
| main/f2/vless/G2/outer       | M-S              |          582 |           96 |  0.302129 |           35 |    9.06227e-06 |
| main/f2/vmess/G0/outer       | I-S              |          978 |          162 |  0.531999 |           47 |    9.72905e-06 |
| main/f2/vmess/G0/outer       | J-G-small        |          978 |          162 |  0.443442 |           46 |    9.93801e-06 |
| main/f2/vmess/G0/outer       | J-Marginal-small |          978 |          162 |  0.530688 |           52 |    9.75638e-06 |
| main/f2/vmess/G0/outer       | J-P-small        |          978 |          162 |  0.476279 |           46 |    9.7977e-06  |
| main/f2/vmess/G0/outer       | J-RawPost-small  |          978 |          162 |  0.506571 |           50 |    9.72836e-06 |
| main/f2/vmess/G0/outer       | J-RawPre-small   |          978 |          162 |  0.951833 |           74 |    9.86433e-06 |
| main/f2/vmess/G0/outer       | J-S              |          978 |          162 |  0.579415 |           52 |    9.01394e-06 |
| main/f2/vmess/G0/outer       | M-S              |          582 |           96 |  0.463938 |           39 |    9.18852e-06 |
| main/f2/vmess/G1/outer       | I-S              |          978 |          162 |  0.54031  |           53 |    9.14017e-06 |
| main/f2/vmess/G1/outer       | J-G-small        |          978 |          162 |  0.419916 |           44 |    8.86377e-06 |
| main/f2/vmess/G1/outer       | J-Marginal-small |          978 |          162 |  0.428429 |           44 |    8.73198e-06 |
| main/f2/vmess/G1/outer       | J-P-small        |          978 |          162 |  0.396275 |           42 |    9.5209e-06  |
| main/f2/vmess/G1/outer       | J-RawPost-small  |          978 |          162 |  0.426525 |           44 |    8.71358e-06 |
| main/f2/vmess/G1/outer       | J-RawPre-small   |          978 |          162 |  0.593136 |           55 |    7.182e-06   |
| main/f2/vmess/G1/outer       | J-S              |          978 |          162 |  0.418162 |           44 |    9.26156e-06 |
| main/f2/vmess/G1/outer       | M-S              |          582 |           96 |  0.359715 |           41 |    7.43833e-06 |
| main/f2/vmess/G2/outer       | I-S              |          978 |          162 |  0.665757 |           55 |    9.11805e-06 |
| main/f2/vmess/G2/outer       | J-G-small        |          978 |          162 |  0.592019 |           54 |    9.63338e-06 |
| main/f2/vmess/G2/outer       | J-Marginal-small |          978 |          162 |  0.665914 |           59 |    8.88077e-06 |
| main/f2/vmess/G2/outer       | J-P-small        |          978 |          162 |  0.540129 |           51 |    8.80946e-06 |
| main/f2/vmess/G2/outer       | J-RawPost-small  |          978 |          162 |  0.612995 |           56 |    9.63508e-06 |
| main/f2/vmess/G2/outer       | J-RawPre-small   |          978 |          162 |  0.803759 |           67 |    9.28259e-06 |
| main/f2/vmess/G2/outer       | J-S              |          978 |          162 |  0.647429 |           57 |    9.60962e-06 |
| main/f2/vmess/G2/outer       | M-S              |          582 |           96 |  0.369077 |           42 |    9.56032e-06 |
| main/f3/shadowsocks/G0/outer | I-S              |          978 |          162 |  0.528461 |           52 |    8.66399e-06 |
| main/f3/shadowsocks/G0/outer | J-G-small        |          978 |          162 |  0.419728 |           43 |    8.7724e-06  |
| main/f3/shadowsocks/G0/outer | J-Marginal-small |          978 |          162 |  0.453152 |           46 |    8.17485e-06 |
| main/f3/shadowsocks/G0/outer | J-P-small        |          978 |          162 |  0.443859 |           45 |    7.42537e-06 |
| main/f3/shadowsocks/G0/outer | J-RawPost-small  |          978 |          162 |  0.445582 |           45 |    8.47094e-06 |
| main/f3/shadowsocks/G0/outer | J-RawPre-small   |          978 |          162 |  0.609154 |           56 |    9.89079e-06 |
| main/f3/shadowsocks/G0/outer | J-S              |          978 |          162 |  0.439557 |           45 |    9.14378e-06 |
| main/f3/shadowsocks/G0/outer | M-S              |          582 |           96 |  0.333454 |           40 |    9.33562e-06 |
| main/f3/shadowsocks/G1/outer | I-S              |          978 |          162 |  0.433444 |           45 |    9.60775e-06 |
| main/f3/shadowsocks/G1/outer | J-G-small        |          978 |          162 |  0.461211 |           46 |    9.56428e-06 |
| main/f3/shadowsocks/G1/outer | J-Marginal-small |          978 |          162 |  0.433649 |           45 |    8.7659e-06  |
| main/f3/shadowsocks/G1/outer | J-P-small        |          978 |          162 |  0.44312  |           45 |    9.93124e-06 |
| main/f3/shadowsocks/G1/outer | J-RawPost-small  |          978 |          162 |  0.468957 |           47 |    9.13094e-06 |
| main/f3/shadowsocks/G1/outer | J-RawPre-small   |          978 |          162 |  0.728428 |           62 |    8.28156e-06 |
| main/f3/shadowsocks/G1/outer | J-S              |          978 |          162 |  0.482556 |           48 |    7.22911e-06 |
| main/f3/shadowsocks/G1/outer | M-S              |          582 |           96 |  0.412826 |           46 |    9.42086e-06 |
| main/f3/shadowsocks/G2/outer | I-S              |          978 |          162 |  0.53124  |           47 |    8.06838e-06 |
| main/f3/shadowsocks/G2/outer | J-G-small        |          978 |          162 |  0.467708 |           46 |    7.10023e-06 |
| main/f3/shadowsocks/G2/outer | J-Marginal-small |          978 |          162 |  0.405158 |           42 |    8.75034e-06 |
| main/f3/shadowsocks/G2/outer | J-P-small        |          978 |          162 |  0.450599 |           45 |    8.69473e-06 |
| main/f3/shadowsocks/G2/outer | J-RawPost-small  |          978 |          162 |  0.437406 |           44 |    9.39329e-06 |
| main/f3/shadowsocks/G2/outer | J-RawPre-small   |          978 |          162 |  0.665982 |           58 |    9.10421e-06 |
| main/f3/shadowsocks/G2/outer | J-S              |          978 |          162 |  0.49184  |           46 |    9.08196e-06 |
| main/f3/shadowsocks/G2/outer | M-S              |          582 |           96 |  0.360991 |           37 |    9.18396e-06 |
| main/f3/trojan/G0/outer      | I-S              |          978 |          162 |  0.50914  |           50 |    7.57281e-06 |
| main/f3/trojan/G0/outer      | J-G-small        |          978 |          162 |  0.447461 |           46 |    8.57878e-06 |
| main/f3/trojan/G0/outer      | J-Marginal-small |          978 |          162 |  0.416781 |           43 |    9.8515e-06  |
| main/f3/trojan/G0/outer      | J-P-small        |          978 |          162 |  0.449537 |           46 |    9.77196e-06 |
| main/f3/trojan/G0/outer      | J-RawPost-small  |          978 |          162 |  0.434273 |           45 |    9.1567e-06  |
| main/f3/trojan/G0/outer      | J-RawPre-small   |          978 |          162 |  0.634356 |           58 |    9.05241e-06 |
| main/f3/trojan/G0/outer      | J-S              |          978 |          162 |  0.449243 |           46 |    8.34345e-06 |
| main/f3/trojan/G0/outer      | M-S              |          582 |           96 |  0.37261  |           43 |    5.03327e-06 |
| main/f3/trojan/G1/outer      | I-S              |          978 |          162 |  0.502985 |           49 |    8.57059e-06 |
| main/f3/trojan/G1/outer      | J-G-small        |          978 |          162 |  0.492572 |           47 |    9.28662e-06 |
| main/f3/trojan/G1/outer      | J-Marginal-small |          978 |          162 |  0.466081 |           46 |    9.4609e-06  |
| main/f3/trojan/G1/outer      | J-P-small        |          978 |          162 |  0.52265  |           49 |    8.78513e-06 |
| main/f3/trojan/G1/outer      | J-RawPost-small  |          978 |          162 |  0.461562 |           46 |    7.51238e-06 |
| main/f3/trojan/G1/outer      | J-RawPre-small   |          978 |          162 |  0.824656 |           67 |    7.80703e-06 |
| main/f3/trojan/G1/outer      | J-S              |          978 |          162 |  0.483063 |           46 |    8.09172e-06 |
| main/f3/trojan/G1/outer      | M-S              |          582 |           96 |  0.348071 |           41 |    9.899e-06   |
| main/f3/trojan/G2/outer      | I-S              |          978 |          162 |  0.419761 |           44 |    8.62368e-06 |
| main/f3/trojan/G2/outer      | J-G-small        |          978 |          162 |  0.366426 |           40 |    8.57738e-06 |
| main/f3/trojan/G2/outer      | J-Marginal-small |          978 |          162 |  0.37852  |           40 |    8.53883e-06 |
| main/f3/trojan/G2/outer      | J-P-small        |          978 |          162 |  0.367268 |           40 |    9.50549e-06 |
| main/f3/trojan/G2/outer      | J-RawPost-small  |          978 |          162 |  0.38563  |           41 |    9.08477e-06 |
| main/f3/trojan/G2/outer      | J-RawPre-small   |          978 |          162 |  0.64192  |           57 |    6.46647e-06 |
| main/f3/trojan/G2/outer      | J-S              |          978 |          162 |  0.390349 |           41 |    8.78062e-06 |
| main/f3/trojan/G2/outer      | M-S              |          582 |           96 |  0.328703 |           38 |    9.47868e-06 |
| main/f3/vless/G0/outer       | I-S              |          978 |          162 |  0.538862 |           52 |    7.50733e-06 |
| main/f3/vless/G0/outer       | J-G-small        |          978 |          162 |  0.433103 |           45 |    7.4324e-06  |
| main/f3/vless/G0/outer       | J-Marginal-small |          978 |          162 |  0.426291 |           43 |    9.84305e-06 |
| main/f3/vless/G0/outer       | J-P-small        |          978 |          162 |  0.400669 |           43 |    7.6719e-06  |
| main/f3/vless/G0/outer       | J-RawPost-small  |          978 |          162 |  0.440944 |           45 |    8.60768e-06 |
| main/f3/vless/G0/outer       | J-RawPre-small   |          978 |          162 |  0.71135  |           62 |    6.69547e-06 |
| main/f3/vless/G0/outer       | J-S              |          978 |          162 |  0.410888 |           44 |    9.78914e-06 |
| main/f3/vless/G0/outer       | M-S              |          582 |           96 |  0.352296 |           40 |    9.70477e-06 |
| main/f3/vless/G1/outer       | I-S              |          978 |          162 |  0.511048 |           49 |    9.71473e-06 |
| main/f3/vless/G1/outer       | J-G-small        |          978 |          162 |  0.450015 |           45 |    9.57881e-06 |
| main/f3/vless/G1/outer       | J-Marginal-small |          978 |          162 |  0.498455 |           47 |    9.95263e-06 |
| main/f3/vless/G1/outer       | J-P-small        |          978 |          162 |  0.46177  |           45 |    9.58267e-06 |
| main/f3/vless/G1/outer       | J-RawPost-small  |          978 |          162 |  0.467557 |           46 |    8.89607e-06 |
| main/f3/vless/G1/outer       | J-RawPre-small   |          978 |          162 |  0.649528 |           57 |    3.7525e-06  |
| main/f3/vless/G1/outer       | J-S              |          978 |          162 |  0.455906 |           45 |    9.16276e-06 |
| main/f3/vless/G1/outer       | M-S              |          582 |           96 |  0.378654 |           41 |    8.89232e-06 |
| main/f3/vless/G2/outer       | I-S              |          978 |          162 |  0.512542 |           43 |    9.5151e-06  |
| main/f3/vless/G2/outer       | J-G-small        |          978 |          162 |  0.35668  |           38 |    9.7045e-06  |
| main/f3/vless/G2/outer       | J-Marginal-small |          978 |          162 |  0.381955 |           41 |    9.04374e-06 |
| main/f3/vless/G2/outer       | J-P-small        |          978 |          162 |  0.385551 |           39 |    9.85098e-06 |
| main/f3/vless/G2/outer       | J-RawPost-small  |          978 |          162 |  0.377043 |           39 |    9.3961e-06  |
| main/f3/vless/G2/outer       | J-RawPre-small   |          978 |          162 |  0.673255 |           59 |    9.68507e-06 |
| main/f3/vless/G2/outer       | J-S              |          978 |          162 |  0.406791 |           39 |    9.04281e-06 |
| main/f3/vless/G2/outer       | M-S              |          582 |           96 |  0.476108 |           38 |    7.41635e-06 |
| main/f3/vmess/G0/outer       | I-S              |          978 |          162 |  0.493945 |           50 |    9.10407e-06 |
| main/f3/vmess/G0/outer       | J-G-small        |          978 |          162 |  0.382947 |           42 |    8.97485e-06 |
| main/f3/vmess/G0/outer       | J-Marginal-small |          978 |          162 |  0.387657 |           42 |    9.04103e-06 |
| main/f3/vmess/G0/outer       | J-P-small        |          978 |          162 |  0.407702 |           43 |    9.50366e-06 |
| main/f3/vmess/G0/outer       | J-RawPost-small  |          978 |          162 |  0.403497 |           43 |    9.53478e-06 |
| main/f3/vmess/G0/outer       | J-RawPre-small   |          978 |          162 |  0.518497 |           51 |    9.77159e-06 |
| main/f3/vmess/G0/outer       | J-S              |          978 |          162 |  0.416795 |           44 |    8.6534e-06  |
| main/f3/vmess/G0/outer       | M-S              |          582 |           96 |  0.303583 |           37 |    9.44478e-06 |
| main/f3/vmess/G1/outer       | I-S              |          978 |          162 |  0.478653 |           50 |    8.66618e-06 |
| main/f3/vmess/G1/outer       | J-G-small        |          978 |          162 |  0.501649 |           48 |    9.04814e-06 |
| main/f3/vmess/G1/outer       | J-Marginal-small |          978 |          162 |  0.413969 |           43 |    8.98682e-06 |
| main/f3/vmess/G1/outer       | J-P-small        |          978 |          162 |  0.499031 |           48 |    9.69027e-06 |
| main/f3/vmess/G1/outer       | J-RawPost-small  |          978 |          162 |  0.399776 |           42 |    8.72406e-06 |
| main/f3/vmess/G1/outer       | J-RawPre-small   |          978 |          162 |  0.625638 |           57 |    9.30034e-06 |
| main/f3/vmess/G1/outer       | J-S              |          978 |          162 |  0.399358 |           42 |    9.24818e-06 |
| main/f3/vmess/G1/outer       | M-S              |          582 |           96 |  0.308947 |           38 |    7.35313e-06 |
| main/f3/vmess/G2/outer       | I-S              |          978 |          162 |  0.565284 |           52 |    9.60796e-06 |
| main/f3/vmess/G2/outer       | J-G-small        |          978 |          162 |  0.472234 |           46 |    8.74642e-06 |
| main/f3/vmess/G2/outer       | J-Marginal-small |          978 |          162 |  0.53642  |           51 |    9.39228e-06 |
| main/f3/vmess/G2/outer       | J-P-small        |          978 |          162 |  0.432942 |           44 |    7.87803e-06 |
| main/f3/vmess/G2/outer       | J-RawPost-small  |          978 |          162 |  0.438501 |           44 |    8.59061e-06 |
| main/f3/vmess/G2/outer       | J-RawPre-small   |          978 |          162 |  0.710967 |           61 |    8.13527e-06 |
| main/f3/vmess/G2/outer       | J-S              |          978 |          162 |  0.426188 |           44 |    9.47396e-06 |
| main/f3/vmess/G2/outer       | M-S              |          582 |           96 |  0.317538 |           38 |    8.94537e-06 |
| main/f4/shadowsocks/G0/outer | I-S              |          978 |          162 |  0.681479 |           61 |    9.19189e-06 |
| main/f4/shadowsocks/G0/outer | J-G-small        |          978 |          162 |  0.543764 |           52 |    7.96301e-06 |
| main/f4/shadowsocks/G0/outer | J-Marginal-small |          978 |          162 |  0.403116 |           43 |    9.53409e-06 |
| main/f4/shadowsocks/G0/outer | J-P-small        |          978 |          162 |  0.509455 |           49 |    9.08855e-06 |
| main/f4/shadowsocks/G0/outer | J-RawPost-small  |          978 |          162 |  0.473452 |           47 |    9.87362e-06 |
| main/f4/shadowsocks/G0/outer | J-RawPre-small   |          978 |          162 |  0.713983 |           62 |    6.97185e-06 |
| main/f4/shadowsocks/G0/outer | J-S              |          978 |          162 |  0.504478 |           49 |    9.90025e-06 |
| main/f4/shadowsocks/G0/outer | M-S              |          582 |           96 |  0.409388 |           45 |    9.93908e-06 |
| main/f4/shadowsocks/G1/outer | I-S              |          978 |          162 |  0.540274 |           49 |    8.05377e-06 |
| main/f4/shadowsocks/G1/outer | J-G-small        |          978 |          162 |  0.434069 |           45 |    9.14153e-06 |
| main/f4/shadowsocks/G1/outer | J-Marginal-small |          978 |          162 |  0.435287 |           45 |    8.60324e-06 |
| main/f4/shadowsocks/G1/outer | J-P-small        |          978 |          162 |  0.450508 |           46 |    7.37709e-06 |
| main/f4/shadowsocks/G1/outer | J-RawPost-small  |          978 |          162 |  0.464501 |           47 |    7.98217e-06 |
| main/f4/shadowsocks/G1/outer | J-RawPre-small   |          978 |          162 |  0.622173 |           57 |    8.69063e-06 |
| main/f4/shadowsocks/G1/outer | J-S              |          978 |          162 |  0.489616 |           48 |    6.57918e-06 |
| main/f4/shadowsocks/G1/outer | M-S              |          582 |           96 |  0.469181 |           42 |    9.05042e-06 |
| main/f4/shadowsocks/G2/outer | I-S              |          978 |          162 |  0.569277 |           54 |    9.59399e-06 |
| main/f4/shadowsocks/G2/outer | J-G-small        |          978 |          162 |  0.458191 |           44 |    7.41293e-06 |
| main/f4/shadowsocks/G2/outer | J-Marginal-small |          978 |          162 |  0.416318 |           43 |    8.78737e-06 |
| main/f4/shadowsocks/G2/outer | J-P-small        |          978 |          162 |  0.439002 |           43 |    9.33424e-06 |
| main/f4/shadowsocks/G2/outer | J-RawPost-small  |          978 |          162 |  0.474844 |           46 |    9.77969e-06 |
| main/f4/shadowsocks/G2/outer | J-RawPre-small   |          978 |          162 |  0.672845 |           57 |    8.62222e-06 |
| main/f4/shadowsocks/G2/outer | J-S              |          978 |          162 |  0.456688 |           46 |    9.78221e-06 |
| main/f4/shadowsocks/G2/outer | M-S              |          582 |           96 |  0.362584 |           41 |    9.38075e-06 |
| main/f4/trojan/G0/outer      | I-S              |          978 |          162 |  0.556427 |           51 |    9.69788e-06 |
| main/f4/trojan/G0/outer      | J-G-small        |          978 |          162 |  0.422013 |           43 |    9.57636e-06 |
| main/f4/trojan/G0/outer      | J-Marginal-small |          978 |          162 |  0.368058 |           40 |    9.19583e-06 |
| main/f4/trojan/G0/outer      | J-P-small        |          978 |          162 |  0.416343 |           42 |    9.89297e-06 |
| main/f4/trojan/G0/outer      | J-RawPost-small  |          978 |          162 |  0.423387 |           44 |    9.18543e-06 |
| main/f4/trojan/G0/outer      | J-RawPre-small   |          978 |          162 |  0.643203 |           57 |    8.34836e-06 |
| main/f4/trojan/G0/outer      | J-S              |          978 |          162 |  0.422237 |           43 |    8.98559e-06 |
| main/f4/trojan/G0/outer      | M-S              |          582 |           96 |  0.359285 |           40 |    9.51756e-06 |
| main/f4/trojan/G1/outer      | I-S              |          978 |          162 |  0.576998 |           50 |    9.95239e-06 |
| main/f4/trojan/G1/outer      | J-G-small        |          978 |          162 |  0.44528  |           44 |    8.94661e-06 |
| main/f4/trojan/G1/outer      | J-Marginal-small |          978 |          162 |  0.512334 |           50 |    6.23342e-06 |
| main/f4/trojan/G1/outer      | J-P-small        |          978 |          162 |  0.472878 |           46 |    9.68593e-06 |
| main/f4/trojan/G1/outer      | J-RawPost-small  |          978 |          162 |  0.445243 |           45 |    7.75604e-06 |
| main/f4/trojan/G1/outer      | J-RawPre-small   |          978 |          162 |  0.717027 |           61 |    7.85222e-06 |
| main/f4/trojan/G1/outer      | J-S              |          978 |          162 |  0.475887 |           45 |    9.19961e-06 |
| main/f4/trojan/G1/outer      | M-S              |          582 |           96 |  0.491696 |           43 |    9.19631e-06 |
| main/f4/trojan/G2/outer      | I-S              |          978 |          162 |  0.573991 |           46 |    9.61369e-06 |
| main/f4/trojan/G2/outer      | J-G-small        |          978 |          162 |  0.431783 |           43 |    9.71268e-06 |
| main/f4/trojan/G2/outer      | J-Marginal-small |          978 |          162 |  0.398101 |           42 |    9.92327e-06 |
| main/f4/trojan/G2/outer      | J-P-small        |          978 |          162 |  0.458143 |           44 |    8.25297e-06 |
| main/f4/trojan/G2/outer      | J-RawPost-small  |          978 |          162 |  0.456087 |           45 |    9.41094e-06 |
| main/f4/trojan/G2/outer      | J-RawPre-small   |          978 |          162 |  0.617949 |           54 |    8.91222e-06 |
| main/f4/trojan/G2/outer      | J-S              |          978 |          162 |  0.463877 |           44 |    8.66199e-06 |
| main/f4/trojan/G2/outer      | M-S              |          582 |           96 |  0.493182 |           39 |    7.53398e-06 |
| main/f4/vless/G0/outer       | I-S              |          978 |          162 |  0.580875 |           52 |    8.79717e-06 |
| main/f4/vless/G0/outer       | J-G-small        |          978 |          162 |  0.404231 |           41 |    9.92052e-06 |
| main/f4/vless/G0/outer       | J-Marginal-small |          978 |          162 |  0.384725 |           41 |    9.96335e-06 |
| main/f4/vless/G0/outer       | J-P-small        |          978 |          162 |  0.396428 |           41 |    9.70113e-06 |
| main/f4/vless/G0/outer       | J-RawPost-small  |          978 |          162 |  0.395657 |           41 |    8.86832e-06 |
| main/f4/vless/G0/outer       | J-RawPre-small   |          978 |          162 |  0.541963 |           52 |    9.59799e-06 |
| main/f4/vless/G0/outer       | J-S              |          978 |          162 |  0.430016 |           42 |    7.92846e-06 |
| main/f4/vless/G0/outer       | M-S              |          582 |           96 |  0.450417 |           42 |    9.13542e-06 |
| main/f4/vless/G1/outer       | I-S              |          978 |          162 |  0.50399  |           49 |    9.1136e-06  |
| main/f4/vless/G1/outer       | J-G-small        |          978 |          162 |  0.440939 |           44 |    9.80334e-06 |
| main/f4/vless/G1/outer       | J-Marginal-small |          978 |          162 |  0.47346  |           47 |    9.50482e-06 |
| main/f4/vless/G1/outer       | J-P-small        |          978 |          162 |  0.50187  |           48 |    9.50626e-06 |
| main/f4/vless/G1/outer       | J-RawPost-small  |          978 |          162 |  0.455712 |           45 |    7.09486e-06 |
| main/f4/vless/G1/outer       | J-RawPre-small   |          978 |          162 |  0.718229 |           61 |    7.61346e-06 |
| main/f4/vless/G1/outer       | J-S              |          978 |          162 |  0.445993 |           45 |    8.96381e-06 |
| main/f4/vless/G1/outer       | M-S              |          582 |           96 |  0.354828 |           42 |    9.90321e-06 |
| main/f4/vless/G2/outer       | I-S              |          978 |          162 |  0.514505 |           45 |    8.8412e-06  |
| main/f4/vless/G2/outer       | J-G-small        |          978 |          162 |  0.370487 |           40 |    7.30675e-06 |
| main/f4/vless/G2/outer       | J-Marginal-small |          978 |          162 |  0.365398 |           40 |    9.0419e-06  |
| main/f4/vless/G2/outer       | J-P-small        |          978 |          162 |  0.374259 |           39 |    9.53108e-06 |
| main/f4/vless/G2/outer       | J-RawPost-small  |          978 |          162 |  0.351375 |           38 |    8.70147e-06 |
| main/f4/vless/G2/outer       | J-RawPre-small   |          978 |          162 |  0.578581 |           54 |    7.69789e-06 |
| main/f4/vless/G2/outer       | J-S              |          978 |          162 |  0.382794 |           39 |    9.82818e-06 |
| main/f4/vless/G2/outer       | M-S              |          582 |           96 |  0.410447 |           38 |    8.27953e-06 |
| main/f4/vmess/G0/outer       | I-S              |          978 |          162 |  0.473069 |           49 |    8.43778e-06 |
| main/f4/vmess/G0/outer       | J-G-small        |          978 |          162 |  0.51281  |           49 |    9.75459e-06 |
| main/f4/vmess/G0/outer       | J-Marginal-small |          978 |          162 |  0.493103 |           48 |    6.84512e-06 |
| main/f4/vmess/G0/outer       | J-P-small        |          978 |          162 |  0.512513 |           49 |    9.54945e-06 |
| main/f4/vmess/G0/outer       | J-RawPost-small  |          978 |          162 |  0.448463 |           44 |    8.8507e-06  |
| main/f4/vmess/G0/outer       | J-RawPre-small   |          978 |          162 |  0.571742 |           52 |    4.7161e-06  |
| main/f4/vmess/G0/outer       | J-S              |          978 |          162 |  0.425338 |           44 |    9.10858e-06 |
| main/f4/vmess/G0/outer       | M-S              |          582 |           96 |  0.340238 |           40 |    9.46728e-06 |
| main/f4/vmess/G1/outer       | I-S              |          978 |          162 |  0.613814 |           57 |    9.70454e-06 |
| main/f4/vmess/G1/outer       | J-G-small        |          978 |          162 |  0.45824  |           46 |    8.24721e-06 |
| main/f4/vmess/G1/outer       | J-Marginal-small |          978 |          162 |  0.461937 |           45 |    9.11738e-06 |
| main/f4/vmess/G1/outer       | J-P-small        |          978 |          162 |  0.435454 |           45 |    8.09636e-06 |
| main/f4/vmess/G1/outer       | J-RawPost-small  |          978 |          162 |  0.418572 |           43 |    9.83236e-06 |
| main/f4/vmess/G1/outer       | J-RawPre-small   |          978 |          162 |  0.610124 |           55 |    5.82748e-06 |
| main/f4/vmess/G1/outer       | J-S              |          978 |          162 |  0.431306 |           45 |    8.45832e-06 |
| main/f4/vmess/G1/outer       | M-S              |          582 |           96 |  0.33315  |           40 |    9.77653e-06 |
| main/f4/vmess/G2/outer       | I-S              |          978 |          162 |  0.712388 |           61 |    8.75218e-06 |
| main/f4/vmess/G2/outer       | J-G-small        |          978 |          162 |  0.495718 |           46 |    9.56387e-06 |
| main/f4/vmess/G2/outer       | J-Marginal-small |          978 |          162 |  0.594144 |           53 |    9.69055e-06 |
| main/f4/vmess/G2/outer       | J-P-small        |          978 |          162 |  0.48112  |           47 |    9.80621e-06 |
| main/f4/vmess/G2/outer       | J-RawPost-small  |          978 |          162 |  0.529541 |           50 |    9.43393e-06 |
| main/f4/vmess/G2/outer       | J-RawPre-small   |          978 |          162 |  0.803795 |           66 |    6.00197e-06 |
| main/f4/vmess/G2/outer       | J-S              |          978 |          162 |  0.529431 |           50 |    9.70427e-06 |
| main/f4/vmess/G2/outer       | M-S              |          582 |           96 |  0.433117 |           46 |    8.43107e-06 |
| main/f0/shadowsocks/G0/outer | I-inner0         |          978 |          162 |  1.1437   |           92 |    9.01673e-06 |
| main/f0/shadowsocks/G0/outer | I-inner0         |          978 |          162 |  0.963805 |           98 |    9.34447e-06 |
| main/f0/shadowsocks/G0/outer | I-inner0         |          978 |          162 |  0.974613 |           79 |    9.35502e-06 |
| main/f0/shadowsocks/G0/outer | I-inner0         |          978 |          162 |  0.657717 |           60 |    8.73353e-06 |
| main/f0/shadowsocks/G0/outer | I-inner1         |          978 |          162 |  1.36958  |           94 |    9.52843e-06 |
| main/f0/shadowsocks/G0/outer | I-inner1         |          978 |          162 |  1.55546  |          102 |    8.73477e-06 |
| main/f0/shadowsocks/G0/outer | I-inner1         |          978 |          162 |  1.10629  |           81 |    9.56188e-06 |
| main/f0/shadowsocks/G0/outer | I-inner1         |          978 |          162 |  0.62668  |           57 |    9.47474e-06 |
| main/f0/shadowsocks/G0/outer | J-inner0         |          978 |          162 |  0.95678  |           73 |    9.19896e-06 |
| main/f0/shadowsocks/G0/outer | J-inner0         |          978 |          162 |  1.0334   |           77 |    9.39382e-06 |
| main/f0/shadowsocks/G0/outer | J-inner0         |          978 |          162 |  0.745638 |           63 |    8.16282e-06 |
| main/f0/shadowsocks/G0/outer | J-inner0         |          978 |          162 |  0.516154 |           49 |    9.26833e-06 |
| main/f0/shadowsocks/G0/outer | J-inner1         |          978 |          162 |  0.937495 |           72 |    9.73179e-06 |
| main/f0/shadowsocks/G0/outer | J-inner1         |          978 |          162 |  1.11091  |           79 |    9.85835e-06 |
| main/f0/shadowsocks/G0/outer | J-inner1         |          978 |          162 |  0.686311 |           60 |    8.03371e-06 |
| main/f0/shadowsocks/G0/outer | J-inner1         |          978 |          162 |  0.468499 |           47 |    8.49411e-06 |
| main/f0/shadowsocks/G0/outer | M-inner0         |          582 |           96 |  0.493537 |           64 |    9.01745e-06 |
| main/f0/shadowsocks/G0/outer | M-inner0         |          582 |           96 |  1.40424  |           69 |    9.43492e-06 |
| main/f0/shadowsocks/G0/outer | M-inner0         |          582 |           96 |  0.420964 |           59 |    7.77372e-06 |
| main/f0/shadowsocks/G0/outer | M-inner0         |          582 |           96 |  0.28615  |           46 |    9.19007e-06 |
| main/f0/shadowsocks/G0/outer | M-inner1         |          582 |           96 |  0.522379 |           67 |    7.63521e-06 |
| main/f0/shadowsocks/G0/outer | M-inner1         |          582 |           96 |  0.547762 |           71 |    8.67869e-06 |
| main/f0/shadowsocks/G0/outer | M-inner1         |          582 |           96 |  0.373428 |           56 |    9.84907e-06 |
| main/f0/shadowsocks/G0/outer | M-inner1         |          582 |           96 |  0.262017 |           45 |    6.0558e-06  |
| main/f0/shadowsocks/G1/outer | I-inner0         |          978 |          162 |  1.70671  |          102 |    9.60842e-06 |
| main/f0/shadowsocks/G1/outer | I-inner0         |          978 |          162 |  2.03078  |          112 |    9.68397e-06 |
| main/f0/shadowsocks/G1/outer | I-inner0         |          978 |          162 |  1.31681  |           89 |    7.28758e-06 |
| main/f0/shadowsocks/G1/outer | I-inner0         |          978 |          162 |  0.76167  |           64 |    9.29896e-06 |
| main/f0/shadowsocks/G1/outer | I-inner1         |          978 |          162 |  1.08098  |           80 |    9.39061e-06 |
| main/f0/shadowsocks/G1/outer | I-inner1         |          978 |          162 |  1.12253  |           83 |    9.74927e-06 |
| main/f0/shadowsocks/G1/outer | I-inner1         |          978 |          162 |  1.00922  |           76 |    9.2239e-06  |
| main/f0/shadowsocks/G1/outer | I-inner1         |          978 |          162 |  0.673092 |           59 |    9.52156e-06 |
| main/f0/shadowsocks/G1/outer | J-inner0         |          978 |          162 |  1.34186  |           91 |    9.39523e-06 |
| main/f0/shadowsocks/G1/outer | J-inner0         |          978 |          162 |  1.50883  |           97 |    9.39677e-06 |
| main/f0/shadowsocks/G1/outer | J-inner0         |          978 |          162 |  1.03858  |           77 |    9.35042e-06 |
| main/f0/shadowsocks/G1/outer | J-inner0         |          978 |          162 |  0.645502 |           56 |    9.46124e-06 |
| main/f0/shadowsocks/G1/outer | J-inner1         |          978 |          162 |  1.06246  |           78 |    9.95369e-06 |
| main/f0/shadowsocks/G1/outer | J-inner1         |          978 |          162 |  1.285    |           87 |    8.39647e-06 |
| main/f0/shadowsocks/G1/outer | J-inner1         |          978 |          162 |  0.832049 |           67 |    9.63323e-06 |
| main/f0/shadowsocks/G1/outer | J-inner1         |          978 |          162 |  0.495281 |           48 |    9.43244e-06 |
| main/f0/shadowsocks/G1/outer | M-inner0         |          582 |           96 |  1.22354  |           86 |    8.64242e-06 |
| main/f0/shadowsocks/G1/outer | M-inner0         |          582 |           96 |  1.35238  |           93 |    9.21274e-06 |
| main/f0/shadowsocks/G1/outer | M-inner0         |          582 |           96 |  1.0497   |           76 |    8.65795e-06 |
| main/f0/shadowsocks/G1/outer | M-inner0         |          582 |           96 |  0.602631 |           53 |    9.93211e-06 |
| main/f0/shadowsocks/G1/outer | M-inner1         |          582 |           96 |  0.882618 |           71 |    9.06968e-06 |
| main/f0/shadowsocks/G1/outer | M-inner1         |          582 |           96 |  1.01833  |           76 |    9.54946e-06 |
| main/f0/shadowsocks/G1/outer | M-inner1         |          582 |           96 |  0.743784 |           63 |    9.50499e-06 |
| main/f0/shadowsocks/G1/outer | M-inner1         |          582 |           96 |  0.480935 |           47 |    7.99259e-06 |
| main/f0/shadowsocks/G2/outer | I-inner0         |          978 |          162 |  1.55555  |           97 |    9.77284e-06 |
| main/f0/shadowsocks/G2/outer | I-inner0         |          978 |          162 |  1.69232  |          103 |    9.18565e-06 |
| main/f0/shadowsocks/G2/outer | I-inner0         |          978 |          162 |  1.21555  |           84 |    8.52482e-06 |
| main/f0/shadowsocks/G2/outer | I-inner0         |          978 |          162 |  0.750659 |           63 |    9.07283e-06 |
| main/f0/shadowsocks/G2/outer | I-inner1         |          978 |          162 |  1.33724  |           92 |    8.88367e-06 |
| main/f0/shadowsocks/G2/outer | I-inner1         |          978 |          162 |  1.50864  |          100 |    9.79755e-06 |
| main/f0/shadowsocks/G2/outer | I-inner1         |          978 |          162 |  0.942004 |           75 |    9.54856e-06 |
| main/f0/shadowsocks/G2/outer | I-inner1         |          978 |          162 |  0.677613 |           60 |    9.26971e-06 |
| main/f0/shadowsocks/G2/outer | J-inner0         |          978 |          162 |  1.10335  |           83 |    9.45041e-06 |
| main/f0/shadowsocks/G2/outer | J-inner0         |          978 |          162 |  1.17389  |           87 |    8.61704e-06 |
| main/f0/shadowsocks/G2/outer | J-inner0         |          978 |          162 |  0.846674 |           69 |    9.1669e-06  |
| main/f0/shadowsocks/G2/outer | J-inner0         |          978 |          162 |  0.51637  |           51 |    9.5368e-06  |
| main/f0/shadowsocks/G2/outer | J-inner1         |          978 |          162 |  0.939977 |           74 |    9.78542e-06 |
| main/f0/shadowsocks/G2/outer | J-inner1         |          978 |          162 |  1.07788  |           81 |    9.30255e-06 |
| main/f0/shadowsocks/G2/outer | J-inner1         |          978 |          162 |  0.855367 |           70 |    8.86681e-06 |
| main/f0/shadowsocks/G2/outer | J-inner1         |          978 |          162 |  0.569674 |           53 |    6.61587e-06 |
| main/f0/shadowsocks/G2/outer | M-inner0         |          582 |           96 |  0.87891  |           71 |    9.45409e-06 |
| main/f0/shadowsocks/G2/outer | M-inner0         |          582 |           96 |  0.960505 |           77 |    9.38968e-06 |
| main/f0/shadowsocks/G2/outer | M-inner0         |          582 |           96 |  0.734439 |           63 |    6.55081e-06 |
| main/f0/shadowsocks/G2/outer | M-inner0         |          582 |           96 |  0.430255 |           45 |    8.43349e-06 |
| main/f0/shadowsocks/G2/outer | M-inner1         |          582 |           96 |  0.879222 |           68 |    9.82237e-06 |
| main/f0/shadowsocks/G2/outer | M-inner1         |          582 |           96 |  0.919653 |           71 |    9.12874e-06 |
| main/f0/shadowsocks/G2/outer | M-inner1         |          582 |           96 |  0.638063 |           57 |    8.64328e-06 |
| main/f0/shadowsocks/G2/outer | M-inner1         |          582 |           96 |  0.485926 |           48 |    5.37892e-06 |
| main/f0/trojan/G0/outer      | I-inner0         |          978 |          162 |  0.802442 |           65 |    9.51474e-06 |
| main/f0/trojan/G0/outer      | I-inner0         |          978 |          162 |  0.968448 |           72 |    9.67137e-06 |
| main/f0/trojan/G0/outer      | I-inner0         |          978 |          162 |  0.628641 |           56 |    9.4107e-06  |
| main/f0/trojan/G0/outer      | I-inner0         |          978 |          162 |  0.383187 |           41 |    7.82668e-06 |
| main/f0/trojan/G0/outer      | I-inner1         |          978 |          162 |  1.20585  |           86 |    9.31626e-06 |
| main/f0/trojan/G0/outer      | I-inner1         |          978 |          162 |  1.36597  |           93 |    9.93207e-06 |
| main/f0/trojan/G0/outer      | I-inner1         |          978 |          162 |  0.932438 |           74 |    9.20636e-06 |
| main/f0/trojan/G0/outer      | I-inner1         |          978 |          162 |  0.600843 |           56 |    9.04597e-06 |
| main/f0/trojan/G0/outer      | J-inner0         |          978 |          162 |  0.687918 |           61 |    8.55515e-06 |
| main/f0/trojan/G0/outer      | J-inner0         |          978 |          162 |  0.784412 |           66 |    8.64444e-06 |
| main/f0/trojan/G0/outer      | J-inner0         |          978 |          162 |  0.529885 |           51 |    8.80918e-06 |
| main/f0/trojan/G0/outer      | J-inner0         |          978 |          162 |  0.393962 |           42 |    8.91324e-06 |
| main/f0/trojan/G0/outer      | J-inner1         |          978 |          162 |  0.972661 |           75 |    9.29337e-06 |
| main/f0/trojan/G0/outer      | J-inner1         |          978 |          162 |  1.11127  |           81 |    9.81699e-06 |
| main/f0/trojan/G0/outer      | J-inner1         |          978 |          162 |  0.695408 |           62 |    9.44465e-06 |
| main/f0/trojan/G0/outer      | J-inner1         |          978 |          162 |  0.547863 |           52 |    9.30569e-06 |
| main/f0/trojan/G0/outer      | M-inner0         |          582 |           96 |  0.767267 |           63 |    9.86777e-06 |
| main/f0/trojan/G0/outer      | M-inner0         |          582 |           96 |  0.845876 |           68 |    9.27576e-06 |
| main/f0/trojan/G0/outer      | M-inner0         |          582 |           96 |  0.594424 |           54 |    8.80038e-06 |
| main/f0/trojan/G0/outer      | M-inner0         |          582 |           96 |  0.355524 |           38 |    8.1961e-06  |
| main/f0/trojan/G0/outer      | M-inner1         |          582 |           96 |  0.979297 |           73 |    9.51956e-06 |
| main/f0/trojan/G0/outer      | M-inner1         |          582 |           96 |  1.17973  |           80 |    9.87349e-06 |
| main/f0/trojan/G0/outer      | M-inner1         |          582 |           96 |  0.780178 |           65 |    8.95589e-06 |
| main/f0/trojan/G0/outer      | M-inner1         |          582 |           96 |  0.562776 |           53 |    9.33708e-06 |
| main/f0/trojan/G1/outer      | I-inner0         |          978 |          162 |  1.08705  |           78 |    9.78786e-06 |
| main/f0/trojan/G1/outer      | I-inner0         |          978 |          162 |  1.29335  |           85 |    9.41165e-06 |
| main/f0/trojan/G1/outer      | I-inner0         |          978 |          162 |  0.938209 |           72 |    9.54277e-06 |
| main/f0/trojan/G1/outer      | I-inner0         |          978 |          162 |  0.541918 |           51 |    9.49339e-06 |
| main/f0/trojan/G1/outer      | I-inner1         |          978 |          162 |  1.55273  |           96 |    9.70783e-06 |
| main/f0/trojan/G1/outer      | I-inner1         |          978 |          162 |  1.60318  |          101 |    9.15878e-06 |
| main/f0/trojan/G1/outer      | I-inner1         |          978 |          162 |  1.17907  |           84 |    8.93734e-06 |
| main/f0/trojan/G1/outer      | I-inner1         |          978 |          162 |  0.727027 |           61 |    9.57699e-06 |
| main/f0/trojan/G1/outer      | J-inner0         |          978 |          162 |  0.658675 |           73 |    8.95327e-06 |
| main/f0/trojan/G1/outer      | J-inner0         |          978 |          162 |  1.18387  |           80 |    9.50883e-06 |
| main/f0/trojan/G1/outer      | J-inner0         |          978 |          162 |  0.478735 |           61 |    9.80297e-06 |
| main/f0/trojan/G1/outer      | J-inner0         |          978 |          162 |  0.284236 |           45 |    8.4979e-06  |
| main/f0/trojan/G1/outer      | J-inner1         |          978 |          162 |  0.560516 |           69 |    9.53036e-06 |
| main/f0/trojan/G1/outer      | J-inner1         |          978 |          162 |  0.640405 |           75 |    8.82889e-06 |
| main/f0/trojan/G1/outer      | J-inner1         |          978 |          162 |  0.448884 |           61 |    9.1172e-06  |
| main/f0/trojan/G1/outer      | J-inner1         |          978 |          162 |  0.276878 |           45 |    9.27159e-06 |
| main/f0/trojan/G1/outer      | M-inner0         |          582 |           96 |  0.808681 |           67 |    8.71966e-06 |
| main/f0/trojan/G1/outer      | M-inner0         |          582 |           96 |  0.927782 |           73 |    9.76331e-06 |
| main/f0/trojan/G1/outer      | M-inner0         |          582 |           96 |  0.674111 |           59 |    7.96954e-06 |
| main/f0/trojan/G1/outer      | M-inner0         |          582 |           96 |  0.426735 |           44 |    8.3588e-06  |
| main/f0/trojan/G1/outer      | M-inner1         |          582 |           96 |  0.794029 |           64 |    9.4565e-06  |
| main/f0/trojan/G1/outer      | M-inner1         |          582 |           96 |  0.906482 |           68 |    9.89403e-06 |
| main/f0/trojan/G1/outer      | M-inner1         |          582 |           96 |  0.608189 |           54 |    9.68455e-06 |
| main/f0/trojan/G1/outer      | M-inner1         |          582 |           96 |  0.406022 |           40 |    7.12227e-06 |
| main/f0/trojan/G2/outer      | I-inner0         |          978 |          162 |  0.862029 |           71 |    9.55806e-06 |
| main/f0/trojan/G2/outer      | I-inner0         |          978 |          162 |  1.01317  |           79 |    8.67107e-06 |
| main/f0/trojan/G2/outer      | I-inner0         |          978 |          162 |  0.752957 |           64 |    8.43955e-06 |
| main/f0/trojan/G2/outer      | I-inner0         |          978 |          162 |  0.483596 |           48 |    8.86528e-06 |
| main/f0/trojan/G2/outer      | I-inner1         |          978 |          162 |  0.874983 |           72 |    8.57994e-06 |
| main/f0/trojan/G2/outer      | I-inner1         |          978 |          162 |  1.0626   |           81 |    9.39544e-06 |
| main/f0/trojan/G2/outer      | I-inner1         |          978 |          162 |  0.754807 |           63 |    8.59186e-06 |
| main/f0/trojan/G2/outer      | I-inner1         |          978 |          162 |  0.476107 |           48 |    9.05447e-06 |
| main/f0/trojan/G2/outer      | J-inner0         |          978 |          162 |  0.966147 |           72 |    9.10516e-06 |
| main/f0/trojan/G2/outer      | J-inner0         |          978 |          162 |  1.14091  |           80 |    7.89712e-06 |
| main/f0/trojan/G2/outer      | J-inner0         |          978 |          162 |  0.747665 |           62 |    9.73896e-06 |
| main/f0/trojan/G2/outer      | J-inner0         |          978 |          162 |  0.482589 |           46 |    8.96554e-06 |
| main/f0/trojan/G2/outer      | J-inner1         |          978 |          162 |  0.841506 |           68 |    9.45179e-06 |
| main/f0/trojan/G2/outer      | J-inner1         |          978 |          162 |  0.912118 |           72 |    9.94024e-06 |
| main/f0/trojan/G2/outer      | J-inner1         |          978 |          162 |  0.656081 |           58 |    9.19407e-06 |
| main/f0/trojan/G2/outer      | J-inner1         |          978 |          162 |  0.424371 |           43 |    9.8419e-06  |
| main/f0/trojan/G2/outer      | M-inner0         |          582 |           96 |  0.635317 |           59 |    9.26026e-06 |
| main/f0/trojan/G2/outer      | M-inner0         |          582 |           96 |  0.685771 |           62 |    9.98812e-06 |
| main/f0/trojan/G2/outer      | M-inner0         |          582 |           96 |  0.544786 |           53 |    9.70544e-06 |
| main/f0/trojan/G2/outer      | M-inner0         |          582 |           96 |  0.347746 |           39 |    9.55886e-06 |
| main/f0/trojan/G2/outer      | M-inner1         |          582 |           96 |  0.600029 |           55 |    9.09494e-06 |
| main/f0/trojan/G2/outer      | M-inner1         |          582 |           96 |  0.654185 |           59 |    9.66479e-06 |
| main/f0/trojan/G2/outer      | M-inner1         |          582 |           96 |  0.461707 |           47 |    9.04484e-06 |
| main/f0/trojan/G2/outer      | M-inner1         |          582 |           96 |  0.318437 |           36 |    8.13426e-06 |
| main/f0/vless/G0/outer       | I-inner0         |          978 |          162 |  0.85727  |           68 |    9.08731e-06 |
| main/f0/vless/G0/outer       | I-inner0         |          978 |          162 |  0.926249 |           72 |    9.78723e-06 |
| main/f0/vless/G0/outer       | I-inner0         |          978 |          162 |  0.681071 |           59 |    9.57782e-06 |
| main/f0/vless/G0/outer       | I-inner0         |          978 |          162 |  0.412479 |           43 |    8.25269e-06 |
| main/f0/vless/G0/outer       | I-inner1         |          978 |          162 |  0.757979 |           67 |    9.55875e-06 |
| main/f0/vless/G0/outer       | I-inner1         |          978 |          162 |  0.896673 |           73 |    9.5984e-06  |
| main/f0/vless/G0/outer       | I-inner1         |          978 |          162 |  0.609624 |           57 |    8.38024e-06 |
| main/f0/vless/G0/outer       | I-inner1         |          978 |          162 |  0.390584 |           42 |    9.43436e-06 |
| main/f0/vless/G0/outer       | J-inner0         |          978 |          162 |  0.665354 |           62 |    9.87469e-06 |
| main/f0/vless/G0/outer       | J-inner0         |          978 |          162 |  0.772451 |           67 |    8.96498e-06 |
| main/f0/vless/G0/outer       | J-inner0         |          978 |          162 |  0.539026 |           53 |    8.43286e-06 |
| main/f0/vless/G0/outer       | J-inner0         |          978 |          162 |  0.359964 |           39 |    8.07587e-06 |
| main/f0/vless/G0/outer       | J-inner1         |          978 |          162 |  0.688945 |           62 |    9.96708e-06 |
| main/f0/vless/G0/outer       | J-inner1         |          978 |          162 |  0.814607 |           69 |    7.81753e-06 |
| main/f0/vless/G0/outer       | J-inner1         |          978 |          162 |  0.520352 |           53 |    9.85569e-06 |
| main/f0/vless/G0/outer       | J-inner1         |          978 |          162 |  0.371771 |           41 |    7.29914e-06 |
| main/f0/vless/G0/outer       | M-inner0         |          582 |           96 |  0.803364 |           63 |    9.2297e-06  |
| main/f0/vless/G0/outer       | M-inner0         |          582 |           96 |  0.871378 |           69 |    8.07892e-06 |
| main/f0/vless/G0/outer       | M-inner0         |          582 |           96 |  0.589206 |           53 |    9.41514e-06 |
| main/f0/vless/G0/outer       | M-inner0         |          582 |           96 |  0.357777 |           39 |    7.2829e-06  |
| main/f0/vless/G0/outer       | M-inner1         |          582 |           96 |  0.729076 |           62 |    9.57496e-06 |
| main/f0/vless/G0/outer       | M-inner1         |          582 |           96 |  0.831749 |           67 |    9.25276e-06 |
| main/f0/vless/G0/outer       | M-inner1         |          582 |           96 |  0.611627 |           55 |    9.87652e-06 |
| main/f0/vless/G0/outer       | M-inner1         |          582 |           96 |  0.334613 |           38 |    9.79354e-06 |
| main/f0/vless/G1/outer       | I-inner0         |          978 |          162 |  1.53752  |           98 |    9.45794e-06 |
| main/f0/vless/G1/outer       | I-inner0         |          978 |          162 |  1.66781  |          101 |    9.17615e-06 |
| main/f0/vless/G1/outer       | I-inner0         |          978 |          162 |  1.17202  |           84 |    9.98037e-06 |
| main/f0/vless/G1/outer       | I-inner0         |          978 |          162 |  0.732005 |           62 |    9.31844e-06 |
| main/f0/vless/G1/outer       | I-inner1         |          978 |          162 |  1.20827  |           85 |    9.80016e-06 |
| main/f0/vless/G1/outer       | I-inner1         |          978 |          162 |  1.34598  |           89 |    9.70479e-06 |
| main/f0/vless/G1/outer       | I-inner1         |          978 |          162 |  1.07577  |           80 |    9.869e-06   |
| main/f0/vless/G1/outer       | I-inner1         |          978 |          162 |  0.641346 |           58 |    9.8739e-06  |
| main/f0/vless/G1/outer       | J-inner0         |          978 |          162 |  1.3592   |           90 |    9.27428e-06 |
| main/f0/vless/G1/outer       | J-inner0         |          978 |          162 |  1.49775  |           97 |    9.50203e-06 |
| main/f0/vless/G1/outer       | J-inner0         |          978 |          162 |  0.967115 |           74 |    9.45079e-06 |
| main/f0/vless/G1/outer       | J-inner0         |          978 |          162 |  0.573508 |           53 |    9.50384e-06 |
| main/f0/vless/G1/outer       | J-inner1         |          978 |          162 |  0.984809 |           78 |    9.47751e-06 |
| main/f0/vless/G1/outer       | J-inner1         |          978 |          162 |  1.0838   |           83 |    9.62957e-06 |
| main/f0/vless/G1/outer       | J-inner1         |          978 |          162 |  0.830326 |           70 |    9.84958e-06 |
| main/f0/vless/G1/outer       | J-inner1         |          978 |          162 |  0.505537 |           51 |    9.68498e-06 |
| main/f0/vless/G1/outer       | M-inner0         |          582 |           96 |  0.856778 |           70 |    9.08879e-06 |
| main/f0/vless/G1/outer       | M-inner0         |          582 |           96 |  0.894074 |           75 |    9.3534e-06  |
| main/f0/vless/G1/outer       | M-inner0         |          582 |           96 |  0.654481 |           60 |    9.50714e-06 |
| main/f0/vless/G1/outer       | M-inner0         |          582 |           96 |  0.423036 |           46 |    9.31241e-06 |
| main/f0/vless/G1/outer       | M-inner1         |          582 |           96 |  0.716781 |           62 |    9.69082e-06 |
| main/f0/vless/G1/outer       | M-inner1         |          582 |           96 |  0.875993 |           70 |    8.14231e-06 |
| main/f0/vless/G1/outer       | M-inner1         |          582 |           96 |  0.582945 |           54 |    9.67574e-06 |
| main/f0/vless/G1/outer       | M-inner1         |          582 |           96 |  0.371848 |           40 |    9.71669e-06 |
| main/f0/vless/G2/outer       | I-inner0         |          978 |          162 |  0.795939 |           67 |    9.70658e-06 |
| main/f0/vless/G2/outer       | I-inner0         |          978 |          162 |  0.793017 |           68 |    9.77971e-06 |
| main/f0/vless/G2/outer       | I-inner0         |          978 |          162 |  0.589346 |           56 |    9.72255e-06 |
| main/f0/vless/G2/outer       | I-inner0         |          978 |          162 |  0.403025 |           42 |    9.73548e-06 |
| main/f0/vless/G2/outer       | I-inner1         |          978 |          162 |  0.746724 |           64 |    9.03498e-06 |
| main/f0/vless/G2/outer       | I-inner1         |          978 |          162 |  0.846465 |           69 |    9.11248e-06 |
| main/f0/vless/G2/outer       | I-inner1         |          978 |          162 |  0.568776 |           54 |    9.57163e-06 |
| main/f0/vless/G2/outer       | I-inner1         |          978 |          162 |  0.368224 |           40 |    8.68009e-06 |
| main/f0/vless/G2/outer       | J-inner0         |          978 |          162 |  0.628649 |           57 |    9.94686e-06 |
| main/f0/vless/G2/outer       | J-inner0         |          978 |          162 |  0.724036 |           62 |    8.43609e-06 |
| main/f0/vless/G2/outer       | J-inner0         |          978 |          162 |  0.494336 |           49 |    9.83516e-06 |
| main/f0/vless/G2/outer       | J-inner0         |          978 |          162 |  0.334749 |           37 |    8.96636e-06 |
| main/f0/vless/G2/outer       | J-inner1         |          978 |          162 |  0.53954  |           54 |    9.4302e-06  |
| main/f0/vless/G2/outer       | J-inner1         |          978 |          162 |  0.621205 |           58 |    9.34865e-06 |
| main/f0/vless/G2/outer       | J-inner1         |          978 |          162 |  0.425043 |           46 |    9.04756e-06 |
| main/f0/vless/G2/outer       | J-inner1         |          978 |          162 |  0.335796 |           38 |    7.69587e-06 |
| main/f0/vless/G2/outer       | M-inner0         |          582 |           96 |  0.571796 |           56 |    7.5541e-06  |
| main/f0/vless/G2/outer       | M-inner0         |          582 |           96 |  0.624896 |           58 |    9.29936e-06 |
| main/f0/vless/G2/outer       | M-inner0         |          582 |           96 |  0.456154 |           47 |    8.11946e-06 |
| main/f0/vless/G2/outer       | M-inner0         |          582 |           96 |  0.30702  |           35 |    9.3762e-06  |
| main/f0/vless/G2/outer       | M-inner1         |          582 |           96 |  0.516417 |           50 |    9.12939e-06 |
| main/f0/vless/G2/outer       | M-inner1         |          582 |           96 |  0.620145 |           54 |    9.42947e-06 |
| main/f0/vless/G2/outer       | M-inner1         |          582 |           96 |  0.445346 |           44 |    9.83944e-06 |
| main/f0/vless/G2/outer       | M-inner1         |          582 |           96 |  0.287234 |           35 |    5.56945e-06 |
| main/f0/vmess/G0/outer       | I-inner0         |          978 |          162 |  0.888105 |           72 |    8.13137e-06 |
| main/f0/vmess/G0/outer       | I-inner0         |          978 |          162 |  0.971647 |           77 |    8.05019e-06 |
| main/f0/vmess/G0/outer       | I-inner0         |          978 |          162 |  0.731905 |           62 |    9.00036e-06 |
| main/f0/vmess/G0/outer       | I-inner0         |          978 |          162 |  0.473192 |           47 |    8.59193e-06 |
| main/f0/vmess/G0/outer       | I-inner1         |          978 |          162 |  1.00452  |           77 |    9.0177e-06  |
| main/f0/vmess/G0/outer       | I-inner1         |          978 |          162 |  1.11311  |           83 |    9.20432e-06 |
| main/f0/vmess/G0/outer       | I-inner1         |          978 |          162 |  0.747466 |           64 |    9.54918e-06 |
| main/f0/vmess/G0/outer       | I-inner1         |          978 |          162 |  0.481548 |           48 |    8.8942e-06  |
| main/f0/vmess/G0/outer       | J-inner0         |          978 |          162 |  0.916945 |           72 |    9.50748e-06 |
| main/f0/vmess/G0/outer       | J-inner0         |          978 |          162 |  1.00264  |           77 |    9.96973e-06 |
| main/f0/vmess/G0/outer       | J-inner0         |          978 |          162 |  0.754357 |           63 |    9.02948e-06 |
| main/f0/vmess/G0/outer       | J-inner0         |          978 |          162 |  0.490242 |           48 |    9.38395e-06 |
| main/f0/vmess/G0/outer       | J-inner1         |          978 |          162 |  1.06986  |           79 |    9.96989e-06 |
| main/f0/vmess/G0/outer       | J-inner1         |          978 |          162 |  1.22879  |           84 |    9.87578e-06 |
| main/f0/vmess/G0/outer       | J-inner1         |          978 |          162 |  0.789065 |           66 |    9.73929e-06 |
| main/f0/vmess/G0/outer       | J-inner1         |          978 |          162 |  0.507486 |           49 |    8.29381e-06 |
| main/f0/vmess/G0/outer       | M-inner0         |          582 |           96 |  0.947866 |           70 |    9.1945e-06  |
| main/f0/vmess/G0/outer       | M-inner0         |          582 |           96 |  1.13785  |           76 |    9.8839e-06  |
| main/f0/vmess/G0/outer       | M-inner0         |          582 |           96 |  0.737544 |           60 |    8.33015e-06 |
| main/f0/vmess/G0/outer       | M-inner0         |          582 |           96 |  0.440012 |           44 |    6.14298e-06 |
| main/f0/vmess/G0/outer       | M-inner1         |          582 |           96 |  0.92838  |           69 |    9.7442e-06  |
| main/f0/vmess/G0/outer       | M-inner1         |          582 |           96 |  0.979601 |           73 |    8.77899e-06 |
| main/f0/vmess/G0/outer       | M-inner1         |          582 |           96 |  0.690261 |           59 |    9.52324e-06 |
| main/f0/vmess/G0/outer       | M-inner1         |          582 |           96 |  0.45219  |           44 |    8.42963e-06 |
| main/f0/vmess/G1/outer       | I-inner0         |          978 |          162 |  1.46726  |           93 |    9.61247e-06 |
| main/f0/vmess/G1/outer       | I-inner0         |          978 |          162 |  1.69917  |          103 |    9.5623e-06  |
| main/f0/vmess/G1/outer       | I-inner0         |          978 |          162 |  1.10286  |           79 |    9.98672e-06 |
| main/f0/vmess/G1/outer       | I-inner0         |          978 |          162 |  0.747832 |           61 |    9.48919e-06 |
| main/f0/vmess/G1/outer       | I-inner1         |          978 |          162 |  1.07172  |           79 |    9.62437e-06 |
| main/f0/vmess/G1/outer       | I-inner1         |          978 |          162 |  1.17923  |           83 |    8.34085e-06 |
| main/f0/vmess/G1/outer       | I-inner1         |          978 |          162 |  0.82297  |           67 |    9.29816e-06 |
| main/f0/vmess/G1/outer       | I-inner1         |          978 |          162 |  0.513777 |           50 |    8.68254e-06 |
| main/f0/vmess/G1/outer       | J-inner0         |          978 |          162 |  1.15342  |           84 |    9.59903e-06 |
| main/f0/vmess/G1/outer       | J-inner0         |          978 |          162 |  1.28995  |           90 |    9.14927e-06 |
| main/f0/vmess/G1/outer       | J-inner0         |          978 |          162 |  0.852018 |           69 |    9.22124e-06 |
| main/f0/vmess/G1/outer       | J-inner0         |          978 |          162 |  0.510141 |           49 |    7.29186e-06 |
| main/f0/vmess/G1/outer       | J-inner1         |          978 |          162 |  0.872497 |           71 |    9.88645e-06 |
| main/f0/vmess/G1/outer       | J-inner1         |          978 |          162 |  1.10046  |           79 |    8.91443e-06 |
| main/f0/vmess/G1/outer       | J-inner1         |          978 |          162 |  0.722458 |           62 |    9.8878e-06  |
| main/f0/vmess/G1/outer       | J-inner1         |          978 |          162 |  0.464096 |           46 |    9.51562e-06 |
| main/f0/vmess/G1/outer       | M-inner0         |          582 |           96 |  1.03754  |           75 |    8.71377e-06 |
| main/f0/vmess/G1/outer       | M-inner0         |          582 |           96 |  1.17184  |           81 |    9.50159e-06 |
| main/f0/vmess/G1/outer       | M-inner0         |          582 |           96 |  0.742953 |           62 |    9.60685e-06 |
| main/f0/vmess/G1/outer       | M-inner0         |          582 |           96 |  0.48288  |           46 |    6.74004e-06 |
| main/f0/vmess/G1/outer       | M-inner1         |          582 |           96 |  0.734653 |           63 |    9.66916e-06 |
| main/f0/vmess/G1/outer       | M-inner1         |          582 |           96 |  0.877009 |           69 |    9.84681e-06 |
| main/f0/vmess/G1/outer       | M-inner1         |          582 |           96 |  0.603273 |           56 |    9.2711e-06  |
| main/f0/vmess/G1/outer       | M-inner1         |          582 |           96 |  0.415745 |           42 |    9.51981e-06 |
| main/f0/vmess/G2/outer       | I-inner0         |          978 |          162 |  1.20633  |           83 |    9.23177e-06 |
| main/f0/vmess/G2/outer       | I-inner0         |          978 |          162 |  1.35408  |           90 |    9.86255e-06 |
| main/f0/vmess/G2/outer       | I-inner0         |          978 |          162 |  0.969597 |           72 |    9.64844e-06 |
| main/f0/vmess/G2/outer       | I-inner0         |          978 |          162 |  0.574702 |           52 |    8.15064e-06 |
| main/f0/vmess/G2/outer       | I-inner1         |          978 |          162 |  0.872242 |           70 |    9.34624e-06 |
| main/f0/vmess/G2/outer       | I-inner1         |          978 |          162 |  1.03307  |           76 |    9.5539e-06  |
| main/f0/vmess/G2/outer       | I-inner1         |          978 |          162 |  0.715536 |           61 |    9.73741e-06 |
| main/f0/vmess/G2/outer       | I-inner1         |          978 |          162 |  0.444026 |           45 |    9.02882e-06 |
| main/f0/vmess/G2/outer       | J-inner0         |          978 |          162 |  1.38335  |           90 |    8.58917e-06 |
| main/f0/vmess/G2/outer       | J-inner0         |          978 |          162 |  1.51818  |           96 |    9.78378e-06 |
| main/f0/vmess/G2/outer       | J-inner0         |          978 |          162 |  0.962977 |           73 |    8.36503e-06 |
| main/f0/vmess/G2/outer       | J-inner0         |          978 |          162 |  0.555729 |           52 |    9.82807e-06 |
| main/f0/vmess/G2/outer       | J-inner1         |          978 |          162 |  1.28593  |           89 |    9.21515e-06 |
| main/f0/vmess/G2/outer       | J-inner1         |          978 |          162 |  1.39814  |           95 |    9.41766e-06 |
| main/f0/vmess/G2/outer       | J-inner1         |          978 |          162 |  0.995381 |           76 |    9.59506e-06 |
| main/f0/vmess/G2/outer       | J-inner1         |          978 |          162 |  0.611806 |           56 |    9.46432e-06 |
| main/f0/vmess/G2/outer       | M-inner0         |          582 |           96 |  0.850733 |           69 |    9.48449e-06 |
| main/f0/vmess/G2/outer       | M-inner0         |          582 |           96 |  0.95869  |           74 |    9.40368e-06 |
| main/f0/vmess/G2/outer       | M-inner0         |          582 |           96 |  0.69715  |           59 |    9.2758e-06  |
| main/f0/vmess/G2/outer       | M-inner0         |          582 |           96 |  0.42744  |           43 |    8.72547e-06 |
| main/f0/vmess/G2/outer       | M-inner1         |          582 |           96 |  0.790579 |           66 |    8.22124e-06 |
| main/f0/vmess/G2/outer       | M-inner1         |          582 |           96 |  0.901782 |           71 |    9.80334e-06 |
| main/f0/vmess/G2/outer       | M-inner1         |          582 |           96 |  0.616188 |           56 |    9.68028e-06 |
| main/f0/vmess/G2/outer       | M-inner1         |          582 |           96 |  0.404944 |           43 |    8.06661e-06 |
| main/f1/shadowsocks/G0/outer | I-inner0         |          978 |          162 |  1.16565  |           92 |    8.93755e-06 |
| main/f1/shadowsocks/G0/outer | I-inner0         |          978 |          162 |  1.02753  |          102 |    9.24135e-06 |
| main/f1/shadowsocks/G0/outer | I-inner0         |          978 |          162 |  0.872574 |           76 |    8.34697e-06 |
| main/f1/shadowsocks/G0/outer | I-inner0         |          978 |          162 |  0.519174 |           55 |    9.92599e-06 |
| main/f1/shadowsocks/G0/outer | I-inner1         |          978 |          162 |  1.69283  |          108 |    9.1874e-06  |
| main/f1/shadowsocks/G0/outer | I-inner1         |          978 |          162 |  1.94767  |          119 |    9.66873e-06 |
| main/f1/shadowsocks/G0/outer | I-inner1         |          978 |          162 |  1.291    |           91 |    9.31976e-06 |
| main/f1/shadowsocks/G0/outer | I-inner1         |          978 |          162 |  0.811563 |           68 |    7.81622e-06 |
| main/f1/shadowsocks/G0/outer | J-inner0         |          978 |          162 |  0.887927 |           72 |    9.59957e-06 |
| main/f1/shadowsocks/G0/outer | J-inner0         |          978 |          162 |  1.01425  |           77 |    8.79268e-06 |
| main/f1/shadowsocks/G0/outer | J-inner0         |          978 |          162 |  0.657925 |           60 |    9.28617e-06 |
| main/f1/shadowsocks/G0/outer | J-inner0         |          978 |          162 |  0.436409 |           46 |    9.01804e-06 |
| main/f1/shadowsocks/G0/outer | J-inner1         |          978 |          162 |  0.96811  |           78 |    9.81594e-06 |
| main/f1/shadowsocks/G0/outer | J-inner1         |          978 |          162 |  1.10192  |           84 |    9.98563e-06 |
| main/f1/shadowsocks/G0/outer | J-inner1         |          978 |          162 |  0.756774 |           66 |    9.48824e-06 |
| main/f1/shadowsocks/G0/outer | J-inner1         |          978 |          162 |  0.500338 |           50 |    9.47417e-06 |
| main/f1/shadowsocks/G0/outer | M-inner0         |          582 |           96 |  0.429749 |           62 |    8.47789e-06 |
| main/f1/shadowsocks/G0/outer | M-inner0         |          582 |           96 |  1.38093  |           69 |    6.84068e-06 |
| main/f1/shadowsocks/G0/outer | M-inner0         |          582 |           96 |  0.340613 |           52 |    9.0634e-06  |
| main/f1/shadowsocks/G0/outer | M-inner0         |          582 |           96 |  0.234957 |           41 |    8.73155e-06 |
| main/f1/shadowsocks/G0/outer | M-inner1         |          582 |           96 |  0.637675 |           80 |    9.30352e-06 |
| main/f1/shadowsocks/G0/outer | M-inner1         |          582 |           96 |  0.768337 |           89 |    9.15921e-06 |
| main/f1/shadowsocks/G0/outer | M-inner1         |          582 |           96 |  0.533369 |           71 |    9.14338e-06 |
| main/f1/shadowsocks/G0/outer | M-inner1         |          582 |           96 |  0.280343 |           48 |    7.77525e-06 |
| main/f1/shadowsocks/G1/outer | I-inner0         |          978 |          162 |  1.1867   |           85 |    9.00932e-06 |
| main/f1/shadowsocks/G1/outer | I-inner0         |          978 |          162 |  1.32197  |           91 |    9.66677e-06 |
| main/f1/shadowsocks/G1/outer | I-inner0         |          978 |          162 |  0.897036 |           72 |    9.53182e-06 |
| main/f1/shadowsocks/G1/outer | I-inner0         |          978 |          162 |  0.666506 |           59 |    8.77145e-06 |
| main/f1/shadowsocks/G1/outer | I-inner1         |          978 |          162 |  1.19695  |           86 |    7.73001e-06 |
| main/f1/shadowsocks/G1/outer | I-inner1         |          978 |          162 |  1.40777  |           94 |    8.39453e-06 |
| main/f1/shadowsocks/G1/outer | I-inner1         |          978 |          162 |  0.887431 |           72 |    9.0705e-06  |
| main/f1/shadowsocks/G1/outer | I-inner1         |          978 |          162 |  0.597702 |           55 |    7.36677e-06 |
| main/f1/shadowsocks/G1/outer | J-inner0         |          978 |          162 |  1.06604  |           79 |    7.33425e-06 |
| main/f1/shadowsocks/G1/outer | J-inner0         |          978 |          162 |  1.18728  |           84 |    9.82526e-06 |
| main/f1/shadowsocks/G1/outer | J-inner0         |          978 |          162 |  0.770088 |           66 |    9.47526e-06 |
| main/f1/shadowsocks/G1/outer | J-inner0         |          978 |          162 |  0.469896 |           49 |    8.7602e-06  |
| main/f1/shadowsocks/G1/outer | J-inner1         |          978 |          162 |  1.17773  |           83 |    8.88353e-06 |
| main/f1/shadowsocks/G1/outer | J-inner1         |          978 |          162 |  1.27771  |           89 |    9.40456e-06 |
| main/f1/shadowsocks/G1/outer | J-inner1         |          978 |          162 |  0.868868 |           69 |    9.46935e-06 |
| main/f1/shadowsocks/G1/outer | J-inner1         |          978 |          162 |  0.537651 |           51 |    9.25405e-06 |
| main/f1/shadowsocks/G1/outer | M-inner0         |          582 |           96 |  0.994669 |           76 |    9.81382e-06 |
| main/f1/shadowsocks/G1/outer | M-inner0         |          582 |           96 |  1.13226  |           84 |    9.33432e-06 |
| main/f1/shadowsocks/G1/outer | M-inner0         |          582 |           96 |  0.765644 |           65 |    9.95891e-06 |
| main/f1/shadowsocks/G1/outer | M-inner0         |          582 |           96 |  0.430637 |           44 |    8.42745e-06 |
| main/f1/shadowsocks/G1/outer | M-inner1         |          582 |           96 |  0.935032 |           73 |    9.776e-06   |
| main/f1/shadowsocks/G1/outer | M-inner1         |          582 |           96 |  1.01982  |           76 |    9.73676e-06 |
| main/f1/shadowsocks/G1/outer | M-inner1         |          582 |           96 |  0.776057 |           63 |    9.39468e-06 |
| main/f1/shadowsocks/G1/outer | M-inner1         |          582 |           96 |  0.46163  |           45 |    9.41713e-06 |
| main/f1/shadowsocks/G2/outer | I-inner0         |          978 |          162 |  1.39698  |           92 |    8.51776e-06 |
| main/f1/shadowsocks/G2/outer | I-inner0         |          978 |          162 |  1.63368  |          100 |    9.92042e-06 |
| main/f1/shadowsocks/G2/outer | I-inner0         |          978 |          162 |  1.14393  |           83 |    7.81824e-06 |
| main/f1/shadowsocks/G2/outer | I-inner0         |          978 |          162 |  0.720797 |           62 |    8.45339e-06 |
| main/f1/shadowsocks/G2/outer | I-inner1         |          978 |          162 |  1.23643  |           86 |    9.70296e-06 |
| main/f1/shadowsocks/G2/outer | I-inner1         |          978 |          162 |  1.36685  |           92 |    9.94945e-06 |
| main/f1/shadowsocks/G2/outer | I-inner1         |          978 |          162 |  0.972357 |           75 |    9.77128e-06 |
| main/f1/shadowsocks/G2/outer | I-inner1         |          978 |          162 |  0.618677 |           55 |    8.75831e-06 |
| main/f1/shadowsocks/G2/outer | J-inner0         |          978 |          162 |  0.943754 |           75 |    9.55777e-06 |
| main/f1/shadowsocks/G2/outer | J-inner0         |          978 |          162 |  1.21744  |           85 |    9.64538e-06 |
| main/f1/shadowsocks/G2/outer | J-inner0         |          978 |          162 |  0.747898 |           64 |    8.34683e-06 |
| main/f1/shadowsocks/G2/outer | J-inner0         |          978 |          162 |  0.479376 |           46 |    8.55599e-06 |
| main/f1/shadowsocks/G2/outer | J-inner1         |          978 |          162 |  1.07809  |           81 |    8.36265e-06 |
| main/f1/shadowsocks/G2/outer | J-inner1         |          978 |          162 |  1.17067  |           86 |    9.57082e-06 |
| main/f1/shadowsocks/G2/outer | J-inner1         |          978 |          162 |  0.848658 |           68 |    8.7829e-06  |
| main/f1/shadowsocks/G2/outer | J-inner1         |          978 |          162 |  0.498656 |           49 |    9.77527e-06 |
| main/f1/shadowsocks/G2/outer | M-inner0         |          582 |           96 |  0.836984 |           70 |    8.99514e-06 |
| main/f1/shadowsocks/G2/outer | M-inner0         |          582 |           96 |  0.916067 |           74 |    9.41558e-06 |
| main/f1/shadowsocks/G2/outer | M-inner0         |          582 |           96 |  0.641953 |           59 |    8.77512e-06 |
| main/f1/shadowsocks/G2/outer | M-inner0         |          582 |           96 |  0.400707 |           43 |    8.11172e-06 |
| main/f1/shadowsocks/G2/outer | M-inner1         |          582 |           96 |  0.924468 |           73 |    9.761e-06   |
| main/f1/shadowsocks/G2/outer | M-inner1         |          582 |           96 |  1.02209  |           79 |    9.47819e-06 |
| main/f1/shadowsocks/G2/outer | M-inner1         |          582 |           96 |  0.728669 |           62 |    8.73615e-06 |
| main/f1/shadowsocks/G2/outer | M-inner1         |          582 |           96 |  0.397708 |           42 |    9.1535e-06  |
| main/f1/trojan/G0/outer      | I-inner0         |          978 |          162 |  0.974612 |           74 |    9.15258e-06 |
| main/f1/trojan/G0/outer      | I-inner0         |          978 |          162 |  1.07536  |           78 |    9.86175e-06 |
| main/f1/trojan/G0/outer      | I-inner0         |          978 |          162 |  0.798029 |           65 |    9.54384e-06 |
| main/f1/trojan/G0/outer      | I-inner0         |          978 |          162 |  0.6093   |           55 |    8.75283e-06 |
| main/f1/trojan/G0/outer      | I-inner1         |          978 |          162 |  1.2447   |           86 |    9.22899e-06 |
| main/f1/trojan/G0/outer      | I-inner1         |          978 |          162 |  1.42697  |           90 |    9.31125e-06 |
| main/f1/trojan/G0/outer      | I-inner1         |          978 |          162 |  0.878403 |           70 |    9.54316e-06 |
| main/f1/trojan/G0/outer      | I-inner1         |          978 |          162 |  0.563601 |           53 |    8.3912e-06  |
| main/f1/trojan/G0/outer      | J-inner0         |          978 |          162 |  0.934511 |           74 |    9.6865e-06  |
| main/f1/trojan/G0/outer      | J-inner0         |          978 |          162 |  1.10022  |           82 |    9.8582e-06  |
| main/f1/trojan/G0/outer      | J-inner0         |          978 |          162 |  0.704609 |           61 |    9.54956e-06 |
| main/f1/trojan/G0/outer      | J-inner0         |          978 |          162 |  0.481856 |           48 |    7.95657e-06 |
| main/f1/trojan/G0/outer      | J-inner1         |          978 |          162 |  1.06982  |           79 |    9.2711e-06  |
| main/f1/trojan/G0/outer      | J-inner1         |          978 |          162 |  1.24795  |           87 |    9.86742e-06 |
| main/f1/trojan/G0/outer      | J-inner1         |          978 |          162 |  0.812285 |           67 |    9.23776e-06 |
| main/f1/trojan/G0/outer      | J-inner1         |          978 |          162 |  0.51602  |           50 |    9.26137e-06 |
| main/f1/trojan/G0/outer      | M-inner0         |          582 |           96 |  0.548955 |           53 |    9.72183e-06 |
| main/f1/trojan/G0/outer      | M-inner0         |          582 |           96 |  0.565707 |           56 |    9.75752e-06 |
| main/f1/trojan/G0/outer      | M-inner0         |          582 |           96 |  0.430462 |           45 |    9.60448e-06 |
| main/f1/trojan/G0/outer      | M-inner0         |          582 |           96 |  0.286102 |           34 |    8.33949e-06 |
| main/f1/trojan/G0/outer      | M-inner1         |          582 |           96 |  1.01877  |           75 |    9.99745e-06 |
| main/f1/trojan/G0/outer      | M-inner1         |          582 |           96 |  1.18651  |           82 |    9.42072e-06 |
| main/f1/trojan/G0/outer      | M-inner1         |          582 |           96 |  0.793694 |           65 |    9.51377e-06 |
| main/f1/trojan/G0/outer      | M-inner1         |          582 |           96 |  0.486057 |           47 |    9.70806e-06 |
| main/f1/trojan/G1/outer      | I-inner0         |          978 |          162 |  1.44259  |           96 |    9.72052e-06 |
| main/f1/trojan/G1/outer      | I-inner0         |          978 |          162 |  1.54805  |          101 |    9.73713e-06 |
| main/f1/trojan/G1/outer      | I-inner0         |          978 |          162 |  1.23081  |           86 |    8.89785e-06 |
| main/f1/trojan/G1/outer      | I-inner0         |          978 |          162 |  0.785514 |           65 |    9.63726e-06 |
| main/f1/trojan/G1/outer      | I-inner1         |          978 |          162 |  1.13629  |           83 |    9.90304e-06 |
| main/f1/trojan/G1/outer      | I-inner1         |          978 |          162 |  1.37224  |           92 |    9.26229e-06 |
| main/f1/trojan/G1/outer      | I-inner1         |          978 |          162 |  0.841536 |           69 |    9.38372e-06 |
| main/f1/trojan/G1/outer      | I-inner1         |          978 |          162 |  0.53354  |           51 |    9.73402e-06 |
| main/f1/trojan/G1/outer      | J-inner0         |          978 |          162 |  0.926906 |           73 |    9.79702e-06 |
| main/f1/trojan/G1/outer      | J-inner0         |          978 |          162 |  1.0425   |           79 |    9.63656e-06 |
| main/f1/trojan/G1/outer      | J-inner0         |          978 |          162 |  0.681349 |           60 |    9.25867e-06 |
| main/f1/trojan/G1/outer      | J-inner0         |          978 |          162 |  0.407166 |           42 |    9.35592e-06 |
| main/f1/trojan/G1/outer      | J-inner1         |          978 |          162 |  1.06524  |           79 |    9.90469e-06 |
| main/f1/trojan/G1/outer      | J-inner1         |          978 |          162 |  1.24031  |           87 |    8.28812e-06 |
| main/f1/trojan/G1/outer      | J-inner1         |          978 |          162 |  0.768619 |           64 |    9.06654e-06 |
| main/f1/trojan/G1/outer      | J-inner1         |          978 |          162 |  0.446921 |           46 |    8.95004e-06 |
| main/f1/trojan/G1/outer      | M-inner0         |          582 |           96 |  0.863574 |           70 |    8.3122e-06  |
| main/f1/trojan/G1/outer      | M-inner0         |          582 |           96 |  0.946528 |           75 |    9.34178e-06 |
| main/f1/trojan/G1/outer      | M-inner0         |          582 |           96 |  0.609713 |           56 |    9.81715e-06 |
| main/f1/trojan/G1/outer      | M-inner0         |          582 |           96 |  0.416343 |           43 |    8.74094e-06 |
| main/f1/trojan/G1/outer      | M-inner1         |          582 |           96 |  0.840188 |           68 |    9.62222e-06 |
| main/f1/trojan/G1/outer      | M-inner1         |          582 |           96 |  1.0316   |           75 |    9.39718e-06 |
| main/f1/trojan/G1/outer      | M-inner1         |          582 |           96 |  0.715291 |           61 |    9.30859e-06 |
| main/f1/trojan/G1/outer      | M-inner1         |          582 |           96 |  0.439826 |           45 |    9.6134e-06  |
| main/f1/trojan/G2/outer      | I-inner0         |          978 |          162 |  0.799153 |           66 |    8.27444e-06 |
| main/f1/trojan/G2/outer      | I-inner0         |          978 |          162 |  0.903082 |           71 |    9.89929e-06 |
| main/f1/trojan/G2/outer      | I-inner0         |          978 |          162 |  0.626989 |           56 |    9.47532e-06 |
| main/f1/trojan/G2/outer      | I-inner0         |          978 |          162 |  0.448016 |           45 |    8.69023e-06 |
| main/f1/trojan/G2/outer      | I-inner1         |          978 |          162 |  0.873428 |           72 |    9.47725e-06 |
| main/f1/trojan/G2/outer      | I-inner1         |          978 |          162 |  1.05476  |           80 |    9.26847e-06 |
| main/f1/trojan/G2/outer      | I-inner1         |          978 |          162 |  0.732041 |           63 |    9.05295e-06 |
| main/f1/trojan/G2/outer      | I-inner1         |          978 |          162 |  0.48671  |           48 |    9.49434e-06 |
| main/f1/trojan/G2/outer      | J-inner0         |          978 |          162 |  0.838006 |           70 |    9.46849e-06 |
| main/f1/trojan/G2/outer      | J-inner0         |          978 |          162 |  1.00772  |           78 |    9.52891e-06 |
| main/f1/trojan/G2/outer      | J-inner0         |          978 |          162 |  0.652414 |           60 |    9.58555e-06 |
| main/f1/trojan/G2/outer      | J-inner0         |          978 |          162 |  0.475488 |           44 |    9.07659e-06 |
| main/f1/trojan/G2/outer      | J-inner1         |          978 |          162 |  1.00246  |           74 |    8.27017e-06 |
| main/f1/trojan/G2/outer      | J-inner1         |          978 |          162 |  1.13348  |           81 |    9.09018e-06 |
| main/f1/trojan/G2/outer      | J-inner1         |          978 |          162 |  0.760384 |           62 |    9.85654e-06 |
| main/f1/trojan/G2/outer      | J-inner1         |          978 |          162 |  0.434106 |           44 |    9.51319e-06 |
| main/f1/trojan/G2/outer      | M-inner0         |          582 |           96 |  0.540065 |           55 |    9.29264e-06 |
| main/f1/trojan/G2/outer      | M-inner0         |          582 |           96 |  0.58242  |           58 |    9.01546e-06 |
| main/f1/trojan/G2/outer      | M-inner0         |          582 |           96 |  0.449802 |           47 |    9.41432e-06 |
| main/f1/trojan/G2/outer      | M-inner0         |          582 |           96 |  0.331278 |           38 |    7.70614e-06 |
| main/f1/trojan/G2/outer      | M-inner1         |          582 |           96 |  0.685762 |           59 |    9.05089e-06 |
| main/f1/trojan/G2/outer      | M-inner1         |          582 |           96 |  0.720488 |           62 |    9.14291e-06 |
| main/f1/trojan/G2/outer      | M-inner1         |          582 |           96 |  0.5733   |           52 |    9.428e-06   |
| main/f1/trojan/G2/outer      | M-inner1         |          582 |           96 |  0.337342 |           37 |    9.75088e-06 |
| main/f1/vless/G0/outer       | I-inner0         |          978 |          162 |  1.00646  |           77 |    8.70112e-06 |
| main/f1/vless/G0/outer       | I-inner0         |          978 |          162 |  1.1724   |           85 |    9.41577e-06 |
| main/f1/vless/G0/outer       | I-inner0         |          978 |          162 |  0.746766 |           64 |    7.1863e-06  |
| main/f1/vless/G0/outer       | I-inner0         |          978 |          162 |  0.4379   |           45 |    9.78196e-06 |
| main/f1/vless/G0/outer       | I-inner1         |          978 |          162 |  1.0872   |           81 |    9.86766e-06 |
| main/f1/vless/G0/outer       | I-inner1         |          978 |          162 |  1.23871  |           86 |    9.61985e-06 |
| main/f1/vless/G0/outer       | I-inner1         |          978 |          162 |  0.891981 |           71 |    8.65556e-06 |
| main/f1/vless/G0/outer       | I-inner1         |          978 |          162 |  0.506614 |           50 |    9.94967e-06 |
| main/f1/vless/G0/outer       | J-inner0         |          978 |          162 |  0.950095 |           75 |    9.73359e-06 |
| main/f1/vless/G0/outer       | J-inner0         |          978 |          162 |  0.989519 |           76 |    9.41856e-06 |
| main/f1/vless/G0/outer       | J-inner0         |          978 |          162 |  0.704862 |           60 |    9.70942e-06 |
| main/f1/vless/G0/outer       | J-inner0         |          978 |          162 |  0.434969 |           43 |    9.85851e-06 |
| main/f1/vless/G0/outer       | J-inner1         |          978 |          162 |  0.940598 |           72 |    9.60556e-06 |
| main/f1/vless/G0/outer       | J-inner1         |          978 |          162 |  1.09375  |           79 |    8.98537e-06 |
| main/f1/vless/G0/outer       | J-inner1         |          978 |          162 |  0.723514 |           61 |    9.02223e-06 |
| main/f1/vless/G0/outer       | J-inner1         |          978 |          162 |  0.440929 |           44 |    8.11935e-06 |
| main/f1/vless/G0/outer       | M-inner0         |          582 |           96 |  0.790639 |           65 |    8.93251e-06 |
| main/f1/vless/G0/outer       | M-inner0         |          582 |           96 |  0.898001 |           72 |    7.89606e-06 |
| main/f1/vless/G0/outer       | M-inner0         |          582 |           96 |  0.609628 |           55 |    9.22588e-06 |
| main/f1/vless/G0/outer       | M-inner0         |          582 |           96 |  0.399018 |           39 |    8.6068e-06  |
| main/f1/vless/G0/outer       | M-inner1         |          582 |           96 |  0.784626 |           64 |    9.90929e-06 |
| main/f1/vless/G0/outer       | M-inner1         |          582 |           96 |  0.911844 |           69 |    9.46021e-06 |
| main/f1/vless/G0/outer       | M-inner1         |          582 |           96 |  0.651424 |           56 |    9.69635e-06 |
| main/f1/vless/G0/outer       | M-inner1         |          582 |           96 |  0.358733 |           39 |    9.90135e-06 |
| main/f1/vless/G1/outer       | I-inner0         |          978 |          162 |  1.431    |           92 |    9.9165e-06  |
| main/f1/vless/G1/outer       | I-inner0         |          978 |          162 |  1.70831  |          102 |    9.82301e-06 |
| main/f1/vless/G1/outer       | I-inner0         |          978 |          162 |  1.1166   |           80 |    8.1615e-06  |
| main/f1/vless/G1/outer       | I-inner0         |          978 |          162 |  0.620051 |           56 |    9.71929e-06 |
| main/f1/vless/G1/outer       | I-inner1         |          978 |          162 |  1.57562  |           99 |    8.95497e-06 |
| main/f1/vless/G1/outer       | I-inner1         |          978 |          162 |  1.77647  |          108 |    9.66688e-06 |
| main/f1/vless/G1/outer       | I-inner1         |          978 |          162 |  1.15614  |           83 |    8.80254e-06 |
| main/f1/vless/G1/outer       | I-inner1         |          978 |          162 |  0.705072 |           61 |    9.18062e-06 |
| main/f1/vless/G1/outer       | J-inner0         |          978 |          162 |  0.990271 |           77 |    7.89608e-06 |
| main/f1/vless/G1/outer       | J-inner0         |          978 |          162 |  1.11527  |           84 |    9.5659e-06  |
| main/f1/vless/G1/outer       | J-inner0         |          978 |          162 |  0.796967 |           66 |    8.03524e-06 |
| main/f1/vless/G1/outer       | J-inner0         |          978 |          162 |  0.463258 |           46 |    9.15583e-06 |
| main/f1/vless/G1/outer       | J-inner1         |          978 |          162 |  1.19675  |           83 |    9.34174e-06 |
| main/f1/vless/G1/outer       | J-inner1         |          978 |          162 |  1.28184  |           87 |    9.36478e-06 |
| main/f1/vless/G1/outer       | J-inner1         |          978 |          162 |  0.94088  |           72 |    8.49629e-06 |
| main/f1/vless/G1/outer       | J-inner1         |          978 |          162 |  0.571096 |           52 |    8.35457e-06 |
| main/f1/vless/G1/outer       | M-inner0         |          582 |           96 |  0.779243 |           65 |    9.92588e-06 |
| main/f1/vless/G1/outer       | M-inner0         |          582 |           96 |  0.904339 |           71 |    9.17848e-06 |
| main/f1/vless/G1/outer       | M-inner0         |          582 |           96 |  0.593174 |           55 |    9.70355e-06 |
| main/f1/vless/G1/outer       | M-inner0         |          582 |           96 |  0.340534 |           38 |    9.25968e-06 |
| main/f1/vless/G1/outer       | M-inner1         |          582 |           96 |  0.885677 |           71 |    9.98668e-06 |
| main/f1/vless/G1/outer       | M-inner1         |          582 |           96 |  0.908626 |           73 |    9.52973e-06 |
| main/f1/vless/G1/outer       | M-inner1         |          582 |           96 |  0.766208 |           62 |    7.97784e-06 |
| main/f1/vless/G1/outer       | M-inner1         |          582 |           96 |  0.471668 |           46 |    9.03868e-06 |
| main/f1/vless/G2/outer       | I-inner0         |          978 |          162 |  0.851785 |           69 |    9.69718e-06 |
| main/f1/vless/G2/outer       | I-inner0         |          978 |          162 |  0.860704 |           71 |    8.86517e-06 |
| main/f1/vless/G2/outer       | I-inner0         |          978 |          162 |  0.660099 |           59 |    9.77307e-06 |
| main/f1/vless/G2/outer       | I-inner0         |          978 |          162 |  0.426126 |           45 |    8.90801e-06 |
| main/f1/vless/G2/outer       | I-inner1         |          978 |          162 |  0.911753 |           71 |    8.71635e-06 |
| main/f1/vless/G2/outer       | I-inner1         |          978 |          162 |  0.983767 |           75 |    9.6336e-06  |
| main/f1/vless/G2/outer       | I-inner1         |          978 |          162 |  0.728975 |           61 |    8.76101e-06 |
| main/f1/vless/G2/outer       | I-inner1         |          978 |          162 |  0.494388 |           47 |    9.77594e-06 |
| main/f1/vless/G2/outer       | J-inner0         |          978 |          162 |  0.782636 |           64 |    9.88617e-06 |
| main/f1/vless/G2/outer       | J-inner0         |          978 |          162 |  0.835067 |           67 |    9.38099e-06 |
| main/f1/vless/G2/outer       | J-inner0         |          978 |          162 |  0.599792 |           54 |    8.80884e-06 |
| main/f1/vless/G2/outer       | J-inner0         |          978 |          162 |  0.36904  |           40 |    7.18649e-06 |
| main/f1/vless/G2/outer       | J-inner1         |          978 |          162 |  0.771692 |           67 |    9.98372e-06 |
| main/f1/vless/G2/outer       | J-inner1         |          978 |          162 |  0.862401 |           72 |    9.37308e-06 |
| main/f1/vless/G2/outer       | J-inner1         |          978 |          162 |  0.606091 |           56 |    9.52967e-06 |
| main/f1/vless/G2/outer       | J-inner1         |          978 |          162 |  0.38284  |           41 |    8.97252e-06 |
| main/f1/vless/G2/outer       | M-inner0         |          582 |           96 |  0.559226 |           54 |    8.74175e-06 |
| main/f1/vless/G2/outer       | M-inner0         |          582 |           96 |  0.564996 |           56 |    9.44217e-06 |
| main/f1/vless/G2/outer       | M-inner0         |          582 |           96 |  0.458427 |           47 |    8.8135e-06  |
| main/f1/vless/G2/outer       | M-inner0         |          582 |           96 |  0.303849 |           36 |    7.59978e-06 |
| main/f1/vless/G2/outer       | M-inner1         |          582 |           96 |  0.659546 |           58 |    9.62678e-06 |
| main/f1/vless/G2/outer       | M-inner1         |          582 |           96 |  0.710209 |           61 |    9.66478e-06 |
| main/f1/vless/G2/outer       | M-inner1         |          582 |           96 |  0.511982 |           50 |    9.55102e-06 |
| main/f1/vless/G2/outer       | M-inner1         |          582 |           96 |  0.370086 |           39 |    7.32277e-06 |
| main/f1/vmess/G0/outer       | I-inner0         |          978 |          162 |  0.794197 |           67 |    9.75391e-06 |
| main/f1/vmess/G0/outer       | I-inner0         |          978 |          162 |  0.90284  |           72 |    9.71972e-06 |
| main/f1/vmess/G0/outer       | I-inner0         |          978 |          162 |  0.672048 |           60 |    9.315e-06   |
| main/f1/vmess/G0/outer       | I-inner0         |          978 |          162 |  0.400289 |           43 |    9.46797e-06 |
| main/f1/vmess/G0/outer       | I-inner1         |          978 |          162 |  1.31627  |           89 |    9.65816e-06 |
| main/f1/vmess/G0/outer       | I-inner1         |          978 |          162 |  1.46245  |           96 |    9.86285e-06 |
| main/f1/vmess/G0/outer       | I-inner1         |          978 |          162 |  0.916546 |           72 |    8.85855e-06 |
| main/f1/vmess/G0/outer       | I-inner1         |          978 |          162 |  0.569713 |           54 |    9.90916e-06 |
| main/f1/vmess/G0/outer       | J-inner0         |          978 |          162 |  0.741838 |           64 |    9.64258e-06 |
| main/f1/vmess/G0/outer       | J-inner0         |          978 |          162 |  0.963208 |           72 |    9.66804e-06 |
| main/f1/vmess/G0/outer       | J-inner0         |          978 |          162 |  0.637307 |           58 |    9.81355e-06 |
| main/f1/vmess/G0/outer       | J-inner0         |          978 |          162 |  0.407417 |           44 |    8.29212e-06 |
| main/f1/vmess/G0/outer       | J-inner1         |          978 |          162 |  1.11367  |           81 |    8.88886e-06 |
| main/f1/vmess/G0/outer       | J-inner1         |          978 |          162 |  1.26761  |           89 |    8.75456e-06 |
| main/f1/vmess/G0/outer       | J-inner1         |          978 |          162 |  0.906803 |           69 |    7.67786e-06 |
| main/f1/vmess/G0/outer       | J-inner1         |          978 |          162 |  0.541915 |           50 |    9.11578e-06 |
| main/f1/vmess/G0/outer       | M-inner0         |          582 |           96 |  0.745628 |           64 |    9.76381e-06 |
| main/f1/vmess/G0/outer       | M-inner0         |          582 |           96 |  0.842441 |           69 |    9.72617e-06 |
| main/f1/vmess/G0/outer       | M-inner0         |          582 |           96 |  0.58639  |           55 |    7.41714e-06 |
| main/f1/vmess/G0/outer       | M-inner0         |          582 |           96 |  0.345811 |           39 |    8.78476e-06 |
| main/f1/vmess/G0/outer       | M-inner1         |          582 |           96 |  1.08343  |           79 |    7.51231e-06 |
| main/f1/vmess/G0/outer       | M-inner1         |          582 |           96 |  1.2214   |           85 |    9.15762e-06 |
| main/f1/vmess/G0/outer       | M-inner1         |          582 |           96 |  0.804182 |           65 |    9.61507e-06 |
| main/f1/vmess/G0/outer       | M-inner1         |          582 |           96 |  0.497527 |           49 |    9.96863e-06 |
| main/f1/vmess/G1/outer       | I-inner0         |          978 |          162 |  1.17509  |           84 |    9.7923e-06  |
| main/f1/vmess/G1/outer       | I-inner0         |          978 |          162 |  1.30844  |           91 |    8.64217e-06 |
| main/f1/vmess/G1/outer       | I-inner0         |          978 |          162 |  0.849675 |           69 |    9.89605e-06 |
| main/f1/vmess/G1/outer       | I-inner0         |          978 |          162 |  0.52646  |           51 |    9.20104e-06 |
| main/f1/vmess/G1/outer       | I-inner1         |          978 |          162 |  0.997422 |           80 |    9.3888e-06  |
| main/f1/vmess/G1/outer       | I-inner1         |          978 |          162 |  1.10918  |           85 |    8.43564e-06 |
| main/f1/vmess/G1/outer       | I-inner1         |          978 |          162 |  0.871104 |           71 |    8.83048e-06 |
| main/f1/vmess/G1/outer       | I-inner1         |          978 |          162 |  0.525681 |           52 |    9.27757e-06 |
| main/f1/vmess/G1/outer       | J-inner0         |          978 |          162 |  0.937449 |           75 |    9.94894e-06 |
| main/f1/vmess/G1/outer       | J-inner0         |          978 |          162 |  0.948151 |           77 |    9.95561e-06 |
| main/f1/vmess/G1/outer       | J-inner0         |          978 |          162 |  0.774856 |           67 |    7.68967e-06 |
| main/f1/vmess/G1/outer       | J-inner0         |          978 |          162 |  0.471198 |           48 |    7.96771e-06 |
| main/f1/vmess/G1/outer       | J-inner1         |          978 |          162 |  1.04268  |           79 |    8.54896e-06 |
| main/f1/vmess/G1/outer       | J-inner1         |          978 |          162 |  1.1139   |           82 |    9.75216e-06 |
| main/f1/vmess/G1/outer       | J-inner1         |          978 |          162 |  0.808932 |           67 |    9.5715e-06  |
| main/f1/vmess/G1/outer       | J-inner1         |          978 |          162 |  0.520647 |           50 |    8.32941e-06 |
| main/f1/vmess/G1/outer       | M-inner0         |          582 |           96 |  0.826438 |           68 |    8.07482e-06 |
| main/f1/vmess/G1/outer       | M-inner0         |          582 |           96 |  0.9401   |           74 |    8.84568e-06 |
| main/f1/vmess/G1/outer       | M-inner0         |          582 |           96 |  0.619034 |           56 |    8.84559e-06 |
| main/f1/vmess/G1/outer       | M-inner0         |          582 |           96 |  0.399476 |           42 |    7.2009e-06  |
| main/f1/vmess/G1/outer       | M-inner1         |          582 |           96 |  0.801098 |           68 |    9.31902e-06 |
| main/f1/vmess/G1/outer       | M-inner1         |          582 |           96 |  0.914442 |           73 |    9.77508e-06 |
| main/f1/vmess/G1/outer       | M-inner1         |          582 |           96 |  0.607058 |           57 |    8.89559e-06 |
| main/f1/vmess/G1/outer       | M-inner1         |          582 |           96 |  0.376062 |           42 |    8.33018e-06 |
| main/f1/vmess/G2/outer       | I-inner0         |          978 |          162 |  0.878425 |           69 |    9.89277e-06 |
| main/f1/vmess/G2/outer       | I-inner0         |          978 |          162 |  0.999907 |           74 |    9.77035e-06 |
| main/f1/vmess/G2/outer       | I-inner0         |          978 |          162 |  0.789097 |           66 |    8.72699e-06 |
| main/f1/vmess/G2/outer       | I-inner0         |          978 |          162 |  0.496414 |           49 |    9.19516e-06 |
| main/f1/vmess/G2/outer       | I-inner1         |          978 |          162 |  1.04599  |           81 |    9.43666e-06 |
| main/f1/vmess/G2/outer       | I-inner1         |          978 |          162 |  1.20683  |           88 |    9.1528e-06  |
| main/f1/vmess/G2/outer       | I-inner1         |          978 |          162 |  0.843063 |           70 |    9.723e-06   |
| main/f1/vmess/G2/outer       | I-inner1         |          978 |          162 |  0.614886 |           57 |    7.02771e-06 |
| main/f1/vmess/G2/outer       | J-inner0         |          978 |          162 |  1.14488  |           85 |    8.32908e-06 |
| main/f1/vmess/G2/outer       | J-inner0         |          978 |          162 |  1.24447  |           90 |    9.59565e-06 |
| main/f1/vmess/G2/outer       | J-inner0         |          978 |          162 |  0.880751 |           71 |    9.66004e-06 |
| main/f1/vmess/G2/outer       | J-inner0         |          978 |          162 |  0.514506 |           51 |    8.6191e-06  |
| main/f1/vmess/G2/outer       | J-inner1         |          978 |          162 |  1.33008  |           89 |    8.91475e-06 |
| main/f1/vmess/G2/outer       | J-inner1         |          978 |          162 |  1.42121  |           95 |    9.80191e-06 |
| main/f1/vmess/G2/outer       | J-inner1         |          978 |          162 |  0.975745 |           74 |    9.62373e-06 |
| main/f1/vmess/G2/outer       | J-inner1         |          978 |          162 |  0.572626 |           53 |    8.9761e-06  |
| main/f1/vmess/G2/outer       | M-inner0         |          582 |           96 |  0.695298 |           59 |    8.95693e-06 |
| main/f1/vmess/G2/outer       | M-inner0         |          582 |           96 |  0.882232 |           66 |    9.20064e-06 |
| main/f1/vmess/G2/outer       | M-inner0         |          582 |           96 |  0.536643 |           51 |    8.19041e-06 |
| main/f1/vmess/G2/outer       | M-inner0         |          582 |           96 |  0.346854 |           38 |    8.85476e-06 |
| main/f1/vmess/G2/outer       | M-inner1         |          582 |           96 |  0.942338 |           73 |    8.72098e-06 |
| main/f1/vmess/G2/outer       | M-inner1         |          582 |           96 |  1.0395   |           78 |    9.41174e-06 |
| main/f1/vmess/G2/outer       | M-inner1         |          582 |           96 |  0.697134 |           62 |    9.6581e-06  |
| main/f1/vmess/G2/outer       | M-inner1         |          582 |           96 |  0.485484 |           47 |    9.91824e-06 |
| main/f2/shadowsocks/G0/outer | I-inner0         |          978 |          162 |  1.45533  |           96 |    9.70365e-06 |
| main/f2/shadowsocks/G0/outer | I-inner0         |          978 |          162 |  1.78447  |          107 |    9.26608e-06 |
| main/f2/shadowsocks/G0/outer | I-inner0         |          978 |          162 |  1.12939  |           83 |    8.13116e-06 |
| main/f2/shadowsocks/G0/outer | I-inner0         |          978 |          162 |  0.679479 |           61 |    8.92085e-06 |
| main/f2/shadowsocks/G0/outer | I-inner1         |          978 |          162 |  1.51952  |           98 |    9.33251e-06 |
| main/f2/shadowsocks/G0/outer | I-inner1         |          978 |          162 |  1.59316  |          101 |    9.91116e-06 |
| main/f2/shadowsocks/G0/outer | I-inner1         |          978 |          162 |  1.22983  |           87 |    9.46171e-06 |
| main/f2/shadowsocks/G0/outer | I-inner1         |          978 |          162 |  0.715958 |           62 |    9.33838e-06 |
| main/f2/shadowsocks/G0/outer | J-inner0         |          978 |          162 |  1.02033  |           79 |    9.85238e-06 |
| main/f2/shadowsocks/G0/outer | J-inner0         |          978 |          162 |  1.06279  |           82 |    9.7881e-06  |
| main/f2/shadowsocks/G0/outer | J-inner0         |          978 |          162 |  0.752188 |           66 |    9.92796e-06 |
| main/f2/shadowsocks/G0/outer | J-inner0         |          978 |          162 |  0.493264 |           50 |    8.20047e-06 |
| main/f2/shadowsocks/G0/outer | J-inner1         |          978 |          162 |  0.933738 |           75 |    9.96989e-06 |
| main/f2/shadowsocks/G0/outer | J-inner1         |          978 |          162 |  1.02596  |           79 |    9.5602e-06  |
| main/f2/shadowsocks/G0/outer | J-inner1         |          978 |          162 |  0.753681 |           65 |    9.98022e-06 |
| main/f2/shadowsocks/G0/outer | J-inner1         |          978 |          162 |  0.482507 |           49 |    8.84883e-06 |
| main/f2/shadowsocks/G0/outer | M-inner0         |          582 |           96 |  0.879409 |           72 |    9.84802e-06 |
| main/f2/shadowsocks/G0/outer | M-inner0         |          582 |           96 |  0.993561 |           79 |    8.95393e-06 |
| main/f2/shadowsocks/G0/outer | M-inner0         |          582 |           96 |  0.672655 |           61 |    8.0397e-06  |
| main/f2/shadowsocks/G0/outer | M-inner0         |          582 |           96 |  0.392679 |           43 |    8.45186e-06 |
| main/f2/shadowsocks/G0/outer | M-inner1         |          582 |           96 |  1.13048  |           82 |    8.86731e-06 |
| main/f2/shadowsocks/G0/outer | M-inner1         |          582 |           96 |  1.31462  |           90 |    8.73063e-06 |
| main/f2/shadowsocks/G0/outer | M-inner1         |          582 |           96 |  0.859227 |           69 |    8.71846e-06 |
| main/f2/shadowsocks/G0/outer | M-inner1         |          582 |           96 |  0.51802  |           51 |    6.17175e-06 |
| main/f2/shadowsocks/G1/outer | I-inner0         |          978 |          162 |  1.11181  |           83 |    9.58636e-06 |
| main/f2/shadowsocks/G1/outer | I-inner0         |          978 |          162 |  1.31222  |           90 |    9.03614e-06 |
| main/f2/shadowsocks/G1/outer | I-inner0         |          978 |          162 |  0.923856 |           74 |    8.52134e-06 |
| main/f2/shadowsocks/G1/outer | I-inner0         |          978 |          162 |  0.678893 |           60 |    9.60152e-06 |
| main/f2/shadowsocks/G1/outer | I-inner1         |          978 |          162 |  1.15483  |           84 |    9.90734e-06 |
| main/f2/shadowsocks/G1/outer | I-inner1         |          978 |          162 |  1.32718  |           90 |    9.96843e-06 |
| main/f2/shadowsocks/G1/outer | I-inner1         |          978 |          162 |  0.968926 |           75 |    9.83183e-06 |
| main/f2/shadowsocks/G1/outer | I-inner1         |          978 |          162 |  0.578352 |           54 |    9.60295e-06 |
| main/f2/shadowsocks/G1/outer | J-inner0         |          978 |          162 |  0.926013 |           75 |    9.97847e-06 |
| main/f2/shadowsocks/G1/outer | J-inner0         |          978 |          162 |  1.07616  |           82 |    9.80711e-06 |
| main/f2/shadowsocks/G1/outer | J-inner0         |          978 |          162 |  0.857825 |           71 |    9.3942e-06  |
| main/f2/shadowsocks/G1/outer | J-inner0         |          978 |          162 |  0.485374 |           49 |    8.33097e-06 |
| main/f2/shadowsocks/G1/outer | J-inner1         |          978 |          162 |  0.900243 |           72 |    9.98831e-06 |
| main/f2/shadowsocks/G1/outer | J-inner1         |          978 |          162 |  1.07518  |           79 |    9.56975e-06 |
| main/f2/shadowsocks/G1/outer | J-inner1         |          978 |          162 |  0.678974 |           61 |    7.97199e-06 |
| main/f2/shadowsocks/G1/outer | J-inner1         |          978 |          162 |  0.45395  |           46 |    8.16379e-06 |
| main/f2/shadowsocks/G1/outer | M-inner0         |          582 |           96 |  1.09856  |           82 |    9.44192e-06 |
| main/f2/shadowsocks/G1/outer | M-inner0         |          582 |           96 |  1.19511  |           87 |    9.8054e-06  |
| main/f2/shadowsocks/G1/outer | M-inner0         |          582 |           96 |  0.862545 |           69 |    9.78309e-06 |
| main/f2/shadowsocks/G1/outer | M-inner0         |          582 |           96 |  0.499038 |           49 |    9.91921e-06 |
| main/f2/shadowsocks/G1/outer | M-inner1         |          582 |           96 |  0.775468 |           64 |    9.4828e-06  |
| main/f2/shadowsocks/G1/outer | M-inner1         |          582 |           96 |  0.911062 |           70 |    9.59733e-06 |
| main/f2/shadowsocks/G1/outer | M-inner1         |          582 |           96 |  0.639005 |           58 |    7.95198e-06 |
| main/f2/shadowsocks/G1/outer | M-inner1         |          582 |           96 |  0.447246 |           46 |    7.91825e-06 |
| main/f2/shadowsocks/G2/outer | I-inner0         |          978 |          162 |  1.60649  |          101 |    9.54889e-06 |
| main/f2/shadowsocks/G2/outer | I-inner0         |          978 |          162 |  1.71695  |          107 |    9.9173e-06  |
| main/f2/shadowsocks/G2/outer | I-inner0         |          978 |          162 |  1.21151  |           85 |    9.76827e-06 |
| main/f2/shadowsocks/G2/outer | I-inner0         |          978 |          162 |  0.801757 |           65 |    8.25478e-06 |
| main/f2/shadowsocks/G2/outer | I-inner1         |          978 |          162 |  1.15007  |           82 |    8.84045e-06 |
| main/f2/shadowsocks/G2/outer | I-inner1         |          978 |          162 |  1.27927  |           88 |    8.5766e-06  |
| main/f2/shadowsocks/G2/outer | I-inner1         |          978 |          162 |  0.843299 |           69 |    8.52302e-06 |
| main/f2/shadowsocks/G2/outer | I-inner1         |          978 |          162 |  0.532746 |           50 |    8.89112e-06 |
| main/f2/shadowsocks/G2/outer | J-inner0         |          978 |          162 |  0.974125 |           78 |    8.60183e-06 |
| main/f2/shadowsocks/G2/outer | J-inner0         |          978 |          162 |  1.12867  |           85 |    8.96982e-06 |
| main/f2/shadowsocks/G2/outer | J-inner0         |          978 |          162 |  0.735045 |           64 |    9.68689e-06 |
| main/f2/shadowsocks/G2/outer | J-inner0         |          978 |          162 |  0.478007 |           48 |    8.55091e-06 |
| main/f2/shadowsocks/G2/outer | J-inner1         |          978 |          162 |  0.873172 |           69 |    9.71722e-06 |
| main/f2/shadowsocks/G2/outer | J-inner1         |          978 |          162 |  1.05582  |           78 |    8.62223e-06 |
| main/f2/shadowsocks/G2/outer | J-inner1         |          978 |          162 |  0.666046 |           60 |    9.29501e-06 |
| main/f2/shadowsocks/G2/outer | J-inner1         |          978 |          162 |  0.425676 |           44 |    8.08604e-06 |
| main/f2/shadowsocks/G2/outer | M-inner0         |          582 |           96 |  0.92599  |           74 |    8.42047e-06 |
| main/f2/shadowsocks/G2/outer | M-inner0         |          582 |           96 |  0.974406 |           78 |    8.93101e-06 |
| main/f2/shadowsocks/G2/outer | M-inner0         |          582 |           96 |  0.674957 |           59 |    9.78338e-06 |
| main/f2/shadowsocks/G2/outer | M-inner0         |          582 |           96 |  0.432616 |           45 |    8.06626e-06 |
| main/f2/shadowsocks/G2/outer | M-inner1         |          582 |           96 |  0.711572 |           61 |    9.11558e-06 |
| main/f2/shadowsocks/G2/outer | M-inner1         |          582 |           96 |  0.810893 |           66 |    8.03536e-06 |
| main/f2/shadowsocks/G2/outer | M-inner1         |          582 |           96 |  0.555251 |           53 |    9.39611e-06 |
| main/f2/shadowsocks/G2/outer | M-inner1         |          582 |           96 |  0.375363 |           41 |    6.64428e-06 |
| main/f2/trojan/G0/outer      | I-inner0         |          978 |          162 |  0.727515 |           62 |    9.49592e-06 |
| main/f2/trojan/G0/outer      | I-inner0         |          978 |          162 |  0.817633 |           65 |    9.84642e-06 |
| main/f2/trojan/G0/outer      | I-inner0         |          978 |          162 |  0.617426 |           56 |    9.61141e-06 |
| main/f2/trojan/G0/outer      | I-inner0         |          978 |          162 |  0.441385 |           44 |    8.83541e-06 |
| main/f2/trojan/G0/outer      | I-inner1         |          978 |          162 |  1.25013  |           87 |    9.57526e-06 |
| main/f2/trojan/G0/outer      | I-inner1         |          978 |          162 |  1.3386   |           93 |    9.66177e-06 |
| main/f2/trojan/G0/outer      | I-inner1         |          978 |          162 |  0.963023 |           73 |    9.35848e-06 |
| main/f2/trojan/G0/outer      | I-inner1         |          978 |          162 |  0.588587 |           54 |    9.93467e-06 |
| main/f2/trojan/G0/outer      | J-inner0         |          978 |          162 |  0.951063 |           73 |    9.45603e-06 |
| main/f2/trojan/G0/outer      | J-inner0         |          978 |          162 |  0.960866 |           74 |    9.91489e-06 |
| main/f2/trojan/G0/outer      | J-inner0         |          978 |          162 |  0.754546 |           64 |    9.76829e-06 |
| main/f2/trojan/G0/outer      | J-inner0         |          978 |          162 |  0.449198 |           46 |    8.49435e-06 |
| main/f2/trojan/G0/outer      | J-inner1         |          978 |          162 |  0.956067 |           74 |    9.89352e-06 |
| main/f2/trojan/G0/outer      | J-inner1         |          978 |          162 |  1.10036  |           80 |    9.54505e-06 |
| main/f2/trojan/G0/outer      | J-inner1         |          978 |          162 |  0.750759 |           62 |    9.44925e-06 |
| main/f2/trojan/G0/outer      | J-inner1         |          978 |          162 |  0.497998 |           46 |    9.46851e-06 |
| main/f2/trojan/G0/outer      | M-inner0         |          582 |           96 |  0.707865 |           61 |    8.09569e-06 |
| main/f2/trojan/G0/outer      | M-inner0         |          582 |           96 |  0.7891   |           65 |    8.88761e-06 |
| main/f2/trojan/G0/outer      | M-inner0         |          582 |           96 |  0.558118 |           52 |    8.79227e-06 |
| main/f2/trojan/G0/outer      | M-inner0         |          582 |           96 |  0.349935 |           38 |    9.78631e-06 |
| main/f2/trojan/G0/outer      | M-inner1         |          582 |           96 |  0.800948 |           66 |    9.12571e-06 |
| main/f2/trojan/G0/outer      | M-inner1         |          582 |           96 |  0.911266 |           72 |    9.9293e-06  |
| main/f2/trojan/G0/outer      | M-inner1         |          582 |           96 |  0.622474 |           56 |    9.00237e-06 |
| main/f2/trojan/G0/outer      | M-inner1         |          582 |           96 |  0.413397 |           42 |    8.55452e-06 |
| main/f2/trojan/G1/outer      | I-inner0         |          978 |          162 |  1.19541  |           83 |    7.96877e-06 |
| main/f2/trojan/G1/outer      | I-inner0         |          978 |          162 |  1.34589  |           88 |    8.37705e-06 |
| main/f2/trojan/G1/outer      | I-inner0         |          978 |          162 |  0.830206 |           68 |    9.69629e-06 |
| main/f2/trojan/G1/outer      | I-inner0         |          978 |          162 |  0.587212 |           54 |    9.26405e-06 |
| main/f2/trojan/G1/outer      | I-inner1         |          978 |          162 |  0.981661 |           76 |    9.94348e-06 |
| main/f2/trojan/G1/outer      | I-inner1         |          978 |          162 |  1.09063  |           83 |    9.02944e-06 |
| main/f2/trojan/G1/outer      | I-inner1         |          978 |          162 |  0.795335 |           66 |    9.03908e-06 |
| main/f2/trojan/G1/outer      | I-inner1         |          978 |          162 |  0.550558 |           51 |    9.34409e-06 |
| main/f2/trojan/G1/outer      | J-inner0         |          978 |          162 |  0.938634 |           74 |    9.39066e-06 |
| main/f2/trojan/G1/outer      | J-inner0         |          978 |          162 |  1.07014  |           79 |    9.66495e-06 |
| main/f2/trojan/G1/outer      | J-inner0         |          978 |          162 |  0.724534 |           61 |    9.07278e-06 |
| main/f2/trojan/G1/outer      | J-inner0         |          978 |          162 |  0.470715 |           47 |    9.13779e-06 |
| main/f2/trojan/G1/outer      | J-inner1         |          978 |          162 |  0.902805 |           73 |    9.58417e-06 |
| main/f2/trojan/G1/outer      | J-inner1         |          978 |          162 |  1.02927  |           80 |    9.45796e-06 |
| main/f2/trojan/G1/outer      | J-inner1         |          978 |          162 |  0.688235 |           61 |    9.78228e-06 |
| main/f2/trojan/G1/outer      | J-inner1         |          978 |          162 |  0.449947 |           46 |    8.92934e-06 |
| main/f2/trojan/G1/outer      | M-inner0         |          582 |           96 |  0.821172 |           68 |    8.99713e-06 |
| main/f2/trojan/G1/outer      | M-inner0         |          582 |           96 |  0.864732 |           71 |    9.55291e-06 |
| main/f2/trojan/G1/outer      | M-inner0         |          582 |           96 |  0.666865 |           59 |    9.45644e-06 |
| main/f2/trojan/G1/outer      | M-inner0         |          582 |           96 |  0.437793 |           45 |    9.40165e-06 |
| main/f2/trojan/G1/outer      | M-inner1         |          582 |           96 |  0.867939 |           70 |    9.05352e-06 |
| main/f2/trojan/G1/outer      | M-inner1         |          582 |           96 |  1.04019  |           78 |    9.50297e-06 |
| main/f2/trojan/G1/outer      | M-inner1         |          582 |           96 |  0.702248 |           60 |    9.03949e-06 |
| main/f2/trojan/G1/outer      | M-inner1         |          582 |           96 |  0.453291 |           45 |    7.66506e-06 |
| main/f2/trojan/G2/outer      | I-inner0         |          978 |          162 |  0.981649 |           77 |    9.80022e-06 |
| main/f2/trojan/G2/outer      | I-inner0         |          978 |          162 |  1.08693  |           82 |    9.90967e-06 |
| main/f2/trojan/G2/outer      | I-inner0         |          978 |          162 |  0.872964 |           70 |    9.34399e-06 |
| main/f2/trojan/G2/outer      | I-inner0         |          978 |          162 |  0.559184 |           53 |    9.75644e-06 |
| main/f2/trojan/G2/outer      | I-inner1         |          978 |          162 |  0.924221 |           75 |    9.73052e-06 |
| main/f2/trojan/G2/outer      | I-inner1         |          978 |          162 |  1.02406  |           80 |    9.97651e-06 |
| main/f2/trojan/G2/outer      | I-inner1         |          978 |          162 |  0.714227 |           63 |    9.64073e-06 |
| main/f2/trojan/G2/outer      | I-inner1         |          978 |          162 |  0.460421 |           47 |    9.96869e-06 |
| main/f2/trojan/G2/outer      | J-inner0         |          978 |          162 |  0.990152 |           77 |    9.81632e-06 |
| main/f2/trojan/G2/outer      | J-inner0         |          978 |          162 |  1.19886  |           87 |    9.57321e-06 |
| main/f2/trojan/G2/outer      | J-inner0         |          978 |          162 |  0.808581 |           67 |    9.89931e-06 |
| main/f2/trojan/G2/outer      | J-inner0         |          978 |          162 |  0.503304 |           49 |    8.22586e-06 |
| main/f2/trojan/G2/outer      | J-inner1         |          978 |          162 |  0.93402  |           75 |    9.32748e-06 |
| main/f2/trojan/G2/outer      | J-inner1         |          978 |          162 |  1.0713   |           82 |    9.66044e-06 |
| main/f2/trojan/G2/outer      | J-inner1         |          978 |          162 |  0.747048 |           65 |    8.89631e-06 |
| main/f2/trojan/G2/outer      | J-inner1         |          978 |          162 |  0.454499 |           47 |    8.3429e-06  |
| main/f2/trojan/G2/outer      | M-inner0         |          582 |           96 |  0.637965 |           59 |    9.91808e-06 |
| main/f2/trojan/G2/outer      | M-inner0         |          582 |           96 |  0.735866 |           64 |    8.53263e-06 |
| main/f2/trojan/G2/outer      | M-inner0         |          582 |           96 |  0.542435 |           51 |    8.64796e-06 |
| main/f2/trojan/G2/outer      | M-inner0         |          582 |           96 |  0.320178 |           37 |    9.55497e-06 |
| main/f2/trojan/G2/outer      | M-inner1         |          582 |           96 |  0.659695 |           58 |    9.37357e-06 |
| main/f2/trojan/G2/outer      | M-inner1         |          582 |           96 |  0.674892 |           60 |    9.8753e-06  |
| main/f2/trojan/G2/outer      | M-inner1         |          582 |           96 |  0.527809 |           50 |    9.04896e-06 |
| main/f2/trojan/G2/outer      | M-inner1         |          582 |           96 |  0.348731 |           39 |    6.41977e-06 |
| main/f2/vless/G0/outer       | I-inner0         |          978 |          162 |  0.921407 |           75 |    9.84354e-06 |
| main/f2/vless/G0/outer       | I-inner0         |          978 |          162 |  1.08669  |           82 |    9.47989e-06 |
| main/f2/vless/G0/outer       | I-inner0         |          978 |          162 |  0.778056 |           66 |    9.43831e-06 |
| main/f2/vless/G0/outer       | I-inner0         |          978 |          162 |  0.468306 |           48 |    9.31708e-06 |
| main/f2/vless/G0/outer       | I-inner1         |          978 |          162 |  1.10974  |           83 |    9.36535e-06 |
| main/f2/vless/G0/outer       | I-inner1         |          978 |          162 |  1.29168  |           91 |    9.74634e-06 |
| main/f2/vless/G0/outer       | I-inner1         |          978 |          162 |  0.852154 |           71 |    9.2526e-06  |
| main/f2/vless/G0/outer       | I-inner1         |          978 |          162 |  0.549437 |           52 |    7.99128e-06 |
| main/f2/vless/G0/outer       | J-inner0         |          978 |          162 |  0.898332 |           69 |    9.32633e-06 |
| main/f2/vless/G0/outer       | J-inner0         |          978 |          162 |  1.01432  |           76 |    8.9018e-06  |
| main/f2/vless/G0/outer       | J-inner0         |          978 |          162 |  0.686032 |           59 |    7.45156e-06 |
| main/f2/vless/G0/outer       | J-inner0         |          978 |          162 |  0.392831 |           41 |    6.98175e-06 |
| main/f2/vless/G0/outer       | J-inner1         |          978 |          162 |  0.930941 |           73 |    8.88673e-06 |
| main/f2/vless/G0/outer       | J-inner1         |          978 |          162 |  1.08092  |           81 |    8.99849e-06 |
| main/f2/vless/G0/outer       | J-inner1         |          978 |          162 |  0.711925 |           63 |    8.92544e-06 |
| main/f2/vless/G0/outer       | J-inner1         |          978 |          162 |  0.443697 |           46 |    8.46507e-06 |
| main/f2/vless/G0/outer       | M-inner0         |          582 |           96 |  0.782767 |           65 |    8.33691e-06 |
| main/f2/vless/G0/outer       | M-inner0         |          582 |           96 |  0.82708  |           67 |    9.68654e-06 |
| main/f2/vless/G0/outer       | M-inner0         |          582 |           96 |  0.580568 |           54 |    7.96461e-06 |
| main/f2/vless/G0/outer       | M-inner0         |          582 |           96 |  0.349228 |           39 |    8.55636e-06 |
| main/f2/vless/G0/outer       | M-inner1         |          582 |           96 |  0.751268 |           65 |    9.81515e-06 |
| main/f2/vless/G0/outer       | M-inner1         |          582 |           96 |  0.876292 |           71 |    9.23656e-06 |
| main/f2/vless/G0/outer       | M-inner1         |          582 |           96 |  0.649967 |           57 |    9.56257e-06 |
| main/f2/vless/G0/outer       | M-inner1         |          582 |           96 |  0.413099 |           42 |    9.89775e-06 |
| main/f2/vless/G1/outer       | I-inner0         |          978 |          162 |  1.11023  |           83 |    9.35369e-06 |
| main/f2/vless/G1/outer       | I-inner0         |          978 |          162 |  1.29449  |           92 |    8.95003e-06 |
| main/f2/vless/G1/outer       | I-inner0         |          978 |          162 |  0.851879 |           70 |    9.24709e-06 |
| main/f2/vless/G1/outer       | I-inner0         |          978 |          162 |  0.52113  |           50 |    9.4006e-06  |
| main/f2/vless/G1/outer       | I-inner1         |          978 |          162 |  1.07388  |           79 |    9.51563e-06 |
| main/f2/vless/G1/outer       | I-inner1         |          978 |          162 |  1.12989  |           81 |    9.92905e-06 |
| main/f2/vless/G1/outer       | I-inner1         |          978 |          162 |  0.836227 |           66 |    9.7967e-06  |
| main/f2/vless/G1/outer       | I-inner1         |          978 |          162 |  0.520151 |           49 |    9.90872e-06 |
| main/f2/vless/G1/outer       | J-inner0         |          978 |          162 |  0.966074 |           76 |    9.03544e-06 |
| main/f2/vless/G1/outer       | J-inner0         |          978 |          162 |  1.09909  |           83 |    8.83795e-06 |
| main/f2/vless/G1/outer       | J-inner0         |          978 |          162 |  0.720383 |           63 |    9.16724e-06 |
| main/f2/vless/G1/outer       | J-inner0         |          978 |          162 |  0.446484 |           47 |    9.99934e-06 |
| main/f2/vless/G1/outer       | J-inner1         |          978 |          162 |  0.937625 |           73 |    8.99809e-06 |
| main/f2/vless/G1/outer       | J-inner1         |          978 |          162 |  1.15818  |           81 |    9.83905e-06 |
| main/f2/vless/G1/outer       | J-inner1         |          978 |          162 |  0.749662 |           63 |    8.70762e-06 |
| main/f2/vless/G1/outer       | J-inner1         |          978 |          162 |  0.446122 |           45 |    9.86241e-06 |
| main/f2/vless/G1/outer       | M-inner0         |          582 |           96 |  0.822615 |           69 |    9.87363e-06 |
| main/f2/vless/G1/outer       | M-inner0         |          582 |           96 |  0.934906 |           75 |    9.50232e-06 |
| main/f2/vless/G1/outer       | M-inner0         |          582 |           96 |  0.615104 |           58 |    9.63879e-06 |
| main/f2/vless/G1/outer       | M-inner0         |          582 |           96 |  0.419729 |           44 |    8.6126e-06  |
| main/f2/vless/G1/outer       | M-inner1         |          582 |           96 |  0.731454 |           61 |    9.78752e-06 |
| main/f2/vless/G1/outer       | M-inner1         |          582 |           96 |  0.789936 |           66 |    9.84192e-06 |
| main/f2/vless/G1/outer       | M-inner1         |          582 |           96 |  0.607811 |           55 |    8.828e-06   |
| main/f2/vless/G1/outer       | M-inner1         |          582 |           96 |  0.387385 |           41 |    9.22184e-06 |
| main/f2/vless/G2/outer       | I-inner0         |          978 |          162 |  0.978056 |           73 |    9.64267e-06 |
| main/f2/vless/G2/outer       | I-inner0         |          978 |          162 |  1.13586  |           79 |    9.76121e-06 |
| main/f2/vless/G2/outer       | I-inner0         |          978 |          162 |  0.729082 |           62 |    9.34403e-06 |
| main/f2/vless/G2/outer       | I-inner0         |          978 |          162 |  0.447302 |           45 |    9.63903e-06 |
| main/f2/vless/G2/outer       | I-inner1         |          978 |          162 |  0.831225 |           69 |    9.70436e-06 |
| main/f2/vless/G2/outer       | I-inner1         |          978 |          162 |  0.925517 |           74 |    9.90476e-06 |
| main/f2/vless/G2/outer       | I-inner1         |          978 |          162 |  0.649767 |           59 |    9.41762e-06 |
| main/f2/vless/G2/outer       | I-inner1         |          978 |          162 |  0.456582 |           46 |    8.16634e-06 |
| main/f2/vless/G2/outer       | J-inner0         |          978 |          162 |  0.723388 |           62 |    9.90625e-06 |
| main/f2/vless/G2/outer       | J-inner0         |          978 |          162 |  0.878237 |           70 |    9.42889e-06 |
| main/f2/vless/G2/outer       | J-inner0         |          978 |          162 |  0.608479 |           55 |    9.79673e-06 |
| main/f2/vless/G2/outer       | J-inner0         |          978 |          162 |  0.397076 |           42 |    5.47722e-06 |
| main/f2/vless/G2/outer       | J-inner1         |          978 |          162 |  0.713132 |           63 |    9.85225e-06 |
| main/f2/vless/G2/outer       | J-inner1         |          978 |          162 |  0.70218  |           64 |    9.95406e-06 |
| main/f2/vless/G2/outer       | J-inner1         |          978 |          162 |  0.574742 |           55 |    9.34459e-06 |
| main/f2/vless/G2/outer       | J-inner1         |          978 |          162 |  0.382477 |           41 |    8.19103e-06 |
| main/f2/vless/G2/outer       | M-inner0         |          582 |           96 |  0.579169 |           57 |    9.46532e-06 |
| main/f2/vless/G2/outer       | M-inner0         |          582 |           96 |  0.691113 |           63 |    9.02324e-06 |
| main/f2/vless/G2/outer       | M-inner0         |          582 |           96 |  0.485729 |           49 |    9.40322e-06 |
| main/f2/vless/G2/outer       | M-inner0         |          582 |           96 |  0.333216 |           38 |    6.87602e-06 |
| main/f2/vless/G2/outer       | M-inner1         |          582 |           96 |  0.637252 |           56 |    9.95538e-06 |
| main/f2/vless/G2/outer       | M-inner1         |          582 |           96 |  0.722705 |           62 |    8.14467e-06 |
| main/f2/vless/G2/outer       | M-inner1         |          582 |           96 |  0.481043 |           48 |    8.51942e-06 |
| main/f2/vless/G2/outer       | M-inner1         |          582 |           96 |  0.335969 |           36 |    8.7016e-06  |
| main/f2/vmess/G0/outer       | I-inner0         |          978 |          162 |  0.906886 |           75 |    9.25632e-06 |
| main/f2/vmess/G0/outer       | I-inner0         |          978 |          162 |  1.05257  |           82 |    9.2492e-06  |
| main/f2/vmess/G0/outer       | I-inner0         |          978 |          162 |  0.746931 |           65 |    8.22165e-06 |
| main/f2/vmess/G0/outer       | I-inner0         |          978 |          162 |  0.492118 |           48 |    8.89714e-06 |
| main/f2/vmess/G0/outer       | I-inner1         |          978 |          162 |  1.13514  |           82 |    9.21428e-06 |
| main/f2/vmess/G0/outer       | I-inner1         |          978 |          162 |  1.26889  |           87 |    9.63297e-06 |
| main/f2/vmess/G0/outer       | I-inner1         |          978 |          162 |  0.823429 |           68 |    9.41547e-06 |
| main/f2/vmess/G0/outer       | I-inner1         |          978 |          162 |  0.497326 |           49 |    9.08556e-06 |
| main/f2/vmess/G0/outer       | J-inner0         |          978 |          162 |  0.910258 |           73 |    8.73885e-06 |
| main/f2/vmess/G0/outer       | J-inner0         |          978 |          162 |  1.02591  |           78 |    9.26259e-06 |
| main/f2/vmess/G0/outer       | J-inner0         |          978 |          162 |  0.712587 |           63 |    9.76749e-06 |
| main/f2/vmess/G0/outer       | J-inner0         |          978 |          162 |  0.469858 |           47 |    7.28481e-06 |
| main/f2/vmess/G0/outer       | J-inner1         |          978 |          162 |  0.84279  |           70 |    9.2344e-06  |
| main/f2/vmess/G0/outer       | J-inner1         |          978 |          162 |  0.940278 |           76 |    9.75189e-06 |
| main/f2/vmess/G0/outer       | J-inner1         |          978 |          162 |  0.647424 |           59 |    9.7206e-06  |
| main/f2/vmess/G0/outer       | J-inner1         |          978 |          162 |  0.462506 |           47 |    9.28353e-06 |
| main/f2/vmess/G0/outer       | M-inner0         |          582 |           96 |  0.718868 |           64 |    9.35525e-06 |
| main/f2/vmess/G0/outer       | M-inner0         |          582 |           96 |  0.803062 |           69 |    9.52196e-06 |
| main/f2/vmess/G0/outer       | M-inner0         |          582 |           96 |  0.543961 |           53 |    8.80028e-06 |
| main/f2/vmess/G0/outer       | M-inner0         |          582 |           96 |  0.353835 |           39 |    9.53479e-06 |
| main/f2/vmess/G0/outer       | M-inner1         |          582 |           96 |  0.757923 |           63 |    8.62639e-06 |
| main/f2/vmess/G0/outer       | M-inner1         |          582 |           96 |  0.861617 |           68 |    9.58386e-06 |
| main/f2/vmess/G0/outer       | M-inner1         |          582 |           96 |  0.568063 |           54 |    9.89139e-06 |
| main/f2/vmess/G0/outer       | M-inner1         |          582 |           96 |  0.360824 |           40 |    9.50268e-06 |
| main/f2/vmess/G1/outer       | I-inner0         |          978 |          162 |  1.32488  |           91 |    9.65302e-06 |
| main/f2/vmess/G1/outer       | I-inner0         |          978 |          162 |  1.29928  |           93 |    9.05897e-06 |
| main/f2/vmess/G1/outer       | I-inner0         |          978 |          162 |  0.967884 |           76 |    8.89218e-06 |
| main/f2/vmess/G1/outer       | I-inner0         |          978 |          162 |  0.621554 |           56 |    9.33246e-06 |
| main/f2/vmess/G1/outer       | I-inner1         |          978 |          162 |  1.03624  |           79 |    8.57363e-06 |
| main/f2/vmess/G1/outer       | I-inner1         |          978 |          162 |  1.1705   |           86 |    8.34844e-06 |
| main/f2/vmess/G1/outer       | I-inner1         |          978 |          162 |  0.783903 |           66 |    9.9811e-06  |
| main/f2/vmess/G1/outer       | I-inner1         |          978 |          162 |  0.5266   |           51 |    9.927e-06   |
| main/f2/vmess/G1/outer       | J-inner0         |          978 |          162 |  1.08137  |           82 |    9.57937e-06 |
| main/f2/vmess/G1/outer       | J-inner0         |          978 |          162 |  1.28372  |           90 |    8.46467e-06 |
| main/f2/vmess/G1/outer       | J-inner0         |          978 |          162 |  0.868824 |           71 |    8.70879e-06 |
| main/f2/vmess/G1/outer       | J-inner0         |          978 |          162 |  0.519709 |           50 |    8.31513e-06 |
| main/f2/vmess/G1/outer       | J-inner1         |          978 |          162 |  0.834071 |           71 |    9.76363e-06 |
| main/f2/vmess/G1/outer       | J-inner1         |          978 |          162 |  0.981682 |           77 |    9.74902e-06 |
| main/f2/vmess/G1/outer       | J-inner1         |          978 |          162 |  0.681971 |           61 |    8.78296e-06 |
| main/f2/vmess/G1/outer       | J-inner1         |          978 |          162 |  0.462092 |           45 |    8.22412e-06 |
| main/f2/vmess/G1/outer       | M-inner0         |          582 |           96 |  0.837399 |           70 |    7.16397e-06 |
| main/f2/vmess/G1/outer       | M-inner0         |          582 |           96 |  0.938727 |           76 |    8.2215e-06  |
| main/f2/vmess/G1/outer       | M-inner0         |          582 |           96 |  0.656303 |           59 |    9.71285e-06 |
| main/f2/vmess/G1/outer       | M-inner0         |          582 |           96 |  0.409739 |           43 |    8.82568e-06 |
| main/f2/vmess/G1/outer       | M-inner1         |          582 |           96 |  0.770288 |           64 |    9.36801e-06 |
| main/f2/vmess/G1/outer       | M-inner1         |          582 |           96 |  0.852674 |           69 |    9.37086e-06 |
| main/f2/vmess/G1/outer       | M-inner1         |          582 |           96 |  0.591489 |           54 |    9.89596e-06 |
| main/f2/vmess/G1/outer       | M-inner1         |          582 |           96 |  0.376871 |           41 |    8.28314e-06 |
| main/f2/vmess/G2/outer       | I-inner0         |          978 |          162 |  1.02991  |           80 |    9.83327e-06 |
| main/f2/vmess/G2/outer       | I-inner0         |          978 |          162 |  1.16996  |           87 |    7.88327e-06 |
| main/f2/vmess/G2/outer       | I-inner0         |          978 |          162 |  0.778833 |           67 |    9.99474e-06 |
| main/f2/vmess/G2/outer       | I-inner0         |          978 |          162 |  0.481002 |           49 |    9.17684e-06 |
| main/f2/vmess/G2/outer       | I-inner1         |          978 |          162 |  1.234    |           88 |    9.01865e-06 |
| main/f2/vmess/G2/outer       | I-inner1         |          978 |          162 |  1.3312   |           94 |    9.74204e-06 |
| main/f2/vmess/G2/outer       | I-inner1         |          978 |          162 |  0.937983 |           75 |    8.68014e-06 |
| main/f2/vmess/G2/outer       | I-inner1         |          978 |          162 |  0.575349 |           56 |    9.38765e-06 |
| main/f2/vmess/G2/outer       | J-inner0         |          978 |          162 |  1.14837  |           86 |    9.2644e-06  |
| main/f2/vmess/G2/outer       | J-inner0         |          978 |          162 |  1.29715  |           93 |    9.92035e-06 |
| main/f2/vmess/G2/outer       | J-inner0         |          978 |          162 |  0.912496 |           73 |    9.54279e-06 |
| main/f2/vmess/G2/outer       | J-inner0         |          978 |          162 |  0.556622 |           53 |    9.18384e-06 |
| main/f2/vmess/G2/outer       | J-inner1         |          978 |          162 |  1.11307  |           84 |    9.0803e-06  |
| main/f2/vmess/G2/outer       | J-inner1         |          978 |          162 |  1.28672  |           91 |    9.68184e-06 |
| main/f2/vmess/G2/outer       | J-inner1         |          978 |          162 |  0.905962 |           73 |    9.42485e-06 |
| main/f2/vmess/G2/outer       | J-inner1         |          978 |          162 |  0.539499 |           53 |    9.45235e-06 |
| main/f2/vmess/G2/outer       | M-inner0         |          582 |           96 |  0.786879 |           65 |    9.25448e-06 |
| main/f2/vmess/G2/outer       | M-inner0         |          582 |           96 |  0.831602 |           68 |    8.48728e-06 |
| main/f2/vmess/G2/outer       | M-inner0         |          582 |           96 |  0.582955 |           55 |    8.58321e-06 |
| main/f2/vmess/G2/outer       | M-inner0         |          582 |           96 |  0.377449 |           41 |    9.18824e-06 |
| main/f2/vmess/G2/outer       | M-inner1         |          582 |           96 |  0.791379 |           64 |    9.67943e-06 |
| main/f2/vmess/G2/outer       | M-inner1         |          582 |           96 |  0.853198 |           67 |    9.76765e-06 |
| main/f2/vmess/G2/outer       | M-inner1         |          582 |           96 |  0.593643 |           55 |    9.73117e-06 |
| main/f2/vmess/G2/outer       | M-inner1         |          582 |           96 |  0.400204 |           43 |    6.36087e-06 |
| main/f3/shadowsocks/G0/outer | I-inner0         |          978 |          162 |  0.887983 |           73 |    8.76685e-06 |
| main/f3/shadowsocks/G0/outer | I-inner0         |          978 |          162 |  0.911929 |           76 |    9.68422e-06 |
| main/f3/shadowsocks/G0/outer | I-inner0         |          978 |          162 |  0.687008 |           62 |    9.93128e-06 |
| main/f3/shadowsocks/G0/outer | I-inner0         |          978 |          162 |  0.410608 |           44 |    8.44734e-06 |
| main/f3/shadowsocks/G0/outer | I-inner1         |          978 |          162 |  0.898127 |           74 |    9.49053e-06 |
| main/f3/shadowsocks/G0/outer | I-inner1         |          978 |          162 |  1.02748  |           80 |    9.92893e-06 |
| main/f3/shadowsocks/G0/outer | I-inner1         |          978 |          162 |  0.733624 |           64 |    9.64595e-06 |
| main/f3/shadowsocks/G0/outer | I-inner1         |          978 |          162 |  0.434223 |           46 |    9.80392e-06 |
| main/f3/shadowsocks/G0/outer | J-inner0         |          978 |          162 |  0.961341 |           77 |    9.68903e-06 |
| main/f3/shadowsocks/G0/outer | J-inner0         |          978 |          162 |  1.01597  |           80 |    9.8432e-06  |
| main/f3/shadowsocks/G0/outer | J-inner0         |          978 |          162 |  0.740049 |           64 |    9.73512e-06 |
| main/f3/shadowsocks/G0/outer | J-inner0         |          978 |          162 |  0.465249 |           47 |    7.3659e-06  |
| main/f3/shadowsocks/G0/outer | J-inner1         |          978 |          162 |  0.807584 |           67 |    9.31886e-06 |
| main/f3/shadowsocks/G0/outer | J-inner1         |          978 |          162 |  0.941443 |           73 |    8.53964e-06 |
| main/f3/shadowsocks/G0/outer | J-inner1         |          978 |          162 |  0.637653 |           57 |    9.45552e-06 |
| main/f3/shadowsocks/G0/outer | J-inner1         |          978 |          162 |  0.468128 |           47 |    9.78989e-06 |
| main/f3/shadowsocks/G0/outer | M-inner0         |          582 |           96 |  0.685331 |           62 |    8.93637e-06 |
| main/f3/shadowsocks/G0/outer | M-inner0         |          582 |           96 |  0.743075 |           66 |    9.57925e-06 |
| main/f3/shadowsocks/G0/outer | M-inner0         |          582 |           96 |  0.558247 |           54 |    9.15788e-06 |
| main/f3/shadowsocks/G0/outer | M-inner0         |          582 |           96 |  0.331964 |           38 |    9.70744e-06 |
| main/f3/shadowsocks/G0/outer | M-inner1         |          582 |           96 |  0.830625 |           67 |    8.68654e-06 |
| main/f3/shadowsocks/G0/outer | M-inner1         |          582 |           96 |  0.868126 |           70 |    9.36269e-06 |
| main/f3/shadowsocks/G0/outer | M-inner1         |          582 |           96 |  0.711679 |           59 |    9.45265e-06 |
| main/f3/shadowsocks/G0/outer | M-inner1         |          582 |           96 |  0.411295 |           43 |    9.70433e-06 |
| main/f3/shadowsocks/G1/outer | I-inner0         |          978 |          162 |  1.59773  |          101 |    9.63195e-06 |
| main/f3/shadowsocks/G1/outer | I-inner0         |          978 |          162 |  1.4065   |           97 |    9.38209e-06 |
| main/f3/shadowsocks/G1/outer | I-inner0         |          978 |          162 |  1.20754  |           86 |    9.53875e-06 |
| main/f3/shadowsocks/G1/outer | I-inner0         |          978 |          162 |  0.708353 |           61 |    8.59152e-06 |
| main/f3/shadowsocks/G1/outer | I-inner1         |          978 |          162 |  1.26894  |           89 |    9.42743e-06 |
| main/f3/shadowsocks/G1/outer | I-inner1         |          978 |          162 |  1.46644  |           97 |    9.86334e-06 |
| main/f3/shadowsocks/G1/outer | I-inner1         |          978 |          162 |  0.964246 |           75 |    9.47392e-06 |
| main/f3/shadowsocks/G1/outer | I-inner1         |          978 |          162 |  0.592502 |           56 |    9.36258e-06 |
| main/f3/shadowsocks/G1/outer | J-inner0         |          978 |          162 |  1.09074  |           82 |    9.5044e-06  |
| main/f3/shadowsocks/G1/outer | J-inner0         |          978 |          162 |  1.06231  |           81 |    9.98703e-06 |
| main/f3/shadowsocks/G1/outer | J-inner0         |          978 |          162 |  0.851464 |           71 |    9.74908e-06 |
| main/f3/shadowsocks/G1/outer | J-inner0         |          978 |          162 |  0.536657 |           53 |    8.07366e-06 |
| main/f3/shadowsocks/G1/outer | J-inner1         |          978 |          162 |  0.835544 |           69 |    8.72301e-06 |
| main/f3/shadowsocks/G1/outer | J-inner1         |          978 |          162 |  0.955333 |           75 |    9.36634e-06 |
| main/f3/shadowsocks/G1/outer | J-inner1         |          978 |          162 |  0.693959 |           61 |    9.40137e-06 |
| main/f3/shadowsocks/G1/outer | J-inner1         |          978 |          162 |  0.529379 |           50 |    8.50242e-06 |
| main/f3/shadowsocks/G1/outer | M-inner0         |          582 |           96 |  1.0179   |           78 |    9.22675e-06 |
| main/f3/shadowsocks/G1/outer | M-inner0         |          582 |           96 |  1.17194  |           85 |    8.24105e-06 |
| main/f3/shadowsocks/G1/outer | M-inner0         |          582 |           96 |  0.783154 |           66 |    8.70114e-06 |
| main/f3/shadowsocks/G1/outer | M-inner0         |          582 |           96 |  0.526382 |           51 |    9.75198e-06 |
| main/f3/shadowsocks/G1/outer | M-inner1         |          582 |           96 |  0.868947 |           71 |    9.57606e-06 |
| main/f3/shadowsocks/G1/outer | M-inner1         |          582 |           96 |  1.05651  |           78 |    9.76386e-06 |
| main/f3/shadowsocks/G1/outer | M-inner1         |          582 |           96 |  0.747275 |           62 |    9.33405e-06 |
| main/f3/shadowsocks/G1/outer | M-inner1         |          582 |           96 |  0.429605 |           46 |    9.77912e-06 |
| main/f3/shadowsocks/G2/outer | I-inner0         |          978 |          162 |  1.39588  |           93 |    9.04094e-06 |
| main/f3/shadowsocks/G2/outer | I-inner0         |          978 |          162 |  1.58251  |          104 |    8.21396e-06 |
| main/f3/shadowsocks/G2/outer | I-inner0         |          978 |          162 |  1.04842  |           79 |    9.51962e-06 |
| main/f3/shadowsocks/G2/outer | I-inner0         |          978 |          162 |  0.645914 |           57 |    8.88082e-06 |
| main/f3/shadowsocks/G2/outer | I-inner1         |          978 |          162 |  1.00061  |           78 |    9.19124e-06 |
| main/f3/shadowsocks/G2/outer | I-inner1         |          978 |          162 |  1.11276  |           83 |    9.89652e-06 |
| main/f3/shadowsocks/G2/outer | I-inner1         |          978 |          162 |  0.732612 |           64 |    9.85265e-06 |
| main/f3/shadowsocks/G2/outer | I-inner1         |          978 |          162 |  0.462634 |           47 |    9.28238e-06 |
| main/f3/shadowsocks/G2/outer | J-inner0         |          978 |          162 |  1.04579  |           80 |    8.78198e-06 |
| main/f3/shadowsocks/G2/outer | J-inner0         |          978 |          162 |  1.16405  |           87 |    8.53253e-06 |
| main/f3/shadowsocks/G2/outer | J-inner0         |          978 |          162 |  0.838599 |           69 |    8.87352e-06 |
| main/f3/shadowsocks/G2/outer | J-inner0         |          978 |          162 |  0.510624 |           50 |    7.02348e-06 |
| main/f3/shadowsocks/G2/outer | J-inner1         |          978 |          162 |  0.928604 |           72 |    9.97406e-06 |
| main/f3/shadowsocks/G2/outer | J-inner1         |          978 |          162 |  1.08995  |           80 |    8.09954e-06 |
| main/f3/shadowsocks/G2/outer | J-inner1         |          978 |          162 |  0.690325 |           60 |    9.91993e-06 |
| main/f3/shadowsocks/G2/outer | J-inner1         |          978 |          162 |  0.434524 |           44 |    9.4155e-06  |
| main/f3/shadowsocks/G2/outer | M-inner0         |          582 |           96 |  0.856737 |           68 |    9.53677e-06 |
| main/f3/shadowsocks/G2/outer | M-inner0         |          582 |           96 |  0.972549 |           73 |    9.90585e-06 |
| main/f3/shadowsocks/G2/outer | M-inner0         |          582 |           96 |  0.680671 |           58 |    8.6166e-06  |
| main/f3/shadowsocks/G2/outer | M-inner0         |          582 |           96 |  0.459189 |           43 |    8.39518e-06 |
| main/f3/shadowsocks/G2/outer | M-inner1         |          582 |           96 |  0.838258 |           66 |    8.16249e-06 |
| main/f3/shadowsocks/G2/outer | M-inner1         |          582 |           96 |  0.869426 |           69 |    7.05359e-06 |
| main/f3/shadowsocks/G2/outer | M-inner1         |          582 |           96 |  0.593171 |           55 |    8.35018e-06 |
| main/f3/shadowsocks/G2/outer | M-inner1         |          582 |           96 |  0.386711 |           42 |    9.4535e-06  |
| main/f3/trojan/G0/outer      | I-inner0         |          978 |          162 |  0.935727 |           74 |    8.93384e-06 |
| main/f3/trojan/G0/outer      | I-inner0         |          978 |          162 |  1.03313  |           79 |    9.9279e-06  |
| main/f3/trojan/G0/outer      | I-inner0         |          978 |          162 |  0.69845  |           62 |    9.88894e-06 |
| main/f3/trojan/G0/outer      | I-inner0         |          978 |          162 |  0.483415 |           47 |    9.52921e-06 |
| main/f3/trojan/G0/outer      | I-inner1         |          978 |          162 |  1.15336  |           83 |    9.91568e-06 |
| main/f3/trojan/G0/outer      | I-inner1         |          978 |          162 |  1.24427  |           87 |    9.9221e-06  |
| main/f3/trojan/G0/outer      | I-inner1         |          978 |          162 |  0.850414 |           69 |    9.99457e-06 |
| main/f3/trojan/G0/outer      | I-inner1         |          978 |          162 |  0.513803 |           50 |    7.7238e-06  |
| main/f3/trojan/G0/outer      | J-inner0         |          978 |          162 |  0.85626  |           71 |    9.11781e-06 |
| main/f3/trojan/G0/outer      | J-inner0         |          978 |          162 |  0.924504 |           75 |    9.63548e-06 |
| main/f3/trojan/G0/outer      | J-inner0         |          978 |          162 |  0.656275 |           60 |    8.91662e-06 |
| main/f3/trojan/G0/outer      | J-inner0         |          978 |          162 |  0.396067 |           42 |    9.502e-06   |
| main/f3/trojan/G0/outer      | J-inner1         |          978 |          162 |  0.89654  |           73 |    9.75709e-06 |
| main/f3/trojan/G0/outer      | J-inner1         |          978 |          162 |  0.968372 |           77 |    9.9225e-06  |
| main/f3/trojan/G0/outer      | J-inner1         |          978 |          162 |  0.720051 |           63 |    9.73521e-06 |
| main/f3/trojan/G0/outer      | J-inner1         |          978 |          162 |  0.440438 |           46 |    8.85375e-06 |
| main/f3/trojan/G0/outer      | M-inner0         |          582 |           96 |  0.66591  |           58 |    9.9695e-06  |
| main/f3/trojan/G0/outer      | M-inner0         |          582 |           96 |  0.745626 |           63 |    9.667e-06   |
| main/f3/trojan/G0/outer      | M-inner0         |          582 |           96 |  0.526841 |           50 |    9.7743e-06  |
| main/f3/trojan/G0/outer      | M-inner0         |          582 |           96 |  0.33175  |           36 |    8.90422e-06 |
| main/f3/trojan/G0/outer      | M-inner1         |          582 |           96 |  0.934099 |           74 |    9.75006e-06 |
| main/f3/trojan/G0/outer      | M-inner1         |          582 |           96 |  0.967226 |           75 |    9.66181e-06 |
| main/f3/trojan/G0/outer      | M-inner1         |          582 |           96 |  0.739904 |           63 |    9.09529e-06 |
| main/f3/trojan/G0/outer      | M-inner1         |          582 |           96 |  0.427398 |           44 |    8.79775e-06 |
| main/f3/trojan/G1/outer      | I-inner0         |          978 |          162 |  1.55057  |           98 |    9.95194e-06 |
| main/f3/trojan/G1/outer      | I-inner0         |          978 |          162 |  1.79396  |          106 |    9.68538e-06 |
| main/f3/trojan/G1/outer      | I-inner0         |          978 |          162 |  1.16093  |           83 |    9.10316e-06 |
| main/f3/trojan/G1/outer      | I-inner0         |          978 |          162 |  0.658864 |           59 |    8.87928e-06 |
| main/f3/trojan/G1/outer      | I-inner1         |          978 |          162 |  1.01686  |           79 |    9.21654e-06 |
| main/f3/trojan/G1/outer      | I-inner1         |          978 |          162 |  1.11228  |           84 |    9.85133e-06 |
| main/f3/trojan/G1/outer      | I-inner1         |          978 |          162 |  0.823894 |           68 |    9.35701e-06 |
| main/f3/trojan/G1/outer      | I-inner1         |          978 |          162 |  0.508415 |           50 |    8.77481e-06 |
| main/f3/trojan/G1/outer      | J-inner0         |          978 |          162 |  0.877075 |           71 |    9.33144e-06 |
| main/f3/trojan/G1/outer      | J-inner0         |          978 |          162 |  0.905715 |           74 |    9.73053e-06 |
| main/f3/trojan/G1/outer      | J-inner0         |          978 |          162 |  0.69775  |           61 |    9.76457e-06 |
| main/f3/trojan/G1/outer      | J-inner0         |          978 |          162 |  0.508137 |           47 |    9.70169e-06 |
| main/f3/trojan/G1/outer      | J-inner1         |          978 |          162 |  0.892929 |           71 |    9.62455e-06 |
| main/f3/trojan/G1/outer      | J-inner1         |          978 |          162 |  1.03483  |           78 |    8.56699e-06 |
| main/f3/trojan/G1/outer      | J-inner1         |          978 |          162 |  0.679264 |           60 |    9.32942e-06 |
| main/f3/trojan/G1/outer      | J-inner1         |          978 |          162 |  0.400272 |           42 |    8.65956e-06 |
| main/f3/trojan/G1/outer      | M-inner0         |          582 |           96 |  0.817866 |           68 |    7.56087e-06 |
| main/f3/trojan/G1/outer      | M-inner0         |          582 |           96 |  0.89436  |           73 |    7.64807e-06 |
| main/f3/trojan/G1/outer      | M-inner0         |          582 |           96 |  0.611768 |           56 |    8.89998e-06 |
| main/f3/trojan/G1/outer      | M-inner0         |          582 |           96 |  0.376674 |           41 |    9.83309e-06 |
| main/f3/trojan/G1/outer      | M-inner1         |          582 |           96 |  0.861421 |           68 |    9.8389e-06  |
| main/f3/trojan/G1/outer      | M-inner1         |          582 |           96 |  0.988553 |           74 |    9.87219e-06 |
| main/f3/trojan/G1/outer      | M-inner1         |          582 |           96 |  0.674964 |           59 |    8.75656e-06 |
| main/f3/trojan/G1/outer      | M-inner1         |          582 |           96 |  0.407468 |           42 |    8.85514e-06 |
| main/f3/trojan/G2/outer      | I-inner0         |          978 |          162 |  0.741759 |           64 |    9.93684e-06 |
| main/f3/trojan/G2/outer      | I-inner0         |          978 |          162 |  0.830734 |           68 |    8.9934e-06  |
| main/f3/trojan/G2/outer      | I-inner0         |          978 |          162 |  0.578304 |           55 |    9.15661e-06 |
| main/f3/trojan/G2/outer      | I-inner0         |          978 |          162 |  0.395326 |           42 |    8.34593e-06 |
| main/f3/trojan/G2/outer      | I-inner1         |          978 |          162 |  0.872843 |           72 |    9.11006e-06 |
| main/f3/trojan/G2/outer      | I-inner1         |          978 |          162 |  1.04338  |           80 |    9.49511e-06 |
| main/f3/trojan/G2/outer      | I-inner1         |          978 |          162 |  0.726576 |           64 |    9.33735e-06 |
| main/f3/trojan/G2/outer      | I-inner1         |          978 |          162 |  0.457249 |           46 |    9.95723e-06 |
| main/f3/trojan/G2/outer      | J-inner0         |          978 |          162 |  0.760949 |           66 |    9.24455e-06 |
| main/f3/trojan/G2/outer      | J-inner0         |          978 |          162 |  0.83132  |           69 |    9.49047e-06 |
| main/f3/trojan/G2/outer      | J-inner0         |          978 |          162 |  0.566346 |           55 |    9.62262e-06 |
| main/f3/trojan/G2/outer      | J-inner0         |          978 |          162 |  0.387086 |           42 |    8.36146e-06 |
| main/f3/trojan/G2/outer      | J-inner1         |          978 |          162 |  1.10066  |           81 |    8.68328e-06 |
| main/f3/trojan/G2/outer      | J-inner1         |          978 |          162 |  1.19953  |           86 |    9.44341e-06 |
| main/f3/trojan/G2/outer      | J-inner1         |          978 |          162 |  0.902411 |           68 |    9.98529e-06 |
| main/f3/trojan/G2/outer      | J-inner1         |          978 |          162 |  0.511527 |           49 |    9.49507e-06 |
| main/f3/trojan/G2/outer      | M-inner0         |          582 |           96 |  0.905622 |           59 |    9.00781e-06 |
| main/f3/trojan/G2/outer      | M-inner0         |          582 |           96 |  0.978425 |           62 |    9.31774e-06 |
| main/f3/trojan/G2/outer      | M-inner0         |          582 |           96 |  0.570005 |           49 |    7.78208e-06 |
| main/f3/trojan/G2/outer      | M-inner0         |          582 |           96 |  0.333015 |           36 |    9.97098e-06 |
| main/f3/trojan/G2/outer      | M-inner1         |          582 |           96 |  0.761194 |           63 |    8.64577e-06 |
| main/f3/trojan/G2/outer      | M-inner1         |          582 |           96 |  0.828863 |           67 |    8.87384e-06 |
| main/f3/trojan/G2/outer      | M-inner1         |          582 |           96 |  0.603585 |           54 |    9.12406e-06 |
| main/f3/trojan/G2/outer      | M-inner1         |          582 |           96 |  0.386981 |           41 |    7.89688e-06 |
| main/f3/vless/G0/outer       | I-inner0         |          978 |          162 |  1.15094  |           83 |    9.90547e-06 |
| main/f3/vless/G0/outer       | I-inner0         |          978 |          162 |  1.22755  |           87 |    9.58437e-06 |
| main/f3/vless/G0/outer       | I-inner0         |          978 |          162 |  0.866553 |           70 |    9.76082e-06 |
| main/f3/vless/G0/outer       | I-inner0         |          978 |          162 |  0.498412 |           49 |    9.84318e-06 |
| main/f3/vless/G0/outer       | I-inner1         |          978 |          162 |  1.30263  |           90 |    9.51897e-06 |
| main/f3/vless/G0/outer       | I-inner1         |          978 |          162 |  1.55716  |          100 |    9.62951e-06 |
| main/f3/vless/G0/outer       | I-inner1         |          978 |          162 |  1.03703  |           77 |    9.86201e-06 |
| main/f3/vless/G0/outer       | I-inner1         |          978 |          162 |  0.556483 |           53 |    9.72337e-06 |
| main/f3/vless/G0/outer       | J-inner0         |          978 |          162 |  0.871565 |           70 |    9.22354e-06 |
| main/f3/vless/G0/outer       | J-inner0         |          978 |          162 |  1.003    |           76 |    9.45394e-06 |
| main/f3/vless/G0/outer       | J-inner0         |          978 |          162 |  0.615628 |           57 |    9.05989e-06 |
| main/f3/vless/G0/outer       | J-inner0         |          978 |          162 |  0.381331 |           41 |    8.52546e-06 |
| main/f3/vless/G0/outer       | J-inner1         |          978 |          162 |  0.895572 |           71 |    9.71536e-06 |
| main/f3/vless/G0/outer       | J-inner1         |          978 |          162 |  1.0136   |           78 |    9.71705e-06 |
| main/f3/vless/G0/outer       | J-inner1         |          978 |          162 |  0.675457 |           60 |    9.58921e-06 |
| main/f3/vless/G0/outer       | J-inner1         |          978 |          162 |  0.391613 |           42 |    9.01712e-06 |
| main/f3/vless/G0/outer       | M-inner0         |          582 |           96 |  0.696108 |           62 |    8.67852e-06 |
| main/f3/vless/G0/outer       | M-inner0         |          582 |           96 |  0.783825 |           67 |    9.8411e-06  |
| main/f3/vless/G0/outer       | M-inner0         |          582 |           96 |  0.53952  |           53 |    9.96509e-06 |
| main/f3/vless/G0/outer       | M-inner0         |          582 |           96 |  0.325273 |           37 |    8.97727e-06 |
| main/f3/vless/G0/outer       | M-inner1         |          582 |           96 |  0.966536 |           73 |    9.37184e-06 |
| main/f3/vless/G0/outer       | M-inner1         |          582 |           96 |  1.10771  |           79 |    9.34991e-06 |
| main/f3/vless/G0/outer       | M-inner1         |          582 |           96 |  0.742899 |           60 |    8.95609e-06 |
| main/f3/vless/G0/outer       | M-inner1         |          582 |           96 |  0.406579 |           43 |    7.06015e-06 |
| main/f3/vless/G1/outer       | I-inner0         |          978 |          162 |  1.21425  |           81 |    8.12818e-06 |
| main/f3/vless/G1/outer       | I-inner0         |          978 |          162 |  1.26431  |           87 |    9.70571e-06 |
| main/f3/vless/G1/outer       | I-inner0         |          978 |          162 |  0.868153 |           68 |    8.84923e-06 |
| main/f3/vless/G1/outer       | I-inner0         |          978 |          162 |  0.563103 |           50 |    8.54361e-06 |
| main/f3/vless/G1/outer       | I-inner1         |          978 |          162 |  1.22608  |           87 |    9.79051e-06 |
| main/f3/vless/G1/outer       | I-inner1         |          978 |          162 |  1.48174  |           98 |    8.6222e-06  |
| main/f3/vless/G1/outer       | I-inner1         |          978 |          162 |  0.95575  |           74 |    9.69087e-06 |
| main/f3/vless/G1/outer       | I-inner1         |          978 |          162 |  0.621003 |           56 |    8.46014e-06 |
| main/f3/vless/G1/outer       | J-inner0         |          978 |          162 |  0.852667 |           72 |    8.7509e-06  |
| main/f3/vless/G1/outer       | J-inner0         |          978 |          162 |  1.07891  |           82 |    8.17093e-06 |
| main/f3/vless/G1/outer       | J-inner0         |          978 |          162 |  0.735492 |           64 |    8.76602e-06 |
| main/f3/vless/G1/outer       | J-inner0         |          978 |          162 |  0.468792 |           46 |    8.86735e-06 |
| main/f3/vless/G1/outer       | J-inner1         |          978 |          162 |  0.814456 |           69 |    9.90093e-06 |
| main/f3/vless/G1/outer       | J-inner1         |          978 |          162 |  0.963547 |           76 |    9.22928e-06 |
| main/f3/vless/G1/outer       | J-inner1         |          978 |          162 |  0.666807 |           59 |    8.98002e-06 |
| main/f3/vless/G1/outer       | J-inner1         |          978 |          162 |  0.429119 |           44 |    9.86611e-06 |
| main/f3/vless/G1/outer       | M-inner0         |          582 |           96 |  0.780939 |           64 |    9.42803e-06 |
| main/f3/vless/G1/outer       | M-inner0         |          582 |           96 |  0.933423 |           68 |    9.72462e-06 |
| main/f3/vless/G1/outer       | M-inner0         |          582 |           96 |  0.568703 |           53 |    8.83206e-06 |
| main/f3/vless/G1/outer       | M-inner0         |          582 |           96 |  0.348969 |           39 |    8.94582e-06 |
| main/f3/vless/G1/outer       | M-inner1         |          582 |           96 |  0.803263 |           67 |    9.69374e-06 |
| main/f3/vless/G1/outer       | M-inner1         |          582 |           96 |  0.956986 |           75 |    9.03063e-06 |
| main/f3/vless/G1/outer       | M-inner1         |          582 |           96 |  0.63459  |           57 |    9.01411e-06 |
| main/f3/vless/G1/outer       | M-inner1         |          582 |           96 |  0.386122 |           42 |    7.75448e-06 |
| main/f3/vless/G2/outer       | I-inner0         |          978 |          162 |  0.996981 |           75 |    9.08317e-06 |
| main/f3/vless/G2/outer       | I-inner0         |          978 |          162 |  1.136    |           81 |    8.15007e-06 |
| main/f3/vless/G2/outer       | I-inner0         |          978 |          162 |  0.72105  |           62 |    8.12287e-06 |
| main/f3/vless/G2/outer       | I-inner0         |          978 |          162 |  0.458949 |           46 |    9.06405e-06 |
| main/f3/vless/G2/outer       | I-inner1         |          978 |          162 |  0.950031 |           73 |    9.1307e-06  |
| main/f3/vless/G2/outer       | I-inner1         |          978 |          162 |  1.06456  |           77 |    9.37663e-06 |
| main/f3/vless/G2/outer       | I-inner1         |          978 |          162 |  0.732721 |           62 |    9.41775e-06 |
| main/f3/vless/G2/outer       | I-inner1         |          978 |          162 |  0.45052  |           45 |    9.95188e-06 |
| main/f3/vless/G2/outer       | J-inner0         |          978 |          162 |  0.850457 |           71 |    9.33223e-06 |
| main/f3/vless/G2/outer       | J-inner0         |          978 |          162 |  0.939018 |           76 |    9.03328e-06 |
| main/f3/vless/G2/outer       | J-inner0         |          978 |          162 |  0.690979 |           61 |    9.52311e-06 |
| main/f3/vless/G2/outer       | J-inner0         |          978 |          162 |  0.413589 |           44 |    8.90902e-06 |
| main/f3/vless/G2/outer       | J-inner1         |          978 |          162 |  0.840854 |           69 |    9.96846e-06 |
| main/f3/vless/G2/outer       | J-inner1         |          978 |          162 |  0.93025  |           74 |    8.24819e-06 |
| main/f3/vless/G2/outer       | J-inner1         |          978 |          162 |  0.634201 |           57 |    9.99299e-06 |
| main/f3/vless/G2/outer       | J-inner1         |          978 |          162 |  0.398694 |           42 |    9.51407e-06 |
| main/f3/vless/G2/outer       | M-inner0         |          582 |           96 |  0.766039 |           64 |    9.91533e-06 |
| main/f3/vless/G2/outer       | M-inner0         |          582 |           96 |  0.851219 |           70 |    9.36116e-06 |
| main/f3/vless/G2/outer       | M-inner0         |          582 |           96 |  0.602983 |           55 |    9.13261e-06 |
| main/f3/vless/G2/outer       | M-inner0         |          582 |           96 |  0.358972 |           40 |    9.71928e-06 |
| main/f3/vless/G2/outer       | M-inner1         |          582 |           96 |  0.690578 |           60 |    9.72544e-06 |
| main/f3/vless/G2/outer       | M-inner1         |          582 |           96 |  0.747465 |           64 |    9.4168e-06  |
| main/f3/vless/G2/outer       | M-inner1         |          582 |           96 |  0.524934 |           50 |    9.94958e-06 |
| main/f3/vless/G2/outer       | M-inner1         |          582 |           96 |  0.353219 |           38 |    8.75942e-06 |
| main/f3/vmess/G0/outer       | I-inner0         |          978 |          162 |  1.16364  |           82 |    9.74009e-06 |
| main/f3/vmess/G0/outer       | I-inner0         |          978 |          162 |  1.38778  |           89 |    9.59626e-06 |
| main/f3/vmess/G0/outer       | I-inner0         |          978 |          162 |  0.987222 |           75 |    9.2448e-06  |
| main/f3/vmess/G0/outer       | I-inner0         |          978 |          162 |  0.567878 |           54 |    9.74398e-06 |
| main/f3/vmess/G0/outer       | I-inner1         |          978 |          162 |  1.03473  |           78 |    9.60824e-06 |
| main/f3/vmess/G0/outer       | I-inner1         |          978 |          162 |  1.13562  |           84 |    9.2144e-06  |
| main/f3/vmess/G0/outer       | I-inner1         |          978 |          162 |  0.79819  |           66 |    9.82515e-06 |
| main/f3/vmess/G0/outer       | I-inner1         |          978 |          162 |  0.498922 |           49 |    8.97626e-06 |
| main/f3/vmess/G0/outer       | J-inner0         |          978 |          162 |  0.814771 |           68 |    9.84639e-06 |
| main/f3/vmess/G0/outer       | J-inner0         |          978 |          162 |  0.950408 |           74 |    9.118e-06   |
| main/f3/vmess/G0/outer       | J-inner0         |          978 |          162 |  0.657048 |           59 |    8.46903e-06 |
| main/f3/vmess/G0/outer       | J-inner0         |          978 |          162 |  0.382421 |           41 |    9.79552e-06 |
| main/f3/vmess/G0/outer       | J-inner1         |          978 |          162 |  0.753425 |           67 |    9.76993e-06 |
| main/f3/vmess/G0/outer       | J-inner1         |          978 |          162 |  0.897621 |           75 |    9.50552e-06 |
| main/f3/vmess/G0/outer       | J-inner1         |          978 |          162 |  0.647319 |           59 |    9.24508e-06 |
| main/f3/vmess/G0/outer       | J-inner1         |          978 |          162 |  0.4037   |           43 |    7.98034e-06 |
| main/f3/vmess/G0/outer       | M-inner0         |          582 |           96 |  0.744578 |           64 |    9.67657e-06 |
| main/f3/vmess/G0/outer       | M-inner0         |          582 |           96 |  0.869646 |           69 |    9.49627e-06 |
| main/f3/vmess/G0/outer       | M-inner0         |          582 |           96 |  0.587601 |           54 |    9.1352e-06  |
| main/f3/vmess/G0/outer       | M-inner0         |          582 |           96 |  0.342858 |           39 |    8.92759e-06 |
| main/f3/vmess/G0/outer       | M-inner1         |          582 |           96 |  0.794644 |           66 |    9.49696e-06 |
| main/f3/vmess/G0/outer       | M-inner1         |          582 |           96 |  0.985081 |           76 |    8.23119e-06 |
| main/f3/vmess/G0/outer       | M-inner1         |          582 |           96 |  0.68817  |           59 |    8.6551e-06  |
| main/f3/vmess/G0/outer       | M-inner1         |          582 |           96 |  0.419948 |           43 |    9.55176e-06 |
| main/f3/vmess/G1/outer       | I-inner0         |          978 |          162 |  0.949437 |           76 |    9.55446e-06 |
| main/f3/vmess/G1/outer       | I-inner0         |          978 |          162 |  1.08609  |           83 |    8.93112e-06 |
| main/f3/vmess/G1/outer       | I-inner0         |          978 |          162 |  0.769313 |           66 |    8.19652e-06 |
| main/f3/vmess/G1/outer       | I-inner0         |          978 |          162 |  0.486481 |           48 |    9.78589e-06 |
| main/f3/vmess/G1/outer       | I-inner1         |          978 |          162 |  1.24361  |           89 |    9.0659e-06  |
| main/f3/vmess/G1/outer       | I-inner1         |          978 |          162 |  1.40995  |           97 |    8.81964e-06 |
| main/f3/vmess/G1/outer       | I-inner1         |          978 |          162 |  0.98477  |           77 |    8.87142e-06 |
| main/f3/vmess/G1/outer       | I-inner1         |          978 |          162 |  0.557114 |           53 |    9.27876e-06 |
| main/f3/vmess/G1/outer       | J-inner0         |          978 |          162 |  0.793517 |           66 |    9.79773e-06 |
| main/f3/vmess/G1/outer       | J-inner0         |          978 |          162 |  0.924978 |           73 |    9.375e-06   |
| main/f3/vmess/G1/outer       | J-inner0         |          978 |          162 |  0.667905 |           58 |    9.6728e-06  |
| main/f3/vmess/G1/outer       | J-inner0         |          978 |          162 |  0.400241 |           42 |    9.03029e-06 |
| main/f3/vmess/G1/outer       | J-inner1         |          978 |          162 |  0.767474 |           68 |    9.18642e-06 |
| main/f3/vmess/G1/outer       | J-inner1         |          978 |          162 |  0.879794 |           73 |    9.98646e-06 |
| main/f3/vmess/G1/outer       | J-inner1         |          978 |          162 |  0.603183 |           57 |    9.15837e-06 |
| main/f3/vmess/G1/outer       | J-inner1         |          978 |          162 |  0.408035 |           43 |    9.53088e-06 |
| main/f3/vmess/G1/outer       | M-inner0         |          582 |           96 |  0.729446 |           64 |    7.78926e-06 |
| main/f3/vmess/G1/outer       | M-inner0         |          582 |           96 |  0.818294 |           69 |    9.71526e-06 |
| main/f3/vmess/G1/outer       | M-inner0         |          582 |           96 |  0.58042  |           55 |    9.30459e-06 |
| main/f3/vmess/G1/outer       | M-inner0         |          582 |           96 |  0.359721 |           40 |    8.20977e-06 |
| main/f3/vmess/G1/outer       | M-inner1         |          582 |           96 |  0.817749 |           68 |    6.82566e-06 |
| main/f3/vmess/G1/outer       | M-inner1         |          582 |           96 |  0.908473 |           72 |    7.49541e-06 |
| main/f3/vmess/G1/outer       | M-inner1         |          582 |           96 |  0.579184 |           55 |    8.84848e-06 |
| main/f3/vmess/G1/outer       | M-inner1         |          582 |           96 |  0.38338  |           42 |    9.0474e-06  |
| main/f3/vmess/G2/outer       | I-inner0         |          978 |          162 |  0.868718 |           71 |    9.42219e-06 |
| main/f3/vmess/G2/outer       | I-inner0         |          978 |          162 |  0.939326 |           75 |    9.97857e-06 |
| main/f3/vmess/G2/outer       | I-inner0         |          978 |          162 |  0.706486 |           62 |    9.95259e-06 |
| main/f3/vmess/G2/outer       | I-inner0         |          978 |          162 |  0.447963 |           46 |    9.28706e-06 |
| main/f3/vmess/G2/outer       | I-inner1         |          978 |          162 |  1.12788  |           81 |    9.57959e-06 |
| main/f3/vmess/G2/outer       | I-inner1         |          978 |          162 |  1.26004  |           88 |    8.71144e-06 |
| main/f3/vmess/G2/outer       | I-inner1         |          978 |          162 |  0.82976  |           68 |    9.56423e-06 |
| main/f3/vmess/G2/outer       | I-inner1         |          978 |          162 |  0.52045  |           51 |    8.24462e-06 |
| main/f3/vmess/G2/outer       | J-inner0         |          978 |          162 |  0.888818 |           73 |    9.89752e-06 |
| main/f3/vmess/G2/outer       | J-inner0         |          978 |          162 |  1.00574  |           80 |    9.88637e-06 |
| main/f3/vmess/G2/outer       | J-inner0         |          978 |          162 |  0.709686 |           63 |    8.98744e-06 |
| main/f3/vmess/G2/outer       | J-inner0         |          978 |          162 |  0.449509 |           47 |    9.23854e-06 |
| main/f3/vmess/G2/outer       | J-inner1         |          978 |          162 |  0.981085 |           75 |    9.81134e-06 |
| main/f3/vmess/G2/outer       | J-inner1         |          978 |          162 |  1.16486  |           83 |    9.58812e-06 |
| main/f3/vmess/G2/outer       | J-inner1         |          978 |          162 |  0.752374 |           64 |    9.01303e-06 |
| main/f3/vmess/G2/outer       | J-inner1         |          978 |          162 |  0.459919 |           46 |    9.31153e-06 |
| main/f3/vmess/G2/outer       | M-inner0         |          582 |           96 |  0.582909 |           57 |    8.97763e-06 |
| main/f3/vmess/G2/outer       | M-inner0         |          582 |           96 |  0.676196 |           63 |    9.7212e-06  |
| main/f3/vmess/G2/outer       | M-inner0         |          582 |           96 |  0.516521 |           52 |    8.31906e-06 |
| main/f3/vmess/G2/outer       | M-inner0         |          582 |           96 |  0.342752 |           39 |    9.01177e-06 |
| main/f3/vmess/G2/outer       | M-inner1         |          582 |           96 |  0.783535 |           66 |    8.45487e-06 |
| main/f3/vmess/G2/outer       | M-inner1         |          582 |           96 |  0.963067 |           75 |    8.40525e-06 |
| main/f3/vmess/G2/outer       | M-inner1         |          582 |           96 |  0.612869 |           56 |    9.32008e-06 |
| main/f3/vmess/G2/outer       | M-inner1         |          582 |           96 |  0.4111   |           43 |    8.18661e-06 |
| main/f4/shadowsocks/G0/outer | I-inner0         |          978 |          162 |  1.18233  |           87 |    9.39265e-06 |
| main/f4/shadowsocks/G0/outer | I-inner0         |          978 |          162 |  1.37726  |           95 |    9.71797e-06 |
| main/f4/shadowsocks/G0/outer | I-inner0         |          978 |          162 |  0.946535 |           75 |    9.84421e-06 |
| main/f4/shadowsocks/G0/outer | I-inner0         |          978 |          162 |  0.588127 |           56 |    9.35039e-06 |
| main/f4/shadowsocks/G0/outer | I-inner1         |          978 |          162 |  1.53562  |           99 |    9.635e-06   |
| main/f4/shadowsocks/G0/outer | I-inner1         |          978 |          162 |  1.61156  |          104 |    9.93291e-06 |
| main/f4/shadowsocks/G0/outer | I-inner1         |          978 |          162 |  1.25014  |           87 |    8.87217e-06 |
| main/f4/shadowsocks/G0/outer | I-inner1         |          978 |          162 |  0.750351 |           64 |    9.53841e-06 |
| main/f4/shadowsocks/G0/outer | J-inner0         |          978 |          162 |  0.920287 |           73 |    9.34746e-06 |
| main/f4/shadowsocks/G0/outer | J-inner0         |          978 |          162 |  1.05413  |           79 |    9.02803e-06 |
| main/f4/shadowsocks/G0/outer | J-inner0         |          978 |          162 |  0.68361  |           61 |    9.4381e-06  |
| main/f4/shadowsocks/G0/outer | J-inner0         |          978 |          162 |  0.441774 |           45 |    9.45606e-06 |
| main/f4/shadowsocks/G0/outer | J-inner1         |          978 |          162 |  1.19751  |           84 |    9.35753e-06 |
| main/f4/shadowsocks/G0/outer | J-inner1         |          978 |          162 |  1.32646  |           89 |    9.59877e-06 |
| main/f4/shadowsocks/G0/outer | J-inner1         |          978 |          162 |  0.818212 |           68 |    9.80203e-06 |
| main/f4/shadowsocks/G0/outer | J-inner1         |          978 |          162 |  0.534891 |           52 |    9.17964e-06 |
| main/f4/shadowsocks/G0/outer | M-inner0         |          582 |           96 |  0.640205 |           60 |    9.09389e-06 |
| main/f4/shadowsocks/G0/outer | M-inner0         |          582 |           96 |  0.771805 |           67 |    9.71983e-06 |
| main/f4/shadowsocks/G0/outer | M-inner0         |          582 |           96 |  0.527668 |           52 |    7.85805e-06 |
| main/f4/shadowsocks/G0/outer | M-inner0         |          582 |           96 |  0.328575 |           38 |    9.52708e-06 |
| main/f4/shadowsocks/G0/outer | M-inner1         |          582 |           96 |  1.11336  |           81 |    8.76221e-06 |
| main/f4/shadowsocks/G0/outer | M-inner1         |          582 |           96 |  1.20696  |           86 |    9.69118e-06 |
| main/f4/shadowsocks/G0/outer | M-inner1         |          582 |           96 |  0.853836 |           70 |    9.9174e-06  |
| main/f4/shadowsocks/G0/outer | M-inner1         |          582 |           96 |  0.535082 |           52 |    8.04582e-06 |
| main/f4/shadowsocks/G1/outer | I-inner0         |          978 |          162 |  1.47654  |           94 |    9.92843e-06 |
| main/f4/shadowsocks/G1/outer | I-inner0         |          978 |          162 |  1.60042  |          100 |    9.50145e-06 |
| main/f4/shadowsocks/G1/outer | I-inner0         |          978 |          162 |  1.2241   |           85 |    9.53379e-06 |
| main/f4/shadowsocks/G1/outer | I-inner0         |          978 |          162 |  0.755896 |           63 |    9.65423e-06 |
| main/f4/shadowsocks/G1/outer | I-inner1         |          978 |          162 |  1.02633  |           78 |    9.93928e-06 |
| main/f4/shadowsocks/G1/outer | I-inner1         |          978 |          162 |  1.19258  |           85 |    9.67045e-06 |
| main/f4/shadowsocks/G1/outer | I-inner1         |          978 |          162 |  0.804006 |           67 |    8.6733e-06  |
| main/f4/shadowsocks/G1/outer | I-inner1         |          978 |          162 |  0.495872 |           49 |    8.78546e-06 |
| main/f4/shadowsocks/G1/outer | J-inner0         |          978 |          162 |  1.0288   |           78 |    9.7684e-06  |
| main/f4/shadowsocks/G1/outer | J-inner0         |          978 |          162 |  1.20634  |           84 |    9.93508e-06 |
| main/f4/shadowsocks/G1/outer | J-inner0         |          978 |          162 |  0.803982 |           67 |    9.85287e-06 |
| main/f4/shadowsocks/G1/outer | J-inner0         |          978 |          162 |  0.509072 |           50 |    7.72271e-06 |
| main/f4/shadowsocks/G1/outer | J-inner1         |          978 |          162 |  0.945055 |           76 |    9.8527e-06  |
| main/f4/shadowsocks/G1/outer | J-inner1         |          978 |          162 |  1.01706  |           79 |    8.84672e-06 |
| main/f4/shadowsocks/G1/outer | J-inner1         |          978 |          162 |  0.788274 |           68 |    8.58941e-06 |
| main/f4/shadowsocks/G1/outer | J-inner1         |          978 |          162 |  0.529435 |           52 |    9.85984e-06 |
| main/f4/shadowsocks/G1/outer | M-inner0         |          582 |           96 |  1.01813  |           79 |    9.78958e-06 |
| main/f4/shadowsocks/G1/outer | M-inner0         |          582 |           96 |  1.12379  |           85 |    9.77857e-06 |
| main/f4/shadowsocks/G1/outer | M-inner0         |          582 |           96 |  0.807676 |           67 |    9.62639e-06 |
| main/f4/shadowsocks/G1/outer | M-inner0         |          582 |           96 |  0.505499 |           50 |    9.43239e-06 |
| main/f4/shadowsocks/G1/outer | M-inner1         |          582 |           96 |  0.837973 |           69 |    9.75937e-06 |
| main/f4/shadowsocks/G1/outer | M-inner1         |          582 |           96 |  0.964975 |           75 |    9.96584e-06 |
| main/f4/shadowsocks/G1/outer | M-inner1         |          582 |           96 |  0.642326 |           59 |    9.5765e-06  |
| main/f4/shadowsocks/G1/outer | M-inner1         |          582 |           96 |  0.380183 |           42 |    9.71772e-06 |
| main/f4/shadowsocks/G2/outer | I-inner0         |          978 |          162 |  1.1474   |           82 |    9.82598e-06 |
| main/f4/shadowsocks/G2/outer | I-inner0         |          978 |          162 |  1.36059  |           91 |    9.82885e-06 |
| main/f4/shadowsocks/G2/outer | I-inner0         |          978 |          162 |  0.85178  |           69 |    9.48016e-06 |
| main/f4/shadowsocks/G2/outer | I-inner0         |          978 |          162 |  0.534748 |           51 |    9.16114e-06 |
| main/f4/shadowsocks/G2/outer | I-inner1         |          978 |          162 |  1.19722  |           85 |    9.85548e-06 |
| main/f4/shadowsocks/G2/outer | I-inner1         |          978 |          162 |  1.31621  |           90 |    9.85332e-06 |
| main/f4/shadowsocks/G2/outer | I-inner1         |          978 |          162 |  0.864019 |           70 |    9.02522e-06 |
| main/f4/shadowsocks/G2/outer | I-inner1         |          978 |          162 |  0.566042 |           53 |    9.59905e-06 |
| main/f4/shadowsocks/G2/outer | J-inner0         |          978 |          162 |  0.993454 |           78 |    7.61918e-06 |
| main/f4/shadowsocks/G2/outer | J-inner0         |          978 |          162 |  1.06587  |           81 |    9.65604e-06 |
| main/f4/shadowsocks/G2/outer | J-inner0         |          978 |          162 |  0.695746 |           62 |    9.3058e-06  |
| main/f4/shadowsocks/G2/outer | J-inner0         |          978 |          162 |  0.457339 |           46 |    9.43686e-06 |
| main/f4/shadowsocks/G2/outer | J-inner1         |          978 |          162 |  0.876749 |           71 |    9.22612e-06 |
| main/f4/shadowsocks/G2/outer | J-inner1         |          978 |          162 |  0.995226 |           77 |    9.32426e-06 |
| main/f4/shadowsocks/G2/outer | J-inner1         |          978 |          162 |  0.617937 |           57 |    9.94332e-06 |
| main/f4/shadowsocks/G2/outer | J-inner1         |          978 |          162 |  0.409975 |           44 |    9.25062e-06 |
| main/f4/shadowsocks/G2/outer | M-inner0         |          582 |           96 |  0.695503 |           62 |    9.51599e-06 |
| main/f4/shadowsocks/G2/outer | M-inner0         |          582 |           96 |  0.7281   |           65 |    9.9168e-06  |
| main/f4/shadowsocks/G2/outer | M-inner0         |          582 |           96 |  0.572172 |           54 |    8.8884e-06  |
| main/f4/shadowsocks/G2/outer | M-inner0         |          582 |           96 |  0.408501 |           43 |    6.6108e-06  |
| main/f4/shadowsocks/G2/outer | M-inner1         |          582 |           96 |  0.660204 |           59 |    9.24202e-06 |
| main/f4/shadowsocks/G2/outer | M-inner1         |          582 |           96 |  0.770326 |           64 |    7.53941e-06 |
| main/f4/shadowsocks/G2/outer | M-inner1         |          582 |           96 |  0.489359 |           49 |    9.46202e-06 |
| main/f4/shadowsocks/G2/outer | M-inner1         |          582 |           96 |  0.350473 |           40 |    6.96058e-06 |
| main/f4/trojan/G0/outer      | I-inner0         |          978 |          162 |  0.768465 |           64 |    9.72031e-06 |
| main/f4/trojan/G0/outer      | I-inner0         |          978 |          162 |  0.851854 |           68 |    9.88055e-06 |
| main/f4/trojan/G0/outer      | I-inner0         |          978 |          162 |  0.6104   |           53 |    9.51705e-06 |
| main/f4/trojan/G0/outer      | I-inner0         |          978 |          162 |  0.402842 |           41 |    8.03945e-06 |
| main/f4/trojan/G0/outer      | I-inner1         |          978 |          162 |  1.35773  |           91 |    9.06524e-06 |
| main/f4/trojan/G0/outer      | I-inner1         |          978 |          162 |  1.51585  |           97 |    9.64138e-06 |
| main/f4/trojan/G0/outer      | I-inner1         |          978 |          162 |  1.02381  |           77 |    9.55632e-06 |
| main/f4/trojan/G0/outer      | I-inner1         |          978 |          162 |  0.595265 |           54 |    9.19715e-06 |
| main/f4/trojan/G0/outer      | J-inner0         |          978 |          162 |  0.723033 |           62 |    9.73014e-06 |
| main/f4/trojan/G0/outer      | J-inner0         |          978 |          162 |  0.868145 |           70 |    9.85516e-06 |
| main/f4/trojan/G0/outer      | J-inner0         |          978 |          162 |  0.578856 |           54 |    8.38263e-06 |
| main/f4/trojan/G0/outer      | J-inner0         |          978 |          162 |  0.374184 |           40 |    9.92568e-06 |
| main/f4/trojan/G0/outer      | J-inner1         |          978 |          162 |  1.01975  |           77 |    9.35909e-06 |
| main/f4/trojan/G0/outer      | J-inner1         |          978 |          162 |  1.1931   |           85 |    9.44831e-06 |
| main/f4/trojan/G0/outer      | J-inner1         |          978 |          162 |  0.806392 |           65 |    9.87823e-06 |
| main/f4/trojan/G0/outer      | J-inner1         |          978 |          162 |  0.496362 |           48 |    9.30656e-06 |
| main/f4/trojan/G0/outer      | M-inner0         |          582 |           96 |  0.627213 |           58 |    9.22328e-06 |
| main/f4/trojan/G0/outer      | M-inner0         |          582 |           96 |  0.714394 |           63 |    8.61102e-06 |
| main/f4/trojan/G0/outer      | M-inner0         |          582 |           96 |  0.486862 |           49 |    9.53701e-06 |
| main/f4/trojan/G0/outer      | M-inner0         |          582 |           96 |  0.318714 |           37 |    8.9664e-06  |
| main/f4/trojan/G0/outer      | M-inner1         |          582 |           96 |  0.807907 |           68 |    9.40211e-06 |
| main/f4/trojan/G0/outer      | M-inner1         |          582 |           96 |  0.928006 |           73 |    9.3866e-06  |
| main/f4/trojan/G0/outer      | M-inner1         |          582 |           96 |  0.692506 |           58 |    8.66158e-06 |
| main/f4/trojan/G0/outer      | M-inner1         |          582 |           96 |  0.425223 |           44 |    9.97672e-06 |
| main/f4/trojan/G1/outer      | I-inner0         |          978 |          162 |  1.71588  |          101 |    9.42114e-06 |
| main/f4/trojan/G1/outer      | I-inner0         |          978 |          162 |  1.84031  |          108 |    9.7814e-06  |
| main/f4/trojan/G1/outer      | I-inner0         |          978 |          162 |  1.20703  |           84 |    9.62994e-06 |
| main/f4/trojan/G1/outer      | I-inner0         |          978 |          162 |  0.694084 |           61 |    9.92902e-06 |
| main/f4/trojan/G1/outer      | I-inner1         |          978 |          162 |  0.966922 |           74 |    9.84922e-06 |
| main/f4/trojan/G1/outer      | I-inner1         |          978 |          162 |  1.07762  |           80 |    9.57321e-06 |
| main/f4/trojan/G1/outer      | I-inner1         |          978 |          162 |  0.758422 |           64 |    9.9607e-06  |
| main/f4/trojan/G1/outer      | I-inner1         |          978 |          162 |  0.5446   |           52 |    8.00004e-06 |
| main/f4/trojan/G1/outer      | J-inner0         |          978 |          162 |  1.02845  |           76 |    9.79241e-06 |
| main/f4/trojan/G1/outer      | J-inner0         |          978 |          162 |  1.20647  |           85 |    9.69135e-06 |
| main/f4/trojan/G1/outer      | J-inner0         |          978 |          162 |  0.789111 |           65 |    9.82352e-06 |
| main/f4/trojan/G1/outer      | J-inner0         |          978 |          162 |  0.493998 |           48 |    8.95967e-06 |
| main/f4/trojan/G1/outer      | J-inner1         |          978 |          162 |  0.853157 |           70 |    9.47037e-06 |
| main/f4/trojan/G1/outer      | J-inner1         |          978 |          162 |  0.908307 |           73 |    9.5586e-06  |
| main/f4/trojan/G1/outer      | J-inner1         |          978 |          162 |  0.688812 |           61 |    9.3308e-06  |
| main/f4/trojan/G1/outer      | J-inner1         |          978 |          162 |  0.409869 |           43 |    9.48009e-06 |
| main/f4/trojan/G1/outer      | M-inner0         |          582 |           96 |  0.777484 |           67 |    8.89601e-06 |
| main/f4/trojan/G1/outer      | M-inner0         |          582 |           96 |  0.823186 |           70 |    9.66097e-06 |
| main/f4/trojan/G1/outer      | M-inner0         |          582 |           96 |  0.656914 |           58 |    9.68934e-06 |
| main/f4/trojan/G1/outer      | M-inner0         |          582 |           96 |  0.429711 |           44 |    7.92773e-06 |
| main/f4/trojan/G1/outer      | M-inner1         |          582 |           96 |  0.784457 |           65 |    9.35215e-06 |
| main/f4/trojan/G1/outer      | M-inner1         |          582 |           96 |  0.848988 |           68 |    9.43822e-06 |
| main/f4/trojan/G1/outer      | M-inner1         |          582 |           96 |  0.603397 |           55 |    9.44284e-06 |
| main/f4/trojan/G1/outer      | M-inner1         |          582 |           96 |  0.420972 |           43 |    7.91349e-06 |
| main/f4/trojan/G2/outer      | I-inner0         |          978 |          162 |  1.06764  |           81 |    7.75254e-06 |
| main/f4/trojan/G2/outer      | I-inner0         |          978 |          162 |  1.1626   |           86 |    9.25196e-06 |
| main/f4/trojan/G2/outer      | I-inner0         |          978 |          162 |  0.848984 |           68 |    9.91062e-06 |
| main/f4/trojan/G2/outer      | I-inner0         |          978 |          162 |  0.555429 |           51 |    9.9951e-06  |
| main/f4/trojan/G2/outer      | I-inner1         |          978 |          162 |  0.963492 |           74 |    9.15402e-06 |
| main/f4/trojan/G2/outer      | I-inner1         |          978 |          162 |  1.13354  |           81 |    9.35179e-06 |
| main/f4/trojan/G2/outer      | I-inner1         |          978 |          162 |  0.713604 |           62 |    9.8208e-06  |
| main/f4/trojan/G2/outer      | I-inner1         |          978 |          162 |  0.511814 |           50 |    9.8286e-06  |
| main/f4/trojan/G2/outer      | J-inner0         |          978 |          162 |  0.935675 |           75 |    9.95933e-06 |
| main/f4/trojan/G2/outer      | J-inner0         |          978 |          162 |  1.03513  |           80 |    9.75452e-06 |
| main/f4/trojan/G2/outer      | J-inner0         |          978 |          162 |  0.705099 |           62 |    9.45049e-06 |
| main/f4/trojan/G2/outer      | J-inner0         |          978 |          162 |  0.45194  |           46 |    8.94639e-06 |
| main/f4/trojan/G2/outer      | J-inner1         |          978 |          162 |  0.969416 |           75 |    9.32153e-06 |
| main/f4/trojan/G2/outer      | J-inner1         |          978 |          162 |  1.13257  |           83 |    9.17427e-06 |
| main/f4/trojan/G2/outer      | J-inner1         |          978 |          162 |  0.811104 |           67 |    8.6026e-06  |
| main/f4/trojan/G2/outer      | J-inner1         |          978 |          162 |  0.469623 |           47 |    9.08908e-06 |
| main/f4/trojan/G2/outer      | M-inner0         |          582 |           96 |  0.752697 |           64 |    7.83174e-06 |
| main/f4/trojan/G2/outer      | M-inner0         |          582 |           96 |  0.787378 |           67 |    8.72015e-06 |
| main/f4/trojan/G2/outer      | M-inner0         |          582 |           96 |  0.545424 |           53 |    9.89917e-06 |
| main/f4/trojan/G2/outer      | M-inner0         |          582 |           96 |  0.35257  |           39 |    9.00882e-06 |
| main/f4/trojan/G2/outer      | M-inner1         |          582 |           96 |  0.669595 |           59 |    8.62573e-06 |
| main/f4/trojan/G2/outer      | M-inner1         |          582 |           96 |  0.7489   |           63 |    7.89284e-06 |
| main/f4/trojan/G2/outer      | M-inner1         |          582 |           96 |  0.523285 |           51 |    9.05818e-06 |
| main/f4/trojan/G2/outer      | M-inner1         |          582 |           96 |  0.339604 |           38 |    9.12191e-06 |
| main/f4/vless/G0/outer       | I-inner0         |          978 |          162 |  0.891655 |           74 |    9.27885e-06 |
| main/f4/vless/G0/outer       | I-inner0         |          978 |          162 |  1.01812  |           80 |    9.70389e-06 |
| main/f4/vless/G0/outer       | I-inner0         |          978 |          162 |  0.729432 |           64 |    9.49619e-06 |
| main/f4/vless/G0/outer       | I-inner0         |          978 |          162 |  0.515494 |           49 |    9.90548e-06 |
| main/f4/vless/G0/outer       | I-inner1         |          978 |          162 |  1.20831  |           85 |    9.106e-06   |
| main/f4/vless/G0/outer       | I-inner1         |          978 |          162 |  1.34197  |           91 |    9.74395e-06 |
| main/f4/vless/G0/outer       | I-inner1         |          978 |          162 |  0.939673 |           73 |    9.6612e-06  |
| main/f4/vless/G0/outer       | I-inner1         |          978 |          162 |  0.561071 |           53 |    8.49966e-06 |
| main/f4/vless/G0/outer       | J-inner0         |          978 |          162 |  0.996399 |           77 |    8.75555e-06 |
| main/f4/vless/G0/outer       | J-inner0         |          978 |          162 |  1.02511  |           79 |    9.91462e-06 |
| main/f4/vless/G0/outer       | J-inner0         |          978 |          162 |  0.760367 |           65 |    9.5207e-06  |
| main/f4/vless/G0/outer       | J-inner0         |          978 |          162 |  0.476513 |           48 |    8.4097e-06  |
| main/f4/vless/G0/outer       | J-inner1         |          978 |          162 |  0.752153 |           66 |    9.72845e-06 |
| main/f4/vless/G0/outer       | J-inner1         |          978 |          162 |  0.875531 |           72 |    9.01346e-06 |
| main/f4/vless/G0/outer       | J-inner1         |          978 |          162 |  0.615617 |           58 |    9.04271e-06 |
| main/f4/vless/G0/outer       | J-inner1         |          978 |          162 |  0.420521 |           44 |    9.63234e-06 |
| main/f4/vless/G0/outer       | M-inner0         |          582 |           96 |  0.691078 |           61 |    9.75217e-06 |
| main/f4/vless/G0/outer       | M-inner0         |          582 |           96 |  0.763741 |           66 |    9.23936e-06 |
| main/f4/vless/G0/outer       | M-inner0         |          582 |           96 |  0.523041 |           51 |    8.38985e-06 |
| main/f4/vless/G0/outer       | M-inner0         |          582 |           96 |  0.348074 |           39 |    9.25416e-06 |
| main/f4/vless/G0/outer       | M-inner1         |          582 |           96 |  0.786794 |           66 |    8.91754e-06 |
| main/f4/vless/G0/outer       | M-inner1         |          582 |           96 |  0.86378  |           71 |    8.5816e-06  |
| main/f4/vless/G0/outer       | M-inner1         |          582 |           96 |  0.53331  |           52 |    8.92012e-06 |
| main/f4/vless/G0/outer       | M-inner1         |          582 |           96 |  0.376573 |           41 |    8.60706e-06 |
| main/f4/vless/G1/outer       | I-inner0         |          978 |          162 |  1.25816  |           87 |    9.52352e-06 |
| main/f4/vless/G1/outer       | I-inner0         |          978 |          162 |  1.53697  |           97 |    8.48118e-06 |
| main/f4/vless/G1/outer       | I-inner0         |          978 |          162 |  0.936112 |           74 |    9.62874e-06 |
| main/f4/vless/G1/outer       | I-inner0         |          978 |          162 |  0.535504 |           52 |    9.85241e-06 |
| main/f4/vless/G1/outer       | I-inner1         |          978 |          162 |  1.39021  |           92 |    9.65374e-06 |
| main/f4/vless/G1/outer       | I-inner1         |          978 |          162 |  1.5817   |           99 |    9.99045e-06 |
| main/f4/vless/G1/outer       | I-inner1         |          978 |          162 |  1.07133  |           78 |    9.46967e-06 |
| main/f4/vless/G1/outer       | I-inner1         |          978 |          162 |  0.640329 |           57 |    9.60029e-06 |
| main/f4/vless/G1/outer       | J-inner0         |          978 |          162 |  0.992321 |           77 |    9.81801e-06 |
| main/f4/vless/G1/outer       | J-inner0         |          978 |          162 |  1.19033  |           85 |    9.54616e-06 |
| main/f4/vless/G1/outer       | J-inner0         |          978 |          162 |  0.804508 |           67 |    9.42373e-06 |
| main/f4/vless/G1/outer       | J-inner0         |          978 |          162 |  0.459232 |           46 |    9.11556e-06 |
| main/f4/vless/G1/outer       | J-inner1         |          978 |          162 |  0.955616 |           76 |    9.75458e-06 |
| main/f4/vless/G1/outer       | J-inner1         |          978 |          162 |  1.03394  |           81 |    9.10528e-06 |
| main/f4/vless/G1/outer       | J-inner1         |          978 |          162 |  0.781099 |           67 |    9.56383e-06 |
| main/f4/vless/G1/outer       | J-inner1         |          978 |          162 |  0.523278 |           51 |    9.28777e-06 |
| main/f4/vless/G1/outer       | M-inner0         |          582 |           96 |  0.830742 |           68 |    9.1023e-06  |
| main/f4/vless/G1/outer       | M-inner0         |          582 |           96 |  0.880855 |           73 |    9.35645e-06 |
| main/f4/vless/G1/outer       | M-inner0         |          582 |           96 |  0.642084 |           59 |    8.10018e-06 |
| main/f4/vless/G1/outer       | M-inner0         |          582 |           96 |  0.389462 |           43 |    7.70035e-06 |
| main/f4/vless/G1/outer       | M-inner1         |          582 |           96 |  0.697144 |           62 |    9.41025e-06 |
| main/f4/vless/G1/outer       | M-inner1         |          582 |           96 |  0.847016 |           69 |    8.925e-06   |
| main/f4/vless/G1/outer       | M-inner1         |          582 |           96 |  0.616917 |           56 |    9.16807e-06 |
| main/f4/vless/G1/outer       | M-inner1         |          582 |           96 |  0.396423 |           41 |    8.46338e-06 |
| main/f4/vless/G2/outer       | I-inner0         |          978 |          162 |  0.799248 |           67 |    9.40008e-06 |
| main/f4/vless/G2/outer       | I-inner0         |          978 |          162 |  0.919685 |           71 |    9.50638e-06 |
| main/f4/vless/G2/outer       | I-inner0         |          978 |          162 |  0.76836  |           64 |    9.39503e-06 |
| main/f4/vless/G2/outer       | I-inner0         |          978 |          162 |  0.506479 |           49 |    8.76177e-06 |
| main/f4/vless/G2/outer       | I-inner1         |          978 |          162 |  0.941296 |           74 |    9.69158e-06 |
| main/f4/vless/G2/outer       | I-inner1         |          978 |          162 |  1.00206  |           77 |    9.17208e-06 |
| main/f4/vless/G2/outer       | I-inner1         |          978 |          162 |  0.722784 |           63 |    9.92763e-06 |
| main/f4/vless/G2/outer       | I-inner1         |          978 |          162 |  0.471704 |           47 |    9.26411e-06 |
| main/f4/vless/G2/outer       | J-inner0         |          978 |          162 |  0.776175 |           64 |    9.37978e-06 |
| main/f4/vless/G2/outer       | J-inner0         |          978 |          162 |  0.863973 |           69 |    9.33948e-06 |
| main/f4/vless/G2/outer       | J-inner0         |          978 |          162 |  0.552471 |           53 |    8.13212e-06 |
| main/f4/vless/G2/outer       | J-inner0         |          978 |          162 |  0.342176 |           38 |    8.85954e-06 |
| main/f4/vless/G2/outer       | J-inner1         |          978 |          162 |  0.77785  |           67 |    9.20343e-06 |
| main/f4/vless/G2/outer       | J-inner1         |          978 |          162 |  0.868753 |           72 |    9.50274e-06 |
| main/f4/vless/G2/outer       | J-inner1         |          978 |          162 |  0.604162 |           57 |    9.87116e-06 |
| main/f4/vless/G2/outer       | J-inner1         |          978 |          162 |  0.391939 |           42 |    9.96712e-06 |
| main/f4/vless/G2/outer       | M-inner0         |          582 |           96 |  0.573835 |           54 |    9.95617e-06 |
| main/f4/vless/G2/outer       | M-inner0         |          582 |           96 |  0.608587 |           58 |    9.75471e-06 |
| main/f4/vless/G2/outer       | M-inner0         |          582 |           96 |  0.496384 |           50 |    9.70839e-06 |
| main/f4/vless/G2/outer       | M-inner0         |          582 |           96 |  0.38994  |           38 |    7.1751e-06  |
| main/f4/vless/G2/outer       | M-inner1         |          582 |           96 |  0.761518 |           64 |    7.41153e-06 |
| main/f4/vless/G2/outer       | M-inner1         |          582 |           96 |  0.785051 |           66 |    9.52398e-06 |
| main/f4/vless/G2/outer       | M-inner1         |          582 |           96 |  0.564256 |           54 |    9.47947e-06 |
| main/f4/vless/G2/outer       | M-inner1         |          582 |           96 |  0.352383 |           39 |    7.59802e-06 |
| main/f4/vmess/G0/outer       | I-inner0         |          978 |          162 |  0.878281 |           69 |    9.84763e-06 |
| main/f4/vmess/G0/outer       | I-inner0         |          978 |          162 |  1.02974  |           74 |    9.84934e-06 |
| main/f4/vmess/G0/outer       | I-inner0         |          978 |          162 |  0.660442 |           59 |    9.71976e-06 |
| main/f4/vmess/G0/outer       | I-inner0         |          978 |          162 |  0.425248 |           44 |    8.32649e-06 |
| main/f4/vmess/G0/outer       | I-inner1         |          978 |          162 |  1.03868  |           78 |    8.58943e-06 |
| main/f4/vmess/G0/outer       | I-inner1         |          978 |          162 |  1.16664  |           85 |    9.60986e-06 |
| main/f4/vmess/G0/outer       | I-inner1         |          978 |          162 |  0.821371 |           67 |    9.79693e-06 |
| main/f4/vmess/G0/outer       | I-inner1         |          978 |          162 |  0.49246  |           48 |    9.76871e-06 |
| main/f4/vmess/G0/outer       | J-inner0         |          978 |          162 |  0.956228 |           74 |    9.61074e-06 |
| main/f4/vmess/G0/outer       | J-inner0         |          978 |          162 |  1.14704  |           80 |    9.0666e-06  |
| main/f4/vmess/G0/outer       | J-inner0         |          978 |          162 |  0.724017 |           63 |    9.063e-06   |
| main/f4/vmess/G0/outer       | J-inner0         |          978 |          162 |  0.467478 |           47 |    9.55289e-06 |
| main/f4/vmess/G0/outer       | J-inner1         |          978 |          162 |  0.916241 |           75 |    9.71863e-06 |
| main/f4/vmess/G0/outer       | J-inner1         |          978 |          162 |  1.05331  |           81 |    9.55309e-06 |
| main/f4/vmess/G0/outer       | J-inner1         |          978 |          162 |  0.749338 |           64 |    9.52367e-06 |
| main/f4/vmess/G0/outer       | J-inner1         |          978 |          162 |  0.490632 |           48 |    8.45941e-06 |
| main/f4/vmess/G0/outer       | M-inner0         |          582 |           96 |  0.745078 |           65 |    7.36115e-06 |
| main/f4/vmess/G0/outer       | M-inner0         |          582 |           96 |  0.777433 |           67 |    9.92173e-06 |
| main/f4/vmess/G0/outer       | M-inner0         |          582 |           96 |  0.559028 |           53 |    9.00139e-06 |
| main/f4/vmess/G0/outer       | M-inner0         |          582 |           96 |  0.335535 |           38 |    9.68032e-06 |
| main/f4/vmess/G0/outer       | M-inner1         |          582 |           96 |  0.780804 |           65 |    9.93824e-06 |
| main/f4/vmess/G0/outer       | M-inner1         |          582 |           96 |  0.858956 |           68 |    9.52705e-06 |
| main/f4/vmess/G0/outer       | M-inner1         |          582 |           96 |  0.621525 |           55 |    9.72191e-06 |
| main/f4/vmess/G0/outer       | M-inner1         |          582 |           96 |  0.420805 |           43 |    7.04432e-06 |
| main/f4/vmess/G1/outer       | I-inner0         |          978 |          162 |  1.04881  |           79 |    9.88443e-06 |
| main/f4/vmess/G1/outer       | I-inner0         |          978 |          162 |  1.18139  |           85 |    9.66736e-06 |
| main/f4/vmess/G1/outer       | I-inner0         |          978 |          162 |  0.813112 |           67 |    9.26227e-06 |
| main/f4/vmess/G1/outer       | I-inner0         |          978 |          162 |  0.505724 |           50 |    8.34963e-06 |
| main/f4/vmess/G1/outer       | I-inner1         |          978 |          162 |  1.17736  |           86 |    9.1577e-06  |
| main/f4/vmess/G1/outer       | I-inner1         |          978 |          162 |  1.3692   |           95 |    9.52399e-06 |
| main/f4/vmess/G1/outer       | I-inner1         |          978 |          162 |  0.954955 |           74 |    9.46702e-06 |
| main/f4/vmess/G1/outer       | I-inner1         |          978 |          162 |  0.641663 |           58 |    6.55999e-06 |
| main/f4/vmess/G1/outer       | J-inner0         |          978 |          162 |  1.04021  |           78 |    9.1645e-06  |
| main/f4/vmess/G1/outer       | J-inner0         |          978 |          162 |  1.23556  |           84 |    7.47503e-06 |
| main/f4/vmess/G1/outer       | J-inner0         |          978 |          162 |  0.844663 |           68 |    6.9105e-06  |
| main/f4/vmess/G1/outer       | J-inner0         |          978 |          162 |  0.494057 |           48 |    8.1097e-06  |
| main/f4/vmess/G1/outer       | J-inner1         |          978 |          162 |  0.999705 |           77 |    9.27967e-06 |
| main/f4/vmess/G1/outer       | J-inner1         |          978 |          162 |  1.08769  |           82 |    9.15668e-06 |
| main/f4/vmess/G1/outer       | J-inner1         |          978 |          162 |  0.718318 |           63 |    9.84342e-06 |
| main/f4/vmess/G1/outer       | J-inner1         |          978 |          162 |  0.46471  |           47 |    8.6696e-06  |
| main/f4/vmess/G1/outer       | M-inner0         |          582 |           96 |  0.805656 |           68 |    9.51911e-06 |
| main/f4/vmess/G1/outer       | M-inner0         |          582 |           96 |  0.890434 |           73 |    9.28699e-06 |
| main/f4/vmess/G1/outer       | M-inner0         |          582 |           96 |  0.635751 |           58 |    9.19989e-06 |
| main/f4/vmess/G1/outer       | M-inner0         |          582 |           96 |  0.399321 |           42 |    8.34901e-06 |
| main/f4/vmess/G1/outer       | M-inner1         |          582 |           96 |  0.845234 |           70 |    8.90655e-06 |
| main/f4/vmess/G1/outer       | M-inner1         |          582 |           96 |  0.939288 |           75 |    9.56811e-06 |
| main/f4/vmess/G1/outer       | M-inner1         |          582 |           96 |  0.67644  |           60 |    9.4234e-06  |
| main/f4/vmess/G1/outer       | M-inner1         |          582 |           96 |  0.429567 |           44 |    7.39888e-06 |
| main/f4/vmess/G2/outer       | I-inner0         |          978 |          162 |  1.12318  |           80 |    9.90814e-06 |
| main/f4/vmess/G2/outer       | I-inner0         |          978 |          162 |  1.26258  |           85 |    9.73527e-06 |
| main/f4/vmess/G2/outer       | I-inner0         |          978 |          162 |  0.829935 |           68 |    9.89372e-06 |
| main/f4/vmess/G2/outer       | I-inner0         |          978 |          162 |  0.531706 |           52 |    9.56346e-06 |
| main/f4/vmess/G2/outer       | I-inner1         |          978 |          162 |  1.42475  |           97 |    9.41905e-06 |
| main/f4/vmess/G2/outer       | I-inner1         |          978 |          162 |  1.55522  |          104 |    9.28386e-06 |
| main/f4/vmess/G2/outer       | I-inner1         |          978 |          162 |  1.15131  |           83 |    9.45679e-06 |
| main/f4/vmess/G2/outer       | I-inner1         |          978 |          162 |  0.688285 |           60 |    9.2359e-06  |
| main/f4/vmess/G2/outer       | J-inner0         |          978 |          162 |  1.17552  |           85 |    9.46644e-06 |
| main/f4/vmess/G2/outer       | J-inner0         |          978 |          162 |  1.42421  |           94 |    9.19515e-06 |
| main/f4/vmess/G2/outer       | J-inner0         |          978 |          162 |  0.901148 |           72 |    9.86819e-06 |
| main/f4/vmess/G2/outer       | J-inner0         |          978 |          162 |  0.504334 |           50 |    9.06681e-06 |
| main/f4/vmess/G2/outer       | J-inner1         |          978 |          162 |  1.15885  |           86 |    8.99892e-06 |
| main/f4/vmess/G2/outer       | J-inner1         |          978 |          162 |  1.27888  |           92 |    9.53084e-06 |
| main/f4/vmess/G2/outer       | J-inner1         |          978 |          162 |  0.932672 |           74 |    9.96561e-06 |
| main/f4/vmess/G2/outer       | J-inner1         |          978 |          162 |  0.574688 |           54 |    9.20356e-06 |
| main/f4/vmess/G2/outer       | M-inner0         |          582 |           96 |  0.779456 |           65 |    9.98306e-06 |
| main/f4/vmess/G2/outer       | M-inner0         |          582 |           96 |  0.890254 |           72 |    7.52635e-06 |
| main/f4/vmess/G2/outer       | M-inner0         |          582 |           96 |  0.626546 |           57 |    8.47986e-06 |
| main/f4/vmess/G2/outer       | M-inner0         |          582 |           96 |  0.410267 |           42 |    7.39966e-06 |
| main/f4/vmess/G2/outer       | M-inner1         |          582 |           96 |  0.791256 |           65 |    9.97785e-06 |
| main/f4/vmess/G2/outer       | M-inner1         |          582 |           96 |  0.848394 |           67 |    9.29193e-06 |
| main/f4/vmess/G2/outer       | M-inner1         |          582 |           96 |  0.587408 |           55 |    9.01976e-06 |
| main/f4/vmess/G2/outer       | M-inner1         |          582 |           96 |  0.473095 |           47 |    8.72282e-06 |
