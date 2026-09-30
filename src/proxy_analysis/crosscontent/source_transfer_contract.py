"""Immutable reuse ledger and separate pre/post inputs for source classifier transfer."""
import argparse
from pathlib import Path
import platform
import numpy as np
import pyarrow
import sklearn
import yaml
from .group_anchor_diagnostics_contract import verify as verify_diagnostics, nullable
from .group_anchor_contract import identity_check
from .source_transfer_coordinates import subsets,fit_source,scale_selected
from .natural_pair_ssl_data import audit_partition,cyclic_donors
from .mechanism_contract import read,cohort
from .business_representations import matrix
from .paired_structure_contract import seal,validate_complete
from ..paired_information.prepare import digest,table
from ..reproducibility.preflight import write_json

CONFIG=Path('configs/source-transfer-0916.yaml')


def settings(config=CONFIG):
    cfg=yaml.safe_load(Path(config).read_text(encoding='utf-8'))
    return cfg,Path(cfg['diagnostics_root']),Path(cfg['output_root'])


def freeze(config=CONFIG):
    cfg,old,root=settings(config);verify_diagnostics(cfg['diagnostics_config'])
    for part in ('utility','recovery','audit','report'):validate_complete(old/part)
    if root.exists():raise FileExistsError(root)
    source=Path(cfg['business_root']);identity=identity_check(source)
    lookup={r['session_id']:r for r in cohort(source)};captures={};ledger=[];checks=[]
    for r in table(source/'capture-audit.parquet'):captures.setdefault(r['session_id'],[]).append(r)
    if list(subsets())!=cfg['subsets']:raise ValueError('Subset definitions differ')
    for fold in range(cfg['folds']):
        tr=read(old/'packages'/f'fold-{fold}.train.json');ev=read(old/'evaluation'/f'fold-{fold}.json')
        train=[lookup[r['session_id']] for r in tr['rows']];test=[lookup[r['session_id']] for r in ev['rows']]
        isolation=audit_partition(train,test,captures)
        if tr['donors']!=cyclic_donors(tr['rows']):raise ValueError('Training donors changed')
        raw_pre=matrix(train,'pre','distribution157');raw_post=matrix(test,'post','distribution157')
        if not np.allclose(raw_pre,np.array(tr['raw_pre'],float),equal_nan=True):raise ValueError('Raw pre changed')
        if not np.allclose(scale_selected(raw_post,tr['post_scaler'],list(range(157))),
                           read(old/'packages'/f'fold-{fold}.input.json')['post'],atol=1e-12):raise ValueError('Post coordinate changed')
        source_scaler=fit_source(raw_pre,tr['pre_scaler'],cfg['numerical_eps'])
        valid=np.array(tr['target_mask']).any(0)
        if np.any(np.array(source_scaler['active']) & ~valid):raise ValueError('Unmapped source dimensions')
        mappings={}
        for arm,name in (('C','Ridge-true'),('D','Ridge-wrong')):
            path=old/'recovery/fits'/f'fold-{fold}-{name}.json';fit=read(path)
            ids=[r['session_id'] for r in tr['rows']]
            donor_ids=ids if arm=='C' else [ids[i] for i in tr['donors']]
            if fit['train_ids']!=ids or fit['donor_ids']!=donor_ids or fit['fits']!=int(valid.sum()) or fit['alpha']!=1.:
                raise ValueError('Ridge reuse contract mismatch')
            mappings[arm]=fit;ledger.append({'type':'mapping','fold':fold,'arm':arm,'path':str(path),'sha256':digest(path)})
        write_json(root/'train'/f'fold-{fold}.json',{'fold':fold,'rows':tr['rows'],'labels':tr['labels'],
            'raw_pre':nullable(raw_pre),'source_scaler':source_scaler,'post_scaler':tr['post_scaler'],
            'target_scaler':tr['pre_scaler'],'mappings':mappings})
        ids=[r['session_id'] for r in ev['rows']]
        write_json(root/'post-input'/f'fold-{fold}.json',{'fold':fold,'session_ids':ids,'raw_post':nullable(raw_post)})
        write_json(root/'pre-reference'/f'fold-{fold}.json',{'fold':fold,'session_ids':ids,
            'raw_pre':nullable(matrix(test,'pre','distribution157'))})
        write_json(root/'evaluation'/f'fold-{fold}.json',{'fold':fold,'rows':ev['rows']})
        for subset,indices in subsets().items():
            path=old/'utility/fits'/f'fold-{fold}-{subset}.json';fit=read(path)
            if fit['indices']!=indices or fit['labels']!=tr['labels'] or fit['train_ids']!=[r['session_id'] for r in tr['rows']]:
                raise ValueError('E reuse contract mismatch')
            ledger.append({'type':'E-classifier','fold':fold,'subset':subset,'path':str(path),'sha256':digest(path)})
        checks.append({'fold':fold,**isolation,'source_active_dimensions':int(sum(source_scaler['active'])),
            'pre_inactive_post_variable_indices':[j for j,v in enumerate(source_scaler['active'])
                                                 if not v and tr['post_scaler']['variance'][j]>cfg['numerical_eps']]})
    parts=['train','post-input','pre-reference','evaluation']
    for part in parts:seal(root/part,passed=True)
    write_json(root/'contract/reuse.json',ledger);write_json(root/'contract/partitions.json',checks)
    paths=list(Path('src/proxy_analysis').rglob('*.py'))+[Path(config),Path(cfg['diagnostics_config']),
        source/'side-summaries.parquet',source/'capture-audit.parquet',source/'identity-gate.json']
    paths += [p for part in ('contract','packages','evaluation','utility','recovery','audit') for p in (old/part).rglob('*') if p.is_file()]
    write_json(root/'contract/manifest.json',{'config':cfg,'sources':{str(p):digest(p) for p in sorted(set(paths))},
        'package_seals':{part:digest(root/part/'complete.json') for part in parts},'identity_gate':identity,
        'new_source_fits':35,'reused_E_models':35,'reused_mapping_files':10,
        'scope':'A may read test pre; B-D accept raw post only; paired calibration in seen deployments'})
    write_json(root/'contract/environment.json',{'python':platform.python_version(),'numpy':np.__version__,
        'sklearn':sklearn.__version__,'device':'cpu','dtype':'float64'})
    seal(root/'contract',passed=True);print('Source transfer frozen: 35 source fits, 45 reused artifacts',flush=True)


def verify(config=CONFIG):
    cfg,old,root=settings(config);validate_complete(root/'contract');manifest=read(root/'contract/manifest.json')
    if cfg!=manifest['config']:raise ValueError('Config changed')
    for p,h in manifest['sources'].items():
        if digest(Path(p))!=h:raise ValueError(f'Frozen source changed: {p}')
    for part,h in manifest['package_seals'].items():
        if digest(root/part/'complete.json')!=h:raise ValueError('Package seal changed')
        validate_complete(root/part)
    return cfg,old,root


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=['freeze','verify'])
    parser.add_argument('--config',default=str(CONFIG));args=parser.parse_args();globals()[args.command](args.config)
