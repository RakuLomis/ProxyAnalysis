"""Preserve complete bounded logical lifecycles for the nine missing-member visits."""
from pathlib import Path
import sys
import json
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
from proxy_analysis.extend_calibration.audit import read,write,fs_path
BASE=ROOT/'outputs/extend-calibration-20260930/run-01'


def main():
    old=BASE/'extraction-01';new=BASE/'extraction-02'
    pool=pd.read_parquet(old/'metadata-qualified-pool.parquet').set_index('session_id')
    cv=pd.read_parquet(new/'full-coverage.parquet')
    clock=read(new/'epoch-capture-audit-01/clock-candidates.json')
    rows=[]
    for sid in cv.loc[~cv.W_gate_passed,'session_id']:
        scope=read(old/'sessions'/sid/'scope.json')
        ids=set(scope['missing_pre'])|{v for c in scope['missing_post'] for v in scope['carriers'][c]}
        base=(fs_path(ROOT/'Datasets/extend')/pool.loc[sid,'manifest_relative']).parent
        snap=read(base/'analysis/summary.json')['trace_snapshot']['traces'][0]
        tail=set(snap.get('causal_tail_event_seqs',[]))
        evidence=[]
        for line in (base/'raw/mihomo-trace.jsonl').open(encoding='utf-8'):
            if not any(ident in line for ident in ids):continue
            e=json.loads(line);seq=e.get('event_seq')
            if not isinstance(seq,int) or not (seq<=snap['cutoff_event_seq'] or seq in tail):continue
            ident=e.get('logical_conn_id') or e.get('conn_id')
            if ident not in ids:continue
            if e.get('type') not in ['tcp_connect','tcp_proxy_dial','logical_carrier_bind','tcp_close']:continue
            evidence.append({k:e.get(k) for k in ['type','ts','event_seq','bytes_up','bytes_down','duration_ms','status']}|{'logical_id':ident})
        rows.append({'session_id':sid,'protocol':pool.loc[sid,'protocol'],'events':evidence,
            'candidate_capture_boundaries':[c for c in clock if c['session_id']==sid],
            'eligibility_changed':False,'clock_mapping_still_conditional':True})
    target=new/'epoch-capture-audit-01/logical-boundary-evidence.json'
    assert not target.exists()
    write(target,rows)
    print({'visits':len(rows),'events':sum(len(r['events']) for r in rows),'eligibility_changed':False})


if __name__=='__main__':main()
