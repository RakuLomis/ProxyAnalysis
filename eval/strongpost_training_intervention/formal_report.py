"""Report finite classification evidence separately from unvalidated influence."""
from common import *
import formal
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def md(d):
    def val(x):
        if isinstance(x,(float,np.floating)):return f'{x:.6f}'
        return str(x).replace('|','\\|')
    return '\n'.join(['| '+' | '.join(d.columns)+' |','| '+' | '.join(['---']*len(d.columns))+' |']+
        ['| '+' | '.join(val(x) for x in r)+' |' for r in d.itertuples(index=False,name=None)])

def figure(fig,name):
    path=DOC/'figures';path.mkdir(parents=True,exist_ok=True)
    fig.tight_layout();fig.savefig(path/(name+'.png'),dpi=180);fig.savefig(path/(name+'.pdf'));plt.close(fig)

def run():
    with stage('formal_report'):
        a=formal.authorization();c=contract();primary=read(OUT/'comparisons/primary.json')
        pooled=pd.read_parquet(OUT/'scores/pooled.parquet').set_index('arm').loc[ARMS].reset_index()
        targets=pd.read_parquet(OUT/'scores/targets.parquet');classes=pd.read_parquet(OUT/'scores/classes.parquet')
        flips=pd.read_parquet(OUT/'scores/error-flips.parquet');local=pd.read_parquet(OUT/'influences/unvalidated-local-vs-actual.parquet')
        parts=pd.read_parquet(OUT/'influences/source-content-contributions.parquet')
        endpoints=pd.read_parquet(OUT/'manifests/formal-endpoints.parquet');pilot=read(OUT/'pilot/promotion.json')
        cols=['arm','F1_uncovered','F1_aux','F1_all','accuracy','CE_nats','Brier','worst_target_uncovered']
        contrasts=[]
        for v in primary['comparisons']:
            contrasts.append({'candidate':v['candidate'],'reference':v['reference'],
                'delta_F1_U':v['delta_F1_uncovered'],'CI98.75_low':v['CI_98_75'][0],
                'CI98.75_high':v['CI_98_75'][1],'positive_increment':v['positive_increment']})
        differences=pd.DataFrame(contrasts)
        fs=flips.groupby(['candidate','reference'])[['fixed_error','new_error','changed','probability_L1']].agg(
            {'fixed_error':'sum','new_error':'sum','changed':'sum','probability_L1':'mean'}).reset_index()
        changes=local.groupby(['arm','scope']).actual_delta_CE.mean().reset_index()
        target_changes=local.groupby(['target','arm','scope']).actual_delta_CE.mean().reset_index()
        times=[read(p)['seconds'] for p in (OUT/'fit-logs').rglob('*.json')]
        beta_labels={'S':'CORAL 100%', 'P-small':'CORAL 90% + paired 10%', 'G-small':'CORAL 90% + group 10%',
                     'P-full':'paired 100%', 'G-full':'group 100%'}
        qualified=[v for v in primary['comparisons'] if v['positive_increment']]
        conclusion='；'.join(f"{v['candidate']}相对{v['reference']}的未覆盖F1增量通过本轮家族校正区间" for v in qualified)
        if not conclusion:conclusion='四项固定比较均未建立家族校正区间下的正向未覆盖F1增量'
        # Fixed figures, no result-driven model choice.
        fig,ax=plt.subplots(figsize=(9,4.5));x=np.arange(4);width=.15
        for j,arm in enumerate(ARMS):
            values=targets[targets.arm.eq(arm)].set_index('target').loc[PROTOCOLS].F1_uncovered
            ax.bar(x+(j-2)*width,values,width,label=arm)
        ax.set_xticks(x,PROTOCOLS);ax.set_ylabel('Uncovered-class F1 (six-class CM)');ax.set_ylim(0,1)
        ax.legend(ncol=5,fontsize=8);figure(fig,'f1-by-deployment')
        fig,ax=plt.subplots(figsize=(8,3.8));ax.axvline(0,color='gray',lw=1)
        for j,v in enumerate(primary['comparisons']):
            point=v['delta_F1_uncovered'];lo,hi=v['CI_98_75'];ax.plot([lo,hi],[j,j],color='C0',lw=2);ax.plot(point,j,'o',color='C0')
        ax.set_yticks(range(4),[f'{v[0]} - {v[1]}' for v in formal.COMPARISONS]);ax.invert_yaxis()
        ax.set_xlabel('Delta uncovered F1; content bootstrap 98.75% CI');figure(fig,'primary-contrasts')
        fig,axes=plt.subplots(1,2,figsize=(10,4.2))
        for ax,scope in zip(axes,['C','U']):
            s=local[local.scope.eq(scope)].groupby('arm').actual_delta_CE.mean().reindex(ARMS[1:])
            ax.bar(np.arange(4),s.values);ax.set_xticks(np.arange(4),ARMS[1:],rotation=25)
            ax.axhline(0,color='gray');ax.set_title('Held-out '+scope+' businesses');ax.set_ylabel('Actual delta CE (nats) vs S')
        figure(fig,'actual-ce-by-coverage')
        fig,ax=plt.subplots(figsize=(7,4.5))
        for arm in ['P-small','G-small']:
            z=local[local.arm.eq(arm)&local.scope.eq('U')]
            ax.scatter(z.I_unvalidated,z.actual_delta_CE,label=arm,alpha=.7,s=23)
        ax.axhline(0,color='gray');ax.axvline(0,color='gray');ax.legend()
        ax.set_xlabel('UNVALIDATED local CE direction per beta');ax.set_ylabel('Actual U delta CE')
        ax.set_title('Retrospective approximation only; not a passed derivative check')
        figure(fig,'unvalidated-local-vs-small-ce')
        fig,ax=plt.subplots(figsize=(9,4));xx=np.arange(4)
        ax.bar(xx-.17,fs.fixed_error,.34,label='Repaired errors');ax.bar(xx+.17,fs.new_error,.34,label='Added errors')
        ax.set_xticks(xx,[f'{r.candidate}\nvs {r.reference}' for r in fs.itertuples()]);ax.legend()
        ax.set_ylabel('Role-visit exposures (overlapping masks)');figure(fig,'error-repair-and-addition')
        fig,ax=plt.subplots(figsize=(7,4.2))
        for arm in ['P','G']:
            v=parts[parts.arm.eq(arm)].I_U.to_numpy();ax.hist(v,bins=40,alpha=.45,label=arm)
        ax.set_xscale('symlog',linthresh=.01);ax.legend();ax.set_xlabel('UNVALIDATED local U contribution')
        ax.set_ylabel('Source deployment-content terms');figure(fig,'source-content-local-contributions')
        body=f'''# StrongPost辅助视图有限训练干预完整报告

2026年10月9日。保持原五臂、映射及分类正则、CUDA float64求解政策和四项比较不变，本轮完成全部60外层角色的有限干预。{conclusion}。

这是固定训练材料替换的分类证据，不是对整个配对方法族的最终裁决。影响函数先导未通过近似精度门，原失败完整保留；用户确认后继续的是有限重训，而不是宣布先导通过。报告将实际业务结果与未验收局部影响明确分开。

## 数据与任务

沿用extend合格TCP队列：Shadowsocks、VLESS、Trojan、VMess；480个访问、30个内容、六业务，每部署每内容四次重复，共23566对排他TCP连接。AnyTLS和Hy2不进入本轮，不将结果推广到这两种载体。

业务为Bing搜索结果、MDN文档、GitHub仓库、Wikipedia文章、YouTube搜索结果、YouTube视频播放。当前extend VLESS是TCP加TLS，不能套用旧队列的REALITY与Vision机制。

五个全局内容折对全部部署、重复、两侧和内部连接整体划分。每个目标部署的三种业务遮蔽分别为G0的GitHub与YouTube搜索、G1的Bing与Wikipedia、G2的MDN与YouTube视频。四部署乘五折乘三个遮蔽，共60角色。

每角色有三源部署的288训练访问，目标四类C的64访问，目标两类U的32训练访问禁止使用任何一侧；六类留出H为24访问。H中校准业务16访问，未覆盖业务8访问。本轮没有同内容跨折随机拆重复。

## 表示与输入权限

固定96维访问级连接边际直方图，由W上下行、U上下行、P上下行、E上下行、正payload方向段和唯一新字节方向段共十项构成。字节四项各9箱、计数六项各10箱。W包含重复观测的正payload字节，U是唯一TCP字节；FR_packet_runs与R_unique_zero_runs各自保持原定义。

没有新增地址、端口、SNI、域名文本、协议ID、访问索引、连接数、IAT或TLS记录序列输入。部署和内容元数据只用于可信分组、划分及权限检查。共同标准化只来自源真实post加目标C-post的352行，常数维scale为1；测试post不重新缩放。

P/G映射在目标C中拟合；它们共同采用原JA2在源内选出的eta。分类正则统一为该角色冻结StrongPost的t，不重新调参。源pre和源post独立排序，分别沿用自己的标签和质量，不按行号恢复同次访问。

## 干预设计

源真实post、源辅助槽、目标C-post损失质量各为1/3，六类总质量各1/6。原核心CE与weight L2不变；bias不惩罚。每个角色保持同一个源库与C资源，只替换辅助槽的质量。

| 臂 | 辅助槽 | beta | 含义 |
| --- | --- | --- | --- |
| S | 原CORAL | 0 | 冻结StrongPost |
| P-small | 90% CORAL加10%真配全仿射视图 | 0.1 | 真配小比例干预 |
| G-small | 90% CORAL加10%匿名内容组全仿射视图 | 0.1 | 同容量身份控制 |
| P-full | 全部真配视图 | 1 | 完整替换 |
| G-full | 全部匿名内容组视图 | 1 | 完整替换控制 |

beta作用于原辅助槽质量，0.1只替换全CE质量约3.33%；它不是平均特征向量。small有928个加权计算行，full与S有640行，不是新增这些数量的独立访问。P与S包含输入侧及变换方式变化；P与G的同设置比较才直接隔离精确身份增量。

分类器为96到6逻辑回归，576个weight加6个bias。L2为0.0005乘1加t乘weight平方和。新拟合统一零初始化、可逆预条件化、CUDA float64、max_iter为2000、max_eval为10000；原坐标梯度不超过1e-5、目标及梯度重放误差小于1e-10。没有warm start、标签调整、新网络或权重搜索。

## 主结果

每部署每遮蔽先合并五折预测，计算完整六类混淆矩阵，再取未覆盖两类F1均值；四部署与三遮蔽组等权汇总。不是仅在真实U样本上建立简化二分类。

{md(pooled[cols])}

![逐部署未覆盖业务F1](figures/f1-by-deployment.png)

## 四项固定比较

以下全部保留，不从small和full中挑选“最终方法”。对30个全局内容按六业务分层，10000次有放回抽样，同一抽样质量共享于部署、遮蔽、重复和方法；随机种子20261009。四项家族采用98.75%区间，95%区间仅在机器表中辅助保存。

{md(differences)}

![固定主比较](figures/primary-contrasts.png)

区间条件于已经拟合的模型，不包含重训练变异，也不是外部验证。数据此前经过多轮分析，本轮内部封存不能使其变为从未接触的盲测。区间跨零不证明等效；部分正向比较不等于完整配对增益主张成立。

## 部署差异

{md(targets[['target','arm','F1_uncovered','F1_aux','F1_all','CE_nats','Brier']])}

部署是当前观测到的特定配置，不能从一个SS或VLESS部署推断协议全部实现。原StrongPost未覆盖F1重现为0.772708；未因某部署退化删掉它或重新选择主方法。

## 校准与未覆盖业务的实际损失变化

下表全部是留出内容的真实post。C表示四类校准业务的新内容，U表示两类未覆盖业务的新内容，而不是训练C与测试U比较。数值是相对S的CE nats变化，负值表示实际损失降低。

{md(changes)}

![实际CE分层](figures/actual-ce-by-coverage.png)

逐部署和逐业务的变化完整保存在附录与机器表。CE改善不能替代原F1终点，修复与新增错误必须一起检查。

## 修复与新增错误

{md(fs)}

![修复与新增错误](figures/error-repair-and-addition.png)

这些是60角色下的访问暴露计数，每比较1440行，含同一访问在三遮蔽组中的重复使用；不是1440个独立用户访问。逐内容、业务、部署和C/U明细均保留，不只挑获益案例。

## 局部影响分析的明确限制

原60个数值诊断全部达到分类求解门，但24个真配或组级方向中参数差分23项、源内留出CE导数22项、源训练CE导数13项未通过。Hessian与线性系统正确、驻点偏移门通过，不等于epsilon为0.01和0.02已足够接近无穷小扰动。

因此I、I_C、I_U及源内容贡献只属于未通过局部导数精度验收的回顾性近似。它们没有进入优化、模型选择、beta选择或数据删除，不能用其符号证明训练机制原因。当前正式60基座也没有独立的有限差分精度通过结论。

![未验收近似与实际small损失](figures/unvalidated-local-vs-small-ce.png)

源内容分解的梯度及线性系统作用已数值验证可加，每角色24源内容可拆为72部署内容项。局部贡献可加不等于有限F1可加，更不能据此将某内容认定为坏数据。

![未验收源内容贡献](figures/source-content-local-contributions.png)

## 计算与谱系

本次正式终点240个：新拟合199个，复用P-full的14个及G-full的27个；另外复用60个冻结S。此前先导新拟合60个，补映射11个，均分别登记，不混作正式候选。旧CT、JA、原failure、先导失败和暂停记录均保持原样。追加授权记录只允许固定有限干预，不将失败先导写成通过。

所有拟合及模型推理在{c['environment']['gpu']}、CUDA {c['environment']['cuda']}上执行，dtype为float64，禁止CPU回退。199新正式拟合单次耗时中位数{np.median(times):.3f}秒、90分位{np.quantile(times,.9):.3f}秒、最大{max(times):.3f}秒、拟合合计{sum(times):.3f}秒。图表、内容bootstrap和文件核验使用CPU，不属于模型推理CPU回退。

全部300个方法角色模型及训练方向先封存，再完成7200行真实post预测封存；此后才开启目标H标签。7200行是五臂乘60角色乘24访问，独立访问仍为480。目标U训练两侧和测试pre均未开放。

## 结论与停止范围

{conclusion}。应结合相对S与相对G两个对照分别判断：超过S不自动说明精确身份必要，超过G也不自动说明优于充分post参照。部署例外、CE与F1分歧和新增错误都不能被总体均值掩盖。

本轮补上了实际重新学习到真实post评价的有限干预环节，但没有完成高精度影响函数机制归因。不会自动增加beta、改eta、删除业务、重选checkpoint或开启C-half。若要把固定干预发展为部署方法，还需说明不利用目标测试标签的合法选择规则和独立验证范围。

## 文件与复现

代码在`eval/strongpost_training_intervention/`，运行根为`outputs/strongpost-training-intervention-20261009/run-01/`。原合同、追加授权、模型谱系、封存预测、六类CM、四项区间、错误翻转和未验收近似表均可追溯。

详见[详细附录](detailed-appendix-20261009.md)以及保留的[数值先导报告](numeric-pilot-report-20261009.md)。最终机器验收位于运行根`verification.json`，完成标志为`completion.json`；本报告本身不是替代独立验收的证据。
'''
        textfile(DOC/'detailed-report-20261009.md',body)
        appendix='# StrongPost有限训练干预详细附录\n\n## 逐业务分类\n\n'+md(classes)+'\n\n## 逐部署校准与未覆盖CE变化\n\n'+md(target_changes)
        appendix+='\n\n## 逐折角色指标\n\n'+md(pd.read_parquet(OUT/'scores/outer-folds.parquet'))
        appendix+='\n\n## 冻结选择与模型复用\n\n'+md(endpoints[['role_id','arm','beta','eta','t','reused','gradient_inf']])
        appendix+='\n\n## 未验收近似汇总\n\n仅描述，不用于新的检验或归因结论。\n\n'+md(local.groupby(['arm','scope'])[['I_unvalidated','actual_delta_CE']].mean().reset_index())
        textfile(DOC/'detailed-appendix-20261009.md',appendix+'\n')
        write(OUT/'manifests/report-complete.json',{'report_sha256':sha(DOC/'detailed-report-20261009.md'),
            'appendix_sha256':sha(DOC/'detailed-appendix-20261009.md'),'figures':6,
            'local_derivative_precision_validated':False,'new_fits':0})

if __name__=='__main__':run()
