"""Render only sealed results; never turn a diagnostic into a business gate."""
from common import *

def table(d,cols=None):
    d=d if cols is None else d[cols]
    def val(v):return f'{v:.6f}' if isinstance(v,(float,np.floating)) else str(v)
    return '| '+' | '.join(d.columns)+' |\n| '+' | '.join(['---']*len(d.columns))+' |\n'+'\n'.join('| '+' | '.join(val(v) for v in row)+' |' for row in d.itertuples(index=False,name=None))

def report():
    point=pd.read_parquet(OUT/'scores/pooled.parquet');targets=pd.read_parquet(OUT/'scores/targets.parquet')
    seeds=pd.read_parquet(OUT/'scores/seed-means.parquet');chosen=pd.read_parquet(OUT/'selections/chosen.parquet')
    primary=read(OUT/'comparisons/primary.json');guard=read(OUT/'comparisons/C-cost-guard.json');budget=read(OUT/'budget.json')
    flips=pd.read_parquet(OUT/'scores/error-flips.parquet')
    ft=flips.groupby(['reference','scope'])[['repaired','introduced','shared_wrong','changed']].sum().reset_index()
    recipe=chosen.groupby(['arm','id','lam','lr','gamma']).size().rename('outer_roles').reset_index()
    contrasts=pd.DataFrame([dict(reference=c['reference'],delta_F1_U=c['delta_F1_U'],CI_95=c['CI_95'],CI_98_75=c['CI_98_75'],positive=c['positive_increment']) for c in primary['comparisons']])
    text=f'''# JAT1 完整联合适配实验报告

本轮已完成。主候选固定为JP，不按结果切换为其他臂；整体效力、精确身份归因和冻结方式比较分别解释。

## 1 任务、数据与权限

Extend四TCP部署SS/VLESS/Trojan/VMess，480次访问、30全局内容、六业务、每内容每部署四重复；96维访问直方图。全部五折内容留出，60外层角色、720源内任务。每外层三源库288访问和目标C64访问可训练；目标U32次训练访问两侧均禁止，H24访问仅在全模型封存后开放post。没有新增PCAP解析或采集，没有将IP、端口、SNI、协议或内容编号送入数值模型。

每内层480带权计算行、192真实训练访问；每外层928计算行、352真实访问。四槽源post/CORAL/P映射pre/C-post质量分别1/3、0.3、1/30、1/3；每业务质量1/6。匿名映射槽不接受猜测的逐访问pre教师目标。共同P-small材料已用过真配映射，JC不等于整个训练管线完全没有pre或精确关系。

## 2 模型与公平对照

模型logits = Wx + VG(x) + c，G=96→16→8 ReLU瓶颈，总2318参数。W/c初始化P-small，V=0；W/V/c/G共同训练，无0.1输出系数、无正交或位置硬保护。输入和完整头float64，G/教师float32，CE/MSE标量及显式L2 float64，训练与推理均CUDA，无AMP/TF32。

JC无新增关联损失；JP真配8维固定教师目标；JG同内容同部署四重复中心；FR前1000步与相应JP/JC相同，后1000步冻结G继续完整头。MX00/01/10和JP在所选JP共同中点构成冻结矩阵，不另选H赢家。原旧A3也联合更新G和残差头，因此不能声称本轮是第一次联合训练或仅靠解冻扩大函数类。

固定2000步Adam，每模型独立clip=5。每神经方法六候选，内层seed20261014，全部12合法伪任务参与每角色选择；先最大化伪部署等权完整六分类矩阵的U-F1，再按CE和登记tie规则。没有局部F1、C代价或MSE资格门。外层seed为20261014/15/16，所有方法同预算。教师1000步固定训练政策，不搜索教师。

## 3 汇总结果

{table(point,['arm','F1_U','F1_C','F1_all','CE_U','CE','Brier_U','Brier','worst_deployment_F1_U'])}

## 4 预先登记的四项主比较

{table(contrasts)}

业务分层共享内容簇bootstrap10000次，seed20261016；四比较家族Bonferroni区间98.75%。每单元先汇总五折完整6×6矩阵，再对部署/遮蔽/seed等权；没有把U变成二分类，也没有平均seed概率形成集成。区间条件于已拟合模型和所选配置，不包含重新训练/选参变异。

## 5 每部署及逐seed

{table(targets,['arm','target','F1_U','F1_C','F1_all','CE_U','Brier_U'])}

{table(seeds,['arm','seed','F1_U','F1_C','CE_U','Brier_U'])}

## 6 选参和实际关联使用

{table(recipe)}

λ=0角色按逻辑别名复用同配方JC；这些角色没有新增目标文件读取，不声称使用了新增配对监督。详细候选分数和每伪部署结果见outputs下selections目录。

## 7 C代价与错误翻转

总体C-F1差JP−B0={guard['overall_delta']:.6f}，总体1个百分点、每部署2个百分点实践范围是否满足：{guard['passed']}。这不是选择资格或H条件回退。

{table(pd.DataFrame(guard['targets']))}

{table(ft)}

翻转计数包括重复角色、seed，不是独立内容数。逐访问真实类概率、共同错误置信度、CE/Brier及逐内容结果完整保存在scores目录；概率损害不得由F1改善掩盖。本轮未温度重校准。

## 8 工程、成本及复核

已采用32模型并发、8 CUDA streams、CUDA Graph，保持独立参数/梯度/clip/Adam。BMM数值不合格版本保留，未用于正式训练。P1固定12任务240物理路径计入14400源内路径，未读取query或H/U；另列928行工程计时及教师。全部源内模型→预测→标签选择，全部外层模型→H-post预测→H标签评分的全局封存屏障保持。

训练活动累计{budget['used_seconds']/3600:.3f}小时，预算24小时；累计登记物理训练片段{budget['fit_count']}，逐模型更新{budget['model_updates']}。源内选择、外层主路径、warm、教师和冻结续训分项均在budget.json中，不能称“只训练720个网络”。墙钟IO/散列/汇总与活动时间分开。

独立目标/头部logits、完整F1与bootstrap重放已核对；历史注册源文件散列已复核，旧停止、资格和业务结果未覆盖。导出包只接收post96及固定模型参数，不接收pre、标签、协议、内容或教师目标。

## 9 解释边界与结项

此为同批历史数据的完整内部验证，H已被多轮历史研究，不是新盲测或跨日期外部验证。没有证明共享carrier、未见配置/协议、真实DIRECT→proxy或无索引在线流量识别；继承原索引窗口和排他TCP资格，不能声称完成全局物理连接无泄漏重建。

JP−B0与JP−JC决定整体效力；JP−JG决定新增精确目标监督的归因；JP−FR及匹配矩阵帮助解释训练程序。训练MSE下降不是未见内容恢复能力，也不自动证明分类收益。冻结矩阵非加性仅是描述量，不是物理因果协同或互信息。

完成本次评价后结项，不自动新增GAN、教师、宽度、lambda网格或部署子集。若区间跨零，报告当前可支持范围而不声称等效；若概率或C代价明显，限定方法用途。
'''
    p=writable(DOC/'complete-report.md');require(not p.exists(),'Report already exists');p.write_text(text,encoding='utf-8')
    p=writable(DOC/'model-card.md');p.write_text('# JAT1模型卡\n\n'+
        '接口：post96→logits6；角色专用，不输入协议身份，但按登记角色使用。导出含mu/scale/W/V/c/G。\n\n'+
        '训练仅允许三源库与目标C，目标U与H-pre禁止；本轮是同批内部验证，不能声明外部或未见协议泛化。\n',encoding='utf-8')
