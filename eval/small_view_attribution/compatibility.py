"""Read-only old-batch qualification; no PCAP, feature conversion or fits."""
from common import *
import pyarrow.parquet as pq
from urllib.parse import urlsplit,parse_qs

SOURCES=[
 'docs/0914-business14-classification-results-20260918.md',
 'docs/0916-dataset-and-experiments-summary-20260917.md',
 'docs/0916-group-anchor-results-20260919.md',
 'docs/mechanism-guided-drift/configuration-gaps.md',
 'outputs/business-recognition-0914/run-01/prepared/visits.parquet',
 'outputs/business-recognition-0914/run-01/prepared/labels.json',
 'outputs/business-recognition-0914/run-01/contract/manifest.json',
 'outputs/content-generalization-20260916/business-01/primary-cohort.parquet',
 'outputs/content-generalization-20260916/business-01/post-features.parquet',
 'outputs/content-generalization-20260916/business-01/identity-gate.json',
 'outputs/protocol-normalization-0914-0916/run-01/tcp-byte-ledger.parquet',
 'outputs/protocol-normalization-0914-0916/run-01/contract.json']

def audit_read(p):
    p=ROOT/p if not Path(p).is_absolute() else Path(p)
    checked(p,contract()['fixed_files'][rel(p)],'qualification-audit');return p

def canonical(u):
    if u.startswith('youtube_video:'):return u
    q=urlsplit(u)
    if q.hostname in ['youtube.com','www.youtube.com'] and q.path=='/watch':
        ids=parse_qs(q.query).get('v',[])
        if len(ids)==1:return 'youtube_video:'+ids[0]
    if q.hostname=='youtu.be' and q.path.strip('/'):return 'youtube_video:'+q.path.strip('/')
    return u

def run():
    with stage('compatibility'):
        current=set.union(*[set(r['train_contents'])|set(r['validation_contents']) for r in contract()['roles']])
        canonical_current={canonical(u) for u in current};rows=[];details=[];overlap=[]
        for batch,path in [('0914',SOURCES[4]),('0916',SOURCES[7])]:
            p=audit_read(path);cols=['session_id','content_id','label_id','protocol','repetition']
            d=pd.read_parquet(p,columns=cols);labels=set(d.label_id);shared=sorted(labels&set(LABELS));missing=sorted(set(LABELS)-labels)
            by=d.groupby('label_id').agg(contents=('content_id','nunique'),visits=('session_id','nunique')).reset_index()
            by['batch']=batch;details.append(by)
            for u in sorted(d.content_id.unique()):
                if canonical(u) in canonical_current:overlap.append({'batch':batch,'historical_content':u,'canonical_content':canonical(u),
                     'exact_string_match':u in current,'global_training_exclusion_required':True})
            rows.append({'batch':batch,'visits':len(d),'contents':d.content_id.nunique(),'labels':len(labels),
                'matching_current_labels':len(shared),'missing_current_labels':'; '.join(missing),
                'protocols':'; '.join(sorted(d.protocol.unique())),'repetitions':'; '.join(map(str,sorted(d.repetition.unique()))),
                'current_96D_ready':False,'identity_overlap_contents':sum(v['batch']==batch for v in overlap),
                'status':'业务覆盖不兼容且需重新构造表示' if missing else '业务标签兼容，需重新构造并审核96维表示'})
        schemas=[]
        for path in [SOURCES[4],SOURCES[8],SOURCES[10]]:
            p=audit_read(path);schemas.append({'path':path,'rows':pq.read_metadata(p).num_rows,'columns':pq.read_schema(p).names,
                        'has_ready_96_columns':set(HIST)<=set(pq.read_schema(p).names)})
        for p in SOURCES:
            if p.endswith('.md') or p.endswith('.json'):audit_read(p)
        save(pd.DataFrame(rows),OUT/'audits/historical-batches.parquet')
        save(pd.concat(details,ignore_index=True),OUT/'audits/historical-businesses.parquet')
        save(pd.DataFrame(overlap,columns=['batch','historical_content','canonical_content','exact_string_match','global_training_exclusion_required']),OUT/'audits/cross-batch-overlap.parquet')
        write(OUT/'audits/historical-compatibility.json',{'passed_inventory':True,'direct_transfer_qualified':False,
             'schemas':schemas,'batches':rows,'new_fits':0,'PCAP_reads':0,'feature_extraction':False,
             'old_VLESS_REALITY_Vision_not_same_as_extend_TLS':True,'historical_SS_cipher_unknown':True,
             'canonicalization_rule':'Only explicit YouTube video ID aliases; other strings unchanged',
             'next_step_requires_user_approval':'Separate compatible-label/content and 96D reconstruction contract'})

if __name__=='__main__':run()
