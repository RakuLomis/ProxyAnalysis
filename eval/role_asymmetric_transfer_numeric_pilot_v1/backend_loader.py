"""Isolated historical functions with policy/IO injection and read-only taps."""
from common import *
import common as C

def module_from_source(path,bindings):
    tree=ast.parse(Path(path).read_text(encoding='utf-8-sig'))
    tree.body=[n for n in tree.body if not (isinstance(n,ast.ImportFrom) and n.module=='common')]
    ast.fix_missing_locations(tree);m=types.ModuleType('nr1_isolated_'+Path(path).stem)
    m.__dict__.update({k:v for k,v in vars(C).items() if not k.startswith('_')});m.__dict__.update(bindings)
    exec(compile(tree,str(path),'exec'),m.__dict__);return m

def policy(old=False):
    m=module_from_source(OLD_CODE/'numeric_policy.py',{})
    if not old:m.POLICY=dict(m.POLICY,version='RA1-NR1-budget-only',max_iter=4000,max_eval=20000)
    return m

def load(attempt_root,old=False,capture=False):
    pol=policy(old);writable(attempt_root/'manifests/numeric-policy.json');write(attempt_root/'manifests/numeric-policy.json',pol.POLICY)
    m=module_from_source(OLD_CODE/'solver_v4.py',dict(OUT=attempt_root,POLICY=pol.POLICY,SOLVER=pol.SOLVER,acceptance_gates=pol.acceptance_gates))
    # Every historical algorithm function is compiled unchanged. Wrappers only
    # check activity budgets and clone an accepted-point observation at n=2000.
    source_objective=m.transformed_objective
    def objective(*args,**kwargs):budget_check();return source_objective(*args,**kwargs)
    m.transformed_objective=objective
    source_install=m.install_local_step;m.prefix=None
    def install(opt,record,converge=None,original_mode=False):
        def observed(flat):
            budget_check()
            if capture and m.prefix is None and int(opt.state[opt._params[0]].get('n_iter',0))==2000:
                m.prefix=dict(parameter_V=opt._params[0].detach().clone(),selected_flat_gradient=flat.detach().clone(),iterations=2000,
                              evaluations=int(opt.state[opt._params[0]].get('func_evals',0)))
            return converge(flat)
        return source_install(opt,record,observed if converge is not None else None,original_mode)
    m.install_local_step=install
    return m

def weight_functions():return module_from_source(OLD_CODE/'weight_schedule.py',{})
