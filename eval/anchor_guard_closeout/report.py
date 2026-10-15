"""Stop-cause explanation; no qualification or scientific endpoint is changed."""
from common import *
os.environ['MPLCONFIGDIR']=str(OUT/'plot-cache')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def run():
    q=pd.read_parquet(OUT/'tables/quadrant-summary.parquet');funnel=pd.read_parquet(OUT/'tables/gate-failure-funnel.parquet')
    marginal=pd.read_parquet(OUT/'tables/gate-failure-marginal.parquet');margins=pd.read_parquet(OUT/'tables/gate-margin-distributions.parquet')
    trace=pd.read_parquet(OUT/'tables/candidate-traces-full-C.parquet');foldtrace=pd.read_parquet(OUT/'tables/candidate-traces-folds.parquet')
    scopes=pd.read_parquet(OUT/'tables/projection-scope-summary.parquet');audit=read(OUT/'audits/numerical-replay-audit.json')
    coords=pd.read_parquet(OUT/'tables/coordinate-top5.parquet');figdir=target(DOC/'figures/placeholder').parent
    fig,axes=plt.subplots(1,2,figsize=(12,5),constrained_layout=True)
    for ax,arm in zip(axes,['P','G']):
        d=funnel[funnel.arm.eq(arm)];ax.barh(np.arange(len(d)),d.after);ax.set_yticks(np.arange(len(d)),d.stage,fontsize=8);ax.invert_yaxis()
        ax.set_title(arm+' fixed-order survival, not causal attribution');ax.set_xlabel('Remaining role-blocks')
        for i,n in enumerate(d.after):ax.text(n+3,i,str(n),va='center',fontsize=8)
        ax.set_xlim(0,620)
    fig.savefig(figdir/'qualification-failure-path.png',dpi=160);plt.close(fig)
    fig,axes=plt.subplots(1,3,figsize=(13,4),constrained_layout=True)
    colors={'P':'tab:blue','G':'tab:orange'}
    for arm in ['P','G']:
        d=q[q.arm.eq(arm)].set_index('quadrant').loc[QUADS];x=np.arange(4)+(-.17 if arm=='P' else .17)
        for ax,col,title in zip(axes,['mass','raw_contribution','std_contribution'],['Quadrant mass','Raw MSE contribution','Standardized MSE contribution']):
            ax.bar(x,d[col],width=.32,label=arm,color=colors[arm]);ax.set_xticks(range(4),QUADS);ax.set_title(title);ax.axhline(0,color='gray',linewidth=.6)
    axes[0].legend();fig.savefig(figdir/'quadrant-mass-and-risk.png',dpi=170);plt.close(fig)
    fig,axes=plt.subplots(1,3,figsize=(13,4),constrained_layout=True)
    for ax,name,title in zip(axes,['variation_margin','epsilon_margin','ratio_margin'],['Content variation minus 0.10','0.10 minus raw Q90','0.50 minus Q90/variation']):
        for arm in ['P','G']:
            d=margins[(margins.arm==arm)&(margins.margin==name)].set_index('feature').reindex(FEATURES)
            ax.plot(range(10),d['median'],marker='o',markersize=3,label=arm)
        ax.axhline(0,color='gray',linestyle='--');ax.set_title(title,fontsize=10);ax.set_xticks(range(10),FEATURES,rotation=65,ha='right',fontsize=7)
    axes[0].legend();fig.savefig(figdir/'training-gate-margins.png',dpi=170);plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(11,4),constrained_layout=True)
    for ax,col,title in zip(axes,['mean_raw_delta','mean_std_delta'],['Raw MSE change by projection scope','Standardized MSE change by scope']):
        for k,arm in enumerate(['P','G']):
            d=scopes[scopes.arm.eq(arm)];ax.bar(np.arange(3)+(-.17 if k==0 else .17),d[col],width=.32,label=arm)
        ax.set_xticks(range(3),['All candidates','Train eligible','Final no-op']);ax.set_title(title,fontsize=10);ax.axhline(0,color='gray',linewidth=.6)
    axes[0].legend();fig.savefig(figdir/'projection-scope-and-coordinate-risk.png',dpi=170);plt.close(fig)
    principal=trace[['role_id','arm','feature','epsilon','variation','epsilon_variation_ratio','OOF_coverage','OOF_excess',
                    'relation_qualified','map_violation_gate','full_C_replayed_train_eligible','rejection_reasons']]
    summary=q[['arm','quadrant','mass','raw_conditional_delta','raw_contribution','std_conditional_delta','std_contribution',
               'raw_worsened_mass','std_worsened_mass']]
    failure=marginal[(marginal.scope=='fold')].groupby(['arm','gate'],as_index=False)[['candidates','passed','failed']].sum()
    pio=q[(q.arm=='P')&(q.quadrant=='IO')].iloc[0];poo=q[(q.arm=='P')&(q.quadrant=='OO')].iloc[0]
    top=coords[['arm','target','feature','coordinate','rank','scale_min','scale_median','std_positive','std_negative','top5_positive_share']]
    registry=[]
    for p in sorted((OUT/'tables').glob('*.parquet')):
        n=len(pd.read_parquet(p));registry.append({'table':p.stem,'rows':n,'parquet':rel(p),'csv':rel(OUT/'csv'/f'{p.stem}.csv')})
    write(OUT/'reports/table-registry.json',registry)
    s=f'''# 锚点资格失败路径与投影误差分层报告

2026年10月12日。独立算式重放通过，原资格、距离、权重、Q90和投影口径没有发现需要修订的实质不一致。保持`stop_no_supported_protection_target`，零新映射拟合、零新分类拟合，不启动180个分类器。

## 诊断范围和原结果保留

使用父运行既有480份C预测、四折评分和完整C规则；1200个角色块、4800个折块、19200行显式四格以及192000个观测块。P包含实际C配对，G包含内容内匿名Cartesian组合，不能把组合或角色重复暴露当独立新访问。没有读取H、目标U或PCAP，没有更改阈值、锚点或原验收。

## 资格失败路径

{failure.to_markdown(index=False)}

各门边际失败可以重叠。固定顺序漏斗只描述展示次序，不提供哪一个门造成方法失败的因果归因。门值余量说明离登记界限的距离，不能自行证明阈值过强或支持放宽。

![固定失败路径](figures/qualification-failure-path.png)

![训练门余量](figures/training-gate-margins.png)

逐折完整表保存Q90、两侧内容中心变化、比例、通过标志及各门余量；逐角色表展开四折覆盖、平均越界、越界折数和完整C三项资格。分位数上限没有截断：实际Q90先保存，再执行0.10资格检查。

## 四个SS候选的停止原因

{principal.to_markdown(index=False,floatfmt='.6f')}

两个R_unique_zero_runs通过四折关系资格和完整C复核，但原映射额外违约分别为-0.093750与-0.078125，达到0.10的折数都是零。它们失败于map_excess，不是完整C资格，也不是原包级FR锚点。

两个W_up存在映射额外违约，却未满足完整块的非平凡关系资格；一个还未满足最差折覆盖。稳定关系与映射破坏分别出现在不同块，不能合成一项保护证据。

## 四格质量与投影风险

{summary.to_markdown(index=False,floatfmt='.8f')}

II为真实界内且映射界内；IO为真实界内且映射界外；OI为真实界外且映射界内；OO为两者都界外。条件误差是该格内部均值，贡献是按其质量乘回总体的误差变化。空格质量零而条件均值缺失，没有用零均值参与汇总。

P的IO质量为{pio.mass:.6f}，原始误差总体贡献为{pio.raw_contribution:.8f}；OO质量为{poo.mass:.6f}，原始误差总体贡献为{poo.raw_contribution:.8f}。这些是候选几何诊断，不是业务结果。完整贡献见分部署、分块与资格分层表。

![四格风险](figures/quadrant-mass-and-risk.png)

真实严格在原始频率欧氏球内时，投影的原始误差非增条件通过；标准化坐标可能因不同scale改变几何而出现另一种误差方向。真实界外的投影没有非增保证。epsilon加1e-12的评分边界与精确投影半径分开审计。

## 投影范围与坐标放大

{scopes.to_markdown(index=False,floatfmt='.8f')}

all_candidate_blocks是对十个候选计算的假设性投影；training_eligible_blocks仅修改训练折合格块；final_selected_blocks_noop对应实际空集合。第一类候选投影的改善或恶化不能写成最终Guard效果，更不能代替F1。

![作用范围与坐标风险](figures/projection-scope-and-coordinate-risk.png)

坐标贡献表将正向恶化与负向改善分别保存，包含scale、真实常数维标志、IO与OO正贡献。top5排序仅用于解释，不删除坐标、不重新赋权。原始MSE与标准化MSE的差异不是自动的尺度转换错误。

## 独立核对

{audit['checks']}项数值和标志核对通过。最大四格误差闭合与重放误差详见numerical-replay-audit.json。未调用父rules、project或score函数，未导入父runner，没有任何fit入口。固定源/C成员、匿名权限、常数维scale=1和源内容剔除均重放核对。

P训练Q90取48值中的第44项，完整C取64值中的第58项；G分别取192值第173项及256值第231项。两侧内容中心两两距离分别为66或120个，Q90位置为60或108。拟合折与完整C采用相同距离与质量定义，只是样本数不同。表格始终使用原冻结epsilon，没有采用重放出的新规则。

## 结项决定

计算一致，保留原停止，无需数值修复或重新拟合。当前结果只关闭完整直方图块近似恒等保护这一具体候选；不否定粗关系、其他表示或条件不变关系，也不支持它们一定有效。P-small已有正结果不撤回，O1仍暂停，独立物理post与在线窗口资格未获得新证据。

所有表格同时提供Parquet和静态CSV，CSV没有可调阈值或Excel重计算模型。来源与输出哈希见独立结项验收。表索引和两个候选的四折详细轨迹见附录。
'''
    textfile(DOC/'closeout-report-20261012.md',s)
    index='\n'.join(f"- [{x['table']} CSV]({str((ROOT/x['csv']).resolve()).replace(chr(92),'/')})，{x['rows']}行；[Parquet]({str((ROOT/x['parquet']).resolve()).replace(chr(92),'/')})" for x in registry)
    textfile(DOC/'appendix-20261012.md','# 锚点诊断结项附录\n\n## 候选四折及完整C\n\n'+foldtrace.to_markdown(index=False,floatfmt='.8f')+
              '\n\n'+principal.to_markdown(index=False,floatfmt='.8f')+'\n\n## 正标准化贡献最大的坐标\n\n'+top.to_markdown(index=False,floatfmt='.8f')+
              '\n\n## 表索引\n\n'+index+'\n')
    write(OUT/'analysis-complete.json',{'passed':True,'table_count':len(registry),'tables':registry,'parent_stop_preserved':True,'new_mapping_fits':0,'new_classifier_fits':0})
    progress('analysis_and_report_complete',tables=len(registry),new_fits=0)

if __name__=='__main__':run()
