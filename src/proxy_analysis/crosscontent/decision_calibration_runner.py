"""Zero-lambda gate, fixed positive-lambda solves and post-only inference."""
import argparse
import numpy as np
from .decision_calibration_contract import CONFIG,verify
from .decision_calibration_objective import fit,losses
from .source_transfer_coordinates import coordinate,logits
from .natural_pair_ssl_report import softmax
from .mechanism_contract import read
from .paired_structure_contract import seal,validate_complete
from ..paired_information.prepare import table,digest
from ..reproducibility.preflight import write_json,write_table


def name(relation,lam):return 'decision_'+relation+'_lambda_'+format(lam,'g')


def mapping(theta,package):
    j=package['indices'];a,b=np.asarray(theta).reshape(2,len(j));coef=np.zeros(157);intercept=np.zeros(157)
    coef[j]=a;intercept[j]=b
    return {'coef':coef.tolist(),'intercept':intercept.tolist()}


def predict_one(post,tr,model,params):
    z,raw=coordinate(post,'C',list(range(157)),tr['source_scaler'],tr['post_scaler'],tr['target_scaler'],params)
    score=logits(z,model)
    return z,raw,score,softmax(score)


def run_fit(config=CONFIG,zero=False):
    cfg,root,source=verify(config);out=root/('zero-gate' if zero else 'positive-fits')
    if (out/'complete.json').exists():validate_complete(out);return
    if out.exists():raise FileExistsError('Partial solve directory; explicit review required')
    if not zero:validate_complete(root/'zero-gate')
    checks=[];count=0
    for f in range(5):
        p=read(root/'train'/f'fold-{f}.json');j=p['indices'];v=np.asarray(p['v']);targets=np.asarray(p['t'])
        tr=read(source/'train'/f'fold-{f}.json');model=read(source/'source-fits'/f'fold-{f}-Full.json')
        for rel,arm in [('true','C'),('wrong','D')]:
            donors=np.arange(len(v)) if rel=='true' else np.asarray(p['donors']);t=targets[donors]
            baseline=p['old_mappings'][arm];old=np.r_[np.asarray(baseline['coef'])[j],np.asarray(baseline['intercept'])[j]]
            for lam in ([0] if zero else cfg['lambdas'][1:]):
                theta,stats=fit(v,t,p['c'],p['weights'],lam,cfg['alpha'])
                before=losses(old,v,t,p['c'],p['weights'],lam,cfg['alpha'])
                if stats['total']>before['total']+1e-9*max(1,abs(before['total'])):raise ValueError('Objective increased')
                params=mapping(theta,p);record={'fold':f,'arm':name(rel,lam),'relation':rel,'lambda':lam,
                    'mapping':params,'theta':theta.tolist(),'indices':j,'statistics':stats,'baseline_objective':before,
                    'train_ids':p['train_ids'],'donor_ids':[p['train_ids'][i] for i in donors],
                    'source_model_sha256':p['source_model_sha256']}
                if zero:
                    err=float(np.max(abs(theta-old)))
                    if err>1e-9 or not np.allclose(theta,old,rtol=1e-9,atol=1e-9):raise ValueError('Zero lambda parameters differ')
                    bundle=read(source/'post-input'/f'fold-{f}.json')
                    new=predict_one(bundle,tr,model,params);ref=predict_one(bundle,tr,model,baseline)
                    forward=max(float(np.max(abs(new[k]-ref[k]))) for k in (0,2,3))
                    if forward>1e-9 or not np.array_equal(new[3].argmax(1),ref[3].argmax(1)):raise ValueError('Zero lambda forward differs')
                    checks.append({'fold':f,'relation':rel,'parameter_error':err,'forward_error':forward})
                write_json(out/'fits'/f'{f}-{name(rel,lam)}.json',record);count+=1
        print(f'Calibration fold {f}: '+('zero gate' if zero else 'positive solves'),flush=True)
    if count!=(10 if zero else 30):raise ValueError('Solve budget mismatch')
    write_json(out/'validation.json',{'passed':True,'solves':count,'new_classifier_fits':0,'checks':checks})
    seal(out,passed=True)


def predict(config=CONFIG):
    cfg,root,source=verify(config)
    for part in ('zero-gate','positive-fits'):validate_complete(root/part)
    out=root/'inference'
    if out.exists():raise FileExistsError('Do not overwrite inference')
    rows=[]
    for f in range(5):
        bundle=read(source/'post-input'/f'fold-{f}.json');tr=read(source/'train'/f'fold-{f}.json')
        model=read(source/'source-fits'/f'fold-{f}-Full.json')
        for rel in ('true','wrong'):
            for lam in cfg['lambdas']:
                arm=name(rel,lam);part='zero-gate' if lam==0 else 'positive-fits'
                state=read(root/part/'fits'/f'{f}-{arm}.json')
                z,raw,l,p=predict_one(bundle,tr,model,state['mapping'])
                for i,sid in enumerate(bundle['session_ids']):
                    rows.append({'fold':f,'session_id':sid,'arm':arm,'relation':rel,'lambda':lam,'subset':'Full',
                        'labels':model['labels'],'indices':list(range(157)),'coordinates':z[i].tolist(),
                        'raw_recovered':raw[i].tolist(),'logits':l[i].tolist(),'probabilities':p[i].tolist(),
                        'source_model_sha256':state['source_model_sha256']})
    if len(rows)!=1920:raise ValueError('Prediction count')
    write_table(out/'predictions.parquet',rows)
    baseline=[r for r in table(source/'inference/predictions.parquet') if r['subset']=='Full']
    if len(baseline)!=1200:raise ValueError('Baseline count')
    write_json(out/'baseline-reuse.json',{'path':str(source/'inference/predictions.parquet'),
        'sha256':digest(source/'inference/predictions.parquet'),'filter':'subset == Full','rows':1200})
    write_json(out/'validation.json',{'passed':True,'new_prediction_rows':1920,'baseline_rows':1200,
        'test_pre_loaded':False,'test_labels_loaded':False})
    seal(out,passed=True);print('1920 post-only predictions sealed',flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['zero','fit','predict']);p.add_argument('--config',default=str(CONFIG));a=p.parse_args()
    if a.command=='predict':predict(a.config)
    else:run_fit(a.config,zero=a.command=='zero')
