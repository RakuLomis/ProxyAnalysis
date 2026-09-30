from copy import deepcopy
import numpy as np
from proxy_analysis.crosscontent.paired_constraint_runner import prepare,specification
from proxy_analysis.paired_information.reference_retrain import SCALAR_NAMES


def fixture():
    rows={};member={'train_ids':[],'test_ids':[],'target_ids':[]}
    for label in ['a','b']:
        for content in range(5):
            for protocol in (['SS'] if content<4 else ['SS','VL']):
                for repetition in [1,2,4,5]:
                    sid=f'{label}{content}-{protocol}-{repetition}'
                    values={k:float(1+i+content+repetition) for i,k in enumerate(SCALAR_NAMES)}
                    rows[sid]={'session_id':sid,'content_id':f'{label}{content}','label_id':label,
                        'protocol':protocol,'repetition':repetition,'post':values,
                        'pre':{k:v*.8 for k,v in values.items()}}
                    part='train_ids' if content<4 else 'test_ids' if protocol=='SS' else 'target_ids'
                    member[part].append(sid)
    return rows,member


def test_target_cannot_change_training_parameters_or_pair_matrices():
    rows,m=fixture();a=prepare(rows,m,'SS');changed=deepcopy(rows)
    for sid in m['target_ids']+m['test_ids']:
        changed[sid]['pre']={}
        changed[sid]['post']={k:1e10 for k in SCALAR_NAMES}
    b=prepare(changed,m,'SS')
    assert a[3]==b[3] and a[4]==b[4] and a[5]==b[5]
    assert np.array_equal(a[2]['train'],b[2]['train'])


def test_budget_and_matrices():
    rows,m=fixture();_,_,_,_,matrices,maps,_=prepare(rows,m,'SS')
    for arm,r in matrices.items():
        c=np.asarray(r['normalized']);assert np.trace(c)==14 or np.isclose(np.trace(c),14)
        assert np.linalg.eigvalsh(c).min()>-1e-8
    assert len(maps)==len(m['train_ids'])*4
    assert len(specification({'lambdas':[.01,.1,1.]}))*20==320
