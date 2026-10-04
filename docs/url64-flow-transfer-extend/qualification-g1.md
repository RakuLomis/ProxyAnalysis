# Broad URL 迁移实验资格检查

日期：2026-10-02。当前结论：原定完整 64 类代理访问任务未通过入口资格，停在 G1 等待任务范围确认，未提取新包级特征、未训练或测试分类器。

仓库原有阶段成果已先行提交并推送，提交为 `6e381d0`。本报告及新审计脚本是此后本地新增产物；不改写 Extend v3 的冻结结果。

## 主要发现

重新读取本批 Broad 的全部 384 次访问，每种部署各 64 次。六部署的主文档路由一致：同一组 41 个 URL 成功走代理，同一组 23 个 URL 成功走 DIRECT。因此，不能将完整 64 类直接描述为代理流量分类。某次 DIRECT 页面访问仍可能存在代理背景连接；这些背景连接不能替代该页面的代理访问证据。

判定使用成功的目标或导航最终 URL 的 Document 请求及其关联连接的 egress 证据，不根据 URL 所属国家、节点名称、SNI 或整个捕获中是否存在代理流量来推断。41 类只代表主文档成功走代理，不表示页面所有资源都走代理。

| 部署 | Broad 访问 | 主文档代理成功 | 主文档 DIRECT 成功 | 代理访问中有排他 TCP 候选 | 非重合四重复 Content 候选内容 |
|---|---:|---:|---:|---:|---:|
| SS | 64 | 41 | 23 | 41 | 24 |
| VLESS | 64 | 41 | 23 | 41 | 22 |
| Trojan | 64 | 41 | 23 | 41 | 24 |
| VMess | 64 | 41 | 23 | 41 | 24 |
| AnyTLS | 64 | 41 | 23 | 0 | 20 |
| Hy2 | 64 | 41 | 23 | 0 | 26 |

最后一列仅为校准池元数据候选：Content 请求及最终 URL 不与 Broad 已观察别名重合，原路由审核为 proxy_success，代际一致，且重复 1、2、4、5 齐全。尚未选择六个内容，不代表配对、原始字节覆盖或共享载体资格已通过。校准池扫描发现两个历史访问缺失 summary，已保留缺失状态而不是填充为通过。

## 本批共享承载证据

新读取 Broad flow-index 的 carrier ID、adapter instance 和协议，建立承载实体成员表，并与既有 Content、Detailed 实体台账比较。此检查不以 SNI 或单独五元组作为物理连接身份。

- Hy2 有一个相同承载实体关联 63 次 Broad 访问，其中包含全部 41 次主文档代理成功访问及 22 次 DIRECT 访问。这是本批 Broad 的证据，不是沿用旧 Content 的排除理由。
- AnyTLS 有一个承载实体同时关联 Google 首页和 example.com 两次代理访问。因此它的访问独立性需要明确处理；仅有 W 访问窗口不能自动宣称物理载体独立。
- SS、VLESS、Trojan、VMess 在当前 carrier 实体键检查中未出现 Broad 跨访问共享。这仍不能替代原始捕获文件身份、TCP 实例及时间重叠审核。
- AnyTLS 和 Hy2 的代理连接均为共享绑定，当前不能把加密 post 按 SNI 拆成排他 TCP 配对。不要把应用请求复用与物理 carrier 复用混为一谈。

上述台账检查尚不是最终 C/U/H 隔离证明。未发现跨角色实体键交叉也不等于原始文件和连接绝无重复。

## 连接级候选规模与边界

在 41 类主文档代理成功访问内，元数据满足代理、排他绑定、完整 post TCP、非共享 post flow 的记录数分别为 SS 3106、VLESS 3681、Trojan 3653、VMess 3730。这些是 flow-index 候选记录数，不是最终去重 TCP 实例数或模型样本数。

许多候选记录尚未关联到 page connection，可能属于捕获背景。当前没有按候选数筛除 URL，也没有把所有捕获连接当成具有独立业务标签的训练样本。后续必须登记仅从 post 与允许的访问索引即可执行的选择规则；不能根据测试 pre 配对是否成功来选取容易的 post。

SNI 未在本轮抽取，不参与资格筛选或模型。资源请求主机名不能冒充 TLS SNI。缺失 SNI 不能自动剔除连接。

## 已完成与尚未完成

| 计划项 | 本轮状态 |
|---|---|
| P00 URL 台账 | 已登记 64 个标签及观察到的最终 URL 别名，未发现不同标签的别名碰撞；中间重定向和额外语义等价尚待检查 |
| P01 路由及窗口 | 384 次重新检查主文档路由、代际、选择和 capture coverage 状态；后面三项均 384 次通过元数据检查，但未做 W 时钟锚点和包级重放 |
| P02 校准池 | 已对 1050 次 Content 的可用 summary 做别名排除及四重复候选计数；未冻结 C |
| P03 身份隔离 | 已建立 carrier 成员表，发现 Broad 共享关系；未完成原始文件哈希、TCP 实例和最终角色连通分量审核 |
| P04 flow 资格 | 已保存排他 TCP 候选、请求关联和缺失状态；post-only 选择器未实施 |
| P05 类别完整性 | 已确认六部署同一 23 类为 DIRECT，完整 64 类代理资格失败；未擅自建立 41 类模型 |

这里是 P00–P05 的元数据预检查及提前触发的 G1，不是宣称所有阶段的完整验收已通过。发现任务定义层面的阻断后，不进行全量 PCAP 扫描或 CUDA 训练。此次 CPU 元数据工作不改变后续模型训练和测试使用 CUDA 的要求。

## 需要确认的下一步

建议另行登记一个共同 41 类候选任务，首先在 SS、VLESS、Trojan、VMess 四个部署完成剩余身份、窗口和 post-only flow 资格审核。保持父访问整体隔离，保留访问级与连接级对照，不能将同次访问的子连接拆进训练和测试。

这会改变原计划的类别数及 A_all 的部署范围，必须获得确认。AnyTLS 作为共享 carrier 处置支线，Hy2 暂不进入独立 flow 分类；它们不是被证明没有业务信息，而是当前单位和独立性条件不满足。若以后将它们加入访问级路线，需要另外确认组件划分和可比预算。

若坚持完整 64 类而不补采，只能另行定义包含 DIRECT 与代理混合路由的闭集页面识别任务。那不能直接回答 64 类代理漂移增广是否有效，也不能把 DIRECT 样本当作指定协议的 post。当前不自动采用这一替代问题。

仅确认采用 41 类后，才继续完成剩余资格检查、冻结 C/U/H 权限和预算；不是确认后立即训练。每个 URL 每部署只有一次访问的限制仍然存在，多条子连接不会增加独立访问次数。

## 复现与产物

从仓库根目录运行：

```powershell
D:/Tools/Anaconda/envs/Pytorch312/python.exe -m unittest discover -s eval/url64_flow_transfer -p test_*.py
D:/Tools/Anaconda/envs/Pytorch312/python.exe eval/url64_flow_transfer/qualify.py --output outputs/url64-flow-transfer-extend/run-02
```

脚本拒绝覆盖已经完成的输出目录。现有结果位于 `outputs/url64-flow-transfer-extend/run-01/`：

- `status.json`：部署计数、停止状态、待检查项及来源指纹。
- `label-registry.json`、`observed-aliases.json`、`alias-collisions.json`：标签和别名证据。
- `broad-visits.parquet`、`request-route-evidence.parquet`：逐访问和逐主文档路由证据。
- `flow-candidates.parquet`：候选记录、承载键、关联和缺失状态，不含端点明文。
- `calibration-candidates.parquet`：逐 Content 候选及排除状态。
- `carrier-components.json`：共享实体的访问成员。
- `metadata-hashes.json`：本次读取的元数据文件指纹；不是 PCAP 内容哈希。

数据集、输出和本地 plan 继续不推送。脚本未修改历史分类器、生成器、旧契约或原始数据。

验证结果：四项合成单元测试通过，覆盖 URL 身份保留、背景代理连接不覆盖 DIRECT 主文档证据、共享 carrier 排除及窗口状态。另对 384 次访问逐一回查已保存的成功主文档连接路由，与访问级结论全部一致。本轮登记 2968 个读取的元数据文件指纹。这些测试不替代上文尚未完成的包级审计。

## DIRECT 类别清单

以下 23 个 URL 在六部署均为主文档 DIRECT 成功，不应因捕获中存在其他代理连接被重新标注为代理访问：

```text
https://www.bilibili.com/
https://www.bilibili.com/video/BV1hu4m1P7Mu/
https://www.bilibili.com/video/BV1HEf2YWEvs/
https://www.gov.cn/
https://www.baidu.com/
https://www.12306.cn/index/
https://map.baidu.com/
https://gitee.com/
https://www.csdn.net/
https://www.zhihu.com/
https://news.sina.com.cn/
https://news.qq.com/
https://news.163.com/
https://www.jd.com/
https://www.taobao.com/
https://www.mi.com/
https://v.qq.com/
https://www.iqiyi.com/
https://www.youku.com/
https://www.douyu.com/
https://www.huya.com/
https://music.163.com/
https://weather.com/
```
