"""Training-only group centers and immutable upstream provenance."""
import argparse
from pathlib import Path
from collections import defaultdict
import numpy as np
import yaml
from .decision_calibration_contract import verify as verify_decision
from .mechanism_contract import read
from .paired_structure_contract import seal,validate_complete
from ..paired_information.prepare import digest
from ..reproducibility.preflight import write_json

CONFIG=Path('configs/source-center-control-0916.yaml')


def groups(rows):
    result=defaultdict(list)
    if len({r['session_id'] for r in rows})!=len(rows):raise ValueError('Duplicate visits')
    for i,r in enumerate(rows):result[(r['content_id'],r['protocol'])].append(i)
    for ix in result.values():
        if len(ix)!=4 or {rows[i]['repetition'] for i in ix}!={1,2,4,5}:raise ValueError('Four-repeat group required')
    return list(result.values())


def center_targets(pre,pre_rows,post_rows):
    """Lookup only by group, never by individual pre/post correspondence."""
    pre=np.asarray(pre,float)
    if not np.isfinite(pre).all():raise ValueError('Incomplete active target')
    if len(pre)!=len(pre_rows):raise ValueError('Target membership mismatch')
    centers={}
    for ix in groups(pre_rows):
        r=pre_rows[ix[0]];centers[r['content_id'],r['protocol']]=pre[ix].mean(0)
    groups(post_rows)
    keys={(r['content_id'],r['protocol']) for r in post_rows}
    if keys!=set(centers):raise ValueError('Pre/post groups differ')
    return np.asarray([centers[r['content_id'],r['protocol']] for r in post_rows])


def settings(config=CONFIG):
    cfg=yaml.safe_load(Path(config).read_text(encoding='utf-8'));return cfg,Path(cfg['output_root'])


def freeze(config=CONFIG):
    cfg,root=settings(config);_,old,source=verify_decision(cfg['decision_config'])
    for part in ('positive-fits','inference','report','audit'):validate_complete(old/part)
    if root.exists():raise FileExistsError(root)
    if cfg['lambda']!=1 or cfg['alpha']!=1 or cfg['solve_budget']!=5:raise ValueError('Fixed design changed')
    checks=[]
    for f in range(5):
        p=read(old/'train'/f'fold-{f}.json');tr=read(source/'train'/f'fold-{f}.json')
        rows=tr['rows'];ev=read(source/'evaluation'/f'fold-{f}.json')['rows'];ix=groups(rows)
        if len(ix)!=48 or len(p['indices'])!=149 or len(rows)!=192:raise ValueError('Cohort mismatch')
        if {r['content_id'] for r in rows}&{r['content_id'] for r in ev}:raise ValueError('Content leakage')
        if p['train_ids']!=[r['session_id'] for r in rows]:raise ValueError('Row mismatch')
        t=np.asarray(p['t']);tc=center_targets(t,rows,rows);z=t*p['c']+p['offset']
        zc=center_targets(z,rows,rows)
        if not np.allclose(zc,tc*p['c']+p['offset'],atol=1e-12):raise ValueError('Center coordinate mismatch')
        perm=np.concatenate([list(reversed(j)) for j in ix]);shuffled=center_targets(t[perm],[rows[i] for i in perm],rows)
        if not np.allclose(tc,shuffled,atol=1e-12):raise ValueError('Center depends on pairing')
        write_json(root/'train'/f'fold-{f}.json',{**p,'t_original':p['t'],'t':tc.tolist(),
            'group_metadata':[{k:r[k] for k in ('session_id','content_id','protocol','repetition')} for r in rows],
            'groups':ix})
        checks.append({'fold':f,'groups':48,'train_visits':192,'test_visits':48,'active_dimensions':149,
            'pre_permutation_invariant':True,'content_overlap':0})
    seal(root/'train',passed=True)
    paths=list(Path('src/proxy_analysis').rglob('*.py'))+[Path(config)]
    paths += [p for base in (old,source) for p in base.rglob('*') if p.is_file()]
    write_json(root/'contract/manifest.json',{'config':cfg,'decision_root':str(old),'source_root':str(source),
        'sources':{str(p):digest(p) for p in sorted(set(paths))},'train_seal':digest(root/'train/complete.json')})
    write_json(root/'contract/checks.json',checks);seal(root/'contract',passed=True)
    print('H centers frozen: 5 folds, 48 four-member groups each',flush=True)


def verify(config=CONFIG):
    cfg,root=settings(config);validate_complete(root/'contract');m=read(root/'contract/manifest.json')
    if cfg!=m['config']:raise ValueError('Config changed')
    for p,h in m['sources'].items():
        if digest(Path(p))!=h:raise ValueError('Source changed: '+p)
    validate_complete(root/'train')
    if digest(root/'train/complete.json')!=m['train_seal']:raise ValueError('Targets changed')
    return cfg,root,Path(m['decision_root']),Path(m['source_root'])


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['freeze','verify']);p.add_argument('--config',default=str(CONFIG));a=p.parse_args();globals()[a.command](a.config)
