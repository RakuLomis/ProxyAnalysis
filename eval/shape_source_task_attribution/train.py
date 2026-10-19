"""192 fresh original-v4 fits; engineering pilot is part of the same matrix."""
from common import *
from prepare import loss_audit

def train():
    with stage('P2'):
        verify_seal(OUT/'slots-complete.json')
        solver=solver_module();roles=contract()['roles']
        pilot=[r for r in roles if r['inner']==1 and r['group']=='G0']
        remaining=[r for r in roles if r not in pilot]
        endpoints=[];attempts=0;times=[]
        for r in pilot+remaining:
            for arm in ARMS:
                attempts+=1;require(attempts<=192,'Physical fit budget')
                write(OUT/'fit-attempts.json',dict(attempts=attempts,limit=192,current_role=r['id'],current_arm=arm))
                src=OUT/'slots'/r['id']/(arm+'.pt');s=own(src)
                with compute('fit-'+r['id']+'/'+arm):
                    m,log=solver.fit_preconditioned(s['x'],s['y'],s['mass'],r['t'],dict(role_id=r['id'],arm=arm,t=r['t'],eta=r['eta'],input_sha256=sha(src)))
                    independent=loss_audit(m,s,r['t'])
                    require(abs(independent['objective']-log['objective'])<1e-10,'Independent training objective')
                    require(abs(independent['gradient']-log['max_gradient'])<1e-10 and independent['gradient']<=1e-5,'Independent training gradient')
                path=OUT/'models'/r['id']/(arm+'.pt')
                put(path,dict(**m,mu=s['mu'],scale=s['scale']),role_id=r['id'],arm=arm,input_sha256=sha(src),t=r['t'],eta=r['eta'],fresh_fit=True)
                times.append(log['seconds'])
                endpoints.append(dict(role_id=r['id'],role_target=r['target'],query_deployment=r['calibration'],group=r['group'],inner=r['inner'],arm=arm,
                    model_path=rel(path),model_sha256=sha(path),t=r['t'],eta=r['eta'],objective=log['objective'],max_gradient=log['max_gradient'],
                    iterations=log['iterations'],evaluations=log['function_evaluations'],fit_seconds=log['seconds'],accepted=True,reused=False))
                save(pd.DataFrame(endpoints),'model-endpoints')
                progress('P2_fitting',fits=attempts,total=192,last_role=r['id'],arm=arm,fit_seconds=log['seconds'])
                if attempts==16:
                    write(OUT/'pilot-complete.json',dict(fits=16,accepted=16,query_reads=0,seconds=sum(times),
                          remaining_fits=176,rough_remaining_fit_seconds=176*np.mean(times),range_seconds=[min(times),max(times)],
                          estimate_not_completion_promise=True))
                    progress('P2_pilot_complete',fits=16,remaining_estimate_seconds=176*np.mean(times))
        require(attempts==192 and len(endpoints)==192,'Incomplete model matrix')
        files=list((OUT/'models').rglob('*.pt'))+list((OUT/'models').rglob('*.json'))+list((OUT/'fit-logs').rglob('*.json'))+[OUT/'model-endpoints.parquet']
        seal(OUT/'models-complete.json',files,logical_endpoints=192,physical_fits=192,new_maps=0,query_reads=0,label_reads=0)
