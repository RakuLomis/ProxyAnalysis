"""Independent artifact, loss, actual-step and budget replay."""
from common import *

def verify():
    c=contract();n=0;accepted=0;qualified=0;worst=0.;reads=[]
    for stagefile in (OUT/'stages').glob('*.json'):reads.extend(read(stagefile)['reads'])
    reads.extend(ACCESS)
    allowed=set(c['inputs'])|set(c['code'])|set(c['fixed_code'])|set(c['parent_metadata'])|{rel(PLAN)}
    for a in reads:
        p=Path(a['path']);path=a['path']
        require(path in allowed or (ROOT/p).resolve().is_relative_to(OUT) or path==c['environment']['installed_LBFGS_path'],'Forbidden recorded read '+path)
    for path,info in c['inputs'].items():checked(ROOT/path,info['sha256'],'final-parent-integrity')
    for r in c['roles']:
        for arm in ARMS:
            root=OUT/'trajectories'/r['id']/arm;p=root/'result.json'
            if not p.exists():continue
            result=read(p);n+=1;qualified+=int(result['passed']);sp=root/'states.parquet'
            if not sp.exists():continue
            d=pd.read_parquet(sp);t=pd.read_parquet(root/'trials.parquet') if (root/'trials.parquet').exists() else pd.DataFrame()
            require(len(d)==result['accepted_updates']+1 and len(d)<=21 and result['trial_evaluations']<=40,'Trajectory budget')
            coeff=None
            if arm!='O-TP':coeff=parent_asset(PARENT/'C-coefficients'/r['id']/(kind_for(arm)+'.pt'),'coefficients',kind_for(arm),r['id'],arm)
            for _,s in d.iterrows():
                q=tensor(s.q);require(bool(((q>=0)&(q<=2)).all()),'Saved q range')
                shrink=float(.001*(q-1).square().sum())
                if coeff is None:pen=0.
                else:pen=float(((q-1)*(coeff['A']*(q+1)-2*coeff['B'])/coeff['s']).clamp_min(0).square().sum()/20)
                err=max(abs(shrink-s.shrink),abs(pen-s.penalty),abs(s.Q_f+shrink+pen-s.L_f),abs(s.Q_v+shrink+pen-s.L_v));worst=max(worst,err)
                require(err<1e-12,'Independent saved target replay')
                for suffix in ['f','v']:
                    g=tensor(s['g_'+suffix]);pg=float((q-(q-g).clamp(0,2)).abs().max())
                    require(abs(pg-s['PG_'+suffix])<1e-12,'Original projected residual replay')
                own(root/f'q{int(s.state):02d}.pt')
            if not t.empty:
                for _,tr in t[t.accepted].iterrows():
                    before=d.iloc[int(tr.iteration)-1];after=d.iloc[int(tr.iteration)];delta=tensor(after.q)-tensor(before.q)
                    require(float((delta-tensor(tr.delta)).abs().max())<1e-14,'Actual projected displacement')
                    gf=tensor(before.g_f);gv=tensor(before.g_v);sf=float(gf@delta);sv=float(gv@delta)
                    td=float(((gf-gv).abs()*delta.abs()).sum())+1e-12*max(1.,abs(sf),abs(sv))
                    tv=1e-8*max(1.,abs(before.L_f),abs(after.L_f));bound=min(before.L_f,before.L_v)+1e-4*min(sf,sv)-tv
                    require(max(sf,sv)<-td and max(after.L_f,after.L_v)<=bound,'Independent dual Armijo replay')
                    require(tr.reason=='dual_descent_and_gradient_qualified','Accepted without derivative qualification');accepted+=1
            if result['status']=='finite_progress':
                a,z=d.iloc[0],d.iloc[-1];require(result['accepted_updates']==20 and z.PG_f<=.2*a.PG_f and z.PG_v<=.2*a.PG_v and min(a.L_f,a.L_v)-max(z.L_f,z.L_v)>=1e-4*max(1,abs(a.L_f)),'Finite progress mislabelled')
            if result['status'].startswith('stationary'):
                z=d.iloc[-1];require(max(z.PG_f,z.PG_v)<=1e-3,'Stationarity mislabelled')
    l=read(OUT/'ledger.json');require(accepted==l['q_updates'],'Update ledger mismatch')
    for k,v in c['caps'].items():require(l[k]<=v,'Budget replay '+k)
    require(all(l[k]==0 for k in ['new_final_LR','H_query','H_score','bootstrap']),'Unauthorized business work')
    for root in ['gradient-cache','value-cache']:
        for mp in (OUT/root).rglob('*.json'):
            meta=read(mp);require(meta['safe_roundtrip_passed'] and sha(mp.with_suffix('.pt'))==meta['sha256'],'Unsafe/changed feedback publication')
    files={rel(p):sha(p) for p in OUT.rglob('*') if p.is_file() and p.name not in ['completion.json','verification.json','progress.json','stage.lock'] and 'stages' not in p.parts}
    files[rel(DOC/'pilot-results.md')]=sha(DOC/'pilot-results.md')
    v=dict(passed=True,completed_trajectories=n,qualified_trajectories=qualified,accepted_updates=accepted,objective_replay_max_error=worst,
           H_U_reads=0,business_models=0,parent_reused_files_unchanged=True,old_models_reused=False,files=files)
    write(OUT/'verification.json',v);completion=read(OUT/'completion.json');completion['verification_sha256']=sha(OUT/'verification.json');write(OUT/'completion.json',completion)
    progress('verification_complete',qualified=qualified,completed=n,accepted_updates=accepted)
