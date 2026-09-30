"""Bounded existing-log evidence check, no raw lines persisted."""
import gzip
from .common import *

def audit_logs():
    selected=load('parse-sample-manifest');reg=pd.read_parquet(BASE/'registry.parquet').set_index('session_id')
    paths=[]
    for sid in sorted(selected[selected.protocol=='VLESS'].session_id.unique()):
        root=Path(reg.loc[sid,'session_path'])
        for rel in ['raw/mihomo-trace.jsonl','raw/trace-input/trace.jsonl.gz']:
            f=root/rel
            if f.exists():paths.append((sid,f))
    total=sum(f.stat().st_size for _,f in paths)
    if total+read(OUT/'budget.json')['bytes']>2**31:
        js('phase-log-audit.json',{'status':'not_scanned_budget','file_bytes':total});return
    markers=['XTLS Vision direct read start','XTLS Vision direct write start','XTLS Vision read padding','XTLS Vision write padding']
    rows=[];expanded=0
    for sid,f in paths:
        counts={m:0 for m in markers}
        opener=gzip.open if f.suffix=='.gz' else open
        with opener(f,'rt',encoding='utf-8',errors='replace') as stream:
            for line in stream:
                expanded+=len(line.encode('utf-8'))
                if expanded>2**31:
                    js('phase-log-audit.json',{'status':'partial_expansion_budget','expanded_bytes':expanded});return
                for m in markers:counts[m]+=int(m in line)
        rows.append({'session_id':sid,'path':str(f),'sha256':digest(f),'markers':counts})
    js('phase-log-audit.json',{'status':'complete','files':len(rows),'file_bytes':total,'expanded_bytes':expanded,
                             'matched_lines':sum(sum(r['markers'].values()) for r in rows),'sources':rows})
    print('Selected-log marker audit:',len(rows),'files;',sum(sum(r['markers'].values()) for r in rows),'matches',flush=True)

if __name__=='__main__':audit_logs()
