"""Uniform-lr CUDA Graph qualification; legacy states are read-only references."""
from common import *
from engine import Engine
from problems import load,initial_head,modelroot
from classifier import basis
from moment_features import grouping,moments
from models import KEYS

class BoundEngine(Engine):
    def __init__(self,data,jobs,heads,streams=True):
        require(len(data)==len(jobs)==len(heads),'Engine exact cardinality')
        keys=[(j['role_id'],j['arm'],j['recipe']['id'],j['seed']) for j in jobs]
        require(len(set(keys))==len(keys),'Duplicate engine job')
        require(len({capfor(j['arm']) for j in jobs})==1 or all(d.get('synthetic') for d in data),'Capability bucket')
        for d,j,h in zip(data,jobs,heads):
            require(d['binding']==(j['role_id'],j['arm']),'Engine data binding')
            require(h['binding']==(j['role_id'],'post' if j['arm']=='E-post' else 'pre',j['recipe']['gamma']),'Engine head binding')
        super().__init__(data,jobs,heads,streams=streams)

def bind(d,j,h):
    return dict(d,binding=(j['role_id'],j['arm'])),dict(h,binding=(j['role_id'],'post' if j['arm']=='E-post' else 'pre',j['recipe']['gamma']))

def synthetic(n,c):
    g=torch.Generator(device='cuda').manual_seed(20261016+n)
    a=torch.cat([(.1*torch.randn((n,k),device='cuda',dtype=torch.float64,generator=g)).softmax(1) for k in SIZES],1)
    b=torch.cat([(.1*torch.randn((n,k),device='cuda',dtype=torch.float64,generator=g)).softmax(1) for k in SIZES],1)
    y=torch.arange(n,device='cuda')%6;w=1/(6*torch.bincount(y)[y]).double()
    ci=torch.arange(c,device='cuda').repeat_interleave(n//c);idx,cw,pi=grouping(ci,w)
    mu=a.mean(0);sa=a.std(0,correction=0);mb=b.mean(0);sb=b.std(0,correction=0);m1,m2=moments(a,idx,cw)
    return dict(a=a,b=b,y=y,y_pre=y,w=w,w_pre=w,ci=ci,z=(b-mb)/sb,mu_A=mu,scale_A=sa,mu_B=mb,scale_B=sb,
        real_x=(a-mu)/sa,target=a,anchor=.9*b+.1*a,condition_rows=idx,conditional_w=cw,pi=pi,mom1=m1,mom2=m2,
        gap=tensor([[i,i//2] for i in range(c//2,c)],torch.long),synthetic=True)

def compare(a,b,i=None,old=False):
    maxerr=0.;idx=range(len(a['parameters'])) if i is None else [i]
    for kidx in idx:
        other=0 if old else kidx
        for k in KEYS:
            for field in ['parameters']+([] if old else ['gradients']):
                x=a[field][kidx][k];y=b[field][other][k]
                maxerr=max(maxerr,float((x-y).abs().max()))
                require(torch.allclose(x,y,atol=1e-9,rtol=1e-8),f'Replay {field} {kidx} {k}')
            for name,x in a['adam'][kidx][k].items():
                y=b['adam'][other][k][name]
                require(torch.equal(x,y) if name=='step' else torch.allclose(x,y,atol=1e-9,rtol=1e-8),f'Adam replay {kidx} {k} {name}')
                maxerr=max(maxerr,float((x-y).abs().max()))
    if not old:require(torch.equal(a['clips'],b['clips']),'Clipping counts')
    return maxerr

def qualify():
    configure('synthetic');begin('R2-synthetic');records=[]
    try:
        for n,c in [(192,16),(352,22)]:
            for lr in [.0003,.001]:
                d=synthetic(n,c);head=dict(W=torch.zeros((6,96),device='cuda',dtype=torch.float64),c=torch.zeros(6,device='cuda',dtype=torch.float64))
                recs=[r for r in RECIPES if r['lr']==lr]
                jobs=[dict(role_id=f'synthetic-{i}',arm=DYNAMIC[i%4],recipe=recs[i%3],seed=SEEDS[0]+i) for i in range(32)]
                ds=[];hs=[]
                for j in jobs:
                    a,b=bind(d,j,head);ds.append(a);hs.append(b)
                ref=BoundEngine(ds,jobs,hs,False);fast=BoundEngine(ds,jobs,hs,True)
                ck=fast.checkpoint();fast.capture();require(compare(ck,fast.checkpoint())==0,'Capture reset')
                for stop in [0,1,10,100]:
                    deadline();ref.advance(stop-ref.steps);fast.advance(stop-fast.steps)
                    err=compare(ref.checkpoint(),fast.checkpoint())
                    records.append(dict(rows=n,conditions=c,lr=lr,step=stop,max_error=err,models=32,passed=True))
                progress('R2_synthetic_bucket',rows=n,lr=lr,max_error=max(r['max_error'] for r in records))
                # Negative binding, duplicate, mixed-lr and mixed-row fixtures.
                for case in ['duplicate','binding','lr','rows']:
                    badjobs=[dict(j) for j in jobs];badds=[dict(x) for x in ds]
                    if case=='duplicate':badjobs[1]=badjobs[0]
                    if case=='binding':badds[0]['binding']=('wrong','N-P')
                    if case=='lr':badjobs[0]=dict(badjobs[0],recipe=next(r for r in RECIPES if r['lr']!=lr))
                    if case=='rows':badds[0]['b']=badds[0]['b'][:-1]
                    rejected=False
                    try:BoundEngine(badds,badjobs,hs,False)
                    except RuntimeError:rejected=True
                    require(rejected,'Negative engine fixture '+case)
                del fast,ref;torch.cuda.empty_cache()
        save(OUT/'tests/cuda-prefix-replay.parquet',records);write(OUT/'tests/R2-synthetic.json',dict(passed=True,rows=len(records)),True);codecheck()
    except BaseException as e:failure('R2-synthetic',e);raise
    finally:end('R2-synthetic')

def legacy(cap):
    configure(cap);begin('R2-legacy-'+cap);records=[]
    try:
        require(read(OUT/'tests/R2-synthetic.json')['passed'],'Synthetic qualification required')
        jobs=[j for j in registration()['jobs'] if capfor(j['arm'])==cap]
        for lr in [.0003,.001]:
            batch=sorted([j for j in jobs if j['recipe']['lr']==lr],key=lambda j:(j['role_id'],j['arm'],j['recipe']['id'],j['seed']))
            require(0<len(batch)<=32,'One fixed bucket at each learning rate')
            ds=[];hs=[];cache={}
            for j in batch:
                key=(j['role_id'],j['arm']);r=lookup(j['role_id'])
                if key not in cache:cache[key]=load(r,j['arm'])
                h=initial_head(r,'post' if cap=='E' else 'pre',j['recipe']['gamma'])
                d,h=bind(cache[key],j,h);ds.append(d);hs.append(h)
            fast=BoundEngine(ds,batch,hs,True);eager=BoundEngine(ds,batch,hs,False);fast.capture()
            for stop in [0,1,10,100,500,1000,2000]:
                deadline();fast.advance(stop-fast.steps);ck=fast.checkpoint()
                if stop<=100:
                    eager.advance(stop-eager.steps);eager_error=compare(ck,eager.checkpoint())
                else:eager_error=None
                for i,j in enumerate(batch):
                    if stop==10:old_error=None
                    else:
                        p=modelroot(lookup(j['role_id']),j['arm'],j['recipe']['id'])
                        old=own(p/('terminal.pt' if stop==2000 else f'trajectory/step-{stop:04}.pt'),j['role_id'])
                        require(old['steps']==stop,'Old state step')
                        old_error=compare(ck,dict(parameters=[old['parameters']],adam=[old['adam']]),i,True)
                    records.append(dict(role_id=j['role_id'],arm=j['arm'],candidate=j['recipe']['id'],lr=lr,step=stop,
                        eager_error=eager_error,legacy_error=old_error,old_gradient_available=False,passed=True))
                    put(OUT/'R2-legacy'/j['role_id']/j['arm']/j['recipe']['id']/f'step-{stop:04}.pt',
                        dict(parameters=ck['parameters'][i],gradients=ck['gradients'][i],adam=ck['adam'][i],clips=ck['clips'][i],steps=stop),
                        role_id=j['role_id'],capability=cap)
                progress('R2_legacy',capability=cap,lr=lr,step=stop,models=len(batch))
            fast.diagnostics();del fast,eager;torch.cuda.empty_cache()
        save(OUT/'tests'/f'legacy-compatibility-{cap}.parquet',records)
        write(OUT/'tests'/f'R2-legacy-{cap}.json',dict(passed=True,paths=len(jobs),query_read=False),True);codecheck()
    except BaseException as e:
        if records:save(OUT/'tests'/f'legacy-compatibility-{cap}-partial.parquet',records)
        failure('R2-legacy-'+cap,e);raise
    finally:end('R2-legacy-'+cap)

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('phase',choices=['synthetic','legacy']);p.add_argument('--cap',choices=['P','G','E'])
    a=p.parse_args();qualify() if a.phase=='synthetic' else legacy(a.cap)
