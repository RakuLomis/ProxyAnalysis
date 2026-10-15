"""Complete v2 evidence report, compact summaries plus detailed case tables."""
from common import *

def frame(p):return pd.read_parquet(p) if p.exists() else pd.DataFrame()
def table(d):return d.to_markdown(index=False,floatfmt='.9g').replace('nan','未执行或不适用')

def run():
    with stage('report'):
        end=read(OUT/'completion.json');c=contract();budget=read(OUT/'ledger.json')
        validations=frame(OUT/'validation-checks.parquet');forwards=frame(OUT/'forward-checks.parquet')
        fd=pd.concat([frame(OUT/f'{p}-FD-checks.parquet') for p in ['one','alt']],ignore_index=True)
        im=pd.concat([frame(OUT/f'{p}-implicit-checks.parquet') for p in ['one','alt']],ignore_index=True)
        centers=pd.concat([frame(OUT/f'{p}-centers.parquet') for p in ['one','alt']],ignore_index=True)
        status=[]
        for p in ['first-three','one','alt']:
            path=OUT/f'{p}-complete.json'
            status.append(dict(stage=p,executed=path.exists(),**(read(path) if path.exists() else dict(passed=False,status='conditional_not_executed'))))
        first=read(OUT/'first-case-verdict.json') if (OUT/'first-case-verdict.json').exists() else None
        first_text=table(pd.DataFrame([first])) if first else '首例新版差分判定尚未完成。'
        if len(validations):
            fields=[x for x in ['role_id','arm','key','gradient_f','gradient_v','risk_change','Newton_backward_error',
                     'independent_step_relative','floating_platform','passed'] if x in validations]
            val_text=table(validations[fields])
        else:val_text='没有完成的有限校验记录。'
        if len(fd):
            summary=fd.groupby(['point','arm']).agg(checks=('passed','size'),passed=('passed','sum'),
                 U_fv_max=('U_fv_with_floor','max'),implicit_f_error_max=('implicit_f_error','max'),
                 implicit_v_error_max=('implicit_v_error','max'),identifiable=('signal_identifiable','sum')).reset_index()
            save(summary,OUT/'FD-summary.parquet');fdtext=table(summary)
            detail=table(fd[[x for x in ['role_id','arm','point','direction','h','D_f','D_v','U_fv_with_floor','U_limit',
                      'implicit_f_error','derivative_limit','passed','failed_gates'] if x in fd]])
        else:fdtext='未完成方向差分。';detail='无完成记录。'
        if len(im):
            ims=im.groupby(['point','arm','state']).agg(checks=('passed','size'),
                H_error_max=('hessian_error','max'),linear_residual_max=('linear_residual','max'),
                condition_max=('condition','max'),mixed_VJP_max=('mixed_VJP_error','max')).reset_index()
            imtext=table(ims)
        else:imtext='隐式导数核对未执行。'
        errors=[]
        for p in (OUT/'failures').glob('*.json') if (OUT/'failures').exists() else []:
            v=read(p);errors.append(dict(stage=v['stage'],type=v['type'],exception=v['exception']))
        error_text=table(pd.DataFrame(errors)) if errors else '无阶段异常；若资格门未过，见阶段状态和差分失败路径。'
        qualified=end['numeric_qualified']
        conclusion=('完整预定源内先导在两个点、两个方向和两个步长上通过第二版数值验收，可据此制定正式业务比较；'
                    '这不是动态系数的分类收益。') if qualified else ('本轮尚未获得完整解级反馈资格，保持停止或未决。'
                    '已通过的局部检查与失败项分别保留，不能据此启动正式分类矩阵。')
        phases=table(pd.DataFrame(status))
        cohort=table(pd.DataFrame([dict(role_id=r['id'],target_excluded=r['target'],group=r['group'],source_calibration=r['calibration'],t=r['t']) for r in c['selected']]))
        text=f'''# 动态软约束漂移解级反馈精度修订完整报告

2026年10月12日。本轮状态为`{end['status']}`。执行完整性为{end['execution_integrity_passed']}，完整数值资格为{qualified}。正式q学习及业务分类矩阵均未启动，没有新业务F1结果。

## 问题与版本区别

本轮保留原充分求解LR加隐式微分。第一版stop_implicit_gradient_not_verified保持不变，旧粗细风险变化指标和失败记录不改写。第二版新增细档f到实际一次Newton校验状态v的稳定性检查，不将v作为新业务模型选优。

原六类、96维十块、P/G基础映射、样本质量、t、mu/scale、内容划分及软惩罚保持不变。目标为带权CE加0.0005(1+t)乘原W平方，bias不正则。485维精确对比数值参数化和q=1训练Cholesky坐标不变。

480行训练槽位、8行源内留出反馈仍沿用旧成员，调整pre占总CE质量1/30。实际目标排除标签不是被读取的目标数据；所有重复、两侧、内部flow整体划分。

{cohort}

## CUDA环境和计算政策

Python {c['environment']['python']}；PyTorch {c['environment']['torch']}；CUDA {c['environment']['cuda']}；GPU {c['environment']['gpu']}。全部训练、推理、Hessian、系统求解和微分CUDA float64，无CPU数值回退。

旧三fine直接复用。其他q点保持原v4 max_iter=2000、max_eval=10000、原梯度1e-5验收；随后保持同目标Newton/Armijo策略，最多30次更新到原梯度1e-9。粗档1e-8仅记录实际独立观察到的状态，不复制fine制造另一层级。

## 一次独立细档校验

每个fine点重算原残差和Hessian，显式公式与AD独立核对；解H delta=−r并与CUDA通用线性求解比较。每点只执行一次完整步长1更新，没有回溯、jitter、第二次校正或源内CE选步长。

校验系统后向误差门1e-12，两解校正相对差门1e-8；f/v原梯度均不超过1e-9。平台标签还要求原梯度不超过1e-12、相对校正不超过1e-10和目标在固定舍入尺度内。平台标签本身不构成资格，风险相等也不能替代独立求解证据。

{val_text}

## 首例旧新指标

旧粗细诊断保留，新指标为(abs(R_f_plus−R_v_plus)加abs(R_f_minus−R_v_minus))/(2h)，另加两端各1e-12底限。带底限值不得超过原导数允许误差的十分之一；允许误差仍为1e-5加1e-3乘细档差分绝对值。

{first_text}

旧首例风险变化门仍不通过；若新首例通过，只说明按修订合同的最终fine稳定性取得资格，不回写旧判定。

## 隐式导数与细档稳定性

g_f与g_v均在相应中心独立核对H、混合偏导与Hv=g。逐维稳定性允许误差保持1e-6加1e-3乘两者最大绝对值。P与T-P共享任务梯度，分别加或不加软惩罚，G使用自己的匿名资产。

{imtext}

{table(centers) if len(centers) else '无完成的中心表。'}

## 固定差分结果

方向仍为全同向与交替两个单位方向，h仍为1e-4和3e-5，q点仍为1和交替0.9／1.1。两步长一致性、f/v差分稳定性和隐式一致性均按冻结门核对。信号不足记未决，不根据微小正负号放行。

{fdtext}

{detail}

软惩罚继续使用独立解析oracle及激活分支核对。跨切换时普通完整中心差分的截断项单列，不误用作唯一验收标准。各臂f/v的完整分项记录保存于arm-FD-checks表。

## 阶段状态及停止路径

{phases}

{error_text}

各点solve_log、fine_state、validation_log、validation_state分别使用明确schema，未把快照侧车缺少accepted字段解释为失败。失败或未决不启动后续依赖阶段，不轮换角色、步长或后端。

## 计算与权限账本

{table(pd.DataFrame([budget]))}

完整上限为202个新LR、11个旧源内参照精炼、216次一次校验和48次中心隐式评估。当前表为实际计算量，f/v快照不是独立访问。已完成的旧计数、72位置几何与惩罚oracle仅来源复核，不重新拟合。

原父产物SHA保持不变，所有数值资产按源内白名单和P/G臂权限加载，G不加载P身份或映射。实际目标C/U/H数值读取0，PCAP读取0，新漂移映射0，正式分类器0。旧P-small正向结果及其身份归因边界未改。

## 结论与适用范围

{conclusion}

本修订是在已分析首例上形成，首例复核不称为独立盲测。即使完整先导通过，也仅覆盖固定六角色、两点和两方向，不证明全部q范围及未来元优化访问点可靠，不是外部验证。正式业务比较仍需独立合同、全矩阵预算和新q点的求解拒绝政策。

## 可复核产物

- [批准方案]({PLAN.as_posix()})
- [冻结合同]({(OUT/'manifests/contract.json').as_posix()})
- [完成状态]({(OUT/'completion.json').as_posix()})
- [独立校验表]({(OUT/'validation-checks.parquet').as_posix()})
- [q为1差分表]({(OUT/'one-FD-checks.parquet').as_posix()})
- [实际计算账本]({(OUT/'ledger.json').as_posix()})
- [完整性验证]({(OUT/'verification.json').as_posix()})
- [运行说明]({(ROOT/'eval/dynamic_soft_drift_implicit_v2/README.md').as_posix()})
'''
        p=DOC/'implicit-fine-validation-v2-report-20261012.md';textfile(p,text)
        write(OUT/'report-seal.json',dict(path=rel(p),sha256=sha(p),completion_sha256=sha(OUT/'completion.json')))
        progress('v2_report_saved',status=end['status'],path=rel(p))

if __name__=='__main__':run()
