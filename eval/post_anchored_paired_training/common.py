"""Sealed data capabilities and CUDA-only transforms for the J experiment."""
from pathlib import Path
import hashlib
import json
import os
os.environ.setdefault('CUBLAS_WORKSPACE_CONFIG', ':4096:8')
import numpy as np
import pandas as pd
import torch

ROOT = Path(__file__).resolve().parents[2]
CODE = Path(__file__).resolve().parent
OLD = ROOT/'outputs/mechanism-conditioned-ssl-extend/run-01'
OUT = ROOT/'outputs/post-anchored-paired-training-extend/run-01'
DOC = ROOT/'docs/post-anchored-paired-training-extend'
PLAN = ROOT/'plan/post-anchored-task-aware-paired-regularization-plan-20261004.md'
W = ['W_up', 'W_down', 'P_up', 'P_down', 'R_up', 'R_down']
M = [f'm{i}' for i in range(6)]
ARMS = [f'J{i}' for i in range(8)]
SEEDS = [20260918, 20260919, 20260920]
PRIMARY = ['J0', 'J7', 'J6', 'J2', 'J3', 'J5']
CONDITIONS = {'J3': 'B4', 'J4': 'B5', 'J5': 'B6', 'J6': 'B5'}
FIT_FILES = ['common.py', 'prepare.py', 'models.py', 'objectives.py',
             'sampling.py', 'train.py', 'predict.py', 'engineering.py', 'test_core.py']


def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))


def write(p, obj):
    p = Path(p); p.parent.mkdir(parents=True, exist_ok=True)
    def convert(v):
        if isinstance(v, np.generic): return v.item()
        if isinstance(v, np.ndarray): return v.tolist()
        if isinstance(v, Path): return str(v)
        raise TypeError(type(v).__name__)
    tmp = p.with_name(p.name+'.partial')
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2,
                              default=convert, allow_nan=False), encoding='utf-8')
    os.replace(tmp, p)


def sha(p):
    h = hashlib.sha256()
    with Path(p).open('rb') as f:
        for block in iter(lambda: f.read(1024*1024), b''): h.update(block)
    return h.hexdigest()


def digest(v):
    return hashlib.sha256(json.dumps(v, sort_keys=True, ensure_ascii=False,
                                    separators=(',', ':')).encode()).hexdigest()


def state_hash(state):
    h = hashlib.sha256()
    for k, v in sorted(state.items()):
        h.update(k.encode()); h.update(v.detach().cpu().contiguous().numpy().tobytes())
    return h.hexdigest()


def device():
    if not torch.cuda.is_available(): raise RuntimeError('CUDA required; no CPU fallback')
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    torch.use_deterministic_algorithms(True)
    return torch.device('cuda')


def tensor(v, dtype=torch.float32):
    return torch.as_tensor(v, dtype=dtype, device=device())


def fit_scale(v, log=False):
    x = tensor(v, torch.float64)
    if log: x = torch.log1p(x)
    mean, scale = x.mean(0), x.std(0, unbiased=False)
    return {'mean': mean.cpu().tolist(), 'scale': torch.where(scale < 1e-10, 1., scale).cpu().tolist(), 'log1p': log}


def scaled(v, spec):
    x = tensor(v, torch.float64)
    if spec['log1p']: x = torch.log1p(x)
    return ((x-tensor(spec['mean'], torch.float64))/tensor(spec['scale'], torch.float64)).float()


def source_frame(folder, key):
    item = read(folder/'manifest.json')['files'][key]; p = folder/item['filename']
    assert p.parent.resolve() == folder.resolve() and sha(p) == item['sha256']
    f = pd.read_parquet(p)
    assert len(f) == item['rows'] and list(f) == item['columns']
    return f


def export(folder, frames):
    folder.mkdir(parents=True, exist_ok=True)
    assert not (folder/'manifest.json').exists()
    info = {}
    for key, f in frames.items():
        p = folder/(key+'.parquet'); f.to_parquet(p, index=False)
        info[key] = {'filename': p.name, 'rows': len(f), 'columns': list(f), 'sha256': sha(p)}
    write(folder/'manifest.json', {'files': info})


class Bundle:
    """Exact software capabilities, not an OS filesystem sandbox."""
    def __init__(self, fold, arm):
        self.arm = arm; self.folder = OUT/'packages'/f'f{fold}'/arm
        self.access = []

    def get(self, key):
        allowed = ({'post'} if self.arm in ['J0', 'J7'] else {'post', 'pre'}
                   if self.arm in ARMS else {'test_post'} if self.arm == 'inference' else {'labels'})
        if key not in allowed: raise PermissionError((self.arm, key))
        if self.arm == 'scoring': assert (OUT/'prediction-seal.json').exists()
        f = source_frame(self.folder, key)
        if self.arm == 'inference': columns = ['session_id', *W]
        elif self.arm == 'scoring': columns = ['session_id', 'label_id']
        else:
            columns = ([] if self.arm == 'J5' else ['row_token'])+['deployment', 'group_id', 'label_id', *W]
            if key == 'pre' and self.arm in CONDITIONS: columns += M
        assert list(f) == columns, ('unexpected columns', self.arm, key)
        self.access.append(key); return f


def authorize(engineering=True):
    s = read(OUT/'seal.json')
    for name, expected in s['hashes'].items():
        assert sha(ROOT/name) == expected, 'sealed source changed: '+name
    assert sha(OUT/'contract.json') == s['contract_sha256']
    assert read(OUT/'qualification.json')['passed']
    if engineering: assert read(OUT/'engineering.json')['passed']
    device(); return read(OUT/'contract.json')


def complete(folder, data):
    write(folder/'complete.json', {**data, 'seal_sha256': sha(OUT/'seal.json'),
          'files': {p.name: sha(p) for p in folder.iterdir() if p.is_file() and p.name != 'complete.json'}})


def completed(folder):
    if not (folder/'complete.json').exists(): return False
    d = read(folder/'complete.json'); assert d['seal_sha256'] == sha(OUT/'seal.json')
    for n, h in d['files'].items(): assert sha(folder/n) == h
    return True
