"""Independent exact-tuple TCP handshake checks of the nominal clock mapping."""
from pathlib import Path
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from decimal import Decimal
import sys
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
from proxy_analysis.extend_calibration.audit import read,write,fs_path,file_hash
from proxy_analysis.extend_calibration.forensic import endpoint
from proxy_analysis.parsing import PcapNgReader,decode_packet
BASE=ROOT/'outputs/extend-calibration-20260930/run-01';OUT=BASE/'extraction-03/clock-anchors-01'


def one(row):
    sid=row['session_id'];base=(fs_path(ROOT/'Datasets/extend')/row['manifest_relative']).parent
    netlog=read(base/'raw/netlog.json');types={v:k for k,v in netlog['constants']['logEventTypes'].items()}
    offset=Decimal(str(netlog['constants']['timeTickOffset']));starts={};intervals=[];tuples=set()
    for e in netlog['events']:
        if types[e['type']]!='TCP_CONNECT':continue
        source=e['source']['id'];params=e.get('params') or {}
        utc=int((Decimal(str(e['time']))+offset)*1_000_000)
        if e['phase']==1:starts[source]=utc
        elif e['phase']==2 and source in starts and not params.get('net_error') and params.get('local_address') and params.get('remote_address'):
            local,remote=endpoint(params['local_address']),endpoint(params['remote_address'])
            key=(*local,*remote);tuples.add(key)
            intervals.append((source,key,starts[source],utc))
    synack=defaultdict(list);syn=defaultdict(list)
    for rec in PcapNgReader(base/'raw/tun.pcap'):
        p=decode_packet(rec.link_type,rec.packet_data)
        if p.transport_protocol!='tcp' or not p.tcp_flags_raw&2:continue
        if p.tcp_flags_raw&16:
            key=(p.ip_dst,p.dst_port,p.ip_src,p.src_port)
            if key in tuples:synack[key].append(rec.timestamp_ns)
        else:
            key=(p.ip_src,p.src_port,p.ip_dst,p.dst_port)
            if key in tuples:syn[key].append(rec.timestamp_ns)
    # Fixed 2 ms descriptive quantization envelope, not fit to outcomes and not
    # an estimate/bound on arbitrary wall-clock drift. Keep exact residuals.
    tolerance=2_000_000;anchors=[]
    for source,key,start,end in intervals:
        observed=synack.get(key,[])
        in_range=[t for t in observed if start-tolerance<=t<=end+tolerance]
        before=[t for t in syn.get(key,[]) if start-tolerance<=t<=end+tolerance]
        anchors.append({'session_id':sid,'netlog_source':source,'begin_ns':start,'end_ns':end,
            'exact_tuple_synack_seen':bool(observed),'synack_candidates_in_interval':len(in_range),
            'client_syn_in_interval':bool(before),'check_passed':bool(in_range) and bool(before),
            'closest_synack_minus_end_ms':min(((t-end)/1e6 for t in observed),key=abs) if observed else None})
    write(OUT/'sessions'/f'{sid}.json',anchors)
    seen=[a for a in anchors if a['exact_tuple_synack_seen']]
    return {'session_id':sid,'protocol':row['protocol'],'offset_ms':str(offset),'successful_connects':len(anchors),
        'exact_tuple_observable':len(seen),'bracket_passed':sum(a['check_passed'] for a in seen),
        'bracket_failed':sum(not a['check_passed'] for a in seen),
        'netlog_sha256':file_hash(base/'raw/netlog.json'),'tun_sha256':file_hash(base/'raw/tun.pcap')}


def main():
    OUT.mkdir(exist_ok=True);assert not (OUT/'summary.json').exists()
    pool=pd.read_parquet(BASE/'extraction-01/metadata-qualified-pool.parquet')
    rows=[]
    with ProcessPoolExecutor(max_workers=4) as ex:
        for i,r in enumerate(ex.map(one,pool.to_dict('records')),1):
            rows.append(r)
            if i%100==0:print(f'Clock TCP anchors {i}/600',flush=True)
    f=pd.DataFrame(rows);f.to_parquet(OUT/'sessions.parquet',index=False)
    write(OUT/'summary.json',{'visits':len(rows),'with_observable_anchor':int(f.exact_tuple_observable.gt(0).sum()),
        'observable_connects':int(f.exact_tuple_observable.sum()),'bracket_passed':int(f.bracket_passed.sum()),
        'bracket_failed':int(f.bracket_failed.sum()),'visits_with_failed_brackets':int(f.bracket_failed.gt(0).sum()),
        'fixed_quantization_envelope_ms':2,'offset_not_fitted':True,'no_clock_drift_upper_bound_claim':True,
        'training_allowed':False,'code_sha256':file_hash(Path(__file__))})


if __name__=='__main__':main()
