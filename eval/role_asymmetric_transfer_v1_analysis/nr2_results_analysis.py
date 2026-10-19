"""Post-seal NR2 interpretation: no fitting, corrections or H reads."""
import time
LOAD_START=time.perf_counter()
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'eval/role_asymmetric_transfer_nr2_pilot'))
import common as C
import numeric as N
import torch
import json

def main():
    C.configure();out=C.OUT/'analysis';doc=C.DOC/'results-interpretation-20261018.md'
    complete=C.read(C.OUT/'completion.json');contract=C.read(C.OUT/'manifests/contract.json');cost=C.read(C.OUT/'cost-final.json')
    C.require(complete['pilot_program_complete'] and C.read(C.OUT/'verification.json')['passed'],'Pilot not complete')
    C.require(C.sha(C.DOC/'complete-report-20261018.md')==complete['report_sha256'],'Sealed report changed')
    bounds={str(p.relative_to(ROOT)):C.sha(p) for p in [C.OUT/'completion.json',C.OUT/'verification.json',C.OUT/'cost-final.json',C.OUT/'manifests/contract.json',C.DOC/'complete-report-20261018.md']}
    results=[C.read(p) for p in (C.OUT/'results').glob('*.json')]
    cases=[r for r in results if r['kind']=='zero-start-case'];C.require(len(cases)==52,'52 cases')
    diag=[C.read(p) for p in (C.OUT/'diagnostics').glob('*-result.json')]
    overlap=C.read(C.OUT/'audits/old-new-overlap.json')['results'];old=C.read(C.OUT/'audits/old-endpoint-compatibility.json')
    geometry=[]
    for e in contract['design']['snapshot_diagnostics']:
        p=ROOT/e['failure_json'];C.require(C.sha(p)==contract['protected'][C.rel(p)],'Failure changed')
        f=C.read(p);s=torch.load(ROOT/e['slot_path'],map_location=C.dev(),weights_only=True)
        state=torch.load(p.with_suffix('.pt'),map_location=C.dev(),weights_only=True)
        h=N.hessian(state['last_original_parameters'],s,f['t']);ev=torch.linalg.eigvalsh((h+h.T)/2)
        geometry.append(dict(id=e['id'],dimension=581,min_eigen=float(ev[0]),max_eigen=float(ev[-1]),condition=float(ev[-1]/ev[0]),no_parameter_update=True))
    prefix=[]
    for ap in (C.OUT/'attempts').glob('*.json'):
        a=C.read(ap)
        if a['kind']=='prefix-diagnostic':
            lg=C.read(C.OUT/'lbfgs-logs'/f"{a['index']:03d}.json")
            prefix.append(dict(attempt=a['index'],closure_evaluations=lg['closure_evaluations'],optimizer_recorded_evaluations=lg['optimization_evaluations'],
                               selected_update_hook_bookkeeping_gap=lg['closure_evaluations']-lg['optimization_evaluations']))
    steps=[tr for r in results+diag for tr in r.get('newton_trace',[]) if 'damping_attempts' in tr]
    eng=C.read(C.OUT/'audits/engineering.json')
    science_new=sum((r['role_id'],r['policy_id']) not in {(e['role_id'],e['policy_id']) for e in contract['endpoints']} for r in cases)
    maxerr=max(r['gradient_replay_error'] for r in C.read(C.OUT/'audits/independent-new-endpoints.json')['results'])
    metadata=dict(unique_cases=52,unique_cases_using_Newton=sum(r['newton_updates']>0 for r in cases),
        max_original_gradient=max(r['max_gradient'] for r in cases),max_total_updates=max(r['total_updates'] for r in cases),
        max_newton_updates=max(r['newton_updates'] for r in cases),max_gradient_replay_error=maxerr,
        old_endpoint_audit_count=old['count'],old_new_overlap_count=len(overlap),new_unique_scientific_candidates=science_new,
        potentially_available_scientific_union=604+science_new,formally_adopted_into_new_full_run=False,
        Newton_direction_steps_including_diagnostics_repeats=len(steps),nonzero_damping_steps=sum(r['mu']>0 for r in steps),
        max_linear_relative_residual=max(r['linear_relative_residual'] for r in steps),
        hessian_total_seconds=sum(r['hessian_and_gradient_seconds'] for r in steps),
        factor_total_seconds=sum(r['factor_and_solve_seconds'] for r in steps),
        line_search_total_seconds=sum(r['line_search_seconds'] for r in steps),
        max_synthetic_hessian_error=max(r['hessian_relative_error'] for r in eng['synthetic']),
        max_real_HVP_error=max(h['relative_error'] for r in eng['real_hvp'] for h in r['hvp']),
        snapshot_geometry=geometry,prefix_count_semantics=prefix,H_reads=0,model_updates=0,source_hashes=bounds)
    rows=[]
    for r in sorted(cases,key=lambda x:(x['role_id'],x['policy_id'])):
        rows.append('| '+' | '.join([r['role_id'].replace('main/','').replace('/outer',''),r['policy_id'],str(r['t']),str(r['lbfgs_updates']),str(r['newton_updates']),
            str(r['counters']['optimization_evaluations']),f"{r['max_gradient']:.6g}",f"{r['seconds']:.3f}"])+' |')
    hard=[]
    for r in cases:
        if (r['role_id'],r['policy_id']) in [('main/f1/trojan/G0/outer','RawPre__m025__UPR'),('main/f0/vless/G0/outer','RawPre__m050__UPR')]:
            hard.append(f"- {r['role_id']} / {r['policy_id']}：1024＋{r['newton_updates']}更新，目标{r['objective']:.16g}，原梯度{r['max_gradient']:.8g}，优化评价{r['counters']['optimization_evaluations']}次，求解{r['seconds']:.3f}秒。")
    text=f'''# NR2结果解释、逐案例表与数值计数补充

## 1. 主要结论

**固定52例全部通过原坐标数值验收。** {metadata['unique_cases_using_Newton']}例实际触发二阶阶段，其余在原LBFGS阶段合格；最大总更新{metadata['max_total_updates']}，最大Newton更新{metadata['max_newton_updates']}，没有增加原4000/20000资源额度，也没有放宽原梯度门。

本轮给出了支持继续审议同目标数值恢复的证据，不是RA1业务有效性的证据。完整实验仍未重启，H-post/标签和实际目标U数据未读取。

## 2. 两个历史难例已从零解决，但旧失败不回写

{chr(10).join(hard)}

失败快照的两个局部诊断各1次Newton合格，但不进入正式端点。两个从零困难点均在1024次切换后1次Newton合格，和事后在4000次旧失败后追加步骤是不同操作。独立前缀参数/目标/梯度/logits误差均为0。

最大的原坐标终态梯度为{metadata['max_original_gradient']:.8g}，门限仍为1e-5。52个终点独立梯度重放最大误差{maxerr:.8g}；合成解析Hessian相对误差最大{metadata['max_synthetic_hessian_error']:.8g}，真实槽HVP最大相对误差{metadata['max_real_HVP_error']:.8g}。

## 3. 二阶数值几何及方向行为

以下是原两失败参数处的完整581维Hessian，只消除共同bias，不丢弃共同W；不执行参数更新：

| 快照 | 最小特征值 | 最大特征值 | 条件数 |
| --- | ---: | ---: | ---: |
'''
    for r in geometry:text+=f"| {r['id']} | {r['min_eigen']:.8g} | {r['max_eigen']:.8g} | {r['condition']:.8g} |\n"
    text+=f'''
包含诊断和重复的Newton方向共{len(steps)}步，非零阻尼{metadata['nonzero_damping_steps']}步；最大线性相对残差{metadata['max_linear_relative_residual']:.8g}。这些结果支持本次固定集合中的二阶方向可用，不代表全部剩余问题也必定合格。

已记录方向步骤中，Hessian及梯度构造合计{metadata['hessian_total_seconds']:.4f}秒，分解和求解{metadata['factor_total_seconds']:.4f}秒，线搜索{metadata['line_search_total_seconds']:.4f}秒。这些是逐步实测，不包含原LBFGS、工程AD核验、I/O和全部审核。

## 4. 旧模型、数值差异与潜在复用

全部1024个旧逻辑端点（604科学＋420历史参照）完成原目标/梯度/尺度复核且原文件哈希未变。52例中与旧可用端点交叠{len(overlap)}个；另有{science_new}个唯一科学候选原先缺失。若以后获得正式恢复授权且兼容核验通过，科学端点并集可达{604+science_new}，但此处没有签入新完整模型合同，也没有把重复或快照诊断算作新增科学端点。

已合格旧端点不被强制Newton重训；相同数值目标和原精度门可支持后续兼容审议，但不能声称它们走过了NR2轨迹。旧新交叠参数或训练概率存在微小差异，并非H业务增量；本轮不按任何H结果选择新旧版本。

## 5. 计数细节与工程停止说明

52唯一Z＋2重复＋2快照诊断＋2前缀诊断=58次优化尝试；其中54个从零最终拟合。原谱系639次加58次，保守合计697次，仍受2348次保护上限约束。

独立前缀诊断在“所选更新完成后”的观察hook退出，早于框架对最后一次线搜索的函数评价计数写回，因此该诊断的optimizer状态计数可能比实际closure调用少。实际调用数完整保存在closure_evaluations，差额如下；它们不是正式接受模型，不能据落后的状态字段漏算工作或宣称接近20000边界仍合法。

| 前缀attempt | 实际closure调用 | optimizer状态计数 | 观察点差额 |
| --- | ---: | ---: | ---: |
'''
    for r in prefix:text+=f"| {r['attempt']} | {r['closure_evaluations']} | {r['optimizer_recorded_evaluations']} | {r['selected_update_hook_bookkeeping_gap']} |\n"
    text+='''
首次登记尝试在任何拟合和合同封存前因NR1政策路径错误停止；记录和报告仍保留。修订后在独立run02目录执行，仅更正工程登记路径，实际政策SHA逐模型核对。首次停止7.1769秒计入同一30分钟额度。该次尚未完成contract/seal，因此不能事后声称已有完整源码封存。其未完成登记账的parent_prior=null不是RA1父成本为零；run02明确继承Full NR1父账。

本补充分析首轮曾因Windows路径分隔符与封存键格式不一致而在元数据查找处退出；已改用原规范化rel函数，无模型更新，也不修改已通过的训练结果。停止信息另存analysis/preliminary-readonly-stop.json，保守计费10秒，未把该次只读分析计为新拟合。

## 6. 完整52例明细（训练目标数值，不是业务分数）

| 角色 | 政策 | t | LBFGS更新 | Newton更新 | 优化评价 | 原梯度 | 求解秒 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
'''+ '\n'.join(rows)+'\n'
    C.pathout(doc).write_text(text,encoding='utf-8')
    elapsed=time.perf_counter()-LOAD_START
    metadata['additional_readonly_analysis_activity_seconds']=elapsed
    metadata['prior_readonly_analysis_stop_charge_seconds']=10.
    metadata['combined_NR2_activity_seconds']=cost['pilot_activity_seconds']+elapsed+10.
    metadata['parent_cumulative_with_analysis_seconds']=cost['parent_cumulative_active_seconds']+elapsed+10.
    C.require(metadata['combined_NR2_activity_seconds']<1800,'NR2 analysis exceeds same pilot activity cap')
    C.require(all(C.sha(ROOT/p)==h for p,h in bounds.items()),'Source changed during analysis')
    C.write(out/'interpretation.json',metadata)
    print(json.dumps({k:v for k,v in metadata.items() if k not in ['source_hashes','snapshot_geometry','prefix_count_semantics']},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
