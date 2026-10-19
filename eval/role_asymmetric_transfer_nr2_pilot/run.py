"""Authorized bounded NR2 only. Does not import full inference or scoring."""
import time
LOAD_START=time.perf_counter()
from common import *
import common as C

def main():
    C.START=LOAD_START
    require(not (OUT/'completion.json').exists() and not (OUT/'failure.json').exists(),'Terminal NR2 run; no automatic retry')
    lock=pathout(OUT/'run.lock');fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY);os.write(fd,str(os.getpid()).encode());os.close(fd)
    success=False
    try:
        initialize_costs();configure();register()
        import tests,pilot,report
        tests.run();pilot.run();pilot.verify()
        summary=report.run(True)
        require(C.PILOT_PRIOR+time.perf_counter()-C.START<1800,'Closeout exceeded activity limit')
        write(OUT/'completion.json',dict(**summary,verification_sha256=sha(OUT/'verification.json'),report_sha256=sha(DOC/'complete-report-20261018.md')))
        success=True;progress('NR2_complete_waiting_for_user',unique_cases=52,optimization_attempts=len(C.ATTEMPTS),full_matrix_started=False)
    except BaseException as exc:
        err=dict(type=type(exc).__name__,exception=str(exc),traceback=traceback.format_exc(),automatic_retry=False,
                 full_matrix_started=False,time_unix=time.time())
        write(OUT/'failure.json',err)
        if C.ATTEMPTS and C.ATTEMPTS[-1]['status']=='running':end(C.ATTEMPTS[-1],status='failed',exception=str(exc))
        import report
        report.run(False,error=str(exc));print(traceback.format_exc(),flush=True)
    finally:
        elapsed=time.perf_counter()-C.START
        write(OUT/'cost-final.json',dict(pilot_activity_seconds=C.PILOT_PRIOR+elapsed,current_process_activity_seconds=elapsed,
              earlier_NR2_registration_stop_seconds=C.PILOT_PRIOR,pilot_cap_seconds=1800,parent_prior_charged_seconds=C.PRIOR,
              parent_cumulative_active_seconds=(C.PRIOR or 0)+elapsed,parent_cap_seconds=28800,success=success,
              optimization_attempts=len(C.ATTEMPTS),full_matrix_started=False))
        if lock.exists() and lock.read_text()==str(os.getpid()):lock.unlink()
    return 0 if success else 1

if __name__=='__main__':raise SystemExit(main())
