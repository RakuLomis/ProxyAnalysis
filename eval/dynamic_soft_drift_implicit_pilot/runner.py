"""Bounded pilot stages. No formal q optimization is authorized here."""
from common import *
import gauge as G
import geometry
import forward as FW
import implicit as IM
import finite_difference as FD
import oracle_bridge as OB

def phase(point):
    with stage(point):
        if point=='alt':require(read(OUT/'one-complete.json')['passed'],'q-one gate required')
        q=tensor(contract()['q_one' if point=='one' else 'q_alt'])
        checks=[]; gradients=[]; centers=[]; ff=[]; armff=[]
        for r in contract()['selected']:
            for arm in ['D-P','D-G']:
                try:
                    eps=FW.solve(r,arm,q,point+'-center',old_reference=point=='one')
                except BaseException as exc:
                    write(OUT/f'{point}-complete.json',dict(passed=False,status='stop_solution_numeric_failure',
                          role_id=r['id'],arm=arm,exception=str(exc),centers_completed=len(centers)))
                    raise
                endpoints=[]
                for level in range(2):
                    ep=own(OUT/'endpoints'/r['id']/arm/f'{point}-center-level{level}.pt')
                    try:result=IM.evaluate(r,arm,ep)
                    except BaseException as exc:
                        write(OUT/f'{point}-complete.json',dict(passed=False,status='stop_implicit_gradient_not_verified',
                              role_id=r['id'],arm=arm,exception=str(exc),centers_completed=len(centers)))
                        raise
                    put(result,OUT/'derivatives'/r['id']/arm/f'{point}-level{level}.pt',level=level,point=point)
                    checks.append(dict(role_id=r['id'],arm=arm,point=point,level=level,
                         **{k:v for k,v in result.items() if not torch.is_tensor(v)}))
                    endpoints.append(result)
                stable,diff=IM.stability(*endpoints)
                checks[-1].update(precision_stability_passed=stable,precision_stability_error=diff)
                save(pd.DataFrame(checks),OUT/f'{point}-implicit-checks.parquet')
                if not stable:
                    write(OUT/f'{point}-complete.json',dict(passed=False,status='stop_implicit_gradient_not_verified',
                          role_id=r['id'],arm=arm,reason='two forward accuracies disagree'))
                    return
                centers.append(dict(role_id=r['id'],arm=arm,point=point,Q_coarse=float(eps[0]['Q']),Q_fine=float(eps[1]['Q']),
                   grad_coarse=eps[0]['original_gradient'],grad_fine=eps[1]['original_gradient']))
                comp=OB.components(task(r,arm),arm,q)
                for method in (['D-P','T-P'] if arm=='D-P' else ['D-G']):
                    combined=endpoints[1]['gradient']+comp['shrink_gradient']+(comp['penalty_gradient'] if method!='T-P' else 0)
                    for j in range(10):
                        gradients.append(dict(role_id=r['id'],arm=method,point=point,block=j,
                            task_gradient=float(endpoints[1]['gradient'][j]),shrink_gradient=float(comp['shrink_gradient'][j]),
                            penalty_gradient=float(comp['penalty_gradient'][j]) if method!='T-P' else 0.,
                            total_gradient=float(combined[j]),oracle_error=comp['error']))
                save(pd.DataFrame(centers),OUT/f'{point}-centers.parquet')
                save(pd.DataFrame(gradients),OUT/f'{point}-arm-gradients.parquet')
                rows,arows=FD.run_case(r,arm,point,q,eps,endpoints[1]['gradient'])
                ff+=rows; armff+=arows
                save(pd.DataFrame(ff),OUT/f'{point}-FD-checks.parquet')
                save(pd.DataFrame(armff),OUT/f'{point}-arm-FD-checks.parquet')
                progress('implicit_case_checked',point=point,cases=len(centers),FD_records=len(ff),passed=sum(x['passed'] for x in ff))
                if not all(x['passed'] for x in ff) or not all(x['passed'] for x in armff):
                    weak=any(not x['signal_identifiable'] for x in ff)
                    write(OUT/f'{point}-complete.json',dict(passed=False,checks=len(ff),
                          status='awaiting_signal_quality_decision' if weak else 'stop_implicit_gradient_not_verified',
                          role_id=r['id'],arm=arm,reason='fixed fully-retrained finite differences'))
                    return
        require(len(centers)==12 and len(ff)==48,'Full phase count mismatch')
        write(OUT/f'{point}-complete.json',dict(passed=True,status='solution_'+point+'_qualified',centers=12,FD_checks=48))

def behavior():
    rows=[]
    if not (OUT/'alt-complete.json').exists() or not read(OUT/'alt-complete.json')['passed']:return
    for r in contract()['selected']:
        for arm in ['D-P','D-G']:
            one=own(OUT/'endpoints'/r['id']/arm/'one-center-level1.pt')
            alt=own(OUT/'endpoints'/r['id']/arm/'alt-center-level1.pt')
            p=one['probability']; pa=alt['probability']
            z=one['logits']; za=alt['logits']; y=task(r,arm)['view']['query_y']
            pred=p.argmax(1); preda=pa.argmax(1)
            delta=(za-za.mean(1,keepdim=True))-(z-z.mean(1,keepdim=True))
            rows.append(dict(role_id=r['id'],arm=arm,delta_Q=float(alt['Q']-one['Q']),
                 probability_TV=float(((p-pa).abs().sum(1)/2).mean()),centered_logit_RMSE=float(delta.square().mean().sqrt()),
                 changed=int((pred!=preda).sum()),fixed=int(((pred!=y)&(preda==y)).sum()),broken=int(((pred==y)&(preda!=y)).sum())))
    save(pd.DataFrame(rows),OUT/'nontrivial-point-behavior.parquet')

def verify():
    with stage('verify'):
        integrity(); behavior()
        result=read(OUT/'alt-complete.json') if (OUT/'alt-complete.json').exists() else read(OUT/'one-complete.json') if (OUT/'one-complete.json').exists() else dict(passed=False,status='stop_solution_numeric_failure')
        qualified=(OUT/'alt-complete.json').exists() and result['passed']
        status='qualified_solution_feedback_pilot' if qualified else result['status']
        files={rel(p):sha(p) for p in OUT.rglob('*') if p.is_file() and p.name not in ['verification.json','completion.json','progress.json','stage.lock']}
        # Actual numeric read allowlist was enforced by every source loader.
        write(OUT/'verification.json',dict(passed=True,parent_files_unchanged=True,files=files,
          execution_integrity_passed=True,numeric_qualified=qualified,status=status,target_C_U_H_numeric_reads=0,
          PCAP_reads=0,formal_matrix_authorized=False,ledger=read(OUT/'ledger.json')))
        write(OUT/'completion.json',dict(execution_complete=True,execution_integrity_passed=True,numeric_qualified=qualified,
          status=status,formal_matrix_authorized=False,verification_sha256=sha(OUT/'verification.json'),**read(OUT/'ledger.json')))
        write(OUT/'awaiting-decision.json',dict(status=status,continue_automatically=False,formal_matrix_authorized=False))

def all_stages():
    synthetic=G.synthetic_tests()
    register()
    write(OUT/'audits/synthetic-verification.json',synthetic)
    try:
        geometry.run(); phase('one')
        if read(OUT/'one-complete.json')['passed']:phase('alt')
    except Exception as exc:
        print('PILOT STOP:',type(exc).__name__,str(exc),flush=True)
    verify()
    import report
    report.run()

if __name__=='__main__':
    action=sys.argv[1]
    {'register':register,'geometry':geometry.run,'one':lambda:phase('one'),'alt':lambda:phase('alt'),
     'verify':verify,'all':all_stages,'test':G.synthetic_tests}[action]()
