"""Fixed frequency-coordinate anchors, no labels or classifier input."""
from common import *

def distance(a,b):return torch.linalg.vector_norm(b-a,dim=-1)/np.sqrt(2.)
def qtile(values,q=.9):
    # Every elementary observation has equal mass by construction.
    v=values.flatten();require(len(v)>0 and torch.isfinite(v).all(),'Invalid quantile observations')
    return float(v.sort().values[max(0,int(np.ceil(q*len(v)))-1)])
def arrays(d,paired=False):
    require('content_token' in d,'Missing anonymous content grouping')
    if paired:
        require(set(d)=={'content_token','query_key','fit_mass',*['pre_'+h for h in HIST],*['post_'+h for h in HIST]},'Paired anchor schema')
        return tensor(d[['pre_'+h for h in HIST]]),tensor(d[['post_'+h for h in HIST]])
    require(set(d)<=set(['content_token','query_key','fit_mass',*HIST]),'Anonymous anchor schema')
    return tensor(d[HIST])
def validate_hist(x):
    require(x.is_cuda and x.dtype==torch.float64 and x.ndim==2 and x.shape[1]==96,'Raw histogram shape/device')
    require(torch.isfinite(x).all() and (x>=0).all(),'Invalid frequency values')
    for j in range(10):require(float((x[:,block(j)].sum(1)-1).abs().max())<1e-12,'Histogram block mass')
def observations(a,b,ta,tb=None):
    if tb is None:return a,b,np.asarray(ta)
    aa=[];bb=[];uu=[]
    for u in sorted(set(ta)):
        ix=np.flatnonzero(np.asarray(ta)==u);iy=np.flatnonzero(np.asarray(tb)==u)
        require(len(ix)==len(iy)==4,'Four anonymous repetitions per content')
        aa.append(a[ix].repeat_interleave(4,dim=0));bb.append(b[iy].repeat((4,1)));uu.extend([u]*16)
    return torch.cat(aa),torch.cat(bb),np.asarray(uu)
def variation(x,tokens,j):
    z=torch.stack([x[np.flatnonzero(np.asarray(tokens)==u),block(j)].mean(0) for u in sorted(set(tokens))])
    require(len(z)>1,'Too few contents for nontriviality')
    return qtile(torch.pdist(z)/np.sqrt(2.))
def rules(a,b,ta,tb=None):
    validate_hist(a);validate_hist(b)
    require(all(np.sum(np.asarray(ta)==u)==4 for u in set(ta)),'Pre repetitions')
    if tb is not None:require(set(ta)==set(tb),'Group membership')
    aa,bb,_=observations(a,b,ta,tb);result=[]
    for j in range(10):
        vp=variation(a,ta,j);vb=variation(b,ta if tb is None else tb,j);v=min(vp,vb)
        delta=distance(aa[:,block(j)],bb[:,block(j)]);eps=qtile(delta)
        ratio=eps/v if v>0 else None
        reasons=[]
        if v<RULE['variation_min']:reasons.append('nontriviality')
        if eps>RULE['epsilon_max']:reasons.append('absolute_change')
        if ratio is None or ratio>RULE['epsilon_variation_ratio_max']:reasons.append('relative_change')
        result.append({'block':j,'feature':FEATURES[j],'epsilon':eps,'variation':v,'pre_variation':vp,
                       'post_variation':vb,'epsilon_variation_ratio':ratio,'train_eligible':not reasons,
                       'reasons':reasons,'train_median':qtile(delta,.5),'train_Q95':qtile(delta,.95),
                       'train_max':float(delta.max()),'observations':len(delta)})
    return result
