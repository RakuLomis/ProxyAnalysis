"""Post-closeout descriptive NR1 interpretation, no fitting or H access."""
from pathlib import Path
import hashlib
import json
import time
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
OLD=ROOT/'outputs/role-asymmetric-transfer-v1-20261017/run-01'
NR=ROOT/'outputs/role-asymmetric-transfer-v1-20261017/numeric-pilot-nr1'
DOC=ROOT/'docs/role-asymmetric-transfer-v1-20261017'

def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def table(df):
    cols=list(df);s=['| '+' | '.join(cols)+' |','| '+' | '.join(['---']*len(cols))+' |']
    for row in df.itertuples(index=False,name=None):s.append('| '+' | '.join(str(x) for x in row)+' |')
    return '\n'.join(s)

def main():
    start=time.perf_counter();comp=read(NR/'completion.json');v=read(NR/'verification.json');c=read(NR/'manifests/contract.json')
    assert comp['pilot_program_complete'] and v['passed'] and not comp['full_matrix_started']
    assert sha(DOC/'numeric-pilot-report-20261018.md')==comp['report_sha256']
    data=pd.read_parquet(NR/'attempt-summary.parquet');unique=data[data.kind.isin(['NR1-hard-case','NR1-case'])].copy()
    assert len(unique)==42 and unique.accepted.all() and len(data)==45
    unique['source']=unique.policy_id.str.split('__').str[0];unique['deployment']=unique.role_id.str.split('/').str[2]
    source=unique.groupby('source').agg(cases=('attempt','size'),median_iterations=('iterations','median'),max_iterations=('iterations','max'),solver_seconds=('seconds','sum'),max_seconds=('seconds','max')).reset_index()
    target=unique.groupby('deployment').agg(cases=('attempt','size'),solver_seconds=('seconds','sum'),max_iterations=('iterations','max')).reset_index()
    raw=source[source.source.eq('RawPre')].iloc[0];hard=unique[unique.kind.eq('NR1-hard-case')].iloc[0]
    oldcase=read(NR/'attempts/001-old-reproduction/result.json');parent=read(OLD/'manifests/contract.json')
    newkeys={(r.role_id,r.policy_id) for r in unique.itertuples()};oldkeys={(r['role_id'],r['policy_id']) for r in c['accepted_old']};union=oldkeys|newkeys
    assert len(union)==166 and len(newkeys&oldkeys)==27
    policies=[p for p in parent['policies'] if p['alias'] is None]
    allkeys={(r['id'],p['id']) for r in parent['roles'] for p in policies};pending=allkeys-union
    assert len(pending)==1754
    # Fresh NR1 time supersedes old time on overlapping keys, fixed without H.
    observations=[]
    for e in c['accepted_old']:
        if (e['role_id'],e['policy_id']) in newkeys:continue
        m=read((ROOT/e['path']).with_suffix('.json'))
        observations.append(dict(deployment=e['role_id'].split('/')[2],source=e['policy_id'].split('__')[0],seconds=m['optimizer']['seconds']))
    observations.extend(unique[['deployment','source','seconds']].to_dict('records'))
    obs=pd.DataFrame(observations);costs=obs.groupby(['deployment','source']).seconds.agg(['count','median','max'])
    rows=[]
    for (deployment,source_name),ss in costs.iterrows():
        n=sum(rid.split('/')[2]==deployment and policy.split('__')[0]==source_name for rid,policy in pending)
        rows.append(dict(deployment=deployment,source=source_name,remaining=n,observed=int(ss['count']),median_seconds=float(ss['median']),max_seconds=float(ss['max']),
                         median_scenario_seconds=n*float(ss['median']),max_observed_scenario_seconds=n*float(ss['max'])))
    forecast=pd.DataFrame(rows);baseline=float(forecast.median_scenario_seconds.sum());conservative=float(forecast.max_observed_scenario_seconds.sum());reserve=600.
    out=NR/'analysis';out.mkdir(parents=True,exist_ok=True)
    source.to_parquet(out/'source-costs.parquet',index=False);target.to_parquet(out/'deployment-costs.parquet',index=False);forecast.to_parquet(out/'remaining-cost-scenarios.parquet',index=False)
    precision=pd.read_parquet(NR/'audits/independent-original-coordinate.parquet')
    summary=dict(new_activity_seconds=comp['active_seconds'],parent_cumulative_activity_seconds=comp['parent_cumulative_active_seconds'],
        unique_case_solver_seconds=float(unique.seconds.sum()),all_solver_seconds=float(data.seconds.sum()),rawpre_time_fraction=float(raw.solver_seconds/unique.seconds.sum()),
        hard_case_time_fraction=float(hard.seconds/unique.seconds.sum()),max_iteration=2974,max_evaluations=int(unique.evaluations.max()),old_prefix_preserved=True,
        hard_objective_reduction_after_2000=oldcase['objective']-float(hard.objective),
        remaining_unique_scientific_endpoints=1754,eligible_old_plus_new_union=166,not_formally_adopted=True,
        remaining_median_scenario_with_600s_reserve=baseline+reserve,remaining_max_observed_scenario_with_600s_reserve=conservative+reserve,
        cost_scenarios_not_bounds_or_time_guarantees=True,all_60_roles_not_verified=True,full_matrix_started=False,H_scored=False)
    fmt=source.copy()
    for col in ['solver_seconds','max_seconds']:fmt[col]=fmt[col].map(lambda x:f'{x:.3f}')
    lines=['# RA1-NR1结果解读与恢复条件','', '日期：2026-10-18。本文件为已封存数值先导的补充解读；不修改原始报告、模型或终态。','',
      '## 1. 核心判断','',
      '**本次同目标数值修订先导通过。**它解决了已知停止点在原2000次额度内不合格的问题，并在固定控制集合上保持原精度门。它不是新业务正结果，尚没有RA1完整H分类成绩。','',
      '## 2. 证据链','',
      '- 旧2000/10000失败从零精确复现，原参数、目标、完整原坐标梯度向量差均为0。',
      '- 新4000/20000轨迹第2000步与旧停止点差均为0，排除了换预算时暗改旧路径的解释。',
      '- 同一难例第2974迭代、5793函数评价达到原坐标梯度9.999096277749238e-6，在新资源上限之前接受。',
      '- 42个不同端点全部通过；另两次重复的参数与训练logits差均为0。',
      '- 27个新旧交叠端点的参数、训练logits及迭代/函数评价计数精确一致；不是扩大资源后强制旧合格模型多跑。',
      '- 151个旧接受端点完成独立原坐标审核，未被直接签入新的完整实验。',
      '', '## 3. 为什么loss几乎不变，仍有必要多跑？','',
      f"已知难例J从{oldcase['objective']:.17g}降至{float(hard.objective):.17g}，额外下降约{summary['hard_objective_reduction_after_2000']:.3e}；但驻点门从未满足变为满足。旧目标变化小没有被误判为原坐标合格，NR1也没有放宽门限。",
      '', '这只证明获得了符合原有限精度标准的解，不声称精确最优、分类一定变化或概率一定改善。下一阶段仍应以完整冻结H评价回答效力，不能拿训练目标下降替代F1_U。',
      '', '## 4. 成本集中在哪里？','',table(fmt),'',
      f"42个不同端点solver-seconds合计{unique.seconds.sum():.3f}；RawPre占{100*summary['rawpre_time_fraction']:.2f}%，已知难例单独占{100*summary['hard_case_time_fraction']:.2f}%。四来源样本数不同，因此同时报告端点数与中位迭代，不把总耗时直接当普遍算法效率结论。",
      '', f"全部45次物理拟合（包含旧失败复现及重复）solver-seconds合计{data.seconds.sum():.3f}。NR1主执行活动{comp['active_seconds']:.3f}秒，约{comp['active_seconds']/60:.2f}分钟；连同旧活动累计{comp['parent_cumulative_active_seconds']:.3f}秒，约{comp['parent_cumulative_active_seconds']/60:.2f}分钟。均低于30分钟子上限及8小时父上限。",
      '', f"42端点独立审核最大原梯度{precision.gradient.max():.9e}；目标重放最大误差{precision.objective_error.max():.3e}，梯度重放最大误差{precision.gradient_error.max():.3e}。",
      '', '## 5. 剩余完整运行的资源情景（未启动）','',
      '151旧接受与42先导去重合计166个端点，不能相加成193。若后续另获恢复授权并通过采纳审核，仍有1754个不同科学端点待补。420个历史参考别名另列，不是新增科学拟合。',
      '', f"按部署×来源分层，以166个去重已有合格端点的求解时长作为观测，剩余1754模型采用分层中位数的参考情景约{(baseline+reserve)/60:.1f}分钟；每层采用最大已观测接受时长的保守情景约{(conservative+reserve)/60:.1f}分钟。两者均另含600秒非拟合预留。分层明细在analysis/remaining-cost-scenarios.parquet。",
      '', '这些是经验资源情景，不是统计区间或严格上下界：尚未覆盖全部折、t/eta、分配与极端输入；也未预测潜在新失败重试。已知VLESS/RawPre慢点会抬高最大观测情景，因此不再沿用旧48模型先导的约88分钟作为新保证。',
      '', '## 6. 是否可以直接恢复？','',
      '数值上已具备提交完整恢复审议的依据；操作上仍未获本轮自动启动权限，程序已经退出。建议保持NR1统一预算和原精度门，另立正式恢复合同、输入/模型采纳台账与累计成本，保留run-01失败。27个交叠端点按事前政策优先采用NR1版本，不能按成绩挑旧/新。',
      '', '完整实验仍需所有2340逻辑端点封存、再统一H-post预测、全部预测封存后统一标签评分。不允许先评分f0或启用子集。先导通过不能保证所有剩余模型也在4000/20000内合格，遇新数值失败仍须按合同停止。',
      '', '## 7. 未改变的边界','',
      '没有实际H/query读取、实际目标U训练值读取、历史H概率选择或新测试分类分数。没有映射/尺度/CORAL重拟合、模型扩容、t/eta/rho搜索、额外bias正则、Newton或温度校准。训练/数学诊断是CUDA float64，统计整理在CPU；仅本补充解读不产生任何新拟合。',
      '', '部署为四个历史TCP部署，不推广到AnyTLS/Hy2、跨日期/新节点或无索引在线识别。此先导不消除历史H重复研究的限制。',
      '', '详细45次拟合记录见numeric-pilot-report-20261018.md；机器终态见numeric-pilot-nr1/completion.json与verification.json。','']
    (DOC/'NR1-results-interpretation-20261018.md').write_text('\n'.join(lines),encoding='utf-8')
    assert sha(DOC/'numeric-pilot-report-20261018.md')==comp['report_sha256']
    for p,h in c['preserve'].items():assert sha(ROOT/p)==h
    summary['additional_readonly_analysis_seconds']=time.perf_counter()-start
    summary['parent_cumulative_including_this_analysis_seconds']=comp['parent_cumulative_active_seconds']+summary['additional_readonly_analysis_seconds']
    (out/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
