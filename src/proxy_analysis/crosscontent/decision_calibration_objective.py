"""Diagonal affine recovery with fixed centered source-logit quadratic penalty."""
import numpy as np
from scipy.linalg import solve, lstsq


def validate(v,t,c,w,mask=None):
    v,t,c,w=map(lambda a:np.asarray(a,float),(v,t,c,w))
    if v.ndim!=2 or t.shape!=v.shape or c.shape!=(v.shape[1],) or w.shape[1]!=v.shape[1]:
        raise ValueError('Coordinate shape mismatch')
    if not all(np.isfinite(a).all() for a in (v,t,c,w)):raise ValueError('Nonfinite training target')
    if mask is not None and not np.asarray(mask,bool).all():raise ValueError('Missing active target')
    return v,t,c,w-w.mean(axis=0)


def losses(theta,v,t,c,w,lam,alpha=1.):
    v,t,c,w=validate(v,t,c,w);n,d=v.shape;a,b=np.asarray(theta).reshape(2,d)
    residual=v*a+b-t
    rec=float(((residual**2).sum()+alpha*(a*a).sum())/(n*d))
    dec=float(((residual*c)@w.T).ravel()@((residual*c)@w.T).ravel()/(n*(len(w)-1)))
    return {'recovery':rec,'decision':dec,'total':rec+lam*dec,
            'target_mse':float(np.mean(residual**2))}


def quadratic(v,t,c,w,lam,alpha=1.,mask=None):
    v,t,c,w=validate(v,t,c,w,mask);n,d=v.shape
    if lam<0 or alpha<=0:raise ValueError('Invalid penalty')
    k=np.eye(d)/d+lam*((w*c).T@(w*c))/(len(w)-1)
    h=np.block([[k*(v.T@v)/n+np.eye(d)*alpha/(n*d), k*v.mean(0)[:,None]],
                [k*v.mean(0)[None,:],k]])
    tk=t@k
    rhs=np.r_[(v*tk).mean(0),tk.mean(0)]
    return h,rhs


def fit(v,t,c,w,lam,alpha=1.,mask=None):
    h,rhs=quadratic(v,t,c,w,lam,alpha,mask)
    eig=np.linalg.eigvalsh(h);condition=float(eig[-1]/eig[0])
    if eig[0]<=0 or not np.isfinite(condition) or condition>1e12:raise ValueError('Ill-conditioned quadratic')
    theta=solve(h,rhs,assume_a='pos')
    grad=float(np.linalg.norm(h@theta-rhs)/(np.linalg.norm(h)*np.linalg.norm(theta)+np.linalg.norm(rhs)+1e-30))
    if not np.isfinite(theta).all() or grad>1e-9:raise ValueError('Stationarity check failed')
    return theta,{'condition_number':condition,'minimum_eigenvalue':float(eig[0]),
                  'normalized_gradient_residual':grad,**losses(theta,v,t,c,w,lam,alpha)}


def independent_lstsq(v,t,c,w,lam,alpha=1.):
    """Explicit residual design, independent of normal-equation assembly."""
    v,t,c,w=validate(v,t,c,w);n,d=v.shape;k=len(w);blocks=[];targets=[]
    eye=np.eye(d)
    for i in range(n):
        design=np.concatenate((np.diag(v[i]),eye),axis=1)
        blocks.append(design/np.sqrt(n*d));targets.append(t[i]/np.sqrt(n*d))
        if lam:
            score=w*c
            blocks.append(np.sqrt(lam/(n*(k-1)))*(score@design))
            targets.append(np.sqrt(lam/(n*(k-1)))*(score@t[i]))
    blocks.append(np.concatenate((np.sqrt(alpha/(n*d))*eye,np.zeros((d,d))),axis=1))
    targets.append(np.zeros(d))
    return lstsq(np.vstack(blocks),np.concatenate(targets),lapack_driver='gelsy')[0]
