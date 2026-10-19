"""ST1 isolated, staged IO and the unchanged v4 numerical contract."""
from pathlib import Path
import contextlib
import hashlib
import importlib.util
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
import torch.nn.functional as F

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'outputs/shape-source-task-attribution-20261016/run-01'
DOC = ROOT / 'docs/shape-source-task-attribution-20261016'
PLAN = ROOT / 'plan/ST1-shape-source-downstream-attribution-plan-20261016.md'
ASSOC = ROOT / 'outputs/post-input-associated-representation-20261014/run-01'
JA = ROOT / 'outputs/joint-affine-transfer-20261007/run-01'
PREP = ROOT / 'outputs/calibrated-deployment-business-transfer-20261006/run-01'
PROTOCOLS = ['shadowsocks', 'vless', 'trojan', 'vmess']
LABELS = ['bing.com::search_results_view', 'developer.mozilla.org::document_view',
          'github.com::repository_view', 'wikipedia.org::article_view',
          'youtube.com::search_results_view', 'youtube.com::video_playback']
FEATURES = ['W_up', 'W_down', 'U_up', 'U_down', 'P_up', 'P_down',
            'E_up', 'E_down', 'FR_packet_runs', 'R_unique_zero_runs']
SIZES = [9]*4 + [10]*6
HIST = [f'h{j:02d}_{k:02d}' for j, n in enumerate(SIZES) for k in range(n)]
ARMS = ['PP', 'PG', 'GP', 'GG']
MASKS = {'G0': [2, 4], 'G1': [0, 3], 'G2': [1, 5]}
COMPARISONS = [('PP', 'PG'), ('GP', 'GG'), ('GP', 'PP')]
READS = []
STAGE = None
_CONTRACT = None
_HASHES = {}

def require(ok, message):
    if not bool(ok):
        raise RuntimeError(message)

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def rel(path):
    return Path(path).resolve().relative_to(ROOT).as_posix()

def sha(path):
    path = Path(path)
    require(path.suffix.lower() not in {'.pcap', '.pcapng', '.cap'}, 'Capture access forbidden')
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()

def writable(path):
    path = Path(path).resolve()
    require(path.is_relative_to(OUT) or path.is_relative_to(DOC), 'Write outside ST1 roots')
    path.parent.mkdir(parents=True, exist_ok=True)
    return path

def scalar(value):
    if isinstance(value, np.generic): return value.item()
    if isinstance(value, Path): return str(value)
    raise TypeError(type(value).__name__)

def write(path, value):
    path = writable(path)
    tmp = path.with_name(path.name + '.tmp')
    tmp.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2,
                              allow_nan=False, default=scalar)+'\n', encoding='utf-8')
    os.replace(tmp, path)

def save(frame, name):
    path = writable(OUT / (name+'.parquet'))
    tmp = path.with_name(path.name+'.tmp')
    frame.to_parquet(tmp, index=False)
    os.replace(tmp, path)

def textfile(path, value):
    writable(path).write_text(value, encoding='utf-8')

def device():
    require(torch.cuda.is_available(), 'CUDA required; CPU numeric fallback forbidden')
    return torch.device('cuda:0')

def configure():
    device()
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False

def tensor(value, dtype=torch.float64):
    return torch.as_tensor(np.asarray(value), device=device(), dtype=dtype)

def cpu(value): return value.detach().cpu().numpy()
def weighted(i, mass, n): return F.one_hot(i, n).to(torch.float64).T @ mass
def block(j): return slice(sum(SIZES[:j]), sum(SIZES[:j+1]))
def truths(d):
    y = d.label_id.map(dict(zip(LABELS, range(6))))
    require(y.notna().all(), 'Unknown business label')
    return y.to_numpy(int)

def error(a, b):
    absolute = float((a-b).abs().max())
    return absolute, absolute/max(1., float(a.abs().max()), float(b.abs().max()))

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

_numeric = load_module('_st1_v4_numeric', ROOT/'eval/calibrated_deployment_transfer_v4/numeric_policy.py')
POLICY, SOLVER, acceptance_gates = _numeric.POLICY, _numeric.SOLVER, _numeric.acceptance_gates

def solver_module():
    # The historical implementation imports only this module's safe globals.
    # No historical OUT/common module or installed torch class is modified.
    previous = sys.modules.get('common')
    sys.modules['common'] = sys.modules[__name__]
    try:
        return load_module('_st1_unchanged_v4_solver', ROOT/'eval/calibrated_deployment_transfer_v4/optimizer_preconditioning.py')
    finally:
        if previous is None: sys.modules.pop('common', None)
        else: sys.modules['common'] = previous

def contract():
    global _CONTRACT
    if _CONTRACT is None:
        require(sha(OUT/'contract.json') == read(OUT/'seal.json')['contract_sha256'], 'Contract changed')
        _CONTRACT = read(OUT/'contract.json')
    return _CONTRACT

def checked(path, kind, role_id=None):
    path = Path(path)
    info = contract()['files'].get(rel(path))
    require(info is not None and info['kind'] == kind, 'Unregistered input kind: '+rel(path))
    require(info.get('role_id') in {None, role_id}, 'Cross-role input')
    if kind == 'query':
        require(STAGE in {'P3', 'P5'}, 'Query outside prediction/verification')
        verify_seal(OUT/'models-complete.json')
    elif kind == 'labels':
        require(STAGE in {'P4', 'P5'}, 'Labels outside scoring/verification')
        verify_seal(OUT/'predictions-complete.json')
    stat = (path.stat().st_size, path.stat().st_mtime_ns)
    if _HASHES.get(rel(path)) != (stat, info['sha256']):
        require(sha(path) == info['sha256'], 'Input hash mismatch: '+rel(path))
        _HASHES[rel(path)] = (stat, info['sha256'])
    READS.append(dict(path=rel(path), kind=kind, role_id=role_id, stage=STAGE,
                      sha256=info['sha256'], numeric_decode=False))
    return path

def package(path, r, kind):
    path = checked(path, kind, r['id'])
    info = contract()['files'][rel(path)]
    require(pq.read_schema(path).names == info['columns'], 'Schema differs')
    d = pd.read_parquet(path)
    require(len(d) == info['rows'], 'Package rows differ')
    READS[-1]['numeric_decode'] = kind != 'labels'
    READS[-1]['columns'] = list(d)
    if kind == 'query':
        require(list(d) == ['visit_id', *HIST] and d.visit_id.is_unique, 'Query identity/schema')
    elif kind in {'source-pre', 'source-post', 'C-post'}:
        expected = r['C_contents'] if kind == 'C-post' else r['train_contents']
        protocols = {r['calibration']} if kind == 'C-post' else set(r['sources'])
        require(set(d.content_id) == set(expected) and set(d.protocol) == protocols, 'Training permission scope')
        require(not set(d.content_id)&set(r['validation_contents']), 'Content leakage')
        require(d.groupby(['protocol', 'content_id']).size().eq(4).all(), 'Repeats differ')
        if kind == 'C-post': require(not np.isin(truths(d), r['missing']).any(), 'C contains U labels')
        if kind == 'source-pre': require(not set(d)&{'visit_id', 'session_id', 'pair_id'}, 'Anonymous pre identity exposed')
    return d

def old_obj(path, r, kind):
    path = checked(path, kind, r['id'])
    z = torch.load(path, map_location=device(), weights_only=True)
    READS[-1]['numeric_decode'] = True
    allowed = {'slot': {'x','y','mass','mu','scale'}, 'map': {'matrix','bias','pre_mean','post_mean','sxx','syx','alpha','tau','mu','scale','fit_min','fit_max'},
               'classification': {'x','y','mass','mu','scale','real_x','real_mass'},
               'old-base': {'weight','bias','mu','scale'}}
    require(set(z) == allowed[kind], 'Unexpected safe tensor schema '+kind)
    return z

def put(path, value, **meta):
    path = writable(path)
    require(not path.exists(), 'Cannot overwrite sealed tensor')
    torch.save(value, path)
    write(path.with_suffix('.json'), dict(sha256=sha(path), contract_sha256=sha(OUT/'contract.json'), **meta))

def own(path):
    path = Path(path)
    meta = read(path.with_suffix('.json'))
    require(meta['contract_sha256'] == sha(OUT/'contract.json') and meta['sha256'] == sha(path), 'Own tensor seal mismatch')
    return torch.load(path, map_location=device(), weights_only=True)

def seal(path, files, **meta):
    require(not Path(path).exists(), 'Cannot replace stage seal')
    write(path, dict(contract_sha256=sha(OUT/'contract.json'),
                     files={rel(p):sha(p) for p in files}, **meta))

def verify_seal(path):
    s = read(path)
    require(s['contract_sha256'] == sha(OUT/'contract.json'), 'Stage contract mismatch')
    for p,h in s['files'].items():
        f=ROOT/p;stat=(f.stat().st_size,f.stat().st_mtime_ns)
        if _HASHES.get(p)!=(stat,h):
            require(sha(f)==h,'Stage asset changed: '+p);_HASHES[p]=(stat,h)
    return s

def progress(name, **values):
    write(OUT/'progress.json', dict(stage=name, unix=time.time(), **values))
    print(name, values, flush=True)

class BudgetStop(RuntimeError): pass

@contextlib.contextmanager
def compute(label):
    p = OUT/'budget.json'
    b = read(p) if p.exists() else dict(active_compute_seconds=0., limit_seconds=3600., segments=[])
    require(b['limit_seconds'] == 3600., 'Budget policy differs')
    if b['active_compute_seconds'] >= 3600: raise BudgetStop('Cumulative activity budget exhausted')
    torch.cuda.synchronize(); start = time.perf_counter()
    try: yield
    finally:
        torch.cuda.synchronize(); elapsed = time.perf_counter()-start
        b['active_compute_seconds'] += elapsed
        b['segments'].append(dict(stage=STAGE, label=label, seconds=elapsed))
        write(p,b)
    if b['active_compute_seconds'] >= 3600: raise BudgetStop('Cumulative activity budget reached')

@contextlib.contextmanager
def stage(name):
    global STAGE
    configure(); STAGE=name; READS.clear()
    c=contract()
    require(sha(PLAN)==c['plan_sha256'], 'Plan changed')
    for p,h in c['source_sha256'].items(): require(sha(ROOT/p)==h, 'Sealed code changed: '+p)
    require(not (OUT/'stages'/f'{name}.json').exists(), 'Stage already complete')
    require(not list((OUT/'failures').glob('stage-*.json')), 'Stopped run cannot silently resume')
    started=time.perf_counter(); progress(name+'_started')
    try:
        yield
        write(OUT/'stages'/f'{name}.json',dict(complete=True,wall_seconds=time.perf_counter()-started))
        progress(name+'_complete',wall_seconds=time.perf_counter()-started)
    except BaseException as exc:
        write(OUT/'failures'/f'stage-{name}-{time.time_ns()}.json',dict(error=repr(exc),traceback=traceback.format_exc()))
        progress(name+'_stopped',reason=str(exc)); raise
    finally:
        write(OUT/'ledgers'/f'{name}.json',dict(reads=READS,wall_seconds=time.perf_counter()-started))
        STAGE=None
