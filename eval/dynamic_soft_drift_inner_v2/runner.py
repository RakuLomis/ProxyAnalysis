"""Frozen coordinates, finite K ladder and gated new-program diagnostics."""
from common import *
import inner as N

def prepared(r,arm):
    v=task(r,arm)['view'].copy();v['conditioning']=load_own(OUT/'coordinates'/r['id']/f'{arm}.pt');return v
def prepare():
    with stage('prepare'):
        A,R,U,O=production();rows=[]
        for r in contract()['roles']:
            for arm in ['D-P','D-G']:
                v=task(r,arm)['view'];train={k:v[k] for k in N.TRAIN_KEYS}
                cond,audit=N.initialize(train,r['t'],U)
                m=reference(r,arm);require(torch.equal(v['mu'],m['mu']) and torch.equal(v['scale'],m['scale']),'Reference coordinates')
                put(cond,OUT/'coordinates'/r['id']/f'{arm}.pt',role_id=r['id'],arm=arm,training_only=True)
                rows.append(dict(role_id=r['id'],arm=arm,old_step=float(v['conditioning']['step']),**audit))
                save(pd.DataFrame(rows),OUT/'audits/coordinates.parquet')
                progress('frozen_full_slot_coordinates',completed=len(rows),total=24,step=audit['step'])
        # Negative checks act before data are read or numerical models executed.
        for name,action in [('deny old write',lambda:writable(REF/'forbidden.json')),
                ('deny group P asset',lambda:asset(SOURCE/'pilot/tasks'/contract()['roles'][0]['id']/'D-P.pt','D-G','negative')),
                ('deny conditioning query',lambda:N.initialize(dict(train,query_x=v['query_x']),r['t'],U))]:
            try:action()
            except RuntimeError:pass
            else:raise RuntimeError('Negative accepted '+name)
        write(OUT/'audits/prepare-complete.json',dict(passed=True,coordinate_tasks=24,reference_refits=0,negative_checks=3))

def compare(v,theta,m,t,q,K,role,arm,U):
    s=U.pack(v,arm,q);ref=torch.cat([m['weight'],m['bias'][:,None]],1)
    J=float(U.original_objective(theta,s,t));Jref=float(U.original_objective(ref,s,t));J0=float(np.log(6))
    grad=float(U.original_gradient(theta,s,t).abs().max());den=J0-Jref;ratio=(J-Jref)/den if den>1e-6 else None
    require(J<=J0+1e-10 and np.isfinite(J) and np.isfinite(grad),'Fixed-step numerical failure or objective increase')
    l=v['query_x']@theta[:,:96].T+theta[:,96];lr=v['query_x']@m['weight'].T+m['bias']
    p=torch.softmax(l,1);pr=torch.softmax(lr,1);y=v['query_y']
    ce=torch.logsumexp(l,1)-l.gather(1,y[:,None]).squeeze(1);cer=torch.logsumexp(lr,1)-lr.gather(1,y[:,None]).squeeze(1)
    ce_abs=(ce-cer).abs();tv=(p-pr).abs().sum(1)/2
    rel=(l-l.mean(1,keepdim=True))-(lr-lr.mean(1,keepdim=True))
    pred=p.argmax(1);predr=pr.argmax(1);changed=pred!=predr
    top=torch.topk(pr,2,dim=1).values;margin=top[:,0]-top[:,1];high=margin>=.02
    metrics=dict(J_new=J,J_ref=Jref,J0=J0,remaining=ratio,gradient=grad,CE_new=float(ce.mean()),CE_ref=float(cer.mean()),
        CE_mean_abs=float(ce_abs.mean()),CE_row_max=float(ce_abs.max()),TV_mean=float(tv.mean()),TV_max=float(tv.max()),
        logit_RMSE=float(rel.square().mean().sqrt()),changed=int(changed.sum()),
        high_margin_changes=int((changed&high).sum()),weak_changes=int((changed&~high).sum()),
        fixed=int(((pred==y)&(predr!=y)).sum()),broken=int(((pred!=y)&(predr==y)).sum()))
    g=contract()['gates'];gates=dict(objective=abs(J-Jref)<=g['objective'],remaining=ratio is not None and abs(ratio)<=g['remaining'],
        gradient=grad<=g['gradient'],CE_mean=metrics['CE_mean_abs']<=g['CE_mean'],CE_row=metrics['CE_row_max']<=g['CE_row'],
        TV_mean=metrics['TV_mean']<=g['TV_mean'],TV_row=metrics['TV_max']<=g['TV_row'],logit=metrics['logit_RMSE']<=g['logit_RMSE'],
        decisions=metrics['high_margin_changes']==0 and metrics['weak_changes']<=g['weak_changes'])
    return dict(role_id=role,arm=arm,K=K,**metrics,**{k+'_pass':value for k,value in gates.items()},
                passed=all(gates.values()),failed_gates=[k for k,val in gates.items() if not val])

def quality():
    with stage('quality'):
        A,R,U,O=production();rows=[];selected=None;updates=0;roles=contract()['roles']
        views={arm:[prepared(r,arm) for r in roles] for arm in ['D-P','D-G']}
        refs={arm:[reference(r,arm) for r in roles] for arm in ['D-P','D-G']}
        for K in contract()['K_ladder']:
            current=[]
            for arm in ['D-P','D-G']:
                with torch.no_grad():risk,theta=N.run(U.batch(views[arm]),tensor(np.ones((12,10))),K,U)
                put(dict(theta=theta,risk=risk),OUT/'quality-models'/f'{arm}-K{K}.pt',source_only=True,K=K)
                for i,r in enumerate(roles):
                    row=compare(views[arm][i],theta[i],refs[arm][i],r['t'],tensor(np.ones(10)),K,r['id'],arm,U)
                    rows.append(row);current.append(row)
                updates+=12*K
            save(pd.DataFrame(rows),OUT/'q-one-quality.parquet')
            progress('inner_quality_ladder',K=K,passed=sum(v['passed'] for v in current),total=24,inner_updates=updates)
            if all(v['passed'] for v in current):selected=K;break
        write(OUT/'selection.json',dict(selected_K=selected,passed=selected is not None,
             status='q_one_quality_passed' if selected is not None else 'stop_inner_quality_not_met',
             inner_updates=updates,short_models=len(rows),q_one_reference_refits=0,formal_matrix_authorized=False))

def gradients():
    with stage('gradients'):
        sel=read(OUT/'selection.json');require(sel['passed'],'Quality gate first');K=sel['selected_K']
        A,R,U,O=production();roles=contract()['roles'];rows=[];trajectories=0
        for kind in ['D-P','D-G']:
            ts=[task(r,kind) for r in roles];v=[prepared(r,kind) for r in roles];b=U.batch(v)
            c={k:torch.stack([t['coeff'][k] for t in ts]) for k in ['A','B','C','s']}
            oc=[{k:x.detach().cpu().numpy() for k,x in t['coeff'].items()} for t in ts]
            def evaluate(q):
                risk,theta=N.run(b,q,K,U);smooth=risk+A.regularizer(q);pen=R.soft(q,c)[0];return smooth,pen,risk,theta
            for point,values in [('one',np.ones(10)),('alt',np.array([.9,1.1]*5))]:
                q=tensor(np.tile(values,(12,1))).requires_grad_();sm,pen,risk,theta=evaluate(q)
                gs=torch.autograd.grad(sm.sum(),q,retain_graph=True)[0];gp=torch.autograd.grad(pen.sum(),q,retain_graph=True)[0]
                gt=torch.autograd.grad((sm+pen).sum(),q)[0];trajectories+=12
                put(dict(theta=theta.detach(),risk=risk.detach(),q=q.detach(),smooth_gradient=gs.detach(),total_gradient=gt.detach()),
                    OUT/'gradients'/f'{kind}-{point}.pt',K=K,shared_task_only=(kind=='D-P'))
                oracle=tensor([[O.derivative(float(q[i,j].detach()),oc[i]['A'][j],oc[i]['B'][j],oc[i]['s'][j]) for j in range(10)] for i in range(12)])
                require(float((gp-oracle).abs().max())<1e-10,'Frozen penalty oracle disagreement')
                for h in [1e-3,3e-4]:
                    for j in range(10):
                        plus=q.detach().clone();minus=plus.clone();plus[:,j]+=h;minus[:,j]-=h
                        with torch.no_grad():sp,pp,_,_=evaluate(plus);sn,pn,_,_=evaluate(minus)
                        sf=(sp-sn)/(2*h);lf=(sp+pp-sn-pn)/(2*h);trajectories+=24
                        for i,r in enumerate(roles):
                            branch=O.branch(float(q[i,j].detach()),h,oc[i]['A'][j],oc[i]['B'][j],oc[i]['s'][j]);se=abs(float(sf[i]-gs[i,j]));sl=1e-5+1e-3*abs(float(sf[i]))
                            for arm in ([kind,'T-P'] if kind=='D-P' else [kind]):
                                fd=sf[i] if arm=='T-P' else lf[i];ag=gs[i,j] if arm=='T-P' else gt[i,j]
                                fe=abs(float(fd-ag));fl=1e-5+1e-3*abs(float(fd));full=arm=='T-P' or branch!='boundary'
                                rows.append(dict(role_id=r['id'],arm=arm,K=K,point=point,coordinate=j,h=h,smooth_error=se,smooth_limit=sl,
                                    full_error=fe,full_limit=fl,branch='no_penalty' if arm=='T-P' else branch,
                                    full_required=full,passed=se<=sl and (not full or fe<=fl)))
            progress('new_surrogate_gradient',kind=kind,checks=len(rows),failed=sum(not x['passed'] for x in rows),trajectories=trajectories)
        save(pd.DataFrame(rows),OUT/'new-gradient-checks.parquet')
        result=dict(passed=all(x['passed'] for x in rows),checks=len(rows),trajectories=trajectories,
                    inner_updates=trajectories*K,K=K,old_Q_qualification_reused=False)
        write(OUT/'gradient-verification.json',result);require(result['passed'] and trajectories<=1968,'New gradient gate')

def perturbation():
    with stage('perturbation'):
        require(read(OUT/'gradient-verification.json')['passed'],'New gradient first')
        K=read(OUT/'selection.json')['selected_K'];A,R,U,O=production();optim=solver();rows=[]
        for i,r in enumerate(contract()['roles']):
            for arm in ['D-P','D-G']:
                v=prepared(r,arm);q=tensor(np.array([.9,1.1]*5));s=U.pack(v,arm,q)
                m,log=optim.fit_preconditioned(s['x'],s['y'],s['mass'],r['t'],dict(role_id=r['id'],arm=arm+'-alt'),diagnostic=True)
                put(dict(**m,mu=v['mu'],scale=v['scale']),OUT/'perturbation-models'/r['id']/f'{arm}.pt',optimizer=log,q=[.9,1.1]*5)
                alt=load_own(OUT/'gradients'/f'{arm}-alt.pt');one=load_own(OUT/'gradients'/f'{arm}-one.pt')
                row=compare(v,alt['theta'][i],m,r['t'],q,K,r['id'],arm,U)
                mr=reference(r,arm);ref1=v['query_x']@mr['weight'].T+mr['bias'];refa=v['query_x']@m['weight'].T+m['bias'];y=v['query_y']
                c1=float((torch.logsumexp(ref1,1)-ref1.gather(1,y[:,None]).squeeze(1)).mean())
                ca=float((torch.logsumexp(refa,1)-refa.gather(1,y[:,None]).squeeze(1)).mean())
                dr=ca-c1;dn=float(alt['risk'][i]-one['risk'][i]);limit=1e-4+.1*abs(dr);weak=abs(dr)<=1e-4
                row.update(delta_new=dn,delta_ref=dr,delta_error=abs(dn-dr),delta_limit=limit,
                           weak_signal=weak,direction_ok=weak or dn*dr>0,delta_passed=abs(dn-dr)<=limit,
                           combined_passed=row['passed'] and abs(dn-dr)<=limit and (weak or dn*dr>0))
                rows.append(row);save(pd.DataFrame(rows),OUT/'perturbation-quality.parquet');progress('fixed_perturbation_references',fits=len(rows),cap=24)
        passed=all(v['combined_passed'] for v in rows);weak=all(v['weak_signal'] for v in rows)
        write(OUT/'perturbation-complete.json',dict(passed=passed,all_weak=weak,new_classifier_fits=24,
             status='qualified_pending_confirmation' if passed and not weak else 'stop_weak_perturbation_signal' if passed else 'stop_perturbation_feedback_not_reliable'))

if __name__=='__main__':
    {'register':register,'prepare':prepare,'quality':quality,'gradients':gradients,'perturbation':perturbation}[sys.argv[1]]()
