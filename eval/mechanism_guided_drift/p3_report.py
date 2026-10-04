"""Frozen results and model card, not an optimization loop."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from p3_common import *


def table(f):return f.to_markdown(index=False,floatfmt='.6f')


def main():
    audit=read(OUT/'independent-verification.json');assert audit['passed']
    ag=pd.read_parquet(OUT/'aggregate-seed-metrics.parquet');detail=pd.read_parquet(OUT/'per-protocol-seed-metrics.parquet')
    contrasts=pd.read_parquet(OUT/'primary-contrasts.parquet');classes=pd.read_parquet(OUT/'per-class-seed-metrics.parquet')
    params=pd.read_parquet(OUT/'center-parameters.parquet');dist=pd.read_parquet(OUT/'distribution-metrics.parquet')
    errors=pd.read_parquet(OUT/'error-transitions.parquet');loco=pd.read_parquet(OUT/'loco-target-metrics.parquet')
    summary=ag.groupby('arm').agg(F1=('protocol_equal_F1','mean'),F1_min_seed=('protocol_equal_F1','min'),
        F1_max_seed=('protocol_equal_F1','max'),worst_F1=('worst_protocol_F1','mean'),CE_bits=('CE_bits','mean'),Brier=('Brier','mean')).reset_index()
    per=detail.groupby(['arm','protocol'])[['F1','accuracy','CE_bits','Brier']].mean().reset_index()
    changes=per.pivot(index='protocol',columns='arm',values='F1')
    change_table=pd.DataFrame({'protocol':changes.index,'D2_minus_D0':changes.D2_pair-changes.D0_pair,
        'D2_minus_D1':changes.D2_pair-changes.D1_pair,'D2_minus_M0':changes.D2_pair-changes.M0}).reset_index(drop=True)
    d=dist.groupby(['arm','feature'])[['MAE','bias','coverage95','interval_width']].mean().reset_index()
    p=params[params.arm.str.startswith('D2')].groupby(['arm','protocol']).agg(
        beta_up_min=('beta_up','min'),beta_up_median=('beta_up','median'),beta_up_max=('beta_up','max'),
        beta_down_min=('beta_down','min'),beta_down_median=('beta_down','median'),beta_down_max=('beta_down','max'),
        column_space_error_min=('center_column_space_relative_error','min'),column_space_error_max=('center_column_space_relative_error','max')).reset_index()
    err=errors.groupby('reference').agg(repaired=('repaired','sum'),new_errors=('new_errors','sum')).reset_index()
    pc=classes.groupby(['arm','class'])[['precision','recall','F1']].mean().reset_index()
    own=loco.groupby('arm').own_target_latent_MSE.mean().reset_index()
    figdir=OUT/'figures';figdir.mkdir(exist_ok=True)
    fig,axes=plt.subplots(1,2,figsize=(12,4),layout='constrained')
    matrix=per.pivot(index='protocol',columns='arm',values='F1')[ARMS]
    for arm in ARMS:axes[0].plot(matrix.index,matrix[arm],marker='o',label=arm)
    axes[0].set_ylim(0,1);axes[0].set_ylabel('Six-class macro F1');axes[0].set_title('OOF protocol results, mean of three seeds');axes[0].legend(fontsize=8)
    x=np.arange(len(contrasts));primary=contrasts.primary.to_numpy()
    lo=np.where(primary,contrasts.adjusted_low,contrasts.low95);hi=np.where(primary,contrasts.adjusted_high,contrasts.high95)
    axes[1].errorbar(x,contrasts.delta,yerr=[contrasts.delta-lo,hi-contrasts.delta],fmt='o',capsize=4)
    axes[1].axhline(0,color='gray',linestyle='--');axes[1].set_xticks(x,contrasts.contrast,rotation=25,ha='right')
    axes[1].set_ylabel('Protocol-equal macro F1 difference');axes[1].set_title('Four primary adjusted intervals; cyclic ordinary95')
    fig.savefig(figdir/'classification.png',dpi=180);plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(11,4),layout='constrained')
    for i,name in enumerate(['W_up','W_down']):
        z=dist[dist.feature.eq(name)].groupby(['protocol','arm']).MAE.mean().unstack()[list(GENERATORS)]
        for arm in GENERATORS:axes[i].plot(z.index,z[arm],marker='o',label=arm)
        axes[i].set_yscale('log');axes[i].set_ylabel('Bytes MAE');axes[i].set_title(name+' query prediction (training only)');axes[i].legend(fontsize=7)
    fig.savefig(figdir/'distribution.png',dpi=180);plt.close(fig)
    tests=[]
    for _,r in contrasts.iterrows():
        if r.primary:
            verdict='支持正向增量' if r.adjusted_low>0 else ('支持负向差异' if r.adjusted_high<0 else '区间跨零，未建立方向性增量')
            tests.append(f"- `{r.contrast}`：点差{r.delta:+.6f}，校正区间[{r.adjusted_low:+.6f}, {r.adjusted_high:+.6f}]，{verdict}。")
    replay=read(OUT/'classifier-baseline-replay.json')
    document=f'''# Extend 机制启发漂移中心正式实验报告

日期：2026-10-04。P3按G2批准的唯一候选完成，没有新增采集、扩模型或事后改中心。本轮检验的是pre实体密度启发的经验中心，在相同增强输入的通用Ridge之外是否有分布与业务增量；不是验证精确协议开销。

## 主要结论

四项主要比较均按预登记家族报告：

{chr(10).join(tests)}

结果未按测试F1筛选协议、内容、seed、checkpoint或公式。若区间跨零，不解释为等效；即使点估计较高，也不声称机制已识别。cyclic为次要比较。完整结果保留各部署退化和负结果，不自动开启优化分支。

本轮没有达到四项主要比较全部建立正向增量的标准。D2_pair总体F1为0.728858，D0为0.724772，D1为0.722704，M0为0.715930。分别约提高0.41、0.62和1.29个百分点，但三项校正区间跨零。相对group提高约6.23个百分点且校正区间为正；相对cyclic约7.79个百分点为预登记次要结果。这里支持的是本生成机制下真配优于较粗控制，不能将新中心超过充分post监督写成已验证成果。

生成误差同样没有全面改善：D2_pair相对同输入D1在五协议上行MAE均降低，下行在AnyTLS/Trojan降低、VLESS近似，但SS/VMess明显增大。group/cyclic下行MAE达到百万字节级，不能把高覆盖率当作高精度，宽残差区间也可能覆盖真实值。原始中心误差、样本覆盖与业务决策是不同终点，不能用一个指标代替另一个。

## 数据与训练资源

五个已见部署SS、VLESS、Trojan、VMess、AnyTLS，600访问、30内容、六业务、每内容每协议四重复。Hy2、T分类、留一协议E2均未执行。同内容在所有部署、全部重复、两侧、内部实体全球同折；每外层480访问训练、120测试。生成器100个job，各72访问/18内容拟合，24访问/6内容只读pre查询；LOCO17内容/68访问，9000个生产内层任务，加500个最终拟合共9500个Ridge。

六业务沿用GitHub仓库浏览、YouTube搜索、Bing搜索、Wikipedia文章、MDN文档、YouTube视频播放。W是登记访问窗口内正TCP/UDP传输载荷总字节，P是正载荷事件数，R是本窗口全局方向段数；含重复传输，不是唯一TCP字节。R不是原stream级FR，本轮未更换其定义或引入记录瞬时点排序。

八个pre代理分别为上下行log1p(正载荷实体数)、log1p(载荷长度q50)、log1p(载荷长度q90)、长度≤256事件比例。q50/q90只用对应方向正载荷pre事件，空方向0并有真实空方向依据；无缓存则停止。N通过round(expm1(log实体数))恢复整数，不输入实体ID。阈值256预先登记，不是Vision或握手状态规则。proxy列在标准化前已是上述log/ratio，不对它们再log1p；原六量仍log1p后共同标准化。

E1全部训练业务都有真实post。M0使用相同480真实post；其余臂另使用同范围训练pre与对应层级信息，不是旧跨业务C/U缺post情景，也没有减少业务标签的证据。D0有42参数，D1有90，D2有92；八个增强pre代理给D1/D2相同。因此D2−D1隔离输入信息增量，但两者仍有2参数及正则先验差别，不能写成严格完全同参数因果实验。

| 臂 | 辅助数据 | 原始中心 | 对应关系 |
|---|---|---|---|
| M0 | 真实post重复槽 | 不适用 | 无生成 |
| D0_pair | 旧六量Ridge合成post | 原pre | 同次 |
| D1_pair | 同八代理通用Ridge合成post | 原pre | 同次 |
| D2_pair | 启动中心＋剩余Ridge合成post | pre字节＋估计beta乘pre实体数 | 同次 |
| D2_group | 同结构合成post | 同内容匿名目标估计beta | 组级 |
| D2_cyclic | 同结构合成post | 固定donor估计beta | 同内容跨重复 |

每访问8视图，原整向量LOCO残差，不改池采样机制。group池288、paired/cyclic72。group原始字节均值仅用于beta，latent均值用于剩余目标；残差采用组内Cartesian，匿名包无session/repetition，没有暗中复原同次访问。

## 模型和 CUDA 配置

启动系数非负，beta=sum N*(目标W−preW)/sumN²，零分母0。固定整数增量floor(beta*N+0.5)，P/R保持pre；旧65527P容量超界停止，不裁剪。中心经旧phi编码，剩余回归保留原pre phi尺度及alpha1、截距不惩罚。所有内层重新估计beta、输入均值/尺度和Ridge。

分类器仍6→32→6 ReLU，422参数；90分类器=六臂×五折×三seed20260918/19/20，1000步Adam、lr0.001、L2权重5e-5。损失相同真实/辅助两槽平均CE+L2，M0辅助重复真实post；各seed同初始化、主槽及视图调度。18独立头并行，不共享参数。回归/编码/生成CUDA float64，分类训练及测试CUDA float32，关闭TF32；CPU只文件、统计及绘图。分类器仅六量post输入，不读pre、八代理、协议配置/身份或地址类信息。没有早停和测试标准化。

## 业务详细结果

以下F1/最差部署F1是逐seed结果再平均，不是所有预测混池后选择高分。

{table(summary)}

逐seed：

{table(ag)}

逐协议三seed均值：

{table(per)}

相对参照的逐协议F1点差如下，仅为描述，没有另行做部署子家族显著性。D2相对D0在SS和Trojan退化；相对M0在VMess退化。最差协议的逐seed平均F1从D0的0.652853降至D2的0.646888，不能用总体点提升掩盖代价。

{table(change_table)}

## 内容簇区间和错误转移

完整六类macroF1，由混淆矩阵计算。10,000次业务分层内容bootstrap，各业务5内容，跨协议、seed和臂共用抽样；bootstrap seed20260928。四项主比较Bonferroni分位0.00625/0.99375，普通95%也同时保存；cyclic只普通95%。区间条件于固定模型，不含新重训练、外部日期或配置验证。

{table(contrasts)}

D2_pair相对各参照的错误修复和新增错误计数如下，包含三seed重复，每seed600访问；不是1800次独立访问。内容/协议/seed明细见error-transitions.parquet。

{table(err)}

逐类结果为部署、seed等权描述，不用其结果回头删业务：

{table(pc)}

## 生成分布与中心结构

以下使用训练query内容的真实post，只有全部生成及业务预测冻结后的独立scorer读取。查询post从未在本job生成器/LOCO中心、尺度或残差拟合中使用，也不用于选择方法。各fold训练区重叠，合并均值是描述，不是独立验证。

{table(d)}

MAE/偏差及区间宽度为原数值单位，coverage95为完整经验残差池映射后逐坐标2.5/97.5分位覆盖，不是多维联合95%或正确概率。遍历池用于离线分布诊断，不增加分类器八视图预算。预测中心使用旧合法解码器；低分布误差不保证决策边界保持。

下表为各训练job系数及中心位移对增强设计矩阵列空间的投影残差范围。系数以字节/pre实体为经验单位，不是cipher/tag/TLS K。列空间误差小可表示某些情况下近重参数化；alpha1不变时中心移位仍可能改变正则先验，不能仅凭有源码动机认定新增机制信息。

{table(p)}

LOCO自身目标latent MSE：

{table(own)}

group/cyclic与paired监督目标不同，不能直接按上述自身目标MSE排名恢复同次访问的能力；业务与query真实post比较才有共同目标。

## 工程复现与隔离审计

独立检查通过：500生成任务、9500生产Ridge、90分类器、10800条post-only预测，全部生成满足原W必要可行域；group匿名置换不变、全部5700个D2中心估计范围容量通过。D0全部100job的残差池、三seed整数样本及donor索引精确复现旧结果。分类基线M0/D0在新18头批处理与原15头结果的最大概率差为{replay['max_probability_difference']:.9g}，决策变化{replay['decision_changes']}，只在新预测封存后核对，不以旧成绩选checkpoint。

独立数值检查还确认D1_pair与D2_pair的抽样索引、残差前四坐标，以及合成P/R完全相同；该中心改动只改变字节坐标，没有暗中更换方向段或事件生成。beta虽然以“启动中心”命名，当前捕获未定位独立启动阶段，这仍然是经验密度先验。

各臂同seed初始化及调度哈希一致；原角色、源代码、缓存与旧输出哈希保持，未覆盖历史实验。权限包/校验是软件隔离，不是OS物理沙箱。推理只读test_post，标签仅评分后读取；没有test_pre包。沿用P2注册实体身份资格，历史5例SYN未观察及预检Trojan摘要曝光例外保留，不能声明任意未观测flow都已数学证明无泄漏。数据已反复研究，非外部盲测。

## 结论范围和停止

本轮最多支持指定已见五部署、未见内容E1下该一次经验中心的分布/业务用途。它不支持精确协议开销、真实协议会话生成、六协议统一分类、未见部署泛化、直连流量替换、在线无索引分段或减少业务标签。N是正载荷pre实体计数，不是新建carrier；AnyTLS日志和未观测padding/QUIC状态都未作为输入。独立仪器对应关系是测量基础，加入生成目标后的额外价值须由对应对照单独判断。

本轮在这里冻结，不因某协议或某个对照更高分而扩大beta/残差池、阈值或网络。后续方向需另定方案和授权。

## 图与复现

![分类和固定家族区间](../../outputs/mechanism-guided-drift-20261003/experiment/run-01/figures/classification.png)

![训练query分布误差](../../outputs/mechanism-guided-drift-20261003/experiment/run-01/figures/distribution.png)

完整契约见experiment-contract.md，代码在eval/mechanism_guided_drift/p3_*.py。运行顺序prepare→engineering→run generate/train/infer→score_adapter→verify→report；每步门控、源哈希、模型/残差/checkpoint、逐访问预测、内容bootstrap和审计保存于独立experiment/run-01，旧输出只读。评分遇到NumPy整数JSON序列化错误，仅以输出边界等值标量适配器修复，封存score源码、模型、预测、区间公式及比较家族保持不改；修复另存hash台账。文档按写作技能区分实测、候选假设及未验证外推，没有将经验收益改写为源码机制证明。
'''
    (DOC/'formal-results.md').write_text(document,encoding='utf-8')
    card='''# 机制启发中心模型卡

用途：Extend五个已见代理部署的六业务、未见内容访问级post分类。W含正TCP/UDP观测及重复传输；R是窗口全局方向段，不是原stream FR。非真实协议流量生成器，非未见部署模型。

训练：480真实post/外层折；生成臂使用同范围pre及各自允许的post对应层级。D0/D1/D2参数42/90/92；业务MLP422参数，三seed，1000CUDA步。N为pre正载荷实体数，不是在线可观测新建carrier状态；八代理只供生成器，不供post业务分类器。

推理：冻结训练post标准化、六量post→MLP。输入不含地址/端口/SNI、协议身份、测试pre、content或session ID。

限制：离线资格及访问窗口依赖采集关联；无索引在线分段未验证，Hy2/T/E2未执行。保留5例无SYN的仪器条件及回顾性研究边界。必要合法摘要不保证实际可生成TCP会话。统计区间条件于固定模型，不是外部验证。

完整结果与正负比较见formal-results.md；不从三seed挑最佳，不以某业务退化为理由删类或重新选择中心。
'''
    (DOC/'model-card.md').write_text(card,encoding='utf-8')
    write(OUT/'report-manifest.json',{'report_sha256':file_hash(DOC/'formal-results.md'),'model_card_sha256':file_hash(DOC/'model-card.md'),
        'reporting_script_sha256':file_hash(Path(__file__)),'final_scope':'E1 W only','new_branch_after_results':False})
    print(summary.to_string(index=False));print(contrasts.to_string(index=False));print('formal report saved')


if __name__=='__main__':main()
