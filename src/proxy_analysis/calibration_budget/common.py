import json,hashlib
from pathlib import Path
import numpy as np
import pandas as pd
import yaml

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'outputs/paired-calibration-budget-0916/run-01'
DOC=ROOT/'docs/paired-calibration-budget-0916'
CONFIG=ROOT/'configs/paired-calibration-budget-0916.yaml'
FEATURES=['U_up','U_down','E_up','E_down','R_up','R_down']
NUMERIC=FEATURES+['F']
IDENTITY=['session_id','content_id','protocol','repetition']
def config():return yaml.safe_load(CONFIG.read_text(encoding='utf-8'))
def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def objhash(x):return hashlib.sha256(json.dumps(x,sort_keys=True).encode()).hexdigest()
def write(path,x):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_suffix('.tmp')
    tmp.write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8');tmp.replace(path)
def save(name,x):
    x=x if isinstance(x,pd.DataFrame) else pd.DataFrame(x);OUT.mkdir(parents=True,exist_ok=True)
    x.to_parquet(OUT/(name+'.parquet'),index=False,compression='zstd');return x
def table(x):return x.to_markdown(index=False,floatfmt='.6f')

class TrainingBundle:
    """Explicit allowlist, not an OS-level security sandbox."""
    allowed={'C_pre','C_post','U_pre','labels'}
    def __init__(self,path):
        self.path=Path(path);self.manifest=read(self.path/'manifest.json');self.access=[]
    def get(self,name):
        if name not in self.allowed:raise PermissionError('Training access forbidden: '+name)
        r=self.manifest['files'][name];path=self.path/r['filename']
        assert path.parent==self.path and sha(path)==r['sha256']
        self.access.append(name);return pd.read_parquet(path)

class StageGate(RuntimeError):pass
