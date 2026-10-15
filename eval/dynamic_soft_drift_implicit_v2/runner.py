"""Sequential fixed-role pilot, all failures preserve previous results."""
from common import *
import forward as FW
import validation as V
G,IM,OB=math_modules()

def pair(r,arm,q,key):
    p=OUT/'points'/r['id']/arm/f'{key}-v.pt'
    if p.exists():
        log=read(p.parent/(key+'-validation.json'));V.evidence_gate(log)
        require(log['passed'],'Failed validation cannot be reused')
        f=own(p.parent/(key+'-f.pt'));v=own(p)
        require(torch.equal(f['q'],q),'Cached q mismatch')
        return f,v,log
    f=FW.fine(r,arm,q,key)
    return (f,*V.validate(r,arm,key,f))

def bootstrap():
    with stage('first_three'):
        r=contract()['selected'][0];q=tensor(contract()['q_one']);d=tensor(contract()['directions']['all']);h=contract()['h'][0]
        for key,qq in [('one-center',q),('one-all-h0-plus',q+h*d),('one-all-h0-minus',q-h*d)]:
            pair(r,'D-P',qq,key)
        # Numeric loader negatives execute before any forbidden input is loaded.
        for action in [lambda:asset(SOURCE/'pilot/tasks'/r['id']/'D-P.pt','D-G','negative'),
                       lambda:writable(PARENT/'forbidden.json'),lambda:asset(ROOT/'not-registered.pt','D-P','negative')]:
            try:action()
            except RuntimeError:pass
            else:raise RuntimeError('Forbidden operation accepted')
        write(OUT/'first-three-complete.json',dict(passed=True,reused_fine=3,new_LR_fits=0,validation_steps=3,permission_negatives=3))

def derivative(r,arm,point,f,v):
    results=[];rows=[]
    for label,ep in [('f',f),('v',v)]:
        ledger(implicit_evaluations=1)
        result=IM.evaluate(r,arm,ep);results.append(result)
        put(result,OUT/'derivatives'/r['id']/arm/f'{point}-{label}.pt',schema='implicit_derivative',role_id=r['id'],arm=arm,point=point,state=label)
        rows.append(dict(role_id=r['id'],arm=arm,point=point,state=label,**{k:x for k,x in result.items() if not torch.is_tensor(x)}))
    stable,error=IM.stability(*results);rows[-1].update(fv_stable=stable,fv_gradient_error=error)
    return results,rows,stable

def fd_case(r,arm,point,q,derivatives):
    rows=[];arows=[];data=task(r,arm)
    for direction,vec in contract()['directions'].items():
        d=tensor(vec);slopes_f=[];slopes_v=[]
        for hi,h in enumerate(contract()['h']):
            fp,vp,mp=pair(r,arm,q+h*d,f'{point}-{direction}-h{hi}-plus')
            fn,vn,mn=pair(r,arm,q-h*d,f'{point}-{direction}-h{hi}-minus')
            df=float((fp['Q']-fn['Q'])/(2*h));dv=float((vp['Q']-vn['Q'])/(2*h))
            ep=abs(float(fp['Q']-vp['Q']));en=abs(float(fn['Q']-vn['Q']))
            ufv=(ep+en)/(2*h);bound=(ep+en+2e-12)/(2*h)
            signal_floor=10*(ep+en+2e-12)
            signal_f=abs(float(fp['Q']-fn['Q']));signal_v=abs(float(vp['Q']-vn['Q']))
            identifiable=signal_f>=signal_floor and signal_v>=signal_floor
            gf=float(derivatives[0]['gradient']@d);gv=float(derivatives[1]['gradient']@d)
            tau=1e-5+1e-3*abs(df);tv=1e-5+1e-3*abs(dv)
            gates=dict(fine_validation_uncertainty=bound<=tau/10,validation_slope=abs(df-dv)<=tau,
                       implicit_f=abs(gf-df)<=tau,implicit_v=abs(gv-dv)<=tv)
            diag=None;cf_slope=None
            if fp['coarse_independently_observed'] and fn['coarse_independently_observed']:
                diag=(abs(float(fp['Q']-fp['coarse_Q']))+abs(float(fn['Q']-fn['coarse_Q']))+2e-12)/(2*h)
                cf_slope=float((fp['coarse_Q']-fn['coarse_Q'])/(2*h))
            row=dict(role_id=r['id'],arm=arm,point=point,direction=direction,h=h,D_f=df,D_v=dv,
                 implicit_f=gf,implicit_v=gv,implicit_f_error=abs(gf-df),implicit_v_error=abs(gv-dv),
                 U_fv=ufv,U_fv_with_floor=bound,U_limit=tau/10,derivative_limit=tau,validation_derivative_limit=tv,
                 signal_f=signal_f,signal_v=signal_v,signal_floor=signal_floor,signal_identifiable=identifiable,
                 weak_direction=abs(df)<=tau,old_CF_diagnostic=diag,old_coarse_slope_diagnostic=cf_slope,
                 old_U_gate_passed_diagnostic=None if diag is None else diag<=tau/10,
                 **{k+'_pass':val for k,val in gates.items()},numerical_passed=all(gates.values()),
                 passed=identifiable and all(gates.values()),failed_gates=[k for k,val in gates.items() if not val])
            rows.append(row);slopes_f.append(df);slopes_v.append(dv)
            for state,der,fd in [('f',derivatives[0],df),('v',derivatives[1],dv)]:
                for a in OB.direction(data,arm,q,d,h,der['gradient'],fd):
                    arows.append(dict(role_id=r['id'],point=point,direction=direction,h=h,state=state,**a))
            save(pd.DataFrame(rows),OUT/'FD-cases'/r['id']/f'{arm}-{point}.parquet')
            save(pd.DataFrame(arows),OUT/'arm-cases'/r['id']/f'{arm}-{point}.parquet')
            if r['id']==contract()['first_role'] and arm=='D-P' and point=='one' and direction=='all' and hi==0:
                write(OUT/'first-case-verdict.json',dict(passed=row['passed'] and all(a['passed'] for a in arows),
                      old_parent_verdict_changed=False,old_CF_diagnostic=diag,U_fv_with_floor=bound,U_limit=tau/10))
            progress('fixed_difference_checked',role=r['id'],arm=arm,point=point,direction=direction,h=h,
                     passed=row['passed'],U_fv=bound,U_limit=tau/10,failed_gates=row['failed_gates'])
            if not row['passed'] or not all(a['passed'] for a in arows):return rows,arows
        ferror=abs(slopes_f[0]-slopes_f[1]);verror=abs(slopes_v[0]-slopes_v[1])
        flimit=1e-5+1e-3*max(map(abs,slopes_f));vlimit=1e-5+1e-3*max(map(abs,slopes_v))
        ok=ferror<=flimit and verror<=vlimit
        for row in rows[-2:]:row.update(step_f_error=ferror,step_v_error=verror,step_f_limit=flimit,
                                      step_v_limit=vlimit,step_consistency_pass=ok,passed=row['passed'] and ok)
        save(pd.DataFrame(rows),OUT/'FD-cases'/r['id']/f'{arm}-{point}.parquet')
        if not ok:return rows,arows
    return rows,arows

def phase(point):
    with stage(point):
        if point=='alt':require(read(OUT/'one-complete.json')['passed'],'All q-one gates required')
        q=tensor(contract()['q_one' if point=='one' else 'q_alt'])
        imrows=[];rows=[];arows=[];gradients=[];centers=[]
        for r in contract()['selected']:
            for arm in ['D-P','D-G']:
                try:f,v,validation=pair(r,arm,q,point+'-center')
                except Exception as exc:
                    write(OUT/f'{point}-complete.json',dict(passed=False,status='stop_fine_validation_numeric_failure',role_id=r['id'],arm=arm,exception=str(exc)))
                    raise
                try:der,ir,stable=derivative(r,arm,point,f,v)
                except Exception as exc:
                    write(OUT/f'{point}-complete.json',dict(passed=False,status='stop_final_solution_feedback_not_verified',role_id=r['id'],arm=arm,exception=str(exc)))
                    raise
                imrows+=ir;save(pd.DataFrame(imrows),OUT/f'{point}-implicit-checks.parquet')
                if not stable:
                    write(OUT/f'{point}-complete.json',dict(passed=False,status='stop_final_solution_feedback_not_verified',reason='center fine-validation gradient'))
                    return
                centers.append(dict(role_id=r['id'],arm=arm,point=point,Q_f=float(f['Q']),Q_v=float(v['Q']),
                              gradient_f=validation['gradient_f'],gradient_v=validation['gradient_v']))
                comp=OB.components(task(r,arm),arm,q)
                for method in (['D-P','T-P'] if arm=='D-P' else ['D-G']):
                    for j in range(10):
                        pg=float(comp['penalty_gradient'][j]) if method!='T-P' else 0.
                        gradients.append(dict(role_id=r['id'],arm=method,point=point,block=j,task=float(der[0]['gradient'][j]),
                          shrink=float(comp['shrink_gradient'][j]),penalty=pg,total=float(der[0]['gradient'][j]+comp['shrink_gradient'][j])+pg))
                save(pd.DataFrame(centers),OUT/f'{point}-centers.parquet');save(pd.DataFrame(gradients),OUT/f'{point}-arm-gradients.parquet')
                try:fr,ar=fd_case(r,arm,point,q,der)
                except Exception as exc:
                    write(OUT/f'{point}-complete.json',dict(passed=False,status='stop_fine_validation_numeric_failure',role_id=r['id'],arm=arm,exception=str(exc)))
                    raise
                rows+=fr;arows+=ar;save(pd.DataFrame(rows),OUT/f'{point}-FD-checks.parquet');save(pd.DataFrame(arows),OUT/f'{point}-arm-FD-checks.parquet')
                if not all(x['passed'] for x in rows) or not all(x['passed'] for x in arows):
                    weak=any(not x['signal_identifiable'] for x in rows)
                    write(OUT/f'{point}-complete.json',dict(passed=False,status='awaiting_fine_validation_decision' if weak else 'stop_final_solution_feedback_not_verified',
                          role_id=r['id'],arm=arm,reason='fixed difference gates',checks=len(rows)))
                    return
                progress('source_case_complete',point=point,cases=len(centers),FD_checks=len(rows))
        require(len(rows)==48 and len(centers)==12,'Phase count mismatch')
        write(OUT/f'{point}-complete.json',dict(passed=True,status='solution_'+point+'_qualified_v2',checks=48,centers=12))

def verify():
    with stage('verify'):
        integrity()
        result=read(OUT/'alt-complete.json') if (OUT/'alt-complete.json').exists() else read(OUT/'one-complete.json') if (OUT/'one-complete.json').exists() else dict(passed=False,status='stop_fine_validation_numeric_failure')
        qualified=(OUT/'alt-complete.json').exists() and result['passed']
        status='qualified_solution_feedback_v2' if qualified else result['status']
        vals=[];solves=[]
        for p in (OUT/'points').rglob('*.json'):
            obj=read(p)
            if obj.get('schema')=='validation_log':vals.append(obj)
            if obj.get('schema')=='solve_log':solves.append({k:v for k,v in obj.items() if k not in ['trace','initial_solver']})
        if vals:save(pd.DataFrame(vals),OUT/'validation-checks.parquet')
        if solves:save(pd.DataFrame(solves),OUT/'forward-checks.parquet')
        files={rel(p):sha(p) for p in OUT.rglob('*') if p.is_file() and p.name not in ['verification.json','completion.json','progress.json','stage.lock']}
        verification=dict(execution_integrity_passed=True,numeric_qualified=qualified,status=status,parent_files_unchanged=True,
                          files=files,ledger=read(OUT/'ledger.json'),target_C_U_H_numeric_reads=0,PCAP_reads=0,formal_matrix_authorized=False)
        write(OUT/'verification.json',verification)
        write(OUT/'completion.json',dict(execution_complete=True,execution_integrity_passed=True,numeric_qualified=qualified,
              status=status,verification_sha256=sha(OUT/'verification.json'),formal_matrix_authorized=False,**read(OUT/'ledger.json')))
        write(OUT/'awaiting-decision.json',dict(status=status,automatic_continuation=False,formal_matrix_authorized=False))

def all_stages():
    tests=V.tests();register();write(OUT/'audits/tests.json',tests)
    try:
        bootstrap();phase('one')
        if read(OUT/'one-complete.json')['passed']:phase('alt')
    except Exception as exc:print('BOUNDED STOP:',type(exc).__name__,str(exc),flush=True)
    verify()
    import report
    report.run()

if __name__=='__main__':
    {'all':all_stages,'register':register,'test':V.tests,'first':bootstrap,'one':lambda:phase('one'),
     'alt':lambda:phase('alt'),'verify':verify}[sys.argv[1]]()
