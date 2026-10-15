# P3封存接口独立结项

此入口仅修复历史P3的路径收集接口，并核验已登记的全部回退。

历史错误为`ROOT[e['base_path']]`；新接口使用`root / e['base_path']`，同时处理可选残差路径和路径去重。历史v3代码不改写，原工程代码封存及停止记录保留。

输入只包括run-01的冻结P-small、其已登记原模型来源，以及run-02的合同、资格决定和已有端点。禁止调用训练器、读取实际H/U数据、改变资格决定或开放Stage B。出现任一启用决定时直接停止，不自动训练。

默认输出为`outputs/post-input-associated-representation-20261014/run-03/`。入口拒绝覆盖已有输出；不能通过重跑此命令清除旧失败记录。

```powershell
& 'D:\Tools\Anaconda\envs\Pytorch312\python.exe' -B -u 'eval\post_associated_p3_closeout\run.py'
```

程序顺序为历史字节哈希快照、独立P3封存、CUDA合成输入回退重放、历史哈希复核、结项封存。75行合成96维直方图输入仅核验接口，不作为实际业务样本或性能结果。

独立验收入口为`eval/post_associated_p3_audit/verify.py`。它在本程序成功之后核对结项、模型及修复代码封存、全部720条端点和零新增训练计数，不读取H/U、不计算F1。

成功状态`closed_all_exact_fallback`表示本次工程结项完成；`formal_complete=false`、`H_scored=false`仍保留。不要运行原训练总调度器来完成此次修复，也不要将此状态解释为获得新的业务增量。
