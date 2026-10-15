# 锚点资格与投影误差诊断结项

只读使用已完成的C预测和评分，独立重放资格、距离、Q90、缩放、投影和误差闭合。没有任何fit或H查询入口，不导入父rules、project或score。

使用Pytorch312 CUDA float64：

```powershell
& D:/Tools/Anaconda/envs/Pytorch312/python.exe -u eval/anchor_guard_closeout/run.py --preflight
& D:/Tools/Anaconda/envs/Pytorch312/python.exe -u eval/anchor_guard_closeout/run.py
```

CSV由捆绑Node与artifact-tool从数值中间表分块导出，不建立Excel模型。先执行技能提供的mark_artifact_operation_started.mjs创建标记一次，再通过指向捆绑依赖的node_modules目录运行csv_export.mjs。全部CSV导出后执行：

```powershell
& D:/Tools/Anaconda/envs/Pytorch312/python.exe -u eval/anchor_guard_closeout/run.py --verify
```

新运行：outputs/invariant-anchor-diagnostic-closeout-20261012/run-01。
报告：docs/invariant-anchor-guarded-drift/closeout-20261012。

父运行、原资格及stop_no_supported_protection_target保持不变。遇到数值不一致保留failure.json并暂停；不能将放宽门限称为修复。所有计算产物附有成员、质量和坐标定义，CSV空格不填零。
