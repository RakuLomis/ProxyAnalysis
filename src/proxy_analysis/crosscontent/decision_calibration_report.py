"""Fixed task contrasts and offline source-fidelity diagnostics; no selection."""
import argparse
from collections import defaultdict
import numpy as np
from sklearn.metrics import precision_recall_fscore_support,confusion_matrix
from .decision_calibration_contract import CONFIG,verify
from .decision_calibration_runner import name,predict_one
from .source_transfer_report import scores,contrast,fixed_margin_contributions
from .source_transfer_coordinates import source_selected
from .source_transfer_runner import physical_checks
from .natural_pair_ssl_report import metrics,softmax
from .business_representations import dictionary,BOUNDED
from .mechanism_contract import read
from .paired_structure_contract import seal,validate_complete
from ..paired_information.prepare import table
from ..reproducibility.preflight import write_json,write_table


def physical(raw):
    raw=np.asarray(raw);nn=dictionary()['distribution157']
    j=[i for i,n in enumerate(nn) if n in BOUNDED or n.startswith(('length_p_','iat_p_','curve_'))]
    return {**physical_checks(raw.tolist(),list(range(157))),
        'maximum_negative_magnitude':float(max(0,-raw.min())),
        'maximum_unit_interval_excess':float(max(0,-raw[j].min(),raw[j].max()-1)),
        'maximum_histogram_sum_deviation':float(max(abs(raw[14:33].sum()-1),abs(raw[33:56].sum()-1))),
        'maximum_curve_decrease':float(max(0,-np.diff(raw[56:]).min()))}


def report(config=CONFIG):
    cfg,root,source=verify(config);validate_complete(root/'inference');out=root/'report'
    if out.exists():raise FileExistsError('Report exists')
    metadata={r['session_id']:r for f in range(5) for r in read(source/'evaluation'/f'fold-{f}.json')['rows']}
    base=[r for r in table(source/'inference/predictions.parquet') if r['subset']=='Full']
    rows=[{**r,**metadata[r['session_id']]} for r in base+table(root/'inference/predictions.parquet')]
    indexed={(r['arm'],r['session_id']):r for r in rows};by=defaultdict(list);foldby=defaultdict(list)
    for r in rows:
        for pr in ('pooled',r['protocol']):
            by[r['arm'],pr].append(r);foldby[r['arm'],pr,r['fold']].append(r)
    result=[];classes=[];confusions=[]
    for (arm,pr),rr in sorted(by.items()):
        s=[scores(r) for r in rr];meta={'arm':arm,'protocol':pr}
        result.append({**meta,**metrics(rr),'ce_bits_uncapped':float(np.mean([x['ce_uncapped'] for x in s])),
            'ce_floor_visits':sum(x['ce_floor_applied'] for x in s)})
        y=[x['true_class'] for x in s];pred=[x['prediction'] for x in s]
        pp,rec,f1,support=precision_recall_fscore_support(y,pred,labels=list(range(6)),zero_division=0)
        classes.extend({**meta,'label':lab,'precision':float(pp[i]),'recall':float(rec[i]),'f1':float(f1[i]),'support':int(support[i])}
                       for i,lab in enumerate(rr[0]['labels']))
        confusions.append({**meta,'labels':rr[0]['labels'],'matrix':confusion_matrix(y,pred,labels=list(range(6))).tolist()})
    comparisons=[];flips=[];flip_summary=[]
    for lam in cfg['lambdas'][1:]:
        f,g=name('true',lam),name('wrong',lam)
        for pr in ('pooled','SHADOWSOCKS','VLESS'):
            for a,b in [(f,'C'),(f,g),(g,'D'),(f,'B'),(f,'A'),(f,'E')]:
                comparisons.append({'lambda':lam,'protocol':pr,'contrast':a+' - '+b,
                    'primary':lam==1 and (a,b) in [(f,'C'),(f,g)],**contrast(by[a,pr],by[b,pr],cfg)})
        for a,b in [('C',f),(g,f),('D',g),('B',f),('A',f)]:
            rr=[]
            for sid,meta in metadata.items():
                x=scores(indexed[a,sid]);y=scores(indexed[b,sid]);p=x['prediction']==x['true_class'];q=y['prediction']==y['true_class']
                rr.append({**meta,'lambda':lam,'transition':a+' -> '+b,'from_correct':p,'to_correct':q,
                    'class_changed':x['prediction']!=y['prediction'],'from_prediction':x['prediction'],'to_prediction':y['prediction'],
                    'ce_change':y['ce']-x['ce'],'brier_change':y['brier']-x['brier'],
                    'true_probability_change':y['true_probability']-x['true_probability']})
            flips+=rr
            for pr in ('pooled','SHADOWSOCKS','VLESS'):
                vv=rr if pr=='pooled' else [r for r in rr if r['protocol']==pr]
                counts={key:sum(r['from_correct']==x and r['to_correct']==y for r in vv) for key,x,y in
                    [('correct_correct',True,True),('correct_wrong',True,False),('wrong_correct',False,True),('wrong_wrong',False,False)]}
                nc=counts['correct_correct']+counts['correct_wrong'];nw=counts['wrong_correct']+counts['wrong_wrong']
                flip_summary.append({'lambda':lam,'transition':a+' -> '+b,'protocol':pr,**counts,
                    'class_change_rate':sum(r['class_changed'] for r in vv)/len(vv),
                    'wrong_wrong_class_changes':sum(not r['from_correct'] and not r['to_correct'] and r['class_changed'] for r in vv),
                    'harm_rate':counts['correct_wrong']/nc if nc else None,'rescue_rate':counts['wrong_correct']/nw if nw else None})
    boundaries=[];diagnostics=[];physical_rows=[]
    manifest=read(root/'contract/manifest.json')
    from pathlib import Path
    old=Path(manifest['diagnostics_root'])
    for fold in range(5):
        tr=read(source/'train'/f'fold-{fold}.json');pack=read(root/'train'/f'fold-{fold}.json');j=pack['indices']
        model=read(source/'source-fits'/f'fold-{fold}-Full.json');w=np.asarray(model['coef']);wc=w-w.mean(0)
        pre=read(source/'pre-reference'/f'fold-{fold}.json');post=read(source/'post-input'/f'fold-{fold}.json')
        training=read(old/'packages'/f'fold-{fold}.train.json')
        train_bundle={'fold':fold,'session_ids':pack['train_ids'],'raw_post':training['raw_post']}
        for sid in post['session_ids']:
            a=indexed['A',sid];c=indexed['C',sid]
            for arm in ['C']+[name('true',lam) for lam in cfg['lambdas'][1:]]:
                target=indexed[arm,sid];val=fixed_margin_contributions(a,target,model)
                boundaries.append({**metadata[sid],'fold':fold,'arm':arm,'transition':'A -> '+arm,**val})
                if arm!='C':
                    original=fixed_margin_contributions(a,c,model)
                    delta={key:val['group_contributions'][key]-original['group_contributions'][key] for key in val['group_contributions']}
                    change=val['fixed_rival_margin_change']-original['fixed_rival_margin_change']
                    boundaries.append({**metadata[sid],'fold':fold,'arm':arm,'transition':'C -> '+arm,
                        **val,'fixed_rival_margin_change':change,'group_contributions':delta,
                        'identity_error':abs(sum(delta.values())-change)})
        for relation,baseline in [('true','C'),('wrong','D')]:
            states=[(baseline,tr['mappings'][baseline])]
            for lam in cfg['lambdas']:
                part='zero-gate' if lam==0 else 'positive-fits';arm=name(relation,lam)
                states.append((arm,read(root/part/'fits'/f'{fold}-{arm}.json')['mapping']))
            for split,bundle,raw_pre in [('train',train_bundle,tr['raw_pre']),('test',post,pre['raw_pre'])]:
                actual=np.asarray(raw_pre,float)
                target_order=np.asarray(pack['donors']) if split=='train' and relation=='wrong' else np.arange(len(actual))
                reference=actual[target_order];zref=source_selected(reference,tr['source_scaler'],list(range(157)))
                tref=(reference[:,j]-np.asarray(tr['target_scaler']['mean'])[j])/np.asarray(tr['target_scaler']['scale'])[j]
                if not np.isfinite(tref).all():raise ValueError('Missing evaluation target requires review')
                refp=softmax(zref@w.T+model['intercept'])
                for arm,mapping in states:
                    z,raw,score,p=predict_one(bundle,tr,model,mapping)
                    u=(raw[:,j]-np.asarray(tr['target_scaler']['mean'])[j])/np.asarray(tr['target_scaler']['scale'])[j]
                    for i,sid in enumerate(bundle['session_ids']):
                        diff=z[i]-zref[i]
                        diagnostics.append({'fold':fold,'split':split,'arm':arm,'session_id':sid,
                            'target_relation':relation if split=='train' else 'true',
                            'target_mse':float(np.mean((u[i]-tref[i])**2)),
                            'source_mse':float(np.mean(diff[j]**2)),
                            'centered_logit_mse':float(np.sum((wc@diff)**2)/5),
                            'source_class_agreement':bool(p[i].argmax()==refp[i].argmax()),
                            'source_probability_l1':float(abs(p[i]-refp[i]).sum())})
                        physical_rows.append({'fold':fold,'split':split,'arm':arm,'session_id':sid,**physical(raw[i])})
    dg=defaultdict(list);pg=defaultdict(list)
    for r in diagnostics:dg[r['split'],r['arm'],r['target_relation']].append(r)
    for r in physical_rows:pg[r['split'],r['arm']].append(r)
    ds=[{'split':key[0],'arm':key[1],'target_relation':key[2],'rows':len(v),
         **{field:float(np.mean([r[field] for r in v])) for field in ('target_mse','source_mse','centered_logit_mse','source_class_agreement','source_probability_l1')}} for key,v in sorted(dg.items())]
    ps=[{'split':key[0],'arm':key[1],'rows':len(v),
         'negative_visits':sum(bool(r['negative_indices']) for r in v),
         'unit_violation_visits':sum(bool(r['unit_interval_violations']) for r in v),
         'nonmonotone_visits':sum(r['curve_nonmonotone'] for r in v),
         **{field:float(max(r[field] for r in v)) for field in ('maximum_negative_magnitude','maximum_unit_interval_excess','maximum_histogram_sum_deviation','maximum_curve_decrease')}} for key,v in sorted(pg.items())]
    if len(comparisons)!=54 or len(rows)!=3120:raise ValueError('Evaluation budget mismatch')
    write_json(out/'metrics.json',result);write_json(out/'paired-contrasts.json',comparisons)
    write_json(out/'per-class.json',classes);write_json(out/'confusions.json',confusions)
    write_json(out/'fold-metrics.json',[{'arm':k[0],'protocol':k[1],'fold':k[2],**metrics(v)} for k,v in sorted(foldby.items())])
    write_table(out/'predictions.parquet',rows);write_table(out/'visit-changes.parquet',flips);write_json(out/'decision-flips.json',flip_summary)
    write_table(out/'boundary-contributions.parquet',boundaries);write_table(out/'fidelity.parquet',diagnostics)
    write_json(out/'fidelity-summary.json',ds);write_table(out/'physical.parquet',physical_rows);write_json(out/'physical-summary.json',ps)
    write_json(out/'validation.json',{'passed':True,'contrasts':54,'predictions_with_baselines':3120,'boundary_rows':len(boundaries),
        'boundary_identity_error':max(r['identity_error'] for r in boundaries),'test_pre_used_only_for_offline_diagnostics':True})
    seal(out,passed=True)
    for r in result:
        if r['protocol']=='pooled':print(r,flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--config',default=str(CONFIG));a=p.parse_args();report(a.config)
