"""CUDA support-preserving six-dimensional observed-payload model."""
from experiment import *
L=65527
LIMIT=2**53-1
def tensor(a):return torch.as_tensor(a,device=device(),dtype=torch.float64)
def validate(a):
    a=tensor(a);w,p,r=a[...,:2],a[...,2:4],a[...,4:]
    assert torch.isfinite(a).all() and (a>=0).all() and (a==a.round()).all()
    assert (r<=p).all() and (p<=w).all() and (w<=L*p).all()
    assert (r.sum(-1)>=1).all() and ((r[...,0]-r[...,1]).abs()<=1).all()
    assert ((r==0)==(p==0)).all() and ((p==0)==(w==0)).all()
    return a
def encode(a):
    a=validate(a);w,p,r=a[...,:2],a[...,2:4],a[...,4:];h=w-p;m=(L-1)*p
    return torch.cat([torch.log(r.sum(-1,keepdim=True)-.5),torch.asinh(r[...,0:1]-r[...,1:2]),
                      torch.log(p-r+.5),torch.log(h+.5)-torch.log(m-h+.5)],-1)
def decode(z):
    z=tensor(z)
    if not torch.isfinite(z).all():raise FloatingPointError('nonfinite latent')
    v=torch.exp(z[...,[0,2,3]])
    if not (torch.isfinite(v).all() and (v<LIMIT//L-2).all()):raise FloatingPointError('count overflow; no retry')
    n=1+v[...,0].floor().to(torch.int64);bound=n%2
    limit=torch.asinh(bound.to(torch.float64));clipped=z[...,1].clamp(min=-limit,max=limit)
    d=-bound+2*((torch.sinh(clipped)+bound)/2).round().to(torch.int64)
    r=torch.stack([(n+d)//2,(n-d)//2],-1);g=v[...,1:].floor().to(torch.int64)
    p=torch.where(r==0,0,r+g);m=(L-1)*p
    if not (m<LIMIT).all():raise FloatingPointError('integer capacity overflow')
    raw=(m+1)*torch.sigmoid(z[...,4:]);h=torch.minimum(raw.floor().to(torch.int64),m)
    h=torch.where(r==0,0,h);w=p+h;out=torch.cat([w,p,r],-1);validate(out)
    return out,{'direction_bound':z[...,1].abs()>limit,'zero_direction':(r==0).any(-1),
                'sigmoid_endpoint':(raw.floor()>m).any(-1)}

class Ridge:
    def __init__(self,a,target):
        a=tensor(a);q=torch.log1p(a);z=encode(a)
        self.mean=q.mean(0);self.scale=q.std(0,unbiased=False);self.scale=torch.where(self.scale<1e-10,1.,self.scale)
        self.zscale=z.std(0,unbiased=False);self.zscale=torch.where(self.zscale<1e-10,1.,self.zscale)
        x=torch.cat([(q-self.mean)/self.scale,torch.ones((len(q),1),device=device(),dtype=q.dtype)],1)
        penalty=torch.eye(7,device=device(),dtype=q.dtype);penalty[-1,-1]=0
        lhs=x.T@x/len(x)+penalty;rhs=x.T@((tensor(target)-z)/self.zscale)/len(x)
        self.weight=torch.linalg.solve(lhs,rhs);assert torch.isfinite(self.weight).all()
        self.normal_residual=float((lhs@self.weight-rhs).abs().max())
    def predict(self,a):
        a=tensor(a);q=(torch.log1p(a)-self.mean)/self.scale
        return encode(a)+(torch.cat([q,torch.ones((len(q),1),device=device(),dtype=q.dtype)],1)@self.weight)*self.zscale
    def state(self):return vars(self)

def fit(pre,post,kind):
    if kind=='group':
        assert set(pre)==set(post)=={'content_id',*FEATURES}
        pre=pre.sort_values(['content_id',*FEATURES]).reset_index(drop=True)
        post=post.sort_values(['content_id',*FEATURES]).reset_index(drop=True)
    else:
        pre=pre.sort_values(['content_id','repetition']).reset_index(drop=True)
        post=post.set_index('session_id').loc[pre.session_id].reset_index()
    a=pre[FEATURES].to_numpy(float);b=encode(post[FEATURES].to_numpy(float));donor=np.arange(len(pre))
    if kind=='cyclic':
        for _,g in pre.groupby('content_id'):
            assert sorted(g.repetition)==[1,2,4,5];ix=g.index.to_numpy();donor[ix]=np.roll(ix,-1)
    if kind=='group':
        means={c:b[np.flatnonzero(post.content_id.eq(c))].mean(0) for c in post.content_id.unique()}
        targets=torch.stack([means[c] for c in pre.content_id])
    else:targets=b[donor]
    model=Ridge(a,targets);res=[];logs=[]
    for c in sorted(pre.content_id.unique()):
        held=pre.content_id.eq(c).to_numpy();inner=Ridge(a[~held],targets[~held]);pred=inner.predict(a[held])
        if kind=='group':
            t=b[np.flatnonzero(post.content_id.eq(c))];rr=(t[None,:,:]-pred[:,None,:]).reshape(-1,6)
        else:rr=targets[held]-pred
        res.append(rr);logs.append({'held_content':c,'fit_contents':sorted(pre.loc[~held,'content_id'].unique()),
                                   'residual_rows':len(rr),'normal_residual':inner.normal_residual})
    return model,torch.cat(res),logs,pre,targets-encode(a)
