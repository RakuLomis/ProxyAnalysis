"""TI12--TI17: finish the fixed 60-fit pilot before inspecting any signs."""
from common import *
import objectives as O
import influence as I

def path(r,arm):return OUT/'pilot/models'/r['id']/(arm+'.pt')

def fit_one(r,v,arm,beta,sol):
    tag='S' if beta==0 else f'{arm}-eps{beta:g}'
    p=path(r,tag)
    if p.exists():return artifact(p)
    s=O.slot(v,arm,beta);sp=OUT/'pilot/slots'/r['id']/(tag+'.pt')
    put(s,sp,role_id=r['id'],arm=tag,beta=beta,diagnostic=True)
    context={'role_id':r['id'],'arm':'pilot-'+tag,'t':r['t'],'eta':r['eta'],'beta':beta,'input_sha256':sha(sp)}
    model,log=sol.fit_preconditioned(s['x'],s['y'],s['mass'],r['t'],context,diagnostic=True)
    model.update(mu=v['mu'],scale=v['scale'])
    put(model,p,role_id=r['id'],arm=tag,beta=beta,eta=r['eta'],t=r['t'],optimizer=log,diagnostic=True)
    return model

def fit():
    with stage('pilot_fit'):
        c=contract();require(read(OUT/'manifests/tests.json')['passed'],'Tests required')
        require((OUT/'stages/prepare.json').exists(),'Prepared views required')
        sol=solver();logs=[];preds=[];count=0
        for r in c['pilot_roles']:
            v=artifact(viewpath(r));ref=artifact(basemodel(r))
            require(torch.equal(ref['mu'],v['mu']) and torch.equal(ref['scale'],v['scale']),'Base coordinate')
            slot=O.slot(v,'P',0.);old=read(basemodel(r).with_suffix('.json'))['optimizer']
            g=O.gradient(ref,slot,r['t']);gmax=max(float(g[0].abs().max()),float(g[1].abs().max()))
            require(abs(float(O.loss(ref,slot,r['t']))-old['objective'])<1e-10,'Base objective replay')
            require(abs(gmax-old['max_gradient'])<1e-10,'Base gradient replay')
            data,log=I.directions(r,v,ref,check_autograd=True)
            put(data,OUT/'pilot/directions'/r['id']/'direction.pt',**log);logs.append(log)
            q=package(rolepath(r)/'query.parquet','pilot-query')
            models=[('S',fit_one(r,v,'P',0.,sol))]
            replay=max(float((models[0][1][k]-ref[k]).abs().max()) for k in ['weight','bias'])
            require(replay<=1e-10,'Zero-beta baseline reproduction differs')
            for arm in ['P','G']:
                for eps in c['epsilons']:models.append((f'{arm}-eps{eps:g}',fit_one(r,v,arm,eps,sol)))
            for tag,model in models:
                pp=predict(model,q);pp['role_id']=r['id'];pp['arm']=tag;preds.append(pp)
                count+=1
            progress('numeric_pilot_fits',fits=count,total=60,role=r['id'],baseline_parameter_replay_error=replay)
        save(pd.concat(preds,ignore_index=True),OUT/'pilot/predictions.parquet')
        require(count==60,'Pilot fit cap/coverage')
        write(OUT/'pilot/predictions-complete.json',{'sha256':sha(OUT/'pilot/predictions.parquet'),
              'models':count,'rows':len(pd.concat(preds)),'actual_target_labels_read':False,'pseudo_labels_read':False})
        save(pd.DataFrame(logs),OUT/'pilot/hessian-checks.parquet')

def uniform_risk(model,x,y,q):
    s={'x':x,'y':y,'mass':torch.full((len(x),),1/len(x),device=device(),dtype=torch.float64)}
    return float(O.loss(model,s,0.,False)),I.pack_gradient(O.gradient(model,s,0.,False),q)

def evaluate():
    with stage('pilot_gate'):
        c=contract();require((OUT/'stages/pilot_fit.json').exists(),'ALL pilot fits first')
        pred=pd.read_parquet(OUT/'pilot/predictions.parquet');rows=[]
        for r in c['pilot_roles']:
            v=artifact(viewpath(r));ref=O.normalized_model(artifact(basemodel(r)))
            d=artifact(OUT/'pilot/directions'/r['id']/'direction.pt');q=d['q']
            query=package(rolepath(r)/'query.parquet','pilot-query')
            labels=package(rolepath(r)/'labels.parquet','pilot-labels')
            ll=labels.set_index('visit_id').loc[query.visit_id]
            xx=(tensor(query[HIST])-v['mu'])/v['scale'];yy=tensor(truths(ll),torch.long)
            baseCE,gr=uniform_risk(ref,xx,yy,q)
            trainCE,gt=uniform_risk(ref,v['main_x'],v['main_y'],q)
            for arm in ['P','G']:
                direction=d['d_'+arm];norm=float(direction.norm());near=norm<=1e-8
                directions=[];riskdiffs=[];traindiffs=[]
                for eps in c['epsilons']:
                    mod=artifact(path(r,f'{arm}-eps{eps:g}'));z=I.encode(O.normalized_model(mod),q)
                    directions.append((z-d['base'])/eps)
                    pp=pred[pred.role_id.eq(r['id'])&pred.arm.eq(f'{arm}-eps{eps:g}')].set_index('visit_id').loc[query.visit_id]
                    p=torch.as_tensor(pp[[f'p{i}' for i in range(6)]].to_numpy(),device=device(),dtype=torch.float64)
                    riskdiffs.append((float(-torch.log(p[torch.arange(len(yy),device=device()),yy]).mean())-baseCE)/eps)
                    risk,_=uniform_risk(mod,v['main_x'],v['main_y'],q);traindiffs.append((risk-trainCE)/eps)
                estimate=2*directions[0]-directions[1]
                absolute=float((estimate-direction).norm());error=absolute/max(1e-12,norm)
                ratio=float(d['e0'].norm())/max(1e-12,c['epsilons'][0]*norm)
                predicted=float(gr@direction);estimated=2*riskdiffs[0]-riskdiffs[1]
                pt=float(gt@direction);et=2*traindiffs[0]-traindiffs[1]
                gates={'stationarity':True if near else ratio<=.1,
                       'parameter_direction':absolute<=1e-6 if near else error<=.1,
                       'heldout_CE_derivative':abs(estimated-predicted)<=max(1e-4,.1*abs(predicted)),
                       'source_CE_derivative':abs(et-pt)<=max(1e-4,.1*abs(pt))}
                rows.append({'role_id':r['id'],'target':r['target'],'calibration':r['calibration'],'group':r['group'],
                             'arm':arm,'eta':r['eta'],'t':r['t'],'direction_norm':norm,'near_zero':near,
                             'stationarity_ratio':ratio,'parameter_absolute_error':absolute,'parameter_relative_error':error,
                             'CE_derivative_predicted':predicted,'CE_derivative_finite':estimated,
                             'CE_derivative_error':abs(estimated-predicted),'source_CE_predicted':pt,
                             'source_CE_finite':et,'source_CE_error':abs(et-pt),
                             **{'gate_'+k:v for k,v in gates.items()},'passed':all(gates.values())})
        table=pd.DataFrame(rows);save(table,OUT/'pilot/finite-difference-checks.parquet')
        logpaths=list((OUT/'diagnostic-fit-logs').rglob('*.json'))
        times=[read(p)['seconds'] for p in logpaths];require(len(logpaths)==60,'Diagnostic fit accounting')
        result={'passed':bool(table.passed.all()),'rows':len(table),'passed_rows':int(table.passed.sum()),
                'failed_rows':int((~table.passed).sum()),'diagnostic_fits':60,'new_mapping_fits':11,
                'formal_fits':0,'target_H_labels_read':False,'target_U_reads':0,'test_pre_reads':0,
                'gate_failures':{k:int((~table[k]).sum()) for k in table if k.startswith('gate_')},
                'fit_seconds':{'mean':float(np.mean(times)),'median':float(np.median(times)),
                               'p90':float(np.quantile(times,.9)),'max':float(max(times))},
                'next_action':'formal_matrix' if table.passed.all() else 'await_user_decision_no_automatic_repair',
                'stationarity_ratio_max':float(table.stationarity_ratio.max()),
                'parameter_relative_error_max':float(table.parameter_relative_error.max())}
        write(OUT/'pilot/promotion.json',result)
        if not result['passed']:
            write(OUT/'awaiting-decision.json',{'reason':'registered numeric pilot gates failed',
                 'promotion_sha256':sha(OUT/'pilot/promotion.json'),'formal_started':False,
                 'automatic_budget_or_precision_change':False,'time_unix':time.time()})
        progress('numeric_pilot_gate',**result)

if __name__=='__main__':{'fit':fit,'gate':evaluate}[sys.argv[1]]()
