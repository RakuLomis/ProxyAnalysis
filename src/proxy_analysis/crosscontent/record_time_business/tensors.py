"""B4-B5: single-side sequence contracts, train-only coordinates and donors."""
import hashlib
from collections import Counter
import numpy as np
import pandas as pd
from .data import OUT,PAIR,KEY,SIDE,cfg,load,save,js,read,digest

def token_structure(lengths,types=None):
    length=np.asarray(lengths,dtype=np.float64);end=np.cumsum(length);total=end[-1]
    x=np.zeros((len(length),7),dtype=np.float64)
    x[:,0]=np.log1p(length);x[:,1]=(end-length)/total;x[:,2]=end/total
    if types is not None:
        for col,kind in enumerate([20,21,22,23]):x[:,3+col]=np.asarray(types)==kind
    return x.astype(np.float32)

def time_tokens(events):
    # Group exact capture ties without imposing an unobserved direction ordering.
    g=events.groupby(['relative_time_ns','direction']).new_payload_bytes.sum().unstack(fill_value=0).sort_index()
    ns=g.index.to_numpy(dtype=np.int64);t=(ns-ns[0])/1e6;dt=np.diff(t,prepend=0)
    return np.log1p(np.column_stack([t,dt,g.get(1,pd.Series(0,index=g.index)),g.get(-1,pd.Series(0,index=g.index))])).astype(np.float32)

def build():
    assert read(OUT/'qualification-gate.json')['passed']
    common=load('common-flow-cohort');keys=common[PAIR];r=load('record-units').merge(keys,on=PAIR,validate='many_to_one')
    ev=load('newbyte-events').merge(keys,on=PAIR,validate='many_to_one')
    rg={k:g for k,g in r.groupby(KEY)};eg={k:g for k,g in ev.groupby(SIDE)}
    dest=OUT/'tensors';dest.mkdir(exist_ok=True);rows=[]
    for row in common.to_dict('records'):
        sid=row['session_id'];cid=row['connection_id']
        uid=hashlib.sha256((sid+'|'+cid).encode()).hexdigest()[:24]
        for side in ['pre','post']:
            events=eg[(sid,cid,side)];arrays={'T':time_tokens(events)}
            for d,name in [(1,'up'),(-1,'down')]:
                records=rg[(sid,cid,side,d)].sort_values('record_index')
                packets=events[events.direction==d].sort_values(['relative_time_ns','packet_ordinal'])
                total=int(records.end.max());assert packets.new_payload_bytes.sum()==total
                sizes=np.diff(np.r_[np.arange(0,total,cfg()['chunk_bytes']),total])
                arrays['R_'+name]=token_structure(records.end-records.start,records.content_type)
                arrays['P_'+name]=token_structure(packets.new_payload_bytes)
                arrays['C_'+name]=token_structure(sizes)
            path=dest/(uid+'-'+side+'.npz');np.savez_compressed(path,**arrays)
            rows.append({'uid':uid,'session_id':sid,'connection_id':cid,'side':side,'path':str(path),'sha256':digest(path),
               **{k+'_tokens':len(v) for k,v in arrays.items()}})
    save('tensor-manifest',rows)
    js('input-schema.json',{'static':['log1p_length','start_fraction','end_fraction','type20','type21','type22','type23'],
       'time':['log1p_relative_ms','log1p_delta_ms','log1p_up_newbytes','log1p_down_newbytes'],
       'independent_shared_time':True,'type_is_syntax_only':True,'all_sequences_untruncated':True,
       'P_position':'cumulative_first_contribution_not_contiguous_sequence_interval',
       'no_record_instantaneous_time_input':True,'FR_unchanged':True,'post_extractor_accepts_pre':False,
       'source_links':'source-links.parquet owns first-observed byte intervals; join by interval overlap to record-units; no payload',
       'zero_time_ties_aggregated':True})
    print('B4 tensors:',len(rows),flush=True)

class Store:
    def __init__(self):
        m=load('tensor-manifest');self.data={};self.visit={};self.uid_to_visit={}
        for r in m.to_dict('records'):
            with np.load(r['path']) as a:self.data[r['uid'],r['side']]={k:a[k] for k in a.files}
            if r['side']=='post':
                self.visit.setdefault(r['session_id'],[]).append(r['uid']);self.uid_to_visit[r['uid']]=r['session_id']
        for s in self.visit:self.visit[s].sort()

def moments(arrays):
    # Each array contributes equally, independent of its number of tokens.
    return np.mean([x.mean(axis=0,dtype=np.float64) for x in arrays],axis=0),np.mean([(x.astype(np.float64)**2).mean(axis=0) for x in arrays],axis=0)

def fit_scaler(store,visits,rep):
    first=[];second=[]
    for sid in visits:
        per_flow=[]
        for uid in store.visit[sid]:
            a=store.data[uid,'post'];arrays=[a['T']] if rep=='T' else [a[rep+'_up'],a[rep+'_down']]
            per_flow.append(moments(arrays))
        first.append(np.mean([v[0] for v in per_flow],axis=0));second.append(np.mean([v[1] for v in per_flow],axis=0))
    mean=np.mean(first,axis=0);var=np.maximum(0,np.mean(second,axis=0)-mean**2);scale=np.sqrt(var);scale[scale<1e-10]=1
    if rep!='T':mean[3:]=0;scale[3:]=1
    return {'mean':mean.tolist(),'scale':scale.tolist(),'variance':var.tolist(),'fit_visits':sorted(visits)}

def schedule(train,store,seed,steps):
    """Every step contains all four repetitions of six training contents.

    Same rank selected on a content's four visits. Rank held for two cycles, so
    L2 pre/pre then post/post matches L3/L4 pre/post exposure exactly.
    """
    assert len(train)==96 and steps%8==0
    rng=np.random.default_rng(seed);contents=sorted(train.content_id.unique());rng.shuffle(contents)
    slots=[];pool=[];groups={}
    for content in contents:
        visits=train[train.content_id==content].sort_values('repetition')
        assert visits.repetition.tolist()==[1,2,4,5]
        ids=visits.session_id.tolist();k=min(len(store.visit[s]) for s in ids);assert k>0
        chosen={}
        for sid in ids:
            chosen[sid]=sorted(store.visit[sid],key=lambda u:hashlib.sha256(f'{seed}|{u}'.encode()).hexdigest())[:k]
            for j,uid in enumerate(chosen[sid]):pool.append({'session_id':sid,'uid':uid,'rank':j,'content_id':content,'k':k})
        groups[content]=(ids,chosen,k)
    for step in range(steps):
        cycle=step//4;batch=[]
        for content in contents[(step%4)*6:(step%4+1)*6]:
            ids,chosen,k=groups[content];rank=(cycle//2)%k
            for i,sid in enumerate(ids):batch.append({'session_id':sid,'uid':chosen[sid][rank],'donor_uid':chosen[ids[(i+1)%4]][rank]})
        assert Counter(x['uid'] for x in batch)==Counter(x['donor_uid'] for x in batch)
        assert all(x['uid']!=x['donor_uid'] and store.uid_to_visit[x['donor_uid']]!=x['session_id'] for x in batch)
        slots.append({'step':step,'L2_side':'pre' if cycle%2==0 else 'post','batch':batch})
    true=Counter();wrong=Counter();l2=Counter();visits_count=Counter()
    for s in slots:
        for b in s['batch']:
            visits_count[b['session_id']]+=1
            for side in ['pre','post']:true[b['uid'],side]+=1
            wrong[b['uid'],'post']+=1;wrong[b['donor_uid'],'pre']+=1
            l2[b['uid'],s['L2_side']]+=2
    assert true==wrong==l2 and len(set(visits_count.values()))==1
    return slots,pool,{'fixed_point_free':True,'preserves_exposure_per_uid_side':True,'equal_visit_exposure':True,
       'visits':len(visits_count),'slots_per_visit':next(iter(visits_count.values())),'steps':steps,
       'flow_semantic_equivalence_across_repetitions':False,'labels_used_to_construct_donor':False}

def prepare():
    store=Store();folds=load('folds');cohort=load('cohort');exposure=[];poolrows=[];scalers={}
    for fold in range(5):
        train=folds[(folds.fold==fold)&(folds.split=='train')]
        test=folds[(folds.fold==fold)&(folds.split=='test')]
        assert not set(train.content_id)&set(test.content_id)
        for rep in ['P','R','C','T']:scalers[f'{fold}:{rep}']=fit_scaler(store,train.session_id,rep)
        for seed in cfg()['seeds']:
            slots,pool,audit=schedule(train,store,seed,cfg()['steps'])
            js(f'schedule-{fold}-{seed}.json',slots)
            exposure.append({'fold':fold,'seed':seed,**audit})
            poolrows.extend({'fold':fold,'seed':seed,**r} for r in pool)
    js('preprocessors.json',scalers);js('exposure-audit.json',exposure);save('ssl-pool',poolrows)
    js('donor-audit.json',{'all_15_contexts_passed':True,'no_test_donors':True,'no_self_pair':True,'no_cross_content':True,
       'same_content_not_same_resource_flow':True,'SSL_pool_is_common_to_all_arms':True,'supervised_uses_all_common_flows':True})
    pool=pd.DataFrame(poolrows);counts=pool.groupby(['fold','seed','session_id']).size().rename('ssl_flows').reset_index()
    counts['all_common_flows']=counts.session_id.map(lambda s:len(store.visit[s]));counts['flow_retention']=counts.ssl_flows/counts.all_common_flows
    save('ssl-pool-retention',counts)
    print('B5 scalers and all donor/exposure audits passed',flush=True)
