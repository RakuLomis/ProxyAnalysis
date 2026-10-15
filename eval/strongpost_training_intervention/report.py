"""Read-only pilot closeout. Never promotes a failed numerical pilot."""
from common import *
import objectives as O
import influence as I

def markdown(d):
    cols=list(d)
    def value(v):
        if isinstance(v,(float,np.floating)):return f'{v:.6g}'
        return str(v).replace('|','\\|')
    return '\n'.join(['| '+' | '.join(cols)+' |','| '+' | '.join(['---']*len(cols))+' |']+
                     ['| '+' | '.join(value(x) for x in row)+' |' for row in d.itertuples(index=False,name=None)])

def run():
    with stage('pilot_report'):
        c=contract();p=read(OUT/'pilot/promotion.json')
        table=pd.read_parquet(OUT/'pilot/finite-difference-checks.parquet')
        hs=pd.read_parquet(OUT/'pilot/hessian-checks.parquet');checks=[];changes=[]
        # Independent numerical replay of all accepted pilot objectives/gradients,
        # in original coordinates rather than their fitted preconditioned space.
        for r in c['pilot_roles']:
            v=artifact(viewpath(r));d=artifact(OUT/'pilot/directions'/r['id']/'direction.pt')
            ref=artifact(basemodel(r));q=d['q']
            for tag,a,beta in [('S','P',0.)]+[(f'{a}-eps{e:g}',a,e) for a in ['P','G'] for e in c['epsilons']]:
                path=OUT/'pilot/models'/r['id']/(tag+'.pt');m=artifact(path)
                s=O.slot(v,a,beta);log=read(path.with_suffix('.json'))['optimizer']
                loss=float(O.loss(m,s,r['t']));gw,gb=O.gradient(m,s,r['t'])
                maximum=max(float(gw.abs().max()),float(gb.abs().max()))
                require(abs(loss-log['objective'])<1e-10 and abs(maximum-log['max_gradient'])<1e-10,'Pilot original replay')
                require(maximum<=1e-5,'Pilot classifier precision')
                if beta==0:
                    require(max(float((m[k]-ref[k]).abs().max()) for k in ['weight','bias'])==0.,'Baseline reproduction')
                else:
                    actual=I.encode(O.normalized_model(m),q)-d['base']
                    linear=beta*d['d_'+a]
                    changes.append({'role_id':r['id'],'arm':a,'epsilon':beta,
                        'linear_parameter_change_norm':float(linear.norm()),
                        'actual_parameter_change_norm':float(actual.norm()),
                        'relative_linear_change_error':float((actual-linear).norm())/max(1e-12,float(linear.norm()))})
                checks.append({'role_id':r['id'],'arm':tag,'gradient_inf':maximum,
                    'objective_replay_error':abs(loss-log['objective']),'gradient_replay_error':abs(maximum-log['max_gradient'])})
        audit=pd.DataFrame(checks);save(audit,OUT/'pilot/independent-model-audit.parquet')
        save(pd.DataFrame(changes),OUT/'pilot/finite-parameter-changes.parquet')
        require(len(audit)==60,'Audit coverage')
        state='数值先导通过' if p['passed'] else '数值先导未通过 正式矩阵暂停'
        summary=table.groupby('arm').agg(direction_norm_median=('direction_norm','median'),
            parameter_error_median=('parameter_relative_error','median'),
            parameter_error_max=('parameter_relative_error','max'),
            heldout_CE_error_median=('CE_derivative_error','median'),passed=('passed','sum')).reset_index()
        elapsed=sum(read(f)['seconds'] for f in (OUT/'stages').glob('*.json'))
        body=f'''# StrongPost训练干预数值先导报告

2026年10月9日。{state}。完成输入登记、权限与数学测试、72角色辅助视图、11个补映射和60个CUDA float64数值诊断拟合；尚未启动60角色的正式业务干预矩阵，也没有新目标H上的分类增益结论。

## 当前判断

本轮不是求解器未收敛，也不是解析Hessian实现与自动微分不符。60个诊断分类器全部满足原v4求解门；12次零比例重放参数误差均为0。24个真配或组级方向中，驻点偏移门全部通过，但参数有限差分有{p['gate_failures']['gate_parameter_direction']}项失败、源内留出CE导数有{p['gate_failures']['gate_heldout_CE_derivative']}项失败、源训练CE导数有{p['gate_failures']['gate_source_CE_derivative']}项失败，没有任何方向同时通过全部近似门。

这直接说明：在原合同的epsilon为0.01与0.02下，局部线性方向还不能以预定精度解释有限重训变化。不能将这一结果写成配对关系无效，也不能据此宣称真配或组级业务收益失败；正式真实目标post评价尚未执行。

## 实验配置

冻结extend四TCP部署、六业务、480访问和五折内容划分。60外层角色用于正式设计，先导仅使用折0对应的12个源内角色，实际目标部署未参加先导拟合或评分。内层折1、校准部署规范排序最前者均在拟合前固定。

共同eta使用原JA2源内选择，t使用原StrongPost选择。真实源post、目标C-post、原CORAL与新P/G视图按原标签和质量参与损失。epsilon仅替换辅助槽质量，不平均特征向量。原CE、weight L2、bias不正则、共同mu和scale全部保留。独立排序的源pre/post未按行号配对。

分类器原582参数仅约去共同bias规范，Hessian系统为581维；保留全部576个weight参数。没有jitter、Hessian逆显式构造、新bias惩罚、warm start或CPU回退。

环境为{c['environment']['torch']}，CUDA {c['environment']['cuda']}，{c['environment']['gpu']}，Pytorch312，所有数值计算float64。

## 数学与求解核验

| 检查 | 本轮结果 |
| --- | --- |
| 解析Hessian对自动微分最大归一误差 | {hs.hessian_autograd_residual.max():.6g} |
| Hessian线性系统最大归一残差 | {hs.linear_system_residual.max():.6g} |
| 解析梯度对自动微分最大归一误差 | {hs.gradient_autograd_residual.max():.6g} |
| 60个独立模型目标最大重放误差 | {audit.objective_replay_error.max():.6g} |
| 60个独立模型梯度最大重放误差 | {audit.gradient_replay_error.max():.6g} |
| 60个模型原坐标梯度最大值 | {audit.gradient_inf.max():.6g} |
| 12个基座Hessian最小特征值的最小值 | {hs.eigen_min.min():.6g} |
| Hessian条件数中位数与最大值 | {hs.condition_number.median():.6g} / {hs.condition_number.max():.6g} |
| 驻点偏移比率最大值 预定门0.1 | {table.stationarity_ratio.max():.6g} |
| 参数导数相对误差中位数与最大值 预定门0.1 | {table.parameter_relative_error.median():.6g} / {table.parameter_relative_error.max():.6g} |

## 有限干预不等于无穷小变化

每单位beta的参数方向二范数范围为{table.direction_norm.min():.6g}至{table.direction_norm.max():.6g}，中位数{table.direction_norm.median():.6g}。因此即使epsilon为0.01，线性预测的参数改变量仍约为{.01*table.direction_norm.min():.6g}至{.01*table.direction_norm.max():.6g}，不是所有角色都处在可以忽略曲率变化的极小扰动区。

这与有限步长近似偏差的解释相容，但没有通过更小epsilon或更高精度的拟合验证其唯一原因。当前原基座非零梯度并未触发预定驻点偏移门；不能将失败全部归为基座未收敛。也没有证据把它解释为配对训练对真实目标业务必然不利。

下面的汇总只描述先导误差，不是新的外层F1结果：

{markdown(summary)}

## 权限和产物状态

目标H标签读取为0，目标U训练数据读取为0，测试pre读取为0。源内留出标签只在全部60个诊断模型及1440行先导预测封存后读取，用于数值误差核对，未按CE符号选择角色、epsilon、eta或t。

正式模型数为0，正式H预测数为0，新增F1主检验数为0。原CT、JA、追加结项与精确分解源文件均保持冻结；旧JA failure仍保留。11个补映射仅位于本轮新目录。

单个诊断拟合耗时中位数{p['fit_seconds']['median']:.3f}秒，90分位{p['fit_seconds']['p90']:.3f}秒，最大{p['fit_seconds']['max']:.3f}秒；先导拟合合计约{sum(read(f)['seconds'] for f in (OUT/'diagnostic-fit-logs').rglob('*.json')):.3f}秒。已完成阶段壁钟合计约{elapsed:.1f}秒，不含本报告构建。这是运行日志，不是GPU内核耗时。

## 需要确认的继续路径

推荐在不修改科学对照的前提下，保留固定small和full正式重训，停止把影响函数数值当作已验收的精确风险导数。原五臂、240终点上限、共同eta、冻结t、CUDA float64和四项F1比较保持不变；局部分析可以作为明确标注的近似参考，也可以从正式解释中撤下。

若必须先获得高精度局部导数，则应另行登记统一精度或更小差分步长的有限数值方案。它是新数值修订，不能在本轮自动搜索epsilon或放宽已有门，更不能从失败终态续跑直到通过。

当前已按批准计划暂停，等待用户决定。没有生成整个实验完成标志，也没有启动可选C-half支线。

## 文件索引

- 代码：`eval/strongpost_training_intervention/`。
- 合同与读账：`outputs/strongpost-training-intervention-20261009/run-01/manifests/`和`stages/`。
- 近似推进门：`pilot/promotion.json`。
- 全24项导数检查：`pilot/finite-difference-checks.parquet`。
- Hessian检查：`pilot/hessian-checks.parquet`。
- 60模型独立原坐标验收：`pilot/independent-model-audit.parquet`。
- 有限参数变化：`pilot/finite-parameter-changes.parquet`。
- 先导完整预测：`pilot/predictions.parquet`及`predictions-complete.json`。
- 暂停请求：运行根目录`awaiting-decision.json`。

详见[数值先导逐项附录](numeric-pilot-appendix-20261009.md)。
'''
        textfile(DOC/'numeric-pilot-report-20261009.md',body)
        columns=['target','calibration','group','arm','eta','t','direction_norm','stationarity_ratio',
                 'parameter_relative_error','CE_derivative_predicted','CE_derivative_finite','CE_derivative_error',
                 'source_CE_error','gate_parameter_direction','gate_heldout_CE_derivative','gate_source_CE_derivative','passed']
        textfile(DOC/'numeric-pilot-appendix-20261009.md','# StrongPost数值先导逐项附录\n\n'
                 +'全部角色和两个映射均保留。下表CE来自源内伪目标，不是正式目标H；检查通过不表示业务增益成立。\n\n'
                 +markdown(table[columns])+'\n\n## Hessian逐角色核验\n\n'+markdown(hs)+'\n')
        # Rehash accepted artifacts and confirm partial completion, not main experiment completion.
        files=list((OUT/'pilot').rglob('*'))+list((OUT/'mappings').rglob('*'))+list(DOC.glob('*.md'))
        hashes={rel(f):sha(f) for f in files if f.is_file()}
        histories=[a for f in (OUT/'stages').glob('*.json') for a in read(f).get('reads',[])]
        forbidden=[a for a in histories if a['purpose']=='score' or 'heldout-visits' in a['path']]
        require(not forbidden,'Forbidden pilot read')
        require(not (OUT/'models').exists() and not (OUT/'predictions/complete.json').exists(),'Formal stage unexpectedly started')
        write(OUT/'pilot/verification.json',{'passed':True,'scientific_promotion_passed':p['passed'],
            'new_diagnostic_classifiers':60,'new_mapping_fits':11,'new_formal_classifiers':0,
            'target_H_label_reads':0,'test_pre_reads':0,'target_U_training_reads':0,
            'original_models_independently_replayed':60,'files':hashes,'report_builder_sha256':sha(Path(__file__))})
        write(OUT/'pilot/completion.json',{'pilot_execution_complete':True,'numerical_promotion_passed':p['passed'],
            'formal_experiment_complete':False,'verification_sha256':sha(OUT/'pilot/verification.json'),
            'time_unix':time.time(),'awaiting_user_decision':not p['passed']})

if __name__=='__main__':run()
