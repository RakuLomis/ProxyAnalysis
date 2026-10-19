# RA1-NR1同目标数值先导详细报告

日期：2026-10-18。完整业务矩阵未重启；本报告没有新F1/CE测试成绩。

## 1. 结项状态

状态：`numeric_pilot_passed_waiting_for_user`。42端点中已接受42个，开始45次物理拟合，完整结果日志45份。

只有全部42端点、旧失败复现、前缀等价、两个确定性重复和独立审核通过，才记为数值先导通过。已运行子集不代表完整先导。

## 2. 问题、目标与唯一修订

原RA1在f0/VLESS/G0的RawPre-U100于2000次迭代停止，原梯度1.1157400392713588e-5，未满足1e-5。NR1只把资源配套提高到4000迭代/20000函数评价，沿用原加权CE+.0005*(1+t)||W||²、bias不正则、共同post尺度、96→6模型、固定视图和零初始化。

CUDA float64、Cholesky、原梯度感知LBFGS、strong_wolfe、history_size=100、lr=1、内部容差与严格预算边界保持。没有改模型、rho、t/eta、数值精度门或数据权限；没有Newton、warm start、裁剪或额外归一化。

## 3. 固定范围与权限

42不同端点：四部署×四来源×U50/U100共32；VLESS/G0四来源的SYM50/CPR100共8；VLESS/G1、G2的RawPre-U100共2。另有原预算预期停止复现1次、两个确定性重复，共45尝试上限。全部训练使用原合法源库与目标C，不是源内业务显著性验证。

不读取query、H-post、H-pre、实际目标U训练值、标签评分或历史H概率；本轮纯训练求解诊断。

## 4. 旧停止与第2000步前缀

旧预算复现：{"attempt": 1, "gradient_vector_error": 0.0, "new_gradient": 1.1157400392708926e-05, "objective_error": 0.0, "original_gradient": 1.1157400392708926e-05, "original_objective": 0.24018086912244446, "parameter_max_error": 0.0, "passed": true}

新轨迹第2000步前缀：{"attempt": 2, "gradient_vector_error": 0.0, "new_gradient": 1.1157400392708926e-05, "objective_error": 0.0, "original_gradient": 1.1157400392708926e-05, "original_objective": 0.24018086912244446, "parameter_max_error": 0.0, "passed": true}

前缀是克隆接受点参数/选中梯度的只读观测，不向优化器追加closure、改参数或历史。目标和梯度独立重放在副本上完成。旧失败不回写为成功。

## 5. 全部已运行拟合明细

| attempt | kind | policy | role | accepted | iterations | evaluations | gradient | J | seconds |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | old-reproduction | RawPre__m050__UPR | main/f0/vless/G0/outer | False | 2000 | 3845 | 1.115740039e-05 | 0.240180869122444 | 65.550 |
| 2 | NR1-hard-case | RawPre__m050__UPR | main/f0/vless/G0/outer | True | 2974 | 5793 | 9.999096278e-06 | 0.240180868251783 | 97.439 |
| 3 | NR1-case | G__m025__UPR | main/f0/shadowsocks/G0/outer | True | 50 | 56 | 8.103206547e-06 | 0.281465059046833 | 0.561 |
| 4 | NR1-case | G__m050__UPR | main/f0/shadowsocks/G0/outer | True | 61 | 64 | 9.711043139e-06 | 0.260833869767 | 0.745 |
| 5 | NR1-case | P__m025__UPR | main/f0/shadowsocks/G0/outer | True | 50 | 55 | 7.884430697e-06 | 0.281471123563447 | 0.553 |
| 6 | NR1-case | P__m050__UPR | main/f0/shadowsocks/G0/outer | True | 61 | 64 | 7.711944153e-06 | 0.26089037612243 | 0.746 |
| 7 | NR1-case | RawPost__m025__UPR | main/f0/shadowsocks/G0/outer | True | 43 | 47 | 9.650770199e-06 | 0.271691583254346 | 0.428 |
| 8 | NR1-case | RawPost__m050__UPR | main/f0/shadowsocks/G0/outer | True | 57 | 61 | 9.334787382e-06 | 0.25149138636239 | 0.666 |
| 9 | NR1-case | RawPre__m025__UPR | main/f0/shadowsocks/G0/outer | True | 215 | 224 | 8.110963287e-06 | 0.27146409698032 | 5.070 |
| 10 | NR1-case | RawPre__m050__UPR | main/f0/shadowsocks/G0/outer | True | 319 | 329 | 8.339607892e-06 | 0.24596899879659 | 8.312 |
| 11 | NR1-case | G__m025__UPR | main/f0/trojan/G0/outer | True | 36 | 39 | 9.892854019e-06 | 0.309671094511793 | 0.348 |
| 12 | NR1-case | G__m050__UPR | main/f0/trojan/G0/outer | True | 37 | 39 | 8.764507768e-06 | 0.310277476152548 | 0.344 |
| 13 | NR1-case | P__m025__UPR | main/f0/trojan/G0/outer | True | 39 | 43 | 9.027339772e-06 | 0.308582191955978 | 0.382 |
| 14 | NR1-case | P__m050__UPR | main/f0/trojan/G0/outer | True | 41 | 45 | 7.143036972e-06 | 0.307732439790458 | 0.412 |
| 15 | NR1-case | RawPost__m025__UPR | main/f0/trojan/G0/outer | True | 38 | 42 | 7.139418574e-06 | 0.280161856377942 | 0.370 |
| 16 | NR1-case | RawPost__m050__UPR | main/f0/trojan/G0/outer | True | 38 | 41 | 9.853403914e-06 | 0.272468844696319 | 0.357 |
| 17 | NR1-case | RawPre__m025__UPR | main/f0/trojan/G0/outer | True | 201 | 210 | 5.098203173e-06 | 0.278696069160184 | 4.779 |
| 18 | NR1-case | RawPre__m050__UPR | main/f0/trojan/G0/outer | True | 259 | 270 | 9.063952593e-06 | 0.262208061323768 | 6.580 |
| 19 | NR1-case | G__m025__UPR | main/f0/vless/G0/outer | True | 35 | 39 | 8.496474445e-06 | 0.278904069435975 | 0.338 |
| 20 | NR1-case | G__m050__CPR | main/f0/vless/G0/outer | True | 39 | 42 | 9.996941519e-06 | 0.2432606521739 | 0.387 |
| 21 | NR1-case | G__m050__SYM | main/f0/vless/G0/outer | True | 35 | 39 | 9.456222548e-06 | 0.283032703933026 | 0.339 |
| 22 | NR1-case | G__m050__UPR | main/f0/vless/G0/outer | True | 37 | 41 | 9.607400906e-06 | 0.276731164684627 | 0.357 |
| 23 | NR1-case | P__m025__UPR | main/f0/vless/G0/outer | True | 36 | 39 | 9.491774349e-06 | 0.26936724800084 | 0.349 |
| 24 | NR1-case | P__m050__CPR | main/f0/vless/G0/outer | True | 42 | 45 | 7.212872042e-06 | 0.249594069939176 | 0.433 |
| 25 | NR1-case | P__m050__SYM | main/f0/vless/G0/outer | True | 36 | 39 | 8.691784795e-06 | 0.275828820172835 | 0.337 |
| 26 | NR1-case | P__m050__UPR | main/f0/vless/G0/outer | True | 37 | 40 | 9.200309161e-06 | 0.263816518576883 | 0.349 |
| 27 | NR1-case | RawPost__m025__UPR | main/f0/vless/G0/outer | True | 39 | 42 | 9.285506360e-06 | 0.256080027158352 | 0.378 |
| 28 | NR1-case | RawPost__m050__CPR | main/f0/vless/G0/outer | True | 38 | 41 | 9.059226879e-06 | 0.248949808052704 | 0.356 |
| 29 | NR1-case | RawPost__m050__SYM | main/f0/vless/G0/outer | True | 39 | 41 | 8.872641312e-06 | 0.253063157398145 | 0.365 |
| 30 | NR1-case | RawPost__m050__UPR | main/f0/vless/G0/outer | True | 40 | 43 | 8.843720700e-06 | 0.246743656879985 | 0.374 |
| 31 | NR1-case | RawPre__m025__UPR | main/f0/vless/G0/outer | True | 178 | 189 | 2.728297025e-06 | 0.256113236555866 | 4.052 |
| 32 | NR1-case | RawPre__m050__CPR | main/f0/vless/G0/outer | True | 142 | 147 | 8.730689751e-06 | 0.238337840317459 | 2.968 |
| 33 | NR1-case | RawPre__m050__SYM | main/f0/vless/G0/outer | True | 54 | 59 | 8.923699162e-06 | 0.274432638044855 | 0.619 |
| 34 | NR1-case | RawPre__m050__UPR | main/f0/vless/G1/outer | True | 242 | 248 | 7.002863398e-06 | 0.221492576616319 | 6.003 |
| 35 | NR1-case | RawPre__m050__UPR | main/f0/vless/G2/outer | True | 385 | 398 | 7.857349546e-06 | 0.166039598231394 | 10.478 |
| 36 | NR1-case | G__m025__UPR | main/f0/vmess/G0/outer | True | 43 | 47 | 9.042249682e-06 | 0.292857115292438 | 0.457 |
| 37 | NR1-case | G__m050__UPR | main/f0/vmess/G0/outer | True | 48 | 52 | 8.923858551e-06 | 0.271190794305964 | 0.528 |
| 38 | NR1-case | P__m025__UPR | main/f0/vmess/G0/outer | True | 42 | 47 | 9.417340416e-06 | 0.293492145523386 | 0.429 |
| 39 | NR1-case | P__m050__UPR | main/f0/vmess/G0/outer | True | 48 | 51 | 9.433493475e-06 | 0.271653318315073 | 0.527 |
| 40 | NR1-case | RawPost__m025__UPR | main/f0/vmess/G0/outer | True | 45 | 49 | 9.609107101e-06 | 0.284754179207728 | 0.473 |
| 41 | NR1-case | RawPost__m050__UPR | main/f0/vmess/G0/outer | True | 54 | 58 | 9.999839642e-06 | 0.262643629201458 | 0.608 |
| 42 | NR1-case | RawPre__m025__UPR | main/f0/vmess/G0/outer | True | 213 | 221 | 6.978896357e-06 | 0.284429905044239 | 5.103 |
| 43 | NR1-case | RawPre__m050__UPR | main/f0/vmess/G0/outer | True | 264 | 273 | 7.924651724e-06 | 0.256221113356806 | 6.714 |
| 44 | NR1-repeat | RawPre__m050__UPR | main/f0/vless/G0/outer | True | 2974 | 5793 | 9.999096278e-06 | 0.240180868251783 | 96.522 |
| 45 | NR1-repeat | P__m025__UPR | main/f0/vless/G0/outer | True | 36 | 39 | 9.491774349e-06 | 0.26936724800084 | 0.330 |

完整机器日志包含训练目标、原/预条件梯度、真实closure与函数评价计数、线搜索、预算和安全退出原因。训练目标下降不作为业务效力结论。

## 6. 确定性与旧端点兼容

两个重复状态：{"passed": true, "repeats": [{"first_attempt": 2, "parameter_error": 0.0, "passed": true, "policy_id": "RawPre__m050__UPR", "role_id": "main/f0/vless/G0/outer", "second_attempt": 44, "training_logit_error": 0.0}, {"first_attempt": 23, "parameter_error": 0.0, "passed": true, "policy_id": "P__m025__UPR", "role_id": "main/f0/vless/G0/outer", "second_attempt": 45, "training_logit_error": 0.0}]}

若完成N4，audits/overlap-comparison.parquet保存27个新旧交叠端点的参数/logit/迭代精确比较；old-endpoint-compatibility.parquet保存151个原接受端点的只读原坐标审核。未完成N4时不能宣称这些审核已经通过。

## 7. 停止原因及边界

没有未解决执行停止。

若4000/20000仍不合格，当前资源候选到此停止，不扩到6000/8000、不换后端、不删困难控制、不启动完整矩阵。若数值先导通过，也只支持相同训练目标在固定集合可充分求解，不支持RA1分类增量。

## 8. 活动成本

报告开始前新活动约360.039秒；旧活动472.9946128996089秒。新先导上限1800秒，1740秒起保留60秒结项窗口；父上限28800秒不重置。累计solver-seconds与活动墙钟分开，最终完整成本见cost-ledger.json与completion.json。

截至本报告拟合求解seconds之和约333.816；原失败复现也计费，失败不隐藏。

## 9. 记录完整性与下一节点

原代码/模型/失败/成本记录哈希未变：True。新先导未对run-01写入完成状态。

没有完整矩阵调度调用。是否恢复完整RA1必须由用户另行确认；旧151与新42最多为166个去重端点而非193，不能把重拟合或重复当成新访问/seed。
