import common as C
from common import *
from features import load_train,ensure_g,feature,offset
from head import basis,objective,independent,projected

def fit(r,arm,eta,seed):
    budget();path=modelpath(r,arm,eta,seed);require(not path.exists(),'No accepted fit repeats')
    s,m=load_train(r);g=ensure_g(r,arm,seed);phi=feature(s['x'],g);z0=offset(s['x'],m);q=basis()
    a=torch.nn.Parameter(torch.zeros((5,phi.shape[1]),device=device(),dtype=torch.float64));b=torch.nn.Parameter(torch.zeros(5,device=device(),dtype=torch.float64))
    opt=torch.optim.LBFGS([a,b],lr=1.,max_iter=2000,max_eval=10000,tolerance_grad=1e-9,
                         tolerance_change=1e-12,history_size=100,line_search_fn='strong_wolfe')
    calls=0;started=time.perf_counter();C._FIT_START=started;ledger(attempted_fits=1)
    initial=float(objective(a,b,phi,z0,s['y'],s['mass'],eta,q).detach())
    try:
        def closure():
            nonlocal calls
            budget();require(calls<10000,'Per-head max_eval exhausted');calls+=1
            opt.zero_grad(set_to_none=True);v=objective(a,b,phi,z0,s['y'],s['mass'],eta,q)
            require(bool(torch.isfinite(v)),'Nonfinite readout objective');v.backward();return v
        opt.step(closure)
        opt.zero_grad(set_to_none=True);value=objective(a,b,phi,z0,s['y'],s['mass'],eta,q);value.backward()
        with torch.no_grad():
            check=independent(a,b,phi,z0,s['y'],s['mass'],eta,q)
            grad=max(float(check['gd'].abs().max()),float(check['ge'].abs().max()))
            replay=abs(float(check['objective'])-float(value));gradient_replay=max(float((check['ga']-a.grad).abs().max()),float((check['gb']-b.grad).abs().max()))
            d,e=projected(a,b,q)
            log=dict(role_id=r['id'],arm=arm,eta=eta,seed=seed if arm!='X' else 0,
                initial_objective=initial,objective=float(value),CE=float(check['CE']),L2=float(check['L2']),
                max_original_gradient=grad,objective_replay_error=replay,gradient_replay_error=gradient_replay,
                iterations=int(opt.state[a].get('n_iter',0)),function_evaluations=calls,
                dimension=phi.shape[1],free_parameters=5*phi.shape[1]+5,
                D_x_norm=float(d[:,:96].norm()),D_g_norm=0. if arm=='X' else float(d[:,96:].norm()),
                bias_norm=float(e.norm()),seconds=time.perf_counter()-started,device='cuda:0',dtype='float64')
            ok=bool(torch.isfinite(value)) and float(value)<=initial+1e-10 and grad<=1e-5 and replay<=1e-10 and gradient_replay<=1e-10
            log['passed']=ok
            write(OUT/'fit-logs'/r['id']/tag(arm,eta,seed)/'quality.json',log)
            require(ok,'Readout original-coordinate optimization quality gate')
            put(path,dict(A=a.detach(),b=b.detach(),Q=q,D=d.detach(),e=e.detach()),
                role_id=r['id'],arm=arm,eta=eta,seed=seed if arm!='X' else 0,accepted=True)
            ledger(accepted_fits=1)
        return log
    finally:
        torch.cuda.synchronize();ledger(fit_seconds=time.perf_counter()-started);C._FIT_START=None
