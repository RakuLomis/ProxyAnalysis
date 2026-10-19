"""Complete AD1 evidence report; no winner search or retrospective reclassification."""
from common import *
from weight_schedule import registry,A,B,C_NEW,D_NEW,BASELINE,EFFECTS,NAMES
BUS=['Bing搜索','MDN文档','GitHub仓库','Wikipedia文章','YouTube搜索','YouTube播放']
PN={'shadowsocks':'SS','vless':'VLESS','trojan':'Trojan','vmess':'VMess'}

def table(d):
    if not isinstance(d,pd.DataFrame):d=pd.DataFrame(d)
    def cell(x):
        if isinstance(x,(float,np.floating)):return f'{x:.6f}'
        return str(x).replace('|','\\|').replace('\n',' ')
    lines=['| '+' | '.join(map(str,d.columns))+' |','| '+' | '.join(['---']*len(d.columns))+' |']
    lines+=['| '+' | '.join(cell(x) for x in r)+' |' for r in d.itertuples(index=False,name=None)]
    return '\n'.join(lines)

def run():
    with stage('report'):
        p=pd.read_parquet(OUT/'scores/pooled.parquet').set_index('policy_id');t=pd.read_parquet(OUT/'scores/targets.parquet')
        cl=pd.read_parquet(OUT/'scores/classes.parquet');fl=pd.read_parquet(OUT/'scores/error-transitions.parquet')
        prim=read(OUT/'comparisons/primary.json');interaction=read(OUT/'comparisons/interaction.json');cost=read(OUT/'scores/C-practical-cost.json')
        new=pd.read_parquet(OUT/'manifests/new-endpoints.parquet');risk=pd.read_parquet(OUT/'audits/training-view-risks.parquet')
        pooled=[dict(方法=NAMES[pid],F1_U百分比=100*p.loc[pid,'F1_U'],F1_C百分比=100*p.loc[pid,'F1_C'],
            F1_all百分比=100*p.loc[pid,'F1_all'],CE_U=p.loc[pid,'CE_U'],Brier_U=p.loc[pid,'Brier_U'],
            最差部署F1_U百分比=100*p.loc[pid,'worst_target_F1_U']) for pid in [A,B,C_NEW,D_NEW,BASELINE]]
        effects=[]
        for x in prim['comparisons']:
            effects.append(dict(对比=NAMES[x['candidate']]+' − '+NAMES[x['reference']],ΔF1_U_pp=100*x['delta_F1_U'],
                校正区间pp=f"[{100*x['CI_family'][0]:+.4f}, {100*x['CI_family'][1]:+.4f}]",
                ΔCE_U=x['delta_CE_U'],ΔBrier_U=x['delta_Brier_U'],
                证据='正向' if x['positive'] else '负向' if x['negative'] else '区间跨零，未定'))
        dep=[]
        for proto in PROTOCOLS:
            z=t[t.target.eq(proto)].set_index('policy_id')
            dep.append(dict(部署=PN[proto],A_U50=100*z.loc[A,'F1_U'],B_SYM25=100*z.loc[B,'F1_U'],
                C_C0U25=100*z.loc[C_NEW,'F1_U'],D_C25U50=100*z.loc[D_NEW,'F1_U'],Psmall=100*z.loc[BASELINE,'F1_U'],
                D减A_pp=100*(z.loc[D_NEW,'F1_U']-z.loc[A,'F1_U']),C减A_pp=100*(z.loc[C_NEW,'F1_U']-z.loc[A,'F1_U'])))
        business=[];counts=[];bb=cl[cl.scope.eq('U')].groupby(['policy_id','label_index']).F1.mean()
        for k in range(6):
            row=dict(业务=BUS[k]);row.update({NAMES[pid]:100*bb.loc[(pid,k)] for pid in [A,B,C_NEW,D_NEW,BASELINE]});business.append(row)
            for pid in [A,B,C_NEW,D_NEW,BASELINE]:
                z=cl[cl.scope.eq('U')&cl.policy_id.eq(pid)&cl.label_index.eq(k)]
                counts.append(dict(业务=BUS[k],方法=NAMES[pid],TP=int(z.TP.sum()),FP=int(z.FP.sum()),FN=int(z.FN.sum())))
        ff=[]
        for a,b,name in EFFECTS+[(a,BASELINE,'descriptive_vs_Psmall') for a in [A,B,C_NEW,D_NEW]]:
            for scope in ['U','C']:
                x=fl[fl.candidate.eq(a)&fl.reference.eq(b)&fl.scope.eq(scope)];ct=x.state.value_counts()
                ff.append(dict(对比=NAMES[a]+' − '+NAMES[b],范围=scope,行数=len(x),修复=int(ct.get('repaired',0)),
                    新增错误=int(ct.get('new_error',0)),共同正确=int(ct.get('both_correct',0)),共同错误=int(ct.get('both_wrong',0)),
                    正确净变化=int(ct.get('repaired',0)-ct.get('new_error',0))))
        cc=[]
        for x in cost:
            row=dict(方法=NAMES[x['policy_id']],总体C变化pp=100*x['delta_F1_C'],总体门=x['overall_pass'],各部署门=x['each_deployment_pass'])
            row.update({PN[k]+'变化pp':100*v for k,v in x['per_deployment'].items()});cc.append(row)
        rv=risk.groupby(['view','scope','policy_id']).conditional_CE.mean().unstack().reset_index()
        rv=rv.rename(columns={k:NAMES[k] for k in NAMES})
        bypid=new.groupby('policy_id').agg(拟合数=('policy_id','size'),求解秒=('seconds','sum'),
            最大梯度=('gradient_inf','max'),最大更新=('iterations','max'),Newton触发=('newton_updates',lambda x:int((x>0).sum()))).reset_index()
        bypid['policy_id']=bypid.policy_id.map(NAMES)
        e={x['name']:x for x in prim['comparisons']}
        claims=[]
        for key,title in [('restore_C_at_U50','U50下恢复C25'),('reduce_U_at_C0','C0下降低U50到U25'),
                          ('restore_C_at_U25','U25下加入C25'),('increase_U_at_C25','C25下增加U25到U50')]:
            x=e[key];status='正向区间支持' if x['positive'] else '负向区间支持' if x['negative'] else '区间跨零，未获定向支持'
            claims.append(f"- {title}：ΔF1_U={100*x['delta_F1_U']:+.4f}pp，{status}。")
        report=f'''# RA1-AD1最小2×2完整实验报告

日期：2026-10-18。全部60角色、120新拟合和180精确复用完成，模型与预测均先封存后评分。本报告生成后的独立验收见`verification.json`与`completion.json`；只有两者通过才称程序完成。

## 1. 执行摘要

本轮只补齐两个分配点，不训练新映射、不改正则、不换模型、不扩大比例网格。它回答的是P-U50退化中的两个因素，**不是一次新方法择优搜索**。

{table(pooled)}

{chr(10).join(claims)}

交互`(D−A)−(B−C)`点估计为{100*interaction['delta_F1_U']:+.4f}pp，探索性95%区间[{100*interaction['CI95'][0]:+.4f}, {100*interaction['CI95'][1]:+.4f}]pp。F1的非线性也可产生此交互，不能直接解释为协议因果机制或网络协同。

不从C/D中事后挑选新主候选。相对P-small的结果只作冻结参照下的描述；如果一个点优于P-U50但仍不超过P-small，属于退化定位进展，不是有效基线升级。

## 2. 四单元与实际质量

| 单元 | ρ_C | ρ_U | P-C质量 | P-U质量 | CORAL-C质量 | CORAL-U质量 | 正质量计算行 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A，旧P-U50 | 0 | 0.50 | 0 | 1/12 | 1/6 | 1/12 | 736 |
| B，旧P-SYM25 | 0.25 | 0.25 | 1/24 | 1/24 | 1/8 | 1/8 | 928 |
| C，新C0-U25 | 0 | 0.25 | 0 | 1/24 | 1/6 | 1/8 | 736 |
| D，新C25-U50 | 0.25 | 0.50 | 1/24 | 1/12 | 1/8 | 1/12 | 928 |

各单元都保留source-post质量1/3、真实目标C-post质量1/3、辅助槽质量1/3。每类总质量1/6；U总质量1/3，不因ρ_U增加而增加标签总权重。增加P必然减少同角色CORAL，所称剂量效应是视图混合替换效应。

A/B同映射总质量1/12；单因素比较改变某个ρ时，映射总质量本来会变化。不能将四单元都叫同总质量。

## 3. 数据、模型与训练权限

- SS/VLESS/Trojan/VMess四部署，30全局内容、六业务、每内容四次重复，合计480次不同访问。
- 五折按全局内容留出，所有部署、重复、两侧及内部flow随父内容划分。每角色训练24内容、H六内容，无内容交集。
- 60角色=五折×四目标部署×三个遮蔽；每角色三源288访问、真实目标C64访问，共352次真实训练访问。实际目标U32访问的两侧都禁用。
- 每角色冻结原96维mu/scale、t/η、P映射、CORAL视图。源pre独立排序，按自身标签拆质量，不按源post行号配对。
- 分类器为六类线性softmax，96×6权重＋六bias；CE是样本质量和，L2=`0.0005*(1+t)||W||²`，bias不罚。
- CUDA float64、原Cholesky LBFGS1024＋最多Newton32，原梯度≤1e−5、原重放1e−10门及4000/20000预算政策不变。
- post-only推理只读取96维H-post；不输入pre、IP/端口/SNI/配置路径或协议身份。角色部署只组织训练和分项报告。

## 4. 四项固定比较与统计

{table(effects)}

10000次共享内容簇bootstrap，种子20261017，六类各五内容分层抽样；四比较家族各98.75%区间，另存95%。先合并五折完整六类混淆矩阵，再计算U/C类F1，最后部署与遮蔽等权。不删除真实C行，不将U任务改为二分类。

区间条件于保存模型，未计入训练重拟合或历史反复分析的选择影响。这批H此前已被研究，不是外部盲测。跨零不是等效，角色、重复和五折也不是新增独立内容。

## 5. 部署分项

{table(dep)}

## 6. 业务分项

以下是每业务作为U时四部署F1平均；每个业务有80条U访问预测。所有业务完整列出，不删除SS或困难内容。

{table(business)}

计数来自完整六类矩阵；下表计数先求和，但主F1仍为部署等权平均，不能用总计数重算值替换原F1口径。

{table(counts)}

## 7. 训练视图取舍

以下是合法训练来源上每视图条件CE，再对60角色平均。质量为0的视图仅作离线诊断，并非该模型训练损失。

{table(rv)}

该表可判断降低U替换是否减少对映射U的追逐、恢复C材料是否改变C区域风险；但训练CE不是实际目标U表现，也不证明映射某项误差必然造成H错误。

## 8. 错误修复、新增与概率质量

{table(ff)}

每政策7200/5=1440条逻辑预测，U480、C960。真实不同访问480、内容30；C在不同遮蔽中重复，不能把960视为独立访问。新两政策预测2880条，不是2880个新样本。

逐内容/业务/部署结果在`scores/contents.parquet`、`classes.parquet`；逐访问错误翻转在`error-transitions.parquet`，概率分组贡献在`probability-contributions.parquet`。不只报告修复，也完整保留新增和共同错误。

## 9. C实践代价

相对P-small总体最多1pp、各部署最多2pp损害的原实践筛查：

{table(cc)}

此表不是统计非劣效检验，不用于在看过H后回退或选择政策。CE/Brier即使与F1方向不同，也全部保留，不要求所有指标同赢才承认单项证据。

## 10. 工程、求解与复用

{table(bypid)}

固定8工程案例属于120新拟合，不另训练；四部署全部包括，先只检查工程与预算，不读H或按F1选择。120个新端点均零起点、同一数值政策，复用180个旧端点没有重拟合。

工程预算记录：`audits/pilot-budget.json`；逐行权重：`audits/weight-ledger.parquet`；所有端点原坐标验收：`audits/all-endpoint-original-coordinate.parquet`。工程失败、数值失败或完整性冲突会停止，不放宽门、不自动重启。

实际新求解合计{new.seconds.sum():.3f}秒，最大单拟合{new.seconds.max():.3f}秒。完整活动和保守前置计费见`cost-final.json`，不是将整个实验成本仅称作120个小LR。

## 11. 封存与结论边界

顺序为：全部模型完成并封存→全部H-post预测→预测封存→H标签评分→报告→独立重放验收。旧A/B/P-small的4320条预测需重放原封存结果；原Full NR2报告、停止记录、模型和原六比较不变。

本轮机制对照完成即结项，不继续比例搜索。C/D即使有正向点估计，也不能直接升级为新方法。它不检验新协议、新配置、异批次、真实DIRECT、无索引在线切分、合法PCAP生成或精确身份的独立增益。

## 12. 复现与产物

命令：`D:/Tools/Anaconda/envs/Pytorch312/python.exe eval/role_asymmetric_transfer_ad1/run.py`。该运行目录终态后禁止原命令自动重启。

运行目录：`outputs/role-asymmetric-transfer-v1-20261017/ad1-2x2-01`。

- `manifests/contract.json`、`seal.json`、`endpoints.parquet`、`endpoint-seal.json`。
- `audits/engineering.json`、`pilot-budget.json`、质量与原坐标验收表。
- `predictions/visits.parquet`和`complete.json`，以及全部逐类/逐内容/部署/混淆矩阵评分。
- `comparisons/primary.json`、`interaction.json`、`bootstrap.npz`与P-small描述对照。
- `verification.json`、`completion.json`、`cost-final.json`。

详细逐角色t/η、尺度、映射来源和模型hash保存在合同及端点清单；访问和路径键不进入数值分类器。
'''
        textfile(DOC/'complete-report.md',report)
        textfile(DOC/'execution-contract.md',PLAN.read_text(encoding='utf-8'))
        progress('AD1_report_written')
