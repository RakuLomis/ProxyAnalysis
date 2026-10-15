"""Fixed 20 Adam updates and q20 full audit, no checkpoint selection."""
from common import *
from solution_feedback import aggregate

def fit_role(r,arm):
    kind='G' if arm=='D-G' else 'P';rs=[e for e in contract()['inner_roles'] if (e['outer'],e['target'],e['group'])==(r['outer'],r['target'],r['group'])]
    require(len(rs)==12,'Source episode set')
    install_tasks({(s['id'],kind):own(OUT/'tasks'/s['id']/(kind+'.pt')) for s in rs})
    coeff=own(OUT/'C-coefficients'/r['id']/(kind+'.pt')) if arm!='T-P' else None
    a,u,_,rec=production();q=torch.ones(10,device=device(),dtype=torch.float64,requires_grad=True)
    opt=torch.optim.Adam([q],lr=.05,betas=(.9,.999),eps=1e-8);rows=[];begin=time.perf_counter()
    for k in range(21):
        qp=q.detach().clone()
        try:
            feedback=aggregate(rs,kind,qp)
            shrink=.01*(q-1).square().mean();gs=torch.autograd.grad(shrink,q)[0]
            if coeff is None:
                penalty=torch.zeros((),device=device(),dtype=torch.float64);gp=torch.zeros_like(q);gap=torch.zeros_like(q);lam=torch.zeros_like(q);error=None
            else:
                penalty,lam,gap=rec.soft(q,coeff);gp=torch.autograd.grad(penalty,q)[0];error=rec.error(q,coeff)
                analytic=lam*(2*coeff['A']*q-2*coeff['B'])/(10*coeff['s'])
                require(float((gp-analytic).abs().max())<1e-10,'Soft penalty analytic gradient replay')
            gradient=feedback['gradient']+gs.detach()+gp.detach();require(torch.isfinite(gradient).all(),'Nonfinite meta gradient')
            row=dict(role_id=r['id'],arm=arm,state=k,Q=feedback['Q'],shrink=float(shrink.detach()),penalty=float(penalty.detach()),
                     total=feedback['Q']+float(shrink.detach()+penalty.detach()),q=qp.tolist(),task_gradient=feedback['gradient'].tolist(),
                     shrink_gradient=gs.tolist(),penalty_gradient=gp.tolist(),total_gradient=gradient.tolist(),
                     gap=gap.detach().tolist(),lambda_closed=lam.detach().tolist(),E=None if error is None else error.detach().tolist(),
                     boundaries=int(((qp==0)|(qp==2)).sum()),mean_gradient_max_difference=feedback['mean_gradient_max_difference'],
                     max_original_gradient=feedback['max_original_gradient'],max_task_gradient_difference=feedback['max_task_gradient_difference'],terminal=k==20)
            rows.append(row)
            # Seal accepted complete q-state and pre-update Adam state. No failed endpoint resume.
            put(dict(q=qp,optimizer_state=opt.state_dict(),feedback=feedback,row=row),OUT/'trajectories'/r['id']/arm/f'q{k:02d}.pt',role_id=r['id'],arm=arm,state=k,accepted=True)
            if k<20:
                q.grad=gradient;opt.step()
                with torch.no_grad():q.clamp_(0,2)
                ledger(q_updates=1)
            progress('q_state_accepted',role=r['id'],arm=arm,state=k,terminal=k==20,seconds=time.perf_counter()-begin)
        except BaseException:
            put(dict(q=qp,optimizer_state=opt.state_dict(),completed_rows=rows),OUT/'failures'/f'meta-{arm}-{time.time_ns()}.pt',role_id=r['id'],arm=arm,state=k,automatic_retry=False)
            raise
    path=OUT/'q'/r['id']/(arm+'.pt')
    put(dict(q=q.detach(),optimizer_state=opt.state_dict()),path,role_id=r['id'],arm=arm,selected_state=20,updates=20,Q_terminal=rows[-1]['Q'],seconds=time.perf_counter()-begin)
    save(pd.DataFrame(rows),OUT/'trajectories'/r['id']/(arm+'.parquet'));return path

