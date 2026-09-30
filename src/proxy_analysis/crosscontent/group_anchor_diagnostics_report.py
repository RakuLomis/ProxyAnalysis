"""Evaluation-only targets and content-clustered diagnostic summaries."""
import argparse
from collections import defaultdict
import numpy as np
from sklearn.metrics import precision_recall_fscore_support, confusion_matrix
from .group_anchor_diagnostics_contract import CONFIG, verify, evaluation_package
from .group_anchor_reliability import feature_groups, normalized
from .natural_pair_ssl_report import metrics, compare
from .group_anchor_delivery import huber
from .mechanism_contract import read
from .paired_structure_contract import seal, validate_complete
from ..paired_information.prepare import table
from ..reproducibility.preflight import write_json, write_table


def business_report(cfg, root, evaluations):
    lookup = {r['session_id']:r for e in evaluations.values() for r in e['rows']}
    rows = [{**r,**lookup[r['session_id']],'seed':20260919} for r in table(root/'utility/predictions.parquet')]
    groups = defaultdict(list); results=[]; classes=[]; confusions=[]
    for r in rows:
        for protocol in (r['protocol'],'pooled'): groups[protocol,r['subset']].append(r)
    for (protocol,subset),rr in sorted(groups.items()):
        if len({r['session_id'] for r in rr})!=len(rr): raise ValueError('Duplicate OOF visit')
        results.append({'protocol':protocol,'subset':subset,**metrics(rr)})
        labels=rr[0]['labels']; y=[labels.index(r['label_id']) for r in rr]; pred=[np.argmax(r['probabilities']) for r in rr]
        pp,recall,f1,support=precision_recall_fscore_support(y,pred,labels=list(range(6)),zero_division=0)
        for j,label in enumerate(labels):
            classes.append({'protocol':protocol,'subset':subset,'label':label,'precision':float(pp[j]),
                            'recall':float(recall[j]),'f1':float(f1[j]),'support':int(support[j])})
        confusions.append({'protocol':protocol,'subset':subset,'labels':labels,
                           'matrix':confusion_matrix(y,pred,labels=list(range(6))).tolist()})
    contrasts=[]
    for protocol in ('SHADOWSOCKS','VLESS','pooled'):
        for g in feature_groups():
            for kind in ('Only','Minus'):
                subset=kind+'-'+g['group']
                contrasts.append({'protocol':protocol,'group':g['group'],'comparison':'Full-minus-'+subset,
                    **compare(groups[protocol,'Full'],groups[protocol,subset],cfg['bootstrap_repetitions'],[20260919])})
    return rows,results,contrasts,classes,confusions


def group_error(pred,target,mask,indices):
    valid=mask[indices]; count=int(valid.sum())
    if not count:return None
    residual=pred[indices][valid]-target[indices][valid]; baseline=target[indices][valid]
    return {'mse':float(np.square(residual).mean()),'huber':float(huber(residual).mean()),
            'null_mse':float(np.square(baseline).mean()),'null_huber':float(huber(baseline).mean()),
            'valid_dimensions':count,'excluded_dimensions':len(indices)-count}


def recovery_errors(root,evaluations):
    targets={};metadata={};rowlists={}
    for fold in range(5):
        train=read(root/'packages'/f'fold-{fold}.train.json'); ev=evaluations[fold]
        for split,rows,raw,donors in (('train',train['rows'],train['raw_pre'],train['donors']),
                                    ('test',ev['rows'],ev['raw_pre'],ev['donors'])):
            raw=np.asarray(raw,float); target=normalized(raw,train['pre_scaler'])
            mask=np.isfinite(raw)&np.array(train['pre_scaler']['valid'])
            targets[fold,split]=(target,mask,donors);rowlists[fold,split]=rows
            metadata[fold,split]={r['session_id']:(i,r) for i,r in enumerate(rows)}
    errors=[]; residuals=[]
    for r in table(root/'recovery/predictions.parquet'):
        fold,split=r['fold'],r['split']; target,mask,donors=targets[fold,split]
        i,meta=metadata[fold,split][r['session_id']];pred=np.array(r['prediction'])
        relations=['true']+(['mismatched'] if r['model'] in ('R5','R6','Ridge-wrong','Mean') else [])
        for relation in relations:
            j=i if relation=='true' else donors[i]; yy=target[j];valid=mask[j]
            base={k:v for k,v in r.items() if k!='prediction'}
            base.update({k:meta[k] for k in ('content_id','label_id','protocol','repetition')})
            base.update({'relation':relation,'target_id':rowlists[fold,split][j]['session_id']})
            residuals.append({**base,'residual':(pred-yy).tolist(),'valid_mask':valid.tolist()})
            for g in feature_groups():
                value=group_error(pred,yy,valid,g['indices'])
                if value is not None:errors.append({**base,'group':g['group'],**value})
    return errors,residuals


def cluster_weights(ids,metadata,repetitions,seed):
    classes=defaultdict(list)
    for i,c in enumerate(ids):classes[metadata[c]].append(i)
    rng=np.random.default_rng(seed)
    draws=np.concatenate([rng.choice(v,size=(repetitions,len(v)),replace=True) for _,v in sorted(classes.items())],axis=1)
    return np.stack([(draws==i).sum(1) for i in range(len(ids))],axis=1)/len(ids)


def recovery_report(cfg,records):
    repeated=defaultdict(list); labels={}
    for r in records:
        labels[r['content_id']]=r['label_id']
        for protocol in (r['protocol'],'pooled'):
            key=(r['split'],r['relation'],protocol,r['group'],r['model'],r['seed'],r['fold'],r['content_id'])
            repeated[key].append([r['mse'],r['huber'],r['null_mse'],r['null_huber']])
    contents=defaultdict(list);seedgroups=defaultdict(list)
    for key,values in repeated.items():
        split,relation,protocol,group,model,seed,fold,content=key;v=np.mean(values,axis=0)
        contents[split,relation,protocol,group,model,fold,content].append(v)
        seedgroups[split,relation,protocol,group,model,seed].append(v)
    def record(key,values):
        split,relation,protocol,group,model=key; m=np.mean(values,axis=0)
        return {'split':split,'relation':relation,'protocol':protocol,'group':group,'model':model,
                'mse':float(m[0]),'huber':float(m[1]),'null_mse':float(m[2]),'null_huber':float(m[3]),
                'skill_mse':float(1-m[0]/m[2]) if m[2]>cfg['numerical_eps'] else None}
    per_seed=[{**record(k[:-1],v),'seed':k[-1]} for k,v in seedgroups.items()]
    aggregate=defaultdict(dict)
    for k,v in contents.items():aggregate[k[:-2]][k[-2],k[-1]]=np.mean(v,axis=0)
    summary=[{**record(k,list(v.values())),'content_fold_blocks':len(v),
              'training_blocks_overlap_across_folds':k[0]=='train'} for k,v in sorted(aggregate.items())]
    contrasts=[]
    for relation in ('true','mismatched'):
        arms=cfg['arms'] if relation=='true' else ['R5','R6']
        refs=['Ridge-true','Mean'] if relation=='true' else ['Ridge-wrong','Mean']
        for protocol in ('SHADOWSOCKS','VLESS','pooled'):
            for g in feature_groups():
                for arm in arms:
                    a=aggregate['test',relation,protocol,g['group'],arm];keys=sorted(a);ids=[k[1] for k in keys]
                    if len(ids)!=len(set(ids)):raise ValueError('OOF content duplicated')
                    weights=cluster_weights(ids,labels,cfg['bootstrap_repetitions'],cfg['bootstrap_seed'])
                    for ref in refs:
                        b=aggregate['test',relation,protocol,g['group'],ref]
                        if set(a)!=set(b):raise ValueError('Evaluation support differs')
                        delta=np.stack([b[k]-a[k] for k in keys]);intervals=np.quantile(weights@delta[:,:2],[.025,.975],axis=0)
                        contrasts.append({'relation':relation,'protocol':protocol,'group':g['group'],'model':arm,'reference':ref,
                            'mse_gain':float(delta[:,0].mean()),'mse_gain_ci':intervals[:,0].tolist(),
                            'huber_gain':float(delta[:,1].mean()),'huber_gain_ci':intervals[:,1].tolist(),
                            'independent_contents':len(ids),'scope':'unadjusted conditional descriptive intervals'})
    return summary,per_seed,contrasts


def report(config=CONFIG):
    cfg,anchor,root=verify(config);validate_complete(root/'hierarchy')
    evaluations={f:evaluation_package(root,f) for f in range(cfg['folds'])}
    predictions,utility,contrasts,classes,confusions=business_report(cfg,root,evaluations)
    errors,residuals=recovery_errors(root,evaluations)
    recovery,per_seed,recovery_contrasts=recovery_report(cfg,errors);out=root/'report'
    write_table(out/'utility-predictions.parquet',predictions)
    for name,data in [('utility-metrics',utility),('utility-contrasts',contrasts),('utility-per-class',classes),
                      ('utility-confusions',confusions),('recovery-summary',recovery),('recovery-per-seed',per_seed),
                      ('recovery-contrasts',recovery_contrasts)]:write_json(out/(name+'.json'),data)
    write_table(out/'recovery-residuals.parquet',residuals);write_table(out/'recovery-group-errors.parquet',errors)
    hierarchy=defaultdict(list)
    for r in read(root/'hierarchy/group-levels.json'):hierarchy[r['protocol'],r['group'],r['relation'],r['level']].append(r)
    hs=[]
    for key,values in sorted(hierarchy.items()):
        protocol,group,relation,level=key
        row={'protocol':protocol,'group':group,'relation':relation,'level':level,'outer_training_folds':len(values)}
        for field in ('pre_energy','post_energy','correlation','signed_total_contribution'):
            v=[r[field] for r in values if r[field] is not None]
            row[field+'_median']=float(np.median(v)) if v else None
            row[field+'_range']=[float(min(v)),float(max(v))] if v else None
        hs.append(row)
    write_json(out/'hierarchy-summary.json',hs);joint=[]
    for protocol in ('SHADOWSOCKS','VLESS','pooled'):
        for g in feature_groups():
            group=g['group'];only=next(r for r in utility if r['protocol']==protocol and r['subset']=='Only-'+group)
            deleted=next(r for r in contrasts if r['protocol']==protocol and r['comparison']=='Full-minus-Minus-'+group)
            rec=[r for r in recovery if r['split']=='test' and r['relation']=='true' and r['protocol']==protocol
                 and r['group']==group and r['model'] in ('Ridge-true','R4')]
            history=[s['skill'] for f in range(5) for s in read(anchor/'reliability'/f'six_business-{f}'/'true.json')['scores']
                     if s['group']==group and (s['protocol']==protocol or protocol=='pooled')]
            joint.append({'protocol':protocol,'group':group,'historical_inner_skill_mean':float(np.mean(history)),
                'historical_pooled_mean_is_deployment_average':protocol=='pooled','only_group':only,
                'deletion_increment':deleted,'heldout_recovery':rec,
                'hierarchy':[r for r in hs if r['protocol']==protocol and r['group']==group]})
    write_json(out/'joint-diagnostics.json',joint)
    write_json(out/'validation.json',{'passed':True,'classifier_fits':read(root/'utility/validation.json')['fits'],
        'ridge_fits':read(root/'recovery/validation.json')['ridge_fits'],'new_neural_fits':0,
        'utility_predictions':len(predictions),'recovery_residual_vectors':len(residuals),'group_errors':len(errors),
        'recovery_contrasts':len(recovery_contrasts),'test_pre_used_only_for_offline_error_evaluation':True,
        'test_driven_model_changes':False})
    seal(out,passed=True);print('Completed evaluation and diagnostic tables',flush=True)
    for r in utility:
        if r['protocol']=='pooled':print(r,flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--config',default=str(CONFIG));args=parser.parse_args();report(args.config)
