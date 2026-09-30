import sys
from pathlib import Path
import numpy as np
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'eval/hy2_carrier_calibration'))
from window_model import encode,decode,validate,torch,Ridge
from experiment import Bundle,OUT

def test_cuda_roundtrip_and_direction_domain():
    a=np.array([[1,0,1,0,1,0],[0,65527,0,1,0,1],[100,200,4,5,2,3],[65527,65527,1,1,1,1]])
    z=encode(a);assert z.is_cuda
    out,_=decode(z);np.testing.assert_array_equal(out.cpu().numpy(),a)

def test_nonfinite_and_overflow_are_not_retried():
    for bad in [np.nan,np.inf,1000.]:
        z=np.zeros((1,6));z[0,0]=bad
        with pytest.raises(FloatingPointError):decode(z)

def test_random_validity():
    a,_=decode(np.random.default_rng(13).normal(0,3,(1000,6)));validate(a)
    np.testing.assert_array_equal(decode(encode(a))[0].cpu().numpy(),a.cpu().numpy())

def test_ridge_constant_dimensions_finite():
    a=np.tile([1,1,1,1,1,1],(8,1));m=Ridge(a,encode(a))
    assert torch.isfinite(m.predict(a)).all()

def test_bundle_forbids_test_and_reference_reads():
    paths=sorted((OUT/'bundles/group').glob('*'))
    if not paths:pytest.skip('prepare required')
    b=Bundle(paths[0],'group')
    for name in ['H_post','H_pre','U_post','labels']:
        with pytest.raises(PermissionError):b.get(name)
    assert set(b.get('C_post'))=={'content_id','W_up','W_down','P_up','P_down','R_up','R_down'}
