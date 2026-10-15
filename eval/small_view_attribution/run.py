"""Bounded stage runner; never retries failed numerical terminals."""
from pathlib import Path
import subprocess
import sys

STAGES=[('inventory.py',[]),('tests.py',[]),('prepare.py',['pilot']),('formal.py',['pilot']),
        ('formal.py',['gate']),('prepare.py',['remaining']),('formal.py',['remaining']),
        ('formal.py',['seal']),('formal.py',['predict']),('score.py',[]),('concentration.py',[]),
        ('compatibility.py',[]),('observation_audit.py',[]),('report.py',[]),('verify.py',[])]

def run():
    here=Path(__file__).resolve().parent
    for file,args in STAGES:
        print('RUN',file,*args,flush=True)
        subprocess.run([sys.executable,str(here/file),*args],check=True,cwd=here.parents[1])

if __name__=='__main__':run()
