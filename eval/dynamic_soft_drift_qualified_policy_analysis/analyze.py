"""Read-only analysis of sealed predictions and terminal trajectories; no fitting."""
from pathlib import Path
import hashlib
import json
import time
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'outputs/dynamic-soft-drift-qualified-policy-business-20261013/run-02'
OUT=ROOT/'outputs/dynamic-soft-drift-qualified-policy-analysis-20261014/run-01'
MASKS={'G0':[2,4],'G1':[0,3],'G2':[1,5]}

def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def require(c,s):
    if not c:raise RuntimeError(s)
def write(name,value):
    (OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def save(name,d):d.to_parquet(OUT/(name+'.parquet'),index=False)

def main():
    require(not OUT.exists(),'Refuse analysis overwrite');OUT.mkdir(parents=True);begin=time.perf_counter()
    completion=read(SOURCE/'completion.json');require(completion['passed'] and completion['formal_complete'] and completion['H_scored'],'Not a complete business run')
    require(sha(SOURCE/'verification.json')==completion['verification_sha256'],'Verification seal changed')
    verification=read(SOURCE/'verification.json');require(verification['passed'],'Verification failed')
    rs=read(SOURCE/'report-seal.json');require(sha(ROOT/rs['path'])==rs['sha256'],'Sealed report changed')
    c=read(SOURCE/'manifests/experiment-contract.json');require(sha(SOURCE/'manifests/experiment-contract.json')==read(SOURCE/'manifests/seal.json')['contract_sha256'],'Contract changed')
    # Recheck all decision/model/prediction seals and result tables, not every 40k solver log.
    checked={}
    for name in ['manifests/policy-complete.json','manifests/models-complete.json','predictions/complete.json']:
        d=read(SOURCE/name);require(d['passed'],'Stage seal failed '+name);checked.update(d['files'])
    for path,h in verification['files'].items():
        if any(path.startswith(str(SOURCE.relative_to(ROOT)).replace('\\','/')+'/'+sub) for sub in ['scores/','comparisons/','audits/','scales/','stages/']):checked[path]=h
    checked.update(c['code']);checked.update(c['fixed_code']);checked.update(c['pilot_files'])
    for path,h in checked.items():require(sha(ROOT/path)==h,'Changed critical artifact '+path)
    decisions=pd.read_parquet(SOURCE/'manifests/policy-decisions.parquet')
    endpoints=pd.read_parquet(SOURCE/'manifests/endpoints.parquet')
    data=pd.read_parquet(SOURCE/'scores/labeled-predictions.parquet')
    pooled=pd.read_parquet(SOURCE/'scores/pooled.parquet');targets=pd.read_parquet(SOURCE/'scores/targets.parquet')
    classes=pd.read_parquet(SOURCE/'scores/classes.parquet');flips=pd.read_parquet(SOURCE/'scores/error-flips.parquet')
    require(len(decisions)==180 and len(endpoints)==600 and len(data)==14400,'Coverage changed')
    label_names=list(c.get('labels',[]))
    if not label_names:
        label_names=['bing_search','mdn_docs','github_repo','wikipedia_article','youtube_search','youtube_video']
    # label_id is the established string identifier, not a feature input.
    mapping=classes[['label','label_index']].drop_duplicates().set_index('label').label_index.to_dict()
    yy=data.label_id.map(mapping);require(not yy.isna().any(),'Unmapped labels')
    data['truth']=yy.astype(int);data['scope']=['U' if y in MASKS[g] else 'C' for y,g in zip(data.truth,data.group)]
    pc=[f'p{i}' for i in range(6)];lc=[f'l{i}' for i in range(6)];maxerr=0.;scenes=[]
    for (arm,target,group),d in data.groupby(['arm','target','group']):
        cm=np.zeros((6,6),np.int64)
        np.add.at(cm,(d.truth.to_numpy(),d.prediction.to_numpy()),1)
        den=cm.sum(0)+cm.sum(1);f=np.divide(2*np.diag(cm),den,out=np.zeros(6),where=den>0)
        u=d.scope.eq('U').to_numpy();y=d.truth.to_numpy();ce=-d[lc].to_numpy()[np.arange(len(d)),y];br=((d[pc].to_numpy()-np.eye(6)[y])**2).sum(1)
        m=dict(arm=arm,target=target,group=group,F1_U=float(f[MASKS[group]].mean()),F1_C=float(np.delete(f,MASKS[group]).mean()),F1_all=float(f.mean()),CE_U=float(ce[u].mean()),CE_C=float(ce[~u].mean()),Brier_U=float(br[u].mean()),Brier_C=float(br[~u].mean()))
        reference=pd.read_parquet(SOURCE/'scores/scenarios.parquet');saved=reference[reference.arm.eq(arm)&reference.target.eq(target)&reference.group.eq(group)].iloc[0]
        for k in ['F1_U','F1_C','F1_all','CE_U','CE_C','Brier_U','Brier_C']:maxerr=max(maxerr,abs(m[k]-saved[k]))
        scenes.append(m)
    require(maxerr<1e-12,'Independent score replay')
    activation=decisions.groupby(['arm','target']).agg(endpoints=('enabled','size'),enabled=('enabled','sum'),fallback=('fallback','sum')).reset_index();activation['enabled_rate']=activation.enabled/activation.endpoints
    save('activation-by-deployment',activation)
    save('statuses',decisions.groupby(['arm','original_stop']).size().rename('count').reset_index())
    metric_cols=['F1_U','F1_C','F1_all','CE_U','CE_C','Brier_U','Brier_C']
    deltas=[]
    for arm,ref in [('QP','P-small'),('QT','P-small'),('QG','G-small'),('QP','QT'),('QP','QG'),('QP','S')]:
        for target in sorted(targets.target.unique()):
            a=targets[targets.arm.eq(arm)&targets.target.eq(target)].iloc[0];b=targets[targets.arm.eq(ref)&targets.target.eq(target)].iloc[0]
            deltas.append(dict(arm=arm,reference=ref,target=target,**{k:float(a[k]-b[k]) for k in metric_cols}))
    save('deployment-deltas',pd.DataFrame(deltas))
    cu=flips.groupby(['reference','target','scope'])[['repaired','introduced','prediction_changed']].sum().reset_index();cu['net_repaired']=cu.repaired-cu.introduced
    save('error-flips-by-deployment-scope',cu);save('error-flips-total',cu.groupby(['reference','scope'])[['repaired','introduced','prediction_changed','net_repaired']].sum().reset_index())
    # Full six-class denominators retained; each class's U status occurs in one registered mask.
    business=classes[classes.uncovered].groupby(['arm','label','label_index']).F1.mean().reset_index()
    bd=[]
    for arm,ref in [('QP','P-small'),('QP','QT'),('QP','S'),('QG','G-small')]:
        a=business[business.arm.eq(arm)].set_index('label');b=business[business.arm.eq(ref)].set_index('label')
        for label in a.index:bd.append(dict(arm=arm,reference=ref,label=label,F1=float(a.loc[label,'F1']),reference_F1=float(b.loc[label,'F1']),delta_F1=float(a.loc[label,'F1']-b.loc[label,'F1'])))
    save('business-deltas',pd.DataFrame(bd))
    # Expand optimization from sealed C/source trajectories, without changing eligibility.
    closeout=[];qrows=[];role_metrics=[]
    for d in decisions.to_dict('records'):
        root=(ROOT/d['trajectory_result_path']).parent;states=pd.read_parquet(root/'states.parquet');trials=pd.read_parquet(root/'trials.parquet');r=read(root/'result.json');a,b=states.iloc[0],states.iloc[-1]
        require(int(b.state)==d['accepted_updates'] and len(states)==d['accepted_updates']+1,'Terminal trajectory membership')
        for p in [root/'states.parquet',root/'trials.parquet']:
            require(sha(p)==read(SOURCE/'manifests/policy-complete.json')['files'][str(p.relative_to(ROOT)).replace('\\','/')],'Trajectory changed')
        J0=min(float(a.L_f),float(a.L_v));Jend=max(float(b.L_f),float(b.L_v));improvement=J0-Jend
        desc=trials[trials.accepted];require(len(desc)==d['accepted_updates'] and desc.value_pass.all() and desc.direction_pass.all(),'Accepted update gate replay')
        row=dict(role_id=d['role_id'],arm=d['arm'],target=d['target'],group=d['group'],outer=d['outer'],enabled=d['enabled'],fallback=d['fallback'],status=d['original_stop'],reused_f0=d['reused_f0'],updates=d['accepted_updates'],trials=d['trial_evaluations'],J0_f=float(a.L_f),J0_v=float(a.L_v),Jend_f=float(b.L_f),Jend_v=float(b.L_v),Q0_f=float(a.Q_f),Qend_f=float(b.Q_f),shrink_end=float(b.shrink),penalty_end=float(b.penalty),PG0_f=float(a.PG_f),PGend_f=float(b.PG_f),PG0_v=float(a.PG_v),PGend_v=float(b.PG_v),PG_ratio_f=float(b.PG_f/a.PG_f) if a.PG_f else None,PG_ratio_v=float(b.PG_v/a.PG_v) if a.PG_v else None,improvement=improvement,total_decreased=improvement>0,Q_change=float(b.Q_f-a.Q_f),seconds=float(d['seconds']))
        closeout.append(row)
        for j,value in enumerate(d['q_use']):qrows.append(dict(role_id=d['role_id'],arm=d['arm'],target=d['target'],block=j,q_use=float(value),q_end=float(d['q_end'][j]),enabled=d['enabled']))
        pred=data[data.role_id.eq(d['role_id'])&data.arm.eq(d['arm'])];ref=data[data.role_id.eq(d['role_id'])&data.arm.eq(d['baseline_arm'])]
        pair=pred.merge(ref[['visit_id','prediction']].rename(columns={'prediction':'reference_prediction'}),on='visit_id',validate='one_to_one')
        for scope,part in pair.groupby('scope'):
            repaired=((part.prediction==part.truth)&(part.reference_prediction!=part.truth)).sum();introduced=((part.prediction!=part.truth)&(part.reference_prediction==part.truth)).sum()
            role_metrics.append(dict(role_id=d['role_id'],arm=d['arm'],target=d['target'],group=d['group'],outer=d['outer'],scope=scope,enabled=d['enabled'],fallback=d['fallback'],visits=len(part),repaired=int(repaired),introduced=int(introduced),changed=int((part.prediction!=part.reference_prediction).sum()),net_repaired=int(repaired-introduced)))
        if d['identity']:
            pred=pred.sort_values('visit_id');ref=ref.sort_values('visit_id');require(np.array_equal(pred[pc+lc+['prediction']].to_numpy(),ref[pc+lc+['prediction']].to_numpy()),'Exact fallback mismatch')
    closeout=pd.DataFrame(closeout);save('optimizer-closeout-180',closeout);save('q-use-by-block',pd.DataFrame(qrows));save('role-error-flips',pd.DataFrame(role_metrics))
    opt=closeout.groupby('arm').agg(trajectories=('arm','size'),total_decreased=('total_decreased','sum'),mean_J_change=('improvement','mean'),mean_Q_change=('Q_change','mean'),median_PG_ratio=('PG_ratio_f','median'),median_end_PG=('PGend_f','median'),updates=('updates','sum'),trials=('trials','sum')).reset_index();save('optimization-summary',opt)
    save('enabled-error-flips',pd.DataFrame(role_metrics).groupby(['arm','enabled','scope'])[['visits','repaired','introduced','changed','net_repaired']].sum().reset_index())
    # Recalculate existing bootstrap quantiles; do not resample or invent a new family.
    boot=np.load(SOURCE/'comparisons/bootstrap.npz',allow_pickle=False);arms=list(boot['arms']);primary=read(SOURCE/'comparisons/primary.json')
    for x in primary['comparisons']:
        values=boot['F1_U'][:,arms.index('QP')]-boot['F1_U'][:,arms.index(x['reference'])];ci=np.quantile(values,[.05/14,1-.05/14]);require(np.max(np.abs(ci-np.array(x['CI_99_285714'])))<1e-12,'Bootstrap quantiles changed')
    write('verification.json',dict(passed=True,checked_critical_files=len(checked),source_verification_sha256=completion['verification_sha256'],all_solver_logs_rehashed=False,independent_metrics_max_error=maxerr,bootstrap_quantiles_replayed=True,exact_fallback_endpoints=int(decisions.identity.sum()),new_model_fits=0,old_assets_modified=False,seconds=time.perf_counter()-begin))
    write('summary.json',dict(completion=completion,activation=activation.to_dict('records'),statuses=decisions.groupby(['arm','original_stop']).size().rename('count').reset_index().to_dict('records'),optimization=opt.to_dict('records'),models=read(SOURCE/'manifests/models-complete.json')|{'files':'omitted'},primary=primary,C_guard=read(SOURCE/'comparisons/C-cost-guard.json'),flips=cu.groupby(['reference','scope'])[['repaired','introduced','prediction_changed','net_repaired']].sum().reset_index().to_dict('records')))
    print(json.dumps(read(OUT/'summary.json'),ensure_ascii=False,indent=2));print(read(OUT/'verification.json'))

if __name__=='__main__':main()
