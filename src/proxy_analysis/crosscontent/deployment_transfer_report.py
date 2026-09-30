"""Same-visit method contrasts and different-visit matched-content domain shifts."""
import argparse
from collections import defaultdict
import numpy as np
from sklearn.metrics import precision_recall_fscore_support,confusion_matrix
from .deployment_transfer_contract import CONFIG,verify,contexts
from .source_transfer_report import scores,contrast,count_scores
from .group_anchor_diagnostics_report import cluster_weights
from .natural_pair_ssl_report import metrics
from .decision_calibration_report import physical
from .source_transfer_coordinates import scale_selected
from .mechanism_contract import read
from .paired_structure_contract import seal,validate_complete
from ..paired_information.prepare import table
from ..reproducibility.preflight import write_json,write_table


def domain_contrast(target,source,cfg):
    ids=sorted({r['content_id'] for r in target});labels={r['content_id']:r['label_id'] for r in target}
    if set(ids)!={r['content_id'] for r in source}:raise ValueError('Content mismatch')
    if {r['session_id'] for r in target}&{r['session_id'] for r in source}:raise ValueError('Different deployments require distinct visits')
    def tensors(rr):
        c=np.zeros((len(ids),6,6));loss=np.zeros((len(ids),2));n=np.zeros(len(ids))
        for r in rr:
            i=ids.index(r['content_id']);s=scores(r);c[i,s['true_class'],s['prediction']]+=1;loss[i]+=[s['ce'],s['brier']];n[i]+=1
        if not np.all(n==4):raise ValueError('Expected four visits per content')
        return c,loss/n[:,None]
    tc,tl=tensors(target);sc,sl=tensors(source);weights=cluster_weights(ids,labels,cfg['bootstrap_repetitions'],cfg['bootstrap_seed'])
    tf,tba=count_scores(np.einsum('bn,njk->bjk',weights,tc));sf,sba=count_scores(np.einsum('bn,njk->bjk',weights,sc))
    boot={'macro_f1':tf-sf,'balanced_accuracy':tba-sba,'ce_bits':weights@(sl[:,0]-tl[:,0]),'brier':weights@(sl[:,1]-tl[:,1])}
    tm,sm=metrics(target),metrics(source);result={'independent_contents':len(ids),'pairing':'same content, different captured visits'}
    for k,v in boot.items():
        result[k+'_gain']=(tm[k]-sm[k])*(-1 if k in ('ce_bits','brier') else 1);result[k+'_ci']=np.quantile(v,[.025,.975]).tolist()
    return result


def report(config=CONFIG):
    cfg,root=verify(config);validate_complete(root/'inference');out=root/'report'
    if out.exists():raise FileExistsError(out)
    meta={(key,domain,r['session_id']):r for _,_,key in contexts(cfg) for domain in ('source','target') for r in read(root/'evaluation'/f'{key}-{domain}.json')['rows']}
    rows=[{**r,**meta[r['context'],r['domain'],r['session_id']]} for r in table(root/'inference/predictions.parquet')]
    by=defaultdict(list);fb=defaultdict(list);idx={}
    for r in rows:
        key=(r['source_protocol'],r['domain'],r['arm']);by[key].append(r);fb[(*key,r['fold'])].append(r)
        k=(r['context'],r['domain'],r['arm'],r['session_id'])
        if k in idx:raise ValueError('Duplicate prediction')
        idx[k]=r
    results=[];classes=[];confusions=[]
    for (protocol,domain,arm),rr in sorted(by.items()):
        ss=[scores(r) for r in rr];m={'source_protocol':protocol,'domain':domain,'arm':arm}
        results.append({**m,**metrics(rr),'ce_bits_uncapped':float(np.mean([s['ce_uncapped'] for s in ss])),
            'ce_floor_visits':sum(s['ce_floor_applied'] for s in ss)})
        y=[s['true_class'] for s in ss];pred=[s['prediction'] for s in ss]
        pp,rec,f1,support=precision_recall_fscore_support(y,pred,labels=list(range(6)),zero_division=0)
        classes.extend({**m,'label':lab,'precision':float(pp[i]),'recall':float(rec[i]),'f1':float(f1[i]),'support':int(support[i])} for i,lab in enumerate(rr[0]['labels']))
        confusions.append({**m,'labels':rr[0]['labels'],'matrix':confusion_matrix(y,pred,labels=list(range(6))).tolist()})
    comps=[]
    for pr in cfg['directions']:
        for domain in ('source','target'):
            for a,b in [('F','B'),('H','B'),('H','F'),('F','E'),('H','E')]:
                comps.append({'source_protocol':pr,'domain':domain,'contrast':a+'-'+b,'type':'same_visit_method',
                    'primary':domain=='target' and b=='B',**contrast(by[pr,domain,a],by[pr,domain,b],cfg)})
        for arm in cfg['arms']:
            comps.append({'source_protocol':pr,'contrast':'target-source','arm':arm,'type':'matched_content_domain',
                **domain_contrast(by[pr,'target',arm],by[pr,'source',arm],cfg)})
    changes=[];fidelity=[];ranges=[];inputs=[]
    for pr,f,key in contexts(cfg):
        state=read(root/'prepared'/f'{key}.json');j=state['indices'];w=np.asarray(read(root/'classifiers'/f'{key}-pre.json')['coef']);wc=w-w.mean(0)
        for domain in ('source','target'):
            bundle=read(root/'post-input'/f'{key}-{domain}.json');raw=np.asarray(bundle['raw_post'],float)
            transformed=scale_selected(raw,state['post_scaler'],list(range(157)))
            inputs.append({'context':key,'domain':domain,'raw_missing_values':int(np.isnan(raw).sum()),
                'max_abs_source_post_z':float(abs(transformed).max()),'coordinates_abs_z_over_10':int((abs(transformed)>10).sum()),'diagnostic_only':True})
            pre=np.asarray(read(root/'pre-reference'/f'{key}-{domain}.json')['raw_pre'],float)
            target_u=(pre[:,j]-np.asarray(state['target_scaler']['mean'])[j])/np.asarray(state['target_scaler']['scale'])[j]
            for i,sid in enumerate(bundle['session_ids']):
                metadata=meta[key,domain,sid];common={**metadata,'context':key,'source_protocol':pr,'domain':domain,'fold':f}
                arow=idx[key,domain,'A',sid]
                for a,b in [('B','F'),('B','H'),('F','H'),('A','F'),('A','H')]:
                    x=scores(idx[key,domain,a,sid]);y=scores(idx[key,domain,b,sid])
                    changes.append({**common,'transition':a+'->'+b,'from_correct':x['prediction']==x['true_class'],
                        'to_correct':y['prediction']==y['true_class'],'class_changed':x['prediction']!=y['prediction'],
                        'ce_change':y['ce']-x['ce'],'brier_change':y['brier']-x['brier'],
                        'true_probability_change':y['true_probability']-x['true_probability']})
                for arm in ('F','H'):
                    row=idx[key,domain,arm,sid];diff=np.asarray(row['coordinates'])-arow['coordinates'];hat=np.asarray(row['raw_recovered'])
                    u=(hat[j]-np.asarray(state['target_scaler']['mean'])[j])/np.asarray(state['target_scaler']['scale'])[j]
                    valid=np.isfinite(target_u[i]);mask=valid.astype(float)
                    if not valid.all():raise ValueError('Missing held-out active pre target: review diagnostic scope')
                    fidelity.append({**common,'arm':arm,'d':len(j),'target_mse':float(np.mean((u-target_u[i])**2)),
                        'source_mse':float(np.mean(diff[j]**2)),'centered_logit_mse':float(np.sum((wc@diff)**2)/5),
                        'source_class_agreement':bool(np.argmax(row['probabilities'])==np.argmax(arow['probabilities']))})
                    ranges.append({**common,'arm':arm,**physical(hat)})
    fs=defaultdict(list);ds=defaultdict(list);ps=defaultdict(list)
    for r in changes:fs[r['source_protocol'],r['domain'],r['transition']].append(r)
    for r in fidelity:ds[r['source_protocol'],r['domain'],r['arm']].append(r)
    for r in ranges:ps[r['source_protocol'],r['domain'],r['arm']].append(r)
    flips=[]
    for k,v in sorted(fs.items()):
        counts={n:sum(r['from_correct']==a and r['to_correct']==b for r in v) for n,a,b in [('correct_correct',True,True),('correct_wrong',True,False),('wrong_correct',False,True),('wrong_wrong',False,False)]}
        nc=counts['correct_correct']+counts['correct_wrong'];nw=counts['wrong_correct']+counts['wrong_wrong']
        flips.append({'source_protocol':k[0],'domain':k[1],'transition':k[2],**counts,
            'class_change_rate':sum(r['class_changed'] for r in v)/len(v),'harm_rate':counts['correct_wrong']/nc if nc else None,
            'rescue_rate':counts['wrong_correct']/nw if nw else None})
    dsrows=[{'source_protocol':k[0],'domain':k[1],'arm':k[2],**{field:float(np.mean([r[field] for r in v])) for field in ('target_mse','source_mse','centered_logit_mse','source_class_agreement')}} for k,v in sorted(ds.items())]
    psrows=[{'source_protocol':k[0],'domain':k[1],'arm':k[2],'negative_visits':sum(bool(r['negative_indices']) for r in v),
        'unit_violation_visits':sum(bool(r['unit_interval_violations']) for r in v),'nonmonotone_visits':sum(r['curve_nonmonotone'] for r in v),
        **{field:max(r[field] for r in v) for field in ('maximum_unit_interval_excess','maximum_histogram_sum_deviation','maximum_curve_decrease')}} for k,v in sorted(ps.items())]
    if len(comps)!=30 or len(results)!=20 or len(rows)!=2400:raise ValueError('Reporting budget')
    write_json(out/'metrics.json',results);write_json(out/'contrasts.json',comps);write_json(out/'per-class.json',classes);write_json(out/'confusions.json',confusions)
    write_json(out/'fold-metrics.json',[{'source_protocol':k[0],'domain':k[1],'arm':k[2],'fold':k[3],**metrics(v)} for k,v in sorted(fb.items())])
    write_table(out/'predictions.parquet',rows);write_table(out/'visit-changes.parquet',changes);write_json(out/'decision-flips.json',flips)
    write_table(out/'fidelity.parquet',fidelity);write_json(out/'fidelity-summary.json',dsrows)
    write_table(out/'physical.parquet',ranges);write_json(out/'physical-summary.json',psrows);write_json(out/'input-diagnostics.json',inputs)
    write_json(out/'validation.json',{'passed':True,'contrasts':30,'predictions':2400,'historical_target_visibility':True})
    seal(out,passed=True)
    for r in results:print(r,flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--config',default=str(CONFIG));a=p.parse_args();report(a.config)
