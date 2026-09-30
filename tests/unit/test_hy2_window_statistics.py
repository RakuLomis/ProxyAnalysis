import sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'eval/hy2_carrier_calibration'))
from window_score import measures

def test_new_f1_includes_auxiliary_false_positive():
    cm=np.eye(5)*4
    cm[2,2]=0;cm[2,0]=4
    mask=np.array([1,1,0,0,0])
    result=measures(cm,0.,0.,0.,0.,mask)
    assert np.isclose(result[0],(2/3+1)/2)
    assert np.isclose(result[2],.8)

def test_full_five_class_perfect_predictions():
    result=measures(np.eye(5)*4,0.,0.,0.,0.,np.array([0,0,0,1,1]))
    np.testing.assert_array_equal(result,[1,1,1,0,0,0,0])
