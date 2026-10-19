"""1044 independent adoptions, 1296 zero-start NR2 fits, then full seal."""
from common import *
from weight_schedule import registry,slot
from backend import audit,source_log,fit as numeric_fit

def adopt():
    with stage('R1'):
        c=contract();pol={p['id']:p for p in registry()};rows=[]
        for r in c['roles']:
            budget_check();v=artifact(trainpath(r));gold=artifact(TI/'slots'/r['id']/'views.pt')
            require(all(torch.equal(v[k],gold[k]) for k in gold),'Frozen parent views differ')
            pre=package(rolepath(r)/'source-pre.parquet','train')
            require(torch.equal(v['rawpre_x'],(tensor(pre[HIST])-v['mu'])/v['scale']) and torch.equal(v['P_y'],tensor(truths(pre),torch.long)),'Anonymous pre coordinates/order')
            for e in [x for x in c['adopted'] if x['role_id']==r['id']]:
                budget_check();s=slot(v,pol[e['policy_id']],r['missing']);m=artifact(ROOT/e['path'])
                if e['slot_path']:
                    ss=artifact(ROOT/e['slot_path']);require(all(torch.equal(s[k],ss[k]) for k in s),'Adopted slot tensor mismatch')
                checked(ROOT/e['source_policy_path'],e['source_policy_sha256'],'source-numeric-policy')
                log=source_log(e);a=audit(m,s,r['t'],log,(e['source_max_iter'],e['source_max_eval']),e['source_kind'])
                row=dict(**e,**a,t=r['t'],eta=r['eta'],reused=True,adopted_before_H=True);rows.append(row)
                write(OUT/'adoptions'/r['id']/(e['policy_id']+'.json'),row)
        require(len(rows)==1044,'Adoption count');save(pd.DataFrame(rows),OUT/'manifests/adopted-endpoints.parquet')
        write(OUT/'audits/adoption-complete.json',dict(passed=True,total=1044,scientific=624,historical=420,H_reads=0,source_policy_preserved=True))
        progress('NR2_adoption_passed',logical=1044,scientific=624,historical=420)

def fit():
    with stage('P3'):
        c=contract();require(read(OUT/'audits/adoption-complete.json')['passed'],'Adoption incomplete')
        pol={p['id']:p for p in registry()};byrole={};rows=[]
        for e in c['pending']:byrole.setdefault(e['role_id'],[]).append(e['policy_id'])
        for r in c['roles']:
            if r['id'] not in byrole:continue
            v=artifact(trainpath(r))
            for pid in sorted(byrole[r['id']]):
                budget_check();p=pol[pid];s=slot(v,p,r['missing']);sp=OUT/'numeric-slots'/r['id']/(pid+'.pt');mp=modelpath(r,p)
                require(not mp.exists(),'Do not append to existing attempt')
                put(sp,s,role_id=r['id'],policy_id=pid,capability='train-only')
                write(OUT/'attempts'/r['id']/(pid+'.json'),dict(started_unix=time.time(),role_id=r['id'],policy_id=pid,slot_sha256=sha(sp)))
                require(697+len(list((OUT/'attempts').rglob('*.json')))<=2348,'Lineage optimization cap')
                model,log=numeric_fit(s,r['t'],dict(role_id=r['id'],arm=pid,t=r['t'],eta=r['eta'],execution_policy='RA1-NR2-full',
                    input_sha256=sha(sp),rho_C=p['rho_C'],rho_U=p['rho_U']))
                a=audit(model,s,r['t'],log,(4000,20000),'NR2')
                put(mp,model,role_id=r['id'],policy_id=pid,optimizer=log,slot_sha256=sha(sp))
                lp=OUT/'fit-logs'/r['id']/f'{pid}-t{r["t"]:g}.json'
                row=dict(role_id=r['id'],policy_id=pid,path=rel(mp),sha256=sha(mp),slot_path=rel(sp),source='NR2-full-new',source_kind='NR2',
                    result_path=rel(lp),result_sha256=sha(lp),source_policy_path=rel(OUT/'manifests/numeric-policy.json'),
                    source_policy_sha256=log['numeric_policy_sha256'],source_max_iter=4000,source_max_eval=20000,
                    target=r['target'],group=r['group'],outer=r['outer'],reused=False,t=r['t'],eta=r['eta'],seconds=log['seconds'],
                    iterations=log['total_updates'],lbfgs_updates=log['lbfgs_updates'],newton_updates=log['newton_updates'],evaluations=log['function_evaluations'],**a)
                write(OUT/'new-endpoints'/r['id']/(pid+'.json'),row);rows.append(row)
                if len(rows)%12==0:progress('NR2_full_fitting',completed=len(rows),total=1296,adopted=1044)
        require(len(rows)==1296,'Full new fit count');save(pd.DataFrame(rows),OUT/'manifests/new-endpoints.parquet')

def seal():
    with stage('P4'):
        require(read(OUT/'stages/P3.json')['passed'],'New fitting incomplete')
        old=pd.read_parquet(OUT/'manifests/adopted-endpoints.parquet');new=pd.read_parquet(OUT/'manifests/new-endpoints.parquet')
        all_=pd.concat([old,new],ignore_index=True).replace({np.nan:None})
        require(len(all_)==2340 and not all_.duplicated(['role_id','policy_id']).any(),'Endpoint coverage')
        pol={p['id']:p for p in registry()};audits=[]
        for r in contract()['roles']:
            v=artifact(trainpath(r))
            for e in all_[all_.role_id.eq(r['id'])].to_dict('records'):
                budget_check();m=artifact(ROOT/e['path']);log=source_log(e)
                a=audit(m,slot(v,pol[e['policy_id']],r['missing']),r['t'],log,(int(e['source_max_iter']),int(e['source_max_eval'])),e['source_kind'])
                audits.append(dict(role_id=r['id'],policy_id=e['policy_id'],**a))
        require(len(list((OUT/'models').rglob('*.pt')))==len(list((OUT/'fit-logs').rglob('*.json')))==1296,'Physical resumed coverage')
        save(pd.DataFrame(audits),OUT/'audits/all-endpoint-original-coordinate.parquet');save(all_,OUT/'manifests/endpoints.parquet')
        write(OUT/'manifests/endpoint-seal.json',dict(sha256=sha(OUT/'manifests/endpoints.parquet'),logical=2340,new=1296,adopted=1044,
            scientific=1920,historical=420,H_reads=0,cumulative_active_seconds=spent()))
        progress('all_NR2_models_sealed',logical=2340,H_reads=0)
