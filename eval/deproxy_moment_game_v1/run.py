"""Complete approved range after P1; stop, never shrink, on budget or any failure."""
from common import *
import subprocess

def call(script,args=()):
    remaining();p=subprocess.run([sys.executable,str(CODE/script),*args],cwd=ROOT)
    require(p.returncode==0,'Subprocess stopped; inspect preserved failure. No automatic retry.')

def worker_matrix(scope):
    for cap,phase in [('G','initial'),('E','initial'),('P','anchor'),('G','anchor'),('P','static'),('G','static'),('P','dynamic'),('G','dynamic'),('E','dynamic')]:
        call('full_worker.py',['--cap',cap,'--phase',phase,'--scope',scope])

def run():
    barrier('P1-complete.json');require(read(OUT/'tests/P1-inference.json')['passed'],'P1 export/reader check')
    from formal import source_model_seal,source_predict,selection,outer_model_seal,outer_predict
    worker_matrix('inner');source_model_seal();source_predict();selection()
    worker_matrix('outer');outer_model_seal();outer_predict()
    from score import run as score
    score()
    from verify import run as verify
    verify()
    immutable(OUT/'completion.json',dict(status='complete',formal_complete=True,H_scored=True,
        activity_used_seconds=read(OUT/'budget.json')['used_seconds'],endpoints=2340,H_prediction_rows=56160))
    progress('complete',formal_complete=True,H_scored=True)

if __name__=='__main__':
    try:run()
    except BaseException as e:
        failure('complete-schedule',e)
        immutable(OUT/('stop-'+str(time.time_ns())+'.json'),dict(status='stopped',reason=str(e),unrun_is_not_fallback=True))
        raise
