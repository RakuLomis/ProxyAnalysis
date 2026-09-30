# 训练侧支持与谱系审计

| protocol    |   business_group | kind   | business_role   |   queries |   mean_outside_dimensions |   mean_nearest_distance |
|:------------|-----------------:|:-------|:----------------|----------:|--------------------------:|------------------------:|
| SHADOWSOCKS |                0 | group  | cal             |      1600 |                  0.653125 |                0.525028 |
| SHADOWSOCKS |                0 | group  | new             |      1280 |                  0.141406 |                1.470413 |
| SHADOWSOCKS |                0 | paired | cal             |      1600 |                  0.653125 |                0.525028 |
| SHADOWSOCKS |                0 | paired | new             |      1280 |                  0.141406 |                1.470413 |
| SHADOWSOCKS |                1 | group  | cal             |      1600 |                  0.765625 |                0.663005 |
| SHADOWSOCKS |                1 | group  | new             |      1280 |                  3.186719 |                2.278545 |
| SHADOWSOCKS |                1 | paired | cal             |      1600 |                  0.765625 |                0.663005 |
| SHADOWSOCKS |                1 | paired | new             |      1280 |                  3.186719 |                2.278545 |
| SHADOWSOCKS |                2 | group  | cal             |      1600 |                  0.640000 |                0.753174 |
| SHADOWSOCKS |                2 | group  | new             |      1280 |                  0.936719 |                1.026980 |
| SHADOWSOCKS |                2 | paired | cal             |      1600 |                  0.640000 |                0.753174 |
| SHADOWSOCKS |                2 | paired | new             |      1280 |                  0.936719 |                1.026980 |
| VLESS       |                0 | group  | cal             |      1600 |                  0.588125 |                0.926724 |
| VLESS       |                0 | group  | new             |      1280 |                  1.253906 |                1.779595 |
| VLESS       |                0 | paired | cal             |      1600 |                  0.588125 |                0.926724 |
| VLESS       |                0 | paired | new             |      1280 |                  1.253906 |                1.779595 |
| VLESS       |                1 | group  | cal             |      1600 |                  0.631875 |                1.190514 |
| VLESS       |                1 | group  | new             |      1280 |                  1.985156 |                3.164793 |
| VLESS       |                1 | paired | cal             |      1600 |                  0.631875 |                1.190514 |
| VLESS       |                1 | paired | new             |      1280 |                  1.985156 |                3.164793 |
| VLESS       |                2 | group  | cal             |      1600 |                  0.533750 |                1.312560 |
| VLESS       |                2 | group  | new             |      1280 |                  0.185156 |                1.161205 |
| VLESS       |                2 | paired | cal             |      1600 |                  0.533750 |                1.312560 |
| VLESS       |                2 | paired | new             |      1280 |                  0.185156 |                1.161205 |

以上是C坐标中的U_pre描述，不使用U_post，不据此筛选或调参。所有donor、LOCO、组级笛卡尔积、24/96行权重与合法摘要核对通过。原始冻结输入哈希未改变。LOCO误差保存在loco-errors.parquet；X6组合误差不等于真实对应恢复误差，不与X4直接当同一目标比较。
