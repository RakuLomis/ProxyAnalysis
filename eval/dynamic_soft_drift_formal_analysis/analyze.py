"""Read-only formal-result replay and descriptive closeout; no fits or tuning."""
from pathlib import Path
import hashlib
import json
import datetime as dt
import numpy as np
import pandas as pd
import torch

ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'outputs/dynamic-soft-drift-business-formal-20261012/run-02'
OUT=ROOT/'outputs/dynamic-soft-drift-business-formal-analysis-20261013/run-01'
DOC=ROOT/'docs/dynamic-soft-drift-calibration/formal-20261012/run-02/complete-results-analysis-20261013.md'
ARMS=['D-P','T-P','D-G','S','P-small','G-small','RawPre-small','RawPost-small','Marginal-small','M-S']
LABELS=['bing.com::search_results_view','developer.mozilla.org::document_view','github.com::repository_view',
        'wikipedia.org::article_view','youtube.com::search_results_view','youtube.com::video_playback']
LABEL_NAMES=['Bing搜索','MDN文档','GitHub仓库','Wikipedia文章','YouTube搜索','YouTube视频']
BLOCKS=['W_up','W_down','U_up','U_down','P_up','P_down','E_up','E_down','FR_packet_runs','R_unique_zero_runs']
MASKS={'G0':[2,4],'G1':[0,3],'G2':[1,5]}
PROTO={'shadowsocks':'SS','vless':'VLESS','trojan':'Trojan','vmess':'VMess'}
PC=[f'p{i}' for i in range(6)];LC=[f'l{i}' for i in range(6)]
READS={}

def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def relative(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def require(ok,s):
    if not bool(ok):raise RuntimeError(s)
def record(p):READS[relative(p)]=sha(p)
def write(p,v):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False,default=lambda x:x.item() if isinstance(x,np.generic) else str(x))+'\n',encoding='utf-8')
def save(d,name):
    p=OUT/(name+'.parquet');p.parent.mkdir(parents=True,exist_ok=True);d.to_parquet(p,index=False)
def table(d):return d.to_markdown(index=False,floatfmt='.6f')

def independent_metrics(d):
    y=d.label_id.map(dict(zip(LABELS,range(6)))).to_numpy(int);z=d.prediction.to_numpy(int)
    cm=np.zeros((6,6),dtype=np.int64)
    np.add.at(cm,(y,z),1)
    den=cm.sum(0)+cm.sum(1);f=np.divide(2*cm.diagonal(),den,out=np.zeros(6),where=den>0)
    u=np.isin(y,MASKS[d.group.iloc[0]])
    ce=-d[LC].to_numpy()[np.arange(len(y)),y]
    br=np.square(d[PC].to_numpy()-np.eye(6)[y]).sum(1)
    return dict(F1_all=f.mean(),F1_U=f[MASKS[d.group.iloc[0]]].mean(),F1_C=np.delete(f,MASKS[d.group.iloc[0]]).mean(),
                accuracy=(y==z).mean(),CE=ce.mean(),CE_U=ce[u].mean(),CE_C=ce[~u].mean(),
                Brier=br.mean(),Brier_U=br[u].mean(),Brier_C=br[~u].mean())

def main():
    require(not (OUT/'completion.json').exists(),'Refuse completed analysis overwrite')
    completion=read(RUN/'completion.json');record(RUN/'completion.json')
    require(completion['passed'] and completion['formal_complete'] and completion['H_scored'],'Formal matrix not complete')
    require(sha(RUN/'verification.json')==completion['verification_sha256'],'Completion verification hash')
    verification=read(RUN/'verification.json');record(RUN/'verification.json')
    require(verification['passed'],'Formal integrity not accepted')
    contract=read(RUN/'manifests/experiment-contract.json');record(RUN/'manifests/experiment-contract.json')
    require(sha(RUN/'manifests/experiment-contract.json')==read(RUN/'manifests/seal.json')['contract_sha256'],'Contract changed')
    for p,h in contract['code'].items():require(sha(ROOT/p)==h,'Changed frozen training code '+p)
    critical=['scores/pooled.parquet','scores/targets.parquet','scores/classes.parquet','scores/scenarios.parquet',
              'scores/labeled-predictions.parquet','scores/error-flips.parquet','comparisons/primary.json','comparisons/bootstrap.npz',
              'manifests/endpoints.parquet','manifests/models-complete.json','predictions/complete.json','predictions/visits.parquet','ledger.json']
    for name in critical:
        p=RUN/name;require(sha(p)==verification['files'][relative(p)],'Changed sealed result '+name);record(p)
    pooled=pd.read_parquet(RUN/'scores/pooled.parquet').set_index('arm').loc[ARMS]
    targets=pd.read_parquet(RUN/'scores/targets.parquet');classes=pd.read_parquet(RUN/'scores/classes.parquet')
    data=pd.read_parquet(RUN/'scores/labeled-predictions.parquet');require(len(data)==14400,'Prediction exposure count')
    require(data.visit_id.nunique()==480 and data.content_id.nunique()==30,'Cohort count')
    scenes=[]
    for (arm,p,g),d in data.groupby(['arm','target','group']):
        require(len(d)==120 and d.visit_id.is_unique and d.content_id.nunique()==30,'OOF scene coverage')
        scenes.append(dict(arm=arm,target=p,group=g,**independent_metrics(d)))
    independently=pd.DataFrame(scenes).groupby('arm')[list(independent_metrics(data.iloc[:120]).keys())].mean()
    error=float((independently.loc[ARMS]-pooled.loc[ARMS,independently.columns]).abs().to_numpy().max())
    require(error<1e-12,'Independent metric replay')
    folds={r['outer']:set(r['validation_contents']) for r in contract['roles']}
    for r in contract['roles']:
        require(set(r['validation_contents'])==folds[r['outer']] and not set(r['train_contents'])&folds[r['outer']],'Global content isolation')
    for r in contract['inner_roles']:
        require(not (set(r['train_contents'])|set(r['validation_contents']))&folds[r['outer']],'Source task saw outer test content')
    boot=np.load(RUN/'comparisons/bootstrap.npz',allow_pickle=False)
    order=list(boot['arms']);comparisons=read(RUN/'comparisons/primary.json');primary=[]
    for row in comparisons['comparisons']:
        reference=row['reference'];delta=boot['F1_U'][:,order.index('D-P')]-boot['F1_U'][:,order.index(reference)]
        ci=np.quantile(delta,[.05/14,1-.05/14]);require(np.max(abs(ci-np.array(row['CI_99_285714'])))<1e-12,'Saved interval replay')
        point=float(pooled.loc['D-P','F1_U']-pooled.loc[reference,'F1_U'])
        require(abs(point-row['delta_F1_U'])<1e-12,'Primary point replay')
        primary.append(dict(reference=reference,delta_pp=point*100,CI_low_pp=ci[0]*100,CI_high_pp=ci[1]*100,passed=bool(ci[0]>0)))
    primary=pd.DataFrame(primary);save(primary,'primary-replay')
    frames=[]
    for p in (RUN/'trajectories').rglob('*.parquet'):
        require(sha(p)==verification['files'][relative(p)],'Changed sealed q trajectory');record(p);frames.append(pd.read_parquet(p))
    trajectories=pd.concat(frames,ignore_index=True)
    require(len(trajectories)==3780,'Trajectory state count')
    summary=[];qsummary=[];penalty=[]
    for arm,d in trajectories.groupby('arm'):
        a=d[d.state.eq(0)].set_index('role_id');b=d[d.state.eq(20)].set_index('role_id').loc[a.index]
        require(len(a)==len(b)==60 and d.groupby('role_id').state.apply(lambda z:sorted(z)==list(range(21))).all(),'Full fixed q trajectory')
        q=np.stack(b.q);lam=np.stack(b.lambda_closed);tg=np.stack(b.task_gradient);pg=np.stack(b.penalty_gradient);gg=np.stack(b.total_gradient)
        summary.append(dict(arm=arm,Q_initial=a.Q.mean(),Q_final=b.Q.mean(),Q_delta=(b.Q-a.Q).mean(),Q_worse=int((b.Q>a.Q).sum()),
                            total_initial=a.total.mean(),total_final=b.total.mean(),total_delta=(b.total-a.total).mean(),total_worse=int((b.total>a.total).sum()),
                            penalty_final=b.penalty.mean(),active_roles=int((lam>0).any(1).sum()),active_blocks=int((lam>0).sum()),
                            task_grad_Linf_median=np.median(abs(tg).max(1)),penalty_grad_Linf_median=np.median(abs(pg).max(1)),
                            total_grad_Linf_median=np.median(abs(gg).max(1)),q_RMS_deviation=np.sqrt(np.mean((q-1)**2)),
                            q_min=q.min(),q_max=q.max(),boundary_coeffs=int(((q==0)|(q==2)).sum())))
        for j,n in enumerate(BLOCKS):qsummary.append(dict(arm=arm,block=n,mean=q[:,j].mean(),std=q[:,j].std(),min=q[:,j].min(),max=q[:,j].max()))
        for k in [1,20]:
            z=d[d.state.eq(k)];g=np.stack(z.gap);grad=np.stack(z.penalty_gradient);c=(np.maximum(g,0)**2).mean(0)/20
            for j,n in enumerate(BLOCKS):penalty.append(dict(arm=arm,state=k,block=n,mean_penalty=c[j],median_abs_gradient=np.median(abs(grad[:,j]))))
    summary=pd.DataFrame(summary);qsummary=pd.DataFrame(qsummary);penalty=pd.DataFrame(penalty)
    save(summary,'meta-summary');save(qsummary,'q-block-summary');save(penalty,'penalty-block-summary')
    state_means=trajectories.groupby(['arm','state'])[['Q','penalty','total']].mean().reset_index();save(state_means,'state-means')
    co=[]
    for p in (RUN/'C-coefficients').rglob('*.pt'):
        require(sha(p)==verification['files'][relative(p)],'Changed C coefficient');record(p)
        # CPU is used only for IO/statistical summaries, not fitting or inference.
        c=torch.load(p,map_location='cpu',weights_only=True)
        for j,n in enumerate(BLOCKS):co.append(dict(kind=p.stem,block=n,s=float(c['s'][j]),raw_variance=float(c['raw_variance'][j]),A_over_s=float(c['A'][j]/c['s'][j])))
    coefficients=pd.DataFrame(co);geometry=coefficients.groupby(['kind','block']).agg(variance_median=('raw_variance','median'),floor_hits=('raw_variance',lambda z:int((z<1e-6).sum())),A_over_s_median=('A_over_s','median'),A_over_s_max=('A_over_s','max')).reset_index();save(geometry,'coefficient-geometry')
    flips=pd.read_parquet(RUN/'scores/error-flips.parquet')
    yy=flips.label_id.map(dict(zip(LABELS,range(6)))).to_numpy(int)
    flips['scope']=['U' if y in MASKS[g] else 'C' for y,g in zip(yy,flips.group)]
    flip_summary=flips.groupby(['reference','scope'])[['repaired','introduced','prediction_changed']].sum().reset_index();save(flip_summary,'error-flip-summary')
    counts=flips.groupby('reference')[['repaired','introduced','prediction_changed']].sum().reset_index();save(counts,'error-flips-all')
    deployment=[]
    for protocol,name in PROTO.items():
        d=targets[targets.target.eq(protocol)].set_index('arm')
        deployment.append(dict(protocol=name,D_P=d.loc['D-P','F1_U']*100,P_small=d.loc['P-small','F1_U']*100,T_P=d.loc['T-P','F1_U']*100,D_G=d.loc['D-G','F1_U']*100,
                               S=d.loc['S','F1_U']*100,delta_vs_P_small_pp=(d.loc['D-P','F1_U']-d.loc['P-small','F1_U'])*100,delta_vs_S_pp=(d.loc['D-P','F1_U']-d.loc['S','F1_U'])*100))
    deployment=pd.DataFrame(deployment);save(deployment,'deployment-comparison')
    business=classes[classes.uncovered].groupby(['label','arm']).F1.mean().unstack().loc[LABELS,ARMS]*100
    business.insert(0,'business',LABEL_NAMES);business['delta_D_P_minus_P_small_pp']=business['D-P']-business['P-small'];business=business.reset_index(drop=True);save(business,'uncovered-business')
    fmt=pd.concat([pd.read_parquet(p) for p in (RUN/'audits/format').rglob('*.parquet')],ignore_index=True)
    fmt=fmt.groupby('arm').agg(block_view_exposures=('rows','sum'),strict_negative_exposures=('negative_rows','sum'),max_block_sum_error=('block_sum_max_error','max')).reset_index();save(fmt,'view-format')
    ledger=read(RUN/'ledger.json');start=dt.datetime.fromisoformat(read(RUN/'launch.json')['started_local']).replace(tzinfo=dt.timezone(dt.timedelta(hours=8)))
    end=dt.datetime.fromtimestamp(read(RUN/'progress.json')['time_unix'],dt.timezone(dt.timedelta(hours=8)));elapsed=(end-start).total_seconds()
    audit=dict(passed=True,independent_metric_error=error,primary_intervals_replayed=7,global_outer_content_isolation=True,
               source_task_outer_H_exclusion=True,predictions=14400,unique_visits=480,unique_contents=30,
               trajectory_states=3780,variance_floor_hits=int((coefficients.raw_variance<1e-6).sum()),
               original_verification_files=len(verification['files']),original_verification_sha256=completion['verification_sha256'],
               start=start.isoformat(),end=end.isoformat(),elapsed_seconds=elapsed,new_model_fits=0,hyperparameters_selected=False,
               model_checkpoints_changed=False,new_statistical_families=0)
    write(OUT/'audit.json',audit)
    overall=pooled.reset_index()[['arm','F1_U','F1_all','F1_C','CE_U','Brier_U','worst_protocol_F1_U']].copy()
    for name in ['F1_U','F1_all','F1_C','worst_protocol_F1_U']:overall[name]*=100
    pt=primary.copy();pt['校正区间百分点']=[f'[{a:+.3f}, {b:+.3f}]' for a,b in zip(pt.CI_low_pp,pt.CI_high_pp)]
    selected_meta=summary[['arm','Q_initial','Q_final','Q_worse','total_initial','total_final','total_worse','total_grad_Linf_median']]
    curve=state_means[state_means.state.isin([0,1,2,5,10,15,20])]
    dp_pen=penalty[penalty.arm.eq('D-P')].pivot(index='block',columns='state',values='mean_penalty').loc[BLOCKS].reset_index();dp_pen.columns=['block','step1_penalty','step20_penalty']
    geom=geometry[geometry.kind.eq('P')][['block','variance_median','floor_hits','A_over_s_median','A_over_s_max']]
    source_checks=dict(max_original_gradient=float(trajectories.max_original_gradient.max()),max_mean_hyper_gradient_difference=float(trajectories.mean_gradient_max_difference.max()),max_member_hyper_gradient_difference=float(trajectories.max_task_gradient_difference.max()))
    write(OUT/'source-check-extrema.json',source_checks)
    lines=['# 动态软约束漂移正式业务实验结果分析','', '分析日期：2026年10月13日。实验版本：run-02。','',
           '正式矩阵完整通过，D-P相对强单侧参照S的未覆盖业务F1提升2.559个百分点，且通过七项预登记联合校正；但相对P-small、T-P、D-G及其他主参照均未建立校正后的增量。D-P没有改善P-small的整体六分类F1或概率质量。',
           '', '另一个关键限制来自外层优化：充分求解LR与隐式微分通过验收，不等于固定20步Adam已充分优化q。D-P与D-G的终态总目标在多数角色中高于起点，软惩罚有显著振荡，且主要集中在上行包数和上行新字节事件数两块。当前结果应解释为这套固定有限优化程序的业务结果，不能推广为动态关系约束或真实对应普遍无用。',
           '', '## 完成状态和实际成本','',
           f'正式计算从{start:%Y年%m月%d日 %H:%M:%S}运行至{end:%Y年%m月%d日 %H:%M:%S}，均为北京时间，耗时约{elapsed/3600:.3f}小时，即6小时31分钟。没有提前终止、跳过角色或回选checkpoint。早期10至14小时估计偏保守，后续任务的实测耗时更低。',
           '',table(pd.DataFrame([ledger])),'',
           '共完成60角色、180条q轨迹、3600次更新和3780个q状态；43920个新源内LR加180个最终业务LR，共44100个新完整LR。1440次缓存命中解释了45360次逻辑前向暴露与真实新求解数的差异。',
           '',f'原完成状态为formal_business_complete，验证清单包含{len(verification["files"])}份文件。分析重新核对了完成清单哈希、关键评分文件及训练源码哈希，独立重算指标最大误差为{error:.3g}，七项区间均从封存bootstrap分布准确重放。没有新拟合、改参数或增加检验家族。',
           '', '## 数据任务和权限','',
           '使用extend中SS、VLESS、Trojan、VMess四个TCP部署的既有共同有效队列。共有480次真实访问、30个内容、六业务，每内容每部署四次重复；不包含AnyTLS、Hy2、64 URL尝试或旧0914/0916队列。',
           '', '六业务为Bing搜索、MDN文档、GitHub仓库、Wikipedia文章、YouTube搜索与YouTube视频。五折全局内容留出，四目标部署与三个遮蔽组组合成60个角色。G0遮蔽GitHub和YouTube搜索；G1遮蔽Bing和Wikipedia；G2遮蔽MDN和YouTube视频。',
           '', '每角色有三源部署24个训练内容、288次访问；实际目标C允许四业务16内容64访问，含训练标签；目标U的两业务8个训练内容32访问，两侧完全禁用。目标H有六个未见内容24次post访问。所有端点封存后才查询H，全部预测封存后才读取H标签。',
           '', '每个外层角色包含12个来源于外层训练区的模拟任务，全矩阵共720个。源内反馈只使用伪目标留出内容中未覆盖两类的8次post CE。这些反馈被反复用于学习q，不能当作独立泛化评价。分析再次核对了所有源内任务均未接触外层H内容。',
           '', '分类单位是访问级96维统计直方图，不是单flow分类。所有同内容的协议、重复、两侧、内部连接与视图遵循共同内容划分。IP、端口、SNI、协议ID、URL文字和配置路径不进入数值输入；标识仅用于关联、分组和评分。当前读取合同支持这种隔离，不能替代外部批次验证或排除所有环境可预测线索。',
           '', '## 方法和冻结配置','',
           '| 臂 | 映射与训练反馈 | 关系约束 |\n| --- | --- | --- |\n| D-P | 精确P映射和源内解级Q | 精确C-OOF增量软惩罚 |\n| T-P | 与D-P相同的P资源 | 无关系软惩罚 |\n| D-G | 匿名内容组G映射和自身Q | 匿名全部组合的C-OOF增量软惩罚 |',
           '', 'T-P仍使用P映射，不是完全无配对基线。D-P与D-G比较的是整个对应权限管线，不能把差别全部归因于惩罚。七类旧参照为S、P-small、G-small、RawPre-small、RawPost-small、Marginal-small、M-S，共420个冻结端点；S本身包含原CORAL来源变换，不是故意弱化的raw参照。M-S保持其自己的原选参来源，不与S混同。',
           '', '十块为W/U/P/E上下行、FR_packet_runs、R_unique_zero_runs。每角色只学习一个十维q，训练期间更新，最终测试时冻结；不是逐访问门控或在线自适应。输出为a加q乘以原基础映射b0减a。q=1对应旧基础映射，不是pre/post恒等假设。',
           '', '最终LR有928行加权槽位：288原post、288 CORAL、288调整pre、64实际C-post。90% CORAL与10%调整pre属于辅助槽位，调整pre总CE质量为1/30。总质量1、六类先验各1/6；原权重L2系数0.0005乘1+t，bias不正则化。源内每任务480行。',
           '', 'q从全1开始，范围[0,2]，Adam学习率0.05、beta为0.9/0.999、epsilon为1e-8，固定20次更新加q20终态审计。收缩rho为0.01、关系权重nu为1，共享方差下限1e-6。固定选择q20，不选择最低源内CE或最高H F1的历史状态。',
           '', '源内LR使用CUDA float64原LBFGS预算2000迭代/10000评价，原坐标梯度门1e-5；同目标Newton精炼至1e-9，最多30步；再执行一次独立完整Newton校验和f/v双隐式梯度核验。所有实际点遵循同一政策，没有转回有限展开，也没有给主臂额外精度。',
           '', '## 整体业务结果','',table(overall),'',
           'F1列为百分数；CE单位为nat，越低越好；Brier越低越好。F1_U由每部署、遮蔽组合合并五折的完整六类混淆矩阵计算，再取未覆盖两类并等权平均。它不是U二分类，也不是逐折F1的平均。',
           '', 'D-P的F1_U为79.830%，比P-small高0.137个百分点，但整体六类F1由81.767%降为81.392%，准确率也下降。CE_U由0.861347增至0.885381，Brier_U由0.383276增至0.389194。当前不是多指标一致改善。',
           '', '## 七项主比较','',table(pt[['reference','delta_pp','校正区间百分点','passed']]),'',
           '共享内容bootstrap为10000次、种子20261012，六业务分层，每业务五内容，同一内容在所有部署、重复、遮蔽和臂中共享重采样质量。七项家族的Bonferroni名义区间为99.285714%。只有D-P减S的下界严格大于0。',
           '', 'D-P减M-S的普通95%区间为[0.314,4.057]个百分点，但主家族校正区间跨0，不能把它改判为主比较通过。核心三项D-P减P-small、T-P、D-G的普通95%区间也跨0。未建立增量不等于证明等效，更不等于证明所有配对方法无效。',
           '', '## 部署异质性','',table(deployment),'',
           '部署分项属于描述性结果，没有追加独立显著性家族。D-P相对P-small在SS增加1.590个百分点、VLESS增加0.693个百分点，在Trojan下降0.522个百分点、VMess下降1.214个百分点。合并结果的小幅正值包含两升两降。',
           '', '最差部署F1_U由P-small的71.652%提高到D-P的73.243%，但RawPre-small的最差值为74.187%。D-P相对S的主要提升集中于SS，不能表述成各协议都有同等收益。',
           '', '## 逐业务结果','',table(business[['business','D-P','P-small','T-P','D-G','S','delta_D_P_minus_P_small_pp']]),'',
           '此表只汇总每业务处于目标未覆盖组时的完整六类CM分项，再在四部署之间平均。GitHub相对P-small下降约0.788个百分点，Bing上升约0.776个百分点，YouTube搜索上升约0.545个百分点；YouTube视频的四部署合并F1恰好相同，不代表逐部署或逐内容预测相同。',
           '', '## 错误修复与新增错误','',table(counts),'',table(flip_summary),'',
           '每臂有1440次预测暴露，即480访问乘三个遮蔽场景，而不是1440个独立访问。D-P相对P-small仅23次预测改变，修复7次、新增12次错误，净多5次错误；未覆盖U内修复3次、新增4次。F1_U仍小幅提高，是六类precision/recall及部署遮蔽等权汇总的结果，不等于净正确样本数增加。',
           '', '相对S，D-P在U内修复20次、新增2次，具有清楚的目标未覆盖决策用途；在C内修复8次、新增14次，显示已覆盖与未覆盖业务之间的取舍。',
           '', '## 内层可靠与外层未充分优化','',table(selected_meta),'',
           'Q是用于学习q的源内未覆盖CE，表中的平均来自60角色；total包括原收缩和关系惩罚。D-P的Q由1.099585增至1.120134，42/60角色变差；总目标由1.099585增至1.197321，57/60变差。D-G的总目标有56/60变差。T-P的Q平均下降，但也有22/60角色变差。',
           '', 'D-P终态总梯度无穷范数的角色中位数约11.117，D-G约11.239，不能称为q的驻点。所有q均没有触及0或2边界。因此，终态不能以“被投影卡在边界”解释。这不是原计划数值资格失败：计划只要求可靠内层解与导数，没有要求20步外层必然下降或收敛。',
           '',table(curve),'',
           'D-P第一步平均软惩罚约16.241，总目标约17.363，之后在大幅回落与再次升高之间振荡。固定使用q20忠实执行了预登记，不应在看到H后改选某个更低源内目标的旧checkpoint。',
           '', '## 惩罚集中与系数几何','',table(dp_pen),'',table(geom),'',
           'D-P的P_up/E_up两块合计占首步软惩罚99.997%，终态占94.786%；D-G也呈现同类集中。D-P首步两块惩罚梯度绝对值的角色中位数约464.5与455.6，远大于其他块。',
           '', '120组P/G系数的1200项方差下限没有一次触发。P_up的A/s中位数约4264.4，E_up约4216.6，其余块大多在1至15附近。因此，现象不能归因为方差下限截断。',
           '', '用delta=q减1重写既有关系增量，可得g为2乘(A减B)/s乘delta加A/s乘delta平方。这一代数式说明：即使起点的一阶增量很小，极大的A/s仍可使固定0.05幅度移动产生较大恢复误差与软惩罚。保存轨迹和系数支持“外层优化面对很不均衡的尺度并产生振荡”的解释；它不是下游分类失败的唯一原因证明，也不保证更小步长或其他优化器一定带来业务增益。',
           '', '## q变化与摘要格式','',table(qsummary),'',table(fmt),'',
           'D-P终态q范围约0.147至1.752，T-P约0.024至1.967。D-P的P_up与E_up均值仍接近1，跨角色标准差约0.012；相比之下其他块及T-P可变化更大。约束确实影响了幅度轨迹，但不能把q解释成不变概率或互信息。',
           '', '格式表的negative采用严格小于0口径，单位是块乘辅助视图暴露，不是独立访问或非法TCP流数，也未扣除微小舍入负值。仿射/幅度外推存在负分箱，而块和仍保持1到浮点精度。本方法不声称生成合法概率直方图或真实TCP会话；这项边界原计划已保留，不能把它单独认定为分类表现的原因。',
           '', '## 结论和后续判断','',
           '本轮建立了完整、可审计的解级反馈正式业务流程，并保留D-P相对S的正向用途；没有建立超越原P-small、仅任务调整或匿名组关系的预定增量。概率指标与不同部署的变化也不支持将D-P称为全面更强模型。',
           '', '当前还应保留一项明确的优化限制：旧有限步数LR反馈问题已被可靠解级反馈替代，但外层固定20步q程序在多数关系约束角色中没有降低其自身目标。因此，科学结论限于这一已登记有限程序，不能用来否定优化充分后的动态关系目标或所有真实配对用途。',
           '', '建议冻结本轮正式分数，不立即按H调整rho、nu、类别、步数或挑checkpoint。如决定继续，下一项有限检查应针对仅源内的q目标尺度与优化质量，独立登记下降/驻点或有限近似要求；不是再重复已经通过的LR后端检查，也不是直接启动更大的分类器。优化质量解决后是否改善H，仍是另一项需要独立对照的业务问题。',
           '', '本轮使用同一批已反复分析的数据和部分目标C校准。区间条件于固定模型，不包含重训练或外部批次不确定性；没有验证未见配置、跨日期、DIRECT到代理、单flow任务、AnyTLS/Hy2共享载体或无索引在线识别。',
           '', '## 复现和结果入口','',
           f'- [正式完成状态]({(RUN/"completion.json").as_posix()})',f'- [预登记主比较]({(RUN/"comparisons/primary.json").as_posix()})',
           f'- [本次独立分析核验]({(OUT/"audit.json").as_posix()})',f'- [分析代码]({Path(__file__).as_posix()})',
           f'- [自动执行报告]({(DOC.parent/"execution-report-20261012.md").as_posix()})','',
           '复现命令：`D:/Tools/Anaconda/envs/Pytorch312/python.exe eval/dynamic_soft_drift_formal_analysis/analyze.py`。独立分析目录已存在完成标记时拒绝覆盖，不触发训练、评分重选或旧版本恢复。','']
    DOC.parent.mkdir(parents=True,exist_ok=True);DOC.write_text('\n'.join(lines),encoding='utf-8')
    write(OUT/'input-sha256.json',READS)
    write(OUT/'completion.json',dict(passed=True,report=relative(DOC),report_sha256=sha(DOC),new_fits=0,formal_results_unchanged=True,
          analysis_code_sha256=sha(Path(__file__)),outputs={relative(p):sha(p) for p in OUT.rglob('*') if p.is_file()}))
    print(json.dumps(dict(report=relative(DOC),elapsed_hours=elapsed/3600,primary_passed=int(primary.passed.sum()),replay_error=error),ensure_ascii=False),flush=True)

if __name__=='__main__':main()
