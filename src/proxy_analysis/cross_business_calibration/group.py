"""Group-only numeric fitting. No paired identifiers or exporter dependencies."""
from .common import *
from ..conditional_drift.model import device,torch

def canonical(pre,post):
    assert set(pre.columns)=={'content_id',*NUMERIC} and set(post.columns)=={'content_id',*FEATURES}
    pre=pre.sort_values(['content_id']+NUMERIC).reset_index(drop=True);post=post.sort_values(['content_id']+FEATURES).reset_index(drop=True)
    assert set(pre.content_id)==set(post.content_id)
    assert pre.groupby('content_id').size().eq(4).all() and post.groupby('content_id').size().eq(4).all()
    return pre,post

class GroupRidge:
    def __init__(self,pre,post):
        pre,post=canonical(pre,post);dev=device()
        a=torch.tensor(np.log1p(pre[FEATURES].to_numpy(float)),device=dev,dtype=torch.float64)
        q=torch.tensor(np.log1p(pre[NUMERIC].to_numpy(float)),device=dev,dtype=torch.float64)
        means={c:np.log1p(g[FEATURES].to_numpy(float)).mean(0) for c,g in post.groupby('content_id')}
        b=torch.tensor(np.stack([means[c] for c in pre.content_id]),device=dev,dtype=torch.float64)
        self.mean=q.mean(0);self.scale=q.std(0,unbiased=False);self.scale=torch.where(self.scale<1e-10,torch.ones_like(self.scale),self.scale)
        x=torch.cat([(q-self.mean)/self.scale,torch.ones((len(q),1),device=dev,dtype=q.dtype)],1)
        y=(b-a)/self.scale[:6];penalty=torch.eye(8,device=dev,dtype=q.dtype);penalty[-1,-1]=0
        self.weight=torch.linalg.solve(x.T@x/len(x)+penalty,x.T@y/len(x))
        self.normal_residual=float(((x.T@x/len(x)+penalty)@self.weight-x.T@y/len(x)).abs().max())
        assert self.weight.is_cuda and torch.isfinite(self.weight).all()
    def predict(self,pre,F):
        with torch.no_grad():
            a=torch.tensor(np.log1p(pre),device=self.weight.device,dtype=torch.float64)
            q=torch.cat([a,torch.tensor(np.log1p(F),device=a.device,dtype=a.dtype)[:,None]],1)
            x=torch.cat([(q-self.mean)/self.scale,torch.ones((len(q),1),device=a.device,dtype=a.dtype)],1)
            return (a+(x@self.weight)*self.scale[:6]).cpu().numpy()
    def state(self):return {'mean':self.mean,'scale':self.scale,'weight':self.weight,'normal_equation_residual':self.normal_residual,'cuda':True}

def fit_group(pre,post):
    pre,post=canonical(pre,post);model=GroupRidge(pre,post);rows=[];audit=[]
    for c in sorted(pre.content_id.unique()):
        pa=pre[pre.content_id==c];pb=post[post.content_id==c]
        inner=GroupRidge(pre[pre.content_id!=c],post[post.content_id!=c]);pred=inner.predict(pa[FEATURES].to_numpy(float),pa.F.to_numpy(float))
        b=np.log1p(pb[FEATURES].to_numpy(float))
        for r in range(4):
            for s in range(4):rows.append({'content_id':c,'pre_local_index':r,'post_local_index':s,**dict(zip(['residual_'+k for k in FEATURES],b[s]-pred[r]))})
        audit.append({'held_content':c,'fit_contents':sorted(pre.loc[pre.content_id!=c,'content_id'].unique()),'cuda':True,'normal_equation_residual':inner.normal_residual})
    return model,pd.DataFrame(rows),audit
