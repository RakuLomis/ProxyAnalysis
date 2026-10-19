"""Detailed source-only closeout; no new fits, no actual H/U evaluation."""
from common import *

def md(df):
    def cell(x):
        if isinstance(x,(float,np.floating)):return f'{x:.6f}' if np.isfinite(x) else '未定义'
        return str(x).replace('|','\\|')
    return '\n'.join(['| '+' | '.join(map(str,df.columns))+' |','| '+' | '.join(['---']*len(df.columns))+' |']+
        ['| '+' | '.join(cell(x) for x in r)+' |' for r in df.itertuples(index=False,name=None)])

def run():
    configure('score');barrier('scores-complete.json');root=OUT/'scores';readt=lambda n:pd.read_parquet(root/(n+'.parquet'))
    pooled=readt('pooled');dep=readt('deployments');classes=readt('classes');flips=readt('error-flips');gen=readt('generation-errors-labeled');mom=readt('generation-conditional-moments')
    primary=read(root/'primary.json');screen=read(root/'progression-screen.json');audit=pd.read_parquet(OUT/'manifests/P0-audit.parquet');point=pooled.set_index('pipeline')
    delta=float(point.loc['DA-P','F1_U']-point.loc['B0','F1_U']);dg=float(point.loc['DA-P','F1_U']-point.loc['DA-G','F1_U'])
    lines=['# 前向决策空间漂移精炼源内先导完整报告','','日期：2026-10-17。DA-FGAN1-Pilot v1。',
        '',f'程序完整完成；本轮只有固定48个源内任务，没有实际H/U评价。DA-P相对B0的ΔF1_U={100*delta:.6f}个百分点，'
        f'相对DA-G为{100*dg:.6f}个百分点。预定源内推进屏通过={screen["passed"]}。',
        '', '## 1 研究问题与边界','',
        '本轮只调整原P-small的1/30映射槽：冻结原JA1全仿射、原B0尺度及正则t，训练96→8→96残差；最终仍是只读取post的96→6线性分类器。'
        '没有逆向pre恢复推理、没有概率融合、没有神经判别器或GAN极小极大训练；决策空间/有限矩是具体训练目标，不是协议语义或类间拓扑不变性的证明。',
        '', '## 2 数据与权限','',
        '48任务=outer f0×四内折×四组织role_target×三业务遮蔽。每任务两个源144访问＋伪目标C48访问，共192不同训练访问；query24访问。'
        '跨任务合计24内容、384次不同query访问；5760逻辑预测包含五管线，不是5760个独立样本。训练18内容与query六内容无交叉，两侧/重复/内部flow随内容分折。',
        '', 'role_target用于组织，并不是查询部署：SS→VLESS、VLESS→Trojan、Trojan→VMess、VMess→SS。实际role_target被排除。'
        '本轮批准的源内query-pre仅在全部模型及分类post预测封存后读取，用于离线诊断；没有进入拟合、尺度、checkpoint或候选选择，实际目标H/U保持禁读。',
        '', 'G进程只接触独立训练边际与匿名同内容中心；与P共享原P-small真配锚点。因此P−G检验共同P-small之上的新增精确监督，不是整系统有无精确关联。',
        '', '六类为Bing搜索、MDN文档、GitHub仓库、Wikipedia文章、YouTube搜索、YouTube播放；G0遮蔽GitHub/YouTube搜索，G1遮蔽Bing/Wikipedia，G2遮蔽MDN/YouTube播放。',
        '', '## 3 四槽、尺度、零起点与数值基线','',
        '源post144行质量1/3、CORAL144行质量0.3、mapped-pre144行质量1/30、目标C-post48行质量1/3。全部槽质量合计1，每类1/6；带权CE不再除行数。'
        '原mapped-pre覆盖六类，而非只有U。修正只在该槽施加；其余三槽、标签、顺序、质量精确保留。',
        '', 'ZERO直接引用原B0，材料逐位相同；不以新拟合制造“模型逐位相同”。B0-R是同目标新数值求解对照，独立列出。'
        '原B0/eta/t已由历史研究选择，源内内容也被多次研究，本次不是新的外部盲测。',
        '', '## 4 模型与固定配置','',
        'Q_feat由类别中心化B0权重SVD提取，秩≤5，不与6×5类别基Q_class混用。'
        f'48角色有效秩分布：{audit["rank"].value_counts().sort_index().to_dict()}。'
        f'正交误差最大{audit.orthogonal_error.max():.3e}；权重重构误差最大{audit.weight_reconstruction_error.max():.3e}。',
        '', '生成器1544参数：U1随机N(0,1/96)，d1=0，U2=0；seed20261017。'
        '三臂全部2000步Adam，lr0.0003、betas(0.9,0.999)、eps1e−8、clip范数5。'
        '没有网格、早停或checkpoint择优。模型全CUDA float64，禁AMP/TF32；最多32独立模型、8 streams、CUDA Graph，凸头4并发。',
        '', 'J=监督误差/d＋业务条件协方差差/d²＋源侧六类残差中心关系项＋0.1dev＋1e−4(||U1||²+||U2||²)。'
        'DA-P用真配Q空间目标；DA-G用同内容post中心与真实post边际协方差；Full-P仅将监督及协方差改为全96空间，其余项一致。'
        '类中心项是相对旧映射的软先验，不保证真实业务不变，本轮没有其独立消融。',
        '', '最终LR：CE_mass＋0.0005(1+t)||W||²，bias不惩罚，统一零初始化；原W/c梯度≤1e−5，独立重放≤1e−10，迭代严格<2000、函数评价严格<10000。'
        '没有增加模型容量到H推理接口，亦没有读取任何H。',
        '', '## 5 全部源内结果','',md(pooled),
        '', 'F1由完整六类CM得到，保留其他类别造成的FP；四内折先合并，再按四query部署×三遮蔽组等权。'
        '不是逐折F1平均，不是U二分类。CE越低越好，Brier为六类概率平方误差之和。',
        '', '## 6 三项预定主比较','']
    cs=[]
    for c in primary['comparisons']:
        cs.append(dict(reference=c['reference'],delta_F1_U_pp=100*c['delta_F1_U'],CI95_pp=[100*x for x in c['CI95']],
            family_CI_pp=[100*x for x in c['family_CI']],family_positive=c['positive_family_increment'],delta_CE_U=c['delta_CE_U'],delta_Brier_U=c['delta_Brier_U']))
    lines += [md(pd.DataFrame(cs)),'','10000次六业务分层共享全局内容簇bootstrap，seed20261017；每业务四内容抽四。'
        '三比较Bonferroni边际98.333333%区间，另报95%。独立NumPy重建与CUDA结果误差见最终验证。'
        '区间条件于固定模型，不能消除历史数据反复开发；本轮没有选参，亦未据结果删任务。',
        '', '## 7 逐查询部署与业务','',md(dep),'',md(classes.groupby(['pipeline','business','scope']).F1.mean().reset_index()),
        '', '逐业务表按其作为U/C的上下文分开，不能混作同一业务单一分数。部署分项为描述性结果，不另外制造逐部署显著性家族。',
        '', '## 8 C实践代价与推进判定','',
        f'总体C ΔF1={100*screen["overall_C_delta"]:.6f}个百分点，总体1个百分点门通过={screen["overall_C_pass"]}。',
        '',md(pd.DataFrame(screen['deployments'])),'',
        '预定推进屏同时要求P相对B0/G的U-F1点估计为正、U-CE相对两者不恶化及C总体1pp/各部署2pp筛查。'
        f'结果passed={screen["passed"]}。它只是是否值得申请完整实验的探索性筛查，不是确认性成功或统计非劣效证明。',
        '', '## 9 错误修复、新增错误及概率贡献','']
    fs=flips.groupby(['reference','scope','flip']).agg(n=('correct','size'),delta_CE=('delta_CE','mean'),delta_Brier=('delta_Brier','mean')).reset_index()
    fs['CE_contribution']=fs.n*fs.delta_CE/fs.groupby(['reference','scope']).n.transform('sum')
    lines += [md(fs),'','每参照U384、C768条角色暴露行，不是新增独立内容。修复与新增计数不是宏F1；共同正确/共同错误的概率变化也影响CE。',
        '', '## 10 源内留出生成诊断','']
    gen['scope']=['U' if y in MASKS[lookup(rid)['group']] else 'C' for y,rid in zip(gen.y,gen.role_id)]
    gm=gen.groupby(['pipeline','scope'])[['Q_MSE','relative_logit_MSE','std_MSE','raw_MSE']].mean().reset_index()
    lines += [md(gm),'',md(mom.groupby(['pipeline','scope'])[['mean_error','covariance_error']].mean().reset_index()),
        '', 'B0在本节代表原前向映射的生成输出，不是用分类器概率当恢复结果。Q误差与相对logit误差权重不同；'
        'raw误差与std误差亦不可混同。诊断只使用新授权的源内留出pre；不是实际H恢复诊断。'
        '前两阶矩比较不足以证明完整条件分布逼真、协议语义或标签保持。',
        '', '## 11 生成值的必要合法性边界','']
    legal=pd.read_parquet(OUT/'diagnostics/legality.parquet');ls=legal.groupby('pipeline').agg(negative_fraction=('negative_fraction','mean'),minimum=('minimum','min'),maximum=('maximum','max'),block_mass_error_max=('mass_error_max','max')).reset_index()
    lines += [md(ls),'','原仿射和新视图均按原值报告，没有裁剪、投影或重新归一化。本轮生成的是训练协变量，不是合法TCP/协议流量生成器。'
        '十个raw块均值在合法直方图中是常量，未被伪装成协议风格判别维度。',
        '', '## 12 训练轨迹与目标取舍','']
    traces=[];qualities=[]
    for r in roles():
        for arm in ARMS:
            t=read(modelroot(r,arm)/'trace.json')['steps'];a,b=t[0],t[-1]
            traces.append(dict(pipeline=arm,J0=a['objective'],Jend=b['objective'],decreased=b['objective']<=a['objective'],
                C_Q0=a['C_Q_error'],C_Qend=b['C_Q_error'],C_std0=a['C_std_error'],C_stdend=b['C_std_error'],
                residual_rms=b['source_residual_rms'],std_max=b['std_max'],clips=b['clip_count'],
                sup=b['parts'][0],cov=b['parts'][1],relation=b['parts'][2],dev_weighted=b['parts'][3],L2=b['parts'][4]))
        for arm in ['B0-R']+ARMS:
            q=read((OUT/'classifiers'/r['id']/(arm+'.pt')).with_suffix('.quality.json'));qualities.append(dict(pipeline=arm,accepted=q['accepted'],iterations=q['iterations'],evaluations=q['evaluations'],gradient=q['original_gradient_max'],objective_error=q['independent_objective_error'],gradient_error=q['independent_gradient_error']))
    tr=pd.DataFrame(traces);save(OUT/'scores/training-trace-summary.parquet',tr)
    lines += [md(tr.groupby('pipeline').mean(numeric_only=True).reset_index()),
        '', '训练C恢复目标的真配/组中心含义不同，不能按绝对大小排名。源内留出指标另表报告，不用训练损失代替泛化。'
        '2000步非凸路径没有被宣称全局最优；本轮没有根据梯度冲突更换损失。',
        '', '## 13 数值、来源与CUDA成本','']
    q=pd.DataFrame(qualities);qs=q.groupby('pipeline').agg(heads=('accepted','size'),accepted=('accepted','sum'),max_iter=('iterations','max'),max_eval=('evaluations','max'),max_gradient=('gradient','max'),max_objective_error=('objective_error','max'),max_gradient_error=('gradient_error','max')).reset_index()
    for k in ['max_gradient','max_objective_error','max_gradient_error']:qs[k]=qs[k].map(lambda x:f'{x:.8e}')
    lines += [md(qs)]
    v=read(OUT/'tests/final-verification.json');f=read(OUT/'manifests/P1-forecast.json');b=read(OUT/'budget.json')
    lines += ['',f'正式生成144条路径、最终LR192个；B0/ZERO均为别名。工程重放另计。'
        f'P1保守预计总活动{f["conservative_total_seconds"]/3600:.4f}小时，门2.4小时；'
        f'截至报告生成活动约{(time.time()-b["start_unix"])/3600:.4f}小时，保护3小时。最终精确累计以completion.json为准。',
        '',f'独立CM最大差{v["metric_max_error"]:.3e}，独立bootstrap最大差{v["bootstrap_max_error"]:.3e}；'
        '32/8 CUDA重放、权限负例及数学测试见tests/engineering.parquet。'
        '无实际H/U读取，源内query-pre在predictions-complete之后开放。',
        '',md(pd.DataFrame(b['items'])[['stage','seconds']]),
        '', '## 14 结项与后续边界','',
        ('预定源内筛查通过，可以申请另立完整720/60评价；尚不能宣称真实H分类增强。' if screen['passed'] else
         '预定源内筛查未通过，按合同停止当前配置，不自动启动完整H、不扩权重或步数搜索。'),
        '', '整体效果、精确监督增量、决策空间聚焦、类中心先验的独立贡献必须分开。'
        '第一版无类中心项独立消融；即使结果正向也不能宣称物理不变性成立。'
        '若P未优于Full-P，不能说全空间方向均无用；若P未优于G，也不能把更多源pre材料的收益归因精确身份。',
        '', '## 15 追溯','',
        f'[实施计划]({PLAN.as_posix()})；[代码]({(CODE/"driver.py").as_posix()})；'
        f'[运行目录]({OUT.as_posix()})。原Full NER1、ST1、JA、P-small模型与原结果未修改。']
    path=writable(DOC/'pilot-results.md');path.write_text('\n\n'.join(lines)+'\n',encoding='utf-8')
    seal(OUT/'manifests/report-complete.json',[path,OUT/'scores/training-trace-summary.parquet'],actual_H_U_read=False)
    progress('report_complete',report=rel(path),progression_screen=screen['passed'])

if __name__=='__main__':run()
