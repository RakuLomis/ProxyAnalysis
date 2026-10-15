"""Fixed fold0/seed0 smoke fits and scope checks; never reads test scoring."""
import unittest
from common import *
from train import fit, load_jobs, batch_loss
from test_core import CoreTests


def main():
    authorize(False)
    if (OUT/'engineering.json').exists(): assert read(OUT/'engineering.json')['passed']; print('engineering sealed'); return
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(CoreTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite); assert result.wasSuccessful()
    permission_checks = 0
    for fold in range(5):
        for arm in ARMS:
            cap = Bundle(fold, arm); cap.get('post')
            if arm not in ['J0', 'J7']: cap.get('pre')
            for key in ['test_post', 'labels', 'test_pre', 'identity_map']:
                try: cap.get(key)
                except PermissionError: permission_checks += 1
                else: raise AssertionError((arm, key))
            if arm in ['J0', 'J7']:
                try: cap.get('pre')
                except PermissionError: permission_checks += 1
                else: raise AssertionError('post-only arm received pre')
    d = load_jobs(0, ['J4', 'J6'], [SEEDS[0]])
    for k in ['xp', 'xa', 'm', 'yp', 'ya', 'ip', 'ia', 'routing']:
        assert torch.equal(d[k][0], d[k][1])
    loss, _ = batch_loss(d, 0, tensor([0., 0.]))
    torch.testing.assert_close(loss[0], loss[1]); loss.sum().backward()
    for p in [*d['E'].parameters(), *d['H'].parameters(), d['A']]:
        torch.testing.assert_close(p.grad[0], p.grad[1])
    fit(0, ARMS, [SEEDS[0]], 20, True)
    write(OUT/'engineering.json', {'passed': True, 'core_tests': result.testsRun,
          'permission_rejections': permission_checks, 'smoke_tasks': 8, 'smoke_steps': 20,
          'smoke_fold': 0, 'smoke_seed': SEEDS[0], 'test_scores_read': False,
          'zero_coefficient_J4_J6_gradients': True, 'CUDA': True})
    print('Engineering passed; smoke checkpoints will not initialize formal training', flush=True)


if __name__ == '__main__': main()
