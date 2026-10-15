"""Pre-only supervised teacher, then trusted target builder."""
from common import *
from models import Heads,latent,pad,finite

def fit_batch(rs,steps=1000,publish=True):
    start=time.perf_counter();data=[own(taskpath(r)/'teacher/fit.pt','teacher') for r in rs]
    x=pad([d['x'].float() for d in data]);y=pad([d['y'] for d in data]);mass=pad([d['mass'].float() for d in data])
    net=Heads([20261014]*len(rs),teacher=True);opt=torch.optim.Adam(net.parameters(),lr=.001,weight_decay=0)
    trace=[]
    for step in range(steps):
        opt.zero_grad(set_to_none=True);z=net(x)
        ce=(F.cross_entropy(z.flatten(0,1),y.flatten(),reduction='none').reshape_as(y)*mass).sum(1)
        j=ce+net.regularizer();j.sum().backward();opt.step()
        if (step+1)%100==0:
            require(finite(net) and bool(torch.isfinite(j).all()),'Nonfinite teacher')
            trace.append(dict(step=step+1,CE=ce.detach().cpu().tolist(),objective=j.detach().cpu().tolist()))
            budget()
    torch.cuda.synchronize();elapsed=time.perf_counter()-start;result=[]
    for i,r in enumerate(rs):
        state=net.snapshot(i);d=data[i];raw=latent(state,d['x']).double()
        mu=(raw*d['mass'][:,None]).sum(0);sd=torch.sqrt(((raw-mu).square()*d['mass'][:,None]).sum(0))
        require(bool((sd>=1e-8).any()),'All teacher bottleneck coordinates constant; candidate pause')
        scale=torch.where(sd>=1e-8,sd,torch.ones_like(sd));z=(raw-mu)/scale
        record=dict(state=state,mu=mu,scale=scale,raw_sd=sd)
        sing=torch.linalg.svdvals((raw-mu)*d['mass'].sqrt()[:,None]);energy=sing.square();ratio=energy/energy.sum().clamp_min(1e-30)
        diag=dict(role_id=r['id'],steps=steps,parameters=sum(v.numel() for v in state.values()),
                  sd=sd.cpu().tolist(),effective_rank=float(torch.exp(-(ratio*ratio.clamp_min(1e-30).log()).sum())),
                  training_accuracy=float((net(x)[i,:len(raw)].argmax(1)==d['y']).double().mean()),
                  device='cuda:0',dtype='float32',seconds_batch=elapsed)
        result.append((record,z,diag))
        if publish:
            put(record,OUT/'teachers'/r['id']/'teacher.pt',role_id=r['id'],steps=steps,parameters=1742)
            write(OUT/'teachers'/r['id']/'diagnostics.json',diag)
            # Target builder is trusted; group branch receives only means, never individual targets.
            group=own(taskpath(r)/'trusted/groups.pt','target-builder')['group'];K=int(group.max())+1
            sums=torch.zeros((K,8),device=device(),dtype=torch.float64);sums.index_add_(0,group,z)
            count=torch.bincount(group,minlength=K).double();require(bool((count==4).all()),'Group targets four repetitions')
            g=(sums/count[:,None])[group]
            put(dict(target=z.float()),OUT/'targets'/r['id']/'A3.pt',role_id=r['id'],kind='true-associated-target')
            put(dict(target=g.float()),OUT/'targets'/r['id']/'A2.pt',role_id=r['id'],kind='anonymous-group-center',four_repeat_mean=True)
    if publish:ledger(teachers=len(rs))
    return result,trace,elapsed
