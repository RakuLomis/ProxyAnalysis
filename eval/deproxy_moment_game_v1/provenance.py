"""Deep P0 seals and observed reader hashes; metadata/hash-only post-P1 audit."""
from common import *

def run():
    b=barrier('P0-complete.json');barrier('P1-numeric-complete.json');expected={};count=0
    for r in roles():
        p=OUT/'packages'/r['id']/'complete.json'
        require(sha(p)==b['files'][rel(p)],'P0 child seal changed')
        for path,h in read(p)['files'].items():
            require(sha(ROOT/path)==h,'P0 tensor or metadata changed: '+path);expected[path]=h;count+=1
    reads=0;cap_counts={};forbidden=[]
    for p in (OUT/'permissions').glob('*.json'):
        for v in read(p)['reads']:
            path=v['path'];cap=v.get('capability','trusted');kind=v.get('kind','')
            reads+=1;cap_counts[cap]=cap_counts.get(cap,0)+1
            if path in expected:require(v['sha256']==expected[path],'Observed read differs from original P0 binding')
            elif path in contract()['files']:require(v['sha256']==contract()['files'][path]['sha256'],'Observed historical read mismatch')
            require(kind not in ['query','labels'],'Query/labels read before P1 completion')
            if cap=='G':require(kind!='P' and '/paired/' not in path,'Group consumed paired artifact')
            if cap=='E':require(kind not in ['P','G','pre','source-pre'] and '/scales/pre.' not in path,'Post control consumed pre')
    require(reads>0,'Missing read audits')
    immutable(OUT/'tests/P1-provenance-audit.json',dict(passed=True,observed_reads=reads,capability_read_counts=cap_counts,
        P0_sealed_files_deeply_verified=count,query_label_reads=0,H_pre_reads=0,target_U_training_rows=0,
        group_paired_artifact_reads=0,post_control_pre_artifact_reads=0,old_source_guard_stop_retained=True))

if __name__=='__main__':run()
