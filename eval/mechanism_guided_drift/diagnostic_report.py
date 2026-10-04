"""Descriptive reporting of sealed P2 results; no fitting or model selection."""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from common import ROOT, DOC, LATEST, read_json, write_json, file_hash
from diagnostics import OUT


def table(frame, digits=3):
    return frame.to_markdown(index=False,floatfmt=f'.{digits}f')


def summarize(frame):
    # Declared diagnostic consensus across repeated fit-role predictions, NOT a deployed ensemble.
    keys=['level','outer_fold','method','protocol','content_id','session_id','direction']
    frame=frame.copy();frame['unit_id']=frame.logical_id.fillna(frame.session_id)
    group=keys+['unit_id']
    averaged=frame.groupby(group,dropna=False).agg(prediction=('prediction','mean'),target=('target','first'),
        pre_bytes=('pre_bytes','first'),negative_estimate=('negative_estimate','max'),load_bin=('load_bin','median')).reset_index()
    averaged['error']=averaged.prediction-averaged.target
    averaged['abs_error']=averaged.error.abs();averaged['sq_error']=averaged.error**2
    rows=[];rng=np.random.default_rng(20261004)
    for values,g in averaged.groupby(['level','outer_fold','protocol','method','direction']):
        c=g.groupby('content_id').agg(mae=('abs_error','mean'),mse=('sq_error','mean'),bias=('error','mean'))
        draws=rng.integers(0,len(c),(1000,len(c)))
        ci=np.quantile(c.mae.to_numpy()[draws].mean(1),[.025,.975])
        rows.append(dict(zip(['level','outer_fold','protocol','method','direction'],values),
            units=len(g),contents=len(c),MAE=c.mae.mean(),RMSE=np.sqrt(c.mse.mean()),bias=c.bias.mean(),
            MAE_low=ci[0],MAE_high=ci[1],negative_estimates=int(g.negative_estimate.sum())))
    return pd.DataFrame(rows),averaged


def main():
    audit=read_json(OUT/'diagnostic-audit.json');assert audit['passed'] and audit['G2_pending']
    contract=read_json(OUT/'diagnostic-contract.json');avail=read_json(OUT/'feature-availability.json')
    pred=pd.read_parquet(OUT/'oof-predictions.parquet')
    metrics,averaged=summarize(pred);metrics.to_parquet(OUT/'metrics.parquet',index=False)
    primary=metrics[metrics.outer_fold.eq(0)]
    sensitivity=metrics[metrics.level.eq('W')].pivot(index=['outer_fold','protocol','direction'],columns='method',values='MAE')
    sensitivity['proxy_MAE_reduction_pct']=100*(1-sensitivity.pre_proxy_W_ridge/sensitivity.frozen_W_ridge)
    sensitivetab=sensitivity.reset_index().groupby(['protocol','direction']).proxy_MAE_reduction_pct.agg(['min','max']).reset_index()
    sensitivetab.to_parquet(OUT/'W-sensitivity.parquet',index=False)
    conn=pd.read_parquet(OUT/'connection-diagnostics.parquet');base=conn[conn.outer_fold.eq(0)].copy()
    descriptors=[]
    for protocol,g in base.groupby('protocol'):
        for name in ['up','down']:
            delta=g['post_U_'+name]-g['pre_U_'+name];x=g['pre_U_'+name]
            positive=x.gt(0);zero=x.eq(0)
            descriptors.append({'protocol':protocol,'direction':name,'connections':len(g),'contents':g.content_id.nunique(),
                'delta_p25':delta.quantile(.25),'delta_median':delta.median(),'delta_p75':delta.quantile(.75),
                'delta_load_spearman':x.corr(delta,method='spearman'),'zero_pre_connections':int(zero.sum()),
                'post_positive_given_zero_pre':int((zero&g['post_U_'+name].gt(0)).sum()),
                'ratio_median_positive_pre':(g.loc[positive,'post_U_'+name]/x[positive]).median(),
                'closed_both':int((g['pre_closed_'+name]&g['post_closed_'+name]).sum())})
    desc=pd.DataFrame(descriptors);desc.to_parquet(OUT/'connection-descriptors.parquet',index=False)
    # Load strata use fold-specific LOCO training thresholds, never all-data thresholds.
    strata=averaged[averaged.outer_fold.eq(0)].copy();strata['load_bin']=strata.load_bin.round().astype(int)
    strat= strata.groupby(['level','protocol','method','direction','load_bin']).agg(
        units=('unit_id','size'),contents=('content_id','nunique'),MAE=('abs_error','mean'),bias=('error','mean')).reset_index()
    strat.to_parquet(OUT/'load-strata.parquet',index=False)
    closed=pred[pred.outer_fold.eq(0)&pred.level.eq('T')].copy()
    closed['error']=closed.prediction-closed.target;closed['abs_error']=closed.error.abs()
    closed=closed.groupby(['protocol','method','direction','closed_both','content_id']).agg(
        MAE=('abs_error','mean'),bias=('error','mean'),units=('session_id','size')).reset_index()
    closed=closed.groupby(['protocol','method','direction','closed_both']).agg(
        MAE=('MAE','mean'),bias=('bias','mean'),contents=('content_id','nunique'),units=('units','sum')).reset_index()
    closed.to_parquet(OUT/'end-state-strata.parquet',index=False)
    window=pd.read_parquet(OUT/'carrier-window-diagnostics.parquet');wc=window[window.outer_fold.eq(0)].copy()
    wc['lifecycle_group']=np.where(wc.bind_reused.gt(0),'logged_reused_binding','no_logged_reused_binding')
    anyrows=[]
    for kind,g in wc[wc.protocol.eq('anytls')].groupby('lifecycle_group'):
        for name in ['up','down']:
            delta=g['W_'+name+'_post']-g['W_'+name+'_pre']
            anyrows.append({'log_group':kind,'direction':name,'visits':len(g),'contents':g.content_id.nunique(),
                           'delta_median':delta.median(),'delta_IQR':delta.quantile(.75)-delta.quantile(.25),
                           'opens_median':g.logged_open_carriers.median()})
    anytab=pd.DataFrame(anyrows);anytab.to_parquet(OUT/'anytls-log-strata.parquet',index=False)
    eligibility=pd.read_parquet(OUT/'connection-eligibility.parquet').merge(
        pd.read_parquet(LATEST/'cohort.parquet',columns=['session_id','protocol']),on='session_id',validate='many_to_one')
    el=eligibility[eligibility.outer_fold.eq(0)]
    eltab=el.groupby('protocol').agg(visits=('session_id','size'),registered_logical=('registered_logical','sum'),
                                    common_valid_nonempty=('common_valid_nonempty','sum')).reset_index()
    eltab['retained_fraction']=eltab.common_valid_nonempty/eltab.registered_logical
    eltab.to_parquet(OUT/'T-coverage.parquet',index=False)
    figdir=OUT/'figures';figdir.mkdir(exist_ok=True)
    fig,axes=plt.subplots(2,2,figsize=(12,8),layout='constrained')
    for row,level in enumerate(['W','T']):
        for col,direction in enumerate(['up','down']):
            g=primary[primary.level.eq(level)&primary.direction.eq(direction)]
            matrix=g.pivot(index='protocol',columns='method',values='MAE')
            labels=matrix.index.tolist();x=np.arange(len(labels))
            for k,method in enumerate(matrix.columns):
                selected=g[g.method.eq(method)].set_index('protocol').loc[labels]
                axes[row,col].errorbar(x+(k-1)*.15,selected.MAE,
                    yerr=[selected.MAE-selected.MAE_low,selected.MAE_high-selected.MAE],
                    marker='o',linestyle='none',capsize=3,label=method)
            axes[row,col].set_xticks(x,labels);axes[row,col].set_yscale('log')
            axes[row,col].set_title(f'{level} {direction} content-balanced MAE (outer-train fold0)')
            axes[row,col].set_ylabel('Bytes, log scale');axes[row,col].set_xlabel('')
            axes[row,col].legend(fontsize=7)
    fig.savefig(figdir/'oof-errors.png',dpi=180);plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(11,4),layout='constrained')
    for index,direction in enumerate(['up','down']):
        g=strat[strat.level.eq('T')&strat.direction.eq(direction)&strat.method.eq('training_median_additive')]
        for protocol,p in g.groupby('protocol'):axes[index].plot(p.load_bin,p.MAE,marker='o',label=protocol)
        axes[index].set_title(f'T {direction}: constant-offset error by train-defined load bin')
        axes[index].set_xlabel('LOCO fit load quartile');axes[index].set_ylabel('Bytes MAE');axes[index].set_yscale('log');axes[index].legend(fontsize=8)
    fig.savefig(figdir/'load-strata.png',dpi=180);plt.close(fig)
    cuda=read_json(OUT/'cuda-replay.json')
    # This candidate is determined by permission / available fields, not error rankings.
    candidate={'version':'G2-proposal-v1','status':'awaiting_human_G2','family':contract['candidate_family_predeclared'],
        'mechanism_claim':'empirical pre entity-density startup prior, NOT salt/chunk/TLS exact count',
        'main_scope':'E1 W five seen deployments, all600 visits, original global folds/labels',
        'inputs':'original six pre W values + eight registered pre-only proxy summaries',
        'offline_eligibility_required':True,'online_deployment_proven':False,
        'center_formula':{
            'N_d':'distinct positive-payload pre entities in direction d; not new physical carriers',
            'beta_d':'max(0, sum_train N_d*(Wpost_d-Wpre_d)/sum_train N_d^2); zero denominator gives 0',
            'raw_center':'W0_d=Wpre_d+floor(beta_d*N_d+0.5); P0=Ppre; R0=Rpre',
            'integer_rule':'fixed nonnegative nearest integer increment; disclosed, not silent constraint repair',
            'admissibility':'if W0>L*Ppre stop corresponding task; no silent clipping/retry; zero pre direction keeps N=0',
            'latent_center':'m=original_phi(raw_center); learned remainder uses phi(post)-m; beta refit in every inner scope'},
        'paired_group_cyclic':'same pre inputs/center; beta uses arm-permitted target alignment (group equal-weight encoded target converted by frozen rule must be specified at P3 contract); no borrowing paired identity for group',
        'group_pending_detail':'group raw-byte beta uses Cartesian equal-weight within-content post marginal means, no session pairing; latent target remains original group encoded mean',
        'D0_parameters':42,'D1_parameters':90,'D2_parameters':92,
        'D1':'same 14 numeric pre input columns and original center; 90 Ridge parameters',
        'D2':'same90 Ridge plus2 nonnegative startup coefficients per protocol; budget difference disclosed',
        'missing_proxy':'stop, not fill missing parsed records as0',
        'protocol_specific_exact_K':False,'new_residual_sampling':False,'classifier_new_inputs':False,
        'authorization_required':['eight pre proxy inputs','two extra center coefficients per protocol','bounded raw center with overflow stop'],
        'further_PCAP_extraction_required':False,'Hy2_classification':False,'T_classification':False,'AnyTLS_log_model_input':False,
        'choice_not_based_on_best_OOF_model':True,'P3_started':False}
    write_json(OUT/'candidate-eligibility.json',candidate)
    wdisplay=primary[primary.level.eq('W')][['protocol','direction','method','MAE','RMSE','bias','MAE_low','MAE_high']]
    tdisplay=primary[primary.level.eq('T')][['protocol','direction','method','MAE','RMSE','bias','MAE_low','MAE_high','negative_estimates']]
    text=f'''# Extend 六协议可观测机制诊断报告

日期：2026-10-04。P2 已完成，停在 G2。本报告使用既有缓存和固定采集源码，不新增捕获，不训练业务分类器，不生成合成训练视图。主要问题是已有观测能否支持一个可部署的机制启发漂移中心，而不是寻找分类最高分。

## 结论与证据范围

六协议都有配置及源码证据，但局部封装长度不等于访问级捕获开销。SS 的分块 Write、TLS record 边界、AnyTLS padding counter/scheme 和 Hy2 QUIC 内部状态没有由本缓存直接观测。Extend 中 VLESS 未启用 Vision/REALITY；VMess 是 WS+TLS；Hy2 启用 Salamander 而未启用 hopping。旧队列配置不能替代这些事实。

主 W 队列保持五协议、600 次访问、30 个内容、六业务、每内容每协议四重复。T 只作四协议共同有效连接的局部诊断，AnyTLS 不获得 T 资格。Hy2 无合格主数值缓存，且共享载体审计单列，因此本轮没有六协议统一回归或分类结果。

本轮可以提出一个 **pre 连接密度与载荷结构启发的经验中心**，不能提出精确协议 K。新增代理 Ridge 的误差即使更低，也只能说明允许的 pre 数值对有限学习器有预测用途，不能验证 salt、chunk、TLS 或状态切换的因果解释。唯一候选依据预登记的输入可用性与权限提出，不按哪一条训练误差最优选择。

实测有三项需要保留的具体发现。第一，主诊断折中增强pre代理使五协议上行W的MAE点估计都低于旧Ridge，但下行仅SS、VLESS和Trojan降低，VMess与AnyTLS变差；五折敏感性也不是所有方向都改善。第二，连接T下行训练中位数参照的MAE在四协议均低于这两种原始差值Ridge，不能把增加代理普遍写成更好。第三，AnyTLS训练区96访问全部有reused binding，因而缺少“没有复用”的对照层，本轮不能识别新建与复用造成的差异。

## 实验划分和数据权限

全局沿用原内容五折，同内容的全部协议、四重复、两侧及内部 flow 不拆开。复用100个 W 生成器训练范围，每个18内容/72访问；内容留一时17内容/68访问，1,800个任务。T 在每折训练区24内容中留一，共480个任务，每次23内容拟合，连接不随机拆分。三方法分别拟合，因此累计 **6,840 个小型模型/中位数估计任务**，不是新神经训练矩阵。

只读取对应外层训练 post。内层留出 post 仅用于误差计算，不进入内层拟合；W 的 query 内容 post 不进入生成拟合。五个外层训练集合互相重叠，不能当作独立重复。报告主表固定为外层折0的训练区，其余四折为敏感性表，不参与事后选择折或候选。

实现按外层训练区加载480访问post缓存，某个job的query访问可能作为其他合法job的拟合/留一评分内容，因此不是每个job都拥有单独物理文件权限包。台账中的query_post_access=false表示本job拟合没有索引其query目标，不表示整个诊断进程未加载过该访问的训练post。P3生成仍需独立权限包；本轮不以该加载方式宣称物理隔离。

划分重放未发现注册 carrier 跨折；历史审计记录 carrier/SYN/完整正载荷 IP 包跨折复用均为0。仍保留5例未观察 SYN 及5,065个跨折复用路径哈希：路径复用不直接证明同连接复用，仪器身份资格也不构成任意未观测 TCP epoch 的普遍证明。本轮没有重新扫描 PCAP。

工程预检曾错误打印一个 Trojan、原外层折2访问的 T-pairs 双侧摘要，已在契约/access ledger 登记；该输出不用于方法选择或拟合。此前数据也已反复分析。因此软件权限隔离不能升级为研究者未见过数据的外部盲测。

## 可用字段和缺失

严格记录缓存清点结果为 **{avail['Extend_strict_record_cache_files']} 个文件**。本轮不把0916定点解析能力移植成Extend全队列可解析性的证明，也不通过补零模拟记录特征。

W 的六量仍是选定窗口内观测传输载荷及其事件/方向段，含重复传输；T 是共同有效非空 TCP pair 的唯一新字节。二者不是同一种开销测量。

八个 pre 代理为上下行正载荷实体数的 log1p、载荷长度中位数/q90的 log1p、小载荷比例。小载荷阈值预先固定256，不是协议状态阈值。零方向的统计值0表示真正没有该方向事件，另存 empty 标志；没有缓存时应停止而非补0。实体 ID 只用于计数和资格，不作为数值输入。

T 代理为各方向 pre 新字节事件中≤256字节的比例。新字节事件也不等于应用 Write。业务标签、地址、端口、SNI、URL及各种身份列均不进入回归。

## 源码局部规则测试

{len(read_json(OUT/'mechanism-unit-tests.json')['checks'])} 项人工输入检查通过。SS AES-256-GCM 每方向 salt32、每块2+16+16=34；同样200字节一次 Write 与两次100字节 Write 的局部长度不同，证明 TCP 包数不能代替块数。Vision 长短填充仅作为人工算法检查，Extend该分支未启用。VMess auto 未落定安全模式，alterId 未保存，故不制造统一精确字节公式。Trojan TCP请求为IPv4 68、IPv6 80、domain65+n，地址长度不加入分类/生成查询。AnyTLS帧头7；默认初始化64只在相应scheme前提下成立。Hy2 QUIC varint边界及每UDP数据报8字节Salamander盐分开验证。

这些检查是源码规则的独立实现测试，不是完整 Go 互操作测试，也不是捕获机制验证。源码行号和 SHA 继承P1 mechanism-contract。

## W 训练内容留一结果

三个参照：训练中位数原始附加量；冻结旧六量支持保持 Ridge；同一编码/解码/alpha1的增强代理 Ridge。旧Ridge42参数，增强90参数，不能把比较单独归因于机制结构。所有矩阵求解和预测均在 **{cuda['device']} CUDA float64**；旧公式零改动重放最大差 {cuda['old_ridge_replay_max_abs']:.3g}。

以下 MAE/RMSE/偏差单位均为字节。每内容等权；重复出现于多个生成训练范围的同一访问先平均其OOF预测，这是描述性共识，不是旧生成器单次使用的预测，也不是新增部署集成方法。区间按内容抽样1,000次，条件于固定拟合，不含重训练不确定性。

{table(wdisplay)}

五折训练诊断中增强代理相对旧Ridge的MAE降低百分比范围如下，正数为点估计降低、负数为变差。训练区互相重叠，这不是五次独立统计检验，也不是性能保证。

{table(sensitivetab)}

## T 连接结果和覆盖

{table(eltab)}

保留比例是共同有效非空连接数除以该训练区登记 logical 数，不是全 raw 包覆盖或全协议可解析率。主600访问未改变，不能把容易闭合的T子集替换W主队列。

{table(tdisplay)}

连接先在内容内等权平均误差，再内容等权；不是把大量连接当独立样本。T 的log摘要 Ridge在原始附加字节目标上拟合，与W旧编码Ridge不是同一个模型。负估计原样计数，未静默截断。

原始差与负载关系如下，Spearman是未控制混杂的描述性相关，不是协议参数估计。比值只在pre>0计算，零分母另列。

{table(desc)}

主诊断折VLESS连接上/下行附加量中位数为495/4,794字节，Trojan为557/4,814，SS为159/236，VMess为904/5,181。它们属于Extend当前配置，不能与历史REALITY/Vision队列的中心混用。VLESS下行有1,137个pre唯一字节为0的连接，其中1,135个post方向为正；Trojan对应1,045/1,042。该现象与外层协议控制数据存在相容，但没有记录/阶段证据时不能将其全部命名为某种握手成本。

负载分层切点来自各LOCO拟合区四分位；完整分层在load-strata.parquet。无论中位附加量看起来多集中，都不能将它写成训练外可验证的固定K。

## AnyTLS 生命周期与 Hy2 共享载体

AnyTLS仅按独立日志是否出现reused binding分层，不按残差高低贴标签。reused日志不表示每次访问只发生复用，也不能从一次日志自动推断counter、成熟padding或所有并发stream共享同一carrier。

{table(anytab)}

若层内内容不足，不作显著性结论；日志是离线状态，不作为生成查询输入。已确认option0经过构造器默认化为30秒，是源码推导，而非观测定时器。

当前唯一日志层覆盖全部96训练访问和24内容，中位数每访问21个logged open carrier；新建和reused可在同一访问共存。只有一个reuse层，无法计算层间差或声称成熟padding造成W差。

Hy2：{avail['Hy2']['selected_sessions']}个登记访问；content子集{avail['Hy2']['content_sessions']}访问，登记carrier {avail['Hy2']['content_carriers']}个，其中跨内容{avail['Hy2']['carriers_cross_content']}个，跨已映射全局内容折{avail['Hy2']['carriers_cross_global_fold']}个，未映射全局折访问{avail['Hy2']['missing_global_fold_sessions']}个。该范围不自动等于原600主队列。无主W数值缓存，不能计算窗口差OOF，也不能用旧Hy2结论代替本轮原因。若后续需要这项数值测量，必须另批准有限缓存/PCAP提取清单及载体整体隔离，当前不执行。

## 逐机制资格

| 协议 | 已支持的局部依据 | 捕获层允许结论 | 未解决的限制 |
|---|---|---|---|
| SS | 已确认aes-256-gcm、salt/chunk规则 | T附加量及负载关系的经验描述 | Write/chunk数未观测；上行还含目标封装，不能每包加34 |
| VLESS | TCP+TLS、无Vision非mux请求 | 普通TLS部署的局部T/W关系 | TLS初始化/记录状态不独立可见，无精确initial/relay |
| VMess | WS+TLS、关闭两种padding选项 | 负载/包化代理的经验回归 | auto实际安全模式与alterId未知，不能累加假定开销 |
| Trojan | 请求头局部长度 | 连接附加量分布及上下行不对称 | 地址、TLS、结束截断与服务器实现未分离 |
| AnyTLS | 帧头、构造器规范化、carrier日志 | 日志分层W差的离线描述 | counter、scheme更新未知，日志不可冒充pre输入 |
| Hy2 | Salamander每数据报8字节、QUIC本地格式 | 当前只能做实体/配置资格 | 无合格W缓存，跨内容carrier及QUIC不可见，不分类 |

## 唯一候选及 G2 确认

候选名称：**pre连接密度启发的非负启动中心＋剩余Ridge**。这是新的经验设计建议，不是本轮已评估方法。对方向d，令N为pre正载荷实体数，训练内估计：

\\[\\widehat\\beta_d=\\max\\left(0,\\frac{{\\sum_i N_{{i,d}}(W^+_{{i,d}}-W^-_{{i,d}})}}{{\\sum_i N_{{i,d}}^2}}\\right),\\qquad W^0_d=W^-_d+\\lfloor\\widehat\\beta_d N_d+0.5\\rfloor.\\]

零分母系数取0。字节增量按固定最近整数规则量化，不能给只接受整数的旧编码器传入小数。P/R保持pre；raw中心必须先通过旧W必要可行域再编码。若越过65527P上限，停止对应任务，不裁剪、不换样本。剩余Ridge拟合phi(post)-phi(center)，每内层重估beta及全部尺度。N不等于新建carrier，beta不等于salt、TLS头或K；非负只是预登记先验，不能证明真实总差非负，剩余项仍允许负变换。

原D0维持42参数。新增八个pre代理使D1通用Ridge为90参数；D2相同90个剩余参数再加两方向系数，共92参数/协议。对照必须给D1完全相同输入，才能分别检验信息增量与中心结构。日志、目标侧连接数和测试pre均不进入post业务推理。分类器仍只读合成/真实post六量。

paired/group/cyclic三臂同结构与预算。group的beta只用组内等权post字节均值与各pre相结合，不恢复session对应；其latent目标仍是原组内encoded均值。cyclic用其固定donor目标。参数和残差均限各臂权限；P3完整契约需将该规则和同输入D1归因比较封存，不直接沿用真配beta给其他臂。

候选没有使用内部不可观测状态，故不是六协议专用精确封装生成器，也不解决Hy2共享载体。是否批准八个新增pre统计、两参数中心及超界停止规则，由G2决定。本轮不自动进入P3，不扩展E2/T/Hy2分类。

## 图和可复现产物

![训练区内容OOF误差](../../outputs/mechanism-guided-drift-20261003/diagnostics/figures/oof-errors.png)

![训练定义负载分层](../../outputs/mechanism-guided-drift-20261003/diagnostics/figures/load-strata.png)

可复用脚本在eval/mechanism_guided_drift：diagnostics.py seal/run、diagnostic_models.py、local_rules.py、diagnostic_report.py。完整成员、输入/代码SHA、CUDA重放、可用性、权限、连接表、carrier窗口表、OOF预测、分层、五折敏感性及拟合台账保存于outputs/mechanism-guided-drift-20261003/diagnostics。旧输入哈希全部保持；原结果未覆盖。报告采用文档写作技能的证据区分规范，源码事实、实测描述与新候选分节保存。

本轮能够支撑可观察代理有一定预测用途及缺失状态边界，不能支撑分类改善、精确协议开销、语义阶段、在线无索引识别或未见协议泛化。P3是否有收益仍须单独检验。
'''
    DOC.mkdir(exist_ok=True);(DOC/'mechanism-diagnostic-report.md').write_text(text,encoding='utf-8')
    write_json(OUT/'report-manifest.json',{'report_sha256':file_hash(DOC/'mechanism-diagnostic-report.md'),
        'reporting_script_sha256':file_hash(__file__),
        'verification_script_sha256':file_hash(ROOT/'eval/mechanism_guided_drift/verify_diagnostics.py'),
        'primary_outer_fold':0,'metrics_rows':len(metrics),'connection_rows_by_fold':conn.groupby('outer_fold').size().to_dict(),
        'fit_ledger_tasks':audit['fit_ledger_rows'],'G2_pending':True,'P3_started':False})
    print('report saved',DOC/'mechanism-diagnostic-report.md')
    print(primary[['level','protocol','direction','method','MAE']].to_string(index=False))
    print('Hy2',avail['Hy2'])


if __name__=='__main__':main()
