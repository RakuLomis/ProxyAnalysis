"""Train-only adoption, zero-init completion, full endpoint seal."""
from common import *
from weight_schedule import registry,slot
from backend import audit,load

def adopt():
    with stage('R1'):
        c=contract();pols={p['id']:p for p in registry()};rows=[]
        for r in c['roles']:
            budget_check();v=artifact(trainpath(r));ends=[e for e in c['adopted'] if e['role_id']==r['id']]
            gold=artifact(TI/'slots'/r['id']/'views.pt')
            require(all(torch.equal(v[k],gold[k]) for k in gold),'Parent train views not replayed')
            pre=package(rolepath(r)/'source-pre.parquet','train')
            require(torch.equal(v['rawpre_x'],(tensor(pre[HIST])-v['mu'])/v['scale']) and torch.equal(v['P_y'],tensor(truths(pre),torch.long)),'Anonymous pre coordinates/order not replayed')
            for e in ends:
                p=pols[e['policy_id']];s=slot(v,p,r['missing']);m=artifact(ROOT/e['path']);meta=read((ROOT/e['path']).with_suffix('.json'))
                if e['slot_path']:
                    oldslot=artifact(ROOT/e['slot_path']);require(all(torch.equal(s[k],oldslot[k]) for k in s),'Adopted exact input differs')
                require(meta['optimizer']['numeric_policy_sha256']==e['source_policy_sha256'],'Source policy identity')
                aa=audit(m,s,r['t'],meta['optimizer'],(e['source_max_iter'],e['source_max_eval']),adopting=True)
                row=dict(**e,t=r['t'],eta=r['eta'],reused=True,adopted_before_H=True,**aa);rows.append(row)
                write(OUT/'adoptions'/r['id']/(p['id']+'.json'),row)
        require(len(rows)==586,'Adoption audit count');save(pd.DataFrame(rows),OUT/'manifests/adopted-endpoints.parquet')
        write(OUT/'audits/adoption-complete.json',dict(passed=True,total=586,scientific=166,historical=420,H_reads=0,source_policy_hash_preserved=True))

def fit():
    with stage('P3'):
        c=contract();require(read(OUT/'audits/adoption-complete.json')['passed'],'Adoption incomplete');b=load();rows=[];byrole={}
        for case in c['pending']:byrole.setdefault(case['role_id'],[]).append(case['policy_id'])
        policies={p['id']:p for p in registry()}
        for r in c['roles']:
            if r['id'] not in byrole:continue
            v=artifact(trainpath(r))
            for pid in sorted(byrole[r['id']]):
                budget_check();p=policies[pid];s=slot(v,p,r['missing']);sp=OUT/'numeric-slots'/r['id']/(pid+'.pt');mp=modelpath(r,p)
                require(not mp.exists(),'Do not append to existing attempt')
                put(sp,s,role_id=r['id'],policy_id=pid,capability='train-only')
                write(OUT/'attempts'/r['id']/(pid+'.json'),dict(started_unix=time.time(),role_id=r['id'],policy_id=pid,slot_sha256=sha(sp)))
                require(200+len(list((OUT/'attempts').rglob('*.json')))<=2348,'Whole lineage physical fit protection')
                model,log=b.fit_preconditioned(s['x'],s['y'],s['mass'],r['t'],dict(role_id=r['id'],arm=pid,t=r['t'],eta=r['eta'],
                    execution_policy='RA1-NR1-full',input_sha256=sha(sp),rho_C=p['rho_C'],rho_U=p['rho_U']))
                model.update(mu=s['mu'],scale=s['scale']);aa=audit(model,s,r['t'],log,(4000,20000))
                put(mp,model,role_id=r['id'],policy_id=pid,optimizer=log,slot_sha256=sha(sp))
                row=dict(role_id=r['id'],policy_id=pid,path=rel(mp),sha256=sha(mp),slot_path=rel(sp),source='NR1-full-new',reused=False,
                    source_max_iter=4000,source_max_eval=20000,source_policy_sha256=log['numeric_policy_sha256'],target=r['target'],group=r['group'],outer=r['outer'],
                    t=r['t'],eta=r['eta'],seconds=log['seconds'],iterations=log['iterations'],evaluations=log['function_evaluations'],**aa)
                write(OUT/'new-endpoints'/r['id']/(pid+'.json'),row);rows.append(row)
                if len(rows)%12==0:progress('full_nr1_fitting',completed=len(rows),total=1754,adopted=586)
        require(len(rows)==1754,'New model coverage');save(pd.DataFrame(rows),OUT/'manifests/new-endpoints.parquet')

def seal():
    with stage('P4'):
        c=contract();require(read(OUT/'stages/P3.json')['passed'],'Fitting incomplete')
        old=pd.read_parquet(OUT/'manifests/adopted-endpoints.parquet');new=pd.read_parquet(OUT/'manifests/new-endpoints.parquet');all_=pd.concat([old,new],ignore_index=True)
        require(len(all_)==2340 and not all_.duplicated(['role_id','policy_id']).any(),'Complete logical endpoints')
        audits=[]
        for r in c['roles']:
            v=artifact(trainpath(r));e=all_[all_.role_id.eq(r['id'])].set_index('policy_id')
            for p in registry():
                budget_check();ee=e.loc[p['id']];m=artifact(ROOT/ee.path);log=read((ROOT/ee.path).with_suffix('.json'))['optimizer']
                aa=audit(m,slot(v,p,r['missing']),r['t'],log,(int(ee.source_max_iter),int(ee.source_max_eval)))
                audits.append(dict(role_id=r['id'],policy_id=p['id'],**aa))
        require(len(list((OUT/'models').rglob('*.pt')))==1754 and len(list((OUT/'fit-logs').rglob('*.json')))==1754,'Physical resumed fit count')
        save(pd.DataFrame(audits),OUT/'audits/all-endpoint-original-coordinate.parquet');save(all_,OUT/'manifests/endpoints.parquet')
        write(OUT/'manifests/endpoint-seal.json',dict(sha256=sha(OUT/'manifests/endpoints.parquet'),logical=2340,new=1754,adopted=586,old_scientific=124,NR1_pilot=42,historical=420,H_reads=0,cumulative_active_seconds=spent()))
