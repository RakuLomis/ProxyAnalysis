"""New blocks only; frozen 96D maps and original targets remain untouched."""
from common import *

def root(matrix,power):
    e,v=torch.linalg.eigh((matrix+matrix.T)/2); require((e>0).all(),'Covariance not SPD; no dynamic jitter')
    return (v*e.pow(power))@v.T

def blocks(d):return [slice(0,96)]+[slice(96+slice_joint(g).start,96+slice_joint(g).stop) for g in range(4)] if d==162 else [slice(0,96)]

def coral(x,source,cx,cp,missing):
    output=x.clone(); parameters={}
    for protocol in sorted(source.protocol.unique()):
        ix=np.flatnonzero(source.protocol.eq(protocol)); yi=truths(source.iloc[ix]); match=~np.isin(yi,missing)
        parameters[protocol]=[]
        for sl in blocks(x.shape[1]):
            a=x[ix][match][:,sl]; b=cx[:,sl]; am=a.mean(0); bm=b.mean(0)
            ac=(a-am).T@(a-am)/(len(a)-1); bc=(b-bm).T@(b-bm)/(len(b)-1)
            eye=torch.eye(len(am),device=device(),dtype=torch.float64)
            matrix=root(ac+eye,-.5)@root(bc+eye,.5)
            output[ix,sl]=(x[ix,sl]-am)@matrix+bm
            parameters[protocol].append({'matrix':matrix,'source_mean':am,'target_mean':bm})
    require(torch.isfinite(output).all(),'Nonfinite CORAL')
    return output,parameters

def affine(x,y,w,eta,constant=0.):
    k=x.shape[1]; mx=w@x; my=w@y; xc=x-mx; yc=y-my
    sxx=xc.T@(xc*w[:,None]); syx=yc.T@(xc*w[:,None]); tau=max(float(sxx.trace())/k,1e-12); alpha=eta*tau
    eye=torch.eye(k,device=device(),dtype=torch.float64); equation=sxx+alpha*eye; rhs=syx+alpha*eye
    matrix=torch.cholesky_solve(rhs.T,torch.linalg.cholesky(equation)).T; bias=my-matrix@mx
    mm=matrix.detach().clone().requires_grad_(); bb=bias.detach().clone().requires_grad_()
    rec=((x@mm.T+bb-y).square()*w[:,None]).sum()/k+constant/k
    reg=alpha*(mm-eye).square().sum()/k; gm,gb=torch.autograd.grad(rec+reg,(mm,bb))
    rawxx=sxx+mx[:,None]*mx[None,:]; rawyx=syx+my[:,None]*mx[None,:]
    replay=(torch.trace(matrix@rawxx@matrix.T)+2*bias@(matrix@mx)+bias.square().sum()
        -2*(matrix*rawyx).sum()-2*bias@my+(y*y*w[:,None]).sum()+constant+alpha*(matrix-eye).square().sum())/k
    agm=2*(matrix@rawxx+bias[:,None]*mx[None,:]-rawyx+alpha*(matrix-eye))/k
    agb=2*(matrix@mx+bias-my)/k
    error=abs(float(replay)-float(rec+reg)); gerror=max(float((agm-gm).abs().max()),float((agb-gb).abs().max()))
    gradient=max(float(gm.abs().max()),float(gb.abs().max()))
    equation_error=float((matrix@equation-rhs).abs().max())/max(1.,float(rhs.abs().max()))
    log={'eta':eta,'tau':tau,'alpha':alpha,'dimensions':k,'parameters':k*(k+1),'recovery':float(rec.detach()),
         'regularization':float(reg.detach()),'group_constant':constant,'gradient_max':gradient,
         'objective_replay_error':error,'gradient_replay_error':gerror,'normalized_equation_residual':equation_error,
         'device':'cuda:0','dtype':'float64','accepted':gradient<=1e-8 and error<1e-10 and gerror<1e-10 and equation_error<=1e-10}
    require(log['accepted'],'New affine block gate failed')
    return {'matrix':matrix.detach(),'bias':bias.detach()},log

def anonymous_moment_map(a,b,wa,wb):
    ma=wa@a; mb=wb@b
    ca=(a-ma).T@((a-ma)*wa[:,None])/(1-wa.square().sum())
    cb=(b-mb).T@((b-mb)*wb[:,None])/(1-wb.square().sum())
    eye=torch.eye(a.shape[1],device=device(),dtype=torch.float64)
    m=root(ca+eye,-.5)@root(cb+eye,.5)
    error=float((m.T@(ca+eye)@m-(cb+eye)).abs().max())/max(1.,float((cb+eye).abs().max()))
    require(error<1e-10,'Anonymous covariance congruence')
    return {'matrix':m.T,'bias':mb-ma@m}, {'congruence_error':error,'cross_side_covariance_used':False}

def mapped_views(r,mu,scale,rawpre):
    cols=INPUTS['J']; rootdir=rolepath(r); views={}; old=artifact(ROOT/r['reuse_views'])
    require(torch.equal(mu[:96],old['mu']) and torch.equal(scale[:96],old['scale']),'Frozen coordinate compatibility')
    paired=package(rootdir/'C-paired.parquet','paired-map')
    x=(tensor(paired[['pre_'+h for h in cols]])-mu)/scale
    y=(tensor(paired[['post_'+h for h in cols]])-mu)/scale; w=tensor(paired.fit_mass)
    gp=package(rootdir/'C-group-pre.parquet','group-map'); gb=package(rootdir/'C-group-post.parquet','group-map')
    gx=(tensor(gp[cols])-mu)/scale; gz=(tensor(gb[cols])-mu)/scale; gw=tensor(gp.fit_mass)
    centers={}; constants={}
    for content in sorted(gb.content_token.unique()):
        ix=np.flatnonzero(gb.content_token.eq(content)); local=tensor(gb.fit_mass.iloc[ix]); local=local/local.sum()
        centers[content]=local@gz[ix]
    gy=torch.stack([centers[u] for u in gp.content_token])
    ap=package(rootdir/'C-marginal-pre.parquet','marginal-map'); ab=package(rootdir/'C-marginal-post.parquet','marginal-map')
    ax=(tensor(ap[cols])-mu)/scale; ay=(tensor(ab[cols])-mu)/scale
    aw=tensor(ap.fit_mass); bw=tensor(ab.fit_mass)
    logs=[]
    for arm,key in [('P','P'),('G','G'),('Marginal','Marginal')]:
        oldmap=artifact(ROOT/(r['reuse_marginal'] if arm=='Marginal' else r['reuse_maps'][key]))
        result=rawpre.clone(); result[:,:96]=rawpre[:,:96]@oldmap['matrix'].T+oldmap['bias']
        for g in range(4):
            sl=slice(96+slice_joint(g).start,96+slice_joint(g).stop)
            if arm=='P':m,log=affine(x[:,sl],y[:,sl],w,r['eta'])
            elif arm=='G':
                constant=0.
                for content,center in centers.items():
                    ix=np.flatnonzero(gb.content_token.eq(content)); ww=tensor(gb.fit_mass.iloc[ix])
                    constant+=float(((gz[ix,sl]-center[sl]).square()*ww[:,None]).sum())
                m,log=affine(gx[:,sl],gy[:,sl],gw,r['eta'],constant)
            else:m,log=anonymous_moment_map(ax[:,sl],ay[:,sl],aw,bw)
            p=OUT/'mappings'/r['id']/f'{arm}-{g}.pt'
            if p.with_suffix('.json').exists():m=artifact(p)
            else:put(m,p,mapping=log,role_id=r['id'],block=g,arm=arm)
            result[:,sl]=rawpre[:,sl]@m['matrix'].T+m['bias']; logs.append({'arm':arm,'block':g,**log})
        require(torch.isfinite(result).all(),'Mapped views finite'); views[arm]=result
    write(OUT/'audits/mappings'/r['id']/'blocks.json',logs)
    return views
