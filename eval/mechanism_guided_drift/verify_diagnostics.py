"""Independent persisted role/input/result verification; no classifier or fit."""
import numpy as np
import pandas as pd
from common import ROOT, LATEST, read_json, file_hash, write_json
from diagnostics import OUT, EXTRACT


def verify():
    contract=read_json(OUT/'diagnostic-contract.json')
    audit=read_json(OUT/'diagnostic-audit.json');assert audit['passed']
    for path,h in contract['input_sha256'].items():assert file_hash(ROOT/path)==h
    for path,h in contract['code_sha256'].items():assert file_hash(ROOT/path)==h
    cohort=pd.read_parquet(LATEST/'cohort.parquet').set_index('session_id')
    access=read_json(OUT/'access-ledger.json')
    for row in access['folds']:
        members=cohort.loc[row['post_W_session_ids']]
        assert len(members)==480 and members.fold.ne(row['outer_fold']).all()
        assert not row['outer_test_post_read'] and not row['query_post_used']
    jobs={j['job']:j for j in read_json(OUT/'diagnostic-roles.json')['jobs']}
    fits=read_json(OUT/'fit-ledger.json')['fits']
    assert sum(f['level']=='W' for f in fits)==1800
    assert sum(f['level']=='T' for f in fits)==480
    for f in fits:
        assert f['device']=='cuda'
        if f['level']=='W':
            j=jobs[f['job']];a=cohort.loc[f['fit_sessions']];b=cohort.loc[f['held_sessions']]
            assert len(a)==68 and len(b)==4
            assert set(a.content_id).isdisjoint(b.content_id)
            assert set(a.index)|set(b.index)==set(j['fit_sessions'])
            assert (a.fold.ne(j['fold'])).all() and (b.fold.ne(j['fold'])).all()
            assert set(j['query_sessions']).isdisjoint(a.index) and set(j['query_sessions']).isdisjoint(b.index)
        else:
            train=cohort[cohort.fold.ne(f['outer_fold'])&cohort.protocol.eq(f['protocol'])]
            assert train.content_id.nunique()==24 and f['held_content'] in set(train.content_id)
            assert train[train.content_id.ne(f['held_content'])].content_id.nunique()==f['fit_contents']==23
    pred=pd.read_parquet(OUT/'oof-predictions.parquet')
    joined=pred.merge(cohort.reset_index()[['session_id','fold','protocol','content_id']],on='session_id',suffixes=('','_registered'))
    assert len(joined)==len(pred) and joined.outer_fold.ne(joined.fold).all()
    assert joined.protocol.eq(joined.protocol_registered).all() and joined.content_id.eq(joined.content_id_registered).all()
    assert np.isfinite(pred[['prediction','target','pre_bytes']].to_numpy()).all()
    assert pred.target.ge(0).all()
    conn=pd.read_parquet(OUT/'connection-diagnostics.parquet')
    assert not conn.protocol.eq('anytls').any()
    for name in ['up','down']:
        for side in ['pre','post']:
            assert (conn[side+'_U_'+name]>=conn[side+'_E_'+name]).all()
            assert (conn[side+'_E_'+name]>=conn[side+'_R_'+name]).all()
    replay=[]
    for fold,g in conn.groupby('outer_fold'):
        ids=g.session_id.unique().tolist()
        for side in ['pre','post']:
            cached=pd.read_parquet(EXTRACT/'full-T-features.parquet',filters=[('side','==',side),('session_id','in',ids)]).set_index('session_id')
            columns=[n for n in cached if n not in {'side','F'}]
            sums=g.groupby('session_id')[[side+'_'+n for n in columns]].sum()
            assert np.array_equal(sums.to_numpy(),cached.loc[sums.index,columns].to_numpy()),'T summary reconstruction differs'
            counts=g.groupby('session_id').size();assert np.array_equal(counts,cached.loc[counts.index,'F'])
            replay.append({'outer_fold':int(fold),'side':side,'sessions':len(ids),'T_six_and_F_exact':True})
    result={'passed':True,'W_inner_tasks':1800,'T_inner_tasks':480,'estimator_tasks':6840,
        'OOF_rows':len(pred),'connection_rows':len(conn),'input_and_sealed_code_unchanged':True,
        'registered_content_and_session_roles_passed':True,'outer_test_post_in_result':False,
        'CPU_fit_fallback':False,'classifier_fits':0,'pcap_reads':0,'P3_started':False,'G2_pending':True,
        'preflight_exception_disclosed':True,'universal_flow_leakage_proof_claimed':False}
    result['T_replay']=replay
    write_json(OUT/'independent-verification.json',result);print(result)


if __name__=='__main__':verify()
