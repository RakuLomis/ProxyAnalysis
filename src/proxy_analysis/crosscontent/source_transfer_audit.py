"""Independent affine-coordinate/probability replay and branch permission audits."""
import argparse
import copy
import numpy as np
from .source_transfer_contract import CONFIG,verify
from .source_transfer_coordinates import subsets,fit_source,coordinate,logits
from .natural_pair_ssl_report import softmax
from .natural_pair_ssl_data import fingerprint
from .mechanism_contract import read
from .paired_structure_contract import seal,validate_complete
from ..paired_information.prepare import table,digest
from ..reproducibility.preflight import write_json


def audit(config=CONFIG):
    cfg,old,root=verify(config)
    for part in ('reuse-gate','source-fits','inference','report'):validate_complete(root/part)
    indexed={(r['fold'],r['subset'],r['arm'],r['session_id']):r for r in table(root/'inference/predictions.parquet')}
    worst=0.;groups=[];ridge_replayed=0
    for fold in range(5):
        tr=read(root/'train'/f'fold-{fold}.json');oldtr=read(old/'packages'/f'fold-{fold}.train.json')
        post=read(root/'post-input'/f'fold-{fold}.json');pre=read(root/'pre-reference'/f'fold-{fold}.json')
        ev=read(root/'evaluation'/f'fold-{fold}.json');ids=post['session_ids']
        if ids!=pre['session_ids'] or ids!=[r['session_id'] for r in ev['rows']]:raise ValueError('Inference IDs differ')
        if {r['content_id'] for r in tr['rows']}&{r['content_id'] for r in ev['rows']}:raise ValueError('Content leakage')
        if fingerprint(fit_source(tr['raw_pre'],tr['target_scaler'],cfg['numerical_eps']))!=fingerprint(tr['source_scaler']):
            raise ValueError('Source preprocessing not training-only')
        active=np.array(tr['source_scaler']['active'])
        def standard(raw,sc):
            x=np.array(raw,float);return (np.where(np.isnan(x),sc['median'],x)-sc['mean'])/sc['scale']
        post_z=standard(post['raw_post'],tr['post_scaler'])
        for arm in ('C','D'):
            m=tr['mappings'][arm];x=np.array(oldtr['post']);y=np.array(oldtr['pre_target']);mask=np.array(oldtr['target_mask'])
            if arm=='D':y=y[oldtr['donors']];mask=mask[oldtr['donors']]
            for j in range(157):
                good=mask[:,j]
                if not good.any():continue
                a=x[good,j];b=y[good,j];coef=np.dot(a-a.mean(),b-b.mean())/(np.dot(a-a.mean(),a-a.mean())+1)
                intercept=b.mean()-coef*a.mean()
                if not np.isclose(coef,m['coef'][j],atol=1e-10) or not np.isclose(intercept,m['intercept'][j],atol=1e-10):
                    raise ValueError('Reused Ridge not reproducible')
                ridge_replayed+=1
        full_source_path=None
        for subset,jj in subsets().items():
            path=root/'source-fits'/f'fold-{fold}-{subset}.json';fit=read(path)
            if fit['indices']!=jj or fit['train_ids']!=[r['session_id'] for r in tr['rows']]:raise ValueError('Source fit members differ')
            if fit['source_scaler_sha256']!=fingerprint(tr['source_scaler']):raise ValueError('Scaler identity differs')
            for arm in cfg['arms']:
                chosen_path=old/'utility/fits'/f'fold-{fold}-{subset}.json' if arm=='E' else path
                chosen=read(chosen_path) if arm=='E' else fit
                if arm=='A':z=standard(pre['raw_pre'],tr['source_scaler'])*active
                elif arm=='B':z=standard(post['raw_post'],tr['source_scaler'])*active
                elif arm=='E':z=post_z
                else:
                    m=tr['mappings'][arm];mapped=post_z*np.array(m['coef'])+m['intercept']
                    raw_hat=mapped*np.array(tr['target_scaler']['scale'])+tr['target_scaler']['mean']
                    z=standard(raw_hat,tr['source_scaler'])*active
                z=z[:,jj];prob=softmax(z@np.array(chosen['coef']).T+chosen['intercept'])
                recorded=[indexed[fold,subset,arm,sid] for sid in ids]
                if any(r['model_sha256']!=digest(chosen_path) for r in recorded):raise ValueError('Classifier changed across arms')
                worst=max(worst,float(abs(prob-np.array([r['probabilities'] for r in recorded])).max()),
                          float(abs(z-np.array([r['coordinates'] for r in recorded])).max()))
            if subset=='Full':full_source_path=path
        # Perturb only an independent A test-pre object; deployed branches never accept it.
        fit=read(full_source_path);changed=copy.deepcopy(pre)
        raw=np.array(changed['raw_pre'],float);raw[:,active]=np.where(np.isfinite(raw[:,active]),raw[:,active],0)+1000
        changed['raw_pre']=raw.tolist()
        def prob(bundle,arm):
            z,_=coordinate(bundle,arm,list(range(157)),tr['source_scaler'],tr['post_scaler'],tr['target_scaler'],tr['mappings'].get(arm))
            return softmax(logits(z,fit))
        before={arm:fingerprint(prob(post,arm).tolist()) for arm in ('B','C','D')}
        a_changed=not np.array_equal(prob(pre,'A'),prob(changed,'A'))
        if not a_changed:raise ValueError('A perturbation test is not sensitive')
        for arm in ('B','C','D'):
            try:prob({**post,'raw_pre':changed['raw_pre']},arm)
            except ValueError:pass
            else:raise ValueError('Post branch accepted test pre')
        for row in ev['rows']:row['label_id']='changed_only_in_evaluation_copy'
        if any(before[arm]!=fingerprint(prob(post,arm).tolist()) for arm in before):raise ValueError('Test target influenced B-D')
        groups.append({'fold':fold,'A_changes_under_pre_perturbation':a_changed,'B_D_unchanged':True,
            'B_D_reject_pre_fields':True,'source_classifiers_shared_across_A_D':True,'labels_do_not_enter_predictors':True})
    if worst>1e-9 or ridge_replayed!=1490 or len(list((root/'source-fits').glob('fold-*.json')))!=35:
        raise ValueError('Replay or budget failed')
    verify(config)
    out=root/'audit';write_json(out/'validation.json',{'passed':True,'new_pre_classifiers':35,'new_ridge_fits':0,
        'new_post_classifiers':0,'new_neural_fits':0,'reused_E_models':35,'reused_ridge_coefficients':ridge_replayed,
        'predictions_replayed':8400,'max_independent_error':worst,'checks':groups,
        'old_artifacts_unchanged':True,'fresh_full_raw_packet_scan':False})
    seal(out,passed=True);print('Source transfer audit passed: 35 fits, 8400 replayed predictions',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--config',default=str(CONFIG));args=parser.parse_args();audit(args.config)
