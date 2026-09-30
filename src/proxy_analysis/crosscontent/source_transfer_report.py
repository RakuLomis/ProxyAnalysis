"""Fixed A-E contrasts, paired decision flips and linear-boundary decompositions."""
import argparse
from collections import defaultdict
import numpy as np
from sklearn.metrics import precision_recall_fscore_support,confusion_matrix
from .source_transfer_contract import CONFIG,verify
from .source_transfer_coordinates import subsets
from .group_anchor_reliability import feature_groups
from .group_anchor_diagnostics_report import cluster_weights
from .natural_pair_ssl_report import metrics
from .mechanism_contract import read
from .paired_structure_contract import seal,validate_complete
from ..paired_information.prepare import table
from ..reproducibility.preflight import write_json,write_table

CONTRASTS=(('B','A'),('C','B'),('C','A'),('C','D'),('C','E'))
FLIPS=(('A','B'),('A','C'),('A','D'),('B','C'),('D','C'))


def scores(row):
    p=np.array(row['probabilities']);y=row['labels'].index(row['label_id']);z=np.array(row['logits'])
    shifted=z-z.max();uncapped=(np.log(np.exp(shifted).sum())-shifted[y])/np.log(2)
    return {'ce':float(-np.log2(max(p[y],1e-15))),'ce_uncapped':float(uncapped),
            'brier':float(((p-np.eye(len(p))[y])**2).sum()),'true_probability':float(p[y]),
            'prediction':int(p.argmax()),'true_class':y,'ce_floor_applied':bool(p[y]<1e-15)}


def count_scores(c):
    diag=np.diagonal(c,axis1=-2,axis2=-1);den=c.sum(-1)+c.sum(-2)
    f1=np.divide(2*diag,den,out=np.zeros_like(diag),where=den>0).mean(-1)
    total=c.sum(-1);ba=np.divide(diag,total,out=np.zeros_like(diag),where=total>0).mean(-1)
    return f1,ba


def contrast(a,b,cfg):
    ids=sorted({r['content_id'] for r in a});ci={c:i for i,c in enumerate(ids)}
    labels={r['content_id']:r['label_id'] for r in a};k=len(a[0]['labels'])
    def tensors(rows):
        counts=np.zeros((len(ids),k,k));loss=np.zeros((len(ids),2));den=np.zeros(len(ids))
        for row in rows:
            i=ci[row['content_id']];v=scores(row)
            counts[i,v['true_class'],v['prediction']]+=1;loss[i]+=[v['ce'],v['brier']];den[i]+=1
        if (den==0).any():raise ValueError('Missing bootstrap content')
        return counts,loss/den[:,None]
    ac,al=tensors(a);bc,bl=tensors(b)
    if {(r['session_id'],r['fold']) for r in a}!={(r['session_id'],r['fold']) for r in b}:raise ValueError('Unpaired contrast')
    weights=cluster_weights(ids,labels,cfg['bootstrap_repetitions'],cfg['bootstrap_seed'])
    af,aba=count_scores(np.einsum('bn,njk->bjk',weights,ac));bf,bba=count_scores(np.einsum('bn,njk->bjk',weights,bc))
    boot={'macro_f1':af-bf,'balanced_accuracy':aba-bba,
          'ce_bits':weights@(bl[:,0]-al[:,0]),'brier':weights@(bl[:,1]-al[:,1])}
    am=metrics(a);bm=metrics(b);result={'independent_contents':len(ids),'bootstrap_repetitions':cfg['bootstrap_repetitions']}
    for metric,values in boot.items():
        sign=-1 if metric in ('ce_bits','brier') else 1
        result[metric+'_gain']=sign*(am[metric]-bm[metric]);result[metric+'_ci']=np.quantile(values,[.025,.975]).tolist()
    result['interval_scope']='unadjusted descriptive, conditional on fitted models'
    return result


def fixed_margin_contributions(a,c,fit):
    y=a['labels'].index(a['label_id']);za=np.array(a['logits']);zc=np.array(c['logits'])
    allowed=[j for j in range(len(za)) if j!=y];ka=max(allowed,key=lambda j:za[j]);kc=max(allowed,key=lambda j:zc[j])
    w=np.asarray(fit['coef']);delta=np.asarray(c['coordinates'])-a['coordinates']
    terms=(w[y]-w[ka])*delta
    expected=(zc[y]-zc[ka])-(za[y]-za[ka]);actual=float(terms.sum())
    if not np.isclose(actual,expected,rtol=1e-9,atol=1e-9):raise ValueError('Boundary decomposition failed')
    index={j:i for i,j in enumerate(fit['indices'])}
    grouped={g['group']:float(sum(terms[index[j]] for j in g['indices'] if j in index)) for g in feature_groups()}
    margin_a=float(za[y]-za[ka]);margin_c=float(zc[y]-zc[kc])
    return {'true_class':y,'A_rival':ka,'C_rival':kc,'rival_changed':ka!=kc,
        'A_margin':margin_a,'C_margin':margin_c,'fixed_rival_margin_change':actual,'group_contributions':grouped,
        'identity_error':abs(actual-float(expected)),
        'train_defined_margin_bin':int(np.searchsorted(fit['train_margin_quartiles'],margin_a,side='right'))}


def report(config=CONFIG):
    cfg,old,root=verify(config);validate_complete(root/'inference')
    lookup={r['session_id']:r for f in range(5) for r in read(root/'evaluation'/f'fold-{f}.json')['rows']}
    rows=[{**r,**lookup[r['session_id']]} for r in table(root/'inference/predictions.parquet')]
    by=defaultdict(list);folds=defaultdict(list);results=[];classes=[];confusions=[]
    for r in rows:
        for protocol in (r['protocol'],'pooled'):
            by[r['subset'],r['arm'],protocol].append(r);folds[r['subset'],r['arm'],protocol,r['fold']].append(r)
    for (subset,arm,protocol),rr in sorted(by.items()):
        if len({r['session_id'] for r in rr})!=len(rr):raise ValueError('Duplicate OOF visits')
        extra=[scores(r) for r in rr];meta={'subset':subset,'arm':arm,'protocol':protocol}
        results.append({**meta,**metrics(rr),'ce_bits_uncapped':float(np.mean([s['ce_uncapped'] for s in extra])),
                        'ce_floor_visits':sum(s['ce_floor_applied'] for s in extra)})
        y=[s['true_class'] for s in extra];pred=[s['prediction'] for s in extra]
        pp,recall,f1,support=precision_recall_fscore_support(y,pred,labels=list(range(6)),zero_division=0)
        for j,label in enumerate(rr[0]['labels']):classes.append({**meta,'label':label,'precision':float(pp[j]),
            'recall':float(recall[j]),'f1':float(f1[j]),'support':int(support[j])})
        confusions.append({**meta,'labels':rr[0]['labels'],'matrix':confusion_matrix(y,pred,labels=list(range(6))).tolist()})
    comparisons=[]
    for subset in cfg['subsets']:
        for protocol in ('SHADOWSOCKS','VLESS','pooled'):
            for a,b in CONTRASTS:comparisons.append({'subset':subset,'protocol':protocol,'contrast':a+'-'+b,
                **contrast(by[subset,a,protocol],by[subset,b,protocol],cfg)})
    indexed={(r['subset'],r['arm'],r['session_id']):r for r in rows};flip_records=[];summaries=defaultdict(list)
    for subset in cfg['subsets']:
        for sid in sorted(lookup):
            for a,b in FLIPS:
                left=indexed[subset,a,sid];right=indexed[subset,b,sid];s=scores(left);t=scores(right)
                was=s['prediction']==s['true_class'];now=t['prediction']==t['true_class']
                value={'subset':subset,'transition':a+'->'+b,'session_id':sid,**lookup[sid],
                    'from_correct':was,'to_correct':now,'prediction_changed':s['prediction']!=t['prediction'],
                    'from_prediction':s['prediction'],'to_prediction':t['prediction'],
                    'ce_change':t['ce']-s['ce'],'brier_change':t['brier']-s['brier'],
                    'true_probability_change':t['true_probability']-s['true_probability']}
                flip_records.append(value)
                for protocol in (value['protocol'],'pooled'):summaries[subset,a+'->'+b,protocol].append(value)
    flips=[]
    for (subset,transition,protocol),rr in sorted(summaries.items()):
        counts={name:sum(r['from_correct']==a and r['to_correct']==b for r in rr)
                for name,a,b in [('correct_correct',True,True),('correct_wrong',True,False),
                                  ('wrong_correct',False,True),('wrong_wrong',False,False)]}
        correct=counts['correct_correct']+counts['correct_wrong'];wrong=counts['wrong_correct']+counts['wrong_wrong']
        flips.append({'subset':subset,'transition':transition,'protocol':protocol,'visits':len(rr),**counts,
            'class_change_rate':sum(r['prediction_changed'] for r in rr)/len(rr),
            'wrong_wrong_class_changes':sum(not r['from_correct'] and not r['to_correct'] and r['prediction_changed'] for r in rr),
            'harm_rate_among_previously_correct':counts['correct_wrong']/correct if correct else None,
            'rescue_rate_among_previously_wrong':counts['wrong_correct']/wrong if wrong else None})
    old_errors={(r['session_id'],r['group']):r for r in table(old/'report/recovery-group-errors.parquet')
                if r['split']=='test' and r['relation']=='true' and r['model']=='Ridge-true'}
    boundaries=[]
    for subset in cfg['subsets']:
        for sid in sorted(lookup):
            a=indexed[subset,'A',sid];c=indexed[subset,'C',sid];fit=read(root/'source-fits'/f'fold-{a["fold"]}-{subset}.json')
            val=fixed_margin_contributions(a,c,fit)
            relevant=[old_errors[sid,g['group']] for g in feature_groups() if subset=='Full' or subset=='Only-'+g['group']]
            den=sum(r['valid_dimensions'] for r in relevant)
            boundaries.append({'session_id':sid,**lookup[sid],'fold':a['fold'],'subset':subset,**val,
                'old_U_target_mse':sum(r['mse']*r['valid_dimensions'] for r in relevant)/den,
                'A_correct':scores(a)['prediction']==val['true_class'],'C_correct':scores(c)['prediction']==val['true_class']})
    if len(comparisons)!=105 or len(rows)!=8400 or len(boundaries)!=1680:raise ValueError('Reporting budget mismatch')
    out=root/'report'
    write_json(out/'metrics.json',results);write_json(out/'paired-contrasts.json',comparisons)
    write_json(out/'per-class.json',classes);write_json(out/'confusion-matrices.json',confusions)
    write_json(out/'fold-metrics.json',[{'subset':k[0],'arm':k[1],'protocol':k[2],'fold':k[3],**metrics(v)} for k,v in sorted(folds.items())])
    write_table(out/'predictions.parquet',rows);write_json(out/'decision-flips.json',flips)
    write_table(out/'visit-decision-changes.parquet',flip_records);write_table(out/'boundary-contributions.parquet',boundaries)
    write_json(out/'physical-range-violations.json',[{'subset':s,'arm':a,'visits':len(rr),
        'negative_visits':sum(bool(r['physical']['negative_indices']) for r in rr),
        'unit_interval_violation_visits':sum(bool(r['physical']['unit_interval_violations']) for r in rr),
        'nonmonotone_curve_visits':sum(r['physical']['curve_nonmonotone'] for r in rr),
        'histogram_nonunit_sum_visits':sum(any(abs(x-1)>1e-9 for x in r['physical']['histogram_sums']) for r in rr)}
        for s in cfg['subsets'] for a in ('C','D') for rr in [by[s,a,'pooled']]])
    write_json(out/'validation.json',{'passed':True,'predictions':8400,'paired_contrasts':105,
        'boundary_rows':len(boundaries),'max_boundary_identity_error':max(r['identity_error'] for r in boundaries),
        'ce_probability_floor':1e-15,'uncapped_logit_ce_also_reported':True,'test_driven_fitting':False})
    seal(out,passed=True);print('Migration metrics, flips and boundaries complete',flush=True)
    for r in results:
        if r['protocol']=='pooled':print(r,flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--config',default=str(CONFIG));args=parser.parse_args();report(args.config)
