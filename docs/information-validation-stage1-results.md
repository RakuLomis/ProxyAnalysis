# 信息论方向第一阶段：实施结果与下一决策

日期：2026-09-07。用户确认的任务标签是 `Y=(站点domain, 业务活动)`；不同站点的视频播放是不同类别，同站点不同视频内容共享播放类别。

## 1. 本次完成了什么

完成计划A–F的主要数据与证据桥接工作：环境检查、cohort冻结、三视图构造、严格分组划分、部署预测、post→Δ和post→pre回归、信息论操作量、标签证据审计及可复现性验证。尚未进行Y任务分类、teacher训练或配对特权学习。

- 使用Pytorch312，Python 3.12；numpy 2.0.1、scipy 1.15.2、scikit-learn 1.6.1；未安装/升级依赖。
- 新代码独立放在 `src/proxy_analysis/information_validation/`，没有修改原始捕获或历史特征计算口径。
- 主cohort为10个URL、SS/VLESS各5轮，共100会话；四轮敏感性为80会话。
- 14个pre标量、同名14个post标量、17个Δ候选量。SS/VLESS的entity-count因严格配对而恒定，排除；JS和累计距离不当成单侧字段。
- 六个预先指定设置：observed主分析、rounds2to5、nonempty、排除完整重传、主文档走代理、排除重试。
- 输出10,940条分类OOF预测、68,240条回归OOF预测。这些是多实验重复预测的记录数，不能当作独立会话数。
- 所有主模型不输入domain/SNI/IP/端口/时间顺序。URL仅作分组；条件U和元数据模型是明确分列的诊断。

结果目录：[20260907-full-02](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/information-theory-validation/20260907-full-02/first-stage-validation-report.md)。第一次全量运行保留在full-01；full-02增加身份一致性等断言后独立重跑，关键数值产物完全一致。

## 2. 最重要的新发现：pre也有很强的部署可预测性

下表为主cohort的logistic、汇总OOF macro-F1；不是平均fold F1。LORO为整轮留出，LOUO为整URL留出，所有参数选择均在外层训练内按相同类别分组进行。

| 输入 → 部署C | 留轮次F1 | 留URL F1 | 留URL log-loss(bits) |
|---|---:|---:|---:|
| pre | 0.980 | 0.930 | 0.398 |
| post | 0.890 | 0.770 | 1.095 |
| Δ | 1.000 | 1.000 | 0.014 |

这直接要求我们收紧teacher假设：当前pre视图不只包含与业务有关的信号，也包含与本次部署相关的信号。它可能来自网络反馈、服务器/路径差异、配对筛选或其他关联，当前结果不识别具体原因。

因此，不能把pre视图等同于“未经部署影响的语义真值”。后续必须比较pre→Y与pre→C，并限制teacher复制部署相关成分的风险。

另外，旧实验0.867是更大数据上的三类部署分类、更多特征与不同评估汇总方式；本表是新数据的两类任务。不能将1.000与0.867直接比较为模型进步。

## 3. Δ分类：较强的探索性支持，但不是机制因果证明

Δ的主分析logistic和固定浅层ExtraTrees在两种划分中都没有分类错误。rounds2to5也为1.000；nonempty的留URL logistic F1为0.990；排除完整重传后为1.000。

这支持：本批SS/VLESS严格配对的变换特征，在未见URL上仍具有部署区分信号。

但必须保留以下限定：

- 仅10个URL及本次两个部署，协议与节点/配置仍混杂。
- 特征家族与研究问题延续自同批数据的前期分析，因此属于后续探索性验证，不是独立新采样的确认试验。
- 完整配对筛选可能影响观察对象，结果不代表全部访问或全部协议。
- 主文档与no-retry的100会话恰好和主cohort相同；其重复得到相同分数不是新的独立稳健性证据。
- 缺失诊断仅达到先验表现，本cohort三视图没有缺失值；元数据诊断留URL balanced accuracy为0.54，但弱元数据模型不排除混杂。

## 4. post→Δ：当前轻量模型不能普遍跨URL恢复

主要ridge模型在留URL测试中的表现：

| Δ目标 | MAE | R² |
|---|---:|---:|
| packet_count | 0.1963 | -0.160 |
| transport_bytes | 0.1147 | -0.486 |
| burst_count | 0.2223 | 0.010 |
| FR-runs | 0.1419 | -4.773 |
| length JS | 0.1749 | -3.832 |
| IAT JS | 0.06385 | -1.433 |

负R²说明相对于该汇总测试目标的常量均值参照表现较差，不意味着互信息为负。实际可部署的训练均值、部署均值等基线另外单列，不能只看R²解释改进。

这并不意味着所有可恢复性都不存在：剔除共享/相关家族后，bytes与burst的留URL R²分别为0.392和0.177，表明输入表示和泛化稳定性影响很大。当前模型是预先固定的轻量ridge，不是Bayes最优估计。

我们还加入：训练全局均值/中位数、训练部署均值、训练URL/URL×部署均值，以及 `log(post)−训练mean(log(pre))` 代数基线。条件均值享有C/U信息，标记为特权参照；留URL时未见U回退到训练全局均值。真实post→pre回归在留URL时，除bytes有弱正R²外，其余三个主要标量R²为负。

因此可写：“Δ中有很强的部署判别信号，但当前post标量基线尚未建立普遍的跨URL变换恢复能力。”不能写成“配对信息已经能由post学习到”，也不能反向写成“post中完全没有变换信息”。

距离目标已做同家族剔除，但未执行完整分布的受控置换耦合实验；该辅助项仍待扩展，未重读大规模PCAP来补做。当前结果不宣称完全消除所有数学耦合。

## 5. 信息论操作量应怎样读

主分析的Δ留URL交叉熵为0.014 bits，对应 `H(C)−CE≈0.986 bits`；留轮次为约0.993 bits。它们是固定评估下的经验代入量，不是精确MI或有总体置信保证的下界。

post留URL logistic的F1虽然为0.770，log-loss却为1.095 bits，超过均衡先验的1 bit，因此 `H(C)−CE≈−0.095 bits`。这说明概率预测存在严重错误/过度自信的代价，不代表真实MI为负。固定ExtraTrees在同设置log-loss约0.828 bits，概率质量优于logistic；未据此替换预定主模型。

零测试错误代入Fano得到1 bit，只能作为plug-in算术结果，不能声称有限样本已证明总体条件熵为零。

URL bootstrap只用于固定OOF结果的条件性描述；共同轮次、重叠训练集和分析选择的不确定性不能由它完全表达。没有对fold/种子做独立样本t检验。

## 6. G1标签审计：现在还不能训练用户指定的视频播放类别

逐会话读取270个最终访问的summary，检查显式播放目标、主内容观测、主内容秒数及活动成功状态。没有用站点名称或视频资源请求推断播放。

| 用户关心的站点活动 | 最终会话 | 播放达标 | 明确未达标 | 无充分播放证据 | 内容数 |
|---|---:|---:|---:|---:|---:|
| bilibili.com::video_playback | 15 | 0 | 0 | 15 | 1 |
| youtube.com::video_playback | 15 | 1 | 14 | 0 | 1 |
| vimeo.com::video_playback（媒体审计扩展项） | 15 | 0 | 0 | 15 | 1 |

唯一达标样本是YouTube、VLESS、第1轮，主内容28.907秒，超过25秒目标，且为页面代理候选。其余YouTube会话没有达到记录的播放目标。没有证据的Bilibili/Vimeo不能解释为“一定没播放”，只能解释为无法凭当前记录验证。

这意味着：

1. 当前无法建立Bilibili播放与YouTube播放两个合格类别的训练/测试集。
2. 唯一成功播放样本没有跨部署/跨轮覆盖。
3. 每站点只有一个内容，即使增加同视频重复，也不能证明跨内容共有活动泛化。
4. 页面加载记录继续保留，但不能自动替换用户要求的播放标签。其他站点细分业务活动仍需行为定义和证据映射。

在此暂停Y任务、teacher和LUPI训练。建议下一步先制定并确认“Bilibili/YouTube视频播放”补采集清单：多个独立视频、可靠的播放成功检测、两部署完整覆盖及轮次平衡。最低内容数只是可划分条件，正式采集规模需另定。采集前还需排查Bilibili直连/代理路由可用性与YouTube播放未达标原因，避免重复产生不可用样本。

如果用户希望先使用现有页面加载数据，只能另行明确批准页面加载活动标签；不能将其结果写成视频播放识别。

## 7. 产物、验证与复跑

- [完整自动报告](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/information-theory-validation/20260907-full-02/first-stage-validation-report.md)
- [标签证据长表](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/information-theory-validation/20260907-full-02/label-evidence.parquet)
- [分类汇总](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/information-theory-validation/20260907-full-02/classification-summary.parquet)
- [回归汇总](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/information-theory-validation/20260907-full-02/recoverability-summary.parquet)
- [分组清单](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/information-theory-validation/20260907-full-02/split-manifest.parquet)
- [输入/代码摘要与有效配置](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/information-theory-validation/20260907-full-02/provenance.json)

全项目102项测试通过。full-01与full-02的分类/回归OOF、两类汇总、信息操作量、cohort、split和label evidence共8个文件逐字节一致。10,940条分类OOF全部核对属于对应fold的test且不属于train。

在工作区根目录设置 `PYTHONPATH=src` 后，使用Pytorch312执行：

```powershell
& D:/Tools/Anaconda/envs/Pytorch312/python.exe -X utf8 -m proxy_analysis.information_validation --output-root outputs/information-theory-validation/<新的run_id>
```

输出目录必须不存在，避免覆盖旧结果。计划和生成数据仍按既有规则排除Git同步；本次未提交或推送仓库。
