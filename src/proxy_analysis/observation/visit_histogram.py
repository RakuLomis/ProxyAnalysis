"""Frozen 96-column visit input; empty/invalid observations are not imputed."""
import bisect
from .window_stats import FEATURES

BYTE_EDGES = [1, 256, 1024, 4096, 16384, 65536, 262144, 1048576]
COUNT_EDGES = [1, 2, 3, 4, 8, 16, 32, 64, 128]
HIST = [f"h{j:02d}_{b:02d}" for j in range(10) for b in range(9 if j < 4 else 10)]


def aggregate(connections, *, coverage_verified, failures=()):
    selected = [c for c in connections if c["nonempty"]]
    reasons = set(failures)
    if not coverage_verified:
        reasons.add("coverage_unverified")
    for c in selected:
        reasons.update(c["reasons"])
    status = "invalid_observation" if reasons else "valid" if selected else "empty_window"
    row = {"status": status, "reasons": sorted(reasons), "connections": len(connections),
           "nonempty_connections": len(selected), "x": None}
    if status != "valid":
        return row
    x = dict.fromkeys(HIST, 0.0)
    for c in selected:
        for j, f in enumerate(FEATURES):
            value = c["statistics"][f]
            if not isinstance(value, int) or value < 0:
                raise ValueError("invalid_native_statistic")
            b = bisect.bisect_right(BYTE_EDGES if j < 4 else COUNT_EDGES, value)
            x[f"h{j:02d}_{b:02d}"] += 1 / len(selected)
    for j in range(10):
        if abs(sum(v for k, v in x.items() if k.startswith(f"h{j:02d}_"))-1) > 1e-12:
            raise AssertionError("histogram_normalization")
    row["x"] = x
    return row
