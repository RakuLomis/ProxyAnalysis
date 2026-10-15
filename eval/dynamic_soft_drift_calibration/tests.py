"""Synthetic mathematics and injected permission checks. No classifier fit."""
from common import *
from amplitude import adjust,regularizer
import recovery as R
import unroll as U

def run():
    with stage('tests'):
        torch.manual_seed(20261012);rows=[]
        def check(name,ok,**details):
            require(ok,name);rows.append(dict(name=name,passed=True,**details))
        a=torch.randn((12,96),device=device(),dtype=torch.float64)
        b0=torch.randn_like(a);b=torch.randn_like(a);w=torch.full((12,),1/12,device=device(),dtype=torch.float64)
        q=tensor(np.linspace(.8,1.2,10));one=tensor(np.ones(10))
        check('q zero raw pre',torch.equal(adjust(a,b0,one*0),a))
        check('q one raw base',float((adjust(a,b0,one)-b0).abs().max())<1e-12)
        check('q two scaled drift',float((adjust(a,b0,one*2)-(2*b0-a)).abs().max())<1e-12)
        mu=torch.randn(96,device=device(),dtype=torch.float64);scale=torch.rand_like(mu)+.2
        check('diagonal coordinate exchange',float(((adjust(a,b0,q)-mu)/scale-
              adjust((a-mu)/scale,(b0-mu)/scale,q)).abs().max())<1e-12)
        c=R.coefficients(a,b0,b,w);c['s'],rawvar=R.anonymous_variance(b,w)
        check('quadratic explicit error',float((R.error(q,c)-R.explicit_error(a,b0,b,w,q)).abs().max())<1e-12)
        check('baseline gap exact zero',torch.equal(R.gap(one,c),one*0))
        qq=q.clone().requires_grad_();gg=R.gap(qq,c)
        grad=torch.autograd.grad(gg.sum(),qq)[0]
        check('analytic recovery derivative',float((grad-(2*c['A']*qq-2*c['B'])/c['s']).abs().max())<1e-12)
        penalty,lam,g=R.soft(q,c)
        saddle=((lam*g-lam.square()/2).mean())
        check('closed dual equals hinge',abs(float(penalty-saddle))<1e-12)
        for r in contract()['pilot_roles']:
            gp=package(ROOT/r['C_group_pre'],'group-recovery','D-G',r)
            gb=package(ROOT/r['C_group_post'],'group-recovery','D-G',r)
            yy,var=R.group_center_targets(gp,gb)
            aa=tensor(gp[HIST]);bb0=aa+.01
            center=R.explicit_error(aa,bb0,yy,tensor(gp.fit_mass),q)+var
            explicit=torch.zeros(10,device=device(),dtype=torch.float64)
            adjusted=adjust(aa,bb0,q)
            for token,d in gp.groupby('content_token'):
                ix=np.flatnonzero(gp.content_token.eq(token));post=gb[gb.content_token.eq(token)]
                other=tensor(post[HIST]);local=tensor(post.fit_mass)/float(post.fit_mass.sum())
                for j in range(10):
                    diff=adjusted[tensor(ix,torch.long)][:,None,block(j)]-other[None,:,block(j)]
                    explicit[j]+=(diff.square().mean(2)*tensor(d.fit_mass)[:,None]*local[None,:]).sum()
            check('group Cartesian moment '+r['id'],float((center-explicit).abs().max())<1e-12)
            rev=gp.iloc[::-1].reset_index(drop=True);rv=gb.sample(frac=1,random_state=20261012).reset_index(drop=True)
            yr,vr=R.group_center_targets(rev,rv)
            check('group order invariant '+r['id'],float((var-vr).abs().max())<1e-12 and float((yy-yr.flip(0)).abs().max())<1e-12)
        for name,call in [
            ('deny target outer labels',lambda:package_permission('main-outer-labels','meta-labels','D-P')),
            ('deny target query as train',lambda:package_permission('main-query','train','D-P')),
            ('deny paired group input',lambda:package_permission('JA-C-paired','paired-recovery','D-G')),
            ('deny P group artifact',lambda:artifact_permission('P','D-G')),
            ('deny unknown raw captures',lambda:package_permission('PCAP','train','D-P')),
            ('deny old write',lambda:writable(JA/'new-file.json'))]:
            try:call()
            except RuntimeError:check(name,True)
            else:raise RuntimeError('Permission negative accepted '+name)
        r=contract()['pilot_roles'][0];bad=dict(r,sources=r['sources']+[r['target']])
        try:role_permission(bad,True)
        except RuntimeError:check('deny actual target in sources',True)
        else:raise RuntimeError('Target source accepted')
        bad=dict(r,train_contents=r['train_contents']+r['validation_contents'][:1])
        try:role_permission(bad,True)
        except RuntimeError:check('deny same content across split',True)
        else:raise RuntimeError('Cross split accepted')
        # Verify the hand-written functional GD gradient against autograd, including bias.
        task=pilot_task(r,'D-P');v=task['view'];slot=U.pack(v,'P',one)
        th=torch.randn((6,97),device=device(),dtype=torch.float64)*.01;th.requires_grad_()
        ag=torch.autograd.grad(U.original_objective(th,slot,r['t']),th)[0]
        check('analytic classifier gradient',float((ag-U.original_gradient(th,slot,r['t'])).abs().max())<1e-10)
        theta=th.detach();cond=v['conditioning'];V=(theta@torch.linalg.inv(cond['inv'])).requires_grad_()
        decoded=V@cond['inv']
        transformed=torch.autograd.grad(U.original_objective(decoded,slot,r['t']),V)[0]
        ax=torch.cat([slot['x'],torch.ones_like(slot['x'][:,:1])],1)@cond['inv'].T
        z=ax@V.T;B=cond['inv'][:,:96]
        manual=((torch.softmax(z,1)-F.one_hot(slot['y'],6))*slot['mass'][:,None]).T@ax+.001*(1+r['t'])*(V@B)@B.T
        check('functional transformed gradient',float((manual-transformed).abs().max())<1e-10)
        check('bias not regularized',float((U.original_gradient(theta,slot,r['t'])[:,96]-
              ((torch.softmax(slot['x']@theta[:,:96].T+theta[:,96],1)-F.one_hot(slot['y'],6))*slot['mass'][:,None]).sum(0)).abs().max())<1e-12)
        check('classifier data CUDA',slot['x'].is_cuda and slot['x'].dtype==torch.float64)
        save(pd.DataFrame(rows),OUT/'audits/unit-tests.parquet')
        write(OUT/'audits/unit-tests.json',dict(passed=True,checks=len(rows),new_classifier_fits=0))

if __name__=='__main__':run()
