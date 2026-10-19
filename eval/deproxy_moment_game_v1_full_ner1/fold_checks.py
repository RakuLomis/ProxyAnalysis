"""Metadata-only nested content/role proof; no query features or labels."""
from common import *

def audit():
    c=contract();count=0;all_contents=set()
    for r in c['roles']:
        train=set(r['train_contents']);held=set(r['validation_contents']);all_contents|=train|held
        require(len(train)==24 and len(held)==6 and not train&held,'Outer content fold')
        require(set(r['C_contents'])|set(r['U_contents'])==train and not set(r['C_contents'])&set(r['U_contents']),'Outer C/U partition')
        inner=[x for x in c['inner_roles'] if (x['outer'],x['target'],x['group'])==(r['outer'],r['target'],r['group'])]
        require(len(inner)==12,'All source pseudo target/fold roles')
        for q in inner:
            qt=set(q['train_contents']);qv=set(q['validation_contents'])
            require(len(qt)==18 and len(qv)==6 and qt|qv==train and not qt&qv,'Nested inner uses only outer train contents')
            require(not (qt|qv)&held,'Outer H content entered inner training/query')
            require(set(q['sources']+[q['calibration']])==set(r['sources']) and q['target'] not in q['sources']+[q['calibration']],'Actual target excluded from all source roles')
            require(set(q['C_contents'])|set(q['U_contents'])==qt and not set(q['C_contents'])&set(q['U_contents']),'Inner C/U partition')
            count+=1
    require(count==720 and len(all_contents)==30,'Global nested coverage')
    immutable(OUT/'manifests/P0-nested-fold-audit.json',dict(passed=True,outer_roles=60,inner_roles=count,global_contents=30,
        inner_query_contents_subset_outer_training=True,actual_target_absent_from_inner=True,query_numeric_reads=0,query_label_reads=0))
    progress('P0_nested_content_audit_passed',outer_roles=60,inner_roles=count)

if __name__=='__main__':audit()
