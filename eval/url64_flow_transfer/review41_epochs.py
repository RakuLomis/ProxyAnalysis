"""Describe exceptional tuple timelines without assigning ambiguous packets."""
from collections import defaultdict
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
import pandas as pd
from proxy_analysis.extend_calibration.audit import read, write, fs_path, path_identity, file_hash
from proxy_analysis.extend_calibration.forensic import flow_tuple
from proxy_analysis.extend_calibration.extraction_v3 import reverse
from proxy_analysis.parsing import PcapNgReader, decode_packet
from proxy_analysis.extend_calibration.common_window import bounded_lifecycles, outside_reason

BASE = ROOT / 'outputs/url64-flow-transfer-extend/run-01/approved41-01'


def main():
    out = BASE / 'epoch-review-01'; assert not (out / 'summary.json').exists()
    paths = pd.read_parquet(BASE / 'raw-audit-01/path-evidence.parquet')
    affected = paths[paths.positive_packets.gt(0) & (paths.syn_count.ne(1) | paths.entity_ids.map(len).gt(1))]
    result = []
    for sid, group in affected.groupby('session_id'):
        scope = read(BASE / 'private-audit' / f'{sid}.json')
        raw_audit = read(BASE / 'raw-audit-01/sessions' / f'{sid}.json')
        base = (fs_path(ROOT / 'Datasets/extend') / scope['manifest_relative']).parent
        a,b = scope['window']['start_ns'], scope['window']['end_ns']
        flows = read(base/'analysis/flow-index.json')['items']
        life = bounded_lifecycles(base, read(base/'analysis/summary.json'))
        for side, sub in group.groupby('side'):
            selected = set(sub.path_hash); mapping = {}
            for ident, values in scope[side+'_index'].items():
                for path in values:
                    h = path_identity(path)
                    if h in selected:
                        k = flow_tuple(path); mapping[k]=(h,1); mapping[reverse(k)]=(h,-1)
            filename = 'raw/tun.pcap' if side == 'pre' else 'raw/phys.pcap'
            assert file_hash(base/filename) == raw_audit['raw_hashes'][filename]
            events = defaultdict(list)
            for rec in PcapNgReader(base/filename):
                p=decode_packet(rec.link_type,rec.packet_data)
                k=(p.transport_protocol,p.ip_src,p.src_port,p.ip_dst,p.dst_port)
                if k not in mapping: continue
                h,d=mapping[k];flags=p.tcp_flags_raw or 0
                if flags&2 or flags&5 or (p.transport_payload_len or 0)>0:
                    events[h].append({'relative_ns':rec.timestamp_ns-a,'ordinal':rec.packet_ordinal,
                                      'direction':d,'flags':flags,'seq':p.tcp_seq,
                                      'bytes':p.transport_payload_len or 0,'in_window':a<=rec.timestamp_ns<b})
            for row in sub.to_dict('records'):
                h=row['path_hash'];ev=events[h];states=[]
                for f in flows:
                    ident=f.get('conn_id') if side=='pre' else (f.get('carrier_binding') or {}).get('carrier_id')
                    if ident not in row['entity_ids']: continue
                    le=life.get(f.get('conn_id'),[])
                    states.append({'entity':ident,'logical_id':f.get('conn_id'),
                                   'logical_outside_reason':outside_reason(le,a,b),
                                   'logical_events':le})
                syn=[e for e in ev if e['direction']==1 and e['flags']&2 and not e['flags']&16]
                result.append({'session_id':sid,'protocol':scope['protocol'],'side':side,'path_hash':h,
                               'entity_ids':row['entity_ids'].tolist(), 'full_capture_syn_count':row['syn_count'],
                               'in_window_syn_sequences':len({e['seq'] for e in syn if e['in_window']}),
                               'syn_after_window':sum(e['relative_ns']>=b-a for e in syn),
                               'logical_states':states,'events':ev,
                               'post_only_epoch_attribution_released':False})
        print(f"Reviewed {sid}",flush=True)
    write(out/'timelines.json',result)
    summary={'visits':int(affected.session_id.nunique()),'path_rows':len(result),
             'multi_syn_all_outside_second_candidate':sum(r['full_capture_syn_count']>1 and r['in_window_syn_sequences']==1 and r['syn_after_window']>0 for r in result),
             'multi_syn_in_window':sum(r['in_window_syn_sequences']>1 for r in result),
             'no_syn_entire_capture':sum(r['full_capture_syn_count']==0 for r in result),
             'no_side_selection_changed':True,'training_allowed':False,
             'logical_lifecycle_not_used_as_test_post_selector':True,'code_sha256':file_hash(Path(__file__))}
    write(out/'summary.json',summary);print(summary)


if __name__=='__main__':main()
