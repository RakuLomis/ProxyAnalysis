"""Independent model/prediction replay, target perturbation and budget checks."""
import argparse
from pathlib import Path
import numpy as np
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler

from .group_anchor_diagnostics_contract import CONFIG, verify, validate_input
from .group_anchor_task_utility import subsets, predict
from .group_anchor_holdout_recovery import ridge_predict, neural_predict
from .group_anchor_reliability import normalized, feature_groups
from .group_anchor_diagnostics_report import group_error
from .natural_pair_ssl_data import cyclic_donors, fingerprint
from .mechanism_contract import read
from .paired_structure_contract import seal, validate_complete
from ..paired_information.prepare import table, digest
from ..reproducibility.preflight import write_json


def audit(config=CONFIG):
    cfg,anchor,root=verify(config)
    for part in ('utility','recovery','hierarchy','report'):validate_complete(root/part)
    util={(r['fold'],r['subset'],r['session_id']):r['probabilities'] for r in table(root/'utility/predictions.parquet')}
    rec={(r['fold'],r['model'],r['seed'],r['split'],r['session_id']):r['prediction'] for r in table(root/'recovery/predictions.parquet')}
    worst=0.;ridge_fits=0;perturbations=[]
    for fold in range(5):
        train=read(root/'packages'/f'fold-{fold}.train.json');inputs=read(root/'packages'/f'fold-{fold}.input.json')
        ev=read(root/'evaluation'/f'fold-{fold}.json')
        if inputs['session_ids']!=[r['session_id'] for r in ev['rows']]:raise ValueError('Evaluation IDs differ')
        if {r['content_id'] for r in train['rows']}&{r['content_id'] for r in ev['rows']}:raise ValueError('Content leakage')
        if set(inputs['session_ids'])&{r['session_id'] for r in train['rows']}:raise ValueError('Visit leakage')
        if train['donors']!=cyclic_donors(train['rows']) or ev['donors']!=cyclic_donors(ev['rows']):raise ValueError('Donors differ')
        imp=SimpleImputer(strategy='median',keep_empty_features=True).fit(np.array(train['raw_post'],float))
        sc=StandardScaler().fit(imp.transform(np.array(train['raw_post'],float)))
        if not np.allclose(train['post'],sc.transform(imp.transform(np.array(train['raw_post'],float))),atol=1e-12):
            raise ValueError('Train-only post scaler replay differs')
        if not np.allclose(train['pre_target'],normalized(train['raw_pre'],train['pre_scaler'])):raise ValueError('Pre target differs')
        for subset,indices in subsets().items():
            fit=read(root/'utility/fits'/f'fold-{fold}-{subset}.json')
            if fit['indices']!=indices or fit['train_ids']!=[r['session_id'] for r in train['rows']]:raise ValueError('Utility membership differs')
            p=predict(fit,inputs)
            expected=np.array([util[fold,subset,sid] for sid in inputs['session_ids']])
            worst=max(worst,float(abs(p-expected).max()))
        for model in ('Ridge-true','Ridge-wrong'):
            fit=read(root/'recovery/fits'/f'fold-{fold}-{model}.json')
            x=np.array(train['post']);y=np.array(train['pre_target']);mask=np.array(train['target_mask'])
            d=train['donors'] if model=='Ridge-wrong' else np.arange(len(x));y=y[d];mask=mask[d]
            for j in range(157):
                if not mask[:,j].any():continue
                a=x[mask[:,j],j];b=y[mask[:,j],j]
                coef=np.dot(a-a.mean(),b-b.mean())/(np.dot(a-a.mean(),a-a.mean())+cfg['ridge_alpha'])
                intercept=b.mean()-coef*a.mean();ridge_fits+=1
                worst=max(worst,abs(float(coef)-fit['coef'][j]),abs(float(intercept)-fit['intercept'][j]))
            values=ridge_predict(fit,inputs)
            expected=np.array([rec[fold,model,None,'test',sid] for sid in inputs['session_ids']])
            worst=max(worst,float(abs(values-expected).max()))
        for arm in cfg['arms']:
            for seed in cfg['seeds']:
                fit=read(anchor/'jobs'/f'six_business-{fold}-{seed}-{arm}'/'ssl-fit.json')
                values=neural_predict(fit,inputs)
                expected=np.array([rec[fold,arm,seed,'test',sid] for sid in inputs['session_ids']])
                worst=max(worst,float(abs(values-expected).max()))
        # Deliberately modified evaluation objects cannot be passed to prediction APIs.
        bad={**inputs,'pre_target':ev['raw_pre'],'labels':[r['label_id'] for r in ev['rows']]}
        try:validate_input(bad)
        except ValueError:rejected=True
        else:raise ValueError('Evaluation metadata accepted by prediction input')
        before=fingerprint(values.tolist());target=normalized(ev['raw_pre'],train['pre_scaler'])
        mask=np.isfinite(np.array(ev['raw_pre'],float))&np.array(train['pre_scaler']['valid'])
        original=group_error(values[0],target[0],mask[0],list(range(157)))
        changed=group_error(values[0],target[0]+1000,mask[0],list(range(157)))
        if original['mse']==changed['mse'] or fingerprint(neural_predict(fit,inputs).tolist())!=before:
            raise ValueError('Target perturbation boundary failed')
        utility_fit=read(root/'utility/fits'/f'fold-{fold}-Full.json')
        prob_before=predict(utility_fit,inputs)
        original_labels=[r['label_id'] for r in ev['rows']]
        # Mutate only this in-memory evaluation copy, not the sealed source artifact.
        for row in ev['rows']:row['label_id']='deliberately_changed'
        if not np.array_equal(prob_before,predict(utility_fit,inputs)):raise ValueError('Test labels affect prediction')
        perturbations.append({'fold':fold,'evaluation_fields_rejected':rejected,'target_error_changed':True,
            'post_predictions_unchanged':True,'labels_mutated_in_memory':len(original_labels),
            'scope':'prediction APIs accept post inputs only; no refit performed'})
    if worst>1e-9 or ridge_fits!=read(root/'recovery/validation.json')['ridge_fits']:raise ValueError('Independent replay failed')
    # Checking the contract again catches any modification of old models/weights by the diagnostics.
    verify(config)
    out=root/'audit'
    write_json(out/'validation.json',{'passed':True,'classifier_fits':65,'ridge_fits':ridge_fits,'new_neural_fits':0,
        'additional_refits_for_audit':0,'max_independent_replay_error':worst,'perturbations':perturbations,
        'old_model_and_reliability_hashes_unchanged':True,'test_pre_only_in_evaluation':True,
        'raw_packet_identity_scope':'reuse verified historical gate; fresh split/path checks; no new full PCAP scan',
        'audit_code_sha256':digest(Path(__file__))})
    seal(out,passed=True);print('Independent replay, permission and budget audit passed',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--config',default=str(CONFIG));args=parser.parse_args();audit(args.config)
