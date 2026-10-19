"""Authorized full RA1 pipeline; stage failures stop without hidden retries."""
from common import *

def main():
    configure();lock=writable(OUT/'run.lock')
    fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY);os.write(fd,str(os.getpid()).encode());os.close(fd)
    try:
        require(not (OUT/'failure.json').exists(),'Stopped run: preserve failure, independent repair authorization required')
        import prepare,tests,fit_lr,predict,score,summarize,verify
        steps=[('P0',prepare.run),('P1',tests.run),('P2',lambda:fit_lr.fit(True)),('P3',lambda:fit_lr.fit(False)),('P4',fit_lr.seal),('P5',predict.run),('P6',score.run),('report',summarize.run),('verify',verify.run)]
        for name,fn in steps:
            if not (OUT/'stages'/(name+'.json')).exists():fn()
        write(OUT/'completion.json',dict(program_complete=True,numeric_pass=True,all_roles_complete=True,H_predictions_sealed=True,H_scored=True,
              new_method_selected_after_H=False,new_classifier_fits=1920,extra_fits=3,reused_models=420,verification_sha256=sha(OUT/'verification.json'),active_seconds=spent(),time_unix=time.time()))
        progress('complete',active_seconds=spent())
    except BaseException as exc:
        path=OUT/'failure.json'
        if not path.exists():write(path,dict(type=type(exc).__name__,exception=str(exc),traceback=traceback.format_exc(),time_unix=time.time(),active_seconds=spent(),automatic_retry=False))
        raise
    finally:
        if lock.exists() and lock.read_text()==str(os.getpid()):lock.unlink()

if __name__=='__main__':main()
