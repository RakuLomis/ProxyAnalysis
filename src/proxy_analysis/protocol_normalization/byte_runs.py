"""A fixed one-pass deletion family. Never merge across connection boundaries."""
import numpy as np

THRESHOLDS = (0, 64, 256, 1024)


def merge_runs(events):
    runs = []
    for direction, size in events:
        if size <= 0:
            continue
        if runs and runs[-1][0] == direction:
            runs[-1] = (direction, runs[-1][1]+size)
        else:
            runs.append((direction, size))
    return runs


def multiscale(events):
    base = merge_runs(events)
    total = sum(v for _, v in base)
    out = []
    for threshold in THRESHOLDS:
        runs = merge_runs((d, v) for d, v in base if v >= threshold)
        values = [v for _, v in runs]
        kept = sum(values)
        row = {'threshold_bytes': threshold, 'run_count': len(runs), 'switches': max(0, len(runs)-1),
               'retained_bytes': kept, 'retained_fraction': kept/total if total else None,
               'run_bytes_median': float(np.median(values)) if values else None,
               'run_bytes_p95': float(np.quantile(values, .95)) if values else None,
               'zero_run': not runs, 'single_run': len(runs) == 1,
               'directions': [d for d, _ in runs], 'new_bytes': values}
        for direction, prefix in [(1, 'up'), (-1, 'down')]:
            den = sum(v for d, v in base if d == direction)
            row[prefix+'_retained_fraction'] = sum(v for d, v in runs if d == direction)/den if den else None
        out.append(row)
    return out
