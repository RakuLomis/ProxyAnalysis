"""Isolated original v4 arithmetic; explicit 1024-update transition only."""
from common import *
import common as C

def backend():
    tree=ast.parse((LEGACY/'solver_v4.py').read_text());tree.body=[n for n in tree.body if not(isinstance(n,ast.ImportFrom) and n.module=='common')]
    m=types.ModuleType('nr2_isolated_original_v4');m.__dict__.update({k:v for k,v in vars(C).items() if not k.startswith('_')})
    exec(compile(ast.fix_missing_locations(tree),str(LEGACY/'solver_v4.py'),'exec'),m.__dict__);return m

def run(s,t,tag,reference=False):
    guard();b=backend();x,y,mass=s['x'],s['y'],s['mass'];cuda(x,mass)
    _,l,ax=b.coordinates(x,mass,t);v=torch.nn.Parameter(torch.zeros((6,97),device=dev(),dtype=torch.float64))
    opt=torch.optim.LBFGS([v],**b.SETTINGS);record={};calls=0;phase=False;last=time.perf_counter()
    def converge(flat):
        nonlocal phase
        chain=flat.reshape(6,97)@l.T;finite(chain)
        record['current_original_gradient_proxy']=float(chain.abs().max())
        if float(chain.abs().max())<=1e-5:
            record['original_audit_evaluations']=record.get('original_audit_evaluations',0)+1
            _,_,g=b.original_audit(v,l,x,y,mass,t)
            require(float((g-chain).abs().max())<1e-10,'Original iteration chain mismatch')
            if float(g.abs().max())<=1e-5:return True
        if not reference and int(opt.state[v].get('n_iter',0))>=1024:
            phase=True;return True
        return False
    b.install_local_step(opt,record,converge)
    if reference:
        # Independent observation point: after selected update, before optimality test.
        ns=inspect.unwrap(opt.step).__globals__;stagnant=ns['_ct_stagnated']
        def observed():
            nonlocal phase
            bad=stagnant()
            if bad:return True
            if int(opt.state[v].get('n_iter',0))>=1024:phase=True;return True
            return False
        ns['_ct_stagnated']=observed
    initial=float(b.transformed_objective(v,l,ax,y,mass,t).detach())
    def closure():
        nonlocal calls,last
        guard();calls+=1;opt.zero_grad();loss=b.transformed_objective(v,l,ax,y,mass,t);finite(loss);loss.backward();finite(v.grad)
        if time.perf_counter()-last>=45:
            progress('LBFGS_heartbeat',tag=tag,iterations=int(opt.state[v].get('n_iter',0)),evaluations=calls);last=time.perf_counter()
        return loss
    started=time.perf_counter();opt.step(closure)
    iterations=int(opt.state[v].get('n_iter',0));evaluations=int(opt.state[v].get('func_evals',0))
    opt.zero_grad();vv=b.transformed_objective(v,l,ax,y,mass,t);vv.backward()
    theta,j,g=b.original_audit(v,l,x,y,mass,t)
    oe=abs(float(vv.detach())-float(j));ge=float((g-v.grad@l.T).abs().max())
    require(oe<1e-10 and ge<1e-10,'LBFGS original replay')
    reason=record.get('reason','unknown')
    if phase:
        reason='reference_prefix_checkpoint' if reference else 'phase_checkpoint'
        record['reason']=reason;record['is_original_gradient_convergence']=False
    require(record.get('reason') not in ['non_descent_failure','unchanged_parameter_failure'],'Original numerical safety failure')
    log=dict(initial_objective=initial,objective=float(j),max_gradient=float(g.abs().max()),objective_replay_error=oe,gradient_replay_error=ge,
        lbfgs_updates=iterations,optimization_evaluations=evaluations,closure_evaluations=calls,lbfgs_seconds=time.perf_counter()-started,
        phase_checkpoint=phase,lbfgs_exit_reason=reason,settings=b.SETTINGS,original_record=record)
    write(OUT/'lbfgs-logs'/f'{tag}.json',log)
    if not reference and float(g.abs().max())>1e-5:
        require(phase and iterations==1024 and evaluations<20000,'No valid Newton transition')
    return theta.detach(),log
