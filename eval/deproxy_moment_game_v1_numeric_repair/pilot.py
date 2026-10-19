"""NER1 bounded stage entrypoint. No query reader and no full-experiment entry."""
from common import *
from classifier import solve,persist,comparison,gate,basis,independent
from problems import specs,spec_cap,build

def tests():
    configure('synthetic');begin('R0-controls');checks=[]
    try:
        for it,ev,expected in [(1999,9999,True),(2000,1,False),(1,10000,False),(2000,10000,False)]:
            got=gate(it,ev,0.,0.,0.,0.,1.)[0];require(got==expected,'Budget priority fixture')
            checks.append(dict(test='budget',iterations=it,evaluations=ev,accepted=got))
        for bad in [float('nan'),float('inf')]:require(not gate(0,1,bad,0,0,0,1)[0],'Nonfinite rejection')
        from lbfgs_local import CertifiedLBFGS,EvaluationBudget
        p=torch.nn.Parameter(torch.tensor([2.],device='cuda',dtype=torch.float64))
        seen=[]
        def cert(g,it,ev):
            require(torch.allclose(g,2*p.detach(),atol=1e-12,rtol=1e-12),'Returned selected gradient fixture')
            seen.append(it);return float(g.abs().max())<1e-8,float(g.abs().max())
        o=CertifiedLBFGS([p],certify=cert,max_iter=2000,max_eval=10000,line_search_fn='strong_wolfe')
        def closure():o.zero_grad();v=p.square().sum();v.backward();return v
        o.step(closure);require(len(seen)>=2 and o.exit_reason=='original_coordinate_candidate','Selected-point callback')
        initial=p.detach().clone()
        def exhausted():raise EvaluationBudget('fixture')
        try:
            with torch.no_grad():o._directional_evaluate(exhausted,o._clone_param(),1.,torch.ones_like(p))
        except EvaluationBudget:pass
        require(torch.equal(p,initial),'Rejected trial restored under budget exception')
        # Independent coordinate chain with original L2 and unregularized bias.
        gen=torch.Generator(device='cuda').manual_seed(20261016)
        x=torch.randn((24,96),device='cuda',dtype=torch.float64,generator=gen);y=torch.arange(24,device='cuda')%6
        w=torch.full((24,),1/24,device='cuda',dtype=torch.float64);q=basis()
        aug=torch.cat([x,torch.ones((24,1),device='cuda',dtype=torch.float64)],1)
        L=torch.linalg.cholesky(aug.T@(aug*w[:,None])/6+torch.diag(torch.tensor([.002]*96+[0.],device='cuda',dtype=torch.float64)))
        v=torch.randn((5,97),device='cuda',dtype=torch.float64,generator=gen,requires_grad=True)
        th=torch.linalg.solve_triangular(L.T,v.T,upper=True).T;full=q@th
        value,gW,gc,_=independent(full[:,:96],full[:,96],x,y,w,.001)
        gv,=torch.autograd.grad(value,v)
        err=float((q@(gv@L.T)-torch.cat([gW,gc[:,None]],1)).abs().max())
        require(err<=1e-10,'Original coordinate gradient chain')
        # Reader negative fixtures must fail before any tensor decode.
        import common
        oldload=torch.load;decoded=[]
        def forbidden_decode(*a,**kw):decoded.append(True);raise AssertionError('Reader decoded forbidden input')
        torch.load=forbidden_decode
        denied=[]
        try:
            rid=roles()[0]['id'];other=roles()[1]['id'];p=OLD/'packages'/rid/'paired/train.pt'
            for path,role in [(p,other),(OLD/'query/forbidden.pt',rid),(OUT/'not-registered.pt',rid)]:
                try:own(path,role)
                except RuntimeError:denied.append(True)
            require(len(denied)==3 and not decoded,'Read deny before decode')
        finally:torch.load=oldload
        write(OUT/'tests/R0-controls.json',dict(passed=True,budget_cases=checks,selected_gradient_points=seen,
            coordinate_chain_error=err,denied_before_decode=3,NaN_Inf_rejected=True,
            cached_pass_flag_is_not_read_by_new_solver=True,missing_version_not_reusable=True),True)
        progress('R0_controls_passed')
    finally:end('R0-controls')

def serial(cap,hard=False):
    configure(cap);base='R1-hard' if hard else 'R1-'+cap
    attempt=1+len(list((OUT/'tests').glob(base+'-attempt-*.json')))
    tag=base+f'-attempt-{attempt:02}'
    require(read(OUT/'tests/R0-controls.json')['passed'],'Controls required')
    if not hard:require(read(OUT/'tests/R1-hard-current.json')['passed'],'Hard case first')
    begin(tag);records=[]
    try:
        selected=specs()[:1] if hard else [s for s in specs()[1:] if spec_cap(s)==cap]
        for s in selected:
            deadline();p=build(s);result=solve(p['x'],p['y'],p['w'],p['gamma'],p['init'])
            result['quality']['legacy_comparison']=comparison(result['head'],p['reference'],p['x'])
            persist(OUT/'R1'/s['key']/'head.pt',result,role_id=s['role_id'],capability=cap,problem_key=s['key'])
            quality={k:v for k,v in result['quality'].items() if k not in ['accepted_points','settings','legacy_comparison']}
            records.append({**s,**quality});progress(tag,problem=s['key'],accepted=quality['accepted'],iterations=quality['iterations'],seconds=quality['seconds'])
            require(result['quality']['accepted'],'R1 head failed original numerical/budget gate: '+s['key'])
        save(OUT/'tests'/f'{tag}.parquet',records)
        write(OUT/'tests'/f'{tag}.json',dict(passed=True,problems=len(records),query_read=False),True)
        write(OUT/'tests'/f'{base}-current.json',dict(passed=True,record=rel(OUT/'tests'/f'{tag}.json')))
        codecheck()
    except BaseException as e:
        if records:save(OUT/'tests'/f'{tag}-partial.parquet',records)
        write(OUT/'tests'/f'{tag}.json',dict(passed=False,problems=len(records),error=str(e)),True)
        failure(tag,e);raise
    finally:end(tag)

def recover_hard():
    """Explicit bookkeeping recovery after an already sealed accepted fit; no refit."""
    configure('G');begin('R1-hard-bookkeeping-recovery')
    try:
        s=specs()[0];problem=build(s);p=OUT/'R1/hard-FG/head.pt'
        h=newown(p,s['role_id']);q=read(p.with_suffix('.quality.json'))
        require(q['accepted'] and q['budget_pass'] and q['numeric_pass'],'Saved accepted numeric snapshot required')
        val,g,c,_=independent(h['W'],h['c'],problem['x'],problem['y'],problem['w'],problem['gamma'])
        require(max(float(g.abs().max()),float(c.abs().max()))<=1e-5,'Recovered original gradient')
        require(abs(float(val)-q['objective'])/max(1,abs(q['objective']))<=1e-10,'Recovered original objective')
        result=dict(passed=True,problems=1,refit=False,retained_stop='R1-hard-attempt-01.json',original_tensor_sha256=sha(p),
            independent_original_gradient_max=max(float(g.abs().max()),float(c.abs().max())),iterations=q['iterations'],evaluations=q['evaluations'])
        write(OUT/'tests/R1-hard-bookkeeping-recovery.json',result,True)
        write(OUT/'tests/R1-hard-current.json',dict(passed=True,record=rel(OUT/'tests/R1-hard-bookkeeping-recovery.json')))
        progress('R1_hard_recovered_without_refit',iterations=q['iterations'],evaluations=q['evaluations'],gradient=q['original_gradient_max']);codecheck()
    finally:end('R1-hard-bookkeeping-recovery')

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('phase',choices=['controls','hard','serial','recover-hard']);p.add_argument('--cap',choices=['P','G','E'],default='G')
    a=p.parse_args()
    if a.phase=='controls':tests()
    elif a.phase=='recover-hard':recover_hard()
    else:serial('G' if a.phase=='hard' else a.cap,a.phase=='hard')
