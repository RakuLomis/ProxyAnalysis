"""One-shot OS-managed supervisor; no retry and no scientific computation."""
from pathlib import Path
import json
import os
import subprocess
import time

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'outputs/dynamic-soft-drift-qualified-policy-business-20261013/run-02'
TASK='ProxyAnalysis-qualified-policy-run02-20261013'
PYTHON=Path('D:/Tools/Anaconda/envs/Pytorch312/python.exe')

def write(name,value):
    p=OUT/name;tmp=p.with_name(p.name+'.tmp');tmp.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');os.replace(tmp,p)

def main():
    began=time.time();base=json.loads((OUT/'ledger.json').read_text())['active_seconds']
    deadline=began+max(0,72000-base)+7200 # reporting allowance, NOT an increased compute budget
    flags=subprocess.CREATE_NO_WINDOW
    worker=None
    try:
        with (OUT/'runner.stdout.log').open('ab',buffering=0) as stdout,(OUT/'runner.stderr.log').open('ab',buffering=0) as stderr:
            worker=subprocess.Popen([str(PYTHON),'-u',str(ROOT/'eval/dynamic_soft_drift_qualified_policy_v2/run.py'),'execute'],cwd=ROOT,stdout=stdout,stderr=stderr,creationflags=flags)
            write('supervisor.json',dict(status='running',pid=os.getpid(),worker_pid=worker.pid,started_unix=began,scheduled_task=TASK,automatic_restart=False,compute_seconds_cap=72000,inherited_active_seconds=base))
            while worker.poll() is None:
                write('supervisor-heartbeat.json',dict(time_unix=time.time(),pid=os.getpid(),worker_pid=worker.pid,worker_running=True))
                if time.time()>deadline:
                    worker.terminate();worker.wait(timeout=30)
                    write('supervisor-exit.json',dict(status='watchdog_deadline',exit_code=worker.returncode,automatic_restart=False,reason='Compute remainder plus fixed reporting allowance exhausted'))
                    break
                time.sleep(10)
            else:
                write('supervisor-exit.json',dict(status='worker_exited',exit_code=worker.returncode,time_unix=time.time(),elapsed_seconds=time.time()-began,automatic_restart=False))
    except BaseException as exc:
        write('supervisor-exit.json',dict(status='supervisor_error',exception=repr(exc),worker_pid=None if worker is None else worker.pid,automatic_restart=False))
        raise
    finally:
        cleanup=subprocess.run(['schtasks.exe','/Delete','/TN',TASK,'/F'],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,creationflags=flags,timeout=30)
        write('scheduled-task-cleanup.json',dict(task=TASK,exit_code=cleanup.returncode,removed=cleanup.returncode==0))

if __name__=='__main__':main()


