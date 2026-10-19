"""Superseding contract audit. Retains old acceptance records; performs no training."""
from common import *
from classifier import within_budget

def run():
    hashes=code_seal('P1-contract-audit-02');q=pd.read_parquet(OUT/'tests/P1-head-quality.parquet');rows=[]
    for _,v in q.iterrows():
        valid=within_budget(v)
        if not valid:rows.append(dict(role_id=v.role_id,arm=v.arm,candidate=v.candidate,gamma=v.gamma,
            iterations=int(v.iterations),evaluations=int(v.evaluations),original_gradient_max=float(v.original_gradient_max),
            original_record_passed=bool(v.passed),effective_contract_passed=False,reason='cumulative_iteration_budget_exhausted'))
    b=read(OUT/'budget.json');buckets=[]
    for v in b['items']:
        if v['kind']!='dynamic-Adam':continue
        lrs=sorted({j['recipe']['lr'] for j in v['batch_jobs']})
        buckets.append(dict(capability=v['capability'],paths=v['paths'],lrs=lrs,uniform_lr=len(lrs)==1,
            seconds=v['seconds'],per_model_optimizer_kept_its_configured_lr=True))
    dummy=dict(iterations=1999,evaluations=9999,settings=dict(max_iter=2000,max_eval=10000))
    require(within_budget(dummy) and not within_budget(dict(dummy,iterations=2000)) and not within_budget(dict(dummy,evaluations=10000)),'Strict budget boundary checks')
    from engine import Engine
    try:Engine([], [dict(recipe=dict(lr=.0003)),dict(recipe=dict(lr=.001))], [], streams=True)
    except RuntimeError as e:require('One learning rate' in str(e),'Mixed-lr guard did not reject before CUDA work')
    else:raise RuntimeError('Mixed-lr guard was not effective')
    out=dict(version=2,engineering_passed=False,budget_passed=False,formal_complete=False,H_scored=False,source_query_scored=False,
        numerical_value_gradient_gates_passed=int(q.passed.sum()),heads_fitted=len(q),strict_head_budget_qualified=len(q)-len(rows),
        unqualified_heads=rows,buckets=buckets,mixed_lr_paths=sum(v['paths'] for v in buckets if not v['uniform_lr']),
        issues=['head accept/reuse path originally omitted cumulative budget rejection','scheduler originally mixed two lrs per bucket'],
        no_retraining=True,no_loss_permission_threshold_change=True,
        code_guards_fixed=['cumulative max_iter/max_eval rejected even when terminal gradient is small','old cached heads rechecked against same budgets',
            'scheduler partitions by row shape and lr before chunking, Engine independently rejects mixed lr',
            'mixed-lr old trajectories cannot be silently reused under corrected scheduler'],
        old_records_retained=['completion.json','manifests/P1-numeric-complete.json','manifests/P1-closeout.json','tests/P1-head-quality.parquet'],
        old_source_guard_stop_retained=True,cost_forecast_is_old_backend_diagnostic_not_corrected_backend_acceptance=True,
        activity_used_seconds=b['used_seconds'],status='stop_P1_contract_and_budget_confirmation_required')
    immutable(OUT/'tests/P1-contract-gate-audit-02.json',out)
    immutable(OUT/'completion-revision-02.json',dict(**out,supersedes=rel(OUT/'completion.json'),previous_completion_sha256=sha(OUT/'completion.json')))
    immutable(OUT/'completion-current.json',dict(path=rel(OUT/'completion-revision-02.json'),sha256=sha(OUT/'completion-revision-02.json')))
    codecheck(hashes);progress(out['status'],unqualified_heads=len(rows),mixed_lr_paths=out['mixed_lr_paths'],query_reads=0)

if __name__=='__main__':run()
