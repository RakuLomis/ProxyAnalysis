"""No fitted models: objective/gauge/Hessian, finite policies and negative tests."""
from common import *
import common as C
import numeric as N
from legacy_prefix import backend

def expect_error(fn):
    try:fn()
    except RuntimeError:return True
    raise RuntimeError('Expected negative test was not rejected')
def hvp_check(theta,s,t):
    u,k=N.encode(theta);h=N.hessian(theta,s,t);out=[]
    for kind in ['alternating','weight17','bias2']:
        d=torch.zeros(581,device=dev(),dtype=torch.float64)
        if kind=='alternating':d[::2]=1;d[1::2]=-1;d=d/d.norm()
        else:d[17 if kind=='weight17' else 578]=1
        _,ad=torch.autograd.functional.hvp(lambda z:N.value(N.decode(z,k),s,t),u,d)
        hh=h@d;err=float((hh-ad).norm()/ad.norm().clamp_min(1))
        require(err<=1e-10,'Analytical HVP mismatch')
        out.append(dict(direction=kind,relative_error=err,absolute_inf_error=float((hh-ad).abs().max())))
    return out
def run():
    guard();progress('P1_engineering')
    q=N.basis();x=torch.sin(torch.arange(18*96,device=dev(),dtype=torch.float64).reshape(18,96)/17)/3
    y=torch.arange(18,device=dev())%6
    m=1+torch.arange(18,device=dev(),dtype=torch.float64)%5
    m=m/(F.one_hot(y,6).double().T@m)[y]/6
    s=dict(x=x,y=y,mass=m)
    theta=torch.cos(torch.arange(582,device=dev(),dtype=torch.float64).reshape(6,97)/37)/10
    theta[:,:96]+=torch.linspace(.01,.03,96,device=dev(),dtype=torch.float64)[None,:];theta[:,96]+=.4
    u,k=N.encode(theta);dec=N.decode(u,k)
    require(torch.equal(theta[:,:96],dec[:,:96]),'W gauge changed')
    require(float((theta-dec).abs().max())<1e-12,'Bias gauge roundtrip')
    results=[]
    for t in [0.,.25,1.,4.]:
        aa=N.audit(theta,s,t)
        h=N.hessian(dec,s,t)
        ah=torch.autograd.functional.hessian(lambda z:N.value(N.decode(z,k),s,t),u,vectorize=True)
        err=float((h-ah).norm()/ah.norm().clamp_min(1));require(err<=1e-10,'Synthetic Hessian mismatch')
        require(abs(float(N.value(theta,s,t)-N.value(dec,s,t)))<1e-10,'Gauge objective')
        results.append(dict(t=t,hessian_relative_error=err,**aa))
    real=[]
    for e in C.CONTRACT['design']['snapshot_diagnostics']:
        f=read(checked(ROOT/e['failure_json'],'failure-metadata'))
        state=load((ROOT/e['failure_json']).with_suffix('.pt'),'failed-parameter-diagnostic')
        ss=load(ROOT/e['slot_path']);th=state['last_original_parameters']
        real.append(dict(id=e['id'],hvp=hvp_check(th,ss,f['t']),audit=N.audit(th,ss,f['t'])))
    eye=torch.eye(4,device=dev(),dtype=torch.float64);g=torch.ones(4,device=dev(),dtype=torch.float64)
    _,undamped=N.direction(eye,g);require(undamped['mu']==0,'Unexpected synthetic damping')
    _,damped=N.direction(eye*0,g);require(damped['mu']>0,'Singular finite system must follow damping ladder')
    neg={}
    neg['CPU_rejected']=expect_error(lambda:N.encode(torch.zeros(6,97,dtype=torch.float64)))
    neg['float32_rejected']=expect_error(lambda:N.encode(theta.float()))
    neg['nonfinite_rejected']=expect_error(lambda:N.direction(eye*float('nan'),g))
    neg['no_descent_rejected']=expect_error(lambda:N.direction(eye,torch.zeros_like(g)))
    counter=dict(optimization_evaluations=0)
    neg['line_search_failed']=expect_error(lambda:N.search(g,-g,1.,-4.,lambda a:torch.ones((),device=dev(),dtype=torch.float64),counter))
    require(counter['optimization_evaluations']==25,'Fixed line search candidate count')
    neg['evaluation_boundary_rejected']=expect_error(lambda:N.search(g,-g,1.,-4.,lambda a:a.sum(),dict(optimization_evaluations=20000)))
    neg['unregistered_H_read_rejected']=expect_error(lambda:checked(ROOT/'unregistered-H-query.parquet','query'))
    a=acceptance_gates(1.,2.,1e-5,3999,0.,0.);b=acceptance_gates(1.,2.,1e-5,4000,0.,0.)
    require(all(a.values()) and not b['iteration_budget'],'Original strict iteration gate')
    require(not acceptance_gates(1.,2.,1.00001e-5,100,0.,0.)['original_coordinate_gradient'],'Original gradient gate')
    backend_settings=backend().SETTINGS
    require(backend_settings['max_iter']==4000 and backend_settings['max_eval']==20000,'Legacy budgets changed')
    require(backend_settings['history_size']==100 and backend_settings['line_search_fn']=='strong_wolfe','Legacy algorithm settings')
    boundary=dict(total_updates3999=a,total_updates4000=b,phase_update_limit=1024,newton_update_limit=32,
                  snapshot_update_limit=8,newton_evaluation19999_available=19999<20000,newton_evaluation20000_available=20000<20000)
    write(OUT/'audits/engineering.json',dict(passed=True,synthetic=results,real_hvp=real,negative=neg,boundary=boundary,
          new_fits=0,mean_W_preserved=True,mean_bias_frozen=True,H_reads=0,backend_settings=backend_settings))
    write(OUT/'audits/backend-diff.json',dict(original_module_sha256=sha(LEGACY/'solver_v4.py'),
          original_objective_and_coordinates_reused=True,original_two_loop_and_wolfe_reused=True,
          added_phase_checkpoint=1024,Newton_module=rel(CODE/'numeric.py'),installed_torch_patched=False,
          original_precision_gates_unchanged=True,solver_algorithm_changed=True))
    progress('P1_passed',Hessian_checked=True,real_HVP_directions=6,new_fits=0)
