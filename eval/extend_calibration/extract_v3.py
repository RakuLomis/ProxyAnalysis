"""Recompute ALL visits in the approved common stable interval, no inheritance."""
from concurrent.futures import ProcessPoolExecutor
from collections import Counter
from pathlib import Path
import argparse
import sys
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
from proxy_analysis.extend_calibration.audit import read,write,file_hash
from proxy_analysis.extend_calibration.extraction_v3 import extract_one
BASE=ROOT/'outputs/extend-calibration-20260930/run-01';OUT=BASE/'extraction-03'


def main():
    p=argparse.ArgumentParser();p.add_argument('--pilot',action='store_true');p.add_argument('--workers',type=int,default=4)
    args=p.parse_args()
    windows={r['session_id']:r for r in read(OUT/'prepared-windows.json')}
    pool=pd.read_parquet(BASE/'extraction-01/metadata-qualified-pool.parquet')
    assert len(windows)==len(pool)==600
    paths=[Path(__file__),ROOT/'src/proxy_analysis/extend_calibration/extraction_v3.py',
        ROOT/'src/proxy_analysis/extend_calibration/reassembly.py',ROOT/'src/proxy_analysis/extend_calibration/common_window.py',
        OUT/'prepared-windows.json',OUT/'clock-source-evidence/manifest.json']
    contract={'version':'extend-WT-3','source_hashes':{str(f.relative_to(ROOT)):file_hash(f) for f in paths},
        'window':'[max(tun_ready,physical_ready), browser_quiescent); mapped by per-session NetLog offset',
        'stopped_semantics':'after process exit, so not used as live-capture end',
        'scope':'uniform 600 visits; only exact unique connect/close lifecycle excludes outside members',
        'source_verified_clock':True,'wall_clock_nanosecond_precision_claimed':False,
        'training_allowed':False,'no_visit_dropped':True}
    if (OUT/'contract.json').exists():assert read(OUT/'contract.json')==contract
    else:write(OUT/'contract.json',contract)
    rows=pool.to_dict('records')
    if args.pilot:
        ids={'23e6e967-e6f6-48d9-af08-b3b7f41d4613','043f4840-7889-40ac-9ff0-1bf4de337599','42b913b9-4790-4b68-811e-d2496d66b63f'}
        ids |= set(pool.groupby('protocol').head(1).session_id)
        rows=[r for r in rows if r['session_id'] in ids]
    tasks=[(dict(r,common_window=windows[r['session_id']]),str(ROOT/'Datasets/extend'),str(OUT)) for r in rows]
    results=[]
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        for i,r in enumerate(ex.map(extract_one,tasks),1):
            results.append(r)
            print(f'{i}/{len(rows)} {r["protocol"]} W={r["W_gate_passed"]} {r["review_reasons"]}',flush=True)
            write(OUT/'progress.json',{'completed':i,'total':len(rows),'pilot':args.pilot,'training_performed':False})
    tag='pilot' if args.pilot else 'full'
    for track in ['W','T']:
        pd.DataFrame([v for r in results for v in r[track]]).to_parquet(OUT/f'{tag}-{track}-features.parquet',index=False)
    fields=['session_id','protocol','W_gate_passed','T_candidate_pairs','T_common_pairs','missing_pre','missing_post','lifecycle_excluded_members']
    pd.DataFrame([{k:r[k] for k in fields}|{'review_reasons':r['review_reasons']} for r in results]).to_parquet(OUT/f'{tag}-coverage.parquet',index=False)
    write(OUT/f'{tag}-gate.json',{'visits':len(results),'W_passed':sum(r['W_gate_passed'] for r in results),
        'reasons':dict(Counter(v for r in results for v in r['review_reasons'])),
        'training_allowed':False,'full_epoch_isolation_passed':False})


if __name__=='__main__':main()
