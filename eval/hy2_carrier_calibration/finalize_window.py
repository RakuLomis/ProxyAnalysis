"""Final fixed-task report and cross-arm identity checks, no new fitting."""
from experiment import *

def main():
    from package_audit import main as package_audit
    package_audit()
    assert read(OUT/'observed-roundtrip-audit.json')['passed']
    assert read(OUT/'path-scope-collision.json')['passed']
    assert read(OUT/'statistics-complete.json')['passed'] and read(OUT/'generation-replay.json')['passed']
    for name in ['learning-contract.json','classification-contract.json']:
        for p,h in read(OUT/name)['files'].items():assert sha(p)==h
    roles=pd.read_parquet(OUT/'roles.parquet');audits=[]
    for name,g in roles.groupby('scenario'):
        assert g.session_id.nunique()==100 and g.groupby('content_id').role.nunique().eq(1).all()
        for seed in SEEDS:
            ck=[]
            for arm in [*ARMS,'reference']:
                mode='reference' if arm=='reference' else 'restricted'
                ck.append(torch.load(OUT/'classifiers'/mode/name/f's{seed}-{arm}.pt',map_location=device(),weights_only=False))
            assert len({x['job']['initial_hash'] for x in ck})==1
            assert len({x['job']['schedule_hash'] for x in ck})==1
            for x in ck:
                np.testing.assert_array_equal(x['mean'],ck[0]['mean']);np.testing.assert_array_equal(x['scale'],ck[0]['scale'])
                assert set(x['scaler_fit_sessions'])==set(g[g.role=='C'].session_id)
            audits.append({'scenario':name,'seed':seed,'seven_arm_comparability':True})
    save('final-comparability-audit',audits)
    summary=pd.read_parquet(OUT/'metrics-summary.parquet');c=pd.read_parquet(OUT/'contrasts.parquet');primary=c[c.primary]
    assert len(primary)==2
    grouped=pd.read_parquet(OUT/'metrics-by-group.parquet');seeds=pd.read_parquet(OUT/'metrics-by-seed.parquet')
    ga=pd.read_parquet(OUT/'generation-audit.parquet');agg=ga.groupby('arm').agg(views=('views','sum'),direction_bound=('direction_bound','sum'),zero_direction=('zero_direction','sum'),sigmoid_endpoint=('sigmoid_endpoint','sum'),unique_views_mean=('unique_views_mean','mean')).reset_index()
    for col in ['direction_bound','zero_direction','sigmoid_endpoint']:agg[col+'_rate']=agg[col]/agg.views
    groups=read(OUT/'business-groups.json')['groups'];gp=pd.DataFrame([{'business_group':i,'target_businesses':' + '.join(g)} for i,g in enumerate(groups)])
    success=bool((primary.adjusted_low>0).all());status='通过' if success else '未同时通过'
    runtime=[]
    for mode in ['restricted','reference']:
        done=[read(p) for p in (OUT/'classifiers'/mode).glob('*/complete.json')]
        runtime.append({'mode':mode,'models':sum(x['models'] for x in done),'scenario_seconds_sum':sum(x['seconds'] for x in done)})
    write(OUT/'environment.json',{'torch':torch.__version__,'cuda':torch.version.cuda,'gpu':torch.cuda.get_device_name(),
                                'generator_dtype':'float64','classifier_dtype':'float32','TF32':False,'deterministic':True})
    figures(summary,grouped)
    report=f'''# Hy2 HFC-W：跨业务窗口摘要增广完整报告

日期：2026-09-28。状态：生成、训练、评分及最终审计完成。本轮冻结，不自动搜索参数。

## 1. 结论与主要结果

在五业务、目标两业务无训练post的预定设置中，paired相对raw和group的双重增量判据**{status}**。判据为两项F1_new的97.5%调整内容bootstrap区间下界均大于零，而非合法率、胜错配或CE改善。

{table(summary)}

![总体结果](figures/summary.png)

### 两项主比较

{table(primary[['contrast','delta','low95','high95','adjusted_low','adjusted_high']])}

F1值为0–1单位，差乘100为百分点。F1_new来自完整五类混淆矩阵，再取目标两类F1均值；并非简化二分类。所有结果先按五折OOF计算，再平均组合/轮换/seed，不做概率集成。

### 本轮结果的具体含义

paired的F1_new=0.612644，raw=0.029655，group=0.601417。相对raw提高58.299个百分点，97.5%调整区间为[51.779,63.777]个百分点；相对group提高1.123个百分点，调整区间为[-0.471,2.712]个百分点，跨零。因此只能确认当前变换增广相对原pre增广有用途，尚未建立精确访问对应超越该组级方法的额外用途。不能将区间跨零解释成方法等效或对应关系完全无信息。

paired相对center、marginal的F1_new分别提高12.664和10.343个百分点，普通95%区间分别为[8.080,17.086]与[6.035,14.550]个百分点。条件化方案有描述性优势，但group/cyclic也约为0.60，不能把全部优势归于真实实例身份。辅助对照不属于两项主要比较的同时覆盖声明。

reference的F1_new=0.680592，paired低6.795个百分点，普通95%区间为[-11.059,-2.745]个百分点，且新业务CE/Brier也不如reference。这不是合成数据已替代真实post的结果。

paired相对group的新业务CE/Brier差分别仅为-0.000593 bits和-0.000855，普通95%区间均跨零；不能在F1未通过时改用概率指标宣布成功。完整五类F1从raw的0.386594改善至paired的0.654907，但相对group的0.648007差距仍小。

十个业务组中，paired−group的20项家族调整区间均跨零。YouTube搜索＋播放组，paired=0.787300而group=0.832337，点估计反而更低；保留这一例外，不能只展示有利组。三个seed的paired合并均值均高于group，但seed不能替代内容级独立性，不能由此宣布显著。

每个100访问OOF中有40个目标业务访问，平均组/轮换/seed后：paired相对raw修复22.472个错误、新增0.011个；相对group修复1.750个、新增1.667个。重复运行的平均计数不是额外独立样本。

raw在十组中的七组F1_new为零，新业务CE达24.670 bits。这是当前混合C_post与U_pre训练在真实post上的严重失败表现，不是概率单位错误，也不是二分类指标；不能凭这个大增益单独证明精确配对必要。共享carrier、范围混杂及表示压缩可能影响实例关系的可利用性，但本轮没有把它们分别做因果对照，不能直接将未通过归因于多路复用。

## 2. 数据与测量口径

只使用0916 Hy2，五类各五内容，每内容四重复1/2/4/5，共25内容、100访问。Bing主目标DIRECT，Bilibili主目标DIRECT，均不进入主实验。旧SS/VLESS为六分类和不同摘要，不能把本次分数直接用于协议排名。

外部窗口固定manifest UTC [started_at,completed_at)，不是pre首尾或媒体播放进度。pre按完整flow-index绑定的主carrier成员在原始TUN中定位，post按carrier路径在原始physical捕获中定位。重建覆盖5520登记成员，不能只复用1526个请求关联成员。

六维为方向payload字节W、正payload事件数P、合并时间线方向段R。实际TCP重传和QUIC控制/恢复观测保留，不称唯一应用字节；R不是旧FR，不将内层F或carrier数放入分类输入。所有成员引用的同一原包只计一次。

200份原始文件约11.56GB；主carrier无重复纳入候选、会话窗口无重叠，5条跨候选生命周期引用中找到的2个旧carrier包全部排除在后续主输入之外。此结论限于所登记观察范围，不是所有网络历史无混杂的证明。

98个carrier创建事件未知，历史carry-in不完全可识别。用户确认窗口观测口径后保留这一限制。另有GitHub python/cpython一次访问的一个尾部成员无包：保留访问，只统计实际观测，不补零、不删除访问、不以缺失标记作特征；原失败审核门保留，另存accepted-window-gate。Wikipedia一次HTTP200但子资源失败的文章访问由用户确认有效，降级原字段保留。详见[原始包审核](measurement-audit.md)。

## 3. 资源预算与隔离

五内容外折继承既有内容ID：每折20训练内容/80访问，5测试内容/20访问。十种目标二业务组合全部报告；三辅助业务各选2内容构成C=6内容/24配对访问，U=14内容/56pre访问，其中目标业务32访问。六均衡轮换，每辅助内容入C三次；三seed为20260918/19/20。

生成器只用C；U只允许pre和既有标签；U_post单独导出，仅受限预测封存后的reference开放。H推理只有post，H_pre没有导出，H标签在预测封存后评分。匿名group包只有C的两侧无序内容数值集合，没有session/repetition/time/carrier身份。raw使用同样额外pre和标签，因此paired−raw不能归因于多拿源标签。

预处理只拟合C_pre，LOCO每次剔除整内容并重拟合。全部内容及访问保持C/U/H互斥。资格整理曾读取两侧原始数据，因此本轮不证明实际无需采集U_post，也不证明无内部索引的在线分段。

## 4. 生成模型与可行构造

令N=R_up+R_down、D=R_up−R_down、G=P−R、H=W−P、M=65526P。

编码为[log(N−.5),asinh(D),log(G_up+.5),log(G_down+.5),log((H_up+.5)/(M_up−H_up+.5)),log((H_down+.5)/(M_down−H_down+.5))]。

解码N=1+floor(exp(z_N))；N偶数时D=0、奇数时D取±1合法格点；R=(N±D)/2；非零方向P=R+floor(exp(z_G))，H=floor((M+1)sigmoid(z_H))，W=P+H；零方向联动归零。边界映射、整数格点及浮点sigmoid端点作用单独记录。L=65527是非jumbo传输payload的保守计数上界，不是实际MTU。

输出满足0≤R≤P≤W≤65527P、零方向联动与单条合并序列|D|≤1。此构造只保证摘要必要约束，不保证可运行QUIC会话或业务语义。溢出停止、零重抽、零fallback。

生成器6输入/6输出加截距42参数Ridge，alpha=1、均方目标、截距不罚。输入原六维log1p标准化；目标为新编码漂移，尺度仅C_pre编码标准差，常数维置1。group在新编码上取目标均值，并用4×4组合的内容LOCO联合残差；不复用真配池。

## 5. 对照与CUDA训练

raw：原pre；center：真实漂移逐维中位数；marginal：真实联合漂移随机抽样；paired：真配条件中心及LOCO残差；cyclic：同内容跨重复错配独立拟合；group：匿名组目标与独立残差；reference：额外真实U_post。center/marginal也依赖真实漂移，不能称为无配对参照。

分类器6→32→5 ReLU，Adam .001、1000步、batch24，权重平方损失.5×1e−4，bias不罚；无早停/搜索/BN/dropout。每来源访问300次，各臂同初值、同调度、同C_pre尺度。每U访问8生成视图，视图不增加独立内容数量。

生成及Ridge为CUDA float64，分类训练/推理CUDA float32，TF32关闭、确定性算法开启；CPU只做解析、台账、抽样、统计和绘图。6300次Ridge、2016000视图、5400受限分类器＋900reference，共6300模型/630万更新，126000预测行。实际独立内容仍25、访问仍100。

## 6. 各业务组合及随机种子

{table(gp)}

{table(grouped)}

![分组结果](figures/by-group.png)

逐seed均值：

{table(seeds)}

十组合的分组双重比較采用20项家族的99.75%区间，不能凭整体结论宣称每组都成立。单类F1/召回、CE、Brier、修复/新增错误、轮换结果以及全部比较见[详细结果表](results-tables.md)和error-ledger/error-counts。

## 7. 解码作用与多样性

{table(agg)}

合法率不是业务收益，边界发生率不能独立证明收益机制。这里direction_bound包含N为偶数时D必须归零的奇偶约束作用，不能把其发生率等同于严重越界或与旧FSC的F条件边界率直接比较。group残差池96条、paired/cyclic24条，均只来自6内容24访问；每查询同为8视图。零方向与边界映射可能改变分布，不称无失真生成。

## 8. 不确定性与解释边界

10000次按五业务分层内容bootstrap，保留重复、所有组/轮换/seed的关联；区间条件于已拟合模型和固定C设计。总体两主比较用家族2；十组的二比较用家族20。其他辅助比较的普通95%区间仅作描述；结果表中的调整分位列不构成所有辅助比较的同时覆盖声明。

paired若通过，支持当前已见Hy2部署、登记窗口与有限组级控制下的增广用途，不证明所有无配对方法不可能成功；若未通过，不扩网络、调阈值或换业务组合挽救结果。reference拥有额外真实post，非理论上界，差距不能因合成合法而忽略。

本次五分类/窗口观测不是旧六分类/唯一TCP字节实验的直接复刻。不能自动合并三个部署的显著性为一个新统一预登记结论；如需联合声明应单独报告六项主比较家族。不能主张QUIC解复用、逐flow生成、真实协议可实现、纯协议因果律、外部DIRECT迁移或实际采集节省。

## 9. 审计与复现

生成2016000视图逐条由保存模型及donor重放；组目标展开等价、匿名重排不变、异常数值停止、输入权限、CUDA串行/批量等价已验收。6300分类器checkpoint重载推理通过，900个scenario/seed核对七臂同初值/调度/尺度。19项回归测试通过，包括完整五类混淆矩阵的目标F1计算。

{table(pd.DataFrame(runtime))}

以上为各scenario累计阶段秒数，不是全任务墙钟时间。主要目录：`eval/hy2_carrier_calibration/`、`outputs/hy2-window-calibration-0916/run-01/`。accepted-window-gate、learning-contract、generation-replay、classification-contract、两次prediction-seal、statistics-complete与completion提供可追溯链。

本轮冻结，不自动新增模型、补采或调整成功标准。
'''
    (DOC/'summary.md').write_text(report,encoding='utf-8')
    write(OUT/'completion.json',{'status':'complete','classifiers':6300,'ridge_fits':6300,'generated_views':2016000,
          'prediction_rows':126000,'cuda':True,'both_primary_adjusted_intervals_positive':success,
          'report_hash':sha(DOC/'summary.md'),'finalizer_hash':sha(__file__),'new_fits_after_results':0})
    print(table(primary[['contrast','delta','adjusted_low','adjusted_high']]),flush=True)

def figures(summary,grouped):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    dest=DOC/'figures';dest.mkdir(parents=True,exist_ok=True)
    arms=[*ARMS,'reference'];g=summary.set_index('arm').loc[arms];x=np.arange(7)
    fig,ax=plt.subplots(figsize=(9,4));ax.bar(x-.18,g.F1_new,.36,label='F1 new');ax.bar(x+.18,g.F1_all,.36,label='F1 all')
    ax.set_xticks(x,arms,rotation=25);ax.set_ylim(0,1.05);ax.set_ylabel('OOF metric mean');ax.legend();fig.tight_layout();fig.savefig(dest/'summary.png',dpi=160);plt.close(fig)
    fig,ax=plt.subplots(figsize=(10,4))
    for arm in ['raw','paired','group','reference']:
        g=grouped[grouped.arm==arm].sort_values('business_group');ax.plot(g.business_group,g.F1_new,marker='o',label=arm)
    ax.set_xticks(range(10));ax.set_xlabel('Fixed target-business pair');ax.set_ylabel('F1 new');ax.legend();ax.grid(alpha=.2);fig.tight_layout();fig.savefig(dest/'by-group.png',dpi=160);plt.close(fig)
if __name__=='__main__':main()
