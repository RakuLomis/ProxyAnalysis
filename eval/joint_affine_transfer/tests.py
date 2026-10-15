"""CUDA algebra, permission and strict syntax tests before sealing."""
from common import *
import affine

def run():
    configure(); torch.manual_seed(20261007); rows=[]; access=[]
    def check(name,ok,**extra):
        require(ok,name); rows.append({'name':name,'passed':True,**extra})
    x=torch.randn((48,96),device=device(),dtype=torch.float64); x[:,0]=0
    true=torch.eye(96,device=device(),dtype=torch.float64); true[4,20]=.8
    y=x@true.T+torch.arange(96,device=device(),dtype=torch.float64)/100
    w=torch.full((48,),1/48,device=device(),dtype=torch.float64)
    for arm in ['JA0','JA1']:
        for eta in ETAS:
            m,log=affine.fit(x,y,w,eta,arm)
            check(arm+' eta '+str(eta),log['accepted'],gradient_max=log['gradient_max'])
            if arm=='JA0':
                mask=torch.zeros((96,96),device=device(),dtype=torch.bool)
                for j in range(10):mask[block(j),block(j)]=True
                check('block zeros '+str(eta),bool((m['matrix'][~mask]==0).all()))
    xx=np.asarray(x.cpu()); yy=np.asarray(y.cpu()); groups=np.repeat(np.arange(12),4).astype(str)
    gp=pd.DataFrame(xx,columns=HIST); gb=pd.DataFrame(yy,columns=HIST)
    for d in [gp,gb]:d['content_token']=groups;d['fit_mass']=1/48
    targets,const=affine.group_targets(gp,gb); gm,log=affine.fit(x,targets,w,1.,'JA2',const)
    pred=affine.apply(gm,x); explicit=torch.zeros((),device=device(),dtype=torch.float64)
    for k in range(12):explicit+=(pred[4*k:4*k+4,None,:]-y[None,4*k:4*k+4,:]).square().sum()/(12*16*96)
    rec,_=affine.objective_parts(gm['matrix'],gm['bias'],x,targets,w,float(gm['alpha']),const)
    check('full donor loss equals center plus variance',abs(float(explicit-rec))<1e-12)
    gp2=gp.sample(frac=1,random_state=19).reset_index(drop=True)
    gb2=gb.sample(frac=1,random_state=31).reset_index(drop=True)
    t2,c2=affine.group_targets(gp2,gb2); shuffled,lg=affine.fit(tensor(gp2[HIST]),t2,tensor(gp2.fit_mass),1.,'JA2',c2)
    check('independent permutation invariant',float((gm['matrix']-shuffled['matrix']).abs().max())<1e-12)
    xm,ym,sxx,_=affine.data_moments(x,targets,w)
    tm,_,txx,_=affine.data_moments(x,y,w)
    check('group retains ALL input covariance',torch.equal(sxx,txx))
    check('group centers differ from input centered-only covariance',
          not torch.allclose(sxx,((x.reshape(12,4,96).mean(1)-xm).T@(x.reshape(12,4,96).mean(1)-xm))/12))
    constantx=torch.zeros_like(x); constanty=torch.ones_like(y)
    cm,cl=affine.fit(constantx,constanty,w,100.,'JA1')
    check('constant dimensions identity prior and intercept',torch.allclose(cm['matrix'],torch.eye(96,device=device(),dtype=torch.float64)) and torch.allclose(cm['bias'],torch.ones(96,device=device(),dtype=torch.float64)))
    big,bl=affine.fit(x,y,w,1e8,'JA1')
    check('strong prior means shift not raw pre',float((big['matrix']-torch.eye(96,device=device(),dtype=torch.float64)).abs().max())<1e-6 and float(big['bias'].abs().max())>.1)
    for identity in ['visit_id','session_id','pair_id','repetition','carrier_id','shared_row_index']:
        wrong=gp.copy(); wrong[identity]='forbidden'
        try:group_schema(wrong)
        except RuntimeError:access.append({'name':'reject '+identity,'passed':True})
        else:raise RuntimeError('Identity not rejected: '+identity)
    negatives=[('C rejects U',lambda:validate_scope(pd.DataFrame({'content_id':['U'],'protocol':['target']}),
                      {'kind':'C-post','scope':{'C_contents':['C'],'calibration':'target'}})),
        ('training rejects heldout',lambda:validate_scope(pd.DataFrame({'content_id':['heldout'],'protocol':['source']}),
                      {'kind':'source-pre','scope':{'train_contents':['train'],'sources':['source']}})),
        ('inner source rejects actual target',lambda:validate_scope(pd.DataFrame({'content_id':['train'],'protocol':['actual-target']}),
                      {'kind':'source-post','scope':{'train_contents':['train'],'sources':['source']}})),
        ('group worker rejects true C',lambda:check_permission('JA-C-paired','group-map')),
        ('fit worker rejects test pre',lambda:check_permission('main-test-paired','source-fit')),
        ('selector rejects outer labels',lambda:check_permission('main-outer-labels','select'))]
    for name,call in negatives:
        try:call()
        except RuntimeError:access.append({'name':name,'passed':True})
        else:raise RuntimeError('Permission negative accepted: '+name)
    bad=pd.DataFrame(np.zeros((1,96)),columns=HIST);bad['visit_id']='x';bad['pre_h00_00']=1
    try:base.validate_query(bad)
    except RuntimeError:access.append({'name':'test pre injection rejected','passed':True})
    else:raise RuntimeError('Unsafe query accepted')
    write(OUT/'manifests/affine-tests.json',{'passed':True,'checks':rows,'CUDA':True,'fit_count':12})
    write(OUT/'manifests/access-tests.json',{'passed':True,'checks':access,'OS_sandbox':False})
    progress('JA_affine_tests_passed',checks=len(rows),access_checks=len(access))

if __name__=='__main__':run()
