"""Finite controlled fits and frozen post-only CUDA prediction."""
from common import *
import objectives as O

def fit_roles(pilot):
    name='fit_pilot' if pilot else 'fit_remaining'
    with stage(name):
        c=contract();require(read(OUT/'manifests/tests.json')['passed'],'Tests not passed')
        if not pilot:require(read(OUT/'pilot/promotion.json')['passed'],'Pilot not passed')
        rs=[r for r in c['roles'] if (r['id'] in c['pilot_roles'])==pilot];sol=solver();rows=[]
        for i,r in enumerate(rs):
            for a in NEW_ARMS:
                s=artifact(newslot(r,a));p=newmodel(r,a)
                require(not p.exists(),'Do not resume failed fit terminal')
                model,log=sol.fit_preconditioned(s['x'],s['y'],s['mass'],r['t'],
                      {'role_id':r['id'],'arm':a,'t':r['t'],'beta':.1,'input_sha256':sha(newslot(r,a))})
                model.update(mu=s['mu'],scale=s['scale']);audit=O.audit(model,s,r['t'],log)
                put(model,p,role_id=r['id'],arm=a,beta=.1,t=r['t'],optimizer=log)
                rows.append({'role_id':r['id'],'target':r['target'],'group':r['group'],'outer':r['outer'],
                    'arm':a,'model_path':rel(p),'model_sha256':sha(p),'seconds':log['seconds'],**audit})
            if (i+1)%4==0:progress(name,roles=i+1,total=len(rs),models=3*(i+1))
        require(len(rows)==(36 if pilot else 144),'Fit count')
        save(pd.DataFrame(rows),OUT/'manifests'/('pilot-endpoints.parquet' if pilot else 'remaining-endpoints.parquet'))

def pilot_gate():
    with stage('pilot_gate'):
        c=contract();rows=[];timings=pd.read_parquet(OUT/'manifests/pilot-endpoints.parquet').seconds
        for r in c['roles']:
            if r['id'] not in c['pilot_roles']:continue
            for a in NEW_ARMS:
                p=newmodel(r,a);m=artifact(p);s=artifact(newslot(r,a));log=read(p.with_suffix('.json'))['optimizer']
                audit=O.audit(m,s,r['t'],log)
                with torch.no_grad():
                    pp=torch.softmax(s['x']@m['weight'].T+m['bias'],1)
                require(pp.is_cuda and torch.isfinite(pp).all(),'CUDA finite engineering inference')
                rows.append({'role_id':r['id'],'arm':a,**audit})
        save(pd.DataFrame(rows),OUT/'pilot/independent-audit.parquet')
        write(OUT/'pilot/promotion.json',{'passed':True,'fits':36,'counted_within_180':True,
              'target_labels_read':False,'target_queries_read':False,'median_fit_seconds':float(timings.median()),
              'estimated_remaining_fit_seconds':float(timings.mean()*144),'estimate_not_promise':True})

def seal_models():
    with stage('seal_models'):
        require(read(OUT/'stages/fit_remaining.json')['passed'],'Incomplete fits')
        ends=pd.concat([pd.read_parquet(OUT/'manifests'/name) for name in ['pilot-endpoints.parquet','remaining-endpoints.parquet']],ignore_index=True)
        require(len(ends)==180 and not ends.duplicated(['role_id','arm']).any(),'Endpoint coverage')
        require(len(list((OUT/'fit-logs').rglob('*.json')))==180,'Fit budget ledger')
        save(ends,OUT/'manifests/new-endpoints.parquet')
        write(OUT/'manifests/models-complete.json',{'passed':True,'new_classifiers':180,'reused_classifiers':180,
             'new_marginal_transforms':len(list((OUT/'transforms').rglob('*.pt'))),
             'endpoints_sha256':sha(OUT/'manifests/new-endpoints.parquet')})

def predict_all():
    with stage('predict'):
        c=contract();require(read(OUT/'manifests/models-complete.json')['passed'],'Seal all models first')
        checked(PARENT/'predictions/visits.parquet',c['fixed_files'][rel(PARENT/'predictions/visits.parquet')],'frozen-reference-predictions')
        old=pd.read_parquet(PARENT/'predictions/visits.parquet');pc=[f'p{i}' for i in range(6)]
        refs={(v['role_id'],v['arm']):v for v in c['references']};rows=[];maxerr=0.
        for i,r in enumerate(c['roles']):
            q=package(rolepath(r)/'query.parquet','query')
            for a in ARMS:
                path=ROOT/refs[(r['id'],a)]['model_path'] if a in ARMS[:3] else newmodel(r,a)
                m=artifact(path);pred=predict(m,q)
                if a in ARMS[:3]:
                    expected=old[old.role_id.eq(r['id'])&old.arm.eq(a)].set_index('visit_id')
                    err=float(np.abs(pred.set_index('visit_id').loc[expected.index,pc].to_numpy()-expected[pc].to_numpy()).max())
                    require(err<1e-12,'Frozen prediction changed');maxerr=max(maxerr,err)
                for k in ['outer','target','group']:pred[k]=r[k]
                pred['role_id']=r['id'];pred['arm']=a;pred['eta']=r['eta'];pred['t']=r['t'];rows.append(pred)
            if (i+1)%12==0:progress('predict',roles=i+1,total=60)
        df=pd.concat(rows,ignore_index=True)
        require(len(df)==8640 and df.visit_id.nunique()==480 and not df.duplicated(['role_id','arm','visit_id']).any(),'Prediction coverage')
        save(df,OUT/'predictions/visits.parquet')
        write(OUT/'predictions/complete.json',{'sha256':sha(OUT/'predictions/visits.parquet'),'rows':8640,
              'unique_visits':480,'reference_probability_max_error':maxerr,'all_models_sealed':True,
              'target_H_labels_read':False,'test_pre_read':False,'prediction_device':'cuda:0','dtype':'float64'})

if __name__=='__main__':
    {'pilot':lambda:fit_roles(True),'remaining':lambda:fit_roles(False),'gate':pilot_gate,
     'seal':seal_models,'predict':predict_all}[sys.argv[1]]()
