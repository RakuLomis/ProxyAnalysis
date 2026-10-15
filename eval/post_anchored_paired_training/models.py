"""Architecture and named initializers reproduce the frozen E1 E/H exactly."""
import torch
from common import device


def encoder():
    return torch.nn.Sequential(torch.nn.Linear(6, 64), torch.nn.ReLU(), torch.nn.Linear(64, 32)).to(device())


def head():
    return torch.nn.Sequential(torch.nn.Linear(32, 32), torch.nn.ReLU(), torch.nn.Linear(32, 6)).to(device())


def init(seed, kind):
    torch.manual_seed(seed+{'E': 0, 'H': 300000}[kind])
    m = encoder() if kind == 'E' else head()
    return {k: v.detach().clone() for k, v in m.state_dict().items()}


class Batched(torch.nn.Module):
    def __init__(self, states):
        super().__init__(); self.keys = list(states[0]); self.layers = len(self.keys)//2
        self.weights = torch.nn.ParameterList([torch.nn.Parameter(torch.stack([s[k] for s in states])) for k in self.keys])

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


def restore(state, kind):
    m = encoder() if kind == 'E' else head(); m.load_state_dict(state); m.eval()
    return m
