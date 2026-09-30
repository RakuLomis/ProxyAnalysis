# P5–P7 阶段实施报告：计数分解、冻结模型诊断与基线确认门

日期：2026-09-18。状态：P5/P6 已完成并通过独立读回审核；P7 工程检查完成，正式实验等待基线口径确认。不是完整 P7 结果报告。

## 1. 实施范围和审核状态

本次依照 [原子化计划](F:/Program/VSCode/MyGit/ProxyAnalysis/plan/0916-paired-structure-mechanism-atomic-plan-20260918.md) 实施。

- 旧 mechanism 冻结输入及40个历史job的产物哈希检查通过；保留旧代码与结果不变。
- 新配置在新诊断之前冻结：240、scalar14、原内容外层划分、λ=0.01/0.1/1、主λ=0.1、三种循环错配、正式320次预算。
- 环境：Pytorch312，Python 3.12.8、NumPy 2.0.1、SciPy 1.15.2、sklearn 1.6.1。没有安装或升级依赖。
- P5：240/299两个重叠队列，3,234条指标记录、720条内容汇总；共299个独立访问ID，不把重叠队列相加为独立访问数。
- P6：40个已拟合M0模型，新增拟合为0；原预测最大重建误差2.1094e−15。
- P7：4个代表上下文，各做新R0和严格sklearn参考，共8次工程拟合；正式拟合0次。
- 独立脚本重新按nonempty摘要计算计数、直接按保存参数重建概率及家族margin，通过。未重读PCAP，因此不是对原始流量提取的重新独立验证。
- 全套测试173 passed，其中新增7项。首次全套运行遇到系统pytest临时目录权限问题，改用工作区内全新临时目录后通过；没有修改旧测试来规避断言。

## 2. P5：变化体现在哪类计数项

访问级计数均来自实体内分别计算后的求和。全部使用observed，不串接不同实体，不混用重传过滤。空载荷包不是纯ACK的同义词。

逐访问精确核验：

```text
N_all = N_data + N_empty
R_all = R_data + G_R
ΔN_all = ΔN_data + ΔN_empty
ΔR_all = ΔR_data + ΔG_R
```

其中R_data为非空方向段fr_runs；G_R为保留空载荷包相对于删除它们增加的方向段。两侧nonempty摘要、capture-audit和session缓存均已交叉核对。两侧实体数量一致；不宣称新增了逐实体配对结果表。

### 2.1 主队列：内容等权的平均绝对增量

以下是post−pre平均计数，不是中位比值；因此各分项严格可加。

| 指标 | SS | VLESS |
|---|---:|---:|
| ΔN_all | 1782.4083 | 675.6333 |
| ΔN_data | 937.5917 | 329.9417 |
| ΔN_empty | 844.8167 | 345.6917 |
| 非空包增量占总包增量 | 52.60% | 48.83% |
| 空载荷包增量占总包增量 | 47.40% | 51.17% |
| ΔR_all | 1552.8000 | 303.6833 |
| ΔR_data | 11.0583 | 20.4833 |
| ΔG_R | 1541.7417 | 283.2000 |
| ΔR_data占总方向段增量 | 0.71% | 6.74% |
| ΔG_R占总方向段增量 | 99.29% | 93.26% |

这些数值回答了“增量落在哪一个计数项”：两部署总方向段增量的主体均落在G_R项；SS的绝对增量更大。另一方面，新增包并不全部是空载荷包，SS约一半包数增量落在非空包中。

不能从这些恒等分解推出“99.29%的变化由ACK因果造成”，也不能把VLESS的全局均值视为每个业务同向。均值易受规模影响，本产物同时保留业务/内容分层、median、MAD、IQR与正负次数；这些与原P4的典型比值回答不同问题。

299作为同批次敏感性队列已完整生成；业务级各项也全部保留。贡献比例仅在分母非零且没有严重抵消时报告；本实现将总差绝对值低于内容绝对平均差的10%标记为抵消，不把该描述性标记用作模型选择。

## 3. P6：分布表示的跨部署错误定位

保存的模型、类别顺序、中位填补及scaler可直接重建历史M0，无需重新拟合。二分类使用等价logits(−t/2,t/2)，多分类使用保存的K行参数。

对真实类别与竞争类别的margin分解为scalar、length、IAT、curve和intercept。错误样本的竞争类是预测类；正确样本为最高概率的非真类。匹配源/目标访问时固定目标竞争类，避免相减不同分类边界。

### 3.1 distribution157跨部署诊断

“最负家族”表示该模型下家族margin的最小项，不是因果重要性，也不是独立样本频数。

| 任务/方向 | 错误访问数/总数 | CE bits | 错误平均置信度 | 最负家族次数：scalar/length/IAT/curve |
|---|---:|---:|---:|---|
| 六类 SS→VLESS | 65/120 | 4.2093 | 0.7435 | 2 / 30 / 22 / 11 |
| 六类 VLESS→SS | 78/120 | 6.3267 | 0.8812 | 8 / 41 / 15 / 14 |
| YouTube SS→VLESS | 20/40 | 9.8781 | 0.9996 | 0 / 17 / 3 / 0 |
| YouTube VLESS→SS | 18/40 | 9.2728 | 0.9623 | 0 / 3 / 1 / 14 |

六类VLESS→SS的错误中，长度桶在41/78个访问上是最负项；但IAT、curve等也参与负margin，不能归纳为唯一一个家族造成全部问题。YouTube两个方向的最负项明显不同，不支持单一通用归因。

scalar14的同方向CE分别为2.8088、0.9415、5.5045、1.5498，错误访问分别64、40、27、11。更丰富表示的同部署优势没有自动转化为迁移优势。

### 3.2 已落盘的诊断细节

- 每访问的真实类、竞争类、家族margin、截距、真实类概率和置信度。
- 每内容平均margin、错误比例、最负平均家族，避免只展示重复访问频数。
- 同内容同轮次的源/目标margin差，竞争类保持一致。
- 源训练、源测试、目标测试的逐特征标准化值分位数，以及超过3/5/10的比例。
- 源方差和scale、零方差标记，逐维margin贡献；未把极端标准化值自动解释为实现错误。
- 固定α=0.5的M0/M2预测变化：由错到对、由对到错、类别不变和CE变化。没有增加教师拟合。

所有方向、任务和表示均保留。不根据这批目标错误删特征、换λ或改P7目标。模型分解不是机制因果证明；输入相关性使多个家族可能共同反映相同结构。

## 4. P7暂停原因：历史基线与高精度基线不逐值一致

### 4.1 工程比较

新R0使用与历史一致的源post填补/标准化、C=1和硬标签；二分类单log-odds的L2尺度单独实现。新目标通过解析梯度/数值梯度、trace等价、共同logit平移不变性及错配映射检查。

代表折为outer_fold=0，覆盖两任务两部署。正式320次训练尚未执行。

| 设置 | 新R0 vs严格sklearn最大概率差 | 新R0 vs历史最大概率差 | 历史预测类别改变数 |
|---|---:|---:|---:|
| 六类 SS | 1.99e−7 | 0.00137795 | 0/24 |
| 六类 VLESS | 1.62e−7 | 0.00108814 | 0/24 |
| YouTube SS | 8.48e−9 | 0.00013120 | 0/8 |
| YouTube VLESS | 1.69e−8 | 0.00027706 | 0/8 |

新R0对严格sklearn的四项比较全部通过1e−6门槛；对历史默认停止精度的四项均超过该门槛。没有事后放宽容差。

新目标值与严格sklearn的差约在1e−13以内；新解梯度无穷范数约2e−9至5e−9，历史解约5e−5至8e−5。历史目标值略高，例如六类SS从0.468851689降至0.468849774。这组证据支持“同一目标收敛精度不同”，没有显示损失尺度不等价。

但这只验证四个代表上下文；不能声称全20个上下文已经对齐，更不能说历史所有外层测试标签都不变。

### 4.2 推荐确认内容

建议允许正式P7统一使用新高精度R0作为比较基线；True/Wrong/Iso都使用相同新优化器及容差。历史M0仅作为历史参考，保留差异审计，绝不替换P0–P4已有指标。

这不是改变λ或挑选有利模型，而是明确新实验内部的共同数值基准。它仍需要用户确认，因为已批准计划明确要求在这种差异出现时暂停。

确认前不生成正式P7性能或收益结论；确认后仍需完成正式runner、完整映射/泄漏测试、320次训练、收益区间和最终独立审核。若后续收敛或来源审核失败，仍按计划暂停。

## 5. 产物与复用入口

- [新冻结配置](F:/Program/VSCode/MyGit/ProxyAnalysis/configs/content-generalization-20260916-paired-constraint.yaml)
- [冻结输入清单](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/content-generalization-20260916/paired-constraint-01/contract/manifest.json)
- [P5分组结果](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/content-generalization-20260916/paired-constraint-01/p5-counts/group-count-summary.json)
- [P5逐访问分解](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/content-generalization-20260916/paired-constraint-01/p5-counts/session-count-decomposition.parquet)
- [P6内容等权结果](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/content-generalization-20260916/paired-constraint-01/report/p5-p6/content-equal-summary.json)
- [P6标准化偏移](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/content-generalization-20260916/paired-constraint-01/p6-diagnostics/standardized-shifts.parquet)
- [P7基线差异审计](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/content-generalization-20260916/paired-constraint-01/p7-models/engineering/baseline-parity.json)
- [P5/P6独立审核](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/content-generalization-20260916/paired-constraint-01/audit/p5-p6/validation.json)

所有入口均为可复用Python模块，默认读取新配置，支持--config。按顺序运行：

```powershell
$env:PYTHONPATH='src'
$env:OMP_NUM_THREADS='1'
$env:MKL_NUM_THREADS='1'
$env:OPENBLAS_NUM_THREADS='1'
# freeze已执行，不要重复创建目录；后续使用verify
& D:/Tools/Anaconda/envs/Pytorch312/python.exe -m proxy_analysis.crosscontent.paired_structure_contract --mode verify
& D:/Tools/Anaconda/envs/Pytorch312/python.exe -m proxy_analysis.crosscontent.count_decomposition
& D:/Tools/Anaconda/envs/Pytorch312/python.exe -m proxy_analysis.crosscontent.frozen_margin_diagnostics
& D:/Tools/Anaconda/envs/Pytorch312/python.exe -m proxy_analysis.crosscontent.paired_constraint_smoke
& D:/Tools/Anaconda/envs/Pytorch312/python.exe -m proxy_analysis.crosscontent.paired_structure_audit
& D:/Tools/Anaconda/envs/Pytorch312/python.exe -m proxy_analysis.crosscontent.paired_structure_delivery
```

已有阶段读取complete清单并验证哈希，不重复拟合或覆盖。工程complete表示工件完整，内部gate明确passed=false；不能把存在complete文件误当正式运行获准。

## 6. 当前结论

P5已将代理边界差异分解成可加的计数项；P6已把迁移错误定位到冻结模型的具体家族margin，而不是继续笼统怀疑软标签实现。P7目前只得到新基线工程等价性证据，尚没有直接配对约束的效果证据。

没有新采集、原始PCAP扫描、目标部署拟合、旧结果覆盖或仓库推送。
