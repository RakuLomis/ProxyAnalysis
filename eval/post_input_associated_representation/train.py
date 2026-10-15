"""Fixed-budget full-batch CE plus optional associated target."""
from common import *
from models import Heads,pad,finite

def fit_batch(jobs,steps=1000,publish=True):
    start=time.perf_counter();ss=[];ms=[];ts=[]
    for r,arm,lam,seed in jobs:
        reader=cfg_arm(arm,lam)
        s=own(taskpath(r)/'classification.pt','branch',reader);m=own(OUT/'base-models'/r['id']/'P-small.pt','branch',reader)
        ss.append(s);ms.append(m)
        # No target reads at zero lambda, even when reused as A2/A3.
        if lam:ts.append(own(OUT/'targets'/r['id']/(arm+'.pt'),'branch',arm)['target'])
        else:ts.append(torch.zeros((len(s['real_x']),8),device=device(),dtype=torch.float32))
    x=pad([s['x'].float() for s in ss]);y=pad([s['y'] for s in ss]);mass=pad([s['mass'] for s in ss])
    z0=pad([base_logits(m,s['x']) for m,s in zip(ms,ss)])
    real=pad([s['real_x'].float() for s in ss]);rmass=pad([s['real_mass'].float() for s in ss]);target=pad(ts)
    lam=tensor([j[2] for j in jobs],torch.float32);net=Heads([j[3] for j in jobs]);opt=torch.optim.Adam(net.parameters(),lr=.001,weight_decay=0)
    have_target=any(j[2]>0 for j in jobs)
    # Verify zero initialization in original float64 source coordinates before any update.
    require(torch.equal(net(x,z0),z0),'Zero residual logits not exactly base')
    initial=[net.snapshot(i) for i in range(len(jobs))];trace=[]
    for step in range(steps):
        opt.zero_grad(set_to_none=True);z=net(x,z0)
        ce=(F.cross_entropy(z.flatten(0,1),y.flatten(),reduction='none').reshape_as(y)*mass).sum(1)
        if have_target:mse=((net.latent(real)-target).square().mean(-1)*rmass).sum(1)
        else:mse=torch.zeros_like(lam)
        reg=net.regularizer();j=ce+lam*mse+reg;j.sum().backward();net.clip();opt.step()
        if (step+1)%100==0:
            require(finite(net) and bool(torch.isfinite(j).all()),'Nonfinite residual training')
            trace.append(dict(step=step+1,CE=ce.detach().cpu().tolist(),MSE=mse.detach().cpu().tolist(),regularizer=reg.detach().cpu().tolist(),objective=j.detach().cpu().tolist()))
            budget()
    torch.cuda.synchronize();elapsed=time.perf_counter()-start;result=[]
    for i,(r,arm,lv,seed) in enumerate(jobs):
        state=net.snapshot(i);result.append(state)
        if publish:
            dest=OUT/('inner-models' if r['inner'] is not None else 'models')/r['id']/tag(arm,lv,seed)
            put(initial[i],dest/'initial.pt',zero_head=True,steps=0)
            put(dict(state=state,base_path=rel(OUT/'base-models'/r['id']/'P-small.pt')),
                dest/'terminal.pt',role_id=r['id'],arm=arm,lambda_value=lv,seed=seed,steps=steps,
                parameters=2318,device='cuda:0',dtype='float32',base_frozen=True)
            write(dest/'training.json',dict(role_id=r['id'],arm=arm,lambda_value=lv,seed=seed,steps=steps,
                  batch_seconds=elapsed,independent_heads=len(jobs),trace=[{k:(v[i] if isinstance(v,list) else v) for k,v in row.items()} for row in trace]))
    if publish:ledger(residual_fits=len(jobs))
    return result,trace,elapsed
