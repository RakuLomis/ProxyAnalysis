# CB3–CB4 小预算生成合法性

120个scenario完成，生成器仅从其C拟合；U_pre只查询，不开放U_post或H_pre。生成、重抽及整数规则保持冻结。

| protocol    |   k | arm   |   source_views |   first_invalid_rate |   fallback_rate |   mean_attempts | passed   |
|:------------|----:|:------|---------------:|---------------------:|----------------:|----------------:|:---------|
| SHADOWSOCKS |   1 | B2    |          34560 |             0.000000 |        0.000000 |        1.000000 | True     |
| SHADOWSOCKS |   1 | B3    |          34560 |             0.001881 |        0.000000 |        1.001968 | True     |
| SHADOWSOCKS |   1 | B4    |          34560 |             0.001678 |        0.000000 |        1.001736 | True     |
| SHADOWSOCKS |   1 | B5    |          34560 |             0.064554 |        0.000000 |        1.078906 | True     |
| SHADOWSOCKS |   2 | B2    |          23040 |             0.000000 |        0.000000 |        1.000000 | True     |
| SHADOWSOCKS |   2 | B3    |          23040 |             0.002170 |        0.000000 |        1.002300 | True     |
| SHADOWSOCKS |   2 | B4    |          23040 |             0.000087 |        0.000000 |        1.000087 | True     |
| SHADOWSOCKS |   2 | B5    |          23040 |             0.058724 |        0.000000 |        1.068924 | True     |
| SHADOWSOCKS |   3 | B2    |          11520 |             0.000000 |        0.000000 |        1.000000 | True     |
| SHADOWSOCKS |   3 | B3    |          11520 |             0.001910 |        0.000000 |        1.001997 | True     |
| SHADOWSOCKS |   3 | B4    |          11520 |             0.000000 |        0.000000 |        1.000000 | True     |
| SHADOWSOCKS |   3 | B5    |          11520 |             0.043229 |        0.000000 |        1.047656 | True     |
| VLESS       |   1 | B2    |          34560 |             0.000000 |        0.000000 |        1.000000 | True     |
| VLESS       |   1 | B3    |          34560 |             0.084491 |        0.000000 |        1.104051 | True     |
| VLESS       |   1 | B4    |          34560 |             0.060185 |        0.000000 |        1.069734 | True     |
| VLESS       |   1 | B5    |          34560 |             0.065567 |        0.000000 |        1.073322 | True     |
| VLESS       |   2 | B2    |          23040 |             0.000000 |        0.000000 |        1.000000 | True     |
| VLESS       |   2 | B3    |          23040 |             0.086762 |        0.000000 |        1.105729 | True     |
| VLESS       |   2 | B4    |          23040 |             0.055208 |        0.000000 |        1.063585 | True     |
| VLESS       |   2 | B5    |          23040 |             0.065104 |        0.000000 |        1.072743 | True     |
| VLESS       |   3 | B2    |          11520 |             0.000000 |        0.000000 |        1.000000 | True     |
| VLESS       |   3 | B3    |          11520 |             0.081337 |        0.000000 |        1.099653 | True     |
| VLESS       |   3 | B4    |          11520 |             0.036458 |        0.000000 |        1.042708 | True     |
| VLESS       |   3 | B5    |          11520 |             0.043316 |        0.000000 |        1.048264 | True     |

门限在读取结果前固定：每部署×预算×臂首次非法≤10%，fallback≤1%；不按预算合并。

| protocol    |   k | arm   | first_reason           |   source_views |
|:------------|----:|:------|:-----------------------|---------------:|
| SHADOWSOCKS |   1 | B3    | direction_imbalance    |             65 |
| SHADOWSOCKS |   1 | B4    | R_E_U_order            |              6 |
| SHADOWSOCKS |   1 | B4    | direction_imbalance    |             52 |
| SHADOWSOCKS |   1 | B5    | R_E_U_order            |            257 |
| SHADOWSOCKS |   1 | B5    | direction_imbalance    |           1810 |
| SHADOWSOCKS |   1 | B5    | runs_below_connections |            164 |
| SHADOWSOCKS |   2 | B3    | direction_imbalance    |             50 |
| SHADOWSOCKS |   2 | B4    | R_E_U_order            |              2 |
| SHADOWSOCKS |   2 | B5    | R_E_U_order            |            228 |
| SHADOWSOCKS |   2 | B5    | direction_imbalance    |            931 |
| SHADOWSOCKS |   2 | B5    | runs_below_connections |            194 |
| SHADOWSOCKS |   3 | B3    | direction_imbalance    |             22 |
| SHADOWSOCKS |   3 | B5    | R_E_U_order            |             53 |
| SHADOWSOCKS |   3 | B5    | direction_imbalance    |            411 |
| SHADOWSOCKS |   3 | B5    | runs_below_connections |             34 |
| VLESS       |   1 | B3    | R_E_U_order            |           2769 |
| VLESS       |   1 | B3    | direction_imbalance    |            151 |
| VLESS       |   1 | B4    | R_E_U_order            |           2005 |
| VLESS       |   1 | B4    | direction_imbalance    |             75 |
| VLESS       |   1 | B5    | R_E_U_order            |           2259 |
| VLESS       |   1 | B5    | direction_imbalance    |              7 |
| VLESS       |   2 | B3    | R_E_U_order            |           1907 |
| VLESS       |   2 | B3    | direction_imbalance    |             92 |
| VLESS       |   2 | B4    | R_E_U_order            |           1268 |
| VLESS       |   2 | B4    | direction_imbalance    |              4 |
| VLESS       |   2 | B5    | R_E_U_order            |           1494 |
| VLESS       |   2 | B5    | direction_imbalance    |              6 |
| VLESS       |   3 | B3    | R_E_U_order            |            879 |
| VLESS       |   3 | B3    | direction_imbalance    |             58 |
| VLESS       |   3 | B4    | R_E_U_order            |            420 |
| VLESS       |   3 | B5    | R_E_U_order            |            498 |
| VLESS       |   3 | B5    | direction_imbalance    |              1 |

全部通过，允许正式分类。

视图计数不是独立内容数；同一原内容会出现在不同外折/轮换/seed中。必要摘要约束通过不代表协议或语义保真。
