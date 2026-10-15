"""Qualification report, including explicitly skipped conditional stages."""
from common import *

def run():
    with stage('report'):
        sel=read(OUT/'selection.json');q=pd.read_parquet(OUT/'q-one-quality.parquet');coords=pd.read_parquet(OUT/'audits/coordinates.parquet')
        summary=q.groupby(['K','arm']).agg(tasks=('role_id','size'),passed=('passed','sum'),
            remaining_min=('remaining','min'),remaining_median=('remaining','median'),remaining_max=('remaining','max'),
            CE_new=('CE_new','mean'),CE_ref=('CE_ref','mean'),CE_mean_abs=('CE_mean_abs','mean'),
            TV=('TV_mean','mean'),logit_RMSE=('logit_RMSE','mean'),gradient_max=('gradient','max')).reset_index()
        save(summary,OUT/'summary.parquet')
        gatecols=[k for k in q if k.endswith('_pass')]
        failures=q.groupby('K')[gatecols].agg(lambda s:int((~s).sum())).reset_index()
        save(failures,OUT/'failure-path.parquet')
        grd=read(OUT/'gradient-verification.json') if (OUT/'gradient-verification.json').exists() else None
        pert=read(OUT/'perturbation-complete.json') if (OUT/'perturbation-complete.json').exists() else None
        status=sel['status'] if not sel['passed'] else pert['status'] if pert is not None else 'awaiting_conditional_stages'
        newfits=0 if pert is None else pert['new_classifier_fits']
        optional='新版梯度扫描及q_alt参照未执行，因为没有起点资格通过的K。' if not sel['passed'] else (
            '新版求导与扰动阶段结果见下表。' if pert else '条件阶段尚未完成，不将其标记为通过。')
        text=f'''# 可微内层第二版源内资格报告

2026年10月12日。本轮执行了完整q=1训练槽位Cholesky坐标与配套固定谱界步长。当前状态为`{status}`。原业务目标、基础映射、损失权重和数据权限不变；有限训练轨迹已改变，不与旧Q64混装。

## 执行范围与复用

同一12个源内任务，P/G共24个训练问题；P与T-P共享相同内层。原24个q=1收敛参照按SHA和数值验收直接复用，重复拟合为零。新基础映射拟合为零，实际目标C/U/H数值及PCAP读取为零。

使用Pytorch312、PyTorch {contract()['environment']['torch']}、CUDA {contract()['environment']['cuda']}和{contract()['environment']['gpu']}。模型运算全部CUDA float64，没有CPU训练或推理回退。

## 坐标与步长

矩阵从q=1的完整480行加权槽位构造，最后一维bias不正则。新参数经冻结L逆解码，原W仍承担0.0005(1+t)平方惩罚，没有把正则改施在新参数上。构造函数只接收训练字段，不接收源内留出post或标签。

步长来自新坐标下的加权谱范数上界，固定安全因子1+1e-12。谱界涵盖q范围[0,2]，不是按留出CE选取。记录各块漂移范数及q=1／q_alt的独立Gram谱界见coordinates表。

新固定步长范围为{coords.step.min():.12g}至{coords.step.max():.12g}；旧步长范围为{coords.old_step.min():.12g}至{coords.old_step.max():.12g}。原／新坐标目标重放最大误差{coords.objective_error.max():.12g}，梯度重放最大误差{coords.gradient_error.max():.12g}。训练目标及坐标等价检查通过，不等于有限轨迹近似质量通过。

## 已预登记的起点质量门

每任务同时要求目标差不超过0.01、剩余目标差距绝对值不超过1%、原梯度不超过1e-3、8行平均绝对CE差不超过0.02、逐行不超过0.05、概率总变差均值不超过0.02且逐行不超过0.05、相对logit RMSE不超过0.10，并满足高margin预测一致及至多一行弱margin改变。全部24组合通过才选择K。

这些是数值近似门，不是业务成功门，也不要求新CE更低。源内反馈用于长度资格，不再是该选择程序的独立验证。门限没有按本轮结果回调。

## 起点质量结果

{summary.to_markdown(index=False,floatfmt='.9g')}

各门失败数量可重叠，不能相加当作失败任务数：

{failures.to_markdown(index=False)}

逐任务完整表包括未截断的剩余比例、原梯度、CE差、概率差、相对logits和改变类别。数据行包含重复角色暴露，不是独立内容数量。没有用更低的源内CE掩盖与参照的近似失配。

## 长度选择与条件阶段

候选长度按64、128、256顺序执行，全任务从零开始；没有逐任务选择不同K。选定长度为{sel['selected_K']}。起点累计执行{sel['short_models']}条单任务前向轨迹、{sel['inner_updates']}次内层更新。

{optional}

新版梯度记录：{json.dumps(grd,ensure_ascii=False) if grd else '未执行，无新版Q求导通过结论。'}

扰动阶段记录：{json.dumps(pert,ensure_ascii=False) if pert else '未执行，新增q_alt收敛LR为零，Delta反馈可靠性尚未评价。'}

## 当前结论和停止边界

新坐标与步长可能显著推进训练，但平均改善、目标降低或坐标等价并不自动满足逐任务近似资格。通过量与失败项应分开看。本轮不支持任何新的动态约束业务增益数字。

若最大长度仍未合格，应接受这个限定内层候选未达到近似要求，不继续扩大K、放宽门或调整步长。尚未执行的求导与固定扰动不能写成失败，亦不能提前放行。下一项数值修订必须独立登记并由用户确认。

所有结果交付后暂停。没有正式q学习、60角色训练或180个最终分类器授权。原先导失败、上一轮修复完成和24个参照保持不变。

## 复现产物

代码目录为eval/dynamic_soft_drift_inner_v2，运行目录为outputs/dynamic-soft-drift-inner-v2-20261012/run-01。contract、reference-reuse、coordinates、quality-models、q-one-quality、summary、failure-path、selection及阶段读取账本构成复核链。条件阶段若执行，会另存gradients与perturbation-models。

完整逐任务结果：

{q[['role_id','arm','K','J_new','J_ref','remaining','gradient','CE_new','CE_ref','CE_mean_abs','TV_mean','logit_RMSE','passed','failed_gates']].to_markdown(index=False,floatfmt='.9g')}
'''
        textfile(DOC/'inner-v2-report-20261012.md',text)
        integrity()
        for p,h in contract()['source_sha256'].items():require(sha(ROOT/p)==h,'New code changed')
        reads=ACCESS[:]
        for p in list((OUT/'stages').glob('*.json'))+list((OUT/'failures').glob('*.json')):reads+=read(p).get('reads',[])
        data=[v for v in reads if v['purpose'] in ['source-task','q-one-reference']]
        require(all(v['path'] in contract()['assets'] and v['arm']==contract()['assets'][v['path']]['arm'] for v in data),'Numeric source permission')
        files={rel(p):sha(p) for p in list(OUT.rglob('*'))+list(DOC.rglob('*')) if p.is_file() and p.name not in ['stage.lock','progress.json','verification.json','completion.json','awaiting-decision.json']}
        verification=dict(passed=True,execution_integrity_passed=True,q_one_quality_passed=sel['passed'],
            selected_K=sel['selected_K'],status=status,new_classifier_fits=newfits,q_one_reference_refits=0,
            target_C_U_H_numeric_reads=0,PCAP_reads=0,parent_files_unchanged=True,files=files,formal_matrix_authorized=False)
        write(OUT/'verification.json',verification)
        write(OUT/'completion.json',dict(passed=True,execution_complete=True,numeric_qualified=bool(sel['passed'] and grd and grd['passed'] and pert and pert['passed'] and not pert['all_weak']),
            status=status,selected_K=sel['selected_K'],new_classifier_fits=newfits,new_mapping_fits=0,
            reference_refits=0,gradient_stage_executed=grd is not None,perturbation_stage_executed=pert is not None,
            formal_matrix_authorized=False,verification_sha256=sha(OUT/'verification.json')))
        write(OUT/'awaiting-decision.json',dict(status=status,formal_matrix_authorized=False,further_numeric_revision_authorized=False))
        progress('inner_v2_report_ready',status=status,new_fits=newfits,selected_K=sel['selected_K'])

if __name__=='__main__':run()
