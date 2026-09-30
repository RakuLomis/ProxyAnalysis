import importlib.util
from pathlib import Path
import numpy as np

PATH=Path(__file__).resolve().parents[2]/'eval/record_time_localization/run.py'
spec=importlib.util.spec_from_file_location('localization',PATH)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

def test_five_states_exhaustive():
    a=np.array([0,0,1,1,2]);b=np.array([0,1,0,1,1]);y=np.zeros(5,dtype=int)
    assert list(module.states(a,b,y))==['both_correct','corrected','new_error','same_wrong','different_wrong']

def test_net_correct_invariant():
    rng=np.random.default_rng(42)
    a,b,y=[rng.integers(0,6,100) for _ in range(3)]
    s=module.states(a,b,y)
    assert (a==y).sum()-(b==y).sum()==(s=='corrected').sum()-(s=='new_error').sum()

def test_error_sets_are_disjoint():
    for s1 in [False,True]:
      for s2 in [False,True]:
       for l3 in [False,True]:
        assert not ((s1 and not s2) and (s2 and not l3))

def test_scores_perfect():
    values=module.scores(np.arange(6),np.eye(6))
    np.testing.assert_allclose(values,[1,1,0,0])

def test_scores_content_weights_not_seed_ensemble():
    y=np.arange(6);p=np.eye(6)*.8+.2/6
    np.testing.assert_allclose(module.scores(y,p),module.scores(y,p,np.ones(6)*4))
