"""Read-only explanatory closeout and additive report-sidecar correction.

No classifier, Hessian, gradient, or new finite-difference evaluation is executed.
"""
from pathlib import Path
import hashlib
import json
import time
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
PARENT=ROOT/'outputs/dynamic-soft-drift-implicit-pilot-20261012/run-01'
OUT=ROOT/'outputs/dynamic-soft-drift-implicit-closeout-20261012/run-01'
DOC=ROOT/'docs/dynamic-soft-drift-calibration/implicit-20261012'
REPORT=DOC/'implicit-pilot-closeout-20261012.md'
OLD_REPORT=DOC/'implicit-pilot-report-20261012.md'
ACCESS=[]

def sha(p):
    p=Path(p)
    if p.suffix in ['.pcap','.pcapng']:raise RuntimeError('No PCAP access')
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()

def read(p):
    ACCESS.append(str(Path(p).relative_to(ROOT)))
    return json.loads(Path(p).read_text(encoding='utf-8-sig'))

def write(p,x):
    p=Path(p); p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf-8')

def table(d):return d.to_markdown(index=False,floatfmt='.9g')
def frame(name):
    p=PARENT/name;ACCESS.append(str(p.relative_to(ROOT)))
    return pd.read_parquet(p)

def main():
    if (OUT/'completion.json').exists():raise RuntimeError('Closeout already sealed')
    c=read(PARENT/'manifests/contract.json'); end=read(PARENT/'completion.json')
    v=read(PARENT/'verification.json'); seal=read(PARENT/'manifests/seal.json')
    assert sha(PARENT/'manifests/contract.json')==seal['contract_sha256']
    assert sha(PARENT/'verification.json')==end['verification_sha256']
    frozen={**c['parent_files'],**c['code'],**c['math_code'],**v['files']}
    for p in PARENT.rglob('*'):
        if p.is_file():frozen[p.relative_to(ROOT).as_posix()]=sha(p)
    frozen[OLD_REPORT.relative_to(ROOT).as_posix()]=sha(OLD_REPORT)
    for p,h in frozen.items():assert sha(ROOT/p)==h,p
    write(OUT/'contract.json',dict(version='read-only-closeout-v1',registered_unix=time.time(),
          parent_files=frozen,source_sha256=sha(Path(__file__)),new_fits=0,new_gradient_evaluations=0,PCAP_reads=0))
    traces=frame('refinement-traces.parquet'); fd=frame('one-FD-checks.parquet'); implicit=frame('one-implicit-checks.parquet')
    snapshots=[]; base_logs=[]; failed=[]
    for p in (PARENT/'endpoints').rglob('*.json'):
        x=read(p)
        if 'old_reference' in x:
            base_logs.append(x)
            if not x['accepted']:failed.append(dict(path=str(p.relative_to(ROOT)),exception=x.get('exception')))
        elif 'sha256' in x and 'threshold' in x:
            assert sha(p.with_suffix('.pt'))==x['sha256']
            log=read(p.parent/(x['key']+'.json'))
            tr=next(t for t in log['trace'] if t['iteration']==x['iteration'])
            passed=log['accepted'] and tr['original_gradient']<=x['threshold']
            snapshots.append(dict(key=x['key'],threshold=x['threshold'],iteration=x['iteration'],
                original_gradient=tr['original_gradient'],passed=passed,artifact_SHA_matches=True))
    assert len(base_logs)==3 and len(snapshots)==6 and not failed
    assert all(x['passed'] for x in snapshots)
    assert end['new_q_LR_accepted']==2 and end['old_reference_refinements']==1
    df=pd.DataFrame(snapshots); OUT.mkdir(parents=True,exist_ok=True)
    df.to_parquet(OUT/'precision-endpoints-corrected.parquet',index=False)
    pd.DataFrame([dict(accepted_forward_points=3,failed_forward_points=0,accepted_precision_snapshots=6,
                      snapshot_sidecars_misclassified_in_old_report=6)]).to_parquet(OUT/'forward-counts-corrected.parquet',index=False)
    row=fd.iloc[0]; fine=implicit.loc[implicit.level==1].iloc[0]
    margin=row['limit']/10
    assert row.signal_identifiable and row.error<=row['limit'] and row.level_difference<=row['limit']
    assert row.FD_precision_error>margin and not row.passed
    gate=pd.DataFrame([
       dict(item='风险差信号',value=row.signal,limit=row.signal_floor,rule='至少等于下限',passed=bool(row.signal_identifiable)),
       dict(item='隐式与细档差分差',value=row.error,limit=row['limit'],rule='不超过上限',passed=True),
       dict(item='粗细差分斜率差',value=row.level_difference,limit=row['limit'],rule='不超过上限',passed=True),
       dict(item='差分精度变化指标',value=row.FD_precision_error,limit=margin,rule='不超过上限',passed=False)])
    gate.to_parquet(OUT/'failure-cause.parquet',index=False)
    geometry=frame('audits/hessian-geometry.parquet')
    geotable=geometry.groupby(['arm','point']).agg(
       raw_min=('raw_contrast_condition','min'),raw_max=('raw_contrast_condition','max'),
       transformed_min=('whitened_contrast_condition','min'),transformed_max=('whitened_contrast_condition','max')).reset_index()
    geotable.to_parquet(OUT/'geometry-summary.parquet',index=False)
    coeff=frame('audits/oracle-coefficients.parquet'); equiv=frame('audits/gauge-equivalence.parquet')
    role=c['selected'][0]; base=pd.DataFrame([dict(key=x['key'],accepted=x['accepted'],Newton_updates=x['Newton_updates'],
               solver_seconds=x.get('initial_solver',{}).get('seconds',0),total_seconds=x['seconds']) for x in base_logs])
    rt=read(PARENT/'stages/geometry.json')['seconds']+read(PARENT/'stages/one.json')['seconds']
    text=f'''# 动态软约束漂移解级反馈先导结项报告

2026年10月12日。本轮已完成有界先导并按预登记门停止，状态保持`{end['status']}`。已完成计数纠正、全部24个旧问题的数值几何、首个源内P问题的中心隐式导数及一个充分重训差分。没有进入正式q学习，其他角色、第二步长、交替方向及q_alt均未执行。

最重要的区别是：本次LR已充分训练，中心Hessian、混合导数和线性系统核对通过，隐式导数与细档差分也非常接近；停止来自粗细前向风险变化的预登记不确定性指标。不能将本次停止写成隐式导数公式错误，也不能据单个一致案例宣布整个先导合格。

## 目标与输入权限

使用Pytorch312、PyTorch {c['environment']['torch']}、CUDA {c['environment']['cuda']}及{c['environment']['gpu']}。训练、模型推理、Hessian和求导全部CUDA float64，没有CPU数值回退。本结项只整理已保存表格和元数据，不新增任何数值实验。

六类任务、96维十块、基础漂移映射、t、mu/scale、标签、质量及内容划分保持不变。原分类目标是带权CE加0.0005(1+t)乘原W平方，bias无正则。480行训练槽位和8行源内留出反馈均沿用封存成员，调整pre占总CE质量1/30。

新反馈是在原LR充分求解后的源内CE。隐式导数通过解Hv=g后计算−M转置v，不显式求逆，不穿过LBFGS或Newton轨迹。旧有限展开及旧影响近似没有迁入本轮资格。

首个角色为`{role['id']}`：实际shadowsocks标签只作为排除对象，源内校准部署是{role['calibration']}，遮蔽组{role['group']}、t={role['t']}。这不是在实际目标SS测试集上验收；实际目标C/U/H数值读取为零。

## 已完成的基础核验

旧失败计数表的27条门记录已独立纠正：各K的全门通过数仍为0/24，类别门4通过、20失败，其余门0通过、24失败。旧报告和Parquet没有原位改写。

24个训练问题的坐标和界重放、72个位置的实际Hessian几何全部完成。485维数值参数消去共同bias，并解析最小化有L2的共同W分量；没有把共同W误当无正则自由度。概率等价最大误差{equiv.probability_error.max():.9g}，原目标重放最大误差{equiv.objective_error.max():.9g}，原梯度链核对最大误差{equiv.gradient_error.max():.9g}。独立惩罚系数最大误差{coeff.coefficient_error.max():.9g}，匿名G不读取P身份或映射。

{table(geotable)}

变换后的零初始化Hessian条件数约为1，说明预条件化能改善局部数值几何；这不改变旧全范围步长界过度保守、有限轨迹近似失败的结论。实际Hessian与设计矩阵上界没有混名。

## 前向解已达到较高精度

中心复用1个旧参照，加减端点新增2个原v4 LR问题；三者均在同一原目标下进行了2次Newton精炼，共6次更新。每点粗档1e-8、细档1e-9原梯度门均通过。

{table(df)}

{table(base)}

共有3个接受的前向点、6个接受的精度端点，失败前向点为0。原报告的失败点附表扫描了带key的JSON，将6个精度快照侧车因没有accepted字段误列为失败；该问题仅影响报告附表，不参与数值门或停止状态。此处独立纠正并保留原报告，不回写封存结果。

## 中心隐式导数通过了哪些检查

细档中心原坐标梯度为{fine.original_gradient:.9g}，已经远低于1e-9门。变换坐标Hessian条件数为{fine.condition:.9g}，Cholesky成功，无jitter。解析H与AD的归一化差为{fine.hessian_error:.9g}，线性系统相对残差为{fine.linear_residual:.9g}，同矩阵独立求解所得任务梯度最大差为{fine.independent_solve_error:.9g}，解析混合偏导与AD VJP最大差为{fine.mixed_VJP_error:.9g}。

两档中心十维梯度最大差为{fine.precision_stability_error:.9g}，逐维稳定性门通过。这只说明当前中心的核对成立，不替代剩余角色及两个方向的重训差分。

## 唯一执行的差分及停止原因

固定全同向单位方向、h=1e-4。细档充分重训差分为{row.D_h:.12g}，隐式方向导数为{row.implicit:.12g}，差为{row.error:.9g}。两者同为正值，表示该局部方向提高源内CE；实验并未要求扰动必须改善业务。

{table(gate)}

停止门是最后一行：粗细风险差形成的差分精度变化指标{row.FD_precision_error:.9g}，约为允许上限{margin:.9g}的{row.FD_precision_error/margin:.6g}倍。细档导数一致性本身没有失败，粗细差分斜率差也没有失败，风险差信号足够可辨。

该指标使用加减端点各自粗细风险差的绝对值之和除2h，因此不会让两个端点的误差相互抵消。它是预登记的经验精度指标，不是细档解误差的严格上界。当前结果不能仅因细档差分看起来正确就删去此门，也不能据这个指标超过门限断言细档导数已经失真。

## 软惩罚仍使用激活分项检查

q=1处十块均跨激活边界。D-P完整中心差分与真实局部导数的差包含约−0.0480544994的惩罚截断项；该普通完整差分按原修订规范不作为唯一验收标准。独立惩罚解析梯度核对通过，T-P平滑目标差分通过。停止并不是再次误用了激活边界的完整中心差分。

## 执行量与未验证范围

数值几何与q=1阶段合计约{rt:.6g}秒，不含启动、合成测试、合同封存、完整性复核和报告。新增LR问题2个，均接受；旧参照精炼1个；不同q点3个；精度端点6份；正式分类器0；漂移映射新拟合0；实际目标读取0；PCAP读取0。

受失败门限制，预定204个新LR问题没有全量运行。当前只覆盖首个角色的P数值问题、起点及一个方向一个步长，不能声称G、其他遮蔽组、q_alt或完整十维局部导数已获得资格。任何已保存CE都是源内数值诊断，不是新的目标业务性能。

## 结项判断

本轮已经摆脱了“为了可微而用几乎没训练起来的分类器提供反馈”的限制：实际完成的三个前向解均高精度，首个隐式导数与充分重训差分取得明确数值一致性。但整条反馈候选尚未通过预登记的前向精度变化门，应保持停止，不自动继续正式学习。

若继续，需先独立登记差分精度指标与前向精度层级如何配套，并保留现有门的失败记录；不能把已有细档一致性直接升级成全先导通过。本轮不修改精度层级、不放宽门限、不增加扰动或求解器。旧P-small正向分类结论和身份归因边界均保持原样。

## 产物

- [原先导报告]({OLD_REPORT.as_posix()})
- [完成状态]({(PARENT/'completion.json').as_posix()})
- [细档差分和停止门]({(OUT/'failure-cause.parquet').as_posix()})
- [纠正后的精度端点表]({(OUT/'precision-endpoints-corrected.parquet').as_posix()})
- [纠正后的前向计数]({(OUT/'forward-counts-corrected.parquet').as_posix()})
- [数值几何汇总]({(OUT/'geometry-summary.parquet').as_posix()})
- [独立结项合同]({(OUT/'contract.json').as_posix()})
- [先导代码]({(ROOT/'eval/dynamic_soft_drift_implicit_pilot/README.md').as_posix()})
'''
    REPORT.parent.mkdir(parents=True,exist_ok=True);REPORT.write_text(text,encoding='utf-8')
    for p,h in frozen.items():assert sha(ROOT/p)==h,p
    write(OUT/'verification.json',dict(passed=True,parent_files_unchanged=True,report_sha256=sha(REPORT),
          reads=ACCESS,new_LR_fits=0,new_Hessian_evaluations=0,new_gradient_evaluations=0,
          numeric_parent_status_unchanged=True,actual_failed_forward_points=0,artifact_sidecars_corrected=6,
          output_files={str(p.relative_to(ROOT)):sha(p) for p in OUT.rglob('*') if p.is_file()}))
    write(OUT/'completion.json',dict(passed=True,status='diagnostic_closeout_complete',
          parent_numeric_qualified=False,parent_status=end['status'],report=str(REPORT.relative_to(ROOT)),
          verification_sha256=sha(OUT/'verification.json'),new_models=0))
    print(json.dumps(read(OUT/'completion.json'),ensure_ascii=False),flush=True)

if __name__=='__main__':main()
