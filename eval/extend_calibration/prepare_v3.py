"""Freeze source-proven clock semantics and common-window metadata for all visits."""
from pathlib import Path
import sys
import urllib.request
from concurrent.futures import ProcessPoolExecutor
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
from proxy_analysis.extend_calibration.audit import read,write,fs_path,file_hash
from proxy_analysis.extend_calibration.common_window import prepare_scope,COLLECTOR_COMMIT,CHROME_COMMIT
BASE=ROOT/'outputs/extend-calibration-20260930/run-01'
OUT=BASE/'extraction-03'


def one(row):
    base=(fs_path(ROOT/'Datasets/extend')/row['manifest_relative']).parent
    manifest=read(base/'manifest.json');flows=read(base/'analysis/flow-index.json')['items']
    window,exclusions=prepare_scope(base,manifest,flows)
    selected=set(read(BASE/'extraction-01/sessions'/row['session_id']/'scope.json')['selected_logical_ids'])
    return {'session_id':row['session_id'],'protocol':row['protocol'],**window,
            'excluded_selected':{k:v for k,v in exclusions.items() if k in selected},
            'original_selected_members':len(selected),'training_allowed':False}


def main():
    OUT.mkdir(exist_ok=True);source=OUT/'clock-source-evidence';source.mkdir(exist_ok=True)
    urls={
        'collector-tshark.txt':f'https://raw.githubusercontent.com/RakuLomis/TrafficTracer/{COLLECTOR_COMMIT}/traffictracer/capture/tshark.py',
        'collector-job.txt':f'https://raw.githubusercontent.com/RakuLomis/TrafficTracer/{COLLECTOR_COMMIT}/traffictracer/capture/job.py',
        'chromium-netlog.txt':f'https://raw.githubusercontent.com/chromium/chromium/{CHROME_COMMIT}/net/log/net_log_util.cc',
        'chromium-time.txt':f'https://raw.githubusercontent.com/chromium/chromium/{CHROME_COMMIT}/base/time/time_now_posix.cc',
        'cpython-clock-reference.txt':'https://raw.githubusercontent.com/python/cpython/v3.12.0/Python/pytime.c'}
    evidence=[]
    for name,url in urls.items():
        target=source/name
        if not target.exists():
            # Stored source text is provenance only; never imported or executed.
            data=urllib.request.urlopen(url,timeout=30).read();target.write_bytes(data)
        evidence.append({'file':name,'url':url,'sha256':file_hash(target)})
    write(source/'manifest.json',{'sources':evidence,'cpython_version_is_implementation_reference_not_claim_of_captured_exact_build':True})
    assert not (OUT/'prepared-windows.json').exists(),'prepared metadata frozen'
    pool=pd.read_parquet(BASE/'extraction-01/metadata-qualified-pool.parquet')
    rows=[]
    with ProcessPoolExecutor(max_workers=4) as ex:
        for i,r in enumerate(ex.map(one,pool.to_dict('records')),1):
            rows.append(r)
            if i%100==0:print(f'Common-window scope {i}/600',flush=True)
    write(OUT/'prepared-windows.json',rows)
    write(OUT/'window-preflight.json',{'visits':len(rows),'all_source_platform_and_order_checks_passed':True,
        'tick_offset_values_ms':sorted({r['tick_offset_ms'] for r in rows}),
        'excluded_selected_members':sum(len(r['excluded_selected']) for r in rows),
        'visits_with_exclusions':sum(bool(r['excluded_selected']) for r in rows),
        'end_boundary':'browser_quiescent, NOT process-exit stopped', 'training_allowed':False,
        'code_sha256':file_hash(ROOT/'src/proxy_analysis/extend_calibration/common_window.py')})


if __name__=='__main__':main()
