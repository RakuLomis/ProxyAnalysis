"""Small conditional histograms and empirical native companions on CUDA."""
import numpy as np
import torch
from common import cuda, require
from bins import encode, size, load


def tensor(x, integer=False):
    return torch.as_tensor(np.asarray(x), dtype=torch.int64 if integer else torch.float64, device=cuda())


def states(frame, feature, merged=False, conditioned=False):
    a = encode(frame['pre_' + feature], feature, merged)
    k = size(feature, merged)
    if conditioned:
        a = a * 3 + load(frame.pre_U_up + frame.pre_U_down)
        k *= 3
    return a, k


def joint_counts(a, b, w, ka, kb):
    return torch.bincount(a * kb + b, weights=w, minlength=ka * kb).reshape(ka, kb)


def group_counts(a, b, wa, wb, ga, gb, ng, ka, kb):
    ca = joint_counts(ga, a, wa, ng, ka)
    cb = joint_counts(gb, b, wb, ng, kb)
    total = ca.sum(1)
    require(torch.allclose(total, cb.sum(1), atol=1e-11, rtol=1e-12), 'Anonymous group mass mismatch')
    return ca.T @ (cb / total[:, None])


def smooth(counts, alpha=1., beta=1.):
    qb = (counts.sum(0) + beta / counts.shape[1]) / (counts.sum() + beta)
    kernel = (counts + alpha * qb[None]) / (counts.sum(1)[:, None] + alpha)
    require(torch.allclose(kernel.sum(1), torch.ones(kernel.shape[0], device=cuda(), dtype=torch.float64),
                           atol=1e-12, rtol=1e-12), 'Kernel does not normalize')
    return qb, kernel


def fit_tables(pre, post, group_pre, group_post, weights, feature, merged=False, conditioned=False):
    a_np, ka = states(pre, feature, merged, conditioned)
    b_np = encode(post['post_' + feature], feature, merged)
    kb = size(feature, merged)
    a, b, w = tensor(a_np, True), tensor(b_np, True), tensor(weights)
    true = joint_counts(a, b, w, ka, kb)
    groups = sorted(group_pre.content_id.unique())
    ids = {v: i for i, v in enumerate(groups)}
    ga = tensor(group_pre.content_id.map(ids), True)
    gb = tensor(group_post.content_id.map(ids), True)
    ag_np, _ = states(group_pre, feature, merged, conditioned)
    bg_np = encode(group_post['post_' + feature], feature, merged)
    anonymous = group_counts(tensor(ag_np, True), tensor(bg_np, True),
                             tensor(group_pre.fit_mass), tensor(group_post.fit_mass),
                             ga, gb, len(groups), ka, kb)
    for axis in [0, 1]:
        require(torch.allclose(true.sum(axis), anonymous.sum(axis), atol=1e-11, rtol=1e-12),
                'True/group marginals differ')
    qb, k1 = smooth(true)
    qg, k2 = smooth(anonymous)
    require(torch.allclose(qb, qg, atol=1e-12, rtol=1e-12), 'Marginal bases differ')
    return {'M0': qb, 'M1': k1, 'M2': k2, 'true_counts': true,
            'group_counts': anonymous, 'row_mass': true.sum(1),
            'feature': feature, 'ka': ka, 'kb': kb,
            'merged': merged, 'conditioned': conditioned}


def native_tables(pre, post, group_pre, group_post, weights, feature):
    a_np, ka = states(pre, feature)
    a, w = tensor(a_np, True), tensor(weights)
    y = tensor(post['post_' + feature], True)
    support, bi = torch.unique(y, sorted=True, return_inverse=True)
    ny = len(support)
    ct = joint_counts(a, bi, w, ka, ny)
    base = ct.sum(0) / ct.sum()
    q1 = (ct + base[None]) / (ct.sum(1)[:, None] + 1)
    ids = {v: i for i, v in enumerate(sorted(group_pre.content_id.unique()))}
    ga = tensor(group_pre.content_id.map(ids), True)
    gb = tensor(group_post.content_id.map(ids), True)
    ag, _ = states(group_pre, feature)
    yg = tensor(group_post['post_' + feature], True)
    bg = torch.searchsorted(support, yg)
    require(torch.equal(support[bg], yg), 'Anonymous native output support differs')
    cg = group_counts(tensor(ag, True), bg, tensor(group_pre.fit_mass), tensor(group_post.fit_mass),
                      ga, gb, len(ids), ka, ny)
    q2 = (cg + base[None]) / (cg.sum(1)[:, None] + 1)
    levels = tensor([.05, .1, .5, .9, .95])
    result = {}
    for arm, q in [('M0', base[None]), ('M1', q1), ('M2', q2)]:
        cdf = torch.cumsum(q, dim=1).contiguous()
        indices = torch.searchsorted(cdf, levels.expand(len(q), -1).contiguous())
        require(int(indices.max()) < ny, 'Invalid native quantile index')
        result[arm] = support[indices]
    return result


def predict(bundle, pre):
    """No test post argument; emit complete distributions for later scoring."""
    a_np, _ = states(pre, bundle['feature'], bundle['merged'], bundle['conditioned'])
    a = tensor(a_np, True)
    return {arm: (bundle[arm].expand(len(a), -1) if arm == 'M0' else bundle[arm][a])
            for arm in ['M0', 'M1', 'M2']}

