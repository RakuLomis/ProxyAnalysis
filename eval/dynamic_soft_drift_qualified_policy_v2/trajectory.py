"""Finite pilot only: 36 fixed trajectories, never a business-model entry point."""
from common import *
import scales
import feedback
import objective
import projected_step as PS
import line_search as LS
import quality

def state_row(s,m,r,arm,k):
    f=s['feedback'];res=quality.residual(s,m)
    return dict(role_id=r['id'],target=r['target'],group=r['group'],arm=arm,state=k,
                q=s['q'].tolist(),Q_f=s['Q_f'],Q_v=s['Q_v'],shrink=s['shrink'],penalty=s['penalty'],L_f=s['L_f'],L_v=s['L_v'],
                task_gradient_f=f['gradient_f'].tolist(),task_gradient_v=f['gradient_v'].tolist(),
                shrink_gradient=s['shrink_gradient'].tolist(),penalty_gradient=s['penalty_gradient'].tolist(),
                g_f=s['g_f'].tolist(),g_v=s['g_v'].tolist(),gap=s['gap'].tolist(),penalty_parts=s['penalty_parts'].tolist(),
                boundaries=int(((s['q']==0)|(s['q']==2)).sum()),max_original_gradient=f['max_original_gradient'],
                mean_gradient_max_difference=f['mean_gradient_max_difference'],max_task_gradient_difference=f['max_task_gradient_difference'],**res)

def fit_role(r,arm):
    kind=kind_for(arm);rs=[e for e in contract()['inner_roles'] if (e['outer'],e['target'],e['group'])==(r['outer'],r['target'],r['group'])]
    require(len(rs)==12,'Source scope count');install_tasks({(e['id'],kind):feedback.validate_task(e,kind,arm) for e in rs})
    m=scales.load(r,arm);coeff=None if arm=='QT' else scales.coefficients(r,arm)
    q=torch.ones(10,device=device(),dtype=torch.float64);begin=time.perf_counter();rows=[];trials=[];accepted=0;evaluations=0
    current=origin=None;status=None;root=OUT/'trajectories'/r['id']/arm
    recovery=contract().get('recovery',{});pending=recovery.get('pending',{})
    restoring=(pending.get('role_id'),pending.get('arm'))==(r['id'],arm)
    old_seconds=0.
    try:
        if restoring:
            rows=pd.read_parquet(root/'states.parquet').to_dict('records');trials=pd.read_parquet(root/'trials.parquet').to_dict('records')
            accepted=pending['accepted_state'];evaluations=pending['evaluation']-1;old_seconds=pending['old_partial_seconds']
            origin=own(root/'q00.pt')['state'];current=own(root/f'q{accepted:02d}.pt')['state']
            require(torch.equal(current['q'],tensor(rows[-1]['q'])) and len(rows)==accepted+1,'Restored state mismatch')
            progress('trajectory_resumed',role=r['id'],arm=arm,state=accepted,prior_trials=evaluations)
        else:
            fb,_=feedback.aggregate(rs,kind,q,arm,True);current=origin=objective.evaluate(q,fb,coeff,arm)
            row=state_row(current,m,r,arm,0);rows.append(row);put(dict(state=current,row=row),root/'q00.pt',role_id=r['id'],arm=arm,state=0,accepted=True)
            progress('origin_accepted',role=r['id'],arm=arm,PG=row['PG_f'],L=row['L_f'])
            if quality.stationary(current,m):status='stationary_at_origin'
        while status is None and accepted<20:
            resource_gate();p,gamma=PS.direction(current['g_f'],m);did_accept=False;all_signal_failed=True
            for bt,alpha in enumerate(contract()['alphas']):
                resource_gate();nq,delta=PS.candidate(current['q'],p,alpha)
                tr=dict(role_id=r['id'],arm=arm,iteration=accepted+1,backtrack=bt,alpha=alpha,gamma=gamma,
                        q=nq.tolist(),delta=delta.tolist(),delta_inf=float(delta.abs().max()),scaled_delta_inf=float((delta*m.sqrt()).abs().max()),
                        forward_evaluated=False,accepted=False,**LS.signal(current,delta))
                if tr['delta_inf']<1e-8:
                    tr['reason']='small_step';trials.append(tr);status='stop_small_step';break
                if not tr['direction_pass']:
                    tr['reason']='direction_unresolved';trials.append(tr);continue
                all_signal_failed=False
                if evaluations>=40:status='stop_budget';tr['reason']='trial_budget';trials.append(tr);break
                reserved=restoring
                if reserved:
                    require(bt==pending['backtrack'] and alpha==pending['alpha'] and feedback.key(nq)==pending['q_sha256'],'Reserved pending trial mismatch')
                    evaluations=pending['evaluation'];ledger(recovery_trial_replays=1);restoring=False
                else:
                    evaluations+=1
                    write(root/'pending-trial.json',dict(role_id=r['id'],arm=arm,iteration=accepted+1,evaluation=evaluations,q=nq.tolist(),q_sha256=feedback.key(nq),alpha=alpha,backtrack=bt,reserved=True,status='before_forward'))
                    ledger(trial_batches=1)
                if reserved:write(root/'pending-trial.json',dict(pending,recovery=True,status='replaying_reserved_forward'))
                fb,values=feedback.aggregate(rs,kind,nq,arm,False,reserved=reserved);trial=objective.evaluate(nq,fb,coeff,arm,False)
                tr.update(forward_evaluated=True,evaluation=evaluations,Q_f=trial['Q_f'],Q_v=trial['Q_v'],
                          shrink=trial['shrink'],penalty=trial['penalty'],L_f=trial['L_f'],L_v=trial['L_v'],**LS.accept(current,trial,tr))
                if not tr['value_pass']:
                    tr['reason']='insufficient_dual_descent';trials.append(tr)
                    save(pd.DataFrame(trials),root/'trials.parquet');write(root/'pending-trial.json',dict(status='rejected',evaluation=evaluations));continue
                # Do not fit again: derive at the SAME fine/validated candidate states.
                fb,_=feedback.aggregate(rs,kind,nq,arm,True,values)
                new=objective.evaluate(nq,fb,coeff,arm)
                require(new['L_f']==trial['L_f'] and new['L_v']==trial['L_v'],'Gradient endpoint changed qualified values')
                accepted+=1;ledger(q_updates=1);tr.update(accepted=True,reason='dual_descent_and_gradient_qualified');trials.append(tr)
                current=new;row=state_row(current,m,r,arm,accepted);rows.append(row)
                put(dict(state=current,row=row,acceptance=tr),root/f'q{accepted:02d}.pt',role_id=r['id'],arm=arm,state=accepted,accepted=True)
                save(pd.DataFrame(rows),root/'states.parquet');save(pd.DataFrame(trials),root/'trials.parquet')
                write(root/'pending-trial.json',dict(status='accepted',evaluation=evaluations,state=accepted))
                progress('outer_update_accepted',role=r['id'],arm=arm,state=accepted,trial_evaluations=evaluations,
                         L=row['L_f'],Q=row['Q_f'],penalty=row['penalty'],PG=row['PG_f'],seconds=time.perf_counter()-begin)
                did_accept=True
                if quality.stationary(current,m):status='stationary'
                break
            if status is None and not did_accept:status='stop_signal_undetermined' if all_signal_failed else 'stop_line_search'
        if status is None:status='accepted_update_limit'
    except BudgetStop as exc:
        write(root/'resource-stop.json',dict(reason=str(exc),accepted_updates=accepted,global_stop=True))
        raise
    except BaseException as exc:
        if rows:save(pd.DataFrame(rows),root/'states.parquet')
        if trials:save(pd.DataFrame(trials),root/'trials.parquet')
        write(root/'failure.json',dict(status='stop_numeric_or_permission',reason=str(exc),accepted_updates=accepted,trial_evaluations=evaluations))
        raise
    if rows:save(pd.DataFrame(rows),root/'states.parquet')
    if trials:save(pd.DataFrame(trials),root/'trials.parquet')
    if current is None:
        result=dict(status='stop_budget',passed=False,accepted_updates=0,origin_available=False)
    else:result=quality.conclude(origin,current,m,status,accepted,all(t['value_pass'] for t in trials if t['accepted']))
    result.update(role_id=r['id'],target=r['target'],group=r['group'],arm=arm,kind=kind,trial_evaluations=evaluations,
                  seconds=old_seconds+time.perf_counter()-begin,continuation_seconds=time.perf_counter()-begin,origin_available=current is not None,
                  Q_origin=None if origin is None else origin['Q_f'],Q_terminal=None if current is None else current['Q_f'],
                  L_origin=None if origin is None else origin['L_f'],L_terminal=None if current is None else current['L_f'])
    write(root/'result.json',result);progress('trajectory_complete',**result);return result


