"""Read-only nvidia-smi sampling, with distinct baseline/capture/train windows."""
from common import *
import subprocess
import threading

FIELDS=['timestamp','index','utilization.gpu','utilization.memory','memory.used','memory.total',
        'power.draw','temperature.gpu','clocks.sm']

class Sampler:
    def __init__(self,path):
        self.path=writable(path);self.rows=[];self.stop_event=threading.Event();self.lock=threading.Lock();self.window='baseline'
        self.thread=threading.Thread(target=self._loop,daemon=True)
    def start(self):self.thread.start();return self
    def label(self,window):
        with self.lock:self.window=window
    def _loop(self):
        while not self.stop_event.is_set():
            start=time.time()
            with self.lock:window=self.window
            try:
                p=subprocess.run(['nvidia-smi','--query-gpu='+','.join(FIELDS),'--format=csv,noheader,nounits'],
                     capture_output=True,text=True,timeout=5,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
                if p.returncode:raise RuntimeError(p.stderr)
                # This experiment admits cuda:0; log all physical GPUs, select index zero in summaries.
                for line in p.stdout.strip().splitlines():
                    vals=[v.strip() for v in line.split(',')];row=dict(zip(FIELDS,vals));row.update(unix=start,window=window,pid=os.getpid())
                    for key in FIELDS[1:]:
                        try:row[key]=float(row[key])
                        except ValueError:row[key]=None
                    self.rows.append(row)
            except Exception as e:self.rows.append(dict(unix=start,window=window,error=repr(e)))
            self.stop_event.wait(max(.1,1.-(time.time()-start)))
    def stop(self):
        self.stop_event.set();self.thread.join(timeout=7)
        require(not self.thread.is_alive(),'Telemetry thread did not stop')
        immutable(self.path,dict(interval_seconds=1,scope='whole GPU, includes desktop and other processes; not per-process utilization',samples=self.rows))
    def summary(self,window):
        rows=[r for r in self.rows if r['window']==window and r.get('index')==0 and 'error' not in r]
        result=dict(samples=len(rows))
        for key in ['utilization.gpu','utilization.memory','memory.used','power.draw','temperature.gpu','clocks.sm']:
            vals=[r[key] for r in rows if r.get(key) is not None]
            if vals:result[key]=dict(mean=float(np.mean(vals)),median=float(np.median(vals)),maximum=float(max(vals)),minimum=float(min(vals)))
        return result
