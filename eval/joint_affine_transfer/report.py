"""Evidence-bound report generation after full verification."""
from common import *

def table(d,columns):
    lines=['| '+' | '.join(columns)+' |','| '+' | '.join(['---']*len(columns))+' |']
    for r in d[columns].to_dict('records'):
        lines.append('| '+' | '.join(f'{r[k]:.6f}' if isinstance(r[k],float) else str(r[k]) for k in columns)+' |')
    return '\n'.join(lines)

def status():
    env=read(OUT/'manifests/environment.json');audit=read(OUT/'observability/audit.json')
    value=['# 联合仿射迁移实施状态','',
        '已完成基线检查、96维重放、角色与C包准备、机制资格及有界记录解析。尚无本轮正式业务成绩。',
        '',f"环境为Pytorch312、PyTorch {env['torch']}、CUDA {env['cuda']}，{env['gpu']}；所有拟合和推理要求CUDA float64。",
        '',f"有限解析登记16访问32对；实际读取{audit['unique_capture_files_read']}个PCAP，扫描{audit['scan_bytes']/1024**3:.3f} GiB，保存{audit['record_rows']}条语法记录。",
        '', '记录语法不等于initial/relay语义。没有新增分类输入，SS chunk及VMess内部状态仍保留不可识别界限。',
        '', '三新臂为JA0逐块真配、JA1联合真配、JA2联合匿名组。匿名组保留所有入口访问方差，仅删除同次对应。',
        '', '固定15角色先导包含720分类器和180映射，计入34740正式分类器和8820映射任务。先导仅验数值与权限，不按F1筛选。',
        '', '契约在先导前封存，通过先导及两次确定性重放后才登记正式推广门。任何封存后的数值失败停止，不改科学候选。',
        '', '运行脚本、科学契约和进度位于新目录；第四版结果只读保留。最终评分与完整报告由runner在预测封存和独立验收后生成。']
    textfile(DOC/'implementation-status.md','\n'.join(value)+'\n')

def run():
    c=start('report');v=read(OUT/'verification.json');require(v['passed'],'Verification required')
    score=pd.read_parquet(OUT/'scores/pooled.parquet');targets=pd.read_parquet(OUT/'scores/targets.parquet')
    scenes=pd.read_parquet(OUT/'scores/scenarios.parquet');classes=pd.read_parquet(OUT/'scores/classes.parquet')
    result=read(OUT/'comparisons/primary.json');audit=read(OUT/'observability/audit.json')
    lines=['# 协议机制资格与联合仿射业务迁移完整报告','',
        '本轮完成固定四部署、六业务与全局未见内容的仿射适配对照。机制资格审计与业务增量分开判断，没有新增机制特征、神经网络或流量采集。',
        '',f"完整业务增量判定：{result['full_business_claim_passed']}；跨块结构增量判定：{result['structure_claim_passed']}；辅助业务实践筛查：{result['safety_screen_passed']}。",
        '', '## 数据与权限','',
        '沿用Extend的23566排他TCP对、480访问、30个共同内容、五个全局内容折。每业务5内容、每内容4重复。AnyTLS和Hy2没有进入本轮同粒度分类。',
        '', '60外层场景分别使用288源访问、64目标C访问；32目标U训练访问的两侧均禁止使用。24个留出访问仅post进入分类。720源内角色负责选择，实际目标不参与选参。',
        '', '## 机制资格','',
        f"固定样本登记16访问、32对。读取{audit['unique_capture_files_read']}个PCAP，哈希和解码共扫描{audit['scan_bytes']/1024**3:.3f} GiB，保存{audit['record_rows']}条记录。剩余登记样本按文件预算保留未解析状态。",
        '', '记录边界和外层类型是语法观测，不是initial/relay或一一对应语义。SS实际chunk、VMess内部块、协商模式与阶段仍有不可识别范围。当前VLESS无Vision，不移植旧Vision结论。',
        '', '## 方法与数值政策','',
        'JA0为同次访问的逐块仿射，JA1为96维联合真配仿射，JA2为同内容匿名全donor平方目标。JA2等价于逐入口拟合出口内容中心加目标方差常数，保留所有入口Sxx，不将入口也取均值。',
        '', '共同目标为weighted MSE/96加eta*tau*矩阵到I的平方距离/96，bias不正则化；eta为0.1、1、10、100，tau为C-pre中心协方差trace/96。共用真实source-post加C-post缩放，常数维scale置1。',
        '', 'JA0参数1020，JA1/JA2参数9312；联合和逐块容量不同。仿射输出是适配向量，不截负、归一化或声称合法流量。强收缩趋向恒等加C均值平移，不严格等同CT1。',
        '', '辅助槽与原实验相同，每源一视图；源post主槽、目标C-post槽及类别质量不变。96到6逻辑回归为582参数，原带权CE与W的L2、未惩罚bias不变，t为0、0.25、1、4。',
        '', 'CUDA float64贯穿全部拟合与推理。LR max_iter为2000、max_eval为10000，原坐标梯度门1e-5；映射梯度门1e-8；目标与梯度重放门1e-10。先导、重放、完整矩阵共用政策。',
        '',f"独立验收34740个正式分类器和8820个映射任务；最大分类梯度{v['original_classifier_gradient_max']:.12g}，最大映射梯度{v['mapping_gradient_max']:.12g}。720先导已计入正式数，两次重放单列。",
        '', '新方法每臂有16个源内组合，旧StrongPost复用其原选择，搜索预算不同须保留。不会按新测试成绩重新选择旧基线。',
        '', '## 总体结果','',table(score,['arm','F1_uncovered','F1_all','F1_aux','accuracy','CE_nats','Brier','worst_target_uncovered']),
        '', '## 四项主比较','', '| 比较 | 未覆盖F1差 | 98.75%家族区间 | 正向增量 |','| --- | ---: | --- | --- |']
    for r in result['comparisons']:
        lines.append(f"| JA1减{r['reference']} | {r['delta_F1_uncovered']:.6f} | {r['CI_98_75']} | {r['positive_increment']} |")
    lines += ['', '四项共享10000次业务分层内容bootstrap，seed为20261007，同一内容权重用于所有部署、重复、方法及业务组。区间条件于固定模型，不是外部验证或完整重训练不确定性。前三项加实践筛查决定完整业务增量，第四项回答跨块结构问题。',
        '', '## 逐部署结果','',table(targets,['arm','target','F1_uncovered','F1_all','F1_aux','CE_nats','Brier']),
        '', '## 业务组与逐类别','',
        'G0未覆盖GitHub仓库和YouTube搜索，G1未覆盖Bing搜索和Wikipedia文章，G2未覆盖MDN文档和YouTube播放。F1均从完整六分类混淆矩阵计算，不简化成二分类。',
        '', table(scenes,['arm','target','group','F1_uncovered','F1_aux','F1_all']),
        '', '各业务在自己未覆盖组的分项如下；更细的60外层场景保存在scores/outer-folds.parquet。',
        '', table(classes[classes.uncovered].sort_values(['arm','target','label_index']),['arm','target','label','F1','support','false_positive','false_negative'])]
    recovery=pd.read_parquet(OUT/'diagnostics/recovery.parquet');recovery['partition']=np.where(recovery.inner.isna(),'outer-heldout','source-inner-heldout')
    rr=recovery.groupby(['arm','calibration','partition']).MSE.mean().reset_index()
    shape=pd.read_parquet(OUT/'diagnostics/source-view-shape.parquet').groupby('arm').mean(numeric_only=True).reset_index()
    flips=pd.read_parquet(OUT/'scores/error-flips.parquet');ff=flips[flips.uncovered].groupby('reference')[['fixed_error','new_error']].sum().reset_index()
    lines += ['', '## 恢复与决策变化','',table(rr,['arm','calibration','partition','MSE']),
        '', '恢复误差是封存后的forward pre到post诊断；测试pre未进入分类、可靠性、选参或重训。系数范数不是协议因果贡献。',
        '',table(ff,['reference','fixed_error','new_error']),
        '', '修复与新增错误按同一留出访问比较；F1差不能直接由净修复个数推算。',
        '', '## 适配向量形状','',table(shape,['arm','negative_fraction','maximum_negative','max_block_sum_error','input_outside_C_coordinate_fraction']),
        '', '这些是输出与外推诊断，不据此剔除、投影、截负或修改主队列。',
        '', '## 结论范围与停止决定','',
        '联合仿射可以检验有限访问级跨块关系，仍只输出条件均值。相对旧CT4的差异同时涉及估计器及粒度，不单独归因协议机制。当前没有加入半机制模块，不能由本轮结果宣称机制约束已带来增量。',
        '', '如果完整业务增量未通过，就保留负向与例外，不扩eta、损失或网络。若通过，仅适用于本轮配置、队列与校准权限，不自动推广真实DIRECT、未见节点或日期。',
        '', '登记实体整体同折不等于全历史TCP epoch已普遍证明；离线关联队列也不等于无索引、无pre的完整外部攻击输入已经验证。',
        '', '后续半机制方法须基于资格证据另行确认，并给同输入通用模型及强post方法公平资源。本轮到此冻结。']
    textfile(DOC/'formal-report.md','\n'.join(lines)+'\n')
    write(OUT/'manifests/report-manifest.json',{'report_sha256':sha(DOC/'formal-report.md'),'verification_sha256':sha(OUT/'verification.json')})
    finish('report',full_business_claim_passed=result['full_business_claim_passed'])

if __name__=='__main__':status() if len(sys.argv)>1 and sys.argv[1]=='status' else run()
