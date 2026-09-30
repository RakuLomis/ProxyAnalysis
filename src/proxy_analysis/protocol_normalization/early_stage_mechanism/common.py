from pathlib import Path
import hashlib
import json
import pandas as pd
from ..common import ROOT, OUT as BASE, digest

PREVIOUS=ROOT/'outputs/protocol-normalization-targeted-diagnostics-0914-0916/run-01'
OUT=ROOT/'outputs/vless-early-stage-mechanism-0914-0916/run-01'
DOC=ROOT/'docs/protocol-normalization/early-stage-mechanism-20260923'
CONFIG=ROOT/'configs/vless-early-stage-mechanism-20260923.yaml'
PLAN=ROOT/'plan/vless-early-stage-mechanism-plan-20260923.md'
SEED='early-stage-v1'
COMMIT='fcacc8696dfd574d0faa2770c5d3151e21dd9bbc'

def stable(text):return hashlib.sha256((SEED+'|'+str(text)).encode()).hexdigest()
def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def js(name,obj):
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def save(name,rows):
    OUT.mkdir(parents=True,exist_ok=True)
    f=rows if isinstance(rows,pd.DataFrame) else pd.DataFrame(rows)
    f.to_parquet(OUT/(name+'.parquet'),index=False,compression='zstd');return f
def load(name):return pd.read_parquet(OUT/(name+'.parquet'))
def freeze():
    files=[*BASE.glob('*.parquet'),*BASE.glob('*.json'),*PREVIOUS.glob('*.parquet'),*PREVIOUS.glob('*.json'),CONFIG,PLAN,
           ROOT/'outputs/content-generalization-20260916/business-01/primary-cohort.parquet']
    obj={str(f):digest(f) for f in sorted(files)}
    if (OUT/'contract.json').exists():assert read(OUT/'contract.json')['inputs']==obj,'frozen input changed'
    js('contract.json',{'inputs':obj,'classifier_fits':0});js('input-manifest.json',obj)

