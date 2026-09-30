# 协议规范化测量入口

在仓库根目录使用 Pytorch312：

```powershell
D:/Tools/Anaconda/envs/Pytorch312/python.exe eval/protocol_normalization/run.py inventory
D:/Tools/Anaconda/envs/Pytorch312/python.exe eval/protocol_normalization/run.py measure
D:/Tools/Anaconda/envs/Pytorch312/python.exe eval/protocol_normalization/run.py evaluate
```

也可运行 `run.py all`。只执行协议证据审计、严格 TCP 配对的 O/F/U 字节测量、多尺度方向段及报告，不进行模型训练或解密。

产物：`outputs/protocol-normalization-0914-0916/run-01/`。
报告：`docs/protocol-normalization/measurement-report.md`。

- O：观测载荷字节；F：删除完全重传包；U：唯一载荷序号区间并集。
- 26 条方向侧记录因序号/epoch 歧义或重叠载荷冲突而不输出精确 U；具体数量以 measurement-quality.json 为准。
- 尚未生成 K（协议校正）特征，当前暂停于历史配置确认门，不是 N13 分类放行。
- 检查点验证捕获哈希；改变数值定义时必须增加 measure.VERSION 并重建本轮新缓存，或使用新 run 目录。绝不能覆盖旧实验产物。
- 新字节事件表和连接标识属于审计/测量数据，不是可直接送入分类器的列清单；后续必须执行 N12 权限导出。
- 所有 payload 内容仅在内存内做重叠一致性检查，不持久化。

回归测试使用一个新的工作区临时目录，避免旧系统 pytest 临时目录权限影响：

```powershell
$env:PYTHONPATH='src'
D:/Tools/Anaconda/envs/Pytorch312/python.exe -m pytest tests/unit/test_protocol_normalization_ledger.py tests/unit/test_tcp_state.py -q -p no:cacheprovider --basetemp <新的工作区临时目录>
```
