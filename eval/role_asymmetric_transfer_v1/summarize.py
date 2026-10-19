"""Human-readable fixed-policy results; no retrospective winner selection."""
from common import *
from weight_schedule import registry,PRIMARY,REFERENCES

def md(frame):
    cols=list(frame);lines=['| '+' | '.join(cols)+' |','| '+' | '.join(['---']*len(cols))+' |']
    for row in frame.itertuples(index=False,name=None):lines.append('| '+' | '.join(str(x) for x in row)+' |')
    return '\n'.join(lines)

def run():
    with stage('report'):
        primary=read(OUT/'comparisons/primary.json');cost=read(OUT/'scores/C-practical-cost.json');c=contract()
        point=pd.read_parquet(OUT/'scores/pooled.parquet');targets=pd.read_parquet(OUT/'scores/targets.parquet')
        new=pd.concat([pd.read_parquet(OUT/'manifests'/(p+'-endpoints.parquet')) for p in ['P2','P3']])
        show=point.set_index('policy_id').loc[[PRIMARY,*REFERENCES],['F1_U','F1_C','F1_all','CE_U','Brier_U','worst_target_F1_U']].reset_index()
        for k in list(show)[1:]:show[k]=show[k].map(lambda v:f'{v:.6f}')
        contrast=pd.DataFrame([dict(reference=z['reference'],delta_F1_U_pp=f"{100*z['delta_F1_U']:+.4f}",family_CI_pp=f"[{100*z['CI_family'][0]:+.4f}, {100*z['CI_family'][1]:+.4f}]",delta_CE_U=f"{z['delta_CE_U']:+.6f}",delta_Brier_U=f"{z['delta_Brier_U']:+.6f}") for z in primary['comparisons']])
        lines=['# RA1 v1完整实验报告','', '日期：2026-10-18。固定主候选：P-U50（rho_C=0、rho_U=.5）。',
          '', '## 1. 问题与实现', '',
          '保持96维访问级表示、历史P/G全仿射映射、CORAL、共同post尺度、StrongPost分类t与JA2来源共同eta。只改变辅助槽C/U的视图损失质量分配。完整96→6 LR从零重新拟合；推理只有冻结标准化与线性分类器，不接收pre或C/U身份。',
          '', '## 2. 数据、规模与权限','',
          '四TCP部署、六业务、30个全局内容，每内容每部署4次访问，共480次不同访问。五折×四目标×三遮蔽=60外层角色；每角色352次真实训练访问、24次H访问。辅助视图不是新增访问。39管线共2340逻辑端点、1920新LR、420历史别名；另有1个合成与2个结构重复核验，共1923次新拟合。无新映射/尺度/CORAL/神经训练。',
          '', 'H-post在全部模型封存后读取；H标签在全部56160条预测封存后读取。实际目标U训练数值、H-pre、PCAP不读取。56160是角色/政策暴露，不是独立样本。',
          '', '## 3. 配置','',
          'm={.1,.25,.5}；SYM=(m,m)、UPR=(0,2m)、CPR=(2m,0)。来源P/G/RawPre/RawPost；另有S及P/G-full。每类CE质量1/6、源post/辅助/目标C槽各1/3；C/U辅助各1/6。主候选映射总质量1/12，P-small为1/30。',
          '', 'CUDA float64，原v4 Cholesky预条件化与原坐标梯度感知LBFGS，max_iter=2000/max_eval=10000。CE按样本质量直接求和；L2=.0005*(1+t)||W||²，bias不惩罚。原梯度≤1e-5、目标/梯度重放误差<1e-10。无新比例/正则选择、温度、概率融合、投影或回退。',
          '', '## 4. 主要结果','',md(show),'',
          '## 5. 六项预定主比较','',md(contrast),'',
          '差值为新减旧；F1正向有利，CE/Brier负向有利。10000次业务分层共享内容簇bootstrap，seed=20261017，六比较Bonferroni边际覆盖99.1666667%，普通95%同时保存在机器表。先合并五折完整六类CM，再取U/C类F1并对部署/遮蔽等权。不是平均小折F1，也不是仅用真实U行构造二分类。',
          '', '## 6. C实践代价','',f"总体Delta F1_C={100*cost['delta_F1_C']:+.4f}个百分点；总体1pp筛查：{cost['overall_pass']}；各部署2pp筛查：{cost['each_deployment_pass']}。",'',
          md(pd.DataFrame([dict(deployment=p,delta_F1_C_pp=f'{100*v:+.4f}') for p,v in cost['per_deployment'].items()])),
          '', '这些是完整外层实践筛查，不是统计非劣效证明，不用于H后回退。',
          '', '## 7. 全政策与分项','',
          '全部39政策的总体表、逐部署、逐遮蔽、逐业务精度/召回、内容表与6×6矩阵分别保存在scores目录；相同剂量UPR/SYM/CPR、三强度曲线与P-U100对P-full的比较在comparisons/descriptive.json。它们为解释性结果，不将最高点重选为主候选。',
          '', 'error-transitions.parquet保留逐访问修复/新错/共同错误及C→U/U→C流向；probability-contributions.parquet按共同正确/修复/新错/共同错误拆解CE/Brier，并独立验证各贡献加和复现总体差。',
          '', '## 8. 计算量与工程验收','',
          f"新科学拟合1920；附加拟合3；历史复用420。科学solver-seconds={new.seconds.sum():.3f}，中位数={new.seconds.median():.3f}，最大={new.seconds.max():.3f}。活动预算上限8小时，活动台账记录阶段区间并集，区别于累计solver-seconds。最终完整活动耗时见completion.json（报告/复核也计入）。",
          '', f"环境：{c['environment']['torch']} / CUDA {c['environment']['cuda']} / {c['environment']['gpu']}。全部新拟合与推理使用CUDA float64，未改变原后端算法。48模型工程先导包含于1920，未读取H或按局部业务成绩放行。",
          '', '## 9. 结论边界','',
          '主候选相对P-small回答增强已有方案；相对P-SYM25回答同总量下角色分配；相对G、RawPre、RawPost分别界定精确管线、额外入口资源与减少CORAL/增加源post曝光解释。各项单独报告，不能用胜P-full替代胜P-small，也不要求六项全正才承认某个局部结论。',
          '', '本轮未证明协议语义不变、合法TCP生成、在线无索引分段、外部新日期/新节点泛化；历史H已经反复研究，区间条件于固定模型与相同30内容。目标C真实槽固定不保证C边界不变。任何次要政策最高点不升级为新主方法。',
          '', '## 10. 文件索引','',
          '- 合同/来源：manifests/contract.json、source-bindings.parquet、role-membership.parquet。',
          '- 质量：weights逐逻辑行台账、manifests/weight-ledger.parquet。',
          '- 数值：audits/P1-complete.json、all-endpoint-original-coordinate.parquet、fit-logs。',
          '- 预测：predictions/visits.parquet及complete.json。',
          '- 指标/区间：scores、comparisons/primary.json与bootstrap.npz。',
          '- 预算/终态：cost-ledger.json、verification.json、completion.json。','']
        textfile(DOC/'complete-report.md','\n'.join(lines))
        # Standard scientific plots, no new model or data extraction.
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        fig,axes=plt.subplots(2,2,figsize=(11,8),sharex=True)
        pts=point.set_index('policy_id')
        for ax,source in zip(axes.flat,['P','G','RawPre','RawPost']):
            for alloc in ['SYM','UPR','CPR']:
                ax.plot([.1,.25,.5],[pts.loc[f'{source}__m{int(m*100):03d}__{alloc}','F1_U'] for m in [.1,.25,.5]],marker='o',label=alloc)
            ax.axhline(pts.loc['P__m010__SYM','F1_U'],color='k',ls='--',lw=1,label='P-small');ax.set_title(source);ax.set_xlabel('Mean auxiliary replacement mass');ax.set_ylabel('F1 U');ax.legend(fontsize=8)
        fig.tight_layout();fig.savefig(writable(DOC/'figures/policy-curves.png'),dpi=160);plt.close(fig)
        write(OUT/'results-summary.json',dict(primary=primary['comparisons'],C_cost=cost,selected_after_H=False))
