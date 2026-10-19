"""Data-independent raw-frequency mass, location and residual subspaces."""
from common import *

def projectors():
    result=[]
    for n in SIZES:
        one=torch.ones(n,device=device(),dtype=torch.float64)/np.sqrt(n)
        loc=torch.linspace(0,1,n,device=device(),dtype=torch.float64)
        loc=(loc-loc.mean()); loc=loc/loc.norm()
        pm=one[:,None]@one[None,:]; pl=loc[:,None]@loc[None,:]
        result.append((pm,pl,torch.eye(n,device=device(),dtype=torch.float64)-pm-pl))
    return result

def mix_shape(p,g,scale,ps):
    require(p.shape==g.shape and p.shape[1]==96 and bool((scale>0).all()), 'Mix dimensions/scale')
    delta=scale*(g-p); residual=torch.empty_like(delta)
    for j,(_,_,pr) in enumerate(ps): residual[:,block(j)]=delta[:,block(j)]@pr
    return dict(PP=p,PG=p+residual/scale,GP=g-residual/scale,GG=g)

def geometry(p,g,mu,scale,ps):
    m=mix_shape(p,g,scale,ps); raw={k:mu+scale*x for k,x in m.items()}; rows=[]
    def check(name,a,b):
        absolute,normalized=error(a,b)
        rows.append(dict(check=name,absolute_error=absolute,normalized_error=normalized,passed=normalized<1e-10))
        require(normalized<1e-10, 'Geometry failed: '+name)
    check('sum',m['PG']+m['GP'],p+g)
    swapped=mix_shape(g,p,scale,ps)
    check('swap-PG',m['PG'],swapped['GP']);check('swap-GP',m['GP'],swapped['PG'])
    identical=mix_shape(p,p,scale,ps)
    for k in ARMS: check('identity-'+k,identical[k],p)
    require(m['PP'] is p and m['GG'] is g,'PP/GG must bypass reconstruction')
    for j,(pm,pl,pr) in enumerate(ps):
        sl=block(j); pml=pm+pl
        check(f'raw-PG-{j}',raw['PG'][:,sl],raw['PP'][:,sl]@pml+raw['GG'][:,sl]@pr)
        check(f'raw-GP-{j}',raw['GP'][:,sl],raw['GG'][:,sl]@pml+raw['PP'][:,sl]@pr)
        for arm,ml,rr in [('PG','PP','GG'),('GP','GG','PP')]:
            check(f'{arm}-ML-{j}',raw[arm][:,sl]@pml,raw[ml][:,sl]@pml)
            check(f'{arm}-R-{j}',raw[arm][:,sl]@pr,raw[rr][:,sl]@pr)
    return m,rows

def synthetic_tests():
    ps=projectors();gen=torch.Generator(device=device()).manual_seed(20261016)
    p=torch.randn((11,96),device=device(),dtype=torch.float64,generator=gen)
    g=torch.randn((11,96),device=device(),dtype=torch.float64,generator=gen)
    scale=torch.linspace(.02,3,96,device=device(),dtype=torch.float64)
    mu=torch.linspace(-.1,1,96,device=device(),dtype=torch.float64)
    m,rows=geometry(p,g,mu,scale,ps)
    for j,(pm,pl,pr) in enumerate(ps):
        eye=torch.eye(SIZES[j],device=device(),dtype=torch.float64)
        for name,a,b in [('orthogonal',pm@pr+pl@pr,torch.zeros_like(pr)),('complete',pm+pl+pr,eye),('idempotent',pr@pr,pr)]:
            ae,ne=error(a,b);require(ne<1e-10,'Synthetic basis')
            rows.append(dict(check=f'{name}-{j}',absolute_error=ae,normalized_error=ne,passed=True))
    wrong=p.clone()
    for j,(_,_,pr) in enumerate(ps):wrong[:,block(j)]+=(g-p)[:,block(j)]@pr
    gap=float((wrong-m['PG']).abs().max());require(gap>1e-3,'Nonuniform-scale negative fixture ineffective')
    rows.append(dict(check='reject-standardized-projection',absolute_error=gap,normalized_error=gap,passed=True))
    # The mixing API has no query, label, metadata or observed-post argument.
    import inspect
    require(list(inspect.signature(mix_shape).parameters)==['p','g','scale','ps'],'Mix dependency boundary')
    return rows
