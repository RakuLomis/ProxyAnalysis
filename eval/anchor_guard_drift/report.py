"""C-only report with unchanged stopping gates; no new business scores."""
from common import *
os.environ['MPLCONFIGDIR']=str(OUT/'plot-cache')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def plots(q,f,changes):
    figdir=DOC/'figures';figdir.mkdir(parents=True,exist_ok=True)
    fig,axes=plt.subplots(2,3,figsize=(16,7),constrained_layout=True)
    for ri,arm in enumerate(['P','G']):
        for ci,(key,title) in enumerate([('relation_qualified','Reliable relation'),('map_violation_gate','Map excess gate'),('accepted_anchor','Final anchor')]):
            z=q[q.arm.eq(arm)].groupby(['target','feature'])[key].sum().unstack().reindex(index=PROTOCOLS,columns=FEATURES)
            ax=axes[ri,ci];im=ax.imshow(z.to_numpy(),vmin=0,vmax=15,cmap='Blues',aspect='auto')
            ax.set_title(arm+' '+title);ax.set_xticks(range(10),FEATURES,rotation=65,ha='right',fontsize=8);ax.set_yticks(range(4),PROTOCOLS)
            for i in range(4):
                for j in range(10):ax.text(j,i,str(int(z.iloc[i,j])),ha='center',va='center',fontsize=8)
    fig.colorbar(im,ax=axes.ravel().tolist(),label='Role-block count; overlapping C contents');fig.savefig(figdir/'qualification-and-gates.png',dpi=160);plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(11,4),constrained_layout=True)
    for ax,arm in zip(axes,['P','G']):
        d=q[q.arm.eq(arm)];colors=np.where(d.relation_qualified,'tab:blue','lightgray')
        ax.scatter(d.OOF_v_real,d.OOF_v_map,c=colors,s=12,alpha=.55)
        ax.plot([0,.9],[.1,1],'--',color='tab:red',label='Excess = 0.10');ax.plot([0,1],[0,1],':',color='black')
        ax.set(xlim=(-.02,1.02),ylim=(-.02,1.02),xlabel='Observed target violation',ylabel='OOF map violation',title=arm+' all 600 role-blocks')
        ax.legend(fontsize=8)
    fig.savefig(figdir/'real-versus-map-violations.png',dpi=160);plt.close(fig)
    fig,ax=plt.subplots(figsize=(10,4),constrained_layout=True)
    by=q.groupby(['arm','feature'])[['OOF_raw_MSE_before','OOF_raw_MSE_after']].mean()
    x=np.arange(10)
    for arm,style in [('P','-'),('G','--')]:
        d=by.loc[arm].reindex(FEATURES)
        ax.plot(x,d.OOF_raw_MSE_before,style,label=arm+' original')
        ax.plot(x,d.OOF_raw_MSE_after,style,marker='o',markersize=3,label=arm+' candidate ball projection')
    ax.set_xticks(x,FEATURES,rotation=45,ha='right',fontsize=8);ax.set_ylabel('OOF raw block MSE')
    ax.set_title('All candidate blocks; not final selected Guard, not classification');ax.legend(fontsize=8)
    fig.savefig(figdir/'candidate-recovery-risk.png',dpi=160);plt.close(fig)
    fig,ax=plt.subplots(figsize=(10,4),constrained_layout=True)
    for arm,marker in [('P','o'),('G','x')]:
        d=q[q.arm.eq(arm)].groupby('feature')[['OOF_coverage','OOF_min_coverage']].mean().reindex(FEATURES)
        ax.plot(x,d.OOF_coverage,marker=marker,label=arm+' mean coverage')
        ax.plot(x,d.OOF_min_coverage,marker=marker,linestyle='--',label=arm+' mean worst-fold coverage')
    ax.axhline(.90,color='gray',linestyle=':');ax.axhline(.875,color='gray',linestyle=':')
    ax.set_xticks(x,FEATURES,rotation=45,ha='right',fontsize=8);ax.set_ylim(0,1.02);ax.set_ylabel('Coverage')
    ax.set_title('All candidates; averages do not replace per-role gates');ax.legend(fontsize=8)
    fig.savefig(figdir/'heldout-content-coverage.png',dpi=160);plt.close(fig)

def run():
    with stage('report'):
        q=pd.read_parquet(OUT/'scores/anchor-qualification.parquet');f=pd.read_parquet(OUT/'scores/fold-scores.parquet')
        ch=pd.read_parquet(OUT/'audits/source-view-change.parquet');fits=pd.read_parquet(OUT/'diagnostics/accepted-maps.parquet')
        gate=read(OUT/'rules/anchor-gate.json');tests=read(OUT/'audits/tests.json');cohort=read(OUT/'audits/cohort-and-replay.json')
        plots(q,f,ch)
        summary=q.groupby(['target','arm']).agg(role_blocks=('block','size'),relation_qualified=('relation_qualified','sum'),
                    map_gate=('map_violation_gate','sum'),final_anchors=('accepted_anchor','sum')).reset_index()
        byblock=q.groupby(['arm','feature']).agg(relation_qualified=('relation_qualified','sum'),final_anchors=('accepted_anchor','sum'),
                    mean_coverage=('OOF_coverage','mean'),mean_map_excess=('OOF_excess','mean')).reset_index()
        active=q[q.accepted_anchor][['target','group','outer','arm','feature','epsilon','variation','OOF_coverage','OOF_excess']]
        affected=ch[ch.arm.isin(['P-Guard','P-Uniform','G-Guard'])].groupby('arm').agg(role_views=('role_id','size'),
                     modified_exposures=('modified_visits','sum'),mean_correction=('mean_correction','mean'),max_correction=('max_correction','max')).reset_index()
        means=f.groupby('arm')[['raw_MSE_before','raw_MSE_after','standardized_MSE_before','standardized_MSE_after']].mean().reset_index()
        if gate['P_anchor_role_blocks']:
            conclusion=f"P在{gate['P_roles_with_anchors']}个角色中有{gate['P_anchor_role_blocks']}个角色块同时通过关系、覆盖、越界和完整C复核。存在启动有限分类对照的结构依据，但尚无新的业务收益证据。"
        elif not gate['P_relation_qualified']:
            conclusion='全部600个P角色块中，没有块通过登记的非平凡性、小变化和内容留出覆盖组合门。当前候选没有形成实施锚点保护的依据，不启动分类、不放宽门限。'
        else:
            conclusion='存在通过关系资格的P角色块，但没有块最终同时通过映射越界和完整C复核。当前保护没有得到支持的作用对象，不启动分类、不放宽门限。'
        s=f'''# 不变锚点与漂移越界第一阶段报告

2026年10月12日。{conclusion}

## 数据与执行范围

extend既有SS、VLESS、Trojan、VMess队列，480访问、30独立内容、23566排他共同有效TCP对；60个外层角色，每角色C为16内容64访问，四折各12内容48访问拟合、4内容16访问验证。O1继续暂停，AnyTLS、Hy2不进入本轮TCP诊断。

已完成480个OOF全96维仿射映射，没有新分类器拟合，没有业务F1重算。十个候选是原96维的十个完整归一化直方图块，未预先指定FR为锚点。原P-small、组控制、96维M-S及162维结果未覆盖。

## 规则与权限

距离为原始频率块L2除以sqrt(2)。训练epsilon为经验Q90，上限0.10；两侧内容中心距离Q90的最小值至少0.10，epsilon与该变化尺度之比不超过0.5。四折训练资格都通过，验证每折覆盖至少0.875、合并至少0.90。映射额外违约质量至少0.10，并且至少两折达到0.10，才进入完整C容差复核。

G独立使用内容内4乘4匿名Cartesian组合，不读取P的规则、访问身份或重复身份。这是保守集合约束，不等价于逐访问不变性；不能仅用锚点数量比较宣布身份价值。

缩放仅使用剔除验证内容后的240个源post与48个C训练post。eta沿用历史源内选出的JA2值，实际目标部署不参与原选择；但旧选择曾接触源部署上的相同内容，因此本诊断不是对全部历史研究流程完全独立的盲测。

完整C仅由可信装包器拆分，诊断工作器只能读取自己的拟合、预测或封存后评分包。全部480份C预测先封存，再解锁C验证post评分。该角色H查询、H标签、目标U数值和全量原生缓存没有进入本轮。跨角色各自训练范围不同，但规则不跨角色共享。应用级字段和API隔离不是操作系统沙箱。

## 分部署资格和停止门

{summary.to_markdown(index=False)}

每个部署每种对应有15角色乘10块，即150个角色块。角色共享部分C内容，不是150个独立实验。

![资格与门](figures/qualification-and-gates.png)

## 分块关系与变化

{byblock.to_markdown(index=False,floatfmt='.6f')}

![真实与映射违约](figures/real-versus-map-violations.png)

![内容留出覆盖](figures/heldout-content-coverage.png)

平均覆盖只能描述所有候选，不能替代逐角色最差折门。高相关、平均差小和归一化总和均未成为资格标准。

## 最终锚点

{active.to_markdown(index=False,floatfmt='.6f') if len(active) else '没有最终合格锚点。全部失败块及逐折原因见详细附录和anchor-qualification.parquet。'}

## 恢复与辅助视图

{means.to_markdown(index=False,floatfmt='.6f')}

上表和下图是全部候选块的投影诊断；其投影在验证post解锁之前已计算，但不是最终选中集合的独立Guard风险评价。恢复误差不替代分类。筛选后数字条件于本C选择，不是新的独立验证。

![候选恢复风险](figures/candidate-recovery-risk.png)

{affected.to_markdown(index=False,floatfmt='.6f')}

源视图每角色288行，汇总的是重复训练暴露，不是新增独立访问。完整C上的冻结原映射仅作描述性核对，不参与OOF停止门。负坐标和块和偏离照实保存，未投影单纯形；输出仍是统计适配视图，不是合法协议会话。

## 数值与工程验收

GPU为{contract()['environment']['gpu']}，Pytorch312、torch {contract()['environment']['torch']}、CUDA {contract()['environment']['cuda']}。映射、保护及推理均CUDA float64，无CPU回退。{tests['checks']}项合成与权限检查通过；历史频率及映射视图重放最大误差为{cohort['max_frequency_or_mapped_view_replay_error']:.3g}。

480个映射全部接受；最大原坐标梯度为{fits.gradient_max.max():.3g}，最大目标重放误差{fits.objective_replay_error.max():.3g}，最大梯度重放误差{fits.gradient_replay_error.max():.3g}，最大线性方程归一化残差{fits.normalized_equation_residual.max():.3g}。接受门分别保持1e-8、1e-10、1e-10、1e-10。

## 阶段决定与结论边界

当前状态为`{gate['status']}`。分类阶段没有授权或启动。{conclusion}

若有合格保护目标，后续仍需用户确认三新臂、最多180个LR拟合。若没有，则本候选按登记规则停止；不指定FR补位、不加阈值、不将候选恢复改善写成业务收益。

本结果不证明所有代理流量都缺少不变关系，也不证明漂移映射没有其他错误。四类C的关系不自动推广到两类U或跨部署源pre。完整物理post连接、独立窗口、无索引在线输入资格仍未通过；当前pre不是DIRECT反事实。小样本经验覆盖不是真实总体覆盖保证，固定既有队列不是外部验证。
'''
        textfile(DOC/'anchor-diagnostic-report-20261012.md',s)
        textfile(DOC/'detailed-appendix-20261012.md','# 不变锚点第一阶段详细附录\n\n## 全部角色块与拒绝原因\n\n'+q.to_markdown(index=False,floatfmt='.6f')+
                 '\n\n## 全部内容折\n\n'+f.to_markdown(index=False,floatfmt='.6f')+'\n\n## 源辅助视图修改\n\n'+ch.to_markdown(index=False,floatfmt='.6f')+'\n')
        write(OUT/'reports/summary.json',{'gate':gate,'relation_counts':summary.to_dict('records'),'modified_source_views':affected.to_dict('records'),
              'new_classifier_fits':0,'new_mapping_fits':480,'tests':tests['checks']})

if __name__=='__main__':run()
