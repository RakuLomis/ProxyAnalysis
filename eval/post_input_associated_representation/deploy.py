"""Standalone deployment. No IO, teacher, labels, visits, protocol or pair tables."""
import torch
import torch.nn.functional as F

def predict_post(raw_post,base_model,residual_state=None):
    if not (raw_post.is_cuda and raw_post.dtype==torch.float64 and raw_post.ndim==2 and raw_post.shape[1]==96):
        raise RuntimeError('Only CUDA float64 96-d post values')
    x=(raw_post-base_model['mu'])/base_model['scale']
    with torch.no_grad():
        z=x@base_model['weight'].T+base_model['bias']
        if residual_state is not None:
            s=residual_state;xf=x.float()
            g=F.linear(F.relu(F.linear(xf,s['w0'],s['b0'])),s['w1'],s['b1'])
            r=F.linear(torch.cat([xf,g],-1),s['w2'],s['b2'])
            z=z+.1*(r-r.mean(-1,keepdim=True)).double()
        if not bool(torch.isfinite(z).all()):raise RuntimeError('Nonfinite post inference')
        return F.log_softmax(z,1)
