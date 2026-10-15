"""Independent lineage, counts, numeric gates and permission-ledger closeout."""
from common import *

def run():
    with stage('verify'):
        c=contract();verify_seal(OUT/'manifests/models-complete.json');verify_seal(OUT/'predictions/complete.json')
        for p,h in {**c['fixed_files'],**c['code']}.items():require(sha(ROOT/p)==h,'Changed frozen dependency')
        led=read(OUT/'ledger.json');require(led['logical_forward']==45360 and led['q_updates']==3600 and led['new_final_LR']==180,'Logical formal budgets')
        require(led['new_source_LR']+led['cache_hits']==45360,'Cache/fit exposure ledger')
        require(led['validation']==led['new_source_LR'] and led['implicit']==2*led['new_source_LR'],'Per-point validation coverage')
        require(len(list((OUT/'q').rglob('*.pt')))==180 and len(list((OUT/'models').rglob('*.pt')))==180,'New endpoint count')
        require(len(pd.read_parquet(OUT/'manifests/endpoints.parquet'))==600,'All endpoints')
        for p in (OUT/'stages').glob('*.json'):
            for row in read(p).get('reads',[]):
                if row['purpose']=='source-feedback':
                    role=c['packages'][row['path']]['role_id'];require('/outer' not in role,'Actual H in source feedback')
                if row.get('arm')=='D-G':
                    require(not row['purpose'].startswith('C-P'),'G accessed P targets')
        files={rel(p):sha(p) for p in OUT.rglob('*') if p.is_file() and p.name not in ['stage.lock','progress.json','verification.json','completion.json']}
        write(OUT/'verification.json',dict(passed=True,files=files,lineage_unchanged=True,new_LR_total=led['new_source_LR']+180,scientific_policy_unchanged=True,source_tasks=720,H_scoring_after_seals=True))
        write(OUT/'completion.json',dict(status='formal_business_complete',passed=True,formal_complete=True,H_scored=True,verification_sha256=sha(OUT/'verification.json'),ledger=led))

if __name__=='__main__':run()

