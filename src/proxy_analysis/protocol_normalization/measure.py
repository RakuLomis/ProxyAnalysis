"""Run stack-independent N3-N6/N10. Do not enable unknown protocol adapters."""
import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
import json
from pathlib import Path
import time

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from .common import ROOT, OUT, digest, read, save
from .tcp_ledger import analyze_descriptor
from ..indexing.pairs import build_exclusive_pairs
from ..reproducibility.preflight import write_json

VERSION = 3


def one(row):
    sid = row['session_id']
    checkpoint = OUT/'sessions'/(sid+'.json')
    if checkpoint.exists():
        old = read(checkpoint)
        if old['version'] == VERSION:
            for p,h in old['sources'].items():
                if digest(p) != h:
                    raise ValueError('Frozen capture changed')
            return sid, len(old['errors']), 'cached'
    result = {'version': VERSION, 'session_id': sid, 'ledger': [], 'runs': [], 'captures': [],
              'excluded': [], 'errors': [], 'sources': {}}
    path = Path(row['session_path'])
    for rel in ['manifest.json', 'analysis/connection-index-v2.json', 'analysis/pcap-index-v1.json']:
        result['sources'][str(path/rel)] = digest(path/rel)
    if row['protocol'] == 'HYSTERIA2':
        result['excluded'].append({'reason': 'shared_udp_carrier_not_exclusive_tcp_pair'})
        write_json(checkpoint, result)
        return sid, 0, 'not_applicable'
    pairs = build_exclusive_pairs(path, row['protocol'])
    counter = Counter((p.post.entity_id, str(p.post.capture_path)) for p in pairs)
    events = []
    for pair in pairs:
        if counter[(pair.post.entity_id, str(pair.post.capture_path))] != 1 or pair.pre.transport_protocol != 'tcp' or pair.post.transport_protocol != 'tcp':
            result['excluded'].append({'connection_id': pair.connection_id, 'reason': 'reused_outer_or_non_tcp'})
            continue
        for desc in [pair.pre, pair.post]:
            meta = {k: row[k] for k in ['batch','item_id','session_id','protocol','repetition','main_route','label_id']}
            meta.update(connection_id=pair.connection_id, entity_id=desc.entity_id, side=desc.capture_side,
                        scope='exclusive_tcp_pair', epoch_id=f'{sid}:{desc.capture_side}:{desc.entity_id}:{desc.artifact_id}')
            try:
                rows, ev, runs, audit = analyze_descriptor(desc)
                result['sources'][str(desc.capture_path)] = digest(desc.capture_path)
                result['captures'].append({**meta, **audit, 'capture_path': str(desc.capture_path), 'sha256': result['sources'][str(desc.capture_path)]})
                for r in rows:
                    r['qualification_reasons'] = json.dumps(r['qualification_reasons'])
                    result['ledger'].append({**meta, **r})
                events.extend({**meta, **e} for e in ev)
                result['runs'].extend({**meta, **r} for r in runs)
            except Exception as exc:
                result['errors'].append({'connection_id': pair.connection_id, 'side': desc.capture_side, 'error': repr(exc)})
    if events:
        dest = OUT/'new-byte-events'/f'{sid}.parquet'
        dest.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(events).to_parquet(dest,index=False,compression='zstd')
        result['event_table'] = str(dest)
        result['event_sha256'] = digest(dest)
    else:
        result['event_table'] = None
    write_json(checkpoint, result)
    return sid, len(result['errors']), 'extracted'


def merge():
    reg = pd.read_parquet(OUT/'registry.parquet')
    ledgers,runs,captures,coverage,events_index = [],[],[],[],[]
    sources = {}
    writer = None
    for row in reg[reg.is_final].to_dict('records'):
        c = read(OUT/'sessions'/(row['session_id']+'.json'))
        assert c['version'] == VERSION
        ledgers.extend(c['ledger']); runs.extend(c['runs']); captures.extend(c['captures'])
        sources.update(c['sources'])
        coverage.append({**{k:row[k] for k in ['session_id','batch','item_id','protocol','repetition','main_route']},
                         'direction_rows':len(c['ledger']), 'capture_count':len(c['captures']),
                         'errors_json':json.dumps(c['errors']), 'error_count':len(c['errors']),
                         'excluded_json':json.dumps(c['excluded']),
                         'eligible_pair_count':len({r['connection_id'] for r in c['ledger']})})
        if c.get('event_table'):
            f=Path(c['event_table'])
            assert digest(f)==c['event_sha256']
            table=pq.read_table(f)
            if writer is None:
                writer=pq.ParquetWriter(OUT/'new-byte-events.parquet',table.schema,compression='zstd')
            writer.write_table(table)
            events_index.append({'session_id':row['session_id'],'rows':table.num_rows,'path':str(f),'sha256':c['event_sha256']})
    if writer is not None: writer.close()
    ledger=save('tcp-byte-ledger.parquet',ledgers)
    save('byte-direction-runs.parquet',runs)
    save('capture-audit.parquet',captures)
    save('coverage.parquet',coverage)
    save('new-byte-events-index.parquet',events_index)
    write_json(OUT/'measurement-source-hashes.json',sources)
    key=['session_id','connection_id','direction']
    a=ledger[ledger.side=='pre']; b=ledger[ledger.side=='post']
    joined=a.merge(b,on=key,suffixes=('_pre','_post'),validate='one_to_one')
    comparisons=[]
    for r in joined.to_dict('records'):
        common={k:r[k+'_pre'] for k in ['batch','item_id','protocol','repetition','main_route','label_id']}
        common.update({k:r[k] for k in key})
        valid=r['observed_unique_valid_pre'] and r['observed_unique_valid_post']
        closed=r['closed_contiguous_capture_candidate_pre'] and r['closed_contiguous_capture_candidate_post']
        for view,field in [('O','observed_payload_bytes'),('F','exclude_full_retransmission_bytes'),('U','unique_payload_bytes')]:
            pre,post=r[field+'_pre'],r[field+'_post']
            finite=pd.notna(pre) and pd.notna(post)
            comparisons.append({**common,'view':view,'pre':pre,'post':post,'common_unique_valid':valid,
                'closed_contiguous_both_sides':closed,'successful_relay_proven':False,
                'difference':post-pre if finite else None,'absolute_error':abs(post-pre) if finite else None,
                'log_ratio':float(np.log(post/pre)) if finite and pre>0 and post>0 else None,
                'relative_error':(post-pre)/pre if finite and pre>0 else None,
                'ratio_status':'positive' if finite and pre>0 and post>0 else 'missing' if not finite else 'zero_operand'})
    comparison=save('dedup-ablation.parquet',comparisons)
    # Paired diagnostics stay outside any future single-side feature export.
    run_df=pd.DataFrame(runs)
    aa=run_df[run_df.side=='pre'];bb=run_df[run_df.side=='post']
    rr=aa.merge(bb,on=['session_id','connection_id','threshold_bytes'],suffixes=('_pre','_post'),validate='one_to_one')
    run_compare=[]
    for r in rr.to_dict('records'):
        run_compare.append({**{k:r[k] for k in ['session_id','connection_id','threshold_bytes']},
            **{k:r[k+'_pre'] for k in ['batch','item_id','protocol','repetition','main_route']},
            'pre_runs':r['run_count_pre'],'post_runs':r['run_count_post'],
            'run_difference':r['run_count_post']-r['run_count_pre'],
            'pre_retained_fraction':r['retained_fraction_pre'],'post_retained_fraction':r['retained_fraction_post'],
            'pre_degenerate':r['run_count_pre']<=1,'post_degenerate':r['run_count_post']<=1})
    save('byte-run-comparison.parquet',run_compare)
    primary_path=ROOT/'outputs/content-generalization-20260916/business-01/primary-cohort.parquet'
    primary=pd.read_parquet(primary_path)
    cover=pd.DataFrame(coverage)
    assert len(primary)==240
    selection=primary[['session_id']].merge(cover,on='session_id',validate='one_to_one')
    assert len(selection)==240
    save('primary240-measurement-coverage.parquet',selection)
    write_json(OUT/'legacy-primary-cohort.json',{'source':str(primary_path),'sha256':digest(primary_path),
                                              'visits':240,'labels_unchanged':True,'model_fits':0})
    print('merged',len(ledger),'direction rows;',len(comparison),'pair contrasts',flush=True)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--workers',type=int,default=4)
    parser.add_argument('--limit',type=int)
    parser.add_argument('--merge-only',action='store_true')
    args=parser.parse_args()
    reg=pd.read_parquet(OUT/'registry.parquet')
    rows=reg[reg.is_final].to_dict('records')
    if args.limit: rows=rows[:args.limit]
    start=time.time()
    if not args.merge_only:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            futures=[pool.submit(one,r) for r in rows]
            errors=0
            for i,f in enumerate(as_completed(futures),1):
                sid,n,state=f.result();errors+=n
                if i%25==0 or n or i==len(rows):print(f'measure {i}/{len(rows)} {state} errors={errors} elapsed={time.time()-start:.1f}s',flush=True)
    if not args.limit: merge()


if __name__=='__main__':
    main()
