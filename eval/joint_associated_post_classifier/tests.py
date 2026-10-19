"""Finite differences, gradient routing, Adam/freeze and parallel prefix qualification."""
from common import *
from data import TrainingPool,pilot_roles
from models import initial,forward_post,loss_one,loss_independent
from train import Engine

def core_tests(pool):
    rows=[];r=pilot_roles()[0];recipe=RECIPES[2];d=pool.get(r,'JP',recipe['lam']);s=initial(d,SOURCE_SEED)
    def check(name,ok,**values):
        require(ok,name);rows.append(dict(test=name,passed=True,**values))
    z,g=forward_post(d['x'],s);base=d['x']@d['W'].T+d['c']
    init=float((z.softmax(1)-base.softmax(1)).abs().max())
    check('initial-base-probabilities',init<1e-12,absolute_error=init)
    p={k:v.detach().clone().requires_grad_() for k,v in s.items()}
    value,parts=loss_one(p,d,recipe);ind,grads=loss_independent(p,d,recipe)
    ad=torch.autograd.grad(value,[p[k] for k in HKEYS],retain_graph=True)
    ge=max(float((a-grads[k]).abs().max()) for a,k in zip(ad,HKEYS))
    oe=abs(float(value)-float(ind));check('independent-objective',oe<1e-10,absolute_error=oe)
    check('independent-head-gradient',ge<1e-10,absolute_error=ge)
    cegrad=torch.autograd.grad(parts[0],[p[k] for k in GKEYS],retain_graph=True)
    check('zero-V-first-CE-G-gradient',max(float(x.abs().max()) for x in cegrad)==0.)
    check('teacher-target-detached',not d['target'].requires_grad)
    biasgrads=torch.autograd.grad(parts[2],[p[k] for k in ['d0','d1','c']],allow_unused=True)
    check('bias-no-L2',all(v is None for v in biasgrads))
    j=dict(role=r,arm='JP',recipe=recipe,seed=SOURCE_SEED)
    en=Engine([d],[j],'independent');en.advance(1)
    pp=en.net.state_head(0);v,ps=loss_one(pp,d,recipe)
    cg=torch.autograd.grad(ps[0],[pp[k] for k in GKEYS])
    size=max(float(x.abs().max()) for x in cg);check('CE-reaches-G-after-V-update',size>0,gradient_max=size)
    midpoint=en.checkpoint()
    frozen=Engine([d],[j],'independent',states=midpoint['parameters'],adam=midpoint['adam'],update_G=False,update_head=True)
    frozen.capture();frozen.advance(10)
    check('freeze-G-values',all(torch.equal(frozen.net.snapshot(0)[k],midpoint['parameters'][0][k]) for k in GKEYS))
    headf=Engine([d],[j],'independent',states=midpoint['parameters'],adam=midpoint['adam'],update_G=True,update_head=False)
    headf.capture();headf.advance(10)
    check('freeze-head-values',all(torch.equal(headf.net.snapshot(0)[k],midpoint['parameters'][0][k]) for k in HKEYS))
    check('Adam-age-inherited',frozen.steps==11 and all(float(frozen.adam_head(0)[k]['step'])==11 for k in HKEYS))
    check('frozen-Adam-values-retained',all(torch.equal(frozen.adam_head(0)[k][field],midpoint['adam'][0][k][field]) for k in GKEYS for field in ['step','exp_avg','exp_avg_sq']))
    # Smooth all-double fixture. Positive hidden bias keeps ReLU branches fixed.
    gen=torch.Generator(device='cuda').manual_seed(20261016)
    x=torch.randn((7,4),device='cuda',dtype=torch.float64,generator=gen)*.01
    a=torch.randn((3,4),device='cuda',dtype=torch.float64,generator=gen)*.1
    p0=torch.cat([a.flatten(),torch.ones(3,device='cuda',dtype=torch.float64),
          torch.randn((2*3+2+3*4+3*2+3,),device='cuda',dtype=torch.float64,generator=gen)*.1]).requires_grad_()
    y=torch.tensor([0,1,2,0,1,2,0],device='cuda');mass=torch.ones(7,device='cuda',dtype=torch.float64)/7
    target=torch.randn((7,2),device='cuda',dtype=torch.float64,generator=gen)
    def objective(v):
        a=v[:12].reshape(3,4);b=v[12:15];h=F.relu(x@a.T+b)
        a1=v[15:21].reshape(2,3);b1=v[21:23];g=h@a1.T+b1
        w=v[23:35].reshape(3,4);vg=v[35:41].reshape(3,2);bias=v[41:44]
        logits=x@w.T+g@vg.T+bias
        return (mass*F.cross_entropy(logits,y,reduction='none')).sum()+.1*((g-target).square().mean(1)*mass).sum()+.001*(a.square().sum()+a1.square().sum()+w.square().sum()+vg.square().sum())
    direction=torch.randn(p0.shape,device='cuda',dtype=torch.float64,generator=gen);direction/=direction.norm()
    ag=torch.autograd.grad(objective(p0),p0)[0]@direction
    for h in [1e-4,1e-5]:
        fd=(objective(p0.detach()+h*direction)-objective(p0.detach()-h*direction))/(2*h)
        ae=abs(float(fd-ag));check('synthetic-difference-'+str(h),ae<=1e-8+1e-6*abs(float(ag)),absolute_error=ae)
    # Permitted route has no query/label/native reader, and zero lambda reads no target asset.
    old=len(READS);pool.get(pilot_roles()[1],'JC',0.)
    check('zero-lambda-no-target-reads',not any(v['kind'].startswith('target') for v in READS[old:]))
    return rows

def compare(reference,candidate):
    rows=[];passed=True
    for k in KEYS:
        a,b=reference['parameters'][0][k],candidate['parameters'][k]
        atol,rtol=(1e-5,1e-4) if a.dtype==torch.float32 else (1e-9,1e-8)
        err=float((a-b).abs().max());ok=bool(torch.allclose(a,b,atol=atol,rtol=rtol))
        rows.append(dict(field=k,absolute_error=err,atol=atol,rtol=rtol,passed=ok));passed &=ok
        for name in ['step','exp_avg','exp_avg_sq']:
            a=reference['adam'][0][k][name];b=candidate['adam'][k][name]
            # Moment arrays use their parameter's frozen precision policy.
            ok=bool(torch.equal(a,b)) if name=='step' else bool(torch.allclose(a,b,atol=atol,rtol=rtol))
            rows.append(dict(field=k+'.'+name,absolute_error=float((a-b).abs().max()),atol=atol,rtol=rtol,passed=ok));passed &=ok
    return passed,rows

def qualify(pool,root):
    rs=pilot_roles();out=[];status={}
    for backend in ['independent','tensorized','streams']:
        allpass=True;started=time.perf_counter()
        for lr,gamma in [(.001,.001),(.0003,.0001)]:
            jobs=[dict(role=rs[i*3],arm='JC' if lam==0 else 'JP',recipe=dict(lam=lam,lr=lr,gamma=gamma),seed=SOURCE_SEED+i) for i,lam in enumerate([0.,.1,1.])]
            data=[pool.get(j['role'],j['arm'],j['recipe']['lam']) for j in jobs]
            reference=[Engine([d],[j],'independent') for d,j in zip(data,jobs)]
            batch=Engine(data,jobs,backend);batch.capture()
            for step in [1,10,100]:
                for e in reference:e.advance(step-e.steps)
                batch.advance(step-batch.steps)
                for i,e in enumerate(reference):
                    ok,rows=compare(e.checkpoint(),dict(parameters=batch.net.snapshot(i),adam=batch.adam_head(i)))
                    allpass &=ok
                    out.extend(dict(backend=backend,lr=lr,head=i,prefix=step,**r) for r in rows)
            del batch,reference;torch.cuda.empty_cache()
        status[backend]=dict(passed=allpass,seconds=time.perf_counter()-started)
        immutable(root/(backend+'-prefix.json'),dict(passed=allpass,rows=[v for v in out if v['backend']==backend]))
        progress('P1_backend_prefix',backend=backend,passed=allpass)
    immutable(root/'qualification.json',status)
    require(status['independent']['passed'],'Safe independent CUDA graph did not qualify')
    return status

def tests(tag):
    with engineering(tag) as root:
        pool=TrainingPool();rows=core_tests(pool);immutable(root/'core-tests.json',dict(passed=True,rows=rows))
        q=qualify(pool,root)
        entry=dict(tag=tag,qualification=rel(root/'qualification.json'),
              code_sha256={rel(p):sha(p) for p in CODE.glob('*.py')},passed=True,backends=q)
        immutable(root/'registered-qualification.json',entry)
        index=OUT/'engineering/qualification-index.json';history=read(index)['history'] if index.exists() else []
        write(index,dict(history=history+[entry],latest_tag=tag))
        progress('P1_core_tests_complete',tests=len(rows),backends=q)
