"""Durable full P2-P6 schedule, one capability process and one ledger writer."""
from common import *
import subprocess

def call(script,args=()):
    remaining();b=read(OUT/'budget.json');used=b['new_seconds'];started=time.perf_counter();name=f'{time.time_ns()}-{Path(script).stem}'
    stdout=writable(OUT/'logs'/f'{name}.stdout.log');stderr=writable(OUT/'logs'/f'{name}.stderr.log')
    with stdout.open('w',encoding='utf-8') as so,stderr.open('w',encoding='utf-8') as se:
        child=subprocess.Popen([sys.executable,'-u',str(CODE/script),*args],cwd=ROOT,stdout=so,stderr=se)
        write(OUT/'active-child.json',dict(pid=child.pid,script=script,args=list(args),unix=time.time(),stdout=rel(stdout),stderr=rel(stderr)))
        timedout=False
        try:rc=child.wait(timeout=remaining())
        except subprocess.TimeoutExpired:
            child.terminate();child.wait(timeout=30);rc=child.returncode;timedout=True
    elapsed=time.perf_counter()-started;b=read(OUT/'budget.json');covered=b['new_seconds']-used;extra=max(0.,elapsed-covered)
    b['new_seconds']+=extra;b['used_seconds']=b['inherited_seconds']+b['new_seconds']
    b['items'].append(dict(stage='subprocess-uncovered-wall',script=script,args=list(args),seconds=extra,wall_seconds=elapsed,
        worker_accounted_seconds=covered,returncode=rc,activity_watchdog=timedout));write(OUT/'budget.json',b)
    immutable(OUT/'logs'/f'{name}.completion.json',dict(script=script,args=list(args),returncode=rc,wall_seconds=elapsed,watchdog=timedout))
    require(not timedout and rc==0,'Full NER1 child stopped; inspect preserved logs; no automatic retry')
    remaining();codecheck();progress('full_child_complete',script=script,args=list(args),cumulative_hours=b['used_seconds']/3600)

def worker_matrix(scope):
    for cap,phase in [('G','initial'),('E','initial'),('P','anchor'),('G','anchor'),('P','static'),('G','static'),('P','dynamic'),('G','dynamic'),('E','dynamic')]:
        call('worker.py',['--cap',cap,'--phase',phase,'--scope',scope])

def run():
    require(not (OUT/'driver-start.json').exists(),'No implicit restart; preserve stopped execution')
    immutable(OUT/'driver-start.json',dict(pid=os.getpid(),unix=time.time(),activity_cap=144000,forecast_gate=115200,full_authorized=True))
    barrier('P1-complete.json')
    try:
        worker_matrix('inner')
        for phase in ['source-seal','source-predict','selection']:call('phase.py',[phase])
        worker_matrix('outer')
        for phase in ['outer-seal','outer-predict','score','verify','report']:call('phase.py',[phase])
        seal(OUT/'manifests/complete-seal.json',[OUT/'manifests/P6-complete.json',OUT/'reports/complete-report.md'])
        immutable(OUT/'completion.json',dict(program_complete=True,numeric_pass=True,all_required_roles_completed=True,H_scored=True,
            cumulative_seconds=read(OUT/'budget.json')['used_seconds'],outer_endpoints=2340,H_prediction_rows=56160,model_effect_not_equal_program_pass=True))
        progress('complete',program_complete=True,H_scored=True)
    except BaseException as e:
        failure('full-schedule',e)
        immutable(OUT/'stop-record.json',dict(program_complete=False,H_scored=(OUT/'manifests/P5-scores-complete.json').exists(),
            reason=str(e),pending_is_not_fallback=True,old_stop_records_preserved=True,cumulative_seconds=read(OUT/'budget.json')['used_seconds']))
        raise

if __name__=='__main__':run()
