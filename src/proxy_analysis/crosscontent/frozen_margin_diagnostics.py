"""P6 reconstructs saved models, never fits or chooses features."""
import argparse
from pathlib import Path

import numpy as np
from scipy.special import softmax

from .paired_structure_contract import CONFIG, verify, seal, validate_complete, read
from .business_representations import matrix, dictionary
from .count_decomposition import grouped
from ..paired_information.prepare import table, digest
from ..reproducibility.preflight import write_json, write_table

FAMILIES={'scalar':slice(0,14),'length':slice(14,33),'IAT':slice(33,56),'curve':slice(56,157)}


def transformed(x,state):
    x=np.asarray(x,dtype=float)
    return (np.where(np.isnan(x),np.asarray(state['imputer_statistics']),x)
            -np.asarray(state['scaler_mean']))/np.asarray(state['scaler_scale'])


def coefficients(state):
    w=np.asarray(state['coef']); intercept=np.asarray(state['intercept'])
    if len(w)==1: return np.vstack([-w/2,w/2]),np.r_[-intercept/2,intercept/2]
    return w,intercept


def contributions(z,w,intercept,y,c):
    diff=(w[y]-w[c])*z
    result={name:float(diff[s].sum()) for name,s in FAMILIES.items() if s.start<len(z)}
    result['intercept']=float(intercept[y]-intercept[c])
    margin=float((w[y]-w[c])@z+intercept[y]-intercept[c])
    if not np.isclose(sum(result.values()),margin,atol=1e-9): raise ValueError('Margin failed')
    return result,margin,diff


def run(config=CONFIG):
    cfg,source,legacy,root=verify(config); out=root/'p6-diagnostics'
    if out.exists(): validate_complete(out); return
    rows={r['session_id']:r for r in table(source/'side-summaries.parquet') if r['selection']=='observed'}
    margins=[]; shifts=[]; matched=[]; transitions=[]; details=[]; max_error=0.; model_count=0
    for job in sorted((legacy/'jobs').iterdir()):
        validate_complete(job); member=read(job/'membership.json'); context=member['context']
        fit=next(f for f in read(job/'fit-ledger.json') if f['arm']=='post')
        state=fit['state']; w,intercept=coefficients(state); rep=context['representation']
        names=dictionary()[rep]; pred=table(job/'predictions.parquet')
        train=[rows[s] for s in member['train_ids']]
        if set(member['train_ids']) & set(member['test_ids']+member['target_ids']): raise ValueError('Session overlap')
        if {r['content_id'] for r in train} & {rows[s]['content_id'] for s in member['test_ids']+member['target_ids']}:
            raise ValueError('Content overlap')
        source_protocol=context['protocol']
        if any(r['protocol']!=source_protocol for r in train): raise ValueError('Non-source training')
        train_x=matrix(train,'post',rep)
        imp=np.where(np.isnan(train_x),state['imputer_statistics'],train_x)
        variance=imp.var(axis=0)
        zsets={'train':transformed(train_x,state)}
        predictions={}; metadata={}; z_by={}
        for stage,ids in [('student',member['test_ids']),('cross',member['target_ids'])]:
            rs=[rows[s] for s in ids]; z=transformed(matrix(rs,'post',rep),state)
            probs=softmax(z@w.T+intercept,axis=1);zsets[stage]=z
            saved={p['session_id']:p for p in pred if p['arm']=='M0' and p['stage']==stage}
            m2={p['session_id']:p for p in pred if p['arm']=='M2' and p['stage']==stage and p['alpha']==.5}
            if set(saved)!=set(ids): raise ValueError('Prediction membership mismatch')
            for i,r in enumerate(rs):
                sid=r['session_id']; old=saved[sid]; p=probs[i]
                if old['fit_id']!=fit['fit_id']: raise ValueError('Different evaluation model')
                error=float(np.max(np.abs(p-np.asarray(old['probabilities']))));max_error=max(max_error,error)
                if error>cfg['probability_reconstruction_tolerance']: raise ValueError('Probability reconstruction failed')
                y=old['truth']; winner=int(p.argmax()); c=int(np.argmax(np.where(np.arange(len(p))==y,-1,p)))
                parts,margin,dim=contributions(z[i],w,intercept,y,c)
                meta={**context,'fit_id':fit['fit_id'],'stage':stage,'session_id':sid,
                    'content_id':r['content_id'],'label_id':r['label_id'],'repetition':r['repetition']}
                margins.append({**meta,'truth':y,'predicted':winner,'competitor':c,'margin':margin,
                    'correct':winner==y,'confidence':float(max(p)),'true_probability':float(p[y]),
                    'loss_bits':float(-np.log2(max(p[y],1e-12))),
                    'worst_family':min((k for k in parts if k!='intercept'),key=parts.get),**parts})
                for j,name in enumerate(names):
                    details.append({**meta,'feature':name,'z':float(z[i,j]),'margin_contribution':float(dim[j])})
                q=np.asarray(m2[sid]['probabilities']); qwin=int(q.argmax())
                transitions.append({**meta,'M0_correct':winner==y,'M2_correct':qwin==y,
                    'same_label':winner==qwin,'M0_confidence':float(max(p)),'M2_confidence':float(max(q)),
                    'M0_loss_bits':old['loss_bits'],'M2_loss_bits':m2[sid]['loss_bits'],
                    'CE_advantage':old['loss_bits']-m2[sid]['loss_bits']})
                key=(r['content_id'],r['repetition']); z_by[stage,key]=z[i]; metadata[stage,key]=(meta,y,c)
        for key in [k[1] for k in z_by if k[0]=='cross']:
            meta,y,c=metadata['cross',key]
            a,am,_=contributions(z_by['student',key],w,intercept,y,c)
            b,bm,_=contributions(z_by['cross',key],w,intercept,y,c)
            matched.append({**meta,'competitor_fixed_to_target':c,'source_margin':am,'target_margin':bm,
                'margin_shift':bm-am,**{f'{k}_shift':b[k]-a[k] for k in a}})
        for stage,z in zsets.items():
            for j,name in enumerate(names):
                x=np.abs(z[:,j]);shifts.append({**context,'fit_id':fit['fit_id'],'stage':stage,'feature':name,
                    'source_variance':float(variance[j]),'source_scale':state['scaler_scale'][j],
                    'source_zero_variance':bool(variance[j]==0),'mean_z':float(z[:,j].mean()),
                    'abs_z_p50':float(np.median(x)),'abs_z_p95':float(np.quantile(x,.95)),
                    'abs_z_max':float(max(x)),**{f'fraction_gt_{t}':float(np.mean(x>t)) for t in (3,5,10)}})
        model_count+=1
    summary=[]
    keys=['task','protocol','representation','stage']
    for key,rs in grouped(margins,keys):
        errors=[r for r in rs if not r['correct']]
        content_means=[np.mean([r['loss_bits'] for r in group]) for _,group in grouped(rs,['content_id'])]
        family_counts={family:sum(r['worst_family']==family for r in errors) for family in FAMILIES}
        summary.append({**dict(zip(keys,key)),'n':len(rs),'errors':len(errors),
            'content_equal_CE':float(np.mean(content_means)),
            'error_confidence':float(np.mean([r['confidence'] for r in errors])) if errors else None,
            'error_worst_family_counts':family_counts})
    out.mkdir()
    for name,data in [('margin-contributions',margins),('matched-margin-shifts',matched),
                      ('standardized-shifts',shifts),('confidence-transitions',transitions),('dimension-contributions',details)]:
        write_table(out/f'{name}.parquet',data)
    write_json(out/'group-summary.json',summary)
    write_json(out/'prediction-reconstruction.json',{'passed':True,'models':model_count,
        'predictions':len(margins),'max_probability_error':max_error,'new_fits':0,
        'target_fits':0,'code_sha256':digest(Path(__file__))})
    seal(out,passed=True);print({'P6':'passed','models':model_count,'max_probability_error':max_error},flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--config',default=str(CONFIG));run(p.parse_args().config)
