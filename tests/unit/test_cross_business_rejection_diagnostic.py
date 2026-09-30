import importlib.util
from pathlib import Path
import numpy as np
from proxy_analysis.conditional_drift.model import decode
spec=importlib.util.spec_from_file_location('rejection_diagnostic',Path(__file__).resolve().parents[2]/'eval/cross_business_calibration/diagnose_rejection.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)

def test_all_constraint_flags_match_frozen_decoder():
    rng=np.random.default_rng(18)
    for _ in range(300):
        raw=rng.uniform(-.5,20,6);F=int(rng.integers(1,8))
        _,_,reason=decode(np.log1p(raw),F)
        assert bool(mod.violations(raw,F)['any_invalid'])==bool(reason)

def test_rounding_can_remove_raw_order_violation():
    raw=np.array([100,100,3.1,5,3.2,5]);assert raw[4]>raw[2]
    assert not mod.violations(raw,2)['R_gt_E_up']

def test_uniform_pool_conditioning_tv_equals_rejection_probability():
    good=np.array([True,False,True,True,False,False])
    before=np.ones(6)/6;after=good/good.sum()
    assert np.isclose(abs(after-before).sum()/2,1-good.mean())

def test_log_margin_decomposition():
    center=np.array([10.,11.,5.,6.,3.,4.]);residual=np.array([.2,.1,-1.,-2.,2.,0.])
    total=center+residual
    assert np.isclose(total[2]-total[4],(center[2]-center[4])+(residual[2]-residual[4]))
