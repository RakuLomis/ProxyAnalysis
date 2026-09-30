"""Look for independent births of five SYN-unobserved carriers in bounded traces."""
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import sys
import json
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
from proxy_analysis.extend_calibration.audit import read,write,fs_path,path_identity,file_hash
BASE=ROOT/'outputs/extend-calibration-20260930/run-01';NEW=BASE/'extraction-03';OUT=NEW/'isolation-followup-01'


def scan(task):
    row,ids=task;sid=row['session_id'];base=(fs_path(ROOT/'Datasets/extend')/row['manifest_relative']).parent
    snap=read(base/'analysis/summary.json')['trace_snapshot']['traces'][0];tail=set(snap.get('causal_tail_event_seqs',[]))
    assert snap['barrier_verified']
    result=read(NEW/'sessions'/sid/'complete.json')
    assert file_hash(base/'raw/mihomo-trace.jsonl')==result['input_hashes']['raw/mihomo-trace.jsonl']
    rows=[]
    for line in (base/'raw/mihomo-trace.jsonl').open(encoding='utf-8'):
        if not any(c in line for c in ids):continue
        e=json.loads(line);seq=e.get('event_seq')
        if not isinstance(seq,int) or not (seq<=snap['cutoff_event_seq'] or seq in tail):continue
        if e.get('carrier_id') not in ids:continue
        rows.append({'source_session':sid,**{k:e.get(k) for k in ['carrier_id','type','ts','event_seq','adapter_instance_id','carrier_relation','logical_conn_id','conn_id']},
            'path_hash':path_identity(e.get('post_flow') or {})})
    return rows


def main():
    OUT.mkdir(exist_ok=True);assert not (OUT/'summary.json').exists()
    pool=pd.read_parquet(BASE/'extraction-01/metadata-qualified-pool.parquet');idx=pool.set_index('session_id')
    missing=pd.read_parquet(NEW/'isolation-01/tcp-paths-without-observed-SYN.parquet')
    targets=[];ids=set()
    for r in missing.to_dict('records'):
        base=(fs_path(ROOT/'Datasets/extend')/idx.loc[r['session_id'],'manifest_relative']).parent
        scope=read(NEW/'sessions'/r['session_id']/'scope.json')
        selected=set(scope['selected_logical_ids'])
        fs=[f for f in read(base/'analysis/flow-index.json')['items'] if f['conn_id'] in selected and any(path_identity(z)==r['path_hash'] for z in (f.get('carrier_binding') or {}).get('physical_paths',[]))]
        cids=sorted({f['carrier_binding']['carrier_id'] for f in fs});ids.update(cids)
        events=pd.read_parquet(NEW/'sessions'/r['session_id']/'post-W-events.parquet')
        positive=events[events.entity_id.isin(cids)]
        targets.append({**r,'protocol':idx.loc[r['session_id'],'protocol'],'carrier_ids':cids,
            'bindings':[{'mode':f['carrier_binding']['mode'],'relation':f['carrier_binding']['relation']} for f in fs],
            'positive_W_events':len(positive),'positive_W_bytes':int(positive.payload_bytes.sum())})
    evidence=[]
    with ProcessPoolExecutor(max_workers=4) as ex:
        for i,r in enumerate(ex.map(scan,[(r,ids) for r in pool.to_dict('records')]),1):
            evidence.extend(r)
            if i%100==0:print(f'Bounded carrier origin search {i}/600',flush=True)
    write(OUT/'targets.json',targets);write(OUT/'all-bounded-events.json',evidence)
    for t in targets:
        ev=[e for e in evidence if e['carrier_id'] in t['carrier_ids']]
        t['carrier_open_events']=[e for e in ev if e['type']=='carrier_open']
        t['created_dial_events']=[e for e in ev if e['type']=='tcp_proxy_dial' and e['carrier_relation']=='created']
        t['independent_origin_present']=bool(t['carrier_open_events'] or t['created_dial_events'])
    write(OUT/'origin-review.json',targets)
    write(OUT/'summary.json',{'cases':len(targets),'zero_positive_contribution':sum(t['positive_W_events']==0 for t in targets),
        'independent_origin_present':sum(t['independent_origin_present'] for t in targets),
        'unresolved_positive_cases':sum(t['positive_W_events']>0 and not t['independent_origin_present'] for t in targets),
        'training_allowed':False,'note':'origin present is not automatic release; review cross-session carrier scope before qualification'})


if __name__=='__main__':main()
