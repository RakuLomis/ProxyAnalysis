"""P2/P3 fixed matrix and P4 all-endpoint sealing; no business gate."""
from common import *
from weight_schedule import registry,slot,audit
import solver_v4 as solver

def fit(pilot):
    name='P2' if pilot else 'P3'
    with stage(name):
        c=contract();require(read(OUT/'audits/P1-complete.json')['passed'],'P1 not passed')
        if not pilot:require(read(OUT/'pilot/promotion.json')['passed'],'P2 not passed')
        done=[];timings=[];count=0
        policies=[p for p in registry() if p['alias'] is None]
        for r in c['roles']:
            v=None
            for p in policies:
                ispilot=r['outer']==0 and p['m']==.25 and p['allocation']=='UPR'
                if ispilot!=pilot:continue
                budget_check()
                if v is None:v=artifact(trainpath(r))
                s=slot(v,p,r['missing']);path=modelpath(r,p);sp=OUT/'numeric-slots'/r['id']/(p['id']+'.pt')
                require(not path.exists(),'Unexpected accepted model; resume by registered stage only')
                put(sp,s,role_id=r['id'],policy_id=p['id'],capability='train-only')
                context=dict(role_id=r['id'],arm=p['id'],t=r['t'],eta=r['eta'],rho_C=p['rho_C'],rho_U=p['rho_U'],input_sha256=sha(sp))
                model,log=solver.fit_preconditioned(s['x'],s['y'],s['mass'],r['t'],context)
                model.update(mu=s['mu'],scale=s['scale']);aa=audit(model,s,r['t'],log)
                put(path,model,role_id=r['id'],policy_id=p['id'],optimizer=log,slot_sha256=sha(sp))
                # Training-only export replay, not H evaluation.
                with torch.no_grad():
                    zz=s['x']@model['weight'].T+model['bias'];pp=zz.softmax(1)
                    require(zz.is_cuda and zz.dtype==torch.float64 and torch.isfinite(pp).all(),'CUDA output gate')
                done.append(dict(role_id=r['id'],policy_id=p['id'],path=rel(path),sha256=sha(path),target=r['target'],group=r['group'],outer=r['outer'],
                                 source=p['source'],seconds=log['seconds'],iterations=log['iterations'],evaluations=log['function_evaluations'],**aa))
                count+=1
                if count%12==0:
                    save(pd.DataFrame(done),OUT/'manifests'/(name+'-partial-endpoints.parquet'))
                    progress(name+'_fitting',completed=count,total=48 if pilot else 1872,active_seconds=spent())
        require(count==(48 if pilot else 1872),'New fit matrix coverage')
        frame=pd.DataFrame(done);save(frame,OUT/'manifests'/(name+'-endpoints.parquet'))
        if pilot:
            # Each deployment/source group has three predeclared masks.
            cells=frame.groupby(['target','source']).seconds.max()
            require(len(cells)==16,'All pilot cost strata')
            # 120 new fits in each deployment/source stratum, 3 completed in pilot.
            forecast=float(cells.sum()*117)+600.+spent()
            require(forecast<28800,'Conservative forecast exceeds activity budget; pause before P3')
            write(OUT/'pilot/promotion.json',dict(passed=True,numeric_pass=True,engineering_fits=48,counted_within_1920=True,
                forecast_total_active_seconds=forecast,explicit_nonfit_reserve_seconds=600,observed_active_seconds=spent(),H_reads=0,
                scientific_effect_screen=False,cell_max_seconds=cells.reset_index().to_dict('records')))

def seal():
    with stage('P4'):
        for k in ['P2','P3']:require(read(OUT/'stages'/(k+'.json'))['passed'],'Incomplete fits')
        c=contract();a=pd.read_parquet(OUT/'manifests/verified-aliases.parquet');new=pd.concat([pd.read_parquet(OUT/'manifests'/(k+'-endpoints.parquet')) for k in ['P2','P3']],ignore_index=True)
        require(len(new)==1920 and len(a)==420,'Endpoint counts')
        e=pd.concat([a.assign(reused=True),new.assign(reused=False)],ignore_index=True)
        require(len(e)==2340 and not e.duplicated(['role_id','policy_id']).any(),'Endpoint uniqueness')
        audits=[]
        for r in c['roles']:
            v=artifact(trainpath(r));ee=e[e.role_id.eq(r['id'])].set_index('policy_id')
            for p in registry():
                row=ee.loc[p['id']];model=artifact(ROOT/row.path);log=read((ROOT/row.path).with_suffix('.json'))['optimizer']
                aa=audit(model,slot(v,p,r['missing']),r['t'],log);audits.append(dict(role_id=r['id'],policy_id=p['id'],**aa))
        save(pd.DataFrame(audits),OUT/'audits/all-endpoint-original-coordinate.parquet')
        require(len(list((OUT/'models').rglob('*.pt')))==1920,'Physical model count')
        require(len(list((OUT/'fit-logs').rglob('*.json')))==1920,'Physical fit ledger count')
        require(len(list((OUT/'diagnostic-fit-logs').rglob('*.json')))==3,'Extra fit ledger count')
        save(e,OUT/'manifests/endpoints.parquet')
        write(OUT/'manifests/endpoint-seal.json',dict(sha256=sha(OUT/'manifests/endpoints.parquet'),logical_endpoints=2340,new_models=1920,reused=420,
              numeric_pass=True,H_reads=0,H_labels_read=False,selection_after_H=False,active_seconds=spent()))
