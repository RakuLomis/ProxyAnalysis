from ..cross_business_calibration.common import ROOT,FEATURES,NUMERIC,IDENTITY,read,sha,objhash,write,table,Bundle,StageGate
from pathlib import Path
import json
import numpy as np
import pandas as pd
import yaml
SOURCE=ROOT/'outputs/cross-business-calibration-0916/run-01'
OUT=ROOT/'outputs/feasible-summary-calibration-0916/run-01'
DOC=ROOT/'docs/feasible-summary-calibration-0916'
CONFIG=ROOT/'configs/feasible-summary-calibration-0916.yaml'
def config():return yaml.safe_load(CONFIG.read_text(encoding='utf-8'))
def save(name,x):
    if not isinstance(x,pd.DataFrame):x=pd.DataFrame(x)
    OUT.mkdir(parents=True,exist_ok=True);x.to_parquet(OUT/(name+'.parquet'),index=False,compression='zstd');return x
