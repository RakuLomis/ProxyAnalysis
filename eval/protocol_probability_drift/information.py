"""Information of one explicitly defined discrete joint distribution, not labels."""
import numpy as np
import torch
from kernels import tensor


def entropy(p, dim=None):
    values = torch.where(p > 0, -p * torch.log2(torch.where(p > 0, p, torch.ones_like(p))), 0.)
    return values.sum(dim=dim)


def information(counts):
    p = counts / counts.sum(dim=(-2, -1), keepdim=True)
    a, b = p.sum(-1), p.sum(-2)
    ha, hb, hab = entropy(a, -1), entropy(b, -1), entropy(p, (-2, -1))
    return {'H_A': ha, 'H_B': hb, 'H_AB': hab, 'H_B_given_A': hab - ha,
            'H_A_given_B': hab - hb, 'MI': ha + hb - hab, 'entropy_delta': hb - ha}


def js(p, q):
    midpoint = (p + q) / 2
    return entropy(midpoint, -1) - (entropy(p, -1) + entropy(q, -1)) / 2


def artificial_checks():
    independent = tensor([[1., 1.], [1., 1.]])
    bijective = tensor([[0., 2.], [2., 0.]])
    assert abs(information(independent)['MI'].item()) < 1e-12
    assert abs(information(bijective)['MI'].item() - 1) < 1e-12
    rng = np.random.default_rng(20261004)
    values = []
    for _ in range(200):
        a, b = rng.integers(0, 4, size=(2, 16))
        n = np.bincount(a * 4 + b, minlength=16).reshape(4, 4)
        values.append(information(tensor(n))['MI'].item())
    return {'independent_exact_MI': 0., 'bijective_flip_MI': 1.,
            'same_marginals_destroy_correspondence_MI': 0.,
            'independent_finite_sample_plugin_MI_mean': float(np.mean(values)),
            'finite_sample_rows': 16, 'finite_sample_bins': 4, 'finite_sample_repetitions': 200,
            'not_a_bias_correction_for_observed_data': True}

