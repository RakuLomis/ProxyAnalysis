"""Independent activation-aware checks then 24 unchanged-objective source fits."""
from common import *
import oracle as O

def gradients():
    with stage('gradients'):
        A,R,U=production();roles=contract()['roles'];rows=[];coefficient_rows=[];replays=[];timings=[];trajectories=0
        save(pd.DataFrame(O.tests()),OUT/'audits/branch-tests.parquet')
        for arm in ARMS:
            tasks=[task(r,arm) for r in roles]
            independent=[O.coefficients(t,arm) for t in tasks]
            for i,r in enumerate(roles):
                for key in ['A','B','C','s']:
                    error=float((independent[i][key]-tasks[i]['coeff'][key]).abs().max())
                    coefficient_rows.append(dict(role_id=r['id'],arm=arm,quantity=key,error=error,passed=error<1e-10))
            require(all(x['passed'] for x in coefficient_rows),'Independent explicit coefficient replay failed')
            b=U.batch([t['view'] for t in tasks]);c={k:torch.stack([t['coeff'][k] for t in tasks]) for k in ['A','B','C','s']}
            oc=[{k:v.detach().cpu().numpy() for k,v in t.items()} for t in independent]
            def evaluate(q):
                risk,theta=U.run(b,q);smooth=risk+A.regularizer(q)
                penalty=R.soft(q,c)[0] if arm!='T-P' else torch.zeros_like(smooth)
                return smooth,penalty,smooth+penalty,risk,theta
            for point,values in [('one',np.ones(10)),('interior',np.array([.9,1.1]*5))]:
                q=tensor(np.tile(values,(12,1))).requires_grad_();torch.cuda.synchronize();torch.cuda.reset_peak_memory_stats();began=time.perf_counter()
                sm,ph,total,risk,theta=evaluate(q)
                gs=torch.autograd.grad(sm.sum(),q,retain_graph=True)[0]
                gp=torch.autograd.grad(ph.sum(),q,retain_graph=True)[0] if arm!='T-P' else torch.zeros_like(q)
                gt=torch.autograd.grad(total.sum(),q)[0]
                torch.cuda.synchronize();timings.append(dict(arm=arm,point=point,seconds=time.perf_counter()-began,
                       peak_MiB=torch.cuda.max_memory_allocated()/1048576,unroll_backward_passes=2,penalty_only_backward=int(arm!='T-P')))
                trajectories+=12
                reference=[]
                for i in range(12):
                    reference.append([O.derivative(float(q[i,j].detach()),oc[i]['A'][j],oc[i]['B'][j],oc[i]['s'][j]) if arm!='T-P' else 0. for j in range(10)])
                gold=tensor(reference);pe=(gp-gold).abs();se=(gt-gs-gp).abs()
                require(float(pe.max())<1e-10 and float(se.max())<1e-10,'Independent penalty or gradient sum precision')
                old=old_gradients(arm,point)
                te=float((theta.detach()-old['theta']).abs().max());ge=float((gt.detach()-old['gradient']).abs().max())
                require(te<1e-10 and ge<1e-10,'Frozen trajectory changed')
                replays.append(dict(arm=arm,point=point,theta_error=te,total_gradient_error=ge,
                                    penalty_error=float(pe.max()),gradient_sum_error=float(se.max()),passed=True))
                put(dict(q=q.detach(),smooth=sm.detach(),penalty=ph.detach(),total=total.detach(),risk=risk.detach(),
                         smooth_gradient=gs.detach(),penalty_gradient=gp.detach(),total_gradient=gt.detach(),theta=theta.detach()),
                    OUT/'gradients'/f'{arm}-{point}.pt',source_only=True,trajectory_unchanged=True)
                for h in [1e-3,3e-4]:
                    for j in range(10):
                        plus=q.detach().clone();minus=plus.clone();plus[:,j]+=h;minus[:,j]-=h
                        with torch.no_grad():sp,pp,lp,_,_=evaluate(plus);sn,pn,ln,_,_=evaluate(minus)
                        ds=(sp-sn)/(2*h);dl=(lp-ln)/(2*h);dp=(pp-pn)/(2*h);trajectories+=24
                        for i,r in enumerate(roles):
                            aa=oc[i]['A'][j];bb=oc[i]['B'][j];ss=oc[i]['s'][j];qq=float(q[i,j].detach())
                            branch=O.branch(qq,h,aa,bb,ss) if arm!='T-P' else 'no_penalty'
                            smootherr=abs(float(ds[i]-gs[i,j]));smoothlim=1e-5+1e-3*abs(float(ds[i]))
                            fullerr=abs(float(dl[i]-gt[i,j]));fulllim=1e-5+1e-3*abs(float(dl[i]))
                            exactfd=(O.phi(qq+h,aa,bb,ss)-O.phi(qq-h,aa,bb,ss))/(2*h) if arm!='T-P' else 0.
                            needsfull=branch!='boundary'
                            passed=smootherr<=smoothlim and bool(pe[i,j]<1e-10) and (not needsfull or fullerr<=fulllim)
                            k=(2*aa-2*bb)/ss
                            rows.append(dict(role_id=r['id'],arm=arm,point=point,coordinate=j,h=h,
                                 smooth_plus=float(sp[i]),smooth_minus=float(sn[i]),smooth_auto=float(gs[i,j]),smooth_FD=float(ds[i]),
                                 smooth_error=smootherr,smooth_limit=smoothlim,smooth_passed=smootherr<=smoothlim,
                                 penalty_auto=float(gp[i,j]),penalty_oracle=float(gold[i,j]),penalty_error=float(pe[i,j]),
                                 branch=branch,full_check_required=needsfull,full_auto=float(gt[i,j]),full_FD=float(dl[i]),
                                 full_error=fullerr,full_limit=fulllim,original_direct_passed=fullerr<=fulllim,
                                 penalty_FD=float(dp[i]),independent_penalty_FD=exactfd,
                                 boundary_truncation=float(dp[i]-gp[i,j]),leading_boundary_term=k*abs(k)*h/40 if point=='one' and arm!='T-P' else None,
                                 revised_passed=passed,criterion='smooth_and_independent_penalty' if not needsfull else 'smooth_penalty_and_full'))
                        save(pd.DataFrame(rows),OUT/'checks/gradient-checks.parquet')
                        progress('activation_aware_gradients',arm=arm,point=point,h=h,coordinate=j,
                                 checks=len(rows),failed=sum(not v['revised_passed'] for v in rows),trajectories=trajectories)
        save(pd.DataFrame(coefficient_rows),OUT/'checks/oracle-coefficients.parquet')
        save(pd.DataFrame(replays),OUT/'checks/unchanged-trajectory.parquet')
        save(pd.DataFrame(timings),OUT/'checks/runtime.parquet')
        result=dict(passed=all(v['revised_passed'] for v in rows),checks=len(rows),
                  revised_failed=sum(not v['revised_passed'] for v in rows),original_direct_failed=sum(not v['original_direct_passed'] for v in rows),
                  max_smooth_error=max(v['smooth_error'] for v in rows),max_penalty_error=max(v['penalty_error'] for v in rows),
                  trajectories=trajectories,inner_updates=trajectories*64,unroll_backward_exposures=144,
                  penalty_backward_exposures=48,formal_matrix_authorized=False)
        write(OUT/'gradient-repair-verification.json',result)
        require(result['passed'] and trajectories<=2952,'Repair gradient gate; no source fit authorized')

def references():
    with stage('references'):
        require(read(OUT/'gradient-repair-verification.json')['passed'],'Repaired gradient gate first')
        A,R,U=production();optim=solver();roles=contract()['roles'];rows=[];predictions=[];one=tensor(np.ones(10))
        for i,r in enumerate(roles):
            for arm in ['D-P','D-G']:
                v=task(r,arm)['view'];s=U.pack(v,arm,one)
                require(s['x'].is_cuda and s['x'].dtype==torch.float64 and s['x'].shape==(480,96),'Source fit coordinate/rows')
                require(abs(float(s['mass'].sum())-1)<1e-12 and float((weighted(s['y'],s['mass'],6)-1/6).abs().max())<1e-12,'Source fit mass')
                old=old_gradients(arm,'one');theta64=old['theta'][i]
                J64=float(U.original_objective(theta64,s,r['t']));G64=float(U.original_gradient(theta64,s,r['t']).abs().max())
                replay=U.run(U.batch([v]),one[None,:])
                require(float((replay[1][0]-theta64).abs().max())<1e-10,'Old unroll replay mismatch')
                del replay
                m,log=optim.fit_preconditioned(s['x'],s['y'],s['mass'],r['t'],dict(role_id=r['id'],arm=arm),diagnostic=True)
                put(dict(**m,mu=v['mu'],scale=v['scale']),OUT/'models'/r['id']/f'{arm}.pt',optimizer=log,source_only=True,q=1.)
                theta=torch.cat([m['weight'],m['bias'][:,None]],1)
                value=float(U.original_objective(theta,s,r['t']));gradient=float(U.original_gradient(theta,s,r['t']).abs().max())
                require(abs(value-log['objective'])<1e-10 and gradient<=1e-5,'Independent original reference acceptance')
                with torch.no_grad():
                    l64=v['query_x']@theta64[:,:96].T+theta64[:,96]
                    lr=v['query_x']@m['weight'].T+m['bias'];p64=torch.softmax(l64,1);pr=torch.softmax(lr,1)
                    y=v['query_y'];ce64=(torch.logsumexp(l64,1)-l64.gather(1,y[:,None]).squeeze(1))
                    cer=(torch.logsumexp(lr,1)-lr.gather(1,y[:,None]).squeeze(1))
                    z64=l64-l64.mean(1,keepdim=True);zr=lr-lr.mean(1,keepdim=True)
                    tv=(p64-pr).abs().sum(1)/2;pred64=p64.argmax(1);predr=pr.argmax(1)
                    oldok=pred64==y;newok=predr==y
                J0=log['initial_objective'];den=J0-value
                ratio=(J64-value)/den if den>1e-6 else None
                rows.append(dict(role_id=r['id'],arm=arm,calibration=r['calibration'],group=r['group'],t=r['t'],
                     J0=J0,J64=J64,J_ref=value,remaining_ratio=ratio,ratio_missing_reason=None if ratio is not None else 'denominator_small',
                     gradient64=G64,gradient_ref=gradient,CE64=float((ce64*v['query_mass']).sum()),CE_ref=float((cer*v['query_mass']).sum()),
                     mean_probability_TV=float(tv.mean()),max_probability_difference=float((p64-pr).abs().max()),
                     relative_logit_RMSE=float((z64-zr).square().mean().sqrt()),relative_logit_max=float((z64-zr).abs().max()),
                     visits=8,changed=int((pred64!=predr).sum()),fixed=int((~oldok&newok).sum()),broken=int((oldok&~newok).sum()),
                     both_correct=int((oldok&newok).sum()),both_wrong=int((~oldok&~newok).sum()),
                     accuracy64=float(oldok.to(torch.float64).mean()),accuracy_ref=float(newok.to(torch.float64).mean()),
                     iterations=log['iterations'],evaluations=log['function_evaluations'],solver_seconds=log['seconds'],accepted=True))
                for k in range(8):
                    predictions.append(dict(role_id=r['id'],arm=arm,feedback_row=k,label=int(y[k]),
                         prediction64=int(pred64[k]),prediction_ref=int(predr[k]),CE64=float(ce64[k]),CE_ref=float(cer[k]),
                         probability_TV=float(tv[k]),**{f'p64_{j}':float(p64[k,j]) for j in range(6)},
                         **{f'pref_{j}':float(pr[k,j]) for j in range(6)},
                         **{f'centered_logit64_{j}':float(z64[k,j]) for j in range(6)},
                         **{f'centered_logitref_{j}':float(zr[k,j]) for j in range(6)}))
                save(pd.DataFrame(rows),OUT/'reference-comparisons.parquet')
                save(pd.DataFrame(predictions),OUT/'source-predictions.parquet')
                progress('source_reference',fits=len(rows),cap=24,arm=arm,remaining_ratio=ratio,solver_seconds=log['seconds'])
        require(len(rows)==24,'Reference count')
        write(OUT/'references-complete.json',dict(passed=True,new_classifier_fits=24,new_mapping_fits=0,q_alt_fits=0,
                model_source_only=True,source_predicted_rows=len(predictions),formal_matrix_started=False))

if __name__=='__main__':
    {'register':register,'gradients':gradients,'references':references}[sys.argv[1]]()
