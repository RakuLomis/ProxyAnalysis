# O1先导入口与范围

用户批准的24文件O1先导由独立入口执行，原metadata入口及其封存代码不变。

```powershell
& 'D:/Tools/Anaconda/envs/Pytorch312/python.exe' -m eval.p_small_observation_validation.pilot --out outputs/p-small-observation-validation-20261010/pilot-02
& 'D:/Tools/Anaconda/envs/Pytorch312/python.exe' -m eval.p_small_observation_validation.pilot_verify --out outputs/p-small-observation-validation-20261010/pilot-02
```

第一条为已执行运行的记录，不是建议重新扫描。入口拒绝覆盖；新读取须满足审批预算。第二条只复核产物，不读取PCAP。范围归因入口`pilot_diagnostics`同样拒绝覆盖，且不读取原始流量。

pilot-02完成24文件单遍提取，产物完整性验收通过；15访问有旧窗口技术候选，9访问因未证实的midstream epoch资格失败，先导闸门未通过。1235条旧共同合格TCP连接十统计全部精确复现。旧W中114591条不相交事件全部为SS UDP，不属于TCP提取范围。

报告：[O1先导报告](../../docs/p-small-observation-validation/o1-pilot-report-20261010.md)。本轮0训练、0评分、0模型推理，不授权O2、full480或后续B/C。
