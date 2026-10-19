"""Sealed NR2 arithmetic in an isolated full-run IO/budget namespace."""
from common import *
import common as C
import textwrap

_MODULES=None
def modules():
    global _MODULES
    if _MODULES is None:
        runtime=types.ModuleType('nr2_full_train_runtime');runtime.__dict__.update({k:v for k,v in vars(C).items() if not k.startswith('_')})
        def load(name):
            path=NR2_CODE/(name+'.py');tree=ast.parse(path.read_text())
            tree.body=[n for n in tree.body if not(isinstance(n,ast.ImportFrom) and n.module=='common') and not(isinstance(n,ast.Import) and any(a.name=='common' for a in n.names))]
            m=types.ModuleType('sealed_NR2_'+name);m.__dict__.update(runtime.__dict__);m.__dict__['C']=runtime
            exec(compile(ast.fix_missing_locations(tree),str(path),'exec'),m.__dict__);return m
        _MODULES=load('numeric'),load('legacy_prefix')
    return _MODULES

def audit(model,s,t,log,source_limits,source_kind):
    n,_=modules();require(torch.equal(model['mu'],s['mu']) and torch.equal(model['scale'],s['scale']),'Model scales differ')
    theta=torch.cat([model['weight'],model['bias'][:,None]],1);a=n.audit(theta,s,t)
    it=log['total_updates'] if source_kind=='NR2' else log['iterations']
    oe=abs(a['objective']-log['objective']);ge=abs(a['max_gradient']-log['max_gradient'])
    require(log['accepted'] and oe<1e-10 and ge<1e-10,'Accepted source log not replayed')
    require(all(acceptance_gates(a['objective'],log['initial_objective'],a['max_gradient'],it,a['objective_replay_error'],a['gradient_replay_error']).values()),'Original precision gates')
    require(it<source_limits[0],'Strict source iteration boundary')
    if source_kind=='NR2':
        require(it==log['lbfgs_updates']+log['newton_updates'] and log['lbfgs_updates']<=1024 and log['newton_updates']<=32,'NR2 stage policy')
        if log['newton_updates']:require(log['lbfgs_updates']==1024,'NR2 Newton transition')
    else:
        require(log['solver']=='cholesky-original-gradient-aware-lbfgs-v4','Unexpected old solver')
        require(log['settings']['max_iter']==source_limits[0] and log['settings']['max_eval']==source_limits[1],'Source budget provenance')
        require(log['function_evaluations']<source_limits[1],'Adoption must precede source evaluation boundary')
    return dict(objective=a['objective'],gradient_inf=a['max_gradient'],objective_replay_error=oe,gradient_replay_error=ge,
                independent_gradient_vector_replay_error=a['gradient_replay_error'])

def source_log(e):
    if e['source_kind']=='NR2':
        p=ROOT/e['result_path'];checked(p,e['result_sha256'],'source-numeric-log');return read(p)
    p=(ROOT/e['path']).with_suffix('.json');return read(p)['optimizer']

def fit(s,t,context):
    n,l=modules();tag=context['role_id']+'/'+context['arm'];started=time.perf_counter();theta=None;ll=None;counter={}
    require(sha(OUT/'manifests/numeric-policy.json')==contract()['fixed'][rel(OUT/'manifests/numeric-policy.json')],'Sealed full numerical policy changed')
    log=dict(**context,solver=SOLVER,settings=POLICY,initialization='zero',device='cuda:0',dtype='float64',
             numeric_policy_sha256=sha(OUT/'manifests/numeric-policy.json'),accepted=False,newton_updates=0)
    fp=OUT/'failures'/context['role_id']/f"{context['arm']}-t{t:g}.json"
    try:
        theta,ll=l.run(s,t,tag);log.update(initial_objective=ll['initial_objective'],lbfgs_updates=ll['lbfgs_updates'])
        put(OUT/'phase-checkpoints'/context['role_id']/(context['arm']+'.pt'),dict(theta=theta.clone()),role_id=context['role_id'],policy_id=context['arm'])
        counter=dict(lbfgs_updates=ll['lbfgs_updates'],optimization_evaluations=ll['optimization_evaluations'])
        if ll['max_gradient']>1e-5:theta,log=n.refine(theta,s,t,32,log,counter,tag)
        aa=n.audit(theta,s,t);updates=ll['lbfgs_updates']+log['newton_updates']
        gates=acceptance_gates(aa['objective'],ll['initial_objective'],aa['max_gradient'],updates,aa['objective_replay_error'],aa['gradient_replay_error'])
        require(all(gates.values()),'Original NR2 precision or budget gates failed')
        log.update(**aa,total_updates=updates,iterations=updates,counters=counter,function_evaluations=counter['optimization_evaluations'],
                   gates=gates,accepted=True,seconds=time.perf_counter()-started,cuda_peak_MiB=torch.cuda.max_memory_allocated()/1048576)
        write(OUT/'fit-logs'/context['role_id']/f"{context['arm']}-t{t:g}.json",log)
        return dict(weight=theta[:,:96].detach(),bias=theta[:,96].detach(),mu=s['mu'],scale=s['scale']),log
    except BaseException as exc:
        log.update(accepted=False,exception_type=type(exc).__name__,exception=str(exc),seconds=time.perf_counter()-started,counters=counter)
        if theta is None:
            tb=exc.__traceback__
            while tb:
                loc=tb.tb_frame.f_locals
                if 'v' in loc and 'l' in loc and isinstance(loc.get('v'),torch.Tensor):
                    try:theta=l.backend().decode(loc['v'].detach(),loc['l']).detach()
                    except Exception:pass
                tb=tb.tb_next
        write(fp,log)
        put(fp.with_suffix('.pt'),dict(last_original_parameters=theta,slot_sha256=context['input_sha256'],
             phase_log=ll),failed=True)
        raise
