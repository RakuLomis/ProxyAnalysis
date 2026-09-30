"""Finite, resumable v3 batch runner; no scheduler, threshold search or silent recovery."""
import argparse,subprocess,sys,time,traceback,os
from pathlib import Path
from datetime import datetime,timezone
from formal_common import OUT,ROOT,read,write,sha,freeze,contract_path

STAGES=[('generation-engineering','formal_generate.py','engineering'),
        ('generation','formal_generate.py','generate'),('generation-gate','formal_generate.py','gate'),
        ('classification-engineering','formal_classify.py','engineering'),
        ('restricted-training','formal_classify.py','restricted'),('restricted-inference','formal_classify.py','infer'),
        ('reference-training','formal_classify.py','reference'),('reference-inference','formal_classify.py','infer-reference'),
        ('statistics','formal_score.py',None)]

def now():return datetime.now(timezone.utc).isoformat()

def check_prior_failure():
    if (OUT/'generation-failure-revision-02.json').exists():
        raise RuntimeError('Unresolved revision-02 generation failure; no automatic retry')
    prior=OUT/'generation-failure.json'
    if prior.exists():
        registry=OUT/'repair-02/compatibility.json';contract=read(contract_path())
        assert sha(registry)==contract['repair']['compatibility_sha256']
        assert sha(prior)==read(registry)['resolved_failure_sha256'],'Unregistered historical failure'

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--wait-pid',type=int);args=parser.parse_args()
    OUT.mkdir(parents=True,exist_ok=True);lock=OUT/'runner.lock'
    # Exclusive lock prevents two resume runners from writing the same model directories.
    fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY);os.write(fd,str(os.getpid()).encode());os.close(fd)
    journal=[];stage='wait-for-active-generation'
    try:
        freeze();check_prior_failure()
        if args.wait_pid:
            import psutil
            try:process=psutil.Process(args.wait_pid)
            except psutil.NoSuchProcess:process=None
            if process:
                command=process.cmdline()
                assert any('formal_generate.py' in s for s in command) and command[-1]=='generate'
                write(OUT/'pipeline-progress.json',{'status':'running','stage':stage,'pid':os.getpid(),'wait_pid':args.wait_pid,'updated':now()})
                while True:
                    try:process.wait(timeout=30);break
                    except psutil.TimeoutExpired:pass
            check_prior_failure()
        for stage,script,argument in STAGES:
            write(OUT/'pipeline-progress.json',{'status':'running','stage':stage,'pid':os.getpid(),'updated':now(),'completed':journal})
            command=[sys.executable,str(Path(__file__).parent/script)]+(['--stage',argument] if argument else [])
            log=OUT/(stage+'.log');started=now();print('START',stage,started,flush=True)
            with log.open('a',encoding='utf-8') as handle:
                handle.write('\nRUN '+started+'\n');handle.flush()
                result=subprocess.run(command,cwd=ROOT,stdout=handle,stderr=subprocess.STDOUT)
            if result.returncode:raise RuntimeError(f'{stage} exit {result.returncode}; inspect {log}')
            journal.append({'stage':stage,'started':started,'completed':now(),'log_sha256':sha(log)})
            print('DONE',stage,flush=True)
        write(OUT/'pipeline-progress.json',{'status':'complete','updated':now(),'completed':journal})
    except BaseException as error:
        write(OUT/'pipeline-progress.json',{'status':'failed','stage':stage,'updated':now(),'error':repr(error),'completed':journal})
        traceback.print_exc();raise
    finally:
        # Only removes this runner's own tiny lock, never data/model artifacts.
        if lock.read_text()==str(os.getpid()):lock.unlink()

if __name__=='__main__':main()
