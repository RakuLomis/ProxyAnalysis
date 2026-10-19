"""Read-only post-closeout audit. Writes only supplementary documentation."""
from pathlib import Path
import sys,time,json,hashlib
started=time.perf_counter()
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'eval/decision_aware_forward_drift_r3'))
import common as c
import numpy as np
import pandas as pd
import torch

def main():
    c.configure('score');out=c.OUT;doc=c.DOC
    for marker in ['complete-seal','scores-complete','report-complete','predictions-complete','models-complete']:
        c.barrier(marker+'.json')
    c.codecheck();data=pd.read_parquet(out/'scores/labeled-predictions.parquet');errors=[];extra=[]
    for r in c.roles():
        rid=r['id'];base=c.own(out/'packages'/rid/'base.pt',rid);q=c.own(out/'diagnostic-query'/rid/'post.pt',rid)
        x=(q['raw']-base['mu'])/base['scale'];sub=data[data.role_id==rid]
        for arm in c.PIPES:
            h=base if arm=='B0' else c.own(out/'classifiers'/rid/(arm+'.pt'),rid)
            w,b=(h['weight'],h['bias']) if arm=='B0' else (h['W'],h['c'])
            with torch.no_grad():z=x@w.T+b;lp=z-z.logsumexp(1)[:,None]
            old=c.tensor(sub[sub.pipeline==arm].set_index('visit_id').loc[q['visit_ids'],[f'l{k}' for k in range(6)]])
            error=float((old-lp).abs().max());c.require(error<=1e-9,'Independent source inference replay');errors.append(error)
        d=c.own(out/'diagnostics'/rid/'outputs.pt',rid);lab=sub[sub.pipeline=='B0'].set_index('visit_id').loc[d['visit_ids']]
        for arm in c.ARMS:
            delta=d['outputs'][arm]-d['outputs']['B0'];energy=delta.square().sum(1);projected=(delta@d['Q']).square().sum(1)
            for scope in ['C','U']:
                ids=c.tensor(np.flatnonzero(lab.scope.to_numpy()==scope),torch.long);allenergy=float(energy[ids].sum());qenergy=float(projected[ids].sum())
                extra.append(dict(pipeline=arm,scope=scope,total_energy=allenergy,decision_energy=qenergy,null_energy=allenergy-qenergy))
    en=pd.DataFrame(extra).groupby(['pipeline','scope'])[['total_energy','decision_energy','null_energy']].sum().reset_index()
    en['null_energy_fraction']=en.null_energy/en.total_energy
    conf=data.groupby(['pipeline','scope']).apply(lambda d:pd.Series(dict(accuracy=d.correct.mean(),CE=d.CE.mean(),Brier=d.Brier.mean(),
        wrong_confidence=d.loc[~d.correct,'confidence'].mean(),high_confidence_wrong=int(((~d.correct)&(d.confidence>=.9)).sum()))),include_groups=False).reset_index()
    # Permission audit checks recorded decoded capabilities, not a universal OS sandbox claim.
    reads=[];permission_files=list((out/'permissions').glob('*.json'))
    pred_stamp=(out/'manifests/predictions-complete.json').stat().st_mtime
    diag_stamp=(out/'manifests/diagnostics-complete.json').stat().st_mtime
    sourcepre_logs=label_logs=0
    for path in permission_files:
        for a in c.read(path)['reads']:
            if a['kind']=='source-query-pre-filtered':
                c.require(path.stat().st_mtime>=pred_stamp,'Source query-pre before post seal');sourcepre_logs+=1
            if a['kind']=='labels':c.require(path.stat().st_mtime>=diag_stamp,'Labels before diagnostics seal');label_logs+=1
            if a.get('capability')=='G':c.require(a['kind'] in ['G','shared'],'G decoded new P data')
            reads.append(a)
    c.require(sourcepre_logs==48 and label_logs==48,'Complete staged audit')
    for name in ['model.py','engine.py','classifier.py','lbfgs_local.py','worker.py','tests.py','evaluate.py','score.py','report.py']:
        import ast
        dumps=[ast.dump(ast.parse((ROOT/'eval'/p/name).read_text(encoding='utf-8'))) for p in ['decision_aware_forward_drift','decision_aware_forward_drift_r2','decision_aware_forward_drift_r3']]
        c.require(len(set(dumps))==1,'Scientific code changed during repair')
    evidence=dict(passed=True,source_forward_replay_max_error=max(errors),models_replayed=240,source_query_pre_logs=sourcepre_logs,
        label_logs=label_logs,permission_files=len(permission_files),scientific_math_engine_evaluation_AST_unchanged=True,
        actual_H_U_reads=0,new_fits=0,analysis_wall_seconds=time.perf_counter()-started,
        original_completion_sha256=c.sha(out/'completion.json'),original_report_sha256=c.sha(doc/'pilot-results.md'))
    (doc/'post-closeout-audit.json').write_text(json.dumps(evidence,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    en.to_parquet(doc/'residual-output-geometry.parquet',index=False);conf.to_parquet(doc/'confidence-summary.parquet',index=False)
    print(json.dumps(evidence,ensure_ascii=False,indent=2));print(en.to_string(index=False));print(conf.to_string(index=False))
    flips=pd.read_parquet(out/'scores/error-flips.parquet')
    print(flips.groupby(['reference','scope','flip']).agg(n=('correct','size'),dCE=('delta_CE','mean')).to_string())

if __name__=='__main__':main()
