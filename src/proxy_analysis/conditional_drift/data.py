from .common import *

def freeze():
    OUT.mkdir(parents=True,exist_ok=True);DOC.mkdir(parents=True,exist_ok=True)
    files=[CONFIG,PLAN,BUS/'primary-cohort.parquet',BUS/'capture-files.parquet',
      *[BASE/(n+'.parquet') for n in ['tcp-byte-ledger','byte-direction-runs','connection-eligibility','primary240-measurement-coverage','registry']],
      *[PREP/f'six_business-{f}.json' for f in range(5)],
      ROOT/'docs/record-time-business-0916/localization/summary.md',
      *Path(__file__).parent.glob('*.py'),ROOT/'eval/conditional_proxy_drift/run.py']
    obj={'inputs':{str(p):digest(p) for p in sorted(files)},'config':config(),'old_outputs_read_only':True,'planned_classifier_tasks':210}
    if (OUT/'contract.json').exists():assert read(OUT/'contract.json')==obj,'Input/code contract changed'
    else:js('contract.json',obj)

def prepare():
    cohort=load('primary-cohort',BUS)
    assert len(cohort)==240 and not cohort.session_id.duplicated().any()
    rows=[]
    for f in range(5):
        old=read(PREP/f'six_business-{f}.json')
        for split in ['train','test']:
            rows.extend({'fold':f,'split':split,**r} for r in old[split])
    folds=pd.DataFrame(rows)
    assert len(folds)==1200 and set(folds.session_id)==set(cohort.session_id)
    test=folds[folds.split=='test'];assert len(test)==240 and not test.session_id.duplicated().any()
    cohort=cohort.rename(columns={'content_id':'registered_content_id'}).merge(test[['session_id','content_id']],on='session_id',validate='one_to_one')
    aliases=cohort[['registered_content_id','content_id']].drop_duplicates()
    assert not aliases.registered_content_id.duplicated().any() and not aliases.content_id.duplicated().any()
    assert cohort.content_id.nunique()==30 and cohort.label_id.nunique()==6
    assert cohort.groupby(['protocol','content_id']).repetition.apply(lambda x:sorted(x)==[1,2,4,5]).all()
    save('cohort',cohort);save('outer-folds',folds);save('content-aliases',aliases)
    ledger=load('tcp-byte-ledger',BASE);ledger=ledger[ledger.session_id.isin(cohort.session_id)]
    runs=load('byte-direction-runs',BASE);runs=runs[runs.session_id.isin(cohort.session_id)&runs.threshold_bytes.eq(0)]
    assert not ledger.duplicated(['session_id','connection_id','side','direction']).any()
    assert not runs.duplicated(['session_id','connection_id','side']).any()
    run_lookup={(sid,cid,side):g.iloc[0] for (sid,cid,side),g in runs.groupby(['session_id','connection_id','side'])}
    eligible=[];excluded=[];values=[]
    for (sid,cid),g in ledger.groupby(['session_id','connection_id']):
        reason=''
        if len(g)!=4 or set(zip(g.side,g.direction))!={('pre',1),('pre',-1),('post',1),('post',-1)}:reason='missing_direction_or_side'
        elif set(g.scope)!={'exclusive_tcp_pair'} or set(g.main_route)!={'proxy'}:reason='scope_or_route'
        elif not g.observed_unique_valid.all() or g.sequence_epoch_ambiguous.any() or g.overlap_content_conflicts.any():reason='invalid_unique_measurement'
        elif any((sid,cid,side) not in run_lookup for side in ['pre','post']):reason='missing_runs'
        if reason:
            excluded.append({'session_id':sid,'connection_id':cid,'protocol':g.protocol.iloc[0],'reason':reason});continue
        pair_values=[]
        for side in ['pre','post']:
            d=g[g.side==side].set_index('direction');r=run_lookup[sid,cid,side]
            directions=np.asarray(r.directions);bytes_=np.asarray(r.new_bytes)
            assert len(directions)==len(bytes_)==r.run_count and (bytes_>0).all()
            assert set(directions).issubset({-1,1})
            assert not (directions[1:]==directions[:-1]).any()
            for direction in [1,-1]:
                assert bytes_[directions==direction].sum()==d.loc[direction,'unique_payload_bytes'],'Direction bytes do not reconcile'
            x=np.array([d.loc[1,'unique_payload_bytes'],d.loc[-1,'unique_payload_bytes'],
               d.loc[1,'new_data_event_count'],d.loc[-1,'new_data_event_count'],(directions==1).sum(),(directions==-1).sum()])
            if x[:2].sum()==0:reason='empty_pair_side';break
            assert not illegal(x,1),f'Observed primitive inconsistency: {sid} {cid} {side} {illegal(x,1)}'
            pair_values.append({'session_id':sid,'connection_id':cid,'side':side,**dict(zip(FEATURES,x.astype('int64'))),
              'F':1,'closed_candidate':bool(d.closed_contiguous_capture_candidate.all())})
        if reason:excluded.append({'session_id':sid,'connection_id':cid,'protocol':g.protocol.iloc[0],'reason':reason});continue
        values.extend(pair_values);eligible.append({'session_id':sid,'connection_id':cid,'protocol':g.protocol.iloc[0]})
    pairs=save('eligible-pairs',eligible);save('excluded-pairs',pd.DataFrame(excluded,columns=['session_id','connection_id','protocol','reason']))
    flow=save('connection-primitives',values)
    coverage=cohort.merge(pairs.groupby('session_id').size().rename('F'),on='session_id',how='left').fillna({'F':0})
    save('coverage',coverage)
    if coverage.F.eq(0).any():
        js('stage-gate.json',{'stage':'F1','passed':False,'reason':'visits_without_pairs','classification_started':False})
        raise StageGate('F1: visits without eligible pair require user decision')
    total=flow.groupby(['session_id','side'])[FEATURES+['F']].sum().reset_index()
    total=total.merge(cohort,on='session_id',validate='many_to_one');assert len(total)==480
    assert total.groupby('session_id').F.nunique().eq(1).all()
    for r in total.to_dict('records'):assert not illegal([r[k] for k in FEATURES],r['F'])
    save('paired-primitives',total)
    inner=[];donors=[];tasks=[]
    for f in range(5):
      ff=folds[folds.fold==f];train=ff[ff.split=='train'];test=ff[ff.split=='test']
      assert not set(train.content_id)&set(test.content_id)
      mapping={}
      for label,g in train.groupby('label_id'):
        contents=sorted(g.content_id.unique());assert len(contents)==4
        mapping.update({c:i for i,c in enumerate(contents)})
      for dep in config()['deployments']:
        tr=train[train.protocol==dep];te=test[test.protocol==dep]
        assert len(tr)==96 and len(te)==24
        assert not set(pairs[pairs.session_id.isin(tr.session_id)].connection_id)&set(pairs[pairs.session_id.isin(te.session_id)].connection_id)
        for r in tr.to_dict('records'):inner.append({**r,'inner_fold':mapping[r['content_id']]})
        for content,g in tr.groupby('content_id'):
            g=g.sort_values('repetition');ids=g.session_id.tolist();assert len(ids)==4
            for i,sid in enumerate(ids):donors.append({'fold':f,'protocol':dep,'content_id':content,'session_id':sid,'donor_session_id':ids[(i+1)%4]})
        for inner_fold in range(4):
            fit=tr[tr.content_id.map(mapping)!=inner_fold];query=tr[tr.content_id.map(mapping)==inner_fold]
            assert len(fit)==72 and len(query)==24 and not set(fit.content_id)&set(query.content_id)
            tasks.append({'fold':f,'protocol':dep,'inner_fold':inner_fold,'fit_sessions':sorted(fit.session_id),
                'query_sessions':sorted(query.session_id),'fit_contents':sorted(fit.content_id.unique()),'query_contents':sorted(query.content_id.unique()),
                'fit_content_hash':object_hash(sorted(fit.content_id.unique()))})
    save('inner-folds',inner);save('wrong-pair-donors',donors);js('generation-tasks.json',tasks)
    captures=load('capture-files',BUS);captures=captures[captures.session_id.isin(cohort.session_id)]
    assert captures.groupby('sha256').session_id.nunique().max()==1,'Capture reused across visits'
    drift=total[total.side=='pre'].merge(total[total.side=='post'],on=['session_id','content_id','protocol','label_id','repetition','F','registered_content_id','primary_candidate','selection'],suffixes=('_pre','_post'),validate='one_to_one')
    records=[]
    for r in drift.to_dict('records'):
        for feature in FEATURES:
            a=r[feature+'_pre'];b=r[feature+'_post']
            records.append({k:r[k] for k in ['session_id','content_id','protocol','label_id','repetition']}|{'feature':feature,'pre':a,'post':b,'difference':b-a,'log1p_difference':float(np.log1p(b)-np.log1p(a)),'log_ratio':float(np.log(b/a)) if a>0 and b>0 else None})
    save('observed-drifts',records)
    summary=coverage.groupby('protocol').agg(visits=('session_id','size'),contents=('content_id','nunique'),pairs=('F','sum'),min_pairs=('F','min')).reset_index()
    js('stage-gate.json',{'stage':'F3','passed':True,'visits':240,'pairs':len(pairs),'classification_started':False})
    (DOC/'coverage-report.md').write_text('# F0–F3 覆盖与划分审计\n\n'+table(summary)+'\n\n240访问全部保留；两侧使用相同合格连接集合，未要求TLS记录可解析。字段与零阈值段字节逐方向对账通过。继承旧五折；四个训练内内容折与LOCO范围已登记。capture哈希跨访问未复用。\n\n排除连接原因：\n\n'+table(pd.DataFrame(excluded).groupby(['protocol','reason']).size().rename('pairs').reset_index())+'\n\n未拟合分类器，未使用外层测试结果选择队列。\n',encoding='utf-8')
    print(summary.to_string(index=False),flush=True)
