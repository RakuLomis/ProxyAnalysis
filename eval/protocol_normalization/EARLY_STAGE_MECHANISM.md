# 早期阶段机制候选复用入口

环境为 Pytorch312。独立数据目录：`outputs/vless-early-stage-mechanism-0914-0916/run-01`。

```powershell
D:/Tools/Anaconda/envs/Pytorch312/python.exe eval/protocol_normalization/run_early_stage_mechanism.py tables
D:/Tools/Anaconda/envs/Pytorch312/python.exe eval/protocol_normalization/run_early_stage_mechanism.py models
D:/Tools/Anaconda/envs/Pytorch312/python.exe eval/protocol_normalization/run_early_stage_mechanism.py sample
D:/Tools/Anaconda/envs/Pytorch312/python.exe eval/protocol_normalization/run_early_stage_mechanism.py sources
D:/Tools/Anaconda/envs/Pytorch312/python.exe eval/protocol_normalization/run_early_stage_mechanism.py parse
```

`sources` 只获取精确版本官方源码，不执行下载的代码；`parse` 只读取已冻结清单里的捕获及对应保留日志。文件哈希在解码前验证。更换口径/样本规则应新开 run，不修改已经冻结的清单。不会扫描其他 PCAP。

测试后生成报告：

```powershell
$env:PYTHONPATH='src'
D:/Tools/Anaconda/envs/Pytorch312/python.exe -m pytest tests/unit/test_early_stage_mechanism.py tests/unit/test_targeted_diagnostics.py tests/unit/test_protocol_normalization_ledger.py tests/unit/test_tcp_state.py tests/unit/test_tcp_transport.py tests/test_itemwise_statistics.py -q -p no:cacheprovider --basetemp <新的工作区临时目录> --junitxml outputs/vless-early-stage-mechanism-0914-0916/run-01/tests.xml
D:/Tools/Anaconda/envs/Pytorch312/python.exe eval/protocol_normalization/run_early_stage_mechanism.py report
```

`all` 顺序运行所有测量阶段；首次运行仍需先准备测试 XML，或在阶段执行后单独运行 `report`。报告：`docs/protocol-normalization/early-stage-mechanism-20260923/report.md`。

本轮存在描述性 LAD 回归拟合，但不存在分类器拟合。新五折按内容 URL 的哈希身份分组，不冒称复用旧业务分类折；同访问所有连接与同内容重复/部署保持同折。

事件图谱展示固定前 12 段与全程，不用 pre/post 相似度挑切点。语法解析先要求从 SYN 起点连续重组并建立初始 Hello；后续记录是语法可观察单位，不等于全程都属于同一加密层。原始载荷不落盘。

当前证据只有 E0/E1，没有 E2 的语义阶段标志，所以没有分阶段特征文件和 K。`post_only_phase` 明确返回 unavailable，不伪装成有效规范化器。不得将这些离线配对统计表直接作为单侧推理输入。
