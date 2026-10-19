# 前向决策空间先导模型说明

任务：四已见TCP部署SS、VLESS、Trojan、VMess的六业务源内伪目标分类。不是实际H、六协议统一识别或外部部署验证。

输入：96维访问直方图。输出：六类log概率。分类推理仅消费post，先按冻结P-small尺度变换，再通过96到6线性模型；不运行生成器，不读取pre、IP、端口、SNI、标签或访问键。

训练辅助：原JA1前向仿射加96到8到96 ReLU残差，共1544个新生成参数；2000步单一Adam配置。最终LR名义582参数，类别对比坐标485自由参数。P/G共享原P-small锚点，差异仅在新增精确/组级监督。

源内query-pre仅作封存后离线诊断。生成的协变量可能含负箱、块质量偏差，不是合法流量生成器。没有神经GAN判别器，不宣称协议语义不变。

当前候选未通过预定推进屏，未获推荐替代P-small；尚无实际H成绩。详细指标及限制见[结项分析](F:/Program/VSCode/MyGit/ProxyAnalysis/docs/decision-aware-forward-drift-20261017/complete-results-analysis-20261017.md)。
