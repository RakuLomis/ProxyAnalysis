"""Small CUDA-only models; fixed alpha1, no tuning or residual sampling."""
import sys
import numpy as np
from common import ROOT
sys.path.insert(0, str(ROOT / 'eval/hy2_carrier_calibration'))
import window_model as wm
torch = wm.torch


def tensor(value):
    result = wm.tensor(value)
    assert result.is_cuda
    return result


class WindowProxy:
    def __init__(self, pre, target, auxiliary=None):
        a = tensor(pre); z = wm.encode(a)
        q = torch.log1p(a)
        if auxiliary is not None: q = torch.cat([q, tensor(auxiliary)], 1)
        self.mean = q.mean(0); self.scale = q.std(0, unbiased=False)
        self.scale = torch.where(self.scale < 1e-10, 1., self.scale)
        self.zscale = z.std(0, unbiased=False)
        self.zscale = torch.where(self.zscale < 1e-10, 1., self.zscale)
        x = torch.cat([(q-self.mean)/self.scale, torch.ones((len(q),1),device=q.device,dtype=q.dtype)],1)
        penalty = torch.eye(x.shape[1],device=q.device,dtype=q.dtype); penalty[-1,-1]=0
        lhs=x.T@x/len(x)+penalty; rhs=x.T@((tensor(target)-z)/self.zscale)/len(x)
        self.weight=torch.linalg.solve(lhs,rhs)
        self.normal_residual=float((lhs@self.weight-rhs).abs().max())
    def predict(self, pre, auxiliary=None):
        a=tensor(pre);q=torch.log1p(a)
        if auxiliary is not None:q=torch.cat([q,tensor(auxiliary)],1)
        q=(q-self.mean)/self.scale
        x=torch.cat([q,torch.ones((len(q),1),device=q.device,dtype=q.dtype)],1)
        return wm.encode(a)+(x@self.weight)*self.zscale


class AdditiveRidge:
    def __init__(self, pre, post, auxiliary=None):
        a=tensor(pre);b=tensor(post);q=torch.log1p(a)
        if auxiliary is not None:q=torch.cat([q,tensor(auxiliary)],1)
        self.mean=q.mean(0);self.scale=q.std(0,unbiased=False)
        self.scale=torch.where(self.scale<1e-10,1.,self.scale)
        target=b-a[:,:2];self.yscale=target.std(0,unbiased=False)
        self.yscale=torch.where(self.yscale<1e-10,1.,self.yscale)
        x=torch.cat([(q-self.mean)/self.scale,torch.ones((len(q),1),device=q.device,dtype=q.dtype)],1)
        penalty=torch.eye(x.shape[1],device=q.device,dtype=q.dtype);penalty[-1,-1]=0
        lhs=x.T@x/len(x)+penalty;rhs=x.T@(target/self.yscale)/len(x)
        self.weight=torch.linalg.solve(lhs,rhs)
    def predict(self, pre, auxiliary=None):
        a=tensor(pre);q=torch.log1p(a)
        if auxiliary is not None:q=torch.cat([q,tensor(auxiliary)],1)
        q=(q-self.mean)/self.scale
        return a[:,:2]+torch.cat([q,torch.ones((len(q),1),device=q.device,dtype=q.dtype)],1)@self.weight*self.yscale


def median_offset(pre, post, query):
    # numpy uses average of two middle values; torch.quantile matches that rule.
    delta=tensor(post)-tensor(pre)[:,:2]
    return tensor(query)[:,:2]+torch.quantile(delta,.5,dim=0)


def replay():
    a=np.array([[100+i*20,200+i*30,5+i,10+i,2,2] for i in range(20)],float)
    b=a.copy();b[:,:2]+=np.arange(20)[:,None]*3+40
    z=wm.encode(b);old=wm.Ridge(a,z);new=WindowProxy(a,z)
    error=float((old.predict(a)-new.predict(a)).abs().max())
    assert error < 1e-12
    return {'cuda':True,'device':torch.cuda.get_device_name(0),'dtype':'float64',
            'old_ridge_replay_max_abs':error,'no_cpu_fit_or_inference_fallback':True}
