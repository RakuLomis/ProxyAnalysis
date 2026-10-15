"""Report fixed source evidence; no training or automatic scientific promotion."""
from common import *

def run():
    with stage('report'):
        parent_integrity();gate=read(OUT/'gradient-repair-verification.json')
        checks=pd.read_parquet(OUT/'checks/gradient-checks.parquet')
        require(gate['passed'] and read(OUT/'references-complete.json')['passed'],'Both repair stages must pass')
        d=pd.read_parquet(OUT/'reference-comparisons.parquet');p=pd.read_parquet(OUT/'source-predictions.parquet')
        require(len(d)==24 and len(p)==192 and d.accepted.all(),'Complete accepted source cohort')
        for row in d.to_dict('records'):
            model=OUT/'models'/row['role_id']/f'{row["arm"]}.pt';meta=read(model.with_suffix('.json'));log=meta['optimizer']
            require(sha(model)==meta['sha256'] and all(acceptance_gates(log['objective'],log['initial_objective'],log['max_gradient'],
                        log['iterations'],log['objective_replay_error'],log['gradient_replay_error']).values()),'Final model acceptance')
        summary=d.groupby('arm').agg(models=('role_id','size'),remaining_min=('remaining_ratio','min'),
            remaining_median=('remaining_ratio','median'),remaining_max=('remaining_ratio','max'),
            CE64=('CE64','mean'),CE_ref=('CE_ref','mean'),TV=('mean_probability_TV','mean'),
            logit_RMSE=('relative_logit_RMSE','mean'),changed=('changed','sum'),fixed=('fixed','sum'),broken=('broken','sum'),
            solver_seconds=('solver_seconds','sum')).reset_index()
        save(summary,OUT/'summary-by-arm.parquet')
        for name,df in [('reference-comparisons',d),('source-predictions',p),('gradient-checks',checks),('summary-by-arm',summary)]:
            csv=writable(DOC/f'{name}.csv');csv.parent.mkdir(parents=True,exist_ok=True);df.to_csv(csv,index=False,encoding='utf-8-sig')
        report=f'''# 动态软约束漂移梯度修复与源内收敛参照报告

2026年10月12日。本轮独立梯度检查修订通过，24个源内LR参照完成并通过原数值验收。只完成数值检查和内层质量比较；没有学习正式q，没有读取实际目标C/U/H数值，没有运行180个正式分类器。按计划在两阶段后暂停。

## 数据与冻结条件

保留原12个源内任务，每任务两个源部署144次训练访问，伪目标C为48次访问，源内未覆盖反馈为8次留出post。P/G成员、映射、eta、尺度、t、六类标签、权重不变。训练槽位共480行，90% CORAL加10%调整视图，总调整质量为1/30。q范围、rho、nu、64步轨迹与初始化均未改变。

使用{contract()['environment']['python']}，PyTorch {contract()['environment']['torch']}，CUDA {contract()['environment']['cuda']}，{contract()['environment']['gpu']}。模型训练与推理均为CUDA float64，未使用CPU回退。

## 梯度检查修订

新验收直接对Q64加rho正则做两种中心差分，步长1e-3与3e-4，门限仍为1e-5加1e-3乘差分绝对值。软惩罚的参考来自原始fixture的独立残差与匿名组合重算，不调用生产gap或soft当标准答案。解析导数、生产自动微分和分项和独立核对；分支检查覆盖整个扰动区间，不仅检查端点同号。

1440个检查位置均保留，修订后失败{gate['revised_failed']}项；平滑项最大绝对误差{gate['max_smooth_error']:.12g}，惩罚解析导数最大误差{gate['max_penalty_error']:.12g}。新重放中，旧完整目标直接差分仍有{gate['original_direct_failed']}项失败，未将它们删除或改写。

分支区间分类：

{checks.groupby(['arm','branch']).size().rename('checks').reset_index().to_markdown(index=False)}

无切换区间保留完整目标直接差分；切换区间由直接平滑项检查与独立惩罚解析导数联合验收。原运行168项失败及`stop_numeric_FD_activation_boundary`保持原样，新通过只属于独立修复版本。原64步参数和总梯度均进行了封存值重放。

修复执行了{gate['trajectories']}条单任务64步前向轨迹、{gate['inner_updates']}次内层更新暴露。平滑项和完整项各反向一次，共{gate['unroll_backward_exposures']}次单任务64步反向暴露，另有{gate['penalty_backward_exposures']}次仅惩罚反向。这些次数不代表独立访问。

## 24个源内参照

12任务乘P/G各拟合一个q=1分类器。T-P与D-P的训练问题相同，未重复拟合。原v4求解器统一max_iter=2000、max_eval=10000，零初始化，原W正则，bias不正则。所有模型通过原坐标梯度不超过1e-5及目标与梯度重放误差小于1e-10的验收。

下表先按臂描述汇总；192行预测是24个模型各8次反馈访问的角色暴露，存在重复，不是192个独立内容或访问。仅源内描述，不构造业务显著性结论。

{summary.to_markdown(index=False,floatfmt='.9g')}

remaining比例定义为(J64-J_ref)/(J0-J_ref)，分母大于1e-6时才计算，没有截断到0至1。J_ref只是原数值政策下的已验收解，不称为精确数学最优。

## 逐模型优化和预测差距

{d[['role_id','arm','J64','J_ref','remaining_ratio','gradient64','gradient_ref','CE64','CE_ref','changed','fixed','broken','solver_seconds']].to_markdown(index=False,floatfmt='.9g')}

概率总变差按每访问六类概率的绝对差之和除以2计算。相对logits先减每行六类均值，排除共同偏置平移；RMSE和最大差与类别变化共同保存在reference-comparisons表。逐访问六类概率、相对logits及标签保存在source-predictions表，评价口径仍为原8行未覆盖反馈。

## 计算成本

24个收敛模型实测求解耗时合计{d.solver_seconds.sum():.3f}秒，单模型范围{d.solver_seconds.min():.3f}至{d.solver_seconds.max():.3f}秒。梯度先导与读写、审计、报告耗时见各阶段账本，不混同为求解时间。

原先导约4分钟的估算只针对元梯度部分，不是完整实验时间。本轮完成源内参照成本测量，但q学习后的正式180端点可能具有不同数值条件，不能把源内单模型耗时直接当作完成时间承诺。

## 当前结论与暂停节点

梯度检查与训练图重放通过，说明激活边界检查问题可以不改变损失地处理。64步是否代表充分训练，应根据逐任务剩余差距、CE、概率、相对logits和错误变化分别判断，不能因梯度准确而自动认可短程反馈。

本轮没有新增业务收益结果。q=1处的检查和参照也不能证明整个q范围的变化方向正确。若源内优化与预测差距明显，应先登记有限的内层轨迹修订；若各项接近，仍需另行授权固定非平凡扰动核对。当前不改坐标、不增加K、不重选初始化、不运行额外24个扰动参照或正式分类矩阵。

## 复现和产物

独立代码位于eval/dynamic_soft_drift_calibration_repair，运行位于outputs/dynamic-soft-drift-calibration-repair-20261012/run-01。repair-contract及seal记录角色、原数学代码SHA、源内资产和父产物；checks、models、fit-logs、reference-comparisons、source-predictions、阶段读取账本及verification形成复核链。

报告目录同时导出四张CSV，保留所有逐任务及逐坐标数值。旧运行、旧代码和旧停止判定未修改。
'''
        textfile(DOC/'repair-report-20261012.md',report)
        parent_integrity()
        for k,h in contract()['source_sha256'].items():require(sha(ROOT/k)==h,'Repair code changed')
        reads=ACCESS[:]
        for path in list((OUT/'stages').glob('*.json'))+list((OUT/'failures').glob('*.json')):reads+=read(path).get('reads',[])
        data=[v for v in reads if v['purpose'] in ['source-task','saved-source-unroll']]
        require(all(v['path'] in contract()['source_assets'] for v in data),'Unregistered numeric data')
        require(not any(v.get('arm')=='D-G' and '/D-P' in v['path'] for v in reads),'Group loaded paired data')
        files={rel(p):sha(p) for p in list(OUT.rglob('*'))+list(DOC.rglob('*')) if p.is_file() and p.name not in ['stage.lock','progress.json','verification.json','completion.json','awaiting-decision.json']}
        v=dict(passed=True,checks=gate,accepted_source_classifiers=24,target_C_U_H_numeric_reads=0,
               PCAP_reads=0,test_pre_reads=0,source_only=True,parent_inputs_unchanged=True,parent_failure_preserved=True,
               scientific_objective_changed=False,unroll_trajectory_changed=False,formal_matrix_authorized=False,files=files)
        write(OUT/'verification.json',v)
        write(OUT/'completion.json',dict(passed=True,repair_complete=True,source_reference_complete=True,
              status='awaiting_inner_quality_decision',new_classifier_fits=24,new_mapping_fits=0,
              extra_perturbation_fits=0,formal_matrix_authorized=False,verification_sha256=sha(OUT/'verification.json')))
        write(OUT/'awaiting-decision.json',dict(status='awaiting_inner_quality_decision',
              formal_matrix_authorized=False,inner_trajectory_revision_authorized=False,extra_perturbation_authorized=False))
        progress('repair_report_ready',source_classifiers=24,formal_matrix_started=False)

if __name__=='__main__':run()
