"""Training-only source-score dispersion and frozen F/G residual description."""
import argparse
from collections import Counter,defaultdict
from itertools import combinations
import numpy as np
from .source_hierarchy_contract import CONFIG,verify,center_targets
from .decision_calibration_runner import name
from .natural_pair_ssl_report import softmax
from .mechanism_contract import read
from .paired_structure_contract import seal
from ..reproducibility.preflight import write_json,write_table


def run(config=CONFIG):
    _,root,old,source=verify(config);out=root/'hierarchy'
    if out.exists():raise FileExistsError(out)
    group_rows=[];visits=[];summaries=[];residuals=[];bins=[];maxerr=0.
    for f in range(5):
        p=read(root/'train'/f'fold-{f}.json');rows=read(source/'train'/f'fold-{f}.json')['rows']
        model=read(source/'source-fits'/f'fold-{f}-Full.json');w=np.asarray(p['weights']);wc=w-w.mean(0)
        z=np.asarray(p['t_original'])*p['c']+p['offset'];zc=np.asarray(p['t'])*p['c']+p['offset']
        s=z@wc.T;sc=zc@wc.T;e=s-sc;score=z@w.T+model['intercept'];prob=softmax(score)
        pred=score.argmax(1);centerpred=(zc@w.T+model['intercept']).argmax(1);donor=np.asarray(p['donors'])
        diff=((s-s[donor])**2).sum(1)/5;predchange=pred!=pred[donor]
        foldgroups=[];foldvisits=[]
        for ix in p['groups']:
            r=rows[ix[0]];err=float(abs(e[ix].sum(0)).max());maxerr=max(maxerr,err)
            if not np.allclose(e[ix].sum(0),0,atol=1e-10):raise ValueError('Residual identity')
            g={'fold':f,'content_id':r['content_id'],'protocol':r['protocol'],
                'dispersion':float((e[ix]**2).sum()/20),'score_std':s[ix].std(0).tolist(),
                'all_four_same':len(set(pred[ix]))==1,'pair_agreement':sum(pred[a]==pred[b] for a,b in combinations(ix,2))/6,
                'majority_fraction':max(Counter(pred[ix]).values())/4,'center_agreement':float(np.mean(pred[ix]==centerpred[ix])),
                'cyclic_score_difference':float(diff[ix].mean()),'donor_class_change':float(predchange[ix].mean()),
                'donor_probability_l1':float(abs(prob[ix]-prob[donor[ix]]).sum(1).mean())}
            foldgroups.append(g)
        for i,r in enumerate(rows):
            y=model['labels'].index(r['label_id']);margin=float(score[i,y]-max(score[i,j] for j in range(6) if j!=y))
            foldvisits.append({**r,'fold':f,'score':s[i].tolist(),'center':sc[i].tolist(),'residual':e[i].tolist(),
                'source_prediction':int(pred[i]),'center_prediction':int(centerpred[i]),'donor_prediction':int(pred[donor[i]]),
                'score_difference':float(diff[i]),'donor_class_change':bool(predchange[i]),
                'donor_probability_l1':float(abs(prob[i]-prob[donor[i]]).sum()),
                'margin':margin,'margin_bin':int(np.searchsorted(model['train_margin_quartiles'],margin,side='right'))})
        for pr in ('SHADOWSOCKS','VLESS'):
            ix=[i for i,r in enumerate(rows) if r['protocol']==pr];gg=[g for g in foldgroups if g['protocol']==pr]
            mu=s[ix].mean(0);total=float(((s[ix]-mu)**2).sum()/len(ix)/5)
            between=float(((sc[ix]-mu)**2).sum()/len(ix)/5);within=float((e[ix]**2).sum()/len(ix)/5)
            maxerr=max(maxerr,abs(total-between-within))
            if not np.isclose(total,between+within,atol=1e-10,rtol=1e-10):raise ValueError('Energy decomposition')
            summaries.append({'fold':f,'protocol':pr,'groups':24,'visits':96,'total_energy':total,
                'between_energy':between,'within_energy':within,'within_fraction':within/total if total else None,
                'dispersion_median':float(np.median([g['dispersion'] for g in gg])),
                'dispersion_iqr':np.quantile([g['dispersion'] for g in gg],[.25,.75]).tolist(),
                'dispersion_max':max(g['dispersion'] for g in gg),
                **{key:float(np.mean([g[key] for g in gg])) for key in ('all_four_same','pair_agreement','majority_fraction','center_agreement','cyclic_score_difference','donor_class_change','donor_probability_l1')}})
            for b in range(4):
                vv=[r for r in foldvisits if r['protocol']==pr and r['margin_bin']==b]
                bins.append({'fold':f,'protocol':pr,'margin_bin':b,'visits':len(vv),
                    **{k:float(np.mean([r[k] for r in vv])) if vv else None for k in ('score_difference','donor_class_change','donor_probability_l1')}})
            for relation,arm in [('true','F'),('wrong','G')]:
                state=read(old/'positive-fits/fits'/f'{f}-{name(relation,1)}.json');j=p['indices']
                a=np.asarray(state['mapping']['coef'])[j];b=np.asarray(state['mapping']['intercept'])[j]
                hat=((np.asarray(p['v'])*a+b)*p['c']+p['offset'])@wc.T
                hc=center_targets(hat,rows,rows);he=hat-hc
                inner=float((he[ix]*e[ix]).sum()/len(ix)/5);pe=float((he[ix]**2).sum()/len(ix)/5)
                residuals.append({'fold':f,'protocol':pr,'arm':arm,'true_visit_mse':float(((hat[ix]-s[ix])**2).sum()/len(ix)/5),
                    'true_center_mse':float(((hat[ix]-sc[ix])**2).sum()/len(ix)/5),'predicted_residual_energy':pe,
                    'true_residual_energy':within,'residual_inner_product':inner,
                    'residual_correlation':inner/np.sqrt(pe*within) if pe>0 and within>0 else None})
        group_rows+=foldgroups;visits+=foldvisits
    write_table(out/'groups.parquet',group_rows);write_table(out/'visits.parquet',visits)
    write_json(out/'fold-protocol-summary.json',summaries);write_json(out/'margin-bins.json',bins)
    write_json(out/'FG-training-residuals.json',residuals)
    write_json(out/'validation.json',{'passed':True,'group_contexts':len(group_rows),'train_appearances':len(visits),'max_identity_error':maxerr,'new_fits':0})
    seal(out,passed=True);print('Training score hierarchy complete',flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--config',default=str(CONFIG));a=p.parse_args();run(a.config)
