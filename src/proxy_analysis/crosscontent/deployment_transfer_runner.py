"""20 fixed logistic classifiers and 20 affine calibrators; post inference first."""
import argparse
import numpy as np
from sklearn.linear_model import LogisticRegression
from .deployment_transfer_contract import CONFIG,verify,contexts
from .decision_calibration_objective import fit as solve,quadratic
from .decision_calibration_runner import mapping
from .source_transfer_coordinates import coordinate,logits
from .natural_pair_ssl_report import softmax
from .mechanism_contract import read
from .paired_structure_contract import seal,validate_complete
from ..paired_information.prepare import digest,table
from ..reproducibility.preflight import write_json,write_table


def forward(bundle,state,model,arm,params=None):
    numerical={'F':'C','H':'C'}.get(arm,arm)
    z,raw=coordinate(bundle,numerical,list(range(157)),state['source_scaler'],state['post_scaler'],state['target_scaler'],params)
    score=logits(z,model);prob=softmax(score)
    if not np.isfinite(prob).all() or not np.isfinite(score).all():raise ValueError('Nonfinite inference')
    return z,raw,score,prob


def classifiers(config=CONFIG):
    cfg,root=verify(config);validate_complete(root/'prepared');out=root/'classifiers'
    if out.exists():raise FileExistsError(out)
    worst=0.;count=0
    for _,f,key in contexts(cfg):
        p=read(root/'prepared'/f'{key}.json')
        for side in ('pre','post'):
            x=np.asarray(p[side]);m=LogisticRegression(C=cfg['classifier_C'],solver='lbfgs',tol=cfg['classifier_tol'],max_iter=cfg['classifier_max_iter'],random_state=20260919).fit(x,p['y'])
            if m.n_iter_.max()>=cfg['classifier_max_iter']:raise ValueError('LR not converged')
            state={'context':key,'side':side,'coef':m.coef_.tolist(),'intercept':m.intercept_.tolist(),
                'classes':m.classes_.tolist(),'labels':p['labels'],'train_ids':p['train_ids'],'n_iter':m.n_iter_.tolist(),
                'prepared_sha256':digest(root/'prepared'/f'{key}.json')}
            worst=max(worst,float(abs(softmax(logits(x,state))-m.predict_proba(x)).max()))
            if side=='pre' and np.any(np.asarray(m.coef_)[:,~np.asarray(p['source_scaler']['active'])]!=0):raise ValueError('Inactive source weights')
            write_json(out/f'{key}-{side}.json',state);count+=1
        print('Source classifiers fitted: '+key,flush=True)
    if count!=20 or worst>1e-10:raise ValueError('Classifier budget/replay')
    write_json(out/'validation.json',{'passed':True,'fits':count,'max_probability_replay_error':worst,'fit_numeric_inputs':'source prepared package only'})
    seal(out,passed=True)


def calibrate(config=CONFIG):
    cfg,root=verify(config);validate_complete(root/'classifiers');out=root/'calibrations'
    if out.exists():raise FileExistsError(out)
    count=0
    for _,f,key in contexts(cfg):
        p=read(root/'prepared'/f'{key}.json');m=read(root/'classifiers'/f'{key}-pre.json');j=p['indices']
        v=np.asarray(p['post'])[:,j];w=np.asarray(m['coef'])[:,j]
        h,_=quadratic(v,p['t'],p['c'],w,1);hc,_=quadratic(v,p['center'],p['c'],w,1)
        if not np.array_equal(h,hc):raise ValueError('Hessian changed')
        for arm,target in [('F',p['t']),('H',p['center'])]:
            theta,stats=solve(v,target,p['c'],w,cfg['lambda'],cfg['alpha'])
            write_json(out/f'{key}-{arm}.json',{'context':key,'arm':arm,'theta':theta.tolist(),'mapping':mapping(theta,p),
                'statistics':stats,'train_ids':p['train_ids'],'indices':j,'prepared_sha256':digest(root/'prepared'/f'{key}.json'),
                'source_model_sha256':digest(root/'classifiers'/f'{key}-pre.json')});count+=1
        print('Source F/H calibrated: '+key,flush=True)
    if count!=20:raise ValueError('Calibration budget')
    write_json(out/'validation.json',{'passed':True,'fits':20,'new_neural_fits':0});seal(out,passed=True)


def predict(config=CONFIG):
    cfg,root=verify(config);validate_complete(root/'calibrations');out=root/'inference'
    if out.exists():raise FileExistsError(out)
    def phase(pre=False):
        rows=[]
        for protocol,f,key in contexts(cfg):
            state=read(root/'prepared'/f'{key}.json')
            for domain in ('source','target'):
                bundle=read(root/('pre-reference' if pre else 'post-input')/f'{key}-{domain}.json')
                for arm in (['A'] if pre else ['B','F','H','E']):
                    modelpath=root/'classifiers'/f'{key}-{"post" if arm=="E" else "pre"}.json'
                    model=read(modelpath);params=read(root/'calibrations'/f'{key}-{arm}.json')['mapping'] if arm in ('F','H') else None
                    z,raw,score,prob=forward(bundle,state,model,arm,params)
                    for i,sid in enumerate(bundle['session_ids']):rows.append({'context':key,'source_protocol':protocol,'fold':f,'domain':domain,
                        'session_id':sid,'arm':arm,'labels':model['labels'],'coordinates':z[i].tolist(),'logits':score[i].tolist(),
                        'probabilities':prob[i].tolist(),'raw_recovered':raw[i].tolist() if raw is not None else None,'model_sha256':digest(modelpath)})
        return rows
    post=phase();write_table(out/'post/predictions.parquet',post);seal(out/'post',passed=True)
    pre=phase(True);write_table(out/'pre/predictions.parquet',pre);seal(out/'pre',passed=True)
    if len(post)!=1920 or len(pre)!=480:raise ValueError('Prediction count')
    write_table(out/'predictions.parquet',post+pre);write_json(out/'validation.json',{'passed':True,'predictions':2400,'post_predictions_before_test_pre':1920})
    seal(out,passed=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['classifiers','calibrate','predict']);p.add_argument('--config',default=str(CONFIG));a=p.parse_args();globals()[a.command](a.config)
