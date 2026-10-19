"""Same original convex objective; certified accepted points and no global sync."""
from common import *
from lbfgs_local import CertifiedLBFGS, EvaluationBudget

SETTINGS=dict(max_iter=2000,max_eval=10000,history_size=100,lr=1.,line_search_fn='strong_wolfe',tolerance_grad=1e-9,tolerance_change=1e-12)

def basis():
    q=torch.zeros((6,5),device='cuda',dtype=torch.float64)
    for j in range(5):
        v=((j+1)*(j+2))**-.5;q[:j+1,j]=v;q[j+1,j]=-(j+1)*v
    return q

def objective(W,c,x,y,w,gamma):
    return (F.cross_entropy(F.linear(x,W,c),y,reduction='none')*w).sum()+gamma*W.square().sum()

def independent(W,c,x,y,w,gamma):
    z=x@W.T+c;lp=z-z.logsumexp(1)[:,None];ce=-(lp.gather(1,y[:,None]).squeeze(1)*w).sum()
    err=(lp.exp()-F.one_hot(y,6))*w[:,None]
    return ce+gamma*(W*W).sum(),err.T@x+2*gamma*W,err.sum(0),ce

def gate(iterations,evaluations,gradient,oe,ge,value,initial):
    budget=iterations<2000 and evaluations<10000
    numeric=all(np.isfinite(t) for t in [gradient,oe,ge,value,initial]) and gradient<=1e-5 and oe<=1e-10 and ge<=1e-10 and value<=initial+1e-10
    return budget and numeric, budget, numeric

def solve(x,y,w,gamma,init=None):
    started=time.perf_counter();deadline()
    require(x.is_cuda and x.dtype==torch.float64 and x.shape[1]==96,'CUDA float64 head')
    require(bool(torch.isfinite(x).all()) and bool(torch.isfinite(w).all()),'Nonfinite head input')
    require(abs(float(w.sum())-1)<1e-12 and float((F.one_hot(y,6).double().T@w-1/6).abs().max())<1e-12,'Head masses')
    q=basis();aug=torch.cat([x,torch.ones((len(x),1),device='cuda',dtype=torch.float64)],1)
    H=aug.T@(aug*w[:,None])/6+torch.diag(torch.cat([torch.full((96,),2*gamma,device='cuda',dtype=torch.float64),torch.zeros(1,device='cuda',dtype=torch.float64)]))
    L=torch.linalg.cholesky(H);ax=torch.linalg.solve_triangular(L,aug.T,upper=False).T
    theta=torch.zeros((5,97),device='cuda',dtype=torch.float64) if init is None else q.T@torch.cat([init['W'],init['c'][:,None]],1)
    v=torch.nn.Parameter(theta@L)
    def decode():return torch.linalg.solve_triangular(L.T,v.T,upper=True).T
    def value():
        th=decode();logits=(ax@v.T)@q.T
        return (F.cross_entropy(logits,y,reduction='none')*w).sum()+gamma*th[:,:96].square().sum()
    def certify(flat,it,ev):
        gv=flat.reshape(5,97);original=q@(gv@L.T)
        residual=float(original.abs().max())
        require(np.isfinite(residual),'Nonfinite accepted-point gradient')
        return residual<=1e-5,residual
    opt=CertifiedLBFGS([v],certify=certify,**SETTINGS)
    initial=float(value().detach());calls=0;error=None
    def closure():
        nonlocal calls
        if calls>=10000:raise EvaluationBudget('evaluation_budget')
        deadline();calls+=1;opt.zero_grad(set_to_none=True);loss=value()
        require(bool(torch.isfinite(loss)),'Nonfinite head loss');loss.backward();return loss
    try:opt.step(closure)
    except EvaluationBudget as e:
        opt._set_param(opt.last_accepted);opt.exit_reason='evaluation_budget';error=str(e)
    # Independent audit does not update history, selected gradient, or parameters.
    opt.zero_grad(set_to_none=True);val=value();val.backward()
    th=decode().detach();full=q@th;W=full[:,:96];c=full[:,96]
    replay,gW,gc,ce=independent(W,c,x,y,w,gamma)
    original_grad=max(float(gW.abs().max()),float(gc.abs().max()))
    gtheta=q.T@torch.cat([gW,gc[:,None]],1);gv=torch.linalg.solve_triangular(L,gtheta.T,upper=False).T
    oe=abs(float(replay)-float(val.detach()))/max(1,abs(float(replay)))
    ge=float((gv-v.grad).abs().max())/max(1,float(gv.abs().max()))
    iterations=int(opt.state[v].get('n_iter',0))
    passed,budget,numeric=gate(iterations,calls,original_grad,oe,ge,float(replay),initial)
    torch.cuda.current_stream().synchronize()
    quality=dict(version='NER1',gamma=gamma,objective=float(replay),initial_objective=initial,CE=float(ce),
        original_gradient_max=original_grad,independent_objective_error=oe,independent_gradient_error=ge,
        iterations=iterations,evaluations=calls,independent_audit_evaluations=2,settings=SETTINGS,
        numeric_pass=numeric,budget_pass=budget,accepted=passed,optimizer_exit=opt.exit_reason,
        acceptance_reason='accepted' if passed else ('cumulative_budget_limit' if not budget else 'original_coordinate_quality_failed'),
        accepted_points=opt.accepted_points,seconds=time.perf_counter()-started,error=error)
    return dict(head=dict(W=W.detach(),c=c.detach()),quality=quality,
        numeric_state=dict(v=v.detach(),gradient=v.grad.detach().clone(),optimizer=opt.state_dict()))

def persist(path,result,**meta):
    path=Path(path);write(path.with_suffix('.quality.json'),dict(**result['quality'],**meta),True)
    # A failed snapshot remains explicitly unaccepted, never a reusable model.
    put(path,result['head'],accepted=result['quality']['accepted'],**meta)
    put(path.with_name(path.stem+'-solver.pt'),result['numeric_state'],**meta)

def validate_old_head(h,x,y,w,gamma):
    v,g,c,_=independent(h['W'],h['c'],x,y,w,gamma)
    require(max(float(g.abs().max()),float(c.abs().max()))<=1e-5 and bool(torch.isfinite(v)),'Historical head original-equation replay')

def comparison(new,old,x):
    with torch.no_grad():
        a=F.linear(x,new['W'],new['c']);b=F.linear(x,old['W'],old['c'])
        return dict(parameter_max=max(float((new[k]-old[k]).abs().max()) for k in ['W','c']),
            relative_logit_max=float(((a-a.mean(1,keepdim=True))-(b-b.mean(1,keepdim=True))).abs().max()),
            probability_max=float((a.softmax(1)-b.softmax(1)).abs().max()),training_class_changes=int((a.argmax(1)!=b.argmax(1)).sum()))
