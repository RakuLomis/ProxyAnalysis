# TrafficTracer-content-generalization-20260916：数据资格与实验可行性分析

日期：2026-09-17。范围：新批次单独审核；未与 0914 合并、未训练分类器、未修改原始数据。

更新（2026-09-17，用户确认）：本批次 Bilibili 视频按用户观察接受正常播放标签。证据是目标级人工观察，不是全部 75 次访问逐次检查或播放时长遥测。下文“自动证据未确认”和自动计数保留原机器审计含义，不再作为排除有效播放标签的理由；“业务证据待确认”的历史表述由本更新替代。后续使用 [有效标签表](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/content-generalization-20260916/audit-01/activity-confirmation-20260917/effective-session-eligibility.parquet) 与 [确认摘要](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/content-generalization-20260916/audit-01/activity-confirmation-20260917/summary.json)。正常播放不改变 DIRECT 路由证据：Bilibili 当前属于“播放有效、主目标直连”，不是严格代理配对主队列。

## 1. 判断摘要

新数据已经补上此前最重要的内容数量缺口：六类业务在 SS/VLESS 下具有五个共同登记内容，具备推进跨内容配对监督实验的初步条件。YouTube 同时有视频播放与搜索结果浏览，为同域名内区分活动提供了有价值的对照。

但不能把整个批次直接当作“七业务 × 三协议”的同质配对数据集：

- Bilibili 主目标请求全部 DIRECT；SS 没有代理配对，VLESS 的少量代理请求来自图片资源域名。该部分不能作为完整视频业务的代理前后变换样本。
- Bilibili 摘要没有播放遥测；这代表新批次缺少自动播放确认，不等于没有播放，也不推翻用户此前对旧批次的确认。
- Hy2 的 Bing 主目标也全部 DIRECT，且 YouTube 存在 UDP/h3 的 REJECT 策略记录。三协议的路由/应用传输策略不完全一致。
- 新审核目前到达“清单、执行证据、路由、索引配对文件存在性”层面；完整包级特征、内容语义独立性、重定向别名及跨集合捕获身份检查还需完成。

## 2. 规模与配置

| 项目 | 结果 |
|---|---:|
| 业务标签 | 7 |
| 登记目标 | 35，每标签 5 个 |
| 部署 | SS / VLESS / Hy2 |
| 每目标每部署重复 | 5 |
| 选定访问 | 525 |
| 保存的采集尝试 | 538 |
| 未选定先前尝试 | 13，不作为额外重复 |
| completed / degraded | 517 / 8 |

所有 525 个选定访问为 TrafficTracer 1.0.27，同一 commit `3329d3d5e6336c99bfc3d60ab97eb46a12495295`，cold 模式，配置采集时长 60 秒。YouTube 播放目标为 25 秒，但沿用用户口径：只要有正片播放即视为有效，不把 25 秒目标当作硬性标签门槛。

525 次的 capture_integrity 和 correlation 汇总均为 passed；这是采集器汇总状态，不是本轮逐包验证的结论。尤其不能据此推出原始捕获零丢包。

期望协议与观测协议在选定访问中没有不一致。但每种协议仍对应固定部署节点，不是随机分配同一网络路径的协议因果实验。

## 3. 业务与内容覆盖

| domain × activity | 五个内容的类型 | 本轮业务意义 |
|---|---|---|
| youtube.com × video_playback | 5 个不同 video ID | 未见视频的播放任务 |
| youtube.com × search_results_view | 5 个不同搜索词 | 同域名内与播放活动对照 |
| wikipedia.org × article_view | 5 篇文章 | 不再是首页与单篇文章混合 |
| developer.mozilla.org × document_view | 5 个文档目标 | 同网站文档访问 |
| github.com × repository_view | 5 个仓库 | 不再用首页、Explore 充当不同仓库 |
| bing.com × search_results_view | 5 个不同搜索词 | 不同查询内容的结果页访问 |
| bilibili.com × video_playback | 5 个视频目标，含一个指定 p=2 | 内容登记改善，但路由资格不通过 |

这里的“内容”是登记资源身份，不等于主题或语义统计独立。Wikipedia 五篇文章集中于网络主题；MDN 多个内容集中于 HTTP。可以研究未见 URL/资源泛化，不能直接声称未见主题泛化。

非视频 activity 是配置的访问业务，摘要一般为 page_load。导航和活动成功支持“访问/加载结果页或文档”，不证明用户阅读、仓库交互或实际手动输入搜索词。

## 4. SS/VLESS 的配对候选

沿用既有排他 TCP 规则：代理 egress、可定位的 pre/post、非共享外层、外层不重复、两侧 TCP、捕获文件存在且非零字节。此处没有逐包确认方向、载荷非空或重新提取完整特征。

| 标签 | SS 配对且业务自动证据通过 | VLESS 配对且业务自动证据通过 | 共同内容数 |
|---|---:|---:|---:|
| YouTube 播放 | 25/25 | 25/25 | 5 |
| YouTube 搜索 | 25/25 | 25/25 | 5 |
| Wikipedia 文章 | 25/25 | 25/25 | 5 |
| MDN 文档 | 24/25 | 25/25 | 5 |
| GitHub 仓库 | 25/25 | 25/25 | 5 |
| Bing 搜索 | 25/25 | 25/25 | 5 |
| Bilibili 视频 | 0；代理索引候选也是 0 | 自动播放未确认；7 次有代理索引候选 | 不可进入主队列 |

前六类业务合计 **299 个保守联合候选访问**。未通过的一个为 MDN Overview、SS、第 3 轮：`NAVIGATION_TIMEOUT_RECOVERED`，最终 HTTP 200、目标 URL 正确、有 4 个排他 TCP 配对，但 navigation/activity 均 degraded。它属于可单独审查的恢复访问，不应直接宣称页面失败，也不应未经审查自动纳入主队列。

前六类全部 SS/VLESS 访问共有 3,246 个索引级排他 TCP 配对；包含 Bilibili 附属资源后共 3,259 个。这些连接数不是独立内容样本量。

## 5. YouTube 正片播放证据

75 个 YouTube 播放访问全部具有正片存在证据，覆盖三部署各 25 次。

| 部署 | 正片时长最小值 | 中位数 | 达到配置 25 秒目标 |
|---|---:|---:|---:|
| SS | 18.283 秒 | 40.033 秒 | 23/25 |
| VLESS | 41.486 秒 | 44.497 秒 | 25/25 |
| Hy2 | 42.218 秒 | 46.200 秒 | 25/25 |

SS 某视频第 4/5 轮分别播放 18.283/20.106 秒，采集器因不足 25 秒标 degraded；按用户“存在正片即有效”的口径，两次均保留视频标签。

Hy2 另有两次 YouTube 访问因关键资源问题标 degraded，但正片分别观察到 47.244/46.951 秒。业务播放有效与网络/资源质量降级可以同时成立，应分列保存。

## 6. Bilibili：播放确认与路由是两道不同门

### 6.1 没有自动播放遥测，不等于没有播放

五个 Bilibili 目标的配置具有 `run_label: video_playback`，但没有 YouTube 那样的 playback provider 配置。75 次摘要的 activity_kind 均为 page_load，74 passed、1 degraded；`playback` 为 null，正片观察/时长字段缺失。

因此本轮自动证据字段为未确认。旧批次的用户确认不自动升级为对本批次全部新内容、全部访问的逐次确认；同时也不能把它们判为“确定没有播放”。

### 6.2 更实质的阻断：业务主目标没有走代理

全部 75 次 Bilibili 的精确目标 URL 请求都归属于 DIRECT 连接：

| 部署配置 | 主目标 DIRECT | 至少有一个代理请求的访问 |
|---|---:|---:|
| SS | 25/25 | 0/25 |
| VLESS | 25/25 | 7/25 |
| Hy2 | 25/25 | 1/25 |

VLESS 的代理请求集中于 `i1.hdslb.com`，共 217 条请求索引记录；这不能替代主视频业务经过代理的证据。Hy2 少量代理请求来自 `s1.hdslb.com`、`api.bilibili.com`、`i0.hdslb.com`。

抽查 SS 的连接明确记录 `egress.outcome=direct`，策略为国内网站规则、selected_node=DIRECT。即使用户补充确认本批次确有视频播放，也不会消除主业务直连问题。

建议将 Bilibili 留作路由失败/业务证据待确认的诊断分支，不进入当前严格代理配对业务主实验。不擅自更改代理规则或要求再次采集；先用已经具备条件的六类业务推进。

## 7. Hy2 需要单列解释

- 共享 UDP carrier 本身不适用排他 TCP 配对；审核表中的 0 不是捕获失败。
- Bing 的 25 次 Hy2 主目标请求全部 DIRECT，尽管其中 10 次访问有附属代理请求。因此三协议 Bing 对比存在路由语义不一致。
- YouTube 的 Hy2 主目标请求走代理；每次有一个 `static.doubleclick.net` 直连请求。
- googlevideo.com 的请求索引中，Hy2 有 445 条关联到 UDP/h3、REJECT 策略的连接记录，另有 147 条关联代理连接。SS 有 520 条代理记录，VLESS 有 567 条代理、6 条 unknown。

445 是请求关联记录数，不是 445 次独立连接或 445 次最终播放失败；样例请求最终 HTTP 200，不能把中间被拒绝的传输尝试与最终应用失败混为一谈。它反映部署策略差异，不能据此估计丢包率或断言 Hy2 协议本身导致失败。

建议首个严格配对业务实验继续只用 SS/VLESS；Hy2 后续使用 carrier-aware 的独立观测定义和明确路由队列。

## 8. 采集设计还留下哪些混杂？

1. **固定顺序**：manifest 中按轮次、目标顺序采集，每目标内通常 VLESS→SS→Hy2；目标按业务成块排列。五轮并非随机化业务时段。
2. **部署固定节点**：每种协议对应固定节点，不能把部署可预测性解释为纯协议因果效应。
3. **仅同一批次/日期**：本批次开始时间覆盖 UTC 2026-09-16 02:04 至 17:36 左右，没有形成多日期的独立外部测试。
4. **旧内容重叠**：35 个目标中有 6 个 URL 在 0914 出现过：YouTube 首个视频、Wikipedia Computer_network、MDN HTTP、GitHub TrafficTracer，以及两个 Bilibili 视频。版本一致不代表两批次是无重叠的独立内容测试集。
5. **网站与业务部分重合**：大多数 domain 只有一个 activity，六类分类仍可能主要辨识网站。YouTube 播放 vs 搜索是更直接的同域活动对照。

因此建议本批次从头独立训练、按 content 分组；不要将旧内容上的旧模型调参结果宣称为对所有新数据的盲测。

## 9. 建议下一步，而不是立即训练

### 9.1 先完成六类 SS/VLESS 的特征资格

对 300 次原始访问单独抽取既有流量特征，保留唯一 MDN 降级标记；逐包检查文件可读、方向、非空载荷、重复原始捕获和 pre/post 边界。建立六类、30 内容的特征集合与来源清单。不要套用原先写死 0914/140 会话的入口。

训练输入继续排除地址、端口、SNI、标签、路径与绝对时间；它们可以用于配对和审计。模型观测仍需标明 offline-index-assisted，不能未经验证称为在线 post-only 选择闭环。

### 9.2 外层按内容分组

建议五折，每折每类别留下一个内容，所有部署和重复访问一起留出；训练侧每类四内容，再做两折教师交叉拟合，留出折内跨不同内容错配。先固定划分，再训练。

五内容恰好满足工程设计，不提供额外独立调参内容，更不是统计功效保证。超参数尽量预先固定或严格在训练侧选择，不能反复用外层测试结果选方案。

### 9.3 不平衡重复的处理要显式

主候选 299 次中，MDN 有一个内容在 SS 仅四次。若教师留出折中两个内容分别四次和五次，要求跨内容全双射时未必可行，不能静默跳过样本或让同内容自配。

一种已核对可行的保守平衡候选是使用轮次 1、2、4、5：六标签 × 五内容 × 两部署 × 四轮 = **240 次**，避开唯一 MDN 第三轮降级，所有内容计数相同。代价是删除不少正常第三轮访问，并改变轮次范围。

另一选择是保留 299 次，在每个训练分区针对业务/部署构造共同平衡子队列，或先确认恢复的 MDN 访问是否可纳入 300 次。应在看模型性能前确定，不能挑选使收益更高的口径。当前尚未自动选定任何训练队列。

### 9.4 两个任务并行报告，但不启动额外采集

- 六类 domain × activity：对应原始业务定义，报告网站识别混杂。
- YouTube 内播放 vs 搜索：同域名活动对照，避免把全部业务收益解释为 domain 指纹。

两任务均比较 post-only、post 教师蒸馏、真实 pre→post 配对监督、同业务错配监督；测试阶段只用 post。主对照必须共享样本、划分、模型容量和预算。

## 10. 产物与边界

已生成：

- [逐访问资格表](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/content-generalization-20260916/audit-01/session-eligibility.parquet)
- [业务 × 部署覆盖表](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/content-generalization-20260916/audit-01/label-protocol-coverage.parquet)
- [业务资格门](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/content-generalization-20260916/audit-01/business-gates.json)
- [执行例外清单](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/content-generalization-20260916/audit-01/exceptions.json)
- [路由汇总](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/content-generalization-20260916/audit-01/routing/route-summary.json)
- [Bilibili 代理资源域名](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/content-generalization-20260916/audit-01/routing/bilibili-proxy-request-hosts.json)
- [清单与配对审核脚本](F:/Program/VSCode/MyGit/ProxyAnalysis/src/proxy_analysis/crosscontent/audit_capture.py)
- [请求路由审核脚本](F:/Program/VSCode/MyGit/ProxyAnalysis/src/proxy_analysis/crosscontent/audit_routes.py)

`exceptions.json` 包含自动播放未确认的 Bilibili 访问，不代表这些访问都失败。`joint_candidate` 是保守索引资格，不是最终训练资格。报告中的请求级细查不能替代媒体逐包关联或完整特征提取。

最终判断：**无需为了启动第一个业务实验再等待所有七类、三协议都完美。现有六类 SS/VLESS 数据已具有推进价值；先完成特征与队列资格，再按内容划分运行单侧业务对照。Bilibili 与 Hy2 的路由差异必须单列，不能混进主结论。**
