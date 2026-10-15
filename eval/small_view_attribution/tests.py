"""Deterministic arithmetic and identity negative tests; no model fitting."""
from common import *
import objectives as O
import marginal as M

def run():
    with stage('tests'):
        gen=torch.Generator(device=device()).manual_seed(20261010)
        x=torch.randn(64,96,device=device(),dtype=torch.float64,generator=gen)
        x[:,95]=0;w=torch.full((64,),1/64,device=device(),dtype=torch.float64)
        y=x@torch.diag(torch.linspace(.7,1.3,96,device=device(),dtype=torch.float64))+.2
        data={'pre':x,'post':y,'pre_mass':w,'post_mass':w};m,log=M.fit(data);results={}
        ident,_=M.fit({**data,'post':x});results['identity']=residual(M.apply(ident,x),x)
        shift,_=M.fit({**data,'post':x+.2});results['translation']=residual(M.apply(shift,x),x+.2)
        order=torch.randperm(64,device=device(),generator=gen)
        perm,_=M.fit({**data,'pre':x[order],'pre_mass':w[order],'post':y.flip(0),'post_mass':w.flip(0)})
        results['independent_permutation']=residual(M.apply(m,x),M.apply(perm,x))
        features=torch.randperm(96,device=device(),generator=gen)
        fp,_=M.fit({**data,'pre':x[:,features],'post':y[:,features]})
        results['feature_equivariance']=residual(M.apply(m,x)[:,features],M.apply(fp,x[:,features]))
        wm=torch.full((48,),1/48,device=device(),dtype=torch.float64)
        _,small=M.fit({**data,'post':y[:48],'post_mass':wm})
        results['different_side_count_finite']=float(small['congruence_error'])
        for bad in ['content_token','pair_id','visit_id']:
            rejected=False
            try:M.schema({**data,bad:torch.arange(64,device=device())})
            except RuntimeError:rejected=True
            require(rejected,'Identity injection was accepted')
        mean,cov=M.moments(x,w);results['sample_covariance']=residual(cov,(x-x.mean(0)).T@(x-x.mean(0))/63)
        require(max(results.values())<1e-10,'Marginal mathematical tests')
        r=contract()['roles'][0];v=artifact(oldviews(r));model=artifact(basemodel(r))
        zero=O.slot(v,v['S_x'],v['S_y'],v['S_mass'],0.)
        noop=O.slot(v,v['S_x'],v['S_y'],v['S_mass'],.1)
        for mm in [model,{'weight':torch.randn(6,96,device=device(),dtype=torch.float64,generator=gen)*.05,
                         'bias':torch.randn(6,device=device(),dtype=torch.float64,generator=gen)*.05}]:
            require(abs(float(O.loss(mm,zero,r['t'])-O.loss(mm,noop,r['t'])))<1e-10,'No-op loss')
            for a,b in zip(O.gradient(mm,zero,r['t']),O.gradient(mm,noop,r['t'])):require(residual(a,b)<1e-10,'No-op gradient')
        expanded=O.slot(v,v['main_x'],v['main_y'],v['main_mass'])
        merged={'x':torch.cat([v['main_x'],v['S_x'],v['C_x']]),
                'y':torch.cat([v['main_y'],v['S_y'],v['C_y']]),
                'mass':torch.cat([1.1*v['main_mass'],.9*v['S_mass'],v['C_mass']])}
        require(abs(float(O.loss(model,expanded,r['t'])-O.loss(model,merged,r['t'])))<1e-10,'Duplicate merge loss')
        for a,b in zip(O.gradient(model,expanded,r['t']),O.gradient(model,merged,r['t'])):require(residual(a,b)<1e-10,'Duplicate merge gradient')
        ww=model['weight'].detach().clone().requires_grad_();bb=model['bias'].detach().clone().requires_grad_()
        gg=torch.autograd.grad(O.loss({'weight':ww,'bias':bb},expanded,r['t']),(ww,bb))
        for a,b in zip(gg,O.gradient(model,expanded,r['t'])):require(residual(a,b)<1e-10,'Independent gradient formula')
        for beta in [0.,.1]:
            zz=O.slot(v,v['P_x'],v['P_y'],v['P_mass'],beta)
            require(len(zz['x'])==(640 if beta==0 else 928),'Weighted rows')
        write(OUT/'manifests/tests.json',{'passed':True,'marginal_tests':results,'identity_negative_tests':3,
              'no_op_objective_and_gradient':True,'duplicate_merge':True,'autograd_gradient':True,
              'classifier_fits':0,'target_test_labels_read':False})

if __name__=='__main__':run()
