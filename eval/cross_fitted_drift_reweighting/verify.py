"""SHA/member/direction/weight/target/model and complete probability replay."""
from common import *
def main():
    c=start('verify'); zeroerr=0.; perr=0.; werr=0.; objectiveerr=0.; directionerr=0.
    for p,h in c['baseline_sha256'].items(): require(sha(ROOT/p)==h,'Historical artifact changed '+p)
    for p,h in c['packages_sha256'].items(): require(sha(ROOT/p)==h,'RW package changed '+p)
    chosen={(x['outer'],x['protocol'],x['arm']):x['setting'] for x in read(OUT/'selection/choices.json')}
    require(read(OUT/'selection/complete.json')['choices_sha256']==sha(OUT/'selection/choices.json'),'Choices preserved')
    pred={part:pd.read_parquet(OUT/('selection/inner-predictions.parquet' if part=='inner' else 'predictions/visits.parquet')) for part in ['inner','outer']}
    logs={part:pd.read_parquet(OUT/f'manifests/{part}-optimizer.parquet') for part in ['inner','outer']}
    dirs={part:pd.read_parquet(OUT/f'weights/{part}-directions.parquet') for part in ['inner','outer']}
    for r in c['roles']:
        inner=r['inner'] is not None; part='inner' if inner else 'outer'
        h=package(r,'train-post','verify'); oo=package(r,'train-OOF','verify'); y=tensor(truths(h),torch.long)
        require(set(h.content_id)==set(r['train_contents']) and oo.visit_id.tolist()==h.visit_id.tolist(),'Training content scope')
        base=baseline(r); x=(tensor(h[HIST])-base['mu'])/base['scale']; query=package(r,'query-post','verify'); validate_query(query)
        dm=dirs[part]; dm=dm[(dm.outer==r['outer'])&(dm.protocol==r['protocol'])&((dm.inner==r['inner']) if inner else dm.inner.isna())]
        for arm in ARMS:
            values=([0.] if arm=='RW0' else L2_SETTINGS if arm=='RW1' else RATIOS) if inner else [0. if arm=='RW0' else chosen[(r['outer'],r['protocol'],arm)]]
            for ratio in values:
                if arm in ARMS[2:]:
                    wp=artifact(folder('weights',r)/f'{arm}-r{ratio:g}.pt','weight-replay')
                    gp=torch.load(folder('packages',r)/(arm+'.pt'),weights_only=True,map_location=device())
                    require(torch.equal(wp['gamma'],gp['gamma']) and wp['visit_id']==h.visit_id.tolist(),'Original gamma preserved')
                    hard,risk=direction(tensor(oo.d_post),y,wp['gamma']); require(hard==wp['hard'],'Role direction replay')
                    dr=dm[dm.arm==arm].iloc[0]; de=max(abs(float(risk[0])-dr.R0_OOF),abs(float(risk[1])-dr.R1_OOF)); directionerr=max(directionerr,de)
                    expected=weights(wp['gamma'],hard,ratio); err=float((expected-wp['w']).abs().max()); werr=max(werr,err); require(err==0,'Frozen w replay')
                    m=artifact(folder('models',r)/(f'{arm}-r{ratio:g}.pt' if inner else arm+'.pt'),'model-replay')
                    if torch.equal(wp['w'],torch.ones_like(wp['w'])):
                        for k in ['mu','scale','weight','bias']:
                            e=float((m[k]-base[k]).abs().max()); zeroerr=max(zeroerr,e); require(e==0,'Exact uniform alias')
                    else:
                        log=logs[part]; sub=log[(log.outer==r['outer'])&(log.protocol==r['protocol'])&(log.arm==arm)&(log.setting==ratio)&((log.inner==r['inner']) if inner else log.inner.isna())]
                        require(len(sub)==1,'Fit record required'); row=sub.iloc[0]; val,parts=objective(m['weight'],m['bias'],x,y,wp['w'],wp['gamma'],base)
                        err=abs(float(val)-row.final_objective)
                        for k,z in parts.items(): err=max(err,abs(float(z)-row['final_'+k]))
                        objectiveerr=max(objectiveerr,err); require(err<1e-12,'Actual final target replay')
                        gw=gradients(m['weight'],m['bias'],x,y,wp['w'],wp['gamma'],base)
                        require(abs(gw['L2_gradient_norm']-row.L2_gradient_norm)<1e-12 and row.L2_bias_gradient_norm==0,'Strict W-only L2 replay')
                        mix=parts['CE'] if hard is None else (parts[f'R{1-hard}']+ratio*parts[f'R{hard}'])/(1+ratio)
                        require(abs(float(mix-parts['weighted_CE']))<1e-12,'Actual group mixture')
                else:
                    m=baseline(r,ratio) if inner else artifact(folder('models',r)/(arm+'.pt'),'model-replay')
                    ref=baseline(r,ratio)
                    for k in ['mu','scale','weight','bias']: require(torch.equal(m[k],ref[k]),'RW0/1 exact model reuse')
                expect=probabilities(m,query).set_index('visit_id'); actual=pred[part]
                actual=actual[(actual.outer==r['outer'])&(actual.protocol==r['protocol'])&(actual.arm==arm)&((actual.inner==r['inner']) if inner else actual.inner.isna())]
                if inner: actual=actual[actual.setting==ratio]
                actual=actual.set_index('visit_id').loc[expect.index]
                err=float(np.max(abs(expect[[f'p{i}' for i in range(6)]].to_numpy()-actual[[f'p{i}' for i in range(6)]].to_numpy())))
                perr=max(perr,err); require(err==0,'All frozen probabilities exact')
        print('verified',rolekey(r),flush=True)
    for q in c['queries']:
        source=next(s for s in c['sources'] if s['id']==q['source']); a=set(source['train_contents']); b=set(q['query_contents']); whole=set(q['parent']['train_contents'])
        require(not a&b and a|b==whole,'Source-query split')
    for stage in ['RW14','RW20']:
        ledger=read(OUT/f'manifests/{stage}-ledger.json')
        require(not any(any(token in p['path'] for token in ['score-labels','train-OOF','/weights/','/states/','/kernels/','test-paired','selection/choices']) for p in ledger['reads']),'Post-only read audit')
    for stage in ['RW11-RW13','RW19']:
        ledger=read(OUT/f'manifests/{stage}-ledger.json')
        require(not any(any(token in p['path'] for token in ['query-','score-labels','train-OOF','test-paired','/kernels/','/states/']) for p in ledger['reads']),'Train permission audit')
    stamp=lambda s:read(OUT/f'manifests/{s}-ledger.json')['completed_unix']
    require(stamp('RW08-RW10')>c['registered_unix'] and stamp('RW17-RW18')>stamp('RW15-RW16') and stamp('RW25')>stamp('RW20'),'Phase chronology')
    fits=sum(len(t) for t in logs.values()); require(fits<=780,'Fit budget')
    write(OUT/'verification.json',{'pass':True,'old_files_unchanged':len(c['baseline_sha256']),
      'zero_parameter_max_error':zeroerr,'probability_max_error':perr,'weights_max_error':werr,
      'direction_max_error':directionerr,'objective_max_error':objectiveerr,'actual_new_fits':fits,
      'post_only_read_audit':True,'train_only_OOF_direction_audit':True,'source_query_content_disjoint':True,
      'registered_entity_crossfold_overlap':0,'universal_TCP_epoch_proof':False,
      'permission_whitelist_not_OS_sandbox':True,'offline_test_pre_no_model_feedback':True})
    finish('RW27',verified=True,new_fits=fits)
if __name__=='__main__': main()
