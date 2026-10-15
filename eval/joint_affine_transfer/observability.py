"""Bounded training-only syntax audit. No decryption or semantic cutpoint."""
from collections import defaultdict
from common import *
sys.path.insert(0,str(ROOT/'src'))
from proxy_analysis.protocol_normalization.early_stage_mechanism.records import reassemble,tls_prefix
from proxy_analysis.extend_calibration.reassembly import NormalizedReader
from proxy_analysis.extend_calibration.extraction_v3 import mapping_add
from proxy_analysis.extend_calibration.audit import fs_path
from proxy_analysis.parsing import decode_packet
from proxy_analysis.parsing.packet_decoder import _strip_link_header

EXTRACT=ROOT/'outputs/extend-calibration-20260930/run-01/extraction-03/sessions'
CAPROOT=ROOT/'Datasets/extend'
LIMIT=2*1024*1024

def parser_tests():
    hello=bytes([1])+int(38).to_bytes(3,'big')+bytes(38)
    record=bytes([22,3,3])+len(hello).to_bytes(2,'big')+hello
    tests=[]
    def check(name,condition):require(condition,name);tests.append({'name':name,'passed':True})
    body,mp,_,_,st=reassemble([(0,record,0,0)],0);rec,reason=tls_prefix(body,mp,1)
    check('continuous hello syntax',len(rec)==1 and reason=='syntax_prefix_complete')
    body,mp,_,_,st=reassemble([(0,record[:3],0,0),(4,record[4:],1,1)],0)
    check('gap not filled',len(body)==3 and st=='gap_or_unobserved_prefix')
    body,mp,_,_,st=reassemble([(0,record,0,0),(0,b'\xff',1,1)],0)
    check('conflict rejected',st=='overlap_conflict' and not body)
    body,mp,_,_,st=reassemble([(0,record,0,0)],None)
    check('missing origin rejected',st=='missing_syn_origin')
    rec,reason=tls_prefix(record[:-1],[{'start':0,'end':len(record)-1,'time_ns':0,'packet_ordinal':0}],1)
    check('partial record not fabricated',not rec and reason=='partial_record_body')
    rec,reason=tls_prefix(b'\xff'+record,[{'start':0,'end':len(record)+1,'time_ns':0,'packet_ordinal':0}],1)
    check('no arbitrary resynchronization',not rec and reason=='invalid_header_no_resynchronization')
    write(OUT/'manifests/parser-unit-tests.json',{'passed':True,'checks':tests,'semantic_stage_available':False})

def run():
    configure();parser_tests()
    registry=ROOT/'outputs/mechanism-guided-drift-20261003/registry'
    files=[registry/'protocol-profile-registry.json',registry/'implementation-registry.json',
           registry/'protocol-field-registry.json',registry/'mechanism-contract.json',
           ROOT/'outputs/mihomo-protocol-audit-20261003/manifest.json',
           ROOT/'outputs/mechanism-guided-drift-20261003/diagnostics/feature-availability.json']
    hashes={rel(p):sha(p) for p in files}; profiles=read(files[0])['profiles']
    summary=[{k:p.get(k) for k in ['protocol','profile_id','build','missing_required_fields','rule_qualification']}
             for p in profiles]
    write(OUT/'observability/profile-evidence.json',{'source_sha256':hashes,'profiles':summary,
        'collection_commit':'74cfed919c03f07a21b252328fe48b72c5361215',
        'reference_commit':'88dcbf7f1614a67c3b36b848ee3592dfa92ada36','raw_secret_node_objects_read':False})
    # Filename inventory is not evidence of a qualified same-cohort cache.
    candidates=[]
    for folder in [ROOT/'outputs/extend-calibration-20260930',ROOT/'Datasets/extend']:
        for p in fs_path(folder).rglob('*record*.parquet'):
            normal=Path(str(p).removeprefix('\\\\?\\'))
            candidates.append({'path':rel(normal),'bytes':p.stat().st_size,'qualified_same_cohort':False})
    write(OUT/'observability/cache-inventory.json',{'filename_candidates':candidates,
        'existing_strict_same_cohort_cache_adopted':False,'old_strict_cache_count':read(files[-1])['Extend_strict_record_cache_files']})
    cols=['session_id','protocol','content_id','repetition','fold','label_id','pair_id','logical_id','carrier_id']
    raw=pd.read_parquet(Q/'features/paired-flow-features.parquet',columns=cols)
    sessions=pd.read_parquet(ROOT/'outputs/extend-calibration-20260930/run-01/sessions.parquet',
                             columns=['session_id','manifest_relative']).drop_duplicates('session_id').set_index('session_id')
    selected=[]
    for protocol in PROTOCOLS:
        d=raw[raw.protocol.eq(protocol)&raw.fold.ne(0)&~raw.label_id.isin([LABELS[2],LABELS[4]])]
        for label in [LABELS[i] for i in [0,1,3,5]]:
            content=sorted(d[d.label_id.eq(label)].content_id.unique())[0]
            q=d[d.content_id.eq(content)&d.repetition.eq(1)].sort_values('pair_id').head(2)
            require(len(q)==2 and q.session_id.nunique()==1,'Fixed parse member rule')
            selected.extend(q.to_dict('records'))
    manifest=pd.DataFrame(selected);require(manifest.session_id.nunique()==16 and len(manifest)==32,'Parse sample size')
    save(manifest,OUT/'observability/parse-sample-manifest.parquet')
    write(OUT/'observability/parse-sample-manifest.json',{'rows':selected,'capture_files_limit':16,
         'scan_bytes_limit':8*1024**3,'prefix_bytes_per_direction':LIMIT,'selection_reads_test':False,
         'selection_rule':'outer f0 G0 C; first lexical training content/class; repetition1; first2 pair_id',
         'scan_order':'label order 0,1,3,5 then fixed protocol order; pre then post'})
    records=[];maps=[];evidence=[];reads=[];scanbytes=0;count=0;exhausted=False
    visits=[]
    for sid,d in manifest.groupby('session_id'):
        a=d.iloc[0];visits.append((LABELS.index(a.label_id),PROTOCOLS.index(a.protocol),sid,d))
    for _,_,sid,chosen in sorted(visits,key=lambda z:z[:3]):
        first=chosen.iloc[0];session=(CAPROOT/str(sessions.loc[sid,'manifest_relative'])).parent
        require(session.resolve().is_relative_to(CAPROOT.resolve()),'PCAP outside named data root')
        flowpath=session/'analysis/flow-index.json';flowdoc=read(fs_path(flowpath))
        flows={f['conn_id']:f for f in flowdoc['items']}
        meta=read(EXTRACT/sid/'complete.json');start_ns=meta['start_ns'];end_ns=meta['end_ns']
        for side,name in [('pre','tun.pcap'),('post','phys.pcap')]:
            path=session/'raw'/name;reason=None
            if exhausted or count>=16:reason='fixed_file_budget_exhausted';exhausted=True
            elif not fs_path(path).exists():reason='registered_capture_missing'
            elif scanbytes+2*fs_path(path).stat().st_size>8*1024**3:reason='fixed_byte_budget_exhausted';exhausted=True
            if reason:
                for a in chosen.to_dict('records'):
                    for direction in [1,-1]:evidence.append({**a,'side':side,'direction':direction,'parse_status':reason,'records':0,'prefix_bytes':0})
                continue
            # Two explicit passes: raw hash then decode; both count toward scanning budget.
            sizebytes=fs_path(path).stat().st_size;count+=1;scanbytes+=2*sizebytes
            digest=hashlib.sha256()
            with fs_path(path).open('rb') as f:
                for chunk in iter(lambda:f.read(1024*1024),b''):digest.update(chunk)
            require(digest.hexdigest()==meta['input_hashes']['raw/'+name],'Historical raw capture hash changed')
            mapping=defaultdict(set);owners={}
            for a in chosen.to_dict('records'):
                flow=flows[a['logical_id']];ident=a['logical_id'] if side=='pre' else a['carrier_id'];owners[ident]=a
                if side=='pre':mapping_add(mapping,flow['pre_flow'],ident)
                else:
                    for pf in flow['carrier_binding'].get('physical_paths') or [flow['post_flow']]:mapping_add(mapping,pf,ident)
            addresses={(k[1],k[3]) for k in mapping};reader=NormalizedReader(fs_path(path),start_ns,end_ns,addresses)
            origins=defaultdict(set);fragments=defaultdict(list);bad=set();truncated=set()
            for rec in reader:
                if not start_ns<=rec.timestamp_ns<end_ns:continue
                p=decode_packet(rec.link_type,rec.packet_data)
                matches=mapping.get((p.transport_protocol,p.ip_src,p.src_port,p.ip_dst,p.dst_port),set())
                if not matches:continue
                if len(matches)!=1:
                    for ident,direction in matches:bad.add((ident,direction))
                    continue
                ident,direction=next(iter(matches));key=(ident,direction)
                if p.decode_status!='ok' or p.ip_fragment_offset or p.ip_more_fragments or rec.captured_len<rec.original_len:
                    bad.add(key);continue
                if p.tcp_flags_raw&2:origins[key].add((p.tcp_seq+1)%(2**32))
                if not p.transport_payload_len or len(origins[key])!=1:continue
                origin=next(iter(origins[key]));offset=((p.tcp_seq+int(bool(p.tcp_flags_raw&2))-origin+2**31)%(2**32))-2**31
                if offset<0:bad.add(key);continue
                data=_strip_link_header(rec.link_type,rec.packet_data)[p.ip_header_len+p.transport_header_len:p.ip_total_len]
                if len(data)!=p.transport_payload_len:bad.add(key);continue
                if offset>=LIMIT:truncated.add(key);continue
                if offset+len(data)>LIMIT:data=data[:LIMIT-offset];truncated.add(key)
                fragments[key].append((offset,data,int(rec.timestamp_ns-start_ns),int(rec.packet_ordinal)))
            reassembly_failures=reader.reassembly.finish()
            reads.append({'path':rel(path),'sha256':digest.hexdigest(),'bytes':sizebytes,'passes':2,
                          'flow_index_sha256':sha(fs_path(flowpath)),'session_id':sid,'side':side,
                          'fragment_reassembly_failures':reassembly_failures})
            for ident,a in owners.items():
                for direction in [1,-1]:
                    key=(ident,direction);m={**a,'side':side,'direction':direction}
                    origin=0 if len(origins[key])==1 else None
                    body,source,_,_,status=reassemble(fragments[key],origin)
                    if key in bad or reassembly_failures:body=b'';source=[];status='decode_or_identity_hold'
                    if side=='post' and a['protocol']=='shadowsocks':rr=[];why='SS_ciphertext_chunks_unobservable_no_keys'
                    else:rr,why=tls_prefix(body,source,1 if direction==1 else 2)
                    if rr and not any(r['hello_established'] for r in rr):rr=[];why='initial_hello_not_completed'
                    records.extend({**m,**r,'length':r['end']-r['start']} for r in rr)
                    maps.extend({**m,**q} for q in source)
                    evidence.append({**m,'parse_status':why,'reassembly_status':status,'records':len(rr),
                        'prefix_bytes':len(body),'prefix_limit_truncated':key in truncated,'semantic_stage':None})
            progress('JA_bounded_parse',files=count,scan_MiB=scanbytes/1048576,session=sid,side=side)
    save(pd.DataFrame(records),OUT/'observability/record-observations.parquet')
    save(pd.DataFrame(maps),OUT/'observability/record-source-map.parquet')
    save(pd.DataFrame(evidence),OUT/'observability/parse-evidence.parquet')
    write(OUT/'observability/audit.json',{'passed':True,'sample_visits':16,'sample_pairs':32,'directions':len(evidence),
        'unique_capture_files_read':count,'scan_bytes':scanbytes,'file_budget':16,'byte_budget':8*1024**3,
        'raw_payload_persisted':False,'source_reads':reads,'record_rows':len(records),
        'semantic_stage_identified':False,'classification_members_changed':False,'no_resync':True,
        'existing_filename_candidates_not_adopted':len(candidates)})
    grouped=pd.DataFrame(evidence).groupby(['protocol','side','parse_status']).size()
    lines=['# 协议机制可观测性资格报告','',
           '本轮仅使用固定训练样本与现有抓包。记录是语法证据，不是initial或relay阶段；不增加业务输入。',
           '',f'登记16访问、32连接对；实际读取{count}个PCAP，含哈希和解码两遍共{scanbytes/1024**3:.3f} GiB；记录{len(records)}条。',
           '', '文件预算耗尽的样本保持原登记且标注未解析，不拿成功子集替换分类队列。',
           '', '| 协议 | 侧 | 状态 | 方向数 |','| --- | --- | --- | ---: |']
    lines += [f'| {p} | {s} | {reason} | {n} |' for (p,s,reason),n in grouped.items()]
    lines += ['', 'SS实际chunk、VMess内部块与initial/relay仍不得补成观测量。AnyTLS及Hy2仍未进入本轮排他TCP分类。',
              '', '训练特权与测试post可生成性分开登记；详细来源、预算和失败见本地observability证据目录。']
    textfile(DOC/'mechanism-observability-report.md','\n'.join(lines)+'\n')
    qualify()

def qualify():
    evidence=pd.read_parquet(OUT/'observability/parse-evidence.parquet')
    profiles=read(OUT/'observability/profile-evidence.json');variables=[]
    for protocol in ['shadowsocks','vless','trojan','vmess','anytls','hysteria2']:
        for side in ['pre','post']:
            e=evidence[evidence.protocol.eq(protocol)&evidence.side.eq(side)]
            seen=int(e.records.sum()) if len(e) else 0
            applicable=protocol in PROTOCOLS and not (side=='post' and protocol=='shadowsocks')
            variables.append({'protocol':protocol,'side':side,'variable_id':'TLS_record_structure',
                'qualification':'single-side syntax observed on bounded sample' if seen else ('candidate not observed' if applicable else 'not qualified at this observation layer'),
                'source_sha256':profiles['source_sha256'],'evidence_path':rel(OUT/'observability/record-observations.parquet'),
                'evidence_sha256':sha(OUT/'observability/record-observations.parquet'),'observed_records':seen,
                'observation_unit':'side direction record interval within bounded TCP prefix',
                'interval_and_direction_columns':['direction','start','end'],
                'continuity_requirement':'unique SYN origin, nonconflicting prefix, no gap fill or resync',
                'training_available':seen>0,'post_only_rule_possible':side=='post' and seen>0,
                'independent_of_opposite_side':True,'test_post_feature_added':False,
                'configuration_required':'actual outer TLS; pre website TLS is a different layer',
                'restriction':'grammar only; not semantic phase, one-to-one record correspondence or whole-cohort coverage'})
        for variable,applicable,restriction in [
            ('SS_chunk_count',protocol=='shadowsocks','no independent chunk encoder evidence; do not infer from delta U'),
            ('VMess_internal_blocks',protocol=='vmess','WS/TLS exterior does not reveal encrypted internal blocks'),
            ('initial_relay',protocol in PROTOCOLS,'no independent captured semantic boundary'),
            ('W_minus_U',protocol in PROTOCOLS,'observed overlap/repetition, not pure retransmission'),
            ('carrier_lifecycle',True,'calibration logs do not prove online state or TCP pair qualification')]:
            q='not applicable at current layer'
            if applicable:q='single-side observed' if variable=='W_minus_U' else ('calibration privileged' if variable=='carrier_lifecycle' else 'latent or unavailable')
            variables.append({'protocol':protocol,'variable_id':variable,'qualification':q,
                'training_available':applicable and variable=='W_minus_U','test_post_feature_added':False,
                'configuration_required':'fixed Extend profile, not historical 0914/0916 defaults',
                'direction_and_intervals':'not resolved for latent state; W/U directional connection statistics',
                'source_sha256':profiles['source_sha256'],'restriction':restriction,
                'collection_commit':profiles['collection_commit'],'actual_hidden_state_identified':False})
    variables.append({'protocol':'shadowsocks','variable_id':'AEAD_format_constants','qualification':'confirmed local format rule',
        'salt_bytes':32,'per_chunk_overhead_bytes':34,'actual_chunk_count_observed':False,
        'configuration_required':'AES-256-GCM native TCP, complete encoded direction stream',
        'restriction':'not exact captured U difference','test_post_feature_added':False,'source_sha256':profiles['source_sha256']})
    write(OUT/'observability/variable-qualification.json',{'variables':variables,'new_classification_features':0})

if __name__=='__main__':qualify() if len(sys.argv)>1 and sys.argv[1]=='qualify' else run()
