"""Post-seal content-cluster scoring; fixed-model conditional intervals only."""
import json
import pandas as pd
from common import *


def macro_f1(cm):
    cm=np.asarray(cm,float);tp=np.diagonal(cm,axis1=-2,axis2=-1)
    denom=cm.sum(-1)+cm.sum(-2)
    return np.divide(2*tp,denom,out=np.zeros_like(tp),where=denom>0).mean(-1)


def metrics(y,p):
    cm=np.zeros((6,6),dtype=float);np.add.at(cm,(y,p.argmax(1)),1)
    tp=np.diag(cm);n=cm.sum();support=cm.sum(1)
    return {'F1':float(macro_f1(cm)),'accuracy':float(tp.sum()/n),
            'BA':float(np.divide(tp,support,out=np.zeros_like(tp),where=support>0).mean()),
            'CE_bits':float(-np.log2(np.maximum(p[np.arange(len(y)),y],1e-30)).mean()),
            'Brier':float(((p-np.eye(6)[y])**2).sum(1).mean())},cm


def main():
    seal=read(OUT/'prediction-seal.json');assert not seal['labels_read'] and not seal['test_pre_read']
    assert file_hash(OUT/'predictions.parquet')==seal['sha256']
    assert seal['contract_sha256']==file_hash(OUT/'contract.json')
    contract=read(OUT/'contract.json');check_files(contract['code_hashes'])
    assert not (OUT/'score-complete.json').exists()
    pred=pd.read_parquet(OUT/'predictions.parquet');cohort=pd.read_parquet(OUT/'cohort.parquet')
    data=pred.merge(cohort[['session_id','content_id','protocol','label_id']],on='session_id',validate='many_to_one')
    classes=sorted(cohort.label_id.unique());assert len(classes)==6
    assert all(json.loads(s)==classes for s in data.classes_json.unique())
    data['y']=data.label_id.map({c:i for i,c in enumerate(classes)});pc=[f'p{i}' for i in range(6)]
    prob=data[pc].to_numpy();assert np.isfinite(prob).all() and (prob>=0).all()
    np.testing.assert_allclose(prob.sum(1),1,atol=2e-6)
    data['prediction']=prob.argmax(1);rows=[];confusions=[]
    for (e,arm,seed,protocol),g in data.groupby(['experiment','arm','seed','protocol']):
        assert len(g)==120 and g.session_id.is_unique
        m,cm=metrics(g.y.to_numpy(),g[pc].to_numpy())
        rows.append({'experiment':e,'arm':arm,'seed':seed,'protocol':protocol,**m})
        confusions.append({'experiment':e,'arm':arm,'seed':seed,'protocol':protocol,'classes':classes,'matrix':cm.tolist()})
    detail=pd.DataFrame(rows);detail.to_parquet(OUT/'per-protocol-seed-metrics.parquet',index=False)
    write(OUT/'confusion-matrices.json',confusions)
    summary=[]
    for (e,arm,seed),g in detail.groupby(['experiment','arm','seed']):
        assert len(g)==5
        raw=data[data.experiment.eq(e)&data.arm.eq(arm)&data.seed.eq(seed)]
        pooled,_=metrics(raw.y.to_numpy(),raw[pc].to_numpy())
        summary.append({'experiment':e,'arm':arm,'seed':seed,'protocol_equal_F1':float(g.F1.mean()),
                        'worst_protocol_F1':float(g.F1.min()),'worst_protocol':g.loc[g.F1.idxmin(),'protocol'],
                        'pooled_F1':pooled['F1']})
    pd.DataFrame(summary).to_parquet(OUT/'aggregate-seed-metrics.parquet',index=False)
    contents=sorted(cohort.content_id.unique());ci={c:i for i,c in enumerate(contents)}
    rng=np.random.default_rng(20260928);weights=np.zeros((10000,30),dtype=np.int16)
    for c in classes:
        group=sorted(cohort.loc[cohort.label_id.eq(c),'content_id'].unique());assert len(group)==5
        draws=rng.integers(0,5,(10000,5))
        for j,content in enumerate(group):weights[:,ci[content]]=(draws==j).sum(1)
    contrasts=[]
    for e in ['E1','E2']:
        arms=['M0','M1','M2','M3','M4'];cms=np.zeros((3,5,5,30,6,6),dtype=float)
        subset=data[data.experiment.eq(e)]
        for (seed,arm,protocol,c),g in subset.groupby(['seed','arm','protocol','content_id']):
            assert len(g)==4
            target=cms[SEEDS.index(seed),arms.index(arm),PROTOCOLS.index(protocol),ci[c]]
            np.add.at(target,(g.y.to_numpy(),g.prediction.to_numpy()),1)
        scores=[];worst=[]
        for start in range(0,len(weights),256):
            cm=np.einsum('bc,sapcij->bsapij',weights[start:start+256],cms,optimize=True)
            f=macro_f1(cm);scores.append(f.mean(axis=(1,3)));worst.append(f.min(axis=3).mean(axis=1))
        sample=np.concatenate(scores);worst_sample=np.concatenate(worst)
        point=macro_f1(cms.sum(axis=3)).mean(axis=(0,2))
        for arm in ['M0','M1','M3','M4']:
            delta=sample[:,2]-sample[:,arms.index(arm)];primary=arm!='M4'
            contrasts.append({'experiment':e,'contrast':f'M2-{arm}','primary':primary,
                'delta':float(point[2]-point[arms.index(arm)]),
                'low95':float(np.quantile(delta,.025)),'high95':float(np.quantile(delta,.975)),
                'adjusted_low':float(np.quantile(delta,.05/(2*3))) if primary else None,
                'adjusted_high':float(np.quantile(delta,1-.05/(2*3))) if primary else None})
        np.savez_compressed(OUT/f'{e}-bootstrap.npz',protocol_equal_F1=sample,worst_F1=worst_sample,arms=np.array(arms))
    pd.DataFrame(contrasts).to_parquet(OUT/'primary-contrasts.parquet',index=False)
    # Keep all accesses and seed repetitions for descriptive repaired/new errors.
    data[['experiment','arm','seed','session_id','protocol','content_id','y','prediction']].to_parquet(OUT/'visit-decisions.parquet',index=False)
    write(OUT/'score-complete.json',{'conditional_on_fixed_models':True,'content_clusters':30,
          'bootstrap_draws':10000,'separate_E1_E2_primary_families':3,'target_refit':False,
          'script_sha256':file_hash(Path(__file__))})


if __name__=='__main__':main()
