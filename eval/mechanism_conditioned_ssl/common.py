"""Independent paths, sealed capabilities, and CUDA-only numeric transforms."""
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
OLD = ROOT / 'outputs/mechanism-guided-drift-20261003/experiment/run-01'
OUT = ROOT / 'outputs/mechanism-conditioned-ssl-extend/run-01'
PLAN = ROOT / 'plan/mechanism-conditioned-paired-ssl-atomic-plan-20261004.md'
W = ['W_up', 'W_down', 'P_up', 'P_down', 'R_up', 'R_down']
AUX = ['log_entities_up', 'log_entities_down', 'log_q50_up', 'log_q50_down',
       'log_q90_up', 'log_q90_down', 'small_ratio_up', 'small_ratio_down']
M = [f'm{i}' for i in range(6)]
SEEDS = [20260918, 20260919, 20260920]
SSL = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6']
ARMS = ['B0', 'B0L', *SSL]
SOURCES = ['R0', *SSL]
PRIMARY = ['B0', 'B0L', 'B1', 'B4', 'B6']
CENTERS = {'B4': 'D1_pair', 'B5': 'D2_pair', 'B6': 'D2_group'}


def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))


def write(p, obj):
    p = Path(p); p.parent.mkdir(parents=True, exist_ok=True)
    # Boundary conversion only; no altered values or statistic selection.
    def convert(v):
        if isinstance(v, np.generic): return v.item()
        if isinstance(v, np.ndarray): return v.tolist()
        if isinstance(v, Path): return str(v)
        raise TypeError(type(v).__name__)
    tmp = p.with_name(p.name + '.partial')
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2, default=convert,
                              allow_nan=False), encoding='utf-8')
    os.replace(tmp, p)


def sha(p):
    h = hashlib.sha256()
    with Path(p).open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''): h.update(chunk)
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
    return torch.as_tensor(v, device=device(), dtype=dtype)


def validate(x):
    x = tensor(x, torch.float64); w, p, r = x[..., :2], x[..., 2:4], x[..., 4:]
    assert torch.isfinite(x).all() and (x >= 0).all() and (x == x.round()).all()
    assert (r <= p).all() and (p <= w).all() and (w <= 65527*p).all()
    assert (r.sum(-1) >= 1).all() and ((r[..., 0]-r[..., 1]).abs() <= 1).all()
    assert ((r == 0) == (p == 0)).all() and ((p == 0) == (w == 0)).all()
    return x


def phi(x):
    """Exact frozen window_model.encode formula; reference hash is sealed."""
    x = validate(x); w, p, r = x[..., :2], x[..., 2:4], x[..., 4:]
    h = w-p; capacity = 65526*p
    return torch.cat([torch.log(r.sum(-1, keepdim=True)-.5),
                      torch.asinh(r[..., 0:1]-r[..., 1:2]),
                      torch.log(p-r+.5), torch.log(h+.5)-torch.log(capacity-h+.5)], -1)


def fit_scale(values, log=False):
    x = tensor(values, torch.float64)
    if log: x = torch.log1p(x)
    mean, scale = x.mean(0), x.std(0, unbiased=False)
    scale = torch.where(scale < 1e-10, 1., scale)
    return {'mean': mean.cpu().tolist(), 'scale': scale.cpu().tolist(), 'log1p': log}


def scaled(values, spec):
    x = tensor(values, torch.float64)
    if spec['log1p']: x = torch.log1p(x)
    return ((x-tensor(spec['mean'], torch.float64))/tensor(spec['scale'], torch.float64)).float()


def source_frame(folder, key):
    manifest = read(folder/'manifest.json'); item = manifest['files'][key]
    path = folder/item['filename']; assert path.parent.resolve() == folder.resolve()
    assert sha(path) == item['sha256']
    frame = pd.read_parquet(path)
    assert len(frame) == item['rows'] and list(frame) == item['columns']
    return frame


def export(folder, frames):
    folder.mkdir(parents=True, exist_ok=True); assert not (folder/'manifest.json').exists()
    meta = {}
    for key, frame in frames.items():
        path = folder/(key+'.parquet'); frame.to_parquet(path, index=False)
        meta[key] = {'filename': path.name, 'columns': list(frame), 'rows': len(frame), 'sha256': sha(path)}
    write(folder/'manifest.json', {'files': meta})


class Bundle:
    """Capabilities are exact frames, not a claim of OS sandboxing."""
    KEYS = {'B1': {'post'}, 'B2': {'post', 'pre'},
            'B3': {'post', 'pre'}, 'B4': {'post', 'pre'},
            'B5': {'post', 'pre'}, 'B6': {'post', 'pre'},
            'supervised': {'post'}, 'inference': {'test_post'}, 'scoring': {'labels'},
            'diagnostic': {'train_pre', 'train_post', 'test_pre', 'test_post'}}
    def __init__(self, fold, capability):
        self.capability = capability
        self.folder = OUT/'packages'/f'f{fold}'/capability
        self.access = []

    def get(self, key):
        if key not in self.KEYS[self.capability]: raise PermissionError(key)
        if self.capability == 'diagnostic':
            assert (OUT/'prediction-seal.json').exists(), 'diagnostics require frozen business predictions'
        f = source_frame(self.folder, key)
        if self.capability == 'diagnostic':
            expected = ['session_id', 'deployment', 'group_id', *W, *AUX] if key.endswith('pre') else ['session_id', 'deployment', 'group_id', *W]
        else:
            expected = (['session_id', *W] if self.capability == 'inference' else
                    ['session_id', 'label_id'] if self.capability == 'scoring' else
                    ['session_id', 'deployment', 'group_id', 'label_id', *W]
                    if self.capability == 'supervised' else
                    ['row_token', 'deployment', 'group_id', *W, *M]
                    if key == 'pre' and self.capability in CENTERS else
                    ['row_token', 'deployment', 'group_id', *W])
        assert list(f) == expected, 'unexpected capability columns'
        self.access.append(key); return f


def authorize(engineering=True):
    s = read(OUT/'seal.json')
    for name, expected in s['hashes'].items(): assert sha(ROOT/name) == expected, 'sealed input changed: '+name
    assert sha(OUT/'contract.json') == s['contract_sha256']
    assert read(OUT/'qualification.json')['passed']
    if engineering: assert read(OUT/'engineering.json')['passed']
    device(); return read(OUT/'contract.json')


def complete(folder, metadata):
    write(folder/'complete.json', {**metadata, 'seal_sha256': sha(OUT/'seal.json'),
                                  'files': {p.name: sha(p) for p in folder.iterdir()
                                            if p.is_file() and p.name != 'complete.json'}})


def completed(folder):
    if not (folder/'complete.json').exists(): return False
    d = read(folder/'complete.json'); assert d['seal_sha256'] == sha(OUT/'seal.json')
    for k, h in d['files'].items(): assert sha(folder/k) == h
    return True


def cli(description):
    import argparse
    p = argparse.ArgumentParser(description=description)
    p.add_argument('--suite', choices=['E1'], default='E1')
    return p
