import sys,argparse
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'src'))
from proxy_analysis.cross_business_calibration.common import StageGate
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--stage',choices=['export','paired','group','gate'],required=True);a=p.parse_args()
    try:
        if a.stage=='export':
            from proxy_analysis.cross_business_calibration.export import export
            export()
        else:
            from proxy_analysis.cross_business_calibration.generate import run,gate
            gate() if a.stage=='gate' else run(a.stage)
    except StageGate as e:print(str(e),flush=True);sys.exit(2)
