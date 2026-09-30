"""Independent five-fold numerical and group-only authority audit."""
import argparse
import numpy as np
from .source_hierarchy_contract import CONFIG,verify,center_targets
from .decision_calibration_objective import independent_lstsq
from .decision_calibration_runner import predict_one
from .decision_calibration_audit import standard
from .natural_pair_ssl_report import softmax
from .mechanism_contract import read
from .paired_structure_contract import seal,validate_complete
from ..paired_information.prepare import table,digest
from ..reproducibility.preflight import write_json


def audit(config=CONFIG):
    _,root,_,source=verify(config)
    for part in ('gate','hierarchy','fits','inference','report'):validate_complete(root/part)
    refs={(r['fold'],r['session_id']):r for r in table(root/'inference/predictions.parquet')}
    checks=[];worst=0.
    for f in range(5):
        pack=read(root/'train'/f'fold-{f}.json');j=pack['indices'];state=read(root/'fits'/f'fold-{f}.json')
        tr=read(source/'train'/f'fold-{f}.json');model=read(source/'source-fits'/f'fold-{f}-Full.json')
        post=read(source/'post-input'/f'fold-{f}.json');ev=read(source/'evaluation'/f'fold-{f}.json')['rows']
        if state['source_model_sha256']!=digest(source/'source-fits'/f'fold-{f}-Full.json') or state['train_ids']!=pack['train_ids']:raise ValueError('Model identity')
        if {r['content_id'] for r in pack['group_metadata']}&{r['content_id'] for r in ev}:raise ValueError('Content overlap')
        # Reverse pre records globally while preserving their group membership.
        tc=center_targets(np.asarray(pack['t_original'])[::-1],pack['group_metadata'][::-1],pack['group_metadata'])
        if not np.allclose(tc,pack['t'],atol=1e-12):raise ValueError('Pair permutation changed centers')
        theta=independent_lstsq(pack['v'],tc,pack['c'],pack['weights'],1)
        if not np.allclose(theta,state['theta'],atol=1e-8,rtol=1e-8):raise ValueError('Independent QR differs')
        x=standard(post['raw_post'],tr['post_scaler']);a,b=theta.reshape(2,len(j))
        raw=np.tile(np.asarray(tr['target_scaler']['mean']),(len(x),1))
        raw[:,j]=(x[:,j]*a+b)*np.asarray(tr['target_scaler']['scale'])[j]+np.asarray(tr['target_scaler']['mean'])[j]
        z=(raw-tr['source_scaler']['mean'])/tr['source_scaler']['scale'];z*=tr['source_scaler']['active']
        score=z@np.asarray(model['coef']).T+model['intercept'];prob=softmax(score)
        for i,sid in enumerate(post['session_ids']):
            for value,key in [(z[i],'coordinates'),(score[i],'logits'),(prob[i],'probabilities')]:
                ref=np.asarray(refs[f,sid][key]);worst=max(worst,float(abs(value-ref).max()))
                if not np.allclose(value,ref,atol=1e-8,rtol=1e-8):raise ValueError('Forward replay differs')
            if prob[i].argmax()!=np.argmax(refs[f,sid]['probabilities']):raise ValueError('Class replay differs')
        original=predict_one(post,tr,model,state['mapping'])[3]
        renamed={**post,'session_ids':['unrelated-'+str(i) for i in range(len(x))]}
        if not np.array_equal(original,predict_one(renamed,tr,model,state['mapping'])[3]):raise ValueError('ID changes numeric prediction')
        for field in ('raw_pre','labels','content_id','protocol','centers'):
            try:predict_one({**post,field:[]},tr,model,state['mapping'])
            except ValueError:pass
            else:raise ValueError('Unauthorized prediction input')
        checks.append({'fold':f,'QR_parameter_error':float(abs(theta-state['theta']).max()),
            'group_pre_permutation_invariant':True,'session_id_renaming_invariant':True,
            'test_pre_label_group_center_fields_rejected':True})
        print(f'H audit fold {f} passed',flush=True)
    if len(list((root/'fits').glob('fold-*.json')))!=5 or len(refs)!=240:raise ValueError('Budget')
    verify(config)
    write_json(root/'audit/validation.json',{'passed':True,'formal_H_fits':5,'independent_QR_replays':5,
        'predictions_replayed':240,'max_forward_error':worst,'new_classifier_fits':0,'new_neural_fits':0,
        'old_sources_unchanged':True,'fresh_raw_packet_scan':False,'checks':checks})
    seal(root/'audit',passed=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--config',default=str(CONFIG));a=p.parse_args();audit(a.config)
