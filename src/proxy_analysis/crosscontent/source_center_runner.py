"""Five center-target solves, preceded by algebra and frozen F/G replay gates."""
import argparse
import numpy as np
from .source_hierarchy_contract import CONFIG,verify
from .decision_calibration_objective import fit,quadratic,losses
from .decision_calibration_runner import name,mapping,predict_one
from .mechanism_contract import read
from .paired_structure_contract import seal,validate_complete
from ..paired_information.prepare import table,digest
from ..reproducibility.preflight import write_json,write_table


def algebra(v,t,tc,c,w,group_indices):
    v,t,tc,c,w=map(lambda x:np.asarray(x,float),(v,t,tc,c,w));n,d=v.shape;wc=w-w.mean(0)
    donors=np.zeros((n,4),int)
    for ix in group_indices:donors[ix]=np.asarray(ix)[None,:]
    target=t[donors];constant=float(np.mean((t-tc)**2)+np.mean(np.sum(((t-tc)*c@wc.T)**2,axis=1))/5)
    h,rhs=quadratic(v,tc,c,w,1);h_old,_=quadratic(v,t,c,w,1)
    if not np.array_equal(h,h_old):raise ValueError('Target changed Hessian')
    errors=[];grad_errors=[]
    for theta in (np.zeros(2*d),np.linspace(-.3,.3,2*d),np.r_[np.ones(d),np.zeros(d)]):
        a,b=theta.reshape(2,d);res=(v*a+b)[:,None,:]-target
        scores=(res*c)@wc.T
        objective=float(np.mean(res**2)+np.sum(a*a)/(n*d)+np.mean(np.sum(scores**2,axis=-1))/5)
        current=losses(theta,v,tc,c,w,1)['total'];err=abs(objective-current-constant)
        # Derivative formed directly from every target residual, not quadratic assembly.
        dq=(2*res/d+2*(scores@wc)*c/5).mean(1)/n
        grad=np.r_[(dq*v).sum(0)+2*a/(n*d),dq.sum(0)]
        expected=2*(h@theta-rhs);ge=float(abs(grad-expected).max())
        if not np.isclose(objective-current,constant,rtol=1e-10,atol=1e-10) or not np.allclose(grad,expected,rtol=1e-10,atol=1e-10):raise ValueError('All-target identity failed')
        errors.append(err);grad_errors.append(ge)
    return {'constant':constant,'max_loss_identity_error':max(errors),'max_gradient_identity_error':max(grad_errors),'hessian_unchanged':True}


def gate(config=CONFIG):
    _,root,old,source=verify(config);validate_complete(root/'hierarchy');out=root/'gate'
    if out.exists():raise FileExistsError(out)
    refs={(r['fold'],r['arm'],r['session_id']):r for r in table(old/'inference/predictions.parquet')}
    checks=[]
    for f in range(5):
        p=read(root/'train'/f'fold-{f}.json');tr=read(source/'train'/f'fold-{f}.json');model=read(source/'source-fits'/f'fold-{f}-Full.json')
        post=read(source/'post-input'/f'fold-{f}.json');worst=0.
        for rel in ('true','wrong'):
            arm=name(rel,1);state=read(old/'positive-fits/fits'/f'{f}-{arm}.json')
            z,_,score,prob=predict_one(post,tr,model,state['mapping'])
            for i,sid in enumerate(post['session_ids']):
                ref=refs[f,arm,sid]
                worst=max(worst,*[float(abs(x-np.asarray(ref[key])).max()) for x,key in [(z[i],'coordinates'),(score[i],'logits'),(prob[i],'probabilities')]])
        if worst>1e-10:raise ValueError('F/G replay differs')
        checks.append({'fold':f,'FG_replay_error':worst,**algebra(p['v'],p['t_original'],p['t'],p['c'],p['weights'],p['groups'])})
    write_json(out/'validation.json',{'passed':True,'checks':checks,'new_fits':0});seal(out,passed=True)
    print('Algebra and F/G reuse gate passed',flush=True)


def run_fit(config=CONFIG):
    _,root,_,_=verify(config);validate_complete(root/'gate');out=root/'fits'
    if out.exists():raise FileExistsError(out)
    for f in range(5):
        p=read(root/'train'/f'fold-{f}.json');theta,stats=fit(p['v'],p['t'],p['c'],p['weights'],1,1)
        write_json(out/f'fold-{f}.json',{'fold':f,'arm':'H','theta':theta.tolist(),'mapping':mapping(theta,p),
            'statistics':stats,'train_ids':p['train_ids'],'source_model_sha256':p['source_model_sha256'],
            'lambda':1,'alpha':1,'parameters':len(theta),'train_package_sha256':digest(root/'train'/f'fold-{f}.json')})
        print(f'H fitted: fold {f}',flush=True)
    write_json(out/'validation.json',{'passed':True,'new_calibration_fits':5,'new_classifiers':0,'new_neural_fits':0})
    seal(out,passed=True)


def predict(config=CONFIG):
    _,root,_,source=verify(config);validate_complete(root/'fits');out=root/'inference'
    if out.exists():raise FileExistsError(out)
    rows=[]
    for f in range(5):
        p=read(source/'post-input'/f'fold-{f}.json');tr=read(source/'train'/f'fold-{f}.json')
        model=read(source/'source-fits'/f'fold-{f}-Full.json');fit=read(root/'fits'/f'fold-{f}.json')
        z,raw,l,prob=predict_one(p,tr,model,fit['mapping'])
        for i,sid in enumerate(p['session_ids']):rows.append({'fold':f,'session_id':sid,'arm':'H','subset':'Full',
            'labels':model['labels'],'coordinates':z[i].tolist(),'raw_recovered':raw[i].tolist(),'logits':l[i].tolist(),
            'probabilities':prob[i].tolist(),'source_model_sha256':fit['source_model_sha256']})
    if len(rows)!=240:raise ValueError('Prediction count')
    write_table(out/'predictions.parquet',rows);write_json(out/'validation.json',{'passed':True,'predictions':240,
        'test_pre_used':False,'test_centers_used':False,'content_or_protocol_numeric_inputs':False})
    seal(out,passed=True);print('240 H post-only predictions sealed',flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['gate','fit','predict']);p.add_argument('--config',default=str(CONFIG));a=p.parse_args()
    {'gate':gate,'fit':run_fit,'predict':predict}[a.command](a.config)
