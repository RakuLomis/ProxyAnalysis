"""Explicit source/post/old-target coordinate adapters, with no target-side fitting."""
import numpy as np
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from .group_anchor_reliability import feature_groups


def subsets():
    return {'Full':list(range(157)), **{'Only-'+g['group']:g['indices'] for g in feature_groups()}}


def fit_source(raw, old_target, eps=1e-12):
    raw=np.asarray(raw,float)
    imp=SimpleImputer(strategy='median',keep_empty_features=True).fit(raw)
    sc=StandardScaler().fit(imp.transform(raw))
    active=np.asarray(old_target['valid']) & (sc.var_>=eps)
    return {'median':imp.statistics_.tolist(),'mean':sc.mean_.tolist(),'scale':sc.scale_.tolist(),
            'variance':sc.var_.tolist(),'active':active.tolist()}


def scale_selected(raw, scaler, indices):
    raw=np.asarray(raw,float)
    if raw.ndim!=2 or raw.shape[1]!=157:raise ValueError('Expected raw 157-column matrix')
    x=raw[:,indices]
    if np.isinf(x).any():raise ValueError('Infinite selected input')
    med=np.array(scaler['median'])[indices];mean=np.array(scaler['mean'])[indices];sd=np.array(scaler['scale'])[indices]
    return (np.where(np.isnan(x),med,x)-mean)/sd


def source_selected(raw, source, indices):
    z=scale_selected(raw,source,indices)
    return z*np.asarray(source['active'])[indices]


def raw_input(bundle, side):
    expected={'fold','session_ids','raw_'+side}
    if set(bundle)!=expected:raise ValueError('Inference package contains unauthorized fields')
    raw=np.asarray(bundle['raw_'+side],float)
    if raw.shape!=(len(bundle['session_ids']),157):raise ValueError('Invalid raw input shape')
    return raw


def coordinate(bundle, arm, indices, source, post, target, mapping=None):
    if arm=='A':return source_selected(raw_input(bundle,'pre'),source,indices),None
    raw=raw_input(bundle,'post')
    if arm=='B':return source_selected(raw,source,indices),None
    zpost=scale_selected(raw,post,indices)
    if arm=='E':return zpost,None
    if arm not in ('C','D') or mapping is None:raise ValueError('Unknown arm or missing mapping')
    old_z=zpost*np.array(mapping['coef'])[indices]+np.array(mapping['intercept'])[indices]
    raw_hat=old_z*np.array(target['scale'])[indices]+np.array(target['mean'])[indices]
    zsource=(raw_hat-np.array(source['mean'])[indices])/np.array(source['scale'])[indices]
    zsource*=np.array(source['active'])[indices]
    if not np.isfinite(zsource).all():raise ValueError('Nonfinite calibrated coordinates')
    return zsource,raw_hat


def logits(z,fit):
    return np.asarray(z)@np.asarray(fit['coef']).T+np.asarray(fit['intercept'])
