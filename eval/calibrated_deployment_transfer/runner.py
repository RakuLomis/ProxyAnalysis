"""Ordered resumable stage driver; fail closed, never change the registered methods."""
import os
os.environ.setdefault('CUBLAS_WORKSPACE_CONFIG', ':4096:8')
os.environ['PYTHONIOENCODING'] = 'utf-8'
import subprocess
import sys
import traceback
from common import *

STAGES = [
    ('diagnostics.py', 'inner-fit'), ('diagnostics.py', 'select'), ('diagnostics.py', 'outer-fit'),
    ('diagnostics.py', 'predict'), ('diagnostics.py', 'kernels'), ('diagnostics.py', 'score'),
    ('report.py', 'diagnostics'), ('representation.py', 'kernels'), ('representation.py', 'slots'),
    ('representation.py', 'profile'),
    ('main_experiment.py', 'inner-fit'), ('main_experiment.py', 'inner-predict'), ('main_experiment.py', 'select'),
    ('main_experiment.py', 'outer-fit'), ('main_experiment.py', 'predict'), ('score.py', 'score'),
    ('score.py', 'explain'), ('report.py', 'observation'), ('plots.py', ''), ('verify.py', ''), ('report.py', 'final')]

def run():
    configure(); c = contract(); lock = OUT/'runner.lock'
    # Exclusive process lock; an interrupted run needs explicit stale-lock review before resume.
    fd = os.open(lock, os.O_CREAT|os.O_EXCL|os.O_WRONLY)
    os.write(fd, str(os.getpid()).encode()); os.close(fd)
    try:
        for index, (script, arg) in enumerate(STAGES):
            key = f'{index:02d}-{Path(script).stem}'+('-'+arg if arg else '')
            mark = OUT/'manifests/stages'/(key+'.json')
            if mark.exists():
                d = read(mark)
                require(d['contract_sha256'] == sha(OUT/'manifests/experiment-contract.json'), 'Stage contract mismatch')
                continue
            start('runner'); progress('running_'+key, pid=os.getpid(), stages_completed=index, stages_total=len(STAGES))
            cmd = [sys.executable, '-u', str(Path(__file__).parent/script)]+([arg] if arg else [])
            subprocess.run(cmd, cwd=str(ROOT), env=os.environ.copy(), check=True)
            complete(mark, contract_sha256=sha(OUT/'manifests/experiment-contract.json'), stage=key)
        files = {rel(p): sha(p) for p in DOC.glob('*.md')}
        complete(OUT/'completion.json', stages=len(STAGES), numerical_stages_complete=True,
                 source_sha256=c['source_sha256'], report_sha256=files,
                 stage3_status='needs_external_window_and_complete_physical_extraction_contract',
                 no_new_capture=True, stopped_without_method_search=True)
        progress('CT40_CT47_CT48_done_stage3_needs_confirmation', numerical_experiments_complete=True,
                 physical_only_extraction_complete=False)
    except BaseException as e:
        write(OUT/'failure.json', {'time_unix': time.time(), 'type': type(e).__name__, 'message': str(e),
                                  'traceback': traceback.format_exc(), 'methods_changed': False})
        progress('engineering_stop', error=str(e)); raise
    finally:
        # Only delete this process's own explicitly created lock, not an artifact tree.
        if lock.exists() and lock.read_text() == str(os.getpid()): lock.unlink()

if __name__ == '__main__': run()
