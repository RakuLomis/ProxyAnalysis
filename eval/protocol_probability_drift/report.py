"""Render the complete frozen measurement report, not a classification claim."""
from pathlib import Path
import numpy as np
import pandas as pd
from common import ROOT, OUT, DOC, PROTOCOLS, FEATURES, read, write, relative, checkpoint, verify_sources

NAMES={'shadowsocks':'SS','vless':'VLESS','trojan':'Trojan','vmess':'VMess','anytls':'AnyTLS'}


def markdown(frame):
    def cell(v):
        if pd.isna(v): return 'NA'
        if isinstance(v,(bool,np.bool_)):return '是' if v else '否'
        if isinstance(v,(float,np.floating)):return f'{v:.6f}'
        return str(v).replace('|','\\|')
    headers=list(frame.columns)
    return '| '+' | '.join(headers)+' |\n| '+' | '.join(['---']*len(headers))+' |\n'+''.join(
           '| '+' | '.join(cell(v) for v in row)+' |\n' for row in frame.itertuples(index=False,name=None))


def means(frame,keys,metrics):
    rows=[]
    for key,g in frame.groupby(keys,sort=True):
        if not isinstance(key,tuple):key=(key,)
        rows.append({**dict(zip(keys,key)),**{m:float(np.average(g[m],weights=g.evaluation_mass)) for m in metrics}})
    return pd.DataFrame(rows)


def run():
    verify_sources()
    verification=read(OUT/'verification.json')
    assert verification['passed']
    contract=read(OUT/'manifests/experiment-contract.json')
    environment=read(OUT/'manifests/environment.json')
    fits=read(OUT/'manifests/fit-ledger.json')
    contrasts=pd.read_parquet(OUT/'comparisons/composite-contrasts.parquet')
    primary=contrasts[contrasts.variant.eq('primary')]
    content=pd.read_parquet(OUT/'scores/content-composite-scores.parquet')
    feature_scores=pd.read_parquet(OUT/'scores/content-feature-scores.parquet')
    native=pd.read_parquet(OUT/'scores/content-native-scores.parquet')
    native_mean=means(native,['variant','protocol','feature','arm'],['MAE','MSE','bias','coverage80','coverage90','width80','width90'])
    native_mean['RMSE']=np.sqrt(native_mean.MSE)
    native_mean.to_parquet(OUT/'scores/native-metrics-summary.parquet',index=False)
    composite_mean=means(content,['variant','protocol','arm'],['CE_bits'])
    composite_mean.to_parquet(OUT/'scores/composite-metrics-summary.parquet',index=False)
    feature_mean=means(feature_scores,['variant','protocol','feature','arm'],['CE_bits','fallback_rate'])
    feature_mean.to_parquet(OUT/'scores/feature-metrics-summary.parquet',index=False)
    info=pd.read_parquet(OUT/'information/information-summary.parquet')
    inf=info[info.weighting.eq('hierarchical')&info.estimator.eq('empirical_true')]
    drift=pd.read_parquet(OUT/'information/drift-summary.parquet')
    drift=drift[drift.weighting.eq('hierarchical')]
    zero=pd.read_parquet(OUT/'information/zero-direction-summary.parquet')
    zero=zero[zero.weighting.eq('hierarchical')&zero.feature.eq('U_down')]
    distance=pd.read_parquet(OUT/'comparisons/kernel-distances.parquet')
    load=pd.read_parquet(OUT/'comparisons/load-contrasts.parquet')
    window_info=pd.read_parquet(OUT/'window-supplement/information-summary.parquet')
    null=read(OUT/'information/smoothing-null-check.json')
    artificial=read(OUT/'information/artificial-checks.json')
    frame=pd.read_parquet(OUT/'features/paired-flow-features.parquet')
    coverage=frame.groupby('protocol').agg(pairs=('pair_id','size'),visits=('session_id','nunique'),contents=('content_id','nunique'),
                  closed_subset=('closed_contiguous_all_four','sum')).reset_index()
    occupied=window_info[window_info.estimator.eq('empirical_true')].copy()
    sections=[]
    sections.append('# Extend 代理前后流级概率漂移与信息关系实验报告\n\n日期：2026年10月4日。\n\n'
      '本轮已完成四协议排他TCP连接的联合概率、条件核、内容外概率预测、原单位预测、信息统计及共同支持核距离。'
      '主范围为23566对连接、480父访问、30内容；既有600访问队列及旧实验保持不变。'
      '真实对应模型的八项预登记组合评分比较均通过家族校正正向区间判断。'
      '这是当前观测队列和有限离散模型的测量结果，不是新增业务分类收益、精确协议开销或完整信道信息量。\n\n'
      '同时保留负载条件扩展的负向结果、原单位长尾误差、窗口分箱退化及有限样本信息估计边界。'
      '本轮没有扫描PCAP，没有拟合分类器，没有进入Hy2新数值提取，也没有改变SSL或J系列结果。')
    sections.append('## 1 数据配置和资格\n\n'
      '数据来源为Extend Content Generalization；目录名称35/R5不等于主成员数。固定主成员实际为30内容、六业务、四重复、五部署600访问。'
      '其中四部署480访问可用于排他TCP分析，AnyTLS仅使用独立访问窗口补充。六业务为Bing搜索、MDN文档、GitHub仓库、Wikipedia文章、YouTube搜索、YouTube视频，每业务五内容。\n\n'
      +markdown(coverage)+'\n'
      '候选pair共23660，主共同有效非空pair共23566。上表闭合子集仅是固定敏感性范围，不替换主队列。十变量无缺失、无插补、无删除。\n\n'
      '| 部署 | 当前配置 | 源码与观测边界 |\n|---|---|---|\n'
      '| SS | AES-256-GCM，无plugin/smux | 32B salt与34B/chunk局部规则；Write/chunk数不可由TCP包数替代 |\n'
      '| VLESS | TCP+TLS，无REALITY/Vision/smux | 不使用旧Vision阶段、+2或1870B先验 |\n'
      '| Trojan | TCP+TLS，无附加SS/REALITY/smux | 请求头位于TLS内部；不是观测字节差K |\n'
      '| VMess | WS+TLS，auto，global padding/authenticated length关闭 | alterId/最终安全模式未保存；请求0至15B随机padding并未因此关闭 |\n'
      '| AnyTLS | TLS carrier与逻辑stream复用 | counter/scheme不完整，访问可混合新建和复用，无TCP pair资格 |\n'
      '| Hy2 | QUIC+Salamander，无hopping | 无合格主W缓存，跨内容carrier另审计，本轮无新数值模型 |\n\n'
      '源码解释优先绑定采集提交74cfed919c03f07a21b252328fe48b72c5361215；本地origin/Meta提交88dcbf7f1614a67c3b36b848ee3592dfa92ada36只作参考，不倒推新版本行为。'
      '协议/config在本任务中明确用于路由部署条件核，不声称这是不含协议身份的业务分类器。')
    sections.append('## 2 特征模型和训练权限\n\n'
      '三族十变量：字节W_up/down、U_up/down；事件P_up/down、E_up/down；交互FR_packet_runs、R_unique_zero_runs。'
      'W含重复传输，U为已观测唯一TCP字节；P为正载荷包，E为新字节事件；原FR按正载荷包方向run计算，唯一run按新字节到达计算，二者分开命名。'
      '对象是排他双向连接对，不把单向flow或访问汇总误作单连接。\n\n'
      '字节固定9箱：0、1–255、256–1023、1024–4095、4096–16383、16384–65535、65536–262143、262144–1048575、1048576以上。'
      '计数固定10箱：0、1、2、3、4–7、8–15、16–31、32–63、64–127、128以上。零独立，末箱开放，全部部署/折/两侧共用物理边界。\n\n'
      '主频数使用每内容质量1、内容内访问等权、访问内连接等权；连接等权另作敏感性。'
      'M0为训练出口边际；M1为真实联合条件核；M2以同内容同部署两侧边际乘积构造匿名组联合表。'
      'M1/M2两侧边际保持一致；M2输入删除pair/session/carrier身份并独立打乱两侧行，不强行建立跨重复donor。\n\n'
      '每折训练24内容、测试6内容，同内容的协议、重复、两侧及全部连接整体划分。训练、pre-only查询、post评分是不同物理文件包和独立进程，'
      '不是OS权限沙箱。预处理资格由双侧离线证据形成；历史数据已经反复分析，不能声称外部盲测。'
      '模型数值输入不包含业务标签、内容ID、地址、端口、SNI或endpoint；内容ID仅用于分组控制和统计，标签仅用于bootstrap分层。\n\n'
      '预测平滑固定alpha=beta=1内容质量单位。q0=(出口频数+1/k)/(训练质量+1)，K=(联合频数+q0)/(入口行质量+1)。'
      '空入口行回退q0。经验信息量来自经验联合分布；平滑信息量从Q(A,B)=训练P(A)K(B|A)重新计算全部边际，不混用两种分布。\n\n'
      '拟合及预测全部使用'+environment['gpu']+'、CUDA float64；不是CPU回退。共3250个登记臂估计任务，保存1150个模型文件：'
      '主600，连接等权600，合并箱600，闭合子集600，负载条件400，访问窗口450。原单位伴随分布另保存在主/窗口模型文件；描述信息表不作为额外OOF模型。')
    main=composite_mean[composite_mean.variant.eq('primary')].pivot(index='protocol',columns='arm',values='CE_bits').reset_index()
    sections.append('## 3 内容外概率预测主结果\n\n'
      '组合评分先在每族内对变量等权，再对三族等权。它是单变量预测的复合log-loss，不是十维联合似然；越低越好，单位bit。\n\n'
      +markdown(main)+'\n'
      '主增益定义为左臂loss减M1 loss，正值表示真配模型较好。10000次按六业务分层的内容组bootstrap，跨协议共享抽样索引；'
      '普通95%和八项Bonferroni家族区间均保留。所有区间条件于固定模型，不含重训练/选择及离散化偏差。\n\n'
      +markdown(primary[['protocol','contrast','gain_bits','low95','high95','family_low','family_high','family_positive']])+'\n'
      '八项家族区间下界均为正。因此可以说：在当前连接队列、固定箱和估计器中，真实同次统计对应提供了超越出口边际及匿名同内容关系的内容外预测用途。'
      'M2打乱了同内容内的连接负载、角色及实例组合；没有可靠同角色控制，因此不能进一步将这全部归为纯重复访问噪声或证明精确访问身份对所有方法必要。'
      '真实对应的用途也不能直接推出业务语义信息或分类F1增量。\n\n'
      '![主概率增益](../../'+relative(OUT/'figures/content-heldout-gains.png')+')')
    fm=feature_mean[feature_mean.variant.eq('primary')].pivot(index=['protocol','feature'],columns='arm',values='CE_bits').reset_index()
    sections.append('## 4 每个变量的概率表现\n\n'+markdown(fm)+'\n'
      '本表为完整十变量分项，不从中选择最有利变量重新定义主终点。各变量普通区间见feature-contrasts.parquet，属于探索性，未单独校正40变量比较。')
    sections.append('## 5 漂移量和原FR保持\n\n'
      '以下为全量主队列、内容—访问—连接等权的原单位差值分位数，与此前外层折0训练区的未加权连接中位数不是同一个汇总。\n\n'
      +markdown(drift[['protocol','feature','delta_q25','delta_median','delta_q75','negative_delta_fraction','zero_delta_fraction']])+'\n'
      'SS原FR有约96.77%完全保持，唯一run约97.89%保持；VLESS/Trojan两种run差中位数均为+3，VMess为+5。'
      '这些是当前非Vision/TLS或WS/TLS部署的观测规律，不恢复旧“+2阶段”结论，也不把+3/+5直接解释为可删除协议段。'
      '大多数唯一字节差为正，仍保存少量上行负差；没有通过截断或删连接制造非负。\n\n'
      '![唯一字节差与固定入口负载](../../'+relative(OUT/'figures/unique-delta-by-fixed-pre-load.png')+')')
    sections.append('## 6 零入口方向的出口分布\n\n'+markdown(zero[['protocol','zero_pre_pairs','zero_pre_contents','positive_post_given_zero_pre']])+'\n'
      'SS在pre下行U为0时，post下行正字节概率约0.716%；VLESS/Trojan/VMess接近99.8%。'
      '这与外层TLS/WS控制流量的存在相容，但本轮没有记录或阶段定位证据，不能把每个出口字节标为握手。'
      '零分母使普通倍率失效，而条件概率能够保留这部分观测。\n\n'
      '![零下行转换](../../'+relative(OUT/'figures/zero-downlink-conversion.png')+')')
    sections.append('## 7 信息关系及支持量\n\n'
      '本表为经验plug-in离散信息，单位bit。信息统计必须与固定分箱、加权目标和已观测支持一起解释；不是原流量的信息总量或业务标签泄漏。\n\n'
      +markdown(inf[['protocol','feature','H_A','H_B','H_B_given_A','H_A_given_B','MI','MI_low95','MI_high95','A_occupied','B_occupied']])+'\n'
      'SS下行U的MI约1.887、条件熵约0.149；原FR约2.119/0.101，唯一run约2.169/0.038。'
      'VLESS/Trojan下行U的MI约1、条件熵约0.18–0.19，VMess唯一run条件熵约0.495。'
      '可以描述固定观测下的可预测与剩余不确定性，不可把不同边际熵直接用于协议保留能力排名。'
      '比较幅度还受到A本身的熵和样本组成影响。\n\n'
      '每个(A,B)格的实际pair/访问/内容数、加权质量、最大单内容贡献及每行支持已保存在joint-and-conditional.parquet。'
      '未观测入口行的经验条件概率为NA，不靠平滑制造观测支持。所有熵恒等式通过；经验表和平滑模型表分开。'
      f'独立变量的16样本四箱人工例中，plug-in MI平均仍为{artificial["independent_finite_sample_plugin_MI_mean"]:.6f} bit，说明有限样本可产生假MI；'
      '这不是对本数据的自动偏差校正。Bootstrap区间同样不能消除偏差。\n\n'
      '![信息关系](../../'+relative(OUT/'figures/information-profile.png')+')\n\n'
      '![下行联合与条件核](../../'+relative(OUT/'figures/unique-down-joint-and-kernel.png')+')\n\n'
      '信息恒等式H(B)-H(A)=H(B|A)-H(A|B)不等于噪声/填充量；十变量MI不相加为整体流信息。'
      '方法定义及边界参照[Paninski研究](https://sites.stat.columbia.edu/liam/research/abstracts/info_est-nc-abs.html)和'
      '[Shannon entropy与KL讲义](https://www.stat.cmu.edu/~cshalizi/754/2006/notes/lecture-28.pdf)，不是本数据数值的外部证据。')
    nm=native_mean[native_mean.variant.eq('primary')]
    sections.append('## 8 原单位预测和名义区间\n\n'
      '原单位伴随分布使用训练目标原值和入口箱，给中位数及80%/90%预测区间，不用开放末箱的虚构中点。'
      '它与含均匀出口箱先验的离散核是不同预测器。下行U重点如下，其余所有变量在附录保留。\n\n'
      +markdown(nm[nm.feature.eq('U_down')][['protocol','arm','MAE','RMSE','bias','coverage80','coverage90','width80','width90']])+'\n'
      'M1使下行U的MAE下降，90%区间更窄，覆盖约95.9%至96.2%；名义90%不是实际校准已经达到90%。'
      '全量下行MAE仍为约7.39万至14.19万字节，偏差为负，大连接长尾影响明显。'
      '低分箱log-loss不等于精准原单位恢复，末箱范围与训练原值尾部限制均没有被修复或掩盖。')
    sensitive=contrasts[contrasts.variant.isin(['flow_equal','merged','closed'])]
    sections.append('## 9 固定敏感性和负载扩展\n\n'+markdown(sensitive[['variant','protocol','contrast','gain_bits','low95','high95']])+'\n'
      '连接等权、预先固定合并箱、闭合连续子集均保留正向点差，普通区间也为正；这些是探索性敏感性，不替换八项主终点。'
      '闭合子集人数见资格表，主23566成员未改。\n\n'
      +markdown(load)+'\n'
      'M1-M1_L四部署均为负，组合评分分别约退化0.0318、0.0379、0.0379、0.0059 bit。'
      '本轮固定负载条件没有额外用途；可能涉及条件分散支持和固定平滑，但本轮未做该因果归因。'
      '不按这项负结果重新选择负载箱、alpha或模型容量。')
    dm=distance.groupby(['protocol_1','protocol_2']).agg(mean_JS=('conditional_JS_bits','mean'),min_JS=('conditional_JS_bits','min'),
             max_JS=('conditional_JS_bits','max'),mean_coverage_1=('coverage_1','mean'),mean_coverage_2=('coverage_2','mean')).reset_index()
    sections.append('## 10 共同入口支持的部署核距离\n\n'
      '每折仅从训练区选择共同A箱，要求每部署至少5内容和10访问。r(A)为两部署入口边际等权混合、在共同集归一化。'
      '五折重叠，范围不是独立重现实验区间。下表把十变量和五折作描述性平均，不能称为真正十维协议距离。\n\n'
      +markdown(dm)+'\n'
      'VLESS/Trojan平均JS约0.0018，而SS与VLESS/Trojan约0.31，SS与VMess约0.384；该范围共同输入质量平均高于99.8%。'
      '这与当前两个普通TCP+TLS部署观测形态相近、SS/WS+TLS更不同相容，但节点、路径和负载仍未因果分离。'
      '每个变量及折的覆盖和距离见kernel-distances.parquet。\n\n'
      '![核距离](../../'+relative(OUT/'figures/common-support-kernel-JS.png')+')')
    wc=contrasts[contrasts.variant.eq('window')]
    sections.append('## 11 独立访问窗口补充及平滑反例\n\n'
      '五部署600访问的窗口W/P/R分析单列，AnyTLS在这里有结果，不获得排他TCP资格。所有窗口信息与主连接信息分开保存。\n\n'
      +markdown(wc[['protocol','contrast','gain_bits','low95','high95']])+'\n'
      +markdown(occupied[['protocol','feature','MI','H_B_given_A']])+'\n'
      '固定连接分箱直接用于大窗口时，很多计数都≥128、下行字节都≥1MiB，导致单箱退化；Trojan/VLESS/VMess大部分窗口变量MI和条件熵为0。'
      '不能据此说窗口流量没有结构，也不按窗口结果重新选箱。AnyTLS窗口的小幅增益不等于复用/padding机制已被识别。\n\n'
      f'进一步人工检查中，训练质量24、10出口箱、A/B均恒定时，经验MI=0，M0目标概率={null["M0_observed_probability"]:.6f}，'
      f'M1目标概率={null["M1_observed_probability"]:.6f}，仍产生{null["log_loss_gain_bits_without_MI"]:.6f} bit预测增益。'
      '这是当前数据驱动q0再用于条件平滑的收缩结构效应，不是信息关系。'
      '因而尤其不能把窗口M0-M1约0.05 bit写成MI；M1/M2拥有相同边际、行质量和先验，该反例中二者完全相等。'
      '四协议主M2-M1比较不由这个单纯平滑差异产生，但仍限定在当前粗匿名组对照。未修改既定核公式补救此现象。')
    sections.append('## 12 审计工程修复和复现\n\n'
      +markdown(pd.DataFrame([verification]))+'\n'
      '未出现新登记carrier或logical跨内容折；原96次FR重放通过；匿名边际最大差约9.1e−13，连接等权直接汇总最大误差约8.9e−16。'
      '历史5例未观察SYN依据既有采集源码/实体资格保留，本轮未重建完整TCP epoch；因此不承诺任意未观测连接都已排除泄漏。\n\n'
      '首次评分前发现连接等权内容汇总会丢失总权重。已保存evaluate/uncertainty/fit原稿、追加修复SHA和原因台账。'
      '修复保留每内容评价质量并在内容汇总/bootstrap中恢复连接等权；主层级目标、核公式、所有模型/预测、折和成员不变。'
      '原预登记contract不覆盖，repair台账独立保存；没有根据测试成绩选修复。\n\n'
      '可复用脚本位于eval/protocol_probability_drift。首次运行顺序为registry、features、prepare、fit、predict、evaluate、uncertainty、tables、supplement、plot、verify、report。'
      '已有run不能覆盖重建：registry/features/prepare具有防覆盖门；fit可验证哈希后复用已完成模型。当前评分修复版本另有register_score_repair记录。'
      '如需完整重新拟合，应先另登记新的run目录，不能删除当前结果重新启动。\n\n'
      '本地输出：outputs/protocol-probability-drift-20261004/run-01；Parquet表、核、OOF完整概率、原单位分位数、bootstrap、配置/源码/访问台账及六组PNG/PDF科学图均保留。'
      'plan与大输出仍忽略，不自动提交或推送。报告使用文档写作技能区分事实、解释和未验证范围。')
    sections.append('## 13 本轮结论和停止位置\n\n'
      '可以凝练为：在四个已见Extend部署的排他TCP连接队列中，真实pre/post对应形成可在未见内容上使用的低维条件概率关系；'
      '在同一两侧数据、成员与权重下，它优于边际及匿名同内容关系。不同部署的字节和交互核有差异，SS较高的run保持与普通TLS/WS+TLS的系统性run增加同时存在。\n\n'
      '不能推出：纯协议因果核、精确K或语义阶段；完整流/业务信息保留量；业务分类改善；逐包/逐记录对应；合法会话生成；'
      '外部DIRECT、未见配置/日期/协议泛化；AnyTLS逻辑stream或Hy2已取得同等资格。\n\n'
      'Q00至Q24的缓存范围工作结项，不追加分类器、分箱/阈值搜索或隐状态拟合。'
      '若下一步要扩大AnyTLS粒度、提取Hy2数值、加入可靠角色控制或将核用于生成/分类，需要独立方案和确认，而不是把本轮正向测量自动转换为业务收益。')
    sections.append('## 14 原单位完整结果附录\n\n'
      '所有原单位伴随预测的主连接指标，误差单位为对应变量的字节或计数；RMSE由加权MSE开方，不是内容RMSE的平均。')
    for p in PROTOCOLS:
        sections.append('### '+NAMES[p]+'\n\n'+markdown(nm[nm.protocol.eq(p)][['feature','arm','MAE','RMSE','bias','coverage80','coverage90','width80','width90']]))
    DOC.mkdir(parents=True,exist_ok=True)
    path=DOC/'formal-report.md'
    path.write_text('\n\n'.join(sections)+'\n',encoding='utf-8')
    write(OUT/'manifests/report-manifest.json',{'report':relative(path),'report_sha256':read_sha(path),
      'tables_used':['scores','comparisons','information','probability-tables','window-supplement'],
      'figure_files':[relative(p) for p in (OUT/'figures').glob('*')],
      'main_contrasts_passed':int(primary.family_positive.sum()),'primary_family_size':8})
    checkpoint('Q24_complete',{'main_contrasts_positive':int(primary.family_positive.sum()),
                             'verification_passed':True,'next_expansions_require_confirmation':True})
    print('Complete report saved:',path,flush=True)


def read_sha(path):
    from common import hash_file
    return hash_file(path)


if __name__=='__main__':run()
