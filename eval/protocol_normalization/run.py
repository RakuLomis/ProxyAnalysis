"""Run only the approved measurement stages; no model training entry point."""
import argparse
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('stage', choices=['inventory','measure','evaluate','all'])
    args = parser.parse_args()
    stages = ['inventory','measure','evaluate'] if args.stage == 'all' else [args.stage]
    for stage in stages:
        subprocess.run([sys.executable,'-m','proxy_analysis.protocol_normalization.'+stage],
                       cwd=ROOT, env={**os.environ,'PYTHONPATH':str(ROOT/'src')}, check=True)


if __name__ == '__main__':
    main()
