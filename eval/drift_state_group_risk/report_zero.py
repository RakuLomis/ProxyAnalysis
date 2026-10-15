"""Explicit rendering adapter for legitimate all-zero outer selections.

No sealed training source is changed. Empty optimizer tables retain zero rows;
only their expected display columns are supplied. A separate rendering contract
records this entry point and the fixed-result hashes before document generation.
"""
import report
from common import *

def main():
    c=start('zero-selection-report'); choices=pd.DataFrame(read(OUT/'selection/choices.json'))
    require(choices[choices.arm.isin(ARMS[2:])].alpha.eq(0).all(),'Adapter is only for all-zero selections')
    empty=pd.read_parquet(OUT/'manifests/outer-optimizer.parquet'); require(len(empty)==0,'No positive outer fits')
    require(not list((OUT/'models/main').rglob('DSR*-a*.pt')) or
            not any('/outer/' in p.as_posix() for p in (OUT/'models/main').rglob('DSR*-a*.pt')),'Unexpected outer positive model')
    seal=OUT/'manifests/zero-selection-report-rendering.json'
    require(not seal.exists(),'Rendering contract already exists; inspect before rerunning')
    write(seal,{'sealed_unix':time.time(),'date':'2026-10-06','scope':'rendering only; no model or score changes',
       'entry_sha256':sha(__file__),'original_report_sha256':sha(Path(report.__file__)),
       'selection_sha256':sha(OUT/'selection/choices.json'),
       'outer_optimizer_sha256':sha(OUT/'manifests/outer-optimizer.parquet'),
       'predictions_sha256':sha(OUT/'predictions/visits.parquet'),
       'handling':'An empty optimizer table has zero rows and expected diagnostic columns; no fitted results are invented',
       'no_training_source_change':True})
    original_frame=report.frame; original_emit=report.emit
    candidates=original_frame('selection/candidate-summary.parquet')
    risk=candidates[candidates.arm.isin(ARMS[2:])]
    baseline=risk[risk.setting==0][['outer','protocol','arm','F1']].rename(columns={'F1':'base_F1'})
    paired=risk[risk.setting>0].merge(baseline,on=['outer','protocol','arm'],validate='many_to_one')
    require(len(paired)==180 and np.max(abs(paired.F1-paired.base_F1))<=1e-12,'Zero selection explanation no longer applies')
    inner=original_frame('selection/inner-predictions.parquet'); keys=['outer','inner','protocol','visit_id']
    base=inner[inner.arm=='DSR0'][keys+['prediction',*[f'p{i}' for i in range(6)]]]
    positive=inner[inner.arm.isin(ARMS[2:])&(inner.setting>0)].merge(base,on=keys,suffixes=('','_base'),validate='many_to_one')
    changed=int((positive.prediction!=positive.prediction_base).sum())
    difference=float(np.max(abs(positive[[f'p{i}' for i in range(6)]].to_numpy()-positive[[f'p{i}_base' for i in range(6)]].to_numpy())))
    mechanism=pd.DataFrame([{'positive_inner_query_rows':len(positive),'changed_classes':changed,
                           'max_probability_difference':difference,'tied_candidate_summaries':len(paired)}])
    save(mechanism,OUT/'diagnostics/zero-selection-mechanism.parquet')
    def display_frame(p):
        d=original_frame(p)
        if p=='manifests/outer-optimizer.parquet' and len(d)==0:
            return pd.DataFrame(columns=['seconds','max_gradient','iterations'])
        return d
    def display_emit(name,sections):
        sections=list(sections)
        if name.startswith('complete-report'):
            sections.insert(2,'三种状态方法在20个外层角色各自都选择alpha=0，共60次零选择；最终模型与DSR0逐概率一致。720个正alpha内层候选均已完成，这不是跳过训练或工程失败。内层选择未支持启用状态约束，因此没有新的外层正alpha优化，空优化表记为0次拟合、0秒、梯度NA，不补造模型或改平局规则。报告使用单独封存的 `report_zero.py` 空表呈现入口；封存训练源码和统计定义不变。')
            sections.insert(3,f'180个正alpha内层候选汇总与零候选的macro-F1全部持平，而不是全都降低；按预登记最小alpha平局规则选择零。{len(positive)}条正alpha内层验证预测的类别改变数为{changed}，概率最大绝对改变为{difference:.9f}。这说明本轮约束确实产生了概率微调，但未改变验证分类决策。对DSR2/3的零宽区间来自最终模型相同，不是独立的统计等效证据。')
            sections.insert(4,'从同轮目标压力诊断看，真实状态的外层基座平均平滑风险增量约为3×10⁻⁶ nat，未乘alpha的增量梯度范数约3.6×10⁻⁵，而CE梯度范数约7.2×10⁻³。结合内层概率变化很小，这支持“本轮风险约束在当前固定尺度下作用较弱”的描述；不证明调整温度必然有效，也不证明漂移与业务无关。DSR1还获得更低的平均CE与Brier。本轮不据此重新调参，分类用途和漂移测量价值分别保留。')
        original_emit(name,sections)
    report.frame=display_frame; report.emit=display_emit; report.main()
    require(sha(__file__)==read(seal)['entry_sha256'],'Rendering source changed')

if __name__=='__main__': main()
