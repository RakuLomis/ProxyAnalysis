"""Fixed nine source-only tasks; engineering and throughput, not method selection."""
from common import *
from teacher import fit_batch as teachers
from train import fit_batch as residuals
from models import logits

def run():
    with stage('P1_cuda_pilot',training=True):
        require(read(OUT/'audits/unit-tests.json')['passed'],'Unit test gate')
        files=[p for p in Path(__file__).parent.glob('*.py') if p.name!='inspect_sources.py']
        seal(OUT/'manifests/engineering-code.json',files,passed=True,
             batch_probability_atol=1e-5,batch_logit_atol=1e-4,version='first-engineering-policy')
        selected=[]
        # Deterministic, one group per calibration protocol from the first actual target.
        rs=contract()['inner_roles'];actual=contract()['roles'][0]['target']
        for pseudo in [p for p in PROTOCOLS if p!=actual]:
            for group in ['G0','G1','G2']:
                selected.append(next(r for r in rs if r['outer']==0 and r['target']==actual and r['calibration']==pseudo and r['group']==group))
        require(len(selected)==9 and all(r['inner']==1 for r in selected),'Fixed pilot members')
        # Same fixed 1000 steps, standalone vs independent batched update.
        first=selected[0];job=(first,'A1',0.,20261014)
        single,_,ts=residuals([job],publish=False,audit_path=OUT/'pilot/stable/standalone')
        batched,_,tb=residuals([job,(selected[1],'A1',0.,20261014)],publish=False,audit_path=OUT/'pilot/stable/batched')
        d=own(taskpath(first)/'classification.pt','test');m=own(PARENT/'base-models'/first['id']/'P-small.pt','test')
        p=logits(single[0],d['x'],m);q=logits(batched[0],d['x'],m)
        pe=float((p.softmax(1)-q.softmax(1)).abs().max());le=float((p-q).abs().max())
        passed=pe<=1e-5 and le<=1e-4
        write(OUT/'pilot/batch-replay.json',dict(passed=passed,max_probability_error=pe,max_logit_error=le,
              changed_classes=int((p.argmax(1)!=q.argmax(1)).sum()),standalone_seconds=ts,batch_seconds=tb,
              engineering_residual_fits=3,steps=1000))
        require(passed,'Independent batched/standalone training replay')
        _,_,tt=teachers(selected)
        jobs=[(r,arm,lam,20261014) for r in selected for arm,lam in CONFIGS]
        times=[]
        for i in range(0,len(jobs),32):
            _,_,sec=residuals(jobs[i:i+32]);times.append(dict(heads=len(jobs[i:i+32]),seconds=sec))
        rate=max(x['seconds']/x['heads'] for x in times)
        teacher_rate=tt/9
        # Conservative throughput estimate plus factor 1.5 for role IO, padding and scheduling.
        remaining=1.5*(rate*(11340-45)+teacher_rate*(780-9))
        estimate=remaining+ts+tb+tt+sum(x['seconds'] for x in times)
        info=dict(passed=True,tasks=9,teachers=9,formal_residual_fits=45,engineering_residual_fits=3,
                  teachers_seconds=tt,residual_batches=times,seconds_per_head_upper=rate,
                  projected_total_training_seconds=estimate,preflight_limit_seconds=34560,
                  estimated_hours=estimate/3600,within_preflight=estimate<=34560,
                  peak_cuda_MiB=torch.cuda.max_memory_allocated()/1048576,H_reads=0,U_reads=0,
                  no_scientific_result_selection=True)
        write(OUT/'pilot/summary.json',info)
        write(OUT/'manifests/pilot-members.json',[r['id'] for r in selected])
        require(info['within_preflight'],'Budget confirmation required; do not shorten matrix')

if __name__=='__main__':run()
