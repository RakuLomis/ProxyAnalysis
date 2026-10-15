"""Permission negatives and fixed amplitude/Adam tests, no H data."""
from common import *

def run():
    with stage('permissions'):
        failures=0
        for kind,purpose,arm in [('main-outer-labels','source-feedback','D-P'),('main-query','final-train','D-P'),
                                 ('P-score','C-P-score','D-G'),('source-pre','H-query','D-P'),
                                 ('JA-C-paired','source-train','D-G'),('main-outer-labels','H-query','T-P')]:
            try:kind_permission(kind,purpose,arm)
            except RuntimeError:failures+=1
            else:raise RuntimeError('Permission negative accepted')
        r=contract()['roles'][0]
        for purpose,fn in [('H-query','query.parquet'),('H-score','labels.parquet'),('source-feedback','query.parquet')]:
            try:package(PREP/'packages'/r['id']/fn,purpose,'D-P',r)
            except RuntimeError:failures+=1
            else:raise RuntimeError('Premature H access accepted')
        # Independent manual Adam recurrence vs PyTorch, with projected parameters.
        q=torch.ones(10,device=device(),dtype=torch.float64,requires_grad=True);ref=q.detach().clone();m=torch.zeros_like(q);v=torch.zeros_like(q)
        opt=torch.optim.Adam([q],lr=.05,betas=(.9,.999),eps=1e-8)
        for k in range(20):
            g=torch.linspace(-.5,.5,10,device=device(),dtype=torch.float64)*(k+1)
            q.grad=g.clone();opt.step()
            with torch.no_grad():q.clamp_(0,2)
            m=.9*m+.1*g;v=.999*v+.001*g.square()
            ref=(ref-.05*(m/(1-.9**(k+1)))/(torch.sqrt(v/(1-.999**(k+1)))+1e-8)).clamp(0,2)
        error=float((q-ref).abs().max());require(error<1e-12,'Adam policy mismatch')
        a,u,_,rec=production()
        x=torch.arange(192,device=device(),dtype=torch.float64).reshape(2,96)/1000
        require(torch.equal(a.adjust(x,x+1,torch.ones_like(q)),x+1),'q=1 adjust identity')
        require(torch.equal(a.adjust(x,x+1,torch.zeros_like(q)),x),'q=0 adjust identity')
        try:cuda(torch.ones(1))
        except RuntimeError:failures+=1
        else:raise RuntimeError('CPU fallback accepted')
        write(OUT/'audits/permission-tests.json',dict(passed=True,negative_checks=failures,Adam_steps=20,Adam_replay_error=error,H_numeric_reads=0))

if __name__=='__main__':run()

