"""Anonymous within-side moments; no pairing/grouping information accepted."""
from common import *

def schema(d):
    require(set(d)=={'pre','pre_mass','post','post_mass'},'Marginal identity/schema leak')
    for side in ['pre','post']:
        x,w=d[side],d[side+'_mass']
        require(x.ndim==2 and x.shape[1]==96 and w.shape==(len(x),),'Marginal shape')
        require(x.is_cuda and x.dtype==torch.float64 and w.is_cuda and w.dtype==torch.float64,'Marginal CUDA64')
        require(torch.isfinite(x).all() and torch.isfinite(w).all() and (w>0).all(),'Marginal finite mass')
        require(abs(float(w.sum())-1)<1e-12,'Normalized side weights')

def moments(x,w):
    mean=w@x;delta=x-mean;den=1-w.square().sum()
    require(float(den)>0,'Effective count <=1')
    cov=delta.T@(delta*w[:,None])/den
    require(residual(cov,cov.T)<1e-12,'Nonsymmetric covariance')
    return mean,(cov+cov.T)/2

def root(cov,power):
    e,q=torch.linalg.eigh(cov);require((e>0).all(),'Not SPD; no dynamic jitter')
    return (q*e.pow(power))@q.T

def fit(d):
    schema(d);mp,cp=moments(d['pre'],d['pre_mass']);mb,cb=moments(d['post'],d['post_mass'])
    eye=torch.eye(96,device=device(),dtype=torch.float64);a=root(cp+eye,-.5)@root(cb+eye,.5)
    m={'matrix':a.T,'bias':mb-mp@a,'pre_mean':mp,'post_mean':mb,'pre_covariance':cp,'post_covariance':cb}
    congruence=residual(a.T@(cp+eye)@a,cb+eye)
    require(congruence<1e-10 and all(torch.isfinite(t).all() for t in m.values()),'Marginal congruence/finite')
    log={'accepted':True,'diagonal_regularizer':1.,'unbiased_sample_covariance':True,
         'cross_side_covariance_used':False,'identity_input':False,'content_group_input':False,
         'congruence_error':congruence,'actual_covariance_relative_error':residual(a.T@cp@a,cb),
         'pre_rows':len(d['pre']),'post_rows':len(d['post']),'dtype':'float64','device':'cuda:0'}
    return m,log

def apply(m,x):return x@m['matrix'].T+m['bias']
