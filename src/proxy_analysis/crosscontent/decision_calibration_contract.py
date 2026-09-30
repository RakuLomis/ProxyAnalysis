"""Frozen source reuse and strictly separated calibration training package."""
import argparse
from pathlib import Path
import platform
import numpy as np
import scipy
import yaml
from .source_transfer_contract import verify as verify_source
from .source_transfer_coordinates import source_selected
from .mechanism_contract import read
from .paired_structure_contract import seal,validate_complete
from ..paired_information.prepare import digest
from ..reproducibility.preflight import write_json

CONFIG=Path('configs/source-decision-calibration-0916.yaml')


def settings(config=CONFIG):
    cfg=yaml.safe_load(Path(config).read_text(encoding='utf-8'))
    return cfg,Path(cfg['output_root'])


def freeze(config=CONFIG):
    cfg,root=settings(config);_,old,source=verify_source(cfg['source_config'])
    for part in ('source-fits','inference','report','audit'):validate_complete(source/part)
    if root.exists():raise FileExistsError(root)
    if cfg['lambdas']!=[0,.1,1,10] or cfg['solve_budget']!=40 or cfg['subset']!='Full':raise ValueError('Design changed')
    ledger=[];checks=[]
    for f in range(5):
        tr=read(source/'train'/f'fold-{f}.json');prev=read(old/'packages'/f'fold-{f}.train.json')
        fit=read(source/'source-fits'/f'fold-{f}-Full.json')
        j=np.flatnonzero(tr['source_scaler']['active']);mask=np.asarray(prev['target_mask'])[:,j]
        if len(j)!=149 or mask.shape!=(192,149) or not mask.all():raise ValueError('Active targets incomplete')
        ids=[r['session_id'] for r in tr['rows']]
        if ids!=fit['train_ids'] or ids!=[r['session_id'] for r in prev['rows']]:raise ValueError('Members changed')
        test=read(source/'post-input'/f'fold-{f}.json')
        if set(ids)&set(test['session_ids']):raise ValueError('Visit overlap')
        donor=np.asarray(prev['donors']);
        if sorted(donor.tolist())!=list(range(192)) or np.any(donor==np.arange(192)):raise ValueError('Invalid donors')
        for i,d in enumerate(donor):
            if any(tr['rows'][i][key]!=tr['rows'][d][key] for key in ('content_id','protocol')):raise ValueError('Wrong donor scope')
        c=np.asarray(tr['target_scaler']['scale'])[j]/np.asarray(tr['source_scaler']['scale'])[j]
        offset=(np.asarray(tr['target_scaler']['mean'])[j]-np.asarray(tr['source_scaler']['mean'])[j])/np.asarray(tr['source_scaler']['scale'])[j]
        t=np.asarray(prev['pre_target'])[:,j];z=source_selected(tr['raw_pre'],tr['source_scaler'],j.tolist())
        if not np.allclose(t*c+offset,z,atol=1e-12):raise ValueError('Target/source affine mismatch')
        package={'fold':f,'train_ids':ids,'indices':j.tolist(),'v':np.asarray(prev['post'])[:,j].tolist(),
            't':t.tolist(),'c':c.tolist(),'offset':offset.tolist(),'donors':donor.tolist(),
            'weights':np.asarray(fit['coef'])[:,j].tolist(),'old_mappings':tr['mappings'],
            'source_model_sha256':digest(source/'source-fits'/f'fold-{f}-Full.json')}
        write_json(root/'train'/f'fold-{f}.json',package)
        checks.append({'fold':f,'train':192,'test':48,'active':149,'missing':0,'donor_valid':True})
        for p in [source/'source-fits'/f'fold-{f}-Full.json',old/'utility/fits'/f'fold-{f}-Full.json']:
            ledger.append({'path':str(p),'sha256':digest(p)})
    seal(root/'train',passed=True)
    paths=list(Path('src/proxy_analysis').rglob('*.py'))+[Path(config),Path(cfg['source_config'])]
    paths += [p for base in (source,old/'packages') for p in base.rglob('*') if p.is_file()]
    write_json(root/'contract/manifest.json',{'config':cfg,'source_root':str(source),'diagnostics_root':str(old),
        'sources':{str(p):digest(p) for p in sorted(set(paths))},'train_seal':digest(root/'train/complete.json'),
        'budget':{'solves':40,'zero_gate':10,'positive':30,'new_classifiers':0,'new_neural':0}})
    write_json(root/'contract/checks.json',checks);write_json(root/'contract/reuse.json',ledger)
    write_json(root/'contract/environment.json',{'python':platform.python_version(),'numpy':np.__version__,
        'scipy':scipy.__version__,'solver':'scipy.linalg.solve positive definite; audit gelsy','dtype':'float64','device':'cpu'})
    seal(root/'contract',passed=True);print('Decision calibration frozen',flush=True)


def verify(config=CONFIG):
    cfg,root=settings(config);validate_complete(root/'contract');m=read(root/'contract/manifest.json')
    if cfg!=m['config']:raise ValueError('Configuration changed')
    for p,h in m['sources'].items():
        if digest(Path(p))!=h:raise ValueError('Source changed: '+p)
    validate_complete(root/'train')
    if digest(root/'train/complete.json')!=m['train_seal']:raise ValueError('Training package changed')
    return cfg,root,Path(m['source_root'])


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['freeze','verify']);p.add_argument('--config',default=str(CONFIG))
    a=p.parse_args();globals()[a.command](a.config)
