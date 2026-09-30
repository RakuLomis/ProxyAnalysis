"""B7-B9 CUDA-only, resumable formal execution of the frozen 195-stage matrix."""
import os
import json
import time
import traceback
from datetime import datetime,timezone
from pathlib import Path
from .data import ROOT,OUT,DOC,CONFIG,PLAN,cfg,load,read,js,digest
from .tensors import Store
from .engineering import setup,supervised_step,ssl_step,predict_visits
from .model import Hierarchy
from .cuda_packing import require_cuda
import numpy as np
import pandas as pd
import torch

FORMAL=OUT/'formal'
ENCODER=('structure.','temporal.','sproj.','tproj.','fusion.')

def now():return datetime.now(timezone.utc).isoformat()
def write_json(path,obj):
    path=Path(path);path.parent.mkdir(exist_ok=True,parents=True)
    temp=path.with_suffix(path.suffix+'.tmp')
    temp.write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8');os.replace(temp,path)
def checkpoint(path,obj):
    temp=path.with_suffix('.tmp');torch.save(obj,temp);os.replace(temp,path)

def specification():
    jobs=[]
    for fold in range(5):
        for seed in cfg()['seeds']:
            for arm in cfg()['supervised_arms']:
                jobs.append({'fold':fold,'seed':seed,'arm':arm,'phase':'supervised'})
            for arm in cfg()['ssl_arms']:
                jobs.extend({'fold':fold,'seed':seed,'arm':arm,'phase':phase} for phase in ['ssl','finetune'])
    assert len(jobs)==195
    return jobs

def job_name(job):return f"f{job['fold']}-s{job['seed']}-{job['arm']}-{job['phase']}"

class View:
    """Restrict the store exposed to a stage. Inference cannot access any pre."""
    def __init__(self,store,visits,sides):
        self.visit={sid:store.visit[sid] for sid in visits}
        self.uid_to_visit={u:s for s,ids in self.visit.items() for u in ids}
        self.data={(u,side):store.data[u,side] for u in self.uid_to_visit for side in sides}
        self._gpu_visit_cache={}

def freeze_formal():
    FORMAL.mkdir(exist_ok=True,parents=True)
    assert read(OUT/'qualification-gate.json')['passed']
    assert read(OUT/'pretraining-audit.json')['passed']
    gpu=read(OUT/'cuda-runtime-audit.json')
    assert gpu['training_checked_on_cuda'] and gpu['prediction_checked_on_cuda'] and not gpu['cpu_fallback']
    for path,h in read(OUT/'contract.json')['inputs'].items():assert digest(path)==h,'old input changed'
    files=[CONFIG,PLAN,ROOT/'configs/record-time-business-cuda.yaml',
           *Path(__file__).parent.glob('*.py'),ROOT/'eval/record_time_business/run.py',
           *[OUT/(x+'.parquet') for x in ['cohort','folds','common-flow-cohort','tensor-manifest','ssl-pool']],
           OUT/'preprocessors.json',OUT/'exposure-audit.json',*OUT.glob('schedule-*.json')]
    manifest=load('tensor-manifest')
    for r in manifest.itertuples():assert digest(r.path)==r.sha256,'tensor changed'
    contract={'files':{str(p):digest(p) for p in sorted(files)},'jobs':specification(),
       'steps_per_stage':cfg()['steps'],'device':'cuda','dtype':'float32','amp':False,'tf32':False,
       'effective_batch':24,'evaluation':'post_only_outer_content_holdout','labels':sorted(load('cohort').label_id.unique()),
       'pretrain_test_adaptation':False,'checkpoints_every_steps':100,'early_stopping':False}
    path=FORMAL/'contract.json'
    if path.exists():assert read(path)==contract,'Formal contract changed; refuse mixed-code resume'
    else:write_json(path,contract)
    return contract

def initialize(job,device):
    setup(job['seed']);model=Hierarchy().to(device)
    if job['phase']=='finetune':
        parent={**job,'phase':'ssl'};directory=FORMAL/job_name(parent);done=read(directory/'done.json')
        path=directory/'final.pt';assert digest(path)==done['checkpoint_sha256']
        source=torch.load(path,map_location=device,weights_only=False)['model']
        fresh=model.state_dict();head={k:v.clone() for k,v in fresh.items() if k.startswith('head.')}
        for k in fresh:
            if k.startswith(ENCODER):fresh[k]=source[k]
        model.load_state_dict(fresh)
        assert all(torch.equal(model.state_dict()[k],v) for k,v in head.items())
    require_cuda(model);return model

def validate_slots(slots,train_view):
    assert len(slots)==1000
    for slot in slots:
        assert len(slot['batch'])==24
        for r in slot['batch']:
            assert r['session_id'] in train_view.visit
            assert r['uid'] in train_view.visit[r['session_id']]
            assert r['donor_uid'] in train_view.uid_to_visit

def progress(completed,total,current=None,step=None,status='running',**extra):
    write_json(FORMAL/'progress.json',{'status':status,'updated_at':now(),'completed_stages':completed,
        'total_stages':total,'current_job':current,'current_step':step,'device':'cuda',**extra})

def run_job(job,store,folds,scalers,labels,completed):
    name=job_name(job);directory=FORMAL/name;directory.mkdir(exist_ok=True)
    if (directory/'done.json').exists():
        done=read(directory/'done.json');assert digest(directory/'final.pt')==done['checkpoint_sha256']
        if job['phase']!='ssl':assert digest(directory/'predictions.parquet')==done['predictions_sha256']
        return
    f=folds[folds.fold==job['fold']];train=f[f.split=='train'];test=f[f.split=='test']
    assert len(train)==96 and len(test)==24
    assert not set(train.content_id)&set(test.content_id)
    train_view=View(store,train.session_id,['pre','post'] if job['phase']=='ssl' else ['post'])
    slots=read(OUT/f"schedule-{job['fold']}-{job['seed']}.json")
    validate_slots(slots,train_view)
    state={rep:scalers[f"{job['fold']}:{rep}"] for rep in ['P','R','C','T']}
    assert all(set(v['fit_visits'])==set(train.session_id) for v in state.values())
    device=setup(job['seed']);model=initialize(job,device);model.train()
    optimizer=torch.optim.Adam(model.parameters(),lr=cfg()['learning_rate']);rng=np.random.default_rng(job['seed'])
    start=0;history=[];prior_seconds=0.0;latest=directory/'latest.pt'
    if latest.exists():
        resumed=torch.load(latest,map_location=device,weights_only=False)
        assert resumed['job']==job and resumed['contract_sha256']==digest(FORMAL/'contract.json')
        model.load_state_dict(resumed['model']);optimizer.load_state_dict(resumed['optimizer'])
        rng.bit_generator.state=resumed['numpy_rng'];torch.set_rng_state(resumed['torch_rng'].cpu())
        torch.cuda.set_rng_state_all([x.cpu() for x in resumed['cuda_rng']])
        start=resumed['step'];history=resumed['history'];prior_seconds=resumed['training_seconds']
    torch.cuda.reset_peak_memory_stats();torch.cuda.synchronize();started=time.perf_counter()
    train_labels={r.session_id:labels.index(r.label_id) for r in train.itertuples()}
    for index in range(start,cfg()['steps']):
        slot=slots[index]
        if job['phase']=='ssl':loss,diag=ssl_step(model,optimizer,train_view,slot,job['arm'],state,rng)
        else:loss,diag=supervised_step(model,optimizer,train_view,[r['session_id'] for r in slot['batch']],job['arm'],state,train_labels)
        if not np.isfinite(loss):raise FloatingPointError(f'{name}: nonfinite loss at step {index+1}')
        history.append({'step':index+1,'loss':loss,**diag})
        if (index+1)%100==0:
            assert bool(torch.stack([torch.isfinite(p).all() for p in model.parameters()]).all())
            torch.cuda.synchronize();elapsed=prior_seconds+time.perf_counter()-started
            checkpoint(latest,{'job':job,'step':index+1,'model':model.state_dict(),'optimizer':optimizer.state_dict(),
                'numpy_rng':rng.bit_generator.state,'torch_rng':torch.get_rng_state(),'cuda_rng':torch.cuda.get_rng_state_all(),
                'history':history,'training_seconds':elapsed,'contract_sha256':digest(FORMAL/'contract.json')})
            progress(completed,195,name,index+1,training_seconds=elapsed,loss=loss)
            print(name,index+1,'/1000 loss',round(loss,6),flush=True)
    torch.cuda.synchronize();seconds=prior_seconds+time.perf_counter()-started
    checkpoint(directory/'final.pt',{'model':model.state_dict(),'job':job,'step':1000,
        'contract_sha256':digest(FORMAL/'contract.json'),'device':'cuda','initialization_seed':job['seed']})
    pd.DataFrame(history).to_parquet(directory/'training-log.parquet',index=False)
    done={'job':job,'steps':1000,'training_seconds':seconds,'cuda_peak_allocated_bytes':torch.cuda.max_memory_allocated(),
        'checkpoint_sha256':digest(directory/'final.pt'),'inference_device':None,'completed_at':now(),
        'train_visits':96,'train_contents':24,'effective_batch':24,'test_pre_exposed_to_inference':False}
    if job['phase']!='ssl':
        evaluation=View(store,test.session_id,['post']);assert all(side=='post' for _,side in evaluation.data)
        ids=test.session_id.tolist();probabilities=predict_visits(model,evaluation,ids,job['arm'],state)
        assert probabilities.is_cuda and torch.isfinite(probabilities).all()
        torch.testing.assert_close(probabilities.sum(1),torch.ones(24,device=device))
        values=probabilities.cpu().numpy();rows=[]
        for row,prob in zip(test.to_dict('records'),values):
            rows.append({**{k:row[k] for k in ['session_id','content_id','label_id','repetition']},**job,
                'target':labels.index(row['label_id']),'prediction':int(prob.argmax()),
                **{f'p{j}':float(v) for j,v in enumerate(prob)},'inference_device':'cuda'})
        pd.DataFrame(rows).to_parquet(directory/'predictions.parquet',index=False)
        done['predictions_sha256']=digest(directory/'predictions.parquet');done['inference_device']='cuda'
        del evaluation,probabilities
    write_json(directory/'done.json',done)
    del model,optimizer,train_view;torch.cuda.empty_cache()

def replay(store,folds,scalers,contract):
    """Reload final classifiers, replay on CUDA with a different visit batch size."""
    device=setup(cfg()['seeds'][0]);rows=[]
    for job in contract['jobs']:
        if job['phase']=='ssl':continue
        directory=FORMAL/job_name(job);done=read(directory/'done.json');assert digest(directory/'final.pt')==done['checkpoint_sha256']
        saved=pd.read_parquet(directory/'predictions.parquet');test=folds[(folds.fold==job['fold'])&(folds.split=='test')]
        assert set(saved.session_id)==set(test.session_id)
        view=View(store,test.session_id,['post']);state={rep:scalers[f"{job['fold']}:{rep}"] for rep in ['P','R','C','T']}
        model=Hierarchy().to(device);model.load_state_dict(torch.load(directory/'final.pt',map_location=device,weights_only=False)['model'])
        ids=saved.session_id.tolist();p=[]
        for start in range(0,24,6):p.append(predict_visits(model,view,ids[start:start+6],job['arm'],state).cpu().numpy())
        actual=np.concatenate(p);expected=saved[[f'p{i}' for i in range(6)]].to_numpy()
        delta=float(np.max(np.abs(actual-expected)));np.testing.assert_allclose(actual,expected,atol=2e-5,rtol=2e-4)
        assert np.array_equal(actual.argmax(1),saved.prediction)
        rows.append({**job,'max_probability_difference':delta,'same_decisions':True,'replay_device':'cuda','new_batch_size':6})
        del model,view;torch.cuda.empty_cache()
    pd.DataFrame(rows).to_parquet(FORMAL/'replay-audit.parquet',index=False)
    write_json(FORMAL/'replay-audit.json',{'classifiers':len(rows),'OOF_rows':3240,'all_passed':True,
        'max_probability_difference':max(r['max_probability_difference'] for r in rows),'device':'cuda',
        'test_pre_available_in_view':False,'heldout_data_fitted':False})

def run():
    # Exclusive process lock, automatically released even after a killed process.
    import msvcrt
    FORMAL.mkdir(parents=True,exist_ok=True)
    with (FORMAL/'process.lock').open('a+b') as lock:
        lock.seek(0);lock.write(b'0');lock.flush();lock.seek(0)
        try:msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
        except OSError:raise RuntimeError('A formal experiment process already owns this run')
        try:
            contract=freeze_formal();device=setup(cfg()['seeds'][0]);store=Store();folds=load('folds');scalers=read(OUT/'preprocessors.json')
            write_json(FORMAL/'launch.json',{'pid':os.getpid(),'started_at':now(),'device':str(device),
                'device_name':torch.cuda.get_device_name(),'contract_sha256':digest(FORMAL/'contract.json')})
            js('stage-status.json',{'B0_B6':'complete','B7_B10':'running','formal_training_started':True,
                'runtime_policy':'cuda_only_no_cpu_fallback','progress_file':str(FORMAL/'progress.json')})
            for i,job in enumerate(contract['jobs']):
                run_job(job,store,folds,scalers,contract['labels'],i)
                progress(i+1,195,job_name(job),1000)
                print('COMPLETED',i+1,'/195',job_name(job),flush=True)
            progress(195,195,status='replaying_cuda_predictions')
            replay(store,folds,scalers,contract)
            for path,h in contract['files'].items():assert digest(path)==h,'Frozen formal input/code changed during run'
            progress(195,195,status='reporting')
            from .formal_report import report
            report()
            progress(195,195,status='complete',report=str(DOC/'formal-results.md'))
            js('stage-status.json',{'B0_B10':'complete','formal_training_started':True,'formal_stages':195,
                'report':str(DOC/'formal-results.md'),'runtime_policy':'cuda_only_no_cpu_fallback'})
        except BaseException as error:
            previous=read(FORMAL/'progress.json') if (FORMAL/'progress.json').exists() else {}
            write_json(FORMAL/'failure.json',{'time':now(),'error':repr(error),'traceback':traceback.format_exc(),'previous_progress':previous})
            progress(previous.get('completed_stages',0),195,previous.get('current_job'),previous.get('current_step'),status='failed',error=repr(error))
            raise
        finally:
            lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_UNLCK,1)
