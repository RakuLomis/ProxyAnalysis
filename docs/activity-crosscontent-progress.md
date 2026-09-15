# 跨内容业务实验：准备阶段实施记录

日期：2026-09-14。

## 已实现

- 新配置 `configs/activity-crosscontent-v1/design.yaml`：采用计划中的四标签和72会话预试验起点，正式960会话仍待预试验后冻结。
- 可运行入口 `python -m proxy_analysis.crosscontent.prepare`：生成内容槽位、可复现随机调度、分区、配置快照和准备状态报告；不启动采集。
- 92个内容槽位：12预试验、48开发、32锁定测试。槽位不是已经核实的URL；未填写内容ID、URL或验证状态。
- 72个预试验计划单元；每时间块的六种协议排列各出现两次，同内容三协议相邻。
- 960个正式草案单元：开发432、未见内容288、未见日期144、联合主测试96。第4块明确标记需要先冻结模型。
- 检查重复槽位、重复内容组、重复URL、域名不匹配、分区角色修改及非法配置。近义查询、转载和URL别名仍需人工语义分组，程序不能自动证明内容独立。
- 输出目录必须不存在，防止覆盖旧调度和证据；保存输入内容及配置摘要。

## 已验证

Pytorch312：Python 3.12.8，pyarrow 24.0.0；现有依赖可用，无安装或升级。

全套测试：125 passed（包含新增9项测试）。验证了计划矩阵、排列均衡、可复现性、错误输入拒绝、未就绪状态及拒绝覆盖。

准备产物位于 `outputs/activity-crosscontent-v1/preparation-01/`：

- `content-slots.json` / `content-slots.parquet`
- `pilot-schedule.parquet`
- `formal-schedule-draft.parquet`
- `design-snapshot.yaml`
- `readiness.json`

所有调度行为 `not_started`，并明确为 `draft_not_capture_authorization`。配置完整也不代表通过采集运行时审计；`capture_ready` 始终为 false，直到后续独立采集验证实现。尚未提供真实日期、节点与会话证据。

## 对应计划状态

| 步骤 | 状态 |
|---|---|
| D01 活动契约 | 已将推荐四标签及动作写入配置，待工程预试验验证动作可执行性 |
| D02 部署契约 | 待采集端位置、节点配置和隔离能力检查 |
| D03 内容清单 | 槽位格式及验证器已实现；真实目标与语义审核未完成 |
| D04 预试验调度 | 生成算法和草案已完成；尚非最终可采集名单 |
| D05/D06 证据及scope | 待采集端接入，不能用本地单元测试代替真实验证 |
| D07 尝试登记 | 本轮只生成计划单元；真实attempt状态机与恢复队列尚未实施 |
| D08及以后 | 未执行；正式预算、模型与采集均未启动 |

## 下一阻塞点

当前仓库检索到的是 TrafficTracer 输出的分析、索引与复现代码，未找到采集控制实现。需要用户提供 TrafficTracer 源码目录或启动入口，以及配置位置（无需在聊天中发送密钥）。

取得入口后：先只读检查是否支持每会话独立代理、干净浏览器起点、共同动作窗口及正片证据；再实施采集适配与attempt登记。目标筛查与日期调度完成后，才执行预试验。

## 复用命令

从仓库根目录运行；每次选择新的输出目录：

```powershell
$env:PYTHONPATH = 'src'
& D:/Tools/Anaconda/envs/Pytorch312/python.exe -m proxy_analysis.crosscontent.prepare --config configs/activity-crosscontent-v1/design.yaml --output outputs/activity-crosscontent-v1/preparation-02
```

填写完整内容槽位JSON后可增加 `--contents <path>`，输入必须保留全部92个槽位及其角色；未填写的正式槽位可继续为空，预试验准备状态仅要求12个预试验槽位的内容验证，但运行时审计仍是单独门槛。

本轮没有修改旧数据、旧分析产物或既有未提交修改，没有启动浏览器、代理、网络采集、模型训练，也没有提交/推送Git。
