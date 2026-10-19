"""Trusted, training-pre-only 1000-step teacher builder. No learner sees pre."""
from common import *

def latent(s,x):return F.linear(F.relu(F.linear(x.float(),s['w0'],s['b0'])),s['w1'],s['b1'])

def fit_teachers(rs):
    from workflow import remaining,debit,codecheck
    pending=[]
    for r in rs:
        p=OUT/'teachers'/r['id']/'teacher.pt'
        if p.exists():
            for q in [p,OUT/'targets'/r['id']/'A2.pt',OUT/'targets'/r['id']/'A3.pt']:own(q)
        else:pending.append(r)
    if not pending:return
    require(len(pending)<=32 and all(r['inner'] is None for r in pending),'Only up to 32 registered outer teachers')
    codecheck();remaining();data=[asset(PARENT/'packages'/r['id']/'teacher/fit.pt',r['id'],'teacher-fit') for r in pending]
    groups=[asset(PARENT/'packages'/r['id']/'trusted/groups.pt',r['id'],'groups')['group'] for r in pending]
    states=[];opts=[];streams=[torch.cuda.Stream() for _ in range(min(8,len(pending)))]
    for d in data:
        require(set(d)=={'x','y','mass'} and d['x'].shape==(352,96),'Pure teacher training schema')
        require(abs(float(d['mass'].sum())-1)<1e-12,'Teacher weight sum')
        s={}
        for j,(ni,no) in enumerate([(96,16),(16,8),(8,6)]):
            gen=torch.Generator(device='cuda').manual_seed(SOURCE_SEED+j*100003)
            w=torch.empty((no,ni),device='cuda',dtype=torch.float32).uniform_(-ni**-.5,ni**-.5,generator=gen)
            b=torch.empty(no,device='cuda',dtype=torch.float32).uniform_(-ni**-.5,ni**-.5,generator=gen)
            s['w'+str(j)]=torch.nn.Parameter(w);s['b'+str(j)]=torch.nn.Parameter(b)
        opt=torch.optim.Adam(s.values(),lr=.001,weight_decay=0,foreach=False,capturable=True)
        for p in s.values():
            p.grad=torch.zeros_like(p);opt.state[p]=dict(step=torch.zeros((),device='cuda'),exp_avg=torch.zeros_like(p),exp_avg_sq=torch.zeros_like(p))
        states.append(s);opts.append(opt)
    xf=[d['x'].float() for d in data];mass=[d['mass'].float() for d in data];bad=torch.zeros(len(data),device='cuda',dtype=torch.bool)
    def step():
        root=torch.cuda.current_stream()
        for stream in streams:stream.wait_stream(root)
        for i,(s,opt,d) in enumerate(zip(states,opts,data)):
            with torch.cuda.stream(streams[i%len(streams)]):
                opt.zero_grad(set_to_none=False);z=F.linear(latent(s,xf[i]),s['w2'],s['b2'])
                ce=(F.cross_entropy(z,d['y'],reduction='none')*mass[i]).sum()
                obj=ce+.01*sum(s['w'+str(j)].square().sum() for j in range(3));obj.backward();opt.step()
                bad[i].logical_or_(~torch.isfinite(obj))
        for stream in streams:root.wait_stream(stream)
    def snapshot():return [dict(state={k:p.detach().clone() for k,p in s.items()},adam={k:{n:v.clone() for n,v in opt.state[p].items()} for k,p in s.items()}) for s,opt in zip(states,opts)]
    init=snapshot()
    def reset():
        with torch.no_grad():
            for s,opt,old in zip(states,opts,init):
                for k,p in s.items():
                    p.copy_(old['state'][k]);p.grad.zero_()
                    for n,v in old['adam'][k].items():opt.state[p][n].copy_(v)
            bad.zero_()
    started=time.perf_counter();warm=torch.cuda.Stream();warm.wait_stream(torch.cuda.current_stream())
    with torch.cuda.stream(warm):
        for _ in range(3):step()
    torch.cuda.current_stream().wait_stream(warm);torch.cuda.synchronize();reset()
    graph=torch.cuda.CUDAGraph()
    with torch.cuda.graph(graph):step()
    torch.cuda.synchronize();reset()
    for i in range(1000):
        graph.replay()
        if (i+1)%100==0:require(not bool(bad.any()),'Nonfinite outer teacher; no automatic policy change')
    torch.cuda.synchronize();elapsed=time.perf_counter()-started
    debit(elapsed,len(pending),1000*len(pending),'outer-teacher',ids=[r['id'] for r in pending])
    for r,s,d,g in zip(pending,states,data,groups):
        with torch.no_grad():
            require(all(torch.isfinite(v).all() for v in s.values()),'Nonfinite teacher parameters')
            raw=latent(s,d['x']).double();mu=(raw*d['mass'][:,None]).sum(0)
            sd=(((raw-mu).square()*d['mass'][:,None]).sum(0)).sqrt();scale=torch.where(sd>=1e-8,sd,torch.ones_like(sd));z=(raw-mu)/scale
            enc=F.one_hot(g,int(g.max())+1).double();count=enc.sum(0);require(bool((count==4).all()),'Four-repeat target centers')
            centers=((enc.T@z)/count[:,None])[g]
            sv=torch.linalg.svdvals((raw-mu)*d['mass'].sqrt()[:,None]);pr=sv.square()/sv.square().sum().clamp_min(1e-30)
        put(OUT/'teachers'/r['id']/'teacher.pt',dict(state={k:v.detach().clone() for k,v in s.items()},mu=mu,scale=scale,raw_sd=sd),
            role_id=r['id'],steps=1000,seed=SOURCE_SEED,pre_only=True)
        put(OUT/'targets'/r['id']/'A3.pt',dict(target=z.float()),role_id=r['id'],kind='target-P')
        put(OUT/'targets'/r['id']/'A2.pt',dict(target=centers.float()),role_id=r['id'],kind='target-G',group_size=4)
        immutable(OUT/'teachers'/r['id']/'diagnostics.json',dict(sd=cpu(sd).tolist(),low_variance=int((sd<1e-8).sum()),
             effective_rank=float(torch.exp(-(pr*pr.clamp_min(1e-30).log()).sum())),seconds_batch=elapsed))
    progress('outer_teachers',completed=len(list((OUT/'teachers').rglob('teacher.pt'))),last_batch_seconds=elapsed)
