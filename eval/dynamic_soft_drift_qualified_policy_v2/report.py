"""Generate outcome or stop report from the current stage, without new fitting."""
from common import *

def table(d,cols):
    d=d[cols];lines=['| '+' | '.join(cols)+' |','| '+' | '.join(['---']*len(cols))+' |']
    for row in d.itertuples(index=False,name=None):lines.append('| '+' | '.join(f'{x:.6f}' if isinstance(x,(float,np.floating)) else str(x) for x in row)+' |')
    return '\n'.join(lines)

def build():
    c=contract();done=read(OUT/'completion.json') if (OUT/'completion.json').exists() else {'status':'in_progress'};cost=read(OUT/'ledger.json')
    inherited=c['inherited_ledger'];combined={k:cost.get(k,0)+inherited.get(k,0) for k in ['logical_forward','new_source_LR','implicit','refinement','validation','q_updates','trial_batches','cache_hits','initial_reuse']}
    write(OUT/'cost-summary.json',dict(new_run=cost,reused_f0=inherited,combined_optimization_counters=combined,optimization_cumulative_hours=cost['active_seconds']/3600,phase_seconds=done.get('phase_seconds',{}),per_arm_cache_cost_not_uniquely_allocated=True))
    text=['# 动态漂移资格启用与固定回退实验报告','',f"运行状态：{done['status']}。本轮保持原资格门与科学目标，将已验收终态启用和精确回退组成完整策略。全部60角色完成且封存后才允许真实post评价；未执行角色不能默认为回退。",'',
        '## 任务与训练条件','',
        '四部署为SS、VLESS、Trojan、VMess；六个domain × activity业务，30内容、每部署每内容四次重复，共480访问。使用96维十个归一化直方图块，五个全局内容折与G0/G1/G2三组业务遮蔽，60角色各有12个合法源内任务。数据、映射、small比例0.1、分类L2、rho=0.01、nu=1和q范围[0,2]均冻结。模型不输入协议身份、IP、端口、SNI或内容文字。','',
        'QP和QT回退至原P-small，QG回退至G-small；回退直接引用冻结模型SHA，不重新拟合。启用仅限stationary或原finite_progress，普通资格失败不改判成功，完整性失败和全局预算停止阻断评价。','',
        '## 预算与来源','',f"累计优化预算20小时，包含复用f0的{inherited['active_seconds']/3600:.6f}小时；当前累计{cost['active_seconds']/3600:.6f}小时。新增源内LR尝试{cost['new_source_LR']}次、隐式评估{cost['implicit']}次；新增最终业务LR{cost['new_final_LR']}次。模型数不能替代源内求解成本。最终拟合、预测、统计及报告耗时独立列在cost-summary.json。",'',
        'f0采用P0不可变封存复用36条终态，12启用、24回退；旧中断阶段读取日志不完整的限制仍保留。其余144条从全1起点按原双档Armijo、固定度量、0.1位移限幅及20接受/40trial预算运行。','']
    decision_path=OUT/'manifests/policy-decisions.parquet'
    if decision_path.exists():
        df=pd.read_parquet(decision_path);rate=df.groupby('arm')[['enabled','fallback','identity']].sum().reset_index();text+=['## 完整资格策略','',table(rate,['arm','enabled','fallback','identity']),'', '主评价包含全部60角色，而不是仅启用子集。逐角色终态、门值、q-use、基线引用及来源见policy-decisions.parquet。','']
    if (OUT/'comparisons/primary.json').exists():
        comp=read(OUT/'comparisons/primary.json');guard=read(OUT/'comparisons/C-cost-guard.json');pooled=pd.read_parquet(OUT/'scores/pooled.parquet');targets=pd.read_parquet(OUT/'scores/targets.parquet')
        text+=['## 完整业务结果','',table(pooled,['arm','F1_U','F1_all','F1_C','CE_U','CE_C','Brier_U','Brier_C','worst_protocol_F1_U']),'',
            '## 部署分项','',table(targets,['arm','target','F1_U','F1_all','F1_C','CE_U','Brier_U']),'',
            '## 七项主检验','',
            'F1_U先合并各部署与遮蔽组五折的完整六分类混淆矩阵，再取未覆盖两类F1均值，部署与遮蔽等权。10000次六业务分层共同内容簇bootstrap，种子20261012，七项Bonferroni家族99.285714%区间。区间条件于固定模型，不计重训练不确定性。','',
            '| 参照 | QP增量 | 家族区间 | 下界为正 |','| --- | --- | --- | --- |']
        for x in comp['comparisons']:text.append(f"| {x['reference']} | {x['delta_F1_U']:.6f} | [{x['CI_99_285714'][0]:.6f}, {x['CI_99_285714'][1]:.6f}] | {x['positive_increment']} |")
        text+=['','## C业务代价门','',f"QP相对P-small总体F1_C变化{guard['overall_delta']*100:.4f}个百分点，最低允许−1个百分点；各部署最低允许−2个百分点。描述性推进门通过：{guard['passed']}。这不是统计非劣效性结论。",'',table(pd.DataFrame(guard['targets']),['target','delta_F1_C','minimum','passed']),'']
        positive={x['reference']:x['positive_increment'] for x in comp['comparisons']}
        if not positive['P-small']:decision='QP未可靠超过P-small，关闭当前十维动态幅度候选，保留原P-small；不默认追加步数或搜索权重。'
        elif not positive['QT']:decision='动态资格策略有新增用途，但关系软约束的独立贡献尚未建立。'
        elif not positive['QG'] or not positive['RawPre-small']:decision='方法改善与精确身份／漂移校准的归因仍须分开。'
        elif not guard['passed']:decision='关键增量与C业务代价不同时满足，不能按完整实用候选推进。'
        else:decision='可保留为新的候选；单侧观测与异批次验证须另行设计与授权。'
        write(OUT/'research-decision.json',dict(decision=decision,automatic_extension=False));text+=['## 结项判断','',decision,'']
    else:text+=['## 当前停止或未决范围','',str(done.get('reason','全部端点尚未封存，未生成新的H业务分数。')),'']
    text+=['## 结果边界','',
        '这是已反复分析队列上的回顾性固定实验，不是全新盲测或外部验证。Hy2和AnyTLS不在本轮；完整物理连接单侧重建、无索引在线识别和异批次泛化均未完成。0916与当前30内容重叠，不作为独立外部集。','',
        '详细产物包括资格决策、600逻辑端点、唯一与新增模型数、14400行预测、逐业务混淆矩阵、C/U错误修复与新增、七项区间以及成本和不可变核验。旧运行及其区间未被覆盖。','']
    textfile(DOC/'complete-report.md','\n'.join(text));return DOC/'complete-report.md'

