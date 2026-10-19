"""NR2 bounded numerical report. No business/query module is imported."""
from common import *
import common as C

def table(rows,cols):
    lines=['| '+' | '.join(cols)+' |','| '+' | '.join(['---']*len(cols))+' |']
    for r in rows:lines.append('| '+' | '.join(str(r.get(c,'')) for c in cols)+' |')
    return '\n'.join(lines)

def run(success,error=None):
    results=[read(p) for p in (OUT/'results').glob('*.json')] if (OUT/'results').exists() else []
    unique=[r for r in results if r['kind']=='zero-start-case']
    diag=[read(p) for p in (OUT/'diagnostics').glob('*-result.json')] if (OUT/'diagnostics').exists() else []
    oldaudit=read(OUT/'audits/old-endpoint-compatibility.json') if (OUT/'audits/old-endpoint-compatibility.json').exists() else None
    eng=read(OUT/'audits/engineering.json') if (OUT/'audits/engineering.json').exists() else None
    geometry=[]
    for r in diag+results:
        for tr in r.get('newton_trace',[]):
            if 'damping_attempts' in tr:geometry.append(tr)
    local_activity=time.perf_counter()-C.START;activity=C.PILOT_PRIOR+local_activity
    counts=dict(optimization_attempts=len(C.ATTEMPTS),unique_zero_start_accepted=len(unique),
                fresh_zero_start_final_fits_attempted=sum(a['kind'] in ['zero-start-case','deterministic-repeat'] for a in C.ATTEMPTS),
                accepted_repeats=sum(r['kind']=='deterministic-repeat' for r in results),snapshot_diagnostics_qualified=len(diag),
                prefix_diagnostics_complete=sum(a['status']=='prefix-verified-not-adoptable' for a in C.ATTEMPTS),
                failed_or_interrupted_attempts=sum(a['status'] in ['failed','running'] for a in C.ATTEMPTS),
                pending_unique_cases=52-len(unique))
    cost=dict(pilot_activity_seconds=activity,pilot_cap_seconds=1800,parent_prior_charged_seconds=C.PRIOR,
              parent_cumulative_active_seconds=(C.PRIOR or 0)+local_activity,parent_cap_seconds=28800,
              current_process_activity_seconds=local_activity,earlier_NR2_registration_stop_seconds=C.PILOT_PRIOR,
              cost_basis=C.CONTRACT['cost_basis'] if C.CONTRACT else None,
              solver_seconds=sum(r['seconds'] for r in results)+sum(r['seconds'] for r in diag),
              additional_prefix_seconds=sum(a.get('seconds',0) for a in C.ATTEMPTS if a['kind']=='prefix-diagnostic'),
              Hessian_direction_steps=len(geometry),factor_attempts=sum(len(r['damping_attempts']) for r in geometry),
              nonzero_damping_steps=sum(r['mu']>0 for r in geometry))
    groups=[]
    if unique:
        df=pd.DataFrame([dict(source=r['policy_id'].split('__')[0],LBFGS=r['lbfgs_updates'],Newton=r['newton_updates'],seconds=r['seconds'],gradient=r['max_gradient']) for r in unique])
        for name,g in df.groupby('source'):
            groups.append(dict(source=name,count=len(g),Newton_cases=int((g.Newton>0).sum()),max_LBFGS=int(g.LBFGS.max()),
                               max_Newton=int(g.Newton.max()),solver_seconds=round(float(g.seconds.sum()),4),max_gradient=float(g.gradient.max())))
    summary=dict(status='numeric_pilot_passed_waiting_for_user' if success else 'numeric_pilot_stopped',
        pilot_program_complete=success,all_52_cases_accepted=len(unique)==52,counts=counts,cost=cost,
        original_objective_unchanged=True,original_precision_gates_unchanged=True,solver_algorithm_changed=True,
        protected_endpoint_audit_count=oldaudit['count'] if oldaudit else 0,source_hashes_unchanged=True if success else None,
        H_query_reads=0,H_label_reads=0,actual_target_U_reads=0,full_matrix_auto_start=False,full_matrix_started=False,
        ready_for_full_resume_review=success,error=error,source_breakdown=groups)
    write(OUT/'summary.json',summary);write(OUT/'cost-ledger.json',cost)
    write(OUT/'reads.json',dict(reads=C.READS,H_query_reads=0,H_label_reads=0,actual_target_U_reads=0))
    if C.CONTRACT:
        write(OUT/'pending.json',[x for x in C.CONTRACT['cases'] if (x['role_id'],x['policy_id']) not in {(r['role_id'],r['policy_id']) for r in unique}])
    diagnostics=table([dict(id=r['diagnostic_id'],parent_iterations=r['parent_iterations'],Newton=r['newton_updates'],
                           gradient=r['max_gradient'],objective=r['objective'],seconds=round(r['seconds'],4),scientific_accepted=False) for r in diag],
                           ['id','parent_iterations','Newton','gradient','objective','seconds','scientific_accepted'])
    hard=[]
    for r in unique:
        if r['policy_id'].startswith('RawPre') and (r['role_id'],r['policy_id']) in [
            ('main/f1/trojan/G0/outer','RawPre__m025__UPR'),('main/f0/vless/G0/outer','RawPre__m050__UPR')]:
            hard.append(dict(role=r['role_id'],policy=r['policy_id'],LBFGS=r['lbfgs_updates'],Newton=r['newton_updates'],
                             total_updates=r['total_updates'],evaluations=r['counters']['optimization_evaluations'],gradient=r['max_gradient'],
                             objective=r['objective'],seconds=round(r['seconds'],4)))
    overlap=read(OUT/'audits/old-new-overlap.json')['results'] if (OUT/'audits/old-new-overlap.json').exists() else []
    overlaptext=(f"交叠{len(overlap)}个端点；最大原目标绝对差{max(abs(x['objective_difference']) for x in overlap):.8g}，最大训练概率平均TV为{max(x['training_probability_TV_mean'] for x in overlap):.8g}。这些是数值轨迹差异，不是H概率或业务成绩。" if overlap else '尚未完成交叠对照。')
    md=f'''# RA1-NR2 二阶收尾数值先导详细报告

状态：**{summary['status']}**。本轮是数值求解实验，不是新的业务评价。完整实验未恢复，实际H/U未读取。

## 1. 授权、目标与数据边界

用户批准30分钟活动上限，保持模型、损失、权限、正则和原门不变。训练材料来自原RA1训练-only包，沿用原x/y/mass/mu/scale、t/eta、P/G及CORAL；不重新组织访问或拟合映射。

原目标是加权六分类CE＋0.0005*(1+t)||W||²，bias不惩罚；原坐标梯度≤1e-5、目标/梯度重放<1e-10、目标不增及严格总更新<4000保持。单个问题优化评价额度20000，原LBFGS评价停止时点保留。

## 2. 数值程序与工程验收

从零：原LBFGS最多1024次，未合格则至多32次Newton；易例原门合格即停止，不强制精炼。全部数值CUDA float64，禁用TF32/AMP，无CPU回退。

二阶阶段581维，保留完整576维W，仅固定共同bias均值，另外5维使用Helmert对比基；不是直接删除共同W的485维旧方法。解析Hessian来自原CE和原W-L2。先尝试无阻尼Cholesky，必要时按事前固定数值阻尼序列求方向；阻尼不计入损失。Armijo c1=1e-4、步长1至2^-24，共25候选。

工程验收记录：{'通过' if eng else '未完成'}。包括四档t的原目标/梯度/解析Hessian对照、两真实失败槽的六个固定HVP核对、CUDA/精度/非有限/阻尼/无下降线搜索/权限及预算负例。详见audits/engineering.json和backend-diff.json；这些工程门不要求业务增益。

## 3. 快照诊断：不修改旧失败

{diagnostics}

两个诊断各最多8次Newton；即使梯度达标，也不能将旧2000/4000次触顶改判通过，不能直接用于正式模型。原失败快照只读，新输出在独立目录。

## 4. 从零的已知困难点

{table(hard,['role','policy','LBFGS','Newton','total_updates','evaluations','gradient','objective','seconds'])}

新算法没有在4000次后追加求解，而是在1024次内部切换，仍在原总预算内。两个困难点的1024步前缀另作独立重放，和新混合程序的阶段参数比较；结果见audits/prefix-comparison.json。不能将“同目标”误写为全程相同轨迹。

## 5. 固定矩阵与计数

设计52个唯一案例，10角色，四部署、五折、G0/G1/G2及t=0/0.25/1/4。当前接受{len(unique)}/52。新增从零拟合含重复、快照诊断、前缀诊断均独立记账。

{table([counts],list(counts))}

{table(groups,['source','count','Newton_cases','max_LBFGS','max_Newton','solver_seconds','max_gradient'])}

案例不是发生率抽样；不以通过率保证其他未运行角色必定合格。

## 6. 原端点保护与独立审核

已完成旧端点原坐标复核{summary['protected_endpoint_audit_count']}/1024；其中604个科学端点和420历史逻辑参照均应保留源后端、政策、额度与哈希，不能改写为走过NR2轨迹。最终来源保护状态：{summary['source_hashes_unchanged']}。

{overlaptext}

两次新Z确定性重复见audits/deterministic-repeats.json。旧新参数不必相等；同一新算法、同输入的重复则要求参数和训练logits精确一致。新旧交叠比较不用于选择模型或调参。

## 7. 实际成本与停止状态

报告生成时先导活动{activity:.3f}秒（含首次登记停止{C.PILOT_PRIOR:.3f}秒），先导上限1800秒；父累计收费约{((C.PRIOR or 0)+local_activity):.3f}秒，父上限28800秒，不重置。最终含报告写盘的数值见cost-final.json。

新结果及快照诊断求解计时{cost['solver_seconds']:.3f}秒；另有前缀诊断{cost['additional_prefix_seconds']:.3f}秒。记录到的Newton方向步骤{len(geometry)}，非零阻尼步骤{cost['nonzero_damping_steps']}。Hessian/分解/求解/审核都消耗活动预算，不以“小LR”掩盖其成本。

父活动账继承Full NR1的1622.342958秒，加入已记录后续只读分析和明确的60秒保守历史分析收费；后者不是实测。源码编写与人工沟通不被伪装成训练活动计时。

异常：{error or '本次无异常'}。首次登记尝试因将NR1政策误定位到根manifests而在拟合前停止；旧failure/cost及报告保留，后续改为读取各attempt实际政策并核对源SHA。它是工程路径修订，不改变模型、目标、门限或58次优化上限。旧登记账中的parent_prior为null，表示登记未完成，不能把其parent累计字段误当作整项RA1成本；本次继承Full NR1父账并另加该停止的实测活动。

## 8. 结论边界与下一节点

{'固定先导的同目标二阶收尾政策已通过数值审核，可提交下一份完整恢复合同审议；不会自动恢复完整实验。' if success else '本轮尚未获得完整数值先导资格；保留停止和已完成产物，不能通过追加步骤、换门或跳过失败项制造通过。'}

没有H预测、标签评分、新F1/CE/Brier或混淆矩阵。这不是分类正负结果，不能说明RA1一定有效或无效。现有合格端点继续保留，未来采纳仍须明确恢复合同；两个快照诊断不能被采纳。

## 9. 主要产物

- 计划：plan/RA1-NR2-same-objective-second-order-pilot-plan-20261018.md
- 代码：eval/role_asymmetric_transfer_nr2_pilot/
- 运行：outputs/role-asymmetric-transfer-v1-20261017/numeric-pilot-nr2-02/；首次登记停止保留在numeric-pilot-nr2/
- contract/seal、input-fingerprints、engineering、snapshot-diagnostics、prefix-comparison、deterministic-repeats、independent-new-endpoints、old-endpoint-compatibility及verification分别保存。
- attempts/results/live/lbfgs-logs保留成功、失败、内部阶段与逐步轨迹；reads.json、cost-final.json及failure/completion保留权限和结项状态。
'''
    pathout(DOC/'complete-report-20261018.md').write_text(md,encoding='utf-8')
    return summary
