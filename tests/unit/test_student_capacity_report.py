import numpy as np
import pytest
from proxy_analysis.crosscontent.student_capacity_report import logits_numpy
from proxy_analysis.crosscontent.student_capacity import network
from proxy_analysis.crosscontent.mechanism_report import clustered
import torch


@pytest.mark.parametrize('d,k',[(14,6),(157,2)])
def test_independent_numpy_replay(d,k):
    m=network(d,k,42);x=np.random.default_rng(9).normal(size=(7,d))
    state={k:v.detach().numpy().tolist() for k,v in m.state_dict().items()}
    assert np.allclose(logits_numpy(x,state),m(torch.tensor(x)).detach().numpy(),atol=1e-12)


def test_bootstrap_collapses_repeats_and_seeds_to_content():
    base=[(label,str(label)+str(i),float(i)) for label in ['a','b'] for i in range(5)]
    repeated=[(l,c,v+s) for l,c,v in base for s in [-2,-1,0,1,2] for _ in range(4)]
    cfg={'seed':3,'bootstrap_repetitions':2000}
    a,_=clustered(base,cfg);b,content=clustered(repeated,cfg)
    assert a==b and len(content)==10
