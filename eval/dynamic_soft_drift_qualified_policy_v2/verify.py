"""Independent endpoint, alias, score and immutable artifact closeout."""
from common import *

def run():
    verify_seal(OUT/'manifests/policy-complete.json');verify_seal(OUT/'manifests/models-complete.json');verify_seal(OUT/'predictions/complete.json')
    decisions=pd.read_parquet(OUT/'manifests/policy-decisions.parquet');endpoints=pd.read_parquet(OUT/'manifests/endpoints.parquet')
    preds=pd.read_parquet(OUT/'scores/labeled-predictions.parquet');scores=pd.read_parquet(OUT/'scores/scenarios.parquet')
    require(len(decisions)==180 and len(endpoints)==600 and len(preds)==14400,'Independent coverage')
    for d in decisions.to_dict('records'):
        ep=endpoints[endpoints.role_id.eq(d['role_id'])&endpoints.arm.eq(d['arm'])].iloc[0]
        if d['identity']:require(not ep.new_fit and ep.model_path==d['baseline_path'] and ep.model_sha256==d['baseline_sha256'],'Exact alias endpoint')
        else:require(ep.new_fit and d['enabled'],'Unqualified final fit')
    maxerr=0.;aliases=0;cols=[f'p{i}' for i in range(6)]+[f'l{i}' for i in range(6)]+['prediction']
    for (a,t,g),part in preds.groupby(['arm','target','group']):
        cm=np.zeros((6,6),dtype=np.int64)
        for y,z in zip(truths(part),part.prediction):cm[int(y),int(z)]+=1
        f=np.array([0. if cm[k].sum()+cm[:,k].sum()==0 else 2*cm[k,k]/(cm[k].sum()+cm[:,k].sum()) for k in range(6)])
        saved=scores[scores.arm.eq(a)&scores.target.eq(t)&scores.group.eq(g)].iloc[0]
        for key,value in [('F1_all',f.mean()),('F1_U',f[MASKS[g]].mean()),('F1_C',np.delete(f,MASKS[g]).mean())]:maxerr=max(maxerr,abs(float(value)-saved[key]))
    require(maxerr<1e-12,'Independent full-six-class F1 replay')
    for d in decisions[decisions.identity].to_dict('records'):
        a=preds[preds.role_id.eq(d['role_id'])&preds.arm.eq(d['arm'])].sort_values('visit_id');b=preds[preds.role_id.eq(d['role_id'])&preds.arm.eq(d['baseline_arm'])].sort_values('visit_id')
        require(np.array_equal(a[cols].to_numpy(),b[cols].to_numpy()),'Exact alias prediction check');aliases+=1
    for p,h in {**contract()['fixed_code'],**contract()['parent_metadata']}.items():checked(ROOT/p,h,'final-parent-lineage')
    for p,info in contract()['inputs'].items():checked(ROOT/p,info['sha256'],'final-training-asset')
    for p,info in contract()['assets'].items():checked(ROOT/p,info['sha256'],'final-baseline-asset')
    for p,h in contract()['pilot_files'].items():checked(ROOT/p,h,'final-pilot-asset')
    files={}
    roots=['manifests','audits','decisions','q-use','scales','trajectories','models','final-slots','predictions','scores','comparisons','tables','stages','value-cache','gradient-cache','feedback-logs']
    for root in roots:
        for p in (OUT/root).rglob('*'):
            if p.is_file() and p.name!='pending-trial.json' and not p.name.endswith('.tmp'):files[rel(p)]=sha(p)
    for p in [OUT/'ledger.json',OUT/'membership-audit.json',OUT/'ready.json']:
        if p.exists():files[rel(p)]=sha(p)
    for p,h in contract()['code'].items():files[p]=h;checked(ROOT/p,h,'final-policy-code')
    write(OUT/'verification.json',dict(passed=True,files=files,logical_endpoints=600,policy_decisions=180,predictions=14400,exact_aliases=aliases,independent_F1_max_error=maxerr,old_interrupted_read_log_complete=False,runtime_files_excluded_by_fixed_type=True))
    return sha(OUT/'verification.json')

