"""HFC-W raw capture audit; standalone observed-window extraction, no training."""
import concurrent.futures
import hashlib
import json
import collections
from pathlib import Path
import sys
import time
import pandas as pd
from prepare import ROOT, OUT as PRIOR, read, write, sha, bounded_events
from proxy_analysis.parsing import PcapNgReader, decode_packet
from proxy_analysis.parsing.packet_decoder import _strip_link_header
from proxy_analysis.indexing.carrier_paths import carrier_paths

OUT=ROOT/'outputs/hy2-window-calibration-0916/run-01'
DOC=ROOT/'docs/hy2-window-calibration-0916'

def key(flow):
    names=('network','src_ip','src_port','dst_ip','dst_port')
    if any(flow.get(n) is None for n in names): raise ValueError('incomplete tuple')
    return tuple(flow[n] for n in names)

def reverse(k): return (k[0],k[3],k[4],k[1],k[2])

def add(mapping,k,value):
    mapping.setdefault(k,set()).add(value)

def summarize(events):
    values={'W_up':0,'W_down':0,'P_up':0,'P_down':0,'R_up':0,'R_down':0}
    last=None
    for _,_,direction,length in sorted(events):
        suffix='up' if direction==1 else 'down'
        values['W_'+suffix]+=length; values['P_'+suffix]+=1
        if direction!=last: values['R_'+suffix]+=1
        last=direction
    return values

def process(row):
    started=time.monotonic(); sid=row['session_id']; destination=OUT/'sessions'/sid
    destination.mkdir(parents=True,exist_ok=True)
    if (destination/'complete.json').exists(): return read(destination/'complete.json')
    p=Path(row['session_path']); manifest=read(p/'manifest.json')
    start=int(pd.Timestamp(manifest['started_at']).value); end=int(pd.Timestamp(manifest['completed_at']).value)
    assert end>start
    con=read(p/'analysis/connection-index-v2.json')['items']
    flows=read(p/'analysis/flow-index.json')['items']
    main={x.get('carrier_binding',{}).get('carrier_id') for x in con if x.get('egress',{}).get('outcome')=='proxy'}-{None}
    assert main
    paths=carrier_paths(p)
    selected=[f for f in flows if f.get('carrier_binding',{}).get('carrier_id') in main]
    pre={}; post={}; allpost={}; reasons=[]
    for f in selected:
        if f.get('egress_outcome')!='proxy': reasons.append('nonproxy_member_bound_to_main')
        k=key(f['pre_flow']); add(pre,k,(f['conn_id'],1)); add(pre,reverse(k),(f['conn_id'],-1))
    for cid,pairs in paths.items():
        for src,dst in pairs:
            k=('udp',src.ip,src.port,dst.ip,dst.port)
            for kk,di in [(k,1),(reverse(k),-1)]:
                add(allpost,kk,(cid,di))
                if cid in main:add(post,kk,(cid,di))
    if not post: reasons.append('no_post_paths')
    member_packets=collections.Counter(); raw_stats=[]; summaries=[]; cross=[]
    for side,name,mapping in [('pre','tun.pcap',pre),('post','phys.pcap',post)]:
        counters=collections.Counter(); events=[]; background=collections.Counter(); first=None; last=None
        fp=p/'raw'/name
        ip_pairs={(k[1],k[3]) for k in mapping}
        for rec in PcapNgReader(fp):
            counters['raw_packets']+=1
            if first is None: first=rec.timestamp_ns
            last=rec.timestamp_ns
            if not start<=rec.timestamp_ns<end:
                counters['outside_session_window']+=1; continue
            packet=decode_packet(rec.link_type,rec.packet_data)
            k=(packet.transport_protocol,packet.ip_src,packet.src_port,packet.ip_dst,packet.dst_port)
            if side=='post' and k in allpost:
                for cid,_ in allpost[k]: background[cid]+=1
            matches=mapping.get(k,set())
            fragmented=bool(packet.ip_fragment_offset or packet.ip_more_fragments)
            if not matches:
                counters['unselected_packets']+=1
                if fragmented and (packet.ip_src,packet.ip_dst) in ip_pairs:
                    counters['unmatched_scope_fragment']+=1
                continue
            counters['selected_packets']+=1
            for identifier,_ in matches: member_packets[(side,identifier)]+=1
            if len({v[1] for v in matches})!=1:
                counters['ambiguous_direction']+=1; continue
            if side=='post' and len({v[0] for v in matches})!=1:
                counters['ambiguous_carrier']+=1; continue
            if len(matches)>1:counters['tuple_multiple_members']+=1
            if fragmented:counters['selected_fragment']+=1; continue
            try: available=len(_strip_link_header(rec.link_type,rec.packet_data))
            except ValueError: available=0
            if rec.captured_len<rec.original_len or packet.ip_total_len is None or available<packet.ip_total_len:
                counters['selected_truncation']+=1; continue
            if packet.decode_status!='ok':
                counters['selected_decode_'+packet.decode_status]+=1; continue
            length=packet.transport_payload_len
            if length is None: counters['selected_unknown_length']+=1; continue
            if length>65527: counters['selected_oversize']+=1; continue
            if length>0: events.append((rec.timestamp_ns,rec.packet_ordinal,next(iter(matches))[1],length))
            else:counters['selected_zero_payload']+=1
        hard=['unmatched_scope_fragment','ambiguous_direction','ambiguous_carrier','selected_fragment',
              'selected_truncation','selected_unknown_length','selected_oversize']
        reasons.extend(side+':'+x for x in hard if counters[x])
        reasons.extend(side+':'+x for x in counters if x.startswith('selected_decode_'))
        if not events:reasons.append(side+':no_positive_events')
        ordered=sorted(events)
        counters['positive_events']=len(events)
        counters['timestamp_ties']=sum(a[0]==b[0] for a,b in zip(ordered,ordered[1:]))
        frame=pd.DataFrame(ordered,columns=['timestamp_ns','raw_packet_ordinal','direction','payload_bytes'])
        frame.to_parquet(destination/(side+'-events.parquet'),index=False,compression='zstd')
        summaries.append({'session_id':sid,'side':side,**summarize(events)})
        raw_stats.append({'side':side,'file_bytes':fp.stat().st_size,'sha256':sha(fp),
                          'first_packet_ns':first,'last_packet_ns':last,**counters})
        for cid,n in background.items(): cross.append({'session_id':sid,'carrier_id':cid,'packets':n,'selected_main':cid in main})
    missing=[f['conn_id'] for f in selected if not member_packets[('pre',f['conn_id'])]]
    # This is a review flag, not proof of dropped packets: some indexed attempts
    # can have no observed packet within this external window.
    if missing:reasons.append('members_without_window_packets')
    pd.DataFrame([{'conn_id':f['conn_id'],'packets':member_packets[('pre',f['conn_id'])]} for f in selected]).to_parquet(destination/'members.parquet',index=False)
    pd.DataFrame(cross).to_parquet(destination/'carrier-packets.parquet',index=False)
    result={'session_id':sid,'content_id':row['content_id'],'label_id':row['label_id'],'fold':int(row['fold']),
            'start_ns':start,'end_ns':end,'main_carriers':sorted(main),'members':len(selected),
            'members_without_packets':len(missing),'summaries':summaries,'raw_stats':raw_stats,
            'review_reasons':sorted(set(reasons)),'passed':not reasons,'seconds':time.monotonic()-started,
            'degraded_label_override':sid=='a293b581-ca2d-469f-acba-c55995635d40'}
    write(destination/'complete.json',result)
    return result

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    inputs=[Path(__file__),ROOT/'plan/hy2-window-observation-amendment-20260928.md',
            PRIOR/'candidate-visits.parquet',PRIOR/'qualification-review.json',
            ROOT/'src/proxy_analysis/parsing/packet_decoder.py',ROOT/'src/proxy_analysis/parsing/pcapng.py',
            ROOT/'src/proxy_analysis/indexing/carrier_paths.py']
    contract={'version':'HFC-W1','files':{str(p):sha(p) for p in inputs},'window':'manifest_utc_half_open',
              'override_session':'a293b581-ca2d-469f-acba-c55995635d40','models_trained':0}
    if (OUT/'contract.json').exists():assert read(OUT/'contract.json')==contract,'frozen contract changed'
    else:write(OUT/'contract.json',contract)
    visits=pd.read_parquet(PRIOR/'candidate-visits.parquet')
    results=[]
    with concurrent.futures.ProcessPoolExecutor(max_workers=4) as pool:
        for item in pool.map(process,visits.to_dict('records')):
            results.append(item)
            print('window audit',len(results),'/100',item['passed'],item['review_reasons'],flush=True)
            write(OUT/'progress.json',{'completed':len(results),'total':100,'models_trained':0})
    reasons=collections.Counter(x for r in results for x in r['review_reasons'])
    pd.DataFrame([s for r in results for s in r['summaries']]).to_parquet(OUT/'side-summaries.parquet',index=False)
    pd.DataFrame([{'session_id':r['session_id'],**s} for r in results for s in r['raw_stats']]).to_parquet(OUT/'capture-audit.parquet',index=False)
    allcross=pd.concat([pd.read_parquet(OUT/'sessions'/r['session_id']/'carrier-packets.parquet') for r in results],ignore_index=True)
    allcross.to_parquet(OUT/'carrier-window-packets.parquet',index=False)
    mains=allcross[allcross.selected_main]
    reused=mains.groupby('carrier_id').session_id.nunique().gt(1)
    gate={'visits':100,'passed_visits':sum(r['passed'] for r in results),'reasons':dict(reasons),
          'main_carrier_reused':int(reused.sum()),'background_carrier_rows':int((~allcross.selected_main).sum()),
          'gate_passed':not reasons and not reused.any(),'models_trained':0,
          'raw_bytes_scanned':sum(s['file_bytes'] for r in results for s in r['raw_stats'])}
    write(OUT/'window-gate.json',gate)
    DOC.mkdir(parents=True,exist_ok=True)
    (DOC/'measurement-audit.md').write_text('# HFC-W 原始包窗口审核\n\n'+
        '使用用户确认的窗口观测口径；未启动生成或训练。\n\n```json\n'+json.dumps(gate,ensure_ascii=False,indent=2)+'\n```\n',encoding='utf-8')
    print(json.dumps(gate),flush=True)

if __name__=='__main__':main()
