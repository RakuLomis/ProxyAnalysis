"""Adapter-only no-fit checks; do not repeat the scientific/numerical pilot."""
from common import *
from backend import modules

def run():
    with stage('E0'):
        n,l=modules()
        gates=[]
        for it in [1024,1056,3999,4000]:
            for gradient in [9.99e-6,1e-5,1.00001e-5]:
                got=acceptance_gates(1.,2.,gradient,it,0.,0.)
                require(got['original_coordinate_gradient']==(gradient<=1e-5) and got['iteration_budget']==(it<4000),'Original numerical gate binding')
                gates.append(dict(it=it,gradient=gradient,result=got))
        theta=torch.cos(torch.arange(582,device=device(),dtype=torch.float64).reshape(6,97)/37)/10
        theta[:,:96]+=.02;theta[:,96]+=.3
        x=torch.sin(torch.arange(12*96,device=device(),dtype=torch.float64).reshape(12,96)/17)/3
        s=dict(x=x,y=torch.arange(12,device=device())%6,mass=torch.full((12,),1/12,device=device(),dtype=torch.float64))
        u,k=n.encode(theta);decoded=n.decode(u,k);require(torch.equal(theta[:,:96],decoded[:,:96]),'All W must survive runtime gauge')
        a=n.audit(theta,s,4.);require(abs(float(n.value(theta,s,4.)-n.value(decoded,s,4.)))<1e-10,'Runtime target equivalence')
        h=n.hessian(decoded,s,4.);v=torch.ones(581,device=device(),dtype=torch.float64);v[1::2]=-1;v=v/v.norm()
        _,hv=torch.autograd.functional.hvp(lambda z:n.value(n.decode(z,k),s,4.),u,v)
        he=float((h@v-hv).norm()/hv.norm().clamp_min(1));require(he<=1e-10,'Full runtime Hessian binding')
        settings=l.backend().SETTINGS;require(settings['max_iter']==4000 and settings['max_eval']==20000,'Original global resource bounds')
        write(OUT/'audits/engineering.json',dict(passed=True,actual_fits=0,source_NR2_math_reused=True,Hessian_binding_error=he,
            original_coordinate_replay=a,boundaries=gates,legacy_settings=settings,H_reads=0))
        progress('NR2_full_engineering_passed',actual_fits=0)
