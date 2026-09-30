"""Paired GPU performance/equivalence checks on training data only."""
import time
import copy
import json
from .data import OUT,DOC,ROOT,cfg,load,read,js,save,digest
from .engineering import setup,input_visits,supervised_step,ssl_step,predict_visits
from .tensors import Store
from .model import Hierarchy
from .cuda_packing import require_cuda
from .cuda_reference import ReferenceSequenceEncoder
import numpy as np
import torch

def reference_model(device):
    model=Hierarchy().to(device)
    for key,channels in [('structure',7),('temporal',4)]:
        old=getattr(model,key);replacement=ReferenceSequenceEncoder(channels,chunk=old.chunk).to(device)
        replacement.load_state_dict(old.state_dict());setattr(model,key,replacement)
    return model

def reference_supervised(model,opt,store,visits,arm,state,labels):
    require_cuda(model);x,sizes=input_visits(store,visits,arm,state)
    opt.zero_grad(set_to_none=True);logits=model.visits(x,sizes,arm)
    target=torch.tensor([labels[s] for s in visits],device=logits.device)
    ce=torch.nn.functional.cross_entropy(logits,target)
    regularizer=sum(p.square().sum() for n,p in model.named_parameters() if n.endswith('weight') and not n.startswith('projector.'))
    loss=ce+.5*cfg()['weight_l2']*regularizer;loss.backward();opt.step()
    return float(loss.detach()),{'ce':float(ce.detach())}

def benchmark():
    seed=cfg()['seeds'][0];device=setup(seed);store=Store();folds=load('folds');cohort=load('cohort')
    train=folds[(folds.fold==0)&(folds.split=='train')];labels=sorted(cohort.label_id.unique())
    labels={r.session_id:labels.index(r.label_id) for r in train.itertuples()}
    scale=read(OUT/'preprocessors.json');state={k:scale['0:'+k] for k in ['P','R','C','T']}
    slots=read(OUT/f'schedule-0-{seed}.json');rows=[];equivalence=[]
    for arm in cfg()['supervised_arms']+cfg()['ssl_arms']:
        setup(seed);baseline=reference_model(device);setup(seed);fast=Hierarchy().to(device)
        fast.load_state_dict(baseline.state_dict())
        # Compare complete 24-visit batch before any fitting; only training visits.
        visits=[r['session_id'] for r in slots[0]['batch']]
        x,sizes=input_visits(store,visits,arm,state)
        ready,ready_sizes=input_visits(store,visits,arm,state,device)
        baseline.zero_grad();fast.zero_grad()
        a=baseline.visits(x,sizes,arm);b=fast.visits(ready,ready_sizes,arm)
        diff=float((a-b).abs().max());torch.testing.assert_close(a,b,atol=2e-5,rtol=2e-4)
        a.square().mean().backward();b.square().mean().backward();gradient_max=0.0
        for (n,p),(m,q) in zip(baseline.named_parameters(),fast.named_parameters()):
            assert n==m
            if p.grad is None:assert q.grad is None
            else:
                torch.testing.assert_close(p.grad,q.grad,atol=2e-5,rtol=2e-4)
                gradient_max=max(gradient_max,float((p.grad-q.grad).abs().max()))
        equivalence.append({'arm':arm,'max_logit_difference':diff,'max_gradient_difference':gradient_max,'training_only':True})
        del a,b,x,ready
        models={'reference':baseline,'optimized':fast}
        for mode in ['reference','optimized']:
            model=models[mode];model.train();store._gpu_visit_cache={}
            optimizer=torch.optim.Adam(model.parameters(),lr=cfg()['learning_rate']);rng=np.random.default_rng(seed)
            losses=[]
            # Four warmup batches prepare the complete repeated supervised batch schedule.
            for step in range(12):
                if step==4:
                    torch.cuda.synchronize();torch.cuda.reset_peak_memory_stats();started=time.perf_counter()
                slot=slots[step];visits=[r['session_id'] for r in slot['batch']]
                if arm.startswith('S'):
                    fn=reference_supervised if mode=='reference' else supervised_step
                    loss,_=fn(model,optimizer,store,visits,arm,state,labels)
                else:loss,_=ssl_step(model,optimizer,store,slot,arm,state,rng)
                assert np.isfinite(loss);losses.append(loss)
            torch.cuda.synchronize();seconds=time.perf_counter()-started
            rows.append({'arm':arm,'mode':mode,'timed_steps':8,'warmup_steps':4,'seconds_per_step':seconds/8,
                'final_loss':losses[-1],'device':str(device),'peak_allocated_bytes':torch.cuda.max_memory_allocated(),
                'resident_input_bytes':sum(v[0].bytes for v in store._gpu_visit_cache.values())})
            print('CUDA bench',arm,mode,round(seconds/8,5),'sec/step',flush=True)
        # Business prediction must return CUDA probabilities (host only for later metrics).
        visits=[r['session_id'] for r in slots[0]['batch']]
        probabilities=predict_visits(fast,store,visits,arm,state)
        assert probabilities.is_cuda and torch.isfinite(probabilities).all()
        torch.testing.assert_close(probabilities.sum(1),torch.ones(len(visits),device=device))
        del probabilities,baseline,fast,models,model,optimizer;store._gpu_visit_cache={};torch.cuda.empty_cache()
    frame=save('cuda-performance-benchmark',rows);save('cuda-equivalence-audit',equivalence)
    pivot=frame.pivot(index='arm',columns='mode',values='seconds_per_step')
    pivot['speedup']=pivot.reference/pivot.optimized;save('cuda-speedup-summary',pivot.reset_index())
    def total(col):return float(15*cfg()['steps']*(pivot.loc[cfg()['supervised_arms'],col].sum()+4*pivot.loc['S2',col]+pivot.loc[cfg()['ssl_arms'],col].sum()))
    result={'required_device':'cuda','cpu_fallback':False,'training_checked_on_cuda':True,'prediction_checked_on_cuda':True,
        'device_name':torch.cuda.get_device_name(),'cuda_runtime':torch.version.cuda,'dtype':'float32','amp':False,'tf32':False,
        'deterministic':True,'outer_test_evaluated':False,'formal_training_started':False,
        'architecture_changed':False,'effective_batch_changed':False,'steps_seeds_folds_changed':False,
        'reference_estimate_hours':total('reference')/3600,'optimized_estimate_hours':total('optimized')/3600,
        'aggregate_speedup':total('reference')/total('optimized'),'max_logit_difference':max(x['max_logit_difference'] for x in equivalence),
        'max_gradient_difference':max(x['max_gradient_difference'] for x in equivalence),
        'peak_allocated_bytes':int(frame[frame['mode']=='optimized'].peak_allocated_bytes.max()),
        'timing_excludes_warmup_evaluation_IO':True,'benchmark_fits':18}
    js('cuda-runtime-audit.json',result)
    from ...protocol_normalization.record_representation.report import table
    text=f'''# CUDA 强制执行与等价提速验收

日期：2026-09-26。根据用户要求，业务训练和预测均强制使用 CUDA，不可用即报错；不允许 CPU fallback。CPU仍可用于PCAP解析、文件读取、标量指标与独立单元测试，这不等于模型在CPU训练或预测。

## 优化范围

逐flow小池化改为批量张量运算；重复监督访问批次的标准化/长度分桶/padding结果常驻GPU，避免每步重复打包和搬运。长序列仍有完整halo，没有截断。架构、loss、batch=24、1000步、五折、三个seed和donor均不变。

未启用AMP/TF32或放宽确定性，避免在本轮性能优化中同时更改数值协议。SSL随机掩码仍按原NumPy种子生成，保持原增强规则。

## 同机同训练批次实测

fold0训练内容，九臂每实现4步warmup＋8步计时；这是独立性能验收，不替代原20步工程测试或正式1000步训练。reference与optimized均在CUDA上；benchmark参考实现固定保存为cuda_reference.py。时长由CUDA同步后wall-time测量，不能只用异步调用提交时间。

{table(pivot.reset_index())}

按同一次实测外推195阶段：参考约{result['reference_estimate_hours']:.2f}小时，优化后约{result['optimized_estimate_hours']:.2f}小时，整体约{result['aggregate_speedup']:.2f}倍。未含warmup、评估、I/O及bootstrap；不保证实际完工时间。旧14.7小时基于前轮实测，不覆盖旧报告。

## 等价性与设备核验

{table(pd_equivalence(equivalence))}

所有九臂的训练及预测设备检查通过；预测返回CUDA概率张量，只有汇总指标时才允许搬回CPU。以上数值比较只用训练访问，不读取外层测试预测。CPU上的单位测试仅用于隔离实现错误，不作为业务模型训练或测试。

优化测量峰值allocated约{result['peak_allocated_bytes']/2**20:.1f}MiB；不等同于显卡总占用。小模型和变长序列不保证GPU利用率持续100%，判断效率以端到端吞吐量为准，不靠增大模型或增加无用计算填满显卡。

## 当前状态

CUDA路径和提速验收已落实。正式195阶段仍未启动，本文件不包含任何新业务分类成绩。运行策略见configs/record-time-business-cuda.yaml。
'''
    (DOC/'cuda-performance-report.md').write_text(text,encoding='utf-8')
    js('cuda-code-provenance.json',{'files':{str(p):digest(p) for p in [*Path(__file__).parent.glob('*.py'),ROOT/'configs/record-time-business-cuda.yaml']}})
    print('CUDA optimized estimated hours:',result['optimized_estimate_hours'],flush=True)

def pd_equivalence(rows):
    import pandas as pd
    return pd.DataFrame(rows)

from pathlib import Path
