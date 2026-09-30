"""HFC-W shared constants and allowlisted packages. No automatic dataset reads."""
from pathlib import Path
import json, hashlib, sys
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
from proxy_analysis.conditional_drift.model import torch,device
OUT=ROOT/'outputs/hy2-window-calibration-0916/run-01'
PRIOR=ROOT/'outputs/hy2-carrier-calibration-0916/run-02'
DOC=ROOT/'docs/hy2-window-calibration-0916'
FEATURES=['W_up','W_down','P_up','P_down','R_up','R_down']
SEEDS=[20260918,20260919,20260920]
ARMS=['raw','center','marginal','paired','cyclic','group']
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
def save(name,v):
    f=v if isinstance(v,pd.DataFrame) else pd.DataFrame(v)
    f.to_parquet(OUT/(name+'.parquet'),index=False);return f
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True).encode()).hexdigest()
def table(f):return f.to_markdown(index=False,floatfmt='.6f')

class Bundle:
    def __init__(self,folder,kind):
        self.folder=Path(folder);self.meta=read(self.folder/'manifest.json');self.kind=kind;self.access=[]
        assert self.meta['kind']==kind
    def get(self,name):
        allowed={'paired':{'C_pre','C_post','U_pre','labels'},'group':{'C_pre','C_post','U_pre'}}
        if name not in allowed[self.kind]:raise PermissionError(name)
        p=self.folder/(name+'.parquet');assert sha(p)==self.meta['hashes'][name]
        self.access.append(name);return pd.read_parquet(p)
