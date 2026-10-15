"""Continue accepted stages only; failed stages never automatically retried."""
from common import *
import subprocess

STAGES=[('P1_tests','tests.py'),('P1_cuda_pilot','cuda_pilot.py'),('P2_inner_train','inner_train.py'),
        ('P2_selection','select.py'),('P3_final_train','final_train.py'),('P4_predict','predict.py'),
        ('P4_score','score.py'),('P4_verify','verify.py'),('P4_report','report.py')]

def run():
    require(read(OUT/'audits/P0-complete.json')['passed'],'P0 gate')
    if (OUT/'completion.json').exists():require(read(OUT/'completion.json')['status']!='stop_stage_gate','No automatic failed-stage retry')
    write(OUT/'supervisor.json',dict(pid=os.getpid(),start_unix=time.time(),Stage_B_authorized=False))
    for key,name in STAGES:
        if (OUT/'stages'/f'{key}.json').exists():
            require(read(OUT/'stages'/f'{key}.json')['passed'],'Cannot skip failed stage');continue
        with writable(OUT/'logs'/f'{key}.stdout.log').open('w',encoding='utf-8') as out, writable(OUT/'logs'/f'{key}.stderr.log').open('w',encoding='utf-8') as err:
            result=subprocess.run([sys.executable,str(Path(__file__).parent/name)],cwd=ROOT,stdout=out,stderr=err)
        require(result.returncode==0,'Stage failed, inspect immutable log: '+key)
    write(OUT/'supervisor-exit.json',dict(exit_code=0,end_unix=time.time()))

if __name__=='__main__':run()
