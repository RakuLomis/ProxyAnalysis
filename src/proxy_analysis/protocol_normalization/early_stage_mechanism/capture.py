from .common import *
from .records import reassemble,tls_prefix,post_only_phase
from ...indexing.pairs import build_exclusive_pairs
from ...pipeline.analyze_entity import analyze_entity_capture
from ...parsing import PcapNgReader,decode_packet
from ...parsing.packet_decoder import _strip_link_header


def parse():
    manifest=load('parse-sample-manifest');budget=read(OUT/'budget.json')
    assert budget['within_budget'] and len(manifest)<=144
    # Frozen pre-data rule: record syntax is not a semantic phase marker.
    rule={'version':1,'header_versions':[769,770,771],'max_record_body':16640,'no_resync':True,
          'requires_syn_origin':True,'requires_initial_hello':True,'phase_detection':'unavailable',
          'reason':'no_independently_visible_Vision_command_in_existing_metadata; encrypted control cannot be inferred from length',
          'parameter_selection_uses_pre':False,'similarity_selected_cut':False}
    if (OUT/'phase-rule.json').exists():assert read(OUT/'phase-rule.json')==rule
    js('phase-rule.json',rule)
    reg=pd.read_parquet(BASE/'registry.parquet');reg=reg[reg.is_final].set_index('session_id')
    ledger=pd.read_parquet(BASE/'tcp-byte-ledger.parquet')
    descriptors={};recs=[];terms=[];evidence=[];failures=[];maps=[]
    for i,r in enumerate(manifest.sort_values(['partition','selection_hash','side']).to_dict('records')):
        path=Path(r['capture_path']);assert digest(path)==r['sha256'],'capture hash changed'
        sid=r['session_id'];cid=r['connection_id'];side=r['side']
        if sid not in descriptors:
            descriptors[sid]={p.connection_id:p for p in build_exclusive_pairs(reg.loc[sid,'session_path'],r['protocol'])}
        pair=descriptors[sid][cid];desc=pair.pre if side=='pre' else pair.post
        assert Path(desc.capture_path).resolve()==path.resolve()
        meta={k:r[k] for k in ['batch','protocol','session_id','connection_id','item_id','partition','mechanism_group','load_layer','side']}
        analysis=analyze_entity_capture(desc)
        byid={s.packet_event_id:s for s in analysis.tcp.segments}
        payloads={}
        for record in PcapNgReader(path):
            p=decode_packet(record.link_type,record.packet_data)
            assert p.transport_protocol=='tcp' and p.decode_status=='ok'
            data=_strip_link_header(record.link_type,record.packet_data)
            payloads[f'{desc.artifact_id}:{record.interface_id}:{record.packet_ordinal}']=data[p.ip_header_len+p.transport_header_len:p.ip_total_len]
        start=min(p.timestamp_ns for p in analysis.tcp_packets)
        for direction in [-1,1]:
            packets=[p for p in analysis.tcp_packets if p.direction==direction]
            origins={byid[p.packet_event_id].seq_start_unwrapped+1 for p in packets if p.flags&2}
            origin=next(iter(origins)) if len(origins)==1 else None
            fragments=[]
            for p in packets:
                segment=byid[p.packet_event_id];offset=segment.seq_start_unwrapped+int(bool(p.flags&2))
                if p.flags&7:
                    terms.append({**meta,'direction':direction,'relative_time_ns':p.timestamp_ns-start,'packet_ordinal':p.packet_ordinal,
                        'syn':bool(p.flags&2),'fin':bool(p.flags&1),'rst':bool(p.flags&4),'payload_len':p.payload_len,
                        'relative_sequence_offset':offset-origin if origin is not None else None})
                if p.payload_len:
                    data=payloads[p.packet_event_id];assert len(data)==p.payload_len
                    fragments.append((offset,data,p.timestamp_ns-start,p.packet_ordinal))
            body,mapping,unique,remaining,status=reassemble(fragments,origin)
            old=ledger[(ledger.session_id==sid)&(ledger.connection_id==cid)&(ledger.side==side)&(ledger.direction==direction)].iloc[0]
            if origin is not None and status!='overlap_conflict':assert unique==old.unique_payload_bytes
            maps.extend({**meta,'direction':direction,**m} for m in mapping)
            if r['protocol']=='VLESS':
                records,reason=tls_prefix(body,mapping,1 if direction==1 else 2)
            else:records,reason=[],'SS_control_no_cipher_record_parser'
            established=any(x['hello_established'] for x in records)
            if records and not established:records=[];reason='initial_hello_not_completed'
            recs.extend({**meta,'direction':direction,**x} for x in records)
            level='E1' if established else ('EX' if status!='contiguous' else 'E0')
            evidence.append({**meta,'direction':direction,'evidence_level':level,'reassembly_status':status,'parse_status':reason,
                'observed_unique_bytes':int(old.unique_payload_bytes),'contiguous_prefix_bytes':len(body),'unparsed_unique_bytes':int(old.unique_payload_bytes)-(records[-1]['end'] if records else 0),
                'record_syntax_bytes':records[-1]['end'] if records else 0,'records':len(records),'phase_boundary':None,'phase_permission':'unavailable'})
            if reason!='syntax_prefix_complete':failures.append({**meta,'direction':direction,'reason':reason,'reassembly_status':status})
        if (i+1)%10==0:print('E7 parsed sides',i+1,'/',len(manifest),flush=True)
    save('record-observations',recs);save('termination-events',terms);save('phase-evidence',evidence);save('parse-failures',failures);save('record-source-map',maps)
    js('post-only-permission-audit.json',{'phase_rule_permission':'unavailable','record_parser_uses_pre':False,
        'same_side_only':True,'normalization_exported':False,'no_test_pre_cutpoint':True,'E9':'not_executed_no_E2','E10':'unavailable_rule_interface_checked'})
    js('parse-audit.json',{'files_decoded':len(manifest),'unique_input_file_bytes':budget['bytes'],'payload_passes_per_file':2,
        'no_payload_persisted':True,'source_maps_are_offsets_and_times_only':True,'E2_rows':sum(x['evidence_level']=='E2' for x in evidence)})
    print('E7-E8 complete; no independently established semantic phase boundary',flush=True)
