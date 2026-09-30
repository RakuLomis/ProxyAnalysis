import json,hashlib
from pathlib import Path
import numpy as np
import pandas as pd
import yaml
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'outputs/cross-business-calibration-0916/run-01'
DOC=ROOT/'docs/cross-business-calibration-0916'
CONFIG=ROOT/'configs/cross-business-calibration-0916.yaml'
FEATURES=['U_up','U_down','E_up','E_down','R_up','R_down']
NUMERIC=FEATURES+['F']
IDENTITY=['session_id','content_id','protocol','repetition']
def config():return yaml.safe_load(CONFIG.read_text(encoding='utf-8'))
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def objhash(x):return hashlib.sha256(json.dumps(x,sort_keys=True).encode()).hexdigest()
def write(p,x):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);t=p.with_suffix('.tmp')
    t.write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8');t.replace(p)
def save(name,x):
    if not isinstance(x,pd.DataFrame):x=pd.DataFrame(x)
    OUT.mkdir(parents=True,exist_ok=True);x.to_parquet(OUT/(name+'.parquet'),index=False,compression='zstd');return x
def table(x):return x.to_markdown(index=False,floatfmt='.6f')
class Bundle:
    def __init__(self,path,kind='paired'):
        self.path=Path(path);self.kind=kind;self.manifest=read(self.path/'manifest.json');self.access=[]
        self.allowed={'paired':{'C_pre','C_post','U_pre','labels'},'group':{'G_pre','G_post','U_pre'}}[kind]
    def get(self,name):
        if name not in self.allowed:raise PermissionError('Forbidden role: '+name)
        f=self.manifest['files'][name];p=self.path/f['filename'];assert p.parent==self.path and sha(p)==f['sha256']
        self.access.append(name);return pd.read_parquet(p)
class StageGate(RuntimeError):pass
