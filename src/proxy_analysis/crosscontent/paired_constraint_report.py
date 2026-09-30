"""Independent P7 matrix, objective, membership and prediction replay audit."""
import argparse
from collections import defaultdict
from pathlib import Path
import numpy as np
from scipy.special import expit,softmax,logsumexp
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler

from .paired_structure_contract import CONFIG,verify,read,validate_complete,seal
from .business_representations import matrix
from .privileged_learning import scores
from .mechanism_report import clustered
from ..paired_information.prepare import digest,table
from ..reproducibility.preflight import write_json,write_table


def groups(rows,keys):
    out=defaultdict(list)
    for r in rows:out[tuple(r[k] for k in keys)].append(r)
    return sorted(out.items())


def predict(x,state):
    z=x@np.asarray(state['coef']).T+state['intercept']
    if z.shape[1]==1:
        p=expit(z[:,0]);return np.column_stack([1-p,p])
    return softmax(z,axis=1)


def audit(config=CONFIG):
    cfg,source,legacy,root=verify(config);base=root/'p7-models';out=base/'report'
    if out.exists():validate_complete(out);return
    validate_complete(base/'formal-contract');complete=read(base/'formal-complete.json')
    for path,h in read(base/'formal-contract/implementation.json')['sources'].items():
        if digest(Path(path))!=h:raise ValueError('Formal implementation drift')
    rows={r['session_id']:r for r in table(source/'side-summaries.parquet') if r['selection']=='observed' and r['primary_candidate']}
    assignment=read(source/'learning/outer-splits.json');predictions=[];fitrows=[];old_difference=[];matrix_stats=[]
    max_probability_error=0.;audited_fits=0;map_count=0
    expected_specs={('R0',0.)}|{(arm,float(lam)) for lam in cfg['lambdas'] for arm in ['R-True','R-Wrong-1','R-Wrong-2','R-Wrong-3','R-Iso']}
    if complete['formal_fits']!=320 or len(complete['jobs'])!=20:raise ValueError('Incomplete formal budget')
    for name,h in complete['jobs'].items():
        job=base/'formal-jobs'/name
        if digest(job/'complete.json')!=h:raise ValueError('Job digest mismatch')
        validate_complete(job);member=read(job/'membership.json');fits=read(job/'fit-ledger.json');c=fits[0]
        task,protocol,fold=c['task'],c['protocol'],c['outer_fold'];labels=fits[0]['labels'];context={k:c[k] for k in ['task','protocol','outer_fold','representation']}
        eligible=[r for r in rows.values() if task=='six_business' or r['label_id'].startswith('youtube.com::')]
        expected={'train':{r['session_id'] for r in eligible if r['protocol']==protocol and assignment[r['content_id']]!=fold},
            'test':{r['session_id'] for r in eligible if r['protocol']==protocol and assignment[r['content_id']]==fold},
            'target':{r['session_id'] for r in eligible if r['protocol']!=protocol and assignment[r['content_id']]==fold}}
        for part,ids in expected.items():
            if len(member[part+'_ids'])!=len(ids) or set(member[part+'_ids'])!=ids:raise ValueError('Membership drift')
        train=[rows[s] for s in member['train_ids']];raw=matrix(train,'post','scalar14')
        imp=SimpleImputer(strategy='median',keep_empty_features=True).fit(raw);sc=StandardScaler().fit(imp.transform(raw))
        x=sc.transform(imp.transform(raw));a=sc.transform(imp.transform(matrix(train,'pre','scalar14')))
        y=np.asarray([labels.index(r['label_id']) for r in train]);n=len(y);index={s:i for i,s in enumerate(member['train_ids'])}
        maps=table(job/'donor-maps.parquet');matrices=read(job/'matrices.json');covs={'R0':np.zeros((14,14)),'R-Iso':np.eye(14)}
        if set(m['arm'] for m in maps)!={'R-True','R-Wrong-1','R-Wrong-2','R-Wrong-3'}:raise ValueError('Donor arms')
        for arm in ['R-True','R-Wrong-1','R-Wrong-2','R-Wrong-3']:
            ms=[m for m in maps if m['arm']==arm]
            if len(ms)!=n or {m['receiver'] for m in ms}!=expected['train'] or {m['donor'] for m in ms}!=expected['train']:
                raise ValueError('Donor bijection failed')
            mapping={m['receiver']:m['donor'] for m in ms};diff=[]
            for receiver in member['train_ids']:
                donor=mapping[receiver];r,s=rows[receiver],rows[donor]
                if (r['label_id'],r['protocol'],r['repetition'])!=(s['label_id'],s['protocol'],s['repetition']):raise ValueError('Donor strata failed')
                contents=sorted({t['content_id'] for t in train if t['label_id']==r['label_id']})
                shift=0 if arm=='R-True' else int(arm[-1]);wanted=contents[(contents.index(r['content_id'])+shift)%4]
                if s['content_id']!=wanted:raise ValueError('Donor shift failed')
                diff.append(x[index[receiver]]-a[index[donor]])
            d=np.array(diff);rawcov=sum(np.outer(v,v) for v in d)/n;tr=np.trace(rawcov)
            cov=rawcov/(tr/14) if tr>0 else rawcov
            if not np.allclose(rawcov,matrices[arm]['raw'],atol=1e-10,rtol=1e-12) or not np.allclose(cov,matrices[arm]['normalized'],atol=1e-12,rtol=1e-12):raise ValueError('Matrix reconstruction')
            covs[arm]=cov;matrix_stats.append({**context,'arm':arm,'raw_trace':float(tr),
                'normalized_trace':float(np.trace(cov)),'rank':int(np.linalg.matrix_rank(rawcov)),
                'mean_delta_norm':float(np.linalg.norm(d.mean(0)))})
        map_count+=len(maps)
        if len(fits)!=16 or {(f['arm'],f['lambda']) for f in fits}!=expected_specs:raise ValueError('Arm coverage')
        ps=table(job/'predictions.parquet');expected_prediction_count=16*(len(expected['test'])+len(expected['target']))
        if len(ps)!=expected_prediction_count:raise ValueError('Prediction count')
        for f in fits:
            if any(f[k]!=v for k,v in context.items()) or f['train_ids']!=member['train_ids'] or f['y']!=y.tolist():raise ValueError('Fit context')
            for k,v in [('imputer_statistics',imp.statistics_),('scaler_mean',sc.mean_),('scaler_scale',sc.scale_)]:
                if not np.allclose(f['preprocessing'][k],v,atol=1e-12,rtol=0):raise ValueError('Non-source preprocessing')
            state=f['state'];w=np.array(state['coef']);b=np.array(state['intercept']);z=x@w.T+b
            centered=w/np.sqrt(2) if len(w)==1 else w-w.mean(0)
            cov=covs[f['arm']];pair=float(np.sum(centered@cov*centered))
            ce=float(np.mean(np.logaddexp(0,z[:,0])-y*z[:,0])) if len(w)==1 else float(np.mean(logsumexp(z,axis=1)-z[np.arange(n),y]))
            l2=float(np.sum(w*w)/(2*n*cfg['model_C']));value=ce+f['lambda']*pair+l2
            if abs(value-state['objective'])>1e-10 or not state['success'] or state['gradient_inf']>1e-6:raise ValueError('Objective/convergence failed')
            fitrows.append({**context,'arm':f['arm'],'lambda':f['lambda'],'objective':value,'training_ce_nats':ce,
                'l2':l2,'penalty':pair,'true_pair_penalty':f['true_normalized_pair_penalty'],
                'training_accuracy':f['training_accuracy'],'weight_norm_squared':f['weight_norm_squared'],
                'gradient_inf':state['gradient_inf'],'iterations':state['iterations']})
            for part,stage in [('test','student'),('target','cross')]:
                ids=member[part+'_ids'];xx=sc.transform(imp.transform(matrix([rows[s] for s in ids],'post','scalar14')))
                probs=predict(xx,state);local=[r for r in ps if r['fit_id']==f['fit_id'] and r['stage']==stage]
                if len(local)!=len(ids) or {r['session_id'] for r in local}!=set(ids):raise ValueError('Model reused/coverage')
                lp={r['session_id']:r for r in local}
                for sid,p in zip(ids,probs):
                    r=lp[sid];ytest=labels.index(rows[sid]['label_id']);error=float(max(abs(p-r['probabilities'])))
                    max_probability_error=max(max_probability_error,error)
                    if error>1e-10 or r['truth']!=ytest or r['content_id']!=rows[sid]['content_id'] or r['arm']!=f['arm'] or r['lambda']!=f['lambda']:raise ValueError('Prediction replay failed')
                    if abs(r['loss_bits']+np.log2(max(p[ytest],1e-12)))>1e-9:raise ValueError('Loss replay failed')
            audited_fits+=1
        old=table(legacy/'jobs'/f'{name}-scalar14'/'predictions.parquet')
        previous={(r['stage'],r['session_id']):r for r in old if r['arm']=='M0'}
        for r in ps:
            if r['arm']=='R0':
                p=previous[r['stage'],r['session_id']]
                old_difference.append({**context,'stage':r['stage'],'session_id':r['session_id'],
                    'probability_max_difference':float(max(abs(np.array(r['probabilities'])-p['probabilities']))),
                    'label_changed':bool(np.argmax(r['probabilities'])!=np.argmax(p['probabilities'])),
                    'old_loss_bits':p['loss_bits'],'new_loss_bits':r['loss_bits']})
        predictions.extend(ps)
    metrics=[];keys=['task','protocol','stage','arm','lambda']
    for key,rs in groups(predictions,keys):metrics.append({**dict(zip(keys,key)),**scores([r['truth'] for r in rs],[r['probabilities'] for r in rs])})
    gains=[];effects=[];keys=['task','protocol','stage']
    for key,rs in groups(predictions,keys):
        idx={(r['arm'],r['lambda'],r['session_id']):r for r in rs}
        for lam in cfg['lambdas']:
            true=[r for r in rs if r['arm']=='R-True' and r['lambda']==lam]
            for comp in ['G_task','G_pair','G_reg']:
                vals=[]
                for r in true:
                    sid=r['session_id']
                    ref=(idx['R0',0.,sid]['loss_bits'] if comp=='G_task' else idx['R-Iso',lam,sid]['loss_bits'] if comp=='G_reg'
                         else np.mean([idx[f'R-Wrong-{s}',lam,sid]['loss_bits'] for s in (1,2,3)]))
                    vals.append((r['label_id'],r['content_id'],ref-r['loss_bits']))
                g,cs=clustered(vals,cfg);v=np.array([c['advantage_bits'] for c in cs]);loco=(v.sum()-v)/(len(v)-1)
                gains.append({**dict(zip(keys,key)),'lambda':lam,'comparison':comp,**g,
                    'leave_one_content_out_min':float(loco.min()),'leave_one_content_out_max':float(loco.max())})
                effects.extend({**dict(zip(keys,key)),'lambda':lam,'comparison':comp,**c} for c in cs)
    out.mkdir();write_json(out/'metrics.json',metrics);write_json(out/'gains.json',gains)
    write_table(out/'content-effects.parquet',effects);write_table(out/'optimization-diagnostics.parquet',fitrows)
    write_table(out/'baseline-history-difference.parquet',old_difference);write_table(out/'matrix-diagnostics.parquet',matrix_stats)
    write_json(out/'validation.json',{'passed':True,'formal_fits':audited_fits,'prior_engineering_fits':8,
        'prediction_rows':len(predictions),'donor_rows':map_count,'max_probability_error':max_probability_error,
        'target_fits':0,'code_sha256':digest(Path(__file__))})
    seal(out,passed=True);print({'P7_audit_passed':True,'formal_fits':audited_fits,'predictions':len(predictions)},flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--config',default=str(CONFIG));audit(p.parse_args().config)
