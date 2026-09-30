"""Fit all numerical coordinate states exclusively on the source training package."""
import argparse
import numpy as np
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from .deployment_transfer_contract import CONFIG,verify,contexts
from .group_anchor_reliability import normalize_fit,normalized
from .source_transfer_coordinates import fit_source,source_selected,scale_selected
from .source_hierarchy_contract import center_targets
from .mechanism_contract import read
from .paired_structure_contract import seal
from ..paired_information.prepare import digest
from ..reproducibility.preflight import write_json


def prepare_state(package):
    rows=package['rows'];protocol=package['source_protocol']
    if len(rows)!=96 or any(r['protocol']!=protocol for r in rows):raise ValueError('Non-source training rows')
    pre=np.asarray(package['raw_pre'],float);post=np.asarray(package['raw_post'],float)
    if pre.shape!=(96,157) or post.shape!=pre.shape or np.isinf(pre).any() or np.isinf(post).any():raise ValueError('Training arrays')
    target=normalize_fit(pre);src=fit_source(pre,target)
    imp=SimpleImputer(strategy='median',keep_empty_features=True).fit(post);sc=StandardScaler().fit(imp.transform(post))
    ps={'median':imp.statistics_.tolist(),'mean':sc.mean_.tolist(),'scale':sc.scale_.tolist(),'variance':sc.var_.tolist()}
    j=np.flatnonzero(src['active']);
    if not len(j) or not np.isfinite(pre[:,j]).all():raise ValueError('Incomplete active training target')
    t=normalized(pre,target)[:,j];v=scale_selected(post,ps,list(range(157)))
    c=np.asarray(target['scale'])[j]/np.asarray(src['scale'])[j]
    offset=(np.asarray(target['mean'])[j]-np.asarray(src['mean'])[j])/np.asarray(src['scale'])[j]
    if not np.allclose(t*c+offset,source_selected(pre,src,j.tolist()),atol=1e-12):raise ValueError('Coordinate mismatch')
    return {'source_scaler':src,'post_scaler':ps,'target_scaler':target,'indices':j.tolist(),
        'pre':source_selected(pre,src,list(range(157))).tolist(),'post':v.tolist(),'t':t.tolist(),
        'center':center_targets(t,rows,rows).tolist(),'c':c.tolist(),'offset':offset.tolist(),
        'pre_inactive_post_variable_indices':[i for i in range(157) if not src['active'][i] and sc.var_[i]>=1e-12]}


def run(config=CONFIG):
    cfg,root=verify(config);out=root/'prepared'
    if out.exists():raise FileExistsError(out)
    checks=[]
    for protocol,f,key in contexts(cfg):
        path=root/'train'/f'{key}.json';p=read(path);state=prepare_state(p)
        write_json(out/f'{key}.json',{'context':key,'source_protocol':protocol,'fold':f,'labels':p['labels'],
            'train_ids':[r['session_id'] for r in p['rows']],'y':[p['labels'].index(r['label_id']) for r in p['rows']],
            'training_package_sha256':digest(path),**state})
        checks.append({'context':key,'d':len(state['indices']),'parameters':2*len(state['indices']),
            'pre_inactive_post_variable_indices':state['pre_inactive_post_variable_indices']})
    write_json(out/'validation.json',{'passed':True,'source_only':True,'checks':checks});seal(out,passed=True)
    print('10 source-only coordinate states fitted',flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--config',default=str(CONFIG));a=p.parse_args();run(a.config)
