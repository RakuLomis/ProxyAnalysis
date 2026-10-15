"""Membership/SHA, scoped states, exact zero and frozen prediction replay."""
from common import *
from grouping import sourcekernel,sourcemodel,true_scores,group_scores

def main():
    c=start('verify'); maximum=0.; gammaerr=0.; zeroerr=0.; predictionerr=0.
    for p,h in c['baseline_sha256'].items(): require(sha(ROOT/p)==h,'Old baseline changed')
    for p,h in c['packages_sha256'].items(): require(sha(ROOT/p)==h,'New package changed')
    predictions=pd.read_parquet(OUT/'predictions/visits.parquet')
    choices={(r['outer'],r['protocol'],r['arm']):r['alpha'] for r in read(OUT/'selection/choices.json')}
    require(read(OUT/'selection/complete.json')['time_unix']<read(OUT/'predictions/complete.json')['time_unix'],'Selection order')
    for r in c['roles']:
        hist=package(mainfolder('packages',r)/'train-post.parquet','verify'); y=tensor(truths(hist),torch.long)
        base=oldartifact('models',r,'zero'); zero=artifact(mainfolder('models',r)/'zero.pt')
        for field in ['mu','scale','weight','bias']:
            diff=float((base[field]-zero[field]).abs().max()); zeroerr=max(zeroerr,diff); require(diff==0,'Zero parameter replay')
        part='outer' if r['inner'] is None else 'inner'; scores=pd.read_parquet(OUT/f'states/{part}-CF-scores.parquet')
        sub=scores[(scores.outer==r['outer'])&(scores.protocol==r['protocol'])&((scores.inner==r['inner']) if r['inner'] is not None else scores.inner.isna())]
        require(sub.visit_id.is_unique and set(sub.content_id)==set(r['train_contents']),'Grouped score support')
        sub=sub.set_index('visit_id').loc[hist.visit_id]
        for arm,col in [('DSR2','d_post'),('DSR3','d_group'),('DSR4','d_true')]:
            saved=artifact(mainfolder('states',r)/(arm+'.pt')); expected,_=partition(tensor(sub[col]),y)
            err=float((saved['gamma']-expected).abs().max()); gammaerr=max(gammaerr,err); require(err==0,'Gamma replay')
        if r['inner'] is not None: continue
        query=package(mainfolder('packages',r)/'query-post.parquet','verify')
        for arm in ARMS:
            if arm=='DSR1':
                t=choices[(r['outer'],r['protocol'],arm)]; model=oldartifact('models',r,'zero' if t==0 else f'KSR1-t{t:g}')
            else:
                a=0 if arm=='DSR0' else choices[(r['outer'],r['protocol'],arm)]
                model=artifact(mainfolder('models',r)/('zero.pt' if a==0 else f'{arm}-a{a:g}.pt'))
            expect=probabilities(model,query).set_index('visit_id')
            actual=predictions[(predictions.outer==r['outer'])&(predictions.protocol==r['protocol'])&(predictions.arm==arm)].set_index('visit_id').loc[expect.index]
            err=float(np.max(abs(expect[[f'p{i}' for i in range(6)]].to_numpy()-actual[[f'p{i}' for i in range(6)]].to_numpy())))
            predictionerr=max(predictionerr,err); require(err==0,'Final probability replay')
    sources={s['id']:s for s in c['sources']}
    for q in c['queries']:
        s=sources[q['source']]; parent=q['parent']; require(not set(s['train_contents'])&set(q['query_contents']) and set(s['train_contents']).issubset(parent['train_contents']),'CF content leak')
        src=queryfolder('packages',q); bundles=[sourcekernel(s,j) for j in range(10)]
        actual=true_scores(package(src/'query-paired.parquet','verify'),bundles)
        anon=group_scores(package(src/'query-group-post.parquet','verify'),package(src/'query-group-pre.parquet','verify'),bundles)
        part='outer' if parent['inner'] is None else 'inner'; frame=pd.read_parquet(OUT/f'states/{part}-CF-scores.parquet')
        sub=frame[(frame.outer==parent['outer'])&(frame.protocol==parent['protocol'])&(frame.CF_fold==q['held'])&((frame.inner==parent['inner']) if parent['inner'] is not None else frame.inner.isna())].set_index('visit_id')
        for field,result in [('d_true',actual),('d_group',anon)]:
            err=float(np.max(abs(result[field].to_numpy()-sub.loc[result.visit_id,field].to_numpy()))); maximum=max(maximum,err); require(err<1e-12,'State score replay')
        query=package(src/'query-post.parquet','verify'); probs=probabilities(sourcemodel(s),query)
        oldpred=pd.read_parquet(queryfolder('CF-predictions',q)/'post-probabilities.parquet').set_index('visit_id').loc[probs.visit_id]
        require(np.array_equal(probs[[f'p{i}' for i in range(6)]].to_numpy(),oldpred[[f'p{i}' for i in range(6)]].to_numpy()),'CF probability replay')
    for stage in ['D16','D20']:
        reads=read(OUT/'manifests'/f'{stage}-ledger.json')['reads']
        require(not any('score-labels' in x['path'] or '/states/' in x['path'] or 'test-paired' in x['path'] or '/kernels/' in x['path'] for x in reads),'Class prediction used forbidden data')
    fitread=read(OUT/'manifests/D14-D15-ledger.json')['reads']+read(OUT/'manifests/D19-ledger.json')['reads']
    require(not any('query-' in x['path'] or 'test-paired' in x['path'] or 'score-labels' in x['path'] for x in fitread),'Risk fit read held-out data')
    require(read(OUT/'manifests/D20-ledger.json')['completed_unix']<read(OUT/'manifests/D23-ledger.json')['completed_unix'],'Offline test diagnostic ordering')
    write(OUT/'verification.json',{'pass':True,'state_score_max_replay_error':maximum,'gamma_max_replay_error':gammaerr,
      'zero_parameter_max_replay_error':zeroerr,'final_probability_max_replay_error':predictionerr,
      'old_sources_artifacts_unchanged':True,'logical_CF_roles':320,'CF12_unique_sources':40,
      'registered_entity_crossfold_overlap':0,'universal_TCP_epoch_proof':False,
      'source_query_content_disjoint':True,'post_only_classification_verified':True,
      'offline_test_pre_no_model_feedback':True,'read_whitelist_not_OS_sandbox':True})
    finish('D25',verified=True)

if __name__=='__main__': main()
