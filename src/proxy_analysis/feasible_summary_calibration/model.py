from .common import *
from ..conditional_drift.model import torch,device
LIMIT=2**53-1

def tensor(x):return torch.as_tensor(x,device=device(),dtype=torch.float64)

def encode(a):
    a=tensor(a);U,E,R=a[...,:2],a[...,2:4],a[...,4:6]
    assert torch.isfinite(a).all() and (a>=0).all() and (a==a.round()).all() and (R<=E).all() and (E<=U).all()
    return torch.cat([torch.log(R.sum(-1,keepdim=True)+.5),torch.asinh(R[...,0:1]-R[...,1:2]),torch.log(E-R+.5),torch.log(U-E+.5)],-1)

def decode(z,F):
    z=tensor(z);F=tensor(F)
    if not torch.isfinite(z).all() or not torch.isfinite(F).all():raise FloatingPointError('Nonfinite feasible decoder input')
    if not ((F>=1)&(F==F.round())&(F<=LIMIT)).all():raise FloatingPointError('Invalid F')
    value=torch.exp(z[..., [0,2,3,4,5]])
    if not (torch.isfinite(value).all() and (value<=LIMIT).all()):raise FloatingPointError('Exp/count overflow; no clipping or retry allowed')
    ints=value.floor().to(torch.int64);ff=F.to(torch.int64);n0=ints[...,0];n=torch.maximum(n0,ff)
    bound=ff-torch.remainder(ff-n,2);limit=torch.asinh(bound.to(torch.float64))
    clipped=torch.maximum(-limit,torch.minimum(limit,z[...,1]));t=torch.sinh(clipped)
    index=((t+bound)/2).round().to(torch.int64)
    # Float roundoff near endpoints may only move by floating epsilon, never an arbitrary count.
    if not ((index>=0)&(index<=bound)).all():raise FloatingPointError('Direction lattice index outside bounds')
    diff=-bound+2*index;rup=(n+diff)//2;rdown=(n-diff)//2;R=torch.stack([rup,rdown],-1)
    G=ints[...,1:3];H=ints[...,3:5];ignored=R==0
    E=torch.where(ignored,0,R+G);U=torch.where(ignored,0,E+H)
    if not ((U<=LIMIT)&(E<=LIMIT)&(R<=LIMIT)).all():raise FloatingPointError('Reconstructed integer exceeds exact output range')
    result=torch.cat([U,E,R],-1)
    assert (result>=0).all() and (R<=E).all() and (E<=U).all() and (R.sum(-1)>=ff).all() and ((R[...,0]-R[...,1]).abs()<=ff).all()
    audit={'N_floor_active':n0<ff,'N_added':n-n0,'D_bound_active':z[...,1].abs()>limit,
        'D_latent_bound_displacement':(z[...,1]-clipped).abs(),'D_lattice_displacement':(diff-t).abs(),
        'zero_direction':ignored.any(-1),'ignored_G':torch.where(ignored,G,0).sum(-1),'ignored_H':torch.where(ignored,H,0).sum(-1)}
    return result,audit

class Ridge:
    def __init__(self,a,F,target):
        za=encode(a);q=torch.cat([torch.log1p(tensor(a)),torch.log1p(tensor(F))[:,None]],1)
        self.mean=q.mean(0);self.scale=q.std(0,unbiased=False);self.scale=torch.where(self.scale<1e-10,1.,self.scale)
        self.zscale=za.std(0,unbiased=False);self.zscale=torch.where(self.zscale<1e-10,1.,self.zscale)
        x=torch.cat([(q-self.mean)/self.scale,torch.ones((len(q),1),device=device(),dtype=q.dtype)],1)
        y=(tensor(target)-za)/self.zscale;penalty=torch.eye(8,device=device(),dtype=q.dtype);penalty[-1,-1]=0
        self.weight=torch.linalg.solve(x.T@x/len(x)+penalty,x.T@y/len(x))
        assert self.weight.is_cuda and torch.isfinite(self.weight).all()
        self.normal_residual=float(((x.T@x/len(x)+penalty)@self.weight-x.T@y/len(x)).abs().max())
    def predict(self,a,F):return predict_state(self.state(),a,F)
    def state(self):return {'mean':self.mean,'scale':self.scale,'zscale':self.zscale,'weight':self.weight,'normal_residual':self.normal_residual,'device':'cuda'}

def predict_state(s,a,F):
    with torch.no_grad():
        q=torch.cat([torch.log1p(tensor(a)),torch.log1p(tensor(F))[:,None]],1)
        x=torch.cat([(q-s['mean'])/s['scale'],torch.ones((len(q),1),device=device(),dtype=q.dtype)],1)
        return encode(a)+(x@s['weight'])*s['zscale']

def fit(pre,post,kind):
    if kind=='group':
        assert set(pre.columns)=={'content_id',*NUMERIC} and set(post.columns)=={'content_id',*FEATURES}
        pre=pre.sort_values(['content_id']+NUMERIC).reset_index(drop=True);post=post.sort_values(['content_id']+FEATURES).reset_index(drop=True)
    else:
        pre=pre.reset_index(drop=True);post=post.set_index('session_id').loc[pre.session_id].reset_index()
    a=pre[FEATURES].to_numpy(float);F=pre.F.to_numpy(float);b=encode(post[FEATURES].to_numpy(float));donor=np.arange(len(pre))
    if kind=='cyclic':
        for c,g in pre.groupby('content_id'):
            ix=g.sort_values('repetition').index.to_numpy();assert pre.loc[ix,'repetition'].tolist()==[1,2,4,5];donor[ix]=np.roll(ix,-1)
    if kind=='group':
        means={c:b[np.flatnonzero(post.content_id.to_numpy()==c)].mean(0) for c in post.content_id.unique()}
        target=torch.stack([means[c] for c in pre.content_id])
    else:target=b[donor]
    model=Ridge(a,F,target);rows=[];audit=[]
    for c in sorted(pre.content_id.unique()):
        held=pre.content_id.eq(c).to_numpy();inner=Ridge(a[~held],F[~held],target[~held]);pred=inner.predict(a[held],F[held])
        indices=np.flatnonzero(held)
        if kind=='group':
            targets=b[np.flatnonzero(post.content_id.to_numpy()==c)]
            for r in range(4):
                for s in range(4):rows.append({'content_id':c,'pre_local_index':r,'post_local_index':s,**dict(zip([f'e{j}' for j in range(6)],(targets[s]-pred[r]).cpu().numpy()))})
        else:
            for r,i in enumerate(indices):rows.append({'content_id':c,'session_id':pre.iloc[i].session_id,'target_session_id':post.iloc[donor[i]].session_id,
                **dict(zip([f'e{j}' for j in range(6)],(target[i]-pred[r]).cpu().numpy())),**dict(zip([f'd{j}' for j in range(6)],(target[i]-encode(a[i:i+1])[0]).cpu().numpy()))})
        audit.append({'held_content':c,'fit_contents':sorted(pre.loc[~held,'content_id'].unique()),'cuda':True,'normal_residual':inner.normal_residual})
    return model,pd.DataFrame(rows),audit,pre
