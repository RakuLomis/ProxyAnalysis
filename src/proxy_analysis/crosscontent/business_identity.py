"""Packet-level audit of cross-session TCP tuple reuse before business training."""
from collections import defaultdict
import hashlib
from itertools import combinations
import json
from pathlib import Path

from ..paired_information.prepare import table, digest
from ..parsing import PcapNgReader
from ..reproducibility.preflight import write_json, write_table
from .business_features import load_config, verify


def main():
    cfg=load_config(); verify(cfg); root=Path(cfg['output_root'])
    rows=table(root/'capture-files.parquet')
    audit={r['path']:r for r in table(root/'capture-audit.parquet')}
    extraction=json.loads((root/'extraction-gate.json').read_text(encoding='utf-8'))
    if not extraction['primary_passed']: raise ValueError('Primary extraction not passed')
    grouped=defaultdict(list)
    for r in rows: grouped[r['tuple_key']].append(r)
    packet_cache={}; comparisons=[]
    def packet_ids(path):
        if path not in packet_cache:
            packet_cache[path]={(r.timestamp_ns,hashlib.sha256(r.packet_data).hexdigest()) for r in PcapNgReader(Path(path))}
        return packet_cache[path]
    for group in grouped.values():
        for a,b in combinations(group,2):
            if a['session_id']==b['session_id']: continue
            aa,bb=audit[a['path']],audit[b['path']]
            overlap=max(aa['first_ns'],bb['first_ns'])<=min(aa['last_ns'],bb['last_ns'])
            packets=packet_ids(a['path'])&packet_ids(b['path'])
            syna={(s['direction'],s['seq']) for s in json.loads(aa['initial_syn_json'])}
            synb={(s['direction'],s['seq']) for s in json.loads(bb['initial_syn_json'])}
            comparisons.append({'session_a':a['session_id'],'session_b':b['session_id'],
                'different_content':a['content_id']!=b['content_id'],'time_overlap':overlap,
                'identical_packets':len(packets),'shared_initial_syn_identity':len(syna&synb),
                'both_have_initial_syn':bool(syna and synb)})
    write_json(root/'tuple-reuse-comparisons.json',comparisons)
    passed=not any(r['time_overlap'] or r['identical_packets'] or r['shared_initial_syn_identity'] for r in comparisons)
    result={'passed':passed,'candidate_sessions':extraction['completed_sessions'],
        'primary_sessions':extraction['actual_primary'],'capture_records':len(rows),
        'tuple_reuse_comparisons':len(comparisons),'time_overlaps':sum(r['time_overlap'] for r in comparisons),
        'identical_packets':sum(r['identical_packets'] for r in comparisons),
        'shared_initial_syn_identities':sum(r['shared_initial_syn_identity'] for r in comparisons),
        'scope':'six_business_300_SS_VLESS_only_not_all_dataset',
        'source_hashes':{name:digest(root/name) for name in ['capture-files.parquet','capture-audit.parquet','side-summaries.parquet']}}
    write_json(root/'identity-gate.json',result); print(json.dumps(result),flush=True)
    if not passed: raise ValueError('Connection identity ambiguity requires review')


if __name__=='__main__': main()
