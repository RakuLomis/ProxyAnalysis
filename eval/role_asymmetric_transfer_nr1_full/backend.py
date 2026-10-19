"""Compile original arithmetic into isolated NR1 runtime bindings."""
from common import *
import common as C

def load():
    source=OLD_CODE/'solver_v4.py';tree=ast.parse(source.read_text())
    tree.body=[n for n in tree.body if not (isinstance(n,ast.ImportFrom) and n.module=='common')];ast.fix_missing_locations(tree)
    m=types.ModuleType('ra1_full_nr1_backend');m.__dict__.update({k:v for k,v in vars(C).items() if not k.startswith('_')})
    exec(compile(tree,str(source),'exec'),m.__dict__)
    raw=m.transformed_objective
    def objective(*a,**kw):budget_check();return raw(*a,**kw)
    m.transformed_objective=objective
    return m

def audit(model,s,t,log,source_limits,adopting=False):
    require(torch.equal(model['mu'],s['mu']) and torch.equal(model['scale'],s['scale']),'Frozen model scale mismatch')
    z=s['x']@model['weight'].T+model['bias'];error=(z.softmax(1)-F.one_hot(s['y'],6))*s['mass'][:,None]
    val=(s['mass']*(z.logsumexp(1)-z.gather(1,s['y'][:,None]).squeeze(1))).sum()+.0005*(1+t)*model['weight'].square().sum()
    gw=error.T@s['x']+.001*(1+t)*model['weight'];gb=error.sum(0);g=max(float(gw.abs().max()),float(gb.abs().max()))
    oe=abs(float(val)-log['objective']);ge=abs(g-log['max_gradient'])
    require(log['solver']==SOLVER and log['accepted'] and g<=1e-5 and oe<1e-10 and ge<1e-10,'Independent accepted endpoint audit')
    require(log['settings']['max_iter']==source_limits[0] and log['settings']['max_eval']==source_limits[1],'Source numeric policy provenance')
    require(log['iterations']<source_limits[0],'Original strict iteration acceptance')
    if adopting:require(log['function_evaluations']<source_limits[1],'Adoption must precede source evaluation boundary')
    require(all(acceptance_gates(float(val),log['initial_objective'],g,log['iterations'],log['objective_replay_error'],log['gradient_replay_error']).values()),'Original precision gates')
    return dict(objective=float(val),gradient_inf=g,objective_replay_error=oe,gradient_replay_error=ge)
