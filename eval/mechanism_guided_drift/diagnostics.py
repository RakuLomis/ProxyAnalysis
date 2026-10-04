"""P2 fixed-role cache diagnostics. No classifier, PCAP, query-post or sampling."""
from pathlib import Path
import argparse
import time
import sys
import numpy as np
import pandas as pd
import pyarrow.parquet as pq
from common import ROOT, OLD, LATEST, OUT as REG, read_json, write_json, digest, file_hash, git
from local_rules import local_rule_checks

OUT = REG.parent / 'diagnostics'
EXTRACT = OLD / 'extraction-03'
W = ['W_up','W_down','P_up','P_down','R_up','R_down']
T = ['U_up','U_down','E_up','E_down','R_up','R_down']
AUX = ['log_entities_up','log_entities_down','log_q50_up','log_q50_down',
       'log_q90_up','log_q90_down','small_ratio_up','small_ratio_down']
TAUX = ['small_ratio_up','small_ratio_down']
PROTOCOLS = ['shadowsocks','vless','trojan','vmess','anytls']


def seal():
    OUT.mkdir(parents=True,exist_ok=True)
    cohort=pd.read_parquet(LATEST/'cohort.parquet')
    assert len(cohort)==600 and cohort.content_id.nunique()==30
    assert cohort.groupby('content_id').fold.nunique().eq(1).all()
    assert cohort.groupby(['protocol','content_id']).repetition.agg(set).map(lambda x:x=={1,2,3,4}).all()
    jobs=[]; hashes={}
    for protocol in PROTOCOLS:
        for fold in range(5):
            role=read_json(LATEST/'roles'/f'E1-all-f{fold}.json')
            assert set(role['train']).isdisjoint(role['test'])
            for q in range(4):
                path=LATEST/'generator-roles'/f'{protocol}-f{fold}-q{q}.json'
                job=read_json(path);hashes[str(path.relative_to(ROOT))]=file_hash(path)
                assert set(job['fit_sessions'])|set(job['query_sessions']) <= set(role['train'])
                assert len(job['fit_sessions'])==72
                for inner in job['loco']:
                    assert len(inner['fit_sessions'])==68 and len(inner['held_sessions'])==4
                    assert set(inner['fit_sessions']).isdisjoint(inner['held_sessions'])
                    assert set(inner['fit_sessions'])|set(inner['held_sessions'])==set(job['fit_sessions'])
                    a=cohort[cohort.session_id.isin(inner['fit_sessions'])]
                    b=cohort[cohort.session_id.isin(inner['held_sessions'])]
                    assert set(a.content_id).isdisjoint(b.content_id)
                jobs.append(job)
    isolation=read_json(EXTRACT/'isolation-01/summary.json')
    identity=read_json(EXTRACT/'identity-source-evidence/qualification.json')
    assert identity['qualified_for_registered_entity_grouping']
    assert all(isolation[k]==0 for k in ['cross_fold_registered_carriers','cross_fold_SYN_signatures',
        'cross_fold_positive_IP_packet_hash_matches','overlapping_windows','repeated_raw_file_hashes'])
    for path in [LATEST/'cohort.parquet',LATEST/'global-folds.parquet',EXTRACT/'full-W-features.parquet',
                 EXTRACT/'full-T-features.parquet',REG/'protocol-profile-registry.json',REG/'mechanism-contract.json',
                 OLD/'entity-graph.parquet',OLD/'carrier-lifecycle-evidence.parquet']:
        hashes[str(path.relative_to(ROOT))]=file_hash(path)
    code={str(p.relative_to(ROOT)):file_hash(p) for p in Path(__file__).parent.glob('*.py')}
    contract={'version':'P2-cache-diagnostic-v1','G1_human_approval':'同意，请你继续',
        'date':'2026-10-04','git_commit':git('rev-parse','HEAD'),'main_visits':600,'contents':30,
        'protocols':PROTOCOLS,'outer_folds':5,'W_jobs':100,'W_LOCO_fits_per_method':1800,
        'W_fit_visits':68,'W_fit_contents':17,'W_held_visits':4,
        'W_models':['training_median_additive','frozen_W_ridge','pre_proxy_W_ridge'],
        'T_models':['training_median_additive','log_T_additive_ridge','pre_proxy_T_additive_ridge'],
        'T_fit_scope':'outer training only, LOCO23/24 content, common-valid nonempty pairs only',
        'proxy_W_columns':AUX,'proxy_T_columns':TAUX,'alpha':1.,'constant_quantile':.5,
        'small_payload_threshold':256,'load_quantiles':[.25,.5,.75],
        'bootstrap_samples':1000,'bootstrap_seed':20261004,
        'bootstrap_unit':'content; average repeated same-visit OOF predictions before resampling',
        'primary_diagnostic_outer_fold':0,'other_outer_folds':'sensitivity, overlapping not independent',
        'post_reads':'explicit per-outer-fold training session filter; never query or outer-test post in fit',
        'preflight_exception':{'session_id':'004b3a67-76a8-42cc-af62-66dcf612ccc7','protocol':'trojan','fold':2,
            'kind':'one T-pairs JSON schema-inspection accidentally printed both-side summaries before seal',
            'use':'none for model design, fit or selection','blind_claim':False},
        'candidate_family_predeclared':'pre-only connection-density startup center, not exact protocol K',
        'classifier_training':False,'residual_sampling':False,'pcap_reads':False,'P3_allowed':False,
        'input_sha256':hashes,'code_sha256':code}
    dest=OUT/'diagnostic-contract.json'
    if dest.exists():
        old=read_json(dest)
        assert old==contract,'contract differs: preserve old output, do not silently overwrite'
    else:write_json(dest,contract)
    write_json(OUT/'diagnostic-roles.json',{'jobs':jobs,'identity_qualification':identity,'historical_isolation':isolation,
        'all_600_members_preserved':True,'global_content_folds':True,'no_random_flow_split':True})
    write_json(OUT/'mechanism-unit-tests.json',{'synthetic':True,'checks':local_rule_checks(),
        'capture_mechanism_verification':False,'Vision_active_in_Extend':False,'internal_write_counts_observed':False})
    print('sealed 100 W jobs / 1800 LOCO; no classifier; G1 accepted, G2 pending',flush=True)


def metadata():
    cohort=pd.read_parquet(LATEST/'cohort.parquet')
    sessions=pd.read_parquet(OLD/'sessions.parquet',columns=['session_id','protocol','dataset_role','content_id'])
    graph=pd.read_parquet(OLD/'entity-graph.parquet',columns=['session_id','protocol','content_id','logical_conn_id','carrier_id','relation'])
    main=graph[graph.session_id.isin(cohort.session_id)].merge(cohort[['session_id','fold']],on='session_id')
    real=main[main.carrier_id.notna() & main.carrier_id.ne('')]
    cross=int(real.groupby(['protocol','carrier_id']).fold.nunique().gt(1).sum())
    assert cross==0
    h=graph[graph.protocol.eq('hysteria2')].merge(sessions[sessions.protocol.eq('hysteria2')][['session_id','dataset_role']],on='session_id')
    hc=h[h.dataset_role.eq('content')].merge(cohort[['content_id','fold']].drop_duplicates(),on='content_id',how='left')
    hd=hc[hc.carrier_id.notna() & hc.carrier_id.ne('')]
    hy2={'selected_sessions':int(sessions.protocol.eq('hysteria2').sum()),
         'content_sessions':int(h[h.dataset_role.eq('content')].session_id.nunique()),
         'content_carriers':int(hd.carrier_id.nunique()),
         'carriers_cross_content':int(hd.groupby('carrier_id').content_id.nunique().gt(1).sum()),
         'carriers_cross_global_fold':int(hd.groupby('carrier_id').fold.nunique().gt(1).sum()),
         'missing_global_fold_sessions':int(hc[hc.fold.isna()].session_id.nunique()),
         'W_numeric_cache_available':False,'classified':False,
         'reason':'not a member of qualified 600 cache; shared carrier content audit, no new PCAP extraction'}
    lifecycle=pd.read_parquet(OLD/'carrier-lifecycle-evidence.parquet')
    summaries=[]
    for _,row in cohort.iterrows():
        sid=row.session_id;sc=read_json(EXTRACT/'sessions'/sid/'scope.json')
        allowed=set(sc['carriers']);f=lifecycle[lifecycle.session_id.eq(sid)&lifecycle.carrier_id.isin(allowed)]
        binds=f[f.event_type.eq('logical_carrier_bind')]
        summaries.append({'session_id':sid,'protocol':row.protocol,'content_id':row.content_id,'fold':row.fold,
            'selected_carriers':len(allowed),'logged_open_carriers':int(f[f.event_type.eq('carrier_open')].carrier_id.nunique()),
            'bind_created':int(binds.relation.eq('created').sum()),'bind_reused':int(binds.relation.eq('reused').sum()),
            'lifecycle_events':len(f),'offline_log_only':True,'padding_counter_observed':False,'scheme_update_observed':False})
    carrier=pd.DataFrame(summaries);carrier.to_parquet(OUT/'carrier-lifecycle-metadata.parquet',index=False)
    avail={'main_visits':600,'cross_fold_registered_carriers_recheck':cross,'Hy2':hy2,
        'Extend_strict_record_cache_files':len(list(EXTRACT.rglob('*record*parquet'))),
        'T_AnyTLS_qualification':False,'W_unit':'all observed selected-window transport payload incl retransmission',
        'T_unit':'unique TCP new bytes in common-valid nonempty connection pairs',
        'all_scope_files':all((EXTRACT/'sessions'/s/'scope.json').exists() for s in cohort.session_id),
        'schemas':{name:pq.read_schema(EXTRACT/name).names for name in ['full-W-features.parquet','full-T-features.parquet']},
        'lifecycle_sources':'captured log, not pre-only query input'}
    write_json(OUT/'feature-availability.json',avail)
    write_json(OUT/'feature-provenance.json',{'W':{'columns':W,'permission':'pre query / paired post training target'},
        'pre_proxy':{'columns':AUX,'source':'pre-W-events.parquet only','unit':'observed payload packet, not chunk/record',
            'log_entities':'distinct positive-payload pre entity IDs per direction; numeric count only, not IDs'},
        'T_proxy':{'columns':TAUX,'source':'T-newbyte-events side==pre common-valid logical IDs',
            'unit':'new-byte observation event, not application Write'},
        'lifecycle':{'permission':'offline log strata only','for_generator':False},
        'membership':{'permission':'frozen offline paired eligibility','online_segmentation_proven':False},
        'forbidden_numeric_inputs':['IP','port','SNI','domain','URL','UUID','content_id','session_id','carrier_id','label_id'],
        'missing_records':'unavailable; never filled by zeros'})
    return cohort,carrier


def pre_cache(cohort):
    rows=[];counts=[]
    for index,row in cohort.iterrows():
        path=EXTRACT/'sessions'/row.session_id/'pre-W-events.parquet'
        events=pd.read_parquet(path,columns=['direction','payload_bytes','entity_id'])
        assert events.payload_bytes.gt(0).all()
        item={'session_id':row.session_id}
        for direction,name in [(1,'up'),(-1,'down')]:
            f=events[events.direction.eq(direction)];v=f.payload_bytes.to_numpy()
            item['log_entities_'+name]=float(np.log1p(f.entity_id.nunique()))
            item['log_q50_'+name]=float(np.log1p(np.quantile(v,.5))) if len(v) else 0.
            item['log_q90_'+name]=float(np.log1p(np.quantile(v,.9))) if len(v) else 0.
            item['small_ratio_'+name]=float(np.mean(v<=256)) if len(v) else 0.
            counts.append({'session_id':row.session_id,'direction':direction,'packet_count':len(v),
                           'payload_bytes':int(v.sum()),'entity_count':int(f.entity_id.nunique()),'empty_direction':not len(v)})
        rows.append(item)
        if (index+1)%100==0:print('pre-only cache',index+1,'/600',flush=True)
    aux=pd.DataFrame(rows);aux.to_parquet(OUT/'pre-only-proxy.parquet',index=False)
    pd.DataFrame(counts).to_parquet(OUT/'pre-only-count-audit.parquet',index=False)
    return aux


def connection_cache(cohort,fold):
    # Only outer TRAIN session IDs are passed here. Never loads a T-pairs JSON.
    rows=[];eligibility=[]
    for _,meta in cohort.iterrows():
        if meta.protocol=='anytls':continue
        folder=EXTRACT/'sessions'/meta.session_id
        ledger=pd.read_parquet(folder/'T-direction-ledger.parquet')
        pre=ledger[ledger.side.eq('pre')].set_index(['logical_id','direction'])
        post=ledger[ledger.side.eq('post')].set_index(['logical_id','direction'])
        good=[]
        for logical in sorted(set(pre.index.get_level_values(0))&set(post.index.get_level_values(0))):
            keys=[(logical,1),(logical,-1)]
            if not all(k in pre.index and k in post.index for k in keys):continue
            a=pre.loc[keys];b=post.loc[keys]
            if a.valid.all() and b.valid.all() and a.unique_bytes.sum()>0 and b.unique_bytes.sum()>0:good.append(logical)
        events=pd.read_parquet(folder/'T-newbyte-events.parquet',filters=[('side','==','pre'),('logical_id','in',good)]) if good else pd.DataFrame()
        summaries={}
        if len(events):
            for (logical,direction),f in events.groupby(['logical_id','direction']):
                v=f.sort_values(['timestamp_ns','raw_packet_ordinal']).new_bytes.to_numpy()
                summaries[(logical,direction)]=(len(v),float(np.mean(v<=256)),int(v.sum()))
        # Segment counts are recomputed on each side using cached events, train-only.
        postev=pd.read_parquet(folder/'T-newbyte-events.parquet',filters=[('side','==','post'),('logical_id','in',good)]) if good else pd.DataFrame()
        for logical in good:
            item={'outer_fold':fold,'session_id':meta.session_id,'protocol':meta.protocol,
                  'content_id':meta.content_id,'logical_id':logical}
            for side,ev,led in [('pre',events,pre),('post',postev,post)]:
                f=ev[ev.logical_id.eq(logical)].sort_values(['timestamp_ns','raw_packet_ordinal'])
                ds=f.direction.to_numpy();starts=np.r_[True,ds[1:]!=ds[:-1]] if len(ds) else np.array([],bool)
                for direction,name in [(1,'up'),(-1,'down')]:
                    d=f[f.direction.eq(direction)]
                    item[side+'_U_'+name]=int(led.loc[(logical,direction),'unique_bytes'])
                    item[side+'_E_'+name]=len(d)
                    item[side+'_R_'+name]=int(np.sum(starts&(ds==direction)))
                    item[side+'_closed_'+name]=bool(led.loc[(logical,direction),'closed_contiguous'])
                    if side=='pre':item['small_ratio_'+name]=summaries.get((logical,direction),(0,0.,0))[1]
                    assert int(d.new_bytes.sum())==item[side+'_U_'+name]
            rows.append(item)
        eligibility.append({'outer_fold':fold,'session_id':meta.session_id,'registered_logical':int(ledger.logical_id.nunique()),'common_valid_nonempty':len(good)})
    return pd.DataFrame(rows),eligibility


def run():
    import diagnostic_models as dm
    contract=read_json(OUT/'diagnostic-contract.json')
    for path,h in contract['code_sha256'].items():assert file_hash(ROOT/path)==h,'code changed after seal'
    write_json(OUT/'cuda-replay.json',dm.replay())
    cohort,carrier=metadata();aux=pre_cache(cohort)
    allpre=pd.read_parquet(EXTRACT/'full-W-features.parquet',filters=[('side','==','pre')]).merge(cohort,on='session_id').merge(aux,on='session_id')
    audit=pd.read_parquet(OUT/'pre-only-count-audit.parquet')
    for direction,name in [(1,'up'),(-1,'down')]:
        x=allpre.set_index('session_id');q=audit[audit.direction.eq(direction)].set_index('session_id').loc[x.index]
        assert np.array_equal(x['W_'+name],q.payload_bytes)
        assert np.array_equal(x['P_'+name],q.packet_count)
    jobs=read_json(OUT/'diagnostic-roles.json')['jobs'];predictions=[];fitlog=[];access=[];connections=[];eligibility=[];windows=[]
    begin=time.time()
    for fold in range(5):
        members=cohort[cohort.fold.ne(fold)];ids=members.session_id.tolist();assert len(ids)==480
        post=pd.read_parquet(EXTRACT/'full-W-features.parquet',filters=[('side','==','post'),('session_id','in',ids)])
        assert set(post.session_id)==set(ids)
        pre=allpre[allpre.session_id.isin(ids)].set_index('session_id');post=post.set_index('session_id')
        access.append({'outer_fold':fold,'post_W_session_ids':ids,'outer_test_post_read':False,'query_post_used':False})
        for job in [j for j in jobs if j['fold']==fold]:
            for inner in job['loco']:
                train=pre.loc[inner['fit_sessions']];held=pre.loc[inner['held_sessions']]
                a=train[W].to_numpy(float);b=post.loc[train.index,W].to_numpy(float);q=held[W].to_numpy(float)
                target=post.loc[held.index,W].to_numpy(float);encoded=dm.wm.encode(b)
                models={'training_median_additive':dm.median_offset(a,b[:,:2],q),
                    'frozen_W_ridge':dm.wm.decode(dm.wm.Ridge(a,encoded).predict(q))[0][:,:2],
                    'pre_proxy_W_ridge':dm.wm.decode(dm.WindowProxy(a,encoded,train[AUX].to_numpy()).predict(q,held[AUX].to_numpy()))[0][:,:2]}
                boundaries=np.quantile(a[:,:2],[.25,.5,.75],axis=0)
                for method,estimate in models.items():
                    estimate=estimate.cpu().numpy()
                    for n,(sid,row) in enumerate(held.iterrows()):
                        for d,name in enumerate(['up','down']):
                            predictions.append({'level':'W','outer_fold':fold,'job':job['job'],'method':method,'protocol':job['protocol'],
                                'content_id':row.content_id,'session_id':sid,'direction':name,'prediction':float(estimate[n,d]),
                                'target':float(target[n,d]),'pre_bytes':float(q[n,d]),'load_bin':int(np.searchsorted(boundaries[:,d],q[n,d],side='right')),
                                'zero_pre':bool(q[n,d]==0),'negative_estimate':bool(estimate[n,d]<0),
                                'closed_both':None,'entities':float(np.expm1(row['log_entities_'+name]))})
                fitlog.append({'level':'W','job':job['job'],'held_content':inner['held_content'],'fit_sessions':inner['fit_sessions'],
                    'held_sessions':inner['held_sessions'],'fit_contents':17,'fit_rows':68,'device':'cuda','models':list(models)})
        trainwindow=pre.reset_index()[['session_id','protocol','content_id',*W]].merge(post.reset_index()[['session_id','W_up','W_down']],on='session_id',suffixes=('_pre','_post')).merge(carrier,on=['session_id','protocol','content_id'])
        trainwindow['outer_fold']=fold;windows.append(trainwindow)
        conn,el=connection_cache(members,fold);connections.append(conn);eligibility.extend(el)
        for protocol,g in conn.groupby('protocol'):
            assert g.content_id.nunique()==24
            for content in sorted(g.content_id.unique()):
                train=g[g.content_id.ne(content)];held=g[g.content_id.eq(content)]
                a=train[['pre_'+n for n in T]].to_numpy(float);b=train[['post_U_up','post_U_down']].to_numpy(float)
                q=held[['pre_'+n for n in T]].to_numpy(float);target=held[['post_U_up','post_U_down']].to_numpy(float)
                models={'training_median_additive':dm.median_offset(a,b,q),
                    'log_T_additive_ridge':dm.AdditiveRidge(a,b).predict(q),
                    'pre_proxy_T_additive_ridge':dm.AdditiveRidge(a,b,train[TAUX].to_numpy()).predict(q,held[TAUX].to_numpy())}
                boundaries=np.quantile(a[:,:2],[.25,.5,.75],axis=0)
                for method,estimate in models.items():
                    estimate=estimate.cpu().numpy()
                    for n,(_,row) in enumerate(held.iterrows()):
                        for d,name in enumerate(['up','down']):
                            predictions.append({'level':'T','outer_fold':fold,'job':protocol+'-T-LOCO','method':method,'protocol':protocol,
                                'content_id':row.content_id,'session_id':row.session_id,'logical_id':row.logical_id,'direction':name,
                                'prediction':float(estimate[n,d]),'target':float(target[n,d]),'pre_bytes':float(q[n,d]),
                                'load_bin':int(np.searchsorted(boundaries[:,d],q[n,d],side='right')),
                                'zero_pre':bool(q[n,d]==0),'negative_estimate':bool(estimate[n,d]<0),
                                'closed_both':bool(row['pre_closed_'+name] and row['post_closed_'+name]),'entities':1.})
                fitlog.append({'level':'T','outer_fold':fold,'protocol':protocol,'held_content':content,
                    'fit_contents':23,'fit_rows':len(train),'held_rows':len(held),'device':'cuda','models':list(models)})
        print('outer fold',fold,'complete; elapsed',round(time.time()-begin,1),'seconds',flush=True)
    pd.DataFrame(predictions).to_parquet(OUT/'oof-predictions.parquet',index=False)
    pd.concat(connections,ignore_index=True).to_parquet(OUT/'connection-diagnostics.parquet',index=False)
    pd.DataFrame(eligibility).to_parquet(OUT/'connection-eligibility.parquet',index=False)
    pd.concat(windows,ignore_index=True).to_parquet(OUT/'carrier-window-diagnostics.parquet',index=False)
    write_json(OUT/'fit-ledger.json',{'fits':fitlog,'cuda':True,'classifier_fits':0,'query_post_access':False,'outer_test_post_access':False})
    write_json(OUT/'access-ledger.json',{'folds':access,'pre_reads':'all600, only pre values; selected-window membership is offline',
        'post_connection_reads':'per-fold outer training members only; held inner targets used scoring, never fitting',
        'preflight_exception':contract['preflight_exception']})
    unchanged={path:file_hash(ROOT/path)==h for path,h in contract['input_sha256'].items()}
    assert all(unchanged.values())
    write_json(OUT/'diagnostic-audit.json',{'passed':True,'frozen_inputs_unchanged':unchanged,'cuda_replay':read_json(OUT/'cuda-replay.json'),
        'fit_ledger_rows':len(fitlog),'W_inner_tasks':1800,'T_inner_tasks':480,'classifier_fits':0,'PCAP_reads':0,
        'residual_draws':0,'old_outputs_modified':False,'G2_pending':True,'P3_started':False,
        'universal_TCP_epoch_proof':False,'historical_unobserved_SYN':5,'preflight_exception_disclosed':True,
        'elapsed_seconds':time.time()-begin})
    print('P2 regression complete; G2 pending',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('step',choices=['seal','run']);args=parser.parse_args()
    if args.step=='seal':seal()
    else:run()
