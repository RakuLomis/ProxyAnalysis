"""Deterministic convex P7 objective; binary baseline matches sklearn log-odds L2."""
import numpy as np
from scipy.optimize import minimize
from scipy.special import expit, logsumexp, softmax


def moment(d):
    d=np.asarray(d,dtype=float)
    if d.ndim!=2 or not np.all(np.isfinite(d)): raise ValueError('Invalid differences')
    raw=d.T@d/len(d); trace=float(np.trace(raw))
    normalized=raw/(trace/d.shape[1]) if trace>0 else np.zeros_like(raw)
    return raw,normalized


def objective(theta,x,y,k,cov,lam,C=1.):
    n,d=x.shape; rows=1 if k==2 else k
    pars=np.asarray(theta).reshape(rows,d+1);w=pars[:,:d];bias=pars[:,d]
    if k==2:
        z=(x@w.T+bias).ravel();p=expit(z)
        ce=float(np.mean(np.logaddexp(0,z)-y*z));err=p-y
        penalty=float((w@cov*w).sum()/2)
        gw=(err@x/n)[None,:]+w/(n*C)+lam*(w@cov)
        gb=np.asarray([err.mean()])
    else:
        z=x@w.T+bias;lp=z-logsumexp(z,axis=1,keepdims=True)
        ce=float(-lp[np.arange(n),y].mean());err=np.exp(lp);err[np.arange(n),y]-=1
        centered=w-w.mean(axis=0)
        penalty=float((centered@cov*centered).sum())
        gw=err.T@x/n+w/(n*C)+2*lam*(centered@cov)
        gb=err.mean(axis=0)
    l2=float((w*w).sum()/(2*n*C))
    return ce+lam*penalty+l2,np.column_stack([gw,gb]).ravel(),{'ce_nats':ce,'pair_penalty':penalty,'l2':l2}


def fit(x,y,k,cov,lam,cfg):
    x=np.asarray(x,dtype=float);y=np.asarray(y,dtype=int)
    if (not np.all(np.isfinite(x)) or cov.shape!=(x.shape[1],)*2
        or not np.all(np.isfinite(cov)) or not np.allclose(cov,cov.T)
        or np.linalg.eigvalsh(cov).min() < -1e-8): raise ValueError('Invalid optimizer inputs')
    theta=np.zeros((1 if k==2 else k)*(x.shape[1]+1))
    def fun(t): value,gradient,_=objective(t,x,y,k,cov,lam,cfg['model_C']);return value,gradient
    result=minimize(fun,theta,jac=True,method='L-BFGS-B',options={
        'gtol':cfg['optimizer_gtol'],'ftol':cfg['optimizer_ftol'],
        'maxiter':cfg['optimizer_maxiter'],'maxls':50})
    value,grad,parts=objective(result.x,x,y,k,cov,lam,cfg['model_C'])
    if not result.success or np.max(np.abs(grad))>1e-6:
        raise ValueError(f'Optimizer did not converge: {result.message}, gradient={max(abs(grad))}')
    pars=result.x.reshape(-1,x.shape[1]+1)
    return {'coef':pars[:,:-1].tolist(),'intercept':pars[:,-1].tolist(),
        'objective':value,'gradient_inf':float(np.max(abs(grad))),**parts,
        'iterations':int(result.nit),'success':bool(result.success),'message':str(result.message)}


def probability(x,state):
    w=np.asarray(state['coef']);c=np.asarray(state['intercept']);z=x@w.T+c
    if len(w)==1:
        p=expit(z.ravel());return np.column_stack([1-p,p])
    return softmax(z,axis=1)


def donor_indices(rows,shift):
    if shift not in (1,2,3): raise ValueError('Invalid donor shift')
    labels=sorted({r['label_id'] for r in rows});lookup={}
    if len({r['protocol'] for r in rows})!=1: raise ValueError('Multiple source deployments')
    for i,r in enumerate(rows):
        key=(r['label_id'],r['content_id'],r['repetition'])
        if key in lookup: raise ValueError('Duplicate visit')
        lookup[key]=i
    mapping=[]
    for r in rows:
        contents=sorted({v['content_id'] for v in rows if v['label_id']==r['label_id']})
        if len(contents)!=4: raise ValueError('Four source training contents required')
        donor=contents[(contents.index(r['content_id'])+shift)%4]
        mapping.append(lookup[r['label_id'],donor,r['repetition']])
    if sorted(mapping)!=list(range(len(rows))): raise ValueError('Not bijective')
    if any(rows[i]['content_id']==rows[j]['content_id'] for i,j in enumerate(mapping)):
        raise ValueError('Fixed content')
    return np.asarray(mapping)
