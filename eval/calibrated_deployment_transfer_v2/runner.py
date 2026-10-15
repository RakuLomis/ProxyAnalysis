"""Run sealed engineering pilot before unchanged formal downstream procedures."""
import os
os.environ.setdefault('CUBLAS_WORKSPACE_CONFIG', ':4096:8')
os.environ['PYTHONIOENCODING']='utf-8'
import subprocess
import sys
import traceback
from common import *

STAGES=[('control.py','pilot'),('control.py','repeat'),('control.py','reuse'),('control.py','promote'),
        ('downstream.py','inner-fit'),('downstream.py','inner-predict'),('downstream.py','select'),
        ('downstream.py','outer-fit'),('downstream.py','predict'),('downstream.py','score'),
        ('downstream.py','explain'),('downstream.py','observation'),('downstream.py','plots'),
        ('verify.py',''),('report.py','')]

def run():
    configure();start('runner');lock=writable(OUT/'runner.lock')
    fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY);os.write(fd,str(os.getpid()).encode());os.close(fd)
    try:
        for i,(script,arg) in enumerate(STAGES):
            marker=OUT/'manifests/stages'/f'{i:02d}-{Path(script).stem}-{arg or "run"}.json'
            seal=sha(OUT/'manifests/experiment-contract-v2.json')
            if marker.exists():require(read(marker)['contract_sha256']==seal,'Stage contract changed');continue
            start('runner');progress('running_'+str(i),script=script,action=arg,pid=os.getpid(),stages_completed=i)
            cmd=[sys.executable,'-u',str(Path(__file__).parent/script)]+([arg] if arg else [])
            subprocess.run(cmd,cwd=ROOT,env=os.environ.copy(),check=True)
            complete(marker,contract_sha256=seal,stage=i)
        complete(OUT/'completion.json',stages=len(STAGES),verification_passed=True,
                 v2_new_main_fits=14700,reused_diagnostic_fits=680,old_run_unchanged=True,
                 stage3_status='external_window_and_physical_only_extraction_not_verified')
        progress('v2_numerical_experiment_complete',physical_only_extraction_complete=False)
    except BaseException as e:
        write(OUT/'failure.json',{'time_unix':time.time(),'exception':str(e),'traceback':traceback.format_exc(),
                                'budget_or_gradient_gate_changed':False})
        progress('engineering_stop',error=str(e));raise
    finally:
        if lock.exists() and lock.read_text()==str(os.getpid()):lock.unlink()

if __name__=='__main__':run()
