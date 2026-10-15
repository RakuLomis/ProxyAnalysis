"""CT deterministic CUDA arithmetic, sealed role IO and independent LR fits."""
from pathlib import Path
import hashlib
import json
import os
import time
os.environ.setdefault('CUBLAS_WORKSPACE_CONFIG', ':4096:8')
import numpy as np
import pandas as pd
import pyarrow.parquet
import torch
import torch.nn.functional as F

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'outputs/calibrated-deployment-business-transfer-20261006/run-01'
DOC = ROOT/'docs/calibrated-deployment-business-transfer'
Q = ROOT/'outputs/protocol-probability-drift-20261004/run-01'
OLD = ROOT/'outputs/kernel-sensitivity-regularization-20261005/run-01'
PLAN = ROOT/'plan/calibrated-deployment-business-transfer-plan-20261006.md'
PROTOCOLS = ['shadowsocks', 'vless', 'trojan', 'vmess']
LABELS = ['bing.com::search_results_view', 'developer.mozilla.org::document_view',
          'github.com::repository_view', 'wikipedia.org::article_view',
          'youtube.com::search_results_view', 'youtube.com::video_playback']
FEATURES = ['W_up', 'W_down', 'U_up', 'U_down', 'P_up', 'P_down', 'E_up', 'E_down',
            'FR_packet_runs', 'R_unique_zero_runs']
BYTE_EDGES = [1, 256, 1024, 4096, 16384, 65536, 262144, 1048576]
COUNT_EDGES = [1, 2, 3, 4, 8, 16, 32, 64, 128]
HIST = [f'h{j:02d}_{b:02d}' for j in range(10) for b in range(9 if j < 4 else 10)]
FEATURE_WEIGHTS = [1/12]*8+[1/6]*2
MASKS = {'G0': [2, 4], 'G1': [0, 3], 'G2': [1, 5]}
ARMS = ['CT0', 'CT1', 'CT2', 'CT3', 'CT4']
TS = [0., .25, 1., 4.]
ACCESS = []

def require(ok, message):
    if not bool(ok):
        raise RuntimeError(message)

def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def json_scalar(x):
    if isinstance(x, np.generic): return x.item()
    raise TypeError('Unsupported JSON type: '+type(x).__name__)
def write(p, value):
    p = Path(p); p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2,
                            allow_nan=False, default=json_scalar)+'\n', encoding='utf-8')
def sha(p):
    p = Path(p); require(p.suffix.lower() not in ['.pcap', '.pcapng', '.cap'], 'No raw captures in cache phases')
    h = hashlib.sha256()
    with p.open('rb') as s:
        for b in iter(lambda: s.read(1024*1024), b''): h.update(b)
    return h.hexdigest()
def rel(p): return Path(p).resolve().relative_to(ROOT).as_posix()
def save(df, p):
    p = Path(p); p.parent.mkdir(parents=True, exist_ok=True); df.to_parquet(p, index=False)
def device():
    require(torch.cuda.is_available(), 'CUDA required; CPU fallback forbidden')
    return torch.device('cuda:0')
def configure():
    device(); torch.set_num_threads(1); torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False; torch.use_deterministic_algorithms(True)
    torch.cuda.reset_peak_memory_stats()
def tensor(x, dtype=torch.float64): return torch.as_tensor(np.asarray(x), device=device(), dtype=dtype)
def visitid(s): return hashlib.sha256(('business-query-v1:'+s).encode()).hexdigest()
def truths(d):
    y = d.label_id.map(dict(zip(LABELS, range(6))))
    require(y.notna().all(), 'Unknown business label'); return y.to_numpy(int)
def size(j): return 9 if j < 4 else 10
def block(j):
    a = sum(size(k) for k in range(j)); return slice(a, a+size(j))
def bins(x, j):
    x = tensor(x)
    require(torch.isfinite(x).all() and (x >= 0).all() and (x == x.floor()).all(), 'Invalid integer feature')
    return torch.bucketize(x, tensor(BYTE_EDGES if j < 4 else COUNT_EDGES), right=True)
def weighted(i, w, n): return F.one_hot(i, n).to(torch.float64).T@w
def validate_query(d): require(set(d) == {'visit_id', *HIST} and d.visit_id.is_unique, 'Unsafe query schema/identity')
def scaler(raw):
    mu = raw.mean(0); scale = raw.std(0, unbiased=False)
    return mu, torch.where(scale > 0, scale, torch.ones_like(scale))
def predict(m, q):
    validate_query(q)
    with torch.no_grad():
        x = (tensor(q[HIST])-m['mu'])/m['scale']
        p = torch.softmax(x@m['weight'].T+m['bias'], 1)
    require(torch.isfinite(p).all() and (p > 0).all(), 'Invalid class probabilities')
    d = pd.DataFrame(p.cpu().numpy(), columns=[f'p{i}' for i in range(6)])
    d['visit_id'] = q.visit_id.to_numpy(); d['prediction'] = p.argmax(1).cpu().numpy(); return d
def metrics(y, p, missing=None):
    y = np.asarray(y, int); z = p.argmax(1)
    cm = np.bincount(y*6+z, minlength=36).reshape(6, 6)
    den = cm.sum(0)+cm.sum(1)
    f1 = np.divide(2*np.diag(cm), den, out=np.zeros(6), where=den > 0)
    m = {'F1_all': float(f1.mean()), 'accuracy': float((y == z).mean()),
         'CE_nats': float(-np.log(p[np.arange(len(y)), y]).mean()),
         'Brier': float(((p-np.eye(6)[y])**2).sum(1).mean())}
    m['CE_bits'] = m['CE_nats']/np.log(2)
    if missing is not None:
        m.update(F1_uncovered=float(f1[missing].mean()), F1_aux=float(np.delete(f1, missing).mean()))
    return m, cm, f1
def objective(w, b, x, y, mass, t):
    return (F.cross_entropy(x@w.T+b, y, reduction='none')*mass).sum()+.0005*(1+t)*w.square().sum()
def fit(x, y, mass, t):
    require(x.is_cuda and x.dtype == torch.float64 and abs(float(mass.sum())-1) < 1e-12, 'Fit coordinate/mass')
    w = torch.nn.Parameter(torch.zeros((6, 96), device=device(), dtype=torch.float64))
    b = torch.nn.Parameter(torch.zeros(6, device=device(), dtype=torch.float64))
    opt = torch.optim.LBFGS([w, b], max_iter=500, tolerance_grad=1e-9,
                           tolerance_change=1e-12, line_search_fn='strong_wolfe')
    calls = 0; started = time.perf_counter(); initial = float(objective(w, b, x, y, mass, t).detach())
    def closure():
        nonlocal calls
        calls += 1; opt.zero_grad(); value = objective(w, b, x, y, mass, t)
        require(torch.isfinite(value), 'Nonfinite objective'); value.backward(); return value
    opt.step(closure); value = float(closure().detach()); torch.cuda.synchronize()
    # Independent formula and gradient replay, not the optimizer's cached closure values.
    rw = w.detach().clone().requires_grad_(); rb = b.detach().clone().requires_grad_()
    logits = x@rw.T+rb
    replay = (mass*(torch.logsumexp(logits, 1)-logits.gather(1, y[:, None]).squeeze(1))).sum()
    replay = replay+.0005*(1+t)*rw.square().sum()
    gw, gb = torch.autograd.grad(replay, (rw, rb))
    grad = max(float(gw.abs().max()), float(gb.abs().max()))
    error = abs(float(replay.detach())-value)
    gradient_error = max(float((gw-w.grad).abs().max()), float((gb-b.grad).abs().max()))
    iterations = int(opt.state[w].get('n_iter', 0))
    require(value <= initial+1e-10 and grad <= 1e-5 and iterations < 500 and error < 1e-10
            and gradient_error < 1e-10, 'Optimization quality gate; no silent budget extension')
    log = {'t': t, 'initial_objective': initial, 'objective': value, 'iterations': iterations,
           'max_gradient': grad, 'objective_replay_error': error, 'gradient_replay_error': gradient_error,
           'closure_evaluations': calls, 'seconds': time.perf_counter()-started,
           'device': 'cuda:0', 'dtype': 'float64', 'budget_hit': False}
    return {'weight': w.detach(), 'bias': b.detach()}, log

_CONTRACT_CACHE = None
def contract():
    global _CONTRACT_CACHE
    if _CONTRACT_CACHE is None:
        original = OUT/'manifests/experiment-contract.json'
        amended = OUT/'manifests/experiment-contract-amended-io-v1.json'
        if amended.exists():
            seal = read(OUT/'manifests/engineering-io-cache-v1/amendment-seal.json')
            require(sha(amended) == seal['amended_contract_sha256'], 'IO amendment seal changed')
            require(sha(original) == seal['original_contract_sha256'], 'Original contract changed')
            _CONTRACT_CACHE = read(amended)
        else: _CONTRACT_CACHE = read(original)
    return _CONTRACT_CACHE
def start(stage):
    configure(); ACCESS.clear(); c = contract()
    amended = OUT/'manifests/experiment-contract-amended-io-v1.json'
    if amended.exists():
        require(sha(amended) == read(OUT/'manifests/engineering-io-cache-v1/amendment-seal.json')['amended_contract_sha256'], 'Active amendment changed')
    require(sha(PLAN) == c['plan_sha256'], 'Approved plan changed')
    for p, h in c['source_sha256'].items(): require(sha(ROOT/p) == h, 'Sealed source changed: '+p)
    return c
def checked(p, hashes, role):
    p = Path(p); h = sha(p); require(hashes.get(rel(p)) == h, 'Unsealed/changed input: '+rel(p))
    ACCESS.append({'role': role, 'path': rel(p), 'sha256': h})
def package(p, role):
    p = Path(p); c = contract(); info = c['packages'][rel(p)]
    allowed = {
        'diag-fit': {'diag-train'}, 'diag-predict': {'diag-query'}, 'diag-select': {'diag-inner-labels'},
        'diag-score': {'diag-outer-labels'}, 'diag-kernel-score': {'diag-test-paired'},
        'kernel-true': {'C-paired'}, 'kernel-group': {'C-group-pre', 'C-group-post'},
        'view-fit': {'source-post', 'source-pre', 'C-post'},
        'main-predict': {'main-query'}, 'main-select': {'main-inner-labels'},
        'main-score': {'main-outer-labels'}, 'main-explain': {'main-test-paired'},
        'verify': {info['kind']}}
    require(role in allowed and info['kind'] in allowed[role], 'Role cannot read '+info['kind'])
    if role in ['diag-score', 'diag-kernel-score']:
        require((OUT/'diagnostics/predictions/complete.json').exists(), 'Seal diagnostic predictions first')
    if role in ['main-score', 'main-explain']:
        require((OUT/'predictions/complete.json').exists(), 'Seal ALL main predictions first')
    checked(p, {rel(p): info['sha256']}, role); df = pd.read_parquet(p)
    require(list(df.columns) == info['columns'], 'Package schema changed')
    if role in ['diag-predict', 'main-predict']: validate_query(df)
    return df
def save_artifact(model, p, **details):
    p = Path(p); p.parent.mkdir(parents=True, exist_ok=True); torch.save(model, p)
    write(p.with_suffix('.json'), {'sha256': sha(p), **details})
def artifact(p):
    p = Path(p); require(read(p.with_suffix('.json'))['sha256'] == sha(p), 'Model seal changed')
    ACCESS.append({'role': 'artifact', 'path': rel(p), 'sha256': sha(p)})
    return torch.load(p, map_location=device(), weights_only=True)
def complete(p, **details):
    p = Path(p); write(p, {'time_unix': time.time(), **details})
def progress(stage, **details):
    write(OUT/'progress.json', {'stage': stage, 'time_unix': time.time(), **details})
    print(stage, details, flush=True)
def finish(stage, **details):
    write(OUT/'manifests'/f'{stage}-ledger.json', {'reads': ACCESS,
          'cuda_peak_MiB': torch.cuda.max_memory_allocated()/1048576, **details})
    progress(stage, **details)
def rolepath(r): return OUT/'packages'/r['id']
def kernelid(r):
    base = 'outer' if r['inner'] is None else 'inner'
    return f"{base}/f{r['outer']}/{r['calibration']}/{r['group']}"+(f"/i{r['inner']}" if r['inner'] is not None else '')
