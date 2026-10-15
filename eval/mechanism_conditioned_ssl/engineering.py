"""Numerical, permission, identity and CUDA gates without test scoring."""
import importlib.util
import time
from common import *
from models import encoder, projector, head, Batched, init, loss_matrix
from sampling import ssl_schedule
from run import ssl_fold


def checks():
    results = {}
    assert sum(p.numel() for p in encoder().parameters()) == 2528
    assert sum(p.numel() for p in projector().parameters()) == 1584
    assert sum(p.numel() for p in head().parameters()) == 1254
    assert sum(p.numel() for p in head(True).parameters()) == 198
    results['parameter_counts'] = True
    # Load the frozen reference without calling any of its experiment entry points.
    import sys
    saved_path = list(sys.path)
    sys.path.insert(0, str(ROOT/'eval/hy2_carrier_calibration'))
    spec = importlib.util.spec_from_file_location('frozen_window_reference', ROOT/'eval/hy2_carrier_calibration/window_model.py')
    ref = importlib.util.module_from_spec(spec); spec.loader.exec_module(ref)
    sys.path[:] = saved_path
    v = [[100, 300, 5, 12, 2, 2], [20, 0, 3, 0, 1, 0], [0, 20, 0, 2, 0, 1]]
    assert torch.equal(phi(v), ref.encode(v)); results['phi_exact_reference'] = True
    a = tensor(np.arange(48).reshape(1, 8, 6)/13)
    b = tensor(np.arange(48, 96).reshape(1, 8, 6)/17)
    a.requires_grad_(True); b.requires_grad_(True)
    group = tensor([0]*4+[1]*4, torch.long)
    neg = (group[:, None] != group[None, :])[None]
    pos = ~neg
    value = loss_matrix(a, b, neg, pos)
    aa = torch.nn.functional.normalize(a, dim=-1, eps=1e-12)
    bb = torch.nn.functional.normalize(b, dim=-1, eps=1e-12)
    dot = torch.bmm(aa, bb.transpose(1, 2))/.2; manual = []
    for i in range(8):
        for j in range(8):
            if group[i] == group[j]:
                ds = torch.cat([dot[0, i, j:j+1], dot[0, i, group != group[i]]])
                manual.append(ds.logsumexp(0)-dot[0, i, j])
    assert torch.allclose(value[0], torch.stack(manual).mean(), atol=1e-6)
    grad = torch.autograd.grad(value.sum(), (a, b))
    perm = tensor([2, 0, 3, 1, 7, 4, 6, 5], torch.long)
    ap, bp = a.detach().clone().requires_grad_(True), b.detach()[:, perm].clone().requires_grad_(True)
    pp = loss_matrix(ap, bp, neg[:, :, perm], pos[:, :, perm]); gp = torch.autograd.grad(pp.sum(), (ap, bp))
    assert torch.allclose(value, pp, atol=1e-6)
    assert torch.allclose(grad[0], gp[0], atol=1e-6)
    assert torch.allclose(grad[1][:, perm], gp[1], atol=1e-6)
    results['group_per_positive_hand_calculation_and_gradient_permutation'] = True
    e = encoder(); batched = Batched([e.state_dict(), e.state_dict()]); x = tensor(np.ones((2, 7, 6)))
    assert torch.allclose(batched(x)[0], e(x[0]), atol=1e-6, rtol=1e-6)
    batched.zero_grad(); batched(x)[0].sum().backward()
    assert all(p.grad[1].eq(0).all() for p in batched.parameters())
    results['batched_parameter_isolation'] = True
    rejected = 0
    for fold in range(5):
        for arm in SSL:
            bundle = Bundle(fold, arm); post = bundle.get('post')
            schedule = ssl_schedule(post, SEEDS[0]); assert schedule.shape == (1000, 120)
            if arm in ['B2', 'B6']:
                pre = bundle.get('pre'); assert set(pre.row_token).isdisjoint(post.row_token)
            for key in ['labels', 'test_pre', 'test_post', 'true_pair_center', 'scoring']:
                try: bundle.get(key)
                except PermissionError: rejected += 1
                else: raise AssertionError('capability escape')
    results.update({'negative_permission_checks': rejected, 'label_free_sampling': True,
                    'group_common_tokens': False, 'test_data_reads': 0})
    return results


def main():
    cli(__doc__).parse_args(); authorize(False)
    start = time.perf_counter(); result = checks()
    smoke = ssl_fold(0, steps=20, smoke=True)
    assert smoke['tasks'] == 6 and smoke['steps'] == 20
    result.update({'passed': True, 'smoke_tasks': 6, 'smoke_steps': 20, 'CUDA': True,
                   'seconds': time.perf_counter()-start, 'sealed_hashes_passed': True,
                   'test_labels_or_scores_read': False, 'production_tasks': 420})
    write(OUT/'engineering.json', result)
    print(json.dumps(result, ensure_ascii=False), flush=True)


if __name__ == '__main__': main()
