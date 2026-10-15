from pathlib import Path
import hashlib
import json
import os
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from proxy_analysis.pathutils import filesystem_path

BASE = ROOT / "outputs/small-view-attribution-20261010/run-02"
Q = ROOT / "outputs/protocol-probability-drift-20261004/run-01"
EXTRACT = ROOT / "outputs/extend-calibration-20260930/run-01/extraction-03"
PLAN = ROOT / "plan/p-small-observation-validation-retraining-cross-batch-plan-20261010.md"
PROTOCOLS = ["shadowsocks", "vless", "trojan", "vmess"]
ARMS = ["S", "P-small", "G-small", "RawPre-small", "RawPost-small", "Marginal-small"]
FORBIDDEN = {"netlog.json", "cdp.json", "mihomo-trace.jsonl", "flow-index.json"}
ACCESS = []


def io_path(path):
    return Path(filesystem_path(path))


def safe_read_path(path):
    p = Path(path).resolve()
    if p.suffix.lower() in {".pcap", ".pcapng", ".cap"} or p.name in FORBIDDEN:
        raise PermissionError("metadata_stage_forbidden_input:" + p.name)
    return p


def sha(path):
    p = safe_read_path(path)
    h = hashlib.sha256()
    with io_path(p).open("rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    ACCESS.append({"path": str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p),
                   "purpose": "metadata_or_model_hash", "sha256": h.hexdigest()})
    return h.hexdigest()


def read(path):
    p = safe_read_path(path)
    ACCESS.append({"path": str(p.relative_to(ROOT)), "purpose": "metadata_json"})
    return json.loads(io_path(p).read_text(encoding="utf-8-sig"))


def parquet(path):
    import pandas as pd
    p = safe_read_path(path)
    ACCESS.append({"path": str(p.relative_to(ROOT)), "purpose": "cohort_or_model_registry"})
    return pd.read_parquet(io_path(p))


def write(out, relative, value):
    out = Path(out).resolve()
    if not out.is_relative_to(ROOT / "outputs/p-small-observation-validation-20261010"):
        raise PermissionError("unregistered_output_root")
    p = out / relative
    if not p.resolve().is_relative_to(out):
        raise PermissionError("output_path_escape")
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_name(p.name + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True,
                              allow_nan=False, default=lambda x: x.item()) + "\n", encoding="utf-8")
    os.replace(tmp, p)


def save(out, relative, frame):
    p = Path(out) / relative
    if not p.resolve().is_relative_to(Path(out).resolve()):
        raise PermissionError("output_path_escape")
    p.parent.mkdir(parents=True, exist_ok=True)
    frame.to_parquet(p, index=False)


def source_lock():
    roots = [ROOT / "eval/p_small_observation_validation", ROOT / "src/proxy_analysis/observation"]
    files = [p for root in roots for p in root.rglob("*.py")]
    files += [ROOT / "src/proxy_analysis/sequences/tcp_state.py",
              ROOT / "src/proxy_analysis/extend_calibration/reassembly.py",
              ROOT / "src/proxy_analysis/parsing/packet_decoder.py",
              ROOT / "src/proxy_analysis/parsing/pcapng.py", PLAN]
    return {str(p.relative_to(ROOT)): sha(p) for p in files}


def timestamp():
    return {"time_unix": time.time(), "local_time": time.strftime("%Y-%m-%d %H:%M:%S %z")}
