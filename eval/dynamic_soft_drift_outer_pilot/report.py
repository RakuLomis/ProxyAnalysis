"""Source-only closeout. No classifier scores or target data readers."""
from common import *

def build():
    completion=read(OUT/'completion.json');summary=read(OUT/'quality-summary.json') if (OUT/'quality-summary.json').exists() else dict(results=[])
    results=summary['results'];rows=[];blocks=[];oldrows=[]
    for r in contract()['roles']:
        for arm in ARMS:
            path=OUT/'trajectories'/r['id']/arm/'result.json'
            if not path.exists():
                fp=path.with_name('failure.json');failure=read(fp) if fp.exists() else {}
                rows.append(dict(role_id=r['id'],target=r['target'],group=r['group'],arm=arm,status=failure.get('status','not_completed'),passed=False,accepted_updates=failure.get('accepted_updates',0),reason=failure.get('reason')));continue
            x=read(path);row={k:v for k,v in x.items() if not isinstance(v,dict)}
            for name in ['origin_residual','terminal_residual','residual_ratios']:
                for k,v in x.get(name,{}).items():row[name+'_'+k]=v
            rows.append(row)
            sp=path.with_name('states.parquet')
            if sp.exists():
                states=pd.read_parquet(sp)
                for _,s in states.iterrows():
                    for j in range(10):blocks.append(dict(role_id=r['id'],target=r['target'],group=r['group'],arm=arm,state=s.state,feature=FEATURES[j],q=float(s.q[j]),gap=float(s.gap[j]),penalty_part=float(s.penalty_parts[j]),task_gradient=float(s.task_gradient_f[j]),relation_gradient=float(s.penalty_gradient[j]),total_gradient=float(s.g_f[j])))
            legacy={'O-DP':'D-P','O-TP':'T-P','O-DG':'D-G'}[arm]
            old=parent_asset(PARENT/'trajectories'/r['id']/(legacy+'.parquet'),'old-source-trajectory',kind_for(arm),r['id'],'report')
            first,last=old.iloc[0],old.iloc[-1]
            oldrows.append(dict(role_id=r['id'],arm=arm,old_total_origin=first.total,old_total_terminal=last.total,old_Q_origin=first.Q,old_Q_terminal=last.Q,new_total_origin=x.get('L_origin'),new_total_terminal=x.get('L_terminal'),new_Q_terminal=x.get('Q_terminal'),descriptive_only=True))
    d=pd.DataFrame(rows);save(d,OUT/'tables/quality.parquet')
    if blocks:save(pd.DataFrame(blocks),OUT/'tables/block-diagnostics.parquet')
    if oldrows:save(pd.DataFrame(oldrows),OUT/'tables/old-source-comparison.parquet')
    counts=d.groupby(['arm','status']).size().reset_index(name='count');save(counts,OUT/'tables/status-counts.parquet')
    table='| 部署 | 组 | 臂 | 状态 | 接受更新 | 总目标起点 | 总目标终点 | 原投影残差终点 |\n| --- | --- | --- | --- | ---: | ---: | ---: | ---: |\n'
    def fmt(v):return '未完成' if v is None or pd.isna(v) else f'{v:.6g}'
    for x in rows:table+=f"| {x['target']} | {x['group']} | {x['arm']} | {x['status']} | {x['accepted_updates']} | {fmt(x.get('L_origin'))} | {fmt(x.get('L_terminal'))} | {fmt(x.get('terminal_residual_PG_f'))} |\n"
    led=read(OUT/'ledger.json');npass=int(d.passed.sum());message='36条轨迹均达到预登记数值资格，仍需确认才进入业务。' if npass==36 else f'{npass}/36条轨迹获得预登记数值资格；未获资格轨迹保留在分母中，不自动进入业务。'
    text=f'''# 动态软约束漂移外层优化先导结果

本轮状态为{completion['status']}。{message}本轮没有拟合最终业务分类器，没有读取H或实际目标U，也没有新增F1、CE业务评价或bootstrap。

## 实验范围

固定外层f0的四部署、三个遮蔽组，共12角色和36轨迹；每条轨迹使用12个等权合法源内任务。P/T共享P映射与尺度，G只用自己的匿名组资产。允许实际目标C原训练系数，不把本轮称为完全无目标部署信息的泛化实验。

原目标、0.1 small比例、96维输入、LR的原W正则与bias无正则均保持。新增外层程序使用M=1+A/s固定度量、尺度位移0.1限幅、[0,2]投影、最多8次双档Armijo回溯。所有目标和质量仍在原q坐标计算。候选使用充分LR、fine精炼和真实一次Newton校验，接受后才计算并验收f/v隐式梯度。

## 逐角色结果

{table}
stationary只表示本政策下近似一阶驻点。finite_progress只允许在20个接受更新的正常终态评定，需总目标改善和原投影残差下降80%。预算、线搜索、信号或小步长停止不重命名为成功；单调下降不等于充分优化。

## 计算与权限

实际新源内LR {led['new_source_LR']}次，逻辑任务前向{led['logical_forward']}次，初始化缓存复用{led['initial_reuse']}次，其他精确缓存命中{led['cache_hits']}次，隐式评估{led['implicit']}次，接受更新{led['q_updates']}次。累计活动计算{led['active_seconds']/3600:.4f}小时，上限4小时。业务LR、H查询、H评分与bootstrap计数均为零。

## 解释边界和停止决定

源内目标变化只能说明既定数值程序的优化质量，不证明真实目标post收益，也不替代未见内容、跨配置或外部批次验证。旧q20、P-small及run-02业务结果不覆盖、不回选。旧源内轨迹仅作为描述参照，不用于本轮初值或更新选择。

完整状态表、接受及拒绝候选、块梯度与惩罚分项、原投影残差、旧源内参照、计数与独立核验保存在新运行目录。无论是否获资格，本轮到先导报告停止；新的180模型业务矩阵必须另行确认。
'''
    textfile(DOC/'pilot-results.md',text)
    write(OUT/'report-manifest.json',dict(report=rel(DOC/'pilot-results.md'),sha256=sha(DOC/'pilot-results.md'),business_scores_created=False))
