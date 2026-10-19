"""N1 no-fit equivalence, boundary and derivative checks."""
from common import *
from backend_loader import load,policy

def run():
    with phase('N1'):
        c=contract();rows=[]
        for old in [True,False]:
            b=load(OUT/'backend-checks'/('old' if old else 'NR1'),old)
            bound=2000 if old else 4000;ebound=10000 if old else 20000
            require(b.SETTINGS['max_iter']==bound and b.SETTINGS['max_eval']==ebound,'Policy namespace')
            for n in [1999,2000,3999,4000]:
                expected='iteration_budget' if n>=bound else 'original_gradient_candidate'
                require(b.stop_action(1e-6,iterations=n)==expected,'Iteration boundary')
            for n in [9999,10000,19999,20000]:
                expected='evaluation_budget' if n>=ebound else 'original_gradient_candidate'
                require(b.stop_action(1e-6,evaluations=n)==expected,'Evaluation boundary')
            require(not b.gates(1.,2.,1.0001e-5,1,0.,0.)['original_coordinate_gradient'],'Gradient threshold unchanged')
            require(not b.gates(1.,2.,1e-6,1,1e-10,0.)['objective_replay'],'Strict objective error')
            require(not b.gates(1.,2.,1e-6,1,0.,1e-10)['gradient_replay'],'Strict gradient error')
            require(b.stop_action(1.,finite=False)=='nonfinite_failure','Nonfinite safety')
            require(b.stop_action(1.,gtd=0.)=='non_descent_failure','Direction safety')
            require(b.stop_action(1.,unchanged=3)=='unchanged_parameter_failure','Stagnation safety')
            rows.append(dict(policy='old' if old else 'NR1',max_iter=bound,max_eval=ebound,passed=True))
        # No source function arithmetic rewrite: remove only common import.
        tree=ast.parse((OLD_CODE/'solver_v4.py').read_text());fn=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))]
        functions={n.name:hashlib.sha256(ast.dump(n).encode()).hexdigest() for n in fn}
        torch.manual_seed(20261018);x=torch.randn(36,96,device=device(),dtype=torch.float64);y=torch.arange(36,device=device())%6;mass=torch.full((36,),1/36,device=device(),dtype=torch.float64)
        b=load(OUT/'backend-checks/NR1',False);_,l,ax=b.coordinates(x,mass,4.)
        v=(torch.randn(6,97,device=device(),dtype=torch.float64)*.01).requires_grad_()
        objective=b.transformed_objective(v,l,ax,y,mass,4.);gv=torch.autograd.grad(objective,v)[0]
        theta=b.decode(v.detach(),l);s=dict(x=x,y=y,mass=mass)
        value,g=independent(s,theta,4.)
        ve=abs(float(objective)-value);ge=float((gv@l.T-g).abs().max())
        require(ve<1e-10 and ge<1e-10,'Coordinate objective/gradient equality')
        # Bias has no L2; shifting all classes by a constant preserves CE.
        shifted=theta.clone();shifted[:,96]+=3.;sv,sg=independent(s,shifted,4.)
        require(abs(sv-value)<1e-12,'Bias regularization changed')
        write(OUT/'audits/N1.json',dict(passed=True,policies=rows,algorithm_function_AST_sha256=functions,
            backend_changes=['isolated policy and IO binding','activity checks before objective','read-only accepted-point n2000 clone'],
            objective_error=ve,gradient_chain_error=ge,new_LR_fits=0,H_U_reads=0))
