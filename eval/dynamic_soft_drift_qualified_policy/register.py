"""Register the human-approved strategy; no numeric H/U reads."""
from common import *

def run():
    configure();require(not (OUT/'manifests/seal.json').exists(),'Run already registered')
    for p in HERE.glob('*.py'):
        if p.name!='closeout.py':compile(p.read_text(encoding='utf-8'),str(p),'exec')
    old=read(PARENT/'manifests/experiment-contract.json');complete=read(PARENT/'completion.json')
    require(complete['formal_complete'] and complete['passed'],'Parent incomplete')
    require(sha(PARENT/'verification.json')==complete['verification_sha256'],'Parent verification changed')
    require(sha(PARENT/'manifests/experiment-contract.json')==read(PARENT/'manifests/seal.json')['contract_sha256'],'Parent contract changed')
    verified=read(PARENT/'verification.json')['files'];immutable=read(CLOSEOUT/'manifests/immutable-input-seal.json')['files']
    p0=read(CLOSEOUT/'completion.json');require(p0['passed'],'P0 failed')
    require(sha(CLOSEOUT/'verification.json')=='ab3d979fe886072b0cd0ac7b57518b68c6a1ac3e0d4ca2dd62d65df61c51481f','P0 verification changed')
    pc=read(PILOT/'manifests/experiment-contract.json')
    for name,value in dict(rho=.01,nu=1.,max_accepted=20,max_trials=40,max_backtracks=8,amplitude=.1,armijo=1e-4,stationary=1e-3,remaining_ratio=.2,improvement=1e-4,direction_floor=1e-12,value_floor=1e-8,small_step=1e-8).items():
        require(pc[name]==value,'Pilot optimizer incompatible '+name)
    roles=old['roles'];inner=old['inner_roles'];require(len(roles)==60 and len(inner)==720,'Role counts')
    for r in roles:role_permission(r,False)
    for r in inner:
        role_permission(r,True);o=next(v for v in roles if (v['outer'],v['target'],v['group'])==(r['outer'],r['target'],r['group']))
        require(set(r['train_contents']+r['validation_contents'])==set(o['train_contents']),'Source content partition')
        require(not set(r['train_contents']+r['validation_contents'])&set(o['validation_contents']),'Global content leakage')
        require(set(r['sources']+[r['calibration']])==set(o['sources']),'Target source leakage')
    for r in roles:require(sum((e['outer'],e['target'],e['group'])==(r['outer'],r['target'],r['group']) for e in inner)==12,'Twelve source tasks')
    for fold in range(5):
        sets={tuple(r['validation_contents']) for r in roles if r['outer']==fold};require(len(sets)==1,'Global content fold mismatch')
    inputs={};assets={};qhash=hashlib.sha256(np.ones(10,dtype=np.float64).tobytes()).hexdigest()
    def add(p,category,kind,rid):
        key=rel(p);require(key in verified and sha(p)==verified[key],'Parent asset lineage '+key)
        inputs[key]=dict(sha256=verified[key],category=category,kind=kind,role_id=rid)
        if p.suffix=='.pt':
            mp=p.with_suffix('.json');mk=rel(mp);require(mk in verified and sha(mp)==verified[mk],'Parent metadata seal '+mk)
            m=read(mp);require(m['sha256']==verified[key] and m['kind']==kind and m['role_id']==rid and m.get('safe_roundtrip_passed'),'Unsafe/wrong parent asset')
            if category=='task':require(m['rows']==(480 if '/outer' not in rid else 928) and m['train_only'] and m['q_coordinate_frozen_at_one'] and m['original_W_L2'],'Task policy mismatch')
            if category=='initial':require(m['q_sha256']==qhash and m['passed'] and m['coordinate_path']==rel(PARENT/'tasks'/rid/(kind+'.pt')),'Only q=1 feedback reusable')
            if category=='coefficients':require(m['actual_C_OOF'] and m['outer_coordinates'],'Actual C coefficient scope')
            inputs[mk]=dict(sha256=verified[mk],category='metadata',kind=kind,role_id=rid)
    def asset(p,purpose,rid,expected=None):
        key=rel(p);h=expected or old['artifacts'][key]['sha256']
        require(sha(p)==h,'External asset changed '+key);assets[key]=dict(sha256=h,purpose=purpose,role_id=rid)
        if p.suffix=='.pt':
            mp=p.with_suffix('.json');mh=verified.get(rel(mp),old['fixed_files'].get(rel(mp)))
            require(mh is not None and sha(mp)==mh and read(mp)['sha256']==h,'External metadata lineage '+rel(mp))
            assets[rel(mp)]=dict(sha256=mh,purpose='metadata',role_id=rid)
    for r in inner:
        for k in ['P','G']:
            add(PARENT/'tasks'/r['id']/(k+'.pt'),'task',k,r['id'])
            add(PARENT/'feedback-cache'/k/r['id']/(qhash+'.pt'),'initial',k,r['id'])
    for r in roles:
        asset(ROOT/r['reuse_views'],'combined-baseline-view',r['id'])
        for k in ['P','G']:
            add(PARENT/'tasks'/r['id']/(k+'.pt'),'task',k,r['id'])
            add(PARENT/'C-coefficients'/r['id']/(k+'.pt'),'coefficients',k,r['id'])
            asset(ROOT/r['reuse_maps'][k],'map-'+k,r['id'])
    for ref in old['references']:asset(ROOT/ref['model_path'],'reference',ref['role_id'],ref['model_sha256'])
    pilot_files={}
    for r in roles:
        if r['outer']!=0:continue
        for arm,oa in {'QP':'O-DP','QT':'O-TP','QG':'O-DG'}.items():
            root=PILOT/'trajectories'/r['id']/oa
            result=read(root/'result.json')
            for p in [root/'result.json',root/'states.parquet',root/'trials.parquet',root/'q00.pt',root/'q00.json',root/f"q{result['accepted_updates']:02d}.pt",root/f"q{result['accepted_updates']:02d}.json",PILOT/'scales'/r['id']/(kind_for(arm)+'.pt')]:
                key=rel(p);require(key in immutable and sha(p)==immutable[key],'P0 immutable pilot changed '+key);pilot_files[key]=immutable[key]
    fixed={}
    for name in ['eval/calibrated_deployment_transfer/common.py','eval/calibrated_deployment_transfer_v4/numeric_policy.py','eval/calibrated_deployment_transfer_v4/optimizer_preconditioning.py','eval/dynamic_soft_drift_calibration/amplitude.py','eval/dynamic_soft_drift_calibration/unroll.py','eval/dynamic_soft_drift_calibration/recovery.py','eval/dynamic_soft_drift_implicit_pilot/gauge.py','eval/dynamic_soft_drift_implicit_pilot/implicit.py','eval/dynamic_soft_drift_formal_v2/solution_feedback.py','eval/dynamic_soft_drift_formal_v2/payload.py']:
        h=old['code'].get(name,old['fixed_files'].get(name));require(h is not None and sha(ROOT/name)==h,'Mathematics changed '+name);fixed[name]=h
    metadata={rel(p):sha(p) for p in [PARENT/'completion.json',PARENT/'verification.json',PARENT/'manifests/experiment-contract.json',PARENT/'manifests/seal.json',CLOSEOUT/'verification.json',CLOSEOUT/'manifests/immutable-input-seal.json',PILOT/'manifests/experiment-contract.json',PILOT/'completion.json']}
    e=old['environment'];require(sha(Path(e['installed_LBFGS_path']))==e['installed_LBFGS_sha256'],'Installed solver changed')
    inherited=read(CLOSEOUT/'global-costs.json')['ledger'];require(inherited['active_seconds']==8293.487963500433,'Inherited time changed')
    packages={rel(PREP/'packages'/r['id']/fn):old['packages'][rel(PREP/'packages'/r['id']/fn)] for r in roles for fn in ['query.parquet','labels.parquet']}
    approval=dict(human_confirmed=True,date='2026-10-13',qualification='original',fallback='fixed-original-model',optimization_seconds_cap=72000,C_overall_F1_cost_max=.01,C_deployment_F1_cost_max=.02,authorized_stages=['P1','P2','P3','P4'],automatic_research_extension=False)
    c=dict(version='qualified-policy-v1',registered_unix=time.time(),roles=roles,inner_roles=inner,arms=ARM_KIND,approval=approval,
        plan_sha256=sha(PLAN),code={rel(p):sha(p) for p in HERE.glob('*.py') if p.name!='closeout.py'},fixed_code=fixed,parent_metadata=metadata,
        inputs=inputs,assets=assets,pilot_files=pilot_files,packages=packages,references=old['references'],q_one_hash=qhash,environment=e,
        inherited_ledger=inherited,rho=.01,nu=1.,q_range=[0.,2.],metric='1+A/s',max_accepted=20,max_trials=40,max_backtracks=8,alphas=[.5**k for k in range(8)],
        active_seconds_cap=72000,amplitude=.1,armijo=1e-4,stationary=1e-3,remaining_ratio=.2,improvement=1e-4,direction_floor=1e-12,value_floor=1e-8,small_step=1e-8,
        final_business_authorized=True,CPU_fallback=False,old_learned_q_forbidden=True,actual_target_U_fit_forbidden=True,
        caps=dict(logical_forward=70848,new_source_LR=70848,implicit=72576,refinement=2125440,validation=70848,q_updates=2880,trial_batches=5760,new_final_LR=156,H_query=60,H_score=60,bootstrap=10000))
    write(OUT/'manifests/experiment-contract.json',c);write(OUT/'manifests/seal.json',dict(contract_sha256=sha(OUT/'manifests/experiment-contract.json')))
    write(OUT/'manifests/numeric-policy.json',read(PARENT/'manifests/numeric-policy.json'));write(OUT/'manifests/user-approval.json',approval)
    for p in HERE.glob('*.py'):
        if p.name!='closeout.py':
            dest=writable(OUT/'source-snapshot'/p.name);shutil.copyfile(p,dest);require(sha(dest)==c['code'][rel(p)],'Source snapshot mismatch')
    write(OUT/'ledger.json',{**{k:0 for k in c['caps']},'cache_hits':0,'initial_reuse':0,'active_seconds':inherited['active_seconds']})
    write(OUT/'membership-audit.json',dict(passed=True,roles=60,inner_tasks=720,global_content_isolation=True,target_excluded_from_source_feedback=True,numeric_H_U_reads=0))
    progress('registered',roles=60,source_tasks=720,remaining_trajectories=144,approved_global_hours=20)
