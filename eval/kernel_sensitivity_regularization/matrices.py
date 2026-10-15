"""CUDA conditional covariance factors; no labels participate in estimation."""
from common import *

def weighted_bins(index,weight,bins):
    # No atomic weighted bincount: this CUDA GEMV has deterministic float64 reduction.
    return F.one_hot(index,num_classes=bins).to(torch.float64).T@weight

def conditional_factor(k,nu):
    require(k.dtype==torch.float64 and k.is_cuda and nu.is_cuda,'CUDA float64 matrices required')
    require(bool((k>=0).all()) and bool((nu>=0).all()),'Negative kernel/frequency')
    require(torch.allclose(k.sum(1),torch.ones_like(nu),atol=1e-12,rtol=0),'Kernel rows not normalized')
    require(abs(float(nu.sum())-1)<1e-12,'nu not normalized')
    q=k.sqrt(); eye=torch.eye(k.shape[1],device=cuda(),dtype=torch.float64)
    factors=[nu[a].sqrt()*torch.diag(q[a])@(eye-q[a,:,None]@q[a,None,:]) for a in range(len(nu))]
    factor=torch.cat(factors,1)
    direct=torch.diag(nu@k)-k.T@(nu[:,None]*k)
    require(float((factor@factor.T-direct).abs().max())<1e-11,'Conditional formula/factor mismatch')
    return factor,direct

def normalize(factor):
    trace=factor.square().sum()
    multiplier=torch.ones((),device=cuda(),dtype=torch.float64) if float(trace)==0 else 96/trace
    normalized=factor*multiplier.sqrt()
    require(bool(torch.isfinite(normalized).all()),'Nonfinite normalized factor')
    return normalized,float(trace),float(multiplier)

def descriptor(matrix):
    eig=torch.linalg.eigvalsh(matrix); tolerance=1e-10*max(1,float(eig.max()))
    require(float(eig.min())>=-tolerance,'PSD gate failed')
    require(float((matrix-matrix.T).abs().max())<=tolerance,'Symmetry gate failed')
    pos=eig.clamp_min(0); p=pos/pos.sum() if float(pos.sum()) else pos
    erank=float(torch.exp(-(p[p>0]*p[p>0].log()).sum())) if bool((p>0).any()) else 0.
    return {'trace':float(matrix.trace()),'min_eigenvalue':float(eig.min()),
            'max_eigenvalue':float(eig.max()),'eigenvalues':eig.cpu().tolist(),
            'numerical_rank':int((eig>tolerance).sum()),'effective_rank':erank,'PSD_tolerance':tolerance,
            'symmetry_error':float((matrix-matrix.T).abs().max())}

def build_kernel(pre,post,group_pre,group_post,feature):
    # The paired estimator joins only the authorized training identities.
    require(set(pre.pair_id)==set(post.pair_id),'Training pair sets differ')
    post=post.set_index('pair_id').loc[pre.pair_id].reset_index()
    k=size(feature); a=tensor(encode(pre['pre_'+feature],feature),torch.int64)
    b=tensor(encode(post['post_'+feature],feature),torch.int64); w=tensor(pre.fit_mass)
    true=weighted_bins(a*k+b,w,k*k).reshape(k,k)
    require(set(group_pre)=={'content_id','fit_mass',*['pre_'+f for f in FEATURES]},'Anonymous pre identity leak')
    require(set(group_post)=={'content_id','fit_mass',*['post_'+f for f in FEATURES]},'Anonymous post identity leak')
    contents=sorted(group_pre.content_id.unique()); mapping={u:i for i,u in enumerate(contents)}
    counts=[]
    for side,df in [('pre',group_pre),('post',group_post)]:
        g=tensor(df.content_id.map(mapping),torch.int64)
        z=tensor(encode(df[side+'_'+feature],feature),torch.int64)
        counts.append(weighted_bins(g*k+z,tensor(df.fit_mass),len(contents)*k).reshape(-1,k))
    ca,cb=counts; group=ca.T@(cb/ca.sum(1)[:,None])
    require(float((true.sum(0)-group.sum(0)).abs().max())<1e-10 and
            float((true.sum(1)-group.sum(1)).abs().max())<1e-10,'True/group resource marginal mismatch')
    nu=true.sum(1)/true.sum()
    bundle={'true_counts':true,'group_counts':group,'nu':nu,'feature':feature}
    for name,c in [('M1',true),('M2',group)]:
        qb=(c.sum(0)+1/k)/(c.sum()+1)
        bundle[name]=(c+qb)/(c.sum(1)[:,None]+1)
    return bundle

def regularizers(bundles,hist,scale):
    require(set(hist)=={'content_id',*HIST},'Matrix hist may not read labels/session identities')
    require(hist.groupby('content_id').size().eq(4).all(),'Expected four repeats per content')
    all_factors={'KSR2':[],'KSR3':[],'KSR4':[],'empirical':[]}; block_rows=[]; at=0
    for j,f in enumerate(FEATURES):
        k=size(f); bundle=bundles[f]; nu=bundle['nu']; block={}
        for arm,kn in [('KSR2','M1'),('KSR3','M2')]:
            block[arm],_=conditional_factor(bundle[kn],nu)
        c=bundle['true_counts']; denom=c.sum(1)
        empirical=torch.where(denom[:,None]>0,c/denom.clamp_min(1e-300)[:,None],bundle['M1'])
        block['empirical'],_=conditional_factor(empirical,nu)
        residual=[]
        for _,df in hist.groupby('content_id',sort=True):
            h=tensor(df[HIST[at:at+k]]); residual.append((h-h.mean(0)).T)
        block['KSR4']=torch.cat(residual,1)/np.sqrt(len(residual)*4)
        for arm,l in block.items():
            raw=l*np.sqrt(WEIGHTS[j]); scaled=raw/scale[at:at+k,None]
            full=torch.zeros((96,scaled.shape[1]),device=cuda(),dtype=torch.float64)
            full[at:at+k]=scaled; all_factors[arm].append(full)
            gh=raw@raw.T; gx=scaled@scaled.T
            require(float((gh@torch.ones(k,device=cuda(),dtype=torch.float64)).abs().max())<1e-10,'Raw null vector failed')
            require(float((gx@scale[at:at+k]).abs().max())<1e-8,'Standardized null D1 failed')
            block_rows.append({'arm':arm,'feature':f,'hist_trace':float(gh.trace()),
                 'standardized_trace':float(gx.trace()),'supported_pre_bins':int((nu>0).sum()),
                 'missing_pre_bins':int((nu==0).sum()),'nu':nu.cpu().tolist()})
        at+=k
    artifacts={}; summaries=[]
    for arm,parts in all_factors.items():
        l=torch.cat(parts,1); norm,tr,mult=normalize(l); m=l@l.T; mn=norm@norm.T
        # Reduced QR preserves the known PSD construction and avoids eigenvalue clipping.
        _,r=torch.linalg.qr(norm.T,mode='reduced'); compact=r.T
        err=float((compact@compact.T-mn).abs().max())
        require(err<1e-9,'Factor compression mismatch')
        artifacts[arm]={'factor':compact,'uncompressed_factor':norm,'matrix_x':m,'normalized_matrix':mn,
                        'trace':tr,'multiplier':mult}
        summaries.append({'arm':arm,'raw':descriptor(m),'normalized':descriptor(mn),
                          'trace_multiplier':mult,'factor_compression_error':err})
    sm=artifacts['KSR2']['matrix_x']; em=artifacts['empirical']['matrix_x']
    return artifacts,{'spectra':summaries,'blocks':block_rows,
          'smoothing_difference_Frobenius':float(torch.linalg.matrix_norm(sm-em)),
          'theoretical_smoothed_rank':86,'rank_is_not_observed_noise_dimension':True}

def tests():
    configure(); checks=[]
    def check(name,ok): require(ok,name); checks.append(name)
    nu=tensor([.2,.3,.5]); k=tensor([[1.,0,0],[0,0,1],[0,1,0]])
    l,m=conditional_factor(k,nu); check('deterministic displaced kernel zero',float(l.abs().max())==0)
    k=tensor([[.5,.5,0],[0,.25,.75],[.2,.3,.5]])
    l,m=conditional_factor(k,nu)
    hand=sum(float(nu[a])*(torch.diag(k[a])-k[a,:,None]@k[a,None,:]) for a in range(3))
    check('three bin manual covariance',torch.allclose(m,hand,atol=1e-14))
    check('same nu K marginal',torch.allclose(m,torch.diag(nu@k)-k.T@torch.diag(nu)@k,atol=1e-14))
    check('PSD and symmetry',descriptor(m)['min_eigenvalue']>=-1e-12)
    check('raw constant null',float((m@tensor([1,1,1])).abs().max())<1e-14)
    d=tensor([.2,2,3]); lx=l/d[:,None]; mx=lx@lx.T
    check('standardized null D1',float((mx@d).abs().max())<1e-14)
    z=tensor([2,3,4]); check('coordinate quadratic equivalence',abs(float(z@mx@z-(z/d)@m@(z/d)))<1e-12)
    ll=torch.zeros((96,lx.shape[1]),device=cuda(),dtype=torch.float64); ll[:3]=lx
    norm,tr,mult=normalize(ll); check('trace matching',abs(float(norm.square().sum())-96)<1e-12)
    zeros=torch.zeros((96,96),device=cuda(),dtype=torch.float64)
    zero,ztr,zmult=normalize(zeros); check('exact zero no divide',bool(torch.isfinite(zero).all()) and ztr==0 and zmult==1)
    w=tensor(np.arange(576).reshape(6,96)/100).requires_grad_()
    r=sensitivity(w,norm); grad=torch.autograd.grad(r,w)[0]
    analytic=2/5*(w-w.mean(0,keepdim=True))@(norm@norm.T)
    check('autograd analytic gradient',float((grad-analytic).abs().max())<1e-10)
    check('common class offset invariance',abs(float(sensitivity(w+tensor(np.arange(96))[None],norm)-r))<1e-10)
    centered=w-w.mean(0,keepdim=True)
    check('factor quadratic equivalence',abs(float(r-(centered@(norm@norm.T)*centered).sum()/5))<1e-10)
    x=tensor(np.zeros((2,96))); y=tensor([0,1],torch.int64); b=tensor(np.zeros(6))
    base=loss(w,b,x,y,'KSR0',0)
    check('four arms exact zero branch',all(torch.equal(loss(w,b,x,y,a,0,None),base) for a in ARMS))
    for col in ['pre_W_up','label_id','content_id','SNI']:
        try: probabilities({},pd.DataFrame(columns=['visit_id',*HIST,col])); ok=False
        except RuntimeError: ok=True
        check('post query rejects '+col,ok)
    try: outer_kernel({'inner':1},'W_up',{}); ok=False
    except RuntimeError: ok=True
    check('inner outer-kernel read rejected before IO',ok)
    rawcoef=tensor(np.arange(18).reshape(6,3)/10)
    rawcoef=rawcoef-rawcoef.mean(0,keepdim=True)
    pairwise=torch.zeros((),device=cuda(),dtype=torch.float64)
    for a in range(3):
        for b0 in range(3):
            for b1 in range(3):
                pairwise+=nu[a]*k[a,b0]*k[a,b1]*(rawcoef[:,b0]-rawcoef[:,b1]).square().sum()/10
    check('pairwise coefficient 1 over 10',abs(float(pairwise-(rawcoef@m*rawcoef).sum()/5))<1e-12)
    check('deterministic weighted bin reduction',torch.equal(weighted_bins(tensor([0,1,0],torch.int64),tensor([.25,.5,.25]),3),tensor([.5,.5,0])))
    write(OUT/'manifests/unit-tests.json',{'passed':True,'checks':checks,'device':'cuda:0','dtype':'float64'})
    print('CUDA matrix tests passed',len(checks),flush=True)
