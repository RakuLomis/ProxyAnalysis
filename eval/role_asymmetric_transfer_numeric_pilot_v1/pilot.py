"""Expected old-stop replay, known hard case first, fixed controls, repeats."""
from common import *
from backend_loader import load

class NumericNotQualified(RuntimeError):pass

def attempts():return sorted((OUT/'attempts').glob('*/started.json'))

def fit_one(case,kind,old=False,capture=False):
    budget_check();n=len(attempts())+1;require(n<=45,'45-attempt cap')
    root=OUT/'attempts'/f'{n:03d}-{kind}';require(not root.exists(),'Attempt already exists')
    c=contract();r=c['roles'][case['role_id']];p=c['policies'][case['policy_id']]
    sp=OUT/'slots'/r['id']/(p['id']+'.pt');s=local_artifact(sp)
    write(root/'started.json',dict(attempt=n,kind=kind,role_id=r['id'],policy_id=p['id'],start_unix=time.time(),input_sha256=sha(sp),content_fingerprint=signature(s)['sha256'],old_budget=old))
    b=load(root,old,capture);model=None;failure=None;begin=time.perf_counter()
    try:
        model,log=b.fit_preconditioned(s['x'],s['y'],s['mass'],r['t'],dict(role_id=r['id'],arm=p['id'],t=r['t'],eta=r['eta'],
            execution_policy='old-budget-reproduction' if old else 'RA1-NR1',kind=kind,input_sha256=sha(sp)))
    except ActivityBudget:raise
    except RuntimeError as exc:failure=str(exc)
    lp=root/'fit-logs'/r['id']/f'{p["id"]}-t{r["t"]:g}.json'
    require(lp.exists(),'Backend failed before final numerical log')
    log=read(lp);theta=None
    if model is not None:
        model.update(mu=s['mu'],scale=s['scale']);theta=torch.cat([model['weight'],model['bias'][:,None]],1)
        put(root/'model.pt',model,role_id=r['id'],policy_id=p['id'],optimizer=log,input_fingerprint=signature(s)['sha256'])
    else:
        statepath=root/'failures'/r['id']/f'{p["id"]}-t{r["t"]:g}.pt'
        require(statepath.exists(),'Backend failure checkpoint missing');checked(statepath,sha(statepath),'new-attempt-failure-state')
        theta=torch.load(statepath,map_location=device(),weights_only=True)['last_original_parameters']
    value,gradient=independent(s,theta,r['t']);oe=abs(value-log['objective']);ge=abs(float(gradient.abs().max())-log['max_gradient'])
    require(oe<1e-10 and ge<1e-10,'Independent attempt objective/gradient replay')
    put(root/'final-parameters.pt',dict(theta=theta.detach(),gradient=gradient.detach()),role_id=r['id'],policy_id=p['id'])
    if b.prefix is not None:
        _,l,_=b.coordinates(s['x'],s['mass'],r['t']);pt=b.decode(b.prefix['parameter_V'],l);pv,pg=independent(s,pt,r['t'])
        put(root/'prefix-2000.pt',dict(**b.prefix,theta=pt.detach(),gradient=pg.detach(),objective=pv),role_id=r['id'],policy_id=p['id'])
    result=dict(attempt=n,kind=kind,role_id=r['id'],policy_id=p['id'],accepted=bool(log['accepted']),old_budget=old,root=rel(root),
        iterations=log['iterations'],evaluations=log['function_evaluations'],closure_evaluations=log['closure_evaluations'],
        objective=log['objective'],initial_objective=log['initial_objective'],gradient=log['max_gradient'],objective_replay_error=oe,gradient_replay_error=ge,
        log_objective_replay_error=log['objective_replay_error'],log_gradient_replay_error=log['gradient_replay_error'],
        reason=log['optimizer_exit_reason'],seconds=log['seconds'],full_attempt_seconds=time.perf_counter()-begin,failure=failure,
        prefix_2000_captured=b.prefix is not None,max_iter=b.SETTINGS['max_iter'],max_eval=b.SETTINGS['max_eval'])
    write(root/'result.json',result);progress('attempt_finished',attempt=n,kind=kind,accepted=result['accepted'],iterations=result['iterations'],gradient=result['gradient'])
    return result

def compare_stop(result,prefix=False):
    c=contract();r=c['roles'][FAIL_ROLE];s=local_artifact(OUT/'slots'/FAIL_ROLE/(FAIL_POLICY+'.pt'))
    old=old_artifact(ROOT/c['old_failure_state']);oldtheta=old['last_original_parameters'];ov,og=independent(s,oldtheta,r['t'])
    root=ROOT/result['root'];new=local_artifact(root/('prefix-2000.pt' if prefix else 'final-parameters.pt'))
    nv,ng=independent(s,new['theta'],r['t']);ve=abs(nv-ov);ge=float((ng-og).abs().max());pe=float((new['theta']-oldtheta).abs().max())
    require(ve<1e-10 and ge<1e-10,'Original stop/prefix replay not equivalent')
    return dict(passed=True,objective_error=ve,gradient_vector_error=ge,parameter_max_error=pe,original_objective=ov,original_gradient=float(og.abs().max()),new_gradient=float(ng.abs().max()),attempt=result['attempt'])

def n2():
    with phase('N2'):
        case=dict(role_id=FAIL_ROLE,policy_id=FAIL_POLICY)
        old=fit_one(case,'old-reproduction',old=True)
        require(not old['accepted'] and old['reason']=='iteration_budget' and old['iterations']==2000,'Expected old stop did not reproduce')
        write(OUT/'audits/old-stop-reproduction.json',compare_stop(old))
        new=fit_one(case,'NR1-hard-case',capture=True)
        require(new['prefix_2000_captured'],'N2000 prefix absent')
        write(OUT/'audits/prefix-comparison.json',compare_stop(new,True))
        if not new['accepted']:raise NumericNotQualified('Known hard case not qualified under fixed 4000/20000; no automatic extension')
        write(OUT/'endpoints'/FAIL_ROLE/(FAIL_POLICY+'.json'),new)

def n3():
    with phase('N3'):
        c=contract()
        for case in c['design']['cases']:
            if case['role_id']==FAIL_ROLE and case['policy_id']==FAIL_POLICY:continue
            result=fit_one(case,'NR1-case')
            if not result['accepted']:raise NumericNotQualified('Fixed control not qualified: '+case['role_id']+'/'+case['policy_id'])
            write(OUT/'endpoints'/case['role_id']/(case['policy_id']+'.json'),result)
        repeats=[]
        for case in c['design']['additional_deterministic_repeats']:
            first=read(OUT/'endpoints'/case['role_id']/(case['policy_id']+'.json'));second=fit_one(case,'NR1-repeat')
            require(second['accepted'],'Repeated fit not qualified')
            a=local_artifact(ROOT/first['root']/'model.pt');b=local_artifact(ROOT/second['root']/'model.pt');s=local_artifact(OUT/'slots'/case['role_id']/(case['policy_id']+'.pt'))
            pe=max(float((a[k]-b[k]).abs().max()) for k in ['weight','bias']);le=float(((s['x']@a['weight'].T+a['bias'])-(s['x']@b['weight'].T+b['bias'])).abs().max())
            require(pe==0. and le==0.,'Deterministic repeated model differs')
            repeats.append(dict(**case,parameter_error=pe,training_logit_error=le,passed=True,first_attempt=first['attempt'],second_attempt=second['attempt']))
        write(OUT/'audits/deterministic-repeats.json',dict(passed=True,repeats=repeats))
