"""Documented output-only repair for NumPy group-key JSON serialization.

Leaves frozen score.py, predictions, all metrics and bootstrap unchanged.
"""
from pathlib import Path
import numpy as np
import score
from common import OUT, read, write, file_hash


def native(value):
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, dict):
        return {key: native(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [native(item) for item in value]
    return value


if __name__=='__main__':
    assert native({'seed':np.int64(20260918),'matrix':[[np.float64(1)]]})=={'seed':20260918,'matrix':[[1.0]]}
    assert not (OUT/'score-complete.json').exists()
    seal=read(OUT/'prediction-seal.json')
    write(OUT/'scoring-serialization-repair.json',{
        'reason':'Frozen score.py failed writing confusion-matrices.json: NumPy int64 group seed is not JSON serializable',
        'scope':'Convert NumPy scalar objects to equivalent Python scalars only at JSON output boundary',
        'model_or_metric_changes':False,'frozen_code_changed':False,'predictions_sha256':seal['sha256'],
        'adapter_sha256':file_hash(Path(__file__))})
    original_write=score.write
    score.write=lambda path,value: original_write(path,native(value))
    score.main()
