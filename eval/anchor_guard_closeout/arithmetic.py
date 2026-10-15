"""Independent equations, no calls to the parent rules/project/score functions."""
from common import *

def distance(a,b):return torch.sqrt(torch.sum((b-a)**2,dim=-1)/2)
def quantile(v,q=.9):
    n=v.numel();need(n>0 and bool(torch.isfinite(v).all()),'Quantile inputs')
    rank=int(np.ceil(q*n));return float(torch.sort(v.reshape(-1))[0][rank-1])
def raw(d,side=None):return t(d[HIST if side is None else [side+'_'+h for h in HIST]])
def cross_indices(ta,tb):
    ia=[];ib=[];tokens=[]
    need(set(ta)==set(tb),'Anonymous content mismatch')
    for u in sorted(set(ta)):
        x=np.flatnonzero(np.asarray(ta)==u);y=np.flatnonzero(np.asarray(tb)==u);need(len(x)==len(y)==4,'Group multiplicity')
        for a in x:
            for b in y:ia.append(a);ib.append(b);tokens.append(u)
    return ia,ib,np.asarray(tokens)
def independent_rules(a,b,ta,tb=None):
    nc=len(set(ta));need(nc in {12,16},'Rules must use exact registered C scope')
    if tb is None:aa,bb=a,b
    else:ix,iy,_=cross_indices(ta,tb);aa,bb=a[ix],b[iy]
    results=[]
    for j in range(10):
        centers=[]
        for z,u in [(a,ta),(b,ta if tb is None else tb)]:
            means=torch.stack([z[np.flatnonzero(np.asarray(u)==v),sl(j)].mean(0) for v in sorted(set(u))])
            pair=torch.triu_indices(nc,nc,offset=1,device='cuda:0');dist=distance(means[pair[0]],means[pair[1]])
            centers.append(quantile(dist))
        v=min(centers);d=distance(aa[:,sl(j)],bb[:,sl(j)]);epsilon=quantile(d);ratio=epsilon/v if v>0 else None
        eligible=v>=.1 and epsilon<=.1 and ratio is not None and ratio<=.5
        results.append({'block':j,'epsilon':epsilon,'pre_variation':centers[0],'post_variation':centers[1],'variation':v,
                        'epsilon_variation_ratio':ratio,'train_eligible':eligible,'observations':len(d),
                        'train_median':quantile(d,.5),'train_Q95':quantile(d,.95),'train_max':float(d.max()),
                        'Q90_rank':int(np.ceil(.9*len(d))),'content_distance_count':nc*(nc-1)//2,
                        'content_Q90_rank':int(np.ceil(.9*nc*(nc-1)/2))})
    return results
def projection(a,b,epsilon):
    d=b-a;n=torch.sqrt(torch.sum(d*d,dim=1));radius=np.sqrt(2)*epsilon
    factor=torch.ones_like(n);hit=n>radius;factor[hit]=radius/n[hit]
    return torch.where(hit[:,None],a+d*factor[:,None],b)
def prepare_pairs(pred,scored,arm):
    if arm=='P':
        ordered=scored.set_index('query_key').loc[pred['query_keys']]
        need(ordered.content_token.tolist()==pred['content_tokens'],'P routing alignment')
        return pred['a'],raw(ordered),pred['b0'],pred['candidate_guard'],pred['train_guard'],np.asarray(pred['content_tokens'])
    ia,ib,u=cross_indices(pred['content_tokens'],scored.content_token.to_numpy())
    return pred['a'][ia],raw(scored)[ib],pred['b0'][ia],pred['candidate_guard'][ia],pred['train_guard'][ia],u
def losses(v,b,scale):
    error=(v-b)**2
    return error.mean(1),(error/(scale**2)).mean(1)

def tests():
    configure();a=t(np.tile([.5,.5],(4,1)));b=t([[.55,.45],[.55,.45],[.8,.2],[.8,.2]])
    m=t([[.58,.42],[.8,.2],[.58,.42],[.9,.1]]);dr=distance(a,b);dm=distance(a,m)
    need([(bool(x<=.1+1e-12),bool(y<=.1+1e-12)) for x,y in zip(dr,dm)]==[(True,True),(True,False),(False,True),(False,False)],'Four-quadrant fixture')
    z=projection(a,m,.1);r0,s0=losses(m,b,t([1.,1.]));r1,s1=losses(z,b,t([1.,1.]))
    need(float(r1[1]-r0[1])<0 and float(r1[3]-r0[3])>0,'IO correction / OO adverse case')
    need(torch.equal(z[0],m[0]) and torch.equal(z[2],m[2]),'Inside no-op')
    aa=t([[.4,.3,.3]]);bb=t([[.48,.3,.22]]);mm=t([[.44,.5,.06]]);zz=projection(aa,mm,.1)
    r0,s0=losses(mm,bb,t([.001,1.,1.]));r1,s1=losses(zz,bb,t([.001,1.,1.]))
    need(float(distance(aa,bb))<.1 and float(r1-r0)<0 and float(s1-s0)>0,'Raw Euclidean improvement does not imply standardized improvement')
    need(quantile(t(np.arange(48)))==43 and quantile(t(np.arange(192)))==172,'Noninterpolated Q90')
    return {'passed':True,'four_grid_fixture':True,'standardized_counterexample':True,'no_fits':True}
