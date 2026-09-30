"""B10: fixed OOF contrasts, content bootstrap and machine-generated report."""
from pathlib import Path
import numpy as np
import pandas as pd
from .data import OUT,DOC,cfg,load,read,digest
from .formal import FORMAL,job_name,write_json

ARMS=['S0','S1','S2','S3','S4','L1','L2','L3','L4']
CONTRASTS=[('S2','S1'),('S2','S3'),('S2','S0'),('S2','S4'),('L3','S2'),('L3','L1'),('L3','L2'),('L3','L4')]

def scores(target,prob,weights=None):
    target=np.asarray(target,dtype=int);prob=np.asarray(prob,dtype=float)
    w=np.ones(len(target)) if weights is None else np.asarray(weights,dtype=float)
    pred=prob.argmax(1);cm=np.bincount(6*target+pred,weights=w,minlength=36).reshape(6,6)
    tp=cm.diagonal();denom=cm.sum(0)+cm.sum(1)
    f1=np.divide(2*tp,denom,out=np.zeros(6),where=denom>0).mean()
    ba=np.divide(tp,cm.sum(1),out=np.zeros(6),where=cm.sum(1)>0).mean()
    ce=np.average(-np.log2(np.maximum(prob[np.arange(len(target)),target],1e-15)),weights=w)
    brier=np.average(((prob-np.eye(6)[target])**2).sum(1),weights=w)
    return np.array([f1,ba,ce,brier])

def report():
    contract=read(FORMAL/'contract.json');frames=[];stages=[]
    for job in contract['jobs']:
        folder=FORMAL/job_name(job);done=read(folder/'done.json');assert done['steps']==1000
        assert digest(folder/'final.pt')==done['checkpoint_sha256']
        stages.append({**job,'training_seconds':done['training_seconds'],'peak_allocated_bytes':done['cuda_peak_allocated_bytes']})
        log=pd.read_parquet(folder/'training-log.parquet');assert log.step.tolist()==list(range(1,1001)) and np.isfinite(log.loss).all()
        if job['phase']!='ssl':
            assert digest(folder/'predictions.parquet')==done['predictions_sha256']
            frames.append(pd.read_parquet(folder/'predictions.parquet'))
    p=pd.concat(frames,ignore_index=True)
    assert len(p)==3240 and not p[['arm','seed','session_id']].duplicated().any()
    assert set(p.inference_device)=={'cuda'} and read(FORMAL/'replay-audit.json')['all_passed']
    probs=[f'p{i}' for i in range(6)];assert np.isfinite(p[probs]).all().all()
    assert (p[probs].to_numpy()>=0).all();np.testing.assert_allclose(p[probs].sum(1),1,atol=2e-6)
    p.to_parquet(FORMAL/'oof-predictions.parquet',index=False)
    pd.DataFrame(stages).to_parquet(FORMAL/'stage-timings.parquet',index=False)
    names=['macro_f1','balanced_accuracy','ce_bits','brier'];metrics=[];recalls=[];confusions=[]
    cohort=load('cohort').sort_values('session_id');ids=cohort.session_id.tolist();seeds=cfg()['seeds'];labels=contract['labels']
    target=np.array([labels.index(x) for x in cohort.label_id]);arrays={}
    for arm in ARMS:
        for seed in seeds:
            g=p[(p.arm==arm)&(p.seed==seed)].set_index('session_id').loc[ids]
            assert len(g)==120 and np.array_equal(g.target,target)
            values=g[probs].to_numpy();arrays[arm,seed]=values
            metrics.append({'arm':arm,'seed':seed,**dict(zip(names,scores(target,values)))})
            pred=values.argmax(1);cm=np.bincount(6*target+pred,minlength=36).reshape(6,6)
            for c,label in enumerate(labels):
                recalls.append({'arm':arm,'seed':seed,'label_id':label,'recall':cm[c,c]/cm[c].sum(),'visits':int(cm[c].sum())})
                for d,other in enumerate(labels):confusions.append({'arm':arm,'seed':seed,'true_label':label,'predicted_label':other,'count':int(cm[c,d])})
    m=pd.DataFrame(metrics);m.to_parquet(FORMAL/'metrics-by-seed.parquet',index=False)
    summary=m.groupby('arm')[names].agg(['mean','min','max']).reindex(ARMS);summary.columns=['_'.join(v) for v in summary.columns]
    summary=summary.reset_index();summary.to_parquet(FORMAL/'metrics-summary.parquet',index=False)
    pd.DataFrame(recalls).to_parquet(FORMAL/'class-recall.parquet',index=False);pd.DataFrame(confusions).to_parquet(FORMAL/'confusion-matrices.parquet',index=False)
    groups=[cohort[cohort.label_id==label].content_id.unique().tolist() for label in labels]
    assert all(len(g)==5 for g in groups)
    rng=np.random.default_rng(20260926);bootstrap=[]
    for repeat in range(cfg()['bootstrap_repetitions']):
        selected=[c for group in groups for c in rng.choice(group,len(group),replace=True)]
        counts={c:selected.count(c) for c in set(selected)};weights=np.array([counts.get(c,0) for c in cohort.content_id])
        assert weights.sum()==120
        result={arm:np.mean([scores(target,arrays[arm,seed],weights) for seed in seeds],axis=0) for arm in ARMS}
        for arm,ref in CONTRASTS:
            delta=(result[arm]-result[ref])*np.array([1,1,-1,-1])
            bootstrap.append({'draw':repeat,'arm':arm,'reference':ref,**dict(zip(names,delta))})
    draws=pd.DataFrame(bootstrap);draws.to_parquet(FORMAL/'content-bootstrap-draws.parquet',index=False)
    gains=[];changes=[];avg=m.groupby('arm')[names].mean()
    for arm,ref in CONTRASTS:
        d=draws[(draws.arm==arm)&(draws.reference==ref)];row={'arm':arm,'reference':ref}
        for metric,sign in zip(names,[1,1,-1,-1]):
            row[metric+'_gain']=float(sign*(avg.loc[arm,metric]-avg.loc[ref,metric]))
            row[metric+'_ci_low']=float(d[metric].quantile(.025));row[metric+'_ci_high']=float(d[metric].quantile(.975))
        gains.append(row)
        for seed in seeds:
            a=arrays[arm,seed].argmax(1);b=arrays[ref,seed].argmax(1)
            changes.append({'arm':arm,'reference':ref,'seed':seed,'changed_predictions':int((a!=b).sum()),
                'corrected':int(((b!=target)&(a==target)).sum()),'new_errors':int(((b==target)&(a!=target)).sum())})
    gains=pd.DataFrame(gains);gains.to_parquet(FORMAL/'paired-gains.parquet',index=False)
    pd.DataFrame(changes).to_parquet(FORMAL/'decision-changes.parquet',index=False)
    write_json(FORMAL/'paired-gains.json',gains.to_dict('records'))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    figdir=DOC/'figures';figdir.mkdir(exist_ok=True,parents=True)
    fig,axes=plt.subplots(1,2,figsize=(11,4),layout='constrained')
    for ax,metric,title in zip(axes,['macro_f1','ce_bits'],['OOF macro-F1','OOF cross-entropy (bits)']):
        vals=summary[metric+'_mean'].to_numpy();low=summary[metric+'_min'].to_numpy();high=summary[metric+'_max'].to_numpy()
        ax.bar(ARMS,vals,color=['#507ba3']*5+['#c18445']*4)
        ax.errorbar(np.arange(9),vals,yerr=[vals-low,high-vals],fmt='none',color='black',capsize=3)
        ax.set_title(title+'; seed mean/range');ax.grid(axis='y',alpha=.2)
    fig.savefig(figdir/'formal-metrics.png',dpi=160);plt.close(fig)
    fig,ax=plt.subplots(figsize=(9,5),layout='constrained')
    y=np.arange(len(gains));v=gains.macro_f1_gain.to_numpy();lo=gains.macro_f1_ci_low.to_numpy();hi=gains.macro_f1_ci_high.to_numpy()
    ax.hlines(y,lo,hi,color='#507ba3');ax.scatter(v,y,color='#507ba3');ax.axvline(0,color='black',lw=1)
    ax.set_yticks(y,[f'{a} - {b}' for a,b in CONTRASTS]);ax.set_xlabel('Macro-F1 gain; descriptive content-bootstrap interval')
    fig.savefig(figdir/'paired-gains.png',dpi=160);plt.close(fig)
    from ...protocol_normalization.record_representation.report import table
    slim=summary[['arm',*[n+'_mean' for n in names]]]
    gaincols=['arm','reference','macro_f1_gain','macro_f1_ci_low','macro_f1_ci_high','ce_bits_gain','ce_bits_ci_low','ce_bits_ci_high']
    class_table=pd.DataFrame(recalls).groupby(['arm','label_id']).recall.mean().unstack().reindex(ARMS).reset_index()
    seconds=sum(s['training_seconds'] for s in stages);replay=read(FORMAL/'replay-audit.json')
    report_text=f'''# 0916 VLESS：记录结构＋独立时间的正式业务实验

## 1. 执行状态与研究范围

195/195正式阶段完成，195,000次优化更新；75个直接监督、60个SSL、60个SSL后微调。135个业务分类器产生3240行OOF预测；这些行包含三个seed和九个臂，不是3240个独立访问。

队列仍为120访问、30独立内容、六个domain×activity业务，每内容四次重复。使用共同可解析的1179对排他TCP连接；6对候选连接未纳入任何表示臂。旧五折保持，每折训练96访问/24内容、测试24访问/6内容。研究范围是当前已见VLESS部署内的未见内容，不是未见协议、外部数据或无索引在线攻击。

## 2. 表示与模型

静态分支分别编码上下行：P_unique按首次贡献的新字节单位，R按严格记录语法，C按1024-byte方向分块。所有臂使用相同独立新字节时间线，不把记录压缩到first/all/prefix中的单一瞬时点。原FR未改名或替换；类型20/21/22/23仅为语法标签，不表示业务或Vision阶段。

静态和时间编码均为两层32-channel、kernel=3卷积及mean/max池化；flow表示32维；访问内flow mean/max加log1p(flow_count)，65→32→6分类头。业务标签仅监督父访问，没有为每条资源flow强加业务标签。IP/端口/SNI/URL和内容身份不作为模型数值输入。

S0=T-only，S1=P＋T，S2=R＋T，S3=C＋T，S4=R-no-type＋T。L1=post-only SSL，L2=双侧侧内SSL，L3=同次排他flow真配，L4=同内容跨重复flow错配；四个L臂固定R＋T并随后访问级微调。L2控制额外见过pre数据的作用。对齐的是flow表示，不是同序号记录。

所有SSL臂共用平衡flow子池。L4为无自配双射；相同内容四次访问按循环donor及同一选中flow rank组合。它不保证跨重复的同一资源连接语义，因此L3−L4不是纯访问噪声或信息量。监督阶段仍使用全部共同flow。

## 3. 固定训练与权限

每阶段1000步，Adam lr=0.001，batch=24。监督CE＋weight L2(1e−4/2)，bias不正则；SSL VICReg权重25/25/1、eps=1e−4、5%数值掩码。无早停、BN/dropout、阈值/权重搜索。seed=20260918/19/20。连续特征只使用训练post缩放；测试pre完全不在推理Store中。

CUDA-only float32，未启用AMP/TF32，确定性算法；模型训练、外层推理和检查点重放均在CUDA，CPU仅用于数据处理/统计。完整序列分块保留halo，GPU缓存与向量池化不改变网络或训练预算。训练时间合计{seconds/3600:.2f}小时（含各阶段保存间隔开销，不等于总wall-time）。

每100步保存模型、优化器和随机状态，支持相同冻结契约恢复。微调仅继承SSL编码器，使用与直接监督相同seed的新分类头。严格资格本身使用双侧离线证据，访问划分由内部索引辅助；保持offline_index_assisted_post边界。

## 4. 主要结果：三seed均值

{table(slim)}

逐seed值及min/max保存在metrics-by-seed/metrics-summary.parquet。CE为bits，Brier为六类平方误差之和。

![主要指标](figures/formal-metrics.png)

## 5. 预声明配对对照

F1/BA为新臂减参照；CE/Brier为参照减新臂，均正值表示改善。

{table(gains[gaincols])}

![配对区间](figures/paired-gains.png)

2000次按业务分层的内容bootstrap；同内容四次访问和全部臂/seed共同重采。每次重采重新计算每seed指标再取均值，不把访问F1平均，不先混合seed概率构造集成。区间是条件于既有模型的未校正描述区间；没有消除历史回顾性分析或多重比较，跨零不表示等效。每业务仅5内容，不能因flow多而夸大独立样本量。

## 6. 业务分项召回

{table(class_table)}

全部逐seed混淆矩阵与“修正错误/新增错误”计数分别保存在confusion-matrices.parquet和decision-changes.parquet；不只报告整体F1。

## 7. 如何解释这些对照

- S2−S1/S3回答记录描述相对于包级/固定分块的用途；S2−S0回答时间之外的结构增量；S2−S4回答语法类型通道的增量。不得将类型通道的可预测性直接解释为业务语义恢复。
- L3−S2混合预训练与对应机制变化；L3−L1还包含pre资源差异，必须联合L2/L4读。若L3仅胜过L1，不足以声称精确对应有独立收益。
- 即使R监督未胜过P/C，仍完整执行和报告SSL比较；没有按中间测试分数选择实验臂。
- 本轮不验证initial/relay、精确K、逐记录语义对应、SS/Hy2统一记录解析或未见部署泛化。

## 8. 再现与审计

135个检查点在CUDA独立重载，使用每批6访问（原预测24访问）重放；全部决策一致，最大概率误差{replay['max_probability_difference']:.8g}。这验证实现/存档一致性，不是新的独立泛化实验。

原120成员与内容折、捕获身份、全部张量、预处理和代码均保存SHA256。每折训练视图限定训练访问；测试视图只能读取post。训练输入不得接触测试内容，训练后的统计评分不能回流为模型选择。

复用入口：eval/record_time_business/run.py --stage formal。结果根目录：outputs/record-time-business-0916/run-01/formal。固定契约、195个子任务done/检查点/训练日志、OOF预测、bootstrap和重放审计均已保存。旧解析研究与旧240访问实验产物没有覆盖。
'''
    DOC.mkdir(exist_ok=True,parents=True);(DOC/'formal-results.md').write_text(report_text,encoding='utf-8')
    write_json(FORMAL/'completion.json',{'formal_stages':195,'optimization_updates':195000,'classifier_fits':135,'SSL_fits':60,
        'OOF_rows':3240,'independent_visits':120,'independent_contents':30,'all_replay_passed':True,
        'report':str(DOC/'formal-results.md'),'report_sha256':digest(DOC/'formal-results.md')})
