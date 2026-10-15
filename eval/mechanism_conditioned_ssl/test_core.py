"""Small fixed tests; no business results or checkpoint selection."""
import unittest
from common import *
from models import encoder, projector, head, Batched, loss_matrix
from sampling import ssl_schedule, independent_schedule
from score import f1, draws


class Core(unittest.TestCase):
    def test_counts(self):
        self.assertEqual(sum(p.numel() for p in encoder().parameters()), 2528)
        self.assertEqual(sum(p.numel() for p in head().parameters()), 1254)
        self.assertEqual(sum(p.numel() for p in projector().parameters()), 1584)

    def test_invalid_support(self):
        for x in [[2, 2, 3, 2, 1, 1], [1, 1, 1, 1, 1, 0], [0, 0, 0, 0, 0, 0]]:
            with self.assertRaises(AssertionError): validate([x])

    def test_batch_isolation(self):
        e = encoder(); b = Batched([e.state_dict(), e.state_dict()])
        b(tensor(np.ones((2, 8, 6))))[0].sum().backward()
        self.assertTrue(all(p.grad[1].eq(0).all() for p in b.parameters()))

    def test_uniform_loss(self):
        q = tensor(np.ones((1, 8, 6))); groups = tensor([0]*4+[1]*4, torch.long)
        neg = (groups[:, None] != groups[None, :])[None]
        self.assertAlmostEqual(float(loss_matrix(q, q, neg, ~neg)[0]), np.log(5), places=5)

    def test_no_identity_group_access(self):
        with self.assertRaises(PermissionError): Bundle(0, 'B6').get('true_pair_center')
        with self.assertRaises(PermissionError): Bundle(0, 'B1').get('pre')

    def test_ssl_schedule_exposure(self):
        f = pd.DataFrame([{'deployment': p, 'group_id': f'g{g}', 'row_token': f'{p}-{g}-{r}'}
                          for p in range(5) for g in range(24) for r in range(4)])
        ix = ssl_schedule(f, SEEDS[0]); self.assertEqual(ix.shape, (1000, 120))
        pre = f.iloc[::-1].reset_index(drop=True)
        ip = independent_schedule(f, pre, ix)
        self.assertEqual(set(f.iloc[ix[0]].group_id), set(pre.iloc[ip[0]].group_id))
        f['label_id'] = 0
        with self.assertRaises(AssertionError): ssl_schedule(f, SEEDS[0])

    def test_f1_sixclasses(self):
        self.assertEqual(float(f1(np.eye(6))), 1.)
        self.assertEqual(float(f1(np.zeros((6, 6)))), 0.)


if __name__ == '__main__': unittest.main()
