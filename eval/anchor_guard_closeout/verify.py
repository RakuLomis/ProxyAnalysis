"""Final lineage and CSV/Parquet reconciliation; no retroactive qualification update."""
from common import *

def run():
    c=contract();need(read(OUT/'analysis-complete.json')['passed'] and read(OUT/'csv-export-verification.json')['passed'],'Unfinished diagnostic/export')
    for p,h in c['files'].items():need(sha(ROOT/p)==h,'Parent input changed at final verification')
    for p,h in c['source_sha256'].items():need(sha(ROOT/p)==h,'Sealed closeout code changed')
    need(sha(PLAN)==c['plan_sha256'],'Plan changed')
    errors={};checks=[]
    for entry in read(OUT/'analysis-complete.json')['tables']:
        a=pd.read_parquet(ROOT/entry['parquet'])
        missing={k:[''] for k in a if pd.api.types.is_numeric_dtype(a[k])}
        b=pd.read_csv(ROOT/entry['csv'],float_precision='round_trip',keep_default_na=False,na_values=missing)
        need(list(a)==list(b) and a.shape==b.shape,'CSV schema/shape mismatch')
        maximum=0.
        for k in a:
            need(a[k].isna().equals(b[k].isna()),'CSV missing-versus-zero mismatch: '+entry['table']+'/'+k)
            keep=~a[k].isna()
            if pd.api.types.is_bool_dtype(a[k]):need(a.loc[keep,k].astype(bool).equals(b.loc[keep,k].astype(bool)),'CSV boolean mismatch')
            elif pd.api.types.is_numeric_dtype(a[k]):
                x=a.loc[keep,k].to_numpy();y=b.loc[keep,k].to_numpy();err=float(np.max(np.abs(x-y))) if len(x) else 0.;maximum=max(maximum,err)
                need(np.allclose(x,y,atol=1e-12,rtol=1e-13),'CSV numeric mismatch')
            else:need(a.loc[keep,k].astype(str).equals(b.loc[keep,k].astype(str)),'CSV identifier/text mismatch')
        errors[entry['table']]=maximum;checks.append({'table':entry['table'],'rows':len(a),'CSV_parquet_match':True})
    audit=read(OUT/'audits/numerical-replay-audit.json');need(audit['passed'],'Numerical replay failed')
    need(not (OUT/'failure.json').exists(),'Failed diagnostic cannot complete')
    for p in c['source_sha256']:
        if Path(p).suffix!='.py':continue
        tree=ast.parse((ROOT/p).read_text(encoding='utf-8'))
        for node in ast.walk(tree):
            if isinstance(node,ast.ImportFrom):need(not (node.module or '').startswith('anchor_guard_drift'),'Parent functions imported')
            if isinstance(node,ast.Import):need(all(not a.name.startswith('anchor_guard_drift') for a in node.names),'Parent functions imported')
    files={rel(p):sha(p) for p in list(OUT.rglob('*'))+list(DOC.rglob('*')) if p.is_file() and 'plot-cache' not in p.parts and p.name not in {'progress.json','verification.json','completion.json'}}
    v={'passed':True,'parent_verification_sha256':c['parent_verification_sha256'],'parent_files_unchanged':True,
       'parent_stop':'stop_no_supported_protection_target','independent_numeric_replay':audit,'files':files,
       'CSV_reconciliation':checks,'CSV_max_numeric_roundtrip_errors':errors,'new_mapping_fits':0,'new_classifier_fits':0,
       'H_U_PCAP_reads':0,'thresholds_changed':False,'physical_post_input_qualified':False,'stage_two_authorized':False}
    write(OUT/'verification.json',v);write(OUT/'completion.json',{'passed':True,'closeout_complete':True,'new_mapping_fits':0,
          'new_classifier_fits':0,'parent_stop_preserved':True,'stage_two_authorized':False,'verification_sha256':sha(OUT/'verification.json')})
    progress('closeout_complete_parent_stop_preserved',tables=len(checks),new_fits=0)

if __name__=='__main__':run()
