"""Read-only independent metric replay and OR1 failure attribution."""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'outputs/output-orthogonal-readout-round1-20261015/run-01'
PC=[f'p{i}' for i in range(6)];LC=[f'l{i}' for i in range(6)]

def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def maximum(x):return float(np.max(np.abs(x)))

def main():
    assert read(OUT/'completion.json')['passed']
    c=read(OUT/'manifests/contract.json')
    for path,h in c['historical'].items():assert sha(ROOT/path)==h,path
    for path,info in c['sources'].items():assert sha(ROOT/path)==info['sha256'],path
    code=read(OUT/'manifests/code.json')
    for path,h in code['files'].items():assert sha(ROOT/path)==h,path
    d=pd.read_parquet(OUT/'predictions/calibrated.parquet')
    scored=pd.read_parquet(OUT/'scores/rows.parquet')
    endpoint=read(OUT/'scores/endpoints.json');summary=read(OUT/'scores/summary.json')
    idx={(v['role_id'],v['pipeline'],v['seed']):v for v in endpoint}
    metricerror=0.;classification_changes=0;audited=[];counts=[]
    for ri,r in enumerate(c['roles']):
        labels=pd.read_parquet(OUT/f'calibration/packages/r{ri:02d}/scoring-labels.parquet')
        z=d[d.role_id.eq(r['id'])].merge(labels[['visit_id','y']],on='visit_id',validate='many_to_one')
        for (pipe,seed),part in z.groupby(['pipeline','seed']):
            y=part.y.to_numpy(int);u=np.isin(y,r['missing'])
            raw_pred=part[['raw_'+k for k in PC]].to_numpy().argmax(1)
            for phase,pcols,lcols in [('raw',['raw_'+k for k in PC],['raw_'+k for k in LC]),('calibrated',PC,LC)]:
                p,lp=part[pcols].to_numpy(),part[lcols].to_numpy();pred=p.argmax(1)
                cm=np.zeros((6,6),int)
                np.add.at(cm,(y,pred),1)
                f1=np.array([0. if cm[k].sum()+cm[:,k].sum()==0 else 2*cm[k,k]/(cm[k].sum()+cm[:,k].sum()) for k in range(6)])
                ce=-lp[np.arange(len(y)),y];br=np.sum((p-np.eye(6)[y])**2,1)
                values=dict(F1_all=f1.mean(),F1_U=f1[r['missing']].mean(),F1_C=np.delete(f1,r['missing']).mean(),
                     CE_all=ce.mean(),CE_U=ce[u].mean(),CE_C=ce[~u].mean(),Brier=br.mean(),Brier_U=br[u].mean(),Brier_C=br[~u].mean(),accuracy=(pred==y).mean())
                target=idx[(r['id'],pipe,int(seed))][phase]
                metricerror=max(metricerror,max(abs(float(v)-target[k]) for k,v in values.items()))
                assert cm.tolist()==target['confusion_matrix']
                if phase=='calibrated':
                    classification_changes+=int((pred!=raw_pred).sum())
                    for split,mask in [('U',u),('C',~u)]:
                        counts.append(dict(role_id=r['id'],pipeline=pipe,seed=int(seed),split=split,n=int(mask.sum()),
                            correct=int(((pred==y)&mask).sum()),C_false_to_U=int(((~u)&(pred!=y)&np.isin(pred,r['missing'])).sum())))
            audited.append((r['id'],pipe,int(seed)))
    assert len(audited)==336 and metricerror<1e-14 and classification_changes==0
    counts=pd.DataFrame(counts);accuracy=[]
    for (pipe,split),part in counts.groupby(['pipeline','split']):
        accuracy.append(dict(pipeline=pipe,split=split,correct=int(part.correct.sum()),n=int(part.n.sum()),
                             accuracy=float(part.correct.sum()/part.n.sum()),C_false_to_U=int(part.C_false_to_U.sum())))
    retained=pd.read_parquet(OUT/'scores/old-P-repair-retention.parquet')
    assert retained[retained.split.eq('U')].old_repaired.sum()==5
    assert retained[retained.split.eq('U')].old_repair_retained.sum()==5
    flipped=[]
    for (split,dep,content,truth,old,new),z in retained[retained.old_P_prediction.ne(retained.OR_P_prediction)].groupby(
            ['split','query_deployment','content_id','truth','old_P_prediction','OR_P_prediction']):
        flipped.append(dict(split=split,query_deployment=dep,content_id=content,truth=int(truth),old_prediction=int(old),
                            new_prediction=int(new),n=len(z),unique_visits=z.visit_id.nunique()))
    train=[read(p) for p in (OUT/'fit-logs').rglob('*.json')]
    geometry=read(OUT/'diagnostics/raw-geometry.json');temps=read(OUT/'calibration/temperatures-new.json')
    byarm=[]
    for arm in c['arms']:
        gg=[v for v in geometry if v['arm']==arm];tt=[v for v in temps if v['pipeline']==arm]
        byarm.append(dict(arm=arm,base_centered_norm=np.mean([v['base_centered_norm'] for v in gg]).item(),
            final_centered_norm=np.mean([v['final_centered_norm'] for v in gg]).item(),delta_RMS=np.mean([v['delta_RMS'] for v in gg]).item(),
            T_min=min(v['temperature'] for v in tt),T_median=float(np.median([v['temperature'] for v in tt])),
            T_max=max(v['temperature'] for v in tt),T1=sum(v['status']=='T1' for v in tt),T5=sum(v['status']=='T5' for v in tt)))
    reference=next(v for v in summary['pipelines'] if v['pipeline']=='OR-P')
    base=next(v for v in summary['pipelines'] if v['pipeline']=='base')
    old=next(v for v in summary['pipelines'] if v['pipeline']=='P_eta0p01')
    differences={name:{k:reference['calibrated'][k]-v['calibrated'][k] for k in reference['calibrated']}
                 for name,v in [('base',base),('ordinary_P',old)]}
    result=dict(passed=True,independent_metric_max_error=metricerror,endpoints_audited=336,
        calibrated_class_changes=classification_changes,source_unique_visits=int(d.visit_id.nunique()),
        source_unique_contents=int(d.content_id.nunique()),old_inputs_unchanged=True,CUDA_code_unchanged=True,
        classifier_fits=0,G_fits=0,temperature_fits=0,H_reads=0,actual_U_reads=0,
        max_original_gradient=max(v['max_original_gradient'] for v in train),
        max_training_radial_error=max(v['geometry']['max_relative_radial_error'] for v in train),
        max_query_radial_error=max(v['max_relative_radial_error'] for v in geometry),
        training_near_zero_rows=sum(v['geometry']['near_zero_rows'] for v in train),
        query_near_zero_exposures=sum(v['near_zero_rows'] for v in geometry),
        by_arm=byarm,accuracy_by_split=accuracy,old_P_class_changes=flipped,differences=differences,
        code_sha256=sha(Path(__file__)))
    with (OUT/'audits/independent-score-analysis.json').open('x',encoding='utf-8') as f:
        json.dump(result,f,indent=2,sort_keys=True,ensure_ascii=False);f.write('\n')
    print(json.dumps({k:result[k] for k in ['passed','independent_metric_max_error','source_unique_visits','source_unique_contents','differences','by_arm']},indent=2))
    print(pd.DataFrame(accuracy).to_string(index=False))

if __name__=='__main__':main()
