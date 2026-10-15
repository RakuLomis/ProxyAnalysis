"""Reproducible complete J report, with repair lineage and fixed stopping rule."""
import common
from common import *


def main():
    out = OUT/'repair-v1'; common.OUT = out
    authorize(); assert read(out/'independent-verification.json')['passed']
    a = pd.read_parquet(out/'aggregate-metrics.parquet')
    c = pd.read_parquet(out/'contrasts.parquet')
    per = pd.read_parquet(out/'per-protocol-seed-metrics.parquet')
    cls = pd.read_parquet(out/'per-class-metrics.parquet')
    er = pd.read_parquet(out/'error-transitions.parquet')
    conf = pd.read_parquet(out/'confusion-matrices.parquet')
    card = read(out/'contract.json'); audit = read(out/'independent-verification.json')
    replay = read(out/'cuda-replay.json'); baseline = read(out/'baseline-reproduction.json')
    primary = c[c.primary].copy(); primary['supported_positive'] = (primary.delta > 0) & (primary.adjusted_low > 0)
    count = int(primary.supported_positive.sum()); point = a.set_index('arm')
    lookup = primary.set_index('contrast'); p = lambda ref: bool(lookup.loc['J4-'+ref, 'supported_positive'])
    interpretations = []
    for ref, question in [('J0', '相对充分post监督'), ('J7', '相对普通post任务一致性'),
                          ('J6', '显式transfer相对条件双侧CE'), ('J2', '机制条件相对无条件任务配对'),
                          ('J3', '机制中心相对通用中心'), ('J5', '精确对应管线相对匿名组管线')]:
        row = lookup.loc['J4-'+ref]
        if p(ref): conclusion = '本固定队列与配方下获得正向业务增量证据'
        elif row.adjusted_high < 0: conclusion = '校正区间全为负，主候选表现更差'
        else: conclusion = '正向增量未建立；区间跨零不等于等效'
        interpretations.append({'问题': question, '比较': 'J4-'+ref, '判断': conclusion})
    text = '# Extend post 单侧任务感知配对训练完整结果\n\n'
    text += ('日期：2026年10月4日。本报告覆盖固定J0至J7、五折、三seed的训练与业务评分，'
             '以及用户批准的15个J0数值修复重拟合。旧E1与第一次失败版本保留，没有重做探针、检索、追加权重或启动E2。\n\n')
    text += (f'唯一主候选J4的部署等权macro-F1为{point.loc["J4", "F1"]:.6f}；'
             f'预定六项比较中{count}项获得家族校正后正向区间。'
             '下面逐项解释，而不是按最好点估计更换主方法。\n\n')
    text += '## 数据观测和划分\n\n'
    text += ('固定600访问、30全局内容、六业务、五已见部署SS/VLESS/Trojan/VMess/AnyTLS，'
             '每内容每部署四次重复1至4。沿用五折全局内容留出，训练480、测试120；'
             '同内容全部部署、重复、两侧与内部连接整体同折。不是0914/旧0916/64URL任务。\n\n'
             '输入只有W_up/W_down/P_up/P_down/R_up/R_down。W为窗口正传输载荷字节含重传，'
             'P为正载荷事件，R为窗口方向段，不是stream FR、TCP去重新字节段或记录时间FR。'
             'MAC、IP、端口、SNI、domain字符串、协议onehot、内容和重复均不是网络数值输入。'
             '标签、内容与部署元数据只服务训练授权、采样、划分及评分。\n\n')
    text += '\n'.join('- '+v for v in card['classes'])+'\n\n'
    text += ('资格继续沿用P2/P3物理身份注册，并保留五例未见SYN与历史P2预检限制；'
             '复用审核不是全量PCAP重新验证，更不是绝对无flow泄漏的数学证明。'
             '本批Hy2存在登记carrier跨内容/跨折及未映射访问，未进入此共同分类队列。\n\n')
    text += '## 方法和任务权限\n\n'
    text += ('E为6→64→32，隐藏ReLU、最终线性；H为32→32→6，隐藏ReLU。'
             'E有2528参数，H有1254，部署共3782。训练条件A为零初始化无偏置6→32，另192参数；推理删除。'
             'pre与post分别采用训练侧log1p及均值标准差。条件是冻结phi(decoded raw_center)−phi(pre)经训练尺度处理，'
             '八个pre辅助统计只参与条件预测。300中心、7200条件行复用18训练内容/6查询内容交叉拟合，不使用真实query post作条件。\n\n'
             '两分支共享E/H，post logits为H(E(post))，辅助logits为H(E(pre)+A m)。'
             '目标为0.5 post CE＋0.5 aux CE＋0.5 T² KL(stopgrad(aux softmax/T) ∥ post softmax/T)'
             '＋5e−5权重平方和，T=2，bias不惩罚。J0/J1/J6关闭KL。'
             'KL的直接梯度只经post路径；共享参数之后仍更新辅助分支，不是独立冻结教师。'
             '新方案显式使用业务标签，是任务感知训练，不是无标签SSL，也不把中心交叉拟合冒充业务OOF教师。\n\n')
    matrix = pd.DataFrame([
        ['J0', 'post单CE，原复制CE代数化简', '无', '充分post监督'],
        ['J1', 'pre业务CE，无条件', '无', '额外pre监督'],
        ['J2', 'pre业务CE，无条件', '真配决策KL', '无条件任务配对'],
        ['J3', 'pre业务CE，D1_pair', '真配决策KL', '通用中心'],
        ['J4', 'pre业务CE，D2_pair', '真配决策KL', '唯一主候选'],
        ['J5', '匿名组pre业务CE，D2_group', '四pre平均概率到组post', '较粗对应'],
        ['J6', 'pre业务CE，D2_pair', '无', '条件双侧CE'],
        ['J7', 'masked post业务CE', 'masked到clean post KL', '普通post一致性']],
        columns=['臂', '辅助分支', '约束', '用途'])
    text += matrix.to_markdown(index=False)+'\n\n'
    text += ('J5组是同内容同部署的四次访问；两侧独立排序，无共同session/repetition。'
             '平均概率而非logits，四pre各编码一次，不把16组合当独立访问。'
             'J4−J5比较整条精确对应管线，包含中心和决策目标的关系，不能独立定位末端身份的因果贡献。'
             'J7只遮一个标准化数值坐标为0；这是学习扰动，不是合法代理流量。\n\n')
    text += '## 优化配置和实际预算\n\n'
    text += ('三seed为20260918/19/20。各模型固定2000步；第1000步保留权重、重置Adam，'
             '重放同一1000步监督采样。每批120访问，各部署各业务一个内容的四重复。'
             'Adam lr0.001、betas0.9/0.999、eps1e−8、foreach=False、optimizer weight_decay=0；显式L2如前。'
             '无早停、checkpoint选择、BN、dropout、AMP、TF32、温度或权重搜索。\n\n'
             'Pytorch312，PyTorch2.5.1/CUDA12.4，RTX4060Ti。全部训练、数值条件核验、编码与推理CUDA，'
             '网络float32，条件核验float64；元数据与bootstrap使用CPU。\n\n'
             '第一次120正式模型加批准的15个J0修复，共实际执行135个2000步模型；最终评分使用120，'
             '原15个J0仅保留为失败实现记录。另8个20步工程烟测，不进入初始化。'
             '并行参数batch模型互不共享权重或优化器状态，不构成集成。\n\n')
    text += (f'第一次拟合加修复的合计训练计时为{audit["summed_fit_seconds"]:.3f}秒，'
             '这是各折记录之和，不是完整流水线墙钟时间。\n\n')
    resources = pd.DataFrame([
        ['J0', 'post＋标签', 2000, 500, 0, '复制CE代数化简，单post前向'],
        ['J1/J2', 'pre/post＋既有标签', 2000, 500, 500, '无条件'],
        ['J3/J4/J6', '同一双侧资源＋合法条件', 2000, 500, 500, '条件由训练侧预测'],
        ['J5', '匿名组双侧资源＋组条件', 2000, 500, 500, '无精确身份'],
        ['J7', 'post＋标签', 2000, 1000, 0, 'clean和masked两次post前向']],
        columns=['臂', '训练资源', '更新步', '每访问post编码曝光', '每访问pre编码曝光', '说明'])
    text += resources.to_markdown(index=False)+'\n\n'
    text += '## 数值修复与不可改写的失败记录\n\n'
    text += ('第一次J0对旧B0L的最大概率差为0.30322763323783875，1800条中19个决策不同；'
             '评分在门前停止。训练侧15组输入、初始化、采样和缩放器一致，'
             '初始重复CE与单CE梯度存在1.862645149230957e−9差异，后续损失轨迹偏离；'
             '第一实现的继续布局为24模型，旧B0L为3。该审计没有单独分解两个数值因素的贡献。\n\n'
             '用户批准追加15个J0之后，使用单CE旧求值路径，第一阶段24位置布局仅更新1/9/17三个位置，'
             '其他21个位置梯度为零、权重不变，属于计算填充而非新增学习器；第二阶段三个模型继续。'
             '修复15个模型前1000步损失与最终E/H哈希均精确复现旧B0L。'
             '训练验证先于业务评分，未按正确率选择旧/新模型。\n\n')
    text += (f'修复预测与旧B0L的最大概率差为{baseline["maximum_probability_difference"]:.12g}，'
             f'决策不同为{baseline["changed_decisions"]}；'
             f'120模型不同推理batch最大概率差{replay["maximum_probability_difference"]:.12g}，决策全部一致。'
             '1e−5门限未放宽。\n\n')
    text += '## 主要业务成绩\n\n'+a.to_markdown(index=False, floatfmt='.6f')+'\n\n'
    text += ('F1先逐seed、逐部署从完整六类OOF计算，再部署与seed等权平均；'
             'min/max seed为部署等权的逐seed范围；worst F1是每seed最差部署F1的均值。'
             '不先平均概率，不以混合访问总F1代替部署等权。CE为bits，Brier为六类概率平方误差和。\n\n')
    text += '## 六项主要比较与解释性比较\n\n'+c.to_markdown(index=False, floatfmt='.6f')+'\n\n'
    text += ('主要家族固定J4−J0/J7/J6/J2/J3/J5。10000次业务分层内容簇bootstrap，seed20260928，'
             '同内容所有部署、重复、seed和臂同步重采样。普通95%与六项Bonferroni分位'
             '0.05/12及1−0.05/12并报。固定模型区间不涵盖外部验证、独立重训或历史选择。'
             '三seed与四重复不是更多独立内容。\n\n')
    text += pd.DataFrame(interpretations).to_markdown(index=False)+'\n\n'
    text += '## 逐部署与逐seed\n\n'
    text += per.groupby(['arm', 'protocol']).F1.mean().unstack('arm').to_markdown(floatfmt='.6f')+'\n\n'
    text += per.groupby(['arm', 'seed']).F1.mean().unstack('seed').to_markdown(floatfmt='.6f')+'\n\n'
    text += '### 全部部署逐seed指标\n\n'+per.to_markdown(index=False, floatfmt='.6f')+'\n\n'
    text += '## 逐业务指标\n\n'
    summary = cls.groupby(['arm', 'class'])[['precision', 'recall', 'F1']].mean().reset_index()
    text += summary.to_markdown(index=False, floatfmt='.6f')+'\n\n'
    text += '### 部署业务分项\n\n'
    text += cls.groupby(['arm', 'protocol', 'class'])[['precision', 'recall', 'F1']].mean().reset_index().to_markdown(index=False, floatfmt='.6f')+'\n\n'
    text += '## 修复错误和新增错误\n\n'
    text += er.groupby('comparison')[['repaired', 'new_error']].sum().reset_index().to_markdown(index=False)+'\n\n'
    text += er.groupby(['comparison', 'protocol'])[['repaired', 'new_error']].sum().reset_index().to_markdown(index=False)+'\n\n'
    text += ('这些计数跨三seed的1800预测，不是1800独立访问。内容级台账另存content-error-transitions.parquet，'
             '不能据有利视频或协议重新选择目标。\n\n')
    text += '## 完整混淆矩阵\n\n'
    for arm in ARMS:
        text += '### '+arm+'\n\n'
        cm = conf[conf.arm.eq(arm)].groupby(['truth', 'guess'])['count'].sum().unstack().reindex(index=card['classes'], columns=card['classes']).fillna(0).astype(int)
        text += cm.to_markdown()+'\n\n'
    text += '## 工程审核与未验证范围\n\n'
    checks = read(out/'independent-score-check.json')
    text += (f'六项CUDA单元测试、170次权限拒绝、八臂20步烟测通过。'
             f'独立sklearn核算{checks["point_checks"]}个点值及{checks["draw_checks"]}个bootstrap值，'
             f'最大误差分别{checks["maximum_point_error"]:.12g}与{checks["maximum_draw_error"]:.12g}。'
             '修复版105个非J0模型权重逐位保持，原拟合和原预测哈希保留。\n\n'
             '正式模型仅接受六个post数值，额外字段被拒绝；拟合和推理没有读取测试pre或评分标签。'
             '准备过程已有历史业务元数据，不能说研究者从未接触测试标签。'
             '观测为离线索引辅助post，不是全自动被动分段。'
             '既有物理身份检查不排除环境可预测性，也不是对未登记实体的普遍无泄漏证明。\n\n'
             '结果仅针对五个已见Extend部署的未见内容任务，不证明未见协议、配置、日期、外部DIRECT或现场攻击。'
             '本批VLESS无REALITY/Vision，SS cipher已登记，VMess auto最终security与AnyTLS内部状态仍有边界。'
             '机制条件是经验先验，不是精确K、隐状态完整恢复或因果识别。\n\n'
             '本次没有新检索、冻结探针或更大头，没有减少业务标签；结果不应被解释为无标签配对SSL终于成功。'
             '旧B系列只有历史参照意义，新联合业务监督的标签曝光和路径不同。\n\n')
    text += '## 停止决定与产物\n\n'
    text += (f'固定主候选J4、全部八臂和六项家族已完成，正向通过{count}/6。'
             '本候选在此冻结，不自动追加lambda、温度、更多seed、分类头、检索诊断或E2。'
             '失败数值实现记录和业务结果都保留，不围绕某项差距修改主方法。\n\n'
             '代码在eval/post_anchored_paired_training；最终机器结果在outputs/post-anchored-paired-training-extend/'
             'run-01/repair-v1。包含最终预测、完整指标、混淆矩阵、内容错误台账、bootstrap索引、'
             '修复来源、模型检查点、纯post模型、CUDA回放与独立审核。plan和outputs保持Git忽略，本次没有推送远端。\n')
    DOC.mkdir(parents=True, exist_ok=True); report = DOC/'formal-results.md'; report.write_text(text, encoding='utf-8')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    figdir = out/'figures'; figdir.mkdir(exist_ok=True)
    fig, ax = plt.subplots(figsize=(9, 4.5)); order = a.set_index('arm').loc[ARMS]
    ax.bar(ARMS, order.F1, color=['#be4d25' if s == 'J4' else '#477c98' for s in ARMS])
    ax.set_ylabel('Deployment-equal macro-F1'); ax.set_ylim(0, 1); ax.set_title('Fixed J0-J7, post-only unseen-content evaluation')
    for i, row in enumerate(order.itertuples()): ax.text(i, row.F1+.01, f'{row.F1:.3f}', ha='center')
    fig.tight_layout(); fig.savefig(figdir/'business-comparison.png', dpi=180); plt.close(fig)
    fig, ax = plt.subplots(figsize=(9, 4.5)); pp = primary.reset_index(drop=True)
    for i, row in enumerate(pp.itertuples()):
        ax.plot([row.adjusted_low, row.adjusted_high], [i, i], color='#477c98', lw=3); ax.scatter(row.delta, i, color='#be4d25')
    ax.axvline(0, color='black', ls='--'); ax.set_yticks(range(len(pp)), pp.contrast); ax.invert_yaxis()
    ax.set_xlabel('Macro-F1 difference, family-adjusted content bootstrap'); fig.tight_layout()
    fig.savefig(figdir/'primary-contrasts.png', dpi=180); plt.close(fig)
    write(out/'stopping-decision.json', {'frozen': True, 'primary_positive': count, 'primary_total': 6,
          'primary_candidate': 'J4', 'automatic_search': False, 'E2_started': False, 'additional_fits_authorized': 15,
          'actual_full_length_fits': 135, 'comparison_model_count': 120})
    write(out/'report-manifest.json', {'complete': True, 'report_sha256': sha(report),
          'source_sha256': sha(Path(__file__)), 'prediction_sha256': sha(out/'oof.parquet'),
          'results_scope': 'seen five deployments, unseen content, task-aware joint training'})
    print('Full report saved:', report, '; positive primary contrasts:', count, '/6', flush=True)


if __name__ == '__main__': main()
