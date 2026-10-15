"""Terminal-only original eligibility, with explicit safe fallback semantics."""
from common import *
import quality

ENABLED={'finite_progress','stationary','stationary_at_origin'}
SAFE={'qualified_descent_only','stop_budget','stop_line_search','stop_signal_undetermined','stop_small_step'}

def choose(result,q,integrity=True,global_stop=False):
    require(integrity and not global_stop and result.get('origin_available',False),'Incomplete/integrity failure is not fallback')
    status=result['status'];require(status in ENABLED|SAFE,'Unknown/unsafe terminal status')
    require(torch.isfinite(q).all() and bool(((q>=0)&(q<=2)).all()),'Invalid terminal q')
    enabled=status in ENABLED;require(bool(result['passed'])==enabled,'Qualification/status inconsistency')
    if enabled:
        if status.startswith('stationary'):require(max(result['terminal_residual']['PG_f'],result['terminal_residual']['PG_v'])<=1e-3,'Stationarity gate')
        else:require(result['accepted_updates']==20 and result['finite_progress_conditions'] and result['dual_descent'],'Finite-progress gate')
    elif status=='stop_budget':require(result['trial_evaluations']==40,'Global/unexecuted budget is not safe fallback')
    use=q.clone() if enabled else torch.ones_like(q)
    return dict(enabled=enabled,fallback=not enabled,identity=bool(torch.equal(use,torch.ones_like(use))),q=use)

def publish(r,arm,root,reused=False):
    if reused:
        for p in [root/'result.json',root/'states.parquet',root/'trials.parquet',root/'q00.pt',root/'q00.json']:
            checked(p,contract()['pilot_files'][rel(p)],'pilot-terminal-reuse',kind_for(arm))
    result=read(root/'result.json');k=result['accepted_updates'];endp=root/f'q{k:02d}.pt'
    if reused:
        for p in [endp,endp.with_suffix('.json')]:checked(p,contract()['pilot_files'][rel(p)],'pilot-terminal-reuse',kind_for(arm))
        origin=torch.load(root/'q00.pt',map_location=device(),weights_only=True)['state'];end=torch.load(endp,map_location=device(),weights_only=True)['state']
    else:origin=own(root/'q00.pt')['state'];end=own(endp)['state']
    states=pd.read_parquet(root/'states.parquet');trials=pd.read_parquet(root/'trials.parquet')
    require(len(states)==k+1 and int(states.iloc[-1]['state'])==k and trials.accepted.sum()==k,'Terminal coverage')
    m=own(OUT/'scales'/r['id']/(kind_for(arm)+'.pt'))['M']
    if reused:
        pm=PILOT/'scales'/r['id']/(kind_for(arm)+'.pt');checked(pm,contract()['pilot_files'][rel(pm)],'pilot-fixed-metric')
        require(torch.equal(m,torch.load(pm,map_location=device(),weights_only=True)['M']),'Pilot metric incompatible')
    acc=trials[trials.accepted];require(acc.value_pass.all() and acc.direction_pass.all(),'Nonqualified accepted update')
    # Re-evaluate unchanged original gates; never use a best historical state.
    status='accepted_update_limit' if result['status'] in ['finite_progress','qualified_descent_only'] else result['status']
    replay=quality.conclude(origin,end,m,status,k,True)
    for key in ['status','passed','accepted_updates','finite_progress_conditions','dual_descent','improvement','origin_residual','terminal_residual','residual_ratios']:require(replay[key]==result[key],'Qualification replay mismatch '+key)
    decision=choose(result,end['q']);basearm='P-small' if kind_for(arm)=='P' else 'G-small'
    baseline=next(x for x in contract()['references'] if (x['role_id'],x['arm'])==(r['id'],basearm))
    qpath=OUT/'q-use'/r['id']/(arm+'.pt')
    put(dict(q=decision['q'],q_end=end['q']),qpath,role_id=r['id'],arm=arm,kind=kind_for(arm),original_status=result['status'],selected_state=k,terminal_only=True,enabled=decision['enabled'],fallback=decision['fallback'],identity=decision['identity'])
    out=dict(role_id=r['id'],outer=r['outer'],target=r['target'],group=r['group'],arm=arm,kind=kind_for(arm),original_stop=result['status'],
        enabled=decision['enabled'],fallback=decision['fallback'],identity=decision['identity'],reused_f0=reused,
        q_end=end['q'].tolist(),q_use=decision['q'].tolist(),q_path=rel(qpath),q_sha256=sha(qpath),
        terminal_path=rel(endp),terminal_sha256=sha(endp),trajectory_result_path=rel(root/'result.json'),trajectory_result_sha256=sha(root/'result.json'),
        baseline_arm=basearm,baseline_path=baseline['model_path'],baseline_sha256=baseline['model_sha256'],
        accepted_updates=k,trial_evaluations=result['trial_evaluations'],seconds=result['seconds'],
        qualification_gates_json=json.dumps(replay,sort_keys=True),reason='original_terminal_qualified' if decision['enabled'] else 'fixed_fallback_'+result['status'])
    write(OUT/'decisions'/r['id']/(arm+'.json'),out);return out

def reuse_pilot():
    rows=[]
    for r in contract()['roles']:
        if r['outer']!=0:continue
        for arm,oldarm in {'QP':'O-DP','QT':'O-TP','QG':'O-DG'}.items():rows.append(publish(r,arm,PILOT/'trajectories'/r['id']/oldarm,True))
    require(len(rows)==36 and sum(x['enabled'] for x in rows)==12 and sum(x['fallback'] for x in rows)==24,'Frozen f0 decisions')
    save(pd.DataFrame(rows),OUT/'audits/pilot-reuse-index.parquet');write(OUT/'audits/pilot-reuse.json',dict(passed=True,decisions=36,enabled=12,fallback=24,new_fits=0,old_read_log_complete=False))
    return rows

def seal_all():
    rows=[];files={}
    for r in contract()['roles']:
        for arm in ARMS:
            p=OUT/'decisions'/r['id']/(arm+'.json');require(p.exists(),'Unexecuted role cannot default to fallback');d=read(p)
            q=own(ROOT/d['q_path']);require(q['q'].tolist()==d['q_use'] and sha(ROOT/d['q_path'])==d['q_sha256'],'q-use identity')
            require(d['identity'] or d['enabled'],'Fallback must be identity')
            root=(ROOT/d['trajectory_result_path']).parent
            for path in [p,ROOT/d['q_path'],(ROOT/d['q_path']).with_suffix('.json'),ROOT/d['trajectory_result_path'],ROOT/d['terminal_path'],(ROOT/d['terminal_path']).with_suffix('.json'),root/'states.parquet',root/'trials.parquet']:files[rel(path)]=sha(path)
            rows.append(d)
    require(len(rows)==180,'All strategy decisions required');df=pd.DataFrame(rows);save(df,OUT/'manifests/policy-decisions.parquet');files[rel(OUT/'manifests/policy-decisions.parquet')]=sha(OUT/'manifests/policy-decisions.parquet')
    save(df.groupby(['target','outer','group','arm'])[['enabled','fallback','identity']].sum().reset_index(),OUT/'audits/activation-by-role.parquet')
    write(OUT/'manifests/policy-complete.json',dict(passed=True,files=files,endpoints=180,enabled=int(df.enabled.sum()),fallback=int(df.fallback.sum()),H_numeric_read=False))
    return df

