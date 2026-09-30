"""Independent NumPy prediction audit and content/seed-aware N1 comparisons."""
import argparse
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.special import softmax,logsumexp
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler

from .student_capacity import CONFIG,verify,array_hash,state_hash
from .paired_structure_contract import read,validate_complete,seal
from .business_representations import matrix
from .privileged_learning import scores
from .mechanism_report import clustered
from ..paired_information.prepare import table,digest
from ..reproducibility.preflight import write_json,write_table


def groups(rows,keys):
    out=defaultdict(list)
    for r in rows:out[tuple(r[k] for k in keys)].append(r)
    return sorted(out.items())


def logits_numpy(x,state):
    x=np.asarray(x);a=np.maximum(x@np.asarray(state['0.weight']).T+state['0.bias'],0)
    return a@np.asarray(state['2.weight']).T+state['2.bias']


def audit(config=CONFIG):
    cfg,source,legacy,root=verify(config);out=root/'report'
    if out.exists():validate_complete(out);return
    complete=read(root/'training-complete.json')
    if complete['formal_fits']!=800 or len(complete['jobs'])!=800:raise ValueError('Fit budget incomplete')
    data={p.stem:read(p) for p in (root/'prepared').glob('*.json') if p.name!='complete.json'}
    lookup={r['session_id']:r for r in table(source/'side-summaries.parquet') if r['selection']=='observed' and r['primary_candidate']}
    old_predictions=[]
    for name,d in data.items():
        old_predictions.extend(r for r in table(legacy/'jobs'/name/'predictions.parquet')
            if r['stage'] in ('student','cross') and (r['arm']=='M0' or (r['arm'] in ('M1','M2','M3') and r['alpha']==.5)))
        train=[lookup[s] for s in d['membership']['train_ids']];x=matrix(train,'post',d['context']['representation'])
        imp=SimpleImputer(strategy='median',keep_empty_features=True).fit(x);sc=StandardScaler().fit(imp.transform(x))
        for a,b in [(imp.statistics_,d['preprocessing']['imputer_statistics']),
                    (sc.mean_,d['preprocessing']['scaler_mean']),(sc.scale_,d['preprocessing']['scaler_scale'])]:
            if not np.allclose(a,b,atol=1e-12,rtol=0):raise ValueError('Preprocessing not source-only')
        for part in ['train','test','target']:
            rows=[lookup[s] for s in d['membership'][part+'_ids']]
            expected=sc.transform(imp.transform(matrix(rows,'post',d['context']['representation'])))
            if not np.allclose(expected,d[part]['x'],atol=1e-12,rtol=0):raise ValueError('Prepared matrix changed')
            if [r['session_id'] for r in d[part]['rows']]!=d['membership'][part+'_ids']:raise ValueError('Row ordering changed')
    allpred=[];fits=[];initials=defaultdict(set);seen=set();max_error=0.
    for name,h in complete['jobs'].items():
        job=root/'jobs'/name
        if digest(job/'complete.json')!=h:raise ValueError('Job completion hash changed')
        validate_complete(job);f=read(job/'fit.json')
        context={k:f[k] for k in ['task','protocol','outer_fold','representation']}
        source_name=f"{f['task']}-{f['protocol']}-{f['outer_fold']}-{f['representation']}"
        d=data[source_name];arm=f['arm'];seed=f['seed'];key=(source_name,seed,arm)
        if key in seen or seed not in cfg['seeds'] or arm not in cfg['arms']:raise ValueError('Unexpected job')
        seen.add(key)
        if f['prepared_sha256']!=digest(root/'prepared'/f'{source_name}.json'):raise ValueError('Prepared hash mismatch')
        if f['train_ids']!=d['membership']['train_ids'] or f['labels']!=d['labels']:raise ValueError('Fit membership changed')
        if f['preprocessing']!=d['preprocessing']:raise ValueError('Fit preprocessing changed')
        if f['x_sha256']!=array_hash(d['train']['x']) or f['targets_sha256']!=array_hash(d['targets'][arm]):raise ValueError('Training input or target changed')
        if f['initial_sha256']!=state_hash(f['initial_state']) or f['final_sha256']!=state_hash(f['final_state']):raise ValueError('State hash')
        initials[source_name,seed].add(f['initial_sha256'])
        trace=table(job/'trajectory.parquet')
        if len(trace)!=1000 or [r['step'] for r in trace]!=list(range(1000)):raise ValueError('Training budget changed')
        if not all(np.isfinite(r[k]) for r in trace for k in ['objective','soft_ce_nats','l2','gradient_inf']):raise ValueError('Nonfinite trajectory')
        z=logits_numpy(d['train']['x'],f['final_state']);lp=z-logsumexp(z,axis=1,keepdims=True)
        ce=float(-np.mean(np.sum(np.asarray(d['targets'][arm])*lp,axis=1)))
        reg=cfg['weight_l2']/2*sum(np.sum(np.asarray(v)**2) for k,v in f['final_state'].items() if k.endswith('weight'))
        if abs(ce+reg-f['final_objective'])>1e-10:raise ValueError('Objective reconstruction mismatch')
        train_truth=np.array([d['labels'].index(r['label_id']) for r in d['train']['rows']])
        fits.append({**context,'seed':seed,'arm':arm,'final_objective':f['final_objective'],
            'final_soft_ce_nats':ce,'target_l1':f['mean_target_probability_l1'],
            'train_hard_CE_bits':float(-lp[np.arange(len(z)),train_truth].mean()/np.log(2)),
            'train_accuracy':float(np.mean(z.argmax(1)==train_truth)),
            'last_gradient_inf':trace[-1]['gradient_inf'],'parameter_count':f['parameter_count']})
        predictions=table(job/'predictions.parquet')
        for stage,part in [('student','test'),('cross','target')]:
            rs=[r for r in predictions if r['stage']==stage];ids=d['membership'][part+'_ids']
            if len(rs)!=len(ids) or {r['session_id'] for r in rs}!=set(ids):raise ValueError('Test coverage')
            p=softmax(logits_numpy(d[part]['x'],f['final_state']),axis=1);byid={s:i for i,s in enumerate(ids)}
            for r in rs:
                if any(r[k]!=v for k,v in context.items()) or r['seed']!=seed or r['arm']!=arm or r['fit_id']!=name:
                    raise ValueError('Prediction context mismatch')
                original=lookup[r['session_id']];y=d['labels'].index(original['label_id'])
                if r['truth']!=y or r['content_id']!=original['content_id'] or r['evaluation_protocol']!=original['protocol']:
                    raise ValueError('Prediction label mismatch')
                prob=p[byid[r['session_id']]];error=float(max(abs(prob-r['probabilities'])));max_error=max(max_error,error)
                if error>1e-10 or abs(-np.log2(max(prob[y],1e-12))-r['loss_bits'])>1e-9:raise ValueError('Prediction mismatch')
        allpred.extend(predictions)
    expected={(name,s,a) for name in data for s in cfg['seeds'] for a in cfg['arms']}
    if seen!=expected or any(len(v)!=1 for v in initials.values()):raise ValueError('Arm coverage or shared initialization failed')
    metrics=[];keys=['task','protocol','representation','stage','seed','arm']
    for key,rs in groups(allpred,keys):
        metrics.append({**dict(zip(keys,key)),**scores([r['truth'] for r in rs],[r['probabilities'] for r in rs]),
            'predicted_class_count':len({int(np.argmax(r['probabilities'])) for r in rs})})
    summary=[]
    for key,rs in groups(metrics,[k for k in keys if k!='seed']):
        outrow=dict(zip([k for k in keys if k!='seed'],key))
        for m in ['log_loss_bits','macro_f1','balanced_accuracy','brier_multiclass']:
            v=[r[m] for r in rs];outrow.update({m+'_mean':float(np.mean(v)),m+'_min':float(min(v)),m+'_max':float(max(v))})
        summary.append(outrow)
    gains=[];effects=[];seed_gains=[];interactions=[];context_keys=['task','protocol','representation','stage']
    old={(r['task'],r['protocol'],r['representation'],r['stage'],r['arm'],r['session_id']):r['loss_bits'] for r in old_predictions}
    for key,rs in groups(allpred,context_keys):
        index={(r['seed'],r['arm'],r['session_id']):r for r in rs}
        true=[r for r in rs if r['arm']=='M2']
        for comparison,ref in [('G_task','M0'),('G_pair','M3'),('G_soft','M1')]:
            values=[];interaction=[]
            for r in true:
                gain=index[r['seed'],ref,r['session_id']]['loss_bits']-r['loss_bits']
                values.append((r['label_id'],r['content_id'],gain))
                lr=old[(*key,ref,r['session_id'])]-old[(*key,'M2',r['session_id'])]
                interaction.append((r['label_id'],r['content_id'],gain-lr))
            g,cr=clustered(values,cfg);gains.append({**dict(zip(context_keys,key)),'comparison':comparison,**g})
            effects.extend({**dict(zip(context_keys,key)),'comparison':comparison,**r} for r in cr)
            g,_=clustered(interaction,cfg);interactions.append({**dict(zip(context_keys,key)),'comparison':comparison,**g})
            for seed in cfg['seeds']:
                v=[(r['label_id'],r['content_id'],index[seed,ref,r['session_id']]['loss_bits']-r['loss_bits']) for r in true if r['seed']==seed]
                g,_=clustered(v,cfg);seed_gains.append({**dict(zip(context_keys,key)),'comparison':comparison,'seed':seed,**g})
    out.mkdir();write_json(out/'metrics-per-seed.json',metrics);write_json(out/'metrics-summary.json',summary)
    write_json(out/'gains-seed-average.json',gains);write_json(out/'gains-per-seed.json',seed_gains)
    write_json(out/'model-family-interaction.json',interactions);write_table(out/'content-effects.parquet',effects)
    write_table(out/'training-diagnostics.parquet',fits)
    write_json(out/'validation.json',{'passed':True,'audited_fits':len(fits),'prediction_rows':len(allpred),
        'max_probability_error':max_error,'shared_initializations':len(initials),'target_fits':0,'new_teacher_fits':0,
        'early_stopping':False,'interval_scope':'content bootstrap conditional on all five fitted seeds; no probability ensembling',
        'audit_code_sha256':digest(Path(__file__))})
    seal(out,passed=True);print({'audit_passed':True,'fits':len(fits),'predictions':len(allpred),'max_error':max_error},flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--config',default=str(CONFIG));audit(p.parse_args().config)
