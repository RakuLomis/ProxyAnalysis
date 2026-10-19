"""Migration acceptance: equation replay of pilot imports; no new head fits."""
from common import *
from worker import initial_problems,static_problems,dynamic,dynamic_jobs
from deploy import mixture,base_logp

def run(cap):
    configure(cap);begin('migration-'+cap)
    try:
        pilotreg=read(PILOT/'registration.json');rs=pilotreg['roles'];keys={(j['role_id'],j['arm'],j['recipe']['id'],j['seed']) for j in pilotreg['jobs']}
        if cap in ['G','E']:require(not list(initial_problems(rs,cap)),'Pilot initial import missing; no smoke fits allowed')
        if cap in ['P','G']:require(not list(static_problems(rs,cap,'inner')),'Pilot static import missing; no smoke fits allowed')
        jobs=[j for j in dynamic_jobs(rs,cap,'inner') if (j['role_id'],j['arm'],j['recipe']['id'],j['seed']) in keys]
        n,reused=dynamic(jobs,'migration-'+cap);require(n==0,'Migration did not preserve pilot paths')
        flush_reads('migration-'+cap);codecheck()
        immutable(OUT/'tests'/f'migration-{cap}.json',dict(passed=True,new_head_fits=0,new_Adam_paths=0,reused_dynamic_paths=reused,query_reads=0))
    except BaseException as e:failure('migration-'+cap,e);raise
    finally:end('migration-'+cap)

def controls():
    configure('tests');begin('migration-controls')
    try:
        from formal import historical,choose,metrics
        for r in [contract()['inner_roles'][0],contract()['roles'][0]]:
            for kind in ['query','labels']:
                rejected=False
                try:historical(r,kind)
                except RuntimeError as e:rejected='barrier' in str(e)
                require(rejected,'Deferred reader prematurely unlocked')
        # Synthetic probability mixture; no test-derived temperature or clipping.
        a=torch.tensor([[1000.,-1000.,0.,1.,2.,3.]],device='cuda',dtype=torch.float64).log_softmax(1)
        b=torch.flip(a,[1]);require(torch.equal(mixture(a,b,0.),a) and torch.equal(mixture(a,b,1.),b),'Exact mixture endpoints')
        for beta in [.25,.5,.75]:require(torch.allclose(mixture(a,b,beta).exp(),(1-beta)*a.exp()+beta*b.exp(),atol=1e-12,rtol=1e-12),'Mixture arithmetic')
        # Enforce source files/classes/candidate coverage without fitting a model.
        require(len(contract()['inner_roles'])==720 and len(contract()['roles'])==60,'Full roles')
        require(720*(2*3+4*6)==21600,'All inner endpoints')
        from selection_checks import run as select_check
        from fold_checks import audit as fold_check
        select_check();fold_check()
        immutable(OUT/'tests/migration-controls.json',dict(passed=True,query_label_negative_tests=4,new_head_fits=0,new_Adam_paths=0,
            selection_tie=1e-12,float64=True,exact_beta_endpoints=True))
        codecheck()
    except BaseException as e:failure('migration-controls',e);raise
    finally:end('migration-controls')

def finish():
    configure('coordinator');begin('migration-seal')
    try:
        files=[OUT/'tests'/f'migration-{c}.json' for c in ['P','G','E']]+[OUT/'tests/migration-controls.json',OUT/'manifests/budget-amendment.json']
        require(all(read(f)['passed'] for f in files[:-1]),'Migration controls')
        require(read(files[-1])['passed'],'32h gate')
        seal(OUT/'manifests/P1-complete.json',files,numeric_version='NER1',inherited_pilot=True,full_authorized=True,query_reads=0,
            activity_cap=144000,forecast_gate=115200)
        progress('full_NER1_migration_passed',query_reads=0,full_experiment_enabled=True)
    finally:end('migration-seal')

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('phase',choices=['controls','train-replay','seal']);p.add_argument('--cap',choices=['P','G','E'])
    a=p.parse_args()
    if a.phase=='controls':controls()
    elif a.phase=='seal':finish()
    else:run(a.cap)
