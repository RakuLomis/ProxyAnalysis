# DP-GAN1-M v1

独立实现根；不覆盖旧JAT1、P-small或其他历史实验。批准合同在
`plan/DP-GAN1-M-v1-local-implementation-plan-20261016.md`。

## 计算与权限

- 新模型、投影、条件一阶/原始二阶矩、凸头及推理均为CUDA float64。
- Adam：最多32模型、8 streams、CUDA Graph；每模型独立状态及裁剪。
- 三类训练工作器分别在P/G/E独立进程运行。G只消费独立匿名边际、组中心与边际矩；E不读取pre。
- 可信生产器按角色先过滤native数值，保存整数直方图计数，不倒算标准化教师张量。
- 凸头求解沿用明确预算的安装版LBFGS；原W上的L2、bias不罚、原坐标梯度验收。
- 总活动保护24小时，先导保守估计不超过19.2小时才可进入完整矩阵。未运行项不是β0。

## 阶段命令

使用`D:/Tools/Anaconda/envs/Pytorch312/python.exe`；下面是顺序，不是失败后的自动重试指令。
所有合同、模型与阶段封存只写一次。已运行实例应先读progress、failures与阶段seal。

1. `contract.register()`、`prepare.prepare()`：P0，已绑定实例不得再次注册。
2. `fold_checks.py`：元数据级嵌套内容/部署隔离核对。
3. `tests.mathematical()`、`cuda_checks.py`：合成数学、权限及CUDA重放。
4. `p1.py`：固定12任务、24锚点、232凸头、88条正式2000步路径；不读取query。
5. `activity_audit.py`、`selection_checks.py`、`inference_check.py`：补充活动计账、选择规则及post-only导出核对。
6. `cost.py`：合成352行/22单元形状计时及完整范围预算预测。未通过则停下请求确认，不删任务。
7. 仅P1全部验收通过后运行`run.py`：完整源内矩阵→全源内模型封存→源query预测封存→双政策选择→完整外层模型封存→H-post预测封存→H标签评分→独立复核。

## 方法口径

这里没有训练二分类GAN判别器。有限二次矩对偶被消去后，以既定矩差平方优化；该实现不声称精确TCP流量生成。
P/G逆锚点为十块Ridge；动态分支为96→8→96低秩ReLU残差及raw单纯形投影。静态参照无残差。
最终推理只有post输入，不接收协议条件、content/visit索引、pre或真实标签。
PURE和FUSE分别选择；β0精确引用B0，β1引用纯分支。C代价只作完整评价后的实践筛查，不按H回退。

P0/P1输出不是业务结论。仅完整H评价才能形成本版本分类结果；既有H历史接触不因新封存消失。
