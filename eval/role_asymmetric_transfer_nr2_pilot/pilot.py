"""Fixed diagnostics, zero-start cases, independent prefix and repeat checks."""
from common import *
import common as C
import numeric as N
import legacy_prefix as L

def casekey(case):return case['role_id']+'/'+case['policy_id']
def role(case):return {r['id']:r for r in C.CONTRACT['roles']}[case['role_id']]
def diagnostics():
    progress('P2_snapshot_diagnostics')
    out=[]
    for e in C.CONTRACT['design']['snapshot_diagnostics']:
        f=read(checked(ROOT/e['failure_json'],'diagnostic-failure-log'));s=load(ROOT/e['slot_path'])
        state=load((ROOT/e['failure_json']).with_suffix('.pt'),'diagnostic-snapshot')
        a=begin('snapshot-diagnostic',dict(role_id=f['role_id'],policy_id=f['arm'],diagnostic_id=e['id']));started=time.perf_counter()
        log=dict(diagnostic_id=e['id'],parent_failure_sha256=sha(ROOT/e['failure_json']),parent_iterations=f['iterations'],
                 initial_objective=f['objective'],scientific_endpoint_accepted=False)
        counter=dict(optimization_evaluations=0,lbfgs_updates=0)
        theta,log=N.refine(state['last_original_parameters'],s,f['t'],8,log,counter,f"{a['index']:03d}")
        aa=N.audit(theta,s,f['t']);require(aa['max_gradient']<=1e-5,'Diagnostic gradient not qualified')
        log.update(**aa,counters=counter,seconds=time.perf_counter()-started,diagnostic_gradient_qualified=True)
        save(OUT/'diagnostics'/(e['id']+'.pt'),dict(theta=theta));write(OUT/'diagnostics'/(e['id']+'-result.json'),log)
        end(a,status='diagnostic-qualified-not-adoptable',seconds=log['seconds'],newton_updates=log['newton_updates'])
        out.append(log);progress('snapshot_qualified',id=e['id'],Newton_updates=log['newton_updates'],gradient=aa['max_gradient'])
    write(OUT/'audits/snapshot-diagnostics.json',dict(passed=True,results=out,scientific_endpoints_added=0))

def fit(case,kind='zero-start-case'):
    s=pilot_slot(case);r=role(case);a=begin(kind,dict(role_id=case['role_id'],policy_id=case['policy_id']));tag=f"{a['index']:03d}"
    started=time.perf_counter();theta,ll=L.run(s,r['t'],tag)
    log=dict(role_id=case['role_id'],policy_id=case['policy_id'],t=r['t'],eta=r['eta'],initialization='zero',
             original_objective_unchanged=True,solver_algorithm_changed=True,lbfgs_log=rel(OUT/'lbfgs-logs'/f'{tag}.json'),
             initial_objective=ll['initial_objective'],newton_updates=0)
    # Preserve checkpoint independently of final Newton parameters.
    save(OUT/'phase-checkpoints'/(tag+'.pt'),dict(theta=theta.clone()))
    count=dict(lbfgs_updates=ll['lbfgs_updates'],optimization_evaluations=ll['optimization_evaluations'])
    if ll['max_gradient']>1e-5:
        theta,log=N.refine(theta,s,r['t'],32,log,count,tag)
    aa=N.audit(theta,s,r['t']);updates=ll['lbfgs_updates']+log['newton_updates']
    gates=acceptance_gates(aa['objective'],ll['initial_objective'],aa['max_gradient'],updates,aa['objective_replay_error'],aa['gradient_replay_error'])
    require(all(gates.values()),'Original final gates not satisfied')
    log.update(**aa,total_updates=updates,counters=count,seconds=time.perf_counter()-started,gates=gates,accepted=True,
               lbfgs_updates=ll['lbfgs_updates'],kind=kind,cuda_peak_MiB=torch.cuda.max_memory_allocated()/1048576)
    mp=OUT/'attempt-models'/(tag+'.pt');save(mp,dict(weight=theta[:,:96],bias=theta[:,96],mu=s['mu'],scale=s['scale']))
    write(OUT/'results'/(tag+'.json'),log);end(a,status='accepted',seconds=log['seconds'],result=rel(OUT/'results'/(tag+'.json')))
    if kind=='zero-start-case':
        ep=dict(**case,model_path=rel(mp),model_sha256=sha(mp),result_path=rel(OUT/'results'/(tag+'.json')),phase_path=rel(OUT/'phase-checkpoints'/(tag+'.pt')),
                t=r['t'],eta=r['eta'],attempt=a['index'],**aa)
        write(OUT/'endpoints'/casekey(case)/'endpoint.json',ep)
    progress('case_accepted',attempt=a['index'],role=case['role_id'],policy=case['policy_id'],LBFGS=ll['lbfgs_updates'],Newton=log['newton_updates'])
    return dict(model_path=mp,phase_path=OUT/'phase-checkpoints'/(tag+'.pt'),log=log)

def prefixes(priority_results):
    out=[]
    for case in C.CONTRACT['design']['prefix_only_cases']:
        r=role(case);s=pilot_slot(case);a=begin('prefix-diagnostic',case);started=time.perf_counter()
        theta,ll=L.run(s,r['t'],f"{a['index']:03d}",reference=True)
        candidate=torch.load(priority_results[casekey(case)]['phase_path'],map_location=dev(),weights_only=True)['theta']
        exact=torch.equal(theta,candidate)
        require(exact,'Independent 1024 prefix parameters differ')
        ja=N.audit(theta,s,r['t']);jb=N.audit(candidate,s,r['t'])
        ge=float((N.raw_gradient(theta,s,r['t'])-N.raw_gradient(candidate,s,r['t'])).abs().max())
        require(abs(ja['objective']-jb['objective'])<1e-10 and ge<1e-10,'Prefix original replay')
        logits_error=float((s['x']@(theta[:,:96]-candidate[:,:96]).T+(theta[:,96]-candidate[:,96])).abs().max())
        row=dict(**case,parameters_exact=exact,gradient_error=ge,objective_error=abs(ja['objective']-jb['objective']),
                 logits_error=logits_error,updates=ll['lbfgs_updates'],scientific_endpoint_accepted=False)
        save(OUT/'prefixes'/f"{a['index']:03d}.pt",dict(theta=theta));out.append(row)
        end(a,status='prefix-verified-not-adoptable',seconds=time.perf_counter()-started)
    write(OUT/'audits/prefix-comparison.json',dict(passed=True,results=out))

def run():
    diagnostics();progress('P3_zero_start_matrix')
    cases=C.CONTRACT['cases'];bykey={casekey(c):c for c in cases};priority_results={}
    priority=[casekey(c) for c in C.CONTRACT['design']['priority_cases']]
    for k in priority:priority_results[k]=fit(bykey[k])
    prefixes(priority_results)
    for k in sorted(set(bykey)-set(priority)):fit(bykey[k])
    rows=[]
    for c in C.CONTRACT['design']['repeat_cases']:
        new=fit(c,kind='deterministic-repeat');old=read(OUT/'endpoints'/casekey(c)/'endpoint.json')
        a=torch.load(new['model_path'],map_location=dev(),weights_only=True)
        b=torch.load(ROOT/old['model_path'],map_location=dev(),weights_only=True);s=pilot_slot(c)
        require(all(torch.equal(a[k],b[k]) for k in a),'Repeat parameters differ')
        za=s['x']@a['weight'].T+a['bias'];zb=s['x']@b['weight'].T+b['bias']
        require(torch.equal(za,zb),'Repeat logits differ')
        rows.append(dict(**c,parameters_exact=True,training_logits_exact=True))
    write(OUT/'audits/deterministic-repeats.json',dict(passed=True,results=rows))

def verify():
    progress('P4_independent_audit')
    eps=[read(p) for p in (OUT/'endpoints').rglob('endpoint.json')];require(len(eps)==52,'52 endpoints required')
    old={(e['role_id'],e['policy_id']):e for e in C.CONTRACT['endpoints']};rows=[];overlap=[]
    for e in eps:
        guard();s=pilot_slot(e);m=torch.load(ROOT/e['model_path'],map_location=dev(),weights_only=True)
        require(sha(ROOT/e['model_path'])==e['model_sha256'],'New model hash')
        theta=torch.cat([m['weight'],m['bias'][:,None]],1);aa=N.audit(theta,s,e['t']);log=read(ROOT/e['result_path'])
        require(all(acceptance_gates(aa['objective'],log['initial_objective'],aa['max_gradient'],log['total_updates'],aa['objective_replay_error'],aa['gradient_replay_error']).values()),'Final independent gates')
        rows.append(dict(role_id=e['role_id'],policy_id=e['policy_id'],**aa))
        ee=old.get((e['role_id'],e['policy_id']))
        if ee:
            om=load(ROOT/ee['path'],'old-accepted-model-audit');ot=torch.cat([om['weight'],om['bias'][:,None]],1)
            oa=N.audit(ot,s,e['t']);newz=s['x']@m['weight'].T+m['bias'];oldz=s['x']@om['weight'].T+om['bias']
            delta=newz-oldz;delta=delta-delta.mean(1,keepdim=True)
            overlap.append(dict(role_id=e['role_id'],policy_id=e['policy_id'],objective_difference=aa['objective']-oa['objective'],
                parameter_max_difference=float((theta-ot).abs().max()),relative_logits_max_difference=float(delta.abs().max()),
                training_probability_TV_mean=float((newz.softmax(1)-oldz.softmax(1)).abs().sum(1).mean()/2),old_gradient=oa['max_gradient']))
    write(OUT/'audits/independent-new-endpoints.json',dict(passed=True,results=rows))
    write(OUT/'audits/old-new-overlap.json',dict(no_model_selection=True,results=overlap))
    compatibility=[]
    for e in C.CONTRACT['endpoints']:
        guard();m=load(ROOT/e['path'],'protected-accepted-model-audit')
        if e.get('slot_path'):s=load(ROOT/e['slot_path'])
        else:
            rr=role(e);v=load(OLD/'packages'/rr['id']/'training.pt');s=build_slot(v,e['policy_id'],rr['missing'])
        require(torch.equal(m['mu'],s['mu']) and torch.equal(m['scale'],s['scale']),'Old model scale changed')
        rr=role(e);aa=N.audit(torch.cat([m['weight'],m['bias'][:,None]],1),s,rr['t'])
        require(aa['max_gradient']<=1e-5,'Old accepted precision audit failed')
        compatibility.append(dict(role_id=e['role_id'],policy_id=e['policy_id'],source=e['source'],**aa))
    write(OUT/'audits/old-endpoint-compatibility.json',dict(passed=True,count=len(compatibility),results=compatibility,new_full_adoption=False))
    for p,h in C.CONTRACT['protected'].items():
        guard();require(sha(ROOT/p)==h,'Protected source changed '+p)
    for p,h in C.CONTRACT['code'].items():require(sha(ROOT/p)==h,'Pilot code changed after seal')
    require(len(C.ATTEMPTS)==58,'Attempt count');require(all(a['status']!='running' for a in C.ATTEMPTS),'Unclosed attempt')
    require(not (OUT/'predictions').exists() and not (OUT/'scores').exists(),'Forbidden business output')
    write(OUT/'verification.json',dict(passed=True,all_52_accepted=True,all_1024_old_endpoints_preserved=True,
          source_hashes_unchanged=True,H_query_reads=0,H_label_reads=0,actual_target_U_reads=0,full_matrix_started=False))
