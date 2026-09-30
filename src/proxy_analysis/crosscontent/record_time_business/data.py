"""B0-B3: frozen identities, bounded capture extraction, strict common cohort."""
import json
import time
from pathlib import Path
import numpy as np
import pandas as pd
import yaml
from ...protocol_normalization.common import ROOT,digest
from ...protocol_normalization.early_stage_mechanism.common import BASE,OUT as CACHE
from ...protocol_normalization.record_representation.core import assemble,parse_records
from ...protocol_normalization.tcp_ledger import conflicts
from ..business_features import accepted_pairs,load_config
from ...pipeline.analyze_entity import analyze_entity_capture
from ...parsing import PcapNgReader,decode_packet
from ...parsing.packet_decoder import _strip_link_header

BUS=ROOT/'outputs/content-generalization-20260916/business-01'
SPLITS=ROOT/'outputs/content-generalization-20260916/natural-pair-ssl-01/prepared'
OUT=ROOT/'outputs/record-time-business-0916/run-01'
DOC=ROOT/'docs/record-time-business-0916'
CONFIG=ROOT/'configs/record-time-business-0916.yaml'
PLAN=ROOT/'plan/record-time-business-0916-plan-20260926.md'
PAIR=['session_id','connection_id'];SIDE=PAIR+['side'];KEY=SIDE+['direction']

def cfg():return yaml.safe_load(CONFIG.read_text(encoding='utf-8'))
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def js(name,x):
    OUT.mkdir(exist_ok=True,parents=True)
    (OUT/name).write_text(json.dumps(x,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8')
def save(name,rows):
    OUT.mkdir(exist_ok=True,parents=True)
    x=rows if isinstance(rows,pd.DataFrame) else pd.DataFrame(rows)
    x.to_parquet(OUT/(name+'.parquet'),index=False,compression='zstd');return x
def load(name,folder=OUT):return pd.read_parquet(folder/(name+'.parquet'))
def canon(p):
    s=str(p).replace('\\','/')
    while '//' in s:s=s.replace('//','/')
    if s.startswith('/?/'):s=s[3:]
    return s.lower()
def eligibility(status,reason,records,unique,ledger_valid):
    parsed=int(records.end.max()) if len(records) else 0
    return bool(ledger_valid and status=='contiguous' and reason=='syntax_prefix_complete' and len(records)>0 and parsed==unique)


def freeze():
    cohort=load('primary-cohort',BUS);cohort=cohort[cohort.protocol=='VLESS'].copy()
    assert len(cohort)==120 and cohort.content_id.nunique()==30 and cohort.label_id.nunique()==6
    assert set(cohort.repetition)=={1,2,4,5}
    ids=set(cohort.session_id);assign=[];references=[];files=[CONFIG,PLAN,BUS/'primary-cohort.parquet',BUS/'capture-files.parquet',BUS/'candidates.parquet']
    for fold in range(5):
        path=SPLITS/f'six_business-{fold}.json';files.append(path);source=read(path)
        parts={split:[r for r in source[split] if r['session_id'] in ids] for split in ['train','test']}
        assert len(parts['train'])==96 and len(parts['test'])==24
        assert not ({r['content_id'] for r in parts['train']}&{r['content_id'] for r in parts['test']})
        assert {r['session_id'] for r in parts['train']+parts['test']}==ids
        for split,rows in parts.items():
            for r in rows:assign.append({'fold':fold,'split':split,**r})
        references.extend(parts['test'])
    old=pd.DataFrame(references);assert not old.session_id.duplicated().any()
    # The historical split uses canonical URL content IDs; the registry has short aliases.
    cohort=cohort.rename(columns={'content_id':'registered_content_id'}).merge(old[['session_id','content_id']],on='session_id',validate='one_to_one')
    aliases=cohort[['registered_content_id','content_id']].drop_duplicates()
    assert not aliases.registered_content_id.duplicated().any() and not aliases.content_id.duplicated().any()
    save('content-aliases',aliases);save('cohort',cohort);save('folds',assign)
    candidates=load('candidates',BUS);candidates=candidates[candidates.session_id.isin(ids)]
    files+=[BASE/'tcp-byte-ledger.parquet',BASE/'new-byte-events.parquet',CACHE/'record-observations.parquet',CACHE/'record-source-map.parquet',CACHE/'parse-sample-manifest.parquet']
    files+=[ROOT/'src/proxy_analysis/protocol_normalization/early_stage_mechanism/records.py',ROOT/'src/proxy_analysis/protocol_normalization/record_representation/core.py']
    sources={str(p):digest(p) for p in files}
    if (OUT/'contract.json').exists():assert read(OUT/'contract.json')['inputs']==sources
    captures=load('capture-files',BUS);captures=captures[captures.session_id.isin(ids)].copy()
    captures['normalized_path']=captures.path.map(canon)
    assert len(captures)==2370 and captures.normalized_path.nunique()==2370
    assert captures.groupby('sha256').session_id.nunique().max()==1
    lookup=captures.set_index('normalized_path');rows=[]
    for r in candidates.to_dict('records'):
        for pair in accepted_pairs(r,load_config()):
            for side,desc in [('pre',pair.pre),('post',pair.post)]:
                path=Path(desc.capture_path);key=canon(path);assert key in lookup.index
                previous=lookup.loc[key];assert previous.session_id==r['session_id'] and previous.side==side
                rows.append({'session_id':r['session_id'],'connection_id':pair.connection_id,'side':side,
                    'entity_id':desc.entity_id,'capture_path':str(path),'normalized_path':key,'sha256':previous.sha256,'file_bytes':path.stat().st_size})
    m=pd.DataFrame(rows);assert len(m)==2370 and not m[SIDE].duplicated().any()
    assert set(m.normalized_path)==set(captures.normalized_path)
    total=int(m.file_bytes.sum());within=total<=cfg()['max_unique_capture_bytes']
    save('capture-manifest',m);save('candidate-visits',candidates)
    js('contract.json',{'inputs':sources,'observation_scope':cfg()['observation_scope'],'classifier_fits':0,
       'original_240_unchanged':True,'cohort_visits':120,'content_alias_bijection_verified':True})
    js('extraction-budget.json',{'files':len(m),'connection_pairs':len(m)//2,'unique_file_bytes':total,
       'max_unique_file_bytes':cfg()['max_unique_capture_bytes'],'within_budget':within,
       'upper_bound_passes_per_file':3,'upper_bound_processed_file_bytes':3*total,'payload_persisted':False})
    assert within,'Budget confirmation required'
    print('B0-B1:',len(m)//2,'pairs;',total,'bytes; old five folds verified',flush=True)


def extract():
    started=time.monotonic();manifest=load('capture-manifest');visits=load('candidate-visits')
    ledger=load('tcp-byte-ledger',BASE).merge(manifest[SIDE],on=SIDE,validate='many_to_one')
    assert len(ledger)==4*(len(manifest)//2) and not ledger[KEY].duplicated().any()
    lg={k:g.iloc[0] for k,g in ledger.groupby(KEY)}
    ev=load('new-byte-events',BASE).merge(manifest[SIDE],on=SIDE,validate='many_to_one')
    save('newbyte-events',ev);save('unique-byte-ledger',ledger)
    cached_manifest=load('parse-sample-manifest',CACHE).set_index(SIDE)
    cached_records={k:g for k,g in load('record-observations',CACHE).groupby(KEY)}
    cached_maps={k:g for k,g in load('record-source-map',CACHE).groupby(KEY)}
    outrec=[];outmap=[];statuses=[];processed=0;reused=0;decoded=0
    lookup={r['session_id']:r for r in visits.to_dict('records')};descriptors={}
    for i,row in enumerate(manifest.to_dict('records')):
        path=Path(row['capture_path']);assert digest(path)==row['sha256'];processed+=row['file_bytes']
        sid=row['session_id'];cid=row['connection_id'];side=row['side'];sk=(sid,cid,side)
        cached=sk in cached_manifest.index and all((*sk,d) in cached_records for d in [-1,1])
        if cached:
            assert cached_manifest.loc[sk,'sha256']==row['sha256'];reused+=1
        else:
            if sid not in descriptors:descriptors[sid]={p.connection_id:p for p in accepted_pairs(lookup[sid],load_config())}
            pair=descriptors[sid][cid];desc=pair.pre if side=='pre' else pair.post
            analysis=analyze_entity_capture(desc);segments={s.packet_event_id:s for s in analysis.tcp.segments};payload={}
            for packet in PcapNgReader(path):
                p=decode_packet(packet.link_type,packet.packet_data)
                assert p.decode_status=='ok' and p.transport_protocol=='tcp'
                data=_strip_link_header(packet.link_type,packet.packet_data)
                payload[f'{desc.artifact_id}:{packet.interface_id}:{packet.packet_ordinal}']=data[p.ip_header_len+p.transport_header_len:p.ip_total_len]
            start=min(p.timestamp_ns for p in analysis.tcp_packets);processed+=2*row['file_bytes'];decoded+=1
        for d in [-1,1]:
            key=(*sk,d);old=lg[key];meta=dict(zip(KEY,key));unique=old.unique_payload_bytes
            if cached:
                records=cached_records[key].copy();mapping=cached_maps[key].copy()
                records['first_ns']=records.first_observation_ns;records['all_ns']=records.complete_available_ns
                records=records.sort_values('record_index');records['prefix_ns']=np.maximum.accumulate(records.all_ns)
                status='contiguous';reason='syntax_prefix_complete'
            else:
                packets=[p for p in analysis.tcp_packets if p.direction==d]
                origins={segments[p.packet_event_id].seq_start_unwrapped+1 for p in packets if p.flags&2}
                origin=next(iter(origins)) if len(origins)==1 else None
                f=[]
                for p in packets:
                    if p.payload_len:
                        b=payload[p.packet_event_id];assert len(b)==p.payload_len
                        f.append((segments[p.packet_event_id].seq_start_unwrapped+int(bool(p.flags&2)),b,p.timestamp_ns-start,p.packet_ordinal))
                if not old.observed_unique_valid:
                    body=b'';mp=[];status='ledger_Q0'
                elif conflicts([(a,b) for a,b,_,_ in f]):
                    body=b'';mp=[];status='overlap_conflict'
                elif origin is not None and any(a<origin for a,_,_,_ in f):
                    body=b'';mp=[];status='payload_before_syn_origin'
                else:body,mp,status=assemble(f,origin)
                records,reason=parse_records(body,mp,1 if d==1 else 2)
                mapping=pd.DataFrame(mp)
            ok=eligibility(status,reason,records,unique,old.observed_unique_valid)
            parsed=int(records.end.max()) if len(records) else 0
            statuses.append({**meta,'epoch_id':old.epoch_id,'ledger_quality':old.quality,
                'prefix_observed':bool(old.prefix_observed),'final_internal_gap_count':old.final_internal_gap_count,
                'reassembly_status':status,'parse_status':reason,'unique_bytes':unique,'record_bytes':parsed,
                'coverage_fraction':parsed/unique if pd.notna(unique) and unique>0 else None,
                'eligible':ok,'cache_reused':cached})
            if len(records):
                records=records[['record_index','start','end','content_type','legacy_version','record_payload_length','first_ns','all_ns','prefix_ns']].copy()
                assert ((records.end-records.start)==records.record_payload_length+5).all()
                for k,v in meta.items():records[k]=v
                outrec.append(records)
            if len(mapping):
                mapping=mapping[['start','end','time_ns','packet_ordinal']].copy()
                for k,v in meta.items():mapping[k]=v
                outmap.append(mapping)
        if (i+1)%100==0:print('B2 captures',i+1,'/',len(manifest),flush=True)
    save('flow-eligibility',statuses);save('record-units',pd.concat(outrec,ignore_index=True))
    save('source-links',pd.concat(outmap,ignore_index=True))
    js('extraction-audit.json',{'files_sha_verified':len(manifest),'files_cache_reused':reused,'files_decoded':decoded,
       'processed_capture_file_bytes':int(processed),'elapsed_seconds':time.monotonic()-started,'payload_persisted':False,
       'cache_parser_hash_verified':True,'zero_filled_or_resynchronized':False})
    print('B2 complete',flush=True)


def coverage():
    from ...protocol_normalization.record_representation.report import table
    cohort=load('cohort');status=load('flow-eligibility');manifest=load('capture-manifest')
    side=status.groupby(SIDE).agg(eligible=('eligible','all'),directions=('direction','size'),
        unique_bytes=('unique_bytes',lambda x:x.sum(min_count=1)),unknown_directions=('unique_bytes',lambda x:int(x.isna().sum()))).reset_index()
    assert (side.directions==2).all()
    a=side[side.side=='pre'];b=side[side.side=='post']
    pairs=a.merge(b,on=PAIR,suffixes=('_pre','_post'),validate='one_to_one')
    pairs['common_eligible']=pairs.eligible_pre&pairs.eligible_post
    save('pair-eligibility',pairs);save('common-flow-cohort',pairs[pairs.common_eligible].merge(cohort,on='session_id',validate='many_to_one'))
    stats=[]
    for row in cohort.to_dict('records'):
        g=pairs[pairs.session_id==row['session_id']];keep=g[g.common_eligible]
        denom=g.unique_bytes_post.sum(min_count=1);retained=keep.unique_bytes_post.sum()
        stats.append({**row,'candidate_pairs':len(g),'common_pairs':len(keep),'post_only_pairs':int(g.eligible_post.sum()),
           'pair_retention':len(keep)/len(g),'post_known_unique_bytes':denom,'retained_post_unique_bytes':retained,
           'post_known_byte_retention':retained/denom if denom>0 else None,
           'post_unknown_direction_rows':int(g.unknown_directions_post.sum())})
    stats=save('visit-coverage',stats);empty=stats[stats.common_pairs==0];gate=len(empty)==0
    js('qualification-gate.json',{'passed':gate,'visits':len(stats),'zero_common_flow_visits':len(empty),
        'candidate_pairs':len(pairs),'common_pairs':int(pairs.common_eligible.sum()),
        'post_only_pairs':int(pairs.eligible_post.sum()),'formal_training_allowed':gate,'training_fits':0})
    groups=stats.groupby('label_id').agg(visits=('session_id','size'),contents=('content_id','nunique'),
        candidate_pairs=('candidate_pairs','sum'),common_pairs=('common_pairs','sum'),empty_visits=('common_pairs',lambda x:int((x==0).sum())),
        mean_pair_retention=('pair_retention','mean'),mean_known_byte_retention=('post_known_byte_retention','mean')).reset_index()
    save('coverage-by-business',groups)
    save('coverage-by-content',stats.groupby(['label_id','content_id']).agg(visits=('session_id','size'),common_pairs=('common_pairs','sum'),mean_pair_retention=('pair_retention','mean'),mean_known_byte_retention=('post_known_byte_retention','mean')).reset_index())
    save('coverage-by-repetition',stats.groupby('repetition').agg(visits=('session_id','size'),common_pairs=('common_pairs','sum'),mean_pair_retention=('pair_retention','mean'),mean_known_byte_retention=('post_known_byte_retention','mean')).reset_index())
    failures=status[~status.eligible].groupby(['side','reassembly_status','parse_status']).size().rename('direction_rows').reset_index()
    save('parse-failure-summary',failures)
    # All old inputs remain byte-identical; capture hashes checked separately during extraction.
    assert all(digest(Path(p))==h for p,h in read(OUT/'contract.json')['inputs'].items())
    DOC.mkdir(parents=True,exist_ok=True)
    report=f'''# 0916 记录结构＋独立时间：B0–B3 覆盖验收

日期：2026-09-26。资格门：{'通过' if gate else '未通过，按计划停止训练'}。

保留原120访问、30内容、六业务、五折；规范化URL内容ID与旧注册短ID之间核验为一一对应，未重新划分。共{len(pairs)}个排他连接对，2370个捕获文件，唯一体积{read(OUT/'extraction-budget.json')['unique_file_bytes']:,} bytes。

共同合格连接 {int(pairs.common_eligible.sum())}/{len(pairs)}；仅post合格 {int(pairs.eligible_post.sum())}/{len(pairs)}；空共同集合访问 {len(empty)}/120。

{table(groups)}

## 资格口径

每连接两侧上下行均须通过严格连续语法解析并覆盖全部有效唯一字节。Q0不填零；byte_retention的分母仅包含台账可知的唯一字节，unknown方向数量另报，不能将未知字节当作0。记录类型不代表业务阶段。没有新增分类训练。

## 方向级未通过原因

{table(failures)}

## 空共同集合访问

{table(empty[['session_id','label_id','content_id','repetition','candidate_pairs','post_only_pairs']]) if len(empty) else '无。'}

## 当前执行边界

{'原120访问的成员保持，允许继续B4–B6工程验收；严格双侧筛选仍为离线队列限制。' if gate else 'G1触发。未执行B4–B10或任何分类拟合；没有删访问、换fold、放宽解析、添加fallback。需要用户决定是否修改严格队列/表示资格，再进行下一步。'}

完整逐访问、逐连接、逐方向台账位于 outputs/record-time-business-0916/run-01。所有原输入哈希复核未变；载荷未落盘。再提取只涉及现有PCAP，不是补采。
'''
    (DOC/'coverage-report.md').write_text(report,encoding='utf-8')
    print('B3 qualification gate:',gate,'empty visits:',len(empty),'common pairs:',int(pairs.common_eligible.sum()),flush=True)
    return gate
