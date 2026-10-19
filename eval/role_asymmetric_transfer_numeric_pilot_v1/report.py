"""Always produce pilot closeout, including bounded numerical-stop outcomes."""
from common import *

def md(d):
    names=list(d);lines=['| '+' | '.join(names)+' |','| '+' | '.join(['---']*len(names))+' |']
    for vals in d.itertuples(index=False,name=None):lines.append('| '+' | '.join(str(v) for v in vals)+' |')
    return '\n'.join(lines)

def closeout(stop=None):
    started=elapsed();c=contract() if (OUT/'manifests/seal.json').exists() else None
    results=[read(p) for p in sorted((OUT/'attempts').glob('*/result.json'))]
    starts=[read(p) for p in sorted((OUT/'attempts').glob('*/started.json'))]
    endpoints=[read(p) for p in (OUT/'endpoints').rglob('*.json')]
    oldrep=read(OUT/'audits/old-stop-reproduction.json') if (OUT/'audits/old-stop-reproduction.json').exists() else None
    prefix=read(OUT/'audits/prefix-comparison.json') if (OUT/'audits/prefix-comparison.json').exists() else None
    repeats=read(OUT/'audits/deterministic-repeats.json') if (OUT/'audits/deterministic-repeats.json').exists() else None
    numeric_pass=(OUT/'verification.json').exists() and read(OUT/'verification.json')['passed']
    original_unchanged=True
    if c:
        for p,h in c['preserve'].items():
            if sha(ROOT/p)!=h:original_unchanged=False
    rows=[]
    for r in results:
        rows.append(dict(attempt=r['attempt'],kind=r['kind'],role_id=r['role_id'],policy_id=r['policy_id'],accepted=r['accepted'],
                         iterations=r['iterations'],evaluations=r['evaluations'],gradient=r['gradient'],objective=r['objective'],seconds=r['seconds'],reason=r['reason']))
    frame=pd.DataFrame(rows)
    if len(frame):save(frame,OUT/'attempt-summary.parquet')
    pending=[]
    if c:
        done={(x['role_id'],x['policy_id']) for x in endpoints}
        for case in c['design']['cases']:
            if (case['role_id'],case['policy_id']) not in done:pending.append(case)
    write(OUT/'pending-cases.json',pending)
    if results:
        show=pd.DataFrame([dict(attempt=x['attempt'],kind=x['kind'],policy=x['policy_id'],role=x['role_id'],accepted=x['accepted'],iterations=x['iterations'],evaluations=x['evaluations'],gradient=f"{x['gradient']:.9e}",J=f"{x['objective']:.15g}",seconds=f"{x['seconds']:.3f}") for x in results])
    else:show=pd.DataFrame(columns=['attempt','kind','accepted'])
    status='numeric_pilot_passed_waiting_for_user' if numeric_pass else ('paused_activity_budget' if stop and stop.get('type')=='ActivityBudget' else 'stopped_not_qualified')
    lines=['# RA1-NR1同目标数值先导详细报告','', '日期：2026-10-18。完整业务矩阵未重启；本报告没有新F1/CE测试成绩。','',
      '## 1. 结项状态','',f'状态：`{status}`。42端点中已接受{len(endpoints)}个，开始{len(starts)}次物理拟合，完整结果日志{len(results)}份。',
      '', '只有全部42端点、旧失败复现、前缀等价、两个确定性重复和独立审核通过，才记为数值先导通过。已运行子集不代表完整先导。',
      '', '## 2. 问题、目标与唯一修订','',
      '原RA1在f0/VLESS/G0的RawPre-U100于2000次迭代停止，原梯度1.1157400392713588e-5，未满足1e-5。NR1只把资源配套提高到4000迭代/20000函数评价，沿用原加权CE+.0005*(1+t)||W||²、bias不正则、共同post尺度、96→6模型、固定视图和零初始化。',
      '', 'CUDA float64、Cholesky、原梯度感知LBFGS、strong_wolfe、history_size=100、lr=1、内部容差与严格预算边界保持。没有改模型、rho、t/eta、数值精度门或数据权限；没有Newton、warm start、裁剪或额外归一化。',
      '', '## 3. 固定范围与权限','',
      '42不同端点：四部署×四来源×U50/U100共32；VLESS/G0四来源的SYM50/CPR100共8；VLESS/G1、G2的RawPre-U100共2。另有原预算预期停止复现1次、两个确定性重复，共45尝试上限。全部训练使用原合法源库与目标C，不是源内业务显著性验证。',
      '', '不读取query、H-post、H-pre、实际目标U训练值、标签评分或历史H概率；本轮纯训练求解诊断。','',
      '## 4. 旧停止与第2000步前缀','',
      '旧预算复现：'+json.dumps(oldrep,ensure_ascii=False),'',
      '新轨迹第2000步前缀：'+json.dumps(prefix,ensure_ascii=False),'',
      '前缀是克隆接受点参数/选中梯度的只读观测，不向优化器追加closure、改参数或历史。目标和梯度独立重放在副本上完成。旧失败不回写为成功。','',
      '## 5. 全部已运行拟合明细','',md(show),'',
      '完整机器日志包含训练目标、原/预条件梯度、真实closure与函数评价计数、线搜索、预算和安全退出原因。训练目标下降不作为业务效力结论。','',
      '## 6. 确定性与旧端点兼容','',
      '两个重复状态：'+json.dumps(repeats,ensure_ascii=False),'',
      '若完成N4，audits/overlap-comparison.parquet保存27个新旧交叠端点的参数/logit/迭代精确比较；old-endpoint-compatibility.parquet保存151个原接受端点的只读原坐标审核。未完成N4时不能宣称这些审核已经通过。',
      '', '## 7. 停止原因及边界','',
      json.dumps(stop,ensure_ascii=False,indent=2) if stop else '没有未解决执行停止。',
      '', '若4000/20000仍不合格，当前资源候选到此停止，不扩到6000/8000、不换后端、不删困难控制、不启动完整矩阵。若数值先导通过，也只支持相同训练目标在固定集合可充分求解，不支持RA1分类增量。',
      '', '## 8. 活动成本','',
      f'报告开始前新活动约{started:.3f}秒；旧活动472.9946128996089秒。新先导上限1800秒，1740秒起保留60秒结项窗口；父上限28800秒不重置。累计solver-seconds与活动墙钟分开，最终完整成本见cost-ledger.json与completion.json。',
      '', f'截至本报告拟合求解seconds之和约{sum(x["seconds"] for x in results):.3f}；原失败复现也计费，失败不隐藏。',
      '', '## 9. 记录完整性与下一节点','',
      f'原代码/模型/失败/成本记录哈希未变：{original_unchanged}。新先导未对run-01写入完成状态。',
      '', '没有完整矩阵调度调用。是否恢复完整RA1必须由用户另行确认；旧151与新42最多为166个去重端点而非193，不能把重拟合或重复当成新访问/seed。','']
    textfile(DOC/'numeric-pilot-report-20261018.md','\n'.join(lines))
    # Snapshot actual reads before any final summary. No broad dataset paths are
    # accepted by the pilot's training-only artifact API.
    require(not any('/query.parquet' in x['path'] or '/labels.parquet' in x['path'] for x in READS),'Forbidden read at closeout')
    write(OUT/'read-audit.json',dict(reads=READS,H_query_reads=0,H_label_reads=0,actual_target_U_reads=0))
    duration=elapsed();parent=c['parent_active_seconds'] if c else read(OLD/'cost-ledger.json')['active_seconds']
    write(OUT/'cost-ledger.json',dict(activity_seconds=duration,activity_limit_seconds=1800,parent_prior_activity_seconds=parent,parent_cumulative_activity_seconds=parent+duration,parent_limit_seconds=28800,
          solver_seconds=sum(x['seconds'] for x in results),fit_attempts=len(starts),complete_fit_logs=len(results),failed_or_expected_rejected_fits=sum(not x['accepted'] for x in results),all_attempts_counted=True))
    complete=dict(status=status,pilot_program_complete=numeric_pass,all_42_cases_attempted=len({(x['role_id'],x['policy_id']) for x in results if not x['old_budget'] and x['kind']!='NR1-repeat'})==42,
        all_42_cases_accepted=len(endpoints)==42,old_failure_reproduced=bool(oldrep and oldrep['passed']),old_failure_record_unchanged=original_unchanged,
        prefix_equivalence_pass=bool(prefix and prefix['passed']),deterministic_repeats_pass=bool(repeats and repeats['passed']),original_objective_unchanged=True,original_precision_gates_unchanged=True,
        resource_limits_revised=dict(max_iter=4000,max_eval=20000),physical_fit_attempts=len(starts),accepted_unique_cases=len(endpoints),active_seconds=duration,
        parent_cumulative_active_seconds=parent+duration,H_query_reads=0,H_label_reads=0,actual_target_U_reads=0,full_matrix_auto_start=False,full_matrix_started=False,
        ready_for_full_resume_review=numeric_pass,activity_cap_respected=duration<=1800,report_sha256=sha(DOC/'numeric-pilot-report-20261018.md'))
    write(OUT/'completion.json',complete);progress('pilot_closed',status=status,accepted=len(endpoints),attempts=len(starts))
