"""Eight-arm fixed evaluation, with train and held-out fidelity kept separate."""
import argparse
from collections import defaultdict
from pathlib import Path
import numpy as np
from sklearn.metrics import precision_recall_fscore_support,confusion_matrix
from .source_hierarchy_contract import CONFIG,verify
from .decision_calibration_runner import name,predict_one
from .decision_calibration_report import physical
from .source_transfer_report import scores,contrast
from .source_transfer_coordinates import source_selected
from .natural_pair_ssl_report import metrics,softmax
from .mechanism_contract import read
from .paired_structure_contract import seal,validate_complete
from ..paired_information.prepare import table,digest
from ..reproducibility.preflight import write_json,write_table


def report(config=CONFIG):
    cfg,root,old,source=verify(config);validate_complete(root/'inference');out=root/'report'
    if out.exists():raise FileExistsError(out)
    meta={r['session_id']:r for f in range(5) for r in read(source/'evaluation'/f'fold-{f}.json')['rows']}
    alias={name('true',1):'F',name('wrong',1):'G'}
    baseline=[r for r in table(source/'inference/predictions.parquet') if r['subset']=='Full']
    baseline += [{**r,'arm':alias[r['arm']]} for r in table(old/'inference/predictions.parquet') if r['arm'] in alias]
    rows=[{**r,**meta[r['session_id']]} for r in baseline+table(root/'inference/predictions.parquet')]
    if len(baseline)!=1680 or len(rows)!=1920:raise ValueError('Budget mismatch')
    by=defaultdict(list);foldby=defaultdict(list);indexed={}
    for r in rows:
        key=(r['arm'],r['session_id'])
        if key in indexed:raise ValueError('Duplicate predictions')
        indexed[key]=r
        for pr in ('pooled',r['protocol']):by[r['arm'],pr].append(r);foldby[r['arm'],pr,r['fold']].append(r)
    results=[];classes=[];confusions=[]
    for (arm,pr),rr in sorted(by.items()):
        ss=[scores(r) for r in rr];m={'arm':arm,'protocol':pr}
        results.append({**m,**metrics(rr),'ce_bits_uncapped':float(np.mean([s['ce_uncapped'] for s in ss])),
            'ce_floor_visits':sum(s['ce_floor_applied'] for s in ss)})
        y=[s['true_class'] for s in ss];pred=[s['prediction'] for s in ss]
        pp,rec,f1,support=precision_recall_fscore_support(y,pred,labels=list(range(6)),zero_division=0)
        classes.extend({**m,'label':label,'precision':float(pp[i]),'recall':float(rec[i]),'f1':float(f1[i]),'support':int(support[i])} for i,label in enumerate(rr[0]['labels']))
        confusions.append({**m,'labels':rr[0]['labels'],'matrix':confusion_matrix(y,pred,labels=list(range(6))).tolist()})
    contrasts=[{'contrast':'H-'+arm,'protocol':pr,'primary':arm in ('F','G'),**contrast(by['H',pr],by[arm,pr],cfg)}
        for arm in ('F','G','C','D','B','A','E') for pr in ('pooled','SHADOWSOCKS','VLESS')]
    changes=[];flip_summaries=[]
    for arm in ('F','G','C','D','A'):
        vv=[]
        for sid,metadata in meta.items():
            a=scores(indexed[arm,sid]);b=scores(indexed['H',sid])
            vv.append({**metadata,'transition':arm+'->H','from_correct':a['prediction']==a['true_class'],
                'to_correct':b['prediction']==b['true_class'],'class_changed':a['prediction']!=b['prediction'],
                'from_prediction':a['prediction'],'to_prediction':b['prediction'],
                'ce_change':b['ce']-a['ce'],'brier_change':b['brier']-a['brier'],
                'true_probability_change':b['true_probability']-a['true_probability']})
        changes+=vv
        for pr in ('pooled','SHADOWSOCKS','VLESS'):
            rr=vv if pr=='pooled' else [r for r in vv if r['protocol']==pr]
            counts={k:sum(r['from_correct']==a and r['to_correct']==b for r in rr) for k,a,b in [('correct_correct',True,True),('correct_wrong',True,False),('wrong_correct',False,True),('wrong_wrong',False,False)]}
            nc=counts['correct_correct']+counts['correct_wrong'];nw=counts['wrong_correct']+counts['wrong_wrong']
            flip_summaries.append({'transition':arm+'->H','protocol':pr,**counts,
                'class_change_rate':sum(r['class_changed'] for r in rr)/len(rr),
                'wrong_wrong_class_changes':sum(not r['from_correct'] and not r['to_correct'] and r['class_changed'] for r in rr),
                'harm_rate':counts['correct_wrong']/nc if nc else None,'rescue_rate':counts['wrong_correct']/nw if nw else None})
    fidelity=[];phys=[]
    diagnostics=Path(read(old/'contract/manifest.json')['diagnostics_root'])
    for fold in range(5):
        pack=read(root/'train'/f'fold-{fold}.json');j=pack['indices'];tr=read(source/'train'/f'fold-{fold}.json')
        model=read(source/'source-fits'/f'fold-{fold}-Full.json');w=np.asarray(model['coef']);wc=w-w.mean(0)
        train=read(diagnostics/'packages'/f'fold-{fold}.train.json')
        trainpost={'fold':fold,'session_ids':pack['train_ids'],'raw_post':train['raw_post']}
        testpost=read(source/'post-input'/f'fold-{fold}.json');testpre=read(source/'pre-reference'/f'fold-{fold}.json')
        states={'H':read(root/'fits'/f'fold-{fold}.json')['mapping']}
        for rel,arm in [('true','F'),('wrong','G')]:states[arm]=read(old/'positive-fits/fits'/f'{fold}-{name(rel,1)}.json')['mapping']
        for split,bundle,rawpre in [('train',trainpost,tr['raw_pre']),('test',testpost,testpre['raw_pre'])]:
            target=source_selected(rawpre,tr['source_scaler'],list(range(157)))
            target_u=(np.asarray(rawpre,float)[:,j]-np.asarray(tr['target_scaler']['mean'])[j])/np.asarray(tr['target_scaler']['scale'])[j]
            if not np.isfinite(target_u).all():raise ValueError('Missing evaluation target')
            for arm,state in states.items():
                z,raw,score,prob=predict_one(bundle,tr,model,state)
                for relation,zref,tref in [('true',target,target_u)]+([('center',np.zeros_like(target),np.asarray(pack['t']))] if arm=='H' and split=='train' else []):
                    if relation=='center':zref[:,j]=tref*pack['c']+pack['offset']
                    refprob=softmax(zref@w.T+model['intercept'])
                    uh=(raw[:,j]-np.asarray(tr['target_scaler']['mean'])[j])/np.asarray(tr['target_scaler']['scale'])[j]
                    for i,sid in enumerate(bundle['session_ids']):
                        diff=z[i]-zref[i]
                        fidelity.append({'fold':fold,'split':split,'arm':arm,'target_relation':relation,'session_id':sid,
                            'target_mse':float(np.mean((uh[i]-tref[i])**2)),'source_mse':float(np.mean(diff[j]**2)),
                            'centered_logit_mse':float(np.sum((wc@diff)**2)/5),
                            'source_class_agreement':bool(prob[i].argmax()==refprob[i].argmax()),
                            'source_probability_l1':float(abs(prob[i]-refprob[i]).sum())})
                for i,sid in enumerate(bundle['session_ids']):phys.append({'fold':fold,'split':split,'arm':arm,'session_id':sid,**physical(raw[i])})
    dg=defaultdict(list);pg=defaultdict(list)
    for r in fidelity:dg[r['split'],r['arm'],r['target_relation']].append(r)
    for r in phys:pg[r['split'],r['arm']].append(r)
    ds=[{'split':k[0],'arm':k[1],'target_relation':k[2],'rows':len(v),**{field:float(np.mean([r[field] for r in v])) for field in ('target_mse','source_mse','centered_logit_mse','source_class_agreement','source_probability_l1')}} for k,v in sorted(dg.items())]
    ps=[{'split':k[0],'arm':k[1],'rows':len(v),'negative_visits':sum(bool(r['negative_indices']) for r in v),
         'unit_violation_visits':sum(bool(r['unit_interval_violations']) for r in v),'nonmonotone_visits':sum(r['curve_nonmonotone'] for r in v),
         **{field:float(max(r[field] for r in v)) for field in ('maximum_negative_magnitude','maximum_unit_interval_excess','maximum_histogram_sum_deviation','maximum_curve_decrease')}} for k,v in sorted(pg.items())]
    write_json(out/'metrics.json',results);write_json(out/'paired-contrasts.json',contrasts)
    write_json(out/'per-class.json',classes);write_json(out/'confusions.json',confusions)
    write_json(out/'fold-metrics.json',[{'arm':k[0],'protocol':k[1],'fold':k[2],**metrics(v)} for k,v in sorted(foldby.items())])
    write_table(out/'predictions.parquet',rows);write_table(out/'visit-changes.parquet',changes);write_json(out/'decision-flips.json',flip_summaries)
    write_table(out/'fidelity.parquet',fidelity);write_json(out/'fidelity-summary.json',ds)
    write_table(out/'physical.parquet',phys);write_json(out/'physical-summary.json',ps)
    write_json(out/'baseline-reuse.json',[{'path':str(p),'sha256':digest(p),'filter':f} for p,f in
        [(source/'inference/predictions.parquet','Full A-E'),(old/'inference/predictions.parquet','true/wrong lambda 1')]])
    write_json(out/'validation.json',{'passed':True,'contrasts':len(contrasts),'predictions':len(rows),
        'new_predictions':240,'reused_predictions':1680,'test_pre_only_offline':True})
    seal(out,passed=True)
    for r in results:
        if r['protocol']=='pooled':print(r,flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--config',default=str(CONFIG));a=p.parse_args();report(a.config)
