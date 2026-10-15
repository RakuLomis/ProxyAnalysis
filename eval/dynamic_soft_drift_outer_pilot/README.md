# 动态软约束漂移外层优化源内先导

独立版本，只改变外层优化政策。固定f0全部12角色、O-DP/O-TP/O-DG共36轨迹，保持原科学目标和CUDA float64内层后端。不存在最终业务训练、H/U查询或评分入口。

## 执行

在仓库根目录用Pytorch312运行：

```powershell
D:/Tools/Anaconda/envs/Pytorch312/python.exe eval/dynamic_soft_drift_outer_pilot/run.py unit-test
D:/Tools/Anaconda/envs/Pytorch312/python.exe eval/dynamic_soft_drift_outer_pilot/run.py prepare
D:/Tools/Anaconda/envs/Pytorch312/python.exe eval/dynamic_soft_drift_outer_pilot/run.py pilot
```

prepare只允许一次，封存新合同、源内角色和读取清单，检查全1初始缓存兼容性，生成P/G尺度。pilot不自动重试或恢复失败运行，不读取旧学习终态；目标候选拒绝不等于数值失败，后者停止全项先导。完成后自动生成报告和独立核验。既有运行只读。

## 固定政策

M=1+A/s；q投影至[0,2]；尺度位移上限0.1；8次alpha=1至1/128回溯；f/v双档下降、方向及数值分辨保护；最多20次接受更新、每轨迹40个trial-q，活动计算4小时上限。

驻点按原坐标投影梯度不超过1e-3判定。有限改进只允许正常20接受更新终态判定，需目标改善至少1e-4乘max(1,起点目标绝对值)，并且f/v原投影残差各下降至少80%。资源、线搜索、小步长和信号停止不升级为成功。

输出：outputs/dynamic-soft-drift-outer-pilot-20261013/run-02。报告：docs/dynamic-soft-drift-calibration/outer-pilot-20261013/run-02。批准计划：plan/dynamic-soft-drift-outer-optimization-pilot-plan-20261013.md。

run-01在启动时发现verify.py语法错误，在进入先导阶段前退出，未发生新拟合或q更新。其合同、日志与源码快照保留；run-02只修复启动语法、补齐全部模块编译检查并使用新输出目录，不改科学或优化政策。

本轮只判断数值程序质量，不证明业务增量。进入新的正式业务矩阵必须另行确认。
