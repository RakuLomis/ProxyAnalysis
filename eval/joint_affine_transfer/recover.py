"""Operational recovery only: never edit the sealed scientific runner or retry failure."""
import argparse
import ctypes
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[2]
DEFAULT = ROOT / 'outputs/joint-affine-transfer-20261007/run-01'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def pid_alive(pid):
    """Access denied is live/unknown, never permission to steal a lock."""
    require(os.name == 'nt', 'This recovery entry is for Windows only')
    api = ctypes.WinDLL('kernel32', use_last_error=True)
    api.OpenProcess.argtypes = [ctypes.c_uint32, ctypes.c_int, ctypes.c_uint32]
    api.OpenProcess.restype = ctypes.c_void_p
    api.GetExitCodeProcess.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint32)]
    api.CloseHandle.argtypes = [ctypes.c_void_p]
    handle = api.OpenProcess(0x1000, False, pid)
    if not handle:
        error = ctypes.get_last_error()
        require(error in (5, 87), f'Cannot establish PID state: {error}')
        return error == 5
    try:
        status = ctypes.c_uint32()
        require(api.GetExitCodeProcess(handle, ctypes.byref(status)), 'PID query failed')
        return status.value == 259
    finally:
        api.CloseHandle(handle)


def workers():
    # Conservative: refuse if any JA worker exists, even one using relative --run.
    cmd = ("$ErrorActionPreference='Stop'; @(Get-CimInstance Win32_Process | "
           "Where-Object { $_.Name -match '^python(w)?\\.exe$' -and "
           " $_.CommandLine -match 'joint_affine_transfer[\\\\/](runner|train|recover)\\.py' "
           f" -and $_.ProcessId -ne {os.getpid()} }} | "
           "Select-Object -ExpandProperty ProcessId) | ConvertTo-Json -Compress")
    result = subprocess.run(['powershell.exe', '-NoProfile', '-Command', cmd],
                            capture_output=True, text=True, check=True,
                            creationflags=subprocess.CREATE_NO_WINDOW)
    value = json.loads(result.stdout) if result.stdout.strip() else []
    return value if isinstance(value, list) else [value]


def gate_model(info, policy, policy_hash):
    log = info['optimizer']
    checks = [log['accepted'], log['device'] == 'cuda:0', log['dtype'] == 'float64',
              log['numeric_policy_sha256'] == policy_hash,
              log['objective'] <= log['initial_objective'] + policy['objective_slack'],
              log['max_gradient'] <= policy['original_gradient_max'],
              log['iterations'] < policy['max_iter'],
              log['objective_replay_error'] < policy['objective_replay_tolerance'],
              log['gradient_replay_error'] < policy['gradient_replay_tolerance']]
    require(all(checks), 'Saved classifier failed original acceptance policy')


def preflight(run):
    require(run == DEFAULT.resolve(), 'Recovery scope must be the approved run-01')
    require(not (run / 'failure.json').exists(), 'Terminal scientific failure cannot be resumed')
    require(not (run / 'completion.json').exists(), 'Experiment already complete')
    lock = run / 'runner.lock'
    if lock.exists():
        require(not pid_alive(int(lock.read_text().strip())), 'Runner lock owner is live/unknown')
    require(not workers(), 'Another JA worker is active')
    seal = read(run / 'manifests/seal.json')
    contract = read(run / 'manifests/experiment-contract.json')
    require(digest(run / 'manifests/experiment-contract.json') == seal['contract_sha256'], 'Contract changed')
    checks = dict(contract['source_sha256'])
    checks.update(contract['baseline_sha256'])
    checks.update({p: v['sha256'] for p, v in contract['packages'].items()})
    for name, expected in checks.items():
        require(digest(ROOT / name) == expected, f'Sealed input/source changed: {name}')
    require(digest(ROOT / 'plan/mechanism-observability-joint-affine-transfer-plan-20261007.md')
            == contract['plan_sha256'], 'Plan changed')
    require(digest(Path(contract['installed_LBFGS_path'])) == contract['installed_LBFGS_sha256'],
            'Installed optimizer changed')
    policy_path = run / 'manifests/numeric-policy.json'
    policy = read(policy_path)
    counts = {}
    for name in ['models', 'maps', 'slots']:
        metadata = list((run / name).rglob('*.json'))
        tensors = list((run / name).rglob('*.pt'))
        require(len(metadata) == len(tensors), f'Orphan artifact in {name}; manual review required')
        for f in metadata:
            info = read(f)
            require(digest(f.with_suffix('.pt')) == info['sha256'], f'Artifact hash mismatch: {f}')
            if name == 'models':
                gate_model(info, policy, digest(policy_path))
            if name == 'maps':
                log = info['mapping']
                require(log['accepted'] and log['device'] == 'cuda:0' and log['dtype'] == 'float64'
                        and log['gradient_max'] <= 1e-8
                        and log['normalized_equation_residual'] <= 1e-10
                        and log['objective_replay_error'] < 1e-10
                        and log['gradient_replay_error'] < 1e-10, 'Unaccepted map')
        counts[name] = len(metadata)
    require(not list(run.rglob('*.tmp')), 'Unfinished temporary artifact; manual review required')
    for f in (run / 'manifests/stages').glob('*.json'):
        require(read(f)['contract_sha256'] == seal['contract_sha256'], 'Stage seal changed')
    # Import the unchanged scientific configuration; no fitting, test labels or diagnostics.
    os.environ['JA_RUN_PATH'] = str(run)
    import common
    common.start('operational_recovery_preflight')
    torch = common.torch
    a = torch.eye(96, device='cuda', dtype=torch.float64)
    require(torch.equal(torch.linalg.cholesky(a), a), 'CUDA float64 smoke failed')
    torch.cuda.synchronize()
    return {'passed': True, 'time_unix': time.time(), 'artifact_counts': counts,
            'contract_sha256': seal['contract_sha256'], 'checked_input_source_files': len(checks),
            'device': 'cuda:0', 'dtype': 'float64', 'test_labels_read': False,
            'scientific_code_changed': False, 'automatic_retry': False}


def atomic_json(path, obj):
    tmp = path.with_name(path.name + '.tmp')
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    os.replace(tmp, path)


def resume(run):
    directory = run / 'recovery'
    directory.mkdir(exist_ok=True)
    guard = directory / 'recovery.lock'
    fd = os.open(guard, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    os.write(fd, str(os.getpid()).encode()); os.close(fd)
    stamp = time.strftime('%Y%m%dT%H%M%S') + '-' + str(os.getpid())
    audit = directory / (stamp + '.json')
    state = {'supervisor_pid': os.getpid(), 'started_unix': time.time(),
             'status': 'preflight', 'automatic_retry': False,
             'recovery_code_sha256': digest(Path(__file__)),
             'authorization': '2026-10-08 user confirmed diagnosis and repair'}
    atomic_json(audit, state)
    try:
        state['preflight'] = preflight(run)
        # Recheck just before changing the stale lock; the original runner acquires its own O_EXCL lock.
        require(not workers(), 'JA worker appeared during preflight')
        lock = run / 'runner.lock'
        if lock.exists():
            require(not pid_alive(int(lock.read_text().strip())), 'Runner became live')
            archive = directory / (stamp + '-stale-runner.lock')
            os.rename(lock, archive)
            state['archived_lock'] = str(archive.relative_to(run))
        env = dict(os.environ, PYTHONIOENCODING='utf-8', PYTHONFAULTHANDLER='1')
        python = Path(sys.executable).with_name('python.exe')
        stdout = directory / (stamp + '-runner.stdout.log')
        stderr = directory / (stamp + '-runner.stderr.log')
        with stdout.open('ab') as out, stderr.open('ab') as err:
            child = subprocess.Popen([str(python), '-u', str(Path(__file__).with_name('runner.py')),
                                      '--run', str(run)], cwd=ROOT, env=env, stdout=out, stderr=err,
                                     creationflags=subprocess.CREATE_NO_WINDOW)
            state.update(status='running', runner_pid=child.pid,
                         stdout=str(stdout.relative_to(run)), stderr=str(stderr.relative_to(run)))
            atomic_json(audit, state)
            state['exit_code'] = child.wait()
        state['completion_present'] = (run / 'completion.json').exists()
        state['failure_present'] = (run / 'failure.json').exists()
        state['status'] = ('complete' if state['exit_code'] == 0 and state['completion_present']
                           else 'stopped_without_completion')
        require(state['status'] == 'complete', 'Runner stopped; no automatic retry')
    except BaseException as exc:
        state.update(exception=str(exc), traceback=traceback.format_exc())
        if state['status'] in ('preflight', 'running'):
            state['status'] = 'operational_stop'
        raise
    finally:
        state['finished_unix'] = time.time()
        atomic_json(audit, state)
        if guard.exists() and guard.read_text() == str(os.getpid()):
            guard.unlink()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--run', type=Path, default=DEFAULT)
    parser.add_argument('--preflight', action='store_true')
    args = parser.parse_args()
    run = args.run.resolve()
    require(run == DEFAULT.resolve(), 'Run scope mismatch')
    if args.preflight:
        print(json.dumps(preflight(run), indent=2))
    else:
        resume(run)
