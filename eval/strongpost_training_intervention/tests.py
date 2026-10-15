"""Synthetic arithmetic checks and injected permission failures; no fit."""
from common import *
import objectives as O
import influence as I

def run():
    with stage('tests'):
        torch.manual_seed(20261009);rows=[]
        def check(name,ok,**kw):require(ok,name);rows.append({'name':name,'passed':True,**kw})
        q=I.basis();check('bias orthonormal',residual(q.T@q,torch.eye(5,device=device(),dtype=torch.float64))<1e-12)
        check('bias excludes only common shift',float((q.T@torch.ones(6,device=device(),dtype=torch.float64)).abs().max())<1e-12)
        x=torch.randn((18,96),device=device(),dtype=torch.float64)/3
        y=torch.arange(18,device=device())%6;m=torch.full((18,),1/18,device=device(),dtype=torch.float64)
        v={}
        for a in ['main','C','S','P','G']:
            v[a+'_x']=x+(.03 if a=='P' else .05 if a=='G' else 0)
            v[a+'_y']=y;v[a+'_mass']=m/3
        v.update(mu=torch.zeros(96,device=device(),dtype=torch.float64),scale=torch.ones(96,device=device(),dtype=torch.float64))
        model={'weight':torch.randn((6,96),device=device(),dtype=torch.float64)/20,
               'bias':torch.randn(6,device=device(),dtype=torch.float64)}
        for a in ['P','G']:
            for beta in [0.,.1,1.]:
                s=O.slot(v,a,beta)
                wanted=O.loss(model,O.slot(v,a,0.),4.)+beta*(O.loss(model,O.auxiliary(v,a),4.,False)-O.loss(model,O.auxiliary(v,'S'),4.,False))
                check('loss-mass interpolation '+a+str(beta),abs(float(O.loss(model,s,4.)-wanted))<1e-12)
        s=O.slot(v,'P',0.);h=I.hessian(model,s,4.,q);ha=I.auto_hessian(model,s,4.,q)
        check('581 Hessian replay',residual(h,ha)<=1e-10,error=residual(h,ha))
        check('gauge probability invariance',residual(torch.softmax(x@model['weight'].T+model['bias'],1),
              torch.softmax(x@model['weight'].T+O.normalized_model(model)['bias'],1))<1e-12)
        for kind,purpose in [('main-outer-labels','train'),('main-test-paired','train'),('JA-C-paired','group-map')]:
            try:permission(kind,purpose)
            except RuntimeError:check('reject '+kind+' in '+purpose,True)
            else:raise RuntimeError('Negative permission accepted')
        for identity in ['visit_id','session_id','pair_id','repetition','carrier_id','shared_row_index']:
            df=pd.DataFrame(np.zeros((1,96)),columns=HIST);df['content_token']='a';df['fit_mass']=1.;df[identity]='x'
            try:group_schema(df)
            except RuntimeError:check('reject group '+identity,True)
            else:raise RuntimeError('Group identity accepted')
        for name,d,info in [
            ('reject target U',pd.DataFrame({'content_id':['U'],'protocol':['p']}),{'kind':'C-post','scope':{'C_contents':['C'],'calibration':'p'}}),
            ('reject heldout content',pd.DataFrame({'content_id':['H'],'protocol':['s']}),{'kind':'source-post','scope':{'train_contents':['train'],'sources':['s']}}),
            ('reject actual target in sources',pd.DataFrame({'content_id':['train'],'protocol':['p']}),{'kind':'source-post','scope':{'train_contents':['train'],'sources':['s']}})]:
            try:validate_scope(d,info)
            except RuntimeError:check(name,True)
            else:raise RuntimeError(name+' failed')
        df=pd.DataFrame(np.zeros((1,96)),columns=HIST);df['visit_id']='x';df['pre_h00_00']=1
        try:base.validate_query(df)
        except RuntimeError:check('reject pre/extra numeric query',True)
        else:raise RuntimeError('Unsafe query accepted')
        for r in contract()['pilot_roles'][:1]:
            try:package(rolepath(r)/'labels.parquet','pilot-labels')
            except RuntimeError:check('pilot labels require whole prediction seal',True)
            else:raise RuntimeError('Early pilot labels accepted')
        r=contract()['roles'][0]
        try:package(rolepath(r)/'labels.parquet','score')
        except RuntimeError:check('outer labels require whole prediction seal',True)
        else:raise RuntimeError('Early outer labels accepted')
        write(OUT/'manifests/tests.json',{'passed':True,'checks':rows,'new_fits':0,'cuda':True,'dtype':'float64','application_permission_checks_not_OS_isolation':True})

if __name__=='__main__':run()
