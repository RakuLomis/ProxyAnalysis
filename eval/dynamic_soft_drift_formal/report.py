"""Local status/closeout report; failed or incomplete runs have no business claims."""
from common import *

def table(d):return d.to_markdown(index=False,floatfmt='.6f')

def run():
    state=read(OUT/'completion.json') if (OUT/'completion.json').exists() else read(OUT/'progress.json')
    ledger_=read(OUT/'ledger.json');status=state.get('status',state.get('stage','unknown'))
    lines=['# 动态软约束漂移正式业务实验执行报告','',f'更新日期：2026年10月12日。当前状态：`{status}`。','',
           '本轮保持extend四部署、六业务、五折全局内容划分和原P-small资源口径，以充分求解LR后的隐式梯度学习十块漂移幅度。新臂为D-P、T-P、D-G；七类旧参照不重新训练或选择。',
           '', '## 执行状态','',json.dumps(state,ensure_ascii=False,indent=2),'','## 计算账本','',table(pd.DataFrame([ledger_])),'',
           '训练和数值微分使用Pytorch312、CUDA float64。实际目标U两侧、测试pre和PCAP均不进入本流程。所有600端点封存后才允许H-post查询；全部14400行预测封存后才允许H标签评分。','']
    for name in ['registration.json','audits/permission-tests.json','audits/OOF-replay.json','audits/q-one-replay.json','batch-one-audit.json']:
        p=OUT/name
        if p.exists():lines+=['## '+name.replace('/',' ').replace('.json',''),'', '```json',json.dumps(read(p),ensure_ascii=False,indent=2),'```','']
    if (OUT/'stages/score.json').exists():
        lines+=['## 业务结果','',table(pd.read_parquet(OUT/'scores/pooled.parquet')),'','## 各部署结果','',table(pd.read_parquet(OUT/'scores/targets.parquet')),
                '','## 七项预定主比较','',table(pd.DataFrame(read(OUT/'comparisons/primary.json')['comparisons'])),'',
                'F1_U来自每部署与遮蔽组合合并五折后的完整六类混淆矩阵，再取未覆盖两类并等权平均。主区间采用10000次共享内容bootstrap及七项Bonferroni家族。区间条件于固定模型，不代表外部验证或重训练不确定性。','']
    else:lines+=['## 业务评价边界','','正式评分尚未执行，不能根据已接受数值解、源内CE或部分q轨迹判断D-P是否优于P-small、T-P或D-G。','']
    failures=list((OUT/'failures').glob('*.json'))
    if failures:
        lines+=['## 停止原因','']
        for p in failures:
            info=read(p);lines+=[f'- {info.get("stage",info.get("role_id","numeric"))}：{info.get("exception","见失败资产")}。',f'  证据：`{rel(p)}`。']
        lines+=['','失败版本保留；不会自动增加预算、放宽验收门、跳过任务或改用先前梯度。后续修订需独立版本。','']
    lines+=['## 复现入口','','`D:/Tools/Anaconda/envs/Pytorch312/python.exe eval/dynamic_soft_drift_formal/run.py prepare`','',
            '`D:/Tools/Anaconda/envs/Pytorch312/python.exe eval/dynamic_soft_drift_formal/run.py formal`','',
            '阶段命令不覆盖已完成产物；formal拒绝已登记的失败版本。报告可以用独立report命令更新。','']
    textfile(DOC/'execution-report-20261012.md','\n'.join(lines))

if __name__=='__main__':run()
