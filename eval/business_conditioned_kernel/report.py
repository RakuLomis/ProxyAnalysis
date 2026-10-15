"""Static scientific plots and local evidence report; never fit classifiers."""
import argparse
from common import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

NAMES={'shadowsocks':'SS','vless':'VLESS','trojan':'Trojan','vmess':'VMess'}
ARMS=['D0','DG','DB','D1-1','D2-1','D3-1']
def get(name): return pd.read_parquet(OUT/'scores'/name)
def table(df, digits=6):
    def fmt(x):
        if isinstance(x,(float,np.floating)): return f'{x:.{digits}f}'
        if isinstance(x,(bool,np.bool_)): return '是' if x else '否'
        return str(x).replace('|','/').replace('\n',' ')
    return '| '+' | '.join(map(str,df.columns))+' |\n| '+' | '.join(['---']*len(df.columns))+' |\n'+'\n'.join('| '+' | '.join(fmt(v) for v in row)+' |' for row in df.itertuples(index=False,name=None))
def finishfig(fig,name):
    dst=DOC/'figures'; dst.mkdir(parents=True,exist_ok=True)
    fig.tight_layout(); fig.savefig(dst/(name+'.png'),dpi=180); fig.savefig(dst/(name+'.pdf')); plt.close(fig)
def plots():
    start('plots'); plt.rcParams.update({'font.size':9,'axes.spines.top':False,'axes.spines.right':False})
    summary=get('probability-summary.parquet'); contrast=get('main-contrasts.parquet')
    fig,ax=plt.subplots(figsize=(10,4)); xx=np.arange(4); width=.13
    for a,arm in enumerate(ARMS):
        y=summary[summary.arm==arm].set_index('protocol').loc[PROTOCOLS].composite
        ax.bar(xx+(a-2.5)*width,y,width,label=arm)
    ax.set_xticks(xx,[NAMES[p] for p in PROTOCOLS]); ax.set_ylabel('Composite log loss (bits; lower better)'); ax.legend(ncol=6,fontsize=8)
    finishfig(fig,'oracle-probability-loss')
    fig,ax=plt.subplots(figsize=(9,5))
    y=np.arange(len(contrast)); means=contrast.gain_bits.to_numpy()
    # Quantile intervals need not contain a skewed point estimate; draw independently.
    ax.hlines(y,contrast.lower_adjusted,contrast.upper_adjusted,color='tab:blue'); ax.scatter(means,y,s=25,color='tab:blue')
    ax.axvline(0,color='gray',lw=1); ax.set_yticks(y,[NAMES[r.protocol]+' / '+r.contrast for r in contrast.itertuples()]); ax.invert_yaxis()
    ax.set_xlabel('Reference minus D1 loss (bits); 12-family adjusted interval')
    finishfig(fig,'main-contrasts')
    fig,axes=plt.subplots(1,4,figsize=(12,3.5),sharey=True)
    for ax,p in zip(axes,PROTOCOLS):
        sub=summary[summary.protocol==p].set_index('arm')
        for d in ['D1','D2','D3']: ax.plot(range(5),[sub.loc[d+'-'+v,'composite'] for v in KAPPAS],marker='o',label=d)
        ax.axhline(sub.loc['D0','composite'],color='black',ls='--',label='D0'); ax.set_xticks(range(5),KAPPAS); ax.set_title(NAMES[p]); ax.set_xlabel('kappa (no selection)')
    axes[0].set_ylabel('Composite log loss (bits)'); axes[-1].legend(fontsize=8)
    finishfig(fig,'shrinkage-sensitivity')
    cov=get('decomposition.parquet'); fig,axes=plt.subplots(1,2,figsize=(12,4))
    for ax,kind in zip(axes,['empirical','smoothed']):
        d=cov[cov.distribution==kind].groupby(['protocol','j']).between_fraction.mean().unstack().loc[PROTOCOLS]
        im=ax.imshow(d,vmin=0,vmax=1,cmap='viridis',aspect='auto'); ax.set_yticks(range(4),[NAMES[p] for p in PROTOCOLS]); ax.set_xticks(range(10),FEATURES,rotation=65,ha='right'); ax.set_title(kind+' coherent covariance'); fig.colorbar(im,ax=ax,label='Between-business trace / total')
    finishfig(fig,'covariance-decomposition')
    moments=get('outer-moments.parquet'); fig,ax=plt.subplots(figsize=(10,4)); width=.13
    for i,t in enumerate(TARGETS):
        vals=moments.assign(err=abs(moments['error_'+t])/PI).groupby('protocol').err.mean().loc[PROTOCOLS]
        ax.bar(xx+(i-2.5)*width,vals,width,label=t)
    ax.set_xticks(xx,[NAMES[p] for p in PROTOCOLS]); ax.set_ylabel('Outer class-tail MAE (conditional mass)'); ax.legend(ncol=6,fontsize=8)
    finishfig(fig,'moment-target-errors')
    q=pd.read_parquet(OUT/'qualification/all-relations.parquet'); fig,ax=plt.subplots(figsize=(10,4))
    for i,field in enumerate(['reliable','incremental','selected']):
        vals=q.groupby('protocol')[field].sum().loc[PROTOCOLS]; ax.bar(xx+(i-1)*.23,vals,.23,label=field)
    ax.set_xticks(xx,[NAMES[p] for p in PROTOCOLS]); ax.set_ylabel('Relations across five outer roles (300 / deployment)'); ax.legend()
    finishfig(fig,'qualification-counts')
    activity=get('constraint-activity.parquet'); fig,ax=plt.subplots(figsize=(9,4))
    for i,field in enumerate(['reliable','selected']):
        vals=activity[activity[field]&activity.interval_nonempty].assign(active=lambda d:d.violation>1e-12).groupby('protocol').active.sum().reindex(PROTOCOLS,fill_value=0)
        ax.bar(xx+(i-.5)*.3,vals,.3,label=field)
    ax.set_xticks(xx,[NAMES[p] for p in PROTOCOLS]); ax.set_ylabel('Frozen LR violated intervals (training only)'); ax.legend()
    finishfig(fig,'constraint-activity')
    finish('Q19',figures=7)

def report():
    c=start('report'); v=read(OUT/'verification.json'); require(v['pass'],'Verification required')
    summary=get('probability-summary.parquet'); contrasts=get('main-contrasts.parquet'); moments=get('outer-moments.parquet')
    cov=get('decomposition.parquet'); qual=pd.read_parquet(OUT/'qualification/all-relations.parquet')
    activity=get('constraint-activity.parquet'); gradients=get('constraint-gradients.parquet'); inner=pd.read_parquet(OUT/'moments/inner-oof.parquet')
    main=summary[summary.arm.isin(ARMS)].pivot(index='protocol',columns='arm',values='composite').loc[PROTOCOLS,ARMS]
    main.index=[NAMES[p] for p in main.index]; main=main.reset_index(names='部署')
    counts=qual.groupby('protocol')[['reliable','incremental','selected']].sum().reindex(PROTOCOLS)
    counts=counts.reset_index(); counts.protocol=counts.protocol.map(NAMES)
    nt=int(contrasts.positive_adjusted.sum()); selected=int(qual.selected.sum()); reliable=int(qual.reliable.sum())
    intro=(f'本轮完成Q00–Q21。保持23,566对连接、480次访问、30个内容和五折全局内容划分不变，新增1000个业务条件核bundle。'
           f'十二项概率主比较中{nt}项校正区间下界大于零；统计目标共有{reliable}/1200个角色关系通过基本可靠资格，'
           f'{selected}个进入预登记约束列表。没有新增业务分类器拟合，没有新的F1结论。')
    lines=['# 业务条件概率核与统计约束资格：第一阶段完整报告','', '日期：2026-10-05；状态：完成并停止，待用户决定下一阶段。','',intro,'',
      '## 1 实验问题、对象与权限','',
      '检验共同核遗漏的业务条件关系，能否从连接级概率预测转化为准确、非冗余的类别总体统计先验。业务条件概率评价允许真实留出Y，是离线oracle诊断，不是攻击分类；资格目标仅使用训练pre/post/Y，校准评分只使用内层留出post/Y。外层post/Y评分在资格和区间封存之后进行。','',
      '| 部署 | 排他TCP对 | 访问 | 当前配置边界 |','| --- | ---: | ---: | --- |',
      '| SS | 5608 | 120 | AES-256-GCM，无plugin/smux；不从包数推导chunk数 |',
      '| VLESS | 5957 | 120 | TCP+TLS，无REALITY/Vision/smux；不沿用旧Vision解释 |',
      '| Trojan | 5919 | 120 | TCP+TLS；不可把字节差当作精确加密内请求头开销 |',
      '| VMess | 6082 | 120 | WS+TLS，auto；最终安全模式等历史缺口保留 |','',
      'AnyTLS/Hy2未纳入本轮同粒度核；保留共享carrier及资格边界。共同成员来自双侧离线关联，登记实体跨折检查不等于普遍完整TCP epoch证明。每类五个内容，每内容每部署四重复（1、2、4、5）；每外层训练24内容/96访问、测试6内容/24访问；内层训练18内容/72访问、验证6内容/24访问。全部部署、两侧、重复及内部连接随内容整体划分。','',
      '六业务：'+ '；'.join(LABELS)+'。','',
      '## 2 模型与评分契约','',
      '十变量：'+', '.join(FEATURES)+'。前四字节变量9箱，后六计数变量10箱；前八权重各1/12，交互两变量各1/6。连接质量为1/(内容重复数×该访问连接数)，外层质量24、每类4，内层质量18、每类3，不把加权质量当独立多项试验数。','',
      '共同核保持alpha=beta=1；条件真配/匿名核以(n_y+kappa K_common)/(n_y(A)+kappa)收缩，空入口行回退共同核。标签post参照以(n_y(B)+kappa q)/(N_y+kappa)收缩。匿名组仅按内容两侧边际乘积构造，不恢复访问或连接身份。主kappa=1；0.25、4、16、∞全部报告，不选择测试赢家。∞精确回到共同参照。','',
      '| 臂 | 预测 | 信息权限 |','| --- | --- | --- |','| D0 | 共同真配B/A | pre |','| DG | 共同匿名组B/A | pre |','| DB | 共同post边际 | 无pre/Y |','| D1 | 业务条件真配B/A,Y | pre及oracle Y |','| D2 | 业务条件匿名组B/A,Y | pre及oracle Y |','| D3 | 业务条件post边际B/Y | oracle Y，无pre |','',
      '连接负log2概率先访问内等权，再内容内四访问等权，再内容等权。复合评分不是十维联合似然；概率增益不是条件互信息估计，也不是业务F1。Brier/尾概率均为出口箱状态预测诊断。','',
      '## 3 内容外概率主结果','',table(main),'','![概率损失](figures/oracle-probability-loss.png)','',
      '下表正数表示D1改善；10000次六业务分层内容bootstrap，跨部署共享抽样。同内容重复和连接一起抽样。95%及12项Bonferroni对应99.583333%边际区间条件于已拟合核，不重拟合，不是外部验证。','',table(contrasts[['protocol','contrast','gain_bits','lower_95','upper_95','lower_adjusted','upper_adjusted','positive_adjusted']]),'',
      '![十二项主比较](figures/main-contrasts.png)','',
      '## 4 固定收缩敏感性、业务和变量分项','',
      '以下设置均未参与选参，也不升级为新的主检验家族。逐业务、逐变量、尾部校准与Brier完整保存在content-feature-probabilities.parquet；支持情况保存于inner/outer-support.parquet。','']
    sens=summary[summary.arm.str.startswith(('D1-','D2-','D3-'))].pivot(index='arm',columns='protocol',values='composite').reindex(columns=PROTOCOLS).reset_index()
    lines += [table(sens),'','![收缩敏感性](figures/shrinkage-sensitivity.png)','']
    detail=get('content-feature-probabilities.parquet')
    business=detail[detail.arm.isin(ARMS)].copy(); business['weighted_loss']=business.loss*business.j.map(dict(enumerate(WEIGHTS)))
    business=business.groupby(['protocol','label_id','arm','content_id']).weighted_loss.sum().groupby(['protocol','label_id','arm']).mean().unstack('arm')[ARMS].reset_index()
    lines += ['### 4.1 全六业务主kappa分项','',table(business),'']
    feature=detail[detail.arm.isin(ARMS)].groupby(['protocol','feature','arm']).loss.mean().unstack('arm')[ARMS].reset_index()
    lines += ['### 4.2 全十变量主kappa分项','',table(feature),'']
    support=get('outer-support.parquet').groupby('protocol').agg(empty_class_A_rows=('empty_A_rows','sum'),class_A_rows=('bins','sum')).reset_index()
    lines += ['### 4.3 稀疏支持','',table(support,0),'',
      '空行仍保留并回退，不按稀疏程度删除连接。空行数是在五外层×十变量×六类范围累计，不能当作独立连接发生率。','',
      '## 5 条件协方差分解','',
      '经验联合分布中，以同一p(Y/A)、nu(A)计算业务内项与业务均值项，两项PSD且相加重放总条件协方差。业务内项仍含内容、连接角色、访问和网络效应，不是纯协议噪声。','',
      '平滑版本仅分解一致混合Kbar=sum_y p(y/A)K_y；它一般不等于原共同核。表中gap显式报告这一差异，不把不同平滑边际拼成错误的恒等式。使用同范围训练post尺度D和族权重变换，两项不分别trace归一；冻结零LR中心化权重只做训练能量解释。','']
    cv=cov.groupby(['protocol','distribution']).agg(within_trace=('within_trace','sum'),between_trace=('between_trace','sum'),
        within_score_energy=('within_score_energy','sum'),between_score_energy=('between_score_energy','sum'),
        max_mixture_common_gap=('mixture_common_max_gap','max'),max_covariance_common_gap=('covariance_common_max_gap','max')).reset_index()
    cv['between_trace_fraction']=cv.between_trace/(cv.within_trace+cv.between_trace)
    lines += [table(cv),'','![协方差两项](figures/covariance-decomposition.png)','',
      '此处跨变量trace汇总只作描述；能量使用登记族权重及实际训练尺度，逐变量和逐折完整数据另存。不能由训练业务均值项推断未见内容分类增益。','',
      '## 6 总体统计目标能否迁移到新内容','',
      '每类每变量仅固定一个上尾b>=4（字节>=4096，计数>=4），共60关系。目标为pi×类条件尾质量，pi=1/6。S只来自允许训练pre；不借用验证pre。T0/T1为共同/条件真配，G0/G1为共同/条件匿名组，P0为经验post，P1为收缩post。','']
    for title,data in [('训练区四折OOF误差',inner),('外层新内容误差',moments)]:
        er=[]
        for p in PROTOCOLS:
            for t in TARGETS:
                x=data[data.protocol==p]['error_'+t]/PI
                er.append({'部署':NAMES[p],'目标':t,'bias':x.mean(),'MAE':abs(x).mean(),'max_abs':abs(x).max()})
        lines += ['### '+title,'','误差转换回类内质量单位，下表0.10表示10个百分点；这些不是独立显著性检验。','',table(pd.DataFrame(er)),'']
    lines += ['![总体目标误差](figures/moment-target-errors.png)','',
      '## 7 资格、容差和停止条件','',
      '主资格仅T1；每关系四个训练外拟合残差，经验区间为全训练目标+[min e,max e]，与[0,pi]求交。空交集拒绝，不把两端独立截断成假点区间。它不是95%预测区间或严格conformal保证。','',
      '基本可靠：四残差完整有限、max|e|<=0.10pi、非空且宽<=0.50pi、OOF该类与其余五类尾质量平均差绝对值>=0.05。真配增量另要求相对G1、经验P0及收缩P1各改善MAE>=0.01pi，且各至少3/4内容严格改善。最多六关系，族/业务各至多2、特征至多1，按最弱参照改善排序，不按外层结果或冻结LR违反量挑关系。','',
      table(counts,0),'','![资格计数](figures/qualification-counts.png)','']
    reasons=[]
    for p in PROTOCOLS:
        sub=qual[qual.protocol==p]
        for reason in ['support','max_error','empty_interval','width','task_relevance','no_increment_vs_all_three_controls']:
            reasons.append({'部署':NAMES[p],'失败原因':reason,'关系数':sub.failures.str.split(';').apply(lambda a:reason in a).sum()})
    lines += ['### 7.1 失败原因（可重叠）','',table(pd.DataFrame(reasons),0),'',
      '### 7.2 外层区间覆盖（描述，不用于修改资格）','']
    coverage=[]
    for p in PROTOCOLS:
        sub=moments[moments.protocol==p]
        for name,mask in [('全部60关系',pd.Series(True,index=sub.index)),('基本可靠',sub.reliable),('最终登记',sub.selected)]:
            ss=sub[mask]; valid=ss[ss.interval_nonempty]
            coverage.append({'部署':NAMES[p],'集合':name,'总数':len(ss),'非空区间':len(valid),'覆盖数':int(valid.covered.sum()),
                '覆盖比例':float(valid.covered.mean()) if len(valid) else 'NA'})
    lines += [table(pd.DataFrame(coverage)),'',
      '## 8 冻结零LR上的训练约束作用','',
      '使用同范围冻结模型与训练post计算mean p_theta(Y=y)×tail；不优化、不读取测试pre，不因原模型满足区间而缩窄容差。表中梯度是登记集合pi缩放平方hinge的参数梯度；空集合正则与梯度定义为零。','',table(gradients),'','![约束作用](figures/constraint-activity.png)','']
    active=[]
    for p in PROTOCOLS:
        s=activity[activity.protocol==p]
        for flag in ['reliable','selected']:
            ss=s[s[flag]&s.interval_nonempty]
            active.append({'部署':NAMES[p],'集合':flag,'非空数':len(ss),'违反数':int((ss.violation>1e-12).sum()),
                           '平均违反/pi':float((ss.violation/PI).mean()) if len(ss) else 0.})
    lines += [table(pd.DataFrame(active)),'',
      '## 9 结论与下一阶段决策','',
      f'概率预测的{nt}/12项校正阳性，应与统计目标的{selected}个登记关系分开解释。加入oracle业务条件可能有可利用关系，但不能据此宣称新增约束会改善post-only业务分类。','']
    if selected==0:
        lines += ['本轮没有关系同时通过预登记的可靠性、三参照增量和容量规则，因而没有可放行的真配新增约束。建议在此结项，保留业务条件概率核的测量结果；不启动GE分类、不降低门限、不从固定敏感性挑赢家。若继续，需要另立问题，而不是把概率预测阳性当作分类约束的通过证。','']
    else:
        nactive=int(((activity.selected)&(activity.violation>1e-12)).sum())
        lines += [f'最终登记关系{selected}个，其中冻结LR上训练违反{nactive}个。它们仅构成有限任务感知约束的候选资格，不是分类收益。本轮仍停止，是否开展独立登记、额外嵌套资格和公平rho/lambda预算的第二阶段由用户确认。','']
    lines += ['本实验是已见部署、回顾性固定队列、固定分箱和有限估计器的诊断。未验证条件独立、完整信道信息量、可逆变换、业务语义解耦、跨部署/日期泛化或在线无索引攻击。父访问标签不意味着每条CDN连接具有唯一业务语义。','',
      '## 10 工程、复现与交付','',table(pd.DataFrame([{'检查':k,'结果':z} for k,z in v.items()])),'',
      'Pytorch312，CUDA float64，严格确定性，关闭TF32；Arrow先于torch；加权频数用one-hot CUDA GEMV。源与包拟合前封存，旧源、核、分类器均未改写。角色白名单和实际读取台账不是OS安全沙箱。没有新采集、PCAP扫描、CPU拟合回退或业务分类训练。','',
      '- 实现与复现命令：`eval/business_conditioned_kernel/README.md`。',
      '- 契约/来源/环境/角色/测试：输出目录`manifests/`。',
      '- 1000个含全部收缩设置的核：`kernels/inner`和`kernels/outer`。',
      '- 全部60关系×20角色台账：`qualification/all-relations.parquet`及本目录`qualification-ledger.md`。',
      '- 矩量目标、四内容OOF、外层误差：`moments/`和`scores/outer-moments.parquet`。',
      '- 内容级概率/Brier/尾校准、协方差、作用及bootstrap：`scores/`。',
      '- 概率查询产物仅oracle诊断，不得复用于post-only攻击接口。','',
      '文档按write-page技能的证据组织原则生成，区分测量结果、解释假设和候选后续方法；未写入云端Pages。']
    DOC.mkdir(parents=True,exist_ok=True)
    (DOC/'formal-report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    ledger=['# 全部统计关系资格台账','','每部署每折60关系，包含失败；MAE、最大误差、区间为联合质量，除以pi可转换回类内质量。不得仅摘录阳性。','']
    for p in PROTOCOLS:
        for fold in range(5):
            s=qual[(qual.protocol==p)&(qual.outer==fold)].sort_values(['y','j'])
            ledger += [f'## {NAMES[p]} / 外层折{fold}','',table(s[['business','feature','mae','max_abs_error','relevance','lower','upper','reliable','incremental','selected','failures']]),'']
    (DOC/'qualification-ledger.md').write_text('\n'.join(ledger)+'\n',encoding='utf-8')
    (DOC/'README.md').write_text('# 第一阶段诊断交付\n\n见[完整报告](formal-report.md)与[全关系资格台账](qualification-ledger.md)。\n\n已完成Q00–Q21，无新业务分类器；本轮到此停止。\n',encoding='utf-8')
    write(OUT/'delivery-manifest.json',{'documents_sha256':{rel(p):sha(p) for p in DOC.glob('*.md')},
        'figures_sha256':{rel(p):sha(p) for p in (DOC/'figures').iterdir()},'stopped':True,
        'awaiting_stage_two_approval':True,'selected_relations':selected,'new_business_classifier_fits':0})
    finish('Q21',stopped=True,selected_relations=selected,positive_main_comparisons=nt)

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('stage',choices=['plots','report']); args=ap.parse_args()
    (plots if args.stage=='plots' else report)()
