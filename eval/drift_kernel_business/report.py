"""Generate a detailed, evidence-linked local Markdown report from frozen artifacts."""
from common import *

def table(frame):
    def fmt(value):
        if isinstance(value,(float,np.floating)):
            return f'{value:.6f}'
        if isinstance(value,(bool,np.bool_)):
            return '是' if value else '否'
        return str(value).replace('|','\\|').replace('\n',' ')
    return '\n'.join(['| '+' | '.join(frame.columns)+' |','| '+' | '.join(['---']*len(frame.columns))+' |']+
                     ['| '+' | '.join(fmt(v) for v in row)+' |' for row in frame.itertuples(index=False,name=None)])

def run():
    contract=read(OUT/'manifests/experiment-contract.json')
    verify=read(OUT/'verification.json')
    require(verify['passed'],'Verification required before formal report')
    summary=pd.read_parquet(OUT/'scores/protocol-summary.parquet')
    seeds=pd.read_parquet(OUT/'scores/protocol-seed.parquet')
    contrasts=pd.read_parquet(OUT/'comparisons/F1-contrasts.parquet')
    classes=pd.read_parquet(OUT/'scores/class-seed.parquet')
    confusion=pd.read_parquet(OUT/'scores/confusion.parquet')
    global_scores=pd.read_parquet(OUT/'scores/global-summary.parquet')
    fit=read(OUT/'manifests/baseline_fit-ledger.json')['fits']
    flips=pd.read_parquet(OUT/'explanations/error-flips.parquet')
    grouped=flips.groupby(['protocol','comparator','seed'])[['repaired','new_error','decision_changed']].sum().reset_index()
    distances=pd.read_parquet(OUT/'explanations/training-class-distances.parquet')
    gap=pd.read_parquet(OUT/'explanations/training-fit-gaps.parquet')
    content=pd.read_parquet(OUT/'scores/content-errors.parquet')
    outrel='../../outputs/drift-kernel-business-20261005/run-01'
    primary=contrasts[contrasts.family.eq('primary')]
    baseline=contrasts[contrasts.family.eq('baseline')]
    paragraphs=['# 漂移概率核与六类业务识别融合实验报告','',
       '日期：2026年10月5日。所有拟合、概率映射与推理已在Pytorch312的CUDA上完成。固定四已见部署、30内容、23566对连接、480父访问；原概率测量、采集数据与其他分类结果没有修改。',
       '',f'本轮预登记主F1家族的8项比较中，{int(primary.family_positive.sum())}项获得家族校正正向区间；直接post概率和小MLP的另8项关键基线比较中，{int(baseline.family_positive.sum())}项获得正向区间。表中负差和跨零区间均保留，没有进行结果驱动调参。',
       '', '## 1 核心结果与科学问题','',
       table(summary[['protocol','arm','F1','accuracy','CE','Brier']]),'',
       'G0是直接post业务概率；G1是post LR；G2是post小MLP三seed指标均值；G3是pre业务分布原样迁移；G4是真实配对漂移核；G5是同内容匿名组级核。所有方法使用相同post访问直方图及已知部署路由。',
       '', '三seed均值不是概率集成，也没有把一个访问复制成三个独立样本。确定性臂只拟合和报告一次。',
       '',f'![四部署F1]({outrel}/figures/protocol-F1.png)',
       '', '## 2 数据范围与业务标签','',
       table(pd.DataFrame([{'protocol':p,'pairs':EXPECTED[p],'visits':120,'contents':30,'repetitions':4} for p in PROTOCOLS])),
       '',table(pd.DataFrame({'label_index':range(6),'business':LABELS,'contents_per_class':[5]*6,'visits_per_protocol':[20]*6})),
       '', '沿用既有全局内容五折。每折24训练内容、6留出内容，每类4训练内容和1测试内容；每部署96训练访问、24测试访问。同内容的全部部署、重复、两侧与内部连接整体划分。最终OOF每部署120访问，业务支持均为20。',
       '', 'AnyTLS不具备当前排他TCP连接模型资格，Hy2是共享carrier单位，未进入主分类。不是沿用旧缺失原因猜测，也不是按性能筛选协议。给定访问范围及合格外层连接集合的条件仍存在，尚未验证无索引在线识别。',
       '', '## 3 观测与方法','',
       '十项是W/U上下行字节、P/E上下行计数、原正载荷包FR run、零阈值唯一新字节run。W/P与U/E分开，原FR没有改名替代。字节9箱、计数10箱，零独立，上界开放，共96维。没有额外加入IP、端口、SNI、URL、时序或连接数。',
       '', '训练频数按内容等权、内容内访问等权、访问内连接等权，每训练内容质量1。每类训练质量4，总质量24。S从带标签训练pre拟合；T从带标签训练post拟合，类分布平滑alpha=1、边际beta=1。真配与组级Q分别为S乘M1和S乘M2。',
       '', 'Q(y,b)=sum_a S(y,a) K(a,b)。核行是pre箱，列是post箱；没有求逆或把转置视为P(A|B)。十个核是单变量核，不是十维联合模型。推理以post连接箱频率h的平均log评分，字节/事件每项1/12，交互每项1/6，类先验1/6，自然对数，固定softmax温度1。',
       '', '共同核近似P(B_j|A_j,Y,c)≈P(B_j|A_j,c)是待检验的模型假设。粗箱未必充分表达资源角色与业务相关变化。高跨侧MI或好的统计预测并不保证源业务差异经过核后可区分。',
       '', '复合分数不是已校准的访问联合后验；CE用自然对数，Brier是六类误差平方和。相同特征频率输入下，判别式方法可以学习不同特征组合；本轮比较没有宣称这些学习器容量或优化预算完全相同。',
       '', '## 4 固定训练配置与资源','',
       '20个LR使用CUDA float64、多类softmax、训练均值/总体标准差、bias不正则、权重正则1e-3、LBFGS最多500步、strong_wolfe。',
       '', '60个MLP使用96→32→6、ReLU、3302参数，CUDA float32，AdamW lr=1e-3、weight_decay=1e-4，batch96，固定1000个更新；无dropout/BatchNorm/early stopping。seed为20261005、20261006、20261007。不按留出结果选择检查点。标准化先在float64计算，再转float32。',
       '', '全部预处理只拟合训练post访问。生成式S/T/Q为闭式CUDA计算，复用每外层训练区的200个主核文件，没有重跑旧1150文件或新增SSL。',
       '',table(pd.DataFrame(fit)[['protocol','fold','arm','seed','seconds','iterations','updates','objective','final_training_CE']].fillna('') if any('seed' in x for x in fit) else pd.DataFrame(fit)),
       '', '## 5 预登记主比较与不确定性','',table(primary[['protocol','comparison','point','lo95','hi95','family_lo','family_hi','family_positive']]),
       '', '主问题分别是真配G4是否优于原样G3，以及是否优于组级G5；这两种差异不能互相替代。主8项单独校正，不借用旧概率预测8项的结论。',
       '', '## 6 充分post基线比较','',table(baseline[['protocol','comparison','point','lo95','hi95','family_lo','family_hi','family_positive']]),
       '',table(contrasts[contrasts.family.eq('supplement')][['protocol','comparison','point','lo95','hi95']]),
       '', 'G4优于G3但未优于充分post基线时，只能说明漂移模型帮助该生成式迁移链，不能宣布超越常规目标侧监督。G4与G5接近也不证明统计等效；本轮没有登记等效界限。',
       '', '所有区间来自10000次六业务分层的内容组bootstrap，携带内容的全部重复和部署，共享同一抽样。主和基线家族各8项，Bonferroni置信度99.375%。区间条件于固定模型，不包含重训练、外部数据或研究者历史选择不确定性。每类仅5内容。',
       '',f'![增量区间]({outrel}/figures/F1-contrasts.png)',
       '', '## 7 部署等权与逐seed结果','',table(global_scores),'',
       table(seeds[seeds.arm.eq('G2')][['protocol','seed','F1','accuracy','CE','Brier']]),'',
       table(summary[summary.arm.eq('G2')][['protocol','F1_min','F1_max','CE_min','CE_max','Brier_min','Brier_max']]),
       '', '## 8 逐类别与混淆矩阵','',
       table(classes.groupby(['protocol','arm','label'])[['F1','precision','recall','support']].mean().reset_index()),
       '',f'![真配混淆矩阵]({outrel}/figures/true-kernel-confusions.png)',
       '', '## 9 概率输出与评分尺度','',
       f'![概率质量]({outrel}/figures/probability-quality.png)','',
       f'![可靠性]({outrel}/figures/reliability.png)',
       '', '固定平均评分与温度1可能使生成式概率较平；未根据测试结果修改温度。MLP概率也不自动校准；CE/Brier与F1是不同终点。可靠性图中的三seed合并点只作描述，正式统计仍按seed分别计算。',
       '', '## 10 业务分布经过核后的差异','',
       table(distances.groupby(['protocol','arm']).JS_nats.mean().reset_index()),'',
       table(gap.groupby('protocol')[['JS_true_vs_direct','JS_group_vs_direct']].mean().reset_index()),
       '', f'![训练类间距离]({outrel}/figures/source-to-output-class-distances.png)',
       '', '上表是训练区中全部15业务对、十变量、五fold的描述均值，不是业务互信息。源分布、真配Q、组级Q和直接post T的区别同时含有限估计及平滑；不能把每个差值都归为协议因果。Q与T不接近也不能单独定位一个具体协议阶段。',
       '', '## 11 修复错误与新增错误','',table(grouped),
       '', f'![错误翻转]({outrel}/figures/error-flips.png)',
       '', '以下内容表按固定标签与内容列出各臂错误；三seed分别保留。完整访问台账保存在explanations/error-flips.parquet。',
       '',table(content),
       '', '## 12 可追溯的分类贡献','',
       '每访问G4前两名业务分数差分解为w_j h_j(b) log(Q_first/Q_second)。全部480访问贡献求和通过分数差重放。各部署各业务的展示访问按稳定匿名ID预定，不挑成功个案。',
       '',f'![固定个案贡献]({outrel}/figures/fixed-example-contributions.png)',
       '', '这些贡献解释模型计算，不为每条CDN连接赋予业务语义，也不将某箱解释为握手或精确协议头。',
       '', '## 13 输入权限与可复现审计','',table(pd.DataFrame([{'check':k,'value':v} for k,v in verify.items() if k!='numeric_inference_input'])),
       '', '可信包装曾读取双侧资格缓存；训练分包只提供训练范围，推理仅读取query-post-hist及冻结模型。测试pre、标签、content ID、地址/SNI/端口不进入预测接口。已知部署只作核与基线路由，所有方法权限相同。文件角色台账不是OS安全沙箱。',
       '', '核频数、组级乘积和平滑已对20部署折、200核重新重放。登记实体不跨内容fold；仍保留历史不完整TCP epoch范围，不夸大为任意未观测会话的证明。全部模型重载后3840行概率及类别重放通过。',
       '', '## 14 结论范围与停止决定','',
       '本轮把已测得的代理条件关系直接接入访问级业务评分，实际检验了源分布、核和出口观测的整条链。结论以第5和第6节的实际增量与家族区间为准，不将统计预测成功自动升级成分类成功。',
       '', '现有数据仍是已见配置、已知路由、给定父访问范围、离线合格连接、未见内容任务。未检验未知部署、跨日期、外部DIRECT、少目标post/标签、AnyTLS/Hy2同粒度模型或在线无索引攻击。',
       '', '候选在这里冻结；未修改alpha、温度、权重、业务、分箱或网络预算。后续新方法需另行登记与用户确认，不以G4必须胜出为理由扩大搜索。',
       '', '## 15 文件与复现入口','',
       '代码：eval/drift_kernel_business。输出：outputs/drift-kernel-business-20261005/run-01。运行顺序及角色说明见该代码目录README.md。机器契约、原源SHA、包SHA、模型完成记录、预测封存和verification.json共同构成复现依据。',
       '', '原实施计划在本地plan目录；本报告不替换其预登记内容，也不覆盖旧protocol-probability-drift正式报告。']
    DOC.mkdir(parents=True,exist_ok=True)
    (DOC/'formal-report.md').write_text('\n\n'.join(paragraphs)+'\n',encoding='utf-8')
    (DOC/'experiment-contract.md').write_text('# 漂移核业务融合实验契约\n\n四部署480访问、23566对连接，六业务、五折全局内容留出。十单变量物理箱形成96维post访问直方图，部署已知并给所有基线相同路由。\n\nG0直接post概率，G1固定LR，G2固定三seed小MLP，G3入口分布原样，G4真实核，G5匿名组级核。训练S/T质量每内容1，alpha=beta=1，核只复用对应训练折，三族等权评分、温度1。\n\n主8项G4对G3/G5，关键基线8项对G0/G2，分别内容bootstrap并校正。所有结果保留，不按测试选模型或特征。详细数值、配置、角色、源码和输入SHA见机器契约及formal-report.md。\n\n全部拟合和推理CUDA；CPU限IO审计与固定模型统计。可信资格依赖双侧历史关联，推理函数post-only，不宣称在线资格发现或外部盲测。\n',encoding='utf-8')
    (DOC/'model-card.md').write_text('# 漂移感知业务分类模型说明\n\n用途：已知当前部署及父访问范围时，利用合格post连接识别六类domain × activity。\n\n训练业务模型S带标签；无业务条件的M1/M2从同折训练两侧估计。Q=S K，精确求和而非采样或逆变换。十核不构成联合似然，平均log评分softmax只是可评价的复合概率输出，不保证校准。\n\n推理数值输入仅96维post连接箱频率，无测试pre、标签、content ID、SNI、IP或端口。每部署独立路由，相同权限给post基线。没有连接数或时间特征。\n\n限制：共享核近似可能不成立，源业务差异可能被粗箱和核抹平；类内内容支持有限。当前离线共同资格及访问索引不能自动在post在线重建。未验证未知部署、跨日期、DIRECT、AnyTLS或Hy2。分类解释为分数贡献，不是协议因果解释。\n',encoding='utf-8')
    write(OUT/'manifests/report-complete.json',{'sha256':{rel(p):sha(p) for p in DOC.glob('*.md')},'formal_report_generated':True})
    print('Detailed formal report saved:',DOC/'formal-report.md',flush=True)

if __name__=='__main__':
    run()
