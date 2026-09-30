# 0916 业务学习：299 次保守候选敏感性结果

日期：2026-09-17。状态：已完成用户确认的 299 候选实验；未新增采集、未纳入 MDN 恢复访问、未更改模型超参数或输入特征、未推送仓库。

## 1. 本次口径

用户确认：降级样本可以用于模拟真实访问，不能因 degraded 标签直接认定为无效；现阶段仍采用比较保守的候选。

本轮沿用既有 299 候选，仅暂不纳入 MDN Overview、SS、第 3 轮恢复访问。**不是一律排除所有 degraded**：已有正片存在证据但未达到 25 秒目标的 YouTube 访问仍按已确认规则保留。Bilibili 保留人工确认的有效播放标签，但主目标 DIRECT，仍不进入代理配对主实验。

240 次平衡主队列与结果不变。本次恢复部分第三轮有效访问，是同一批次上的样本口径敏感性，不是新独立验证集，也不能把 240 与 299 相加作为样本量。

数据范围：六业务、30 个内容、SS/VLESS。六类任务 SS 149 次、VLESS 150 次；YouTube 同域二类任务各部署 50 次，是六类数据的子集。

## 2. 公平匹配与模型不变项

继续采用原五折外层 content 分组、三种预设教师 2+2 分法、14 个标量特征、线性 LogisticRegression、C=1、alpha=0.5、T=1。没有在新结果上重新调参或选择最优教师分法。

在各外层训练集、教师留出分区、业务和部署内，两个内容只使用共同可用轮次。匹配后的样本同时用于 M0、M1、M2、M3；不是仅从错配组删除难样本。测试内容和有效测试访问不因错配需要被删减。

- SS 六类：受影响内容在训练侧时，119 个可用训练访问进一步匹配为 118；它在测试侧时，训练 120、测试 29。
- VLESS 六类：训练 120、测试 30。
- YouTube 二类，两部署：训练 40、测试 10。

这与训练前输出的 299 候选匹配方案逐项一致。每个学生组都使用对应分法的共同训练池；由于 SS 的匹配池随教师分法可能变化，M0 只在训练成员完全相同时复用，不错误地拿不同训练池的 M0 作对照。

本轮运行四臂及 pre 教师诊断，没有重复上一阶段的同内容跨重复错配补充。正式拟合 476 次；9,552 条配对映射与 5,985 条预测记录通过成员/教师排除/双射/OOF 覆盖审核。这些记录数不等于独立测试样本数。

## 3. 指标权重

主要报告按内容等权：四次访问的内容与五次访问的内容总权重相同。macro-F1、balanced accuracy 使用每次访问权重 1/该内容访问数计算；CE、Brier 也按同一内容权重汇总。普通按访问汇总的指标另存作次要结果。

区间在各业务类别内部按内容重采样 2,000 次，保留所有组的配对关系，条件于本轮已拟合模型。不是外部环境置信区间，也不把三种教师分法当成三个独立数据集。不报告未经多重比较处理的显著性结论。

## 4. 主教师分法结果

单元为按内容等权 macro-F1 / CE(bits)，CE 越低越好。

| 任务与部署 | M0 post-only | M1 post 教师 | M2 真实配对 | M3 跨内容错配 |
|---|---|---|---|---|
| 六类，SS | 0.8860 / 0.5331 | 0.8930 / 0.6120 | 0.8924 / 0.5877 | 0.8983 / 0.6448 |
| 六类，VLESS | 0.7934 / 0.8781 | 0.7561 / 0.9850 | 0.7840 / 0.9315 | 0.8132 / 0.9490 |
| YouTube，SS | 0.8800 / 0.5181 | 0.8599 / 0.5204 | 0.8800 / 0.5142 | 0.8800 / 0.5531 |
| YouTube，VLESS | 0.7596 / 1.0428 | 0.7196 / 0.8903 | 0.6377 / 0.8946 | 0.7182 / 0.8921 |

F1 和 CE 并不一致。例如六类 SS 的 M3 F1 更高，但 CE 明显更差；YouTube VLESS 的 M2 CE 比 M0 低，但 F1 下降。不能按结果临时更换主要指标来宣称配对收益。

## 5. 主要差值及条件性区间

G_task=CE(M0)−CE(M2)，表示单侧任务收益；G_pair=CE(M3)−CE(M2)，表示相对错配的对应收益。正值支持 M2 损失更低。

| 任务与部署 | G_task [95%条件性区间] | G_pair [95%条件性区间] |
|---|---|---|
| 六类，SS | −0.0546 [−0.0722, −0.0338] | 0.0571 [0.0381, 0.0760] |
| 六类，VLESS | −0.0534 [−0.0987, −0.0110] | 0.0175 [−0.0218, 0.0486] |
| YouTube，SS | 0.0039 [−0.0241, 0.0349] | 0.0390 [−0.1118, 0.1377] |
| YouTube，VLESS | 0.1482 [−0.0673, 0.4191] | −0.0025 [−0.2084, 0.2096] |

相对普通 post 软标签监督的 G_soft=CE(M1)−CE(M2)：六类 SS 0.0243、六类 VLESS 0.0535、YouTube SS 0.0062、YouTube VLESS −0.0043 bits。YouTube 两项区间均跨零，不能认为 pre 教师在同域活动任务中稳定优于普通软标签训练。

## 6. 三种教师分法的变化范围

| 任务与部署 | G_task 范围 | G_pair 范围 |
|---|---|---|
| 六类，SS | [−0.0558, −0.0546] | [0.0437, 0.0571] |
| 六类，VLESS | [−0.0631, −0.0534] | [0.0175, 0.0450] |
| YouTube，SS | [−0.0091, 0.0039] | [−0.0199, 0.0390] |
| YouTube，VLESS | [0.1040, 0.1482] | [−0.0264, 0.0550] |

六类任务的 M2 均未在主要损失上超过 M0，结论没有因加入有效第三轮访问而逆转。YouTube SS 在 299 口径下也出现分法间变号，不能只突出主分法的小幅正值。

## 7. 可以与不可以得出的结论

可以：当前表示和固定软标签线性学习器显示一定的真实对应依赖；尤其六类 SS 的真配损失低于跨内容错配。但这种依赖没有转化为稳定优于 post-only 的任务收益。同域活动任务仍缺乏确定的配对增益证据。

不可以：宣称配对学习已经实现业务闭环；宣称所有配对方法无效；把 log-loss 差等同真实互信息；或将同批次口径敏感性视为新环境外部验证。

降级访问的现实意义仍然成立。本轮并未测试主动放宽到全部 300 次、按故障程度分层、真实网络拥塞鲁棒性等新问题。后续若采用更宽松队列，应单独冻结规则并保留本轮对照，而不是为改变当前结论事后放宽样本。

## 8. 产物与复跑

- [299 候选冻结队列](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/content-generalization-20260916/business-01/conservative-299/cohort.parquet)
- [四组指标与教师诊断](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/content-generalization-20260916/business-01/conservative-299/metrics.json)
- [收益与条件性区间](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/content-generalization-20260916/business-01/conservative-299/paired-gains.parquet)
- [逐内容差值](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/content-generalization-20260916/business-01/conservative-299/content-gains.parquet)
- [实际训练/测试成员与匹配排除](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/content-generalization-20260916/business-01/conservative-299/student-membership.json)
- [审核结果](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/content-generalization-20260916/business-01/conservative-299/validation.json)
- [可复用执行与汇总脚本](F:/Program/VSCode/MyGit/ProxyAnalysis/src/proxy_analysis/crosscontent/business_conservative.py)

命令记录：

```powershell
$env:PYTHONPATH='src'
& D:/Tools/Anaconda/envs/Pytorch312/python.exe -m proxy_analysis.crosscontent.business_conservative
& D:/Tools/Anaconda/envs/Pytorch312/python.exe -m proxy_analysis.crosscontent.business_conservative --report
```

训练入口拒绝覆盖已存在的 conservative-299 目录；报告入口在验证训练输出哈希后重建派生统计，不触发重训练。完整测试 **153 项通过**。上一份 240 队列报告的“等待 299 敏感性确认”已由本次完成状态替代；其数值与主队列仍保持不变。
