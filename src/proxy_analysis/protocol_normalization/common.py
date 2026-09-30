from pathlib import Path
import hashlib
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT/'outputs/protocol-normalization-0914-0916/run-01'
DOC = ROOT/'docs/protocol-normalization'


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda: f.read(4*1024*1024), b''):
            h.update(b)
    return h.hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(name, rows):
    OUT.mkdir(parents=True, exist_ok=True)
    df = rows if isinstance(rows, pd.DataFrame) else pd.DataFrame(rows)
    df.to_parquet(OUT/name, index=False, compression='zstd')
    return df


def markdown(name, text):
    DOC.mkdir(parents=True, exist_ok=True)
    (DOC/name).write_text(text.rstrip()+'\n', encoding='utf-8')
