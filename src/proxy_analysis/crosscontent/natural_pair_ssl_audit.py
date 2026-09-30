"""Supplemental membership, initialization and input reconstruction audit."""
import argparse
from collections import defaultdict
from pathlib import Path
import numpy as np

from .natural_pair_ssl import CONFIG, verify
from .natural_pair_ssl_data import prepare_train, fingerprint
from .mechanism_contract import cohort, read
from .paired_structure_contract import validate_complete, seal
from ..paired_information.prepare import table, digest
from ..reproducibility.preflight import write_json


def audit(config=CONFIG):
    cfg,source,root=verify(config)
    lookup={r['session_id']:r for r in cohort(source)}
    identity=read(source/'identity-gate.json')
    if not identity['passed']:
        raise ValueError('Historical packet identity gate failed')
    for name,h in identity['source_hashes'].items():
        if digest(source/name)!=h:raise ValueError('Historical identity input changed')
    contexts=[];initials=defaultdict(dict);steps=0;fits=0
    for task in cfg['tasks']:
        for fold in range(5):
            name=f'{task}-{fold}';data=read(root/'prepared'/f'{name}.json')
            ssl=read(root/'prepared'/f'{name}.ssl.json')
            rows=[lookup[r['session_id']] for r in data['train']]
            rebuilt,scaler,_=prepare_train(rows)
            if fingerprint(rebuilt)!=fingerprint(ssl) or fingerprint(scaler)!=fingerprint(data['preprocessing']):
                raise ValueError('Train-only reconstruction differs')
            if ssl['session_ids']!=[r['session_id'] for r in data['train']]:
                raise ValueError('Misaligned SSL and supervised rows')
            expected_train=192 if task=='six_business' else 64
            if len(rows)!=expected_train or len(data['test'])!=expected_train//4:
                raise ValueError('Unexpected cohort size')
            contexts.append({'context':name,'reconstructed':True,**data['audit']})
    for job in sorted((root/'jobs').iterdir()):
        validate_complete(job);mem=read(job/'membership.json');group=(mem['context'],mem['seed']);arm=mem['arm']
        ft=read(job/'finetune-fit.json')
        enc={k[2:]:v for k,v in ft['initial'].items() if k.startswith('0.')}
        head={k:v for k,v in ft['initial'].items() if k.startswith('1.')}
        if arm=='B0':
            initenc=enc
        else:
            info=read(job/'ssl-fit.json');initenc=info['initial']['encoder']
            if fingerprint(enc)!=fingerprint(info['encoder']):raise ValueError('Fine-tune initialization changed')
            if fingerprint(read(job/'probe-fit.json')['encoder'])!=fingerprint(info['encoder']):
                raise ValueError('Probe encoder differs from SSL')
            if info['train_ids']!=mem['train_ids'] or info['labels_used']:
                raise ValueError('SSL membership/label violation')
        initials[group][arm]=(fingerprint(initenc),fingerprint(head))
        for stage in (['ssl'] if arm!='B0' else [])+['finetune']:
            trace=table(job/f'{stage}-trajectory.parquet')
            if len(trace)!=cfg['steps'] or [r['step'] for r in trace]!=list(range(cfg['steps'])):
                raise ValueError('Training budget differs')
            if not all(np.isfinite(list(r.values())).all() for r in trace):raise ValueError('Nonfinite trajectory')
            steps+=len(trace);fits+=1
    if len(initials)!=30 or any(set(g)!=set(['B0']+cfg['ssl_arms']) or len(set(g.values()))!=1 for g in initials.values()):
        raise ValueError('Initialization not matched across arms')
    if fits!=270 or steps!=270000:raise ValueError('Unexpected optimization budget')
    out=root/'independent-audit'
    write_json(out/'contexts.json',contexts)
    write_json(out/'validation.json',{'passed':True,'initialization_groups':30,
        'gradient_training_fits':fits,'gradient_updates':steps,'additional_linear_probe_fits':120,
        'train_input_reconstruction':True,'ssl_metadata_has_no_labels':True,
        'historical_identity_gate':identity,'fresh_raw_packet_reaudit':False,
        'audit_code_sha256':digest(Path(__file__))})
    seal(out,passed=True)
    print('Independent membership, initialization, budget and historical identity audits passed',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--config',default=str(CONFIG));args=parser.parse_args()
    audit(args.config)
