# 0916 跨内容业务配对学习：第一阶段结果

日期：2026-09-17。唯一训练数据：TrafficTracer-content-generalization-20260916。

## 1. 摘要

已按确认计划完成六类 SS/VLESS 业务的特征资格检查、240 次平衡队列、五折跨内容验证、三种教师交叉拟合分法、四臂对照与同内容跨重复错配补充。没有新增采集，没有混入 0914，没有改变模型参数追逐更高性能。

主要发现：

- 六类任务中，真实配对监督 M2 的损失低于跨内容错配 M3，但高于 post-only M0；这支持一定的对应依赖，**不支持当前学习方法带来单侧业务收益**。
- YouTube 同域播放/搜索任务中，M2 相对 M0 有损失改善，但内容级条件性区间跨零；VLESS 下相对跨内容错配的优势还随教师分法改变符号。不能声称已完成可靠业务收益闭环。
- 同内容跨重复错配的描述性平均损失也高于真配，但该对照改变重复轮次对应，不能和跨内容同轮次错配混为同一个机制证据。
- 所有预设分法和负向结果均保存。下一步停在 299 次非平衡候选的敏感性口径审核，不擅自纳入唯一 MDN 恢复访问。

## 2. 仓库同步与代码状态

实施前已提交并推送当前仓库到 origin/main：`ec80859`，远程同步确认 0 ahead / 0 behind。当时 145 项测试通过；Datasets、outputs、plan 与大文件未上传。

本报告对应的业务实现是在该同步之后新增的本地工作，尚未再次提交/推送。最终代码测试为 **151 项通过**。原始数据与历史模型输出未修改。

## 3. 数据与资格

### 3.1 候选和主队列

- 候选：六类 × 五内容 × 两部署 × 五轮 = 300 次访问。
- 业务保守候选：299 次；MDN Overview、SS、第 3 轮因 navigation timeout recovered 单列。其最终响应 200 不是本轮自动放宽标签的依据。
- 主队列：固定第 1/2/4/5 轮，六类 × 五内容 × 两部署 × 四轮 = **240 次**。
- 六标签：Bing 搜索、MDN 文档、GitHub 仓库、Wikipedia 文章、YouTube 搜索、YouTube 播放。

Bilibili 继续采用用户确认的有效播放标签，不因缺少自动遥测回退为无效。其主目标 DIRECT，所以不进入本轮代理配对主队列；Hy2 同样不混入 TCP 排他配对模型。

### 3.2 源与内容身份

冻结 7,502 个输入/代码文件指纹。Bing 重定向只添加已观察到的 rdr/rdrig 参数，搜索词保持不变；其他参数不会被泛化删除。未发现登记资源因最终 URL 合并而减少五内容数。

这证明资源身份层面的内容分组，不证明文章主题独立、没有共享网站模板，也不证明跨日期泛化。

### 3.3 包与连接审计

- 300 次访问特征提取全部完成，0 解析/方向错误。
- 3,246 个排他 TCP 配对，6,492 个两侧捕获记录。
- 时间逆序记录为 0；输入文件检查未发现跨会话相同路径/文件哈希。
- 222 组跨会话 TCP 元组复用比较：时间重叠 0、相同时间戳与原始字节包交集 0、相同初始 SYN 身份 0。
- 240 次主队列全部通过，没有因特征结果额外筛选样本。

范围是六类业务的 300 次 SS/VLESS 访问，不代表整个数据集、Hy2 或所有未来数据都已排除泄漏。流量环境和采集时段混杂仍存在。

## 4. 特征与观测口径

每次访问一行；模型输入仅为 14 个标量：packet_count、transport_bytes、ip_bytes、up/down_transport_bytes、burst_count、fr_runs、fr_switches、fr_runs_per_packet、up_byte_fraction、transition_p_pm、direction_entropy、length_median、iat_median_us。

IAT、burst、FR 与转移在原始实体内计算再聚合。没有使用 Wireshark 内置统计特征。地址、MAC、端口、SNI、domain、路径、绝对时间、session_id 与 captured_bytes 派生量均未进入 X；标签与分组元数据在导出表中保留，不等于被模型使用。

模型主输入为 observed。另缓存 nonempty、exclude_full_retransmission 两种口径和分布摘要，但本轮没有根据这些表示筛选更优模型。

观测为 **offline_index_assisted_post**：测试预测函数只接收 post 数值矩阵，但页面连接范围由离线索引帮助界定。不能由此直接声称未知原始网络流量上的在线 post-only 闭环。

## 5. 划分与模型

### 5.1 五折外层内容验证

每折每类留一个内容。同内容全部重复、两种部署与原始连接共用外层归组；分别在 SS、VLESS 内训练评估，不将部署混合准确率作为主指标。

| 任务，每部署 | 主样本 | 每折训练/测试 | 独立内容 |
|---|---:|---:|---:|
| 六类 domain × activity | 120 | 96 / 24 | 30 |
| YouTube 播放 vs 搜索 | 40 | 32 / 8 | 10 |

三种预先固定的教师分法均使用外层训练每类四内容，分成两个每类各两内容的教师分区。老师为其未见内容产生 OOF 概率；教师训练同时排除错配的 donor 与 receiver 内容。

### 5.2 四臂

| 组 | 训练监督 | 测试输入 |
|---|---|---|
| M0 | post + 硬业务标签 | post |
| M1 | post + 硬标签 + 同次 post 教师 OOF 软标签 | post |
| M2 | post + 硬标签 + 真实对应 pre 教师 OOF 软标签 | post |
| M3 | post + 硬标签 + 同业务跨内容错配 pre 软标签 | post |

M3 保持业务、部署、重复轮次与教师留出分区一致，只交换两个内容，双射且无自配。该交换在约束下是确定的，不制造重复的错配随机种子。

补充 M3_within_content 在同内容内跨重复进行五个种子的双射错配，不改变标签或部署，但改变轮次对应。

### 5.3 固定估计器

教师与学生同为线性 LogisticRegression，C=1、最大迭代 3000；训练内 median imputation 与 standardization；温度 T=1，alpha=0.5。学生软目标为 0.5×one_hot(Y)+0.5×teacher_probability。

软标签通过类别展开/样本权重实现，预处理在原始样本而非展开数据上拟合；已测试 alpha=0 与硬标签训练数值等价，二类和六类均通过。没有调参或校准后挑选结果。

正式实验 760 次拟合，另有 9 次单折烟雾拟合。M0 和全训练侧 pre 教师诊断各 20 次；交叉拟合教师 240 次；M1/M2/M3 学生 180 次；同内容错配学生 300 次。M0 不因教师分法变化而重复训练或计为独立证据。

## 6. 主结果：预登记教师分法 0

下表单元为 macro-F1 / log-loss(bits)，损失越低越好。

| 任务与部署 | M0 post-only | M1 post 教师 | M2 真实配对 | M3 跨内容错配 |
|---|---|---|---|---|
| 六类，SS | 0.8927 / 0.5797 | 0.8847 / 0.6716 | 0.8841 / 0.6429 | 0.8758 / 0.7024 |
| 六类，VLESS | 0.7713 / 0.9310 | 0.7473 / 1.0527 | 0.7383 / 0.9996 | 0.7626 / 1.0112 |
| YouTube，SS | 0.8500 / 0.5773 | 0.8500 / 0.5592 | 0.8500 / 0.5594 | 0.8249 / 0.5887 |
| YouTube，VLESS | 0.6732 / 1.0680 | 0.6732 / 0.9069 | 0.6229 / 0.9003 | 0.6465 / 0.8940 |

损失与 F1 不总同向。YouTube VLESS 的 M2 损失下降，但 F1 比 M0 低，不能只选较有利指标宣称性能提升。

全外层训练内容上的 pre-only 教师诊断 F1 分别为 0.9585、0.8481、0.9499、0.7749，通常高于相应 post-only 学生。但该教师使用每类四个训练内容，辅助监督来自只见过每类两个内容的交叉拟合教师；不能直接用前者性能证明后者必然改善学生。

## 7. 配对差值与内容分组不确定性

定义：G_task=CE(M0)−CE(M2)，G_pair=CE(M3)−CE(M2)，G_soft=CE(M1)−CE(M2)。正值支持 M2 较低损失。

先在内容内平均重复访问，再按类别内 content 重采样 2,000 次；区间条件于当前拟合模型，不能当作外部验证或消除回顾性选择的总体区间。没有据多个比较计算未校正的显著性结论。

| 任务与部署 | G_task [条件性95%区间] | G_pair [条件性95%区间] | G_soft [条件性95%区间] |
|---|---|---|---|
| 六类，SS | −0.0632 [−0.0894, −0.0327] | 0.0595 [0.0406, 0.0774] | 0.0288 [0.0174, 0.0411] |
| 六类，VLESS | −0.0686 [−0.1049, −0.0320] | 0.0115 [−0.0211, 0.0389] | 0.0530 [0.0252, 0.0833] |
| YouTube，SS | 0.0179 [−0.0252, 0.0688] | 0.0293 [−0.1336, 0.1352] | −0.0002 [−0.0349, 0.0291] |
| YouTube，VLESS | 0.1677 [−0.0663, 0.4443] | −0.0063 [−0.1426, 0.1358] | 0.0066 [−0.0580, 0.0750] |

六类 SS 表现为“真配比错配好，但没有优于不使用教师”；这是有价值的利用边界，不是成功业务增益。YouTube 的内容数仅十个，区间较宽，不能将改善均值单独当作确定结论。

## 8. 预设敏感性全部保留

三个教师分法的 G_task 范围：

- 六类 SS：−0.0632 至 −0.0561；三个分法均未胜过 M0。
- 六类 VLESS：−0.0931 至 −0.0671；三个分法均未胜过 M0。
- YouTube SS：0.0179 至 0.0248；均值小幅改善，不能替代内容级区间。
- YouTube VLESS：0.1109 至 0.1677；G_pair 为 −0.0332 至 0.0434，随教师分法变号。

主教师分法下，同内容跨重复错配相对真配的平均损失差（五映射种子的描述性均值）：六类 SS 0.0598、六类 VLESS 0.0312、YouTube SS 0.0669、YouTube VLESS 0.1528 bits。

这些种子不是新样本。该控制改变访问轮次对应，而主跨内容错配保持轮次，因此不能将两者差值直接解释为纯内容/纯时序的因果分解。完整种子级差值与内容区间已输出。

## 9. 防泄漏与追踪核对

- 26,880 条配对映射通过独立审核：教师训练不含 donor/receiver 内容；映射不进入外层测试；业务、部署和分区约束满足；双射、自配规则正确。
- 8,320 条正式 OOF 记录按任务/部署/分法/组分别检查覆盖与重复，并非 8,320 个独立测试样本。
- 概率归一化、外层内容归组、标签编码、输入哈希、输出文件哈希均通过检查。
- 模型参数、填补与标准化统计保存在 fit-ledger，教师 OOF 与训练成员可追踪。
- 测试样本未参与教师训练、预处理或超参数选择；测试 pre 只用于单独的教师诊断，不进入学生预测。

这些检查不排除部署环境、固定采集顺序、同网站模板与已知主题范围的影响，也不等于在线页面边界已解决。

## 10. 可直接使用的特征与结果文件

输出根：`outputs/content-generalization-20260916/business-01/`。

- [pre 特征，300 行](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/content-generalization-20260916/business-01/pre-features.parquet)
- [post 特征，300 行](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/content-generalization-20260916/business-01/post-features.parquet)
- [配对平铺特征，300 行](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/content-generalization-20260916/business-01/paired-features.parquet)
- [完整两侧摘要，三种包口径](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/content-generalization-20260916/business-01/side-summaries.parquet)
- [主队列，240 行](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/content-generalization-20260916/business-01/primary-cohort.parquet)
- [特征字典与输入白名单](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/content-generalization-20260916/business-01/feature-dictionary.json)
- [全部模型指标与混淆矩阵](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/content-generalization-20260916/business-01/report/metrics.json)
- [配对差值与条件性区间](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/content-generalization-20260916/business-01/report/paired-gains.parquet)
- [逐内容差值](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/content-generalization-20260916/business-01/report/content-gains.parquet)
- [模型与映射审核](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/content-generalization-20260916/business-01/report/validation.json)
- [299 候选敏感性审核方案](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/content-generalization-20260916/business-01/report/299-sensitivity-proposal.json)

300 行表包含第三轮及唯一恢复访问，使用者必须依据 primary_candidate 和资格字段筛选；不能直接把所有行视为已确认的主模型训练集。完整摘要有 900 行，三种包口径也不能被当成三个独立访问。

## 11. 复用入口

配置：[content-generalization-20260916-business.yaml](F:/Program/VSCode/MyGit/ProxyAnalysis/configs/content-generalization-20260916-business.yaml)。

新增 Python 模块：business_features（冻结/逐包提取）、business_identity（连接身份门）、business_splits（外层与教师划分）、privileged_learning（四臂及补充）、business_report（独立审计与统计）、business_export（配对特征导出）。

执行顺序记录：

```powershell
$env:PYTHONPATH = 'src'
& D:/Tools/Anaconda/envs/Pytorch312/python.exe -m proxy_analysis.crosscontent.business_features --mode freeze
& D:/Tools/Anaconda/envs/Pytorch312/python.exe -m proxy_analysis.crosscontent.business_features --mode extract
& D:/Tools/Anaconda/envs/Pytorch312/python.exe -m proxy_analysis.crosscontent.business_identity
& D:/Tools/Anaconda/envs/Pytorch312/python.exe -m proxy_analysis.crosscontent.privileged_learning --smoke
& D:/Tools/Anaconda/envs/Pytorch312/python.exe -m proxy_analysis.crosscontent.privileged_learning
& D:/Tools/Anaconda/envs/Pytorch312/python.exe -m proxy_analysis.crosscontent.business_report
& D:/Tools/Anaconda/envs/Pytorch312/python.exe -m proxy_analysis.crosscontent.business_export
```

这些是已执行流程，不应直接在当前已有目录重复全流程。freeze、learning、report 拒绝覆盖；提取复用会话缓存，读取缓存不算重训练。新运行需选择新输出配置并冻结来源；部分入口当前使用默认配置路径，不宣称任意数据集可直接一键运行。

## 12. 当前需要确认的关键节点

299 候选敏感性只完成了样本匹配方案，尚未训练。保持唯一 MDN 恢复访问排除时：

- 六类 SS：当受影响 MDN 内容在训练侧时，原有 119 个训练访问，跨内容共同轮次匹配后为 118；其余一折训练 120、测试 29。
- 六类 VLESS：各折训练 120、测试 30。
- YouTube 两部署：各折训练 40、测试 10。

这与 240 主队列的“所有类别均四轮”是不同口径。建议继续采用上述共同轮次、共同样本池的敏感性，不放弃双射、不纳入 MDN 恢复访问；确认后再实施。若希望改用全 300 次，需先确认恢复访问的标签资格，不能根据本轮负向结果放宽。

现在可以写入论文的结论：现有部署对应价值不自动迁移为业务收益。当前固定线性软标签方法显示一定对应依赖，但六类任务未优于 post-only，同域活动任务证据仍不确定。该边界限于当前表示、学习器、监督形式与离线观测条件，不证明配对信息对所有业务方法都无用。
