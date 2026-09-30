"""Approved P1-P3 job runner; source-only fits and same-model target predictions."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import yaml

from .mechanism_contract import verify, cohort, read
from .business_representations import matrix, views, dictionary
from .business_splits import disjoint, teacher_assignment, donors
from .privileged_learning import LinearStudent
from ..paired_information.prepare import digest, table
from ..reproducibility.preflight import write_json, write_table


def array_digest(x):
    return hashlib.sha256(np.asarray(x,dtype='<f8').tobytes()).hexdigest()


def source_guard(train, test, target, protocol):
    disjoint(train,test)
    if any(r['protocol']!=protocol for r in train+test) or any(r['protocol']==protocol for r in target):
        raise ValueError('Target deployment entered source training or incorrect target')
    if {r['content_id'] for r in train}&{r['content_id'] for r in target}:
        raise ValueError('Target heldout content entered training')
    if {(r['content_id'],r['repetition']) for r in test}!={(r['content_id'],r['repetition']) for r in target}:
        raise ValueError('Source/target heldout content-round mismatch')


def verify_complete(directory):
    complete=read(directory/'complete.json')
    for name,expected in complete['artifacts'].items():
        if digest(directory/name)!=expected: raise ValueError('Completed job changed')
    return complete


def run_job(train, test, target, context, cfg, business, dest, historical):
    source_guard(train,test,target,context['protocol'])
    labels=sorted({r['label_id'] for r in train}); k=len(labels)
    hard=np.eye(k)[[labels.index(r['label_id']) for r in train]]
    representation=context['representation']
    xv, tv=views(train,representation), views(test,representation)
    # No target pre matrix is constructed. Target post is only transformed by fitted source models.
    target_post=matrix(target,'post',representation)
    fits=[]; predictions=[]; maps=[]; teacher_outputs=[]; splits=[]

    def fit(x,q,arm,member_rows,input_view,alpha=-1.,held=-1,donor_rows=None):
        if any(r['protocol']!=context['protocol'] for r in member_rows):
            raise ValueError('Non-source fit')
        model=LinearStudent(business).fit(x,q)
        fit_id=f'{dest.name}:{len(fits):03d}'
        fits.append({'fit_id':fit_id,**context,'arm':arm,'alpha':alpha,'held':held,
            'train_ids':[r['session_id'] for r in member_rows],'input_view':input_view,
            'donor_ids':[r['session_id'] for r in donor_rows] if donor_rows is not None else [],
            'labels':labels,'x_sha256':array_digest(x),'targets':q.tolist(),
            'weight_sum':float(q.sum()),'n_features':x.shape[1],'state':model.state(),
            'fresh_fit':True})
        return model,fit_id

    def record(model,fit_id,rows,x,arm,stage,alpha=-1.):
        p=model.predict(x)
        for row,prob in zip(rows,p):
            y=labels.index(row['label_id'])
            predictions.append({**context,'fit_id':fit_id,'arm':arm,'stage':stage,'alpha':alpha,
                'evaluation_protocol':row['protocol'],'session_id':row['session_id'],
                'content_id':row['content_id'],'label_id':row['label_id'],'truth':y,
                'probabilities':prob.tolist(),'loss_bits':float(-np.log2(max(prob[y],1e-12)))})
        if representation=='scalar14' and stage=='view' and arm in ('post','pre'):
            old_arm='M0' if arm=='post' else 'pre_teacher_diagnostic'
            for row,prob in zip(rows,p):
                old=historical[(context['task'],context['protocol'],context['outer_fold'],-1,old_arm,row['session_id'])]
                if np.max(np.abs(prob-np.asarray(old['probabilities'])))>cfg['probability_tolerance']:
                    raise ValueError('Historical view baseline not reproduced')
        if representation=='scalar14' and stage=='student' and alpha==.5 and arm in ('M1','M2','M3'):
            for row,prob in zip(rows,p):
                old=historical[(context['task'],context['protocol'],context['outer_fold'],0,arm,row['session_id'])]
                if np.max(np.abs(prob-np.asarray(old['probabilities'])))>cfg['probability_tolerance']:
                    raise ValueError('Historical student baseline not reproduced')

    for view in ('post','pre','joint','transformation'):
        model,fit_id=fit(xv[view],hard,view,train,view)
        record(model,fit_id,test,tv[view],view,'view')
        if view=='post':
            record(model,fit_id,test,tv['post'],'M0','student',0.)
            record(model,fit_id,target,target_post,'M0','cross',0.)
    partition=teacher_assignment(train,cfg['teacher_scheme'])
    cross=donors(train,partition)
    q={name:np.zeros_like(hard) for name in ('pre','post','J-True','J-Wrong')}
    for held in (0,1):
        tr=[i for i,r in enumerate(train) if partition[r['content_id']]!=held]
        va=[i for i,r in enumerate(train) if partition[r['content_id']]==held]
        a,b=[train[i] for i in tr],[train[i] for i in va]
        disjoint(a,b,test); disjoint(a,b,target)
        for teacher in q:
            if teacher in ('pre','post'):
                x,xt=xv[teacher][tr],xv[teacher][va]; donor_train=None
            else:
                perm=np.arange(len(train)) if teacher=='J-True' else cross
                x=np.concatenate([xv['pre'][perm[tr]],xv['post'][tr]],axis=1)
                xt=np.concatenate([xv['pre'][perm[va]],xv['post'][va]],axis=1)
                donor_train=[train[perm[i]] for i in tr]
            model,fit_id=fit(x,hard[tr],teacher+'_teacher',a,teacher,held=held,donor_rows=donor_train)
            q[teacher][va]=model.predict(xt)
            splits.append({'fit_id':fit_id,'held':held,'teacher':teacher,
                           'train_ids':[r['session_id'] for r in a],'holdout_ids':[r['session_id'] for r in b]})
            if teacher in ('J-True','J-Wrong'):
                for role,indices in (('train',tr),('holdout',va)):
                    for i in indices:
                        maps.append({'teacher_fit_id':fit_id,'arm':teacher,'role':role,'held':held,
                                     'receiver':train[i]['session_id'],'donor':train[perm[i]]['session_id']})
            for i in va:
                teacher_outputs.append({'fit_id':fit_id,'teacher':teacher,'session_id':train[i]['session_id'],
                    'probabilities':q[teacher][i].tolist(),'truth':labels.index(train[i]['label_id'])})
    for i,row in enumerate(train):
        maps.append({'teacher_fit_id':'pre_oof_by_holdout','arm':'M3','role':'student','held':partition[row['content_id']],
                     'receiver':row['session_id'],'donor':train[cross[i]]['session_id']})
    for arm,prob in [('M1',q['post']),('M2',q['pre']),('M3',q['pre'][cross]),
                     ('J-True',q['J-True']),('J-Wrong',q['J-Wrong'])]:
        for alpha in cfg['alphas']:
            model,fit_id=fit(xv['post'],(1-alpha)*hard+alpha*prob,arm,train,'post',alpha=alpha)
            record(model,fit_id,test,tv['post'],arm,'student',alpha)
            record(model,fit_id,target,target_post,arm,'cross',alpha)
    smoothing=cfg['label_smoothing']
    model,fit_id=fit(xv['post'],(1-smoothing)*hard+smoothing/k,'LS10',train,'post',alpha=smoothing)
    record(model,fit_id,test,tv['post'],'LS10','student',smoothing)
    record(model,fit_id,target,target_post,'LS10','cross',smoothing)
    write_json(dest/'fit-ledger.json',fits)
    write_json(dest/'teacher-splits.json',splits)
    write_table(dest/'predictions.parquet',predictions)
    write_table(dest/'pair-maps.parquet',maps)
    write_table(dest/'teacher-oof.parquet',teacher_outputs)
    write_json(dest/'membership.json',{'context':context,'train_ids':[r['session_id'] for r in train],
        'test_ids':[r['session_id'] for r in test],'target_ids':[r['session_id'] for r in target]})
    write_json(dest/'complete.json',{'fresh_fits':len(fits),'prediction_rows':len(predictions),
        'artifacts':{p.name:digest(p) for p in dest.iterdir() if p.is_file() and p.name!='failed.json'}})


def main():
    cfg,business,source,out=verify()
    sanity=verify_complete(out/'p0-diagnostics')
    if not sanity['passed']: raise ValueError('P0 gate missing')
    rows=cohort(source); assignment=read(source/'learning/outer-splits.json')
    feature_cfg=yaml.safe_load(Path(business['feature_config']).read_text(encoding='utf-8'))
    if (len(feature_cfg['histograms']['transport_payload_len_edges_bytes'])!=18 or
            len(feature_cfg['histograms']['iat_edges_us'])!=22): raise ValueError('Unexpected frozen bins')
    representations=out/'representations'; representations.mkdir(exist_ok=True)
    dictionary_path=representations/'representation-dictionary.json'
    if dictionary_path.exists() and read(dictionary_path)!=dictionary(): raise ValueError('Representation dictionary changed')
    write_json(dictionary_path,dictionary())
    for representation in cfg['representations']:
        feature_rows=[]
        for row in rows:
            v=views([row],representation)
            feature_rows.append({k:row[k] for k in ('session_id','content_id','label_id','protocol','repetition')}|
                {name:v[name][0].tolist() for name in ('pre','post','transformation')})
        write_table(representations/(representation+'.parquet'),feature_rows)
    historical={(r['task'],r['protocol'],r['outer_fold'],r['teacher_scheme'],r['arm'],r['session_id']):r
                for r in table(source/'learning/oof.parquet') if r['arm'] in ('M0','M1','M2','M3','pre_teacher_diagnostic')}
    jobs=out/'jobs'; jobs.mkdir(exist_ok=True); fit_count=sanity['fresh_fits']; manifest=[]
    for task in ('six_business','youtube_activity'):
        task_rows=[r for r in rows if task=='six_business' or r['label_id'].startswith('youtube.com::')]
        for protocol in business['protocols']:
            for fold in range(5):
                train=[r for r in task_rows if r['protocol']==protocol and assignment[r['content_id']]!=fold]
                test=[r for r in task_rows if r['protocol']==protocol and assignment[r['content_id']]==fold]
                target=[r for r in task_rows if r['protocol']!=protocol and assignment[r['content_id']]==fold]
                for representation in cfg['representations']:
                    name=f'{task}-{protocol}-{fold}-{representation}'
                    context={'task':task,'protocol':protocol,'outer_fold':fold,'representation':representation}
                    dest=jobs/name
                    if dest.exists():
                        if not (dest/'complete.json').exists():
                            raise ValueError(f'Incomplete job requires review: {dest}')
                        complete=verify_complete(dest); reused=True
                    else:
                        dest.mkdir()
                        try: run_job(train,test,target,context,cfg,business,dest,historical)
                        except Exception as exc:
                            write_json(dest/'failed.json',{'context':context,'error':repr(exc),'action':'stop_no_automatic_retuning'})
                            raise
                        complete=verify_complete(dest); reused=False
                    fit_count+=complete['fresh_fits']
                    if fit_count>cfg['fresh_fit_budget']: raise ValueError('Approved fit budget exceeded')
                    manifest.append({'job':name,**complete,'reused_complete_job':reused})
                    write_json(out/'job-progress.json',{'finished_jobs':len(manifest),'total_fits_including_P0':fit_count,'jobs':manifest})
                    print(json.dumps({'job':name,'completed':len(manifest),'total':40,'fits':fit_count,'reused':reused}),flush=True)
    write_json(out/'training-complete.json',{'jobs':40,'fits_including_P0':fit_count,
        'job_complete_hashes':{p.parent.name:digest(p) for p in jobs.glob('*/complete.json')}})


if __name__=='__main__': main()
