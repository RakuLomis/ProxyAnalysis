"""User-authorized, byte-preserving continuation of an interrupted pilot."""
from common import *
OLD=ROOT/'outputs/dynamic-soft-drift-outer-pilot-20261013/run-02'

def register():
    configure();require(not OUT.exists(),'Recovery destination must be new')
    for p in HERE.glob('*.py'):compile(p.read_text(encoding='utf-8'),str(p),'exec')
    old=read(OLD/'manifests/experiment-contract.json')
    require(sha(OLD/'manifests/experiment-contract.json')==read(OLD/'manifests/seal.json')['contract_sha256'],'Old contract seal')
    require(not (OLD/'completion.json').exists(),'Only interrupted pilot can continue')
    for p,h in {**old['code'],**old['fixed_code'],**old['parent_metadata']}.items():require(sha(ROOT/p)==h,'Old lineage changed '+p)
    rows=[];completed=[];active=[];allaccepted=0;done_trials=0
    for r in old['roles']:
        for arm in ARMS:
            root=OLD/'trajectories'/r['id']/arm;sp=root/'states.parquet';rp=root/'result.json'
            if rp.exists():
                z=read(rp);completed.append(dict(role_id=r['id'],arm=arm,result_sha256=sha(rp)))
                done_trials+=z['trial_evaluations']
            if not sp.exists():continue
            d=pd.read_parquet(sp);t=pd.read_parquet(root/'trials.parquet');require(len(d)-1==int(t.accepted.sum()),'Checkpoint/accepted table mismatch')
            for k,(_,s) in enumerate(d.iterrows()):
                p=root/f'q{k:02d}.pt';m=read(p.with_suffix('.json'))
                require(m['accepted'] and m['safe_roundtrip_passed'] and sha(p)==m['sha256'],'Unqualified recovery checkpoint')
            for _,tr in t[t.accepted].iterrows():
                a=d.iloc[int(tr.iteration)-1];z=d.iloc[int(tr.iteration)];delta=np.asarray(z.q)-np.asarray(a.q);gf=np.asarray(a.g_f);gv=np.asarray(a.g_v)
                sf=float(gf@delta);sv=float(gv@delta);td=float((np.abs(gf-gv)*np.abs(delta)).sum())+1e-12*max(1,abs(sf),abs(sv));tl=1e-8*max(1,abs(a.L_f),abs(z.L_f))
                require(max(sf,sv)<-td and max(z.L_f,z.L_v)<=min(a.L_f,a.L_v)+1e-4*min(sf,sv)-tl,'Recovered Armijo replay')
            allaccepted+=len(d)-1
            if not rp.exists():active.append(dict(role=r,arm=arm,accepted=len(d)-1,evaluations=int(t.forward_evaluated.sum()),last_q=d.iloc[-1].q.tolist()))
    ledger_old=read(OLD/'ledger.json');require(allaccepted==ledger_old['q_updates'] and len(active)==1,'Interrupted accepted-state accounting')
    a=active[0];r=a['role'];arm=a['arm'];kind=kind_for(arm);root=OLD/'trajectories'/r['id']/arm
    cp=root/f"q{a['accepted']:02d}.pt";state=torch.load(cp,map_location=device(),weights_only=True)['state']
    m=torch.load(OLD/'scales'/r['id']/(kind+'.pt'),map_location=device(),weights_only=True)['M']
    import projected_step as PS
    p,gamma=PS.direction(state['g_f'],m);nq,delta=PS.candidate(state['q'],p,1.)
    qhash=hashlib.sha256(nq.cpu().numpy().tobytes()).hexdigest()
    require(done_trials+a['evaluations']+1==ledger_old['trial_batches'],'Exactly one reserved pending trial required')
    rs=[e for e in old['inner_roles'] if (e['target'],e['group'])==(r['target'],r['group'])]
    published=[];unpublished=[]
    for e in rs:
        vp=OLD/'value-cache'/kind/e['id']/(qhash+'.pt');lp=OLD/'feedback-logs'/kind/e['id']/(qhash+'.json')
        if vp.exists() and vp.with_suffix('.json').exists():
            vm=read(vp.with_suffix('.json'));require(vm['forward_passed'] and sha(vp)==vm['sha256'],'Pending cache publication invalid');published.append(e['id'])
        elif lp.exists():
            log=read(lp);require(log['status']=='attempting' and np.array_equal(np.asarray(log['q']),nq.cpu().numpy()),'No retry of failed numeric points');unpublished.append(e['id'])
    require(published and len(unpublished)==1,'One interrupted, not failed, inner fit required')
    require(ledger_old['logical_forward']==(len(completed)+1+ledger_old['trial_batches'])*12,'Logical batches accounted')
    pending=dict(role_id=r['id'],arm=arm,kind=kind,accepted_state=a['accepted'],evaluation=a['evaluations']+1,
                 q=nq.tolist(),q_sha256=qhash,alpha=1.,backtrack=0,logical_batch_reserved=True,
                 qualified_cached_tasks=published,interrupted_task=unpublished[0],old_partial_seconds=float(read(OLD/'progress.json')['seconds']))
    # Runtime outputs are copied mechanically; authored source and old outputs remain unchanged.
    files={};copied=0;total_bytes=0
    for directory in ['scales','tables','tests','trajectories','value-cache','gradient-cache','feedback-logs','diagnostic-fit-logs']:
        src=OLD/directory
        if not src.exists():continue
        for p in src.rglob('*'):
            if not p.is_file() or p.name.endswith('.tmp'):continue
            if p.suffix=='.pt':
                require(p.with_suffix('.json').exists(),'Unpublished checkpoint cannot be imported')
                meta=read(p.with_suffix('.json'));require(meta.get('safe_roundtrip_passed') and sha(p)==meta['sha256'],'Unsafe copied asset')
            dest=writable(OUT/p.relative_to(OLD));require(not dest.exists(),'Recovery copy overwrite')
            shutil.copy2(p,dest);h=sha(dest);require(h==sha(p),'Recovery byte copy');files[rel(p)]=h;copied+=1;total_bytes+=p.stat().st_size
    c=dict(old);c['version']='outer-pilot-v1-controlled-recovery';c['code']={rel(p):sha(p) for p in HERE.glob('*.py')}
    c['fixed_code']={**old['fixed_code'],**old['code']}
    c['parent_metadata']={**old['parent_metadata'],**{rel(OLD/p):sha(OLD/p) for p in ['manifests/experiment-contract.json','manifests/seal.json','ledger.json','progress.json','ready.json']}}
    c['recovery']=dict(user_authorized=True,old_run=rel(OLD),completed=completed,pending=pending,old_files=files,
                       inherited_active_seconds=ledger_old['active_seconds'],unaccounted_tail_reserve_seconds=60.,
                       scientific_policy_changed=False,quality_policy_changed=False,automatic_restart=False)
    c['registered_unix']=time.time()
    write(OUT/'manifests/experiment-contract.json',c);write(OUT/'manifests/seal.json',dict(contract_sha256=sha(OUT/'manifests/experiment-contract.json')))
    write(OUT/'manifests/numeric-policy.json',read(OLD/'manifests/numeric-policy.json'))
    ledger_old['active_seconds']+=60.;ledger_old.update(recovery_trial_replays=0,recovery_cache_hits=0)
    write(OUT/'ledger.json',ledger_old);write(OUT/'ready.json',dict(passed=True,trajectories=36,business_authorized=False,controlled_recovery=True))
    write(OUT/'recovery-audit.json',dict(passed=True,completed_trajectories=len(completed),accepted_updates=allaccepted,
                                     copied_files=copied,copied_bytes=total_bytes,pending=pending,old_run_unchanged=True,
                                     inherited_ledger=ledger_old,unaccounted_tail_reserve_seconds=60.,restart_from_zero=False))
    progress('recovery_registered',completed=len(completed),accepted_updates=allaccepted,pending_state=a['accepted'],cached_pending_tasks=len(published))
