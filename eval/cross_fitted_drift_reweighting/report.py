"""Evidence-first complete report, contract summary, model card and stop record."""
from common import *
def table(d):
    def fmt(v):
        if v is None or (isinstance(v,(float,np.floating)) and np.isnan(v)): return 'NA'
        if isinstance(v,(float,np.floating)): return f'{v:.6f}'
        return str(v).replace('|','\\|').replace('\n',' ')
    return '| '+' | '.join(map(str,d.columns))+' |\n| '+' | '.join(['---']*len(d.columns))+' |\n'+'\n'.join('| '+' | '.join(fmt(v) for v in row)+' |' for row in d.itertuples(index=False,name=None))
def main():
    c=start('report'); require(read(OUT/'verification.json')['pass'],'Verification before report')
    protocol=pd.read_parquet(OUT/'scores/protocol-summary.parquet'); overall=pd.read_parquet(OUT/'scores/overall-summary.parquet')
    comparisons=pd.read_parquet(OUT/'comparisons/main-contrasts.parquet'); classes=pd.read_parquet(OUT/'scores/class-summary.parquet')
    choices=pd.DataFrame(read(OUT/'selection/choices.json')); flips=pd.read_parquet(OUT/'scores/error-flip-summary.parquet')
    dirs=pd.concat([pd.read_parquet(OUT/f'weights/{s}-directions.parquet').assign(phase=s) for s in ['inner','outer']])
    ws=pd.concat([pd.read_parquet(OUT/f'weights/{s}-summary.parquet').assign(phase=s) for s in ['inner','outer']])
    opt=pd.concat([pd.read_parquet(OUT/f'manifests/{s}-optimizer.parquet').assign(phase=s) for s in ['inner','outer']])
    act=pd.read_parquet(OUT/'diagnostics/inner-base-activity.parquet'); changes=pd.read_parquet(OUT/'diagnostics/inner-candidate-changes.parquet')
    verify=read(OUT/'verification.json'); success=bool(comparisons.family_positive.all() and comparisons.iloc[0].point>=.01)
    rw4=overall[overall.arm=='RW4'].iloc[0]; rw1=overall[overall.arm=='RW1'].iloc[0]
    positive_choices=choices[choices.arm.isin(ARMS[2:])]; ratio_counts=positive_choices.groupby(['arm','setting']).size().rename('roles').reset_index()
    direction_summary=dirs.assign(hard=dirs.hard.fillna('tie')).groupby(['phase','protocol','arm','hard']).size().rename('roles').reset_index()
    gsummary=act[act.setting==4].groupby('arm')[['change_gradient_norm','CE_gradient_norm','L2_gradient_norm','base_residual_gradient_norm','change_CE_norm_ratio','change_L2_norm_ratio']].agg(['mean','min','max'])
    gsummary.columns=['_'.join(k) for k in gsummary.columns]; gsummary=gsummary.reset_index()
    activity_summary=opt.groupby(['phase','arm']).agg(fits=('iterations','size'),mean_iterations=('iterations','mean'),
      max_iterations=('iterations','max'),max_gradient=('max_gradient','max'),seconds=('seconds','sum'),
      mean_parameter_change=('weight_delta_norm','mean'),mean_logit_RMS=('centered_logit_RMS','mean'),
      max_probability_change=('probability_max_change','max'),training_class_changes=('training_class_changes','sum')).reset_index()
    wsummary=ws.groupby(['phase','arm','setting']).agg(vectors=('mean','size'),min_weight=('minimum','min'),max_weight=('maximum','max'),min_ESS=('ESS','min'),
      max_class_mean_error=('max_class_mean_error','max')).reset_index()
    cc=changes[(changes.arm.isin(ARMS[2:]))&(changes.setting>1)].groupby(['arm','setting']).agg(roles=('outer','size'),
      changed_validation_visits=('validation_prediction_changes','sum'),max_probability_change=('validation_probability_max_change','max')).reset_index()
    body=f'''# 交叉拟合漂移状态固定重加权实验完整报告

本轮在既定30内容、480访问和四个已见TCP代理部署上，检验由训练内OOF难度确定的固定权重能否改善未见内容业务分类。RW4四部署等权macro-F1为{rw4.equal_protocol_F1:.6f}，强post监督RW1为{rw1.equal_protocol_F1:.6f}，差值为{rw4.equal_protocol_F1-rw1.equal_protocol_F1:+.6f}。预登记完整成功条件{'通过' if success else '未通过'}，本轮按有限矩阵结项，不追加比值、保护系数、分组或网络搜索。

## 数据和任务

固定23566条排他TCP连接对，480访问，30内容，六业务，每内容每部署四次重复。SS、VLESS、Trojan、VMess各120访问。AnyTLS和Hy2未进入本轮；也没有解析新PCAP或引入新特征。特征为十种流级统计的96维访问内直方图，不输入IP、端口、SNI、URL字符串或数值协议身份。业务标签为domain × activity，内容ID仅用于整体分折与训练权重审计。

五折内容全局留出：同一内容在四部署的全部重复、两侧和内部连接处于同一个折。20个外层角色各24训练内容、96访问及6测试内容、24访问；80个内层角色各18训练内容、72访问及6验证内容、24访问。外层状态难度来自18内容源的4折OOF，内层来自12内容源的3折OOF，两种训练范围的困难方向分别计算，禁止复用外层方向到内层。

已登记pair、session、logical、carrier、epoch proxy和content未跨折，不等于拥有所有TCP连接重用的普适证明。当前模型按已知部署路由至四个独立分类器；它不是一个协议未知的统一模型，也不是留一协议泛化。

## 对照与训练权限

| 臂 | 状态或模型 | 本轮变化 |
| --- | --- | --- |
| RW0 | 原post逻辑回归 | 精确复用，基础L2=0.001 |
| RW1 | 公平强L2 post监督 | t=0/0.25/1/4，复用原模型并精确重放选择 |
| RW2 | OOF post CE两组 | 确定方向后固定强调困难组 |
| RW3 | 匿名内容组漂移状态 | 不使用精确访问对应的核与查询，使用相同重加权结构 |
| RW4 | 真实访问对应漂移状态 | 同一核/状态来源的训练OOF困难方向，使用相同重加权结构 |

三种状态保持原DSR定义和每类各半的软质量，不重估阈值、核或CF教师。OOF CE由未见该查询内容的源post模型生成。业务标签参与OOF风险均值和权重构造，所以这是任务感知方法，不能称完全无标签。方向选取最大OOF组风险本身也没有独立验证资格。

每个角色只有一个全业务共同方向：高组减低组OOF CE超过1e-12 nat取高组，低于−1e-12取低组，否则均匀权重。并列容差是数值规则，不是统计显著性。固定r∈{{1,1.5,2,4}}，w=2/(1+r)·[1+(r−1)γhard]；权重始终正、每类和全体平均1。所有真实post和标签仍用于训练，但其相对损失质量改变，不应说原CE完全不变。

新目标为 mean(w·CE)+0.0005||W||²+0.1·mean(||P6(logit−base_logit)||²)/5。保护项不加权，L2只惩罚最终W，不惩罚bias或DeltaW。源标准化坐标来自原未加权训练post，测试不重新标准化。基座固定，DeltaW/Delta b零初始化，合并后仍为582参数的六类逻辑回归。这是固定权重凸优化，不是新的Group DRO、互信息最大化或生成式分类器。

r=1和严格均匀权重精确别名原模型，不重新优化以制造数值差异。CUDA float64全批量LBFGS至多500迭代，strong Wolfe，梯度容差1e-9、变化容差1e-12；工程门为有限、目标不升、最终最大梯度≤1e-5且未耗尽迭代预算。原CE、F1或预测类别不改变，不是工程失败条件。

## 执行与选择

源核和CF模型新增拟合数为0。实际新分类优化数为{verify['actual_new_fits']}，预算上界780。内层32640行概率，外层2400行概率，全部训练与推理使用CUDA float64，无CPU回退。空优化表从登记时即保留完整schema。

内层将四个验证折合成96访问、24内容，按完整六类macro-F1选r，1e-12并列取最小值；不以CE、Brier或预测变化破平局。RW1与原KSR1全部20项选择完全一致。80项选择封存后才计算外层60个新困难方向与选定权重。

{table(ratio_counts)}

实际非均匀优化及训练干预如下，未拟合的精确别名不冒充优化任务：

{table(activity_summary)}

## 完整分类结果

主终点是先分别重算各部署120访问的六类macro-F1再等权平均，不是平均外层折F1，也不是将480访问混算。

{table(overall[['arm','equal_protocol_F1','worst_protocol_F1','mean_CE','mean_Brier','pooled_F1']])}

{table(protocol)}

## 内容簇区间和正式判定

复用原DSR的内容顺序及seed=20261005的10000次六业务分层内容簇索引。每类5内容抽5次，四次重复与全部连接跟随内容，四部署和各臂共享索引，重算混淆矩阵。三项正式比较报告95%及Bonferroni 98.333333%边际区间。

{table(comparisons)}

完整条件要求三个校正下界都>0且RW4减RW1点估计至少0.01。本轮判定为{'通过' if success else '未通过'}。所有区间条件于固定已选择模型、方向、权重和r，不重新拟合；不覆盖方向选择、核估计、选参和回顾性方法开发的不确定性。30内容已被反复分析，不能视为外部盲测。预测相同产生的零宽区间只代表别名，不构成独立等效性证据。逐部署12项普通区间仅作探索性，完整文件为comparisons/protocol-descriptive.parquet。

## 方向和权重结构

{table(direction_summary)}

{table(wsummary)}

权重正值范围0.4至1.6。r≤4时访问ESS理论下界为n·25/34，最大内容类内份额的上界为外层0.4、内层0.533333。这些由既定权重和四重复推导，不是科学成败阈值。所有实际质量、有效内容数、CF来源方向差及RW4相对RW2/RW3的软重叠均在weights和diagnostics中保存，没有裁剪、删除内容或事后按业务定向。

## 干预尺度和预测变化

r=4基座处的梯度诊断如下。change指mean((w−1)·CE)的梯度；同时报告其相对原CE和L2的尺度，不仅用已近乎抵消的基座总梯度作为分母。零范数比值与余弦标NA。单独L2只求W梯度，bias明确为零，其他项保持严格梯度检查。

{table(gsummary)}

全部正比值内层候选的验证改变如下；同一访问出现在多个候选中，这些计数不能当作独立样本数：

{table(cc)}

最终RW4相对四臂的修复错误与新增错误均保留：

{table(flips)}

逐访问、内容和业务翻转分别见scores/error-flip-visits.parquet、content-flips.parquet、business-flips.parquet。预测移动仅证明训练干预实际发生，不证明分类增量；主比较的统计判定必须独立成立。

## 六业务分项

每个部署每类支持均为20。以下完整保留所有臂，不只展示收益最大的业务。

'''
    for p in PROTOCOLS:
        body+='### '+p+'\n\n'+table(classes[classes.protocol==p].pivot(index='business',columns='arm',values='F1').reindex(index=LABELS,columns=ARMS).reset_index())+'\n\n'
    states=pd.read_parquet(OUT/'diagnostics/fixed-test-state-summary.parquet')
    body+='## 固定测试状态附录\n\n测试状态复用原DSR4训练阈值和已经封存的离线状态，所有新臂使用相同低高组。仅在新预测封存后读取，不按新测试CE选择方向或重算中位数。高意外状态不是本轮OOF困难方向；四个18内容核平均的测试分数与训练单核OOF分数仍有观测差异，无六类完整支持时F1标NA。\n\n'+table(states)+'\n\n'
    body+='## 工程核验与使用边界\n\n'+table(pd.DataFrame([verify]))+'\n\n'
    body+='原DSR原始契约、L2诊断修复的修订链与报表适配封存均保留；本轮未修改旧实验文件。方向、权重、原模型别名、新模型逐项目标和全部内外层概率已重载重放。读取白名单、源码SHA和台账属于审计，不是操作系统安全沙箱。\n\n推理仅接收opaque访问ID及96维post直方图，输出六类概率；不接收pre、标签、内容、权重、核或选择台账。测试pre仅进入事后固定状态附录。本轮不验证外部DIRECT、新协议、新日期、在线无索引分段、语义解耦或精确对应普遍必要性。\n\n'
    body+='## 图表与复现\n\n'+''.join(f'![{name}](../../outputs/cross-fitted-drift-reweighting-20261006/run-01/figures/{file}.png)\n\n' for name,file in [('Classification and contrasts','outcomes'),('Directions weights and gradients','interventions'),('Classes and error flips','classes-and-flips')])
    body+='源码位于eval/cross_fitted_drift_reweighting，固定契约及来源位于outputs/cross-fitted-drift-reweighting-20261006/run-01/manifests。README给出完整顺序。所有候选、权重、概率和统计表均保留；计划RW00至RW29结项，无自动追加搜索。\n'
    DOC.mkdir(parents=True,exist_ok=True); (DOC/'complete-report-20261006.md').write_text(body,encoding='utf-8')
    (DOC/'experiment-contract-summary-20261006.md').write_text('# 交叉拟合固定重加权实验契约摘要\n\n固定四部署、30内容、480访问、六类、96维直方图和原内容折。内层方向来自12内容源OOF，外层来自18内容源OOF；选择封存后才构造外层新权重。\n\n'+table(pd.DataFrame([{'ratios':str(RATIOS),'eta':ETA,'rho':.001,'direction_eps':EPS,'parameters':582,'max_new_fits':780,'actual_new_fits':verify['actual_new_fits'],'bootstrap':10000,'formal_family':3}]))+'\n\nRW0/RW1只读精确复用。RW2/3/4同一目标与预算，标签感知方向，每类与全体权重均值1。r=1别名。训练、数值构造和推理CUDA float64。主判定三项校正下界正且RW4减RW1≥0.01；区间条件于固定选择。机器契约已在方向/权重/拟合前封存，见manifests/experiment-contract.json。\n',encoding='utf-8')
    (DOC/'model-card-20261006.md').write_text('# 固定重加权post逻辑回归模型卡\n\n四个已知部署独立路由，六类线性softmax，96维post直方图，582参数。最终导出模型只有mu/scale/W/bias。输入仅访问ID和post直方图；不需要pre、机制核、状态或训练权重。\n\n适用范围为本队列已见SS/VLESS/Trojan/VMess部署的未见内容评价。模型使用全部训练真实post标签，漂移只改变固定训练损失权重，不节省标签或post数据。本轮预登记成功条件'+('通过' if success else '未通过')+'。不声称未知部署、跨日期、外部DIRECT或在线单flow识别能力。\n',encoding='utf-8')
    write(OUT/'completion.json',{'stage':'RW29','complete':True,'full_claim_supported':success,'stop':True,
      'automatic_more_search_authorized':False,'scientific_negative_not_engineering_failure':True,
      'docs_sha256':{rel(p):sha(p) for p in DOC.glob('*.md')},'time_unix':time.time()})
    finish('RW28-RW29',complete=True,full_claim_supported=success,stop=True)
if __name__=='__main__': main()
