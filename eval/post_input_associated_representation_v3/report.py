"""Frozen reports; no H-triggered refit or Stage B start."""
from common import *

def table(d):
    cols=list(d);rows=['| '+' | '.join(cols)+' |','| '+' | '.join(['---']*len(cols))+' |']
    for _,r in d.iterrows():rows.append('| '+' | '.join(f'{v:.6f}' if isinstance(v,(float,np.floating)) else str(v) for v in r)+' |')
    return '\n'.join(rows)

def run():
    with stage('P4_report'):
        require(read(OUT/'verification.json')['passed'],'Verification before success report')
        scores=pd.read_parquet(OUT/'scores/pooled.parquet');targets=pd.read_parquet(OUT/'scores/targets.parquet')
        primary=read(OUT/'comparisons/primary.json');guard=read(OUT/'comparisons/C-cost-guard.json');decs=read(OUT/'selections/decisions.json')
        coverage=pd.DataFrame(decs).groupby('arm')[['enabled','fallback']].sum().reset_index()
        rows=pd.DataFrame([dict(reference=v['reference'],delta_F1_U=v['delta_F1_U'],interval=str(v['CI_98_333333']),positive=v['positive_increment']) for v in primary['comparisons']])
        success=all(v['positive_increment'] for v in primary['comparisons']) and guard['passed']
        content='# post输入关联表征残差分支完整报告\n\n日期：2026年10月14日登记；实际时间以阶段日志为准。Stage A已经完成；Stage B未启动。\n\n'
        content+='固定四TCP部署、30内容、480访问、96维和60角色。P-small主路冻结，八维pre监督瓶颈由post输入分支估计；最终只读取post。实际目标U两侧及H-pre不用于拟合。\n\n'
        content+='## 完整业务结果\n\n'+table(scores)+'\n\n## 三项主比较\n\n'+table(rows)+'\n\n'
        content+='三项共同家族98.333333%区间，10000次业务分层共同内容bootstrap。三seed先各自计算指标再等权平均，不集成概率。区间条件于固定模型，不是外部验证。\n\n'
        content+='## 源内启用和固定回退\n\n'+table(coverage)+'\n\n## 部署结果\n\n'+table(targets)+'\n\n'
        content+=f"H上C代价门通过：{guard['passed']}。没有用H决定回退或重新训练。完整候选判据通过：{success}。\n\n"
        content+='所有新臂共享已使用精确配对的P-small基座。A3与A2仅检验新增表征目标的对应层级，不能据此声称整个系统没有其他精确关联。\n\n'
        content+='## 计算和复核\n\n```json\n'+json.dumps(read(OUT/'ledger.json'),indent=2)+'\n```\n\n'
        content+='教师、基座、源内与最终拟合分别计数；逻辑端点不是新增拟合数。回退为原基座精确别名。独立deploy.py不导入教师或训练表，全部端点逐一精确重放。\n\n'
        content+='本轮保持离线关联辅助的观测条件，未验证无索引在线分段、AnyTLS/Hy2、外部节点、跨日期或独立内容批次。\n'
        textfile(DOC/'complete-report.md',content)
        write(OUT/'completion.json',dict(status='stage_A_complete',passed=True,formal_complete=True,H_scored=True,
              scientific_primary_passed=success,Stage_B_started=False,verification_sha256=sha(OUT/'verification.json'),
              report_path=rel(DOC/'complete-report.md'),report_sha256=sha(DOC/'complete-report.md'),end_unix=time.time()))

if __name__=='__main__':run()
