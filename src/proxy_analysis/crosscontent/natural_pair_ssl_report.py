"""Independent NumPy prediction replay and content-clustered SSL evaluation."""
from collections import defaultdict
from pathlib import Path
import argparse
import json

import numpy as np
from sklearn.metrics import f1_score, balanced_accuracy_score

from .natural_pair_ssl import CONFIG, verify
from .mechanism_contract import read
from .paired_structure_contract import validate_complete, seal
from ..paired_information.prepare import table
from ..reproducibility.preflight import write_json, write_table


def mlp(x,state,prefix=''):
    a=np.maximum(0,np.asarray(x)@np.asarray(state[prefix+'0.weight']).T+state[prefix+'0.bias'])
    return a@np.asarray(state[prefix+'2.weight']).T+state[prefix+'2.bias']


def softmax(z):
    z=z-z.max(1,keepdims=True);p=np.exp(z);return p/p.sum(1,keepdims=True)


def metrics(rows):
    p=np.asarray([r['probabilities'] for r in rows]);k=p.shape[1]
    y=np.asarray([r['labels'].index(r['label_id']) for r in rows]);pred=p.argmax(1)
    return {'ce_bits':float(-np.log2(np.maximum(p[np.arange(len(y)),y],1e-15)).mean()),
        'macro_f1':float(f1_score(y,pred,labels=list(range(k)),average='macro',zero_division=0)),
        'balanced_accuracy':float(balanced_accuracy_score(y,pred)),
        'brier':float(((p-np.eye(k)[y])**2).sum(1).mean()),'visits':len(rows)}


def f1_from_counts(c):
    # c: bootstrap x seed x true-class x predicted-class.
    diag=np.diagonal(c,axis1=-2,axis2=-1)
    denom=c.sum(-1)+c.sum(-2)
    scores=np.divide(2*diag,denom,out=np.zeros_like(diag,dtype=float),where=denom>0)
    return scores.mean(-1).mean(-1)


def compare(a,b,repetitions,seeds):
    """B3 minus control F1; control minus B3 CE; paired content resampling."""
    ids=sorted({r['content_id'] for r in a});index={c:i for i,c in enumerate(ids)}
    k=len(a[0]['labels']);n=len(ids)
    def tensors(rows):
        counts=np.zeros((n,len(seeds),k,k));ce=np.zeros((n,len(seeds)));den=np.zeros_like(ce)
        for r in rows:
            i=index[r['content_id']];s=seeds.index(r['seed']);y=r['labels'].index(r['label_id']);p=r['probabilities']
            counts[i,s,y,np.argmax(p)]+=1;ce[i,s]+=-np.log2(max(p[y],1e-15));den[i,s]+=1
        if (den==0).any():raise ValueError('Incomplete content/seed coverage')
        return counts,ce/den
    ac,ae=tensors(a);bc,be=tensors(b)
    classes=defaultdict(list)
    for r in a:classes[r['label_id']].append(index[r['content_id']])
    classes=[sorted(set(v)) for v in classes.values()]
    rng=np.random.default_rng(20260918)
    draws=np.concatenate([rng.choice(v,size=(repetitions,len(v)),replace=True) for v in classes],axis=1)
    w=np.zeros((repetitions,n),dtype=float)
    for j in range(n):w[:,j]=(draws==j).sum(1)
    af=f1_from_counts(np.einsum('bn,nskl->bskl',w,ac));bf=f1_from_counts(np.einsum('bn,nskl->bskl',w,bc))
    ce=w@(be-ae).mean(1)/n
    point_f=float(f1_from_counts(ac.sum(0)[None])-f1_from_counts(bc.sum(0)[None]))
    return {'f1_gain':point_f,'f1_ci':np.quantile(af-bf,[.025,.975]).tolist(),
        'ce_gain_bits':float((be-ae).mean()),'ce_ci':np.quantile(ce,[.025,.975]).tolist(),
        'independent_contents':n,'bootstrap_repetitions':repetitions,
        'multiplicity':'unadjusted descriptive intervals, not confirmatory tests'}


def report(config=CONFIG):
    cfg,_,root=verify(config);jobs=sorted((root/'jobs').iterdir())
    if len(jobs)!=150:raise ValueError('Expected 150 completed arm/context/seed jobs')
    predictions=[];stages=0;worst=0.;diagnostics=[]
    for job in jobs:
        validate_complete(job);mem=read(job/'membership.json');data=read(root/'prepared'/f'{mem["context"]}.json')
        if set(mem['train_ids'])&set(mem['test_ids']):raise ValueError('Membership overlap')
        rows=table(job/'predictions.parquet');stages+=mem['stages'];x=np.asarray(data['test_post'])
        fit=read(job/'finetune-fit.json');h=mlp(x,fit['final'],'0.')
        p=softmax(h@np.asarray(fit['final']['1.weight']).T+fit['final']['1.bias'])
        replay={'finetune':p}
        if mem['arm']!='B0':
            fit=read(job/'probe-fit.json');h=(mlp(x,fit['encoder'])-fit['mean'])/fit['scale']
            z=h@np.asarray(fit['coef']).T+fit['intercept']
            replay['probe']=softmax(np.concatenate([np.zeros_like(z),z],1) if z.shape[1]==1 else z)
            ssl=read(job/'ssl-fit.json')
            diagnostics.append({'context':mem['context'],'seed':mem['seed'],'arm':mem['arm'],
                **ssl['encoder_diagnostics'],'projection_mean_std':ssl['projection_diagnostics']['mean_std']})
        for stage,p in replay.items():
            rr=[r for r in rows if r['stage']==stage]
            if [r['session_id'] for r in rr]!=mem['test_ids']:raise ValueError('Prediction membership differs')
            worst=max(worst,float(abs(p-np.asarray([r['probabilities'] for r in rr])).max()))
        predictions.extend(rows)
    if stages!=390 or worst>1e-10:raise ValueError('Budget or independent replay failed')
    out=root/'report';write_table(out/'predictions.parquet',predictions)
    write_json(out/'representation-diagnostics.json',diagnostics)
    groups=defaultdict(list)
    for r in predictions:
        for protocol in [r['protocol'],'pooled']:
            groups[r['task'],r['stage'],protocol,r['arm'],r['seed']].append(r)
    result=[];summaries=defaultdict(list)
    for key,rr in sorted(groups.items()):
        if len({r['session_id'] for r in rr})!=len(rr):raise ValueError('Duplicate visits across folds')
        task,stage,protocol,arm,seed=key
        value={'task':task,'stage':stage,'protocol':protocol,'arm':arm,'seed':seed,**metrics(rr)}
        result.append(value);summaries[key[:-1]].append(value)
    summary=[]
    for key,rr in sorted(summaries.items()):
        task,stage,protocol,arm=key
        s={'task':task,'stage':stage,'protocol':protocol,'arm':arm}
        for m in ['ce_bits','macro_f1','balanced_accuracy','brier']:
            v=[r[m] for r in rr];s[m]=float(np.mean(v));s[m+'_range']=[min(v),max(v)]
        summary.append(s)
    gains=[]
    for task in cfg['tasks']:
        for stage in ['probe','finetune']:
            for protocol in ['SHADOWSOCKS','VLESS','pooled']:
                def pick(arm):
                    return [r for seed in cfg['seeds'] for r in groups[task,stage,protocol,arm,seed]]
                for control in (['B0'] if stage=='finetune' else [])+['B1','B2','B4']:
                    gains.append({'task':task,'stage':stage,'protocol':protocol,'control':control,
                        **compare(pick('B3'),pick(control),cfg['bootstrap_repetitions'],cfg['seeds'])})
    write_json(out/'metrics-per-seed.json',result);write_json(out/'metrics-summary.json',summary)
    write_json(out/'paired-gains.json',gains)
    write_json(out/'validation.json',{'passed':True,'jobs':150,'training_stages':stages,
        'predictions':len(predictions),'max_independent_probability_error':worst,
        'scope':cfg['observation_scope'],'interval_scope':'conditional on fitted models, content resampling',
        'external_validation':False})
    seal(out,passed=True)
    print(json.dumps({'passed':True,'stages':stages,'max_replay_error':worst}),flush=True)
    for r in summary:
        if r['protocol']=='pooled':print(json.dumps(r),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--config',default=str(CONFIG));args=parser.parse_args()
    report(args.config)
