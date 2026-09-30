import importlib.util
from pathlib import Path
import numpy as np
from sklearn.metrics import f1_score,balanced_accuracy_score,log_loss,confusion_matrix

path=Path(__file__).resolve().parents[2]/'eval/paired_calibration_budget/summarize.py'
spec=importlib.util.spec_from_file_location('budget_statistics',path)
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)

def test_vectorized_statistics_match_explicit_repeated_rows():
    rng=np.random.default_rng(77);y=np.tile(np.arange(6),20)
    probabilities=rng.dirichlet(np.ones(6),size=120);pred=probabilities.argmax(1)
    weights=rng.integers(1,5,120);ids=np.repeat(np.arange(120),weights)
    cm=confusion_matrix(y,pred,labels=np.arange(6),sample_weight=weights)
    ce=(-np.log2(probabilities[np.arange(120),y])*weights).sum()
    br=(np.square(probabilities-np.eye(6)[y]).sum(1)*weights).sum()
    actual=mod.measures(cm[None,None],np.array([[ce]]),np.array([[br]]))[0,0]
    expected=[f1_score(y[ids],pred[ids],average='macro'),balanced_accuracy_score(y[ids],pred[ids]),
        log_loss(y[ids],probabilities[ids])/np.log(2),np.square(probabilities[ids]-np.eye(6)[y[ids]]).sum(1).mean()]
    np.testing.assert_allclose(actual,expected,rtol=1e-12,atol=1e-12)

def test_metrics_average_is_not_probability_ensemble():
    cm=np.array([[[3,1],[1,3]],[[2,2],[0,4]]],float)
    values=mod.measures(cm,np.zeros(2),np.zeros(2))
    assert not np.isclose(values[:,0].mean(),mod.measures(cm.sum(0),0.,0.)[0])
