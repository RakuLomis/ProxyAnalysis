"""Verify trusted export, then freeze generation dependencies before execution."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'src'))
from proxy_analysis.calibration_budget.common import *
contract=read(OUT/'contract.json')
for path,h in contract['inputs'].items():assert sha(path)==h
files=[ROOT/'src/proxy_analysis/conditional_drift/model.py',ROOT/'src/proxy_analysis/conditional_drift/common.py',
       *Path(ROOT/'src/proxy_analysis/calibration_budget').glob('*.py'),CONFIG,Path(__file__),
       *list((OUT/'bundles').glob('*/manifest.json'))]
state={'inputs':{str(p):sha(p) for p in files},'device':'cuda','classification_started':False,'training_access':['C_pre','C_post','U_pre'],'generator_label_access':False}
path=OUT/'worker-contract.json'
if path.exists():assert read(path)==state
else:write(path,state)
print('Worker contract frozen; original input hashes verified',flush=True)
