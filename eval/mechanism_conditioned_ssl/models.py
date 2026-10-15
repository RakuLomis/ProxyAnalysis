"""Independent batched parameters: parallel tasks never share weights."""
import torch
from common import device, state_hash


def encoder():
    return torch.nn.Sequential(torch.nn.Linear(6, 64), torch.nn.ReLU(), torch.nn.Linear(64, 32)).to(device())


def projector():
    return torch.nn.Sequential(torch.nn.Linear(32, 32), torch.nn.ReLU(), torch.nn.Linear(32, 16)).to(device())


def head(linear=False):
    return (torch.nn.Sequential(torch.nn.Linear(32, 6)) if linear else
            torch.nn.Sequential(torch.nn.Linear(32, 32), torch.nn.ReLU(), torch.nn.Linear(32, 6))).to(device())


def init(seed, kind):
    # Different named streams for E/P/head; common initial weights across arms.
    offset = {'E': 0, 'P': 100000, 'linear': 200000, 'mlp': 300000}[kind]
    torch.manual_seed(seed+offset)
    module = encoder() if kind == 'E' else projector() if kind == 'P' else head(kind == 'linear')
    return {k: v.detach().clone() for k, v in module.state_dict().items()}


class Batched(torch.nn.Module):
    def __init__(self, states):
        super().__init__()
        self.keys = list(states[0]); self.weights = torch.nn.ParameterList(
            [torch.nn.Parameter(torch.stack([s[k] for s in states])) for k in self.keys])
        self.layers = len(self.keys)//2

    def forward(self, x):
        assert x.is_cuda
        for layer in range(self.layers):
            x = torch.bmm(x, self.weights[2*layer].transpose(1, 2))+self.weights[2*layer+1][:, None]
            if layer+1 < self.layers: x = torch.relu(x)
        return x

    def l2(self):
        return sum(v.square().flatten(1).sum(1) for k, v in zip(self.keys, self.weights) if k.endswith('weight'))

    def one(self, i):
        return {k: v[i].detach().clone() for k, v in zip(self.keys, self.weights)}


def loss_matrix(q, k, negative, positive, temperature=.2):
    """Per-positive denominator, not multi-positive logsumexp numerator."""
    assert q.is_cuda and k.is_cuda
    q = torch.nn.functional.normalize(q, dim=-1, eps=1e-12)
    k = torch.nn.functional.normalize(k, dim=-1, eps=1e-12)
    scores = torch.bmm(q, k.transpose(1, 2))/temperature
    neg = scores.masked_fill(~negative, -torch.inf).logsumexp(-1, keepdim=True)
    values = torch.logaddexp(scores, neg)-scores
    return ((values*positive).sum(-1)/positive.sum(-1)).mean(-1)


def symmetric(q, k, negative, diagonal):
    return .5*(loss_matrix(q, k, negative, diagonal)+
               loss_matrix(k, q, negative.transpose(1, 2), diagonal))


def restore(state, kind):
    module = encoder() if kind == 'E' else projector() if kind == 'P' else head(kind == 'linear')
    module.load_state_dict(state); module.eval(); return module
