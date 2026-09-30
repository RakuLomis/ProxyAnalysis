"""Generate the measurement report and figures from persisted outputs only."""
import xml.etree.ElementTree as ET
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .run import OUT,DOC,ROOT,PAIR,SIDE,KEY,TIME,load,save,js,read,digest

REPS=['P_raw','P_unique','R','C']

def table(df):
    def fmt(v):
        if pd.isna(v):return '—'
        if isinstance(v,(float,np.floating)):return f'{v:.6g}'
        return str(v).replace('|','/')
    cols=list(df.columns)
    return '| '+' | '.join(cols)+' |\n| '+' | '.join(['---']*len(cols))+' |\n'+'\n'.join('| '+' | '.join(fmt(v) for v in row)+' |' for row in df.itertuples(index=False,name=None))

def report():
    DOC.mkdir(parents=True,exist_ok=True);figdir=DOC/'figures';figdir.mkdir(exist_ok=True)
    p=load('paired-representation-metrics');delta=load('paired-minus-P-unique')
    inter=load('interaction-preservation');sp=load('unit-span-interactions');sw=load('tie-switch-sensitivity')
    units=load('all-units');manifest=load('sample-manifest');r4=load('resegmentation-audit');rt=load('record-time-audit')
    pairmeta=manifest[PAIR+['batch','protocol','item_id','partition','load_layer','mechanism_group']].drop_duplicates()
    counts=pairmeta.groupby(['batch','protocol']).size().rename('pairs').reset_index()
    med=p.groupby('representation')[['w_log2','w_bytes','ks','js_bits','count_ratio','byte_ratio']].median().reindex(REPS)
    changes=[]
    for rep,g in delta.groupby('representation'):
        changes.append({'representation':rep,'directions':len(g),'W_log_lower':int((g.w_log2<0).sum()),
            'W_log_equal':int((g.w_log2==0).sum()),'W_log_higher':int((g.w_log2>0).sum()),
            'median_W_log_change':g.w_log2.median(),'median_KS_change':g.ks.median(),'median_JS_change':g.js_bits.median()})
    changes=pd.DataFrame(changes);save('paired-distance-change-summary',changes)
    connection=p.groupby(PAIR+['representation'])[['w_log2','ks','js_bits']].mean().reset_index()
    connsummary=connection.groupby('representation')[['w_log2','ks','js_bits']].median().reindex(REPS).reset_index()
    save('connection-summary',connection)
    equal=[]
    for name in ['visit-equal-metrics','content-equal-metrics']:
        x=load(name)
        for (batch,rep),g in x.groupby(['batch','representation']):
            equal.append({'unit':name.split('-')[0],'batch':batch,'representation':rep,'units':len(g),'mean_W_log':g.w_log2.mean(),'mean_KS':g.ks.mean(),'mean_JS':g.js_bits.mean()})
    eq=pd.DataFrame(equal);save('equal-weight-summary',eq)
    it=inter.groupby(['representation','time']).agg(n=('direction','size'),mean_grid_MAE=('mean_abs_curve_error','mean'),
        mean_grid_peak=('max_abs_curve_error','mean'),mean_exact_peak=('exact_event_grid_max_error','mean'),
        largest_exact_peak=('exact_event_grid_max_error','max')).reset_index()
    spanrows=[]
    for rep,g in sp.groupby('representation'):
        spanrows.append({'representation':rep,'units':len(g),'median_span_ms':g.span_ns.median()/1e6,
            'q95_span_ms':g.span_ns.quantile(.95)/1e6,'max_span_ms':g.span_ns.max()/1e6,
            'opposite_event_inside_fraction':(g.opposite_events_strictly_inside>0).mean(),
            'prefix_wait_positive_units':int((g.prefix_wait_ns>0).sum())})
    spans=pd.DataFrame(spanrows)
    ties=sw.merge(pairmeta[PAIR+['protocol']],on=PAIR,validate='many_to_one');ties=ties[ties.protocol=='VLESS']
    ties['priority_order_difference']=(ties.switches_down_first-ties.switches_up_first).abs()
    tie_table=ties.groupby(['representation','time']).agg(mean_mixed_tie_fraction=('mixed_tie_unit_fraction','mean'),
        order_sensitive_sides=('priority_order_difference',lambda x:int((x>0).sum())),max_priority_difference=('priority_order_difference','max')).reset_index()
    r4pos=r4[r4.static_signature_equal.notna()];r4neg=r4[r4.negative_rejected.notna()]
    perturb=r4pos.groupby('scenario').agg(streams=('direction','size'),passed=('static_signature_equal','sum'),
        max_synthetic_span_ns=('span_max_ns','max'),max_synthetic_prefix_wait_ns=('prefix_wait_max_ns','max')).reset_index()
    type_diff=load('paired-record-types');type_summary=type_diff.groupby(['kind','from_type','to_type']).fraction_difference.agg(['median','mean']).reset_index()
    save('record-type-change-summary',type_summary)
    # Figures deliberately separate distribution distance, time aggregation and workload.
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    fig,axes=plt.subplots(1,3,figsize=(12,3.8),layout='constrained')
    for ax,col,label in zip(axes,['w_log2','ks','js_bits'],['Wasserstein: log2(1+bytes)','KS statistic','JS divergence (bits)']):
        ax.boxplot([p[p.representation==rep][col] for rep in REPS],tick_labels=REPS,showfliers=False)
        ax.set_ylabel(label);ax.grid(axis='y',alpha=.2)
    fig.suptitle('Frozen VLESS: 90 paired directions (not a population sample)');fig.savefig(figdir/'length-distances.png',dpi=160);plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(10,4),layout='constrained')
    for ax,col,title in zip(axes,['mean_abs_curve_error','exact_event_grid_max_error'],['101-point grid: mean absolute error','Exact event grid: peak error']):
        x=inter.pivot_table(index='time',columns='representation',values=col,aggfunc='mean').reindex(TIME)
        x.plot.bar(ax=ax,rot=0);ax.set_ylabel('Fraction of directional unique bytes');ax.set_title(title);ax.set_xlabel('Record/chunk timestamp');ax.grid(axis='y',alpha=.2)
    fig.savefig(figdir/'time-aggregation.png',dpi=160);plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(10,4),layout='constrained')
    base=p[p.representation=='P_unique'].set_index(PAIR+['direction']);rr=p[p.representation=='R'].set_index(PAIR+['direction'])
    for d,color in [(1,'tab:orange'),(-1,'tab:blue')]:
        idx=base.index.get_level_values('direction')==d
        axes[0].scatter(base.loc[idx,'w_log2'],rr.loc[base.index[idx],'w_log2'],label=f'direction {d:+d}',s=25,alpha=.75,color=color)
    lim=max(base.w_log2.max(),rr.w_log2.max());axes[0].plot([0,lim],[0,lim],'k--',lw=1)
    axes[0].set(xlabel='P_unique log-length W',ylabel='Record log-length W',title='Matched directions');axes[0].legend()
    for d,g in p[p.representation=='R'].groupby('direction'):axes[1].scatter(g.bytes_pre,g.byte_difference,label=f'direction {d:+d}',s=25,alpha=.75)
    axes[1].set_xscale('log');axes[1].set(xlabel='Pre unique bytes',ylabel='Post minus pre unique bytes',title='Recordization does not remove byte excess');axes[1].legend()
    fig.savefig(figdir/'paired-and-workload.png',dpi=160);plt.close(fig)
    xml=ET.parse(OUT/'tests.xml').getroot();suites=list(xml.iter('testsuite'))
    tests={key:sum(int(s.get(key,0)) for s in suites) for key in ['tests','failures','errors','skipped']}
    js('tests.json',tests);assert tests['failures']==tests['errors']==0
    byte_ref=load('unique-byte-reference')
    ss=byte_ref[byte_ref.protocol=='SHADOWSOCKS'].pivot(index=PAIR+['direction'],columns='side',values='unique_payload_bytes').reset_index()
    ss['difference']=ss.post-ss.pre;ss['ratio']=ss.post/ss.pre
    ss_summary=ss.groupby('direction')[['difference','ratio']].median().reset_index()
    m0=load('m0-summary');m0all=load('m0-post-only-byte-estimates')
    run=load('zero-threshold-runs').groupby(SIDE).size().rename('run_count').reset_index()
    run=run.merge(pairmeta[PAIR+['protocol']],on=PAIR,validate='many_to_one')
    runpairs=run.pivot(index=PAIR+['protocol'],columns='side',values='run_count').reset_index();runpairs['difference']=runpairs.post-runpairs.pre
    save('zero-threshold-run-comparison',runpairs)
    # Side-level total U and count quantities remain inspectable, including SS controls.
    total=load('direction-summary');totals=total.groupby(['protocol','side','representation']).agg(direction_sides=('count','size'),units=('count','sum'),bytes=('total','sum')).reset_index()
    shape_cols=['count_axis_shape_mae',*[t+'_common_window_shape_mae' for t in TIME],*[t+'_normalized_duration_shape_mae' for t in TIME]]
    shape=p.groupby('representation')[shape_cols].median().reindex(REPS).reset_index()
    batch=p.groupby(['batch','direction','representation'])[['w_log2','ks','js_bits']].median().reset_index()
    strata=p.groupby(['partition','mechanism_group','representation']).agg(directions=('direction','size'),median_W_log=('w_log2','median'),median_KS=('ks','median')).reset_index()
    lower=int((delta[delta.representation=='R'].w_log2<0).sum())
    content_count=manifest.content_group.nunique();visit_count=manifest.session_id.nunique()
    text=f'''# 记录级 flow 表示：冻结样本方法可行性报告

日期：2026-09-26。范围：R0–R9。已执行；没有新增分类/回归训练，没有生成 initial/relay 或精确 K。

## 1. 核心结论

1. **同字节流的静态记录结构通过重分段测试。** {len(r4pos)} 个正向方向流场景全部通过，{len(r4neg)} 个负向场景全部拒绝完整性；这是解析实现性质，不是代理前后记录不变性的证据。
2. **在当前定点 VLESS 样本，记录级长度描述整体更接近，但并非每条连接都改善。** 90 个配对方向中，R 的 log-length Wasserstein 在 {lower} 个方向低于 P_unique；中位距离由 {med.loc['P_unique','w_log2']:.6f} 降至 {med.loc['R','w_log2']:.6f}。这里是两个距离分布的中位数，不是配对差值中位数；后者见下表。
3. **固定分块说明距离不能单独判优。** C 的同一距离中位数为 {med.loc['C','w_log2']:.6f}，比 R 更小；但 C 丢失语法结构，且其时间聚合损失需要一起看。
4. **记录化保留全部唯一字节，不会消除部署附加量。** R/C/P_unique 的方向总字节逐项相等；本样本 post/pre 字节比中位数仍为 {med.loc['R','byte_ratio']:.6f}。头部也被计入，不冒充业务有效载荷。
5. **不能宣布交互或业务语义完整保留。** 记录时刻约定、跨方向 tie、记录内部反向事件都可能改变方向序列；101 点均值可能很小而短时峰值不小。本轮额外报告全事件时刻的精确峰值作为数值核查，不用于选择表示。

## 2. 样本、冻结与资格

57 对/114 个捕获原样保留，其中 VLESS 45 对、SS 12 对。涉及 {visit_count} 个父访问、{content_count} 个既有内容组。VLESS 主比较为 90 个配对方向、180 条方向侧流；SS 为 48 条方向侧流基础参照。Hy2 不在冻结样本内。下表单位为连接对，不是捕获文件。

{table(counts)}

这是旧抽样层定点样本，不估计全数据集发生率。discovery/verification 都已经看过，仅保留历史标记，不叫新盲测。12 对 SS 不套 TLS 解析；未知 cipher 的边界不变。

180 条 VLESS 方向侧流全部通过：连续索引、连续无重叠字节区间、5-byte 头计账、完整 U 覆盖、旧 first/all 时间重算一致，以及按序前缀时间与来源区间核验。失败或替换成员均为 0。语法 E1 不意味着认证成功、同一封装层或 E2 阶段定位。

## 3. 表示和固定方法

|表示|单位|重传处理|边界|
|---|---|---|---|
|P_raw|非空 TCP 载荷包|保留重复载荷|只用方向、TCP 载荷长度与时间|
|P_unique|每包首次贡献字节|去掉零新字节，部分重叠只计新字节|主要包级参照|
|U|方向唯一字节与零阈值方向段|去重|沿用旧口径，无阈值搜索|
|R|严格连续可见记录，总长含头|按重组字节计账|语法而非业务阶段|
|C|方向内固定 1024-byte 块，末块可短|按重组字节计账|非协议粗化对照，无块大小搜索|

{table(totals)}

长度距离：W(log2(1+length))、原始 bytes W、KS statistic、固定箱 JS divergence（base 2，非平方根）。箱边界为 0/64/128/256/512/1024/2048/4096/8192/16384/32768/∞，在结果计算前配置冻结。没有逐条记录配对、DTW、最相似前缀或距离总分。

时间：first=首次看到任一字节，all=全部记录字节已出现，prefix=从方向起点到记录末尾连续可用。prefix 不是应用读取时间。原始 ns 相对捕获首包，另存各侧首个新字节归零时间；两侧归零不是同一真实事件，不能据此估计代理延迟。方向内 IAT 按字节序计算，零值和负值保留。

## 4. 受控重分段：只证明实现性质

{table(perturb)}

每个 VLESS 方向流：固定 256/1460/4096、固定种子不等长切分、记录头跨段、一段多记录、重复/部分重叠/邻近乱序，以及继承原来源时间的细分。静态签名逐项比较 record_index/start/end/content_type/version/body_length，字节内容不改、U 不改。加速来源映射与旧冻结重组器在所有实际流上交叉核验，随机重叠也有单元测试。

继承时间场景只细分原所有权区间，三个时间全部一致；其他场景使用明确的 1000 ns 人工到达步长，能改变 span/prefix wait。这不是网络性能模拟。缺字节、冲突、缺 SYN 起点、末记录缺字节均不得完整通过，未补零或重新同步。

## 5. 同连接跨侧距离

### 5.1 配对方向分布中位数（每种表示 n=90）

{table(med.reset_index())}

### 5.2 同方向相对 P_unique 的变化

负差表示相应描述距离下降；不作独立记录显著性检验。

{table(changes)}

### 5.3 先在连接内平均两个方向，再取 45 对连接中位数

{table(connsummary)}

![长度距离](figures/length-distances.png)

![配对距离与字节量](figures/paired-and-workload.png)

### 5.4 批次和方向（+1 为既有入口方向定义，−1 为反向）

{table(batch)}

### 5.5 访问/内容等权敏感性

先平均同连接方向，再在父访问内平均连接；内容等权再在同批次同内容内平均访问。表中 mean 是各等权单位的距离均值，不是上文中位数。少量定点内容不能支持跨内容泛化结论。

{table(eq)}

### 5.6 历史抽样层

{table(strata)}

更细的 batch×partition×mechanism_group×load_layer 交叉层保存在 stratified-metrics.parquet，空层不补零。完整逐连接结果见附录与机器表。

## 6. 字节形状、记录类型与时间聚合

### 6.1 跨侧累计形状

下表为配对方向中位数。count_axis 是各方向单位索引归一化；common_window 是两侧各自首新字节归零后的共同截取秒窗（至较短观察终点）；normalized_duration 各自除以持续时间。后者主动消除持续时间差，不是时间保真。所有曲线各用本方向总字节归一化，不能替代绝对工作量分析。

{table(shape)}

### 6.2 同侧相对新字节到达曲线的误差

n=180/表示/时间约定。grid_MAE 和 grid_peak 使用预定 101 点；exact_peak 在所有相关事件时刻的并集求最大值，防止短跨度被网格漏掉。表中 mean 对方向侧流等权，largest 是最大单流峰值；数值为方向唯一字节比例。

{table(it)}

![时间聚合](figures/time-aggregation.png)

first 整条计账可提前释放字节，all/prefix 可延后。即使 101 点均值低，也不能声称完整保留字节到达过程。精确事件峰值是补充数值验算，不是新增调参指标。

### 6.3 记录/分块跨度内反向事件

{table(spans)}

仅计 first < opposite_time < all 的事件，端点 tie 不擅自排先后。同一反向事件可能落入多个单位跨度，不能把累加值当独立流量。逐单位原始量保存于 unit-span-interactions.parquet。

### 6.4 跨方向 tie 与切换敏感性

每个时间约定有 90 个 VLESS 连接侧。两种方向优先次序是预定敏感性场景，不宣称所有合法排列的严格上下界。相同切换数也不能证明唯一因果次序。

{table(tie_table)}

### 6.5 类型组成与方向内转移

类型仅作语法标签：20/21/22/23；不映射为真实握手、业务、Vision initial/relay。各方向内按字节位置取转移，分母为该方向记录数−1（单记录时缺失而非零）。下表为 post−pre 比例差；记录序号不跨侧配对。

{table(type_summary)}

## 7. SS 基础参照与旧 M0 旁路

SS 共 12 对，仍只报告唯一 TCP 字节与旧零阈值方向段；没有 SS 记录、没有猜 cipher。方向字节差与比的中位数：

{table(ss_summary)}

SS 零阈值段差分布：{runpairs[runpairs.protocol=='SHADOWSOCKS'].difference.value_counts().sort_index().to_dict()}。VLESS 段差分布：{runpairs[runpairs.protocol=='VLESS'].difference.value_counts().sort_index().to_dict()}。这些是原抽样层选择后的构成，不是总体发生率。

M0 全部复用旧 byte_all 的内容 OOF 中心，没有在这 45 对 VLESS/12 对 SS 中重新拟合。对 114 个配对方向逐项核对旧系数、训练折中位数、内容排除与旧残差；估计器只用 post 字节和已知 batch×deployment×direction 的训练中心。pre 仅用于评分。

{table(m0)}

全表负估计 {int(m0all.negative_estimate.sum())}/{len(m0all)}，pre=0 分母 {int(m0all.zero_pre_denominator.sum())}/{len(m0all)}；负值不会截断。这里样本中没有负值不等于规则保证非负。每行有相对误差和训练中心。M0 是标量估计，R 是结构表示，未定义共同预测任务，因此不声称 R 胜过 M0。经验字节中心不是精确 K，更不是从 post 头部删除同样长度。

## 8. 权限、预算和可复现性

- post 的记录/分块表示仅接收同侧区间和来源映射；90 条 post 方向流替换无关 pre 后输出不变。114 条 M0 估计替换评分 pre 后也不变。
- 本轮 classifier_fits=0、regression_fits=0；IP/端口/SNI/业务标签没有进入训练（本轮根本无模型）。协议、身份、语法类型保存在审计表，并未自动加入旧模型。
- 输入和旧结果 SHA256 复核一致；旧 240 访问队列未改。独立输出目录保存契约、样本清单、来源、代码哈希、种子、表和测试结果。
- 唯一捕获仍为 114 个，共 {read('capture-read-audit.json')['unique_file_bytes']:,} bytes；没有扫描其他捕获。capture-read-audit.json 记录**单次 capture 阶段**的读文件遍数（含哈希、分析、VLESS 载荷读取）和处理体积。本次开发执行 capture 两次，第二次增加继承时间细分检查；累计捕获文件处理体积为单次的两倍，唯一输入体积不变。所有载荷只在内存，没有保存或发送。
- 测试 {tests['tests']} 项，失败 {tests['failures']}，错误 {tests['errors']}。Pytorch312；完整入口见下。

```powershell
& 'D:/Tools/Anaconda/envs/Pytorch312/python.exe' eval/protocol_normalization/run_record_representation.py --stage all
```

支持 prepare/capture/metrics/report 分阶段；先运行测试生成 tests.xml 再生成报告。配置冻结后不按结果改 bin、样本、块大小或解析规则。主要输出均为 Parquet，避免巨型逐记录 Markdown。

## 9. 结项判断与边界

本轮支持：**严格重组后的可见记录语法具有对同字节流分段变化的静态稳健性；在这批 VLESS 定点连接上，其部分长度描述较包级更接近，且与任意固定分块具有不同的时间聚合特征。**

本轮不支持：逐记录 pre/post 语义对应、同一封装层认证、initial/relay 切换、精确 K、全数据集普遍改善、业务语义恢复、SSL/分类收益。记录化没有把所有 post 字节恢复成 pre；经验中心也没有解释协议机制。

R0–R9 在此停止。没有自动扩大 PCAP 范围、没有重训编码器、没有恢复阶段切点搜索。若后续研究下游价值，需要单独批准同内容划分、相同 post 编码器和配对对照的任务；这不能由当前距离结果替代。

详细文件目录：outputs/record-representation-0914-0916/run-01。附录：connection-details.md。
'''
    (DOC/'report.md').write_text(text,encoding='utf-8')
    # Complete paired-direction table per frozen connection; no record-by-record semantic alignment.
    sections=['# 冻结连接详细结果\n\n所有数值为描述统计。VLESS 每方向四种表示；SS 保留基础参照。']
    for row in pairmeta.sort_values(['protocol','batch','session_id','connection_id']).to_dict('records'):
        sid=row['session_id'];cid=row['connection_id'];x=p[(p.session_id==sid)&(p.connection_id==cid)]
        sections.append(f"## {row['protocol']} / {row['batch']} / {sid} / {cid}\n\nitem={row['item_id']}; partition={row['partition']}; load={row['load_layer']}; stratum={row['mechanism_group']}\n")
        if len(x):sections.append(table(x[['direction','representation','count_pre','count_post','bytes_pre','bytes_post','w_log2','w_bytes','ks','js_bits']]))
        else:sections.append(table(ss[(ss.session_id==sid)&(ss.connection_id==cid)][['direction','pre','post','difference','ratio']]))
    (DOC/'connection-details.md').write_text('\n\n'.join(sections)+'\n',encoding='utf-8')
    (DOC/'next-gate.md').write_text('# R9 停止门\n\n已通过资格、字节守恒、重分段和权限核验。记录级方法可行性研究结项；不自动新增分类、阶段搜索或全量提取。\n\n下一轮若要扩展，应先确定：仅扩大既有 PCAP 的表示测量，还是在冻结划分/模型下检验业务收益；需用户另行确认。SS cipher 与 Hy2 carrier 边界保持。\n',encoding='utf-8')
    js('report-artifacts.json',{'files':{str(f):digest(f) for f in [*DOC.glob('*.md'),*figdir.glob('*.png')]}})
    print('R9 report generated:',DOC/'report.md',flush=True)
