import common as C
from common import *
from head import *

def fit(r,arm,seed):
    budget();require(read(OUT/'ledger.json')['attempted_fits']<132,'132 physical fit cap')
    path=modelpath(r,arm,seed);require(not path.exists(),'No repeated accepted fit')
    s,m,g=train(r,arm,seed);phi=features(s['x'],g,arm).detach();z0=offset(s['x'],m).detach();q=basis();geo=geometry(z0,q)
    w=torch.nn.Parameter(torch.zeros((5,phi.shape[1]),device=device(),dtype=torch.float64))
    b=torch.nn.Parameter(torch.zeros(5,device=device(),dtype=torch.float64))
    opt=torch.optim.LBFGS([w,b],lr=1.,max_iter=2000,max_eval=10000,tolerance_grad=1e-9,
                         tolerance_change=1e-12,history_size=100,line_search_fn='strong_wolfe')
    initial=float(objective(w,b,phi,z0,s['y'],s['mass'],q,geo).detach());calls=0
    start=time.perf_counter();C.FIT_START=start;ledger(attempted_fits=1)
    try:
        def closure():
            nonlocal calls
            budget();require(calls<10000,'Per-head 10000 evaluation budget');calls+=1
            opt.zero_grad(set_to_none=True);j=objective(w,b,phi,z0,s['y'],s['mass'],q,geo)
            require(bool(torch.isfinite(j)),'Nonfinite head objective');j.backward();return j
        opt.step(closure);opt.zero_grad(set_to_none=True)
        j=objective(w,b,phi,z0,s['y'],s['mass'],q,geo);j.backward()
        with torch.no_grad():
            ind=independent(w,b,phi,z0,s['y'],s['mass'],q)
            grad=max(maxabs(ind['gd']),maxabs(ind['ge']));freegrad=max(maxabs(ind['gw']),maxabs(ind['gb']))
            je=abs(float(j)-float(ind['objective']));ge=max(maxabs(w.grad-ind['gw']),maxabs(b.grad-ind['gb']))
            zz,h,delta=logits(w,b,phi,z0,q,geo);geometry_log=geometry_errors(geo['s'],delta,geo['mask'])
            ok=bool(torch.isfinite(j)) and float(j)<=initial+1e-10 and grad<=1e-5 and je<=1e-10 and ge<=1e-10
            diag=dict(passed=ok,role_id=r['id'],role_target=r['target'],query_deployment=r['calibration'],
                 arm=arm,seed=seed_for(arm,seed),initial_objective=initial,objective=float(j),CE=float(ind['CE']),L2=float(ind['L2']),
                 max_original_gradient=grad,max_free_gradient=freegrad,objective_replay_error=je,gradient_replay_error=ge,
                 iterations=int(opt.state[w].get('n_iter',0)),function_evaluations=calls,
                 dimension=phi.shape[1],free_parameters=5*phi.shape[1]+5,
                 W_x_norm=float(w[:,:96].norm()),W_g_norm=float(w[:,96:].norm()),bias_norm=float(b.norm()),
                 delta_RMS=float(delta.square().mean().sqrt()),pre_projection_RMS=float(h.square().mean().sqrt()),
                 geometry=geometry_log,seconds=time.perf_counter()-start,device='cuda:0',dtype='float64')
            write(OUT/'fit-logs'/r['id']/f'{arm}-seed{seed_for(arm,seed)}.json',diag)
            require(ok,'Original-coordinate readout optimization quality gate')
            put(path,dict(W=w.detach(),b=b.detach(),Q=q),role_id=r['id'],arm=arm,seed=seed_for(arm,seed),eta=.01,tau=1e-12)
            ledger(accepted_fits=1)
            return diag
    finally:
        torch.cuda.synchronize();ledger(fit_seconds=time.perf_counter()-start);C.FIT_START=None
