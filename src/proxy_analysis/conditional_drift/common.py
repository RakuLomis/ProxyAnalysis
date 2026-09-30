import json,hashlib
from pathlib import Path
import numpy as np
import pandas as pd
import yaml

ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'outputs/protocol-normalization-0914-0916/run-01'
BUS=ROOT/'outputs/content-generalization-20260916/business-01'
PREP=ROOT/'outputs/content-generalization-20260916/natural-pair-ssl-01/prepared'
OUT=ROOT/'outputs/conditional-proxy-drift-0916/run-01'
DOC=ROOT/'docs/conditional-proxy-drift-0916'
CONFIG=ROOT/'configs/conditional-proxy-drift-0916.yaml'
PLAN=ROOT/'plan/conditional-proxy-drift-forward-plan-20260926.md'
FEATURES=['U_up','U_down','E_up','E_down','R_up','R_down']

def config():return yaml.safe_load(CONFIG.read_text(encoding='utf-8'))
def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for part in iter(lambda:f.read(1024*1024),b''):h.update(part)
    return h.hexdigest()
def object_hash(value):return hashlib.sha256(json.dumps(value,sort_keys=True).encode()).hexdigest()
def js(name,value):
    OUT.mkdir(exist_ok=True,parents=True)
    p=OUT/name;t=p.with_suffix(p.suffix+'.tmp')
    t.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8');t.replace(p)
def save(name,rows):
    x=rows if isinstance(rows,pd.DataFrame) else pd.DataFrame(rows)
    OUT.mkdir(exist_ok=True,parents=True);x.to_parquet(OUT/(name+'.parquet'),index=False,compression='zstd');return x
def load(name,base=OUT):return pd.read_parquet(base/(name+'.parquet'))
def table(frame):return frame.to_markdown(index=False,floatfmt='.6f')

class StageGate(RuntimeError):pass

def illegal(x,F):
    """Necessary summary constraints, not proof of TCP realizability."""
    x=np.asarray(x,dtype=float)
    if x.shape!=(6,) or not np.isfinite(x).all():return 'nonfinite_or_shape'
    if not np.isfinite(F) or F<1 or F!=round(F):return 'invalid_F'
    if (x<0).any():return 'negative'
    if (x>9007199254740991).any():return 'integer_overflow'
    if not np.equal(x,np.rint(x)).all():return 'noninteger'
    U,E,R=x[:2],x[2:4],x[4:6]
    if (E>U).any() or (R>E).any():return 'R_E_U_order'
    if ((U>0)&((E<1)|(R<1))).any() or ((U==0)&((E!=0)|(R!=0))).any():return 'zero_positive_mismatch'
    if R.sum()<F:return 'runs_below_connections'
    if abs(R[0]-R[1])>F:return 'direction_imbalance'
    return ''
