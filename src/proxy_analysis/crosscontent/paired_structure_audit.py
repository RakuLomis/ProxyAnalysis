"""Independent read-back audit for completed P5/P6; explicitly not a P7 completion gate."""
import argparse
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.special import expit

from .paired_structure_contract import CONFIG, verify, validate_complete, seal, read
from ..paired_information.prepare import table, digest
from ..reproducibility.preflight import write_json


def run(config=CONFIG):
    cfg,source,legacy,root=verify(config);out=root/'audit'/'p5-p6'
    if out.exists():validate_complete(out);return
    for name in ['p5-counts','p6-diagnostics','p7-models/engineering']:validate_complete(root/name)
    side={(r['session_id'],r['selection']):r for r in table(source/'side-summaries.parquet')}
    p5=table(root/'p5-counts/session-count-decomposition.parquet')
    members=read(root/'contract/manifest.json')
    for cohort,key in [('240','primary_ids'),('299','conservative_ids')]:
        rs=[r for r in p5 if r['cohort']==cohort]
        if {r['session_id'] for r in rs}!=set(members[key]) or len(rs)!=len(members[key])*6:
            raise ValueError('P5 membership failure')
    for r in p5:
        observed=side[r['session_id'],'observed'];data=side[r['session_id'],'nonempty']
        expected={}
        for s in ['pre','post']:
            n=observed[s]['packet_count'];d=data[s]['packet_count']
            runs=observed[s]['burst_count'];fr=data[s]['burst_count']
            expected[s]={'N_all':n,'N_data':d,'N_empty':n-d,'R_all':runs,'R_data':fr,'G_R':runs-fr}[r['metric']]
        if r['pre']!=expected['pre'] or r['post']!=expected['post'] or r['delta']!=expected['post']-expected['pre']:
            raise ValueError('Independent count reconstruction failure')
    feature_names=read(root/'contract/manifest.json')['feature_dictionary']
    margin_rows=table(root/'p6-diagnostics/margin-contributions.parquet')
    expected_predictions={};fits={};max_margin_error=0.;max_prob_error=0.
    for job in sorted((legacy/'jobs').iterdir()):
        fits.update({f['fit_id']:f for f in read(job/'fit-ledger.json')})
        for p in table(job/'predictions.parquet'):
            if p['arm']=='M0':expected_predictions[p['fit_id'],p['stage'],p['session_id']]=p
    if len(margin_rows)!=len(expected_predictions):raise ValueError('P6 row count mismatch')
    seen=set()
    for r in margin_rows:
        key=r['fit_id'],r['stage'],r['session_id']
        if key in seen:raise ValueError('Duplicate prediction')
        seen.add(key);expected=expected_predictions[key];state=fits[r['fit_id']]['state']
        s=side[r['session_id'],'observed']['post'];names=feature_names[r['representation']]
        values=[s.get(k) for k in names[:14]]
        if len(names)>14:
            for h in ['length_hist','iat_hist']:
                v=np.asarray(s[h]);values.extend(v/v.sum() if v.sum() else np.full(len(v),np.nan))
            values.extend(s['curve'] if s['curve'] is not None else [np.nan]*101)
        x=np.array(values,dtype=float);x[np.isnan(x)]=np.array(state['imputer_statistics'])[np.isnan(x)]
        z=(x-state['scaler_mean'])/state['scaler_scale']
        w=np.array(state['coef']);b=np.array(state['intercept']);scores=w@z+b
        if len(scores)==1:
            p1=float(expit(scores[0]));p=np.array([1-p1,p1]);logits=np.array([-scores[0]/2,scores[0]/2])
            w=np.vstack([-w/2,w/2]);b=np.r_[-b/2,b/2]
        else:
            logits=scores;v=np.exp(scores-max(scores));p=v/v.sum()
        max_prob_error=max(max_prob_error,float(max(abs(p-np.array(expected['probabilities'])))))
        y,c=r['truth'],r['competitor'];m=float(logits[y]-logits[c])
        max_margin_error=max(max_margin_error,abs(m-r['margin']))
        for name,start,end in [('scalar',0,14),('length',14,33),('IAT',33,56),('curve',56,157)]:
            if start>=len(z):continue
            part=float(np.dot((w[y]-w[c])[start:end],z[start:end]))
            if not np.isclose(part,r[name],atol=1e-9):raise ValueError('Family contribution mismatch')
        if not np.isclose(b[y]-b[c],r['intercept'],atol=1e-9):raise ValueError('Intercept mismatch')
    if seen!=set(expected_predictions) or max_prob_error>1e-10 or max_margin_error>1e-8:
        raise ValueError('Independent model reconstruction failure')
    out.mkdir(parents=True)
    write_json(out/'validation.json',{'passed':True,'scope':'P5_P6_only',
        'count_rows':len(p5),'prediction_rows':len(margin_rows),
        'max_probability_error':max_prob_error,'max_margin_error':max_margin_error,
        'new_fits':0,'raw_pcap_parses':0,'P7_formal_complete':False,'code_sha256':digest(Path(__file__))})
    seal(out,passed=True);print('Independent P5/P6 audit passed',flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--config',default=str(CONFIG));run(p.parse_args().config)
