"""Versioned approved transport-datagram/union extraction; training stays gated."""
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
from collections import Counter
import argparse
import shutil
import sys
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
from proxy_analysis.extend_calibration.audit import read,write,file_hash
from proxy_analysis.extend_calibration.extraction import extract_one as verify_original
from proxy_analysis.extend_calibration.extraction_v2 import extract_one

BASE=ROOT/'outputs/extend-calibration-20260930/run-01'
OLD=BASE/'extraction-01'
OUT=BASE/'extraction-02'


def task(row):
    args=(row,str(ROOT/'Datasets/extend'),str(OUT))
    # v1 already verified absence of selected/scope fragments and tuple ambiguity
    # for passing visits. Their event representation is unchanged by this rule.
    if row['old_W_passed']:
        original=verify_original((row,args[1],str(OLD)))  # verifies every raw input hash
        dest=OUT/'sessions'/row['session_id']
        if not dest.exists():
            shutil.copytree(OLD/'sessions'/row['session_id'],dest)
            write(dest/'inheritance.json',{'source':'extraction-01','reason':'no selected fragments or ambiguous tuple; v2 numeric units unchanged',
                'source_complete_sha256':file_hash(OLD/'sessions'/row['session_id']/'complete.json'),
                'raw_inputs_rehashed':True,'training_allowed':False})
        assert read(dest/'complete.json')==original
        return original
    return extract_one(args)


def main():
    p=argparse.ArgumentParser();p.add_argument('--pilot',action='store_true');p.add_argument('--workers',type=int,default=4)
    args=p.parse_args();OUT.mkdir(exist_ok=True)
    pool=pd.read_parquet(OLD/'metadata-qualified-pool.parquet')
    cv=pd.read_parquet(OLD/'full-coverage.parquet').rename(columns={'W_gate_passed':'old_W_passed'})
    pool=pool.merge(cv[['session_id','old_W_passed','review_reasons']],on='session_id',validate='one_to_one')
    files=[Path(__file__),ROOT/'src/proxy_analysis/extend_calibration/extraction_v2.py',
        ROOT/'src/proxy_analysis/extend_calibration/reassembly.py',OLD/'contract.json',OLD/'full-coverage.parquet']
    contract={'version':'extend-WT-2','approved':True,'training_allowed':False,'sessions':sorted(pool.session_id),
        'source_hashes':{str(f.relative_to(ROOT)):file_hash(f) for f in files},
        'window':'unchanged manifest UTC half-open','IPv4':'complete only, consistent overlap, explicit first fragment then complete epoch, no cross-window state',
        'IPv6_fragments':'unsupported hold','W_unit':'one complete transport datagram, complete-availability time',
        'W_union':'same-scope same-direction packet counted once; no T ownership inferred',
        'missing_members':'no waiver; unchanged hold','inherited_passes':'raw inputs rehashed; numerical identity from absence of affected packet categories'}
    if (OUT/'contract.json').exists():assert read(OUT/'contract.json')==contract
    else:write(OUT/'contract.json',contract)
    selected=pool
    if args.pilot:
        selected=pd.concat([pool[pool.review_reasons.str.contains(v)].head(1) for v in ['selected_fragment','ambiguous','members_without']]+[pool[pool.old_W_passed].head(1)]).drop_duplicates('session_id')
    results=[]
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        for i,r in enumerate(ex.map(task,selected.to_dict('records')),1):
            results.append(r)
            print(f'{i}/{len(selected)} {r["protocol"]} W={r["W_gate_passed"]} {r["review_reasons"]}',flush=True)
            write(OUT/'progress.json',{'completed':i,'total':len(selected),'pilot':args.pilot,'training_performed':False})
    tag='pilot' if args.pilot else 'full'
    pd.DataFrame([v for r in results for v in r['W']]).to_parquet(OUT/f'{tag}-W-features.parquet',index=False)
    pd.DataFrame([v for r in results for v in r['T']]).to_parquet(OUT/f'{tag}-T-features.parquet',index=False)
    fields=['session_id','protocol','W_gate_passed','T_candidate_pairs','T_common_pairs','missing_pre','missing_post']
    pd.DataFrame([{k:r[k] for k in fields}|{'review_reasons':r['review_reasons']} for r in results]).to_parquet(OUT/f'{tag}-coverage.parquet',index=False)
    write(OUT/f'{tag}-gate.json',{'visits':len(results),'W_passed':sum(r['W_gate_passed'] for r in results),
        'reasons':dict(Counter(v for r in results for v in r['review_reasons'])),
        'training_allowed':False,'epoch_and_capture_scope_gate_passed':False})


if __name__=='__main__':main()
