"""Sealed finite experiment; failure is a terminal state, not a silent retry."""
import subprocess
import traceback
from common import *

STAGES=[('train.py','pilot'),('train.py','repeat'),('train.py','promote'),
        ('train.py','inner-fit'),('selection.py','inner-predict'),('selection.py','select'),
        ('train.py','outer-fit'),('selection.py','predict'),('evaluate.py','references'),
        ('evaluate.py','score'),('diagnostics.py',''),('plots.py',''),('verify.py',''),('report.py','')]

def run():
    configure();start('runner');require(not (OUT/'failure.json').exists(),'Terminal failure requires user-approved revision')
    require(not (OUT/'completion.json').exists(),'Run already complete')
    lock=writable(OUT/'runner.lock');lock.parent.mkdir(parents=True,exist_ok=True)
    fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY);os.write(fd,str(os.getpid()).encode());os.close(fd)
    try:
        seal=sha(OUT/'manifests/experiment-contract.json')
        for index,(script,arg) in enumerate(STAGES):
            marker=OUT/'manifests/stages'/f'{index:02d}-{Path(script).stem}-{arg or "run"}.json'
            if marker.exists():require(read(marker)['contract_sha256']==seal,'Stage contract changed');continue
            start('runner');progress('JA_running_stage',stage_index=index,total_stages=len(STAGES),script=script,action=arg,pid=os.getpid())
            cmd=[sys.executable,'-u',str(Path(__file__).parent/script)]+([arg] if arg else [])+['--run',str(OUT)]
            subprocess.run(cmd,cwd=ROOT,env=dict(os.environ,PYTHONIOENCODING='utf-8'),check=True)
            complete(marker,contract_sha256=seal,stage_index=index)
        require(read(OUT/'verification.json')['passed'],'Final verification failed')
        complete(OUT/'completion.json',stages=len(STAGES),verification_passed=True,
                 new_main_classifiers=34740,mapping_tasks=8820,old_main_models_used_as_new=0)
        progress('JA_experiment_complete',verification_passed=True)
    except BaseException as exc:
        write(OUT/'failure.json',{'time_unix':time.time(),'exception':str(exc),'traceback':traceback.format_exc(),
                                'policy_extended':False,'automatic_retry':False})
        progress('JA_engineering_stop',error=str(exc));raise
    finally:
        if lock.exists() and lock.read_text()==str(os.getpid()):lock.unlink()

if __name__=='__main__':run()
