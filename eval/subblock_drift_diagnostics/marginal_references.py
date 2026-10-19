"""Only marginal means and content/repetition population variances, no maps fit."""
from .common import *
from .basis import energies, validate_hist


def summarize_side(values, groups, bases):
    validate_hist(values)
    need(len(values) == 48 and len(set(groups)) == 12, 'Summary training scope')
    centers, within = [], []
    for g in sorted(set(groups)):
        rows = values[np.flatnonzero(np.asarray(groups) == g)]
        need(len(rows) == 4, 'Summary repeats')
        center = rows.mean(0)
        centers.append(center)
        within.append(energies(rows - center, bases).mean(0))
    centers = torch.stack(centers)
    mean = centers.mean(0)
    return mean, energies(centers - mean, bases).mean(0), torch.stack(within).mean(0)


def summarize_marginals(a, ga, b, gb, bases):
    need(set(ga) == set(gb), 'Marginal content mismatch')
    ma, va, wa = summarize_side(a, ga, bases)
    mb, vb, wb = summarize_side(b, gb, bases)
    return {'mean_pre': ma, 'mean_post': mb, 'V_pre': va, 'V_post': vb,
            'V_min': torch.minimum(va, vb), 'repeat_pre': wa, 'repeat_post': wb}
