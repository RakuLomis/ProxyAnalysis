"""Ten block scalar amplitudes; no clipping or simplex projection."""
from common import *

INDEX = [j for j in range(10) for _ in range(size(j))]

def adjust(a, b0, q):
    index = torch.tensor(INDEX,device=a.device)
    if q.ndim==1: gain=q[index]
    else: gain=q[:,index].unsqueeze(1)
    return a+(b0-a)*gain

def regularizer(q): return .01*(q-1).square().mean(-1)
