"""Detailed evidence-bound report; original JA failure state is not rewritten."""
from pathlib import Path
import json
import datetime as dt
import hashlib
import sys
ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'outputs/joint-affine-transfer-20261007/run-01'
DATA=RUN/'report-analysis-20261009'
DOC=ROOT/'docs/joint-affine-transfer'
FIG=DOC/'figures/20261009'
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

LABELS=['bing.com::search_results_view','developer.mozilla.org::document_view','github.com::repository_view',
        'wikipedia.org::article_view','youtube.com::search_results_view','youtube.com::video_playback']
NAMES=dict(zip(LABELS,['Bing搜索','MDN文档','GitHub仓库','Wikipedia文章','YouTube搜索','YouTube播放']))
ARMS=['CT0','CT1','CT2','CT3','CT4','StrongPost','JA0','JA1','JA2','CT5']
PROTOS=['shadowsocks','vless','trojan','vmess']
MASKS={'G0':[2,4],'G1':[0,3],'G2':[1,5]}


def read(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def table(frame, columns=None, decimals=6):
    if columns is not None:frame=frame[columns]
    def fmt(x):
        if isinstance(x,(bool,np.bool_)):return '是' if x else '否'
        if isinstance(x,(float,np.floating)):return f'{x:.{decimals}f}'
        return str(x).replace('|','\\|').replace('\n',' ')
    rows=['| '+' | '.join(map(str,frame.columns))+' |','| '+' | '.join(['---']*len(frame.columns))+' |']
    rows+=['| '+' | '.join(fmt(x) for x in values)+' |' for values in frame.itertuples(index=False,name=None)]
    return '\n'.join(rows)
def stamp(t):return dt.datetime.fromtimestamp(t,dt.timezone(dt.timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S')
def load(name):return pd.read_parquet(DATA/name)
def section(lines,name,body):lines.extend(['',f'## {name}','',body])
def ordered(frame):return frame.set_index('arm').loc[ARMS].reset_index()


def figures(pooled,targets,contrasts,recovery):
    FIG.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    fig,ax=plt.subplots(figsize=(9,4.4));xx=np.arange(len(ARMS));dd=ordered(pooled)
    colors=['#999999']*6+['#7ba9d1','#2166ac','#92c5de','#d9b875']
    ax.bar(xx,dd.F1_uncovered,color=colors);ax.set_xticks(xx,ARMS,rotation=25,ha='right')
    ax.set_ylim(0,1);ax.set_ylabel('Uncovered-business macro F1')
    for x,y in zip(xx,dd.F1_uncovered):ax.text(x,y+.015,f'{y:.3f}',ha='center',fontsize=9)
    ax.set_title('JA and frozen references (CT5: full-target supervision)');fig.tight_layout()
    fig.savefig(FIG/'pooled-uncovered-f1.png',dpi=200);fig.savefig(FIG/'pooled-uncovered-f1.pdf');plt.close(fig)
    fig,ax=plt.subplots(figsize=(8,3.9));rows=contrasts['comparisons']
    for i,r in enumerate(rows):
        point=r['delta']*100;lo,hi=np.array(r['CI_98_75'])*100
        ax.errorbar(point,i,xerr=[[point-lo],[hi-point]],fmt='o',capsize=5,color='#2166ac' if r['positive_increment'] else '#b2182b')
    ax.axvline(0,color='gray',ls='--');ax.set_yticks(range(4),['JA1 - '+r['reference'] for r in rows]);ax.invert_yaxis()
    ax.set_xlabel('Uncovered F1 difference (percentage points), 98.75% intervals')
    ax.set_title('Four prespecified comparisons; content-stratified bootstrap');fig.tight_layout()
    fig.savefig(FIG/'primary-comparisons.png',dpi=200);fig.savefig(FIG/'primary-comparisons.pdf');plt.close(fig)
    fig,ax=plt.subplots(figsize=(8,4.5));pivot=targets.pivot(index='target',columns='arm',values='F1_uncovered').loc[PROTOS]
    for arm in ['StrongPost','CT1','CT4','JA0','JA1','JA2']:ax.plot(range(4),pivot[arm],marker='o',label=arm)
    ax.set_xticks(range(4),['SS','VLESS','Trojan','VMess']);ax.set_ylim(0,1);ax.set_ylabel('Uncovered-business macro F1')
    ax.legend(ncol=3);ax.set_title('Per-target descriptive results');fig.tight_layout()
    fig.savefig(FIG/'target-uncovered-f1.png',dpi=200);fig.savefig(FIG/'target-uncovered-f1.pdf');plt.close(fig)
    fig,ax=plt.subplots(figsize=(8,4.5));p=recovery.pivot(index='calibration',columns='arm',values='MSE').loc[PROTOS]
    for arm in ['JA0','JA1','JA2']:ax.plot(range(4),p[arm],marker='o',label=arm)
    ax.set_xticks(range(4),['SS','VLESS','Trojan','VMess']);ax.set_yscale('log');ax.set_ylabel('Held-out standardized forward MSE (log scale)')
    ax.legend();ax.set_title('All six businesses; independent diagnostic, not classifier input');fig.tight_layout()
    fig.savefig(FIG/'forward-recovery.png',dpi=200);fig.savefig(FIG/'forward-recovery.pdf');plt.close(fig)


def run():
    complete=read(DATA/'complete.json');assert complete['report_analysis_complete']
    assert not (RUN/'completion.json').exists() and (RUN/'failure.json').exists()
    numerical=read(DATA/'independent-numeric-audit.json');integrity=read(DATA/'integrity.json')
    references=read(DATA/'reference-replay.json');primary=read(DATA/'comparisons/primary.json')
    pooled=load('scores/pooled.parquet');targets=load('scores/targets.parquet');scenes=load('scores/scenarios.parquet')
    classes=load('scores/classes.parquet');folds=load('scores/outer-folds.parquet');flips=load('scores/error-flips.parquet')
    recovery=load('diagnostics/recovery.parquet');coeff=load('diagnostics/cross-block-coefficients.parquet');shapes=load('diagnostics/source-view-shape.parquet')
    fits=load('audit/classifier-fit-summary.parquet');choices=pd.DataFrame(read(RUN/'selection/choices.json'))
    contract=read(RUN/'manifests/experiment-contract.json');obs=read(RUN/'observability/audit.json')
    recovery['partition']=np.where(recovery.inner.isna(),'outer-heldout','source-inner-heldout')
    recovery['uncovered']=[LABELS.index(y) in MASKS[g] for y,g in zip(recovery.label_id,recovery.group)]
    outer=recovery[recovery.inner.isna()]
    rec=outer.groupby(['arm','calibration']).MSE.mean().reset_index()
    recu=outer[outer.uncovered].groupby(['arm','calibration']).MSE.mean().reset_index()
    shape=shapes.groupby('arm')[['negative_fraction','maximum_negative','max_block_sum_error','input_outside_C_coordinate_fraction']].mean().reset_index()
    cs=classes[classes.uncovered].groupby(['arm','label']).F1.mean().unstack(0).loc[LABELS,['JA0','JA1','JA2','CT4','StrongPost','CT1']]
    cs['JA1减StrongPost']=cs.JA1-cs.StrongPost;cs['JA1减JA2']=cs.JA1-cs.JA2
    cs=cs.reset_index();cs['label']=cs.label.map(NAMES)
    tp=targets.pivot(index='target',columns='arm',values='F1_uncovered').loc[PROTOS,['JA0','JA1','JA2','CT4','StrongPost','CT1']]
    for a in ['StrongPost','CT1','JA2','JA0','CT4']:tp['JA1减'+a]=tp.JA1-tp[a]
    scene=scenes.pivot(index=['target','group'],columns='arm',values='F1_uncovered').reset_index()
    for a in ['StrongPost','JA2','JA0','CT4']:scene['JA1减'+a]=scene.JA1-scene[a]
    aux=targets.pivot(index='target',columns='arm',values='F1_aux').loc[PROTOS,['JA1','StrongPost','CT1','JA2']]
    aux['JA1减StrongPost']=aux.JA1-aux.StrongPost
    flip=flips[flips.uncovered].groupby('reference')[['fixed_error','new_error','prediction_changed']].sum().reset_index()
    flip['净正确增量']=flip.fixed_error-flip.new_error
    fliptarget=flips[flips.uncovered].groupby(['reference','target'])[['fixed_error','new_error']].sum().reset_index()
    fliptarget['净正确增量']=fliptarget.fixed_error-fliptarget.new_error
    eta=pd.crosstab(choices.arm,choices.eta).reset_index();reg=pd.crosstab(choices.arm,choices.t).reset_index()
    cost=fits.groupby('arm').agg(models=('seconds','size'),fit_seconds=('seconds','sum'),mean_seconds=('seconds','mean'),
        median_iterations=('iterations','median'),p95_iterations=('iterations',lambda s:s.quantile(.95)),
        max_iterations=('iterations','max'),max_evaluations=('function_evaluations','max')).reset_index()
    for name,frame in [('uncovered-business',cs),('target-deltas',tp.reset_index()),('aux-target',aux.reset_index()),
                       ('error-flip-summary',flip),('error-flip-target',fliptarget),('selection-eta',eta),('selection-t',reg),
                       ('runtime-by-arm',cost),('outer-recovery',rec),('outer-uncovered-recovery',recu),('shape-summary',shape)]:
        frame.to_parquet(DATA/(name+'.parquet'),index=False)
    figures(pooled,targets,primary,rec)
    contrasts=[]
    for r in primary['comparisons']:
        contrasts.append({'比较':'JA1减'+r['reference'],'F1差':r['delta'],'百分点差':r['delta']*100,
            '98.75%家族区间':f"[{r['CI_98_75'][0]:.6f}, {r['CI_98_75'][1]:.6f}]",
            '95%描述区间':f"[{r['CI_95'][0]:.6f}, {r['CI_95'][1]:.6f}]",'正向增量通过':r['positive_increment']})
    timeline=[{'阶段':'初次启动锁建立','北京时间':stamp((RUN/'recovery/20261008T111318-3564-stale-runner.lock').stat().st_mtime)}]
    for path in sorted((RUN/'manifests/stages').glob('*.json')):
        timeline.append({'阶段':path.stem,'北京时间':stamp(read(path)['time_unix'])})
    resume=read(RUN/'recovery/20261008T111318-3564.json')
    timeline.append({'阶段':'恢复任务启动','北京时间':stamp(resume['started_unix'])})
    timeline.append({'阶段':'恢复预检查完成','北京时间':stamp(resume['preflight']['time_unix'])})
    timeline.append({'阶段':'旧参照重放失败','北京时间':stamp(read(RUN/'failure.json')['time_unix'])})
    timeline=pd.DataFrame(timeline).sort_values('北京时间')
    numerical_table=pd.DataFrame([{'检查':'分类模型数','结果':numerical['models']},
        {'检查':'映射数','结果':numerical['maps']},
        {'检查':'分类器最大原坐标梯度','结果':f"{numerical['classifier_gradient_max']:.12g}"},
        {'检查':'分类器最大目标重放差','结果':f"{numerical['classifier_objective_error_max']:.12g}"},
        {'检查':'映射最大原坐标梯度','结果':f"{numerical['mapping_gradient_max']:.12g}"},
        {'检查':'映射最大目标重放差','结果':f"{numerical['mapping_objective_error_max']:.12g}"},
        {'检查':'新预测CUDA重放最大差','结果':complete['prediction_replay_max_error']},
        {'检查':'420项旧参照CUDA重放最大差','结果':references['probability_max_error']},
        {'检查':'旧指标重算最大差','结果':read(DATA/'scores/historical-reproduction.json')['max_metric_error']},
        {'检查':'原失败终态保留','结果':complete['original_failure_preserved']}])
    lines=['# 协议机制资格与联合仿射业务迁移实验完整分析报告','',
        '报告日期为2026年10月9日。本报告覆盖本轮数据、方法、训练权限、参数选择、运行中断、已封存预测、独立重放结果及结论边界。34740个新分类模型与8820个映射任务已经完成。原runner在旧CT5元数据读取处停止，未生成正式completion或verification；本报告在独立目录重放全部参照、复核全部新模型并计算既定统计，不改写原失败状态。',
        '', '## 一 核心结论','',
        '本轮没有建立联合仿射主方法的完整业务优势。JA1的未覆盖业务F1为0.685604，优于原样pre控制CT1的0.583306；但低于StrongPost的0.772708，与同容量组控制JA2的0.687591接近，较逐块真配JA0的0.668073只有描述性提升。四项家族校正比较只有JA1减CT1通过；联合结构增量和精确访问身份增量均未建立。',
        '',table(pd.DataFrame(contrasts)),
        '', '辅助业务实践筛查也未通过：合并辅助业务差满足登记门限，但Trojan的JA1减StrongPost辅助F1为-0.051005，低于预定-0.05门。差距仅比门限多0.1005个百分点，也不能事后放宽。',
        '', '可保留的研究结论是：校准后的访问视图比直接添加原样入口视图更有用途，但本轮联合仿射未达到强post适配参照，也没有证明同次访问身份在该映射中提供额外业务收益。机制资格审计还表明，代码中的编码规则并不自动成为历史抓包中的可观测状态。',
        '',f"![四项主比较]({(FIG/'primary-comparisons.png').as_posix()})"]
    section(lines,'二 原运行状态与报告结果的关系',
        '原实验于10月9日08:20:30封存全部4320条新外层预测，随后08:20:33在旧参照重放处停止。准确状态是“训练、选择和新预测完成；原评分及工程结项未完成”，不是训练失败或全部流程正常结束。\n\n'
        '停止原因是代码将历史CT5权重的元数据格式误认为逐模型同名JSON。20个权重均存在，历史模型通过其所在目录的complete.json及本轮已封存的历史IO契约保存哈希；没有权重丢失、重新选参或模型替换。\n\n'
        '独立报告分析沿用这条真实封存链，完成420项旧参照CUDA重放，概率与历史封存预测完全一致；同时重放180个新外层模型，概率与本轮封存预测完全一致。所有34740个分类器和8820个映射均通过独立原坐标目标与梯度复核。原failure.json保持原哈希，原completion.json和verification.json仍未创建。\n\n'
        '以下业务数字不是只读取训练loss得出的推测，而是封存后同口径评分与内容bootstrap结果；但不能据此声称原runner已经正式结项。')
    section(lines,'三 研究问题及与上一轮的区别',
        '上一轮CT第四版连接级逐统计量概率核CT4的未覆盖F1为0.717475，优于CT1和CT3，但低于StrongPost。本轮检验两种尚未证实的解释：协议内部机制变量可能未表达；访问级跨特征判别结构可能被独立核及期望直方图遗漏。\n\n'
        '工作A先界定机制变量可观测性。工作B保持96维输入，比较逐块真配、联合真配与同容量匿名组目标。新方法只学习确定性仿射条件均值，不是新的完整概率漂移分布，也没有引入半机制状态模块。\n\n'
        '旧CT4使用精确连接关系，本轮JA真配使用同次访问的两侧直方图。JA1减CT4同时改变估计器与粒度，不能单独归因于跨特征关系；JA1减JA0更接近联合结构比较，但参数量仍不同。')
    section(lines,'四 数据与实际部署',
        '| 部署 | 连接对 | 访问 | 当前配置范围 |\n| --- | ---: | ---: | --- |\n'
        '| SS | 5608 | 120 | AES-256-GCM，无plugin或smux |\n'
        '| VLESS | 5957 | 120 | TCP加TLS，无REALITY、Vision或smux |\n'
        '| Trojan | 5919 | 120 | TCP加TLS，无附加SS、REALITY或smux |\n'
        '| VMess | 6082 | 120 | WS加TLS，security为auto，alterId及最终内部模式仍有证据缺口 |\n'
        '| 合计 | 23566 | 480 | 四个实际部署，不是纯协议因果干预 |\n\n'
        '六业务为Bing搜索、MDN文档、GitHub仓库、Wikipedia文章、YouTube搜索和YouTube播放。每业务5内容、每内容4重复，重复1至4。四部署共享30个全局内容，不是120个独立内容。\n\n'
        '数据沿用Extend固定排他TCP队列，不混入0914、0916或64 URL尝试。AnyTLS与Hy2参加资格审计而未进入本轮分类；前者缺少同粒度排他TCP pair资格，当前Hy2来源缺少合格主W缓存并涉及共享carrier，不能沿用其他批次理由或强套TCP定义。')
    section(lines,'五 特征与输入表示',
        '连接级十项统计为W_up、W_down（观测正payload字节，含重复），U_up、U_down（唯一TCP字节），P_up、P_down（正payload包数），E_up、E_down（带正新字节的事件数），FR_packet_runs及R_unique_zero_runs。FR保留原非空包方向run口径，未替换为记录时间排序特征。\n\n'
        '四个字节特征各9箱，边界为1、256、1024、4096、16384、65536、262144、1048576；六个计数特征各10箱，边界为1、2、3、4、8、16、32、64、128。整数零独立落入第一箱，边界右侧归箱，末箱开放。访问内连接统计汇聚为十个归一化直方图块，共96维。\n\n'
        '没有新增flow数量、IAT、TLS记录序列、握手阶段、IP、端口、SNI、域名或协议ID作为数值模型输入。业务标签和内容身份用于监督、分折与权限，不作为输入特征。')
    section(lines,'六 划分与训练权限',
        '五个全局内容折，每折6内容、每业务1内容；同一内容在全部部署、重复、两侧、内部连接及生成视图中整体同折。外层4目标乘5折乘3业务组，共60场景。\n\n'
        '| 外层数据 | 数量 | 权限 |\n| --- | ---: | --- |\n'
        '| 三源库 | 288访问，24训练内容跨三源 | 六业务pre/post与标签可用 |\n'
        '| 目标C | 64访问，16内容，四业务 | 校准pre/post可用，身份按方法隔离 |\n'
        '| 目标U训练内容 | 32访问，8内容，两业务 | 两侧均禁止拟合、缩放、生成或选参 |\n'
        '| 目标H留出 | 24访问，6内容，六业务 | 冻结分类仅接收post，封存后评分及离线诊断 |\n\n'
        'G0未覆盖GitHub仓库及YouTube搜索；G1未覆盖Bing搜索及Wikipedia文章；G2未覆盖MDN文档及YouTube播放。三个源轮流作伪目标、四个内层内容折，形成720内层角色，实际外层目标不参与选参。\n\n'
        '权限负测试13项通过，包括匿名身份字段、C/U与留出边界、实际目标进入内层、组worker读取真配包、测试pre注入和外层标签选参。可信打包及应用白名单不是操作系统沙箱；登记成员整折不等于全历史TCP epoch重用均已普遍证明。')
    section(lines,'七 三新臂与七个冻结参照',
        '| 方法 | 辅助输入或权限 | 用途 |\n| --- | --- | --- |\n'
        '| JA0 BlockPaired | 逐块访问仿射、同次C配对 | 同粒度逐块参照 |\n'
        '| JA1 JointPaired | 全96维访问仿射、同次C配对 | 联合真配主候选 |\n'
        '| JA2 JointGroup | 同容量全96维仿射、同内容匿名集合 | 精确身份控制 |\n'
        '| CT0 PostJoint | 原源post重复辅助槽 | 充分混合post监督 |\n'
        '| CT1 RawPre | 原样源pre辅助槽 | 更多入口视图控制 |\n'
        '| CT2 CORAL | 源post经C匹配的CORAL | 常规适配强参照 |\n'
        '| CT3 GroupKernel | 源pre经匿名连接组核 | 旧粗对应概率核 |\n'
        '| CT4 PairedKernel | 源pre经精确连接核 | 旧配对概率核 |\n'
        '| StrongPost | 旧源内选择CT0或CT2，本轮固定 | 相同校准权限强参照 |\n'
        '| CT5 TargetFull | 完整六类目标post监督 | 不同权限的更多资源参照 |\n\n'
        'StrongPost在旧60场景均选择CT2，两个成绩相同不是新结果上事后选优。CT5不是数学上界，也不是主方法公平同权限参照。七旧对象重放预测但不重训。')
    section(lines,'八 仿射目标与匿名组构造',
        '每角色仅用真实source-post与C-post拟合共同均值和总体标准差，常数维scale置1。外层352个真实post行、内层192行；入口和出口都使用该post坐标，测试不重新标准化。\n\n'
        r'$$x_i=(h_i^- -\mu)/\sigma,\quad y_i=(h_i^+ -\mu)/\sigma,\quad\widehat y_i=Mx_i+b.$$' '\n\n'
        r'$$\mathcal L=\frac1{96}\sum_iw_i\|Mx_i+b-y_i\|_2^2+\frac{\eta\tau}{96}\|M-I\|_F^2,\quad\tau=\max\{\operatorname{tr}(S_{xx})/96,10^{-12}\}.$$' '\n\n'
        'C内内容与重复等权，权重总和1。截距不正则化，b为出口均值减M乘入口均值。JA0十个对角块以外结构置零，共1020参数；JA1与JA2为全矩阵，共9312参数。用CUDA float64 Cholesky解方程，不显式求逆、不加新jitter、不迭代训练大型生成器。\n\n'
        'JA2对每个pre输入使用同内容post中心，并保留目标方差常数，等价于对组内所有独立post donor的平方目标平均。保留全部pre协方差，不能把pre也取内容中心后声称目标等价；不读取同次访问身份或共享行序。\n\n'
        '强收缩趋向恒等线性部分加C均值平移，不严格等于CT1。适配输出是标准化坐标向量，不截负、归一化或声称合法TCP流量；这是恢复目标和任务效用的对照，不是按协议可行域生成会话。')
    section(lines,'九 分类器与源内选择',
        '固定96到6多项逻辑回归，582参数，无隐藏层。目标为带权CE加0.0005乘(1+t)乘W平方和，bias不正则化。外层源主槽288行、源pre辅助槽288行、C-post槽64行，共640行；内层144加144加48，共336行。三个槽质量各1/3，六类总质量各1/6，标签与源前后可用资源一致。\n\n'
        'eta为0.1、1、10、100；t为0、0.25、1、4，每新方法16组合。每个源伪目标合并四内层折的六类混淆矩阵计算未覆盖F1，再对三个伪目标等权。同分容差1e-12时优先更大eta，再优先更小t。旧StrongPost保留原选择，不能用新测试结果重选。新方法与旧方法搜索预算不同须保留。\n\n'
        '720乘3乘4乘4为34560内层分类器；60乘3为180外层分类器，共34740。内层8640加外层180为8820映射任务。先导720分类候选和180映射已计入，不重复加数；两次确定性重放是额外诊断。')
    section(lines,'十 选参分布',
        '以下为60外层场景每方法的源内选择次数，不是依据外层测试优化。较多选择网格下端eta=0.1，但不能据此扩展更低eta或认定边界最优；本轮冻结。\n\n映射正则eta：\n\n'+table(eta)+'\n\n分类正则t：\n\n'+table(reg))
    section(lines,'十一 评价与统计口径',
        '每方法、目标、业务组先合并五折120访问的完整六类混淆矩阵。未覆盖F1为其中两类F1平均，辅助F1为其余四类平均，均计入其他类造成的假阳性，不改成二分类。总体对四目标乘三组的12单元等权；最差部署为每部署三组均值的最小值。CE为nats，Brier为六类概率平方差之和。\n\n'
        '30个全局内容按六业务分层，每层5内容有放回采样，10000次、seed 20261007；同内容权重用于全部部署、重复、业务组和方法。四主比较共享98.75% Bonferroni家族区间，另给95%描述区间。区间条件于既有模型和选参，不覆盖完整独立重训练、外部部署、跨日期或人类回顾性选择不确定性。\n\n'
        '前三主比较JA1减StrongPost、CT1、JA2的校正下界均大于0且通过实践筛查，才构成完整业务增量；JA1减JA0单独检验联合结构。辅助合并差门为-0.02，最差目标辅助差门为-0.05；不是统计非劣效或等效检验。')
    section(lines,'十二 总体详细结果',table(ordered(pooled),['arm','F1_uncovered','F1_all','F1_aux','accuracy','CE_nats','CE_bits','Brier','worst_target_uncovered'])+
        f"\n\n![总体未覆盖业务F1]({(FIG/'pooled-uncovered-f1.png').as_posix()})\n\n"
        'JA1相对JA0改善F1、CE和Brier的点估计，但F1家族区间跨0。相对JA2，JA1的CE较低，但F1略低、Brier略高；不能把其中一个概率指标的改善包装为完整业务优势。相对StrongPost，JA1的主要分类和概率指标均更差。JA1比旧CT4低约3.19个百分点，属于估计器与粒度同时变化的描述性比较。')
    section(lines,'十三 四项主比较与辅助筛查',table(pd.DataFrame(contrasts))+'\n\n辅助业务逐目标：\n\n'+table(aux.reset_index())+
        '\n\nJA1合并辅助F1差分别为：对StrongPost -0.009566，对CT1 +0.022530，对JA2 +0.007512，均通过-0.02门；Trojan对StrongPost -0.051005使最差目标门未通过。不能因轻微越界删除Trojan或放宽门。完整业务与结构增量判定均为未通过。')
    section(lines,'十四 逐部署表现',table(tp.reset_index())+
        f"\n\n![逐部署未覆盖F1]({(FIG/'target-uncovered-f1.png').as_posix()})\n\n"
        'JA1在四目标上均低于StrongPost。SS和VMess相对CT1明显改善，但仍有约10.06与13.95个百分点强参照缺口；Trojan相对CT1也较弱。VLESS的JA1较JA0提升约4.79个百分点，但同容量JA2更高。VMess则JA1高于JA2约4.12个百分点。相反方向说明总体接近不等于每个部署都一样，逐部署差只作描述，不另造显著性结论。')
    section(lines,'十五 全部十二业务缺失场景',table(scene,['target','group','JA0','JA1','JA2','CT4','StrongPost','CT1','JA1减StrongPost','JA1减JA2','JA1减JA0'])+
        '\n\n十二场景中，JA1对JA0为7胜5负，对JA2为6胜1平5负，对StrongPost为3胜9负，对CT4为5胜7负。这些是点估计计数，不是十二次独立显著性检验。\n\n'
        'G1的Bing与Wikipedia迁移仍是突出弱项：VMess G1的JA1为0.460000、StrongPost为0.777090；SS G1分别0.512500与0.732639。VLESS G1的JA1还低于JA2。不能通过删除G1、改成更容易的二业务任务或只挑G0证明方法胜出。')
    section(lines,'十六 未覆盖条件下六业务分项',table(cs)+
        '\n\n每业务只取其作为U的对应业务组，再对四部署等权；不是在所有C/U权限场景混合平均。GitHub仓库和YouTube播放对StrongPost存在描述性点增量，但MDN、Bing、Wikipedia及YouTube搜索较弱，Wikipedia差距最大。JA1对JA2在GitHub及MDN点估计较高，在其余四业务较低；不能据这些例外重新选标签。')
    section(lines,'十七 修复错误与新增错误',table(flip)+
        '\n\n每个对照在未覆盖条件下比较480条同访问预测。JA1对CT1修复65、新增13，净增52；对StrongPost修复30、新增76，净减46；对JA2修复15、新增20，净减5。对JA0净增11，但宏F1区间仍跨0。净正确数不能直接换算宏F1。\n\n'+
        table(fliptarget[fliptarget.reference.isin(['StrongPost','JA2','JA0','CT4'])]))
    section(lines,'十八 留出forward恢复诊断',
        '测试pre只在全部新预测封存后进入离线诊断，不进入分类、权重、参数选择或重训。MSE在各角色共同post标准化坐标中计算，不是原始字节误差。以下先按全部六业务留出访问汇总，每方法外层1440条；同一访问跨三个掩码出现，不能当作独立1440访问。\n\n'+table(rec)+
        '\n\n仅未覆盖业务的外层恢复误差：\n\n'+table(recu)+
        f"\n\n![forward恢复误差]({(FIG/'forward-recovery.png').as_posix()})\n\n"
        'JA1较JA0降低了SS和VMess的MSE点估计，却未形成对应的家族校正分类优势；Trojan的MSE也未改善。这进一步表明恢复更准不自动等于业务识别更好。这里没有另行对MSE开展显著性检验。\n\n'
        '恢复误差反映条件均值可预测性，不保证分类边界或概率决策被保持。源内诊断受已选择参数条件约束，单独保存，不能替代外层证据。跨块系数范数仅作映射描述，不是协议因果贡献或互信息。')
    section(lines,'十九 适配向量形状与外推',table(shape)+
        '\n\nnegative_fraction为解码回直方图尺度后的负坐标比例；maximum_negative为每角色最负量幅度，再跨角色平均；max_block_sum_error为每角色最坏块和偏差的均值；input_outside_C_coordinate_fraction为源pre坐标超出训练C逐维范围的比例。均未据此剔除样本、截负或归一化。\n\n'
        '这些适配向量不受概率单纯形约束，不能称为合法出口直方图生成器。异常形状与分类失败同时存在也不足以证明它是唯一原因。')
    section(lines,'二十 机制审计与有限解析',
        f"采集实现绑定74cfed919c03f07a21b252328fe48b72c5361215，本地参考Meta绑定88dcbf7f1614a67c3b36b848ee3592dfa92ada36。登记16训练访问、32连接对，实际读取{obs['unique_capture_files_read']}个PCAP，哈希与解码累计扫描{obs['scan_bytes']/1024**3:.3f} GiB，保存{obs['record_rows']}条语法记录。\n\n"
        '达到16文件预算后，其余登记样本保留未解析标记，未以成功子集替换主分类队列。连续解析只使用有起点证据、无冲突的字节前缀，不补零、不任意重同步。外层记录类型、长度和区间是语法观测，不是initial/relay阶段、真实业务或逐记录语义对应。\n\n'
        'SS的实际AEAD chunk数、VMess内部WS或加密块、实际协商状态和语义阶段仍未识别。当前VLESS无Vision，不引入历史Vision规则；AnyTLS和Hy2的载体边界没有自动解除。源码局部格式可确认与捕获实际操作数可观测是两层证据。\n\n'
        '这些解析结果没有进入新分类器，因此不能将任何JA成绩归因为TLS记录输入或协议精确开销校正，也没有实现半机制模块。详见[机制资格报告](mechanism-observability-report.md)。')
    section(lines,'二十一 数值与完整性验收',table(numerical_table)+
        f"\n\n报告级校验覆盖{integrity['baseline_files']}项直接历史封存文件、{integrity['package_files']}个注册工作包以及模型、映射、槽位张量与元数据。数值先导720候选通过，两次重放参数差为0；完整模型统一CUDA float64、原坐标梯度门1e-5，映射梯度门1e-8，目标重放门1e-10。\n\n"
        '未增加分类器拟合，未重选旧参照，未改变installed optimizer、计划、封存源码或原失败哈希。报告级审计已通过，但原流程的正式verification没有生成。')
    section(lines,'二十二 时间与计算成本',table(timeline)+'\n\n'+table(cost)+
        f"\n\n34740个主分类器记录拟合秒数合计{fits.seconds.sum():.2f}，约{fits.seconds.sum()/3600:.2f}小时，平均{fits.seconds.mean():.4f}秒。日志秒数不含所有I/O、启动与报告级重放。首次启动至旧参照中止约38小时，其中有约11小时24分的外部中断间隔，不把停机等待算作GPU训练。\n\n"
        '此次长运行来自720角色乘三臂乘四eta乘四t的串行候选矩阵，而不是大网络或全量抓包重扫。旧CT第四版14700模型、约5小时50分完成，本轮数量约2.36倍，且单模型平均成本更高。单纯使用CUDA不保证多个小模型能持续占满显卡。')
    section(lines,'二十三 如何解释这组结果',
        '得到支持的是相对原样pre的适配用途，不是联合仿射主方法胜出。联合比逐块的F1点提升没有通过家族校正；同容量精确与组目标总体接近不能证明等效，更不能证明精确配对普遍无用。\n\n'
        '本轮至少表明：将连接级独立概率核换成访问级全矩阵条件均值，并不足以解决此前强post参照缺口。这也不证明所有联合分布模型不可能奏效，因为本轮没有生成联合随机分布、引入可见机制状态或检验其他低容量参数化。\n\n'
        'JA1相对旧CT4总体下降，不能归因为某个协议机制或配对关系失效；表示粒度和估计器同时变了。Trojan和VLESS、VMess的不同方向需要保留，不能把取消后的合并差解释成纯实例噪声或信息量。恢复MSE、系数、概率loss也不是互信息或通道容量估计。')
    section(lines,'二十四 结论范围与停止建议',
        '建议冻结JA0、JA1、JA2本轮候选和结果，不因负结果扩eta、删业务、扩大分类器或重新搜索状态。核心对照已经给出清楚回答：本轮没有新的强基线优势，也没有精确访问身份或联合结构的家族校正增量。\n\n'
        '若要完成原工程结项，下一步只需登记CT5元数据格式兼容修订，采用已经封存的目录级哈希链重放参照，然后执行原评分、诊断与最终验收；无需重训34740模型或8820映射。本次报告没有自动修订runner。\n\n'
        '后续科研若转回协议概率模型，应由可观测变量资格决定：记录语法、唯一字节及载体事件可用到哪一层，就只建模到那一层；不补成SS实际chunk、VMess隐状态、initial/relay或精确K。半机制设计及其同输入强post参照需要另行确认。\n\n'
        '当前数据已被反复分析，结果是拟合期内容隔离与固定部署校准评价，不是外部盲测。未验证范围仍包括未见节点配置、跨日期、真实DIRECT库、无索引在线分段、全部物理背景连接及全历史TCP epoch身份。')
    section(lines,'二十五 产物与复现入口',
        '独立证据脚本：`eval/joint_affine_transfer_analysis/build_report_evidence.py`；报告及绘图脚本：`eval/joint_affine_transfer_analysis/render_complete_report.py`。分析与推理用Pytorch312，拟合重放和模型推理要求CUDA float64，统计与制图可用CPU。\n\n'
        '报告证据位于 `outputs/joint-affine-transfer-20261007/run-01/report-analysis-20261009/`，包含完整性审计、420参照重放记录、独立数值验收、14400带标签预测、120评分单元、720逐类结果、600外层折结果、内容bootstrap、错误翻转、56160恢复诊断、18000跨块范数和180适配形状。\n\n'
        '原契约、模型、预测、进度和failure均保留；图表为本次报告生成，不能据图中点估计代替登记统计判断。完整逐项表见[结果附录](detailed-results-appendix-20261009.md)。')
    DOC.mkdir(parents=True,exist_ok=True)
    report=DOC/'detailed-experiment-report-20261009.md';report.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    appendix=['# 联合仿射迁移实验详细结果附录','',
        '这些表来自2026年10月9日独立报告重放。原runner保留失败状态；主报告说明设计、统计和结论范围。表内F1、CE及Brier采用完整六类预测，逐折表仅作描述，不把六内容的小折当作独立seed。']
    for title,frame in [('全部120个目标业务组评分单元',scenes.sort_values(['arm','target','group'])),
                        ('全部720条逐类别结果',classes.sort_values(['arm','target','group','label_index'])),
                        ('全部600个外层折评分',folds.sort_values(['arm','target','group','outer'])),
                        ('180个外层参数选择',choices.sort_values(['arm','target','group','outer'])),
                        ('源内及外层恢复概览',recovery.groupby(['partition','arm','calibration']).MSE.mean().reset_index()),
                        ('十特征块外层恢复误差',outer.groupby(['arm','calibration'])[[c for c in outer if c.startswith('MSE_')]].mean().reset_index())]:
        section(appendix,title,table(frame))
    (DOC/'detailed-results-appendix-20261009.md').write_text('\n'.join(appendix)+'\n',encoding='utf-8')
    appendix_path=DOC/'detailed-results-appendix-20261009.md'
    manifest={'report':str(report.relative_to(ROOT)).replace('\\','/'),'report_sha256':hashlib.sha256(report.read_bytes()).hexdigest(),
              'appendix_sha256':hashlib.sha256(appendix_path.read_bytes()).hexdigest(),
              'generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'figure_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(FIG.iterdir()) if p.suffix in {'.png','.pdf'}},
              'original_pipeline_complete':False,'independent_report_analysis_complete':True,
              'scientific_models_retrained':0,'numeric_replay_passed':numerical['passed'],
              'full_business_claim_passed':primary['full_business_claim_passed'],
              'structure_claim_passed':primary['structure_claim_passed']}
    (DATA/'report-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(manifest,ensure_ascii=False,indent=2))


if __name__=='__main__':run()
