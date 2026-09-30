# 2026-09-23 定点诊断

环境：Pytorch312。仓库根目录执行：

```powershell
D:/Tools/Anaconda/envs/Pytorch312/python.exe eval/protocol_normalization/run_targeted_diagnostics.py all
```

可选阶段：`evidence`、`completeness`、`runs`、`report`。每次执行先验证输入契约；重跑覆盖本次独立 run 的派生产物，不修改原 run、PCAP 或分类结果。

```powershell
$env:PYTHONPATH='src'
D:/Tools/Anaconda/envs/Pytorch312/python.exe -m pytest tests/unit/test_targeted_diagnostics.py tests/unit/test_protocol_normalization_ledger.py tests/unit/test_tcp_state.py tests/unit/test_tcp_transport.py tests/test_itemwise_statistics.py -q -p no:cacheprovider --basetemp <新的工作区临时目录> --junitxml outputs/protocol-normalization-targeted-diagnostics-0914-0916/run-01/tests.xml
D:/Tools/Anaconda/envs/Pytorch312/python.exe eval/protocol_normalization/run_targeted_diagnostics.py report
```

新产物：`outputs/protocol-normalization-targeted-diagnostics-0914-0916/run-01/`。

报告：`docs/protocol-normalization/targeted-diagnostics-20260923/report.md`。

所有连接/访问 ID、协议标签、跨侧联合差值与资格信息仅用于本轮离线审计和测量，不是单侧模型输入。本入口没有训练功能。

`S_valid` 是同一方向两侧有效；`S_both` 额外要求该方向两侧闭合连续；`S_all4` 要求同连接四条方向侧记录均候选。空子集访问不作零字节填补。候选仍不是成功交付证明。

段比较要求两侧两个方向均有效；`first/interior/last/singleton` 为互斥的侧内段位置，不是协议阶段或两侧段对应。

未来如修改口径，应新开 run 并同步配置、代码与测试；不能在同一契约下悄悄换阈值或主集合。
