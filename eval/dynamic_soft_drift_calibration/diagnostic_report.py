"""Additive diagnosis of saved FD checks; cannot authorize or resume training."""
from common import *
import unroll as U

def run():
    with stage('failure_diagnosis'):
        result=read(OUT/'pilot/hypergradient-completion.json')
        require(not result['passed'],'This report is only for the preserved rejected pilot')
        original_hash=sha(OUT/'pilot/hypergradient-checks.parquet')
        d=pd.read_parquet(OUT/'pilot/hypergradient-checks.parquet');rows=[];decomposition=[];finite=[]
        roles=contract()['pilot_roles'];byid={r['id']:r for r in roles};cache={}
        # Independent scalar formula, without importing the recovery penalty function.
        for arm in ARMS:
            for r in roles:
                task=pilot_task(r,arm)
                cache[(arm,r['id'])]={k:task['coeff'][k].detach().cpu().numpy() for k in ['A','B','s']}
        for row in d.to_dict('records'):
            arm=row['arm'];j=row['coordinate'];q=1. if row['point']=='one' else (.9 if j%2==0 else 1.1)
            c=cache[(arm,row['role_id'])];a=float(c['A'][j]);b=float(c['B'][j]);s=float(c['s'][j]);h=row['step']
            def g(v):return (v-1)*(a*(v+1)-2*b)/s
            def p(v):return max(g(v),0.)**2/20 if arm!='T-P' else 0.
            gp=(2*a*q-2*b)/s
            derivative=max(g(q),0.)*gp/10 if arm!='T-P' else 0.
            fdpen=(p(q+h)-p(q-h))/(2*h)
            bias=fdpen-derivative
            corrected=row['finite_difference']-bias
            smoothauto=row['automatic']-derivative
            smoothfd=row['finite_difference']-fdpen
            error=abs(smoothauto-smoothfd);limit=1e-5+1e-3*abs(smoothfd)
            rows.append(dict(**row,analytic_penalty_gradient=derivative,penalty_central_difference=fdpen,
                     penalty_FD_bias=bias,corrected_total_FD=corrected,
                     smooth_auto=smoothauto,smooth_FD=smoothfd,smooth_error=error,
                     diagnostic_limit=limit,diagnostic_passed=error<=limit,
                     original_gate_rewritten=False))
        table=pd.DataFrame(rows);save(table,OUT/'pilot/diagnostics/FD-penalty-decomposition.parquet')
        # D-P and T-P have identical unroll, step, data and rho. Only soft penalty differs.
        for point in ['one','interior']:
            p=OUT/'pilot/gradients'/f'D-P-{point}.pt';q=OUT/'pilot/gradients'/f'T-P-{point}.pt'
            pp=torch.load(p,map_location=device(),weights_only=True);tt=torch.load(q,map_location=device(),weights_only=True)
            require(sha(p)==read(p.with_suffix('.json'))['sha256'] and sha(q)==read(q.with_suffix('.json'))['sha256'],'Saved gradients changed')
            analytic=[]
            for i,r in enumerate(roles):
                c=cache[('D-P',r['id'])];z=pp['q'][i].cpu().numpy()
                g=(z-1)*(c['A']*(z+1)-2*c['B'])/c['s']
                analytic.append(np.maximum(g,0)*(2*c['A']*z-2*c['B'])/c['s']/10)
            diff=float((pp['gradient']-tt['gradient']-tensor(np.stack(analytic))).abs().max())
            riske=float((pp['risk']-tt['risk']).abs().max())
            decomposition.append(dict(point=point,penalty_gradient_replay_error=diff,task_risk_replay_error=riske,
                                      passed=diff<1e-10 and riske<1e-10))
        for arm in ['D-P','D-G']:
            path=OUT/'pilot/gradients'/f'{arm}-one.pt'
            q= torch.load(path,map_location=device(),weights_only=True)
            for i,r in enumerate(roles):
                v=pilot_task(r,arm)['view'];slot=U.pack(v,arm,tensor(np.ones(10)));theta=q['theta'][i]
                obj=float(U.original_objective(theta,slot,r['t']));grad=float(U.original_gradient(theta,slot,r['t']).abs().max())
                finite.append(dict(role_id=r['id'],arm=arm,source_training_objective=obj,
                       zero_initial_objective=float(np.log(6)),training_improvement=float(np.log(6))-obj,
                       original_gradient_max=grad,meta_CE=float(q['risk'][i]),
                       inner_step=float(v['conditioning']['step']),converged_reference_available=False))
        save(pd.DataFrame(finite),OUT/'pilot/diagnostics/finite-step-quality.parquet')
        save(pd.DataFrame(decomposition),OUT/'pilot/diagnostics/penalty-gradient-replay.parquet')
        require(sha(OUT/'pilot/hypergradient-checks.parquet')==original_hash,'Original FD table changed')
        diag=dict(passed=bool(table.diagnostic_passed.all() and all(x['passed'] for x in decomposition)),
                  original_gate_passed=False,original_failed=int((~d.passed).sum()),
                  original_failures_all_at_activation_boundary=bool(d.loc[~d.passed,'point'].eq('one').all()),
                  smooth_checks=len(table),smooth_failed=int((~table.diagnostic_passed).sum()),
                  smooth_max_absolute_error=float(table.smooth_error.max()),
                  penalty_gradient_replay=decomposition,original_checks_sha256=original_hash,
                  new_inner_updates=0,new_mapping_fits=0,new_classifier_fits=0,
                  diagnostic_does_not_authorize_continuation=True)
        write(OUT/'pilot/diagnostics/diagnostic-completion.json',diag)
        timing=pd.read_parquet(OUT/'pilot/hypergradient-timings.parquet')
        warm=timing.iloc[1:].seconds
        budget=dict(formal_meta_updates=3600,batch_tasks=12,median_warm_seconds=float(warm.median()),
                    rough_formal_meta_seconds=float(warm.median()*3600),
                    steady_observed_range_seconds=[float(warm.min()*3600),float(warm.max()*3600)],
                    peak_observed_MiB=float(timing.peak_MiB.max()),
                    representativeness='mixed source pilot tasks, not all formal episode batches',
                    includes_final_180_LR=False,includes_io_or_report=False,
                    final_LR_total_seconds_estimate=None,source_converged_reference_fits=0,
                    estimate_not_completion_promise=True)
        write(OUT/'pilot/runtime-budget.json',budget)
        summary=d.groupby(['arm','point']).agg(checks=('passed','size'),
                     failed=('passed',lambda x:int((~x).sum())),max_error=('absolute_error','max')).reset_index()
        text=f'''# 动态软约束漂移源内先导报告

2026年10月12日。新代码和源内CUDA先导已执行，但原超梯度验收未通过。当前状态为`stop_numeric_FD_activation_boundary`，没有进入正式元训练、实际目标C系数学习或业务分类。

## 已完成的范围

Pytorch312使用PyTorch {contract()['environment']['torch']}、CUDA {contract()['environment']['cuda']}和{contract()['environment']['gpu']}，全程数值计算为CUDA float64。

已登记60个外层角色、720个源内任务，核对1440个源内映射引用，无缺失。480份实际C预测完成文件哈希与元数据清点，没有加载其数值张量；正式阶段仍需核对坐标与权重。12个源内先导任务构造了独立P/G输入，44项数学与权限单元检查通过。原锚点停止、旧输入文件、旧失败记录均保留。

本轮运行了2952条单任务64步轨迹，共188928次内层更新暴露；以12任务GPU向量化执行。没有新闭式映射拟合，没有新收敛LR拟合，也没有业务F1结果。

## 原超梯度验收

{summary.to_markdown(index=False, floatfmt='.9g')}

1440项检查有{int((~d.passed).sum())}项失败，全部位于D-P或D-G的q=1点。T-P两个点全部通过，D-P和D-G的交替0.9／1.1内点全部通过。相对误差门可能在较大梯度处允许较大的绝对差，因此不能只报通过比例而省略误差。

原门限保持`1e-5 + 1e-3 * abs(FD)`，两个差分步长保持1e-3与3e-4。原失败表、完成文件和异常记录未被覆盖；附加诊断不将原门改判为通过。

## 激活边界的解析定位

单块软惩罚为phi(q)=[g(q)]_+平方除以20。q=1时g=0，phi的导数为0，但两个扰动点可能分处激活与非激活分支。记k=g'(1)，中心差分包含约k乘abs(k)乘h除以40的一阶截断项，而不是普通光滑点的二阶截断项。除以较小的共享方差后，这项可以超过登记的绝对阈值。

附加诊断使用相同已保存有限差分，减去解析惩罚自身的中心差分截断项，再检查剩余的Q加rho正则梯度。没有重新展开或拟合。{len(table)}项分解检查通过标志为{diag['passed']}，剩余误差最大为{diag['smooth_max_absolute_error']:.12g}。

另外，D-P与T-P的相同任务风险及梯度差被独立重放：两者任务项一致，梯度差等于解析软惩罚梯度。详见penalty-gradient-replay表。这支持当前失败来自激活边界的检查近似，而非当前已发现的训练图断裂；它不能证明全部未来程序正确，也不等于原验收通过。

## 有限展开的质量

24个已保存q=1的64步模型，源训练目标范围为{min(x['source_training_objective'] for x in finite):.9g}至{max(x['source_training_objective'] for x in finite):.9g}；零初始化目标为log(6)={np.log(6):.9g}。其目标改善范围为{min(x['training_improvement'] for x in finite):.9g}至{max(x['training_improvement'] for x in finite):.9g}。原坐标最大梯度范围为{min(x['original_gradient_max'] for x in finite):.9g}至{max(x['original_gradient_max'] for x in finite):.9g}。

登记的全范围曲率上界给出的步长范围为{min(x['inner_step'] for x in finite):.9g}至{max(x['inner_step'] for x in finite):.9g}。64步结果不应被称为收敛模型。原验收失败后，没有启动后续24个收敛LR参照，故还不能给出与收敛解的实测差距，也不能完成全部DS12。

## 成本测量

12任务64步完整超梯度的稳态中位耗时为{budget['median_warm_seconds']:.6f}秒，观察峰值显存为{budget['peak_observed_MiB']:.3f}MiB。按3600次正式系数更新粗算，元梯度计算部分约{budget['rough_formal_meta_seconds']/60:.2f}分钟，不包含180个最终LR、缓存、序列化和汇报。这是混合源内先导的估算，不是完整矩阵完成时间承诺。

最后LR尚未测量，不能把上述分钟数当成整轮预计耗时。

## 当前暂停节点和建议

DS01至DS10及固定源内梯度试验已执行；DS11原验收失败，24个收敛参照及后续正式矩阵未执行。正式学习系数、实际目标查询和评分均未授权。

建议先独立登记一项梯度检查修订，而不是改科学方法：对Q加rho正则沿用同样的两个中心差分步长与误差限；对解析软惩罚使用独立解析导数及自动微分重放，并在激活边界明确报告原总目标中心差分的截断项。非切换内点仍保留总目标直接有限差分。保留本轮原失败，不扩大损失权重、q范围、K、辅助比例或门限。

这项检查修订需要确认后再执行，不能由本附加诊断自行放行。修订通过后，先完成24个原数值政策的源内收敛参照与完整成本报告，再决定是否启动正式矩阵。

## 文件与权限

代码目录为eval/dynamic_soft_drift_calibration，运行目录为outputs/dynamic-soft-drift-calibration-20261012/run-01。主要产物包括合同与哈希清单、role-membership、reuse-audit、q-one-replay、conditioning-audit、unit-tests、hypergradient-checks、FD-penalty-decomposition、finite-step-quality及runtime-budget。

实际目标C、U、H数值读取为零，测试pre及PCAP读取为零，正式模型数为零。源内伪目标的留出post和标签用于预先登记的元训练数值检查，不是实际目标测试数据。
'''
        textfile(DOC/'pilot-report-20261012.md',text)
        # Recheck every sealed input and ledger. A passed diagnostic is not pilot promotion.
        c=contract()
        for p,h in {**c['fixed_files'],**c['artifacts'],**c['source_sha256']}.items(): require(sha(ROOT/p)==h,'Historical or registered source changed')
        writes=[v for p in (OUT/'stages').glob('*.json') for v in read(p)['reads']]+ACCESS
        data=[v for v in writes if v['purpose'] in ['train','meta-query','meta-labels','paired-recovery','group-recovery']]
        allowed=set(sum(c['pilot_packages_by_role'].values(),[]))
        require(all(v['path'] in allowed for v in data),'Non-source pilot data read')
        require(all(not (v['arm']=='D-G' and ('paired.parquet' in v['path'] or '/JA1-' in v['path'])) for v in writes),'Group exact relation read')
        files={rel(p):sha(p) for p in list(OUT.rglob('*'))+list(DOC.rglob('*')) if p.is_file() and p.name not in ['progress.json','verification.json','completion.json','stage.lock']}
        verification=dict(passed=True,diagnostic_integrity_passed=True,pilot_numeric_acceptance_passed=False,
                    scientific_effect_evaluated=False,original_failure_preserved=True,historical_inputs_unchanged=True,
                    target_C_U_H_numeric_reads=0,PCAP_reads=0,test_pre_reads=0,formal_meta_started=False,
                    new_mapping_fits=0,new_classifier_fits=0,postprocessing_source_sha256=sha(Path(__file__)),files=files)
        write(OUT/'verification.json',verification)
        completion=dict(passed=False,pilot_execution_finished=True,pilot_numeric_acceptance_passed=False,
                    full_first_stage_complete=False,status='stop_numeric_FD_activation_boundary',
                    diagnostic_integrity_passed=True,formal_matrix_started=False,formal_matrix_authorized=False,
                    new_mapping_fits=0,new_classifier_fits=0,verification_sha256=sha(OUT/'verification.json'))
        write(OUT/'completion.json',completion)
        write(OUT/'awaiting-decision.json',dict(status=completion['status'],
              needs_confirmation='Register activation-aware gradient check, preserve original failure, then complete 24 source LR references',
              formal_matrix_authorized=False,scientific_hyperparameters_changed=False))
        progress('pilot_stopped_report_ready',status=completion['status'],original_failed=int((~d.passed).sum()),decomposition_passed=diag['passed'])

if __name__=='__main__':run()
