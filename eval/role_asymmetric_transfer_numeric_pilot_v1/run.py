"""NR1 N0-N4 only. Never dispatch the full RA1 classifier matrix."""
from common import *
import common as C

def main():
    C.START=time.perf_counter();lock=writable(OUT/'run.lock')
    fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY);os.write(fd,str(os.getpid()).encode());os.close(fd)
    stop=None
    try:
        require(not (OUT/'completion.json').exists(),'Pilot already closed; no automatic replay')
        configure()
        import register,tests,pilot,verify
        register.run();tests.run();pilot.n2();pilot.n3();verify.run()
    except BaseException as exc:
        stop=dict(type=type(exc).__name__,exception=str(exc),traceback=traceback.format_exc(),time_unix=time.time(),activity_seconds=elapsed(),automatic_retry=False)
        write(OUT/'stop.json',stop);progress('pilot_stopped',reason=stop['exception'])
    finally:
        import report
        try:report.closeout(stop)
        finally:
            if lock.exists() and lock.read_text()==str(os.getpid()):lock.unlink()
    if stop:sys.exit(2)

if __name__=='__main__':main()
