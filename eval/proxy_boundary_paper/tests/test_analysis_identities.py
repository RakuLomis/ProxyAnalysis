import numpy as np
import xml.etree.ElementTree as ET
from pathlib import Path

def test_center_identity():
    rng=np.random.default_rng(11)
    targets=rng.normal(size=(7,4,6));pred=rng.normal(size=targets.shape)
    transform=rng.normal(size=(6,6));metric=transform.T@transform
    center=targets.mean(axis=1,keepdims=True);res=targets-center
    quad=lambda x:np.einsum('...i,ij,...j->...',x,metric,x).mean()
    lhs=quad(pred-targets)-quad(pred-center)
    rhs=quad(res)-2*np.einsum('...i,ij,...j->...',pred-pred.mean(axis=1,keepdims=True),metric,res).mean()
    np.testing.assert_allclose(lhs,rhs,atol=1e-12)

def test_centered_logits_preserve_softmax():
    rng=np.random.default_rng(8);logits=rng.normal(size=(20,6))
    shift=rng.normal(size=(20,1))
    def softmax(x):
        v=np.exp(x-x.max(axis=1,keepdims=True));return v/v.sum(axis=1,keepdims=True)
    np.testing.assert_allclose(softmax(logits),softmax(logits+shift),atol=1e-14)

def test_coordinate_distortion():
    rng=np.random.default_rng(1);c=rng.uniform(.2,3,size=8);e=rng.normal(size=(10,8))
    np.testing.assert_allclose(np.mean((e/c)**2),np.einsum('ni,ij,nj->',e,np.diag(1/c**2),e)/(10*8))

def test_diagram_ids_and_connections():
    root=Path(__file__).resolve().parents[3]/'docs/paper/proxy-boundary-correspondence/figures/source'
    paths=list(root.glob('*.drawio'));assert len(paths)==2
    for p in paths:
        tree=ET.parse(p);cells=tree.findall('.//mxCell');ids=[c.get('id') for c in cells]
        assert len(ids)==len(set(ids))
        for c in cells:
            if c.get('edge')=='1':assert c.get('source') in ids and c.get('target') in ids
