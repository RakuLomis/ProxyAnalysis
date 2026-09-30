"""Directional packages: source-only fit, held-out pre/post separated."""
import argparse
from pathlib import Path
from collections import Counter
import numpy as np
import yaml
from .source_hierarchy_contract import verify as verify_center,groups
from .mechanism_contract import read
from .natural_pair_ssl_data import audit_partition
from .paired_structure_contract import seal,validate_complete
from ..paired_information.prepare import table,digest
from ..reproducibility.preflight import write_json

CONFIG=Path('configs/source-calibration-cross-deployment-0916.yaml')


def settings(config=CONFIG):
    cfg=yaml.safe_load(Path(config).read_text(encoding='utf-8'));return cfg,Path(cfg['output_root'])


def contexts(cfg):return [(pr,f,f'{pr}-{f}') for pr in cfg['directions'] for f in range(cfg['folds'])]


def freeze(config=CONFIG):
    cfg,root=settings(config);_,center,decision,source=verify_center(cfg['center_config'])
    validate_complete(center/'audit');validate_complete(center/'report')
    if root.exists():raise FileExistsError(root)
    diag=Path(read(decision/'contract/manifest.json')['diagnostics_root'])
    captures={}
    capture_path=Path('outputs/content-generalization-20260916/business-01/capture-audit.parquet')
    for r in table(capture_path):captures.setdefault(r['session_id'],[]).append(r)
    checks=[]
    for protocol,f,key in contexts(cfg):
        old=read(diag/'packages'/f'fold-{f}.train.json');test=read(source/'evaluation'/f'fold-{f}.json')['rows']
        post=read(source/'post-input'/f'fold-{f}.json');pre=read(source/'pre-reference'/f'fold-{f}.json')
        ix=[i for i,r in enumerate(old['rows']) if r['protocol']==protocol];rows=[old['rows'][i] for i in ix]
        banned=[r for r in old['rows'] if r['protocol']!=protocol]
        if len(rows)!=96 or len(banned)!=96 or len(groups(rows))!=24 or set(Counter(r['label_id'] for r in rows).values())!={16}:raise ValueError('Source cohort mismatch')
        isolation=audit_partition(rows,test,captures)
        write_json(root/'train'/f'{key}.json',{'context':key,'fold':f,'source_protocol':protocol,'rows':rows,'labels':old['labels'],
            'raw_pre':[old['raw_pre'][i] for i in ix],'raw_post':[old['raw_post'][i] for i in ix]})
        write_json(root/'forbidden'/f'{key}.json',{'rows':banned,'numeric_data_exported':False})
        for domain in ('source','target'):
            ti=[i for i,r in enumerate(test) if (r['protocol']==protocol)==(domain=='source')];ev=[test[i] for i in ti]
            if len(ti)!=24:raise ValueError('Evaluation cohort mismatch')
            sid=[r['session_id'] for r in ev]
            if sid!=[post['session_ids'][i] for i in ti] or sid!=[pre['session_ids'][i] for i in ti]:raise ValueError('Evaluation ordering')
            write_json(root/'post-input'/f'{key}-{domain}.json',{'fold':f,'session_ids':sid,'raw_post':[post['raw_post'][i] for i in ti]})
            write_json(root/'pre-reference'/f'{key}-{domain}.json',{'fold':f,'session_ids':sid,'raw_pre':[pre['raw_pre'][i] for i in ti]})
            write_json(root/'evaluation'/f'{key}-{domain}.json',{'rows':ev})
        checks.append({'context':key,**isolation,'train_protocols':[protocol],'source_train_visits':96,'target_forbidden_visits':96,'source_test':24,'target_test':24})
    parts=['train','forbidden','post-input','pre-reference','evaluation']
    for p in parts:seal(root/p,passed=True)
    paths=list(Path('src/proxy_analysis').rglob('*.py'))+[Path(config),capture_path]
    paths += [p for base in (center,decision,source,diag/'packages') for p in base.rglob('*') if p.is_file()]
    write_json(root/'contract/manifest.json',{'config':cfg,'source_root':str(source),'sources':{str(p):digest(p) for p in sorted(set(paths))},
        'package_seals':{p:digest(root/p/'complete.json') for p in parts},'historical_target_visibility':True})
    write_json(root/'contract/partitions.json',checks);seal(root/'contract',passed=True);print('Cross-deployment source-only packages frozen',flush=True)


def verify(config=CONFIG):
    cfg,root=settings(config);validate_complete(root/'contract');m=read(root/'contract/manifest.json')
    if cfg!=m['config']:raise ValueError('Configuration changed')
    for p,h in m['sources'].items():
        if digest(Path(p))!=h:raise ValueError('Frozen source changed: '+p)
    for part,h in m['package_seals'].items():
        validate_complete(root/part)
        if digest(root/part/'complete.json')!=h:raise ValueError('Package seal changed')
    return cfg,root


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['freeze','verify']);p.add_argument('--config',default=str(CONFIG));a=p.parse_args();globals()[a.command](a.config)
