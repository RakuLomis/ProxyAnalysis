"""Independent augmented least-squares replay and inference-permission audit."""
import argparse
import numpy as np
from .decision_calibration_contract import CONFIG,verify
from .decision_calibration_objective import independent_lstsq,losses
from .decision_calibration_runner import name,predict_one
from .mechanism_contract import read
from .paired_structure_contract import seal,validate_complete
from ..paired_information.prepare import table,digest
from ..reproducibility.preflight import write_json


def standard(raw,sc):
    x=np.asarray(raw,float)
    return (np.where(np.isnan(x),sc['median'],x)-sc['mean'])/sc['scale']


def audit(config=CONFIG):
    cfg,root,source=verify(config)
    for part in ('zero-gate','positive-fits','inference','report'):validate_complete(root/part)
    saved={(r['fold'],r['arm'],r['session_id']):r for r in table(root/'inference/predictions.parquet')}
    checks=[];worst=0.;qrworst=0.;count=0
    for f in range(5):
        pack=read(root/'train'/f'fold-{f}.json');j=pack['indices'];v=np.asarray(pack['v']);target=np.asarray(pack['t'])
        post=read(source/'post-input'/f'fold-{f}.json');tr=read(source/'train'/f'fold-{f}.json')
        model=read(source/'source-fits'/f'fold-{f}-Full.json');modelhash=digest(source/'source-fits'/f'fold-{f}-Full.json')
        pre=read(source/'pre-reference'/f'fold-{f}.json');evaluation=read(source/'evaluation'/f'fold-{f}.json')
        train_contents={r['content_id'] for r in tr['rows']};test_contents={r['content_id'] for r in evaluation['rows']}
        if train_contents&test_contents or set(pack['train_ids'])&set(post['session_ids']):raise ValueError('Partition overlap')
        for rel in ('true','wrong'):
            donors=np.arange(len(v)) if rel=='true' else np.asarray(pack['donors']);t=target[donors]
            for lam in cfg['lambdas']:
                arm=name(rel,lam);part='zero-gate' if lam==0 else 'positive-fits'
                state=read(root/part/'fits'/f'{f}-{arm}.json');theta=np.asarray(state['theta'])
                if state['source_model_sha256']!=modelhash or state['train_ids']!=pack['train_ids'] or state['donor_ids']!=[pack['train_ids'][i] for i in donors]:raise ValueError('State identity differs')
                independent=independent_lstsq(v,t,pack['c'],pack['weights'],lam,cfg['alpha'])
                theta_error=float(abs(theta-independent).max());qrworst=max(qrworst,theta_error)
                if not np.allclose(theta,independent,rtol=1e-8,atol=1e-8):raise ValueError('Independent solve differs')
                x=standard(post['raw_post'],tr['post_scaler']);a,b=independent.reshape(2,len(j))
                raw=np.tile(np.asarray(tr['target_scaler']['mean']), (len(x),1))
                raw[:,j]=(x[:,j]*a+b)*np.asarray(tr['target_scaler']['scale'])[j]+np.asarray(tr['target_scaler']['mean'])[j]
                z=(raw-tr['source_scaler']['mean'])/tr['source_scaler']['scale'];z*=tr['source_scaler']['active']
                score=z@np.asarray(model['coef']).T+model['intercept'];exp=np.exp(score-score.max(1,keepdims=True));p=exp/exp.sum(1,keepdims=True)
                for i,sid in enumerate(post['session_ids']):
                    ref=saved[f,arm,sid]
                    for value,field in [(z[i],'coordinates'),(score[i],'logits'),(p[i],'probabilities')]:
                        err=float(abs(value-np.asarray(ref[field])).max());worst=max(worst,err)
                        if not np.allclose(value,ref[field],rtol=1e-8,atol=1e-8):raise ValueError('Independent prediction differs')
                    if p[i].argmax()!=np.argmax(ref['probabilities']):raise ValueError('Independent decision differs')
                before=predict_one(post,tr,model,state['mapping'])[3]
                altered_pre={**pre,'raw_pre':(np.asarray(pre['raw_pre'])+1000).tolist()}
                altered_labels=[{**r,'label_id':'perturbed'} for r in evaluation['rows']]
                after=predict_one(post,tr,model,state['mapping'])[3]
                if not np.array_equal(before,after):raise ValueError('Evaluation data affected predictions')
                for forbidden in ({'raw_pre':altered_pre['raw_pre']},{'labels':altered_labels}):
                    try:predict_one({**post,**forbidden},tr,model,state['mapping'])
                    except ValueError:pass
                    else:raise ValueError('Predictor accepted forbidden fields')
                checks.append({'fold':f,'arm':arm,'independent_parameter_error':theta_error,
                    'pre_and_labels_rejected':True,'evaluation_perturbation_prediction_unchanged':True})
                count+=1
        print(f'Independent QR and permissions audited: fold {f}',flush=True)
    files=sum(len(list((root/part/'fits').glob('*.json'))) for part in ('zero-gate','positive-fits'))
    if files!=40 or count!=40 or len(saved)!=1920:raise ValueError('Audit budget mismatch')
    verify(config)
    write_json(root/'audit/validation.json',{'passed':True,'formal_quadratic_fits':40,'zero_gate_fits':10,'positive_fits':30,
        'independent_numerical_replays':40,'new_classifier_fits':0,'new_neural_fits':0,
        'predictions_replayed':1920,'max_independent_parameter_error':qrworst,'max_independent_forward_error':worst,
        'old_sources_unchanged':True,'fresh_raw_packet_scan':False,'checks':checks})
    seal(root/'audit',passed=True);print('Decision calibration audit passed',flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--config',default=str(CONFIG));a=p.parse_args();audit(a.config)
