"""Final cross-regime identity, permission and numerical audit; detailed report."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'src'))
from proxy_analysis.feasible_summary_calibration.common import *
from proxy_analysis.conditional_drift.model import torch,device

def main():
    for name in ['contract.json','classification-contract.json']:
        for p,h in read(OUT/name)['files'].items():assert sha(p)==h
    assert read(OUT/'statistics-complete.json')['passed'] and read(OUT/'generation-audit.json')['passed']
    assert sha(OUT/'scored-predictions.parquet')==read(OUT/'statistics-complete.json')['scored_hash']
    pairs=pd.read_parquet(ROOT/'outputs/conditional-proxy-drift-0916/run-01/eligible-pairs.parquet')
    captures=pd.read_parquet(ROOT/'outputs/content-generalization-20260916/business-01/capture-files.parquet')
    roles=pd.read_parquet(OUT/'roles.parquet');identity=[];modelrows=[]
    for scenario,g in roles.groupby('scenario'):
        rr={r:set(v.session_id) for r,v in g.groupby('role')}
        for a,b in [('C','U'),('C','H'),('U','H')]:
            assert not rr[a]&rr[b]
            for frame,key in [(pairs,'connection_id'),(captures,'sha256')]:
                assert not set(frame[frame.session_id.isin(rr[a])][key])&set(frame[frame.session_id.isin(rr[b])][key])
        meta=read(SOURCE/'bundles/paired'/scenario/'manifest.json')
        assert not g[g.role=='C'].label_id.isin(meta['new_labels']).any()
        identity.append({'scenario':scenario,'content_parent_flow_capture_disjoint':True,'new_business_absent_in_C':True})
        for seed in config()['seeds']:
            checkpoints=[]
            for arm in ['raw','center','marginal','paired','cyclic','group','reference']:
                mode='reference' if arm=='reference' else 'restricted';path=OUT/'classifiers'/mode/scenario/f's{seed}-{arm}.pt'
                ck=torch.load(path,map_location=device(),weights_only=False);assert set(ck['scaler_fit_sessions'])==rr['C'];checkpoints.append(ck)
            assert len({c['job']['initial_hash'] for c in checkpoints})==1 and len({c['job']['schedule_hash'] for c in checkpoints})==1
            for ck in checkpoints:
                np.testing.assert_array_equal(ck['mean'],checkpoints[0]['mean']);np.testing.assert_array_equal(ck['scale'],checkpoints[0]['scale'])
            modelrows.append({'scenario':scenario,'seed':seed,'seven_arms_same_initial_schedule_scaler':True})
    save('final-identity-audit',identity);save('final-model-comparability-audit',modelrows)
    summary=pd.read_parquet(OUT/'metrics-summary.parquet');bygroup=pd.read_parquet(OUT/'metrics-by-group.parquet');contrast=pd.read_parquet(OUT/'contrasts.parquet');primary=contrast[contrast.primary]
    effects=pd.read_parquet(OUT/'decoder-effects.parquet');rates=effects.groupby(['protocol','arm']).sum(numeric_only=True).reset_index()
    for k in ['N_active','D_active','zero_direction']:rates[k+'_rate']=rates[k]/rates.views
    diversity=pd.read_parquet(OUT/'view-diversity.parquet').groupby(['protocol','arm']).unique_views.agg(['mean','min','max']).reset_index()
    seeds=pd.read_parquet(OUT/'metrics-by-seed.parquet');rot=pd.read_parquet(OUT/'metrics-by-rotation.parquet')
    runtime=[]
    for mode in ['restricted','reference']:
        done=[read(p) for p in (OUT/'classifiers'/mode).glob('*/complete.json')]
        runtime.append({'mode':mode,'scenarios':len(done),'models':sum(r['models'] for r in done),'sum_scenario_seconds':sum(r['seconds'] for r in done)})
    save('classification-runtime-summary',runtime)
    figures(summary,bygroup)
    outcomes=[]
    for dep,g in primary.groupby('protocol'):
        passed=bool((g.adjusted_low>0).all());delta=bool((g.delta>=.01).all());strong=bool((g.adjusted_low>.01).all())
        outcomes.append({'protocol':dep,'both_adjusted_lower_above_zero':passed,'both_points_at_least_1pp':delta,'both_adjusted_lower_above_1pp':strong})
    text='''# 可行摘要坐标增广：完整实验报告

日期：2026-09-28。状态：FSC0–FSC9完成。本轮结果冻结，不追加参数搜索。

## 1. 本轮回答什么

旧跨业务实验因VLESS生成候选违反上行R≤E等必要约束，在分类前停止。本轮按独立方案，将输出改成段数/方向差/事件余量/字节余量坐标与可行解码，保留业务角色、七维分类输入与固定模型。不是继续放宽旧10%门限，也不是把旧失败记录覆盖。

主要问题仍然是：在目标两业务没有训练post时，真配增广是否同时优于原pre增广和只知道内容组、不知道逐访问对应的增广。合法性按构造通过是实施条件，不是方法成功本身。

## 2. 结果概览

以下按部署先等权平均三个业务组、八轮换、三个seed的OOF指标，不进行概率集成。F1_new来自完整六分类混淆矩阵，再取该设置的两个未覆盖类F1均值。

'''
    text+=table(summary)+'\n\n![总体指标](figures/summary.png)\n\n'
    text+='### 按预定判据解释\n\n'
    for dep,g in primary.groupby('protocol'):
        raw=g[g.contrast=='paired-raw'].iloc[0];group_row=g[g.contrast=='paired-group'].iloc[0]
        text+=f"{dep}：paired相对raw的F1_new差为{raw.delta*100:+.3f}个百分点，相对group为{group_row.delta*100:+.3f}个百分点。"
        if raw.adjusted_low>0 and group_row.adjusted_low>0:text+='两项调整区间下界均大于零，满足本轮限定条件下的双重增量判据；不等于普遍必要性或外部泛化证明。'
        elif raw.adjusted_low>0:text+='相对原pre增广建立了当前区间口径下的正向证据，但相对组级方法的额外增量尚未建立；不能把变换用途全部归于精确配对。'
        elif group_row.adjusted_low>0:text+='相对组级方法有正向证据，但相对原pre增广的净用途尚未建立，双重主命题未同时通过。'
        else:text+='两项预定增量没有同时获得调整区间支持，不能以合法性通过替代业务有效性结论。'
        text+='\n\n'
    text+='### 两项预定主对照\n\n'
    text+=table(primary[['protocol','contrast','delta','low95','high95','adjusted_low','adjusted_high']])+'\n\n'
    text+='普通区间为95%；调整区间为四项主要比较的98.75%双侧内容bootstrap百分位区间。正差值有利于paired，F1为0–1单位。\n\n'+table(pd.DataFrame(outcomes))+'\n\n'
    text+='''同一部署两项调整区间下界都大于零，才符合预定双重增量判断。1个百分点只是操作性效果量参考；点估计过1pp和调整下界过1pp不同。不能以paired胜cyclic替代胜group，也不能在F1失败后改以CE作为主成功终点。具体结果的科学解释见后续结论，不由零非法率推导。

## 3. 数据、权限与任务

沿用0916六业务、30内容、240访问，SS/VLESS各120，四次重复{1,2,4,5}。五外折每部署训练24内容/96访问，测试6内容/24访问。C为6辅助内容/24配对访问，U为18内容/72个pre访问，其中两种post未覆盖业务32访问。八轮换及三个seed不增加独立内容数量。

固定业务组：g0=GitHub仓库+YouTube搜索；g1=Wikipedia文章+Bing搜索；g2=YouTube播放+MDN文档。没有删除视频、重选业务或改变标签。

生成拟合仅用C，U_pre仅查询。group生成包不含校准session/repetition/时间/连接索引或post F，只保留无序两侧数值与内容关联。分类输入仅七维数值，无IP、端口、SNI或身份信息。reference在受限预测封存后独立运行，才开放U_post；没有反馈主实验。

原共同连接资格和F仍来自历史双侧审计，本轮不等于证明可以完全不采集U_post。当前所有结果是既有数据上的后续研究，不是新外部盲测。

## 4. 编码、解码与生成目标

原输入为U_up/down、E_up/down、R_up/down和F；R为连接零阈值新字节方向段数之和，不是旧FR。

新编码只用一侧六维：N=R_up+R_down，D=R_up−R_down，G=E−R，H=U−E；编码为[log(N+.5),asinh(D),log(G_up+.5),log(G_down+.5),log(H_up+.5),log(H_down+.5)]，不需要post F。

解码Q(z)=floor(exp(z))保证非负整数；N=max(F,Q(z_N))。D先限制在F允许范围，再取与N同奇偶的合法格点。R=(N±D)/2；非零方向E=R+G、U=E+H；零R方向联动令E/U为零，并记录忽略余量。所有输出需满足精确整数范围，溢出停止而不裁剪或fallback。

这是包含边界映射的支持保持解码，不是完全无投影、无分布变化的生成器。各生成臂共用它；一次donor抽取只解码一次，不拒绝重抽。

Ridge仍为7输入/6输出、含截距48参数，alpha=1，截距不罚，CUDA float64。输入原pre七维log1p按C标准化；输出漂移改为新编码，输出尺度只用C_pre编码的总体标准差，常数维置1。容量和正则系数不变，但目标几何改变，不能声称损失与旧模型完全一样。

group的目标为该内容全部post编码的均值，不是原始均值再编码。LOCO重新拟合，逐内容生成4×4完整残差，仍只代表四次真实重复。展开平方目标与均值目标在新坐标重新验证，未借用旧目标证明或真配残差。

## 5. 全部对照与分类配置

| 臂 | U输入/监督资源 |
|---|---|
| raw | 原pre与标签 |
| center | 固定新坐标漂移中心 |
| marginal | 无条件联合新坐标漂移 |
| paired | 真配条件中心+内容LOCO残差 |
| cyclic | 同内容跨重复循环错配，独立重拟合 |
| group | 匿名内容组目标+笛卡尔积LOCO残差 |
| reference | 独立额外权限真实U_post |

所有臂C部分均为真实post；分类器输入仍是还原后的原七维，不提供潜变量。共同分类尺度仅C_pre原七维log1p。模型7→32→6 ReLU，Adam .001，1000步，batch24，CE(nats)+.5×10⁻⁴权重平方和，bias不罚，无BN/dropout、无早停或搜索。每来源访问250次，七臂初值和调度一致，seed为20260918/19/20。

全部拟合、训练、模型推理使用Pytorch312 CUDA；CPU仅用于数据管理、随机抽样、统计和绘图。独立分类器批量计算，不共享模型参数，工程阶段验证串行等价和模型维隔离。

## 6. 解码作用不等于无失真

2073600生成视图全部通过独立旧约束检查，零重抽、零fallback。N下界映射、D边界和零方向联动的发生率如下：

'''
    text+=table(rates[['protocol','arm','views','N_active_rate','D_active_rate','zero_direction_rate']])+'\n\n'
    text+='D边界位移保存在潜变量坐标；整数格点量化单独记录，不与幅度截界混合。零方向被忽略的G/H和输出分位数均有台账。合法性不保证协议会话可实现或标签保真。\n\n每源访问每seed的八视图实际去重数：\n\n'+table(diversity)+'\n\n'
    text+='固定中心重复视图不创造额外信息。离散解码可能合并不同潜变量；没有按多样性或边界发生率选择臂或调整参数。\n\n'
    text+='## 7. 业务组、seed和错误变化\n\n'+table(bygroup)+'\n\n![业务组结果](figures/by-group.png)\n\n'
    text+='逐seed均值：\n\n'+table(seeds)+'\n\n'
    text+='逐业务召回/F1、各组逐轮换、paired相对其他臂的修复/新增错误、所有CE/Brier对照和次级区间见[完整结果表](results-tables.md)及输出error-ledger/error-counts。group0/1/2的成绩全部保留，不依据结果改换主问题。\n\n'
    text+='''### 不能被总体均值掩盖的差异

SS的主要收益集中在g2：paired相对raw的F1_new提高55.050个百分点；g1的raw已经达到0.958529，paired为0.955898，略低0.263个百分点。采用12项次级比较的调整区间后，分组双重增量仅在SS的g2，以及VLESS的g1/g2同时成立。g0中paired相对group的额外增量，在两个部署均未取得相应调整区间支持。因此总体主终点成立，不等于每个业务组均成立。

SS的center、marginal也很强：paired相对center仅提高0.367个百分点，普通95%区间为[-0.511,1.251]个百分点；相对marginal为-0.233个百分点，普通95%区间为[-0.766,0.254]。这些结果不支持SS中条件生成器必不可少；但center/marginal自身使用了真配漂移，不能将它们称为完全不需要对应信息的控制。

VLESS的paired仍比额外权限reference低7.403个百分点F1_new，普通95%区间为[-13.200,-3.409]个百分点。YouTube搜索的paired单类F1仅0.415717、召回0.308333；GitHub的单类F1则由raw的0.952997降至paired的0.920369。YouTube播放由raw的零召回改善至0.768750，但这些例外说明生成并未普遍保持或恢复所有业务边界。

按每个120访问OOF中的40个目标业务访问计数，再平均组/轮换/seed：SS的paired相对raw平均修复10.264个错误、新增0.528个；相对group修复3.208个、新增0.111个。VLESS对应为12.931/0.958，以及6.625/1.417。它们是重复实验平均计数，不是新增独立样本。

当前支持的是：在本次固定预算和目标业务无训练post的设置中，新方法相对原pre增广及所登记的匿名内容组控制均有总体业务增量。它不证明优于所有可能的非逐访问配对方法，也不将零非法率本身解释为业务收益。

## 8. 不确定性与边界

每个组/轮换/seed先合并五折的120个访问评分，再平均。10000次bootstrap按六业务分层抽取内容，保留重复及全部部署/组/轮换/seed的关联。区间条件于现有模型和固定校准集合，不包含重新采C并重训的全部不确定性。4个主要比较做Bonferroni区间；如讨论限定业务组的双重优势，使用12个次级比较的同时处理，不能事后缩小家族。

完整对照表还保存了辅助比较的调整分位数列；四项/十二项家族的覆盖声明仅用于预登记主比较及分组双重比较，不覆盖表中所有辅助对照。上述简单参照与逐业务解释属于描述性结果，不另行宣布多重检验成功。

reference使用同尺度、网络、步数及调度，但拥有额外真实post，是匹配训练预算的额外数据参考而非理论上界。由于旧拒绝版本未完成分类，本轮不能宣称业务性能优于旧版本；合法性改动、目标几何与边界映射一起构成方法，不能把结果唯一归因于其中一个因素。

本轮不能直接证明实际采集节省、标签节省、合法TCP协议生成、精确协议开销、Hy2共享载体支持、跨未知配置/日期或外部DIRECT泛化。所有测试内容仍来自反复研究的0916。

## 9. 执行规模与最终审计

240scenario；5040次CUDA Ridge；2073600生成视图；4320受限分类器+720额外权限参考=5040分类器，504万次更新；120960预测行，但真实访问240、独立内容30。

观测编码/解码往返、随机与边界样例、数值溢出停止、组目标等价和排列不变、LOCO来源、旧独立约束、全量CUDA解码重放、逐模型加载重放及C/U/H flow/capture互斥均核对通过。七臂同scenario/seed初值、来源调度与分类scaler精确一致。

'''
    text+=table(pd.DataFrame(runtime))+'\n\n时间为逐scenario阶段累计，不等于整个任务墙钟时间。生成耗时另见generation-runtime.parquet。\n\n'
    text+='''## 10. 文件和复现

- 计划：`plan/feasible-summary-calibration-plan-20260928.md`。
- 配置：`configs/feasible-summary-calibration-0916.yaml`。
- 核心代码：`src/proxy_analysis/feasible_summary_calibration/`。
- 执行脚本：`eval/feasible_summary_calibration/`。
- 完整模型、预测、bootstrap、日志：`outputs/feasible-summary-calibration-0916/run-01/`。
- 本报告及图：`docs/feasible-summary-calibration-0916/`。

关键封存文件包括contract、generation-gate、generation-audit、classification-contract、restricted/reference-prediction-seal、statistics-complete和completion。旧XBC失败与拒绝诊断文件未覆盖。

本轮到此冻结。无论两项主要比较是否同时成立，均不自动扩大网络、加入flow生成、调整残差池或搜索权重。下一研究需要用户单独确定。
'''
    env=read(OUT/'environment.json')
    env_note=f"实际环境：Python 3.12.8 / Pytorch312，PyTorch {env['torch']}、CUDA {env['cuda_runtime']}，{env['gpu']}；Ridge/编解码float64，分类float32，TF32关闭，确定性算法开启。18项相关回归测试通过，记录见outputs/feasible-tests-complete.xml。\n\n"
    text=text.replace('## 6. 解码作用不等于无失真',env_note+'## 6. 解码作用不等于无失真')
    (DOC/'summary.md').write_text(text,encoding='utf-8')
    write(OUT/'completion.json',{'status':'complete','stages':[f'FSC{i}' for i in range(10)],'CUDA':True,'ridge_fits':5040,'classifiers':5040,'generated_views':2073600,'prediction_rows':120960,
        'new_fits_after_results':0,'old_experiments_unchanged':True,'primary_outcomes':outcomes,'report_hash':sha(DOC/'summary.md'),
        'source_hashes':{str(p):sha(p) for p in [*Path(__file__).parent.glob('*.py'),*Path(ROOT/'src/proxy_analysis/feasible_summary_calibration').glob('*.py'),CONFIG]}})
    print('FSC0-FSC9 complete',outcomes,flush=True)

def figures(summary,group):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    dest=DOC/'figures';dest.mkdir(exist_ok=True,parents=True);arms=['raw','center','marginal','paired','cyclic','group','reference']
    fig,axes=plt.subplots(1,2,figsize=(13,4.5),sharey=True)
    for ax,dep in zip(axes,['SHADOWSOCKS','VLESS']):
        g=summary[summary.protocol==dep].set_index('arm').loc[arms];x=np.arange(7)
        ax.bar(x-.18,g.F1_new,width=.36,label='F1 new');ax.bar(x+.18,g.F1_all,width=.36,label='F1 all');ax.set_xticks(x,arms,rotation=35,ha='right');ax.set_title(dep);ax.set_ylim(0,1.05);ax.grid(axis='y',alpha=.2)
    axes[0].set_ylabel('OOF metric mean (not ensemble)');axes[1].legend();fig.tight_layout();fig.savefig(dest/'summary.png',dpi=160);plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(12,4),sharey=True)
    for ax,dep in zip(axes,['SHADOWSOCKS','VLESS']):
        for arm in ['raw','paired','group','reference']:
            g=group[(group.protocol==dep)&(group.arm==arm)].sort_values('business_group');ax.plot(g.business_group,g.F1_new,marker='o',label=arm)
        ax.set_title(dep);ax.set_xticks([0,1,2],['g0','g1','g2']);ax.set_xlabel('Fixed target-post-uncovered business group');ax.grid(alpha=.2)
    axes[0].set_ylabel('F1 new');axes[1].legend();fig.tight_layout();fig.savefig(dest/'by-group.png',dpi=160);plt.close(fig)

if __name__=='__main__':main()
