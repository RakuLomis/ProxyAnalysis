import importlib.util
from pathlib import Path
import numpy as np
from sklearn.metrics import f1_score,confusion_matrix,log_loss
spec=importlib.util.spec_from_file_location('fsc_score',Path(__file__).resolve().parents[2]/'eval/feasible_summary_calibration/score.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def test_new_f1_keeps_auxiliary_false_positives():
    y=np.tile(np.arange(6),10);pred=y.copy();pred[y==2]=0
    cm=confusion_matrix(y,pred,labels=np.arange(6));mask=np.array([1,1,0,0,0,0]);p=np.eye(6)[pred]*.9+.1/6
    ce=-np.log2(p[np.arange(60),y]);br=np.square(p-np.eye(6)[y]).sum(1);new=mask[y].astype(bool)
    result=m.measures(cm,ce.sum(),br.sum(),ce[new].sum(),br[new].sum(),mask)
    np.testing.assert_allclose(result[0],f1_score(y,pred,labels=[0,1],average='macro'))
    assert result[0]<f1_score(y[new],pred[new],labels=[0,1],average='macro')
    np.testing.assert_allclose(result[5],log_loss(y[new],p[new],labels=list(range(6)))/np.log(2))

def test_bootstrap_weighted_confusion_matches_replicated_rows():
    rng=np.random.default_rng(14);y=np.tile(np.arange(6),5);p=rng.dirichlet(np.ones(6),size=30);pred=p.argmax(1);w=rng.integers(1,4,30);ids=np.repeat(np.arange(30),w)
    cm=confusion_matrix(y,pred,labels=np.arange(6),sample_weight=w);mask=np.array([0,0,1,0,1,0])
    ce=-np.log2(p[np.arange(30),y]);br=np.square(p-np.eye(6)[y]).sum(1);new=mask[y]
    result=m.measures(cm,(ce*w).sum(),(br*w).sum(),(ce*w*new).sum(),(br*w*new).sum(),mask)
    np.testing.assert_allclose(result[0],f1_score(y[ids],pred[ids],labels=[2,4],average='macro'))
