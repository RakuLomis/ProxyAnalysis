"""Independent SD1 IO boundary, immutable dependencies and cumulative budget."""
from pathlib import Path
import contextlib
import hashlib
import json
import os
import sys
import time
import traceback

os.environ.setdefault('CUBLAS_WORKSPACE_CONFIG', ':4096:8')
import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import torch

ROOT = Path(__file__).resolve().parents[2]
PARENT = ROOT / 'outputs/invariant-anchor-guarded-drift-20261012/run-01'
CLOSE = ROOT / 'outputs/invariant-anchor-diagnostic-closeout-20261012/run-01'
TI = ROOT / 'outputs/strongpost-training-intervention-20261009/run-01'
RUN_ID = os.environ.get('SD1_RUN_ID', 'run-03')
need_run_id = RUN_ID in {'run-01', 'run-02', 'run-03'}
if not need_run_id:
    raise ValueError('Unregistered SD1 run id')
OUT = ROOT / 'outputs/subblock-drift-diagnostics-20261015' / RUN_ID
DOC = ROOT / 'docs/subblock-drift-diagnostics-20261015'
PLAN = ROOT / 'plan/SD1-subblock-drift-code-implementation-plan-20261015.md'
FEATURES = ['W_up', 'W_down', 'U_up', 'U_down', 'P_up', 'P_down',
            'E_up', 'E_down', 'FR_packet_runs', 'R_unique_zero_runs']
SIZES = [9] * 4 + [10] * 6
HIST = [f'h{j:02d}_{k:02d}' for j, n in enumerate(SIZES) for k in range(n)]
PROTOCOLS = ['shadowsocks', 'vless', 'trojan', 'vmess']
PREDICTORS = ['ID', 'MEAN', 'SHIFT', 'P', 'G']
VIEWS = ['BASE', 'MASS', 'LOC', 'MASSLOC']
META = ['role_id', 'deployment', 'outer', 'group', 'inner', 'row', 'query_key', 'content_token']
READS = []
_CONTRACT = None
_CACHE = {}
_STAGE = None
TOL = 1e-10
SCALE_MIN = 1e-12


class BudgetStop(RuntimeError):
    pass


def need(ok, message):
    if not bool(ok):
        raise RuntimeError(message)


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def rel(path):
    return Path(path).resolve().relative_to(ROOT).as_posix()


def sha(path):
    path = Path(path)
    need(path.suffix.lower() not in {'.pcap', '.pcapng', '.cap'}, 'Capture IO forbidden')
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def target(path):
    path = Path(path).resolve()
    need(path.is_relative_to(OUT) or path.is_relative_to(DOC), 'Write outside SD1 roots')
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def scalar(value):
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, Path):
        return str(value)
    raise TypeError(type(value).__name__)


def write(path, value):
    path = target(path)
    tmp = path.with_name(path.name + '.tmp')
    tmp.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2,
                              allow_nan=False, default=scalar) + '\n', encoding='utf-8')
    os.replace(tmp, path)


def save(frame, name):
    path = target(OUT / (name + '.parquet'))
    tmp = path.with_name(path.name + '.tmp')
    frame.to_parquet(tmp, index=False)
    os.replace(tmp, path)


def textfile(path, value):
    target(path).write_text(value, encoding='utf-8')


def configure():
    need(torch.cuda.is_available(), 'CUDA required; CPU numeric fallback forbidden')
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False


def t(value):
    return torch.as_tensor(np.asarray(value), device='cuda:0', dtype=torch.float64)


def cpu(value):
    return value.detach().cpu().numpy()


def sl(j):
    return slice(sum(SIZES[:j]), sum(SIZES[:j + 1]))


def prefix_sum(values):
    """CUDA deterministic short-prefix sums, same mathematical cumulative sum."""
    n = values.shape[-1]
    lower = torch.tril(torch.ones((n, n), device=values.device, dtype=values.dtype))
    return values @ lower.T


def token(value):
    return hashlib.sha256(('ja-content:' + str(value)).encode()).hexdigest()


def error(a, b):
    return float((a - b).abs().max()) / max(1., float(a.abs().max()), float(b.abs().max()))


def contract():
    global _CONTRACT
    if _CONTRACT is None:
        path = OUT / 'contract.json'
        need(sha(path) == read(OUT / 'seal.json')['contract_sha256'], 'SD1 contract changed')
        _CONTRACT = read(path)
    return _CONTRACT


def checked(path, purpose, role_id=None):
    path = Path(path)
    c = contract()
    key = rel(path)
    info = c['files'].get(key)
    need(info is not None, 'Unregistered input: ' + key)
    if info.get('role_id') is not None:
        need(role_id == info['role_id'], 'Cross-role dependency access')
    signature = (path.stat().st_size, path.stat().st_mtime_ns)
    if _CACHE.get(key) != (signature, info['sha256']):
        need(sha(path) == info['sha256'], 'Input hash mismatch: ' + key)
        _CACHE[key] = (signature, info['sha256'])
    READS.append({'path': key, 'purpose': purpose, 'role_id': role_id,
                  'sha256': info['sha256'], 'stage': _STAGE, 'numeric_decode': False})
    return path


def package(path, role, purpose):
    key = rel(path)
    info = contract()['files'].get(key, {})
    permissions = {
        'membership': {'P-query', 'P-train', 'G-pre-train', 'G-post-train'},
        'common-query-pre': {'P-query'},
        'anonymous-fit': {'G-pre-train', 'G-post-train'},
        'paired-fit-verification': {'P-train'},
        'old-G-query-fixture': {'G-query'},
        'C-score': {'P-score'},
        'C-business-metadata': {'C-metadata'},
    }
    need(info.get('kind') in permissions.get(purpose, set()), 'SD1 package permission denied')
    if purpose in {'C-score', 'C-business-metadata'}:
        need(_STAGE in {'P3', 'P5'}, 'Score/metadata outside scoring stage')
        verify_prediction_seal()
    checked(path, purpose, role['id'])
    if purpose == 'membership':
        cols = ['content_token'] + (['query_key'] if info['kind'] == 'P-query' else ['fit_mass'])
    elif purpose == 'C-business-metadata':
        cols = ['content_id', 'label_id', 'protocol']
    else:
        cols = info['columns']
    # Column projection is mandatory for metadata: no hidden histogram decode.
    schema = pq.read_schema(path).names
    need(schema == info['columns'], 'Package schema changed')
    d = pd.read_parquet(path, columns=cols)
    need(len(d) == info['rows'], 'Package row count changed')
    if purpose == 'C-business-metadata':
        need(set(d.content_id) == set(role['C_contents']), 'Metadata outside role C')
        need(set(d.protocol) == {role['target']}, 'Metadata deployment mismatch')
    else:
        need(set(d.content_token) == set(info['content_tokens']), 'Package content scope')
        need(d.groupby('content_token').size().eq(4).all(), 'Four repeats per content')
        need(not set(d) & {'label_id', 'content_id', 'visit_id', 'protocol'}, 'Identity/label leak')
    READS[-1]['columns_decoded'] = cols
    READS[-1]['numeric_decode'] = any(h in cols or 'pre_' + h in cols for h in HIST)
    return d


def obj(path, role, kind):
    info = contract()['files'].get(rel(path), {})
    need(info.get('kind') == kind, 'Tensor kind mismatch')
    checked(path, 'frozen-' + kind, role['id'])
    value = torch.load(path, map_location='cuda:0', weights_only=True)
    READS[-1]['numeric_decode'] = True
    if kind == 'old-forecast':
        # Legacy payload is an audit container, never reuse its guarded outputs.
        return {k: value[k] for k in ['a', 'b0', 'scale', 'query_keys', 'content_tokens']}
    return value


def put(path, value):
    path = target(path)
    need(not path.exists(), 'Cannot overwrite a sealed SD1 tensor')
    tmp = path.with_name(path.name + '.tmp')
    torch.save(value, tmp)
    os.replace(tmp, path)
    write(path.with_suffix('.json'), {'sha256': sha(path),
                                     'contract_sha256': sha(OUT / 'contract.json')})


def own_obj(path):
    path = Path(path)
    info = read(path.with_suffix('.json'))
    need(info['contract_sha256'] == sha(OUT / 'contract.json'), 'Incompatible SD1 tensor')
    need(sha(path) == info['sha256'], 'Changed SD1 tensor')
    return torch.load(path, map_location='cuda:0', weights_only=True)


def verify_prediction_seal():
    seal = read(OUT / 'predictions-complete.json')
    need(seal['contract_sha256'] == sha(OUT / 'contract.json'), 'Prediction contract mismatch')
    need(seal['maps'] == 480 and seal['score_reads_before_seal'] == 0, 'Incomplete forecast barrier')
    return seal


def progress(stage_name, **values):
    write(OUT / 'progress.json', {'stage': stage_name, 'unix': time.time(), **values})
    print(stage_name, values, flush=True)


@contextlib.contextmanager
def compute(label):
    path = OUT / 'budget.json'
    b = read(path) if path.exists() else {'active_compute_seconds': 0., 'limit_seconds': 1800., 'segments': []}
    if b['active_compute_seconds'] >= b['limit_seconds']:
        raise BudgetStop('Cumulative 1800-second activity budget exhausted')
    torch.cuda.synchronize()
    started = time.perf_counter()
    try:
        yield
    finally:
        torch.cuda.synchronize()
        elapsed = time.perf_counter() - started
        b['active_compute_seconds'] += elapsed
        b['segments'].append({'stage': _STAGE, 'label': label, 'seconds': elapsed})
        write(path, b)
    if b['active_compute_seconds'] >= b['limit_seconds']:
        raise BudgetStop('Cumulative activity budget reached after bounded segment')


@contextlib.contextmanager
def stage(name):
    global _STAGE
    configure()
    _STAGE = name
    READS.clear()
    c = contract()
    need(sha(PLAN) == c['plan_sha256'], 'Plan changed')
    for p, h in c['source_sha256'].items():
        need(sha(ROOT / p) == h, 'SD1 code changed after sealing: ' + p)
    need(not (OUT / 'stages' / (name + '.json')).exists(), 'Stage already complete')
    progress(name + '_started')
    started = time.perf_counter()
    try:
        yield
        write(OUT / 'stages' / (name + '.json'), {'complete': True, 'seconds': time.perf_counter() - started})
        progress(name + '_complete', seconds=time.perf_counter() - started)
    except Exception as exc:
        fail = OUT / 'failures' / f'{name}-{time.time_ns()}.json'
        write(fail, {'exception': repr(exc), 'traceback': traceback.format_exc(),
                     'budget_stop': isinstance(exc, BudgetStop), 'old_results_unchanged': True})
        progress(name + '_stopped', reason=str(exc))
        raise
    finally:
        write(OUT / 'ledgers' / f'{name}-{time.time_ns()}.json',
              {'reads': READS, 'seconds': time.perf_counter() - started})
        _STAGE = None
