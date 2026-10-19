"""Fixed, query-post-blind block diagonal projections. No clipping."""
from .common import *


def make_views(query_pre, predicted_post, bases):
    outputs = [predicted_post.clone() for _ in VIEWS]
    for j, n in enumerate(SIZES):
        delta = query_pre[..., sl(j)] - predicted_post[..., sl(j)]
        mass = delta @ bases[n]['PM']
        loc = delta @ bases[n]['PL']
        outputs[1][..., sl(j)] += mass
        outputs[2][..., sl(j)] += loc
        outputs[3][..., sl(j)] += mass + loc
    return torch.stack(outputs, dim=0)
