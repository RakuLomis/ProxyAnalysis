import sys,argparse
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'src'))
from proxy_analysis.conditional_drift.data import freeze,prepare
from proxy_analysis.conditional_drift.common import StageGate

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--stage',choices=['prepare','generate','all'],default='all');a=p.parse_args()
    freeze()
    try:
        if a.stage in ['prepare','all']:prepare()
        if a.stage in ['generate','all']:
            from proxy_analysis.conditional_drift.generate import run
            run()
    except StageGate as error:
        print('USER CONFIRMATION REQUIRED:',error,flush=True)
        raise SystemExit(2)
