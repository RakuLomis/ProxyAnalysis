"""Generate factual closeout, retaining all directions and probability costs."""
from common import *

def table(df,columns=None):
    if columns is not None:df=df[columns]
    cols=list(df);lines=['| '+' | '.join(cols)+' |','| '+' | '.join(['---']*len(cols))+' |']
    for _,r in df.iterrows():
        vals=[]
        for c in cols:
            v=r[c]
            if isinstance(v,(float,np.floating)):v=f'{v:.6f}'
            vals.append(str(v).replace('|','/'))
        lines.append('| '+' | '.join(vals)+' |')
    return '\n'.join(lines)

def classify(ci):
    if ci[0]>0:return '家族区间为正'
    if ci[1]<0:return '家族区间为负'
    return '家族区间跨零'

def report():
    with stage('P6'):
        v=read(OUT/'verification.json');require(v['passed'],'Verification required')
        primary=read(OUT/'primary-comparisons.json');screen=read(OUT/'C-practical-screen.json')
        cover=read(OUT/'coverage.json');budget=read(OUT/'budget.json')
        overall=pd.read_parquet(OUT/'metrics-overall.parquet');dep=pd.read_parquet(OUT/'metrics-by-query-deployment.parquet')
        roles=pd.read_parquet(OUT/'metrics-by-role-group.parquet');business=pd.read_parquet(OUT/'metrics-by-business.parquet')
        endpoints=pd.read_parquet(OUT/'model-endpoints.parquet');flips=pd.read_parquet(OUT/'error-flips.parquet')
        geom=pd.read_parquet(OUT/'geometry-tests.parquet');affine=pd.read_parquet(OUT/'affine-replay.parquet')
        interaction=read(OUT/'interaction.json')
        completion=dict(program_complete=True,source_integrity_pass=True,numeric_pass=True,
           models_reused_PP=0,models_reused_GG=0,new_LR_fits=192,physical_fit_attempts=192,new_map_fits=0,logical_endpoints=192,
           unique_query_visits=384,query_contents=24,prediction_rows=4608,
           shape_effect_under_P_background=classify(primary['PP-PG']['F1_U_family_CI']),
           shape_effect_under_G_background=classify(primary['GP-GG']['F1_U_family_CI']),
           GP_minus_PP_point=primary['GP-PP']['point']['F1_U'],GP_minus_PP_family_interval=primary['GP-PP']['F1_U_family_CI'],
           C_practical_screen_passed=screen['passed'],actual_H_reads=0,actual_U_reads=0,
           formal_60_role_authorized=False,new_G_training_authorized=False,old_artifacts_changed=False,
           active_compute_seconds=budget['active_compute_seconds'],status='complete_source_inner_only')
        write(OUT/'completion.json',completion)
        rows=[]
        for k,x in primary.items():
            rows.append(dict(comparison=k,F1_U_delta=x['point']['F1_U'],CI95=str(x['F1_U_CI95']),family_CI=str(x['F1_U_family_CI']),
                 family_result=classify(x['F1_U_family_CI']),CE_U_delta=x['point']['CE_U'],Brier_U_delta=x['point']['Brier_U']))
        comp=pd.DataFrame(rows)
        summary=flips.groupby(['comparison','is_U','case'],as_index=False).agg(exposures=('visit_id','size'),CE_delta_sum=('CE_delta','sum'),Brier_delta_sum=('Brier_delta','sum'))
        totalfits=endpoints.fit_seconds.sum()
        body=f'''# 固定映射形状来源替换的业务归因实验报告

日期：2026-10-16。ST1 已完成固定48个源内任务、192个新LR和4608行预测；来源、数值、预测和统计重放均通过。未读取实际目标H/U，未训练新映射或表征网络。

## 核心结论

在P质量与位置背景下，PP相对PG的U业务F1差为 {primary['PP-PG']['point']['F1_U']*100:+.4f} 个百分点，{classify(primary['PP-PG']['F1_U_family_CI'])}。在G背景下，GP相对GG为 {primary['GP-GG']['point']['F1_U']*100:+.4f} 个百分点，{classify(primary['GP-GG']['F1_U_family_CI'])}。

新组合GP相对完整PP为 {primary['GP-PP']['point']['F1_U']*100:+.4f} 个百分点，{classify(primary['GP-PP']['F1_U_family_CI'])}。这三项分别回答形状的条件性分类作用和组合是否形成新增收益，不能相互替代。GP的C代价实践筛查为 **{'通过' if screen['passed'] else '未通过'}**。

## 数据和权限

沿用Extend的96维访问直方图及六个domain乘activity业务。仅使用outer f0训练范围内的24个内容，每业务4内容。四个源内留出折每次训练18内容、查询6内容；同内容的重复、两侧及内部连接整体分组，不随机拆flow。

每任务两个源部署提供144个真实访问的独立pre包与post包；伪目标C提供48个访问，共192次真实训练访问。pre144行不代表额外144次独立采集。伪目标U训练内容的两侧均禁止读取。480计算行只是四槽重复利用，不是480次独立访问。

| role_target组织角色 | query_deployment实际查询部署 | 源部署 |
| --- | --- | --- |
| shadowsocks | vless | trojan、vmess |
| vless | trojan | shadowsocks、vmess |
| trojan | vmess | shadowsocks、vless |
| vmess | shadowsocks | vless、trojan |

48任务为4角色乘3遮蔽组乘4内折。查询共1152次角色暴露、384次不同部署访问、24个不同内容。四臂产生4608行预测，不能将其当作4608份独立样本。role_target并非该行成绩所对应的流量部署。

G0遮蔽GitHub仓库和YouTube搜索，G1遮蔽Bing搜索和Wikipedia文章，G2遮蔽MDN文档和YouTube视频播放。每次仍是完整六分类。

## 固定方法与几何

P/G分别为冻结的真配与匿名组全仿射前向映射，不是旧的post恢复网络。十个直方图块全部参与，不按SD1的D单元筛选。前四块9箱、后六块10箱；固定分解为10维质量M、10维位置L、76维剩余形状R。

| 臂 | 质量及位置ML来源 | 形状R来源 |
| --- | --- | --- |
| PP | P | P |
| PG | P | G |
| GP | G | P |
| GG | G | G |

混合在原频率坐标中执行：d_raw=scale乘(zG减zP)，r为各块PR投影；PG=zP+r/scale，GP=zG减r/scale。PP/GG直接保留原辅助矩阵，不旋转重算。没有把位置锁回pre，没有截负、重新归一化或合法性筛选。混合后的负值和块质量偏离在view-diagnostics中全量记录，仅作描述。

原映射前向最大绝对重放误差 {affine.absolute_error.max():.3e}；几何恒等最大归一化误差 {geom.normalized_error.max():.3e}。非均匀尺度的负夹具能检出错误的标准化空间投影。

## 训练材料和数值配置

每任务依次为源post144行、CORAL144行、映射pre144行、C post48行，CE总质量分别1/3、0.3、1/30、1/3。逐行标签、质量和顺序直接继承原CT/JA槽；总质量1，各类别质量1/6，PP与既有纯classification张量精确一致。

模型为96到6的LR，原参数582个。目标是带权CE之和加0.0005乘(1+t)乘W平方和；bias不惩罚，不额外除以行数或类别数。eta/t逐角色继承，eta分布100四项、0.1三十六项、1四项、10四项；t分布4三十二项、0.25四项、0四项、1八项。

所有四臂统一零初始化，CUDA float64，可逆Cholesky预条件化，原v4 LBFGS，max_iter=2000、max_eval=10000、history=100、strong_wolfe。原坐标最大梯度门1e-5，目标及梯度重放门1e-10。未新增Newton精炼。旧纯PP模型因经过额外精炼，仅作训练目标兼容性审计，没有混入主结果。

实际192个物理拟合全部验收；工程先导16个已包含其中，无额外seed矩阵。独立原坐标梯度最大 {v['original_gradient_max']:.3e}，目标重放误差最大 {v['objective_max_error']:.3e}，梯度重放误差最大 {v['gradient_max_error']:.3e}。

## 完整总体结果

F1和概率误差均为比例或原单位，不是百分数；F1越高越好，CE和Brier越低越好。

{table(overall,['arm','F1_U','F1_C','F1_all','CE_U','CE_C','CE_all','Brier_U','Brier_C','Brier_all'])}

## 三项主要比较

先合并四内折，再为每个角色乘遮蔽组建立完整6乘6混淆矩阵。U/C F1提取自该矩阵中的两类或四类，保留其他业务造成的FP。12单元等权，不平均内折F1。差值均为候选减参照。

{table(comp)}

10000次六业务分层的共同内容簇bootstrap，每业务4内容有放回抽4；同内容次数在部署、遮蔽、重复和四臂共享。三项主F1差同时报告95%描述区间和Bonferroni 98.3333%家族区间。CE、Brier和交互只作95%描述区间，详见primary-comparisons.json。

交互I=PP减PG减GP加GG，点估计 {interaction['F1_U_point']:.6f}，95%区间 {interaction['CI95']}。这是训练材料的非加性，不是物理因果交互或互信息。

## 各查询部署结果

各部署先对三个遮蔽组等权；不是按role_target名称解释部署。

{table(dep,['role_target','query_deployment','arm','F1_U','F1_C','F1_all','CE_U','Brier_U'])}

最差部署完整保留：

{table(pd.read_parquet(OUT/'metrics-worst-deployment.parquet'))}

## 错误修复和概率代价

下表是角色暴露计数，同一次访问会跨遮蔽重复，不能作独立样本显著性。repair指候选正确而参照错误，new_error相反。CE和Brier列是该组差值之和。

{table(summary)}

共同错误的置信度及真类概率、逐内容修复与新增错误均保存在error-flips和shared-error-probability-cost。若分类点估计变好而概率代价变差，两者同时保留，本轮不追加温度校准。

## C业务实践筛查

GP减PP的F1_C总体差 {screen['GP_minus_PP_overall']*100:+.4f} 个百分点，上限允许损失1个百分点。各部署允许损失2个百分点：

{table(pd.DataFrame([dict(query_deployment=k,F1_C_delta=v,passed=v>=-.02) for k,v in screen['by_query_deployment'].items()]))}

筛查{'通过' if screen['passed'] else '未通过'}不等于统计非劣效，也不构成正式60角色评价授权。

## 独立核验和计算量

全部模型由封存训练槽独立复算原目标和解析梯度；推理用展开后的原始输入仿射式重放，最大概率差 {v['probability_max_error']:.3e}。完整混淆矩阵独立逐类别重建；全部10000次bootstrap用NumPy独立重算，最大指标差 {v['bootstrap_max_error']:.3e}，家族区间差 {v['family_interval_max_error']:.3e}。

累计活动预算记账 {budget['active_compute_seconds']:.2f} 秒，上限3600秒；其中求解器记录拟合时间合计 {totalfits:.2f} 秒，单模型中位数 {endpoints.fit_seconds.median():.3f} 秒，最大 {endpoints.fit_seconds.max():.3f} 秒。活动段包含必要的封装与槽加载开销，采用保守记账，不把它当作纯GPU核时间。源内优化、预测和统计均未扩大原拟合上限。

读取台账覆盖ST1受控适配器，不是操作系统级系统调用审计。重新核验全部 {v['registered_input_hashes']} 个登记输入散列，旧产物未变。顺序为训练槽封存、全部模型封存、全部预测封存、源内标签开放。实际H/U、query-pre、native、PCAP和含query的旧反馈包读取均为0。

## 适用范围和停止边界

本轮是同批历史数据上的固定材料干预。eta/t的旧选择已使用过相关内折内容；模型固定的bootstrap不能消除回顾性选择，也不是外部验证。源内24内容不能替代实际目标或异批次数据。

形状来源替换还可能改变两种映射输出的联合结构。因此某个混合臂的退化不能自动解释为所有形状无用，也不能仅凭一个正方向宣布精确身份具有普遍不可替代作用。SD1原来的停止记录不变；本轮没有恢复LOC保护，没有估计信息量，没有证明协议语义分解。

本轮到此结项。不会自动打开实际H/U、训练G/GAN、搜索子集或扩大分类器。是否进入新的全角色评价，需要另行确认。

## 产物索引

- 机器可读合同及封存：contract.json、seal.json、slots-complete.json、models-complete.json、predictions-complete.json、scores-complete.json。
- 来源与成员：source-bindings.parquet、role-membership.parquet、slot-row-ledger.parquet、compatibility.parquet、ledger.json。
- 几何与数值：geometry-synthetic-tests.parquet、geometry-tests.parquet、affine-replay.parquet、view-diagnostics.parquet、independent-endpoint-checks.parquet、verification.json。
- 分项结果：metrics-by-role-group.parquet、metrics-by-query-deployment.parquet、metrics-by-business.parquet、metrics-by-content.parquet、confusion-matrices.parquet。
- 比较和错误：primary-comparisons.json、interaction.json、bootstrap.npz、error-flips.parquet、error-flip-summary.parquet、shared-error-probability-cost.parquet、C-practical-screen.json。
- 完成状态：completion.json、budget.json、model-endpoints.parquet。

原子方案位于plan/ST1-shape-source-downstream-attribution-plan-20261016.md。全部结果路径相对于outputs/shape-source-task-attribution-20261016/run-01。
'''
        textfile(DOC/'complete-report.md',body)
        textfile(DOC/'results-interpretation.md',f'''# 固定映射形状来源的结果解释

ST1完成48个源内任务和192个统一政策新LR，未读取实际H/U。

{table(comp)}

PP减PG检验P背景下移除真配形状的影响；GP减GG检验G背景下加入真配形状的影响；GP减PP才是相对完整P-small的新增方法比较。结果分别为：{completion['shape_effect_under_P_background']}、{completion['shape_effect_under_G_background']}、{classify(primary['GP-PP']['F1_U_family_CI'])}。

GP的C业务代价筛查{'通过' if screen['passed'] else '未通过'}。区间跨零不表示等效，恢复预测优势不自动转化为分类贡献；形状作用还依赖ML背景和混合后的联合结构。所有区间条件于历史固定模型与同批内容，不构成独立外部验证。

本轮结项，不自动进入60角色实际目标评价。详细配置、各部署、错误翻转、概率代价和读取边界见complete-report.md。
''')
        seal(OUT/'reports-complete.json',[DOC/'complete-report.md',DOC/'results-interpretation.md',OUT/'completion.json'])
        progress('ST1_complete',**completion)
