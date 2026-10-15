"""Comprehensive attribution evidence, with qualification gates kept separate."""
from common import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def md(d):
    def fmt(v):return f'{v:.6f}' if isinstance(v,(float,np.floating)) else str(v).replace('|','\\|')
    return '\n'.join(['| '+' | '.join(d.columns)+' |','| '+' | '.join(['---']*len(d.columns))+' |']+
                    ['| '+' | '.join(fmt(v) for v in row)+' |' for row in d.itertuples(index=False,name=None)])

def figure(fig,name):
    dst=DOC/'figures';dst.mkdir(parents=True,exist_ok=True);fig.tight_layout()
    fig.savefig(dst/(name+'.png'),dpi=180);fig.savefig(dst/(name+'.pdf'));plt.close(fig)

def run():
    with stage('report'):
        c=contract();pooled=pd.read_parquet(OUT/'scores/pooled.parquet').set_index('arm').loc[ARMS].reset_index()
        targets=pd.read_parquet(OUT/'scores/targets.parquet');classes=pd.read_parquet(OUT/'scores/classes.parquet')
        primary=read(OUT/'comparisons/primary.json');legacy=read(PARENT/'comparisons/primary.json')
        flips=pd.read_parquet(OUT/'diagnostics/overall.parquet');concentration=read(OUT/'diagnostics/concentration.json')
        percontent=pd.read_parquet(OUT/'diagnostics/content.parquet');cov=pd.read_parquet(OUT/'scores/coverage.parquet')
        historical=read(OUT/'audits/historical-compatibility.json');physical=read(OUT/'audits/physical-post-qualification.json')
        endpoints=pd.read_parquet(OUT/'manifests/new-endpoints.parquet');pilot=read(OUT/'pilot/promotion.json')
        comparisons=pd.DataFrame([{'candidate':v['candidate'],'reference':v['reference'],'delta_F1_U':v['delta_F1_uncovered'],
            'CI98.333333_low':v['CI_98_333333'][0],'CI98.333333_high':v['CI_98_333333'][1],
            'positive_increment':v['positive_increment']} for v in primary['comparisons']])
        passed=[v['reference'] for v in primary['comparisons'] if v['positive_increment']]
        conclusion=('P-small相对三个新增小比例对照均建立正向未覆盖业务F1增量。' if len(passed)==3 else
                    'P-small相对'+('、'.join(passed) if passed else '任何新增小比例对照均未')+'建立正向未覆盖业务F1增量。')
        fig,ax=plt.subplots(figsize=(11,4.5));xx=np.arange(4);width=.13
        for j,a in enumerate(ARMS):
            vals=targets[targets.arm.eq(a)].set_index('target').loc[PROTOCOLS].F1_uncovered
            ax.bar(xx+(j-2.5)*width,vals,width,label=a)
        ax.set_xticks(xx,PROTOCOLS);ax.set_ylim(0,1);ax.set_ylabel('Uncovered F1 from six-class CM');ax.legend(ncol=3,fontsize=8)
        figure(fig,'six-arm-deployment-f1')
        fig,ax=plt.subplots(figsize=(8,3.8));ax.axvline(0,color='gray')
        for i,v in enumerate(primary['comparisons']):
            ax.plot(v['CI_98_333333'],[i,i],color='C0');ax.plot(v['delta_F1_uncovered'],i,'o',color='C0')
        ax.set_yticks(range(3),[f"P-small - {v['reference']}" for v in primary['comparisons']]);ax.invert_yaxis()
        ax.set_xlabel('Delta F1; 98.333333% content bootstrap CI');figure(fig,'primary-three-contrasts')
        fig,ax=plt.subplots(figsize=(10,4));x=np.arange(5)
        ax.bar(x-.17,flips.repaired,.34,label='Repaired');ax.bar(x+.17,flips.added,.34,label='Added')
        ax.set_xticks(x,flips.reference,rotation=15);ax.legend();ax.set_ylabel('Role-visit exposures, not independent visits')
        figure(fig,'repaired-added-errors')
        fig,axes=plt.subplots(2,1,figsize=(12,7));labels=['Bing','MDN','GitHub','Wikipedia','YT search','YT video']
        classavg=classes.groupby(['arm','label_index']).F1.mean();d=pd.read_parquet(OUT/'scores/labeled-predictions.parquet')
        ce={}
        for (a,lab),part in d.groupby(['arm','label_id']):
            yy=truths(part);p=part[[f'p{i}' for i in range(6)]].to_numpy();ce[(a,LABELS.index(lab))]=float(-np.log(p[np.arange(len(yy)),yy]).mean())
        for j,a in enumerate(ARMS[1:]):
            axes[0].plot(range(6),[classavg.loc[(a,i)]-classavg.loc[('S',i)] for i in range(6)],marker='o',label=a)
            axes[1].plot(range(6),[ce[(a,i)]-ce[('S',i)] for i in range(6)],marker='o',label=a)
        for ax in axes:ax.axhline(0,color='gray');ax.set_xticks(range(6),labels);ax.legend(ncol=3,fontsize=8)
        axes[0].set_ylabel('Class F1 delta vs S');axes[1].set_ylabel('Class CE delta vs S (nats)');figure(fig,'business-f1-ce')
        part=percontent[percontent.reference.eq('S')].sort_values(['label_id','content_id'])
        fig,ax=plt.subplots(figsize=(12,4));x=np.arange(len(part))
        ax.bar(x-.18,part.repaired,.36,label='Repaired');ax.bar(x+.18,part.added,.36,label='Added')
        ax.set_xticks(x,[str(i+1) for i in x]);ax.set_xlabel('All 30 contents; identities in appendix');ax.set_ylabel('Role-visit exposures');ax.legend()
        figure(fig,'all-content-concentration')
        oldcontrast=next(v for v in legacy['comparisons'] if v['candidate']=='P-small' and v['reference']=='G-small')
        body=f'''# 小比例辅助视图收益归因完整报告

2026年10月10日。冻结P-small、StrongPost和G-small，补齐RawPre-small、RawPost-small及Marginal-small三个同样小比例的对照，共完成180个新分类器和60个匿名边际矩变换。{conclusion}

本轮解释原P-small相对StrongPost的约2.42个百分点收益，不改变P-small或重新搜索比例。新对照能排除哪些解释，应逐项依据下表；不能把某一个参照失败解释为精确访问身份必要。

## 数据和输入

extend的SS、VLESS、Trojan、VMess四部署，480访问、30内容、六业务、每内容每部署四重复，23566对排他TCP连接。五个全局内容折对全部部署、重复、两侧及flow整体划分；四目标乘五折乘三个业务遮蔽，共60外层角色。每角色使用三源288训练访问、目标四类C的64访问，目标两类U的32训练访问两侧均禁用，留出H为24访问。

六类依次为Bing搜索、MDN文档、GitHub仓库、Wikipedia文章、YouTube搜索、YouTube视频。当前VLESS是TCP+TLS，不是历史REALITY/Vision。AnyTLS、Hy2未进入本轮。

模型输入固定96维连接边际直方图，由W上下行、U上下行、P上下行、E上下行、FR_packet_runs和R_unique_zero_runs组成。分箱、连接纳入和访问汇聚沿用冻结口径。IP/端口/SNI/URL文本、协议ID、连接数、时间序列和配对索引均不进入分类器。

预处理只来自源真实post288行加目标C-post64行，常数维scale为1。pre也使用这套post坐标，不重新缩放、剪裁或投影。源pre/post独立排序，各自标签和质量随自身行移动。

## 六臂设计与训练资源

| 臂 | 原辅助槽组成 | 新拟合 |
| --- | --- | --- |
| S | 100% CORAL | 0，复用60 |
| P-small | 90% CORAL+10%真配全仿射pre | 0，复用60 |
| G-small | 90% CORAL+10%内容组全仿射pre | 0，复用60 |
| RawPre-small | 90% CORAL+10%原始源pre | 60 |
| RawPost-small | 90% CORAL+10%原始源post | 60 |
| Marginal-small | 90% CORAL+10%匿名边际矩适配pre | 60 |

所有新臂的目标为J_S+0.1(A_X-A_CORAL)。源post主槽1/3、CORAL0.3、新视图1/30、目标C-post1/3，六类各1/6。10%是辅助槽比例，只占总CE质量约3.33%，不是新增加10%独立样本，也不是把两个向量平均。

RawPost-small增加同一源post的损失暴露，源post直接暴露由1/3增至11/30。因此其用途是检查减CORAL/加原post解释，不能声称所有臂post暴露相同。small统一保存928个加权计算行，独立访问并未增加。

Marginal只使用目标C两侧各64行的匿名数值与等权质量，不读取内容token、visit、repetition、配对索引或业务标签。两侧独立置乱，在冻结坐标使用样本协方差、固定+I白化着色：T(z)=(z-m_pre)(Σ_pre+I)^(-1/2)(Σ_post+I)^(1/2)+m_post。没有跨侧交叉协方差，保留两侧各自的96维跨维协方差。正则化协方差的对齐不等于原始协方差精确对齐。它是双侧适配而非post-only；与P的估计器也不同，不能单独提供身份必要性的因果证据。

## 模型和数值配置

96→6逻辑回归，582参数；weight L2为0.0005(1+t)，bias不惩罚。t完全复用StrongPost；P/G与其原JA2 eta和视图冻结，Marginal无eta选择。零初始化、可逆Cholesky预条件化、原坐标梯度感知LBFGS，max_iter=2000、max_eval=10000，原梯度最大值≤1e-5、目标和梯度重放误差<1e-10。

训练、矩变换与模型推理在{c['environment']['gpu']}、CUDA {c['environment']['cuda']}、float64上执行，CPU仅用于文件处理、bootstrap和绘图。12固定角色的36先导拟合已计入180；先导只核验数值、未读目标标签或查询。拟合耗时中位数{endpoints.seconds.median():.3f}秒，总计{endpoints.seconds.sum():.3f}秒，不含其他阶段。

全部360个方法角色模型先封存，之后生成并封存8640行post预测；真实独立访问仍是480。目标U训练两侧和测试pre未读取。原S/P/G概率与指标复现，旧full负结果及失败影响函数先导保持原样。

## 主要结果

每部署×遮蔽先合并五折，构造完整六类混淆矩阵，再取未覆盖两类F1，四部署与三遮蔽等权。不是在真实U行上做二分类。

{md(pooled)}

![逐部署六臂结果](figures/six-arm-deployment-f1.png)

## 三项预定比较

30内容按六业务分层，10000次bootstrap、种子20261010；同一抽样质量共享于部署、重复、遮蔽和方法。新三项家族使用98.333333%区间，95%只辅助保存。

{md(comparisons)}

![三项主要增量](figures/primary-three-contrasts.png)

旧四项家族区间不改写。本轮不重复检验旧P-small−G-small以期待转正：其原点差为{oldcontrast['delta_F1_uncovered']:.6f}，98.75%区间为{oldcontrast['CI_98_75']}。即使新三项全通过，该旧比较仍未建立精确访问配对的额外业务用途。区间跨零不是等效。

区间条件于固定模型，不包含重训练变异，也不是跨日期、外部节点或研究者未知数据验证。此前多轮分析带来的回顾性选择边界仍存在；旧四项加新三项不能称一个统一七项家族。

## 部署与业务分项

{md(targets)}

业务CE与F1变化分开保留，不用概率改善替代主F1终点，负部署和YouTube例外不删除。

![业务变化](figures/business-f1-ce.png)

## 修复和新增错误及集中程度

{md(flips)}

{md(pd.DataFrame(concentration))}

![错误翻转](figures/repaired-added-errors.png)

![全部内容的收益集中程度](figures/all-content-concentration.png)

每比较1440个角色—访问暴露；unique_fixed_visits和unique_added_visits去除了同访问在不同遮蔽中的重复计数，但两列可重叠，因为同一访问可能在不同模型角色中被修复或被损害。内容全表、C/U、部署、折、概率L1和CE差均在附录及机器表中。30次留一内容只对冻结预测描述性计分，不重训，不作为主区间或选择依据。

## 跨批次和物理输入资格

{md(pd.DataFrame(historical['batches']))}

0914/0916不是自动加入训练的新数据。历史157维业务摘要不能直接替代96维连接直方图；既有字节台账提供部分基础，但仍需独立构造、连接资格及窗口审核。跨批次相同资源必须全局排除训练/测试重叠。旧VLESS配置不同、历史SS cipher未知；不因配置差异删掉数据，也不强行重标业务。

物理输入资格仍未通过：现有{physical['existing_windows']}个窗口的结束规则依赖browser_quiescent，未核实攻击者独立外部窗口；完整物理连接重建也未验证。现有W/T缓存不能自动证明能从物理post恢复全部96维输入。没有读取PCAP或执行重建，本轮仍是离线关联整理后的post-only模型推理。

详见[历史批次兼容性](historical-batch-compatibility-20261010.md)和[物理post资格](physical-post-qualification-20261010.md)。需新提取、跨批次训练或有限PCAP时另行确认，不阻断本轮已完成的分类归因。

## 结论与停止

{conclusion} 未超过RawPre时，原样额外pre仍可能足够；未超过RawPost时，减CORAL/重复post仍可能解释收益；超过这两项但未超过Marginal时，简单双侧矩适配尚未被排除。超过三个也不能越过旧G-small证据边界。

这轮不选择新的最强臂，不改beta/eta/t，不削弱G，不增seed或重跑full。物理输入与跨批次资格保持单独状态；不会因主分类完成写成全部验证通过。

## 复核产物

运行根`{rel(OUT)}/`包含合同、来源SHA、匿名工作包、60矩变换、180新模型和日志、8640预测、六类CM、抽样质量、三项区间及独立验收。首次run-01仅完成登记，外部库路径核验错误导致在测试/拟合前停止；记录保留，run-02只修复路径处理，科学设置与数值政策不变。代码在`eval/small_view_attribution/`。详见[详细附录](detailed-appendix-20261010.md)。
'''
        textfile(DOC/'detailed-report-20261010.md',body)
        appendix='# 小比例收益归因详细附录\n\n'
        for title,path in [('逐类别结果','scores/classes.parquet'),('逐角色结果','scores/outer-folds.parquet'),
              ('留出覆盖分项','scores/coverage.parquet'),('全部内容错误翻转','diagnostics/content.parquet'),
              ('逐业务与覆盖错误翻转','diagnostics/business-coverage.parquet'),('留一内容描述性敏感性','diagnostics/leave-one-content.parquet'),
              ('新分类器数值验收','manifests/new-endpoints.parquet')]:
            appendix+='## '+title+'\n\n'+md(pd.read_parquet(OUT/path))+'\n\n'
        appendix+='## 原四项检验保留\n\n```json\n'+json.dumps(legacy,ensure_ascii=False,indent=2)+'\n```\n'
        textfile(DOC/'detailed-appendix-20261010.md',appendix)
        details=pd.read_parquet(OUT/'audits/historical-businesses.parquet');over=pd.read_parquet(OUT/'audits/cross-batch-overlap.parquet')
        textfile(DOC/'historical-batch-compatibility-20261010.md','# 历史批次业务与表示兼容性\n\n'+md(pd.DataFrame(historical['batches']))+
          '\n\n## 历史业务与内容覆盖\n\n'+md(details)+'\n\n## 跨批次资源重叠\n\n'+md(over)+
          '\n\n只统一显式YouTube video ID别名，其他URL不任意删查询参数。0916六类标签吻合不意味着资源独立或表示可直接迁移；0914缺当前YouTube搜索类，不能强行重标。历史缓存与新96维输入需要单独登记重构。当前没有新特征提取、PCAP扫描或跨批次拟合。\n')
        textfile(DOC/'physical-post-qualification-20261010.md','# 物理post输入资格审计\n\n当前模型是post-only，但输入连接集与窗口仍依赖离线整理，物理输入资格未通过。\n\n```json\n'+json.dumps(physical,ensure_ascii=False,indent=2)+
          '\n```\n\n继续需要攻击者独立窗口、全部物理连接（含背景和未配对）、单侧方向与去重状态、固定截断和并发规则。若需要读取PCAP，先限定文件与读盘预算由用户确认。本轮仅盘点缓存及窗口来源，没有构造新的测试输入。\n')
        write(OUT/'manifests/report-complete.json',{'report_sha256':sha(DOC/'detailed-report-20261010.md'),
              'appendix_sha256':sha(DOC/'detailed-appendix-20261010.md'),'figures':5,'new_fits':0})

if __name__=='__main__':run()
