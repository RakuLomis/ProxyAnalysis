# 机制引导漂移的历史配置注册

本目录实现三步计划的P1注册与P2训练区机制诊断。使用Pytorch312；元数据登记/统计在CPU，回归拟合与推理强制CUDA。P2不训练业务分类器，不读PCAP、不抽残差视图。

```powershell
conda run -n Pytorch312 python eval/mechanism_guided_drift/collect_instrumentation.py
conda run -n Pytorch312 python -m unittest discover -s eval/mechanism_guided_drift -p "test_*.py"
conda run -n Pytorch312 python eval/mechanism_guided_drift/registry.py
conda run -n Pytorch312 python eval/mechanism_guided_drift/verify_registry.py
```

原始源码锁由`eval/mihomo_protocol_audit/collect_sources.py`生成，本目录只增加固定采集提交的九个记录实现文件，不覆盖原锁。Windows长路径使用显式兼容接口。

输出在`outputs/mechanism-guided-drift-20261003/registry`，报告在`docs/mechanism-guided-drift`。数据/输出/本地计划不随Git同步。报告列明Extend与0914/0916配置差异；effective是适配器option快照，不自动代表协商及内部状态。

G1已获用户确认，P2产物在同根`diagnostics`目录，停在G2。独立授权记录保存在P2契约；P1历史审计的G1待确认状态保持不改。

```powershell
conda run -n Pytorch312 python eval/mechanism_guided_drift/diagnostics.py seal
conda run --no-capture-output -n Pytorch312 python eval/mechanism_guided_drift/diagnostics.py run
conda run -n Pytorch312 python eval/mechanism_guided_drift/verify_diagnostics.py
conda run -n Pytorch312 python eval/mechanism_guided_drift/diagnostic_report.py
```

seal保存角色/输入/代码哈希，run拒绝已封存代码发生变化；复跑不得静默修改契约。W复用100个训练范围及1800内容留一任务；T使用外层训练区共同有效pair，480个内容留一任务。只读取各外层训练post；预检意外显示一个Trojan双侧摘要的例外已披露，不构成外部盲测。严格记录缓存未发现，AnyTLS日志仅离线分层，Hy2保持资格边界。

详细报告为`docs/mechanism-guided-drift/mechanism-diagnostic-report.md`。输出包含权限、拟合台账、CUDA重放、连接/载体表、OOF和内容抽样区间。没有合成样本或新分类收益结论；唯一经验中心候选需G2确认后另写P3完整契约。

## P3 已见五部署 W 实验

G2用户确认后执行P3，独立输出为`outputs/mechanism-guided-drift-20261003/experiment/run-01`。方法只改变经验启动中心，增强输入同时提供给通用Ridge对照；90个MLP、9500个生产Ridge、原8视图预算、CUDA，无E2/T/Hy2分类。完整契约与结果分别见`docs/mechanism-guided-drift/experiment-contract.md`和`formal-results.md`，模型卡为`model-card.md`。

```powershell
conda run -n Pytorch312 python eval/mechanism_guided_drift/p3_prepare.py
conda run -n Pytorch312 python eval/mechanism_guided_drift/p3_engineering.py
conda run --no-capture-output -n Pytorch312 python eval/mechanism_guided_drift/p3_run.py generate
conda run --no-capture-output -n Pytorch312 python eval/mechanism_guided_drift/p3_run.py train
conda run -n Pytorch312 python eval/mechanism_guided_drift/p3_run.py infer
conda run -n Pytorch312 python eval/mechanism_guided_drift/p3_score_adapter.py
conda run -n Pytorch312 python eval/mechanism_guided_drift/p3_verify.py
conda run -n Pytorch312 python eval/mechanism_guided_drift/p3_report.py
```

prepare/engineering/infer/score首次执行有防覆盖门；generate/train可按同一seal及完整文件哈希恢复。score_adapter只修复JSON NumPy标量序列化，不改冻结scorer、预测、统计或模型。旧实验保持只读。报告生成仅消费固定结果，不重训或选参数。

P3完成后冻结。D2真配的F1点估计为0.728858，但相对D0/D1/M0的家族校正区间跨零；相对D2group为正。不能据此宣称经验中心可靠优于旧中心或强post监督，亦不能解释为精确协议K。
