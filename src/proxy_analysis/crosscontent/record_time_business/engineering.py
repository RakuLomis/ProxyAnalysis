"""Train-only smoke and resource gate; never inspect held-out predictions."""
import copy
import time
import os
os.environ.setdefault('CUBLAS_WORKSPACE_CONFIG',':4096:8')
import numpy as np
# This Windows environment must load Arrow/pandas before torch DLLs.
from .data import OUT,DOC,cfg,load,read,js,save
import torch
from .tensors import Store
from .model import Hierarchy,transformed,vicreg
from .cuda_packing import prepare_flows,state_key,require_cuda

def setup(seed):
    if not torch.cuda.is_available():
        raise RuntimeError('CUDA is required for business training and inference; CPU fallback is forbidden')
    torch.set_num_threads(1);torch.manual_seed(seed);np.random.seed(seed)
    torch.use_deterministic_algorithms(True)
    torch.backends.cudnn.benchmark=False;torch.backends.cudnn.deterministic=True
    torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
    return torch.device('cuda:0')

def input_visits(store,visits,arm,state,device=None):
    cache_key=None
    if device is not None:
        context=state_key(state)
        if not hasattr(store,'_gpu_visit_cache') or getattr(store,'_gpu_cache_context',None)!=context:
            store._gpu_visit_cache={};store._gpu_cache_context=context
        cache_key=(tuple(visits),arm,context,str(device))
        if cache_key in store._gpu_visit_cache:return store._gpu_visit_cache[cache_key]
    rep={'S0':'R','S1':'P','S2':'R','S3':'C','S4':'R'}.get(arm,'R');data=[];sizes=[]
    for sid in visits:
        ids=store.visit[sid];sizes.append(len(ids))
        data.extend(transformed(store,u,'post',rep,state,no_type=arm=='S4') for u in ids)
    if device is not None:
        prepared=prepare_flows(data,arm,device)
        if len(store._gpu_visit_cache)>=32:
            store._gpu_visit_cache.pop(next(iter(store._gpu_visit_cache)))
        store._gpu_visit_cache[cache_key]=(prepared,sizes)
        return prepared,sizes
    return data,sizes

def supervised_step(model,opt,store,visits,arm,state,labels):
    require_cuda(model)
    x,sizes=input_visits(store,visits,arm,state,next(model.parameters()).device);opt.zero_grad(set_to_none=True)
    logits=model.visits(x,sizes,arm);target=torch.tensor([labels[s] for s in visits],device=logits.device)
    ce=torch.nn.functional.cross_entropy(logits,target)
    reg=sum(p.square().sum() for n,p in model.named_parameters() if n.endswith('weight') and not n.startswith('projector.'))
    loss=ce+.5*cfg()['weight_l2']*reg;loss.backward();opt.step()
    return float(loss.detach()),{'ce':float(ce.detach())}

def ssl_step(model,opt,store,slot,arm,state,rng):
    require_cuda(model)
    a=[];b=[]
    for r in slot['batch']:
        uid=r['uid'];donor=r['donor_uid']
        if arm=='L1':left=(uid,'post');right=left
        elif arm=='L2':left=(uid,slot['L2_side']);right=left
        elif arm=='L3':left=(uid,'post');right=(uid,'pre')
        else:left=(uid,'post');right=(donor,'pre')
        a.append(transformed(store,*left,'R',state,mask_rng=rng));b.append(transformed(store,*right,'R',state,mask_rng=rng))
    opt.zero_grad(set_to_none=True)
    ha=model.flows(a,arm);hb=model.flows(b,arm)
    loss,diag=vicreg(model.projector(ha),model.projector(hb));loss.backward();opt.step()
    diag['flow_std_mean']=float(ha.detach().std(0).mean());return float(loss.detach()),diag

@torch.inference_mode()
def predict_visits(model,store,visits,arm,state):
    require_cuda(model);model.eval()
    x,sizes=input_visits(store,visits,arm,state,next(model.parameters()).device)
    logits=model.visits(x,sizes,arm)
    assert logits.is_cuda
    probabilities=torch.softmax(logits,dim=1)
    assert probabilities.is_cuda
    return probabilities

def engineer():
    device=setup(cfg()['seeds'][0]);store=Store();cohort=load('cohort');folds=load('folds')
    train=folds[(folds.fold==0)&(folds.split=='train')];assert len(train)==96
    classes=sorted(cohort.label_id.unique());labels={r.session_id:classes.index(r.label_id) for r in train.itertuples()}
    allscalers=read(OUT/'preprocessors.json');state={rep:allscalers['0:'+rep] for rep in ['P','R','C','T']}
    slots=read(OUT/f"schedule-0-{cfg()['seeds'][0]}.json");rows=[]
    # Only training flow used for numerical mode agreement.
    uid=store.visit[train.iloc[0].session_id][0];x=[transformed(store,uid,'post','R',state)]
    model=Hierarchy().to(device)
    with torch.no_grad():
        cpu=copy.deepcopy(model).cpu();reference=cpu.flows(x,'S2');actual=model.flows(x,'S2').cpu()
        difference=float((reference-actual).abs().max());assert torch.allclose(reference,actual,atol=2e-5,rtol=2e-4)
    for arm in cfg()['supervised_arms']+cfg()['ssl_arms']:
        setup(cfg()['seeds'][0]);model=Hierarchy().to(device);opt=torch.optim.Adam(model.parameters(),lr=cfg()['learning_rate']);rng=np.random.default_rng(cfg()['seeds'][0])
        if device.type=='cuda':torch.cuda.reset_peak_memory_stats();torch.cuda.synchronize()
        start=time.monotonic();losses=[];diag={}
        for step in range(cfg()['engineering_steps']):
            slot=slots[step]
            if arm.startswith('S'):loss,diag=supervised_step(model,opt,store,[b['session_id'] for b in slot['batch']],arm,state,labels)
            else:loss,diag=ssl_step(model,opt,store,slot,arm,state,rng)
            assert np.isfinite(loss);losses.append(loss)
        if device.type=='cuda':torch.cuda.synchronize()
        elapsed=time.monotonic()-start
        rows.append({'arm':arm,'steps':len(losses),'seconds':elapsed,'seconds_per_step':elapsed/len(losses),
            'initial_loss':losses[0],'final_loss':losses[-1],**diag,
            'peak_allocated_bytes':torch.cuda.max_memory_allocated() if device.type=='cuda' else None})
        print('B6',arm,'seconds/step',round(elapsed/len(losses),4),'loss',round(losses[-1],4),flush=True)
        assert all(p.grad is None or torch.isfinite(p.grad).all() for p in model.parameters())
    r=save('engineering-smoke',rows).set_index('arm')
    estimated=15*cfg()['steps']*(r.loc[cfg()['supervised_arms'],'seconds_per_step'].sum()+4*r.loc['S2','seconds_per_step']+r.loc[cfg()['ssl_arms'],'seconds_per_step'].sum())
    result={'device':str(device),'device_name':torch.cuda.get_device_name() if device.type=='cuda' else 'CPU','torch':torch.__version__,
       'dtype':'float32','deterministic_algorithms':True,'cpu_gpu_max_forward_difference':difference,'outer_test_read':False,
       'formal_stages':195,'estimated_training_seconds':float(estimated),'estimated_training_hours':float(estimated/3600),
       'estimate_excludes_evaluation_IO_bootstrap':True,'peak_allocated_bytes':int(r.peak_allocated_bytes.max()) if device.type=='cuda' else None,
       'qualification_gate_passed':True,'engineering_smoke_passed':True,'formal_training_started':False}
    js('budget-final.json',result)
    DOC.mkdir(exist_ok=True,parents=True)
    from ...protocol_normalization.record_representation.report import table
    (DOC/'engineering-report.md').write_text('# B4–B6 工程验收\n\n只使用旧fold0训练内容，未读取测试预测。全序列无截断，静态/时间分支分开。\n\n'+table(r.reset_index())+f'\n\n正式195阶段估算训练耗时 {estimated/3600:.2f} 小时，未计评估与I/O；这不是已完成训练。\n\n设备：{result["device_name"]}。CPU/GPU训练样本forward最大差：{difference:.8g}。\n',encoding='utf-8')
    print('B6 estimate hours:',estimated/3600,flush=True)
