"""New experiment paths and definitions; never mutates Extend v3 artifacts."""
from pathlib import Path
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from proxy_analysis.extend_calibration.audit import read, write, file_hash, digest

OLD = ROOT / 'outputs/extend-calibration-20260930/run-01'
EXTRACT = OLD / 'extraction-03'
OUT = ROOT / 'outputs/business-protocol-eval-extend/run-01'
PROTOCOLS = ['shadowsocks', 'vless', 'trojan', 'vmess', 'anytls']
FEATURES = ['W_up', 'W_down', 'P_up', 'P_down', 'R_up', 'R_down']
SEEDS = [20260918, 20260919, 20260920]


def valid_w(x):
    x = np.asarray(x)
    assert x.ndim == 2 and x.shape[1] == 6
    assert np.isfinite(x).all() and (x >= 0).all() and (x == np.floor(x)).all()
    w,p,r = x[:,:2], x[:,2:4], x[:,4:]
    assert (r <= p).all() and (p <= w).all() and (w <= 65527*p).all()
    assert (r.sum(1) >= 1).all() and (abs(r[:,0]-r[:,1]) <= 1).all()
    assert ((r == 0) == (p == 0)).all() and ((p == 0) == (w == 0)).all()


def device():
    import torch
    if not torch.cuda.is_available():
        raise RuntimeError('CUDA is required; CPU fallback is prohibited')
    return torch.device('cuda')


def check_files(mapping):
    for name, expected in mapping.items():
        assert file_hash(ROOT / name) == expected, 'Changed source: ' + name
