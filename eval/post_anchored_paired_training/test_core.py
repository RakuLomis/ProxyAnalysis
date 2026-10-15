"""New-objective engineering tests, not another representation probe."""
import unittest
from common import *
from models import Batched, init, encoder, head
from objectives import objective, transfer, ce
from predict import PostPredictor


class CoreTests(unittest.TestCase):
    def setUp(self):
        device(); torch.manual_seed(123)

    def test_dimensions_and_interface(self):
        self.assertEqual(sum(v.numel() for v in encoder().parameters()), 2528)
        self.assertEqual(sum(v.numel() for v in head().parameters()), 1254)
        art = {'E': init(123, 'E'), 'H': init(123, 'H'), 'features': W,
               'post_scaler': {'mean': [0.]*6, 'scale': [1.]*6, 'log1p': True}}
        model = PostPredictor(art); f = pd.DataFrame(np.ones((7, 6)), columns=W)
        p = model.predict(f, 7); r = model.predict(f, 3)
        np.testing.assert_allclose(p, r, atol=1e-6)
        with self.assertRaises(PermissionError): model.predict(f.assign(pre=0))
        with self.assertRaises(PermissionError): PostPredictor({**art, 'A': None})

    def test_hand_computed_loss(self):
        p = tensor([[[1., 2., 0., -1., .2, .3], [0., .5, 1., 1.5, 2., 2.5]]], torch.float64)
        q = p.flip(-1); y = tensor([[0, 4]], torch.long); eye = torch.eye(2, device=device(), dtype=torch.float64)[None]
        total, parts = objective(p, q, y, y, eye, tensor([.5], torch.float64), tensor([.03], torch.float64))
        pp, qq = p.cpu().numpy()[0], q.cpu().numpy()[0]
        def soft(a):
            x = np.exp(a-a.max(1, keepdims=True)); return x/x.sum(1, keepdims=True)
        sp, sq = soft(pp/2), soft(qq/2)
        kl = 4*np.mean(np.sum(sq*(np.log(sq)-np.log(sp)), axis=1))
        c1 = -np.log(soft(pp)[[0, 1], [0, 4]]).mean(); c2 = -np.log(soft(qq)[[0, 1], [0, 4]]).mean()
        self.assertAlmostEqual(total.item(), .5*(c1+c2)+.5*kl+.03, places=12)

    def test_stop_gradient(self):
        e = Batched([init(123, 'E')]); h = Batched([init(123, 'H')])
        a = torch.nn.Parameter(torch.zeros(1, 32, 6, device=device()))
        xp = torch.randn(1, 4, 6, device=device()); xa = torch.randn_like(xp, requires_grad=True)
        m = torch.randn_like(xp); pl = h(e(xp)); al = h(e(xa)+torch.bmm(m, a.transpose(1, 2)))
        pl.retain_grad(); al.retain_grad()
        loss, _ = transfer(pl, al, torch.eye(4, device=device())[None]); loss.sum().backward()
        self.assertIsNone(al.grad); self.assertIsNone(a.grad); self.assertIsNone(xa.grad)
        self.assertGreater(pl.grad.abs().sum().item(), 0)
        self.assertGreater(sum(v.grad.abs().sum().item() for v in e.parameters()), 0)

    def test_zero_transfer_and_duplicate_ce(self):
        p = torch.randn(1, 4, 6, device=device(), requires_grad=True)
        q = torch.randn_like(p, requires_grad=True); y = tensor([[0, 1, 2, 3]], torch.long)
        route = torch.eye(4, device=device())[None]
        l, _ = objective(p, q, y, y, route, tensor([0.]), tensor([0.]))
        g = torch.autograd.grad(l.sum(), [p, q], retain_graph=True)
        expected = .5*(ce(p, y)+ce(q, y))
        gg = torch.autograd.grad(expected.sum(), [p, q])
        for x, z in zip(g, gg): torch.testing.assert_close(x, z)
        d, _ = objective(p, p, y, y, route, tensor([0.]), tensor([0.]))
        torch.testing.assert_close(d, ce(p, y))

    def test_group_permutation_gradients(self):
        p = torch.randn(1, 8, 6, device=device(), requires_grad=True)
        q = torch.randn_like(p, requires_grad=True); y = tensor([[0, 0, 0, 0, 1, 1, 1, 1]], torch.long)
        r = torch.block_diag(torch.ones(4, 4)/4, torch.ones(4, 4)/4).to(device())[None]
        perm = tensor([3, 0, 2, 1, 5, 7, 4, 6], torch.long)
        l, _ = objective(p, q, y, y, r, tensor([.5]), tensor([0.]))
        l2, _ = objective(p, q[:, perm], y, y[:, perm], r, tensor([.5]), tensor([0.]))
        g = torch.autograd.grad(l.sum(), [p, q], retain_graph=True)
        gg = torch.autograd.grad(l2.sum(), [p, q])
        torch.testing.assert_close(l, l2, atol=1e-6, rtol=1e-6)
        for x, z in zip(g, gg): torch.testing.assert_close(x, z, atol=1e-6, rtol=1e-6)

    def test_independent_batched_parameters(self):
        states = [init(123, 'E'), init(123, 'E')]; b = Batched(states)
        x = torch.randn(2, 7, 6, device=device()); z = b(x)
        singles = [Batched([s]) for s in states]
        for i, model in enumerate(singles):
            torch.testing.assert_close(z[i:i+1], model(x[i:i+1]), atol=1e-6, rtol=1e-6)
        z[0].sum().backward()
        for p in b.parameters(): self.assertEqual(p.grad[1].abs().sum().item(), 0.)


if __name__ == '__main__': unittest.main(verbosity=2)
