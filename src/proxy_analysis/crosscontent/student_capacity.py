"""N1 fixed MLP students with frozen historical OOF supervision, no target fitting."""
import argparse
import hashlib
import json
import platform
from pathlib import Path

import numpy as np
# Load Arrow before Torch: avoid Windows native DLL load-order conflicts.
import pyarrow
import yaml
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from threadpoolctl import threadpool_info

from .mechanism_contract import verify as legacy_verify, cohort, read
from .mechanism_report import audit_job
from .business_representations import matrix, dictionary
from .paired_structure_contract import seal, validate_complete
from ..paired_information.prepare import digest, table
from ..reproducibility.preflight import write_json, write_table
import torch

CONFIG=Path('configs/content-generalization-20260916-student-capacity.yaml')


def settings(config=CONFIG):
    cfg=yaml.safe_load(Path(config).read_text(encoding='utf-8'))
    return cfg,Path(cfg['business_root']),Path(cfg['mechanism_root']),Path(cfg['output_root'])


def array_hash(x):
    return hashlib.sha256(np.asarray(x,dtype='<f8').tobytes()).hexdigest()


def state_hash(state):
    h=hashlib.sha256()
    for k,v in sorted(state.items()):h.update(k.encode());h.update(np.asarray(v,dtype='<f8').tobytes())
    return h.hexdigest()


def preprocess(x,state):
    x=np.asarray(x,dtype=float)
    return (np.where(np.isnan(x),state['imputer_statistics'],x)-state['scaler_mean'])/state['scaler_scale']


def export_job(job,lookup,assignment,old_cfg):
    audit_job(job,lookup,assignment,old_cfg)
    mem=read(job/'membership.json');context=mem['context'];rep=context['representation']
    train=[lookup[s] for s in mem['train_ids']]
    fits=read(job/'fit-ledger.json');base=next(f for f in fits if f['arm']=='post')
    labels=base['labels'];hard=np.eye(len(labels))[[labels.index(r['label_id']) for r in train]]
    q={(r['teacher'],r['session_id']):r['probabilities'] for r in table(job/'teacher-oof.parquet')}
    donor={r['receiver']:r['donor'] for r in table(job/'pair-maps.parquet') if r['arm']=='M3'}
    targets={'M0':hard}
    for arm,teacher in [('M1','post'),('M2','pre'),('M3','pre')]:
        t=np.asarray([q[teacher,donor[s] if arm=='M3' else s] for s in mem['train_ids']])
        targets[arm]=.5*hard+.5*t
        fit=next(f for f in fits if f['arm']==arm and f['alpha']==.5)
        if fit['train_ids']!=mem['train_ids'] or np.max(abs(targets[arm]-fit['targets']))>1e-10:
            raise ValueError('Frozen targets not reproduced')
    raw=matrix(train,'post',rep);imp=SimpleImputer(strategy='median',keep_empty_features=True).fit(raw)
    sc=StandardScaler().fit(imp.transform(raw));state={k:base['state'][k] for k in
        ['imputer_statistics','scaler_mean','scaler_scale']}
    for a,b in [(imp.statistics_,state['imputer_statistics']),(sc.mean_,state['scaler_mean']),(sc.scale_,state['scaler_scale'])]:
        if not np.allclose(a,b,atol=1e-12,rtol=0):raise ValueError('Non-source preprocessing')
    out={'context':context,'membership':mem,'labels':labels,'preprocessing':state,
        'targets':{k:v.tolist() for k,v in targets.items()},'donors':donor,
        'teacher_fit_ids':sorted({r['fit_id'] for r in table(job/'teacher-oof.parquet') if r['teacher'] in ('pre','post')}),
        'legacy_complete_sha256':digest(job/'complete.json')}
    for part in ['train','test','target']:
        rows=[lookup[s] for s in mem[part+'_ids']]
        out[part]={'x':preprocess(matrix(rows,'post',rep),state).tolist(),
            'rows':[{k:r[k] for k in ['session_id','content_id','label_id','protocol','repetition']} for r in rows]}
    return out


def freeze(config=CONFIG):
    old_cfg,_,_,_=legacy_verify();cfg,source,legacy,root=settings(config)
    if root.exists():raise FileExistsError(root)
    rows=cohort(source);lookup={r['session_id']:r for r in rows}
    if len(lookup)!=cfg['cohort_size']:raise ValueError('Cohort changed')
    assignment=read(source/'learning/outer-splits.json')
    jobs=sorted((legacy/'jobs').iterdir())
    if len(jobs)!=40:raise ValueError('Expected 40 source jobs')
    prepared={j.name:export_job(j,lookup,assignment,old_cfg) for j in jobs}
    paths=[Path(config),source/'side-summaries.parquet',source/'learning/outer-splits.json',source/'primary-cohort.parquet']
    paths+=list(Path('src/proxy_analysis').rglob('*.py'))
    paths += [p for j in jobs for p in j.iterdir() if p.is_file()]
    root.mkdir(parents=True)
    for name,value in prepared.items():write_json(root/'prepared'/f'{name}.json',value)
    seal(root/'prepared',passed=True,jobs=40)
    write_json(root/'contract/manifest.json',{'config':cfg,'sources':{str(p):digest(p) for p in sorted(set(paths))},
        'prepared_complete_sha256':digest(root/'prepared/complete.json'),'features':dictionary(),
        'primary_ids':sorted(lookup),'assignment':assignment,
        'approval':'User approved starting fixed student-capacity experiment; linear P7 remains deferred'})
    write_json(root/'contract/environment.json',{'python':platform.python_version(),'torch':torch.__version__,
        'numpy':np.__version__,'device':'cpu','dtype':'float64','threadpools':threadpool_info()})
    seal(root/'contract',passed=True)
    print('Frozen 40 audited source jobs and their identical historical targets',flush=True)


def verify(config=CONFIG):
    cfg,source,legacy,root=settings(config);validate_complete(root/'contract')
    man=read(root/'contract/manifest.json')
    if cfg!=man['config']:raise ValueError('Configuration changed')
    for p,h in man['sources'].items():
        if digest(Path(p))!=h:raise ValueError(f'Frozen source changed: {p}')
    if digest(root/'prepared/complete.json')!=man['prepared_complete_sha256']:raise ValueError('Prepared manifest changed')
    validate_complete(root/'prepared');return cfg,source,legacy,root


def setup(cfg):
    torch.set_num_threads(cfg['threads']);torch.use_deterministic_algorithms(True)


def network(d,k,seed,width=32):
    torch.manual_seed(seed)
    return torch.nn.Sequential(torch.nn.Linear(d,width,dtype=torch.float64),torch.nn.ReLU(),
                               torch.nn.Linear(width,k,dtype=torch.float64))


def loss_parts(model,x,targets,weight_l2):
    logp=torch.log_softmax(model(x),dim=1)
    ce=-(targets*logp).sum(1).mean()
    l2=weight_l2/2*sum((p*p).sum() for name,p in model.named_parameters() if name.endswith('weight'))
    return ce+l2,ce,l2


def train(x,targets,seed,cfg):
    x=np.asarray(x,dtype=float);targets=np.asarray(targets,dtype=float)
    if (not np.all(np.isfinite(x)) or not np.all(np.isfinite(targets)) or np.any(targets<0)
        or not np.allclose(targets.sum(1),1,atol=1e-12) or len(x)!=len(targets)):
        raise ValueError('Invalid training inputs')
    model=network(x.shape[1],targets.shape[1],seed,cfg['hidden_width'])
    initial={k:v.detach().numpy().copy().tolist() for k,v in model.state_dict().items()}
    opt=torch.optim.Adam(model.parameters(),lr=cfg['learning_rate'],betas=tuple(cfg['adam_betas']),
                         eps=cfg['adam_eps'],weight_decay=0,foreach=False)
    tx=torch.tensor(x,dtype=torch.float64);tq=torch.tensor(targets,dtype=torch.float64);trace=[]
    for step in range(cfg['steps']):
        opt.zero_grad();loss,ce,l2=loss_parts(model,tx,tq,cfg['weight_l2']);loss.backward()
        grad=max(float(p.grad.abs().max()) for p in model.parameters())
        if not np.isfinite(float(loss.detach())) or not np.isfinite(grad):raise ValueError('Nonfinite optimization')
        trace.append({'step':step,'objective':float(loss.detach()),'soft_ce_nats':float(ce.detach()),
                      'l2':float(l2.detach()),'gradient_inf':grad})
        opt.step()
    with torch.no_grad():
        loss,ce,l2=loss_parts(model,tx,tq,cfg['weight_l2']);p=torch.softmax(model(tx),1).numpy()
    state={k:v.detach().numpy().tolist() for k,v in model.state_dict().items()}
    if not all(np.isfinite(np.asarray(v)).all() for v in state.values()):raise ValueError('Nonfinite weights')
    hard=targets.argmax(1)
    info={'initial_state':initial,'initial_sha256':state_hash(initial),'final_state':state,
        'final_sha256':state_hash(state),'x_sha256':array_hash(x),'targets_sha256':array_hash(targets),
        'final_objective':float(loss),'final_soft_ce_nats':float(ce),'final_l2':float(l2),
        'mean_target_probability_l1':float(np.mean(abs(p-targets).sum(1))),
        'parameter_count':sum(p.numel() for p in model.parameters()),'steps':cfg['steps']}
    return model,info,trace


def run(config=CONFIG,mode='run'):
    cfg,_,_,root=verify(config);setup(cfg)
    if mode=='smoke':
        out=root/'engineering'
        if out.exists():validate_complete(out);return
        records=[]
        # Eight distinct contexts, each repeated: exactly 16 engineering fits.
        for path in sorted((root/'prepared').glob('*-0-*.json')):
            data=read(path);a,info,t=train(data['train']['x'],data['targets']['M2'],cfg['seeds'][0],cfg)
            b,again,_=train(data['train']['x'],data['targets']['M2'],cfg['seeds'][0],cfg)
            if info['final_sha256']!=again['final_sha256']:raise ValueError('Determinism failed')
            records.append({'job':path.stem,'repeat_identical':True,**info})
        if 2*len(records)!=cfg['engineering_fit_budget']:raise ValueError('Smoke budget')
        write_json(out/'fits.json',records);write_json(out/'validation.json',{'passed':True,
            'fresh_fits':2*len(records),'test_predictions_used':False,'hyperparameter_selection':False})
        seal(out,passed=True);print('Engineering gate passed: 16 fits, identical replay, no test evaluation',flush=True);return
    validate_complete(root/'engineering')
    if not read(root/'engineering/validation.json')['passed']:raise ValueError('Engineering gate failed')
    for path in sorted((root/'prepared').glob('*.json')):
        if path.name=='complete.json':continue
        data=read(path);c=data['context'];labels=data['labels']
        for seed in cfg['seeds']:
            for arm in cfg['arms']:
                dest=root/'jobs'/f'{path.stem}-{seed}-{arm}'
                if dest.exists():validate_complete(dest);continue
                model,info,trace=train(data['train']['x'],data['targets'][arm],seed,cfg)
                fit_id=dest.name
                record={**c,'seed':seed,'arm':arm,'fit_id':fit_id,'labels':labels,
                    'train_ids':data['membership']['train_ids'],'preprocessing':data['preprocessing'],
                    'teacher_fit_ids':data['teacher_fit_ids'] if arm!='M0' else [],
                    'prepared_sha256':digest(path),**info}
                predictions=[]
                for part,stage in [('test','student'),('target','cross')]:
                    with torch.no_grad():p=torch.softmax(model(torch.tensor(data[part]['x'],dtype=torch.float64)),1).numpy()
                    for r,prob in zip(data[part]['rows'],p):
                        y=labels.index(r['label_id'])
                        predictions.append({**c,'seed':seed,'arm':arm,'fit_id':fit_id,'stage':stage,
                            **r,'protocol':c['protocol'],'evaluation_protocol':r['protocol'],'truth':y,
                            'probabilities':prob.tolist(),'loss_bits':float(-np.log2(max(prob[y],1e-12)))})
                dest.mkdir(parents=True);write_json(dest/'fit.json',record)
                write_table(dest/'trajectory.parquet',trace);write_table(dest/'predictions.parquet',predictions)
                seal(dest,passed=True,fresh_fits=1)
            print(json.dumps({'job':path.stem,'seed':seed,'completed_arms':4}),flush=True)
    jobs=list((root/'jobs').iterdir())
    if len(jobs)!=cfg['formal_fit_budget']:raise ValueError('Formal budget mismatch')
    write_json(root/'training-complete.json',{'formal_fits':len(jobs),'teacher_fits':0,'target_fits':0,
        'jobs':{j.name:digest(j/'complete.json') for j in sorted(jobs)}})
    print('Formal training complete: 800 fits',flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--config',default=str(CONFIG))
    p.add_argument('--mode',choices=['freeze','verify','smoke','run'],required=True);a=p.parse_args()
    if a.mode=='freeze':freeze(a.config)
    elif a.mode=='verify':verify(a.config)
    else:run(a.config,a.mode)
