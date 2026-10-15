"""Paths, immutable inputs, and small JSON helpers for probability drift."""
from pathlib import Path
import hashlib
import json
import platform
import subprocess

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'outputs/protocol-probability-drift-20261004/run-01'
EXTRACT = ROOT / 'outputs/extend-calibration-20260930/run-01/extraction-03'
PARENTS = ROOT / 'outputs/business-protocol-eval-extend/run-01'
REGISTRY = ROOT / 'outputs/mechanism-guided-drift-20261003/registry'
DOC = ROOT / 'docs/protocol-probability-drift'
PLAN = ROOT / 'plan/protocol-conditioned-flow-probability-information-plan-20261004.md'
PROTOCOLS = ['shadowsocks', 'vless', 'trojan', 'vmess']
WINDOW_PROTOCOLS = PROTOCOLS + ['anytls']
FAMILIES = {
    'bytes': ['W_up', 'W_down', 'U_up', 'U_down'],
    'events': ['P_up', 'P_down', 'E_up', 'E_down'],
    'interaction': ['FR_packet_runs', 'R_unique_zero_runs'],
}
FEATURES = sum(FAMILIES.values(), [])
EXPECTED = {'shadowsocks': 5608, 'vless': 5957, 'trojan': 5919, 'vmess': 6082}
SEED = 20261004


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def write(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2,
                               allow_nan=False) + '\n', encoding='utf-8')


def hash_file(path):
    path = Path(path)
    if path.suffix.lower() in {'.pcap', '.pcapng', '.cap'}:
        raise ValueError('PCAP reads are outside the approved cache-only scope')
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def relative(path):
    return Path(path).resolve().relative_to(ROOT).as_posix()


def cuda():
    import torch
    if not torch.cuda.is_available():
        raise RuntimeError('CUDA required: do not silently fit or predict on CPU')
    return torch.device('cuda:0')


def environment():
    import torch
    import numpy
    import pandas
    import pyarrow
    device = cuda()
    x = torch.arange(4, dtype=torch.float64, device=device)
    assert (x * x).sum().item() == 14
    return {'python': platform.python_version(), 'torch': torch.__version__,
            'numpy': numpy.__version__, 'pandas': pandas.__version__,
            'pyarrow': pyarrow.__version__, 'cuda_runtime': torch.version.cuda,
            'gpu': torch.cuda.get_device_name(device), 'dtype': 'float64',
            'float64_check': True, 'device': str(device)}


def git_state():
    prefix = ['git', '-c', 'safe.directory=' + ROOT.as_posix(), '-C', str(ROOT)]
    return {'commit': subprocess.check_output(prefix + ['rev-parse', 'HEAD'], text=True).strip(),
            'status': subprocess.check_output(prefix + ['status', '--short'], text=True).splitlines()}


def require(check, message):
    if not check:
        raise RuntimeError(message)


def verify_sources():
    baseline = read(OUT / 'manifests/baseline-manifest.json')
    for rel, sha in baseline['sha256'].items():
        require(hash_file(ROOT / rel) == sha, 'Frozen source changed: ' + rel)


def checkpoint(stage, data):
    write(OUT / 'progress.json', {'stage': stage, **data})

