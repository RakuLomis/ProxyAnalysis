"""Synthetic geometry, invariance fallacies, and worker access negative tests."""
from common import *
from anchors import rules,validate_hist,distance
from guard import project,uniform
from affine import fit,group_targets

def checks():
    configure();count=0
    def check(ok,msg):
        nonlocal count
        require(ok,msg);count+=1
    rng=np.random.default_rng(20261012)
    a=tensor(np.concatenate([rng.dirichlet(np.ones(n),size=200) for n in SIZES],axis=1))
    b=a+tensor(rng.normal(size=(200,96)));rr=[{'block':j,'epsilon':.07,'train_eligible':j%2==0} for j in range(10)]
    z=project(a,b,rr);u,g=uniform(a,b,z)
    for j in range(10):
        sl=block(j)
        if j%2==0:check(float(distance(a[:,sl],z[:,sl]).max())<=.07+1e-12,'Ball violation')
        else:check(torch.equal(z[:,sl],b[:,sl]),'Unprotected block changed')
    check(float((torch.linalg.vector_norm(z-a,dim=1)-torch.linalg.vector_norm(u-a,dim=1)).abs().max())<1e-10,'Uniform radius')
    check(torch.equal(project(a,a,rr),a),'Zero displacement')
    check(torch.equal(project(a,b,rr,active=[]),b),'Empty anchors')
    infinite=[dict(v,epsilon=float('inf')) for v in rr]
    check(torch.equal(project(a,b,infinite),b),'Infinite radius')
    mu=tensor(rng.normal(size=96));sc=tensor(rng.uniform(.1,3,size=96))
    check(float((((z-mu)/sc)*sc+mu-z).abs().max())<1e-12,'Raw/standardized roundtrip')
    # Exact identity can be nontrivial; a constant or offset relation is not automatically an anchor.
    x=torch.zeros((48,96),device=device(),dtype=torch.float64)
    for j in range(10):
        t=torch.linspace(.1,.9,12,device=device(),dtype=torch.float64).repeat_interleave(4)
        x[:,block(j).start]=t;x[:,block(j).start+1]=1-t
    tok=np.repeat([f'c{k:02d}' for k in range(12)],4)
    identity=rules(x,x,tok)
    check(all(v['train_eligible'] and v['epsilon']==0 for v in identity),'Nontrivial exact identity rejected')
    y=x.clone()
    for j in range(10):y[:,block(j).start]+= .2;y[:,block(j).start+1]-=.2
    # Keep this counterexample valid by constructing a separate domain away from zero.
    xc=x.clone()
    for j in range(10):
        t=torch.linspace(.35,.65,12,device=device(),dtype=torch.float64).repeat_interleave(4)
        xc[:,block(j).start]=t;xc[:,block(j).start+1]=1-t
    yc=xc.clone()
    for j in range(10):yc[:,block(j).start]+=.2;yc[:,block(j).start+1]-=.2
    check(all(not v['train_eligible'] for v in rules(xc,yc,tok)),'Large high-correlation offset accepted')
    alternating=xc.clone();sign=tensor(np.tile([1,-1,1,-1],12))*.2
    for j in range(10):alternating[:,block(j).start]+=sign;alternating[:,block(j).start+1]-=sign
    check(all(not v['train_eligible'] for v in rules(xc,alternating,tok)),'Zero-mean large change accepted')
    const=xc[:1].expand_as(xc).clone()
    check(all(not v['train_eligible'] for v in rules(xc,const,tok)),'Constant target accepted')
    check(all(not v['train_eligible'] for v in rules(const,const,tok)),'Block mass pseudo-anchor accepted')
    for k in range(100):
        ix=rng.permutation(48);iy=rng.permutation(48)
        r1=rules(xc,yc,tok,tok);r2=rules(xc[ix],yc[iy],tok[ix],tok[iy])
        for v,w in zip(r1,r2):
            check(abs(v['epsilon']-w['epsilon'])<1e-12 and v['train_eligible']==w['train_eligible'],'Anonymous permutation changed rule')
    gt,con=group_targets(xc,yc,tok,tok)
    m,log=fit(xc,yc,1.);mg,lg=fit(xc,gt,1.,con)
    check(log['accepted'] and lg['accepted'],'Synthetic affine gate')
    df=pd.DataFrame(xc.cpu().numpy(),columns=HIST);df['content_token']=tok;df['label_id']='forbidden'
    from anchors import arrays
    try:arrays(df);raise AssertionError('Anonymous labels accepted')
    except RuntimeError:count+=1
    return {'passed':True,'checks':count,'device':'cuda:0','dtype':'float64','classifier_fits':0}

def run():
    with stage('tests'):
        result=checks();r=contract()['roles'][0];root=rolepath(r)/'i0'
        for path,purpose in [(root/'P-fit.parquet','G-fit'),(root/'P-score.parquet','P-score'),
                             (root/'G-post-validation.parquet','G-score'),(root/'P-query.parquet','G-query')]:
            try:package(path,purpose);raise AssertionError('Forbidden package accepted')
            except RuntimeError:result['checks']+=1
        # H and U are not registered under any stage-one package purpose.
        try:parent_package(PREP/'packages'/r['id']/'query.parquet','trusted-C-source-packer');raise AssertionError('H query accepted')
        except RuntimeError:result['checks']+=1
        try:parent_package(ROOT/r['C_paired'],'G-fit');raise AssertionError('Group opened paired parent')
        except RuntimeError:result['checks']+=1
        write(OUT/'audits/tests.json',result);print(result,flush=True)

if __name__=='__main__':
    if '--preflight' in sys.argv:print(checks(),flush=True)
    else:run()
