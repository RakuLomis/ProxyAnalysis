"""Per-content effects without additional fitting."""
import argparse
from collections import defaultdict
from pathlib import Path
import numpy as np
from .natural_pair_ssl import CONFIG, verify
from .mechanism_contract import read
from .paired_structure_contract import validate_complete, seal
from ..paired_information.prepare import table, digest
from ..reproducibility.preflight import write_json, write_table


def deliver(config=CONFIG):
    cfg,_,root=verify(config)
    for stage in ['report','independent-audit']:
        validate_complete(root/stage)
        if not read(root/stage/'validation.json')['passed']:raise ValueError('Failed audit')
    grouped=defaultdict(list)
    for r in table(root/'report/predictions.parquet'):
        for protocol in [r['protocol'],'pooled']:
            grouped[r['task'],r['stage'],protocol,r['content_id'],r['arm']].append(r)
    effects=[]
    for (task,stage,protocol,content,arm),a in sorted(grouped.items()):
        if arm!='B3':continue
        def per_visit(rr):
            out={}
            for r in rr:
                y=r['labels'].index(r['label_id']);p=r['probabilities']
                out[r['session_id'],r['seed']]=(-np.log2(max(p[y],1e-15)),float(np.argmax(p)!=y))
            return out
        av=per_visit(a)
        for control in (['B0'] if stage=='finetune' else [])+['B1','B2','B4']:
            bv=per_visit(grouped[task,stage,protocol,content,control])
            if set(av)!=set(bv):raise ValueError('Unpaired content effects')
            delta=np.asarray([np.asarray(bv[k])-av[k] for k in sorted(av)])
            effects.append({'task':task,'stage':stage,'protocol':protocol,'content_id':content,
                'label_id':a[0]['label_id'],'control':control,'ce_gain_bits':float(delta[:,0].mean()),
                'error_rate_gain':float(delta[:,1].mean()),'paired_predictions':len(av),
                'unique_visits':len({k[0] for k in av})})
    out=root/'delivery';write_table(out/'content-effects.parquet',effects)
    write_json(out/'validation.json',{'passed':True,'new_training_fits':0,'content_effect_rows':len(effects),
        'code_sha256':digest(Path(__file__)),'report_complete_sha256':digest(root/'report/complete.json'),
        'audit_complete_sha256':digest(root/'independent-audit/complete.json'),
        'next_stage':'not_started_requires_direction_at_S10',
        'warning':'same-content cross-repeat control retains content information; not arbitrary random pairing'})
    seal(out,passed=True)
    print(f'Delivered {len(effects)} content effects, no new fits',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--config',default=str(CONFIG));args=parser.parse_args()
    deliver(args.config)
