"""Isolated CUDA replay of the first failed fit; no formal artifact writes.

Only the failed training role and its training packages are read. Optimizer
settings, initialization, objective and numerical replay match the sealed fit.
An observational Python trace identifies the actual LBFGS break statement.
"""
from pathlib import Path
import ast
import hashlib
import inspect
import json
import os
import sys
import time

os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")
import numpy as np
import pandas as pd
import pyarrow.parquet
import torch
import torch.nn.functional as F

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "eval/calibrated_deployment_transfer"))
import common as original

RUN = original.OUT
DEST = ROOT / "outputs/calibrated-deployment-optimizer-diagnosis-20261006/run-01"
ROLE = "main/f0/shadowsocks/G0/i1/vless"


def checked_artifact(path):
    sidecar = original.read(path.with_suffix(".json"))
    assert original.sha(path) == sidecar["sha256"]
    return torch.load(path, map_location=original.device(), weights_only=True)


def scalar(value):
    if torch.is_tensor(value):
        return float(value.detach())
    if isinstance(value, (int, float)):
        return value
    return None


def optimizer_breaks():
    method = inspect.unwrap(torch.optim.LBFGS.step)
    text, line = inspect.getsourcelines(method)
    import textwrap
    parsed = ast.parse(textwrap.dedent("".join(text)))
    breaks = {}
    for node in ast.walk(parsed):
        if isinstance(node, ast.If) and any(isinstance(item, ast.Break) for item in node.body):
            for item in node.body:
                if isinstance(item, ast.Break):
                    breaks[line + item.lineno - 1] = ast.unparse(node.test)
    return method.__code__, breaks


def replay(slot, name, t=0.0):
    x, y, mass = slot["x"], slot["y"], slot["mass"]
    w = torch.nn.Parameter(torch.zeros((6, 96), device=original.device(), dtype=torch.float64))
    b = torch.nn.Parameter(torch.zeros(6, device=original.device(), dtype=torch.float64))
    optimizer = torch.optim.LBFGS([w, b], max_iter=500, tolerance_grad=1e-9,
                                tolerance_change=1e-12, line_search_fn="strong_wolfe")
    initial = float(original.objective(w, b, x, y, mass, t).detach())
    calls, trajectory, break_record = 0, [], {}
    code, breaks = optimizer_breaks()

    def trace(frame, event, arg):
        if frame.f_code is not code:
            return None
        if event == "line" and frame.f_lineno in breaks:
            break_record.update(condition=breaks[frame.f_lineno], source_line=frame.f_lineno)
            for key in ["n_iter", "current_evals", "max_iter", "max_eval", "loss", "prev_loss", "gtd", "t", "opt_cond"]:
                if key in frame.f_locals:
                    break_record[key] = scalar(frame.f_locals[key])
        return trace

    def closure():
        nonlocal calls
        calls += 1
        optimizer.zero_grad()
        value = original.objective(w, b, x, y, mass, t)
        assert torch.isfinite(value)
        value.backward()
        trajectory.append(dict(closure=calls, objective=float(value.detach()),
                               gradient_max=max(float(w.grad.abs().max()), float(b.grad.abs().max()))))
        return value

    started = time.perf_counter()
    assert sys.gettrace() is None
    try:
        sys.settrace(trace)
        optimizer.step(closure)
    finally:
        sys.settrace(None)
    value = float(closure().detach())
    torch.cuda.synchronize()
    rw = w.detach().clone().requires_grad_()
    rb = b.detach().clone().requires_grad_()
    logits = x @ rw.T + rb
    loss = (mass * (torch.logsumexp(logits, 1) - logits.gather(1, y[:, None]).squeeze(1))).sum()
    loss = loss + .0005 * (1 + t) * rw.square().sum()
    gw, gb = torch.autograd.grad(loss, (rw, rb))
    grad = max(float(gw.abs().max()), float(gb.abs().max()))
    error = abs(float(loss.detach()) - value)
    gradient_error = max(float((gw - w.grad).abs().max()), float((gb - b.grad).abs().max()))
    state = optimizer.state[w]
    iterations = int(state.get("n_iter", 0))
    gates = dict(objective_nonincrease=value <= initial + 1e-10,
                 original_coordinate_gradient=grad <= 1e-5, iteration_budget=iterations < 500,
                 objective_replay=error < 1e-10, gradient_replay=gradient_error < 1e-10)
    result = dict(name=name, t=t, initial_objective=initial, objective=value, iterations=iterations,
                  function_evaluations=int(state.get("func_evals", 0)), closure_evaluations=calls,
                  max_gradient=grad, objective_replay_error=error, gradient_replay_error=gradient_error,
                  gates=gates, accepted=all(gates.values()), actual_optimizer_break=break_record,
                  max_iter=500, default_max_eval=optimizer.param_groups[0]["max_eval"],
                  seconds=time.perf_counter() - started, device=str(x.device), dtype=str(x.dtype))
    pd.DataFrame(trajectory).to_parquet(DEST / f"{name}-closure-trajectory.parquet", index=False)
    print(json.dumps(result, ensure_ascii=False), flush=True)
    return result, {"weight": w.detach(), "bias": b.detach()}, optimizer


def moments(slot):
    x, mass = slot["x"], slot["mass"]
    weighted_second = (mass[:, None] * x.square()).sum(0)
    augmented = torch.cat([x, torch.ones((len(x), 1), device=x.device, dtype=x.dtype)], 1)
    # At zero logits the five orthonormal class contrasts share this 97D block.
    initial_hessian_block = augmented.T @ (augmented * mass[:, None]) / 6
    initial_hessian_block += torch.diag(torch.cat([torch.full((96,), .001, device=x.device, dtype=x.dtype),
                                                   torch.zeros(1, device=x.device, dtype=x.dtype)]))
    eigenvalues = torch.linalg.eigvalsh(initial_hessian_block)
    return dict(rows=len(x), finite=bool(torch.isfinite(x).all()),
                max_abs=float(x.abs().max()), weighted_second_max=float(weighted_second.max()),
                initial_hessian_contrast_min=float(eigenvalues.min()),
                initial_hessian_contrast_max=float(eigenvalues.max()),
                initial_hessian_contrast_condition=float(eigenvalues.max() / eigenvalues.min()),
                constant_positive_scale_below_1e12=int(((slot["scale"] > 0) & (slot["scale"] < 1e-12)).sum()),
                class_mass=[float(mass[slot["y"] == j].sum()) for j in range(6)])


def main():
    assert not (RUN / "runner.lock").exists(), "Formal runner may be active"
    assert original.read(RUN / "progress.json")["stage"] == "engineering_stop"
    original.configure()
    contract = original.contract()
    before = {p: original.sha(ROOT / p) for p in contract["source_sha256"]}
    assert before == contract["source_sha256"]
    failure_before = original.sha(RUN / "failure.json")
    progress_before = original.sha(RUN / "progress.json")
    DEST.mkdir(parents=True, exist_ok=True)
    slots = {arm: checked_artifact(RUN / "slots" / ROLE / f"{arm}.pt") for arm in ["CT0", "CT1"]}
    # Reconstruct the CT1 auxiliary input from allowed training pre, not test data.
    path = RUN / "packages" / ROLE / "source-pre.parquet"
    assert original.rel(path) in contract["packages"]
    assert original.sha(path) == contract["packages"][original.rel(path)]["sha256"]
    pre = pd.read_parquet(path)
    aux = (original.tensor(pre[original.HIST]) - slots["CT1"]["mu"]) / slots["CT1"]["scale"]
    source_rows = len(pre)
    slot_error = float((aux - slots["CT1"]["x"][source_rows:2 * source_rows]).abs().max())
    assert slot_error == 0
    control, control_model, _ = replay(slots["CT0"], "CT0-control")
    previous = checked_artifact(RUN / "models" / ROLE / "CT0-t0.pt")
    control_error = max(float((control_model[key] - previous[key]).abs().max()) for key in ["weight", "bias"])
    assert control["accepted"] and control_error < 1e-10
    first, first_model, _ = replay(slots["CT1"], "CT1-failure-replay-1")
    second, second_model, _ = replay(slots["CT1"], "CT1-failure-replay-2")
    repeat_error = max(float((first_model[key] - second_model[key]).abs().max()) for key in ["weight", "bias"])
    assert repeat_error == 0 and first["gates"] == second["gates"]
    top = slots["CT1"]["x"].abs().amax(0)
    indexes = torch.argsort(top, descending=True)[:10].cpu().tolist()
    columns = [dict(index=i, feature=original.HIST[i], max_abs=float(top[i]),
                    post_training_scale=float(slots["CT1"]["scale"][i])) for i in indexes]
    result = dict(status="isolated_diagnosis_only", role=ROLE, formal_methods_changed=False,
                  formal_model_written=False, formal_runner_restarted=False,
                  target_U_or_test_data_read=False, diagnostic_replay_fits=3,
                  original_fit_source_sha256=original.sha(ROOT / "eval/calibrated_deployment_transfer/common.py"),
                  installed_lbfgs_source_sha256=original.sha(Path(inspect.getfile(torch.optim.LBFGS))),
                  CT1_training_view_reconstruction_max_error=slot_error,
                  CT0_original_checkpoint_replay_max_error=control_error,
                  CT1_duplicate_replay_max_error=repeat_error,
                  input_moments={arm: moments(slot) for arm, slot in slots.items()},
                  largest_CT1_columns=columns, fits=[control, first, second])
    assert all(original.sha(ROOT / p) == h for p, h in before.items())
    assert original.sha(RUN / "failure.json") == failure_before
    assert original.sha(RUN / "progress.json") == progress_before
    result["formal_sources_failure_and_progress_unchanged"] = True
    original.write(DEST / "diagnosis.json", result)
    print(json.dumps({k: v for k, v in result.items() if k != "fits"}, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
