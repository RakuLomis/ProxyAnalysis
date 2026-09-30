"""Bounded TCP epoch / missing-member investigation. No inferred remapping."""
from collections import defaultdict, Counter
from decimal import Decimal
from pathlib import Path
import sys
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
from proxy_analysis.extend_calibration.audit import read,write,fs_path,path_identity,bounded_trace,file_hash
from proxy_analysis.extend_calibration.forensic import flow_tuple
from proxy_analysis.extend_calibration.extraction import reverse
from proxy_analysis.parsing import PcapNgReader,decode_packet

BASE=ROOT/'outputs/extend-calibration-20260930/run-01'
OLD=BASE/'extraction-01';NEW=BASE/'extraction-02';OUT=NEW/'epoch-capture-audit-01'


def main():
    OUT.mkdir(exist_ok=True)
    assert not (OUT/'summary.json').exists()
    pool=pd.read_parquet(OLD/'metadata-qualified-pool.parquet').set_index('session_id')
    old=pd.read_parquet(OLD/'full-coverage.parquet')
    chosen=old[old.review_reasons.str.contains('ambiguous|without_window')]
    epochs_out=[];missing_out=[];clock_out=[];candidate_out=[];inputs={}
    for i,row in enumerate(chosen.to_dict('records'),1):
        sid=row['session_id'];folder=OLD/'sessions'/sid
        result,scope=read(folder/'complete.json'),read(folder/'scope.json')
        base=(fs_path(ROOT/'Datasets/extend')/pool.loc[sid,'manifest_relative']).parent
        flows={f['conn_id']:f for f in read(base/'analysis/flow-index.json')['items'] if f['conn_id'] in scope['selected_logical_ids']}
        ev,ta=bounded_trace(base/'raw/mihomo-trace.jsonl',read(base/'analysis/summary.json'),set(scope['carriers']))
        assert ta['sha256']==result['input_hashes']['raw/mihomo-trace.jsonl']
        inputs[sid]={'trace_sha256':ta['sha256']}
        groups=defaultdict(set);tuples={}
        for f in flows.values():
            for path in f['carrier_binding'].get('physical_paths') or [f.get('post_flow') or {}]:
                h=path_identity(path);groups[h].add(f['carrier_binding']['carrier_id']);tuples[h]=flow_tuple(path)
        ambiguous={h:c for h,c in groups.items() if h and len(c)>1}
        relevant={k:(h,1) for h in ambiguous for k in [tuples[h]]}
        relevant.update({reverse(k):(h,-1) for k,(h,_) in list(relevant.items())})
        epoch_lists=defaultdict(list)
        aliases={}
        for ident in scope['missing_pre']:
            f=flows[ident]['pre_flow'];aliases[(f['src_ip'],f['src_port'])]=ident
        candidates=defaultdict(lambda:{'packets':0,'syn':0,'first_ns':None,'last_ns':None})
        for side,filename in [('pre','tun.pcap'),('post','phys.pcap')]:
            if side=='pre' and not aliases:continue
            if side=='post' and not ambiguous:continue
            assert file_hash(base/'raw'/filename)==result['input_hashes']['raw/'+filename]
            for rec in PcapNgReader(base/'raw'/filename):
                if not result['start_ns']<=rec.timestamp_ns<result['end_ns']:continue
                p=decode_packet(rec.link_type,rec.packet_data)
                k=(p.transport_protocol,p.ip_src,p.src_port,p.ip_dst,p.dst_port)
                if side=='pre':
                    ident=aliases.get((p.ip_src,p.src_port)) or aliases.get((p.ip_dst,p.dst_port))
                    if ident and p.transport_protocol=='tcp':
                        forward=(p.ip_src,p.src_port) in aliases
                        q=k if forward else reverse(k)
                        h=path_identity(dict(zip(['network','src_ip','src_port','dst_ip','dst_port'],q)))
                        v=candidates[(ident,h)];v['packets']+=1
                        v['syn']+=int(bool(p.tcp_flags_raw & 2) and not bool(p.tcp_flags_raw & 16))
                        v['first_ns']=rec.timestamp_ns if v['first_ns'] is None else min(v['first_ns'],rec.timestamp_ns)
                        v['last_ns']=rec.timestamp_ns if v['last_ns'] is None else max(v['last_ns'],rec.timestamp_ns)
                elif k in relevant and p.transport_protocol=='tcp':
                    h,d=relevant[k];seq=epoch_lists[h]
                    syn=d==1 and bool(p.tcp_flags_raw & 2) and not bool(p.tcp_flags_raw & 16)
                    new=syn and (not seq or seq[-1]['initial_seq']!=p.tcp_seq or seq[-1]['closed'])
                    if not seq or new:
                        seq.append({'first_ns':rec.timestamp_ns,'last_ns':rec.timestamp_ns,'first_ordinal':rec.packet_ordinal,
                            'last_ordinal':rec.packet_ordinal,'initial_seq':p.tcp_seq if syn else None,
                            'starts_with_syn':syn,'packets':0,'rst_packets':0,'closed':False,'fin_directions':set()})
                    e=seq[-1];e['last_ns']=rec.timestamp_ns;e['last_ordinal']=rec.packet_ordinal;e['packets']+=1
                    if p.tcp_flags_raw & 4:e['rst_packets']+=1;e['closed']=True
                    if p.tcp_flags_raw & 1:e['fin_directions'].add(d)
                    if len(e['fin_directions'])==2:e['closed']=True
        for h,cids in ambiguous.items():
            # A containment result is evidence to inspect, NOT permission to
            # assign delayed packets by time alone.
            binds={c:[int(pd.Timestamp(e['ts']).value) for e in ev if e['carrier_id']==c and e['event_type']=='logical_carrier_bind'] for c in cids}
            for n,e in enumerate(epoch_lists[h]):
                e['fin_directions']=sorted(e['fin_directions'])
                e['binds_inside_observed_span']=[c for c,ts in binds.items() if any(e['first_ns']<=t<=e['last_ns'] for t in ts)]
                epochs_out.append({'session_id':sid,'path_hash':h,'epoch_index':n,**e})
            missing_out.append({'session_id':sid,'kind':'ambiguous_path','path_hash':h,'registered_carriers':len(cids),
                'observed_syn_epochs':sum(e['starts_with_syn'] for e in epoch_lists[h]),'binds':binds})
        for (ident,h),v in candidates.items():
            candidate_out.append({'session_id':sid,'logical_id':ident,'observed_path_hash':h,**v,
                'registered_path_hash':path_identity(flows[ident]['pre_flow']), 'remapped':False})
        if scope['missing_pre'] or scope['missing_post']:
            context=read(base/'raw/capture-context.json');netlog=read(base/'raw/netlog.json')
            inputs[sid].update({k:file_hash(base/'raw'/k) for k in ['capture-context.json','netlog.json']})
            coverage=context['packet_coverage'];offset=Decimal(str(netlog['constants']['timeTickOffset']))*1_000_000
            stops={side:int(Decimal(str(coverage['stopped'][key]))*1_000_000_000+offset) for side,key in [('pre','tun'),('post','physical')]}
            ready={side:int(Decimal(str(coverage['ready'][key]))*1_000_000_000+offset) for side,key in [('pre','tun'),('post','physical')]}
            for cap in result['capture_audit']:
                side=cap['side']
                clock_out.append({'session_id':sid,'side':side,'mapped_ready_ns':ready[side],'mapped_stop_ns':stops[side],
                    'first_packet_minus_ready_ms':(cap['first_packet_ns']-ready[side])/1e6,
                    'stop_minus_last_packet_ms':(stops[side]-cap['last_packet_ns'])/1e6,
                    'mapping_status':'candidate OS monotonic mapping via NetLog offset; capture-clock identity not independently established'})
            for side,ids in [('pre',scope['missing_pre']),('post',scope['missing_post'])]:
                for ident in ids:
                    cids={flows[ident]['carrier_binding']['carrier_id']} if side=='pre' else {ident}
                    # Bind events for a shared carrier must also match the logical member.
                    matches=[e for e in ev if e['carrier_id'] in cids and e['event_type']=='logical_carrier_bind'
                             and (side=='post' or e.get('logical_conn_id')==ident)]
                    times=[int(pd.Timestamp(e['ts']).value) for e in matches]
                    missing_out.append({'session_id':sid,'protocol':row['protocol'],'kind':'missing_member','side':side,'identifier':ident,
                        'exact_member_bind_count':len(times),'bind_minus_mapped_stop_ms':[(t-stops[side])/1e6 for t in times],
                        'accepted_as_out_of_capture':False})
        print(f'Epoch/capture evidence {i}/{len(chosen)}',flush=True)
    write(OUT/'epochs.json',epochs_out);write(OUT/'missing-and-binding.json',missing_out)
    write(OUT/'clock-candidates.json',clock_out);write(OUT/'same-endpoint-candidates.json',candidate_out)
    write(OUT/'source-hashes.json',inputs)
    write(OUT/'summary.json',{'sessions':len(chosen),'epochs':len(epochs_out),'path_groups':sum(x['kind']=='ambiguous_path' for x in missing_out),
        'missing_member_rows':sum(x['kind']=='missing_member' for x in missing_out),'same_endpoint_candidate_rows':len(candidate_out),
        'epoch_attribution_released':False,'capture_boundary_exception_released':False,'training_allowed':False})


if __name__=='__main__':main()
