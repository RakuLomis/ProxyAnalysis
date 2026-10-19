"""Train-free post-only export replay and negative phase-reader checks."""
from common import *
from deploy import branch_logp
from formal import historical
from cuda_checks import synthetic
from moment_features import losses
from worker import modelroot

def verify():
    configure('inference');barrier('P1-numeric-complete.json');hashes=code_seal('P1-inference');t=time.perf_counter();checks=[]
    try:
        for r in [contract()['roles'][0],pilot_roles()[0]]:
            try:historical(r,'query')
            except (RuntimeError,FileNotFoundError) as e:
                require('barrier' in str(e),'Unexpected negative reader failure');checks.append(dict(test='query barrier',role=r['id'],passed=True))
            else:raise RuntimeError('Premature query read was allowed')
        d=synthetic();truth=losses(d['a'],d)
        require(max(abs(float(v)) for v in truth)<1e-24,'Truth gap was not zero')
        pre1=d['mom1'];ii,jj=d['gap'].T
        require(float((pre1[ii]-pre1[jj]).square().sum())>1e-7,'Missing nonzero pre-domain gap negative fixture')
        checks.append(dict(test='zero correct gap despite nonzero original pre-domain difference',passed=True))
        centers=d['a'].reshape(48,4,96).mean(1).repeat_interleave(4,0)
        require(float((d['a']-centers).square().sum())>1e-5,'Group rec should not be asserted zero for true pre')
        checks.append(dict(test='truth does not force group recovery zero',passed=True))
        r=pilot_roles()[0];raw=d['b'][:24]
        for arm,rec in [('R-P',gamma_tag(.0001)),('R-G',gamma_tag(.0001))]+[(a,'H01') for a in DYNAMIC]:
            exp=own(modelroot(r,arm,rec,SEEDS[0])/'export.pt',r['id']);lp=branch_logp(raw,exp)
            z=(raw-exp['mu_B'])/exp['scale_B'];anchor=raw if exp['anchor'] is None else torch.cat([z[:,block(j)]@exp['anchor'][f'M{j}'].T+exp['anchor'][f'c{j}'] for j in range(10)],1)
            if exp['residual'] is not None:
                s=exp['residual'];anchor=anchor+((z@s['U1'].T+s['d1']).clamp_min(0))@s['U2'].T
            projected=[]
            for j in range(10):
                u=anchor[:,block(j)].sort(1,descending=True).values;n=u.shape[1]
                prefix=torch.stack([u[:,:k+1].sum(1) for k in range(n)],1)-1
                k=torch.arange(1,n+1,device='cuda',dtype=torch.float64);rho=(u-prefix/k>0).sum(1)
                tau=prefix[torch.arange(len(u),device='cuda'),rho-1]/rho
                projected.append((anchor[:,block(j)]-tau[:,None]).clamp_min(0))
            a=torch.cat(projected,1);x=(a-exp['mu_A'])/exp['scale_A'];scores=x@exp['head']['W'].T+exp['head']['c']
            replay=scores-scores.logsumexp(1)[:,None]
            err=float((lp-replay).abs().max());require(torch.allclose(lp,replay,atol=1e-9,rtol=1e-8),'Independent post-only export replay '+arm)
            checks.append(dict(test='post-only independent projection/anchor/head',arm=arm,passed=True,max_error=err))
        immutable(OUT/'tests/P1-inference.json',dict(passed=True,checks=checks,query_H_U_reads=0));codecheck(hashes)
        progress('P1_inference_passed',checks=len(checks))
    except BaseException as e:failure('P1-inference',e);raise
    finally:debit('post-only-engineering-replay',time.perf_counter()-t,formal_fits=0);flush_reads('P1-inference')

if __name__=='__main__':verify()
