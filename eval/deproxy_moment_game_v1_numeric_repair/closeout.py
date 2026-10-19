"""Metadata-only engineering closeout; actual query/H/U are never decoded."""
from common import *

def closeout(partial=False):
    configure('coordinator');begin('R5-closeout')
    try:
        paths=list((OUT/'R1').rglob('head.quality.json'))
        r1=[read(p) for p in paths]
        exitok=len(r1)==25 and all(q['accepted'] and q['iterations']<2000 and q['evaluations']<10000 for q in r1)
        replayok=all((OUT/'tests'/name).exists() and read(OUT/'tests'/name)['passed'] for name in ['R2-synthetic.json']+[f'R2-legacy-{c}.json' for c in ['P','G','E']])
        backend=read(OUT/'tests/backend-choice.json') if (OUT/'tests/backend-choice.json').exists() else None
        tables=sorted((OUT/'tests').glob('R4-*.parquet'));rows=[]
        for p in tables:
            if 'export' not in p.name and 'partial' not in p.name:rows.extend(pd.read_parquet(p).to_dict('records'))
        integrated=len(rows)==232 and all(q['accepted'] and q['iterations']<2000 and q['evaluations']<10000 for q in rows)
        exports=all((OUT/'tests'/f'R4-export-{c}.json').exists() and read(OUT/'tests'/f'R4-export-{c}.json')['passed'] for c in ['P','G','E'])
        if rows:save(OUT/'tests/integrated-P1-inventory.parquet',rows)
        cost=dict(status='forecast_undetermined',qualified=False,scope=dict(convex_heads=27960,Adam_paths=18720),
            gate_seconds=69120,real_outer_conditioning_observed=False,no_automatic_full_experiment=True)
        if integrated and backend:
            # Head data cover all fixed roles; forecasts below are descriptive.
            # Median normalized to measured complete workload, NOT serial / threads.
            vals=np.array([q['seconds'] for q in rows]);kind={}
            for k in ['initial','static','refit']:
                v=np.array([q['seconds'] for q in rows if q['kind']==k]);kind[k]=dict(count=len(v),median=float(np.median(v)),p90=float(np.quantile(v,.9)),maximum=float(v.max()))
            R4secs=sum(i['seconds'] for i in read(OUT/'budget.json')['items'] if i['stage'].startswith('R4-'))
            cost.update(heads=kind,head_seconds_median=float(np.median(vals)),head_seconds_p90=float(np.quantile(vals,.9)),
                measured_fixed_P1_seconds=R4secs,proportional_P1_scope_proxy_seconds=R4secs*max(27960/232,18720/88),
                minimum_outer_shape_factor=352/192,
                reason='P1 integrated capability phase totals combine different head/path queues; no independently timed role/phase queue model yet. Shape tests do not identify real outer conditioning. Do not promote proportional proxy to a qualified conservative forecast.')
        write(OUT/'cost-forecast-revised.json',cost,True)
        state=dict(version='NER1',exit_policy_verified=exitok,uniform_lr_replay_verified=replayok,
            concurrent_heads_verified=bool(backend and backend['qualified']),integrated_pilot_verified=integrated and exports,
            full_scope_budget_feasible=False,forecast_status=cost['status'],query_read=False,H_scored=False,full_experiment_enabled=False,
            old_stop_preserved=True,partial=partial,qualified_integrated_heads=len(rows),
            status='stop_awaiting_review_no_full_experiment' if integrated and exports else 'stop_numeric_repair_pilot_incomplete')
        write(OUT/'completion.json',state,True);progress(state['status'],**{k:state[k] for k in ['exit_policy_verified','uniform_lr_replay_verified','integrated_pilot_verified','full_experiment_enabled']});codecheck()
    finally:end('R5-closeout')

if __name__=='__main__':closeout('--partial' in sys.argv)
