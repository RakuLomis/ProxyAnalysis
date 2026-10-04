"""Post-seal content-cluster scoring; no fitting, candidate choice or target adaptation."""
import json
from p3_common import *


def macro_f1(cm):
    cm=np.asarray(cm,float);tp=np.diagonal(cm,axis1=-2,axis2=-1);denom=cm.sum(-1)+cm.sum(-2)
    return np.divide(2*tp,denom,out=np.zeros_like(tp),where=denom>0).mean(-1)


def metrics(y,p):
    cm=np.zeros((6,6));np.add.at(cm,(y,p.argmax(1)),1)
    tp=np.diag(cm);support=cm.sum(1)
    return {'F1':float(macro_f1(cm)),'accuracy':float(tp.sum()/cm.sum()),
        'CE_bits':float(-np.log2(np.maximum(p[np.arange(len(y)),y],1e-30)).mean()),
        'Brier':float(((p-np.eye(6)[y])**2).sum(1).mean())},cm


def distribution():
    # Query post only in this SCORER, after generator/classifier/prediction freeze.
    rows=[];loco=[];params=[]
    for jp in sorted((OUT/'generator-roles').glob('*.json')):
        job=read(jp);role=read(OUT/'roles'/f'E1-all-f{job["fold"]}.json')
        post=Bundle(OUT/'packages/training'/role['scenario'],'classifier').get('post').set_index('session_id')
        for arm in GENERATORS:
            dest=OUT/'generation'/job['job']/arm;assert completed(dest);done=read(dest/'complete.json')
            params.append({'job':job['job'],'protocol':job['protocol'],'arm':arm,'outer_fold':job['fold'],
                'beta_up':done['beta'][0],'beta_down':done['beta'][1],
                'center_column_space_relative_error':done['center_column_space_relative_error']})
            with np.load(dest/'distribution.npz',allow_pickle=False) as f:
                ids=f['session_ids'].tolist();truth=post.loc[ids,W].to_numpy(float)
                assert set(ids)==set(job['query_sessions'])
                for i,sid in enumerate(ids):
                    meta=post.loc[sid]
                    for j,name in enumerate(W):
                        value=truth[i,j];point=f['raw_center'][i,j]
                        rows.append({'outer_fold':job['fold'],'job':job['job'],'protocol':job['protocol'],'arm':arm,
                            'session_id':sid,'content_id':meta.content_id,'feature':name,'target':value,'prediction':point,
                            'abs_error':abs(point-value),'error':point-value,
                            'covered95':bool(f['raw_low'][i,j]<=value<=f['raw_high'][i,j]),
                            'interval_width':f['raw_high'][i,j]-f['raw_low'][i,j]})
            with np.load(dest/'loco-latent.npz',allow_pickle=False) as f:
                errors=(f['predictions']-f['targets'])**2
                for c in np.unique(f['content_ids']):
                    loco.append({'job':job['job'],'arm':arm,'protocol':job['protocol'],'outer_fold':job['fold'],
                        'held_content':str(c),'own_target_latent_MSE':float(errors[f['content_ids']==c].mean())})
    f=pd.DataFrame(rows);f.to_parquet(OUT/'distribution-query-scores.parquet',index=False)
    g=f.groupby(['outer_fold','arm','protocol','feature','content_id']).agg(MAE=('abs_error','mean'),
        bias=('error','mean'),coverage95=('covered95','mean'),width=('interval_width','mean')).reset_index()
    g.groupby(['outer_fold','arm','protocol','feature']).agg(MAE=('MAE','mean'),bias=('bias','mean'),
        coverage95=('coverage95','mean'),interval_width=('width','mean')).reset_index().to_parquet(OUT/'distribution-metrics.parquet',index=False)
    pd.DataFrame(loco).to_parquet(OUT/'loco-target-metrics.parquet',index=False)
    pd.DataFrame(params).to_parquet(OUT/'center-parameters.parquet',index=False)


def main():
    authorize();seal=read(OUT/'prediction-seal.json')
    assert not seal['labels_read'] and not seal['test_pre_read']
    assert file_hash(OUT/'predictions.parquet')==seal['sha256'];assert not (OUT/'score-complete.json').exists()
    pred=pd.read_parquet(OUT/'predictions.parquet');cohort=pd.read_parquet(OUT/'cohort.parquet')
    data=pred.merge(cohort[['session_id','content_id','protocol','label_id']],on='session_id',validate='many_to_one')
    classes=sorted(cohort.label_id.unique());assert len(classes)==6
    assert all(json.loads(v)==classes for v in data.classes_json.unique())
    data['y']=data.label_id.map({c:i for i,c in enumerate(classes)});pc=[f'p{i}' for i in range(6)]
    prob=data[pc].to_numpy();assert np.isfinite(prob).all() and (prob>=0).all()
    np.testing.assert_allclose(prob.sum(1),1,atol=2e-6);data['prediction']=prob.argmax(1)
    detail=[];confusions=[];perclass=[]
    for (arm,seed,protocol),g in data.groupby(['arm','seed','protocol']):
        assert len(g)==120 and g.session_id.is_unique
        m,cm=metrics(g.y.to_numpy(),g[pc].to_numpy());detail.append({'arm':arm,'seed':seed,'protocol':protocol,**m})
        confusions.append({'arm':arm,'seed':seed,'protocol':protocol,'classes':classes,'matrix':cm.tolist()})
        tp=np.diag(cm);precision=np.divide(tp,cm.sum(0),out=np.zeros(6),where=cm.sum(0)>0)
        recall=tp/cm.sum(1);den=precision+recall
        for j,c in enumerate(classes):
            perclass.append({'arm':arm,'seed':seed,'protocol':protocol,'class':c,'support':int(cm.sum(1)[j]),
                'precision':precision[j],'recall':recall[j],'F1':2*precision[j]*recall[j]/den[j] if den[j]>0 else 0.})
    detail=pd.DataFrame(detail);detail.to_parquet(OUT/'per-protocol-seed-metrics.parquet',index=False)
    write(OUT/'confusion-matrices.json',confusions);pd.DataFrame(perclass).to_parquet(OUT/'per-class-seed-metrics.parquet',index=False)
    aggregate=[]
    for (arm,seed),g in detail.groupby(['arm','seed']):
        aggregate.append({'arm':arm,'seed':seed,'protocol_equal_F1':g.F1.mean(),'worst_protocol_F1':g.F1.min(),
            'CE_bits':g.CE_bits.mean(),'Brier':g.Brier.mean()})
    pd.DataFrame(aggregate).to_parquet(OUT/'aggregate-seed-metrics.parquet',index=False)
    contents=sorted(cohort.content_id.unique());ci={c:i for i,c in enumerate(contents)}
    rng=np.random.default_rng(20260928);weights=np.zeros((10000,30),dtype=np.int16)
    for c in classes:
        group=sorted(cohort.loc[cohort.label_id.eq(c),'content_id'].unique());assert len(group)==5
        draws=rng.integers(0,5,(10000,5))
        for j,content in enumerate(group):weights[:,ci[content]]=(draws==j).sum(1)
    cms=np.zeros((3,6,5,30,6,6))
    for (seed,arm,protocol,c),g in data.groupby(['seed','arm','protocol','content_id']):
        assert len(g)==4;target=cms[SEEDS.index(seed),ARMS.index(arm),LC.PROTOCOLS.index(protocol),ci[c]]
        np.add.at(target,(g.y.to_numpy(),g.prediction.to_numpy()),1)
    draws=[]
    for start in range(0,10000,256):
        f=macro_f1(np.einsum('bc,sapcij->bsapij',weights[start:start+256],cms,optimize=True))
        draws.append(f.mean(axis=(1,3)))
    samples=np.concatenate(draws);point=macro_f1(cms.sum(3)).mean(axis=(0,2));contrasts=[]
    for arm in ['D0_pair','D2_group','M0','D1_pair','D2_cyclic']:
        delta=samples[:,ARMS.index('D2_pair')]-samples[:,ARMS.index(arm)];primary=arm!='D2_cyclic'
        contrasts.append({'contrast':'D2_pair-'+arm,'primary':primary,
            'delta':point[ARMS.index('D2_pair')]-point[ARMS.index(arm)],
            'low95':np.quantile(delta,.025),'high95':np.quantile(delta,.975),
            'adjusted_low':np.quantile(delta,.05/8) if primary else None,
            'adjusted_high':np.quantile(delta,1-.05/8) if primary else None})
    pd.DataFrame(contrasts).to_parquet(OUT/'primary-contrasts.parquet',index=False)
    np.savez_compressed(OUT/'bootstrap.npz',protocol_equal_F1=samples,arms=np.array(ARMS))
    data[['arm','seed','session_id','protocol','content_id','y','prediction']].to_parquet(OUT/'visit-decisions.parquet',index=False)
    errors=[]
    for arm in ['D0_pair','D1_pair','D2_group','M0','D2_cyclic']:
        a=data[data.arm.eq('D2_pair')];b=data[data.arm.eq(arm)]
        joined=a[['seed','session_id','protocol','content_id','y','prediction']].merge(
            b[['seed','session_id','prediction']],on=['seed','session_id'],suffixes=('_new','_ref'),validate='one_to_one')
        joined['repaired']=(joined.prediction_ref!=joined.y)&(joined.prediction_new==joined.y)
        joined['new_error']=(joined.prediction_ref==joined.y)&(joined.prediction_new!=joined.y)
        for key,g in joined.groupby(['seed','protocol','content_id']):
            errors.append({'reference':arm,'seed':key[0],'protocol':key[1],'content_id':key[2],
                'repaired':int(g.repaired.sum()),'new_errors':int(g.new_error.sum()),'visits':len(g)})
    pd.DataFrame(errors).to_parquet(OUT/'error-transitions.parquet',index=False)
    # Compare ONLY after new predictions are frozen; never select checkpoint by old results.
    old=pd.read_parquet(LATEST/'predictions.parquet');old=old[old.experiment.eq('E1')&old.arm.isin(['M0','M2'])].copy()
    old['arm']=old.arm.map({'M0':'M0','M2':'D0_pair'})
    z=data[data.arm.isin(['M0','D0_pair'])].merge(old[['arm','seed','session_id',*pc]],on=['arm','seed','session_id'],suffixes=('','_old'),validate='one_to_one')
    d=np.abs(z[pc].to_numpy()-z[[p+'_old' for p in pc]].to_numpy())
    replay={'max_probability_difference':float(d.max()),'decision_changes':int(np.sum(z[pc].to_numpy().argmax(1)!=z[[p+'_old' for p in pc]].to_numpy().argmax(1))),
            'same_input_schedule_and_initialization':True,'comparison_after_prediction_seal':True}
    write(OUT/'classifier-baseline-replay.json',replay)
    distribution()
    write(OUT/'score-complete.json',{'passed':True,'bootstrap':10000,'primary_family_size':4,
        'conditional_on_fixed_models':True,'candidate_reselected':False,'test_refit':False,
        'scoring_labels_read_after_prediction_seal':True,'query_post_used_for_scoring_only':True,
        'classifier_baseline_replay':replay,'script_sha256':file_hash(Path(__file__))})
    print(pd.DataFrame(aggregate).groupby('arm').mean(numeric_only=True).to_string())
    print(pd.DataFrame(contrasts).to_string(index=False))


if __name__=='__main__':main()
