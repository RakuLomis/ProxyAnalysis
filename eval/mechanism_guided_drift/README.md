# 机制引导漂移的历史配置注册

本目录目前只实现三步计划的P1。使用Pytorch312，元数据登记不训练模型、不读取PCAP；未来正式训练和测试仍要求CUDA。

```powershell
conda run -n Pytorch312 python eval/mechanism_guided_drift/collect_instrumentation.py
conda run -n Pytorch312 python -m unittest discover -s eval/mechanism_guided_drift -p "test_*.py"
conda run -n Pytorch312 python eval/mechanism_guided_drift/registry.py
conda run -n Pytorch312 python eval/mechanism_guided_drift/verify_registry.py
```

原始源码锁由`eval/mihomo_protocol_audit/collect_sources.py`生成，本目录只增加固定采集提交的九个记录实现文件，不覆盖原锁。Windows长路径使用显式兼容接口。

输出在`outputs/mechanism-guided-drift-20261003/registry`，报告在`docs/mechanism-guided-drift`。数据/输出/本地计划不随Git同步。报告列明Extend与0914/0916配置差异；effective是适配器option快照，不自动代表协商及内部状态。

G1未确认前不执行P2。没有机制回归、合成样本或分类增益结论。
