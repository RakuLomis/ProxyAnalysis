"""Authorized minimal AD1 2x2; two new policies, no new mappings or tuning."""
import time
LOAD_START=time.perf_counter()
from common import *
import common as C
from weight_schedule import registry,slot,A,B,C_NEW,D_NEW,BASELINE
from backend import modules,audit,source_log,fit as numeric_fit

def register():
    with stage('R0'):
        parent=read(PARENT/'manifests/contract.json')
        require(sha(PARENT/'manifests/contract.json')==read(PARENT/'manifests/seal.json')['sha256'],'Parent contract seal')
        comp=read(PARENT/'completion.json');ver=read(PARENT/'verification.json')
        require(comp['program_complete'] and ver['passed'],'Parent full run incomplete')
        require(sha(PARENT/'verification.json')==comp['verification_sha256'],'Parent verification changed')
        require(not OUT.joinpath('manifests/seal.json').exists(),'No overwrite/restart of AD1 contract')
        fixed=dict(parent['fixed']);arts=dict(parent['artifacts'])
        def fix(p,expected=None):
            h=sha(p);require(expected is None or h==expected,'Changed registration source '+rel(p))
            fixed[rel(p)]=h;checked(p,h,'registration');return h
        for p,h in parent['code'].items():fix(ROOT/p,h)
        for p in [PARENT/'manifests/contract.json',PARENT/'manifests/seal.json',PARENT/'completion.json',
                  PARENT/'verification.json',PARENT/'cost-final.json',PARENT/'manifests/endpoints.parquet',
                  PARENT/'manifests/endpoint-seal.json',PARENT/'predictions/complete.json',
                  PARENT/'comparisons/primary.json',PARENT/'comparisons/bootstrap.npz']:
            fix(p)
        fix(ROOT/'docs/role-asymmetric-transfer-v1-20261017/full-nr2/complete-report.md',ver['report_sha256'])
        require(sha(Path(inspect.getfile(torch.optim.LBFGS)))==parent['environment']['installed_LBFGS_sha256'],'Installed solver changed')
        ends=pd.read_parquet(PARENT/'manifests/endpoints.parquet')
        require(sha(PARENT/'manifests/endpoints.parquet')==read(PARENT/'manifests/endpoint-seal.json')['sha256'],'Parent endpoint seal')
        old=ends[ends.policy_id.isin([A,B,BASELINE])].replace({np.nan:None}).to_dict('records')
        require(len(old)==180,'180 reuse endpoints')
        for e in old:
            p=ROOT/e['path'];fix(p,e['sha256']);arts[rel(p)]=e['sha256'];fix(p.with_suffix('.json'))
            if e.get('result_path'):fix(ROOT/e['result_path'],e['result_sha256'])
            if e.get('slot_path'):
                sp=ROOT/e['slot_path'];arts[rel(sp)]=fix(sp);fix(sp.with_suffix('.json'))
        # Source numerical function bodies are bound by the prior frozen code hashes.
        for p in [NR2_CODE/'numeric.py',NR2_CODE/'legacy_prefix.py',LEGACY/'solver_v4.py']:
            require(rel(p) in fixed,'Unbound numerical source');fix(p,fixed[rel(p)])
        write(OUT/'manifests/numeric-policy.json',read(PARENT/'manifests/numeric-policy.json'))
        fix(OUT/'manifests/numeric-policy.json')
        roles=parent['roles'];require(len(roles)==60,'Role coverage')
        eng=[dict(role_id=r['id'],policy_id=p) for r in roles if r['outer']==0 and r['group']=='G0' for p in [C_NEW,D_NEW]]
        require(len(eng)==8 and len({next(r['target'] for r in roles if r['id']==x['role_id']) for x in eng})==4,'Fixed engineering design')
        own={rel(p):sha(p) for p in Path(__file__).parent.glob('*.py')}
        c=dict(version='RA1-AD1-minimal-2x2',roles=roles,policies=registry(),adopted=old,
            engineering_cases=eng,packages=parent['packages'],fixed=fixed,artifacts=arts,code=own,
            plan_sha256=sha(PLAN),parent_contract_sha256=sha(PARENT/'manifests/contract.json'),
            new_fit_cap=120,reuse_count=180,logical_endpoints=300,logical_predictions=7200,new_policy_predictions=2880,
            cumulative_cap_seconds=28800,prior_activity=read(OUT/'manifests/prior-activity.json'),
            prior_optimization_attempts=1993,total_lineage_cap=2348,environment=parent['environment'],
            fixed_comparisons=[['D','A'],['C','A'],['B','C'],['D','B']],
            bootstrap=dict(samples=10000,seed=20261017,stratify='6 business classes; 5 contents each',
                           family_size=4,marginal_coverage=.9875,quantile_method='linear'),
            no_H_selection=True,no_new_mapping=True,no_new_regularizer=True,retrospective_internal_evaluation=True,
            original_failure_sha256=parent['original_failure_sha256'],full_NR1_failure_sha256=parent['full_NR1_failure_sha256'])
        write(OUT/'manifests/contract.json',c);write(OUT/'manifests/seal.json',dict(sha256=sha(OUT/'manifests/contract.json')))
        textfile(DOC/'execution-contract.md',PLAN.read_text(encoding='utf-8'))
        progress('AD1_contract_sealed',new_fit_cap=120,reuse=180)

def engineering_and_adopt():
    with stage('P2'):
        c=contract();pol={p['id']:p for p in registry()};rows=[];ledgers=[];checks=[]
        n,l=modules();require(l.backend().SETTINGS['max_iter']==4000 and l.backend().SETTINGS['max_eval']==20000,'Numeric resource policy')
        for r in c['roles']:
            budget_check();v=artifact(trainpath(r))
            require(len(v['main_y'])==len(v['P_y'])==288 and len(v['C_y'])==64,'352 real visits')
            require(len(r['train_contents'])==24 and len(r['validation_contents'])==6 and not(set(r['train_contents'])&set(r['validation_contents'])),'Global content split')
            for p in registry():
                s,ledger=slot(v,p,r['missing'],ledger=True)
                ledgers.extend(dict(role_id=r['id'],policy_id=p['id'],**x) for x in ledger)
                expected_rows=736 if p['rho_C']==0 else 928
                require(len(s['y'])==expected_rows,'Expected retained rows')
                if not p['existing']:
                    sp=OUT/'numeric-slots'/r['id']/(p['id']+'.pt')
                    put(sp,s,role_id=r['id'],policy_id=p['id'],capability='source-and-C-only',t=r['t'],eta=r['eta'])
                    continue
                e=next(e for e in c['adopted'] if e['role_id']==r['id'] and e['policy_id']==p['id'])
                m=artifact(ROOT/e['path'])
                require(float(e['t'])==r['t'] and float(e['eta'])==r['eta'],'Inherited hyperparameters changed')
                if e.get('slot_path'):
                    old=artifact(ROOT/e['slot_path']);require(all(torch.equal(s[k],old[k]) for k in s),'Old slot incompatibility')
                a=audit(m,s,r['t'],source_log(e),(int(e['source_max_iter']),int(e['source_max_eval'])),e['source_kind'])
                # Fixed training-input forward, not H, for the adapter arithmetic.
                probe=s['x'][:8];z=probe@m['weight'].T+m['bias']
                require(z.is_cuda and z.dtype==torch.float64 and torch.isfinite(z).all(),'CUDA inference binding')
                row=dict(e);row.update(**a,reused=True,adopted_before_H=True);rows.append(row)
                checks.append(dict(role_id=r['id'],policy_id=p['id'],**a,retained_rows=len(s['y'])))
        require(len(rows)==180 and len(list((OUT/'numeric-slots').rglob('*.pt')))==120,'Adapter coverage')
        save(pd.DataFrame(rows),OUT/'manifests/adopted-endpoints.parquet')
        save(pd.DataFrame(ledgers),OUT/'audits/weight-ledger.parquet')
        save(pd.DataFrame(checks),OUT/'audits/adopted-original-coordinate.parquet')
        write(OUT/'audits/engineering.json',dict(passed=True,new_mapping_fits=0,actual_new_LR_fits=0,
            exact_slot_function_body=True,new_training_slots=120,adopted=180,H_reads=0,
            scientific_objective_unchanged=True,numeric_policy_unchanged=True))
        progress('AD1_engineering_and_reuse_passed',reused=180,prepared=120)

def fit_one(r,p):
    budget_check();pid=p['id'];sp=OUT/'numeric-slots'/r['id']/(pid+'.pt');s=artifact(sp)
    ap=OUT/'attempts'/r['id']/(pid+'.json');require(not ap.exists(),'No implicit retry')
    write(ap,dict(started_unix=time.time(),role_id=r['id'],policy_id=pid,slot_sha256=sha(sp)))
    attempts=len(list((OUT/'attempts').rglob('*.json')))
    require(attempts<=120 and 1993+attempts<=2348,'New/lineage fit cap')
    m,log=numeric_fit(s,r['t'],dict(role_id=r['id'],arm=pid,t=r['t'],eta=r['eta'],execution_policy='AD1-unchanged-NR2',
        input_sha256=sha(sp),rho_C=p['rho_C'],rho_U=p['rho_U']))
    a=audit(m,s,r['t'],log,(4000,20000),'NR2');mp=modelpath(r,p)
    put(mp,m,role_id=r['id'],policy_id=pid,optimizer=log,slot_sha256=sha(sp))
    lp=OUT/'fit-logs'/r['id']/f'{pid}-t{r["t"]:g}.json'
    row=dict(role_id=r['id'],policy_id=pid,path=rel(mp),sha256=sha(mp),slot_path=rel(sp),source='AD1-new',source_kind='NR2',
        result_path=rel(lp),result_sha256=sha(lp),source_policy_path=rel(OUT/'manifests/numeric-policy.json'),
        source_policy_sha256=log['numeric_policy_sha256'],source_max_iter=4000,source_max_eval=20000,
        target=r['target'],group=r['group'],outer=r['outer'],reused=False,t=r['t'],eta=r['eta'],seconds=log['seconds'],
        iterations=log['total_updates'],lbfgs_updates=log['lbfgs_updates'],newton_updates=log['newton_updates'],
        evaluations=log['function_evaluations'],**a)
    write(OUT/'new-endpoints'/r['id']/(pid+'.json'),row);return row

def pilot():
    with stage('E1'):
        c=contract();roles={r['id']:r for r in c['roles']};pol={p['id']:p for p in registry()};rows=[]
        for case in c['engineering_cases']:rows.append(fit_one(roles[case['role_id']],pol[case['policy_id']]))
        slow=max(r['seconds'] for r in rows);estimate=max(600.,3*112*slow+600.)
        passed=spent()+estimate<28680
        write(OUT/'audits/pilot-budget.json',dict(passed=passed,pilot_cases=8,all_numeric_accepted=True,H_reads=0,
            pilot_solver_seconds=sum(x['seconds'] for x in rows),slowest_seconds=slow,remaining_new_fits=112,
            conservative_remaining_estimate_seconds=estimate,cumulative_at_gate=spent(),cap_seconds=28800))
        require(passed,'AD1 conservative budget gate: confirmation required')
        progress('AD1_fixed_pilot_passed',accepted=8,remaining=112,estimate_seconds=estimate)

def fit_rest():
    with stage('P3'):
        require(read(OUT/'audits/pilot-budget.json')['passed'],'No budget qualification')
        done={(e['role_id'],e['policy_id']) for e in contract()['engineering_cases']}
        for r in contract()['roles']:
            for p in registry():
                if p['existing'] or (r['id'],p['id']) in done:continue
                fit_one(r,p)
                completed=len(list((OUT/'new-endpoints').rglob('*.json')))
                if completed%12==0:progress('AD1_new_fitting',completed=completed,total=120)
        rows=[read(p) for p in sorted((OUT/'new-endpoints').rglob('*.json'))]
        require(len(rows)==120,'120 new endpoint count');save(pd.DataFrame(rows),OUT/'manifests/new-endpoints.parquet')

def seal():
    with stage('P4'):
        ends=pd.concat([pd.read_parquet(OUT/'manifests/adopted-endpoints.parquet'),pd.read_parquet(OUT/'manifests/new-endpoints.parquet')],ignore_index=True).replace({np.nan:None})
        require(len(ends)==300 and not ends.duplicated(['role_id','policy_id']).any(),'All 300 endpoints')
        pol={p['id']:p for p in registry()};audits=[];risks=[]
        for r in contract()['roles']:
            v=artifact(trainpath(r))
            for e in ends[ends.role_id.eq(r['id'])].to_dict('records'):
                budget_check();m=artifact(ROOT/e['path']);s=slot(v,pol[e['policy_id']],r['missing'])
                a=audit(m,s,r['t'],source_log(e),(int(e['source_max_iter']),int(e['source_max_eval'])),e['source_kind'])
                audits.append(dict(role_id=r['id'],policy_id=e['policy_id'],**a,L2=float(.0005*(1+r['t'])*m['weight'].square().sum())))
                for nm in ['main','S','P','C']:
                    xx,yy,mm=v[nm+'_x'],v[nm+'_y'],v[nm+'_mass'];zz=xx@m['weight'].T+m['bias']
                    ce=zz.logsumexp(1)-zz.gather(1,yy[:,None]).flatten()
                    for scope in ['C','U']:
                        take=torch.isin(yy,tensor(r['missing'],torch.long))
                        if scope=='C':take=~take
                        if bool(take.any()):risks.append(dict(role_id=r['id'],target=r['target'],policy_id=e['policy_id'],view=nm,scope=scope,
                            conditional_CE=float((ce[take]*mm[take]).sum()/mm[take].sum())))
        require(len(list((OUT/'models').rglob('*.pt')))==120 and len(list((OUT/'fit-logs').rglob('*.json')))==120,'Physical fit/model count')
        save(pd.DataFrame(audits),OUT/'audits/all-endpoint-original-coordinate.parquet')
        save(pd.DataFrame(risks),OUT/'audits/training-view-risks.parquet')
        save(ends,OUT/'manifests/endpoints.parquet')
        write(OUT/'manifests/endpoint-seal.json',dict(sha256=sha(OUT/'manifests/endpoints.parquet'),logical=300,new=120,reused=180,H_reads=0))
        progress('AD1_all_models_sealed',new=120,reused=180)

def predict():
    with stage('P5'):
        ends=pd.read_parquet(OUT/'manifests/endpoints.parquet');rows=[]
        for r in contract()['roles']:
            q=package(rolepath(r)/'query.parquet','query');raw=tensor(q[HIST]);ee=ends[ends.role_id.eq(r['id'])].set_index('policy_id')
            for p in registry():
                er=ee.loc[p['id']];m=artifact(ROOT/er.path,'inference-model')
                with torch.no_grad():
                    z=((raw-m['mu'])/m['scale'])@m['weight'].T+m['bias'];lp=z.log_softmax(1);pp=z.softmax(1)
                require(z.is_cuda and z.dtype==torch.float64 and torch.isfinite(lp).all(),'CUDA frozen prediction')
                d=pd.DataFrame(pp.cpu().numpy(),columns=[f'p{i}' for i in range(6)])
                for j in range(6):d[f'logp{j}']=lp[:,j].cpu().numpy();d[f'logit{j}']=z[:,j].cpu().numpy()
                d['visit_id']=q.visit_id.to_numpy();d['prediction']=pp.argmax(1).cpu().numpy()
                for k in ['target','group','outer']:d[k]=r[k]
                d['role_id']=r['id'];d['policy_id']=p['id'];rows.append(d)
        d=pd.concat(rows,ignore_index=True)
        require(len(d)==7200 and d.visit_id.nunique()==480 and not d.duplicated(['role_id','policy_id','visit_id']).any(),'Prediction coverage')
        save(d,OUT/'predictions/visits.parquet')
        write(OUT/'predictions/complete.json',dict(sha256=sha(OUT/'predictions/visits.parquet'),rows=7200,
            new_policy_rows=2880,unique_visits=480,roles=60,policies=5,H_labels_read=False,H_pre_reads=0))
        pp=PARENT/'predictions/visits.parquet';checked(pp,read(PARENT/'predictions/complete.json')['sha256'],'old-prediction-replay-after-seal')
        old=pd.read_parquet(pp);cols=[f'p{j}' for j in range(6)]+[f'logp{j}' for j in range(6)]
        maximum=0.
        for pid in [A,B,BASELINE]:
            aa=d[d.policy_id.eq(pid)].set_index(['role_id','visit_id']).sort_index()
            bb=old[old.policy_id.eq(pid)].set_index(['role_id','visit_id']).loc[aa.index]
            err=float(np.abs(aa[cols].to_numpy()-bb[cols].to_numpy()).max());require(err<1e-12,'Reused probabilities changed');maximum=max(maximum,err)
        write(OUT/'audits/reused-prediction-replay.json',dict(passed=True,max_error=maximum,policies=3,rows=4320))

def main():
    C.START=LOAD_START
    parentcost=read(PARENT/'cost-final.json')['cumulative_active_seconds']
    resultcost=read(PARENT/'result-analysis-20261018/analysis.json')['readonly_analysis_activity_seconds']
    latestdiag=read(PARENT/'allocation-diagnostic-20261018/summary.json')['active_seconds']
    components=dict(parent_full_cumulative_seconds=parentcost,recorded_result_analysis_seconds=resultcost,
        first_allocation_diagnostic_seconds=9.575209700036794,latest_allocation_diagnostic_seconds=latestdiag,
        conservative_unmetered_pre_AD1_charge_seconds=1800.,charge_not_a_measurement=True)
    C.PRIOR=parentcost+resultcost+9.575209700036794+latestdiag+1800.
    components['prior_charged_seconds']=C.PRIOR
    lock=writable(OUT/'run.lock');fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY);os.write(fd,str(os.getpid()).encode());os.close(fd)
    try:
        require(not (OUT/'failure.json').exists() and not (OUT/'completion.json').exists(),'Terminal AD1 run; no automatic restart')
        configure();write(OUT/'manifests/prior-activity.json',components)
        register();engineering_and_adopt();pilot();fit_rest();seal();predict()
        import score,report,verify
        score.run();report.run();verify.run()
        write(OUT/'completion.json',dict(program_complete=True,numeric_pass=True,all_60_roles_complete=True,
            new_fits=120,reused_endpoints=180,logical_endpoints=300,H_predictions_sealed=True,H_scored=True,
            new_mapping_fits=0,new_method_selected_after_H=False,retrospective_internal_evaluation=True,
            cumulative_active_seconds=spent(),verification_sha256=sha(OUT/'verification.json'),old_stops_preserved=True))
        progress('AD1_complete',new=120,reused=180)
    except BaseException as exc:
        write(OUT/'failure.json',dict(type=type(exc).__name__,exception=str(exc),traceback=traceback.format_exc(),
            time_unix=time.time(),cumulative_active_seconds=spent(),automatic_retry=False))
        textfile(DOC/'stop-report.md','# AD1停止记录\n\n没有自动修改设置或重启。\n\n```text\n'+traceback.format_exc()+'\n```\n')
        print(traceback.format_exc(),flush=True)
    finally:
        write(OUT/'cost-final.json',dict(prior_components=components,new_active_seconds=time.perf_counter()-C.START,
            cumulative_active_seconds=spent(),cap_seconds=28800,program_complete=(OUT/'completion.json').exists()))
        if lock.exists() and lock.read_text()==str(os.getpid()):lock.unlink()
    return 0 if (OUT/'completion.json').exists() else 1

if __name__=='__main__':raise SystemExit(main())
