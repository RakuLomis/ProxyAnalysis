"""Synthetic mathematics, negative permissions and explicit objective checks only."""
from common import *
from simplex import Simplex,project_blocks,valid
from classifier import basis,objective as headobjective,independent,fit as headfit
from ridge_anchor import fit_inverse,forward
from moment_features import grouping,moments,losses

def mathematical(tag='P1-math-01'):
    configure('tests');barrier('P0-complete.json');hashes=code_seal(tag);checks=[];gen=torch.Generator(device='cuda').manual_seed(20261016)
    def check(name,ok,**kw):require(ok,name);checks.append(dict(test=name,passed=True,**kw))
    start=time.perf_counter()
    try:
        q=basis();check('Q contrast isometry',torch.allclose(q.T@q,torch.eye(5,device='cuda',dtype=torch.float64),atol=1e-14,rtol=0))
        v=torch.randn((24,96),device='cuda',dtype=torch.float64,generator=gen);a=project_blocks(v);valid(a)
        check('projection idempotent',torch.allclose(project_blocks(a),a,atol=1e-14,rtol=1e-14))
        check('projection constant shift',torch.allclose(project_blocks(v+3),a,atol=1e-14,rtol=1e-14))
        for j in range(10):
            sl=block(j);x=v[:,sl];z=a[:,sl];active=z>0;tau=((x-z)*active).sum(1)/active.sum(1)
            check('KKT block '+str(j),bool(((x-tau[:,None])[~active]<=1e-12).all()) and float(((x-z-tau[:,None])*active).abs().max())<1e-12)
        target=project_blocks(torch.rand((24,96),device='cuda',dtype=torch.float64,generator=gen))
        check('projection nonexpansive to feasible target',bool(((a-target).square().sum(1)<=(v-target).square().sum(1)+1e-10).all()))
        x=torch.full((2,9),1/9,device='cuda',dtype=torch.float64,requires_grad=True);direction=torch.randn(x.shape,device='cuda',dtype=x.dtype,generator=gen);coef=torch.randn(x.shape,device='cuda',dtype=x.dtype,generator=gen)
        z=Simplex.apply(x);grad=torch.autograd.grad((z*coef).sum(),x)[0]
        for h in [1e-4,1e-5]:
            fd=((Simplex.apply(x.detach()+h*direction)*coef).sum()-(Simplex.apply(x.detach()-h*direction)*coef).sum())/(2*h)
            exact=(grad*direction).sum();check('projection smooth FD '+str(h),torch.allclose(fd,exact,atol=1e-8,rtol=1e-6),error=float(abs(fd-exact)))
        vertex=tensor([[3.,0.,0.]]).requires_grad_();g=torch.autograd.grad(Simplex.apply(vertex).square().sum(),vertex)[0]
        check('single vertex generalized derivative',torch.equal(g,torch.zeros_like(g)))
        boundary=tensor([[1.,0.,0.]]).requires_grad_();g=torch.autograd.grad(Simplex.apply(boundary).sum(),boundary)[0]
        check('boundary saved strict active set',torch.equal(g,torch.zeros_like(g)))
        delta=tensor([[1.,-1.,0.]])
        one=(Simplex.apply(boundary.detach()+1e-5*delta)-Simplex.apply(boundary.detach()))/1e-5
        check('boundary outward one-sided constant',float(one.abs().max())<1e-8)
        ci=torch.arange(4,device='cuda').repeat_interleave(6);w=torch.full((24,),1/24,device='cuda',dtype=torch.float64)
        idx,cw,pi=grouping(ci,w);first,second=moments(target,idx,cw)
        d=dict(condition_rows=idx,conditional_w=cw,pi=pi,mom1=first,mom2=second,gap=tensor([[2,0],[3,1]],torch.long))
        check('truth has zero fidelity and gap',max(float(z.abs()) for z in losses(target,d))<1e-25)
        pred=(target+.005*torch.randn(target.shape,device='cuda',dtype=torch.float64,generator=gen)).requires_grad_()
        fast=sum(losses(pred,d));phi=lambda x:torch.cat([x/np.sqrt(10),(x[:,:,None]*x[:,None,:]).flatten(1)/10],1)
        em=phi(pred).reshape(4,6,-1).mean(1)-phi(target).reshape(4,6,-1).mean(1)
        explicit=(pi*em.square().sum(1)).sum()+(em[[2,3]]-em[[0,1]]).square().sum(1).mean()
        gf=torch.autograd.grad(fast,pred,retain_graph=True)[0];ge=torch.autograd.grad(explicit,pred)[0]
        check('explicit Phi versus raw moment values',torch.allclose(fast,explicit,atol=1e-12,rtol=1e-10))
        check('explicit Phi versus moment gradients',torch.allclose(gf,ge,atol=1e-12,rtol=1e-10))
        check('finite moment dual factor',abs(float((em*em).sum()/2-(em*em-em.square()/2).sum()))<1e-12)
        centers=target.reshape(6,4,96).mean(1).repeat_interleave(4,0)
        cart=((pred.detach()[:,None]-target.reshape(6,4,96).repeat_interleave(4,0)).square().sum(2).mean(1)*w).sum()/10
        cent=((pred.detach()-centers).square().sum(1)*w).sum()/10
        constant=((target-centers).square().sum(1)*w).sum()/10
        check('Cartesian center constant',abs(float(cart-cent-constant))<1e-12)
        check('group center second moment is not true moment',float((target.T@target/24-centers.T@centers/24).norm())>1e-5)
        z=torch.randn((24,96),device='cuda',dtype=torch.float64,generator=gen)
        p,errs=fit_inverse(z,target,w);gp,_=fit_inverse(z,centers,w)
        check('independent inverse Ridge bundles',float((forward(z,p)-forward(z,gp)).norm())>1e-5)
        perm=torch.arange(24,device='cuda').reshape(6,4).flip(1).flatten();gc,_=fit_inverse(z,centers[perm],w)
        check('group permutation invariance',max(float((gc[k]-gp[k]).abs().max()) for k in gp)<1e-13)
        W=torch.randn((6,96),device='cuda',dtype=torch.float64,generator=gen).requires_grad_();b=torch.randn(6,device='cuda',dtype=torch.float64,generator=gen).requires_grad_()
        y=torch.arange(6,device='cuda').repeat(4);value=headobjective(W,b,z,y,w,.001);gW,gb=torch.autograd.grad(value,(W,b));ref,rw,rb,_=independent(W,b,z,y,w,.001)
        check('head independent loss and gradient',abs(float(value-ref))<1e-10 and max(float((gW-rw).abs().max()),float((gb-rb).abs().max()))<1e-10)
        lp0=F.log_softmax(z[:,:6],1);lp1=F.log_softmax(-z[:,:6],1)
        for beta in BETAS:
            lp=lp0 if beta==0 else lp1 if beta==1 else torch.logaddexp(np.log1p(-beta)+lp0,np.log(beta)+lp1)
            prob=(1-beta)*lp0.exp()+beta*lp1.exp();check('mixture '+str(beta),torch.allclose(lp.exp(),prob,atol=1e-14,rtol=1e-14))
        # Capability checks stop before tensor deserialization, no actual P input is read.
        r=pilot_roles()[0]
        configure('G')
        try:own(OUT/'packages'/r['id']/'paired/train.pt',r['id'])
        except RuntimeError as e:check('G P-reader negative','Capability denied' in str(e))
        else:raise RuntimeError('Group P-reader allowed')
        configure('E')
        try:own(OUT/'packages'/r['id']/'scales/pre.pt',r['id'])
        except RuntimeError as e:check('E pre-reader negative','Capability denied' in str(e))
        else:raise RuntimeError('E pre-reader allowed')
        configure('tests')
        immutable(OUT/'tests'/tag/'math.json',dict(passed=True,checks=checks,query_reads=0,H_U_reads=0))
        progress('P1_math_passed',tests=len(checks))
    except BaseException as e:failure(tag,e);raise
    finally:
        debit('engineering-math',time.perf_counter()-start,formal_fit=False);flush_reads(tag);codecheck(hashes)
