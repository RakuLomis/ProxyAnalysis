"""Content/carrier/raw-source audit plus TCP SYN and positive-packet fingerprints."""
from pathlib import Path
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
import hashlib
import sys
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
from proxy_analysis.extend_calibration.audit import read,write,fs_path,path_identity
from proxy_analysis.extend_calibration.forensic import flow_tuple
from proxy_analysis.extend_calibration.extraction import reverse
from proxy_analysis.parsing import PcapNgReader,decode_packet
from proxy_analysis.parsing.packet_decoder import _strip_link_header
BASE=ROOT/'outputs/extend-calibration-20260930/run-01';NEW=BASE/'extraction-03';OUT=NEW/'isolation-01'


def scan(task):
    row,reused=task;sid=row['session_id'];folder=NEW/'sessions'/sid
    scope=read(folder/'scope.json');result=read(folder/'complete.json')
    base=(fs_path(ROOT/'Datasets/extend')/row['manifest_relative']).parent
    flows=[f for f in read(base/'analysis/flow-index.json')['items'] if f['conn_id'] in set(scope['selected_logical_ids'])]
    evidence=[];packet_hashes=set();coverage=[]
    for side,filename in [('pre','tun.pcap'),('post','phys.pcap')]:
        mapping={}
        for f in flows:
            paths=[f['pre_flow']] if side=='pre' else f['carrier_binding'].get('physical_paths') or [f['post_flow']]
            for path in paths:
                h=path_identity(path)
                if h not in reused:continue
                k=flow_tuple(path);mapping[k]=(h,1);mapping[reverse(k)]=(h,-1)
        if not mapping:continue
        found=defaultdict(lambda:{'tcp_packets_in_window':0,'udp_packets_in_window':0,'client_syn_sequences':set()})
        for rec in PcapNgReader(base/'raw'/filename):
            p=decode_packet(rec.link_type,rec.packet_data)
            key=(p.transport_protocol,p.ip_src,p.src_port,p.ip_dst,p.dst_port)
            if key not in mapping:continue
            h,d=mapping[key];v=found[h]
            # Include SYN before the common start if present in this raw capture;
            # the signature is audit context, never a feature.
            if p.transport_protocol=='tcp' and d==1 and p.tcp_flags_raw&2 and not p.tcp_flags_raw&16:
                v['client_syn_sequences'].add(p.tcp_seq)
            if result['start_ns']<=rec.timestamp_ns<result['end_ns']:
                v[p.transport_protocol+'_packets_in_window']+=1
                if (p.transport_payload_len or 0)>0 and p.decode_status=='ok' and not(p.ip_fragment_offset or p.ip_more_fragments):
                    ip=_strip_link_header(rec.link_type,rec.packet_data)
                    if len(ip)>=p.ip_total_len:packet_hashes.add(hashlib.sha256(ip[:p.ip_total_len]).digest())
        for h,v in found.items():
            seqs=v.pop('client_syn_sequences')
            coverage.append({'session_id':sid,'side':side,'path_hash':h,**v,'syn_count':len(seqs)})
            for seq in seqs:
                evidence.append({'session_id':sid,'side':side,'path_hash':h,
                    'syn_signature':hashlib.sha256((h+':'+str(seq)).encode()).hexdigest()})
    pd.DataFrame({'packet_hash':list(packet_hashes)}).to_parquet(OUT/'packets'/f'{sid}.parquet',index=False)
    write(OUT/'sessions'/f'{sid}.json',{'syn':evidence,'coverage':coverage})
    return {'session_id':sid,'syn':evidence,'coverage':coverage,'packet_fingerprints':len(packet_hashes)}


def main():
    OUT.mkdir(exist_ok=True);(OUT/'packets').mkdir(exist_ok=True)
    assert not (OUT/'summary.json').exists()
    pool=pd.read_parquet(BASE/'extraction-01/metadata-qualified-pool.parquet')
    members=pd.read_parquet(BASE/'extraction-01/verification-01/candidate-fold-members.parquet').set_index('session_id')
    reg=defaultdict(set);carriers=defaultdict(set);raw=defaultdict(set);windows=[]
    for r in pool.to_dict('records'):
        sid=r['session_id'];folder=NEW/'sessions'/sid;s=read(folder/'scope.json');v=read(folder/'complete.json')
        for h in s['pre_path_hashes']+s['post_path_hashes']:reg[h].add(sid)
        for c in s['carriers']:carriers[c].add(sid)
        for k in ['raw/tun.pcap','raw/phys.pcap']:raw[v['input_hashes'][k]].add(sid)
        windows.append((v['start_ns'],v['end_ns'],sid))
    reused={h for h,ids in reg.items() if members.loc[sorted(ids),'fold'].nunique()>1}
    syn=[];coverage=[];counts=[]
    with ProcessPoolExecutor(max_workers=4) as ex:
        for i,r in enumerate(ex.map(scan,[(r,reused) for r in pool.to_dict('records')]),1):
            syn.extend(r['syn']);coverage.extend(r['coverage']);counts.append(r['packet_fingerprints'])
            if i%100==0:print(f'Isolation raw evidence {i}/600',flush=True)
    sf=pd.DataFrame(syn);cf=pd.DataFrame(coverage)
    sf=sf.merge(members.reset_index()[['session_id','fold','content_id']],on='session_id',validate='many_to_one')
    collisions=sf.groupby('syn_signature').fold.nunique();bad_sig=set(collisions[collisions>1].index)
    sf[sf.syn_signature.isin(bad_sig)].to_parquet(OUT/'cross-fold-SYN-collisions.parquet',index=False)
    cf.to_parquet(OUT/'reused-path-coverage.parquet',index=False)
    # Hashes are protocol bytes, never learning features. Empty ACK templates and
    # non-first fragments are outside this packet-content check, explicitly.
    owner={};duplicates=[]
    for r in pool.to_dict('records'):
        sid=r['session_id'];fold=int(members.loc[sid,'fold'])
        for h in pd.read_parquet(OUT/'packets'/f'{sid}.parquet').packet_hash:
            if h in owner and owner[h][1]!=fold:
                duplicates.append({'session_a':owner[h][0],'session_b':sid,'sha256':h.hex()})
            else:owner.setdefault(h,(sid,fold))
    write(OUT/'cross-fold-packet-collisions.json',duplicates)
    overlap=[];ordered=sorted(windows)
    for i,(start,end,sid) in enumerate(ordered):
        for st,en,other in ordered[i+1:]:
            if st>=end:break
            overlap.append([sid,other])
    write(OUT/'window-overlaps.json',overlap)
    carrier_cross=[c for c,ids in carriers.items() if members.loc[sorted(ids),'fold'].nunique()>1]
    unknown=cf[cf.tcp_packets_in_window.gt(0)&cf.syn_count.eq(0)]
    unknown.to_parquet(OUT/'tcp-paths-without-observed-SYN.parquet',index=False)
    summary={'visits':600,'cross_fold_reused_path_hashes':len(reused),'overlapping_windows':len(overlap),
        'cross_fold_registered_carriers':len(carrier_cross),'repeated_raw_file_hashes':sum(len(v)>1 for v in raw.values()),
        'cross_fold_SYN_signatures':len(bad_sig),'cross_fold_positive_IP_packet_hash_matches':len(duplicates),
        'audited_positive_packet_fingerprints':sum(counts),'tcp_path_side_rows_without_SYN':len(unknown),
        'no_random_flow_split':True,'training_allowed':False,
        'limitation':'checks registered carriers, SYN signatures and complete positive IP packets on cross-fold reused paths; not a universal connection identity proof',
        'passed_without_unresolved_TCP_epochs':not(overlap or carrier_cross or bad_sig or duplicates or len(unknown))}
    write(OUT/'summary.json',summary);print(summary,flush=True)


if __name__=='__main__':main()
