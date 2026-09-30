"""Directional membership, source-state reconstruction and independent QR replay."""
import argparse
import numpy as np
from .deployment_transfer_contract import CONFIG,verify,contexts
from .deployment_transfer_prepare import prepare_state
from .deployment_transfer_runner import forward
from .decision_calibration_objective import independent_lstsq
from .decision_calibration_audit import standard
from .source_hierarchy_contract import center_targets
from .natural_pair_ssl_report import softmax
from .mechanism_contract import read
from .paired_structure_contract import seal,validate_complete
from ..paired_information.prepare import table,digest
from ..reproducibility.preflight import write_json


def audit(config=CONFIG):
    cfg,root=verify(config)
    for p in ('prepared','classifiers','calibrations','inference','report'):validate_complete(root/p)
    refs={(r['context'],r['domain'],r['arm'],r['session_id']):r for r in table(root/'inference/predictions.parquet')}
    checks=[];worst=0.;qrworst=0.
    for protocol,f,key in contexts(cfg):
        train=read(root/'train'/f'{key}.json');state=read(root/'prepared'/f'{key}.json');rebuilt=prepare_state(train)
        for field,value in rebuilt.items():
            if value!=state[field]:raise ValueError('Source-only preprocessing differs: '+field)
        if state['training_package_sha256']!=digest(root/'train'/f'{key}.json'):raise ValueError('Training provenance')
        forbidden=read(root/'forbidden'/f'{key}.json')['rows'];trainids=set(state['train_ids'])
        if trainids&{r['session_id'] for r in forbidden}:raise ValueError('Forbidden training ID')
        if {r['protocol'] for r in train['rows']}!={protocol}:raise ValueError('Target training row')
        j=state['indices'];v=np.asarray(state['post'])[:,j];models={s:read(root/'classifiers'/f'{key}-{s}.json') for s in ('pre','post')}
        for m in models.values():
            if m['train_ids']!=state['train_ids'] or m['prepared_sha256']!=digest(root/'prepared'/f'{key}.json'):raise ValueError('Classifier provenance')
        tc=center_targets(np.asarray(state['t'])[::-1],train['rows'][::-1],train['rows'])
        if not np.allclose(tc,state['center'],atol=1e-12):raise ValueError('Center depends on pairing')
        qrfits={}
        for arm,target in [('F',state['t']),('H',tc)]:
            old=read(root/'calibrations'/f'{key}-{arm}.json')
            if old['train_ids']!=state['train_ids'] or old['source_model_sha256']!=digest(root/'classifiers'/f'{key}-pre.json'):raise ValueError('Calibrator provenance')
            theta=independent_lstsq(v,target,state['c'],np.asarray(models['pre']['coef'])[:,j],1)
            qrworst=max(qrworst,float(abs(theta-old['theta']).max()))
            if not np.allclose(theta,old['theta'],atol=1e-8,rtol=1e-8):raise ValueError('Independent QR differs')
            qrfits[arm]=theta.reshape(2,len(j))
        for domain in ('source','target'):
            post=read(root/'post-input'/f'{key}-{domain}.json');pre=read(root/'pre-reference'/f'{key}-{domain}.json')
            ev=read(root/'evaluation'/f'{key}-{domain}.json')['rows']
            if trainids&set(post['session_ids']) or {r['content_id'] for r in train['rows']}&{r['content_id'] for r in ev}:raise ValueError('Held-out leakage')
            zp=standard(post['raw_post'],state['post_scaler'])
            for arm in cfg['arms']:
                if arm=='A':z=standard(pre['raw_pre'],state['source_scaler'])*state['source_scaler']['active']
                elif arm=='B':z=standard(post['raw_post'],state['source_scaler'])*state['source_scaler']['active']
                elif arm=='E':z=zp
                else:
                    a,b=qrfits[arm];z=np.zeros_like(zp);z[:,j]=(zp[:,j]*a+b)*state['c']+state['offset']
                m=models['post' if arm=='E' else 'pre'];score=z@np.asarray(m['coef']).T+m['intercept'];prob=softmax(score)
                for i,sid in enumerate(post['session_ids']):
                    ref=refs[key,domain,arm,sid]
                    for x,field in [(z[i],'coordinates'),(score[i],'logits'),(prob[i],'probabilities')]:
                        worst=max(worst,float(abs(x-ref[field]).max()))
                        if not np.allclose(x,ref[field],atol=1e-8,rtol=1e-8):raise ValueError('Forward replay')
                    if prob[i].argmax()!=np.argmax(ref['probabilities']):raise ValueError('Class mismatch')
                if arm!='A':
                    params=read(root/'calibrations'/f'{key}-{arm}.json')['mapping'] if arm in ('F','H') else None
                    orig=forward(post,state,m,arm,params)[3]
                    renamed={**post,'session_ids':[str(i) for i in range(24)]}
                    if not np.array_equal(orig,forward(renamed,state,m,arm,params)[3]):raise ValueError('ID dependence')
                    for field in ('raw_pre','labels','content_id','protocol','centers'):
                        try:forward({**post,field:[]},state,m,arm,params)
                        except ValueError:pass
                        else:raise ValueError('Unauthorized input accepted')
        checks.append({'context':key,'train_protocol':protocol,'train_visits':96,'active_dimensions':len(j),
            'forbidden_target_members_in_fit':0,'source_preprocessing_reconstructed':True,'center_permutation_invariant':True,'post_permission_checks':True})
        print('Cross-deployment audit: '+key,flush=True)
    if len(refs)!=2400 or len(list((root/'classifiers').glob('*-pre.json')))!=10 or len(list((root/'classifiers').glob('*-post.json')))!=10 or len(list((root/'calibrations').glob('*-F.json')))!=10 or len(list((root/'calibrations').glob('*-H.json')))!=10:raise ValueError('Budget mismatch')
    verify(config)
    write_json(root/'audit/validation.json',{'passed':True,'classifiers':20,'calibrators':20,'independent_QR_replays':20,
        'predictions_replayed':2400,'max_QR_parameter_error':qrworst,'max_forward_error':worst,'checks':checks,
        'historical_target_visibility':True,'fresh_raw_packet_scan':False,'old_artifacts_unchanged':True})
    seal(root/'audit',passed=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--config',default=str(CONFIG));a=p.parse_args();audit(a.config)
