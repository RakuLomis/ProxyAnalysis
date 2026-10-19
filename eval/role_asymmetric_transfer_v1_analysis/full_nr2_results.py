"""Read-only full NR2 result analysis; no model fits or source H/pre reads."""
import time
LOAD_START=time.perf_counter()
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'outputs/role-asymmetric-transfer-v1-20261017/full-nr2-01'
DOC=ROOT/'docs/role-asymmetric-transfer-v1-20261017/full-nr2'
OUT=RUN/'result-analysis-20261018'
PRIMARY='P__m025__UPR'
REFS=['P__m010__SYM','P__m025__SYM','G__m025__UPR','RawPre__m025__UPR','RawPost__m025__UPR','S']
NAMES={PRIMARY:'P-U50（主候选）',REFS[0]:'P-small / SYM10',REFS[1]:'P-SYM25',REFS[2]:'G-U50',REFS[3]:'RawPre-U50',REFS[4]:'RawPost-U50','S':'S（强post）','P-full':'P-full','G-full':'G-full'}
SHORT={PRIMARY:'P-U50',REFS[0]:'P-small',REFS[1]:'P-SYM25',REFS[2]:'G-U50',REFS[3]:'RawPre-U50',REFS[4]:'RawPost-U50','S':'StrongPost'}
PROTOCOLS=['shadowsocks','vless','trojan','vmess']
PN={'shadowsocks':'SS','vless':'VLESS','trojan':'Trojan','vmess':'VMess'}
LABELS=['bing.com::search_results_view','developer.mozilla.org::document_view','github.com::repository_view',
        'wikipedia.org::article_view','youtube.com::search_results_view','youtube.com::video_playback']
BUS=['Bing搜索','MDN文档','GitHub仓库','Wikipedia文章','YouTube搜索','YouTube播放']
MASKS={'G0':[2,4],'G1':[0,3],'G2':[1,5]}

def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def require(ok,msg):
    if not bool(ok):raise RuntimeError(msg)
def rel(p):return Path(p).relative_to(ROOT).as_posix()
def table(frame):
    if not isinstance(frame,pd.DataFrame):frame=pd.DataFrame(frame)
    def cell(x):
        if isinstance(x,(float,np.floating)):return '—' if np.isnan(x) else f'{x:.6f}'
        return str(x).replace('|','\\|').replace('\n',' ')
    cols=list(frame);lines=['| '+' | '.join(cols)+' |','| '+' | '.join(['---']*len(cols))+' |']
    lines.extend('| '+' | '.join(cell(v) for v in row)+' |' for row in frame.itertuples(index=False,name=None))
    return '\n'.join(lines)
def matrix_table(cm):
    d=pd.DataFrame(cm,columns=[f'预测{k}' for k in range(6)]);d.insert(0,'真实类别',[str(k) for k in range(6)]);return table(d)
def f1(cm):
    den=cm.sum(0)+cm.sum(1)
    return np.divide(2*np.diag(cm),den,out=np.zeros(6),where=den>0)
def frame(name):return pd.read_parquet(RUN/'scores'/(name+'.parquet'))
def main():
    comp=read(RUN/'completion.json');verification=read(RUN/'verification.json');contract=read(RUN/'manifests/contract.json')
    require(comp['program_complete'] and comp['H_scored'] and verification['passed'],'Full experiment not complete')
    require(not (RUN/'failure.json').exists() and not (RUN/'run.lock').exists(),'Unresolved stop/lock')
    require(sha(RUN/'verification.json')==comp['verification_sha256'],'Verification seal')
    require(sha(DOC/'complete-report.md')==verification['report_sha256'],'Original report seal')
    require(sha(RUN/'manifests/contract.json')==read(RUN/'manifests/seal.json')['sha256'],'Contract seal')
    require(sha(RUN/'manifests/endpoints.parquet')==read(RUN/'manifests/endpoint-seal.json')['sha256'],'Endpoint seal')
    require(sha(RUN/'predictions/visits.parquet')==read(RUN/'predictions/complete.json')['sha256'],'Prediction seal')
    paths=[RUN/'completion.json',RUN/'verification.json',RUN/'cost-final.json',RUN/'manifests/contract.json',RUN/'manifests/seal.json',
           RUN/'manifests/endpoints.parquet',RUN/'manifests/endpoint-seal.json',RUN/'predictions/complete.json',RUN/'predictions/visits.parquet',
           RUN/'comparisons/primary.json',RUN/'comparisons/descriptive.json',RUN/'comparisons/bootstrap.npz',DOC/'complete-report.md']
    paths += list((RUN/'scores').glob('*'))+list((RUN/'stages').glob('*.json'))
    bound={rel(p):sha(p) for p in paths if p.is_file()}
    primary=read(RUN/'comparisons/primary.json');cost=read(RUN/'cost-final.json');ccost=read(RUN/'scores/C-practical-cost.json')
    pooled=frame('pooled').set_index('policy_id');targets=frame('targets');classes=frame('classes');flips=frame('error-transitions')
    d=frame('labeled-predictions');raw=pd.read_parquet(RUN/'predictions/visits.parquet');ends=pd.read_parquet(RUN/'manifests/endpoints.parquet')
    new=pd.read_parquet(RUN/'manifests/new-endpoints.parquet');scenario=frame('scenarios').set_index(['policy_id','target','group'])
    require(len(d)==len(raw)==56160 and d.visit_id.nunique()==480 and d.content_id.nunique()==30,'Prediction/data coverage')
    require(len(ends)==2340 and len(new)==1296,'Model coverage')
    keys=['role_id','policy_id','visit_id'];pc=[f'p{k}' for k in range(6)];lp=[f'logp{k}' for k in range(6)]
    a=d.set_index(keys).sort_index();b=raw.set_index(keys).sort_index()
    require(a.index.equals(b.index) and np.array_equal(a[pc+lp+['prediction']],b[pc+lp+['prediction']]),'Derived scored predictions differ from sealed export')
    max_metric_error=0.;cm_by={}
    for key,p in d.groupby(['policy_id','target','group']):
        y=p.label_id.map(dict(zip(LABELS,range(6)))).to_numpy();z=p.prediction.to_numpy(int)
        cm=np.bincount(y*6+z,minlength=36).reshape(6,6);cf=f1(cm);expected=scenario.loc[key]
        max_metric_error=max(max_metric_error,abs(float(cf[MASKS[key[2]]].mean())-expected.F1_U),abs(float(cf.mean())-expected.F1_all))
        cm_by[key]=cm
    require(max_metric_error<1e-12,'Independent confusion replay')
    scope_audits=[]
    for r in contract['roles']:
        contents=set(d[d.role_id.eq(r['id'])].content_id.unique())
        require(not contents&set(r['train_contents']) and contents==set(r['validation_contents']),'Global train/test content scope')
        require(len(r['train_contents'])==24 and len(contents)==6 and len(r['C_contents'])==16 and len(r['U_contents'])==8,'Role content counts')
        scope_audits.append(dict(role_id=r['id'],train_contents=24,H_contents=6,intersection=0))
    bootstrap=np.load(RUN/'comparisons/bootstrap.npz',allow_pickle=False);arms=list(bootstrap['arms']);uu=bootstrap['F1_U']
    for v in primary['comparisons']:
        delta=uu[:,arms.index(PRIMARY)]-uu[:,arms.index(v['reference'])]
        ci=np.quantile(delta,[.05/12,1-.05/12],method='linear');require(np.max(np.abs(ci-v['CI_family']))<1e-12,'Primary interval replay')
        require(abs(float(pooled.loc[PRIMARY,'F1_U']-pooled.loc[v['reference'],'F1_U'])-v['delta_F1_U'])<1e-12,'Primary point replay')
    reads=[];stages=[]
    for p in (RUN/'stages').glob('*.json'):
        s=read(p);require(s['passed'],'Incomplete stage');reads.extend(s['reads']);stages.append(dict(stage=p.stem,seconds=s['seconds']))
    p4=read(RUN/'stages/P4.json');p5=read(RUN/'stages/P5.json')
    query=[r for r in reads if r['purpose']=='query'];label=[r for r in reads if r['purpose']=='score']
    require(all(r['time_unix']>=p4['ended_unix'] for r in query),'Query precedes model seal')
    require(all(r['time_unix']>=p5['ended_unix'] for r in label),'Labels precede prediction stage completion')
    # Confirm every newly fitted endpoint was accepted; summarize actual Newton behavior.
    traces=[]
    for r in new[new.newton_updates.gt(0)].itertuples():
        log=read(ROOT/r.result_path);require(log['accepted'] and log['newton_updates']==1,'Unexpected second-order result')
        traces.extend(t for t in log['newton_trace'] if 'damping_attempts' in t)
    require((new.gradient_inf<=1e-5).all() and new.iterations.max()<4000,'New model original gradient/update gates')
    OUT.mkdir(parents=True,exist_ok=True);fig=DOC/'figures';fig.mkdir(exist_ok=True)
    # Confirmatory six-comparison intervals, not a post-hoc family.
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    fs,ax=plt.subplots(figsize=(8.2,4.1))
    for i,v in enumerate(primary['comparisons']):
        point=100*v['delta_F1_U'];lo,hi=100*np.array(v['CI_family']);color='#c34747' if v['negative'] else ('#218454' if v['positive'] else '#627484')
        ax.errorbar(point,i,xerr=[[point-lo],[hi-point]],fmt='o',capsize=4,color=color)
    ax.set_yticks(range(6),[SHORT[r] for r in REFS]);ax.invert_yaxis();ax.axvline(0,color='#666',lw=1,ls='--')
    ax.set_xlabel('P-U50 minus reference: macro F1_U (percentage points)');ax.set_title('Pre-registered six-comparison intervals (99.1667% each)');ax.grid(axis='x',alpha=.2)
    fs.tight_layout();fs.savefig(fig/'primary-comparisons.png',dpi=180);plt.close(fs)
    fs,axes=plt.subplots(2,2,figsize=(10,7),sharey=True,sharex=True)
    for ax,source in zip(axes.flat,['P','G','RawPre','RawPost']):
        for alloc,marker in [('SYM','o'),('UPR','s'),('CPR','^')]:
            ys=[100*pooled.loc[f'{source}__m{m:03d}__{alloc}','F1_U'] for m in [10,25,50]]
            ax.plot([10,25,50],ys,marker=marker,label=alloc)
        ax.axhline(100*pooled.loc['S','F1_U'],color='#777',ls='--',lw=1,label='StrongPost')
        ax.set_title(source);ax.set_ylim(45,85);ax.grid(alpha=.2);ax.set_xlabel('Mean auxiliary replacement m (%)');ax.set_ylabel('Macro F1_U (%)')
    axes.flat[0].legend(ncol=2,fontsize=8);fs.suptitle('All fixed dose/allocation points: descriptive, no winner selection')
    fs.tight_layout();fs.savefig(fig/'dose-allocation.png',dpi=180);plt.close(fs)
    fs,ax=plt.subplots(figsize=(8.8,4.1));x=np.arange(4)
    for j,pid in enumerate([REFS[0],REFS[1],PRIMARY]):
        vals=targets[targets.policy_id.eq(pid)].set_index('target').loc[PROTOCOLS,'F1_U']*100
        ax.bar(x+(j-1)*.24,vals,.24,label=SHORT[pid])
    ax.set_xticks(x,[PN[p] for p in PROTOCOLS]);ax.set_ylim(0,100);ax.set_ylabel('Macro F1_U (%)');ax.set_title('Deployment breakdown (point estimates, descriptive)');ax.legend(ncol=3);ax.grid(axis='y',alpha=.2)
    fs.tight_layout();fs.savefig(fig/'deployment-breakdown.png',dpi=180);plt.close(fs)
    # Main tables.
    mainrows=[]
    for pid in [PRIMARY,*REFS]:
        q=pooled.loc[pid];mainrows.append(dict(方法=NAMES[pid],F1_U百分比=100*q.F1_U,F1_C百分比=100*q.F1_C,F1_all百分比=100*q.F1_all,CE_U=q.CE_U,Brier_U=q.Brier_U,最差部署F1_U百分比=100*q.worst_target_F1_U))
    comparisons=[]
    for v in primary['comparisons']:
        comparisons.append(dict(参照=NAMES[v['reference']],ΔF1_U_pp=100*v['delta_F1_U'],校正区间pp=f"[{100*v['CI_family'][0]:+.4f}, {100*v['CI_family'][1]:+.4f}]",
            ΔCE_U=v['delta_CE_U'],ΔBrier_U=v['delta_Brier_U'],裁决='正向证据' if v['positive'] else ('负向证据' if v['negative'] else '区间跨零，未定')))
    deployment=[]
    for p in PROTOCOLS:
        z=targets[targets.target.eq(p)].set_index('policy_id');deployment.append(dict(部署=PN[p],P_U50=100*z.loc[PRIMARY,'F1_U'],P_small=100*z.loc[REFS[0],'F1_U'],
            P_SYM25=100*z.loc[REFS[1],'F1_U'],G_U50=100*z.loc[REFS[2],'F1_U'],Δ对Psmall_pp=100*(z.loc[PRIMARY,'F1_U']-z.loc[REFS[0],'F1_U']),
            ΔCE_U对Psmall=z.loc[PRIMARY,'CE_U']-z.loc[REFS[0],'CE_U'],ΔC_F1对Psmall_pp=100*ccost['per_deployment'][p]))
    cu=classes[classes.scope.eq('U')].groupby(['policy_id','label_index']).agg(F1=('F1','mean'),precision=('precision','mean'),recall=('recall','mean'),TP=('TP','sum'),FP=('FP','sum'),FN=('FN','sum'))
    business=[]
    for k in range(6):
        c=cu.loc[(PRIMARY,k)];old=cu.loc[(REFS[0],k)];delta=100*(c.F1-old.F1)
        business.append(dict(业务=BUS[k],主候选F1_U百分比=100*c.F1,Psmall_F1_U百分比=100*old.F1,Δ_pp=delta,对总体Δ贡献pp=delta/6,
            Precision百分比=100*c.precision,Recall百分比=100*c.recall,TP=int(c.TP),FP=int(c.FP),FN=int(c.FN)))
    fliprows=[];probrows=[]
    for ref in REFS:
        for scope in ['U','C']:
            f=flips[flips.reference.eq(ref)&flips.scope.eq(scope)];n=len(f);ct=f.state.value_counts()
            fliprows.append(dict(参照=SHORT[ref],范围=scope,行数=n,共同正确=int(ct.get('both_correct',0)),共同错误=int(ct.get('both_wrong',0)),修复=int(ct.get('repaired',0)),新增错误=int(ct.get('new_error',0)),正确数净变化=int(ct.get('repaired',0)-ct.get('new_error',0))))
            if ref==REFS[0] and scope=='U':
                for st in ['both_correct','repaired','new_error','both_wrong']:
                    ff=f[f.state.eq(st)];probrows.append(dict(分组=st,访问数=len(ff),CE差贡献=ff.delta_CE.sum()/n,Brier差贡献=ff.delta_Brier.sum()/n,
                        条件平均ΔCE=ff.delta_CE.mean(),条件平均ΔBrier=ff.delta_Brier.mean()))
    # Content diagnosis: fixed paired prediction flips, not new tests.
    fu=flips[flips.reference.eq(REFS[0])&flips.scope.eq('U')]
    ct=fu.groupby(['content_id','label_id','state']).size().unstack(fill_value=0)
    for col in ['new_error','repaired']:
        if col not in ct:ct[col]=0
    ct['net_errors']=ct.new_error-ct.repaired
    ce=fu.groupby(['content_id','label_id']).delta_CE.mean();ct['delta_CE']=ce
    contentrows=[]
    for (content,labelid),q in ct.sort_values(['net_errors','delta_CE'],ascending=False).head(8).iterrows():
        contentrows.append(dict(内容=content,业务=BUS[LABELS.index(labelid)],新增错误=int(q.new_error),修复=int(q.repaired),净新增=int(q.net_errors),ΔCE=q.delta_CE))
    descriptive=read(RUN/'comparisons/descriptive.json');allocation=[]
    for source in ['P','G','RawPre','RawPost']:
        for m in [10,25,50]:
            a=f'{source}__m{m:03d}__UPR';b=f'{source}__m{m:03d}__SYM';v=next(v for v in descriptive if v['candidate']==a and v['reference']==b)
            allocation.append(dict(来源=source,m百分比=m,UPR_F1_U百分比=100*pooled.loc[a,'F1_U'],SYM_F1_U百分比=100*pooled.loc[b,'F1_U'],Δ_UPR减SYM_pp=100*v['delta_F1_U'],描述性CI95_pp=f"[{100*v['CI95'][0]:+.4f},{100*v['CI95'][1]:+.4f}]"))
    allpol=[]
    order=['S','P-full','G-full']+[f'{s}__m{m:03d}__{al}' for s in ['P','G','RawPre','RawPost'] for m in [10,25,50] for al in ['SYM','UPR','CPR']]
    for pid in order:
        q=pooled.loc[pid];allpol.append(dict(政策=pid,F1_U百分比=100*q.F1_U,F1_C百分比=100*q.F1_C,F1_all百分比=100*q.F1_all,CE_U=q.CE_U,Brier_U=q.Brier_U,最差部署F1_U百分比=100*q.worst_target_F1_U))
    newstats=new.assign(source=new.policy_id.str.split('__').str[0]).groupby('source').agg(新拟合数=('policy_id','size'),Newton触发=('newton_updates',lambda z:int((z>0).sum())),最大LBFGS=('lbfgs_updates','max'),最大Newton=('newton_updates','max'),最大总更新=('iterations','max'),求解秒=('seconds','sum')).reset_index()
    stageorder=['R0','E0','R1','P3','P4','P5','P6','report','verify'];stageframe=pd.DataFrame(stages).set_index('stage').loc[stageorder].reset_index()
    delta_ss=next(x['Δ对Psmall_pp'] for x in deployment if x['部署']=='SS');total_decline=100*(pooled.loc[PRIMARY,'F1_U']-pooled.loc[REFS[0],'F1_U'])
    metadata=dict(status='full_NR2_completed_analysis_verified',completed=True,main_candidate_upgrade_supported=False,
        negative_vs_Psmall=True,negative_vs_same_mass_SYM25=True,positive_vs_RawPre=True,exact_pair_increment_established=False,
        models=2340,new_fits=1296,adopted_scientific=624,historical_aliases=420,unique_visits=480,contents=30,roles=60,logical_predictions=56160,
        U_rows_per_policy=480,C_rows_per_policy=960,H_pre_reads=verification['H_pre_reads'],actual_target_U_training_reads=verification['actual_target_U_training_reads'],
        scope_train_H_content_intersection_max=0,query_events=len(query),score_events=len(label),original_point_metric_replay_max=max_metric_error,
        new_Newton_cases=int(new.newton_updates.gt(0).sum()),new_Newton_updates=int(new.newton_updates.sum()),new_nonzero_damping_steps=sum(x['mu']>0 for x in traces),
        new_max_gradient=float(new.gradient_inf.max()),new_max_updates=int(new.iterations.max()),new_max_optimization_evaluations=int(new.evaluations.max()),
        new_solver_seconds=float(new.seconds.sum()),new_solver_median_seconds=float(new.seconds.median()),new_solver_max_seconds=float(new.seconds.max()),
        original_report_unchanged=True,source_hashes=bound,no_new_training=True,no_restart=True)
    # Human report; original sealed complete-report.md is intentionally not changed.
    report=f'''# RA1 Full NR2完整实验结果分析报告

日期：2026-10-18。状态：**完整实验已正常完成，全部数值、模型/预测封存及独立复核通过；没有新的停止或重启。**

本报告只分析已有输出，没有修改设置、重训模型、重新拟合映射、调温度或重新选择政策。原封存报告、completion、verification和历史停止记录保持不变。

## 1. 执行摘要与结论分层

本轮最终把此前因RawPre困难参照而中断的同一项RA1实验做完。二阶修订解决了这批实际问题的求解障碍，但**预先指定的P-U50并未成为P-small的升级方案**：

- P-U50的F1_U为**{100*pooled.loc[PRIMARY,'F1_U']:.4f}%**，P-small为**{100*pooled.loc[REFS[0],'F1_U']:.4f}%**；差**{total_decline:+.4f}个百分点**，六项家族校正区间全为负。
- 相对同替换质量P-SYM25也出现负向证据，不能将失败仅归于“总增广量不同”。
- 相对RawPre-U50有正向业务证据，支持在这一固定比较中使用漂移变换优于直接补充入口视图；不等于整个方法优于强参照。
- 相对G-U50、RawPost-U50和S，F1_U校正区间均跨零。没有建立精确身份增量，也没有建立相对强post的新增收益；不能把跨零称为等效。
- C实践代价门通过：总体−0.4828pp，四部署均未超过2pp损害；**它是实践筛查，不是主终点成功，也不是统计非劣效证明**。

建议将本轮作为当前角色非对称主候选的完整结项：保留P-small和本轮局部对照证据，不因剩余预算充足而默认继续细搜比例。

## 2. 从原停止到最终完成

| 阶段 | 事实 | 是否已有完整H评价 |
| --- | --- | --- |
| 原RA1 run-01 | VLESS/f0/G0 RawPre-U100在2000次后原梯度未达门 | 否 |
| NR1固定先导 | 42例通过；原困难点扩大预算后2974次合格 | 否 |
| Full NR1 | Trojan/f1/G0 RawPre-U50在4000次后仍未达原门 | 否 |
| NR2固定先导 | 52例通过，4例1024＋1收尾；前缀和重复通过 | 否 |
| Full NR2（本报告） | 1296新拟合通过，全部2340端点及预测封存、评分和复核完成 | **是** |

旧两次科学停止、先导记录及工程登记停止均保留。不能给未完成的NR1拼出F1，再宣称NR2提高了其业务成绩；NR2主要改变的是数值求解，科学问题并未改换。

## 3. 数据、样本单位与业务标签

沿用当前Extend相关的四TCP部署固定分析队列：SS、VLESS、Trojan、VMess。原始扩展目录覆盖六种代理不等于本轮用了六种；AnyTLS/Hy2没有进入本RA1矩阵。本报告不重新推定它们未纳入的原因。

- 六业务、每业务5个内容，共30个全局内容。
- 每内容×每部署4次重复：30×4×4=**480次不同访问**。
- 五折内容留出，每折训练24内容、留出6内容；同内容的重复、两侧和内部flow随父访问整体组织。
- 五折×四目标部署×三个C/U遮蔽组=**60个外层角色**。
- 每角色三源训练288次访问＋目标C的64次访问=352次真实训练访问；H为24次。
- 实际目标U的32次训练访问两侧数值不开放；H-pre禁止。

**分类对象是访问**。不是一条flow一个标签，也不是把一个PCAP的子流随机拆成独立样本。本轮输入是既有96维访问汇聚直方图；角色、内容ID及标签用于组织和评分，不作为数值分类输入。没有新增IP、端口或SNI等强指示信息。

| 类别ID | 业务标签（domain × activity） |
| --- | --- |
'''
    report+='\n'.join(f'| {i} | {BUS[i]} / `{LABELS[i]}` |' for i in range(6))
    report+=r'''

遮蔽：G0的U为GitHub仓库/YouTube搜索；G1为Bing搜索/Wikipedia文章；G2为MDN文档/YouTube播放。其他四类为C。

每政策输出1440个角色化访问预测（480访问×三个遮蔽）；其中U恰好480行、C为960行。39政策共56160逻辑预测，**不是56160个独立采集样本**。H上的480访问仍只有30个内容簇。

本次从合同范围元数据和已有评分产物独立核对了60个角色的训练/测试内容集合，交集均为0。这核对内容级隔离，不是重新扫描PCAP获得的新physical-flow审计；沿用原父访问/连接归属台账，不以“内容不相交”声称消除了历史回顾性选择影响。

## 4. 模型、视图和权重

模型是固定96维输入的六分类线性softmax：`logits = W x + b`，W为6×96，bias为6，共582名义参数。不是MLP、GAN或新增序列编码器。

原目标：

\[
J=\sum_i w_i\,CE(Wx_i+b,y_i)+0.0005(1+t)\|W\|_F^2.
\]

bias不惩罚。逐角色t及映射来源eta冻结；mu/scale、P/G前向全仿射漂移映射及CORAL均不重拟合。推理只用实际post的96维、原训练尺度和W/b；无测试pre、测试侧重新标准化、温度拟合或H后模型选择。

训练质量：源真实post主槽1/3、辅助槽1/3、目标C真实post槽1/3；辅助C/U各1/6。原设计使每类总CE质量1/6。损失已按mass求和，**不再除计算行数或类别数**。

本轮替换原辅助CORAL槽的一部分，而不是无上限添加样本：

| 分配 | rho_C | rho_U | 作用 |
| --- | ---: | ---: | --- |
| SYM | m | m | 两组同替换比例 |
| UPR | 0 | 2m | 仅替换U辅助材料，C保留原CORAL |
| CPR | 2m | 0 | 仅替换C辅助材料 |

m∈0.1/0.25/0.5；四来源P、G、RawPre、RawPost，各9政策；另有S、P-full、G-full，合计39。

主候选P-U50是m=.25、rho_C=0/rho_U=.5；同质量对照P-SYM25是rho_C=rho_U=.25；P-small为SYM10。前两者替换质量都是全训练CE的1/12（8.333%），P-small为1/30（3.333%）。计算行数可以不同，不代表mass不同。

U100仅表示U辅助CORAL槽完全替换，**不是删除所有U真实source-post监督**；源主槽、目标C真实post始终保留。P/G/RawPre使用相同允许的源pre及标签资源，RawPost用源post作为曝光控制；不从实际目标U取新数据。

## 5. NR2求解与完整执行验收

新拟合统一从零，最多1024次原Cholesky/LBFGS更新，原门未通过才进入最多32次Newton。二阶581坐标保留所有W，只冻结共同bias自由度；不是新增bias正则或把W-L2换成约简坐标惩罚。

原完整W/b梯度≤1e-5、目标/梯度重放<1e-10、目标不增、总更新严格<4000、20000优化评价政策及数值安全规则保持。所有拟合和模型前向CUDA float64，无AMP/TF32/CPU数值回退；评分/重采样和元数据可在CPU执行。

新拟合1296例全部通过；只有6例触发Newton，均为RawPre、且每例1次无阻尼更新。最大总更新1025。不存在新的数值失败或扩大上限。详细统计：

'''+table(newstats)+f'''

新端点最大原梯度{metadata['new_max_gradient']:.10g}，最大优化评价{metadata['new_max_optimization_evaluations']}。源模型优先级：NR2先导52优先，其余旧992，复用1044（624科学＋420参照）；补1296后得2340逻辑端点。旧32个被覆盖键仍保留，不把旧后端模型声称为已跑NR2。

封存顺序与60角色内容范围本次再次核对；原verification还重放2340个模型前向，概率/logprob最大误差均0、混淆指标误差0、bootstrap精确重放；420历史逻辑参照与历史概率最大误差0。H-pre和实际目标U训练读取均为0。这里是应用已记录读通路及绑定产物的核查，不冒充操作系统级全文件取证。

## 6. 统计口径

每政策在每部署×遮蔽内合并五折120行，计算完整6×6矩阵，再取U两类和C四类F1；最后对四部署×三遮蔽等权平均。**F1_U不是只留真实U行的二分类**，因为来自真实C的误预测也贡献U类FP。

10000次共享内容簇bootstrap，seed=20261017；六类分别抽5个内容，各政策/部署/遮蔽同步复用权重。六项预定比较用Bonferroni：每项99.1667%边际区间，对应名义95%家族控制；普通95%同时保存。它们条件于既有模型/当前30内容，不包括重训练不确定性，也不为历次研究的回顾性选择统一校正。

本报告重新从已封存导出重算全部468个政策×部署×遮蔽混淆指标，最大误差0；从已保存bootstrap样本重算六主区间，误差<1e-12。没有另建有利检验家族。

## 7. 主要方法成绩

'''+table(mainrows)+f'''

F1列为百分比；CE/Brier为原尺度，越低越好。F1_all也是各场景完整六类宏F1等权，不是把全部角色行混成单个新模型的分数。

## 8. 六项主比较与正式裁决

差均为P-U50减参照；F1正值有利，CE/Brier负值有利。

'''+table(comparisons)+f'''

![六项主比较区间]({(fig/'primary-comparisons.png').as_posix()})

**相对P-small和P-SYM25是负向证据，不只是“没有显著提高”。** 相对G的区间允许两方向差异，不能用点估计接近宣布精确配对与组级等效。相对RawPre的正结果应保留，但不能代替相对强基线的升级判断。

## 9. 部署差异与C实践成本

以下均为描述性分层，不另宣称各部署显著性。

'''+table(deployment)+f'''

![部署分项]({(fig/'deployment-breakdown.png').as_posix()})

P-U50相对P-small四部署U侧F1均下降，SS为{delta_ss:+.4f}pp、降幅最大；该最差部署没有被统一模型平均分掩盖。C侧总体差{100*ccost['delta_F1_C']:+.4f}pp，实践1pp门通过；各部署2pp门也通过。Trojan/VMess的C差分别约−1.4061/−1.4390pp，SS/VLESS为正。

C门仅用于完整结果的实践筛查，未用于H后回退或重新拟合。它不保证总体有效、不证明统计非劣效，也不补救U主终点的负向证据。

## 10. 业务类别与内容差异

U侧每业务有80次真实访问，表中F1/precision/recall先在正确的部署×遮蔽完整矩阵上计算再平均；TP/FP/FN为相应四部署的计数和，不能拿计数重算值替换宏平均。

'''+table(business)+'''

六业务的U-F1点估计相对P-small全部下降；Wikipedia文章降幅最大。各业务的“对总体Δ贡献”只是宏平均的代数分解，不是因果归因，不能和部署分解简单相加。

下表按已有配对预测翻转列出净新增错误最多的8个内容，每内容16次U访问；这不是事后删除困难内容或重新检验。

'''+table(contentrows)+'''

## 11. 错误修复、剩余错误与概率代价

U行对应480次不同访问；C行960为角色化预测，每个真实访问在两个C遮蔽下出现。不能把C逻辑行当独立新访问。

'''+table(fliprows)+'''

对P-small：U修复7、新增错误15，净少正确8次；C修复7、新增错误11，净少正确4个角色行。对同质量SYM25：U修复5、新增16，净少正确11次。对G-U50，U和C的修复/新增数分别相等，但F1仍不同，因为类别与FP流向不同。不能只看正确总数推断宏F1。

对RawPre-U50：U修复39、新增7，是真实可见的局部任务收益；同时有C错误交换，仍需结合完整六类矩阵理解。对S：U有净11次修复，但主F1区间仍跨零，不把少量净修复写成确认性增益。

P-U50相对P-small的U侧概率损害分解：每行贡献为该组所有delta之和除480，可加和重放总体CE/Brier差。

'''+table(probrows)+'''

这不是只有“置信度更大、F1不变”的现象：本轮F1、CE和Brier相对P-small均恶化。概率贡献只描述哪些预测状态承担损害，不证明某一特征、某段协议开销或某个恢复残差是原因。

## 12. 剂量／分配规律：完整披露，不能据此换主方法

'''+table(allocation)+f'''

![全部固定剂量与分配]({(fig/'dose-allocation.png').as_posix()})

上述95%区间是预登记的描述性对照，不混入六项确认性家族。P/G在最高UPR剂量下U-F1分别约66.52%/67.64%，RawPre/RawPost约53.87%/57.04%；“把U辅助槽完全替换”在四来源都出现明显点估计退化。中等剂量UPR也未优于对应SYM。

这些支持当前替换策略存在剂量和角色分配敏感性，不证明确定的协议/业务因果机制。不将G-SYM25或其他事后最高点自动升级为新主候选，不继续在同一H上细搜比例。

## 13. 混淆矩阵：如何读与样本单位

类别0—5依次为Bing、MDN、GitHub、Wikipedia、YouTube搜索、YouTube播放。行真实、列预测。

以下合并三遮蔽的矩阵是**诊断汇总**：全体1440行、每类240行，重复的是同访问在不同训练角色下的预测；不是一个单模型的1440个独立测试样本。主指标仍按第6节的场景宏平均计算。

### 13.1 主候选合并矩阵

'''
    cm_primary=sum(cm for (pid,p,g),cm in cm_by.items() if pid==PRIMARY)
    cm_small=sum(cm for (pid,p,g),cm in cm_by.items() if pid==REFS[0])
    report+=matrix_table(cm_primary)+'\n\n### 13.2 P-small合并矩阵\n\n'+matrix_table(cm_small)
    for p in PROTOCOLS:
        cm=sum(cm_by[(PRIMARY,p,g)] for g in MASKS)
        report+=f'\n\n### 13.{3+PROTOCOLS.index(p)} {PN[p]}主候选矩阵\n\n每部署360个角色化行、每类60行（实际120次访问，每类20次）。\n\n'+matrix_table(cm)
    report+='''

完整468个政策×部署×遮蔽矩阵保存在原`scores/confusion-matrices.json`，逐类precision/recall/F1及支持数保存在`classes.parquet`；不在这里省略原六类的假阳性流向来提高F1_U。

## 14. 实际成本与预算

'''+table(stageframe)+f'''

本次完整恢复活动{cost['new_active_seconds']:.3f}秒，约{cost['new_active_seconds']/60:.2f}分钟；继承此前计费基数{cost['prior_components']['total_prior_charged_seconds']:.3f}秒后，累计{cost['cumulative_active_seconds']:.3f}秒，约{cost['cumulative_active_seconds']/3600:.4f}小时，低于8小时。未用余额不构成继续扩充实验的授权。

1296新拟合solver-seconds合计{new.seconds.sum():.3f}秒，中位{new.seconds.median():.3f}秒、最大{new.seconds.max():.3f}秒；RawPre占主要求解成本。R0/R1、完整模型复核、导出、bootstrap、独立重放等有额外开销，不能把整轮称为“1296个小LR几秒钟”。

此前697加1296=1993是保守优化尝试谱系，包含旧失败、诊断和重复，不是1993个新样本或独立科学假设。8小时从未重置；NR2先导30分钟上限与本轮完整实验8小时是不同执行范围，不将40余分钟完整恢复误认为先导超时。

## 15. 当前可以和不可以写成的结论

**可以写：**

1. 已冻结NR2二阶数值政策在本轮实际完整矩阵中完成了1296个缺失端点，原科学目标和精度门保持，整体实现及权限/统计审计完成。
2. 当前P-U50相对直接补充RawPre-U50具有局部正向业务证据。
3. 当前P-U50显著弱于P-small和同质量P-SYM25；角色非对称分配没有成为已有P-small的升级方案。
4. 当前精确管线相对G-U50的新增作用未建立；这和两者等效、真实关联没有价值不是同一命题。

**不可以写：**

- 修复数值后F1自然提高；旧未完成NR1没有可比较的完整业务结果。
- 配对或漂移对所有任务无用；本轮只是既定96维、四部署、有限内容和固定权重政策的检验。
- C代价通过所以主方法成功；或胜RawPre就证明胜强post。
- 当前置信区间是跨日期/新节点外部验证；历史H已多次研究，当前家族校正不覆盖所有历次方案选择。
- 已解决单flow识别、完整physical连接重建、无索引在线访问分段或外部DIRECT→代理迁移。
- 所有模型都运行了NR2：历史参照及旧兼容模型保留旧求解来源，统一NR2政策仅适用于本次新拟合及被采纳的NR2先导模型。

## 16. 结项建议

接受完整实验完成，并关闭“P-U50角色非对称分配必然升级P-small”的当前候选。保留P-small与同剂量RawPre比较等正负证据。若之后继续，应提出区别于本次细调比例的新问题并重新登记；本轮不自动重启、调阈值、删控制或按现有H选新赢家。

当前结论是**数值实现完成，但主要升级假设不获支持且相对两个强参照存在负向证据**，不是“又一次求解没做完”。

## 附录A：全部39政策的点估计

按固定设计顺序列出，非按分数排序选赢家。

'''+table(allpol)+f'''

## 附录B：证据与可复现分析

- 原恢复合同：`plan/RA1-NR2-full-resume-contract-20261018.md`
- 完整运行：`outputs/role-asymmetric-transfer-v1-20261017/full-nr2-01/`
- 原封存主报告：[complete-report.md]({(DOC/'complete-report.md').as_posix()})
- 终态：completion、verification、cost-final及全部stages均完整；failure和run.lock不存在。
- 全部原评分、错误翻转、概率贡献、混淆矩阵、共享bootstrap样本均保留。
- 本报告程序：`eval/role_asymmetric_transfer_v1_analysis/full_nr2_results.py`
- 本次额外核对及来源指纹：`result-analysis-20261018/analysis.json`及`content-scope-audit.parquet`

本次只读分析不改写原合同、原报告、completion或任何模型，也不重新拟合/校准。分析新增活动和原账分开记入本次analysis.json，后续若另有授权应继承原账再加本次已记录分析，不重置预算。
'''
    (DOC/'results-analysis-20261018.md').write_text(report,encoding='utf-8')
    pd.DataFrame(scope_audits).to_parquet(OUT/'content-scope-audit.parquet',index=False)
    pd.DataFrame(business).to_parquet(OUT/'business-summary.parquet',index=False)
    pd.DataFrame(comparisons).to_parquet(OUT/'primary-summary.parquet',index=False)
    require(all(sha(ROOT/p)==h for p,h in bound.items()),'Source output modified during read-only analysis')
    metadata['readonly_analysis_activity_seconds']=time.perf_counter()-LOAD_START
    metadata['parent_cumulative_plus_analysis_seconds']=cost['cumulative_active_seconds']+metadata['readonly_analysis_activity_seconds']
    metadata['report_path']=rel(DOC/'results-analysis-20261018.md');metadata['report_sha256']=sha(DOC/'results-analysis-20261018.md')
    (OUT/'analysis.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in metadata.items() if k!='source_hashes'},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
