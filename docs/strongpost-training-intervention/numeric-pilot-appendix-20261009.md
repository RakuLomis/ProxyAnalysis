# StrongPost数值先导逐项附录

全部角色和两个映射均保留。下表CE来自源内伪目标，不是正式目标H；检查通过不表示业务增益成立。

| target | calibration | group | arm | eta | t | direction_norm | stationarity_ratio | parameter_relative_error | CE_derivative_predicted | CE_derivative_finite | CE_derivative_error | source_CE_error | gate_parameter_direction | gate_heldout_CE_derivative | gate_source_CE_derivative | passed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| shadowsocks | trojan | G0 | P | 100 | 4 | 1513.83 | 0.00030638 | 0.969397 | -449.28 | -4.05538 | 445.225 | 0.149185 | False | False | False | False |
| shadowsocks | trojan | G0 | G | 100 | 4 | 1511.3 | 0.000306893 | 0.969581 | -464.47 | -4.28977 | 460.18 | 0.168184 | False | False | False | False |
| shadowsocks | trojan | G1 | P | 0.1 | 0.25 | 380.968 | 0.00613114 | 0.554594 | -12.513 | -17.6107 | 5.09774 | 0.0526843 | False | False | False | False |
| shadowsocks | trojan | G1 | G | 0.1 | 0.25 | 354.495 | 0.00658899 | 0.535969 | 7.46151 | -18.012 | 25.4735 | 0.00445479 | False | False | True | False |
| shadowsocks | trojan | G2 | P | 1 | 0 | 967.893 | 0.00314571 | 0.855025 | 87.4768 | 52.8835 | 34.5932 | 0.214912 | False | False | False | False |
| shadowsocks | trojan | G2 | G | 1 | 0 | 892.706 | 0.00341065 | 0.845313 | 92.9873 | 61.8092 | 31.1781 | 0.146061 | False | False | False | False |
| vless | shadowsocks | G0 | P | 0.1 | 4 | 70.7578 | 0.00772579 | 0.221527 | -4.53687 | -3.22247 | 1.3144 | 0.000767301 | False | False | True | False |
| vless | shadowsocks | G0 | G | 0.1 | 4 | 70.0755 | 0.00780102 | 0.217862 | -5.65936 | -4.45235 | 1.20701 | 0.00433702 | False | False | True | False |
| vless | shadowsocks | G1 | P | 0.1 | 4 | 55.4158 | 0.0107816 | 0.173888 | -5.72009 | -4.46725 | 1.25284 | 0.0135792 | False | False | False | False |
| vless | shadowsocks | G1 | G | 0.1 | 4 | 61.2664 | 0.00975203 | 0.146286 | -1.67243 | -0.887673 | 0.784759 | 0.0135606 | False | False | False | False |
| vless | shadowsocks | G2 | P | 0.1 | 1 | 194.437 | 0.00649388 | 0.374812 | -16.5729 | -12.8438 | 3.72913 | 0.0602099 | False | False | False | False |
| vless | shadowsocks | G2 | G | 0.1 | 1 | 194.813 | 0.00648133 | 0.379199 | -9.30599 | -10.1103 | 0.804323 | 0.0410638 | False | True | False | False |
| trojan | shadowsocks | G0 | P | 0.1 | 4 | 73.9863 | 0.00582209 | 0.29422 | -6.53136 | -4.83271 | 1.69865 | 0.00596973 | False | False | True | False |
| trojan | shadowsocks | G0 | G | 0.1 | 4 | 70.1836 | 0.00613755 | 0.31434 | -5.83271 | -4.47297 | 1.35974 | 0.0117955 | False | False | True | False |
| trojan | shadowsocks | G1 | P | 0.1 | 4 | 62.3525 | 0.0102282 | 0.177592 | -2.95476 | -2.81838 | 0.13638 | 0.00447212 | False | True | True | False |
| trojan | shadowsocks | G1 | G | 0.1 | 4 | 61.404 | 0.0103862 | 0.0868783 | -0.260048 | 0.1103 | 0.370348 | 0.00724894 | True | False | True | False |
| trojan | shadowsocks | G2 | P | 0.1 | 4 | 118.057 | 0.00483398 | 0.438875 | -10.2004 | -8.18078 | 2.01963 | 0.00705333 | False | False | True | False |
| trojan | shadowsocks | G2 | G | 0.1 | 4 | 117.35 | 0.00486307 | 0.432863 | -6.03567 | -5.39598 | 0.639689 | 0.000459345 | False | False | True | False |
| vmess | shadowsocks | G0 | P | 10 | 4 | 189.557 | 0.00292315 | 0.534267 | -17.6391 | -8.04013 | 9.59895 | 0.101191 | False | False | False | False |
| vmess | shadowsocks | G0 | G | 10 | 4 | 190.213 | 0.00291307 | 0.565116 | -14.2449 | -6.28033 | 7.96455 | 0.119602 | False | False | False | False |
| vmess | shadowsocks | G1 | P | 0.1 | 1 | 233.209 | 0.00876356 | 0.49008 | -6.85542 | -8.1049 | 1.24948 | 0.0323707 | False | False | False | False |
| vmess | shadowsocks | G1 | G | 0.1 | 1 | 225.774 | 0.00905215 | 0.406395 | -8.9287 | -5.52165 | 3.40705 | 0.0496611 | False | False | False | False |
| vmess | shadowsocks | G2 | P | 0.1 | 4 | 64.1931 | 0.00881707 | 0.299657 | -9.7984 | -6.39837 | 3.40003 | 0.0059528 | False | False | True | False |
| vmess | shadowsocks | G2 | G | 0.1 | 4 | 63.7267 | 0.00888161 | 0.238756 | -5.47904 | -4.15139 | 1.32765 | 0.00446577 | False | False | True | False |

## Hessian逐角色核验

| role_id | dimension | gradient_inf | stationarity_displacement_norm | linear_system_residual | hessian_symmetry_residual | hessian_autograd_residual | gradient_autograd_residual | eigen_min | eigen_max | condition_number | seconds | cuda_peak_MiB | device | dtype | jitter | new_bias_regularization |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| main/f0/shadowsocks/G0/i1/trojan | 581 | 7.52109e-06 | 0.00463807 | 2.79316e-15 | 1.04083e-17 | 4.78784e-16 | 5.75711e-17 | 0.00211288 | 0.844644 | 399.76 | 0.51128 | 97.9062 | cuda:0 | float64 | 0 | 0 |
| main/f0/shadowsocks/G1/i1/trojan | 581 | 8.59186e-06 | 0.0233576 | 1.83187e-15 | 3.46945e-18 | 8.9425e-16 | 7.86318e-17 | 0.000714809 | 0.423822 | 592.916 | 0.0413708 | 104.902 | cuda:0 | float64 | 0 | 0 |
| main/f0/shadowsocks/G2/i1/trojan | 581 | 9.59577e-06 | 0.0304471 | 3.68802e-15 | 6.93889e-18 | 7.50051e-16 | 6.1481e-17 | 0.00046311 | 0.735911 | 1589.06 | 0.0456362 | 105.172 | cuda:0 | float64 | 0 | 0 |
| main/f0/vless/G0/i1/shadowsocks | 581 | 8.46881e-06 | 0.0054666 | 1.60288e-15 | 2.77556e-17 | 1.8735e-16 | 2.90566e-17 | 0.00168606 | 4.37449 | 2594.5 | 0.0533602 | 105.172 | cuda:0 | float64 | 0 | 0 |
| main/f0/vless/G1/i1/shadowsocks | 581 | 8.43604e-06 | 0.00597472 | 2.84495e-15 | 2.77556e-17 | 3.57353e-16 | 3.16587e-17 | 0.00240084 | 2.63643 | 1098.13 | 0.121011 | 110.559 | cuda:0 | float64 | 0 | 0 |
| main/f0/vless/G2/i1/shadowsocks | 581 | 8.36666e-06 | 0.0126265 | 1.92901e-15 | 2.08167e-17 | 8.04912e-16 | 1.17853e-16 | 0.00088052 | 2.73051 | 3101.02 | 0.0479495 | 110.559 | cuda:0 | float64 | 0 | 0 |
| main/f0/trojan/G0/i1/shadowsocks | 581 | 7.69957e-06 | 0.00430755 | 1.52656e-15 | 2.77556e-17 | 5.0307e-16 | 6.03901e-17 | 0.0023571 | 3.97312 | 1685.6 | 0.0510463 | 111.327 | cuda:0 | float64 | 0 | 0 |
| main/f0/trojan/G1/i1/shadowsocks | 581 | 9.61806e-06 | 0.00637756 | 1.47105e-15 | 1.38778e-17 | 3.40006e-16 | 3.98986e-17 | 0.00273064 | 2.51167 | 919.812 | 0.0524466 | 111.327 | cuda:0 | float64 | 0 | 0 |
| main/f0/trojan/G2/i1/shadowsocks | 581 | 9.39371e-06 | 0.00570683 | 2.41474e-15 | 1.38778e-17 | 2.77556e-16 | 3.55618e-17 | 0.00247262 | 3.16691 | 1280.79 | 0.0511954 | 112.084 | cuda:0 | float64 | 0 | 0 |
| main/f0/vmess/G0/i1/shadowsocks | 581 | 9.88335e-06 | 0.00554104 | 4.2466e-15 | 2.77556e-17 | 4.89192e-16 | 7.54605e-17 | 0.00139053 | 3.47912 | 2502.02 | 0.0464376 | 112.084 | cuda:0 | float64 | 0 | 0 |
| main/f0/vmess/G1/i1/shadowsocks | 581 | 9.66318e-06 | 0.0204374 | 3.4972e-15 | 1.38778e-17 | 3.29597e-16 | 4.98733e-17 | 0.000634118 | 1.33552 | 2106.11 | 0.049654 | 112.67 | cuda:0 | float64 | 0 | 0 |
| main/f0/vmess/G2/i1/shadowsocks | 581 | 7.89539e-06 | 0.00565995 | 2.35922e-15 | 1.38778e-17 | 5.58581e-16 | 3.74592e-17 | 0.00136024 | 2.79096 | 2051.81 | 0.0561711 | 112.981 | cuda:0 | float64 | 0 | 0 |
