# Hy2 资格阶段结果与待确认事项

本轮已执行HFC0、HFC1及HFC2–HFC3的证据审计，未通过训练前资格门。没有提取新六维摘要、生成样本或训练分类器，不能报告Hy2业务分数。旧FSC产物哈希保持不变。

## 已确认

- 固定100访问、25内容、五业务，重复1/2/4/5；既有五折内容身份映射核对通过。
- 100次主目标均proxy，主请求索引各对应一个不同carrier。窗口内索引路径没有发现trace路径遗漏，已索引捕获文件存在。
- 扫描全部538历史尝试的有界trace，不只看100个候选。
- 新增审计及既有carrier路径共7项回归测试通过。系统临时目录权限错误通过全新工作区测试目录解决，未改测试断言。首轮工程脚本错误地把视频规范ID当URL映射折，断言停止；已改为原规范内容ID并保留run-01失败contract，正式审核在run-02，未重分折。

## carrier成员：可补充的信息与仍缺的证据

主carrier的trace绑定成员共5520，请求关联connection-index成员1526，差3994；flow-index覆盖全部5520成员，未发现trace成员缺出flow-index。

所以“缺请求索引成员”不等于原始数据丢失，也不是必须补采。它说明旧请求筛选的pre范围不够：若后续继续，需要从flow-index/有界trace给出的完整成员及raw/tun.pcap重建入口，而不能直接复用请求级pre特征。此扩展仍属于已有原始数据提取，但重建后要重新验收。

98个主carrier在全部保存尝试中找不到创建事件，另外2个有创建证据；4次访问涉及4个缺少connect起点的绑定成员。没有capture-start活跃成员快照或等价完整历史链时，无法排除窗口前已有成员。

## 跨访问引用不等于已证实训练/测试泄漏

非本访问的carrier引用台账共139行，其中logical_carrier_bind共0条；引用落在其他100候选访问中的数量为5。

这些引用必须按类型区分。定点例子显示主carrier在随后的VLESS/SS尝试中仍有path_update/close；另有5条引用位于其他候选Hy2访问，均为path_update/close而没有新增logical_carrier_bind。它们证明生命周期可以超出当前访问，但不自动证明另一个业务复用了同一carrier的逻辑流量。不能把初步gate中的carrier_referenced_other_attempt解释成已证实同一flow进入训练和测试，也不能声称已证明完整隔离。五条跨候选生命周期引用必须在后续原始包范围审计中处理，不能忽略或直接随机分折。

## 时间窗口

manifest保存独立UTC session起止，capture-context保存单调时钟capture ready/stop。已有会话边界可作为独立粗窗口候选，但精确捕获交集的UTC映射尚未验证。本轮未用pre包起止、流量相似度或测试表现推算窗口。

若改为“会话控制边界内实际捕获到的流量”作为主观测，需要明确两侧采集覆盖可能不同，并登记为窗口观测任务，不能称为完全闭合载体转换。不得静默改为pre envelope。

## 一次降级访问不应直接判作业务失败

Wikipedia的Hypertext_Transfer_Protocol，重复1，session a293b581-ca2d-469f-acba-c55995635d40：navigation passed、HTTP 200，activity因CRITICAL_RESOURCE_FAILURE_BURST降级。既有effective_label_valid为false且无人工覆盖。

鉴于用户允许降级访问，本次将其列为待确认，而不是因degraded字段自动删除。保留它需要登记有效性口径：导航到目标文章成功即可，关键子资源失败作为访问状态。不能替换为重复3以凑齐样本。

## 建议用户决定

推荐不补采，下一步先单独批准一个**窗口观测版HFC-W**：用完整flow-index成员重建pre，使用外部session边界及实际捕获覆盖；如实保留98个carrier起点未知与成员carry-in不确定性。先做原始包覆盖审计，再冻结更新后的方法，不立即训练。

这会将主张从“已验证完整成员的载体转换”收窄为“同次访问窗口两侧可观察摘要的增广”。同时建议接受上述HTTP 200文章访问的有效标签并保留降级标记。若用户坚持原严格闭合资格，则本轮停在这里，不可用现有证据强行通过。

## 文件

- 可复用命令：Pytorch312运行`eval/hy2_carrier_calibration/prepare.py`，随后`refine.py`。
- 初步机器台账及复核：`outputs/hy2-carrier-calibration-0916/run-02/`。
- 主要文件：candidate-visits、carrier-registry、membership、window-audit、source-hashes、historical-trace-sources、cross-attempt-references、activity-review、qualification-gate、qualification-review、review-provenance。
- 初步审核说明：[measurement-audit.md](measurement-audit.md)。以本报告对初步警告的解释为准，原始警告保留供追溯。

状态：等待用户确认资格口径，不是实验负结果。未使用CUDA训练，因为当前工作只有元数据和trace审核；后续模型拟合/推理仍要求CUDA。
