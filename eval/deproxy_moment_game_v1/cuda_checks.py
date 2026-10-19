"""Independent versus 32-model, 8-stream CUDA Graph replay; train-only synthetic geometry."""
from common import *
from models import initial,objective,KEYS
from classifier import basis
from simplex import project_blocks
from moment_features import grouping,moments
from engine import Engine

def synthetic(n=192,c=16):
    g=torch.Generator(device='cuda').manual_seed(20261016+n)
    a=torch.cat([(.1*torch.randn((n,k),device='cuda',dtype=torch.float64,generator=g)).softmax(1) for k in SIZES],1)
    b=torch.cat([(.1*torch.randn((n,k),device='cuda',dtype=torch.float64,generator=g)).softmax(1) for k in SIZES],1)
    w=torch.full((n,),1/n,device='cuda',dtype=torch.float64);y=torch.arange(n,device='cuda')%6
    ci=torch.arange(c,device='cuda').repeat_interleave(n//c);idx,cw,pi=grouping(ci,w)
    mu=a.mean(0);sa=a.std(0,correction=0);mb=b.mean(0);sb=b.std(0,correction=0)
    m1,m2=moments(a,idx,cw)
    return dict(a=a,b=b,y=y,y_pre=y,w=w,w_pre=w,ci=ci,z=(b-mb)/sb,mu_A=mu,scale_A=sa,mu_B=mb,scale_B=sb,
        real_x=(a-mu)/sa,target=a,anchor=.9*b+.1*a,condition_rows=idx,conditional_w=cw,pi=pi,mom1=m1,mom2=m2,
        gap=tensor([[i, i//2] for i in range(c//2,c)],torch.long))

def qualify(tag='P1-CUDA-01'):
    configure('tests');barrier('P0-complete.json');hashes=code_seal(tag);started=time.perf_counter();records=[]
    try:
        d=synthetic();q=basis();head=dict(W=torch.zeros((6,96),device='cuda',dtype=torch.float64),c=torch.zeros(6,device='cuda',dtype=torch.float64))
        state={k:v.requires_grad_() for k,v in initial(head,SEEDS[0]).items()}
        gen=torch.Generator(device='cuda').manual_seed(17)
        # Tiny nonzero U2 activates both residual layers for a full objective FD.
        with torch.no_grad():state['U2'].normal_(0,.0001,generator=gen)
        checks=[]
        for arm in DYNAMIC:
            val,_,_,_=objective(state,d,arm,RECIPES[0],q)
            grad=torch.autograd.grad(val,list(state.values()))
            vec={k:torch.randn(v.shape,device='cuda',dtype=torch.float64,generator=gen)*.01 for k,v in state.items()}
            exact=sum((x*vec[k]).sum() for k,x in zip(state,grad))
            for h in [1e-4,1e-5]:
                plus={k:v.detach()+h*vec[k] for k,v in state.items()};minus={k:v.detach()-h*vec[k] for k,v in state.items()}
                fd=(objective(plus,d,arm,RECIPES[0],q)[0]-objective(minus,d,arm,RECIPES[0],q)[0])/(2*h)
                err=float(abs(fd-exact));require(torch.allclose(fd,exact,atol=1e-8,rtol=1e-6),'Full objective FD '+arm)
                checks.append(dict(arm=arm,h=h,error=err))
        jobs=[dict(arm=DYNAMIC[i%4],recipe=RECIPES[0],seed=SEEDS[0]+i) for i in range(32)]
        data=[d]*32;heads=[head]*32
        ref=Engine(data,jobs,heads,streams=False);fast=Engine(data,jobs,heads,streams=True)
        before=fast.checkpoint();fast.capture();after=fast.checkpoint()
        require(all(torch.equal(before['parameters'][i][k],after['parameters'][i][k]) and torch.equal(before['adam'][i][k]['step'],after['adam'][i][k]['step']) for i in range(32) for k in KEYS),'Capture warmup was not reset')
        for endpoint in [1,10,100]:
            ts=time.perf_counter();ref.advance(endpoint-ref.steps);torch.cuda.synchronize();rs=time.perf_counter()-ts
            ts=time.perf_counter();fast.advance(endpoint-fast.steps);torch.cuda.synchronize();fs=time.perf_counter()-ts
            a=ref.checkpoint();b=fast.checkpoint();maxerr=0.
            for i in range(32):
                for k in KEYS:
                    for field in ['parameters','gradients']:
                        x=a[field][i][k];y=b[field][i][k];maxerr=max(maxerr,float((x-y).abs().max()))
                        require(torch.allclose(x,y,atol=1e-9,rtol=1e-8),f'CUDA replay {field} {i} {k}')
                    for name,x in a['adam'][i][k].items():
                        y=b['adam'][i][k][name]
                        require(torch.equal(x,y) if name=='step' else torch.allclose(x,y,atol=1e-9,rtol=1e-8),'CUDA Adam replay')
            require(torch.equal(a['clips'],b['clips']),'Clipping counter replay')
            records.append(dict(endpoint=endpoint,independent_seconds=rs,graph_seconds=fs,max_abs_error=maxerr))
            progress('P1_CUDA_replay',endpoint=endpoint,graph_seconds=fs,max_error=maxerr)
        immutable(OUT/'tests'/tag/'replay.json',dict(passed=True,full_objective_FD=checks,replay=records,models=32,streams=8,dtype='float64',H_U_query_reads=0,
            peak_allocated_MiB=torch.cuda.max_memory_allocated()/1048576,peak_reserved_MiB=torch.cuda.max_memory_reserved()/1048576))
        codecheck(hashes);progress('P1_CUDA_passed',prefixes=[1,10,100])
    except BaseException as e:failure(tag,e);raise
    finally:debit('CUDA-engineering',time.perf_counter()-started,formal_paths=0);flush_reads(tag)

if __name__=='__main__':qualify()
