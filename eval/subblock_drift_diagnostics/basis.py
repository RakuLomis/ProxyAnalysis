"""Data-independent moment projectors in raw frequency coordinates."""
from .common import *


def make_fixed_basis(n):
    need(n in {9, 10}, 'Only registered bin counts')
    c = torch.linspace(0., 1., n, device='cuda:0', dtype=torch.float64)
    u0 = torch.ones_like(c) / np.sqrt(n)
    u1 = c - c.mean()
    u1 = u1 / torch.linalg.vector_norm(u1)
    columns = [u0, u1]
    for j in range(n):
        v = torch.eye(n, device='cuda:0', dtype=torch.float64)[:, j].clone()
        for _ in range(2):
            for u in columns:
                v = v - (v @ u) * u
        length = torch.linalg.vector_norm(v)
        if float(length) <= 1e-12:
            continue
        v = v / length
        if float(v[v.abs().argmax()]) < 0:
            v = -v
        columns.append(v)
        if len(columns) == n:
            break
    need(len(columns) == n, 'Fixed basis rank')
    pm = torch.outer(u0, u0)
    pl = torch.outer(u1, u1)
    pr = torch.eye(n, device='cuda:0', dtype=torch.float64) - pm - pl
    return {'c': c, 'u0': u0, 'u1': u1, 'PM': pm, 'PL': pl, 'PR': pr,
            'T': torch.stack(columns, dim=1)}


def all_bases():
    return {n: make_fixed_basis(n) for n in [9, 10]}


def energies(values, bases):
    """[...,96] -> [...,10,3], per-subspace dimension, CUDA float64."""
    need(values.is_cuda and values.dtype == torch.float64 and values.shape[-1] == 96, 'Energy input')
    out = []
    for j, n in enumerate(SIZES):
        x = values[..., sl(j)]
        b = bases[n]
        em = (x @ b['u0']).square()
        el = (x @ b['u1']).square()
        er = (x @ b['PR']).square().sum(-1) / (n - 2)
        out.append(torch.stack([em, el, er], -1))
    return torch.stack(out, -2)


def validate_hist(values):
    need(values.is_cuda and values.dtype == torch.float64 and values.shape[-1] == 96, 'Histogram input')
    need(torch.isfinite(values).all() and (values >= 0).all(), 'Invalid raw frequency')
    for j in range(10):
        need(float((values[..., sl(j)].sum(-1) - 1).abs().max()) < 1e-12, 'Raw block mass rejected')
