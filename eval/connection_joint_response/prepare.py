"""Only trusted packer may open whole native cache; workers receive scoped bags."""
from common import *
from representation import summarize

def run():
    with stage('prepare'):
        c=contract(); checked(NATIVE,c['fixed_files'][rel(NATIVE)],'trusted-full-cache-packer')
        df=pd.read_parquet(NATIVE); folds=pd.read_parquet(FOLDS)
        require(len(df)==23566 and df.pair_id.is_unique and df.session_id.nunique()==480,'Cohort changed')
        require(df.groupby('protocol').size().to_dict()==dict(zip(PROTOCOLS,[5608,5957,5919,6082])),'Deployment counts')
        require(set(df.repetition)=={1,2,3,4} and df.content_id.nunique()==30,'Content/repetition count')
        require(df.common_valid_nonempty.all(),'Qualification changed')
        foldmap=dict(zip(folds.content_id,folds.fold)); require(df.content_id.map(foldmap).eq(df.fold).all(),'Fold mismatch')
        overlaps={f:int(df.groupby(f).fold.nunique().gt(1).sum()) for f in
                  ['pair_id','session_id','logical_id','carrier_id','registered_epoch_proxy','content_id']}
        require(not any(overlaps.values()),'Registered entity crosses fold')
        pools={}; statepool={}; support=[]; native_checks=[]
        for side in ['pre','post']:
            rows={r:[] for r in INPUTS}; st=[]
            for sid,part in df.groupby('session_id',sort=True):
                meta=part.iloc[0]
                x=part[[side+'_'+f for f in FEATURES]].copy(); x.columns=FEATURES
                values,s=summarize(x)
                for d in ['up','down']:
                    require((part[side+'_R_unique_'+d]<=part[side+'_E_'+d]).all(),'Direction run bound')
                require((part[side+'_R_unique_up']+part[side+'_R_unique_down']).eq(part[side+'_R_unique_zero_runs']).all(),'Run replay')
                for rep,h in values.items():
                    row={k:meta[k] for k in ['protocol','content_id','label_id','fold']}
                    row['visit_id']=token('business-query-v1:',sid)
                    row.update(dict(zip(INPUTS[rep],h))); rows[rep].append(row)
                q=part[['pair_id','session_id','content_id','protocol','content_visit_flow_mass']].copy()
                q['visit_id']=token('business-query-v1:',sid)
                for g in range(4):q['s'+str(g)]=s[:,g]
                for f in FEATURES:q[f]=x[f].to_numpy()
                st.append(q)
                for g in range(4):
                    h=values['J'][96+slice_joint(g).start:96+slice_joint(g).stop]
                    support.append({'side':side,'visit_id':row['visit_id'],'block':NAMES[g],
                                    'occupied_states':int((h>0).sum()),'sum_error':abs(h.sum()-1)})
            for rep,v in rows.items():pools[side,rep]=pd.DataFrame(v).sort_values('visit_id').reset_index(drop=True)
            statepool[side]=pd.concat(st,ignore_index=True)
        packages={}; roleaudits=[]; replay=0.
        def store(d,p,kind,scope):
            save(d,p); packages[rel(p)]={'sha256':sha(p),'kind':kind,'scope':scope,
                                        'columns':list(d),'rows':len(d)}
        def take(side,rep,protocols,contents):
            a=pools[side,rep]
            return a[a.protocol.isin(protocols)&a.content_id.isin(contents)].copy().sort_values(
                ['protocol','visit_id'],kind='stable').reset_index(drop=True)
        for r in c['roles']:
            root=rolepath(r)
            for rep in INPUTS:
                cols=INPUTS[rep]
                source=take('post',rep,r['sources'],r['train_contents'])
                pre=take('pre',rep,r['sources'],r['train_contents']).drop(columns='visit_id').sort_values(
                    ['protocol','label_id',*HIST],kind='stable').reset_index(drop=True)
                cp=take('post',rep,[r['target']],r['C_contents'])
                cb=take('pre',rep,[r['target']],r['C_contents'])
                query=take('post',rep,[r['target']],r['validation_contents'])
                require(len(source)==len(pre)==288 and len(cp)==len(cb)==64 and len(query)==24,'Role coverage')
                for name,d in [('source-post',source),('source-pre',pre),('C-post',cp)]:
                    store(d,root/rep/(name+'.parquet'),name,r)
                store(query[['visit_id',*cols]],root/rep/'query.parquet','query',r)
                if rep=='M':
                    for name,new in [('source-post',source),('source-pre',pre),('C-post',cp),('query',query)]:
                        oldp=ROOT/'outputs/calibrated-deployment-business-transfer-20261006/run-01/packages'/r['id']/(name+'.parquet')
                        checked(oldp,c['fixed_files'][rel(oldp)],'historical-M-replay'); old=pd.read_parquet(oldp)
                        require(len(new)==len(old),'Historical row count')
                        if 'visit_id' in old:old=old.set_index('visit_id').loc[new.visit_id]
                        else:
                            require(new[['content_id','protocol','label_id']].reset_index(drop=True).equals(
                                old[['content_id','protocol','label_id']].reset_index(drop=True)),'Source pre ordering changed')
                        replay=max(replay,float(np.max(np.abs(new[HIST].to_numpy()-old[HIST].to_numpy()))))
                for inner,validation in enumerate(r['inner_validation_contents']):
                    iq=source[source.content_id.isin(validation)]
                    store(iq,root/rep/f'inner-query-{inner}.parquet','inner-query',r)
                if rep=='J':
                    pair=cb[['visit_id',*cols]].merge(cp[['visit_id','content_id',*cols]],on='visit_id',
                        suffixes=('_pre','_post'),validate='one_to_one')
                    paired=pd.DataFrame({'content_token':pair.content_id.map(lambda u:token('ja-content:',u)),
                                         'fit_mass':np.full(len(pair),1/64)})
                    for side in ['pre','post']:
                        for f in cols:paired[side+'_'+f]=pair[f+'_'+side].to_numpy()
                    store(paired,root/'C-paired.parquet','C-paired',r)
                    for side,frame in [('pre',cb),('post',cp)]:
                        grouped=frame[['content_id',*cols]].rename(columns={'content_id':'content_token'})
                        grouped['content_token']=grouped.content_token.map(lambda u:token('ja-content:',u))
                        grouped['fit_mass']=1/64
                        grouped=grouped.sample(frac=1,random_state=103 if side=='pre' else 209).reset_index(drop=True)
                        store(grouped,root/f'C-group-{side}.parquet','C-group',r)
                        anon=grouped[cols+['fit_mass']].sample(frac=1,random_state=307 if side=='pre' else 419)
                        store(anon,root/f'C-marginal-{side}.parquet','C-marginal',r)
            labelq=query[['visit_id','content_id','label_id','protocol']]
            store(labelq,root/'labels.parquet','labels',r)
            for inner,val in enumerate(r['C_diagnostic_contents']):
                dr=root/'diagnostics'/f'i{inner}'
                frames={side:statepool[side][statepool[side].protocol.eq(r['target'])&
                    statepool[side].content_id.isin(r['C_contents'])].copy() for side in ['pre','post']}
                train={side:d[~d.content_id.isin(val)].copy() for side,d in frames.items()}
                test={side:d[d.content_id.isin(val)].copy() for side,d in frames.items()}
                paired=train['pre'][['pair_id','content_id','content_visit_flow_mass',*[f's{g}' for g in range(4)]]].merge(
                    train['post'][['pair_id',*[f's{g}' for g in range(4)]]],on='pair_id',suffixes=('_pre','_post'),validate='one_to_one')
                paired=paired.rename(columns={'content_id':'content_token','content_visit_flow_mass':'fit_mass'}).drop(columns='pair_id')
                paired.content_token=paired.content_token.map(lambda u:token('cj-content:',u))
                store(paired,dr/'paired.parquet','diag-paired',r)
                for side in ['pre','post']:
                    gp=train[side][['content_id','content_visit_flow_mass',*[f's{g}' for g in range(4)]]].rename(
                        columns={'content_id':'content_token','content_visit_flow_mass':'fit_mass'})
                    gp.content_token=gp.content_token.map(lambda u:token('cj-content:',u))
                    store(gp.sample(frac=1,random_state=103 if side=='pre' else 209),dr/f'group-{side}.parquet','diag-group',r)
                tq=test['pre'][['pair_id',*[f's{g}' for g in range(4)]]].copy()
                tq.pair_id=tq.pair_id.map(lambda v:token('cj-diag-query:',v))
                store(tq,dr/'query.parquet','diag-query',r)
                score=test['post'][['pair_id','content_id','content_visit_flow_mass',*[f's{g}' for g in range(4)]]].copy()
                score.pair_id=score.pair_id.map(lambda v:token('cj-diag-query:',v))
                score['post_U_total']=test['post'].U_up.to_numpy()+test['post'].U_down.to_numpy()
                # Attach only diagnostic C pre operands; never a main-classifier query.
                prealign=test['pre'].set_index('pair_id').loc[test['post'].pair_id]
                for d in ['up','down']:
                    for f in ['U','E']:
                        score['pre_'+f+'_'+d]=prealign[f+'_'+d].to_numpy()
                        score['post_'+f+'_'+d]=test['post'][f+'_'+d].to_numpy()
                store(score,dr/'score.parquet','diag-score',r)
            roleaudits.append({'role_id':r['id'],'source_visits':288,'C_visits':64,'H_post_queries':24,
                'target_U_worker_rows':0,'H_pre_worker_rows':0,'source_sides_row_matched':False})
        require(replay<=1e-14,'Old M replay failed')
        save(pd.DataFrame(support),OUT/'audits/feature-support.parquet')
        save(pd.DataFrame(roleaudits),OUT/'audits/role-permissions.parquet')
        write(OUT/'audits/cohort-and-native.json',{'pairs':len(df),'visits':480,'contents':30,'registered_crossfold':overlaps,
             'native_inequalities_passed':True,'missing_imputation':False,'universal_TCP_epoch_proof':False,
             'trusted_packer_full_cache_read':True,'target_U_worker_numeric_rows':0,'raw_capture_reads':0,'M_replay_error':replay})
        preparation={'packages':packages,'roles':60,'representations':[96,162,162],'M_replay_error':replay,
                     'full_native_cache_available_only_to_trusted_packer':True}
        write(OUT/'manifests/preparation.json',preparation)
        write(OUT/'manifests/preparation-seal.json',{'sha256':sha(OUT/'manifests/preparation.json')})
        progress('prepared_packages',roles=60,packages=len(packages),M_replay_error=replay)

if __name__=='__main__':run()
