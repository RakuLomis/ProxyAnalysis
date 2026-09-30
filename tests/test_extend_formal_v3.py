"""Synthetic tests only: no H labels, hidden U post or raw captures."""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'eval/extend_calibration'))
import formal_common as c
import formal_generate as g
from formal_score import measures

def test_scenario_metadata():
    assert c.metadata('W-vless-f3-g2-r7')==dict(scenario='W-vless-f3-g2-r7',track='W',protocol='vless',fold=3,business_group=2,rotation=7)

def test_six_class_confusion_not_binary():
    cm=np.eye(6)*4
    # One old-business example classified as a new class reduces its precision.
    cm[2,2]-=1;cm[2,0]+=1
    m=measures(cm,0.,0.,0.,0.,np.array([1,1,0,0,0,0]))
    assert m[0]==pytest.approx((8/9+1)/2)

def test_necessary_domain():
    g.valid(np.array([[5,6,2,3,1,1]]),'W')
    g.valid(np.array([[5,6,2,3,1,1]]),'T',np.array([2]))
    for bad in [np.array([[0,6,2,3,1,1]]),np.array([[5,6,2,3,0,1]]),np.array([[5,6,2.1,3,1,1]])]:
        with pytest.raises(AssertionError):g.valid(bad,'W')

def test_reference_and_scoring_not_training_bundle():
    for kind in ['reference','scoring']:
        with pytest.raises(PermissionError):c.Bundle(Path('absent'),kind)

@pytest.fixture
def sealed(tmp_path,monkeypatch):
    monkeypatch.setattr(c,'OUT',tmp_path)
    c.write(c.contract_path(),{'test':True})
    dest=tmp_path/'generation/paired/test';dest.mkdir(parents=True)
    data=dest/'data.txt';data.write_text('original',encoding='utf-8')
    c.checkpoint(dest,{'models':1})
    return dest,data

def test_json_string_hash_and_resume(sealed):
    dest,data=sealed
    assert c.sha(str(data))==c.sha(data)
    snapshot={p:(c.sha(p),p.stat().st_mtime_ns) for p in dest.iterdir()}
    c.checkseal(str(dest/'complete.json'))
    assert snapshot=={p:(c.sha(p),p.stat().st_mtime_ns) for p in dest.iterdir()}

def test_tamper_rejected(sealed):
    dest,data=sealed;data.write_text('changed',encoding='utf-8')
    with pytest.raises(AssertionError):c.checkseal(dest/'complete.json')

def test_missing_rejected(sealed):
    dest,data=sealed;data.unlink()
    with pytest.raises(FileNotFoundError):c.checkseal(dest/'complete.json')

def test_unregistered_contract_rejected(sealed):
    dest,_=sealed;p=dest/'complete.json';d=c.read(p);d['contract']='unregistered';c.write(p,d)
    with pytest.raises((AssertionError,FileNotFoundError)):c.checkseal(p)

def test_incomplete_not_checkpoint(sealed):
    dest,_=sealed;(dest/'complete.json').unlink()
    with pytest.raises(FileNotFoundError):c.checkseal(dest/'complete.json')

def test_explicit_old_generation_only(sealed):
    dest,_=sealed;p=dest/'complete.json';d=c.read(p);d['contract']='old-hash';c.write(p,d)
    registry=c.OUT/'repair-02/compatibility.json'
    c.write(registry,{'old_contract_sha256':'old-hash','generation_seals':{str(p.resolve()):c.sha(p)}})
    c.write(c.contract_path(),{'repair':{'compatibility_sha256':c.sha(registry)}})
    c.checkseal(p)
    other=dest/'other-complete.json';c.write(other,d)
    with pytest.raises(AssertionError):c.checkseal(other)
    d['models']=2;c.write(p,d)
    with pytest.raises(AssertionError):c.checkseal(p)

def test_reference_stays_locked(sealed):
    with pytest.raises(FileNotFoundError):c.later_package('absent','reference','U_post')
    with pytest.raises(FileNotFoundError):c.later_package('absent','scoring','H_labels')

def test_real_generate_skip_does_not_read_or_write(sealed,monkeypatch):
    dest,_=sealed
    monkeypatch.setattr(g,'OUT',c.OUT)
    # generate_one only needs a valid scenario name and an already sealed directory.
    renamed=dest.with_name('W-shadowsocks-f0-g0-r0');dest.rename(renamed)
    seal=c.read(renamed/'complete.json')
    seal['files']={str(renamed/Path(p).name):h for p,h in seal['files'].items()}
    c.write(renamed/'complete.json',seal)
    before={str(p):(c.sha(p),p.stat().st_mtime_ns) for p in renamed.iterdir()}
    def forbidden(*args,**kwargs):raise AssertionError('Completed resume opened a training package')
    monkeypatch.setattr(g,'Bundle',forbidden)
    g.generate_one(Path('W-shadowsocks-f0-g0-r0'),'paired')
    assert before=={str(p):(c.sha(p),p.stat().st_mtime_ns) for p in renamed.iterdir()}

@pytest.mark.skipif(not c.torch.cuda.is_available(),reason='CUDA required')
@pytest.mark.parametrize('track',['W','T'])
def test_generated_support_and_integer_roundtrip(track):
    mod=g.wm if track=='W' else g.tm
    # Shared valid boundary cases, including a zero direction.
    x=np.array([[1,0,1,0,1,0],[65527,65527,1,1,1,1],[10000,20000,100,200,51,50]])
    f=np.ones(len(x));z=mod.encode(x);out,_=mod.decode(z) if track=='W' else mod.decode(z,f)
    np.testing.assert_array_equal(out.cpu().numpy(),x)
    rng=np.random.default_rng(887);z=rng.uniform(-20,15,(100,6));f=rng.integers(1,50,100)
    out,_=mod.decode(z) if track=='W' else mod.decode(z,f)
    g.valid(out.cpu().numpy(),track,f)
    with pytest.raises(FloatingPointError):
        mod.decode(np.full((1,6),1000.)) if track=='W' else mod.decode(np.full((1,6),1000.),np.ones(1))
