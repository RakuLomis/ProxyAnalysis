"""Independent selected-occupancy audit and sustained whole-GPU observation."""
from pathlib import Path
import argparse
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'eval/joint_associated_post_classifier'))
from common import *
from data import TrainingPool,pilot_roles
from train import Engine
from tests import compare
from telemetry import Sampler

def jobs32(pool):
    roles=pilot_roles();jobs=[]
    for i in range(32):
        lam=[0.,.1,1.][i%3]
        jobs.append(dict(role=roles[i%12],arm='JC' if lam==0 else ('JP' if i%2 else 'JG'),
                    recipe=dict(lam=lam,lr=.001,gamma=.001),seed=SOURCE_SEED+i))
    return jobs,[pool.get(j['role'],j['arm'],j['recipe']['lam']) for j in jobs]

def occupancy_audit(jobs,data,root):
    references=[Engine([d],[j],'independent') for d,j in zip(data,jobs)]
    engine=Engine(data,jobs,'streams');engine.capture();records=[]
    for step in [1,10,100]:
        for ref in references:ref.advance(step-ref.steps)
        engine.advance(step-engine.steps)
        for i,ref in enumerate(references):
            ok,rows=compare(ref.checkpoint(),dict(parameters=engine.net.snapshot(i),adam=engine.adam_head(i)))
            require(ok,'Selected 32-model occupancy changed independent prefix')
            records.extend(dict(model=i,prefix=step,**v) for v in rows)
        progress('GPU_selected_occupancy_audit',models=32,prefix=step,passed=True)
    checkpoint=engine.checkpoint();freeze=[]
    for update_G,update_head,keys,frozen_keys in [(False,True,HKEYS,GKEYS),(True,False,GKEYS,HKEYS)]:
        branch=Engine(data,jobs,'streams',states=checkpoint['parameters'],adam=checkpoint['adam'],update_G=update_G,update_head=update_head)
        branch.capture();branch.advance(10)
        for i in range(32):
            state=branch.net.snapshot(i);adam=branch.adam_head(i)
            for k in frozen_keys:
                require(torch.equal(state[k],checkpoint['parameters'][i][k]),'Frozen parameter moved')
                for f in ['step','exp_avg','exp_avg_sq']:require(torch.equal(adam[k][f],checkpoint['adam'][i][k][f]),'Frozen Adam state moved')
            for k in keys:require(float(adam[k]['step'])==110,'Active Adam age changed')
        freeze.append(dict(update_G=update_G,update_head=update_head,models=32,passed=True))
        del branch
    immutable(root/'occupancy-audit.json',dict(passed=True,models=32,rows=records,freeze_modes=freeze,
            parameter_max_error=max(v['absolute_error'] for v in records if '.' not in v['field']),
            Adam_max_error=max(v['absolute_error'] for v in records if '.' in v['field'])))
    del engine,references;torch.cuda.empty_cache()

def observe(pool,jobs,data,root):
    sampler=Sampler(root/'sustained-nvidia-smi.json').start();rows=[]
    try:
        time.sleep(7);baseline=sampler.summary('baseline')
        for backend,n,graph,duration,cap in [('independent',8,False,8.,400),('independent',32,True,8.,600),('streams',32,True,30.,1000)]:
            name=f'{backend}-{n}-'+('graph' if graph else 'eager');sampler.label(name+'-setup')
            torch.cuda.empty_cache();torch.cuda.reset_peak_memory_stats();setup=time.perf_counter()
            engine=Engine(data[:n],jobs[:n],backend)
            if graph:engine.capture()
            torch.cuda.synchronize();setup=time.perf_counter()-setup
            initial={k:p.detach().clone() for k,p in engine.net.named_parameters()}
            def reset_probe():
                with torch.no_grad():
                    for k,p in engine.net.named_parameters():p.copy_(initial[k]);p.grad.zero_()
                    for s in engine.opt.state.values():
                        for v in s.values():v.zero_()
                    engine.net.bad.zero_();engine.steps=0
            engine.advance(10);reset_probe();torch.cuda.synchronize()
            sampler.label(name);started=time.perf_counter();updates=0;blocks=0
            # Repeated bounded prefixes, not a long train-to-convergence model.
            while time.perf_counter()-started<duration and blocks<12:
                engine.advance(cap);updates+=cap;blocks+=1;reset_probe();torch.cuda.synchronize()
                progress('GPU_sustained_window',case=name,seconds=time.perf_counter()-started,blocks=blocks)
            elapsed=time.perf_counter()-started
            row=dict(name=name,backend=backend,models=n,cuda_graph=graph,seconds=elapsed,
                  prefix_updates=cap,prefix_blocks=blocks,model_updates=n*updates,
                  model_updates_per_second=n*updates/elapsed,setup_seconds=setup,
                  peak_allocated_MiB=torch.cuda.max_memory_allocated()/1048576,
                  peak_reserved_MiB=torch.cuda.max_memory_reserved()/1048576,
                  telemetry=sampler.summary(name),reset_to_initial_between_prefixes=True,official_models_created=0)
            sampler.label(name+'-cleanup');rows.append(row);del engine,initial;torch.cuda.empty_cache()
    finally:sampler.stop()
    immutable(root/'sustained-summary.json',dict(baseline=baseline,cases=rows,official_models_created=0,actual_H_U_reads=0))
    return baseline,rows

def mdtable(rows):
    lines=['| 路径 | 模型并发 | 模型更新每秒 | GPU忙碌均值 | PyTorch峰值MiB | 整卡峰值MiB | 样本数 |',
           '| --- | ---: | ---: | ---: | ---: | ---: | ---: |']
    for r in rows:
        t=r['telemetry'];u=t.get('utilization.gpu',{}).get('mean',float('nan'));mem=t.get('memory.used',{}).get('maximum',float('nan'))
        lines.append(f"| {r['name']} | {r['models']} | {r['model_updates_per_second']:.1f} | {u:.1f}% | {r['peak_allocated_MiB']:.1f} | {mem:.0f} | {t['samples']} |")
    return '\n'.join(lines)

def report(root,baseline,rows):
    stream=next(r for r in rows if r['backend']=='streams');eager=rows[0]
    ratio=stream['model_updates_per_second']/eager['model_updates_per_second']
    audit=read(root/'occupancy-audit.json');numeric=read(OUT/'engineering/numeric-04/qualification.json')
    old=read(OUT/'engineering/gpu-02/summary.json')
    # Check only actually decoded source assets; historical query bytes remain unopened.
    for r in READS:
        info=contract()['files'][r['path']]
        require(r['kind'] in {'classification','base','target-P','target-G'},'Unexpected numeric access')
        require(sha(ROOT/r['path'])==info['sha256'],'Decoded source modified')
    text=f'''# JAT1 显卡利用率与CUDA工程验收报告

日期：2026-10-16。完成训练核心实现、780角色资产登记、源内数值验收与显卡观测。正式业务矩阵尚未启动，未读取query数值/标签、实际H/U、native或PCAP。

## 实测结果

显卡为RTX 4060 Ti，显存16380 MiB。以下是相邻时间窗口的真实CUDA训练计算，重复使用12个固定合法源内任务，不是空矩阵或分配显存的占位负载。

{mdtable(rows)}

8-stream、32个独立模型加CUDA Graph的实测吞吐是普通执行的约 **{ratio:.2f}倍**。32模型持续观测 {stream['seconds']:.2f} 秒，累计 {stream['model_updates']} 次模型更新；每个探针块最多1000步，块间复原初值和Adam状态，不导出正式模型或业务评价。

观测基线整卡GPU忙碌均值为 {baseline.get('utilization.gpu',{}).get('mean',0):.2f}%。nvidia-smi是整卡时间忙碌比例，含Windows桌面及其他进程，不是本进程SM occupancy或理论FLOPS。更高的GPU百分比不一定更快；本轮以合法更新吞吐为主要性能依据。

## 为什么不把16GB显存填满

模型仅2318个参数，当前真实训练槽480行。显存占用主要是数据、CUDA工作区、图及自动微分缓冲，而非参数本身。先前批大小扫描中，多stream的8/32/64/128模型吞吐依次约为 {', '.join(str(round(v['model_updates_per_second'])) for v in old['cases'] if v['backend']=='streams')} 次模型更新/秒；扩大到64、128没有继续加速，却提高了显存占用。

因此推荐32模型、最多8个CUDA streams，并缓存合法源内输入。保留余量比重复堆数据或空缓存更有意义。PyTorch allocated/reserved与整卡显存分别记录，不能把nvidia-smi的memory utilization当作容量使用比例。当前还没有测量SM占用率、显存带宽峰值或理论算力利用率，不能说已达到硬件峰值。

## 数值资格与保留的失败

独立CUDA Graph及多stream路径通过原计划的参数/Adam前缀门。当前选定32模型规模全部模型在1/10/100步与独立执行比较通过，最大参数差 {audit['parameter_max_error']:.3e}，Adam差 {audit['Adam_max_error']:.3e}；两种冻结续训的参数和冻结Adam状态保持不变。

张量化BMM路径未通过门限，因而未用于性能推荐或正式训练。它在float32分支的不同数值路径造成后续float64头参数偏差，不能为追求速度把门限放宽。失败详情保留在numeric-01/02/03/04中。

numeric-02还出现两项工程记录问题：多stream检查点误把独立Adam矩当成堆叠矩切片；再次发布时尝试覆盖旧latest记录。修订仅涉及状态导出和版本索引。其失败记录未覆盖；修订后的numeric-03/04重新验收。冻结参数的Adam状态保留接口也已纳入numeric-04及32模型复核。

## 已实现与尚未执行

已实现完整可训练W/V/c/G、原带权分类与关联目标、实际输出单位L2、独立模型优化器/clip、两种冻结继续、检查点继承、CUDA Graph与多stream、训练数据权限适配器、数值测试及遥测。

未执行720源内完整选择、60外层角色训练、H预测或业务评分。完整P2至P5调度和评分程序尚未封存为可执行实验，当前CLI只提供register/tests/profile，不能把训练核心完成写成全方案实施完成。

下一步先完成固定12任务P1工程先导，并实测2000步、中点分叉及928行外层规模，再冻结全矩阵执行版本。按本次内层稳态吞吐简单折算24480000次源内更新约 {24480000/stream['model_updates_per_second']/3600:.2f} 小时；它不包含图准备、IO、外层、教师和审计，也没有测量所有λ/lr/冻结模式，不能当作整轮完成时间承诺。

## 产物与复核

- 当前32模型复核与长窗口观测：`{rel(root)}`。
- 原始显卡样本：`sustained-nvidia-smi.json`，包含每秒采样、窗口标签与整卡范围说明。
- 批大小扫描：`outputs/joint-associated-post-classifier-20261016/run-01/engineering/gpu-02/summary.json`。
- 最终核心资格：`outputs/joint-associated-post-classifier-20261016/run-01/engineering/numeric-04/qualification.json`。
- 实现：`eval/joint_associated_post_classifier/`；独立复核脚本位于`eval/joint_associated_post_classifier_gpu_analysis/`。

这是性能与工程报告，不包含任何新F1、CE或Brier实验结论。
'''
    path=writable(DOC/'gpu-utilization-report-20261016.md');require(not path.exists(),'Report already exists');path.write_text(text,encoding='utf-8')
    immutable(root/'closeout.json',dict(passed=True,report_path=rel(path),report_sha256=sha(path),source_inputs_unchanged=True,
               preferred_backend='streams',streams=8,batch_models=32,cuda_graph=True,sustained_speedup=ratio,
               formal_matrix_started=False,P1_full_pilot_complete=False,query_reads=0,actual_H_reads=0,actual_U_reads=0,
               implementation_scope='training core and GPU engineering, not complete P2-P5 orchestrator'))

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--tag',default='occupancy-01');args=parser.parse_args()
    with engineering(args.tag) as root:
        immutable(root/'analysis-code.json',dict(path=rel(__file__),sha256=sha(__file__)))
        q=read(OUT/'engineering/numeric-04/registered-qualification.json')
        for p,h in q['code_sha256'].items():require(sha(ROOT/p)==h,'Code changed after final qualification')
        pool=TrainingPool();jobs,data=jobs32(pool)
        occupancy_audit(jobs,data,root)
        baseline,rows=observe(pool,jobs,data,root)
        report(root,baseline,rows)
        progress('GPU_engineering_closeout',report=rel(DOC/'gpu-utilization-report-20261016.md'))

if __name__=='__main__':main()
