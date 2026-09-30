"""Run E00--E06 qualification; never fits or exports learning data."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from proxy_analysis.extend_calibration.audit import main

if __name__ == "__main__":
    main(ROOT)
