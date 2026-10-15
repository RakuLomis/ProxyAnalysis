# 同连接联合响应实验

独立新实验，不修改旧P-small、不读取PCAP。默认Python为
`D:/Tools/Anaconda/envs/Pytorch312/python.exe`，训练和推理必须CUDA float64。

已批准计划：`plan/connection-joint-response-business-plan-20261010.md`。
新产物：`outputs/connection-joint-response-20261010/run-01/`。

## 执行顺序

在仓库根目录使用Pytorch312解释器运行：

```powershell
python eval/connection_joint_response/inventory.py
python eval/connection_joint_response/prepare.py
python eval/connection_joint_response/tests.py
python eval/connection_joint_response/diagnostics.py predict
python eval/connection_joint_response/diagnostics.py score
python eval/connection_joint_response/verify.py
python eval/connection_joint_response/report.py
python eval/connection_joint_response/learning_inventory.py
python eval/connection_joint_response/formal.py pilot
```

已完成阶段不能重复运行覆盖。所有核心代码、输入、合同及工作包有SHA封存。
数值先导只读取外折0的12角色，不评分H。先导共384分类器，计入1920总上限。
学习代码扩展以追加清单封存，不改变最初科学合同或准备阶段代码。

`formal.py remaining`必须在先导数值通过并核对实际预算后启动；它不自动由先导触发。
全部11520预测封存之前，H标签读取被拒绝。完整统计与报告阶段须继续按计划实现、验收，初始验收不是业务实验完成标志。

## 权限与口径

只有可信装包器打开完整已封存原生缓存；学习器只接收角色工作包。
source pre和post独立排序，不共享访问ID；group只保留内容token及侧内质量；
marginal连内容token也不保留。目标U两侧不得进入学习，H查询仅含post数值。

KG用内容内边际外积，不使用循环donor。I是边际乘积表示参照，不是物理流量生成。
FR保持正payload方向段定义，E保持正新字节事件定义，不能解释为协议chunk。
O1暂停，物理post资格未通过；不能把本轮离线结果写成无索引在线攻击。
