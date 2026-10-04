"""Approved startup center; old support, scaling, penalty and whole-vector residuals."""
import numpy as np
import pandas as pd
from diagnostic_models import wm, torch, tensor
from diagnostics import W, AUX


def entity_counts(aux):
    n=torch.round(torch.expm1(tensor(aux)[:,:2]))
    assert (n>=0).all() and torch.isfinite(n).all()
    return n


def startup_beta(pre, raw_targets, aux):
    a=tensor(pre);n=entity_counts(aux);delta=tensor(raw_targets)[:,:2]-a[:,:2]
    denom=(n*n).sum(0);numerator=(n*delta).sum(0)
    return torch.where(denom>0,numerator/denom.clamp_min(1),0.).clamp_min(0.)


def startup_center(pre, aux, beta):
    a=wm.validate(pre).clone();n=entity_counts(aux)
    assert ((a[:,2:4]==0)==(n==0)).all(),'zero direction mismatch'
    increment=torch.floor(n*tensor(beta)+.5)
    a[:,:2]+=increment
    # Never clip, retry or drop an overflow. Qualification must stop.
    if (a[:,:2]>wm.L*a[:,2:4]).any():raise ValueError('startup center exceeds approved W capacity')
    wm.validate(a);return a


class CenterRidge:
    def __init__(self, pre, latent_targets, aux=None, raw_targets=None, mechanism=False):
        a=tensor(pre);z=wm.encode(a)
        self.mechanism=mechanism;self.augmented=aux is not None
        self.beta=startup_beta(a,raw_targets,aux) if mechanism else torch.zeros(2,device=a.device,dtype=a.dtype)
        center=wm.encode(startup_center(a,aux,self.beta)) if mechanism else z
        q=torch.log1p(a)
        if self.augmented:q=torch.cat([q,tensor(aux)],1)
        self.mean=q.mean(0);self.scale=q.std(0,unbiased=False)
        self.scale=torch.where(self.scale<1e-10,1.,self.scale)
        # Preserve ORIGINAL pre-phi scale, not a new target or center scale.
        self.zscale=z.std(0,unbiased=False);self.zscale=torch.where(self.zscale<1e-10,1.,self.zscale)
        x=torch.cat([(q-self.mean)/self.scale,torch.ones((len(q),1),device=a.device,dtype=a.dtype)],1)
        penalty=torch.eye(x.shape[1],device=a.device,dtype=a.dtype);penalty[-1,-1]=0
        lhs=x.T@x/len(x)+penalty;rhs=x.T@((tensor(latent_targets)-center)/self.zscale)/len(x)
        self.weight=torch.linalg.solve(lhs,rhs)
        self.normal_residual=float((lhs@self.weight-rhs).abs().max())
        assert torch.isfinite(self.weight).all()
        shift=center-z
        # CUDA SVD projection tolerates constant/rank-deficient proxy columns.
        projection=x@torch.linalg.pinv(x)@shift
        self.center_column_space_relative_error=float(torch.linalg.vector_norm(shift-projection)/(torch.linalg.vector_norm(shift)+1e-30))
    def predict(self, pre, aux=None):
        a=tensor(pre);q=torch.log1p(a)
        if self.augmented:q=torch.cat([q,tensor(aux)],1)
        q=(q-self.mean)/self.scale
        x=torch.cat([q,torch.ones((len(q),1),device=a.device,dtype=a.dtype)],1)
        center=wm.encode(startup_center(a,aux,self.beta)) if self.mechanism else wm.encode(a)
        return center+(x@self.weight)*self.zscale
    def state(self):return vars(self)


def fit(pre, post, kind, method):
    assert kind in {'paired','group','cyclic'} and method in {'D0','D1','D2'}
    extra=[] if method=='D0' else AUX
    if kind=='group':
        assert set(pre)=={'content_id',*W,*extra} and set(post)=={'content_id',*W}
        pre=pre.sort_values(['content_id',*W,*extra]).reset_index(drop=True)
        post=post.sort_values(['content_id',*W]).reset_index(drop=True)
    else:
        assert set(pre)=={'session_id','content_id','repetition',*W,*extra}
        assert set(post)=={'session_id','content_id','repetition',*W}
        pre=pre.sort_values(['content_id','repetition']).reset_index(drop=True)
        post=post.set_index('session_id').loc[pre.session_id].reset_index()
        assert pre.groupby('content_id').repetition.agg(set).map(lambda x:x=={1,2,3,4}).all()
    assert len(pre)==len(post)==72 and pre.content_id.nunique()==18
    assert pre.groupby('content_id').size().eq(4).all() and post.groupby('content_id').size().eq(4).all()
    a=pre[W].to_numpy(float);raw=post[W].to_numpy(float);b=wm.encode(raw)
    donor=np.arange(72)
    if kind=='cyclic':
        for _,g in pre.groupby('content_id'):
            ix=g.index.to_numpy();donor[ix]=np.roll(ix,-1)
        assert (donor!=np.arange(72)).all()
    if kind=='group':
        latent_means={c:b[post.content_id.eq(c).to_numpy()].mean(0) for c in pre.content_id.unique()}
        raw_means={c:raw[post.content_id.eq(c).to_numpy()].mean(0) for c in pre.content_id.unique()}
        target=torch.stack([latent_means[c] for c in pre.content_id])
        rt=np.stack([raw_means[c] for c in pre.content_id])
    else:target=b[donor];rt=raw[donor]
    aux=pre[AUX].to_numpy(float) if method!='D0' else None
    mechanism=method=='D2'
    model=CenterRidge(a,target,aux,rt,mechanism);pool=[];logs=[];oof=[]
    for content in sorted(pre.content_id.unique()):
        held=pre.content_id.eq(content).to_numpy();fitaux=aux[~held] if aux is not None else None
        heldaux=aux[held] if aux is not None else None
        inner=CenterRidge(a[~held],target[~held],fitaux,rt[~held],mechanism)
        pred=inner.predict(a[held],heldaux)
        if kind=='group':
            z=b[post.content_id.eq(content).to_numpy()]
            residual=(z[None,:,:]-pred[:,None,:]).reshape(-1,6)
        else:residual=target[held]-pred
        pool.append(residual)
        oof.append({'content_id':content,'pre':a[held],'prediction':pred.detach().cpu().numpy(),
            'target':target[held].detach().cpu().numpy()})
        logs.append({'held_content':content,'fit_contents':sorted(pre.loc[~held,'content_id'].unique()),
            'fit_rows':68,'residual_rows':len(residual),'normal_residual':inner.normal_residual,
            'beta':inner.beta.cpu().tolist(),'center_column_space_error':inner.center_column_space_relative_error,
            'cuda':True,'query_post_reads':0,'beta_reestimated':mechanism})
    return model,torch.cat(pool),logs,pre,oof


def sample(model,pool,query,name,seed):
    # Exact old RNG key and draw budget; same draws for paired D0/D1/D2.
    from p3_legacy import LC
    a=query[W].to_numpy(float);aux=query[AUX].to_numpy(float) if model.augmented else None
    pred=model.predict(a,aux)
    rng=np.random.default_rng(int(LC.digest(['business-protocol-draw-v1',name,seed])[:16],16))
    draw=rng.integers(0,len(pool),(len(query),8))
    z=pred[:,None,:]+pool[torch.as_tensor(draw,device=pred.device)]
    decoded,audit=wm.decode(z);values=decoded.cpu().numpy();LC.valid_w(values.reshape(-1,6))
    return values,{k:int(v.sum()) for k,v in audit.items()},draw
