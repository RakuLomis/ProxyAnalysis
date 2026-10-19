"""Read-only GPU sampling alongside NER1; never imports training/data modules."""
import csv,json,time,subprocess,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[1]
out=root/'outputs/deproxy-moment-game-v1-20261016/numeric-repair-01'
path=out/'gpu-observation.csv'
with path.open('x',newline='',encoding='utf-8') as f:
    w=csv.writer(f);w.writerow(['unix','stage','gpu_percent','memory_percent','memory_MiB','power_W'])
    deadline=time.monotonic()+14400
    while time.monotonic()<deadline:
        if (out/'completion.json').exists():break
        try:
            stage=json.loads((out/'progress.json').read_text(encoding='utf-8'))['stage']
            r=subprocess.run(['nvidia-smi','--query-gpu=utilization.gpu,utilization.memory,memory.used,power.draw','--format=csv,noheader,nounits'],capture_output=True,text=True,timeout=5)
            if r.returncode==0:w.writerow([time.time(),stage,*[v.strip() for v in r.stdout.strip().split(',')]]);f.flush()
        except (OSError,ValueError,subprocess.TimeoutExpired):pass
        time.sleep(1)
print('GPU observation ended',flush=True)
