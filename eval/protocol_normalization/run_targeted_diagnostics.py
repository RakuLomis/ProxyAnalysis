"""Run the targeted diagnostics; no training entry point is provided."""
import os
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[2]
env = dict(os.environ, PYTHONPATH=str(root/'src'))
subprocess.run([sys.executable, '-m', 'proxy_analysis.protocol_normalization.targeted_diagnostics.run', *sys.argv[1:]],
               cwd=root, env=env, check=True)
