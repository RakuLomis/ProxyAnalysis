"""Narrow allowlist: no parent H/U packages, scores or learned q assets."""
from common import *

def register():
    configure();require(not (OUT/'manifests/experiment-contract.json').exists(),'Run already registered')
    for p in HERE.glob('*.py'):compile(p.read_text(encoding='utf-8'),str(p),'exec')
    complete=read(PARENT/'completion.json');require(complete['formal_complete'] and complete['passed'],'Parent incomplete')
    require(sha(PARENT/'verification.json')==complete['verification_sha256'],'Parent verification seal changed')
    old=read(PARENT/'manifests/experiment-contract.json')
    require(sha(PARENT/'manifests/experiment-contract.json')==read(PARENT/'manifests/seal.json')['contract_sha256'],'Parent contract changed')
    verified=read(PARENT/'verification.json')['files']
    keep=['id','outer','inner','target','calibration','sources','group','missing','t','eta','train_contents','validation_contents','C_contents','U_contents']
    roles=[{k:r[k] for k in keep} for r in old['roles'] if r['outer']==0]
    inner=[{k:r[k] for k in keep} for r in old['inner_roles'] if r['outer']==0]
    require(len(roles)==12 and len(inner)==144,'Fixed f0 role counts')
    for r in roles:role_permission(r,False)
    for r in inner:
        role_permission(r,True);parent=next(p for p in roles if (p['target'],p['group'])==(r['target'],r['group']))
        require(set(r['train_contents']+r['validation_contents'])==set(parent['train_contents']),'Inner content scope')
        require(not set(r['train_contents']+r['validation_contents'])&set(parent['validation_contents']),'Global H content isolation')
    for r in roles:require(len([e for e in inner if (e['target'],e['group'])==(r['target'],r['group'])])==12,'Twelve equal tasks')
    inputs={};qhash=hashlib.sha256(np.ones(10,dtype=np.float64).tobytes()).hexdigest()
    def add(p,category,kind,rid):
        key=rel(p);require(key in verified and sha(p)==verified[key],'Parent asset lineage '+key)
        inputs[key]=dict(sha256=verified[key],category=category,kind=kind,role_id=rid)
        if p.suffix=='.pt':
            mp=p.with_suffix('.json');mk=rel(mp);require(sha(mp)==verified[mk],'Parent metadata seal')
            m=read(mp);require(m['sha256']==verified[key] and m['kind']==kind and m['role_id']==rid and m.get('safe_roundtrip_passed'),'Parent metadata compatibility')
            if category=='task':require(m['rows']==480 and m['train_only'] and m['q_coordinate_frozen_at_one'] and m['original_W_L2'],'Source task compatibility')
            if category=='initial':require(m['q_sha256']==qhash and m['passed'] and m['coordinate_path']==rel(PARENT/'tasks'/rid/(kind+'.pt')),'Only matching q=1 cached feedback')
            if category=='coefficients':require(m['actual_C_OOF'] and m['outer_coordinates'],'Original actual-C coefficients')
            inputs[mk]=dict(sha256=verified[mk],category='metadata',kind=kind,role_id=rid)
    for r in inner:
        for k in ['P','G']:
            add(PARENT/'tasks'/r['id']/(k+'.pt'),'task',k,r['id'])
            add(PARENT/'feedback-cache'/k/r['id']/(qhash+'.pt'),'initial',k,r['id'])
    for r in roles:
        for k in ['P','G']:add(PARENT/'C-coefficients'/r['id']/(k+'.pt'),'coefficients',k,r['id'])
        for arm in ARMS:
            legacy={'O-DP':'D-P','O-TP':'T-P','O-DG':'D-G'}[arm]
            add(PARENT/'trajectories'/r['id']/(legacy+'.parquet'),'old-source-trajectory',kind_for(arm),r['id'])
    fixed_paths=['eval/calibrated_deployment_transfer/common.py','eval/calibrated_deployment_transfer_v4/numeric_policy.py',
                 'eval/calibrated_deployment_transfer_v4/optimizer_preconditioning.py','eval/dynamic_soft_drift_calibration/amplitude.py',
                 'eval/dynamic_soft_drift_calibration/unroll.py','eval/dynamic_soft_drift_calibration/recovery.py',
                 'eval/dynamic_soft_drift_implicit_pilot/gauge.py','eval/dynamic_soft_drift_implicit_pilot/implicit.py',
                 'eval/dynamic_soft_drift_formal_v2/solution_feedback.py','eval/dynamic_soft_drift_formal_v2/payload.py']
    fixed={}
    for p in fixed_paths:
        h=old['code'].get(p,old['fixed_files'].get(p));require(h is not None and sha(ROOT/p)==h,'Frozen mathematical code changed '+p);fixed[p]=h
    metadata={rel(PARENT/p):sha(PARENT/p) for p in ['completion.json','verification.json','manifests/experiment-contract.json','manifests/seal.json','manifests/numeric-policy.json']}
    e=old['environment'];require(sha(Path(e['installed_LBFGS_path']))==e['installed_LBFGS_sha256'],'Installed solver changed')
    c=dict(version='outer-pilot-v1-launch-repair',registered_unix=time.time(),roles=roles,inner_roles=inner,arms=ARM_KIND,
           launch_repair=dict(old_run='run-01',old_training_started=False,scientific_policy_changed=False,all_modules_compiled=True),
           plan_sha256=sha(PLAN),code={rel(p):sha(p) for p in HERE.glob('*.py')},fixed_code=fixed,parent_metadata=metadata,
           inputs=inputs,q_one_hash=qhash,environment=e,rho=.01,nu=1.,q_range=[0.,2.],metric='1+A/s',
           max_accepted=20,max_trials=40,max_backtracks=8,alphas=[.5**k for k in range(8)],
           active_seconds_cap=14400,amplitude=.1,armijo=1e-4,stationary=1e-3,remaining_ratio=.2,
           improvement=1e-4,direction_floor=1e-12,value_floor=1e-8,small_step=1e-8,
           H_U_reads_forbidden=True,final_business_authorized=False,CPU_fallback=False,old_q_forbidden=True,
           caps=dict(logical_forward=17712,new_source_LR=17712,implicit=18144,refinement=531360,validation=17712,
                     q_updates=720,trial_batches=1440,new_final_LR=0,H_query=0,H_score=0,bootstrap=0))
    write(OUT/'manifests/experiment-contract.json',c);write(OUT/'manifests/seal.json',dict(contract_sha256=sha(OUT/'manifests/experiment-contract.json')))
    write(OUT/'manifests/numeric-policy.json',read(PARENT/'manifests/numeric-policy.json'))
    write(OUT/'ledger.json',{**{k:0 for k in c['caps']},'cache_hits':0,'initial_reuse':0,'active_seconds':0.})
    write(OUT/'parent-integrity.json',dict(passed=True,verified_reused_assets=len(inputs),roles=12,source_tasks=144,
                                       parent_verification_sha256=complete['verification_sha256'],H_U_numeric_read=False))
    progress('registered',roles=12,trajectories=36,source_tasks=144,restricted_inputs=len(inputs))
