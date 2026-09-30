"""Engineering R0 parity gate only; failure requires user decision before formal fits."""
import argparse
from pathlib import Path
import warnings

import numpy as np
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.exceptions import ConvergenceWarning

from .paired_structure_contract import CONFIG, verify, seal, validate_complete, read
from .business_representations import matrix
from .paired_constraint_objective import fit, probability, objective, moment, donor_indices
from ..paired_information.prepare import table, digest
from ..reproducibility.preflight import write_json, write_table


def run(config=CONFIG):
    cfg,source,legacy,root=verify(config);out=root/'p7-models'/'engineering'
    if out.exists(): validate_complete(out);return
    lookup={r['session_id']:r for r in table(source/'side-summaries.parquet') if r['selection']=='observed'}
    results=[];ledger=[];maps=[]
    for task in cfg['tasks']:
        for protocol in cfg['protocols']:
            job=legacy/'jobs'/f'{task}-{protocol}-0-scalar14'
            validate_complete(job);mem=read(job/'membership.json')
            train=[lookup[s] for s in mem['train_ids']];test=[lookup[s] for s in mem['test_ids']]
            if {r['content_id'] for r in train}&{r['content_id'] for r in test}:raise ValueError('Content overlap')
            if any(r['protocol']!=protocol for r in train):raise ValueError('Target in source')
            labels=sorted({r['label_id'] for r in train});y=np.array([labels.index(r['label_id']) for r in train]);k=len(labels)
            imputer=SimpleImputer(strategy='median',keep_empty_features=True)
            xi=imputer.fit_transform(matrix(train,'post','scalar14'));scaler=StandardScaler().fit(xi)
            x=scaler.transform(xi);xt=scaler.transform(imputer.transform(matrix(test,'post','scalar14')))
            a=scaler.transform(imputer.transform(matrix(train,'pre','scalar14')))
            raw,cov=moment(x-a)
            for shift in cfg['wrong_shifts']:
                donor=donor_indices(train,shift)
                maps.extend({'task':task,'protocol':protocol,'outer_fold':0,'shift':shift,
                    'receiver':r['session_id'],'donor':train[donor[i]]['session_id']} for i,r in enumerate(train))
            context={'task':task,'protocol':protocol,'outer_fold':0}
            state=fit(x,y,k,cov,0.,cfg);p=probability(xt,state)
            ledger.append({**context,'kind':'new_R0','state':state,'train_ids':mem['train_ids'],
                'imputer_statistics':imputer.statistics_.tolist(),'scaler_mean':scaler.mean_.tolist(),
                'scaler_scale':scaler.scale_.tolist(),'C_raw':raw.tolist(),'C_normalized':cov.tolist()})
            with warnings.catch_warnings():
                warnings.simplefilter('error',ConvergenceWarning)
                reference=LogisticRegression(C=cfg['model_C'],solver='lbfgs',tol=1e-12,max_iter=10000).fit(x,y)
            refstate={'coef':reference.coef_.tolist(),'intercept':reference.intercept_.tolist()}
            ledger.append({**context,'kind':'strict_sklearn_R0','state':refstate,'train_ids':mem['train_ids']})
            old=next(f for f in read(job/'fit-ledger.json') if f['arm']=='post')
            oldstate=old['state']; oldp=probability(xt,oldstate)
            saved={r['session_id']:r for r in table(job/'predictions.parquet') if r['arm']=='M0' and r['stage']=='student'}
            if max(np.max(abs(oldp[i]-saved[r['session_id']]['probabilities'])) for i,r in enumerate(test))>1e-10:
                raise ValueError('Legacy preprocessing mismatch')
            def diag(s):
                t=np.column_stack([np.asarray(s['coef']),np.asarray(s['intercept'])]).ravel()
                val,g,_=objective(t,x,y,k,cov,0.,cfg['model_C']);return val,float(max(abs(g)))
            ov,og=diag(oldstate);rv,rg=diag(refstate)
            strict_error=float(np.max(abs(p-reference.predict_proba(xt))))
            historical_error=float(np.max(abs(p-oldp)))
            results.append({**context,'strict_probability_error':strict_error,'historical_probability_error':historical_error,
                'strict_parity_passed':strict_error<=cfg['baseline_probability_tolerance'],
                'historical_parity_passed':historical_error<=cfg['baseline_probability_tolerance'],
                'new_objective':state['objective'],'legacy_objective':ov,'strict_objective':rv,
                'new_gradient_inf':state['gradient_inf'],'legacy_gradient_inf':og,'strict_gradient_inf':rg,
                'historical_label_changes':int(np.sum(p.argmax(axis=1)!=oldp.argmax(axis=1))),
                'n_test':len(test)})
    out.mkdir(parents=True)
    write_json(out/'baseline-parity.json',results);write_json(out/'fit-ledger.json',ledger)
    write_table(out/'donor-maps.parquet',maps)
    passed=all(r['strict_parity_passed'] and r['historical_parity_passed'] for r in results)
    write_json(out/'gate.json',{'passed':passed,'fresh_engineering_fits':len(ledger),'formal_fits':0,
        'requires_confirmation':not passed,'code_sha256':{
            str(Path(__file__)):digest(Path(__file__)),
            str(Path(__file__).with_name('paired_constraint_objective.py')):digest(Path(__file__).with_name('paired_constraint_objective.py'))},
        'reason':None if passed else 'Baseline probability difference exceeds frozen tolerance; inspect objective and gradients before approval'})
    seal(out,passed=passed)
    print({'P7_engineering_passed':passed,'engineering_fits':len(ledger),'results':results},flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--config',default=str(CONFIG));run(p.parse_args().config)
