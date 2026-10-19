"""Reversible v2 coordinates; v4 original-gradient-aware local LBFGS stops."""
import ast
import inspect
import textwrap
import types
import hashlib
from collections import Counter
import torch.optim.lbfgs as installed
from common import *

SETTINGS = dict(lr=1., max_iter=POLICY['max_iter'], max_eval=POLICY['max_eval'], history_size=100,
                tolerance_grad=1e-9, tolerance_change=1e-12, line_search_fn='strong_wolfe')

def coordinates(x, mass, t):
    a = torch.cat([x, torch.ones((len(x), 1), device=x.device, dtype=x.dtype)], 1)
    h = a.T@(a*mass[:, None])/6
    h = h+torch.diag(torch.cat([torch.full((96,), .001*(1+t), device=x.device, dtype=x.dtype),
                               torch.zeros(1, device=x.device, dtype=x.dtype)]))
    l = torch.linalg.cholesky(h)
    ax = torch.linalg.solve_triangular(l, a.T, upper=False).T
    return a, l, ax

def decode(v, l): return torch.linalg.solve_triangular(l.T, v.T, upper=True).T
def transformed_objective(v, l, a, y, mass, t):
    theta = decode(v, l)
    return (F.cross_entropy(a@v.T, y, reduction='none')*mass).sum()+.0005*(1+t)*theta[:, :96].square().sum()

def original_audit(v, l, x, y, mass, t):
    with torch.enable_grad():
        theta = decode(v.detach(), l)
        w = theta[:, :96].clone().requires_grad_(); b = theta[:, 96].clone().requires_grad_()
        z = x@w.T+b
        loss = (mass*(torch.logsumexp(z, 1)-z.gather(1, y[:, None]).squeeze(1))).sum()
        loss = loss+.0005*(1+t)*w.square().sum()
        gw, gb = torch.autograd.grad(loss, (w,b))
    return theta, loss.detach(), torch.cat([gw,gb[:,None]], 1)

def gates(value, initial, gradient, iterations, error, gradient_error):
    return acceptance_gates(value, initial, gradient, iterations, error, gradient_error)

def stop_action(original_gradient, *, finite=True, gtd=None, unchanged=0, iterations=0,
                evaluations=0, small_change=False, small_step=False):
    """Pure injectable stop policy, also used by negative unit tests."""
    if not finite: return 'nonfinite_failure'
    if iterations >= POLICY['max_iter']: return 'iteration_budget'
    if evaluations >= POLICY['max_eval']: return 'evaluation_budget'
    if original_gradient <= 1e-5: return 'original_gradient_candidate'
    if gtd is not None and (not np.isfinite(gtd) or gtd >= 0): return 'non_descent_failure'
    if unchanged >= 3: return 'unchanged_parameter_failure'
    return 'continue'

def reference_metadata():
    step = textwrap.dedent(inspect.getsource(inspect.unwrap(torch.optim.LBFGS.step)))
    line = textwrap.dedent(inspect.getsource(installed._strong_wolfe))
    return {'installed_file': inspect.getfile(torch.optim.LBFGS),
            'installed_file_sha256': sha(Path(inspect.getfile(torch.optim.LBFGS))),
            'step_sha256': hashlib.sha256(step.encode()).hexdigest(),
            'line_search_sha256': hashlib.sha256(line.encode()).hexdigest(),
            'step_source': step, 'line_search_source': line,
            'changes': ['Original gradient replaces both transformed-gradient optimal exits',
                'Negative gtd of arbitrarily small magnitude may proceed',
                'Small loss/parameter change is logged, not accepted as convergence',
                'Three exactly unchanged updates fail',
                'Budget branch order, two-loop and line-search arithmetic retained; limits uniformly revised',
                'All logic changes are local; installed library/class is never patched']}

def _line_function(record):
    tree = ast.parse(textwrap.dedent(inspect.getsource(installed._strong_wolfe)))
    class Observe(ast.NodeTransformer):
        def visit_Return(self, node):
            return [ast.Expr(ast.Call(ast.Name('_ct_line_record',ast.Load()),
                [ast.Call(ast.Name('locals',ast.Load()),[],[])],[])), node]
    tree=Observe().visit(tree);ast.fix_missing_locations(tree)
    namespace=dict(installed._strong_wolfe.__globals__)
    def hook(local):
        step=local['t']; loss=local['f_new']; g=local['g_new']; gtd=local['gtd']
        armijo=bool(loss <= local['f']+local['c1']*step*gtd)
        curvature=bool(abs(float(g.dot(local['d']))) <= -local['c2']*float(gtd))
        bracket=local.get('bracket',[])
        width=float(abs(bracket[1]-bracket[0])*local['d_norm']) if len(bracket)==2 else None
        reason='wolfe_satisfied' if local['done'] else ('max_ls' if local['ls_iter'] >= local['max_ls'] else 'bracket_tolerance')
        row={'reason':reason,'armijo':armijo,'curvature':curvature,
             'iterations':int(local['ls_iter']),'evaluations':int(local['ls_func_evals']),
             'step':float(step),'bracket_width_times_direction':width}
        record['line_searches'].append(row)
    namespace['_ct_line_record']=hook
    exec(compile(tree,'<local-observed-installed-strong-wolfe>','exec'),namespace)
    return namespace['_strong_wolfe']

def install_local_step(opt, record, converge=None, original_mode=False):
    """Derive a local step from sealed installed reference; never global-patch."""
    tree=ast.parse(textwrap.dedent(inspect.getsource(inspect.unwrap(torch.optim.LBFGS.step))))
    tree.body[0].decorator_list=[]
    replaced=Counter()
    class Rewrite(ast.NodeTransformer):
        def visit_If(self,node):
            self.generic_visit(node)
            test=ast.unparse(node.test)
            if not original_mode:
                if test=='opt_cond':
                    node.test=ast.parse('_ct_converged(flat_grad)',mode='eval').body
                    replaced['optimal']+=1
                elif test=='gtd > -tolerance_change':
                    node.test=ast.parse('_ct_bad_direction(gtd)',mode='eval').body
                    replaced['direction']+=1
                elif test in ['d.mul(t).abs().max() <= tolerance_change','abs(loss - prev_loss) < tolerance_change']:
                    node.body=[ast.Expr(ast.Call(ast.Name('_ct_small_event',ast.Load()),[ast.Constant(test)],[]))]
                    replaced['small']+=1
            for j,item in enumerate(node.body):
                if isinstance(item,(ast.Break,ast.Return)):
                    node.body.insert(j,ast.Expr(ast.Call(ast.Name('_ct_stop',ast.Load()),
                        [ast.Constant(test),ast.Call(ast.Name('locals',ast.Load()),[],[])],[])))
                    break
            return node
        def visit_Expr(self,node):
            if not original_mode and ast.unparse(node)=='self._add_grad(t, d)':
                # This runs at the selected line-search point, not last trial.
                replaced['updated']+=1
                return [node,ast.parse('if _ct_stagnated():\n    break').body[0]]
            return node
    tree=Rewrite().visit(tree);ast.fix_missing_locations(tree)
    if not original_mode:
        require(dict(replaced)=={'optimal':2,'direction':1,'small':2,'updated':2},'Unexpected installed LBFGS AST')
    namespace=dict(inspect.unwrap(torch.optim.LBFGS.step).__globals__)
    record.setdefault('line_searches',[]);record.setdefault('small_events',{})
    record.setdefault('original_audit_evaluations',0)
    previous=opt._params[0].detach().clone();same=0
    def converged(flat):
        ok=converge(flat)
        if ok: record['reason']='original_gradient_converged'
        return ok
    def bad_direction(gtd):
        value=float(gtd)
        if not np.isfinite(value) or value>=0:
            record['reason']='non_descent_failure';return True
        if value > -SETTINGS['tolerance_change']: small('negative_small_gtd')
        return False
    def small(name): record['small_events'][name]=record['small_events'].get(name,0)+1
    def stagnant():
        nonlocal previous,same
        current=opt._params[0].detach()
        same=same+1 if torch.equal(current,previous) else 0
        previous=current.clone();record['unchanged_updates']=same
        if same>=3: record['reason']='unchanged_parameter_failure';return True
        return False
    def stop(test,local):
        record['condition']=test
        if test=='n_iter == max_iter':record['reason']='iteration_budget'
        elif test=='current_evals >= max_eval':record['reason']='evaluation_budget'
        for key in ['n_iter','current_evals','max_iter','max_eval','loss','prev_loss','gtd','t']:
            value=local.get(key)
            if value is not None:record[key]=float(value.detach()) if torch.is_tensor(value) else value
    namespace.update(_ct_converged=converged,_ct_bad_direction=bad_direction,
                     _ct_small_event=small,_ct_stagnated=stagnant,_ct_stop=stop,
                     _strong_wolfe=_line_function(record))
    exec(compile(tree,'<local-original-gradient-aware-lbfgs-v4>','exec'),namespace)
    opt.step=types.MethodType(torch.no_grad()(namespace['step']),opt)
    return dict(replaced)

def fit_preconditioned(x,y,mass,t,context,diagnostic=False):
    basepath=OUT/('diagnostic-fit-logs' if diagnostic else 'fit-logs')/context['role_id']/f"{context['arm']}-t{t:g}.json"
    failure=OUT/('diagnostic-failures' if diagnostic else 'failures')/context['role_id']/f"{context['arm']}-t{t:g}.pt"
    log={**context,'solver':SOLVER,'settings':SETTINGS,'initialization':'zero',
         'device':'cuda:0','dtype':'float64','formal_fit':not diagnostic,
         'numeric_policy_sha256':sha(OUT/'manifests/numeric-policy.json')}
    started=time.perf_counter();v=l=opt=None;record={};calls=0;last_heartbeat=started
    try:
        require(x.is_cuda and x.dtype==torch.float64,'CUDA float64 required')
        require(x.shape[1]==96 and abs(float(mass.sum())-1)<1e-12,'Coordinate/mass')
        require(torch.isfinite(x).all() and (mass>0).all(),'Nonfinite input or invalid mass')
        require(float((weighted(y,mass,6)-1/6).abs().max())<1e-12,'Class mass changed')
        _,l,ax=coordinates(x,mass,t)
        v=torch.nn.Parameter(torch.zeros((6,97),device=device(),dtype=torch.float64))
        opt=torch.optim.LBFGS([v],**SETTINGS)
        def converge(flat):
            chain=flat.reshape(6,97)@l.T
            require(torch.isfinite(chain).all(),'Nonfinite chain gradient')
            record['current_original_gradient_proxy']=float(chain.abs().max())
            if record['current_original_gradient_proxy']>1e-5:return False
            record['original_audit_evaluations']+=1
            _,_,gradient=original_audit(v,l,x,y,mass,t)
            require(float((gradient-chain).abs().max())<1e-10,'Independent iteration gradient mismatch')
            return float(gradient.abs().max())<=1e-5
        install_local_step(opt,record,converge)
        initial=float(transformed_objective(v,l,ax,y,mass,t).detach())
        def closure():
            nonlocal calls,last_heartbeat
            calls+=1;opt.zero_grad();loss=transformed_objective(v,l,ax,y,mass,t)
            require(torch.isfinite(loss),'Nonfinite loss');loss.backward()
            require(torch.isfinite(v.grad).all(),'Nonfinite transformed gradient')
            if time.perf_counter()-last_heartbeat>=60:
                progress('GS_solver_heartbeat',role=context['role_id'],arm=context['arm'],t=t,
                         evaluations=calls,iterations=int(opt.state[v].get('n_iter',0)))
                last_heartbeat=time.perf_counter()
            return loss
        opt.step(closure);value=float(closure().detach())
        theta,replay,gradient=original_audit(v,l,x,y,mass,t)
        record['original_audit_evaluations']+=1
        err=abs(float(replay)-value);gerr=float((gradient-v.grad@l.T).abs().max())
        iterations=int(opt.state[v].get('n_iter',0));maximum=float(gradient.abs().max())
        accepted=gates(float(replay),initial,maximum,iterations,err,gerr)
        hard_failure=record.get('reason') in ['non_descent_failure','unchanged_parameter_failure']
        log.update(initial_objective=initial,objective=float(replay),transformed_objective=value,
            iterations=iterations,function_evaluations=int(opt.state[v].get('func_evals',0)),
            closure_evaluations=calls,max_gradient=maximum,transformed_gradient_max=float(v.grad.abs().max()),
            objective_replay_error=err,gradient_replay_error=gerr,gates=accepted,
            accepted=all(accepted.values()) and not hard_failure,actual_optimizer_break=record,
            original_audit_evaluations=record['original_audit_evaluations'],seconds=time.perf_counter()-started,
            iteration_budget_hit=iterations>=POLICY['max_iter'],
            evaluation_budget_hit=int(opt.state[v].get('func_evals',0))>=POLICY['max_eval'],
            evaluation_budget_overshoot=max(0,int(opt.state[v].get('func_evals',0))-POLICY['max_eval']),
            optimizer_exit_reason=record.get('reason','unknown'),cuda_peak_MiB=torch.cuda.max_memory_allocated()/1048576)
        write(basepath,log)
        require(log['accepted'],'Original-coordinate precision, revised budget or numerical safety failure; no further extension')
        return {'weight':theta[:,:96].detach(),'bias':theta[:,96].detach()},log
    except BaseException as exc:
        log.update(accepted=False,exception_type=type(exc).__name__,exception=str(exc),
                   seconds=time.perf_counter()-started,actual_optimizer_break=record)
        write(failure.with_suffix('.json'),log);failure.parent.mkdir(parents=True,exist_ok=True)
        torch.save({'parameter_V':None if v is None else v.detach(),'cholesky':l,
                    'optimizer_state':None if opt is None else opt.state_dict(),
                    'last_original_parameters':None if v is None or l is None else decode(v.detach(),l)},writable(failure))
        raise
