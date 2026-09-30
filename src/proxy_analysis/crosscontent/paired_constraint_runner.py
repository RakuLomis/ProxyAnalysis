"""P7 approved high-precision R0 and fixed linear pair-moment controls."""
import argparse
from pathlib import Path
import numpy as np
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler

from .paired_structure_contract import CONFIG,verify,read,seal,validate_complete
from .paired_constraint_objective import fit,probability,moment,donor_indices
from .business_representations import matrix
from .joint_teacher import source_guard,array_digest
from ..paired_information.prepare import table,digest
from ..reproducibility.preflight import write_json,write_table


def prepare(rows,member,protocol):
    train=[rows[s] for s in member['train_ids']];test=[rows[s] for s in member['test_ids']]
    target=[rows[s] for s in member['target_ids']];source_guard(train,test,target,protocol)
    labels=sorted({r['label_id'] for r in train});y=np.array([labels.index(r['label_id']) for r in train])
    imp=SimpleImputer(strategy='median',keep_empty_features=True)
    xraw=matrix(train,'post','scalar14');xi=imp.fit_transform(xraw);sc=StandardScaler().fit(xi)
    x=sc.transform(xi);a=sc.transform(imp.transform(matrix(train,'pre','scalar14')))
    transforms={'train':x,'test':sc.transform(imp.transform(matrix(test,'post','scalar14'))),
                'target':sc.transform(imp.transform(matrix(target,'post','scalar14')))}
    matrices={};maps=[]
    for arm,indices in [('R-True',np.arange(len(train)))]+[(f'R-Wrong-{s}',donor_indices(train,s)) for s in (1,2,3)]:
        d=x-a[indices];raw,cov=moment(d);eigen=np.linalg.eigvalsh(raw);tr=float(np.trace(raw))
        matrices[arm]={'raw':raw.tolist(),'normalized':cov.tolist(),'mean_delta':d.mean(0).tolist(),
            'trace':tr,'eigenvalues':eigen.tolist(),
            'participation_rank':float(tr*tr/np.sum(eigen**2)) if tr>0 else 0.,
            'matrix_rank':int(np.linalg.matrix_rank(raw)),'difference_sha256':array_digest(d)}
        maps.extend({'arm':arm,'receiver':r['session_id'],'donor':train[indices[i]]['session_id']} for i,r in enumerate(train))
    matrices['R-Iso']={'normalized':np.eye(14).tolist(),'trace':14.}
    state={'imputer_statistics':imp.statistics_.tolist(),'scaler_mean':sc.mean_.tolist(),'scaler_scale':sc.scale_.tolist()}
    return labels,y,transforms,state,matrices,maps,{'train':train,'test':test,'target':target}


def specification(cfg):
    return [('R0',0.)]+[(arm,float(lam)) for lam in cfg['lambdas']
        for arm in ['R-True','R-Wrong-1','R-Wrong-2','R-Wrong-3','R-Iso']]


def run(config=CONFIG):
    cfg,source,legacy,root=verify(config);out=root/'p7-models';eng=out/'engineering'
    validate_complete(eng);gate=read(eng/'gate.json')
    if not all(r['strict_parity_passed'] for r in read(eng/'baseline-parity.json')):
        raise ValueError('Strict reference parity gate failed; approval does not waive this')
    for p,h in gate['code_sha256'].items():
        if digest(Path(p))!=h:raise ValueError('Engineering implementation changed')
    contract=out/'formal-contract'
    if not contract.exists():
        contract.mkdir()
        write_json(contract/'approval.json',{'decision':'Use new high-precision R0 for all P7 controls; old M0 stays historical',
            'user_confirmation':'可采用新的R0。', 'resume_request':'好的，请你根据MLP的结果来继续，P7',
            'historical_gate_retained':True,'original_engineering_gate_sha256':digest(eng/'gate.json'),
            'MLP_results_not_used_for_parameter_selection':True})
        paths=[Path(__file__),Path(__file__).with_name('paired_constraint_objective.py'),Path(config)]
        write_json(contract/'implementation.json',{'sources':{str(p):digest(p) for p in paths},
            'specification':specification(cfg),'formal_fit_budget':320,'additional_engineering_fits':0})
        seal(contract,passed=True)
    validate_complete(contract)
    for p,h in read(contract/'implementation.json')['sources'].items():
        if digest(Path(p))!=h:raise ValueError('Formal implementation changed')
    rows={r['session_id']:r for r in table(source/'side-summaries.parquet') if r['selection']=='observed' and r['primary_candidate']}
    jobpaths=[]
    for task in cfg['tasks']:
        for protocol in cfg['protocols']:
            for fold in range(5):
                name=f'{task}-{protocol}-{fold}';old=legacy/'jobs'/f'{name}-scalar14';validate_complete(old)
                member=read(old/'membership.json');labels,y,x,prep,matrices,maps,parts=prepare(rows,member,protocol)
                context={'task':task,'protocol':protocol,'outer_fold':fold,'representation':'scalar14'}
                dest=out/'formal-jobs'/name;jobpaths.append(dest)
                if dest.exists():validate_complete(dest);continue
                records=[];predictions=[];baseline=None
                for arm,lam in specification(cfg):
                    cov=np.zeros((14,14)) if arm=='R0' else np.array(matrices[arm]['normalized'])
                    try: state=fit(x['train'],y,len(labels),cov,lam,cfg)
                    except Exception as error:
                        write_json(out/'failure.json',{'context':context,'arm':arm,'lambda':lam,
                            'error':repr(error),'completed_in_context':len(records),'requires_diagnosis':True})
                        raise
                    if arm=='R0':baseline=state
                    w=np.array(state['coef']);centered=w/np.sqrt(2) if len(w)==1 else w-w.mean(0)
                    true_pen=float(np.sum(centered@np.array(matrices['R-True']['normalized'])*centered))
                    fit_id=f'{name}:{arm}:{lam}'
                    records.append({**context,'arm':arm,'lambda':lam,'fit_id':fit_id,'state':state,
                        'labels':labels,'train_ids':member['train_ids'],'preprocessing':prep,
                        'x_sha256':array_digest(x['train']),'y':y.tolist(),'matrix_sha256':array_digest(cov),
                        'true_normalized_pair_penalty':true_pen,'weight_norm_squared':float(np.sum(w*w)),
                        'training_accuracy':float(np.mean(probability(x['train'],state).argmax(1)==y))})
                    for part,stage in [('test','student'),('target','cross')]:
                        p=probability(x[part],state)
                        for r,prob in zip(parts[part],p):
                            truth=labels.index(r['label_id'])
                            predictions.append({**context,'arm':arm,'lambda':lam,'fit_id':fit_id,'stage':stage,
                                'session_id':r['session_id'],'content_id':r['content_id'],'label_id':r['label_id'],
                                'evaluation_protocol':r['protocol'],'truth':truth,'probabilities':prob.tolist(),
                                'loss_bits':float(-np.log2(max(prob[truth],1e-12)))})
                dest.mkdir(parents=True);write_json(dest/'membership.json',member)
                write_json(dest/'matrices.json',matrices);write_json(dest/'fit-ledger.json',records)
                write_table(dest/'donor-maps.parquet',maps);write_table(dest/'predictions.parquet',predictions)
                seal(dest,passed=True,fresh_fits=len(records));print({'completed_context':name,'fits':len(records)},flush=True)
    if len(jobpaths)*len(specification(cfg))!=cfg['formal_fit_budget']:raise ValueError('Budget mismatch')
    write_json(out/'formal-complete.json',{'formal_fits':320,'prior_engineering_fits':8,
        'target_fits':0,'teacher_fits':0,'jobs':{j.name:digest(j/'complete.json') for j in jobpaths}})


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--config',default=str(CONFIG));run(p.parse_args().config)
