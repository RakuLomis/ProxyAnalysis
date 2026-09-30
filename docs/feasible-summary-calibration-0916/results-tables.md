# 可行摘要增广：完整统计表

F1_new从完整六类混淆矩阵取目标两类F1均值；先计算各OOF指标，再平均组/轮换/seed，没有概率集成。

## 总体

| protocol    | arm       |   F1_new |   F1_all |   BA_all |   CE_all_bits |   Brier_all |   CE_new_bits |   Brier_new |
|:------------|:----------|---------:|---------:|---------:|--------------:|------------:|--------------:|------------:|
| SHADOWSOCKS | center    | 0.957334 | 0.959446 | 0.959491 |      0.310475 |    0.077141 |      0.349813 |    0.091642 |
| SHADOWSOCKS | cyclic    | 0.873508 | 0.905276 | 0.907755 |      0.501982 |    0.170021 |      0.644677 |    0.246315 |
| SHADOWSOCKS | group     | 0.896676 | 0.917525 | 0.918866 |      0.471777 |    0.153204 |      0.577347 |    0.206982 |
| SHADOWSOCKS | marginal  | 0.963339 | 0.964534 | 0.964583 |      0.300803 |    0.071798 |      0.317041 |    0.076092 |
| SHADOWSOCKS | paired    | 0.961005 | 0.962720 | 0.962731 |      0.303847 |    0.074152 |      0.344651 |    0.088708 |
| SHADOWSOCKS | raw       | 0.758973 | 0.864246 | 0.879630 |      0.503814 |    0.175004 |      0.948524 |    0.384238 |
| SHADOWSOCKS | reference | 0.958370 | 0.960168 | 0.960185 |      0.286504 |    0.067319 |      0.294794 |    0.068552 |
| VLESS       | center    | 0.537126 | 0.696877 | 0.725694 |      1.061763 |    0.374436 |      1.820888 |    0.631731 |
| VLESS       | cyclic    | 0.582880 | 0.715652 | 0.737616 |      0.865666 |    0.345646 |      1.242648 |    0.526551 |
| VLESS       | group     | 0.652044 | 0.745629 | 0.762153 |      0.829183 |    0.328390 |      1.135333 |    0.475751 |
| VLESS       | marginal  | 0.670577 | 0.752101 | 0.766319 |      0.823391 |    0.315062 |      1.116398 |    0.441921 |
| VLESS       | paired    | 0.747832 | 0.788936 | 0.798495 |      0.773526 |    0.297187 |      0.987750 |    0.398232 |
| VLESS       | raw       | 0.445694 | 0.660628 | 0.713542 |      1.185511 |    0.414508 |      2.388272 |    0.836384 |
| VLESS       | reference | 0.821861 | 0.829010 | 0.835880 |      0.664898 |    0.247835 |      0.690791 |    0.259095 |

## 业务组

| protocol    |   business_group | arm       |   F1_new |   F1_all |   BA_all |   CE_all_bits |   Brier_all |   CE_new_bits |   Brier_new |
|:------------|-----------------:|:----------|---------:|---------:|---------:|--------------:|------------:|--------------:|------------:|
| SHADOWSOCKS |                0 | center    | 0.954876 | 0.959298 | 0.959375 |      0.313137 |    0.080423 |      0.340479 |    0.130731 |
| SHADOWSOCKS |                0 | cyclic    | 0.946055 | 0.950840 | 0.951042 |      0.432849 |    0.132272 |      0.358801 |    0.145078 |
| SHADOWSOCKS |                0 | group     | 0.939483 | 0.947879 | 0.948264 |      0.415962 |    0.123138 |      0.348961 |    0.141193 |
| SHADOWSOCKS |                0 | marginal  | 0.965041 | 0.964867 | 0.964931 |      0.303469 |    0.074613 |      0.274090 |    0.099775 |
| SHADOWSOCKS |                0 | paired    | 0.961472 | 0.963866 | 0.963889 |      0.295909 |    0.071521 |      0.242512 |    0.086361 |
| SHADOWSOCKS |                0 | raw       | 0.903243 | 0.935140 | 0.935764 |      0.387901 |    0.116995 |      0.573730 |    0.226547 |
| SHADOWSOCKS |                0 | reference | 0.956461 | 0.960412 | 0.960417 |      0.289142 |    0.069917 |      0.216543 |    0.079293 |
| SHADOWSOCKS |                1 | center    | 0.956832 | 0.957914 | 0.957986 |      0.311637 |    0.075173 |      0.483555 |    0.084036 |
| SHADOWSOCKS |                1 | cyclic    | 0.864762 | 0.898172 | 0.902431 |      0.501971 |    0.169970 |      0.822789 |    0.266757 |
| SHADOWSOCKS |                1 | group     | 0.903301 | 0.920431 | 0.922222 |      0.466446 |    0.149879 |      0.754807 |    0.225383 |
| SHADOWSOCKS |                1 | marginal  | 0.962097 | 0.962442 | 0.962500 |      0.302073 |    0.069721 |      0.461804 |    0.074539 |
| SHADOWSOCKS |                1 | paired    | 0.955898 | 0.956571 | 0.956597 |      0.316947 |    0.079302 |      0.540789 |    0.112674 |
| SHADOWSOCKS |                1 | raw       | 0.958529 | 0.948526 | 0.948958 |      0.345352 |    0.092885 |      0.462523 |    0.072706 |
| SHADOWSOCKS |                1 | reference | 0.967437 | 0.961786 | 0.961806 |      0.279762 |    0.061930 |      0.446436 |    0.063730 |
| SHADOWSOCKS |                2 | center    | 0.960294 | 0.961127 | 0.961111 |      0.306649 |    0.075828 |      0.225404 |    0.060158 |
| SHADOWSOCKS |                2 | cyclic    | 0.809708 | 0.866817 | 0.869792 |      0.571126 |    0.207822 |      0.752440 |    0.327110 |
| SHADOWSOCKS |                2 | group     | 0.847245 | 0.884266 | 0.886111 |      0.532921 |    0.186596 |      0.628274 |    0.254370 |
| SHADOWSOCKS |                2 | marginal  | 0.962878 | 0.966291 | 0.966319 |      0.296868 |    0.071060 |      0.215229 |    0.053963 |
| SHADOWSOCKS |                2 | paired    | 0.965646 | 0.967722 | 0.967708 |      0.298685 |    0.071632 |      0.250653 |    0.067089 |
| SHADOWSOCKS |                2 | raw       | 0.415146 | 0.709071 | 0.754167 |      0.778188 |    0.315134 |      1.809319 |    0.853460 |
| SHADOWSOCKS |                2 | reference | 0.951213 | 0.958307 | 0.958333 |      0.290607 |    0.070110 |      0.221402 |    0.062634 |
| VLESS       |                0 | center    | 0.517926 | 0.722243 | 0.754514 |      0.858664 |    0.341611 |      1.457406 |    0.679209 |
| VLESS       |                0 | cyclic    | 0.611847 | 0.770643 | 0.792361 |      0.802128 |    0.320044 |      1.060253 |    0.485520 |
| VLESS       |                0 | group     | 0.635649 | 0.780774 | 0.800000 |      0.791909 |    0.311049 |      1.032397 |    0.464648 |
| VLESS       |                0 | marginal  | 0.667071 | 0.777829 | 0.796528 |      0.745651 |    0.289728 |      1.038314 |    0.455861 |
| VLESS       |                0 | paired    | 0.668043 | 0.774655 | 0.788542 |      0.763731 |    0.299662 |      1.020125 |    0.444884 |
| VLESS       |                0 | raw       | 0.489296 | 0.709017 | 0.758333 |      0.935856 |    0.359264 |      1.720115 |    0.744106 |
| VLESS       |                0 | reference | 0.758401 | 0.831865 | 0.839236 |      0.642631 |    0.246540 |      0.775044 |    0.312874 |
| VLESS       |                1 | center    | 0.546671 | 0.641023 | 0.682986 |      1.491252 |    0.450366 |      2.691149 |    0.616923 |
| VLESS       |                1 | cyclic    | 0.674119 | 0.692907 | 0.718750 |      0.991658 |    0.376530 |      1.544702 |    0.531011 |
| VLESS       |                1 | group     | 0.735195 | 0.725372 | 0.748264 |      0.923711 |    0.351757 |      1.337547 |    0.455750 |
| VLESS       |                1 | marginal  | 0.694581 | 0.710120 | 0.732986 |      0.985219 |    0.366498 |      1.294864 |    0.418221 |
| VLESS       |                1 | paired    | 0.844473 | 0.796557 | 0.806944 |      0.821095 |    0.303382 |      0.944933 |    0.316506 |
| VLESS       |                1 | raw       | 0.518530 | 0.619796 | 0.673958 |      1.557250 |    0.458221 |      3.183138 |    0.754645 |
| VLESS       |                1 | reference | 0.931757 | 0.835241 | 0.842361 |      0.674311 |    0.240217 |      0.425179 |    0.114919 |
| VLESS       |                2 | center    | 0.546780 | 0.727366 | 0.739583 |      0.835373 |    0.331331 |      1.314110 |    0.599060 |
| VLESS       |                2 | cyclic    | 0.462673 | 0.683407 | 0.701736 |      0.803211 |    0.340364 |      1.122989 |    0.563121 |
| VLESS       |                2 | group     | 0.585286 | 0.730740 | 0.738194 |      0.771931 |    0.322365 |      1.036055 |    0.506854 |
| VLESS       |                2 | marginal  | 0.650079 | 0.768353 | 0.769444 |      0.739303 |    0.288960 |      1.016017 |    0.451681 |
| VLESS       |                2 | paired    | 0.730981 | 0.795595 | 0.800000 |      0.735752 |    0.288517 |      0.998193 |    0.433306 |
| VLESS       |                2 | raw       | 0.329254 | 0.653071 | 0.708333 |      1.063426 |    0.426039 |      2.261563 |    1.010402 |
| VLESS       |                2 | reference | 0.775423 | 0.819924 | 0.826042 |      0.677751 |    0.256748 |      0.872150 |    0.349492 |

## 全部对照区间

| protocol    |   business_group | contrast         | metric      |     delta |     low95 |    high95 |   adjusted_low |   adjusted_high |   family_size | primary   |
|:------------|-----------------:|:-----------------|:------------|----------:|----------:|----------:|---------------:|----------------:|--------------:|:----------|
| SHADOWSOCKS |               -1 | paired-raw       | F1_new      |  0.202032 |  0.165164 |  0.243989 |       0.155052 |        0.255388 |             4 | True      |
| SHADOWSOCKS |               -1 | paired-raw       | F1_all      |  0.098474 |  0.075876 |  0.122208 |       0.070459 |        0.128754 |             4 | False     |
| SHADOWSOCKS |               -1 | paired-raw       | BA_all      |  0.083102 |  0.062037 |  0.104051 |       0.056539 |        0.110301 |             4 | False     |
| SHADOWSOCKS |               -1 | paired-raw       | CE_all_bits | -0.199967 | -0.237306 | -0.163646 |      -0.247165 |       -0.153184 |             4 | False     |
| SHADOWSOCKS |               -1 | paired-raw       | Brier_all   | -0.100853 | -0.119176 | -0.082803 |      -0.123981 |       -0.078035 |             4 | False     |
| SHADOWSOCKS |               -1 | paired-raw       | CE_new_bits | -0.603872 | -0.698948 | -0.513050 |      -0.725387 |       -0.491871 |             4 | False     |
| SHADOWSOCKS |               -1 | paired-raw       | Brier_new   | -0.295530 | -0.338606 | -0.254266 |      -0.350659 |       -0.243648 |             4 | False     |
| SHADOWSOCKS |               -1 | paired-group     | F1_new      |  0.064329 |  0.041990 |  0.093224 |       0.036417 |        0.102058 |             4 | True      |
| SHADOWSOCKS |               -1 | paired-group     | F1_all      |  0.045194 |  0.027956 |  0.065810 |       0.024234 |        0.071514 |             4 | False     |
| SHADOWSOCKS |               -1 | paired-group     | BA_all      |  0.043866 |  0.026736 |  0.063194 |       0.022858 |        0.068114 |             4 | False     |
| SHADOWSOCKS |               -1 | paired-group     | CE_all_bits | -0.167930 | -0.191029 | -0.143356 |      -0.196436 |       -0.136285 |             4 | False     |
| SHADOWSOCKS |               -1 | paired-group     | Brier_all   | -0.079052 | -0.091936 | -0.066227 |      -0.095021 |       -0.063385 |             4 | False     |
| SHADOWSOCKS |               -1 | paired-group     | CE_new_bits | -0.232696 | -0.262065 | -0.204203 |      -0.269933 |       -0.197100 |             4 | False     |
| SHADOWSOCKS |               -1 | paired-group     | Brier_new   | -0.118274 | -0.135462 | -0.101581 |      -0.140490 |       -0.097618 |             4 | False     |
| SHADOWSOCKS |               -1 | paired-cyclic    | F1_new      |  0.087497 |  0.060894 |  0.123542 |       0.054165 |        0.133369 |             4 | False     |
| SHADOWSOCKS |               -1 | paired-cyclic    | F1_all      |  0.057444 |  0.038399 |  0.079839 |       0.033412 |        0.086443 |             4 | False     |
| SHADOWSOCKS |               -1 | paired-cyclic    | BA_all      |  0.054977 |  0.036111 |  0.075694 |       0.031423 |        0.081597 |             4 | False     |
| SHADOWSOCKS |               -1 | paired-cyclic    | CE_all_bits | -0.198135 | -0.224952 | -0.169586 |      -0.232283 |       -0.161284 |             4 | False     |
| SHADOWSOCKS |               -1 | paired-cyclic    | Brier_all   | -0.095870 | -0.110721 | -0.080982 |      -0.114733 |       -0.076874 |             4 | False     |
| SHADOWSOCKS |               -1 | paired-cyclic    | CE_new_bits | -0.300025 | -0.341551 | -0.259571 |      -0.353070 |       -0.249117 |             4 | False     |
| SHADOWSOCKS |               -1 | paired-cyclic    | Brier_new   | -0.157607 | -0.182299 | -0.134097 |      -0.188997 |       -0.128373 |             4 | False     |
| SHADOWSOCKS |               -1 | paired-center    | F1_new      |  0.003671 | -0.005109 |  0.012506 |      -0.007620 |        0.014948 |             4 | False     |
| SHADOWSOCKS |               -1 | paired-center    | F1_all      |  0.003274 | -0.004463 |  0.010607 |      -0.006749 |        0.012727 |             4 | False     |
| SHADOWSOCKS |               -1 | paired-center    | BA_all      |  0.003241 | -0.004514 |  0.010532 |      -0.006772 |        0.012616 |             4 | False     |
| SHADOWSOCKS |               -1 | paired-center    | CE_all_bits | -0.006628 | -0.030004 |  0.013021 |      -0.036388 |        0.017174 |             4 | False     |
| SHADOWSOCKS |               -1 | paired-center    | Brier_all   | -0.002990 | -0.010846 |  0.004241 |      -0.013085 |        0.005962 |             4 | False     |
| SHADOWSOCKS |               -1 | paired-center    | CE_new_bits | -0.005161 | -0.034769 |  0.021233 |      -0.042422 |        0.026811 |             4 | False     |
| SHADOWSOCKS |               -1 | paired-center    | Brier_new   | -0.002934 | -0.015306 |  0.008078 |      -0.018667 |        0.010666 |             4 | False     |
| SHADOWSOCKS |               -1 | paired-marginal  | F1_new      | -0.002334 | -0.007660 |  0.002544 |      -0.009200 |        0.003745 |             4 | False     |
| SHADOWSOCKS |               -1 | paired-marginal  | F1_all      | -0.001814 | -0.005414 |  0.001235 |      -0.006359 |        0.001783 |             4 | False     |
| SHADOWSOCKS |               -1 | paired-marginal  | BA_all      | -0.001852 | -0.005440 |  0.001157 |      -0.006366 |        0.001736 |             4 | False     |
| SHADOWSOCKS |               -1 | paired-marginal  | CE_all_bits |  0.003044 | -0.002432 |  0.007720 |      -0.004102 |        0.008673 |             4 | False     |
| SHADOWSOCKS |               -1 | paired-marginal  | Brier_all   |  0.002354 |  0.000585 |  0.004112 |       0.000145 |        0.004518 |             4 | False     |
| SHADOWSOCKS |               -1 | paired-marginal  | CE_new_bits |  0.027610 |  0.013268 |  0.040797 |       0.009755 |        0.044158 |             4 | False     |
| SHADOWSOCKS |               -1 | paired-marginal  | Brier_new   |  0.012615 |  0.006075 |  0.019198 |       0.004280 |        0.020705 |             4 | False     |
| SHADOWSOCKS |               -1 | paired-reference | F1_new      |  0.002635 | -0.006453 |  0.012651 |      -0.008259 |        0.015596 |             4 | False     |
| SHADOWSOCKS |               -1 | paired-reference | F1_all      |  0.002552 | -0.004692 |  0.012576 |      -0.005873 |        0.015246 |             4 | False     |
| SHADOWSOCKS |               -1 | paired-reference | BA_all      |  0.002546 | -0.004633 |  0.012616 |      -0.005903 |        0.015278 |             4 | False     |
| SHADOWSOCKS |               -1 | paired-reference | CE_all_bits |  0.017343 | -0.002747 |  0.035013 |      -0.008294 |        0.038815 |             4 | False     |
| SHADOWSOCKS |               -1 | paired-reference | Brier_all   |  0.006833 |  0.000613 |  0.012583 |      -0.000985 |        0.013897 |             4 | False     |
| SHADOWSOCKS |               -1 | paired-reference | CE_new_bits |  0.049857 |  0.022051 |  0.074144 |       0.013753 |        0.079613 |             4 | False     |
| SHADOWSOCKS |               -1 | paired-reference | Brier_new   |  0.020156 |  0.009049 |  0.031074 |       0.006119 |        0.033609 |             4 | False     |
| SHADOWSOCKS |                0 | paired-raw       | F1_new      |  0.058229 |  0.008408 |  0.116909 |      -0.007329 |        0.147225 |            12 | False     |
| SHADOWSOCKS |                0 | paired-raw       | F1_all      |  0.028726 |  0.003178 |  0.056213 |      -0.006473 |        0.067168 |            12 | False     |
| SHADOWSOCKS |                0 | paired-raw       | BA_all      |  0.028125 |  0.002778 |  0.055208 |      -0.006944 |        0.066031 |            12 | False     |
| SHADOWSOCKS |                0 | paired-raw       | CE_all_bits | -0.091992 | -0.147950 | -0.040214 |      -0.170645 |       -0.020324 |            12 | False     |
| SHADOWSOCKS |                0 | paired-raw       | Brier_all   | -0.045474 | -0.064934 | -0.027761 |      -0.072453 |       -0.020863 |            12 | False     |
| SHADOWSOCKS |                0 | paired-raw       | CE_new_bits | -0.331217 | -0.479425 | -0.205662 |      -0.545796 |       -0.170206 |            12 | False     |
| SHADOWSOCKS |                0 | paired-raw       | Brier_new   | -0.140186 | -0.189335 | -0.097180 |      -0.211993 |       -0.081778 |            12 | False     |
| SHADOWSOCKS |                0 | paired-group     | F1_new      |  0.021988 | -0.002396 |  0.053067 |      -0.011066 |        0.066429 |            12 | False     |
| SHADOWSOCKS |                0 | paired-group     | F1_all      |  0.015987 | -0.000884 |  0.034442 |      -0.007394 |        0.042793 |            12 | False     |
| SHADOWSOCKS |                0 | paired-group     | BA_all      |  0.015625 | -0.001042 |  0.033681 |      -0.007986 |        0.041667 |            12 | False     |
| SHADOWSOCKS |                0 | paired-group     | CE_all_bits | -0.120053 | -0.143232 | -0.095917 |      -0.154135 |       -0.086650 |            12 | False     |
| SHADOWSOCKS |                0 | paired-group     | Brier_all   | -0.051616 | -0.064082 | -0.039405 |      -0.070219 |       -0.034566 |            12 | False     |
| SHADOWSOCKS |                0 | paired-group     | CE_new_bits | -0.106449 | -0.162717 | -0.045359 |      -0.179451 |       -0.019621 |            12 | False     |
| SHADOWSOCKS |                0 | paired-group     | Brier_new   | -0.054832 | -0.084064 | -0.024838 |      -0.093415 |       -0.012653 |            12 | False     |
| SHADOWSOCKS |                0 | paired-cyclic    | F1_new      |  0.015417 | -0.008448 |  0.042059 |      -0.017353 |        0.054062 |            12 | False     |
| SHADOWSOCKS |                0 | paired-cyclic    | F1_all      |  0.013027 | -0.003704 |  0.030452 |      -0.010563 |        0.038113 |            12 | False     |
| SHADOWSOCKS |                0 | paired-cyclic    | BA_all      |  0.012847 | -0.003819 |  0.030208 |      -0.010764 |        0.037847 |            12 | False     |
| SHADOWSOCKS |                0 | paired-cyclic    | CE_all_bits | -0.136940 | -0.160391 | -0.111059 |      -0.170098 |       -0.100739 |            12 | False     |
| SHADOWSOCKS |                0 | paired-cyclic    | Brier_all   | -0.060751 | -0.073222 | -0.047820 |      -0.078480 |       -0.042508 |            12 | False     |
| SHADOWSOCKS |                0 | paired-cyclic    | CE_new_bits | -0.116289 | -0.170315 | -0.049989 |      -0.184895 |       -0.020110 |            12 | False     |
| SHADOWSOCKS |                0 | paired-cyclic    | Brier_new   | -0.058717 | -0.086594 | -0.026799 |      -0.095163 |       -0.013772 |            12 | False     |
| SHADOWSOCKS |                0 | paired-center    | F1_new      |  0.006596 | -0.013607 |  0.028268 |      -0.021457 |        0.038140 |            12 | False     |
| SHADOWSOCKS |                0 | paired-center    | F1_all      |  0.004569 | -0.009021 |  0.017923 |      -0.015211 |        0.023679 |            12 | False     |
| SHADOWSOCKS |                0 | paired-center    | BA_all      |  0.004514 | -0.009028 |  0.017708 |      -0.015278 |        0.023264 |            12 | False     |
| SHADOWSOCKS |                0 | paired-center    | CE_all_bits | -0.017228 | -0.045086 |  0.007269 |      -0.057688 |        0.015055 |            12 | False     |
| SHADOWSOCKS |                0 | paired-center    | Brier_all   | -0.008902 | -0.021045 |  0.001880 |      -0.026360 |        0.005432 |            12 | False     |
| SHADOWSOCKS |                0 | paired-center    | CE_new_bits | -0.097966 | -0.177735 | -0.028601 |      -0.211012 |       -0.009801 |            12 | False     |
| SHADOWSOCKS |                0 | paired-center    | Brier_new   | -0.044370 | -0.078186 | -0.015012 |      -0.093479 |       -0.006144 |            12 | False     |
| SHADOWSOCKS |                0 | paired-marginal  | F1_new      | -0.003569 | -0.013615 |  0.005775 |      -0.018463 |        0.008903 |            12 | False     |
| SHADOWSOCKS |                0 | paired-marginal  | F1_all      | -0.001001 | -0.008526 |  0.005600 |      -0.011896 |        0.008089 |            12 | False     |
| SHADOWSOCKS |                0 | paired-marginal  | BA_all      | -0.001042 | -0.008681 |  0.005556 |      -0.011806 |        0.007986 |            12 | False     |
| SHADOWSOCKS |                0 | paired-marginal  | CE_all_bits | -0.007560 | -0.013855 | -0.001760 |      -0.016630 |        0.000495 |            12 | False     |
| SHADOWSOCKS |                0 | paired-marginal  | Brier_all   | -0.003091 | -0.006340 | -0.000085 |      -0.007896 |        0.000881 |            12 | False     |
| SHADOWSOCKS |                0 | paired-marginal  | CE_new_bits | -0.031578 | -0.043370 | -0.021811 |      -0.048621 |       -0.018788 |            12 | False     |
| SHADOWSOCKS |                0 | paired-marginal  | Brier_new   | -0.013414 | -0.017254 | -0.009694 |      -0.018911 |       -0.008197 |            12 | False     |
| SHADOWSOCKS |                0 | paired-reference | F1_new      |  0.005011 |  0.000562 |  0.010717 |       0.000000 |        0.013396 |            12 | False     |
| SHADOWSOCKS |                0 | paired-reference | F1_all      |  0.003455 |  0.000006 |  0.007966 |      -0.001000 |        0.010058 |            12 | False     |
| SHADOWSOCKS |                0 | paired-reference | BA_all      |  0.003472 |  0.000000 |  0.007986 |      -0.001042 |        0.010069 |            12 | False     |
| SHADOWSOCKS |                0 | paired-reference | CE_all_bits |  0.006767 | -0.010229 |  0.021176 |      -0.018333 |        0.025984 |            12 | False     |
| SHADOWSOCKS |                0 | paired-reference | Brier_all   |  0.001604 | -0.003267 |  0.006028 |      -0.005225 |        0.007578 |            12 | False     |
| SHADOWSOCKS |                0 | paired-reference | CE_new_bits |  0.025969 | -0.003045 |  0.050376 |      -0.016483 |        0.057896 |            12 | False     |
| SHADOWSOCKS |                0 | paired-reference | Brier_new   |  0.007068 | -0.003789 |  0.016578 |      -0.008682 |        0.019339 |            12 | False     |
| SHADOWSOCKS |                1 | paired-raw       | F1_new      | -0.002632 | -0.037273 |  0.022999 |      -0.056336 |        0.031422 |            12 | False     |
| SHADOWSOCKS |                1 | paired-raw       | F1_all      |  0.008045 | -0.015322 |  0.029360 |      -0.027898 |        0.037911 |            12 | False     |
| SHADOWSOCKS |                1 | paired-raw       | BA_all      |  0.007639 | -0.015278 |  0.028125 |      -0.027489 |        0.036458 |            12 | False     |
| SHADOWSOCKS |                1 | paired-raw       | CE_all_bits | -0.028405 | -0.055543 |  0.001295 |      -0.066434 |        0.016729 |            12 | False     |
| SHADOWSOCKS |                1 | paired-raw       | Brier_all   | -0.013583 | -0.029782 |  0.004020 |      -0.036316 |        0.013779 |            12 | False     |
| SHADOWSOCKS |                1 | paired-raw       | CE_new_bits |  0.078266 |  0.007769 |  0.159575 |      -0.017986 |        0.199381 |            12 | False     |
| SHADOWSOCKS |                1 | paired-raw       | Brier_new   |  0.039968 | -0.001301 |  0.088704 |      -0.013891 |        0.112700 |            12 | False     |
| SHADOWSOCKS |                1 | paired-group     | F1_new      |  0.052596 |  0.028698 |  0.074705 |       0.018959 |        0.080486 |            12 | False     |
| SHADOWSOCKS |                1 | paired-group     | F1_all      |  0.036140 |  0.020799 |  0.052197 |       0.014504 |        0.059059 |            12 | False     |
| SHADOWSOCKS |                1 | paired-group     | BA_all      |  0.034375 |  0.020139 |  0.048958 |       0.013889 |        0.055556 |            12 | False     |
| SHADOWSOCKS |                1 | paired-group     | CE_all_bits | -0.149499 | -0.170091 | -0.127732 |      -0.178351 |       -0.118382 |            12 | False     |
| SHADOWSOCKS |                1 | paired-group     | Brier_all   | -0.070577 | -0.081755 | -0.058430 |      -0.086144 |       -0.053011 |            12 | False     |
| SHADOWSOCKS |                1 | paired-group     | CE_new_bits | -0.214018 | -0.254408 | -0.174764 |      -0.271867 |       -0.158362 |            12 | False     |
| SHADOWSOCKS |                1 | paired-group     | Brier_new   | -0.112709 | -0.133891 | -0.087218 |      -0.139844 |       -0.075848 |            12 | False     |
| SHADOWSOCKS |                1 | paired-cyclic    | F1_new      |  0.091136 |  0.052147 |  0.133975 |       0.037136 |        0.150721 |            12 | False     |
| SHADOWSOCKS |                1 | paired-cyclic    | F1_all      |  0.058399 |  0.035491 |  0.082998 |       0.026363 |        0.094500 |            12 | False     |
| SHADOWSOCKS |                1 | paired-cyclic    | BA_all      |  0.054167 |  0.032986 |  0.075347 |       0.024941 |        0.085475 |            12 | False     |
| SHADOWSOCKS |                1 | paired-cyclic    | CE_all_bits | -0.185024 | -0.217141 | -0.152873 |      -0.231090 |       -0.139089 |            12 | False     |
| SHADOWSOCKS |                1 | paired-cyclic    | Brier_all   | -0.090668 | -0.108594 | -0.072482 |      -0.116408 |       -0.065424 |            12 | False     |
| SHADOWSOCKS |                1 | paired-cyclic    | CE_new_bits | -0.282000 | -0.358339 | -0.206233 |      -0.388419 |       -0.187949 |            12 | False     |
| SHADOWSOCKS |                1 | paired-cyclic    | Brier_new   | -0.154083 | -0.198002 | -0.110671 |      -0.214143 |       -0.095574 |            12 | False     |
| SHADOWSOCKS |                1 | paired-center    | F1_new      | -0.000935 | -0.013901 |  0.008908 |      -0.020739 |        0.012606 |            12 | False     |
| SHADOWSOCKS |                1 | paired-center    | F1_all      | -0.001343 | -0.010245 |  0.006692 |      -0.014744 |        0.009889 |            12 | False     |
| SHADOWSOCKS |                1 | paired-center    | BA_all      | -0.001389 | -0.010069 |  0.006597 |      -0.014236 |        0.009722 |            12 | False     |
| SHADOWSOCKS |                1 | paired-center    | CE_all_bits |  0.005310 | -0.022604 |  0.028544 |      -0.036451 |        0.035914 |            12 | False     |
| SHADOWSOCKS |                1 | paired-center    | Brier_all   |  0.004129 | -0.003359 |  0.011089 |      -0.006890 |        0.013958 |            12 | False     |
| SHADOWSOCKS |                1 | paired-center    | CE_new_bits |  0.057234 |  0.022495 |  0.086241 |       0.007157 |        0.094722 |            12 | False     |
| SHADOWSOCKS |                1 | paired-center    | Brier_new   |  0.028638 |  0.016703 |  0.038837 |       0.011495 |        0.042096 |            12 | False     |
| SHADOWSOCKS |                1 | paired-marginal  | F1_new      | -0.006200 | -0.022017 |  0.007823 |      -0.030694 |        0.012136 |            12 | False     |
| SHADOWSOCKS |                1 | paired-marginal  | F1_all      | -0.005871 | -0.014290 |  0.001444 |      -0.018102 |        0.003864 |            12 | False     |
| SHADOWSOCKS |                1 | paired-marginal  | BA_all      | -0.005903 | -0.013889 |  0.001389 |      -0.017361 |        0.003819 |            12 | False     |
| SHADOWSOCKS |                1 | paired-marginal  | CE_all_bits |  0.014874 | -0.001375 |  0.029523 |      -0.009064 |        0.035149 |            12 | False     |
| SHADOWSOCKS |                1 | paired-marginal  | Brier_all   |  0.009581 |  0.002979 |  0.015998 |       0.000170 |        0.018533 |            12 | False     |
| SHADOWSOCKS |                1 | paired-marginal  | CE_new_bits |  0.078985 |  0.041072 |  0.113645 |       0.020683 |        0.127591 |            12 | False     |
| SHADOWSOCKS |                1 | paired-marginal  | Brier_new   |  0.038135 |  0.020894 |  0.055358 |       0.012573 |        0.061577 |            12 | False     |
| SHADOWSOCKS |                1 | paired-reference | F1_new      | -0.011539 | -0.033930 |  0.007694 |      -0.044201 |        0.013469 |            12 | False     |
| SHADOWSOCKS |                1 | paired-reference | F1_all      | -0.005215 | -0.019102 |  0.009704 |      -0.024725 |        0.016657 |            12 | False     |
| SHADOWSOCKS |                1 | paired-reference | BA_all      | -0.005208 | -0.018750 |  0.009722 |      -0.024017 |        0.016667 |            12 | False     |
| SHADOWSOCKS |                1 | paired-reference | CE_all_bits |  0.037185 |  0.006367 |  0.064259 |      -0.008174 |        0.075156 |            12 | False     |
| SHADOWSOCKS |                1 | paired-reference | Brier_all   |  0.017372 |  0.005739 |  0.028653 |       0.000823 |        0.034133 |            12 | False     |
| SHADOWSOCKS |                1 | paired-reference | CE_new_bits |  0.094353 |  0.018615 |  0.156136 |      -0.015003 |        0.172417 |            12 | False     |
| SHADOWSOCKS |                1 | paired-reference | Brier_new   |  0.048944 |  0.021741 |  0.076396 |       0.012129 |        0.087843 |            12 | False     |
| SHADOWSOCKS |                2 | paired-raw       | F1_new      |  0.550500 |  0.455881 |  0.660517 |       0.410129 |        0.702553 |            12 | False     |
| SHADOWSOCKS |                2 | paired-raw       | F1_all      |  0.258651 |  0.213905 |  0.306716 |       0.193543 |        0.326162 |            12 | False     |
| SHADOWSOCKS |                2 | paired-raw       | BA_all      |  0.213542 |  0.176042 |  0.250694 |       0.159316 |        0.265336 |            12 | False     |
| SHADOWSOCKS |                2 | paired-raw       | CE_all_bits | -0.479503 | -0.570702 | -0.392691 |      -0.610889 |       -0.353765 |            12 | False     |
| SHADOWSOCKS |                2 | paired-raw       | Brier_all   | -0.243501 | -0.283965 | -0.203993 |      -0.306608 |       -0.186183 |            12 | False     |
| SHADOWSOCKS |                2 | paired-raw       | CE_new_bits | -1.558666 | -1.792393 | -1.331287 |      -1.898553 |       -1.247819 |            12 | False     |
| SHADOWSOCKS |                2 | paired-raw       | Brier_new   | -0.786372 | -0.898961 | -0.680024 |      -0.954167 |       -0.631880 |            12 | False     |
| SHADOWSOCKS |                2 | paired-group     | F1_new      |  0.118402 |  0.071219 |  0.187457 |       0.055500 |        0.230737 |            12 | False     |
| SHADOWSOCKS |                2 | paired-group     | F1_all      |  0.083456 |  0.052579 |  0.120809 |       0.040393 |        0.140044 |            12 | False     |
| SHADOWSOCKS |                2 | paired-group     | BA_all      |  0.081597 |  0.051042 |  0.115278 |       0.039583 |        0.131597 |            12 | False     |
| SHADOWSOCKS |                2 | paired-group     | CE_all_bits | -0.234237 | -0.266378 | -0.198560 |      -0.280227 |       -0.182441 |            12 | False     |
| SHADOWSOCKS |                2 | paired-group     | Brier_all   | -0.114964 | -0.133271 | -0.097260 |      -0.142137 |       -0.089874 |            12 | False     |
| SHADOWSOCKS |                2 | paired-group     | CE_new_bits | -0.377621 | -0.431505 | -0.334460 |      -0.456729 |       -0.322024 |            12 | False     |
| SHADOWSOCKS |                2 | paired-group     | Brier_new   | -0.187281 | -0.224355 | -0.158468 |      -0.242265 |       -0.151560 |            12 | False     |
| SHADOWSOCKS |                2 | paired-cyclic    | F1_new      |  0.155939 |  0.099390 |  0.240582 |       0.079515 |        0.291207 |            12 | False     |
| SHADOWSOCKS |                2 | paired-cyclic    | F1_all      |  0.100904 |  0.067875 |  0.141981 |       0.055935 |        0.163543 |            12 | False     |
| SHADOWSOCKS |                2 | paired-cyclic    | BA_all      |  0.097917 |  0.065625 |  0.134028 |       0.053761 |        0.150523 |            12 | False     |
| SHADOWSOCKS |                2 | paired-cyclic    | CE_all_bits | -0.272442 | -0.309114 | -0.233060 |      -0.324953 |       -0.216038 |            12 | False     |
| SHADOWSOCKS |                2 | paired-cyclic    | Brier_all   | -0.136189 | -0.156980 | -0.116007 |      -0.167217 |       -0.107913 |            12 | False     |
| SHADOWSOCKS |                2 | paired-cyclic    | CE_new_bits | -0.501787 | -0.578573 | -0.435456 |      -0.613168 |       -0.413333 |            12 | False     |
| SHADOWSOCKS |                2 | paired-cyclic    | Brier_new   | -0.260022 | -0.309891 | -0.216867 |      -0.333568 |       -0.203032 |            12 | False     |
| SHADOWSOCKS |                2 | paired-center    | F1_new      |  0.005352 |  0.000155 |  0.011203 |      -0.002126 |        0.013999 |            12 | False     |
| SHADOWSOCKS |                2 | paired-center    | F1_all      |  0.006595 |  0.001752 |  0.011912 |       0.000040 |        0.014788 |            12 | False     |
| SHADOWSOCKS |                2 | paired-center    | BA_all      |  0.006597 |  0.001736 |  0.011806 |       0.000000 |        0.014642 |            12 | False     |
| SHADOWSOCKS |                2 | paired-center    | CE_all_bits | -0.007964 | -0.025430 |  0.007314 |      -0.033227 |        0.012964 |            12 | False     |
| SHADOWSOCKS |                2 | paired-center    | Brier_all   | -0.004196 | -0.010700 |  0.001788 |      -0.013801 |        0.004118 |            12 | False     |
| SHADOWSOCKS |                2 | paired-center    | CE_new_bits |  0.025248 |  0.000294 |  0.043752 |      -0.013669 |        0.047545 |            12 | False     |
| SHADOWSOCKS |                2 | paired-center    | Brier_new   |  0.006930 | -0.005504 |  0.016881 |      -0.012725 |        0.018929 |            12 | False     |
| SHADOWSOCKS |                2 | paired-marginal  | F1_new      |  0.002768 | -0.006436 |  0.010519 |      -0.011368 |        0.013316 |            12 | False     |
| SHADOWSOCKS |                2 | paired-marginal  | F1_all      |  0.001431 | -0.004459 |  0.007022 |      -0.007334 |        0.009168 |            12 | False     |
| SHADOWSOCKS |                2 | paired-marginal  | BA_all      |  0.001389 | -0.004514 |  0.006944 |      -0.007292 |        0.009028 |            12 | False     |
| SHADOWSOCKS |                2 | paired-marginal  | CE_all_bits |  0.001817 | -0.005811 |  0.010424 |      -0.008899 |        0.013956 |            12 | False     |
| SHADOWSOCKS |                2 | paired-marginal  | Brier_all   |  0.000572 | -0.003661 |  0.004821 |      -0.005348 |        0.006693 |            12 | False     |
| SHADOWSOCKS |                2 | paired-marginal  | CE_new_bits |  0.035423 |  0.022650 |  0.048607 |       0.018392 |        0.054574 |            12 | False     |
| SHADOWSOCKS |                2 | paired-marginal  | Brier_new   |  0.013125 |  0.006167 |  0.021504 |       0.004382 |        0.025705 |            12 | False     |
| SHADOWSOCKS |                2 | paired-reference | F1_new      |  0.014433 | -0.003807 |  0.037721 |      -0.011049 |        0.050270 |            12 | False     |
| SHADOWSOCKS |                2 | paired-reference | F1_all      |  0.009415 | -0.002591 |  0.024127 |      -0.006871 |        0.031790 |            12 | False     |
| SHADOWSOCKS |                2 | paired-reference | BA_all      |  0.009375 | -0.002778 |  0.023958 |      -0.006944 |        0.031656 |            12 | False     |
| SHADOWSOCKS |                2 | paired-reference | CE_all_bits |  0.008078 | -0.010584 |  0.024702 |      -0.018515 |        0.030123 |            12 | False     |
| SHADOWSOCKS |                2 | paired-reference | Brier_all   |  0.001522 | -0.006096 |  0.008311 |      -0.009395 |        0.010690 |            12 | False     |
| SHADOWSOCKS |                2 | paired-reference | CE_new_bits |  0.029250 |  0.001868 |  0.053701 |      -0.009126 |        0.061693 |            12 | False     |
| SHADOWSOCKS |                2 | paired-reference | Brier_new   |  0.004455 | -0.011809 |  0.018127 |      -0.019478 |        0.022853 |            12 | False     |
| VLESS       |               -1 | paired-raw       | F1_new      |  0.302138 |  0.242564 |  0.359245 |       0.227232 |        0.374436 |             4 | True      |
| VLESS       |               -1 | paired-raw       | F1_all      |  0.128308 |  0.096185 |  0.161331 |       0.087176 |        0.170536 |             4 | False     |
| VLESS       |               -1 | paired-raw       | BA_all      |  0.084954 |  0.058565 |  0.112731 |       0.051215 |        0.119387 |             4 | False     |
| VLESS       |               -1 | paired-raw       | CE_all_bits | -0.411985 | -0.485234 | -0.339017 |      -0.501790 |       -0.320995 |             4 | False     |
| VLESS       |               -1 | paired-raw       | Brier_all   | -0.117321 | -0.139242 | -0.094764 |      -0.144797 |       -0.088088 |             4 | False     |
| VLESS       |               -1 | paired-raw       | CE_new_bits | -1.400522 | -1.590511 | -1.204481 |      -1.640269 |       -1.151379 |             4 | False     |
| VLESS       |               -1 | paired-raw       | Brier_new   | -0.438152 | -0.496708 | -0.378795 |      -0.512009 |       -0.363291 |             4 | False     |
| VLESS       |               -1 | paired-group     | F1_new      |  0.095789 |  0.060124 |  0.136019 |       0.051231 |        0.146133 |             4 | True      |
| VLESS       |               -1 | paired-group     | F1_all      |  0.043307 |  0.016348 |  0.071396 |       0.008769 |        0.079418 |             4 | False     |
| VLESS       |               -1 | paired-group     | BA_all      |  0.036343 |  0.012153 |  0.061458 |       0.005960 |        0.068577 |             4 | False     |
| VLESS       |               -1 | paired-group     | CE_all_bits | -0.055657 | -0.117386 |  0.015568 |      -0.130903 |        0.039674 |             4 | False     |
| VLESS       |               -1 | paired-group     | Brier_all   | -0.031203 | -0.054649 | -0.006235 |      -0.059871 |        0.000404 |             4 | False     |
| VLESS       |               -1 | paired-group     | CE_new_bits | -0.147582 | -0.241361 | -0.039474 |      -0.261179 |       -0.007543 |             4 | False     |
| VLESS       |               -1 | paired-group     | Brier_new   | -0.077519 | -0.118695 | -0.033747 |      -0.127426 |       -0.021892 |             4 | False     |
| VLESS       |               -1 | paired-cyclic    | F1_new      |  0.164952 |  0.121899 |  0.209607 |       0.110122 |        0.220768 |             4 | False     |
| VLESS       |               -1 | paired-cyclic    | F1_all      |  0.073283 |  0.042553 |  0.104115 |       0.033951 |        0.112028 |             4 | False     |
| VLESS       |               -1 | paired-cyclic    | BA_all      |  0.060880 |  0.032755 |  0.089583 |       0.025693 |        0.096471 |             4 | False     |
| VLESS       |               -1 | paired-cyclic    | CE_all_bits | -0.092140 | -0.161768 | -0.012270 |      -0.175888 |        0.013724 |             4 | False     |
| VLESS       |               -1 | paired-cyclic    | Brier_all   | -0.048459 | -0.075569 | -0.020359 |      -0.081773 |       -0.012595 |             4 | False     |
| VLESS       |               -1 | paired-cyclic    | CE_new_bits | -0.254898 | -0.359787 | -0.135505 |      -0.383993 |       -0.100151 |             4 | False     |
| VLESS       |               -1 | paired-cyclic    | Brier_new   | -0.128319 | -0.176943 | -0.077506 |      -0.187662 |       -0.063593 |             4 | False     |
| VLESS       |               -1 | paired-center    | F1_new      |  0.210706 |  0.165971 |  0.258312 |       0.153013 |        0.271666 |             4 | False     |
| VLESS       |               -1 | paired-center    | F1_all      |  0.092058 |  0.072781 |  0.112738 |       0.068403 |        0.118231 |             4 | False     |
| VLESS       |               -1 | paired-center    | BA_all      |  0.072801 |  0.059144 |  0.087037 |       0.056019 |        0.090741 |             4 | False     |
| VLESS       |               -1 | paired-center    | CE_all_bits | -0.288237 | -0.348343 | -0.240419 |      -0.365748 |       -0.231492 |             4 | False     |
| VLESS       |               -1 | paired-center    | Brier_all   | -0.077249 | -0.091424 | -0.062524 |      -0.095187 |       -0.057897 |             4 | False     |
| VLESS       |               -1 | paired-center    | CE_new_bits | -0.833138 | -0.956549 | -0.720594 |      -0.982923 |       -0.694733 |             4 | False     |
| VLESS       |               -1 | paired-center    | Brier_new   | -0.233499 | -0.276377 | -0.191200 |      -0.287811 |       -0.181823 |             4 | False     |
| VLESS       |               -1 | paired-marginal  | F1_new      |  0.077255 |  0.052807 |  0.105293 |       0.046935 |        0.111787 |             4 | False     |
| VLESS       |               -1 | paired-marginal  | F1_all      |  0.036835 |  0.024071 |  0.050847 |       0.020657 |        0.053896 |             4 | False     |
| VLESS       |               -1 | paired-marginal  | BA_all      |  0.032176 |  0.019907 |  0.044329 |       0.016667 |        0.047281 |             4 | False     |
| VLESS       |               -1 | paired-marginal  | CE_all_bits | -0.049865 | -0.069951 | -0.034420 |      -0.075374 |       -0.031632 |             4 | False     |
| VLESS       |               -1 | paired-marginal  | Brier_all   | -0.017875 | -0.023808 | -0.011889 |      -0.025417 |       -0.010201 |             4 | False     |
| VLESS       |               -1 | paired-marginal  | CE_new_bits | -0.128648 | -0.181890 | -0.081889 |      -0.197326 |       -0.071717 |             4 | False     |
| VLESS       |               -1 | paired-marginal  | Brier_new   | -0.043689 | -0.061335 | -0.024912 |      -0.065687 |       -0.020089 |             4 | False     |
| VLESS       |               -1 | paired-reference | F1_new      | -0.074028 | -0.131999 | -0.034088 |      -0.148176 |       -0.024265 |             4 | False     |
| VLESS       |               -1 | paired-reference | F1_all      | -0.040074 | -0.076562 | -0.009555 |      -0.086061 |       -0.002011 |             4 | False     |
| VLESS       |               -1 | paired-reference | BA_all      | -0.037384 | -0.072454 | -0.004398 |      -0.081830 |        0.003531 |             4 | False     |
| VLESS       |               -1 | paired-reference | CE_all_bits |  0.108628 |  0.066625 |  0.160751 |       0.058410 |        0.176348 |             4 | False     |
| VLESS       |               -1 | paired-reference | Brier_all   |  0.049352 |  0.030148 |  0.073447 |       0.026198 |        0.080486 |             4 | False     |
| VLESS       |               -1 | paired-reference | CE_new_bits |  0.296959 |  0.214451 |  0.404882 |       0.201674 |        0.436448 |             4 | False     |
| VLESS       |               -1 | paired-reference | Brier_new   |  0.139137 |  0.099952 |  0.188042 |       0.092853 |        0.201783 |             4 | False     |
| VLESS       |                0 | paired-raw       | F1_new      |  0.178746 |  0.099934 |  0.248444 |       0.055055 |        0.276382 |            12 | False     |
| VLESS       |                0 | paired-raw       | F1_all      |  0.065638 |  0.025712 |  0.101511 |       0.004640 |        0.114687 |            12 | False     |
| VLESS       |                0 | paired-raw       | BA_all      |  0.030208 | -0.003819 |  0.062847 |      -0.020892 |        0.075406 |            12 | False     |
| VLESS       |                0 | paired-raw       | CE_all_bits | -0.172125 | -0.243599 | -0.098015 |      -0.274055 |       -0.064660 |            12 | False     |
| VLESS       |                0 | paired-raw       | Brier_all   | -0.059602 | -0.089750 | -0.025381 |      -0.101475 |       -0.009304 |            12 | False     |
| VLESS       |                0 | paired-raw       | CE_new_bits | -0.699990 | -0.880364 | -0.514872 |      -0.948929 |       -0.438392 |            12 | False     |
| VLESS       |                0 | paired-raw       | Brier_new   | -0.299222 | -0.371661 | -0.214641 |      -0.396310 |       -0.171481 |            12 | False     |
| VLESS       |                0 | paired-group     | F1_new      |  0.032394 | -0.013268 |  0.083589 |      -0.026670 |        0.106891 |            12 | False     |
| VLESS       |                0 | paired-group     | F1_all      | -0.006119 | -0.039320 |  0.024676 |      -0.055774 |        0.038673 |            12 | False     |
| VLESS       |                0 | paired-group     | BA_all      | -0.011458 | -0.040625 |  0.015972 |      -0.054572 |        0.027083 |            12 | False     |
| VLESS       |                0 | paired-group     | CE_all_bits | -0.028178 | -0.076876 |  0.023055 |      -0.095425 |        0.048075 |            12 | False     |
| VLESS       |                0 | paired-group     | Brier_all   | -0.011387 | -0.035661 |  0.014611 |      -0.045139 |        0.024436 |            12 | False     |
| VLESS       |                0 | paired-group     | CE_new_bits | -0.012272 | -0.081210 |  0.065996 |      -0.104754 |        0.104851 |            12 | False     |
| VLESS       |                0 | paired-group     | Brier_new   | -0.019764 | -0.048513 |  0.008558 |      -0.060872 |        0.020072 |            12 | False     |
| VLESS       |                0 | paired-cyclic    | F1_new      |  0.056196 |  0.014811 |  0.099640 |       0.001400 |        0.118705 |            12 | False     |
| VLESS       |                0 | paired-cyclic    | F1_all      |  0.004012 | -0.030592 |  0.033990 |      -0.049335 |        0.046092 |            12 | False     |
| VLESS       |                0 | paired-cyclic    | BA_all      | -0.003819 | -0.035069 |  0.024306 |      -0.050694 |        0.035822 |            12 | False     |
| VLESS       |                0 | paired-cyclic    | CE_all_bits | -0.038397 | -0.093731 |  0.020211 |      -0.113285 |        0.050509 |            12 | False     |
| VLESS       |                0 | paired-cyclic    | Brier_all   | -0.020382 | -0.046043 |  0.006430 |      -0.056080 |        0.017479 |            12 | False     |
| VLESS       |                0 | paired-cyclic    | CE_new_bits | -0.040128 | -0.111137 |  0.046206 |      -0.135120 |        0.090778 |            12 | False     |
| VLESS       |                0 | paired-cyclic    | Brier_new   | -0.040636 | -0.069375 | -0.012655 |      -0.081100 |       -0.001011 |            12 | False     |
| VLESS       |                0 | paired-center    | F1_new      |  0.150117 |  0.110906 |  0.199071 |       0.098770 |        0.221313 |            12 | False     |
| VLESS       |                0 | paired-center    | F1_all      |  0.052412 |  0.026625 |  0.080171 |       0.014269 |        0.092916 |            12 | False     |
| VLESS       |                0 | paired-center    | BA_all      |  0.034028 |  0.008681 |  0.060764 |      -0.003125 |        0.072281 |            12 | False     |
| VLESS       |                0 | paired-center    | CE_all_bits | -0.094934 | -0.158365 | -0.035838 |      -0.187132 |       -0.011194 |            12 | False     |
| VLESS       |                0 | paired-center    | Brier_all   | -0.041949 | -0.072171 | -0.012780 |      -0.086907 |       -0.000061 |            12 | False     |
| VLESS       |                0 | paired-center    | CE_new_bits | -0.437281 | -0.585472 | -0.303788 |      -0.655142 |       -0.256763 |            12 | False     |
| VLESS       |                0 | paired-center    | Brier_new   | -0.234325 | -0.310004 | -0.165288 |      -0.345580 |       -0.141604 |            12 | False     |
| VLESS       |                0 | paired-marginal  | F1_new      |  0.000971 | -0.024666 |  0.028139 |      -0.036622 |        0.041628 |            12 | False     |
| VLESS       |                0 | paired-marginal  | F1_all      | -0.003175 | -0.016621 |  0.010173 |      -0.022381 |        0.016127 |            12 | False     |
| VLESS       |                0 | paired-marginal  | BA_all      | -0.007986 | -0.020139 |  0.003819 |      -0.025059 |        0.009028 |            12 | False     |
| VLESS       |                0 | paired-marginal  | CE_all_bits |  0.018080 | -0.004071 |  0.042024 |      -0.012792 |        0.052252 |            12 | False     |
| VLESS       |                0 | paired-marginal  | Brier_all   |  0.009935 | -0.001943 |  0.022982 |      -0.006555 |        0.029461 |            12 | False     |
| VLESS       |                0 | paired-marginal  | CE_new_bits | -0.018189 | -0.068719 |  0.039733 |      -0.086182 |        0.064420 |            12 | False     |
| VLESS       |                0 | paired-marginal  | Brier_new   | -0.010977 | -0.039659 |  0.022000 |      -0.049796 |        0.036966 |            12 | False     |
| VLESS       |                0 | paired-reference | F1_new      | -0.090358 | -0.144315 | -0.044314 |      -0.172558 |       -0.028359 |            12 | False     |
| VLESS       |                0 | paired-reference | F1_all      | -0.057210 | -0.094711 | -0.024310 |      -0.112806 |       -0.013660 |            12 | False     |
| VLESS       |                0 | paired-reference | BA_all      | -0.050694 | -0.088194 | -0.016319 |      -0.105903 |       -0.003761 |            12 | False     |
| VLESS       |                0 | paired-reference | CE_all_bits |  0.121099 |  0.074660 |  0.169212 |       0.057001 |        0.188672 |            12 | False     |
| VLESS       |                0 | paired-reference | Brier_all   |  0.053123 |  0.032376 |  0.077594 |       0.024937 |        0.087441 |            12 | False     |
| VLESS       |                0 | paired-reference | CE_new_bits |  0.245081 |  0.167314 |  0.326840 |       0.135115 |        0.363185 |            12 | False     |
| VLESS       |                0 | paired-reference | Brier_new   |  0.132010 |  0.099007 |  0.180373 |       0.093548 |        0.203389 |            12 | False     |
| VLESS       |                1 | paired-raw       | F1_new      |  0.325943 |  0.197713 |  0.447795 |       0.156366 |        0.497100 |            12 | False     |
| VLESS       |                1 | paired-raw       | F1_all      |  0.176760 |  0.117569 |  0.233018 |       0.096347 |        0.256749 |            12 | False     |
| VLESS       |                1 | paired-raw       | BA_all      |  0.132986 |  0.086450 |  0.178134 |       0.070310 |        0.194562 |            12 | False     |
| VLESS       |                1 | paired-raw       | CE_all_bits | -0.736156 | -0.874632 | -0.575357 |      -0.902353 |       -0.501672 |            12 | False     |
| VLESS       |                1 | paired-raw       | Brier_all   | -0.154839 | -0.202530 | -0.108067 |      -0.219792 |       -0.092256 |            12 | False     |
| VLESS       |                1 | paired-raw       | CE_new_bits | -2.238205 | -2.642826 | -1.756501 |      -2.706958 |       -1.523402 |            12 | False     |
| VLESS       |                1 | paired-raw       | Brier_new   | -0.438139 | -0.575154 | -0.301556 |      -0.624899 |       -0.258875 |            12 | False     |
| VLESS       |                1 | paired-group     | F1_new      |  0.109277 |  0.066412 |  0.155284 |       0.043536 |        0.174037 |            12 | False     |
| VLESS       |                1 | paired-group     | F1_all      |  0.071185 |  0.044246 |  0.097452 |       0.031643 |        0.107876 |            12 | False     |
| VLESS       |                1 | paired-group     | BA_all      |  0.058681 |  0.032986 |  0.083333 |       0.022858 |        0.093403 |            12 | False     |
| VLESS       |                1 | paired-group     | CE_all_bits | -0.102616 | -0.161648 | -0.028815 |      -0.179572 |        0.008336 |            12 | False     |
| VLESS       |                1 | paired-group     | Brier_all   | -0.048375 | -0.070253 | -0.022937 |      -0.077365 |       -0.011001 |            12 | False     |
| VLESS       |                1 | paired-group     | CE_new_bits | -0.392613 | -0.461816 | -0.314852 |      -0.485663 |       -0.284237 |            12 | False     |
| VLESS       |                1 | paired-group     | Brier_new   | -0.139243 | -0.193756 | -0.069897 |      -0.210880 |       -0.040767 |            12 | False     |
| VLESS       |                1 | paired-cyclic    | F1_new      |  0.170353 |  0.100782 |  0.231991 |       0.059041 |        0.258063 |            12 | False     |
| VLESS       |                1 | paired-cyclic    | F1_all      |  0.103649 |  0.065930 |  0.136106 |       0.046949 |        0.149551 |            12 | False     |
| VLESS       |                1 | paired-cyclic    | BA_all      |  0.088194 |  0.053125 |  0.118056 |       0.039583 |        0.130267 |            12 | False     |
| VLESS       |                1 | paired-cyclic    | CE_all_bits | -0.170563 | -0.240560 | -0.085640 |      -0.263975 |       -0.044806 |            12 | False     |
| VLESS       |                1 | paired-cyclic    | Brier_all   | -0.073148 | -0.101038 | -0.040050 |      -0.110916 |       -0.026213 |            12 | False     |
| VLESS       |                1 | paired-cyclic    | CE_new_bits | -0.599768 | -0.703442 | -0.490017 |      -0.747529 |       -0.450010 |            12 | False     |
| VLESS       |                1 | paired-cyclic    | Brier_new   | -0.214505 | -0.283788 | -0.127035 |      -0.304377 |       -0.087518 |            12 | False     |
| VLESS       |                1 | paired-center    | F1_new      |  0.297802 |  0.184748 |  0.406976 |       0.149572 |        0.454288 |            12 | False     |
| VLESS       |                1 | paired-center    | F1_all      |  0.155534 |  0.099029 |  0.210120 |       0.076891 |        0.232553 |            12 | False     |
| VLESS       |                1 | paired-center    | BA_all      |  0.123958 |  0.078125 |  0.167708 |       0.059199 |        0.184781 |            12 | False     |
| VLESS       |                1 | paired-center    | CE_all_bits | -0.670157 | -0.793045 | -0.557319 |      -0.841288 |       -0.519561 |            12 | False     |
| VLESS       |                1 | paired-center    | Brier_all   | -0.146985 | -0.187099 | -0.106371 |      -0.205462 |       -0.090433 |            12 | False     |
| VLESS       |                1 | paired-center    | CE_new_bits | -1.746215 | -2.069590 | -1.446879 |      -2.193209 |       -1.358814 |            12 | False     |
| VLESS       |                1 | paired-center    | Brier_new   | -0.300417 | -0.394655 | -0.210173 |      -0.432592 |       -0.185850 |            12 | False     |
| VLESS       |                1 | paired-marginal  | F1_new      |  0.149891 |  0.104686 |  0.190900 |       0.085628 |        0.208336 |            12 | False     |
| VLESS       |                1 | paired-marginal  | F1_all      |  0.086437 |  0.057345 |  0.116058 |       0.045527 |        0.130978 |            12 | False     |
| VLESS       |                1 | paired-marginal  | BA_all      |  0.073958 |  0.044444 |  0.103472 |       0.032639 |        0.117420 |            12 | False     |
| VLESS       |                1 | paired-marginal  | CE_all_bits | -0.164124 | -0.220921 | -0.114632 |      -0.246926 |       -0.097527 |            12 | False     |
| VLESS       |                1 | paired-marginal  | Brier_all   | -0.063116 | -0.085880 | -0.042303 |      -0.095267 |       -0.034605 |            12 | False     |
| VLESS       |                1 | paired-marginal  | CE_new_bits | -0.349931 | -0.492008 | -0.243143 |      -0.554648 |       -0.214273 |            12 | False     |
| VLESS       |                1 | paired-marginal  | Brier_new   | -0.101714 | -0.128446 | -0.075408 |      -0.138924 |       -0.064121 |            12 | False     |
| VLESS       |                1 | paired-reference | F1_new      | -0.087285 | -0.223064 | -0.020870 |      -0.308947 |       -0.009922 |            12 | False     |
| VLESS       |                1 | paired-reference | F1_all      | -0.038685 | -0.101254 |  0.004191 |      -0.136669 |        0.018276 |            12 | False     |
| VLESS       |                1 | paired-reference | BA_all      | -0.035417 | -0.088203 |  0.007292 |      -0.110822 |        0.021875 |            12 | False     |
| VLESS       |                1 | paired-reference | CE_all_bits |  0.146784 |  0.073361 |  0.250060 |       0.055896 |        0.297310 |            12 | False     |
| VLESS       |                1 | paired-reference | Brier_all   |  0.063165 |  0.032866 |  0.106644 |       0.024731 |        0.127065 |            12 | False     |
| VLESS       |                1 | paired-reference | CE_new_bits |  0.519754 |  0.337272 |  0.821734 |       0.312813 |        0.967331 |            12 | False     |
| VLESS       |                1 | paired-reference | Brier_new   |  0.201588 |  0.120748 |  0.328017 |       0.108450 |        0.390860 |            12 | False     |
| VLESS       |                2 | paired-raw       | F1_new      |  0.401726 |  0.333094 |  0.467460 |       0.301587 |        0.494400 |            12 | False     |
| VLESS       |                2 | paired-raw       | F1_all      |  0.142525 |  0.094939 |  0.191699 |       0.074292 |        0.211782 |            12 | False     |
| VLESS       |                2 | paired-raw       | BA_all      |  0.091667 |  0.046875 |  0.137500 |       0.026389 |        0.157986 |            12 | False     |
| VLESS       |                2 | paired-raw       | CE_all_bits | -0.327674 | -0.449769 | -0.223191 |      -0.516508 |       -0.191110 |            12 | False     |
| VLESS       |                2 | paired-raw       | Brier_all   | -0.137522 | -0.169964 | -0.104690 |      -0.184146 |       -0.088859 |            12 | False     |
| VLESS       |                2 | paired-raw       | CE_new_bits | -1.263370 | -1.617315 | -0.978236 |      -1.799167 |       -0.898575 |            12 | False     |
| VLESS       |                2 | paired-raw       | Brier_new   | -0.577096 | -0.647956 | -0.502005 |      -0.675101 |       -0.470206 |            12 | False     |
| VLESS       |                2 | paired-group     | F1_new      |  0.145695 |  0.076962 |  0.222373 |       0.050062 |        0.252906 |            12 | False     |
| VLESS       |                2 | paired-group     | F1_all      |  0.064855 |  0.026927 |  0.107006 |       0.012771 |        0.122877 |            12 | False     |
| VLESS       |                2 | paired-group     | BA_all      |  0.061806 |  0.028819 |  0.098958 |       0.016955 |        0.113600 |            12 | False     |
| VLESS       |                2 | paired-group     | CE_all_bits | -0.036179 | -0.131170 |  0.074642 |      -0.164577 |        0.133242 |            12 | False     |
| VLESS       |                2 | paired-group     | Brier_all   | -0.033848 | -0.069941 |  0.004795 |      -0.082512 |        0.021772 |            12 | False     |
| VLESS       |                2 | paired-group     | CE_new_bits | -0.037862 | -0.293752 |  0.271247 |      -0.375481 |        0.435255 |            12 | False     |
| VLESS       |                2 | paired-group     | Brier_new   | -0.073548 | -0.177160 |  0.037734 |      -0.212002 |        0.082499 |            12 | False     |
| VLESS       |                2 | paired-cyclic    | F1_new      |  0.268308 |  0.182275 |  0.356676 |       0.143319 |        0.388850 |            12 | False     |
| VLESS       |                2 | paired-cyclic    | F1_all      |  0.112188 |  0.063426 |  0.163658 |       0.041629 |        0.183967 |            12 | False     |
| VLESS       |                2 | paired-cyclic    | BA_all      |  0.098264 |  0.053472 |  0.144097 |       0.034258 |        0.164295 |            12 | False     |
| VLESS       |                2 | paired-cyclic    | CE_all_bits | -0.067459 | -0.171535 |  0.051172 |      -0.209286 |        0.113497 |            12 | False     |
| VLESS       |                2 | paired-cyclic    | Brier_all   | -0.051847 | -0.093895 | -0.007754 |      -0.109010 |        0.010599 |            12 | False     |
| VLESS       |                2 | paired-cyclic    | CE_new_bits | -0.124796 | -0.405572 |  0.209446 |      -0.505615 |        0.376106 |            12 | False     |
| VLESS       |                2 | paired-cyclic    | Brier_new   | -0.129815 | -0.249827 | -0.002668 |      -0.294106 |        0.047212 |            12 | False     |
| VLESS       |                2 | paired-center    | F1_new      |  0.184200 |  0.112219 |  0.265348 |       0.087003 |        0.289815 |            12 | False     |
| VLESS       |                2 | paired-center    | F1_all      |  0.068229 |  0.033890 |  0.106386 |       0.020793 |        0.121331 |            12 | False     |
| VLESS       |                2 | paired-center    | BA_all      |  0.060417 |  0.036111 |  0.086120 |       0.026042 |        0.097569 |            12 | False     |
| VLESS       |                2 | paired-center    | CE_all_bits | -0.099621 | -0.148589 | -0.053344 |      -0.172165 |       -0.035644 |            12 | False     |
| VLESS       |                2 | paired-center    | Brier_all   | -0.042814 | -0.064236 | -0.022566 |      -0.075427 |       -0.013758 |            12 | False     |
| VLESS       |                2 | paired-center    | CE_new_bits | -0.315917 | -0.404274 | -0.229480 |      -0.445364 |       -0.194001 |            12 | False     |
| VLESS       |                2 | paired-center    | Brier_new   | -0.165754 | -0.208309 | -0.122832 |      -0.227274 |       -0.104071 |            12 | False     |
| VLESS       |                2 | paired-marginal  | F1_new      |  0.080901 |  0.028999 |  0.152513 |       0.009739 |        0.180842 |            12 | False     |
| VLESS       |                2 | paired-marginal  | F1_all      |  0.027243 |  0.001978 |  0.056754 |      -0.009612 |        0.069314 |            12 | False     |
| VLESS       |                2 | paired-marginal  | BA_all      |  0.030556 |  0.007986 |  0.052431 |      -0.001736 |        0.060764 |            12 | False     |
| VLESS       |                2 | paired-marginal  | CE_all_bits | -0.003551 | -0.025632 |  0.021165 |      -0.034057 |        0.032068 |            12 | False     |
| VLESS       |                2 | paired-marginal  | Brier_all   | -0.000443 | -0.013302 |  0.013862 |      -0.018985 |        0.020364 |            12 | False     |
| VLESS       |                2 | paired-marginal  | CE_new_bits | -0.017824 | -0.074224 |  0.051578 |      -0.090484 |        0.084677 |            12 | False     |
| VLESS       |                2 | paired-marginal  | Brier_new   | -0.018375 | -0.052079 |  0.022348 |      -0.062104 |        0.041385 |            12 | False     |
| VLESS       |                2 | paired-reference | F1_new      | -0.044442 | -0.113611 |  0.019827 |      -0.144535 |        0.046624 |            12 | False     |
| VLESS       |                2 | paired-reference | F1_all      | -0.024328 | -0.062261 |  0.013456 |      -0.078222 |        0.031091 |            12 | False     |
| VLESS       |                2 | paired-reference | BA_all      | -0.026042 | -0.062847 |  0.013542 |      -0.077201 |        0.031367 |            12 | False     |
| VLESS       |                2 | paired-reference | CE_all_bits |  0.058001 |  0.020643 |  0.096452 |       0.005369 |        0.113817 |            12 | False     |
| VLESS       |                2 | paired-reference | Brier_all   |  0.031769 |  0.010568 |  0.053995 |       0.000152 |        0.063764 |            12 | False     |
| VLESS       |                2 | paired-reference | CE_new_bits |  0.126043 |  0.027210 |  0.225356 |      -0.010946 |        0.264112 |            12 | False     |
| VLESS       |                2 | paired-reference | Brier_new   |  0.083814 |  0.026208 |  0.141755 |       0.003615 |        0.166273 |            12 | False     |

## 逐seed

| protocol    | arm       |     seed |   F1_new |   F1_all |   BA_all |   CE_all_bits |   Brier_all |   CE_new_bits |   Brier_new |
|:------------|:----------|---------:|---------:|---------:|---------:|--------------:|------------:|--------------:|------------:|
| SHADOWSOCKS | center    | 20260918 | 0.948778 | 0.951344 | 0.951389 |      0.346072 |    0.090635 |      0.387105 |    0.109169 |
| SHADOWSOCKS | center    | 20260919 | 0.955133 | 0.958287 | 0.958333 |      0.314966 |    0.078519 |      0.363976 |    0.094219 |
| SHADOWSOCKS | center    | 20260920 | 0.968093 | 0.968708 | 0.968750 |      0.270385 |    0.062270 |      0.298357 |    0.071537 |
| SHADOWSOCKS | cyclic    | 20260918 | 0.869281 | 0.896887 | 0.898958 |      0.522590 |    0.180140 |      0.673760 |    0.261599 |
| SHADOWSOCKS | cyclic    | 20260919 | 0.872930 | 0.907082 | 0.909722 |      0.503470 |    0.169237 |      0.647926 |    0.245359 |
| SHADOWSOCKS | cyclic    | 20260920 | 0.878313 | 0.911860 | 0.914583 |      0.479886 |    0.160687 |      0.612345 |    0.231988 |
| SHADOWSOCKS | group     | 20260918 | 0.883365 | 0.907587 | 0.909375 |      0.495277 |    0.164710 |      0.607417 |    0.224077 |
| SHADOWSOCKS | group     | 20260919 | 0.899115 | 0.919528 | 0.920833 |      0.469683 |    0.151560 |      0.579696 |    0.207103 |
| SHADOWSOCKS | group     | 20260920 | 0.907549 | 0.925460 | 0.926389 |      0.450369 |    0.143344 |      0.544930 |    0.189764 |
| SHADOWSOCKS | marginal  | 20260918 | 0.955908 | 0.956183 | 0.956250 |      0.338144 |    0.086035 |      0.350622 |    0.091614 |
| SHADOWSOCKS | marginal  | 20260919 | 0.963336 | 0.965926 | 0.965972 |      0.299911 |    0.070089 |      0.324471 |    0.075255 |
| SHADOWSOCKS | marginal  | 20260920 | 0.970773 | 0.971492 | 0.971528 |      0.264355 |    0.059269 |      0.276030 |    0.061408 |
| SHADOWSOCKS | paired    | 20260918 | 0.952636 | 0.953454 | 0.953472 |      0.341521 |    0.088868 |      0.384388 |    0.107167 |
| SHADOWSOCKS | paired    | 20260919 | 0.959307 | 0.963529 | 0.963542 |      0.303683 |    0.072819 |      0.354232 |    0.089415 |
| SHADOWSOCKS | paired    | 20260920 | 0.971072 | 0.971176 | 0.971181 |      0.266337 |    0.060769 |      0.295334 |    0.069541 |
| SHADOWSOCKS | raw       | 20260918 | 0.728787 | 0.843279 | 0.861111 |      0.553674 |    0.200794 |      1.026864 |    0.428397 |
| SHADOWSOCKS | raw       | 20260919 | 0.763199 | 0.869330 | 0.885069 |      0.501333 |    0.171115 |      0.957944 |    0.380860 |
| SHADOWSOCKS | raw       | 20260920 | 0.784932 | 0.880129 | 0.892708 |      0.456435 |    0.153104 |      0.860763 |    0.343456 |
| SHADOWSOCKS | reference | 20260918 | 0.953599 | 0.954172 | 0.954167 |      0.320817 |    0.079570 |      0.326395 |    0.080761 |
| SHADOWSOCKS | reference | 20260919 | 0.957883 | 0.960734 | 0.960764 |      0.288424 |    0.066860 |      0.301727 |    0.068760 |
| SHADOWSOCKS | reference | 20260920 | 0.963628 | 0.965599 | 0.965625 |      0.250271 |    0.055528 |      0.256260 |    0.056135 |
| VLESS       | center    | 20260918 | 0.513145 | 0.684917 | 0.714931 |      1.062187 |    0.383662 |      1.826102 |    0.642905 |
| VLESS       | center    | 20260919 | 0.551084 | 0.702241 | 0.729514 |      1.063384 |    0.369242 |      1.833192 |    0.627080 |
| VLESS       | center    | 20260920 | 0.547148 | 0.703474 | 0.732639 |      1.059719 |    0.370405 |      1.803371 |    0.625208 |
| VLESS       | cyclic    | 20260918 | 0.584586 | 0.712852 | 0.732292 |      0.872564 |    0.352009 |      1.264719 |    0.537957 |
| VLESS       | cyclic    | 20260919 | 0.564440 | 0.705491 | 0.730208 |      0.868126 |    0.343056 |      1.251576 |    0.525593 |
| VLESS       | cyclic    | 20260920 | 0.599613 | 0.728614 | 0.750347 |      0.856308 |    0.341873 |      1.211650 |    0.516101 |
| VLESS       | group     | 20260918 | 0.661214 | 0.748523 | 0.763194 |      0.831934 |    0.332317 |      1.138668 |    0.475319 |
| VLESS       | group     | 20260919 | 0.637153 | 0.738229 | 0.756944 |      0.828434 |    0.326950 |      1.136675 |    0.476324 |
| VLESS       | group     | 20260920 | 0.657764 | 0.750134 | 0.766319 |      0.827182 |    0.325903 |      1.130655 |    0.475609 |
| VLESS       | marginal  | 20260918 | 0.666461 | 0.746659 | 0.759375 |      0.828785 |    0.324658 |      1.124749 |    0.451104 |
| VLESS       | marginal  | 20260919 | 0.671607 | 0.757735 | 0.772917 |      0.812164 |    0.308323 |      1.096333 |    0.431877 |
| VLESS       | marginal  | 20260920 | 0.673664 | 0.751908 | 0.766667 |      0.829224 |    0.312205 |      1.128114 |    0.442781 |
| VLESS       | paired    | 20260918 | 0.742140 | 0.782554 | 0.790625 |      0.779552 |    0.308451 |      1.011351 |    0.414793 |
| VLESS       | paired    | 20260919 | 0.748221 | 0.790691 | 0.802778 |      0.761160 |    0.288992 |      0.957946 |    0.385254 |
| VLESS       | paired    | 20260920 | 0.753135 | 0.793561 | 0.802083 |      0.779865 |    0.294119 |      0.993954 |    0.394648 |
| VLESS       | raw       | 20260918 | 0.452316 | 0.660531 | 0.712153 |      1.134877 |    0.409089 |      2.207840 |    0.795880 |
| VLESS       | raw       | 20260919 | 0.443991 | 0.662115 | 0.714236 |      1.200954 |    0.413656 |      2.486654 |    0.857976 |
| VLESS       | raw       | 20260920 | 0.440774 | 0.659237 | 0.714236 |      1.220701 |    0.420779 |      2.470322 |    0.855297 |
| VLESS       | reference | 20260918 | 0.799304 | 0.812130 | 0.821181 |      0.678865 |    0.260332 |      0.723626 |    0.276354 |
| VLESS       | reference | 20260919 | 0.832818 | 0.836480 | 0.843750 |      0.657816 |    0.242243 |      0.674252 |    0.250283 |
| VLESS       | reference | 20260920 | 0.833460 | 0.838420 | 0.842708 |      0.658013 |    0.240931 |      0.674495 |    0.250648 |

## 逐轮换

| protocol    |   business_group | arm       |   rotation |   F1_new |   F1_all |   BA_all |   CE_all_bits |   Brier_all |   CE_new_bits |   Brier_new |
|:------------|-----------------:|:----------|-----------:|---------:|---------:|---------:|--------------:|------------:|--------------:|------------:|
| SHADOWSOCKS |                0 | center    |          0 | 0.946882 | 0.949945 | 0.950000 |      0.329211 |    0.088783 |      0.367668 |    0.147527 |
| SHADOWSOCKS |                0 | center    |          1 | 0.964201 | 0.966553 | 0.966667 |      0.309923 |    0.077315 |      0.341585 |    0.129619 |
| SHADOWSOCKS |                0 | center    |          2 | 0.939912 | 0.952790 | 0.952778 |      0.297651 |    0.078986 |      0.317828 |    0.123530 |
| SHADOWSOCKS |                0 | center    |          3 | 0.955897 | 0.961017 | 0.961111 |      0.292394 |    0.073672 |      0.302788 |    0.113908 |
| SHADOWSOCKS |                0 | center    |          4 | 0.964669 | 0.961031 | 0.961111 |      0.309131 |    0.077766 |      0.332040 |    0.128649 |
| SHADOWSOCKS |                0 | center    |          5 | 0.956122 | 0.961031 | 0.961111 |      0.328068 |    0.086067 |      0.340885 |    0.133040 |
| SHADOWSOCKS |                0 | center    |          6 | 0.946657 | 0.955429 | 0.955556 |      0.320961 |    0.082011 |      0.379890 |    0.141578 |
| SHADOWSOCKS |                0 | center    |          7 | 0.964669 | 0.966586 | 0.966667 |      0.317759 |    0.078785 |      0.341144 |    0.127994 |
| SHADOWSOCKS |                0 | cyclic    |          0 | 0.942134 | 0.947179 | 0.947222 |      0.471280 |    0.147741 |      0.398217 |    0.164688 |
| SHADOWSOCKS |                0 | cyclic    |          1 | 0.907843 | 0.924110 | 0.925000 |      0.470155 |    0.152141 |      0.391157 |    0.164541 |
| SHADOWSOCKS |                0 | cyclic    |          2 | 0.964201 | 0.969331 | 0.969444 |      0.397354 |    0.116328 |      0.348591 |    0.133780 |
| SHADOWSOCKS |                0 | cyclic    |          3 | 0.968943 | 0.969364 | 0.969444 |      0.367274 |    0.103209 |      0.319560 |    0.122823 |
| SHADOWSOCKS |                0 | cyclic    |          4 | 0.937315 | 0.947040 | 0.947222 |      0.444560 |    0.134226 |      0.353165 |    0.143097 |
| SHADOWSOCKS |                0 | cyclic    |          5 | 0.947125 | 0.955438 | 0.955556 |      0.381623 |    0.107262 |      0.319211 |    0.124226 |
| SHADOWSOCKS |                0 | cyclic    |          6 | 0.959459 | 0.955400 | 0.955556 |      0.422034 |    0.128327 |      0.356356 |    0.148351 |
| SHADOWSOCKS |                0 | cyclic    |          7 | 0.941415 | 0.938853 | 0.938889 |      0.508512 |    0.168944 |      0.384154 |    0.159115 |
| SHADOWSOCKS |                0 | group     |          0 | 0.940190 | 0.952508 | 0.952778 |      0.451375 |    0.137822 |      0.385193 |    0.159912 |
| SHADOWSOCKS |                0 | group     |          1 | 0.909334 | 0.929750 | 0.930556 |      0.463572 |    0.146762 |      0.388774 |    0.164702 |
| SHADOWSOCKS |                0 | group     |          2 | 0.930869 | 0.946800 | 0.947222 |      0.410159 |    0.124148 |      0.372393 |    0.148992 |
| SHADOWSOCKS |                0 | group     |          3 | 0.964201 | 0.961123 | 0.961111 |      0.349321 |    0.096251 |      0.326598 |    0.127422 |
| SHADOWSOCKS |                0 | group     |          4 | 0.940379 | 0.952434 | 0.952778 |      0.426583 |    0.123243 |      0.341339 |    0.136587 |
| SHADOWSOCKS |                0 | group     |          5 | 0.955429 | 0.955428 | 0.955556 |      0.353385 |    0.093656 |      0.269923 |    0.099424 |
| SHADOWSOCKS |                0 | group     |          6 | 0.959459 | 0.960964 | 0.961111 |      0.383214 |    0.107361 |      0.309687 |    0.124111 |
| SHADOWSOCKS |                0 | group     |          7 | 0.916005 | 0.924025 | 0.925000 |      0.490086 |    0.155859 |      0.397783 |    0.168391 |
| SHADOWSOCKS |                0 | marginal  |          0 | 0.956140 | 0.955472 | 0.955556 |      0.314303 |    0.079454 |      0.281089 |    0.105060 |
| SHADOWSOCKS |                0 | marginal  |          1 | 0.968943 | 0.969364 | 0.969444 |      0.304238 |    0.074707 |      0.281128 |    0.102801 |
| SHADOWSOCKS |                0 | marginal  |          2 | 0.961516 | 0.963854 | 0.963889 |      0.299436 |    0.078941 |      0.288439 |    0.105843 |
| SHADOWSOCKS |                0 | marginal  |          3 | 0.965587 | 0.963859 | 0.963889 |      0.290008 |    0.070900 |      0.243133 |    0.086384 |
| SHADOWSOCKS |                0 | marginal  |          4 | 0.969636 | 0.969406 | 0.969444 |      0.291729 |    0.068855 |      0.246212 |    0.092099 |
| SHADOWSOCKS |                0 | marginal  |          5 | 0.969411 | 0.969396 | 0.969444 |      0.312638 |    0.077170 |      0.266085 |    0.097316 |
| SHADOWSOCKS |                0 | marginal  |          6 | 0.968943 | 0.966578 | 0.966667 |      0.304780 |    0.071719 |      0.294010 |    0.103864 |
| SHADOWSOCKS |                0 | marginal  |          7 | 0.960152 | 0.961006 | 0.961111 |      0.310621 |    0.075154 |      0.292626 |    0.104832 |
| SHADOWSOCKS |                0 | paired    |          0 | 0.960864 | 0.961050 | 0.961111 |      0.305942 |    0.075531 |      0.249698 |    0.091384 |
| SHADOWSOCKS |                0 | paired    |          1 | 0.960864 | 0.961127 | 0.961111 |      0.299054 |    0.073135 |      0.237870 |    0.086402 |
| SHADOWSOCKS |                0 | paired    |          2 | 0.958318 | 0.961095 | 0.961111 |      0.293379 |    0.075468 |      0.252170 |    0.087224 |
| SHADOWSOCKS |                0 | paired    |          3 | 0.957040 | 0.961078 | 0.961111 |      0.286919 |    0.069661 |      0.234691 |    0.081643 |
| SHADOWSOCKS |                0 | paired    |          4 | 0.965587 | 0.966637 | 0.966667 |      0.289374 |    0.067175 |      0.221659 |    0.078021 |
| SHADOWSOCKS |                0 | paired    |          5 | 0.961538 | 0.963868 | 0.963889 |      0.302871 |    0.072210 |      0.238321 |    0.084641 |
| SHADOWSOCKS |                0 | paired    |          6 | 0.961538 | 0.966646 | 0.966667 |      0.292282 |    0.068582 |      0.259155 |    0.094218 |
| SHADOWSOCKS |                0 | paired    |          7 | 0.966026 | 0.969429 | 0.969444 |      0.297451 |    0.070408 |      0.246534 |    0.087356 |
| SHADOWSOCKS |                0 | raw       |          0 | 0.896680 | 0.910470 | 0.911111 |      0.434174 |    0.141802 |      0.565969 |    0.233412 |
| SHADOWSOCKS |                0 | raw       |          1 | 0.919335 | 0.944229 | 0.944444 |      0.386611 |    0.112901 |      0.535387 |    0.205443 |
| SHADOWSOCKS |                0 | raw       |          2 | 0.916062 | 0.949757 | 0.950000 |      0.355285 |    0.104958 |      0.565701 |    0.224209 |
| SHADOWSOCKS |                0 | raw       |          3 | 0.910436 | 0.944031 | 0.944444 |      0.346073 |    0.104987 |      0.529585 |    0.211584 |
| SHADOWSOCKS |                0 | raw       |          4 | 0.891425 | 0.934987 | 0.936111 |      0.374281 |    0.109423 |      0.614618 |    0.243545 |
| SHADOWSOCKS |                0 | raw       |          5 | 0.891425 | 0.934987 | 0.936111 |      0.367539 |    0.109326 |      0.571807 |    0.236004 |
| SHADOWSOCKS |                0 | raw       |          6 | 0.897664 | 0.929892 | 0.930556 |      0.416323 |    0.128264 |      0.625754 |    0.241243 |
| SHADOWSOCKS |                0 | raw       |          7 | 0.902919 | 0.932766 | 0.933333 |      0.422919 |    0.124298 |      0.581016 |    0.216938 |
| SHADOWSOCKS |                0 | reference |          0 | 0.956815 | 0.961068 | 0.961111 |      0.289840 |    0.071027 |      0.217734 |    0.080781 |
| SHADOWSOCKS |                0 | reference |          1 | 0.961538 | 0.963868 | 0.963889 |      0.289988 |    0.070392 |      0.217333 |    0.081299 |
| SHADOWSOCKS |                0 | reference |          2 | 0.937393 | 0.950129 | 0.950000 |      0.283380 |    0.073250 |      0.221998 |    0.082521 |
| SHADOWSOCKS |                0 | reference |          3 | 0.945299 | 0.952764 | 0.952778 |      0.282718 |    0.069725 |      0.219767 |    0.080723 |
| SHADOWSOCKS |                0 | reference |          4 | 0.961538 | 0.963868 | 0.963889 |      0.292690 |    0.069225 |      0.211020 |    0.078793 |
| SHADOWSOCKS |                0 | reference |          5 | 0.961538 | 0.963868 | 0.963889 |      0.296678 |    0.070135 |      0.216102 |    0.079641 |
| SHADOWSOCKS |                0 | reference |          6 | 0.966026 | 0.963861 | 0.963889 |      0.287216 |    0.066285 |      0.213759 |    0.074138 |
| SHADOWSOCKS |                0 | reference |          7 | 0.961538 | 0.963868 | 0.963889 |      0.290630 |    0.069297 |      0.214634 |    0.076449 |
| SHADOWSOCKS |                1 | center    |          0 | 0.957254 | 0.958264 | 0.958333 |      0.312469 |    0.072538 |      0.505941 |    0.091897 |
| SHADOWSOCKS |                1 | center    |          1 | 0.970299 | 0.966616 | 0.966667 |      0.299322 |    0.067789 |      0.487347 |    0.079733 |
| SHADOWSOCKS |                1 | center    |          2 | 0.953205 | 0.952614 | 0.952778 |      0.322418 |    0.081702 |      0.512052 |    0.098216 |
| SHADOWSOCKS |                1 | center    |          3 | 0.941026 | 0.947092 | 0.947222 |      0.331271 |    0.086345 |      0.511388 |    0.101143 |
| SHADOWSOCKS |                1 | center    |          4 | 0.958318 | 0.961053 | 0.961111 |      0.305001 |    0.076419 |      0.468836 |    0.082326 |
| SHADOWSOCKS |                1 | center    |          5 | 0.954060 | 0.958253 | 0.958333 |      0.310579 |    0.079113 |      0.457329 |    0.084064 |
| SHADOWSOCKS |                1 | center    |          6 | 0.962179 | 0.958286 | 0.958333 |      0.301030 |    0.068852 |      0.455821 |    0.070465 |
| SHADOWSOCKS |                1 | center    |          7 | 0.958318 | 0.961132 | 0.961111 |      0.311006 |    0.068627 |      0.469726 |    0.064445 |
| SHADOWSOCKS |                1 | cyclic    |          0 | 0.819176 | 0.874895 | 0.880556 |      0.571083 |    0.200566 |      0.967658 |    0.330595 |
| SHADOWSOCKS |                1 | cyclic    |          1 | 0.851671 | 0.882809 | 0.886111 |      0.541693 |    0.194398 |      0.855398 |    0.293710 |
| SHADOWSOCKS |                1 | cyclic    |          2 | 0.934293 | 0.935698 | 0.936111 |      0.480675 |    0.155516 |      0.640305 |    0.166456 |
| SHADOWSOCKS |                1 | cyclic    |          3 | 0.869688 | 0.897998 | 0.900000 |      0.499497 |    0.169026 |      0.851116 |    0.279112 |
| SHADOWSOCKS |                1 | cyclic    |          4 | 0.874434 | 0.906722 | 0.908333 |      0.453816 |    0.151720 |      0.759804 |    0.247792 |
| SHADOWSOCKS |                1 | cyclic    |          5 | 0.938578 | 0.944393 | 0.944444 |      0.417409 |    0.129127 |      0.708931 |    0.210984 |
| SHADOWSOCKS |                1 | cyclic    |          6 | 0.686325 | 0.812377 | 0.833333 |      0.594377 |    0.227998 |      1.126804 |    0.451948 |
| SHADOWSOCKS |                1 | cyclic    |          7 | 0.943927 | 0.930480 | 0.930556 |      0.457215 |    0.131411 |      0.672297 |    0.153459 |
| SHADOWSOCKS |                1 | group     |          0 | 0.892408 | 0.912689 | 0.913889 |      0.526861 |    0.177523 |      0.882939 |    0.288075 |
| SHADOWSOCKS |                1 | group     |          1 | 0.894683 | 0.904460 | 0.905556 |      0.498238 |    0.167448 |      0.763781 |    0.234693 |
| SHADOWSOCKS |                1 | group     |          2 | 0.939271 | 0.938532 | 0.938889 |      0.482924 |    0.155079 |      0.668803 |    0.175220 |
| SHADOWSOCKS |                1 | group     |          3 | 0.924314 | 0.932947 | 0.933333 |      0.446003 |    0.138313 |      0.731032 |    0.208106 |
| SHADOWSOCKS |                1 | group     |          4 | 0.913481 | 0.927455 | 0.927778 |      0.428280 |    0.137088 |      0.706197 |    0.214059 |
| SHADOWSOCKS |                1 | group     |          5 | 0.934548 | 0.949846 | 0.950000 |      0.398189 |    0.118724 |      0.677616 |    0.189602 |
| SHADOWSOCKS |                1 | group     |          6 | 0.770452 | 0.855943 | 0.866667 |      0.516977 |    0.185931 |      0.965670 |    0.358691 |
| SHADOWSOCKS |                1 | group     |          7 | 0.957254 | 0.941575 | 0.941667 |      0.434098 |    0.118929 |      0.642422 |    0.134617 |
| SHADOWSOCKS |                1 | marginal  |          0 | 0.961961 | 0.966611 | 0.966667 |      0.295187 |    0.064864 |      0.456884 |    0.074467 |
| SHADOWSOCKS |                1 | marginal  |          1 | 0.970299 | 0.966616 | 0.966667 |      0.299900 |    0.066590 |      0.469690 |    0.072121 |
| SHADOWSOCKS |                1 | marginal  |          2 | 0.962179 | 0.966599 | 0.966667 |      0.304500 |    0.071597 |      0.448064 |    0.071525 |
| SHADOWSOCKS |                1 | marginal  |          3 | 0.949573 | 0.955509 | 0.955556 |      0.306709 |    0.076596 |      0.472592 |    0.088447 |
| SHADOWSOCKS |                1 | marginal  |          4 | 0.966239 | 0.963849 | 0.963889 |      0.301671 |    0.071134 |      0.457852 |    0.074558 |
| SHADOWSOCKS |                1 | marginal  |          5 | 0.953632 | 0.955434 | 0.955556 |      0.307195 |    0.075148 |      0.478217 |    0.088748 |
| SHADOWSOCKS |                1 | marginal  |          6 | 0.962179 | 0.958295 | 0.958333 |      0.297383 |    0.066220 |      0.459762 |    0.069422 |
| SHADOWSOCKS |                1 | marginal  |          7 | 0.970716 | 0.966627 | 0.966667 |      0.304038 |    0.065618 |      0.451371 |    0.057025 |
| SHADOWSOCKS |                1 | paired    |          0 | 0.948043 | 0.955451 | 0.955556 |      0.310525 |    0.075301 |      0.545984 |    0.116684 |
| SHADOWSOCKS |                1 | paired    |          1 | 0.965362 | 0.963845 | 0.963889 |      0.306841 |    0.074056 |      0.538251 |    0.106993 |
| SHADOWSOCKS |                1 | paired    |          2 | 0.957692 | 0.963833 | 0.963889 |      0.304683 |    0.071705 |      0.480454 |    0.083684 |
| SHADOWSOCKS |                1 | paired    |          3 | 0.940362 | 0.952708 | 0.952778 |      0.326703 |    0.085771 |      0.551174 |    0.123936 |
| SHADOWSOCKS |                1 | paired    |          4 | 0.956122 | 0.950030 | 0.950000 |      0.326103 |    0.087743 |      0.571838 |    0.136282 |
| SHADOWSOCKS |                1 | paired    |          5 | 0.948002 | 0.950129 | 0.950000 |      0.335622 |    0.091340 |      0.583474 |    0.140117 |
| SHADOWSOCKS |                1 | paired    |          6 | 0.961302 | 0.952720 | 0.952778 |      0.319679 |    0.081689 |      0.566142 |    0.123918 |
| SHADOWSOCKS |                1 | paired    |          7 | 0.970294 | 0.963851 | 0.963889 |      0.305419 |    0.066811 |      0.488997 |    0.069777 |
| SHADOWSOCKS |                1 | raw       |          0 | 0.961375 | 0.952382 | 0.952778 |      0.359956 |    0.100728 |      0.444878 |    0.065185 |
| SHADOWSOCKS |                1 | raw       |          1 | 0.943505 | 0.915409 | 0.916667 |      0.401498 |    0.121392 |      0.492226 |    0.068266 |
| SHADOWSOCKS |                1 | raw       |          2 | 0.970508 | 0.955827 | 0.955556 |      0.320670 |    0.081898 |      0.482048 |    0.080380 |
| SHADOWSOCKS |                1 | raw       |          3 | 0.974567 | 0.963870 | 0.963889 |      0.299846 |    0.071317 |      0.463336 |    0.075126 |
| SHADOWSOCKS |                1 | raw       |          4 | 0.978841 | 0.963938 | 0.963889 |      0.317423 |    0.078575 |      0.459690 |    0.077372 |
| SHADOWSOCKS |                1 | raw       |          5 | 0.982681 | 0.972184 | 0.972222 |      0.296222 |    0.067729 |      0.441143 |    0.072345 |
| SHADOWSOCKS |                1 | raw       |          6 | 0.937776 | 0.943486 | 0.944444 |      0.374726 |    0.103167 |      0.468355 |    0.075248 |
| SHADOWSOCKS |                1 | raw       |          7 | 0.918979 | 0.921113 | 0.922222 |      0.392477 |    0.118271 |      0.448506 |    0.067723 |
| SHADOWSOCKS |                1 | reference |          0 | 0.966448 | 0.963873 | 0.963889 |      0.265726 |    0.057203 |      0.427430 |    0.058147 |
| SHADOWSOCKS |                1 | reference |          1 | 0.970508 | 0.963872 | 0.963889 |      0.279349 |    0.059526 |      0.456628 |    0.062061 |
| SHADOWSOCKS |                1 | reference |          2 | 0.962179 | 0.958312 | 0.958333 |      0.293656 |    0.068754 |      0.470951 |    0.072912 |
| SHADOWSOCKS |                1 | reference |          3 | 0.966448 | 0.961090 | 0.961111 |      0.281636 |    0.064739 |      0.449066 |    0.068941 |
| SHADOWSOCKS |                1 | reference |          4 | 0.966448 | 0.961090 | 0.961111 |      0.284248 |    0.064533 |      0.445367 |    0.063989 |
| SHADOWSOCKS |                1 | reference |          5 | 0.966448 | 0.961090 | 0.961111 |      0.280290 |    0.061794 |      0.443774 |    0.061279 |
| SHADOWSOCKS |                1 | reference |          6 | 0.970508 | 0.963872 | 0.963889 |      0.276170 |    0.059238 |      0.438128 |    0.061480 |
| SHADOWSOCKS |                1 | reference |          7 | 0.970508 | 0.961089 | 0.961111 |      0.277024 |    0.059656 |      0.440145 |    0.061030 |
| SHADOWSOCKS |                2 | center    |          0 | 0.947735 | 0.952866 | 0.952778 |      0.312587 |    0.075184 |      0.199531 |    0.049093 |
| SHADOWSOCKS |                2 | center    |          1 | 0.972125 | 0.972174 | 0.972222 |      0.291395 |    0.067294 |      0.229859 |    0.061653 |
| SHADOWSOCKS |                2 | center    |          2 | 0.952741 | 0.958206 | 0.958333 |      0.325684 |    0.080665 |      0.166401 |    0.035183 |
| SHADOWSOCKS |                2 | center    |          3 | 0.964189 | 0.961056 | 0.961111 |      0.310212 |    0.076722 |      0.162520 |    0.034641 |
| SHADOWSOCKS |                2 | center    |          4 | 0.967643 | 0.966745 | 0.966667 |      0.301035 |    0.075457 |      0.239321 |    0.065882 |
| SHADOWSOCKS |                2 | center    |          5 | 0.959892 | 0.950013 | 0.950000 |      0.326360 |    0.086789 |      0.231059 |    0.061173 |
| SHADOWSOCKS |                2 | center    |          6 | 0.959141 | 0.963931 | 0.963889 |      0.291168 |    0.071289 |      0.280206 |    0.083401 |
| SHADOWSOCKS |                2 | center    |          7 | 0.958886 | 0.964024 | 0.963889 |      0.294752 |    0.073222 |      0.294337 |    0.090241 |
| SHADOWSOCKS |                2 | cyclic    |          0 | 0.840183 | 0.883475 | 0.883333 |      0.559585 |    0.198265 |      0.718437 |    0.307558 |
| SHADOWSOCKS |                2 | cyclic    |          1 | 0.794762 | 0.853536 | 0.855556 |      0.610368 |    0.225389 |      0.814327 |    0.361964 |
| SHADOWSOCKS |                2 | cyclic    |          2 | 0.604029 | 0.761652 | 0.777778 |      0.685970 |    0.274691 |      1.041203 |    0.502781 |
| SHADOWSOCKS |                2 | cyclic    |          3 | 0.849561 | 0.873123 | 0.875000 |      0.558242 |    0.201376 |      0.657462 |    0.266566 |
| SHADOWSOCKS |                2 | cyclic    |          4 | 0.804969 | 0.862578 | 0.863889 |      0.566198 |    0.208542 |      0.763039 |    0.330513 |
| SHADOWSOCKS |                2 | cyclic    |          5 | 0.852827 | 0.891007 | 0.891667 |      0.550249 |    0.190003 |      0.694126 |    0.293304 |
| SHADOWSOCKS |                2 | cyclic    |          6 | 0.823737 | 0.881682 | 0.883333 |      0.526524 |    0.189335 |      0.716140 |    0.310326 |
| SHADOWSOCKS |                2 | cyclic    |          7 | 0.907592 | 0.927486 | 0.927778 |      0.511875 |    0.174971 |      0.614786 |    0.243871 |
| SHADOWSOCKS |                2 | group     |          0 | 0.873676 | 0.902056 | 0.902778 |      0.513295 |    0.174053 |      0.562133 |    0.217269 |
| SHADOWSOCKS |                2 | group     |          1 | 0.787911 | 0.851701 | 0.852778 |      0.579885 |    0.212797 |      0.735337 |    0.319403 |
| SHADOWSOCKS |                2 | group     |          2 | 0.703551 | 0.794876 | 0.802778 |      0.666168 |    0.261070 |      0.897753 |    0.413923 |
| SHADOWSOCKS |                2 | group     |          3 | 0.867423 | 0.887564 | 0.888889 |      0.512609 |    0.176072 |      0.545909 |    0.206960 |
| SHADOWSOCKS |                2 | group     |          4 | 0.844878 | 0.882426 | 0.883333 |      0.528907 |    0.186362 |      0.629448 |    0.251059 |
| SHADOWSOCKS |                2 | group     |          5 | 0.885773 | 0.907052 | 0.908333 |      0.505450 |    0.167664 |      0.580787 |    0.225434 |
| SHADOWSOCKS |                2 | group     |          6 | 0.912042 | 0.930498 | 0.930556 |      0.459647 |    0.149433 |      0.544180 |    0.205305 |
| SHADOWSOCKS |                2 | group     |          7 | 0.902704 | 0.917951 | 0.919444 |      0.497410 |    0.165316 |      0.530643 |    0.195604 |
| SHADOWSOCKS |                2 | marginal  |          0 | 0.968060 | 0.969401 | 0.969444 |      0.296677 |    0.067599 |      0.191231 |    0.042529 |
| SHADOWSOCKS |                2 | marginal  |          1 | 0.968060 | 0.969394 | 0.969444 |      0.286346 |    0.066319 |      0.213490 |    0.053873 |
| SHADOWSOCKS |                2 | marginal  |          2 | 0.956229 | 0.961096 | 0.961111 |      0.312367 |    0.077982 |      0.202887 |    0.049594 |
| SHADOWSOCKS |                2 | marginal  |          3 | 0.968060 | 0.969397 | 0.969444 |      0.298451 |    0.071386 |      0.186678 |    0.043598 |
| SHADOWSOCKS |                2 | marginal  |          4 | 0.959930 | 0.963842 | 0.963889 |      0.295715 |    0.073632 |      0.225646 |    0.059804 |
| SHADOWSOCKS |                2 | marginal  |          5 | 0.955672 | 0.963918 | 0.963889 |      0.304550 |    0.074779 |      0.221209 |    0.056157 |
| SHADOWSOCKS |                2 | marginal  |          6 | 0.959146 | 0.963873 | 0.963889 |      0.289459 |    0.068066 |      0.239562 |    0.062997 |
| SHADOWSOCKS |                2 | marginal  |          7 | 0.967867 | 0.969406 | 0.969444 |      0.291374 |    0.068716 |      0.241131 |    0.063154 |
| SHADOWSOCKS |                2 | paired    |          0 | 0.975610 | 0.974986 | 0.975000 |      0.284364 |    0.062441 |      0.220845 |    0.053931 |
| SHADOWSOCKS |                2 | paired    |          1 | 0.971738 | 0.972194 | 0.972222 |      0.286190 |    0.065723 |      0.249068 |    0.067114 |
| SHADOWSOCKS |                2 | paired    |          2 | 0.955275 | 0.961221 | 0.961111 |      0.316584 |    0.079955 |      0.274399 |    0.076222 |
| SHADOWSOCKS |                2 | paired    |          3 | 0.958928 | 0.963927 | 0.963889 |      0.297973 |    0.070177 |      0.251680 |    0.069492 |
| SHADOWSOCKS |                2 | paired    |          4 | 0.964161 | 0.966649 | 0.966667 |      0.300668 |    0.074485 |      0.253984 |    0.068271 |
| SHADOWSOCKS |                2 | paired    |          5 | 0.963145 | 0.964015 | 0.963889 |      0.319395 |    0.080727 |      0.263400 |    0.073820 |
| SHADOWSOCKS |                2 | paired    |          6 | 0.964189 | 0.966606 | 0.966667 |      0.290045 |    0.069023 |      0.250751 |    0.066298 |
| SHADOWSOCKS |                2 | paired    |          7 | 0.972125 | 0.972175 | 0.972222 |      0.294259 |    0.070528 |      0.241092 |    0.061560 |
| SHADOWSOCKS |                2 | raw       |          0 | 0.315810 | 0.672041 | 0.730556 |      0.833725 |    0.341833 |      2.022003 |    0.956938 |
| SHADOWSOCKS |                2 | raw       |          1 | 0.375319 | 0.687224 | 0.736111 |      0.824893 |    0.334764 |      1.956682 |    0.928577 |
| SHADOWSOCKS |                2 | raw       |          2 | 0.525590 | 0.756613 | 0.791667 |      0.691990 |    0.265747 |      1.482633 |    0.682564 |
| SHADOWSOCKS |                2 | raw       |          3 | 0.489226 | 0.749318 | 0.791667 |      0.815197 |    0.316270 |      1.927606 |    0.864481 |
| SHADOWSOCKS |                2 | raw       |          4 | 0.458476 | 0.724771 | 0.763889 |      0.715647 |    0.296066 |      1.595496 |    0.770597 |
| SHADOWSOCKS |                2 | raw       |          5 | 0.492530 | 0.740768 | 0.777778 |      0.746239 |    0.289035 |      1.699255 |    0.774285 |
| SHADOWSOCKS |                2 | raw       |          6 | 0.335060 | 0.672325 | 0.722222 |      0.793382 |    0.337260 |      1.911888 |    0.936746 |
| SHADOWSOCKS |                2 | raw       |          7 | 0.329160 | 0.669510 | 0.719444 |      0.804428 |    0.340096 |      1.878988 |    0.913492 |
| SHADOWSOCKS |                2 | reference |          0 | 0.955285 | 0.961089 | 0.961111 |      0.284230 |    0.064576 |      0.196106 |    0.051837 |
| SHADOWSOCKS |                2 | reference |          1 | 0.955285 | 0.961090 | 0.961111 |      0.286425 |    0.065834 |      0.203589 |    0.055864 |
| SHADOWSOCKS |                2 | reference |          2 | 0.943283 | 0.952816 | 0.952778 |      0.306037 |    0.077587 |      0.237659 |    0.071318 |
| SHADOWSOCKS |                2 | reference |          3 | 0.943657 | 0.952643 | 0.952778 |      0.294820 |    0.070406 |      0.212627 |    0.058812 |
| SHADOWSOCKS |                2 | reference |          4 | 0.959350 | 0.963868 | 0.963889 |      0.287829 |    0.071434 |      0.232677 |    0.065976 |
| SHADOWSOCKS |                2 | reference |          5 | 0.959350 | 0.963868 | 0.963889 |      0.288138 |    0.070564 |      0.232479 |    0.066270 |
| SHADOWSOCKS |                2 | reference |          6 | 0.951220 | 0.958312 | 0.958333 |      0.284559 |    0.067841 |      0.219619 |    0.060963 |
| SHADOWSOCKS |                2 | reference |          7 | 0.942276 | 0.952767 | 0.952778 |      0.292818 |    0.072643 |      0.236464 |    0.070029 |
| VLESS       |                0 | center    |          0 | 0.559190 | 0.744215 | 0.780556 |      0.760655 |    0.307814 |      1.335407 |    0.611886 |
| VLESS       |                0 | center    |          1 | 0.472621 | 0.702413 | 0.741667 |      0.837561 |    0.338542 |      1.455697 |    0.691618 |
| VLESS       |                0 | center    |          2 | 0.606381 | 0.750433 | 0.777778 |      0.811270 |    0.315616 |      1.225176 |    0.539679 |
| VLESS       |                0 | center    |          3 | 0.448172 | 0.696943 | 0.730556 |      0.904535 |    0.365377 |      1.502032 |    0.732537 |
| VLESS       |                0 | center    |          4 | 0.455531 | 0.690425 | 0.725000 |      0.957085 |    0.379370 |      1.664684 |    0.787864 |
| VLESS       |                0 | center    |          5 | 0.541087 | 0.729300 | 0.758333 |      0.876848 |    0.343365 |      1.424719 |    0.658420 |
| VLESS       |                0 | center    |          6 | 0.474198 | 0.719156 | 0.752778 |      0.893856 |    0.358640 |      1.638868 |    0.774605 |
| VLESS       |                0 | center    |          7 | 0.586229 | 0.745058 | 0.769444 |      0.827504 |    0.324164 |      1.412667 |    0.637063 |
| VLESS       |                0 | cyclic    |          0 | 0.701058 | 0.796689 | 0.813889 |      0.746823 |    0.302939 |      0.899272 |    0.396215 |
| VLESS       |                0 | cyclic    |          1 | 0.535404 | 0.741052 | 0.772222 |      0.836160 |    0.336122 |      1.205311 |    0.562462 |
| VLESS       |                0 | cyclic    |          2 | 0.665651 | 0.787398 | 0.808333 |      0.728040 |    0.291185 |      0.876915 |    0.386893 |
| VLESS       |                0 | cyclic    |          3 | 0.534468 | 0.748151 | 0.775000 |      0.849880 |    0.342290 |      1.154945 |    0.552026 |
| VLESS       |                0 | cyclic    |          4 | 0.583369 | 0.747906 | 0.766667 |      0.848137 |    0.339523 |      1.234193 |    0.575119 |
| VLESS       |                0 | cyclic    |          5 | 0.620273 | 0.780124 | 0.797222 |      0.829183 |    0.322384 |      1.043213 |    0.475034 |
| VLESS       |                0 | cyclic    |          6 | 0.638043 | 0.785163 | 0.802778 |      0.806578 |    0.320713 |      1.044081 |    0.479057 |
| VLESS       |                0 | cyclic    |          7 | 0.616511 | 0.778656 | 0.802778 |      0.772222 |    0.305199 |      1.024096 |    0.457352 |
| VLESS       |                0 | group     |          0 | 0.732565 | 0.809264 | 0.822222 |      0.737806 |    0.297986 |      0.862764 |    0.380539 |
| VLESS       |                0 | group     |          1 | 0.564823 | 0.761404 | 0.791667 |      0.797197 |    0.311276 |      1.097909 |    0.500850 |
| VLESS       |                0 | group     |          2 | 0.694562 | 0.791942 | 0.811111 |      0.746693 |    0.291519 |      0.911746 |    0.385036 |
| VLESS       |                0 | group     |          3 | 0.580941 | 0.752115 | 0.769444 |      0.841711 |    0.333042 |      1.084587 |    0.512822 |
| VLESS       |                0 | group     |          4 | 0.606716 | 0.762946 | 0.777778 |      0.842776 |    0.335419 |      1.221045 |    0.565396 |
| VLESS       |                0 | group     |          5 | 0.644377 | 0.792676 | 0.808333 |      0.802865 |    0.310951 |      1.009189 |    0.454068 |
| VLESS       |                0 | group     |          6 | 0.657366 | 0.808166 | 0.825000 |      0.789866 |    0.302997 |      1.006738 |    0.445853 |
| VLESS       |                0 | group     |          7 | 0.603842 | 0.767679 | 0.794444 |      0.776354 |    0.305204 |      1.065200 |    0.472621 |
| VLESS       |                0 | marginal  |          0 | 0.711538 | 0.806665 | 0.825000 |      0.704512 |    0.274886 |      1.010264 |    0.441898 |
| VLESS       |                0 | marginal  |          1 | 0.670176 | 0.772016 | 0.788889 |      0.731598 |    0.288589 |      1.046126 |    0.464532 |
| VLESS       |                0 | marginal  |          2 | 0.686153 | 0.775171 | 0.791667 |      0.744168 |    0.289303 |      1.010730 |    0.430907 |
| VLESS       |                0 | marginal  |          3 | 0.651569 | 0.784448 | 0.802778 |      0.747153 |    0.291043 |      0.999285 |    0.447989 |
| VLESS       |                0 | marginal  |          4 | 0.636912 | 0.749140 | 0.769444 |      0.783849 |    0.308003 |      1.103497 |    0.492124 |
| VLESS       |                0 | marginal  |          5 | 0.624099 | 0.771634 | 0.794444 |      0.763384 |    0.293412 |      1.059563 |    0.468552 |
| VLESS       |                0 | marginal  |          6 | 0.644833 | 0.769990 | 0.791667 |      0.744801 |    0.284459 |      1.004097 |    0.440406 |
| VLESS       |                0 | marginal  |          7 | 0.711292 | 0.793569 | 0.808333 |      0.745740 |    0.288127 |      1.072947 |    0.460477 |
| VLESS       |                0 | paired    |          0 | 0.709307 | 0.792841 | 0.808333 |      0.725244 |    0.285138 |      0.901310 |    0.380948 |
| VLESS       |                0 | paired    |          1 | 0.646496 | 0.757608 | 0.777778 |      0.764807 |    0.305018 |      1.033034 |    0.449600 |
| VLESS       |                0 | paired    |          2 | 0.743068 | 0.800743 | 0.811111 |      0.739244 |    0.291675 |      0.875131 |    0.362051 |
| VLESS       |                0 | paired    |          3 | 0.643186 | 0.763423 | 0.777778 |      0.791202 |    0.311292 |      1.019513 |    0.464040 |
| VLESS       |                0 | paired    |          4 | 0.573638 | 0.737393 | 0.755556 |      0.808006 |    0.323766 |      1.221445 |    0.552896 |
| VLESS       |                0 | paired    |          5 | 0.687936 | 0.792176 | 0.800000 |      0.759138 |    0.294869 |      1.011265 |    0.441417 |
| VLESS       |                0 | paired    |          6 | 0.650321 | 0.770212 | 0.780556 |      0.776526 |    0.296563 |      1.050020 |    0.461857 |
| VLESS       |                0 | paired    |          7 | 0.690392 | 0.782840 | 0.797222 |      0.745678 |    0.288977 |      1.049283 |    0.446265 |
| VLESS       |                0 | raw       |          0 | 0.513295 | 0.704094 | 0.752778 |      0.894806 |    0.361240 |      1.644034 |    0.736941 |
| VLESS       |                0 | raw       |          1 | 0.468436 | 0.691354 | 0.741667 |      0.931044 |    0.366272 |      1.688640 |    0.754877 |
| VLESS       |                0 | raw       |          2 | 0.503524 | 0.697505 | 0.747222 |      0.879869 |    0.340736 |      1.542665 |    0.666715 |
| VLESS       |                0 | raw       |          3 | 0.504040 | 0.729201 | 0.772222 |      0.884504 |    0.336700 |      1.394837 |    0.648910 |
| VLESS       |                0 | raw       |          4 | 0.480062 | 0.709282 | 0.758333 |      1.001540 |    0.376653 |      1.817153 |    0.772502 |
| VLESS       |                0 | raw       |          5 | 0.485556 | 0.706837 | 0.755556 |      0.956737 |    0.367210 |      1.678039 |    0.725775 |
| VLESS       |                0 | raw       |          6 | 0.500000 | 0.739851 | 0.791667 |      0.924870 |    0.343786 |      1.838801 |    0.772114 |
| VLESS       |                0 | raw       |          7 | 0.459459 | 0.694009 | 0.747222 |      1.013475 |    0.381518 |      2.156752 |    0.875017 |
| VLESS       |                0 | reference |          0 | 0.759396 | 0.837010 | 0.844444 |      0.630147 |    0.243775 |      0.776569 |    0.316660 |
| VLESS       |                0 | reference |          1 | 0.770082 | 0.826793 | 0.833333 |      0.635549 |    0.250104 |      0.765162 |    0.315274 |
| VLESS       |                0 | reference |          2 | 0.725132 | 0.812782 | 0.822222 |      0.640030 |    0.251973 |      0.784423 |    0.321266 |
| VLESS       |                0 | reference |          3 | 0.753768 | 0.830923 | 0.838889 |      0.639452 |    0.251196 |      0.767243 |    0.316598 |
| VLESS       |                0 | reference |          4 | 0.760264 | 0.831713 | 0.838889 |      0.632228 |    0.242306 |      0.776785 |    0.313085 |
| VLESS       |                0 | reference |          5 | 0.759604 | 0.840085 | 0.847222 |      0.644814 |    0.242664 |      0.791375 |    0.311247 |
| VLESS       |                0 | reference |          6 | 0.773749 | 0.844196 | 0.850000 |      0.661230 |    0.243179 |      0.756307 |    0.299213 |
| VLESS       |                0 | reference |          7 | 0.765214 | 0.831416 | 0.838889 |      0.657600 |    0.247122 |      0.782485 |    0.309650 |
| VLESS       |                1 | center    |          0 | 0.501470 | 0.614282 | 0.655556 |      1.523425 |    0.470657 |      2.655594 |    0.613179 |
| VLESS       |                1 | center    |          1 | 0.504084 | 0.622222 | 0.666667 |      1.538587 |    0.475881 |      2.644168 |    0.626332 |
| VLESS       |                1 | center    |          2 | 0.693360 | 0.706688 | 0.730556 |      1.133846 |    0.379400 |      1.925534 |    0.532002 |
| VLESS       |                1 | center    |          3 | 0.617504 | 0.674336 | 0.711111 |      1.334348 |    0.413999 |      2.377048 |    0.551533 |
| VLESS       |                1 | center    |          4 | 0.532700 | 0.633638 | 0.680556 |      1.602309 |    0.450282 |      3.149520 |    0.676680 |
| VLESS       |                1 | center    |          5 | 0.523706 | 0.625358 | 0.672222 |      1.490639 |    0.444902 |      2.832997 |    0.648188 |
| VLESS       |                1 | center    |          6 | 0.512248 | 0.624567 | 0.669444 |      1.615932 |    0.476580 |      2.950209 |    0.638322 |
| VLESS       |                1 | center    |          7 | 0.488295 | 0.627093 | 0.677778 |      1.690933 |    0.491232 |      2.994123 |    0.649152 |
| VLESS       |                1 | cyclic    |          0 | 0.793784 | 0.751562 | 0.766667 |      0.895040 |    0.341737 |      1.259924 |    0.398945 |
| VLESS       |                1 | cyclic    |          1 | 0.508029 | 0.586958 | 0.627778 |      1.102303 |    0.422646 |      1.830810 |    0.643173 |
| VLESS       |                1 | cyclic    |          2 | 0.751879 | 0.727605 | 0.750000 |      0.904640 |    0.348942 |      1.325564 |    0.462342 |
| VLESS       |                1 | cyclic    |          3 | 0.674725 | 0.689797 | 0.727778 |      1.037655 |    0.377158 |      1.709272 |    0.545403 |
| VLESS       |                1 | cyclic    |          4 | 0.582891 | 0.653402 | 0.683333 |      1.061703 |    0.411032 |      1.785149 |    0.652663 |
| VLESS       |                1 | cyclic    |          5 | 0.749993 | 0.739566 | 0.761111 |      0.936868 |    0.343134 |      1.337813 |    0.420527 |
| VLESS       |                1 | cyclic    |          6 | 0.607760 | 0.659468 | 0.680556 |      1.091349 |    0.408405 |      1.777734 |    0.628488 |
| VLESS       |                1 | cyclic    |          7 | 0.723892 | 0.734899 | 0.752778 |      0.903708 |    0.359183 |      1.331346 |    0.496550 |
| VLESS       |                1 | group     |          0 | 0.847440 | 0.762407 | 0.772222 |      0.839628 |    0.327845 |      1.099838 |    0.359563 |
| VLESS       |                1 | group     |          1 | 0.534314 | 0.622749 | 0.663889 |      1.035381 |    0.403533 |      1.597382 |    0.571814 |
| VLESS       |                1 | group     |          2 | 0.814636 | 0.771012 | 0.791667 |      0.848276 |    0.322286 |      1.151358 |    0.386500 |
| VLESS       |                1 | group     |          3 | 0.740497 | 0.724876 | 0.755556 |      0.966818 |    0.353882 |      1.505358 |    0.465091 |
| VLESS       |                1 | group     |          4 | 0.635072 | 0.680046 | 0.708333 |      0.998215 |    0.383475 |      1.624629 |    0.591255 |
| VLESS       |                1 | group     |          5 | 0.797089 | 0.761319 | 0.777778 |      0.861039 |    0.319452 |      1.135261 |    0.356261 |
| VLESS       |                1 | group     |          6 | 0.702629 | 0.705990 | 0.727778 |      1.007061 |    0.380245 |      1.482103 |    0.521932 |
| VLESS       |                1 | group     |          7 | 0.809888 | 0.774573 | 0.788889 |      0.833265 |    0.323334 |      1.104445 |    0.393580 |
| VLESS       |                1 | marginal  |          0 | 0.676940 | 0.696893 | 0.713889 |      0.995002 |    0.376724 |      1.293080 |    0.419366 |
| VLESS       |                1 | marginal  |          1 | 0.657053 | 0.686190 | 0.708333 |      1.016021 |    0.383493 |      1.329065 |    0.430926 |
| VLESS       |                1 | marginal  |          2 | 0.759656 | 0.743875 | 0.758333 |      0.942963 |    0.355165 |      1.225272 |    0.403139 |
| VLESS       |                1 | marginal  |          3 | 0.802349 | 0.753631 | 0.769444 |      0.891811 |    0.337269 |      1.084596 |    0.347558 |
| VLESS       |                1 | marginal  |          4 | 0.675186 | 0.692679 | 0.722222 |      0.998755 |    0.371025 |      1.362313 |    0.460310 |
| VLESS       |                1 | marginal  |          5 | 0.744104 | 0.729771 | 0.752778 |      0.916507 |    0.341724 |      1.152668 |    0.375665 |
| VLESS       |                1 | marginal  |          6 | 0.652586 | 0.699623 | 0.725000 |      1.009568 |    0.365416 |      1.343772 |    0.427652 |
| VLESS       |                1 | marginal  |          7 | 0.588776 | 0.678297 | 0.713889 |      1.111123 |    0.401171 |      1.568149 |    0.481148 |
| VLESS       |                1 | paired    |          0 | 0.885357 | 0.811582 | 0.813889 |      0.779654 |    0.293587 |      0.776479 |    0.255923 |
| VLESS       |                1 | paired    |          1 | 0.828488 | 0.778279 | 0.788889 |      0.818745 |    0.307543 |      0.863274 |    0.290471 |
| VLESS       |                1 | paired    |          2 | 0.825166 | 0.786039 | 0.800000 |      0.868268 |    0.321282 |      1.075626 |    0.355164 |
| VLESS       |                1 | paired    |          3 | 0.830197 | 0.784792 | 0.797222 |      0.842052 |    0.317915 |      1.012261 |    0.335606 |
| VLESS       |                1 | paired    |          4 | 0.781962 | 0.761795 | 0.777778 |      0.863323 |    0.314489 |      1.157112 |    0.404614 |
| VLESS       |                1 | paired    |          5 | 0.856003 | 0.806047 | 0.816667 |      0.813874 |    0.298773 |      0.930865 |    0.305830 |
| VLESS       |                1 | paired    |          6 | 0.863997 | 0.808201 | 0.816667 |      0.795988 |    0.290329 |      0.851370 |    0.292419 |
| VLESS       |                1 | paired    |          7 | 0.884612 | 0.835717 | 0.844444 |      0.786856 |    0.283137 |      0.892480 |    0.292022 |
| VLESS       |                1 | raw       |          0 | 0.549199 | 0.556308 | 0.616667 |      1.499984 |    0.473249 |      2.826876 |    0.713462 |
| VLESS       |                1 | raw       |          1 | 0.524841 | 0.608539 | 0.661111 |      1.443634 |    0.441119 |      2.812660 |    0.691518 |
| VLESS       |                1 | raw       |          2 | 0.489367 | 0.625776 | 0.672222 |      1.593013 |    0.479857 |      3.296582 |    0.807708 |
| VLESS       |                1 | raw       |          3 | 0.535408 | 0.628341 | 0.680556 |      1.459401 |    0.440673 |      2.986646 |    0.737516 |
| VLESS       |                1 | raw       |          4 | 0.511031 | 0.633270 | 0.688889 |      1.703141 |    0.468461 |      3.709441 |    0.832597 |
| VLESS       |                1 | raw       |          5 | 0.500735 | 0.609223 | 0.669444 |      1.656488 |    0.479175 |      3.530816 |    0.835293 |
| VLESS       |                1 | raw       |          6 | 0.549038 | 0.655804 | 0.702778 |      1.506239 |    0.424950 |      3.010652 |    0.678342 |
| VLESS       |                1 | raw       |          7 | 0.488621 | 0.641110 | 0.700000 |      1.596104 |    0.458283 |      3.291430 |    0.740723 |
| VLESS       |                1 | reference |          0 | 0.928836 | 0.834602 | 0.838889 |      0.675847 |    0.243906 |      0.440189 |    0.124413 |
| VLESS       |                1 | reference |          1 | 0.925301 | 0.832717 | 0.838889 |      0.694780 |    0.244418 |      0.450650 |    0.119432 |
| VLESS       |                1 | reference |          2 | 0.923077 | 0.825460 | 0.833333 |      0.682989 |    0.245635 |      0.442469 |    0.118042 |
| VLESS       |                1 | reference |          3 | 0.926444 | 0.826953 | 0.833333 |      0.671192 |    0.252240 |      0.405131 |    0.111579 |
| VLESS       |                1 | reference |          4 | 0.935181 | 0.830617 | 0.841667 |      0.671221 |    0.237614 |      0.414355 |    0.110620 |
| VLESS       |                1 | reference |          5 | 0.939668 | 0.843836 | 0.852778 |      0.662544 |    0.239673 |      0.402423 |    0.111964 |
| VLESS       |                1 | reference |          6 | 0.947241 | 0.851867 | 0.858333 |      0.672776 |    0.230144 |      0.430614 |    0.112246 |
| VLESS       |                1 | reference |          7 | 0.928311 | 0.835878 | 0.841667 |      0.663141 |    0.228107 |      0.415603 |    0.111052 |
| VLESS       |                2 | center    |          0 | 0.493476 | 0.694607 | 0.705556 |      0.889265 |    0.356730 |      1.387354 |    0.647097 |
| VLESS       |                2 | center    |          1 | 0.503200 | 0.703567 | 0.719444 |      0.986423 |    0.374084 |      1.573764 |    0.698810 |
| VLESS       |                2 | center    |          2 | 0.530047 | 0.730864 | 0.747222 |      0.724112 |    0.285963 |      1.148244 |    0.519341 |
| VLESS       |                2 | center    |          3 | 0.522746 | 0.739062 | 0.761111 |      0.767054 |    0.306771 |      1.344328 |    0.623798 |
| VLESS       |                2 | center    |          4 | 0.596735 | 0.749555 | 0.755556 |      0.795769 |    0.309370 |      1.185238 |    0.528632 |
| VLESS       |                2 | center    |          5 | 0.699589 | 0.788253 | 0.788889 |      0.737579 |    0.303602 |      1.127814 |    0.507823 |
| VLESS       |                2 | center    |          6 | 0.577609 | 0.728329 | 0.730556 |      0.887371 |    0.350626 |      1.318724 |    0.600807 |
| VLESS       |                2 | center    |          7 | 0.450841 | 0.684696 | 0.708333 |      0.895411 |    0.363504 |      1.427410 |    0.666174 |
| VLESS       |                2 | cyclic    |          0 | 0.348836 | 0.645487 | 0.677778 |      0.823016 |    0.353539 |      1.226967 |    0.628945 |
| VLESS       |                2 | cyclic    |          1 | 0.361305 | 0.629441 | 0.655556 |      0.881782 |    0.368978 |      1.176255 |    0.598814 |
| VLESS       |                2 | cyclic    |          2 | 0.528289 | 0.705536 | 0.716667 |      0.740424 |    0.316794 |      1.065728 |    0.525919 |
| VLESS       |                2 | cyclic    |          3 | 0.330522 | 0.639651 | 0.675000 |      0.853754 |    0.370186 |      1.249323 |    0.646785 |
| VLESS       |                2 | cyclic    |          4 | 0.519797 | 0.703422 | 0.711111 |      0.764134 |    0.321562 |      1.042964 |    0.511707 |
| VLESS       |                2 | cyclic    |          5 | 0.621312 | 0.749966 | 0.758333 |      0.754188 |    0.318595 |      1.048994 |    0.507754 |
| VLESS       |                2 | cyclic    |          6 | 0.409236 | 0.668086 | 0.691667 |      0.872506 |    0.366683 |      1.200294 |    0.613120 |
| VLESS       |                2 | cyclic    |          7 | 0.582084 | 0.725669 | 0.727778 |      0.735886 |    0.306575 |      0.973391 |    0.471921 |
| VLESS       |                2 | group     |          0 | 0.418145 | 0.658264 | 0.675000 |      0.793026 |    0.343987 |      1.181424 |    0.600540 |
| VLESS       |                2 | group     |          1 | 0.534162 | 0.703418 | 0.711111 |      0.815897 |    0.337410 |      1.067426 |    0.528540 |
| VLESS       |                2 | group     |          2 | 0.643065 | 0.751129 | 0.758333 |      0.731072 |    0.306312 |      0.989692 |    0.474683 |
| VLESS       |                2 | group     |          3 | 0.508414 | 0.710168 | 0.725000 |      0.811667 |    0.346169 |      1.119368 |    0.564072 |
| VLESS       |                2 | group     |          4 | 0.663030 | 0.756877 | 0.761111 |      0.737517 |    0.304935 |      0.962548 |    0.455650 |
| VLESS       |                2 | group     |          5 | 0.625232 | 0.745953 | 0.752778 |      0.743770 |    0.313294 |      1.029302 |    0.496295 |
| VLESS       |                2 | group     |          6 | 0.609843 | 0.742322 | 0.744444 |      0.819556 |    0.331961 |      1.026473 |    0.501528 |
| VLESS       |                2 | group     |          7 | 0.680400 | 0.777791 | 0.777778 |      0.722938 |    0.294853 |      0.912206 |    0.433527 |
| VLESS       |                2 | marginal  |          0 | 0.631292 | 0.758110 | 0.761111 |      0.726103 |    0.284083 |      1.010232 |    0.455700 |
| VLESS       |                2 | marginal  |          1 | 0.624263 | 0.752498 | 0.752778 |      0.798137 |    0.303768 |      1.140502 |    0.505084 |
| VLESS       |                2 | marginal  |          2 | 0.666461 | 0.776851 | 0.777778 |      0.715809 |    0.279052 |      0.975779 |    0.426701 |
| VLESS       |                2 | marginal  |          3 | 0.658780 | 0.773608 | 0.775000 |      0.715144 |    0.281315 |      0.974038 |    0.436811 |
| VLESS       |                2 | marginal  |          4 | 0.669857 | 0.775014 | 0.775000 |      0.746274 |    0.286599 |      0.996331 |    0.421801 |
| VLESS       |                2 | marginal  |          5 | 0.673645 | 0.789762 | 0.791667 |      0.701084 |    0.279369 |      0.945482 |    0.418231 |
| VLESS       |                2 | marginal  |          6 | 0.664734 | 0.770244 | 0.769444 |      0.758036 |    0.295951 |      1.030497 |    0.460927 |
| VLESS       |                2 | marginal  |          7 | 0.611603 | 0.750735 | 0.752778 |      0.753839 |    0.301544 |      1.055276 |    0.488193 |
| VLESS       |                2 | paired    |          0 | 0.734921 | 0.800211 | 0.800000 |      0.731435 |    0.283359 |      0.993330 |    0.429671 |
| VLESS       |                2 | paired    |          1 | 0.740377 | 0.798908 | 0.802778 |      0.751649 |    0.287158 |      1.001102 |    0.433882 |
| VLESS       |                2 | paired    |          2 | 0.732192 | 0.800248 | 0.805556 |      0.735058 |    0.290540 |      0.993948 |    0.434488 |
| VLESS       |                2 | paired    |          3 | 0.720270 | 0.786603 | 0.791667 |      0.722530 |    0.292279 |      1.026560 |    0.463292 |
| VLESS       |                2 | paired    |          4 | 0.746282 | 0.798369 | 0.805556 |      0.743803 |    0.286439 |      1.005767 |    0.419428 |
| VLESS       |                2 | paired    |          5 | 0.744478 | 0.801772 | 0.811111 |      0.717765 |    0.286494 |      1.004208 |    0.431346 |
| VLESS       |                2 | paired    |          6 | 0.750466 | 0.804737 | 0.808333 |      0.750536 |    0.291895 |      0.991799 |    0.426623 |
| VLESS       |                2 | paired    |          7 | 0.678861 | 0.773917 | 0.775000 |      0.733238 |    0.289973 |      0.968830 |    0.427715 |
| VLESS       |                2 | raw       |          0 | 0.361559 | 0.659378 | 0.708333 |      1.142475 |    0.459094 |      2.386096 |    1.057899 |
| VLESS       |                2 | raw       |          1 | 0.387626 | 0.672048 | 0.722222 |      1.226551 |    0.450847 |      2.588201 |    1.066042 |
| VLESS       |                2 | raw       |          2 | 0.285714 | 0.637187 | 0.697222 |      0.965244 |    0.398227 |      2.102604 |    0.956901 |
| VLESS       |                2 | raw       |          3 | 0.318008 | 0.655119 | 0.711111 |      0.952235 |    0.393132 |      2.035328 |    0.943708 |
| VLESS       |                2 | raw       |          4 | 0.300979 | 0.635235 | 0.688889 |      1.049030 |    0.421451 |      2.160912 |    0.982614 |
| VLESS       |                2 | raw       |          5 | 0.243590 | 0.630289 | 0.702778 |      1.000047 |    0.415020 |      2.210898 |    1.011661 |
| VLESS       |                2 | raw       |          6 | 0.375000 | 0.669881 | 0.719444 |      1.070700 |    0.431485 |      2.189900 |    1.009199 |
| VLESS       |                2 | raw       |          7 | 0.361559 | 0.665429 | 0.716667 |      1.101126 |    0.439055 |      2.418566 |    1.055187 |
| VLESS       |                2 | reference |          0 | 0.814112 | 0.847973 | 0.852778 |      0.671238 |    0.249022 |      0.848730 |    0.330256 |
| VLESS       |                2 | reference |          1 | 0.760107 | 0.812873 | 0.816667 |      0.702734 |    0.258394 |      0.887218 |    0.348393 |
| VLESS       |                2 | reference |          2 | 0.782154 | 0.826396 | 0.830556 |      0.676548 |    0.253102 |      0.860069 |    0.344357 |
| VLESS       |                2 | reference |          3 | 0.729539 | 0.790233 | 0.797222 |      0.679038 |    0.264558 |      0.906354 |    0.379229 |
| VLESS       |                2 | reference |          4 | 0.771903 | 0.818340 | 0.825000 |      0.666255 |    0.253989 |      0.885989 |    0.352419 |
| VLESS       |                2 | reference |          5 | 0.773123 | 0.819049 | 0.825000 |      0.653759 |    0.255823 |      0.859435 |    0.353838 |
| VLESS       |                2 | reference |          6 | 0.775690 | 0.817632 | 0.825000 |      0.692871 |    0.263118 |      0.873961 |    0.348774 |
| VLESS       |                2 | reference |          7 | 0.796758 | 0.826895 | 0.836111 |      0.679566 |    0.255980 |      0.855447 |    0.338669 |

## 业务

| protocol    |   business_group | arm       | label_id                             | is_new   |       F1 |   recall |
|:------------|-----------------:|:----------|:-------------------------------------|:---------|---------:|---------:|
| SHADOWSOCKS |                0 | center    | bing.com::search_results_view        | False    | 0.958364 | 0.950000 |
| SHADOWSOCKS |                0 | center    | developer.mozilla.org::document_view | False    | 0.986789 | 0.997917 |
| SHADOWSOCKS |                0 | center    | github.com::repository_view          | True     | 0.981496 | 0.964583 |
| SHADOWSOCKS |                0 | center    | wikipedia.org::article_view          | False    | 0.963872 | 0.977083 |
| SHADOWSOCKS |                0 | center    | youtube.com::search_results_view     | True     | 0.928257 | 0.875000 |
| SHADOWSOCKS |                0 | center    | youtube.com::video_playback          | False    | 0.937010 | 0.991667 |
| SHADOWSOCKS |                0 | cyclic    | bing.com::search_results_view        | False    | 0.974359 | 0.950000 |
| SHADOWSOCKS |                0 | cyclic    | developer.mozilla.org::document_view | False    | 0.971528 | 0.975000 |
| SHADOWSOCKS |                0 | cyclic    | github.com::repository_view          | True     | 0.996899 | 0.997917 |
| SHADOWSOCKS |                0 | cyclic    | wikipedia.org::article_view          | False    | 0.954449 | 0.972917 |
| SHADOWSOCKS |                0 | cyclic    | youtube.com::search_results_view     | True     | 0.895210 | 0.827083 |
| SHADOWSOCKS |                0 | cyclic    | youtube.com::video_playback          | False    | 0.912593 | 0.983333 |
| SHADOWSOCKS |                0 | group     | bing.com::search_results_view        | False    | 0.974359 | 0.950000 |
| SHADOWSOCKS |                0 | group     | developer.mozilla.org::document_view | False    | 0.972131 | 0.983333 |
| SHADOWSOCKS |                0 | group     | github.com::repository_view          | True     | 0.997967 | 1.000000 |
| SHADOWSOCKS |                0 | group     | wikipedia.org::article_view          | False    | 0.958053 | 0.968750 |
| SHADOWSOCKS |                0 | group     | youtube.com::search_results_view     | True     | 0.880999 | 0.797917 |
| SHADOWSOCKS |                0 | group     | youtube.com::video_playback          | False    | 0.903765 | 0.989583 |
| SHADOWSOCKS |                0 | marginal  | bing.com::search_results_view        | False    | 0.974359 | 0.950000 |
| SHADOWSOCKS |                0 | marginal  | developer.mozilla.org::document_view | False    | 0.984853 | 1.000000 |
| SHADOWSOCKS |                0 | marginal  | github.com::repository_view          | True     | 1.000000 | 1.000000 |
| SHADOWSOCKS |                0 | marginal  | wikipedia.org::article_view          | False    | 0.963661 | 0.972917 |
| SHADOWSOCKS |                0 | marginal  | youtube.com::search_results_view     | True     | 0.930082 | 0.887500 |
| SHADOWSOCKS |                0 | marginal  | youtube.com::video_playback          | False    | 0.936248 | 0.979167 |
| SHADOWSOCKS |                0 | paired    | bing.com::search_results_view        | False    | 0.974359 | 0.950000 |
| SHADOWSOCKS |                0 | paired    | developer.mozilla.org::document_view | False    | 0.990851 | 0.997917 |
| SHADOWSOCKS |                0 | paired    | github.com::repository_view          | True     | 1.000000 | 1.000000 |
| SHADOWSOCKS |                0 | paired    | wikipedia.org::article_view          | False    | 0.968136 | 0.985417 |
| SHADOWSOCKS |                0 | paired    | youtube.com::search_results_view     | True     | 0.922944 | 0.897917 |
| SHADOWSOCKS |                0 | paired    | youtube.com::video_playback          | False    | 0.926908 | 0.952083 |
| SHADOWSOCKS |                0 | raw       | bing.com::search_results_view        | False    | 0.974359 | 0.950000 |
| SHADOWSOCKS |                0 | raw       | developer.mozilla.org::document_view | False    | 0.976849 | 0.962500 |
| SHADOWSOCKS |                0 | raw       | github.com::repository_view          | True     | 0.972110 | 0.945833 |
| SHADOWSOCKS |                0 | raw       | wikipedia.org::article_view          | False    | 0.959811 | 0.997917 |
| SHADOWSOCKS |                0 | raw       | youtube.com::search_results_view     | True     | 0.834376 | 0.758333 |
| SHADOWSOCKS |                0 | raw       | youtube.com::video_playback          | False    | 0.893334 | 1.000000 |
| SHADOWSOCKS |                0 | reference | bing.com::search_results_view        | False    | 0.973234 | 0.947917 |
| SHADOWSOCKS |                0 | reference | developer.mozilla.org::document_view | False    | 0.990902 | 1.000000 |
| SHADOWSOCKS |                0 | reference | github.com::repository_view          | True     | 0.998932 | 0.997917 |
| SHADOWSOCKS |                0 | reference | wikipedia.org::article_view          | False    | 0.967073 | 0.983333 |
| SHADOWSOCKS |                0 | reference | youtube.com::search_results_view     | True     | 0.913990 | 0.895833 |
| SHADOWSOCKS |                0 | reference | youtube.com::video_playback          | False    | 0.918339 | 0.937500 |
| SHADOWSOCKS |                1 | center    | bing.com::search_results_view        | True     | 0.964259 | 0.950000 |
| SHADOWSOCKS |                1 | center    | developer.mozilla.org::document_view | False    | 0.966601 | 0.993750 |
| SHADOWSOCKS |                1 | center    | github.com::repository_view          | False    | 0.980118 | 0.979167 |
| SHADOWSOCKS |                1 | center    | wikipedia.org::article_view          | True     | 0.949406 | 0.937500 |
| SHADOWSOCKS |                1 | center    | youtube.com::search_results_view     | False    | 0.940256 | 0.887500 |
| SHADOWSOCKS |                1 | center    | youtube.com::video_playback          | False    | 0.946844 | 1.000000 |
| SHADOWSOCKS |                1 | cyclic    | bing.com::search_results_view        | True     | 0.973344 | 0.950000 |
| SHADOWSOCKS |                1 | cyclic    | developer.mozilla.org::document_view | False    | 0.856359 | 0.997917 |
| SHADOWSOCKS |                1 | cyclic    | github.com::repository_view          | False    | 0.991818 | 0.997917 |
| SHADOWSOCKS |                1 | cyclic    | wikipedia.org::article_view          | True     | 0.756179 | 0.656250 |
| SHADOWSOCKS |                1 | cyclic    | youtube.com::search_results_view     | False    | 0.898635 | 0.831250 |
| SHADOWSOCKS |                1 | cyclic    | youtube.com::video_playback          | False    | 0.912694 | 0.981250 |
| SHADOWSOCKS |                1 | group     | bing.com::search_results_view        | True     | 0.974359 | 0.950000 |
| SHADOWSOCKS |                1 | group     | developer.mozilla.org::document_view | False    | 0.890691 | 1.000000 |
| SHADOWSOCKS |                1 | group     | github.com::repository_view          | False    | 0.994919 | 1.000000 |
| SHADOWSOCKS |                1 | group     | wikipedia.org::article_view          | True     | 0.832244 | 0.752083 |
| SHADOWSOCKS |                1 | group     | youtube.com::search_results_view     | False    | 0.909395 | 0.847917 |
| SHADOWSOCKS |                1 | group     | youtube.com::video_playback          | False    | 0.920977 | 0.983333 |
| SHADOWSOCKS |                1 | marginal  | bing.com::search_results_view        | True     | 0.969284 | 0.950000 |
| SHADOWSOCKS |                1 | marginal  | developer.mozilla.org::document_view | False    | 0.974687 | 0.997917 |
| SHADOWSOCKS |                1 | marginal  | github.com::repository_view          | False    | 0.988563 | 0.989583 |
| SHADOWSOCKS |                1 | marginal  | wikipedia.org::article_view          | True     | 0.954911 | 0.950000 |
| SHADOWSOCKS |                1 | marginal  | youtube.com::search_results_view     | False    | 0.940888 | 0.895833 |
| SHADOWSOCKS |                1 | marginal  | youtube.com::video_playback          | False    | 0.946322 | 0.991667 |
| SHADOWSOCKS |                1 | paired    | bing.com::search_results_view        | True     | 0.969284 | 0.950000 |
| SHADOWSOCKS |                1 | paired    | developer.mozilla.org::document_view | False    | 0.954729 | 1.000000 |
| SHADOWSOCKS |                1 | paired    | github.com::repository_view          | False    | 0.983482 | 0.989583 |
| SHADOWSOCKS |                1 | paired    | wikipedia.org::article_view          | True     | 0.942511 | 0.910417 |
| SHADOWSOCKS |                1 | paired    | youtube.com::search_results_view     | False    | 0.942805 | 0.908333 |
| SHADOWSOCKS |                1 | paired    | youtube.com::video_playback          | False    | 0.946615 | 0.981250 |
| SHADOWSOCKS |                1 | raw       | bing.com::search_results_view        | True     | 0.965362 | 0.933333 |
| SHADOWSOCKS |                1 | raw       | developer.mozilla.org::document_view | False    | 0.942608 | 0.918750 |
| SHADOWSOCKS |                1 | raw       | github.com::repository_view          | False    | 0.978246 | 0.983333 |
| SHADOWSOCKS |                1 | raw       | wikipedia.org::article_view          | True     | 0.951696 | 0.989583 |
| SHADOWSOCKS |                1 | raw       | youtube.com::search_results_view     | False    | 0.927894 | 0.941667 |
| SHADOWSOCKS |                1 | raw       | youtube.com::video_playback          | False    | 0.925350 | 0.927083 |
| SHADOWSOCKS |                1 | reference | bing.com::search_results_view        | True     | 0.974359 | 0.950000 |
| SHADOWSOCKS |                1 | reference | developer.mozilla.org::document_view | False    | 0.982724 | 1.000000 |
| SHADOWSOCKS |                1 | reference | github.com::repository_view          | False    | 0.996951 | 1.000000 |
| SHADOWSOCKS |                1 | reference | wikipedia.org::article_view          | True     | 0.960514 | 0.964583 |
| SHADOWSOCKS |                1 | reference | youtube.com::search_results_view     | False    | 0.926442 | 0.906250 |
| SHADOWSOCKS |                1 | reference | youtube.com::video_playback          | False    | 0.929726 | 0.950000 |
| SHADOWSOCKS |                2 | center    | bing.com::search_results_view        | False    | 0.965369 | 0.950000 |
| SHADOWSOCKS |                2 | center    | developer.mozilla.org::document_view | True     | 0.975235 | 0.979167 |
| SHADOWSOCKS |                2 | center    | github.com::repository_view          | False    | 0.987163 | 0.981250 |
| SHADOWSOCKS |                2 | center    | wikipedia.org::article_view          | False    | 0.953877 | 0.970833 |
| SHADOWSOCKS |                2 | center    | youtube.com::search_results_view     | False    | 0.939764 | 0.893750 |
| SHADOWSOCKS |                2 | center    | youtube.com::video_playback          | True     | 0.945354 | 0.991667 |
| SHADOWSOCKS |                2 | cyclic    | bing.com::search_results_view        | False    | 0.974359 | 0.950000 |
| SHADOWSOCKS |                2 | cyclic    | developer.mozilla.org::document_view | True     | 0.795610 | 0.706250 |
| SHADOWSOCKS |                2 | cyclic    | github.com::repository_view          | False    | 0.995831 | 0.995833 |
| SHADOWSOCKS |                2 | cyclic    | wikipedia.org::article_view          | False    | 0.840373 | 0.962500 |
| SHADOWSOCKS |                2 | cyclic    | youtube.com::search_results_view     | False    | 0.770926 | 0.683333 |
| SHADOWSOCKS |                2 | cyclic    | youtube.com::video_playback          | True     | 0.823805 | 0.920833 |
| SHADOWSOCKS |                2 | group     | bing.com::search_results_view        | False    | 0.969861 | 0.941667 |
| SHADOWSOCKS |                2 | group     | developer.mozilla.org::document_view | True     | 0.859268 | 0.810417 |
| SHADOWSOCKS |                2 | group     | github.com::repository_view          | False    | 0.996847 | 0.995833 |
| SHADOWSOCKS |                2 | group     | wikipedia.org::article_view          | False    | 0.870662 | 0.947917 |
| SHADOWSOCKS |                2 | group     | youtube.com::search_results_view     | False    | 0.773735 | 0.666667 |
| SHADOWSOCKS |                2 | group     | youtube.com::video_playback          | True     | 0.835222 | 0.954167 |
| SHADOWSOCKS |                2 | marginal  | bing.com::search_results_view        | False    | 0.974359 | 0.950000 |
| SHADOWSOCKS |                2 | marginal  | developer.mozilla.org::document_view | True     | 0.977830 | 0.995833 |
| SHADOWSOCKS |                2 | marginal  | github.com::repository_view          | False    | 0.996951 | 1.000000 |
| SHADOWSOCKS |                2 | marginal  | wikipedia.org::article_view          | False    | 0.957138 | 0.960417 |
| SHADOWSOCKS |                2 | marginal  | youtube.com::search_results_view     | False    | 0.943542 | 0.904167 |
| SHADOWSOCKS |                2 | marginal  | youtube.com::video_playback          | True     | 0.947926 | 0.987500 |
| SHADOWSOCKS |                2 | paired    | bing.com::search_results_view        | False    | 0.973344 | 0.950000 |
| SHADOWSOCKS |                2 | paired    | developer.mozilla.org::document_view | True     | 0.982305 | 0.983333 |
| SHADOWSOCKS |                2 | paired    | github.com::repository_view          | False    | 0.994867 | 0.997917 |
| SHADOWSOCKS |                2 | paired    | wikipedia.org::article_view          | False    | 0.962278 | 0.981250 |
| SHADOWSOCKS |                2 | paired    | youtube.com::search_results_view     | False    | 0.944550 | 0.906250 |
| SHADOWSOCKS |                2 | paired    | youtube.com::video_playback          | True     | 0.948988 | 0.987500 |
| SHADOWSOCKS |                2 | raw       | bing.com::search_results_view        | False    | 0.974359 | 0.950000 |
| SHADOWSOCKS |                2 | raw       | developer.mozilla.org::document_view | True     | 0.142074 | 0.079167 |
| SHADOWSOCKS |                2 | raw       | github.com::repository_view          | False    | 0.975640 | 0.960417 |
| SHADOWSOCKS |                2 | raw       | wikipedia.org::article_view          | False    | 0.675355 | 1.000000 |
| SHADOWSOCKS |                2 | raw       | youtube.com::search_results_view     | False    | 0.798780 | 0.972917 |
| SHADOWSOCKS |                2 | raw       | youtube.com::video_playback          | True     | 0.688218 | 0.562500 |
| SHADOWSOCKS |                2 | reference | bing.com::search_results_view        | False    | 0.970985 | 0.943750 |
| SHADOWSOCKS |                2 | reference | developer.mozilla.org::document_view | True     | 0.977832 | 0.997917 |
| SHADOWSOCKS |                2 | reference | github.com::repository_view          | False    | 0.998984 | 1.000000 |
| SHADOWSOCKS |                2 | reference | wikipedia.org::article_view          | False    | 0.956292 | 0.962500 |
| SHADOWSOCKS |                2 | reference | youtube.com::search_results_view     | False    | 0.921154 | 0.900000 |
| SHADOWSOCKS |                2 | reference | youtube.com::video_playback          | True     | 0.924593 | 0.945833 |
| VLESS       |                0 | center    | bing.com::search_results_view        | False    | 0.779643 | 0.827083 |
| VLESS       |                0 | center    | developer.mozilla.org::document_view | False    | 0.912938 | 0.872917 |
| VLESS       |                0 | center    | github.com::repository_view          | True     | 0.847091 | 0.762500 |
| VLESS       |                0 | center    | wikipedia.org::article_view          | False    | 0.904360 | 0.993750 |
| VLESS       |                0 | center    | youtube.com::search_results_view     | True     | 0.188761 | 0.120833 |
| VLESS       |                0 | center    | youtube.com::video_playback          | False    | 0.700664 | 0.950000 |
| VLESS       |                0 | cyclic    | bing.com::search_results_view        | False    | 0.837899 | 0.875000 |
| VLESS       |                0 | cyclic    | developer.mozilla.org::document_view | False    | 0.927629 | 0.893750 |
| VLESS       |                0 | cyclic    | github.com::repository_view          | True     | 0.899238 | 0.831250 |
| VLESS       |                0 | cyclic    | wikipedia.org::article_view          | False    | 0.919249 | 0.989583 |
| VLESS       |                0 | cyclic    | youtube.com::search_results_view     | True     | 0.324456 | 0.220833 |
| VLESS       |                0 | cyclic    | youtube.com::video_playback          | False    | 0.715383 | 0.943750 |
| VLESS       |                0 | group     | bing.com::search_results_view        | False    | 0.844930 | 0.877083 |
| VLESS       |                0 | group     | developer.mozilla.org::document_view | False    | 0.924009 | 0.900000 |
| VLESS       |                0 | group     | github.com::repository_view          | True     | 0.912541 | 0.850000 |
| VLESS       |                0 | group     | wikipedia.org::article_view          | False    | 0.925171 | 0.989583 |
| VLESS       |                0 | group     | youtube.com::search_results_view     | True     | 0.358757 | 0.254167 |
| VLESS       |                0 | group     | youtube.com::video_playback          | False    | 0.719236 | 0.929167 |
| VLESS       |                0 | marginal  | bing.com::search_results_view        | False    | 0.885982 | 0.868750 |
| VLESS       |                0 | marginal  | developer.mozilla.org::document_view | False    | 0.846224 | 0.810417 |
| VLESS       |                0 | marginal  | github.com::repository_view          | True     | 0.969402 | 0.945833 |
| VLESS       |                0 | marginal  | wikipedia.org::article_view          | False    | 0.874455 | 0.956250 |
| VLESS       |                0 | marginal  | youtube.com::search_results_view     | True     | 0.364741 | 0.254167 |
| VLESS       |                0 | marginal  | youtube.com::video_playback          | False    | 0.726171 | 0.943750 |
| VLESS       |                0 | paired    | bing.com::search_results_view        | False    | 0.863994 | 0.885417 |
| VLESS       |                0 | paired    | developer.mozilla.org::document_view | False    | 0.851640 | 0.800000 |
| VLESS       |                0 | paired    | github.com::repository_view          | True     | 0.920369 | 0.862500 |
| VLESS       |                0 | paired    | wikipedia.org::article_view          | False    | 0.878005 | 0.975000 |
| VLESS       |                0 | paired    | youtube.com::search_results_view     | True     | 0.415717 | 0.308333 |
| VLESS       |                0 | paired    | youtube.com::video_playback          | False    | 0.718202 | 0.900000 |
| VLESS       |                0 | raw       | bing.com::search_results_view        | False    | 0.823864 | 0.812500 |
| VLESS       |                0 | raw       | developer.mozilla.org::document_view | False    | 0.886176 | 0.852083 |
| VLESS       |                0 | raw       | github.com::repository_view          | True     | 0.952997 | 0.945833 |
| VLESS       |                0 | raw       | wikipedia.org::article_view          | False    | 0.902876 | 0.975000 |
| VLESS       |                0 | raw       | youtube.com::search_results_view     | True     | 0.025596 | 0.014583 |
| VLESS       |                0 | raw       | youtube.com::video_playback          | False    | 0.662591 | 0.950000 |
| VLESS       |                0 | reference | bing.com::search_results_view        | False    | 0.971098 | 0.947917 |
| VLESS       |                0 | reference | developer.mozilla.org::document_view | False    | 0.894924 | 0.860417 |
| VLESS       |                0 | reference | github.com::repository_view          | True     | 0.998984 | 1.000000 |
| VLESS       |                0 | reference | wikipedia.org::article_view          | False    | 0.910202 | 0.989583 |
| VLESS       |                0 | reference | youtube.com::search_results_view     | True     | 0.517819 | 0.416667 |
| VLESS       |                0 | reference | youtube.com::video_playback          | False    | 0.698164 | 0.820833 |
| VLESS       |                1 | center    | bing.com::search_results_view        | True     | 0.255183 | 0.150000 |
| VLESS       |                1 | center    | developer.mozilla.org::document_view | False    | 0.671547 | 0.702083 |
| VLESS       |                1 | center    | github.com::repository_view          | False    | 0.920878 | 0.997917 |
| VLESS       |                1 | center    | wikipedia.org::article_view          | True     | 0.838159 | 1.000000 |
| VLESS       |                1 | center    | youtube.com::search_results_view     | False    | 0.495805 | 0.445833 |
| VLESS       |                1 | center    | youtube.com::video_playback          | False    | 0.664565 | 0.802083 |
| VLESS       |                1 | cyclic    | bing.com::search_results_view        | True     | 0.542272 | 0.383333 |
| VLESS       |                1 | cyclic    | developer.mozilla.org::document_view | False    | 0.829663 | 0.950000 |
| VLESS       |                1 | cyclic    | github.com::repository_view          | False    | 0.877670 | 0.991667 |
| VLESS       |                1 | cyclic    | wikipedia.org::article_view          | True     | 0.805966 | 0.783333 |
| VLESS       |                1 | cyclic    | youtube.com::search_results_view     | False    | 0.407618 | 0.322917 |
| VLESS       |                1 | cyclic    | youtube.com::video_playback          | False    | 0.694254 | 0.881250 |
| VLESS       |                1 | group     | bing.com::search_results_view        | True     | 0.607265 | 0.450000 |
| VLESS       |                1 | group     | developer.mozilla.org::document_view | False    | 0.860668 | 0.952083 |
| VLESS       |                1 | group     | github.com::repository_view          | False    | 0.907600 | 0.997917 |
| VLESS       |                1 | group     | wikipedia.org::article_view          | True     | 0.863125 | 0.872917 |
| VLESS       |                1 | group     | youtube.com::search_results_view     | False    | 0.411008 | 0.322917 |
| VLESS       |                1 | group     | youtube.com::video_playback          | False    | 0.702563 | 0.893750 |
| VLESS       |                1 | marginal  | bing.com::search_results_view        | True     | 0.521348 | 0.360417 |
| VLESS       |                1 | marginal  | developer.mozilla.org::document_view | False    | 0.718746 | 0.762500 |
| VLESS       |                1 | marginal  | github.com::repository_view          | False    | 0.945523 | 1.000000 |
| VLESS       |                1 | marginal  | wikipedia.org::article_view          | True     | 0.867815 | 1.000000 |
| VLESS       |                1 | marginal  | youtube.com::search_results_view     | False    | 0.499193 | 0.431250 |
| VLESS       |                1 | marginal  | youtube.com::video_playback          | False    | 0.708094 | 0.843750 |
| VLESS       |                1 | paired    | bing.com::search_results_view        | True     | 0.766879 | 0.627083 |
| VLESS       |                1 | paired    | developer.mozilla.org::document_view | False    | 0.859604 | 0.920833 |
| VLESS       |                1 | paired    | github.com::repository_view          | False    | 0.982043 | 1.000000 |
| VLESS       |                1 | paired    | wikipedia.org::article_view          | True     | 0.922066 | 0.983333 |
| VLESS       |                1 | paired    | youtube.com::search_results_view     | False    | 0.517592 | 0.427083 |
| VLESS       |                1 | paired    | youtube.com::video_playback          | False    | 0.731156 | 0.883333 |
| VLESS       |                1 | raw       | bing.com::search_results_view        | True     | 0.177270 | 0.097917 |
| VLESS       |                1 | raw       | developer.mozilla.org::document_view | False    | 0.776172 | 0.902083 |
| VLESS       |                1 | raw       | github.com::repository_view          | False    | 0.877407 | 1.000000 |
| VLESS       |                1 | raw       | wikipedia.org::article_view          | True     | 0.859791 | 0.866667 |
| VLESS       |                1 | raw       | youtube.com::search_results_view     | False    | 0.455830 | 0.450000 |
| VLESS       |                1 | raw       | youtube.com::video_playback          | False    | 0.572308 | 0.727083 |
| VLESS       |                1 | reference | bing.com::search_results_view        | True     | 0.946677 | 0.925000 |
| VLESS       |                1 | reference | developer.mozilla.org::document_view | False    | 0.940456 | 0.902083 |
| VLESS       |                1 | reference | github.com::repository_view          | False    | 0.992682 | 0.991667 |
| VLESS       |                1 | reference | wikipedia.org::article_view          | True     | 0.916838 | 1.000000 |
| VLESS       |                1 | reference | youtube.com::search_results_view     | False    | 0.515452 | 0.412500 |
| VLESS       |                1 | reference | youtube.com::video_playback          | False    | 0.699341 | 0.822917 |
| VLESS       |                2 | center    | bing.com::search_results_view        | False    | 0.906272 | 0.833333 |
| VLESS       |                2 | center    | developer.mozilla.org::document_view | True     | 0.771040 | 0.639583 |
| VLESS       |                2 | center    | github.com::repository_view          | False    | 0.993850 | 0.997917 |
| VLESS       |                2 | center    | wikipedia.org::article_view          | False    | 0.813383 | 1.000000 |
| VLESS       |                2 | center    | youtube.com::search_results_view     | False    | 0.557133 | 0.708333 |
| VLESS       |                2 | center    | youtube.com::video_playback          | True     | 0.322521 | 0.258333 |
| VLESS       |                2 | cyclic    | bing.com::search_results_view        | False    | 0.908622 | 0.862500 |
| VLESS       |                2 | cyclic    | developer.mozilla.org::document_view | True     | 0.626194 | 0.477083 |
| VLESS       |                2 | cyclic    | github.com::repository_view          | False    | 0.989824 | 0.993750 |
| VLESS       |                2 | cyclic    | wikipedia.org::article_view          | False    | 0.774249 | 1.000000 |
| VLESS       |                2 | cyclic    | youtube.com::search_results_view     | False    | 0.502404 | 0.612500 |
| VLESS       |                2 | cyclic    | youtube.com::video_playback          | True     | 0.299151 | 0.264583 |
| VLESS       |                2 | group     | bing.com::search_results_view        | False    | 0.919288 | 0.875000 |
| VLESS       |                2 | group     | developer.mozilla.org::document_view | True     | 0.717782 | 0.577083 |
| VLESS       |                2 | group     | github.com::repository_view          | False    | 0.992782 | 0.995833 |
| VLESS       |                2 | group     | wikipedia.org::article_view          | False    | 0.803206 | 1.000000 |
| VLESS       |                2 | group     | youtube.com::search_results_view     | False    | 0.498593 | 0.545833 |
| VLESS       |                2 | group     | youtube.com::video_playback          | True     | 0.452791 | 0.435417 |
| VLESS       |                2 | marginal  | bing.com::search_results_view        | False    | 0.934849 | 0.885417 |
| VLESS       |                2 | marginal  | developer.mozilla.org::document_view | True     | 0.809825 | 0.712500 |
| VLESS       |                2 | marginal  | github.com::repository_view          | False    | 1.000000 | 1.000000 |
| VLESS       |                2 | marginal  | wikipedia.org::article_view          | False    | 0.840216 | 0.983333 |
| VLESS       |                2 | marginal  | youtube.com::search_results_view     | False    | 0.534893 | 0.591667 |
| VLESS       |                2 | marginal  | youtube.com::video_playback          | True     | 0.490334 | 0.443750 |
| VLESS       |                2 | paired    | bing.com::search_results_view        | False    | 0.942715 | 0.897917 |
| VLESS       |                2 | paired    | developer.mozilla.org::document_view | True     | 0.782317 | 0.670833 |
| VLESS       |                2 | paired    | github.com::repository_view          | False    | 1.000000 | 1.000000 |
| VLESS       |                2 | paired    | wikipedia.org::article_view          | False    | 0.836848 | 0.997917 |
| VLESS       |                2 | paired    | youtube.com::search_results_view     | False    | 0.532048 | 0.464583 |
| VLESS       |                2 | paired    | youtube.com::video_playback          | True     | 0.679644 | 0.768750 |
| VLESS       |                2 | raw       | bing.com::search_results_view        | False    | 0.867309 | 0.829167 |
| VLESS       |                2 | raw       | developer.mozilla.org::document_view | True     | 0.658509 | 0.500000 |
| VLESS       |                2 | raw       | github.com::repository_view          | False    | 0.987950 | 1.000000 |
| VLESS       |                2 | raw       | wikipedia.org::article_view          | False    | 0.794509 | 1.000000 |
| VLESS       |                2 | raw       | youtube.com::search_results_view     | False    | 0.610148 | 0.920833 |
| VLESS       |                2 | raw       | youtube.com::video_playback          | True     | 0.000000 | 0.000000 |
| VLESS       |                2 | reference | bing.com::search_results_view        | False    | 0.970189 | 0.947917 |
| VLESS       |                2 | reference | developer.mozilla.org::document_view | True     | 0.854858 | 0.797917 |
| VLESS       |                2 | reference | github.com::repository_view          | False    | 1.000000 | 1.000000 |
| VLESS       |                2 | reference | wikipedia.org::article_view          | False    | 0.868883 | 0.968750 |
| VLESS       |                2 | reference | youtube.com::search_results_view     | False    | 0.529625 | 0.433333 |
| VLESS       |                2 | reference | youtube.com::video_playback          | True     | 0.695988 | 0.808333 |

