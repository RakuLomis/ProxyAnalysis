import os
from pathlib import Path
import subprocess
import sys
root=Path(__file__).resolve().parents[2]
subprocess.run([sys.executable,'-m','proxy_analysis.protocol_normalization.record_representation.run',*sys.argv[1:]],
               cwd=root,env=dict(os.environ,PYTHONPATH=str(root/'src')),check=True)
