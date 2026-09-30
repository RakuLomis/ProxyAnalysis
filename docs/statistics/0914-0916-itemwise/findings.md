# 统计结果解读与重点发现

本章解释逐条目数据表所呈现的规律，不把本轮全量描述性统计替换成此前分类实验的性能结论。

## 1. 数据覆盖与资格

两个数据集包含 1,002 次存储尝试，选定 987 次。分批条目为 64 + 18 + 35 = 117；相同资源在 broad 与 repeat 中仍是不同条目，不能视作独立的新内容或简单拼成六次重复。

| 批次 | 部署 | 访问 | 可计算代理上下文 | 主请求proxy | DIRECT pre观测 |
| --- | --- | --- | --- | --- | --- |
| 0914-broad | Hy2 | 64 | 41 | 37 | 43 |
| 0914-broad | SS | 64 | 42 | 39 | 26 |
| 0914-broad | VLESS | 64 | 44 | 41 | 24 |
| 0914-repeat | Hy2 | 90 | 65 | 60 | 55 |
| 0914-repeat | SS | 90 | 70 | 65 | 25 |
| 0914-repeat | VLESS | 90 | 79 | 70 | 20 |
| 0916 | Hy2 | 175 | 136 | 125 | 100 |
| 0916 | SS | 175 | 150 | 150 | 25 |
| 0916 | VLESS | 175 | 157 | 150 | 25 |


“可计算代理上下文”比“主请求 proxy”多，并不是多了有效的视频代理样本，而是某些主请求走 DIRECT 的访问仍包含辅助代理资源。0916 VLESS 的 157 次上下文中，有 150 次主请求 proxy；这一区别在条目表中保留，不把余下辅助上下文并入六业务主统计。

Bilibili 的用户播放确认继续有效，本轮并未否定播放。缺失的是将其主要播放负载解释为经代理传输的路由证据。Hy2 Bing 同样按 DIRECT 实况报告。

## 2. 字节量、分包与交互不表现为同一种变换

下表均为主请求 proxy、严格 TCP 配对访问集合。先对每个条目的重复取中位 log-ratio，再按条目等权汇总；各部署可用条目数不完全一致。

| 批次 | 部署 | 条目n | 包数倍率 | 载荷字节倍率 | burst倍率 | FR倍率 | length JS | IAT JS |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0914-broad | SS | 39 | 1.6603 | 1.0144 | 1.8592 | 1.0329 | 0.31749 | 0.2 |
| 0914-broad | VLESS | 41 | 1.2498 | 1.0569 | 1.0705 | 1.2439 | 0.054306 | 0.072271 |
| 0914-repeat | SS | 13 | 1.6311 | 1.0166 | 1.8256 | 1.0267 | 0.33436 | 0.22625 |
| 0914-repeat | VLESS | 14 | 1.2834 | 1.06 | 1.1727 | 1.2304 | 0.060592 | 0.072237 |
| 0916 | SS | 30 | 1.6383 | 1.0194 | 1.7494 | 1.0508 | 0.34833 | 0.19959 |
| 0916 | VLESS | 30 | 1.2241 | 1.0588 | 1.0768 | 1.2324 | 0.050631 | 0.076912 |


三个批次中，SS 的载荷字节典型增幅约 1.4%–1.9%，但包数约增加 63%–66%、burst 约增加 75%–86%。这支持“在当前观测范围内，宏观载荷量相近而微观分包/方向交互明显改变”的描述，不能升级为字节严格守恒或所有 URL 一律如此。

SS 的 TCP FR 典型增幅约 2.7%–5.1%，远小于其 observed burst 的增幅。这与定义相符：observed burst 会被空载荷控制包分割，FR 只计非空方向段。不能将两者混称为一个方向反转指标。

VLESS 的载荷字节典型增加约 5.7%–6.0%，包数约增加 22%–28%，FR 约增加 23%–24%。但 burst 的方向不统一：0916 的 30 个条目中 21 个中位变换为正、8 个为负、1 个为零。因而总体 burst 中位增长不能写成每个业务都增加。

长度分布 JS 在 SS 下明显高于 VLESS：0916 分别约 0.348 与 0.051。IAT JS 分别约 0.200 与 0.077。它们是固定分箱散度，不是分类准确率，也不是信息泄露量；其大小受采集点、offload、传输状态和应用负载共同影响。

## 3. 先对齐条目集合，再比较 SS 与 VLESS

以下补表只保留两部署主请求均可代理观测的共同条目：0914 broad 为 39 个、repeat 为 13 个、0916 为 30 个。同条目并不意味着相同时间或完全相同响应字节，所以仍不是因果随机对照。

| 批次 | 部署 | 指标 | 条目n | 访问n | Δ中位 | 倍率 | 方向 +/− |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0914-broad | SS | packet_count | 39 | 39 | 0.507 | 1.6603 | 39/0 |
| 0914-broad | VLESS | packet_count | 39 | 39 | 0.22296 | 1.2498 | 39/0 |
| 0914-broad | SS | transport_bytes | 39 | 39 | 0.01428 | 1.0144 | 38/1 |
| 0914-broad | VLESS | transport_bytes | 39 | 39 | 0.057963 | 1.0597 | 39/0 |
| 0914-broad | SS | burst_count | 39 | 39 | 0.62016 | 1.8592 | 38/1 |
| 0914-broad | VLESS | burst_count | 39 | 39 | 0.068153 | 1.0705 | 28/11 |
| 0914-broad | SS | fr_runs | 39 | 39 | 0.032391 | 1.0329 | 29/1 |
| 0914-broad | VLESS | fr_runs | 39 | 39 | 0.21825 | 1.2439 | 39/0 |
| 0914-broad | SS | length_js | 39 | 39 | 0.31749 | — | 39/0 |
| 0914-broad | VLESS | length_js | 39 | 39 | 0.054306 | — | 39/0 |
| 0914-broad | SS | iat_js | 39 | 39 | 0.2 | — | 39/0 |
| 0914-broad | VLESS | iat_js | 39 | 39 | 0.072271 | — | 39/0 |
| 0914-repeat | SS | packet_count | 13 | 65 | 0.48924 | 1.6311 | 13/0 |
| 0914-repeat | VLESS | packet_count | 13 | 65 | 0.23665 | 1.267 | 12/1 |
| 0914-repeat | SS | transport_bytes | 13 | 65 | 0.016481 | 1.0166 | 13/0 |
| 0914-repeat | VLESS | transport_bytes | 13 | 65 | 0.061404 | 1.0633 | 13/0 |
| 0914-repeat | SS | burst_count | 13 | 65 | 0.60189 | 1.8256 | 12/0 |
| 0914-repeat | VLESS | burst_count | 13 | 65 | 0.1449 | 1.1559 | 9/4 |
| 0914-repeat | SS | fr_runs | 13 | 65 | 0.026317 | 1.0267 | 10/0 |
| 0914-repeat | VLESS | fr_runs | 13 | 65 | 0.21622 | 1.2414 | 13/0 |
| 0914-repeat | SS | length_js | 13 | 65 | 0.33436 | — | 13/0 |
| 0914-repeat | VLESS | length_js | 13 | 65 | 0.067274 | — | 13/0 |
| 0914-repeat | SS | iat_js | 13 | 65 | 0.22625 | — | 13/0 |
| 0914-repeat | VLESS | iat_js | 13 | 65 | 0.068178 | — | 13/0 |
| 0916 | SS | packet_count | 30 | 150 | 0.49367 | 1.6383 | 30/0 |
| 0916 | VLESS | packet_count | 30 | 150 | 0.20218 | 1.2241 | 25/5 |
| 0916 | SS | transport_bytes | 30 | 150 | 0.019171 | 1.0194 | 30/0 |
| 0916 | VLESS | transport_bytes | 30 | 150 | 0.057094 | 1.0588 | 30/0 |
| 0916 | SS | burst_count | 30 | 150 | 0.55925 | 1.7494 | 30/0 |
| 0916 | VLESS | burst_count | 30 | 150 | 0.07398 | 1.0768 | 21/8 |
| 0916 | SS | fr_runs | 30 | 150 | 0.04954 | 1.0508 | 30/0 |
| 0916 | VLESS | fr_runs | 30 | 150 | 0.20897 | 1.2324 | 30/0 |
| 0916 | SS | length_js | 30 | 150 | 0.34833 | — | 30/0 |
| 0916 | VLESS | length_js | 30 | 150 | 0.050631 | — | 30/0 |
| 0916 | SS | iat_js | 30 | 150 | 0.19959 | — | 30/0 |
| 0916 | VLESS | iat_js | 30 | 150 | 0.076912 | — | 30/0 |


逐条目报告另外给出 pre、post 各自的跨部署差异。若 pre 已经明显不同，就不能将全部 post 差异归因于代理变换；请同时检查请求数、字节量、时长和路由。

## 4. 六业务内部差异：0916 的全部五次重复

此处使用 300 次 SS/VLESS 主请求代理访问，而非先前保守的 240 次队列。每业务 5 个内容、每内容 5 次重复；降级访问作为真实观测保留，状态见条目报告。未将 Bilibili DIRECT 播放并入代理业务统计。

| domain × activity | 部署 | 指标 | 内容n | 访问n | Δ中位 | 倍率 |
| --- | --- | --- | --- | --- | --- | --- |
| bing.com::search_results_view | SS | burst_count | 5 | 25 | 0.24483 | 1.2774 |
| bing.com::search_results_view | SS | fr_runs | 5 | 25 | 0.028171 | 1.0286 |
| bing.com::search_results_view | SS | iat_js | 5 | 25 | 0.16705 | — |
| bing.com::search_results_view | SS | length_js | 5 | 25 | 0.22233 | — |
| bing.com::search_results_view | SS | packet_count | 5 | 25 | 0.22868 | 1.2569 |
| bing.com::search_results_view | SS | transport_bytes | 5 | 25 | 0.02709 | 1.0275 |
| bing.com::search_results_view | VLESS | burst_count | 5 | 25 | -0.15118 | 0.85969 |
| bing.com::search_results_view | VLESS | fr_runs | 5 | 25 | 0.17768 | 1.1944 |
| bing.com::search_results_view | VLESS | iat_js | 5 | 25 | 0.076546 | — |
| bing.com::search_results_view | VLESS | length_js | 5 | 25 | 0.049697 | — |
| bing.com::search_results_view | VLESS | packet_count | 5 | 25 | -0.049787 | 0.95143 |
| bing.com::search_results_view | VLESS | transport_bytes | 5 | 25 | 0.09688 | 1.1017 |
| developer.mozilla.org::document_view | SS | burst_count | 5 | 25 | 0.47146 | 1.6023 |
| developer.mozilla.org::document_view | SS | fr_runs | 5 | 25 | 0.099091 | 1.1042 |
| developer.mozilla.org::document_view | SS | iat_js | 5 | 25 | 0.18311 | — |
| developer.mozilla.org::document_view | SS | length_js | 5 | 25 | 0.27828 | — |
| developer.mozilla.org::document_view | SS | packet_count | 5 | 25 | 0.34221 | 1.4081 |
| developer.mozilla.org::document_view | SS | transport_bytes | 5 | 25 | 0.019218 | 1.0194 |
| developer.mozilla.org::document_view | VLESS | burst_count | 5 | 25 | 0.012059 | 1.0121 |
| developer.mozilla.org::document_view | VLESS | fr_runs | 5 | 25 | 0.18232 | 1.2 |
| developer.mozilla.org::document_view | VLESS | iat_js | 5 | 25 | 0.066577 | — |
| developer.mozilla.org::document_view | VLESS | length_js | 5 | 25 | 0.029659 | — |
| developer.mozilla.org::document_view | VLESS | packet_count | 5 | 25 | 0.046687 | 1.0478 |
| developer.mozilla.org::document_view | VLESS | transport_bytes | 5 | 25 | 0.062722 | 1.0647 |
| github.com::repository_view | SS | burst_count | 5 | 25 | 0.53324 | 1.7044 |
| github.com::repository_view | SS | fr_runs | 5 | 25 | 0.054559 | 1.0561 |
| github.com::repository_view | SS | iat_js | 5 | 25 | 0.22702 | — |
| github.com::repository_view | SS | length_js | 5 | 25 | 0.37891 | — |
| github.com::repository_view | SS | packet_count | 5 | 25 | 0.52788 | 1.6953 |
| github.com::repository_view | SS | transport_bytes | 5 | 25 | 0.0075208 | 1.0075 |
| github.com::repository_view | VLESS | burst_count | 5 | 25 | 0.044273 | 1.0453 |
| github.com::repository_view | VLESS | fr_runs | 5 | 25 | 0.2103 | 1.234 |
| github.com::repository_view | VLESS | iat_js | 5 | 25 | 0.1022 | — |
| github.com::repository_view | VLESS | length_js | 5 | 25 | 0.10275 | — |
| github.com::repository_view | VLESS | packet_count | 5 | 25 | 0.2294 | 1.2579 |
| github.com::repository_view | VLESS | transport_bytes | 5 | 25 | 0.037052 | 1.0377 |
| wikipedia.org::article_view | SS | burst_count | 5 | 25 | 0.5925 | 1.8085 |
| wikipedia.org::article_view | SS | fr_runs | 5 | 25 | 0.054067 | 1.0556 |
| wikipedia.org::article_view | SS | iat_js | 5 | 25 | 0.19209 | — |
| wikipedia.org::article_view | SS | length_js | 5 | 25 | 0.29825 | — |
| wikipedia.org::article_view | SS | packet_count | 5 | 25 | 0.46334 | 1.5894 |
| wikipedia.org::article_view | SS | transport_bytes | 5 | 25 | 0.020291 | 1.0205 |
| wikipedia.org::article_view | VLESS | burst_count | 5 | 25 | 0.07544 | 1.0784 |
| wikipedia.org::article_view | VLESS | fr_runs | 5 | 25 | 0.20764 | 1.2308 |
| wikipedia.org::article_view | VLESS | iat_js | 5 | 25 | 0.063746 | — |
| wikipedia.org::article_view | VLESS | length_js | 5 | 25 | 0.019014 | — |
| wikipedia.org::article_view | VLESS | packet_count | 5 | 25 | 0.1232 | 1.1311 |
| wikipedia.org::article_view | VLESS | transport_bytes | 5 | 25 | 0.057793 | 1.0595 |
| youtube.com::search_results_view | SS | burst_count | 5 | 25 | 0.88042 | 2.4119 |
| youtube.com::search_results_view | SS | fr_runs | 5 | 25 | 0.04256 | 1.0435 |
| youtube.com::search_results_view | SS | iat_js | 5 | 25 | 0.25181 | — |
| youtube.com::search_results_view | SS | length_js | 5 | 25 | 0.41193 | — |
| youtube.com::search_results_view | SS | packet_count | 5 | 25 | 0.69034 | 1.9944 |
| youtube.com::search_results_view | SS | transport_bytes | 5 | 25 | 0.011766 | 1.0118 |
| youtube.com::search_results_view | VLESS | burst_count | 5 | 25 | 0.35217 | 1.4221 |
| youtube.com::search_results_view | VLESS | fr_runs | 5 | 25 | 0.21706 | 1.2424 |
| youtube.com::search_results_view | VLESS | iat_js | 5 | 25 | 0.097293 | — |
| youtube.com::search_results_view | VLESS | length_js | 5 | 25 | 0.067942 | — |
| youtube.com::search_results_view | VLESS | packet_count | 5 | 25 | 0.37067 | 1.4487 |
| youtube.com::search_results_view | VLESS | transport_bytes | 5 | 25 | 0.033284 | 1.0338 |
| youtube.com::video_playback | SS | burst_count | 5 | 25 | 0.88221 | 2.4162 |
| youtube.com::video_playback | SS | fr_runs | 5 | 25 | 0.04879 | 1.05 |
| youtube.com::video_playback | SS | iat_js | 5 | 25 | 0.2477 | — |
| youtube.com::video_playback | SS | length_js | 5 | 25 | 0.43151 | — |
| youtube.com::video_playback | SS | packet_count | 5 | 25 | 0.68139 | 1.9766 |
| youtube.com::video_playback | SS | transport_bytes | 5 | 25 | 0.010508 | 1.0106 |
| youtube.com::video_playback | VLESS | burst_count | 5 | 25 | 0.30514 | 1.3568 |
| youtube.com::video_playback | VLESS | fr_runs | 5 | 25 | 0.21653 | 1.2418 |
| youtube.com::video_playback | VLESS | iat_js | 5 | 25 | 0.10002 | — |
| youtube.com::video_playback | VLESS | length_js | 5 | 25 | 0.10579 | — |
| youtube.com::video_playback | VLESS | packet_count | 5 | 25 | 0.37426 | 1.4539 |
| youtube.com::video_playback | VLESS | transport_bytes | 5 | 25 | 0.029458 | 1.0299 |


以上业务级数字是内容等权的描述，不能作为新的标签选择依据或重新声称跨内容识别性能。详细的内容间差异及异常重复保留在 35 份 0916 条目页中。

## 5. Hy2：这些大倍率不能解释为协议开销

Hy2 carrier_context_envelope 中，三个批次的载荷字节典型倍率约为 16.0、27.6、21.5，包数典型倍率约为 23.2、33.5、33.0。它们是“相关 pre 逻辑连接集合”对“共享 UDP 载体时间包络”的观测比值，而非已验证的一对一业务载荷膨胀倍数。

共享载体可能包含窗口内非目标逻辑流、背景传输和协议控制负载；索引相关性不提供每个 UDP 包的明文业务归属。即使限定时间包络，业务归属范围仍未变得相同。因此不能写成“Hy2 有二十倍加密开销”，也不能与 TCP FR 或 SS/VLESS 的载荷守恒直接排序。

保留这些数值的用途是展示可观察载体行为、窗口敏感性及后续归因的边界。full/envelope、关联逻辑连接/载体扇出和三种 packet selection 在机器表中可复核，本轮未放宽 Hy2 的严格配对资格。

## 6. 重复性和跨批次结论的强度

重复数据的每条目报告均包含 IQR、MAD、最小/最大值及每次访问原值。0916 SS 的载荷 log-ratio 条目 MAD 中位约 0.00252、包数约 0.0483；VLESS 分别约 0.00394、0.0636。宏观载荷比的重复离散性较小，不意味着所有方向/时间特征也同样稳定。

0914 broad 每个部署仅一次访问，没有重复离散性可估计；其 MAD/IQR 标为缺失，而不是零。五次重复同样不足以给出高精度总体方差、等效结论或大量显著性结论。

跨批次表有 12 对条目级资源重合候选（包含 broad/repeat 两种来源），不等于 12 个独立的共同 URL。Bilibili 候选缺少主业务代理资格；保留下来的数值比较仍未严格匹配采集时长与工作负载，只能作为批次参考。

## 7. 质量、复现与尚未覆盖的内容

本轮解析 23,677 个连接/载体捕获记录，累计 14,894,652 个记录内数据包；不是去重后的全局链路包数。记录原始顺序时间回退 33,965 次，IAT 计算统一按连接内时间排序。没有未知方向或包数解析缺口触发提取错误。

与既有 0916 缓存的 36,000 项标量、0914 repeat 的 36,666 项数值/变换进行交叉核对，均无差异。方向包/字节守恒、FR 恒等关系、直方图计数、唯一键与非负 IAT 校验均通过。

本轮新增及相关单元测试共 19 项通过。首次历史测试遇到旧 pytest 临时目录权限错误，改用本轮输出目录的独立临时目录后通过，不涉及修改原始数据或 conda 环境。

未新增 TLS/SNI 指纹、CDN 厂商识别或解密后的应用字节；IP/端口/SNI 不进入统计特征。已有模型实验没有重训，旧产物不覆盖。序列附表保存每实体前 32 包，完整包序列仍由原始 PCAP 提供，所有标量使用完整选定包集合。

[返回总报告](overall-report.md) · [完整口径](methods.md) · [全条目索引](README.md)
