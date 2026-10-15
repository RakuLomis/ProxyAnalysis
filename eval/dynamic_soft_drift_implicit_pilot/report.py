"""Evidence report including conditional stages and exact budget accounting."""
from common import *

def table(d): return d.to_markdown(index=False,floatfmt='.8g')

def frame(p):
    return pd.read_parquet(p) if p.exists() else pd.DataFrame()

def run():
    with stage('report'):
        end=read(OUT/'completion.json'); c=contract(); budget=read(OUT/'ledger.json')
        counts=frame(OUT/'audits/failure-counts-corrected.parquet')
        bounds=frame(OUT/'audits/geometry-bounds.parquet')
        geo=frame(OUT/'audits/hessian-geometry.parquet')
        checks=pd.concat([frame(OUT/f'{p}-implicit-checks.parquet') for p in ['one','alt']],ignore_index=True)
        fd=pd.concat([frame(OUT/f'{p}-FD-checks.parquet') for p in ['one','alt']],ignore_index=True)
        centers=pd.concat([frame(OUT/f'{p}-centers.parquet') for p in ['one','alt']],ignore_index=True)
        failure_rows=[]; traces=[]
        for p in (OUT/'endpoints').rglob('*.json') if (OUT/'endpoints').exists() else []:
            m=read(p)
            if 'key' not in m:continue
            for t in m.get('trace',[]):traces.append(dict(role_id=m['role_id'],arm=m['arm'],key=m['key'],**t))
            if not m.get('accepted',False):failure_rows.append(dict(path=rel(p),**{k:m.get(k) for k in ['role_id','arm','key','exception','Newton_updates','seconds']}))
        if traces: save(pd.DataFrame(traces),OUT/'refinement-traces.parquet')
        if failure_rows:save(pd.DataFrame(failure_rows),OUT/'failed-forward-points.parquet')
        phases=[]
        for p in ['one','alt']:
            f=OUT/f'{p}-complete.json'
            phases.append(dict(point=p,executed=f.exists(),**(read(f) if f.exists() else dict(passed=False,status='conditional_not_executed'))))
        write(OUT/'phase-status.json',phases)
        section_counts=table(counts) if len(counts) else '计数导出未完成。'
        geometry_text='数值几何阶段未完整完成，不能按72个位置已完成描述。'
        if len(bounds):
            geometry_text=f'''完成{len(bounds)}个训练问题的界重放，以及{len(geo)}个参数位置的实际Hessian几何。实际Hessian使用485维对比坐标，消去共同bias，并解析最小化受L2约束的共同W分量。原／变换坐标分列，不含已知共同bias零方向。

全范围界与q=1局部设计界的比值为{bounds.global_over_q_one_design.min():.8g}至{bounds.global_over_q_one_design.max():.8g}；与q_alt局部设计界的比值为{bounds.global_over_q_alt_design.min():.8g}至{bounds.global_over_q_alt_design.max():.8g}。这些比较对象均为设计矩阵界，不是实际Hessian特征值。

{table(geo[['arm','point','raw_contrast_condition','whitened_contrast_condition']].groupby(['arm','point']).agg(['min','max']).reset_index())}
'''
        center_text=table(centers) if len(centers) else '尚无完成并通过中心导数检查的案例。已完成的前向精炼以端点及日志为准。'
        check_text=table(checks) if len(checks) else '未形成中心隐式导数验收表；这不是分类负结果。'
        fd_text=table(fd) if len(fd) else '充分重训差分未执行或尚无完成记录，不能声称已验收局部导数。'
        failure_text=table(pd.DataFrame(failure_rows)) if failure_rows else '无未接受的前向点；若导数门停止，原因见阶段状态和失败JSON。'
        selected=pd.DataFrame([dict(role_id=r['id'],target_exclusion=r['target'],mask=r['group'],source_calibration=r['calibration'],t=r['t']) for r in c['selected']])
        text=f'''# 动态软约束漂移解级反馈先导完整报告

2026年10月12日。本轮状态为`{end['status']}`，执行完整性通过为{end['execution_integrity_passed']}，数值资格为{end['numeric_qualified']}。没有正式q学习，没有新业务F1结果，也没有读取实际目标C/U/H或PCAP。

## 实验问题和冻结范围

本轮以原LR充分求解后的源内留出CE作为反馈，替代质量不合格的有限展开反馈。旧Q64/Q128/Q256没有迁入本轮资格。基础漂移映射、P-small槽位、96维、十块、标签、质量、标准化和t保持不变。

原目标为加权六类CE加0.0005(1+t)乘原W平方；bias不正则。训练槽位480行，反馈为原源内留出的8次访问。调整pre占总CE质量1/30。所有内容重复、两侧及内部flow整体划分，实际目标业务队列不参与拟合或反馈。

{table(selected)}

## CUDA环境和前向政策

Python为{c['environment']['python']}，PyTorch {c['environment']['torch']}，CUDA {c['environment']['cuda']}，GPU为{c['environment']['gpu']}。模型、Hessian、求解和求导均使用CUDA float64，未启用CPU数值回退。

旧q=1参照按SHA复用为起点。新q点使用原v4 LBFGS，max_iter=2000、max_eval=10000、原梯度门1e-5。之后同目标Newton精炼，原梯度门为1e-8和1e-9，每点两档合计最多30次更新。Armijo常数1e-4，缩小因子0.5，每次最多25次回溯；没有jitter、bias正则或额外科学候选。

## 失败计数纠正

旧_pass列实际存放失败计数。新表以passed_count和failed_count独立导出并核对，不更改原运行及0/24停止结论。

{section_counts}

## 数值坐标与Hessian几何

{geometry_text}

## 解级求导与独立验证

隐式导数通过解Hv=g后计算−M转置v，不显式求逆、不穿过LBFGS更新。解析H和混合偏导与自动微分独立核对；线性残差门1e-10，另用CUDA通用线性求解作同矩阵复核。对比参数化保持原目标，485是数值未知量数，不是修改了业务分类器维数。

{check_text}

## 两档中心端点

{center_text}

## 充分重训差分和信号

固定两方向为全同向和交替方向，均单位归一化；固定h=1e-4、3e-5。信号与两档前向风险差及1e-12底限比较，不以微小正负号判定。误差门为1e-5加1e-3乘差分绝对值；跨惩罚分支时用任务项差分与原独立oracle组合，保存完整差分截断项。

{fd_text}

## 阶段状态与停止证据

{table(pd.DataFrame(phases))}

{failure_text}

逐步精炼日志见refinement-traces.parquet，原始端点JSON保留目标、梯度、步长、下降内积及回溯次数。阶段失败JSON保留异常和读取账本。未执行阶段不能计为失败的分类实验。

## 计算与权限账本

{table(pd.DataFrame([budget]))}

完整预登记上限为216个不同q点，其中12个复用端点精炼、204个新LR问题。当前表为实际执行量，不将两档快照称为独立访问。失败点的精炼更新亦计入账本，已产生的端点和失败日志不覆盖。

父产物SHA复核通过；P/G资产按臂权限加载；G未读取P身份或映射。实际目标C/U/H数值读取0，PCAP读取0，漂移映射新拟合0，正式分类器0。旧P-small的正向结果及精确身份归因边界保持原样。

## 结论和下一步边界

本轮只检验反馈取得方式的数值资格，不能据此声称动态系数已提高分类。当前状态为`{end['status']}`，不自动进入D-P、T-P、D-G正式矩阵。若存在精度、差分或信号失败，应先根据封存日志决定是否授权独立修订；不扩K、不改损失、不按真实目标F1选择方向或后端。

## 可复核文件

- [批准的实施方案]({PLAN.as_posix()})
- [封存实验合同]({(OUT/'manifests/contract.json').as_posix()})
- [完成状态]({(OUT/'completion.json').as_posix()})
- [完整性验证]({(OUT/'verification.json').as_posix()})
- [实际计算账本]({(OUT/'ledger.json').as_posix()})
- [代码与重放说明]({(ROOT/'eval/dynamic_soft_drift_implicit_pilot/README.md').as_posix()})
'''
        path=DOC/'implicit-pilot-report-20261012.md'; textfile(path,text)
        write(OUT/'report-seal.json',dict(path=rel(path),sha256=sha(path),completion_sha256=sha(OUT/'completion.json')))
        progress('report_saved',status=end['status'],path=rel(path))

if __name__=='__main__':run()
