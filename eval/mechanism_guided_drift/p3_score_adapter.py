"""Output-only NumPy scalar repair; sealed scorer, models and statistics unchanged."""
from pathlib import Path
import numpy as np
import p3_score
from p3_common import OUT, read, write, file_hash


def native(value):
    if isinstance(value,np.generic):return value.item()
    if isinstance(value,dict):return {key:native(item) for key,item in value.items()}
    if isinstance(value,(list,tuple)):return [native(item) for item in value]
    return value


if __name__=='__main__':
    assert native({'seed':np.int64(20260918),'matrix':[[np.float64(1)]]})=={'seed':20260918,'matrix':[[1.]]}
    assert not (OUT/'score-complete.json').exists()
    seal=read(OUT/'prediction-seal.json');before=file_hash(Path(p3_score.__file__))
    write(OUT/'scoring-serialization-repair.json',{'reason':'NumPy int64 group seed not JSON serializable',
        'scope':'equivalent scalar conversion at JSON output only','model_or_metric_changed':False,
        'frozen_score_sha256':before,'predictions_sha256':seal['sha256'],'adapter_sha256':file_hash(Path(__file__)),
        'refit':False,'bootstrap_or_contrasts_changed':False})
    original=p3_score.write;p3_score.write=lambda path,value:original(path,native(value))
    p3_score.main()
    assert file_hash(Path(p3_score.__file__))==before
    assert file_hash(OUT/'predictions.parquet')==seal['sha256']
