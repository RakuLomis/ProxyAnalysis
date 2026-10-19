"""N4 independent pilot audit and read-only old-endpoint compatibility."""
from common import *
from backend_loader import policy

def run():
    with phase('N4'):
        c=contract();endpoints=[read(p) for p in (OUT/'endpoints').rglob('*.json')]
        require(len(endpoints)==42,'42 endpoints must be accepted');audits=[];overlap=[]
        newer={(e['role_id'],e['policy_id']):e for e in endpoints}
        for e in endpoints:
            budget_check();s=local_artifact(OUT/'slots'/e['role_id']/(e['policy_id']+'.pt'));m=local_artifact(ROOT/e['root']/'model.pt')
            theta=torch.cat([m['weight'],m['bias'][:,None]],1);value,g=independent(s,theta,c['roles'][e['role_id']]['t'])
            require(abs(value-e['objective'])<1e-10 and float(g.abs().max())<=1e-5,'Independent original gate')
            require(all(policy(False).acceptance_gates(value,e['initial_objective'],float(g.abs().max()),e['iterations'],e['log_objective_replay_error'],e['log_gradient_replay_error']).values()),'Independent numerical policy')
            audits.append(dict(role_id=e['role_id'],policy_id=e['policy_id'],objective=value,gradient=float(g.abs().max()),objective_error=abs(value-e['objective']),gradient_error=abs(float(g.abs().max())-e['gradient'])))
        oldledger=[]
        for e in c['accepted_old']:
            budget_check();s=old_artifact(OLD/'numeric-slots'/e['role_id']/(e['policy_id']+'.pt'));m=old_artifact(ROOT/e['path']);t=c['old_role_settings'][e['role_id']]['t']
            theta=torch.cat([m['weight'],m['bias'][:,None]],1);value,g=independent(s,theta,t);info=read((ROOT/e['path']).with_suffix('.json'));log=info['optimizer']
            require(abs(value-log['objective'])<1e-10 and abs(float(g.abs().max())-log['max_gradient'])<1e-10 and float(g.abs().max())<=1e-5,'Old endpoint independent audit')
            require(log['iterations']<2000 and log['function_evaluations']<10000,'Old endpoint before original budget boundary')
            entry=dict(**e,objective=value,gradient=float(g.abs().max()),source_policy_sha256=log['numeric_policy_sha256'],source_limits=dict(max_iter=2000,max_eval=10000),
                       eligible_for_future_budget_only_adoption_review=True,adopted_into_full_run=False)
            oldledger.append(entry)
            key=(e['role_id'],e['policy_id'])
            if key in newer:
                ee=newer[key];n=local_artifact(ROOT/ee['root']/'model.pt');ss=local_artifact(OUT/'slots'/e['role_id']/(e['policy_id']+'.pt'))
                require(all(torch.equal(s[k],ss[k]) for k in s),'Overlapping input content differs')
                pe=max(float((m[k]-n[k]).abs().max()) for k in ['weight','bias']);le=float(((s['x']@m['weight'].T+m['bias'])-(s['x']@n['weight'].T+n['bias'])).abs().max())
                require(pe==0. and le==0. and log['iterations']==ee['iterations'] and log['function_evaluations']==ee['evaluations'],'Overlapping zero-start trajectory differs')
                overlap.append(dict(role_id=e['role_id'],policy_id=e['policy_id'],parameter_error=pe,training_logit_error=le,iterations=ee['iterations'],passed=True))
        require(len(overlap)==27,'27 historical overlap endpoints')
        save(pd.DataFrame(audits),OUT/'audits/independent-original-coordinate.parquet');save(pd.DataFrame(oldledger),OUT/'audits/old-endpoint-compatibility.parquet');save(pd.DataFrame(overlap),OUT/'audits/overlap-comparison.parquet')
        for p,h in c['preserve'].items():require(sha(ROOT/p)==h,'Original source/result changed')
        for p,h in c['code'].items():require(sha(ROOT/p)==h,'NR1 code changed')
        require(not any('/query.parquet' in x['path'] or '/labels.parquet' in x['path'] or 'heldout-visits' in x['path'] or 'main-test-paired' in x['path'] for x in READS),'Forbidden read')
        require(not (OLD/'completion.json').exists(),'Original stop incorrectly overwritten')
        write(OUT/'verification.json',dict(passed=True,new_original_coordinate_audits=42,old_original_coordinate_audits=151,overlap_exact=27,
              old_failure_preserved=True,H_query_reads=0,H_label_reads=0,actual_target_U_reads=0,full_matrix_auto_start=False))
