import os
os.environ.setdefault('CUBLAS_WORKSPACE_CONFIG',':4096:8')
from .common import *  # pandas/Arrow must precede torch DLLs on Windows
import torch

def device():
    if not torch.cuda.is_available():raise RuntimeError('CUDA required; no CPU model fallback')
    torch.set_num_threads(1);torch.use_deterministic_algorithms(True)
    torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
    return torch.device('cuda:0')

class Ridge:
    """Mean-per-visit squared Euclidean error + alpha ||W||²; intercept free."""
    def __init__(self,pre,post,F,alpha=1.):
        dev=device();a=torch.tensor(np.log1p(pre),device=dev,dtype=torch.float64)
        b=torch.tensor(np.log1p(post),device=dev,dtype=torch.float64)
        q=torch.cat([a,torch.tensor(np.log1p(F),device=dev,dtype=torch.float64)[:,None]],dim=1)
        self.mean=q.mean(0);self.scale=q.std(0,unbiased=False);self.scale=torch.where(self.scale<1e-10,torch.ones_like(self.scale),self.scale)
        x=(q-self.mean)/self.scale;x=torch.cat([x,torch.ones((len(x),1),device=dev,dtype=x.dtype)],dim=1)
        y=(b-a)/self.scale[:6]
        penalty=torch.eye(8,device=dev,dtype=x.dtype)*alpha;penalty[-1,-1]=0
        self.weight=torch.linalg.solve(x.T@x/len(x)+penalty,x.T@y/len(x))
        assert self.weight.is_cuda and torch.isfinite(self.weight).all()
        self.normal_residual=float(((x.T@x/len(x)+penalty)@self.weight-x.T@y/len(x)).abs().max())
        self.center=torch.quantile(b-a,.5,dim=0).cpu().numpy()
    def predict(self,pre,F):
        with torch.no_grad():
            a=torch.tensor(np.log1p(pre),device=self.weight.device,dtype=torch.float64)
            q=torch.cat([a,torch.tensor(np.log1p(F),device=self.weight.device,dtype=torch.float64)[:,None]],dim=1)
            x=(q-self.mean)/self.scale;x=torch.cat([x,torch.ones((len(x),1),device=x.device,dtype=x.dtype)],dim=1)
            result=a+(x@self.weight)*self.scale[:6];assert result.is_cuda
            return result.cpu().numpy()
    def state(self):return {'mean':self.mean,'scale':self.scale,'weight':self.weight,'center':self.center,'device':'cuda','normal_equation_residual':self.normal_residual}

def targets(frame,wrong):
    a=frame[[k+'_pre' for k in FEATURES]].to_numpy(float)
    b=frame[[k+'_post' for k in FEATURES]].to_numpy(float)
    donor=np.arange(len(frame))
    if wrong:
        for c in frame.content_id.unique():
            indices=np.flatnonzero(frame.content_id.to_numpy()==c)
            indices=indices[np.argsort(frame.iloc[indices].repetition.to_numpy())]
            assert frame.iloc[indices].repetition.tolist()==[1,2,4,5]
            donor[indices]=np.roll(indices,-1)
        assert np.all(donor!=np.arange(len(frame))) and len(np.unique(donor))==len(frame)
    return a,b[donor],frame.F.to_numpy(float),donor

def fit_pool(frame,wrong=False):
    frame=frame.reset_index(drop=True);a,b,F,donor=targets(frame,wrong)
    model=Ridge(a,b,F);residual=np.zeros_like(a);audit=[]
    for c in sorted(frame.content_id.unique()):
        held=frame.content_id.eq(c).to_numpy();sub=frame.loc[~held].reset_index(drop=True)
        sa,sb,sF,_=targets(sub,wrong);inner=Ridge(sa,sb,sF)
        pred=inner.predict(a[held],F[held]);residual[held]=np.log1p(b[held])-pred
        audit.append({'held_content':c,'fit_content_hash':object_hash(sorted(sub.content_id.unique())),
            'fit_contents':sorted(sub.content_id.unique()),'held_sessions':frame.loc[held,'session_id'].tolist(),
            'normal_equation_residual':inner.normal_residual,'cuda':True})
    pool=frame[['session_id','content_id','repetition']].copy()
    pool['target_session_id']=frame.iloc[donor].session_id.to_numpy()
    for j,k in enumerate(FEATURES):pool['residual_'+k]=residual[:,j];pool['drift_'+k]=np.log1p(b[:,j])-np.log1p(a[:,j])
    return model,pool,audit

def decode(log_values,F):
    with np.errstate(over='ignore',invalid='ignore'):raw=np.expm1(log_values)
    if not np.isfinite(raw).all():return raw,raw,'nonfinite_or_shape'
    if (raw<0).any():return raw,np.rint(raw),'negative'
    rounded=np.rint(raw) # Fixed nearest / ties-to-even; no clipping.
    return raw,rounded,illegal(rounded,F)
