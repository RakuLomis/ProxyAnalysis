# P-small单侧观测验证

阶段A前置实现，固定旧六臂及96维口径，不新增分类方法。

```powershell
& 'D:/Tools/Anaconda/envs/Pytorch312/python.exe' -m eval.p_small_observation_validation.run --metadata-only
& 'D:/Tools/Anaconda/envs/Pytorch312/python.exe' -m eval.p_small_observation_validation.run --tests-only
```

默认入口只检查元数据、旧模型哈希与CUDA可用性，并运行内存合成TCP测试；不打开PCAP、不拟合、不生成模型预测。每次正式前置运行须使用新的`--out`，不得覆盖旧运行。

核心计算代码在`src/proxy_analysis/observation/`，提取器只有端点与数值窗口参数，不接收标签、pair或浏览器数据。它保留连接生命周期歧义、窗口冷启动唯一字节、原FR、新字节游程和失败状态。背景/失败/未配对有payload连接不能静默删去。

`--pilot`和`--full`目前明确拒绝执行。完成A06的起点、端点、时钟与读盘预算确认后，再登记受控原始数据入口。合成测试通过不等于真实PCAP重建、完整固定窗或整项阶段A已经通过。

B/C不是本入口的后续自动阶段，也没有模型训练代码被调度。旧结果、旧窗口和旧源码均为只读依赖。
