import argparse,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'src'))
from proxy_analysis.calibration_budget.common import StageGate
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--stage',choices=['export','generate'],required=True);a=p.parse_args()
    try:
        if a.stage=='export':
            from proxy_analysis.calibration_budget.export import export
            export()
        else:
            from proxy_analysis.calibration_budget.generate import run
            run()
    except StageGate as e:
        print('USER CONFIRMATION REQUIRED:',e,flush=True);raise SystemExit(2)
