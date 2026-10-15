"""Approved conditional workflow; no automatic retries after a scientific gate."""
from common import *
import register
import permissions
import payload_tests
import OOF_coefficients
import episodes
import solution_feedback
import meta
import final_fit
import predict
import score
import verify
import report

def prepared():
    for name in ['permissions','payload_tests','OOF_coefficients','episodes','numeric_tests']:require(read(OUT/'stages'/f'{name}.json')['passed'],'Preparation gate '+name)

def prepare():
    register.run();permissions.run();payload_tests.run();OOF_coefficients.run();episodes.run()
    with stage('numeric_tests'):write(OUT/'audits/synthetic-math.json',solution_feedback.synthetic_tests())

def batch(first):
    name='batch_one' if first else 'batch_remaining'
    with stage(name):
        prepared();rs=[r for r in contract()['roles'] if (r['outer']==0)==first]
        if not first:require(read(OUT/'batch-one-audit.json')['passed'],'First batch promotion')
        begin=time.perf_counter();endpoints=[]
        for i,r in enumerate(rs):
            disk=disk_gate()
            for arm in ARMS:
                meta.fit_role(r,arm);endpoints.append(final_fit.fit(r,arm))
            disk_gate();progress(name+'_roles',roles=i+1,total=len(rs),new_models=len(endpoints),elapsed=time.perf_counter()-begin)
        require(len(endpoints)==(36 if first else 144),'Batch final model count')
        save(pd.DataFrame(endpoints),OUT/'manifests'/f'{name}-endpoints.parquet')
        seconds=time.perf_counter()-begin
        if first:write(OUT/'batch-one-audit.json',dict(passed=True,roles=12,new_final_models=36,seconds=seconds,rough_remaining_seconds=4*seconds,estimate_not_promise=True,H_queries_read=False,H_labels_read=False,disk=disk,peak_cuda_MiB=torch.cuda.max_memory_allocated()/1048576))

def formal():
    require(not (OUT/'completion.json').exists(),'Closed/failed version cannot continue automatically')
    prepared();batch(True);batch(False);predict.seal_models();predict.run();score.run();verify.run()

if __name__=='__main__':
    try:
        {'prepare':prepare,'formal':formal,'all':lambda:(prepare(),formal()),'report':report.run}[sys.argv[1]]()
    finally:
        if (OUT/'ledger.json').exists():report.run()

