"""Train 35 pre classifiers once; infer B-E before loading the separate A input."""
import argparse
import numpy as np
from sklearn.linear_model import LogisticRegression
from .source_transfer_contract import CONFIG,verify
from .source_transfer_coordinates import subsets,coordinate,source_selected,logits
from .natural_pair_ssl_report import softmax
from .natural_pair_ssl_data import fingerprint
from .mechanism_contract import read
from .paired_structure_contract import seal,validate_complete
from ..paired_information.prepare import table,digest
from ..reproducibility.preflight import write_json,write_table


def reuse_gate(config=CONFIG):
    cfg,old,root=verify(config);out=root/'reuse-gate'
    if (out/'complete.json').exists():validate_complete(out);return
    expected={(r['fold'],r['subset'],r['session_id']):r['probabilities'] for r in table(old/'utility/predictions.parquet')}
    ridge={(r['fold'],r['model'],r['session_id']):r['prediction'] for r in table(old/'recovery/predictions.parquet')
           if r['split']=='test' and r['model'] in ('Ridge-true','Ridge-wrong')}
    worst=0.;count=0
    for fold in range(5):
        tr=read(root/'train'/f'fold-{fold}.json');bundle=read(root/'post-input'/f'fold-{fold}.json')
        for subset,indices in subsets().items():
            fit=read(old/'utility/fits'/f'fold-{fold}-{subset}.json')
            z,_=coordinate(bundle,'E',indices,tr['source_scaler'],tr['post_scaler'],tr['target_scaler'])
            p=softmax(logits(z,fit));reference=np.array([expected[fold,subset,sid] for sid in bundle['session_ids']])
            worst=max(worst,float(abs(p-reference).max()));count+=1
        for arm,name in (('C','Ridge-true'),('D','Ridge-wrong')):
            indices=list(range(157))
            z,raw_hat=coordinate(bundle,arm,indices,tr['source_scaler'],tr['post_scaler'],tr['target_scaler'],tr['mappings'][arm])
            reference=np.array([ridge[fold,name,sid] for sid in bundle['session_ids']])
            expected_raw=reference*np.array(tr['target_scaler']['scale'])+tr['target_scaler']['mean']
            expected_z=source_selected(expected_raw,tr['source_scaler'],indices)
            worst=max(worst,float(abs(z-expected_z).max()))
    if count!=35 or worst>1e-10:raise ValueError('Reuse probability/coordinate replay failed')
    write_json(out/'validation.json',{'passed':True,'E_models':35,'mapping_files':10,'max_replay_error':worst,'new_fits':0})
    seal(out,passed=True);print('Reuse gate passed: 35 E models and 10 mapping files',flush=True)


def fit(config=CONFIG):
    cfg,_,root=verify(config);validate_complete(root/'reuse-gate');out=root/'source-fits'
    if (out/'complete.json').exists():validate_complete(out);return
    if out.exists():raise FileExistsError('Partial source fits exist; do not silently refit')
    count=0;worst=0.
    for fold in range(5):
        tr=read(root/'train'/f'fold-{fold}.json');y=np.array([tr['labels'].index(r['label_id']) for r in tr['rows']])
        for subset,indices in subsets().items():
            x=source_selected(tr['raw_pre'],tr['source_scaler'],indices)
            model=LogisticRegression(C=cfg['classifier_C'],solver='lbfgs',max_iter=cfg['classifier_max_iter'],
                tol=cfg['classifier_tol'],random_state=20260919).fit(x,y)
            if model.n_iter_.max()>=cfg['classifier_max_iter']:raise ValueError('Source LR did not converge')
            inactive=~np.array(tr['source_scaler']['active'])[indices]
            if inactive.any() and abs(model.coef_[:,inactive]).max()>1e-12:raise ValueError('Source constant column learned weight')
            state={'fold':fold,'subset':subset,'indices':indices,'labels':tr['labels'],'classes':model.classes_.tolist(),
                'coef':model.coef_.tolist(),'intercept':model.intercept_.tolist(),'n_iter':model.n_iter_.tolist(),
                'train_ids':[r['session_id'] for r in tr['rows']],'source_scaler_sha256':fingerprint(tr['source_scaler']),
                'training_input_sha256':fingerprint(x.tolist()),'training_side':'pre'}
            z=logits(x,state);p=softmax(z);worst=max(worst,float(abs(p-model.predict_proba(x)).max()))
            rivals=z.copy();rivals[np.arange(len(y)),y]=-np.inf
            margins=z[np.arange(len(y)),y]-rivals.max(1)
            state['train_margin_quartiles']=np.quantile(margins,[.25,.5,.75]).tolist()
            write_json(out/f'fold-{fold}-{subset}.json',state);count+=1
        print(f'source fold {fold}: seven pre classifiers fitted',flush=True)
    if count!=35 or worst>1e-10:raise ValueError('Source fit budget/replay failed')
    write_json(out/'validation.json',{'passed':True,'new_source_fits':count,'max_numpy_replay_error':worst,
        'test_inputs_loaded_by_fit':False,'new_post_fits':0,'new_ridge_fits':0,'new_neural_fits':0})
    seal(out,passed=True)


def physical_checks(raw,indices):
    if raw is None:return None
    bounded={8,9,10,11}  # Replaced below by names to avoid scalar-position assumptions.
    from .business_representations import dictionary,BOUNDED
    names=dictionary()['distribution157'];negative=[];outside=[]
    for local,j in enumerate(indices):
        value=raw[local];name=names[j]
        if value < -1e-9:negative.append(j)
        if (name in BOUNDED or name.startswith(('length_p_','iat_p_','curve_'))) and (value < -1e-9 or value > 1+1e-9):
            outside.append(j)
    index={j:i for i,j in enumerate(indices)}
    histogram_sums=[]
    for block in (list(range(14,33)),list(range(33,56))):
        if all(j in index for j in block):histogram_sums.append(float(sum(raw[index[j]] for j in block)))
    curve=[raw[index[j]] for j in range(56,157) if j in index]
    return {'negative_indices':negative,'unit_interval_violations':outside,'histogram_sums':histogram_sums,
            'curve_nonmonotone':bool(len(curve)==101 and (np.diff(curve)<-1e-9).any())}


def predict(config=CONFIG):
    cfg,old,root=verify(config);validate_complete(root/'source-fits');out=root/'inference'
    if (out/'complete.json').exists():validate_complete(out);return
    if out.exists():raise FileExistsError('Partial inference exists; explicit review required')
    post_rows=[];pre_rows=[]
    def records(bundle,arm,subset,indices,fit,path,z,raw_hat):
        scores=logits(z,fit);prob=softmax(scores)
        if not np.isfinite(scores).all() or not np.isfinite(prob).all():raise ValueError('Nonfinite classification')
        return [{'fold':bundle['fold'],'session_id':sid,'arm':arm,'subset':subset,'labels':fit['labels'],
                 'probabilities':p.tolist(),'logits':s.tolist(),'coordinates':xx.tolist(),'indices':indices,
                 'model_sha256':digest(path),'physical':physical_checks(hat,indices)}
                for sid,p,s,xx,hat in zip(bundle['session_ids'],prob,scores,z,
                    raw_hat if raw_hat is not None else [None]*len(z))]
    # Finish and seal post-only predictions before any test pre values are loaded.
    for fold in range(5):
        tr=read(root/'train'/f'fold-{fold}.json');bundle=read(root/'post-input'/f'fold-{fold}.json')
        for subset,indices in subsets().items():
            source_path=root/'source-fits'/f'fold-{fold}-{subset}.json';source_fit=read(source_path)
            for arm in ('B','C','D','E'):
                path=old/'utility/fits'/f'fold-{fold}-{subset}.json' if arm=='E' else source_path
                model=read(path) if arm=='E' else source_fit
                z,hat=coordinate(bundle,arm,indices,tr['source_scaler'],tr['post_scaler'],tr['target_scaler'],tr['mappings'].get(arm))
                post_rows.extend(records(bundle,arm,subset,indices,model,path,z,hat))
    write_table(out/'post/predictions.parquet',post_rows);seal(out/'post',passed=True,test_pre_used=False)
    for fold in range(5):
        tr=read(root/'train'/f'fold-{fold}.json');bundle=read(root/'pre-reference'/f'fold-{fold}.json')
        for subset,indices in subsets().items():
            path=root/'source-fits'/f'fold-{fold}-{subset}.json';model=read(path)
            z,hat=coordinate(bundle,'A',indices,tr['source_scaler'],tr['post_scaler'],tr['target_scaler'])
            pre_rows.extend(records(bundle,'A',subset,indices,model,path,z,hat))
    write_table(out/'pre/predictions.parquet',pre_rows);seal(out/'pre',passed=True,scope='A reference only')
    write_table(out/'predictions.parquet',pre_rows+post_rows)
    if len(pre_rows)!=1680 or len(post_rows)!=6720:raise ValueError('Unexpected prediction count')
    write_json(out/'validation.json',{'passed':True,'predictions':8400,'A_predictions':1680,
        'B_to_E_predictions':6720,'B_to_D_test_pre_inputs':False,'evaluation_labels_used':False})
    seal(out,passed=True);print('A-E predictions sealed: 8400 rows; B-E preceded test pre access',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=['reuse_gate','fit','predict'])
    parser.add_argument('--config',default=str(CONFIG));args=parser.parse_args();globals()[args.command](args.config)
