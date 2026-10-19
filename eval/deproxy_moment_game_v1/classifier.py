"""Explicit-gamma CUDA convex heads, optional reversible Cholesky coordinates."""
from common import *

def basis():
    q=torch.zeros((6,5),device='cuda',dtype=torch.float64)
    for j in range(5):v=((j+1)*(j+2))**-.5;q[:j+1,j]=v;q[j+1,j]=-(j+1)*v
    return q
def objective(W,c,x,y,w,gamma):
    return (F.cross_entropy(F.linear(x,W,c),y,reduction='none')*w).sum()+gamma*W.square().sum()
def independent(W,c,x,y,w,gamma):
    z=x@W.T+c;lp=z-z.logsumexp(1)[:,None];ce=-(lp.gather(1,y[:,None]).squeeze(1)*w).sum()
    err=(lp.exp()-F.one_hot(y,6))*w[:,None]
    return ce+gamma*(W*W).sum(),err.T@x+2*gamma*W,err.sum(0),ce

def within_budget(quality):
    return quality['iterations']<quality['settings']['max_iter'] and quality['evaluations']<quality['settings']['max_eval']

def fit(x,y,w,gamma,path,meta,init=None):
    if Path(path).exists():
        # Reuse accepted artifacts only after replaying the original-coordinate
        # equations on the requested, capability-legal current training arrays.
        h=own(path,meta['role_id']);quality=read(Path(path).with_suffix('.quality.json'))
        replay,gW,gc,_=independent(h['W'],h['c'],x,y,w,gamma)
        require(quality['passed'] and within_budget(quality) and quality['gamma']==gamma and max(float(gW.abs().max()),float(gc.abs().max()))<=1e-5 and
            abs(float(replay)-quality['objective'])/max(1,abs(quality['objective']))<=1e-10,'Saved convex head compatibility replay')
        return h
    remaining();require(x.is_cuda and x.dtype==torch.float64 and x.shape[1]==96,'CUDA float64 head')
    require(abs(float(w.sum())-1)<1e-12 and float((F.one_hot(y,6).double().T@w-1/6).abs().max())<1e-12,'Head masses')
    started=time.perf_counter();available=remaining();q=basis();aug=torch.cat([x,torch.ones((len(x),1),device='cuda',dtype=torch.float64)],1)
    H=aug.T@(aug*w[:,None])/6+torch.diag(torch.cat([torch.full((96,),2*gamma,device='cuda',dtype=torch.float64),torch.zeros(1,device='cuda',dtype=torch.float64)]))
    L=torch.linalg.cholesky(H);ax=torch.linalg.solve_triangular(L,aug.T,upper=False).T
    theta=torch.zeros((5,97),device='cuda',dtype=torch.float64) if init is None else q.T@torch.cat([init['W'],init['c'][:,None]],1)
    v=torch.nn.Parameter(theta@L)
    def decode():return torch.linalg.solve_triangular(L.T,v.T,upper=True).T
    def value():
        th=decode();logits=(ax@v.T)@q.T
        return (F.cross_entropy(logits,y,reduction='none')*w).sum()+gamma*th[:,:96].square().sum()
    opt=torch.optim.LBFGS([v],lr=1,max_iter=2000,max_eval=10000,history_size=100,line_search_fn='strong_wolfe',tolerance_grad=1e-9,tolerance_change=1e-12)
    initial=float(value().detach());calls=0
    def closure():
        nonlocal calls
        require(calls<10000,'Head total function-evaluation budget exhausted');calls+=1
        # This process is the sole budget writer: cache the remaining allowance
        # rather than parse the cumulative audit JSON at every line-search call.
        require(time.perf_counter()-started<available,'Global activity budget exhausted in head')
        opt.zero_grad(set_to_none=True);loss=value();require(torch.isfinite(loss),'Nonfinite head');loss.backward();return loss
    try:
        opt.step(closure)
        opt.zero_grad(set_to_none=True);val=value();val.backward()
        th=decode().detach();full=q@th;W=full[:,:96];c=full[:,96]
        replay,gW,gc,ce=independent(W,c,x,y,w,gamma)
        original_grad=max(float(gW.abs().max()),float(gc.abs().max()))
        gtheta=q.T@torch.cat([gW,gc[:,None]],1);gv=torch.linalg.solve_triangular(L,gtheta.T,upper=False).T
        err=abs(float(replay)-float(val.detach()))/max(1,abs(float(replay)))
        ge=float((gv-v.grad).abs().max())/max(1,float(gv.abs().max()))
        log=dict(**meta,gamma=gamma,objective=float(replay),initial_objective=initial,CE=float(ce),original_gradient_max=original_grad,
            independent_objective_error=err,independent_gradient_error=ge,iterations=int(opt.state[v].get('n_iter',0)),evaluations=calls,
            settings=dict(max_iter=2000,max_eval=10000,history=100,tolerance_grad=1e-9,tolerance_change=1e-12),
            coordinate='fixed reversible Cholesky; L2 on original W, no bias regularization',seconds=time.perf_counter()-started)
        numerical=original_grad<=1e-5 and err<=1e-10 and ge<=1e-10 and float(replay)<=initial+1e-10
        passed=numerical and within_budget(log)
        reason='accepted' if passed else ('cumulative_budget_limit' if not within_budget(log) else 'original_coordinate_quality_failed')
        immutable(Path(path).with_suffix('.quality.json'),dict(**log,passed=passed,numerical_quality_passed=numerical,stop_reason=reason))
        require(passed,'Convex head '+reason+'; no automatic refinement or beta0 fallback')
        put(path,dict(W=W.detach(),c=c.detach()),**meta,accepted=True,gamma=gamma)
        return dict(W=W.detach(),c=c.detach())
    except BaseException as e:
        failure('head',e);raise
    finally:
        torch.cuda.synchronize();debit('convex-head',time.perf_counter()-started,role_id=meta['role_id'],path=rel(path),gamma=gamma,evaluations=calls)
