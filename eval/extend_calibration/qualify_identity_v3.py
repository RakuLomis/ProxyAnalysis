"""Source-qualified carrier identity release, distinct from full SYN reconstruction."""
from pathlib import Path
import sys
import urllib.request
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
from proxy_analysis.extend_calibration.audit import read,write,fs_path,file_hash
BASE=ROOT/'outputs/extend-calibration-20260930/run-01';NEW=BASE/'extraction-03'
COMMIT='74cfed919c03f07a21b252328fe48b72c5361215'


def main():
    out=NEW/'identity-source-evidence';out.mkdir(exist_ok=True)
    assert not (out/'qualification.json').exists()
    paths=['adapter/outbound/anytls.go','transport/anytls/session/client.go','transport/anytls/session/stream.go',
           'common/traffictrace/context.go','common/traffictrace/flow.go']
    sources=[]
    for name in paths:
        url=f'https://raw.githubusercontent.com/RakuLomis/mihomo/{COMMIT}/{name}'
        path=out/(name.replace('/','__')+'.txt')
        if not path.exists():
            for attempt in range(3):
                try:path.write_bytes(urllib.request.urlopen(url,timeout=30).read());break
                except Exception:
                    if attempt==2:raise
        sources.append({'upstream_path':name,'url':url,'local_file':path.name,'sha256':file_hash(path)})
    code={r['upstream_path']:(out/r['local_file']).read_text(encoding='utf-8') for r in sources}
    assert 'return s.sess.seq' in code['transport/anytls/session/stream.go']
    assert 'session.seq = c.sessionCounter.Add(1)' in code['transport/anytls/session/client.go']
    assert 'observation = observation.Clone()' in code['adapter/outbound/anytls.go']
    assert 'observation.Relation = traffictrace.CarrierRelationReused' in code['adapter/outbound/anytls.go']
    assert 'observer.ObserveOuterFlow(observation.Clone())' in code['common/traffictrace/context.go']
    assert 'clone := o' in code['common/traffictrace/flow.go']
    pool=pd.read_parquet(BASE/'extraction-01/metadata-qualified-pool.parquet')
    pairs=0
    for row in pool.to_dict('records'):
        base=(fs_path(ROOT/'Datasets/extend')/row['manifest_relative']).parent
        assert read(base/'manifest.json')['component_versions']['mihomo']['commit']==COMMIT
        selected=set(read(NEW/'sessions'/row['session_id']/'scope.json')['selected_logical_ids'])
        for f in read(base/'analysis/flow-index.json')['items']:
            if f['conn_id'] not in selected:continue
            assert f['outer_conn_id']==f['carrier_binding']['carrier_id']
            pairs+=1
    isolation=read(NEW/'isolation-01/summary.json')
    assert all(isolation[k]==0 for k in ['overlapping_windows','cross_fold_registered_carriers','repeated_raw_file_hashes',
        'cross_fold_SYN_signatures','cross_fold_positive_IP_packet_hash_matches'])
    audit=read(NEW/'isolation-followup-01/origin-review.json')
    for r in audit:
        assert r['independent_origin_present'] or (r['protocol']=='anytls' and all(x['mode']=='shared' and x['relation']=='reused' for x in r['bindings']))
    write(out/'qualification.json',{'qualified_for_registered_entity_grouping':True,'manifest_builds_verified':len(pool),
        'selected_bindings_outer_id_equals_carrier_id':pairs,'source_commit':COMMIT,'sources':sources,
        'SYN_unobserved_cases':len(audit),'birth_timestamp_reconstructed':False,'complete_TCP_epoch_reconstruction_claimed':False,
        'basis':'verified stable physical-session identity + no cross-fold carrier/SYN/positive-packet reuse; no visit or carrier split',
        'boundary':'conditional on captured build and correct runtime instrumentation; not a proof against arbitrary unobserved implementation faults',
        'training_allowed':False})
    print({'qualified_for_registered_entity_grouping':True,'selected_bindings_verified':pairs})


if __name__=='__main__':main()
